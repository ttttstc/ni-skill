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
        self.assertIn("name: ni-book-downloader", match.group(1))
        self.assertIn("description:", match.group(1))

    def test_readme_pair_exists(self):
        self.assertTrue((SKILL_DIR / "README.md").is_file())
        self.assertTrue((SKILL_DIR / "README.en.md").is_file())

    def test_registered_and_version_consistent(self):
        codex = json.loads(
            (REPO_DIR / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        claude = json.loads(
            (REPO_DIR / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
        )
        self.assertRegex(codex["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual(codex["version"], claude["metadata"]["version"])
        self.assertIn("./skills/ni-book-downloader", claude["plugins"][0]["skills"])

    def test_format_semantics_are_explicit(self):
        for required in (
            "--format text",
            "--format pdf",
            "全量格式",
            "epub",
            "mobi",
            "azw3",
            "fb2",
            "txt",
        ):
            self.assertIn(required, self.skill)

    def test_source_order_is_no_quota_first(self):
        order = ["GitHub", "LibGen", "Z-Library", "Anna", "全网搜索"]
        positions = [self.skill.index(name) for name in order]
        self.assertEqual(positions, sorted(positions))

    def test_offline_smoke_suite_passes(self):
        result = subprocess.run(
            [sys.executable, str(SKILL_DIR / "tests" / "smoke_test.py")],
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
