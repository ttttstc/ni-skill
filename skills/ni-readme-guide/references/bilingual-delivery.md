# Bilingual README delivery

## File contract

Use this pair unless the user explicitly requires another repository convention:

```text
README.md       Simplified Chinese and default landing page
README.en.md    English
```

Place these switches near the top:

```markdown
中文 | [English](./README.en.md)
```

```markdown
[中文](./README.md) | English
```

Do not use absolute GitHub URLs for language switching. Relative links survive forks, branches, and local previews.

## Draft once, localize twice

Create a language-neutral content matrix before prose:

| Section role | Evidence | Chinese copy goal | English copy goal |
| --- | --- | --- | --- |
| Pitch | package metadata + source | natural, concrete value | natural, concrete value |
| Proof | screenshot/output/test | same artifact and claim | same artifact and claim |
| Quick start | verified commands | exact commands | exact commands |
| Limits | code/config/docs | explicit boundary | same boundary |

Use the matrix to prevent translation drift. Do not translate one finished README mechanically and assume parity.

## Keep invariant content exact

Keep these identical across both files:

- shell commands and code;
- filenames, flags, environment variables, API names, and identifiers;
- version numbers, ports, URLs, badge sources and targets, and image paths;
- measured values and qualified claims.

Translate prose, headings, captions, table labels, alt text, and callouts naturally. Do not leave Chinese prose in the English file or English filler in the Chinese file when a normal translation exists.

## Parity review

Compare the pair section by section:

1. Same section roles and order, unless language-specific navigation requires a tiny difference.
2. Same features, limitations, requirements, and contribution steps.
3. Same code blocks and command order.
4. Same badges, images, destinations, and factual numbers.
5. Same level of certainty; do not make one translation more promotional.
6. Both language links resolve with exact filename casing.

If a concept has no clean direct translation, preserve the canonical technical term and explain it briefly in each language instead of inventing different terminology.

## Existing repositories

When an existing repository uses `README.md` for English plus `README.zh-CN.md` or another convention:

1. Inspect references from docs, manifests, websites, and other Markdown files.
2. Explain that this skill defaults `README.md` to Chinese and `README.en.md` to English.
3. If migration is in scope, rename/update both files and repair local inbound links.
4. If compatibility is required, follow the user-approved convention but still produce a visible reciprocal switch and record the exception.

Never silently discard content present in only one existing language. Reconcile it against repository evidence first.
