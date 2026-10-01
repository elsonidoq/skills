---
name: requirements-manager
description: Use when a detailed requirement or selected source needs reviewed, dependency-aware tasks without an intermediate specification or plan.
---

# Requirements Manager

Turn a sufficiently detailed, owner-authorized requirement into reviewed tasks and an
implementation handoff. This is a lightweight producer: it preserves evidence and owner
gates but does not create an intermediate specification or plan.

## Preconditions and route decision

Read repository instructions, the detailed prompt or explicitly selected source, related
artifacts and evidence, governing principles, and applicable project memory before
assessing the work. Use the project's established artifact format and locations; do not
assume paths or create a state schema. Treat source claims as claims: retain citations and
mark unverified claims rather than inventing facts.

Use the sizing guidance in [`../../docs/best_practices_spec_driven_development.md`](../../docs/best_practices_spec_driven_development.md)
to decide whether the lightweight route fits. If this distributed reference is missing, stop
with a missing-install report rather than substituting guidance. If scope
justifies an EPIC, explain the observed sizing evidence and obtain the owner's route
decision; do not silently reroute. Preserve an explicit documentation-initialization
exception when the detected workflow requires an EPIC. Resolve mechanically answerable
details, but stop for a material product, architecture, privacy, permission, cost, or
irreversible decision until the owner decides.

Before proceeding, verify that usable question, applicable memory, and owner-selected
class bindings are available where this workflow needs them. Verify discoverable shared
skills `epic-brainstorming` and `task-generation`, plus `coordinate-implementation` for
the eventual handoff. If a required capability or skill is unavailable, report the missing
capability and stop; do not replace it with guessed decisions or a local substitute.

## 1. Preserve the requirement

Capture the current requirement durably in an existing source or decision artifact, or in
the task artifact when no separate source is established. Record its scope, acceptance
criteria, exclusions, constraints, source evidence, settled decisions, open material
questions, and deferrals. This preservation is not a design phase. No intermediate
specification or plan is created.

Record enough content or revision evidence to compare the requirement and tasks with later
approval. If the source, decisions, or tasks change materially after review, treat approval
as stale and return to the affected review and owner-approval step.

## 2. Resolve only material uncertainty

Invoke the shared `epic-brainstorming` mechanism with the durable requirement/task artifact
as its bounded source and direct task readiness as its target. Follow its capability
preflight, exact gate result, owner-owned one-at-a-time dialogue, decision application,
deferral, and resume rules. A settled, well-specified requirement skips brainstorming; it
does not skip review or authorization. Do not fork the shared mechanism or invoke generic
brainstorming in its place.

## 3. Produce direct tasks

Use the `task-generation` direct adapter to generate tasks from the durable requirement.
It does not require a plan or SpecKit. Supply authorization to **prepare** tasks and any
already-applicable upstream approvals; do not require final requirement/task implementation
approval before the producer has created the artifact. Apply its full task contract, explicit dependency
validation, documentation/integration/acceptance coverage, class-share rule, and manual
traceability review. Organize consecutive same-class work context-coherently without
reordering prerequisites or padding with distant tasks; retain individual acceptance
evidence and record shared context and producer/integration checkpoints.

Derive documentation scope from the requirement and inspected affected changes, not from a
missing plan. Return a task-order or traceability defect to this manager's review gate;
never repair a forward dependency by silently reordering approved work.

## 4. Review and authorize

The approval order is: preserve/resolve the requirement, prepare tasks, review the produced
requirement-to-task evidence, then approve current requirement, tasks, and implementation
scope. This clarifies producer authorization without adding a gate.

Review requirement-to-task traceability, complete in-scope coverage, exclusions,
documentation, integration, acceptance evidence, ordering, implicit dependencies, model
class share, and unresolved or deferred owner decisions. Record the review result and the
current content/revision evidence in durable artifacts.

Obtain explicit current owner approval of the requirement, tasks, and implementation scope.
A chat-only approval or an `approved` label without durable content evidence is insufficient
for a fresh-session handoff. Missing, stale or unverifiable approval stops; return the defect
to this manager's review gate and renew the affected approval after correction.

## 5. Handoff

Hand off explicit locations for the durable requirement/source, task list, review evidence,
owner approval, decisions/deferrals, and applicable supporting artifacts to
`coordinate-implementation`. State the workflow origin as `requirements-manager`. The
coordinator alone selects execution strategy, verifies its own capability preflight, and
revalidates current approvals; this manager does not select models, batches, or fabricate
SpecKit artifacts.

If the owner requested execution in the same session, provide the same complete handoff
before invoking the coordinator. Otherwise provide concise fresh-session context: settled
scope and decisions, deferrals, source/task/review/approval locations and revisions,
validation outcomes, and unresolved blockers. Report readiness for implementation, not
feature acceptance.

## Maintaining this contract

With Python 3 available, run `python3 scripts/test_contract.py` from this skill directory.
It checks explicit static workflow wording, not runtime model obedience. If Python is
unavailable, report the check `UNAVAILABLE` and manually inspect the contract; do not claim
automated validation passed.
