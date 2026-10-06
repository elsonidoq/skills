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
treat a memory summary as downstream application or override source/owner authority.
No default index/history intake; justified clarification uses index-first relevant-only
retrieval, retaining uncertainty on no match.
Optional `residual_reasoning: low|medium|high` with a brief rationale fits existing notes;
absence requires no migration and does not alter classes, share or approval rules.

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

Every task records an outcome, explicit prerequisites, likely files or interfaces,
independently observable acceptance evidence, required capabilities, model class, and a
brief class rationale. Cover all in-scope work, integration/acceptance checks, and
lockstep documentation whose evidence compares documentation with implemented behavior.
Record exclusions so tasking cannot reintroduce them.

Acceptance evidence uses the smallest sufficient check at the lowest layer that can
observe the changed seam's concrete failure. In existing task fields, distinguish
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

Default bounded, well-specified work to `sonnet-class`. Use `opus-class` only when it cannot
be safely decomposed into bounded independently verifiable work. No more than 30% of the
complete task list may be `opus-class` without recorded owner approval of the affected IDs,
rationale, and delivery impact.

Follow the observed project format. When no established complete format exists, use numbered
Markdown tasks with explicit `Depends` fields. Number in execution order from T001 with no
gaps; each prerequisite must be an earlier task. Keep shared setup before stories and each
story or stage in one contiguous segment. Check implicit dependencies and whether each stage
can obtain its producers before its consumers; revise the producer placement rather than
papering over a forward dependency.

Organize consecutive same-class tasks into coherent sequential work where their retained
context is useful. Preserve prerequisite order, individual evidence, and story acceptance
boundaries; do not reorder dependencies or pad a segment with distant work merely to fill a
batch. Internal producer/consumer dependencies, shared files, and phase/story headings may
remain together when producer verification precedes consumer work. Record likely shared
context and integration checkpoints so the execution coordinator can make an evidence-based
batch decision.

## Review and handoff

Before approval, validate explicit dependencies and story continuity with
`python3 scripts/check-task-order.py /path/to/tasks.md` from this skill directory when the
format supports it. Then manually inspect traceability, exclusions, documentation,
integration, acceptance evidence, class share, implicit dependencies, and stage feasibility.
Return defects to the producing workflow's review gate. Record the validation outcome and
current content evidence with the task artifact so a later handoff can detect stale approval.

## Mandatory task checkpoint

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md). An authorized task-list production is a retained bounded deliverable and checkpoints before combined artifact approval; preserve source approval and dependency semantics while checkpointing it separately.
