# Project coordination guidelines

## Workflow parent wakeups

When changing this repository's workflow bridge or notification behavior, preserve the
owner's explicit direction: routine task transitions/completions and steering-status
updates must not wake the parent agent or request acknowledgment. Only an agent question
or terminal workflow completion (success or error) triggers a parent turn. Keep routine
updates observable without triggering turns, and preserve regression coverage for this
boundary. See the [runtime operating contract](../../docs/coordinate-implementation.md).

Provenance: owner explicitly requested disabling per-task wakeups and, during
`finish-session`, directed that they not be reintroduced in future changes.
