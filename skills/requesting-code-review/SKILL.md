---
name: requesting-code-review
description: Use when a completed change needs independent assessment before integration, handoff, or dependent work continues.
---

# Requesting Code Review

## Purpose

Obtain a findings-first assessment against explicit requirements and observable change evidence.

## Prepare The Review

1. Identify the requirements or acceptance criteria.
2. Define the exact change scope using the evidence available: a working-tree diff, staged diff, patch, pull request, file list, or revision range. Do not invent a base branch or commit.
3. Include verification already performed and known constraints.
4. Exclude unrelated session history and secrets.

## Choose A Review Path

- If an independent reviewer capability is available, provide it the prepared context and the contract in [code-reviewer.md](code-reviewer.md).
- For executable Coordinate Implementation, missing independent review leaves final acceptance incomplete; self-review cannot substitute. Review the actual full committed range in a fresh read-only context against the requested work and relevant project checks. No schema, provenance receipt or evidence template is required. For other workflows, label any explicitly permitted self-review as self-review, never independent review.
- If the change evidence cannot be accessed, request or produce an accessible patch or file set. Do not claim a review occurred without reading the changed code.

The reviewer mechanism may be an agent, person, service, or local review tool. Do not assume a fixed agent name, model, Git host, branch, commit layout, or shell command.

## Act On Findings

- Address blocking correctness, security, data-loss, and requirement failures before proceeding.
- Resolve other findings according to their demonstrated impact and project policy.
- Verify technically questionable feedback against code, tests, and requirements; respond with evidence when declining it.
- Re-run affected checks after fixes. Request another review when fixes materially change behavior or architecture.

## Completion Check

- The reviewer read the actual change scope.
- Findings cite concrete locations and impact.
- The verdict states whether the change is ready and under what conditions.
- Unresolved findings and verification gaps are visible to the next decision-maker.

## Mandatory task checkpoint

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md). Review requests preserve exact review scope; a read-only request does not create a commit or grant implementation authority.
