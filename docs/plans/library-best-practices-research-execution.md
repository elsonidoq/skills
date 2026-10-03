# Library best-practices research — execution

Producer: planner; depth: TinySpec. Approved source/tasks and content hashes are in `reviews/library-best-practices-research-review.md`. Owner approved implementation with “Make sure there are no regressions in the skill behavior.” Later selections: GPT-6.1 Sol for implementation and a fresh independent final review; local task commits explicitly allowed, no push. These answer the task document's reserved model/commit permissions.

## Preflight and strategy

Seven bounded sonnet-class tasks require delegated sequential execution. Binding: `openai-codex/gpt-6.1-sol`, verified available in registry and successful preparation runs; `delegate` has read/bash/edit/write, successful edit/write route exists in parent, worker has declared edit/write. Question tool usable; fresh reviewer discovered with read-only tools and same model available. Async doctor reports available support, unlimited session budget, fan-out limit 64. Actual launch remains authoritative capability evidence.

Workspace: `/home/dev/projects/skills`, branch `main`, initial implementation base `f59ed226194da789c245f5983a618c0cf13a1486`. Only this task's planning artifacts are untracked; no unrelated changes observed. Single writer in existing checkout; no competing writes/isolation requirement. No declared memory adoption. No Standard/SpecKit prerequisite for implementing this TinySpec-origin skill change.

Context capacity metrics are unavailable; use two fresh bounded batches (T001–T004 and T005–T007), not forced retained-session reuse. Dependency order is unchanged; each producer is verified before its consumer. One final fresh independent review after all task commits.

## Execution graph

| Batch | Tasks | Scope | Dependencies | Integration | Verification | Class / mode | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | T001–T004 | Shared reference and route hooks | Approved source/tasks | Planner, TinySpec, Standard helper | Clause/link review; existing gates/checks | sonnet-class / delegated GPT-6.1 Sol | completed |
| 2 | T005–T007 | Tests, documentation, acceptance | Verified Batch 1 | Checker, fixtures, indices | Existing/new regressions, lint, coordinator tests | sonnet-class / delegated GPT-6.1 Sol | completed |

- [x] Batch 1 — completed; T001–T004 verified and separately committed.
- [x] Batch 2 — completed; T005–T007 verified and separately committed.
- [x] Fresh final independent review — GPT-6.1 Sol reviewed `f59ed226..7e4c1d0` independently; no issues found, verdict ready with runtime-validation limits.

## Validation and evidence

Preparation baseline: task-order validator PASS; planner static checker PASS; 56 existing fixture tests PASS; diff whitespace PASS. No live research, model-obedience or genuine SpecKit behavior exercise is authorized by these results. Implementation must preserve execution hash/gates and existing tests; add evidence-backed negative/mutation/scenario coverage. No claim of absolute regression absence can be inferred from static tests.

### Batch 1 task evidence

- T001 verified: fail-before confirmed the shared reference absent; inline clause assertions
  pass-after cover all eight source clauses, durable schema, safe failure and simulated
  evidence → constraint → validation. Manual mapping: clauses 1–3 → Discover, trigger
  and reuse; 4–5 → Obtain sufficient evidence; 6–7 → Classify and translate;
  8/durable schema → Persist within verified authority; route/failure → persistence,
  Safe failure and return. No actual library claims or internet exercise.
  Packaging inspection: installer links whole skill directories (`scripts/install-links.py`);
  sibling links will resolve within the distributed suite, not a copied standalone skill.
  `git diff --check` PASS. Commit: `3a07e2e` (`feat: establish shared dependency research contract`).
- T002 verified: fail-before showed no shared link, bounded docs brief or early spec
  research. Pass-after operational-section assertions confirm resolving shared link,
  read-only preselection, research before consequential spec constraints, helper/direct
  Standard bounded documentation permission and both route reviews. Existing checker
  PASS and 56 tests PASS; `git diff --check` PASS. One intermediate mutation failure
  exposed duplicated `explicit owner deferral` text masking the original assertion;
  rephrased the new clause without weakening its semantics, then reran all 56 tests.
  Manual comparison: order, classes, owner gates, approvals/renewal and single-plan
  semantics preserved; no helper permissions presumed before T004 alignment.
  Commit: `5b786b5` (`feat: integrate dependency research into planner stages`).
- T003 verified: fail-before showed missing shared invocation and direct-entry authority
  checks. Pass-after assertions verify resolving sibling link, research section before
  compact approach, direct authority, reuse/refresh, precise failure and traceability.
  Checker PASS; 56 tests PASS; `git diff --check` PASS. Manual boundary comparison:
  separate tasks/direct adapter, no SpecKit and no standalone source approval unchanged.
  Simulated walkthrough (not model/library output): managed TinySpec receives findings
  and bounded writes from T002; direct TinySpec verifies equivalent selection and write
  authority itself. In either route, simulated version-specific “Lifecycle” support →
  compact constraint “await queued work before close” → acceptance “pending work completes
  before close event”; source links the discovered canonical owner. Adequate applicable
  local guidance needs no new search; targeted refresh preserves other sections; inadequate
  evidence returns the affected shutdown decision, missing supporting span/version and
  validation needs. No mandatory research artifact chain introduced.
  Commit: `f21ea5b` (`feat: apply shared dependency research in TinySpec`).
- T004 verified: fail-before showed missing shared contract and no bounded docs exception
  alongside the SpecKit-only boundary. Pass-after operational assertions verify resolving
  link, standalone pre-design research, exact failure, bounded extra documentation writes,
  renewed specification approval and retained single creation. Manual before/after review:
  explicit destination/change/prohibition permission now aligns with T002; absence stops,
  no arbitrary docs/code authority; approved spec, genuine SpecKit, fixed adapter class,
  owner stops and standalone fallback remain, and fallback cannot bypass research.
  Simulated Standard/helper/standalone walkthrough: classify version-specific supporting
  span, derive a plan constraint and observable check, persist under explicit owner/index
  bounds before readiness; unavailable evidence returns affected decisions, not a ruling.
  Checker PASS; 56 tests PASS; lint PASS (22 skills, plus existing suites of 135/4/2/7/3/6
  tests); task-order validator PASS; `git diff --check` PASS. Installed packaging inspected
  read-only via `scripts/install.sh`/`install-links.py`: actual `~/.agents/skills` symlinks
  for all three consumers resolve this checkout's shared reference. No installation run.
  Commit: `55a56a3` (`feat: align Standard research and bounded documentation authority`).

Batch 1 final reconciliation: source/task digests remain exactly approval-bound; only
three skills, the new shared reference and this tracker changed from preparation commit
`27dee6f`. No source/task/approval/test mutations. Existing approval/recovery and SDD
contracts inspected; gate/class/one-plan checks and execution freeze PASS. No unresolved
blockers. T005 focused regression coverage, T006 discovery docs, T007 full acceptance and
fresh independent review remain outstanding. Static/semantic review is not model obedience
or real research quality proof; live research/model/real-SpecKit exercises NOT RUN.
Run `/reload` inside pi after global skill changes.

### Batch 2 task evidence

- Preflight: inspected all five Batch 1 commits and their actual files; clean workspace,
  `main`, source/task hashes match approval. Baseline checker PASS; original 56 tests PASS.
  No skill integration defect found; no skill writes required in this batch.
- T005 verified: new tests failed before checker implementation (65 tests, 36 named
  failures), including carrier/link, removed clauses, unsafe permissions and stage order.
  After implementation and expanded coverage: checker PASS; 68 tests PASS (all original
  56 preserved). `DependencyResearchTests` adds 12 tests: 36 individual clause-removal
  subcases assert specific diagnostics; whole carrier/stage deletion retains summary
  mentions but fails; missing/wrong packaged links, post-design placement and contradictory
  permissions fail. Required shared carrier and actual relative link owner checked;
  isolated whole-directory symlink packaging resolves all consumers without installation.
  Simulated indexing trace and reuse/skip/version-refresh/failure/deferral walkthroughs
  assert carrier obligations and illustrative evidence→constraint→check correspondence,
  not agent execution or research quality. No new policy engine/fixture workflow.
  Execution hash freeze unchanged; `git diff --check` PASS. Verified changes committed as
  `test: protect shared dependency research obligations` (T005), commit `51485d7`.
- T006 verified: fail-before discovery assertion reported absent Dependency Research
  index link. Pass-after inline Python check resolves all local index/regression links,
  confirms every documented named test exists and the no-memory declaration is preserved.
  Added only shared/source/task/execution discovery and focused regression guidance;
  manual comparison with operational carriers/tests confirms both routes and standalone,
  repository-first reuse/refresh, discovered durable ownership, safe failure, timing and
  bounded Standard writes. Illustrative static walkthroughs versus semantic supporting-span
  review versus NOT RUN authorized behavioral evidence are distinct. Checker PASS;
  68 tests PASS; `git diff --check` PASS. Verified changes committed as
  `docs: expose dependency research and assurance limits` (T006), commit `e588bc6`.
- T007 verified: fail-before packet assertion reported missing R1–R6 reconciliation.
  Pass-after reconciliation below checked against actual clauses, named test results,
  links and attributable full-range diffs. No introduced integration defect or excluded
  surface found. Verified evidence committed as `docs: reconcile dependency research
  integration evidence` (T007); this completes implementation tasks, not independent
  review or final feature acceptance.

### R1–R6 integration reconciliation

| Criterion | Carrying sections and positive/rejection evidence | Result / limit |
| --- | --- | --- |
| R1 routes/direct/standalone | Planner TinySpec source, Standard `spec_create`/`plan_create`/`overall_review`; TinySpec dependency evidence; helper Preflight/adapter. Simulated indexing route/entry assertions; missing invocation, standalone clause, stage deletion and after-design mutations | PASS static/manual; no actual model or SpecKit production |
| R2 proportional reuse/refresh | Shared Discover/Obtain, all consumer preflights. Simulated reuse/skip/version-refresh assertions; repository-first, skip, targeted-refresh, local-evidence and source hierarchy clause removals | PASS static/manual; no real version research |
| R3 durable provenance/traceability | Shared Classify/Persist; TinySpec compact source; helper Boundary/Completion; planner selected-production review. Classification/version/source/owner/schema/traceability removals reject; index links resolve | PASS static/manual simulated correspondence; no real research output |
| R4 safe failure/bounded authority | Shared Safe failure/Persist, planner plan brief, helper Preflight/Boundary/adapter. Unsupported-source, fallback, exact-gap, bounded permission and arbitrary-write rejection; illustrative bounded deferral assertions | PASS static/manual; no actual unavailable-tool behavior exercise |
| R5 selected-only persistence/gates | Planner Before selection/selected stages, shared Persist, TinySpec direct authority, helper approved-spec/renewal rules. No-persistence and permission mutations; original approval/class/one-plan checks and coordinator freeze unchanged | PASS static/manual; actual write timing outside these local edits NOT RUN |
| R6 regression integrity | Required shared carrier/link loader; 12 research tests plus all original 56; regression guide limitations and whole-stage/summary masking tests | PASS deterministic; independent review ready with runtime-validation limits |

Manual supporting-span walkthrough: the explicitly simulated shared “Lifecycle” span
requires queued work completion before close; simulated local shutdown races a queue.
The recommendation is distinct from the derived shutdown ordering constraint; the
observable check tests completion before the close event. The wait-time assumption
has a separate validation check, not a documented guarantee. The test's fictional v2
URL is labelled simulated and unresolvable by design; it is not internet evidence.
No universal batching/flush claim is inferred. For actual use, canonical guidance must
hold version, primary supporting claims/date and uncertainty, be discovered through the
repository owner/index, and receive only deficient-section refresh; the source/plan links
that owner and carries the constraint/check. Both Standard brief modes and helper boundary
agree on explicit destinations/changes/prohibitions in addition to SpecKit artifacts.

Final commands/results (all local; Python invocations use `PYTHONDONTWRITEBYTECODE=1`):

- `python3 scripts/check-planner-workflow.py`: PASS.
- `python3 scripts/test-planner-workflow.py -v`: PASS, 68 tests; named research positives/rejections.
- `bash scripts/check-skills-lint.sh`: PASS, 22 skills, 0 failures; planner 68 and focused
  suites 135/4/2/7/3/6 tests PASS. No introduced lint failure or warning to ignore.
- `python3 skills/task-generation/scripts/check-task-order.py docs/plans/library-best-practices-research-tasks.md`: PASS.
- `python3 skills/coordinate-implementation/scripts/test_intake_contract.py`: PASS, 6 tests.
- `python3 skills/coordinate-implementation/scripts/test_batching_contract.py`: PASS, 3 tests.
- Inline Python index/regression link and named-test check: PASS; packet reconciliation assertions PASS.
- `git diff --check` and full-range whitespace check from `f59ed226`: PASS.
- Full-range diff/name inspection, clean/staged inventory and `sha256sum` of source/tasks:
  PASS, approval-bound digests unchanged. Since preparation `27dee6f`, only authorized
  three skills/shared reference, two scripts, index/regression docs and tracker differ.
  Batch 2 changes only its five allowed existing files; original tests and execution SHA
  remain unchanged. No untracked/staged unrelated work, installation, push or deployment.

Residual limits: phrase-based checker sensitivity is not semantic completeness, natural-language
obedience, real source quality/applicability or actual filesystem preservation proof. Semantic
walkthroughs here are simulated, not agent-produced plans. Live research/model/real-SpecKit and
baseline/candidate behavioral runs NOT RUN; no dependency integration was designed. Fresh
independent review completed with no findings; coordinator accepts the instruction/check/documentation
change based on that review and rerun local gates, not demonstrated runtime obedience.
Parent reran the checker, 68 planner tests, complete skill lint (22 skills, zero failures and
all focused suites), and full committed-range whitespace checks: PASS. Working tree was clean.
Fresh reviewer inspected the full committed patch and current/baseline carrying files; its
read-only tool set did not run test commands. No review fixes were required. Implementation
T001–T007 is complete, with no pending dependency-ready work or owner gate. Runtime behavioral
acceptance remains NOT RUN as described above. Run `/reload` inside pi after the global skill changes.

Per-task verified commits are delegated. Parent separately commits these approved preparation records. Do not change approved source/task contracts; task status/evidence updates only under existing approval contract. No push, deploy, paid/live research or external publication.
