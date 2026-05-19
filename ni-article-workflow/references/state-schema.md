# 共享约定：工作目录、state.yaml、接口契约

> 本文定义 ni-article-workflow 编排模式下的共享约定。**这套约定只在 workflow 模式下生效**——原子 skill 单独调用时不遵守，由 workflow 调用时注入路径参数。

---

## 1. 工作目录布局

每篇文章一个目录，目录名是用户手动指定的 `article-name`。

```
drafts/
└── {article-name}/                 # kebab-case，≤40 字符
    ├── state.yaml                  # 状态机，workflow 独占读写
    ├── research.md                 # ni-research 产物
    ├── insight.md                  # ni-insight 产物
    ├── article.md                  # ni-writer 产物
    ├── formatted.md                # ni-formatter 产物
    ├── inspect-report.md           # ni-inspect 产物
    ├── images/                     # ni-article-image-gen 产物
    │   ├── cover-prompts.md
    │   └── inline-prompts.md
    ├── draft-meta.yaml             # ni-draft 产物（含 draft media_id）
    └── logs/                       # 各 skill 执行日志
        └── {step}-{timestamp}.log
```

`drafts/` 整个目录已加入 `.gitignore`——草稿产物不入库。

---

## 2. article-name 校验规则

workflow 启动时询问用户，并强制校验：

| 规则 | 处理 |
|------|------|
| 只允许 `[a-z0-9-]` | 含其他字符 → 报错让用户重输 |
| 长度 1-40 | 超出 → 报错重输 |
| 用户给中文 | 提示「请用英文 kebab-case，例如 how-to-evaluate-ai-coding-tools」 |
| `drafts/{article-name}/` 已存在 | 问「续跑这篇 / 换个名 / 覆盖」 |

---

## 3. state.yaml schema

```yaml
article_name: how-to-evaluate-ai-coding-tools
created_at: 2026-05-19T10:00:00+08:00
updated_at: 2026-05-19T11:23:00+08:00

# 当前阶段：init|research|insight|writing|formatting|inspect|imaging|draft|done|failed
phase: writing

# 每个阶段的结果
stages:
  research:
    status: done            # pending|in_progress|done|skipped|failed|degraded
    started_at: 2026-05-19T10:05:00+08:00
    finished_at: 2026-05-19T10:20:00+08:00
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
    started_at: 2026-05-19T10:45:00+08:00
  formatting:
    status: pending
  inspect:
    status: pending
  imaging:
    status: pending
  draft:
    status: pending

# 用户决策记录（每次需要用户确认时落盘）
user_decisions:
  - at: 2026-05-19T10:30:00+08:00
    stage: insight
    question: "三个角度选哪个？"
    answer: "角度 2（反转型）"

# 降级记录
degradations:
  - at: 2026-05-19T11:00:00+08:00
    stage: research
    reason: "WebSearch 不可用，降级到 LLM 训练数据采集"
```

### 字段说明

| 字段 | 说明 |
|------|------|
| `phase` | 当前阶段，断点续跑读这个 |
| `stages.{name}.status` | pending / in_progress / done / skipped / failed / degraded |
| `stages.{name}.artifact` | 该阶段产物的相对路径 |
| `stages.insight.soul_one_liner` | 核心论点，下游 ni-writer / ni-formatter 要用 |
| `stages.insight.selected_angle` | 用户选定的角度类型 |
| `user_decisions` | 所有需用户确认处的决策留痕 |
| `degradations` | 所有降级事件，供用户复盘 |

`state.yaml` 由 workflow **独占读写**。原子 skill 不碰它。

---

## 4. 接口契约

workflow 调用每个原子 skill 时按以下模式注入参数：

```
触发 {skill_name}：
- workdir: drafts/{article-name}/
- inputs:
    - {上游产物的相对路径，如 research.md}
    - {从 state.yaml 提取的关键字段，如 soul_one_liner}
- output_path: drafts/{article-name}/{产物文件名}
- on_success: workflow 写回 state.yaml 对应 stage（status: done, artifact: ...）
- on_failure: 走该 skill 的降级路径，workflow 标 degraded=true 并记 degradations
```

### 各阶段的输入输出

| skill | 输入 | 输出 | 写回 state 的关键字段 |
|-------|------|------|---------------------|
| ni-research | 选题关键词 | research.md | notes（素材数等） |
| ni-insight | research.md | insight.md | soul_one_liner, selected_angle |
| ni-writer | research.md + insight.md（核心论点作「独特视角」注入） | article.md | — |
| ni-formatter | article.md + insight.md（取 soul_one_liner 定位 verdict） | formatted.md | — |
| ni-inspect | formatted.md | inspect-report.md | readiness |
| ni-article-image-gen | article.md + insight.md | images/cover-prompts.md, images/inline-prompts.md | — |
| ni-draft | formatted.md + 标题 + 摘要 + 封面 media_id（可选） | draft-meta.yaml | draft_media_id |

---

## 5. ni-writer 适配契约

ni-writer 是已存在 skill，不改它的 SKILL.md。workflow 调用时：

- 把 `insight.md` 的 `soul_one_liner` + 支撑逻辑 + 预判反驳作为「独特视角」整体传入。
- 明确告知 ni-writer：独特视角已定，**跳过其 SKILL.md 第二步「独特视角询问」**。
- ni-writer 的四层自检 L1-L4 不动，照常执行并产出自检报告。

workflow 读 ni-writer 的 L4 自检结果：通过 → formatting；不通过 → 留在 writing。

---

## 6. 原子 skill 单独调用时

原子 skill 不依赖本约定。单独调用时：

- 输入靠用户粘贴内容或给文件路径。
- 输出落到用户指定路径或 skill 默认路径。
- 不读写 `state.yaml`，不假设 `drafts/` 存在。

契约校验只在 workflow 入口做。原子 skill 不需要懂这套约定——这是「共享约定仅在 workflow 模式下强制」的落点。
