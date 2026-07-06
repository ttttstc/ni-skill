# ni-skill

English | [中文](./README.zh.md)

> A content creation skill suite for 泥巴猪. End-to-end pipeline from topic to publication, covering AI, engineering management, DevOps, and architecture.

ni-skill is a set of cooperating skills for AI coding agents (Codex, Claude Code, and similar runtimes), spanning source capture, research, insight, writing, layout, preflight, imagery, and publishing. Each skill works standalone, and `ni-article-workflow` orchestrates them into a complete pipeline.

---

## Requirements

- **Codex** / **Claude Code** / any AI agent runtime that loads skills from a local skills directory
- **Python 3.10+** — required by `ni-draft` for pushing WeChat drafts
- **Node.js + Chrome** — required by `ni-url2md` for web scraping

See each skill's `SKILL.md` for its specific dependencies.

---

## Installation

Pick the path that matches your runtime.

### Codex — local plugin

The repo ships a Codex plugin manifest at `.codex-plugin/plugin.json`. For local development, clone the repo and install or symlink it per your Codex plugin workflow.

If you only need the skills, copy them into `~/.codex/skills/`. This snippet installs the full published set:

```bash
git clone https://github.com/ttttstc/ni-skill.git
mkdir -p ~/.codex/skills
for skill in \
  ni-url2md ni-research ni-insight ni-writer ni-formatter ni-inspect \
  ni-article-image-gen ni-draft ni-article-workflow ni-unknown-first \
  ni-tech-report ni-book-writer
do
  cp -R "ni-skill/skills/$skill" ~/.codex/skills/
done
```

PowerShell:

```powershell
git clone https://github.com/ttttstc/ni-skill.git
New-Item -ItemType Directory -Force $HOME\.codex\skills | Out-Null
$skills = @(
  "ni-url2md", "ni-research", "ni-insight", "ni-writer", "ni-formatter",
  "ni-inspect", "ni-article-image-gen", "ni-draft", "ni-article-workflow",
  "ni-unknown-first", "ni-tech-report", "ni-book-writer"
)
foreach ($skill in $skills) {
  Copy-Item "ni-skill\skills\$skill" "$HOME\.codex\skills\$skill" -Recurse -Force
}
```

To install only `ni-unknown-first`:

```bash
git clone https://github.com/ttttstc/ni-skill.git
mkdir -p ~/.codex/skills
cp -R ni-skill/skills/ni-unknown-first ~/.codex/skills/
```

PowerShell:

```powershell
git clone https://github.com/ttttstc/ni-skill.git
New-Item -ItemType Directory -Force $HOME\.codex\skills | Out-Null
Copy-Item ni-skill\skills\ni-unknown-first $HOME\.codex\skills\ni-unknown-first -Recurse -Force
```

After installing, start a new Codex session so the skill list is refreshed.

### Claude Code — Plugin Marketplace

In Claude Code:

```
/plugin marketplace add ttttstc/ni-skill
/plugin install ni-skill@ni-skill
```

### Any runtime — ask the agent

Tell Codex or Claude:

> Please install skills from github.com/ttttstc/ni-skill

For a single skill (e.g. only `ni-unknown-first` into Codex):

> Please install only ni-unknown-first from github.com/ttttstc/ni-skill into ~/.codex/skills

### Manual — copy into your skills directory

Most AI agent runtimes load skills from `~/.{agent}/skills/` (e.g. `~/.codex/skills/`, `~/.claude/skills/`). Clone the repo and copy the subdirectories under `skills/` into your runtime's skills folder:

```bash
git clone https://github.com/ttttstc/ni-skill.git
cp -R ni-skill/skills/* ~/.claude/skills/
```

PowerShell:

```powershell
git clone https://github.com/ttttstc/ni-skill.git
Copy-Item ni-skill\skills\* $HOME\.claude\skills\ -Recurse -Force
```

Manual install doesn't support auto-updates; prefer the per-runtime path above when available.

---

## Skills

| Stage | Skill | Capability |
|-------|-------|------------|
| Source | [`ni-url2md`](./skills/ni-url2md) | Scrape any URL into Markdown, with JS rendering and logged-in page support |
| Research | [`ni-research`](./skills/ni-research) | Trend analysis, competitor scanning, sourced material collection |
| Insight | [`ni-insight`](./skills/ni-insight) | Identify the core argument and a distinctive angle |
| Writing | [`ni-writer`](./skills/ni-writer) | Long- and short-form writing across 5 article archetypes, in a hybrid Orwell / Calvino / Borges voice |
| Book writing | [`ni-book-writer`](./skills/ni-book-writer) | Long-form book writing in two styles (technical / trade-press), with structure, outline, and chapter scaffolding |
| Reporting | [`ni-tech-report`](./skills/ni-tech-report) | Build a clear technical report — narrative arc, evidence layout, and executive-summary synthesis |
| Layout | [`ni-formatter`](./skills/ni-formatter) | Inject layout modules (part / callout / quote / steps / verdict) |
| Preflight | [`ni-inspect`](./skills/ni-inspect) | Check metadata, content quality, and structure before publishing |
| Imagery | [`ni-article-image-gen`](./skills/ni-article-image-gen) | Generate cover and inline image prompts |
| Publish | [`ni-draft`](./skills/ni-draft) | Push the article to the WeChat draft inbox |
| Orchestration | [`ni-article-workflow`](./skills/ni-article-workflow) | Thread the skills into a complete pipeline with resume support |
| Diagnosis | [`ni-unknown-first`](./skills/ni-unknown-first) | Diagnose which kind of "unknown" you are facing and emit a Chinese next-step prompt |

Each skill can be used standalone or orchestrated by `ni-article-workflow`.

### The 5 article archetypes in ni-writer

Before writing, classify the piece along three axes — **argument / emotion / source-compression** — then pick the matching archetype:

| Archetype | Word count | Soul | Fit for |
|-----------|-----------|------|---------|
| 1. Hands-on review | ≤ 6,000 | I tried it myself | Field tests, product reviews, process narratives |
| 2. Discovery brief (speed-read digest) | 500-1,500 | I pre-filtered the source for you | Distilling posts / videos / blogs / papers |
| 3. Engineering playbook | ≤ 6,000 | Here's my battle-tested framework | Engineering experience + actionable steps |
| 4. Technical polemic | 5,000-8,500 | Clear stance, zero filler, no fence-sitting | Concept disambiguation, paradigm reframing |
| 5. Personal essay | 3,000-5,000 | I've been turning this over | Stream-of-thought, feelings, non-argumentative pieces |

Full rules: [`skills/ni-writer/SKILL.md`](./skills/ni-writer/SKILL.md) and the sub-style files under `references/`.

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

Describe a topic to Codex or Claude, for example:

> Use ni-skill to write an article on "AGENTS.md in practice"

`ni-article-workflow` takes over and runs each stage in turn.

### Individual skills

Describe what you need to trigger the matching skill:

- Find an article angle → `ni-insight`
- Lay out an article → `ni-formatter`
- Scrape a URL into Markdown → `ni-url2md`
- Diagnose which "unknown" you're facing and get a next-step prompt → `ni-unknown-first`
- Push a draft → `ni-draft`

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
