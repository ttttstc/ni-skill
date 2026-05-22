"""ni-draft 离线冒烟测试：用模拟响应验证成功 / 重试 / 降级分支。

不调真实微信 API。运行：python ni-draft/tests/smoke_test.py
"""

import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

import wechat_draft as w  # noqa: E402

MOCKS = json.load(
    open(os.path.join(HERE, "fixtures", "mock-wechat-response.json"), encoding="utf-8")
)
ARTICLE = os.path.join(HERE, "fixtures", "sample-article.md")


class Args:
    def __init__(self, output, cover=""):
        self.article = ARTICLE
        self.title = "测试标题"
        self.digest = "测试摘要"
        self.output = output
        self.cover_media_id = cover
        self.author = "泥巴猪"


def _setup(monkey_post):
    """注入桩：跳过真实配置和 token，替换 post_draft。"""
    w.load_config = lambda: ("appid", "secret", os.path.join(tempfile.gettempdir(), "tok.json"))
    w.token_cache.get_token = lambda *a, **k: "FAKE_TOKEN"
    w.token_cache.invalidate = lambda *a, **k: None
    w.post_draft = monkey_post


def case_success():
    _setup(lambda token, article: MOCKS["success"])
    out = os.path.join(tempfile.gettempdir(), "meta_success.yaml")
    rc = w.cmd_create(Args(out))
    meta = open(out, encoding="utf-8").read()
    assert rc == 0, "成功场景应返回 0"
    assert "status: success" in meta and "MOCK_DRAFT_MEDIA_ID" in meta
    print("[PASS] 成功路径：rc=0，draft-meta 写入 draft_media_id")


def case_token_retry():
    calls = {"n": 0}

    def post(token, article):
        calls["n"] += 1
        return MOCKS["token_expired"] if calls["n"] == 1 else MOCKS["success"]

    _setup(post)
    out = os.path.join(tempfile.gettempdir(), "meta_retry.yaml")
    rc = w.cmd_create(Args(out))
    assert rc == 0 and calls["n"] == 2, "40001 应触发一次重试后成功"
    print("[PASS] 40001 凭证失效：换 token 重试 1 次后成功")


def case_digest_retry():
    calls = {"n": 0}

    def post(token, article):
        calls["n"] += 1
        return MOCKS["digest_too_long"]

    _setup(post)
    out = os.path.join(tempfile.gettempdir(), "meta_digest.yaml")
    rc = w.cmd_create(Args(out))
    meta = open(out, encoding="utf-8").read()
    assert rc == 1 and calls["n"] == 2, "45004 应截断重试 1 次"
    assert "degraded: true" in meta, "重试仍失败应降级"
    print("[PASS] 45004 摘要超长：截断重试 1 次，仍失败则降级")


def case_cover_missing_degrade():
    _setup(lambda token, article: MOCKS["cover_missing"])
    out = os.path.join(tempfile.gettempdir(), "meta_cover.yaml")
    rc = w.cmd_create(Args(out, cover=""))
    meta = open(out, encoding="utf-8").read()
    local_html = os.path.join(os.path.dirname(ARTICLE), "local-preview.html")
    assert rc == 1 and "degraded: true" in meta
    assert "封面素材 id" in meta, "缺封面应给占位 media_id 指引"
    assert os.path.exists(local_html), "降级应产出本地 HTML"
    os.remove(local_html)
    print("[PASS] 缺封面：降级到本地 HTML，并给出占位 media_id 指引")


if __name__ == "__main__":
    case_success()
    case_token_retry()
    case_digest_retry()
    case_cover_missing_degrade()
    print("\n全部冒烟测试通过 ✓")
