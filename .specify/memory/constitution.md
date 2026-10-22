# Coherence Skill Suite Constitution

## Core Principles

### I. Portable Global Assets

Global commands and skills MUST work across unrelated projects without assuming a project name,
layout, model, branch, deployment state, or project-specific policy. Project-local guidance MUST
remain in project-owned stores or project instructions, never in the global skill installation. This prevents one
project's experience from silently changing another project's workflow.

### II. Evidence Before Guidance

Agents MUST distinguish observed outcomes from inferred reusable guidance, preserve uncertainty
and counterevidence, and avoid treating a single failure as a permanent routing rule. Growing
historical evidence MUST be selectively retrievable rather than loaded in full during routine
planning. Compact guidance MUST not become a transcript or substitute for current source evidence.

### III. Explicit Authority

Agents MUST respect the owner's selected planning depth and current-content approval gates.
They MUST NOT implement unapproved scope, silently switch selected models, or modify project guidance without explicit user future-directed feedback authority.
Clear bounded feedback needs no routine second approval; ambiguity asks before writing. Denial, ambiguity, and missing
required capabilities MUST stop the affected stage rather than imply consent.

### IV. Pragmatic Planning and Verification

Choose the simplest approach that meets the approved requirements and the observed risks.
Planning, task decomposition, and checks MUST target the actual changed seam and a concrete
failure mode. Do not add speculative abstractions, redundant artifacts, exhaustive test matrices,
or new test infrastructure without a specific need that existing mechanisms cannot meet. Use the
smallest sufficient check while retaining owner-required acceptance, security, persistence, and
integration checks where applicable. Report PASS, FAIL, NOT RUN, or UNAVAILABLE honestly; static
fixtures alone MUST NOT be represented as runtime-obedience proof.

### V. Safe Execution and Recovery

Implementation MUST follow approved task dependencies, preserve unrelated workspace changes,
verify before claiming completion, and obtain independent review where the workflow requires
it. Authorized retained repository tasks MUST follow the shared
[task-commit contract](../../skills/memory-handling/references/task-commit-contract.md): focused,
path-limited verification commits precede subsequent task work, reporting, or handoff; read-only/no-change
work makes no empty commit; ownership/Git/verification conflicts stop rather than waive the checkpoint.
No automatic STATE maintenance or routine coordination evidence-only checkpoints.
Recovery starts with available summary/recent context and selectively reconstructs uncertain
authority, Git/check/commit and child status; active or unknown children cannot be replaced
without reconciliation. Preserve existing STATE/custom content and historical records.
This does not grant write, guideline, adaptation, external-operation, or runtime-extension authority. Inspect a
failed delegated run and its invocation before retrying, resuming, or relaunching; unknown failures MUST be
reported rather than blindly rerun.

For authorized executable Coordinate Implementation runs, workers may propose/produce owned task changes but do not stage, commit, select work or own workflow persistence. The runner establishes baseline/ownership, runs actual specified project checks and manual gates, inspects actual owned diffs, and creates one focused verified owned-path task or repair commit before subsequent mutation or handoff. Never blindly replay Git after interruption: inspect the actual commit and partial work. Unknown/live work, missing verification/Git authority, failed hooks/checks/signing or ownership conflict block the affected operation; no configure-around, broad staging, reset, history rewrite or discard. Read-only/no-change creates no empty commit. Planning/standalone retained artifacts continue to use their authorized writer's existing focused task-checkpoint contract. Ordinary SQLite task progress is permitted; no agent-written narrative STATE, routine summaries/indexes, reflection or inferred guidance. Preserve independent review, existing STATE/custom content, technical gotchas, historical rows, unrelated dirty work and explicit scope/permission approvals. Six task-linter checks govern task validity; no graph, cgroup, manifest, original-session, intent-settlement or evidence-receipt eligibility is required.

### VI. Compatibility and Ownership

New capabilities MUST preserve existing TinySpec, Standard, and documented legacy workflows
unless an explicit approved change says otherwise. Coordination memory stores only explicit
user feedback intended to change future rounds, never agent-inferred lessons. Missing store
or STATE MUST NOT block otherwise authorized execution. There MUST NOT be automatic
initialization, routine summaries/index updates, reflection or evidence-only commits.
Relevant existing compact guidance is consulted; explicit relevant history retrieval is
selective, index-first where useful. Only needed bounded guidelines ownership may be created
for authorized feedback, never history/index/run scaffolding. Preserve local path/symlink,
sensitive-data, custom, dirty and concurrent ownership safeguards. Keep gotchas, feedback,
substantive task/runtime evidence, documentation and Git ownership distinct.

## Project Constraints

The repository's `AGENTS.md` governs global portability and skill-use policy;
`REQUIREMENTS.md` owns runtime prerequisites and saved planning-assignment requirements; `docs/index.md` routes
other documentation. Reuse a coordination root declared in the current project's instructions
or configuration; otherwise use `<project-root>/memory/coordination/`. Resolve the current project
root from its selected repository/workspace, never from the global skill installation. Every
coordination destination MUST stay inside that project. Gotcha-memory adoption remains a separate
contract and MUST NOT be implicitly initialized by coordination-store setup. Do not store secrets, tokens, personal data,
or sensitive payloads in memory or execution evidence. Prefer bounded skill changes when sufficient. The owner-approved Coordinate Implementation migration permits the existing sequential Python/SQLite task executor plus a thin official Pi SDK host for implementation only; it does not authorize a generalized platform, automatic installations, planning-workflow rewrite or other runtime extensions.

## Development Workflow

Planner presents TinySpec and Standard and obtains the owner's choice; each route preserves
its established artifact and approval gates before coordinator execution. The coordinator
verifies authorization, task evidence, integration, and required independent review. Changes
to shared skill contracts MUST be checked with focused fixtures and the relevant existing
suite checks. Trust approved settled design and task contracts. For the executable Coordinate Implementation path, the runner orders tasks by dependencies, uses the owner-selected model/effort without provenance admission, runs actual specified project checks/manual gates, inspects actual diffs and creates focused task checkpoints. The six task-linter checks are the entire task-startup linter. Old graph/custody/manifest/session/evidence eligibility mandates are superseded; historical rows remain readable, never rewritten as completed effects. No automatic retries of expensive failed runs or invented repair budgets. One writer per worktree and fresh independent read-only full-range final review remain mandatory. Planning remains skill-based: direct asynchronous single-stage delegation, fresh artifact producers, parent inspection before dependent-stage release, and existing owner choice/current-content approval gates remain required. A planning workflow wrapper still needs earned branching, parallel-independent or aggregation justification; it grants no parallel implementation writers. No background LLM decides workflow transitions. In Paseo, global skill/prompt changes require a fresh-session handoff, not an owner reload instruction or automatic restart.

## Governance

This constitution constrains project work alongside `AGENTS.md`; it does not override
higher-priority repository or owner instructions. Amendments require an explicit owner decision,
a recorded rationale, and a check of affected skill contracts and templates. Use semantic
versions: MAJOR for incompatible principle changes, MINOR for new principles or materially
expanded guidance, PATCH for non-semantic clarification. Review compliance against the actual
changed surfaces before final artifact approval; document justified exceptions rather than
silently weakening a rule.

**Version**: 4.1.1 | **Ratified**: 2026-10-05 | **Last Amended**: 2026-10-20

Amendment 4.1.1 removes the one-time restriction on delivery through the runtime
being changed, at the owner's explicit direction. It is not a general workflow
constraint. Sole-writer ownership, scoped authority, verified task checkpoints and
independent review remain unchanged. PATCH corrects an overgeneralized delivery rule.

Amendment 4.1.0 records the owner's approved lean-runtime decision for the reviewed
`workflow-runtime-lean` TinySpec/tasks: deletion-first usable coding retains five readiness
facts (valid work, usable configuration, scoped approval, safe ownership and runnable
verification), scoped authority, real REQUIRED/manual gates, focused commits and independent
final review. It permits the bounded instruction-managed Terra writer checkpoints for this
refactor. Optional telemetry is
observed rather than an execution veto; current settlement, custody and external-action
safeguards remain mandatory. MINOR reflects this material operational simplification.
Rationale: remove duplicate proof protocols without creating another workflow mode.
The subsequent explicit owner direction “Launch a fresh sol subagent to finish t001. Then
continue with the rest also using sol” renews this delivery binding to Sol/medium after
inspection of incomplete Terra runs; it does not change the amendment, historical planning
inputs or generic product profile resolution. T002/T003 outcomes remain pending.


Amendment 4.0.0 records the current owner's actual ask_user decision **“Approve policy amendments”**
for the three exact operative proposals in `specs/003-coordinate-workflow/tasks.md`,
section SHA256 `a318e50bf8914fce910f62d9aedf8700e3b9a1bb0b804a08281e46b0423bdcea`,
unchanged from independent planning review at `79faff9` and confirmed by the parent.
Reproduce the approved section with UTF-8 `read_text().split('## T008 exact operative amendment proposals', 1)[1].split('Remaining constitution/task-commit safeguards', 1)[0]`, without normalization
(3843 bytes); the marker is excluded, its trailing heading text included.
Rationale: replace subjective implementation coordination with the approved bounded
executable runtime while retaining authority, verification, checkpoints and independence.
MAJOR reflects incompatible verifier/committer responsibility changes. Affected owners:
this constitution, shared task-commit contract, planning/task adapters and executable-entry
consumers/templates. No receipt ID or final production acceptance is invented. The current
instruction-managed migration continues its worker-owned verified checkpoints; the runner
clause governs authorized executable runs.

Amendment 3.0.0 records the explicit owner decision in the
[approved review](../../docs/plans/reviews/coordinator-no-bookkeeping-planning-review.md):
no automatic STATE maintenance, routine coordination summaries/index updates, evidence-only
commits or reflection; only explicit future-directed user feedback changes coordination memory.
The owner also approved lightweight plan-trusting coordination and substantive compression.
MAJOR reflects incompatible removal of the mandatory persistence principle, not weakened
verification, task commits, current-content approvals, independent review or safe retries.
Prior amendments below retain their historical provenance; their persistence/state obligations
are superseded by 3.0.0.

Amendment 2.3.0 records owner-approved ephemeral recovery-state semantics and the narrow
STATE-only checkpoint exception in the [approved TinySpec](../../docs/plans/ephemeral-recovery-state-tinyspec.md).
The rationale is lightweight recovery after auto-compaction, not weakened task verification.
Retained implementation and worker evidence commits, approval authority and safety remain.
MINOR reflects the scoped policy change.

Amendment 2.2.0 records the owner's approval of compact one-file-per-run coordination
evidence for future runs, with a bounded compaction of the two 2026-10-06 batch-routing
runs. It preserves indexed selective retrieval, factual task/attempt attribution, distinct
Git evidence checkpoints, historical multi-file compatibility and exact guideline approval;
no existing learned guideline is changed. MINOR reflects a material evidence-layout change.

Amendment 2.1.0 records the owner-approved package-wide mandatory task-checkpoint policy. It
adds no runtime interception/adapter requirement and preserves existing authorization, planning,
guideline, and safety boundaries; the MINOR version reflects materially expanded execution guidance.
