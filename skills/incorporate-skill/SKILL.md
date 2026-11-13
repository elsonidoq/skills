---
name: incorporate-skill
description: Use when, and only when, adapting an external command or skill into the installed global pi configuration repository.
---

Adapt the source path named in the user's request into the installed global pi configuration repository. This workflow is proposal-first: do not
copy, edit, delete, stage, commit, or overwrite any asset until the owner explicitly approves the adaptation plan.

## Step 1: Identify the Source

1. Require one readable path from the user's request. If it is absent, unreadable, or neither a command Markdown file nor
   a skill directory containing `SKILL.md`, report the problem and stop.
2. Classify it:
   - **Command:** a Markdown command prompt, normally one `*.md` file.
   - **Skill:** a directory containing `SKILL.md` and any necessary supporting files.
3. Read `AGENTS.md` and `README.md`. For a skill, also read `skills/writing-skills/SKILL.md`. Read the closest
   comparable global asset when one exists.

## Step 2: Assess Portability

Apply this policy: a global asset must not assume a named project, its data, repository state, undocumented local
path, branch, deployed state, model, agent, tracker, or command.

A named reusable capability such as SpecKit, Railway, GitHub, Jev, or a configured agent is allowed only
when the asset:

1. states the dependency;
2. verifies it is available in the target project or runtime; and
3. states an unavailable fallback.

Identify each source assumption and classify it as:

- retain as portable;
- generalize through discovery and fallback;
- move to project-local instructions or a local skill; or
- remove as redundant, unsafe, stale, or git-owned history.

Also identify duplicated guidance, vague branches, hard-coded paths or commands, unsafe mutations, unverified
claims, credentials or sensitive examples, unsupported frontmatter, and supporting files that are no longer needed.

## Step 3: Propose the Adaptation

Present a concise plan containing:

1. Source path, classification, and proposed destination:
   - command: discover the installed command directory and use its `<name>.md` path; if command support or a
     writable directory is unavailable, recommend converting the prompt to a skill or stop with that limitation.
   - skill: this repository's `skills/<name>/SKILL.md`
2. Files to create, change, retain, remove, or move to project-local guidance.
3. Assumptions found, with the exact capability check and unavailable fallback for each reusable dependency.
4. The proposed frontmatter and a section-level outline.
5. Focused validation and fresh-review steps.

Stop and wait for explicit owner approval. Do not treat a request to inspect, summarize, or explain the source as
approval to import it.

## Step 4: Implement After Approval

Make only the approved changes. Preserve unrelated work and re-read a target immediately before editing; stop for a
direct conflict. Do not add credentials, tokens, personal data, or sensitive payloads.

For a skill, ensure the directory name matches frontmatter `name`, the description begins with `Use when...` and
states triggers rather than workflow, and supporting files are retained only when necessary. For a command, keep
the normal path lightweight, make capability checks and expensive work conditional, and state unavailable behavior.

Validate changed paths, frontmatter, local references, and relevant focused tests. If an independent reviewer
capability is available, request a fresh review for portability, safety, trigger accuracy, and accidental loss of
essential guidance. Otherwise, perform a separate self-review and report `independent review: UNAVAILABLE`. Report
the source, destination, changes, validations, review findings, and anything intentionally left project-local.

## Mandatory task checkpoint

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md). Adaptation-plan approval still precedes every write; after approval, owned retained changes checkpoint without adopting unknown work.
