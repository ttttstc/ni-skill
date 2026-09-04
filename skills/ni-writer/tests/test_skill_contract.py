from pathlib import Path
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[1]


class NiWriterContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.tech_rules = (
            SKILL_DIR / "references" / "tech_writing_rules.md"
        ).read_text(encoding="utf-8")
        cls.examples = (
            SKILL_DIR / "references" / "style_examples.md"
        ).read_text(encoding="utf-8")
        cls.readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    def test_technical_routes_are_merged_without_dropping_other_archetypes(self):
        self.assertIn("## 文章原型(5 种)", self.skill)
        self.assertIn("技术方法论型(沉淀 + 深水区合并)", self.skill)
        self.assertIn("技术思辨型", self.skill)
        self.assertIn("人生哲学随笔型", self.skill)
        self.assertIn("发现分享型(速读精华式)", self.skill)
        self.assertIn("产品体验和评价型", self.skill)

    def test_scene_rules_make_technical_prose_more_vivid(self):
        # SKILL.md 只做分流:场景规则下沉到 tech_writing_rules.md,主文件保留路由指针
        self.assertIn("references/tech_writing_rules.md", self.skill)
        self.assertNotIn("## 子风格分化", self.skill)

        for phrase in (
            "可见现场 → 动作或产物 → 阻力或转折 → 机制解释 → 取舍或下一步",
            "一条主场景贯穿",
            "场景卡五项",
            "主场景至少写出三项",
            "对话只写决策线",
            "读者能否在脑中截出一帧画面",
        ):
            self.assertIn(phrase, self.tech_rules)

        # 反 AI 鸡汤与功能列表化终检项同样下沉到两条技术路由的终检清单
        polemic_rules = (
            SKILL_DIR / "references" / "tech_polemic_rules.md"
        ).read_text(encoding="utf-8")
        for phrase in ("功能列表化", "营销话术"):
            self.assertIn(phrase, self.tech_rules)
            self.assertIn(phrase, polemic_rules)

    def test_current_anti_ai_rules_and_output_tail_are_explicit(self):
        self.assertIn("human-writing 增量终审", self.skill)
        self.assertIn("副词先删后判", self.skill)
        self.assertIn("默认不自动添加公众号推广尾部或署名", self.skill)
        self.assertNotIn("## 固定尾部", self.skill)

    def test_historical_examples_are_not_current_routing_rules(self):
        self.assertIn("示例库保留历史语料", self.examples)
        self.assertIn("不用于复制固定句式或判定现行路由", self.examples)

    def test_readme_documents_the_scene_contract(self):
        self.assertIn("5 种文章原型", self.readme)
        self.assertIn("一条主场景承载判断", self.readme)


if __name__ == "__main__":
    unittest.main()
