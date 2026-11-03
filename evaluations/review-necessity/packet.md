# Review packet

## Review scope

Review the planning specification and task below, not an implementation. This packet contains all material required for this review. No repository files, code diff or implementation tests are in scope. Report supported planning defects or explain why none qualify.

## Owner outcome

Prepare an isolated experimental index, preserving stable identities, complete source payloads and old interfaces. No production compute or serving storage may be used. Reuse existing input and indexing machinery; adapt only necessary seams.

## Source

The named frozen CSV lacks some native payload fields. Retained exact-identity payload material may also exist; its availability and completeness are unverified. Join required missing fields to retained capture or a bounded read-only canonical source. Never fabricate fields, overwrite frozen fields or weaken provenance checks. The assembled payload must be complete before indexing. Verify selected experimental targets against actual production bindings before mutation; unknown isolation blocks mutation, not safe synthetic software work.

## Task T001

Deliver the import-safe input adapter with permanent synthetic helper tests; consume the frozen CSV plus an explicitly bound exact-identity supplement. Parent must supply a verified full same-identity supplement before real indexing. Preserve checksums, identity joins, field types and provenance; keep old interfaces unchanged.

## Parent review context

CSV is incomplete native payload; exact-identity supplement needed. Review the source and task for supported material findings, including unnecessary work. Findings need location, consequence and smallest sufficient correction. Zero is valid.
