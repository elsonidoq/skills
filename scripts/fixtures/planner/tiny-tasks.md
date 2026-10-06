# TinySpec adapter fixture tasks

Source: [TinySpec](tiny-spec.md), AC1–AC2. Synthetic parser/contract fixture, not authorized work.
Excluded: migrations and unrelated ranking changes. It exercises the direct adapter: no Standard
plan is required. The following is a complete **pending** task/reviewer routing preview, not an
approval or dispatch authorization; successful parsing does not make this fixture implementation-ready.

| Role | Family | Concrete binding | Effort | Capability/benchmark evidence and rationale | Uncertainty / approval |
| --- | --- | --- | --- | --- | --- |
| T001 | Terra | `fixture-tiny-binding` | medium | Runtime support record `fixture-T1`; bounded tie rule and unit oracle support least adequate effort after decomposition. | No matching benchmark row; bounded owner uncertainty decision required before final approval. |
| T002 | Terra | `fixture-tiny-binding` | medium | Runtime support record `fixture-T1`; verified producer and API acceptance oracle bound remaining reasoning. | No matching benchmark row; bounded owner uncertainty decision required before final approval. |
| Reviewer | Astra | `fixture-review-binding` | medium | Runtime support record `fixture-R1`; fresh read-only review of named evidence, not role-based escalation. | Pending the same final approval and current capability check. |

Bounded retry authority is pending and must be recorded with final approval; this fixture does not
infer effort, use a provider ID, or establish a family default.

- [ ] T001 Implement and validate deterministic score ties.
  - **Depends**: none
  - **Outcome**: stable ID ordering for ties, existing score/filter behavior unchanged.
  - **Files/interfaces**: search ranking module and unit checks, located by fixture inspection.
  - **Acceptance**: failing-then-passing unit checks for AC1–AC2, empty inputs and filters.
  - **Capabilities**: file editing and the project's observed unit-test runner.
  - **Routing**: proposed Terra / `fixture-tiny-binding` / medium; support `fixture-T1`; residual tie-rule reasoning after decomposition with unit oracle. Pending owner selection; no-row uncertainty disposition required.
  - **Integration checkpoint**: verify ranking producer before API contract consumer.

- [ ] T002 Verify API contract and document the tie rule.
  - **Depends**: T001
  - **Outcome**: unchanged result shape and accurate tie-order documentation.
  - **Files/interfaces**: search API integration checks and established behavior documentation.
  - **Acceptance**: API integration evidence for AC1–AC2; compare documentation with T001 behavior.
  - **Capabilities**: observed integration runner and documentation editing.
  - **Routing**: proposed Terra / `fixture-tiny-binding` / medium; support `fixture-T1`; verified producer and API oracle bound residual reasoning. Pending owner selection; no-row uncertainty disposition required.
  - **Shared context**: T001 tie cases and unchanged API contract; no live deployment checks claimed.
