# Standard adapter fixture tasks

Synthetic fixture for shared task semantics; not output from a real SpecKit run. Assume the
fixture's specification defines versioned API compatibility and its plan defines a producer
adapter before consumers. No stage or approval evidence is claimed; coordinator must reject
this fixture as an implementation handoff.

- [ ] T001 Establish the versioned response adapter and contract checks.
  - **Depends**: none
  - **Outcome**: old clients receive their unchanged response contract.
  - **Files/interfaces**: API adapter, response schema and contract checks in fixture repository.
  - **Acceptance**: old-version fixtures pass without losing required fields; invalid versions reject.
  - **Capabilities**: editing and observed contract-test runner.
  - **Model class**: sonnet-class — bounded adapter with explicit contract evidence.
  - **Integration checkpoint**: inspect adapter evidence before updating its consumers.

- [ ] T002 [US1] Integrate consumers against the verified adapter.
  - **Depends**: T001
  - **Outcome**: consumers select the defined API version and retain failure handling.
  - **Files/interfaces**: client request layer and integration checks.
  - **Acceptance**: old/new response fixtures and failed requests exercise the approved contracts.
  - **Capabilities**: editing and observed integration runner.
  - **Model class**: sonnet-class — producer contract is already verified.
  - **Shared context**: response version rules, error fixtures, adapter checks.

- [ ] T003 [US1] Validate compatibility and update authoritative documentation.
  - **Depends**: T001–T002
  - **Outcome**: versioned contract and actual consumer behavior remain aligned.
  - **Files/interfaces**: integration suite and established API documentation owner.
  - **Acceptance**: compare schema/docs with implemented behavior; report simulated versus live results.
  - **Capabilities**: observed test runner and documentation editing.
  - **Model class**: sonnet-class — independently verifiable contract/documentation checks.
