# Coherence — Pi Skill Suite

Global pi skills for deliberate feature delivery across unrelated repositories. The suite
uses pi agent capabilities and requires adoption per project; it is not runtime-portable.

## Setup

See [REQUIREMENTS.md](REQUIREMENTS.md). The installer verifies pi, reports package registrations without installing or updating them,
links suite skills, the SDD reference and user-agent role files, and runs deterministic validation. Verify required
registered tools are usable in the session before their applicable stages:

```bash
scripts/install.sh
scripts/install.sh --probe  # additionally invokes one model; authorize separately
```

Foreign entries at installation destinations are preserved and reported, not overwritten.
Retired links are backed up only when their target proves they belong to this checkout.
After installation or global skill changes, in Paseo prepare a fresh-session handoff instead; the fresh agent verifies the checkout, revision, current approval and loaded capabilities before work. Do not reload or restart the current Paseo session automatically.

On a project, use [Initialize Coherence](skills/initialize-coherence/SKILL.md)
(`initialize-coherence`) for proposal-first suite instructions, project memory association,
and documentation owners/indexes/routing, including a schema owner when a persistent
database exists. Use [Save ADR](skills/save-adr/SKILL.md) before affected planning or changes
to discover the project's decision owner, consult its whole index and relevant accepted records,
and propagate applicable constraints; it never assumes or creates a general ADR store. Compatible association is validated without rewriting it; a missing/outdated
managed policy still proposes a bounded refresh. Approved changes preserve custom paths/policy,
existing memory and planning artifacts.

On full initialization, initially clean projects may initialize required documentation with verified content.
Tracked-dirty or untracked-only projects require a fresh read-only investigation and approval
of the current plan plus exact missing-shell/index bounds; documentation writes remain
empty/template shells, maps and indexes only. Structural readiness requires all approved
instructions/memory and required documentation structure; missing requirements, denied
approval or missing structure prevent a ready claim. Empty/stale substantive documentation
remains explicit outstanding work for planner's owner-selected TinySpec/Standard path.
On every full initialization, including compatible adoption and refresh, check actual
SpecKit commands, templates and scripts against the detected integration/version inventory,
including readability, nonempty files, permissions and references. Complete/custom valid
assets need no rewrite; compatible association remains an association/memory no-op but
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

### Coherence role activation

`scripts/install.sh` links `roles/coherence-producer.md` and `roles/coherence-reviewer.md`
into `~/.agents/`. These are persistent user agents, discovered in the same way as other
user roles. No project extension or session-start runtime registration is required.
The installer preserves conflicting files and links; resolve reported conflicts before retrying.
Start a fresh Pi session and use the `subagent` tool's `get` action for each role to verify
its source, prompt and tools. Dispatch either with the normal `{ agent, task }` API.

`roles/coherence-roles.js` remains a no-op compatibility entry for existing activation links;
`python3 scripts/activate-coherence-roles.py PROJECT_DIRECTORY` is no longer needed.
Previously copied registration extensions must also be replaced with that compatibility entry
in explicitly authorized locations, or they can collide with the user-agent names. Do not
mass-update unrelated projects. Already running parents retain their runtime registrations
until session replacement. In Paseo, prepare a fresh-session handoff; do not reload or restart
the current session automatically.

Planner passes the saved stage model and effort with the explicit producer/reviewer role;
issue review uses the project's selected reviewer binding. Suite-owned role prompts and tools
are distinct from model selection. These file-based agents use normal pi-subagents settings and
override behavior; inspect the effective configuration rather than assuming runtime-role override protection. The executable coordinate-implementation runtime constructs
its own SDK sessions and prompts with its selected executor; it does not dispatch these roles.
For file-only producer reports, keep the report in the runtime-bound file and return a short final
acknowledgement after a successful write. File-only controls report delivery; an empty final response
can still fail runtime completion. The acknowledgement does not establish task acceptance.
Instruction delivery does not prove model compliance, and read-only shell access is not a sandbox.

### Existing-project policy refresh

Installation/update alone does not refresh already-adopted project instructions. After later
approved integration, use the existing installer above to install/update the suite. In Paseo, prepare a fresh-session handoff for changed global skills instead of reloading or restarting the current session. In each explicitly selected and authorized target,
request: “Use initialize-coherence for a policy-only parsimony refresh of this already-adopted project.”
It compares the actual installed [canonical policy fragment](skills/planner/references/parsimony.md),
not a version/hash/receipt. Inspect and approve its exact bounded instructions diff; resolve
local keep/reconcile/location choices and separately approve already-dirty exact overlaps.
It re-reads before patching and stops on concurrent drift or unsafe paths, preserving custom
owners/overrides/paths, memory, history, docs and SpecKit. Unchanged repeat is a no-op without
writes, duplicates or empty commits. Verify only `policy refresh applied` or `policy already current`,
not full initialization/Standard readiness.

Explicit policy-only intent does not require unrelated installation, full reinitialization,
documentation repair, broad dirty-project documentation investigation or SpecKit provisioning,
even when unrelated assets/docs are missing. Applicable bounded runtime/question/approval and
ownership safeguards remain; missing required capability stops that operation. Use normal full
initialization (the default) only when its broader adoption/docs/assets work is intended.
No arbitrary target refresh or rollout is implied by installing this repository.

This repository tracks its project-local SpecKit 1.0.12 setup: `.specify/` contains shared
scripts, templates, integration metadata and the [project constitution](.specify/memory/constitution.md);
`.pi/prompts/` exposes the project SpecKit commands in pi. Use `planner` for the managed
Standard guarantee: after specify and any required clarification it runs the distinct
independent specification review, returns material answers to the producer, and records
current-specification approval before planning. Raw standalone SpecKit commands remain
available as vendor flows, but are outside that planner guarantee; this does not add a
wrapper command or change their installer/runtime. Machine-local feature pointers, extension
overrides and `.pi/subagents/` runtime state remain ignored. Other projects still need their
own SpecKit installation for Standard; TinySpec does not require it.

When SpecKit metadata is absent (not malformed/conflicting), inspect supported installed-CLI
choices and version read-only, propose from current runtime/repository evidence and obtain
material owner selection via `ask_user` without guessed/silent defaults. The installed CLI
version can supply the absent recorded version. Selection grants no writes: the exact
staging/target proposal still needs explicit approval; unresolved selections/recipes stop.

## Planning and Implementation

Start with one entry point:

```text
Use planner for this requirement:
<structured requirement or selected source path/section>
```

Planner inspects the requirement/codebase and assesses brainstorming needs directly in the parent
session, without a subagent call or saved-assignment prerequisite. It discusses unresolved material
choices and presents an approximate scope assessment. This phase is read-only. It always presents
both paths and stops for your explicit choice; the recommendation does not choose for you.

```text
                         ┌→ TinySpec → Spec review → Tasks → Fresh task review → Combined approval ─┐
Request → Planner → Choose│                                                   ├→ coordinate-implementation
                         └→ SpecKit Specify → Spec review → Spec approval → Plan → Tasks ──┤
                                                               → Analyze → Final approval ─┘
```

- **TinySpec:** compact context, scope, decisions, approach, acceptance and validation;
  fresh independent specification review before mandatory separate tasks, then a fresh independent
  read-only task review before one combined approval. The parent evaluates its findings and routes
  substantive corrections to producers. No SpecKit
  or unnecessary spec/plan/research hierarchy is required.
- **Standard:** through planner, genuine installed SpecKit stages, separate what/how/task
  reasoning, a distinct independent specification review and current-specification approval
  before planning, fresh independent read-only overall review and final approval. The parent evaluates
  its findings and routes substantive corrections to producers. The later plan helper
  review/fix pass is not that specification review and does not trigger it again.
- **Both:** specification review primarily checks fidelity to the original request and actual
  owner answers; unresolved material intent gaps block downstream work. Reviewers neither edit
  nor approve; parents evaluate findings and source producers make substantive corrections.
  No additional TinySpec approval or automatic rereview loop is added.
  Planner delegates each source/specification, applicable Standard plan and separate
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

Coordinate Implementation executes requested tasks sequentially using the existing CLI and
installed Pi SDK. Source worktrees reuse that Pi SDK rather than requiring copied runtime
`node_modules`; explicit isolated workflow setup retains its lockfile-resolved SDK. Ordinary direct
owner-authorized coding needs no new planning artifacts.
Task intake checks only readable file, parsed list, ID/work, unique IDs, existing dependencies
and no cycles; empty work launches nothing. Dependency order need not match file order.

```sh
scripts/coordinate-implementation intake --tasks /tmp/tasks.json
scripts/coordinate-implementation start --project /absolute/project \
  --tasks /tmp/tasks.json --executor /tmp/executor.json --run requested-fix
```

Minimal tasks: `[{"id":"fix","description":"Fix the requested behavior and run its project test."}]`.
Executor JSON contains the actual selected `provider`, `model`, `effort`; no substitution or
provenance assessment. No workflow graph, manifest, catalogue, cgroup delegation, original
session, parent receipt or proof-of-effect database is required. Installed entry is
`coordinate-implementation`; optional explicit isolated setup is separate install/network authority,
never ordinary-use provisioning or auth refresh. Explicit cross-repository activation uses
`scripts/install-workflow.sh --prefix "$HOME/.local/share/coherence-workflow" --allow-network --global`.
It links the command and Pi bridge globally; the bridge source is in `runtime/pi-extensions/`, not
project auto-discovery, so new worktrees do not load a duplicate. Retain this suite checkout, put
`~/.local/bin` on PATH, and start a fresh Pi/Paseo session. Existing bridge links need the
[source-path update](docs/coordinate-implementation.md#setup-and-verification), not a runtime reinstall.
Project tasks, executor selection and permissions remain local.
Read actual `--help` and the
[operating guide](docs/coordinate-implementation.md) / [storage owner](docs/coordinate-implementation-schema.md).

Workers use ordinary SDK tools and correct harmless read/argument errors in the same conversation.
The runner inspects baseline/actual edits, preserves unrelated work, runs optional specified project
commands, and creates one focused explicit-path commit per task with normal hooks/signing.
No mandatory collected-count/evidence format or no-change empty commit. Fresh independent
read-only initial review covers the full range and reports passing coverage plus defects.
Repair reviews check fixes and affected interactions, retaining valid prior coverage; unresolved
findings or coverage gaps prevent acceptance.
SDK compaction and long-output continuation remain normal behavior, not launch poison.

`status`/`history` are passive readers. `abandon` explicitly labels an inspected old run abandoned,
releases its reservation without signalling processes or settling old effects, and preserves
partial files/history. Current terminal input answers material questions without transcript
proofs; noninteractive questions stop honestly. No automatic resume/replay or expensive retry
loop. An ordinary writer lock prevents cooperating overlap; SDK tools are not an adversarial
sandbox. Inspect actual conflicting writers/files and uncertain effects, never kill/adopt them.
After adopting changed global skills/prompts in Paseo, prepare a fresh-session handoff instead of reloading or restarting the current session.

## Context-first recovery and owner guidance

No automatic STATE maintenance or routine coordination summaries/index updates,
evidence-only commits or reflection. Existing STATE/custom content and historical evidence
stay untouched. Recovery begins with available conversation summary/recent context, then
selectively reconstructs uncertain authority, completion, Git/check/commit and child status.
Active/unknown children require reconciliation before replacement; inspect failures before
retry, never guess completion, repeat commits or blindly relaunch. See the
[recovery contract](skills/coordinate-implementation/SKILL.md#recover-context).

Consult relevant project memory through [Memory Handling](skills/memory-handling/SKILL.md).
One verified association/index carries technical gotchas and explicit future-directed owner
guidance. Missing store/STATE is nonblocking. Only explicit user corrective/future-round
feedback permits compact guidance changes; clear feedback needs no routine second approval,
ambiguity asks and explanation-only/no feedback/explicit no-write means no write. Respect
local ownership/path/symlink, sensitive-data and dirty/concurrent protections; never create
history/index/run scaffolding or a second guidance store. Read the adopted index first and
keep technical-gotcha retrieval distinct from guidance authority.

Planner defaults to direct async stage → parent artifact/checkpoint inspection → next
authorized stage with the saved assignment unchanged. A workflow needs earned branching,
parallel independent work or other orchestration beyond convenience/single-child/sequential
wrapping; stage authority/reviewer independence remain. Executable implementation remains single-writer and dependency-ordered.
Coordinator trusts settled approved design, cheaply audits actual diffs/focused commits/
REQUIRED outputs, then advances ready tasks. Only concrete invalidation reopens affected
work; no routine replanning or unchanged preflight loops. Independent final review remains.
After changing global assets in Paseo, prepare a fresh-session handoff instead of reloading or restarting the current session.

## Supporting Skills

- `planning-brainstorming`: shared bounded uncertainty gate and owner dialogue.
- `tiny-spec`: lightweight source producer; not an independent manager or executor.
- `task-generation`: task semantics, ordering, validation and adapter contract.
- `delegating-architectural-planning`: observed SpecKit planning adapter.
- `initialize-coherence`: single adoption/memory/documentation entry point;
  substantive documentation work goes through planner, without a forced depth exception.
- `save-adr`: canonical discovery, save, consultation and propagation for consequential
  decisions; project routing selects the actual owner and store, if any.
- `requesting-code-review` / `receiving-code-review`: independent assessment and disposition.
- `memory-handling`: verified project gotchas and explicitly authorized owner guidance.
- `finish-session`: reconcile documentation and other authorized owners with existing session outcomes;
  no fresh implementation review, rerun of implementation checks, or new acceptance gate.
- `track-open-issue`: project-discovered GitHub unresolved-issue lifecycle, scoped writes, independent readback and configured read-only body review.
- `import-open-issues`: default offline historical Markdown preview, conflict-aware reconciliation and separately authorized import; never an automatic migration.

## Validation and Documentation

Run `scripts/check-skills-lint.sh` for deterministic suite checks. See the
[planner regression guide](docs/plans/planner-regression.md) for trace fixtures, mutations,
read-only RPC smoke testing, full behavioral scenarios and evidence limitations. Static tests
are not proof of model obedience; live tests require separate authorization. See the
[issue-derived evaluation convention](evaluations/README.md) for later selective comparisons.

Use [docs/index.md](docs/index.md) to find the canonical documentation owner. Documentation
describes current behavior; one project-local memory index carries verified non-obvious
warnings and explicit future-directed user guidance. This repository's
canonical active unresolved-work tracker is [GitHub Issues](https://github.com/elsonidoq/skills/issues),
explicit target `github.com/elsonidoq/skills`, through `track-open-issue`. `docs/open_issues.md` is
preserved historical source only; actual historical migration is **NOT RUN**. A future import needs
separate apply authority, reviewed preview, OI-4/#2 mapping choice and full independent readback.
For active GitHub operations, verify usable `gh`, exact-host authentication and issue-read capability;
reads do not grant write authority. Missing capability or scoped authority returns the candidate,
evidence and resumption condition in the response, not a persistent local fallback. See
[requirements](REQUIREMENTS.md#github-unresolved-work-tracking) and the skill contracts.
Global assets discover each project's own target; they must not assume project paths, branch,
deployment state, named models or an invented artifact/state schema.

## Mandatory task checkpoints

For authorized retained repository output, the shared [task-commit contract](skills/memory-handling/references/task-commit-contract.md)
requires a focused, verified per-task commit before later task work, completion reporting, or handoff. A task is an
independently verifiable work unit, not a tool call or batch. Read-only, no-change, scratch, and external-only work
creates no empty commit. Preserve unrelated staged/unstaged work; ambiguous ownership, unavailable Git, failed hooks,
or incompatible policy stops rather than waives the checkpoint. Executable runs use runner-owned real verification, diff audits, focused commits and actual Git inspection; workers do not stage/commit or own workflow state. Planning/standalone and an
ongoing instruction-managed bootstrap keep their authorized writer checkpoints. The interface
cannot waive safety or create routine evidence-only checkpoints. Static/Git fixtures are not
universal model-obedience proof. After changed global skills/prompts are adopted in Paseo, prepare a fresh-session handoff instead of reloading or restarting the current session.
