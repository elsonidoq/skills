# Acceptance run-and-fix stage — TinySpec

> **Stage 1 — what, scope, decisions and acceptance only.** The detailed how (state fields,
> history row schema, node code, resume rules per node) is PENDING the owner's explicit
> agreement to the [interactive high-level design](acceptance-run-fix-design.html). Do not
> generate tasks from this file until the detailed how is written after that agreement.

- **Qualified issue:** <https://github.com/elsonidoq/skills/issues/56>
  (`github.com/elsonidoq/skills#56`). The issue body holds the owner-approved design and
  requirements 1–11; this source carries them as requirements.
- **Planning depth:** TinySpec → Tasks → Implement, selected by the owner on 2026-11-26.
- **Status:** PROPOSED. Nothing in this file is implemented.

## Outcome and scope

**Beneficiary.** The owner and every project that runs planned work through
`coordinate-implementation`.

**Problem (verified).** The runner has two correction loops: per-task required checks
(`runtime/coherence_workflow/graph.py`, `checks` node, failure returns to the same worker) and
the read-only independent final review with scoped repair (`_add_review_nodes`). After the last
task checkpoint, `no_ready()` routes directly to `review_route` (`graph.py`, `no_ready`).
Nothing runs the integrated result against its intended behavior. "Every task passed, but the
feature does not work when used" is not detected.

**Required behavior.** An optional acceptance run-and-fix stage runs after all implementation
tasks are checkpointed and before the independent final review. A fixed controller graph in
the runner moves between these nodes:

```
run ──pass──► stage complete → final review
 │
fail (confirmed by one rerun)
 ▼
diagnose ──► classify ──► implementation defect ──► fix ──► run
                     ├──► environment / flaky   ──► rerun or stop (see choice C1)
                     ├──► oracle defect         ──► escalate to owner
                     └──► spec gap / scope      ──► escalate to owner
```

**Included surfaces.**

- Planning: `skills/planner/SKILL.md` (approval-brief line; Standard declaration),
  `skills/planner/references/spec-review.md` (reviewer checks the ON/OFF choice),
  `skills/tiny-spec/SKILL.md` (source declares the section), `skills/task-generation/SKILL.md`
  and its `scripts/check-task-order.py` (executable handoff of scenarios; see choice C5).
- Runner: `runtime/coherence_workflow/graph.py` (stage nodes between the last checkpoint and
  `review_route`), `engine.py` (diagnoser/fixer prompts, reviewer evidence section),
  `verification.py` (reused command execution), `tracing.py` (phase name), and offline tests in
  `runtime/tests/`.
- Documentation: `skills/coordinate-implementation/SKILL.md`, `docs/coordinate-implementation.md`,
  `docs/coordinate-implementation-schema.md`, and one new ADR (planned; see Docs/ADR obligations).

**Exclusions.**

- Agent-judged and owner-judged ("procedure") scenarios. Owner decision (a) narrows
  requirement 1 to command scenarios. Possible follow-up issue.
- Stage display in `coherence-status` (status CLI snapshot) and the Paseo `coherence-status`
  plugin. Verified: both show run and tasks only, so they do not enumerate stages
  (`runtime/coherence_workflow/status_cli.py`, `snapshot`; `paseo_plugins/coherence-status/OVERVIEW.md`).
  `workflow_monitor/` is a retired README only.
- A new intake check, a new SQL table, a new recovery semantic, a new executor JSON key, a
  cost/token budget subsystem, sandboxing of scenario commands.
- Running acceptance scenarios again after a final-review repair (see choice C6).
- Changes to SpecKit templates in `.specify/templates/` (see choice C7).
- Historical runs, history rows and approvals: unchanged; no backfill or conversion.

## Decisions and constraints

### Owner decisions (binding, this planning session, 2026-11-26)

- **(a) Oracle type: command only.** "Each scenario is a command or script; exit 0 = pass.
  Multi-step checks are written as scripts. Agent-judged and owner-judged ('procedure')
  scenarios are OUT OF SCOPE now (possible follow-up issue)." Written pass/fail criteria and
  environment stay as required fields: criteria are input for the diagnoser; the exit code
  decides pass.
- **(b) ON/OFF protocol, no new owner question.** "The source producer of each future plan
  writes either an 'Acceptance scenarios' section or 'No acceptance scenarios' with a reason.
  The independent spec reviewer checks the choice. The existing approval brief shows one line
  'Run-and-fix stage: ON (n scenarios) / OFF (reason)'. TinySpec: combined approval; Standard:
  specification approval and shown again at final approval. Live/paid/destructive scenario
  effects still go through existing owner gates. The runner runs the stage only when scenarios
  are present; otherwise behavior is exactly as today."
- **(c) Planning depth:** TinySpec → Tasks → Implement.
- **Accepted design and requirements 1–11:** issue #56 body, "Accepted design (owner-approved)".

### Accepted ADR constraints (`docs/decisions/index.md`, read in full)

- [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md): the runner
  injects current launch authority into worker prompts, including corrective and resumed ones.
  → The diagnoser and fixer prompts carry `_IMPLEMENTATION_AUTHORITY` (fixer) and the
  current-authority statement; scenario blocks stay authorization-neutral (no approval status
  text). A launch does not authorize automatic retries.
- [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md): one shared
  `_ROUTINE_AUTHORITY` block; small isolated tests and local test databases are allowed; no
  resource-control subsystem; no blind retries of expensive failed executions.
  → The fixer prompt includes `_ROUTINE_AUTHORITY` and `_DECISION_CONSTRAINTS` unchanged;
  scenario defaults are isolated/local; the stage adds no resource ceiling; an uncertain or
  failed agent invocation is never replayed automatically.

### Owner guidance (`memory/MEMORY.md`)

- Routine stage iterations (run, rerun, diagnose, fix) do not wake the parent. Only an agent
  or owner question and terminal workflow completion (success or error) trigger a parent turn.
- Routine technical choices are autonomous; ask only product or material scope questions.
  Routine repairs inside approved scope are approved by default.
- Executor: `.pi/workflow-executor.json` (workers Sonnet 5.5/medium; implementation fallback
  and reviewers Opus 5.5/medium). The stage adds no executor key (see choice C4).

### Repository-derived constraints (verified at source)

| Evidence | Constraint |
| --- | --- |
| `intake.py` `admit`: six checks only; a dict contract keeps other top-level keys | Scenarios live in one optional top-level contract key. No new intake check (owner mandate in `AGENTS.md`). |
| `store.start(... contract=...)`; `validate()` and `_run_graph` compare the retained contract on resume | The scenario block is immutable for the run. A changed block on resume stops with the existing "inputs differ" diagnostic. |
| `verification._run_check`: command string or argv, captured output, interruption recorded | Scenario runs reuse this function. No new process runner. |
| `graph.py` `checks`: "required check failed and remains unchanged after scoped correction" when the new failure equals the previous attempt | Precedent for the no-progress rule (choice C3). |
| `engine.run_fix`: `FocusedGit`, union of task checks, `fixer_check` / `fixer_checkpoint` rows, `repair_context` scope text | The acceptance fixer reuses this pattern. It must not be recorded in the review chain (`route()` reads the last review execution). |
| `runtime/pi-host/host.mjs`: `readOnly` sessions get only `read`, `grep`, `find`, `ls` | The diagnoser uses the existing read-only session mode. It cannot run commands; the runner gives it the two retained failure outputs. |
| `execution_history` rows, `store.history`, `review_dispatch` reservations; `_review_check_evidence` writes private output files | Stage evidence uses `execution_history` rows with new kinds. No new table unless the detailed how proves a need. |
| Review range is `review_base..HEAD` (`_review_attribution`) | Final review covers implementation and run-and-fix commits cumulatively without a range change. Fix checkpoints need attribution. |
| `tracing.py` `boundary()`: closed phase set `{ready, worker, wait, checks, checkpoint, review, repair, join}`; other names become `ready` | Tracing enumerates phases, so requirement 11 applies: add one stage phase name. |
| `cli.py` `status` full JSON: `history` lists all rows (safe keys only); `review_authorization.next_stage` lists review sub-stages only | New history kinds appear in `history` without change. No new status field is required (choice C8). |
| `graph_recovery_action('refresh-review-target')` jumps to `review_route` when all tasks are complete | This path must not skip an unfinished acceptance stage. |
| `_run_graph` `recursion_limit = max(100, tasks*20+50)` | Stage iterations must fit inside the graph step limit, or the limit must include the stage bound. |

### Dependency research (reuse decision)

No new external dependency. Reuse decision: LangGraph `StateGraph` with the SQLite saver
(`langgraph==1.2.21`, `langgraph-checkpoint-sqlite==3.1.3`, `runtime/requirements.lock`) is
already in repository use for the same purpose (conditional edges, `durability='sync'`,
retained-thread resume) in `graph.py` `task_graph` and `_add_review_nodes`. The stage adds
nodes of the same kind. This is a repository-derived decision, not new library use, so new
internet research is skipped. Validation: the resume acceptance test (A-RESUME) exercises the
real saver with an interrupted stage iteration.

## Acceptance criteria (observable)

Each criterion names the smallest check. Runner tests use the existing offline fake adapters
and temporary Git fixture projects in `runtime/tests/` (for example `support.py`). They prove
runner logic, not live model behavior.

### Planning side

- **P1 — declaration.** `tiny-spec` and the planner Standard path tell the source producer to
  write an "Acceptance scenarios" section (each scenario: id, command, environment, written
  pass/fail criteria, allowed effects, oracle paths) or "No acceptance scenarios" with a reason.
  Check: planner/skill contract tests (`scripts/test-planner-workflow.py`,
  `scripts/check-planner-workflow.py`) assert the instruction text.
- **P2 — review of the choice.** `spec-review.md` tells the independent specification reviewer
  to check the ON/OFF choice and that each scenario is a command with criteria and allowed
  effects. Check: same contract tests.
- **P3 — approval brief line.** The planner approval brief shows exactly one line
  "Run-and-fix stage: ON (n scenarios) / OFF (reason)": TinySpec combined approval; Standard
  specification approval and final approval. Check: same contract tests.
- **P4 — executable handoff.** `task-generation` carries declared scenarios unchanged into the
  executable task file's optional top-level block, and writes no block for "No acceptance
  scenarios". Check: contract test plus a fixture task file.
- **P5 — planning-time shape check** (if choice C5 is accepted): `check-task-order.py` reports
  a malformed scenario block with an actionable message. Check: validator test.

### Runner

- **A-SKIP — no scenarios, exactly as today.** A contract without the block runs tasks and
  review with the same node sequence and history kinds as today. Check: runner test that
  compares the node path and history kinds with and without the change; existing runtime
  tests pass unchanged.
- **A-E2E — full loop.** Fixture project: scenario fails → confirmation rerun fails →
  diagnoser classifies "implementation defect" → fixer changes code → runner checks and makes
  a focused commit → scenario rerun passes → final review prompt contains the stage evidence
  (both failure outputs, diagnosis, fix commit SHA) and the review range includes the fix
  commit. Check: one runner test.
- **A-POSITION.** The stage starts only after all task checkpoints and before the first review
  dispatch; `refresh-review-target` cannot skip an unfinished stage. Check: runner test.
- **A-FLAKY.** A failure that passes on the one confirmation rerun is classified
  environment/flaky, is not sent to the diagnoser or fixer, and does not count as a pass. The
  result follows choice C1. Check: runner test.
- **A-READONLY.** The diagnoser runs in the existing read-only session mode and returns a
  hypothesis, evidence and one classification from the fixed set. A missing or invalid
  classification stops the stage for the owner and sends nothing to the fixer. Check: runner
  test with a fake adapter that asserts `read_only=True` and an invalid-output case.
- **A-FIXGATE.** Only "implementation defect" dispatches the fixer. Check: covered by the
  stop-path tests below.
- **A-ORACLE.** A fixer edit to an oracle path (scenario scripts and fixtures named in the
  block, plus the task file) is rejected at the write boundary or before the checkpoint; no
  commit contains it; the stage stops with an actionable message and preserves the bytes.
  Check: runner test.
- **A-ORACLE-ESC.** Classification "oracle defect" stops and escalates to the owner; no fix.
  Check: runner test.
- **A-SPEC-ESC.** Classification "spec gap / scope" stops and escalates to the owner; no fix.
  A fixer that reports scope growth or a paid/live/destructive need also stops. Check: runner test.
- **A-CAP.** The stage stops at the bound (choice C2) and does not dispatch another fix.
  Check: runner test.
- **A-NOPROGRESS.** After a fix, the same failure signature (choice C3) stops the stage.
  Check: runner test.
- **A-SAFETY.** A scenario with declared live, production-write, paid or destructive effects
  runs only after its existing manual gate is answered "yes"; stage approval alone grants no
  such authority. Default effects are isolated/local. Check: runner test with a gate question.
- **A-EVIDENCE.** Each iteration's failure output (first run and rerun), diagnosis and fix
  result are retained in run history; raw output stays private (not in `status` projections);
  each fix is a focused commit under the task-commit contract with attribution in the review
  brief. Check: runner test that reads history and the review prompt.
- **A-RESUME.** A run interrupted during a stage iteration resumes from retained state; an
  uncertain run, diagnosis or fix invocation is never replayed and stops with the existing
  "inspect before replay" style of diagnostic. Check: runner test with the real SQLite saver.
- **A-AUTHORITY.** Diagnoser and fixer prompts include the current-authority text and, for the
  fixer, `_ROUTINE_AUTHORITY` and `_DECISION_CONSTRAINTS` (ADR-0003, ADR-0004). Check: prompt
  test in the style of `runtime/tests/test_worker_authority.py`.
- **A-QUIET.** Routine stage iterations write no parent-turn event; only questions and
  terminal completion do. Check: runner test or inspection of the existing notification path.
- **A-VISIBLE.** Stage boundaries trace under one new phase name; stage history kinds appear in
  full `status` `history`. Check: tracing unit test and status test.
- **A-REGRESSION.** Existing checks pass: `runtime/tests/` (pytest),
  `skills/coordinate-implementation/scripts/test_*_contract.py`, `scripts/test-planner-workflow.py`,
  `scripts/check-planner-workflow.py`, `scripts/check-skills-lint.sh`. Report any check that is
  not run.

### Docs/ADR obligations

- New ADR (planned deliverable, not written in this stage): record the stage decision
  (command-only oracle, ON/OFF protocol, read-only diagnoser, oracle protection, bound and
  no-progress rule). Add it to `docs/decisions/index.md`.
- Update the operating guide and schema documentation for the scenario block, stage behavior,
  stop paths and resume.
- Update `docs/plans/index.md` with the task artifacts when they exist.

## Risks and early-risk reduction

- **Hardest core:** adding stage nodes to the retained LangGraph thread without replay on
  resume. The same pattern exists and is tested (`_add_review_nodes`, worker dispatch
  reservations). Proof selection: permanent tests of the actual helpers (A-RESUME, A-E2E); no
  disposable prototype, because the behavior is known and bounded and the test oracle is
  cheap. Expected finding: existing `execution_history` rows and reservation style are
  sufficient (UNVERIFIED until the detailed how).
- **Fixer and the review chain:** `run_fix` writes `execution_review_executions` rows. If the
  acceptance fixer reuses it directly, review routing can misread the chain. The detailed how
  must reuse the focused-commit pattern without review-chain rows; A-E2E and A-SKIP detect a
  break.
- **Read-only diagnoser cannot run commands.** It depends on the two retained outputs. Limit:
  some failures can be unclassifiable; those stop (A-READONLY). The fixer may observe the
  runtime per `scientific-method-debugging` inside its normal authority.
- **Scenario side effects are not sandboxed.** The runner runs the command in the project
  checkout. Safety comes from declared effects, specification review and existing gates. A
  scenario that writes files in the checkout can mix with fix bytes; the detailed how must
  define how such outputs are kept out of fix commits (for example the existing
  `generated_outputs` handling).
- **Graph step limit.** Stage iterations consume graph steps; the limit formula must cover the
  bound (A-CAP test exercises the maximum).
- **Continuation after a terminal stop.** The retained contract cannot change in a run. After
  an oracle defect or spec gap, the owner corrects through planning and starts a new run (it
  can set `review_base` to keep the cumulative review range). A run with an empty task list
  launches nothing today; this source does not change that.

## Open choices (deferred to this source; recommendation for the parent)

- **C1 — result of a non-repeating (flaky) failure.**
  (A) Terminal stop with report. Simple; continuation needs a new run with at least one task.
  (B) **Recommended:** ask the owner through the existing question channel (graph interrupt,
  as manual gates do): "Rerun the stage (counts toward the bound)" or "Stop". Never a pass
  without that answer. Low friction and uses existing resume semantics.
  (C) Automatic extra rerun and pass on success. Rejected: it counts a flaky result as pass.
- **C2 — form and default of the bound.**
  (A) **Recommended:** a fix-iteration count only, default **3** per stage run, optional plan
  override in the scenario block. Each flaky rerun accepted under C1 also counts. Basis: the
  owner requires a bound; a count reuses no new subsystem.
  (B) First fix automatic, later fixes need an owner grant (like the `owner-pair-v1` review
  policy). More owner questions.
  (C) Token/cost budget. Rejected for now: no existing enforcement; spending ceilings are out of
  scope by default (parsimony).
- **C3 — no-progress detection.**
  (A) **Recommended:** after a fix, the same scenario fails again with the same exit code and
  identical captured output (reuse of the existing `checks` "remains unchanged after scoped
  correction" rule). Deterministic. Output with timestamps defeats it; the C2 bound is then the
  backstop.
  (B) Same scenario and exit code only. Stops some real progress (a different failure in the
  same scenario).
  (C) The diagnoser reports "same cause as before". Agent judgment; not deterministic.
- **C4 — executors.** **Recommended:** the diagnoser and fixer use the existing `reviewer`
  executor (fresh sessions; the fixer is not a continuation of the diagnoser, to keep them
  separate). Alternative: the task worker executor for the fixer. No new executor key either way.
- **C5 — where the scenario block shape is checked.** **Recommended:** at the stage boundary in
  the runner (consumer, actionable stop) plus the planning-time `check-task-order.py` report.
  Not in runner intake (owner mandate). Limit: a malformed block that skips planning tools is
  found only when the stage starts.
- **C6 — scenarios after a final-review repair.** **Recommended:** exclude now; record as a
  limit and a possible follow-up issue. Alternative: add scenario commands to the review
  fixer's required checks (changes the existing review loop).
- **C7 — Standard SpecKit templates.** **Recommended:** no template change; the planner and
  `spec-review.md` instructions apply to Standard sources. Alternative: add a section pointer
  to `.specify/templates/spec-template.md` (SpecKit-owned file).
- **C8 — status output.** **Recommended:** no new status field; history rows and the tracing
  phase are enough. Alternative: a compact `acceptance` summary in full `status` JSON.

## Remaining blockers

- Owner design agreement on the [design page](acceptance-run-fix-design.html) and answers or a
  bounded deferral for C1–C3 (material); C4–C8 are routine unless the owner wants to decide.
- Detailed how (stage 2) is not written.
