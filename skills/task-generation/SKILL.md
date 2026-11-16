---
name: task-generation
description: Use when producing or reviewing dependency-aware implementation tasks from an approved source, specification, plan, or direct requirement.
---

# Task Generation

Turn the authorized source into tasks that each deliver a verifiable outcome. For each
outcome, identify the work, its prerequisites and the check that shows it is complete.
Return the task artifact for the producing workflow's review and approval. This skill
owns task decomposition and validation, not source changes, workflow selection or execution.

## Draft outcomes from the source

Read the source, relevant supporting artifacts, repository instructions, governing principles
and existing task format. Confirm authority to **prepare** tasks and that applicable upstream
approvals cover the current source; final task or implementation approval comes after production.
If required input, preparation authority or an applicable approval is missing, name the gap
and stop the affected production rather than invent it.

Choose the source route:

- The **direct adapter** uses an owner-authorized durable TinySpec or legacy requirement.
  It needs neither a plan nor SpecKit. New TinySpec work has a separate source and tasks file;
  existing task-embedded legacy requirements remain valid.
- The **SpecKit adapter** uses the Standard specification as requirements truth and the
  approved plan for derived sequencing only. Verify the project's observed task-stage command
  is usable and follow its instructions; if unavailable, report the missing capability and
  stop this stage. Keep production create-only where required: authorized drafting, revision,
  shortening and mechanical checks of unsubmitted output need no supervisor gate. Submitted
  defects return through the producing workflow's review/correction route.

Both routes use the source's criteria, not SDD as downstream requirements input. Reference
source sections instead of copying them. Cover all in-scope outcomes, integration, acceptance
and lockstep documentation that must agree with implemented behavior; record exclusions.
State shared constraints once and put only outcome-specific work and checks in each entry.

For both routes, including direct and fresh/resumed entry, consult
[Memory Handling](../memory-handling/SKILL.md) for relevant explicit owner guidance and gotchas
from the verified unified index, and [save-adr](../save-adr/SKILL.md#consult-and-propagate) for
current accepted outcomes, explicit mechanism constraints and source links. Apply their
retrieval and authority rules; missing optional memory or STATE is nonblocking. Map each
applicable source observable to its task dependency or gate, task-local REQUIRED check and
worker/reviewer briefs. The constraint must affect that mapping, not merely appear as a link.
A source/task conflict or uncertain supersession stops only the affected mapping for resolution.

## Make each outcome independently finishable

<a id="executor-sized-outcomes"></a>

Before decomposing work in either route, read the selected executor JSON yourself at the exact
absolute path supplied by the planner/coordinator. Use its valid worker model and effort to
size the work, not the planner, parent or producer profile or a remembered default. A valid
selection needs no new owner question. If the path is missing, ambiguous or unreadable, or the
worker model/effort is invalid or missing, stop the affected producer and ask the owner to
resolve that role, path and problem; do not infer or substitute a binding.

On standalone entry without a resolved path, use the suite's
[executor resolver](../../scripts/resolve-workflow-executor.py):
`python3 scripts/resolve-workflow-executor.py --project PROJECT_ROOT` from the suite checkout.
Use `--executor PATH` only for an explicit override. Relative overrides are project-root-relative;
otherwise the resolver selects only `PROJECT_ROOT/.pi/workflow-executor.json`. Pass its absolute
result unchanged in briefs and handoffs. Do not search for alternatives, fall back after a failed
override, create/copy configuration, authenticate or invoke models to resolve it. Verify Python 3
and the resolver are available before use; if not, report the affected capability and correction
needed under [runtime requirements](../../REQUIREMENTS.md), without installing it.

Write one bounded behavior or interface per task, with acceptance that can pass using completed
prerequisites and that task's own result, without unfinished downstream implementation. Name
its owned paths, scope/exclusions, consumed interfaces, earlier producers and observable result
in the description or existing fields. Inspect the product interface together with its acceptance
selectors, coupled fixtures, admitting harness and final configuration/override owners. Before
relying on a producer fixture, inspect its applicable admitting/type check. Include necessary
in-scope support changes or name the existing producer dependency that supplies them.

Split a milestone at independently testable seams when it leaves multiple concerns unfinished
together. Account for context loss, compaction and drift during implementation and verification,
using the selected executor/effort and observed capabilities, not a model-family hierarchy or
invented task-count, file, line, token or time limits. Unknown capability calls for explicit
boundaries. Keep ordinary tests, evidence, relevant documentation, review preparation and routine
teardown with the outcome. Separate work only for an independently necessary deliverable,
prerequisite, gate, resource boundary or material context incompatibility—not a phase name.

For example, a new reader, mapping layer and browser are a milestone when each has its own
contract. Finish and test the reader against existing storage before tasks that consume it;
reader acceptance must not wait for the browser. A small reader fix and its regression test
stay together. Established cross-system wiring may also stay one task when its focused test
and support work establish the final observable; multiple files alone do not require a split.

## Give each task sufficient proof

Use the smallest relevant project check that observes the changed behavior, not generic green
output. For a wiring task, this can be the existing fixture that captures the selected ID at the
consumer unchanged. If separate green components cannot establish a risky boundary, use the
smallest composed check of the final observable, order or custody. Reuse a focused check that
already observes it. Place composed acceptance at the first boundary with the necessary
prerequisites; a separate proof task is needed only for an independently necessary prerequisite.
Preserve required security, durability and owner checks.

Apply [early risk reduction](../planner/references/early-risk-reduction.md) in both routes,
including direct entry; verify it is readable or stop affected planning with a missing-install
report. Use its selection and proof-lifetime rules to decide whether ordinary actual-helper tests
or an earlier step in this delivery suffice, or a consequential unknown needs an experiment.
For an experiment, mark the title **[PROTOTYPE]** (an explicit equivalent only if the format
cannot support it). Scope it to one consequential question and an informational conclusion and
limits supported by script code and actual observed execution evidence. Carry that marker and
scope into the handoff and worker brief. Carry the findings and necessary dependencies under
that contract's reuse/retention limits, production acceptance and disproof/renewal rules into
review and dependent tasks; failed or unrun proof cannot release assumed reliance. Planning schedules proof, not execution without authority.

Apply [Parsimony and Actionable Checks](../planner/references/parsimony.md) when selecting
requirements, design choices and checks. Distinguish owner requirements, verified interface
restrictions and agent design choices in existing fields. Before declaring a technical blocker,
verify the affected operation's enforced limit at its consumer; do not generalize a tool limit
into an artifact limit or a narrow remedy into a broader owner requirement.

Check commands are optional task context, not universal acceptance boilerplate. When specified,
they must run after the relevant work and report the real outcome; missing or failed is not
passed. Carry criterion/check/evidence and dependency mappings through both routes unchanged.
Manual STOP or representative-sample approval belongs only where the actual source or risk
requires it before downstream or expensive work, not on ordinary coding tasks.

<a id="authorization-neutral-tasks"></a>

Write authorization-neutral work instructions. Temporary phase/approval status belongs in the
approval record, not task descriptions or check permissions. Current launch authority covers
its assigned scope, including necessary approved setup and capacity investigation; identify
actual unapproved effects instead of demanding renewed exact-operation or download consent.
Preserve genuine action-specific permission boundaries and manual gates. Routine verification
may use small isolated tests and local test databases without another owner question, bounded
so they do not exhaust machine resources or affect unrelated data/services.

## Encode the tasks for their consumer

<a id="structured-executable-handoff-both-adapters"></a>

For executable intake, emit JSON or YAML as a task list or an object containing `tasks`.
Each task needs a nonempty string `id` and `outcome` (or `description`). Optional `depends`
is a list of task IDs. IDs must be unique, references must exist, and dependencies must not cycle.
File order and ID numbering do not determine execution order. Empty lists mean no work and
reserve or launch nothing.

These are the six startup linter checks: readable input, parsed task list, ID/work description,
unique IDs, existing dependency references and acyclic dependencies. Do not add mandatory
eligibility metadata or a depth-specific schema. Keep useful optional context; do not regenerate
old tasks merely to remove metadata. Markdown may remain the human presentation.

Dedicated paths, interfaces, acceptance and shared-context fields are optional; descriptions
can carry them. Optional `owned_paths` restricts mutation when supplied; omitting it does not
authorize adoption of dirty files or arbitrary staging. Existing `required` check mappings remain
consumed when supplied. Put an authored deterministic required command once in an existing
`checks`, `check`, or `required[].check` field. Keep semantic criteria as prose; never compile
prose into shell, and leave absent optional checks absent. Sources may supply context without
content-pinning execution authority; external effects still need authority at the action.

Carry an associated qualified issue URL from the source or brief as optional top-level
`delivery_issue` in human tasks, executable handoff and coordinator handoff. It is not an issue
prerequisite for bare task lists. If tracker work is needed, use
[track-open-issue](../track-open-issue/SKILL.md) for its authority and operation result; task
production does not grant tracker write authority.

## Return a checked task artifact

Verify the graph with `python3 scripts/check-task-order.py /path/to/tasks.json` from this skill
directory; JSON, YAML and Markdown are supported. Check Python 3 and the bundled validator
before relying on them. If unavailable or the format is incompatible, report scripted validation
as unavailable and manually inspect dependencies, order, references, cycles, implicit producers
and stage feasibility.

Review the draft against the source and the outcome/proof rules above in either route, including
direct tasking. Inspect scope and feasibility beyond syntax: task granularity, necessary support,
actual proof consumption and authorization neutrality need judgment, not extra intake metadata.
This does not replace independent review or permit upstream requirement changes. A direct owner
coding request does not itself need a new planning/approval cycle; historical documents stay
unchanged unless their revision is requested.

Return the artifact, source links, validation results/limits and task-specific material execution
risks or prerequisites to the existing producing review and coordinator handoff. For each risk,
name the affected task and concrete runtime/interface/access or predecessor need, observed evidence
versus unknowns, and the next investigation, mitigation or necessary permission. The coordinator
must consume these findings before affected worker reliance; later discoveries use the same
handoff. Missing capability, access, paid, data or external authority must identify the affected
operation and corrective action, while unrelated safe work continues. No new risk schema or
universal report is needed. Worker briefs carry work-specific checks, exclusions and material
permission boundaries, together with the mappings established above.

Checkpoint authorized retained task-list production under the shared
[task-commit contract](../memory-handling/references/task-commit-contract.md) before combined
artifact approval, separately from source approval and with dependency semantics intact.
