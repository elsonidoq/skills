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

Implementation uses one owner-selected exact binding plus independently justified effort per
batch invocation, not the old implementation-task class mapping. This sample intentionally
has no `worker` model override. Keep unrelated reviewer/scout/oracle stage choices separate;
the shown defaults are examples, not verified callable profiles or owner selections.

Planning/advisory selections also use the existing
[qualified seed rubric](../skills/coordinate-implementation/references/batch-routing.md),
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

Use the [qualified seed rubric](../skills/coordinate-implementation/references/batch-routing.md)
and [coordinator contract](../skills/coordinate-implementation/SKILL.md) to assess the batch
and record proposed versus selected profile, rationale and applicable approved guidance or none.
After verifying installed-runtime permissions, callable binding, supported effort and tools at
assignment and dispatch, pass the selected profile explicitly using the runtime's verified
per-run interface (`model: "provider/id:effort"` for pi-subagents). Copy it unchanged into
actual dispatch arguments and inspect the effective configuration before launch: no default,
agent override or setting may silently replace the selected implementation profile. A mismatch
blocks dispatch and returns to capability/owner selection, never automatic substitution.
Do not assume override precedence from this sample alone. Record observed profile separately;
unobservable actual binding/effort stays unknown.

Practical task-local REQUIRED items form the whole unchanged batch verification union before
coding, preserving criterion/check/evidence/gates and optional distinction through both adapters.
Shared checks run once with every distinct mapping; practical combined verification and attributable
failures inform consecutive batches, preserving producer checks before consumers. The sole six-factor
rubric compares closed design/implementation difficulty with weakest oracle quality, check cost and
observability, not scores or defaults. Return concrete item-mapped evidence and inspect focused
per-task commits plus separate evidence checkpoints. Cheap audit checks coverage, criterion relevance,
current revision/environment, consistency, actual diffs/checkpoints and owned scope/gates, not full
rereview. Executor pass/fail/not_verified maps through proof to satisfied/failed/insufficient-evidence;
failed needs demonstrated criterion violation, not merely missing/irrelevant/stale/conflicting/unrun
proof. Retain proven defects and evidence limitations together. Only satisfied REQUIRED items/gates
release dependents; optional green cannot compensate. Required representative-sample manual STOP
needs inspectable sample and explicit user approval before downstream/full expensive operation,
permitting scoped continuation only, never LLM self-review; ordinary tasks need no invented ceremony.
Inadequate approved/legacy contracts return to producing review/renewal, not weaker acceptance.
Passing contracts allow cheap acceptance without a strong per-batch reviewer, while one fresh
independent final review remains required. Empty project guidelines use the qualified seed
without invented success history; relevant approved guidance cannot override source/owner gates.
Inspected diagnosed repair is authorized stronger implementation continuation for exact gaps under
the same original contracts, not generic strong review. Carry current SHA/state, prior proof,
dependencies and invalidations; preserve attempts/valid work, rerun invalidated checks and reuse
only confirmed-valid evidence through the same gates, not a fixed ladder. Unknown/non-model/manual/
permission/contract gaps do not automatically escalate. Clean retry is exceptional: documented
justification, ownership/safe repository mechanics and required owner/project gates first, not
automatic reset/discard. The same SUMMARY/index records factual batch/task dispositions/proof,
first/final selected versus observed profiles/unknowns, contract strength, reused/invalidated items,
exact escalation reason and next selected profile or pending selection, not automatic guideline approval.

Static/symbolic fixtures demonstrate these contracts, not live model performance, supported effort
or authenticated callability. Registry names and effort suffix syntax alone are insufficient;
any live/provider probe requires separate permission and usable runtime support. See
[REQUIREMENTS.md](../REQUIREMENTS.md) for runtime and workflow gates.

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
