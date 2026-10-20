# Required monitor validation — revised proposal

All revised SC-001–006 in [spec](../spec.md) are required. This is an application acceptance contract,
not startup ceremony or a claim tests already exist/pass. [Tasks](../tasks.md) assign delivery owners.

## Focused required checks

| Criterion | Smallest meaningful checks | Pass evidence / delivery |
| --- | --- | --- |
| SC-001 inventory/identity | Production mapper fixtures from the retained script descriptor plus actual emitted occurrences; unvisited branches, repeats, non-task phases, unsupported records, typed edges, hidden history. Real browser selection/reveal. | Compare complete IDs/counts/edge kinds with source records; zero fabricated/inaccessible occurrences. T001–T006 descriptor/emission, T007–T010 core graph, T011–T015 history/lineage/liveness. |
| SC-002 review/fixes/history | Real engine/check/Git paths using clearly labelled offline model adapters for deterministic failures, questions, interruption, rejected review, separate linked fixing run and subsequent fresh review. Assert distinct model nodes, retained first failure and actual original base→new head in rereview prompt/record. Browser navigates that lineage. | Actual emitted DB rows/readback, separate adapter calls/roles, Git ranges/checkpoints, no automatic retry, failed original remains failed. Dangling/cyclic/wrong-worktree relation tests cannot confer acceptance. T001–T006 recording/range; T013–T014 composed viewer behavior. |
| SC-003 near-live | Actual isolated writer while reader/browser polls; measured record/read/display timing, selection/viewport preservation, forced read errors/stale responses and runner loss. Repeat live observation during own application build. | Timing pairs normally about2s, deviations retained without invented percentile; last-success/liveness/incomplete warnings correct. T010–T011 core polling; T015–T016 live/error/self-build proof. |
| SC-004 fidelity | Missing metadata, unknown times/metrics, zero exit/count, no-change checkpoint, requested-not-acknowledged model, absent checks, question requested/returned/sent/send failure, partial history and recorder unavailable/recovered. | Source→DTO assertions; no answer-consumed claim, invented review range, synthetic transition or private-text fallback. Recorder exceptions never prevent worker/check/Git/review or replace original error. T001–T006 producer, T008 mapping, T012–T015 composed edge cases. |
| SC-005 privacy/noninterference | Real concurrent script writer + production mode=ro reader/HTTP; SELECT boundary, authoritative rows unchanged by viewer, writer progresses. Browser malicious text, foreign Host/Origin/method/path and actual500/error-log cases; private sentinel scan across all outputs. | No viewer execution/control/SQL mutation, no raw summaries/errors/commands/findings/question/answer/transcript/paths. Normal SQLite sidecar bookkeeping is not authoritative mutation. T001–T006 recording minimization; T007–T010 baseline boundary; T013–T016 composed completion. |
| SC-006 integration/own build | Validate T001–T006 before a fresh run of T007–T016. At usable T010 checkpoint operator observes earlier records and genuine subsequent T011–T016 work of THAT SAME run. Additional actual isolated same-spec/completed/failed/linked-correction histories supplement. | Real run IDs, recording version, baseline/checkpoint/review ranges and safe observation times. Same-build live interval mandatory, never replaced by a fixture/demo. Final review outcome inspected after task completion. T016 plus final operator acceptance. |

Offline SDK fixtures test the actual script seams but are not live-provider success. Use actual approved
SDK execution for the application build; do not require separately charged provider traffic merely to
repeat deterministic cases. Never fabricate human approval or tool receipts. Missing required capability
or evidence is FAIL/NOT VERIFIED, not a passing skip or empty test collection. Ordinary project checks
retain their actual semantics; this adds no universal collection-count rule to the script.

## Proposed executable checks by outcome

[Human tasks](../tasks.md) and matching [JSON](../tasks.json) carry task-local REQUIRED T001/V1–T016/V1
mappings, exact owned paths, predecessors, source-read instructions, capabilities and focused ordinary
commands. Modules/scripts are future delivery targets, not existing passing tests.

- T001–T006 deliver permanent actual recorder/engine/check/Git/adapter/CLI tests; T006 additionally runs
  the runtime unittest discovery and Node host regression because foundation changes cross those seams.
- T007–T009 deliver reader/mapper/privacy/HTTP/launcher tests with prepared Python dependencies.
- T010–T014 include ordinary web build and installed-local-browser tests for their changed graph seam;
  T012/T013 additionally check actual history/lineage reader/HTTP composition.
- T015 checks actual concurrent record/read/display, degraded observations and browser recovery.
- T016 runs focused app discovery/build/browser checks for the shipped package and records actual SAME
  application-run retrospective/live operator observation. Final review occurs after its checkpoint.

Commands use prepared Python/Node/local browser only; no install/download, PythonAnswer/deadline workaround,
frozen dependency descriptor, source-copy/custody or environment attestation. Test subprocesses and normal
teardown stay with outcomes. Locks are conventional package locks, not an execution admission protocol.
Missing required capability/permission/evidence remains NOT VERIFIED. Optional broader regression is not
a blocker; real permission gates and SC criteria are unchanged.

## Privacy and optional-recording checks

Sentinels belong in synthetic private inputs, not actual private transcripts. Assert they do not enter
monitoring rows and do not escape through API/HTML/assets/headers/logs. Explicit reviewed presentation
may contain adversarial inert text but must not contain secrets. Raw existing progress details remain
private; tests must catch a future accidental forwarding fallback.

Inject recording errors at start/mid-run/end and question callbacks without disabling ordinary progress
storage. Actual execution still reaches its proper outcome; its original errors remain intact. Reader
shows unavailable/incomplete rather than reconstructing history. A hard-killed producer may leave no
terminal record or durable gap marker; absence remains unknown, not falsely certified complete.

Concurrent observation compares selected authoritative SQL rows at quiescent points and actual writer
progress, not byte equality of an actively changing database. Do not acquire writer authority, checkpoint,
repair sidecars or use immutable/nolock to make tests pass. Exact 500/250ms budgets are not acceptance.

## Same-build sequencing and final acceptance

1. Separately authorize, implement, validate and checkpoint T001–T006. Review the recording/range behavior;
   approve the fresh application run of T007–T016 and its actual existing tools/setup.
2. Start that application run without needing the viewer. At T010 checkpoint, build/serve production
   assets under separately explicit operator launch authority. Observer is independently owned and
   read-only, not a second coordinator or a task-owned daemon left behind.
3. Observe the same run's earlier T007–T010 events retrospectively and genuine T011–T016 activity live. Keep safe
   run/occurrence/time references in normal test/acceptance output, not proof receipts or private dumps.
4. T016 validates delivery but cannot require the future final reviewer to have finished. After the
   runner's fresh independent final review, operator inspects the recorded actual outcome/range.
5. If review finds defects, retain the rejection; obtain scope approval for a linked fixing run and
   original-range rereview. Actual fixing-agent and rereview nodes must appear. No automatic retries,
   inference from commit ancestry or substitution of a clean run.

If viewer launch or the same-run live interval is missed, SC-006 remains NOT VERIFIED. Seek an explicit
acceptance decision before any replacement demonstration; never silently waive it. No artificial tasks,
pauses or injected production failures solely to generate evidence. Isolated failures test retention;
any real build failures must also remain visible.

## Reporting and permission

Report each SC as PASS/FAIL/NOT VERIFIED with actual commands, relevant observed versions, run/range
references, failures and manual steps. Keep tests/docs with outcomes and ordinary teardown. Future
focused explicit-owned-path commits, real project checks, sole-writer lock, normal hooks/signing,
unrelated-work preservation and fresh independent final review remain required. No catalog, manifest,
cgroup, receipt, source-binding or repeated environment attestation gates.

Current session only revises artifacts. No implementation, dependency install, model/application launch,
activation, deployment, merge, push, private transcript access or global change is authorized.
