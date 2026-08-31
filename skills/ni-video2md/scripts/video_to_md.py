#!/usr/bin/env python3
"""Download a public Douyin video and transcribe it to Markdown locally."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


GITHUB_RELEASES_URL = "https://api.github.com/repos/ggml-org/whisper.cpp/releases/latest"
WHISPER_MODEL_URLS = {
    "tiny": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin",
    "base": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin",
    "small": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin",
}
DEFAULT_PROMPT = (
    "中文视频转录；保留技术术语 Agent、AI、ERP、API、MCP、CLI、Workflow、"
    "Skill、SOP、Data Infra、Harness、Evaluation、FDE、ToB、RPA。"
)
DEFAULT_USER_AGENT = "ni-video2md/0.1"
URL_TRAILING_CHARS = ".,;:!?)]}>，。；：！？）》】”’"
TIMESTAMP_LINE = re.compile(
    r"^\[?\d{2}:\d{2}:\d{2}(?:[.,]\d{3})?\s*(?:-->|-)?\s*"
    r"\d{2}:\d{2}:\d{2}(?:[.,]\d{3})?\]?\s*"
)


class Video2MdError(RuntimeError):
    """A user-actionable failure without exposing signed media URLs."""


@dataclass(frozen=True)
class CapturedPage:
    source_url: str
    canonical_url: str
    title: str
    media_urls: tuple[str, ...]
    user_agent: str
    cookie_header: str


def cache_root() -> Path:
    configured = os.environ.get("NI_VIDEO2MD_HOME", "").strip()
    if configured:
        return Path(configured).expanduser()

    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA", str(Path.home()))
        return Path(base) / "ni-video2md"

    base = os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))
    return Path(base) / "ni-video2md"


def extract_source_url(source: str) -> str:
    """Extract the first HTTP(S) URL from a pasted share sentence."""

    urls = re.findall(r"https?://[^\s<>\"']+", source)
    if not urls:
        raise ValueError("没有找到 http(s) 视频链接；请粘贴视频 URL 或完整分享文案。")
    return urls[0].rstrip(URL_TRAILING_CHARS)


def safe_filename(value: str, fallback: str = "video-transcript") -> str:
    normalized = re.sub(r"[^\w\-\u4e00-\u9fff.]+", "-", value.strip())
    normalized = normalized.strip("-._")
    return (normalized or fallback)[:100]


def normalize_output_path(value: str | None, title: str) -> Path:
    if value:
        output = Path(value).expanduser()
        if output.suffix.lower() != ".md":
            if output.suffix:
                raise ValueError("输出文件必须使用 .md 扩展名。")
            output = output.with_suffix(".md")
        return output

    return Path.cwd() / f"{safe_filename(title)}.md"


def yaml_string(value: str) -> str:
    return json.dumps(value.replace("\r", " ").replace("\n", " ").strip(), ensure_ascii=False)


def clean_transcript(text: str) -> str:
    lines: list[str] = []
    for raw_line in text.replace("\ufeff", "").splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        line = TIMESTAMP_LINE.sub("", line).strip()
        if not line:
            continue
        lines.append(line)
    if not lines:
        raise Video2MdError("Whisper 没有生成有效文字稿。")
    return "\n".join(lines)


def render_markdown(
    *,
    source_url: str,
    title: str,
    captured_at: str,
    model: str,
    language: str,
    transcript: str,
) -> str:
    heading = title.strip() or "视频文字稿"
    return "\n".join(
        [
            "---",
            f"source: {yaml_string(source_url)}",
            f"title: {yaml_string(heading)}",
            f"captured_at: {yaml_string(captured_at)}",
            'transcription: "local whisper.cpp"',
            f"model: {yaml_string(model)}",
            f"language: {yaml_string(language)}",
            "---",
            "",
            f"# {heading}",
            "",
            "## 文字稿",
            "",
            clean_transcript(transcript),
            "",
        ]
    )


def request_headers(extra: dict[str, str] | None = None) -> dict[str, str]:
    headers = {"User-Agent": DEFAULT_USER_AGENT}
    if extra:
        headers.update(extra)
    return headers


def download_file(url: str, target: Path, *, headers: dict[str, str] | None = None) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_suffix(target.suffix + ".part")
    try:
        request = urllib.request.Request(url, headers=request_headers(headers))
        with urllib.request.urlopen(request, timeout=180) as response, partial.open("wb") as stream:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                stream.write(chunk)
    except (OSError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        partial.unlink(missing_ok=True)
        raise Video2MdError("下载公开依赖失败，请检查网络，或手动准备该依赖。") from exc
    partial.replace(target)


def fetch_json(url: str) -> dict[str, Any]:
    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": DEFAULT_USER_AGENT,
                "Accept": "application/vnd.github+json",
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except (OSError, ValueError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        raise Video2MdError("无法读取 Whisper.cpp 发布信息，请检查网络或手动安装 whisper-cli。") from exc
    if not isinstance(payload, dict):
        raise Video2MdError("Whisper.cpp 发布信息格式异常。")
    return payload


def safe_extract(zip_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    try:
        with zipfile.ZipFile(zip_path) as archive:
            for member in archive.infolist():
                target = (destination / member.filename).resolve()
                if root != target and root not in target.parents:
                    raise Video2MdError("依赖压缩包包含越界路径，已拒绝解压。")
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source, target.open("wb") as stream:
                    shutil.copyfileobj(source, stream)
    except (OSError, zipfile.BadZipFile) as exc:
        raise Video2MdError("依赖压缩包损坏或无法解压。") from exc


def find_file(root: Path, names: Iterable[str]) -> Path | None:
    wanted = {name.lower() for name in names}
    if not root.exists():
        return None
    for candidate in root.rglob("*"):
        if candidate.is_file() and candidate.name.lower() in wanted:
            return candidate
    return None


def configured_executable(*names: str) -> Path | None:
    for env_name in names:
        value = os.environ.get(env_name, "").strip()
        if value:
            configured = Path(value).expanduser()
            if configured.is_file():
                return configured.resolve()
    for name in names:
        found = shutil.which(name)
        if found:
            return Path(found).resolve()
    return None


def ensure_ffmpeg() -> Path:
    existing = configured_executable("NI_VIDEO2MD_FFMPEG", "FFMPEG_PATH", "ffmpeg", "ffmpeg.exe")
    if existing:
        return existing

    if platform.system() != "Windows":
        raise Video2MdError(
            "没有找到 ffmpeg。请先安装 ffmpeg，或设置 NI_VIDEO2MD_FFMPEG；"
            "当前自动下载路径只覆盖 Windows。"
        )

    root = cache_root() / "ffmpeg"
    cached = find_file(root, ("ffmpeg.exe",))
    if cached:
        return cached

    archive = cache_root() / "downloads" / "ffmpeg-release-essentials.zip"
    if not archive.exists():
        print("未找到 ffmpeg，正在下载 Windows 便携版…", file=sys.stderr)
        download_file(
            "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
            archive,
        )
    safe_extract(archive, root)
    cached = find_file(root, ("ffmpeg.exe",))
    if not cached:
        raise Video2MdError("ffmpeg 下载完成但未找到可执行文件。")
    return cached


def select_whisper_asset(release: dict[str, Any], system: str, machine: str) -> dict[str, str] | None:
    assets = release.get("assets", [])
    if not isinstance(assets, list):
        return None

    system_name = system.lower()
    machine_name = machine.lower()
    preferred_names: tuple[str, ...]
    if system_name == "windows" and machine_name in {"amd64", "x86_64"}:
        preferred_names = ("whisper-bin-x64.zip",)
    elif system_name == "linux" and machine_name in {"amd64", "x86_64"}:
        preferred_names = ("whisper-bin-linux-x64.zip", "whisper-bin-linux-amd64.zip")
    elif system_name == "darwin" and machine_name in {"arm64", "aarch64"}:
        preferred_names = ("whisper-bin-macos-arm64.zip", "whisper-bin-macos-arm64.tar.gz")
    else:
        return None

    for asset in assets:
        if not isinstance(asset, dict):
            continue
        name = str(asset.get("name", ""))
        url = str(asset.get("browser_download_url", ""))
        if name in preferred_names and url:
            return {"name": name, "url": url}
    return None


def ensure_whisper_cli() -> Path:
    existing = configured_executable(
        "NI_VIDEO2MD_WHISPER_CLI",
        "WHISPER_CLI",
        "whisper-cli",
        "whisper-cli.exe",
    )
    if existing:
        return existing

    root = cache_root() / "whisper"
    cached = find_file(root, ("whisper-cli", "whisper-cli.exe"))
    if cached:
        return cached

    if platform.system() != "Windows":
        raise Video2MdError(
            "没有找到 whisper-cli。请安装 whisper.cpp，或设置 NI_VIDEO2MD_WHISPER_CLI；"
            "当前自动下载路径只覆盖 Windows x64。"
        )

    release = fetch_json(GITHUB_RELEASES_URL)
    asset = select_whisper_asset(release, platform.system(), platform.machine())
    if not asset:
        raise Video2MdError("没有找到当前平台对应的 Whisper.cpp 预编译包，请手动安装 whisper-cli。")

    archive = cache_root() / "downloads" / asset["name"]
    if not archive.exists():
        print("未找到 whisper-cli，正在下载本地 Whisper.cpp…", file=sys.stderr)
        download_file(asset["url"], archive)
    tag = safe_filename(str(release.get("tag_name", "latest")), "latest")
    safe_extract(archive, root / tag)
    cached = find_file(root / tag, ("whisper-cli.exe", "whisper-cli"))
    if not cached:
        raise Video2MdError("Whisper.cpp 下载完成但未找到 whisper-cli。")
    return cached


def ensure_model(model_size: str) -> Path:
    env_model = os.environ.get("NI_VIDEO2MD_MODEL", os.environ.get("WHISPER_MODEL", "")).strip()
    if env_model and Path(env_model).is_file():
        return Path(env_model).expanduser().resolve()

    model_path = cache_root() / "models" / f"ggml-{model_size}.bin"
    if not model_path.exists():
        print(f"未找到 {model_size} 模型，正在下载本地 Whisper 模型…", file=sys.stderr)
        download_file(WHISPER_MODEL_URLS[model_size], model_path)
    if model_path.stat().st_size == 0:
        raise Video2MdError("Whisper 模型文件为空。")
    return model_path


def browser_candidates() -> list[Path]:
    configured = os.environ.get("NI_VIDEO2MD_BROWSER", os.environ.get("BROWSER_PATH", "")).strip()
    candidates: list[Path] = []
    if configured:
        candidates.append(Path(configured).expanduser())

    names = ("google-chrome", "chromium", "chromium-browser", "microsoft-edge")
    for name in names:
        found = shutil.which(name)
        if found:
            candidates.append(Path(found))

    if platform.system() == "Windows":
        roots = [
            os.environ.get("PROGRAMFILES", ""),
            os.environ.get("PROGRAMFILES(X86)", ""),
            os.environ.get("LOCALAPPDATA", ""),
        ]
        relative_paths = (
            "Google\\Chrome\\Application\\chrome.exe",
            "Microsoft\\Edge\\Application\\msedge.exe",
            "Chromium\\Application\\chrome.exe",
        )
        for root in roots:
            if root:
                candidates.extend(Path(root) / relative for relative in relative_paths)
    elif platform.system() == "Darwin":
        candidates.extend(
            [
                Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
                Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
            ]
        )

    return [candidate.resolve() for candidate in candidates if candidate.is_file()]


def load_playwright():
    try:
        from playwright.sync_api import sync_playwright

        return sync_playwright
    except ImportError:
        print("未找到 Playwright，正在安装本地浏览器依赖…", file=sys.stderr)
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--user", "playwright"],
                check=True,
                stdout=subprocess.DEVNULL,
            )
            from playwright.sync_api import sync_playwright

            return sync_playwright
        except (OSError, subprocess.CalledProcessError, ImportError) as exc:
            raise Video2MdError("无法安装 Playwright；请手动执行 pip install playwright。") from exc


def launch_browser(playwright: Any) -> Any:
    candidates = browser_candidates()
    if candidates:
        try:
            return playwright.chromium.launch(headless=True, executable_path=str(candidates[0]))
        except Exception as exc:
            raise Video2MdError("检测到浏览器但无法启动，请设置 NI_VIDEO2MD_BROWSER。") from exc

    try:
        return playwright.chromium.launch(headless=True)
    except Exception:
        try:
            subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                check=True,
            )
            return playwright.chromium.launch(headless=True)
        except (OSError, subprocess.CalledProcessError) as exc:
            raise Video2MdError("没有可用浏览器，已尝试下载 Chromium 但失败。") from exc


def is_media_response(url: str, content_type: str) -> bool:
    lowered_url = url.lower()
    lowered_type = content_type.lower()
    if "media-audio" in lowered_url:
        return True
    if lowered_type.startswith("audio/"):
        return True
    return lowered_type.startswith("video/") and any(
        marker in lowered_url for marker in (".mp4", "/play/", "aweme")
    )


def capture_page(source_url: str) -> CapturedPage:
    sync_playwright = load_playwright()
    with sync_playwright() as playwright:
        browser = launch_browser(playwright)
        try:
            context = browser.new_context(locale="zh-CN")
            page = context.new_page()
            user_agent = DEFAULT_USER_AGENT
            media_urls: list[str] = []

            def on_response(response: Any) -> None:
                content_type = response.headers.get("content-type", "")
                if response.status in {200, 206} and is_media_response(response.url, content_type):
                    if response.url not in media_urls:
                        media_urls.append(response.url)

            page.on("response", on_response)
            try:
                page.goto(source_url, wait_until="domcontentloaded", timeout=60_000)
            except Exception:
                if page.url in {"", "about:blank"}:
                    raise Video2MdError("抖音页面无法打开，可能需要登录或遇到访问限制。")

            try:
                detected_user_agent = page.evaluate("navigator.userAgent")
                if isinstance(detected_user_agent, str) and detected_user_agent:
                    user_agent = detected_user_agent
            except Exception:
                pass

            page.wait_for_timeout(8_000)
            try:
                page.evaluate(
                    """() => {
                        for (const element of document.querySelectorAll('video, audio')) {
                            element.muted = true;
                            const pending = element.play();
                            if (pending) pending.catch(() => {});
                        }
                    }"""
                )
                page.wait_for_timeout(3_000)
            except Exception:
                pass

            try:
                dom_sources = page.eval_on_selector_all(
                    "video, audio",
                    "elements => elements.map(element => element.currentSrc || element.src).filter(Boolean)",
                )
            except Exception:
                dom_sources = []
            for source in dom_sources:
                if isinstance(source, str) and source.startswith("http") and source not in media_urls:
                    media_urls.append(source)

            if not media_urls:
                raise Video2MdError(
                    "没有捕获到公开媒体流；页面可能需要登录、遇到验证码，或抖音页面结构已变化。"
                )

            media_urls.sort(key=lambda value: (0 if "media-audio" in value.lower() else 1, len(value)))
            cookies = context.cookies()
            cookie_header = "; ".join(
                f"{cookie['name']}={cookie['value']}" for cookie in cookies if cookie.get("name")
            )
            title = page.title().strip() or "视频文字稿"
            canonical_url = page.url if page.url.startswith("http") else source_url
            return CapturedPage(
                source_url=source_url,
                canonical_url=canonical_url,
                title=title,
                media_urls=tuple(media_urls),
                user_agent=user_agent,
                cookie_header=cookie_header,
            )
        finally:
            browser.close()


def parse_content_range(value: str) -> tuple[int, int, int | None] | None:
    match = re.match(r"bytes\s+(\d+)-(\d+)/(\d+|\*)", value or "", re.IGNORECASE)
    if not match:
        return None
    total = None if match.group(3) == "*" else int(match.group(3))
    return int(match.group(1)), int(match.group(2)), total


def download_media(capture: CapturedPage, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    last_error: Video2MdError | None = None
    for media_url in capture.media_urls:
        partial = target.with_suffix(target.suffix + ".part")
        offset = 0
        try:
            complete = False
            with partial.open("wb") as stream:
                while True:
                    headers = {
                        "User-Agent": capture.user_agent,
                        "Referer": capture.canonical_url,
                    }
                    if capture.cookie_header:
                        headers["Cookie"] = capture.cookie_header
                    if offset:
                        headers["Range"] = f"bytes={offset}-"
                    request = urllib.request.Request(media_url, headers=headers)
                    with urllib.request.urlopen(request, timeout=180) as response:
                        status = getattr(response, "status", response.getcode())
                        data = response.read()
                        if status == 200 and offset == 0:
                            stream.write(data)
                            complete = True
                            break
                        if status == 200 and offset:
                            stream.seek(0)
                            stream.truncate(0)
                            stream.write(data)
                            complete = True
                            break
                        if status != 206:
                            raise Video2MdError("媒体流返回了不可用的 HTTP 状态。")

                        range_info = parse_content_range(response.headers.get("Content-Range", ""))
                        if not data:
                            raise Video2MdError("媒体流返回空内容。")
                        if range_info:
                            start, end, total = range_info
                            if start != offset:
                                raise Video2MdError("媒体流分片范围不连续。")
                            stream.write(data)
                            offset = end + 1
                            if total is None or offset >= total:
                                complete = True
                                break
                        else:
                            stream.write(data)
                            complete = True
                            break
            if complete:
                target.unlink(missing_ok=True)
                partial.replace(target)
                return
        except (OSError, urllib.error.URLError, urllib.error.HTTPError, Video2MdError) as exc:
            partial.unlink(missing_ok=True)
            last_error = exc if isinstance(exc, Video2MdError) else Video2MdError("媒体流下载失败。")

    raise last_error or Video2MdError("媒体流下载失败。")


def run_command(command: list[str], message: str) -> None:
    try:
        completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except OSError as exc:
        raise Video2MdError(message) from exc
    if completed.returncode != 0:
        raise Video2MdError(message)


def convert_to_wav(ffmpeg: Path, media: Path, wav: Path) -> None:
    run_command(
        [
            str(ffmpeg),
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(media),
            "-vn",
            "-ar",
            "16000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            str(wav),
        ],
        "ffmpeg 无法从视频流提取音频。",
    )


def transcribe(whisper_cli: Path, model: Path, wav: Path, output_base: Path, language: str) -> str:
    run_command(
        [
            str(whisper_cli),
            "-m",
            str(model),
            "-f",
            str(wav),
            "-l",
            language,
            "-otxt",
            "-of",
            str(output_base),
            "-ng",
            "-np",
            "--prompt",
            DEFAULT_PROMPT,
        ],
        "whisper.cpp 本地转录失败。",
    )
    text_path = output_base.with_suffix(".txt")
    if not text_path.is_file():
        raise Video2MdError("Whisper.cpp 未生成文字稿文件。")
    return clean_transcript(text_path.read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="将抖音视频 URL 或分享文案通过本地 Whisper 转成 Markdown 文字稿。"
    )
    parser.add_argument("source", help="视频 URL，或包含 URL 的完整分享文案")
    parser.add_argument("-o", "--output", help="Markdown 输出路径；默认写入当前目录")
    parser.add_argument("--model-size", choices=tuple(WHISPER_MODEL_URLS), default="small")
    parser.add_argument("--language", default="zh", help="Whisper 语言代码，默认 zh")
    parser.add_argument(
        "--keep-work",
        action="store_true",
        help="保留下载的媒体、WAV 和 Whisper 临时文件，便于排查；默认任务结束后清理",
    )
    parser.add_argument(
        "--work-dir",
        help="指定临时工作目录；指定后不会自动清理其中的媒体和中间文件",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        source_url = extract_source_url(args.source)
        ffmpeg = ensure_ffmpeg()
        whisper_cli = ensure_whisper_cli()
        model = ensure_model(args.model_size)
        capture = capture_page(source_url)

        if args.work_dir:
            work_dir = Path(args.work_dir).expanduser().resolve()
            work_dir.mkdir(parents=True, exist_ok=True)
            cleanup = False
        else:
            work_dir = Path(tempfile.mkdtemp(prefix="ni-video2md-"))
            cleanup = not args.keep_work

        try:
            print("正在下载视频音频并进行本地转录…", file=sys.stderr)
            media = work_dir / "source.mp4"
            wav = work_dir / "source.wav"
            transcript_base = work_dir / "transcript"
            download_media(capture, media)
            convert_to_wav(ffmpeg, media, wav)
            transcript = transcribe(
                whisper_cli,
                model,
                wav,
                transcript_base,
                args.language,
            )
            output = normalize_output_path(args.output, capture.title)
            output.parent.mkdir(parents=True, exist_ok=True)
            from datetime import datetime, timezone

            markdown = render_markdown(
                source_url=capture.canonical_url,
                title=capture.title,
                captured_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                model=args.model_size,
                language=args.language,
                transcript=transcript,
            )
            output.write_text(markdown, encoding="utf-8")
            print(f"已保存 Markdown：{output}")
            return 0
        finally:
            if cleanup:
                shutil.rmtree(work_dir, ignore_errors=True)
            elif not args.work_dir:
                print(f"已保留临时文件：{work_dir}", file=sys.stderr)
    except (ValueError, Video2MdError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2
    except Exception:
        print("错误：任务失败，请检查依赖和网络后重试。", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
