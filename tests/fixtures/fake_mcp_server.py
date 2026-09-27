"""Minimal stdio MCP server with switchable failure modes for mcp_stdio_probe tests."""
import json
import os
import sys
import time

MODE = sys.argv[1] if len(sys.argv) > 1 else "healthy"
TOOLS = [
    {"name": "list_accounts", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "search_mail", "inputSchema": {
        "type": "object",
        "properties": {"query": {"type": "string"}, "limit": {"type": "integer"}},
        "required": ["query"],
    }},
    {"name": "move_mail", "inputSchema": {"type": "object", "properties": {}}},
]


def send(message):
    sys.stdout.buffer.write((json.dumps(message) + "\n").encode("utf-8"))
    sys.stdout.buffer.flush()


def reply(request, result):
    send({"jsonrpc": "2.0", "id": request["id"], "result": result})


if MODE == "crash_on_start":
    print("Traceback (most recent call last):", file=sys.stderr)
    print("ModuleNotFoundError: No module named 'mcp'", file=sys.stderr)
    sys.exit(1)
if MODE == "pollute":
    print("Verbinde Postfach ...")
    sys.stdout.flush()

for line in sys.stdin.buffer:
    request = json.loads(line)
    method = request.get("method")
    if "id" not in request:
        continue
    if method == "initialize":
        if MODE == "slow_init":
            time.sleep(5)
        if MODE == "close_stdout":
            sys.stdout.flush()
            os.close(1)
            time.sleep(30)
        reply(request, {
            "protocolVersion": request["params"]["protocolVersion"],
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "fake-mail", "version": "0.1"},
        })
    elif method == "tools/list":
        reply(request, {"tools": TOOLS})
    elif method == "tools/call":
        name = request["params"]["name"]
        if MODE == "crash_on_call":
            print("imaplib.error: LOGIN user@example.com hunter2 failed", file=sys.stderr)
            print("password=hunter2", file=sys.stderr)
            sys.exit(3)
        if MODE == "bad_utf8":
            sys.stdout.buffer.write("Betreff: Grüße\n".encode("cp1252"))
            sys.stdout.buffer.flush()
        if MODE == "tool_error":
            reply(request, {"content": [{"type": "text", "text": "Konto nicht erreichbar"}], "isError": True})
            continue
        text = f"{name}: " + json.dumps(request["params"].get("arguments", {}), sort_keys=True)
        reply(request, {"content": [{"type": "text", "text": text}]})

if MODE == "ignore_eof":
    time.sleep(30)
