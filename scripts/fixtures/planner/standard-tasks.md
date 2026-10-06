# Standard adapter fixture tasks

Synthetic fixture for shared task semantics; not output from a real SpecKit run. Assume the
fixture's specification defines versioned API compatibility and its plan defines a producer
adapter before consumers. The following is a complete **pending** task/reviewer routing preview:
no stage or approval evidence is claimed, and coordinator must reject this fixture as an
implementation handoff.

| Role | Family | Concrete binding | Effort | Capability/benchmark evidence and rationale | Uncertainty / approval |
| --- | --- | --- | --- | --- | --- |
| T001 | Sol | `fixture-standard-binding` | medium | Runtime support record `fixture-S1`; bounded adapter and contract oracle justify the least adequate effort after decomposition. | Matching benchmark applicability is unknown; research or bounded owner uncertainty decision required before final approval. |
| T002 | Sol | `fixture-standard-binding` | medium | Runtime support record `fixture-S1`; verified adapter producer and integration oracle bound remaining reasoning. | Matching benchmark applicability is unknown; research or bounded owner uncertainty decision required before final approval. |
| T003 | Sol | `fixture-standard-binding` | medium | Runtime support record `fixture-S1`; documentation comparison and compatibility oracle bound remaining reasoning. | Matching benchmark applicability is unknown; research or bounded owner uncertainty decision required before final approval. |
| Reviewer | Astra | `fixture-review-binding` | medium | Runtime support record `fixture-R1`; independent evidence review, not role- or risk-based escalation. | Pending the same final approval and current capability check. |

Bounded retry authority is pending and must be recorded with final approval; this fixture does not
infer effort, use a provider ID, or establish a family default.

- [ ] T001 Establish the versioned response adapter and contract checks.
  - **Depends**: none
  - **Outcome**: old clients receive their unchanged response contract.
  - **Files/interfaces**: API adapter, response schema and contract checks in fixture repository.
  - **Acceptance**: old-version fixtures pass without losing required fields; invalid versions reject.
  - **Capabilities**: editing and observed contract-test runner.
  - **Routing**: proposed Sol / `fixture-standard-binding` / medium; support `fixture-S1`; adapter decomposition and contract oracle justify residual reasoning. Pending owner selection; benchmark uncertainty disposition required.
  - **Integration checkpoint**: inspect adapter evidence before updating its consumers.

- [ ] T002 [US1] Integrate consumers against the verified adapter.
  - **Depends**: T001
  - **Outcome**: consumers select the defined API version and retain failure handling.
  - **Files/interfaces**: client request layer and integration checks.
  - **Acceptance**: old/new response fixtures and failed requests exercise the approved contracts.
  - **Capabilities**: editing and observed integration runner.
  - **Routing**: proposed Sol / `fixture-standard-binding` / medium; support `fixture-S1`; verified producer and integration oracle bound residual reasoning. Pending owner selection; benchmark uncertainty disposition required.
  - **Shared context**: response version rules, error fixtures, adapter checks.

- [ ] T003 [US1] Validate compatibility and update authoritative documentation.
  - **Depends**: T001–T002
  - **Outcome**: versioned contract and actual consumer behavior remain aligned.
  - **Files/interfaces**: integration suite and established API documentation owner.
  - **Acceptance**: compare schema/docs with implemented behavior; report simulated versus live results.
  - **Capabilities**: observed test runner and documentation editing.
  - **Routing**: proposed Sol / `fixture-standard-binding` / medium; support `fixture-S1`; compatibility/documentation oracle bound residual reasoning. Pending owner selection; benchmark uncertainty disposition required.
