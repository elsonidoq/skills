# Bounded execution efficiency — TinySpec

## Status, provenance and outcome

Owner-selected TinySpec and Sol/medium source producer; preparation and focused source
commit only. Implementation is NOT authorized. Separate tasks, planner review and
current-content combined owner approval remain required. This is authoritative what/how
for that later task production, not an implementation checklist or readiness declaration.
Production baseline: `592cd051080e2e0a9f0045561427dde09420deea` on `main`.
Only this source and its [discovery entry](index.md) are owned by this production.

The conversation supplies the request: a reported multi-hour run with many calls,
retries/compactions and setup, composed-boundary, timeout and obsolete-selector failures.
These reports motivate bounded improvements; they are not independently reconstructed
runtime evidence, a model comparison, or a speedup prediction. Beneficiaries are owners
and future executors: avoid setup surprises, unnecessary round trips, repeated checks and
broad recovery while preserving verification, privacy, ownership, approvals and review.

## Scope, authority and exclusions

Canonical owners remain [coordinator](../../skills/coordinate-implementation/SKILL.md)
(readiness, dispatch, proof reuse and recovery), [planner](../../skills/planner/SKILL.md)
and [task-generation](../../skills/task-generation/SKILL.md) (acceptance definition), and
[batch-routing](../../skills/coordinate-implementation/references/batch-routing.md)
(profiles). Changes are narrow skill/reference and existing regression-harness changes;
update current consumers or [REQUIREMENTS](../../REQUIREMENTS.md) only for demonstrated
consistency needs. Do not create another owner or duplicate contracts across consumers.

Preserve [AGENTS](../../AGENTS.md), [constitution](../../.specify/memory/constitution.md),
[documentation routing](../index.md), [task checkpoints](../../skills/memory-handling/references/task-commit-contract.md),
[feedback boundaries](../../skills/memory-handling/references/project-coordination.md),
[early risk reduction](../../skills/planner/references/early-risk-reduction.md),
[dependency research](../../skills/planner/references/dependency-research.md) and
[TinySpec source contract](../../skills/tiny-spec/SKILL.md) and
[SDD source quality](../best_practices_spec_driven_development.md). The producer also read
`writing-skills` completely from its discoverable installation; it supplies portability,
observable-branch and focused-validation guidance, not new suite runtime requirements.
The adopted [memory index](../../memory/MEMORY.md) has no gotchas and
[coordination guidelines](../../memory/coordination/GUIDELINES.md) have no approved guidance;
no memory writes or invented lessons.

Excluded: external-project/memory changes; installs, live probes, external operations,
deploy/push; settings/provider/runtime changes or package-pin updates; Epic/STATE/research/
evidence scaffolds; mandatory readiness ledgers, exhaustive audits or integration programmes;
Cartesian matrices, duplicate prototypes, routine polling, stop thresholds, blind retries;
quotas, writer caps, time targets, automatic model changes or universal provider hierarchy.
Exact commands, cache traps, flags, limits, fixtures and historical project prevention belong
in the affected project's tooling/docs/memory, never reusable global skills. Preserve
TinySpec/Standard/legacy compatibility, explicit permissions, REQUIRED/manual gates,
per-task owned-path commits and fresh independent final review. After later global skill
changes, tell the owner to run `/reload` inside pi.

## Evidence and genuine gap inventory

**Repository-derived decisions**, from complete current contract inspection:

| Supporting span / local evidence | Missing specificity and resulting constraint |
| --- | --- |
| Coordinator “Prepare Approved Execution”; routing “Readiness before dispatch” | Exact profile/tool permissions already gate dispatch, including detached-context readiness. Add the smallest actual local first-check proof in the assigned workspace, not a broader provider audit (A1). |
| Planner “Proportionate validation”; task-generation “Task contract” | Lowest-layer seam proof is already required. Clarify when separate green components cannot establish the actual risky composed boundary (A2), not blanket integration testing. |
| Coordinator “Delegate”; planner “Selected production and stage handoffs”; `SimulatedUnionReturnTests` | Whole REQUIRED briefs already exist. Compact source-bound presentation and safe deterministic inspection/check batching are targeted specificity; do not repeat the existing contract as a fix for nonenforcement (A3). |
| Coordinator “Execute and Integrate”; `PracticalVerificationTests`, `SimulatedAcceptanceTests`, `VerificationGapTests` | Current revision/environment and missing-proof stops already exist. Make current collection/selector, final-byte and inherited-baseline applicability explicit (A4). |
| Coordinator “Recover Context”, “Delegate”, failure paragraph in “Execute and Integrate”; `SimulatedRepairTests` | Inspected failure, checkpoint preservation and targeted retry already exist. Add observed-stall inspection now, rather than waiting for the full timeout, and isolate delivery-threatening unresolved setup (A5). |
| Routing “Assess all six factors”, “Provisional family and effort choices” | Already distinguishes family/effort, uncertainty, oracle/check cost, tool depth and coupling. No concrete gap found: retain the rubric unchanged (A6). |

Failed application of existing whole-contract transfer, evidence reuse, checkpoint
preservation, permission, safe-retry or review rules is not a missing requirement.
Do not solve it by repetitive prose. Retain existing guards and improve only the
specific predicates above and their regression sensitivity.

**Observed local evidence:** the owner-owned dirty addition `ExecutionReadinessTests` in
[coordinator batching harness](../../skills/coordinate-implementation/scripts/test_batching_contract.py)
was inspected, not edited/adopted/committed by this source producer. The owner permits
its eventual implementation adoption. At the stated HEAD with that addition, Python
coordinator checks returned intake 3 tests PASS, state 12 tests PASS, batching 56 tests
FAIL (36 failing subcases, all within the new class). Those failures expose missing
instruction carriers; they do not independently prove live behavioral defects. Its
finite readiness cases and existing item-audit fixtures are reusable starts, not adequate
keyword-only acceptance for every distinction below.

**Dependency evidence reuse/skip:** [REQUIREMENTS runtime table](../../REQUIREMENTS.md#runtime)
retains pi 0.87.x (tested 0.87.1), pi-subagents 0.73.1 and pi-ask-user 0.15.1;
SpecKit is Standard-only. No version-dependent runtime integration or new dependency
is selected here. Local prose and Python harness inspection suffice; Python 3 executed
the baseline checks. External dependency research and provider/source audits are unnecessary
for these bounded instruction changes. No callable provider, child environment, observed
model/effort or runtime-obedience claim is inferred from the owner's Sol/medium selection.

## Approach and observable acceptance

Use short conditional additions at the canonical seams and targeted fixtures/mutations
in existing harnesses. Source pointers reduce background, not applicable contractual
content. No migration is needed; corrections are separately verified focused changes,
not rollback/discard of valid checkpoints. Material contract/scope changes renew affected
producing review and approval; missing required authority/evidence blocks reliance.

**A1 — Executable local readiness.** Before tooling-dependent dispatch, establish or reuse
the smallest applicable actual proof that the assigned workspace can execute its first
required local check. Authorization is not availability; a dependency directory is not
an installed usable dependency; a client is not a runnable required server; reusable
packages do not establish writable-cache isolation. Inspect the actual loader/tool write
location and current applicable guard branch, not a historical adjacent guard. Proof is
reusable only for applicable workspace, versions, write conditions and check. Already-
authorized bounded local setup needs no redundant permission request; destructive,
ownership, network and external-operation boundaries still apply. Missing permission
stops the affected setup; missing capability stops affected dispatch with the exact gap.
No mandatory install, provider probe or exhaustive environment audit is implied.

Observable: finite positive/reuse and negative cases distinguish authorized-but-unusable,
directory-only, client-only, cache-write mismatch, parent-versus-assigned workspace and
historical-versus-current guard. Applicable execution evidence records check/outcome and
context; a declaration of readiness alone cannot release tooling-dependent work. For this
instruction change these are offline cases, not execution against an external project.

**A2 — Smallest composed acceptance where needed.** Planner and both task adapters must
identify a genuine risky boundary that separate green components cannot establish, and
require the smallest composed check that observes it. Relevant examples are serialization
through storage limits, primary input/error custody through cleanup, sanitization before
the first durable write, and transport arguments through wrappers. Assert the final
observable/order/custody, not only each helper's green test. If a focused existing seam
check already establishes the contract, reuse it; no Cartesian matrix, duplicate proof
or blanket integration programme. Preserve necessary security/durability checks.

Observable: representative offline fixtures make isolated components green while the
composed contract fails; a corrected composition passes. A negative control keeps an
ordinary already-observed wiring seam bounded. Each required item carries criterion,
smallest check, expected accessible proof, dependencies and permission/manual gates
through direct and SpecKit adapters, with no executor-defined weaker acceptance.

**A3 — Compact complete briefs and returns.** Keep briefs source-bound, not transcript-bound,
while retaining the WHOLE applicable REQUIRED union, constraints, scope and gates before
coding. Safely batch independent deterministic inspections/checks with attributable
failures and preserved dependency/permission boundaries; implementation writers/batches
remain sequential. Return concise item-mapped results with accessible command/output or
artifact proof and focused checkpoints. A shared check runs once with every item mapping.

Observable: existing multi-item shared-proof fixture remains accepted; removing an item,
gate or accessible output blocks acceptance/dependence. Bounded batching cases distinguish
independent read-only checks from dependent producer/consumer checks and unsafe writes.
No quota, writer cap, transcript forwarding or profile change is introduced.

**A4 — Applicable current proof, not generic green.** Choose affected checks from the changed
contract and current test collection; verify selectors actually reach current guards rather
than retired adjacent contracts. Attribute an inherited failure only with an applicable
baseline: same selector, contract, tool/environment and unchanged relevant bytes. Run
checks on final bytes; subsequent edits invalidate only affected proof. Reuse previous
proof only after confirming scope, relevant bytes and environment. Rerun invalidated or
contradicted items, not all unchanged checks. A skip or old green is not new proof;
missing REQUIRED evidence blocks acceptance and dependent release.

Observable: fixtures reject obsolete/empty selection, skip-as-pass, post-check affected
edits and mismatched baseline attribution; accept unchanged applicable proof and retain
unaffected proof after a bounded edit. Reports distinguish proven defect from
insufficient evidence without relabeling either as success.

**A5 — Delivery-risk setup and event-driven recovery.** Separate materially delivery-threatening
unresolved setup from a large implementation assignment so it can be diagnosed without
burying the blocker in the whole batch. Ordinary bounded ready setup needs no ceremonial
split. On an observed stall/failure inspect the actual invocation and available checkpoint/
proof now; do not wait for the full timeout just because budget remains. Narrow diagnosed
missing work and preserve verified checkpoints and applicable partial proof. Running
children require inspect/wait; unknown status/cause blocks replacement or blind retry.
Resume suitable retained context only with supported capability and existing authority.

Observable: offline event traces show inspection before the remaining deadline, exact
missing-work handoff with preserved SHA/item proof, and no duplicate dispatch. Controls
reject unknown-cause retry, discard of valid work and routine polling/threshold protocols;
healthy sequential internal tasks still continue without supervisor round trips.

**A6 — Routing and safety preservation.** Keep the existing six-factor rubric/profile rules
unchanged absent a demonstrated concrete gap returned through scope review. Preserve
independent family/effort justification, readiness versus suitability, exact owner selection,
Standard Sol/medium exception, permission/privacy boundaries, per-task commits and final
independent review. No historical failure implies model superiority or a new default.

Observable: existing routing, intake, state, ownership, union, acceptance and safe-repair
regressions remain green after authorized implementation; changed links resolve and
`git diff --check` passes. Static/symbolic results cannot be called live obedience or speedup.

## Verification, proof lifetime and handoff limits

Early risk reduction uses existing mutation/fixture checks, not a duplicate prototype:
the hard seam is distinguishing permitted transitions and sufficient evidence in prose;
no new library/runtime core warrants a disposable implementation experiment. Before
instruction changes, demonstrate meaningful failing contract/mutation tests for A1–A5
in existing harnesses. Test the distinctions and negative controls, not keywords alone;
retain current safety tests. The present dirty tests supply baseline failures, but later
authorized work must close symbolic coverage gaps rather than merely paste asserted phrases.

Proof producer → instruction consumers → final production validation → cleanup: failing
fixtures precede changed coordinator/planner/task-generation text; each affected consumer
inspects/runs applicable fixtures and preserves their tested boundaries; final-byte harnesses
and links validate the delivered contract; retain fixtures and mapped evidence through all
consumers and independent final review. No disposable artifact is currently planned, hence
no cleanup scaffold. Failed/unrun REQUIRED proof blocks assumed consumers; disproof retains
limits and renews affected approvals if approach/source/acceptance changes.

Required later coordinator checks, from its skill directory, each prefixed
`PYTHONDONTWRITEBYTECODE=1`: `python3 scripts/test_intake_contract.py`,
`python3 scripts/test_batching_contract.py`, `python3 scripts/test_state_contract.py`.
For task-generation changes also run `python3 scripts/test_contract.py` and
`python3 scripts/test_check_task_order.py` there; planner changes use its current documented
workflow checks when affected. Check changed links and `git diff --check` on final bytes.
Task production must map A1–A6 to stable REQUIRED items, outputs and gates, selecting the
smallest checks sufficient for each distinction; optional broader checks remain separate.

No material design question is deferred. Source production has no implementation authority,
tasks, combined approval or final implementation review. Runtime/enforcement limitations
remain: instruction-managed checks cannot guarantee live agent compliance, child setup,
provider availability or measured improvement. Live evaluation requires separate authority
and usable capabilities; it is not scheduled as a mandatory probe by this source. The
owner-owned dirty batching test must remain untouched/uncommitted during source production.
