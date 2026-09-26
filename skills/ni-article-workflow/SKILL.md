---
name: ni-article-workflow
description: |
  编排公众号 AI 技术文章从选题雷达、选题、来源归档、深度研究、研究讨论、观点与大纲、实践边界到正文初稿的完整生产链路。支持用户在场的 collaborative 模式和无人值守的 autonomous 模式；逐阶段验收产物并记录门禁，只在条件满足时调用 ni-writer 生成 article-draft.md，随后停止。
---

# ni-article-workflow — 公众号文章初稿生产编排

你是生产编排器，不替代各原子 Skill。你的职责是传递明确输入、维护状态、验收每个阶段产物、阻断越级执行，并把一篇已选主题稳定推进到 `article-draft.md`。

## 流程边界

本流程包含：

1. `ni-radar weekly` 生成本周选题报告；
2. 用户选择或工作流按规则选择一个主题；
3. 确保关键来源已归档为本地可读 Markdown；
4. `ni-research stage: research` 生成 `research.md`，协作模式先讨论并确认研究结论；
5. `ni-research stage: outline` 把观点与大纲聊透，生成 `article-outline.md`；
6. 明确实践边界并检查研究、大纲与实践的一致性；
7. `ni-writer` 生成 `article-draft.md`；
8. 验收初稿并停止在 `draft_ready`。

本流程不负责正文终审、优化定稿、封面、配图、排版、公众号草稿箱、定时或发布。`draft_ready` 表示初稿可交给人审，不表示成稿或发布就绪。

## 默认内容范围

- AI 工程实践
- AI DevOps / CI/CD 实践
- Agent 工程与多智能体协作
- AI-Native 研发体系与小团队自动化
- AI 时代的工程判断

最终范围以用户输入和素材池真实内容为准。工具、公司、模型和新闻只是素材，不自动成为长期内容支柱。

## 运行模式

### `collaborative`

交互调用的默认模式：

- 用户从本周报告中明确选择主题；
- `ni-research` 先交付研究，取得当前版本的 `research_status: user_confirmed`，再与用户分轮讨论大纲，并得到 `outline_status: user_confirmed`；
- 用户明确表示“可以写正文”“开始成稿”或等价授权后，才允许写初稿。

需要用户决定时进入 `pending_user`。不得因等待超时自行切换到自主模式。

### `autonomous`

仅当本次调用或持久化配置明确提供以下状态时启用：

```yaml
mode: autonomous
run_to_draft: true
```

- 工作流只能选择 `ni-radar` 明确标记为主推且通过雷达门禁的最高优先级主题；
- `ni-research` 自行生成并筛选观点，产出 `outline_status: autonomous_ready`；
- `run_to_draft: true` 只授权生成本地初稿，不代表用户确认观点、定稿或发布；
- 没有精确归档目录、合格主推主题或可追溯证据时停止为 `blocked`，不能为了无人值守而降低标准。

## 阶段与验收门禁

每个阶段遵守同一顺序：读取上游产物，执行当前阶段，写出产物，运行门禁，把 PASS / FAIL / WAITING 及证据写入 `gate-report.md`，最后才更新 `state.yaml`。门禁未通过时不得进入下一阶段。

### 1. `radar`

调用 `ni-radar weekly`。门禁：

- 报告文件存在且可读；
- 报告记录完整 21 天编辑窗口和 X / 关联原文最近 14 天检索窗口；
- 候选只使用可核验的一手来源，并完成时间、重复和内容范围筛选；
- 至少一个主推候选同时具备明确方法、证据潜力和公众号写作价值。

强候选不足 5 个时可标记 `degraded`，但只能保留真实过线候选。没有主推候选时门禁失败。

### 2. `selection`

生成 `topic-selection.md`。门禁：

- 协作模式：用户明确选定主题，记录 `selection_origin: user`；
- 自主模式：选择报告中排序最高的合格主推，记录 `selection_origin: workflow`；
- 记录候选编号、报告路径、核心话题、推荐理由、原始来源和重复检查结果；
- 一次运行只选择一个文章任务。

Agent 推荐不等于用户在协作模式下已经选择。

### 3. `source`

复用已有归档，或调用 `ni-radar archive` / `ni-url2md` / `ni-video2md` 获取本地原始素材，生成 `source-manifest.md`。门禁：

- 每个影响核心结论的来源都有本地可读 Markdown；
- 清单记录原始 URL、作者、发布日期、来源等级、本地绝对路径和文件哈希；
- 来源正文与元数据可追溯，不以搜索摘要代替原文；
- 新归档只能写入用户或工作流配置提供的精确路径，且不得静默覆盖。

自主模式缺少 `source_archive.path` 时，不自行猜测 `/素材收集库/{第几周}/`，直接阻断。已有本地归档满足门禁时不重复抓取。

### 4. `research`

调用 `ni-research stage: research`，生成 `research.md`。门禁：

- 问题、定义、机制、竞争解释、反证、适用边界与未知项清楚；
- 中心事实能追溯到已读的 A-official 或 B-original 原始来源；理论与历史材料按主张适配来源，不受 radar 近期窗口限制；
- 主张与证据账本包含来源、时间或版本、原文位置、支持力度和同源关系；
- 未核实内容不会影响正文结论；关键缺口仍在时为 blocked，不策划大纲。

协作模式先以 `ready_for_discussion` 交付并进入 `pending_user`。调用 `ni-research stage: discussion` 讨论后，只有明确确认当前研究版本，才接受 `research_status: user_confirmed`。用户修改中心判断时定向补查并重新确认。自主模式通过同样证据门禁后使用 `research_status: autonomous_ready`，不得冒充用户确认。研究不支持成文时正常交付研究并停止，不硬凑大纲。

### 5. `outline`

调用 `ni-research stage: outline`，生成 `article-outline.md`。门禁：

- 协作模式研究已确认，且大纲必须为 `user_confirmed`；
- 自主模式研究和大纲均为 `autonomous_ready`，且 `opinion_origin: agent_synthesis`；
- 大纲指向当前研究版本，包含唯一核心任务、读者、观点与来源边界、完整结构、风格、预计篇幅和章节证据；
- 没有未核实中心事实、虚构用户立场或伪造第一人称实践；核心论点未与近期文章重复。

大纲为 draft 或 blocked 时不得继续。出现改变中心判断的新主张时退回 research；旧研究确认和大纲确认失效。表达调整不要求重复整轮研究。

### 6. `practice`

生成 `practice-record.md` 并检查与研究、大纲的一致性。门禁：

- 状态只能是 `verified`、`not_required`、`source_only` 或 `blocked`；
- `verified` 必须记录实践来源、时间、输入、动作、结果和可复查证据；
- 自主模式只有在调用前已存在可复查的用户实践记录时才能使用 `verified`；
- `source_only` 不得把外部案例写成用户亲历；
- 研究、大纲与实践不存在未解决冲突；主题依赖未完成实测时阻断，或退回 research / outline 收窄判断并重新确认。

`blocked` 禁止进入写作。实践核验发现中心结论变化时，不能只改实践记录而沿用已确认的大纲。

### 7. `draft`

写作授权门禁：

- 协作模式必须记录用户本次明确授权，`authorization_origin: user`；
- 自主模式必须从初始调用或持久化配置读取 `run_to_draft: true`，记录 `authorization_origin: workflow_config`。

通过后调用 `ni-writer`，明确指定输入为 `article-outline.md`、`research.md`、`practice-record.md`，输出为 `article-draft.md`。初稿门禁：

- 文件存在、非空，没有未完成占位符或聊天残留；
- 只完成大纲中的一个核心任务，章节与论证没有实质偏离；
- 影响结论的事实、数字、案例和判断都能映射到研究或实践记录；
- 自主模式没有把 `agent_synthesis` 写成用户亲历、用户测试或用户立场；
- 正文只保留影响结论的关键链接，其余来源留在 `research.md`；
- 未引入大纲与研究之外的新事实主张。

第一次失败时，只允许把明确失败项交给 `ni-writer` 修复一次。第二次仍失败则标记 `draft.status: blocked` 并停止，避免无限自修复。

## 状态机

```text
intake
  |
radar -------- blocked / degraded
  |
selection ---- pending_user / blocked
  |
source ------- blocked
  |
research ----- pending_user / blocked
  |
outline ------ research / pending_user / blocked
  |
practice ----- research / outline / blocked
  |
draft -------- pending_user / blocked
  |
draft_ready
```

`pending_user` 是协作门禁，不是失败。`degraded` 只允许表示数量不足但仍有合格主推，不允许降低单项质量门槛。

## 产物与交接

工作目录固定为 `drafts/{article-name}/`，详细字段见 `references/state-schema.md`。

| 阶段 | 调用能力 | 主要输入 | 主要产物 |
|---|---|---|---|
| `radar` | `ni-radar weekly` | 素材库、关注范围、发布日志 | 本周选题报告 |
| `selection` | 用户决定或自主选择规则 | 本周报告 | `topic-selection.md` |
| `source` | `ni-radar archive` 等来源提取能力 | 已选主题、精确归档目录 | 原始 Markdown、`source-manifest.md` |
| `research` | `ni-research stage: research / discussion` | 已选问题、来源、模式 | `research.md` 与研究确认 |
| `outline` | `ni-research stage: outline` | 当前研究、用户讨论、实践边界 | `article-outline.md` |
| `practice` | 用户记录或既有实践资料 | 大纲中的实践依赖 | `practice-record.md` |
| `draft` | `ni-writer` | 大纲、研究、实践记录 | `article-draft.md` |

每个阶段还要更新 `gate-report.md` 和 `state.yaml`。完整来源保留在研究文件，正文只保留影响结论的关键链接。

## 稳定运行规则

1. 每次运行先读取 `state.yaml`、`gate-report.md` 和当前阶段产物，从未通过阶段继续，不重复执行已通过阶段。
2. 调用原子 Skill 时传递显式模式、输入绝对路径、输出绝对路径和不可越过的状态字段。
3. 先生成阶段产物，再验收；只有验收通过后才把阶段状态改为 `passed`。
4. 为输入和输出记录 SHA-256。上游产物变化时，将所有下游阶段标为 `stale`，保留旧文件供审计，但禁止复用。
5. 已通过产物不静默覆盖。确需重跑时保存新版本并更新 manifest、哈希和原因。
6. 外部访问失败、来源不完整或原子 Skill 返回异常时记录原始错误摘要，标记 `blocked`；不伪装成功。
7. 同一阶段最多自动重试一次。只有明确的临时错误可重试；事实缺失、用户决定和配置缺失不能靠重试解决。
8. `state.yaml`、产物和 `gate-report.md` 不一致时，以最保守状态为准并停下修复状态，不越级执行。

## 回退

- 选题来源失效或日期不成立：退回 `radar` 或 `selection`。
- 归档素材与报告摘要不一致：退回 `source`，重新核对原文。
- 证据推翻中心观点：退回 `research`，更新结论后再走 `outline`；协作模式重新确认，自主模式重新比较观点。
- 上游文件发生变化：下游全部标记 `stale`，从最早受影响阶段重跑。
- 初稿门禁失败：按失败项定向修复一次；仍失败则阻断。

## 完成标准

只有以下条件同时满足，才能标记 `phase: draft_ready`：

- `topic-selection.md` 通过选题门禁；
- `source-manifest.md` 通过来源门禁；
- `article-outline.md` 为 `user_confirmed` 或 `autonomous_ready`；
- `practice-record.md` 的状态允许写作；
- `research.md` 通过研究门禁，且确认对应当前版本；
- `article-draft.md` 通过初稿门禁；
- `gate-report.md` 中所有必要阶段均为 PASS；
- `state.yaml` 的路径、状态和哈希与实际产物一致。

完成后返回模式、选题、初稿路径、各门禁状态和仍需人工审阅的风险，然后停止。

## 参考

- `references/state-schema.md`：共享状态、阶段产物、门禁记录和跨 Agent 接口。
