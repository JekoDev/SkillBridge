"""Conservative, read-only project inventory for agent-assisted integrations."""
from pathlib import Path
from .core import SkillBridgeError

MARKERS = {
    "Python": ("pyproject.toml", "requirements.txt", "setup.py"),
    "JavaScript/TypeScript": ("package.json", "tsconfig.json"),
    "Rust": ("Cargo.toml",),
    "Go": ("go.mod",),
    "C#/.NET": ("*.csproj", "*.sln"),
    "Java": ("pom.xml", "build.gradle", "build.gradle.kts"),
    "C/C++": ("CMakeLists.txt", "meson.build"),
}
IGNORE = {".git", "node_modules", ".venv", "venv", "dist", "build", "target", "__pycache__"}


def inspect_project(path: str = ".") -> dict:
    root = Path(path).expanduser().resolve()
    if not root.is_dir():
        raise SkillBridgeError(f"Not a directory: {root}")
    # Top-level markers only: do not read arbitrary source files or secrets.
    names = {p.name for p in root.iterdir() if p.is_file() and not p.is_symlink()}
    stacks = []
    evidence = {}
    for stack, markers in MARKERS.items():
        found = sorted({name for marker in markers for name in names if (name == marker if '*' not in marker else __import__('fnmatch').fnmatch(name, marker))})
        if found:
            stacks.append(stack)
            evidence[stack] = found[:12]
    manifest = root / "skillbridge.json"
    from .core import load_manifest
    existing = None
    if manifest.is_file() and not manifest.is_symlink():
        try:
            parsed = load_manifest(manifest)
            existing = {"valid": True, "app": parsed["app"], "skills": [s["name"] for s in parsed["skills"]]}
        except SkillBridgeError as exc:
            existing = {"valid": False, "error": str(exc)}
    return {
        "project": str(root),
        "stacks": stacks,
        "evidence": evidence,
        "existing_skillbridge_manifest": existing,
        "suggested_next_steps": [
            "Inspect public application entry points and existing authorization checks",
            "Propose a small, read-only-first capability inventory for user approval",
            "Use official SkillBridge examples to implement a minimal adapter and manifest",
            "Run skillbridge inspect on the manifest, then project tests",
            "Do not execute write operations without explicit authorization"
        ],
        "read_only": True,
        "limitations": "Detects top-level build markers only; does not inspect functions, edit files, or execute code."
    }
