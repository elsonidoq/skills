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
assessed, approved family/binding/effort, selected capability role, model and reasoning effort when
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

## Family and effort routing

Luna, Terra, Sol and Astra are family names, not provider IDs, fixed stages or a
universal rank. Record separate family suitability and effort rationale for every
stage/task/reviewer. Verify provider-documented options, permitted usable exact runtime
binding/effort, required tools/context and current owner selection before execution.
Catalog-only availability does not prove callability; unsupported runtime effort blocks.
Verify nonadjustable behavior explicitly; omitted effort remains unknown. Never silently
replace selected models. Drift or unavailability requires renewed affected owner decision.

Decompose first. Profile complexity, risk/security/data/dependency impact, residual ambiguity,
oracle quality, context/tool needs, latency/cost constraints and relevant local outcomes.
Risk strengthens decomposition, executable checks and applicable approval/review/recovery
safeguards, not automatic high effort or strongest-family selection. Choose the least
supported effort justified as adequate after decomposition. Higher effort needs concrete
remaining reasoning or comparable lower-setting counterevidence, not role, family, stakes
or spare budget alone. High-risk/strong-oracle work and fresh independent reviewer roles
do not force high effort. Weak-oracle work returns for decomposition and stronger observable
acceptance, not reflexive max. No unconditional low/medium default, universal rank,
fabricated savings or mandatory per-configuration probe. Unknown costs remain unknown.

Benchmark coverage is advisory: a supported no-row pairing is not automatically excluded.
Before consequential selection, inspect adequate evidence, complete targeted research or
record an explicit bounded owner uncertainty decision with gap, rationale, allowed scope
and remaining validation. Neither that decision nor a score waives provider documentation,
runtime support, owner routing authorization or REQUIRED acceptance. Missing research tools
or durable-write authority is a reported gap, never invented evidence.

Keep benchmark observations, derived provisional guidance, owner preferences and project
outcomes distinct. A conservative owner preference is a choice, not a measured score.
Retain source identity/location and supporting row/span, inspection date, reported version
and effort, metric/unit/direction, dataset/split/harness/setup, reported result, verification
status, limitations and task applicability. Unknown snapshot, mode, evaluation date and run
manifest remain unknown. Missing results, other versions/efforts/workloads and Estimated-only
evidence may inform qualified context, never fabricated exact-pair measurements. Secondary
labels are not firsthand verification. Compare only comparable versions, metrics, splits,
harnesses and setup; do not rank noncomparable percentages, composites, normalized Elo or
overlapping samples as project success. Retain counterevidence and nonmonotonic effort results.

Keep source-backed initial guidance and archive discovery separate from learned guidelines
and local execution records. Guideline supersession/removal must not erase original source
facts, unknown metadata or discovery links. Routine agents receive concise rubric/citations
only: no automatic whole-CSV loading or full-dataset prompts. Use compact research/index →
source archive → matching rows on demand, not whole history or unrelated rows. Project-owned
sources and outcomes never become permanent global skill policy.

Routing approval and exact-content guideline approval are distinct. Before the single final
implementation approval present all task/reviewer proposals with family, exact binding,
independent effort, capability/benchmark evidence, rationale, uncertainty disposition and
bounded retry authority. Record approved scope and listed selections distinctly; approval
starts preflight, not a routine second assignment question. Missing hard gates stop readiness.

Inspect the failed child run and invocation before retry/escalation. Unknown cause,
unavailable permitted option or unestablished clean state stops. Preserve valid evidence
and unrelated work; existing task-commit and safety/approval gates remain in force.
Record both attempts and outcomes, selected/observed family/binding/effort or unknown.
No new failed-attempt commit/inverse authority is granted by this rubric. Guidelines express
task/oracle conditions, not permanent family rules from a single outcome.

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
