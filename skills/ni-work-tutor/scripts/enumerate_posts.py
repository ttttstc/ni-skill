#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright

AUTHOR_ID = "MS4wLjABAAAAuf_LJbB5-Ax1mK7A-haX99dBuPsiU5KvqVG183M-xEZjesCpObHPdYe6pdC_XyoG"
AUTHOR_NAME = "陈小树🌲"
PROFILE_URL = f"https://www.douyin.com/user/{AUTHOR_ID}"


def normalize_aweme(item: dict[str, Any]) -> dict[str, Any]:
    aweme_id = str(item.get("aweme_id") or "").strip()
    desc = str(item.get("desc") or "").strip()
    author = item.get("author") or {}
    video = item.get("video") or {}
    images = item.get("images") or []
    image_post_info = item.get("image_post_info") or {}
    is_image = bool(images or image_post_info)
    return {
        "content_id": aweme_id,
        "web_url": f"https://www.douyin.com/{'note' if is_image else 'video'}/{aweme_id}",
        "description": desc,
        "created_at_epoch": item.get("create_time"),
        "duration_ms": video.get("duration"),
        "kind": "image_album" if is_image else "video",
        "author_sec_uid": str(author.get("sec_uid") or ""),
        "author_nickname": str(author.get("nickname") or ""),
        "stats": item.get("statistics") or {},
        "raw_has_video": bool(video),
        "raw_has_images": bool(images or image_post_info),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="posts.jsonl")
    ap.add_argument("--summary", default="enumeration-summary.json")
    ap.add_argument("--max-scrolls", type=int, default=500)
    args = ap.parse_args()

    posts: dict[str, dict[str, Any]] = {}
    api_pages = 0
    saw_terminal = False
    errors: list[str] = []
    author_verified = False
    api_author_mismatch = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(locale="zh-CN", viewport={"width": 1440, "height": 1200})
        page = context.new_page()

        def ingest_item(item: dict[str, Any]) -> None:
            nonlocal api_author_mismatch, author_verified
            normalized = normalize_aweme(item)
            cid = normalized["content_id"]
            if not cid:
                return
            sec_uid = normalized["author_sec_uid"]
            if sec_uid:
                if sec_uid != AUTHOR_ID:
                    api_author_mismatch += 1
                    return
                author_verified = True
            posts[cid] = normalized

        def on_response(resp: Any) -> None:
            nonlocal api_pages, saw_terminal
            if "/aweme/v1/web/aweme/post/" not in resp.url:
                return
            try:
                payload = resp.json()
                if not isinstance(payload, dict):
                    return
                api_pages += 1
                for item in payload.get("aweme_list") or []:
                    if isinstance(item, dict):
                        ingest_item(item)
                if payload.get("has_more") in (0, False, None):
                    # Only treat explicit terminal if an aweme_list was present.
                    if "aweme_list" in payload:
                        saw_terminal = True
                print(json.dumps({
                    "event": "page",
                    "api_pages": api_pages,
                    "posts": len(posts),
                    "has_more": payload.get("has_more"),
                    "max_cursor": payload.get("max_cursor"),
                }, ensure_ascii=False), flush=True)
            except Exception as exc:
                try:
                    body = resp.body()
                    diag = {
                        "status": resp.status,
                        "content_type": resp.headers.get("content-type"),
                        "content_length": resp.headers.get("content-length"),
                        "body_len": len(body or b""),
                        "resource_type": resp.request.resource_type,
                        "error": str(exc)[:200],
                    }
                    print(json.dumps({"event": "api_parse_failure", **diag}, ensure_ascii=False), flush=True)
                    errors.append("response:" + json.dumps(diag, ensure_ascii=False))
                except Exception as diag_exc:
                    errors.append("response:" + str(exc)[:200] + "|diag:" + str(diag_exc)[:100])

        page.on("response", on_response)
        def on_request_failed(req: Any) -> None:
            if "/aweme/v1/web/aweme/post/" in req.url:
                print(json.dumps({
                    "event": "api_request_failed",
                    "resource_type": req.resource_type,
                    "failure": req.failure,
                }, ensure_ascii=False), flush=True)
        page.on("requestfailed", on_request_failed)
        try:
            page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=90000)
            page.wait_for_timeout(10000)
            html = page.content()
            try:
                body_text = page.locator("body").inner_text(timeout=5000)
                for line in body_text.splitlines():
                    if "作品" in line or "粉丝" in line or "获赞" in line:
                        if len(line) < 120:
                            print(json.dumps({"event": "profile_text", "text": line}, ensure_ascii=False), flush=True)
            except Exception:
                pass
            if AUTHOR_ID in page.url or AUTHOR_ID in html:
                author_verified = True

            stagnant = 0
            previous_count = len(posts)
            for scroll_index in range(args.max_scrolls):
                # DOM fallback only collects IDs; API handler remains source of metadata.
                try:
                    hrefs = page.eval_on_selector_all(
                        'a[href*="/video/"],a[href*="/note/"]',
                        "els => els.map(e => e.href).filter(Boolean)",
                    )
                    for href in hrefs:
                        if not isinstance(href, str):
                            continue
                        for marker, kind in (("/video/", "video"), ("/note/", "image_album")):
                            if marker in href:
                                cid = href.split(marker, 1)[1].split("?", 1)[0].split("/", 1)[0]
                                if cid.isdigit() and cid not in posts:
                                    posts[cid] = {
                                        "content_id": cid,
                                        "web_url": f"https://www.douyin.com/{'note' if kind == 'image_album' else 'video'}/{cid}",
                                        "description": "",
                                        "created_at_epoch": None,
                                        "duration_ms": None,
                                        "kind": kind,
                                        "author_sec_uid": AUTHOR_ID,
                                        "author_nickname": AUTHOR_NAME,
                                        "stats": {},
                                        "raw_has_video": kind == "video",
                                        "raw_has_images": kind == "image_album",
                                        "metadata_source": "dom_fallback",
                                    }
                                break
                except Exception as exc:
                    errors.append("dom:" + str(exc)[:200])

                page.mouse.wheel(0, 8000)
                page.wait_for_timeout(1200)

                if len(posts) == previous_count:
                    stagnant += 1
                else:
                    stagnant = 0
                    previous_count = len(posts)

                if saw_terminal and stagnant >= 4:
                    break
                if stagnant >= 15:
                    errors.append("stopped_after_stagnant_scrolls")
                    break

            # One last wait for late network callbacks.
            page.wait_for_timeout(3000)
        except Exception as exc:
            errors.append("page:" + str(exc)[:500])
        finally:
            browser.close()

    ordered = sorted(
        posts.values(),
        key=lambda x: ((x.get("created_at_epoch") or 0), x["content_id"]),
        reverse=True,
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for item in ordered:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    summary = {
        "author_id": AUTHOR_ID,
        "author_name": AUTHOR_NAME,
        "profile_url": PROFILE_URL,
        "author_verified": author_verified,
        "api_pages": api_pages,
        "saw_terminal_page": saw_terminal,
        "total_posts": len(ordered),
        "video_posts": sum(1 for x in ordered if x.get("kind") == "video"),
        "image_posts": sum(1 for x in ordered if x.get("kind") == "image_album"),
        "dom_fallback_posts": sum(1 for x in ordered if x.get("metadata_source") == "dom_fallback"),
        "api_author_mismatch": api_author_mismatch,
        "errors": errors,
    }
    Path(args.summary).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    # Full-scan gate: verified author, at least one API page, and explicit terminal page.
    if not author_verified or api_pages == 0 or not saw_terminal or len(ordered) == 0:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
