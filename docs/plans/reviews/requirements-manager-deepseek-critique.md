# DeepSeek critique-and-fix report — Requirements Manager task artifact

Stage: critique/fix of the TASK ARTIFACT only. No implementation, no delegation, no commit, no staging, no install,
no runtime configuration change. Only repository write: `docs/plans/requirements-manager-tasks.md`.

## Verdict

**Ready with stated follow-up for independent overall review.** The artifact now requires the three owner-critical
guarantees that were missing (source-derived coverage matrix + behavior inventory, operational-instruction-level
mutation checks, independent final semantic diff review). It does **not** carry owner implementation approval, and
I did not invent any. Remaining blockers for the owner: (1) independent overall review of this task artifact is
still outstanding; (2) T011's `opus-class` assignment is a critique-stage judgment flagged for the owner; (3)
T011 reviewer availability is unknown and may end as `UNAVAILABLE`.

Static evidence is honestly labelled: no test in this plan proves runtime model obedience.

## Artifacts

| Artifact | sha256 | note |
|---|---|---|
| `docs/plans/requirements-manager-tasks.md` (revision 2, delivered) | `fc5485b7226ed8bac1234808f99d532f8d6b2826f84cd583e2cd041ad3ab19c8` | git blob `04728426d571f92ac30142f982a4905ae20f3d33`; 305 lines; untracked |
| `docs/plans/requirements-manager-tasks.md` (revision 1, reviewed) | `35070a8b71ffb360a90d10d3c58e71fc276d40d9fd5b430ea4a2e456496cff69` | git blob `d8a7b549571ea7a6238f12cc8010efbbc0e7788f`; findings cite this revision |
| `docs/plans/requirements-manager.md` (design, unchanged) | `4393a641c34d5b3f2817b39c7eb0fa1b0581a9d7eb36ae3c1087c577bd7ee1e4` | git blob `11d7271ea944dc3b5e3c70e88ad7229522ffb257`; hash identical to pre-critique baseline |
| `docs/index.md` (unchanged) | — | pre-existing `+4` lines preserved (`git diff --stat` still 4 insertions) |

No staged files. `git status --short`: ` M docs/index.md`, `?? docs/plans/`.

## Method

Read completely: `AGENTS.md`, `REQUIREMENTS.md`, `docs/plans/requirements-manager.md`,
`docs/plans/requirements-manager-tasks.md`, `docs/best_practices_spec_driven_development.md`,
`docs/pi-settings-sample.md`, `README.md`, `docs/index.md`, `skills/epics-manager/SKILL.md`,
`skills/epics-manager/scripts/check-task-order.py`, `test_check_task_order.py`,
`skills/coordinate-implementation/SKILL.md`, `skills/create-epic/SKILL.md`, `skills/install-memory/SKILL.md`,
`skills/initialize-documentation/SKILL.md`, `skills/memory-handling/SKILL.md`, `scripts/check-skills-lint.sh`,
`scripts/probe-pi-load.sh`, `scripts/install.sh`, and the comparison sources
`skills/requesting-code-review/code-reviewer.md` / `skills/receiving-code-review/SKILL.md`.
Historical contract: `git show 32e12feb382a6a0acb7e9d7f2e82559e3d397f2e:skills/epics-manager/SKILL.md` (614 lines).
Removal confirmed via `git show --stat fdb91a5`. No full `epics-manager` run, no SpecKit stage, no model call.

## Findings (locations refer to revision 1 unless stated)

| ID | Severity | Location | Finding | Disposition |
|---|---|---|---|---|
| F1 | blocking | rev1 §Tasks (no such task); §Coverage checklist mapped design packages→tasks only | No durable **requirement-to-implementation/test matrix** derived from original request + historical EPIC + current protections. A shortened redesign could pass every check while dropping owner-scope behavior. | Fixed: new T002 produces `docs/plans/requirements-manager-coverage.md` with a mandated column set and a binding derivation rule (sources only; drafted before reading the new prompts); consumed by T004, T010, T011. |
| F2 | blocking | rev1 §Tasks T003/T005 | No **preserved/changed/removed behavior inventory**, so historical operational behavior (reading contract, flagged-item protocol, handoff context, resume recovery, `done` report, deferral scan) could vanish with the diagram still "correct". | Fixed: T002 inventory (each historical behavior marked with historical line evidence + current protection); T004 must honour each row; unaccounted removals must be flagged to the owner, not silently restored/deleted. |
| F3 | blocking | rev1 §Tasks T007/T008 acceptance | Mutations were satisfied by "removed/reordered required stages" without requiring the checker to resolve a stage to its **operational instruction body** — diagram-token matching could pass. | Fixed: T008 requires per-stage operational-section assertions (entry condition, inputs, outputs, class, gate/approval, resume); T009 adds mutations that delete the instruction body, class assignment, gate transition, create-only wording, capability stop text, and stale-approval wording while the diagram stays intact. |
| F4 | important | rev1 §Tasks T009 ("independent overall review is requested … when available") | No reviewer contract, inputs, classification, or disposition requirement; a self-review could satisfy it and could not detect silent stage deletion. | Fixed: new T011 (independent reviewer, required inputs incl. diff + original request + historical commit + current protections + matrix, per-row preserved/changed/removed/absent classification, severity findings with `file:line`, verdict, dispositions per `receiving-code-review`, `UNAVAILABLE` honesty). |
| F5 | important | rev1 §Tasks T007–T009 | Tests could be reported as proof that EPIC behavior was restored. | Fixed: artifact-level evidence-honesty rule; T008/T009 must state the prompt-contract limitation; T010 walkthroughs must be labelled static; T011 must state it assessed prompt/diff semantics only. |
| F6 | important | rev1 §Tasks T009 ("do not … commit, or authorize execution"); §Scope boundary | Read literally, could be taken as permanently forbidding owner-authorized implementation delegation/commits. | Fixed: new §Scope of the exclusions in this artifact; T010's limits are explicitly scoped to that task; the owner-approved single focused small-run commit before review, the review-fix commit, 15+ per-batch commits, and the T011 review delegation are preserved. |
| F7 | important | rev1 §Tasks T003 acceptance | Omitted design-mandated items: clarification optional/conditional, approvals as checkpoints rather than extra create/critique/fix stages, renewal of specification approval when `plan_create`/`overall_review` changes approved spec content, sizing/provenance admission verdict, documentation coverage, observed (not hard-coded) reviewer selection. | Fixed: all added to T004 acceptance. |
| F8 | important | rev1 §Tasks T001/T003/T005 (capability mentions only) | No inventory preserved the documented **capability checks and fallbacks** (SpecKit stage detection, mandatory delegation, question tool + prose fallback, model-class binding resolution, memory store, constitution, reviewer selection). | Fixed: T002 capability/fallback inventory with current `file:line` and unavailable-case behavior; T008 asserts presence + stop wording; T010 must report `UNAVAILABLE`, never `PASS`. |
| F9 | minor | rev1 §Tasks T005 acceptance | Omitted documentation scope derived from requirement + inspected changes (no plan), and sequencing defects returning to the producing workflow's review gate. | Fixed in T006 acceptance. |
| F10 | minor | rev1 §Tasks T006 acceptance | Omitted install/discovery explanation, `/reload` reminder, coverage-artifact index entry, README routing that admits owner-authorized direct task lists into the coordinator. | Fixed in T007 acceptance; T007 dependency on T002 added. |
| F11 | minor | rev1 §Task contract "Count and split" | Count/share statements stale after renumbering. | Fixed: 11 tasks, 9 `sonnet-class`, 2 `opus-class` = 18.2% (<30%, no exception). |
| F12 | minor | rev1 §Coverage checklist / §Review concerns | Referenced only old numbering; lacked matrix-completion and semantic-review rows. | Fixed. |
| F13 | minor | new T011 | `opus-class` for the independent review is my judgment, not an owner-settled class; reviewer binding is an owner selection at coordinator preflight. | **Flagged for owner**, not silently applied: rationale plus the `sonnet-class` alternative (share would drop to 1/11) recorded in T011. |
| F14 | important | rev1 §Tasks T003/T005 | No check that obsolete historical elements stay excluded (OpenCode command files/paths, provider/agent IDs, `resolve_epic.py`-style resolution, rigid JSON state schema). | Fixed: T008 negative assertions; T009 legacy-token reintroduction mutation; T011 review item. |
| F15 | minor | `scripts/probe-pi-load.sh` `REQUIRED` list | Stale entry `use-railway` no longer exists in `skills/` (removed by `6782415`), so the paid probe would fail on a stale name rather than a real regression. | Fixed in scope: T007 must reconcile stale required entries. |

Also verified as already correct and left unchanged: consecutive `T` numbering, explicit `**Depends**` fields,
narrow write scope, `opus-class` ≤ 30% with rationale, no parallel-batch policy weakening, EPIC
approval/provenance preservation, SpecKit-as-EPIC-provider, 14/15 boundary semantics, and the plan-free
Requirements Manager route.

## Fixes applied (task-level, no architecture change)

- Added T002 (coverage matrix + behavior inventory + capability/fallback inventory + deliberately-not-restored
  list), T011 (independent semantic diff review); renumbered to a contiguous T001–T011 with explicit backward-only
  `Depends` and updated the count/share statements, coverage checklist, and review concerns.
- Strengthened acceptance on T004 (operational stage sections, conditional clarification, approval checkpoints,
  approval renewal, sizing/documentation preservation, observed reviewer), T005 (owner model selection, no parallel
  batches, sequencing-defect routing, commit boundary distinctions), T006 (documentation scope, sequencing-defect
  routing), T007 (index entries, `/reload`, stale probe list, README direct-task routing), T008
  (operational-section checks, capability/fallback assertions, negative legacy assertions, class-distinction),
  T009 (in-memory mutation list that must fail on missing operational instructions), T010 (matrix completion,
  `UNAVAILABLE` reporting, static-walkthrough labelling, task-scoped exclusions).
- Added: artifact evidence-honesty rule, three-way review-stage distinction, critique review record with hashes,
  §Scope of the exclusions in this artifact, updated handoff context.

Nothing in the settled architecture (stage sequence, stage classes, 15-task boundary, small-list policy,
seven-package shape, SpecKit role) was changed.

## Commands and results

| Command | Result |
|---|---|
| `python3 skills/epics-manager/scripts/check-task-order.py docs/plans/requirements-manager-tasks.md` (rev1) | PASS (exit 0) |
| `python3 skills/epics-manager/scripts/check-task-order.py docs/plans/requirements-manager-tasks.md` (rev2, final) | PASS (exit 0) — 11 tasks, backward-only deps, contiguous stages |
| `python3 skills/epics-manager/scripts/test_check_task_order.py` | OK, 5 tests |
| `bash scripts/check-skills-lint.sh` | 21 skills checked, 0 failed |
| `git diff --check`, `git diff --stat docs/index.md` | clean; `docs/index.md` still +4 lines only |
| `git status --short` | ` M docs/index.md`, `?? docs/plans/` (no staged files) |
| `git show --stat fdb91a5`, `git show 32e12feb…:skills/epics-manager/SKILL.md` | confirmed the historical pipeline and its removal (782 changed lines in `skills/epics-manager/SKILL.md`; `resolve_epic.py`, `migrate_state.py`, `test_compatibility.py` deleted) |
| `ls skills/ | grep use-railway` | 0 matches (confirms F15) |

Not run, deliberately: full `epics-manager`, any SpecKit stage, `scripts/install.sh`, `scripts/probe-pi-load.sh`
(paid model call), any delegation/paid agent. No automatic retry on any failure was needed; no failure occurred.

## Residual risks

1. Static prompt-contract checks still cannot prove runtime model obedience; T010/T011 are required to say so.
2. T002's matrix is only as complete as its derivation; the "draft before reading the rewritten prompts" rule is
   the control, and it is a process control, not a mechanically enforced one.
3. Independent reviewer availability for T011 is unknown; the honest outcome may be `UNAVAILABLE` plus a recorded
   blocker rather than a review.
4. T011's `opus-class` flag (F13) is open for the owner; accepting it keeps the `opus-class` share at 2/11.
5. The approved count is now 11 tasks across two classes; the design's seven-package illustration (sonnet 1–3 →
   opus 4 → sonnet 5–7) no longer matches, so the coordinator must derive the real schedule from the approved
   count — recorded in the handoff context.

## Handoff context for the parent / next session

- The task artifact is revision 2 with its own critique record inside (durable, inspectable). I did **not** label it
  overall-reviewed, approved, or implemented.
- The only repo write was `docs/plans/requirements-manager-tasks.md`; `docs/index.md` and
  `docs/plans/requirements-manager.md` are byte-identical to the pre-critique state (hashes recorded above).
- Implementation authorization remains yours/at the review barrier. Once the owner authorizes, the artifact's
  exclusions permit the coordinator's mandatory delegation, the single focused small-run commit before review, the
  review-fix commit, 15+ per-batch commits, and the T011 review delegation.
- Suggested next actions: (a) run the independent overall review of this task artifact, (b) put F13 and the
  11-task schedule to the owner, (c) only then hand off to `coordinate-implementation` with the T002 coverage
  artifact required as an input.
