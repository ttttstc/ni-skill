# ni-insight — `article-outline.md` 契约

`collaborative` 与 `autonomous` 必须输出同一种大纲。下游只根据状态和字段判断是否可写，不根据自然语言猜测。

## 顶部状态

```yaml
schema_version: 2
authorship_mode: collaborative        # collaborative|autonomous
opinion_origin: user                  # user|mixed|agent_synthesis
outline_status: draft                 # draft|user_confirmed|autonomous_ready|blocked
topic_id: null
topic_title: ""
radar_report: ""
source_manifest: ""
practice_status: pending              # pending|verified|not_required|source_only|blocked
created_at: ""
updated_at: ""
blocking_issues: []
```

状态含义：

- `draft`：仍需用户确认或存在不阻断结构讨论的缺口；
- `user_confirmed`：协作模式下用户已确认核心内容、完整结构和风格；
- `autonomous_ready`：自主模式已完成观点比较和机器门禁，可以交给工作流判断是否写初稿；
- `blocked`：中心事实、来源、实践或文章任务不成立，禁止写作。

`autonomous` 必须使用 `opinion_origin: agent_synthesis`。只有协作模式可以使用 `user` 或 `mixed`。

## 正文结构

```markdown
# {工作标题}

## 1. 文章任务

- 目标读者：
- 读者当前问题：
- 核心观点或核心价值：
- 读完后的判断变化或可执行动作：
- 本文明确不解决：

## 2. 选题与观点来源

- 选题报告与候选编号：
- 观点形成方式：用户确认 / 用户与编辑共同收敛 / Agent 综合判断
- 采用这个观点的原因：
- 未采用的候选观点及原因：

## 3. 作者位置与声明边界

- 用户确认的观点：
- Agent 综合判断：
- 来源作者的观点：
- 可以写成第一人称的实践：
- 只能归因给来源的实践：
- 推断与未知：
- 不准备声称的内容：

## 4. 证据与实践

- 关键事实和对应来源：
- 可用数字、代码、截图、日志或案例：
- 反例、代价和成立边界：
- 实践状态与依据：
- 仍需核验但不影响中心结论的事项：
- 会阻断写作的事项：

## 5. 写作决策

- 文章原型：
- 原型选择理由：
- 风格确认：
- 第一人称强度：
- 技术细节深度：
- 预计篇幅：
- 正文链接策略：只保留影响结论的关键链接

## 6. 完整结构

### 第 1 节：{小标题或功能名}

- 本节目的：
- 核心内容：
- 展开顺序：
- 来源与证据：
- 用户观点 / Agent 综合判断 / 来源观点：
- 边界与避免声称：
- 与前后文的关系：
- 预计篇幅：

{按同一格式列出全部章节}

## 7. 写作前任务

- 必须完成：
- 可选增强：
- 明确放弃：

## 8. 大纲门禁

- [ ] 只有一个核心任务
- [ ] 目标读者与价值明确
- [ ] 观点归属清楚
- [ ] 每节都有证据或明确标注的综合判断
- [ ] 实践状态不阻断写作
- [ ] 没有未核实的中心事实
- [ ] 没有重复近期文章的核心论点
- [ ] 完整结构、风格确认和预计篇幅齐全
```

## 验收规则

- 清单全部通过，且 `blocking_issues` 为空，状态才能设为 `user_confirmed` 或 `autonomous_ready`。
- `user_confirmed` 必须对应用户明确确认记录。
- `autonomous_ready` 必须保留 2–4 个观点候选的比较结果；不能只留下获选结论。
- 每一节必须写出来源或观点归属。只写章节标题不算完整结构。
- 会改变中心结论的证据或实践缺口必须进入 `blocking_issues`。
- 大纲不是正文写作授权；授权由 `ni-article-workflow` 单独记录。
