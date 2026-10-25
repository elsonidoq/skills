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

No technical project gotchas recorded yet.
