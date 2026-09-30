# Feature Specification: Measurable Jev Skill Assistance

**Feature Branch**: `001-jev-skill-metrics`  
**Created**: 2026-09-29  
**Status**: Approved for planning  
**Input**: Owner-approved epic at `docs/epics/jev-skill-optimizations.md`

## Approvals

- **Specification approval**: Owner approved the current specification for planning on 2026-09-29.

## Clarifications

### Session 2026-09-29

- Q: Which workflow writes persistent session metrics? → A: The `finish-session` skill appends one aggregate CSV row for the session.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve trusted skill-use metrics (Priority: P1)

A Pi user runs an optimized skill and then retrieves counts of Jev activity and the agent's explicit
use of its proposals, without asking the agent to remember or calculate totals.

**Why this priority**: Measurable, trustworthy telemetry is required before any optimized seam may
be enabled.

**Independent Test**: After one tracked Jev attempt that returns three ranked candidates, the user
can retrieve session and per-skill counts showing one attempt, one success, three proposals, and
three pending proposals.

**Acceptance Scenarios**:

1. **Given** a successful tracked result with three candidate proposals and no dispositions, **When**
   the user requests metrics, **Then** the result shows one attempt, one success, three proposals,
   zero accepted, zero overridden, zero not used, and three pending for that skill and session.
2. **Given** explicit dispositions accepting two candidates and overriding one candidate, **When**
   the user requests metrics, **Then** the result shows two accepted, one overridden, and no pending
   proposals, and repeated disposition events do not change those counts.
3. **Given** an owner closes the session, **When** the `finish-session` skill runs, **Then** it
   appends a simple local CSV row containing only aggregate counters and identifiers needed for later
   review, not raw candidate text or credentials.

---

### User Story 2 - Use bounded Jev advice safely (Priority: P2)

A Pi user receives Jev ordering only for an explicit, bounded candidate set while the main agent
retains the full evidence and makes all engineering, authorization, and verification decisions.

**Why this priority**: The optimization must narrow candidate width without replacing judgment or
silently losing evidence.

**Independent Test**: An instrumented seam presents a ranked result with stable candidate IDs, while
the complete original candidate set remains available and the required manual/final checks still run.

**Acceptance Scenarios**:

1. **Given** an approved optimized seam with an explicit candidate set, **When** Jev returns a
   ranking, **Then** every ranked candidate has a stable proposal ID and can receive one explicit
   disposition.
2. **Given** a low-confidence, ambiguous, or high-impact candidate, **When** the agent evaluates it,
   **Then** the agent retains responsibility for the decision and can inspect the original evidence.
3. **Given** a failed, malformed, or unavailable Jev response, **When** the skill is not installed in
   Jev-on mode, **Then** it follows the original manual workflow and does not claim tracked use.

---

### User Story 3 - Install and maintain compatible optimizations (Priority: P3)

A maintainer can install the suite with Jev-on behavior only when its required Jev capability and
tracking tool are available, and can distribute SpecKit seam changes without patching generated base
prompts.

**Why this priority**: A hard Jev-on contract and upgrade-safe SpecKit distribution prevent silently
unmeasured or nonportable behavior.

**Independent Test**: A Jev-on installation fails clearly when Jev or the tracking tool is missing;
a compatible installation uses a project-owned SpecKit extension or override and leaves base toolkit
prompts upgradeable.

**Acceptance Scenarios**:

1. **Given** a user selects Jev-on installation mode, **When** Jev is unavailable or unauthenticated
   or the tracking tool is unavailable, **Then** installation fails with an actionable diagnostic and
   does not enable an optimized seam.
2. **Given** a user does not select Jev-on mode, **When** Jev or the tracker is unavailable, **Then**
   the original manual skill behavior remains usable and makes no measured-use claim.
3. **Given** a target project uses compatible SpecKit, **When** its four seam customizations are
   installed, **Then** they are supplied by a project-owned extension or override layer rather than
   direct changes to generated `.pi/prompts/speckit.*.md` files.

### Edge Cases

- A failed tracked call counts as an attempt but not a success or a usable proposal.
- Duplicate, malformed, unknown, or cross-session disposition events do not inflate or misattribute
  counts and are reported as invalid or untracked rather than treated as acceptance.
- Reload, resume, branch changes, and a missing metrics store must not silently report misleading
  zeroes.
- Raw shell or MCP Jev calls outside the instrumented tool are explicitly reported as untracked; the
  metrics view does not claim to observe them.
- The `finish-session` skill appends the closeout CSV row even if documentation ownership/routing is
  not yet initialized; the row is metrics state, not a substitute for documentation ownership.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The suite MUST provide a Pi-native tracked Jev interface that records an attempted
  invocation, a successful invocation, stable session and skill identifiers, a stable invocation
  identifier, result status, and timestamp without storing raw candidates, logs, secrets, personal
  data, or credentials.
- **FR-002**: The tracked interface MUST emit a stable proposal identifier for each ranked candidate
  from a successful result. Each candidate, rather than the whole ranking, is one proposal unit.
- **FR-003**: The agent MUST record one structured disposition referencing a proposal identifier when
  it accepts, overrides, or does not use that proposal; absence of a disposition remains pending or
  unknown and MUST NOT be counted as accepted or rejected.
- **FR-004**: The metrics retrieval path MUST show active-session totals and per-skill attempts,
  successes, proposals, accepted, overridden, not used, pending, and clear denominators without
  relying on model-maintained totals.
- **FR-005**: The `finish-session` skill MUST append simple aggregate metrics to a local CSV for
  cross-session retrieval. The CSV is metrics state rather than an authoritative documentation owner
  and MUST exclude raw candidate bodies, logs, secrets, personal data, and credentials.
- **FR-006**: The harness MUST validate event schema, prevent duplicate counting, and make failed,
  malformed, unavailable, missing-store, and uninstrumented states explicit rather than reporting a
  misleading zero.
- **FR-007**: The harness MUST preserve original evidence and manual behavior for installations that
  do not select Jev-on mode; it MUST NOT force a Jev call or block manual fallback in that mode.
- **FR-008**: A Jev-on installation mode MUST fail before enabling any optimized seam when Jev is
  unavailable or unauthenticated or when the tracking tool is unavailable. The failure MUST identify
  the missing prerequisite and the action needed to resolve it.
- **FR-009**: The optimized paths MUST initially cover exactly these global-suite seams:
  `scientific-method-debugging`, `receiving-code-review`, `coordinate-implementation`, and
  `track-open-issue`; `compact-memory` is excluded.
- **FR-010**: The optimized paths MUST initially cover exactly these SpecKit seams: analysis,
  checklist, clarification, and tasks. Their project customizations MUST be distributed through a
  project-owned SpecKit extension or override, not by direct modification of generated base prompts.
- **FR-011**: Every optimized seam MUST operate only on an explicit bounded candidate set, retain the
  full original set, treat uncertain, ambiguous, and high-impact decisions as main-agent work, and
  preserve existing required final verification.
- **FR-012**: The main agent MUST retain responsibility for architecture, root-cause hypotheses, code
  generation, owner authorization, final correctness, and final verification. Jev output MUST only
  narrow candidates or rank investigation priority.
- **FR-013**: The initial seam behaviors MUST be: rank observed log/test chunks for debugging; rank
  review comments for investigation while every comment receives a main-agent disposition; rank
  targeted tests while mandatory checks remain; rank possible duplicate open issues; rank
  requirement-task associations and low-risk cross-artifact findings; group/rank checklist candidates;
  rank more than five clarification candidates; and rank likely user-story matches for entities or
  interface contracts.
- **FR-014**: The feature MUST provide deterministic, fixture-driven verification of counter
  arithmetic, proposal/disposition handling, duplicate protection, display output, failed calls, and
  privacy boundaries.
- **FR-015**: The feature MUST NOT run an A/B benchmark or claim token, latency, or quality
  improvement. Any later evaluation requires separate owner approval and paired existing-versus-
  instrumented runs including fallback rate and downstream regret.

### Key Entities *(include if feature involves data)*

- **Invocation event**: A recorded attempt by the instrumented Pi tool, identified by invocation,
  session, and skill, with result status and timestamp.
- **Proposal**: One ranked candidate from a successful invocation, identified stably within that
  invocation and attributed to its skill and session.
- **Disposition**: A structured, idempotent statement that a proposal was accepted, overridden, or
  not used; absent disposition is pending or unknown.
- **Metrics summary**: Aggregate counters by session and skill, with an optional closeout CSV row for
  later aggregate review.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a fixture with one successful tracked attempt and three ranked candidates, the
  metrics view reports exactly one attempt, one success, three proposals, and three pending proposals
  before any dispositions.
- **SC-002**: In a fixture with two accepted and one overridden candidate dispositions, the metrics
  view reports exactly those counts and remains unchanged after duplicate events are replayed.
- **SC-003**: For each of the eight named seams, inspection demonstrates one explicit bounded input,
  access to the original candidate set, and unchanged main-agent final-verification responsibility.
- **SC-004**: Jev-on installation tests fail in 100% of fixtures that omit Jev authentication or the
  tracking tool, with no optimized seam enabled; non-Jev-on fixtures retain manual behavior.
- **SC-005**: The session metrics view and any closeout CSV fixture contain zero raw candidate bodies,
  logs, secrets, personal data, or credentials.
- **SC-006**: This feature's recorded verification evidence contains no benchmark execution or claim
  of performance, token, or quality improvement.

## Assumptions

- The existing owner-approved epic remains the authoritative scope source; no benchmark, global tool
  routing, irreversible/deployment action, or `compact-memory` optimization is included.
- A Pi extension can expose a dedicated instrumented tool and a paired disposition action, subject to
  planning verification against the installed Pi extension API.
- Cross-session metrics use a simple CSV append during the `finish-session` workflow. This metrics
  state is distinct from the project's authoritative documentation and does not require a
  documentation-routing decision to append.
- SpecKit extensions or overrides can be validated during planning against the project-local toolkit;
  if the selected mechanism is incompatible, no SpecKit seam is enabled until the owner approves a
  revised distribution decision.
- A conservative numerical confidence threshold may be evaluated during planning, but no score is
  treated as calibrated and no high-impact decision passes automatically.
