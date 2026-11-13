# Dependency and seam research

Canonical research owner for this migration; discover through [plan](plan.md).
Research date: 2026-11-13. Requirements: [current specification](spec.md).
These are design findings, not installed integration or live acceptance results. Derived
choices below remain revisable under the [plan](plan.md#requirements-versus-proposed-mechanisms);
source findings and required observables are not waived by a simpler equivalent mechanism.

## Dependency selection

**Decision (derived):** Target Python >=3.10, retaining the current public minimum;
use Python 3.12 Linux x86_64 for the existing hashed wheel-lock convention.
Select `langgraph==1.2.21`, `langgraph-checkpoint-sqlite==3.1.3`, and
`opentelemetry-api==1.45.2`, `opentelemetry-sdk==1.45.2`,
`opentelemetry-exporter-otlp-proto-http==1.45.2`; retain `PyYAML==6.0.3`. These are Python
dependency choices, not required versions of Pi, subagents or ask-user capabilities.

Read-only Python `urllib.request` successfully fetched official documentation,
PyPI metadata and wheel source in memory. No packages were installed or imported.
Version-specific metadata inspected:

- [LangGraph 1.2.21](https://pypi.org/pypi/langgraph/1.2.21/json): Python >=3.10;
  `langchain-core>=1.4.7,<2`, checkpoint >=4.3.0,<5, prebuilt >=1.1.0,<1.2,
  SDK >=0.4.6,<0.5, Pydantic >=2.7.4 and xxhash >=3.5.
- [SQLite saver 3.1.3](https://pypi.org/pypi/langgraph-checkpoint-sqlite/3.1.3/json):
  Python >=3.10; checkpoint >=4.3.1,<5, aiosqlite >=0.20 and sqlite-vec >=0.1.6.
- [OpenTelemetry API](https://pypi.org/pypi/opentelemetry-api/1.45.2/json),
  [SDK](https://pypi.org/pypi/opentelemetry-sdk/1.45.2/json) and
  [OTLP HTTP exporter](https://pypi.org/pypi/opentelemetry-exporter-otlp-proto-http/1.45.2/json)
  1.45.2 all require Python >=3.10. SDK pins API 1.45.2 and semantic conventions 0.66b2;
  HTTP exporter uses proto/common 1.45.2 and HTTP transport/OTLP common 0.66b2.
  Their inspected metadata supports the suite floor without the Phoenix wrapper.
- [Phoenix 21.0.0](https://pypi.org/pypi/arize-phoenix/21.0.0/json) and
  [Phoenix OTel 0.17.3](https://pypi.org/pypi/arize-phoenix-otel/0.17.3/json) require
  Python >=3.11,<3.16. Isolate the server in its official container; do not install either
  package in the workflow environment or force an old wrapper. Standard OTLP suffices.
- Previously inspected [langchain-core 1.4.7](https://pypi.org/pypi/langchain-core/1.4.7/json)
  declares Python >=3.10,<4, LangSmith >=0.3.45,<1 and PyYAML >=5.3,<7.
  Remove the direct RunTree adapter/dependency need, not the necessary transitive package.
  Package presence is not hosted export; ambient hosted tracing must still be suppressed.

**Rationale:** Use current documented APIs and the supported file saver, not a custom
checkpoint implementation. Exact direct versions make the reviewed privacy behavior
reproducible. Metadata intersection is not a resolved transitive lock or wheel-platform
proof. During authorized dependency delivery, resolve the complete lock using the
repository convention, run dependency consistency/import checks, and execute the actual
saver/graph checks on supported Python environments. Do not silently raise the Python
minimum if a selected transitive release fails; resolve compatible transitive versions
or return the affected compatibility decision. No install is authorized by this report.

**Alternatives:** In-memory saver cannot survive reopen. Postgres and a hosted graph
service add unrequested operations. Owner selected LangGraph after framework comparison;
no concrete finding here disproves that choice. No second framework or scheduler.

## Persistence and graph control

Official sources read as Markdown, using their named sections:

- [Checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers),
  “Threads,” “Choose how to continue a thread,” “Pending writes,” and “Durability modes”:
  stable `thread_id` selects saved state; `None` resumes unfinished non-interrupt work;
  `Command(resume=...)` answers interrupts. Successful node writes in a failed superstep
  can be retained. `durability="sync"` persists before the next step. Replaying a historic
  checkpoint is different from continuing the latest one.
- [Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api), “State,”
  “Reducers,” “Re-execution and idempotency,” and `Send`: nodes return partial updates;
  parallel writes need reducers. `Send` supplies per-branch input, not application DAG
  readiness. [Control flow](https://docs.langchain.com/oss/python/langgraph/graph-api-control-flow)
  is the parent's applicable supporting source for synchronized supersteps.
- [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts), “Resume,”
  “Handling multiple interrupts,” and “Rules of interrupts”: the interrupted node starts
  again. Resume values can be mapped by interrupt ID. Do not catch the framework interrupt
  with a broad exception handler, reorder interrupt calls, or perform unreconciled effects
  before them. The newer event-stream v3 interface is not needed for this CLI.
- Version-specific SQLite saver wheel, `langgraph/checkpoint/sqlite/__init__.py`,
  `SqliteSaver` and `from_conn_string`: lightweight synchronous local usage; connection
  uses `check_same_thread=False` and an internal lock. This does not make the repository's
  separate `Store` connection safe for graph worker threads or provide distributed scaling.

**Implication:** Standard persistence supports the proposed graph layout, but does not prove
external effects occurred exactly once. Use durable state and effect reconciliation; the
[plan](plan.md#one-execution-controller) owns proposed wiring and the
[quickstart](quickstart.md#composed-execution-and-recovery) owns its observable checks.

## Pi, Git and question seams

Repository inspection at `4c1725ebded2f89dec6933b8d193bf34997c62ce`:

- `engine.py:Engine.invoke`, `_finish_reviews`, `run_fix` and recovery methods contain
  the controller to replace. Keep prompt/attribution/session/check helpers, not their
  custom stage-selection loops. `intake.py:admit` already implements exactly six checks.
- `git_effects.py:FocusedGit` claims actual edit paths and commits with `--only` and
  normal hooks/signing. `reconcile_checkpoint` currently relies on in-memory attempted
  parent/paths and current HEAD. The worker commit-success/history-write window therefore
  needs durable operation-local intent and actual Git comparison before graph retry.
  Existing fixer/external-recovery history already records comparable intent; reuse that
  pattern. No new receipt database or broad range attribution is warranted.
- `store.py:Authority` takes a per-worktree `flock` inherited by the SDK host; `Store`
  creates a normal thread-bound SQLite connection. Keep one controller per worktree and
  allow its authorized disjoint workers to overlap. Serialize history transactions with
  connections created in their owning threads; never share the present connection freely.
  Quiesce sibling mutations before project checks and Git checkpoints. Git's index lock
  alone does not protect a check→stage→commit interval.
- `pi_adapter.py:PiAdapter.prompt` owns host subprocess/callback decoding and private saved
  session references. `host.mjs:ask_owner` currently blocks on a callback; `execute` drains
  SDK abort before disposal; `promptSession` waits for idle and rejects aborted results.
  A Python `interrupt()` cannot simply be thrown through this live callback: that would
  neither durably deliver the answer nor prove settlement.
- The proposed [question adaptation](plan.md#questions-reach-the-actual-consumer) must
  establish SDK idle/settlement and deliver the real answer after reopen. Existing abort
  support is not proof of durable pause. Test the actual installed SDK boundary before
  reliance; prefer a simpler supported equivalent if it establishes the same observables.
- The parent bridge currently has one active steering target and one question. Change
  target storage to a map keyed by task/invocation/session for an authorized wave. Serialize
  owner questions through the existing tools, preserving their request IDs and owner-only
  distinction. No broadcast steering or automatic consent. Routine updates remain
  `triggerTurn: false`; questions and terminal completion can wake the parent.
- `sessions.py` already rejects nonidle, incompatible and reviewer reuse. Preserve this
  selection policy, not a new session inventory. A session cannot serve overlapping calls.
  `metrics.py:interval_record` qualifies continuous exclusive before/after deltas; reuse
  it rather than export `getSessionStats()` cumulative totals.

**Verification basis:** Pure graph mocks cannot establish Pi settlement, Git custody or
actual answer consumption. Use permanent production-boundary checks in
[quickstart](quickstart.md#composed-execution-and-recovery), not a separate demo chain.

## Metadata-only local Phoenix submission

**Current selection:** local Phoenix replaces the historical LangSmith destination; LangGraph
and metadata-only privacy remain. Only opaque identities, hierarchy, role/model, safe status,
time and qualified invocation-local usage/cost may leave the process, even over loopback.
Unknown values are omitted, not zero; reuse `metrics.interval_record`. No raw prompts,
responses, tool data, exceptions, paths or environment metadata. No per-token/per-tool tracing.

### Sources and minimal deployment

- Parent-inspected [Docker guidance](https://arize.com/docs/phoenix/self-hosting/deployment-options/docker)
  supports one container, SQLite in a persistent working directory, UI and OTLP HTTP 6006.
  [Privacy guidance](https://arize.com/docs/phoenix/self-hosting/security/privacy) describes
  disabling telemetry and external resources. Direct refresh returned HTTP 403 here; readable
  tagged official [config source](https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/config.py)
  confirms `PHOENIX_WORKING_DIR`, SQLite guidance, `PHOENIX_TELEMETRY_ENABLED=false`,
  `PHOENIX_ALLOW_EXTERNAL_RESOURCES=false` and suppression of automatic model-price fetch
  when external resources are false. These flags do not forbid operator-configured providers;
  configure none in Phoenix. This is not a universal firewall or ban on existing Pi traffic.
- Tagged official [Dockerfile](https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/Dockerfile)
  starts `phoenix.server.main serve`, binds container interfaces and exposes 6006/4317/9090.
  Expose **only** host loopback HTTP 6006; do not copy the repository's Postgres Compose example
  or publish gRPC/Prometheus ports. Tagged `auth_enabled_for_host` enables authentication
  for the container non-loopback bind; retain that default and configure only local Phoenix
  credentials in private durable storage during ordinary setup, not a hosted account. No
  separate collector, Redis, ClickHouse or agent server.
- Read-only [Docker Hub tag metadata](https://hub.docker.com/v2/repositories/arizephoenix/phoenix/tags/version-21.0.0)
  identifies `arizephoenix/phoenix:version-21.0.0`, multi-platform index digest
  `sha256:1f9a144a5357b4973e93a15718f050247cb7a4ee7b7c6c06ecb91b5eed3fbaad`,
  amd64 child `sha256:b5bcec3455bd5c431f52737fc62046c081752b483e3fff40c63f40783736bcad`.
  Pin the index digest in future maintained configuration; metadata is provenance, not a
  pulled/running image or verified package/UI contents. Confirm the selected image's effective
  version/configuration during authorized setup. No image pull/build occurred here.
- Local read-only discovery: Docker client/daemon 29.1.3, Linux amd64, accessible; no running
  containers or cached Phoenix image reported, no listener on 6006. Compose is absent.
  Plain Docker is sufficient; this is not an agent-version requirement or new startup gate.
  Recheck service/storage collisions only at actual setup; do not adopt/stop unknown assets.
  [Configuration contract](contracts/interfaces.md#local-monitoring-configuration) owns storage
  and settings. Local setup/config/docs belong with adapter delivery, not a provisioning platform.

### Standard adapter and concrete privacy seams

Use explicit manual run→task→invocation spans with fixed names, isolated OTel provider and
closed attributes; use small completed boundary spans for useful progress while the root is
open. Opaque IDs replace user strings. A fixed `openinference.span.kind=CHAIN` attribute can
help Phoenix render hierarchy without pretending these are raw LLM message spans. Known
usage/cost can remain approved numeric attributes; do not rely on server price estimates.
Parent-inspected [instrumentation guidance](https://arize.com/docs/phoenix/tracing/how-to-tracing/setup-tracing/instrument)
shows decorators capturing inputs/outputs; do not use them or generic auto-instrumentors.

Read-only wheel inspection of the selected SDK/exporter and transport found concrete seams:

- `Resource.create` invokes detectors and merges defaults/environment. Construct an explicit
  `Resource` with fixed safe service/project fields instead; no process/host/path detectors,
  ambient baggage or parent context. Use an isolated provider, not global auto-configuration.
- `OTLPSpanExporter` accepts explicit endpoint and Requests session. Its `_resolve_headers`
  merges environment headers **even with an explicit empty mapping**. An empty `headers={}`
  is not isolation. Use a dedicated session with `trust_env=False`, no ambient auth/cookies, and a
  small final-request closed-header projection in the adapter, retaining only required safe
  OTLP/HTTP protocol headers and explicitly supplied local Phoenix authorization. Never
  inherit ambient authorization or include credentials in spans/logs. This is a local adapter safeguard, not a redaction service.
  Do not mutate shared process environment around concurrent worker calls.
- HTTP transport 0.66b2's `RequestsHTTPTransport.request` explicitly uses
  `allow_redirects=False`. Reuse that control; check it at the final request seam. Explicit
  numeric-loopback endpoint plus `trust_env=False` prevents ambient endpoint/proxy routing;
  do not permit userinfo, query secrets, alternate hosts or remote redirects. A configured
  nonlocal destination disables affected export with an actionable diagnostic, not execution.
- Suppress automatic exception recording/status descriptions; set safe status/category only.
  Disable exporter internal metrics via an explicit no-op meter provider, and create no
  ambient metrics/log exporters. Suppress automatic LangGraph/LangSmith tracing, including
  inherited hosted settings (the transitive `tracing_context(enabled=False)` is a candidate).
  Final-wire checks must establish suppression, not merely inspect flags. Do not relay raw
  exporter errors/collector response bodies into telemetry; report a safe local gap category.

These helper choices are derived. Equivalent simpler SDK controls are preferred if final
payload/destination proof holds. No wrapper, custom collector/firewall or telemetry ledger.
When disabled, create no exporter and send zero monitoring requests; when enabled, loopback
HTTP is expected. Optional export failure cannot veto checks, commits or safe continuation.

### Incremental visibility: required, not yet proven

The inspected [OpenTelemetry trace SDK specification](https://opentelemetry.io/docs/specs/otel/trace/sdk/)
`OnEnd`/span-processor behavior exports finished spans independently of root completion.
Standard batch processing and boundary flush can deliver completed invocation/task/progress
spans during a running graph; do not hold everything until graph END. Parent-inspected
[historical partial-trace change](https://github.com/Arize-ai/phoenix/pull/2353) supports the
possibility, not current UI refresh behavior, an open-span timer or latency/parity guarantee.

[Final-wire checks](quickstart.md#trace-privacy-before-real-metadata-export) precede real
metadata export. [Actual evolving-run UI acceptance](quickstart.md#live-replacement-and-monitor-retirement--explicit-gate)
must show useful incremental hierarchy/progress before root completion. If inadequate,
report the specific gap and retain the old monitor; no custom UI or heartbeat/event-log
framework. Installation/transitive lock, image readiness, SDK final-wire privacy, server/UI
incidental-network behavior and incremental visibility are **NOT VERIFIED**. No collector,
UI, provider or hosted account operation was run. Ordinary future local setup needs no cloud
account/project/region/pricing/upload ceremony; actual new external/paid/security/data effects
keep their applicable gates.

## Lifecycle and retirement research

Use existing planner/task/finish-session and `track-open-issue` conventions. Its paginated
`gh api ... issues?state=all` pattern includes PRs, so exclude `pull_request` entries.
Source association and summaries belong to the issue and chat, not a new service. Reuse
existing-label semantics if suitable; intake found none. Proposed state labels are in the
[interface contract](contracts/interfaces.md). Creation/application remains later authority.

Verified active retirement seam: `scripts/test-planner-workflow.py` loads `rpc` at line 32;
only `RpcDriverTests` uses that module. Remove that load/class with the driver. Keep adjacent
carrier/trace/installer tests subject to maintained-contract relevance, not immutable strings.
`README.md` validation and `docs/plans/planner-regression.md` operative smoke/scenario
sections point to the retired convention. The latter also has historical NOT RUN evidence:
explicit supersession must preserve that distinction. `docs/index.md` routes evaluations;
AGENTS points to the evaluation README. No skill Markdown literal `evaluations/` caller
was found; skill verification wording still needs focused semantic alignment, not bulk edits.

`workflow_monitor/README.md` owns current monitor/cutover/rollback and pending usability
limits. Keep its historical reference and retained databases. Monitor-specific source,
recording and dependencies are removed only after live replacement verification. Existing
metric artifacts and history readers are useful compatibility mechanisms, not redundant
trace ledgers to rebuild or automatically delete.
