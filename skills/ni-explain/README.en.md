# ni-explain

[中文](./README.md) | English

A writing Skill for Chinese technical proposals, concept explanations, and business/technical reporting. Four modes: **write, rewrite, review, explain**. One goal: **the reader understands in one pass, one way only.**

It starts from the controlled-language approach of ASD-STE100 (Simplified Technical English) and adapts it to common faults in Chinese technical writing, then adds two layers above the sentence: **structure** and **format choice**.

## When to use it

- Technical proposals, design documents, review materials
- Business / technical reporting (expression layer only; judgment and framing belong to `ni-tech-report`)
- READMEs, runbooks, ops / troubleshooting docs
- Explaining an unfamiliar concept to a non-technical reader
- Rewriting, reviewing, or explaining existing text

## Kept unchanged

- Code literals, commands, API paths, environment variables, field names
- Facts, numbers, dates, conclusions, conditions, exceptions, boundaries
- Quoted text, proper nouns, and the author's own words
- **Sentences that are already fine** (guardrail §0.4: if it is clear, leave it alone)

## Three layers of clarity

| Layer | Means | Reference |
|---|---|---|
| Sentence | Controlled Chinese: one word per concept, no empty verbs, named actors, sentences ≤50 chars (steps ≤40) | `references/rules-zh.md` |
| Structure | Conclusion first, known→unknown, one judgment per paragraph, map before streets | `references/explain-patterns.md` |
| Format | Prose → list/table → diagram → HTML → video script, chosen by how hard it is to read | `references/explain-patterns.md` |

## Four modes

| Mode | Input | Output |
|---|---|---|
| write | material / outline | clear text following the rules |
| rewrite | existing text | clearer version (facts kept, wording only) |
| review | existing text | a list of problems, no rewrite |
| explain | a concept / plan | the right format + an explanation method, from scratch |

## Rules at a glance

The full rules are in [`references/rules-zh.md`](./references/rules-zh.md), across 10 chapters, opening with a **top-priority guardrail section**:

- **Guardrails (0)**: same name for the same object; conditions / exceptions stay attached to their action; keep advice, requirements, and possibility distinct; **if it is already clear, leave it — never delete reasons or boundaries to be shorter**
- **Words / noun phrases (1–2)**: one word per concept, no vague words, at most one modifier before a noun
- **Verbs (3)**: no empty verbs, named actors (active voice), requirement words 应 / 宜 / 可
- **Sentences (4)**: one idea per sentence, subjects written out, pronouns point to one thing, single-meaning connectives
- **Procedures (5)**: one instruction per step, start with an imperative verb, condition first
- **Descriptive writing (6)**: conclusion first, one topic per paragraph, numbers carry their conditions
- **Warnings (7)**: before the step, instruction first then risk, two levels (warning / caution)
- **Punctuation and length (8)**: full-width punctuation, spacing around Latin text, date formats
- **Writing practices (9)**: consistent terms, code verbatim, no Chinese AI-tells

## Boundary with ni-tech-report

`ni-tech-report` owns "does the judgment hold" (premise / stance / evidence / closure); `ni-explain` owns "can this sentence be understood". **On reports, ni-explain borrows sentences only, never touches judgments** — the anti-idiom rule, length limits, and reordering rules all yield to the report's value frame. Missing judgment at the content level is out of its scope: it does not hand off or redirect.

## Borrowing from STE

The controlled-Chinese rules borrow the nine-chapter structure and the anti-misreading principles of ASD-STE100: consistent terms, active voice, one action per step, conditions before actions, two warning levels, and no dropped sentence parts.

**But this is not a Chinese version of STE, and it does not certify STE compliance:**

- STE's core is the **controlled dictionary** in Part 2 (about 900 approved words in Issue 9); ni-explain has **no controlled dictionary**, only banned word classes plus a project glossary.
- Sentence length: STE uses 20 / 25 English words; this Skill uses 40 / 50 Chinese characters. STE itself states its word limits do not transfer to other languages.
- Mechanical check results only mark "places to look" — they **do not indicate STE compliance**.

See the [ASD-STE100 official page](https://www.asd-ste100.org/) for the standard.

## Quick start

```bash
# Mechanical check: reports "places to look", not verdicts. 确定=mechanical; 存疑=judgment (may be false positives)
python scripts/check.py your-plan.md

# Offline self-check
python tests/smoke_test.py
```

## Repository layout

```text
ni-explain/
├── SKILL.md                       # entry: four modes + three layers + flow
├── references/
│   ├── rules-zh.md                # controlled Chinese rules (guardrails + 10 chapters)
│   ├── explain-patterns.md        # structure + format ladder + explanation method + five ways to shorten
│   └── output-template.md         # four delivery formats
├── scripts/check.py               # mechanical check (stdlib)
├── tests/                         # smoke + contract tests
├── evals/                         # skill-up evaluation (5 cases)
└── README.md / README.en.md
```

## Evaluation and self-check

```bash
python tests/smoke_test.py
python -m unittest tests/test_skill_contract.py
```

`evals/` is a skill-up evaluation config (5 cases: rewrite empty verbs / review without rewriting / explain picks a format / keep report framing without redirecting / strip idioms).

## Rule sources

The controlled Chinese rules follow the nine-chapter structure of ASD-STE100; **the rule wording is authored in this repository**, only the rule ideas are borrowed. The guardrails and the Chinese AI-tell list reference [tw93/Waza](https://github.com/tw93/Waza) (MIT).
