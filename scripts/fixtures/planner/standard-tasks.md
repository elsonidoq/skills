# Standard adapter fixture tasks

Synthetic fixture for shared task semantics; not output from a real SpecKit run. Assume the
fixture's specification defines versioned API compatibility and its plan defines a producer
adapter before consumers. No stage or approval evidence is claimed; coordinator must reject
this fixture as an implementation handoff.

- [ ] T001 Establish the versioned response adapter and contract checks.
  - **Depends**: none
  - **Outcome**: old clients receive their unchanged response contract.
  - **Files/interfaces**: API adapter, response schema and contract checks in fixture repository.
  - **Acceptance**: REQUIRED T001/V1: old-version fixtures pass without losing required fields; invalid versions reject. Pass: stated behavior holds. Smallest check: focused fixture checks for this outcome. Evidence: command/output and bounded documentation comparison where applicable. Manual/permission gates: no live operations authorized.
  - **Capabilities**: editing and observed contract-test runner.
  - **Integration checkpoint**: inspect adapter evidence before updating its consumers.

- [ ] T002 [US1] Integrate consumers against the verified adapter.
  - **Depends**: T001
  - **Outcome**: consumers select the defined API version and retain failure handling.
  - **Files/interfaces**: client request layer and integration checks.
  - **Acceptance**: REQUIRED T002/V1: old/new response fixtures and failed requests exercise the approved contracts. Pass: stated behavior holds. Smallest check: focused fixture checks for this outcome. Evidence: command/output and bounded documentation comparison where applicable. Manual/permission gates: no live operations authorized.
  - **Capabilities**: editing and observed integration runner.
  - **Shared context**: response version rules, error fixtures, adapter checks.

- [ ] T003 [US1] Validate compatibility and update authoritative documentation.
  - **Depends**: T001–T002
  - **Outcome**: versioned contract and actual consumer behavior remain aligned.
  - **Files/interfaces**: integration suite and established API documentation owner.
  - **Acceptance**: REQUIRED T003/V1: compare schema/docs with implemented behavior; report simulated versus live results. Pass: stated behavior holds. Smallest check: focused fixture checks for this outcome. Evidence: command/output and bounded documentation comparison where applicable. Manual/permission gates: no live operations authorized.
  - **Capabilities**: observed test runner and documentation editing.
