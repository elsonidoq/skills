# TinySpec: Coordinator batch approval and persistence cadence

Producer: `planner`; depth: TinySpec. Status: preparation authorized; implementation approval pending.

## Context and provenance

The owner reports that coordinate-implementation skips an approval table, routes all work to Sol/medium, and repeatedly writes state and coordination memory. The owner explicitly limits corrections to the coordinator: subagent behavior and per-task implementation/evidence commits remain unchanged. Conversation in pi session `01a11363-637b-70cf-9968-9f8d03265bf9` is the original request. The owner selected TinySpec and approved direct planning profile `openai-codex/gpt-6.1-sol:medium` through ask_user. Planning profile is not an implementation assignment.

Verified baseline: `skills/coordinate-implementation/SKILL.md` Build the Execution Graph requires a table but says “Do not ask for routine batching approval when the owner already approved implementation”; Select Execution Capability places assessment “Before each batch.” Brief Current State and Recovery permits broad “meaningful transitions.” The shared task-commit and coordination contracts require internal worker task/evidence checkpoints. The routing seed offers alternatives and independent family/effort rationales; it does not require universal Sol/medium implementation routing. Runtime obedience and the owner's reported runs are not independently verified here.

## Scope and constraints

Change coordinator-facing approval, routing presentation and persistence instructions, their existing focused tests, and necessary normative documentation. Clarify shared-owner references only where needed to distinguish coordinator boundaries from unchanged worker duties. No worker brief/return/commit behavior change, task checkpoint weakening, runtime/settings/dependency changes, live/paid probes, benchmark, learned-guideline edits, historical-record rewrites, deployment or push.

Associated gotcha store: `memory/MEMORY.md`, no entries. Coordination `GUIDELINES.md` contains no approved guidance. Dependency research: local existing contracts suffice; no new library/runtime API or version-sensitive integration is introduced, so new external research is unnecessary.

## Decisions and approach

D1 — Build and assess the entire batch plan before presenting it. Keep existing dependency order, batching eligibility, six-factor assessment and capability checks. Require one or two explanatory sentences describing each batch's outcome and principal work. Table rows include batch/task IDs, dependencies, mode, proposed exact binding/effort, and concise independent family/effort rationale; retain integration/verification pointers and status without duplicating full contracts.

D2 — Implementation authorization does not approve execution routing. Present the table, then ask_user for explicit approval of boundaries and exact profiles before implementation writes or dispatch. Cancelled/ambiguous/missing selection blocks work. Persist approval against the current plan in the existing tracker/evidence convention. Identical profiles are allowed when each batch is justified; do not force diversity or inherit a universal Sol/medium default. Copy approved settings unchanged into dispatch. Resume reuses verified unchanged approval; material boundary/profile changes require approval of affected rows. Routine progress does not reopen approval.

D3 — Replace open-ended coordinator refresh instructions with the exclusive schedule below. Reads, checks and tracker progress are not automatically repository persistence events. Within one safe boundary, coalesce summary/index/state changes into one evidence checkpoint; skip byte-identical writes. Preserve recoverability, ownership checks, pending coordinator dirtiness exclusions, safe Git boundaries and failures that stop affected work. Do not chase self-referential SHAs.

| Coordinator boundary | Snapshot | Coordination evidence |
| --- | --- | --- |
| Approved execution start / imminent dispatch | Establish current truth and checkpoint dispatch intent before launch; reuse a just-audited boundary for next dispatch intent | Record approval/plan pointers and baseline once, not full assessments copied from briefs |
| Returned child ID | Write the ID immediately; checkpoint at the next safe coordinator boundary, never racing an active writer | No extra summary/index write solely for ID capture |
| Batch terminal and audited (or verified local task boundary) | Update accepted progress and exact next safe action; include next dispatch intent when known | Add one bounded audit disposition, referencing worker checkpoints instead of reproducing their ledger |
| Genuine blocked pause / failed attempt needing repair or owner decision | Record blocker, active child if any and safe next action; checkpoint when safe | Record diagnosis/exception and any approval disposition; do not repeat unchanged blockers |
| Final independent review transition and terminal closeout | Record review dispatch intent/returned ID using the same safety rules; then terminal disposition | Record review findings/dispositions and reflection once at closeout; blocked-pause reflection remains permitted |
| Recovery reconciliation with materially changed current truth | Refresh reconciled truth once before continuation | Record only recovered missing facts/exception, not replayed history |

No coordinator state/memory writes for polling, waiting, routine tool calls or messages, passing individual checks, unchanged status, or healthy internal worker task progress. Local execution still performs existing implementer task/evidence commits; this does not authorize weakening those duties. Repair dispatch uses the imminent-dispatch boundary only after diagnosis and owner profile gates. Reflection does not occur at routine batch boundaries. Guideline mutation remains separately approved and out of scope.

D4 — Preserve original snapshot recovery: authorization/content comparison, Git/index/path ownership reconciliation, runtime inspection including unrecorded dispatches, no duplicate dispatch/unknown-status replacement, immediate ID capture, safe pause on persistence failures. No timers, compaction hooks or new persistence framework.

## Acceptance and validation

A1 — Entire table appears before execution approval and dispatch, with one/two-sentence descriptions and exact proposed binding/effort per batch. Existing test harness rejects omitted table/description/profile/approval gates and the old approval-bypass instruction.

A2 — Per-batch independent family/effort assessment precedes table approval; no default Sol/medium or silent settings override. Uniform justified routing and reuse of unchanged approved plans remain valid. Focused positive/negative fixtures cover unapproved profile change and stale versus valid resumed approval.

A3 — Coordinator writes are allowed only at D3 boundaries; polling, unchanged status and healthy worker progress cause zero coordinator persistence. Multiple events at one safe boundary coalesce. Existing bounded fixtures cover approved start, returned ID pending safe commit, audited batch with next intent, blocker, review/closeout, and recovery; no new engine or exhaustive matrix.

A4 — Worker task/evidence commit duties remain byte-equivalent in meaning; workers never acquire snapshot ownership. Shared clarification cannot weaken internal checkpoints or introduce per-task supervisor waits. Manual baseline-to-diff comparison and existing state/Git-backed tests verify preserved recovery and commit safety.

A5 — Normative runtime/coordination documentation agrees with coordinator behavior, local links resolve, and relevant existing tests pass. Static/manual/Git fixtures are labelled honestly: actual runtime obedience is NOT RUN unless separately authorized, not a required live acceptance condition. Fresh independent final implementation review remains required over the committed range.

Use Python 3 and existing batching/state/intake and coordination/task-commit checks at the lowest sufficient layer. Each separate task retains stable REQUIRED item mappings; optional broad/live checks cannot substitute for required evidence. Source and separate tasks receive planner review and combined approval before coordinator preflight. No standalone TinySpec approval is required.

## Risks and recovery

Instruction tests cannot prove agent obedience. The concrete regressions are approval bypass and coordinator persistence churn; bounded fixtures and semantic review target them. The returned-ID immediate write is deliberately retained despite reduced cadence because it protects restart safety. Shared files may contain mixed coordinator/worker policy; edits must be narrowly role-qualified. Conflicts or missing REQUIRED evidence stop, not a silent scope expansion.
