---
name: delegating-architectural-planning
description: Use when an owner-approved specification needs delegated architectural planning through an installed SpecKit planning capability.
---

# Delegating Architectural Planning

Arrange one delegated SpecKit planning pass from an approved specification and the owner's
request for a plan. The coordinating caller supplies authority and handles owner decisions;
the delegated producer reviews the specification, creates the plan and checks its outputs.
Return that plan and its evidence to the caller, not implementation or a task breakdown.

## Arrange the bounded planning pass

Read the approved specification and approval evidence, repository instructions, governing
principles, relevant contracts, existing architecture and upstream/downstream dependencies.
Establish the intended plan location and allowed artifact writes from actual project paths.
Standalone entry must verify equivalent Standard planning/preparation authority; invocation
alone grants none.

Before affected planning, use [Memory Handling](../memory-handling/SKILL.md) for relevant explicit
owner guidance and gotchas from the verified unified index. Missing optional memory or STATE
is nonblocking; retain that owner's retrieval, write and concurrency safeguards. In fresh or
resumed, managed or standalone entry, consult
[save-adr](../save-adr/SKILL.md#consult-and-propagate) for current accepted outcomes, explicit
mechanism constraints and source links. Carry them into the producer brief and return; verify
their effect on architectural decisions and observables, not merely their presence as links.
Preserve dependency/gate and check needs for task-local REQUIRED checks and worker/reviewer
briefs downstream. Source/owner authority remains binding; conflicting accepted authority or
uncertain applicability stops only affected work through the existing decision/renewal gate.

Inspect the project's installed SpecKit planning command or skill, invocation instructions,
template, prerequisite scripts and expected output paths. Verify it is usable in the delegated
context. If not, report `SpecKit planning: UNAVAILABLE` and stop; do not write a generic plan or
claim the stage ran. Use its supported interface, not a shell simulation of a slash command.

Verify an allowed delegation tool and a configured planning-capable agent under
[runtime requirements](../../REQUIREMENTS.md). Never invent an agent, model, command or
configuration. Missing, unusable or unauthorized delegation stops the pass; no local fallback.

Before dispatch in managed and standalone entry, give the fresh producer brief the
already-discovered inputs: approved specification and approval evidence, repository
instruction/principle/contract paths, architecture decisions and dependencies, intended plan
location, allowed writes and prohibited operations, research results and gaps, and the observed
SpecKit command or skill, invocation instructions, template, prerequisite scripts and expected
output paths. Reuse this input package; do not repeat discovery or create a separate artifact.

<a id="planner-standard-adapter-contract"></a>

For planner-managed Standard `plan_create`, the caller supplies the resolved
`standard-plan-helper` saved assignment under the planner's
[saved-assignment contract](../planner/SKILL.md#saved-planner-assignments). Use the suite-owned
`coherence-producer` in a separate fresh bounded context for the entire pass. Carry the exact
binding unchanged in brief and dispatch, and verify it is permitted and callable at dispatch.
If invalid or unavailable, return the contract's focused owner-correction question; do not
substitute or run a local pass. Record observed binding/effort separately; unknown stays unknown.
The coordinating caller does not author fresh artifacts or make substantive repairs. Direct
mechanical fixes use the [bounded mechanical correction contract](../planner/references/approval-and-recovery.md#bounded-mechanical-corrections)
and its equivalence result; uncertain or substantive corrections return to suitable originating
producer context or a fresh bounded correction delegate.

The producer may write only the detected SpecKit artifacts and authorized specification
corrections. Canonical research-document and necessary discovery-link writes need additional
explicit bounded permission: observed destinations, allowed changes and prohibited operations.
Re-read targets and preserve unrelated content. This pass grants no arbitrary documentation or
product-code edits, product-scope change, implementation, push, further delegation, or unrelated
paid/live/deployment/release operations. Required write authority cannot be inferred from tooling.

## Resolve architectural choices from evidence

Before consequential architecture/plan decisions, apply the
[dependency research contract](../planner/references/dependency-research.md). Use local dependency
and version evidence, reusable guidance, inspected supporting spans and usable permitted research
capabilities from the caller or verify them locally. Consume its reuse/skip/refresh result and
classify documented recommendations, repository-derived decisions/rationale and assumptions with
defined checks. Translate evidence into plan constraints and observable verification. Persist
required reusable guidance in the discovered technical owner/index within the write bounds above
before readiness; this applies to standalone production too.

If required tools, evidence, versions or write permission are missing, stop affected design and
return exact gaps, affected decisions and needed authority. The caller or standalone owner must
resolve any explicit bounded deferral, with impact, allowed bounds and outstanding validation.
No recollection-based completion or automatic deferral is permitted.

Apply [early risk reduction](../planner/references/early-risk-reduction.md) to sequencing and
verification. Consume its justified proof selection/omission, necessary dependencies, applicability,
reuse/lifetime, production acceptance and disproof/renewal results. Known bounded behavior can use
actual-helper tests; consequential unknowns need the contract's appropriate proof and real gates.
Failed or unrun proof cannot release assumed reliance. Planning schedules proof, not its execution.
Verify both references are readable before use; missing packaging stops affected planning with a
missing-install report. Do not assume the caller already applied them on standalone entry.

Use [Parsimony and Actionable Checks](../planner/references/parsimony.md) for approach and review
in either entry mode. Tailor useful implementation guidance to the owner's selected coding model
and effort, not a producer/reviewer substitute or universal model ranking. Name interfaces,
invariants, non-obvious decisions and edge cases; state what is bounded, what remains open and
what is uncertain. Do not shrink required acceptance, dependencies, safety or approval gates.
Task-generation owns decomposition and task sizing; planning bindings do not select runtime ones.

## Produce and inspect the plan

The specification is requirements truth; the plan provides derived architecture and sequencing.
Do not forward or reread SDD as direct requirements input. Governing instructions, memory and
actual permission/safety boundaries still apply. In one same-session pass:

1. Review/fix the approved specification within authorized bounds. Record unambiguous clerical
   corrections. Changes to approved specification content, including research-driven changes,
   return through the caller's renewed specification approval gate before leaving the affected
   stage; standalone entry uses its owner gate. Apply the mechanical-equivalence exception only
   under its canonical contract, never by assuming approval.
2. Run the detected SpecKit planning capability once to create the plan. Supplement its outputs
   with architecture, contracts, relevant interfaces/files (or discovery steps), sequencing,
   dependencies, parallel-safety constraints and integration points. Include verification with
   fail-then-pass checks for behavior changes and evidence-to-constraint-to-check mappings;
   relevant security/privacy, migration/rollback and authorization gates; documentation scope
   and specialized implementation capabilities.
3. Review/fix the produced plan against the approved source, write bounds and evidence rules
   above. Verify the installed stage actually ran, inspect its outputs and shared-link resolution,
   and retain actual evidence and limits. Do not direct the caller to create the plan again.

For a material product, architecture, privacy, permission, irreversible or paid-operation choice,
stop that branch and return:

```text
NEEDS_OWNER_DECISION
Question: ...
Why it blocks: ...
Affected plan sections: ...
Options: ...
Recommendation: ...
```

The caller obtains the answer and resumes the same planning context when supported. Do not
invent a ruling. A future live operation can be an explicit authorization gate rather than a
planning blocker, unless its required runtime policy is undefined.

## Return the checked outputs

Return the plan path and content evidence, architecture/dependency summary, capability needs,
corrections, accepted constraints and source links, open decisions and explicit deferral bounds.
Include the research/risk results above, supporting spans, canonical owner/discovery locations,
verification needs and remaining capability/permission gaps. These feed the caller's review
and [task-generation](../task-generation/SKILL.md) with applicable guidelines and observable checks;
leave implementation task breakdown to the SpecKit tasks stage, not an embedded task chain.

Checkpoint verified, already-authorized retained planning/adaptation outputs before completion
or handoff under the shared [task-commit contract](../memory-handling/references/task-commit-contract.md).
This grants no new write or adaptation authority. Stop after planning; implementation requires
owner approval.
