from pathlib import Path
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]


class RadarContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.weekly = (SKILL_DIR / "references" / "weekly-report.md").read_text(
            encoding="utf-8"
        )
        cls.selection = (
            SKILL_DIR / "references" / "source-selection.md"
        ).read_text(encoding="utf-8")

    def test_radar_combines_search_local_analysis_and_weekly_recommendation(self):
        for phrase in ("`weekly`", "本地素材库", "5–8 个候选", "推荐本周优先写的 1–2 个"):
            self.assertIn(phrase, self.skill)

    def test_weekly_window_and_source_priority_are_explicit(self):
        for phrase in ("滚动 21 天", "最近 14 天", "AI 领域知名实践者", "用户关注博主", "长帖"):
            self.assertIn(phrase, self.skill)
        for organization in ("Anthropic / Claude", "OpenAI", "Google DeepMind", "GitHub"):
            self.assertIn(organization, self.skill)
        self.assertIn("published", self.skill)
        self.assertIn("UNVERIFIED", self.skill)

    def test_weekly_topic_cards_cover_editorial_recommendation_fields(self):
        for phrase in (
            "原始标题或核心话题",
            "作者及来源",
            "热度或讨论度依据",
            "核心观点摘要",
            "为什么值得写成公众号文章",
            "建议的中文文章切入角度与标题",
            "可进一步深挖的争议点或工程问题",
        ):
            self.assertIn(phrase, self.weekly)
        self.assertIn("避免连续多天推荐相同内容或高度相似话题", self.skill)

    def test_two_is_depth_not_a_quota(self):
        self.assertIn("`TWO` 是深度判断，不是数量指标", self.skill)
        self.assertIn("每周不设 `TWO` 配额", self.skill)
        self.assertIn("TWO-A", self.weekly)
        self.assertIn("TWO-B", self.weekly)

    def test_report_is_saved_and_returned_in_full(self):
        self.assertIn(r"D:\0-brain\raw\素材池\选题指南", self.skill)
        self.assertIn("完整报告同时返回聊天", self.skill)
        self.assertIn("不覆盖旧报告", self.weekly)

    def test_original_sources_are_not_archived_by_default(self):
        self.assertIn("默认不归档原文", self.skill)
        self.assertIn("只有用户给出精确目标目录", self.skill)
        self.assertIn("调用 `ni-url2md`", self.skill)

    def test_radar_stays_out_of_article_writing(self):
        self.assertIn("不写公众号正文", self.skill)
        self.assertIn("不把来源总结冒充用户观点", self.skill)
        for excluded in ("工具清单", "产品推荐", "促销", "广告", "软文", "纯新闻搬运"):
            self.assertIn(excluded, self.skill)

    def test_evidence_mode_accepts_both_outline_modes(self):
        self.assertIn("user_confirmed", self.skill)
        self.assertIn("autonomous_ready", self.skill)
        self.assertIn("自主模式重新生成并筛选观点候选", self.skill)

    def test_last30days_is_optional_and_uses_agent_mode(self):
        for phrase in (
            "/last30days",
            "--days=14",
            "--agent",
            "--register=dev",
            "完整调用、预检、来源和输出契约",
        ):
            self.assertIn(phrase, self.skill)

    def test_last30days_topic_stays_narrow_and_article_anchored(self):
        for phrase in (
            "参考文章作为锚点",
            "具体对象 + 工程动作或机制 + 具体问题、结果或边界",
            "主题太大",
            "紧贴参考文章",
        ):
            self.assertIn(phrase, self.skill + self.selection)
        for field in ("参考文章锚点", "深化主题", "分析方式", "系统分析摘要", "覆盖限制"):
            self.assertIn(field, self.weekly)

    def test_last30days_missing_or_unusable_falls_back_transparently(self):
        for phrase in (
            "未安装",
            "ni-radar` 自行分析",
            "不在本流程中安装或配置",
            "分析方式: ni-radar fallback",
            "不得声称已经完成 `/last30days` 系统分析",
        ):
            self.assertIn(phrase, self.skill)


if __name__ == "__main__":
    unittest.main()
