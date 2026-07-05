# ni-unknown-ladder

`ni-unknown-ladder` 是一个用于 Claude Code / Claude Skills 的 **Vibe Coding 未知阶段诊断器**。

它不替代 `brainstorming`、`office-hours`、`grill-me`、`review`、`qa` 等具体 skill，而是作为开工前、中、后的“分诊台”：

1. 判断你当前面对的是哪一类 unknown；
2. 推荐下一步 AI 应该进入什么协作模式；
3. 输出一段中文、可复制的下一阶段提示词。

## 版本

当前版本：`0.4.0`

本版重点增强：

- 增加 **基于上下文的重新诊断**：后续调用会复盘已确认事实、已解决 unknown、待处理 unknown 和新出现 unknown；
- 增加 **多重 unknown 队列**：允许识别多个 unknown，但每次只推进一个主 unknown；
- 增加 **unknown 关闭条件**：处理完最优先 unknown 后，再次调用会判断是否可推进到下一个 unknown；
- 增加 **轻量状态管理规则**：默认不写文件；可选写入用户全局目录；项目内状态必须显式 opt-in；
- 继续保持“不替代下游 skill，只诊断和生成下一阶段提示词”的定位。

## 它解决什么问题

Vibe coding 中最常见的问题，不是 AI 不会写代码，而是人类还没有把问题、约束、质量标准、隐藏假设和验收标准说清楚。

但这不意味着每次都要长时间访谈。

`ni-unknown-ladder` 的定位是：

> 先诊断 unknown，再决定下一步该让 AI 脑暴、访谈、质询、探索代码库、实现，还是验收。

它只做：

```text
诊断 unknown → 推荐下一模式 → 生成下一阶段提示词
```

它不做：

```text
替你完成完整访谈 / 直接写代码 / 替代专门 skill / 自动进入下一阶段
```

## 安装方式

把整个 `ni-unknown-ladder/` 目录复制到 Claude skills 目录：

```bash
mkdir -p ~/.claude/skills
cp -R ni-unknown-ladder ~/.claude/skills/
```

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force $HOME\.claude\skills
Copy-Item -Recurse .\ni-unknown-ladder $HOME\.claude\skills\
```

## 推荐触发方式

```text
使用 ni-unknown-ladder 诊断这个任务当前处在哪类 unknown，并输出下一步提示词。
```

```text
先不要实现。请用 ni-unknown-ladder 判断我现在是想法空白、伪需求风险、行动未知、计划风险，还是验收未知。
```

```text
用 ni-unknown-ladder 看看下一步应该让 AI 访谈我、brainstorm，还是 grill 这个方案。
```

```text
AI 已经实现完了。请用 ni-unknown-ladder 判断我现在该怎么验收。
```

## 输出示例

```markdown
## Unknown 诊断

- 阶段：0 想法空白
- 置信度：高
- 判断理由：你现在描述的是一个产品冲动，而不是清晰需求。它可能是工具、助手、自动化工作流，也可能是完整产品。

## 推荐下一模式

- AI 角色：想法访谈官 / 盲点扫描器
- 最适合的能力：Blind Spot Pass / Idea Interview
- 是否建议现在实现：否

## 下一阶段提示词

```text
你现在扮演「想法访谈官 + 盲点扫描器」。

我的模糊想法是：{想法}

你的任务不是实现，而是帮我把这个想法定义清楚。

请遵守：
1. 不要写代码；
2. 不要直接给完整方案；
3. 一次只问一个会影响方向的关键问题；
4. 每个问题都要说明为什么值得问，并给出你的推荐答案；
5. 对低风险细节不要问我，先记录为假设。

请先输出：
- 这个想法可能的 3 种定义；
- 当前最大的未知；
- 你要问我的第一个关键问题；
- 你的推荐答案。

停止条件：确认第一版最应该验证的核心假设，以及明确不做什么。
```

## 停止条件

当我们确认第一版要验证的核心假设，以及不做什么之后，再进入方案脑暴或实现计划。
```

## 目录结构

```text
ni-unknown-ladder/
  SKILL.md
  README.md
  VERSION
  references/
    stage-classifier.md
    load-bearing-filter.md
    next-prompt-templates.md
    prompt-quality-rubric.md
    routing-map.md
    output-format.md
    context-diagnosis.md
    unknown-closure.md
    unknown-queue.md
    state-management.md
    anti-patterns.md
  examples/
    idea-blank.md
    false-demand-risk.md
    action-unknown.md
    quality-unknown.md
    decision-unknown.md
    plan-risk.md
    codebase-unknown.md
    expression-unknown.md
    implementation-drift.md
    verification-unknown.md
```


## 状态管理

`ni-unknown-ladder` 默认不创建任何文件，也不污染用户工程目录。

推荐三层策略：

1. **默认无状态**：只基于当前输入、对话上下文和用户显式提供的文档进行诊断。
2. **全局用户态持久化**：当你明确要求“保存状态 / 跨会话继续 / 下次继续”时，建议写到：

   ```text
   ~/.claude/ni-unknown-ladder/projects/{project-id}/state.md
   ```

3. **项目内状态**：只有当你明确要求“团队共享 / 写入项目 / 沉淀到当前工程”时，才写入：

   ```text
   .ai/ni-unknown-ladder/state.md
   ```

   写入项目前应该先确认，并可选择加入 `.gitignore`：

   ```gitignore
   .ai/ni-unknown-ladder/
   ```

状态文件只保存诊断必要信息，例如已确认事实、已解决 unknown、待处理队列、当前主 unknown、上一次停止条件；不保存完整对话、敏感内容或大段代码。

## 后续调用时的行为

当你处理完当前最优先 unknown 后，再次使用 `ni-unknown-ladder`，它应该：

1. 复盘当前上下文中的已确认事实；
2. 判断上一个主 unknown 是否满足关闭条件；
3. 如果已关闭，将它移入“已解决 Unknown”；
4. 从后续队列中提升下一个最阻塞 unknown；
5. 生成只面向新主 unknown 的下一阶段提示词。

一句话：后续调用不是重新开始，而是基于当前上下文重新分诊。

## 设计原则

- 它是诊断器，不是实现器。
- 它是路由器，不是大而全 agent。
- 它输出下一阶段提示词，而不是替代下一阶段。
- 它最多问一个关键问题。
- 它只问会改变方向、架构、数据模型、用户流程、验收标准的问题。
- 它面向中文用户，所有用户可见输出都使用中文。

## License

MIT
