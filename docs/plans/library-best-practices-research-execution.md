# Library best-practices research — execution

Producer: planner; depth: TinySpec. Approved source/tasks and content hashes are in `reviews/library-best-practices-research-review.md`. Owner approved implementation with “Make sure there are no regressions in the skill behavior.” Later selections: GPT-6.1 Sol for implementation and a fresh independent final review; local task commits explicitly allowed, no push. These answer the task document's reserved model/commit permissions.

## Preflight and strategy

Seven bounded sonnet-class tasks require delegated sequential execution. Binding: `openai-codex/gpt-6.1-sol`, verified available in registry and successful preparation runs; `delegate` has read/bash/edit/write, successful edit/write route exists in parent, worker has declared edit/write. Question tool usable; fresh reviewer discovered with read-only tools and same model available. Async doctor reports available support, unlimited session budget, fan-out limit 64. Actual launch remains authoritative capability evidence.

Workspace: `/home/dev/projects/skills`, branch `main`, initial implementation base `f59ed226194da789c245f5983a618c0cf13a1486`. Only this task's planning artifacts are untracked; no unrelated changes observed. Single writer in existing checkout; no competing writes/isolation requirement. No declared memory adoption. No Standard/SpecKit prerequisite for implementing this TinySpec-origin skill change.

Context capacity metrics are unavailable; use two fresh bounded batches (T001–T004 and T005–T007), not forced retained-session reuse. Dependency order is unchanged; each producer is verified before its consumer. One final fresh independent review after all task commits.

## Execution graph

| Batch | Tasks | Scope | Dependencies | Integration | Verification | Class / mode | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | T001–T004 | Shared reference and route hooks | Approved source/tasks | Planner, TinySpec, Standard helper | Clause/link review; existing gates/checks | sonnet-class / delegated GPT-6.1 Sol | in_progress |
| 2 | T005–T007 | Tests, documentation, acceptance | Batch 1 | Checker, fixtures, indices | Existing/new regressions, lint, coordinator tests | sonnet-class / delegated GPT-6.1 Sol | pending |

- [ ] Batch 1 — in_progress; T001–T002 verified, remaining consumers pending.
- [ ] Batch 2 — pending; blocked on verified Batch 1.
- [ ] Fresh final independent review — pending all task commits.

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
  Commit subject: `feat: integrate dependency research into planner stages`.

Per-task verified commits are delegated. Parent separately commits these approved preparation records. Do not change approved source/task contracts; task status/evidence updates only under existing approval contract. No push, deploy, paid/live research or external publication.
