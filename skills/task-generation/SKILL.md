---
name: task-generation
description: Use when producing or reviewing dependency-aware implementation tasks from an approved source, specification, plan, or direct requirement.
---

# Task Generation

Produce complete, dependency-aware, independently verifiable implementation tasks. This
shared contract owns task semantics and validation; it does not select a workflow origin,
create a plan, or execute tasks.

## Preconditions and adapters

Apply [Parsimony and Actionable Checks](../planner/references/parsimony.md). Both direct and SpecKit adapters apply it to requirements, choices and checks.

Read repository instructions, the source and supporting artifacts, existing task format,
governing principles, and applicable project memory before tasking. Confirm authorization to
**prepare** tasks and that already-applicable upstream owner decisions and approvals apply to
the current content. Do not require final task/implementation approval before the producer
creates the task artifact. If a required source, preparation authorization, applicable upstream
approval, or capability is missing, report the missing evidence and stop rather than inventing
an artifact.

Apply the shared [project coordination contract](../memory-handling/references/project-coordination.md)
during initial understanding, including direct entry without planner: consult relevant existing
compact guidelines; missing store or STATE is nonblocking. Do not auto-initialize, persist
routine summaries/indexes, reflect, infer lessons or maintain STATE. Only explicit user
future-directed feedback authorizes bounded project-local guideline changes; ambiguity asks,
explanation-only/no feedback/no-write boundaries write nothing. Preserve local path/symlink,
sensitive-data and dirty/concurrent ownership safeguards. Carry exact applicable constraints
and evidence references through source observables → dependencies/REQUIRED checks → brief;
Verify a relevant decision reaches the dependency/check and runtime brief, not merely a link.
Never override source/owner authority. No default
history intake; explicit relevant retrieval is index-first where useful and retains uncertainty
on no match. Required gotcha-memory gates remain separate.

Optional residual-reasoning notes describe remaining inference, not an execution assignment or runtime routing.
Planning selection belongs to the [qualified seed rubric](../planner/references/profile-selection.md).
Execution uses the owner-selected configured binding without silent substitutions.

Use the adapter matching the producing workflow:

- A SpecKit adapter accepts planner's Standard specification/plan, first verifies the
  project's observed task-stage command and follows its instructions; unavailable required
  stage capability is a stop. Specification is requirements truth; approved plan is derived
  sequencing only. No SDD forwarding/rereading as direct requirements input. Trace source
  criteria into task checks. Governing instructions/contracts, memory and permission/safety
  still apply. Keep the stage create-only when its producer requires it: ordinary drafting,
  revision, shortening and mechanical validation of unsubmitted output are permitted within
  authorized scope, without a supervisor gate. Production does not substitute for independent
  review or authorize upstream requirement changes. Submitted defects follow the producing
  workflow's review/correction route.
- A direct adapter derives tasks from an owner-authorized durable TinySpec or legacy
  requirement/source and does not
  require a plan or SpecKit; final approval follows the produced-artifact review. TinySpec/
  legacy source is requirements truth. No SDD forwarding/rereading as direct requirements
  input. Trace source criteria into task checks. Governing instructions/contracts, memory
  and permission/safety still apply.

New TinySpec work always has a separate source and tasks file. Reference source sections
or acceptance criteria; put work-unit outcomes and task-specific checks in tasks, not a
copy of the entire source. Existing task-embedded requirements remain valid for legacy
work. The same task semantics apply to both adapters; no depth-specific execution schema.

For either adapter, verify Python 3 before relying on the bundled validator. If unavailable
or the task format is incompatible, manually inspect explicit dependencies, ordering,
dependency references, cycles, implicit producers, and stage feasibility, and report scripted validation
as unavailable.

## Executor guidance

Use the owner's selected executor and effort when tailoring useful implementation guidance.
Do not silently substitute a different model. Executor settings belong to the actual runtime
configuration, not task eligibility metadata: no execution-intent resolution, compatible-binding
assessment or provenance receipt is required in tasks. Historical optional context may remain.

## Task contract

Read and apply [early risk reduction](../planner/references/early-risk-reduction.md);
verify it is readable or stop with a missing-install report. Both adapters and direct entry
apply it without assuming planner already did. Planning schedules proofs, not execution
without separate authority. Known bounded behavior normally uses permanent actual-helper
tests or a verified earlier step inside its delivery task; do not add a prototype task when
that proof suffices. Select a disposable experiment only for a genuinely unknown consequential
behavior, to answer ONE consequential question before costly reliance. If selected, use existing
task fields to scope its informational conclusion/limits, with both script code and actual
observed execution evidence; the shared owner defines the complete evidence, applicability and
lifetime contract. Both the direct and SpecKit adapters mark the task title **[PROTOTYPE]** (or an
explicit equivalent only for an incompatible observed format) and carry its bounded
informational scope through the task handoff and worker brief. Only an independently necessary
prerequisite becomes an earlier task; otherwise verify before reliance inside the same task.
Consumers use applicable findings and preserve behavior with permanent production acceptance
tests. Failed or unrun evidence cannot release assumed reliance; retain limits, correct/replan
and renew affected existing approvals rather than label a failed technique proven.

A task delivers an independently verifiable outcome, not a phase label. Separate tasks only
for a concrete independently necessary deliverable, prerequisite, gate, resource boundary or
material context incompatibility. Test writing/running, evidence, verification, review
preparation and routine teardown normally stay inside that outcome. Do not split by a workflow
noun or task-count quota; preserve real dependencies and gates rather than mechanically merging
independent work.

State shared constraints once in their authoritative context. Task entries contain
outcome-specific scope, interfaces, acceptance and verification, not repeated specification
prose or administrative reports. Keep the human document a concise presentation, not a prose
copy of machine authorization metadata. Keep task-specific work and useful checks clear.

Before declaring a technical blocker, verify the exact affected operation and its enforced
limit at the consuming interface. A worker file-tool bound is not a task-contract loader bound;
do not impose a universal artifact size limit. Distinguish owner-requested behavior, verified
runtime restrictions and agent-selected design choices in existing task fields. An inference
or agreement to a narrowly explained remedy must not become a broader owner requirement.

Each task needs an ID and work description. Include dependencies when work needs a producer.
Likely files, interfaces, acceptance checks and shared context are useful optional details. Cover all in-scope work, integration/acceptance checks, and
lockstep documentation whose evidence compares documentation with implemented behavior.
Record exclusions so tasking cannot reintroduce them.

Use practical observables, not generic green output: an ordinary wiring task might require
`T001/V1`: the selected ID reaches the consumer unchanged, checked by the existing argument
fixture with its captured ID as evidence; local permission, no special manual gate. Both adapters
carry these same item mappings through handoff. A representative-sample manual STOP belongs
only to tasks whose actual risk/source requires explicit user approval before downstream/full
expensive operation; do not invent that ceremony for ordinary tasks.

When separate green components cannot establish a genuine risky boundary, require the
smallest composed check that observes the final observable, order or custody—not just
helper outputs. Reuse an existing focused check that already observes the boundary;
ordinary observed wiring needs no extra integration programme. Preserve necessary security
and durability checks. This check does not itself require a separate task: use an earlier
producer only when an independently necessary prerequisite is evidenced, otherwise verify
before reliance inside the same delivery. Block reliance on insufficient or invalidated proof,
not unrelated seams or a duplicate prototype.

Use the smallest relevant project check that observes the changed behavior. Check commands
are optional task context, not mandatory universal acceptance items or collection-count receipts.
When a check is specified, run it after the relevant work and report its real outcome. Missing
or failed checks are not passes. Keep owner-required checks and actual permission boundaries;
do not impose generic acceptance boilerplate or manual gates on ordinary coding.

## Structured executable handoff (both adapters)

For executable intake, emit JSON or YAML as a task list or an object containing `tasks`.
Each task has a nonempty string `id` and `outcome` (or `description`). Optional `depends`
is a list of task IDs. IDs must be unique, references must exist, and dependencies must
not cycle. File order and ID numbering do not determine execution order.

Example:

```json
[
  {"id": "test-title", "outcome": "Test the corrected title", "depends": ["fix-title"]},
  {"id": "fix-title", "outcome": "Correct the settings page title"}
]
```

These are the entire six startup linter checks: readable input, JSON/YAML task list,
ID/work description, unique IDs, existing dependencies, and no cycles. Empty lists mean
no work and reserve/launch nothing. No required order, context group, source hashes,
approvals, execution intent, envelopes, gates, oracle mappings or model assessments.
Do not regenerate old tasks solely to remove metadata: useful optional context remains valid.

Optional `owned_paths` restricts file mutation when provided. Without it, the runner claims
only clean, unchanged paths immediately before actual tool edits; it does not adopt dirty
files or stage arbitrary post-run changes. Useful existing `required` check mappings are
still consumed if supplied; they are not universally required. Sources may be context, not
content-pinned execution authority. Keep actual external action permission at that action.

Markdown may remain a human presentation. `check-task-order.py` also checks its IDs,
descriptions and dependency graph; no contiguous numbering or story-group constraints.

## Review and handoff

For a [PROTOTYPE] task, preserve the marker and bounded informational
scope in the handoff and worker brief. Reuse unchanged applicable proof once with all mappings;
keep routine teardown inside its task. A separate cleanup task needs an
actual independently consequential resource or outcome.

Review selection/omission, real-runtime evidence, applicable dependencies, proof lifetime,
production acceptance, disproof/renewal and feasibility through both adapters/direct entry.
Challenge redundant task splits, duplicate proofs/report chains and disproportionate checks
without weakening acceptance or original gates. Return only necessary producer/consumer
dependencies, applicable evidence/limits and blocked reliance to the existing producing review
and coordinator handoff; syntax/order validation alone cannot prove consumption.

Carry work-specific checks, exclusions and genuinely material permission boundaries into
the worker brief. Verify the dependency graph with
`python3 scripts/check-task-order.py /path/to/tasks.json` from this skill directory (YAML
and Markdown are also supported). Manually inspect relevant scope and feasibility; do not
turn that review into additional executable intake metadata. A direct owner coding request
does not require a new planning or approval cycle. Historical source/task documents remain
unchanged unless the owner requests their revision.

## Mandatory task checkpoint

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md). An authorized task-list production is a retained bounded deliverable and checkpoints before combined artifact approval; preserve source approval and dependency semantics while checkpointing it separately.
