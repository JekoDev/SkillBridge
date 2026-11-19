import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from skillbridge.registry import roots, add_root
from skillbridge.transport import resolve
from skillbridge.forge import ForgeAdapter
from skillbridge.core import SkillBridgeError

class Features(unittest.TestCase):
    def test_roots(self):
        with tempfile.TemporaryDirectory() as d:
            with patch('skillbridge.registry.CONFIG', Path(d)/'config.json'):
                self.assertEqual(roots(), [])
                self.assertEqual(add_root(d), [str(Path(d).resolve())])
    def test_auto(self):
        target = Path(__file__).resolve().parents[1]/'examples/autodiscovery'
        result = resolve('TestApp', [str(target)])
        self.assertEqual(result['transport'], 'local-manifest')
    def test_forge_denies(self):
        target = Path(__file__).resolve().parents[1]/'examples/autodiscovery'
        adapter = ForgeAdapter('TestApp', [str(target)])
        with self.assertRaises(SkillBridgeError):
            adapter.call('anything', {}, approved=False)

if __name__ == '__main__': unittest.main()
