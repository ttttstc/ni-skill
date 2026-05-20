---
name: ni-draft
description: |
  泥巴猪「低卧扑食」公众号的草稿推送 skill。把排版好的文章推送到微信公众号草稿箱。当用户说「推到草稿箱」「发草稿」「推送公众号」「上传到微信」「发布这篇」「推到公众号后台」时触发。也适用于用户给一篇排版后的 markdown、说「弄到公众号去」的场景。不适用于还没写完 / 没排版的文章、推送到非微信平台、需要正文配图上传的场景（P0 不支持正文图片）。
---

# ni-draft — 草稿箱推送

> 这是泥巴猪「低卧扑食」公众号创作套件里的发布 skill。它把排版好的文章推送到微信公众号草稿箱。

你现在的任务是把一篇 markdown 文章变成微信草稿。推送靠一个内嵌的 Python 脚本完成，你负责调它、读懂它的输出、把结果用人话讲给用户。

## 这个 skill 在管线里的位置

ni-formatter 产出 `formatted.md`（带 `:::xxx` 排版注释），ni-draft 把它转成微信兼容 HTML，调微信草稿箱 API 创建草稿。创建成功后，用户在公众号后台看到草稿，**自己设封面、自己点发布**。

## P0 范围

本版本只做文章推送，**不做**正文配图上传、不做封面生成。

- 封面：用户自己在草稿箱里设。`--cover-media-id` 参数可选。
- 正文图片：P0 不处理。文章里如有本地图片，跳过并提示用户手动补。

## 原则

- **不谎报推送结果**：失败就说失败，绝不打「已提交」。
- **错误转人话**：不甩 errcode 数字，翻译成「发生了什么 + 你该做什么」。
- **失败必降级**：推送失败 → 本地 HTML + 手动上传指引，不只抛个错。
- **输出前验证**：title 字节数 / digest 字节数 / 配置就绪 / 5 模块渲染对。

## 技术栈

- Python 3.10+，纯内嵌脚本，零外部二进制依赖。
- 三个 PyPI 包：`requests` / `markdown` / `pyyaml`（见 `requirements.txt`）。
- 首次使用前装依赖：`pip install -r ${SKILL_DIR}/requirements.txt`。

> **关于 `${SKILL_DIR}`**：本 SKILL.md 所在的目录。Claude Code 加载 skill 时自动解析；用户手动跑命令时，把它替换成 skill 的实际安装路径即可（例如 `~/.claude/skills/ni-skill/skills/ni-draft` 或 `git clone` 下来的对应位置）。

## 工程结构

```
ni-draft/
├── SKILL.md
├── requirements.txt
├── references/
│   ├── wechat-api.md          错误码、API 端点、配置说明
│   └── html-style-guide.md    微信兼容 HTML 的内联 CSS 约定
├── scripts/
│   ├── wechat_draft.py        CLI 主入口
│   ├── token_cache.py         access_token 缓存
│   └── md_to_wechat_html.py   markdown → 内联 CSS HTML
└── tests/
    └── fixtures/              离线测试样例
```

## 配置

脚本读两处配置，环境变量优先：

1. 环境变量：`WECHAT_APPID`、`WECHAT_SECRET`
2. 兜底配置文件：`~/.config/ni-skill/config.yaml`

```yaml
wechat:
  appid: wx_xxxxxxxx
  secret: xxxxxxxxxxxxxxxx
```

用户没配过，第一次用时引导他配，别让他对着报错猜。

## 怎么用

### 第一步：确认输入

- 文章文件存在（`formatted.md` 或任意排版后的 markdown）
- 标题（≤ 64 字节）、摘要 digest（≤ 120 字节）
- 封面 media_id —— 可选，不给就让用户回头在草稿箱设

### 第二步：调脚本

```bash
python ${SKILL_DIR}/scripts/wechat_draft.py create \
  --article path/to/formatted.md \
  --title "文章标题" \
  --digest "文章摘要" \
  --output path/to/draft-meta.yaml
```

可选参数 `--cover-media-id xxx`、`--author "泥巴猪"`。

### 第三步：读懂结果，转人话

- 成功 → 脚本写出 `draft-meta.yaml`（含返回的 draft media_id）。告诉用户「推上去了，去后台草稿箱看，记得设个封面再发」。
- 失败 → 脚本会自己降级出本地 HTML。把降级情况和原因用人话讲清楚。

## 封面处理（用户决策：占位）

用户的选择是封面先占位、自己在草稿箱编辑。所以：

- 默认不传 `--cover-media-id`，让脚本尝试无封面建草稿。
- 微信草稿箱 API 对 `thumb_media_id` 可能强制要求。如果脚本报「缺封面素材」类错误，告诉用户：「微信这个接口必须带个封面素材 id。你去公众号后台素材库随便传一张图，拿到它的 media_id，给我一次就行，以后复用。」
- 成功建草稿后，提醒用户：封面是占位的，发布前自己在草稿箱换成正式封面。

## markdown → HTML 转换要点

`md_to_wechat_html.py` 负责。关键约定（详见 `references/html-style-guide.md`）：

- 全部 CSS 内联到 `style="..."`（公众号不支持 `<style>` 和 `<link>`）。
- 不引入任何 JS。
- ni-formatter 的 5 个 `:::xxx` 注释在这一步渲染成对应 HTML 结构：
  - `:::part` → 分隔线 + 标题强调
  - `:::callout` → 背景色块（warning / info / tip 三色）
  - `:::quote` → 缩进引用 + 左侧色条
  - `:::steps` → 编号列表（每步开头加粗）
  - `:::verdict` → 加粗居中块（视觉锚点）

## 错误处理

脚本处理常见错误码，你负责转人话（详见 `references/wechat-api.md`）：

- **40001 凭证失效** → 脚本自动删缓存、重拿 token、重试 1 次。对用户说「凭证过期，我换了张新的，成了」。
- **45004 摘要超长** → 脚本自动把 digest 截到 110 字节、重试 1 次。对用户说「摘要太长我帮你截短了一点」。
- **其他错误** → 脚本降级到本地 HTML。对用户说清楚是什么问题、本地文件在哪、怎么手动传。

绝不把原始 errcode 数字甩给用户。

## 验收

- **输入合法**：文章文件存在、title ≤ 64 字节、digest ≤ 120 字节、Python 环境和依赖就绪、配置可读。
- **输出对齐**：成功时 `draft-meta.yaml` 写出且含 draft media_id。
- **渲染正确**：HTML 在草稿箱预览不变形，5 个排版模块都正常显示。
- **交付前自查**：给用户的每句话都是人话，没有泄露 errcode、没有谎报结果。

## 降级

| 场景 | 降级路径 |
|------|---------|
| 推送失败（非 40001 / 45004） | 脚本输出 `local-preview.html` + 手动上传指引，对用户显式说明这是降级结果 |
| Python 依赖没装 | 引导用户 `pip install -r ${SKILL_DIR}/requirements.txt`，不硬跑 |
| 配置缺失 | 引导用户填 `~/.config/ni-skill/config.yaml` 或设环境变量 |
| 正文有本地图片 | P0 不传图，跳过并提示用户在草稿箱手动补图 |

降级必须显式标注，让用户知道这是降级，不是正常成功。

## 参考资料

- **`references/wechat-api.md`** — 微信草稿箱 API 端点、错误码全表、配置示例、access_token 机制。
- **`references/html-style-guide.md`** — 微信兼容 HTML 的内联 CSS 规范，含 5 个排版模块的样式定义。
