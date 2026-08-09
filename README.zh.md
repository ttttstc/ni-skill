# ni-skill

[English](./README.md) | 中文

> 面向内容创作与首层软件架构决策的技能矩阵，覆盖 AI / 工程化管理 / DevOps / 架构四个领域。

ni-skill 是一组面向 AI 编程 agent（Codex、Claude Code 及类似运行时）的协同 skill，覆盖素材抓取、调研、灵魂挖掘、写作、排版、预检、配图、发布和第一性原则架构决策。每个 skill 均可独立使用，内容类 skill 可由 `ni-article-workflow` 编排为完整管线。

---

## 环境要求

- **Codex** / **Claude Code** / 任何能从本地 skills 目录加载 skill 的 AI agent 运行时
- **Python 3.10+** —— `ni-draft` 推送微信草稿时需要
- **Node.js + Chrome** —— `ni-url2md` 抓取网页时需要

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
  ni-tech-report ni-book-writer ni-readme-guide think-like-architect
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
  "ni-unknown-first", "ni-tech-report", "ni-book-writer", "ni-readme-guide",
  "think-like-architect"
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
| 调研 | [`ni-research`](./skills/ni-research) | 热点分析、竞品扫描、采集具名素材 |
| 灵魂 | [`ni-insight`](./skills/ni-insight) | 挖掘文章的核心观点与独特角度 |
| 写作 | [`ni-writer`](./skills/ni-writer) | 6 种文章原型的长/短文写作，融合奥威尔 / 卡尔维诺 / 博尔赫斯文风 |
| 写书 | [`ni-book-writer`](./skills/ni-book-writer) | 长篇书稿写作（技术书 / 畅销书双风格），含结构、大纲与章节脚手架 |
| 汇报 | [`ni-tech-report`](./skills/ni-tech-report) | 构建一份清晰的技术汇报——叙事线索、证据布局、执行摘要综合 |
| 排版 | [`ni-formatter`](./skills/ni-formatter) | 注入排版模块（part / callout / quote / steps / verdict） |
| 预检 | [`ni-inspect`](./skills/ni-inspect) | 发布前检查元数据、内容质量与结构 |
| 配图 | [`ni-article-image-gen`](./skills/ni-article-image-gen) | 生成封面与内文配图提示词 |
| 海报 | [`ni-poster`](./skills/ni-poster) | 一个公开入口，按参数路由四种 ZINE 风格并生成图像 |
| 发布 | [`ni-draft`](./skills/ni-draft) | 将文章推送至微信公众号草稿箱 |
| 编排 | [`ni-article-workflow`](./skills/ni-article-workflow) | 串联上述 skill 为完整管线，支持断点续跑 |
| 诊断 | [`ni-unknown-first`](./skills/ni-unknown-first) | 判断你正面临哪一类 unknown，并给出可复制的下一阶段中文提示词 |
| README | [`ni-readme-guide`](./skills/ni-readme-guide) | 创建中文默认、英文配套、可双向跳转并含可验证徽章的 GitHub README |
| 架构 | [`think-like-architect`](./skills/think-like-architect) | 将 PRD 或现有项目上下文转化为第一性原则的首层架构方案 |

每个 skill 均可独立调用；`ni-article-workflow` 只编排内容生产类 skill。

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

### ni-writer 的 6 种文章原型

写作前先按「**论点 / 情绪 / 资料压缩**」三分判型，再选对应原型：

| 原型 | 字数 | 灵魂 | 适用题材 |
|------|------|------|---------|
| 1. 产品体验和评价型 | ≤ 6000 | 我亲自下场 | 实测、上手评价、过程叙事 |
| 2. 发现分享型（速读精华式） | 500-1500 | 我替你刷资料压缩精华 | 帖子 / 视频 / 博客 / 论文转译 |
| 3. 技术方法论型 | ≤ 6000 | 我把框架掏给你 | 工程经验 + 落地清单 |
| 4. 技术思辨型 | 5000-8500 | 立场鲜明、字字不冗、不左右摇摆 | 概念辨析、范式升维 |
| 5. 人生哲学随笔型 | 3000-5000 | 我在想这件事 | 思绪流、感受、非论点写作 |
| 6. 工程现场方法论型（深水区实践） | 4500-7000 | 我遇到一个工程问题，事后整理成方法 | 工程治理、工作流、协作、AI 工具反思 |

详细规则见 [`skills/ni-writer/SKILL.md`](./skills/ni-writer/SKILL.md) 与 `references/` 下的子风格规则文件。

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
选题
  ↓
ni-research           热点分析、竞品扫描、素材采集
  ↓
ni-insight            确定核心观点与独特角度
  ↓
ni-writer             按文风与角度展开长文
  ↓
ni-formatter          注入排版模块
  ↓
ni-inspect            发布前质量检查
  ↓
ni-article-image-gen  生成配图提示词（可选）
  ↓
ni-draft              推送至微信草稿箱
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
- 做一张 ZINE 风格极简海报 → `ni-poster`
- 判断自己处于哪一类 unknown 并获取下一阶段提示词 → `ni-unknown-first`
- 创建中文默认、英文配套且可双向跳转的 GitHub README → `ni-readme-guide`
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

---

## License

MIT
