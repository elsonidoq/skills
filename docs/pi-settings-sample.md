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