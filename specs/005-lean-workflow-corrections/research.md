# Technical evidence — lean workflow corrections

Canonical technical research owner for this feature; inspected 2026-10-26 at `0bb64cd5088f950e0228f94a0058c55182d8f27b`. Requirements remain [spec.md](spec.md); decisions below are repository-derived unless labelled otherwise. No implementation acceptance was executed.

## Dependency and capability basis

- `runtime/pyproject.toml`: Python >=3.10, PyYAML 6.0.3; `runtime/requirements.lock` pins that dependency for Python 3.12/Linux. Standard-library unittest, SQLite, subprocess and Git already support the needed fixtures.
- `runtime/pi-host/package.json` pins `@earendil-works/pi-coding-agent` 0.87.1 and Node >=22; `package-lock.json:1–22` confirms the exact package version and registry integrity. This is compatibility evidence, not permission to install or a new admission gate. No dependency changes are warranted.
- `.specify/integration.json`: SpecKit 1.0.12, pi/sh. Actual `resolve-template.sh plan-template` returned the composed template; `setup-plan.sh --json` created this feature's plan once. `common.sh:174–265` resolves the ignored feature locator independently of Git branch. Its returned BRANCH is `005-lean-workflow-corrections`; actual Git branch remains `plan-standard-spec-flow-issues-23-28`. No hooks file exists.
- Selected `.pi/workflow-executor.json`: `openai-codex/gpt-5.6-terra`, medium worker; `openai-codex/gpt-6.1-sol`, medium reviewer. Task producer must read that actual selected file itself. Planning's saved `openai-codex/gpt-6-astra`, medium assignment is not an execution assignment.
- Installed Pi 0.87.1 `docs/sdk.md` (Session lifecycle/Prompting), `docs/message-types.md` (AssistantMessage), `docs/sessions.md`, `docs/session-format.md`, and `examples/sdk/11-sessions.ts` were inspected locally. Documented behavior: prompt resolution means run finished; message `stopReason` describes provider execution, not task acceptance; `SessionManager.open` supports explicit retained sessions. Source authority: [SDK](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/sdk.md), [message types](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/message-types.md); local installed version, not changing main-branch documentation, controls applicability.
- Repository source exposes continuation and parent question interfaces; availability in a future execution session must be verified there. This planning child has no delegation/provider/issue-mutation authority. No external research was necessary: current local implementation, tests, pins and installed SDK documentation answer consequential dependency questions. No external tool availability is claimed.

## Evidence → decision → observable

### Completion and deterministic commands (#23/#19)

**Evidence:** `runtime/coherence_workflow/engine.py:1019–1129` stores worker text, runs checks/corrections, checkpoints, then unconditionally marks the task complete. `runtime/pi-host/host.mjs:25–46` waits for idle, rejects SDK error/aborted stops, and otherwise returns last assistant text. Neither is semantic acceptance. `verification.py:16–24,80–105` consumes `checks`, `required[].check`, `check`; it never extracts commands from descriptions. Nonzero exits become `CheckFailure`, with real command/output retained. `engine.py:1050–1109` already supports same-task check/checkpoint correction.

**Decision:** Put the unsuccessful-outcome decision at the task-return/completion seam, before success checkpoint/session settlement/dependency release. Do not treat transport success, green baseline checks or a commit as sufficient. Preserve the existing correction path and natural-language semantic judgment; no extra judging model, universal command, intake rule or prose-to-shell translator. Do not prescribe a new worker-result schema or a keyword scanner. The implementation must demonstrate its smallest compatible result interpretation against the negative AND positive V1 cases before relying on it; incidental mentions of corrected failures are not terminal failure declarations.

**Alternatives rejected:** extra verifier model (cost/scope), mandatory check for every task (breaks legitimate no-command work), blanket tool-error veto (breaks safe correction), description parsing (unsafe and unnecessary).

**Observable:** actual Engine plus disposable Git/stub adapter; failed/incomplete/blocked task stays unsuccessful, B/review/fixer absent, partial bytes retained. Authored required command reaches one existing executable field, actual nonzero result observed. Existing `test_engine.py`, `test_check_correction.py`, `test_verification.py`, `test_worker_authority.py` supply fixtures. Test resume only if a focused counterexample shows a newly introduced bypass: `engine.py` and `test_resume.py` already recover checkpoints without replay; do not redesign recovery.

### Routine authority (#24)

**Evidence:** shared `_IMPLEMENTATION_AUTHORITY` / `_ROUTINE_AUTHORITY` in `engine.py:69–90` and injection inside `invoke_worker` apply to initial/corrective/resumed calls. `test_worker_authority.py:14–91` verifies prompt delivery and an actual tiny SQLite check, expressly not model obedience. The exact incident's application task/recovery consent wording remains UNVERIFIED in this checkout.

**Decision:** reproduce the incident's precedence conflict as a labelled instruction fixture, then amend only the causal shared instruction/handoff if the fixture reveals insufficient reconciliation. Earlier agent-authored exact-resource/rerun consent language must not outrank later scoped authority; genuine owner restrictions remain. No application checkout repair, historical rewriting or broad layer sweep.

**Observable:** V2 initial and affected corrective/resumed handoffs retain both the scoped authority and genuine manual/paid/security limits. Text delivery is not agent-obedience evidence. [ADR-0003](../../docs/decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md) keeps tasks neutral and explicitly leaves false completion unresolved; [ADR-0004](../../docs/decisions/ADR-0004-shared-routine-worker-permissions.md) requires reuse of shared defaults, not a permission service.

### Scoped repair and continuation (#25)

**Evidence:** `skills/coordinate-implementation/SKILL.md` Question triage authorizes routine diagnosis, but also says “No automatic resume”. Interface Actions already exposes explicit retained `resume`. `engine.py:884–942` inspects retained invocation state, requires a diagnosis for failed saved sessions and preserves reuse compatibility. `runtime/tests/test_resume.py` demonstrates completed-checkpoint skipping and retained review continuation. `.pi/extensions/coordinate-implementation-bridge.js:160–246` registers `coordinate_implementation_start` with `resume`; lines 151–158 and 280–296 route routine questions/replies to the parent. Host `createWorkflowSession` explicitly opens runner-private saved sessions; worker tool set excludes delegation. These are real source entrypoints, not proof of loaded parent tools in this child.

**Decision:** coordinator-led repair, not worker scope expansion. After inspected terminal settlement/lock reconciliation, delegate a separate bounded repair with current selected executor, inspect diff/check/checkpoint, then invoke existing retained continuation and answer the later routine question. Clarify that prohibition concerns uninspected retries/legacy automatic restarts, not reasoned continuation after authorized repair. Do not call review-fixer machinery for arbitrary repair or recursively launch the CLI inside a worker. If a live worker still owns the lock, do not launch a competing writer or fabricate cancellation; finish/reconcile the affected invocation first. Runtime edits require a demonstrated limitation in the supported exercise.

**Observable:** V3 representative sequence records actual paths, repair/checkpoint, no completed-task replay, retained unfinished continuation and later autonomous routine answer. Offline adapters can prove wiring/Git/order, not model investigation or autonomy; any controlled live portion needs current authority and loaded tools. No historical monitor run.

### Issue workflow (#26)

**Evidence:** `skills/track-open-issue/SKILL.md` Candidate/target, Discover overlap, Create/scoped change and Report sections already require full open/closed pagination, exact target, mutation authority, pre-overwrite reinspection and independent GET readback. They lack an explicit RCA → independent actual-body intent-review sequence.

**Decision:** replace behavior in the existing entry point, retaining its name/routing where possible (no second skill/tracker). Investigate before mutation; uncertain cause becomes facts/hypotheses/next investigation, not an indefinite block. After readback, give a separate read-only reviewer original intent/evidence and actual body; choose configured reviewer, not planner model. Evaluate findings, narrowly correct actionable drift once through existing scoped mutation/readback safeguards. Report creation and review completeness separately. Exact duplicates use existing dedup/scoped-update semantics, never forced new issues.

**Observable:** V4 includes actionable ambiguity/scope drift corrected and independently read back; unavailable reviewer, uncertain RCA, target/auth and concurrent-content cases retain honest outcomes. Existing mutation instructions remain the safety boundary. A scripted reviewer response is not actual independent model judgment; live issue authority is separate from implementation approval.

### Citation compatibility (#27)

**Evidence:** `Engine._review_value`, `engine.py:590–613`, uses `^\S+:\d+\s+-\s+\S`; a range fails solely because whitespace is required immediately after first number. Existing JSON/type/nonempty-list/location protections surround it; `test_review_chain.py` exercises the real review flow.

**Decision:** narrowly admit the optional numeric range in the existing location expression; retain text/verdict untouched and other guards. No new location object, review semantics or historical outcome changes.

**Observable:** V5 otherwise identical single/range rejections enter existing rejected-review/repair handling; malformed JSON/types/missing location remain invalid. Offline is sufficient.

### Exact recovery-file ownership (#28)

**Evidence:** `FocusedGit.__init__/claim/facts/checkpoint`, `git_effects.py:82–155`, recognizes resumed exact paths, refuses other pre-existing dirty targets before optional path-limit matching, and checkpoints only explicitly selected paths. `test_git_effects.py` covers dirty-target rejection, unrelated staged preservation, symlinks, hooks and focused commits. Broad `owned_paths` is not authorization today and must not become it.

**Decision:** add a narrow exact-file handoff into existing ownership handling, carrying only explicitly authorized identified targets, separately from path limits and generated outputs. Reuse current facts/claim/checkpoint lifecycle; do not fake old resume history or adopt directory contents. Check the identified file at the transfer/edit boundary so changed/unknown bytes are not silently accepted. Keep starting content and apply intended edit; no cleaning/resetting first. Expose the supported handoff through the existing execution input path, not a new permission service/ledger. Concrete optional syntax is an implementation detail, not an extra startup requirement.

**Observable:** V6 actual Git fixture passes tracked-modified and untracked transfers, verifies before/after bytes and exact checkpoint paths, refuses unapproved target even under broad allowlist with filename/operation/correction, and preserves unrelated dirty/staged bytes.

## Risk and evidence lifetime

No separate prototype is justified: completion/parser/ownership seams are bounded and have existing permanent fixture owners. Put failing reproductions and passing regressions within their deliveries. V3/V4 composed demonstrations cannot be replaced by static prose assertions; select the smallest supported exercise, label simulated actors, and retain any missing behavioral proof as NOT RUN. No new startup ceremony results. Evidence applies only to tested revision/environment; changed semantics invalidate affected proof. Failure blocks reliance on that outcome, not unrelated outcomes. Scope/acceptance changes return through existing approval gates.
