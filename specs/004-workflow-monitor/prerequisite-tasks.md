# Tasks: Workflow monitor — small runtime preparation precursor

**Input**: approved app specification; derived plan's Small prerequisite section and subsequent owner technical direction. **Origin**: Standard; `legacy_origin: null`, `schema_version: 1`.
**Authoritative machine contract**: [prerequisite-tasks.json](prerequisite-tasks.json), the ONE adjacent JSON carrier. This human contract preserves its task/order/dependency, intent, ownership, whole REQUIRED mappings and gates.
**Status**: create-only planning draft; NOT operationally admitted, NOT implementation permission, NOT a CLI-dispatched runnable contract. One logical precursor delivery, no app tasks produced here.

## Source identity and authority

All hashes are raw SHA256 of complete files; sections select relevance, not partial hashing.

| Kind | File / selected section | SHA256 |
|---|---|---|
| spec | [spec.md](spec.md): FR-016/017, SC-006; acceptance/executor gates | `f8c8040942a509f5d62fa2f4d21b5bdf3de4c6c424eeaf644a28a091ca4e3f55` |
| plan | [plan.md](plan.md): Small prerequisite — reference-based independent review; stage 1 | `abb9159ef09824e74e7f4fd9cc0418d1976d0463367a43186e68862c30633004` |
| source | [validation](contracts/validation.md): Small reference-based prerequisite and admission; unchanged runtime/checks | `834de3891658417543747dd47ab04a2ca725d0e4f6bcd0d24ac30c368348dad4` |
| source | [research](research.md): Minimal reviewer-reference adjustment; repository-first evidence | `f7cacb7d9185efeaed48ae5964042be91c42a4f6080c349d6fdf9046bc5d527a` |
| decision | [specification approval](specification-approval.md): Current specification renewal — 2026-10-19; planning only | `3a816bb8513471a6e6eeba2685364f224a6d28e552a7f7258609c7e48ec2c188` |

Genuine renewal recorded at `b12d0145e55947311707d933710d021547653712` approves the app specification for continued planning, **not runtime edits**. The prerequisite follows the app's complete independent-review/accepted-runtime own-build requirement plus subsequent owner technical direction captured in the plan: references rather than copying; “Yes, make sure the changes are small and continue. You blocked yourself with a tiny issue that was really easy to fix.” This authorizes task preparation, not final concrete runtime scope/mode. No fabricated historical prerequisite approval or requirements-source rewrite.

Root `approval_refs: []`; envelope `approval_refs: []`. Existing specification approval is preserved above as decision evidence, not fabricated executable external-catalog authority. Current overall review/final owner scope and bootstrap-mode approval remain unresolved. Standard's specification/overall/implementation authority and full source/task/review identities remain required for any eventual **CLI** intake. This draft intentionally has no final tasks/review source pins or external catalog; static schema validity cannot satisfy `intake.admit`.

## Execution intent and boundary

Root intent: `model_class: Sol`, `effort: medium`, `resolution: resolved`. Compatible binding: provider `openai-codex`, model `gpt-6.1-sol`, effort `medium`.

- **Provenance**: owner separately selected implementation Sol/medium, clarified “use 6.1 sol medium”, recorded in specification/approval and preserved unchanged by parent. Planning selection is separate, despite same exact target. Later small-change direction authorizes preparation only.
- **Assumptions**: instruction-managed bootstrap is a PROPOSAL requiring explicit owner approval, not CLI-dispatched app execution. One implementer writer; named reference/byte/custody seams, REQUIRED checks and original gates explicit; routine helper choices open. Fresh independent full-original-range review/current acceptance before app admission.
- **Existing-file exception**: `cli.py` is **77250 bytes**. A narrow bootstrap wiring edit is proposed, not a refactor to fit worker tools. Existing oversized operating/schema documents also need explicitly disclosed bootstrap editing authority. Every new helper/test and every later app worker-managed source/test/doc/config/lock file stays **strictly <32768 UTF-8 bytes**. No blanket waiver. No `pi_adapter.py`/host/protocol edits proposed.
- **Reuse**: existing read permissions, admitted raw hashes, SQLite custody and SDK protocol. No identity/currentness claim for the historical wheel. Accepted source-local runtime remains unchanged throughout app execution.
- **Compatibility assessment**: exact intended implementation/repair target fits the bounded scaffold; actual fresh usable SDK/tools/resources/auth/effort and separate reviewer readiness still required. Existing operating guide supports observer `codex-final-payload`, version `1`, for this binding only; this is not permission or current availability proof.
- **Decomposition rationale**: one independently necessary reference-delivered-review/strict-byte outcome with permanent actual-helper tests, smallest composed existing review, affected docs, evidence and checkpoint. No prototype/test/docs/admin task chain; no family superiority or empirical effort-benefit claim.

Root envelope ID `monitor-runtime-bootstrap-draft`; profiles exactly `openai-codex/gpt-6.1-sol:medium`, observer `codex-final-payload:1`; `capabilities: []`, `limits: []`, `external_paid_authority: denied`. Empty capabilities reflect **non-CLI draft**, not authorized effects. The bootstrap check IDs below are instruction-managed labels, **NOT registered runtime capabilities**. Never feed this contract to CLI or invent a bootstrap schema flag. Any later decision to use CLI requires producing renewal with real registered versions/args and canonical scopes from `authority.action_requirement`; a source-local runtime cannot edit its own pinned imported source.

## Foundational prerequisite — one coherent delivery

- [ ] T001 Separately prepare and accept reference-delivered independent review and strict UTF-8 file guards in `runtime/coherence_workflow/cli.py`, `verification.py`, `intake.py`, new `review_documents.py`, focused tests and affected operating owners before any app execution.
  - **Depends**: none
  - **Order**: 0
  - **Context group**: `runtime-bootstrap`
  - **Authorization envelope**: `monitor-runtime-bootstrap-draft`
  - **Outcome**: accept the smallest reference-delivered independent-review/strict-file-boundary adjustment before app execution; never mutate the executing app runtime or call this CLI-dispatched bootstrap.
  - **Owned paths** (exact, no wildcard):
    - `runtime/coherence_workflow/cli.py`
    - `runtime/coherence_workflow/verification.py`
    - `runtime/coherence_workflow/intake.py`
    - `runtime/coherence_workflow/review_documents.py` (new small helper)
    - `runtime/tests/test_review_documents.py` (new focused permanent tests)
    - `runtime/tests/test_review_repair.py`
    - `docs/coordinate-implementation.md`
    - `docs/coordinate-implementation-schema.md`
  - **Optional**: none (`[]`). Broader unrelated regression remains optional, not substitute evidence.
  - **Gates**: `T001/G1`, `T001/G2` below; null approval refs; neither satisfied by planning.

### Implementation scaffold and exclusions

1. In `ReviewRepair.bundle`, replace embedded source/approval content values with complete exact authorized pinned refs (path, raw SHA, source kind/section or approval role, revision when available). Keep whole authoritative task contract and full original base→current-head binary patch. Remove a receipt's task-contract value only on canonical identity equality to the already supplied original authoritative task; retain unequal/dynamic correction contracts and all state/evidence/checkpoint/finding data.
2. Put small reusable document/UTF-8/coverage functions in `review_documents.py`; wire existing `_tools`/review boundary, admission and final-file verification without broad refactoring. Read once, validate identity/hash/strict UTF-8/byte bound, return those same decoded bytes. Keep exact original read allowlist. Store minimal raw hash/ref/read-process/review correlation, not document bodies/transcript history. Existing SDK turn intents and tool-process links must establish originating review and successful returned-content settlement; a read-result callback/intent alone is not proof of delivery. Reject incomplete/wrong-host coverage before review acceptance or finding-resolution effects. Preserve applicable original-question continuation only under exact independent lineage/bundle and current receipts.
3. Encode actual write text once as strict UTF-8; reject `>=32768` before filesystem effects (including parent mkdir); write those bytes. Apply byte rule to admitted source/approval documents and final actual worker-owned file set before checkpoint, not just JSON character count or process exit. Explicit preexisting bootstrap exceptions are G1-only, never later app worker exceptions.
4. Extend existing focused real review/correction test to exercise coverage before acceptance. Do not create a generic platform, new process framework or disposable PoC. Tests and evidence stay with delivery.
5. Narrowly align operating/schema docs; preserve original authorities, SDK protocol and full review. Any genuinely necessary additional path or semantics returns to producing review/current approval, not expansion by implementer.

**Excluded**: app files/tasks/locks/config prepared outside app runtime; registry/schema/host/SDK/dependency changes; new services/settings/auth/install/paid actions;120000/262144 limit increases; streaming/chunk/append/range tools; generic artifact platform; source/criteria/evidence/custody removal; SDK upgrade/package-registry authority expansion; historical wheel/catalog/run/receipt adoption; zero-owned-path PythonAnswer write/shell generator; broad runtime refactor. No lock/config/source staged to evade app review. Bootstrap code changes are not authorized now.

### REQUIRED checks — complete item mappings

All six items have `producer_dependencies: []` (no prior task) and gates **both `T001/G1`, `T001/G2`**. Internal ordering: focused V1–V3 proof before reliance in V4; V1–V5 before focused implementation checkpoint and separate V6 review/release. Missing/unrun/empty/skipped/stale evidence is NOT VERIFIED, never pass. Version for every instruction-managed label is string `"1"`. Check args and commands below mirror adjacent JSON; none is CLI capability registration.

Common unit command environment: `PYTHONPATH=runtime:runtime/tests`, `PYTHONDONTWRITEBYTECODE=1`. Interpreter `.pi/workflow-validation/venv/bin/python`, flags `-B -m unittest`, final `-v`; actual current dependencies must be revalidated at execution. These are concrete future local commands, not tests run during task preparation.

#### T001/V1 — complete reference bundle, no acceptance loss

- **Check**: `bootstrap.ReferenceBundleTests`, version1; argv `.pi/workflow-validation/venv/bin/python -B -m unittest test_review_documents.ReferenceBundleTests -v`, common env. Proposed permanent class, instruction-managed only.
- **Criterion**: complete pinned source/approval refs replace only redundant bodies. Preserve original authoritative contract, full original-range binary patch, REQUIRED/state/evidence/checkpoint/finding content and unequal/dynamic corrections. Remove per-task receipt contract only on exact canonical equality to supplied original. Keep120000 bundle and262144 SDK guards.
- **Pass**: positive collection, zero skip/error/failure. Compare exact admitted ref set and original patch/evidence before/after; equal contracts refer canonically, unequal/dynamic contracts retained. Measure actual final serialized bundle bytes; true oversize rejects without truncation/increased limits.
- **Expected evidence**: nonempty count/exit/output and assertions for inventory, equivalence, full-range/evidence preservation, actual byte measurement and oversize rejection, bound to precursor revision/environment.

#### T001/V2 — same-byte actual delivery, independently correlated coverage

- **Check**: `bootstrap.ReferenceDeliveryTests`, version1; argv `.pi/workflow-validation/venv/bin/python -B -m unittest test_review_documents.ReferenceDeliveryTests -v`, common env. Proposed permanent class, instruction-managed only.
- **Criterion**: every required ref actually obtained by existing read_file; safe identity, raw pinned hash, strict UTF-8/bound from SAME returned bytes. Audit minimal read receipts against originating independent host/turn/process/exact bundle/range/ref before record_review, finding resolution or acceptance. No prose claim, path expansion, hash/reread race, raw content ledger or prior/wrong-host coverage.
- **Pass**: actual production helpers positive succeeds; missing/changed/deleted/unsafe-symlink/unrelated unauthorized/unread/wrong-hash/wrong-host-turn-range/undelivered negatives reject before acceptance effects. Real process/SDK settlement and returned-byte hash establish coverage, not file-open intent. Continuation only with exact applicable independent lineage/bundle/current delivered proof.
- **Expected evidence**: nonempty named positive/negative counts/exit, actual returned SHA=pin=receipt, full ref coverage, zero acceptance/finding-resolution effects on negatives. Helper fixtures are not composed SDK proof (V4 supplies it).

#### T001/V3 — strict UTF-8 bytes, no prior write effects

- **Check**: `bootstrap.WorkerFileByteTests`, version1; argv `.pi/workflow-validation/venv/bin/python -B -m unittest test_review_documents.WorkerFileByteTests -v`, common env. Proposed permanent class, instruction-managed only.
- **Criterion**: worker reads/writes, admitted source/approval docs and final actual owned set strictly<32768 UTF-8 bytes. Validate same decoded/returned or encoded/written bytes; reject invalid UTF-8/exact32768/oversize before any file/directory/partial-write effect. Preexisting oversized bootstrap runtime/docs require G1 exceptions; no app-worker waiver.
- **Pass**: actual `_tools` read/write and admission/final guard: valid32767 succeeds;32768/larger ASCII and multibyte, invalid UTF-8 fail. Character-count-small/byte-large fails; existing target unchanged and new parent/file absent. No append/range/limit increase/JSON-character proxy.
- **Expected evidence**: nonempty counts/exit, measured sizes and returned/written identity, exact-boundary/multibyte filesystem before/after assertions; final per-owned-path byte inventory with only explicit G1 bootstrap exceptions.

#### T001/V4 — actual composed independent review before acceptance

- **Check**: `bootstrap.ComposedIndependentReview`, version1; exact argv:
  `.pi/workflow-validation/venv/bin/python -B -m unittest test_review_repair.IndependentReviewTests.test_actual_sdk_independent_review_finding_authorized_correction_and_full_rereview -v`.
  Common env plus `COHERENCE_LIVE=1`. Required external inputs: explicitly approved existing `COHERENCE_TEST_CGROUP_PARENT`; approved read-only current `COHERENCE_AUTH_PATH`/`COHERENCE_CATALOG_PATH`; explicitly owned isolated `TMPDIR`. Existing local unittest extended in scope, instruction-managed live test, **not CLI check dispatch**.
- **Criterion**: actual shipped CLI/SDK/Gateway review obtains full ref set; hashes/receipts correlate actual delivered bytes to independent host/turn/process before acceptance. Preserve fresh read-only role/full original patch/REQUIRED/checkpoint/correction/rereview/custody/original gates; no framework or fabricated production receipt.
- **Pass**: positive no-skip collection and actual independent current acceptance with original range/finding/correction/checkpoint chain. On real settled proof remove/mismatch coverage and observe recording/acceptance denial, then restore original proof for valid audit. Nonempty cgroup/SDK evidence, exact Sol/medium requests; no stale identities or mock-only positive claim.
- **Expected evidence**: test output + coverage assertions, isolated run/base/head/review-host/turn/read-process/hash correlation, incomplete/wrong-review denial and final acceptance/custody receipts. Retain failed-attempt diagnostics; test-only standing authority never claims human production approval.

#### T001/V5 — narrow diff and matching operating owners

- **Check**: `bootstrap.DiffAndDocumentationInspection`, version1; instruction-managed manual inspection, NOT runtime registry. Paths: `docs/coordinate-implementation.md`, `docs/coordinate-implementation-schema.md`; compare symbols `Coordinate._tools`, `Coordinate.review_boundary`, `Coordinate.checkpoint`, `ReviewRepair.bundle`, `ReviewRepair.record_review`, `ReviewRepair.acceptance`, `admit`, new `review_documents` helpers. Baseline: exact approved implementation baseline captured before mutation. Git argv: `git diff --no-ext-diff --no-textconv --check`.
- **Criterion**: docs match refs/delivered-read coverage/strict bytes; original protocol/authority effects/catalog authenticity/REQUIRED/gates/full patch/custody/hooks/signing/app runner-only commits unchanged. No new schema/platform/registry/dependency authority or redesign.
- **Pass**: diff check zero and explicit symbol/doc/error/limit comparison. Only eight owned paths, narrow cli wiring and helper/tests/docs; no app/lock/config/host/schema/skill changes/constants increase. New helpers/tests<32768; G1 exceptions only for preexisting oversized bootstrap files. New needed scope returns to producer review/current approval.
- **Expected evidence**: nonempty symbol/doc notes; exact owned diff/stat/byte inventory; diff-check exit/output; explicit120000/262144 and authority/custody/gate preservation confirmation.

#### T001/V6 — focused checkpoint, separate fresh full-range acceptance, app release

- **Check**: `bootstrap.IndependentAcceptance`, version1; instruction-managed writer checkpoint plus **separate fresh** independent review, not runtime registry. Reviewer `openai-codex/gpt-6.1-sol:medium`; range exact approved precursor implementation baseline→final precursor head including corrections; fresh reviewer gets full source/task/patch/REQUIRED evidence, no implementer history. Parent inspects commit/findings/dispositions/current acceptance and refreshed runtime identities before app start.
- **Criterion**: verify V1–V5 then focused eight-path writer checkpoint; independently accept exact original full range before app baseline admission. Never call bootstrap CLI-dispatched or manually mark app task complete. Later accepted runtime unchanged during same app build; preserve all SC-001–006/own-build retrospective AND live, no replacement demo.
- **Pass**: all required evidence current/nonempty. Writer inspects diff, stages/commits owned paths only, preserves unrelated work/identity/hooks/signing. Separate reviewer accepts exact current full range with resolved findings and original REQUIRED/gates. Authorized corrections get focused verified checkpoints/affected rereview. Parent admits accepted revised runtime as app baseline; no app executing from mutable runtime. Missing authority/evidence blocks reliance.
- **Expected evidence**: implementation baseline/result SHAs, focused tree/commit/diff, V1–V5 evidence/current applicability, separate reviewer identity/range/findings/dispositions/current acceptance; refreshed runtime source/config/registry/resource identities and parent baseline admission. Planning artifacts/static validation supply none of this implementation proof yet.

### Original manual/permission/capability gates

- **T001/G1** — kind `manual`, `approval_ref: null`, **UNRESOLVED**. Independent overall planning review and actual current-content owner approval must explicitly authorize separate instruction-managed bootstrap, exact eight paths and narrow edits to preexisting oversized cli/operating docs. Scope: current prerequisite human/JSON + Standard source/plan identities, before app CLI run, no source relabel/amendment/app/install/live-runtime mutation. Expected: actual parent owner-tool answer bound to reviewed current content/mode/owned exceptions, reviewed scope and release; denial/cancellation/drift blocks. Existing app spec renewal is insufficient; no invented external catalog or approval ref.
- **T001/G2** — kind `capability`, `approval_ref: null`, **UNRESOLVED**. Before implementation/tests verify sole writer, no active/unknown runtime using mutable sources, baseline and Git hooks/signing, actual Python deps, exact profile/resources. Before V4 verify scoped local live/model/test/cgroup/read-only auth/catalog/scratch permission and genuine standing test-only authority. Scope: named bootstrap commands; real runtime custody only in separate test-owned project; no app dispatch/paid/historical wheel/catalog/receipt reuse. Expected: actual current writer/resource/Git/interpreter readiness, approved scratch/delegated-parent identity/capability, current genuine auth/catalog/profile/tools/test-only scope. No install/auth/config workaround, skipped-pass or uninspected retry.

## Dependencies, validation and next gate

One T001, no story tasks and no task prerequisite. It is foundational to all later app work but **not T001 of the future app contract**. One instruction-managed implementer writer (only after G1/G2), then separate fresh reviewer, then parent acceptance/admission. No delegation or runtime dispatch in this planning stage. Keep code/permanent tests/docs/ordinary evidence/teardown in the delivery; missing proof stops app reliance rather than generating broad administrative work.

Expected verification effort: focused actual-helper tests plus ONE extension of existing live composed review/correction test because helper mocks cannot prove SDK reference delivery/receipt coverage before acceptance. Full independent implementation-range review remains mandatory; no unrelated suite/quota/benchmark/prototype chain.

Stage evidence: actual `.pi/prompts/speckit.tasks.md`1.0.12/pi/sequential and `setup-tasks.sh --json` followed; resolved checkout-local `.specify/templates/tasks-template.md`, prerequisite script passed with spec/plan present. Logical feature004 and `SPECIFY_FEATURE_NO_PERSIST=1` preserve real Git branch; no default app tasks created. Before/after extension hooks absent. Parent-selected precursor destination overrides default app tasks names. Create-only producer performs static schema/order/parity/hash/size/link validation, not self-review/substantive correction. Parent inspection → separate app-task producer → independent overall planning review → current-content final owner approval remain next. No implementation tests/provider/browser/live actions ran here.
