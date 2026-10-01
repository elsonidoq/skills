# Requirements Manager execution tracker

## Current state

**OWNER APPROVED EXECUTION: “go ahead”.** T001–T011 and FR1–FR3 are committed; FR3 is `c50d91368fc91af40fdea34de3336fb0d457caa0`. T012 remains pending parent disposition and successful recheck. Completion of initial checks or corrections is not feature acceptance. The following preparation-era statement is historical: earlier planning reconciliation: `3817425a08fe7c9bdeefed7e6e3322e268bda02e`; the subsequent batch-approval preparation commit is the complete implementation review baseline.

Approved sequence: T001–T005 (Terra), T006 (Sol), T007–T011 (Terra), then T012 (fresh Sol reviewer). Execute only async background delegation, sequentially, with per-task verification/commits and no per-task reviews. The workflow is regenerated against revision 4.

## Authorization, policy, and capabilities

- Direct bootstrap is owner-selected; do not fabricate a specification or claim the current coordinator already supports its planned intake. Historical/current protection baseline: `fa41d5f3f5aeb7ddfa9963222eff2c0447533059`.
- Models chosen by owner: sonnet-class implementation = openai-codex/gpt-5.6-terra; opus-class implementation = openai-codex/gpt-6.1-sol; fresh independent final reviewer = openai-codex/gpt-6.1-sol.
- All delegation must be async/background. Delegate tools observed: read/edit/write/bash; reviewer is read-only. Git identity and commit capability are available. Refresh capabilities before dispatch as needed, without re-requesting settled selections.
- More than three implementation tasks require delegation. Batches amortize startup and carry useful context across sequential tasks, including internal dependencies/shared files/phase headings. Task ordering remains fixed. Commit each task after verification, before next task; no per-task reviews. One final independent review.
- Task count is not context headroom; pause/split/rotate for observed context limits, model changes, owner gates, incompatible scope or external integration blockers. No forced one-session-per-class limit, parallel implementation, blind retry, or silent model switch.
- No project memory store/adoption contract is declared in this configuration repository's AGENTS.md; do not invent one. SpecKit is not required for this explicit bootstrap.

## Approved implementation batches

| Batch | Task IDs | Context shared within batch | Dependencies | Integration / verification | Class / model | Status |
|---|---|---|---|---|---|---|
| 1 | T001–T005 | Historical/current workflow sources; coverage baseline → shared primitives/validator → EPIC restoration → shared batching criteria | None external; internal prerequisites run sequentially | Draft T001 baseline before replacement text; focused tests/lint/inventory; verify and commit each of five tasks | sonnet-class / Terra | completed |
| 2 | T006 | Origin-specific authorization and shared execution contract built by batch 1 | T003–T005 | Intake gates, local/delegated threshold, context/batching/commit checks; one task commit | opus-class / Sol | completed |
| 3 | T007–T011 | Lightweight producer, routing/docs/discovery, contract tests, mutations and integration evidence | T001–T006 from preceding batches; internal prerequisites run sequentially | Producer/handoff tests, links/lint, operational/named mutation checks, coverage/walkthroughs and full review packet; separate commit for each of five tasks | sonnet-class / Terra | completed |

T001's source-first ordering is an internal checkpoint, not an extra agent launch. Phase headings and shared file writes are not automatic split reasons because these are sequential single-writer batches. Batch 2 has one task because of its model-class boundary. The two five-task batches share coherent context and fit the target batch size, subject to actual scope/context observations during execution.

## Final independent review (not an implementation batch)

First T012 report: [final semantic review](reviews/requirements-manager-final-semantic-review.md), complete reviewed range `e21a6b27aed02192aecac739e5ef033e6ce61dcf..1a067b02b45747d907619f9f5aebe7643208dd73`. Verdict NOT_READY. This is the single end-of-implementation review, followed by scoped corrections and a focused final recheck—not per-task reviews.

T012 began after batch 3, in a fresh read-only Sol reviewer session. It reads the complete committed implementation range, exact historical EPIC, pre-change protection files, coverage matrix/inventory and actual checks. Parent records findings/dispositions and completion and commits review evidence; confirmed scoped fixes get separate verified commits. Do not resume an implementation session for review. A clean worktree is not the review input.

## Baseline verification

Before the earlier preparation commit: existing validator units PASS (5 tests), task-order PASS, suite lint PASS (21 skills), git diff --check PASS. After revision 4: rerun task-order and diff checks before presenting batches. Workflow/mutation tests and coverage now exist, but the final review demonstrated incomplete operational checks. Parent reproduced three false negatives: deleting the gate body, changing specification class, and adding contradictory mandatory-plan policy all passed the initial routine checker. Those test protections must be corrected; no runtime behavior is claimed verified.

## Task evidence and commits

| Task | Status | Evidence | Commit |
| --- | --- | --- | --- |
| T001 | completed | Source-derived baseline and inventory. | `f807b1c249d179c48cad088055f23d229cb2d9eb` |
| T002 | completed | Shared gate and bounded owner dialogue. | `7e77966a42de95736b5f689095a7c8d6b3b4ce68` |
| T003 | completed | Shared adapters and sole validator; FR2 adds the required T001-start unit. | `24f53bb01a1d96748792617f3b8d917c1f67d8d5` |
| T004 | completed | EPIC workflow; FR1 restores reviewed safeguards. | `f4c2981270587d6aa8849719d88f2a10e5530d1c` |
| T005 | completed | Context-continuity batching. | `e6ceef97a7d4ab79882d8544406e9cc73d47a8bf` |
| T006 | completed | Origin-neutral intake and selection. | `be290fc1fd9d4f776912e01d304b120fd4b23165` |
| T007 | completed | Plan-free requirements producer. | `f9b5ff2f72a070a6df33bbd63b9376c894c63dc0` |
| T008 | completed | Routing/discovery documentation. | `f718726d94bfc0c4a567d6a13594f127e66d1c73` |
| T009 | completed | Routine static workflow checker. | `f7d93a5b28b55990645929228a867aa965b2b629` |
| T010 | completed | Initial mutation checks. | `4045a14427976b669862ebc9ba2503ff15d43a17` |
| T011 | completed | Integration evidence. | `1a067b02b45747d907619f9f5aebe7643208dd73` |

### Historical T006 dispatch-era verification checkpoint

- Fresh bounded session selected at the approved sonnet/opus model-class boundary; one task is intentional. Scheduler context metrics are unavailable; no runtime reuse or model-obedience claim is made.
- Read the approved design/revision-4 tasks, coverage baseline, historical EPIC, protection-baseline coordinator, current coordinator/EPIC/shared task contract, runtime requirements and memory contract. This repository declares no project memory adoption.
- Before behavior edits: `python3 skills/coordinate-implementation/scripts/test_intake_contract.py` **FAIL** (all six new checks); existing batching contract **PASS** (3 tests). This is the smallest static baseline for the intake/strategy defect.
- After edits: intake contract **PASS** (6), batching **PASS** (3), EPIC workflow **PASS** (4), task-generation contract **PASS** (2), task-order units **PASS** (6), shared brainstorming **PASS** (4). All run via their adjacent `scripts/test_*.py` entry points.
- `bash scripts/check-skills-lint.sh` **PASS** (23 skills); `python3 skills/task-generation/scripts/check-task-order.py docs/plans/requirements-manager-tasks.md` **PASS**; `git diff --check` **PASS**. Inspected actual coordinator diff against T005 and protection baseline; no second graph or batching algorithm added.
- Static read-through: EPIC retains both current approvals/spec/plan/review/stage evidence; direct inputs with or without installed SpecKit require no plan; ambiguous/stale inputs stop. Three class/context-fit tasks permit local execution; four and four resumed with three remaining remain delegated. Different class/context pressure delegates the affected segment, with no unauthorized fallback. These are prompt-contract observations, not live trials.
- T006 changes only coordinator instructions, coupled tests and task/tracker evidence. Batch 2 completes here; batch 3 is marked `in_progress` as the next approved unit, not launched by this leaf delegate. Final independent review remains T012; routine wiring/mutations remain T009–T010.

## Final review dispositions and scoped correction tasks

All F1–F11 are valid against inspected source. F4's false negatives were reproduced by the parent. No scope/architecture change is required: restore approved safeguards and test them. The additional T001-start validator limitation is also valid and explicitly within original T003 acceptance, despite being inherited.

| Fix task | Findings / scope | Class | Status |
|---|---|---|---|
| FR1 | F1–F3, F5–F8, F11: restored EPIC/source/approval/production/fallback contracts with focused checks | sonnet-class / Terra, medium | completed (`29c64edf72211bd7c4398698ee1e7bbfb210f349`) |
| FR2 | F4/F9 and T003 T001-start gap: operational section/transitions/classes/contradiction checks, real named mutations, routine/custom-tree wiring and validator units | sonnet-class / Terra, medium | completed (`1cbfd24ecf2669af604981575002ebf9c99679c6`) |
| FR3 | F10: truthful metadata; update coverage/dispositions, record actual task commits/checks and export corrected review packet | sonnet-class / Terra, medium | completed (`c50d91368fc91af40fdea34de3336fb0d457caa0`) |

One coherent async/background Terra fix batch ran FR1→FR2→FR3 with the distinct verified commits: FR1 `29c64edf72211bd7c4398698ee1e7bbfb210f349`, FR2 `1cbfd24ecf2669af604981575002ebf9c99679c6`, and FR3 `c50d91368fc91af40fdea34de3336fb0d457caa0`. Then a fresh async/background Sol reviewer with explicit medium thinking rechecks the final corrected range and findings. No high-thinking launch or resumption of a high-thinking reviewer.

### Second recheck and targeted correction dispositions

The second recheck assessed A1, A4, and A5 as **PARTIAL**; its failed report is preserved at [second final recheck](reviews/requirements-manager-second-final-recheck.md). TF1–TF3 are scoped follow-up corrections, not T012 acceptance.

| Targeted task | Finding / evidence | Status / commit |
|---|---|---|
| SR1 | Original routing, constitution, helper, and sizing correction | completed `77b501a356d1c61f1bf2ab6a71b690cef24f8092` |
| SR2 | Original operational checker/mutation correction | completed `d9e0ad5e40ccd7fbf4f81f748c2a66a0a0210344` |
| SR3 | Original durable evidence correction | completed `8b14df9bdecc81c69635ff64058f3ab72182e977` |
| TF1 | A1: RM operational invocation, conditional outputs, and separate eligibility/count mutations | completed `8344516af2b570c22727b08973f373ad02bfb077` |
| TF2 | A4: one adapter-governed planning pass; no post-adapter recreate | completed `d429afcd434d248abf3efe5cf14371e20dac3855` |
| TF3 | A5: provenance and evidence reconciliation | completed in this metadata commit; its SHA is recorded only in the final packet to avoid a self-reference |

- **A1 targeted correction:** section-local operational diagnostics and named mutations now cover the reported RM invocation, transition, class/context, and complete-count omissions. This is deterministic static coverage, not natural-language completeness or live behavior proof.
- **A2 fixed:** invalid required constitutions are repaired through the detected capability and verified usable before specification, otherwise stop.
- **A3 fixed (new owner-authorized routing addition):** fresh small work is explicitly recommended to `requirements-manager`; documentation initialization and admitted/resumed safeguards remain.
- **A4 targeted correction:** `plan_create` conditionally composes one manager-governed architectural-planning pass, then inspects its evidence/artifacts without a second plan create.
- **A5 targeted correction:** FR and SR provenance are distinct, FR3 has an absolute SHA, and the T006 dispatch-era paragraph is explicitly marked historical.
- **A6 fixed:** `create-epic` points to the authoritative sizing section instead of copying conditions; this was a preexisting duplication, not an FR1–FR3 regression.
- **T012 remains pending** parent disposition and recheck; no correction task self-certifies acceptance.

### Correction evidence and dispositions

| Finding | Disposition | Code/test evidence | Result |
|---|---|---|---|
| F1 | corrected | `epics-manager` overall-review rule; `material-default` mutation | PASS static |
| F2 | corrected | constitution checkpoint; `constitution` mutation | PASS static |
| F3 | corrected | required reference/sizing rule; `reference-sizing` mutation | PASS static |
| F4 | corrected | `check-requirements-manager-workflow.py`; stage/block/class/transition mutations | PASS static |
| F5 | corrected | every-stage brief/handoff rule; `reading-handoff` mutation | PASS static |
| F6 | corrected | task-generation and requirements producer authorization checks | PASS static |
| F7 | corrected | plan created-plan review/fix; `plan-transition` mutation | PASS static |
| F8 | corrected | `REQUIREMENTS.md` and brainstorming prose-end-turn/stop contract | PASS static |
| F9 | corrected | custom-directory lint mutation test reports explicit SKIP | PASS static |
| F10 | corrected | current-state/task metadata reconciled in this commit | PASS documentation inspection |
| F11 | corrected | specification and outcome/phase briefing checks | PASS static |
| T003 T001-start gap | corrected | `test_lone_t002_is_rejected` | PASS (7 validator units) |

FR1 checks: four focused contract units (5+4+2+4 tests), suite lint, and diff check PASS.
FR2 checks: operational checker, six named mutation methods, seven validator units, suite lint,
task-order, and diff check PASS. These static checks do not prove model obedience, live owner
questions, SpecKit execution, async scheduling, or reviewer independence.

Delegates record changed files, actual checks/results, context limitations and separate task commits; update only assigned completion/evidence fields in task artifact and tracker. Preserve approved definitions and owner decisions. No installer, paid probe, provider/runtime config changes, product work, push or deployment.
