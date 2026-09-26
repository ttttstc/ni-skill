"""Static integration checks for the published skill and workflow contracts.

These checks verify routing and document consistency, not live agent behavior.
"""
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
SKILLS = ROOT / "skills"


def read(path):
    return path.read_text(encoding="utf-8")


class PipelineContractTest(unittest.TestCase):
    def test_public_registry_routes_to_research_not_retired_insight(self):
        registry = json.loads(read(ROOT / ".claude-plugin/marketplace.json"))
        paths = registry["plugins"][0]["skills"]
        self.assertIn("./skills/ni-research", paths)
        self.assertNotIn("./skills/ni-insight", paths)
        self.assertTrue((SKILLS / "ni-research/SKILL.md").is_file())
        self.assertFalse((SKILLS / "ni-insight/SKILL.md").exists())
        for filename in ("README.md", "README.en.md"):
            for target in re.findall(r"\]\((\./skills/[^)#]+)\)", read(ROOT / filename)):
                self.assertTrue((ROOT / target).exists(), target)

    def test_all_research_reference_routes_resolve(self):
        skill = read(SKILLS / "ni-research/SKILL.md")
        refs = re.findall(r"`(references/[^`]+\.md)`", skill)
        self.assertGreaterEqual(len(set(refs)), 5)
        for ref in refs:
            self.assertTrue((SKILLS / "ni-research" / ref).is_file(), ref)

    def test_workflow_and_state_agree_on_stage_order(self):
        workflow = read(SKILLS / "ni-article-workflow/SKILL.md")
        schema = read(SKILLS / "ni-article-workflow/references/state-schema.md")
        expected = ["radar", "selection", "source", "research", "outline", "practice", "draft"]
        self.assertEqual(re.findall(r"^### \d+\. `([^`]+)`", workflow, re.M), expected)
        stage_block = schema.split("\nstages:\n", 1)[1].split("\nuser_decisions:", 1)[0]
        self.assertEqual(re.findall(r"^  (\w+):$", stage_block, re.M), expected)
        self.assertNotIn("调用 `ni-insight`", workflow)
        self.assertNotIn("调用 `ni-radar evidence`", workflow)

    def test_unconfirmed_and_changed_research_cannot_authorize_outline(self):
        contract = read(SKILLS / "ni-research/references/research-contract.md")
        outline = read(SKILLS / "ni-research/references/outline-contract.md")
        writer = read(SKILLS / "ni-writer/SKILL.md")
        self.assertIn("不代表用户认可，也不授权策划或写作", contract)
        self.assertIn("清空确认", contract)
        self.assertIn("confirmed_revision", outline)
        self.assertIn("旧大纲状态退回 draft", outline)
        self.assertIn("版本不一致", writer)
        self.assertIn("用户明确写正文的授权", writer)

    def test_old_passes_are_not_reused_as_new_research_confirmation(self):
        schema = read(SKILLS / "ni-article-workflow/references/state-schema.md")
        migration = schema.split("## 旧状态迁移", 1)[1]
        self.assertIn("PASS 不能直接换名沿用", migration)
        self.assertIn("practice / draft 标为 stale", migration)
        self.assertIn("不得凭旧 outline.user_confirmed", migration)


if __name__ == "__main__":
    unittest.main()
