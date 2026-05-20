# ni-skill

[English](./README.md) | 中文

> 泥巴猪「低卧扑食」公众号的创作技能矩阵。从选题到发布的完整管线，覆盖 AI / 工程化管理 / DevOps / 架构 四个领域。

ni-skill 是为 Claude Code 设计的一组协同 skill，串起调研 → 灵魂挖掘 → 写作 → 排版 → 预检 → 发布的全流程。所有 skill 共享 3 条工程通则（诚实输出 / 输出前自检 / 显式降级），每个 skill 还有自己的领域原则。既能单独使用，也能由 `ni-article-workflow` 编排器串成一条管线。

---

## Prerequisites

- **Claude Code**（支持 Plugin Marketplace）
- **Python 3.10+** — 仅 `ni-draft` 推送微信草稿用
- **Node.js + Chrome** — 仅 `ni-url2md` 抓网页用（首次会用 `npx -y bun` 拉取 Bun 运行时）

各 skill 的具体依赖见各自的 `SKILL.md`。

---

## 安装

### 方式 1：Plugin Marketplace（推荐）

在 Claude Code 里：

```
/plugin marketplace add ttttstc/ni-skill
/plugin install ni-skill@ni-skill
```

### 方式 2：让 Agent 帮你装

直接告诉 Claude：

> 帮我安装 github.com/ttttstc/ni-skill 的 skill

### 方式 3：手动 clone

```bash
git clone https://github.com/ttttstc/ni-skill.git ~/.claude/skills/ni-skill
```

> 手动安装时 skill 在 `~/.claude/skills/ni-skill/skills/ni-*/` 下，Claude Code 会自动扫描。

---

## Skills

9 个 skill，按管线阶段排列：

| 阶段 | Skill | 触发场景 |
|------|-------|---------|
| 素材 | [`ni-url2md`](./skills/ni-url2md) | 把任意 URL 抓成 Markdown（Chrome CDP，含 `--wait` 登录态） |
| 调研 | [`ni-research`](./skills/ni-research) | 摸热点、扫竞品（二分输出）、采具名素材 |
| 灵魂 | [`ni-insight`](./skills/ni-insight)  | 角度发现 → 用户碰撞 → 灵魂锁定。 |
| 写作 | [`ni-writer`](./skills/ni-writer) | 长文写作，奥威尔 + 卡尔维诺 + 博尔赫斯文风糅合，四层自检 |
| 排版 | [`ni-formatter`](./skills/ni-formatter) | 5 模块最小集（part/callout/quote/steps/verdict） |
| 预检 | [`ni-inspect`](./skills/ni-inspect) | 元数据 / 内容质量 / 结构三组检查，自带禁用词黑名单 |
| 配图 | [`ni-article-image-gen`](./skills/ni-article-image-gen) | 1 张封面 + 9 张内文 prompt，默认黏土定格动画，可切风格 |
| 发布 | [`ni-draft`](./skills/ni-draft) | Markdown → 微信兼容 HTML → 草稿箱（Python 内嵌，零外部二进制依赖） |
| 编排 | [`ni-article-workflow`](./skills/ni-article-workflow) | 串起以上 8 个 skill，状态机驱动，支持断点续跑 |

每个 skill 都支持**独立运行**，也都能被 `ni-article-workflow` 编排调度。

---

## 原则

`ni-writer` 的写作风格（七条价值观 + 底盘四律 + 活人感七条）是它自己的事。其他 8 个 skill 各有自己的工程原则，大体围绕三件事：

- **诚实输出**：不编造、不谎报、不夸大；失败如实报。
- **输出前自检**：按各自的检查清单核对再交付。
- **显式降级**：外部依赖不可用时给降级路径，标注清楚，不抛 stack trace。

每个 skill 还有自己的领域原则——比如 `ni-insight` 的「角度必须挂回素材 + 用户拍板」、`ni-formatter` 的「不堆模块 + verdict 必存在」、`ni-draft` 的「错误转人话 + 失败必降级到本地 HTML」。详见各 skill 的 SKILL.md。

---

## 完整管线流程

```
选题
  ↓
ni-research        摸热点 + 扫竞品 + 采素材
  ↓
ni-insight       挖灵魂、锁定 10-20 字核心论点
  ↓
ni-writer          按文风 + 灵魂展开成长文
  ↓
ni-formatter       穿衣：5 模块最小集
  ↓
ni-inspect         体检：BLOCKED 回炉 / WARNING 提示 / ready 放行
  ↓
ni-article-image-gen   1 封面 + 9 内文配图 prompt（可选）
  ↓
ni-draft           推送微信草稿箱（封面占位，自己在后台设）
  ↓
done（公众号后台看到草稿，发布前自己再调一遍）
```

中间任何一步降级或失败，都会显式告诉你，你来定下一步。

---

## 怎么用

### 完整管线

直接说：

> 用 ni-skill 从头写一篇关于「AGENTS.md 该不该写」的文章

`ni-article-workflow` 会接管，问你 article-name，建工作目录，逐阶段调对应 skill。

### 单步触发

直接说想做的事：

- 「帮我挖这篇的角度」→ `ni-insight`
- 「这篇排个版」→ `ni-formatter`
- 「把这个链接抓成 markdown」→ `ni-url2md`
- 「推到草稿箱」→ `ni-draft`

每个 skill 的 SKILL.md 里有完整触发词清单。

---

## 配置

### 微信草稿推送（ni-draft）

环境变量：

```bash
WECHAT_APPID=wx_xxxxxxxx
WECHAT_SECRET=xxxxxxxxxxxxxxxx
```

或写到 `~/.config/ni-skill/config.yaml`：

```yaml
wechat:
  appid: wx_xxxxxxxx
  secret: xxxxxxxxxxxxxxxx
```

凭证从公众号后台「设置与开发 → 基本配置」拿。注意把调用机器的 IP 加进白名单。

### 网页抓取（ni-url2md）

可选环境变量：

| 变量 | 用途 |
|------|------|
| `URL_CHROME_PATH` | Chrome 不在默认位置时指定 |
| `URL_DATA_DIR` | 默认输出目录 |
| `URL_CHROME_PROFILE_DIR` | 保留 cookies 用 |

---

## License

MIT
