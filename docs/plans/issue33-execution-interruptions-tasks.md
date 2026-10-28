# Issue #33 — concrete correction tasks

Requirements: [TinySpec](issue33-execution-interruptions-tinyspec.md), AC1–AC5/Binding constraints.
[Executable tasks](issue33-execution-interruptions-tasks.json) replace the five investigation tasks
with three bounded corrections. Source SHA256 remains
`0e8bc6494de5fd018797d8818c5d9b30248e06132aec04b59dee3c70e77fbe80`.
Correction/diagnosis baseline: `d7aa64901abf8088ee3fa222dd431b77764ded0e`.

## Outcomes and completed/no-task mappings

| Source | Correction or established unchanged outcome |
| --- | --- |
| AC1 | **T001:** operating-guide check-command/setup explanation only. Actual environment-boundary proof is completed below; inheritance is normal, not a runtime defect. |
| AC2 | **No implementation task:** complete task/acceptance carriers and existing successful/unsuccessful dispatch support are intact. Local completion and eligible dependents remain possible with explicit live-only evidence unavailable; genuine failed/unrun required acceptance still blocks its actual claim/dependents. No live-readiness/deployment or model-judgment claim. |
| AC3 | **T002:** one cohesive refinement of the existing supporting-ownership recipe: final configuration/override owners and producer's applicable admitting/type check. Small static contrasts/ordinary-success control, not a toy application or compiler. Fixture-location source alignment remains required below. |
| AC4 | **T003:** actionable terminal EOF/actual parent-channel-loss diagnostics with focused input/socket regressions. Supported living-parent wait/reply works on settled evidence; no bridge lifetime implementation. |
| AC5 | Every task preserves authority, scoped repairs, real acceptance/manual gates, partial bytes/checkpoints, unaffected cumulative coverage and notification rules through the shared contract. Only affected verification reruns. |

These are independently verifiable documentation, shared-authoring and adapter-diagnostic outcomes
for Terra/medium. T002 combines the two preparation specifics in the same existing recipe/fixture,
not independent unfinished product interfaces. No producer dependencies exist among the corrections;
the existing executor is sequential (lowest ready ID). Empty `depends` is not concurrency authority.

## Settled diagnosis consumed by the tasks

The separately authorized diagnosis ran against clean baseline above; parent inspected production
helpers/probe and unchanged Git state. This correction inspected supporting spans without rerunning
the diagnosis. Findings below are durable bounded inputs, not implementation acceptance.
The supporting session report/probe at `/tmp/skills-issue33-diagnosis.md` and
`/tmp/skills-issue33-boundary-probe.py` are optional detail, not future executable prerequisites.

| Evidence | Observed result and source spans at the diagnosis baseline |
| --- | --- |
| **Environment / AC1** | `verification.py:27–41,78–101` runs checks in project cwd without env override; bridge `:213–220` spreads parent env; launcher `:6–8` selects existing runtime knobs, not project shell setup. Probe called production `run_checks` with the same argv `[sys.executable, '-B', str(check)]`: child `/bin/sh -c 'export ISSUE33_DUMMY=ready'` did not change coordinator's `ISSUE33_DUMMY=mismatch`; check exited **17**, output `missing ISSUE33_DUMMY=ready at runner check; set it on coordinator launch or in this check command`. Scoped coordinator `ISSUE33_DUMMY=ready` made that **same argv** exit **0**, output `dummy prerequisite ready`; command-prefixed self-contained control also exited **0**. Seven existing ProjectCheckTests passed. T001 consumes this causal proof and compares guidance to unchanged behavior, not repeat experiments. Arbitrary prerequisite diagnosis remains project-command responsibility. |
| **Carriers / AC2** | `intake.py:17–19` deep-copies context; `engine.py:1289`, `419–420`, `895` deliver complete task/original contracts to worker/fixer/reviewer. `_COMPLETION_REPORTING:92–100` already distinguishes worker and runner stages. Existing two-task authority success and actual-adapter blocked-result tests passed: unchanged contract/success dispatch versus preserved partial bytes/no checkpoint/no dependent. No field loss or local/live enforcement defect found. Historical contradictory worker decision is judgment/handoff error; fixtures prove delivery/ordering, not agent semantic understanding. |
| **Preparation / AC3** | `task-generation/SKILL.md:133–151,166–173,199–212` already covers coupled selectors/harness, support ownership/dependencies, finishable acceptance and final composed observable. `planner/SKILL.md:141–149,168–174,424–438,551–574` already consumes that owner in both routes/reviews. Missing specificity: final config/override-owner inspection and producer fixture's applicable admitting check before reliance. Existing supporting-ownership/executor-recipe tests passed **2/2**. Generated-output preservation `test_generated_outputs.py:12–55` is intact/inspected, not rerun or an implementation outcome. Refinement/contrasts prove instruction sensitivity only. |
| **Questions / AC4** | `terminal_question:457–460` calls builtin input after TTY check; real PTY ordinary answer returned `yes`, exit **0**; canonical Ctrl-D raised raw empty-message **EOFError** (probe exit **3**). `parent_question:45–63` real Unix peer close yielded `Blocked: parent owner bridge unavailable: connection closed before an owner reply`, lacking pending-operation/recovery action. Marker bytes `preserve-me\n` remained unchanged. `cli.py:173–179` authenticated readiness/no terminal fallback, bridge `:132–159,185–192,224–242,276–292,315` pending/reply/closure mechanics and real triage fixture establish a pending question remains answerable after observation wait completion with fixture parent alive; exact reply led to terminal **exit 0**. No elapsed-wait expiry or current bridge defect demonstrated. |

Exact diagnostic executions (historical results, **not rerun here**):

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/runtime" .pi/workflow-validation/venv/bin/python -B /tmp/skills-issue33-boundary-probe.py
```

Expected mismatch/loss/EOF findings and successful environment/PTY controls above were observed;
this scratch-script command is provenance, not a required retained artifact or implementation check.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests .pi/workflow-validation/venv/bin/python -B -m unittest -v test_verification.ProjectCheckTests test_worker_authority.WorkerAuthorityTests.test_every_task_gets_authority_without_rewriting_historical_task_text test_engine.SequentialExecutionTests.test_actual_adapter_transport_outcome_blocks_before_checkpoint_or_dispatch test_pi_adapter.SDKTransportTests.test_parent_question_requires_correlated_bridge_response test_pi_adapter.SDKTransportTests.test_parent_readiness_requires_positive_correlated_response test_pi_adapter.SDKTransportTests.test_parent_question_reports_unavailable_bridge test_pi_adapter.SDKTransportTests.test_interactive_terminal_answer_is_direct_owner_input test_pi_adapter.SDKTransportTests.test_noninteractive_question_stops_without_fabricating_answer test_pi_adapter.SDKTransportTests.test_unanswered_question_closes_input_before_waiting_for_owned_host test_pi_adapter.SDKTransportTests.test_adapter_multiplexes_steering_while_correlated_question_waits
```

**16 passed**. The exact two-selector instruction-test command retained in T002's executable
`checks` also ran during diagnosis: **2 passed**, sensitivity evidence only.

```sh
PYTHONDONTWRITEBYTECODE=1 COHERENCE_PYTHON="$PWD/.pi/workflow-validation/venv/bin/python" node --test --test-name-pattern='parent triages a technical question|runner output stays off|missing parent reply capability|bridge start abort signal|bridge wakes|bridge launches explicit' runtime/tests/test_question_triage.mjs runtime/tests/test_bridge.mjs
```

**7 selections passed**, but the idle/busy bridge fixtures emitted `SDK callback lacks a correlation ID`
and do not assert terminal success: their PASS is **not completion evidence**. The load-bearing
ordinary-success control is `test_question_triage.mjs`'s first real bridge/Python socket test
(exact correlation/session/run rejection, later reply, terminal exit 0). The unrelated real-SDK
steering selection hardcodes absent `runtime/.venv/bin/python`; it was not run and needs no repair
for this scope. No broad-suite rerun or model/provider call occurred.

Owner reports a recent Paseo configuration change from Node 22 to Node 24. That is configured
host context, not verified effective runtime: distinguish the configured executable, already-running
parent/coordinator and actual project-check subprocess. It creates no global Node 24 requirement or
new check gate. The dummy Python inheritance proof remains applicable to unchanged process mechanics;
no historical Node-version observation establishes current runtime. No config change/restart/probe is needed here.

Evidence applies to unchanged helpers/carriers at this revision. Before reliance, compare relevant
spans/diff for invalidation; retain applicable results, refresh only invalidated evidence. T003's
changed diagnostics need their own permanent actual-input/socket regressions and success controls.
Historical wait-timeout → PTY-loss causality remains **UNVERIFIED**, not a blocker to the observed
EOF/loss diagnostic correction. PTY callback/socket fixtures are not whole-engine resume proof,
production long-wait/Paseo assurance, live acceptance, deployment or agent-obedience evidence.

## Shared worker and reviewer contract

Read this section, settled evidence and the relevant source AC/Binding constraints before work
or review. Each executable task directs that read. Inspected `engine.py:1289` includes the full
individual task, `:419–420` original contracts in corrective context and `:895` tasks in review;
references reach fresh contexts without a new carrier. Follow them, not link-only compliance.

Producer re-read exact `/home/dev/projects/skills/.pi/workflow-executor.json` before tasking/recovery.
Pass unchanged: worker `openai-codex/gpt-5.6-terra`, medium; fresh reviewer
`openai-codex/gpt-6.1-sol`, medium. Saved producer remains `tinyspec-tasks:
openai-codex/gpt-6.1-sol`, medium. No search/substitution/configuration change.

- [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md):
  **“Preserve task requirements, acceptance criteria, real manual gates and safety/permission boundaries. Material unresolved authority conflicts still ask the owner.”**
  Current scoped launch supersedes historical phase wording, not acceptance or unrelated scope.
- [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md):
  **“Unknown/pre-existing bytes must not be adopted or deleted.”**
  Small isolated tests/databases and scoped routine repairs/selective artifacts need no renewed
  routine consent; retain resource/data/security/paid/external limits and no global installation.
- [Verified memory](../../memory/MEMORY.md): routine technical choices are autonomous; ask only
  material product/scope/real-permission questions. Preserve completed checkpoints and still-valid
  unaffected review/check coverage. Routine transitions/steering do not wake parent; questions and
  terminal success/error may. Keep existing #30/#32 support, not repeat its implementation.
- Required failed/inconclusive/unavailable/unrun checks block affected claims/dependents, never
  become a waiver. Real live/manual/paid/external acceptance needs its real capability/authority.
  Local completion never means live readiness/deployment. No extra manual gate for isolated local
  verification; no semantic judging engine or scripted proof of agent reasoning.
- Narrow owned paths bound actual corrections. Outside-path necessity uses existing scoped
  coordination, not automatic adoption/expansion. Preserve unknown/concurrent bytes and honor the
  [checkpoint contract](../../skills/memory-handling/references/task-commit-contract.md): executable
  runner owns staging/commits, no-change has no empty commit. Return actual paths/checks/checkpoint
  identities/limits in existing returns, no ledger. Global skill activation uses fresh-session Paseo
  handoff, never `/reload`. No prototype or research chain is selected: diagnosis already settled scope.
- Reuse [canonical dependency guidance](../coordinate-implementation.md#setup-and-verification),
  Python >=3.10/PyYAML 6.0.3 and Node >=22/Pi SDK 0.87.1 declarations; no lifecycle redesign by recollection.
  Preserve all source exclusions: no application/Cerca replay, #28 dirty-file takeover, #5 loops,
  #14 replay, added intake rules, env schema/capture/admission/framework/amendment API/recovery service,
  STATE/reflection/ledgers/retry budgets, production/deployment/push/auth/global settings or automatic
  install/reload/restart. Sensitive question/answer/token text must not newly reach safe/public outputs.

## Approval and source alignment

**Combined-approval readiness is blocked on ONE source alignment:** TinySpec AC3 explicitly places
conditional representative examples in `scripts/test-planner-workflow.py` ("there"); T002 instead
uses the existing, narrower `skills/task-generation/scripts/test_contract.py`. Parent confirmed it
will route this exact fixture-location correction to the original source producer before combined
approval. Do not reinterpret the source location as illustrative or silently waive it. Preserve the
representative config/producer contrasts, ordinary-success control, pass conditions and sensitivity
limits. No upstream source was edited here; these tasks are a prepared correction, not a ready or
approved implementation handoff.

AC1/AC2/AC4 accept reuse of completed actual-boundary diagnosis and supported unchanged mechanisms;
source timing about checks not executed **during source preparation** is historical, not a new task.
Both prior combined approvals were cancelled; parent inspection and renewed current-content approval
remain required. No implementation authority is inferred from diagnosis or planning recovery.

This correction runs mechanical planning validation only. The parent-reported unchanged planner
full-suite result **170/171**, with
`CoordinateAcceptedDecisionBriefTests.test_skill_requires_consultation_and_worker_review_propagation`
failing on a missing literal in the coordinate-implementation skill, remains outside scope: no
unrelated repair, test weakening or broad rerun. Product changes/new regression passes are not claimed.
