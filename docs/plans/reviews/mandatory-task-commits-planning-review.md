# Mandatory task commits — TinySpec planning review

Producer: planner; depth: TinySpec. Review is planner-owned; no independent planning reviewer is required for this path. Combined implementation authorization is **approved**, as recorded below.

## Current-content evidence

- Source: `docs/plans/mandatory-task-commits-tinyspec.md`, SHA-256 `10bd9145bc61aecbb7df6c045fe7d7c2e1e0f6f335e757a9e15684bab29956c6`.
- Tasks: `docs/plans/mandatory-task-commits-tasks.md`, SHA-256 `b0bc9f8a4cf8fe55d917b72cfb545884750db9b60e5257bdd2477dbfca1478d7`.
- Source preparation checkpoint: `2c8d168` (verified focused commit).
- Planning input: `docs/plans/mandatory-task-commits.md`, pre-existing untracked draft, preserved outside checkpoints. Its runtime-gate proposal is superseded by the selected source and owner-approved pragmatic design.
- Owner decisions: explicitly selected TinySpec; approved coordinator-owned commit recovery/fresh-implementer guard without runtime extension; selected Current Sol (`openai-codex/gpt-6.1-sol`) for bounded sonnet-class preparation. Those decisions do not authorize this as-yet-unapproved implementation list.

## Review disposition

READY for combined source/task/scope approval, not implementation acceptance.

| Criterion | Disposition / evidence |
| --- | --- |
| Owner intent | Mandatory task commits, no skip/defer question, coordinator recovery, no fresh blind commit and no extension gate captured explicitly. |
| Traceability | A1: T001/T003/T004/T006; A2: T001/T002/T003/T004/T006; A3: T001/T002/T005; A4/A5: T002/T003/T004/T005; A6: T002/T003/T005/T007; A7: T005/T006/T007. |
| Coverage | 22 current skills accounted for: coordinator T002, 12 workflow consumers T003, nine remaining skills T004; references/prompts/governing docs and tests included. T001 produces durable verified inventory before downstream integration claims. |
| Dependencies | T001 through T007 numbered in producer-first order with earlier explicit prerequisites; shared-file and phase overlaps do not force parallel work or separate sessions. |
| Class share | Seven bounded sonnet-class implementation tasks; zero opus-class, no share exception needed. Preparation provider is not silently reused as implementation/reviewer selection. |
| Authority / safety | Planning/adaptation/guideline approvals and external-operation permissions preserved. Unrelated staged/unstaged changes retained; ambiguous ownership and incompatible policy block rather than waive. |
| Checkpoint semantics | Per-task commits inside coherent batches; coordinator verifies SHA/diff/checks/task-relative cleanliness; fresh/resumed implementers stop on unknown state; metadata closeout is a distinct bounded checkpoint. |
| Verification | Focused static operational checks/mutations plus actual temporary-Git fixtures required; no runtime extension/live provider tests or false model-obedience claim. Existing freeze updated only deliberately with evidence. |
| Recovery | Failed commit prevents dispatch; inspection before retry, interrupted SHA reconciliation, affected-dependency handling for later defects. No automatic cleanup/history rewrite. |
| Documentation / migration | Governing policy and version rationale included; no history migration; no package installation/push/deployment; `/reload` guidance at implemented closeout. |

No unresolved material scope choice remains. Implementation workspace/model/reviewer/capability preflight remains the coordinator's gate. The original draft must not be staged with implementation work merely to satisfy whole-worktree cleanliness.

## Actual validation

- `python3 skills/task-generation/scripts/check-task-order.py docs/plans/mandatory-task-commits-tasks.md`: PASS.
- `python3 scripts/check-planner-workflow.py`: PASS, static instructions only.
- `python3 skills/coordinate-implementation/scripts/test_intake_contract.py`: PASS, 6 tests.
- `python3 skills/coordinate-implementation/scripts/test_batching_contract.py`: PASS, 3 tests.
- `git diff --check`: PASS on tracked changes; new planning artifacts additionally inspected directly.
- SHA-256 source/task identities captured with `sha256sum`.

These checks validate current baseline instructions and planning dependency structure; proposed protocol changes and Git fixtures are **NOT RUN / not implemented**. No fresh independent implementation review or feature acceptance is claimed.

## Approval gate

Owner answered the combined `ask_user` gate: **“Approve implementation”**. This approves exactly the source/task SHA-256 identities above and implementation scope T001–T007. Coordinator preflight starts in this session. The coordinator must obtain implementation/reviewer mappings and preserve actual workspace changes; approval does not waive these gates, authorize external operations or change learned guidelines. Planning task checkpoint: `f86a70d`; approval itself is recorded afterward to avoid self-reference.
