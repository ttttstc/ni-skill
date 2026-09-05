from pathlib import Path
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]


class CoverPromptContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    def test_skill_stops_at_one_cover_prompt(self):
        self.assertIn("cover-prompt.md", self.skill)
        self.assertIn("只产出封面提示词", self.skill)
        self.assertNotIn("固定九张", self.skill)
        self.assertNotIn("1 张封面 + 9 张内文", self.skill)

    def test_prompt_must_be_grounded_in_article_entities(self):
        for phrase in ("真实实体", "核心判断", "不要添加正文没有的事实"):
            self.assertIn(phrase, self.skill)
        self.assertIn("article-outline.md", self.skill)


if __name__ == "__main__":
    unittest.main()
