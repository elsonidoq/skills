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
      "reviewer": { "model": "deepseek/deepseek-v4.1-flash" },
      "scout": { "model": "deepseek/deepseek-v4.1-flash" },
      "oracle": { "model": "anthropic/claude-opus-5" }
    }
  }
}
```

Executable implementation uses approved exact YAML bindings/efforts and a separate executor
intent compatibility assessment, not a subagent batch model override. This sample intentionally
has no worker override; it neither changes runner config nor authorizes dispatch. Requested
versus observed binding remains separate; resource/trust/tool/permission validation still applies.

Planning/advisory selections also use the existing
[qualified seed rubric](../skills/planner/references/profile-selection.md),
with all six applicable factors and independent family/effort rationales, not stage classes.
Implementation-only batching, task-count and REQUIRED-item rules are not planning prerequisites.
Standard `plan_create` alone requires **Sol with exactly medium supported effort** for the entire
same-session specification review/fix → one plan creation → produced-plan review/fix, both direct
and helper execution. Resolve the concrete Sol binding from permitted usable runtime options;
unavailable Sol/medium stops with the precise gap, never substitutes another profile or uses a
standalone helper fallback to bypass the manager. Other independently authorized standalone helper
selections remain separate. These example Claude IDs/defaults imply no current routing authority.
For every planning invocation, verify selection, permissions, tools, callable binding and supported
effort at assignment and dispatch; propagate the exact selected profile unchanged. A default or
agent override mismatch blocks dispatch. Record proposed/selected separately from observed;
unknown actual binding/effort stays unknown. No configuration change is prescribed by this cleanup.

The planning rubric governs planning/advisory choice only. Executable runs do not use LLM
batching, task-count thresholds, model escalation or coordination-feedback obligations. Preserve
whole REQUIRED maps and original gates; the runner executes real checks, audits owned diffs and
creates individual focused task commits. A fresh current full-range independent review is still
required for acceptance. No settings sample can substitute authority/capability proof.

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
