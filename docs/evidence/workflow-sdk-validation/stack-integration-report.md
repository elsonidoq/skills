# Focused Pi SDK-host PoC — PASS within tested bounds

Executed 2026-10-18 UTC. This is the newly authorized disposable empirical seam probe,
not architecture planning, migration implementation, production readiness, owner acceptance,
or A/B/C reselection. Prior candidate A remains the Python LangGraph/SQLite stack;
**B/C NOT RUN**. Parent review is required before planning resumes. Affected specification
renewal is still pending; paused planner files were not adopted or edited.

## Acceptance matrix

All paths here are relative to this report. Real means actual installed Pi SDK/provider/tool;
synthetic cases are explicitly separated. No installed SDK/provider source was modified.

| # | Result | Executed evidence and boundaries |
|---|---|---|
| 1 SDK host + reuse | **PASS** | Standalone Python controller → Node LF-JSONL host, installed official 0.87.1 SDK. Two real write-tool tasks used observed session `01a1512d-b0ee-73b2-ae85-ea72e7b9625b`. Actual `loadSkills` + loader override + `/skill:toy-skill` expansion; both final responses matched skill-only marker. Explicit model/effort/tools/cwd/resources/settings/session manager. Requested/runtime and final outgoing body model/effort recorded, no fallback. [reuse log](logs/reuse.jsonl), [results](logs/results.json), [actual file observations](logs/file-observations.json). |
| 2 telemetry | **PASS** | Actual session `settingsManager.getCompactionSettings(session.model)` returns enabled true, reserve 16384, contextWindow 500000; threshold 483616. Current projected occupancy 0→452→725 differs from cumulative totals. Deltas below. Controlled **synthetic inputs to real SDK settings** prove recursive global/project conflict resolution, exact-model override, ordinary/default fallback, invalid rejection and zero storage writes. External caller cutoff fixtures: 150000 reuse, 149999/unknown/disabled/unsettled fresh-or-block. No threshold token burn. [settings](logs/settings.json), [results](logs/results.json), [unit tests](logs/unit.log). |
| 3 outbound guard | **PASS within tested pipeline** | Six real provider request turns (four short-task turns + one per interrupted task) observed final body `model=gpt-6.1-sol`, `reasoning.effort=medium`. SDK runtime effort medium maps to wire **medium** in this actual catalog. Guard composes SDK extension transforms before validating, outside swallowed extension exceptions. Explicit synthetic extension changes wire effort to high; second extension throws. Guard yields error, not successful task; zero instrumented sends, no forbidden file. Synthetic summary-route call also blocked with zero sends. [focused guard regression](logs/guard-regression.jsonl), [real logs](logs/reuse.jsonl), [abort](logs/abort.jsonl), [kill](logs/kill.jsonl). Actual overflow/compaction/retry **not induced**. |
| 4 interruption/quiescence | **PASS for bounded Linux bash descendants** | Real agent launched standard bash and a bounded descendant mutation loop. Abort request → SDK abort/waitForIdle → observed settled/idle, no live owned identities/group, partial bytes 1→1 over 0.6s. Separate run SIGKILLed host during live tool: descendant **survived and kept writing** (1→4 bytes in 0.3s). Python supervisor reconciled pre-recorded PID+start-time ancestry/PGID, killed proven-owned tool group, observed no live group + 4→4 bytes over 0.6s, then admitted deterministic replacement writer. No agent replacement/replay or persisted-session reopen claim. [results process records](logs/results.json), [file observations](logs/file-observations.json), [independent checks](logs/recorded.log). |
| 5 protocol/errors/limits | **PASS for trusted single caller** | Subscribe before prompt. ID-correlated prompt acceptance separate from settled record; awaits SDK prompt + waitForIdle, never completes on agent_end. Actual abort ends with successful=false/aborted, synthetic guard error ends as error. Version mismatch poisons/rejects, missing/unknown/nonfinite headroom denies reuse, EOF raises instead of completion. Bounded controller/provider/tool waits, no retries or alternate profile, independent status reads JSON without Node/LLM. [unit](logs/unit.log), [source](poc/controller.py), [wire semantics/limits](README.md). Not a hardened arbitrary-client protocol. |

## Actual measured short tasks

| Task | Current context start→end | Input/output/cacheRead/cacheWrite delta | End headroom | File SHA256 |
|---|---|---|---|---|
| t1 | 0→452 | 774 / 69 / 0 / 0 | 483164 | `5891b5b522d5df086d0ff0b110fbd9d21bb4fc7163af34d08286a2e846f6be03` |
| t2 | 452→725 | 1319 / 70 / 0 / 0 | 482891 | `a948904f2f0f479b8f8197694b30184b0d2ed1c1cd2a1ec0fb85d299a192a447` |

Cumulative end counters after t2: input 2093, output 139, cacheRead/cacheWrite 0/0,
total **2232**, not current occupancy **725**. SDK cost field for these two tasks is in
`results.json` (0.005576); abort-run recorded cost is 0.000976. Killed-host final usage/cost
is **unknown**, not zero; the sixth provider request was observed before host termination.
Zero cache counters
are measured zero, not fabricated unknowns. Current occupancy is the SDK's projected
estimate, **not** exact tokenizer truth; post-compaction occupancy can legitimately be
null until another assistant response. Host reports null headroom in that situation;
unknown/disabled compaction is not infinite headroom. Headroom is an admission preference,
not a guarantee a long active task will not compact.

## Reproduction and executed checks

[README](README.md) documents environment, dependencies, wire contract, safe toy-only
commands and limitations. No dependency installation, new venv, toy Git repo, database,
global configuration, credential, identity, original evidence or production file writes.
Runtime code: 137 Node host lines + 212 Python controller lines (includes synthetic fixture
and process observations), plus focused tests/skill. Four short-task fetches plus one abort-run
fetch were counted; the sixth request's real provider-produced tool call proves it was sent,
but host termination prevented a final counter read. Six corresponding guard passes are
retained. No paid retries, model switches, threshold burn, daemon or orchestration LLM.

Environment for actual runs:

- `PI_SDK_ROOT=/home/dev/.pi/agent/install/releases/0.87.1/node_modules/@earendil-works/pi-coding-agent`
- `PI_AUTH_PATH=/home/dev/.pi/agent/auth.json` (read-only; never retained)
- `PI_MODELS_STORE_PATH=/home/dev/.pi/agent/models-store.json` (read-only catalog)
- `PI_OFFLINE=1`, `PYTHONDONTWRITEBYTECODE=1`
- `TMPDIR=$PWD/.pi/workflow-validation/sdk-poc/tmp`

Executed commands (from worktree root):

```sh
node --check docs/evidence/workflow-sdk-validation/poc/host.mjs
python3 docs/evidence/workflow-sdk-validation/poc/controller.py run \
  --root "$PWD/.pi/workflow-validation/sdk-poc/run2" \
  --logs docs/evidence/workflow-sdk-validation/logs
node docs/evidence/workflow-sdk-validation/poc/test-settings.mjs
python3 docs/evidence/workflow-sdk-validation/poc/test_controller.py
RECORDED_ROOT="$PWD/.pi/workflow-validation/sdk-poc/run2" \
  python3 docs/evidence/workflow-sdk-validation/poc/test_recorded.py
python3 docs/evidence/workflow-sdk-validation/poc/controller.py status \
  --logs docs/evidence/workflow-sdk-validation/logs
```

Full real run: [suite.log](logs/suite.log). Three no-paid-call unit tests and two
independent retained-evidence/actual-file/process tests pass. Focused guard regression
initialized a fresh host with the same explicit profile/tools and sent only
`synthetic_guard`; two actual extension-throw notifications, two guard failures,
**zero transport calls**, both actual provider error responses inspected. See retained
JSONL rather than interpreting provider response prose.

### Bounded corrections (no hidden infrastructure retry)

Initial `run1` stopped **before any provider request**: static-only SDK model runtime could
not find the exact selected model. An init-only diagnostic exposed `exact model unavailable`;
inspected actual installed cached catalog and exported `ModelsStore` API. Corrected host
reads existing catalog into private memory with network disabled. Init-only diagnostic2
confirmed exact model/effort/settings and zero guards/sends; then one real `run2` passed.
The initial generic error obscured diagnosis and close-before-init failed; both corrected
without provider calls. Later tests found a Python unclosed-stdout ResourceWarning; reader
join/pipe closing fixed and unit tests reran without warnings. Synthetic extension-throw
notifications and nonfinite-headroom rejection were added and focused no-paid tests reran.
No unknown provider failure, expensive uninspected retry, or framework fallback occurred.

## Official API/source provenance

[Source manifest](source-manifest.json) records baseline, branch, exact installed package
versions, input catalog hash and SHA256 of meaningful installed sources. All are read-only.

- `docs/sdk.md` fully read: session configuration, prompt/retry completion, subscribe before
  prompting, agent_settled vs agent_end, abort/waitForIdle/dispose. Linked SDK examples
  02/04/05/06/09/10/11/12 read, plus skills/extensions/compaction/CLI integration and linked
  configuration/settings/sessions/models/providers/session-format/message-types/security docs.
- `pi-coding-agent/dist/core/sdk.js:75–143`: explicit configuration/model/effort clamping;
  `177–245`: SDK stream function, extension payload transforms and cache warmer. Fallback
  message is checked, exact model mandatory, clamped effort mismatch blocked.
- `pi-agent-core/dist/agent.d.ts:40–45`: public mutable `streamFunction` and `onPayload`.
  Host wraps public stream function, not private SDK implementation or installed source.
- `agent-session.js:1842–1845`, `2938`, `3181`: compaction/branch/bug summaries use public
  agent stream function. `compaction.js:484–508` summary options do not inherit
  agent.onPayload, so wrapping **only onPayload is insufficient**. Host wraps stream and
  composes existing per-call hook or SDK hook before guard. Synthetic no-hook summary-route
  fixture exercises provider builder, not a real summary of a large conversation.
- `pi-ai/dist/api/openai-codex-responses.js:363–428`: effort clamp/map into body.reasoning;
  `174–180`: await hook before serialize; `267`: SSE fetch. SSE explicitly selected;
  real wire counter wraps fetch. Synthetic test replaces fetch with a counting sentinel,
  preventing actual sends even on regression. No raw body/header/auth logging.
- `extensions/runner.js:961–987`: ordinary before_provider_request exceptions are swallowed;
  host guard throws after runner returns. Synthetic thrown handler is observed explicitly.
- `settings-manager.js:566–596`, `compaction.js:194–197`: model override→ordinary→default;
  threshold enabled and contextWindow−reserve. `agent-session.js:3043–3136`: cumulative
  billing vs projected context estimate/null after compaction.
- `cache-warmer.js:91–93,114–118`: off avoids starts; host sets off. Agent/provider retries
  disabled; six real guard passes correlate to five counted fetches plus the killed run's
  real provider-produced tool call (no final transport counter after host death).
- `agent-session.js:1608–1625`: abort awaits idle. `tools/bash.js:35–110` uses detached
  shell, abort group kill and child wait; `utils/shell.js:169–214` group killing. Abrupt
  SIGKILL cannot execute cleanup: orphan danger is empirically observed, not assumed away.

## Ownership/checkpoint and conclusion

Baseline **79f315980c3380471579f1e556ee2016b587eaeb**, branch
`follow-attached-workflow-migration-instructions`. Authorized retained scope only this new
`docs/evidence/workflow-sdk-validation/**`; scratch under `.pi/workflow-validation/sdk-poc/`.
Whole `memory/MEMORY.md` read (empty gotcha index), coordination guidelines empty; no writes.
Expected six paused-planner path hashes and empty index verified before implementation;
rechecked before/after the focused task commit (result SHA in scratch return, avoiding
self-reference). No broad staging, planner adoption, spec edits or global asset changes.

**Conclusion:** official SDK path is empirically suitable for this small telemetry,
request-binding and lifecycle seam **within the tested limits**. Host death alone is not a
quiescence boundary. A real supervisor/process registry and fail-closed reconciliation are
required before any production replacement writer; this toy demonstrates one Linux owned
group only. No durability, production runner/schema/approval system, general sandbox,
exactly-once, full workflow, arbitrary extension/provider support, model alternatives,
real high-pressure compaction, resumed Pi-session recovery or architecture approval is
claimed. Parent should independently inspect evidence and commit before planner resumption.
