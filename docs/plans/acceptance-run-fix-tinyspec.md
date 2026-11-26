# Default end-to-end acceptance task — TinySpec

**Status:** source with detailed how, after owner design agreement (section 9). Not
implemented. Separate tasks pending; specification review and combined approval pending.

- **Qualified issue:** https://github.com/elsonidoq/skills/issues/56 (authoritative scope).
- **Planning depth:** TinySpec (owner selection).
- **Replaces:** the rejected stage-1 design for a dedicated runtime run-and-fix stage. That
  source and page stay available in Git at commit `8293329`.

## 1. Outcome and scope

**Beneficiary:** the owner. A plan that changes behavior gets, by default and without an owner
request, one last task that uses the integrated feature. A failure goes through the existing
run → fix → rerun loop before the independent final review.

**Included (planning text only):**

- `skills/task-generation/SKILL.md`: the default acceptance task, its opt-out, its
  `owned_paths` rule and its run-safety default.
- `skills/planner/SKILL.md`: the source states the acceptance intent (ON with command, or
  OFF with reason), for TinySpec and Standard.
- `skills/planner/references/approval-and-recovery.md`: the one-line approval-brief item.
- `skills/planner/references/spec-review.md`: source and final task review check presence or
  the OFF reason.
- One extension of an existing contract check (see A8).

**Excluded:** runtime code (`runtime/`), a new runtime stage, a new task field or schema, a new
owner question or approval gate, an ADR, agent-judged or owner-judged acceptance procedures,
automatic flaky reruns, SpecKit template edits, `tiny-spec` and `simplicity-review` edits
(see C1, C2).

## 2. Owner decisions (provenance: issue #56 body and the owner conversation)

- D1 (verbatim): "Yes, I think the current run, fix, repair, rerun loop works perfectly. I
  don't want to induce more complexity than to that. But I just want to include that as a step
  that can happen automatically without me saying, hey, now I want you to do this."
- D2 ("yes" to the proposal; issue #56 requirement 1): task generation adds by default one
  last acceptance task for a behavior-changing plan. It depends on all other tasks in the plan.
  Its required check is a command that uses the integrated feature; exit 0 = pass.
- D3 (issue #56 requirement 3, corrected after independent issue review): the acceptance task
  declares non-empty `owned_paths`: the implementation paths a fix may need (normally the union
  of the earlier tasks' `owned_paths`), minus the command and scenario files. Never
  `owned_paths: []` (a verification-only task that cannot fix) and never omitted (no
  protection). Scenario files are not listed in `generated_outputs`. The required check first
  verifies that the committed scenario files are unchanged, for example
  `git diff --quiet HEAD -- <scenario paths> && <command>`.
- D4: docs-only work, pure refactors and similar work write "No acceptance task" with a reason.
- D5: the existing approval brief shows one line, "Acceptance task: ON (command …)" or
  "OFF (reason …)". No new owner question. The owner can change it at that approval: TinySpec
  combined approval; Standard specification approval and again at final approval.
- D6: specification and task review check that the task is present, or that an OFF reason is
  present and names why the plan does not change behavior (for example docs-only or pure
  refactor).
- D7: no runtime code change; no ADR; command only. Live, production-write, paid or destructive
  effects in the command stay under existing owner gates. Isolated/local resources by default
  are a convention, not an owner requirement.
- D8: the owner accepts these limits: the fixing worker also diagnoses; no automatic flaky
  rerun; an oracle defect or spec gap is found only if the worker asks (`ask_owner`); one
  worker call happens even when the check passes the first time.

## 3. Constraints and verified facts

Repository facts at HEAD `8293329` (verified at source, not assumed):

- F1 — Same-worker correction loop. A failed required check returns the actual failure to the
  same task worker; the runner reruns all checks before checkpointing
  (`runtime/coherence_workflow/graph.py:542-591`, prompt text `:387-398`). An unchanged failure
  after a correction stops the run (`graph.py:574-577`). Checks run as shell commands in the
  project working tree, exit 0 = pass (`runtime/coherence_workflow/verification.py:79-99`).
- F2 — Session bound. One task-worker session gets the initial call plus at most two further
  calls, including check corrections (`docs/coordinate-implementation.md:594-597`,
  `skills/coordinate-implementation/SKILL.md:172`).
- F3 — No-change checkpoint. A task with no edits checkpoints as `no_change` with no commit
  (`runtime/coherence_workflow/git_effects.py:279-286`, `graph.py:648`).
- F4 — Edit/write tools. A claim outside `owned_paths` raises `Blocked`
  (`git_effects.py:207-208`). The adapter returns it as a tool error; the run continues
  (`runtime/coherence_workflow/pi_adapter.py:366-370, 416-426`).
- F5 — Shell changes. A shell-made change outside `owned_paths` is not blocked; it is not
  committed and is logged as `uncommitted_changes` (`git_effects.py:170-182`,
  `graph.py:427-428`; prompt `engine.py:110-112`). It stays in the working tree when the check
  runs. Hence the scenario-file check in D3.
- F5a — `owned_paths: []` makes the task unable to change any file
  (`git_effects.py:134-135, 207-208`); an absent `owned_paths` sets no limit.
- F6 — Final-review fixer. The review-fix task takes the union of all task `owned_paths` and
  all task checks (`runtime/coherence_workflow/engine.py:495-507`). So the fixer reruns the
  acceptance command, and it can edit oracle files that an earlier task owned.
- F7 — Standard coverage. `task-generation` serves both the direct (TinySpec) and SpecKit
  adapters (`skills/task-generation/SKILL.md:21-34`). One rule there covers both depths.
- F8 — Current text. Check commands are "optional task context, not universal acceptance
  boilerplate" (`task-generation/SKILL.md:133-137`); composed acceptance goes "at the first
  boundary with the necessary prerequisites" (`:109-114`). The executive brief list is in
  `approval-and-recovery.md` "Executive brief before approval"; the final task proof check
  is in `spec-review.md` "Design and task proof review". No current text adds a default
  end-to-end task.
- F9 — Executable fields exist: `depends`, `checks`, `owned_paths`, `gates`
  (`task-generation/SKILL.md:150-178`). No new field is necessary.
- F10 — The command can already exist or an earlier task can author it: checks run in the
  working tree at the acceptance task's check time, after its dependencies checkpoint (F1).

Constraints: global skill text stays portable (no project command names; AGENTS.md "Global
Assets"); ADR-0003 (tasks stay authorization-neutral) and ADR-0004 (small isolated local tests
need no extra approval) apply to the acceptance task as to any task. Dependency research: no new
library or external dependency; research skipped for that reason. Early risk reduction: all
relied-on runtime behavior is known and covered by existing runtime tests; no prototype.

## 4. Acceptance criteria

- **A1 Default task.** `task-generation` says: for a behavior-changing plan, add one last
  task by default, depending on every other task in the plan, whose required `checks` entry
  is a command that uses the integrated feature (exit 0 = pass). The owner need not ask.
- **A2 Opt-out.** Docs-only work, pure refactors and similar work write "No acceptance task"
  with a reason instead. Similar work includes instruction or guidance-text changes whose only
  integrated use is a live agent run.
- **A3 Oracle.** The acceptance task declares non-empty `owned_paths` (normally the union of
  the earlier tasks' `owned_paths`; when earlier tasks omit them, every implementation path
  the delivery changes) minus the command and scenario files; never `[]`, never omitted;
  scenario files not in `generated_outputs`. Its required check first verifies the
  committed scenario files are unchanged (`git diff --quiet HEAD -- <scenario paths> &&
  <command>`). The command may already exist or come from an earlier task.
- **A4 Run safety.** One sentence points to the existing `gates` rule: a live,
  production-write, paid or destructive command puts its owner-approval question in the task
  `gates`. Isolated/local resources stay an unenforced convention, not an owner requirement
  (no checker phrase for it).
- **A5 Brief line.** The executive-brief list includes "Acceptance task: ON (command …)" or
  "OFF (reason …)" at TinySpec combined approval and at Standard specification and final
  approval. The owner can change it there. No new question.
- **A6 Source intent.** The planner source-creation guidance requires the source to state the
  acceptance intent (ON with the command or scenario, or OFF with reason).
- **A7 Review.** `spec-review.md` checks, at source review and at final task review, that the
  task is present, or that an OFF reason is present and names why no command can use the
  integrated behavior (docs-only, pure refactor, or guidance text that needs a live agent run).
- **A8 Tests.** An existing contract check (`scripts/check-planner-workflow.py`,
  `check_contracts`) requires the A1–A7 phrases, with a negative case in
  `scripts/test-planner-workflow.py`. `python3 scripts/check-planner-workflow.py` and
  `python3 scripts/test-planner-workflow.py` pass. `scripts/check-skills-lint.sh` passes, or
  shows no new failure beyond the pre-existing set recorded below; its result is reported at
  final review; it is not a task check. Report any check not run.
  Pre-existing lint failures (at `2da2100` and `main` `9ab5d19`, unrelated files):
  `scripts/check-task-commit-contract.py` architectural-planning guard (3);
  `skills/initialize-coherence/scripts/test_contract.py` (2 failures);
  `scripts/test-task-commit-contract.py` (6 failures).
- **A9 No runtime change.** The delivery diff has no change under `runtime/`. Verified once
  over the delivery range at final review, not as a per-task check (a task's check runs before
  its own commit, so a per-task commit diff cannot see that change).

Static text checks prove the text, not model obedience or a live run (repository Definition of
Done).

## 5. Known limits (accepted, D8, plus verified)

- The fixing worker also diagnoses. No separate diagnoser.
- No automatic flaky rerun. A failure with varying output does not hit the unchanged-failure
  stop; the session bound (F2) still stops it.
- An oracle defect or spec gap is found only if the worker asks the owner.
- One worker call happens even when the check passes the first time (F3: no-change checkpoint).
- If a needed fix is outside the acceptance task's `owned_paths`, the edit is refused (F4);
  the worker must ask or return blocked.
- The final-review fixer scope is the union of declared task `owned_paths` (F6), only when
  any task declares them (`engine.py:495-507`). If earlier tasks omit `owned_paths`, the
  acceptance task's list becomes the whole fixer scope. So that list must then name every
  implementation path the delivery changes (10.1).
- The final-review fixer reruns the acceptance check before its checkpoint
  (`engine.py:654`, `:689`). The guard therefore also fails an uncommitted fixer edit to
  scenario files: a correct oracle correction during final review stops for owner direction.
  Scenario changes that earlier tasks committed are visible to the reviewer in the diff.
- `git diff --quiet HEAD` sees changes to tracked scenario files only; a new untracked file in
  a scenario directory is not detected.

## 6. Rejected alternative

A dedicated runtime run-and-fix stage (read-only diagnoser, classifier with escalation routes,
oracle guard, flaky confirmation rerun, new tracing phase), commit `8293329`. The owner rejected
it as more complexity than needed (D1).

## 7. Risks

- R1 Shell bypass of the oracle (F5). Addressed by the scenario-file check (D3, A3).
- R2 Text growth in dense skills. Keep each addition to a few sentences in existing sections.
- R3 Over-application to small changes. The opt-out (A2) and the brief line (A5) let the
  owner see and change it.

## 8. Resolved choices

- **C1:** state the ON/OFF intent once in the planner source-creation guidance (covers TinySpec
  and Standard); no `tiny-spec` edit.
- **C2:** no `simplicity-review.md` edit; it already preserves required acceptance (`:25`).

Both were the recommendations shown on the agreed page; the owner did not object.

## 9. Design agreement

- **Shown content:** `docs/plans/acceptance-run-fix-design.html` at commit `3afa64d`, with this
  source's stage-1 content at the same commit.
- **Answer:** "Agree", via `ask_user`, 2026-11-26. Scope as shown, including C1/C2
  recommendations.
- **Ordering:** agreement came before this detailed how. The page is unchanged since.

## 10. Approach (detailed how)

Text changes are additions of a few sentences in existing sections. Final wording belongs to
the implementing task. Global skill text stays portable: no project command names.

### 10.1 Acceptance-task template (convention in existing fields, no new schema)

- **Position and `depends`:** last task; `depends` lists every other task ID in the plan.
- **`owned_paths`:** non-empty. Normally the union of the earlier tasks' `owned_paths`, minus
  the acceptance command and its scenario files. When earlier tasks omit `owned_paths`, list
  every implementation path the delivery changes; this list also becomes the final-review
  fixer's scope (§5). Never `[]`; never omitted. Scenario files are not in `generated_outputs`.
- **`checks`:** one required command:
  `git diff --quiet HEAD -- <scenario paths> && <command>`. Exit 0 = pass. The command uses
  the integrated feature. It can already exist or an earlier task can author it (then that
  earlier task owns the scenario files).
- **`gates`:** empty by default. Existing rule: a live, production-write, paid or destructive
  command puts its owner-approval question in `gates`. Isolated/local resources are an
  unenforced convention.
- **Description:** authorization-neutral (ADR-0003). States the scenario, the pass meaning, and
  that a failure is fixed inside `owned_paths`, or the worker asks the owner when the oracle or
  the specification looks wrong.
- **Opt-out:** when the plan does not change behavior, the task file has no acceptance task
  and states "No acceptance task: <reason>" (for example docs-only, pure refactor, or
  instruction/guidance text whose only integrated use is a live agent run).

### 10.2 Per-file changes

| File | Section / anchor | Required content |
| --- | --- | --- |
| `skills/task-generation/SKILL.md` | `## Give each task sufficient proof` (after the composed-acceptance paragraph, `:109-114`) | A1–A4: the default last acceptance task and its template (10.1); opt-out with reason; state that it is the explicit exception to "check commands are optional" (`:133-137`) and that the existing check loop runs and fixes it. Covers both adapters (F7). |
| `skills/task-generation/SKILL.md` | `## Encode the tasks for their consumer` (`owned_paths` paragraph, `:164-167`) | One sentence: the acceptance task needs non-empty `owned_paths` without scenario files, not `[]`, not omitted; when earlier tasks omit `owned_paths`, it lists every implementation path the delivery changes, because this list also becomes the final-review fixer's scope; scenario files not in `generated_outputs`. |
| `skills/planner/SKILL.md` | `### Give producers the inputs their owners require`, source-creation bullet (`:144-148`) | A6/C1: the source states acceptance intent: ON with the scenario command, or OFF with a reason that names why no command can use the integrated behavior. |
| `skills/planner/references/approval-and-recovery.md` | `## Executive brief before approval` bullet list | A5: one bullet: "Acceptance task: ON (command …)" or "OFF (reason …)"; the owner can change it in the same approval answer; no separate question. Applies at TinySpec combined approval and Standard specification and final approval. |
| `skills/planner/references/spec-review.md` | `## Definition of done and intent alignment` and `## Design and task proof review` (final task paragraph) | A7: source review checks the ON/OFF intent; final task review checks that the acceptance task is present and follows 10.1, or that the OFF reason names why no command can use the integrated behavior. |
| `scripts/check-planner-workflow.py` | new `ACCEPTANCE_TASK_CARRIERS` tuple `(key, heading, clauses)` next to `ISSUE_ASSOCIATION_CARRIERS` (`:559`), checked from `check_contracts` (`:593-595`) | A8: require the key clauses of A1–A7 in their sections (keys `tasks`, `planner`, `approval`, `spec_review_prompt`). |
| `scripts/test-planner-workflow.py` | new test beside `IssueAssociationWalkthroughTests` (`:253-273`), same pattern | A8: current texts pass; removing each clause from its section, even with an inert summary appended elsewhere, produces an error. |

No change: `skills/tiny-spec/SKILL.md` (C1), `simplicity-review.md` (C2), SpecKit templates
(task-generation covers the SpecKit adapter, F7), `README.md` (its validation section names
`check-skills-lint.sh` generically; no new command), `docs/coordinate-implementation.md`
(runtime behavior unchanged), `runtime/` (A9).

### 10.3 Sequencing

One planning-text change and its contract check are coupled: the checker fails until the text
exists. Either one task (text + checker + test) or two (text first, then checker/test that
depends on it). Task generation decides by executor sizing. This delivery changes only
planning text, so its own acceptance task is OFF: "No acceptance task: planning-guidance
text and its static contract check only; no command can use the integrated planning behavior
without a live model run (outside the Definition of Done); the last task's required checks
already run the composed contract check."

### 10.4 Check-to-criterion mapping

| Criterion | Check | Pass condition |
| --- | --- | --- |
| A1, A2, A3, A4 | `python3 scripts/check-planner-workflow.py` (task-generation carriers) | exit 0 |
| A5 | same (approval carrier) | exit 0 |
| A6 | same (planner carrier) | exit 0 |
| A7 | same (spec-review carrier) | exit 0 |
| A8 | `python3 scripts/test-planner-workflow.py` (task check) | exit 0; new negative test fails on clause removal |
| A8 | `scripts/check-skills-lint.sh` (reported at final review; not a task check) | exit 0, or no new failure beyond the pre-existing set in A8 |
| A9 | `git diff --name-only <review_base>..HEAD -- runtime/` (once at final review; not a task check) | empty output |

The contract check requires one key phrase per criterion (A1–A7), not every sub-clause. No
phrase is required for the isolated/local convention.

Limits: these are static text checks; they do not prove model obedience or a live run.
Final independent review judges the semantic fit of the wording to 10.1.
