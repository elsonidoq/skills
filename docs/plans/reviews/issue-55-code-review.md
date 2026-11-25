# Code review: issue #55 (range 4882c3c..7fc3164, branch fix-issue-55)

Reviewer: independent read-only review. Head examined: `7fc3164`. No file changes except this report.

## Findings

No blocking findings. No important findings.

### Minor 1: no negative test for the relaxed check-reference match
- Location: `runtime/coherence_workflow/store.py:718-722` (`Store.completed_checkpoints`); tests in `runtime/tests/test_checkpoint_recovery.py`.
- Observation: the match now compares only the keys that the intent stores (`command`, `exit_code`, `output`). The changed tests prove only the positive path (`test_lost_checkpoint_history_reopens_original_commit_after_head_advances`). No test gives an intent whose `checks[i]` differs from the referenced passing row (other command or output) and expects `Blocked`.
- Impact: a future change that weakens the projection (for example, comparing only `command`) would not fail a test. Current behavior is correct (see "Examined and passing").
- Suggested correction (optional): one small test that edits a retained intent `checks[0]['output']` (or points `check_refs` at another task's row) and asserts `Blocked('checkpoint intent or check references are invalid ...')`.

### Minor 2: an empty-dict check entry now matches any passing row
- Location: `runtime/coherence_workflow/store.py:721`.
- Observation: if `check == {}`, the projection is `{}` and the comparison passes for any passing `check` row with that `seq`, `run_id` and `task_id`. Before the change, `{}` never matched.
- Impact: low. The runtime always writes `checks` from `run_checks` results (`verification.py:93`, three keys) in `graph.py:611-613`, so `{}` occurs only in corrupt or hand-edited history. The row must still be a passing check of the same run and task.
- Suggested correction (optional): require `isinstance(check, dict) and check` before the projection, which also makes the non-dict case explicit. Not required for this fix.

## Answers to the specific questions

### Commit 5783299 (`store.py`)
- Diagnosis is correct. `graph.py:556-561` writes each check row as `{**attempt, **attribution}` (adds `producer_invocation_id`, `correction_id`, and `target_head` when pinned). `graph.py:584-589,611-613` stores in the intent the plain `results` (`command`, `exit_code`, `output`), except in the `verification_target` path where the results already include the attribution. So the old whole-dict comparison failed in the normal path and passed only in the pinned path.
- Wrong command / changed output: rejected. Every key that the intent stores is compared, so a different `command`, `exit_code` or `output` gives a mismatch and `ValueError` -> `Blocked`.
- Failed check: rejected. The SQL requires `kind='check' AND state='passed'` (`store.py:719`); a failed check row is not found.
- Other task or other run: rejected. The SQL requires `run_id=?` and `task_id=?` with the current run and `row['task_id']`; the intent `task_id` must also equal the row task (`store.py:715`).
- Pinned verification path: still stronger. Intent checks include the attribution keys, so they are compared too.
- Non-dict `check`: handled by the existing `except (KeyError, TypeError, ValueError)` -> `Blocked`. A list, int or `None` gives `TypeError` (unhashable key or not iterable). A string iterates its characters, gives a dict that is not equal to the string, and raises `ValueError`. Only `{}` is an accepted edge (Minor 2). A non-dict `details` in the history row would give `AttributeError`, which is not caught; but the runtime always writes dict details, and the old code had no such check either. Not a regression from this diff in practice.

### Commit 7fc3164 (`test_question_triage.mjs`)
- Matches current engine behavior: `166fe07` removed the owner-only `engine.question(...)` call from the review route (`graph.py`, review pair block) and records grants with `decision: 'routine_default'`. `grep owner_only runtime/coherence_workflow/*.py` now finds only `pi_adapter.py` and `trace_capture.py`; no engine producer of owner-only questions remains.
- Matches owner direction: `memory/MEMORY.md` "Routine repair authorization" ("routine repairs are always approved by default").
- Still useful: through the real bridge and production engine it proves (a) the run completes with `exit 0`, (b) two additional pairs are assigned and reserved (Python fixture: reviews 4, fixes 3, 2 grants = 2 reservations, distinct rejecting executions, matching grant ids, review base), and (c) no question message and no `ask_user` call occur, although `ask_user` is registered. (c) is a regression guard against reintroducing round consent.
- Owner-only coverage is not lost: test "parent routes an owner-only continuation through ask_user and rejects routine reply" (lines 63-112) and "owner-only continuation stops when ask_user is unavailable" (line 190 onward) still exercise the bridge owner-only path, the routine-reply rejection, the empty-answer rejection and the unavailable-tool stop. What is gone is only the engine-level producer, which no longer exists.
- Cosmetic only: the `until` message still says "expected composed owner event did not arrive" (line 174); the variable `ownerQuestions` keeps the old name. No action needed.

## Examined and passing
- Full diff `4882c3c..7fc3164` (two commits, two files).
- `store.py:695-745` reconciliation flow, its SQL filters and its exception handling.
- Writers of check rows and checkpoint intents: `graph.py:550-614`; `verification.py` `run_checks` result shape.
- `test_checkpoint_recovery.py` lost-checkpoint test (lines 131-169) and related intent tests.
- `166fe07` changes to `graph.py`/`store.py`, and the memory entry.
- Whole of `runtime/tests/test_question_triage.mjs` (four tests).

## Open questions
None that affect the verdict.

## Verification gaps
- I did not run tests (read-only review; test execution not authorized). Supervisor reports: Python runtime suite 495 OK; all `runtime/tests/*.mjs` pass (66) with `runtime/.venv/bin` on `PATH`.
- Limit that remains: `test_question_triage.mjs` needs the venv `python3` on `PATH` (it spawns `python3` that needs `langgraph`). This environment dependency is outside this diff.
- No negative test for check-reference mismatch (Minor 1).

## Verdict
Ready. Minor 1 and Minor 2 are optional follow-ups and are not merge conditions.
