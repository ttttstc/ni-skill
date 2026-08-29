# ni-design-with-docs

[中文](./README.md) | English

> Provide decision-relevant research, align with the user through interviews, derive the smallest sufficient product and high-level architecture from first principles, and pass independent architecture and security reviews.

`ni-design-with-docs` V1 is for new product or platform requirements. It does not analyze an existing codebase or expand an ambiguous request directly into a long report. It first closes the decisions that change product behavior, system boundaries, impact scope, high-level responsibilities, quality, security, or acceptance.

## Quick start

Codex:

```text
$ni-design-with-docs 我需要为平台支持某项新能力。目标是……；已知业务和平台约束如下……
```

Claude Code:

```text
/ni-design-with-docs 我需要为平台支持某项新能力。目标是……；已知业务和平台约束如下……
```

The first substantive response must provide a current understanding, decision-relevant research input, and the first 3–5 questions. It must not start architecture design.

## Core guarantees

- Design starts only after an interview, an alignment summary, and explicit user confirmation.
- The user may accept every recommendation in a round or authorize recommendations for all remaining branches; no decision is omitted.
- Research process, interview transcripts, tutorial terminology, review output, and skill policy remain in the workbench.
- The formal report uses plain language, includes a directly locatable product plan and system specification, and focuses on user outcomes, system boundaries and impact scope, key decisions, the main flow, verifiable quality requirements, concrete security problems, failure handling, rollout, and acceptance.
- After the interview, the designer derives system boundaries from confirmed input. The user is not asked to draw the architecture, and code is not scanned to invent internal facts.
- The design chooses the smallest set of responsibilities and relationships that completely solves the problem.
- The report has six top-level chapters. Overall design moves from conclusion to product plan, boundaries and responsibilities, system specification, flow/data/state, and key decisions and collaboration constraints.
- Main flows use UML sequence or activity diagrams, core states use UML state diagrams, cross-boundary data uses data-flow diagrams, and multi-module responsibilities use a module architecture relationship diagram. L0 and L1 are conditional. Key decisions, responsibilities, and collaboration constraints remain authoritative in text instead of existing only in diagrams.
- The formal report normally keeps 1–2 tables and never more than 3. Quality, security, failure, and acceptance content uses direct blocks such as what-happens/system-response/how-to-verify instead of wide tables or abstract labels.
- The report is Chinese-first and does not invent unnecessary modules or terminology.
- Independent reviews focus on material contradictions. If a review fails, the skill lists the conclusion, minimum fixes, impact of not fixing, and recommendation for user confirmation before editing and re-reviewing.
- Formal delivery requires independent architecture and security reviews.

## Workflow

```text
任务与证据准备
  → 调研输入与分轮访谈
  → 对齐摘要
  → 推荐决策清单与用户确认
  → 最小充分设计
  → 正式草稿
  → 独立架构评审 + 独立安全评审
  → 正式方案
```

“Use every recommendation in this round” closes only the current questions. The user may also authorize recommendations for all remaining branches to reduce back-and-forth. The skill still traverses the decision tree and records each choice, rationale, and impact.

When the user says to skip the interview and use recommendations, the skill enters the recommendation fast path instead of skipping decisions. The Agent investigates facts it can discover. User goals, internal authority, commercial commitments, or compliance decisions that lack a reliable recommendation still require a question. Every choice enters the alignment summary, and design starts only after confirmation.

## Research and report boundary

Research before the interview answers only questions that can change scope, collaboration constraints, quality, security, or acceptance. It prioritizes user-provided material, official standards, official product documentation, and official reference implementations.

The formal report has no default research-process, interview-transcript, or tutorial-glossary section. An external source appears only where it supports a material fact or decision.

Non-goals contain only user-confirmed business or product scope. The skill's own implementation-depth policy must not be presented as a project non-goal.

## Security review

Every design determines security applicability. Changes involving identity, permissions, sensitive data, secrets, external input, trust boundaries, high-value operations, or resource risk must:

- identify assets, actors, entry points, data flows, and trust boundaries;
- analyze the main threats and abuse paths;
- locate controls in product behavior, responsibilities, collaboration constraints, or runtime paths;
- state residual risk and ownership;
- define executable security acceptance scenarios;
- pass an independent security review.

When the security impact is not material, the report gives a short, concrete rationale. The security reviewer validates the rationale instead of requiring a generic checklist.

## Formal deliverable

The tailored Markdown design uses six top-level chapters and selects only relevant detail within them:

- a 2–3 sentence overall design conclusion, goals, and business scope;
- a complete product plan covering users, problems, entry points, actions, states, feedback, and support boundaries;
- system boundaries, impact scope, and responsibilities;
- system rules for permissions, data, states, failures, and architecture-changing hard limits;
- key product and architecture decisions;
- necessary responsibility, runtime, data, and collaboration constraints;
- UML sequence/activity diagrams, UML state diagrams, data-flow diagrams, and module architecture relationship diagrams when applicable;
- quality requirements stated as what-happens, system-response, and how-to-verify blocks;
- security problems, impact, solutions, and verification;
- failure handling and troubleshooting;
- rollout, compatibility, and rollback;
- acceptance, risks, and engineering next steps.

The template is not a completeness checklist. Empty subsections may be merged or removed, while the six top-level chapters and their conclusion-to-detail order stay stable.

## Quality gates

- G0: user alignment
- G1: complete product behavior
- G2: system boundaries and impact scope
- G3: architecture decisions and responsibilities
- G4: runtime, data, and collaboration constraints
- G5: security and trust boundaries
- G6: quality, failure, and operability
- G7: evolution and reversibility
- G8: acceptance and traceability
- G9: readability and maintainability

The architecture reviewer owns G0–G4 and G6–G9. The security reviewer owns G5. Both must pass before release.

## Structure

```text
skills/ni-design-with-docs/
├── SKILL.md
├── README.md
├── README.en.md
├── agents/
│   ├── openai.yaml
│   ├── researcher.md
│   ├── reviewer.md
│   └── security-reviewer.md
├── eval/
│   ├── gates.md
│   └── scenarios.md
├── references/
│   ├── 01-workflow.md
│   ├── 02-concepts-and-interview.md
│   ├── 03-current-state-and-research.md
│   ├── 04-architecture-design.md
│   ├── 05-views-interfaces-constraints.md
│   ├── 06-testing-and-output.md
│   ├── 07-writing-style.md
│   └── 08-security-review.md
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

See [eval/scenarios.md](./eval/scenarios.md) for behavioral forward-test scenarios.

## License

[MIT](../../LICENSE)
