from pathlib import Path
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]


class UrlArchiveContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.script = (SKILL_DIR / "scripts" / "main.ts").read_text(encoding="utf-8")

    def test_archive_mode_requires_explicit_destination(self):
        self.assertIn("/素材收集库/{第几周}/", self.skill)
        self.assertIn("只有当上游明确给出目标目录并要求归档时", self.skill)

    def test_default_mode_does_not_archive_to_obsidian(self):
        self.assertIn("默认模式：只抓取，不归档", self.skill)
        self.assertIn("不会自动归档到 Obsidian", self.skill)
        self.assertIn("URL_DATA_DIR", self.skill)

    def test_explicit_output_is_safe_by_default(self):
        self.assertIn("overwrite: boolean", self.script)
        self.assertIn("overwrite: false", self.script)
        self.assertIn("--overwrite", self.script)
        self.assertIn("Refusing to overwrite existing file", self.script)


if __name__ == "__main__":
    unittest.main()
