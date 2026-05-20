# ni-skill

English | [中文](./README.zh.md)

> A content creation skill suite for "低卧扑食" — a WeChat public-account brand by 泥巴猪 (Ni). End-to-end pipeline from topic → research → soul → writing → layout → preflight → publish. Focus: AI / engineering management / DevOps / architecture.

ni-skill is a set of cooperating skills for Claude Code, threading research → soul mining → writing → layout → preflight → publishing into one pipeline. All skills share three engineering ground rules (honest output / self-verify before delivering / explicit degradation), and each skill has its own domain principles on top. Every skill works standalone, and `ni-article-workflow` orchestrates them into a single pipeline.

---

## Prerequisites

- **Claude Code** (with Plugin Marketplace support)
- **Python 3.10+** — only for `ni-draft` (push WeChat drafts)
- **Node.js + Chrome** — only for `ni-url2md` (scrape web pages; first run uses `npx -y bun` to fetch the Bun runtime)

See each skill's `SKILL.md` for its specific dependencies.

---

## Installation

### Option 1: Plugin Marketplace (recommended)

In Claude Code:

```
/plugin marketplace add ttttstc/ni-skill
/plugin install ni-skill@ni-skill
```

### Option 2: Ask the Agent

Just tell Claude:

> Please install skills from github.com/ttttstc/ni-skill

### Option 3: Manual install (only if you can't use the Marketplace)

Claude Code only scans the **immediate children** of `~/.claude/skills/` for `SKILL.md`, so the 9 ni-* sub-skill directories must be **flattened to the root**:

```bash
git clone https://github.com/ttttstc/ni-skill.git
mv ni-skill/skills/* ~/.claude/skills/
```

PowerShell:

```powershell
git clone https://github.com/ttttstc/ni-skill.git
Move-Item ni-skill\skills\* $HOME\.claude\skills\
```

> This approach **loses bundled management and auto-updates** — prefer Option 1 when possible. Cloning directly into `~/.claude/skills/ni-skill/` **won't work** — Claude Code does not recurse into nested directories.

---

## Skills

9 skills, ordered by pipeline stage:

| Stage | Skill | When to trigger |
|-------|-------|-----------------|
| Source | [`ni-url2md`](./skills/ni-url2md) | Scrape any URL into Markdown (Chrome CDP, supports `--wait` for logged-in pages) |
| Research | [`ni-research`](./skills/ni-research) | Trend check, competitor scan (binary output), named-source material |
| Soul | [`ni-insight`](./skills/ni-insight) ⭐ | Angle discovery → user collision → soul lock. **The suite's North Star** |
| Writing | [`ni-writer`](./skills/ni-writer) | Long-form writing in a hybrid Orwell + Calvino + Borges voice, four-layer self-check |
| Layout | [`ni-formatter`](./skills/ni-formatter) | Minimal 5-module set (part / callout / quote / steps / verdict) |
| Preflight | [`ni-inspect`](./skills/ni-inspect) | Metadata / content quality / structure checks, with built-in banned-word list |
| Imagery | [`ni-article-image-gen`](./skills/ni-article-image-gen) | 1 cover + 9 inline image prompts, default claymation style, switchable |
| Publish | [`ni-draft`](./skills/ni-draft) | Markdown → WeChat-compatible HTML → draft inbox (Python, zero binary deps) |
| Orchestration | [`ni-article-workflow`](./skills/ni-article-workflow) | Threads the 8 skills above into a state-machine-driven pipeline with resume support |

Every skill is **independently runnable** and also orchestratable by `ni-article-workflow`.

---

## Principles

`ni-writer`'s writing style (seven values + four hard rules + seven traits of voice) is its own concern. The other 8 skills each have their own engineering principles, all roughly clustered around three things:

- **Honest output**: no fabrication, no overstating, no claiming success on failure.
- **Self-verify before delivering**: each skill runs its own checklist before output.
- **Explicit degradation**: when external dependencies fail, provide a degraded path, mark it clearly, never dump a stack trace.

Each skill also has its own domain principles — e.g. `ni-insight` requires "angles must hook to real material + user must approve", `ni-formatter` requires "no module stuffing + verdict must exist", `ni-draft` requires "translate errors to plain language + always fall back to local HTML". See each skill's SKILL.md.

---

## Full Pipeline

```
topic
  ↓
ni-research        trend + competitor + material
  ↓
ni-insight  ⭐     mine the soul, lock a 10-20 char core thesis (passes the "would-anyone-comment-on-this-on-Moments" test)
  ↓
ni-writer          expand into long-form following the style + soul
  ↓
ni-formatter       dress it: minimal 5-module set
  ↓
ni-inspect         health check: BLOCKED → rewrite / WARNING → notify / ready → pass
  ↓
ni-article-image-gen   1 cover + 9 inline image prompts (optional)
  ↓
ni-draft           push to WeChat draft inbox (cover is a placeholder, set the real one in the dashboard)
  ↓
done (find the draft in WeChat back-office; fine-tune before publishing)
```

Any stage that degrades or fails will tell you explicitly — you decide what to do next.

---

## How to use

### Full pipeline

Just say:

> Use ni-skill to write a full piece on "should we still write AGENTS.md".

`ni-article-workflow` takes over, asks for an article-name, creates a working directory, and walks the stages.

### Single skill

Say what you want:

- "Help me find an angle for this draft" → `ni-insight`
- "Lay this out" → `ni-formatter`
- "Scrape this URL into markdown" → `ni-url2md`
- "Push to drafts" → `ni-draft`

Each skill's SKILL.md has the full trigger-word list.

---

## Configuration

### WeChat draft push (ni-draft)

Env vars:

```bash
WECHAT_APPID=wx_xxxxxxxx
WECHAT_SECRET=xxxxxxxxxxxxxxxx
```

Or `~/.config/ni-skill/config.yaml`:

```yaml
wechat:
  appid: wx_xxxxxxxx
  secret: xxxxxxxxxxxxxxxx
```

Get credentials from WeChat back-office → "设置与开发 → 基本配置". Don't forget to add the calling machine's IP to the allowlist.

### Web scraping (ni-url2md)

Optional env vars:

| Variable | Purpose |
|----------|---------|
| `URL_CHROME_PATH` | Specify Chrome when not in the default location |
| `URL_DATA_DIR` | Default output directory |
| `URL_CHROME_PROFILE_DIR` | Persist cookies for logged-in sessions |

---

## License

MIT
