import json
import re
import unittest
from pathlib import Path


SKILL_NAME = "ni-design-with-docs"
OLD_SKILL_NAME = "ni-product-architect"
SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[1]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class SkillContractTests(unittest.TestCase):
    def test_folder_and_frontmatter_name_match(self) -> None:
        skill_text = read_text(SKILL_ROOT / "SKILL.md")
        frontmatter = re.match(r"\A---\s*\n(.*?)\n---", skill_text, re.DOTALL)

        self.assertIsNotNone(frontmatter, "SKILL.md must start with YAML frontmatter")
        name = re.search(r"^name:\s*(\S+)\s*$", frontmatter.group(1), re.MULTILINE)
        self.assertIsNotNone(name, "SKILL.md frontmatter must contain name")
        self.assertEqual(SKILL_NAME, SKILL_ROOT.name)
        self.assertEqual(SKILL_NAME, name.group(1))

    def test_referenced_resources_exist(self) -> None:
        expected = [
            "agents/openai.yaml",
            "agents/researcher.md",
            "agents/reviewer.md",
            "agents/security-reviewer.md",
            "eval/gates.md",
            "eval/scenarios.md",
            "references/01-workflow.md",
            "references/02-concepts-and-interview.md",
            "references/03-current-state-and-research.md",
            "references/04-architecture-design.md",
            "references/05-views-interfaces-constraints.md",
            "references/06-testing-and-output.md",
            "references/07-writing-style.md",
            "references/08-security-review.md",
            "templates/architecture-baseline.md",
            "README.md",
            "README.en.md",
        ]

        missing = [relative for relative in expected if not (SKILL_ROOT / relative).is_file()]
        self.assertEqual([], missing, f"Missing skill resources: {missing}")

    def test_openai_metadata_contract(self) -> None:
        metadata = read_text(SKILL_ROOT / "agents" / "openai.yaml")
        short_description = re.search(
            r'^\s*short_description:\s*"([^"]+)"\s*$',
            metadata,
            re.MULTILINE,
        )
        default_prompt = re.search(
            r'^\s*default_prompt:\s*"([^"]+)"\s*$',
            metadata,
            re.MULTILINE,
        )

        self.assertIsNotNone(short_description)
        self.assertGreaterEqual(len(short_description.group(1)), 25)
        self.assertLessEqual(len(short_description.group(1)), 64)
        self.assertIsNotNone(default_prompt)
        self.assertIn("$" + SKILL_NAME, default_prompt.group(1))

    def test_workflow_has_real_user_alignment_gate(self) -> None:
        skill = read_text(SKILL_ROOT / "SKILL.md")
        workflow = read_text(SKILL_ROOT / "references" / "01-workflow.md")
        interview = read_text(SKILL_ROOT / "references" / "02-concepts-and-interview.md")
        combined = "\n".join([skill, workflow, interview])

        self.assertIn("第一次有效响应不得直接输出架构", skill)
        self.assertIn("随后暂停，等待用户明确确认或修改", skill)
        self.assertIn("本轮全部按推荐", combined)
        self.assertIn("不等于自动授权开始设计", skill)
        self.assertIn("用户确认前仍不得进入设计", skill)
        self.assertIn("推荐项快速路径", combined)
        self.assertIn("后续全部按推荐", combined)
        self.assertIn("对齐摘要", combined)

    def test_workbench_is_separated_from_formal_report(self) -> None:
        skill = read_text(SKILL_ROOT / "SKILL.md")
        template = read_text(SKILL_ROOT / "templates" / "architecture-baseline.md")

        self.assertIn("工作底稿与正式报告分离", skill)
        self.assertIn("这次不做什么", template)
        forbidden_sections = [
            "## 调研过程",
            "## 访谈记录",
            "## 核心概念与设计语言",
            "## 业界参考与设计依据",
            "## 独立评审记录",
        ]
        for heading in forbidden_sections:
            self.assertNotIn(heading, template)

        leaked_policy_phrases = [
            "数据库表",
            "内部 DTO",
            "缓存键",
            "线程模型",
            "具体消息队列",
        ]
        for phrase in leaked_policy_phrases:
            self.assertNotIn(phrase, template)

        self.assertIn("使用 2–3 个短句", template)
        self.assertIn("第一句说最终要做到什么", template)

    def test_views_are_conditional_and_user_interaction_is_prioritized(self) -> None:
        skill = read_text(SKILL_ROOT / "SKILL.md")
        views = read_text(
            SKILL_ROOT / "references" / "05-views-interfaces-constraints.md"
        )
        template = read_text(SKILL_ROOT / "templates" / "architecture-baseline.md")

        self.assertIn("用户交互涉及多角色、多状态或分支时", skill)
        self.assertIn("不要用 L1 架构图替代用户交互", views)
        self.assertIn("不是必填项", skill)
        self.assertIn("UML 时序图", skill)
        self.assertIn("UML 状态图", template)
        self.assertIn("数据流图", views)
        self.assertIn("模块架构关系图", template)
        self.assertIn("核心内容的图形组合", views)
        self.assertIsNone(re.search(r"^#{2,4}\s+.*L0", template, re.MULTILINE))
        self.assertIsNone(re.search(r"^#{2,4}\s+.*L1", template, re.MULTILINE))

    def test_product_specification_is_explicit(self) -> None:
        skill = read_text(SKILL_ROOT / "SKILL.md")
        architecture = read_text(
            SKILL_ROOT / "references" / "04-architecture-design.md"
        )
        gates = read_text(SKILL_ROOT / "eval" / "gates.md")
        template = read_text(SKILL_ROOT / "templates" / "architecture-baseline.md")

        self.assertIn("可直接定位的产品规格", skill)
        self.assertIn("产品规格先闭合", architecture)
        self.assertIn("## 3. 产品规格", template)
        self.assertIn("产品对象和使用入口", template)
        self.assertIn("产品场景 | 系统必须做什么 | 用户或调用方看到什么", template)
        self.assertIn("有可直接定位的产品规格", gates)

    def test_security_has_dedicated_reference_reviewer_and_gate(self) -> None:
        security = read_text(SKILL_ROOT / "references" / "08-security-review.md")
        reviewer = read_text(SKILL_ROOT / "agents" / "security-reviewer.md")
        gates = read_text(SKILL_ROOT / "eval" / "gates.md")

        self.assertIn("安全适用性", security)
        self.assertIn("硬阻断条件", security)
        self.assertIn("独立安全评审", reviewer)
        self.assertIn("## G5 安全与信任边界", gates)
        self.assertIn("高残余风险", security)
        self.assertIn("安全影响不显著", reviewer)
        self.assertIn("安全问题 | 可能造成什么后果 | 解决办法 | 怎么验证", security)

    def test_report_tables_are_lean_and_plain(self) -> None:
        template = read_text(SKILL_ROOT / "templates" / "architecture-baseline.md")
        architecture = read_text(
            SKILL_ROOT / "references" / "04-architecture-design.md"
        )
        contracts = read_text(
            SKILL_ROOT / "references" / "05-views-interfaces-constraints.md"
        )

        for text in [template, architecture]:
            self.assertNotIn("接受的代价", text)
            self.assertNotIn("复审条件", text)

        collaboration_header = "| 必须共同遵守的规则 | 涉及对象 | 不满足时的系统结果 |"
        self.assertIn(collaboration_header, template)
        self.assertIn(collaboration_header, contracts)
        self.assertNotIn("| 兼容要求 |", contracts)

        for heading in [
            "## 3. 产品规格",
            "## 4. 用户怎么使用",
            "## 5. 系统边界与影响范围",
            "## 6. 总体设计",
            "## 7. 系统必须达到的质量要求",
            "## 8. 安全问题和解决办法",
            "## 9. 出错怎么办",
            "## 10. 如何上线和回退",
            "## 11. 如何验收",
        ]:
            self.assertIn(heading, template)

    def test_system_boundary_is_interview_derived_in_v1(self) -> None:
        skill = read_text(SKILL_ROOT / "SKILL.md")
        boundary = read_text(
            SKILL_ROOT / "references" / "03-current-state-and-research.md"
        )
        template = read_text(SKILL_ROOT / "templates" / "architecture-baseline.md")

        self.assertIn("已确认的系统边界与影响范围", skill)
        self.assertIn("V1 不扫描代码、仓库、配置或内部接口", boundary)
        self.assertIn("用户不需要自己画架构图", boundary)
        self.assertIn("根据已经确认的访谈输入，由设计者归纳", template)
        self.assertNotIn("架构驱动因素", template)

    def test_quality_requirements_are_scenario_based_and_verifiable(self) -> None:
        template = read_text(SKILL_ROOT / "templates" / "architecture-baseline.md")
        quality = read_text(
            SKILL_ROOT / "references" / "06-testing-and-output.md"
        )
        gates = read_text(SKILL_ROOT / "eval" / "gates.md")

        scenario_header = "| 发生什么 | 系统必须怎样响应 | 怎样判断通过 |"
        self.assertIn(scenario_header, template)
        self.assertIn(scenario_header, quality)
        self.assertIn("ISO/IEC 25010:2023", quality)
        self.assertIn("SEI Quality Attribute Scenarios", quality)
        self.assertIn("没有编造性能、容量、可用率或恢复时间", gates)
        self.assertIn("不会改变的数值留给详细设计或容量测试", gates)

    def test_gate_contract_is_g0_through_g9(self) -> None:
        gates = read_text(SKILL_ROOT / "eval" / "gates.md")
        gate_ids = re.findall(r"^## (G\d+)\b", gates, re.MULTILINE)
        self.assertEqual([f"G{i}" for i in range(10)], gate_ids)
        self.assertIn("架构评审负责 G0–G4、G6–G9", gates)
        self.assertIn("独立安全评审负责 G5", gates)

    def test_runtime_quality_and_rollback_guards_are_explicit(self) -> None:
        template = read_text(SKILL_ROOT / "templates" / "architecture-baseline.md")
        views = read_text(
            SKILL_ROOT / "references" / "05-views-interfaces-constraints.md"
        )
        rollout = read_text(
            SKILL_ROOT / "references" / "06-testing-and-output.md"
        )
        gates = read_text(SKILL_ROOT / "eval" / "gates.md")

        self.assertIn("处理中、成功、失败、超时和取消", template)
        self.assertIn("系统边界与影响范围", template)
        self.assertIn("存在并发、重复、乱序或异步结果合并时", views)
        self.assertIn("超时、取消或部分失败后如何停止、恢复或继续", views)
        self.assertIn("发生什么、系统必须怎样响应和怎样判断通过", gates)
        self.assertIn("谁负责判断、批准和执行", rollout)

    def test_product_goal_cannot_be_document_process_goal(self) -> None:
        template = read_text(SKILL_ROOT / "templates" / "architecture-baseline.md")
        architecture = read_text(
            SKILL_ROOT / "references" / "04-architecture-design.md"
        )
        style = read_text(SKILL_ROOT / "references" / "07-writing-style.md")
        gates = read_text(SKILL_ROOT / "eval" / "gates.md")

        self.assertIn("不要把“帮助研发、统一认知、建设能力", template)
        self.assertIn("不把写文档、帮助研发、统一认知或建设能力当目标", architecture)
        self.assertIn("这些是文档用途，不是产品目标", style)
        self.assertIn("没有把文档用途或研发过程当成产品目标", gates)

    def test_design_review_does_not_require_implementation_evidence(self) -> None:
        reviewer = read_text(SKILL_ROOT / "agents" / "reviewer.md")
        security_reviewer = read_text(
            SKILL_ROOT / "agents" / "security-reviewer.md"
        )
        security = read_text(SKILL_ROOT / "references" / "08-security-review.md")
        gates = read_text(SKILL_ROOT / "eval" / "gates.md")

        self.assertIn("不得要求提供尚未开发的代码、测试结果或生产证据", reviewer)
        self.assertIn("不需要提前提供实现证据", security_reviewer)
        self.assertIn("设计评审通过不等于实现已经通过安全验收", security)
        self.assertIn("不要求提前提供实现证据", gates)

    def test_security_review_covers_outputs_and_incident_stop_loss(self) -> None:
        security = read_text(SKILL_ROOT / "references" / "08-security-review.md")
        reviewer = read_text(SKILL_ROOT / "agents" / "security-reviewer.md")
        gates = read_text(SKILL_ROOT / "eval" / "gates.md")

        self.assertIn("面向用户或其他系统的详情、错误、日志和导出", security)
        self.assertIn("遵守请求者权限", reviewer)
        self.assertIn("处理进行中操作、秘密或凭证", gates)
        self.assertIn("停止继续扩大风险", gates)

    def test_behavior_scenarios_cover_fast_paths_and_security(self) -> None:
        scenarios = read_text(SKILL_ROOT / "eval" / "scenarios.md")
        headings = re.findall(r"^## 场景 \d+：", scenarios, re.MULTILINE)
        self.assertGreaterEqual(len(headings), 7)
        for behavior in [
            "全新复杂需求必须先访谈",
            "后续决策全部采用推荐项",
            "全部选择推荐项",
            "交互复杂但系统改动简单",
            "高安全风险必须阻断",
            "安全影响不显著",
            "workflow_call 十层完整报告",
            "质量要求不能写成口号",
        ]:
            self.assertIn(behavior, scenarios)

    def test_host_registration_and_catalogs_use_new_name(self) -> None:
        codex_manifest = json.loads(read_text(REPO_ROOT / ".codex-plugin" / "plugin.json"))
        claude_manifest = json.loads(
            read_text(REPO_ROOT / ".claude-plugin" / "marketplace.json")
        )
        claude_skills = claude_manifest["plugins"][0]["skills"]
        root_readmes = [
            read_text(REPO_ROOT / "README.md"),
            read_text(REPO_ROOT / "README.en.md"),
        ]

        self.assertTrue(
            any(SKILL_NAME in prompt for prompt in codex_manifest["interface"]["defaultPrompt"])
        )
        self.assertIn(f"./skills/{SKILL_NAME}", claude_skills)
        for readme in root_readmes:
            self.assertIn(SKILL_NAME, readme)
            self.assertNotIn(OLD_SKILL_NAME, readme)

    def test_bilingual_readmes_share_commands_and_reciprocal_links(self) -> None:
        readme_zh = read_text(SKILL_ROOT / "README.md")
        readme_en = read_text(SKILL_ROOT / "README.en.md")
        invariant_lines = [
            "$" + SKILL_NAME + " 我需要为平台支持某项新能力。目标是……；已知业务和平台约束如下……",
            f"/{SKILL_NAME} 我需要为平台支持某项新能力。目标是……；已知业务和平台约束如下……",
            f"python -m unittest skills/{SKILL_NAME}/tests/test_skill_contract.py",
            "python skills/ni-readme-guide/scripts/audit_readme.py "
            f"skills/{SKILL_NAME}",
        ]

        self.assertIn("中文 | [English](./README.en.md)", readme_zh)
        self.assertIn("[中文](./README.md) | English", readme_en)
        for line in invariant_lines:
            self.assertIn(line, readme_zh)
            self.assertIn(line, readme_en)

    def test_repository_has_no_stale_old_identifier(self) -> None:
        stale = []
        for path in REPO_ROOT.rglob("*"):
            if not path.is_file() or ".git" in path.parts:
                continue
            if path.suffix.lower() not in {".md", ".yaml", ".json"}:
                continue
            if OLD_SKILL_NAME in read_text(path):
                stale.append(str(path.relative_to(REPO_ROOT)))

        self.assertEqual([], stale, f"Stale identifier found in: {stale}")


if __name__ == "__main__":
    unittest.main()
