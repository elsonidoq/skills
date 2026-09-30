# Session Metrics CSV Contract

## Ownership and location

The file is local metrics state, not repository documentation and not project memory:

```text
${XDG_STATE_HOME:-~/.local/state}/pi/jev-metrics/<project-fingerprint>.csv
```

`project-fingerprint` is the lowercase hexadecimal SHA-256 digest of the canonical project root. It
partitions local state; it is not included in the file body. The implementation must not create or
modify a repository file merely to persist metrics.

## Header

The first row is exactly:

```csv
schema_version,closed_at,session_id,leaf_id,skill_ids,attempts,successes,proposals,accepted,overridden,not_used,pending,invalid_events,coverage
```

Rows use UTF-8, LF line endings, and RFC 4180 field quoting. The header is written only when creating
an empty store.

## Row rules

- One row per Pi `session_id`; a repeated closeout is an idempotent `already_exported` outcome.
- `skill_ids` is the sorted approved skill ID set joined with `|`.
- All counter fields are base-10 non-negative integers.
- `coverage` is exactly `instrumented-only`.
- `successes <= attempts`.
- `accepted + overridden + not_used + pending = proposals`.
- No field may contain candidate bodies, criteria, prompts, logs, raw Jev output, stderr, credentials,
  environment-variable values, personal data, user names, home paths, project paths, or provider
  endpoints.
- A row is built only from the active branch's validated event stream.

Example using synthetic identifiers:

```csv
1,2026-09-29T12:00:00.000Z,session-fixture-1,leaf-fixture-1,receiving-code-review,1,1,3,2,1,0,0,0,instrumented-only
```

## Mutation rules

1. Create the parent state directory with user-only permissions where the platform supports them.
2. Acquire the project-partition lock.
3. Re-read and validate the header and every existing row while holding the lock.
4. If `session_id` already exists, return `already_exported` without writing.
5. Append one fully rendered row using append semantics, flush it, then release the lock.
6. On lock, validation, create, append, or flush failure, return `store_error` and do not claim
   closeout success.

A corrupt header or row is not silently repaired or replaced. The retrieval and closeout paths report
`storeState: invalid`, preserving the file for manual inspection.

## Retrieval rules

- Missing file: `storeState: missing`, no historical-zero claim.
- Permission/read failure: `storeState: unreadable`, no historical-zero claim.
- Header/row/invariant failure: `storeState: invalid`, no historical-zero claim.
- Valid file with only a header: `storeState: available`, zero rows.
- Valid rows may be filtered or summed deterministically, but the UI must retain the
  `instrumented-only` coverage label.

## Migration and rollback

`schema_version` governs additive future migrations. Version 1 readers reject unsupported versions
as invalid rather than guessing. Rollback removes the Jev-on activation and extension; it does not
delete the CSV. Deletion or transformation of historical state requires separate explicit user
authorization.
