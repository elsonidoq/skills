# Project coordination memory — approval and execution

## Current-content combined approval

Producer: `planner`; depth: TinySpec; source provenance: owner's conversation request “Implementation Prompt: Project-Specific Coordination Memory for the Skill Pack.”

- Source: `docs/plans/project-coordination-memory.md`
- Source SHA256: `1a51f7888d7b90e4a655981965f0c926468c181a8a43ab00bcccf73c0697acb9`
- Tasks: `docs/plans/project-coordination-memory-tasks.md`
- Tasks SHA256: `fdf460094fb45b3b9ef40289d4f47aec447ba8aed38c2f60616e7d3944726cb3`
- Owner answer through `ask_user`: **Approve implementation**.
- Authorized scope: T001–T007, generic coordination-memory support, focused tests and lockstep documentation. Coordinator preflight starts immediately. No actual project-store initialization, live/paid runs, push or deployment.
- Planning preparation model choice: `openai-codex/gpt-6.1-sol`; implementation and independent-review selection remain pending.

## Planner-owned review

Read source and all seven tasks in full. Source A1–A12 map to producer tasks and focused verification consumers. Dependencies are earlier; all tasks are bounded sonnet-class (opus share 0%). Optional coordination discovery is separate from required adopted gotcha memory. Evidence/history is separate from synthesized guidance, with selective reads and explicit memory approval. Existing depth choice, provenance, acceptance, sequential batches, task commits, inspected-cause retries and fresh independent final review remain required. No unresolved material planning gate.

Preparation validation (not feature acceptance):

- `python3 skills/task-generation/scripts/check-task-order.py docs/plans/project-coordination-memory-tasks.md`: PASS.
- `python3 scripts/check-planner-workflow.py`: PASS, static instructions only.
- `python3 scripts/test-planner-workflow.py`: PASS, 74 tests.
- `git diff --check`: PASS.
- Both artifact digests verified against producer reports and current files immediately before approval.

## Workspace and preflight

Existing worktree branch: `project-coordination-memory`; initial HEAD: `6f4448eeaeaf48031a612bd0eef192d9cf3adea2`.
Pre-existing untracked `.pi/` and `.specify/` are excluded from edits/staging. Planning source/tasks are authorized newly created files. No declared project-memory association; no project knowledge inferred. No SpecKit implementation required for TinySpec.

Owner selected through `ask_user`: **Use gpt-6.1-sol for both roles**. Worker and fresh separate reviewer use `openai-codex/gpt-6.1-sol`. Native child launch was observed usable during both preparation stages; builtin worker/reviewer are executable with bounded read/edit tools (reviewer read-only). `ask_user` is callable. Runtime doctor confirms async support, native supervisor channel, unlimited session spawn/active capacity and 64 claims per workflow. No paid/live capability is required. Git commits are permitted by repository policy; stage only authorized paths.

### Execution tracker

Complete implementation count: seven (T001–T007), requiring delegation. One consecutive homogeneous sequential batch retains the shared producer/consumer contract and checks each task before its consumer. Current local context is not used to waive delegated execution; a fresh bounded worker has no accumulated child context. Metrics cannot guarantee capacity; checkpoint early and report observed limitations, rotate only under existing safety rules.

| Batch | Task IDs | Scope | Dependencies | Integration surface | Verification | Class | Mode | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | T001–T007 | Contract, consumers, evidence/routing, reflection, tests, docs, integration | Internal T001 → T002 → T003 → T004 → T005 → T006 → T007 | memory-handling, planner, TinySpec, task-generation, coordinator | Per-task checks and required aggregate regression | sonnet-class | Delegated | in_progress |

- [ ] Batch 1: **in_progress**, T001 first dependency-ready task.
- [ ] Fresh independent final review after all task commits.

Per-task evidence follows; independent acceptance remains pending. This approval record is external to approved source/tasks to avoid recursive self-hashes. Expected task checkbox/evidence changes do not alter task contracts; compare normalized contract content against approved revision evidence when resuming.

## Sequential implementation evidence

All commands are local/offline. No association, actual guideline/store, `.pi/` or `.specify/` writes. Original source digest verified; task contracts compared to e3c2910 with checkbox normalization. Commits are recorded at the next checkpoint to avoid recursive self-hashes; the final task commit is identified by its unique subject and returned full revision range.

### T001 — completed

- Missing-clause baseline: canonical coordination reference absent (expected FAIL); existing planner checker PASS.
- Added portable shared association, compact guidelines, selective history, separate evidence/index and conservative approval contract; gotcha rules unchanged.
- Checks: `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-planner-workflow.py` PASS; focused Python clause/layout/link assertions PASS; `git diff --check` PASS. Manual mapping to A1–A10: declared paths/no fallback, record-before-index/resume, unknown/partial/manual and exact approval/drift boundaries inspected.
- Diff inspected: only shared owner/link plus task status/evidence. Commit: `feat: define optional project coordination memory contract` (hash at next checkpoint).
- No live model or persistence claim; tests for lifecycle/wiring follow T005.
