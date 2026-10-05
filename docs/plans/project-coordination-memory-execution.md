# Project coordination memory — approval and execution

## Current-content combined approval

Producer: `planner`; depth: TinySpec; source provenance: owner's conversation request “Implementation Prompt: Project-Specific Coordination Memory for the Skill Pack.”

- Source: `docs/plans/project-coordination-memory.md`
- Source SHA256: `1a51f7888d7b90e4a655981965f0c926468c181a8a43ab00bcccf73c0697acb9`
- Tasks: `docs/plans/project-coordination-memory-tasks.md`
- Tasks SHA256: `fdf460094fb45b3b9ef40289d4f47aec447ba8aed38c2f60616e7d3944726cb3`
- Owner answer through `ask_user`: **Approve implementation**.
- Authorized scope: T001–T007, generic coordination-memory support, focused tests and lockstep documentation. Coordinator preflight starts immediately. No actual project-store initialization, live/paid runs, push or deployment.
- Planning preparation model choice: `openai-codex/gpt-6.1-sol`; implementation and independent-review owner selections are recorded in preflight below.

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
| 1 | T001–T007 | Contract, consumers, evidence/routing, reflection, tests, docs, integration | Internal T001 → T002 → T003 → T004 → T005 → T006 → T007 | memory-handling, planner, TinySpec, task-generation, coordinator | Per-task checks and required aggregate regression | sonnet-class | Delegated | completed |

- [x] Batch 1: **completed**, T001–T007 sequentially implemented and locally verified/committed; feature acceptance is not self-certified.
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
- Commit: `feat: gate coordination guideline reflection on exact approval` `aad1840`.
- Operational hooks checkpoint complete before T005 assurance; actual model/SpecKit behavior NOT RUN, independent final review pending.

### T005 — completed

- Baseline expected FAIL: no source-specific approval diagnostic or lifecycle fixtures. Extended operational checker with named coordination diagnostics, required canonical links and phase placement; retained every prior assertion, mutation and execution digest.
- Added 18 focused tests (instruction removals/unsafe policies and explicitly simulated filesystem examples) and 4 planner wiring tests. Examples prescribe file operations, not a production persistence/approval engine; no helper introduced. Cover two runs/tasks, failed/partial/manual/unknown, new/resume/interrupted rows retaining prior run, evidence-only/tentative/contrary/no-update, all decision states/exact content/drift, observed selected reads/no match and compatible two-attempt routing.
- First planner test run: FAIL (1/78), moved reflection could still satisfy section lookup after Finish. Inspected cause; added actual phase-order validation instead of weakening mutation. Final planner run PASS (78); focused PASS (18). Explicit removed-drift check rejected with `coordination-approval` diagnostic.
- Commands (Python bytecode disabled for suite commands): `python3 skills/memory-handling/scripts/test_coordination_contract.py` PASS (18); `python3 scripts/check-planner-workflow.py` PASS; `python3 scripts/test-planner-workflow.py` PASS (78); coordinator intake/batching PASS (6/3); task-generation contract/order units PASS (2/7); `python3 skills/task-generation/scripts/check-task-order.py docs/plans/project-coordination-memory-tasks.md` PASS; `bash scripts/check-skills-lint.sh` PASS (22 skills, all bundled suites); `git diff --check` PASS.
- Static diff/new test file inspected: focused source-derived boundaries only, no engine/dependency/model calls. Offline PASS is not live acceptance. Commit: `test: cover coordination memory contracts and simulated lifecycle` `7a148cc`.

### T006 — completed

- Baseline expected FAIL: user docs lacked discoverable optional coordination setup/feedback. Updated README, requirements, routing index and regression guide in lockstep with implemented owner and actual test counts.
- Checks: focused local Markdown link resolution across all four docs PASS; `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-planner-workflow.py` PASS; `PYTHONDONTWRITEBYTECODE=1 python3 skills/memory-handling/scripts/test_coordination_contract.py` PASS (18); `git diff --check` PASS.
- Manual doc-to-contract comparison/diff inspected: optional absence versus required gotcha gate, no-adoption declaration, separate records/selective history, bounded setup/writes/exact approval/drift, owner-selected two-class routing, fictional-only heuristic example and offline versus live NOT RUN all retained. `/reload` advised. No runtime/dependency pin or actual association change.
- Commit: `docs: explain optional coordination memory and verification limits` `5c05148`.

### T007 — completed (implementer integration, not independent acceptance)

- Baseline expected FAIL: aggregate A1–A12 packet not recorded. Reconciled current source → carrier → named checks below; no integration defect required further contract/test scope.
- Required commands, all with `PYTHONDONTWRITEBYTECODE=1` for Python/lint: `python3 skills/memory-handling/scripts/test_coordination_contract.py` PASS (18); `python3 scripts/check-planner-workflow.py` PASS; `python3 scripts/test-planner-workflow.py` PASS (78); `python3 skills/coordinate-implementation/scripts/test_intake_contract.py` PASS (6); `python3 skills/coordinate-implementation/scripts/test_batching_contract.py` PASS (3); `python3 skills/task-generation/scripts/test_contract.py` PASS (2); `python3 skills/task-generation/scripts/test_check_task_order.py` PASS (7); `python3 skills/task-generation/scripts/check-task-order.py docs/plans/project-coordination-memory-tasks.md` PASS; `bash scripts/check-skills-lint.sh` PASS (22 skills and all bundled suites); `git diff --check` PASS.
- Focused aggregate Python inspection PASS: source digest unchanged; task contracts byte-equal to e3c2910 after checkbox normalization; only authorized paths changed; all changed Markdown links resolve; original frozen execution lines/order preserved; no staged files before final task. Manual full carrier diff inspected: early handoff, failure/partial/index/current-content approval and class-compatible escalation preserve TinySpec/direct, Standard/SpecKit and legacy routes, 0% opus, owner gates, sequential batches, task commits and fresh independent final review.
- Final task commit: `test: reconcile coordination memory integration evidence`; resolve with `git log -1 --format=%H --grep='^test: reconcile coordination memory integration evidence$'`. Actual hash/full committed range returned in worker artifact, avoiding a recursive self-hash. Review the seven implementation commits from e3c2910, not merely a clean tree; initial project base is 6f4448eeaeaf48031a612bd0eef192d9cf3adea2.
- No actual association/guideline/store, excluded untracked `.pi/`/`.specify/`, dependency, provider, SpecKit, push or deployment writes/calls. Real model adherence and real SpecKit acceptance NOT RUN (not authorized). Natural-language adherence, evidence quality and compact-index growth remain residual risks; offline simulations do not eliminate them.
- Next action: coordinator obtains one fresh separate owner-selected final review of full range/source/tasks/approval/evidence. Independent review and feature acceptance remain **pending**. Run `/reload` inside pi after these global skill changes.

## A1–A12 integration packet

Local static/simulated status: PASS for each row; this is not independent feature acceptance.
Canonical carrier: `skills/memory-handling/references/project-coordination.md` (PC below).
Named cases are in `skills/memory-handling/scripts/test_coordination_contract.py` unless noted.

| ID | Operational carrier | Named positive / meaningful rejection evidence |
| --- | --- | --- |
| A1 | PC Compact guidelines; planner Discovery + Selected production; TinySpec Inputs; tasks Preconditions | `test_A1_A2_early_association_and_both_route_direct_constraints`; `test_A1_late_discovery_with_summary_intact_is_rejected`; simulated early handoff; required-link negatives |
| A2 | PC Association; all consumer preflights, separate required gotcha stops | Same A1/A2 contract case; `test_A1_A2_simulated_early_guideline_handoff_and_no_store`; removed no-adoption/no-fabrication/gotcha-distinction clauses fail specific diagnostics |
| A3 | PC Separate factual evidence; coordinator Coordination evidence checkpoint | `test_A3_A4_A5_factual_checkpoint_and_index_removals`; `test_A3_A4_simulated_two_runs_multiple_tasks_failed_partial_manual_unknown` |
| A4 | PC per-run summary/task/reflection layout + coordinator checkpoint | Same two-run/multi-task example; removed separate-record checkpoint fails `coordination-checkpoint` |
| A5 | PC record-before-index/resume + coordinator checkpoint | `test_A5_simulated_resume_interrupted_record_then_index_repair` (unique row, prior record retained); record/refresh/reconcile removals fail named diagnostics |
| A6 | PC Conservative reflection; coordinator post-review/blocked reflection | `test_A6_reflection_uncertainty_and_no_update_removals`; `test_A6_simulated_reflection_evidence_only_tentative_contrary_no_update` |
| A7 | PC Exact guideline approval; coordinator reflection approval gate | `test_A7_A8_A9_exact_approval_rejection_and_drift_removals`; `test_A7_A9_simulated_pending_unavailable_cancelled_ambiguous_rejected_bytes`; silent-authority contradiction rejected |
| A8 | Same exact resulting-content/baseline re-read carriers | `test_A8_simulated_exact_accept_edit_add_content_and_baseline_evidence`; `test_A8_simulated_concurrent_drift_preserved_and_renewal_pending`; removed current-content/diff/selection clauses rejected |
| A9 | Same explicit rejection/evidence retention carriers | Pending/reject example checks bytes plus retained evidence/disposition; removal of byte-identity/disposition rejected |
| A10 | PC Selective historical retrieval; planner/direct consumer clarification + coordinator synthesis | `test_A10_selective_index_first_and_no_match_removals`; `test_A10_simulated_index_first_relevant_only_and_no_match_uncertainty`; bulk policies rejected |
| A11 | PC Class-compatible routing; task residual notes; coordinator Select Execution Capability + checkpoint | `test_A11_routing_selection_class_and_inspected_cause_removals`; factual two-attempt fictional fixture; `test_unsafe_bulk_silent_drift_class_retry_and_single_outcome_policies` |
| A12 | Unchanged existing route/approval/class/share/graph/commit/review clauses; deliberately reviewed digest | `test_A12_existing_execution_safeguards_survive_mutations`; planner 78 tests incl `ProjectCoordinationWiringTests`; coordinator/task/order suites and lint; baseline original-line-order check |

No optional memory approval is pending for this repository because none was requested and no store is associated. Future actual guideline proposals require their own explicit approval; implementation approval is not reusable memory authority.
