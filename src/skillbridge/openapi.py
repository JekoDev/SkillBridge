"""Read-only OpenAPI capability discovery; no remote execution."""
import json
from pathlib import Path
from .core import SkillBridgeError

def discover_openapi(path):
    p = Path(path).expanduser().resolve()
    try:
        spec = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SkillBridgeError(f"Cannot read OpenAPI JSON: {exc}") from exc
    if not isinstance(spec, dict) or not (str(spec.get("openapi", "")).startswith("3.")):
        raise SkillBridgeError("Expected OpenAPI 3.x JSON")
    skills = []
    for route, methods in spec.get("paths", {}).items():
        if not isinstance(methods, dict):
            continue
        for method, operation in methods.items():
            if method.lower() not in ("get", "post", "put", "patch", "delete") or not isinstance(operation, dict):
                continue
            name = operation.get("operationId") or f"{method}_{route}"
            skills.append({"name": name, "description": operation.get("summary", operation.get("description", "")), "type": "documentation", "method": method.upper(), "path": route})
    return {"app": spec.get("info", {}).get("title", p.stem), "skills": skills, "_manifest_path": str(p)}
