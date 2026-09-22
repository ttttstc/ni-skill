#!/usr/bin/env python3
"""Parallel-shard real-media ASR for ni-work-tutor.

Evidence policy:
- never read platform subtitles / AI transcripts;
- only bytes captured from the actual public media page are transcribed;
- media is temporary and deleted after each item;
- transcript segments keep timestamps for evidence anchoring.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

import requests
from faster_whisper import WhisperModel
from playwright.sync_api import sync_playwright

MEDIA_MARKERS = (".mp4", ".m4a", ".mp3", ".aac", ".webm", "/play/", "media-audio", "aweme")


def load_posts(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def capture_media(page, context, url: str) -> tuple[str, dict[str, str]]:
    media: list[tuple[str, str]] = []

    def on_response(resp):
        try:
            ctype = (resp.headers.get("content-type") or "").lower()
            u = resp.url
            if resp.status not in (200, 206):
                return
            if (
                ctype.startswith("audio/")
                or ctype.startswith("video/")
                or any(m in u.lower() for m in MEDIA_MARKERS)
            ):
                if all(existing[0] != u for existing in media):
                    media.append((u, ctype))
        except Exception:
            pass

    page.on("response", on_response)
    page.goto(url, wait_until="domcontentloaded", timeout=90_000)
    page.wait_for_timeout(5_000)
    try:
        page.evaluate("""() => {
          for (const e of document.querySelectorAll('video,audio')) {
            e.muted = true;
            const p = e.play();
            if (p) p.catch(() => {});
          }
        }""")
        page.wait_for_timeout(4_000)
    except Exception:
        pass

    try:
        dom = page.eval_on_selector_all(
            "video,audio",
            "els => els.map(e => e.currentSrc || e.src).filter(Boolean)",
        )
        for u in dom:
            if isinstance(u, str) and u.startswith("http") and all(x[0] != u for x in media):
                media.append((u, ""))
    except Exception:
        pass

    if not media:
        raise RuntimeError("no real media response captured")

    # Prefer a separate audio track (usually much smaller and faster), then
    # ordinary audio content-types, then video streams.
    def rank(item):
        u, ctype = item
        lu = u.lower()
        return (
            0 if "media-audio" in lu else
            1 if ctype.startswith("audio/") else
            2 if ctype.startswith("video/") else 3,
            len(u),
        )

    media.sort(key=rank)
    cookies = context.cookies()
    cookie_header = "; ".join(
        f"{c['name']}={c['value']}" for c in cookies if c.get("name")
    )
    ua = page.evaluate("navigator.userAgent")
    headers = {"User-Agent": ua, "Referer": page.url}
    if cookie_header:
        headers["Cookie"] = cookie_header
    return media[0][0], headers


def download(url: str, headers: dict[str, str], target: Path) -> int:
    with requests.get(url, headers=headers, timeout=120, stream=True) as r:
        r.raise_for_status()
        total = 0
        with target.open("wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)
                    total += len(chunk)
    if total < 4096:
        raise RuntimeError("captured media is unexpectedly small")
    return total


def to_wav(media: Path, wav: Path) -> None:
    cp = subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(media), "-vn", "-ac", "1", "-ar", "16000",
            "-c:a", "pcm_s16le", str(wav),
        ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    if cp.returncode != 0 or not wav.exists() or wav.stat().st_size < 4096:
        raise RuntimeError("ffmpeg could not extract a usable audio track")


def transcribe(model: WhisperModel, wav: Path) -> tuple[list[dict[str, Any]], str, float]:
    segments, info = model.transcribe(
        str(wav),
        language="zh",
        beam_size=5,
        vad_filter=True,
        condition_on_previous_text=True,
    )
    rows = []
    texts = []
    for seg in segments:
        text = re.sub(r"\s+", " ", seg.text or "").strip()
        if not text:
            continue
        rows.append({
            "start": round(float(seg.start), 3),
            "end": round(float(seg.end), 3),
            "text": text,
        })
        texts.append(text)
    transcript = "".join(texts).strip()
    if len(transcript) < 8:
        raise RuntimeError("ASR produced no meaningful speech")
    return rows, transcript, float(getattr(info, "duration", 0.0) or 0.0)


def write_result(out_dir: Path, post: dict[str, Any], segments, transcript: str, model_name: str, duration: float):
    cid = str(post.get("content_id") or "")
    source = post.get("web_url") or f"https://www.douyin.com/video/{cid}"
    created = post.get("created_at")
    title = post.get("title") or post.get("description") or ""
    desc = post.get("description") or ""
    sha = hashlib.sha256(transcript.encode("utf-8")).hexdigest()

    json_payload = {
        "content_id": cid,
        "source": source,
        "created_at": created,
        "title": title,
        "description": desc,
        "transcription_source": "real_media_local_asr",
        "asr_engine": "faster-whisper",
        "model": model_name,
        "language": "zh",
        "audio_duration_seconds": round(duration, 3),
        "transcript_sha256": sha,
        "segments": segments,
        "transcript": transcript,
    }
    (out_dir / f"{cid}.json").write_text(
        json.dumps(json_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "---",
        f'content_id: "{cid}"',
        f'source: "{source}"',
        f'created_at: "{created or ""}"',
        'transcription_source: "real_media_local_asr"',
        'asr_engine: "faster-whisper"',
        f'model: "{model_name}"',
        'language: "zh"',
        f'transcript_sha256: "{sha}"',
        "---", "",
        f"# {title or cid}", "",
        "## 文字稿", "",
        transcript, "",
        "## 时间锚点", "",
    ]
    for seg in segments:
        md.append(f'- [{seg["start"]:.3f}-{seg["end"]:.3f}] {seg["text"]}')
    md.append("")
    (out_dir / f"{cid}.md").write_text("\n".join(md), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--posts", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--shard", type=int, required=True)
    ap.add_argument("--shards", type=int, required=True)
    ap.add_argument("--model", default="small")
    args = ap.parse_args()

    posts = load_posts(Path(args.posts))
    selected = [
        p for i, p in enumerate(posts)
        if i % args.shards == args.shard
    ]
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    status_path = out.parent / f"status-{args.shard}.jsonl"

    # One model instance per runner/shard.
    model = WhisperModel(args.model, device="cpu", compute_type="int8", cpu_threads=2)

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chrome")
        context = browser.new_context(locale="zh-CN", viewport={"width": 1280, "height": 900})
        try:
            for index, post in enumerate(selected, 1):
                cid = str(post.get("content_id") or "")
                kind = str(post.get("kind") or "")
                url = post.get("web_url") or (f"https://www.douyin.com/video/{cid}" if cid else "")
                row = {
                    "content_id": cid, "kind": kind, "source": url,
                    "shard": args.shard, "status": None, "error": None,
                }
                if not cid or not url:
                    row["status"] = "invalid_metadata"
                    results.append(row)
                    continue
                if kind and kind != "video":
                    row["status"] = "no_audio_scope"
                    results.append(row)
                    print(json.dumps(row, ensure_ascii=False), flush=True)
                    continue

                page = context.new_page()
                try:
                    media_url, headers = capture_media(page, context, url)
                    with tempfile.TemporaryDirectory(prefix=f"ni-work-{cid}-") as td:
                        media = Path(td) / "media.bin"
                        wav = Path(td) / "audio.wav"
                        size = download(media_url, headers, media)
                        to_wav(media, wav)
                        segments, transcript, duration = transcribe(model, wav)
                        write_result(out, post, segments, transcript, args.model, duration)
                    row.update({
                        "status": "ok",
                        "media_bytes": size,
                        "segment_count": len(segments),
                        "transcript_chars": len(transcript),
                    })
                except Exception as exc:
                    row["status"] = "failed"
                    row["error"] = f"{type(exc).__name__}: {str(exc)[:500]}"
                finally:
                    page.close()
                results.append(row)
                print(json.dumps({
                    "progress": f"{index}/{len(selected)}",
                    **row,
                }, ensure_ascii=False), flush=True)
                # Avoid hitting Douyin like a tight scraper loop.
                time.sleep(1.5)
        finally:
            browser.close()

    with status_path.open("w", encoding="utf-8") as f:
        for row in results:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    failures = sum(1 for r in results if r["status"] == "failed")
    print(json.dumps({
        "shard": args.shard,
        "selected": len(selected),
        "ok": sum(1 for r in results if r["status"] == "ok"),
        "excluded": sum(1 for r in results if r["status"] == "no_audio_scope"),
        "failed": failures,
    }, ensure_ascii=False))
    # Do not fail the job for individual videos: aggregate coverage decides.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
