import tempfile
import unittest
from pathlib import Path
from skillbridge.project_inspect import inspect_project
from skillbridge.core import SkillBridgeError

class ProjectInspectTests(unittest.TestCase):
    def test_read_only_detection(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "pyproject.toml").write_text("[project]\nname='demo'\n")
            (root / "package.json").write_text("{}")
            (root / ".env").write_text("TOP_SECRET")
            result = inspect_project(d)
            self.assertEqual(result["stacks"], ["Python", "JavaScript/TypeScript"])
            self.assertNotIn("TOP_SECRET", str(result))
            self.assertIsNone(result["existing_skillbridge_manifest"])
    def test_invalid_path(self):
        with self.assertRaises(SkillBridgeError):
            inspect_project("/nonexistent-skillbridge-project-zz")
    def test_manifest_validation(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "skillbridge.json").write_text('{"app":"Demo","skills":[]}')
            self.assertTrue(inspect_project(d)["existing_skillbridge_manifest"]["valid"])
