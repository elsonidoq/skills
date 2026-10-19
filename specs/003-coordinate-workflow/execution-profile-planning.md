# Execution-profile-aware planning — owner-requested amendment

## Scope and approval

The owner requested this future-workflow capability after the original overall review:
planning must know which coding model class and effort will execute the tasks, including
when the planning model has greater capability than the executor. This is a substantive
amendment to the specification, architecture and T008, not a change to the coding model
for the present migration, a spend authorization, or a new runtime model router.
Historical approvals/review remain evidence for their original bytes only. Renew current
artifact review/approval before relying on this amended package for implementation.

## Requirement (FR-040)

Planner intake MUST capture the intended implementation model class and effort before
architecture planning (Standard) or task decomposition (TinySpec). Keep this separate
from specification/plan/task producer and reviewer profiles. Unknown executor input must
be resolved during planning intake, not guessed from the planner's own model. An exact
provider/model ID may be unresolved during planning, but the class and effort, resolution
status, capability assumptions and their provenance MUST be explicit. Execution preflight
MUST resolve an approved exact binding and verify its compatibility with those assumptions.
This metadata is planning intent, not permission to dispatch or spend.

Both planning paths MUST pass this input through to task generation and preserve it as
root-level machine-readable handoff metadata with a matching human summary. Tasks inherit
the profile; this does not introduce per-task model routing. The planner MUST explain how
task boundaries and instruction specificity address the intended executor's needs rather
than assuming that a smaller executor can reconstruct the planner's implicit reasoning.

## Minimal qualitative rubric

Use owner preferences and available verified capability guidance, not a fabricated model
benchmark or fixed token/file/task-size threshold. Initial owner-directed starting points:

| Executor | Planning starting point |
| --- | --- |
| Luna class | High explicitness: narrow coherent outcomes, named interfaces and invariants, ordered implementation guidance where useful, relevant context/file pointers, edge cases and objective verification. Avoid leaving architectural decisions implicit. |
| Terra class | Moderate scaffolding: clear boundaries, interfaces, constraints and verification; make non-obvious decisions explicit, allowing routine implementation choices. |
| Sol class | Outcome-oriented instructions may leave more routine implementation choices open where justified by available guidance; still state all contracts, constraints and verification. |

These are adjustable owner preferences, not proven rankings, universal limits or claims
about every member of a class. Effort level and actual available guidance refine the
assessment; higher effort is not assumed to compensate for missing context. Unknown or
mixed capability defaults to explicit instructions without unnecessary micro-tasks.
Never remove REQUIRED checks, acceptance detail, dependencies, safety/approval gates or
context needed to complete a task for a supposedly stronger model. Astra or any unlisted
class uses explicit assumptions/guidance, not an invented tier. Planning model class does
not determine the implementation class.

Record a concise decomposition rationale: what was made explicit or bounded for this
executor, what routine choices remain open, and any uncertain capability assumptions.
No arbitrary task count, exhaustive pseudo-code, duplicated source, mandatory extra PoC
or model-selection bureaucracy is required.

## Profile changes

If the intended implementation class/effort changes after planning, assess affected task
boundaries, detail and capability assumptions. Preserve unaffected tasks; revise only what
is necessary through existing producing-stage/current-content approval rules. A mismatch
must not silently dispatch, auto-escalate, or trigger unconditional whole-plan regeneration.
An equivalent exact binding within the approved intent uses documented compatibility
assessment and existing authorization rules, not a new blanket approval.

## Implementation placement and verification

T008 owns this change in planner intake, architecture delegation, TinySpec, shared task
generation, SpecKit task adapter/template, handoff documentation and task contract schema.
It must preserve the existing separation between planning profile selection and approved
runtime configuration. Extend the contract deliberately; do not infer the field from prose
or silently reject historical artifacts without the documented legacy renewal path.

Extend T008/V1 with permanent fixtures for both Standard and TinySpec showing:

- Executor class/effort reaches the architecture/task producer even when the planner uses
  a different class; missing input is caught at planning intake.
- The same requirement planned for Luna versus Sol retains identical acceptance/safety
  obligations while demonstrating justified differences in scaffolding, not just labels.
- Human/machine metadata agrees, includes assumptions/provenance and rationale, and
  survives handoff without becoming execution/spend authority.
- Changed class/effort triggers a compatibility/revision assessment; no silent model
  substitution, weakened checks, fixed unsupported capability thresholds or mandatory
  full regeneration. Execution binding validation catches unresolved/incompatible intent.

Static fixtures establish contract propagation and required planning instructions, not
universal model performance or semantic compliance. Existing real runtime binding tests
remain responsible for observed provider/model/effort enforcement.
