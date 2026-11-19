"""CLI for discovery, inspection, and explicitly authorized execution."""
import argparse
import json
import sys
from .core import SkillBridgeError, discover, invoke

def main():
    parser = argparse.ArgumentParser(prog="skillbridge", description="Discover app skills from a local manifest or Markdown")
    sub = parser.add_subparsers(dest="action", required=True)
    for command in ("discover", "inspect"):
        sub.add_parser(command).add_argument("location")
    call = sub.add_parser("call")
    call.add_argument("location")
    call.add_argument("skill")
    call.add_argument("--args", default="{}", help="JSON object")
    call.add_argument("--allow-execute", action="store_true", help="Explicitly authorize command execution")
    args = parser.parse_args()
    try:
        manifest = discover(args.location)
        if args.action == "discover":
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
