# Bounded execution efficiency — TinySpec

## Status, provenance and outcome

Owner-selected TinySpec and Sol/medium source producer; preparation and focused source
commit only. Implementation is NOT authorized; combined approval was withheld pending
focused source/task revisions. Preserve the separately produced two-task structure;
planner inspection precedes task-producer correction and current-content combined approval.
This is authoritative what/how, not an implementation checklist or readiness declaration.
Initial production baseline: `592cd051080e2e0a9f0045561427dde09420deea` on `main`;
source-correction baseline: `fdf94c2fccb1c8c19520770c5371dd82519a508d`.
Only this source is owned by the correction; its [discovery entry](index.md) is unchanged.

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
[feedback boundaries](https://github.com/elsonidoq/skills/blob/5088b25877467887dd41c9547197c6da43b3c165/skills/memory-handling/references/project-coordination.md),
[early risk reduction](../../skills/planner/references/early-risk-reduction.md),
[dependency research](../../skills/planner/references/dependency-research.md) and
[TinySpec source contract](../../skills/tiny-spec/SKILL.md) and
[SDD source quality](../best_practices_spec_driven_development.md). The producer also read
`writing-skills` completely from its discoverable installation; it supplies portability,
observable-branch and focused-validation guidance, not new suite runtime requirements.
The adopted [memory index](../../memory/MEMORY.md) has no gotchas and
[coordination guidelines](https://github.com/elsonidoq/skills/blob/5088b25877467887dd41c9547197c6da43b3c165/memory/coordination/GUIDELINES.md) have no approved guidance;
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
content. No migration is needed. Within-approved-scope corrections under existing repair
authority are verified focused repairs, not automatic replanning or rollback/discard of
valid checkpoints; file ownership still applies. Genuinely new scope or acceptance changes
renew affected producing review and approval. Missing authority/evidence blocks reliance.

**A1 — Executable local readiness.** Before dependent product implementation dispatch,
establish or reuse the smallest applicable actual proof that the assigned workspace can
execute its first required local check. An authorized bounded setup/readiness assignment
may establish this proof; the parent need not personally provision every environment.
Dependent product implementation waits for sufficient proof. One applicable first-check
result may cover multiple tasks without per-task repeats. Authorization is not availability;
a dependency directory is not an installed usable dependency; a client is not a runnable required server; reusable
packages do not establish writable-cache isolation. Inspect the actual loader/tool write
location and current applicable guard branch, not a historical adjacent guard. Proof is
reusable only for applicable workspace, versions, write conditions and check. Readiness
covers only capabilities exercised or otherwise established; newly encountered dependencies
need bounded readiness checks, not another full preflight or assumed first-check coverage.
Already-authorized bounded local setup needs no redundant permission request; destructive,
ownership, network and external-operation boundaries still apply. Missing permission
stops the affected setup; missing capability stops affected dispatch with the exact gap.
No mandatory install, provider probe or exhaustive environment audit is implied.

Observable: finite positive/reuse and negative cases distinguish authorized-but-unusable,
directory-only, client-only, cache-write mismatch, parent-versus-assigned workspace and
historical-versus-current guard. Applicable execution evidence records check/outcome and
context; a declaration alone cannot release dependent product implementation. A minimal
setup-to-implementation scenario distinguishes permitted readiness work from blocked
product work and demonstrates shared applicable proof. These are offline cases, not
execution against an external project.

**A2 — Smallest composed acceptance where needed.** Planner and both task adapters must
identify a genuine risky boundary that separate green components cannot establish, and
require the smallest composed check that observes it. Illustrative examples are
serialization through storage limits, primary input/error custody through cleanup,
sanitization before the first durable write, and transport arguments through wrappers;
these are not four mandated toy systems or a future-project matrix. Assert the final
observable/order/custody, not only each helper's green test. Apply the existing
[early-risk ordering](../../skills/planner/references/early-risk-reduction.md#produce-a-minimal-executable-reference)
at the earliest practical risky producer/consumer boundary, blocking downstream reliance
until proof exists. This is not an all-seams-before-coding rule or a duplicate prototype.
Reuse a focused existing check that already establishes the contract; preserve necessary
security/durability checks without a Cartesian matrix or blanket integration programme.

Observable: the smallest representative offline fixture set covers distinct decision rules,
combining cases where meaningful: isolated components can be green while composition fails,
and corrected composition passes. A negative control keeps already-observed wiring bounded.
Both adapters position the risky proof at the earliest practical boundary with blocked
reliance, carrying criterion, smallest check, expected proof, dependencies and gates;
no executor-defined weaker acceptance.

**A3 — Compact complete briefs and returns.** Use one canonical contract reference and keep
briefs source-bound, not transcript-bound. Inline the WHOLE APPLICABLE REQUIRED content
before coding, including complete criteria, checks, expected proof/pass conditions and
gates, not abbreviated criteria or pointers in their place. Retain scope and constraints;
avoid repeated contract reconstruction or rediscovery between healthy tasks. Safely batch
independent deterministic inspections/checks with attributable failures and preserved
dependency/permission boundaries; implementation writers/batches remain sequential.
Return changed outcomes, blockers and accessible proof, plus still-REQUIRED ordered
baseline/result SHAs and every item disposition. Record a shared command result once,
mapped to all covered items, rather than duplicating its output.

Observable: inspect a compact brief/return for the single canonical reference, full
applicable inline content, one shared result and all item/checkpoint mappings. Existing
shared-proof fixtures remain accepted; missing criteria, gates or accessible proof block
reliance. Minimal cases distinguish safe independent checks from dependent checks and
unsafe writes. No quota, writer cap, transcript forwarding or profile change is introduced.

**A4 — Applicable current proof, not generic green.** Choose affected checks from the changed
contract and current test collection; verify selectors actually reach current guards rather
than retired adjacent contracts. Distinguish proof reuse from inherited-failure comparison.
Reuse without rerunning requires unchanged pertinent bytes and applicable scope/environment.
Comparison may involve changed bytes: identify both revisions and relevant differences,
use equivalent selector, tool/environment and failure oracle, and observe the same failing
behavior before attributing it as inherited. Matching failure text alone is insufficient;
byte identity is not an automatic comparison prerequisite. Inherited failure may coexist
with a new regression or increased severity: compare relevant behavior/oracle and retain
both; baseline failure alone cannot dismiss changed behavior. Run checks on final bytes;
subsequent edits invalidate only affected proof. Rerun invalidated or contradicted items,
not all unchanged checks. A skip or old green is not new proof; missing REQUIRED evidence
blocks acceptance and dependent release.

Observable: minimal fixtures reject obsolete/empty selection, skip-as-pass, affected edits
as reusable proof and mismatched baseline attribution. They permit comparison with identified
changed bytes and equivalent observed failure, but reject matching text without an equivalent
oracle. Unchanged applicable proof and unaffected proof remain reusable. Reports distinguish
proven defect from insufficient evidence without relabeling either as success.

**A5 — Delivery-risk setup and event-driven recovery.** Separate materially delivery-threatening
unresolved setup from a large implementation assignment so it can be diagnosed without
burying the blocker in the whole batch; authorized setup/readiness work establishes A1
proof before dependent product work. Ordinary bounded ready setup needs no ceremonial split.
Concrete events include a worker-reported setup blocker, failed first check, runtime
attention/failure notification, or available progress event demonstrating blocked work.
On such an observed stall/failure inspect the actual invocation and available checkpoint/
proof now; do not wait for a full timeout just because budget remains. Silence alone is
not an observable stall. Without supported signals, early detection is not promised;
do not add polling, monitoring loops or thresholds. Narrow diagnosed missing work and
preserve verified checkpoints and applicable partial proof. Running children require
inspect/wait; unknown status/cause blocks replacement or blind retry. Resume suitable
retained context only with supported capability and existing authority.

Observable: a minimal event trace shows available blocker/failure evidence triggering
inspection without waiting for the full timeout, a narrowed handoff retaining SHA/item
proof, and no duplicate dispatch. A silence/no-signal control makes no early-detection
claim. Preserve unknown-cause retry and valid-work safeguards; healthy sequential tasks
continue without supervisor round trips.

**A6 — Routing and safety preservation.** Keep the existing six-factor rubric/profile rules
unchanged absent a demonstrated concrete gap returned through scope review. Preserve
independent family/effort justification, readiness versus suitability, exact owner selection,
Standard Sol/medium exception, permission/privacy boundaries, per-task commits and final
independent review. No historical failure implies model superiority or a new default.

Observable: existing routing, intake, state, ownership, union, acceptance and safe-repair
regressions remain green after authorized implementation; changed links resolve and
`git diff --check` passes. Static/symbolic results cannot be called live obedience or speedup.

## Verification, proof lifetime and handoff limits

Acceptance separates three claims: existing policy is preserved (relevant safety checks);
the actual changed instruction clearly expresses the missing decision rule (review the
changed spans); minimal offline scenarios demonstrate that the distinction is testable
(representative positive/negative observations). None establishes an enforcement fix,
live obedience or timing improvement. The critique did not inspect repository/harnesses
or reconstruct runtime; its acceptance corrections are adopted on their merits, not as
new historical timing evidence.

Early risk reduction uses existing focused contract/mutation and fixture checks, not a
duplicate prototype: no new library/runtime core warrants a disposable experiment. Before
instruction changes demonstrate meaningful failing checks for A1–A5 at the affected seams.
Scope mutation sensitivity proportionately; no exhaustive carrier-mutation programme or
general simulator. Retain safety tests. The present dirty tests supply baseline failures,
not sufficient acceptance by phrase insertion; pair focused instruction review with the
smallest realistic scenario set covering the distinct rules.

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

No material design question is deferred. This source correction does not edit the separate
tasks or grant implementation authority, combined approval or final implementation acceptance.
Runtime/enforcement limitations remain: instruction-managed checks cannot guarantee live agent compliance, child setup,
provider availability or measured improvement. Live evaluation requires separate authority
and usable capabilities; it is not scheduled as a mandatory probe by this source. The
owner-owned dirty batching test must remain untouched/uncommitted during source production.
