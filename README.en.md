# ni-skill

[中文](./README.md) | English

**A personal skill toolbox for everyday work and creative projects with AI agents.**

Skills I use with Codex, Claude Code, OpenCode, and similar AI agents for collecting sources, learning, research, writing, product architecture, and visual creation. Pick what the task needs. Each skill works on its own.

## Start here

After installation, name the skill, your goal, and your sources in a conversation:

| Goal | Example request |
|---|---|
| Imagine bigger goals | Use be-ambitious to rethink the goal, examine assumptions in the initial approach, and recommend a more ambitious task as an actionable prompt |
| Organize sources | Use ni-video2md to turn this public video into Markdown: 〈URL〉 |
| Find ebooks | Use ni-book-downloader to download a book by title. Confirm text or PDF format first |
| Learn a domain | Use ni-fde-copilot to read these sources. Confirm a learning blueprint before writing the guide |
| Design product architecture | Use ni-design-with-docs to build a reviewable architecture baseline from these requirements and sources |
| Write an article | Use ni-article-workflow for an article about Agent engineering. Confirm the research findings and outline first |
| Create a poster | Use ni-poster to turn this text into a minimal paper-zine poster: 〈text〉 |
| Restage a photo | Use ni-poster r to rebuild this travel photo into a restrained surreal cinematic tableau: 〈photo〉 |
| Create metallic light effects | Use ni-picarts to turn this image into a shallow relief with interactive metallic wipe effects. Start with one sample: 〈image〉 |
| Explain a plan clearly | Use ni-explain to rewrite this technical proposal clearly, removing empty verbs and vague words |

## Install

**Codex:** give the agent this request:

> Install skills from https://github.com/ttttstc/ni-skill into ~/.agents/skills/. Check existing skills with the same name before overwriting. Tell me which skills need extra dependencies.

For one skill, add “Install only be-ambitious.” Start a new session after installation.

**Claude Code:**

```text
/plugin marketplace add ttttstc/ni-skill
/plugin install ni-skill@ni-skill
```

**OpenCode:** give the agent this request:

> Install the required skills from https://github.com/ttttstc/ni-skill into ~/.config/opencode/skills/. Check existing skills with the same name before overwriting. For be-ambitious only, copy the entire skills/be-ambitious directory.

You can also copy the required full subdirectories from `skills/` to the matching location, keeping their documentation and licenses:

| Agent | User directory | Project directory |
|---|---|---|
| Codex | `~/.agents/skills/` | `.agents/skills/` |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| OpenCode | `~/.config/opencode/skills/` | `.opencode/skills/` |

The installed layout should be `<skills directory>/<skill name>/SKILL.md`. See the official [Codex](https://developers.openai.com/codex/skills), [Claude Code](https://code.claude.com/docs/en/skills), and [OpenCode](https://opencode.ai/docs/skills/) documentation for directory conventions.

Configure dependencies as needed: web capture uses Node.js and a browser; local video transcription uses Python and tools such as Whisper; WeChat draft delivery needs account credentials; 3D modeling needs image generation and an image-to-3D service; ni-picarts uses image generation and Python with Pillow and NumPy, with Node.js and Playwright for automated browser validation. See each skill's documentation for setup.

## Choose by task

| Task | Skills and purpose |
|---|---|
| Goal and task exploration | [be-ambitious](./skills/be-ambitious/SKILL.md): rethink the initial approach, recommend more ambitious outcomes, and connect expert methods, a first action, and real feedback in a task prompt; [installation and source](./skills/be-ambitious/README.md) |
| Source collection | [ni-url2md](./skills/ni-url2md/SKILL.md): web pages to Markdown; [ni-video2md](./skills/ni-video2md/SKILL.md): local public-video transcription; [douyin-bulk-transcript-exporter](./skills/douyin-bulk-transcript-exporter/SKILL.md): batch transcripts from a Douyin creator; [ni-book-downloader](./skills/ni-book-downloader/SKILL.md): download ebooks by title, separating text formats from PDF |
| Learning and research | [ni-fde-copilot](./skills/ni-fde-copilot/SKILL.md): learning blueprints and guides; [ni-unknown-first](./skills/ni-unknown-first/SKILL.md): identify unknowns and next steps; [ni-research](./skills/ni-research/SKILL.md): deep research, discussion, and article outlines |
| Product and architecture | [ni-design-with-docs](./skills/ni-design-with-docs/SKILL.md): product architecture baselines; [think-like-architect](./skills/think-like-architect/SKILL.md): first-cut architecture decisions |
| Writing and communication | [ni-radar](./skills/ni-radar/SKILL.md): topic recommendations; [ni-writer](./skills/ni-writer/SKILL.md): articles; [ni-book-writer](./skills/ni-book-writer/SKILL.md): books and chapters; [ni-tech-report](./skills/ni-tech-report/SKILL.md): technical reports; [ni-explain](./skills/ni-explain/SKILL.md): explain clearly (proposals and reports); [ni-readme-guide](./skills/ni-readme-guide/SKILL.md): Chinese and English READMEs |
| Article preparation | [ni-inspect](./skills/ni-inspect/SKILL.md): prepublication checks; [ni-formatter](./skills/ni-formatter/SKILL.md): layout; [ni-article-image-gen](./skills/ni-article-image-gen/SKILL.md): image prompts; [ni-draft](./skills/ni-draft/SKILL.md): WeChat draft delivery |
| Visual creation | [ni-poster](./skills/ni-poster/SKILL.md): ZINE-style posters and documentary-photo surreal restaging (five modes); [ni-picarts](./skills/ni-picarts/SKILL.md): relief base images, normal maps, masks, and interactive metallic wipe effects, with a static-only option; [ni-3d-model](./skills/ni-3d-model/SKILL.md): multiview review and textured GLB generation and validation |

To connect the article stages, use [ni-article-workflow](./skills/ni-article-workflow/SKILL.md) for topics, research, outlines, and an initial draft, with support for resuming interrupted work. By default, it requires confirmation of findings, the outline, and permission to write. Review, imagery, formatting, and draft delivery are separate calls.

## License

[MIT](./LICENSE)
