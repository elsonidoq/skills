# Active planning routing — bounded implementation validation

Status: T001/T002 verified; T003 static/manual validation complete, **fresh independent final
semantic review pending coordinator action**. This is implementer evidence, not final feature acceptance.
Source: [approved TinySpec](../active-planning-routing-tinyspec.md), SHA-256
`1f44d5b3dfe4fdddcd4a0445ab85ec8700363b11465c13f19252a65c66423c5a`;
[tasks](../active-planning-routing-tasks.md), SHA-256
`0acca7d33e004631137a0ec744f9b065e832b4fb7b0bf066746e6acc42cd586e`.
[Owner approval](active-planning-routing-planning-review.md) binds those unchanged contents.

## Provenance and review boundary

Implementation baseline: main `91d560de5d00d7f22a57b49f4a0e0c67a83eea97`.
T001 instructions/tests: `f9330400adaf668b0ead6089deaf6affefc915b5`;
T001 evidence: `eae54d671f09f52304b8f1092b710f11b1a43207`.
T002 docs: `0fd2c67499e94827173bf672e3d3d98f52519163`;
T002 evidence: `c4d13740194c26c90727b792d85867cde10ff77a` (T003 baseline).
T003 artifact/discovery and separate evidence checkpoints follow; their exact SHAs and final
review range are returned in the worker handoff. Review **baseline..final HEAD**, not a clean-tree diff;
the substantive code/doc producer range is already baseline..`0fd2c67499e94827173bf672e3d3d98f52519163`.
The [existing run summary](../../../memory/coordination/evidence/2026-10-06-active-planning-routing/SUMMARY.md)
owns task/evidence outcomes and pending review disposition; no new coordination evidence store/file.

Requested/selected worker: `openai-codex/gpt-6.1-sol:medium` (parent preflight evidence).
Observed worker actual model/effort: **unknown**; selection is not execution attestation.
Approved project guidance/gotchas: none. Live/provider/model-obedience checks: **NOT RUN**;
no network, installation, settings/runtime/package change, delegation, benchmark, push or deploy.

## T003/V1: bounded manual instruction walkthroughs

All results below are **manual/simulated instruction PASS**, not runtime dispatch or LIVE PASS.
Bindings/support in positive cases are hypothetical verified inputs, not claims about providers.
The inspection asks which instruction controls the consumer and whether an unsafe continuation
has authority; static mutation tests additionally check those carriers, not agent obedience.

| Scenario / inputs | Applicable operational sections | Expected selection or stop; protected gate | Manual result |
| --- | --- | --- | --- |
| TinySpec source/tasks: current owner TinySpec choice, bounded preparation authority; hypothetical supported owner-selected Luna/medium | Planner Shared routing selection, Before selection, TinySpec Source creation/Tasks/Review; task-generation Preconditions and adapters | Six factors assessed for each invocation; family and effort separately justified; exact Luna/medium reaches source/tasks, no Standard Sol prerequisite. Separate source/tasks and combined current-content approval retained; no intermediate TinySpec approval/SpecKit requirement | PASS: no fixed class or implementation quota controls production |
| Standard direct: current approved specification, detected usable SpecKit, permitted callable Sol binding with medium support, bounded writes | Planner Standard preflight and plan_create; Shared routing selection; approval/recovery Transition table | Exact Sol/medium for same-session spec review/fix → one plan → produced-plan review/fix. No helper means direct pass only. Any approved specification change renews spec approval before leaving stage; tasks remain create-only; independent overall review/final approval retained | PASS: entire-pass profile and stage ownership explicit |
| Standard helper: same valid inputs, manager invokes architectural helper for entire pass | Planner plan_create; helper Planner Standard adapter contract, Preflight, Planner Boundary | Manager's exact selected Sol/medium copied unchanged to brief/dispatch; one full pass returned for inspection, not another plan. Standalone local/separate-review selection cannot bypass manager; documentation writes need separately bounded authority | PASS: manager precedence and no duplicate creation retained |
| Non-plan owner-selected supported profile: hypothetical Standard specification/tasks or independent reviewer Terra/low; separate independently authorized standalone helper with same supported selection | Planner Shared routing selection and relevant stage; helper standalone Preflight | Existing six factors justify Terra family and low effort independently, permissions/support verified, exact selection reaches consumer; no automatic stage-family mapping. Proposed/selected/observed distinct, observations unknown if unobservable. Reviewer independence and standalone prerequisites remain | PASS: Standard plan exception does not leak into other selections |
| Sol/medium unavailable or unsupported: no permitted callable Sol binding, or binding lacks medium; other profile available | Planner plan_create; helper adapter; shared seed Applicability | Stop with precise binding/support gap; no other family/effort/default/local helper fallback. Missing owner selection/support elsewhere also stops affected invocation, not guessed selection | PASS: no alternative dispatch authorized |
| Settings/default mismatch: owner selected exact profile but effective agent default differs | Planner Shared routing selection/plan_create; brainstorming Capability preflight; helper Preflight/adapter; settings sample | Assignment/dispatch checks block mismatch; selected profile unchanged. Neither illustrative Claude ID nor registry/suffix establishes owner selection, callable support or observed execution | PASS: no silent override; observations stay unknown |
| Denied/stale approval or missing write authority: denied depth/artifact gate, changed approved spec/tasks, or required research-document permission absent | Planner Before selection, Standard stages, Approval/resume; approval/recovery Transition table; helper Preflight/Boundary | Denial grants no affected production; stale content returns earliest invalid gate and renews approval; missing bounded permission stops required write/design branch. Model availability never creates permission | PASS: owner/current-content/write gates preserved |

D4 baseline comparison is the bounded protected-section table in the run summary (T001/V3).
Orchestrator-owned dialogue, proportional research, preselection read-only exceptions, one entire
helper pass, create-only Standard tasks, per-task checkpoints, inspected-failure safety and fresh
independent final implementation review remain. No task-generation implementation profile assignments
or new per-task review/approval gates were added.

## T003/V2: commands and concrete outputs

All Python invocations and lint used `PYTHONDONTWRITEBYTECODE=1`; Python 3.12.3.

| Command/check | Actual result |
| --- | --- |
| `python3 scripts/check-planner-workflow.py` | PASS static production instructions (T001/T002 and lint) |
| `python3 scripts/test-planner-workflow.py` | PASS 87 tests, baseline 80; 7 added `ActivePlanningRoutingTests`, 46 consumer-scoped mutation/link cases |
| `python3 skills/planning-brainstorming/scripts/test_contract.py` | PASS 4 |
| `python3 skills/task-generation/scripts/test_contract.py` | PASS 4; no task-generation operational edit |
| `python3 skills/memory-handling/scripts/test_coordination_contract.py` | PASS 21 at T001 and T003; persistence semantics unchanged |
| `bash scripts/check-skills-lint.sh` | PASS 22 skills, 0 failed; planner and task-commit static checkers PASS; embedded suites 87 planner, 135 initialization, 4 brainstorming, 4 task-generation, 7 task-order, 25 batching, 9 intake, 12 task-commit = 283 tests |
| `git diff --check` | PASS per task, including T003 artifact; no whitespace errors |
| Scoped local Markdown link resolution / active-label inventory | PASS 66 links in T002 docs; zero obsolete class labels in three active skills/scoped normative docs; T003 report/discovery links checked before commit |
| Path-limited commit/index/status and protected fixture audits | PASS: only approved surfaces; historical initialization `source-contract.json` byte-identical to baseline; approved digests unchanged; no staged/task-owned residual files |

Pre-change exact Sol/medium assertion: expected FAIL (missing policy), then identical post-change
assertion PASS. Mutation diagnostics: restored Sonnet/Opus labels → `obsolete-planning-class`;
changed Sol/medium, partial pass, missing stop, silent substitution/default → `plan-profile` /
`adapter-profile`; lost independent rationale/selection/observation → `planning-selection` /
`routing-brainstorm` / `routing-helper`; adapter bypass/duplicate creation → `adapter-profile`;
miswired brainstorming assessment/application → named routing consumer diagnostics; wrong shared
owner → `routing-reference`; planning batching prerequisite → `routing-applicability`.
Existing stage/order/approval/research/checkpoint/reviewer-removal checks retained.
Inspected intermediate test failures and targeted fixes are preserved in the run summary; no
failed check was attributed to model capability. Final required commands pass, not waived.

## T003/V3: acceptance/item reconciliation and reviewer packet

| Source criterion | Concrete evidence | Disposition |
| --- | --- | --- |
| A1 | T001/V1 mutations and T002/V2 scoped inventory; historical snapshot and rejection assertions preserved | PASS static/manual |
| A2 | T001/V1 exact family/effort/whole-pass/fallback mutations; direct/helper/unavailable walkthroughs; T002/V1 docs | PASS static/manual; callable support/obedience not live-verified |
| A3 | Three consumer-scoped wiring/selection/observed tests and single shared owner links; TinySpec/non-plan/mismatch walkthroughs | PASS static/manual |
| A4 | T001/V2 retained causal checks, T001/V3 baseline section table, no task-generation/coordinator operational edits, permission/approval walkthrough | PASS static/manual |
| A5 | Item-mapped command results/docs/links and honest simulation/live limits | PARTIAL: fresh independent final semantic review NOT VERIFIED, pending coordinator |

T001/V1–V4 and T002/V1–V3: **PASS**, detailed per-item evidence in the run summary.
T003/V1: **PASS manual/simulated**; T003/V2: **PASS static**;
T003/V3: reconciliation/reviewer packet **PASS**, coordinator-owned independent review
**NOT VERIFIED (pending)**; T003/V4: report/discovery validation **PASS**, focused task and separate
evidence commits recorded by worker handoff/summary. No feature-accepted verdict is implied.

Changed-path inventory for the final reviewer (all within approved ownership):
- T001: `skills/planner/SKILL.md`, `skills/planning-brainstorming/SKILL.md`,
  `skills/delegating-architectural-planning/SKILL.md`,
  `skills/coordinate-implementation/references/batch-routing.md`,
  `scripts/check-planner-workflow.py`, `scripts/test-planner-workflow.py`,
  `skills/planning-brainstorming/scripts/test_contract.py`,
  `skills/memory-handling/scripts/test_coordination_contract.py`.
- T002: `REQUIREMENTS.md`, `docs/index.md`, `docs/pi-settings-sample.md`,
  `.specify/memory/constitution.md` (only owner-reference phrase).
- T003: this validation artifact and `docs/plans/reviews/index.md`.
- Separate evidence checkpoints: existing run `SUMMARY.md` and `memory/coordination/evidence/INDEX.md`.

Coordinator must inspect the complete committed range and independent review for conflicting prose,
policy propagation, helper precedence, unsupported/substituted profiles, inherited implementation
prerequisites and weakened safeguards; tests alone do not certify semantic completeness. Any material
finding blocks completion; verified corrections checkpoint separately and affected evidence/review renews.
Disposable full-range patch and name-status exports are supplied in the worker handoff, not repo scratch.

## T003/V4: closeout limits

No live provider/runtime-obedience probes; **NOT RUN**, separately authorized only.
Unrelated untracked `.env` and `docs/plans/mandatory-task-commits.md` were neither read nor edited;
metadata and status remained unchanged. No historical migration or guideline change. Semantic prose
and real model behavior remain residual risks until independent review and any separately permitted
runtime validation. After global skill changes, run **`/reload` inside pi**.
