import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "video_to_md.py"
SPEC = importlib.util.spec_from_file_location("video_to_md", SCRIPT)
assert SPEC and SPEC.loader
video_to_md = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = video_to_md
SPEC.loader.exec_module(video_to_md)

ARCHIVE_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "archive_markdown.py"
ARCHIVE_SPEC = importlib.util.spec_from_file_location("archive_markdown", ARCHIVE_SCRIPT)
assert ARCHIVE_SPEC and ARCHIVE_SPEC.loader
archive_markdown = importlib.util.module_from_spec(ARCHIVE_SPEC)
sys.modules[ARCHIVE_SPEC.name] = archive_markdown
ARCHIVE_SPEC.loader.exec_module(archive_markdown)


class VideoToMarkdownTests(unittest.TestCase):
    def test_extracts_url_from_share_text_and_strips_punctuation(self) -> None:
        source = "点击链接打开，看看作品：https://v.douyin.com/RL48iNxXGTw/。"
        self.assertEqual(
            "https://v.douyin.com/RL48iNxXGTw/",
            video_to_md.extract_source_url(source),
        )

    def test_rejects_input_without_http_url(self) -> None:
        with self.assertRaises(ValueError):
            video_to_md.extract_source_url("没有链接")

    def test_output_path_is_markdown_only(self) -> None:
        title = video_to_md.build_document_title("一句话概括。", "作者")
        self.assertEqual(
            Path(f"{title}.md"),
            video_to_md.normalize_output_path("transcript.md", title),
        )
        self.assertEqual(
            Path("archive") / f"{title}.md",
            video_to_md.normalize_output_path("archive", title),
        )
        with self.assertRaises(ValueError):
            video_to_md.normalize_output_path("transcript.srt", title)

    def test_cleans_timestamps_but_keeps_transcript_lines(self) -> None:
        raw = "[00:00:00.000 --> 00:00:01.000] 你好\n\n这是第二句"
        self.assertEqual("你好\n这是第二句", video_to_md.clean_transcript(raw))

    def test_markdown_has_local_metadata_and_no_srt_output_contract(self) -> None:
        summary = "企业采购 AI Agent 不能只按单价判断。"
        author = "VA7"
        title = video_to_md.build_document_title(summary, author)
        markdown = video_to_md.render_markdown(
            source_url="https://www.douyin.com/video/123",
            title=title,
            summary=summary,
            author=author,
            captured_at="2026-08-31T00:00:00+00:00",
            model="small",
            language="zh",
            transcript="第一句\n第二句",
        )
        self.assertIn('transcription: "local whisper.cpp"', markdown)
        self.assertIn('model: "small"', markdown)
        self.assertIn(f'title: "{title}"', markdown)
        self.assertIn(f'summary: "{summary}"', markdown)
        self.assertIn('author: "VA7"', markdown)
        self.assertIn(f"# {title}", markdown)
        self.assertIn("## 文字稿", markdown)
        self.assertNotIn(".srt", markdown)
        self.assertNotIn("-osrt", markdown)

    def test_summary_is_one_sentence_and_uses_transcript_content(self) -> None:
        transcript = (
            "今天先聊一个常见误区。"
            "企业采购 AI Agent 不能只按一个 Agent 多少钱来判断。"
            "还要看知识库、ERP、工单系统、权限管理和操作追责。"
        )
        summary = video_to_md.summarize_transcript(transcript)
        self.assertIn("企业采购 AI Agent", summary)
        self.assertTrue(summary.endswith(("。", "！", "？", "!", "?", "…", ".")))
        self.assertEqual(1, len(video_to_md.split_transcript_sentences(summary)))

    def test_document_title_uses_summary_and_author(self) -> None:
        self.assertEqual(
            "企业采购 AI Agent 不能只按单价判断。-VA7",
            video_to_md.build_document_title("企业采购 AI Agent 不能只按单价判断。", "VA7"),
        )
        self.assertEqual(
            "视频内容概述-未知作者",
            video_to_md.build_document_title("", ""),
        )

    def test_extracts_author_hint_from_share_text(self) -> None:
        self.assertEqual(
            "VA7",
            video_to_md.extract_author_hint("看看【VA7的作品】分享 https://v.douyin.com/test/"),
        )

    def test_archives_markdown_without_deleting_or_overwriting(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "generated.md"
            archive_dir = root / "archive"
            source.write_text("# 文字稿\n", encoding="utf-8")

            target = archive_markdown.archive_markdown(source, archive_dir)

            self.assertEqual((archive_dir / source.name).resolve(), target)
            self.assertEqual("# 文字稿\n", source.read_text(encoding="utf-8"))
            self.assertEqual(source.read_text(encoding="utf-8"), target.read_text(encoding="utf-8"))
            with self.assertRaises(archive_markdown.ArchiveError):
                archive_markdown.archive_markdown(source, archive_dir)

    def test_removes_transient_work_dir_after_success(self) -> None:
        capture = video_to_md.CapturedPage(
            source_url="https://v.douyin.com/test/",
            canonical_url="https://www.douyin.com/video/123",
            title="测试视频",
            media_urls=("https://example.com/media.mp4",),
            user_agent="test-agent",
            cookie_header="",
            author="作者",
        )
        work_dirs: list[Path] = []

        def fake_download(_capture: object, target: Path) -> None:
            work_dirs.append(target.parent)
            target.write_bytes(b"media")

        def fake_convert(_ffmpeg: Path, _media: Path, wav: Path) -> None:
            wav.write_bytes(b"wav")

        with tempfile.TemporaryDirectory() as output_dir:
            output = Path(output_dir) / "result.md"
            expected_output = Path(output_dir) / "本地转录。-作者.md"
            with patch.object(video_to_md, "ensure_ffmpeg", return_value=Path("ffmpeg")), \
                patch.object(video_to_md, "ensure_whisper_cli", return_value=Path("whisper-cli")), \
                patch.object(video_to_md, "ensure_model", return_value=Path("model.bin")), \
                patch.object(video_to_md, "capture_page", return_value=capture), \
                patch.object(video_to_md, "download_media", side_effect=fake_download), \
                patch.object(video_to_md, "convert_to_wav", side_effect=fake_convert), \
                patch.object(video_to_md, "transcribe", return_value="本地转录"):
                self.assertEqual(
                    0,
                    video_to_md.main([capture.source_url, "-o", str(output)]),
                )

            self.assertEqual(1, len(work_dirs))
            self.assertFalse(work_dirs[0].exists())
            self.assertFalse(output.exists())
            self.assertTrue(expected_output.is_file())

    def test_removes_transient_work_dir_after_failure(self) -> None:
        capture = video_to_md.CapturedPage(
            source_url="https://v.douyin.com/test/",
            canonical_url="https://www.douyin.com/video/123",
            title="测试视频",
            media_urls=("https://example.com/media.mp4",),
            user_agent="test-agent",
            cookie_header="",
            author="作者",
        )
        work_dirs: list[Path] = []

        def failing_download(_capture: object, target: Path) -> None:
            work_dirs.append(target.parent)
            raise video_to_md.Video2MdError("模拟媒体下载失败")

        with tempfile.TemporaryDirectory() as output_dir:
            output = Path(output_dir) / "result.md"
            with patch.object(video_to_md, "ensure_ffmpeg", return_value=Path("ffmpeg")), \
                patch.object(video_to_md, "ensure_whisper_cli", return_value=Path("whisper-cli")), \
                patch.object(video_to_md, "ensure_model", return_value=Path("model.bin")), \
                patch.object(video_to_md, "capture_page", return_value=capture), \
                patch.object(video_to_md, "download_media", side_effect=failing_download):
                self.assertEqual(
                    2,
                    video_to_md.main([capture.source_url, "-o", str(output)]),
                )

            self.assertEqual(1, len(work_dirs))
            self.assertFalse(work_dirs[0].exists())
            self.assertFalse(output.exists())

    def test_selects_windows_x64_whisper_asset(self) -> None:
        release = {
            "assets": [
                {"name": "whisper-bin-linux-x64.zip", "browser_download_url": "linux"},
                {"name": "whisper-bin-x64.zip", "browser_download_url": "windows"},
            ]
        }
        self.assertEqual(
            {"name": "whisper-bin-x64.zip", "url": "windows"},
            video_to_md.select_whisper_asset(release, "Windows", "AMD64"),
        )

    def test_append_path_entry_deduplicates_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir).resolve()
            initial = os.pathsep.join([str(directory.parent), str(directory)])
            unchanged, changed = video_to_md.append_path_entry(initial, directory)
            self.assertFalse(changed)
            self.assertEqual(initial, unchanged)

            new_directory = directory / "bin"
            updated, changed = video_to_md.append_path_entry(initial, new_directory)
            self.assertTrue(changed)
            self.assertIn(str(new_directory.resolve()), updated.split(os.pathsep))

    def test_exposes_executable_directory_to_current_process_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            executable = Path(temp_dir) / "whisper-cli.exe"
            executable.write_bytes(b"test")
            with patch.dict(video_to_md.os.environ, {"PATH": "existing"}, clear=True), \
                patch.object(video_to_md, "persist_user_path", return_value=False) as persist:
                video_to_md.expose_executable(executable, "whisper-cli")

                self.assertIn(str(Path(temp_dir).resolve()), video_to_md.os.environ["PATH"].split(os.pathsep))
                if os.name == "nt":
                    persist.assert_called_once_with(Path(temp_dir).resolve())
                else:
                    persist.assert_not_called()

    def test_persists_path_to_windows_user_environment(self) -> None:
        class FakeRegistry:
            HKEY_CURRENT_USER = object()
            KEY_READ = 1
            KEY_WRITE = 2
            REG_SZ = 1
            REG_EXPAND_SZ = 2

            def __init__(self) -> None:
                self.current = "existing"
                self.updated: tuple[int, str] | None = None

            def OpenKey(self, *_args: object) -> "FakeRegistry":
                return self

            def __enter__(self) -> "FakeRegistry":
                return self

            def __exit__(self, *_args: object) -> bool:
                return False

            def QueryValueEx(self, *_args: object) -> tuple[str, int]:
                return self.current, self.REG_EXPAND_SZ

            def SetValueEx(
                self,
                _key: object,
                _name: str,
                _reserved: int,
                value_type: int,
                value: str,
            ) -> None:
                self.updated = (value_type, value)

        fake_registry = FakeRegistry()
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir).resolve()
            with patch.object(video_to_md.os, "name", "nt"), \
                patch.dict(sys.modules, {"winreg": fake_registry}):
                self.assertTrue(video_to_md.persist_user_path(directory))

        self.assertIsNotNone(fake_registry.updated)
        assert fake_registry.updated is not None
        self.assertIn(str(directory), fake_registry.updated[1].split(os.pathsep))


if __name__ == "__main__":
    unittest.main()
