---
name: initialize-documentation
description: Use when a project's documentation owners or directory indexes are missing and need safe initialization.
---

# Initialize Documentation

Establish documentation that can accurately own the repository's current state.
Do not modify application code, tests, generated application assets, deployment
state, or unrelated files.

## Preconditions

1. Read repository instructions (`AGENTS.md`, `CLAUDE.md`, or equivalent) and
   existing documentation indexes, registers, runbooks, architecture records,
   decisions, specifications, and memory configuration.
2. Run `git status --short`. A project is **clean** only when it has no output.
   Untracked files make it non-clean.
3. Preserve an existing authoritative owner and its format. Do not create a
   competing document for information that already has an owner.
4. Never state an unverified code, operational, or historical claim as current
   fact. Do not write credentials, tokens, personal data, or sensitive payloads.
5. Determine from repository evidence whether the project has a persistent
   database. If so, require an authoritative database-schema document or
   documented set of schema documents; an existing authoritative schema
   document satisfies this requirement even when no convention names it.
6. Require a documentation-routing guide that names the project's material
   change categories and the authoritative documentation owner for each. The
   guide may be a dedicated document or a clearly identified section of an
   existing authoritative documentation owner.

## Clean Project: Initialize Documentation Owners

When the project is clean, initialize every documentation owner required by
its instructions or established local conventions. Discover every directory
that the project treats as documentation, including nested directories. Each
such directory must use the project's documented index mechanism to describe
its direct documentation files and use sections where they make the contents
easier to scan. Inspect code and configuration only as needed to identify those
owners; do not infer a detailed system description merely to fill a new document.

When the project has a persistent database, its documentation owners must also
include an authoritative database-schema document or documented set of schema
documents. The owner must describe the current tables or collections, fields
and types, keys and relationships, constraints, and indexes where applicable.
Preserve an existing schema owner and format. If none exists, obtain the
user's choice alongside the architecture-document location; do not assume a
fixed filename or documentation layout.

Initialize or preserve the documentation-routing guide. It must identify the
project-specific changes that require documentation and the authoritative owner
to update for each. It may reference existing owner documents rather than
duplicate their content. Start it with only verified categories and owners;
do not use a generic list as a claim that every category applies to the project.

When no local convention names an equivalent owner, ask the user to choose the
documentation root, directory-index mechanism, and the locations and formats
for architecture facts, database schema, documentation-routing guide, unresolved work, and deployment steps. Do not assume a
`docs/` layout or create any owner until the user supplies that decision.

Create a missing directory index only in the established or user-selected
format. For every new index, list direct documentation files other than the
index itself, using their title, frontmatter description, or a verified one-line
purpose. Do not claim that a file is current or complete solely from its name.
Add an entry to a parent index for each direct child documentation directory.

Create parent directories only when needed for one of these files. The
`install-memory` skill owns suite adoption and the project memory store; do not
create a memory store, planning artifacts,
or placeholder architecture facts here. Before every edit, record the target's
initial state and content, then re-read it immediately before patching; stop if
it changed concurrently. Validate only paths, headings, links, and references
introduced by this command.

Report the initializations, existing owners retained, intentionally absent
owners, and validation result. Then instruct the user to adopt the suite with the
`install-memory` skill when the project has not adopted it yet, and to use the
`finish-session` skill.

## Non-Clean Project: Investigate Before Initializing

When the project is non-clean, do not initialize documentation files before
the investigation and plan approval. First verify that the native task/sub-agent
capability is available. If it is not, report `documentation initialization
blocked: sub-agent capability unavailable` and stop without edits.

Launch a fresh sub-agent to inspect repository instructions, changed and
untracked paths, relevant code, configuration, schemas, generated outputs, and
existing documentation. Require it to return:

1. A verified inventory of current documentation owners and missing or stale
    documentation work, including the database-schema owner when the project
    has a persistent database, the documentation-routing guide, the source and
    minimum safe shell for every missing required owner, with primary
    `file:line` evidence where possible.
2. A separation of attributable current changes, likely historical/stale
   material, dead-code candidates, and conclusions that remain uncertain.
3. Only the material intent questions that can change documentation scope,
   truth, ownership, including database-schema ownership when required, or
   documentation-routing categories, or whether work is obsolete.
4. A recommended substantive documentation scope and acceptance criteria, without
   editing files or inventing owner intent.

Use the sub-agent's evidence to ask the user its material questions. Do not
assume that changed code is live, intentional, or representative of the
current design. After answers are available, present a documentation plan that
identifies authoritative owners, including database-schema ownership when
required, the documentation-routing guide, additions and corrections,
exclusions, evidence gaps, and deterministic acceptance criteria. Separate missing-owner
shells and directory indexes from substantive documentation: shells establish discoverability
only. Resolve unknown shell formats with the user. Before `ask_user` approval, present an
executive brief in 4–6 short bullets covering outcome, scope/exclusions, decisions,
risks/deferrals, actual
validation results and exact authorization. Verify question capability and discoverable
planner approval contract; if unavailable stop. Wait for explicit approval of the current
investigation plan and shell/index bounds. Denial/cancellation grants no edits. Renew changed
approval with a new brief. This approval is not substantive implementation authorization.

After approval, re-discover owners/directories and initialize only explicitly selected missing
owners as empty/template shells plus file maps and indexes. Preserve existing formats and
apply the clean-project dirty-target/concurrent-edit protections. Do not write substantive
current-state documentation or implement the investigated changes here.

Report investigation evidence, decisions/deferrals, approval location and initialized shells.
Verify discoverable `planner`, then hand off the substantive documentation requirement and
source evidence for its scope assessment and explicit TinySpec/Standard choice. Missing planner
reports `planner: UNAVAILABLE` and stops that handoff; no Epic or forced Standard exception.
Instruct the user to adopt via `install-memory` when not yet adopted, use `finish-session` for
this bounded initialization, and continue substantive work through planner. Preserve custom
project owners and source bounds; never treat shell initialization as substantive completion.
