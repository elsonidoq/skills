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

Use the adapter matching the producing workflow:

- A SpecKit adapter first verifies the project's observed task-stage command and follows its
  instructions; unavailable required stage capability is a stop.
- A direct adapter derives tasks from an owner-authorized durable requirement/source and does not
  require a plan or SpecKit; final approval follows the produced-artifact review.

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
