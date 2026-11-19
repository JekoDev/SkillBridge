import json
import tempfile
import unittest
from pathlib import Path
from skillbridge import discover, invoke, SkillBridgeError

class CoreTests(unittest.TestCase):
    def test_discovery_and_execution_gate(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "skillbridge.json").write_text(json.dumps({"app": "Test", "skills": [{"name": "echo", "description": "Echo", "type": "command", "inputs": {"msg": "string"}, "argv": ["python", "-c", "import sys; print(sys.argv[1])", "{msg}"]}]}))
            m = discover(p)
            self.assertEqual(m["app"], "Test")
            with self.assertRaises(SkillBridgeError): invoke(m, "echo", {"msg": "hi"})
            self.assertIn("hi", invoke(m, "echo", {"msg": "hi"}, allow_execute=True)["stdout"])
            with self.assertRaises(SkillBridgeError): invoke(m, "echo", {"msg": "hi", "bad": "x"}, allow_execute=True)
    def test_markdown_discovery(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "SKILL.md"
            p.write_text("# A skill")
            self.assertEqual(discover(d)["skills"][0]["type"], "documentation")

if __name__ == "__main__": unittest.main()
