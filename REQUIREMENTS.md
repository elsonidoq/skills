# Coherence — Pi Skill Suite Requirements

This repository is a pi configuration repository. It is **not runtime-portable by design**:
it binds to specific pi packages, pins their versions, and relies on the convention that a
project adopts the suite through `initialize-coherence` before the workflow skills run.

## Runtime

| Requirement | Pin | Verified how | Missing behavior |
|---|---|---|---|
| pi coding agent | 0.87.x (tested with 0.87.1) | `pi --version` | Install or update pi |
| pi-subagents | npm:`pi-subagents@0.73.1` | the `subagent` tool is registered and usable | `Delegation: UNAVAILABLE`; stop and `pi install npm:pi-subagents@0.73.1` |
| pi-ask-user | npm:`pi-ask-user@0.15.1` | the `ask_user` tool is registered | Where a stage permits prose interaction, ask in prose and end the turn; do not proceed past the owner-answer gate or infer an answer. A manager's explicit mandatory preflight may stop earlier. |
| SpecKit toolkit | installed in the **project** for planner's Standard path | detected stage commands and assets exist in the target project | Stop at the affected Standard stage with a capability report; TinySpec/direct tasking does not require it |
| jev (optional) | `~/.agents/skills/jev` | `command -v jev` or the skill loads | Manual routing in `finish-session-jev` |

All npm pins are exact: pi treats versioned npm specifications as pinned, and `pi update
--extensions` reconciles the checkout without moving the configured ref.

Keep this table in sync with the dependency statements inside the skills. The
`initialize-coherence` skill records the approved requirement list in the project's
instructions during adoption. It reports missing prerequisites without installing them;
its mandatory question/approval-contract gates stop when unavailable.

## Model class mapping

The pipeline skills label work with two model classes. The mapping below is the
configuration used by this suite and must resolve to usable options on the configured
providers. It is enforced by the `subagents.agentOverrides` sample in
[`docs/pi-settings-sample.md`](docs/pi-settings-sample.md); skills must never hard-code a
provider/model ID — they verify that usable options exist and ask the owner to choose.

| Class | Meaning | Model |
|---|---|---|
| `sonnet-class` | bounded, well-specified implementation work | `deepseek/deepseek-v4.1-flash` (fallback `deepseek/deepseek-v4-flash`) |
| `opus-class` | work that cannot be safely decomposed | `anthropic/claude-opus-5` or `openai/gpt-sol-latest` |

## Memory contract

Successful adoption through `initialize-coherence` establishes an approved project-memory
association and index, or validates a compatible existing one. Merely invoking initialization
does not establish readiness: missing capabilities, denied approval or missing structure block
it. Owner-selected paths remain valid; bounded refresh preserves existing memory and custom
policy. Retrieval and write rules live in `memory-handling`; `compact-memory`, `finish-session`,
`planner`, `tiny-spec`, `coordinate-implementation`, and `initialize-coherence` reference it.
A missing association routes to `initialize-coherence`, never a guessed global store.

## Project docs

`docs/open_issues.md` holds the canonical register of unresolved work
(`track-open-issue`). `initialize-coherence` preserves or establishes documentation
owners/indexes and a verified project-specific documentation-routing guide, recording them
in approved project instructions. Persistent-database projects also require an authoritative
schema owner or documented set, even without a naming convention. Initially clean projects
may initialize verified content; non-clean projects first require fresh read-only investigation
and approved shell/index bounds, with no substantive documentation writes. Missing required
structure blocks readiness; empty/stale substantive content remains planner work, not completed
by a shell. `finish-session` checks owner/index/routing/schema existence without initializing
or auditing them.