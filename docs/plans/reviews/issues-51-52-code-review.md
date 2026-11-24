# Review: PR #54 (`origin/main..ccc8019`, commits b97d779 #51, ccc8019 #52)

Reviewed HEAD: `ccc801947535001a0c19fddf16ec947ef4fbaa80`. Base: `origin/main` = `a18d6c9`.
The review was read-only. I wrote only this file.

## Findings

### 1. Important (P1): the #51 rule sends post-work manual confirmations to a pre-start gate

- Location: `skills/task-generation/SKILL.md:171-173` (new sentence). The test that pins it is at `skills/task-generation/scripts/test_contract.py:198-203`.
- Problem: the new text says "put a manual or owner-confirmation step in the task `gates` list as its question text". The runner asks `gates` **before the worker starts**:
  - `runtime/coherence_workflow/graph.py:322-324`: `prepare()` calls `manual_gates(task, engine.question)` before `next_node: 'worker'`.
  - `docs/coordinate-implementation.md:493-494`: "current owner approval is needed before that task's worker starts".
  - `runtime/coherence_workflow/engine.py:503,526-527`: the fixer task copies every original gate and asks it again before each fixer dispatch.
  - `verification.py:102-109`: any answer other than `yes`/`y` raises `Blocked('manual gate not approved ...')`.
- Impact: the observed #51 case is a post-work step ("the coordinator reads the diagnosis report ... and confirms cause, evidence and correction"). With this rule, task generation moves it to a question that the runner asks before the report exists. If the answerer says no, the task cannot start, which is the same "cannot pass" result as #51 at an earlier point. If the answerer says yes, they approve work that nobody can inspect yet, so the confirmation has no value as acceptance. The routing of the observed case is still wrong. Only the failure is different.
- Basis: there is a contract mismatch between the skill text and the runner's gate timing, which is the subject of question 3. The skill already has a correct place for post-work manual acceptance. `SKILL.md:102-105` requires observable acceptance, and the runner docs make semantic/manual acceptance worker-owned and reviewer-evaluated (`docs/coordinate-implementation.md:492`).
- Smallest fix: change the text only (no runner change), for example: "The runner executes every `checks` entry as a shell command, never manual text. Put an owner approval that must happen before the task starts in `gates` as its question text (asked before the worker starts). Keep a manual confirmation of finished work as acceptance prose for the worker and reviewer." Update the pinned clauses in `test_contract.py` to match. This keeps the owner's choice (no runner/intake change; `gates` for manual gates) and stays within the six-rule linter limit.

### 2. Minor (P2, report only): the external monitor will hide more findings

- Location: `docs/coordinate-implementation-schema.md:344` and `workflow_monitor/README.md:305-307` (both unchanged).
- Observation: the monitor shows a finding "only when it matches the inert `path:line - issue` review form". The new parser accepts forms such as `scripts/a.ts:53 and 269 (with admin/b.ts:146) - ...`, `` `a.py:3` - ...`` and `**a.py:3** - ...`. If the monitor's filter is strict, it will not show these findings in Details. This is not new: before the PR the parser already accepted `1-2 and 4-5` and `, interacting with ...` forms. The monitor code is not in this repository, so I could not confirm its regex.
- Impact: findings are hidden in the display only. The rejection stays in place, the CLI shows the parsed findings (`cli.py:129`, `store.py:1039-1040`), and no data leaks (hidden is the safe direction). No change is necessary for this PR.

No other findings.

## Answers to the specific questions

1. **Regex `^\S+:\d+\b.*?\s-\s+\S` (`engine.py:944`).**
   - Downstream: no consumer parses the location. `run_fix` (`engine.py:484`), `store.review_outcome` (`store.py:986-1003`), the store's pair checks (`store.py:475-484, 819, 861, 926, 935`), the CLI projection and `trace_projection.py:118` treat findings as opaque non-empty strings. A repo-wide grep found no other location regex except the recovery `legacy` regex.
   - Cannot become approval: `engine.py:1242` gives `approved` only when `findings` is empty, and `graph.py:1110` stops (`not an actionable rejection`) when `approved:true` is sent with findings. Recovery (`engine.py:1399`) requires `original.approved is False` and non-empty findings, and writes `rejected`. The widening changes only "malformed stop" into "rejected with findings". It never changes anything into approval. I confirmed directly that `_review_value` keeps the flag as given and the caller decides the state.
   - Valid forms still rejected (all were also rejected before, so there is no regression): `a.py:L12 - x`, `a.py#L12 - x`, en dash or em dash separators, a path that contains spaces. The new negative tests cover a missing line, a location that is not leading, `1x`, a missing separator and an empty defect.
   - Loose acceptance: prose such as `a.py:3 looks fine; nothing - approved` and `a.py:3\n- x` is now a finding. A finding with that text sends a fixer (or stops when `approved:true`) and never approves. This is acceptable under the owner's "only the leading anchor is structural" decision.
2. **Recovery** (`engine.py:1255-1411`): the code still behaves correctly. A transcript must pass the current parser and have at least one finding that the per-stage `legacy` regex rejects. Because of the wider parser, the #52 Cerca run (failed, uncertain, `malformed`, `attempt_count 2`, cross-file finding) can now be recovered through the supported transcript path. That agrees with the #52 resumption condition. A transcript that the new parser rejects still goes to `Blocked`. `docs/coordinate-implementation.md:774` ("current parser accepts but the applicable earlier parser rejected") stays accurate.
3. **#51 against runner consumption:** "`checks` entries run as shell" is correct (`verification.py:17-24, 79-99` include `checks`, `check` and `required[].check`). "`gates` list as its question text" agrees with `manual_gates` (string, or object with `question`/`description`). Timing is wrong for post-work steps. See Finding 1.
4. **Docs:**
   - `skills/coordinate-implementation/SKILL.md:206` and `docs/coordinate-implementation-schema.md:172` agree with the code.
   - `docs/coordinate-implementation.md:595` ("Every blocker uses `path:line - defect`") and `docs/coordinate-implementation-schema.md:511` still agree because they describe the leading anchor.
   - The reviewer prompt (`engine.py:1207-1208`) agrees.
   - The recovery question text "compound-location format failure" (`engine.py:1337`) and the error "not an actionable compound-location rejection" (`engine.py:1402`) are still acceptable.
   - None of these texts is stale apart from the monitor note in Finding 2.

## Examined and passing

- The full diff of the six changed files and the code around each change: `_review_value`, the review dispatch and state at `engine.py:1196-1253`, `_recover_format_rejection`, `graph.py` review routing (`1100-1120`), `run_fix` gate/check inheritance, and `verification.commands/run_checks/manual_gates`.
- Regex behaviour on 11 extra inputs (direct call to `Engine._review_value`): the results are listed in answer 1.
- `runtime/tests`: `test_review_format_recovery test_review_chain test_cumulative_review` passed (64 tests, `runtime/.venv/bin/python`).
- `skills/task-generation/scripts/test_contract.py` passed. `skills/coordinate-implementation/scripts` passed (16 tests).
- `test_review_chain.py:773-795` (malformed types, `"no location or concrete impact"` finding) still stops without a fixer under the new parser.
- No other skill produces `Manual:` text in `checks` (grep).
- No ADR in `docs/decisions/` covers the finding format (from the supervisor's brief; I did not check the ADR index again).

## Coverage gaps

- I did not run the full runtime suite. In particular I did not run `test_graph_execution`, `test_recovery` or `test_trace_publication`, which use findings strings as fixtures. These tests use conforming strings, so I expect no break, but I have not shown it.
- No end-to-end test runs a task with a `gates` entry through task generation and the runner. #51 has proof only from the skill text and the contract test.
- The monitor's actual filter regex is outside this repository.

## Verdict

**Not ready**, with one small condition: correct the #51 sentence so that `gates` is only for owner approvals before the task starts, and post-work manual confirmation stays acceptance prose, never `checks` (Finding 1). Then update the pinned test clauses. The #52 change is ready as it is.
