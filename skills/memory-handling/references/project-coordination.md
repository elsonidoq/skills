# Project coordination memory

Optional project-local coordination knowledge, shared by memory-handling, planner,
TinySpec, task-generation and coordinator. This is an instruction contract, not a
persistence engine or a replacement workflow. Actual project knowledge never belongs
in global skills. Keep required adopted gotcha-memory discovery/retrieval/write gates
unchanged; coordination evidence is not a gotcha ledger.

## Association and optional discovery

Discover association only from project instructions or documented project configuration
naming a coordination root; respect declared equivalent layouts and explicit approved
paths. No global-store fallback or guessed association. Undeclared optional coordination
memory means existing behavior, no invented knowledge, no writes and no new adoption
blocker. Report a declared missing/unreadable root or guidelines accurately; do not
fabricate guidance or bypass an existing required-memory policy. Discovery is read-only.

For requested setup, propose `<approved-project-memory-root>/coordination/` only if a
project-memory root already exists; otherwise obtain a project-local root through the
existing question/approval interaction. This is a proposal convention, never a discovery
assumption. Association and skeleton creation require bounded owner approval of exact
paths/writes and preserve existing content. No-memory reads never initialize a store.

## Compact guidelines

Read associated `GUIDELINES.md` during initial understanding, before brainstorming,
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

For new approved layouts:

```text
<approved-coordination-root>/
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
update summary/index metadata without erasing observations or prior runs. Bound writes to
the associated store and verified write authority. Without association/write authority,
report observations in the existing execution handoff and offer future bounded setup,
never silently initialize a store. Evidence-write authority is not guideline authority.

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
from optional memory approval that is pending or rejected.
