# Ephemeral recovery state — TinySpec

Producer: planner; owner-selected TinySpec. Preparation authorized in this conversation;
implementation requires combined source/task approval recorded in linked run evidence.

## Outcome and provenance

Owner: bookkeeping must be lightweight; STATE exists only to recover gracefully after
auto-compaction, giving the big picture and enough pointers to reconstruct details from
project files. Owner accepted recovery-bookmark semantics and explicitly required small,
ephemeral current content removed when its task finishes. This source preserves the
conversation-only request. [Run evidence](https://github.com/elsonidoq/skills/blob/5088b25877467887dd41c9547197c6da43b3c165/memory/coordination/evidence/2026-10-08-ephemeral-recovery-state/SUMMARY.md)
owns approval identities and execution evidence.

## Scope and settled decisions

Replace checkpoint-driven STATE persistence with recovery-driven bookmarking. Canonical
owner remains [coordinator](../../skills/coordinate-implementation/SKILL.md#brief-current-state-and-recovery).
Align finish-session, shared task-commit/coordination references and active documentation
(including repository instructions/constitution if necessary). Preserve global portability,
custom/unrelated concurrent state, approval authority, implementation verification/commits,
worker evidence checkpoints, inspected-failure repair and independent final review.
No new runtime component, compaction hook, schema, tracker, dependency, installation,
historical migration, learned-guideline mutation, push or deployment. Do not rewrite old
planning/evidence records to pretend the new protocol governed historical work.

Repository-derived evidence: coordinator currently requires dispatch-intent checkpoints,
latest SHA in state, audit/local-task updates and recovery refresh; shared task-commit and
coordination references repeat these requirements. Existing state fixture encodes them.
These contradictions must be changed together, not merely supplemented with lighter prose.
No external dependency/API decision: local contract inspection is sufficient; external
research omitted. Project memory has no gotchas or approved coordination guidelines.

## Approach

- One understood current block per ongoing workstream, roughly five short bullets: goal,
  authoritative source/tasks/approval links, active execution/run identity, next safe action,
  and material blocker if any. Example shape, not mandatory schema or invented fields.
  Omit routine Git SHAs, check outputs, completed-task history and duplicate evidence.
- Write at authorized start, returned child ID, materially changed next safe action or
  completion. A task/batch/check/commit/poll alone never triggers an update. Broad accurate
  next actions can span batches. Skip unchanged writes; coalesce available facts.
- No committed dispatch-intent prerequisite and no state-specific commit/evidence cycle.
  State may remain coordinator-owned working-tree dirtiness until the next safe otherwise-
  required commit, or across a state-only closeout without an invented commit. Explicitly
  exempt ephemeral state-only edits from retained-task checkpoint requirements. Preserve
  owned-path staging and avoid active-writer/index races; workers never own state writes.
- Recovery reads the bookmark once, then selectively opens linked authoritative files and
  inspects Git/runtime enough to choose the next safe action. Validate current permission
  before writes/dispatch and verification before acceptance, but do not mandate replay of
  all history/approvals/checks on every recovery. Missing/ambiguous state or child ID requires
  runtime reconciliation before replacement; running/unknown children cannot be duplicated.
  Repair still needs inspected failure. State is navigation, not authority or acceptance.
- Remove a verified finished task/workstream entry, leaving only genuinely ongoing items
  and unresolved gates. Preserve headers/custom content/unrelated concurrent work. Empty
  current content is valid; never retain terminal placeholders. Unknown completion, ownership,
  active child or unresolved acceptance prevents deletion.
- Coordination records audited outcomes and meaningful exceptions at existing evidence
  boundaries, referencing worker evidence. No summary/index edit merely because state changes,
  no duplicate routine event ledger. Required implementation-task/evidence commits remain.

## Acceptance

A1. Canonical contract explicitly treats STATE as small ephemeral recovery-only navigation;
its example needs no SHA/log ledger; finished attributable entries disappear without erasing
other active/gated items or durable files, and repeat empty closeout makes no extra write.

A2. Update rules prohibit routine task/batch/check/commit/poll-driven changes and permit only
start, returned identity, material next-action change and completion. No dispatch-intent
commit prerequisite, audit refresh mandate or unconditional recovery refresh survives.

A3. Shared checkpoint rules explicitly allow pending owned state and state-only closeout
without separate commits/evidence writes. Task/evidence checkpoints, ownership/drift checks,
worker exclusion and Git/index race prevention remain intact. No competing consumer rule.

A4. Recovery uses selective reads and retains approval/acceptance safety, Git ownership,
active/unknown/missing-ID runtime reconciliation and inspected-failure gates. No guessed
completion, blind redispatch or permission inferred from STATE.

A5. Focused instruction/mutation and existing symbolic/Git checks detect reinstated heavyweight
rules and lost recovery/lifecycle safeguards. Active docs and discovery agree with the
implementation. Existing affected state, task-commit and coordination checks pass; independently
review the actual diff. Static examples are not runtime-obedience proof.

A6. A bounded fresh-context read-only native-agent exercise, supplied only a compact bookmark
and file links in disposable local scratch, reconstructs goal, authority, pending work and
next safe action from project files, recognizes an unknown/active-child safety gate, and
requires no history ledger or state rewrite. Retain compact prompt/result observations and
limitations in run evidence. This is live reconstruction evidence, not actual auto-compaction
or long-running cadence proof. Missing capability/result blocks this item, never implies PASS.

## Risk reduction and sequencing

No isolatable dependency core warrants a prototype: the risk is instruction consistency and
agent recovery behavior. Change coupled owner/consumers/fixtures together; validate static
contracts, then fresh-context reconstruction, then independent review before acceptance.
Use existing fixture mechanisms and native delegation, not a new harness. Scratch proof
materials remain until review consumes their results; preserve findings in run evidence,
then discard only attributable scratch if needed. Disproof blocks reliance and returns affected
source/tasks to planner review/renewal; do not weaken acceptance or relaunch on unknown failure.
Actual automatic compaction and sustained obedience remain unverified beyond this bounded test.
