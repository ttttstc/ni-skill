import importlib.util
import sys
import unittest
from pathlib import Path


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
