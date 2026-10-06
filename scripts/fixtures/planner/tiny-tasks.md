# TinySpec adapter fixture tasks

Source: [TinySpec](tiny-spec.md), AC1–AC2. Synthetic parser/contract fixture, not authorized work.
Excluded: migrations and unrelated ranking changes. Approval/review evidence is intentionally
absent; successful parsing does not make this fixture implementation-ready.

- [ ] T001 Implement and validate deterministic score ties.
  - **Depends**: none
  - **Outcome**: stable ID ordering for ties, existing score/filter behavior unchanged.
  - **Files/interfaces**: search ranking module and unit checks, located by fixture inspection.
  - **Acceptance**: REQUIRED T001/V1: failing-then-passing unit checks for AC1–AC2, empty inputs and filters. Pass: stated behavior holds. Smallest check: focused fixture checks for this outcome. Evidence: command/output and bounded documentation comparison where applicable. Manual/permission gates: no live operations authorized.
  - **Capabilities**: file editing and the project's observed unit-test runner.
  - **Integration checkpoint**: verify ranking producer before API contract consumer.

- [ ] T002 Verify API contract and document the tie rule.
  - **Depends**: T001
  - **Outcome**: unchanged result shape and accurate tie-order documentation.
  - **Files/interfaces**: search API integration checks and established behavior documentation.
  - **Acceptance**: REQUIRED T002/V1: API integration evidence for AC1–AC2; compare documentation with T001 behavior. Pass: stated behavior holds. Smallest check: focused fixture checks for this outcome. Evidence: command/output and bounded documentation comparison where applicable. Manual/permission gates: no live operations authorized.
  - **Capabilities**: observed integration runner and documentation editing.
  - **Shared context**: T001 tie cases and unchanged API contract; no live deployment checks claimed.
