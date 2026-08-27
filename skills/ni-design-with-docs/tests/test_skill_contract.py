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
            "eval/gates.md",
            "references/01-workflow.md",
            "references/02-concepts-and-interview.md",
            "references/03-current-state-and-research.md",
            "references/04-architecture-design.md",
            "references/05-views-interfaces-constraints.md",
            "references/06-testing-and-output.md",
            "references/07-writing-style.md",
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
        self.assertIn(f"${SKILL_NAME}", default_prompt.group(1))

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
            f"${SKILL_NAME} 我需要为平台支持某项新能力。",
            f"/{SKILL_NAME} 我需要为平台支持某项新能力。",
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
