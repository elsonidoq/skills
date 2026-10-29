# Workflow execution reliability — TinySpec

## Status, request and authority

Source preparation only; not implementation approval, task approval, or feature acceptance.
The owner requested **“Address the three of them using /skill:planner”**, referring to
[skills #34](https://github.com/elsonidoq/skills/issues/34),
[#35](https://github.com/elsonidoq/skills/issues/35), and
[#36](https://github.com/elsonidoq/skills/issues/36). The owner explicitly confirmed task
granularity is in scope and selected **“OK. Let's use tiny spec”**. This retains that actual
depth choice and request provenance, not an inferred routing decision. Full current issue
bodies were read with `gh issue view 34/35/36 --repo elsonidoq/skills` during preparation.
The bounded brainstorming handoff `/tmp/issues-34-36-brainstorm-assessment.md` informed
inspection only; the issues and supplied owner constraints govern requirements.

Baseline inspected: `9407b52843145f346ef1db16e9c98245c291ca31`, clean index/worktree.
Source production assignment: `openai-codex/gpt-6.1-sol`, medium; not an implementation
assignment. The direct task producer must itself read the selected executor JSON at
`/home/dev/.paseo/worktrees/0zfm1a0e/poor-fireant/.pi/workflow-executor.json` before
later decomposition; preserve this exact resolved path, not this producer's model.
Separate tasks follow fresh independent read-only specification review, producer corrections
as needed, and planner inspection; combined current-content source/task approval precedes
implementation. No implementation task checklist is embedded here.

## Outcome and bounds

For owners and selected executors, authorized workflows should reach genuine completion
without repeated owner prompting for routine technical recovery. Final task review makes
material execution needs usable before reliance; coordinators investigate and follow through;
reviewers can reassess actual retained evidence without replaying completed implementation;
workers receive consistent completion guidance, bounded same-session continuation, and
nonrecursive recovery context. Task creators **and** reviewers enforce independently
acceptable bounded outcomes, rather than approving milestone-shaped assignments.

Included: existing shared task-authoring/final-review and coordinator contracts; task-worker
prompt/outcome-tool and continuation boundaries; retained check evidence in independent
review; a narrow evidence-only review continuation; focused regressions and affected canonical
operating/storage documentation. Both TinySpec/Standard and direct tasking consume the shared
contracts. Preserve the six existing task-linter rules, task fields, and normal SDK tools.

Excluded: application/Cerca changes, active Cerca task rewrites, historical experiment/run
replay or migration, model experiments/evaluation, installs, deployments, external writes,
worker/model selection changes, broader tooling policy, new recovery framework, evidence
schema, risk scoring, admission subsystem, mandatory prototypes, report chains, arbitrary
file/task/token/time/resource quotas, and automatic new sessions/retries. Private historical
sessions are not prerequisites; supplied incidents motivate requirements, not verified local
application acceptance.

## Binding constraints

- [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md)
  requires current scoped launch authority in initial, corrective and resumed worker briefs;
  historical planning-only text does not veto a later authorized launch. Executable tasks stay
  authorization-neutral; temporary approval status belongs in approval records. Preserve real
  acceptance, manual gates and material authority conflicts. Observable: prompt and task-review
  checks retain these outcomes, without rewriting historical artifacts.
- [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md) preserves the
  shared `_ROUTINE_AUTHORITY` block, ordinary scoped fixes and small isolated fixtures/databases
  without repeat approval. Preserve paid application/API, credential, security/data, global
  install, external-action, deployment/push and unrelated-byte boundaries. Observable: initial,
  corrective and resumed prompts retain shared defaults and exclusions; authority never supplies
  missing passes. No new permissions service or per-task permission metadata.
- [Project memory](../../memory/MEMORY.md), read in full, directs coordinator-owned routine
  technical diagnosis, owner questions only for product/material-scope decisions and actual
  gates, correction-only review preserving unaffected coverage, and no repeated routine
  authorization. Inspect failed invocation/cause before targeted continuation; unknown failure
  is not retry permission. Routine transitions need no parent acknowledgment. No memory writes.
- [AGENTS.md](../../AGENTS.md), [constitution](../../.specify/memory/constitution.md),
  [task checkpoints](../../skills/memory-handling/references/task-commit-contract.md) and
  [documentation routing](../index.md) retain ownership, focused verified commits, independent
  review and truthful evidence limits. Current owner removal of the Pi version requirement in
  baseline `9407b52` governs; older REQUIREMENTS wording must not reinstate it. Do not broaden
  this into tooling-policy edits. Changed skills/prompts require a Paseo fresh-session handoff,
  never an owner `/reload` instruction or automatic restart.

## Verified seams and dependency evidence

These are repository-derived findings at the baseline, not claims of model causality:

| Inspected supporting span | Existing mechanism / missing seam | Constraint and observable check |
| --- | --- | --- |
| [Task Generation](../../skills/task-generation/SKILL.md#executor-sized-outcomes), especially outcome recipe steps 1–3 and Review and handoff; [planner review](../../skills/planner/SKILL.md), TinySpec step 4 and Standard overall review | Already requires executor-sized outcomes, feasibility and evidence limits. Explicit actionable risk output and proactive consumption are insufficiently clear. | Strengthen existing review/briefs only; representative risk-handoff and atomicity fixtures plus contract inspection. |
| [Coordinator](../../skills/coordinate-implementation/SKILL.md#question-triage), Prepare Approved Execution and Review and Acceptance | Already owns routine diagnosis and inspected resume; currently stops nonactionable reviews. | Diagnose routine early stops and continue through supported paths; actual gates remain scoped. |
| [engine.py](../../runtime/coherence_workflow/engine.py), `_review` (834–930), `_finish_reviews` (931 onward) | Fresh read-only review gets tasks/diff/prior cumulative coverage/checkpoint attribution, but no explicit retained-check evidence handoff. Findings-free rejection stops. | Supply applicable actual check results and narrowly reassess evidence gaps; do not equate read-only inability to rerun with failure. |
| [store.py](../../runtime/coherence_workflow/store.py), `review_dispatch` (658–730), `refresh_review_target_dispatch` (627–656); [CLI](../../runtime/coherence_workflow/cli.py), actions/resume (189–247) | Normal chain requires reviewer→fixer→reviewer. Refresh requires actionable rejection, stale unreserved grant and changed HEAD. Neither supports same-head, findings-free evidence reassessment; ordinary resume reaches the same stop. | Extend existing resume/chain handling narrowly, not misuse target refresh, invent a no-op fixer, or overwrite a settled verdict. Test causal/history retention and restart. |
| [verification.py](../../runtime/coherence_workflow/verification.py), `_run_check`/`run_checks`; engine task completion and `check`/`fixer_check` history | Actual command, exit and output are retained; completed task details include checks. Safe status intentionally omits private outputs. | Reuse private retained evidence, associated with applicable task/repair revision and acceptance; keep raw outputs out of safe status/monitor. |
| engine `invoke_worker` and resume construction (1144–1265), check/checkpoint correction callers (1290–1365); store `resume`/history (535–560) | Run-resume count is not task-session count. Every task-worker/corrective call enters `invoke_worker`; history records distinct invocation IDs/start/terminal facts and saved session, but lacks the requested cap. Full retained prompt is recursively serialized. | Enforce at common task-worker dispatch before adapter/provider call; count durable distinct invocations by actual same task/session, not terminal rows or run resumes. Compact context only. |
| [PiAdapter](../../runtime/coherence_workflow/pi_adapter.py), `prompt` and session/result branches; [host](../../runtime/pi-host/host.mjs), `createWorkflowSession`, `execute` | Effective saved session may come from explicit argument or adapter state. Host validates ID/file/compatibility and emits opened-session identity before prompting. Successful prior-task reuse is distinct from unfinished-task continuation. | Resolve effective identity consistently; preserve existing reconciliation/unknown-outcome stops. Initial invocation for a new task is not charged for another task's use of the same SDK session. |
| host `report_task_outcome` (159–167); engine `_COMPLETION_REPORTING` | Actual tool cue invites unsuccessful reporting for failed/unrun acceptance; shared completion wording also needs alignment. | Correct actual tool description and conflicting current reporting text, not merely append another exhortation; preserve honest failure controls. |

Dependency research reuses the canonical [operating](../coordinate-implementation.md) and
[storage](../coordinate-implementation-schema.md) owners and actual transport source. Python
runtime metadata declares Python ≥3.10/PyYAML 6.0.3; host package/lock metadata declares SDK
0.87.1 for explicit isolated setup. The current resolver actually loaded SDK **1.4.0** from
the existing Pi installation, observed without a provider call. This is version evidence,
not a required version or authority to install/change either environment.

For consequential session semantics, inspected installed official `docs/sdk.md` sections
“Session lifecycle”, “Session storage”, “Prompting”, and `examples/sdk/11-sessions.ts`, plus
`dist/core/session-manager.d.ts` (`getSessionId`, `open`). Official source location:
[Pi SDK documentation](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/sdk.md)
(repository URL verified from installed package metadata; current web content was not fetched;
inspected installed files govern this observation).
Documented: SessionManager owns persistent conversation context/active branch; `open` restores
an explicit session; prompt completion includes SDK retries; `waitForIdle` is distinct from
low-level agent-end. Derived constraint: retain existing SessionManager/adapter lifecycle;
implement an application task/session dispatch limit, not an SDK retry/compaction counter or
transcript mutation. Validate with actual production dispatch-helper/reopen fixtures. No new
SDK API is proposed, so no broad external research or disposable prototype is warranted.
Changes touching version-sensitive APIs must recheck applicable installed declarations, not
assume the latest online API. This source is the bounded reusable findings owner, discoverable
through [plans index](index.md); no separate research document is needed.

## Approach and behavior

### Material risk handoff and coordinator follow-through (#34, #35)

At final task review, return a concise work-specific account of **material execution risks,
executor prerequisites, unresolved assumptions, affected tasks, verified evidence versus
unknowns, and next mitigation/investigation or necessary permission**. Include concrete
runtime/tool/access, interface, fixture or predecessor needs only when relevant. Existing
handoff/task prose carries these findings; no mandatory schema or universal checklist.

The coordinator consumes this account before affected reliance, investigates/prepares within
current authority and gives affected workers actionable findings, usable interfaces, evidence
limits and remaining gates. Apply the same ownership to later discoveries. Report mitigated,
unverified and blocked affected work; do not halt unrelated safe work. Missing credentials,
capability, authorized spend/writes or material product/scope decisions get the exact blocker,
affected operation and corrective action/necessary owner decision, not a generic stop.
Routine worker/reviewer returns are diagnosis events, not completion or automatic owner work:
inspect the invocation, unfinished scope, actual checks and retained effects, supply a targeted
correction and drive authorized work onward, subject to session limits and genuine gates.

### Evidence-only independent review recovery (#35)

Initial and follow-up read-only review briefs must expose applicable retained task/repair check
commands, actual results/output or usable private references, checkpoint/revision association,
and known limits. Reviewer distinguishes: a performed passing check; a genuine failed/missing
required check; inability to rerun in read-only mode; and a check not required by approved
local-versus-live acceptance. Retained evidence is evaluated, not blindly trusted as semantic
proof or inferred from a worker summary, zero exit alone, or current clean tree. Missing actual
required execution remains a gap and is performed in an authorized execution context.

Use existing explicit `resume` after coordinator inspection to support the narrow same-target
case: latest review is settled, rejected for evidence/coverage only, with no actionable code
findings; coordinator supplies targeted evidence/diagnosis, not an unchanged review request.
Append a fresh independent read-only reassessment execution linked to that rejected stage,
using existing chain/history and cumulative coverage. Extend dispatch/selection only enough
for this evidence-only transition: no fixer, empty commit, task replay, fake repair approval,
new permission ceremony or separate recovery service. Preserve prior rejection/attempts,
completed checkpoints, original range/head, valid unaffected coverage and real review policy
for actual code repairs. A repeated unchanged evidence handoff cannot dispatch another
expensive review. A new substantive diagnosis or newly available applicable evidence is
required before reassessment; retain its basis in existing private history.

Reassessment examines outstanding gaps/evidence and affected conclusions; it does not
rereview unaffected passing work wholesale or certify unchecked original scope. Approval
requires no blockers/gaps and cumulative sufficient coverage. New actionable findings follow
the existing scoped repair/permission policy; unresolved evidence gaps remain explicit.
Uncertain invocation, unknown completed effects or target drift stop affected continuation
for reconciliation, never auto-replay. Preserve historical-policy behavior and historical rows;
no mass conversion or automatic historical-run restart. The new transition applies to current
`owner-pair-v1` runs, not a rewrite of historical two-review/one-fixer limits.

### Consistent outcome cue, durable task-session limit and compact context (#36)

Correct `report_task_outcome` at its registration and align conflicting shared reporting text:
unfinished authorized implementation, unrun worker-owned checks, complexity and correctable
failures mean **continue**, not voluntarily report incomplete. Pending runner-owned
checks/checkpoint/review are not worker blockers. Genuine inability to progress, cancellation
and execution failure still report honestly; unmet acceptance never becomes success.

After a task's initial invocation, permit **at most two further invocations of that same
task-worker session**. This includes runner-required-check/checkpoint corrective prompts and
explicit process/run continuation, not SDK-internal retries, compaction or within-invocation
tool correction. Initial use for another task remains that task's initial invocation even
when reusing a settled earlier-task SDK conversation. No numeric limit is added to reviewer/
fixer lifecycle, whose existing causal grants and recovery rules remain intact.

At the shared task-worker dispatch boundary resolve the effective saved-session identity
(including explicit selected session and adapter-held session), and use durable ordinary
invocation history under the writer lock to reserve/count distinct dispatched attempts before
the provider call. Started and terminal rows for one invocation count once; failed/interrupted
calls do not reset the allowance. Refuse the third resume **before** adapter/provider dispatch,
including after reopening storage. Retain identity association for fresh-session initial calls
and subsequent continuations; unknown/unfinished dispatches keep existing inspection stops
rather than assuming unused allowance. History is the required source, not optional metrics
or process-local counters. Reconcile operation-local persistence failures without duplicating
reservations or calls, using existing Store write patterns.

Refusal names exact task/session, used allowance and actionable instruction to investigate
ineffective recovery or deliberately dispatch fresh context under applicable authority. Preserve
partial bytes, checkpoints, diagnostics and history. Do not automatically relaunch, switch model,
reset counts by reopening, or treat the cap as authority for a fresh expensive session. Fresh
context follows inspected failure/fresh-session necessity and existing owner authority.

Continuation prompts carry only actionable diagnosis/targeted correction, unfinished scope,
relevant evidence/history references and unchanged task/authority/acceptance constraints.
Do not serialize previous full prompts or recursively embed invocation history. Retain original
history unmodified for inspection; omit nested prompt bodies from coordinator diagnosis input
as well as worker continuation. No arbitrary prompt-size cap or invented summary of effects.

### Atomic creator and reviewer responsibility (#36)

Both creator and final task reviewer explicitly verify: **one task delivers one bounded
behavior or interface whose meaningful acceptance passes using completed prerequisites and
its own result, without unfinished downstream implementation**. Challenge milestone bundles
and split at useful independently testable seams; several new interfaces needing simultaneous
design/debugging are a warning. Keep behavior's ordinary tests/docs/verification together.
A small wiring change across established systems can remain one outcome; one file can still
contain an oversized subsystem. No file/task quotas, scoring, new metadata, phase-only splits
or fixed example template. Shared Task Generation owns this rule; planner adapters apply it.

## Observable acceptance and smallest sufficient checks

These criteria are source truth for later task-local REQUIRED mappings and worker/reviewer
briefs, not a task sequence. Reuse one sufficient check across mappings; rerun only when
changed revision/environment/scope invalidates it.

| ID | Required observable / normal, error and edge controls | Planned focused evidence |
| --- | --- | --- |
| A1 | Final review exposes a concrete environment/interface prerequisite, affected work, evidence/unknown and next action; coordinator investigates before reliance and briefs executor with usable findings. Unavailable access identifies precise permission/capability boundary and only affected work waits. Later risk gets same ownership. | Extend existing planner/coordinator contract fixtures in `scripts/test-planner-workflow.py` and its existing fixtures; representative local prerequisite scenario and unavailable-access control. Inspect actual producer→handoff→worker brief path for dropped findings, not just matching words. |
| A2 | Actual retained required check evidence reaches read-only reviewer. Same-head evidence-only rejection can be independently reassessed without implementation/fixer replay; original rejection, checkpoints and unaffected coverage survive restart. Genuine missing/failed required check remains gap; unapproved live check is not invented. Unchanged reassessment and uncertain/drifted target dispatch no provider. | Extend `runtime/tests/test_review_chain.py`/`test_resume.py` using scripted adapters, real disposable Git/check operations and reopened Authority/Engine; assert provider roles/count, evidence contents, exact checkpoint SHAs and retained chain/coverage. Positive immediate approval and ordinary actionable repair remain controls. |
| A3 | Actual outcome tool says continue for unfinished authorized work/unrun checks/correctable failures; initial/corrective/resumed authority remains consistent. Completed return still succeeds; genuine inability/cancellation/execution failure still blocks acceptance and preserves diagnostics. | `runtime/tests/test_host.mjs` checks actual registered description/tool behavior; `test_worker_authority.py` and existing outcome tests check prompts and unsuccessful boundary. Do not remove the unsuccessful-result API or use text-keyword acceptance. |
| A4 | Initial call plus two same-task/session resumes work; third is refused before any adapter/provider call, across reopened process/storage and through required-check/checkpoint correction paths. Duplicate start/terminal records do not double count. Distinct tasks/sessions do not consume another task/session allowance; reopening/failure does not reset it. Partial files/history/checkpoints remain. | Permanent actual dispatch/history tests in `test_resume.py`, using concrete saved identities, reopened Store/Engine and provider-call counters. Include correctable check failure, persisted dispatch/interruption and normal success controls; preserve existing missing-history/uncertain-call stops. |
| A5 | Second/later continuation prompts and diagnosis inputs contain relevant failure/correction, unfinished task/evidence references and authority/acceptance, but no embedded prior full prompt bodies. Original history remains inspectable. | Focused `test_resume.py`/`test_worker_authority.py` assertions on distinctive prior-prompt sentinels and required current context; do not impose a character/token threshold. |
| A6 | Creator and reviewer each challenge a milestone containing independently testable interfaces and accept bounded slices with completed prerequisites; a legitimate cross-system wiring change remains atomic with its tests/docs. | Existing `scripts/test-planner-workflow.py` instruction/scenario fixtures and manual source/task review. Confirm both adapters and direct tasking share the rule; no new semantic task validator or active Cerca edits. |
| A7 | ADR-0003/0004 outcomes remain in relevant briefs; authorization-neutral task review, actual required/manual/paid/data/external gates and independent correction-only review survive. Canonical operating/storage docs match actual implemented changes, including narrow exception to generic no-quota language. | `test_worker_authority.py`, affected review/resume tests and focused contract/link inspection; inspect owned diffs and actual Git checkpoints. Update only current canonical owners, not historical approvals or broader Pi policy. |

Implementation verification should use the existing prepared Python environment (no automatic
setup), e.g. `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests python3 -B -m unittest
discover -s runtime/tests -p 'test_resume.py'`, with the analogous `test_review_chain.py` and
`test_worker_authority.py` selectors; `node --test runtime/tests/test_host.mjs`; and
`python3 scripts/test-planner-workflow.py`. Task production resolves runnable exact commands
from the available environment and places each deterministic required command once in existing
check fields. Broader regression is justified only by affected integration. Source production
itself checks links, preservation, scope and `git diff --check`, not these future behaviors.

## Risk rationale, limits and gates

Highest concrete mechanical risks are durable identity/count enforcement before dispatch and
evidence-only chain selection without replay or coverage loss. Permanent production-helper
integration fixtures using real local Git/checks and reopen boundaries are the earliest useful
proof, inside their bounded delivery before reliance; no separate prototype/scaffolding chain.
Existing SDK lifecycle is documented and not being redesigned. Retain relevant proof/results
through consumers and review; disproof blocks affected reliance and returns to targeted diagnosis
or affected source/task review/approval renewal, never weakened acceptance or blind retries.

A1's representative coordinator scenario should show review→investigation→brief order and both
resolved local evidence and precise unavailable access. A2's representative recovery should show
actual executed local check results consumed after a settled coverage-only rejection, with zero
implementation replay. Scripted fixtures prove mechanics/instruction delivery, **not actual agent
judgment, autonomous coordinator follow-through or model obedience**. Manual inspection verifies
contract fidelity only. No offline check can guarantee the behavioral effect of the cue/risk/atomicity
wording; that remains an explicit empirical limitation, not an excuse to require an unapproved
live-model evaluation. Any later real-agent observation must separately name its authority,
capabilities and tested bounds; this source imposes no live model experiment or historical replay.

Required gates: fresh independent source review; separate executor-informed tasks; planner
review and combined current-content owner approval before implementation; usable existing test
runtime for its checks; independent read-only final implementation review and focused verified
checkpoints. Missing real target access blocks only acceptance that actually requires that access;
this package scope does not require Cerca/SSH/live application access. Missing capability or
separately scoped paid/external action requires its specific correction/permission, not routine
repeat consent. No remaining material product question was identified during bounded inspection.
Exact patch/helper names are implementation details; neither model-internal cause nor new wording's
behavioral effectiveness is established. Keep those uncertainties visible in downstream briefs.
