# ni-skill

[中文](./README.md) | English

> A skill suite for content creation, conversation-ready domain learning, product architecture baselines, first-cut software architecture, and review-gated 3D asset production.

ni-skill is a set of cooperating skills for AI coding agents (Codex, Claude Code, and similar runtimes), spanning source capture, research, domain learning, insight, writing, layout, preflight, imagery, publishing, product architecture baselines, first-principles architecture decisions, and review-gated multiview-to-GLB production. Each skill works standalone, and `ni-article-workflow` orchestrates the content skills into a complete pipeline.

---

## Requirements

- **Codex** / **Claude Code** / any AI agent runtime that loads skills from a local skills directory
- **Python 3.10+** — required by `ni-draft` for pushing WeChat drafts
- **Node.js + Chrome** — required by `ni-url2md` for web scraping
- **Image generation + browser control + an available image-to-3D service** — required by `ni-3d-model`; login and free quota depend on the selected provider

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
  ni-article-image-gen ni-poster ni-draft ni-article-workflow ni-unknown-first \
  ni-tech-report ni-book-writer ni-3d-model ni-fde-copilot ni-readme-guide \
  ni-product-architect think-like-architect
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
  "ni-inspect", "ni-article-image-gen", "ni-poster", "ni-draft", "ni-article-workflow",
  "ni-unknown-first", "ni-tech-report", "ni-book-writer", "ni-3d-model", "ni-fde-copilot", "ni-readme-guide",
  "ni-product-architect", "think-like-architect"
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
| Domain learning | [`ni-fde-copilot`](./skills/ni-fde-copilot) | Turn expert-oriented source material into a gated learning blueprint and conversation-ready guide |
| Insight | [`ni-insight`](./skills/ni-insight) | Identify the core argument and a distinctive angle |
| Writing | [`ni-writer`](./skills/ni-writer) | Long- and short-form writing across 6 article archetypes, in a hybrid Orwell / Calvino / Borges voice |
| Book writing | [`ni-book-writer`](./skills/ni-book-writer) | Long-form book writing in two styles (technical / trade-press), with structure, outline, and chapter scaffolding |
| Reporting | [`ni-tech-report`](./skills/ni-tech-report) | Build a clear technical report — narrative arc, evidence layout, and executive-summary synthesis |
| Layout | [`ni-formatter`](./skills/ni-formatter) | Inject layout modules (part / callout / quote / steps / verdict) |
| Preflight | [`ni-inspect`](./skills/ni-inspect) | Check metadata, content quality, and structure before publishing |
| Imagery | [`ni-article-image-gen`](./skills/ni-article-image-gen) | Generate cover and inline image prompts |
| Poster | [`ni-poster`](./skills/ni-poster) | One public poster skill with four routed ZINE styles and image generation |
| 3D modeling | [`ni-3d-model`](./skills/ni-3d-model) | Confirm requirements, review consistent multiview images, then generate and validate a textured GLB |
| Publish | [`ni-draft`](./skills/ni-draft) | Push the article to the WeChat draft inbox |
| Orchestration | [`ni-article-workflow`](./skills/ni-article-workflow) | Thread the skills into a complete pipeline with resume support |
| Diagnosis | [`ni-unknown-first`](./skills/ni-unknown-first) | Diagnose which kind of "unknown" you are facing and emit a Chinese next-step prompt |
| README | [`ni-readme-guide`](./skills/ni-readme-guide) | Create synchronized Chinese-default and English GitHub READMEs with reciprocal links and verified badges |
| Product architecture | [`ni-product-architect`](./skills/ni-product-architect) | Turn an ambiguous product or cloud-service requirement into a review-gated architecture baseline for engineering |
| Architecture | [`think-like-architect`](./skills/think-like-architect) | Turn a PRD or project context into a first-principles Architecture First Cut |

Each skill can be used standalone. `ni-article-workflow` orchestrates the content-production skills.

### ni-fde-copilot

`ni-fde-copilot` supports FDE client preparation and learning in unfamiliar professional domains. It inventories the sources, builds the domain model, Cognitive Gaps, and Learning Spine, then delivers a five-part Learning Blueprint for confirmation. Only after confirmation does it write the Guided Learning Guide, transfer challenges, and Conversation Readiness.

To invoke it, enter `$ni-fde-copilot` in a new Agent session, attach the professional sources, describe the meeting or learning goal, and ask for the Learning Blueprint before the full guide.

It supports text, PDFs, books, reports, slides, charts, video, audio, and transcripts, subject to the tools available in the current Agent environment. Inaccessible scope is blocked explicitly instead of being treated as processed. See the [Chinese guide](./skills/ni-fde-copilot/README.md) and [English guide](./skills/ni-fde-copilot/README.en.md) for usage, evidence boundaries, and validation details.

### ni-readme-guide

`ni-readme-guide` creates or audits a synchronized README pair:

- `README.md` — Simplified Chinese and the default entry point
- `README.en.md` — English counterpart with a reciprocal language link

It derives the story from repository evidence, puts the shortest successful path early, keeps commands, facts, and verified badges aligned, and validates local links, images, code blocks, and basic SVG safety. See [`skills/ni-readme-guide/README.md`](./skills/ni-readme-guide/README.md) for the bilingual skill guide.

### ni-poster style selectors

`ni-poster` is the only public poster skill. Use a short selector after `/ni-poster` when you want deterministic style control:

| Command | Internal style | Use when |
|---------|----------------|----------|
| `/ni-poster s ...` | Standard | Minimal paper zine: 3:5 portrait, 70–90% negative space, small subject cluster, aged scan texture, sparse type, one restrained chromatic anchor |
| `/ni-poster g ...` | Gathered Scenes | Keep a supplied photo truthful, then connect it to a simplified source-derived illustration field with a visible torn-fiber edge |
| `/ni-poster d ...` | Scene Distillation | Use a supplied photo as semantic reference only; create an authored abstract reinterpretation with no photographic pixels in the result |
| `/ni-poster a ...` | Photo Abstract Editorial | Keep the original photo intact, then add a clean flat ivory memory panel derived from its spatial and color relationships |

Without `s`, `g`, `d`, or `a`, a decisive style description can still select a mode. If the request remains ambiguous, `ni-poster` asks one focused question at a time until the style is confirmed; it does not silently default to Standard. The full selectors `standard`, `gathered`, `distillation`, and `photo-abstract-editorial` remain compatibility aliases. `g` and `a` require a reference photo; `d` also supports the exact `单色块模式` trigger.

Direct distinctions: minimal paper zine selects `s`; photo plus torn-paper illustration selects `g`; no photographic pixels selects `d`; original photo plus a clean lower abstract panel selects `a`. Generic words such as “photo”, “abstract”, or “zine” start the guided interview when they do not identify one mode.

Examples:

```text
/ni-poster s 把这句话做成极简纸刊：夏天结束得很轻
/ni-poster g 保留这张照片的真实场景，加入手撕纤维边
/ni-poster d 用这张照片做视觉隐喻，不保留照片像素
/ni-poster a 保留原照片，在下方生成干净象牙色抽象面板
```

### The 6 article archetypes in ni-writer

Before writing, classify the piece along three axes — **argument / emotion / source-compression** — then pick the matching archetype:

| Archetype | Word count | Soul | Fit for |
|-----------|-----------|------|---------|
| 1. Hands-on review | ≤ 6,000 | I tried it myself | Field tests, product reviews, process narratives |
| 2. Discovery brief (speed-read digest) | 500-1,500 | I pre-filtered the source for you | Distilling posts / videos / blogs / papers |
| 3. Engineering playbook | ≤ 6,000 | Here's my battle-tested framework | Engineering experience + actionable steps |
| 4. Technical polemic | 5,000-8,500 | Clear stance, zero filler, no fence-sitting | Concept disambiguation, paradigm reframing |
| 5. Personal essay | 3,000-5,000 | I've been turning this over | Stream-of-thought, feelings, non-argumentative pieces |
| 6. Field methodology (deep-water practice) | 4,500-7,000 | I hit a real engineering problem, then abstracted it | Engineering governance, workflows, collaboration, AI-tool reflection |

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
- Turn professional sources into a conversation-ready learning guide → `ni-fde-copilot`
- Make a minimal ZINE-style poster → `ni-poster`
- Turn a theme into reviewed multiview images and a validated GLB → `ni-3d-model`
- Diagnose which "unknown" you're facing and get a next-step prompt → `ni-unknown-first`
- Create synchronized Chinese-default and English GitHub READMEs → `ni-readme-guide`
- Turn an ambiguous product or cloud-service requirement into an engineering-reviewable architecture baseline → `ni-product-architect`
- Turn a PRD or existing project into a first-cut architecture decision set → `think-like-architect`
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