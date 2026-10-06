import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = SKILL_DIR.parents[1]


class SkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    def test_frontmatter_name_matches_folder(self):
        match = re.match(r"^---\n(.*?)\n---\n", self.skill, re.DOTALL)
        self.assertIsNotNone(match)
        self.assertIn("name: ni-explain", match.group(1))
        self.assertIn("description:", match.group(1))

    def test_readme_pair_exists(self):
        self.assertTrue((SKILL_DIR / "README.md").is_file())
        self.assertTrue((SKILL_DIR / "README.en.md").is_file())

    def test_references_present(self):
        for name in ("rules-zh.md", "explain-patterns.md", "output-template.md"):
            self.assertTrue((SKILL_DIR / "references" / name).is_file(), name)
        self.assertTrue((SKILL_DIR / "scripts" / "check.py").is_file())

    def test_registered_and_version_consistent(self):
        codex = json.loads(
            (REPO_DIR / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        claude = json.loads(
            (REPO_DIR / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
        )
        self.assertRegex(codex["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual(codex["version"], claude["metadata"]["version"])
        self.assertIn("./skills/ni-explain", claude["plugins"][0]["skills"])

    def test_tech_report_boundary_documented(self):
        for required in ("ni-tech-report", "框架句豁免", "不碰判断"):
            self.assertIn(required, self.skill)

    def test_offline_smoke_suite_passes(self):
        result = subprocess.run(
            [sys.executable, str(SKILL_DIR / "tests" / "smoke_test.py")],
            capture_output=True, text=True, timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
