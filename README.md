# ni-skill

中文 | [English](./README.en.md)

**个人技能工具箱，让 AI Agent 帮你处理日常工作与创作。**

用于 Codex、Claude Code、OpenCode 等 AI Agent，收集我在资料整理、学习研究、写作、产品架构和视觉创作中使用的技能。按任务取用，每个技能都能独立调用。

## 先用起来

安装后，在对话中指定技能、目标和材料：

| 想做什么 | 可以这样说 |
|---|---|
| 深化任务 | 用 be-ambitious 深化这个任务，明确原始材料、专业方法和外部验收标准，先重写提示词 |
| 整理资料 | 用 ni-video2md 把这个公开视频转成 Markdown：〈链接〉 |
| 找电子书 | 用 ni-book-downloader 按书名下载电子书，先确认要文字版还是 PDF |
| 学习陌生领域 | 用 ni-fde-copilot 读这些资料，先出学习蓝图，确认后再写指南 |
| 设计产品架构 | 用 ni-design-with-docs，基于这些需求和资料形成可评审的架构基线 |
| 写一篇文章 | 用 ni-article-workflow 写一篇 Agent 工程实践文章，先确认研究结论与大纲 |
| 做一张海报 | 用 ni-poster，把这句话做成极简纸刊风格海报：〈文案〉 |
| 重构一张照片 | 用 ni-poster r，把这张旅行照重构成克制的超现实电影画面：〈照片〉 |
| 做金属光影动效 | 用 ni-picarts，把这张图做成浅浮雕金属擦拭互动网页，先做一张样片：〈图片〉 |
| 把方案讲清楚 | 用 ni-explain 把这段技术方案写清楚，去掉万能动词和含糊词 |

## 安装

**Codex：**把下面这句话交给 Agent：

> 帮我从 https://github.com/ttttstc/ni-skill 安装 skills 到 ~/.agents/skills/；已有同名技能先检查，不直接覆盖。安装后告诉我哪些技能需要额外依赖。

只需要一个技能时，加上“只安装 be-ambitious”。安装后开启新会话。

**Claude Code：**

```text
/plugin marketplace add ttttstc/ni-skill
/plugin install ni-skill@ni-skill
```

**OpenCode：**把下面这句话交给 Agent：

> 帮我从 https://github.com/ttttstc/ni-skill 安装所需 skills 到 ~/.config/opencode/skills/；已有同名技能先检查，不直接覆盖。只安装 be-ambitious 时，请复制完整的 skills/be-ambitious 目录。

也可手动将本仓库 `skills/` 下所需的完整子目录复制到对应位置，保留附带的说明和许可证：

| Agent | 用户级目录 | 当前项目目录 |
|---|---|---|
| Codex | `~/.agents/skills/` | `.agents/skills/` |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| OpenCode | `~/.config/opencode/skills/` | `.opencode/skills/` |

安装后的结构应为 `<skills 目录>/<技能名>/SKILL.md`。具体目录约定见 [Codex](https://developers.openai.com/codex/skills)、[Claude Code](https://code.claude.com/docs/en/skills) 和 [OpenCode](https://opencode.ai/docs/skills/) 官方文档。

依赖按需配置：网页抓取需要 Node.js 与浏览器；本地视频转写需要 Python 和 Whisper 等工具；微信草稿推送需要公众号凭证；3D 建模需要图像生成与图生 3D 服务；ni-picarts 需要图像生成与 Python（Pillow、NumPy），自动浏览器验收另需 Node.js 和 Playwright。具体配置见各技能文档。

## 按场景选工具

| 场景 | 技能与用途 |
|---|---|
| 任务深化 | [be-ambitious](./skills/be-ambitious/SKILL.md)：保持任务目标与范围，明确专业做法、原始材料、具体工具和外部验收，用动作与预期效果重写提示词；[安装与来源](./skills/be-ambitious/README.md) |
| 资料整理 | [ni-url2md](./skills/ni-url2md/SKILL.md)：网页转 Markdown；[ni-video2md](./skills/ni-video2md/SKILL.md)：公开视频本地转写；[douyin-bulk-transcript-exporter](./skills/douyin-bulk-transcript-exporter/SKILL.md)：抖音博主逐字稿批量归档；[ni-book-downloader](./skills/ni-book-downloader/SKILL.md)：按书名下载电子书，严格区分文字版与 PDF |
| 学习与研究 | [ni-fde-copilot](./skills/ni-fde-copilot/SKILL.md)：专业资料学习蓝图与指南；[ni-unknown-first](./skills/ni-unknown-first/SKILL.md)：识别未知与下一步；[ni-research](./skills/ni-research/SKILL.md)：深度研究、讨论结论与文章大纲 |
| 产品与架构 | [ni-design-with-docs](./skills/ni-design-with-docs/SKILL.md)：产品架构基线；[think-like-architect](./skills/think-like-architect/SKILL.md)：首层架构决策 |
| 写作与表达 | [ni-radar](./skills/ni-radar/SKILL.md)：选题推荐；[ni-writer](./skills/ni-writer/SKILL.md)：文章写作；[ni-book-writer](./skills/ni-book-writer/SKILL.md)：书稿与章节；[ni-tech-report](./skills/ni-tech-report/SKILL.md)：技术汇报；[ni-explain](./skills/ni-explain/SKILL.md)：讲清楚（技术方案/汇报）；[ni-readme-guide](./skills/ni-readme-guide/SKILL.md)：中英文 README |
| 文章处理 | [ni-inspect](./skills/ni-inspect/SKILL.md)：发布前检查；[ni-formatter](./skills/ni-formatter/SKILL.md)：排版；[ni-article-image-gen](./skills/ni-article-image-gen/SKILL.md)：配图提示词；[ni-draft](./skills/ni-draft/SKILL.md)：推送微信草稿箱 |
| 视觉创作 | [ni-poster](./skills/ni-poster/SKILL.md)：ZINE 风格海报与纪实照片超现实重构（五种模式）；[ni-picarts](./skills/ni-picarts/SKILL.md)：浅浮雕底图、法线、遮罩与金属擦拭互动网页，也支持仅静态图；[ni-3d-model](./skills/ni-3d-model/SKILL.md)：多视图审核与带纹理 GLB 生成验收 |

需要串联文章生产时，用 [ni-article-workflow](./skills/ni-article-workflow/SKILL.md) 从选题、研究和大纲推进到初稿，支持断点续跑。默认先确认研究结论、大纲和写作授权；审稿、配图、排版与推送草稿箱另行调用。

## License

[MIT](./LICENSE)
