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

- [ ] Batch 1: **in_progress**, T001–T004 verified; T005 next dependency-ready task.
- [ ] Fresh independent final review after all task commits.

Per-task evidence follows; independent acceptance remains pending. This approval record is external to approved source/tasks to avoid recursive self-hashes. Expected task checkbox/evidence changes do not alter task contracts; compare normalized contract content against approved revision evidence when resuming.

## Sequential implementation evidence

Operational checkpoint after T003: shared discovery/planning/evidence/routing hooks committed before reflection and expensive assurance work. No blockers; observed tool/diff capacity adequate for remaining bounded sequence. Fresh independent review is still required.

All commands are local/offline. No association, actual guideline/store, `.pi/` or `.specify/` writes. Original source digest verified; task contracts compared to e3c2910 with checkbox normalization. Commits are recorded at the next checkpoint to avoid recursive self-hashes; the final task commit is identified by its unique subject and returned full revision range.

### T001 — completed

- Missing-clause baseline: canonical coordination reference absent (expected FAIL); existing planner checker PASS.
- Added portable shared association, compact guidelines, selective history, separate evidence/index and conservative approval contract; gotcha rules unchanged.
- Checks: `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-planner-workflow.py` PASS; focused Python clause/layout/link assertions PASS; `git diff --check` PASS. Manual mapping to A1–A10: declared paths/no fallback, record-before-index/resume, unknown/partial/manual and exact approval/drift boundaries inspected.
- Diff inspected: only shared owner/link plus task status/evidence. Commit: `feat: define optional project coordination memory contract` `916642b`.
- No live model or persistence claim; tests for lifecycle/wiring follow T005.

### T002 — completed

- Baseline expected FAIL: no early coordination discovery/handoff in planner.
- Added discovery before brainstorm/assessment/choice and exact source/task/checkpoint handoffs for both routes and direct consumers; optional absence remains read-only, required gotchas remain distinct.
- Checks: `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-planner-workflow.py` PASS; `PYTHONDONTWRITEBYTECODE=1 python3 scripts/test-planner-workflow.py` PASS (74 tests); `PYTHONDONTWRITEBYTECODE=1 python3 skills/task-generation/scripts/test_contract.py` PASS (2 tests); focused early-stage/two-route/link assertions PASS; `git diff --check` PASS.
- Manual fictional walkthrough: an owner-supplied heuristic-implementation guideline with a manual checkpoint flows from early read to informed owner depth choice, source observable, task verification and brief in either route; no-store path invents nothing. This is not actual project evidence or global policy. Existing choice/approval/Standard stages unchanged; diff inspected.
- Commit: `feat: carry project coordination guidance through planning` `e30525e`.

### T003 — completed

- Baseline expected FAIL: absent attributable checkpoint/routing carrier. Added load/write-authority hook, separate factual checkpoint and class-compatible real-work experiment; no actual store writes.
- Manual A3–A5/A11 walkthrough: failed/partial/manual/unknown observations retain individual attempts, resume uses same ID and repairs row after records; absent authority uses handoff. Inspected cause/clean-state/stronger-capability/owner-selection gates stop uncertain escalation.
- Checks: planner checker PASS; coordinator intake PASS (6), batching PASS (3); `git diff --check` PASS. Commands: `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-planner-workflow.py`, `PYTHONDONTWRITEBYTECODE=1 python3 skills/coordinate-implementation/scripts/test_intake_contract.py`, `PYTHONDONTWRITEBYTECODE=1 python3 skills/coordinate-implementation/scripts/test_batching_contract.py`.
- Diff inspected. First whole-file additive-line assertion failed because load sentence was split; inspected cause, then checked the actually frozen execution region: original lines/order retained PASS. Deliberate T003 execution digest `7e13bff8311eb4df622b49b8a46ab7f4b683ade6e12d43fa81b9ff2133378184`; existing safety assertions unchanged.
- Commit: `feat: record coordination outcomes and safe routing experiments` `6a690e7`.

### T004 — completed

- Baseline expected FAIL: no coordinator closeout carrying phase for shared approval protocol. Added post-review/blocked reflection and exact decision/baseline gate; canonical procedure from T001 already supplies full shared protocol unchanged.
- Manual state walkthrough: accept/edit/add require explicit resulting content; reject retains bytes/evidence; pending/unavailable/cancelled/ambiguous grant no write; immediate re-read detects drift and requires renewed approval. Implementation approval alone grants none. Nine reflection prompts and scoped evidence-only/no-update/contrary statuses inspected.
- Checks: `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-planner-workflow.py` PASS; intake (6) and batching (3) commands from T003 PASS; `git diff --check` PASS. Frozen execution original lines/order preserved PASS; digest deliberately refreshed to `89cbd7fa77bcb098d39ff9dcc9c17bc4892de2a248a45dfa25aa1d460e0b4660` for only additive reflection phase. Diff inspected; no safety assertion removed.
- Commit: `feat: gate coordination guideline reflection on exact approval` (hash at next checkpoint).
- Operational hooks checkpoint complete before T005 assurance; actual model/SpecKit behavior NOT RUN, independent final review pending.
