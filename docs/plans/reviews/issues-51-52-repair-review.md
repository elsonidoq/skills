# Repair review: PR #54 (`ccc8019..232fdcb`)

Reviewed HEAD: `232fdcb4b5be5b730ee7b339109952f14192f8de`. Prior reviewed HEAD: `ccc8019`.
Repair delta: `skills/task-generation/SKILL.md` (lines 171-175) and
`skills/task-generation/scripts/test_contract.py` (lines 198-206).
The review was read-only. I wrote only this file.

## Findings

No new findings.

### Prior Finding 1 (P1, #51 gate timing): resolved

- The old text sent every manual or owner-confirmation step to `gates`. The new text
  (`skills/task-generation/SKILL.md:171-175`) puts three different cases in three different places:
  1. Manual steps never go in `checks`. This agrees with `verification.py:17-24, 79-99`, which run `checks` as shell.
  2. An owner approval that is necessary before the work goes in `gates`. The text also says that the runner
     asks `gates` before the worker starts. This agrees with `graph.py:320-324` (`prepare()` calls
     `manual_gates` before `next_node: 'worker'`), `verification.py:102-109` and
     `docs/coordinate-implementation.md:493-494`.
  3. A manual confirmation of finished work stays as acceptance prose. This agrees with
     `docs/coordinate-implementation.md:492`: the worker owns semantic/manual acceptance and the reviewer
     evaluates it. The observed #51 case ("the coordinator reads the diagnosis report and confirms cause,
     evidence and correction") now becomes acceptance prose. It does not go to a shell check or a pre-start gate.
- The new clause "when dependent work must wait for it, put that gate on the dependent task" is
  correct for the runner. `graph.py:307-308` makes a task eligible only when every `depends` entry is in
  `completed_checkpoints`. Thus the dependent task's gate is asked after the predecessor's checkpoint exists,
  so the owner can inspect the finished work. This is also true in parallel waves, because `_ready_wave`
  gets only `eligible` tasks.
- There is no runner or intake change. The six-rule startup linter text (`SKILL.md:158-159`) did not
  change. The fix stays within the owner-approved scope and does not add a new field or check.
- Test: `test_manual_steps_are_gates_not_shell_checks` (`test_contract.py:198-206`) pins the five new
  clauses. `require_clauses` (`test_contract.py:29-38`) also proves that the test fails when you remove
  any one clause. `body()` (`test_contract.py:24-26`) joins the section on whitespace, so the clause that
  crosses a source line break ("The runner asks `gates` before / the task's worker starts") is matched.
  I ran the test and it passes.

### Prior Finding 2 (P2, monitor filter): unchanged, report only

The repair does not touch it. No change is necessary for this PR.

## Examined and passing

- The full repair diff and the text around it (`SKILL.md:150-185`), including consistency with
  `SKILL.md:104` and `SKILL.md:145` (manual/permission gates in existing fields), which still agree.
- Runner consumption of `gates` and `checks`: `graph.py:300-329`, `verification.py:102-109`.
- Dependency order for the "gate on the dependent task" clause: `graph.py:307-317`.
- `python3 skills/task-generation/scripts/test_contract.py`: OK (I ran it).
- Carried forward from the prior review (still valid; the repair does not touch these files): the #52
  parser change (`engine.py:944`), the approval and recovery boundaries (`engine.py:1242, 1255-1411`,
  `graph.py:1110`), the docs consistency for the finding format, and the runtime tests
  `test_review_format_recovery`, `test_review_chain` and `test_cumulative_review` (64 OK).
- Supervisor-reported (I did not rerun): `test_graph_execution`, `test_recovery` and
  `test_trace_publication`, 52 OK. This closes the prior gap for those findings-fixture tests.

## Open questions

None that affect the verdict.

## Coverage gaps

- No end-to-end test runs a generated task with a `gates` entry, or a dependent-task gate, through the
  runner. The #51 proof is still the skill text, the contract test and the source reading above.
- The skill text controls only what task generation emits. A model can still put manual text in `checks`;
  that is an accepted limit of a text-only fix (the owner chose no runner/intake change).
- If a post-work owner confirmation is necessary and there is no dependent task, the rule leaves it as
  acceptance prose that the worker and reviewer evaluate. An owner-only confirmation then occurs at
  finish-session or final acceptance, not inside the run. This is within the owner-approved scope; it is
  not a defect.
- The monitor's filter regex is outside this repository (prior Finding 2).
- I did not run the full runtime suite myself.

## Verdict

**Ready.** Finding 1 is resolved by `232fdcb`. The #52 change stays ready as in the prior review.
Finding 2 is report only. There are no remaining conditions.
