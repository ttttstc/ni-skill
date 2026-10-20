# Be ambitious：重新想象我们可以做到的事

给它一个准备交给 AI 的任务，打开目标的想象空间，再把选定方向做深。基于 [Attention Heads](https://attentionheads.substack.com/?utm_source=github&utm_medium=readme&utm_campaign=skills) 的原始技能，按 [Felix Rieseberg 的文章](https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/) 组织向上、向下两个方向。

## 它做什么

| 方向 | 它会检查什么 |
|---|---|
| 向上扩展目标 | 追问目标背后的目标，提高抽象层次，设想更大胆的结果、更广范围和新的工作方式 |
| 向下补齐证据 | 专家会多做什么，从什么原始材料开始，用哪些具体方法与工具，以及什么外部检验能证明结果正确 |

向上会从“修好这次崩溃”探索到“持续保持应用稳定”，从“做一份季度汇报”探索到“持续提早发现问题、支持资源调整”。它会提出原先没有要求的目标和范围，再说明这些目标需要接通什么数据、工具、环境和反馈。

先展开目标选项，再比较收益、代价与风险。探索阶段允许扩大目标和范围；执行时以你选定的目标与授权为准。允许提出替代任务，不等于已经选定其中一个。

选定后交付一段可复制的提示词，等待你授权执行。应急止损和用户锁定的范围照守，简单明确的任务简短处理。

## 原始四问

向下做深保留 Felix Rieseberg（Anthropic）分享的提示。“更深而不是更大”用于这个方向，向上仍可打开新的目标与范围：

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

上游目录包含 `SKILL.md` 和 `README.md`，两份文件均已翻译为中文。本仓库扩展目标的抽象层次、想象力、野心与范围，以及竞争解释和反证，并保留原始四问、技能名和三种 Agent 的安装方式。

方法设计还参考 [dbskill](https://github.com/dontbesilent2025/dbskill) 的相关技能，用于还原目标和验证判断。向上展开目标以 Felix 的 Altitude 为主线，DBS 的目标澄清不作为限制想象空间的门槛：

| 方法入口 | 吸收的判断 |
|---|---|
| [dbs-goal](https://github.com/dontbesilent2025/dbskill/blob/14b567fc71beef647d52a6bc40a4e9b71a9ee6c5/skills/dbs-goal/SKILL.md) | 有条件地追问手段与目的，只补会改变路径或验收的信息 |
| [dbs-jtbd](https://github.com/dontbesilent2025/dbskill/blob/14b567fc71beef647d52a6bc40a4e9b71a9ee6c5/skills/dbs-jtbd/SKILL.md) | 区分表面请求、想推进的进展和现实结果 |
| [dbs-deconstruct](https://github.com/dontbesilent2025/dbskill/blob/14b567fc71beef647d52a6bc40a4e9b71a9ee6c5/skills/dbs-deconstruct/SKILL.md) | 用动作、对象和结果还原概念，检查隐藏预设 |
| [dbs-good-question](https://github.com/dontbesilent2025/dbskill/blob/14b567fc71beef647d52a6bc40a4e9b71a9ee6c5/skills/dbs-good-question/SKILL.md) | 用可观察信号区分竞争解释，设计最小验证 |

运行时只需本技能，不依赖 DBS 安装。[行为验证说明](./evals/README.md) 提供样本、判据、原始答复及证据边界。

原作者为 Dan McAteer。上游 MIT 许可证及版权声明原文保留在 [LICENSE.upstream](./LICENSE.upstream)。
