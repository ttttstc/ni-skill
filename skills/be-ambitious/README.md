# Be ambitious：把任务做深

来自 [Attention Heads](https://attentionheads.substack.com/?utm_source=github&utm_medium=readme&utm_campaign=skills) 的小技能，改编自 Felix Rieseberg（Anthropic）分享的提示词。给它一个任务，它会提高这个任务的专业标准，保持原有目标与范围。

## 它做什么

重写提示词之前，先针对任务所属领域回答四个问题：

1. 顶尖专业人士会做哪些你没有要求的事？
2. 他们会从什么最原始的材料入手，而不是别人消化过的内容？
3. 他们会使用哪些具体方法和工具？
4. 除了你和模型之外，什么能证明结果正确？

随后将提示词改写为明确要求这些做法，把交付物名词改成动作和预期效果，再停止，留给你审阅；你同意后才执行。用户指定的报告、文件和格式仍会保留，任务范围不扩大。

## 示例

```text
/be-ambitious 总结间歇性禁食的最新研究。
```

```text
/be-ambitious 查清楚我们的结账页面为什么在上周变慢了。
```

也可以直接说“用 be-ambitious 深化这个任务：〈任务〉”。Codex 可用 `$be-ambitious` 指定技能；Claude Code 手动安装后用 `/be-ambitious`，通过下方插件安装后用 `/ni-skill:be-ambitious`；OpenCode 可在对话中指定技能名称，由 Agent 加载。

重写时，把“要一个产物”变成“用它完成什么事”：

```text
原要求：给我一份调研报告。
改写方向：用一个丰富全面的报告来给我讲清楚，让我完全了解。
```

实际改写会结合主题，把需要理解的问题说具体，再补上四问对应的原始材料、方法和检验标准。

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

上游目录包含 `SKILL.md` 和 `README.md`，两份文件均已翻译为中文；本仓库补充“把名词换成动词”的重写规则及三种 Agent 的安装说明，技能目录名和 frontmatter `name` 保持 `be-ambitious`。

原作者为 Dan McAteer。上游 MIT 许可证及版权声明原文保留在 [LICENSE.upstream](./LICENSE.upstream)。
