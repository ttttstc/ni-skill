# Be ambitious：重新想象我们可以做到的事

给它一个准备交给 AI 的任务，重新设想值得追求的结果，找出初始解法中可以改变的前提，把推荐的新任务写成可执行、可验证的提示词。基于 [Attention Heads](https://attentionheads.substack.com/?utm_source=github&utm_medium=readme&utm_campaign=skills) 的原始技能和 [Felix Rieseberg 的文章](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/)。

## 它做什么

它把报告、工具或 Agent 当作你想到的一种解法，继续检查希望发生什么变化，以及哪些旧前提限制了目标。例如从“每天汇总构建失败”探索到“让维护者只介入真正需要人处理的问题，并持续发现和消除重复故障”。

推荐目标会说明新增的结果、替代原流程的做法、已有依据和必要条件。随后按专业标准确定原始材料、具体方法、当前能开始的第一步和反馈入口，设计检验新做法的办法。

有影响投入、承诺或关键目标的分歧时，先推荐并请你选择；已选定或授权自行选择时，直接生成提示词，不再重开选择。默认用简短说明配一段可复制的 prompt，避免解释和 prompt 重复。应急与锁定范围照守，简单任务简短处理；已有执行授权时可以接着做第一步。

野心需要接上反馈：新目标能带来什么原先没有的判断、行动或结果？第一步怎样检验最关键的假设？结果怎样与原做法比较？文本评分不能代替这些证据。

## 专业标准

深化选定任务时，使用 Felix Rieseberg 分享的四问：

> 我想要这个任务的更深版本，而不是更大的版本。在重写之前：
> （1）说出这个领域的顶尖专业人士在这里会做哪些我没要求的事；
> （2）说出他们会从什么最原始的材料起步，而不是别人已经消化好的东西；
> （3）说出他们会使用的具体方法与工具；
> （4）说出除了你和我之外，还有什么能证明结果是对的。
> 然后把我的提示词改写成正好要求这些。

## 示例

```text
/be-ambitious 总结间歇性禁食的最新研究。
```

```text
/be-ambitious 查清楚我们的结账页面为什么在上周变慢了。
```

```text
/be-ambitious 我准备给每个项目写一个自动清日志的脚本。如果我们能让 AI 接入数据、工具和验证环境，可以追求什么更高层、更有野心的结果？先展开目标选项，说明新增范围与必要条件，让我选。
```

```text
/be-ambitious 我想把新人手册做成问答机器人，让新人少找老同事。请重新检查这个解法，提出更值得追求的结果。你可以自行推荐目标，直接交付任务 prompt，写清第一步用什么反馈验证，不必等我再选。
```

也可以直接说“用 be-ambitious 深化这个任务：〈任务〉”。Codex 可用 `$be-ambitious` 指定技能；Claude Code 手动安装后用 `/be-ambitious`，通过下方插件安装后用 `/ni-skill:be-ambitious`；OpenCode 可在对话中指定技能名称，由 Agent 加载。

重写时，把“要一个产物”变成“用它完成什么事”：

```text
原要求：给我一份季度调研报告。
初步改写：用一个丰富全面的报告来给我讲清楚，让我完全了解。
继续明确：帮助负责人看懂本季度的变化、判断风险，并决定下一季度的资源分配。
```

“丰富全面”“完全了解”仍需结合主题说清楚。实际改写会保留报告要求，补上已有材料、硬约束、专业方法和可检查的完成条件；不会替用户编造数字或期限。

## 安装

把下面这句话交给 Agent，将 `〈安装目录〉` 替换为表中的对应路径：

```text
请从 https://github.com/ttttstc/ni-skill 安装 skills/be-ambitious，将整个目录复制到〈安装目录〉，保留 README.md 和 LICENSE.upstream。已有同名技能先检查，不直接覆盖。
```

| Agent | 用户级安装目录 | 当前项目安装目录 |
|---|---|---|
| Codex | `~/.agents/skills/be-ambitious/` | `.agents/skills/be-ambitious/` |
| Claude Code | `~/.claude/skills/be-ambitious/` | `.claude/skills/be-ambitious/` |
| OpenCode | `~/.config/opencode/skills/be-ambitious/` | `.opencode/skills/be-ambitious/` |

也可手动将本仓库的整个 `skills/be-ambitious/` 目录复制到对应位置。用户级安装对该用户的项目生效，项目级安装只用于当前项目。安装后开启新会话，用上面的示例确认技能可用。该技能不需要额外依赖。

Claude Code 还可通过仓库插件安装：

```text
/plugin marketplace add ttttstc/ni-skill
/plugin install ni-skill@ni-skill
```

目录与调用约定见 [Codex 文档](https://developers.openai.com/codex/skills)、[Claude Code 文档](https://code.claude.com/docs/en/skills) 和 [OpenCode 文档](https://opencode.ai/docs/skills/)。

## 来源与许可

完整移植并翻译自 [DannyMac180/skills 的 be-ambitious](https://github.com/DannyMac180/skills/tree/7dc63b7a748b8bd14bf213c15ecddd4536409407/be-ambitious)，上游提交为 `7dc63b7a748b8bd14bf213c15ecddd4536409407`。

上游目录包含 `SKILL.md` 和 `README.md`，两份文件均已翻译为中文。目标探索、专业工具、原始材料、假设检验和外部验证依据 Felix 的文章组织；技能名与原始四问保留。

[行为验证](./evals/README.md) 提供场景、完整答复、独立评分和证据范围。

原作者为 Dan McAteer。上游 MIT 许可证及版权声明原文保留在 [LICENSE.upstream](./LICENSE.upstream)。
