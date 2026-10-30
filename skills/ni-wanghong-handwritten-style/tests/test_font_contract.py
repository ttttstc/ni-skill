#!/usr/bin/env python3
from __future__ import annotations

import unittest
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
TARGET_FAMILY = "HanziPen SC"
sys.path.insert(0, str(SKILL_DIR / "scripts"))
from prepare_render_html import validate_font_file


class PreviewFontContractTests(unittest.TestCase):
    def test_template_prefers_hanzipen_and_has_portable_fallback(self) -> None:
        css = (SKILL_DIR / "assets" / "template.css").read_text(encoding="utf-8")
        self.assertIn(f'--hand: "{TARGET_FAMILY}", "Wanghong Portable";', css)
        self.assertIn("--font-sans: var(--hand);", css)
        self.assertIn("--font-display: var(--hand);", css)
        self.assertIn("--font-mono: var(--hand);", css)
        self.assertIn("--font-serif: var(--hand);", css)

    def test_bundled_font_is_the_expected_font(self) -> None:
        font = SKILL_DIR / "assets" / "fonts" / "Xiaolai-Regular.ttf"
        self.assertEqual(validate_font_file(font), "Xiaolai")
        with self.assertRaises(ValueError):
            validate_font_file(SKILL_DIR / "SKILL.md")

    def test_shared_assets_use_the_same_family(self) -> None:
        base = (SKILL_DIR / "assets" / "base.css").read_text(encoding="utf-8")
        annotations = (SKILL_DIR / "assets" / "neat-annotations.css").read_text(
            encoding="utf-8"
        )
        runtime = (SKILL_DIR / "assets" / "runtime.js").read_text(
            encoding="utf-8"
        )
        self.assertIn('fonts/Xiaolai-Regular.ttf', base)
        self.assertIn(f"--font-sans: '{TARGET_FAMILY}', 'Wanghong Portable';", base)
        self.assertIn(f"--font-serif: '{TARGET_FAMILY}', 'Wanghong Portable';", base)
        self.assertIn(f"--font-mono: '{TARGET_FAMILY}', 'Wanghong Portable';", base)
        self.assertIn(f"--ann-font: '{TARGET_FAMILY}', 'Wanghong Portable';", annotations)
        self.assertIn(f'font-family: "{TARGET_FAMILY}", "Wanghong Portable";', runtime)

    def test_instructions_use_preview_as_the_glyph_reference(self) -> None:
        skill = (SKILL_DIR / "references" / "ppt-workflow.md").read_text(encoding="utf-8")
        guide = (SKILL_DIR / "references" / "style-guide.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("assets/preview-cover.png", skill)
        self.assertIn("assets/preview-cover.png", guide)
        self.assertIn("随包的小赖字体", skill)

    def test_static_renderer_injects_and_checks_the_font_file(self) -> None:
        preparer = (SKILL_DIR / "scripts" / "prepare_render_html.py").read_text(
            encoding="utf-8"
        )
        renderer = (SKILL_DIR / "scripts" / "render.sh").read_text(encoding="utf-8")
        self.assertIn("@font-face", preparer)
        self.assertIn('DEMO_FONT_POSTSCRIPT = "HanziPenSC-W3"', preparer)
        self.assertIn('PORTABLE_FONT_POSTSCRIPT = "Xiaolai"', preparer)
        self.assertIn("validate_font_file(font)", preparer)
        self.assertIn("dataset.wanghongFontReady", preparer)
        self.assertIn("prepare_render_html.py", renderer)
        self.assertIn("--dump-dom", renderer)
        self.assertIn('data-wanghong-font-ready="yes"', renderer)


if __name__ == "__main__":
    unittest.main()
