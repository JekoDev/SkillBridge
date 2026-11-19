"""User-approved discovery roots, not a global filesystem crawler."""
import json
import os
from pathlib import Path
from .core import SkillBridgeError

CONFIG = Path(os.environ.get('SKILLBRIDGE_CONFIG', str(Path.home() / '.config' / 'skillbridge' / 'registry.json')))

def roots():
    try:
        obj = json.loads(CONFIG.read_text(encoding='utf-8'))
        if not isinstance(obj, dict) or not isinstance(obj.get('roots'), list):
            raise ValueError('invalid registry')
        return [str(Path(p).expanduser().resolve()) for p in obj['roots'] if isinstance(p, str)]
    except FileNotFoundError:
        return []
    except (OSError, ValueError) as exc:
        raise SkillBridgeError(f'Invalid registry: {exc}') from exc

def add_root(path):
    p = Path(path).expanduser().resolve()
    if not p.is_dir():
        raise SkillBridgeError(f'Not a directory: {p}')
    all_roots = list(dict.fromkeys([*roots(), str(p)]))
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps({'roots': all_roots}, indent=2), encoding='utf-8')
    return all_roots
