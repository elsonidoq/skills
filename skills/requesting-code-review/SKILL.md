---
name: requesting-code-review
description: Use when a completed change needs independent assessment before integration, handoff, or dependent work continues.
---

# Requesting Code Review

## Purpose

Obtain a findings-first assessment against explicit requirements and observable change evidence.

## Prepare The Review

Apply [Parsimony and Actionable Checks](../planner/references/parsimony.md). Include source basis and legitimate-behavior costs for proposed safeguards.

For direct review requests in fresh or resumed contexts, consult [save-adr](../save-adr/SKILL.md)'s **Consult and propagate** contract when a discovered decision owner or supplied accepted constraints apply. Re-establish applicable accepted authority from the whole discovered index, relevant accepted records, and needed supersession links rather than parent context or a prior-read claim. Put each applicable accepted outcome, explicit mechanism constraint, and source link in the requirements or constraints already supplied with the review scope; proposed and superseded records are not current policy. Contradictory accepted authority or uncertain current supersession stops only the affected review pending an owner decision.

1. Identify the requirements or acceptance criteria.
2. Define the exact change scope using the evidence available: a working-tree diff, staged diff, patch, pull request, file list, or revision range. Do not invent a base branch or commit.
3. Include verification already performed and known constraints.
4. Exclude unrelated session history and secrets.

## Choose A Review Path

- If an independent reviewer capability is available, provide it the prepared context and the contract in [code-reviewer.md](code-reviewer.md).
- For executable Coordinate Implementation, missing independent review leaves final acceptance incomplete; self-review cannot substitute. Initially review the actual full committed range in a fresh read-only context against the requested work and relevant project checks. After repairs, provide the prior findings and passing coverage plus the actual repair delta; independently review fixes and affected interactions, carrying forward still-valid unaffected coverage rather than restarting the original review. Revisit invalidated conclusions with an explanation; never certify unchecked original work through a fix-only review. No schema, provenance receipt or evidence template is required. For other workflows, label any explicitly permitted self-review as self-review, never independent review.
- If the change evidence cannot be accessed, request or produce an accessible patch or file set. Do not claim a review occurred without reading the changed code.

The reviewer mechanism may be an agent, person, service, or local review tool. Do not assume a fixed agent name, model, Git host, branch, commit layout, or shell command.

## Act On Findings

- Address blocking correctness, security, data-loss, and requirement failures before proceeding.
- Resolve other findings according to their demonstrated impact and project policy.
- Verify technically questionable feedback against code, tests, and requirements; respond with evidence when declining it.
- Re-run affected checks after fixes. Independently review repairs and their affected interactions, confirming addressed findings and retaining unresolved findings or coverage gaps. Completion combines retained valid coverage with successful repair review; a repair alone is not acceptance.

## Completion Check

- The reviewer read the actual change scope.
- The outcome explicitly separates examined/passing areas from actionable defects; unchecked areas are not claimed as passing.
- Findings cite concrete locations and impact.
- The verdict states whether the change is ready and under what conditions.
- Unresolved findings and verification gaps are visible to the next decision-maker.

## Mandatory task checkpoint

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md). Review requests preserve exact review scope; a read-only request does not create a commit or grant implementation authority.
