---
name: task-generation
description: Use when producing or reviewing dependency-aware implementation tasks from an approved source, specification, plan, or direct requirement.
---

# Task Generation

Turn authoritative requirements into independent, executor-sized implementation tasks.
Read the source and selected executor, decompose and verify the task boundaries, then return
human tasks, an executable handoff and material risks to the producing review/coordinator.
This contract owns task semantics, not workflow selection, planning or execution.

## Preconditions and adapters

Apply [Parsimony and Actionable Checks](../planner/references/parsimony.md). Both direct and SpecKit adapters apply it to requirements, choices and checks.

Read repository instructions, the source and supporting artifacts, existing task format,
governing principles, and applicable project memory before tasking. Confirm authorization to
**prepare** tasks and that already-applicable upstream owner decisions and approvals apply to
the current content. Do not require final task/implementation approval before the producer
creates the task artifact. If a required source, preparation authorization, applicable upstream
approval, or capability is missing, report the missing evidence and stop rather than inventing
an artifact.

For both adapters, including direct entry without planner, apply these common inputs on
direct entry and fresh/resumed production. Verify the linked owners are readable; missing
required guidance stops the affected mapping with a missing-install report:

- Use [Memory Handling](../memory-handling/SKILL.md) to retrieve relevant guidance from the
  verified unified index. Missing optional storage or STATE is nonblocking; do not initialize
  storage or perform routine persistence, default history intake or execution-time feedback routing.
- Apply [save-adr](../save-adr/SKILL.md)'s consult/propagate contract to re-establish relevant
  accepted authority and current supersession. Carry applicable accepted constraints and
  explicit owner guidance, alongside gotchas, through source observables → dependencies or
  gates → task-local REQUIRED checks → worker/reviewer briefs, with source links. Each
  relevant decision must affect the task's dependency or gate, task-local REQUIRED check and
  worker brief, not merely a link. A source/task conflict or uncertain current supersession
  stops only the affected task mapping; required gotcha-memory gates remain separate.
- Trace source criteria into task checks. Source criteria are requirements truth; a plan
  supplies derived sequencing only. No SDD forwarding/rereading as direct requirements input.
  Governing instructions, memory and permission/safety constraints apply throughout.

Use the adapter matching the producing workflow:

- A SpecKit adapter accepts planner's Standard specification/plan. Verify the project's
  observed task-stage command and follow its instructions; unavailable required stage
  capability is a stop. Specification is requirements truth; approved plan is derived
  sequencing only. Keep the stage create-only when its producer requires it. Authorized
  drafting, revision, shortening and mechanical validation of unsubmitted output need no
  supervisor gate. Submitted defects follow the producing workflow's review/correction route.
- A direct adapter accepts an owner-authorized durable TinySpec or legacy requirement/source;
  it does not require a plan or SpecKit. TinySpec/legacy source is requirements truth.
  Final approval follows produced-artifact review.

Production does not substitute for independent review or authorize upstream requirement changes.

Carry the associated qualified issue URL from the source or planner brief into the human tasks
and executable handoff as optional top-level `delivery_issue`, and into the coordinator handoff.
Do not create an issue prerequisite or require it for bare task lists; tracker operations follow
[track-open-issue](../track-open-issue/SKILL.md) and their actual authority.

New TinySpec work always has a separate source and tasks file. Reference source sections
or acceptance criteria; put work-unit outcomes and task-specific checks in tasks, not a
copy of the entire source. Existing task-embedded requirements remain valid for legacy
work. The same task semantics apply to both adapters; no depth-specific execution schema.

For either adapter, verify Python 3 before relying on the bundled validator. If unavailable
or the task format is incompatible, manually inspect explicit dependencies, ordering,
dependency references, cycles, implicit producers, and stage feasibility, and report scripted validation
as unavailable.

## Executor guidance

Use the exact absolute executor path already resolved by the coordinator/planner; do not search
again. On standalone entry without a resolved path, run
`python3 scripts/resolve-workflow-executor.py --project PROJECT_ROOT` from the suite checkout
([resolver](../../scripts/resolve-workflow-executor.py)); add `--executor PATH` only for an explicit
override. Relative overrides are project-root-relative; otherwise only
`PROJECT_ROOT/.pi/workflow-executor.json` is selected. Pass the resulting absolute path unchanged
in downstream briefs/handoffs. Never search neighboring repositories, home directories, other
worktrees or historical tasks, fall back after a failed override, create/copy configuration,
authenticate providers, invoke models to resolve configuration or invent model/effort selections.

Before either adapter decomposes work, the producer itself must read the current project's selected
executor JSON at the exact path supplied in its brief. Use that JSON's valid worker model and effort
for bounded implementation guidance; do not use a planner/parent/producer profile, remembered
default, or a brief claim that the file was read. A present valid JSON needs no executor-selection
question.

If the path is missing, ambiguous or unreadable, or the worker model/effort is missing or invalid,
stop only the affected producer and ask the owner to resolve the affected role, path and problem.
Do not recommend, infer or silently substitute a model or effort. Executor settings belong to the
actual runtime configuration, not task eligibility metadata: no execution-intent resolution,
compatible-binding assessment or provenance receipt is required in tasks. Historical optional
context may remain. Reading configuration does not replace decomposition: retain concrete
interfaces, owned paths, earlier dependencies, local checks and real permission/manual gates.

## Task contract

Read and apply [early risk reduction](../planner/references/early-risk-reduction.md);
verify it is readable or stop with a missing-install report. Both adapters and direct entry
use its selection/omission, evidence, applicability/lifetime and disproof rules; do not assume
planner already did. Planning schedules proofs, not execution without separate authority.
Consume its findings as task dependencies, checks and blocked reliance, not report-only links.
Known bounded behavior uses permanent actual-helper tests or a verified step in its delivery.
For a genuinely unknown consequential behavior, select a disposable experiment only under that
owner's criteria. Both the direct and SpecKit adapters mark the task title **[PROTOTYPE]**
(or an explicit equivalent only for an incompatible observed format), and carry its bounded
informational scope into the handoff and worker brief. Only an independently necessary
prerequisite becomes an earlier task; otherwise verify before reliance inside the same task.
Consumers use applicable findings and keep permanent production acceptance tests. Failed or
unrun evidence cannot release assumed reliance; use the owner's correction/approval-renewal route.

A task delivers an independently verifiable outcome, not a phase label. Separate tasks only
for a concrete independently necessary deliverable, prerequisite, gate, resource boundary or
material context incompatibility. Test writing/running, evidence, verification, review
preparation and routine teardown normally stay inside that outcome. Do not split by a workflow
noun or task-count quota; preserve real dependencies and gates rather than mechanically merging
independent work.

### Executor-sized outcomes

A delivery milestone groups related capabilities; an execution task implements **one bounded
outcome** that can be verified and checkpointed before later work. A coherent milestone is
not automatically an executor-sized assignment, even when an advanced model could finish it.

During authoring and review:

1. Name the outcome, owned change paths, scope/exclusions, consumed interfaces and earlier
   producer dependencies. Inspect the acceptance selectors, coupled fixtures and admitting
   harness alongside the product interface, and inspect the final configuration/override owners
   that produce its final observable. Before a dependent relies on a producer fixture, inspect
   that fixture's applicable admitting/type check. Keep necessary in-scope support, final
   configuration/override ownership and applicable producer check with the bounded outcome, or
   name a genuinely necessary existing producer dependency. Give a concrete observable and the
   smallest sufficient verification; keep its ordinary tests, relevant docs and routine teardown
   with the outcome. Express these in the work description or existing fields, not new mandatory
   metadata.
2. If the assignment bundles independently testable interfaces or behaviors and requires the
   configured executor to carry multiple unfinished concerns, split at those real seams.
   Consider context loss, compaction and drift across implementation, debugging and verification,
   not just whether the author understands the whole milestone. Tailor boundaries and needed
   scaffolding to the selected executor/effort and observed capabilities, not a model-family
   hierarchy; unknown capability calls for explicit boundaries, not an invented model binding.
3. Check that each task delivers one bounded behavior or interface whose meaningful acceptance
   passes using completed prerequisites and its own result, without unfinished downstream
   implementation. Challenge a milestone bundle that leaves several independently testable
   interfaces unfinished together; split it at useful independently verifiable seams. Put
   composed acceptance at the first boundary where its prerequisites exist. Review both coarse
   bundles and gratuitous splits: no universal task count or file/line/token/time ceiling; more
   prose or reading executor configuration alone does not make a task bounded.

**Before:** “Deliver the reader, privacy mapper, HTTP service and browser; verify the app.”
This bundles independently testable contracts into a milestone.

**After:** Deliver the reader against existing storage, with consistency/no-write checks and
its docs; exclude mapper, HTTP and browser work. Then deliver each dependent interface against
its completed predecessor with local acceptance. Reader acceptance does not wait for the browser.
Keep a simple reader fix and its regression test together; this example sets no task count.

**Supporting ownership:** A UI export control may also need its capture selector, admitting
harness, final configuration/override support and producer fixture's admitting/type check.
Inspect these owners; include necessary in-scope changes with the control or name the real
existing producer dependency. An ordinary already-observed control needs only its existing
focused check. An ordinary cross-system wiring outcome may remain one task when established
interfaces, its focused wiring test, relevant documentation and ordinary support work establish
the final observable. Multiple files alone do not justify a split. This is authoring guidance,
not a generic path/dependency-closure validator or a new task field.

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
Dedicated fields for paths, interfaces, acceptance checks and shared context remain optional;
the work description can carry the outcome boundaries above. Cover all in-scope work,
integration/acceptance checks, and lockstep documentation whose evidence compares documentation
with implemented behavior.
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

### Authorization-neutral tasks

Write executable tasks as authorization-neutral work instructions. Keep temporary phase status
such as "planning only" or "implementation awaiting approval" in the approval record, not task
descriptions or check permissions. Do not add generic demands for separate exact-operation approval
to work covered by the current launch; identify actual unapproved effects instead. Necessary approved
setup and capacity investigation are technical prerequisites, not renewed download consent. Preserve
genuine action-specific permission boundaries and manual gates. Routine verification may use small
isolated tests and local test databases without an extra owner question; keep data and execution
bounded to avoid exhausting machine resources or affecting unrelated data/services.

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
still consumed if supplied; they are not universally required. When authoring a deterministic
required command, place it once in an existing `checks`, `check`, or `required[].check` field;
keep semantic criteria as prose, never compile prose into shell, and leave absent optional checks
absent. Sources may be context, not content-pinned execution authority. Keep actual external
action permission at that action.

Markdown may remain a human presentation. `check-task-order.py` also checks its IDs,
descriptions and dependency graph; no contiguous numbering or story-group constraints.

## Review and handoff

At final planning review, check that executable tasks are authorization-neutral and temporary
approval status is confined to the approval record; retain real action-specific permission gates.

Apply the early-risk owner's review contract to selection/omission, applicable dependencies,
proof lifetime, production acceptance, disproof/renewal and feasibility in both adapters/direct
entry. Return its applicable evidence/limits and blocked reliance through the producing review
and coordinator handoff. Before handoff, return concise task-specific material execution risks
or prerequisites: name the affected task, concrete runtime/interface/access or predecessor need,
observed evidence versus unknowns,
and the next investigation, mitigation, or necessary permission. Do not create a risk schema,
score, admission checklist, or universal report. The coordinator must consume these findings before
affected worker reliance; later discoveries use the same handoff. Exact unavailable capability,
access, paid, data, or external boundary names the affected operation and corrective action, while
unrelated safe work continues.
Challenge redundant task splits, duplicate proofs/report chains and disproportionate checks
without weakening acceptance or original gates. Syntax/order validation alone cannot prove
consumption or appropriate granularity. Apply the executor-sized outcome recipe at final review
for either adapter and direct tasking: reject a multi-interface milestone whose interfaces must all remain unfinished for acceptance; accept
independently verifiable slices with completed prerequisites and ordinary established cross-system
wiring with its focused tests/docs.

Carry work-specific checks, exclusions and genuinely material permission boundaries into
the worker brief. Verify the dependency graph with
`python3 scripts/check-task-order.py /path/to/tasks.json` from this skill directory (YAML
and Markdown are also supported). Manually inspect relevant scope and feasibility; do not
turn that review into additional executable intake metadata. A direct owner coding request
does not require a new planning or approval cycle. Historical source/task documents remain
unchanged unless the owner requests their revision.

## Mandatory task checkpoint

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md). An authorized task-list production is a retained bounded deliverable and checkpoints before combined artifact approval; preserve source approval and dependency semantics while checkpointing it separately.
