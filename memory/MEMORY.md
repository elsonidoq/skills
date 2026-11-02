# Project gotcha memory index

This repository associates this store through the marked Coherence contract in
`AGENTS.md`. Read this entire index first, then only entries whose triggers match the
current action. Recheck after writes. It carries verified, non-obvious, trigger-first
gotchas with consequences and evidence pointers, plus explicit future-directed owner
guidance with provenance and a concise trigger/action. Do not use global memory as a
substitute or store secrets, completed-work inventories or fabricated knowledge.

## Owner guidance

### Parent-turn notifications

- **Trigger:** Reporting routine task transitions/completions or steering-status updates.
- **Action:** Routine task transitions/completions and steering-status updates must not wake the parent agent or require acknowledgment. Only agent questions and terminal workflow completion, whether success or error, should trigger a parent turn.
- **Provenance:** Explicit current owner feedback in the T005 implementation launch conversation; guidance is recorded verbatim, not inferred from historical evidence.

### Routine technical decisions and review scope

- **Trigger:** Resolving implementation trade-offs or continuing review of a corrected change.
- **Action:** Handle routine technical decisions autonomously; ask the owner only for product decisions or material scope creep. Preserve mandatory explicit permission gates rather than treating this preference as consent. When the owner requests correction-only review, assess the correction and affected behavior instead of re-reviewing areas already confirmed correct.
- **Provenance:** Explicit owner direction in the workflow-monitor implementation conversation: “Do not ask me again about these decisions,” clarified as “Only product or scope creepy”; later, “yes, but do not re-review what it has already reviewed and confirmed it's correctness.”

### Routine repair authorization

- **Trigger:** Continuing routine repair/review rounds after the owner has explicitly authorized them within a bounded implementation scope.
- **Action:** Do not repeatedly ask for the same routine authorization. Use the supported run-and-scope-bound authority mechanism; preserve actual material scope, manual, paid, security, data and external-action gates. A conflicting runtime consent rule needs a scoped correction, not fabricated owner replies or silent bypass.
- **Provenance:** Explicit owner feedback during #30 implementation: “Why do you keep asking for these authorizations? Yes I authorize them all” and “Stop asking me for authorization for routine things like that.” The owner then approved the proposed scoped policy correction and retained continuation with “Go ahead.” This records the conversational preference, not blanket permission for unrelated runs or actions.

### Installed agent capability versions

- **Trigger:** Specifying, installing, checking, or using required installed agent capabilities.
- **Action:** Do not require specific versions; verify the applicable capability is usable instead.
- **Provenance:** Owner direction on the Coherence roles runtime-version question: “remove the specific version requirement. It's the fifth time I ask for that. Do not require specific versions”.

No technical project gotchas recorded yet.
