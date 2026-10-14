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
  Report missing runtime requirements; do not proceed silently or install them.
  The only exception is approved project-local SpecKit asset provisioning below,
  not global CLI/runtime installation or a change to planning depth.
  TinySpec/direct tasking still does not require SpecKit.
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

**SpecKit project-asset discovery (read-only).**

- After the dirty-first capability gate, check SpecKit project assets on every initialization:
  new adoption, compatible adoption and refresh.
- Detect integration, script variant, command location, recorded version and relevant options
  from target metadata/configuration; do not silently select noninteractive Copilot defaults.
- Distinguish absent SpecKit metadata from malformed or conflicting metadata; absence is not an
  unsupported integration.
- When metadata is absent, inspect installed official CLI source/help read-only for supported
  integration, script, version and options; use current runtime/repository evidence to prepare
  explicit supported choices for Approval, not guessed or silent defaults.
- Use the installed official CLI version verified from source evidence when no recorded project
  version exists; unresolved selections or unknown/unsupported recipes stop until resolved,
  without readiness.
- Compare an authoritative expected inventory from the official bundle for the detected
  integration/version against commands, templates and scripts.
- Check every expected actual file is readable and nonempty, required script permissions are
  usable, and command/template/script references resolve inside safe project-root/symlink
  bounds.
- Empty directory shells, missing families, individual missing files and incomplete manifests
  are incomplete; directory or manifest existence alone cannot establish readiness.
- Valid custom files remain valid; hash differences alone grant no overwrite permission.
- Ambiguous integration, unsupported version, malformed metadata, unreadable assets or unsafe
  paths stop the affected operation with specific gaps/conflicts, not guessed readiness.

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

**SpecKit install/repair proposal.**

- For absent metadata, obtain material owner selection of integration, script, command location
  and relevant options via `ask_user` under the existing brief/capability/denial gates;
  selection alone grants no writes, then present the exact staging/target proposal for explicit
  approval.
- Include SpecKit integration/version/options, three-family status, conflicts, exact prospective
  asset paths and necessary manifest/metadata entry changes in the current-content proposal
  before permission to repair.
- Complete assets propose no asset rewrite; missing assets require an exact official
  install/repair recipe and bounded target writes.
- Missing usable CLI is a reported blocker for repair; do not silently install/upgrade global
  tooling.
- Before future execution inspect the installed official CLI version, current help and source;
  unknown safe recipe/version/integration stops.
- For inspected official 1.0.12, assets are bundled offline; use isolated fresh staging with
  explicit `--integration`, `--script` and detected relevant options, not silent CLI defaults.
- Propose the exact staging command and options, staging location, candidate inventory/diff and
  approved missing-file-only transfer paths before any staging or target write.
- No blanket `specify init --here --force` against an existing repository: `--force` permits
  merge/overwrite and managed refresh is not an overwrite waiver.

For 1.0.12, the official shape is `specify init <fresh-staging-directory>
--integration <detected-integration> --script <detected-variant> --non-interactive`
plus only source-verified relevant options. Resolve placeholders from discovery,
verify target-option compatibility with current official help/source, and include
the concrete command in the proposal. Do not execute this illustrative shape
until current-content approval. Other versions need renewed applicable evidence.
Derive the proposed candidate inventory/diff read-only from the installed bundle;
inspect actual staged output before transfer and renew approval if it differs.
Pass integration-specific options via verified `--integration-options` where needed
(e.g. a detected custom command directory); never add presets/extensions, network
operations or agent-tool-check bypasses merely to make scaffolding succeed.

## Adoption

For a compatible existing adoption, report adoption unnecessary and validate the
existing association as a no-op (instructions/memory only). For new adoption, apply
the approved requirements block and append a marked, self-contained suite contract
to existing instructions,
preserving existing custom content verbatim. `memory-handling`, `finish-session`,
and `compact-memory` can cite it. Record:

- Package contracts: resolve the installed package location from the discoverable suite
  configuration. Record resolving links to `planner/SKILL.md` (planning),
  `coordinate-implementation/SKILL.md` (execution), `task-generation/SKILL.md` (task mechanics),
  `planner/references/approval-and-recovery.md` (approval/recovery and bounded mechanical
  corrections) and `memory-handling/references/task-commit-contract.md` (retained checkpoints).
  Verify each target before writing; missing installed contracts stop adoption/refresh.
  Refer to these owners rather than reproduce their workflow rules. Neither automatically
  creates an Epic. Package references do not supersede local product policy or authorize work.
- Memory: default `<project-root>/memory/` with `memory/MEMORY.md` and entry files;
  owner-chosen paths remain valid. Follow `memory-handling` trigger-first retrieval:
  Read the whole index first, then trigger-matching entries. Recheck after any memory
  write. No global-store substitution.
- Coordination: consult relevant existing compact guidance; missing store is nonblocking.
  Only explicit future-directed user feedback authorizes bounded guidelines storage, not
  auto-init, routine summaries/index updates, reflection or inferred lessons. Preserve local
  path/symlink, sensitive-data and dirty/concurrent ownership protections.
- Recovery association: preserve any existing STATE/custom content and document its existing
  location when applicable; no STATE initialization or upkeep. Reference installed execution
  and approval/recovery owners above, not a project-local workflow ledger. Keep pi sessions
  as the conversation record and the canonical unresolved-work register via `track-open-issue`.
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

For association changes, Adoption writes are limited to approved instructions/memory; do not create
documentation directories or planning artifacts in this stage.

**Approved SpecKit project-asset operation (all routes).**

- Compatible adoption remains an instructions/memory no-op, not an exit that bypasses the
  SpecKit check.
- New, compatible and refresh routes all continue from Discovery through Approval to the
  approved asset operation below and final Validation; no adoption early return.
- Asset repair is separately bounded by Approval, not authority to change instructions/memory or
  documentation.
- Only after explicit approval, scaffold with the verified official recipe into the isolated
  fresh staging directory; inspect candidate inventory/diff before approved missing-file-only
  transfer.
- Preserve existing custom assets, constitution and integration metadata; exclude incidental
  scaffold outputs, `.git`, constitution replacements and unrelated metadata changes.
- Never blindly copy scaffold manifests over custom metadata; reconcile only necessary approved
  entries so the recorded inventory describes actual installed files.
- Apply Preflight dirty-target/exact-overlap and concurrent-change protections to staging, asset
  and metadata writes; re-read each target immediately before writing.
- Conflict, drift, CLI failure or partial output stops the affected operation; report partial
  outputs and blockers without readiness, automatic retry or destructive rollback.
- Complete assets remain untouched on repeat runs; revalidate the actual three-family inventory
  after approved repair.

Staging and metadata reconciliation must remain within approved safe path bounds;
no escaping symlink or unapproved incidental output is transferable. If an existing
file is invalid rather than missing, report a conflict and stop that transfer,
not an overwrite. Missing mandatory approval capability, denial, cancellation,
timeout or ambiguity grants no staging, asset or metadata writes. General adoption
approval does not waive exact overlap approval or approve an unlisted asset repair.

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

**SpecKit validation/reporting (all routes).**

- On all new, compatible and refresh routes, report detected SpecKit integration/version, actual
  commands/templates/scripts completeness, repair or no-op, partial outputs and blockers.
- Missing or incomplete required SpecKit project assets block initialization-ready claims even
  on compatible adoption; documentation shell readiness is not asset completeness.
- Revalidate the authoritative expected inventory against actual readable, nonempty files,
  required permissions and resolving references; manifest-only success or CLI exit status is
  insufficient.
- After global skill changes, tell the user to run `/reload` inside pi.

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
