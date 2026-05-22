# 微信公众号草稿箱 API 参考

> 本文是 ni-draft 调微信接口的参考。覆盖：access_token 机制、草稿箱 API 端点、错误码全表、配置说明。

---

## 1. 配置

脚本按以下顺序读取凭证，环境变量优先：

1. 环境变量 `WECHAT_APPID` / `WECHAT_SECRET`
2. 配置文件 `~/.config/ni-skill/config.yaml`：

```yaml
wechat:
  appid: wx_xxxxxxxx
  secret: xxxxxxxxxxxxxxxx
  token_cache_path: ~/.cache/ni-skill/wechat_token.json   # 可选，默认即此路径
```

凭证从公众号后台「设置与开发 → 基本配置」获取。注意：调 API 的服务器 IP 需加进后台的「IP 白名单」，否则报 40164。

---

## 2. access_token

**端点**：`GET https://api.weixin.qq.com/cgi-bin/token`

**参数**：`grant_type=client_credential` + `appid` + `secret`

**返回**：`{"access_token": "xxx", "expires_in": 7200}`

**缓存策略**（`token_cache.py` 实现）：
- 写入 `~/.cache/ni-skill/wechat_token.json`，格式 `{"token": "xxx", "expires_at": <unix 秒>}`。
- 微信给 `expires_in=7200`，我们存 `now + 7000`（留 200 秒 buffer）。
- 后续调用先读缓存，未过期直接复用，不重复拿。
- 文件锁防并发竞态：Windows 用 `msvcrt.locking`，Unix 用 `fcntl.flock`。
- 收到 40001 → 删缓存、重拿、重试 1 次。

---

## 3. 草稿箱 API

**端点**：`POST https://api.weixin.qq.com/cgi-bin/draft/add?access_token=xxx`

**请求体**：

```json
{
  "articles": [
    {
      "title": "文章标题",
      "author": "泥巴猪",
      "digest": "文章摘要",
      "content": "<完整内联 CSS HTML>",
      "thumb_media_id": "封面素材 id",
      "content_source_url": "",
      "need_open_comment": 0,
      "only_fans_can_comment": 0
    }
  ]
}
```

**成功返回**：`{"media_id": "草稿的 media_id"}`

**字段约束**：
- `title` ≤ 64 字节
- `digest` ≤ 120 字节（建议留余量，截断到 110）
- `content` ≤ 20000 字
- `thumb_media_id`：微信对普通图文要求此字段。用户决策为「封面占位」，脚本默认尝试不带；若被拒，需用户提供一个一次性占位 media_id（后台素材库任意图片）。

**封面占位说明**：微信草稿箱接口通常强制 `thumb_media_id`。若不带导致建草稿失败，错误信息会指向缺素材。此时引导用户去公众号后台素材库传一张图，拿 media_id，作为占位长期复用，发布前在草稿箱替换为正式封面。

---

## 4. 错误码表

| errcode | 含义 | ni-draft 处理 |
|---------|------|--------------|
| 0 | 成功 | 写 draft-meta.yaml |
| 40001 | access_token 失效 | 删缓存 → 重拿 → 重试 1 次 |
| 40164 | 调用 IP 不在白名单 | 转人话：提示去后台加 IP 白名单，停止 |
| 41059 / 缺 thumb_media_id | 缺封面素材 | 转人话：引导用户提供占位 media_id |
| 45004 | digest 超长 | 截断 digest 到 110 字节 → 重试 1 次 |
| 45009 | 接口调用频率超限 | 转人话：提示稍后再试，降级本地 HTML |
| 40007 | media_id 不合法 | 转人话：封面 media_id 无效，让用户重新提供 |
| 其他 | 未知错误 | 转人话 + 降级本地 HTML + 给手动上传指引 |

**转人话原则**：绝不把 errcode 数字直接甩给用户。每个错误都翻译成「发生了什么 + 你该做什么」。

---

## 5. 降级：本地 HTML

推送失败（40001 / 45004 自动重试之外的错误），脚本：

1. 把转好的 HTML 写到文章同目录的 `local-preview.html`。
2. 输出指引：「打开 local-preview.html，全选内容，粘贴到公众号后台编辑器」。
3. 在 `draft-meta.yaml` 标 `degraded: true` 和失败原因。

降级是兜底，不是失败——用户照指引仍能发出文章。
