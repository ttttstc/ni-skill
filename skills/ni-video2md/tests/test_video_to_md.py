import importlib.util
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
        self.assertEqual(
            Path("transcript.md"),
            video_to_md.normalize_output_path("transcript", "ignored"),
        )
        with self.assertRaises(ValueError):
            video_to_md.normalize_output_path("transcript.srt", "ignored")

    def test_cleans_timestamps_but_keeps_transcript_lines(self) -> None:
        raw = "[00:00:00.000 --> 00:00:01.000] 你好\n\n这是第二句"
        self.assertEqual("你好\n这是第二句", video_to_md.clean_transcript(raw))

    def test_markdown_has_local_metadata_and_no_srt_output_contract(self) -> None:
        markdown = video_to_md.render_markdown(
            source_url="https://www.douyin.com/video/123",
            title="测试视频",
            captured_at="2026-08-31T00:00:00+00:00",
            model="small",
            language="zh",
            transcript="第一句\n第二句",
        )
        self.assertIn('transcription: "local whisper.cpp"', markdown)
        self.assertIn('model: "small"', markdown)
        self.assertIn("## 文字稿", markdown)
        self.assertNotIn(".srt", markdown)
        self.assertNotIn("-osrt", markdown)

    def test_removes_transient_work_dir_after_success(self) -> None:
        capture = video_to_md.CapturedPage(
            source_url="https://v.douyin.com/test/",
            canonical_url="https://www.douyin.com/video/123",
            title="测试视频",
            media_urls=("https://example.com/media.mp4",),
            user_agent="test-agent",
            cookie_header="",
        )
        work_dirs: list[Path] = []

        def fake_download(_capture: object, target: Path) -> None:
            work_dirs.append(target.parent)
            target.write_bytes(b"media")

        def fake_convert(_ffmpeg: Path, _media: Path, wav: Path) -> None:
            wav.write_bytes(b"wav")

        with tempfile.TemporaryDirectory() as output_dir:
            output = Path(output_dir) / "result.md"
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
            self.assertTrue(output.is_file())

    def test_removes_transient_work_dir_after_failure(self) -> None:
        capture = video_to_md.CapturedPage(
            source_url="https://v.douyin.com/test/",
            canonical_url="https://www.douyin.com/video/123",
            title="测试视频",
            media_urls=("https://example.com/media.mp4",),
            user_agent="test-agent",
            cookie_header="",
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


if __name__ == "__main__":
    unittest.main()
