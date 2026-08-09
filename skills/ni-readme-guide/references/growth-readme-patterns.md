# Evidence-led README growth patterns

Use these patterns selectively. They are adapted from the [GitHub README Template Guide](https://gingiris.github.io/growth-tools/blog/2026/04/02/github-readme-template-guide/) and constrained by repository evidence. Treat the article's performance figures as author-reported observations, not universal guarantees.

## Opening stack

Build the first screen from the strongest available elements:

1. Project name and project-native visual identity.
2. One concise pitch answering what, difference, and audience.
3. Primary actions such as quick start, demo, or documentation.
4. Real screenshot, output, or demonstration.

Do not add empty placeholders just to complete the stack. A repository without a demo should show a real output, test result, architecture cue, or concise example instead.

## Quick start

Prefer the shortest end-to-end success path:

```text
Install → Configure only if required → Run or verify
```

- Aim for three steps or fewer.
- Make every command copyable.
- State prerequisites before the commands.
- Include the observable success result.
- Move advanced configuration to docs or a later section.
- Test commands locally when the environment allows it.

## Optional momentum chart

For a public project with meaningful release history, a Star History chart can make project activity visible. Add it only when the user accepts the external service and the repository can support the claim. It is optional context, not proof of quality or adoption.

## Scannable capability proof

Use a short table or compact list when visitors compare capabilities. Each row should pair a capability with a concrete outcome or evidence. Avoid long adjective-only feature lists.

Prefer:

```markdown
| Capability | What it lets you do |
| --- | --- |
| Local cache | Resume work without fetching the same source again |
```

Avoid:

```markdown
- Powerful
- Fast
- Modern
```

## Architecture and FAQ

Add an architecture diagram when several components or state transitions are hard to explain linearly. Keep it small enough to understand in roughly ten seconds and repeat essential detail in Markdown.

Add FAQ or troubleshooting entries only for real questions or common setup failures. Do not manufacture questions for section-count completeness.

## Contribution guidance

Replace generic invitations with an executable path:

1. where to read contribution rules;
2. how to create a branch or change;
3. which tests/checks to run;
4. what a useful PR description contains.

Do not promise response or merge times unless the repository documents and sustains them.

## Selection test

Keep a module only if it answers one of these:

- What is this?
- Why should the intended user care?
- Can I trust the claim?
- How do I succeed quickly?
- How does it work?
- What are the limits?
- How can I contribute or get help?

Remove modules that exist only because a template included them.
