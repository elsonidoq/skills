---
name: handoff-prompt
description: Use when preparing a Cerca continuation prompt for a fresh OpenCode session or subagent that lacks the current conversation.
---

# Handoff Prompt

Produce one copyable Markdown prompt that leads with the intended outcome.
Reference durable context; carry ephemeral context. A fresh agent can read files
in its workspace but cannot recover this conversation.
Use `/handoff-prompt <next goal>`. This is a global skill
(`~/.config/opencode/skills/handoff-prompt/SKILL.md`), available in any OpenCode
project — there is no project-local wrapper command. Restart OpenCode after
skill changes.

## Assemble the context

Identify whether the next agent is implementing, planning, researching, or reviewing.
For implementation, name the next dependency-ready unchecked task ID and acceptance
criteria; do not blindly choose the first checkbox if its prerequisites are unmet.
For planning/review/research, name the desired artifact or claim and its scope.

Verify the workspace, branch and git status. Read `AGENTS.md` and follow its current
plan pointer if it is an actual path. Read the applicable constitution; identify a
template constitution as uninitialized rather than claiming it sets project policy.

For epic work, resolve source file and canonical epic heading from the selected
spec's metadata or matching manager state under `.opencode/epics-workflow/` if present.
For legacy state, use the manager's State migration rules, not an old filename as
proof of identity. Read the feature STATE.md when present for implementation progress.
That state's `epic_file` field names the actual epic document; read its own
preamble as this project's product context — there is no single hardcoded epic
bundle file. Read only the selected epic and explicitly cited cross-epic sections.
Preserve Settled decisions, Non-obvious facts, NOT included, target shapes, and
approved §12 answers. Follow source/dependency rules in the `epics-manager` skill
without launching its workflow.

Verify every cited input exists. Resolve ADR identifiers to actual paths, checking
acceptance status when a consumer needs them. Clearly label proposed output paths
and optional references as future/optional. Do not list missing code, datasets or
ADRs as mandatory reads for the agent tasked with producing them.

Include relevant spec/plan/tasks/research/contracts only when they exist. If they
accurately contain the design, point to them instead of repeating them. Carry:

- Decisions and rationale that exist only in the conversation, with who approved
  them; distinguish proposals from settled decisions.
- Scope fences, rejected alternatives, deferrals and revisit gates.
- Work completed, verified results, incomplete work and exact next step.
- Runtime surprises, cross-task dependencies, evidence-backed traps and blockers.
- Any required inputs the next workspace must receive; uncommitted files are not
  automatically available in another checkout.

Keep artifact-backed prompts short (aim under 400 words); include as much additional
context as needed when the conversation is the only source.

## Verification and mechanics

Use cheap checks appropriate to the current stage, from the actual repository root:

- Before a feature exists: direct input/template checks; no feature prerequisite run.
- With a spec: bind `SPECIFY_FEATURE_DIRECTORY` to its absolute directory and verify
  its feature.json pin using the manager's feature-context rules, then run
  `check-prerequisites.sh --json --paths-only` and check spec.md directly.
- With plan and spec: `check-prerequisites.sh --json`.
- For implementation with tasks:
  `check-prerequisites.sh --json --require-tasks --include-tasks`.

The script is `.specify/scripts/bash/check-prerequisites.sh`. Verify returned paths
match the handoff's feature. Quote checks actually run and their results; if a result
is from an earlier run, identify it as such. Do not repeat costly tests merely to
produce a prompt. State NOT RUN and why when a check is unavailable or outside scope.

Use actual OpenCode command names, for example `/speckit.plan` or
`/coordinate-implementation`. The Speckit instructions live in
`.opencode/command/speckit.plan.md`; the coordinator is the global
`coordinate-implementation` skill (no project-local file). For other stages, use the
manager's command table and verify the corresponding file. In a delegated prompt,
tell the agent to read and follow the command body with explicit stage context as
`$ARGUMENTS`; slash commands are not shell executables or callable agent tools.
Do not launch nested CLI sessions or treat generated handoffs as automatic gates.

Delegate via OpenCode's `task` with `subagent_type: "general"`, `description`, and
the verified `prompt` if appropriate and permitted, or work locally with a separate
review pass. A fresh task receives no prior conversation; a returned `task_id` can
resume only that same task. Delegates share the checkout, not an isolated worktree.
The tool has no per-call model parameter; report use of the configured agent model.
If the user needs a particular model, session `--model provider/model` or agent
`model` configuration must use a verified identifier; do not invent or change pins.

Carry authorization and limits accurately. Open owner choices stay open: use a
permitted OpenCode `question` tool in the coordinator (not the general subagent),
or, if unavailable or noninteractive, ask a concise question in the final response
after saving progress. Do not invent answers to make the prompt appear complete.
Live/costly external work needs the applicable authorization; record what remains
blocked and the first useful local step.

Close the prompt with the exact working directory, branch, path binding, and
verification baseline so continuation does not depend on the original shell.
Launch a fresh session with `opencode <absolute-workspace>` and supply the prompt
or named command there. Existing chats can resume with `opencode --session <session-id>`
from the verified workspace, but session history and `todowrite` are not substitutes
for manager JSON or feature STATE.md. Carry pending gates and accepted answers even
when no session ID is available; do not invent a persisted handoff path.
