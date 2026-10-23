# Early isolated technical risk reduction — TinySpec

## Authority, context and outcome

Owner request in the 2026-10-07 planning session is the source provenance: modify
planning skills to **selectively schedule early technical risk-reduction implementation
tasks**, not merely validate assumptions while planning. Beneficiaries are owners and
executors whose integration work would otherwise depend on an untested hard core.
Owner selected **TinySpec** and authorized source, separate tasks and planner-owned
review only, using **openai-codex/gpt-6.1-sol / medium** for all three stages.
`NO_BRAINSTORM_NEEDED`: detailed direction, exclusions and A–E scenarios are settled;
remaining placement and task mechanics are answerable by repository inspection.
Combined current-content owner approval is pending. This source does not authorize
implementation, proof execution, live tests, installation or policy changes.

## Scope and exclusions

Include one portable shared reference, likely
`skills/planner/references/early-risk-reduction.md`, applied through operational sections
of planner, TinySpec, delegating architectural planning and task generation; their
review/handoff obligations; focused existing checker/mutation/adapter fixtures; and
the planner regression guide. Preserve existing task syntax and dependencies, managed
TinySpec/Standard workflows, direct/standalone adapters and all affected approval gates.

Exclude runtime extensions, settings, production code, provider/model tests, new external
dependencies, global/project policy or memory-guideline changes, compulsory spikes,
new task schemas, research engines and extra approval stages. Existing local SpecKit
assets are inspected for compatibility only; they are not targets or TinySpec prerequisites.
No separate Epic, research/design chain or mandatory prototype per task.

## Inspected basis and decisions

Repository-derived facts, verified at baseline
`63804165e0d9b285501daad65215ac9b0fadc33e`:

- [Planner](../../skills/planner/SKILL.md), “Proportionate validation” selects the actual
  seam, concrete failure and lowest sufficient checks; “TinySpec path” owns combined
  source/task review; Standard retains independent overall review. Extend these actual
  carriers, not a summary-only mention. New proof work remains scheduled implementation.
- [TinySpec](../../skills/tiny-spec/SKILL.md), “Compact source contract” already carries
  approach, producer/consumer sequencing and acceptance; “Boundary and return” forbids
  an embedded task checklist. Carry selection rationale and proof needs here; leave work
  units in separate tasks.
- [Architectural helper](../../skills/delegating-architectural-planning/SKILL.md),
  “Planner Boundary” prohibits product-code implementation and requires sequencing and
  verification; its managed Standard adapter and standalone entry retain their gates.
- [Task generation](../../skills/task-generation/SKILL.md), “Task contract” requires
  explicit earlier prerequisites and REQUIRED criterion/check/evidence/gates;
  “Review and handoff” checks implicit producers and returns inadequate contracts to
  producing review/renewal. Reuse these fields for proof production, consumption and cleanup.
- [Checker](../../scripts/check-planner-workflow.py) loads shared owners and validates
  operational sections and resolved links. [Tests](../../scripts/test-planner-workflow.py)
  already use named removal mutations, summary-only negatives and isolated link fixtures.
  [Adapter examples](../../scripts/fixtures/planner/tiny-tasks.md) and
  [Standard examples](../../scripts/fixtures/planner/standard-tasks.md) use numbered
  Markdown with explicit `Depends`; the existing task-order validator checks syntax/order,
  not semantic proof consumption.
- Local `.specify/templates/plan-template.md` describes architecture/technical context;
  `.specify/templates/tasks-template.md` demonstrates story task sequencing. Preserve the
  observed SpecKit workflow, while the shared task contract supplies explicit dependencies
  and required verification; do not adopt template parallel/group-commit examples as policy.
- [Regression guide](planner-regression.md) distinguishes offline contract sensitivity
  from runtime obedience. No existing generic green test proves the requested behavior.

Research skip: this change defines instruction/task semantics, not new external dependency
behavior. Adequate local owners above determine integration; no internet/library research
or live capability is needed. Future proofs that exercise a real dependency still carry
version/runtime applicability under the existing
[dependency research contract](../../skills/planner/references/dependency-research.md).
`memory/MEMORY.md` has no gotchas; coordination guidelines contain no approved guidance.
No historical run summaries were read. There are no owner deferrals or open material choices.

## Approach and behavioral contract

**R1 — Select on leverage, not ceremony.** During authorized planning, assess whether
one disproportionate technically uncertain/difficult core drives downstream risk and can
be cheaply isolated with a meaningful executable oracle. If so, schedule an early,
independently verifiable implementation producer before integration/plumbing that assumes
its success. State the concrete risk and expected value relative to effort. If ordinary
inspection/documentation answers an easy name/type/method question, do that; do not manufacture
a trivial script. If the uncertainty is only observable in a whole environment, plan the
appropriate real-system validation at the earliest feasible seam and its actual prerequisites,
not a forced standalone prototype. No arbitrary cost threshold or universal spike mandate.
Planning may inspect existing evidence but may not execute these implementation proofs
without separate execution authorization.

**R2 — Small executable producer.** Selected proof work builds the smallest disposable
script, minimal program, test or benchmark that actually exercises the hard behavior,
using the real dependency/runtime/version where relevant rather than a mock that cannot
observe it. Bound inputs/outputs and representative plus adversarial cases to the actual
risk, with explicit objective success/failure criteria, commands, expected evidence and
capability/permission gates. Do not build production plumbing or an exhaustive matrix.
Record what was tested, runtime/dependency applicability, observations and limitations;
missing/unrun evidence is NOT VERIFIED, not a pass. A passing experiment establishes only
its tested bounds, not general production correctness.

**R3 — Proof has a consumer and lifetime.** Retain artifact, reproducible commands and
findings until downstream production work has an explicit dependency on the producer and
must inspect, run or use the proof. Consumer acceptance demonstrates preservation of the
proven behavior in the production implementation, not merely links a report. Plan production
tests covering that transfer and remaining integration risks, then cleanup of disposable
material only after consumption and production validation; preserve reproducible evidence
and findings in the established evidence owner. No fixed global artifact directory. Multiple
consumers retain proof until all applicable consumers satisfy this boundary. Proof reuse
requires still-applicable revisions/environment; changes invalidate affected evidence.

**R4 — Disproof changes the plan.** Failed/adversarial results block downstream reliance
on the assumed approach. Retain observed failure, diagnose its bounds and feed results into
correction/replanning, affected consumers and existing producing review/approval renewal
when source/specification, scope, acceptance or dependencies change. A failed technique is
never labelled proven; a later correction cannot erase the failed attempt. Missing capability
or permission is an evidence gap, not technical disproof. No blind retries, automatic
approval, weaker post-hoc criteria or new standalone experiment-approval workflow.

**R5 — Operational coverage and compatibility.** One shared owner is linked and applied
by all four skills in the executing sections and their review/handoffs. Missing/unreadable
packaged reference stops affected planning with a missing-install report. Planner review
checks justified selection/omission, executable proof criteria, explicit consumption,
lifetime/cleanup, failure routing and feasibility through both paths. TinySpec carries
what/how and required evidence without task checklist; Standard/helper plans carry sequencing
and verification without replacing installed task production. Direct TinySpec, direct tasking,
and standalone helper cannot assume planner already applied the contract or granted execution.
Existing approvals, task numbering/fields, depth/model routing, mandatory task/evidence
checkpoints and coordinator release gates remain unchanged.

## Acceptance and validation

| ID | Observable criterion and smallest sufficient evidence |
| --- | --- |
| AC1 | R1–R5 are carried by the shared reference and all four operational consumers/reviews; resolved-link and carrier-removal tests fail for missing/misplaced obligations, including summary-only replacements. |
| AC2 / A | Easy method-name scenario resolves by inspected documentation; no executable spike is scheduled solely to print names/types. Bounded labelled walkthrough plus contract mutation distinguishes it from a real semantic core. |
| AC3 / B | Subtle real-library core schedules early tested proof using real dependency/runtime with explicit criteria; dependent production task consumes retained proof and verifies behavior transfer before cleanup. Offline fixture demonstrates task shape only; no actual library claim. |
| AC4 / C | Difficult transformation schedules a minimal executable representative/adversarial proof before integration plumbing. Producer/consumer ordering and semantic consumption are inspected, not inferred from parser success. |
| AC5 / D | Only-whole-environment risk plans the required real-system check and its prerequisites/gates without forced isolated script; unrun/unavailable check remains NOT VERIFIED. |
| AC6 / E | Disproof retains observed results, blocks assumed downstream approach, changes downstream plan via correction/replanning and renews affected existing approvals as needed; failed technique cannot be presented as proven. |
| AC7 | Existing TinySpec and Standard fixtures still validate; new fixtures use the same task schema and explicit earlier dependencies. Direct/standalone links, preparation/execution boundaries and approval gates remain intact. |
| AC8 | Regression guide accurately maps A–E and named offline tests to implemented contracts; static/fixture PASS never claims live-agent or real-library proof. Separately gated live tests remain NOT RUN. |

Use existing Python checker/tests and adapter/task-order fixtures; add bounded regressions
rather than new infrastructure or production experiment scripts for this instruction change.
Test clause removals/wrong links/early cleanup/no dependency/disproof-as-success and whole
carrier deletion with summary words intact where these expose the changed seam. Preserve
all existing safety regressions. Required suite lint and relevant shared task units complement
focused checks, because the contract is coupled across four consumers. Manual semantic review
must inspect A–E, real-executable versus trivial/mock substitutions, producer-to-consumer
transfer and failure routing. No live/provider operation is authorized by this validation plan.

## Risk and execution notes

The weakest oracle is model obedience: static clauses and synthetic fixture walkthroughs
cannot establish actual behavior. Report that limitation rather than add unauthorized live
runs. Multi-consumer drift is addressed by one linked owner, scoped sensitivity checks and
manual review. Instruction edits are reversible by authorized correction; no migration,
deployment or production rollback is required. Future global skill changes require `/reload`
in pi; planning-artifact production alone does not change installed skills.

Source and separate tasks are independently verified retained deliverables with focused
commits and distinct factual evidence checkpoints. Their digests and planner-owned review
belong in [this run's SUMMARY](https://github.com/elsonidoq/skills/blob/5088b25877467887dd41c9547197c6da43b3c165/memory/coordination/evidence/2026-10-07-early-risk-reduction/SUMMARY.md),
not recursive hashes here. Combined owner approval remains required before implementation.
