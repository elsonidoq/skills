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
| 1 | T001–T007 | Contract, coordinator, all consumers/prompts, fixtures, governing docs, integration evidence | Internal T001 → T007, approved order | Shared reference → consumer checkpoints → regression wiring/docs | Per-task required checks and commits; coordinator verifies each checkpoint; final full-range review | sonnet-class / Terra | async delegated, one writer | completed |

- [x] Batch 1 — completed; T001–T007 commits and task-relative checkpoints independently verified. Initial incomplete return was inspected and the retained Terra session continued; fresh final review remains pending.

## Task checkpoints

| Task | State | Task baseline / commit | Checks / remaining work |
| --- | --- | --- | --- |
| T001 | completed | 4781969baa8be02f939fbaaf31f8fc3d70cb8ff3 / f49113d5b6dd5f926c2ecea5fb9780562342a0b8; evidence checkpoint 5021e0ec8b4ca7c2ac2b1f8553d4b59d7e7da0f4 | shared contract/inventory; parent checkpoint validated; lint/diff checks PASS |
| T002 | completed | 5021e0ec8b4ca7c2ac2b1f8553d4b59d7e7da0f4 / d2d1b2f7ac4c744337e2118922cf343b9345128f; coordinator evidence recovery b358b64 | coordinator protocol; parent intake 7/batching 3/static workflow/diff checks PASS |
| T003 | completed | b358b64344a0388328e2079a24fe2d1468e7024b / 65564a4e232872afa99762454754d7412b6f258c; correction bcfb7b3; evidence 251ad9c plus coordinator index recovery | workflow consumers; link/lint tests PASS; actual correction and task-relative clean state independently validated |
| T004 | completed | 7f7ed1ae09b1f7d2751ab1b68809806414b0622a / 5e60119779596f03e0d31e478957cce650a1dbb4; correction 827b684; evidence f162c6d/f33b239 | standalone skills/prompts; restored original hooks; parent validated; links/lint/diff PASS |
| T005 | completed | f33b2395c72a0d4e835123f0cfcdbf388f5764f0 / 0b26a28e31cb618656aaafc01b61ef169ebf0f71; corrections b1b6da4/d2262dd; evidence 48a4245/81d6793/a67497b | diagnostic mutations and Git fixtures PASS; parent validated |
| T006 | completed | a67497b0f879442f64ee9a2d781851da226d8b81 / e7db4ec2dea26e4c25567352850cb29f2087f8ea; evidence 8b2faaa | governing docs/link checks PASS; parent validated |
| T007 | completed | 8b2faaafcd353538ca2dff19c4d628ba9058a81e / f701e697a485b13b0223cd900bf62b9afb3c43d2; evidence 105284c plus parent final metadata reconciliation | integration PASS; parent reran lint and confirmed full packet matches actual committed diff |

**Historical run-specific supervision, not a reusable execution policy:** this completed implementation used per-task supervisor waits. The owner's subsequent “remove that overhead” direction supersedes those waits for future runs: healthy subagents verify/commit internal tasks and continue; coordinator audits all returned task checkpoints at the batch boundary. The original instructions below are retained only as evidence of how this run was executed.

Writer owns task commits and evidence-only metadata checkpoints. After each task, provide exact baseline/task commit/evidence checkpoint and check outcomes via supervisor, then wait for coordinator validation before next-task writes. Coordinator independently inspects actual Git/diff/required checks; unknown or failing state is not commit authority. If a missing commit is recoverable, coordinator alone commits understood verified changes; otherwise stop. Fresh implementers must not commit inherited unknown changes.

Preserve approved source/task contracts; update this tracker and bounded execution evidence rather than editing acceptance definitions. Commit each task's verified changes separately; record its SHA afterward in a focused evidence-only checkpoint before the next task. No per-task independent reviews, no push/deploy/install/paid services, no skip/defer question.

## Inspected execution interruption

Initial worker `0a1e298e-4f37-4ce0-9209-0d1deab128e7` exited with an incomplete final report after T002 task commit. Workflow `96f38eed-425a-47bb-a848-236b1beb4f84` failed acceptance: criterion-1 not-satisfied. Parent inspected status, terminal output and session/tool events; no timeout or infrastructure failure reported. Immediate rejection cause is incomplete batch scope, not failed implementation tests or proven model-capability insufficiency. Both task commits preserved; missing T002 metadata is recovered by coordinator before continuation. Tracked/index clean with historical draft unchanged. Resume must retain the same selected model/session and continue T003–T007, not replay T001/T002 or finalize at an intermediate checkpoint. Final review is not yet launched.

## Final acceptance

Implementation T001–T007 and RF001 are complete with verified focused commits. Initial Sol review of `4781969..9a715c2` was BLOCK for F1, the architectural-planning commit opt-in. After RF001, independent Sol targeted recheck (`fa9d8238-b609-497a-8a5d-e6e45bc1b6e2`) returned **F1 FIXED; READY / Merge verdict OK** against corrected HEAD `ec27632c013d59c8676c177e5f2fe4dd4fa75cb8`. Parent accepted the implementation; final full package lint/integrated checks PASS (11 focused checkpoint tests). Review/disposition: `reviews/mandatory-task-commits-final-review.md`. Acceptance covers the approved instruction-managed protocol and Git/static checks, not runtime-obedience proof, provider/live tests or deployment.

| Correction | State | Binding | Dependencies / verification |
| --- | --- | --- | --- |
| RF001 | completed | f8baf91d527466d61db750121a4892d27bcbdd43 / a742f2064ad6a55450594bf57f13c577662a38f0; evidence ec27632c013d59c8676c177e5f2fe4dd4fa75cb8 | parent checkpoint verified; checks PASS; independent Sol recheck FIXED / READY |

Retained Terra implementation and independent fresh-origin Sol reviewer sessions supplied RF001/recheck without replacement or model switching. Final closeout only records review/tracker/evidence/reflection; no operational edits after reviewed HEAD. No pending implementation tasks or review blockers. Historical untracked draft remains unchanged/excluded. No push/deploy performed. Run `/reload` in pi to load changed global skills.

The original packet covers `4781969baa8be02f939fbaaf31f8fc3d70cb8ff3..105284c001cc8166561a1829716c24e6fe8e3a4f`; coordinator verified it byte-identical to actual Git diff and reran final skill lint PASS. This factual reconciliation is committed afterward; packet/history are regenerated through that resulting metadata commit, with exact final endpoint stored in the external history packet to avoid a self-referential SHA. Original historical draft remains untracked, unchanged and excluded.
