# Requirements Manager execution tracker

## Authorization and baseline

Owner authorized direct bootstrap implementation after critique/fix and task review; see task artifact revision 3. Current source/task definitions and durable review records are committed in the preparation commit immediately preceding T001. Pre-change protection revision: `fa41d5f3f5aeb7ddfa9963222eff2c0447533059`. The complete implementation review range begins at that preparation commit and ends at the T010 commit (not a working-tree diff).

Models: sonnet-class implementation = openai-codex/gpt-5.6-terra; opus-class implementation = openai-codex/gpt-6.1-sol; independent fresh reviewer = openai-codex/gpt-6.1-sol. Chosen by owner. Runtime preflight observed delegate edit/write/bash and reviewer read-only capabilities; git identity and commit capability are available.

No suite project-memory contract/store is declared in this configuration repository's AGENTS.md; do not fabricate one. Preserve existing project instructions. No SpecKit is required for this explicit direct bootstrap.

More than three implementation tasks require delegation. Use sequential consecutive class/stage batches, with fresh bounded handoffs where surfaces change or context metrics are unavailable. No hard one-session-per-class cap. Commit each task after actual checks and before next task; no per-task reviews. One fresh independent final review. Only one batch in_progress. On a verified blocker, leave dependents pending and report missing decision/capability; no blind retry.

## Batches

| Batch | Task IDs | Scope | Dependencies | Integration surface | Verification | Class | Status |
|---|---|---|---|---|---|---|---|
| 1 | T001 | Source-derived coverage baseline | none | coverage/index | citations, diff/lint | sonnet-class | in_progress |
| 2 | T002–T003 | Shared primitives and validator | T001 | shared skills/tests + observed pointers | focused tests, validator/lint | sonnet-class | pending (T001) |
| 3 | T004 | Restore EPIC | T001–T003 | EPIC instructions/shared invocations | inventory, stage contracts/lint | sonnet-class | pending (T001–T003) |
| 4 | T005 | Coordinator | T003–T004 | origin gates + shared execution | intake/threshold/commit/context checks | opus-class | pending (T003–T004) |
| 5 | T006 | Requirements Manager | T002–T005 | direct producer/handoff | source/tasks/review/capability checks | sonnet-class | pending (T002–T005) |
| 6 | T007 | Routing/docs/discovery | T001, T004–T006 | docs + affected entry points/probe | lint, links, no-model discovery | sonnet-class | pending (T001, T004–T006) |
| 7 | T008–T009 | Contract and mutation suite | T004–T006 | routine validation/tests | positive + named negative tests | sonnet-class | pending (T004–T006) |
| 8 | T010 | Integration evidence | T001, T007–T009 | coverage + introduced integration seams | full static suite/walkthroughs | sonnet-class | pending (T001, T007–T009) |
| 9 | T011 | Independent final semantic review | T010 | complete committed diff + source inventory | findings/dispositions/coverage | opus-class (fresh reviewer) | pending (T010) |

## Baseline verification

Before dispatch: existing validator units PASS (5 tests), current task order PASS, suite lint PASS (21 skills), git diff --check PASS. New workflow/mutation tests do not yet exist; missing behavior is documented in plan/history rather than claimed tested.

## Task evidence and commits

Delegates append each task's changed files, actual checks/outcomes, scope/context limitations and commit evidence here, update the task checkbox, and commit the task changes. Do not alter approved task definitions. No install, paid probe, provider/configuration changes, product work, push, or deployment.

## Final review

Pending. T010 prepares accessible complete committed patch and exact historical/pre-change files outside the repository for read-only reviewer tools. T011 reviewer returns its report; parent records dispositions and completion, commits review evidence, and handles confirmed scoped fixes. A clean working tree is not proof of feature acceptance or complete review.
