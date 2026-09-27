#!/usr/bin/env python3
"""Diagnose a local stdio MCP server the way an MCP client (e.g. Codex) talks to it.

Starts the server exactly as configured, runs the MCP handshake
(initialize -> notifications/initialized -> tools/list) and optionally one
read-only tool call. Reports the crash, timeout or protocol violation that makes
a client give up with "Transport closed".

Standard library only, so it runs with the same interpreter the server uses:

    C:\\Python314\\python.exe scripts\\mcp_stdio_probe.py --codex-server mail_leanstech
    C:\\Python314\\python.exe scripts\\mcp_stdio_probe.py --codex-server mail_leanstech --call list_accounts
    python scripts/mcp_stdio_probe.py -- python path/to/server.py

Output is ASCII on purpose: it has to survive cp1252/cp850 pipes on Windows.
"""
from __future__ import annotations

import argparse
import json
import os
import queue
import re
import subprocess
import sys
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

PROTOCOL_VERSION = "2025-06-18"
CLIENT_INFO = {"name": "leans-mcp-stdio-probe", "version": "1.0"}
DEFAULT_STARTUP_TIMEOUT = 60.0
DEFAULT_TOOL_TIMEOUT = 120.0
SHUTDOWN_GRACE = 5.0
STDERR_TAIL_LINES = 40
PREVIEW_CHARS = 400
MAX_TOOL_PAGES = 20

# Name tokens of state-changing tools. The probe never calls such a tool.
WRITE_TOKENS = frozenset({
    "send", "move", "delete", "del", "trash", "remove", "sort", "archive", "flag",
    "unflag", "mark", "write", "update", "create", "reply", "forward", "draft",
    "upload", "rename", "copy", "expunge", "set", "put", "post", "apply", "purge",
    "empty", "label", "unlabel", "clear", "drop", "save", "import", "restore",
})

# Variables kept by --clean-env: roughly what a sandboxed client passes to a child.
WINDOWS_BASE_ENV = frozenset({
    "APPDATA", "COMPUTERNAME", "COMSPEC", "HOMEDRIVE", "HOMEPATH", "LOCALAPPDATA",
    "NUMBER_OF_PROCESSORS", "OS", "PATH", "PATHEXT", "PROCESSOR_ARCHITECTURE",
    "PROGRAMDATA", "PROGRAMFILES", "PROGRAMFILES(X86)", "SYSTEMDRIVE", "SYSTEMROOT",
    "TEMP", "TMP", "USERDOMAIN", "USERNAME", "USERPROFILE", "WINDIR",
})
POSIX_BASE_ENV = frozenset({"HOME", "LANG", "LOGNAME", "PATH", "SHELL", "TERM", "TMPDIR", "USER"})

SECRET_PATTERNS = (
    re.compile(
        r"(?i)\b((?:pass(?:word|wort)?|pwd|secret|token|api[_-]?key|credential)s?"
        r"[\"']?\s*[:=]\s*)(\"[^\"]*\"|'[^']*'|\S+)"
    ),
    re.compile(r"(?i)\b(bearer\s+)(\S+)"),
    re.compile(r"(?i)\b(LOGIN\s+\S+\s+)(\S+)"),
)

HINTS = {
    "SPAWN_FAILED": "Pfad zu Interpreter oder Skript in der Konfiguration pruefen.",
    "SERVER_EXITED": "Traceback unter 'stderr' zeigt die Ursache (fehlendes Paket, Port belegt, "
                     "UnicodeEncodeError, Login-Fehler ...).",
    "STDOUT_CLOSED": "Der Server schliesst oder ersetzt sys.stdout; stdout muss fuer JSON-RPC offen bleiben.",
    "TIMEOUT": "Der Server blockiert (z. B. Verbindungsaufbau vor dem Handshake) oder haengt im Tool.",
    "STDOUT_NOT_JSON": "stdout ist beim stdio-Transport exklusiv fuer JSON-RPC. print()/Logs nach stderr "
                       "umleiten (print(..., file=sys.stderr) bzw. logging auf stderr).",
    "INVALID_UTF8": "stdout-Pipe laeuft unter Windows in cp1252. PYTHONUTF8=1 in env setzen oder "
                    "sys.stdout.reconfigure(encoding='utf-8') im Server.",
    "STDOUT_NOT_JSONRPC": "Jede stdout-Zeile muss genau eine JSON-RPC-2.0-Nachricht sein.",
    "SLOW_STARTUP": "Knapp am Start-Timeout: Verbindungen erst beim ersten Tool-Aufruf aufbauen.",
    "NO_EXIT_ON_STDIN_EOF": "Server muss sich bei geschlossenem stdin beenden, sonst bleiben verwaiste "
                            "Prozesse zurueck.",
}


class ConfigError(Exception):
    """Invalid probe configuration (exit code 2)."""


@dataclass
class ServerSpec:
    command: str
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    cwd: str | None = None
    startup_timeout: float = DEFAULT_STARTUP_TIMEOUT
    tool_timeout: float = DEFAULT_TOOL_TIMEOUT


@dataclass
class Event:
    level: str  # "OK", "WARN" or "FAIL"
    code: str
    text: str


@dataclass
class Report:
    events: list[Event] = field(default_factory=list)
    stderr_tail: list[str] = field(default_factory=list)
    tool_names: list[str] = field(default_factory=list)
    exit_code: int | None = None

    def ok(self, text: str) -> None:
        self.events.append(Event("OK", "", text))

    def warn(self, code: str, text: str) -> None:
        self.events.append(Event("WARN", code, text))

    def fail(self, code: str, text: str) -> None:
        self.events.append(Event("FAIL", code, text))

    def codes(self, level: str | None = None) -> list[str]:
        return [e.code for e in self.events if e.code and (level is None or e.level == level)]

    @property
    def failed(self) -> bool:
        return any(e.level == "FAIL" for e in self.events)


class ProbeFailure(Exception):
    def __init__(self, code: str, text: str):
        super().__init__(text)
        self.code = code
        self.text = text


def redact(text: str) -> str:
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(lambda m: m.group(1) + "***", text)
    return text


def preview(text: str, limit: int = PREVIEW_CHARS) -> str:
    text = redact(" ".join(text.split()))
    return text if len(text) <= limit else text[:limit] + " ..."


def is_write_tool(name: str) -> bool:
    tokens = re.split(r"[_\-\s.]+|(?<=[a-z])(?=[A-Z])", name)
    return any(token.lower() in WRITE_TOKENS for token in tokens if token)


def parse_assignments(pairs: list[str], *, json_values: bool) -> dict:
    result = {}
    for pair in pairs:
        key, sep, value = pair.partition("=")
        if not sep or not key:
            raise ConfigError(f"Erwartet KEY=VALUE, erhalten: {pair!r}")
        if json_values:
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass
        result[key] = value
    return result


def default_codex_config() -> Path:
    home = os.environ.get("CODEX_HOME")
    return (Path(home) if home else Path.home() / ".codex") / "config.toml"


def load_codex_server(config_path: Path, name: str) -> ServerSpec:
    import tomllib

    try:
        with config_path.open("rb") as fh:
            config = tomllib.load(fh)
    except FileNotFoundError:
        raise ConfigError(f"Codex-Konfiguration nicht gefunden: {config_path}") from None
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Codex-Konfiguration ist kein gueltiges TOML ({config_path}): {exc}") from None

    servers = config.get("mcp_servers") or {}
    entry = servers.get(name)
    if entry is None:
        known = ", ".join(sorted(servers)) or "-"
        raise ConfigError(f"MCP-Server '{name}' fehlt in {config_path}. Vorhanden: {known}")
    if not entry.get("command"):
        raise ConfigError(f"MCP-Server '{name}' hat kein 'command' (kein stdio-Server?).")

    startup = entry.get("startup_timeout_sec")
    if startup is None and "startup_timeout_ms" in entry:
        startup = entry["startup_timeout_ms"] / 1000
    return ServerSpec(
        command=str(entry["command"]),
        args=[str(arg) for arg in entry.get("args", [])],
        env={str(k): str(v) for k, v in (entry.get("env") or {}).items()},
        cwd=entry.get("cwd"),
        startup_timeout=float(startup or DEFAULT_STARTUP_TIMEOUT),
        tool_timeout=float(entry.get("tool_timeout_sec") or DEFAULT_TOOL_TIMEOUT),
    )


def build_env(spec: ServerSpec, clean: bool) -> dict[str, str]:
    if clean:
        keep = WINDOWS_BASE_ENV if os.name == "nt" else POSIX_BASE_ENV
        env = {k: v for k, v in os.environ.items() if k.upper() in keep}
    else:
        env = dict(os.environ)
    env.update(spec.env)
    return env


_EOF = object()


class StdioSession:
    """One server process plus reader threads for its stdout and stderr."""

    def __init__(self, spec: ServerSpec, env: dict[str, str]):
        self.proc = subprocess.Popen(
            [spec.command, *spec.args],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=spec.cwd,
            env=env,
        )
        self._stdout: queue.Queue = queue.Queue()
        self._stderr: deque[str] = deque(maxlen=STDERR_TAIL_LINES)
        self._stderr_lock = threading.Lock()
        self._next_id = 0
        # code -> [count, first example, phase of first occurrence]
        self.violations: dict[str, list] = {}
        self._stdout_thread = threading.Thread(target=self._pump_stdout, daemon=True)
        self._stderr_thread = threading.Thread(target=self._pump_stderr, daemon=True)
        self._stdout_thread.start()
        self._stderr_thread.start()

    def _pump_stdout(self) -> None:
        for raw in iter(self.proc.stdout.readline, b""):
            self._stdout.put(raw)
        self._stdout.put(_EOF)

    def _pump_stderr(self) -> None:
        for raw in iter(self.proc.stderr.readline, b""):
            with self._stderr_lock:
                self._stderr.append(raw.decode("utf-8", errors="replace").rstrip())

    def stderr_tail(self) -> list[str]:
        with self._stderr_lock:
            lines = list(self._stderr)
        return [redact(line) for line in lines]

    def _violation(self, code: str, phase: str, sample: str) -> None:
        entry = self.violations.setdefault(code, [0, preview(sample, 160), phase])
        entry[0] += 1

    def _send(self, message: dict, phase: str) -> None:
        data = (json.dumps(message, ensure_ascii=False) + "\n").encode("utf-8")
        try:
            self.proc.stdin.write(data)
            self.proc.stdin.flush()
        except OSError:
            raise self._closed_failure(phase) from None

    def notify(self, method: str, phase: str) -> None:
        self._send({"jsonrpc": "2.0", "method": method}, phase)

    def request(self, method: str, params: dict, timeout: float, phase: str) -> dict:
        self._next_id += 1
        request_id = self._next_id
        self._send({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}, phase)
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ProbeFailure("TIMEOUT", f"Keine Antwort auf {phase} innerhalb von {timeout:.0f}s.")
            try:
                raw = self._stdout.get(timeout=remaining)
            except queue.Empty:
                continue
            if raw is _EOF:
                raise self._closed_failure(phase)
            message = self._decode(raw, phase)
            if message is None:
                continue
            if message.get("id") == request_id and ("result" in message or "error" in message):
                return message
            if "method" in message and "id" in message:
                self._answer_server_request(message, phase)

    def _decode(self, raw: bytes, phase: str) -> dict | None:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            self._violation("INVALID_UTF8", phase, raw.decode("cp1252", errors="replace"))
            return None
        text = text.strip()
        if not text:
            return None
        try:
            message = json.loads(text)
        except json.JSONDecodeError:
            self._violation("STDOUT_NOT_JSON", phase, text)
            return None
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
            self._violation("STDOUT_NOT_JSONRPC", phase, text)
            return None
        return message

    def _answer_server_request(self, message: dict, phase: str) -> None:
        if message.get("method") == "ping":
            reply = {"jsonrpc": "2.0", "id": message["id"], "result": {}}
        else:
            reply = {"jsonrpc": "2.0", "id": message["id"],
                     "error": {"code": -32601, "message": "Method not found"}}
        self._send(reply, phase)

    def _closed_failure(self, phase: str) -> ProbeFailure:
        try:
            code = self.proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            return ProbeFailure(
                "STDOUT_CLOSED",
                f"Verbindung waehrend {phase} geschlossen, der Prozess laeuft aber weiter (PID {self.proc.pid}).",
            )
        return ProbeFailure("SERVER_EXITED", f"Server hat sich waehrend {phase} beendet (Exit-Code {code}).")

    def close(self) -> tuple[int, bool]:
        """Close stdin like a client does. Returns (exit code, exited on its own)."""
        try:
            self.proc.stdin.close()
        except OSError:
            pass
        try:
            result = self.proc.wait(timeout=SHUTDOWN_GRACE), True
        except subprocess.TimeoutExpired:
            self.proc.terminate()
            try:
                result = self.proc.wait(timeout=SHUTDOWN_GRACE), False
            except subprocess.TimeoutExpired:
                self.proc.kill()
                result = self.proc.wait(), False
        # A grandchild can inherit the pipes and keep them open; never block on those.
        for thread, pipe in ((self._stdout_thread, self.proc.stdout), (self._stderr_thread, self.proc.stderr)):
            thread.join(timeout=1)
            if not thread.is_alive():
                pipe.close()
        return result


def _tool_text(result: dict) -> str:
    parts = []
    for item in result.get("content") or []:
        if isinstance(item, dict):
            parts.append(item.get("text") if item.get("type") == "text" else f"<{item.get('type')}>")
    if not parts and "structuredContent" in result:
        parts.append(json.dumps(result["structuredContent"], ensure_ascii=False))
    return " ".join(p for p in parts if p)


def _list_tools(session: StdioSession, timeout: float) -> list[dict]:
    tools: list[dict] = []
    params: dict = {}
    for _ in range(MAX_TOOL_PAGES):
        reply = session.request("tools/list", params, timeout, "tools/list")
        if "error" in reply:
            raise ProbeFailure("TOOLS_LIST_ERROR", f"tools/list lieferte Fehler: {preview(json.dumps(reply['error']))}")
        tools.extend(reply["result"].get("tools") or [])
        cursor = reply["result"].get("nextCursor")
        if not cursor:
            break
        params = {"cursor": cursor}
    return tools


def describe_schema(tool: dict) -> str:
    schema = tool.get("inputSchema") or {}
    required = set(schema.get("required") or [])
    props = [f"{name}{'*' if name in required else ''}" for name in (schema.get("properties") or {})]
    return f"{tool.get('name')}({', '.join(props)})"


def run_probe(spec: ServerSpec, *, call: str | None = None, call_args: dict | None = None,
              clean_env: bool = False, show_schemas: bool = False) -> Report:
    report = Report()
    started = time.monotonic()
    try:
        session = StdioSession(spec, build_env(spec, clean_env))
    except OSError as exc:
        report.fail("SPAWN_FAILED", f"Serverprozess nicht startbar: {exc}")
        return report
    report.ok(f"Prozess gestartet (PID {session.proc.pid})")

    try:
        reply = session.request(
            "initialize",
            {"protocolVersion": PROTOCOL_VERSION, "capabilities": {}, "clientInfo": CLIENT_INFO},
            spec.startup_timeout,
            "initialize",
        )
        elapsed = time.monotonic() - started
        if "error" in reply:
            raise ProbeFailure("INIT_ERROR", f"initialize abgelehnt: {preview(json.dumps(reply['error']))}")
        info = reply["result"].get("serverInfo") or {}
        report.ok(f"initialize nach {elapsed:.1f}s: {info.get('name', '?')} {info.get('version', '')} "
                  f"(Protokoll {reply['result'].get('protocolVersion', '?')})")
        if elapsed > spec.startup_timeout / 2:
            report.warn("SLOW_STARTUP", f"Start dauert {elapsed:.1f}s bei {spec.startup_timeout:.0f}s Limit.")
        session.notify("notifications/initialized", "notifications/initialized")

        tools = _list_tools(session, spec.tool_timeout)
        report.tool_names = [str(t.get("name")) for t in tools]
        report.ok(f"tools/list: {len(tools)} Tools - {', '.join(report.tool_names) or '-'}")
        if show_schemas:
            for tool in tools:
                report.ok(f"  Schema {describe_schema(tool)}   (* = Pflicht)")

        if call:
            if call not in report.tool_names:
                raise ProbeFailure("TOOL_NOT_FOUND", f"Tool '{call}' bietet der Server nicht an.")
            call_started = time.monotonic()
            reply = session.request("tools/call", {"name": call, "arguments": call_args or {}},
                                    spec.tool_timeout, f"tools/call {call}")
            took = time.monotonic() - call_started
            if "error" in reply:
                raise ProbeFailure("TOOL_RPC_ERROR", f"{call}: JSON-RPC-Fehler {preview(json.dumps(reply['error']))}")
            result = reply["result"]
            if result.get("isError"):
                raise ProbeFailure("TOOL_ERROR", f"{call} meldet isError nach {took:.1f}s: {preview(_tool_text(result))}")
            report.ok(f"tools/call {call} nach {took:.1f}s: {preview(_tool_text(result)) or '(leer)'}")
    except ProbeFailure as failure:
        report.fail(failure.code, failure.text)
    finally:
        exit_code, exited_cleanly = session.close()
        report.exit_code = exit_code
        report.stderr_tail = session.stderr_tail()

    for code, (count, sample, phase) in session.violations.items():
        report.fail(code, f"{count} ungueltige stdout-Zeile(n), erste waehrend {phase}: {sample}")
    if not report.failed:
        if exited_cleanly:
            report.ok(f"Server beendet sich nach Schliessen von stdin (Exit-Code {exit_code})")
        else:
            report.warn("NO_EXIT_ON_STDIN_EOF",
                        f"Server lief nach Schliessen von stdin weiter und wurde nach {SHUTDOWN_GRACE:.0f}s beendet.")
    return report


def render(spec: ServerSpec, report: Report, clean_env: bool) -> str:
    env_keys = ", ".join(sorted(spec.env)) or "-"
    lines = [
        "MCP-stdio-Probe",
        f"  Befehl  : {spec.command} {' '.join(spec.args)}".rstrip(),
        f"  cwd     : {spec.cwd or os.getcwd()}",
        f"  env     : {env_keys} (Werte ausgeblendet){'; reduzierte Umgebung' if clean_env else ''}",
        f"  Timeouts: Start {spec.startup_timeout:.0f}s, Tool {spec.tool_timeout:.0f}s",
        "",
    ]
    labels = {"OK": "[OK]    ", "WARN": "[WARN]  ", "FAIL": "[FEHLER]"}
    for event in report.events:
        prefix = f"{event.code}: " if event.code else ""
        lines.append(f"{labels[event.level]} {prefix}{event.text}")
    if report.failed or report.codes("WARN"):
        if report.stderr_tail:
            lines += ["", "stderr (letzte Zeilen, Geheimnisse maskiert):"]
            lines += [f"  | {line}" for line in report.stderr_tail]
        hints = [code for code in dict.fromkeys(report.codes()) if code in HINTS]
        if hints:
            lines += ["", "Hinweise:"] + [f"  {code}: {HINTS[code]}" for code in hints]
    lines += ["", "Ergebnis: " + ("FEHLER" if report.failed else "OK")]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prueft einen stdio-MCP-Server wie ein MCP-Client (Handshake, tools/list, "
                    "optional ein lesender Tool-Aufruf).",
    )
    parser.add_argument("--codex-server", metavar="NAME", help="Server aus der Codex config.toml laden")
    parser.add_argument("--codex-config", metavar="PATH", type=Path, help="Pfad zur Codex config.toml")
    parser.add_argument("--timeout", type=float, help="Start-Timeout in Sekunden (ueberschreibt Konfiguration)")
    parser.add_argument("--tool-timeout", type=float, help="Timeout je Anfrage nach dem Start in Sekunden")
    parser.add_argument("--cwd", help="Arbeitsverzeichnis fuer den Server")
    parser.add_argument("--env", action="append", default=[], metavar="KEY=VALUE",
                        help="zusaetzliche Umgebungsvariable, z. B. PYTHONUTF8=1")
    parser.add_argument("--clean-env", action="store_true",
                        help="nur System-Basisvariablen plus Konfigurations-env weitergeben")
    parser.add_argument("--call", metavar="TOOL", help="ein lesendes Tool aufrufen")
    parser.add_argument("--arg", action="append", default=[], metavar="KEY=VALUE",
                        help="Tool-Argument; Werte werden als JSON gelesen, sonst als Text")
    parser.add_argument("--show-schemas", action="store_true", help="Parameter aller Tools anzeigen")
    parser.add_argument("command", nargs=argparse.REMAINDER,
                        help="Serverbefehl nach '--', falls keine Codex-Konfiguration genutzt wird")
    return parser


def resolve_spec(opts: argparse.Namespace) -> ServerSpec:
    command = opts.command[1:] if opts.command[:1] == ["--"] else opts.command
    if opts.codex_server and command:
        raise ConfigError("Entweder --codex-server oder einen Befehl nach '--' angeben, nicht beides.")
    if opts.codex_server:
        spec = load_codex_server(opts.codex_config or default_codex_config(), opts.codex_server)
    elif command:
        spec = ServerSpec(command=command[0], args=command[1:])
    else:
        raise ConfigError("Kein Server angegeben: --codex-server NAME oder -- BEFEHL ...")
    spec.env.update(parse_assignments(opts.env, json_values=False))
    if opts.cwd:
        spec.cwd = opts.cwd
    if opts.timeout:
        spec.startup_timeout = opts.timeout
    if opts.tool_timeout:
        spec.tool_timeout = opts.tool_timeout
    return spec


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    opts = build_parser().parse_args(argv)
    try:
        if opts.call and is_write_tool(opts.call):
            raise ConfigError(f"'{opts.call}' sieht nach einem schreibenden Tool aus; die Probe ruft nur "
                              "lesende Tools auf.")
        spec = resolve_spec(opts)
        call_args = parse_assignments(opts.arg, json_values=True)
    except ConfigError as exc:
        print(f"Konfigurationsfehler: {exc}", file=sys.stderr)
        return 2
    report = run_probe(spec, call=opts.call, call_args=call_args,
                       clean_env=opts.clean_env, show_schemas=opts.show_schemas)
    print(render(spec, report, opts.clean_env))
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main())
