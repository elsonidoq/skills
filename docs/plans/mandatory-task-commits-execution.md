# Mandatory task commits — execution tracker

## Authorization and preflight

Producer: planner; depth: TinySpec. Owner combined approval: **“Approve implementation”**, recorded in `reviews/mandatory-task-commits-planning-review.md` against source SHA-256 `10bd9145bc61aecbb7df6c045fe7d7c2e1e0f6f335e757a9e15684bab29956c6` and tasks SHA-256 `b0bc9f8a4cf8fe55d917b72cfb545884750db9b60e5257bdd2477dbfca1478d7`. Both hashes rechecked unchanged before execution. Source checkpoint `2c8d168`; tasks/review checkpoint `f86a70d`.

Owner said “go ahead” to the exact recommendation: `sonnet-class` implementation T001–T007 = **openai-codex/gpt-5.6-terra**; fresh independent final reviewer = **openai-codex/gpt-6.1-sol**. No other model switch authorized. Launch preflight remains authoritative; registered model names are not successful launch proof. Requested effort: medium for worker and reviewer, not an escalation to high thinking.

All seven implementation tasks require delegation based on complete task count (>3), not remaining count. One consecutive homogeneous batch is appropriate because all consumers share the new contract, the changes overlap the same reference/test/documentation surfaces, and one writer runs producer-first. No parallel writers. Initial fresh-context brief is bounded to approved artifacts; context must be reassessed if actual run headroom becomes inadequate, without blind retry or arbitrary class changes.

Runtime doctor: async available; native supervisor available; session spawn budget unlimited; run fan-out limit 64; zero active async children before dispatch. Selected worker receives read/edit/write/bash plus supervisor; selected reviewer is fresh/read-only. Git identity and path-limited commit capability verified through preparation commits. Question capability observed working. No SpecKit prerequisite: selected TinySpec.

Selected workspace: current repository `/home/dev/projects/skills`, branch `main`, one writer only. Approval-record changes are contextual preflight work committed before dispatch. Historical `docs/plans/mandatory-task-commits.md` is pre-existing untracked input; preserve byte-for-byte, SHA-256 `8a41de4b5b5716e9f5f2883836ccd2b33023f3a6be54cad5e778d7f287157a85`, never stage or delete it. No other source changes or staged work observed. Task-relative cleanliness permits this known excluded file; no automatic whole-repository cleanup/worktree installation.

Coordination store `memory/coordination/`; no approved guidelines. Use run ID `2026-10-05-mandatory-task-commits-implementation` for separate factual task evidence and reflection, with one compact index row. No learned-guideline writes authorized.

## Execution plan

| Batch | Tasks | Scope | Dependencies | Integration surface | Verification | Class / model | Mode | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | T001–T007 | Contract, coordinator, all consumers/prompts, fixtures, governing docs, integration evidence | Internal T001 → T007, approved order | Shared reference → consumer checkpoints → regression wiring/docs | Per-task required checks and commits; coordinator verifies each checkpoint; final full-range review | sonnet-class / Terra | async delegated, one writer | in_progress |

- [ ] Batch 1 — in_progress; first dependency-ready task T001.

## Task checkpoints

| Task | State | Task baseline / commit | Checks / remaining work |
| --- | --- | --- | --- |
| T001 | pending | not started | shared contract/inventory |
| T002 | pending | not started | coordinator protocol |
| T003 | pending | not started | workflow consumers |
| T004 | pending | not started | standalone skills/prompts |
| T005 | pending | not started | diagnostic mutations/Git fixtures |
| T006 | pending | not started | governing policy/documentation |
| T007 | pending | not started | integrated validation/review packet |

Writer owns task commits and evidence-only metadata checkpoints. After each task, provide exact baseline/task commit/evidence checkpoint and check outcomes via supervisor, then wait for coordinator validation before next-task writes. Coordinator independently inspects actual Git/diff/required checks; unknown or failing state is not commit authority. If a missing commit is recoverable, coordinator alone commits understood verified changes; otherwise stop. Fresh implementers must not commit inherited unknown changes.

Preserve approved source/task contracts; update this tracker and bounded execution evidence rather than editing acceptance definitions. Commit each task's verified changes separately; record its SHA afterward in a focused evidence-only checkpoint before the next task. No per-task independent reviews, no push/deploy/install/paid services, no skip/defer question.

## Final acceptance

Pending all task commits and one fresh independent Sol review of the complete actual committed range. Reviewer findings/dispositions and scoped correction commits will be recorded here. No completion, feature acceptance, runtime-obedience proof or model-causation conclusion is implied by dispatch.
