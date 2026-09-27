"""Tests for scripts/mcp_stdio_probe.py. Run: python -m unittest discover -s tests"""
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import mcp_stdio_probe as probe  # noqa: E402

FAKE_SERVER = str(ROOT / "tests" / "fixtures" / "fake_mcp_server.py")


def spec(mode, **overrides):
    values = {"command": sys.executable, "args": [FAKE_SERVER, mode],
              "startup_timeout": 10.0, "tool_timeout": 10.0}
    values.update(overrides)
    return probe.ServerSpec(**values)


class RunProbeTests(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(probe, "SHUTDOWN_GRACE", 1.0)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_healthy_server_passes_handshake_and_read_call(self):
        report = probe.run_probe(spec("healthy"), call="search_mail", call_args={"query": "Herrmann", "limit": 1})
        self.assertFalse(report.failed, report.events)
        self.assertEqual(report.tool_names, ["list_accounts", "search_mail", "move_mail"])
        self.assertIn('search_mail: {"limit": 1, "query": "Herrmann"}', report.events[-2].text)
        self.assertEqual(report.exit_code, 0)

    def test_crash_on_start_reports_exit_and_stderr(self):
        report = probe.run_probe(spec("crash_on_start"))
        self.assertEqual(report.codes("FAIL"), ["SERVER_EXITED"])
        self.assertIn("Exit-Code 1", report.events[-1].text)
        self.assertIn("ModuleNotFoundError: No module named 'mcp'", report.stderr_tail)

    def test_crash_during_tool_call_is_reported_and_secrets_masked(self):
        report = probe.run_probe(spec("crash_on_call"), call="list_accounts")
        self.assertEqual(report.codes("FAIL"), ["SERVER_EXITED"])
        self.assertIn("tools/call list_accounts", report.events[-1].text)
        tail = "\n".join(report.stderr_tail)
        self.assertNotIn("hunter2", tail)
        self.assertIn("password=***", tail)

    def test_stdout_pollution_is_a_failure(self):
        report = probe.run_probe(spec("pollute"))
        self.assertEqual(report.codes("FAIL"), ["STDOUT_NOT_JSON"])
        self.assertIn("Verbinde Postfach", report.events[-1].text)

    def test_non_utf8_stdout_is_a_failure(self):
        report = probe.run_probe(spec("bad_utf8"), call="search_mail", call_args={"query": "x"})
        self.assertEqual(report.codes("FAIL"), ["INVALID_UTF8"])

    def test_slow_initialize_times_out(self):
        report = probe.run_probe(spec("slow_init", startup_timeout=1.0))
        self.assertEqual(report.codes("FAIL"), ["TIMEOUT"])

    def test_closed_stdout_with_live_process(self):
        report = probe.run_probe(spec("close_stdout"))
        self.assertEqual(report.codes("FAIL"), ["STDOUT_CLOSED"])

    def test_tool_error_and_unknown_tool(self):
        self.assertEqual(probe.run_probe(spec("tool_error"), call="list_accounts").codes("FAIL"), ["TOOL_ERROR"])
        self.assertEqual(probe.run_probe(spec("healthy"), call="nope").codes("FAIL"), ["TOOL_NOT_FOUND"])

    def test_server_that_ignores_stdin_eof_is_warned(self):
        report = probe.run_probe(spec("ignore_eof"))
        self.assertFalse(report.failed)
        self.assertEqual(report.codes("WARN"), ["NO_EXIT_ON_STDIN_EOF"])

    def test_missing_command_reports_spawn_failure(self):
        report = probe.run_probe(probe.ServerSpec(command=str(ROOT / "does-not-exist.exe")))
        self.assertEqual(report.codes("FAIL"), ["SPAWN_FAILED"])


class ConfigTests(unittest.TestCase):
    def write_config(self, text):
        handle = tempfile.NamedTemporaryFile("w", suffix=".toml", delete=False, encoding="utf-8")
        handle.write(text)
        handle.close()
        self.addCleanup(Path(handle.name).unlink)
        return Path(handle.name)

    def test_loads_codex_server_entry(self):
        path = self.write_config(
            '[mcp_servers.mail_leanstech]\n'
            'command = "C:\\\\Python314\\\\python.exe"\n'
            'args = ["C:\\\\Users\\\\semir\\\\Documents\\\\MailManager\\\\mail_mcp.py"]\n'
            'startup_timeout_sec = 60\n'
            'env = { PYTHONUTF8 = "1" }\n'
        )
        loaded = probe.load_codex_server(path, "mail_leanstech")
        self.assertEqual(loaded.command, "C:\\Python314\\python.exe")
        self.assertEqual(loaded.args, ["C:\\Users\\semir\\Documents\\MailManager\\mail_mcp.py"])
        self.assertEqual(loaded.env, {"PYTHONUTF8": "1"})
        self.assertEqual(loaded.startup_timeout, 60.0)

    def test_legacy_millisecond_timeout_and_unknown_server(self):
        path = self.write_config('[mcp_servers.a]\ncommand = "x"\nstartup_timeout_ms = 20000\n')
        self.assertEqual(probe.load_codex_server(path, "a").startup_timeout, 20.0)
        with self.assertRaisesRegex(probe.ConfigError, "Vorhanden: a"):
            probe.load_codex_server(path, "mail_leanstech")


class HelperTests(unittest.TestCase):
    def test_write_tools_are_refused(self):
        for name in ("move_mail", "sendMail", "delete-message", "sort_mails", "mark_read"):
            self.assertTrue(probe.is_write_tool(name), name)
        for name in ("list_accounts", "search_mail", "get_message", "listFolders"):
            self.assertFalse(probe.is_write_tool(name), name)

    def test_redaction(self):
        self.assertEqual(probe.redact('"password": "geheim 1"'), '"password": ***')
        self.assertEqual(probe.redact("Authorization: Bearer abc.def"), "Authorization: Bearer ***")
        self.assertEqual(probe.redact("LOGIN user@x.de geheim"), "LOGIN user@x.de ***")
        self.assertEqual(probe.redact("Passwort=abc"), "Passwort=***")

    def test_arg_parsing_reads_json_values(self):
        parsed = probe.parse_assignments(["limit=1", "query=Herrmann", "folder=S Klima"], json_values=True)
        self.assertEqual(parsed, {"limit": 1, "query": "Herrmann", "folder": "S Klima"})


class CliTests(unittest.TestCase):
    def run_cli(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = probe.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_cli_with_command_after_double_dash(self):
        code, out, _ = self.run_cli(["--call", "list_accounts", "--", sys.executable, FAKE_SERVER, "healthy"])
        self.assertEqual(code, 0, out)
        self.assertIn("Ergebnis: OK", out)
        out.encode("ascii")  # output must survive cp1252/cp850 pipes

    def test_cli_refuses_write_tool_before_starting_server(self):
        code, out, err = self.run_cli(["--call", "move_mail", "--", sys.executable, FAKE_SERVER, "healthy"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("schreibenden Tool", err)

    def test_cli_failure_shows_stderr_and_hint(self):
        code, out, _ = self.run_cli(["--", sys.executable, FAKE_SERVER, "crash_on_start"])
        self.assertEqual(code, 1)
        self.assertIn("No module named 'mcp'", out)
        self.assertIn("Hinweise:", out)
        self.assertIn("Ergebnis: FEHLER", out)


if __name__ == "__main__":
    unittest.main()
