---
name: ni-readme-guide
description: Create, rewrite, beautify, or audit GitHub repository READMEs as a synchronized Chinese-default and English pair, with reciprocal language links, verified functional badges, project-native visuals, real proof, concise quick starts, and maintainable Markdown. Use when a user asks to write, redesign, improve, localize, translate, visually upgrade, or review a README; create README heroes, badges, diagrams, screenshots, or optional GitHub-safe GIF assets; or turn a repository homepage into a clear bilingual project story.
---

# NI README Guide

Build a trustworthy GitHub homepage from repository evidence. Keep Chinese as the default README, deliver an English counterpart every time README copy changes, and use visuals only when they communicate identity, proof, or mechanism.

This skill is derived from `oil-oil/beautify-github-readme` at commit `55bdb1c05414cd7a0cf911d02e55ece79777206e`. Preserve its project-native design, GitHub-safe asset, and approval boundaries. See `LICENSE.upstream` for the upstream MIT notice.

## Non-negotiable bilingual contract

For README creation, rewrite, or copy editing, always deliver both files:

```text
README.md       Simplified Chinese; repository default
README.en.md    English
```

Put a visible language switch near the top of both files, before the main body:

```markdown
<!-- README.md -->
中文 | [English](./README.en.md)

<!-- README.en.md -->
[中文](./README.md) | English
```

- Keep the links relative so forks and local previews work.
- Keep headings, examples, claims, links, badges, and section order synchronized.
- Preserve commands, identifiers, API names, URLs, and version numbers exactly across languages.
- Translate meaning, not sentence shape. Use natural Chinese in `README.md` and natural English in `README.en.md`.
- Treat a one-language change as incomplete until the counterpart is updated.
- If an established repository uses another language-file convention, preserve compatibility only when the user explicitly requires it; otherwise migrate to this contract and update inbound local links.
- For an audit-only request, remain read-only. Report a missing or stale counterpart instead of creating it without permission.

Read [references/bilingual-delivery.md](references/bilingual-delivery.md) before writing or changing README copy.

## Choose one mode

- **README mode** — create or improve information order, copy, proof, Markdown, bilingual parity, and visual system.
- **Asset-only mode** — create only requested SVG/PNG/WebP/GIF assets. Do not change either README or embed assets without explicit scope.
- **Audit mode** — inspect clarity, hierarchy, trust, bilingual parity, links, images, and maintenance cost without editing.

If the scope is unclear, ask whether the user wants both READMEs improved, visual assets only, or a read-only audit. Do not infer permission to publish, commit, push, or open a PR.

## Workflow

### 1. Inspect repository evidence

Read the existing README files, repository tree, package metadata, release/install configuration, license, contribution instructions, tests, screenshots, examples, design tokens, and real outputs. For a GitHub URL, inspect the current default branch.

Identify:

```text
Audience:
Project category:
One-sentence value:
Differentiator:
Primary proof:
First successful action:
Supported claims:
Unknown or unverifiable claims:
Native visual material:
```

Never invent adoption, benchmarks, compatibility, testimonials, response times, community links, or features. Remove or qualify unsupported claims.

### 2. Plan the bilingual content matrix

Before drafting prose, freeze one shared outline and evidence set for both languages. Use [references/growth-readme-patterns.md](references/growth-readme-patterns.md) to select modules from evidence rather than forcing a universal template.

Strong default order:

1. Language switch.
2. Project-native hero or title.
3. Plain-language pitch: what it is, why it differs, and who it serves.
4. Verified functional badges and primary actions.
5. Real demo, screenshot, output, or other proof.
6. Quick start: shortest working path, preferably no more than three steps.
7. Scannable capabilities or use cases.
8. Mechanism or architecture when it improves understanding.
9. Configuration, compatibility, limits, and troubleshooting.
10. Concrete contribution process and license.

Move proof and first success early. Keep advanced internals, long changelogs, and exhaustive API details in dedicated docs.

### 3. Write the opening clearly

- Make the first paragraph answer: What is this? Why is it different? Who is it for?
- Keep the shortest copy-paste quick start near the opening, ideally within the first 200 words when prerequisites allow.
- Add only badges backed by live repository state: license, CI, release/package version, supported platform or distribution, and an active community channel.
- Link every badge to its authoritative target. Omit any badge whose source, destination, or claim cannot be verified.
- Keep the set compact. Do not add decorative, redundant, or generic promotional badges.
- Use descriptive headings and image alt text.
- Add FAQ or troubleshooting only for real recurring questions or likely setup failures.
- Add a Star History chart only for a public project when its momentum is meaningful and the user accepts the external dependency; never treat it as mandatory proof.

### 4. Design from project material

Read [references/visual-direction.md](references/visual-direction.md) and [references/project-native-hero.md](references/project-native-hero.md). Freeze:

```text
Palette: background / foreground / primary / accent / muted
Typography: system stack / scale / weight contrast
Shape: radius / stroke / grid / spacing
Motif: one recurring project-specific cue
Composition: calm / editorial / technical / playful / cinematic
```

Prefer real screenshots, outputs, logos, diagrams, and repository-native artifacts. Do not apply one house style to every project.

For a hero where pure SVG and generated raster material are both credible, explain the tradeoff and confirm implementation before producing it:

- **Pure SVG** — deterministic, lightweight, editable, sharp; best for typography, diagrams, code, icons, and geometry.
- **Hybrid SVG composition** — SVG layout plus optional generated/photographic raster material, published as PNG/WebP; richer but heavier and partly stochastic.

Default to pure SVG when delegated. Generated material must have a project-specific communication job and must not replace stronger real proof. Motion is opt-in; static SVG remains the editable fallback.

### 5. Execute only selected scope

#### README mode

- Create or update `README.md` and `README.en.md` together.
- Preserve one evidence set and section structure while localizing phrasing.
- Use tables or compact lists for feature comparison; use prose for nuance.
- Keep commands copyable and explanations in Markdown. Do not rasterize the whole README.
- Use Mermaid or a GitHub-safe diagram for complex architecture only when it shortens understanding.
- Update local links after any language-file migration.

#### Asset-only mode

- Create assets under `assets/readme/` or a user-approved path.
- Use SVG for deterministic heroes, headers, badges, diagrams, and workflows.
- Use PNG/WebP for screenshots, photos, generated art, or complex compositing.
- Use GIF only after explicit opt-in and retain the static SVG source.
- Provide embed snippets separately. Do not edit either README without approval.

Read [references/github-readme-canvas.md](references/github-readme-canvas.md) and [references/svg-production.md](references/svg-production.md) before creating assets. For hybrid work, read [references/hybrid-svg-production.md](references/hybrid-svg-production.md). For motion, read [references/motion-production.md](references/motion-production.md).

### 6. Validate both languages

Run the bundled audit against the repository root:

```bash
python scripts/audit_readme.py /path/to/repository
```

The audit checks the required pair, reciprocal language links, shared Markdown links and image targets, local image existence, useful HTML alt text, and basic SVG safety. It cannot judge translation quality; manually compare every heading, claim, command, number, and link.

Also verify:

- Quick start commands match repository configuration and succeed when runnable.
- Wide and narrow previews remain readable.
- SVG text is not clipped and required detail survives GitHub scaling.
- Light/dark GitHub surroundings retain contrast.
- No stale one-language section or language-specific broken link remains.
- `git diff` contains only approved README/assets/registration changes.

### 7. Hand off safely

Show local previews and the diff. Report evidence used, claims omitted or qualified, and files deliberately untouched. Commit, push, publish, or open a PR only when explicitly requested.

## Quality bar

- `README.md` is Chinese and is the default; `README.en.md` is English.
- Both language switches work and both documents remain semantically aligned.
- First screen explains project and points to proof or first action.
- Real proof appears before abstract claims.
- Quick start is short, copyable, and verified where possible.
- Badges are useful, verifiable, linked to authoritative targets, and identical across languages.
- Visual direction belongs to the project, not this skill.
- README is clearer, not merely longer or more decorated.
- Essential content remains usable when images fail.
- No fabricated growth, usage, compatibility, or maintenance claims.

## Invocation examples

```text
Use $ni-readme-guide to rewrite this repository README. Deliver README.md in Chinese and README.en.md in English with reciprocal language links.
```

```text
Use $ni-readme-guide to audit both README languages for clarity, parity, broken links, and weak proof. Do not edit files.
```

```text
Use $ni-readme-guide to create one project-native SVG hero without modifying either README.
```
