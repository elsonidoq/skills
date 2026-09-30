# Pi Skill Suite Requirements

This repository is a pi configuration repository. It is **not runtime-portable by design**:
it binds to specific pi packages, pins their versions, and relies on the convention that a
project adopts the suite through the `install-memory` skill before the workflow skills run.

## Runtime

| Requirement | Pin | Verified how | Missing behavior |
|---|---|---|---|
| pi coding agent | 0.87.x (tested with 0.87.1) | `pi --version` | Install or update pi |
| pi-subagents | npm:`pi-subagents@0.73.1` | the `subagent` tool is registered and usable | `Delegation: UNAVAILABLE`; stop and `pi install npm:pi-subagents@0.73.1` |
| pi-ask-user | npm:`pi-ask-user@0.15.1` | the `ask_user` tool is registered | Ask in prose and end the turn |
| SpecKit toolkit | installed in the **project** | detected stage commands and assets exist in the target project | Stop at the affected stage with a capability report |
| jev (optional) | `jev-cli` | `command -v jev` | Jev-on tracking requires `jev-cli` plus provider auth; manual mode needs neither |

All npm pins are exact: pi treats versioned npm specifications as pinned, and `pi update
--extensions` reconciles the checkout without moving the configured ref.

Keep this table in sync with the dependency statements inside the skills. The
`install-memory` skill copies the requirement list into a project's `AGENTS.md` when the
suite is adopted.

## Jev metrics compatibility and installation modes

The Jev metrics feature has a manual default and an explicit, transactional Jev-on mode.
These are compatibility limits tested by the local installer fixtures, not a statement of
support beyond the versions below.

| Capability | Tested compatibility | Jev-on preflight | Action when unavailable or incompatible |
|---|---|---|---|
| Pi extension API | Pi `0.87.x`, tested with `0.87.1` | `scripts/install.sh --jev-on` requires a `0.87.x` version and verifies the extension registers `jev_rank`, `jev_disposition`, `jev_metrics`, and `/jev-metrics`. | Install Pi `0.87.x` (tested `0.87.1`), then rerun the installer. Manual mode only warns when Pi version wording may drift. |
| JavaScript runtime | Node.js 22 with ES2022 support | Jev-on requires Node major version 22 or later plus `node:test` and ES2022 private-field support. Node 22 is the documented tested baseline; a later runtime passing this gate is not an expanded compatibility claim. | Install Node.js 22 and rerun `scripts/install.sh --jev-on`. |
| Jev CLI and authentication | `jev-cli` `0.6.3` response contract; provider-scoped auth tested with `--provider openrouter` | Jev-on accepts only the tested `jev --version` response for `0.6.3`, then runs `jev auth test --provider <provider>` (default `openrouter`; override with `--jev-provider` or `JEV_AUTH_PROVIDER`). After tracker verification it atomically persists that provider for runtime `jev run - --provider <provider>` calls. The provider-scoped auth check is the only Jev-provider network prerequisite and is run only after explicit opt-in. | Install `jev-cli` `0.6.3`; store the provider key with `jev auth set --provider openrouter` (or your provider); then retry Jev-on. A bare `jev auth test` defaults to `official` and will fail if the key is stored for another provider. |
| Project SpecKit append preset | SpecKit `1.0.12` | A requested project requires a live constitution, project scripts, generated Pi command artifacts, an active tracker, and resolver/introspection proof of one core plus one append layer for all four commands. | Initialize or repair the target SpecKit project and Pi integration, install SpecKit `1.0.12`, activate the tracker first, then retry the complete four-command install. |

### Manual mode

`scripts/install.sh` without `--jev-on` installs the normal suite and deliberately disables the
tracker and removes both the global Jev-on marker and persisted provider file. It does not require
Jev, Jev authentication, the metrics extension, or SpecKit. Missing Jev capability is therefore a
manual-routing condition, not an installation error, and guarded workflows retain their original
manual path.

### Jev-on mode

Use `scripts/install.sh --jev-on` only when measured advisory ranking is intended. It stages the
tracker, completes all preflight checks, verifies the active tracker, and then enables the exact
four global seams as one transaction. A failed preflight reports the prerequisite, observed
status without credential material, a resolution action, and that no optimized seam was enabled.
An activation failure rolls back the tracker, seam marker, and provider state; partial activation
is an error. At runtime the extension provider precedence is: explicit `provider` option, trimmed
`JEV_AUTH_PROVIDER`, `${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}/jev-metrics/provider`, then undefined.
Only `official|vercel|openrouter|custom` are valid. A selected provider produces the exact argv
`["run", "-", "--provider", "<provider>"]`; undefined preserves `["run", "-"]`.

For a project-local SpecKit installation, the user-facing all-or-none command is:

```bash
scripts/install.sh --jev-on --speckit-project <dir>
```

The top-level installer invokes the project helper
`scripts/install-jev-speckit.sh --project DIR [--uninstall]`; the helper has **no** `--jev-on`
flag. It installs or removes only the complete four-command preset through SpecKit's registry and
reconciliation support. It never makes direct source edits to generated
`.pi/prompts/speckit.*.md` files.

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
skill; `compact-memory`, `finish-session`, `create-epic`, `coordinate-implementation`, and
`initialize-documentation` reference it. There is no "memory unavailable" case in projects
that ran `install-memory`.

## Project docs

`docs/open_issues.md` holds the canonical register of unresolved work
(`track-open-issue`). Documentation owners and the documentation-routing guide are
established by `initialize-documentation` and recorded in each project's instructions.