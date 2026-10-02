# TinySpec: Coherence initialization

Status: preparation authorized; not approved for implementation.
Producer: planner. Depth: TinySpec. Separate tasks required.

## Request and decisions

The owner requests:

> ## Context
> The skills package works well for the planning part, from receiving the plan to finishing it. However, the onboarding flow is somewhat odd. There are two separate skills: `Initialize Memory` and `Initialize Documentation`. Both are blockers for using the rest of the skills package.
>
> ## Objectives
> 1. **Name the project** Brainstorm with the user to choose a project name. A single skill called `Initialize` would be too abstract, so a concrete project name is required.
> 2. **Merge the two initialization skills** Combine `Initialize Memory` and `Initialize Documentation` into one skill that guarantees the repository invariants are satisfied. These skills currently identify how documentation and memory are being handled and bring them into the current schema.
>
> ## Constraints
> - Do not rely solely on the description above. Base the unification on the actual behavior of the existing skills.
> - The merged skill should be named something like `Initialize` or `Initialize Invariants` (or similar).
> - Preserve the original intent, names, numbers, negation, and constraints.
> - If any part is ambiguous or unsupported by the context, mark it explicitly as `[unclear]`.

Owner answers through ask_user, in order:

- Project name: “use coherence” → **Coherence**.
- Guarantee: “Structural readiness; explicit outstanding work (recommended)”. Complete substantive documentation is not promised by initialization.
- Depth: “TinySpec → Tasks → Implement (recommended)”. This authorizes preparation only until combined approval.
- Planning producer binding: “Gpt 6.1 sol” → registered `openai-codex/gpt-6.1-sol`, explicitly selected for these planning stages; not a global skill/model-policy change.
- Merged name: “initialize-coherence — Initialize Coherence (recommended)”.
- Compatibility: “Don't care about retrocompatibility, these are the firsts iterations on this skills project. The important thing is that an agent executing this skill behaves like an agent executing both old skills. This is just a UI simplification”. Plan one new skill and retire both old entry points, without aliases or a backward-compatibility project. Preserve source provenance and combined operational behavior.

The actual sources are `install-memory` / **Install Memory** and `initialize-documentation` / **Initialize Documentation**. “Initialize Memory” is the request's label, not an additional discovered skill. No separate machine-readable “current schema” was found: **[unclear]** beyond the inspected suite contracts. Do not invent a universal schema or migrate project data to satisfy that phrase.

## Outcome and scope

Give owners and agents one onboarding UI that establishes the same combined adoption, memory, documentation ownership/routing/index, and bounded refresh behavior as the two existing skills. Existing substantive documentation gaps remain explicit planner inputs.

Include the merged skill, retirement of the two source entry points, active consumer references, user-facing Coherence naming/setup, requirements references, installer/load-probe inventory and workflow/fixture checks. Update only relevant active references; retain original names in provenance and historical records. Preserve all pre-existing unrelated work.

Exclude broader branding/artifact rewrites, aliases, compatibility conversion of adopted projects or legacy planning artifacts, new universal state schemas, application changes, deployment, requirement installation by initialization, live model probes without separate authorization, and substantive documentation writes on dirty repositories. Initialization does not itself implement planner handoffs.

Repository conventions: subject plans under `docs/plans/`, routing in `docs/index.md`. That index explicitly declares this configuration repository has no project-memory association; do not create or consult global memory for this work.

## Authoritative behavior and preservation requirements

Working-tree sources, not HEAD alone, govern this change. Both source skills are already modified by unrelated planner work. Preserve their current combined contracts, including the following:

1. **Approval and requirements:** Adoption is proposal-first: no target write/edit/overwrite before explicit approval. Record required runtime prerequisites; report missing requirements rather than proceeding silently or installing. Preserve pi 0.87.x (tested 0.87.1), exact `npm:pi-subagents@0.73.1` and `npm:pi-ask-user@0.15.1` pins. SpecKit is required only for applicable Standard stages, not TinySpec; Jev is optional for Jev triage with the documented manual fallback. Verify actual capabilities. Missing mandatory question capability or planner approval contract stops. Every applicable artifact approval/renewal has **4–6 short bullets before ask_user**, covering outcome, scope/exclusions, decisions, risks/deferrals, actual validation, current targets and exact authorization. Denial/cancellation/ambiguous answers grant no writes. Renew changed approvals; persist comparable current-content evidence. Ancillary adoption/shell approval is not substantive implementation authorization.
2. **Dirty and concurrent targets:** Run `git status --short`. Clean means no output; untracked files make the project non-clean. Record prospective targets' initial state/content. Do not edit already-dirty targets without explicit owner approval. Re-read immediately before patches and stop on concurrent changes. Preserve unrelated bytes. Approval of a general plan is not an implicit dirty-target waiver.
3. **Adoption/instructions/memory:** Append a marked self-contained suite contract to existing instructions, preserving custom content verbatim. Record planning flow through planner → owner TinySpec/Standard choice → reviewed tasks → approved handoff → coordinate-implementation → finish-session, without automatically creating an Epic. Record memory retrieval, conditional temporary execution-state convention (commonly STATE.md), pi session conversation record, canonical `docs/open_issues.md` unresolved register via track-open-issue, and documentation owners/routing. Default approved memory location is `<project-root>/memory/` with `memory/MEMORY.md` and entry files; owner-chosen paths remain valid. New skeleton contains only header, contract rules, and a no-gotchas-yet placeholder—never fabricated facts. Whole index first, then trigger-matching entries; recheck after memory writes. No global-store substitution, secrets, tokens, personal data or sensitive payloads.
4. **Existing adoption/refresh:** Validate an existing compatible association rather than unnecessarily adopting again. Refresh only owner-approved bounds of the suite-owned marked section, retaining custom paths/docs/policy and every unrelated byte. Unmarked/ambiguously customized/dirty sections require exact bounds/diff and approval. Preserve existing memory/index; no skeleton reset, global rename, old artifact/approval conversion, or substantive documentation authorization through refresh.
5. **Documentation ownership:** Read instructions, indexes, registers, runbooks, architecture, decisions, specifications and memory configuration. Preserve existing authoritative owners and formats; no competing documents. Discover every documentation directory, including nested ones. Each uses the local or owner-selected index mechanism for direct documentation files other than the index itself, with verified titles/descriptions/purposes and suitable sections. Parent indexes map direct child documentation directories. Filenames alone do not establish currentness/completeness. If conventions do not name equivalent owners, obtain owner choices for documentation root, index mechanism, architecture/schema/routing/unresolved-work/deployment locations and formats. Do not assume a docs layout. Create parent directories only as needed. Do not invent detailed descriptions or placeholder architecture facts.
6. **Schema/routing:** Determine persistent-database presence from evidence. If present, require an authoritative schema document or documented set—even without a convention naming it. Preserve its owner/format. Its substantive obligation covers current tables/collections, fields/types, keys/relationships, constraints and indexes where applicable. Obtain missing schema ownership choices alongside architecture location. Require a documentation-routing guide (document or identified existing section) mapping verified project-specific material changes to authoritative owners; no generic applicability claims or duplicated owner content. Preserve this obligation even though dirty initialization can only create shells.
7. **Clean/non-clean branches:** Preserve existing clean initialization authority for required documentation owners/indexes and verified content; no application code/tests/generated application assets/deployment/unrelated edits. On a non-clean project FIRST verify native task/sub-agent capability; if absent report exactly `documentation initialization blocked: sub-agent capability unavailable` and stop without edits. Launch a fresh read-only investigation sub-agent. Its four outputs remain: (1) verified owners/missing/stale work, schema/routing included, sources/minimum safe shells with primary file:line evidence where possible; (2) attributable current versus likely historical/stale/dead-code/uncertain findings; (3) only material intent questions changing scope/truth/ownership/routing/obsolescence; (4) substantive scope and acceptance recommendation without edits or invented intent. Changed code is not assumed live/intentional. Resolve questions and explicitly approve the current investigation plan plus shell/index bounds. Re-discover owners/directories after approval; create only approved missing empty/template shells plus file maps/indexes, never substantive current-state documentation or investigated implementation. Adoption instructions/memory writes have their own stated approved authority. Do not use structural readiness to bypass this branch.
8. **Validation/report/handoff:** Re-read approved instructions and memory index; verify association/no fabricated gotchas/no unrelated changes. Validate only introduced documentation paths/headings/links/references, not a repository-wide audit. Report retained/initialized/intentionally absent owners, requirements, paths, evidence, decisions/deferrals, approval evidence and gaps. Missing required structure prevents a ready claim. Substantive gaps are outstanding work; a shell is not substantive completion. Verify planner before substantive handoff; missing planner reports `planner: UNAVAILABLE` and stops that handoff. Planner asks explicit TinySpec/Standard choice; no new Epic or forced Standard exception. Preserve finish-session closeout guidance.

Evidence anchors: `skills/install-memory/SKILL.md:8–94`; `skills/initialize-documentation/SKILL.md:8–130`; `skills/memory-handling/SKILL.md:13–60`; `skills/planner/references/approval-and-recovery.md:3–62`; `REQUIREMENTS.md:3–49`; `AGENTS.md:3–29`; `docs/index.md:3–23`. These citations describe the inspected working tree and must be revalidated if it changes.

## Approach, sequencing and failure handling

Replace reciprocal “run the other skill” instructions with one operational owner, `skills/initialize-coherence/SKILL.md`, not concatenated conflicting prohibitions. Combine preflight/discovery, preserve branch-specific investigation, gather material choices, approve exact adoption/documentation targets, apply bounded operations, verify and report. Existing prohibitions separating old skill ownership become explicit permissions within the merged approved stages—not permission to relax application, planning-artifact, dirty-documentation or memory-preservation exclusions.

Advertise one entry point and remove both old skill directories from active inventory. Update active references in README, REQUIREMENTS, memory-handling, compact-memory, finish-session, load probes and checker source mappings. Installer discovery is dynamic; inspect `scripts/install-links.py` retirement logic and safely retire only links proven owned by this checkout. Preserve foreign/uncertain entries and conflict-before-write/race protection. Do not invoke installation or live probes without authorization. Rollback is an attributable patch/revert and proven suite-owned link restoration, not resetting the dirty workspace or changing project memory/custom instructions.

Preserve all constraints through a source-to-merged-contract coverage ledger/test evidence, with both positive and negative cases. Do not weaken checkers merely to make removed safeguards pass. Static checks are not proof of agent obedience.

## Acceptance

- **A1:** Coherence has one advertised `initialize-coherence` / Initialize Coherence onboarding entry point. The two old operational skills are retired without redirects; active references, installer inventory and probe/checker expectations agree. Historical identifiers remain attributable.
- **A2:** The merged workflow preserves requirements 1–8 above. A source-to-contract coverage check demonstrates combined old behavior and explicitly maps ownership-only exclusions to approved merged stages.
- **A3:** Structural readiness reports discoverable approved instructions/memory association/index, required documentation owners/indexes/routing and schema owner where required; missing structure blocks readiness. Empty/stale substantive documentation is separately reported and handed to planner, never claimed complete.
- **A4:** Fixtures cover clean, tracked-dirty and untracked-only inputs; missing capabilities and exact stop messages; approval denial/cancellation/renewal; dirty overlap and concurrent changes; fresh adoption, compatible no-op and bounded refresh; custom layouts/nested indexes/schema owners/routing; no fabricated facts/secrets/global-memory fallback. Dirty documentation remains shells/maps/indexes only.
- **A5:** Active consumer routing and setup/docs describe actual merged behavior. Installer fixtures preserve foreign entries, exact-checkout retirement proof, conflicts, races, settings and repeat-run behavior. Retiring names does not authorize historical or unrelated-project rewrites.

## Validation, evidence and remaining limitations

Baseline producer checks: `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-planner-workflow.py` PASS (static instructions); `PYTHONDONTWRITEBYTECODE=1 python3 scripts/test-planner-workflow.py` **48 tests, OK**. Baseline is not merger acceptance. After implementation run suite lint, planner checker/fixtures and focused merged-contract/mutation checks. Validate separate task ordering via task-generation's validator and manually review coverage/dependencies/class share.

Live clean/dirty/refresh approval behavior and `scripts/probe-pi-load.sh` are NOT RUN and require separate authorization. Repository is already substantially dirty; no blanket approval to modify those targets or commit existing work is provided by depth selection. Exact implementation overlap bounds must be presented at combined approval/preflight. No material naming/compatibility question remains. “Current schema” beyond these inspected contracts remains [unclear] and excluded rather than guessed.

Preparation provenance: initial child TinySpec output `c9fc7230-dbb6-45a8-9fdd-5a7719df1838/coherence-tinyspec-production.md`; planner persisted this repository source after owner naming/compatibility decisions. The child output was provisional, not implementation authorization. Final combined source/task/current-scope approval is still required.
