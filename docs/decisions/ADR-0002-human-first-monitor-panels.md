# ADR-0002: Human-first workflow-monitor panels

## Status

Accepted owner direction; implementation and combined source/task approval remain pending.
Recorded 2026-10-21. Acceptance of this decision is not feature acceptance.

## Decision

Prioritize meaningful recorded work titles, plain-language progress and outcomes, blockers
and available review findings in monitor panels. Technical IDs and long reference lists
must not fill the default view; retain them as accessible secondary diagnostic information.

Keep the exact selected-run identity persistently visible for unambiguous selection.
A concise useful task code may distinguish work; opaque hashes must not replace an explanation.

## Context and rationale

The owner needs to understand what happened and what prevents progress, not decode internal
references. Existing recorded findings/reasons should explain the state before technical
provenance. Human-facing presentation must still distinguish a successfully returned agent
from accepted work, including rejected reviews or failed checks.

## Consequences and limits

- Use recorded facts and the completed T017/T018 result/finding contract after inspection.
  When an explanation is absent, say “not recorded” or “unknown”; do not fabricate it.
- Keep full IDs, ranges, history and original rejection/failure evidence discoverable in
  expandable technical references. This is presentation hierarchy, not data deletion or a
  reinstated privacy filter.
- Render recorded text inertly; preserve credential protection, read-only access and existing
  execution/acceptance semantics. No new summarizing model calls or transcript reconstruction.
- Exact panel structure and test changes remain derived proposals for combined approval.
  Verify actual production panel content/order and include it in the post-run visual review.

## Provenance

The owner's explicit instruction was: “also, make sure the information showed in the panels
are meaningful for a human. Do not fill the screen with ids”. The existing persistent
selected-run requirement is preserved rather than silently removed. The owner requested
retaining decisions and approved this ADR store/recording through `ask_user`; combined
implementation approval remains pending.

Authoritative behavior and acceptance: [readability TinySpec R4/A3](../plans/workflow-monitor-readable-graph-tinyspec.md#r4--human-first-panels-and-headers).
Derived work proposal: [readability tasks](../plans/workflow-monitor-readable-graph-tasks.md).
Related presentation decision: [ADR-0001](ADR-0001-dependency-first-top-to-bottom-graph.md).

## Supersession

No preceding ADR is superseded. No superseding ADR is recorded.
