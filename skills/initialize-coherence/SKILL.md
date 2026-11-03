---
name: initialize-coherence
description: Use when adopting Coherence on a project, refreshing its suite contract, or repairing missing documentation owners, routing, or directory indexes.
---

# Initialize Coherence

One onboarding entry point for suite adoption, unified project memory and documentation
structure. Structural readiness is not substantive documentation completion.
Follow the stages below; approvals authorize only their stated bounded writes.

## Preflight

Full initialization is the default. Only explicit policy-only refresh intent for an
already-adopted project selects instructions-policy inspection/proposal/update/validation.
It does not install tooling, reinitialize, create memory/shells, repair documentation or
inspect/repair SpecKit inventory. Missing unrelated assets/docs do not block that route.
Retain applicable runtime/question, approval-contract, safe-path/readability and task-checkpoint
requirements; missing capability required for the bounded operation stops it. Use targeted dirty ownership
and exact-overlap inspection for policy-only, not broad investigation merely for unrelated dirt.
The full-route documentation/sub-agent and asset duties below remain unchanged in scope.

- Run `git status --short`. Clean means no output; untracked files make the project
  non-clean. Classify from the initial status, not from changes made by this workflow.
- For full initialization: On a non-clean project FIRST verify native task/sub-agent capability. If absent,
  report exactly `documentation initialization blocked: sub-agent capability unavailable`
  and stop without edits. No adoption write may precede this dirty capability gate.
- Confirm the suite runtime requirements from the discoverable global configuration
  repository's `REQUIREMENTS.md`: pi and the `pi-subagents` and `pi-ask-user`
  capabilities, without specific version requirements.
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

Planning/issue-review roles are global user agents installed into `~/.agents/` by the
[suite installer](../../README.md#coherence-role-activation), not project extensions.
Do not add project activation files or install global roles during project adoption.
Report missing roles with the suite setup correction; the dispatching session verifies
applicable roles with `subagent get` before relying on them.

## Discovery

For policy-only, confirm the existing approved association and equivalent instructions owner;
reuse an already-approved owner rather than automatically creating AGENTS.md. Absent or
materially ambiguous adoption needs a specific owner choice, not silent initialization.
Inspect only relevant instructions, policy, path/symlink bounds and ownership. Broad docs
and SpecKit discovery below apply to full initialization, not policy-only refresh.

Read repository instructions (`AGENTS.md`, `CLAUDE.md`, or equivalent); in pi these
are loaded automatically as context files, but also read them for the association
and conventions. Read existing documentation indexes, registers, runbooks,
architecture records, decisions, specifications, and memory configuration.

Discover the actual project decision owner, index and record convention from those
instructions and routing. Preserve a readable owner/index and custom location; do not
assume a global or default decision store. If ownership is absent, unreadable or
conflicting, propose or confirm the material owner/location/format choice before an
affected adoption write or decision-dependent operation. An absent store alone does
not block unrelated legacy work.

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
- Preserve the existing declared local register until approved cutover. Discovery or bounded
  refresh does not migrate issues or switch a project's canonical owner; retain its declared
  local association while cutover proof/approval is unresolved.
- Resolve the unresolved-work owner from project routing. An explicitly configured GitHub
  Issues target is an external owner, not a local documentation file: do not create or
  require `docs/open_issues.md`. Confirm the explicit target and usable `gh`, authenticated
  issue-read capability as specified by `track-open-issue`. Missing or conflicting target,
  `gh`, authentication, or issue capability is an actionable `issue tracking: UNAVAILABLE`
  gap with its corrective action; do not claim that owner/readiness is satisfied or fall
  back to a local tracker.
- If conventions do not name equivalent owners, obtain owner choices for
  documentation root, index mechanism, architecture/schema/routing/unresolved-work/deployment
  locations and formats. Do not assume a `docs/` layout or create owners before those
  choices.

### Work-routing choice

For new adoption and full refresh, inspect existing work-routing rules in project instructions,
including local overrides outside managed bounds. For policy-only refresh, address routing only
when requested; a parsimony-only refresh does not add a routing-policy decision.
When routing is missing or conflicts with a blanket Coherence requirement, use `ask_user` to
offer the template below, customization, or retention/reconciliation of an existing local policy.
Explain the three routes before asking; never silently impose the template. An already-approved,
clear local policy needs no repeated selection. Selection alone grants no writes: include the
selected text, exact instructions owner/subsection and any conflicts in the existing Approval diff.

Suggested project-instructions template (customize with the owner; no universal size thresholds):

> **Work routing**
> - **Direct work:** Handle small, bounded inspection, edits and focused checks in the current
>   session without a workflow. File counts are examples, not eligibility rules.
> - **Ordinary delegation:** Delegate bounded unplanned work to an agent or agents, including
>   unexpected repairs found during coordinated implementation. Multiple consecutive delegations
>   are allowed; do not manufacture a new Coherence workflow for ad hoc work.
> - **Planned Coherence work:** Use the applicable planning and approval contracts to derive
>   implementation tasks from specifications, then execute those approved tasks. Launching a
>   workflow runner alone is not using Coherence; adoption is not a blanket workflow requirement.
> - **Larger unexpected work:** Ask the owner whether to address it now through bounded delegation,
>   plan it through Coherence, or file an issue with the declared tracker and continue the original
>   work. Do not infer the answer from agent, file or action counts.
> - Routing grants no new scope or external effects and waives no required acceptance, review,
>   safety or permission gates. Keep ordinary scoped repair authority and existing local overrides.

**SpecKit project-asset discovery (full initialization, read-only).**

- After the dirty-first capability gate, check SpecKit project assets on every full initialization:
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

Policy-only skips broad documentation investigation; perform targeted status/ownership and
exact-overlap checks from Preflight. The rest of this stage applies to full initialization.

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
For policy-only, propose only the exact instructions target, subsection bounds and before/after
policy diff, including local customization conflicts. For full initialization, propose requirements
to record, instructions-section bounds, memory path/skeleton or preservation, documentation
targets/formats and branch-specific operations. For a new adoption or explicitly approved
bounded refresh that adds decision consultation, include the discovered decision owner/index,
canonical contract location and exact managed before/after instructions diff; approval for another
refresh or incidental skill use does not authorize that addition.
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

**SpecKit install/repair proposal (full initialization only).**

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
existing association as a no-op (association/memory only); policy currency is a separate
comparison below, even on compatible adoption. For new adoption, apply
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
- Work routing: record the owner-selected policy from Discovery in the approved project
  instructions owner (`AGENTS.md` or equivalent), not merely a link to the installer or a planning
  artifact. Preserve approved custom wording and reconcile conflicting blanket workflow rules only
  within the exact approved diff. Do not change this or any other project's policy as a side effect
  of changing the installed skill.
- Policy: Resolve the installed [Parsimony and Actionable Checks](../planner/references/parsimony.md)
  owner and include its marked project-copy fragment exactly once in the approved managed
  instructions. Verify it is readable before relying on it; no hard-coded installation path.
- Decision consultation: resolve the installed canonical `save-adr/SKILL.md` from the
  discoverable suite configuration, not a fixed developer path, and verify it is readable.
  In approved managed instructions, direct affected planning or changes to read the whole
  discovered decision index, then relevant accepted records in full and needed supersession
  links. Carry applicable accepted outcomes/source links into the work; proposed or superseded
  records are not current policy. A capability removal that conflicts with an accepted outcome
  needs explicit approved supersession; compatible cleanup that preserves the outcome does not.
  The actual project decision owner/index remains authoritative; this managed consultation does
  not create an unapproved store or replace a custom owner.
- Unified memory: default `<project-root>/memory/` with `memory/MEMORY.md` and entry
  files; owner-chosen paths remain valid. One associated index carries verified technical
  gotchas and explicit future-directed owner guidance. Follow `memory-handling` trigger-first
  retrieval: Read the whole index first, then trigger-matching entries; open only relevant
  entries and recheck after any memory write. Guidance
  needs actual user provenance and never follows from routine approval, reflection or
  inferred lessons. No global-store substitution, separate guideline root, auto-init or
  routine summaries/index updates; preserve local path/symlink, sensitive-data and
  dirty/concurrent ownership protections.
- Executable runtime: report optional explicit isolated Python/SDK setup and approved skill/
  settings resource root. Missing dependency/auth/containment blocks execution, never silent
  provisioning or task mass conversion. Core standalone CLI has no Paseo dependency; selected
  interactive mode requires verified same-parent transport and actual registered ask_user.
  Record resolving operating/schema owners, preserve original approvals and reconcile any
  active/unknown legacy writer before execution-origin reuse. Refresh only approved marked
  association bounds; preserve every unrelated/custom byte and dirty/concurrent protections.
- Recovery association: preserve any existing STATE/custom content and document its existing
  location when applicable; no STATE initialization or upkeep. Reference installed execution
  and approval/recovery owners above, not a project-local workflow ledger. Keep pi sessions
  as the conversation record and the canonical unresolved-work register via `track-open-issue`;
  its explicitly configured GitHub Issues target remains external and does not require a local
  register.
- Worktree retention: include the following rule in approved project instructions, regardless of
  whether worktrees are created by Paseo, another host or Git: a disposable worktree or scratch
  directory must not hold the only copy of information or runtime assets required after work ends.
  Route durable information when it arises: source/tests/reproducible configuration to Git, current
  behavior/decisions/operating instructions to existing documentation, unresolved work to the declared
  tracker, and eligible gotchas or explicit owner guidance through `memory-handling`. Required private
  assets belong in project-approved persistent storage, never Git; document their owner and recovery
  procedure without secrets. Do not invent a storage path or migrate existing assets during adoption.
  Working changes may remain in the active worktree until their normal checkpoint/integration; before
  removal verify they survive on the intended retained branch. Completed workflow history and temporary
  evidence need no archive unless required for active recovery or explicit project retention, including
  paid-data or failure-evidence duties. No automatic deletion, shutdown, migration or file registry.
  Resolve and link installed `finish-session/SKILL.md` for the three removal-readiness checks. Existing
  projects receive this rule only through an approved bounded refresh; a package update alone does not
  update their instructions. Reconcile conflicting retention rules within that approved scope.
- Documentation: Record documentation owners and the documentation-routing guide
  discovered here.

Create the approved memory skeleton only for new adoption: only the header, contract
rules, and a no-gotchas-yet placeholder. The unified skeleton's compact rules also cover
authorized owner guidance, with no guidance entries yet—never fabricated facts, feedback or
guidance. Do not scaffold a separate coordination or guidelines root.

For older adoption, propose a bounded refresh. Refresh only owner-approved bounds
of the marked suite-owned section; preserve custom memory paths, docs, policy and every
unrelated byte, including existing index/content. Preserve the discovered decision owner/index
as well. Add managed
decision consultation only through a new adoption or an explicitly approved bounded refresh
with its exact diff; do not incidentally refresh a project merely because `save-adr` is consulted.
For unmarked, ambiguously customized, dirty or concurrently changed sections, show
exact bounds/diff and obtain approval; a concurrent change first stops the patch
under Preflight. Do not globally rename references, overwrite local modifications,
convert old artifacts or approvals, authorize substantive documentation through refresh,
or reset the memory store. Do not implicitly migrate/delete legacy custom stores. Preserve
the existing memory store and index on refresh, never replace them with a skeleton or create
a separate guidelines system.

On refresh, retain the selected work-routing policy, including custom wording inside managed
bounds; it is not a canonical fragment to replace when the suggested template changes. Missing
routing proposes only an approved bounded insertion; ambiguous/conflicting policy requires the
keep/customize/reconcile choice from Discovery. An unchanged repeat makes no routing write or
duplicate block. Apply the existing Approval and Preflight protections to any routing patch.

For association changes, Adoption writes are limited to approved instructions/memory; do not create
documentation directories or planning artifacts in this stage.

### Managed parsimony comparison and refresh

Apply this comparison on new adoption and existing full/policy-only refresh. Association
compatibility alone does not establish policy currency. Resolve the installed canonical
fragment above and compare actual policy text with the managed copy, normalizing only
irrelevant whitespace/line endings. Dates, hashes, versions, receipts, headings or links
are not currency proof. Exact normalized equality is unchanged; arbitrary customized text
is not automatically equivalent.

Reuse approved outer `<!-- coherence-suite-contract:start -->` / `<!-- coherence-suite-contract:end -->`
bounds or an already-approved equivalent managed convention. Within standard bounds use
`<!-- coherence-parsimony:start -->` / `<!-- coherence-parsimony:end -->` around the copied
**Parsimony and Actionable Checks** subsection. These are delimiters, not authorization.
Missing policy proposes insertion only inside approved bounds; clearly managed outdated
policy proposes only subsection replacement. Preserve local overrides even inside outer bounds.
Unmarked, ambiguous, duplicated or customized sections, including equivalent local policy,
need a specific keep/reconcile/location choice, never mechanical replacement or a competing block.
An approved semantically equivalent local policy may be retained; record that choice in ordinary
approval evidence, not a registry.

Follow this order:

1. Compare canonical text and initial target bytes/status, verifying safe project-local
   path/symlink bounds, readability, ownership and current scope. Unsafe paths stop.
2. Propose the exact target and bounded before/after diff, including conflicts; obtain normal
   current-content approval under Approval. Already-dirty exact overlap requires separate explicit
   overlap approval; general approval is not a waiver. Denial/ambiguity or unavailable mandatory
   question capability grants no write.
3. Re-read immediately before patching; concurrent drift stops the affected patch even after
   approval. Do not adopt intervening work or automatically retry.
4. Patch only the approved insertion/replacement, preserving every unrelated byte, overrides,
   custom paths/association, memory/guidelines/STATE/history/docs/SpecKit. Never regenerate the
   outer contract wholesale, reset memory, reinstall or destructively roll back.
5. Validate by re-reading and comparing the result with the approved candidate/canonical text,
   inspecting the actual bounded diff and unchanged surrounding content.

Unchanged repeat has no proposal to write, duplicate or unrelated work. For failed/partial
operations report actual state and the smallest necessary correction, without automatic retry
or readiness claim. A mistaken text edit needs an authorized bounded correction preserving
intervening work, not blanket reset.

**Approved SpecKit project-asset operation (full initialization routes only).**

- Compatible association remains an association/memory no-op, not an exit that bypasses the
  full-initialization SpecKit check; approved bounded policy changes remain separate.
- Full new, compatible and refresh routes continue from Discovery through Approval to the
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

Full initialization only. Policy-only refresh does not discover/repair documentation or create shells.

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

For policy-only, re-read instructions, compare with the approved candidate/canonical fragment,
verify one retained policy and unchanged surrounding bytes/overrides. Report only `policy refresh applied`
or `policy already current`, with target/diff/approval evidence and actual limits:
not full initialization/Standard readiness. Unchanged repetition means no write, duplicate,
unrelated work or no-op checkpoint: no empty commit. Do not audit missing unrelated docs,
SpecKit or memory structure for this result. Full-initialization validation below retains its
applicable obligations; policy-only has no substantive documentation handoff.

Re-read approved instructions and the whole memory index; then relevant trigger entries,
including technical-gotcha or owner-guidance entries. Verify marked contract, associated store
path, resolving index, no fabricated gotchas and no unrelated changes; it is one associated
index and has no fabricated guidance. Validate only introduced documentation paths/headings/links/references,
not a repository-wide audit.

When routing is in scope, re-read the actual project instructions and verify the approved routing
text is recorded once, existing customizations and surrounding bytes are preserved, and an
unchanged repeat needs no write. Report retained versus added/reconciled policy; static text checks
do not prove live agent routing judgment.

Structural readiness requires approved instructions/memory association/index,
documentation owners/indexes/routing and schema owner where required.
Missing required structure blocks readiness. Report empty/stale substantive content
separately as outstanding planner work. Never treat shell initialization as substantive
completion. Do not promise readiness when requirements or approval gates failed.

**SpecKit validation/reporting (full initialization routes only).**

- On full new, compatible and refresh routes, report detected SpecKit integration/version, actual
  commands/templates/scripts completeness, repair or no-op, partial outputs and blockers.
- Missing or incomplete required SpecKit project assets block initialization-ready claims even
  on compatible adoption; documentation shell readiness is not asset completeness.
- Revalidate the authoritative expected inventory against actual readable, nonempty files,
  required permissions and resolving references; manifest-only success or CLI exit status is
  insufficient.
- After global skill changes, branch on host activation: in Paseo, prepare a fresh-session handoff; the fresh agent verifies the checkout and loaded required capabilities before launching approved workflow. Do not instruct the owner to run `/reload`, and do not automatically reload, restart or install. Outside Paseo, tell the user to run `/reload` inside pi.

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
