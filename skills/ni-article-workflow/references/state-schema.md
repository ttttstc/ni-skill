# 公众号文章初稿生产共享契约

本契约供 `ni-article-workflow` 与配置到同一条 Multica 生产链路的 Agent 使用。原子 Skill 单独调用时不能假设其他阶段已完成，也不能自行把状态标为通过。

## 工作目录

```text
drafts/
└── {article-name}/
    ├── state.yaml
    ├── gate-report.md          # 各阶段验收证据
    ├── topic-selection.md      # 用户选择或工作流自主选择的主题
    ├── source-manifest.md      # 指向精确归档目录中的原始素材
    ├── article-outline.md      # user_confirmed 或 autonomous_ready
    ├── practice-record.md      # 实践、验证或 source_only 边界
    ├── research.md             # 深化研究与证据账本
    ├── article-draft.md        # 等待人工审阅的正文初稿
    └── logs/
        └── {stage}-{timestamp}.log
```

本周报告和原始素材不复制进草稿目录作为第二份真源。`state.yaml` 记录报告绝对路径，`source-manifest.md` 指向用户或工作流配置指定的归档目录。

## `state.yaml`

```yaml
schema_version: 4
article_name: example-article
created_at: 2026-09-05T10:00:00+08:00
updated_at: 2026-09-05T10:00:00+08:00

mode: collaborative               # collaborative|autonomous
run_to_draft: false               # autonomous 进入 draft 的显式授权

# intake|radar|selection|source|insight|practice|evidence|draft|draft_ready|blocked|pending_user
phase: intake

radar_report:
  path: null
  period_start: null
  period_end: null
  x_period_start: null
  x_period_end: null
  candidate_count: 0
  recommendation_count: 0

selection:
  status: pending                 # pending|selected|blocked
  origin: null                    # user|workflow
  candidate_id: null
  topic: null
  artifact: topic-selection.md

content:
  pillar: null
  title_working: null
  article_archetype: null

source_archive:
  path: null                      # 新归档必须显式配置；不猜默认周目录
  source_archived: false
  manifest: source-manifest.md
  items: []

outline:
  path: article-outline.md
  status: draft                   # draft|user_confirmed|autonomous_ready|blocked
  authorship_mode: null           # collaborative|autonomous
  opinion_origin: null            # user|mixed|agent_synthesis

practice:
  status: pending                 # pending|verified|not_required|source_only|blocked
  artifact: practice-record.md

evidence:
  status: pending                 # pending|ready|conflict|blocked
  artifact: research.md

draft:
  authorized: false
  authorization_origin: null      # user|workflow_config
  status: pending                 # pending|in_progress|ready|blocked
  artifact: article-draft.md
  attempts: 0                     # 最多 2：初写一次，定向修复一次

stages:
  radar:
    status: pending               # pending|in_progress|passed|degraded|blocked|stale
    artifact: null                # 绝对路径；本周报告不复制到 drafts
    input_fingerprint: null
    output_sha256: null
    validated_at: null
  selection:
    status: pending
    artifact: topic-selection.md
    input_fingerprint: null
    output_sha256: null
    validated_at: null
  source:
    status: pending
    artifact: source-manifest.md
    input_fingerprint: null
    output_sha256: null
    validated_at: null
  insight:
    status: pending
    artifact: article-outline.md
    input_fingerprint: null
    output_sha256: null
    validated_at: null
  practice:
    status: pending
    artifact: practice-record.md
    input_fingerprint: null
    output_sha256: null
    validated_at: null
  evidence:
    status: pending
    artifact: research.md
    input_fingerprint: null
    output_sha256: null
    validated_at: null
  draft:
    status: pending
    artifact: article-draft.md
    input_fingerprint: null
    output_sha256: null
    validated_at: null

user_decisions: []
degradations: []
blockers: []
```

## 统一阶段状态

- `pending`：尚未执行；
- `in_progress`：正在生成产物，门禁尚未运行；
- `passed`：产物和门禁均通过；
- `degraded`：数量或外部覆盖不足，但至少一个候选满足全部质量条件；只允许用于 `radar`；
- `blocked`：存在不能自动越过的问题；
- `stale`：上游输入已变化，旧产物仅供审计，不得继续使用。

`phase` 表示下一步要执行或当前等待的阶段。它不能单独证明上游门禁已经通过。

## `gate-report.md`

每个阶段追加或更新一个固定小节：

```markdown
## {stage}

- status: PASS | FAIL | WAITING | DEGRADED
- mode: collaborative | autonomous
- checked_at: {ISO 8601}
- inputs:
  - {absolute path} | sha256: {hash}
- artifact: {absolute path} | sha256: {hash}
- checks:
  - PASS | {检查项} | {证据}
  - FAIL | {检查项} | {原因}
- next_action: {下一步或阻断条件}
```

只写“已检查”不算证据。路径、字段值、来源等级、状态或失败项必须可复查。

## 各阶段最小验收

### `radar`

- 报告可读，时间窗口和候选数量可解析；
- 至少一个一手来源、非重复、方法密度充足的主推；
- 不足 5 个强候选时明确 `DEGRADED`，不填充弱项。

### `selection`

- `topic-selection.md` 记录报告、候选、来源和选择原因；
- `collaborative` 的 `origin` 必须为 `user`；
- `autonomous` 的 `origin` 必须为 `workflow`，且候选为最高优先级合格主推。

### `source`

- `source-manifest.md` 中每个关键来源都有 URL、作者、发布日期、等级、本地绝对路径和 SHA-256；
- 本地文件真实存在且可读；
- 新归档目录来自显式配置。

### `insight`

- 协作模式：`outline.status: user_confirmed`；
- 自主模式：`outline.status: autonomous_ready`、`opinion_origin: agent_synthesis`；
- 完整大纲中不存在阻断项或虚构用户实践。

### `practice`

| 值 | 允许继续 | 写作限制 |
|---|---:|---|
| `verified` | 是 | 只使用记录中可复查的第一人称实践，不扩大结论 |
| `not_required` | 是 | 文章不依赖用户亲自实践 |
| `source_only` | 是 | 外部案例必须明确归因，不写成用户亲历 |
| `pending` | 否 | 协作模式等待用户；自主模式改选或阻断 |
| `blocked` | 否 | 禁止进入证据与初稿阶段 |

### `evidence`

- `research.md` 存在并覆盖全部中心主张；
- 来源等级为 A-official 或 B-original；
- 与大纲、实践记录没有未解决冲突；
- 未核实项不影响文章结论。

### `draft`

- 协作模式由用户授权；自主模式由初始 `run_to_draft: true` 授权；
- `article-draft.md` 存在且非空；
- 结构、观点归属、证据和第一人称边界符合上游产物；
- 仅保留影响结论的关键链接；
- 没有占位符、聊天残留或未追溯的新事实；
- `draft.attempts` 不超过 2。

## 阶段接口

| 阶段 | 输入 | 输出 | 必须写回 |
|---|---|---|---|
| radar | 素材库、用户范围、关注博主、发布日志 | 本周选题报告 | `radar_report.*`、radar gate |
| selection | 本周报告、用户决定或自主规则 | `topic-selection.md` | `selection.*`、selection gate |
| source | 已选主题、直接来源、精确归档目录 | 原始文件、`source-manifest.md` | `source_archive.*`、source gate |
| insight | 报告、选题、归档素材、运行模式 | `article-outline.md` | `outline.*`、insight gate |
| practice | 大纲、用户实践或既有记录 | `practice-record.md` | `practice.*`、practice gate |
| evidence | 大纲、归档素材、实践记录 | `research.md` | `evidence.*`、evidence gate |
| draft | 已授权的大纲、研究、实践记录 | `article-draft.md` | `draft.*`、draft gate |

原子 Skill 只负责生成自己的产物。编排器验收后才能把对应阶段改为 `passed`。

## 一致性与失效

- `input_fingerprint` 是按固定顺序拼接上游文件 SHA-256 后得到的 SHA-256；模式和关键配置也要纳入。
- 当前输入指纹与上次不一致时，本阶段及下游阶段全部标记 `stale`。
- 文件哈希与 `output_sha256` 不一致时，不接受已有 PASS，重新验收。
- `state.yaml`、`gate-report.md` 和文件实况冲突时，以最保守状态为准。
- 旧产物不删除、不覆盖；版本化保存并在 manifest 中说明替代关系。

## 关键链接约定

`research.md` 保存完整来源清单。正文只允许保留会影响结论的关键链接：

- 直接改变读者结论的官方来源；
- 读者必须复查的原始案例、代码、文档或定价页；
- 证明关键数字或事实的来源。

其余链接留在研究文件，不复制进正文。
