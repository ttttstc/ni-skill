# ni-skill

English | [中文](./README.zh.md)

> A Claude Code skill collection by 泥巴猪. Two tracks: a long-form content creation pipeline, and harness engineering tools for AI agents.

ni-skill has two tracks. **Content creation** — a set of cooperating skills for Claude Code spanning six stages (research, insight, writing, layout, preflight, publishing), each usable standalone or orchestrated by `ni-article-workflow` into a complete pipeline. **Harness engineering** — tooling for making codebases legible to AI coding agents.

---

## Requirements

- **Claude Code** (with Plugin Marketplace support)
- **Python 3.10+** — required by `ni-draft` for pushing WeChat drafts
- **Node.js + Chrome** — required by `ni-url2md` for web scraping

See each skill's `SKILL.md` for its specific dependencies.

---

## Installation

### Option 1: Plugin Marketplace (recommended)

In Claude Code:

```
/plugin marketplace add ttttstc/ni-skill
/plugin install ni-skill@ni-skill
```

### Option 2: Via the Agent

Ask Claude:

> Please install skills from github.com/ttttstc/ni-skill

### Option 3: Manual

Clone the repository and move the skill directories under `skills/article/` and `skills/harness/` into `~/.claude/skills/`:

```bash
git clone https://github.com/ttttstc/ni-skill.git
mv ni-skill/skills/article/* ni-skill/skills/harness/* ~/.claude/skills/
```

PowerShell:

```powershell
git clone https://github.com/ttttstc/ni-skill.git
Move-Item ni-skill\skills\article\*,ni-skill\skills\harness\* $HOME\.claude\skills\
```

Manual installation does not support auto-updates; Option 1 is recommended.

---

## Skills

### Content creation (`skills/article/`)

| Stage | Skill | Capability |
|-------|-------|------------|
| Source | [`ni-url2md`](./skills/article/ni-url2md) | Scrape any URL into Markdown, with JS rendering and logged-in page support |
| Research | [`ni-research`](./skills/article/ni-research) | Trend analysis, competitor scanning, sourced material collection |
| Insight | [`ni-insight`](./skills/article/ni-insight) | Identify the core argument and a distinctive angle |
| Writing | [`ni-writer`](./skills/article/ni-writer) | Long-form writing in a hybrid Orwell / Calvino / Borges voice |
| Layout | [`ni-formatter`](./skills/article/ni-formatter) | Inject layout modules (part / callout / quote / steps / verdict) |
| Preflight | [`ni-inspect`](./skills/article/ni-inspect) | Check metadata, content quality, and structure before publishing |
| Imagery | [`ni-article-image-gen`](./skills/article/ni-article-image-gen) | Generate cover and inline image prompts |
| Publish | [`ni-draft`](./skills/article/ni-draft) | Push the article to the WeChat draft inbox |
| Orchestration | [`ni-article-workflow`](./skills/article/ni-article-workflow) | Thread the skills into a complete pipeline with resume support |

Each skill can be used standalone or orchestrated by `ni-article-workflow`.

### Harness engineering (`skills/harness/`)

| Skill | Capability |
|-------|------------|
| [`agent-legible`](./skills/harness/agent-legible) | Audit how legible a TS/JS codebase is to AI agents: flag misusable interfaces, check layering, produce an audit report with fix drafts |

---

## Design Guidelines

All skills follow three shared guidelines:

- **Honest output**: no fabrication or overstatement; failures are reported as-is.
- **Self-verification**: each skill runs its own checklist before delivering output.
- **Explicit degradation**: when an external dependency is unavailable, a degraded path is provided and clearly marked.

Each skill also has its own domain guidelines; see the corresponding `SKILL.md`.

---

## Pipeline

```
topic
  ↓
ni-research           trend analysis, competitor scan, material collection
  ↓
ni-insight            define the core argument and angle
  ↓
ni-writer             develop the long-form article
  ↓
ni-formatter          inject layout modules
  ↓
ni-inspect            pre-publication quality check
  ↓
ni-article-image-gen  generate image prompts (optional)
  ↓
ni-draft              push to the WeChat draft inbox
```

If any stage degrades or fails, the skill reports it clearly and leaves the next step to you.

---

## Usage

### Full pipeline

Describe a topic to Claude, for example:

> Use ni-skill to write an article on "AGENTS.md in practice"

`ni-article-workflow` takes over and runs each stage in turn.

### Individual skills

Describe what you need to trigger the matching skill:

- Find an article angle → `ni-insight`
- Lay out an article → `ni-formatter`
- Scrape a URL into Markdown → `ni-url2md`
- Push a draft → `ni-draft`
- Audit a codebase's agent legibility → `agent-legible`

See each skill's `SKILL.md` for its full trigger-word list.

---

## Configuration

### WeChat draft push (ni-draft)

Configure via environment variables:

```bash
WECHAT_APPID=wx_xxxxxxxx
WECHAT_SECRET=xxxxxxxxxxxxxxxx
```

Or in `~/.config/ni-skill/config.yaml`:

```yaml
wechat:
  appid: wx_xxxxxxxx
  secret: xxxxxxxxxxxxxxxx
```

Obtain credentials from the WeChat Official Account admin console, and add the calling host's IP to the allowlist.

### Web scraping (ni-url2md)

Optional environment variables:

| Variable | Purpose |
|----------|---------|
| `URL_CHROME_PATH` | Path to the Chrome executable |
| `URL_DATA_DIR` | Default output directory |
| `URL_CHROME_PROFILE_DIR` | Chrome profile directory, to persist login sessions |

---

## License

MIT
