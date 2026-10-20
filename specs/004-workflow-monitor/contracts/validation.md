# Required monitor validation — revised proposal

All revised SC-001–006 in [spec](../spec.md) are required. This is an application acceptance contract,
not startup ceremony or a claim tests already exist/pass. [Tasks](../tasks.md) assign delivery owners.

## Focused required checks

| Criterion | Smallest meaningful checks | Pass evidence / delivery |
| --- | --- | --- |
| SC-001 inventory/identity | Production mapper fixtures from the retained script descriptor plus actual emitted occurrences; unvisited branches, repeats, non-task phases, unsupported records, typed edges, hidden history. Real browser selection/reveal. | Compare complete IDs/counts/edge kinds with source records; zero fabricated/inaccessible occurrences. T001 descriptor/emission, T002 core graph, T003 follow-up/history completion. |
| SC-002 review/fixes/history | Real engine/check/Git paths using clearly labelled offline model adapters for deterministic failures, questions, interruption, rejected review, separate linked fixing run and subsequent fresh review. Assert distinct model nodes, retained first failure and actual original base→new head in rereview prompt/record. Browser navigates that lineage. | Actual emitted DB rows/readback, separate adapter calls/roles, Git ranges/checkpoints, no automatic retry, failed original remains failed. Dangling/cyclic/wrong-worktree relation tests cannot confer acceptance. T001 recording/range; T003 composed viewer behavior. |
| SC-003 near-live | Actual isolated writer while reader/browser polls; measured record/read/display timing, selection/viewport preservation, forced read errors/stale responses and runner loss. Repeat live observation during own application build. | Timing pairs normally about2s, deviations retained without invented percentile; last-success/liveness/incomplete warnings correct. T002 core polling; T003 complete live/error/self-build proof. |
| SC-004 fidelity | Missing metadata, unknown times/metrics, zero exit/count, no-change checkpoint, requested-not-acknowledged model, absent checks, question requested/returned/sent/send failure, partial history and recorder unavailable/recovered. | Source→DTO assertions; no answer-consumed claim, invented review range, synthetic transition or private-text fallback. Recorder exceptions never prevent worker/check/Git/review or replace original error. T001 producer, T002 mapping, T003 composed edge cases. |
| SC-005 privacy/noninterference | Real concurrent script writer + production mode=ro reader/HTTP; SELECT boundary, authoritative rows unchanged by viewer, writer progresses. Browser malicious text, foreign Host/Origin/method/path and actual500/error-log cases; private sentinel scan across all outputs. | No viewer execution/control/SQL mutation, no raw summaries/errors/commands/findings/question/answer/transcript/paths. Normal SQLite sidecar bookkeeping is not authoritative mutation. T001 recording minimization; T002 baseline boundary; T003 composed adversarial completion. |
| SC-006 integration/own build | Validate T001 before a fresh run of T002/T003. At usable T002 checkpoint operator observes earlier records and genuine subsequent T003 work of THAT SAME run. Additional actual isolated same-spec/completed/failed/linked-correction histories supplement. | Real run IDs, recording version, baseline/checkpoint/review ranges and safe observation times. Same-build live interval mandatory, never replaced by a fixture/demo. Final review outcome inspected after task completion. T003 plus final operator acceptance. |

Offline SDK fixtures test the actual script seams but are not live-provider success. Use actual approved
SDK execution for the application build; do not require separately charged provider traffic merely to
repeat deterministic cases. Never fabricate human approval or tool receipts. Missing required capability
or evidence is FAIL/NOT VERIFIED, not a passing skip or empty test collection. Ordinary project checks
retain their actual semantics; this adds no universal collection-count rule to the script.

## Proposed executable checks by outcome

These ordinary commands are future delivery targets; helpers/packages do not exist yet. The implementer
must deliver the named tests/scripts before relying on them. No current application pass is claimed.

- **T001:** `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests <prepared-python> -B -m unittest discover -v -s runtime/tests`
  plus `node --test runtime/tests/test_host.mjs`. New monitoring tests belong in that discovered suite.
  Cover real per-check failure emission, worker/reviewer invocation boundaries, abandon retention,
  invalid review response, checkpoint failure/no-change, noninteractive question and optional recorder
  exceptions. Confirm default review range unchanged and explicit original-base range actually used.
- **T002:** `python -B -m unittest discover -v -s workflow_monitor/tests`; frontend `npm run build`
  and `npm test` (local browser script). Deliver reader/mapper/HTTP tests and baseline browser tests
  for one graph, real DOM edges, selection/polling, origin guards and safe output.
- **T003:** rerun those same focused app/build/browser checks with added composed lineage, privacy,
  stale/liveness and full-history cases; actual same-build observation is a manual acceptance step,
  not a fake automated return value. App docs specify exact prepared environment/commands at delivery.

No registered PythonAnswer, 15-second deadline, separate long-scenario workaround harness, frozen
external descriptor or source-copy/receipt reattestation. Ordinary test subprocesses, scratch/build
output and cleanup are allowed within future explicitly approved task scope. Dependencies use normal
manifests/locks; install/download/browser setup requires separate permission and is never a test side
effect. Recheck environment only when changed state invalidates relevant evidence.

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

1. Separately authorize, implement, validate and checkpoint T001. Review the recording/range behavior;
   approve the fresh application run of T002/T003 and its actual existing tools/setup.
2. Start that application run without needing the viewer. At T002 checkpoint, build/serve production
   assets under separately explicit operator launch authority. Observer is independently owned and
   read-only, not a second coordinator or a task-owned daemon left behind.
3. Observe the same run's earlier T002 events retrospectively and genuine T003 activity live. Keep safe
   run/occurrence/time references in normal test/acceptance output, not proof receipts or private dumps.
4. T003 validates delivery but cannot require the future final reviewer to have finished. After the
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
