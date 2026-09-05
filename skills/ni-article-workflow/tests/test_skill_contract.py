from pathlib import Path
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]


class ArticleWorkflowContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.schema = (SKILL_DIR / "references" / "state-schema.md").read_text(
            encoding="utf-8"
        )
        cls.combined = cls.skill + cls.schema

    def test_workflow_runs_from_radar_to_initial_draft_only(self):
        for phrase in (
            "ni-radar weekly",
            "topic-selection.md",
            "article-outline.md",
            "research.md",
            "`ni-writer`",
            "article-draft.md",
            "draft_ready",
        ):
            self.assertIn(phrase, self.combined)
        for forbidden in (
            "inspect-report.md",
            "cover-prompt.md",
            "`ni-formatter`",
            "`ni-draft`",
        ):
            self.assertNotIn(forbidden, self.combined)

    def test_both_collaborative_and_autonomous_modes_are_explicit(self):
        for phrase in (
            "`collaborative`",
            "`autonomous`",
            "run_to_draft: true",
            "selection_origin: user",
            "selection_origin: workflow",
            "user_confirmed",
            "autonomous_ready",
            "agent_synthesis",
        ):
            self.assertIn(phrase, self.skill)

    def test_every_stage_has_an_acceptance_gate(self):
        for stage in ("radar", "selection", "source", "insight", "practice", "evidence", "draft"):
            self.assertIn(f"### `{stage}`", self.schema)
        for phrase in ("gate-report.md", "PASS | FAIL | WAITING | DEGRADED", "门禁未通过时不得进入下一阶段"):
            self.assertIn(phrase, self.combined)

    def test_source_and_evidence_boundaries_are_enforced(self):
        for phrase in (
            "精确归档目录",
            "原始 URL",
            "本地可读 Markdown",
            "A-official",
            "B-original",
            "未核实内容不会影响正文结论",
        ):
            self.assertIn(phrase, self.combined)

    def test_draft_authorization_is_mode_specific(self):
        for phrase in (
            "authorization_origin: user",
            "authorization_origin: workflow_config",
            "run_to_draft: true",
            "只授权生成本地初稿",
        ):
            self.assertIn(phrase, self.skill)

    def test_draft_gate_prevents_false_first_person_and_source_drift(self):
        for phrase in (
            "没有把 `agent_synthesis` 写成用户亲历",
            "未引入大纲与研究之外的新事实主张",
            "只允许把明确失败项交给 `ni-writer` 修复一次",
            "draft.attempts",
        ):
            self.assertIn(phrase, self.combined)

    def test_reruns_are_idempotent_and_upstream_changes_invalidate_downstream(self):
        for phrase in (
            "input_fingerprint",
            "output_sha256",
            "标记 `stale`",
            "不重复执行已通过阶段",
            "不静默覆盖",
        ):
            self.assertIn(phrase, self.combined)

    def test_schema_keeps_full_sources_outside_article_body(self):
        self.assertIn("正文只允许保留", self.schema)
        self.assertIn("其余链接留在研究文件", self.schema)


if __name__ == "__main__":
    unittest.main()
