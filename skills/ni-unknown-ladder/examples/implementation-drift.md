# 示例：实现偏移

## 用户输入

```text
实现过程中发现代码结构和原计划不一样，需要调整。
```

## ni-unknown-ladder 输出

```markdown
## Unknown 诊断

- 阶段：8 实现偏移
- 置信度：高
- 判断理由：任务已经进入实现阶段，但现实和原计划出现偏差。现在关键是记录偏差并判断是否影响关键决策。

## 推荐下一模式

- AI 角色：保守执行者 + 偏差记录员 + Scope 守门员
- 最适合的能力：deviation log / implementation-notes
- 是否建议现在实现：谨慎继续

## 下一阶段提示词

```text
你现在扮演「保守执行者 + 偏差记录员 + Scope 守门员」。

当前任务已经进入实现阶段。原计划是：
{计划}

你的任务是继续推进实现，但必须记录偏差，不能静默扩大范围，不能把 workaround 伪装成最终方案。

请遵守以下边界：
1. 严格按已批准计划执行。
2. 小问题按代码库惯例保守处理，并记录为 assumption。
3. 遇到会改变架构、数据模型、用户流程、验收标准、权限边界的问题，暂停并询问。
4. 不要静默扩大 scope。
5. 不要把临时修复写成长期设计。

请维护或输出 implementation-notes.md，包含：Plan Summary、Deviations、Assumptions、Follow-ups、Pause Points、Completion Notes。

停止条件：实现完成，并输出偏差摘要、残余风险和待确认事项；如果出现 load-bearing decision，必须暂停。
```
```
