# Coherence — Pi Skill Suite

Global pi skills for deliberate feature delivery across unrelated repositories. The suite
binds to pinned pi packages and requires adoption per project; it is not runtime-portable.

## Setup

See [REQUIREMENTS.md](REQUIREMENTS.md). The installer verifies pi, installs missing pinned
packages, links suite skills and the SDD reference, and runs deterministic validation:

```bash
scripts/install.sh
scripts/install.sh --probe  # additionally invokes one model; authorize separately
```

Foreign entries at installation destinations are preserved and reported, not overwritten.
Retired links are backed up only when their target proves they belong to this checkout.
After installation or global skill changes, run `/reload` inside pi.

On a project, use [Initialize Coherence](skills/initialize-coherence/SKILL.md)
(`initialize-coherence`) for proposal-first suite instructions, project memory association,
and documentation owners/indexes/routing, including a schema owner when a persistent
database exists. Compatible adoption is validated without rewriting it; an approved
bounded refresh preserves custom paths/policy, existing memory and planning artifacts.

Initially clean projects may initialize required documentation with verified content.
Tracked-dirty or untracked-only projects require a fresh read-only investigation and approval
of the current plan plus exact missing-shell/index bounds; documentation writes remain
empty/template shells, maps and indexes only. Structural readiness requires all approved
instructions/memory and required documentation structure; missing requirements, denied
approval or missing structure prevent a ready claim. Empty/stale substantive documentation
remains explicit outstanding work for planner's owner-selected TinySpec/Standard path.
On every initialization, including compatible adoption and refresh, check actual
SpecKit commands, templates and scripts against the detected integration/version inventory,
including readability, nonempty files, permissions and references. Complete/custom valid
assets need no rewrite; compatible adoption remains an instructions/memory no-op but
continues to this check. Missing/incomplete assets block initialization-ready claims.
The bounded exception is proposal-first project-asset repair with the installed official
CLI: explicitly detected integration/script/options, isolated fresh staging and
approved missing-file-only transfer with scoped manifest reconciliation. Preserve custom
assets, constitution and metadata; no blanket `specify init --here --force` in an existing
repository. Missing usable CLI or unknown safe recipe is a blocker, not permission to
install/upgrade tooling. Conflict/drift/failure stops; report partial outputs without
readiness, automatic retry or destructive rollback. Other missing runtime prerequisites
are reported, not installed by initialization. TinySpec/direct tasking still does not
require SpecKit; Standard retains its stage capability gates.

This repository tracks its project-local SpecKit 1.0.12 setup: `.specify/` contains shared
scripts, templates, integration metadata and the [project constitution](.specify/memory/constitution.md);
`.pi/prompts/` exposes the project SpecKit commands in pi. Machine-local feature pointers,
extension overrides and `.pi/subagents/` runtime state remain ignored. Other projects
still need their own SpecKit installation for Standard; TinySpec does not require it.

## Planning and Implementation

Start with one entry point:

```text
Use planner for this requirement:
<structured requirement or selected source path/section>
```

Planner inspects the requirement/codebase, brainstorms unresolved material choices, and
presents an approximate scope assessment. This phase is read-only. It always presents both
paths and stops for your explicit choice; the recommendation does not choose for you.

```text
                         ┌→ TinySpec → Tasks → Review → Combined approval ───┐
Request → Planner → Choose│                                                   ├→ coordinate-implementation
                         └→ SpecKit Specify → Spec approval → Plan → Tasks ──┤
                                                 → Analyze → Final approval ─┘
```

- **TinySpec:** compact context, scope, decisions, approach, acceptance and validation;
  mandatory separate tasks. Planner reviews both before one combined approval. No SpecKit
  or unnecessary spec/plan/research hierarchy is required.
- **Standard:** genuine installed SpecKit stages, separate what/how/task reasoning,
  specification approval before planning, independent overall review and final approval.
- **Both:** planner delegates each source/specification, applicable Standard plan and separate
  task artifact to its own fresh bounded-context producer. Corrections use suitable originating
  producer context or a fresh bounded correction delegate; planner never authors/repairs artifacts
  or falls back inline. Missing usable authorized delegation stops. Planner still owns dialogue,
  inspection, review, coordination and its own approval brief. SDD quality guidance applies only
  to specification creation (including TinySpec); downstream plans/tasks use the complete source
  as requirements truth, approved Standard plan as derived sequencing, not direct SDD input.
  Governing instructions, contracts, memory and permission/safety still apply. Both use the shared
  `task-generation` contract and durable current-content approval evidence.
  Before every artifact approval or renewal, planner presents a brief bullet-list executive
  summary in the conversation, then calls `ask_user`. You may approve, request changes or
  withhold approval. The brief names concrete included scope, every actual ordered plan stage
  separately when applicable, and every actual task ID/outcome separately in execution order,
  with no total-count cap or catch-alls. TinySpec has no plan; specification-only approval has no
  invented tasks or added plan gate. Renewals regenerate current coverage. Necessary boundaries,
  decisions, risks and actual checks remain; the brief states exact content and next-phase authority.

After approval, planner immediately starts the next authorized phase without another
continuation prompt. Final approval automatically starts `coordinate-implementation` and
its preflight unless you explicitly requested planning-only or a separate-session handoff.
Capability failures, material owner gates and denied/ambiguous approvals still stop progress.

Choosing depth authorizes planning, not implementation. Existing legacy artifacts retain
original provenance, source shapes and applicable gates; planner owns their repair checkpoints.
No new Epic is required or produced.

After an approved handoff, in this or a fresh session:

```text
Use coordinate-implementation for the approved work.
Producer: planner
Planning depth: [TinySpec or Standard]
Source: [path/section]
Tasks: [path]
Supporting artifacts: [paths; Standard includes specification and plan]
Review and decisions/deferrals: [paths/sections]
Approval evidence: [combined approval, or specification and overall approvals]
Approved current content/revisions and implementation scope: [evidence]
```

Coordinator revalidates the handoff and preserves one shared execution graph: up to three
bounded tasks may run locally only when owner-selected exact profile/context fit; larger
complete lists use asynchronous sequential delegation. Tasks carry stable REQUIRED item contracts,
not implementation-model classes or shares. Normally 2–5 consecutive related tasks share one
exact binding plus independently justified effort per invocation when feasible; this is not a quota.
The [qualified seed rubric](skills/coordinate-implementation/references/batch-routing.md) and relevant
approved project guidelines inform owner selection; empty guidelines invent no success history.
Before implementation, coordinator presents the complete batch table with one/two-sentence batch
descriptions, exact proposed model/effort and separate family/effort rationales, then obtains
explicit approval of batch boundaries and profiles. Implementation approval alone does not approve
routing. Reuse verified unchanged routing approval on resume; approve changed rows before execution.
No universal Sol/medium default or forced model diversity applies. Apply **rubric first,
capability verification second**: **Prior launch success establishes availability, not superiority**.
First proposals inspect demands/oracles, then material evidence or explicit non-reliance, then compare
family and effort independently before proposing. Compare suitable options—even when an alternative has no
previous launch history—and retain a suitable proposal as pending rather than treating incomplete readiness as inadequacy.
Catalog evidence is distinct from authoritative authenticated/runtime readiness and observed launch.
Reuse applicable passive proof; a conditional source audit is warranted only by concrete uncertainty,
contradiction, clamping risk, or absent necessary support evidence. If verification is insufficient,
surface the gap and ask for necessary authorization or an explicit fallback choice—not silently
substitute Sol. A fallback needs independent rationale, readiness, and exact owner selection; model
variety is not itself a goal.
Verify permitted callable binding, supported effort, tools and owner gates at assignment/dispatch,
and ensure settings do not silently override actual dispatch arguments. Actual profile stays
unknown when unobservable, never inferred from selection.
The [coordinator dispatch seam](skills/coordinate-implementation/SKILL.md#delegate)
ends preparation once mandatory conditions are satisfied (no state-specific intent commit), reopening only
for concrete affected invalidation. One worker implementing one batch normally uses direct
asynchronous delegation, including multiple internal sequential tasks; a workflow needs a
concrete orchestration reason in the existing brief, not merely a batch label.

Verification per task; execution per coherent batch. Practical producer contracts retain
criterion/check/evidence/gates and optional distinction through both adapters. In the sole
six-factor rubric compare closed design/implementation difficulty with weakest oracle quality,
check cost and observability; combined verification must be feasible and failures attributable.
Preserve consecutive order and producer verification before consumer work.
Dispatch supplies the whole unchanged REQUIRED union before coding; shared checks run once
with every distinct task/item mapping. Cheap audit checks coverage, relevance to each original
criterion, current revision/environment, consistency, every actual task diff/checkpoint and
owned scope/gates, not general full rereview. Executor pass/fail/not_verified maps through proof
to satisfied/failed/insufficient-evidence: failed needs demonstrated criterion violation;
missing/irrelevant/stale/conflicting/unrun proof is insufficient unless valid observations
independently prove a defect. Retain defect and evidence limitation together. Only satisfied
REQUIRED items and gates release dependents; optional green cannot compensate. Source-required
representative-sample manual STOP needs inspectable sample and explicit user approval before
downstream/full expensive operation, permitting only scoped continuation; LLM self-review
cannot replace it. Ordinary tasks need no invented manual ceremony. Inadequate approved/legacy
contracts return to producing review/renewal, never weaker post-hoc acceptance.
A passing contract needs no mandatory strong per-batch reviewer. Inspect failure/run/invocation/
partial commits and proof before authorized stronger implementation continuation for exact gaps
under the same original contracts, not generic strong review. Carry current SHA/state, prior
proof, dependencies and invalidations, retain valid work/attempts, rerun invalidated checks and
reuse only confirmed-valid evidence without a fixed ladder. Unknown/non-model/manual/permission/
contract gaps do not automatically escalate. Clean retry is exceptional: documented justification,
ownership/safe repository mechanics and required owner/project gates, never automatic reset/discard.
Each task has its own verified focused commit with concrete task/runtime proof;
one fresh independent final review covers the complete committed range. Planning depth and
unrelated planning/reviewer selections remain separate from implementation selection.
Static/symbolic fixtures demonstrate contracts, not live model performance, provider acceptance,
or obedience; live support/callability checks require separate permission and usable runtime
capabilities. After global-contract changes, run `/reload` in pi.

## Context-first recovery and coordination feedback

No automatic STATE maintenance or routine coordination summaries/index updates,
evidence-only commits or reflection. Existing STATE/custom content and historical evidence
stay untouched. Recovery begins with available conversation summary/recent context, then
selectively reconstructs uncertain authority, completion, Git/check/commit and child status.
Active/unknown children require reconciliation before replacement; inspect failures before
retry, never guess completion, repeat commits or blindly relaunch. See the
[recovery contract](skills/coordinate-implementation/SKILL.md#recover-context).

Consult relevant existing project-local guidance through the
[feedback contract](skills/memory-handling/references/project-coordination.md).
Missing store/STATE is nonblocking. Only explicit user corrective/future-round feedback
permits compact guideline changes; clear feedback needs no routine second approval,
ambiguity asks and explanation-only/no feedback/explicit no-write means no write.
Respect local ownership/path/symlink, sensitive-data and dirty/concurrent protections;
create only needed guidelines storage, never history/index/run scaffolding.
Required adopted gotcha-memory discovery/retrieval stays separate.

Planner defaults to direct async stage → parent artifact/checkpoint inspection → next
authorized stage with selected profile unchanged. A workflow needs earned branching,
parallel independent work or other orchestration beyond convenience/single-child/sequential
wrapping; stage authority/reviewer independence remain. Implementation batches stay sequential.
Coordinator trusts settled approved design, cheaply audits actual diffs/focused commits/
REQUIRED outputs, then advances ready tasks. Only concrete invalidation reopens affected
work; no routine replanning or unchanged preflight loops. Independent final review remains.
After changing global assets, run `/reload` in pi.

## Supporting Skills

- `planning-brainstorming`: shared bounded uncertainty gate and owner dialogue.
- `tiny-spec`: lightweight source producer; not an independent manager or executor.
- `task-generation`: task semantics, ordering, validation and adapter contract.
- `delegating-architectural-planning`: observed SpecKit planning adapter.
- `initialize-coherence`: single adoption/memory/documentation entry point;
  substantive documentation work goes through planner, without a forced depth exception.
- `requesting-code-review` / `receiving-code-review`: independent assessment and disposition.
- `memory-handling`, `track-open-issue`, `finish-session`: durable guidance and closeout.

## Validation and Documentation

Run `scripts/check-skills-lint.sh` for deterministic suite checks. See the
[planner regression guide](docs/plans/planner-regression.md) for trace fixtures, mutations,
read-only RPC smoke testing, full behavioral scenarios and evidence limitations. Static tests
are not proof of model obedience; live tests require separate authorization.

Use [docs/index.md](docs/index.md) to find the canonical documentation owner. Documentation
describes current behavior, gotcha memory contains only verified non-obvious warnings,
project-local coordination memory records only explicit future-directed user feedback, and
`docs/open_issues.md` is the canonical unresolved-work register. Global assets must not assume
project paths, branch, deployment state, named models or an invented artifact/state schema.

## Mandatory task checkpoints

For authorized retained repository output, the shared [task-commit contract](skills/memory-handling/references/task-commit-contract.md)
requires a focused, verified per-task commit before later task work, completion reporting, or handoff. A task is an
independently verifiable work unit, not a tool call or batch. Read-only, no-change, scratch, and external-only work
creates no empty commit. Preserve unrelated staged/unstaged work; ambiguous ownership, unavailable Git, failed hooks,
or incompatible policy stops rather than waives the checkpoint. Coordinators independently inspect task diffs/checks
and may recover only understood verified contextual changes; fresh implementers never commit unknown work. Subagents
verify and commit each internal task and continue without routine coordinator pauses; the coordinator audits all task
checkpoints when the batch returns, before acceptance or external dependents. Failed checkpoints and genuine owner
gates still stop execution. No routine evidence-only checkpoints are required. This is instruction-managed with static/Git-fixture evidence, not
runtime proof that a model obeys it. After these global skill changes, run `/reload` in pi.
