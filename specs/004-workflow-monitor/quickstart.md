# Planned monitor validation/operator guide

**Not delivered commands or test results.** Application/tasks/setup/implementation approval do not exist yet. Canonical details: [API/privacy](contracts/monitor-v1.md), [REQUIRED proofs/admission](contracts/validation.md), [record mapping](data-model.md), [version-specific usage cookbook](research.md).

## Prerequisites in order

1. Parent inspects architecture and routes **small reference-based reviewer prerequisite** into concrete source/task/current approval. Independently validate/accept before app build; no limit increase or active-runtime mutation. Preserve full original-range independent review, actual verified referenced-document reads, all REQUIRED/gates/custody. Exact scope/proof in [plan](plan.md#small-prerequisite--reference-based-independent-review).
2. Review the four app tasks independently; preserve every SC check/version/args/pass/evidence/dependency/gate. Sol/medium is intent, not permission. Scoped operator setup approval is separate from final app implementation authority; obtain final current-content app approval only after the real launch pins/source hashes in step5 are complete.
3. BEFORE final app binding/start, under separately explicit dependency/setup/network authority, the operator resolves the already-selected exact direct versions into reviewable external locks/installed Python/frontend/test environments, audits licenses/advisories and verifies actual Node/Chrome/Playwright/containment. Freeze dependency inputs in enforced read-only custody; no app source/config/helper is prepared outside runner. Follow [concrete descriptor/binding recipe](contracts/validation.md#pre-admitted-dependency-inputs-and-launch-binding), not question/answer delivery. Worker later writes exact direct manifests and all app source DURING this build; tests only generate approved writable scratch.
4. Before first app run, committed retained raw-hash config and public presentation sources carry v1 markers. Verify workflow canonical digest against **actual** `wf_run_bindings.config_hash`, not combined Engine hash; preserve Git objects. No old-run conversion.
5. Prepare immutable external `TMPDIR/monitor-inputs.json` and fill the two launch pins below from its actual raw bytes/fresh preselected app run ID. Refresh this source's raw hash in tasks.json and affected canonical scopes; obtain current-content final review/approval and genuine external catalog/config/SDK/local-resource/cgroup/mode readiness. Start actual shipped CLI with that exact fresh `--run` ID and inherited TMPDIR; accepted adjusted runtime/inputs stay unchanged throughout build. No fabricated approval, event or future receipt. No migration IDs, hand implementation or unfinished-viewer prerequisite.

## Prelaunch pins — intentionally unresolved

```text
monitor_inputs_sha256: UNRESOLVED
monitor_app_run_id: UNRESOLVED
```

These exact lines are consumed by worker-written `workflow_monitor/tests/setup_inputs.py` and pinned through this existing quickstart source in the immutable admitted contract. They are NOT currently executable launch input: fill with actual descriptor raw SHA256 (64 lowercase hex) and fresh preselected CLI run ID only after authorized setup, then refresh source hashes/review/approval BEFORE binding/start. No fake values or new artifact required. Descriptor excludes this document/task/final-approval hashes, so no cycle. Its exact canonical project/run/source/config/tool/lock/tree/fixture bindings are checked against real read-only stores. At each check the expected descriptor hash must come from this source as pinned in actual `wf_run_inputs.contract.sources`, not descriptor self-attestation. A preselected ID does not establish any runtime event.

Keep `request_owner_input`/CLI answer/resume only for genuine product-priority/unexpected-material-change questions, never anticipated technical setup or approved tests; genuine answers are separately capped at16384 UTF-8 bytes.

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
