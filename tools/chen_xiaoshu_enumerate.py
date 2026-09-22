#!/usr/bin/env python3
import json, time
from pathlib import Path
from playwright.sync_api import sync_playwright

SEED = "https://v.douyin.com/YkkwCC0b_3Y/"
OUT = Path("artifacts/chen-xiaoshu")
OUT.mkdir(parents=True, exist_ok=True)
raw_dir = OUT / "raw"
raw_dir.mkdir(exist_ok=True)

profile = {}
posts = {}
state = {"has_more": None, "cursor": None, "post_responses": 0}

def save_post(item):
    cid = str(item.get("aweme_id") or "")
    if not cid:
        return
    author = item.get("author") or {}
    posts[cid] = {
        "content_id": cid,
        "desc": item.get("desc") or "",
        "create_time": item.get("create_time"),
        "duration_ms": ((item.get("video") or {}).get("duration")),
        "aweme_type": item.get("aweme_type"),
        "author_sec_uid": author.get("sec_uid"),
        "author_nickname": author.get("nickname"),
        "url": f"https://www.douyin.com/video/{cid}",
    }
    (raw_dir / f"{cid}.json").write_text(
        json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8"
    )

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
    )
    context = browser.new_context(
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
        viewport={"width": 1440, "height": 1200},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/156.0.0.0 Safari/537.36"
        ),
    )
    page = context.new_page()

    def on_response(resp):
        try:
            u = resp.url
            if "/aweme/v1/web/aweme/detail/" in u:
                data = resp.json()
                item = data.get("aweme_detail") or {}
                author = item.get("author") or {}
                if author.get("sec_uid"):
                    profile.update({
                        "sec_uid": author.get("sec_uid"),
                        "nickname": author.get("nickname"),
                        "unique_id": author.get("unique_id"),
                        "signature": author.get("signature"),
                    })
                    save_post(item)
            elif "/aweme/v1/web/aweme/post/" in u:
                data = resp.json()
                state["post_responses"] += 1
                for item in data.get("aweme_list") or []:
                    save_post(item)
                state["has_more"] = data.get("has_more")
                state["cursor"] = data.get("max_cursor")
                print(
                    "POST_PAGE",
                    state["post_responses"],
                    "items", len(data.get("aweme_list") or []),
                    "total", len(posts),
                    "has_more", state["has_more"],
                    flush=True,
                )
        except Exception as e:
            print("RESPONSE_PARSE_ERROR", type(e).__name__, str(e)[:300], flush=True)

    page.on("response", on_response)
    print("OPEN_SEED", SEED, flush=True)
    page.goto(SEED, wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(12000)

    if not profile.get("sec_uid"):
        # DOM fallback: use the first actual /user/ link near the author area.
        for a in page.locator('a[href*="/user/"]').all():
            try:
                href = a.get_attribute("href") or ""
                if "/user/" in href:
                    sec = href.split("/user/", 1)[1].split("?", 1)[0].split("/", 1)[0]
                    if sec.startswith("MS4wLj"):
                        profile["sec_uid"] = sec
                        profile["nickname"] = (a.inner_text() or "").strip()
                        break
            except Exception:
                pass

    if not profile.get("sec_uid"):
        print("PAGE_TITLE", page.title(), flush=True)
        print("PAGE_URL", page.url, flush=True)
        page.screenshot(path=str(OUT / "seed-failure.png"), full_page=False)
        raise SystemExit("无法从种子视频获得作者 sec_uid；可能遇到登录/验证码/风控")

    if "陈小树" not in (profile.get("nickname") or ""):
        print("AUTHOR_WARNING", profile, flush=True)

    profile_url = f'https://www.douyin.com/user/{profile["sec_uid"]}'
    print("AUTHOR", json.dumps(profile, ensure_ascii=False), flush=True)
    print("OPEN_PROFILE", profile_url, flush=True)
    page.goto(profile_url, wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(12000)

    stagnant = 0
    last_total = len(posts)
    for i in range(240):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1500)
        now = len(posts)
        if state["has_more"] in (0, False):
            print("REACHED_LAST_PAGE", flush=True)
            break
        if now == last_total:
            stagnant += 1
        else:
            stagnant = 0
            last_total = now
        if stagnant >= 12:
            print("STAGNANT_STOP", i, "total", now, "has_more", state["has_more"], flush=True)
            break
    page.wait_for_timeout(3000)
    browser.close()

profile["profile_url"] = f'https://www.douyin.com/user/{profile.get("sec_uid","")}'
profile["captured_post_count"] = len(posts)
profile["has_more_at_end"] = state["has_more"]
profile["post_responses"] = state["post_responses"]
(OUT / "profile.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
with (OUT / "manifest.jsonl").open("w", encoding="utf-8") as f:
    for item in sorted(posts.values(), key=lambda x: (x.get("create_time") or 0, x["content_id"]), reverse=True):
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print("FINAL", json.dumps(profile, ensure_ascii=False), flush=True)
if not posts:
    raise SystemExit("没有捕获到任何作品")
if state["has_more"] not in (0, False):
    raise SystemExit(f"未确认到最后一页：captured={len(posts)} has_more={state['has_more']!r}")
