# Coherence initialization execution

## Authorized intake

Producer planner; selected depth TinySpec. Source `coherence-initialization.md`; tasks `coherence-initialization-tasks.md`; current digest-bound combined approval/review in `reviews/coherence-planning-review.md`. Seven implementation tasks, all sonnet-class. No declared project-memory association.

Owner selections through ask_user:
- Implementation binding: `openai-codex/gpt-6.1-sol`.
- Fresh independent final reviewer binding: `openai-codex/gpt-6.1-sol`, separate read-only reviewer session.
- Dirty-target gate: **Approve these exact bounds**, covering original source skill deletion after preserved baseline; README/REQUIREMENTS naming/onboarding; docs/index new skill and artifact links; memory-handling/compact-memory/finish-session onboarding references; installer retirement/probe inventory/checker adoption-doc carriers; corresponding test fixtures and lint wiring. Additional targets/broader changes require approval. Installer safety corrections only for demonstrated affected defects.
- Commit policy: owner rejects deferred commits; per-task or per-batch commits are mandatory for tracking/regression diagnosis. Owner directs reuse of existing worktrees or feature branches, commit before starting and report that commit; ask on main/dev/staging-like branches. Current checkout is an existing worktree on feature branch `redesign-planning-workflow-tinyspec-standard`. This authorizes an explicit separate current-workspace baseline commit here, then focused per-task commits, not pushing or rewriting unrelated history. This session instruction is not a global contract change.

## Execution graph and strategy

More than three tasks require async sequential delegation. One single-writer batch is coherent: original sources feed merged behavior, retirement inventory, consumer docs, shared focused tests and final reconciliation. No parallel writes, task reordering, forced model change or stage-heading split. Verify each internal producer before its consumers; commit each verified task separately. Parent performs final independent review after implementation, against complete baseline-to-result revision range. Available worker mutation tools: edit/write (registry declarations; task producer successfully wrote a new repository artifact through native execution). Runtime doctor: async available, session spawn budget unlimited, run fan-out cap 64, active async capacity unlimited. No live installation/probe authorized.

| Batch | IDs | Scope | Dependencies | Integration | Verification | Class/model | Mode | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | T001–T007 | Source baseline, merged skill, retirement, consumers/docs, positive/mutation tests, integration | T001→T002→T003→T004→T005→T006→T007 | Skills, installer/probe/checker, canonical docs | Individual acceptance/checkpoints and commits; full deterministic suite; independent final review | sonnet-class / openai-codex/gpt-6.1-sol | Async sequential single writer | in_progress: T001 ready; baseline committed |

- [ ] Batch 1: in_progress; first dependency-ready task T001; baseline commit completed.
- [ ] Independent final review: pending full attributable revision range.

## Baseline and evidence

Before baseline: HEAD `a04e3df68b094f90fb2900994a82d11b1a681581`; no staged paths. Source/task digests match current approval. Existing workspace changes are prior planner work plus Coherence planning/approval/tracker artifacts and will be explicitly separated in the baseline commit. Baseline commit: `7f6c0cb0cbdd15967d91c84b2295a45f3c64a2d3` (`chore: snapshot current planner work before Coherence initialization`), explicitly authorized and reported to the owner before implementation. Worktree was clean immediately after this commit. Task commit IDs, actual results, source-to-merged coverage, residual limitations and review dispositions will be recorded here. Static checks do not prove model obedience; live onboarding/install/load probe remain NOT RUN unless separately authorized.

## Completion

Implementation in progress; independent review remains pending. Status-only task updates preserve approved contracts. Material changes require renewal.

## Verified task checkpoints

- T002: predecessor `685ac3f62b160452d8a219791bd44f4b387130fd` (T001). Implemented seven bounded stages, with stage-local ownership exclusions and separate adoption/documentation authority. All 43 source-ledger carriers pass, including pins, exact stops, dirty-FIRST gate/four investigation outputs, no-op/refresh and structural versus substantive readiness. `PYTHONDONTWRITEBYTECODE=1 python3 skills/initialize-coherence/scripts/test_contract.py`: 4 tests PASS. Initial candidate failures were sentence-case/contiguous report-shape mismatches; normalized sentence case only (no safeguard removed), made report shape explicit. Frontmatter/new relative reference PASS; `git diff --check` PASS. Old operational sources remain unchanged until T003. Full inventory integration not yet claimed.

- T001: predecessor `7f6c0cb0cbdd15967d91c84b2295a45f3c64a2d3`. Captured complete original source bytes/hashes and 43 source-derived ledger rows in `skills/initialize-coherence/scripts/fixtures/source-contract.json`, with stage, ownership transitions, downstream tasks, named positive/rejection checks, A1–A5 mapping and active/history inventory. Every original operational line has a carrier. Original evidence is captured before merged production/deletion. `PYTHONDONTWRITEBYTECODE=1 python3 skills/initialize-coherence/scripts/test_contract.py --baseline`: 3 tests PASS. Smallest meaningful red: `... test_contract.py CandidateTests` failed exactly `initialize-coherence candidate missing` (expected, before T002). Baseline planner checker PASS; existing planner fixtures 48 tests PASS. Source/task production hashes revalidated unchanged before status updates. Only initial dirt was the approved parent baseline tracker update, included here. No staged/unrelated paths. Static coverage is not proof of model obedience.
