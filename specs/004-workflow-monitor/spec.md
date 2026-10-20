# Feature Specification: Read-only Workflow Monitor

**Status:** revised proposal; owner authorized artifact simplification in this session, not implementation.
**Branch:** `follow-attached-workflow-migration-instructions`

## Product intent and authority

A local operator selects runs from the viewed worktree, understands the script's workflow and
observed progress in one graph, inspects brief details, and observes live and retained history,
including failures. The website is private and read-only.

This revision follows the corrected parsimony brief and the owner's clarification: a reviewer
finding defects must be followed, when fixes actually execute, by a distinct fixing-agent node,
checks/checkpoint and a subsequent reviewer node. Showing that cycle is required; automatically
launching it is not. Historical approvals in `specification-approval.md`, `app-scope.md`'s Git
history and `overall-review.md` do not approve these revised bytes or future execution.

## User Scenarios & Testing

### Story 1 — Understand a selected run (P1)

Select a run on the left and explore one graph on the right, with brief details.

1. Same-spec runs and historical failures remain distinguishable by stable identity, safe labels,
   recorded times and outcomes. Only new recording-contract runs from this worktree are eligible.
2. The graph distinguishes the script's defined phases, declared task dependencies and observed
   execution occurrences. A gray possible branch is not a recorded execution.
3. Each model execution has its own node and role: worker, fixing worker or independent reviewer.
   Worker return, check success, checkpoint and final acceptance are separate milestones.
4. Run-level phases remain visible without fabricated task membership. Repeated occurrences are
   distinct; ordered observations do not by themselves prove a causal transition.

### Story 2 — Understand review, fixes and failures (P1)

1. A reviewer that finds defects remains a visible execution node with its actual reviewed range
   and outcome. A later fixing-agent execution is a separate node, never just a task-status update.
2. An explicitly linked correction run can be expanded inside the selected run's graph, including
   its worker, checks/checkpoint and rereview. Each node displays its source run. This is a bounded
   follow-up view, not an arbitrary merged graph or second primary task view.
3. The relation to the earlier review is declared explicitly, not inferred from matching task names,
   spec, Git ancestry or timestamps. Missing/wrong-worktree references are unresolved, not invented.
4. Earlier failed checks, failed executions, review findings and interruptions stay accessible after
   later success. Actual review ranges are shown; correction-only review is not full-range acceptance.
5. Questions distinguish requested, terminal answer returned and answer sent to the SDK host where
   recorded. Sending is not proof of model consumption. No question or answer text is exposed.

### Story 3 — Observe safely (P1)

1. Changes normally appear within about two seconds, preserving selected node, viewport and positions.
2. Failed reads retain the last sanitized view with last-success/read warnings. Read freshness, last
   recorded activity, stored state and observed runner liveness are distinct.
3. Private-data sentinels never appear in responses, errors, logs, links or assets. Stored text cannot
   execute. Viewer actions have no execution/control effects or authoritative SQL writes.
4. After recording is delivered separately, the viewer displays its own application build retrospectively
   and observes genuinely later work of that same build live. A different demo cannot substitute.

## Functional Requirements

- **FR-001 Local scope:** loopback-only, one canonical worktree chosen by the operator at startup.
  No cross-project scanning, remote/multiuser service, legacy conversion or pre-contract fallback.
- **FR-002 Selection:** left run list; one selected-run graph and detail panel. Only explicitly linked
  local correction/rereview history may extend that graph, with visible run attribution.
- **FR-003 Defined versus observed:** retain a versioned description of actual script phases and
  task declarations at run start. It describes code, not an executable YAML workflow or configurable
  engine. Keep definition, prerequisite, recorded sequence and declared follow-up edges distinguishable.
- **FR-004 Inventory:** every retained defined phase and recorded occurrence is discoverable, including
  run-level review/terminal stages, unvisited alternatives and unsupported records. No illustrative
  happy-path graph, invented visit or inferred execution edge.
- **FR-005 Executions:** distinct stable occurrence identity for every script-invoked worker/reviewer,
  including explicitly associated fixing workers and subsequent reviews. Do not claim access to internal
  SDK retries, tool repairs or model turns that the script does not record.
- **FR-006 History:** append-only milestones preserve starts, returns, outcomes, failures, interruptions,
  checks, checkpoints, review ranges and terminal results. Current-state rows are not historical events.
- **FR-007 Review/fix/rereview:** display actual reviewer → declared correction → fixing-agent execution
  → checks/checkpoint → subsequent review, including separately authorized runs. Preserve original
  findings/count and each reviewed base/head. Only an approving independent review covering the
  required original range at the current head establishes full-range acceptance. No automatic correction
  scheduler, retry loop, finding-disposition ledger or authorization by graph link.
- **FR-008 Status:** gray unstarted, blue recorded running with liveness qualification, green successful
  milestone, red confirmed failure, amber waiting/blocked with distinct labels; warnings for unknown,
  stale and incomplete evidence. Use text/icons too. Historical failures never turn green.
- **FR-009 Details:** understandable phase descriptions, very brief public-safe task summaries, execution
  role/identity, recorded times, check ordinal/exit status, validated Git references and review outcomes.
  No raw worker summaries, commands, exception text, findings, private paths or transcript links.
  Missing safe summaries use generic labels, not private description fallback.
- **FR-010 Questions:** record coarse terminal/host delivery milestones without content. No durable
  answer mailbox, accepted/queued/original-conversation recovery protocol or model-consumption claim.
- **FR-011 Freshness:** approximate two-second updates, stable navigation, explicit last successful
  observation and incomplete/liveness warnings. Lack of events is not evidence of a dead or live runner.
- **FR-012 Fidelity:** absent timestamps/metrics/identity observations remain unknown; observed zero is
  zero. Executor configuration is requested identity, not provider acknowledgement. Metrics collection
  and revision histories are not required in this iteration.
- **FR-013 Observer only:** viewer never schedules, starts, answers, pauses, cancels, resumes, repairs,
  abandons, checks, commits or launches models. No writable runtime imports or browser SQL.
- **FR-014 Minimal recording:** a small additive seam at existing script boundaries, retaining run
  description and ordered observations in the existing database. Recording failure warns but cannot
  become an execution gate; missing history cannot be reconstructed from private transcripts or prose.
- **FR-015 Privacy:** minimize before exposure, render inert text, protect loopback/origin boundaries,
  parameterize read-only SQL, and close short snapshots before responding. Protect real ownership and
  authorization; do not restore retired admission machinery.
- **FR-016 Validation:** deterministic mapping/privacy fixtures plus real isolated script execution/readback
  and browser checks. Clearly label offline adapters; they do not prove live-provider success. Real check
  failures are failures; missing required evidence is NOT VERIFIED, never a passing skip.
- **FR-017 Own build:** validate recording before starting the application build. The usable graph must
  precede genuine later application work in that same run. Retain actual failures; do not inject production
  faults or busywork to manufacture evidence. Final independent review remains outside task completion.

## Key Entities

Worktree; run; retained script-phase description; declared task; execution occurrence; append-only
observation; declared review-follow-up relation; reviewed Git range; minimized observer snapshot.
These have distinct identities. No retired graph operation, receipt or saver identity is assumed.

## Success Criteria

- **SC-001 Coverage:** complete phase/occurrence inventory in one graph, correct identities and typed
  edges; no invented execution order from prerequisites; every hidden record revealable.
- **SC-002 Review and history:** actual isolated failure/check/interruption/question/review cases retain
  their milestones. A review finding, distinct fixing-agent execution and subsequent independent review
  are navigable together with correct run/range attribution. Earlier failure remains visible after success;
  invalid/missing follow-up references cannot establish recovery or acceptance.
- **SC-003 Live honesty:** demonstrate normal about-two-second updates during real isolated script work
  and own-build observation; retain deviations without inventing a percentile. Forced failed/stale reads
  and runner loss warn; navigation remains stable.
- **SC-004 Evidence fidelity:** unknowns, zeros, requested executor identity, no-change checkpoints,
  question send-versus-consumption and incomplete history are represented without fabricated facts.
- **SC-005 Safety:** zero viewer execution/control effects or authoritative mutations; writer progresses;
  adversarial stored text cannot execute; sensitive sentinels occur in no viewer-accessible output.
- **SC-006 Integration/self-history:** recording emission/readback is tested through actual script paths;
  the viewer loads its own application build retrospectively and observes later work in that same run.
  Additional actual isolated completed/failed/same-spec/linked-correction runs supplement, not substitute.

All six criteria remain required under these explicit revised meanings. No implementation acceptance
is claimed. Ordinary focused checks and independent final review remain required for future delivery.

## Acceptance reconciliation

| Old assumption/criterion | Revised treatment and basis |
| --- | --- |
| Pinned executable 19-node YAML, graph-op visits, trace-hash proof | Retained descriptive script phases and actual boundary observations; the script no longer executes that YAML. |
| Failure→automatic repair/reconciliation, original-conversation resumption | Preserve actual failures and explicitly linked, separately authorized fixing executions; no automatic cycle is provided. |
| Review→correction→rereview | **Preserved**, including distinct model nodes. Actual range coverage is explicit, not inferred from a later task/run success. |
| Accepted/queued/delivered/continued mailbox states | Replace with real terminal-answer/host-send observations; consumption is unknown. |
| Metric revisions/four binding classes | Not collected; unknown rather than invented. Requested executor config may be shown as requested only. |
| Same-build retrospective/live observation | **Preserved**; recording must precede the application build, with an early usable viewer. |
| No runtime changes in app tasks | Separate recording foundation before the app run; no runtime edits during that app build. |
| Catalogs/manifests/custody/receipt admission and tool/wire ceilings | Removed per current operative instructions; real permissions, writer ownership and project checks remain. |

## Assumptions and remaining authority

Current sources are `store.py`, `engine.py`, `verification.py`, `pi_adapter.py`, `cli.py`, and the
runtime operating/schema guides, not historical proposals. Existing rows do not provide this contract.
Only new recording-contract runs are in scope. No historical adapters or mass conversions.

Owner-selected future executor remains `openai-codex/gpt-6.1-sol`, effort `medium`; no substitution,
install, activation, launch, merge or push is authorized. Current session authorizes preparing these
revised artifacts. Current-content review and explicit implementation approval, especially for the
recording seam and bounded correction-review range support, remain necessary before execution.
