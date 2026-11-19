"""MCP JSON-RPC 2.0 stdio server. Stdout uses newline-delimited JSON per MCP specification."""
import json
import sys
from .core import discover, invoke, SkillBridgeError

def _schema(skill):
    inputs = skill.get("inputs", {})
    types = {"string": "string", "integer": "integer", "boolean": "boolean"}
    return {"type": "object", "properties": {k: {"type": types.get(v, "string")} for k, v in inputs.items()}, "required": list(inputs), "additionalProperties": False}

def dispatch(message, manifest, allow_execute=False):
    method = message.get("method")
    mid = message.get("id")
    if mid is None:
        return None
    try:
        if method == "initialize":
            result = {"protocolVersion": "2025-06-18", "capabilities": {"tools": {"listChanged": False}}, "serverInfo": {"name": "skillbridge", "version": "0.8.0"}}
        elif method == "ping":
            result = {}
        elif method == "tools/list":
            result = {"tools": [{"name": s["name"], "description": s["description"], "inputSchema": _schema(s)} for s in manifest["skills"] if s["type"] == "command"]}
        elif method == "tools/call":
            params = message.get("params") or {}
            outcome = invoke(manifest, params.get("name"), params.get("arguments", {}), allow_execute=allow_execute)
            result = {"content": [{"type": "text", "text": json.dumps(outcome)}], "isError": outcome["exit_code"] != 0}
        else:
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "Method not found"}}
        return {"jsonrpc": "2.0", "id": mid, "result": result}
    except (SkillBridgeError, ValueError, TypeError) as exc:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32000, "message": str(exc)}}

def _read_messages(stream):
    """Accept MCP Content-Length frames and legacy JSON-lines for local clients."""
    while True:
        first = stream.readline()
        if not first:
            return
        if first.lstrip().startswith(b"{"):
            try:
                yield json.loads(first)
            except ValueError:
                continue
            continue
        if not first.lower().startswith(b"content-length:"):
            continue
        try:
            size = int(first.split(b":", 1)[1].strip())
            if size < 1 or size > 4 * 1024 * 1024:
                return
            while True:
                header = stream.readline()
                if not header:
                    return
                if header in (b"\r\n", b"\n"):
                    break
            body = stream.read(size)
            if len(body) != size:
                return
            yield json.loads(body)
        except (ValueError, UnicodeError):
            continue

def serve_stdio(location, allow_execute=False):
    manifest = discover(location)
    for message in _read_messages(sys.stdin.buffer):
        if not isinstance(message, dict):
            continue
        response = dispatch(message, manifest, allow_execute)
        if response is not None:
            body = json.dumps(response, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
            sys.stdout.buffer.write(body + b'\n')
            sys.stdout.buffer.flush()
