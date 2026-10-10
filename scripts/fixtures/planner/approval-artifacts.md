# Synthetic approval artifacts

Trusted fixture, not a live plan or task list. Outcomes are independently authored
here and mapped by the supervisor inventory, never extracted from a tested brief.

## Specification scope

- Scope: preserve ordered imports and explicit error recovery.

## Derived Standard plan

- Stage intake: validate incoming batch headers.
- Stage parse: decode each bounded record.
- Stage normalize: canonicalize record identifiers.
- Stage validate: reject conflicting record versions.
- Stage persist: atomically retain accepted records.
- Stage recover: replay interrupted batches safely.
- Stage report: expose accepted and rejected counts.
- Stage document: describe import and recovery contracts.

## Separate tasks

- T001: add bounded header validation.
- T002: implement deterministic record decoding.
- T003: normalize identifiers without collisions.
- T004: reject conflicting versions explicitly.
- T005: persist accepted records atomically.
- T006: replay interrupted batches idempotently.
- T007: test import counts and recovery failures.
- T008: document observable import contracts.
