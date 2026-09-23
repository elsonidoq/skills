---
description: Initialize a project's documentation owners when clean, or create an evidence-backed documentation epic when existing changes require discovery.
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

## Clean Project: Initialize Documentation Owners

When the project is clean, initialize every documentation owner required by
its instructions or established local conventions. Discover every directory
that the project treats as documentation, including nested directories. Each
such directory must contain an `index.md` that describes every direct
documentation file in that directory and uses sections where they make the
contents easier to scan. Inspect code and configuration only as needed to
identify those owners; do not infer a detailed system description merely to
fill a new document.

When no local convention names an equivalent owner, initialize these portable
fallbacks only if they do not already exist:

1. `docs/index.md`: list the direct documentation files and child documentation
   directories in `docs/`.
2. `docs/architecture/index.md`: explain that focused architecture documents
   record verified current-state facts and link to them as they are added.
3. `docs/open_issues.md`: add the `OI-N` convention and a concise entry template
   containing `Status`, `Problem`, `Primary evidence`, and `Resumption condition`.
4. `docs/deployment_steps.md`: add a lifecycle and short entry template for
   status, timing, environments, procedure, verification, and
   rollback/irreversibility.

Create a missing `index.md` in every discovered documentation directory; use
`index.md`, not a `README.md`, for directory indexes. For every new index, list
direct files other than `index.md`, using their title, frontmatter description,
or a verified one-line purpose. Do not claim that a file is current or complete
solely from its name. Add an entry to a parent index for each direct child
documentation directory.

Create parent directories only when needed for one of these files. Do not
create a project memory store, an epic directory, a specification, a task list,
or placeholder architecture facts. Before every edit, record the target's
initial state and content, then re-read it immediately before patching; stop if
it changed concurrently. Validate only paths, headings, links, and references
introduced by this command.

Report the initializations, existing owners retained, intentionally absent
owners, and validation result. Then instruct the user to run `/finish-session`.

## Non-Clean Project: Investigate Before Initializing

When the project is non-clean, do not initialize documentation files before
the investigation and plan approval. First verify that the native task/sub-agent
capability is available. If it is not, report `documentation initialization
blocked: sub-agent capability unavailable` and stop without edits.

Launch a fresh sub-agent to inspect repository instructions, changed and
untracked paths, relevant code, configuration, schemas, generated outputs, and
existing documentation. Require it to return:

1. A verified inventory of current documentation owners and missing or stale
   documentation work, including the source and minimum safe shell for every
   missing required owner, with primary `file:line` evidence where possible.
2. A separation of attributable current changes, likely historical/stale
   material, dead-code candidates, and conclusions that remain uncertain.
3. Only the material intent questions that can change documentation scope,
   truth, ownership, or whether work is obsolete.
4. A recommended documentation-epic scope and acceptance criteria, without
   editing files or inventing owner intent.

Use the sub-agent's evidence to ask the user its material questions. Do not
assume that changed code is live, intentional, or representative of the
current design. After answers are available, present a documentation plan that
identifies authoritative owners, additions and corrections, exclusions,
evidence gaps, and deterministic acceptance criteria. Wait for explicit
approval of that plan. Separate missing-owner shells and directory indexes from
the epic: they establish discoverability only, while substantive current-state
documentation belongs in the epic. Resolve any unknown shell format with the
user before approval.

After approval, invoke `/create-epic` with the approved plan, verified
evidence, and the explicit directive `documentation initialization requires an
epic`. Do not implement the plan in this command.

After the epic is created, re-discover required owners and documentation
directories, then initialize every missing owner and directory index, including
baseline fallbacks and any directory introduced by epic creation. Preserve the
established format and create only an empty or template shell plus required file
maps; do not add substantive current-state documentation scoped by the epic.
Apply the same dirty-target and concurrent-edit protections as the clean-project
path.

Report the created epic's path and baseline owners and indexes initialized,
then instruct the user to run `/finish-session`, followed by `/epics-manager`
with that epic's path.
