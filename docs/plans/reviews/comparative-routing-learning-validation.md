# Comparative routing and actionable learning — bounded validation

T003 evidence for [source](../comparative-routing-learning-tinyspec.md), [tasks](../comparative-routing-learning-tasks.md)
and [run record](../../../memory/coordination/evidence/2026-10-09-comparative-routing-learning/SUMMARY.md).
Scope comparison: baseline `ff74a9e111d325ccc823cbbe6b93b408b3064077`; B1 producer commits
`32227744d30d875dd2703c401093619c59cbcc52` and `2e7acbd9a4a2171dee352cf3d4cf53ff99fd2d67`;
source digest and normalized task contract remained unchanged (completed checkbox only).

## A1–A6 and prior REQUIRED evidence

| Source criterion / prior item | Actual evidence and disposition |
| --- | --- |
| A1 comparative routing | T001/V1: `ComparativeRoutingTests` in `skills/coordinate-implementation/scripts/test_batching_contract.py` covers closed/recovery, unavailable alternatives, policy, override, inadequate-contract stop and Standard non-leakage; T001/V3: batching 50, planner checker PASS, planner 99, brainstorming 4. Local/simulated, not runtime behavior. |
| A2 batching trade-off | T001/V2: `test_batch_tradeoff_examples` plus comparative owner text distinguish startup/context savings from smaller-profile opportunity and preserve coherent batching. Same T001/V3 checks. |
| A3 compact attributable evidence | T002/V1: `test_coordination_contract.py` fixtures cover compact checkpoints/index and mutations preserving failed/partial unknown attempts; final run reported 26 tests PASS. |
| A4 actionable reflection | T002/V2: same coordination fixtures exercise covered/candidate/incidental, non-model proposal and preservation; 26 tests PASS. |
| A5 approval and future consumption | T002/V2–V3: approval/reject/drift byte-preservation plus same-store guidance-to-source/task/brief decision walkthrough, both adapter/direct consumers and mutation checks; coordination 26, planner 99 and task-generation 6 PASS. Simulated/manual translation only. |
| A6 integration and limits | T002/V4: coordination 26, checker PASS, planner 99, task-generation 6 and batching 50 PASS; consumer links and gates inspected. Live obedience/performance NOT RUN. |
| T001/V1–V3 | Preserved accepted B1 evidence in SUMMARY, T001 checkpoint commit `8118b2be28502979d984aebf56a299e0087183cb`, implementation `32227744d30d875dd2703c401093619c59cbcc52`; coordinator audit records all three satisfied within fixture/static limits. |
| T002/V1–V4 | Preserved accepted B1 evidence in SUMMARY, implementation `2e7acbd9a4a2171dee352cf3d4cf53ff99fd2d67`; coordinator audit records all four satisfied within fixture/static limits. |

## R1 superseding qualification — comparative fixture sensitivity

The A1/A2 and T001/V1–V2 coverage/accepted claims above are historical, not current
unqualified proof. Fresh independent review finding 1 and independent coordinator/worker
reproduction showed three contradictory outputs survived all three ComparativeRoutingTests:
mandatory-medium proposal changed to low, shortfall comparison changed to “Sol is suitable”,
and both batch decisions exchanged. This is a verification-contract/test-sensitivity defect,
not model-incapability evidence. T003/V1's original mapping is qualified accordingly.

R1 adds independent finite case expectations for proposals and family/effort reasons, a
specific recovery-shortfall obligation, and each batch scenario's own expected outcome.
Explicit negative records remain separate from expectations. No contract semantics, family
ladder, production router or model invocation changed. The same output-only mutant replay
leaves all expected values fixed: mandatory-low now fails `strict_medium` profile equality;
suitability-only fails the recovery comparison obligation; swapped decisions fail both
named batch equality assertions. Normal batching50/checker PASS/planner99/coordination26/
task-generation6 pass. Reproduction logs: `/tmp/routing-learning-R1-worker-before.log`
(all three survived), `/tmp/routing-learning-R1-worker-after.log` (all three rejected).
Replay: `PYTHONDONTWRITEBYTECODE=1 python3 /tmp/pi-routing-learning-R1-replay.py`;
normal checks use the five existing scripts with the same environment flag.

This corrects bounded fixture sensitivity for T001/V1–V2 and the T003/V1 evidence mapping;
final independent reviewer recheck remains pending. Static/simulated checks still do not
prove live model obedience/performance. The separate original T004/V3 preservation-baseline
gap remains unresolved and outside R1; no final acceptance is implied.

Documentation cross-check: `skills/coordinate-implementation/references/batch-routing.md` remains
sole comparative rubric; `skills/memory-handling/references/project-coordination.md` owns compact
factual evidence, three-way reflection, exact approval/drift protection and retrieval-to-decision
consumption. `REQUIREMENTS.md` and `docs/index.md` describe those actual seams without creating a
second contract or boilerplate chain; README does not contradict them. Link/package check is included
in the lint result below. No A criterion is represented as live model proof.

## T003/V2: future behavioral comparison recipe

[Planner Regression](../planner-regression.md#comparative-routing-and-approved-learning-evaluation-permission-gated-not-run)
holds four fixed cases: closed design; hidden-coupling/recovery; docs plus acceptance grouping; and a
non-model process lesson through exact approval and later retrieval. It requires preserved baseline
inputs/revisions, fresh read-only baseline/candidate outputs, exact selected and supported profiles,
one run per case per side (eight total) with no retries, finite spend/run budget, permission and
capability checks before invocation, independent criterion review, selected-versus-observed/unknown
attribution and explicit sample/performance limits. This task did not run it; separate explicit
permission remains required.

## T003/V3 validation

At T003 working revision: batching 50, planner static checker PASS, planner workflow 99,
brainstorming 4, coordination 26, task-generation 6; existing shared lint/package suite PASS:
22 skills checked, 0 failed, with embedded planner workflow 99, coordination 135, brainstorming 4,
task-generation 6, batching 50 and remaining listed suite checks 10/18/13/7. The lint suite reports
its internal checks; these counts are not unique tests across combined commands. `git diff --check`
and changed-link inspection are required at checkpoint. These focused static/fixture checks do not
measure model performance or prove obedience. The fresh full independent review and retained rechecks are recorded in the linked run
SUMMARY. R1's three contradictory mutants are independently rejected; corrected content
has no remaining finding. Owner approved the exact T004/V3 alternate proof-method
amendment at e7a68d7, then the reviewer accepted its trace/scoped-commit/correction-hash
proof: **ready with disclosed limitations / OK with notes**. Original dirty-content byte
baseline remains missing; unhashed untracked files and live model obedience remain
unverified, not silently passed. All 13 REQUIRED items are accepted within their approved
local/manual/simulated bounds and the explicit preservation amendment. Cerca's local
checkpoint retains the original limitation; the later approval/acceptance belongs to the
linked global source/task run, without editing its concurrently dirty shared index.
