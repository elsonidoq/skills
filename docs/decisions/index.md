# Project decision index

This is the canonical ADR store for this repository, selected by the owner through
`ask_user` on 2026-10-21 during bounded `initialize-coherence` documentation setup.
See [documentation routing](../index.md#documentation-routing-guide) and
[Save ADR](../../skills/save-adr/SKILL.md).

Read this whole index before affected planning, implementation or review; then read
applicable accepted records and their supersession links. Accepted decisions constrain
outcomes; they do not authorize implementation or prove it complete. Proposed decisions
are not binding. Preserve superseded decisions and their rationale.

Records use `ADR-NNNN-short-title.md`, increasing identifiers (do not renumber or reuse removed IDs), and sections for status,
decision, context/rationale, consequences, provenance and supersession. Map every direct
record here with its status and a short purpose. Do not duplicate specifications or
Git-owned completion inventories.

- [ADR-0003: Current launch authority and authorization-neutral tasks](ADR-0003-current-launch-authority-and-neutral-tasks.md) — **accepted** owner direction; historical planning-only wording does not block owner-authorized task execution; final planning review keeps task instructions neutral.
- [ADR-0004: Shared routine worker permissions without repeated approval](ADR-0004-shared-routine-worker-permissions.md) — **accepted** owner direction; small isolated tests/databases and ordinary scoped fixes use shared defaults, with resource, data and external-action boundaries preserved.
