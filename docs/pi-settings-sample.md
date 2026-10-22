# Pi settings sample

`~/.pi/agent/settings.json` (user-level) additions can expose this skill suite. Preserve
existing settings and use your local skill path.

```json
{
  "skills": [
    "/path/to/skills"
  ]
}
```

In Paseo, changed tools or extensions require a fresh-session handoff. The fresh agent verifies
the checkout and loaded capabilities; do not instruct the owner to reload or restart the current session.

Executable implementation uses the approved exact executor configuration; this sample neither
changes runner config nor authorizes dispatch. Requested versus observed binding remains separate;
resource, trust, tool and permission validation still applies.

Planning roles use the canonical saved assignments in
[`skills/planner/references/model-assignments.json`](../skills/planner/references/model-assignments.json).
A saved assignment is copied unchanged into its bounded brief and dispatch. A missing, malformed,
unsupported or unavailable assignment stops only the affected role for an owner correction; no
default, recommendation, inference, substitution or fallback is implied. Executable runs do not
use task-count thresholds, model escalation or coordination-feedback obligations. Preserve whole
REQUIRED maps and original gates; the runner executes real checks, audits owned diffs and creates
individual focused task commits. A fresh current full-range independent review is still required
for acceptance. No settings sample can substitute authority/capability proof.

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
child report and enclosing workflow summary. In Paseo, use a fresh-session handoff after changing extension configuration; do not reload or
restart the current session automatically.

## Configuration decisions

Use this section for related configuration choices. Record scope/trigger, rule,
rationale, owner provenance/date, verification, and active/superseded status; keep
runtime-specific settings out of reusable skill contracts.

| Scope / trigger | Decision and rationale | Provenance | Verification | Status |
| --- | --- | --- | --- | --- |
| Global subagent display; lengthy review reports | Prefer compact inline results and explicitly file-only reports to avoid raw completion dumps; assistant summaries should remain concise. | Owner requested global configuration and approved documentation preservation, 2026-10-01. | Installed pi-subagents 0.73.1 configuration docs support `inlineToolDisplay: "summary"`; local extension config contains it. Completion-preview suppression is not claimed. | Active; revise here if superseded. |
