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
in either adapter, including direct entry without planner: ensure the mandatory project-local
store exists; automatically initialize missing files, notify the user and commit only
initialization files before proceeding, without a setup approval gate. Read compact guidelines
during initial understanding; empty guidelines invent no knowledge, not a nonpersistent path.
Initialization/commit failures stop; required gotcha-memory stops remain distinct.
Carry exact applicable constraints and evidence references from source/handoff into task
dependencies, delegation briefs, checkpoints and REQUIRED verification/acceptance. Do not
treat a memory summary as downstream application or override source/owner authority. Verify
a relevant decision reaches the dependency/check and coordinator brief, not merely a link.
No default index/history intake; justified clarification uses index-first relevant-only
retrieval, retaining uncertainty on no match.
Optional `residual_reasoning: low|medium|high` with a brief rationale fits existing notes;
it informs later batch assessment, not an execution assignment. Absence requires no
migration and does not alter approval rules. The coordinator owns batch profile selection
using the shared [qualified seed rubric](../coordinate-implementation/references/batch-routing.md),
not a model/effort label assigned by the task producer.

Use the adapter matching the producing workflow:

- A SpecKit adapter accepts planner's Standard specification/plan, first verifies the
  project's observed task-stage command and follows its instructions; unavailable required
  stage capability is a stop. Keep the stage create-only when its producer requires it.
- A direct adapter derives tasks from an owner-authorized durable TinySpec or legacy
  requirement/source and does not
  require a plan or SpecKit; final approval follows the produced-artifact review.

New TinySpec work always has a separate source and tasks file. Reference source sections
or acceptance criteria; put work-unit outcomes and task-specific checks in tasks, not a
copy of the entire source. Existing task-embedded requirements remain valid for legacy
work. The same task semantics apply to both adapters; no depth-specific execution schema.

For either adapter, verify Python 3 before relying on the bundled validator. If unavailable
or the task format is incompatible, manually inspect explicit dependencies, ordering,
story continuity, implicit producers, and stage feasibility, and report scripted validation
as unavailable.

## Task contract

Read and apply [early risk reduction](../planner/references/early-risk-reduction.md);
verify it is readable or stop with a missing-install report. Both adapters and direct entry
apply it without assuming planner already did. Planning schedules proofs, not execution
without separate authority. Justify selection/omission: difficult isolatable cores need
substantial leverage, easy names/types use inspection, non-isolatable risks use real-system
validation with actual prerequisites/gates. Use existing fields for a minimal real-runtime
executable producer with representative/adversarial criteria, commands/artifact/findings,
applicability and permission gates. Production consumers explicitly depend on the earlier
producer; acceptance requires inspect/run/use of the reference and preserving proven
behavior with production tests, not a report-only link. Retain proof until all consumers
and production validation pass; schedule cleanup last and preserve reproducible evidence.
Failed/unrun proofs cannot release assumed dependents: retain disproof/limits, correct/replan
and renew affected existing approvals rather than label failed techniques proven.

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

Acceptance evidence uses the smallest sufficient check at the lowest layer that can
observe the changed seam's concrete failure. Use stable task-local references such as
`T001/V1` in existing acceptance/observable/invariant/test fields, not a new schema. Each
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

Do not assign implementation-task model classes, family/effort profiles or allocation quotas.
Describe residual reasoning and required capabilities instead; later batch assessment selects
one owner-authorized supported profile per invocation, independently justifying family and effort.

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
context and integration checkpoints so the execution coordinator can make an evidence-based
batch decision.

## Review and handoff

Review early risk reduction selection/omission, real-runtime executable criteria,
explicit consumption/dependencies, all-consumer retention, production tests before cleanup,
disproof/renewal and feasibility through both adapters/direct entry. Return producer → consumer
→ production validation → cleanup mapping, applicability and blocked reliance to existing
producing review and coordinator handoff; syntax/order validation alone cannot prove consumption.

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
