---
name: brainstorming
description: Use when a request would create a feature, change behavior, introduce a component, or make a design choice whose requirements are not yet approved.
---

# Brainstorming

## Purpose

Turn an idea into an approved design before implementation. Scale the process to the uncertainty and impact of the request, not to a fixed ceremony.

## Choose A Path

- **Spike:** The requested result is feasibility evidence, not retained implementation.
- **Bounded:** An existing flow is being changed, its boundaries are visible, and no public interface or subsystem structure changes.
- **Architectural:** The request creates a subsystem, changes shared interfaces, or leaves major boundaries unresolved.

If investigation reveals broader impact, move to the heavier path.

## Workflow

1. Inspect available project context, constraints, and existing behavior. If context cannot be inspected, state that limitation and ask for the minimum missing information.
2. Classify the path and tell the user which path applies.
3. Resolve material ambiguity one question at a time. Prefer concrete options when the choice set is known.
4. Present the design at the path's required depth.
5. Obtain explicit approval before retained implementation begins.

### Spike

State the question, probe, success signal, and disposal boundary. After approval, investigate with the least costly reliable method. Report evidence and a recommendation; do not silently retain exploratory changes.

### Bounded

Present a short design covering the changed behavior, affected files or components, error cases, and verification. Stop for approval. No separate design document is required unless the repository or user requires one.

### Architectural

Offer two or three viable approaches with trade-offs and a recommendation. Present the selected design in reviewable sections covering boundaries, data flow, failure handling, compatibility, and testing. Record the approved design only when the repository, user, or downstream workflow requires an artifact; choose its location from documented project conventions or ask.

## Decision Rules

Apply [Parsimony and Actionable Checks](../planner/references/parsimony.md). Apply when choosing the smallest approach.

- Ask only questions whose answers can change the design.
- Follow established project patterns unless they conflict with the request or create a demonstrated risk.
- Include targeted cleanup only when necessary for the requested change.
- Use a visual aid only when the decision concerns spatial or visual differences and an available tool can produce it. Otherwise use text. If the tool is unavailable, describe the alternatives textually.
- Transition to planning or implementation through the capabilities available in the current environment; do not assume a particular agent, tool, file layout, branch, or commit workflow.

## Completion Check

- Scope and success conditions are explicit.
- Important alternatives and trade-offs were considered.
- Error, compatibility, and verification expectations are stated.
- The user approved the design that will be implemented.

## Mandatory task checkpoint

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md). Exploration remains read-only/disposable until existing approval authorizes retained implementation; no empty checkpoint for analysis.
