# ni-fde-copilot

[中文](./README.md) | English

> Turn long, heterogeneous, expert-oriented sources into a domain learning guide that a smart outsider can understand, judge, apply, and use in expert conversations.

`ni-fde-copilot` is a standalone FDE domain-learning skill. It does not summarize sources in their original order. It first builds a minimum sufficient domain model, detects the Cognitive Gaps that would block an outsider, and reorganizes the material along a causally continuous Learning Spine. A strict two-phase gate is the default, preventing long-form generation before the topic, scope, and knowledge structure are aligned.

## Use cases

- Enter an unfamiliar industry before a client meeting
- Study professional books, PDFs, research reports, or internal proposals
- Convert course videos, slides, charts, and whiteboards into self-contained prose
- Interpret expert interviews, meeting recordings, and fragmented transcripts
- Reach conversation-ready depth instead of settling for a high-level summary

## Quick start

After installing the repository, provide the sources in a new Agent session, invoke `$ni-fde-copilot`, describe the meeting or learning goal, and ask for the Learning Blueprint before the full guide.

The first response contains only the five-part Learning Blueprint:

1. Topic identification
2. Knowledge structure
3. Source case inventory
4. Predicted Cognitive Gaps
5. Target capabilities

Only after confirmation does the skill produce the Guided Learning Guide, transfer challenges, and Conversation Readiness.

## How it works

The workflow is:

1. Frame the Learning Mission.
2. Inventory and read all sources.
3. Build the domain model and Cognitive Gaps.
4. Construct the causally continuous Learning Spine.
5. Deliver the five-part Learning Blueprint and wait for confirmation.
6. Write the Guided Learning Guide after confirmation.
7. Audit quality, add transfer challenges, and report Conversation Readiness.

### Phase 1: Learning Blueprint

Phase 1 aligns the topic, scope, domain model, cases, Cognitive Gaps, learning path, and target capabilities. The skill does not draft or preview Phase 2 before confirmation.

### Phase 2: Guided Learning Guide

The guide progresses through confusion, mechanism, case validation, a new question, and the next concept. Every core concept covers its definition, importance, mechanism, recognition, application, common mistakes, close distinctions, boundaries, and practical consequence. Every reasoning-bearing case explains the scenario, mechanism, alternative approach, and transferable principle.

## Inputs and degradation boundaries

The skill can work with text, webpages, PDFs, books, reports, slides, charts, video, audio, and transcripts, subject to the tools available in the current Agent environment.

- Long sources are split by semantic boundaries and tracked in a Source Inventory so material does not disappear silently.
- Videos and demonstrations require inspection of reasoning-bearing visual information, not transcripts alone.
- Audio and spoken material require pronoun resolution, speaker context, and preservation of useful trial-and-error.
- If an in-scope source is inaccessible, incomplete, or missing critical visual context, the skill blocks that portion explicitly instead of pretending it was read.

## Evidence boundaries

Load-bearing claims use five evidence states:

| State | Meaning |
|---|---|
| `SOURCE` | Explicitly supported by supplied material |
| `INFERENCE` | A reviewable deduction from supplied material |
| `EXTERNAL` | Verified external knowledge used to close a critical Cognitive Gap |
| `UNKNOWN` | Not answerable from current evidence |
| `NEED VALIDATION` | Reasonable to discuss, but unsafe to treat as settled in practice |

External knowledge may close a blocking prerequisite or mechanism Gap. It must not silently rewrite source claims or hide real conflicts between sources.

## Rapid exception

The skill skips the default gate only when the user explicitly asks for Rapid mode, an extremely time-constrained version, one-pass generation, or no confirmation step. Rapid changes knowledge selection: it prioritizes the Root Problem, high-leverage concepts, core mechanisms, key distinctions, decision rules, failure boundaries, Unknowns, and expert questions, while naming active omissions.

If the user explicitly asks to confirm before writing, Rapid cannot bypass the gate.

## Structure

```text
ni-fde-copilot/
├── SKILL.md
├── README.md
├── README.en.md
├── agents/openai.yaml
├── references/
│   ├── domain-model.md
│   ├── cognitive-gap-model.md
│   ├── writing-standard.md
│   └── quality-rubric.md
├── evals/
│   ├── technical-source.md
│   ├── industry-source.md
│   └── expert-transcript.md
└── tests/test_skill_contract.py
```

The three eval inputs cover a technical reliability note, B2B SaaS operating material, and an expert transcript that depends on missing visual context. Offline contract tests check the confirmation gate, five-part Blueprint, concept and case coverage, evidence states, oral and visual rules, transfer challenges, and plugin registration.

Run the contract tests:

```bash
python -m unittest discover -s skills/ni-fde-copilot/tests -p "test_*.py" -v
```

## Capability boundary

The target is conversation-ready domain fluency, not a substitute for licensed experts, full professional training, or real-world project validation. Conversation Readiness explicitly separates well-supported topics, topics that can be reasoned about but require validation, topics unsupported by current sources, and the highest-value questions to ask experts next.

## License

[MIT](../../LICENSE)
