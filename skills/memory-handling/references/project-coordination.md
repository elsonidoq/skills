# Project coordination memory

Required project-local coordination knowledge, shared by memory-handling, planner,
TinySpec, task-generation and coordinator. This is an instruction contract, not a
persistence engine or a replacement workflow. Actual project knowledge never belongs
in global skills. Keep required adopted gotcha-memory discovery/retrieval/write gates
unchanged; coordination evidence is not a gotcha ledger.

## Project-local initialization

Use one mandatory lifecycle in every entry point: ensure the project-local store exists,
read compact guidelines, persist execution evidence, reflect, and apply only approved
guideline changes. There is no opt-out or handoff-only persistence path.

Resolve the current project root from the selected repository/workspace, never the global
skill installation. Reuse a coordination root/layout explicitly declared in project
instructions or configuration; otherwise use `<project-root>/memory/coordination/`.
The default requires no adoption or association ceremony. Keep every destination inside
the current project; refuse an outside-project path, unreadable file or path collision
rather than selecting a second store or overwriting existing content.

Before planning assessment/depth choice or direct task/execution work, automatically
create only missing directories, `GUIDELINES.md` and `evidence/INDEX.md`. Initialize
empty guidelines with “No approved project coordination guidelines yet” and an empty
index with Run, Date, Areas/tags, Relevant patterns and Outcome columns. Do not invent
lessons, historical runs or seed a generic policy. Preserve every existing file byte-for-byte;
partial stores get only their missing files. Repeated entry is idempotent: no new files
or initialization commit when nothing is missing.

Tell the user which files were initialized, then commit only those new files as a focused
initialization commit before proceeding. Preserve unrelated working-tree and staged
changes; use explicit paths and a path-limited commit, never `git add .` or a commit of
all staged files. No separate setup approval is required. If creation or commit is blocked
by permissions, repository policy or unavailable Git, report the exact blocker and stop;
do not continue with nonpersistent memory or silently skip the commit. On resume, inspect
any partially completed initialization and finish its missing commit without duplicating
files/commits. The preselection read-only rule permits only bounded coordination-store
initialization/commit and factual evidence/index/reflection persistence, including runs
blocked before depth selection (for example, unavailable question capability). Record
observed blockers and evidence-only reflection in the project-local store; do not infer
an owner decision. This exception grants no source, planning-artifact/decision-file or
unapproved learned-guideline write authority.

## Compact guidelines

Read project-local `GUIDELINES.md` during initial understanding, before brainstorming,
scope assessment and depth choice. Report applicable guidance and carry exact constraints
and evidence references into either selected source route, task decomposition/dependencies,
checkpoints, verification and coordinator briefs. Direct/standalone consumers discover
through this same boundary; they must not assume planner invocation. Guidance informs
owner choice and source observables, never overrides owner authority or source requirements.

Each compact guideline contains a scope/trigger, short actionable statement, qualitative
status (`tentative`, `repeated`, `stable` or `owner-supplied`) and evidence pointers where
available. Cover only reusable planning, decomposition, delegation, verification, manual
checkpoints, subsystem risk and implementation traps. Preserve uncertainty and contrary
evidence. Owner-supplied entries name their origin, never fabricate supporting runs.
Merge/refine/supersede instead of accumulating transcripts or duplicating observations.
`GUIDELINES.md` is not the gotcha `MEMORY.md` index; run evidence and reflection are not planner guidance.

## Selective historical retrieval

Ordinary planning reads guidelines, not `evidence/INDEX.md` or history. Historical
clarification is justified only by matching ambiguous/tentative/conflicting guidance,
pattern synthesis, a user request for justification, or new contradictory observations.
State the trigger, read the compact evidence index first, select relevant run summaries
(or task records in older runs) by tags and pointers, then open only those selected records. Do not recursively
load the directory or promote raw outcomes directly into instructions. Unrelated records
stay unread; no relevant evidence means proceed retaining uncertainty, not invented facts.

## Separate factual evidence

For new runs use one compact evidence file per run (existing declared project-local equivalents
use the same lifecycle):

```text
<project-root>/memory/coordination/
  GUIDELINES.md
  evidence/
    INDEX.md
    <run-id>/
      SUMMARY.md
```

`SUMMARY.md` owns the current disposition, a short attributable checkpoint/attempt ledger,
exceptions and reflection/any guideline candidate or decision. Do not create separate task,
review or reflection files for new runs, and do not reproduce task contracts, full check logs,
Git inventories or a second narrative of every task. Keep task ID, baseline/result/evidence
SHA, exact selected/observed profile when applicable, item result/evidence pointer, attribution
and manual/reviewer exceptions sufficiently traceable for later synthesis; use a terse row when
checks pass normally and expand only a surprising failure or contested conclusion. Shared
run-wide limitations are stated once. A summary is a selective learning source, not a task
transcript. Per-task implementation commits and distinct evidence-only Git checkpoints remain
required; each checkpoint updates this same file and the compact index row.

Reuse an existing safe project execution/run ID; otherwise derive a unique filesystem-safe
date/subject ID and retain it in the execution tracker. Reuse that ID on resume; never
overwrite another run. Older runs with separate task or `REFLECTION.md` files remain valid and
selectively readable; do not migrate them by default. Evidence is factual and append-oriented:
keep attempts and corrections distinguishable, update current disposition and index metadata
without erasing observations or prior runs. Persist every run's evidence in the initialized
project-local store; an execution handoff may link it, never replace it. If an evidence write
fails, report the blocker and stop affected work, not a successful persistence checkpoint.
Evidence-write authority is not guideline authority. The project-owned brief current-state
snapshot (`STATE.md` by default) is separate from this append-oriented factual evidence:
[coordinator snapshot/recovery](../../coordinate-implementation/SKILL.md#brief-current-state-and-recovery)
owns its execution update lifecycle. State links run/checkpoint evidence without copying it;
it is neither another coordination store nor an authorization record. Exclude state writes
from delegated worker evidence scope; coordinate explicit write boundaries with other workflows.
State updates join only the exclusive coordinator write boundaries under that lifecycle;
coalesce same-boundary changes and skip unchanged status. Returned child IDs still get immediate
snapshot capture with safe deferred commit; polling and healthy internal worker progress do not
trigger coordinator summary/index writes. The coordinator references worker evidence at the audited
batch boundary instead of duplicating its task ledger. Internal worker task/evidence checkpoints
remain uninterrupted and independently audited on return.

At task/attempt checkpoints, record task ID/type, areas/tags, residual reasoning when
assessed, selected capability role, exact selected and observed profile (binding plus
reasoning effort, or unknown observation), assessment factors, applicable approved guidance
or none, contract strength, first/final outcome, diagnosis, repair/escalation and bounded
item check/checkpoint references. Retain accepted, partial, escalated and blocked attempts,
individual attempt/check results, reviewer findings, surprises and manual/user validation;
unknown observation is never overwritten by the requested/selected profile.
Include failed, blocked and partial work; unknown outcomes are explicitly unknown,
not inferred successes. Link bounded check/review evidence; do not copy raw logs,
credentials, tokens, personal data, secrets or sensitive payloads.

Create/update the run record before its index entry. Every new evidence write refreshes
that run's compact row: linked summary, date, areas/tags, relevant patterns and concise
outcome. Keep one row per run, no duplicate rows, transcripts or full logs. Reconcile an
interrupted record/index update on resume before reporting successful persistence;
failed writes remain reported failures, not acceptance passes.

## Qualified batch routing feedback

Optional `residual_reasoning: low|medium|high` plus a brief rationale fits existing task
notes/briefs; it informs the coordinator's [qualified seed](../../coordinate-implementation/references/batch-routing.md),
not an implementation-task class or model assignment. Family and effort have independent
rationales; one exact permitted owner-selected profile serves each sequential invocation.
Relevant approved guidance may override the seed when its scope and evidence apply, never
owner/source authority, permissions, supported-effort/callability or REQUIRED acceptance gates.
Empty guidelines invent no project success history. This evidence owner is not a second router,
store, schema, score or automatic learner.

Retain each attempt's exact selected and observed profile separately, original assessment,
contract strength, first/final outcome and repair/checkpoint references without erasing failures.
Use diagnosis values `model_capability`, `planning_or_spec_gap`, `verification_contract_gap`,
`batching_error`, `environment_or_tooling`, `external_dependency` or `unknown` with concrete
supporting evidence. Non-model causes never count as capability failure; unavailable environments
keep REQUIRED checks not verified and acceptance blocked without penalizing the selected profile.
Complete meaningful first-attempt evidence may support qualified positive feedback, but weak or
invalidated successes are not strong positive guidance. Repair success alone does not prove
model-only attribution. Unknown actual model/effort stays unknown; later supported observations
are appended with provenance, not retroactively inferred from selection.

Inspect failed child run, invocation, partial commits and item evidence before targeted repair.
Preserve valid work/prior attempts, identify affected dependencies and invalidated items, and
reuse only confirmed-valid evidence. Repair may change model, effort or both only through usable
permitted binding/support and owner gates; unknown cause or unavailable/unauthorized repair stops,
not blind restart or a fixed ladder. Carry original assessment/profile, passed/failed mappings,
current state and full contract, rerunning all invalidated checks through coordinator acceptance.
Guideline synthesis still uses selective/index-first retrieval, exact owner approval and immediate
baseline drift checks below; raw attempt outcomes never automatically become guidance.

## Conservative reflection

After implementation/verification and independent review, or when pausing with a blocker,
ask whether the observation is:

1. Useful to future planning?
2. Project-specific versus general?
3. Reusable versus incidental?
4. Reinforcing existing guidance?
5. Contradicting existing guidance?
6. Supported enough for guidance or evidence-only?
7. Informative about delegation?
8. A manual-validation discovery automated checks missed?
9. A surprising outcome requiring qualification or more evidence?

Append attributable observations and concise candidates (or `no update proposed`) in the
run's `SUMMARY.md`, then refresh the index separately. Older runs may retain separate task
and `REFLECTION.md` files. Distinguish direct observation, tentative
pattern, repeated pattern, stable guideline, insufficient evidence and conflicting
evidence without numerical confidence scores. Review selected prior evidence only when
needed for synthesis using selective retrieval. One failure may support a narrowly scoped
tentative caution, never a universal class/subsystem ban or permanent one-outcome rule.

Propose add/refine/supersede/remove changes with scope, qualitative status, supporting
and contradicting pointers, plus evidence-only items. General lessons stay out unless
explicitly project-scoped; global skill improvement is separately approved work. If no
reusable lesson exists, record `no update proposed`. Synthesis is never automatic mutation.

## Exact guideline approval

Present an executive brief and exact candidate diff before the existing `ask_user` gate;
allow accept, edit, reject, or add a guideline. Implementation approval grants no guideline
mutation authority. Persist the answer, approved bounds, comparable baseline/proposed
content evidence and decision disposition in the run's `SUMMARY.md` (or an existing older
`REFLECTION.md`) and refresh the index.
Accepted, edited or added resulting content must be explicitly approved; do not infer
an edited/additional statement or widen approval beyond that content.

Pending, unavailable, cancelled or ambiguous interaction leaves guidelines unchanged
and proposals pending. Rejection leaves guidelines byte-identical while retaining evidence
and rejection disposition. Immediately before applying only approved changes, re-read
`GUIDELINES.md` and compare with the approved baseline; concurrent/baseline drift stops
application and requires renewed review/approval, never unapproved overwrite. Re-check
relevant guidance after approved writes. Report implementation/feature acceptance separately
from guideline approval that is pending or rejected.
