# ni-skill

中文 | [English](./README.en.md)

> 面向内容创作、视频转写、陌生领域学习、产品架构基线、首层软件架构决策与审核制 3D 资产生产的技能矩阵。

ni-skill 是一组面向 AI 编程 agent（Codex、Claude Code 及类似运行时）的协同 skill，覆盖素材抓取、视频转写、调研、陌生领域学习、灵魂挖掘、写作、排版、预检、配图、发布、产品架构基线、第一性原则架构决策，以及带人工审核门禁的多视图到 GLB 生产。每个 skill 均可独立使用，内容类 skill 可由 `ni-article-workflow` 编排为完整管线。

---

## 环境要求

- **Codex** / **Claude Code** / 任何能从本地 skills 目录加载 skill 的 AI agent 运行时
- **Python 3.10+** —— `ni-draft` 推送微信草稿、`ni-video2md` 运行本地转写脚本时需要
- **Node.js + Chrome** —— `ni-url2md` 抓取网页时需要
- **Chrome/Edge 或可下载的 Chromium** —— `ni-video2md` 抓取抖音公开媒体流时需要
- **图像生成、浏览器控制与可用的图生 3D 服务** —— `ni-3d-model` 需要；登录状态与免费额度取决于所选服务

各 skill 的具体依赖见对应的 `SKILL.md`。

---

## 安装

按你的运行时挑一条。

### Codex — 本地插件

仓库已包含 Codex 插件清单 `.codex-plugin/plugin.json`。本地开发时，clone 后按你的 Codex 插件工作流安装或软链这个仓库。

如果只需要使用 skills，也可以把 `skills/` 下的子目录复制到 `~/.codex/skills/`。下面这段适合直接交给 AI Agent 执行，会安装当前发布的 ni-skill 集合：

```bash
git clone https://github.com/ttttstc/ni-skill.git
mkdir -p ~/.codex/skills
for skill in \
  ni-url2md ni-research ni-insight ni-writer ni-formatter ni-inspect \
  ni-article-image-gen ni-poster ni-draft ni-article-workflow ni-unknown-first \
  ni-tech-report ni-book-writer ni-3d-model ni-fde-copilot ni-readme-guide \
  ni-design-with-docs ni-video2md think-like-architect
do
  cp -R "ni-skill/skills/$skill" ~/.codex/skills/
done
```

PowerShell：

```powershell
git clone https://github.com/ttttstc/ni-skill.git
New-Item -ItemType Directory -Force $HOME\.codex\skills | Out-Null
$skills = @(
  "ni-url2md", "ni-research", "ni-insight", "ni-writer", "ni-formatter",
  "ni-inspect", "ni-article-image-gen", "ni-poster", "ni-draft", "ni-article-workflow",
  "ni-unknown-first", "ni-tech-report", "ni-book-writer", "ni-3d-model", "ni-fde-copilot", "ni-readme-guide",
  "ni-design-with-docs", "ni-video2md", "think-like-architect"
)
foreach ($skill in $skills) {
  Copy-Item "ni-skill\skills\$skill" "$HOME\.codex\skills\$skill" -Recurse -Force
}
```

只安装 `ni-unknown-first`：

```bash
git clone https://github.com/ttttstc/ni-skill.git
mkdir -p ~/.codex/skills
cp -R ni-skill/skills/ni-unknown-first ~/.codex/skills/
```

PowerShell：

```powershell
git clone https://github.com/ttttstc/ni-skill.git
New-Item -ItemType Directory -Force $HOME\.codex\skills | Out-Null
Copy-Item ni-skill\skills\ni-unknown-first $HOME\.codex\skills\ni-unknown-first -Recurse -Force
```

安装后开启新的 Codex 会话，让 skill 列表重新加载。

### Claude Code — Plugin Marketplace

```
/plugin marketplace add ttttstc/ni-skill
/plugin install ni-skill@ni-skill
```

### 任意运行时 — 让 Agent 代装

向 Codex 或 Claude 说明：

> 帮我安装 github.com/ttttstc/ni-skill 的 skill

只装单个 skill 到 Codex 时可以说：

> 只把 github.com/ttttstc/ni-skill 里的 ni-unknown-first 安装到 ~/.codex/skills

### 手动安装 — 复制到对应 skills 目录

大多数 AI agent 运行时都从 `~/.{agent}/skills/` 加载 skill（如 `~/.codex/skills/`、`~/.claude/skills/`）。clone 仓库后，把 `skills/` 下的子目录复制到你运行时的 skills 目录：

```bash
git clone https://github.com/ttttstc/ni-skill.git
cp -R ni-skill/skills/* ~/.claude/skills/
```

PowerShell：

```powershell
git clone https://github.com/ttttstc/ni-skill.git
Copy-Item ni-skill\skills\* $HOME\.claude\skills\ -Recurse -Force
```

手动安装不支持自动更新：能走运行时专属路径就优先走那条。

---

## Skills

| 阶段 | Skill | 能力 |
|------|-------|------|
| 素材 | [`ni-url2md`](./skills/ni-url2md) | 将任意 URL 抓取为 Markdown，支持 JS 渲染与登录态页面 |
| 视频 | [`ni-video2md`](./skills/ni-video2md) | 将公开视频通过本地 Whisper 转为“全文概括-作者.md”文字稿，不生成 SRT |
| 调研 | [`ni-research`](./skills/ni-research) | 热点分析、竞品扫描、采集具名素材 |
| 领域学习 | [`ni-fde-copilot`](./skills/ni-fde-copilot) | 将面向内行的专业资料转化为经过确认门禁的学习蓝图和可对话级指南 |
| 灵魂 | [`ni-insight`](./skills/ni-insight) | 挖掘文章的核心观点与独特角度 |
| 写作 | [`ni-writer`](./skills/ni-writer) | 5 种文章原型；两类技术方法论合并，技术思辨保留独立路由 |
| 写书 | [`ni-book-writer`](./skills/ni-book-writer) | 长篇书稿写作（技术书 / 畅销书双风格），含结构、大纲与章节脚手架 |
| 汇报 | [`ni-tech-report`](./skills/ni-tech-report) | 构建一份清晰的技术汇报——叙事线索、证据布局、执行摘要综合 |
| 排版 | [`ni-formatter`](./skills/ni-formatter) | 注入排版模块（part / callout / quote / steps / verdict） |
| 预检 | [`ni-inspect`](./skills/ni-inspect) | 发布前检查元数据、内容质量与结构 |
| 配图 | [`ni-article-image-gen`](./skills/ni-article-image-gen) | 生成封面与内文配图提示词 |
| 海报 | [`ni-poster`](./skills/ni-poster) | 一个公开入口，按参数路由四种 ZINE 风格并生成图像 |
| 3D 建模 | [`ni-3d-model`](./skills/ni-3d-model) | 先确认需求和多视图，再生成并验收带纹理的 GLB 模型 |
| 发布 | [`ni-draft`](./skills/ni-draft) | 将文章推送至微信公众号草稿箱 |
| 编排 | [`ni-article-workflow`](./skills/ni-article-workflow) | 串联上述 skill 为完整管线，支持断点续跑 |
| 诊断 | [`ni-unknown-first`](./skills/ni-unknown-first) | 判断你正面临哪一类 unknown，并给出可复制的下一阶段中文提示词 |
| README | [`ni-readme-guide`](./skills/ni-readme-guide) | 创建中文默认、英文配套、可双向跳转并含可验证徽章的 GitHub README |
| 文档驱动设计 | [`ni-design-with-docs`](./skills/ni-design-with-docs) | 基于资料、访谈和公开证据，将模糊产品或云服务需求生成通过独立评审的研发级产品架构基线 |
| 架构判断 | [`think-like-architect`](./skills/think-like-architect) | 将 PRD 或现有项目上下文转化为第一性原则的首层架构方案 |

每个 skill 均可独立调用；`ni-article-workflow` 只编排内容生产类 skill。

### ni-fde-copilot

`ni-fde-copilot` 面向 FDE 客户会前补课和陌生专业领域学习。它先完整清点资料，建立领域模型、认知缺口与学习主线，再输出五部分学习蓝图等待确认；确认后才生成引导式学习指南、迁移挑战和对话准备度。

调用方式：在新的代理会话中输入 `$ni-fde-copilot`，附上专业资料，说明会议或学习目标，并要求先输出学习蓝图，确认后再写完整指南。

它支持文本、PDF、书籍、报告、PPT、图表、视频、音频和转录，但实际读取能力取决于当前代理环境。无法读取的范围会被明确阻断，不会假装已经处理。完整使用方式、证据边界与验证说明见[中文说明](./skills/ni-fde-copilot/README.md)和[英文说明](./skills/ni-fde-copilot/README.en.md)。

### ni-video2md

`ni-video2md` 将抖音等公开视频 URL 或分享文案转成本地 Whisper 生成的 Markdown 文字稿。它优先使用本地 `whisper.cpp`，首次运行如果缺少 ffmpeg、Whisper.cpp、模型或浏览器依赖，会先下载/安装并缓存；安装或发现 ffmpeg、Whisper.cpp 后会自动把可执行文件目录加入当前进程 PATH，并在 Windows 写入当前用户 PATH；不调用云端转录 API，也不生成 SRT。文字稿会基于全文用本地抽取式算法生成一句话概括，标题、一级标题和文件名统一为“概括-作者”；交付后可将 Markdown 安全复制到用户指定的归档路径。

```bash
python skills/ni-video2md/scripts/video_to_md.py "<video-url-or-share-text>" -o ./transcripts
```

转换期间的媒体、WAV 和 Whisper 中间 TXT 只写入一次性临时目录，成功或失败后自动删除；仅保留 Markdown 输出和依赖缓存。

`-o` 用于指定输出目录（传入 `.md` 路径时取其父目录），最终文件名始终是生成的“概括-作者.md”。返回 Markdown 后，先询问用户是否归档；确认后运行 `skills/ni-video2md/scripts/archive_markdown.py`，目标已存在时不会覆盖，原文件也会保留。

默认支持 Windows x64 的依赖自动下载；其他平台可通过 `NI_VIDEO2MD_FFMPEG`、`NI_VIDEO2MD_WHISPER_CLI`、`NI_VIDEO2MD_MODEL` 和 `NI_VIDEO2MD_BROWSER` 指向已有本地工具。视频和公开依赖下载会消耗网络流量，但语音识别在本机完成。

### ni-readme-guide

`ni-readme-guide` 创建或审计一组同步的 README：

- `README.md` —— 简体中文，默认入口
- `README.en.md` —— 英文配套，并反向链接中文版本

它从仓库证据提炼项目故事，把最短可成功路径前置，保持命令、事实和可验证徽章一致，并校验本地链接、图片、代码块和基础 SVG 安全性。详见 [`skills/ni-readme-guide/README.md`](./skills/ni-readme-guide/README.md)。

### ni-poster 风格参数

`ni-poster` 是海报功能唯一对外暴露的 skill。需要显式控制风格时，在 `/ni-poster` 后使用短参数：

| 命令 | 内部风格 | 适用场景 |
|------|----------|----------|
| `/ni-poster s ...` | Standard | 极简纸刊：3:5 竖版、70–90% 留白、小主体、旧纸扫描质感、稀疏文字、单个克制色彩锚点 |
| `/ni-poster g ...` | Gathered Scenes | 保留用户照片真实内容，再接入来源简化插画场和可见手撕纤维边 |
| `/ni-poster d ...` | Scene Distillation | 照片只作语义参考，最终不保留照片像素，进行作者化抽象重构 |
| `/ni-poster a ...` | Photo Abstract Editorial | 保留原照片，在下方增加由照片空间与色彩关系推导的干净象牙色抽象记忆面板 |

不写 `s`、`g`、`d`、`a` 时，足够明确的风格描述仍可直接判型；如果需求仍然模糊，`ni-poster` 会每次询问一个关键问题，直到风格确认，不再静默默认 Standard。完整参数名 `standard`、`gathered`、`distillation`、`photo-abstract-editorial` 仍兼容。`g` 和 `a` 需要参考照片；`d` 还支持精确触发词 `单色块模式`。

最直白的区别：极简纸刊选 `s`；照片与撕纸插画融合选 `g`；最终不保留照片选 `d`；原照片加下方干净抽象面板选 `a`。只有“照片、抽象、纸感、ZINE”等泛词时会进入访谈。

示例：

```text
/ni-poster s 把这句话做成极简纸刊：夏天结束得很轻
/ni-poster g 保留这张照片的真实场景，加入手撕纤维边
/ni-poster d 用这张照片做视觉隐喻，不保留照片像素
/ni-poster a 保留原照片，在下方生成干净象牙色抽象面板
```

### ni-writer 的 5 种文章原型

写作前先判断文章的主要价值来自亲自体验、资料压缩、工程方法、技术思辨还是个人思绪。原有两类技术方法论合并为一个入口，其他风格保留：

| 原型 | 字数 | 灵魂 | 适用题材 |
|------|------|------|---------|
| 1. 产品体验和评价型 | ≤ 6000 | 我亲自下场 | 实测、上手评价、过程叙事 |
| 2. 发现分享型（速读精华式） | 500-1500 | 我替你刷资料压缩精华 | 帖子 / 视频 / 博客 / 论文转译 |
| 3. 技术方法论型（沉淀 + 深水区合并） | 4500-7000 | 我把事实讲清，再把机制想透 | 工程实践、架构、流程、协作、工具复盘 |
| 4. 技术思辨型 | 5000-8500 | 我把一个判断想清楚 | 概念辨析、机制推演、范式升维 |
| 5. 人生哲学随笔型 | 3000-5000 | 我在想这件事 | 思绪流、感受、非论点写作 |

技术方法论型的专项规则见 [`skills/ni-writer/SKILL.md`](./skills/ni-writer/SKILL.md) 与 `references/tech_writing_rules.md`，技术思辨型保留独立的 `references/tech_polemic_rules.md`。技术方法论要求用一条主场景承载判断，写出可见动作、产物和判断变化。反 AI 终审吸收 `human-writing` 的材料、说话位置、自然推进和改稿规则，并单独检查可删副词与缺少证据的程度副词。

---

## 设计准则

所有 skill 遵循三条共同准则：

- **诚实输出**：不编造、不夸大，失败如实反馈。
- **输出前自检**：交付前按各自的检查清单核对。
- **显式降级**：外部依赖不可用时提供降级路径，并明确标注。

每个 skill 另有各自的领域准则，详见对应的 `SKILL.md`。

---

## 创作管线

```
topic
  ↓
ni-research           trend analysis, competitor scan, material collection
  ↓
ni-insight            define the core argument and angle
  ↓
ni-writer             develop the long-form article
  ↓
ni-formatter          inject layout modules
  ↓
ni-inspect            pre-publication quality check
  ↓
ni-article-image-gen  generate image prompts (optional)
  ↓
ni-draft              push to the WeChat draft inbox
```

任一阶段降级或失败时，对应 skill 会明确告知，由你决定后续处理。

---

## 使用方式

### 完整管线

向 Codex 或 Claude 描述选题，例如：

> 用 ni-skill 写一篇关于「AGENTS.md 实践」的文章

`ni-article-workflow` 会接管流程，逐阶段调用对应 skill。

### 单个 skill

直接描述需求即可触发对应 skill：

- 挖掘文章角度 → `ni-insight`
- 排版文章 → `ni-formatter`
- 抓取网页为 Markdown → `ni-url2md`
- 将视频 URL 或分享文案转成本地 Markdown 文字稿 → `ni-video2md`
- 把专业资料转化为可对话级学习指南 → `ni-fde-copilot`
- 做一张 ZINE 风格极简海报 → `ni-poster`
- 按主题先审多视图、再生成并验收 GLB → `ni-3d-model`
- 判断自己处于哪一类 unknown 并获取下一阶段提示词 → `ni-unknown-first`
- 创建中文默认、英文配套且可双向跳转的 GitHub README → `ni-readme-guide`
- 基于现有资料将模糊产品或云服务需求生成可研发评审的产品架构基线 → `ni-design-with-docs`
- 将 PRD 或现有项目转成首层架构决策 → `think-like-architect`
- 推送草稿 → `ni-draft`

各 skill 的完整触发词见对应的 `SKILL.md`。

---

## 配置

### 微信草稿推送（ni-draft）

通过环境变量配置：

```bash
WECHAT_APPID=wx_xxxxxxxx
WECHAT_SECRET=xxxxxxxxxxxxxxxx
```

或写入 `~/.config/ni-skill/config.yaml`：

```yaml
wechat:
  appid: wx_xxxxxxxx
  secret: xxxxxxxxxxxxxxxx
```

凭证可在微信公众号后台「设置与开发 → 基本配置」获取，并需将调用方 IP 加入白名单。

### 网页抓取（ni-url2md）

可选环境变量：

| 变量 | 用途 |
|------|------|
| `URL_CHROME_PATH` | 指定 Chrome 可执行文件路径 |
| `URL_DATA_DIR` | 指定默认输出目录 |
| `URL_CHROME_PROFILE_DIR` | 指定 Chrome 配置目录以保留登录态 |

### 视频转 Markdown（ni-video2md）

可选环境变量：

| 变量 | 用途 |
|------|------|
| `NI_VIDEO2MD_HOME` | 工具、模型和下载缓存目录 |
| `NI_VIDEO2MD_FFMPEG` / `FFMPEG_PATH` | 指定 ffmpeg 可执行文件 |
| `NI_VIDEO2MD_WHISPER_CLI` / `WHISPER_CLI` | 指定 whisper-cli 可执行文件 |
| `NI_VIDEO2MD_MODEL` / `WHISPER_MODEL` | 指定本地 Whisper `ggml-*.bin` 模型 |
| `NI_VIDEO2MD_BROWSER` / `BROWSER_PATH` | 指定 Chrome、Edge 或 Chromium 可执行文件 |

---

## License

MIT
