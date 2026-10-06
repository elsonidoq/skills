# Operational Data Model

This describes the three entities in [the approved spec](spec.md), not a database, new mandatory schema or competing memory store. Use existing acceptance fields, coordinator tracker/brief and indexed coordination run/task records. [Plan](plan.md) owns integration and gates.

## Task verification item

- Stable task-local reference (for example `T001/V1`), linked source requirement, REQUIRED or optional status.
- Objective observable/pass criterion, smallest sufficient check and expected evidence source.
- Manual checkpoint or permission gate where applicable; unavailable required checks stay unverified.
- Result: pass, fail or not verified, with concrete output/evidence or explicit reason.

A reference is unique within its task and remains stable through dispatch/return. Shared check evidence may satisfy several references but must retain each mapping. Approved tasks lacking usable contracts return to their producing review/approval gate; do not fabricate historical fields.

## Batch routing decision

- Batch ID and ordered consecutive task IDs, dependencies and shared context.
- Assessment: residual reasoning, agentic/tool depth, weakest material verification blind spot, scope/coupling, failure cost/reversibility.
- Relevant approved guideline/evidence references and applicability, or explicit none.
- Proposed and owner-selected family, exact provider/model binding and independently selected effort; rationale for each dimension.
- Capability/support/permission evidence, execution mode, and conditional repair option with its gates.
- Aggregated REQUIRED item references and any shared-check mappings.

One selected model/effort covers the invocation. Proposed, selected and actually observed profiles are distinct; unknown actual effort is recorded as unknown, never copied from the request as proof. No fixed profile ladder or task-level assignments are implied.

## Batch outcome / attempt feedback

- Batch/attempt references and original decision; selected and observed profile (or unknown).
- Item-mapped results, check/evidence pointers, changed files and ordered per-task baseline/result checkpoint references, including separate evidence checkpoints.
- Contract strength, first-attempt/final outcome, valid partial work and invalidated evidence.
- Diagnosis: `model_capability`, `planning_or_spec_gap`, `verification_contract_gap`, `batching_error`, `environment_or_tooling`, `external_dependency` or `unknown`.
- Targeted repair/escalation rationale, authorized profile and re-verification disposition; prior attempt retained.

Existing coordination records/index own feedback; guideline candidate approval remains a separate existing reflection lifecycle. Weak or later-invalidated successes are not strong positive guidance; unavailable environments are not model failure.

## Relationships and transitions

Tasks own items; a batch decision references their union; each attempt returns results against that union and references its checkpoints. Multiple attempts retain one causal history without overwriting the first failure. A single check may support several items across tasks.

Operational lifecycle (descriptive, not new stored enum): proposed → capability/owner/contract preflight → dispatch → evidence validation → accepted or blocked/partial. Only complete, consistent, in-scope REQUIRED evidence with honored manual gates and inspected task checkpoints permits acceptance and release of dependents. Passing optional checks cannot compensate for missing required items. Accepted batches still require the existing final independent review before final implementation acceptance.

Blocked/partial attempts → inspected diagnosis → authorized targeted repair → affected re-verification → renewed validation. Preserve valid work; rerun all invalidated items, reuse unchanged evidence only after confirming applicability. Unknown cause prevents blind retry. Feedback persists for all dispositions; raw feedback does not transition directly into approved guidelines.
