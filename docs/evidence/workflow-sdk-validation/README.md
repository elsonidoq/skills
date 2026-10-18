# Disposable official Pi SDK-host probe

Not production code, architecture approval, migration implementation, or stack reselection.
Python is the deterministic caller; Node holds one Pi conversation and reports facts. No
LangGraph/SQLite authority is moved into Node. B/C remain NOT RUN.

## Reproduce (authorized toy checkout only)

Requires Node 22.23.3 (tested), Python 3.12.3, installed official
`@earendil-works/pi-coding-agent`, `pi-ai`, and `pi-agent-core` **0.87.1**, and an already
ready OpenAI Codex OAuth credential with >10 minutes validity. No installation is needed.
The host requires explicit installed-package resolution, not a shipped global path.

```sh
# Set these to your existing read-only installation/inputs; never print credential contents.
export PI_SDK_ROOT=/absolute/path/to/node_modules/@earendil-works/pi-coding-agent
export PI_AUTH_PATH=/absolute/path/to/existing/auth.json
export PI_MODELS_STORE_PATH=/absolute/path/to/existing/models-store.json
export PI_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
mkdir -p .pi/workflow-validation/sdk-poc/tmp
export TMPDIR="$PWD/.pi/workflow-validation/sdk-poc/tmp"
export RECORDED_ROOT="$PWD/.pi/workflow-validation/sdk-poc/reproduction"
# Root MUST NOT exist. Logs must be a new scratch directory, not retained original logs.
python3 docs/evidence/workflow-sdk-validation/poc/controller.py run \
  --root "$RECORDED_ROOT" --logs "$PWD/.pi/workflow-validation/sdk-poc/reproduction-logs"
python3 docs/evidence/workflow-sdk-validation/poc/controller.py status \
  --logs "$PWD/.pi/workflow-validation/sdk-poc/reproduction-logs"
node docs/evidence/workflow-sdk-validation/poc/test-settings.mjs
python3 docs/evidence/workflow-sdk-validation/poc/test_controller.py
```

`status` only reads JSON; no Node/model/conversational coordinator. The recorded-evidence
test targets the retained original logs and requires `RECORDED_ROOT` to name the original
scratch run (`run2` here), not a new reproduction. It deliberately also checks actual files
and recorded `/proc` process identities rather than trusting narrative success.

Only model `openai-codex/gpt-6.1-sol`, effort `medium`, is accepted. The exact model is in
the existing cached catalog, **not** the SDK's bundled static catalog. The catalog is read
into a private in-memory `ModelsStore`; model metadata is not invented or rewritten. OAuth
is read using exported `readStoredCredential`; custom `CredentialStore` forbids refresh,
logout, and persistence. Expiry blocks instead of refreshing shared credentials. SDK
`modelsPath:null`, scratch `agentDir`, explicit resource loader, in-memory settings,
`PI_OFFLINE=1`, and cache warming off prevent unintended configuration/catalog writes.
This does not sandbox arbitrary model-generated tools.

## Tiny wire contract

UTF-8 LF JSONL, `v:1`, string `id`. Commands: `init`, `prompt`, `abort`, `status`, `close`,
and explicitly synthetic `synthetic_guard`. Example init:

```json
{"v":1,"id":"init","op":"init","provider":"openai-codex","model":"gpt-6.1-sol","effort":"medium","skill":"/absolute/to/poc/toy-skill","tools":["write"]}
```

`response` is ID-correlated acceptance, **not** completion. Subscribe before `prompt`;
`event` contains only selected lifecycle/tool names. `settled` is emitted after awaiting
SDK `session.prompt()` **and** `waitForIdle()`, with an explicit success/stop reason.
Low-level `agent_end` is never used as completion. Abort has its own response after
`session.abort()` and `waitForIdle()`. EOF, invalid version, unavailable facts, errors and
unknown settlement never permit the controller's next writer. Timed waits are 90 seconds,
provider timeout 30 seconds, retries zero. Tool loops self-limit to 12 seconds and request a
15-second bash timeout. Status/close remain available after poisoning.

The line-size rejection is after readline framing (16 KiB), not a hardened streaming
allocation bound. Trusted single-caller protocol only: no replay protection, comprehensive
schema/ID deduplication, arbitrary-client concurrency guarantees or production security.
The Python controller drops unmatched queue events from its wait queue but retains every
record separately; settlement records are emitted after prompt acceptance in this host.

## What the guard actually proves

Public `Agent.streamFunction` is wrapped, preserving the SDK stream function and invoking
existing `options.onPayload` (or SDK `agent.onPayload` for summary routes) **before** final
validation. Official provider code invokes `onPayload` after reasoning mapping and before
serialization/transport. Host validates requested provider/model and final body
`model`/`reasoning.effort`; only those sanitized fields are logged. Real mapping here is
`medium → medium`, **not** a conclusion from the model suffix.

A `before_provider_request` extension first transforms payloads; a second deliberately
throws in the synthetic case. SDK swallows that extension exception. The host's guard
throws **outside** that runner, producing an error assistant response, no task file, and
zero calls to an instrumented synthetic transport. A separate synthetic summary-route
call uses the real SDK stream function/provider request builder with no per-call
`onPayload`; it is also guarded. No official source is patched. This is not a real
compaction/overflow/retry burn; those route semantics have source provenance in the report.

## Lifecycle safety boundary

Normal abort kills the real standard bash process group, settles, and is checked against
previously observed `/proc` PID **and start-time** identities, process-group membership,
and a 0.6-second stable-file window before a deterministic replacement writer is admitted.
SIGKILL of the host **does not stop its detached bash child**: the experiment observed
continued writes. The independent Python supervisor records actual descendants/PGID before
host death, checks an unchanged owned identity remains live, kills that group, confirms
non-zombie processes drained and partial bytes stable, then admits a replacement.

Only bounded same-group descendants are tested. Escaped process groups, containers,
remote tools, reparented unknown identities, malicious children, power loss, cross-host
recovery, resumed Pi sessions and workflow exactly-once are not proven. Unknown ownership
or drain blocks; do not infer quiescence from a dead host or checkpoint alone. Zombies are
non-writing and excluded from live checks. No broad sandbox claim or automatic task replay.
