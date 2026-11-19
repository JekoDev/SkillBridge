import json
from pathlib import Path
from skillbridge.openapi import discover_openapi
from skillbridge.mcp import dispatch
from skillbridge.core import discover

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "examples" / "manifests"

def test_openapi():
    d = discover_openapi(MANIFEST / "openapi.json")
    assert d["skills"][0]["name"] == "listUsers"

def test_mcp_list():
    d = discover(MANIFEST)
    r = dispatch({"jsonrpc":"2.0","id":1,"method":"tools/list"}, d)
    assert r["result"]["tools"][0]["name"] == "greet"

def test_mcp_denied_by_default():
    d = discover(MANIFEST)
    r = dispatch({"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"greet","arguments":{"name":"Forge"}}}, d)
    assert "Execution denied" in r["error"]["message"]

def test_mcp_initialize():
    d = discover(MANIFEST)
    r = dispatch({"jsonrpc":"2.0","id":3,"method":"initialize","params":{}}, d)
    assert "protocolVersion" in r["result"]
