#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, time
from pathlib import Path
import requests

BASE = "http://127.0.0.1:8000"
AUTHOR_ID = "MS4wLjABAAAAuf_LJbB5-Ax1mK7A-haX99dBuPsiU5KvqVG183M-xEZjesCpObHPdYe6pdC_XyoG"
RETRYABLE = {
    "UPSTREAM_RISK_CONTROL", "IDENTITY_POOL_EXHAUSTED",
    "ENDPOINT_CIRCUIT_OPEN", "RATE_LIMITED", "QUEUE_FULL",
    "SIGNING_FAILED", "INTERNAL",
}

class DtkError(RuntimeError):
    def __init__(self, err):
        self.err = err or {}
        super().__init__(f"{self.err.get('code')}: {self.err.get('message')}")


def unwrap(resp):
    body = resp.json()
    if not body.get("success"):
        raise DtkError(body.get("error"))
    return body["data"]


def poll_task(s, task_id, timeout=180):
    end = time.time() + timeout
    while time.time() < end:
        row = unwrap(s.get(BASE + f"/api/v1/tasks/{task_id}", timeout=30))
        if row["state"] == "done":
            return row.get("data")
        if row["state"] == "failed":
            raise DtkError(row.get("error"))
        time.sleep(2)
    raise TimeoutError(task_id)


def page_once(s, cursor):
    params = {
        "sec_user_id": AUTHOR_ID,
        "count": 20,
        "wait": 30,
        "include_raw": "false",
    }
    if cursor:
        params["cursor"] = cursor
    resp = s.get(BASE + "/api/v1/douyin/user/posts", params=params, timeout=45)
    data = unwrap(resp)
    if resp.status_code == 200:
        return data
    return poll_task(s, data["task_id"], 150)


def page_with_retry(s, cursor, page_no):
    last = None
    for attempt in range(1, 11):
        try:
            return page_once(s, cursor)
        except DtkError as exc:
            last = exc
            code = exc.err.get("code")
            if code not in RETRYABLE and exc.err.get("retryable") is not True:
                raise
            delay = int(exc.err.get("retry_after") or min(20 * attempt, 90))
            print(json.dumps({
                "event": "retry",
                "page": page_no,
                "attempt": attempt,
                "code": code,
                "delay": delay,
            }, ensure_ascii=False), flush=True)
            time.sleep(delay)
    raise last or RuntimeError("page retries exhausted")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    token = os.environ["DTK_SETUP_TOKEN"]
    s = requests.Session()
    username = "ni_work_tutor"
    password = "Tmp-" + os.urandom(18).hex()

    unwrap(s.post(BASE + "/api/setup/init",
        json={"token": token, "username": username, "password": password}, timeout=30))
    unwrap(s.post(BASE + "/api/v1/auth/login",
        json={"username": username, "password": password}, timeout=30))

    minted = unwrap(s.post(BASE + "/api/v1/admin/identities/mint",
        json={"platform": "douyin", "count": 3}, timeout=30))
    task_ids = list(minted["task_ids"])
    mint_states = {}
    for tid in task_ids:
        try:
            poll_task(s, tid, 240)
            mint_states[tid] = "done"
        except Exception as exc:
            mint_states[tid] = f"failed:{type(exc).__name__}"
            raise

    # Let cookies/fingerprints settle before the first sensitive list call.
    time.sleep(10)

    items_by_id = {}
    pages = []
    cursor = None
    seen = set()
    terminal = False
    for page_no in range(1, 101):
        page = page_with_retry(s, cursor, page_no)
        items = page.get("items") or []
        for item in items:
            cid = str(item.get("content_id") or "")
            if cid:
                items_by_id[cid] = item
        nxt = page.get("cursor")
        more = bool(page.get("has_more"))
        stat = {
            "page": page_no,
            "items": len(items),
            "total_unique": len(items_by_id),
            "has_more": more,
            "has_cursor": bool(nxt),
        }
        pages.append(stat)
        print(json.dumps(stat, ensure_ascii=False), flush=True)
        if not more:
            terminal = True
            break
        if not nxt or nxt in seen:
            raise RuntimeError("cursor stopped before terminal")
        seen.add(nxt)
        cursor = nxt
        time.sleep(20)

    rows = sorted(
        items_by_id.values(),
        key=lambda x: (x.get("created_at") or "", str(x.get("content_id") or "")),
        reverse=True,
    )
    with (out / "posts.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    summary = {
        "author_id": AUTHOR_ID,
        "terminal_page_seen": terminal,
        "page_count": len(pages),
        "total_posts": len(rows),
        "video_posts": sum(1 for x in rows if x.get("kind") == "video"),
        "image_posts": sum(1 for x in rows if x.get("kind") == "image_album"),
        "mint_count": len(task_ids),
        "mint_states": mint_states,
        "pages": pages,
    }
    (out / "enumeration-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not terminal or not rows:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
