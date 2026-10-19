# Implementation Plan: Read-only Workflow Monitor

**Branch**: `follow-attached-workflow-migration-instructions` | **Date**: 2026-10-19 | **Spec**: [spec.md](spec.md)

**Input**: renewed approved specification SHA256 `f8c8040942a509f5d62fa2f4d21b5bdf3de4c6c424eeaf644a28a091ca4e3f55`; [approval](specification-approval.md). Architecture baseline `b12d0145e55947311707d933710d021547653712`. Standard preparation only; tasks/independent overall review/final implementation approval pending.

## Summary

Separate worktree-local read-only observer: selectable runs left, **one execution graph for the selected run** right, safe brief details. React Flow supplies maintained interaction/accessibility; ELK supplies organized layout. Starlette/Uvicorn serves production assets and explicit versioned minimized JSON from short read-only SQLite snapshots. No scheduler/controller/SDK/effect/repair seam.

New monitoring-contract runs only, including **THIS actual app build**, retrospectively and live once usable. Older runtime-migration runs excluded by renewed owner direction; no adapter/import/archive/fallback. Preserve all new completed/failed/recovered/same-spec histories and every SC-001–006. Planning chat/fixtures/different demonstration cannot substitute for own build.

## Technical Context

**Language/Version**: Python3.12, browser JavaScript/JSX, build Node22.23.3 observed.

**Primary Dependencies**: agent-derived under owner delegated community-use/documentation criteria: React/ReactDOM19.3.1, @xyflow/react12.12.0, elkjs0.12.0, Vite8.3.4; Starlette1.9.0/Uvicorn0.54.0, separately pinned PyYAML6.0.3. Proposed browser test Playwright1.64.1 against installed Chrome; actual usability NOT VERIFIED. [Research](research.md) owns attributable adoption, exact-version official guidance, alternatives, APIs/pitfalls and checks. Exact locks/advisory/license/setup validation pending, no installations now.

**Storage**: viewed-worktree SQLite schema1 sole authority; retained Git-addressable config/presentation pins; bounded sanitized in-memory snapshots. No new runtime DDL, persistent app DB, browser storage or projection publication.

**Testing**: permanent focused production-helper fixtures, actual isolated shipped-runtime composition before UI reliance, real DOM/browser checks, SAME own-build retrospective/live evidence. All implementation tests NOT RUN. [Validation contract](contracts/validation.md) preserves REQUIRED criteria, evidence, dependencies and gates.

**Target Platform**: numeric127.0.0.1 local Linux trusted single-host/same-UID operator; modern browser with Fetch Metadata. Browser-origin defenses, not user authentication/malicious-local-client isolation or remote/multiuser deployment.

**Project Type**: separate ASGI/static web application, no execution API.

**Performance Goals**: normal about2s update target; initial1000ms polling/one in flight, stable selection/viewport, finite anchors and explicitly revealable history windows, cancelable ELK worker. No invented percentile/throughput promise.

**Constraints**: all worker-managed source/tests/docs/config/lock files **strictly <32768 UTF-8 bytes** by owner direction; SDK transport262144 unchanged. Small reference-based reviewer adjustment precedes app build, independently accepted under separate concrete task approval. No runtime mutation during its own app build.

**Scale/Scope**: one worktree, multiple new eligible runs, selected run only; shipped19 nodes are baseline, never hard-coded inventory. Every pinned node and recorded visit remains accessible, including finite unvisited loops, repeats, non-task stages and unsupported records.

## Constitution Check

*Checked before Phase0 and again after Phase1.*

| Principle | Disposition |
|---|---|
| I portable assets | PASS: project app/research owns local specifics; no global changes |
| II evidence | PASS: actual record/identity/replay source and official versioned documentation; unknowns/counterevidence retained |
| III authority | PASS: genuine specification renewal; technical selections delegated, not owner-picked brands. Subsequent small prerequisite direction is planning scope, not code authorization |
| IV proportionate checks | PASS: smallest helpers/composed/browser observables, no disposable prototype/report chain or unrelated exhaustive matrix |
| V safe execution | PASS design: one runner writer, real REQUIRED/gates, focused commits and fresh full-range independent review preserved; exact future admission still required |
| VI ownership/compatibility | PASS: only explicitly narrowed older compatibility; no memory/STATE/feedback writes or history erasure |

No exception/waiver. Design validation is not runtime/application acceptance.

## Project Structure

### Documentation (this feature)

- [research.md](research.md): canonical dependency/source evidence and version-specific implementation cookbook.
- [data-model.md](data-model.md): identities, graph/replay/task/status/metric mapping.
- [contracts/monitor-v1.md](contracts/monitor-v1.md): exact read seam, pin proof, SQL fields, HTTP/DTO/privacy/origin/interaction contracts.
- [contracts/validation.md](contracts/validation.md): REQUIRED proofs, byte/reference prerequisite, capability/custody and own-build gates.
- [quickstart.md](quickstart.md): future validation/operator sequence; [contract index](contracts/README.md).

No tasks generated by plan stage. These owners avoid copying the entire requirements/API/cookbook into each document.

### Source Code (proposed, not created)

```text
workflow_monitor/
├── __main__.py / app.py            # fixed CLI/ASGI/closed boundary
├── reader.py / pins.py             # read-only snapshots/actual config pins
├── mapping.py / public.py / schemas/
├── pyproject.toml / requirements.lock / README.md
├── web/
│   ├── package.json / package-lock.json / vite.config.js
│   ├── src/                       # run list/one graph/details/ELK worker
│   └── tests/                     # real browser assertions
└── tests/                         # permanent helpers/fixtures/composed tests
    └── acceptance_*.py            # bounded registered PythonAnswer entrypoints
```

**Structure Decision**: app outside active runtime package. No runtime/config/schema/host/skill edits during app build. Sensible modules and file-byte guard, not larger read/write/ranged tools. Required retained source/locks/config stay under runner custody/full review. Build/venv/node_modules/test output live in explicitly owned isolated environment/scratch, not Git or observer-created files. A test check cannot generate retained worktree artifacts.

## Phase 0 — research and decisions

[Canonical research](research.md) completed before consequential design. Official tagged archives/docs successfully replace failed website403/DNS retrieval, not recollection. Maintained graph renderer+layout selected after owner's organized-interaction concern; adoption is not correctness proof. Backend framework chosen over custom HTTP burden, not dependency-count preference. Loopback no-token same-origin design accepted for pursuit under delegated backend choice, final plan approval pending.

Concrete hardest seam: actual pinned SQL semantics→complete minimized DTO while writer runs. Use smallest real production-reader/shipped-runtime composition before UI reliance; permanent helper tests for known bounded mapping. No mandatory prototype chain. Preserve proof/counterevidence through consumers; failed/unrun proof blocks reliance.

Residual dependencies: SDK OI-3 remains restricted-host reachability residual, not clearance; app cannot expose SDK package/default/glob/model-scope APIs. Official WAL-reset advisory includes observed SQLite3.45.1; observer never writes/checkpoints and cannot certify existing runtime writer arrangement. No silent upgrades; actual environment/advisory/setup assessment remains required.

## Phase 1 — architecture

Detailed invariants live in linked owners, not repeated prose:

1. **Pins**: uniquely marked kind=config workflow/presentation sources, full raw SHA, retained committed bytes; strict YAML canonical digest must equal actual SQL `wf_run_bindings.binding.config_hash`, not combined `wf_runs.config_hash`. No unrelated config declaration/current-YAML fallback/runtime archival/launch wrapper.
2. **Identity**: finite definition anchors, graph-op UUID visits, SDK turns and semantic records separate. Reconstruct/verify Engine trace-prefix args hashes before asserting execution transitions; prerequisites never execution order. Owner-input can interrupt before gate operation intent: semantic park, no invented visit. Unknown records remain opaque accessible evidence.
3. **Status**: separate worker-finished/verified/committed/review-head/finally-accepted badges; historical failure stays red after recovery. Running blue only with controller/operation facts; waiting/blocked amber labelled distinctly; missing evidence warning not red failure. Accepted input/delivery/continuation-entered/request-start distinct. Nulls/zero/superseding revisions/four binding provenance classes preserved.
4. **Read/privacy**: fixed existing canonical DB, mode=ro/query_only/authorizer, bounded short thread-owned snapshot closed before network. No Authority/saver/Publisher/controller/DDL/checkpoint/repair import. Only allowlisted minimized DTO; reviewed pinned brief labels, never arbitrary outcome/question/approval/tool/finding text. Errors/logs/links/assets included in exclusion, no raw file gateway.
5. **HTTP/trust**: closed GET routes/static production asset manifest; numeric127.0.0.1 and exact bound Host:port, no proxy/debug/reload/websocket. Same-origin custom API header/Fetch Metadata/Origin checks, no CORS/cookies/persistent auth UX. CSP protects script/connect/worker/frame boundaries; library geometry style attributes explicitly permitted, never stored executable content. Not malicious-local-client authentication.
6. **Graph**: maintained click/keyboard node+edge selection, details/pan/zoom/find/reveal/collapse/organize only, all editor/control actions absent. ELK Worker handles measured nodes/compound coordinates/cycles on copy; no changed domain edges. Stable IDs, topology/status revisions, no poll relayout/refit, discard stale run-generation results. Hidden red/amber counts + finite windows + explicit inventory ensure every visit reachable in the same graph. Narrow screens use rail/detail drawer, not competing task/workflow views.

## Small prerequisite — reference-based independent review

Owner directed “referencing files rather than copying” and keeping all worker files below32KB, then authorized planning the small change and continuation. This is **not approval to implement it now**.

Actual `ReviewRepair.bundle()` always embeds full source/approval bytes plus whole task contract, repeated task contracts in receipts, full original-range binary patch, evidence/findings. Existing `Coordinate._tools(review=True)` already authorizes reads of source/approval/owned paths; `intake.admit` rechecks immutable raw source/approval hashes, safe paths, current scope and authority. Therefore retain this mechanism and remove redundant embedding, not raise120000/262144 constants or introduce a generic artifact platform.

Narrow planned change:

- Replace source/approval **content values** in review prompt with exact authorized `{path,sha256,kind/section or approval role, revision where available}` references from current admitted contract. Complete inventory remains; no omitted required context. Keep current contract/approval validation at actual read and acceptance.
- Reviewer must actually obtain every required referenced document through existing read_file. Read bytes once, validate file identity/strict UTF-8 byte bound/raw pinned hash on those same bytes, and return exactly that content (no separate hash-then-reread race). Bind a minimal read receipt (path/ref, raw content hash, read process operation and originating review host/turn) to actual returned bytes; audit required receipt coverage for that independent review before accepting result. No transcript/raw content ledger, generic tool or authority relaxation. Missing/stale/wrong-host/unread reference blocks.
- Remove redundant per-task contract copies from receipts only where exact canonical task hash/reference to the already supplied authoritative contract proves identity; preserve all task states/checkpoint/evidence/gate/finding content and dynamic correction contracts not already represented.
- Enforce **<32768 UTF-8 bytes**, not Python-character/JSON-schema character count, for worker reads/writes and source/approval/doc admission; reject before filesystem effects without partial writes. Current code admits exactly32768 and write schema counts characters. No append/chunk/limit increase. Guard actual final file set; sensible modules; actual unavoidable lock-size issue returns evidence, never speculative blocker or format splitting.
- Preserve full original base→current-head patch, source→task/REQUIRED review, original authority/custody/protocol and final-current acceptance. Measure remaining actual contract/receipt/diff overhead separately; unchanged bounds still block genuinely oversized final payload. No speculative streaming/patch platform.

Validate with permanent focused actual-helper tests: unchanged full-range patch/evidence; all referenced bytes actually read; changed/deleted/unsafe/unread/wrong-review sources reject; unrelated source not authorized; multi-byte/exact-bound reads/writes reject; small complete review succeeds; final bundle measured. Composed shipped-runtime review verifies these guards precede acceptance. No mock-only claim for actual tool receipt chain.

Parent routes this prerequisite into concrete reviewed source/task/current-approval scope and drift-safe execution, independently validates/accepts it **before** fresh app build. Accepted adjusted runtime then stays unchanged throughout SAME app build; no app code staged outside runner or split-demo workaround. No larger-file tooling or broad runtime redesign.

## Ordered delivery stages (not task IDs)

1. **Accept narrow review-reference/byte-guard prerequisite** as above under proper separate scope/current approval. Refresh affected runtime acceptance/config/resource identities; preserve all gates. No implementation in this planning pass.
2. **App admission and real read seam**: finalize approved immutable config/presentation/task inputs, exact setup/capabilities/byte/payload checks; implement read/normalize/minimize and permanent fixtures + actual isolated noninterference/pin proof before UI reliance.
3. **Usable selected-run graph**: production API/assets, measured React Flow/ELK, safe details/read-only navigation/polling; basic browser/origin checks. Early usable checkpoint allows operator-owned read-only viewer while SAME build proceeds.
4. **Full history/security/freshness integration**: all source-required repair/question/recovery/review/metrics/unknown/large-history/adversarial cases, real runtime and browser proof. Keep tests/evidence/ordinary teardown with each coherent outcome; genuine remaining work supplies live interval, no busywork.
5. **Own-build acceptance and docs**: retrospective + live same app run, retained failures, exact source/config/checkpoints/observations, aligned operating/API/setup docs and fresh full-original-range independent review/current final acceptance. Completion is not acceptance.

One runner writer/checkpointer; worker never Git/select work. Independently operator-owned observer is not a task descendant left alive at settlement or task coordinator. If live SAME-build evidence missing, SC-006 NOT VERIFIED; no separate demo substitute.

## Executor and handoff

Preserve root intent: `model_class:Sol`, `effort:medium`, `resolution:resolved`, compatible target `openai-codex/gpt-6.1-sol:medium`; owner provenance “use6.1 sol medium”. Assessment: current restricted observer supports only this exact binding; fresh usable SDK/auth/resources/tools/effort still required. Assumptions/scaffolding: named seams/status/privacy/proofs/dependencies explicit, routine component/file choices open. Outcome-oriented decomposition, no artificial microtasks; class/effort change needs affected compatibility review, no silent escalation/fallback.

Planning six factors: coupled history/privacy/status inference; bounded stateful tools; weakest adequate oracle semantic/security coverage not generic green; one UI/backend seam; reversal preserves records/runtime authority; no approved coordination guidance/benchmark reliance. Sol explicitly selected versus plausible Terra/medium, no established comparative superiority; medium required, empirical benefit over low unclaimed. Selected/observed env exact Sol/medium matched, provider acknowledgement unknown. Actual three local skills/hash bindings verified; six config paths are candidate resources, not six loaded bodies.

Separate fresh task producer inherits [whole REQUIRED contract](contracts/validation.md), not source-pointer-only acceptance: exact registered check/version/args/pass/evidence/producer/gate maps. Existing PythonAnswer executes explicitly trusted project helpers under concrete scoped test authority, no arbitrary selector/shell/install backdoor and no retained worktree generation. Exact dependency/lock/file/custody/browser admission required, ordinary stop gates not owner-choice ceremonies.

## Documentation, rollback and stage review

Future app README owns launch/trust/limits and app schema/API owner matches actual DTO. Root README/REQUIREMENTS/runtime owners updated only for actual affected facts under task authority; docs/index gets bounded discovery now. No global setting/install/reload, STATE/memory/feedback record.

Rollback stops viewer only; preserves DB/WAL/private records/Git/partial work/unrelated history; no control/DB downgrade/projection rebuild/reset/legacy restart. Runtime prerequisite rollback/release is separately reviewed, never observer effect.

## Complexity Tracking

No constitutional exception. SQL read adapter, minimized DTO and layout worker serve actual completeness/privacy/responsiveness failures. No registry/platform/scheduler/prototype chain.

## Plan-stage evidence

Followed actual `.pi/prompts/speckit.plan.md`1.0.12/pi/sequential. `setup-plan.sh --json` ran ONCE before interruption, copied real template to004; logical BRANCH004 did not switch Git branch. Revival reused retained pass after inspected timeout, no stage/research replay. Research→entities/contracts/quickstart→post-design constitution review completed; pre/post extensions.yml absent, no hooks. Specification correction separately committed/renewed, approved bytes unchanged since. Actual draft/link/size/FR-SC/manual review and focused checkpoint reported in return. Application/runtime/browser proofs NOT RUN; independent overall planning review/final approval pending.
