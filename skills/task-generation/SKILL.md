---
name: task-generation
description: Use when producing or reviewing dependency-aware implementation tasks from an approved source, specification, plan, or direct requirement.
---

# Task Generation

Produce complete, dependency-aware, independently verifiable implementation tasks. This
shared contract owns task semantics and validation; it does not select a workflow origin,
create a plan, or execute tasks.

## Preconditions and adapters

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
Execution uses approved exact configured bindings and deterministic role-safe selection.

Use the adapter matching the producing workflow:

- A SpecKit adapter accepts planner's Standard specification/plan, first verifies the
  project's observed task-stage command and follows its instructions; unavailable required
  stage capability is a stop. Specification is requirements truth; approved plan is derived
  sequencing only. No SDD forwarding/rereading as direct requirements input. Trace source
  criteria into task checks. Governing instructions/contracts, memory and permission/safety
  still apply. Keep the stage create-only when its producer requires it.
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
story continuity, implicit producers, and stage feasibility, and report scripted validation
as unavailable.

## Intended executor before decomposition

Before Standard architecture or TinySpec task decomposition, capture the intended coding
model class and effort; unknown input blocks planning intake, never infer it from the
planner/producer/reviewer profile. Pass it unchanged to each architecture/task producer.
Root `execution_intent` in the authoritative task JSON and matching human summary carry
`model_class`, `effort`, `resolution` (unresolved/resolved), `assumptions`, `provenance`,
`decomposition_rationale` and `compatible_bindings`. Each compatible binding records exact
`provider`, `model`, `effort`, an `assessment` and its `provenance`; execution preflight
checks the actual implementation/repair bindings only, not planning/reviewer profiles.
This is planning intent, not execution permission or separately chargeable service authority.

Use owner-guided qualitative scaffolding, not universal rankings or fixed thresholds:
Luna: narrow coherent outcomes, named interfaces/invariants, context/edge-case pointers and
ordered guidance where useful. Terra: clear boundaries, non-obvious decisions and moderate
scaffolding. Sol: outcome-oriented instructions may leave routine choices open when justified.
Effort and verified guidance refine assumptions; unknown/unlisted classes default to explicit
instructions without unnecessary micro-tasks. A more capable planner must not leave architecture
implicit for a smaller executor. Record what is explicit/bounded, what choices remain open and
uncertainty. REQUIRED acceptance, dependencies, safety and approval gates never shrink.

Changed class/effort or exact binding requires a documented compatibility/revision assessment
of affected boundaries/detail/assumptions, with producing review/current-content renewal where
needed. Preserve unaffected tasks; no silent substitution, auto-escalation or unconditional
whole-plan regeneration. Resolve approved exact compatible bindings before dispatch using
explicit trusted owner/registry provenance; unresolved/incompatible intent blocks execution.
Historical handoffs lacking intent return to the earliest affected producing renewal gate,
preserving original source and approval evidence, never fabricated historical metadata.

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

Every task records an outcome, explicit prerequisites, likely files or interfaces,
independently observable acceptance evidence, required capabilities and shared context. Cover all in-scope work, integration/acceptance checks, and
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

Acceptance evidence uses the smallest sufficient check at the lowest layer that can
observe the changed seam's concrete failure. Use stable task-local references such as
`T001/V1` in existing acceptance/observable/invariant/test fields, in the shared structured contract. Each
REQUIRED item states its objective pass criterion, smallest sufficient check, expected evidence
(command/output or bounded artifact reference), and any manual/permission gates. Identify
optional checks separately. Missing required capability, permission or evidence means explicitly
NOT VERIFIED, not passed. Preserve item references through handoff so a shared check can cover
multiple items without losing any task mapping. In existing task fields, distinguish
REQUIRED checks from optional hardening/broader regression and separately gated
live/provider/engine/browser checks; record required permissions and unavailable
capabilities without treating them as passes. State briefly the expected verification
effort and why any broader check is necessary, not a universal deadline or new schema.
Do not attach exhaustive matrices, fault injection, new test infrastructure or broad
suites to simple query/wiring changes by default. Preserve necessary schema/security/
durability checks and owner-required criteria. Optional checks do not become blockers;
changing approved acceptance requires the producing workflow's review/approval gate.
Reference valid unchanged evidence rather than duplicating checks. Keep unrelated
compatibility repairs in small causal steps, with evidenced prerequisites only.

Tasks inherit root execution intent; do not assign per-task model classes or routing quotas.
Describe required capabilities; the executable runner verifies approved configuration.

Follow the observed project format. When no established complete format exists, use numbered
Markdown tasks with explicit `Depends` fields. Number in execution order from T001 with no
gaps; each prerequisite must be an earlier task. Keep shared setup before stories and each
story or stage in one contiguous segment. Check implicit dependencies and whether each stage
can obtain its producers before its consumers; revise the producer placement rather than
papering over a forward dependency.

Organize consecutive related tasks into coherent sequential work where their retained
context is useful. Preserve prerequisite order, individual evidence, and story acceptance
boundaries; do not reorder dependencies or pad a segment with distant work merely to fill a
batch. Internal producer/consumer dependencies, shared files, and phase/story headings may
remain together when producer verification precedes consumer work. Record likely shared
context and integration checkpoints for deterministic runtime intake and verification.

## Structured executable handoff (both adapters)

Emit exactly one authoritative adjacent JSON or fenced JSON representation matching the
suite's delivered `task.schema.json`; the human task document identifies it and agrees
field-for-field on execution intent and task IDs/order/deps/context_group/owned_paths,
REQUIRED criterion/check/version/args/pass_condition/expected_evidence/producer_dependencies/
gates, optional distinction and original manual/permission gates. Never infer these from
narrative or replace a whole REQUIRED mapping with a source pointer. IDs start at T001,
are contiguous, prerequisites earlier and story/context groups contiguous.

Preserve original `origin`, `legacy_origin`, source paths/sections/content hashes and
approval_refs. TinySpec retains separate source/tasks and combined approval; Standard
retains spec/plan/tasks, specification approval, independent overall review and final
approval plus actual installed stage evidence. Legacy retains documented original gates.
Draft refs may be empty/unresolved; denial/cancellation/staleness blocks affected execution,
not task preparation. Inadequate legacy returns to producing review/renewal, no forced Epic,
mass conversion, STATE initialization or historical rewrite. Reconcile active/unknown legacy
writers before reusing an origin.

Builtin runtime actions require explicit capability declarations for the actually exposed
read_file/write_file/request_owner_input tools, every REQUIRED oracle and potentially mutating
runner-git-commit stream (not unused registry checks). Their action_scope is canonical JSON:
version 1, action ID, tasks with original IDs/owned_paths; read_file additionally includes
sorted readable_paths from sources/approval record refs/owned paths. Check actions include
checks with task_id/version/args_hash; PythonAnswer also declares execution=trusted-project-python.
Use the delivered authority.action_requirement helper to obtain exact canonical bytes rather
than narrative matching. Effects are external for local read/question actions, mutation for
write/Git, test for oracles. External here is a local action, not network or financial authority.
PythonAnswer executes explicitly trusted project code, not a harmless byte comparison or
sandbox; a test declaration never infers arbitrary network/extra mutation authority. Keep
workflow and applicable node permissions/effect restrictions consistent. Duplicate, missing,
wrong-path/check/effect scopes block for producing renewal. Other scoped/paid-service actions
retain their original semantics; never silently convert historical prose approvals.

Root authorization_envelope and each task's authorization_envelope_id preserve selected exact
profiles, capabilities/action scope, actual owner references and unresolved/denied/approved
semantics. Ordinary approved-profile model traffic has no financial approval/cap/reservation.
Separately chargeable API/service actions need purpose/cost-impact explanation and explicit
scoped authority before action dispatch; known gaps are aggregated before tasks. Inside-envelope
technical work and approved isolated tests proceed without repetitive owner questions.

## Review and handoff

Review selection/omission, real-runtime evidence, applicable dependencies, proof lifetime,
production acceptance, disproof/renewal and feasibility through both adapters/direct entry.
Challenge redundant task splits, duplicate proofs/report chains and disproportionate checks
without weakening acceptance or original gates. Return only necessary producer/consumer
dependencies, applicable evidence/limits and blocked reliance to the existing producing review
and coordinator handoff; syntax/order validation alone cannot prove consumption.

For both adapters, carry each criterion/item ID, smallest check, accessible proof/pass
conditions, applicable earlier producer dependencies and original permission/manual gates into
the inline REQUIRED brief. For a [PROTOTYPE] task, preserve the marker and bounded informational
scope in the handoff and worker brief; missing marker/scope or code-only/unrun success claims
are not proof. Missing, weakened or unrun REQUIRED evidence blocks reliance; source pointers
cannot substitute for the contract. Reuse unchanged applicable proof once with all mappings,
rerun only affected invalidated evidence, and keep routine teardown inside its task. A separate
cleanup task needs an actual independently consequential resource or outcome.

Before approval, validate explicit dependencies and story continuity with
`python3 scripts/check-task-order.py /path/to/tasks.md` from this skill directory when the
format supports it. Then manually inspect traceability, exclusions, documentation,
integration, item completeness/evidence/gates, implicit dependencies, and stage feasibility.
For inadequate approved/legacy contracts, stop at producing review/renewal; an executor cannot
define replacement criteria or weaken acceptance post hoc. Missing or ambiguous REQUIRED contracts block dispatch and return to the producing review/approval gate,
including existing approved tasks with inadequate contracts. Do not fabricate historical contracts,
retrofit new requirements into legacy approvals, or waive checks; obtain affected review and renewed
approval before dispatch. Preserve original source provenance and legacy task-embedded requirements.
Return other defects to the producing workflow's review gate. Record the validation outcome and
current content evidence with the task artifact so a later handoff can detect stale approval.

## Mandatory task checkpoint

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md). An authorized task-list production is a retained bounded deliverable and checkpoints before combined artifact approval; preserve source approval and dependency semantics while checkpointing it separately.
