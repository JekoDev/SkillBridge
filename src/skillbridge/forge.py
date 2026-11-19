"""Framework-neutral Forge adapter: JSON tool schema + dispatch with explicit authorization."""
from .agent import tools_for
from .autodiscovery import connect
from .core import discover, invoke, SkillBridgeError

class ForgeAdapter:
    def __init__(self, target, roots=()):
        self.info = connect(target, roots)
        self.manifest = discover(self.info['location'])

    def tools(self):
        return tools_for(self.manifest)

    def call(self, name, arguments, *, approved=False):
        if not approved:
            raise SkillBridgeError('Explicit user approval required')
        return invoke(self.manifest, name, arguments, allow_execute=True)
