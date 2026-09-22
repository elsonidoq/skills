# OpenCode Configuration

Global OpenCode configuration, commands, and reusable skills for this machine.

## Layout

| Path | Purpose |
| --- | --- |
| `opencode.jsonc` | Global OpenCode configuration, providers, plugins, and MCP servers. |
| `AGENTS.md` | Agent-facing operating policy loaded into sessions. |
| `command/` | Global slash-command prompts. |
| `skills/` | Reusable global skills. Each skill lives in `<name>/SKILL.md`. |

## Portability

Global commands and skills must work across unrelated repositories. They do not encode a project's paths, data,
branch conventions, deployment state, models, or agents. A reusable dependency such as SpecKit, Railway,
Supabase, GitHub, or a configured agent must be discovered before use and have an unavailable fallback.

Project-specific policy belongs in that repository's `AGENTS.md`, `CLAUDE.md`, or local `.opencode/` assets.

## Session Closeout

`/finish-session` preserves current documentation, unresolved work, verified deployment prerequisites, and
trigger-first project memory when those capabilities exist. `/finish-session-jev` adds optional bounded Jev
triage. `/compact-memory` operates only on an explicitly project-associated memory store.

## Updating Assets

Use `skills/writing-skills/SKILL.md` when creating or materially revising a reusable skill. Keep command and skill
changes scoped, verify any optional capability they use, and restart OpenCode after changing configuration-time
assets.
