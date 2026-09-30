# Pi Tool and Command Contracts

## `jev_rank`

Model-callable, instrumented Jev interface. The tool is advisory and never applies a decision.

### Input

```json
{
  "skillId": "receiving-code-review",
  "criterion": "Rank comments by investigation priority; ambiguity and impact increase priority.",
  "candidates": [
    {"candidateId": "review-001", "body": "Synthetic candidate text"},
    {"candidateId": "review-002", "body": "Another synthetic candidate"}
  ]
}
```

Rules:

- `skillId` is one of the eight approved IDs in `data-model.md`.
- `criterion` is non-empty and bounded in length; it must define ranking semantics but cannot grant
  Jev authority to decide architecture, root cause, code, correctness, authorization, or verification.
- `candidates` contains 2–50 entries with unique opaque candidate IDs.
- The caller retains the complete original set outside telemetry. The extension passes candidate
  bodies to the selected Jev provider for this call but never copies them into telemetry, metrics, or
  CSV. Callers must exclude unauthorized secrets, credentials, personal data, and sensitive payloads.

### Success result

```json
{
  "tracked": true,
  "invocationId": "uuid",
  "status": "succeeded",
  "proposals": [
    {
      "proposalId": "uuid:proposal:review-001",
      "candidateId": "review-001",
      "rank": 1,
      "score": 3.5,
      "confidence": 0.91
    }
  ],
  "coverage": "instrumented-only",
  "requiredNextAction": "Record one disposition for each proposal after main-agent review."
}
```

Every input candidate appears once. Equal scores retain input order. `confidence` is optional and
advisory; no score or confidence automatically accepts or suppresses a candidate.

### Failure result

```json
{
  "tracked": true,
  "invocationId": "uuid",
  "status": "unavailable",
  "failureClass": "auth",
  "proposals": [],
  "fallback": "Use the complete original candidate set manually.",
  "coverage": "instrumented-only"
}
```

`unavailable`, `failed`, and `malformed` count as attempts but not successes and return no usable
proposals. Failure text, raw stderr, and raw responses are not persisted. The skill must continue its
manual path when installation mode permits fallback.

## `jev_disposition`

Model-callable explicit outcome for one proposal.

### Input

```json
{
  "proposalId": "uuid:proposal:review-001",
  "disposition": "accepted"
}
```

### Result

```json
{
  "recorded": true,
  "idempotentReplay": false,
  "proposalId": "uuid:proposal:review-001",
  "disposition": "accepted"
}
```

Semantics:

- `accepted`: main agent used the proposed position/group.
- `overridden`: main agent intentionally used a conflicting position/group.
- `not_used`: main agent reviewed but did not use this proposal.
- Same-proposal/same-disposition replay returns `recorded: true` and
  `idempotentReplay: true` without appending or incrementing.
- Unknown, cross-session, or conflicting second dispositions return `recorded: false`, a stable
  reason code, and do not change proposal counters.

## `jev_metrics`

Model-callable deterministic metrics operation. It never invokes Jev.

### Input

```json
{"action": "current"}
```

Allowed actions:

- `current`: return active-branch session totals and per-skill totals.
- `history`: return parsed cross-session rows for the current project partition, or explicit store
  state.
- `closeout`: append the current session aggregate exactly once. Reserved for `finish-session`.

### Current result

```json
{
  "sessionId": "pi-session-id",
  "leafId": "active-leaf-id",
  "coverage": "instrumented-only",
  "coverageNotice": "Only jev_rank calls are tracked; raw shell and MCP calls are untracked.",
  "total": {
    "attempts": 1,
    "successes": 1,
    "proposals": 3,
    "accepted": 2,
    "overridden": 1,
    "notUsed": 0,
    "pending": 0,
    "invalidEvents": 0
  },
  "bySkill": []
}
```

A missing or invalid history store returns `storeState: missing|unreadable|invalid`; it must not
return empty rows with `storeState: available` or imply a historical zero.

### Closeout result

The result reports `appended`, `already_exported`, or `store_error`, the session ID, and aggregate
counters. `finish-session` may report closeout complete only for `appended` or `already_exported`.

## `/jev-metrics`

User-facing Pi command:

- `/jev-metrics` renders the same current result as `jev_metrics(action=current)`.
- `/jev-metrics history` renders validated closeout rows and store state.
- `/jev-metrics help` explains counters, denominators, privacy boundary, and that raw shell/MCP Jev
  calls are untracked.

The command works in TUI, RPC, JSON, and print modes without relying on a custom terminal-only UI.
Human-readable output always includes:

- attempts and successes (`successes / attempts`),
- accepted, overridden, not used, and pending (`each / proposals`),
- total and per-skill rows,
- active session ID,
- `instrumented-only` coverage notice, and
- explicit missing/invalid state where applicable.

## Concurrency and lifecycle

- Event-producing operations are serialized within the extension runtime.
- `session_start` and `session_tree` reconstruct from the active branch.
- Reload, resume, new-session, fork, and shutdown cleanup are idempotent.
- Cancellation after an invocation start records a non-success terminal result when possible; an
  orphaned start is still counted as an attempt and displayed as incomplete/failed, never success.
- CSV mutation uses a separate filesystem lock and rechecks session-id idempotency while holding it.
