---
name: receiving-code-review
description: Use when code review feedback must be evaluated, clarified, prioritized, or implemented.
---

# Receiving Code Review

## Purpose

Convert review feedback into verified technical decisions. Treat each comment as a claim about requirements or code behavior, not as an automatic instruction.

## Evaluate Feedback

Apply [Parsimony and Actionable Checks](../planner/references/parsimony.md). Challenge unnecessary safeguards as well as omissions; preserve binding acceptance through existing gates.

For each item:

1. Identify the requested outcome and cited evidence.
2. Inspect the referenced code and relevant requirements.
3. Classify the item as valid, invalid, ambiguous, already addressed, or outside scope.
4. Determine its impact and dependencies on other findings.
5. Record the intended action or evidence-based reason for declining it.

If missing context prevents classification, ask a specific question. Independent, well-understood items may proceed when doing so cannot invalidate or conceal the unresolved item.

## Prioritize

Apply fixes in an order supported by dependencies and risk:

1. correctness, security, data-loss, and build blockers
2. prerequisite or broad mechanical fixes
3. localized behavior fixes
4. refactors and lower-impact improvements

Do not implement speculative infrastructure or compatibility behavior without observable use, a stated requirement, persisted data, or an external consumer.

## Executable corrections

Evaluate findings against the requested work. Fix ordinary in-scope defects without a new
approval envelope or correction template; ask the owner for material scope or permission
changes. Keep the reviewer read-only and implement each independently verifiable correction
in a focused commit after relevant checks. Re-review the updated range before acceptance.
No schema dispositions, receipt chain or numerical repair budget is required.

## Implement And Verify

- Reproduce a reported defect when feasible before changing code.
- Change one independently verifiable item at a time.
- Run the narrow relevant check, then the broader affected checks.
- Re-read the original comment after verification to confirm the requested outcome is met.
- If a fix changes architecture, public behavior, or agreed scope, obtain the required decision before continuing.

## Disagreement

Decline or question feedback when evidence shows it would break behavior, contradict requirements, duplicate existing handling, or add unused scope. Cite code, tests, documentation, or compatibility constraints. If evidence is unavailable, state what cannot be verified and what would resolve it.

When new evidence disproves an earlier position, update the classification and proceed from the corrected facts.

## Completion Check

- Every review item has a visible disposition.
- Clarifications are specific and limited to material ambiguity.
- Accepted changes have verification evidence.
- Declined items have technical rationale.
- Remaining risks or unresolved decisions are explicit.

## Mandatory task checkpoint

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md). Review is read-only until an authorized fix becomes a separate verified retained task; unknown inherited changes stop.
