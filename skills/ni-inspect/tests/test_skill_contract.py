from pathlib import Path
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]


class InspectContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.rules = (SKILL_DIR / "references" / "check-rules.md").read_text(
            encoding="utf-8"
        )

    def test_inspect_accepts_raw_article_inputs(self):
        for phrase in ("article.md", "article-outline.md", "practice-record.md"):
            self.assertIn(phrase, self.skill)
        self.assertNotIn("ni-formatter", self.skill)
        self.assertNotIn("verdict", self.skill)

    def test_inspect_checks_practice_and_key_links(self):
        for phrase in ("实践声明", "关键链接", "伪造来源", "未实践内容写成亲历"):
            self.assertIn(phrase, self.skill + self.rules)


if __name__ == "__main__":
    unittest.main()
