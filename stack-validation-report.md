# Stack validation report — candidate A PASS (parent acceptance pending)

**Executed:** 2026-10-18 UTC. **Scope:** one bounded fresh-context candidate A validation;
no planner read/invocation, migration implementation/planning, B/C build, or coding delegation.
The parent alone may accept this PASS and authorize its next phase.

| Ordered candidate | Result |
|---|---|
| A — Python LangGraph + SQLite checkpointer + Pi RPC + YAML adapter | **PASS**, executed demonstrations 1–8 below; prototype limitations explicit |
| B — Temporal | **NOT RUN** |
| C — Prefect 3 | **NOT RUN** |

## Identity, ownership and prerequisites

Fresh coding worker's actual environment `PI_SESSION_ID`:
`01a14fd4-b163-705e-bac3-a12947a304b7` (see [environment](docs/evidence/workflow-stack-validation/environment.json)).
This is distinct from the real Pi worker session used by the harness. No additional coding
subagents were launched. Real Pi RPC nodes are explicitly authorized harness workers.

Outer baseline: `18e400d2613cd8341d5d4cc73014e6bd0a2f1af8`; initial tracked index/worktree clean,
rechecked before retained writes. Owned retained paths only: this report and
`docs/evidence/workflow-stack-validation/**`. Result SHA is the focused commit containing
these paths, recorded exactly in the worker return artifact (avoids a self-referential SHA).
STATE, production skills, global settings, installed code, credentials and identity untouched.
Runtime/session/cache/temp/toy repositories stayed under ignored `.pi/workflow-validation/`.
Memory discovery: `memory/MEMORY.md` read fully; no gotcha entries, no memory writes.

Actual runtime: Python **3.12.3**, Git **2.43.0**, Pi **0.87.1**; parent's verified extension
prerequisites pi-subagents **0.73.1**, pi-ask-user **0.15.1**. Neither extension is needed in
the runtime worker: discovery disabled and `ask_user` never invoked. Installed into existing
isolated worktree venv using `pip --no-cache-dir`: LangGraph **1.2.16**,
langgraph-checkpoint-sqlite **3.1.2**, PyYAML **6.0.3**, jsonschema **4.26.0**.
`pip check`: **No broken requirements found**. No daemon/server or orchestration LLM.

## Acceptance matrix — identical required demonstrations 1–8

Paths below are relative to `docs/evidence/workflow-stack-validation/`.
The principal executed command was:

```sh
POC_ROOT="$PWD/.pi/workflow-validation/candidate-a/run4" \
  .pi/workflow-validation/venv/bin/python docs/evidence/workflow-stack-validation/test_harness.py
```

| # | Result / executed assertion | Command/test and inspectable evidence |
|---|---|---|
| 1 YAML graph | PASS. JSON Schema plus reference/handler/transition validation; two code nodes and implement/repair agent definitions. YAML-only alternate profile alias, instruction skill B, and success→END bypass checks/commit without engine edits. Unknown handler rejected. | `test_01_configuration_and_cutoff`; `workflow.yaml`, `schema.json`, executed `variant.yaml`; `logs/suite.log`. Variant is synthetic, same verified concrete model via another alias, not a claim of a real different-model test. |
| 2 Real Pi | PASS. Real write-tool tasks create then update toy.txt in `story-1`; same **observed** session ID; requested/observed `openai-codex/gpt-6.1-sol`, **medium**. Actual assistant replies acknowledge instruction skill marker twice. | `test_02_real_two_tasks`; `logs/real-metrics.jsonl`, `logs/skill-observed.json`, `logs/t1-state.json`, `logs/t2-state.json`. |
| 3 Telemetry/status | PASS. Real before/after `get_session_stats`, current context occupancy distinct from session cumulative counters, per-attempt deltas, cache zeroes, headroom provenance, timestamps, checks and SHAs. Separate subprocess CLI reads SQLite without Pi or conversational coordination. | Same test invokes `harness.py status --root .../real --task t1` and `t2`; stdout in `logs/suite.log`; before/after records in `logs/real-metrics.jsonl`. |
| 4 Greedy cutoff | PASS. Explicit synthetic factory selects same session at exactly 150000 free, new UUID at 149999; unknown/incompatible/unready/different affinity deny reuse. Real inputs verified via Pi contextUsage/contextWindow plus controlled effective settings and installed version source. | `test_01_configuration_and_cutoff`, `logs/cutoff.json`; threshold **483616**, not model advertised **500000**. See README telemetry section. No large token burn. |
| 5 Checks/Git | PASS. REQUIRED exact text equality before each focused `git commit --only -- toy.txt`; commits retain task ID/baseline/result. Staged unrelated.txt excluded, unrelated tracked seed modification preserved. | `test_02_real_two_tasks`, `test_03_crashes`, `test_04_bounded_repair`; commit/check events in `logs/*state.json`. |
| 6 Crash/reconcile | PASS. Actual process SIGKILL after file-write/receipt before node-success checkpoint; separately after real Git commit before commit-node checkpoint. New processes resume real LangGraph/SQLite. One synthetic worker dispatch and one task commit per case; no destructive cleanup. Reconciliation checks expected file, unique task commit, HEAD, parent baseline and owned path. | `test_03_crashes`; `logs/crash-recheck.log`, `logs/crash-file-state.json`, `logs/crash-commit-state.json`. Worker is synthetic, engine/Git/checkpointer/kill/restart real. |
| 7 Bounded failure | PASS. Synthetic worker intentionally writes bad text, REQUIRED check fails, one configured repair role succeeds, then one focused task commit. No narrative-based decision. CLI independently runnable/queryable. | `test_04_bounded_repair`, `logs/repair-state.json`: checks `[false,true]`, repair count 1; `logs/suite.log`. |
| 8 No orchestration LLM | PASS. Registered handlers return enumerated code outcomes; LangGraph YAML transitions route them. Pi writes files only; no free-form response selects node/model. No Pi process in synthetic crash/repair/config tests or status CLI. | `harness.py` node handlers/conditional edges, `test_harness.py`, validated YAML. No LangChain agent abstraction instantiated. |

## Real result details

Observed real Pi session for **both** tasks:
`01a14fd9-6b69-7576-a1f8-46806138c694`.

| Task | Baseline → task commit | Context start→end | Input/output/cache-read/cache-write deltas |
|---|---|---|---|
| t1 (fresh) | `eb8155ba1980d6df868230fc8cc62238de3344e4` → `65df7ea8b57c17eb3334c8a7f6ffdbe3dd3ec925` | 0 → 938 | 1744 / 70 / 0 / 0 |
| t2 (reused) | `65df7ea8b57c17eb3334c8a7f6ffdbe3dd3ec925` → `a121470c57b3e8ebee0cf45356a689c453519efa` | 938 → 1120 | 2107 / 71 / 0 / 0 |

Both have effective threshold **483616** (500000 minus configured/verified reserve 16384).
End headroom: **482678**, **482496**. Session-cumulative end counters after t2:
input **3851**, output **141**, cache read/write **0/0**. Context occupancy **1120** is not
cumulative **3992**. Provenance is actual Pi RPC, not guessed usage or advertised headroom.
Compaction is observed enabled after explicitly trusting the known toy-local configuration;
exact-model reserve override prevents global-model override ambiguity.

## Execution and bounded corrections

- Installed pinned stable dependencies in supplied venv; direct pip/no cache, worktree temp.
- First draft: four tests passed, but inspection identified missing effective-compaction
  observation and async checkpoint uncertainty. Added enabled assertion, controlled model
  override, synchronous checkpoint durability, before/after deltas, and stronger evidence.
- Next run failed **before a model prompt** because project settings were untrusted and
  global compaction was disabled. Inspected traceback/settings/source; bounded correction
  was **`--approve` for the known disposable toy only**, not a global configuration change.
- Corrected suite passed; strengthened staged/unrelated dirt and actual assistant-marker
  assertions; final full suite: **4 tests, 15.215 seconds, OK** (`logs/suite.log`).
- Added parent-SHA/single-path commit reconciliation assertions; focused crash rerun:
  **1 test, 4.379 seconds, OK** (`logs/crash-recheck.log`). No unexplained agent relaunch.
- `pip check`, Python compilation, JSON evidence parsing and `git diff --check` passed.
  Full first-draft history is summarized in `logs/corrections.json`, not hidden as framework failure.

[Portable reproduction and state/telemetry semantics](docs/evidence/workflow-stack-validation/README.md).
Dependencies, schema, YAML, minimal code and sanitized logs are retained; no venv, SQLite
binary, raw sensitive transcript, environment dump, credentials or toy `.git` is retained.

## Authoritative remote verification — 2026-10-18 UTC

See [dated responses and exact URLs](docs/evidence/workflow-stack-validation/remote-signals.json).
Official GitHub latest stable LangGraph **1.2.16**, published **2026-10-16**;
official PyPI agrees. SQLite checkpointer latest **3.1.2**, uploaded **2026-10-12**.
Both require Python >=3.10 and declare **MIT**. GitHub repo is not archived, pushed
**2026-10-18**; official response: **43447 stars**, **7407 forks**, **652 open issues**.
These are dated popularity/activity proxies, **not users, installs, support guarantees or
an issue-quality assessment**. This evidence supports active maintenance/community only.
Pinned versions executed successfully on Python 3.12.3; no prerequisites auto-installed globally.

## Operational/glue cost and residual limits

The adapter is roughly 240 Python lines plus roughly 120 lines of acceptance tests, a tiny
YAML and schema. Framework provides graph routing/checkpoints; custom glue explicitly owns
RPC lifecycle, admission/telemetry, file/commit reconciliation, checks, lock and projections.
Installation needs a Python venv and native SQLite, no orchestration service. Status requires
only a short-lived CLI process. Host exit stops execution; explicit restart resumes it.

This PASS concerns the eight executable **toy** demonstrations, not production readiness:

- SQLite does **not** make external effects exactly once. Tested known receipts/Git effects
  reconcile; uncertain partial file content raises instead of dispatching a second worker.
  Power loss/fsync guarantees and adversarial receipts/task IDs are not tested.
- Real Pi stays alive across the two in-process task threads. Persisted real-session
  reattachment, real mid-tool process death/orphan cleanup and mid-task pressure monitoring
  are **not** demonstrated. Never blindly resume a real in-flight worker; confirm it stopped,
  reconcile partial files and block if uncertain. The crash worker was explicitly synthetic.
- 150k is an admission preference, not an optimum or guarantee against long-task compaction.
  Effective threshold relies on controlled settings plus installed-source provenance, not a
  direct RPC threshold field; production would need reliable per-version/model resolution.
- Inline toy instruction skills demonstrate binding/reaching the node, not production skill
  loading or compliance enforcement. Tool/instruction restrictions are not a filesystem sandbox.
- State projection is latest queried task; append-only JSONL observations are derived from
  SQLite, versioned/idempotently keyed, not a production all-run status service. JSONL tail
  corruption, multi-host locks, comprehensive approvals/review semantics and untrusted YAML
  hardening remain outside this deliberately disposable experiment.
- No different real concrete model or effort was exercised. YAML profile alias/skill/edge
  variation ran synthetically; default exact Sol/medium was observed in real execution.

**Next:** parent independently reviews this evidence and focused commit. B/C remain NOT RUN;
this worker does not start Phase 2 or assert owner acceptance.

## Superseded BLOCKED history (preserved)

The baseline report dated 2026-10-18 recorded **shared prerequisite BLOCKED**, with A/B/C
all NOT RUN: the fresh-subagent extension rejected unsupported `config.permissions.ask_user`.
It had observed Pi/Git/Python/catalog availability, but no real RPC or candidate test, and
reported an earlier disposable `/tmp` pip dry-run, not this run's environment. It correctly
did not classify any framework FAIL. Before this assignment the parent explicitly repaired
the global config preserving ask_user denial under `permissions.rules`, verified real RPC
`PREREQUISITE_OK`, and launched this distinct worker. This supersedes that shared blocker
with executed A evidence; this child made no global repair and used no `/tmp` toy/code repo.
