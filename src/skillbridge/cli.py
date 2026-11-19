"""CLI for discovery, inspection, and explicitly authorized execution."""
import argparse
import json
import sys
from .core import SkillBridgeError, discover, invoke
from .openapi import discover_openapi
from .mcp import serve_stdio
from .autodiscovery import connect
from .agent import chat, tools_for
from .transport import resolve
from .system_discovery import connect_system, system_roots
from .wasm import run_wasi
from .registry import add_root, roots as saved_roots
from .project_inspect import inspect_project

def main():
    parser = argparse.ArgumentParser(prog="skillbridge", description="Discover app skills from a local manifest or Markdown")
    sub = parser.add_subparsers(dest="action", required=True)
    for command in ("discover", "inspect"):
        sub.add_parser(command).add_argument("location")
    conn = sub.add_parser("connect", help="Resolve a local app name or path without executing code")
    conn.add_argument("target")
    conn.add_argument("--root", action="append", default=[], help="Trusted search root (repeatable)")
    agent = sub.add_parser("agent", help="Interactive agent connected to a local app via LM Studio")
    agent.add_argument("target")
    agent.add_argument("--root", action="append", default=[])
    agent.add_argument("--endpoint", default="http://127.0.0.1:1234/v1")
    agent.add_argument("--model", default="local-model")
    oa = sub.add_parser("openapi", help="Discover operations from a local OpenAPI 3 JSON file")
    oa.add_argument("location")
    mcp = sub.add_parser("mcp", help="Serve a manifest over MCP stdio")
    mcp.add_argument("location")
    mcp.add_argument("--allow-execute", action="store_true")
    call = sub.add_parser("call")
    call.add_argument("location")
    call.add_argument("skill")
    call.add_argument("--args", default="{}", help="JSON object")
    call.add_argument("--allow-execute", action="store_true", help="Explicitly authorize command execution")
    rootcmd = sub.add_parser("roots", help="Show or register explicit discovery roots")
    rootcmd.add_argument("--add", metavar="PATH")
    auto = sub.add_parser("auto", help="Select a safe discovery transport without executing")
    auto.add_argument("target")
    auto.add_argument("--root", action="append", default=[])
    sysconn = sub.add_parser('system-connect', help='Opt-in discovery of installed app folders')
    sysconn.add_argument('target')
    sub.add_parser('system-roots', help='List opt-in operating system search roots')
    wasm = sub.add_parser('wasm', help='Run a WASI module with no preopened directories (requires wasmtime)')
    wasm.add_argument('module')
    project = sub.add_parser("inspect-project", help="Read-only project analysis for coding agents")
    project.add_argument("path", nargs="?", default=".")
    args = parser.parse_args()
    try:
        if args.action == "inspect-project":
            print(json.dumps(inspect_project(args.path), ensure_ascii=False, indent=2))
            return 0
        if args.action == 'system-roots':
            print(json.dumps({'roots':system_roots()}, indent=2))
            return 0
        if args.action == 'system-connect':
            print(json.dumps(connect_system(args.target), indent=2))
            return 0
        if args.action == 'wasm':
            print(json.dumps(run_wasi(args.module), indent=2))
            return 0
        if args.action == "roots":
            print(json.dumps({'roots': add_root(args.add) if args.add else saved_roots()}, indent=2))
            return 0
        if args.action == "auto":
            print(json.dumps(resolve(args.target, args.root), ensure_ascii=False, indent=2))
            return 0
        if args.action == "agent":
            chat(args.target, args.root, endpoint=args.endpoint, model=args.model)
            return 0
        if args.action == "connect":
            print(json.dumps(connect(args.target, args.root), ensure_ascii=False, indent=2))
            return 0
        if args.action == "mcp":
            serve_stdio(args.location, allow_execute=args.allow_execute)
            return 0
        manifest = discover_openapi(args.location) if args.action == "openapi" else discover(args.location)
        if args.action in ("discover", "openapi"):
            result = {"app": manifest["app"], "skills": [{k: v for k, v in s.items() if k in ("name", "description", "type", "inputs")} for s in manifest["skills"]]}
        elif args.action == "inspect":
            result = {k: v for k, v in manifest.items() if not k.startswith("_")}
        else:
            result = invoke(manifest, args.skill, json.loads(args.args), allow_execute=args.allow_execute)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (SkillBridgeError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
