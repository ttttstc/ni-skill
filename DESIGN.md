# ni-skill 公众号创作技能矩阵设计书（蓝图级）

**版本**：1.0（蓝图）
**作者**：泥巴猪
**日期**：2026-05-17
**上游**：[SPEC.md](./SPEC.md) v2.0
**状态**：待评审，评审通过后进入实现阶段

> **本文定位**：在 SPEC.md 的"做什么"之上，回答"怎么做"——锁定跨 skill 的接口契约、共享约定、最小可行模块集，以及关键 prompt 设计骨架。每个 skill 的完整 SKILL.md 在实现阶段单独落盘，不在本文中展开。

---

## 第零章 套件基因（元规范）

ni-writer 是套件中已验证的标杆。下面 5 条基因从 ni-writer 提取，**所有 ni-* skill 强制遵守**。

### G1 真实优先

- 禁编造场景、禁假设性例子、禁空泛工具名（不说"AI 工具"，说 "Claude Code / Codex"）
- 未验证的事实标 `[待核实]`，不写得像验证过
- 数据/案例必须可追溯到具名来源

**落到各 skill**：
- `ni-research` 素材表多一列 `source_verifiable: true|false`
- `ni-insight` 角度必须挂靠真实素材，不允许凭空"反直觉"
- `ni-formatter` 不堆模块凑数
- `ni-inspect` L1 扫描接入 ni-writer 的禁用词表

### G2 独特角度门槛

- "没有干货或独特角度不下笔"——ni-writer 的硬门槛
- 三个反直觉提问模板（X 其实是坏的 / Y 是症状不是问题 / Z 在某条件下负收益）是 ni-insight 的主流程

**落到各 skill**：
- `ni-research` 竞品扫描二分输出：`已被竞品说过` vs `未被覆盖`，前者交给 ni-insight 当避雷区
- `ni-insight` 直接复用三个提问模板
- `ni-article-workflow` 在 insight 阶段不通过时**拒绝**进入 writing 阶段

### G3 活人在场

- 第一人称必须在场，承认混合情绪与不确定
- 所有 skill 对用户的输出文案**都用第一人称对话腔**，禁报告体

**反例**（禁止）：
```
[ni-research] 已完成调研，共采集 6 条素材，3 条来源已具名。
```
**正例**（推荐）：
```
[ni-research] 我扫了一圈，捞到 6 条素材，3 条能溯源，剩下 3 条我标了"待核实"——
其中 X 这条我有点拿不准，要不要你自己看一眼？
```

### G4 四层自检骨架（L1-L4）

ni-writer 的 L1 硬规则 / L2 风格 / L3 内容 / L4 反 AI 四层结构是套件统一的验收骨架。每个 skill 的"验收标准"按以下模式映射：

| 层级 | ni-writer 含义 | 在其他 skill 的映射 |
|------|---------------|-------------------|
| L1 | 禁用词/标点/工具名硬规则 | 输入格式合法、必填字段齐全、外部依赖可用 |
| L2 | 节奏/活人感/可读性折返 | 输出结构匹配契约、与上游 skill 接口对齐 |
| L3 | 观点支撑/知识输出/对立面 | 输出在内容质量层面达标（如素材具名率、角度独特性） |
| L4 | humanizer 双盘问 | 反向自查"这个输出最像 AI 偷懒的是哪一处" |

### G5 降级而不放弃

- 外部依赖不可用时给降级路径，不抛错给用户
- 降级必须**显式标注**，让用户知道这是降级结果

**示例**：
- WebSearch 不可用 → ni-research 用 LLM 训练数据 + 标注 `[降级采集]`
- 微信 token 失效 → ni-draft 输出本地 HTML + 手动上传指引 + 标注 `[降级发布]`

---

## 第一章 ni-article-workflow 编排器

### 1.1 定位

**纯编排，零业务**。它只做四件事：
1. 维护状态机
2. 在阶段之间传递产物
3. 强制执行跨 skill 的共享约定（工作目录、文件命名、接口契约）
4. 失败降级与断点续跑

**它不做的事**：
- 不执行调研、不挖灵魂、不写文章、不排版、不推送——所有这些都委托给原子 skill
- 不维护任何"业务"知识（禁用词表、文风规则、模块清单都在原子 skill 里）

### 1.2 共享约定（仅在 workflow 模式下强制）

> **重要**：原子 skill 单独调用时**不**遵守这套约定（不硬编码路径），只在被 workflow 调度时才按约定读写文件。约定由 workflow 在调用时**注入路径参数**。

#### 1.2.1 工作目录布局

```
drafts/
└── {article-name}/                  # article-name 由用户在 workflow 启动时手动指定（kebab-case，≤40 字符）
    ├── state.yaml                   # 状态机（workflow 独占读写）
    ├── research.md                  # ni-research 产物
    ├── insight.md                   # ni-insight 产物
    ├── article.md                   # ni-writer 产物（已存在 skill 的产物路径）
    ├── formatted.md                 # ni-formatter 产物
    ├── inspect-report.md            # ni-inspect 产物
    ├── images/                      # ni-article-image-gen 产物
    │   ├── cover-prompts.md
    │   └── inline-prompts.md
    ├── draft-meta.yaml              # ni-draft 产物（含 media_id、digest 等）
    └── logs/                        # 各 skill 执行日志
        └── {step}-{timestamp}.log
```

#### 1.2.2 state.yaml schema

```yaml
article_name: how-to-evaluate-ai-coding-tools
created_at: 2026-05-17T10:00:00+08:00
updated_at: 2026-05-17T11:23:00+08:00

# 当前阶段，取值：init|research|insight|writing|formatting|inspect|imaging|draft|done|failed
phase: writing

# 每个阶段的结果
stages:
  research:
    status: done           # pending|in_progress|done|skipped|failed|degraded
    started_at: ...
    finished_at: ...
    artifact: research.md
    degraded: false
    notes: 6 条素材，3 条待核实
  insight:
    status: done
    artifact: insight.md
    soul_one_liner: "AI 工具不是替你写代码，是替你不写那些不该写的代码"
    selected_angle: 反转型
  writing:
    status: in_progress
    started_at: ...
  # ...

# 用户决策记录（每次需要用户确认时落盘）
user_decisions:
  - at: 2026-05-17T10:30:00+08:00
    stage: insight
    question: "三个角度选哪个？"
    answer: "角度 2"
  # ...

# 降级记录
degradations: []
```

#### 1.2.3 接口契约（workflow 调用 skill 的参数注入）

workflow 调用每个原子 skill 时按以下模式传参：

```
触发 {skill_name}：
- workdir: drafts/{article-name}/
- inputs:
    - {上游产物的相对路径}
    - {从 state.yaml 提取的关键字段}
- output_path: drafts/{article-name}/{产物文件名}
- on_success: 写回 state.yaml 对应 stage
- on_failure: 走该 skill 的降级路径，标 degraded=true
```

### 1.3 article-name 生成规则

**手动指定模式**（用户决策）：workflow 启动时**必须**询问用户：

```
workflow: 这篇文章我们叫什么？(用作工作目录名，kebab-case，≤40 字符)
        例如：how-to-evaluate-ai-coding-tools
user:   ai-tools-2026
workflow: 好，drafts/ai-tools-2026/ 已建好，开始走流程……
```

**校验规则**（workflow 强制）：
- 只允许 `[a-z0-9-]`，其他字符报错让用户重输
- 长度 1-40
- 如果 `drafts/{article-name}/` 已存在 → 询问"续跑这篇 / 换个名 / 覆盖"
- 用户给中文 → 提示"请用英文 kebab-case，例如 ..."

### 1.4 状态机

```
init
  ↓ (用户给选题)
research ─────────失败─→ failed (用户决定 retry/skip/abort)
  ↓ (素材就绪)
insight  ─────────失败─→ failed
  ↓ (用户选定角度)
writing  ─────────失败─→ failed
  ↓ (ni-writer L4 通过)
formatting
  ↓
inspect  ─────────BLOCKED─→ writing (回炉重改)
  ↓ (ready 或 degraded)
imaging (可选并发)
  ↓
draft    ─────────失败─→ degraded (输出本地 HTML)
  ↓
done
```

**断点续跑**：用户重新触发 `ni-article-workflow --article-name xxx` 时，workflow 读 `state.yaml`，从 `phase` 继续。

**回退**：用户可手动改 `state.yaml.phase` 回退到任意阶段，workflow 不阻拦。

### 1.5 SKILL.md 骨架（不含业务）

```markdown
---
name: ni-article-workflow
description: 串联 ni-research → ni-insight → ni-writer → ni-formatter → ni-inspect → ni-draft 的编排器。
              当用户说"从头写一篇""走完整管线""一键发"时触发。
              本 skill 只编排，不含业务，所有业务委托给原子 skill。
---

# ni-article-workflow

你是一个**纯调度器**。你的工作只有 4 件：维护 state.yaml、调原子 skill、传产物、降级。
你**不**写文章、不挖角度、不排版。看到要做这些事，调对应 skill。

## 启动流程
1. 用户给选题 → 询问 article-name（手动指定）→ 校验 → 建 drafts/{article-name}/ → 初始化 state.yaml
2. 进入状态机循环

## 状态机循环
读 state.yaml.phase → 调对应 skill（注入 workdir + inputs + output_path）→ 写回 state.yaml

## 阶段映射
| phase | 调用 skill | 输入 | 输出 |
|-------|-----------|------|------|
| research | ni-research | 选题关键词 | research.md |
| insight | ni-insight | research.md | insight.md |
| ... | ... | ... | ... |

## 降级
任何 skill 返回 degraded 状态，记录到 state.yaml.degradations，
显式告诉用户："这一步降级了，原因是 X，你要继续还是处理一下？"

## 断点续跑
触发时若 state.yaml 已存在，从 phase 继续，不重做已完成阶段。
```

---

## 第二章 7 个原子 skill 蓝图

下面每个 skill 给：**定位 / 输入输出契约 / SKILL.md 骨架要点 / references 清单 / 验收 L1-L4 / 降级**。

### 2.1 ni-research

| 项 | 内容 |
|----|------|
| **定位** | 内容生产前端：调研 + 素材采集 + 竞品扫描 |
| **输入** | 选题关键词（必填）、领域（可选） |
| **输出** | `research.md`（结构见下） |
| **核心依赖** | WebSearch（降级到 LLM 训练数据） |

**research.md 结构**：
```markdown
# 调研：{选题}

## 热点分析
- 趋势：上升 / 平稳 / 下降
- 写作时机：现在发 / 等等看
- 数据来源：[具名]

## 竞品覆盖
### 已被说过的角度（避雷）
1. {主流观点 1} — 出处：xxx
2. {主流观点 2} — 出处：xxx

### 尚未被覆盖
1. {空白区 1}
2. {空白区 2}

## 素材库
| # | 素材 | 来源 | 可核实 | 备注 |
|---|------|------|--------|------|
| 1 | ... | https://... | ✅ | |
| 2 | ... | ... | ⚠️ 待核实 | |

## 潜在角度
- 角度 A：{描述}
- 角度 B：{描述}
- 角度 C：{描述}
```

**SKILL.md 要点**：
- 强制 G1：每条素材必须有 `source` 字段，无 source 标 `[待核实]`
- 强制 G2：竞品扫描二分输出（已说过 vs 未覆盖）
- 强制 G3：以"我捞到了什么"对话腔输出
- 强制 G5：WebSearch 不可用降级到 LLM + 标 `[降级采集]`

**验收（L1-L4）**：
- L1：选题非空、输出文件合法、至少 5 条素材
- L2：与 ni-insight 的接口字段齐全（热点 / 竞品 / 素材 / 角度）
- L3：素材具名率 ≥ 60%、竞品至少 3 条、角度至少 3 个
- L4：自查"这份调研是不是只是 Wikipedia 复述"

**references**：
- `topic-analysis.md`（热点判断标准、写作时机决策树）

---

### 2.2 ni-insight ⭐⭐⭐

| 项 | 内容 |
|----|------|
| **定位** | 灵魂注入站，整个管线的北极星 |
| **输入** | `research.md` |
| **输出** | `insight.md`（含核心论点、选定角度、支撑逻辑、预判反驳） |

**insight.md 结构**：
```markdown
# 灵魂定位：{选题}

## 一句话核心论点
{10-20 字}
- 类型：反转型 / 升维型 / 利己型 / 类比型 / 时间型

## 三个候选角度（用户已选择）
1. ✅ {选定角度} | 预期反应："{读者会说什么}"
2. {备选 1}
3. {备选 2}

## 支撑逻辑
1. {为什么观点成立 1}
2. {为什么观点成立 2}
3. {为什么观点成立 3}

## 预判反驳
- 反驳 1：{别人会怎么反对} → 应对：{怎么回}
- 反驳 2：... → 应对：...

## 灵魂验收
- 朋友圈测试：{这句发朋友圈会有人想评论吗？} → 通过 / 不通过
```

**SKILL.md 要点**：
- 强制 G2：直接复用 ni-writer 第二步的三个反直觉提问模板
- 强制用户碰撞：未拿到用户明确选定的角度，**拒绝**输出 `insight.md`
- 强制 G3：用"哎我有个角度，你看这样行不行"的对话腔，禁报告体
- 与 workflow 协议：若用户三轮碰撞后仍未确认，标 `failed`，让 workflow 决定 abort 或回 research 补料

**关键 prompt 片段**（角度发现）：
```
读完 research.md 后，先做两件事：
1. 把"已被说过"清单列出来——这些角度禁用，不许踩
2. 在"未被覆盖"区找 3 个潜在角度

然后用三模板挖：
(1) 大家都觉得 X 是好的，有没有 X 其实是坏的的情况？
(2) 大家都在抱怨 Y，Y 会不会其实是症状不是问题？
(3) 最佳实践 Z 在什么条件下其实是负收益？

把 3 个角度抛给用户：
"我有三个角度，你看哪个最有感觉？
 A: ... | 我猜读者会说"...
 B: ... | 我猜读者会说"...
 C: ... | 我猜读者会说"...
 或者你心里有别的，直接告诉我。"
```

**验收（L1-L4）**：
- L1：必须有用户明确选择记录、核心论点 10-20 字
- L2：与 ni-writer 输入字段对齐
- L3：支撑逻辑 ≥ 3、预判反驳 ≥ 1
- L4：灵魂验收（朋友圈测试）通过

**references**：
- `angle-discovery.md`（5 种角度类型详解 + 案例）
- `question-templates.md`（三个反直觉提问模板的具体话术 + 变体）

---

### 2.3 ni-writer（已存在，仅做接口适配）

| 项 | 内容 |
|----|------|
| **定位** | 已存在 skill，无需重写 |
| **输入新增** | `insight.md`（核心论点 + 支撑逻辑 + 预判反驳）作为附加输入 |
| **输出** | `article.md` |

**适配点**（无需改 ni-writer/SKILL.md，由 workflow 在调用时注入）：
- workflow 把 `insight.md` 的核心论点作为"独特视角"传给 ni-writer 第二步
- 跳过 ni-writer 内部的"独特视角询问"（已在 ni-insight 完成）
- 保留 ni-writer 的四层自检不动

**验收**：完全复用 ni-writer 现有 L1-L4。

---

### 2.4 ni-formatter（最小正文模块集）

| 项 | 内容 |
|----|------|
| **定位** | 给文章"穿衣"，注入排版意图 |
| **输入** | `article.md` + `insight.md`（核心论点用于决定 verdict 模块的内容） |
| **输出** | `formatted.md`（含排版意图注释的 markdown） |

#### 2.4.1 最小正文模块集（5 个）

| 模块 | 作用 | 使用频率上限 | 触发场景 |
|------|------|------|---------|
| **part** | 章节分段 | ≤ 文章 H2 数 | 技术章节强制；非技术章节按需 |
| **callout** | 提示/警告/重点 | ≤ 3 | 技术警告、易踩坑、反直觉判断 |
| **quote** | 引用/金句 | ≤ 2 | 开头名言、文中可独立截图的金句 |
| **steps** | 步骤流程 | ≤ 1 | 落地路径、操作流程 |
| **verdict** | 核心判断 | = 1 | insight.md 的核心论点对应处 |

**总模块数上限**：5（与 SPEC.md "6 个"一致，但正文阶段先收紧到 5）

**禁止**：
- 任何模块数量超上限
- 模块与文章类型不匹配（如纯抒情文章塞 steps）
- 重复模块

#### 2.4.2 每个模块的 AI 转译 prompt（蓝图）

> 完整 prompt 在实现阶段单独写到 `references/layout-modules.md`，这里给骨架。

**part**：
```
触发：H2 标题前
输出：在 H2 标题处保留原标题 + 注释 "<!-- :::part {title} -->"，
     由下游渲染时转成视觉分段（分隔线 + 标题强调）
```

**callout**：
```
触发：检测到"注意 / 警告 / 容易踩坑 / 反直觉" 等关键词的段落
输出：用 "<!-- :::callout {warning|info|tip} -->" 包裹该段
     {warning}: 技术警告类
     {info}: 中性提示
     {tip}: 经验技巧
```

**quote**：
```
触发：开头名言 + 文中可独立截图转发的金句
输出：用 "<!-- :::quote -->" 包裹，并标注 source（如有）
约束：金句 ≤ 30 字；名言遵循 ni-writer 的"短/冷/张力"原则
```

**steps**：
```
触发：检测到"第一步 / 第二步" 或编号列表（≥3 条）的操作流程
输出：用 "<!-- :::steps -->" 包裹该列表
约束：每步开头加粗（符合 ni-writer 加粗规则）；总步骤 ≤ 7
```

**verdict**：
```
触发：从 insight.md 读取核心论点，在文章中找到首次完整呈现该论点的句子
输出：用 "<!-- :::verdict -->" 包裹该句
约束：全文 = 1 处；位置通常在第一节末或开头铺垫之后
```

#### 2.4.3 选模块决策算法

```
1. 读文章类型（从 article.md 的 ni-writer 自检报告推断，或问用户）
2. 必选：verdict（来自 insight.md）
3. 按文章类型加：
   - 技术方法论型 / 架构原理型 → +part, +steps
   - 现象解读型 / 工具分享型 → +callout, +quote
   - 调查实验型 / 产品体验型 → +quote, +callout（按需）
4. 总数检查 ≤ 5
5. 无 verdict 不输出（必须有核心论点锚点）
```

**SKILL.md 要点**：
- 强制 G1：不堆模块凑数
- 强制 G3：以"我给你穿衣服，看看哪件合身"的对话腔
- 强制 G5：找不到合适触发点的模块直接不放，不硬塞

**验收（L1-L4）**：
- L1：模块语法合法、verdict 必存在且 = 1
- L2：模块选择匹配文章类型
- L3：每个模块的内容确实对应触发场景（不是为加而加）
- L4：自查"如果把所有 :::xxx 注释去掉，文章还能读吗？"——能读才合格

**references**：
- `layout-modules.md`（5 个模块的完整 prompt + 正反例）
- `module-decision.md`（决策算法 + 文章类型映射表）

---

### 2.5 ni-inspect

| 项 | 内容 |
|----|------|
| **定位** | 发布前的质量检查站 |
| **输入** | `formatted.md` |
| **输出** | `inspect-report.md`（含 readiness：ready / degraded / blocked） |

**检查项分三组**：

**Metadata**（机械检查）：
- title 长度 5-64 字节
- digest ≤ 120 字节
- 正文字数 ≥ 200
- 图片数 ≤ 10

**内容质量**（复用 ni-writer 禁用词表）：
- 禁用词命中数 = 0
- 加粗密度 ≤ 15%
- 标题/伪标题加粗完整
- 至少 1 处金句

**结构**（与 ni-formatter 接口对齐）：
- 模块总数 ≤ 5
- verdict = 1
- callout ≤ 3、quote ≤ 2、steps ≤ 1

**分级**：
- **BLOCKED**：禁用词命中、verdict 缺失、字数 < 200 → workflow 回 writing
- **WARNING**：加粗密度超标、digest 超长 → workflow 提示用户但可跳过
- **INFO**：模块数偏多但未超限 → 不影响流程

**SKILL.md 要点**：
- 强制 G3：报告以"我扫了一遍，发现这些"的对话腔
- 强制 G4：报告本身就是 L1-L4 自检报告的扩展版
- 强制 G5：BLOCKED 项给具体修复建议，不只是报错

**验收**：
- L1：所有检查项都跑了（不漏检）
- L2：报告格式与 workflow 接口对齐（readiness 字段必填）
- L3：每条问题定位到具体段落/句子
- L4：修复建议具体可操作

**references**：
- `check-rules.md`（每项检查的具体阈值 + 分级规则）

---

### 2.6 ni-draft（仅文章→草稿，不传图，Python 内嵌）

| 项 | 内容 |
|----|------|
| **定位** | 文章推送到微信草稿箱 |
| **输入** | `formatted.md` + 必填 `cover_media_id`（用户预先在公众号后台传好的封面 media_id） |
| **输出** | `draft-meta.yaml`（含返回的 draft media_id） |
| **技术栈** | Python 3.10+，纯内嵌脚本，**不依赖** md2wechat / wewrite |

**P0 范围**（本次实现）：
- 文章 markdown → 微信兼容 HTML 转换（内联 CSS）
- 调微信草稿箱 API 创建草稿
- access_token 获取与本地缓存（≤ 7000s 复用）
- 错误码处理（40001 token 失效自动重试、45004 digest 超长截断、其他转人话）
- **不**做：图片上传、封面生成、正文配图替换

**ni-draft 工程结构**：
```
ni-draft/
├── SKILL.md
├── references/
│   ├── wechat-api.md           # 错误码、API 端点、配置说明
│   └── html-style-guide.md     # 微信兼容 HTML 的内联 CSS 约定
├── scripts/
│   ├── wechat_draft.py         # 主入口 CLI（约 200-300 行）
│   ├── token_cache.py          # access_token 缓存（文件锁 + TTL）
│   └── md_to_wechat_html.py    # markdown → 内联 CSS HTML
├── requirements.txt            # requests / markdown / pyyaml
└── tests/
    └── fixtures/               # 离线测试样例
```

**Python 依赖**（最小集）：
```
requests>=2.31      # HTTP 调微信 API
markdown>=3.5       # MD → HTML
pyyaml>=6.0         # 读配置、写 draft-meta.yaml
```

**CLI 接口**：
```bash
python scripts/wechat_draft.py create \
  --article drafts/{article-name}/formatted.md \
  --cover-media-id {用户传入} \
  --title "..." \
  --digest "..." \
  --output drafts/{article-name}/draft-meta.yaml
```

**配置**：
- 环境变量优先：`WECHAT_APPID`、`WECHAT_SECRET`
- 兜底配置文件：`~/.config/ni-skill/config.yaml`
  ```yaml
  wechat:
    appid: wx_xxx
    secret: xxx
    token_cache_path: ~/.cache/ni-skill/wechat_token.json
  ```

**access_token 管理**：
- 首次调用拿 token，写入 `~/.cache/ni-skill/wechat_token.json`（含过期时间戳）
- 后续调用先读缓存，未过期直接复用
- 收到 40001 → 删缓存重拿 → 重试 1 次

**markdown → HTML 转换原则**：
- 全部 CSS 内联到 `style="..."`（公众号不支持 `<style>` 和 `<link>`）
- 标题 / 段落 / 列表 / 引用 / 代码块都按公众号视觉规范配默认样式
- ni-formatter 的 `<!-- :::xxx -->` 注释在此阶段转成对应 HTML 结构：
  - `:::part` → 视觉分隔线 + 标题强调
  - `:::callout` → 背景色块（warning/info/tip 三色）
  - `:::quote` → 缩进引用 + 左侧色条
  - `:::steps` → 编号列表（每步开头加粗）
  - `:::verdict` → 加粗居中块（视觉锚点）

**SKILL.md 要点**：
- 强制 G3：所有错误输出转人话（不直接抛 errcode）
- 强制 G5：推送失败必降级到本地 HTML
- 不要求用户懂 API

**降级路径**：
```
推送失败 → 输出 drafts/{article-name}/local-preview.html
        + 输出"打开这个文件复制内容到公众号后台"的指引
        + state.yaml 标 degraded=true
```

**验收（L1-L4）**：
- L1：环境变量/配置可用、cover_media_id 非空、article.md 存在、Python 环境就绪
- L2：返回的 draft media_id 写入 draft-meta.yaml
- L3：HTML 在公众号草稿箱预览不变形（5 个排版模块都正常渲染）
- L4：错误信息对用户友好（不暴露原始 errcode 数字）

**references**：
- `wechat-api.md`（错误码表、API 端点、配置示例）
- `html-style-guide.md`（5 个模块的内联 CSS 规范）

---

### 2.7 ni-article-image-gen（P1）

| 项 | 内容 |
|----|------|
| **定位** | 生成封面和配图的 prompt（不直接出图） |
| **输入** | `article.md` + `insight.md` |
| **输出** | `images/cover-prompts.md` + `images/inline-prompts.md` |

**P1 优先级**——不阻塞 P0 闭环。规格细节按 SPEC.md 4.7 节，本设计书不展开。

---

## 第三章 ni-formatter 5 个模块的最小转译规则

见 2.4 节。完整 prompt 在 `ni-formatter/references/layout-modules.md` 实现阶段写。

---

## 第四章 ni-draft Python 内嵌实现方案

### 4.1 设计原则

- **零外部二进制依赖**：不依赖 md2wechat、不依赖 wewrite，所有逻辑在 ni-draft 目录内
- **Python 3.10+ 原生**：用户机器只需 Python 环境
- **最小依赖**：仅 `requests` / `markdown` / `pyyaml` 三个 PyPI 包
- **可独立测试**：fixtures + 离线测试，不必每次连微信 API

### 4.2 模块拆分

| 模块 | 职责 | 行数估算 |
|------|------|---------|
| `wechat_draft.py` | CLI 入口 + 主流程编排 | ~120 |
| `token_cache.py` | access_token 文件缓存（含文件锁防并发竞态） | ~50 |
| `md_to_wechat_html.py` | markdown → 内联 CSS HTML + 5 个排版模块渲染 | ~150 |
| **合计** | | ~320 |

### 4.3 主流程（wechat_draft.py create）

```
1. 解析 CLI 参数（article / cover-media-id / title / digest / output）
2. 读配置（env > ~/.config/ni-skill/config.yaml）
3. 校验输入（article 文件存在、cover-media-id 非空、title ≤ 64 字节、digest ≤ 120 字节）
4. 读 article markdown
5. 调 md_to_wechat_html.convert(md) → 得到 HTML
6. 调 token_cache.get_token() → access_token
7. POST https://api.weixin.qq.com/cgi-bin/draft/add?access_token=xxx
   body: { articles: [{ title, content: html, thumb_media_id: cover-media-id, digest, ... }] }
8. 处理响应：
   - 成功 → 写 output (draft-meta.yaml)
   - 40001 → token_cache.invalidate() + 重试 1 次
   - 45004 → digest 自动截断到 110 字节 + 重试 1 次
   - 其他 → 转人话报错 + 降级到本地 HTML
```

### 4.4 微信兼容 HTML 的关键约定

| 约束 | 处理 |
|------|------|
| 不支持 `<style>` 和 `<link>` | 全部 CSS 内联到元素 `style` 属性 |
| 不支持 JS | 不引入任何 JS |
| `<img>` 的 src 必须是微信素材 URL 或 base64 | P0 不处理图片（仅封面用 media_id） |
| 段落必须用 `<p>` 包裹 | markdown 库默认行为 |
| 标题 H1-H4 各自配色和字号 | `html-style-guide.md` 给标准 |

### 4.5 5 个排版模块的 HTML 渲染

> 完整 CSS 在 `references/html-style-guide.md` 定义，这里给骨架。

| 模块标记 | 渲染目标 |
|---------|---------|
| `<!-- :::part {title} -->` | `<hr style="border-top:1px solid #ddd;margin:2em 0"><h2 style="...">{title}</h2>` |
| `<!-- :::callout warning -->...<!-- ::: -->` | `<div style="background:#fff3cd;border-left:4px solid #ffc107;padding:1em;margin:1em 0">...</div>` |
| `<!-- :::quote -->...<!-- ::: -->` | `<blockquote style="border-left:3px solid #999;padding-left:1em;color:#666;margin:1em 0">...</blockquote>` |
| `<!-- :::steps -->...<!-- ::: -->` | `<ol style="...">` 每个 `<li>` 加粗开头 |
| `<!-- :::verdict -->...<!-- ::: -->` | `<div style="text-align:center;font-weight:bold;font-size:1.1em;margin:2em 0;padding:1em;background:#f5f5f5">...</div>` |

### 4.6 access_token 缓存策略

- 文件路径：`~/.cache/ni-skill/wechat_token.json`
- 格式：`{"token": "xxx", "expires_at": 1747xxx}`
- 微信返回 `expires_in=7200`，我们存 `now + 7000`（留 200s buffer）
- 文件锁（`fcntl` on Unix，`msvcrt` on Windows）防并发拿 token
- 失效自动重拿，不要求用户介入

### 4.7 测试样例

`tests/fixtures/` 提供：
- `sample-article.md`（含 5 个排版模块全集）
- `expected-html.html`（对应的微信兼容 HTML）
- `mock-wechat-response.json`（模拟成功/40001/45004 三种响应）

离线测试只跑 markdown→HTML 部分，**不**调真微信 API。
真实推送测试由用户在自己的公众号上手动验证。

### 4.8 升级路径

P1 阶段加图片上传时：
- 在 `scripts/` 新增 `image_upload.py`（约 80 行）
- `wechat_draft.py` 增加 `upload-image` 子命令
- 不破坏现有 `create` 命令的接口

---

## 第五章 实现优先级与里程碑

### 5.1 优先级

| 优先级 | Skill | 理由 |
|--------|-------|------|
| **P0-1** | ni-article-workflow（骨架） | 没有它就没有套件，先把状态机和共享约定立起来 |
| **P0-2** | ni-insight | 灵魂 skill，是套件的差异化所在，最早验证 prompt 设计 |
| **P0-3** | ni-formatter（5 模块） | 排版最小集，验证"穿衣"概念 |
| **P0-4** | ni-draft（无图） | 完成发布闭环 |
| **P1-1** | ni-research | 当前可临时用 WebSearch 手工替代 |
| **P1-2** | ni-inspect | ni-writer 自带四层自检暂时够用 |
| **P1-3** | ni-article-image-gen | 配图可手工生成 |

### 5.2 里程碑

| 里程碑 | 交付 | 验收 |
|--------|------|------|
| **M1（骨架）** | DESIGN.md + ni-article-workflow SKILL.md 骨架 + 目录结构 | workflow 能空跑一遍（每步只打印"调用 xxx skill"） |
| **M2（灵魂）** | ni-insight 完整可用 | 给一个 research.md 能产出 insight.md，三模板触发正常 |
| **M3（穿衣）** | ni-formatter 5 模块完整 | 给 article.md 能产出含 5 模块的 formatted.md |
| **M4（发布）** | ni-draft 裁剪完成 | 能把 formatted.md 推上草稿箱 |
| **M5（P0 闭环）** | 用真实选题走通 init → done | 在公众号后台看到草稿 |
| **M6+（P1）** | ni-research / ni-inspect / ni-article-image-gen | 替换 P0 阶段的手工替代 |

### 5.3 风险与对策

| 风险 | 对策 |
|------|------|
| ni-insight 的角度挖掘 prompt 效果不达预期 | M2 用 3 个真实选题做 A/B 测试，调 prompt 直到通过朋友圈测试 |
| md2wechat 裁剪超出预算 | 退化为薄壳调用整个 md2wechat 二进制，只用 draft 子命令 |
| 共享约定在原子 skill 单独调用时被违反 | 在 workflow 入口做契约校验，原子 skill 不需要懂约定 |
| ni-formatter 5 模块不够用 | 按需补加，但每补一个走 G1 审视（"真的必要吗？"） |

---

## 第六章 评审决策记录

所有蓝图级决策已落定：

1. ✅ 5 个 ni-formatter 正文模块（part / callout / quote / steps / verdict）
2. ✅ 共享约定仅在 workflow 模式下强制；原子 skill 单独调用时不硬编码路径
3. ✅ 蓝图级粒度（本文件不含完整 SKILL.md）
4. ✅ 各 skill references 独立持有（不抽 shared 目录）
5. ✅ ni-draft 采用 **Python 内嵌**（不依赖 md2wechat）
6. ✅ article-name **用户手动指定**（kebab-case + workflow 强制校验）
7. ✅ 工作目录单位命名采用 `article-name`（替代原方案 `slug`）

---

## 附录 A：与 SPEC.md 的差异

| 项 | SPEC.md | 本设计书 | 理由 |
|----|---------|---------|------|
| ni-formatter 模块数 | 43 个模块全集 | 正文 5 个最小集 | P0 收紧，符合 G1 |
| ni-draft 图片上传 | 完整支持 | P0 不做，要求预传 media_id | 压缩 P0 范围 |
| ni-draft 技术栈 | 未明确 | Python 内嵌，零外部二进制依赖 | 用户决策 |
| 套件编排 | 未明确 | 新增 ni-article-workflow | 用户决策 |
| 共享约定 | 未明确 | 仅 workflow 模式强制 | 用户决策 |
| 套件基因 | 隐式 | 显式 5 条 G1-G5 | 用户决策 |
| 工作目录单位 | 未明确 | `article-name`（用户手动指定） | 用户决策 |

## 附录 B：术语

| 术语 | 定义 |
|------|------|
| 套件基因 | 全 skill 强制遵守的元规范（G1-G5） |
| 共享约定 | workflow 模式下的工作目录与接口契约 |
| article-name | 一篇文章在 drafts/ 下的目录名，由用户手动指定，kebab-case，≤40 字符 |
| 灵魂 | ni-insight 输出的"一句话核心论点" |
| 穿衣 | ni-formatter 的排版意图注入过程 |
| 降级 | 外部依赖不可用时的兜底处理（必须显式标注） |
| 朋友圈测试 | ni-insight 灵魂验收的最终测试（"发朋友圈会有人评论吗？"） |
