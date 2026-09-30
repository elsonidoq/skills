# Implementation Plan: Measurable Jev Skill Assistance

**Branch**: `001-jev-skill-metrics` | **Date**: 2026-09-29 | **Spec**: [spec.md](spec.md)

**Input**: Owner-approved feature specification at `specs/001-jev-skill-metrics/spec.md` and source
epic at `docs/epics/jev-skill-optimizations.md`.

## Approvals

- **Plan approval**: Owner approved this plan for delegated task generation on 2026-09-29. The
  approved scope is the current `plan.md` and linked Phase 0/1 artifacts in this directory.
- **Post-task analysis correction**: The main agent clarified delivery wording without changing
  scope, architecture, acceptance criteria, or authorization: source seam edits may precede the
  installer only when activation remains gated; the deterministic `finish-session` tool contract is
  tested with the metrics milestone, while user-facing closeout documentation remains last.
- **Overall review approval**: Owner approved the reviewed current specification, plan, tasks, and
  recorded analysis evidence for implementation handoff on 2026-09-29.

## Summary

Add a Pi 0.87.x extension that is the sole measured Jev boundary: it invokes `jev-cli` on an
explicit 2–50 candidate set, records privacy-safe invocation/proposal events in Pi session entries,
accepts one idempotent main-agent disposition per candidate-level proposal, and derives session and
per-skill metrics. `/jev-metrics` exposes active/history views, while `finish-session` explicitly
appends one aggregate row per session to an XDG local-state CSV. Activate four global skill seams and
four SpecKit seams only after the tracker exists; distribute SpecKit changes as a project-local
composable preset rather than patches to generated prompts. Jev-on installation is transactional and
fails when Jev, authentication, tracking, or requested SpecKit capability is unavailable. Default
installation keeps the current manual workflows.

## Technical Context

**Language/Version**: JavaScript ES2022 on Node.js 22 for extension/core/tests; POSIX shell and Python
3 only where the existing installer/verification scripts already use them; Markdown/YAML for skills
and SpecKit preset layers

**Primary Dependencies**: Pi coding agent 0.87.x extension API (`registerTool`, `registerCommand`,
`appendEntry`, session manager); `jev-cli` response contract tested at 0.6.3; project-local SpecKit
1.0.12 preset resolver for the four SpecKit overrides; Node standard library only for feature core

**Storage**: Versioned Pi custom entries on the active session branch; one RFC 4180 aggregate CSV at
`${XDG_STATE_HOME:-~/.local/state}/pi/jev-metrics/<project-fingerprint>.csv`

**Testing**: Node built-in `node:test` for pure modules and fake Pi/process adapters; deterministic
shell/Python installer fixtures; existing suite lint; SpecKit resolver/artifact introspection against
a temporary fixture project

**Target Platform**: Pi 0.87.x on local developer environments supported by the existing suite
installer; project-local SpecKit 1.0.12 when SpecKit seams are requested

**Project Type**: Global Pi configuration/skill suite with a JavaScript Pi extension and a
distributable project-local SpecKit preset

**Performance Goals**: No token, latency, or quality target is claimed and no benchmark is permitted.
Local aggregation and CSV operations remain deterministic and bounded by at most 50 candidates per
invocation and the active branch event count.

**Constraints**: Exactly eight approved seams; candidate-level proposals; no raw candidate text,
logs, prompts, credentials, personal data, or raw Jev response in telemetry/CSV; raw shell/MCP calls
remain explicitly untracked; no automatic consequential decision; no partial Jev-on activation; one
CSV row per Pi session; no direct edits to generated SpecKit prompts; no live benchmark

**Scale/Scope**: One extension, three model-callable tools, one user command, four global skill seams,
four SpecKit command layers, one `finish-session` closeout integration, and fixture-driven coverage
of counters/privacy/fallback/install behavior

## Constitution Check

*GATE: Passed before Phase 0 research. Re-checked after Phase 1 design and passed.*

| Principle / gate | Pre-research evidence | Post-design evidence | Result |
| --- | --- | --- | --- |
| I. Portable Global Assets | No project name, absolute target path, provider/model ID, or deployment state is embedded in the approach. | Contracts use Pi/XDG/project-root discovery and a project-installable SpecKit preset. | PASS |
| II. Evidence and Capability Gates | Planning prompt, setup/check scripts, template, constitution, Pi API docs, SpecKit 1.0.12, and Jev 0.6.3 contracts were inspected. | [installation.md](contracts/installation.md) fails Jev-on before activation and preserves manual fallback; current missing Jev auth is recorded, not bypassed. | PASS |
| III. Artifact-Led, Owner-Approved Delivery | `spec.md` records owner approval for planning and links the source epic. Settled decisions are retained. | Design traces tools, events, CSV, and all eight seams to FR-001–FR-015 without adding a benchmark or new seam. | PASS |
| IV. Durable Knowledge and Documentation Integrity | `memory/MEMORY.md` was read and has no gotchas. Existing documentation owners are not invented. | Metrics remain XDG state, not docs/memory; implementation docs update existing README/REQUIREMENTS/skill contracts only. | PASS |
| V. Verification Before Claims | The plan relies on inspected interfaces rather than an assumed extension or SpecKit mechanism. | Quickstart and contracts specify deterministic fail/pass evidence, privacy sentinels, resolver checks, fallback checks, and no live benchmark. | PASS |
| Operating constraints | Pi is 0.87.1; project-local SpecKit assets are installed; Jev is present but unauthenticated. | Jev remains optional in manual mode; Jev-on requires `auth test`; sensitive payload submission is prohibited. | PASS |
| Delivery/review workflow | Current approved spec is the input; this stage stops after planning. | Tasks, implementation, activation, benchmark, commit, push, and deployment remain outside this stage. | PASS |

No constitution exception or complexity violation is required.

## Project Structure

### Documentation (this feature)

```text
specs/001-jev-skill-metrics/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── installation.md
│   ├── pi-tools.md
│   ├── seams.md
│   ├── session-metrics.csv.md
│   └── telemetry.schema.json
└── tasks.md                       # Later /speckit.tasks output; not created now
```

### Source Code (repository root)

```text
extensions/
└── jev-metrics/
    ├── index.js                   # Pi adapter: tools, command, lifecycle
    ├── lib/
    │   ├── aggregate.js           # Event validation, dedupe, derived summaries
    │   ├── csv-store.js           # XDG path, lock, RFC 4180 append/read
    │   ├── events.js              # Schemas, IDs, privacy-safe event creation
    │   └── jev-client.js          # Spawn jev run -, normalize exits/response
    ├── fixtures/
    │   ├── events/
    │   ├── jev-responses/
    │   └── seams/
    └── test/
        ├── aggregate.test.js
        ├── csv-store.test.js
        ├── extension.test.js
        ├── jev-client.test.js
        └── privacy.test.js

configs/
└── speckit/
    └── presets/
        └── jev-seams/
            ├── preset.yml
            └── commands/
                ├── speckit.analyze.md
                ├── speckit.checklist.md
                ├── speckit.clarify.md
                └── speckit.tasks.md

skills/
├── scientific-method-debugging/SKILL.md
├── receiving-code-review/SKILL.md
├── coordinate-implementation/SKILL.md
├── track-open-issue/SKILL.md
└── finish-session/SKILL.md

scripts/
├── install.sh                     # Add explicit manual/Jev-on mode handling
├── install-jev-speckit.sh         # Project-local preset staging/reconciliation
└── tests/
    ├── test-install-jev.sh
    └── test-install-jev-speckit.sh

README.md                          # User-facing modes, metrics command, reload
REQUIREMENTS.md                    # Compatible Pi/Jev/SpecKit capability contract
```

**Structure Decision**: Keep executable tracking behavior in one repository-owned Pi extension with
pure, dependency-free core modules. Keep semantic seam instructions in their existing global skills.
Ship SpecKit changes from `configs/speckit/presets/jev-seams/` and install them into a target
project's preset registry through SpecKit's supported resolver. Do not place runtime state in this
repository or copy core SpecKit prompts into a maintained fork.

## Architecture

### Components and responsibilities

1. **Pi adapter (`extensions/jev-metrics/index.js`)**
   - Registers `jev_rank`, `jev_disposition`, `jev_metrics`, and `/jev-metrics`.
   - Obtains session/leaf identity from the current `ExtensionContext`.
   - Serializes event-producing calls and appends the owned custom-entry type.
   - Reconstructs from `getBranch()` on session start/tree changes.
   - Does not implement semantic ranking, counters, or CSV parsing itself.

2. **Jev client**
   - Validates the bounded request, writes an invocation-start event, and spawns `jev run -` with a
     JSON request on stdin.
   - Maps CLI absence/exit/abort/malformed response to stable terminal states.
   - Produces one candidate-level proposal for each valid answer and stable tie ordering.
   - Returns complete candidates to the caller through its normal workflow; telemetry receives only
     IDs, scores/ranks, status, and timestamps.

3. **Event/aggregate core**
   - Enforces [telemetry.schema.json](contracts/telemetry.schema.json), approved skill IDs, unique
     starts/terminals, proposal references, and first-valid-write dispositions.
   - Derives session and per-skill denominators from active-branch entries.
   - Reports orphaned/invalid/missing states explicitly rather than converting them to zero.

4. **CSV store**
   - Computes the XDG project partition, validates existing header/rows, locks, rechecks session-ID
     idempotency, and appends one aggregate row.
   - Never persists candidate bodies, criteria, stderr, raw responses, project paths, or credentials.
   - Leaves invalid history untouched and returns an explicit error.

5. **Global skill seams**
   - Construct bounded candidates and call only the instrumented tools when Jev-on is active.
   - Retain complete evidence, main-agent decisions, and every existing final check.
   - Use manual behavior when not Jev-on or when a tracked call produces no proposals.

6. **Project-local SpecKit preset**
   - Adds the four SpecKit seams through append composition.
   - Depends on, but does not copy or patch, the target's generated core prompts.
   - Is activated as a four-command unit only after resolver compatibility and tracker availability
     are proven.

7. **Installer/activation gate**
   - Stages and verifies all requested Jev-on capabilities before changing active resources.
   - Runs the fixed Jev authentication test only after explicit Jev-on selection.
   - Rolls back partial activation and reports actionable prerequisites.

### Data flow

```text
approved seam
  -> explicit candidates + criterion
  -> jev_rank
       -> append invocation_started (IDs/status metadata only)
       -> jev run - (candidate bodies sent to configured provider)
       -> validate complete response
       -> append invocation_terminal (+ proposal IDs/ranks/scores only)
  -> main agent reviews original evidence + advisory ranking
  -> jev_disposition per decided proposal
       -> append first valid proposal_disposition
  -> jev_metrics or /jev-metrics
       -> validate active branch -> derive totals/per-skill denominators
  -> finish-session -> jev_metrics(closeout)
       -> append one aggregate XDG CSV row
```

### Failure and fallback behavior

- Invalid/oversized input: no Jev launch; return schema error and manual fallback.
- Missing CLI/auth/provider, nonzero exit, cancellation, or malformed/partial response: count the
  started attempt, record no success/proposals, and return manual fallback.
- Duplicate terminal/disposition: deterministic no-op or invalid diagnostic; never inflate counts.
- Unknown/cross-session proposal: reject and report; never attribute it.
- Reload/resume/tree navigation: reconstruct active branch; abandoned branches do not count.
- Missing/unreadable/invalid CSV: display state explicitly; do not report historical zero.
- Jev-on preflight failure: no seam enabled. Manual install remains usable.

## Dependency and Delivery Sequence

This is architecture sequencing, not the task breakdown owned by `/speckit.tasks`.

1. **Schemas and pure aggregation first**: implement validated events, proposal/disposition
   invariants, and fixture arithmetic before any seam can activate.
2. **Jev process boundary second**: add fake-process fail/pass tests for every exit/response class;
   no live provider call belongs in verification.
3. **Pi adapter third**: register tools/command, serialize writes, and prove branch/reload behavior
   against a fake session manager.
4. **CSV closeout fourth**: prove privacy, lock/idempotency, store-state errors, and one-row session
   behavior before changing `finish-session`.
5. **Installer gate fifth**: prove manual mode, every Jev-on missing-prerequisite fixture, staged
   activation, and rollback before any optimized seam is considered enableable. Source seam changes
   may be prepared after the tracker is verified, but no Jev-on activation may expose them until this
   gate passes.
6. **Global seams sixth**: integrate the four skills individually against their source-named
   fixtures while preserving manual/final checks.
7. **SpecKit preset seventh**: compose and inspect all four commands in a temporary initialized
   project; activate all or none.
8. **Closeout/docs last**: complete user-facing README/requirements documentation, final acceptance,
   and no-benchmark inspection. The deterministic `finish-session` tool-contract integration belongs
   to the metrics milestone so its CSV behavior is tested before seam activation.

Parallel implementation is safe only among pure fixture authors whose files do not overlap. Event
schema/aggregation precede adapter/CSV; tracker precedes every seam, and the installer gate precedes
every Jev-on activation; each shared skill, installer, preset registry, and acceptance pass has one
writer at a time.

## Verification Strategy

### Fail-then-pass checks

- Begin with fixtures for one success/three proposals and two accepted/one overridden; assertions
  fail until event aggregation exists.
- Add replay/conflict/cross-session fixtures before disposition mutation.
- Add missing CLI, auth exit 3, retryable exit 4, malformed JSON, partial answers, cancellation, and
  oversized candidate fixtures before Jev client handling.
- Add resume/reload/tree-navigation fixtures before lifecycle reconstruction.
- Add missing, unreadable, corrupt, duplicate-session, and valid CSV fixtures before closeout.
- Add a forbidden-string sentinel to candidate/log/credential fixtures and assert it occurs in
  neither custom entries, metrics output, nor CSV.
- Add one source-named fixture per seam before modifying its skill/preset layer.
- Add Jev-on installer fixtures with missing auth/tracker/SpecKit before activation logic.

### Required checks after implementation

```text
node --test extensions/jev-metrics/test/*.test.js
scripts/tests/test-install-jev.sh
scripts/tests/test-install-jev-speckit.sh
scripts/check-skills-lint.sh
.specify/scripts/bash/check-prerequisites.sh --json --require-spec
specify preset resolve speckit.analyze
specify preset resolve speckit.checklist
specify preset resolve speckit.clarify
specify preset resolve speckit.tasks
specify artifact info speckit.analyze --json
specify artifact info speckit.checklist --json
specify artifact info speckit.clarify --json
specify artifact info speckit.tasks --json
```

The SpecKit commands run only against a disposable fixture project during implementation validation,
not by editing this checkout's generated prompts. Live `jev auth test` is an installation preflight,
not a deterministic test-suite command. No validation command runs an A/B benchmark or claims token,
latency, or quality improvement.

### Acceptance evidence

- SC-001/SC-002: exact fixture counter output and replay invariance.
- SC-003: eight seam fixtures showing bounded input, retained originals, and unchanged verification.
- SC-004: all missing-prerequisite Jev-on fixtures fail before activation; manual fixtures pass.
- SC-005: forbidden-string scan of session entries, metrics output, and CSV.
- SC-006: command log and artifact scan show no benchmark execution/performance claim.

## Security and Privacy

- The extension executes only the configured `jev` executable with an argument array; no shell
  interpolation.
- Request JSON travels on stdin, not command-line arguments or repository scratch files.
- Candidate data is sent to the configured provider only after the calling seam has excluded
  unauthorized sensitive content. The extension cannot make sensitive content safe by redaction
  inference.
- Telemetry uses allowlisted fields and stable reason codes; raw stderr/provider output is returned
  only as a bounded generic class and is never persisted.
- CSV excludes project path/fingerprint, candidate text, criteria, logs, prompts, credentials, raw
  responses, and endpoints.
- The XDG state directory is created user-private where supported. No credential file is read or
  copied by the extension; `jev-cli` owns authentication.
- High-impact, architecture, root-cause, code, authorization, and final-correctness decisions remain
  with the main agent regardless of rank/confidence.

## Migration, Compatibility, and Rollback

- Event entries and CSV rows start at schema version 1. Unknown future versions are reported, not
  guessed.
- No existing telemetry migration is required because this is the first tracked schema.
- Compatibility is gated to inspected Pi 0.87.x, `jev-cli` 0.6.3 response behavior, and SpecKit
  preset composition compatible with 1.0.12 until dedicated compatibility fixtures expand it.
- Rollback disables tracker/seam activation and reconciles SpecKit from remaining layers. It leaves
  session entries and CSV history intact. Destructive deletion requires separate authorization.
- Non-Jev-on installs remain the compatibility fallback and do not claim telemetry coverage.

## Documentation Scope

Implementation updates only established owners:

- `README.md`: install modes, `/jev-metrics`, privacy/coverage notice, and `/reload` requirement.
- `REQUIREMENTS.md`: Pi/Jev/SpecKit compatibility and missing behavior.
- The four global `SKILL.md` files: bounded seam and manual fallback.
- `skills/finish-session/SKILL.md`: deterministic closeout action and explicit store-error reporting.
- The project-local SpecKit preset command layers: their four bounded seam contracts.

No new documentation owner, routing guide, memory entry, benchmark report, changelog, or deployment
runbook is required. Metrics CSV remains state rather than documentation. The stale checklist note
that says CSV append depends on documentation routing does not govern the approved spec; the approved
spec explicitly requires closeout append even when routing is not initialized.

## Specialized Capability Requirements

- Pi extension implementation against the installed 0.87.x declarations and examples.
- Deterministic child-process protocol testing for `jev-cli` 0.6.3.
- SpecKit 1.0.12 preset composition/reconciliation and artifact introspection.
- Privacy review focused on allowlisted persisted fields and fixture sentinel leakage.
- Shell installer staging/rollback review.

No deployment, paid benchmark, database migration, MCP integration, or new provider selection is
required.

## Review Evidence

- **Main-agent task validation (2026-09-29)**: `tasks.md` has 35 sequential tasks with required
  metadata; `python3 skills/epics-manager/scripts/check-task-order.py
  specs/001-jev-skill-metrics/tasks.md` passed; 28 tasks are `sonnet-class` and 7 are `opus-class`
  (20%); documentation tasks and all eight source-named seam fixtures are present.
- **Delegated analysis (2026-09-29)**: The exact Sol task-agent context ran the installed
  `/speckit.analyze` stage after corrections. It found 100% requirement coverage, no unmapped tasks,
  no ambiguities, duplications, or constitution conflicts, and no remaining findings. Its prerequisite
  and task-structure checks passed; no analysis artifact was written because the installed stage is
  read-only.

## Open Decisions

None. The approved specification and owner-settled decisions determine the material architecture,
privacy boundary, persistence form, proposal unit, fallback, and SpecKit ownership mechanism. A
future benchmark/activation beyond local installation remains a separate owner authorization gate,
not a blocker for this plan.

