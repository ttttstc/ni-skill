"""Offline contract tests for the ni-fde-copilot skill."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]
SKILL = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
WRITING = (SKILL_DIR / "references" / "writing-standard.md").read_text(encoding="utf-8")
COGNITIVE = (SKILL_DIR / "references" / "cognitive-gap-model.md").read_text(encoding="utf-8")
QUALITY = (SKILL_DIR / "references" / "quality-rubric.md").read_text(encoding="utf-8")


class FdeCopilotContractTests(unittest.TestCase):
    def test_frontmatter_is_minimal_and_complete(self) -> None:
        match = re.match(r"\A---\n(.*?)\n---\n", SKILL, re.DOTALL)
        self.assertIsNotNone(match)
        fields = [line.split(":", 1)[0] for line in match.group(1).splitlines()]
        self.assertEqual(fields, ["name", "description"])
        self.assertIn("name: ni-fde-copilot", match.group(0))
        self.assertNotIn("TODO", SKILL)

    def test_all_direct_references_exist(self) -> None:
        expected = {
            "domain-model.md",
            "cognitive-gap-model.md",
            "writing-standard.md",
            "quality-rubric.md",
        }
        for name in expected:
            self.assertIn(f"references/{name}", SKILL)
            self.assertTrue((SKILL_DIR / "references" / name).is_file())

    def test_default_gate_cannot_be_silently_skipped(self) -> None:
        self.assertIn("第一阶段只输出五部分学习蓝图", SKILL)
        self.assertIn("未确认前不得起草、预览或续写第二阶段正文", SKILL)
        self.assertIn("只有用户明确要求快速模式、一次性生成或跳过确认", SKILL)
        self.assertIn("不要附正文示例", WRITING)

    def test_blueprint_keeps_exact_five_part_contract(self) -> None:
        headings = re.findall(
            r"^## ([1-5]\. (?:主题识别|知识结构梳理|关键例子盘点|认知缺口预判|预期产出))$",
            WRITING,
            re.MULTILINE,
        )
        self.assertEqual(
            headings,
            [
                "1. 主题识别",
                "2. 知识结构梳理",
                "3. 关键例子盘点",
                "4. 认知缺口预判",
                "5. 预期产出",
            ],
        )

    def test_concept_and_case_coverage_is_explicit(self) -> None:
        for phrase in (
            "是什么",
            "为什么重要",
            "机制",
            "怎么判断",
            "怎么用",
            "常见错误",
            "容易混淆的概念",
            "边界",
            "所以呢",
            "每个承载推理的案例",
        ):
            self.assertIn(phrase, WRITING)
        self.assertIn("每个核心概念", QUALITY)
        self.assertIn("每个承载推理的案例", QUALITY)

    def test_gap_and_evidence_contract_is_complete(self) -> None:
        for status in ("SOURCE", "INFERENCE", "EXTERNAL", "UNKNOWN", "NEED VALIDATION"):
            self.assertIn(status, SKILL)
            self.assertIn(status, COGNITIVE)
        for gap in ("机制缺口", "区分缺口", "边界缺口", "视觉上下文缺口"):
            self.assertIn(gap, COGNITIVE)

    def test_oral_visual_and_style_rules_are_explicit(self) -> None:
        for phrase in (
            "大家看这个",
            "就是那种感觉",
            "你们懂的",
            "先试 A，因 X 失败，再转向 B",
            "U+2014",
            "U+2013",
            "使用「」",
        ):
            self.assertIn(phrase, WRITING)

    def test_transfer_and_conversation_readiness_are_required(self) -> None:
        self.assertIn("迁移挑战", SKILL)
        self.assertIn("对话准备度", SKILL)
        self.assertIn("原资料没有出现的新场景", QUALITY)
        self.assertIn("不要装懂", QUALITY)

    def test_chinese_skill_surface_does_not_use_english_workflow_terms(self) -> None:
        chinese_surface = "\n".join(
            [
                SKILL,
                (SKILL_DIR / "README.md").read_text(encoding="utf-8"),
                (SKILL_DIR / "references" / "domain-model.md").read_text(encoding="utf-8"),
                COGNITIVE,
                WRITING,
                QUALITY,
            ]
        )
        for phrase in (
            "Learning Blueprint",
            "Guided Learning Guide",
            "Learning Mission",
            "Cognitive Gap",
            "Learning Spine",
            "Conversation Readiness",
            "Source Inventory",
            "Root Problem",
            "Core Concept",
            "Reasoning-bearing Case",
            "Don't Bluff",
        ):
            self.assertNotIn(phrase, chinese_surface)

    def test_three_eval_source_types_exist(self) -> None:
        evals = sorted((SKILL_DIR / "evals").glob("*.md"))
        self.assertEqual(
            [item.name for item in evals],
            ["expert-transcript.md", "industry-source.md", "technical-source.md"],
        )
        for item in evals:
            self.assertIn("# Source", item.read_text(encoding="utf-8"))

    def test_skill_is_registered_and_documented(self) -> None:
        marketplace = json.loads(
            (REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
        )
        codex = json.loads(
            (REPO_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual("1.2.0", codex["version"])
        self.assertEqual(codex["version"], marketplace["metadata"]["version"])
        skills = marketplace["plugins"][0]["skills"]
        self.assertIn("./skills/ni-fde-copilot", skills)
        for readme in ("README.md", "README.en.md"):
            text = (REPO_ROOT / readme).read_text(encoding="utf-8")
            self.assertGreaterEqual(text.count("ni-fde-copilot"), 2)


if __name__ == "__main__":
    unittest.main()
