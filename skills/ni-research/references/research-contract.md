# research.md 契约

```yaml
schema_version: 1
mode: collaborative
research_status: draft # draft|ready_for_discussion|user_confirmed|autonomous_ready|blocked
topic_id: null
radar_report: null
source_manifest: null
research_revision: 1
confirmed_revision: null
confirmation_record: null
blocking_issues: []
```

`ready_for_discussion` 表示研究已完成并可讨论，不代表用户认可，也不授权策划或写作。`user_confirmed` 必须有用户明确确认记录，且 `confirmed_revision` 等于当前版本。自主模式只允许 `autonomous_ready`，不能填写用户确认。中心结论不成立可正常交付否定结论；关键证据缺失导致无法回答则标记 `blocked`，并解释为什么不能成文。

正文包含：

1. 研究问题、范围、概念、约束与初始假设。
2. 直接回答与把握程度：明确结论和推理链，区分证据不足与证据反驳。
3. 机制解释；按需包含理论原义、历史比较及类比失效边界。
4. 主张与证据账本。
5. 竞争解释、失败案例、反证与冲突处理。
6. 适用条件、代价、未知及下一步最小验证。
7. 查询记录、实际来源覆盖、失败路径和停止理由。

证据账本每项记录：主张 ID、具体主张、状态（已核实事实／来源解释／本次推断／待核实）、原始 URL、作者与标题、发布日期或版本、访问时间、原文位置或短摘录、支持力度与限制、同源关系。本次推断必须指向支撑它的主张 ID，并交代推导过程。有链接不等于核实，原文必须支持所述内容。

来源分为 `A-official`（产品或机构自身声明）、`B-original`（原始研究、实验、实践记录与当事人表述）、`C-secondary`（二手解释和线索）。等级不等于真理；记录各自能支撑的范围。关键理论允许原著或原始论文，不能把仅有官方产品说明当成唯一合格来源。

交付门禁：核心问题已有证据支持的回答；竞争解释与边界已检查；引用可追溯；同源材料未重复计票；无法消解的冲突与未知已标明。关键缺口写入 `blocking_issues`，不得用数量或具名率抵消。

修改中心结论、关键证据或适用范围时递增 `research_revision`，清空确认，并令旧大纲失效。大纲记录所依据的 `research_revision`；发现版本不匹配必须重审，不能沿用旧确认。保存新版本，保留旧文件和确认记录供复查。
