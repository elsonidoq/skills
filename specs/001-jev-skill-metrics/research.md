# Phase 0 Research: Measurable Jev Skill Assistance

## R1. Instrumentation boundary

**Decision**: Implement one Pi extension that registers the model-callable `jev_rank`,
`jev_disposition`, and `jev_metrics` tools plus the user-facing `/jev-metrics` command. Only
`jev_rank` invokes Jev. `jev_disposition` records an explicit per-proposal outcome, and
`jev_metrics` deterministically reads or closes out the event stream.

**Rationale**: Pi 0.87.1's installed extension API supports model-callable tools with
`registerTool()`, commands with `registerCommand()`, non-context session entries with
`appendEntry()`, session identity through `ctx.sessionManager.getSessionId()`, and active-branch
reconstruction through `getBranch()`. A dedicated tool is the only reliable coverage boundary:
watching shell or MCP traffic cannot establish that Jev was used by an approved seam, and no event
hook can infer semantic acceptance without an explicit disposition.

**Alternatives considered**:

- Observe shell/MCP calls: rejected because coverage is incomplete and acceptance cannot be inferred.
- Ask the model to maintain counters: rejected because it is neither deterministic nor durable.
- Infer acceptance from subsequent prose: rejected because silence and model wording are not a
  disposition contract.
- Use one overloaded tool for ranking, disposition, retrieval, and export: rejected because separate
  schemas make authorization, validation, and privacy boundaries inspectable.

## R2. Jev invocation and ranking shape

**Decision**: Spawn the installed `jev` executable as `jev run -`, pass one JSON request on stdin,
and ask one ordered `score` question for each caller-supplied candidate. Rank candidates
stably by score descending and original input order as the tie-breaker. A successful invocation
produces exactly one proposal per input candidate. Reject more than 50 candidates and return to the
manual workflow instead of silently truncating or splitting the comparison.

**Rationale**: The inspected `jev-cli` 0.6.3 contract supports complete batched request objects on
stdin, emits a single JSON object on stdout, exposes answers under caller-defined question keys, and
uses exit codes 1–4 for malformed/non-retryable, local input, authentication, and retryable failures.
A score per candidate makes the proposal unit stable and supports all eight ordering/grouping seams.
A fixed maximum proves that every call is bounded; refusing oversized input avoids incomparable
scores across separately evaluated batches.

**Alternatives considered**:

- One `choice` across all candidates: rejected because it yields one winner rather than one proposal
  per candidate.
- Repeated one-candidate CLI calls: rejected because it inflates invocation counts and adds avoidable
  network calls.
- Chunk candidate sets above the limit: rejected because cross-batch rank is not defined.
- Treat a confidence threshold as automatic acceptance: rejected because Jev confidence is not
  calibrated and the main agent must decide every disposition.

## R3. Stable identifiers and event semantics

**Decision**: Generate a random UUID for each invocation. Require a seam-owned opaque candidate ID
matching a conservative identifier grammar, and generate proposal IDs from the invocation UUID and
candidate ID rather than from candidate content. Record an invocation event before starting the Jev
process, then a terminal event that marks `succeeded`, `unavailable`, `failed`, or `malformed`.
Only a succeeded terminal event may introduce proposal IDs.

For dispositions, use first-valid-write semantics per proposal: replaying the same disposition is an
idempotent no-op; a conflicting second disposition, an unknown proposal, or a proposal from another
active session/branch is invalid and cannot change counters. Missing disposition is derived as
`pending`.

**Rationale**: UUIDs avoid embedding candidate content or repository paths. A two-event invocation
lifecycle means a crash or cancellation after launch remains an attempt rather than disappearing.
First-valid-write semantics is consistent with one explicit disposition per proposal and makes
replays deterministic.

**Alternatives considered**:

- Hash candidate text into identifiers: rejected because even hashes create avoidable linkage to
  potentially sensitive source material.
- Last-write-wins dispositions: rejected because replays could alter already reported metrics.
- Store aggregate counters directly: rejected because branch navigation and duplicate handling
  cannot be reconstructed or audited safely.

## R4. Session persistence, branch behavior, and metrics derivation

**Decision**: Store telemetry as versioned Pi custom session entries excluded from model context and
reconstruct state only from `ctx.sessionManager.getBranch()` on startup, reload, resume, fork, and
tree navigation. Serialize event mutations inside the extension because Pi may execute sibling tool
calls concurrently. Derive totals from validated events; never persist mutable counters as the source
of truth.

**Rationale**: The installed Pi documentation explicitly recommends `appendEntry()` for durable
non-context session data and active-branch reconstruction for branch-sensitive state. This naturally
prevents abandoned branches from inflating the current branch. It also lets reload and resume recover
the same event stream without an independent session database.

**Alternatives considered**:

- A repository-local event log: rejected because it duplicates Pi session state, requires branch and
  concurrency reconciliation, and risks accidental commit.
- In-memory-only state: rejected because reload and resume would silently reset metrics.
- Scan every session-file entry: rejected because abandoned branches would be counted.

## R5. Cross-session CSV

**Decision**: On explicit `finish-session` closeout, call `jev_metrics` with `action=closeout` to
append exactly one RFC 4180 CSV row for the Pi session. Store the file under
`${XDG_STATE_HOME:-~/.local/state}/pi/jev-metrics/<sha256(canonical-project-root)>.csv`. The project
fingerprint partitions files but is not written into a row. Rows contain only schema version,
closeout time, Pi session ID, active leaf ID, a sorted pipe-delimited list of approved skill IDs,
aggregate counters, invalid-event count, and the fixed coverage label `instrumented-only`.

Append under a local lock and suppress a duplicate session ID. `/jev-metrics history` reads this file.
A missing, unreadable, or invalid store is reported as such; it is never converted to a zero total.

**Rationale**: XDG state is persistent but not documentation and is not placed in a target repository.
One session row honors the approved closeout contract. The row has enough identifiers and aggregate
counters for later review without candidate bodies, logs, prompts, credentials, project paths, or
user identity.

**Alternatives considered**:

- One row per skill: rejected because the owner settled one aggregate row per session.
- JSON embedded in a CSV cell for per-skill history: rejected as unnecessary complexity; per-skill
  detail remains available in active-session metrics.
- Put CSV under `docs/` or `memory/`: rejected because metrics state is neither current-state
  documentation nor trigger-first memory.
- Store a global project path column: rejected because paths may contain personal information.

## R6. SpecKit distribution

**Decision**: Ship a project-installable SpecKit preset that appends Jev seam guidance to exactly
`speckit.analyze`, `speckit.checklist`, `speckit.clarify`, and `speckit.tasks`. Install it through the
SpecKit 1.0.12 preset resolver and verify each composed artifact with `specify preset resolve` and
`specify artifact info`. Never patch generated `.pi/prompts/speckit.*.md` files directly.

**Rationale**: The installed toolkit's extension command namespace cannot shadow core commands, while
its preset system explicitly supports `append` and `wrap` composition over core commands and
reconciles generated integration prompts. A project-local preset is therefore the supported override
layer for modifying existing core seams without owning generated files.

**Alternatives considered**:

- A SpecKit extension with commands named like the four core commands: rejected because SpecKit
  1.0.12 rejects core-command collisions.
- Direct edits to `.pi/prompts/`: rejected because integration upgrade/reconciliation overwrites
  generated prompts.
- Four replacement commands: rejected because copying the complete core prompt would drift; append
  composition retains upstream behavior and adds only the bounded Jev seam.

## R7. Installation and activation

**Decision**: Keep the existing manual suite as the default. A requested Jev-on install performs all
preflight checks before activating any seam: compatible Pi, loadable tracking extension, compatible
`jev-cli`, successful `jev auth test`, and, when SpecKit seams are requested for a target project, a
compatible project-local SpecKit preset capability. Stage changes and roll back on failure. The
successful Jev-on path activates the tracker before optimized skill/preset instructions.

**Rationale**: Presence of an executable or a stored key does not prove an authenticated Jev path.
The spec requires Jev-on to fail before enabling a seam if Jev or tracking is unavailable. In manual
mode, the optimized instructions remain unreachable because the instrumented tools are absent and the
original workflow remains intact.

**Alternatives considered**:

- Warn and continue in Jev-on mode: rejected by FR-008.
- Check only `command -v jev`: rejected because it misses authentication and response-contract
  compatibility.
- Always install the extension: rejected because non-Jev-on installations must preserve the original
  manual workflow without implying measured use.

## R8. Verification and privacy

**Decision**: Put aggregation, schema validation, Jev-response parsing, CSV rendering, and seam
fixtures in pure JavaScript modules tested with Node's built-in test runner. Test the Pi adapter with
a fake ExtensionAPI/session manager and the Jev client with a fake executable/process adapter. Add
fixture-driven checks for all eight seams, duplicate/conflicting dispositions, branch reconstruction,
reload/resume, missing/corrupt stores, CLI exit mappings, CSV idempotency, and forbidden telemetry
strings. No acceptance command calls a live Jev provider or runs a benchmark.

**Rationale**: The repository currently has no Node package/test framework, while the installed Pi
runtime supports JavaScript extensions. Built-in modules avoid a new runtime dependency and allow
fully deterministic tests. A fake process boundary proves request/response handling without cost or
sensitive data transmission.

**Alternatives considered**:

- Live Jev calls in the test suite: rejected because they are nondeterministic, potentially paid, and
  outside the approved no-benchmark boundary.
- Snapshot-only tests: rejected because counter invariants and duplicate protection need explicit
  assertions.
- Persist raw payload fixtures: rejected because privacy tests should use synthetic sentinels and
  assert those sentinels never enter telemetry or CSV.

## Resolved unknowns and observed capability notes

- Pi is installed at version 0.87.1 and its extension declarations support every planned integration
  point.
- SpecKit planning assets and prompt workflow are installed locally at version 1.0.12. No
  `.specify/extensions.yml` exists, so this planning run had no pre- or post-plan hooks.
- SpecKit 1.0.12 has no installed presets in this checkout, but supports project-local preset
  composition and introspection.
- `jev-cli` 0.6.3 is installed, but `jev auth status` reported that the official API key is not
  stored. That is expected to make a Jev-on installation fail; it does not block design or
  deterministic implementation tests.
- The project memory index is `memory/MEMORY.md`; it records no gotchas, so no memory constraints
  beyond the repository instructions apply.
