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

### Routine approved-work publication

- **Trigger:** Preparing a delivery branch, publishing approved work, opening its PR or linking its issue in this repository.
- **Action:** Treat a dedicated branch push, PR creation, reciprocal issue/PR links and effect readback as pre-approved for the approved work in `github.com/elsonidoq/skills`. Do not ask again for these routine delivery operations. Exclude unrelated work; preserve target/authentication/data-safety and final acceptance checks. Force-push, merge, closure, deployment, credential changes and additional paid services are not granted by this direction.
- **Provenance:** During issue #45 delivery, the agent asked permission to publish only the issue's change set on a dedicated branch and open/link its PR. The owner answered: “you shouldn't ask me for these things. These operational stuff must be pre-approved”. The specific operations presented in that question bound this guidance.

### Direct implementation executor

- **Trigger:** Selecting executors for future implementation tasks in this repository.
- **Action:** Use the current `.pi/workflow-executor.json` selection: Sol/medium directly, not Terra with Sol reserved only for fallback. Preserve historical runs and review records; do not reinterpret their actual assignments.
- **Provenance:** Explicit owner direction during issue #45: “use Sol/medium for future tasks directly”. Configuration was changed in commit `80090951`.

### Installed agent capability versions

- **Trigger:** Specifying, installing, checking, or using required installed agent capabilities.
- **Action:** Do not require specific versions; verify the applicable capability is usable instead.
- **Provenance:** Owner direction on the Coherence roles runtime-version question: “remove the specific version requirement. It's the fifth time I ask for that. Do not require specific versions”.

### Persistent Coherence role installation

- **Trigger:** Installing Coherence roles or diagnosing missing `coherence-producer` / `coherence-reviewer` agents.
- **Action:** Use the persistent user-agent files installed in `~/.agents/` by `scripts/install.sh`, then verify each role with `subagent get` in a fresh session. Do not restore the former session-start registration setup by copying extensions into project or global `.pi/extensions/`. Follow [Coherence role activation](../README.md#coherence-role-activation) for compatibility and conflict handling.
- **Provenance:** Explicit owner report and retention request in this conversation: “it was finally fixed by installing them in ~/.agents. Save that information”. Installation links and the canonical setup documentation were verified; see commit `9a76ff75a8ca7f2f5315db329bfffc0937353369`. This records the working resolution, not an established cause for every earlier failure.

No technical project gotchas recorded yet.
