---
name: epics-manager
description: Use when preparing or resuming a selected feature brief through an installed SpecKit workflow before implementation.
---

# EPIC Manager

Guide an owner-selected brief through reviewed SpecKit artifacts. This manager prepares
work; it does not implement it. It requires the shared `epic-brainstorming` and
`task-generation` skills: verify they are discoverable before use and stop with a capability
report if either is unavailable rather than duplicating their behavior.

## Preflight and provenance

Read repository instructions, the selected bounded brief, its cited sources, governing
principles, existing artifacts, and applicable project memory when the project declares the
memory contract. Record the source path/section, settled decisions, acceptance criteria,
exclusions, dependencies, provenance, and existing artifact/review links. Re-read selected
bounds and links on resume. Ambiguous provenance is a blocker; obtain owner selection through
the available question capability rather than attaching a likely source.

Verify the project's observed SpecKit constitution (when required), specification,
clarification, planning, tasks, and analysis commands, instructions, templates, and
prerequisite checks. Report each as `AVAILABLE` or `UNAVAILABLE` with evidence and blocker.
If a required capability is unavailable, stop at the affected stage; never install, simulate,
or replace it with generic Markdown. Verify usable question/delegation capabilities and
owner-selected class bindings before assigning work; missing capabilities stop with an
explicit report. Do not hard-code a provider, model, agent, path, state schema, or command
name.

Use existing durable project artifacts for decisions, approvals, deferrals, revisions, and
handoff. A bare approval label is insufficient: identify the approved current content or
revision. Resume from the earliest missing, stale, or inconsistent artifact/checkpoint.

## Stage sequence

Run the first incomplete or invalid stage. Approval checks are checkpoints inside this
sequence, not new create/critique/fix stages:

```text
brainstorm_gate
  → [epic_brainstorm → epic_brainstorm_fix]
  → spec_create → plan_create → tasks_create → overall_review → done
```

### `brainstorm_gate` — `sonnet-class`

**Entry/input:** verified selected brief and preflight evidence. **Steps:** invoke the shared
`epic-brainstorming` gate on the selected brief section; preserve its exact
`NO_BRAINSTORM_NEEDED`/`BRAINSTORM_NEEDED` result and evidence. **Output:** a saved next stage:
skip goes to `spec_create`; needed goes to `epic_brainstorm`. **Approval/resume:** no new owner
approval on a skip; on resume validate source/decision evidence and re-run the gate if material
content changed.

### `epic_brainstorm` — orchestrator-owned

**Entry/input:** saved shared-skill agenda. **Steps:** use the available question capability
for one material agenda item at a time, as required by `epic-brainstorming`; do not delegate
owner dialogue. Capture decisions and deferrals. **Output:** durable formatted decisions for
`epic_brainstorm_fix`. **Approval/resume:** each material owner decision is the approval; if
answers are incomplete, re-present the saved agenda rather than guessing.

### `epic_brainstorm_fix` — `sonnet-class`

**Entry/input:** selected bounded brief, saved agenda, and owner decisions. **Steps:** invoke
shared decision application to apply exactly those decisions inside the selected source;
preserve structure, exclusions, and deferrals. **Output:** updated brief plus concise handoff
context for `spec_create`. **Approval/resume:** validate the decision record and bounded edit;
missing evidence stops rather than reinterpreting the owner.

### `spec_create` — `sonnet-class`

**Entry/input:** source/constraints, shared-gate result, and detected specification capability.
**Steps:** follow the observed SpecKit specification instructions; apply the spec-driven
reference where installed; reflect settled decisions without re-deriving them. Run optional
clarification only when requested or required by the detected workflow, resolving mechanical
gaps directly and sending material choices to the owner. **Output:** verified specification and
its path. **Approval/resume:** obtain and durably record explicit approval of the current
specification before `plan_create`; missing/stale approval returns here.

### `plan_create` — `opus-class`

**Entry/input:** current approved specification, source, and detected planning capability.
**Steps:** in one same-session pass, review the specification, correct non-material defects,
and create the plan with the observed SpecKit planning instructions. Cover interfaces,
sequencing, risks, verification, integration, documentation scope, and coherent consecutive
same-class work where retained context is useful. Preserve prerequisite order and story
acceptance boundaries; do not reorder dependencies or pad distant work to fill a future batch.
Material scope, architecture, privacy, permission, irreversible, cost, or settled-requirement choices are owner
gates; do not use speculative defaults. If review or planning changes approved specification
content, renew specification approval before leaving this stage. **Output:** verified plan and
handoff context. **Approval/resume:** retain flagged owner decisions and resume the same
correction context when supported; otherwise use durable handoff evidence. Do not split this
into separate spec critique/fix stages.

### `tasks_create` — `sonnet-class`

**Entry/input:** current approved source/specification/plan and detected tasks capability.
**Steps:** follow the observed SpecKit task command under the shared `task-generation` contract.
This stage is create-only: create the best task list, including documentation and acceptance
coverage. Prepare coherent consecutive same-class work with producer checks and shared-context
notes, but keep task order, dependencies, and story acceptance boundaries intact. Do not
self-review or self-correct it. **Output:** verified task list and handoff
context. **Approval/resume:** task defects belong to `overall_review`; resume validates inputs
and output rather than trusting a stage label.

### `overall_review` — observed independent reviewer

**Entry/input:** source, current specification, plan, tasks, approvals, and detected analysis
capability. **Steps:** use an observed permitted independent reviewer selected by the owner;
follow the detected analysis capability and inspect traceability, exclusions, principles,
coverage, dependencies, documentation, integration, class share, and approvals. Apply
mechanical task-level fixes and report them. Flag only material friction/complexity or genuine
spec deviation with concrete alternatives and a recommended applied default; never flag task
ordering, grouping, file choice, batch sizing, naming, or internally verifiable fixes. Resolve
single-option mechanical items directly. **Output:** review evidence, decisions, deferrals,
corrections, and concise handoff. **Approval/resume:** obtain explicit overall-review approval
for current artifacts. If review changes the specification or plan materially, renew affected
approval before handoff. Missing reviewer, review evidence, or current approval stops.

### `done`

**Entry/input:** current reviewed artifacts and both current approvals. **Steps:** revalidate
source links, SpecKit prerequisites where applicable, artifact existence, task ordering, and
approval/content evidence. **Output:** a fresh-session handoff naming source, specification,
plan, tasks, both approvals, review evidence, decisions, and deferrals for
`coordinate-implementation`. **Approval/resume:** if any artifact or approval drifted, return
to the earliest affected stage; readiness is not implementation or feature acceptance.

## Decision and handoff discipline

Use the question capability only for material product or technical choices. Describe owner
questions in outcome, scope, trade-off, risk, and evidence terms; offer concrete alternatives
and a recommendation. If the question capability is unavailable, stop at a material gate rather
than infer an answer. Record decisions, rationale, deferrals, correction outcomes, and concise
handoff context in established project conventions. Preserve current safety protections and
source/task authorization without resurrecting obsolete platform tools, paths, rigid state
files, named bindings, or historical speculative defaults.
