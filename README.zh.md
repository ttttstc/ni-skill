# ni-skill

[English](./README.md) | 中文

> 泥巴猪公众号的创作技能矩阵。从选题到发布的完整管线，覆盖 AI / 工程化管理 / DevOps / 架构 四个领域。

ni-skill 是一组面向 Claude Code 的协同 skill，覆盖调研、灵魂挖掘、写作、排版、预检、发布六个阶段。每个 skill 均可独立使用，也可由 `ni-article-workflow` 编排为完整管线。

---

## 环境要求

- **Claude Code**（支持 Plugin Marketplace）
- **Python 3.10+** —— `ni-draft` 推送微信草稿时需要
- **Node.js + Chrome** —— `ni-url2md` 抓取网页时需要

各 skill 的具体依赖见对应的 `SKILL.md`。

---

## 安装

### 方式 1：Plugin Marketplace（推荐）

在 Claude Code 中执行：

```
/plugin marketplace add ttttstc/ni-skill
/plugin install ni-skill@ni-skill
```

### 方式 2：通过 Agent 安装

向 Claude 说明：

> 帮我安装 github.com/ttttstc/ni-skill 的 skill

### 方式 3：手动安装

clone 仓库后，将 `skills/` 下的子目录移动到 `~/.claude/skills/`：

```bash
git clone https://github.com/ttttstc/ni-skill.git
mv ni-skill/skills/* ~/.claude/skills/
```

PowerShell：

```powershell
git clone https://github.com/ttttstc/ni-skill.git
Move-Item ni-skill\skills\* $HOME\.claude\skills\
```

手动安装不支持自动更新，推荐使用方式 1。

---

## Skills

| 阶段 | Skill | 能力 |
|------|-------|------|
| 素材 | [`ni-url2md`](./skills/ni-url2md) | 将任意 URL 抓取为 Markdown，支持 JS 渲染与登录态页面 |
| 调研 | [`ni-research`](./skills/ni-research) | 热点分析、竞品扫描、采集具名素材 |
| 灵魂 | [`ni-insight`](./skills/ni-insight) | 挖掘文章的核心观点与独特角度 |
| 写作 | [`ni-writer`](./skills/ni-writer) | 5 种文章原型的长/短文写作，融合奥威尔 / 卡尔维诺 / 博尔赫斯文风 |
| 排版 | [`ni-formatter`](./skills/ni-formatter) | 注入排版模块（part / callout / quote / steps / verdict） |
| 预检 | [`ni-inspect`](./skills/ni-inspect) | 发布前检查元数据、内容质量与结构 |
| 配图 | [`ni-article-image-gen`](./skills/ni-article-image-gen) | 生成封面与内文配图提示词 |
| 发布 | [`ni-draft`](./skills/ni-draft) | 将文章推送至微信公众号草稿箱 |
| 编排 | [`ni-article-workflow`](./skills/ni-article-workflow) | 串联上述 skill 为完整管线，支持断点续跑 |

每个 skill 均可独立调用，也可由 `ni-article-workflow` 统一编排。

### ni-writer 的 5 种文章原型

写作前先按「**论点 / 情绪 / 资料压缩**」三分判型，再选对应原型：

| 原型 | 字数 | 灵魂 | 适用题材 |
|------|------|------|---------|
| 1. 产品体验和评价型 | ≤ 6000 | 我亲自下场 | 实测、上手评价、过程叙事 |
| 2. 发现分享型（速读精华式） | 500-1500 | 我替你刷资料压缩精华 | 帖子 / 视频 / 博客 / 论文转译 |
| 3. 技术方法论型 | ≤ 6000 | 我把框架掏给你 | 工程经验 + 落地清单 |
| 4. 技术思辨型 | 5000-8500 | 立场鲜明、字字不冗、不左右摇摆 | 概念辨析、范式升维 |
| 5. 人生哲学随笔型 | 3000-5000 | 我在想这件事 | 思绪流、感受、非论点写作 |

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

向 Claude 描述选题，例如：

> 用 ni-skill 写一篇关于「AGENTS.md 实践」的文章

`ni-article-workflow` 会接管流程，逐阶段调用对应 skill。

### 单个 skill

直接描述需求即可触发对应 skill：

- 挖掘文章角度 → `ni-insight`
- 排版文章 → `ni-formatter`
- 抓取网页为 Markdown → `ni-url2md`
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
