# Pi Skill Suite Requirements

This repository is a pi configuration repository. It is **not runtime-portable by design**:
it binds to specific pi packages, pins their versions, and relies on the convention that a
project adopts the suite through the `install-memory` skill before the workflow skills run.

## Runtime

| Requirement | Pin | Verified how | Missing behavior |
|---|---|---|---|
| pi coding agent | 0.87.x (tested with 0.87.1) | `pi --version` | Install or update pi |
| pi-subagents | npm:`pi-subagents@0.73.1` | the `subagent` tool is registered and usable | `Delegation: UNAVAILABLE`; stop and `pi install npm:pi-subagents@0.73.1` |
| pi-ask-user | npm:`pi-ask-user@0.15.1` | the `ask_user` tool is registered | Where a stage permits prose interaction, ask in prose and end the turn; do not proceed past the owner-answer gate or infer an answer. A manager's explicit mandatory preflight may stop earlier. |
| SpecKit toolkit | installed in the **project** when using EPIC stages | detected stage commands and assets exist in the target project | Stop at the affected EPIC stage with a capability report; direct requirements-manager tasking does not require it |
| jev (optional) | `~/.agents/skills/jev` | `command -v jev` or the skill loads | Manual routing in `finish-session-jev` |

All npm pins are exact: pi treats versioned npm specifications as pinned, and `pi update
--extensions` reconciles the checkout without moving the configured ref.

Keep this table in sync with the dependency statements inside the skills. The
`install-memory` skill copies the requirement list into a project's `AGENTS.md` when the
suite is adopted.

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

Memory is part of this skill set; a project adopting the suite is guaranteed a memory
store through `install-memory`. Retrieval and write rules live in the `memory-handling`
skill; `compact-memory`, `finish-session`, `create-epic`, `requirements-manager`,
`coordinate-implementation`, and `initialize-documentation` reference it. There is no "memory unavailable" case in projects
that ran `install-memory`.

## Project docs

`docs/open_issues.md` holds the canonical register of unresolved work
(`track-open-issue`). Documentation owners and the documentation-routing guide are
established by `initialize-documentation` and recorded in each project's instructions.