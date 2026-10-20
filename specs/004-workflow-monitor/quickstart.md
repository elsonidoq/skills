# Planned monitor validation/operator guide

**Not delivered application commands or acceptance results.** Four app tasks are unchanged. The owner authorized archive-and-fresh-Sol launch after runtime fixes; exact external authority binding and live readiness remain required. Isolated setup and supplemental runtime fixtures exist; they do not certify the app. Canonical details: [API/privacy](contracts/monitor-v1.md), [REQUIRED proofs/admission](contracts/validation.md), [record mapping](data-model.md), [version-specific usage cookbook](research.md).

## Prerequisites in order

1. Reference-only precursor was independently accepted at `73dbaad0030c36245b078a18d9e33c9de987a6e1`. Subsequent owner-authorized inventory/preflight fixes through `97935288f857d430d022ab25dacc681a3ae30133` passed 167 available nonlive tests; parent inspected code and reran all 22 inventory tests. Full mandatory/live suite is NOT claimed. Freeze the current runtime throughout this new app execution; retain all REQUIRED/custody/review gates.
2. Preserve the independently reviewed four tasks and every SC/check/version/args/pass/evidence/dependency/gate. The actual owner selected **Archive old state and launch fresh Sol build**, authorizing only reviewed runtime-source/launch-binding renewal and this unchanged Sol/medium plan. Bind that genuine decision through the trusted external catalog; do not relabel historical approvals or infer authority from intent.
3. Actual isolated dependency setup/audit/smoke is complete, with operational read-only inputs (write bits removed, independently pinned hashes/identities), not malicious-same-UID isolation. No app source/config/helper exists outside runner. Follow [descriptor validation](contracts/validation.md#pre-admitted-dependency-inputs-and-launch-binding); workers write exact direct manifests and all app source DURING this build, checks only declared scratch. Drift or unsafe identity stops.
4. Before first app run, committed retained raw-hash config and public presentation sources carry v1 markers. Verify workflow canonical digest against **actual** `wf_run_bindings.binding.config_hash`, not combined Engine hash; preserve Git objects. No old-run conversion.
5. Fresh descriptor/run identity are pinned below. Revalidate all hashes, exact SDK/local resources/cgroup capability and run the actual read-only CLI `preflight` before startup. Bind the actual owner archive/fresh-launch decision and reviewed source renewal to exact scopes in the external catalog. Start source-local CLI with this run ID and `TMPDIR=/tmp/coherence-monitor-inputs-q0ww12wq`. A NEW real launch/challenge/ready handshake must succeed; no old receipt, manual implementation or unfinished-viewer prerequisite. The old never-dispatched attempt was archived intact under explicit owner approval; it is not in the new live database and is not substituted as own-build acceptance.

## Prelaunch pins — actual frozen input bytes, not launch approval

```text
monitor_inputs_sha256: d12624227927a5a216c08376c55f3d030d1800c7b4fd9786c8e9ff17a6242be4
monitor_app_run_id: monitor-app-20261020-0ec48f3fe91b
```

These exact lines are consumed by worker-written `workflow_monitor/tests/setup_inputs.py` and pinned through this existing quickstart source in the admitted contract. Actual raw SHA256 and preselected ID do not grant execution: current review/approval/catalog and launch preflight remain required. Descriptor excludes this document/task/final-approval hashes, so no cycle. Its exact canonical project/run/source/config/tool/lock/tree/fixture bindings are checked against real read-only stores. At each check the expected descriptor hash must come from this source as pinned in actual `wf_run_inputs.contract.sources`, not descriptor self-attestation. A preselected ID does not establish any runtime event.

Keep `request_owner_input`/CLI answer/resume only for genuine product-priority/unexpected-material-change questions, never anticipated technical setup or approved tests; genuine answers are separately capped at16384 UTF-8 bytes.

## Actual descriptor schema and trusted consumer

The fixed file is `/tmp/coherence-monitor-inputs-q0ww12wq/monitor-inputs.json`. Read once as raw UTF-8 JSON with duplicate-key rejection; expected raw hash comes from the exact quickstart bytes pinned by **actual** `wf_run_inputs.contract.sources`, never this descriptor itself. SDK read_file cannot open it; this declared schema is implementer context for the trusted `setup_inputs` consumer, not a new model tool.

Closed root fields (schema_version=1): `purpose`, `project`, `app_run_id`, `workflow`, `runtime`, `tools`, `dependencies`, `fixtures`, `scratch`, `observer`. Exact shapes:

- `workflow={source,sha256,config_hash}` names `specs/004-workflow-monitor/monitor-workflow.yaml`, its raw hash and canonical parsed config digest. Resolve this one marked source from actual app contract, compare retained raw bytes, `wf_run_bindings.binding.config_hash` and source-list digest; Engine combined hash is different.
- `runtime={accepted_revision,suite_root,source_hashes,sdk_version}`; `source_hashes` maps checkout-relative runtime/host/schema files to raw SHA256, SDK version0.87.1. Verify current files against every entry and accepted revision9793528; later approval/binding commits need not equal that runtime revision. No future app-file hashes here.
- `tools={python,python_root,node,node_sha256,node_version,node_modules,vite_cli,playwright_package,chrome,chrome_version,chromium_sandbox_verified}`. Python is `/tmp/coherence-monitor-deps-vjwa035g/python/bin/python`; Node is `/home/dev/.nvm/versions/node/v22.23.3/bin/node` (22.23.3); Vite/Playwright resolve inside the declared node_modules; Chrome `/opt/google/chrome/google-chrome`154.0.8037.92. Boolean sandbox observation is setup evidence, not a waiver of actual sandbox checks. No arbitrary executable/env override.
- `dependencies={python_direct,node_direct,python_lock,node_lock,inventory,python_advisories,node_advisories,node_licenses,license_selection,operational_custody}`. `python_direct` maps starlette/uvicorn/PyYAML to exact versions; `node_direct` is the actual resolver package object `{name,private,version,type,dependencies,devDependencies}`. Compare worker manifest dependency intent, not its project name, to the exact dependency/devDependency maps. T001 requires Python only; T002 onward also requires frontend/test manifest. Each lock/inventory/advisory/license entry is `{path,sha256}`: verify same bytes and identity. `license_selection` records EPL2/MPL2 notice/source obligations; `operational_custody` describes write bits removed, not stronger sandboxing.
- Inventory is a2894-entry array rooted at `/tmp/coherence-monitor-deps-vjwa035g`: files `{path,kind:"file",bytes,mode,sha256}` (2885), symlinks `{path,kind:"symlink",target,resolved}` (9). Validate full declared tree/hash/identity before use, missing/extra/changed entries stop. Only enumerated symlinks are permitted, with exact targets/resolutions; Python bin links explicitly resolve to system `/usr/bin/python3.12`, lib64 to local lib, Node bin links within admitted tree. Never reject a documented interpreter link merely for being external, nor allow arbitrary escape. Tool/base-interpreter identity is revalidated; read-only prefix is python/node and frozen metadata/locks, **not** every child of the broader setup root.
- `fixtures` is four objects sharing `{kind,project,run_id,source_root,events,status,workflow_sha256,config_hash,provenance}`, with optional `tasks`, `cli_exit`, `question_stage` only as present. Kinds: `failed-check-repair`, `review-correction`, `same-spec-repeat`, `question-crash-recovery-original-continuation`. Each fixed DB is `project/.coherence/workflow/workflow.sqlite`; use real `wf_run_inputs`/bindings, baseline/checkpoint/source pins and typed events, not the descriptor's counts/status as proof. First and repeat share the SAME fixture project/spec but have distinct run IDs. Config/presentation pins must resolve from each actual fixture contract; no invented alias or production approval. Fresh controlled crash/question fixture is test-only CLI authority, NOT human ask_user consent. All four are supplemental inputs, never SC-006 own-build acceptance or active-writer proof by themselves. Mutable runtime observations are not dependency inventory entries; do not edit fixtures.
- `scratch={root,assets,results,fixture_projects,browser_tmp}` names only writable children of `/tmp/coherence-monitor-inputs-q0ww12wq/work`. Descriptor/root is operationally read-only, this work child writable. Explicitly set `tempfile.tempdir=scratch.root` (or pass dir on EVERY tempfile call); child fixed env `TMPDIR=scratch.browser_tmp` or an explicit declared work child. Never default to inherited descriptor-root TMPDIR, HOME, worktree caches or generic /tmp. Use explicit results/build/browser paths; fixed shell=False argv, bytecode off, no installs/download/network or dependency writes. Copy current owned frontend/test/config bytes to scratch and bind hashes; scratch-only node_modules link points to declared tree. Close/drain all check descendants within existing15s bounds.
- `observer={project,run_id,start_after_task,authority}` binds this app run, T002 then independently operator-owned read-only viewer; no scheduler/control or task descendant. Live interval and acceptance do not exist yet.

The separate private operator control root holds SDK manifest/parent-binding/catalog inputs; it is **not** a fixture project, approved browser data or oracle-readable dependency input. Do not open auth/catalog/session conversations. Actual interactive-parent config is explicit (paseo-0.9.2/ask_user, fresh parent binding); no standalone/manual-poll default. Parent metadata was probed read-only successfully; genuine run-bound challenge/launch/ready tool receipts remain mandatory before dispatch.

Custody is trusted single-host/same-UID operational read-only: write bits removed plus independently expected hashes and canonical identities; revalidate descriptor/tool/lock/full-tree bytes before use. Model file tools cannot write these external paths. Trusted project-code tests are scoped, not adversarial filesystem-sandboxed; chmod/hash checks cannot defeat malicious same-UID/root races. Any drift/missing/unsafe identity stops, never silently refresh pins during execution.

## Intended delivered commands

Application README must confirm exact supported flags/owned paths before use:

```sh
# After validating the frozen descriptor and current worker manifests/source:
# copy CURRENT owned web/test/config bytes into approved scratch; bind source hashes.
# Scratch-only node_modules links the admitted immutable tree; no worktree link/install.
# Actual paths/argv come from validated descriptor, not arbitrary environment input.
"$APP_NODE_ENV/node_modules/.bin/vite" build "$SCRATCH_WEB_SOURCE" --outDir "$OWNED_ASSET_OUTPUT"

# Separately operator-owned read-only viewer after early usable checkpoint:
"$APP_PYTHON" -B -m workflow_monitor --project "$CANONICAL_WORKTREE" \
  --assets "$OWNED_VERIFIED_ASSET_OUTPUT" --port "$LOOPBACK_PORT"
```

Verify asset manifest/hash/identity, use exact printed numeric127.0.0.1 origin. No token/cookie/persistence ceremony; APIs require same-origin Fetch Metadata/custom header. Observer never builds/installs/starts execution. A task/check-owned viewer/browser must settle/drain before its check exits; independently operator-owned observer can remain open while SAME app run continues.

## Validation sequence

### Before UI reliance

Run permanent production-reader/mapper tests against source-derived actual-definition inventory, not a chosen route: changed YAML inventory, shipped19-node cycles, all repeated/non-task/terminal/unvisited visits, trace hashes/typed edges, unsupported records, null/zero/revision/binding provenance. Unrelated config source fails actual binding proof.

Then actual isolated shipped-runtime + reader/HTTP composition: current authoritative records while controller writes, no viewer SQL/control/model/process effects or projection publication, bounded read snapshots and controller noninterference. Compare causal records/quiescent fingerprints, not naive byte equality of a writing DB. Test-only authority must be genuine through shipped interfaces, not fake production approvals. Failed/unrun proof blocks dependent reliance.

### Browser graph and safe output

Use actual measured DOM/ELK: keyboard/click node **and edge** detail selection, non-overlapping organized cards, preserved original cycle/multiedge endpoints, distinct possible/recorded/prerequisite/semantic connectors. Run A→same-spec B replaces graph. Hidden failed/waiting counts and find/reveal reach every visit in one graph; narrow rail/detail drawer, no competing task view/editor/control buttons.

Status refresh preserves viewport/selected ID/existing positions; stale worker from old run discarded. Real source/display observation pairs show normal about2s, retain deviations; forced read/stale/controller loss warns with last success, not fake progress. Actual failure→repair, interruption→reconciliation, question→accepted→entry-delivery→continuation/request, review→correction→rereview keep all milestones/history distinct.

Sentinels in private fixture payloads/paths/errors/tool/check/approval/question/finding text must occur in **no response/header/log/asset/link**. Safe approved adversarial text cannot execute. Foreign origin/Host/Fetch-Metadata/preflight/write methods/traversal/duplicate cursor/frame requests reject before data access. Test actual500 response and logs. CSP supports graph geometry styles, never stored HTML/script/URL.

### SAME actual app build

Retain real build run ID/raw pins/canonical config binding/baseline/checkpoint/range and failures. At early usable graph checkpoint, operator opens that run and inspects its earlier build steps, then observes genuine later work of **that same run** live before final acceptance. Capture source/display timing tied to ID. Additional real isolated/same-spec/completed/failed/recovered runs supplement, never replace it. No planning-chat import/old migration/clean demo. If live own-build interval absent, SC-006 NOT VERIFIED.

## Reporting and disable

Use [REQUIRED matrix](contracts/validation.md) for each SC PASS/FAIL/NOT VERIFIED and actual command/args/version/environment/evidence/permission/manual gate. Positive collection/no skips; missing browser/authority/setup/real integration is NOT VERIFIED, generic green insufficient. Shared checks retain every mapping; ordinary teardown/evidence stay with coherent delivery.

Stop only viewer to disable. Preserve runtime DB/WAL/private evidence/Git/history/partial work; no pause/cancel/control/repair/downgrade/projection rebuild/reset/legacy restart. Prerequisite runtime changes require separate reviewed/accepted scope, never monitor repair.
