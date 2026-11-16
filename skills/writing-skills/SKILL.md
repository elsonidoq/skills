---
name: writing-skills
description: Use when creating or materially revising a reusable agent skill, including its trigger, workflow, examples, dependencies, or supporting files.
---

# Writing Skills

## Purpose

Write concise, discoverable guidance that remains correct across projects and capable environments. Put project-specific rules in project instructions and automate purely mechanical constraints.

## Global Portability

A global skill must not assume:

- a named project, organization, repository, branch, commit, agent, or model
- project data, repository state, or undocumented local paths
- a particular shell, package manager, hosting service, or tool vocabulary
- that optional network, filesystem, review, browser, or delegation capabilities exist

Express branches with observable conditions. For example: "if an independent reviewer capability is available" rather than "dispatch the reviewer agent."

### Reusable Dependency Exception

A global skill may depend on a reusable tool, script, reference, or other skill only when all of these are true:

1. The dependency provides general capability rather than project knowledge.
2. Its availability can be checked before use.
3. The skill states that capability check.
4. The skill defines a safe unavailable fallback or an explicit stop condition.
5. Any relative cross-reference resolves within the distributed skill, and any external skill reference is discoverable by name.

If any condition fails, remove the dependency or make the guidance self-contained.
In this repository the suite's runtime and capabilities are declared in the global
`REQUIREMENTS.md`; a skill that depends on a capability cites that file while still
verifying availability at run time. Planning-role assignments belong to the canonical saved
assignment owner, not reusable skill text.

## Authoring

1. Use a lowercase, hyphenated directory name and matching frontmatter `name`.
2. Start `description` with "Use when..." and state only concrete loading triggers, symptoms, or contexts. Do not summarize the workflow.
3. Identify the job, inputs, decisions, outputs/consumers and authority boundary. Separate behavior this skill owns from results it consumes from an existing owner.
4. Draft a fresh procedure from that conceptual contract, not the old headings or sentence inventory. Lead with normal work; put prerequisites and exceptions at the operation that needs them. Use observable conditions for branches and fallbacks.
5. Prefer a positive recipe or output contract for shape problems. Reserve prohibitions for demonstrated safety or discipline failures.
6. State each rule once. Delete duplication rather than move it into references. For an existing owner, state when to use it and which result to consume. Retain supporting files only for necessary reusable tools or substantial reference material linked from the main file.
7. After drafting, compare the source and canonical contracts for lost behavior, capabilities or guarantees. Restore necessary behavior, not old prose; surface genuine conflicts rather than silently changing authority.
8. Read the procedure for repeated rules, excessive setup, jargon and checklists that restate the steps. Choose headings that explain this job; no identical template or size cap is required. Include an example only when it explains a non-obvious decision better than the rule itself.

## Validation

Before publishing, verify:

- directory name, frontmatter name, and references agree
- the description is trigger-only and uses concrete discovery terms
- no named project, fixed path, branch, commit, model, agent, or shell workflow is assumed
- each reusable dependency has a stated capability check and unavailable fallback
- branching conditions are observable and actions are executable
- the main file contains no redundant sections or examples
- every supporting file is still required and referenced

Use the smallest meaningful check of the changed behavior and report its limits. For a discipline-enforcing or high-risk change, use realistic pressure scenarios where they test the affected risk; paired before/after runs are not universally required. For ordinary guidance, a focused read-through or static check may suffice. Preserve applicable required runtime, integration, application, security and permission checks. Static or fixture checks do not prove model obedience or replace required live acceptance and its authority.

## Mandatory task checkpoint

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md). A material reusable-skill deliverable is a bounded retained task; use the shared checkpoint after validation.
