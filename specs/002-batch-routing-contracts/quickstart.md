# Quickstart: Bounded Contract Validation

This is a validation guide for future implementation of [the plan](plan.md), not evidence that routing changes or live model tests have run. [Research](research.md) owns benchmark/runtime limitations; [data model](data-model.md) defines item mappings without a new schema.

## Prerequisites and setup

Use the selected repository root, Python 3, Git, installed suite check scripts and approved implementation artifacts. No package install, credentials, internet or paid provider call is needed for static/fixture validation. Preserve unrelated workspace changes. Before live dispatch separately verify Pi/subagent capabilities, exact permitted binding, supported effort, tools, owner selection and permissions; a catalog entry is insufficient.

From the repository root:

```bash
python3 --version
git status --short
sha256sum specs/002-batch-routing-contracts/spec.md
```

Expected current approved spec digest: `1b4d5b90ac1e1429739e5260d0955716d125a1b4ae8430141e89b610eacd9895`. A changed spec requires renewed approval, not inferred permission.

## Focused checks after implementation

Extend these existing check seams as described in the plan; they currently check the old workflow and cannot yet prove the new scenarios:

```bash
python3 scripts/check-planner-workflow.py
python3 scripts/test-planner-workflow.py
python3 skills/task-generation/scripts/test_contract.py
python3 skills/task-generation/scripts/test_check_task_order.py
python3 skills/coordinate-implementation/scripts/test_intake_contract.py
python3 skills/coordinate-implementation/scripts/test_batching_contract.py
python3 scripts/check-task-commit-contract.py
python3 scripts/test-task-commit-contract.py
git diff --check
```

Expected: updated focused assertions and fixtures pass, while source/overall approval, consecutive sequential execution, per-task commits and final independent review remain enforced. Run task-order validation against the eventual task artifact using the installed task-generation command; this stage creates no tasks. Inspect the actual revision diff as well as test results.

## REQUIRED simulated scenarios

Use bounded fixtures in the existing coordinator checks. Profiles are symbolic permitted/supported selections in simulation, not authenticated live calls.

| Scenario | Expected decision/evidence and disposition |
| --- | --- |
| Closed-design Luna/medium, strong contracts, no local guideline | One profile; all required item evidence/checkpoints inspected; accepted without a mandatory strong per-batch reviewer |
| Bounded Luna/max experiment | Recorded independent effort rationale; selected and reported max retained; complete evidence accepted without per-batch strong review |
| Diagnosed capability failure under Luna/max, authorized Sol/medium repair | Original attempt retained, diagnosis supported, valid work preserved, full contract supplied and invalidated checks rerun before acceptance |
| Environment-blocked Luna/medium | Required item not verified; blocked; attribution `environment_or_tooling`, no model-capability penalty |
| Relevant approved local guideline selects Sol/medium over seed Luna/max | Applicability and approved evidence cited; guideline refines prior without overriding source or owner permissions |

For each accepted fixture, verify 100% of REQUIRED task items have concrete evidence, exact selected binding/effort is retained, every task checkpoint is in scope, and final independent review remains required. Add one small two-task/shared-check case: one check can satisfy both references, but removing a required result or contradicting its output blocks acceptance and dependent work. A missing supported binding/permission blocks dispatch; an unobservable actual effort is unknown, not falsely reported as proven.

## Manual integration review

Trace an actual sample artifact chain: task acceptance references → batch contract union → selected dispatch arguments → return evidence → each task diff/checkpoint audit → disposition → existing indexed feedback. Check empty-guideline behavior, direct and helper planning research links, legacy producing-gate return, retained exact guideline approval/drift checks, and settings that must not silently override the selected profile. Verify no raw outcome edits guidelines and no fixed escalation ladder is introduced.

Report PASS, FAIL, PARTIAL, NOT RUN or UNAVAILABLE with evidence for each scenario. These static/fixture/manual checks are not live performance, cost comparisons or runtime model-obedience proof. Live checks require separate permission and usable bindings; required live checks that cannot run remain blocked, never waived by fixture passes.
