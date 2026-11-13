# Dependency and seam research

Canonical research owner for this migration; discover through [plan](plan.md).
Research date: 2026-11-13. Requirements: [approved specification](spec.md).
These are design findings, not installed integration or live acceptance results.

## Dependency selection

**Decision (derived):** Target Python >=3.10, retaining the current public minimum;
use Python 3.12 Linux x86_64 for the existing hashed wheel-lock convention.
Select `langgraph==1.2.21`, `langgraph-checkpoint-sqlite==3.1.3`, and
`langsmith==0.14.17`; retain `PyYAML==6.0.3`. These are new Python dependency
choices, not required versions of Pi, subagents or ask-user capabilities.

Read-only Python `urllib.request` successfully fetched official documentation,
PyPI metadata and wheel source in memory. No packages were installed or imported.
Version-specific metadata inspected:

- [LangGraph 1.2.21](https://pypi.org/pypi/langgraph/1.2.21/json): Python >=3.10;
  `langchain-core>=1.4.7,<2`, checkpoint >=4.3.0,<5, prebuilt >=1.1.0,<1.2,
  SDK >=0.4.6,<0.5, Pydantic >=2.7.4 and xxhash >=3.5.
- [SQLite saver 3.1.3](https://pypi.org/pypi/langgraph-checkpoint-sqlite/3.1.3/json):
  Python >=3.10; checkpoint >=4.3.1,<5, aiosqlite >=0.20 and sqlite-vec >=0.1.6.
- [LangSmith 0.14.17](https://pypi.org/pypi/langsmith/0.14.17/json): Python >=3.10;
  includes HTTP, serialization and compression dependencies. No optional provider,
  evaluation, OpenTelemetry or hosted-agent extras are selected.
- [langchain-core 1.4.7](https://pypi.org/pypi/langchain-core/1.4.7/json), wheel
  METADATA: Python >=3.10,<4; LangSmith >=0.3.45,<1 and PyYAML >=5.3,<7.
  The selected direct requirements intersect these declarations.

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

**Derived choice → checks:** One `StateGraph` with a task subgraph, a stable run ID as
thread ID, sync file checkpoints and no provider-node automatic retry policy. Application
readiness selects one ready task by default or an explicitly authorized disjoint wave.
Keyed task-result reducers merge distinct IDs, not unordered append-only trace data.
Use separate saver and ordinary history connections. Prove crash/reopen and failed-sibling
pending writes through the permanent production graph, not a second demo implementation.
Graph state contains control data/references; it is neither an effect receipt nor a trace
warehouse. Reconcile retained dispatch/Git facts before a rerun can mutate.

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
- Use a narrow opt-in host question-pause result: preserve the question and saved session,
  mark the tool as awaiting a decision (not an owner answer), stop further generation with
  SDK abort and await idle, then report a settled waiting outcome. The graph's separate
  owner-wait node interrupts only after that result is retained. Resume reopens the same
  saved context with the actual answer and an instruction to continue only the pending
  operation. An unconfirmed abort/idle or lost result is uncertain, not permission to
  invoke again. Existing SDK/tool tests and fixture provider can exercise this exact seam
  without a real paid call. This is an implementation assumption with a defined test,
  not a claim that the current host already supports durable pause.
- The parent bridge currently has one active steering target and one question. Change
  target storage to a map keyed by task/invocation/session for an authorized wave. Serialize
  owner questions through the existing tools, preserving their request IDs and owner-only
  distinction. No broadcast steering or automatic consent. Routine updates remain
  `triggerTurn: false`; questions and terminal completion can wake the parent.
- `sessions.py` already rejects nonidle, incompatible and reviewer reuse. Preserve this
  selection policy, not a new session inventory. A session cannot serve overlapping calls.
  `metrics.py:interval_record` qualifies continuous exclusive before/after deltas; reuse
  it rather than export `getSessionStats()` cumulative totals.

**Checks before reliance:** Actual graph + adapter + SDK fixture provider + temporary Git
repository: manual wait, worker question, process reopen, answered/denied operation,
uncertain-call stop, commit-before-history failure, disjoint fork/join, unrelated staged
bytes, and check/hook failure. This is the smallest composed boundary that can observe
replay, path custody and answer consumption. Pure graph mocks cannot establish those
outcomes. Keep tests in their coherent delivery outcomes; no mandatory prototype chain.

## Metadata-only LangSmith submission

**Owner constraint:** only opaque identities, hierarchy, role/model, safe outcome/category,
elapsed time and known invocation-local usage/cost may leave the process. No prompt,
response, tool payload, private path, raw error, event or incidental environment metadata.

Sources inspected:

- [Annotate code](https://docs.langchain.com/langsmith/annotate-code), “RunTree API”:
  supports explicit root/child relationships. Manual RunTree is usually less convenient
  than `traceable`; unlike automatic tracing it posts even when `LANGSMITH_TRACING` is off.
- [Mask inputs and outputs](https://docs.langchain.com/langsmith/mask-inputs-outputs),
  “Hide inputs and outputs” and “Hide metadata”: IO hiding leaves metadata; client
  metadata filtering is separate. These controls alone are not complete privacy.
- [Log LLM calls](https://docs.langchain.com/langsmith/log-llm-trace), “Provide token and
  cost information”: numeric usage can live on the run independently of output messages.
  No need to send messages for the required metadata visibility.
- Exact LangSmith 0.14.17 wheel source: `client.py:Client.__init__` has public
  `omit_traced_runtime_info`, `hide_inputs`, `hide_outputs`, `hide_metadata` options.
  `_insert_runtime_env` returns immediately when omission is true; otherwise it inserts
  runtime and environment metadata. `create_run` and `update_run` both pass through
  client transformations. `run_trees.py:post/patch` call client methods; replicas are
  additional destinations. This is why defaults and an environment toggle are insufficient.

**Decision (derived):** One explicit adapter constructs safe RunTree chain spans for
run→task→invocation, and posts only when scoped upload authority and selected endpoint/
project are present. Use a dedicated Client with `omit_traced_runtime_info=True`, IO hidden,
closed metadata filtering and explicit single-endpoint credentials; no replicas, ambient
tracing callbacks, attachments, raw exception recording or provider wrappers. Wrap graph
execution in `tracing_context(enabled=False)` so ambient graph tracing cannot export state;
explicit safe RunTree submission is the sole enabled path. Use fixed span names; map any
user-supplied IDs to opaque UUIDs rather than trust arbitrary task/run/session strings.
No raw task descriptions or Git paths in names/tags. Chain spans can show known numeric
usage/cost as approved metadata without claiming LLM message/playground functionality or
estimated server pricing as an invoice. Retain field-level unknowns locally; omit unknown
numeric values on upload.

**Observable checks:** Intercept final HTTP requests from the real selected SDK (not only
our mapper) with private sentinels in task names, state, session paths, exceptions, tool
payloads and ambient LangSmith/LangChain metadata. Inspect creation, update and failure
paths plus headers/URLs for unintended payload leakage. Disabled authority must cause
zero network requests even if ambient tracing is enabled. Fail initialization/submission
and show safe task/checkpoint completion with a visibility-gap diagnostic. Check hierarchy
and known/unknown usage. Do not add redaction services or a durable upload queue.

**Still NOT VERIFIED:** Installed transitive compatibility, actual safe request bodies,
Pi question pause behavior, graph recovery/concurrency, and live UI visibility. These are
implementation acceptance work. No LangSmith account API was contacted. Account/project,
region/access, pricing and network/upload approval are later gates. Local sentinel checks
must pass before live use; a real visible approved invocation must pass before monitor
removal. Missing upload access is not a blocker to local graph work.

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
