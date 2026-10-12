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
`REQUIREMENTS.md` owns runtime prerequisites and model/effort routing requirements; `docs/index.md` routes
other documentation. Reuse a coordination root declared in the current project's instructions
or configuration; otherwise use `<project-root>/memory/coordination/`. Resolve the current project
root from its selected repository/workspace, never from the global skill installation. Every
coordination destination MUST stay inside that project. Gotcha-memory adoption remains a separate
contract and MUST NOT be implicitly initialized by coordination-store setup. Do not store secrets, tokens, personal data,
or sensitive payloads in memory or execution evidence. Avoid a new framework when a bounded
extension of the existing skills suffices.

## Development Workflow

Planner presents TinySpec and Standard and obtains the owner's choice; each route preserves
its established artifact and approval gates before coordinator execution. The coordinator
verifies authorization, task evidence, integration, and required independent review. Changes
to shared skill contracts MUST be checked with focused fixtures and the relevant existing
suite checks. Trust approved settled design and task contracts: bounded delegation,
actual diff/focused commit/REQUIRED audit, dependency-ready advance and independent final
review. No routine replanning, unchanged preflight loops or broad redundant checks.
Concrete invalidation reopens only affected decisions/checks; reuse applicable proof elsewhere.
Planner defaults to direct asynchronous single-stage dispatch with parent inspection before
next-stage release. Workflow wrappers need earned orchestration, not a single child or
sequential convenience; they preserve stage authority/reviewer independence and never
imply parallel implementation permission. Global skill/prompt changes require `/reload` in pi.

## Governance

This constitution constrains project work alongside `AGENTS.md`; it does not override
higher-priority repository or owner instructions. Amendments require an explicit owner decision,
a recorded rationale, and a check of affected skill contracts and templates. Use semantic
versions: MAJOR for incompatible principle changes, MINOR for new principles or materially
expanded guidance, PATCH for non-semantic clarification. Review compliance against the actual
changed surfaces before final artifact approval; document justified exceptions rather than
silently weakening a rule.

**Version**: 3.0.0 | **Ratified**: 2026-10-05 | **Last Amended**: 2026-10-12

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
