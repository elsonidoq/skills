# Delivery validation guide

This is a future run guide, not evidence of implementation acceptance. V1–V6 are **NOT RUN** in planning. Requirements and exact acceptance mappings: [spec.md](spec.md#required-acceptance-evidence). Decisions and supporting source: [research.md](research.md). Interface invariants: [contracts](contracts/README.md).

## Prerequisites and setup

After later implementation approval, use the selected worktree, current task scope and actual `.pi/workflow-executor.json`. Python >=3.10/PyYAML 6.0.3, Git and the existing fixture infrastructure support offline checks; Node >=22/Pi SDK 0.87.1 are needed only for affected host/bridge checks. Missing dependencies report the actual missing operation; do not install/authenticate automatically. No provider or historical workflow launch is needed for V1/V5/V6.

From repository root, existing focused test entry points are:

```sh
PYTHONPATH=runtime:runtime/tests python3 -B -m unittest discover -s runtime/tests -p 'test_engine.py'
PYTHONPATH=runtime:runtime/tests python3 -B -m unittest discover -s runtime/tests -p 'test_check_correction.py'
PYTHONPATH=runtime:runtime/tests python3 -B -m unittest discover -s runtime/tests -p 'test_verification.py'
PYTHONPATH=runtime:runtime/tests python3 -B -m unittest discover -s runtime/tests -p 'test_worker_authority.py'
PYTHONPATH=runtime:runtime/tests python3 -B -m unittest discover -s runtime/tests -p 'test_resume.py'
PYTHONPATH=runtime:runtime/tests python3 -B -m unittest discover -s runtime/tests -p 'test_review_chain.py'
PYTHONPATH=runtime:runtime/tests python3 -B -m unittest discover -s runtime/tests -p 'test_git_effects.py'
```

Select relevant existing classes/cases as implementation adds regressions; these commands are discovery entry points, not a requirement to run every suite for every edit. Existing `scripts/check-task-commit-contract.py` and task/planner contract checks are appropriate only where their owned instructions change. Baseline failures must be reported separately from correction-induced failures; never weaken assertions to obtain green output.

## Required demonstrations

| Mapping | Setup and action | Passing observable / evidence |
| --- | --- | --- |
| V1 / FR-001–003,005 | Extend existing actual-Engine/stub-adapter disposable-Git tests. Reproduce negative no-edit and partial-edit returns, including delivered answer then blocked return; run authored failing command through existing executable field. Repeat after correction. | Fail-before/pass-after; task A not complete, B/review/fixer absent, partial bytes/history retained. Actual command/exit recorded; known worker-reported required failure/unrun result not accepted. Positive successful required, no-command/no-change, optional/unconfigured, corrected-tool and existing required-correction cases pass. Add focused resume regression only if it demonstrates a bypass. |
| V2 / FR-004–005 | Label the external incident wording as a scenario, not current verified application source. Inspect current causal prompts and reproduce earlier agent-created exact-setup/rerun restriction versus later scoped authority. Test initial and affected correction/resume handoffs. | Current authority/shared routine permissions delivered without routine renewal, genuine owner/manual/paid/security/data limits preserved. Report text-contract evidence versus any actual behavior separately. No historical application repair. |
| V3 / FR-005–007 | Small supported exercise: completed predecessor, unfinished worker blocked by diagnosed in-scope file outside its paths; settle/reconcile invocation/lock, delegate bounded repair under selected executor, verify diff/check/checkpoint, use retained continuation, then issue a later routine question. | Repair's exact paths/selected settings/check output/SHA observed; original worker boundary intact; predecessor not replayed; unfinished work continues; later question investigated/answered autonomously, no routine approval. Identify actual versus stubbed coordinator/worker actions. Prompt assertions alone do not establish behavioral completion. |
| V4 / FR-008–010 | Small representative failure with primary evidence and an actionable issue-body ambiguity/scope drift. Run RCA, create/readback, separate actual-body intent review, evaluate/correct drift and read back. Include uncertain cause and unavailable reviewer/concurrent-body protections at changed seams. | Intent/evidence and actual body reach independent reviewer; actionable finding evaluated and narrow correction observed by separate GET; qualified URL, mutation outcome, review result and uncertainty reported. Exact duplicate/auth/target/sensitive/concurrent safeguards preserved. Scripted reviewer output is labelled simulated, never actual model judgment. |
| V5 / FR-011 | Feed otherwise identical single-line/range rejected review JSON through actual parser and existing engine review/repair fixture; keep malformed JSON/type/missing-location cases. | Both valid forms reach rejected-review/repair with unchanged finding text; invalid forms remain invalid, not approved. Offline sufficient. |
| V6 / FR-012–013 | Disposable Git repository with named authorized untracked target, named authorized modified tracked target and unrelated dirty/staged files. Exercise supported input→handoff→claim→intended edit→checkpoint. Repeat unapproved/broad-limit cases. | Initial target bytes survive except intended edit; exact owned results checkpointed; unrelated bytes/index unchanged. Unapproved target refused with file/operation/supported correction even under broad path limit. Hooks/signing and safe-path protections preserved. Offline sufficient. |

## Live and manual boundaries

Prefer existing focused fixtures and the smallest controlled supported exercises; do not force paid/live/historical replay. V3 actual delegation/continuation requires implementation authority, inspected failure/state and usable selected tools. V4 actual issue mutation requires explicit target/operation authority and usable GitHub capability; actual separate reviewer requires loaded delegation/configuration. Neither permission is granted by these artifacts. Missing authority/capability yields NOT RUN/UNAVAILABLE for the affected evidence, with resumption action; it does not waive V3/V4. Offline mechanical coverage may proceed when authorized but cannot replace missing independent judgment/autonomy evidence. Do not invent extra application startup ceremonies or universal manual gates.

## Reporting and evidence lifetime

For each applicable V item report concrete command/scenario, actual result, tested revision/environment, actual versus simulated actors and remaining gates. Keep ordinary checks/docs/teardown with their delivery outcome. Preserve disposable evidence until affected consumers are validated; no separate proof/report/cleanup task chain. Failed/unrun proof blocks reliance on its outcome. Renew affected producing review/approval for material scope/acceptance changes, not routine technical corrections. Later focused commits preserve unrelated work; final independent review remains required.
