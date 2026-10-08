# Ephemeral recovery state — tasks

Direct TinySpec adapter; [source](ephemeral-recovery-state-tinyspec.md), A1–A6;
source checkpoint ca2d2af. Preparation authorized; implementation pending combined approval.
[Run evidence](../../memory/coordination/evidence/2026-10-08-ephemeral-recovery-state/SUMMARY.md)
records review, approval identities and checkpoints.

## Shared context

STATE is small ephemeral recovery navigation, never task history or authorization. Remove
finished attributable work; preserve genuinely ongoing/gated/unrelated items. Retain worker
task/evidence commits, current-content approvals, independent final review and runtime/Git
reconciliation safety. Explicitly change only the state-specific checkpoint requirements.
No dependency research/prototype: instruction consistency is tested at existing contract seams;
agent reconstruction uses bounded real native runtime, not a new harness or actual compaction.
Project memory has no gotchas or approved coordination guidance.

Required capabilities: local read/edit, Git with existing identity, Python 3, registered native
fresh-context delegate/reviewer and exact owner-selected profiles at dispatch. No installation,
external CLI fallback, provider infrastructure operation, push/deploy, historical migration,
learned-guideline mutation or runtime extension. Missing REQUIRED evidence stops acceptance.
Inspect existing ownership and diff before writes/commits; preserve unrelated work and stage
explicit paths. Use the existing checkpoint/coordination contracts until their approved scoped
changes are implemented. Independent review cannot be replaced with producer self-review.

## Implementation

- [ ] T001 Replace heavyweight state protocol and validate its coupled consumers
  - **Depends**: none
  - **Outcome**: source A1–A6 implemented coherently, including shared policy exceptions, focused regressions, lockstep active docs and bounded native recovery proof.
  - **Files / interfaces**: `skills/coordinate-implementation/SKILL.md` (snapshot/recovery and references to update cadence); `skills/finish-session/SKILL.md`; `skills/memory-handling/references/{task-commit-contract,project-coordination}.md`; `skills/coordinate-implementation/scripts/test_state_contract.py`; affected existing assertions in `scripts/{check,test}-task-commit-contract.py` and `skills/memory-handling/scripts/`; `README.md`, `REQUIREMENTS.md`, `AGENTS.md`, `docs/index.md`, `.specify/memory/constitution.md` for explicit scoped exception/alignment. Inspect `skills/{initialize-coherence,finish-session-jev}/SKILL.md` and coordinator related fixtures; change only demonstrated active contradictions or invalidated assertions. Leave historical sources/evidence unchanged. Project STATE/run evidence are coordinator-owned, not delegated implementation scope. Disposable runtime scenario lives outside retained repository output.
  - **Context / reasoning**: shared owner and consumers must change together to avoid heavyweight fallback. Medium residual reasoning: coupled instructions/tests and selective recovery safety; no model assignment by task producer. No artificial separate docs/test task because they constitute the same changed contract.
  - **REQUIRED acceptance / checks**:
    - **T001/V1 → A1**: owner/closeout define small recovery-only bookmark with goal/authority/run/next action/blocker example and no mandatory SHA/check ledger. Finished-entry removal, concurrent/gated retention, durable-byte preservation and empty repeat closeout remain covered by existing scenarios and targeted mutations. Evidence: focused state unittest output plus actual section diff; no extra manual permission beyond approved writes.
    - **T001/V2 → A2**: section-bound assertions/mutations reject restored mandatory dispatch-intent checkpoint, routine task/batch/check/commit/poll update or unconditional recovery refresh. Symbolic write schedule demonstrates only start/returned-ID/material-action/completion writes and unchanged skip. Evidence: state unittest named cases/PASS; static evidence only.
    - **T001/V3 → A3**: shared commit/evidence and active consumers allow pending coordinator-owned state and state-only closeout without separate commit/summary/index event. Existing Git fixture checks safe inclusion in an otherwise-required commit and unrelated dirty preservation; worker task/evidence checkpoints and index race/ownership guards remain. Evidence: state, task-commit and coordination suites PASS plus bounded active-carrier comparison. Smallest layer: existing local symbolic/Git mechanisms, no new runtime persistence code.
    - **T001/V4 → A4**: selective recovery rules retain source permission validation before action, Git/runtime inspection before continuation, unknown/missing-ID reconciliation, no running-child duplicate dispatch and inspected failure. Focused mutation/recovery scenarios detect removed safeguards. Evidence: named state assertions/scenarios and actual diff; no unconditional history reread requirement.
    - **T001/V5 → A5**: lockstep active documentation and scoped constitution checkpoint exception agree with implementation; changed links resolve. Commands: `python3 -B skills/coordinate-implementation/scripts/test_state_contract.py`; `python3 -B scripts/check-task-commit-contract.py`; `python3 -B scripts/test-task-commit-contract.py`; `python3 -B -m unittest discover -s skills/coordinate-implementation/scripts -p 'test_*_contract.py'`; run existing coordination contract suite discovered in `skills/memory-handling/scripts/`; `git diff --check`. Evidence: commands/counts, carrier dispositions and link/diff inspection. Related suites are justified by shared state/commit/evidence coupling, not broad repository audit. Other suites optional unless a changed assertion/dependency invalidates them.
    - **T001/V6 → A6**: coordinator runs one bounded fresh-context read-only native-agent recovery scenario using disposable local files: small bookmark points to minimal authoritative source/tasks/approval; files contain pending task/gate truth not duplicated in state. Ask agent to determine big picture/authorized pending work/next action and active-or-unknown-child handling without writing. Pass requires correct reconstruction from links and no duplicate dispatch/acceptance inferred from bookmark. Evidence: exact selected/observed profile, input/result pointers, inspected transcript/reads and concise outcome in existing run SUMMARY. Gate: owner-selected available profile, native launch and read-only scratch permission; missing/failed result is NOT VERIFIED, inspected failure before any retry. Honest limit: fresh-context reconstruction, not actual automatic compaction or sustained cadence proof. Do not build a harness; preserve scratch through independent review then only attributable cleanup.
  - **Expected verification effort**: focused existing contract/mutation/Git suites, bounded active-carrier diff/link review and one small native reconstruction exercise. No exhaustive matrices, timed quota, actual forced compaction or expensive integration required.
  - **Integration / release**: coordinator verifies ownership/baselines before execution. Commit retained contract/test/docs changes as one focused task commit, then distinct factual evidence checkpoint. Runtime evidence remains in the same run record. Fresh independent final reviewer checks committed diff, V1–V6 and scoped exception/safety boundaries; findings stop acceptance and fixes get separate verified commits. If execution disproves approach/criteria, retain evidence and return affected source/tasks to planner review/renewal, never weaken checks. At closeout remove only this verified finished current entry; unrelated/gated work survives. Report `/reload` after global skill changes.

## Planning validation

Producer → consumers → validation → cleanup: coordinator bookmark owner → shared checkpoint/
evidence and finish-session/docs → existing focused checks/native reconstruction/independent
review → attributable scratch cleanup only after proof consumption. All retained production
fixtures remain. One task has no forward/story dependency; task-order validation and manual
A1–A6/V1–V6 traceability are required before combined approval. Review/approval identity belongs
in linked run evidence, not recursive self-hashes in this mutable task artifact.
