# Default end-to-end acceptance task — tasks

Delivery issue: https://github.com/elsonidoq/skills/issues/56

## Approval record

Source: [TinySpec](acceptance-run-fix-tinyspec.md) at `2da2100` (independent specification
review findings applied). Agreed design page: [acceptance-run-fix-design.html](acceptance-run-fix-design.html)
at `3afa64d` (owner "Agree", 2026-11-26). Task production used the saved `tinyspec-tasks`
operation, `claude-bridge/claude-opus-5-5`, medium. This record holds approval status; the tasks below
do not.

Final task review (fresh correctness and simplicity reviewers) findings were applied in
`949953b` (source) and `02ed732` (tasks). Combined owner approval: "Approve and implement"
via `ask_user` on 2026-11-26, for the source, T001–T002 and the implementation scope at
`02ed732` (sha256: TinySpec `d3743efa…09052`, tasks.md `2f0b778f…cd23d`, tasks.json
`dbdb62e4…7cbc6`), including the changed lint criterion (no new failure beyond the recorded
pre-existing set) and this delivery's acceptance task OFF. Approval starts implementation and
the pre-approved branch/PR delivery.

## Shared worker brief

Read the entire [TinySpec](acceptance-run-fix-tinyspec.md). It is requirements truth. The
[executable JSON](acceptance-run-fix-tasks.json) has the exact owned paths, task-local REQUIRED
pass conditions and check commands. This file is the human presentation, not a second
requirements source. Commands run from the repository root.

Selected executor, passed unchanged:
`/home/dev/.paseo/worktrees/0zfm1a0e/solid-giraffe/.pi/workflow-executor.json`
(task workers `claude-bridge/claude-sonnet-5-5`, medium).

Shared constraints:

- Additions of a few sentences in the named existing sections. Keep every existing sentence;
  existing contract carriers and `skills/task-generation/scripts/test_contract.py` depend on them.
- Global skill text stays portable: no project command names (AGENTS.md "Global Assets").
- No change under `runtime/`, to `skills/tiny-spec/`, `simplicity-review.md`, SpecKit
  templates, `README.md` or `docs/coordinate-implementation.md` (TinySpec 10.2 "No change").
- Final wording belongs to the implementing task; TinySpec 10.1 is the template it describes.
- Static text checks prove the text, not model obedience or a live run.

## Tasks

### T001 — task-generation default acceptance task and its contract check

- **Depends:** none.
- **Owned paths:** `skills/task-generation/SKILL.md`, `scripts/check-planner-workflow.py`,
  `scripts/test-planner-workflow.py`.
- **Work:** TinySpec 10.2 rows 1, 2, 6, 7 for A1–A4. In `## Give each task sufficient proof`,
  after the composed-acceptance paragraph: default last task (depends on all others, required
  command check, exit 0, no owner request, the scenario-unchanged guard form, command may
  pre-exist or come from an earlier task), the explicit exception to "Check commands are
  optional", the existing check loop fixes failures, opt-out with reason, one run-safety
  sentence that points to the existing `gates` rule for live, production-write, paid or
  destructive commands (isolated/local resources is an unenforced convention, no carrier
  phrase). In `## Encode the tasks for their
  consumer` (`owned_paths` paragraph): the non-empty `owned_paths` sentence, including the
  "every implementation path" case and no scenario files in `generated_outputs`. Add
  `ACCEPTANCE_TASK_CARRIERS` and its check to `check_contracts`, with `tasks` entries; add the
  negative test beside `IssueAssociationWalkthroughTests`.
- **REQUIRED:** A1–A4 content present (final review judges semantic fit); `check_contracts`
  requires one key phrase per criterion A1, A2, A3 and A4, not every sub-clause; removal of
  each key phrase fails the check even with an inert summary elsewhere.
- **Checks:** `python3 scripts/check-planner-workflow.py`;
  `python3 scripts/test-planner-workflow.py`;
  `python3 skills/task-generation/scripts/test_contract.py`.

### T002 — planner intent, approval brief line, review check and their contract check

- **Depends:** T001 (shared checker and test files; T002 extends the T001 carrier tuple and
  reviews against the T001 template text).
- **Owned paths:** `skills/planner/SKILL.md`,
  `skills/planner/references/approval-and-recovery.md`,
  `skills/planner/references/spec-review.md`, `scripts/check-planner-workflow.py`,
  `scripts/test-planner-workflow.py`.
- **Work:** TinySpec 10.2 rows 3–7 for A5–A7. Planner source-creation bullet: ON/OFF intent.
  Executive brief: one "Acceptance task: ON (command …)" / "OFF (reason …)" bullet,
  changeable in the same approval answer, no new question, at TinySpec combined and Standard
  specification and final approval. Spec review: intent at source review; presence and
  template fit, or OFF reason, at final task review. Append `planner`, `approval` and
  `spec_review_prompt` carrier entries and extend the negative test.
- **REQUIRED:** A5–A7 content present (final review judges semantic fit); `check_contracts`
  requires one key phrase per criterion A5, A6 and A7 (A7: one per spec-review section);
  T001 key phrases still pass; removal of each new key phrase fails the check even with an
  inert summary elsewhere.
- **Checks:** same three commands as T001.
- **Execution note:** other checks read the edited planner files.
  `scripts/test-task-commit-contract.py` reads clauses from `approval-and-recovery.md`, and
  `skills/planning-brainstorming/scripts/test_contract.py` needs the anchor
  `../planner/SKILL.md#saved-planner-assignments`. Make additions only and keep every
  existing sentence and heading.

No acceptance task: planning-guidance text and its static contract check only; no command can
use the integrated planning behavior without a live model run (outside the Definition of Done);
the last task's required checks already run the composed contract check. (TinySpec 10.3.)

## Criterion mapping

| Criterion | Task | Check |
| --- | --- | --- |
| A1 default task | T001 | `python3 scripts/check-planner-workflow.py` (tasks carrier) |
| A2 opt-out | T001 | same |
| A3 oracle | T001 | same |
| A4 run safety | T001 | same |
| A5 brief line | T002 | same (approval carrier) |
| A6 source intent | T002 | same (planner carrier) |
| A7 review | T002 | same (spec-review carriers) |
| A8 tests | T001, T002 | `python3 scripts/test-planner-workflow.py`, `python3 skills/task-generation/scripts/test_contract.py`; `bash scripts/check-skills-lint.sh` report-only (below) |
| A9 no runtime change | final review | `git diff --name-only <review_base>..HEAD -- runtime/` is empty |

A9 is verified once at final review over the delivery range. It is not a task check: the
runner commits only claimed paths inside `owned_paths`, and no task owns `runtime/`. The run
`review_base` stays the default run baseline. Do not rebase the branch before the run.

## Report-only observation: `bash scripts/check-skills-lint.sh`

The composed lint fails at `2da2100` and at `main` `9ab5d19` for reasons outside this delivery.
It is not a task check (a worker cannot fix those files inside its owned paths). After T002,
the final review runs it and confirms no new failure beyond this pre-existing set:

- `scripts/check-task-commit-contract.py`: "architectural planning checkpoint guard missing"
  for `'focused path-limited task checkpoint'`, `'before completion or handoff'` and
  `'must not push or dispatch additional agents'`.
- `skills/initialize-coherence/scripts/test_contract.py`: 2 failures,
  `CandidateTests.test_consumer_routes_preserve_noninitializing_closeout_and_memory_rules` and
  `ExternalIssueOwnerTests.test_optional_jev_inherits_the_external_issue_owner_boundary`.
- `scripts/test-task-commit-contract.py`: 6 failures (same architectural planning guard).

## Delivery fact

The changed global skills need a fresh-session handoff in Paseo after delivery, not `/reload`.
