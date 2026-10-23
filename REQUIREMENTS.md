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

On every full initialization, including compatible adoption and refresh, the bounded exception
is proposal-first project-local SpecKit assets, not global tooling installation. Discover
integration/version/script/options and verify commands, templates and scripts against an
authoritative expected inventory and actual files. Complete valid/custom assets remain
untouched; compatible association stays an association/memory no-op, not an early exit.
Missing/incomplete assets block initialization-ready claims. Use an installed official CLI
with a source-verified recipe, explicit integration/options, isolated fresh staging and
approved missing-file-only transfer; reconcile only approved necessary manifest entries.
Preserve custom assets, constitution and metadata; no blanket `specify init --here --force`
against an existing repository. Missing usable CLI or unknown safe recipe blocks repair;
do not silently install/upgrade tooling. Conflict/drift/failure stops without readiness,
automatic retry or destructive rollback; report partial outputs. Other missing runtime prerequisites
retain stop/report behavior. TinySpec/direct tasking still does not require SpecKit, and
Standard capability gates remain. In Paseo, changed tools or extensions require a fresh-session handoff; the fresh agent verifies the checkout, revision, current approval and loaded capabilities without an automatic reload or restart.

Explicit policy-only parsimony refresh on an already-adopted project is narrower than full
initialization. It requires applicable runtime/question, approval-contract, safe path/readability,
status/ownership and exact-overlap/concurrent protections for the bounded instructions change,
not unrelated tooling installation, full reinitialization, documentation repair/investigation or
SpecKit inventory/provisioning. Missing unrelated assets/docs do not block the limited result;
missing capability required for that operation does. Full default new/compatible/refresh routes
retain their applicable documentation, SpecKit and structural readiness duties.

After later integration, use the existing [setup procedure](README.md#setup). Installation alone does not refresh existing project
instructions. In Paseo, changed tools or extensions require a fresh-session handoff and fresh-agent checkout/revision/current-approval/capability verification; no automatic reload or restart occurs. Only in an explicitly selected authorized project, request initialize-coherence
policy-only refresh, compare actual canonical policy text, approve the exact bounded diff and
separately approve dirty exact overlap. Retain custom/equivalent owners and overrides; drift stops.
Verify `policy refresh applied` / `policy already current`, never full initialization/Standard
readiness; unchanged repeat has no write, duplicate or empty commit. Use full initialization only
when broader work is intended. No global activation or fleet rollout follows from this guidance.

When SpecKit metadata is absent (not malformed/conflicting), inspect supported installed-CLI
choices and version read-only, propose from current runtime/repository evidence and obtain
material owner selection via `ask_user` without guessed/silent defaults. The installed CLI
version can supply the absent recorded version. Selection grants no writes: the exact
staging/target proposal still needs explicit approval; unresolved selections/recipes stop.

## Executable implementation runtime

Coordinate Implementation uses the existing Python CLI, PyYAML6.0.3, standard-library
SQLite/Git process handling and the installed Pi SDK (0.87.1 tested). Python >=3.10,
local Git and a usable Node/SDK installation are actual dependencies. The tested SDK lock
is install metadata, not an exact runtime version/provenance admission gate. No LangGraph,
SQLite saver, cgroup delegation, closed host manifest, resource hashes or catalogue is needed.
Optional explicit isolated setup never runs on ordinary entry; missing dependencies/auth/model
report their actual operation errors, not administrative readiness failures.

Task validity has only six linter checks: readable file, parsed task list, ID/work description,
unique IDs, existing dependency references and acyclic dependencies. Empty work launches nothing.
Nonempty work takes project/tasks and ordinary executor JSON (`provider`, `model`, `effort`).
Preserve the actual owner-selected model/effort without silent substitution or provenance
assessment. Ordinary selected-model tokens need no financial receipt; obtain narrow permission
for unrequested chargeable/irreversible external actions.

Tasks run sequentially with normal SDK read/search/edit/write/command tools. The runner owns
actual project check execution and explicit-owned-path focused commits; workers never stage
or commit. Checks and path limits are optional context, not universally required metadata.
Actual check failures cannot be reported passed. Normal Git hooks/signing and unrelated
staged/unstaged/untracked/STATE/custom work are preserved. No no-change empty commit. One
fresh independent read-only full-range final review remains distinct from implementation.
Findings are reported honestly, not accepted through a SQL disposition or evidence hash.

SQLite stores useful ordinary progress/history. Old tables/rows remain readable in place;
new work never replays or settles old intent records. Optional history errors cannot veto coding.
An ordinary exclusive worktree writer lock prevents cooperating overlap. Current recorded live
writers cannot be replaced/killed; explicit historical abandon inspects identities/scopes,
releases only the old reservation and preserves incomplete effects/partial work. No cgroup
provisioning for normal tasks. SDK compaction and output continuation are normal behavior;
no pressure fields, lifetime caps, watchdogs, repair budgets or arbitrary workflow deadlines.
The SDK's ordinary errors/cancellation remain real failures, not permanent launch poison.

Questions use actual current terminal input, not Paseo versions, original-session proofs,
transcript receipts or external owner catalogues. Noninteractive unanswered questions stop
honestly with partial work retained. No automatic legacy resume/restart, auth refresh,
installation, global settings changes, mass conversion or background daemon. Inspect actual
failed operations/partial commits before targeted follow-up; no autonomous expensive retry loop.
See the [operating](docs/coordinate-implementation.md) and [storage/interface](docs/coordinate-implementation-schema.md) owners.

### Planning assignments

Planning roles use the canonical saved assignments in
[`skills/planner/references/model-assignments.json`](skills/planner/references/model-assignments.json).
The selected assignment is copied unchanged into its bounded brief and dispatch. If its saved
assignment is missing, malformed, unsupported or unavailable, stop only that operation and ask
the owner for a correction; do not recommend, infer, substitute or use a fallback. The planner
parent, source/task producers, plan pass, brainstorming, and independent review retain their
separate assigned roles. Planner-owned dialogue, stage order, approvals, producer/parent boundaries,
write boundaries and reviewer independence remain unchanged. See the operational
[planner](skills/planner/SKILL.md) and
[helper adapter](skills/delegating-architectural-planning/SKILL.md) contracts.
Settings examples are neither current owner assignments nor capability proof.

## Memory contract

Successful adoption through `initialize-coherence` establishes one approved project-memory
association and index for verified technical gotchas and explicit future-directed owner guidance,
or validates a compatible existing one. Merely invoking initialization does not establish
readiness: missing capabilities, denied approval or missing structure block it. Owner-selected
paths remain valid; bounded refresh preserves existing memory and custom policy. Retrieval and
write rules live in [Memory Handling](skills/memory-handling/SKILL.md); `compact-memory`,
`finish-session`, `planner`, `tiny-spec`, `coordinate-implementation`, and
`initialize-coherence` reference it. A missing required association routes to
`initialize-coherence`, never a guessed global store.

Read the whole associated index first, then relevant entries, and recheck it after a write.
Missing store/STATE is nonblocking; no auto-init, routine summaries/index updates, evidence-only
commits, reflection or inferred lessons. Only explicit future-directed user feedback can
authorize guidance changes; clear feedback needs no routine second approval, ambiguity asks,
and explanation-only/no feedback/no-write writes nothing. Preserve local ownership/path/symlink,
sensitive-data and dirty/concurrent safeguards. Never create a second guidance store or
history/index/run scaffolding.

## Context-first recovery

No automatic STATE creation/edit/removal. Preserve existing STATE/custom content. Start with
available conversation summary/recent context and selectively reconstruct uncertain approvals,
completion, Git ownership/checkpoints and actual child status under the
[recovery contract](skills/coordinate-implementation/SKILL.md#recover-context).
Unknown authority/completion blocks affected actions; active children mean inspect/wait,
unknown child status blocks replacement. Inspect failures before targeted retry; unknown
cause stops blind relaunch. No guessed completion, duplicate dispatch or repeated commits.

## Project docs

This repository's canonical active unresolved-work tracker is
[GitHub Issues](https://github.com/elsonidoq/skills/issues), explicit target
`github.com/elsonidoq/skills`, via `track-open-issue`. `docs/open_issues.md` is retained historical
source only; actual historical migration is NOT RUN, not implied by routing activation.
`initialize-coherence` preserves or establishes documentation
owners/indexes and a verified project-specific documentation-routing guide, recording them
in approved project instructions. Persistent-database projects also require an authoritative
schema owner or documented set, even without a naming convention. Initially clean projects
may initialize verified content; non-clean projects first require fresh read-only investigation
and approved shell/index bounds, with no substantive documentation writes. Missing required
structure blocks readiness; empty/stale substantive content remains planner work, not completed
by a shell. `finish-session` checks owner/index/routing/schema existence without initializing
or auditing them.

## GitHub unresolved-work tracking

For a project configured to use GitHub Issues, `track-open-issue` requires usable GitHub CLI
`gh`, authentication for the exact configured hostname, issue-read capability and explicit scoped
write authority before mutation. Verify these at the operation boundary without displaying token
values; do not install `gh` or refresh authentication automatically. An ADMIN permission field
or successful read is not issue-write authority. Missing target/capability/authority yields
`issue tracking: UNAVAILABLE` or `deferred`, with candidate/evidence/resumption and corrective
action in the response, not a persistent local fallback tracker. Other suite operations do not
acquire a new unconditional GitHub dependency.

`import-open-issues` defaults to offline Python preview; remote reconciliation is explicit and
read-only. The bounded observed closure mapping uses github.com REST API `2022-11-28` and native
completed metadata, never proof of a historical fix. Future actual import requires separate
named-destination/apply authority, reviewed preview, overlap/mapping choice (here OI-4/#2), and
independent full mapping/content/state/count readback. Preserve original Markdown; no automatic
migration, source deletion or new local tracking database. The skills own exact operation and
recovery rules; changed global assets require a fresh-session activation handoff in Paseo.

## Task commit contract

Package-managed execution uses the shared [task-commit contract](skills/memory-handling/references/task-commit-contract.md).
It requires focused per-task Git checkpoints for authorized retained repository output, while preserving
compatible signing/message conventions, unrelated dirty work, and existing approval gates. It adds no
runtime extension, adapter, provider/model binding, dependency, installation, live probe, push, deployment,
or history rewrite requirement. Missing Git/identity/permissions, failed hooks/checks, unclear ownership, or
conflicting policy stops the affected task; static checks and temporary-Git fixtures do not prove model obedience.
