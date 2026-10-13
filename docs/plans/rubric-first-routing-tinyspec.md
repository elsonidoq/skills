# Rubric-first routing — TinySpec

## Status, provenance and outcome

Owner-selected TinySpec; preparation only. Implementation remains on hold. Separate tasks,
planner review and current-content combined owner approval are still required; this source
is not an implementation authorization or an implementation-task profile assignment.
Preselection gate: `NO_BRAINSTORM_NEEDED` (settled bounded design).

The request exists in the planning conversation. The owner quoted the coordinator:
“All use openai-codex/gpt-6.1-sol:medium. Sol is already launch-verified here; smaller
profiles are only cataloged, not verified...” and requested grounded rubric selection
instead. The owner accepted the bounded design, requested planner, explicitly selected
TinySpec through `ask_user`, and approved `openai-codex/gpt-6.1-sol:medium` for this
source producer, subsequent task producer and planner review. That exact planning
selection is not evidence that Sol is universally preferable, nor authorization to
probe alternatives. The quotation is owner-supplied problem provenance, not independently
reconstructed tool history. No inference about actual previous child calls is required.

Beneficiaries are owners and planning/implementation coordinators: suitable family and
effort proposals must arise from task shape and weakest material oracle, not previous
launch history. Availability checking must remain a separate, strict dispatch gate.
The verified production baseline is `a32d9ff8c4808f63d543fbd2041fbb4f67501d57`, with
initially clean index/worktree and usable Git identity. This production writes only this
source and its discovery row in [plans index](index.md).

## Settled owner constraints (verbatim)

- 'rubric first, capability verification second'
- 'Prior launch success establishes availability, not superiority'
- 'Compare suitable family/effort options—even when an alternative has no previous launch history'
- 'If verification is insufficient, surface the gap'
- 'Ask for the necessary authorization or an explicit fallback choice—not silently substitute Sol'
- 'Exact-profile owner approval, supported effort, permissions, no unauthorized provider probes, and inspected-failure retry rules remain intact'
- 'model variety is not itself a goal'

## Scope and governing evidence

Included: the existing shared routing rubric, coordinator selection/dispatch language,
shared planning consumers, narrow regression sensitivity and current explanatory docs.
The canonical operational owner remains
[batch-routing.md](../../skills/coordinate-implementation/references/batch-routing.md),
not this source or a new research database/framework. Expected consumers are
[coordinator](../../skills/coordinate-implementation/SKILL.md#prepare-approved-execution),
[planner Shared routing selection](../../skills/planner/SKILL.md#shared-routing-selection),
[architectural helper](../../skills/delegating-architectural-planning/SKILL.md), and their
existing direct/advisory adapters. Align
[REQUIREMENTS](../../REQUIREMENTS.md#planningadvisory-selection),
[README](../../README.md) and necessary existing documentation routing descriptions
only where they otherwise contradict the corrected rule.

Preserve [AGENTS](../../AGENTS.md), [constitution](../../.specify/memory/constitution.md),
[SDD source quality](../best_practices_spec_driven_development.md),
[dependency research](../../skills/planner/references/dependency-research.md),
[early risk reduction](../../skills/planner/references/early-risk-reduction.md), and
[task checkpoints](../../skills/memory-handling/references/task-commit-contract.md).
The adopted [memory index](../../memory/MEMORY.md) has no gotchas; relevant
[coordination guidelines](../../memory/coordination/GUIDELINES.md) have no approved
guidance. Apply explicit none with uncertainty; do not fabricate learned history.

Excluded: model diversity quotas, fixed universal model ladders/defaults, benchmark-only
eligibility, new benchmark research, provider probes, runtime/Git configuration,
installation, pushes, operational implementation during planning, task creation by this
producer, review/STATE/memory evidence or guidance writes, new persistence infrastructure,
and historical artifact migrations. Standard `plan_create` retains its owner-mandated
Sol/exactly-medium supported-effort exception for the entire direct/helper pass; this is
not a capability ranking. Other stages retain existing dialogue/approval/independence gates.

## Evidence classification and version applicability

**Reused qualified prior:** [canonical batch research](../../specs/002-batch-routing-contracts/research.md),
“Inspected representative signals and limits” and Decisions 1–4, grounds the existing
six-factor prior. Different SciCode, AutomationBench-AA, Terminal-Bench and small custom
coding harnesses/snapshots are not comparable Pi success rates or a universal ranking.
No new benchmark research is necessary for this bounded policy correction. Historical
runtime/ownership descriptions in that research are provenance, not current workflow policy.

**Repository-derived regression target:**
[ComparativeRoutingTests](../../skills/coordinate-implementation/scripts/test_batching_contract.py)
(at baseline approximately lines 819–859) requires “suitable smaller verified, permitted
alternative”, “none is verified/permitted”, and authors `alternative_unavailable` →
`symbolic/sol:low`. These fixtures and the matching rubric wording encode the selection
restriction to correct. They are not proof of the actual quoted agent's invocation history.
Coordinator/planner already preserve exact selection and unavailable-support stops; retain
those clauses while removing comparison eligibility tied to prior verification.

**Installed authoritative evidence inspected read-only:** `pi --version` reports 0.87.1;
installed `pi-subagents/package.json` reports 0.73.1. Evidence pointers are package-relative,
not portable global operational paths:

- Pi 0.87.1 `docs/models.md`, “Select a model”/“Troubleshooting”: `/model` shows choices
  with usable authentication and `/thinking` limits choices to supported levels. Its
  authentication sections and `docs/providers.md` describe credential resolution, not
  guaranteed provider acceptance. Do not read or retain credential values.
- Pi coding-agent `dist/core/model-registry.js:getAvailable` delegates to the active
  runtime's `getAvailableSnapshot`; `getAll` is a different catalog surface. RPC
  `dist/modes/rpc/rpc-mode.js:get_available_models` exposes that available snapshot.
- Pi AI `dist/models.js:getSupportedThinkingLevels` and `clampThinkingLevel` implement
  model-specific level choices and possible clamping. For native Codex,
  `dist/api/openai-codex-responses.js:streamSimple` and `buildRequestBody` clamp and map
  reasoning effort through `thinkingLevelMap`. Unsupported selection must stop rather
  than quietly accept clamping or an omitted/different requested effort.
- pi-subagents 0.73.1 `docs/tool-reference.md`, `model` parameter: an exact `provider/id`
  plus suffix carries per-run thinking; standalone `thinking` is ignored on dispatch.
  `docs/models.md`, precedence/model scope/thinking ceiling sections, describe explicit
  overrides and policy gates. Its provider-catalog refresh/profile-check commands perform
  live probes and are **not** passive verification options.
- pi-subagents `src/api/preflight.js:resolveSubagentLaunchContract` resolves model scope,
  thinking ceiling, tool plan and launch binding; it warns when no host available-model
  snapshot is supplied. `src/shared/model-info.js:getSupportedThinkingLevels` has permissive
  defaults when model metadata is missing. Generic suffix parsing or that default output
  alone is therefore insufficient support evidence.

These sources settle a non-probe readiness contract below. They do **not** attest that
any concrete alternative is currently authenticated/supported here. No alternative
snapshot, provider call, auth resolution command or live launch was performed in source
production. Observed model/effort is not inferred from the approved planning selection.

## Approach and deterministic routing behavior

Use the existing brief/table and runtime return fields, not a new score, schema or ledger.

**Assessment and proposal precede readiness:** assess all six factors for each invocation:
residual reasoning; agentic/tool depth; verification blind spots (oracle quality, cost,
observability and weakest material condition); scope/coupling; failure cost/reversibility;
applicable approved guidance or explicit none. Implementation uses ordered coherent batches;
planning uses applicable invocation scope, without importing task-count/batching prerequisites.

Record separate comparative **Family rationale** and **Effort rationale** against suitable
options. Closed design, bounded tooling, cheap reversible recovery and strong cheap oracles
can positively justify a smaller candidate even with zero previous launches. Explain its
sufficiency, or explain the concrete shortfall that justifies a stronger choice. Effort
follows remaining inference independently of family. A mandatory medium requirement excludes
low; a default preference allowing low does not. Deep stateful recovery/weak but adequate
oracles can justify stronger capability; inadequate contracts or unresolved design stop at
producing review/owner clarification, not model escalation. Compare relevant alternatives,
not every catalog entry. No benchmark row or prior-launch requirement filters suitability.

**Keep readiness states separate:** a cataloged candidate may be proposed as pending readiness.
Supported/authenticated runtime-ready means enough current non-probe evidence for the exact
execution context; prior observed launch is a separate historical fact, not a prerequisite
or a comparative quality claim. Unknown actual model/effort remains unknown.

**Sufficient non-probe runtime verification** requires the conjunction of:

- Exact provider/id resolved in the active host's available/authentication-aware runtime
  snapshot (or equivalent existing `/model` evidence), applicable to the intended child
  provider/environment. A bare catalog/list-models entry or configured credential presence
  alone is insufficient. Missing/stale/opaque evidence is an exact readiness gap.
- Authoritative model-specific supported-level evidence from the installed runtime's
  supported choices, with inspected applicable provider adapter/mapping confirming that
  the requested effort survives unchanged in meaning. Reject unsupported choices,
  clamping, ambiguous aliases/defaults and missing material mapping evidence. Registry
  `reasoning`/thinking flags or a syntactically accepted suffix alone cannot establish this.
- Current child launch-resolution evidence agrees with exact selected binding/effort and
  permitted model scope/thinking ceiling; tool/extension access, mutation permissions,
  execution environment and owner gates fit. Parent availability does not automatically
  prove detached-child availability. Use current known evidence; no speculative auth or
  configuration execution to fill gaps.

This conjunction proves runtime-declared launch readiness, not successful live provider
acceptance, quota, network health or obedience. It does not demand a previous launch.
Only use passive evidence already available or safe permitted read-only inspection; auth
refresh, credential commands, live discovery/probes and profile refresh are not implicitly
authorized by selection or by this contract. If material evidence cannot be obtained without
such operations, report the precise gap and ask for necessary bounded authorization or an
explicit fallback choice. Do not mark readiness true from unknown evidence.

**Approval and dispatch:** present rubric proposal/rationales and readiness status/gaps first.
Obtain one exact owner-selected profile; an approval while readiness is pending approves
selection only, not probes or launch. Dispatch requires both owner selection and complete
readiness/permission/tool gates, checked at assignment and dispatch. On insufficiency stop
the affected launch, retaining the recommendation and uncertainty. An explicitly requested
fallback must receive its own justification, readiness checks and exact selection; never
auto-select Sol because another candidate is unlaunch-tested or unavailable. Preserve proposed,
selected and observed separately, exact `model: "provider/id:effort"` arguments and settings/
agent-default mismatch stops. Inspect failed run/invocation/partial commits/checks before
any targeted retry/repair; unknown failure blocks blind restart. No stronger model repairs
missing permission, support, requirements or oracle adequacy.

## Observable acceptance and smallest sufficient validation

| ID | Required observable / pass criterion |
| --- | --- |
| A1 | Existing named closed-design/strong-cheap-oracle scenario assesses all six factors and positively recommends suitable symbolic smaller family/effort with independent comparative rationales, even when never previously launched; pending readiness is not inadequacy. |
| A2 | A catalog-only or otherwise insufficiently verified proposed smaller candidate retains its recommendation, exposes the exact binding/auth/effort/context/tool/permission gap and blocks dispatch; asks for bounded authorization or explicit fallback choice, never `alternative_unavailable` → automatic Sol. |
| A3 | Current adequate non-probe runtime readiness plus exact owner selection allows an unlaunch-tested candidate through dispatch preparation; prior observed launch is neither required nor misreported. Missing actual support still stops. |
| A4 | Named stronger-choice scenario explains smaller candidate's concrete shortfall using weakest adequate oracle/stateful recovery/coupling, separately justifies effort; suitability-only Sol rationale is rejected. Inadequate contracts stop at producing review, not escalation. |
| A5 | Strict-medium versus default-medium-permitting-low, unsupported effort, permission/tool denial, missing owner selection and settings/default mismatch cases preserve stop/exactness semantics. Standard `plan_create` Sol/medium exception remains unchanged across direct/helper pass. |
| A6 | Proposed/selected/observed remain distinct; selected exact profile reaches dispatch unchanged, unknown actual profile stays unknown. Failed-run inspection and targeted owner-approved repair remain mandatory; no unauthorized probes, fabricated guidance, benchmark eligibility filter or diversity quota appears. |
| A7 | Rubric, coordinator, planning/helper consumers and current explanatory docs have consistent assessment → comparison/proposal → readiness → exact approval/dispatch semantics; canonical evidence stays the shared rubric and qualified prior. |

Use narrow mutations/negative assertions in existing ComparativeRoutingTests and exact-profile
fixtures: the old verified-only comparison clause and authored unavailable→Sol case must be
rejected by the corrected checks. Symbolic records should distinguish proposal, readiness and
dispatch outcome so positive proposal cannot be mistaken for launch permission. Targeted clause
inspection across the named consumers covers A7; existing coordinator intake/batching/state and
relevant planner/helper contract checks cover preservation only where affected. Keep every
criterion mapped to smallest sufficient check and concrete expected proof in later separate tasks;
optional green cannot replace a failed/unrun REQUIRED check. Source verification itself is
settled-requirement coverage, relative link resolution, actual source/index diff inspection and
`git diff --check`, not feature acceptance.

## Early risk rationale, sequencing and residual limits

Omit a separate disposable real-runtime prototype: this change is a bounded instruction/fixture
policy seam, not a difficult isolatable runtime algorithm. Installed source inspection resolves
names, version behavior and passive-evidence limits; a script printing registry names would not
prove auth, supported effort or model obedience. The high-risk remainder—actual instruction
following/provider acceptance—is non-isolatable from a real permitted invocation. Static/symbolic
checks demonstrate regression sensitivity only, never live obedience.

The corrected shared owner and regression expectations are the producer; coordinator/planning/
helper consumers must inspect and exercise the applicable existing checks before relying on it;
production contract tests and cross-consumer clause consistency must pass before acceptance.
Retain applicable fixtures/evidence until all consumers validate; no disposable proof cleanup is
needed. Actual model-obedience validation remains NOT RUN and requires separately authorized
real-system execution with usable exact profile/tools/permissions, representative closed-design
and adversarial readiness-gap inputs, visible proposal/rationales and no-launch-on-gap observables.
No such execution is authorized by this planning-only source. An unavailable or failed required
runtime check blocks claims relying on it; it is not technical disproof by itself. Contradictory
runtime evidence or failed regression returns affected source/consumer decisions to producing
review and existing approval renewal, preserving valid work and inspected failure evidence.

No material design choice is deferred or filled by a speculative default. Concrete alternative
readiness is intentionally unresolved until a future invocation supplies the defined evidence;
this blocks that dispatch, not comparison or source production. No live performance claim or
implementation acceptance is made. Later authorized global-contract changes require `/reload`
in pi; this source-only checkpoint does not change global operational assets.
