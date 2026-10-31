#!/usr/bin/env python3
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SKILL_HOME = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_HOME / "scripts"))

from book_common import ManuscriptError, TeXCodec, discover_latin_font, discover_main_font, find_ghostscript, load_json, safe_filename, validate_manuscript
from build_style import build_style, load_themes
import install as install_skill


class PoetryBookSkillTests(unittest.TestCase):
    def test_install_removes_only_unmodified_legacy_fonts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            destination = root / "installed"
            (source / "assets" / "fonts").mkdir(parents=True)
            (source / "SKILL.md").write_text("name: ni-poetry-book\n", encoding="utf-8")
            (source / "assets" / "fonts" / "NotoSerifSC-VF.ttf").write_bytes(b"new font")
            (destination / "assets" / "fonts").mkdir(parents=True)
            (destination / "SKILL.md").write_text("name: ni-poetry-book\n", encoding="utf-8")
            fonts = destination / "assets" / "fonts"
            (fonts / "old.ttf").write_bytes(b"stock font")
            (fonts / "old-license.txt").write_bytes(b"stock license")
            (fonts / "custom.ttf").write_bytes(b"modified font")
            (fonts / "custom-license.txt").write_bytes(b"stock license")
            license_hash = hashlib.sha256(b"stock license").hexdigest()
            legacy = {
                "old.ttf": (hashlib.sha256(b"stock font").hexdigest(), "old-license.txt", license_hash),
                "custom.ttf": (hashlib.sha256(b"stock font").hexdigest(), "custom-license.txt", license_hash),
            }
            with patch.object(install_skill, "ROOT", source), patch.object(install_skill, "LEGACY_FONTS", legacy), patch.object(sys, "argv", ["install.py", "--dest", str(destination)]):
                install_skill.main()
            self.assertFalse((fonts / "old.ttf").exists())
            self.assertFalse((fonts / "old-license.txt").exists())
            self.assertEqual((fonts / "custom.ttf").read_bytes(), b"modified font")
            self.assertTrue((fonts / "custom-license.txt").exists())
            self.assertEqual((fonts / "NotoSerifSC-VF.ttf").read_bytes(), b"new font")

    def test_install_supports_legacy_console_encoding(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "中文路径"
            source, destination = root / "source", root / "installed"
            (source / "assets" / "fonts").mkdir(parents=True)
            (source / "SKILL.md").write_text("name: ni-poetry-book\n", encoding="utf-8")
            (destination / "assets" / "fonts").mkdir(parents=True)
            (destination / "SKILL.md").write_text("name: ni-poetry-book\n", encoding="utf-8")
            custom = destination / "assets" / "fonts" / "BabelStoneHan.ttf"
            custom.write_bytes(b"custom font")
            script = "import sys; from pathlib import Path; sys.path.insert(0, sys.argv[1]); import install; install.ROOT=Path(sys.argv[2]); sys.argv=['install.py', '--dest', sys.argv[3]]; install.main()"
            result = subprocess.run(
                [sys.executable, "-c", script, str(SKILL_HOME / "scripts"), str(source), str(destination)],
                env=dict(os.environ, PYTHONIOENCODING="cp1252"), capture_output=True, text=True, encoding="cp1252",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(custom.read_bytes(), b"custom font")

    def test_bundled_font_package_is_small(self):
        fonts = [font for font in (SKILL_HOME / "assets" / "fonts").iterdir() if font.suffix.lower() in {".ttf", ".otf", ".ttc", ".otc", ".woff", ".woff2"}]
        names = {font.name for font in fonts}
        self.assertIn("NotoSerifSC-VF.ttf", names)
        self.assertLessEqual(names, {"NotoSerifSC-VF.ttf", "AnthropicSerif-Regular.ttf", "AnthropicSerif-Italic.ttf"})
        self.assertLess(sum(font.stat().st_size for font in fonts), 26 * 1024 * 1024)

    def test_bundled_main_font_is_default_and_override_is_respected(self):
        bundled = SKILL_HOME / "assets" / "fonts" / "NotoSerifSC-VF.ttf"
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(discover_main_font(), bundled)
        with tempfile.NamedTemporaryFile(suffix=".ttf") as override:
            with patch.dict(os.environ, {"POETRY_BOOK_MAIN_FONT": override.name}):
                self.assertEqual(discover_main_font(), Path(override.name))

    def test_missing_latin_font_fails_with_setup_hint(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {}, clear=True), patch("book_common.SKILL_HOME", Path(directory)), patch("book_common.Path.home", return_value=Path(directory)):
                with self.assertRaisesRegex(ManuscriptError, "POETRY_BOOK_LATIN_FONT"):
                    discover_latin_font()

    def test_latin_font_prefers_explicit_then_portable_then_home(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            portable = root / "skill" / "assets" / "fonts" / "AnthropicSerif-Regular.ttf"
            local = root / "home" / ".local" / "share" / "ni-skill" / "fonts" / "AnthropicSerif-Regular.ttf"
            override = root / "override.ttf"
            portable.parent.mkdir(parents=True)
            local.parent.mkdir(parents=True)
            local.write_bytes(b"local")
            override.write_bytes(b"override")
            with patch.dict(os.environ, {}, clear=True), patch("book_common.SKILL_HOME", root / "skill"), patch("book_common.Path.home", return_value=root / "home"):
                self.assertEqual(discover_latin_font(), local.resolve())
                portable.write_bytes(b"portable")
                self.assertEqual(discover_latin_font(), portable.resolve())
                with patch.dict(os.environ, {"POETRY_BOOK_LATIN_FONT": str(override)}):
                    self.assertEqual(discover_latin_font(), override.resolve())

    def test_missing_cjk_character_fails_instead_of_silent_substitution(self):
        with self.assertRaisesRegex(ManuscriptError, "U\\+20000"):
            TeXCodec().tex(chr(0x20000))

    def test_ghostscript_finds_windows_console_executable(self):
        with patch("book_common.shutil.which", side_effect=lambda name: "C:/gswin64c.exe" if name == "gswin64c" else None):
            self.assertEqual(find_ghostscript(), "C:/gswin64c.exe")

    @classmethod
    def setUpClass(cls):
        cls.example = load_json(SKILL_HOME / "examples" / "book.json")

    def style_args(self, theme, output):
        return argparse.Namespace(
            config=str(SKILL_HOME / "assets" / "themes.json"),
            assets=str(SKILL_HOME / "assets"),
            font_dir=str(SKILL_HOME / "assets" / "fonts"),
            theme=theme,
            output=str(output),
            title="月照诗心",
            subtitle="独立测试",
            author="李清照",
            series="编年诗选",
            edition="测试本",
            seal="易安",
            subject="通用技能测试",
            keywords="诗词,横排",
        )

    def test_six_themes_generate_real_styles(self):
        payload, _ = load_themes(SKILL_HOME / "assets" / "themes.json")
        self.assertEqual(payload["default"], "song-mist")
        self.assertEqual(len(payload["themes"]), 6)
        with tempfile.TemporaryDirectory() as directory:
            for theme in payload["themes"]:
                with self.subTest(theme=theme["id"]):
                    output = Path(directory) / f"{theme['id']}.tex"
                    with patch.dict(os.environ, {"POETRY_BOOK_LATIN_FONT": str(SKILL_HOME / "assets" / "fonts" / "NotoSerifSC-VF.ttf")}):
                        result = build_style(self.style_args(theme["id"], output))
                    self.assertEqual(result["theme"], theme["id"])
                    style = output.read_text(encoding="utf-8")
                    self.assertIn("\\newcommand{\\ThemeCover}", style)
                    self.assertIn("月照诗心", style)
                    self.assertNotIn("%THEME_DEFINITIONS%", style)
                    self.assertIn((SKILL_HOME / "assets" / "fonts").as_posix(), style)
                    self.assertIn("NotoSerifSC-VF.ttf", style)

    def test_unknown_theme_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ManuscriptError, "未知主题"):
                build_style(self.style_args("not-a-theme", Path(directory) / "style.tex"))

    def test_theme_list_cli(self):
        result = subprocess.run(
            [sys.executable, str(SKILL_HOME / "scripts" / "build_style.py"), "--list"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(len(json.loads(result.stdout)["themes"]), 6)

    def test_theme_list_cli_supports_legacy_console_encoding(self):
        env = dict(os.environ, PYTHONIOENCODING="cp1252")
        result = subprocess.run(
            [sys.executable, str(SKILL_HOME / "scripts" / "build_style.py"), "--list"],
            check=True, capture_output=True, text=True, encoding="ascii", env=env,
        )
        self.assertEqual(json.loads(result.stdout)["themes"][0]["name"], "烟雨留白")

    def test_example_is_valid_and_not_sushi(self):
        quality = validate_manuscript(self.example)
        self.assertEqual(quality["works"], 4)
        self.assertEqual(quality["warnings"], [])
        self.assertEqual(self.example["metadata"]["author"], "李清照")

    def test_duplicate_work_id_fails(self):
        payload = copy.deepcopy(self.example)
        payload["chapters"][0]["works"][1]["id"] = "L001"
        with self.assertRaisesRegex(ManuscriptError, "ID 重复"):
            validate_manuscript(payload)

    def test_reverse_chronology_fails(self):
        payload = copy.deepcopy(self.example)
        payload["chapters"][0]["works"][0]["date"].update({"start": 1200, "end": 1200})
        with self.assertRaisesRegex(ManuscriptError, "升序"):
            validate_manuscript(payload)

    def test_unsafe_work_id_fails(self):
        payload = copy.deepcopy(self.example)
        payload["chapters"][0]["works"][0]["id"] = "../escape"
        with self.assertRaisesRegex(ManuscriptError, "id"):
            validate_manuscript(payload)

    def test_missing_source_fails(self):
        payload = copy.deepcopy(self.example)
        payload["chapters"][0]["works"][0]["sources"] = []
        with self.assertRaisesRegex(ManuscriptError, "来源"):
            validate_manuscript(payload)

    def test_empty_paragraph_fails(self):
        payload = copy.deepcopy(self.example)
        payload["chapters"][0]["works"][0]["paragraphs"] = [""]
        with self.assertRaisesRegex(ManuscriptError, "非空文本"):
            validate_manuscript(payload)

    def test_output_filename_cannot_escape(self):
        self.assertEqual(safe_filename("诗/词"), "诗_词")
        with self.assertRaises(ManuscriptError):
            safe_filename("..")

    def test_duplicate_chapter_id_fails(self):
        payload = copy.deepcopy(self.example)
        payload["chapters"][1]["id"] = "early"
        with self.assertRaisesRegex(ManuscriptError, "章节 ID 重复"):
            validate_manuscript(payload)

    def test_unknown_year_must_use_appendix(self):
        payload = copy.deepcopy(self.example)
        payload["chapters"][0]["works"][0]["date"].update({"start": None, "end": None})
        with self.assertRaisesRegex(ManuscriptError, "appendix"):
            validate_manuscript(payload)

    def test_index_must_be_boolean(self):
        payload = copy.deepcopy(self.example)
        payload["index"] = "false"
        with self.assertRaisesRegex(ManuscriptError, "布尔值"):
            validate_manuscript(payload)

    def test_appendix_only_book_renders(self):
        from book_common import TeXCodec, normalized_metadata
        from render_book import render_manuscript, validation_expectations

        payload = copy.deepcopy(self.example)
        del payload["chapters"]
        self.assertEqual(validate_manuscript(payload)["works"], 1)
        rendered = render_manuscript(payload, TeXCodec())
        self.assertIn("系年未详作品", rendered)
        expectations = validation_expectations(payload, normalized_metadata(payload))
        self.assertEqual(expectations["golden"], {"L004": "千古风流八咏楼，江山留与后人愁。"})

    def test_no_machine_specific_paths_in_skill(self):
        paths = [SKILL_HOME / "SKILL.md"]
        paths.extend((SKILL_HOME / "scripts").glob("*.py"))
        paths.extend((SKILL_HOME / "assets").rglob("*.tex"))
        for path in paths:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("/Users/", text)
                self.assertNotIn("sushi-poetry-book", text)


if __name__ == "__main__":
    unittest.main()
