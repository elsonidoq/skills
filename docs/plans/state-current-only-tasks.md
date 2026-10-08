# STATE current-only concurrent lifecycle — tasks

Direct TinySpec adapter; authoritative [source](state-current-only-tinyspec.md), A1–A6.
Source checkpoint: `7fc07816978c33cf4ca9ce94883d7e9e695a82e5`; factual source evidence
checkpoint: `9008b5cedd0e3008b3058d751b1e47049feb6ac8`.
Status: prepared for combined source/task review and exact-content owner approval;
**not implementation authorization**. Task preparation was explicitly authorized.
[Run evidence](../../memory/coordination/evidence/2026-10-08-state-current-only/SUMMARY.md)
records production validation/checkpoints; final approval identity belongs in its reviewed
handoff, not a self-hash in this mutable artifact.

## Shared context and execution gates

Read the source's settled semantics, scope, A1–A6 and limits before execution. Current
means genuinely active, paused, blocked or pending review/acceptance/owner gate. Verified
finished work is removed, not replaced with terminal status. Preserve unrelated concurrent
items and custom structure. Finished planning never automatically becomes implementation;
a genuinely active authorized successor is distinct. Durable artifacts remain with their
owners; STATE is neither history nor authorization.

Coordinator preflight must verify current source/task approval, capabilities, Git baseline,
index/worktree ownership and allowed paths before writes. Required capabilities: local
inspection/editing, Git with usable commit prerequisites, Python 3 and the existing fixtures;
no provider calls, SpecKit, Jev or installation required for this change. Use the existing
[checkpoint contract](../../skills/memory-handling/references/task-commit-contract.md) and
[coordination evidence contract](../../skills/memory-handling/references/project-coordination.md):
verified path-limited task commit, then a distinct evidence-only checkpoint in the same run
SUMMARY/index before later work/handoff. Missing capability, permission or REQUIRED evidence
is **NOT VERIFIED**, stopping affected acceptance. Do not weaken approved criteria.

No fixed global schema, tracker, persistence engine, runtime/settings changes, historical
migration, broad cleanup/audit, new framework, live provider exercise, guideline mutation,
push/deploy/install or external operation. Preserve all existing recovery, dispatch, ownership,
checkpoint and review gates. No planning-stage STATE writes. Authorized implementation/closeout
may apply the lifecycle only to understood verified current blocks, with exclusive ownership;
root STATE's completed previous run is motivation, not advance cleanup permission.

## Implementation task

- [ ] T001 Align the shared current-only lifecycle, closeout, focused fixture and active documentation
  - **Depends**: none
  - **Outcome / source**: source A1–A6 are implemented as one coherent independently verifiable unit: coordinator produces current-only truth, finish-session selectively removes verified finished items, and tests/docs reflect the same lifecycle. Coupled operational wording and its assertions stay in lockstep, not artificial separate tasks.
  - **Files / interfaces**: `skills/coordinate-implementation/SKILL.md` (Brief Current State and Recovery table, Writes and checkpoint ordering, Finish); `skills/finish-session/SKILL.md` (Core Invariant 7, Step 6); `skills/coordinate-implementation/scripts/test_state_contract.py`; `README.md` (Brief current state). Bounded inspect-only carrier inventory: `REQUIREMENTS.md`, `skills/initialize-coherence/SKILL.md`, `skills/finish-session-jev/SKILL.md`, `AGENTS.md`, `docs/index.md`, shared checkpoint/coordination references. Leave compatible references unchanged; any necessary clarification is limited to the approved lifecycle, not policy/guideline changes. Coordinator-owned project STATE application and run evidence are separate exclusive-boundary closeout outputs, never worker-owned paths.
  - **Required capabilities / context**: shared preflight above; existing local unittest, temporary-Git and symbolic scenario mechanisms. Re-read then-current carrier sections and state before deciding changes; do not adopt unknown dirtiness. No implementation model assignment. `residual_reasoning: low` — owner-settled semantics and bounded local contradictions; coupling requires carrier-level inspection, while behavioral obedience remains unproven.
  - **REQUIRED acceptance**:
    - **T001/V1 → A1**: coordinator producer/table/checkpoint/Finish and finish-session invariant/Step 6 remove verified finished attributable items rather than retain terminal disposition; active items still update in place. Check section-bound instruction assertions and targeted negative mutations for removed removal rules and restored terminal-retention instructions. Evidence: focused fixture PASS, named mutation rejection and bounded actual carrier diff inspection. Gate: approved source/tasks and owned paths before edits.
    - **T001/V2 → A2**: a genuinely finished planner spec disappears; source/tasks/evidence bytes remain unchanged and no synthetic implementation successor appears. Check a finished-spec symbolic closeout scenario in the existing fixture, including preservation of a distinct independently current successor. Evidence: scenario assertions for absent finished item, unchanged durable bytes and successor absence/preservation. Gate: applicable planning completion/approval evidence; symbolic results are not live obedience.
    - **T001/V3 → A3**: removing one finished item preserves unrelated concurrent items/custom structure byte-for-byte; paused, blocked, review/acceptance-pending items remain. Unknown runtime/ownership/completion, running child, partial work or ownership/drift cannot authorize deletion. Check mixed-current-item and gated/unknown retention/stop scenarios in the same fixture, retaining existing recovery and ownership guards. Evidence: preserved-byte comparisons and named retain/stop outcomes. Gate: verified runtime/ownership evidence or precise stop, never destructive inference.
    - **T001/V4 → A4**: when no current items remain, existing header/empty-current-content structure is valid, with no completed/idle-history placeholder; file/custom structure survives. Repeated closeout is byte-identical with no extra checkpoint. Check empty-state and repeated-closeout scenarios using existing symbolic/temporary-Git mechanisms. Evidence: exact bytes, unchanged commit count on repeat, absent terminal/history record. Gate: preserve existing format, no new schema.
    - **T001/V5 → A5**: active producer/consumer references have no removal contradiction; ordered recovery, child reconciliation/no duplicate dispatch, worker exclusion, immediate ID/deferred commit, safe boundaries/coalescing/unchanged skip, worker task/evidence checkpoints and independent review gates remain intact. Check the bounded carrier inventory against the actual changed behavior, changed local links/anchors, and both commands below. Evidence: PASS command outputs, brief inventory dispositions (changed/compatible), link results and actual diff review; historical records stay untouched. Gates: no broad audit/framework/live calls; final independent implementation review is still mandatory, fixture PASS alone cannot grant acceptance.
    - **T001/V6 → A6**: any actual STATE application is limited to understood attributable verified current items at authorized execution/closeout, preserving unrelated items/custom structure; no arbitrary history migration or invented authority. Coordinator checks before/after block bounds against approval/artifact/Git/checkpoint/runtime evidence and rechecks concurrent drift/ownership before writing/staging. Evidence: bounded attributable diff and inspected path-limited implementation/evidence commits, or explicit no-change disposition when application is unauthorized/unneeded. Gates: exclusive writer and dirty-overlap permission, verified completion and required acceptance; unknown runtime/ownership blocks deletion. This is a coordinator closeout gate, not delegated worker write scope.
  - **Checks / expected effort**: run `python3 -B skills/coordinate-implementation/scripts/test_state_contract.py`, then `python3 -B -m unittest discover -s skills/coordinate-implementation/scripts -p 'test_*_contract.py'`; inspect changed links/anchors and `git diff --check`. The small fixture covers V1–V4; the existing related contract suite and bounded diff/reference review cover V5 without a new framework. Record V1–V6 separately even when a shared check covers several. Existing 15-test baseline validates the old terminal-retention assertions, not this implementation. Optional broader regression only if a demonstrated changed dependency warrants it; no mandatory live test or exhaustive matrix.
  - **Integration / checkpoint / release**: inspect the actual coupled diff and all REQUIRED evidence, commit only owned implementation paths, then persist result SHA/item outcomes and limits in a separate evidence-only checkpoint. Coordinator audits checkpoints before accepting return. Final fresh independent implementation review examines the complete committed range and V1–V6, not self-certification; unresolved findings block acceptance and verified review fixes need separate focused task/evidence checkpoints. At authorized closeout reconcile only current attributable STATE work under V6; review-pending work remains current until resolved. Tell the owner to run `/reload` after global skill changes.

## Risk-reduction and planning validation

No isolated prototype: this instruction lifecycle has no difficult executable dependency core.
The non-isolatable risk is agent obedience; offline instruction/mutation and symbolic/Git
fixtures do not prove live behavior. External research is omitted because no dependency/API/
version decision is introduced. Producer → consumers → validation → cleanup: coordinator
lifecycle → finish-session and inherited initialization/Jev plus explanatory docs → retained
state fixture/related suite and independent diff review → no disposable proof cleanup.
All carriers consume the same lifecycle in T001; retain the production fixture and evidence.
Failures/disproof stop reliance, retain findings and return affected source/task contracts to
producing review/renewed approval, never blindly retry or weaken acceptance.

Production validation: run the existing task-order validator; inspect source A1–A6 to
T001/V1–V6 traceability, explicit dependencies, implicit carrier dependencies, stage feasibility,
checks/evidence/gates, exclusions and links. One task has no forward/story dependency; its
contract, fixture and documentation form the bounded integration seam. Result/checkpoint
identity is recorded in run evidence before combined artifact review/owner approval.
