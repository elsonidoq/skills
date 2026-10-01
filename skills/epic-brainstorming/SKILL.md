---
name: epic-brainstorming
description: Use when a manager must decide whether unresolved design or owner-direction questions require a bounded brainstorm before producing downstream artifacts.
---

# EPIC Brainstorming

Provide the single shared brainstorming mechanism for workflow managers. It preserves
owner direction; it does not create a specification, plan, task list, or implementation.

## Capability preflight

Before using this skill, verify that the runtime can ask the owner questions and that the
manager can persist the selected source, decisions, deferrals, and handoff according to
project conventions. Verify a usable owner-selected `sonnet-class` binding before assigning
gate assessment or decision application. If a required capability is unavailable, report the
missing capability and stop before downstream production. When the runtime's permitted fallback
is prose interaction, ask in prose and end the turn; do not continue downstream or infer an
answer. A manager's explicit mandatory preflight may instead stop before the question is posed.
Do not substitute an unavailable interactive dialogue with guessed decisions.

The calling manager supplies a bounded source and the next-stage readiness target. It must
read applicable repository instructions, principles, source evidence, and any applicable
memory before this mechanism. For a selected brief, edits stay inside its selected section;
for a direct requirement, the durable requirement/task artifact is the bounded source.

## 1. Gate assessment

Have bounded `sonnet-class` work return a first line that is exactly one of:

- `NO_BRAINSTORM_NEEDED` — direction is settled, or remaining ambiguity is mechanical or
  answerable from the source/evidence. State why the target is ready for the next stage.
- `BRAINSTORM_NEEDED` — only when an open-ended design question, owner product-direction
  decision, or material technical trade-off blocks downstream work.

Bias toward `NO_BRAINSTORM_NEEDED`. Do not invoke brainstorming for task ordering, naming,
file placement, batch grouping, bounded clarification, or a decision with an obvious
mechanical default.

For `BRAINSTORM_NEEDED`, provide `## Brainstorm agenda` with no more than three items. Each
item states its topic, type (`open-design`, `product-decision`, or `technical-tradeoff`), why
it blocks readiness, two to four concrete alternatives, and a recommended direction.

## 2. Owner dialogue

The orchestrator, not a delegated worker, conducts the dialogue. Present one material item
at a time through the available question capability. Offer concrete alternatives and a
recommendation for product decisions and technical trade-offs; converge open-design dialogue
on a specific downstream-ready direction. Record each result as:

```text
## [item]
Decision: [direction] — [detail]
```

Record owner deferrals, including their rationale. For a missing question capability, use the
permitted prose-and-end-turn fallback when available, then stop; otherwise report the stop. It
is never permission to infer a material decision.

## 3. Apply decisions

Use bounded `sonnet-class` work to apply exactly the recorded owner decisions to the supplied
bounded source. Update only claims affected by those decisions: settled decisions, outcome,
acceptance criteria, exclusions, and open questions as applicable. Preserve the source's
format; add a concise deferred note when the owner deferred work. Do not invent scope,
rewrite unrelated sections, or replace the next stage with a plan.

## Durable handoff and resume

Persist the gate result, agenda when present, owner decisions, deferrals, changed source,
and concise handoff context using existing project conventions. Handoff context includes
settled decisions, trade-offs, intentional deferrals, uncertainties, and the next-stage
readiness target. On resume, validate the bounded source and decision record; if owner
answers are missing, re-present the saved agenda instead of regenerating decisions. If the
source or decisions changed materially, re-run the gate before downstream production.
