---
name: receiving-code-review
description: Use when code review feedback must be evaluated, clarified, prioritized, or implemented.
---

# Receiving Code Review

## Purpose

Convert review feedback into verified technical decisions. Treat each comment as a claim about requirements or code behavior, not as an automatic instruction.

## Evaluate Feedback

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

## Optional Jev-on advisory investigation ranking

Use this optional seam only when **Jev-on mode** is active, the instrumented tool is available, and there are **2 to 50** review comments awaiting investigation. Give each comment a stable opaque ID and retain the complete original review-comment set outside telemetry; all originals remain visible to the main agent. Jev-on authentication is provider-scoped: this suite is installed and tested with `jev auth set --provider openrouter` (the installer default; override with `--jev-provider`).

Only `jev_rank` is the measured Jev interface; never use raw shell or MCP Jev. Do not send credentials, secrets, personal data, or unauthorized sensitive payloads. Ask `jev_rank` only to rank investigation priority, with ambiguity and high impact increasing priority. Jev cannot reject a finding, classify it, authorize a change, or establish correctness.

Evaluate every original comment from its cited evidence. Inspect cited code and relevant requirements. Every original review comment has a visible disposition. Record `jev_disposition` for every ranked proposal as accepted, overridden, or not used after the main-agent review. If Jev-on is absent or `jev_rank` returns no proposals, use the original manual path and evaluate the complete original review-comment set manually.

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
