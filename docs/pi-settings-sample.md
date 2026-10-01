# Pi settings sample

`~/.pi/agent/settings.json` (user-level) additions that make this skill suite work. Edit
while pi is not running, then run `/reload` inside the next session.

```json
{
  "skills": [
    "/Users/elsonidoq/.config/opencode/skills"
  ],
  "subagents": {
    "defaultModel": "deepseek/deepseek-v4.1-flash",
    "agentOverrides": {
      "worker": { "model": "deepseek/deepseek-v4.1-flash" },
      "reviewer": { "model": "deepseek/deepseek-v4.1-flash" },
      "scout": { "model": "deepseek/deepseek-v4.1-flash" },
      "oracle": { "model": "anthropic/claude-opus-5" }
    }
  }
}
```

The `subagents` block implements this suite's model-class mapping
([REQUIREMENTS.md](../REQUIREMENTS.md)): `sonnet-class` work runs on
`deepseek/deepseek-v4.1-flash`; `opus-class` advisors run on `anthropic/claude-opus-5`.
Per-run overrides from `coordinate-implementation` take precedence over these
`agentOverrides` values.

The `packages` array is maintained automatically by `pi install` (see
[REQUIREMENTS.md](../REQUIREMENTS.md) for the exact pins).

Resource paths in user settings resolve from the agent directory; paths in project
settings resolve from the project `.pi` directory. Absolute paths and `~` are supported.

## Compact subagent output

Merge this into `~/.pi/agent/extensions/subagent/config.json`, **not** into Pi's
`settings.json` or its `subagents` object. Preserve other existing keys:

```json
{
  "inlineToolDisplay": "summary"
}
```

This keeps each inline subagent tool result to one stable row without child-output
previews. It does not suppress separate completion-notification previews or change
model-facing output. Detailed reports still require an explicit launch binding:
`output: "review.md", outputMode: "file-only"`. Use separate output paths for the
child report and enclosing workflow summary. Restart Pi after changing extension
configuration; `/reload` is the suite's resource-refresh step after skill changes.

## Configuration decisions

Use this section for related configuration choices. Record scope/trigger, rule,
rationale, owner provenance/date, verification, and active/superseded status; keep
runtime-specific settings out of reusable skill contracts.

| Scope / trigger | Decision and rationale | Provenance | Verification | Status |
| --- | --- | --- | --- | --- |
| Global subagent display; lengthy review reports | Prefer compact inline results and explicitly file-only reports to avoid raw completion dumps; assistant summaries should remain concise. | Owner requested global configuration and approved documentation preservation, 2026-10-01. | Installed pi-subagents 0.73.1 configuration docs support `inlineToolDisplay: "summary"`; local extension config contains it. Completion-preview suppression is not claimed. | Active; revise here if superseded. |
