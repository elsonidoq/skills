# ADR decisions — TinySpec planning review

## Scope and authority

Planner-owned review, not an independent implementation review. Owner selected
TinySpec, Sol/medium planning producers, and granular outcomes suitable for intended
Terra/medium implementation. Exact implementation binding remains for later selection.
**Planning only: combined artifact approval and a separate explicit instruction to
start implementation remain outstanding. Approval of planning alone cannot launch work.**

Owner permits planning in this concurrently edited checkout confined to our created
files. A temporary no-commit instruction has now been lifted. No unrelated files,
shared indexes, skills, runtime, application files or memory were edited by this review.

## Reviewed content

SHA-256 of complete UTF-8 file bytes (approval applies to these contents):

| Artifact | SHA-256 |
| --- | --- |
| `docs/plans/adr-decisions-tinyspec.md` | `f2d9e2cb6ed1dba8fc37ece57d7ab83377032df4c7df110e599f5a7457c676ce` |
| `docs/plans/adr-decisions-tasks.md` | `9e169cf50f05c063b2e11dad80727b6647e3ab7b494fd1d68357f85b1b4e474f` |
| `docs/plans/adr-decisions-tasks.json` | `27bcdb6196d7b667ec7498085f2a979cbd27fbdc75c59a25c6a6b48a34a54f68` |

Source checkpoint: `4207aba5461c8c400b99f1c85516a3e0ac3db2c3`.
Task checkpoint: `728da6060233ab82e4543a426f0da9d0109cdc44`.
Unrelated HEAD advancement is expected; approval comparison uses these scoped contents.

## Findings and disposition

- Initial broad planning/execution milestones were too coarse for the owner's later
  Terra/medium sizing requirement. Corrected by the original producers: source records
  intended executor and task-sizing constraint; task list now has eleven bounded outcomes.
- T001 delivers the canonical contract (A1/A2); T002 closeout (A3); T003 adoption (A4).
  T004–T009 separate orchestration, source/task adapter, brainstorming, architecture,
  implementation-skill and paired review contracts (A5). T010 owns only actual engine
  prompt text/captures (A5). T011 publishes bounded docs and composes delivered evidence (A6).
- Each task has owned paths, a consumed interface and local completion oracle. Ordinary
  tests/docs/checkpoints stay with delivery. Thin consumers depend on the canonical
  contract; shared test-file edits require sequential ownership checks, not invented
  producer dependencies. Documentation integration depends on delivered consumers.
- Accepted outcomes and explicitly mandated mechanisms remain protected. Compatible
  helper deletion adds no gate. Approval, implementation status and permission to act
  are distinct; proposed supersession cannot authorize conflicting changes.
- Specs/current docs retain their owners; no bulk migration, historical backfill,
  guessed ADR-store location, new approval ceremony or enforcement subsystem is included.
  Missing storage alone does not block unrelated legacy work.
- Runtime scope is justified by the final reviewer's disabled automatic skill loading.
  T010 changes only two existing prompts and their tests, not the host/runtime design.
  It cannot run underneath current work: fresh sole-writer/path checks and completion
  of the running workflow remain explicit future implementation boundaries.
- No separate prototype or external research is justified for these known local seams.
  Pressure/contract scenarios and actual prompt captures are proportional; they do not
  prove unrestricted model obedience. No mandatory paid/provider/live test is introduced.
- Shared-index links are deferred to T011, honoring current created-files-only authority.
  Paseo activation later needs a fresh-session handoff, not automatic reload/restart.

**Review result: no unresolved planning blocker in reviewed content.** This is not
feature acceptance, proof of current capabilities, or implementation authorization.

## Verification

PASS: both actual task-order validators:

- `python3 skills/task-generation/scripts/check-task-order.py docs/plans/adr-decisions-tasks.json`
- `python3 skills/task-generation/scripts/check-task-order.py docs/plans/adr-decisions-tasks.md`

PASS: parent inspected complete source and both task representations, producer commits
and actual scoped diffs. Focused Python assertions checked eleven tasks, A1–A6 coverage,
check/pass/evidence fields, owned paths/consumed interfaces, argv command shapes, separate
Terra/Sol intent, and minimal T010 runtime paths. Source/task paths have no uncommitted
changes; reviewed SHA-256 identities are above. Owned whitespace checks passed.

NOT RUN: future feature/contract/runtime acceptance tests, live model behavior, actual
adoption, store creation and independent final implementation review. They are not
claimed satisfied by planning syntax or scenario descriptions.

## Approval

Owner answered **“Approve planning only”** through `ask_user` after the full task brief.
This approves the combined source/task contents identified by the SHA-256 values above,
not implementation. **Implementation remains stopped until the owner's separate explicit
go-ahead.** Intended implementation family/effort remains Terra/medium; exact binding and
usable configuration are unresolved until later preflight. Any future material source/task
change requires affected review and renewed approval; current runtime/path state must be
inspected again before implementation.
