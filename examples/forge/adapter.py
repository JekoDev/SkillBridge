"""Example host integration: Forge needs to register these tools in its own tool system."""
from skillbridge.forge import ForgeAdapter

bridge = ForgeAdapter('TestApp', roots=['examples/autodiscovery'])
print('Tools for Forge:', bridge.tools())
# When Forge requests a call, ask the human for approval first:
# result = bridge.call('greet', {'name': 'Forge'}, approved=user_confirmed)
