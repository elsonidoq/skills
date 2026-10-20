# Consequential decisions and ADR continuity — TinySpec

## Provenance, depth and authority

**Status: planning source only; feature approval and implementation authorization absent.**
The owner selected planner's **TinySpec** path and `openai-codex/gpt-6.1-sol`,
**medium**, for source/task production in the current conversation. This fresh source
producer may create and checkpoint only this source; no tasks are authorized in this
stage. Separate tasks, planner review and combined approval remain necessary. The
owner explicitly requires a later instruction before implementation may start, even
after planning approval. Saving this proposal is not accepting its feature design.

The conversation is the request authority: add an anytime reusable `save-adr` skill;
preserve existing decision ownership, authority and history; integrate approved-decision
closeout, adoption and direct/delegated planning/execution/review continuity. The
beneficiary is a project owner whose accepted outcomes must survive fresh contexts
and simplification without becoming a blanket prohibition on compatible cleanup.

TinySpec is proportionate: settled instruction/document contracts, reversible edits,
no new data model or external dependency; cross-skill propagation is the principal
coupling. Profile assessment: residual reasoning is reconciling authority and outcome
versus mechanism; tools are bounded local inspection; weakest oracle is instruction
review, which cannot prove model obedience; scope crosses skills and two existing
runtime prompts; failure costs are accidental unauthorized supersession or competing
document owners; approved coordination guidance is **none**. Sol and Luna are plausible
adequate families, with **no established comparative difference** for this work. Medium
is the owner's choice for cross-skill reasoning, not an empirically established gain
over lower effort. Terra/Astra are not needed to resolve missing requirements; a more
capable profile cannot supply missing permission. No benchmark-ranking evidence is
claimed. Environment reports `PI_MODEL=gpt-6.1-sol`; actual effort is not independently
observable here. This source assigns no implementation executor or runtime settings.

## Verified local evidence and resulting constraints

Paths below refer to **this checkout**, not an installed `/home/dev/projects/skills`
copy. Section names are evidence spans; current content must be rechecked before edits.

| Evidence inspected | Derived constraint / acceptance mapping |
| --- | --- |
| `AGENTS.md`, Purpose, Global Assets and marked Coherence adoption contract; `.specify/memory/constitution.md`, I, III–VI and Governance | Global skill remains project-neutral; project policy stays local; explicit authority, focused checkpoints, preservation and independent review remain. A1–A6. |
| `memory/MEMORY.md` (whole index: no gotchas); `memory/coordination/GUIDELINES.md` (no approved guidance); `skills/memory-handling/SKILL.md`, Retrieval/Write Protocol | Decisions are not a new memory category or inferred feedback. No memory write or global-store substitution. A1, A3. |
| `docs/index.md`, Documentation Routing Guide / Project Guidance; `docs/plans/index.md`, opening ownership rule | Skill operational owners are their SKILL.md; existing specifications/plans own requirements; current docs and Git retain their roles. Shared-index updates are deferred to approved implementation, explicitly contrary to no assumption of automatic index writes during this source stage. A1, A6. |
| `specs/003-coordinate-workflow/decisions.md`, title/status and D1–D3; `docs/index.md`, configuration-decision routing | Existing subject-specific decisions/provenance exist, but the routing guide does not declare a general ADR store/index. Preserve these owners; do not treat draft/historical choices as current blanket approvals or backfill them. A1, A2. |
| `skills/finish-session/SKILL.md`, Steps 0–3, 5–8 and Core Invariants; `skills/finish-session-jev/SKILL.md`, base-workflow/manual routing rules | Add approved consequential-decision routing without replacing current-doc/schema, issue, deploy, memory, feedback or validation duties; Jev is optional and cannot confer acceptance. A3. |
| `skills/initialize-coherence/SKILL.md`, Discovery, Approval, Adoption, managed refresh and Validation | ADR discovery/owner proposal and managed instruction updates use existing approval/dirty-target gates, preserve customization, and distinguish new adoption/approved refresh from incidental use. A4. |
| `skills/planner/SKILL.md`, Discovery, Selected production and stage handoffs, Handoff; `skills/tiny-spec/SKILL.md`, Inputs, Compact source; `skills/task-generation/SKILL.md`, Preconditions/adapters and Review/handoff | Constraints must reach direct entry, both planning depths, source/task acceptance and delegated briefs, not only parent context. A5. |
| `skills/planning-brainstorming/SKILL.md`, capability preflight/modes/handoff; `skills/delegating-architectural-planning/SKILL.md`, Preflight approved architecture decisions | Preselection remains read-only; standalone architecture and brainstorming entry also consult relevant accepted decisions, without introducing an artifact or stage. A5. |
| `skills/coordinate-implementation/SKILL.md`, Load/Verify, Recover Context, Execute/Integrate and Review; `skills/requesting-code-review/SKILL.md`, Prepare/Choose; its `code-reviewer.md`, Inputs/Review Focus | Fresh/resumed workers and independent reviewers need relevant accepted constraints and supersession authority. Keep ordinary errors, six intake checks and independent review unchanged. A5. |
| `runtime/coherence_workflow/engine.py`, worker prompt in `Engine.invoke` (around lines 74–86), final reviewer prompt (around line 135); `runtime/pi-host/host.mjs`, `createWorkflowSession` (`noSkills: readOnly`, normal context/skills loading) | Worker receives one task; reviewer receives tasks/range/diff with skills disabled. Skill edits alone cannot reliably instruct the reviewer to discover the shared contract. Permit only thin prompt pointers/discovery instructions at these existing two seams; no host/runner redesign. A5. |
| `runtime/tests/test_engine.py`, `SequentialExecutionTests` prompt-capturing adapter; `skills/initialize-coherence/scripts/test_contract.py`; planner maintenance commands in `skills/planner/SKILL.md` | Reuse focused prompt/contract fixtures and existing checks rather than introduce a validator subsystem. A4–A6. |
| `skills/writing-skills/SKILL.md`, Global Portability, Authoring and Validation; TinySpec's dependency-research, parsimony, early-risk references and `docs/best_practices_spec_driven_development.md` | Concise trigger-only skill, resolving references, capability/fallback clarity, proportional scenario checks and honest evidence limits. A1–A6. |

**Dependency evidence reuse:** this is local document/instruction design, not selection
of a third-party API. The checkout contracts above adequately establish the changed
seams; no external research, dependency addition, canonical research-note write or
prototype is needed. `REQUIREMENTS.md`, Runtime/Executable implementation, records
Pi 0.87.x (0.87.1 tested), pinned subagents/ask-user, Python >=3.10 and the existing SDK
host. Those are applicability context, not proof of live capability or permission.
An implementation touching prompts must use the existing runtime test setup; source
production invokes no runtime, provider, delegation, installation or owner-approval tool.

## Behavior and bounded approach

### One shared contract; anytime saving

Proposed canonical operational owner: `skills/save-adr/SKILL.md`, discoverable by a
trigger-only description for recording consequential decisions and consulting accepted
decision constraints. Keep its save/consult/propagate rules here once; consumers add
thin links and role-specific timing, not another protocol. Supporting reference/template
material is warranted only if needed for concision, linked from the skill and portable.

On invocation, discover the selected project's instructions, routing guide, decision
index and record conventions; reuse the actual owner/location/format. Do not assume
`docs/adr`, this repository's paths, a global decision store, or that a subject-specific
decision file is the project's general ADR owner. If none exists, choose within explicit
existing authorization or propose/confirm the material owner/location/format choice;
no creation outside authorized bounds. Missing/unreadable/conflicting ownership stops
only the affected write or decision-dependent operation with the problem and remedy.
An unadopted/legacy project's absent store alone adds no unrelated startup gate.

A record contains the consequential **decision**, context/rationale, consequences and
trade-offs, **proposed / accepted / superseded** decision status, approval/source
provenance (including unknown or pending authority), and applicable supersedes /
superseded-by links. Preserve an equivalent existing format rather than force a schema.
Keep implementation state separate: an accepted decision can be unimplemented, and an
implemented experiment is not automatically an accepted decision. Never invent approval
from prior work, a model recommendation or this source's preparation authorization.
Saving a record confers no implementation permission. Ask only for materially unclear
decision meaning, authority, conflict or location, not routine wording or naming.

Preserve history: a superseding record and navigable status/link updates retain the
older decision and its rationale; update the relevant discovered index under write
permission. No silent historical rewrite, copied specification or retrospective backfill.
Repeated saving of the same decision should reuse/update its owner rather than create
competing records. Apply existing safe path/symlink, secrets, dirty-target/concurrency
and focused checkpoint rules; no new receipts, metadata registry or runtime enforcement.

### Consultation and change authority

Before planning or changes that may alter accepted decisions, read the **whole decision
index**, then relevant **accepted ADRs** in full. Follow supersession links as needed to
resolve current authority, not an indiscriminate history intake. Carry relevant outcome
constraints and source links into source/task acceptance, worker briefs and review scope;
fresh/resumed contexts re-establish applicability rather than trust a prior read claim.
An index is a map, not approval proof. Proposed decisions are not binding; superseded
records explain history, not current policy. Contradictory accepted records or uncertain
authority require a material owner decision before the affected conflicting continuation.

Accepted ADRs protect accepted **outcomes**, not automatically every implementation
mechanism. Removing a capability during simplification can conflict and needs explicit
supersession approval through existing producing/current-content gates before the
conflicting change. Compatible helper deletion or mechanism cleanup that preserves the
accepted outcome needs no new gate. If an ADR explicitly accepts a mechanism as a
constraint, honor it or obtain supersession; do not dismiss it as incidental. Saving a
proposed supersession is not that approval. ADRs complement specs and current reference /
operational docs; they do not replace their owners or confer broader execution authority.

### Thin integrations and local adoption bounds

`finish-session` uses `save-adr` when an **explicitly approved consequential decision**
warrants durable recording, not once per session and not for agent-inferred implementation
lessons. Its primary-artifact verification, current docs/schema, runbooks, issue register,
gotcha memory and explicit-feedback duties remain intact. A routing pointer may distinguish
a decision/rationale from the current-state document without duplicating either narrative.
Any Jev route addition, if needed, remains a thin manual-authority integration, never a
requirement to classify decisions externally.

`initialize-coherence` discovers/preserves or proposes decision owners/index alongside
its existing routing discovery. New adoption or an explicitly approved bounded refresh
adds managed `AGENTS.md`/equivalent instructions to consult the whole index and relevant
accepted records before affected planning/changes, including capability removal. Resolve
the installed canonical contract by discovered package location, not a fixed developer
path. Preserve local overrides and exact-overlap/concurrency approval. Incidental skill
use does not silently refresh projects, initialize stores or demand fleet migration.

Thin consult/propagate links belong in planner, planning-brainstorming, TinySpec,
task-generation (both adapters), delegating-architectural-planning, coordinate-implementation,
requesting-code-review and its reviewer contract at the evidence spans above. Fresh and
resumed planning/execution/review briefs carry relevant accepted constraints and links;
review compares the actual change with those outcomes, including simplification/deletion.

The **only proposed runtime seam** is minimal discovery/consultation text in the existing
worker and final-review prompts in `runtime/coherence_workflow/engine.py`. It directs each
context to discover the canonical contract from the configured/installed suite and project
routing, or use supplied relevant accepted constraints; the reviewer can read that contract
as a file despite disabled skill loading. Reuse existing task context; no new required intake
fields, preflight gates, host capability, sessions/recovery scheme, SQL state or read receipts.
Do not treat unavailable contract packaging as permission to ignore known accepted constraints;
report the affected evidence gap without blocking unrelated legacy work for absent ADR storage.

For **this repository**, any adoption instructions/routing changes must be separately
explicit bounded task scope: the marked association in `AGENTS.md`, `docs/index.md`,
`docs/plans/index.md` discovery entry for this source/future tasks, and necessary README
workflow/skill discovery text only. No general ADR-store path is selected here: future
creation needs existing owner authorization or its material location choice. No constitution
amendment is proposed; if implementation discovers an actual principle conflict, return
through Governance instead of editing it incidentally. Shared indexes are deliberately
unchanged during this one-file planning checkpoint; include their bounded updates in
approved implementation, not an unapproved planning cleanup.

## Observable acceptance and verification needs

These are source criteria for future task-local REQUIRED mappings, **not an implementation
checklist**. Each needs concrete pass evidence; a green generic suite alone is insufficient.

| ID | Required observable / smallest sufficient check |
| --- | --- |
| A1 — Portable save/discovery | Focused skill read-through/static reference checks plus scenarios for an existing custom store/format, authorized absent-store proposal, repeat save and unavailable/ambiguous owner. Existing owner is reused; no arbitrary global/default store or competing spec; skill name/frontmatter/trigger and links resolve. |
| A2 — Authority/history | Scenario records show all required semantics, accepted-but-unimplemented and proposed-but-experimented distinctions, honest missing approval, linked approved supersession retaining history/index, and no implementation authority from saving. Unapproved/conflicting supersession stops only affected work and identifies the needed owner decision. |
| A3 — Closeout preservation | Attributable approved consequential decision routes to save-adr; ordinary session and inferred lesson create no ADR. Read-through/scenarios retain current-doc/schema/runbook/issues/memory/feedback duties, no retrospective backfill or fabricated acceptance. |
| A4 — Adoption/legacy boundary | Focused existing initialization fixtures and managed-diff inspection cover new adoption, approved existing refresh/custom owner, unchanged repeat, denial, dirty overlap and concurrent drift; whole-index/relevant-accepted consultation reaches managed instructions. No incidental refresh, global path, unapproved store or absent-store-only legacy startup veto. |
| A5 — Constraint continuity | Focused source-to-task/brief scenarios cover direct TinySpec/Standard helper/task/review entry and fresh/resumed contexts. Existing engine prompt-capture fixtures verify the worker and read-only reviewer actually receive the shared-contract discovery/accepted-constraint instruction. Scenarios distinguish capability-removing simplification (explicit supersession first), compatible helper deletion (no extra gate), proposed/superseded nonbinding records and conflicting accepted authority. Reviewers remain fresh/read-only; no duplicated canonical protocol or intake changes. |
| A6 — Bounded integration | Validate only introduced links/sections, actual owned diffs and affected existing contract tests. Relevant current docs/routing/discovery agree with implemented behavior; no unrelated migration, settings/memory/STATE write or runner redesign. Final independent full-range implementation review remains required; report actual commands/results and unavailable checks. |

Task generation must map A1–A6 to owned outcomes with check, pass condition, evidence and
actual permission/manual gates. Compose the propagation check only when the canonical
contract and consumers exist; ordinary tests/docs/checkpoint stay with their delivery.
No independently necessary prototype producer, disposable cleanup task or benchmark is
justified. Use existing planner workflow checks and initialization/prompt fixtures for
the changed seams, extending only focused assertions/scenarios. Pressure scenarios for
this authority-sensitive skill should expose the pre-change omission and verify the
new contract's response, not build a second workflow engine.

Static/fixture PASS means instructions, links, scenario expectations or prompt wiring
are present and sensitive to regressions. It **does not prove** an unrestricted model
reads, understands or obeys ADRs. No receipt/attestation can supply that proof. Live
provider/behavior evaluation is not required for this instruction-contract scope and is
not authorized here; if later requested, obtain its actual capabilities/permissions and
report observed limits separately. Implementation runtime tests are **NOT RUN** in this
source-only stage; they are future acceptance, not claimed present evidence.

## Risks, permissions and stop boundary

Principal risks are over-broad mechanism protection, confusing accepted decisions with
implemented work, losing constraints in delegated/reviewer contexts, and multiplying
owners/protocol text. A2/A5's authority/deletion scenarios and one canonical owner target
these directly. Missing ADR ownership is resolved at the actual save/adoption boundary,
not by guessing a repository-wide store during planning. No material feature trade-off
remains unresolved in this source; repository store creation is neither selected nor
authorized and must not be smuggled into task execution.

Excluded: wholesale documentation migration, retrospective ADR backfill without explicit
scope, runtime enforcement/receipts/read attestations, new approval stages, automatic
installs/auth/reload/restart, unrelated resume/cached-agent/paid-permission fixes, running
workflow edits, and adoption refresh in unrelated projects. Preserve operational/spec
owners, history, existing checks and unrelated concurrent work. In Paseo activation later
requires a **fresh-session handoff**, not instructions to run `/reload` or an automatic
restart; the fresh agent verifies the checkout and loaded capabilities.

**STOP before implementation.** This deliverable is only the authorized one-file source
checkpoint. Next possible work is separately authorized task production, planner review
and combined source/task approval; the owner's explicit planning-only boundary survives
that approval until they separately authorize implementation. Current blockers to feature
execution are missing tasks, review, combined approval and explicit implementation go-ahead,
not a request for a new planning stage or a claim of feature acceptance.
