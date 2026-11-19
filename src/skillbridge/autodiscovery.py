"""Conservative local app discovery: explicit roots, no network or execution."""
from __future__ import annotations
import os
from pathlib import Path
from .core import discover, SkillBridgeError

MARKERS = ('skillbridge.json', 'SKILL.md', 'AGENT.md', 'README.md')

def connect(target: str, roots=(), *, max_depth: int = 2) -> dict:
    """Resolve an app name or filesystem path, then load its capabilities.

    Name lookup searches only the given roots (or SKILLBRIDGE_PATH); it never
    probes arbitrary hosts, installs packages, or runs app commands.
    """
    candidate = Path(target).expanduser()
    if candidate.exists():
        return _describe(candidate)
    if candidate.is_absolute() or '/' in target or '\\' in target or target in ('.', '..'):
        raise SkillBridgeError(f'App path not found: {target}')
    if not roots:
        from .registry import roots as saved_roots
        roots = [*saved_roots(), *filter(None, os.environ.get('SKILLBRIDGE_PATH', '').split(os.pathsep))]
    matches = []
    for root in roots:
        base = Path(root).expanduser().resolve()
        if not base.is_dir():
            continue
        for path in [base, *list(base.iterdir())[:500]]:
            if path.is_dir() and path.name.casefold() == target.casefold():
                matches.append(path)
            elif path.is_dir() and max_depth >= 2:
                for child in list(path.iterdir())[:500]:
                    if child.is_dir() and child.name.casefold() == target.casefold():
                        matches.append(child)
    unique = list(dict.fromkeys(p.resolve() for p in matches))
    if not unique:
        raise SkillBridgeError(f'App {target!r} not found in configured roots; set SKILLBRIDGE_PATH or use --root')
    if len(unique) > 1:
        raise SkillBridgeError('Ambiguous app name; use full path: ' + ', '.join(map(str, unique)))
    return _describe(unique[0])

def _describe(path: Path) -> dict:
    manifest = discover(path)
    return {
        'app': manifest['app'],
        'location': str(path.resolve()),
        'source': manifest['_manifest_path'],
        'skills': [{k: v for k, v in skill.items() if k in ('name', 'description', 'type', 'inputs')} for skill in manifest['skills']],
        'execution': 'disabled-by-default',
    }
