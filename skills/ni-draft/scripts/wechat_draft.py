"""ni-draft CLI 主入口。

把排版好的 markdown 文章推送到微信公众号草稿箱。

用法：
    python wechat_draft.py create \\
        --article path/to/formatted.md \\
        --title "标题" --digest "摘要" \\
        --output path/to/draft-meta.yaml \\
        [--cover-media-id xxx] [--author "泥巴猪"]

接口形态参考微信草稿箱 API：POST /cgi-bin/draft/add，
响应 {errcode, errmsg, media_id}。错误码见 references/wechat-api.md。
"""

import argparse
import datetime
import json
import os
import sys

import requests
import yaml

# 同目录模块（脚本直接运行时，其所在目录自动进 sys.path）
import token_cache
from md_to_wechat_html import convert

DRAFT_URL = "https://api.weixin.qq.com/cgi-bin/draft/add"
TITLE_LIMIT = 64       # 字节
DIGEST_LIMIT = 120     # 字节
DIGEST_SAFE = 110      # 45004 重试时截断到此

# errcode -> 给用户的人话
ERR_HINTS = {
    40001: "微信凭证过期了。",
    40007: "封面素材 id 不合法，可能填错或已被删除。",
    40164: "当前机器的 IP 不在公众号后台的 IP 白名单里，去后台「基本配置」加上。",
    41059: "微信这个接口要求带一个封面素材 id。",
    45002: "文章正文超过了微信的长度限制，需要精简。",
    45003: "标题太长了，需要缩短。",
    45004: "摘要太长了。",
    45005: "正文里有个链接字段不合法或超长。",
    45009: "接口调用太频繁，被微信限流了，过会儿再试。",
}


def _bytelen(text):
    return len(text.encode("utf-8"))


def _truncate_bytes(text, limit):
    raw = text.encode("utf-8")
    if len(raw) <= limit:
        return text
    return raw[:limit].decode("utf-8", errors="ignore")


def load_config():
    """读凭证，环境变量优先，兜底配置文件。返回 (appid, secret, cache_path)。"""
    appid = os.environ.get("WECHAT_APPID")
    secret = os.environ.get("WECHAT_SECRET")
    cache_path = token_cache.DEFAULT_CACHE
    cfg_path = os.path.expanduser("~/.config/ni-skill/config.yaml")
    if (not appid or not secret) and os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh) or {}
        wx = cfg.get("wechat", {}) or {}
        appid = appid or wx.get("appid")
        secret = secret or wx.get("secret")
        if wx.get("token_cache_path"):
            cache_path = os.path.expanduser(wx["token_cache_path"])
    return appid, secret, cache_path


def post_draft(token, article):
    """调微信草稿箱接口，返回解析后的 JSON dict。"""
    body = json.dumps({"articles": [article]}, ensure_ascii=False).encode("utf-8")
    resp = requests.post(
        DRAFT_URL,
        params={"access_token": token},
        data=body,
        headers={"Content-Type": "application/json"},
        timeout=15,
    )
    return resp.json()


def _write_meta(output_path, data):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, allow_unicode=True, sort_keys=False)


def _degrade(article_path, html, output_path, reason):
    """降级：输出本地 HTML + 写降级版 draft-meta。"""
    local_html = os.path.join(
        os.path.dirname(os.path.abspath(article_path)), "local-preview.html"
    )
    with open(local_html, "w", encoding="utf-8") as fh:
        fh.write(f"<!DOCTYPE html><html><head><meta charset=\"utf-8\">"
                 f"</head><body>{html}</body></html>")
    _write_meta(output_path, {
        "status": "degraded",
        "degraded": True,
        "reason": reason,
        "local_html": local_html,
        "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
    })
    print(f"[ni-draft] 推送没成上，原因：{reason}")
    print(f"[ni-draft] 我把转好的文章存成了本地文件：{local_html}")
    print("[ni-draft] 你可以打开它、全选内容，粘贴进公众号后台编辑器，照样能发。")
    return 1


def cmd_create(args):
    appid, secret, cache_path = load_config()
    if not appid or not secret:
        print("[ni-draft] 还没配微信凭证。设环境变量 WECHAT_APPID / WECHAT_SECRET，")
        print("           或在 ~/.config/ni-skill/config.yaml 里填 wechat.appid / wechat.secret。")
        return 1

    if not os.path.exists(args.article):
        print(f"[ni-draft] 找不到文章文件：{args.article}")
        return 1
    if _bytelen(args.title) > TITLE_LIMIT:
        print(f"[ni-draft] 标题太长了（{_bytelen(args.title)} 字节，上限 {TITLE_LIMIT}），先缩短。")
        return 1

    with open(args.article, "r", encoding="utf-8") as fh:
        md_text = fh.read()
    html = convert(md_text)

    digest = args.digest
    if _bytelen(digest) > DIGEST_LIMIT:
        digest = _truncate_bytes(digest, DIGEST_SAFE)
        print(f"[ni-draft] 摘要有点长，我先帮你截短到 {_bytelen(digest)} 字节。")

    article = {
        "title": args.title,
        "author": args.author or "",
        "digest": digest,
        "content": html,
        "content_source_url": "",
        "thumb_media_id": args.cover_media_id or "",
        "need_open_comment": 0,
        "only_fans_can_comment": 0,
    }

    try:
        token = token_cache.get_token(appid, secret, cache_path)
        result = post_draft(token, article)
    except (requests.RequestException, RuntimeError) as exc:
        return _degrade(args.article, html, args.output, f"网络或凭证问题：{exc}")

    errcode = result.get("errcode", 0)

    # 40001：凭证失效，换新 token 重试 1 次
    if errcode == 40001:
        print("[ni-draft] 凭证过期了，我换张新的重试一下。")
        token_cache.invalidate(cache_path)
        try:
            token = token_cache.get_token(appid, secret, cache_path, force_refresh=True)
            result = post_draft(token, article)
        except (requests.RequestException, RuntimeError) as exc:
            return _degrade(args.article, html, args.output, f"重拿凭证失败：{exc}")
        errcode = result.get("errcode", 0)

    # 45004：摘要超长，截断重试 1 次
    if errcode == 45004:
        print("[ni-draft] 微信嫌摘要太长，我再截短一点重试。")
        article["digest"] = _truncate_bytes(digest, DIGEST_SAFE)
        result = post_draft(token, article)
        errcode = result.get("errcode", 0)

    if errcode == 0 and result.get("media_id"):
        _write_meta(args.output, {
            "status": "success",
            "degraded": False,
            "draft_media_id": result["media_id"],
            "title": args.title,
            "cover_media_id": args.cover_media_id or "",
            "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
        })
        print("[ni-draft] 推上去了，草稿在你公众号后台躺着呢。")
        if not args.cover_media_id:
            print("[ni-draft] 封面是空的，发布前记得自己在草稿箱里设一张。")
        else:
            print("[ni-draft] 封面用的是你给的占位图，发布前可以在草稿箱换成正式封面。")
        return 0

    # 失败：转人话 + 降级
    errmsg = result.get("errmsg", "")
    hint = ERR_HINTS.get(errcode, "")
    cover_missing = (not args.cover_media_id) and (
        errcode in (40007, 41059) or "media" in errmsg.lower() or "thumb" in errmsg.lower()
    )
    if cover_missing:
        reason = ("微信这个接口必须带一个封面素材 id。你去公众号后台素材库随便传一张图，"
                  "拿到它的 media_id，下次用 --cover-media-id 传给我，以后一直复用就行。")
    else:
        reason = hint or f"微信返回了一个我没专门处理的错误（errmsg：{errmsg}）。"
    return _degrade(args.article, html, args.output, reason)


def main():
    parser = argparse.ArgumentParser(description="把 markdown 文章推送到微信草稿箱")
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create", help="创建草稿")
    p_create.add_argument("--article", required=True, help="排版后的 markdown 文件路径")
    p_create.add_argument("--title", required=True, help="文章标题")
    p_create.add_argument("--digest", required=True, help="文章摘要")
    p_create.add_argument("--output", required=True, help="draft-meta.yaml 输出路径")
    p_create.add_argument("--cover-media-id", default="", help="封面素材 id（可选）")
    p_create.add_argument("--author", default="", help="作者名（可选）")

    args = parser.parse_args()
    if args.command == "create":
        return cmd_create(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
