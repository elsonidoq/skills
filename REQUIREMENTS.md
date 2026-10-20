# Coherence — Pi Skill Suite Requirements

This repository is a pi configuration repository. It is **not runtime-portable by design**:
it binds to specific pi packages, pins their versions, and relies on the convention that a
project adopts the suite through `initialize-coherence` before the workflow skills run.

## Runtime

| Requirement | Pin | Verified how | Missing behavior |
|---|---|---|---|
| pi coding agent | 0.87.x (tested with 0.87.1) | `pi --version` | Install or update pi |
| pi-subagents | npm:`pi-subagents@0.73.1` | the `subagent` tool is registered and usable | `Delegation: UNAVAILABLE`; stop and `pi install npm:pi-subagents@0.73.1` |
| pi-ask-user | npm:`pi-ask-user@0.15.1` | the `ask_user` tool is registered | Where a stage permits prose interaction, ask in prose and end the turn; do not proceed past the owner-answer gate or infer an answer. A manager's explicit mandatory preflight may stop earlier. |
| SpecKit toolkit | installed in the **project** for planner's Standard path | detected integration/version inventory matches real readable, nonempty commands, templates and scripts, including permissions/references | Stop at the affected Standard stage with a capability report; TinySpec/direct tasking does not require it |
| jev (optional) | `~/.agents/skills/jev` | `command -v jev` or the skill loads | Manual routing in `finish-session-jev` |

All npm pins are exact: pi treats versioned npm specifications as pinned, and `pi update
--extensions` reconciles the checkout without moving the configured ref.

Keep this table in sync with the dependency statements inside the skills. The
`initialize-coherence` skill records the approved requirement list in the project's
instructions during adoption. It reports missing prerequisites without installing them;
its mandatory question/approval-contract gates stop when unavailable.

On every initialization, including compatible adoption and refresh, the bounded exception
is proposal-first project-local SpecKit assets, not global tooling installation. Discover
integration/version/script/options and verify commands, templates and scripts against an
authoritative expected inventory and actual files. Complete valid/custom assets remain
untouched; compatible association stays an instructions/memory no-op, not an early exit.
Missing/incomplete assets block initialization-ready claims. Use an installed official CLI
with a source-verified recipe, explicit integration/options, isolated fresh staging and
approved missing-file-only transfer; reconcile only approved necessary manifest entries.
Preserve custom assets, constitution and metadata; no blanket `specify init --here --force`
against an existing repository. Missing usable CLI or unknown safe recipe blocks repair;
do not silently install/upgrade tooling. Conflict/drift/failure stops without readiness,
automatic retry or destructive rollback; report partial outputs. Other missing runtime prerequisites
retain stop/report behavior. TinySpec/direct tasking still does not require SpecKit, and
Standard capability gates remain. After global skill changes, run `/reload` inside pi.

When SpecKit metadata is absent (not malformed/conflicting), inspect supported installed-CLI
choices and version read-only, propose from current runtime/repository evidence and obtain
material owner selection via `ask_user` without guessed/silent defaults. The installed CLI
version can supply the absent recorded version. Selection grants no writes: the exact
staging/target proposal still needs explicit approval; unresolved selections/recipes stop.

## Executable implementation runtime

Coordinate Implementation is a deterministic Python LangGraph1.2.16/SQLite-saver3.1.2 runner,
with PyYAML6.0.3/jsonschema4.26.0 and thin pinned Pi SDK0.87.1 Node host. Python >=3.10
(3.12.3 tested), compatible Node22.23.3–22.x, local Git/SQLite and approved delegated Linux
cgroup-v2 own-child capability are required for mutation. No daemon/server is required.
Source and wheel resource discovery includes YAML/schemas/host/package lock. Installation
is optional explicit isolated setup, never ordinary-use provisioning/global auth/settings changes.
Use the actual CLI --help and [operating/schema owners](docs/coordinate-implementation.md).

The runner alone selects tasks/sessions from approved exact config, owns SQLite persistence,
executes/audits real REQUIRED/gates and focused owned-path commits/checkpoint reconciliation.
Workers never stage/commit or select work; planning/standalone/bootstrap writers keep existing
checkpoint duties. One writer, earlier producer verification/checkpoint before consumers,
unknown/live effects block replacement. Preserve hooks/signing, unrelated index/custom/STATE/
history and original approvals. No LLM batches/local task thresholds/escalation or execution
coordination-feedback obligations. Only satisfied REQUIRED items/gates release dependents;
optional green cannot compensate, missing proof is insufficient-evidence. Fresh independent
full-range review and resolved findings are required for acceptance, separate from implementation
completion. Repairs retain original contracts and configured limits; unknown causes stop retry.

Exact provider/model/effort, resources/tools/permissions and requested versus observed evidence
remain mandatory. Root executor class/effort intent is captured before architecture/decomposition,
separate from planning/reviewer profiles, with assumptions/provenance/resolution/rationale.
Approved compatible implementation/repair bindings must be resolved before dispatch; changed
intent assesses affected detail/boundaries and renews affected producing approval without silent
substitution or whole-plan regeneration. Ordinary model tokens have no financial approval/cap/
reservation. Separately chargeable service actions need purpose/cost-impact and scoped authority.

Lean execution uses five boundary facts—valid work, usable selected configuration,
scoped current authority, one-writer safe ownership and runnable REQUIRED checks. Optional
telemetry is observed, not an execution veto; scoped external action and own-child custody
remain required. This approved refactor is delivered through bounded instruction-managed
owner-selected writer checkpoints, not by launching the runtime under refactor.

Durability uses existing LangGraph/SQLite and ordered task/check/decision/review/effect history.
Compatible runtime revisions may append new attempts only at settled boundaries; whole-code
identity is not permanent eligibility. Current configuration/schema/authority incompatibility
and incomplete SDK/tool/Git effects still block affected replay. Retained actual YAML/graph and
private semantic SQLite reader v1 are documented in the operating/schema owners. Old pins and
records remain historical/read-only or explicitly unsupported, never auto-migrated. Optional
metrics/publication cannot veto authoritative results; recorded state is not observed liveness.
Monitor-v1 needs separate reader/data-model/source/task approval renewal for retired Engine-pin
and parent/proof assumptions; no unchanged-app compatibility or monitor remediation is implied.

Standalone CLI needs no Paseo. Interactive-parent requires selected public transport (Paseo0.9.2
tested), verified original parent/session and registered ask_user capability. Answers derive from
actual scoped original-session tool results, not launch/ACK/provenance chains. Uncertain sends
are not blindly retried/reasked. Full-range review uses actual base/head/source/evidence references
and read-only file continuation, not binary bundles or document-byte/SDK-delivery attestation.
Missing UI stays pending; never silent polling or fabricated answers. Original-conversation
answer pin overrides greedy session selection. Missing/incompatible/unsettled original blocks,
never fresh substitution. Received/queued/SDK-delivered/worker-acknowledged are separate.
Host exit stops work, no background continuation. Cgroups cover trusted single-host/same-UID
local processes, not filesystem sandboxing, remote/adversarial tracking or power-loss guarantees.

### Planning/advisory selection

Planning/advisory invocations use the same
[qualified seed rubric](skills/planner/references/profile-selection.md): assess
all six applicable factors, including the weakest verification blind spot, and justify family
and supported effort independently. Proposal precedes readiness: a suitable never-launched
option may remain pending while passive, authoritative readiness evidence is incomplete. Distinguish
catalog from authenticated/runtime readiness and observed launch; reuse current applicable proof
and audit provider/source mappings only for concrete uncertainty, contradiction, clamping risk,
or absent necessary support evidence. Missing readiness blocks dispatch, retains the proposal,
and requires bounded authorization or an explicitly selected, independently justified fallback.
Obtain one exact owner-selected binding plus effort; verify permissions, tools, callable binding
and supported effort at assignment and dispatch. Pass the selected profile unchanged through direct
calls and helper briefs/dispatch. A missing selection/support or settings/default mismatch blocks
work, never silently substitutes. Record proposed, selected and observed separately; unknown actual
binding/effort stays unknown. Implementation-only batching, task-count and REQUIRED-item rules are
not planning prerequisites.

The explicit owner-required exception is Standard `plan_create`: **Sol with exactly medium
supported effort** for the complete same-session specification review/fix → one plan creation →
produced-plan review/fix, both delegated non-helper and helper execution. Planner never
authors fresh artifacts or makes substantive repairs: each artifact has a separate fresh bounded-context producer;
uncertain or substantive corrections use suitable originating producer context or a fresh bounded delegate.
Direct mechanical repair follows the [bounded mechanical correction contract](skills/planner/references/approval-and-recovery.md#bounded-mechanical-corrections). Missing,
unusable or unauthorized delegation stops with no parent inline/local fallback. Resolve its concrete binding from
permitted usable runtime options, not a provider/version hard-coded into skills. Unavailable
Sol/medium stops with the precise binding/support gap; no substitution, settings/default override
or standalone helper fallback may bypass this rule. It is an owner preference, not a family
hierarchy, capability ranking or benchmark claim. Independently authorized standalone helper
selection stays separate but cannot override a manager-governed Standard invocation.

Other selections—including TinySpec source/tasks, brainstorming assessment/application,
Standard specification/tasks and independent reviewer—follow the shared rubric, not fixed
stage families or replacement classes. Preserve planner-owned dialogue, stage order, approvals,
write boundaries and reviewer independence. See the operational
[planner](skills/planner/SKILL.md) and
[helper adapter](skills/delegating-architectural-planning/SKILL.md) contracts.
Settings examples are neither current owner selections nor capability proof.

## Memory contract

Successful adoption through `initialize-coherence` establishes an approved project-memory
association and index, or validates a compatible existing one. Merely invoking initialization
does not establish readiness: missing capabilities, denied approval or missing structure block
it. Owner-selected paths remain valid; bounded refresh preserves existing memory and custom
policy. Retrieval and write rules live in `memory-handling`; `compact-memory`, `finish-session`,
`planner`, `tiny-spec`, `coordinate-implementation`, and `initialize-coherence` reference it.
A missing required gotcha association routes to `initialize-coherence`, never a guessed global store.

Coordination memory is project-local explicit feedback only, separate from adopted gotchas.
The [shared contract](skills/memory-handling/references/project-coordination.md) owns relevant
existing guideline consultation and bounded user-feedback writes. Missing store/STATE is
nonblocking; no auto-init, routine summaries/index updates, evidence-only commits, reflection
or inferred lessons. Clear future corrective feedback can authorize a minimal guideline
without routine second approval; ambiguity asks, explanation-only/no feedback/no-write writes
nothing. Preserve local ownership/path/symlink, sensitive-data and dirty/concurrent safeguards.
Only a needed guidelines owner may be created, never history/index/run scaffolding.

## Context-first recovery

No automatic STATE creation/edit/removal. Preserve existing STATE/custom content. Start with
available conversation summary/recent context and selectively reconstruct uncertain approvals,
completion, Git ownership/checkpoints and actual child status under the
[recovery contract](skills/coordinate-implementation/SKILL.md#recover-context).
Unknown authority/completion blocks affected actions; active children mean inspect/wait,
unknown child status blocks replacement. Inspect failures before targeted retry; unknown
cause stops blind relaunch. No guessed completion, duplicate dispatch or repeated commits.

## Project docs

`docs/open_issues.md` holds the canonical register of unresolved work
(`track-open-issue`). `initialize-coherence` preserves or establishes documentation
owners/indexes and a verified project-specific documentation-routing guide, recording them
in approved project instructions. Persistent-database projects also require an authoritative
schema owner or documented set, even without a naming convention. Initially clean projects
may initialize verified content; non-clean projects first require fresh read-only investigation
and approved shell/index bounds, with no substantive documentation writes. Missing required
structure blocks readiness; empty/stale substantive content remains planner work, not completed
by a shell. `finish-session` checks owner/index/routing/schema existence without initializing
or auditing them.
## Task commit contract

Package-managed execution uses the shared [task-commit contract](skills/memory-handling/references/task-commit-contract.md).
It requires focused per-task Git checkpoints for authorized retained repository output, while preserving
compatible signing/message conventions, unrelated dirty work, and existing approval gates. It adds no
runtime extension, adapter, provider/model binding, dependency, installation, live probe, push, deployment,
or history rewrite requirement. Missing Git/identity/permissions, failed hooks/checks, unclear ownership, or
conflicting policy stops the affected task; static checks and temporary-Git fixtures do not prove model obedience.
