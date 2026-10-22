---
name: planning-brainstorming
description: Use when unresolved design or owner-direction questions may block scope assessment or downstream planning artifacts.
---

# Planning Brainstorming

Provide the single shared brainstorming mechanism for workflow managers. It preserves
owner direction; it does not create a specification, plan, task list, or implementation.

## Capability preflight

Before using this skill, verify that the runtime can ask the owner questions and that the
planner can retain the selected source bounds, decisions, deferrals and handoff. In
preselection mode retain interim answers in available session history, while allowing
read-only inspection of existing project evidence; in selected-production or legacy
repair mode use established project artifacts.

Before gate assessment or authorized decision application, resolve the caller's
`brainstorm-assessment` or `brainstorm-application` operation through the planner's
[shared saved-assignment contract](../planner/SKILL.md#saved-planner-assignments).
Both operations use the shared saved `brainstorming` assignment. Pass its exact binding
unchanged in the bounded brief and dispatch; verify it is permitted and callable only
at dispatch. A missing, malformed, unsupported, or unavailable assignment stops that
affected operation with the contract's focused owner-correction question and no
candidate recommendation, inference, substitution, or fallback. The parent still
conducts owner dialogue. This selection does not authorize implementation work.

Implementation-only batching, task-count and REQUIRED-item rules are not planning prerequisites. If a required capability is unavailable, report the
missing capability and stop before downstream production. When the runtime's permitted fallback
is prose interaction, ask in prose and end the turn; do not continue downstream or infer an
answer. A manager's explicit mandatory preflight may instead stop before the question is posed.
Do not substitute an unavailable interactive dialogue with guessed decisions.

The caller supplies the request or bounded source, mode, and next-stage readiness target.
Read applicable repository instructions, principles, source evidence and applicable memory.
Before gate assessment, consult [save-adr](../save-adr/SKILL.md)'s **Consult and
propagate** contract. In all modes, including standalone fresh preselection, allow
read-only discovery of existing project decision ownership, the whole decision index and
relevant accepted records in full before affected gate assessment, even when not supplied
by the caller. Use supplied constraints and session history as additional context, not a
discovery limit. Preselection forbids writes or artifact production, not reading existing
decision artifacts. An absent decision store alone is nonblocking; material authority or
conflicts follow the canonical contract. Preselection target is informed scope
assessment, not immediate task production. Do not select TinySpec/Standard here. Generic
brainstorming's design-depth labels do not replace the planner's mandatory user choice.

## Modes

- **Preselection:** read-only source inspection and owner dialogue; no source edits or
  planning/decision files. Keep exact answers, rationale and deferrals in session history.
  If interrupted and evidence is unavailable, ask for missing answers instead of guessing.
- **Selected production / legacy repair:** apply recorded decisions to the explicitly
  selected source/section only and persist evidence using established project conventions.
  A task-embedded requirement remains valid for legacy repair; no new source shape is imposed.

## 1. Gate assessment

Apply [Parsimony and Actionable Checks](../planner/references/parsimony.md). Apply before raising material owner questions. Applicable accepted outcome constraints and source links inform readiness and whether an owner question is material; they do not replace current bounded-source content or existing material-question authority.

Have bounded work using the shared saved `brainstorming` assignment return a first line
that is exactly one of:

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
on a specific downstream-ready direction. Retain each result, with the owner's rationale,
in the mode's permitted carrier as:

```text
## [item]
Decision: [direction] — [detail]
```

Record owner deferrals, including their rationale. For a missing question capability, use the
permitted prose-and-end-turn fallback when available, then stop; otherwise report the stop. It
is never permission to infer a material decision.

## 3. Apply decisions

Only in selected-production or legacy-repair mode, use bounded work with the shared saved
`brainstorming` assignment to apply exactly the recorded owner decisions to the supplied bounded source. Update only
claims affected by those decisions: settled decisions, outcome,
acceptance criteria, exclusions, and open questions as applicable. Preserve the source's
format; add a concise deferred note when the owner deferred work. Do not invent scope,
rewrite unrelated sections, or replace the next stage with a plan.

Planning gate bindings are not implementation-task assignments. Carry settled source constraints,
research links, applicable guidelines and observable verification needs into the next-stage handoff;
leave task-local REQUIRED items and inherited executor intent to task generation; executable
runtime bindings are approved separately, not selected by the brainstorming producer.

## Durable handoff and resume

Retain the gate result, agenda when present, applicable accepted outcome constraints and
source links, owner decisions/rationale, deferrals and concise handoff in session history
before depth selection. Do not write a source or state file to make a preselection resume
possible. After selection, persist them and the changed source using existing project
conventions. Handoff context includes settled decisions, applicable accepted outcome
constraints and source links, trade-offs, intentional deferrals, uncertainties, and the
next-stage readiness target. On resume in every mode, including preselection, re-establish
applicability through read-only discovery and consultation of current project decision
ownership, the whole index and relevant accepted records under save-adr, not solely supplied
constraints/session history or an earlier-read claim. Keep preselection read-only and absent
store alone nonblocking. Then validate the bounded source and decision record; if owner answers are missing,
re-present the saved agenda instead of regenerating decisions. If the source or decisions
changed materially, re-run the gate before downstream production.

## Mandatory task checkpoint

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md). Preselection remains read-only and creates no empty commit; any authorized retained decision artifact is a bounded task and never adopts inherited work.
