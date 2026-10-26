# Changed behavioral interfaces

Requirements: [spec.md](../spec.md). Technical basis: [research.md](../research.md). These are compatibility constraints, not new protocol schemas.

## Task author → runtime

- Deterministic required commands occupy an existing executable field (`checks`, `check`, or `required[].check`) once; descriptions are never compiled into shell.
- Unconfigured/optional checks and genuine no-command/no-change outcomes remain supported. Existing six intake checks are unchanged.
- Normal worker return is not task acceptance. Explicit terminal blocked/failed/incomplete work and known unmet required acceptance prevent completion, dependent release and success-path review/fixer. Existing required-check correction remains available; corrected ordinary errors are not terminal failures.
- No prescribed new worker result syntax or extra model call; V1 validates the actual boundary, including delivered answer followed by blocked return.

## Coordinator → repair / retained continuation

Use current selected executor and explicit repair paths. Inspect failure and actual invocation before delegation/continuation; preserve original worker path limits. After repair diff, checks and focused checkpoint, resume only unfinished retained work through supported CLI/parent bridge. Do not replay completed tasks, ask routine permission again, replace live/unknown children, or recursively delegate from a worker. Subsequent routine questions use existing autonomous coordinator triage; material/manual/paid/security gates retain owner authority. Runtime expansion needs demonstrated insufficiency, not an assumed absent API.

## Issue caller → existing tracking entry

One entry owns RCA → create/readback → separate actual-body intent review → evaluated narrow correction/readback. Keep `track-open-issue` routing unless a necessary discovery change is demonstrated. Reviewer configuration comes from the selected project executor, not a global fixed model. Return existing mutation outcome/qualified URL plus review result and uncertainty; do not conflate them. Retain full duplicate discovery, target/auth, sensitive-data, pre-overwrite reinspection, concurrent-content preservation and independent GET. No underlying application repair or repeated-review loop.

## Reviewer → parser / repair

Both `path:717 - defect` and `path:717-723 - defect` convey the same otherwise valid rejection. Preserve findings byte-for-byte through parsing and repair input. Preserve malformed JSON, invalid types and missing-location refusal; syntax acceptance is not substantive acceptance.

## Authorized caller → file ownership

Supported exact-file handoff identifies an explicitly authorized pre-existing target separately from optional path limits. Transfer preserves starting bytes, then permits intended edit and focused checkpoint for tracked-modified and untracked files. No glob/directory/broad allowlist adoption; no synthetic historical ownership. At transfer/edit boundary, refuse unapproved or changed unknown content with filename, operation and corrective action. Normal symlink/path, unrelated staged/dirty work, hooks/signing protections remain. V6 must prove the real input→claim→edit→checkpoint path, not only an isolated bypass helper.
