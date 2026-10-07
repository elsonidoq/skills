# Illustrative TinySpec risk adapter — B

Synthetic task shape only: no real library, execution, approval or model-obedience proof.
B: subtle queued-write/close semantics are disproportionately uncertain and cheaply isolatable;
tested core behavior has substantial leverage before production lifecycle plumbing.

- [ ] T001 Prove queued completion before close in a disposable executable reference.
  - **Depends**: none
  - **Outcome**: determine whether the assumed lifecycle technique works in tested bounds.
  - **Files/interfaces**: disposable proof.py, assertions and retained findings in discovered project owners.
  - **Acceptance**: REQUIRED T001/V1. Pass: representative and adversarial queued writes complete before close, no loss or duplicate completion; failure rejects the technique. Smallest check: real dependency/runtime, observed target version, executable assertions for empty, pending and failure cases (not a mock/name-print script). Commands: `python proof.py --cases representative,adversarial`; expected completion-before-close event order. Evidence: artifact, commands actually run, observed findings, version/runtime/revision applicability and limits. Gate: separately authorized local execution and available target runtime; unrun/unavailable is NOT VERIFIED, not PASS, and blocks dependent reliance.
  - **Capabilities**: separately permitted target runtime and dependency; no installation or live call assumed.
  - **Integration checkpoint**: retain executable artifact, commands and findings for all consumers; failed result blocks assumed consumer approach and returns to correction/replanning and affected approval renewal.

- [ ] T002 Implement production lifecycle using the tested reference.
  - **Depends**: T001
  - **Outcome**: production preserves proven behavior within applicable bounds, with remaining integration risks tested.
  - **Files/interfaces**: production lifecycle and production tests in discovered project repository.
  - **Acceptance**: REQUIRED T002/V1. Pass: inspect and run applicable proof.py, use it as implementation reference, preserve completion-before-close behavior with production tests; a report-only link is insufficient. Smallest check: `python proof.py --cases representative,adversarial` then observed project production test command for shutdown ordering, error propagation and remaining integration risks. Evidence: replay output, applicability check, production assertions/results compared to T001 findings. Gate: T001 passed and still-applicable version/runtime/revision, separate production execution authority; failed/unrun producer cannot release this task.
  - **Capabilities**: editing and observed production runner under approved permissions.
  - **Shared context**: proof artifact, commands, findings and limits retained until all consumers and production validation pass.

- [ ] T003 Clean disposable proof only after validated consumption.
  - **Depends**: T001, T002
  - **Outcome**: disposable reference removed without losing reproducible findings.
  - **Files/interfaces**: disposable proof and established evidence owner.
  - **Acceptance**: REQUIRED T003/V1. Pass: cleanup only after all applicable consumers and production validation pass; preserve reproducible evidence, commands, findings and limits. Smallest check: compare T001/T002 replay and production results to retention inventory before deletion. Evidence: consumer mapping, passed production results and preserved reproduction record. Gate: all consumers validated; otherwise retain proof.
  - **Capabilities**: authorized artifact cleanup and evidence writing.
