---
name: task-generation
description: Use when producing or reviewing dependency-aware implementation tasks from an approved source, specification, plan, or direct requirement.
---

# Task Generation

Turn authoritative requirements into executable, independently verifiable tasks.
Decide where work can finish, what it needs first, and how its result will be checked.
Return a human task document, JSON/YAML executable tasks, and the findings needed by
reviewers and the coordinator. This skill prepares work; it does not select a workflow,
change requirements, approve implementation, or execute the tasks.

## Establish the inputs

Confirm authorization to **prepare** tasks and the upstream approvals applicable to the
current source. Final task/implementation approval comes after production, not before
it. Read repository instructions, governing principles, source/supporting artifacts and
existing task formats. Missing required source, authority or capability stops affected
production with the exact gap and corrective action. Check applicable capabilities at their
operation boundary under [suite requirements](../../REQUIREMENTS.md); do not install missing
tools automatically.

Choose the source route:

- **Direct:** use the owner-authorized durable TinySpec or legacy requirement as requirements
  truth. No plan or SpecKit is required, including standalone entry. New TinySpec work has a
  separate source and tasks file; legacy task-embedded requirements remain valid.
- **SpecKit:** use the Standard specification as requirements truth and the approved plan
  only as derived sequencing. Verify the project's observed task-stage command is usable,
  then follow its instructions; an unavailable required stage stops production. Respect a
  create-only stage: authorized drafting, revision, shortening and mechanical validation of
  unsubmitted output need no supervisor gate. Submitted defects use the producing workflow's
  review/correction route, not an upstream requirements rewrite.

For both routes, source criteria govern task checks. Do not forward or reread SDD guidance
as direct requirements input. Governing instructions, memory and permission/safety contracts
still apply. Preserve exclusions and distinguish source requirements, verified runtime
restrictions and agent-selected choices; an inferred remedy is not a new owner requirement.

Before decomposition, apply these existing owners on direct, standalone, fresh and resumed
entry. Verify required references are readable; report missing packaging rather than invent
replacement rules:

- [Parsimony and Actionable Checks](../planner/references/parsimony.md): use its proportionate
  decision rules when choosing task boundaries and checks.
- [Memory Handling](../memory-handling/SKILL.md): retrieve relevant explicit owner guidance and
  gotchas from the verified unified index. Missing optional storage or STATE is nonblocking.
  Apply its retrieval and write safeguards; do not add default history intake, execution-time
  feedback routing, initialization or routine persistence.
- [save-adr](../save-adr/SKILL.md): consult current accepted decisions and supersession under
  its consult/propagate contract. Do not rely on a previous context's applicability claim.

Map each applicable source observable and memory/accepted constraint, with its source link,
into the task dependency or gate, task-local REQUIRED check and worker/reviewer brief.
The constraint must change the work or verification, not merely appear as a link. Source
conflict or uncertain current supersession stops only the affected mapping.

## Read the execution binding

Before either route decomposes work, the producer itself must read the selected executor
JSON. Use the exact absolute path supplied by the planner/coordinator, unchanged in later
briefs and handoffs; a claim that someone else read it is insufficient.

On standalone entry without a resolved path, verify Python 3 and use the suite's
[resolver](../../scripts/resolve-workflow-executor.py):
`python3 scripts/resolve-workflow-executor.py --project PROJECT_ROOT`.
Add `--executor PATH` only for an explicit override; relative overrides are project-root
relative. Otherwise select only `PROJECT_ROOT/.pi/workflow-executor.json`. Missing resolver
capability stops this resolution with the affected operation and corrective action.

Use the JSON's valid worker model and effort to size implementation work, not the
planner/parent/producer profile or a remembered default. Valid configuration needs no
executor-selection question. If the path is missing, ambiguous or unreadable, or the worker
model/effort is missing or invalid, stop the affected producer and ask the owner to resolve
the role, path and problem. Do not substitute assignments, search other locations, fall back
after a failed override, create/copy configuration, authenticate providers or invoke models
to resolve it. Configuration is not task eligibility metadata: no binding assessment,
execution-intent resolution or provenance receipt is needed.

## Find work that can finish

<a id="executor-sized-outcomes"></a>

Start from outcomes, not workflow phases. Each task must deliver one bounded behavior or
interface whose meaningful acceptance passes with completed predecessors and its own
result, without unfinished downstream implementation. A milestone with several independently
testable interfaces is not one task merely because a capable model could implement it.

For each candidate:

1. Name the outcome, owned change paths, scope/exclusions, consumed interfaces and actual
   earlier producers. Size the work for the selected executor/effort and observed capability,
   including context loss, compaction and drift during implementation and debugging. Split
   independently testable concerns that would otherwise stay unfinished together. Do not
   infer a model-family hierarchy or impose task-count, file, line, token or time ceilings.
2. Inspect the product interface together with acceptance selectors, coupled fixtures,
   admitting harness and final configuration/override owners. Before relying on a producer
   fixture, inspect its applicable admitting/type check. Include necessary in-scope tests,
   fixtures, configuration, harness changes and relevant documentation in the outcome, or
   name the real predecessor that supplies them. Do not assign a product file alone when
   its observable result needs supporting edits.
3. Keep ordinary test writing/running, evidence, review preparation and routine teardown with
   the outcome. Separate only an independently necessary deliverable, prerequisite, gate,
   resource boundary or material context incompatibility—not a workflow noun or quota.

For example, a storage reader can finish against the existing storage contract with its
readback tests and contract docs, before a mapper, HTTP service or browser exists. Reader
acceptance must not wait for that browser. Conversely, ordinary cross-system wiring through
established interfaces can remain one task when its focused wiring test, docs and support
work establish the final observable. Several changed files alone do not justify a split.

Record boundaries in the work description or existing optional fields, not a new schema.
State shared constraints once in their authoritative context; reference source criteria
rather than copy the specification into each task. Cover all in-scope work, integration and
acceptance checks, including lockstep documentation checked against implemented behavior.

## Choose evidence before reliance

Use the smallest relevant project check that observes the changed behavior. State the
observable and pass condition, not just “suite green.” For ordinary wiring, an existing
argument fixture showing the selected ID reaches the consumer unchanged can suffice.
Check commands are optional task context, not universal acceptance boilerplate. Specified
checks must run after the relevant work and report the real outcome; missing or failed
checks are not passes. Preserve owner-required checks, security/durability checks and actual
permission/manual gates. A representative-sample STOP needs a real source/risk reason, not
a generic coding ceremony.

When separate green components cannot establish a genuine risky boundary, require the
smallest composed check that observes the final observable, order or custody. Reuse an
existing focused check if it already observes that boundary. Put composed acceptance at the
first boundary with the necessary prerequisites; do not build an extra integration programme
for already-observed wiring. Before declaring a technical blocker, verify the exact operation
and enforced limit at its consuming interface. A file-tool read limit is not a task-loader
limit or a universal artifact-size cap.

Apply [early risk reduction](../planner/references/early-risk-reduction.md) for both routes,
including direct/standalone entry; verify it is readable or stop with a missing-install
report. Use its selection, evidence, applicability/lifetime, consumption, teardown and
disproof rules, and return their findings through review and handoff. Planning schedules
proofs; it does not execute them without separate authority.

Known bounded behavior uses permanent actual-helper tests or a verified earlier step in the
delivery task. A disposable experiment is for one genuinely unknown consequential question
before costly reliance, not a substitute implementation. Mark its title **[PROTOTYPE]**
(or an explicit equivalent only for an incompatible observed format), and keep the marker
and bounded informational scope in the handoff and worker brief. Require script code and
actual observed execution evidence, with conclusions and limits under the shared owner.
Only an independently necessary prerequisite becomes an earlier task; otherwise verify
before reliance inside the same task. Consumers must use applicable findings and retain
permanent production acceptance tests. Failed or unrun evidence cannot release assumed
reliance: retain limits, correct/replan and renew affected existing approvals under that owner.
Block affected reliance, not unrelated safe work or a duplicate proof chain.

## Write the deliverables

<a id="authorization-neutral-tasks"></a>

Write authorization-neutral work instructions. Temporary phase status such as “planning
only” or “awaiting implementation approval” belongs in the approval record, not task
instructions or check permissions. Do not demand renewed exact-operation permission for
work covered by the current launch. Identify actual unapproved effects and retain genuine
action-specific permission boundaries and manual gates.

Ordinary scoped fixes, necessary approved setup/capacity investigation and routine verification
need no repeated approval. Small isolated tests and local test databases need no extra owner
question; keep data and execution bounded to avoid exhausting resources or affecting unrelated
data/services. This does not authorize global installs, paid-scope expansion or external
actions, nor waive credential, security or data protections.

<a id="structured-executable-handoff-both-adapters"></a>

Provide a concise human task document and JSON or YAML executable intake: a task list, or an
object containing `tasks`. Each task has a nonempty string `id` and `outcome` (or `description`).
Optional `depends` is a list of task IDs. The entire startup linter has six checks:

1. Readable input.
2. Parsed JSON/YAML task list.
3. ID and work description.
4. Unique IDs.
5. Existing dependency references.
6. Acyclic dependencies.

File order and ID numbering do not determine execution order. Empty lists mean no work and
reserve/launch nothing. Paths, interfaces, acceptance, commands and shared context can stay
in descriptions or optional fields. Do not require context groups, hashes, approval envelopes,
gates, oracle mappings or model assessments for intake, or regenerate legacy tasks just to
remove metadata. Useful optional context remains valid; there is no depth-specific schema.

When supplied, `owned_paths` restricts mutation and existing `required` check mappings must
be consumed. Without owned paths the runner claims only clean, unchanged paths immediately
before tool edits; it cannot adopt dirty files or stage arbitrary post-run changes. Put each
authored deterministic required command once in an existing `checks`, `check`, or
`required[].check` field. Keep semantic criteria as prose, never compile prose into shell,
and leave absent optional checks absent. Sources can be context without content-pinned
execution authority; external-action permission stays at the action.

Carry a qualified issue URL supplied by the source/planner as optional top-level
`delivery_issue` into human tasks, executable output and coordinator handoff. Do not make an
issue a prerequisite for bare lists. Any tracker operation uses
[track-open-issue](../track-open-issue/SKILL.md) and its capability/authority checks.

## Check and return

For either route, review source coverage, exclusions, authorization neutrality, outcome size,
supporting ownership, actual dependencies and stage feasibility. Reject multi-interface
milestones whose acceptance needs several unfinished concerns; accept independent slices
using completed predecessors and ordinary established wiring with focused tests/docs.
Challenge gratuitous splits and disproportionate checks without weakening acceptance or gates.
Review the early-risk owner's selection/omission rationale, runtime evidence, applicability,
proof lifetime/reuse, production acceptance and failed/unrun reliance blockers. Preserve
work-specific checks, item mappings, exclusions and material permission boundaries in briefs.

Verify Python 3 before using the bundled validator. From this skill directory run
`python3 scripts/check-task-order.py /path/to/tasks.json` (YAML and Markdown are supported).
If Python is unavailable or the format is incompatible, manually inspect dependencies,
ordering, references, cycles, implicit producers and stage feasibility; report scripted
validation as unavailable. Syntax/graph validation is not proof of granularity or consumption.

Return task-specific material execution risks or prerequisites: affected task, concrete
runtime/interface/access or predecessor need, observed evidence versus unknowns, and next
investigation, mitigation or necessary permission. The coordinator must consume these findings
before affected worker reliance; later discoveries use the same handoff. Name the exact
unavailable capability, access, paid, data or external operation and corrective action. Block
only affected work; do not add a risk schema, score or admission checklist.

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md)
to authorized retained task-list production: validate and checkpoint this deliverable before
combined artifact approval, separately from its source while preserving dependencies and
source approval. Return it through the producing workflow's independent review and approval
route; production is not approval. A direct owner coding request needs no new planning cycle.
Leave historical source/task documents unchanged unless the owner requests revision.
