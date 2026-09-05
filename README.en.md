# ni-skill

[中文](./README.md) | English

> A skill suite for content creation, local video transcription, conversation-ready domain learning, product architecture baselines, first-cut software architecture, and review-gated 3D asset production.

ni-skill is a set of cooperating skills for AI coding agents (Codex, Claude Code, and similar runtimes), spanning source capture, local video transcription, topic radar, domain learning, article planning, writing, layout, preflight, imagery, publishing, product architecture baselines, first-principles architecture decisions, and review-gated multiview-to-GLB production. Each skill works standalone; `ni-article-workflow` provides a gated path through the initial article draft.

---

## Requirements

- **Codex** / **Claude Code** / any AI agent runtime that loads skills from a local skills directory
- **Python 3.10+** — required by `ni-draft` for pushing WeChat drafts and by `ni-video2md` for local transcription
- **Node.js + Chrome** — required by `ni-url2md` for web scraping
- **yt-dlp** — used by `ni-video2md` to download public X, YouTube, Bilibili, and Xiaohongshu videos; a portable copy is cached when missing
- **Chrome/Edge or a downloadable Chromium** — required by `ni-video2md` to capture public Douyin media streams
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
  ni-url2md ni-radar ni-insight ni-writer ni-formatter ni-inspect \
  ni-article-image-gen ni-poster ni-draft ni-article-workflow ni-unknown-first \
  ni-tech-report ni-book-writer ni-3d-model ni-fde-copilot ni-readme-guide \
  ni-design-with-docs ni-video2md think-like-architect
do
  cp -R "ni-skill/skills/$skill" ~/.codex/skills/
done
```

PowerShell:

```powershell
git clone https://github.com/ttttstc/ni-skill.git
New-Item -ItemType Directory -Force $HOME\.codex\skills | Out-Null
$skills = @(
  "ni-url2md", "ni-radar", "ni-insight", "ni-writer", "ni-formatter",
  "ni-inspect", "ni-article-image-gen", "ni-poster", "ni-draft", "ni-article-workflow",
  "ni-unknown-first", "ni-tech-report", "ni-book-writer", "ni-3d-model", "ni-fde-copilot", "ni-readme-guide",
  "ni-design-with-docs", "ni-video2md", "think-like-architect"
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
| Video | [`ni-video2md`](./skills/ni-video2md) | Transcribe public Douyin, X, YouTube, Bilibili, and Xiaohongshu videos to `full-summary-author.md` with local Whisper; no SRT output |
| Topic radar | [`ni-radar`](./skills/ni-radar) | Search 14 days of original X content, combine it with 21 days of local sources, and recommend 1–2 of 5–8 topics |
| Domain learning | [`ni-fde-copilot`](./skills/ni-fde-copilot) | Turn expert-oriented source material into a gated learning blueprint and conversation-ready guide |
| Article planning | [`ni-insight`](./skills/ni-insight) | Interview the user or autonomously synthesize candidate theses, preserve authorship boundaries, and produce a complete outline |
| Writing | [`ni-writer`](./skills/ni-writer) | Five article archetypes; the two technical-methodology routes are merged while technical polemic remains separate |
| Book writing | [`ni-book-writer`](./skills/ni-book-writer) | Long-form book writing in two styles (technical / trade-press), with structure, outline, and chapter scaffolding |
| Reporting | [`ni-tech-report`](./skills/ni-tech-report) | Build a clear technical report — narrative arc, evidence layout, and executive-summary synthesis |
| Layout | [`ni-formatter`](./skills/ni-formatter) | Inject layout modules (part / callout / quote / steps / verdict) |
| Preflight | [`ni-inspect`](./skills/ni-inspect) | Check metadata, content quality, and structure before publishing |
| Imagery | [`ni-article-image-gen`](./skills/ni-article-image-gen) | Generate cover and inline image prompts |
| Poster | [`ni-poster`](./skills/ni-poster) | One public poster skill with four routed ZINE styles and image generation |
| 3D modeling | [`ni-3d-model`](./skills/ni-3d-model) | Confirm requirements, review consistent multiview images, then generate and validate a textured GLB |
| Publish | [`ni-draft`](./skills/ni-draft) | Push the article to the WeChat draft inbox |
| Orchestration | [`ni-article-workflow`](./skills/ni-article-workflow) | Gate topic selection, sources, outline, evidence, and writing; resume safely and stop at the initial draft |
| Diagnosis | [`ni-unknown-first`](./skills/ni-unknown-first) | Diagnose which kind of "unknown" you are facing and emit a Chinese next-step prompt |
| README | [`ni-readme-guide`](./skills/ni-readme-guide) | Create synchronized Chinese-default and English GitHub READMEs with reciprocal links and verified badges |
| Docs-driven design | [`ni-design-with-docs`](./skills/ni-design-with-docs) | Use source documents, interviews, and public evidence to turn an ambiguous product or cloud-service requirement into a review-gated architecture baseline |
| Architecture | [`think-like-architect`](./skills/think-like-architect) | Turn a PRD or project context into a first-principles Architecture First Cut |

Each skill can be used standalone. `ni-article-workflow` orchestrates topic discovery through the initial draft; review, imagery, layout, and publishing remain standalone steps.

### ni-fde-copilot

`ni-fde-copilot` supports FDE client preparation and learning in unfamiliar professional domains. It inventories the sources, builds the domain model, Cognitive Gaps, and Learning Spine, then delivers a five-part Learning Blueprint for confirmation. Only after confirmation does it write the Guided Learning Guide, transfer challenges, and Conversation Readiness.

To invoke it, enter `$ni-fde-copilot` in a new Agent session, attach the professional sources, describe the meeting or learning goal, and ask for the Learning Blueprint before the full guide.

It supports text, PDFs, books, reports, slides, charts, video, audio, and transcripts, subject to the tools available in the current Agent environment. Inaccessible scope is blocked explicitly instead of being treated as processed. See the [Chinese guide](./skills/ni-fde-copilot/README.md) and [English guide](./skills/ni-fde-copilot/README.en.md) for usage, evidence boundaries, and validation details.

### ni-video2md

`ni-video2md` turns public Douyin, X, YouTube, Bilibili, and Xiaohongshu video URLs or share text into Markdown transcripts using local Whisper. It prefers local `whisper.cpp`; X, YouTube, Bilibili, and Xiaohongshu use `yt-dlp` for single-video downloads, while Douyin still uses browser capture. On first run it downloads and caches missing ffmpeg, Whisper.cpp, the model, or `yt-dlp`; browser dependencies are needed only for Douyin. After finding or installing these executables, it adds their directories to the current process PATH and persists them in the Windows user PATH. It does not call a cloud transcription API and does not generate SRT files. The transcript gets a local extractive one-sentence summary based on the full text, and the document title, H1, and filename all use `summary-author`; the Markdown can then be safely copied to a user-selected archive path. Login walls, CAPTCHAs, and site compatibility failures are reported rather than bypassed.

```bash
python skills/ni-video2md/scripts/video_to_md.py "<video-url-or-share-text>" -o ./transcripts
```

Media, WAV, and Whisper intermediate TXT files live only in a one-shot temporary directory and are deleted after success or failure; only the Markdown output and dependency cache persist.

`-o` selects the output directory (when given an `.md` path, its parent directory is used), while the generated `summary-author.md` name is always enforced. After returning the Markdown, ask whether to archive it; if confirmed, run `skills/ni-video2md/scripts/archive_markdown.py`. Existing archive targets are never overwritten, and the original file is retained.

Automatic dependency downloads currently cover Windows x64. On other platforms, point `NI_VIDEO2MD_FFMPEG`, `NI_VIDEO2MD_WHISPER_CLI`, `NI_VIDEO2MD_MODEL`, `NI_VIDEO2MD_YTDLP`, and `NI_VIDEO2MD_BROWSER` at existing local tools. Video and public dependency downloads use network bandwidth, but speech recognition runs locally.

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

### The 5 article archetypes in ni-writer

Classify by the article's primary value: hands-on experience, source compression, engineering method, technical polemic, or personal reflection. The two technical-methodology routes now share one entry point; the other styles remain available:

| Archetype | Word count | Soul | Fit for |
|-----------|-----------|------|---------|
| 1. Hands-on review | ≤ 6,000 | I tried it myself | Field tests, product reviews, process narratives |
| 2. Discovery brief (speed-read digest) | 500-1,500 | I pre-filtered the source for you | Distilling posts / videos / blogs / papers |
| 3. Technical methodology (framework + deep-scene merge) | 4,500-7,000 | Explain the facts, then reason through the mechanism | Engineering practice, architecture, process, collaboration, tool retrospectives |
| 4. Technical polemic | 5,000-8,500 | Think one judgment through to its boundary | Concept disambiguation, mechanism analysis, paradigm reframing |
| 5. Personal essay | 3,000-5,000 | I've been turning this over | Stream-of-thought, feelings, non-argumentative pieces |

Technical methodology uses [`skills/ni-writer/SKILL.md`](./skills/ni-writer/SKILL.md) and `references/tech_writing_rules.md`; technical polemic keeps its independent `references/tech_polemic_rules.md`. Technical methodology now uses one spine scene to carry the judgment, with visible actions, artifacts, and judgment changes. The anti-AI pass adopts `human-writing` checks for material sufficiency, speaker position, natural progression, revision, removable adverbs, and unsupported degree claims.

---

## Design Guidelines

All skills follow three shared guidelines:

- **Honest output**: no fabrication or overstatement; failures are reported as-is.
- **Self-verification**: each skill runs its own checklist before delivering output.
- **Explicit degradation**: when an external dependency is unavailable, a degraded path is provided and clearly marked.

Each skill also has its own domain guidelines; see the corresponding `SKILL.md`.

---

## Initial-draft pipeline

```
topic
  ↓
ni-radar              14-day X search, 21-day local analysis, weekly recommendations
  ↓
selection + source    user selection or qualified top pick, locally archived sources
  ↓
ni-insight            collaborative interview or autonomous thesis synthesis
  ↓
ni-radar evidence     deepen evidence and detect outline conflicts
  ↓
ni-writer             produce article-draft.md
  ↓
draft_ready           workflow stops for human review
```

Each stage validates its artifact before advancing. Failures retain evidence and stop instead of bypassing a gate with defaults.

---

## Usage

### Initial-draft pipeline

Describe a topic to Codex or Claude, for example:

> Use ni-skill to write an article on "AGENTS.md in practice"

`ni-article-workflow` takes over, runs each gated stage, and stops after the initial draft passes validation.

### Individual skills

Describe what you need to trigger the matching skill:

- Discuss the topic with the user or autonomously synthesize its thesis, structure, and style into a complete outline → `ni-insight`
- Lay out an article → `ni-formatter`
- Scrape a URL into Markdown → `ni-url2md`
- Turn a video URL or share text into a local Markdown transcript → `ni-video2md`
- Turn professional sources into a conversation-ready learning guide → `ni-fde-copilot`
- Make a minimal ZINE-style poster → `ni-poster`
- Turn a theme into reviewed multiview images and a validated GLB → `ni-3d-model`
- Diagnose which "unknown" you're facing and get a next-step prompt → `ni-unknown-first`
- Create synchronized Chinese-default and English GitHub READMEs → `ni-readme-guide`
- Use existing source material to turn an ambiguous product or cloud-service requirement into an engineering-reviewable architecture baseline → `ni-design-with-docs`
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

### Video to Markdown (`ni-video2md`)

Optional environment variables:

| Variable | Purpose |
|----------|---------|
| `NI_VIDEO2MD_HOME` | Tool, model, and download cache directory |
| `NI_VIDEO2MD_FFMPEG` / `FFMPEG_PATH` | Path to the ffmpeg executable |
| `NI_VIDEO2MD_WHISPER_CLI` / `WHISPER_CLI` | Path to the whisper-cli executable |
| `NI_VIDEO2MD_MODEL` / `WHISPER_MODEL` | Path to a local Whisper `ggml-*.bin` model |
| `NI_VIDEO2MD_YTDLP` / `YTDLP_PATH` | Path to the yt-dlp executable |
| `NI_VIDEO2MD_JS_RUNTIME` | JavaScript runtime for yt-dlp, such as `node` or `deno` |
| `NI_VIDEO2MD_BROWSER` / `BROWSER_PATH` | Path to Chrome, Edge, or Chromium |

---

## License

MIT
