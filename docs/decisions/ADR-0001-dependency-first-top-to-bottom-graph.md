# ADR-0001: Dependency-first, top-to-bottom workflow graph

## Status

Accepted owner direction; implementation and combined source/task approval remain pending.
Recorded 2026-10-21. This record does not approve the complete implementation proposal.

## Decision

Make task dependencies the workflow graph's primary structure and lay out that backbone
**top-to-bottom**. Show other relation types by default only when crucial to understanding
the current state, rather than showing every recorded connection equally.

Build the readability change on the completed T017/T018 chain and overview implementation.
Inspect those delivered interfaces before affected work; do not build an interim competing
mapper/view and assume a later Git merge will establish compatibility.

## Context and rationale

The owner supplied an unreadable graph screenshot with generic task labels, crossing lines
and repeated relation labels. Changing to a different Sugiyama-style engine alone would not
address the mixing of dependency, ownership and recorded-order relations.

The initial retained left-to-right assumption came from compatibility with T018, not proven
readability. The owner's later explicit top-to-bottom choice supersedes that assumption for
this new scope. Preserve T018's other chain, overview, panel and navigation outcomes.

## Consequences and limits

- Dependency structure must stay complete; do not manufacture dependencies from execution order.
- Ownership grouping and eligible stopping/correction connections are detailed proposals in
  the TinySpec, not additional owner-approved mechanisms merely because this ADR is accepted.
- Preserve distinct attempts, failures, pending work, planned versus actual review and
  execution outcome versus acceptance. Secondary relations must not obscure those facts.
- Reuse existing presentation mechanisms where sufficient. Actual layout/group geometry and
  human readability require production-view evidence; a clean Git merge is not that proof.
- Delivery depends on inspecting completed T017/T018, and any material source/task adaptation
  requires the existing review/approval gates. Final visual acceptance remains post-run.

## Provenance

Owner conversation: “We should only show dependency edges unless there is another edge type
that is crucial to understanding the current state”; “Consider this will be merged into a
repo where T017 and T018 will be implemented.” The owner twice selected **“Use top-to-bottom”**
through `ask_user`, then requested retaining decisions and approved this ADR store/recording.
The final combined implementation approval questions were cancelled, not approved.

Authoritative behavior and acceptance: [readability TinySpec](../plans/workflow-monitor-readable-graph-tinyspec.md).
Derived work proposal: [tasks](../plans/workflow-monitor-readable-graph-tasks.md).
Integration producer: [session-reuse tasks T017/T018](../plans/session-reuse-metrics-permissions-tasks.json).

## Supersession

No preceding ADR is superseded. This records the later direction-only override described
above without rewriting historical T018 approval. No superseding ADR is recorded.
