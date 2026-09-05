from pathlib import Path
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]


class InsightContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.questions = (
            SKILL_DIR / "references" / "question-templates.md"
        ).read_text(encoding="utf-8")
        cls.autonomous = (
            SKILL_DIR / "references" / "autonomous-mode.md"
        ).read_text(encoding="utf-8")
        cls.outline = (SKILL_DIR / "references" / "outline-contract.md").read_text(
            encoding="utf-8"
        )

    def test_insight_uses_report_selected_topic_and_local_sources(self):
        for phrase in ("本周选题报告", "选定的主题", "source-manifest.md", "本地原始素材"):
            self.assertIn(phrase, self.skill)

    def test_collaborative_mode_interviews_and_waits(self):
        for phrase in (
            "`collaborative`",
            "不替用户决定本周写哪一篇",
            "有依赖关系的决定",
            "最多三个问题",
            "编辑建议",
            "等待用户回答",
            "outline_status: user_confirmed",
        ):
            self.assertIn(phrase, self.skill)
        self.assertIn("Agent 自己读取文件和核对事实", self.questions)

    def test_autonomous_mode_generates_and_scores_multiple_theses(self):
        for phrase in (
            "`autonomous`",
            "2–4 个观点候选",
            "证据强度",
            "方法密度",
            "读者价值",
            "可写性",
            "重复风险",
            "outline_status: autonomous_ready",
        ):
            self.assertIn(phrase, self.skill + self.autonomous)

    def test_autonomous_mode_never_impersonates_user(self):
        for phrase in (
            "opinion_origin: agent_synthesis",
            "不是用户观点",
            "不得虚构用户的第一人称经历",
            "source_only",
            "not_required",
        ):
            self.assertIn(phrase, self.skill + self.autonomous)

    def test_unique_or_contrarian_angle_is_not_required(self):
        self.assertIn("文章不必拥有刻意制造的独特角度", self.skill)
        self.assertIn("优秀实践的忠实总结", self.skill)
        self.assertIn("不把“独特”“反直觉”作为硬门槛", self.skill)

    def test_complete_outline_is_the_writer_handoff(self):
        self.assertIn("article-outline.md", self.skill)
        for phrase in (
            "核心观点或核心价值",
            "风格确认",
            "完整结构",
            "预计篇幅",
            "authorship_mode",
            "opinion_origin",
            "user_confirmed",
            "autonomous_ready",
        ):
            self.assertIn(phrase, self.outline)

    def test_insight_does_not_write_article_body(self):
        self.assertIn("不写正文段落", self.skill)
        self.assertIn("不为了展示风格提前生成开头和结尾成稿", self.skill)


if __name__ == "__main__":
    unittest.main()
