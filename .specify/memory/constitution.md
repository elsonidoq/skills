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
They MUST NOT implement unapproved scope, silently switch selected models, or modify synthesized
project guidance without explicit owner review and approval. Denial, ambiguity, and missing
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
This does not grant write, guideline, adaptation, external-operation, or runtime-extension authority. Inspect a
failed delegated run and its invocation before retrying, resuming, or relaunching; unknown failures MUST be
reported rather than blindly rerun.

### VI. Compatibility and Ownership

New capabilities MUST preserve existing TinySpec, Standard, and documented legacy workflows
unless an explicit approved change says otherwise. Coordination memory is mandatory: every
entry point MUST initialize missing project-local files, notify the user, commit only initialization
files and proceed without a separate setup approval. There MUST NOT be an opt-out or handoff-only
persistence path. Existing files and unrelated staged changes MUST be preserved; repeated entry
MUST NOT duplicate initialization or commits. Creation, commit or evidence-write failures MUST
stop with the exact blocker, not silently select nonpersistent execution. Other optional
capabilities retain their documented absence behavior. Keep authoritative owners distinct: verified gotchas,
execution evidence, synthesized coordination guidance, documentation, and git history MUST NOT
be collapsed into one competing store.

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
suite checks. Before assessment/depth choice or direct task/execution work, ensure the coordination
store exists and read its compact guidelines. Factual evidence and reflection MUST be persisted
in one indexed project-local evidence file per new run, including blocked preselection runs;
older multi-file run records remain valid and selectively retrievable. This bounded
initialization/commit and factual persistence is the exception to preselection read-only operation;
it grants no source/planning/decision-file or unapproved learned-guideline write authority.
Synthesized guideline changes still require explicit review/approval against exact resulting
content. Ordinary planning MUST NOT load execution history by default; justified retrieval is
index-first and relevant-only. When a global skill or project prompt changes, instruct users to
run `/reload` in pi.

## Governance

This constitution constrains project work alongside `AGENTS.md`; it does not override
higher-priority repository or owner instructions. Amendments require an explicit owner decision,
a recorded rationale, and a check of affected skill contracts and templates. Use semantic
versions: MAJOR for incompatible principle changes, MINOR for new principles or materially
expanded guidance, PATCH for non-semantic clarification. Review compliance against the actual
changed surfaces before final artifact approval; document justified exceptions rather than
silently weakening a rule.

**Version**: 2.2.0 | **Ratified**: 2026-10-05 | **Last Amended**: 2026-10-06

Amendment 2.2.0 records the owner's approval of compact one-file-per-run coordination
evidence for future runs, with a bounded compaction of the two 2026-10-06 batch-routing
runs. It preserves indexed selective retrieval, factual task/attempt attribution, distinct
Git evidence checkpoints, historical multi-file compatibility and exact guideline approval;
no existing learned guideline is changed. MINOR reflects a material evidence-layout change.

Amendment 2.1.0 records the owner-approved package-wide mandatory task-checkpoint policy. It
adds no runtime interception/adapter requirement and preserves existing authorization, planning,
guideline, and safety boundaries; the MINOR version reflects materially expanded execution guidance.
