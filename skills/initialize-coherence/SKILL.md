---
name: initialize-coherence
description: Use when adopting Coherence on a project, refreshing its suite contract, or repairing missing documentation owners, routing, or directory indexes.
---

# Initialize Coherence

One onboarding entry point for suite adoption, project memory and documentation
structure. Structural readiness is not substantive documentation completion.
Follow the stages below; approvals authorize only their stated bounded writes.

## Preflight

- Run `git status --short`. Clean means no output; untracked files make the project
  non-clean. Classify from the initial status, not from changes made by this workflow.
- On a non-clean project FIRST verify native task/sub-agent capability. If absent,
  report exactly `documentation initialization blocked: sub-agent capability unavailable`
  and stop without edits. No adoption write may precede this dirty capability gate.
- Confirm the suite runtime requirements from the discoverable global configuration
  repository's `REQUIREMENTS.md`: pi 0.87.x (tested 0.87.1),
  `npm:pi-subagents@0.73.1` and `npm:pi-ask-user@0.15.1`.
  Verify actual registered and usable capabilities, not package names alone.
  SpecKit is required only for applicable Standard stages, not TinySpec.
  Jev is optional for Jev triage in `finish-session-jev`, with manual routing fallback.
  Report missing requirements; do not proceed silently or install them.
- Record every prospective target’s initial dirty state and content, including
  instructions, memory and documentation. Do not edit an already-dirty target
  without explicit owner approval; general plan approval is not an overlap waiver.
  Re-read immediately before each patch; stop on a concurrent change.
  Preserve unrelated bytes. These protections apply to every stage and write.
- Do not modify application code, tests, generated application assets, deployment
  state, or unrelated files. Do not create planning artifacts.
  Never state unverified code, operational or historical claims as current fact.
  Do not write credentials, tokens, personal data, or sensitive payloads.

## Discovery

Read repository instructions (`AGENTS.md`, `CLAUDE.md`, or equivalent); in pi these
are loaded automatically as context files, but also read them for the association
and conventions. Read existing documentation indexes, registers, runbooks,
architecture records, decisions, specifications, and memory configuration.

- Preserve existing authoritative owners and formats; do not create competing
  documents. Discover every documentation directory, including nested directories.
  Each uses the local or owner-selected index mechanism; use suitable sections.
  Inspect code/configuration only as needed to identify owners; do not infer detailed
  system descriptions to fill documents.
- Determine persistent-database presence from repository evidence. If present,
  require an authoritative database-schema document or documented set, even without
  a convention naming it; an existing authoritative schema owner satisfies this
  requirement. Its substantive obligation covers current tables/collections,
  fields/types, keys/relationships, constraints and indexes where applicable.
  Preserve schema owner/format. Obtain missing schema ownership choices alongside
  architecture location; do not assume a filename/layout.
- Require a documentation-routing guide, either a document or an identified section
  of an authoritative owner. Map only verified project-specific material change
  categories to authoritative owners; reference owner content rather than duplicate
  it. Do not claim a generic category applies without evidence.
- If conventions do not name equivalent owners, obtain owner choices for
  documentation root, index mechanism, architecture/schema/routing/unresolved-work/deployment
  locations and formats. Do not assume a `docs/` layout or create owners before those
  choices. Preserve the suite's canonical unresolved-work register described below.

## Investigation

Skip this stage only for an initially clean project. On a non-clean project,
launch a fresh read-only investigation sub-agent before any documentation
initialization. Have it inspect repository instructions, changed and untracked
paths, relevant code, configuration, schemas, generated outputs and existing
documentation. Require all four outputs:

1. Verified owners and missing/stale work, including schema/routing, sources and
   minimum safe shells for every missing required owner, with primary `file:line`
   evidence where possible.
2. Attributable current changes versus likely historical/stale material, dead-code
   candidates and uncertain conclusions.
3. Only material intent questions changing scope, truth, ownership (including
   schema), routing categories or obsolescence.
4. Recommended substantive documentation scope and acceptance criteria, without
   edits or invented owner intent.

Do not assume changed code is live, intentional or representative of current design.
Resolve material questions and unknown shell formats with the owner. Present the
current investigation plan: authoritative owners including schema/routing,
additions/corrections, exclusions, evidence gaps and deterministic acceptance.
Separate shells/indexes from substantive scope; shells establish discoverability only.

## Approval

Proposal-first: do not write, edit, or overwrite any target until explicit owner approval.
Propose requirements to record, instructions-section bounds, memory path/skeleton or
preservation, documentation targets/formats and branch-specific operations.
For non-clean documentation, explicitly approve the current investigation plan plus
exact shell/index bounds. Show exact overlaps for already-dirty targets separately.

Verify the discoverable planner approval contract; if missing, report and stop.
Missing mandatory question capability stops approval. Before calling `ask_user`
at every applicable approval or renewal, present an executive brief in
4–6 short bullets in assistant text, covering outcome, scope/exclusions, decisions,
risks/deferrals, actual validation results (including NOT RUN/UNAVAILABLE),
current targets/content and exact authorization. A tool-argument summary is insufficient.
Denial, cancellation, timeout or ambiguous answers grant no writes. Wait for explicit
approval. Renew changed approvals with a new brief, re-reviewing affected evidence.
Persist affirmative answers and comparable current-content evidence in existing
artifact/decision conventions; avoid recursive self-hashes. Recheck evidence on resume.
Ancillary adoption/shell approvals are not substantive implementation authorization.
Continue only the approved bounded stages, not investigated implementation.

## Adoption

For a compatible existing adoption, report adoption unnecessary and validate the
existing association as a no-op. For new adoption, apply the approved requirements
block and append a marked, self-contained suite contract to existing instructions,
preserving existing custom content verbatim. `memory-handling`, `finish-session`,
and `compact-memory` can cite it. Record:

- Planning: request → `planner` understanding/brainstorming/scope → explicit owner
  TinySpec/Standard choice → reviewed tasks → approved handoff →
  `coordinate-implementation` → `finish-session`.
  TinySpec uses `tiny-spec`, separate tasks and combined approval; Standard uses
  installed SpecKit and specification/final approval gates. Neither automatically
  creates an Epic.
- Memory: default `<project-root>/memory/` with `memory/MEMORY.md` and entry files;
  owner-chosen paths remain valid. Follow `memory-handling` trigger-first retrieval:
  Read the whole index first, then trigger-matching entries. Recheck after any memory
  write. No global-store substitution.
- State: temporary current-execution state only when the project uses one (commonly
  root `STATE.md`), pi sessions as the conversation record, and `docs/open_issues.md`
  as the canonical unresolved-work register via `track-open-issue`.
- Documentation: Record documentation owners and the documentation-routing guide
  discovered here.

Create the approved memory skeleton only for new adoption: only the header, contract
rules, and a no-gotchas-yet placeholder—never fabricated facts.

For older adoption, propose a bounded refresh. Refresh only owner-approved bounds
of the marked suite-owned section; preserve custom memory paths, docs, policy and
every unrelated byte.
For unmarked, ambiguously customized, dirty or concurrently changed sections, show
exact bounds/diff and obtain approval; a concurrent change first stops the patch
under Preflight. Do not globally rename references, overwrite local modifications,
convert old artifacts or approvals, authorize substantive documentation through
refresh, or reset the memory store. Preserve the existing memory store and index
on refresh, never replace them with a skeleton.

Adoption writes are limited to approved instructions/memory; do not create
documentation directories or planning artifacts in this stage.

## Documentation

After approval re-discover owners/directories, retaining existing formats and source
bounds. Create parent directories only as needed for approved files.

- On the clean branch initialize required documentation owners/indexes with verified
  content only. Do not invent detailed descriptions or architecture facts.
- On the non-clean branch, create only explicitly approved missing
  empty/template shells plus file maps/indexes. Do not write substantive current-state documentation
  or implement investigated changes. Adoption instructions/memory writes have separate
  stated approved authority, not permission to bypass dirty documentation bounds.
- For each index, list direct documentation files other than the index itself, using
  a verified title, frontmatter description or one-line purpose. Filenames alone do
  not establish currentness/completeness. Parent indexes map each direct child
  documentation directory; preserve the established or owner-selected index format.

Documentation writes do not create memory stores, planning artifacts or placeholder
architecture facts. Apply Preflight dirty-target/concurrent-edit protections to every write.

## Validation

Re-read approved instructions and the whole memory index; then relevant trigger entries.
Verify marked contract, associated store path, resolving index, no fabricated gotchas
and no unrelated changes. Validate only introduced documentation paths/headings/links/references,
not a repository-wide audit.

Structural readiness requires approved instructions/memory association/index,
documentation owners/indexes/routing and schema owner where required.
Missing required structure blocks readiness. Report empty/stale substantive content
separately as outstanding planner work. Never treat shell initialization as substantive
completion. Do not promise readiness when requirements or approval gates failed.

Report instructions/memory paths, requirements recorded and approval evidence.
Report retained, initialized and intentionally absent owners, validation results,
evidence, decisions/deferrals and remaining gaps. On the non-clean branch also report investigation
evidence, decisions/deferrals, approval location and initialized shells.

Verify discoverable `planner` before substantive handoff. If absent, report exactly
`planner: UNAVAILABLE` and stop that handoff. Otherwise hand off the substantive
requirement and source evidence for scope assessment and
explicit TinySpec/Standard choice; no new Epic or forced Standard exception. Initialization does not implement
that work. Use `finish-session` for bounded initialization closeout.

Offline source-ledger checks: [scripts/test_contract.py](scripts/test_contract.py).
These static checks do not prove agent obedience; live behavior requires separate authorization.

**Mandatory task checkpoint.** Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md). Focused, idempotent initialization and approved adoption outputs checkpoint only their owned paths; preserve concurrent/unrelated work and approval boundaries.
