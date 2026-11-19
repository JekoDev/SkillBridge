"""Manifest-based discovery and intentionally restricted execution."""
from __future__ import annotations
import json
import re
import subprocess
from pathlib import Path
from typing import Any

class SkillBridgeError(Exception):
    pass

NAME = re.compile(r"^[a-zA-Z][a-zA-Z0-9_.-]{0,79}$")

def load_manifest(path: str | Path) -> dict[str, Any]:
    p = Path(path).expanduser().resolve()
    if p.is_dir():
        p = p / "skillbridge.json"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SkillBridgeError(f"Cannot read manifest {p}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("app"), str) or not isinstance(data.get("skills"), list):
        raise SkillBridgeError("Manifest requires 'app' string and 'skills' array")
    names = set()
    for skill in data["skills"]:
        if not isinstance(skill, dict) or not isinstance(skill.get("name"), str) or not NAME.fullmatch(skill["name"]):
            raise SkillBridgeError("Each skill needs a valid name")
        if skill["name"] in names:
            raise SkillBridgeError("Duplicate skill name")
        names.add(skill["name"])
        if not isinstance(skill.get("description"), str):
            raise SkillBridgeError("Each skill needs a description")
        if skill.get("type") not in ("command", "documentation"):
            raise SkillBridgeError("Supported types: command, documentation")
        if skill["type"] == "command" and (not isinstance(skill.get("argv"), list) or not skill["argv"] or not all(isinstance(a, str) for a in skill["argv"])):
            raise SkillBridgeError("Command skills require argv string array")
    data["_manifest_path"] = str(p)
    return data

def discover(location: str | Path) -> dict[str, Any]:
    """Discover local manifests or Markdown docs; never execute during discovery."""
    p = Path(location).expanduser().resolve()
    if p.is_file() and p.suffix.lower() == ".md":
        return {"app": p.parent.name, "skills": [{"name": "documentation", "description": p.read_text(encoding="utf-8"), "type": "documentation"}], "_manifest_path": str(p)}
    if p.is_dir() and not (p / "skillbridge.json").exists():
        for filename in ("SKILL.md", "AGENT.md", "README.md"):
            if (p / filename).is_file():
                return discover(p / filename)
        raise SkillBridgeError(f"No skillbridge.json or skill documentation in {p}")
    return load_manifest(p)

def invoke(manifest: dict[str, Any], name: str, arguments: dict[str, Any], *, allow_execute: bool = False, timeout: int = 10) -> Any:
    """Execute only explicitly approved command skills; no shell interpolation."""
    skill = next((s for s in manifest["skills"] if s["name"] == name), None)
    if skill is None:
        raise SkillBridgeError(f"Unknown skill: {name}")
    if skill["type"] != "command":
        raise SkillBridgeError("Documentation skills cannot be executed")
    if not allow_execute:
        raise SkillBridgeError("Execution denied by default; pass --allow-execute to approve this invocation")
    if not isinstance(arguments, dict):
        raise SkillBridgeError("Arguments must be a JSON object")
    schema = skill.get("inputs", {})
    if not isinstance(schema, dict):
        raise SkillBridgeError("inputs must be an object")
    if set(arguments) - set(schema):
        raise SkillBridgeError("Unexpected input arguments")
    for key, kind in schema.items():
        if key not in arguments:
            raise SkillBridgeError(f"Missing argument: {key}")
        if kind not in ("string", "integer", "boolean"):
            raise SkillBridgeError(f"Unsupported input type: {kind}")
        value = arguments[key]
        if not ((kind == "string" and isinstance(value, str)) or (kind == "integer" and type(value) is int) or (kind == "boolean" and type(value) is bool)):
            raise SkillBridgeError(f"Invalid type for {key}: expected {kind}")
    argv = []
    for part in skill["argv"]:
        matches = re.findall(r"\{([a-zA-Z][a-zA-Z0-9_]*)\}", part)
        if "{" in part or "}" in part:
            if len(matches) != 1 or part != "{" + matches[0] + "}":
                raise SkillBridgeError("Arguments must occupy an entire argv element")
        if matches:
            key = matches[0]
            if key not in arguments:
                raise SkillBridgeError(f"Unknown placeholder: {key}")
            argv.append(str(arguments[key]).lower() if type(arguments[key]) is bool else str(arguments[key]))
        else:
            argv.append(part)
    base = Path(manifest["_manifest_path"]).parent
    try:
        result = subprocess.run(argv, cwd=base, capture_output=True, text=True, timeout=min(max(timeout, 1), 60), shell=False, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise SkillBridgeError(f"Execution failed: {exc}") from exc
    return {"exit_code": result.returncode, "stdout": result.stdout[:65536], "stderr": result.stderr[:65536]}
