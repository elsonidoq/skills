---
name: coordinate-implementation
description: Use when implementing or resuming approved work from a reviewed task list and its authorized source artifacts.
---

# Coordinate Implementation

Trust the approved settled design. Deliver bounded tasks in dependency order:
approved intake → bounded delegation → actual diff/commit/REQUIRED audit → next
ready work → fresh independent final review. Do not routinely replan, rereview the
design, repeat unchanged preflight or run broad redundant checks.

## Load and Verify

Read the identified approved source/tasks and repository instructions once. Establish
current-content review/scope authorization, constraints, exclusions and dependencies.
Missing, stale or unverifiable approval blocks the affected action; never invent
provenance or regenerate planning artifacts to bypass a blocker. Resolve ambiguous
origin or conflicting planning depth. For applicable origin-specific approval and
repair gates, use the existing [approval/recovery mapping](../planner/references/approval-and-recovery.md).
Direct artifact repair is limited by the
[bounded mechanical correction contract](../planner/references/approval-and-recovery.md#bounded-mechanical-corrections);
uncertain or substantive intake corrections return to the originating/fresh bounded producer
and affected review/approval renewal, never approval relabeling.
TinySpec needs separate source/tasks and current combined approval; Standard needs
specification/plan/tasks, both current approvals and required SpecKit stage evidence.
Preserve legacy source shape and authorization rather than relabeling work.
SpecKit applies only to its selected origin/stages, not merely because installed;
report unavailable applicable commands and use direct artifact checks where permitted.

Load adopted gotcha memory through `memory-handling` and only relevant existing
compact coordination guidance under the [project coordination contract](../memory-handling/references/project-coordination.md).
Carry applicable constraints into task briefs and REQUIRED checks. Missing coordination
store or STATE is nonblocking. No automatic STATE creation, editing or removal; no
routine summaries, index updates, evidence-only commits, reflection or inferred lessons.
Leave existing STATE/custom content and historical records untouched.

Before the first retained task write, establish baseline HEAD, allowed paths, index/
worktree ownership, usable Git/identity/signing/permissions and required check baseline.
A fresh/resumed implementer compares the supplied baseline and repository state;
unexpected changes or unresolved checkpoints mean no edits, cleanup, or commits.
A fresh implementer never adopts or commits unknown work. Apply the canonical
[task-commit contract](../memory-handling/references/task-commit-contract.md).

## Recover Context

Start with available conversation summary/recent context; do not assume retained tokens
or require a snapshot. Selectively reconstruct only uncertain authorization, completion,
Git HEAD/diffs/index ownership and actual check/commit evidence needed for the next action.
Unknown approval/completion blocks that action: never guess completion or repeat commits.
Reconcile recorded and unrecorded active children through usable runtime before dispatch:
a running child means inspect/wait, not duplicate dispatch; unknown child status or
missing runtime evidence stops replacement. Inspect a failed run and its invocation
before targeted resume/retry; unknown cause stops blind retries. Preserve partial and
unrelated work. Missing context alone calls for selective reconstruction, not a new ledger.

## Prepare Approved Execution

Verify usable question/delegation capabilities, async budgets, permitted mutation tools
and a fresh independent reviewer before implementation. Missing required capabilities
stop with the exact gap (`question: UNAVAILABLE`, `Delegation: UNAVAILABLE`,
`Independent review: UNAVAILABLE` or `Agent/model selection: UNAVAILABLE`).
No unauthorized local fallback; do not install, probe live providers or change settings.

Count the complete approved implementation task list, including completed tasks but
excluding standalone reviews. Up to three bounded tasks may run locally only with the
current owner-selected exact profile and adequate observed context; otherwise delegate.
More than three require delegation. Completing tasks does not change that strategy.
Both routes use the same dependencies, per-task checkpoints and final review.

Build consecutive context-coherent batches in approved order, one exact profile per
invocation. Normally 2–5 related tasks, not a quota; shared files, phase headings and
internal dependencies alone do not require splits. One writer verifies and commits each
producer before its consumer. Split for material profile, context, permission, owner-gate
or external-prerequisite incompatibility. A later-numbered prerequisite is a sequencing
blocker: return to producing review, never silently reorder. All implementation batches
execute sequentially, never in parallel. Continue all incomplete dependency-ready work;
for an explicit partial boundary use `ask_user` to confirm boundary versus full completion.

Assess each batch using the six-factor [routing rubric](references/batch-routing.md),
not a universal default. Start the first proposal with demands/oracles, inspect material evidence
or state non-reliance, then compare suitable family/effort options before readiness with independent
comparative Family and Effort rationales; an adequate never-launched proposal may remain pending.
Then report readiness/gaps under the shared rubric: readiness blocks launch, not suitability;
retain the recommendation and ask for bounded authorization or an explicit fallback choice.
A fallback needs its own justification, readiness and exact owner selection; no silent fallback.
Reuse applicable passive proof; deeper source inspection is conditional, not a routine audit gate.
Present the entire proposed execution table: task IDs, outcome,
dependencies, integration/check pointers, local/delegated mode, exact binding/effort,
separate comparative Family and Effort rationales, applicable guidance or none.
Implementation approval is not routing approval: use `ask_user` for explicit batch/profile
approval before writes or dispatch. Reuse verified unchanged approval; changed boundaries/
profiles renew affected rows, source/scope/acceptance changes renew producing gates.

Verify callable binding, supported effort, permissions and tool access through the shared rubric's
readiness conjunction at assignment and dispatch; missing permission/binding/effort/tool support blocks dispatch. Registry
names/suffixes alone are not proof. Copy the owner-selected exact profile
unchanged into actual arguments (pi-subagents `model: "provider/id:effort"`); no silent
settings/agent override. Selected versus observed stays separate; unobservable actual
binding/effort is unknown. Unsupported or mismatched arguments block launch.

Before tooling-dependent dispatch, establish the smallest applicable executable proof
that the first required local check runs in the assigned workspace. An authorized bounded
setup/readiness assignment may establish it; dependent product implementation waits for
sufficient proof. Record check/outcome, workspace, tool/dependency versions and write
conditions; one applicable result can serve multiple tasks. It covers only capabilities
exercised or otherwise established; new dependencies need bounded readiness checks,
not assumed coverage or another full preflight.
Authorization is not availability; an existing dependency directory is not a usable installation,
and client binaries do not prove a required server can run. Reusable packages do not
establish writable-cache isolation: inspect where the actual loader/tool writes.
Read the current guard branch, not historical adjacent restrictions. Reuse readiness proof
only while its workspace, tool/dependency versions and write conditions still apply.
Already-authorized bounded local setup may proceed without another approval request;
missing permission stops setup, missing capability stops dependent dispatch with the exact gap.
Separate unresolved setup from a large implementation assignment when it materially threatens
delivery; ordinary ready setup stays internal. This grants no destructive, ownership,
network or external-operation permission.

## Delegate

Normally launch one direct asynchronous worker for a batch, including internal sequential
tasks. A single child or batch does not justify a workflow wrapper; a concrete branching,
aggregation or other earned orchestration need may, with a terse reason in the existing
brief. Both shapes retain all gates. Stay within observed per-run/session budgets.
Reuse a child only with selected profile, supported resume and adequate relevant retained
context; otherwise narrow a fresh brief. Unknown context capacity is not billed-token
capacity. Rotation is not retry authority. On timeout inspect the checkpoint and failed
invocation, preserve completed proof and narrow only the diagnosed remaining work.

On an observed stall or failure, inspect the actual invocation and available checkpoint/proof now;
do not wait for a full timeout just because budget remains. Supported signals include a
worker setup blocker, failed first check, runtime attention/failure or available progress
showing blocked work. Narrow the diagnosed missing work while preserving verified checkpoints
and applicable partial evidence, using the recovery safeguards above. Silence alone is not
an observable stall. Without supported signals, early detection is not promised.
This is event-driven recovery, not routine polling or an arbitrary stop threshold.

Keep briefs compact and source-bound, not transcript-bound: use one canonical contract reference.
Source pointers do not replace the whole applicable REQUIRED contract.
The self-contained worker brief supplies workspace, baseline, exact selected profile,
source/tasks/approval paths, ordered task IDs, allowed paths and mutation tools, shared
constraints, dependencies, exclusions and permission/manual gates. Include the whole
unchanged REQUIRED union before coding: each ID's criterion, smallest check, expected
proof and pass condition; optional checks stay separate. Missing contracts return to the
producer, never retrofit weaker acceptance. Require per-task verified owned-path commits
and healthy internal continuation without routine coordinator approval. No healthy-task
contract reconstruction or rediscovery is needed. Batch independent deterministic inspections/checks
when safe; preserve dependency order, attributable failures and permission boundaries.
This does not parallelize implementation writers. Return concise item-mapped results with
accessible proof, changed outcomes/blockers, every REQUIRED disposition and ordered baseline/result SHAs.
Record each shared command result once with all covered item mappings.

Once required preparation is satisfied, dispatch. Reopen only affected decisions/checks
on concrete contradiction, failed prerequisite, material scope change or ownership,
permission, profile, runtime, environment or budget drift. Reuse unchanged applicable
proof; routine progress is not invalidation. No separate progress ledger or persistence gate.

## Execute and Integrate

Workers establish a meaningful failing check/mutation, implement only owned scope,
inspect the actual diff and run each task's REQUIRED checks at the smallest sufficient
layer. Required unavailable/unrun checks or unmet manual/permission gates block reliance;
optional checks cannot compensate. Representative-sample manual STOP, when required,
needs the inspectable sample and explicit owner approval, never self-review.

Choose affected checks from the changed contract and current test collection;
verify selectors reach current guards rather than retired adjacent contracts, and that
selection is nonempty. Run checks on final bytes; later edits invalidate only affected proof.
A skipped test or old green report is not new proof. Reuse prior evidence only after confirming
scope, relevant bytes and environment remain applicable: unchanged pertinent bytes and
applicable selector/tool conditions allow reuse; bounded unrelated edits leave proof valid.
Rerun invalidated or contradicted items, not all unchanged checks.
Attribute inherited failures only with an applicable baseline: identify both revisions and
relevant differences, equivalent selector, tool/environment and failure oracle, and observed
same failing behavior. Matching failure text alone is insufficient; byte identity is not an
automatic comparison prerequisite. Retain inherited failures alongside new regressions or
increased severity against the relevant behavior/oracle; baseline failure cannot dismiss
changed behavior. Proven criterion violations are failed; inadequate comparison proof is
insufficient-evidence, not an invented historical green.

Commit each task's verified changes as one focused owned-path commit before later task
writes or handoff. Explicit staging/path-limited commits preserve unrelated staged and
unstaged work; same-file ambiguity stops. There is no skip/defer question or No-Git fallback.
Missing verification, Git/identity/signing/permission, hook/check/commit failure or policy/
ownership conflict stops; never disable hooks/signing, configure identity, broadly stage,
push, reset or rewrite history to force success. Only the coordinator alone may recover
understood verified uncommitted task work; failed recovery stops dispatch. No extra
evidence-only checkpoint. Healthy internal tasks continue without a supervisor round trip.

At return, cheaply inspect every task's actual diff, focused commit/SHA, REQUIRED outputs
and residual owned changes before releasing external dependents. A child report, clean
tree, commit existence or generic green is not proof. Reject combined, empty-success or
unauthorized commits. For each REQUIRED item audit criterion relevance, current revision/
environment, command exit/observables, accessible proof and consistency; record satisfied,
failed or insufficient-evidence with reason/proof in the task/runtime return. Missing,
stale, conflicting, irrelevant or unavailable proof is insufficient-evidence, not success.
Only satisfied REQUIRED items and fulfilled original gates release dependents. Shared
checks run once with distinct item mappings; this audit is not general design rereview.

On failure inspect run/invocation, partial commits and check evidence; diagnose capability,
planning/contract, batching, tooling, dependency or unknown. Preserve valid work and prior
attempts, identify affected dependencies/invalidated items. Targeted repair retains the
same original contracts, needs usable owner-selected capability and reruns invalidated
items only. Unknown cause blocks blind restart; planning/contract gaps return to producing
approval, not model substitution. Clean retry is exceptional, requiring diagnosed
unsoundness/contamination, safe ownership and applicable owner gates; never automatic
rollback or discard. Material product/architecture/privacy/cost/irreversible choices remain
owner gates. No external operations without explicit authorization.

## Review and Acceptance

No per-task reviews. After all task commits obtain one fresh independent final review
from the owner-selected usable reviewer, not an implementation session. Supply the full
committed revision range, source/tasks/approval and criterion-mapped evidence. Missing
reviewer blocks final acceptance. Correct authorized findings as separate verified focused
tasks; rerun invalidated checks/review and renew affected producing approvals as needed.

Return ordered baseline/result SHAs, owned changed files, every REQUIRED item disposition
and concrete command/output/artifact proof, residual state, incomplete work and blockers.
Report selected versus observed profile (unknown stays unknown), local/symbolic versus live
validation, and PASS/FAIL/PARTIAL/NOT RUN/UNAVAILABLE truthfully. State implementation
completion separately from final acceptance. No automatic STATE/memory closeout, reflection
or learning ledger. Explicit future-directed user feedback alone follows the feedback owner.

## Maintaining this contract

With `PYTHONDONTWRITEBYTECODE=1`, run `python3 scripts/test_intake_contract.py`,
`python3 scripts/test_batching_contract.py` and `python3 scripts/test_state_contract.py`
from this skill directory. Static mutations, symbolic recovery/dispatch and temporary-Git
fixtures check contract sensitivity, not live model obedience or compaction fidelity.
Tell the user to run `/reload` in pi after global skill changes.
