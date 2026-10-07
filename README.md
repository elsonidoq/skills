# Coherence — Pi Skill Suite

Global pi skills for deliberate feature delivery across unrelated repositories. The suite
binds to pinned pi packages and requires adoption per project; it is not runtime-portable.

## Setup

See [REQUIREMENTS.md](REQUIREMENTS.md). The installer verifies pi, installs missing pinned
packages, links suite skills and the SDD reference, and runs deterministic validation:

```bash
scripts/install.sh
scripts/install.sh --probe  # additionally invokes one model; authorize separately
```

Foreign entries at installation destinations are preserved and reported, not overwritten.
Retired links are backed up only when their target proves they belong to this checkout.
After installation or global skill changes, run `/reload` inside pi.

On a project, use [Initialize Coherence](skills/initialize-coherence/SKILL.md)
(`initialize-coherence`) for proposal-first suite instructions, project memory association,
and documentation owners/indexes/routing, including a schema owner when a persistent
database exists. Compatible adoption is validated without rewriting it; an approved
bounded refresh preserves custom paths/policy, existing memory and planning artifacts.

Initially clean projects may initialize required documentation with verified content.
Tracked-dirty or untracked-only projects require a fresh read-only investigation and approval
of the current plan plus exact missing-shell/index bounds; documentation writes remain
empty/template shells, maps and indexes only. Structural readiness requires all approved
instructions/memory and required documentation structure; missing requirements, denied
approval or missing structure prevent a ready claim. Empty/stale substantive documentation
remains explicit outstanding work for planner's owner-selected TinySpec/Standard path.
Initialization reports missing capabilities rather than installing prerequisites.

This repository tracks its project-local SpecKit 1.0.12 setup: `.specify/` contains shared
scripts, templates, integration metadata and the [project constitution](.specify/memory/constitution.md);
`.pi/prompts/` exposes the project SpecKit commands in pi. Machine-local feature pointers,
extension overrides and `.pi/subagents/` runtime state remain ignored. Other projects
still need their own SpecKit installation for Standard; TinySpec does not require it.

## Planning and Implementation

Start with one entry point:

```text
Use planner for this requirement:
<structured requirement or selected source path/section>
```

Planner inspects the requirement/codebase, brainstorms unresolved material choices, and
presents an approximate scope assessment. This phase is read-only except mandatory
project-local coordination-store initialization/commit and factual evidence/index/reflection
persistence, including runs blocked before depth selection. It always presents both
paths and stops for your explicit choice; the recommendation does not choose for you.

```text
                         ┌→ TinySpec → Tasks → Review → Combined approval ───┐
Request → Planner → Choose│                                                   ├→ coordinate-implementation
                         └→ SpecKit Specify → Spec approval → Plan → Tasks ──┤
                                                 → Analyze → Final approval ─┘
```

- **TinySpec:** compact context, scope, decisions, approach, acceptance and validation;
  mandatory separate tasks. Planner reviews both before one combined approval. No SpecKit
  or unnecessary spec/plan/research hierarchy is required.
- **Standard:** genuine installed SpecKit stages, separate what/how/task reasoning,
  specification approval before planning, independent overall review and final approval.
- **Both:** shared `task-generation` contract and durable current-content approval evidence.
  Before every artifact approval or renewal, planner presents a brief bullet-list executive
  summary in the conversation, then calls `ask_user`. You may approve, request changes or
  withhold approval. The brief states the next phase that approval will start.

After approval, planner immediately starts the next authorized phase without another
continuation prompt. Final approval automatically starts `coordinate-implementation` and
its preflight unless you explicitly requested planning-only or a separate-session handoff.
Capability failures, material owner gates and denied/ambiguous approvals still stop progress.

Choosing depth authorizes planning, not implementation. Existing legacy artifacts retain
original provenance, source shapes and applicable gates; planner owns their repair checkpoints.
No new Epic is required or produced.

After an approved handoff, in this or a fresh session:

```text
Use coordinate-implementation for the approved work.
Producer: planner
Planning depth: [TinySpec or Standard]
Source: [path/section]
Tasks: [path]
Supporting artifacts: [paths; Standard includes specification and plan]
Review and decisions/deferrals: [paths/sections]
Approval evidence: [combined approval, or specification and overall approvals]
Approved current content/revisions and implementation scope: [evidence]
```

Coordinator revalidates the handoff and preserves one shared execution graph: up to three
bounded tasks may run locally only when owner-selected exact profile/context fit; larger
complete lists use asynchronous sequential delegation. Tasks carry stable REQUIRED item contracts,
not implementation-model classes or shares. Normally 2–5 consecutive related tasks share one
exact binding plus independently justified effort per invocation when feasible; this is not a quota.
The [qualified seed rubric](skills/coordinate-implementation/references/batch-routing.md) and relevant
approved project guidelines inform owner selection; empty guidelines invent no success history.
Before implementation, coordinator presents the complete batch table with one/two-sentence batch
descriptions, exact proposed model/effort and separate family/effort rationales, then obtains
explicit approval of batch boundaries and profiles. Implementation approval alone does not approve
routing. Reuse verified unchanged routing approval on resume; approve changed rows before execution.
No universal Sol/medium default or forced model diversity applies.
Verify permitted callable binding, supported effort, tools and owner gates at assignment/dispatch,
and ensure settings do not silently override actual dispatch arguments. Actual profile stays
unknown when unobservable, never inferred from selection.
The [coordinator dispatch seam](skills/coordinate-implementation/SKILL.md#select-execution-capability)
ends preparation once mandatory conditions and committed intent are satisfied, reopening only
for concrete affected invalidation. One worker implementing one batch normally uses direct
asynchronous delegation, including multiple internal sequential tasks; a workflow needs a
concrete orchestration reason in the existing brief/tracker, not merely a batch label.

Verification per task; execution per coherent batch. Practical producer contracts retain
criterion/check/evidence/gates and optional distinction through both adapters. In the sole
six-factor rubric compare closed design/implementation difficulty with weakest oracle quality,
check cost and observability; combined verification must be feasible and failures attributable.
Preserve consecutive order and producer verification before consumer work.
Dispatch supplies the whole unchanged REQUIRED union before coding; shared checks run once
with every distinct task/item mapping. Cheap audit checks coverage, relevance to each original
criterion, current revision/environment, consistency, every actual task diff/checkpoint and
owned scope/gates, not general full rereview. Executor pass/fail/not_verified maps through proof
to satisfied/failed/insufficient-evidence: failed needs demonstrated criterion violation;
missing/irrelevant/stale/conflicting/unrun proof is insufficient unless valid observations
independently prove a defect. Retain defect and evidence limitation together. Only satisfied
REQUIRED items and gates release dependents; optional green cannot compensate. Source-required
representative-sample manual STOP needs inspectable sample and explicit user approval before
downstream/full expensive operation, permitting only scoped continuation; LLM self-review
cannot replace it. Ordinary tasks need no invented manual ceremony. Inadequate approved/legacy
contracts return to producing review/renewal, never weaker post-hoc acceptance.
A passing contract needs no mandatory strong per-batch reviewer. Inspect failure/run/invocation/
partial commits and proof before authorized stronger implementation continuation for exact gaps
under the same original contracts, not generic strong review. Carry current SHA/state, prior
proof, dependencies and invalidations, retain valid work/attempts, rerun invalidated checks and
reuse only confirmed-valid evidence without a fixed ladder. Unknown/non-model/manual/permission/
contract gaps do not automatically escalate. Clean retry is exceptional: documented justification,
ownership/safe repository mechanics and required owner/project gates, never automatic reset/discard.
Each task has its own implementation commit followed by a separate factual evidence checkpoint;
one fresh independent final review covers the complete committed range. Planning depth and
unrelated planning/reviewer selections remain separate from implementation selection.
Static/symbolic fixtures demonstrate contracts, not live model performance or obedience;
live support/callability checks require separate permission and usable runtime capabilities.

## Brief current state

During approved execution, coordinator maintains implementation-relevant current truth in
project-owned root `STATE.md` (or an explicitly declared project-local equivalent).
This is a **brief snapshot**, not a coordinator-owned tracker: short current-work/run,
authorization/checkpoint/evidence pointers, active workers, blocker and exact next action.
Replace current truth; no transcripts, logs, completed-task ledger or accumulated history.
Preserve custom/unrelated content and coordinate write boundaries with other workflows.
Coordinator writes only at approved start/imminent dispatch, child-ID capture, audited batch or
local task checkpoint, genuine blockers, final review/closeout, or materially changed recovery truth.
Capture child IDs immediately and commit safely later; coalesce same-boundary changes and skip
unchanged status. Polling and healthy internal worker progress do not trigger coordinator writes.
Worker per-task commits/evidence remain unchanged; reflection occurs at closeout or a genuine pause.
`finish-session` reconciles the same snapshot, retaining only a concise terminal disposition
and next action when complete. Task artifacts, approvals, Git and coordination evidence stay
authoritative; state confers no authorization or acceptance.

After compaction/restart/uncertainty, read state and revalidate approval, Git/ownership,
verification evidence and recorded children before continuing. Stale/missing state requires
reconciliation or a precise stop, never fabricated progress or duplicate dispatch. See the
[coordinator lifecycle and recovery contract](skills/coordinate-implementation/SKILL.md#brief-current-state-and-recovery)
for bounded evidence commits, safe active-worker persistence and failure handling. No runtime
compaction hook or live robustness claim is implied.

## Project coordination memory

Every run uses project-local coordination files through the
[shared contract](skills/memory-handling/references/project-coordination.md). Before planning
or direct task/execution work, skills automatically create missing `GUIDELINES.md` and
`evidence/INDEX.md`, tell the user and commit only the initialization files, then proceed.
No setup approval or opt-out/handoff-only path. Use a declared project-local coordination
root if present; otherwise the default is `<project-root>/memory/coordination/`. Existing
files and unrelated staged work are preserved; repeat entry needs no initialization commit.
Initialization/write/commit failures stop with a precise blocker, not nonpersistent execution.
Empty guidelines invent no lessons. Required adopted gotcha-memory rules remain separate.
This repository's coordination store is `memory/coordination/`.

Compact `GUIDELINES.md` is read during initial understanding, **before Planner → Choose**,
and exact applicable constraints/evidence references reach TinySpec or Standard, tasks and
coordinator briefs. Ordinary planning does not read execution history. Only justified
clarification/synthesis (tentative/conflicting guidance, user justification or contrary
observations) reads the compact evidence index, then selected relevant records.

One compact `evidence/<run-id>/SUMMARY.md` per new run holds the current disposition, short
task/checkpoint references, exceptions and reflection or proposed guidance; no separate task
or reflection files are created. Older multi-file runs remain readable. Factual attempts,
checks, failures/partial work, unknowns and manual validation stay outside approved guidelines
and the gotcha `MEMORY.md` index. The run record precedes refresh of its one compact index row;
resume retains attempts and reconciles interrupted updates. Every run persists observations
locally; execution handoffs link evidence rather than replace it.

After verification and independent review (or a blocked pause), conservative reflection
proposes scoped guidance or evidence-only/no update. An executive brief and exact candidate
diff precede `ask_user`: **accept, edit, reject, or add**. Implementation approval grants no
guideline authority. Only explicitly approved resulting content may be applied after an
immediate baseline re-read; drift requires renewed approval. Reject preserves guideline
bytes; pending/unavailable/cancelled/ambiguous decisions change no learned guidelines.
Guideline approval is reported separately from implementation acceptance; automatic empty
initialization is not permission to add or rewrite learned guidance.

Indexed attempts record exact selected/observed profile or unknown, assessment factors, contract
strength, first/final outcome, diagnosis and repair/checkpoint references, preserving partial,
escalated and blocked work. The same SUMMARY/index retains batch/task item dispositions and
proof references, reused/invalidated checks, exact escalation reason and next selected profile
or pending selection; first/final selected versus observed attempts preserve original unknowns.
Non-model causes (including unavailable tools/environments) do not
count as capability failure; weak/invalidated success is not strong guidance. Residual-reasoning
notes inform batch assessment, not task assignments. No automatic model replacement or permanent
rule from one outcome; only relevant approved guidelines may override the seed within owner/source gates.
For example, a **fictional project** might scope a manual output checkpoint to heuristic
implementation. That example is neither real evidence nor a global heuristic policy.
After changing these global skills, run `/reload` inside pi.

## Supporting Skills

- `planning-brainstorming`: shared bounded uncertainty gate and owner dialogue.
- `tiny-spec`: lightweight source producer; not an independent manager or executor.
- `task-generation`: task semantics, ordering, validation and adapter contract.
- `delegating-architectural-planning`: observed SpecKit planning adapter.
- `initialize-coherence`: single adoption/memory/documentation entry point;
  substantive documentation work goes through planner, without a forced depth exception.
- `requesting-code-review` / `receiving-code-review`: independent assessment and disposition.
- `memory-handling`, `track-open-issue`, `finish-session`: durable guidance and closeout.

## Validation and Documentation

Run `scripts/check-skills-lint.sh` for deterministic suite checks. See the
[planner regression guide](docs/plans/planner-regression.md) for trace fixtures, mutations,
read-only RPC smoke testing, full behavioral scenarios and evidence limitations. Static tests
are not proof of model obedience; live tests require separate authorization.

Use [docs/index.md](docs/index.md) to find the canonical documentation owner. Documentation
describes current behavior, gotcha memory contains only verified non-obvious warnings,
project-local coordination memory separates reusable guidelines from factual run/task evidence, and
`docs/open_issues.md` is the canonical unresolved-work register. Global assets must not assume
project paths, branch, deployment state, named models or an invented artifact/state schema.

## Mandatory task checkpoints

For authorized retained repository output, the shared [task-commit contract](skills/memory-handling/references/task-commit-contract.md)
requires a focused, verified per-task commit before later task work, completion reporting, or handoff. A task is an
independently verifiable work unit, not a tool call or batch. Read-only, no-change, scratch, and external-only work
creates no empty commit. Preserve unrelated staged/unstaged work; ambiguous ownership, unavailable Git, failed hooks,
or incompatible policy stops rather than waives the checkpoint. Coordinators independently inspect task diffs/checks
and may recover only understood verified contextual changes; fresh implementers never commit unknown work. Subagents
verify and commit each internal task and continue without routine coordinator pauses; the coordinator audits all task
checkpoints when the batch returns, before acceptance or external dependents. Failed checkpoints and genuine owner
gates still stop execution. Evidence updates remain separate evidence-only checkpoints. This is instruction-managed with static/Git-fixture evidence, not
runtime proof that a model obeys it. After these global skill changes, run `/reload` in pi.
