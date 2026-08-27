# ni-design-with-docs

[中文](./README.md) | English

> Turn ambiguous product or cloud-service requirements into an engineering-reviewable Markdown architecture baseline through source documents, interviews, public evidence, and independent review.

`ni-design-with-docs` is for product owners, platform architects, and technical leads. It establishes a factual and conceptual baseline before closing the important unknowns in scope, current state, contracts, and constraints. The final result is a product architecture baseline that passes the G0–G10 gates—not a long document generated before the design is understood.

## Quick start

First install `ni-design-with-docs` in the current Agent's skills directory. See the [ni-skill root README](../../README.md) for complete installation instructions.

Codex:

```text
$ni-design-with-docs 我需要为平台支持某项新能力。目标是……；当前已支持……；相关产品、架构和接口资料如下……
```

Claude Code:

```text
/ni-design-with-docs 我需要为平台支持某项新能力。目标是……；当前已支持……；相关产品、架构和接口资料如下……
```

The first response should establish the factual baseline, align the core concepts that affect the design, and ask the first batch of 3–5 architecture questions. The formal baseline is produced only after the information has converged.

## When to use it

| Good fit | Not a fit |
|---|---|
| Creating a product, platform, or cloud-service capability | Writing implementation code or a complete PRD |
| Making a structural enhancement to an existing capability | Designing database tables, classes, methods, or internal DTOs |
| Supporting a third-party protocol, ecosystem, or product behavior | Reverse-engineering an entire codebase by default |
| Converging top-level design from multiple product, architecture, or interface documents | Comparing only two local technical options |
| Defining product shape, L0/L1, major contracts, global constraints, and acceptance | Replacing internal facts and business decisions with vague “best practices” |

## What it delivers

The final Markdown is tailored to the problem, but it cannot omit design-critical information:

| Design area | Result |
|---|---|
| Problem and scope | Background, goals, non-goals, users, and successful outcomes |
| Facts and evidence | Confirmed facts, assumptions, unknowns, public sources, and capability gaps |
| Product and architecture | Product shape, L0/L1, first-level module responsibilities, and necessary views |
| Contracts and constraints | Major interfaces, permissions, data, compatibility, reliability, capacity, and evolution boundaries |
| Verification | Test scenarios, observable acceptance criteria, risks, open questions, and detailed-design boundaries |
| Independent review | A G0–G10 result for every gate; the formal version is released only after all gates pass |

## Workflow

1. Understand the task and source material, then establish a factual baseline.
2. Align core concepts and run staged batch interviews.
3. Analyze relevant documents and define current-state capability gaps.
4. Research public sources and converge the key architecture decisions.
5. Design the product shape, L0/L1, necessary views, major interfaces, and global constraints.
6. Derive tests and acceptance criteria, then produce the Markdown draft.
7. Run independent review and revise until the formal baseline can be released.

Each round usually asks only 3–5 questions at the same decision level, with a maximum of 7 for complex cases. Information already supplied by the user is not asked again. Questions that do not change boundaries, contracts, constraints, or acceptance are left to detailed design.

## Source and evidence rules

- Product, architecture, interface, and design documents are analyzed only where they directly affect the current capability.
- The skill does not scan the entire codebase by default; code analysis enters scope only when the user explicitly requests it.
- Public research prioritizes official standards, official product documentation, official reference implementations, and design records.
- Industry practice is evidence, not an automatic user constraint.
- Unverified current-state claims and metrics remain assumptions, unknowns, or items to confirm; numbers are never invented.
- Important sources stay near the design judgment they support, with an explanation of how the evidence affects the decision.

## Review and degradation

During research, 2–4 non-overlapping questions are preferably delegated to independent subagents for parallel evidence collection. If research subagents are unavailable, the main agent may investigate the questions sequentially, but it must mark the degradation explicitly and still check sources, versions, and conflicts.

The independent review before formal delivery cannot degrade into self-review. If the runtime cannot start an independent review subagent, the result must be `BLOCKED`; it cannot claim that G0–G10 passed.

## Structure

```text
skills/ni-design-with-docs/
├── SKILL.md
├── README.md
├── README.en.md
├── agents/
│   ├── openai.yaml
│   ├── researcher.md
│   └── reviewer.md
├── eval/
│   └── gates.md
├── references/
│   ├── 01-workflow.md
│   ├── 02-concepts-and-interview.md
│   ├── 03-current-state-and-research.md
│   ├── 04-architecture-design.md
│   ├── 05-views-interfaces-constraints.md
│   ├── 06-testing-and-output.md
│   └── 07-writing-style.md
├── templates/
│   └── architecture-baseline.md
└── tests/
    └── test_skill_contract.py
```

## Maintainer verification

Run from the repository root:

```bash
python -m unittest skills/ni-design-with-docs/tests/test_skill_contract.py
python skills/ni-readme-guide/scripts/audit_readme.py skills/ni-design-with-docs
```

## License

[MIT](../../LICENSE)
