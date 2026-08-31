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

    def test_product_plan_and_system_specification_are_layered(self) -> None:
        skill = read_text(SKILL_ROOT / "SKILL.md")
        architecture = read_text(
            SKILL_ROOT / "references" / "04-architecture-design.md"
        )
        gates = read_text(SKILL_ROOT / "eval" / "gates.md")
        template = read_text(SKILL_ROOT / "templates" / "architecture-baseline.md")

        self.assertIn("先写完整的产品方案", skill)
        self.assertIn("系统规格写系统必须遵守的规则", skill)
        self.assertIn("先闭合产品方案，再设计系统", architecture)
        self.assertIn("## 3. 总体设计", template)
        ordered_sections = [
            "### 3.1 总体设计结论",
            "### 3.2 产品方案",
            "### 3.3 系统边界、影响范围与责任",
            "### 3.4 主要流程、数据与状态",
            "### 3.5 系统规格",
            "### 3.6 关键决定与协作约束",
        ]
        indexes = [template.index(heading) for heading in ordered_sections]
        self.assertEqual(sorted(indexes), indexes)
        for product_content in [
            "面向谁和解决什么",
            "从哪里进入，怎样完成任务",
            "用户会看到什么结果",
            "支持什么，不支持什么",
        ]:
            self.assertIn(product_content, template)
        for spec_content in [
            "核心规则",
            "权限和数据规则",
            "状态和结果规则",
            "失败时必须遵守的规则",
            "硬限制",
        ]:
            self.assertIn(spec_content, template)
        self.assertNotIn("产品场景 1", template)
        self.assertIn("有可直接定位的产品方案", gates)
        self.assertIn("有独立可定位的系统规格", gates)

    def test_current_target_delta_is_conditional(self) -> None:
        skill = read_text(SKILL_ROOT / "SKILL.md")
        template = read_text(SKILL_ROOT / "templates" / "architecture-baseline.md")
        architecture = read_text(
            SKILL_ROOT / "references" / "04-architecture-design.md"
        )
        gates = read_text(SKILL_ROOT / "eval" / "gates.md")
        scenarios = read_text(SKILL_ROOT / "eval" / "scenarios.md")

        for text in [skill, template, architecture, gates]:
            self.assertIn("当前", text)
            self.assertIn("目标", text)
        self.assertIn("当前与目标差异（仅增量需求）", template)
        self.assertIn("不生成空差异小节", skill)
        self.assertIn("全新能力或没有有意义现状时", architecture)
        self.assertIn("已有平台能力增量修改", scenarios)
        self.assertIn("全新能力不机械生成差异", scenarios)
        self.assertIn("不生成空的“当前与目标差异”小节", scenarios)

    def test_system_specification_is_the_only_behavior_source(self) -> None:
        skill = read_text(SKILL_ROOT / "SKILL.md")
        template = read_text(SKILL_ROOT / "templates" / "architecture-baseline.md")
        architecture = read_text(
            SKILL_ROOT / "references" / "04-architecture-design.md"
        )
        views = read_text(
            SKILL_ROOT / "references" / "05-views-interfaces-constraints.md"
        )
        gates = read_text(SKILL_ROOT / "eval" / "gates.md")

        for text in [skill, template, architecture, gates]:
            self.assertIn("唯一", text)
            self.assertIn("行为", text)
        self.assertIn("不新增独立 Story、行为规格或 Gherkin 章节", skill)
        self.assertIn("Given / When / Then 是可选表达工具", views)
        self.assertIn("不描述内部模块调用", skill)
        for forbidden_heading in ["### Story", "### 行为规格", "### Behavior Spec"]:
            self.assertNotIn(forbidden_heading, template)

    def test_acceptance_uses_deterministic_main_scenarios(self) -> None:
        skill = read_text(SKILL_ROOT / "SKILL.md")
        template = read_text(SKILL_ROOT / "templates" / "architecture-baseline.md")
        output = read_text(
            SKILL_ROOT / "references" / "06-testing-and-output.md"
        )
        gates = read_text(SKILL_ROOT / "eval" / "gates.md")
        reviewer = read_text(SKILL_ROOT / "agents" / "reviewer.md")

        for label in ["覆盖要求", "前置条件", "操作", "通过条件"]:
            self.assertIn(label, template)
            self.assertIn(label, output)
            self.assertIn(label, gates)
            self.assertIn(label, reviewer)
        for signal in ["状态", "数量", "阈值", "一致性"]:
            self.assertIn(signal, skill)
            self.assertIn(signal, output)
            self.assertIn(signal, gates)
        self.assertIn("设计级主场景", output)
        self.assertIn("不是详细测试设计", output)
        self.assertIn("不得为了形式完整生成来源不明的 P95", output)
        self.assertIn("没有为了形式完整编造性能", gates)
        self.assertIn("兼容与回归要求", gates)
        self.assertIn("等价类", output)
        self.assertIn("自动化实现", gates)
        self.assertIn("唯一行为真源", reviewer)
        self.assertIn("没有展开详细测试或编造数值", reviewer)

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
        self.assertIn("**问题和后果**", security)
        self.assertIn("**系统怎么处理**", security)
        self.assertIn("**验收标准**", security)

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

        self.assertIn("约束 1", template)
        self.assertIn("### 约束 1", contracts)
        self.assertNotIn("| 兼容要求 |", contracts)

        table_separator = re.compile(r"^\|(?:\s*:?-+:?\s*\|){2,}\s*$", re.MULTILINE)
        report_tables = table_separator.findall(template)
        self.assertLessEqual(
            len(report_tables),
            3,
            "Formal report template should not encourage table fatigue",
        )
        self.assertIn("发生什么", template)
        self.assertIn("系统怎么处理", template)
        self.assertNotIn("**适配策略**", template)
        for wide_table_header in [
            "| 产品场景 |",
            "| 发生什么 | 系统必须怎样响应 | 怎样判断通过 |",
            "| 安全问题 | 可能造成什么后果 | 解决办法 | 怎么验证 |",
            "| 失败情况 | 用户或调用方看到什么 | 系统怎么处理 | 如何恢复 |",
            "| 场景 | 前提和操作 | 预期结果 |",
            "| 事项 | 对开发或上线的影响 | 下一步 |",
        ]:
            self.assertNotIn(wide_table_header, template)

        top_level_headings = re.findall(r"^## (\d+\..+)$", template, re.MULTILINE)
        self.assertEqual(
            [
                "1. 方案摘要",
                "2. 目标和范围",
                "3. 总体设计",
                "4. 质量、安全和异常处理",
                "5. 上线与验收",
                "6. 风险与参考来源",
            ],
            top_level_headings,
        )
        ordered_subsections = [
            "### 4.1 关键质量要求",
            "### 4.2 安全问题和解决办法",
            "### 4.3 关键失败与恢复",
            "### 5.1 如何上线和回退",
            "### 5.2 如何验收",
            "### 6.1 风险、待确认和后续详细设计",
            "### 6.2 参考来源",
        ]
        indexes = [template.index(heading) for heading in ordered_subsections]
        self.assertEqual(sorted(indexes), indexes)

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

    def test_quality_requirements_are_plain_and_verifiable(self) -> None:
        template = read_text(SKILL_ROOT / "templates" / "architecture-baseline.md")
        quality = read_text(
            SKILL_ROOT / "references" / "06-testing-and-output.md"
        )
        gates = read_text(SKILL_ROOT / "eval" / "gates.md")

        self.assertIn("**发生什么**", template)
        self.assertIn("**系统怎么处理**", template)
        self.assertIn("**怎样判断通过**", template)
        self.assertIn("### 下游在处理期间不可用", quality)
        self.assertIn("**系统怎么处理**", quality)
        self.assertIn("**怎样判断通过**", quality)
        self.assertNotIn("**适配策略**", quality)
        self.assertIn("ISO/IEC 25010:2023", quality)
        self.assertIn("SEI Quality Attribute Scenarios", quality)
        self.assertIn("没有编造性能、容量、可用率或恢复时间", gates)
        self.assertIn("不会改变的数值留给详细设计或容量测试", gates)

    def test_report_is_conclusion_first_without_duplicate_ownership(self) -> None:
        skill = read_text(SKILL_ROOT / "SKILL.md")
        template = read_text(SKILL_ROOT / "templates" / "architecture-baseline.md")
        style = read_text(SKILL_ROOT / "references" / "07-writing-style.md")
        gates = read_text(SKILL_ROOT / "eval" / "gates.md")

        self.assertIn("每章、每节都按金字塔原理写", skill)
        self.assertIn("用金字塔原理组织内容", style)
        self.assertIn("每节先写一句结论", template)
        self.assertIn("同一个问题只放在一个主要位置", template)
        self.assertIn("验收只验证前文结论", template)
        for repeated_heading in ["产品场景 1", "质量场景 1", "失败场景 1"]:
            self.assertNotIn(repeated_heading, template)
        self.assertIn("正文是权威结论", template)
        self.assertIn("图只帮助理解", template)
        self.assertIn("同一个问题只有一个主要归属", gates)

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

        self.assertIn("处理中、成功、失败、等待、超时和取消", template)
        self.assertIn("系统边界、影响范围与责任", template)
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

    def test_transfer_contract_is_explicit_and_conditional(self) -> None:
        skill = read_text(SKILL_ROOT / "SKILL.md")
        interview = read_text(
            SKILL_ROOT / "references" / "02-concepts-and-interview.md"
        )
        architecture = read_text(
            SKILL_ROOT / "references" / "04-architecture-design.md"
        )
        views = read_text(
            SKILL_ROOT / "references" / "05-views-interfaces-constraints.md"
        )
        template = read_text(SKILL_ROOT / "templates" / "architecture-baseline.md")
        gates = read_text(SKILL_ROOT / "eval" / "gates.md")
        security = read_text(SKILL_ROOT / "agents" / "security-reviewer.md")

        for text in [skill, interview, architecture, views, template, gates]:
            self.assertIn("传递", text)
        for phrase in [
            "关键传递项清单",
            "输入、上下文、凭证、Secret 和结果传递",
            "来源和接收方",
            "继承或覆盖",
            "缺失或非法",
            "可观察结果",
            "传递契约",
            "作用域",
        ]:
            combined = "\n".join(
                [skill, interview, architecture, views, template, gates, security]
            )
            self.assertIn(phrase, combined)
        self.assertIn("不适用", interview)
        self.assertIn("未知项回到 P1/P2", interview)
        self.assertIn("Secret", security)

    def test_formal_report_has_content_firewall(self) -> None:
        skill = read_text(SKILL_ROOT / "SKILL.md")
        template = read_text(SKILL_ROOT / "templates" / "architecture-baseline.md")
        style = read_text(SKILL_ROOT / "references" / "07-writing-style.md")
        gates = read_text(SKILL_ROOT / "eval" / "gates.md")
        combined = "\n".join([skill, template, style, gates])

        for phrase in [
            "作者推导",
            "报告策略",
            "面向读者",
            "背景可以保留",
            "当前事实、直接影响和本次变化",
            "正式报告只呈现方案事实和客观设计结论",
            "一个句子只表达一个主要判断",
        ]:
            self.assertIn(phrase, combined)
        for heading in ["## 访谈记录", "## 调研过程", "## 独立评审记录"]:
            self.assertNotIn(heading, template)

    def test_eval_covers_transfer_and_report_boundary(self) -> None:
        scenarios = read_text(SKILL_ROOT / "eval" / "scenarios.md")
        self.assertIn("场景 12：跨边界传递契约不能遗漏", scenarios)
        for phrase in [
            "输入",
            "上下文",
            "Token",
            "Secret",
            "成功",
            "未授权",
            "不泄露",
            "报告策略",
        ]:
            self.assertIn(phrase, scenarios)

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

    def test_failed_reviews_require_user_scope_confirmation(self) -> None:
        skill = read_text(SKILL_ROOT / "SKILL.md")
        workflow = read_text(SKILL_ROOT / "references" / "01-workflow.md")
        reviewer = read_text(SKILL_ROOT / "agents" / "reviewer.md")
        security_reviewer = read_text(
            SKILL_ROOT / "agents" / "security-reviewer.md"
        )
        gates = read_text(SKILL_ROOT / "eval" / "gates.md")

        for text in [skill, workflow, reviewer, security_reviewer, gates]:
            self.assertIn("主要问题", text)
            self.assertIn("最小修复", text)
            self.assertIn("不修复后果", text)
            self.assertIn("推荐选择", text)
        self.assertIn("用户确认修复项或修改范围后", skill)
        self.assertIn("用户确认前不改稿", workflow)
        self.assertIn("不为完整而完整", gates)
        self.assertIn("场景 10：独立评审不通过时先确认修复范围", read_text(
            SKILL_ROOT / "eval" / "scenarios.md"
        ))

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
            "已有平台能力增量修改",
            "质量指标未知时不编造阈值",
            "结论先行且不重复",
            "独立评审不通过时先确认修复范围",
            "全新能力不机械生成差异",
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
