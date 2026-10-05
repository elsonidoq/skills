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
files/commits. This bounded initialization is the sole exception to planner's preselection
read-only rule; it grants no source, planning-artifact or learned-guideline write authority.

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
`GUIDELINES.md` is not the gotcha `MEMORY.md` index; `REFLECTION.md` is not planner guidance.

## Selective historical retrieval

Ordinary planning reads guidelines, not `evidence/INDEX.md` or history. Historical
clarification is justified only by matching ambiguous/tentative/conflicting guidance,
pattern synthesis, a user request for justification, or new contradictory observations.
State the trigger, read the compact evidence index first, select relevant summaries/task
records by tags and pointers, then open only those selected records. Do not recursively
load the directory or promote raw outcomes directly into instructions. Unrelated records
stay unread; no relevant evidence means proceed retaining uncertainty, not invented facts.

## Separate factual evidence

Default layout (existing declared project-local equivalents use the same lifecycle):

```text
<project-root>/memory/coordination/
  GUIDELINES.md
  evidence/
    INDEX.md
    <run-id>/
      SUMMARY.md
      T001.md
      T002.md
      REFLECTION.md
```

Reuse an existing safe project execution/run ID; otherwise derive a unique filesystem-safe
date/subject ID and retain it in the execution tracker. Reuse that ID on resume; never
overwrite another run. Separate summary/task files prevent a monolithic execution history.
Evidence is factual and append-oriented: keep attempts and corrections distinguishable,
update summary/index metadata without erasing observations or prior runs. Persist every
run's evidence in the initialized project-local store; an execution handoff may link it,
never replace it. If an evidence write fails, report the blocker and stop affected work,
not a successful persistence checkpoint. Evidence-write authority is not guideline authority.

At task/attempt checkpoints, record task ID/type, areas/tags, residual reasoning when
assessed, approved class, selected capability role, model and reasoning effort when
observed (otherwise `unknown`), individual attempt/check results, reviewer findings,
failure cause, retries/escalation and outcomes, surprises, manual/user validation.
Include failed, blocked and partial work; unknown outcomes are explicitly unknown,
not inferred successes. Link bounded check/review evidence; do not copy raw logs,
credentials, tokens, personal data, secrets or sensitive payloads.

Create/update the run record before its index entry. Every new evidence write refreshes
that run's compact row: linked summary, date, areas/tags, relevant patterns and concise
outcome. Keep one row per run, no duplicate rows, transcripts or full logs. Reconcile an
interrupted record/index update on resume before reporting successful persistence;
failed writes remain reported failures, not acceptance passes.

## Class-compatible routing experiment

Optional `residual_reasoning: low|medium|high` plus a brief rationale fits task notes/briefs;
absence preserves existing routing. Low favors a cheaper usable owner-selected option
compatible with the approved class. Medium requires a strong executable acceptance oracle
plus stronger verification/review; high favors stronger compatible reasoning. These are
real-work experiment proposals, not synthetic benchmarks, model optimization or a new
class taxonomy. Existing sonnet-class/opus-class semantics and class-share gates remain
authoritative: high alone never forces opus or bypasses the share gate. Never silently
replace selected models, relabel/weaken classes or waive REQUIRED acceptance.

Inspect the failed child run and invocation before retry/escalation. Preserve valid evidence
and unrelated work; isolate/restore only the failed task's clean state where the existing
workspace architecture and authority permit. Escalate through verified stronger capability
and owner-selection gates; unknown cause, unavailable permitted option or unestablished
clean state stops with a precise blocker. Record both attempts and outcomes, approved class,
capability role, actual observed model/effort or unknown. Guidelines refer to class/capability
and task/oracle conditions, not provider names or permanent rules from a single outcome.

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

Append attributable observations to run/task evidence and refresh the index separately
from concise candidates in `REFLECTION.md`. Distinguish direct observation, tentative
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
content evidence and decision disposition in `REFLECTION.md` (and refresh the index).
Accepted, edited or added resulting content must be explicitly approved; do not infer
an edited/additional statement or widen approval beyond that content.

Pending, unavailable, cancelled or ambiguous interaction leaves guidelines unchanged
and proposals pending. Rejection leaves guidelines byte-identical while retaining evidence
and rejection disposition. Immediately before applying only approved changes, re-read
`GUIDELINES.md` and compare with the approved baseline; concurrent/baseline drift stops
application and requires renewed review/approval, never unapproved overwrite. Re-check
relevant guidance after approved writes. Report implementation/feature acceptance separately
from guideline approval that is pending or rejected.
