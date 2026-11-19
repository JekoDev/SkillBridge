"""Conservative transport resolution. Never silently fetch URLs or execute commands."""
from pathlib import Path
from .core import discover, SkillBridgeError
from .openapi import discover_openapi
from .autodiscovery import connect

def resolve(target, roots=()):
    p = Path(target).expanduser()
    if p.is_file() and p.name.lower() in ('openapi.json', 'swagger.json'):
        manifest = discover_openapi(p)
        return {'transport': 'openapi-document', 'app': manifest['app'], 'skills': manifest['skills'], 'executable': False}
    info = connect(target, roots)
    manifest = discover(info['location'])
    return {'transport': 'local-manifest', 'app': info['app'], 'location': info['location'], 'skills': info['skills'], 'executable': any(s['type'] == 'command' for s in manifest['skills'])}
