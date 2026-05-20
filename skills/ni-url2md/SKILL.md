---
name: ni-url2md
description: |
  泥巴猪「低卧扑食」公众号的网页抓取 skill。用 Chrome 真实浏览器把任意 URL 抓成干净的 Markdown，带元数据。当用户说「把这个链接存下来」「这篇文章抓成 md」「保存这个网页」「这个博客我想读」「这个文档转成 markdown」「网页转 md」时触发。也适用于用户丢一个链接、说「帮我把这个弄下来当素材」的场景。支持自动捕获和等待用户登录两种模式。覆盖任何能用浏览器打开的页面（包括 SPA、需 JS 渲染、需登录）。不适用于已经是 markdown 的本地文件、二进制/媒体下载、需要绕反爬的场景。
---

# ni-url2md — 网页抓取 Markdown

> 这是泥巴猪「低卧扑食」公众号创作套件里的网页抓取 skill。它把任何 URL 抓成干净的 Markdown，给后续 ni-research / ni-writer 当素材。

你现在的任务是把一个 URL 抓成 Markdown：用真实 Chrome 渲染、清除导航/广告/侧栏、提取正文 + 元数据。

## 这个 skill 在管线里的位置

**独立可用**：用户丢链接 → 抓成 md → 用户拿去读、存档、引用。
**给 ni-research 喂料**：workflow 模式下，抓下来的 md 进 `research-sources/`，ni-research 从里面抠主流观点和具名素材。

## 原则

- **真实优先**：抓下来的内容必须挂回真实 URL 和真实捕获时间。不要替用户「整理」「润色」原文意思，只做清理和转格式。
- **活人在场**：脚本本身的 CLI 输出可以英文（这是 baoyu 的原版风格，保留），但你在和用户对话时用第一人称中文。
  - 反例（禁止）：「抓取完成，输出位置：xxx.md。」
  - 正例（推荐）：「抓下来了，存在 xxx.md。标题是『……』，作者那栏空着——这站可能没在 meta 里写作者，你看一眼。」
- **四层自检**：交付前过 L1-L4（见下方「验收」）。
- **降级而不放弃**：Chrome / Bun 缺失、页面抓不到时给清晰的人话错误 + 安装/排查指引，不甩 stack trace。

## 技术栈与脚本来源

**技术栈**：TypeScript + Bun + Chrome DevTools Protocol（CDP），全 JS 渲染，能跑现代 SPA。

**脚本来源**：`scripts/` 下 5 个 .ts 文件直接复用自 `baoyu-url-to-markdown`（用户本地已有的 skill），未做改动。SKILL.md 是 ni 风格新写的。

## 工程结构

```
ni-url2md/
├── SKILL.md
└── scripts/
    ├── main.ts                  CLI 入口 + 主流程
    ├── cdp.ts                   Chrome 启动 + CDP 连接 + 网络空闲/滚动
    ├── html-to-markdown.ts      浏览器内清理脚本 + HTML→MD 转换
    ├── constants.ts             超时/滚动等常量
    └── paths.ts                 数据目录 / Chrome 配置目录解析
```

## 前置依赖

| 依赖 | 说明 |
|------|------|
| Bun | 通过 `npx -y bun` 临时拉取，无需全局安装；首次会慢 |
| Chrome | 本地装了 Chrome 即可。装在非默认位置时设 `URL_CHROME_PATH` |

第一次跑会比较慢（拉 Bun + 启动 Chrome）。后续命中缓存就快了。

> **关于 `${SKILL_DIR}`**：本 SKILL.md 所在的目录。Claude Code 加载 skill 时自动解析；用户手动跑命令时，把它替换成 skill 的实际安装路径即可（例如 `~/.claude/skills/ni-skill/skills/ni-url2md` 或 `git clone` 下来的对应位置）。

## 使用方法

### 自动模式（默认）

适合公开页：博客、技术文档、新闻、产品页。脚本等页面加载 + 网络空闲 + 自动滚动触发懒加载，然后抓。

```bash
npx -y bun ${SKILL_DIR}/scripts/main.ts <url>
npx -y bun ${SKILL_DIR}/scripts/main.ts <url> -o my-article.md
```

### 等待模式（`--wait`）

适合需登录 / 付费墙 / 懒加载严重的页面。脚本打开浏览器，你登录或滚到位后，**回车**触发抓取。

```bash
npx -y bun ${SKILL_DIR}/scripts/main.ts <url> --wait
```

### 超时

```bash
npx -y bun ${SKILL_DIR}/scripts/main.ts <url> --timeout 60000
```

## CLI 参数

| 参数 | 说明 |
|------|------|
| `<url>` | 要抓的 URL（必填） |
| `-o <path>` | 输出文件路径（不给则自动按 `domain/slug.md` 生成） |
| `--wait` | 等待用户回车再抓 |
| `--timeout <ms>` | 页面加载超时，默认 30000 |

## 环境变量

| 变量 | 用途 |
|------|------|
| `URL_CHROME_PATH` | 自定义 Chrome 可执行文件路径（Chrome 不在默认位置时用） |
| `URL_DATA_DIR` | 自动输出的数据目录根（不给 `-o` 时用），默认 `./url-to-markdown/` |
| `URL_CHROME_PROFILE_DIR` | Chrome 用户配置目录（保留 cookies / 登录态） |

> 这套变量沿用 baoyu 原版命名，方便和 baoyu-url-to-markdown 共用配置。

## 输出格式

每个抓下来的 markdown 文件带 YAML frontmatter 元数据 + 正文：

```markdown
---
url: https://...
title: 文章标题
description: 摘要（来自 meta description）
author: 作者（如果页面有）
published: 发布日期（如果页面有）
captured_at: 2026-05-20T10:00:00.000Z
---

# 文章标题

正文 markdown ...
```

`captured_at` 永远有；`title` 通常有；`description / author / published` 看页面 meta 是否给。

## 接入 ni-research

把抓下来的 md 当作 ni-research 的 **真实素材**：

- 单条链接 → 一个 md 文件 → ni-research 在「素材库」里引用，标 ✅（有具名来源）。
- 多条链接 → 多个 md 文件 → ni-research 做竞品二分扫描（已被说过 / 未被覆盖）。

workflow 模式下，把多个抓取产物放进 `drafts/{article-name}/research-sources/`，ni-research 启动时优先读这个目录。

## 硬规则

- **不改写原文。** 只清理（去导航/广告/侧栏）+ 转格式（HTML→MD），不删段落、不归纳、不重写。
- **元数据必须挂回真实 URL 和捕获时间。** 这是 真实优先的落点：让作者引用时能溯源。
- **抓取失败不要静默成功。** 错误就报错，降级也要显式标注。

## 验收（四层自检）

- **L1 输入合法**：URL 是有效 http(s) URL；Chrome 和 Bun 就绪。
- **L2 输出对齐**：md 文件含 frontmatter（至少 url、title、captured_at），正文非空。
- **L3 内容达标**：正文是文章本体，不是导航和广告残渣；段落、标题、链接、代码块结构合理。
- **L4 反 AI 自查**：通读一遍开头，问自己「这看起来是原文，还是被我『润色』过」。润色过的回炉——这个 skill 只清理、不改写。

## 降级

| 场景 | 降级路径 |
|------|---------|
| Chrome 找不到 | 转人话告诉用户：装 Chrome 或设 `URL_CHROME_PATH` 指向已有的 Chrome。 |
| Bun 拉不下来 | 提示网络问题，建议手动 `npm i -g bun` 后再跑。 |
| 页面超时 | 提示用 `--timeout 60000` 加长，或用 `--wait` 手动控时。 |
| 抓到内容明显残缺 | 切 `--wait` 模式手动等页面完整加载完再回车。 |
| 需登录 | 走 `--wait` 模式；登录态可以靠 `URL_CHROME_PROFILE_DIR` 持久化，下次复用。 |
| 反爬 / 403 / 验证码 | 不硬突破。告诉用户「这站有反爬，我抓不动，建议手动复制」，不假装抓到了。 |

降级显式标注。

## 已知限制

- 只输出 markdown，不下载图片（图片在 md 里是原图 URL 链接，发到公众号还是要单独传素材）。
- 不处理付费墙绕过、不处理验证码识别——这些场景请用 `--wait` 手动操作。
- 中文 slug 生成可能不理想，建议用 `-o` 显式指定输出文件名。

## 参考

baoyu-url-to-markdown 是本 skill 的脚本源。如果你直接装了 baoyu 的 skill，两个 skill 行为完全一致——ni-url2md 提供的是 ni-skill 套件层面的对接（接入 ni-research、原则风格、与套件其他 skill 协同）。
