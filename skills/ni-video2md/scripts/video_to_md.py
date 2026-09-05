#!/usr/bin/env python3
"""Download a public video and transcribe it to Markdown locally."""

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
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


GITHUB_RELEASES_URL = "https://api.github.com/repos/ggml-org/whisper.cpp/releases/latest"
YTDLP_RELEASE_URLS = {
    "Windows": "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
    "default": "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp",
}
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
SUPPORTED_PLATFORM_HOSTS = {
    "x": ("x.com", "twitter.com", "mobile.twitter.com", "t.co"),
    "youtube": ("youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"),
    "bilibili": ("bilibili.com", "www.bilibili.com", "m.bilibili.com", "b23.tv", "bili2233.cn"),
    "xiaohongshu": ("xiaohongshu.com", "www.xiaohongshu.com", "xhslink.com"),
}
PLATFORM_LABELS = {
    "x": "X",
    "youtube": "YouTube",
    "bilibili": "哔哩哔哩",
    "xiaohongshu": "小红书",
}
MEDIA_SUFFIXES = {
    ".avi",
    ".flv",
    ".m4a",
    ".mkv",
    ".mov",
    ".mp3",
    ".mp4",
    ".ogg",
    ".opus",
    ".ts",
    ".webm",
    ".wav",
}
UNKNOWN_AUTHOR = "未知作者"
SUMMARY_MAX_LENGTH = 80
AUTHOR_MAX_LENGTH = 32
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
    author: str = UNKNOWN_AUTHOR
    downloader: str = "browser"
    platform: str = "douyin"


def supported_platform(source_url: str) -> str | None:
    """Return the yt-dlp-backed platform for a public page URL, if known."""

    hostname = (urllib.parse.urlsplit(source_url).hostname or "").lower().rstrip(".")
    for platform_name, domains in SUPPORTED_PLATFORM_HOSTS.items():
        if hostname in domains or any(hostname.endswith(f".{domain}") for domain in domains):
            return platform_name
    return None


def public_source_url(source_url: str) -> str:
    """Return a stable source URL without short-lived platform access tokens."""

    if supported_platform(source_url) != "xiaohongshu":
        return source_url
    parsed = urllib.parse.urlsplit(source_url)
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))


def platform_label(platform_name: str) -> str:
    return PLATFORM_LABELS.get(platform_name, platform_name)


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


def normalize_title_component(value: str, fallback: str, limit: int) -> str:
    normalized = re.sub(r"[\x00-\x1f<>:\"/\\|?*]", "-", value)
    normalized = re.sub(r"\s+", " ", normalized).strip().rstrip(" .")
    normalized = normalized or fallback
    normalized = normalized[:limit].rstrip(" .-")
    return normalized or fallback


def safe_filename(value: str, fallback: str = "video-transcript") -> str:
    return normalize_title_component(value, fallback, 120)


def build_document_title(summary: str, author: str) -> str:
    summary_part = normalize_title_component(summary, "视频内容概述", SUMMARY_MAX_LENGTH)
    author_part = normalize_title_component(author, UNKNOWN_AUTHOR, AUTHOR_MAX_LENGTH)
    return f"{summary_part}-{author_part}"


def normalize_output_path(value: str | None, title: str) -> Path:
    filename = f"{safe_filename(title)}.md"
    if value:
        requested = Path(value).expanduser()
        if requested.suffix.lower() not in {"", ".md"}:
            raise ValueError("输出路径必须是目录或使用 .md 扩展名的路径。")
        output_dir = requested.parent if requested.suffix.lower() == ".md" else requested
        return output_dir / filename

    return Path.cwd() / filename


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


def split_transcript_sentences(text: str) -> list[str]:
    sentences: list[str] = []
    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if not line:
            continue
        parts = re.split(r"(?<=[。！？!?；;])|(?<=[.])\s+", line)
        sentences.extend(part.strip() for part in parts if part.strip())
    return sentences


def summary_terms(sentence: str) -> list[str]:
    terms = [
        token.lower()
        for token in re.findall(r"[A-Za-z][A-Za-z0-9_+#.-]*|\d+(?:\.\d+)?", sentence)
        if len(token) > 1
    ]
    for run in re.findall(r"[\u4e00-\u9fff]+", sentence):
        terms.extend(run[index : index + 2] for index in range(len(run) - 1))
    return terms


def one_sentence_summary(value: str) -> str:
    summary = re.sub(r"\s+", " ", value).strip()
    if len(summary) > SUMMARY_MAX_LENGTH:
        summary = summary[:SUMMARY_MAX_LENGTH].rstrip("，,、:：;； ") + "…"
    if not summary.endswith(("。", "！", "？", "!", "?", "…", ".")):
        summary += "。"
    return summary


def summarize_transcript(transcript: str) -> str:
    cleaned = clean_transcript(transcript)
    sentences = split_transcript_sentences(cleaned)
    if not sentences:
        raise Video2MdError("无法从文字稿生成一句话概括。")
    if len(sentences) == 1:
        return one_sentence_summary(sentences[0])

    frequencies: Counter[str] = Counter()
    sentence_terms: list[set[str]] = []
    for sentence in sentences:
        terms = set(summary_terms(sentence))
        sentence_terms.append(terms)
        frequencies.update(terms)

    scored = []
    for index, (sentence, terms) in enumerate(zip(sentences, sentence_terms)):
        coverage = sum(frequencies[term] for term in terms)
        length_bonus = min(len(sentence), SUMMARY_MAX_LENGTH) / SUMMARY_MAX_LENGTH
        opening_bonus = 0.15 * (1 - index / len(sentences))
        thesis_bonus = 0.8 if re.search(
            r"(?:不能|不是|关键|核心|本质|真正|需要|应该|因为|所以|为什么|如何)", sentence
        ) else 0
        supporting_penalty = 0.35 * sentence.count("、")
        if re.match(r"(?:还要|此外|另外|同时|具体来说|包括)", sentence):
            supporting_penalty += 0.8
        scored.append(
            (coverage + length_bonus + opening_bonus + thesis_bonus - supporting_penalty, -index, sentence)
        )
    return one_sentence_summary(max(scored)[2])


def normalize_author(value: str) -> str:
    return normalize_title_component(value, UNKNOWN_AUTHOR, AUTHOR_MAX_LENGTH)


def extract_author_hint(source: str) -> str:
    match = re.search(r"【\s*([^】]{1,80}?)\s*的作品】", source)
    return normalize_author(match.group(1)) if match else UNKNOWN_AUTHOR


def render_markdown(
    *,
    source_url: str,
    title: str,
    summary: str,
    author: str,
    captured_at: str,
    model: str,
    language: str,
    transcript: str,
) -> str:
    expected_title = build_document_title(summary, author)
    heading = title.strip() or expected_title
    if heading != expected_title:
        raise ValueError("Markdown 标题必须使用“一句话概括-作者”格式。")
    return "\n".join(
        [
            "---",
            f"source: {yaml_string(source_url)}",
            f"title: {yaml_string(heading)}",
            f"summary: {yaml_string(summary)}",
            f"author: {yaml_string(author)}",
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
        partial.replace(target)
    except (OSError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        partial.unlink(missing_ok=True)
        raise Video2MdError("下载公开依赖失败，请检查网络，或手动准备该依赖。") from exc


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


def normalized_path_entry(value: str | Path) -> str:
    raw_value = str(value).strip().strip('"')
    return os.path.normcase(os.path.normpath(os.path.expandvars(raw_value)))


def append_path_entry(path_value: str, directory: Path) -> tuple[str, bool]:
    entries = path_value.split(os.pathsep) if path_value else []
    directory_text = str(directory.expanduser().resolve())
    directory_key = normalized_path_entry(directory_text)
    if any(
        entry.strip() and normalized_path_entry(entry) == directory_key
        for entry in entries
    ):
        return path_value, False
    return os.pathsep.join(entries + [directory_text]), True


def add_to_current_path(directory: Path) -> bool:
    current_path = os.environ.get("PATH", "")
    updated_path, changed = append_path_entry(current_path, directory)
    if changed:
        os.environ["PATH"] = updated_path
    return changed


def persist_user_path(directory: Path) -> bool | None:
    """Add a tool directory to the Windows user PATH when possible."""

    if os.name != "nt":
        return False

    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            "Environment",
            0,
            winreg.KEY_READ | winreg.KEY_WRITE,
        ) as key:
            try:
                current_value, value_type = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                current_value, value_type = "", winreg.REG_EXPAND_SZ
            updated_value, changed = append_path_entry(str(current_value or ""), directory)
            if not changed:
                return False
            if value_type not in (winreg.REG_SZ, winreg.REG_EXPAND_SZ):
                value_type = winreg.REG_EXPAND_SZ
            winreg.SetValueEx(key, "Path", 0, value_type, updated_value)
            return True
    except (ImportError, OSError):
        return None


def expose_executable(executable: Path, label: str) -> Path:
    """Make an executable available to this process and future Windows shells."""

    directory = executable.resolve().parent
    changed = add_to_current_path(directory)
    if changed and os.name == "nt":
        persisted = persist_user_path(directory)
        if persisted is True:
            print(f"已将 {label} 安装目录加入 Windows 用户 PATH：{directory}", file=sys.stderr)
        elif persisted is None:
            print(
                f"已将 {label} 目录加入当前进程 PATH，但无法持久化用户 PATH；"
                "新开的终端可能需要手动配置。",
                file=sys.stderr,
            )
    return executable


def ensure_yt_dlp() -> Path:
    existing = configured_executable(
        "NI_VIDEO2MD_YTDLP",
        "YTDLP_PATH",
        "yt-dlp",
        "yt-dlp.exe",
    )
    if existing:
        return expose_executable(existing, "yt-dlp")

    system_name = platform.system()
    executable_name = "yt-dlp.exe" if system_name == "Windows" else "yt-dlp"
    cached = cache_root() / "yt-dlp" / executable_name
    if cached.is_file() and cached.stat().st_size:
        return expose_executable(cached, "yt-dlp")

    print("未找到 yt-dlp，正在下载视频下载器…", file=sys.stderr)
    download_file(YTDLP_RELEASE_URLS.get(system_name, YTDLP_RELEASE_URLS["default"]), cached)
    if not cached.is_file() or cached.stat().st_size == 0:
        raise Video2MdError("yt-dlp 下载完成但文件为空。")
    if system_name != "Windows":
        try:
            cached.chmod(cached.stat().st_mode | 0o111)
        except OSError as exc:
            raise Video2MdError("yt-dlp 下载完成但无法设置可执行权限。") from exc
    return expose_executable(cached, "yt-dlp")


def yt_dlp_runtime_args() -> list[str]:
    configured = os.environ.get("NI_VIDEO2MD_JS_RUNTIME", "").strip()
    if configured:
        return ["--no-js-runtimes", "--js-runtimes", configured]

    for runtime in ("deno", "node", "bun", "quickjs"):
        if shutil.which(runtime):
            return ["--no-js-runtimes", "--js-runtimes", runtime]
    return []


def yt_dlp_base_command(yt_dlp: Path) -> list[str]:
    return [
        str(yt_dlp),
        "--ignore-config",
        "--no-playlist",
        "--no-warnings",
        *yt_dlp_runtime_args(),
    ]


def yt_dlp_failure_message(platform_name: str, phase: str, details: str) -> str:
    lowered = details.lower()
    label = platform_label(platform_name)
    if any(
        marker in lowered
        for marker in (
            "login",
            "log in",
            "sign in",
            "private video",
            "members-only",
            "members only",
            "captcha",
            "not a bot",
            "requires authentication",
            "验证码",
            "登录",
        )
    ):
        return f"{label} 视频无法公开访问，可能需要登录、验证码或其他访问权限。"
    if "unsupported url" in lowered:
        return f"当前 yt-dlp 不支持该 {label} 视频链接，请更新 yt-dlp 后重试。"
    if "no video formats" in lowered or "requested format is not available" in lowered:
        return f"{label} 页面未提供可下载的公开视频格式，可能是页面变化或访问限制。"
    return f"yt-dlp 无法{phase}{label}视频，请确认链接可公开播放并更新 yt-dlp 后重试。"


def run_yt_dlp(command: list[str], platform_name: str, phase: str) -> subprocess.CompletedProcess[str]:
    try:
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
        )
    except subprocess.TimeoutExpired as exc:
        raise Video2MdError(f"yt-dlp {phase}{platform_label(platform_name)}视频超时。") from exc
    except OSError as exc:
        raise Video2MdError("无法启动 yt-dlp，请检查安装路径。") from exc
    if completed.returncode != 0:
        raise Video2MdError(
            yt_dlp_failure_message(platform_name, phase, completed.stderr or "")
        )
    return completed


def ensure_ffmpeg() -> Path:
    existing = configured_executable("NI_VIDEO2MD_FFMPEG", "FFMPEG_PATH", "ffmpeg", "ffmpeg.exe")
    if existing:
        return expose_executable(existing, "ffmpeg")

    if platform.system() != "Windows":
        raise Video2MdError(
            "没有找到 ffmpeg。请先安装 ffmpeg，或设置 NI_VIDEO2MD_FFMPEG；"
            "当前自动下载路径只覆盖 Windows。"
        )

    root = cache_root() / "ffmpeg"
    cached = find_file(root, ("ffmpeg.exe",))
    if cached:
        return expose_executable(cached, "ffmpeg")

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
    return expose_executable(cached, "ffmpeg")


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
        return expose_executable(existing, "whisper-cli")

    root = cache_root() / "whisper"
    cached = find_file(root, ("whisper-cli", "whisper-cli.exe"))
    if cached:
        return expose_executable(cached, "whisper-cli")

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
    return expose_executable(cached, "whisper-cli")


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
            try:
                detected_author = page.evaluate(
                    """() => {
                        const selectors = [
                            'meta[name="author"]',
                            'meta[property="og:author"]',
                            'meta[property="article:author"]',
                            '[data-e2e="video-author-nickname"]',
                            '[data-e2e="video-author-name"]',
                            '[data-e2e="video-author"]',
                            '[data-e2e="user-info"] a',
                            'a[href*="/user/"]'
                        ];
                        for (const selector of selectors) {
                            const element = document.querySelector(selector);
                            if (!element) continue;
                            const value = element.getAttribute('content') || element.textContent || '';
                            if (value.trim()) return value.trim();
                        }
                        for (const element of document.querySelectorAll('script[type="application/ld+json"]')) {
                            try {
                                const data = JSON.parse(element.textContent || '');
                                const author = Array.isArray(data) ? data[0]?.author : data?.author;
                                const name = Array.isArray(author) ? author[0]?.name : author?.name;
                                if (typeof name === 'string' && name.trim()) return name.trim();
                            } catch (_) {}
                        }
                        return '';
                    }"""
                )
            except Exception:
                detected_author = ""
            author = normalize_author(detected_author) if isinstance(detected_author, str) else UNKNOWN_AUTHOR
            canonical_url = page.url if page.url.startswith("http") else source_url
            return CapturedPage(
                source_url=source_url,
                canonical_url=canonical_url,
                title=title,
                media_urls=tuple(media_urls),
                user_agent=user_agent,
                cookie_header=cookie_header,
                author=author,
            )
        finally:
            browser.close()


def parse_yt_dlp_metadata(output: str, platform_name: str) -> dict[str, Any]:
    candidates = [output.strip()]
    candidates.extend(line.strip() for line in reversed(output.splitlines()))
    for candidate in candidates:
        if not candidate or not candidate.startswith("{"):
            continue
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    raise Video2MdError(f"yt-dlp 返回的 {platform_label(platform_name)} 视频信息格式异常。")


def metadata_text(info: dict[str, Any], keys: Iterable[str]) -> str:
    for key in keys:
        value = info.get(key)
        if not isinstance(value, str):
            continue
        normalized = value.strip()
        if normalized and normalized.lower() not in {"na", "n/a", "none"}:
            return normalized
    return ""


def inspect_with_yt_dlp(yt_dlp: Path, source_url: str, platform_name: str) -> CapturedPage:
    completed = run_yt_dlp(
        yt_dlp_base_command(yt_dlp)
        + ["--dump-single-json", "--skip-download", source_url],
        platform_name,
        "读取",
    )
    info = parse_yt_dlp_metadata(completed.stdout, platform_name)
    if info.get("_type") == "playlist" or isinstance(info.get("entries"), list):
        raise Video2MdError(f"暂不支持一次转录 {platform_label(platform_name)} 播放列表。")

    canonical_url = metadata_text(info, ("webpage_url", "original_url")) or source_url
    if not canonical_url.startswith("http"):
        canonical_url = source_url
    title = metadata_text(info, ("title", "fulltitle")) or f"{platform_label(platform_name)}视频文字稿"
    author = normalize_author(
        metadata_text(info, ("uploader", "channel", "creator", "artist", "uploader_id"))
    )
    return CapturedPage(
        source_url=source_url,
        canonical_url=canonical_url,
        title=title,
        media_urls=(),
        user_agent=DEFAULT_USER_AGENT,
        cookie_header="",
        author=author,
        downloader="yt-dlp",
        platform=platform_name,
    )


def download_with_yt_dlp(
    yt_dlp: Path,
    capture: CapturedPage,
    ffmpeg: Path,
    target: Path,
) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    output_template = str(target.with_suffix("")) + ".%(ext)s"
    command = yt_dlp_base_command(yt_dlp) + [
        "--format",
        "bv*+ba/b",
        "--merge-output-format",
        "mp4",
        "--ffmpeg-location",
        str(ffmpeg),
        "--output",
        output_template,
        "--no-part",
        "--no-overwrites",
        "--quiet",
        "--no-progress",
        capture.canonical_url,
    ]
    run_yt_dlp(command, capture.platform, "下载")

    if target.is_file() and target.stat().st_size:
        return
    candidates = [
        path
        for path in target.parent.glob(f"{target.stem}.*")
        if path.is_file() and path.suffix.lower() in MEDIA_SUFFIXES and path.stat().st_size
    ]
    if not candidates:
        raise Video2MdError(f"yt-dlp 完成后没有找到可处理的 {platform_label(capture.platform)} 媒体文件。")
    candidate = max(candidates, key=lambda path: path.stat().st_size)
    try:
        candidate.replace(target)
    except OSError as exc:
        raise Video2MdError("无法整理 yt-dlp 下载的临时媒体文件。") from exc


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


def transcribe_with_temporary_files(
    capture: CapturedPage,
    ffmpeg: Path,
    whisper_cli: Path,
    model: Path,
    language: str,
    yt_dlp: Path | None = None,
) -> str:
    """Download and transcribe media inside a directory removed on exit."""

    with tempfile.TemporaryDirectory(prefix="ni-video2md-") as temporary_name:
        work_dir = Path(temporary_name)
        media = work_dir / "source.mp4"
        wav = work_dir / "source.wav"
        transcript_base = work_dir / "transcript"
        if capture.downloader == "yt-dlp":
            if yt_dlp is None:
                raise Video2MdError("缺少 yt-dlp，无法下载该平台视频。")
            download_with_yt_dlp(yt_dlp, capture, ffmpeg, media)
        else:
            download_media(capture, media)
        convert_to_wav(ffmpeg, media, wav)
        return transcribe(
            whisper_cli,
            model,
            wav,
            transcript_base,
            language,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="将公开视频 URL 或分享文案通过本地 Whisper 转成 Markdown 文字稿。"
    )
    parser.add_argument("source", help="视频 URL，或包含 URL 的完整分享文案")
    parser.add_argument(
        "-o",
        "--output",
        help="Markdown 输出目录，或用于确定目录的 .md 路径；文件名始终按概括-作者生成",
    )
    parser.add_argument("--model-size", choices=tuple(WHISPER_MODEL_URLS), default="small")
    parser.add_argument("--language", default="zh", help="Whisper 语言代码，默认 zh")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        source_url = extract_source_url(args.source)
        ffmpeg = ensure_ffmpeg()
        whisper_cli = ensure_whisper_cli()
        model = ensure_model(args.model_size)
        source_platform = supported_platform(source_url)
        yt_dlp = ensure_yt_dlp() if source_platform else None
        capture = (
            inspect_with_yt_dlp(yt_dlp, source_url, source_platform)
            if source_platform and yt_dlp is not None
            else capture_page(source_url)
        )

        print("正在下载视频音频并进行本地转录…", file=sys.stderr)
        transcript = transcribe_with_temporary_files(
            capture,
            ffmpeg,
            whisper_cli,
            model,
            args.language,
            yt_dlp,
        )
        author = capture.author if capture.author != UNKNOWN_AUTHOR else extract_author_hint(args.source)
        summary = summarize_transcript(transcript)
        document_title = build_document_title(summary, author)
        output = normalize_output_path(args.output, document_title)
        output.parent.mkdir(parents=True, exist_ok=True)
        from datetime import datetime, timezone

        markdown = render_markdown(
            source_url=public_source_url(capture.canonical_url),
            title=document_title,
            summary=summary,
            author=author,
            captured_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            model=args.model_size,
            language=args.language,
            transcript=transcript,
        )
        output.write_text(markdown, encoding="utf-8")
        print(f"已保存 Markdown：{output}")
        return 0
    except (ValueError, Video2MdError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2
    except Exception:
        print("错误：任务失败，请检查依赖和网络后重试。", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
