# ni-readme-guide

[中文](./README.md) | English

Create or redesign synchronized GitHub README files: `README.md` is Simplified Chinese and the default entry point; `README.en.md` is the English counterpart. Keep structure, facts, commands, and links aligned across both files.

## Use cases

- Turn repository code, configuration, examples, and real outputs into a clear README
- Restructure the opening story, quick start, capabilities, architecture, and contribution guide
- Add a compact set of verified, clickable badges aligned across both languages
- Create project-native SVGs, screenshots, diagrams, or other README visual assets
- Audit bilingual parity, broken links, image references, and GitHub rendering safety

## Output contract

Every README copy change delivers both files:

```text
README.md
README.en.md
```

Place reciprocal language links near the top:

```markdown
中文 | [English](./README.en.md)
[中文](./README.md) | English
```

Do not invent features, metrics, compatibility, user counts, or project proof. Lead with real outputs and the shortest successful path. Keep commands, versions, links, badge sources, and code identical across languages. Use badges only for verifiable license, CI, version, platform, or community state, and link them to authoritative targets.

## Usage

```text
Use $ni-readme-guide to rewrite this repository README.
Deliver README.md in Chinese and README.en.md in English with reciprocal language links.
```

Audit an existing bilingual README pair:

```bash
python scripts/audit_readme.py /path/to/repository
```

The script checks the required pair, reciprocal language links, heading levels, code blocks, link and image targets, HTML alt text, and basic SVG safety.

## Resources

- [SKILL.md](./SKILL.md): complete workflow and quality bar
- [references/bilingual-delivery.md](./references/bilingual-delivery.md): bilingual delivery rules
- [references/growth-readme-patterns.md](./references/growth-readme-patterns.md): evidence-led README structure
- [scripts/audit_readme.py](./scripts/audit_readme.py): local bilingual audit

This skill is based on [oil-oil/beautify-github-readme](https://github.com/oil-oil/beautify-github-readme); see [LICENSE.upstream](./LICENSE.upstream) for the upstream license.
