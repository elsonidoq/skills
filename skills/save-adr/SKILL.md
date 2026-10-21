---
name: save-adr
description: Use when recording a significant architectural decision, consulting accepted decision constraints before affected planning or changes, or propagating those constraints into a work brief or review.
---

# Save ADR

Preserve significant architectural choices and their rationale without inventing a decision store, approval, or implementation authority. This skill owns the save/consult/propagate contract; project routing chooses the record owner and format.

## Decide whether an ADR fits

Use an ADR for a significant choice about system structure, interfaces, dependencies, construction techniques, or security/reliability/performance/cost trade-offs when losing its rationale could cause expensive rework, incompatible changes or repeated substantial debate. An important owner instruction alone is not enough.

Route ordinary feature/UI requirements to their specification; supported behavior and mandatory procedures or permission rules to maintained documentation/instructions; scoped observations and lessons to project memory or evidence; unfinished work to its task or handoff. Use the project's existing owners rather than creating parallel stores. Required rules must be available in reliably loaded instructions, not only an ADR or memory.

Record actual alternatives considered and why they were rejected when known; never invent an evaluation retrospectively. Keep the historical reasoning in the ADR and link to current operational guidance rather than copying changing requirements. Do not require an ADR, documentation and memory entry for every task.

## Discover and save

Read the selected project's instructions, routing guide, and decision conventions. Reuse its actual decision owner, index, identifiers, and equivalent record format; do not assume a directory, filename, global store, or template.

- If an existing owner/index is readable, use it. On a repeat save, update or reuse that record rather than create a competing one.
- If ownership, location, format, write authority, or a material conflict is absent or ambiguous, stop only the affected save or decision-dependent operation. Name the problem and ask the owner to choose or confirm the owner/location/format or authority needed. Do not create a store merely because one is absent. Absent storage alone does not block unrelated legacy work.
- Before writing, follow applicable project safe-path/symlink, sensitive-data, dirty-target/concurrency, and focused [task checkpoint](../memory-handling/references/task-commit-contract.md) rules. Update a discovered index only with actual write authority.

Preserve the project's equivalent format while recording: the decision; context/rationale; consequences and trade-offs; decision status (`proposed`, `accepted`, or `superseded`); approval/source provenance (including unknown or pending authority); and applicable `supersedes`/`superseded-by` links. Do not label a decision accepted or a supersession approved when authority is unknown; record it as proposed with that provenance. Keep implementation state separate: an accepted decision may be unimplemented, and an implemented experiment is not thereby accepted. Saving, drafting, or proposing a decision never grants implementation permission.

An approved supersession creates or preserves a navigable newer record and status/link updates while retaining the older decision and rationale. A proposed supersession may link its proposal but does not supersede the older record. Never silently rewrite history, backfill records, or copy a specification into a competing record. Changing an accepted decision requires approved supersession through the project's existing authority; a proposed supersession is not approval. Explicit owner-authorized removal of a misclassified record is classification cleanup, not supersession: repair references and preserve any still-applicable requirements in their authoritative home. Ask only when decision meaning, authority, conflict, or location is materially unclear.

## Consult and propagate

Before planning or changing work that may affect accepted decisions, read the whole discovered decision index, then each relevant accepted record in full and any needed supersession links. The index maps records; it is not approval proof. Re-establish this applicability in fresh or resumed contexts rather than relying on an earlier-read claim.

Carry each applicable accepted outcome and its source link once into the relevant source/task acceptance, worker brief, or review scope. Do not duplicate this contract in consumers. Proposed records are not binding; superseded records retain history but are not current policy. Contradictory accepted records or uncertain current authority stop only the affected conflicting continuation and require an owner decision.

Accepted decisions protect accepted outcomes, not every incidental mechanism. Compatible helper/mechanism cleanup that preserves the outcome needs no new gate. An explicitly accepted mechanism remains binding until approved supersession. Review actual changes against those applicable outcomes and links; decision records complement rather than replace specifications, current operational documentation, or existing execution authority.
