# Dependency research contract

Shared by planner, TinySpec and architectural planning; apply within their existing
stages before consequential dependency decisions. This is evidence and persistence
guidance, not a separate workflow, artifact chain or approval stage. Verify this
reference is readable in the executing context; missing packaging stops the affected
stage with a missing-install report.

## Discover, trigger and reuse

Read repository instructions, dependency declarations/lockfiles, specific technical
owners, documentation indices and relevant project guidance first. Identify the actual
installed/targeted dependency and version/range, or report unresolved selection; do
not guess a version or assume this suite's documentation paths apply to the project.

First repository use, insufficient guidance, performance/reliability/architecture-
sensitive behavior or uncertainty triggers research. Trivial use can skip new internet
research with a brief reason; sufficiently documented relevant use can reuse guidance
with cited evidence. Risk-sensitive decisions still need adequate evidence. Check
version applicability, stale/conflicting claims and missing portions; refresh only
those portions. A recent date alone proves neither applicability nor completeness;
there is no universal freshness deadline or decorative date bump.

## Obtain sufficient evidence

Before required external research, verify actually usable, permitted search/fetch/
browser or equivalent capabilities in the executing context. Tool names/configuration
alone are not capability evidence; do not install missing tools or assume permission
for internet, paid or live operations. Adequate local guidance can satisfy evidence
without a new search call.

Use proportional current internet research when needed and permitted. Prefer source
material for the installed/targeted version: official documentation, official guides/
examples/repositories and maintainers first, reputable technical sources next, then
selective community evidence. Label newer-version differences; corroborate weaker
sources or retain their uncertainty. Inspect meaningful supporting sections, not just
search snippets or URL lists.

Investigate only concerns relevant to the decision: batching/concurrency, I/O,
synchronization/persistence, memory, lifecycle, transactions, caching/indexing,
retries/rate limits, deployment, pitfalls and version behavior. Do not turn this into
a dependency-wide audit or invent universal batching/flush rules.

## Classify and translate

Separate:

- **Documented recommendation:** inspected supporting source section/claim, primary
  URL and applicable version.
- **Repository-derived decision:** local evidence, resulting decision and rationale.
- **Assumption:** uncertainty and a defined validation check, not a documented rule.

Unsupported snippets, uninspected URLs, uncertain statements and generic model
recollection cannot satisfy required source evidence. Preserve the chain **source
recommendation/local evidence → derived decision/implementation constraint → observable
validation** in the compact TinySpec source or Standard specification/plan. Cite
supporting spans; make constraints and checks explicit rather than merely linking a
note. Material unresolved choices return to the existing owner gate.

## Persist within verified authority

Preselection inspection/research is read-only: keep findings in session context; do
not persist dependency docs, source, plan or decisions. During authorized selected
production, persist reusable guidance before readiness. Prefer the existing specific
repository technical owner and its discoverability index. If none exists, discover
conventions and verify/obtain bounded authority for a suitable owner and necessary
discovery-link destination before writing. Re-read each target immediately before
targeted updates and preserve unrelated content; stop on concurrent overlap.

The durable owner contains dependency/version or range, applicable practices and
pitfalls, repository-derived decisions/rationale, primary URLs tied to supporting
claims, research date for evolving guidance, and uncertainty/validation needs. Link
that canonical owner from planning artifacts; carry execution constraints/checks
there without duplicating the full note. Reused guidance gets necessary targeted
corrections only.

For Standard helpers, canonical research-document and necessary discovery-link writes
require explicit bounded permission **in addition to** detected SpecKit artifacts:
observed destinations, allowed changes and prohibited operations. This grants no
arbitrary documentation edits, product code writes or implementation authority.
Standalone/direct entry verifies equivalent selection/preparation and write authority;
caller invocation is not evidence of permission.

## Safe failure and return

If required tools, usable sources, version evidence or write authority are unavailable
or insufficient, stop affected consequential design and return the exact gap, affected
decisions and evidence/authority needed. No generic-knowledge fallback, fabricated
sources, automatic deferral, installation or premature readiness. Planner may obtain
explicit bounded owner deferral through existing gates; standalone callers return to
their owner. Record impact, allowed bounds and outstanding validation. A deferral does
not fabricate evidence or waive unrelated gates. Research-driven approved-specification
changes retain existing approval-renewal rules.

Return reuse/skip rationale, capability evidence, canonical owner/discovery locations,
version/provenance, supporting spans → constraints → checks, assumptions, deferrals
and remaining gaps for existing caller review/approval, not a new research approval.

## Simulated traceability example (not a library claim)

Suppose an inspected **simulated** version-specific guide section “Lifecycle” states
that queued work must complete before closing, and local call-site evidence shows
shutdown may race a queue. Classify the guide statement as a documented recommendation
and the shutdown sequencing as a repository-derived decision: constrain shutdown to
await queued work before close; verify with an observable test that pending work
completes before the close event. Any assumption about bounded wait time needs its own
check. This illustrates evidence → constraint → validation, not a universal library
rule or live research result.
