#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import stat
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]


class DirectHtmlRendererContractTests(unittest.TestCase):
    def test_renderer_uses_original_html_dom(self) -> None:
        renderer = (SKILL_DIR / "scripts" / "render_html_video.mjs").read_text(
            encoding="utf-8"
        )
        self.assertIn("pathToFileURL", renderer)
        self.assertIn("querySelectorAll('.deck > .slide')", renderer)
        self.assertIn("page.screenshot", renderer)

    def test_renderer_locks_the_exact_demo_font(self) -> None:
        renderer = (SKILL_DIR / "scripts" / "render_html_video.mjs").read_text(
            encoding="utf-8"
        )
        self.assertIn("DEMO_FONT_FAMILY = 'HanziPen SC'", renderer)
        self.assertIn("DEMO_FONT_POSTSCRIPT = 'HanziPenSC-W3'", renderer)
        self.assertIn("PORTABLE_FONT_POSTSCRIPT = 'Xiaolai'", renderer)
        self.assertIn("--font-file", renderer)
        self.assertIn("new FontFace", renderer)
        self.assertIn("CSS.getPlatformFontsForNode", renderer)
        self.assertIn("图片示例字体校验失败", renderer)

    def test_renderer_encodes_silent_h264_mp4(self) -> None:
        renderer = (SKILL_DIR / "scripts" / "render_html_video.mjs").read_text(
            encoding="utf-8"
        )
        for token in (
            "'-an'",
            "'libx264'",
            "'yuv420p'",
            "'bt709'",
            "'1920x1080'",
        ):
            self.assertIn(token, renderer)

        wrapper = SKILL_DIR / "scripts" / "render_html_video.sh"
        text = wrapper.read_text(encoding="utf-8")
        self.assertIn("ffprobe", text)
        self.assertIn('if [[ "$audio_streams" != "0" ]]', text)
        if os.name != "nt":
            self.assertTrue(wrapper.stat().st_mode & stat.S_IXUSR)

    def test_wrapper_validates_with_the_combined_skill(self) -> None:
        wrapper = (SKILL_DIR / "scripts" / "render_html_video.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("$SKILL_DIR/scripts/check_deck.py", wrapper)
        self.assertIn("$SKILL_DIR/assets/template.css", wrapper)

    def test_dependency_is_pinned(self) -> None:
        package = json.loads((SKILL_DIR / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(package["dependencies"]["puppeteer-core"], "25.5.0")

    def test_skill_explicitly_preserves_demo_font_and_html_layout(self) -> None:
        skill = (SKILL_DIR / "references" / "video-workflow.md").read_text(encoding="utf-8")
        self.assertIn("直接渲染原 HTML DOM", skill)
        self.assertIn("不重新排版文字", skill)
        self.assertIn("与静态导出相同的选定字体", skill)
        self.assertIn("零条音频流", skill)


if __name__ == "__main__":
    unittest.main()
