# Requirements Manager execution tracker

## Current state

**OWNER APPROVED EXECUTION: “go ahead”.** Preparation commits record the approved revision-4 task body and batch grouping before T001. T001–T006 are verified and committed with their task evidence; batch 3 is the next approved implementation work. Earlier planning reconciliation: `3817425a08fe7c9bdeefed7e6e3322e268bda02e`; the subsequent batch-approval preparation commit is the complete implementation review baseline.

Approved sequence: T001–T005 (Terra), T006 (Sol), T007–T011 (Terra), then T012 (fresh Sol reviewer). Execute only async background delegation, sequentially, with per-task verification/commits and no per-task reviews. The workflow is regenerated against revision 4.

## Authorization, policy, and capabilities

- Direct bootstrap is owner-selected; do not fabricate a specification or claim the current coordinator already supports its planned intake. Historical/current protection baseline: `fa41d5f3f5aeb7ddfa9963222eff2c0447533059`.
- Models chosen by owner: sonnet-class implementation = openai-codex/gpt-5.6-terra; opus-class implementation = openai-codex/gpt-6.1-sol; fresh independent final reviewer = openai-codex/gpt-6.1-sol.
- All delegation must be async/background. Delegate tools observed: read/edit/write/bash; reviewer is read-only. Git identity and commit capability are available. Refresh capabilities before dispatch as needed, without re-requesting settled selections.
- More than three implementation tasks require delegation. Batches amortize startup and carry useful context across sequential tasks, including internal dependencies/shared files/phase headings. Task ordering remains fixed. Commit each task after verification, before next task; no per-task reviews. One final independent review.
- Task count is not context headroom; pause/split/rotate for observed context limits, model changes, owner gates, incompatible scope or external integration blockers. No forced one-session-per-class limit, parallel implementation, blind retry, or silent model switch.
- No project memory store/adoption contract is declared in this configuration repository's AGENTS.md; do not invent one. SpecKit is not required for this explicit bootstrap.

## Approved implementation batches

| Batch | Task IDs | Context shared within batch | Dependencies | Integration / verification | Class / model | Status |
|---|---|---|---|---|---|---|
| 1 | T001–T005 | Historical/current workflow sources; coverage baseline → shared primitives/validator → EPIC restoration → shared batching criteria | None external; internal prerequisites run sequentially | Draft T001 baseline before replacement text; focused tests/lint/inventory; verify and commit each of five tasks | sonnet-class / Terra | completed |
| 2 | T006 | Origin-specific authorization and shared execution contract built by batch 1 | T003–T005 | Intake gates, local/delegated threshold, context/batching/commit checks; one task commit | opus-class / Sol | completed |
| 3 | T007–T011 | Lightweight producer, routing/docs/discovery, contract tests, mutations and integration evidence | T001–T006 from preceding batches; internal prerequisites run sequentially | Producer/handoff tests, links/lint, operational/named mutation checks, coverage/walkthroughs and full review packet; separate commit for each of five tasks | sonnet-class / Terra | in_progress |

T001's source-first ordering is an internal checkpoint, not an extra agent launch. Phase headings and shared file writes are not automatic split reasons because these are sequential single-writer batches. Batch 2 has one task because of its model-class boundary. The two five-task batches share coherent context and fit the target batch size, subject to actual scope/context observations during execution.

## Final independent review (not an implementation batch)

T012 runs once after batch 3, in a fresh read-only Sol reviewer session. It reads the complete committed implementation range, exact historical EPIC, pre-change protection files, coverage matrix/inventory and actual checks. Parent records findings/dispositions and completion and commits review evidence; confirmed scoped fixes get separate verified commits. Do not resume an implementation session for review. A clean worktree is not the review input.

## Baseline verification

Before the earlier preparation commit: existing validator units PASS (5 tests), task-order PASS, suite lint PASS (21 skills), git diff --check PASS. After revision 4: rerun task-order and diff checks before presenting batches. New workflow/mutation tests and coverage artifact do not yet exist; no runtime behavior is claimed verified.

## Task evidence and commits

| Task | Status | Evidence | Commit |
| --- | --- | --- | --- |
| T001 | completed | Added source-derived requirement matrix, historical inventory, deliberate-change watchlist, and capability/fallback inventory before any replacement skill was read or written. Baseline and post-change suite lint, five validator units, task-order validation, and diff check passed. | recorded with T001 change |
| T002 | completed | Added portable shared gate, bounded owner dialogue, exact decision application, capability stop, deferral/handoff/resume contract and deterministic static checks. | recorded with T002 change |
| T003 | completed | Added shared direct/SpecKit adapter contract and centralized the sole task-order validator with expanded units; no proven active caller needed a forwarding wrapper. | recorded with T003 change |
| T004 | completed | Restored executable EPIC stage sequence with shared primitives, current SpecKit/capability/approval/resume protections, and an observed independent review contract; focused static contract checks added. | recorded with T004 change |
| T005 | completed | Replaced isolation-first batching with context-continuity criteria, upstream coherent-work guidance, task commit checkpoints, async-only sequential batches, and focused static scenario contracts. | recorded with T005 change |
| T006 | completed | Generalized origin-specific authorization/intake, applicable SpecKit only, full-list three-task local/delegated selection and common graph; preserved T005 batching, explicit context/failure safety and fresh final review. Six failing-before/passing-after intake checks plus predecessor contracts/lint/validator passed. | recorded with T006 change |
| T007 | completed | Added plan-free Requirements Manager with durable requirement evidence, shared gate/direct-task adapters, review/approval stale detection, and origin-marked coordinator handoff. Initial absent-skill check failed; four focused static checks, lint, and diff check passed. | recorded with T007 change |

### T006 verification checkpoint

- Fresh bounded session selected at the approved sonnet/opus model-class boundary; one task is intentional. Scheduler context metrics are unavailable; no runtime reuse or model-obedience claim is made.
- Read the approved design/revision-4 tasks, coverage baseline, historical EPIC, protection-baseline coordinator, current coordinator/EPIC/shared task contract, runtime requirements and memory contract. This repository declares no project memory adoption.
- Before behavior edits: `python3 skills/coordinate-implementation/scripts/test_intake_contract.py` **FAIL** (all six new checks); existing batching contract **PASS** (3 tests). This is the smallest static baseline for the intake/strategy defect.
- After edits: intake contract **PASS** (6), batching **PASS** (3), EPIC workflow **PASS** (4), task-generation contract **PASS** (2), task-order units **PASS** (6), shared brainstorming **PASS** (4). All run via their adjacent `scripts/test_*.py` entry points.
- `bash scripts/check-skills-lint.sh` **PASS** (23 skills); `python3 skills/task-generation/scripts/check-task-order.py docs/plans/requirements-manager-tasks.md` **PASS**; `git diff --check` **PASS**. Inspected actual coordinator diff against T005 and protection baseline; no second graph or batching algorithm added.
- Static read-through: EPIC retains both current approvals/spec/plan/review/stage evidence; direct inputs with or without installed SpecKit require no plan; ambiguous/stale inputs stop. Three class/context-fit tasks permit local execution; four and four resumed with three remaining remain delegated. Different class/context pressure delegates the affected segment, with no unauthorized fallback. These are prompt-contract observations, not live trials.
- T006 changes only coordinator instructions, coupled tests and task/tracker evidence. Batch 2 completes here; batch 3 is marked `in_progress` as the next approved unit, not launched by this leaf delegate. Final independent review remains T012; routine wiring/mutations remain T009–T010.

Delegates record changed files, actual checks/results, context limitations and separate task commits; update only assigned completion/evidence fields in task artifact and tracker. Preserve approved definitions and owner decisions. No installer, paid probe, provider/runtime config changes, product work, push or deployment.
