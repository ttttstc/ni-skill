import json
import re
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = SKILL_DIR.parents[1]


class SkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.intake = (SKILL_DIR / "references" / "intake-and-image-review.md").read_text(
            encoding="utf-8"
        )
        cls.qa = (SKILL_DIR / "references" / "glb-production-and-qa.md").read_text(
            encoding="utf-8"
        )

    def test_frontmatter_and_name(self):
        match = re.match(r"^---\n(.*?)\n---\n", self.skill, re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter = match.group(1)
        self.assertIn("name: ni-3d-model", frontmatter)
        self.assertIn("description:", frontmatter)

    def test_hard_gates_precede_generation(self):
        requirements_gate = self.skill.index("确认前我不会生成图片")
        image_gate = self.skill.index("图片通过前我不会生成 GLB")
        submission = self.skill.index("点击提交前")
        self.assertLess(requirements_gate, image_gate)
        self.assertLess(image_gate, submission)

    def test_provider_protocol_and_generator_precedence(self):
        self.assertIn("用户明确指定图像生成器时，优先使用该工具", self.skill)
        self.assertNotIn("gpt-image-2` thinking", self.skill)
        self.assertIn("front/left/right/back", self.skill)
        self.assertIn("不要用左前 45° 或右后 45° 替代左右侧图", self.intake)

    def test_attempt_budget_and_atomic_reset(self):
        for field in ("image_attempt_budget", "image_attempts_used"):
            self.assertIn(field, self.skill)
        self.assertIn("需求改变：递增", self.skill)
        self.assertIn("生成新图：递增", self.skill)

    def test_recoverable_submission_and_versioned_sources(self):
        for field in (
            "generation_version",
            "provider",
            "submission_status",
            "job_id",
            "credits_before",
            "submitted_at",
        ):
            self.assertIn(field, self.skill)
            self.assertIn(field, self.qa)
        self.assertIn("models/sources/generation-{generation_version}-source.glb", self.qa)
        self.assertNotIn("models/source.glb", self.skill + self.qa)

    def test_plugin_registration_and_version(self):
        codex = json.loads((REPO_DIR / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        claude = json.loads(
            (REPO_DIR / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
        )
        self.assertEqual("1.2.0", codex["version"])
        self.assertEqual("1.2.0", claude["metadata"]["version"])
        self.assertIn("./skills/ni-3d-model", claude["plugins"][0]["skills"])


if __name__ == "__main__":
    unittest.main()
