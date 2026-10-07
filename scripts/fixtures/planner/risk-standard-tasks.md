# Illustrative Standard risk adapter — C

Synthetic task shape only, not output from real SpecKit or a real transformation experiment.
No execution, approval or model-obedience proof. C: difficult canonical transformation is the
hardest core, cheaply isolatable with an executable oracle and substantial downstream leverage.
The assumed plan sequences this producer before integration plumbing using existing fields.

- [ ] T001 Prove canonical transformation with a minimal executable reference.
  - **Depends**: none
  - **Outcome**: determine whether canonical output preserves required information in tested bounds.
  - **Files/interfaces**: disposable transform-proof.py, assertions and retained findings in discovered project owners.
  - **Acceptance**: REQUIRED T001/V1. Pass: representative and adversarial inputs preserve fields, deterministic round-trip canonical output, explicit rejection of malformed/ambiguous input; failure rejects the technique. Smallest check: real dependency/runtime where relevant, observed target version, executable assertions for nested, empty and conflicting inputs (not a mock/name-print script). Commands: `python transform-proof.py --cases representative,adversarial`; expected exact output and rejection assertions. Evidence: artifact, commands actually run, observed findings, version/runtime/revision applicability and limits. Gate: separately authorized local execution and available target runtime; unrun/unavailable is NOT VERIFIED, not PASS, and blocks dependent reliance.
  - **Capabilities**: separately permitted target runtime and dependency; no installation or live call assumed.
  - **Integration checkpoint**: retain executable artifact, commands and findings for all consumers; failed result blocks assumed consumer approach and returns to correction/replanning and affected approval renewal.

- [ ] T002 [US1] Integrate production transformation using the tested reference.
  - **Depends**: T001
  - **Outcome**: production preserves proven behavior within applicable bounds, with remaining integration risks tested.
  - **Files/interfaces**: production transformation plumbing and production tests in discovered project repository.
  - **Acceptance**: REQUIRED T002/V1. Pass: inspect and run applicable transform-proof.py, use it as implementation reference, preserve canonical behavior with production tests; a report-only link is insufficient. Smallest check: `python transform-proof.py --cases representative,adversarial` then observed project production test command for round-trip/rejection behavior and remaining integration risks. Evidence: replay output, applicability check, production assertions/results compared to T001 findings. Gate: T001 passed and still-applicable version/runtime/revision, separate production execution authority; failed/unrun producer cannot release this task.
  - **Capabilities**: editing and observed production runner under approved permissions.
  - **Shared context**: proof artifact, commands, findings and limits retained until all consumers and production validation pass.

- [ ] T003 [US1] Clean disposable proof only after validated consumption.
  - **Depends**: T001, T002
  - **Outcome**: disposable reference removed without losing reproducible findings.
  - **Files/interfaces**: disposable proof and established evidence owner.
  - **Acceptance**: REQUIRED T003/V1. Pass: cleanup only after all applicable consumers and production validation pass; preserve reproducible evidence, commands, findings and limits. Smallest check: compare T001/T002 replay and production results to retention inventory before deletion. Evidence: consumer mapping, passed production results and preserved reproduction record. Gate: all consumers validated; otherwise retain proof.
  - **Capabilities**: authorized artifact cleanup and evidence writing.
