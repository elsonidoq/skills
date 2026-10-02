# TinySpec adapter fixture tasks

Source: [TinySpec](tiny-spec.md), AC1–AC2. Synthetic parser/contract fixture, not authorized work.
Excluded: migrations and unrelated ranking changes. Approval/review evidence is intentionally
absent; successful parsing does not make this fixture implementation-ready.

- [ ] T001 Implement and validate deterministic score ties.
  - **Depends**: none
  - **Outcome**: stable ID ordering for ties, existing score/filter behavior unchanged.
  - **Files/interfaces**: search ranking module and unit checks, located by fixture inspection.
  - **Acceptance**: failing-then-passing unit checks for AC1–AC2, empty inputs and filters.
  - **Capabilities**: file editing and the project's observed unit-test runner.
  - **Model class**: sonnet-class — bounded rule with independently observable checks.
  - **Integration checkpoint**: verify ranking producer before API contract consumer.

- [ ] T002 Verify API contract and document the tie rule.
  - **Depends**: T001
  - **Outcome**: unchanged result shape and accurate tie-order documentation.
  - **Files/interfaces**: search API integration checks and established behavior documentation.
  - **Acceptance**: API integration evidence for AC1–AC2; compare documentation with T001 behavior.
  - **Capabilities**: observed integration runner and documentation editing.
  - **Model class**: sonnet-class — bounded validation/documentation using verified producer.
  - **Shared context**: T001 tie cases and unchanged API contract; no live deployment checks claimed.
