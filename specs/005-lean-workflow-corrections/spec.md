# Feature Specification: Lean Workflow Corrections

Apply [Parsimony and Actionable Checks](../../skills/planner/references/parsimony.md).

**Feature Branch**: `plan-standard-spec-flow-issues-23-28` (unchanged; directory numbering is independent)

**Created**: 2026-10-26

**Status**: Draft — specification production only; independent review and owner specification approval pending

**Input**: User description: “I want to address the following issues https://github.com/elsonidoq/skills/issues/23 https://github.com/elsonidoq/skills/issues/24 https://github.com/elsonidoq/skills/issues/25 https://github.com/elsonidoq/skills/issues/26 https://github.com/elsonidoq/skills/issues/27 https://github.com/elsonidoq/skills/issues/28. Read them carefully. It is important to avoid confusion among downstream agents, as well as to avoid scope creep and over complexities. I think all of these issues can be addressed by the Standard spec flow”.

**Selection and authority**: On 2026-10-26 the owner selected **“Standard: Specify → Plan → Tasks → Implement”** through `ask_user`. This authorizes bounded planning preparation and focused planning commits, not implementation or external mutations. This invocation creates only this specification, its required quality checklist, and `.specify/feature.json`, in `/home/dev/.paseo/worktrees/0zfm1a0e/tasty-quail`; the main worktree and global configuration must not change. Producer operation `standard-spec-create` uses saved `source-and-tasks` binding `openai-codex/gpt-6.1-sol`, effort `medium`, from [model assignments](../../skills/planner/references/model-assignments.json). Parent assessment: `NO_BRAINSTORM_NEEDED`; six independently useful outcomes in one specification, with #19 consolidated into #23 and no assumed dependencies between the six. Next: parent inspection → fresh independent read-only specification review → owner approval of the current specification. No plan or tasks yet. The issues' historical no-implementation notices remain true of filing alone; this later planning choice does not authorize implementation, historical restarts or acceptance changes.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Unsuccessful work cannot masquerade as completion (#23, including #19) (Priority: P1)

As an owner relying on dependency order, I need blocked, failed or incomplete work to remain unsuccessful even when a worker returns normally or leaves useful partial edits. Deterministic required commands must actually execute rather than disappear into description prose.

**Why this priority**: False completion permits downstream reliance on unmet acceptance and misleading final delivery.

**Independent Test**: V1 below exercises the actual execution and authored-command handoff boundaries without a provider or historical application run.

**Acceptance Scenarios**:

1. **Given** prerequisite A returns blocked, failed or incomplete, with either no changes or partial owned edits, **When** its invocation returns normally, **Then** A is not complete, dependent B is not dispatched, and the run does not enter success-path final review or its automatic fixer; partial work and actual history are preserved. This includes a delivered question answer followed by the worker's explicit blocked return, without treating delivered text as controller cancellation.
2. **Given** an authored deterministic required command, **When** tasks are handed to the runner, **Then** the command reaches an existing executable field, executes with its actual exit status recorded, and a failed or known unrun required result prevents completion and dependent reliance. A known worker-reported required failure is not certified by successful transport or checkpointing.
3. **Given** genuinely completed no-command/no-change work, successful required-command work, optional/unconfigured checks, or harmless corrected tool errors, **When** normal execution proceeds, **Then** these remain supported without a universal machine check or empty commit requirement. Ordinary safe same-task corrections remain possible; unmet required acceptance is never waived.

### User Story 2 - Routine approved tests do not require repeated consent (#24) (Priority: P1)

As an owner who has authorized isolated testing, I need agents to reconcile earlier agent-authored restrictions with later actual scoped authority and make routine technical setup choices without interrupting me again.

**Why this priority**: Repeated consent requests obstruct already-authorized verification while providing no test evidence.

**Independent Test**: V2 examines the affected instruction conflict and its supported handoff, preserving genuine owner restrictions.

**Acceptance Scenarios**:

1. **Given** an earlier agent-authored task/recovery demand for renewed exact-resource or rerun consent and later applicable owner approval for routine isolated tests, **When** selecting disposable fixtures, local setup or finite test windows, **Then** agents reconcile the conflict using current authority and shared defaults, not another routine approval request.
2. **Given** an actual owner-imposed limit, mandatory manual gate, paid application API, production operation, credential/global change or risk to unrelated data, **When** routine testing would exceed that boundary, **Then** it remains outside routine authority. Permission alone never marks the test run or passed.

### User Story 3 - Coordinator repairs a diagnosed in-scope blocker and continues (#25) (Priority: P1)

As an owner of an authorized implementation, I need the coordinator to arrange an understood routine repair that the current worker cannot edit, verify it, and continue unfinished work rather than hand me a recipe and wait.

**Why this priority**: A correct worker edit boundary must not turn an ordinary coordination problem into an unnecessary owner dependency.

**Independent Test**: V3 demonstrates scoped repair, verification/checkpoint, retained continuation and subsequent routine question handling together.

**Acceptance Scenarios**:

1. **Given** an inspected failure requires an in-scope file outside the current worker's paths, **When** the coordinator understands the cause and current authority covers repair, **Then** it delegates explicitly scoped repair with the necessary paths and selected executor settings, checks the diff and relevant verification, makes the focused checkpoint, and resumes unfinished work without replaying completed tasks or routine reapproval. A suitable retained session may be reused; fresh context is not universally required.
2. **Given** continued work asks another routine in-scope technical question after that repair, **When** the coordinator triages it, **Then** it investigates and answers autonomously. Product decisions, material scope/complexity increases and genuine permission/spending/security/data-loss boundaries still escalate; a failed repair is investigated rather than declared complete or blindly relaunched.

### User Story 4 - Newly tracked issues receive investigation and independent quality review (#26) (Priority: P2)

As an owner reporting a failure, I need one issue-tracking entry point that investigates the failure, records a focused issue, and independently checks the created instructions for ambiguity, omissions and unnecessary complexity before correcting actionable drift.

**Why this priority**: Successful issue creation/readback alone does not show that another agent can follow the issue without expanding its intent.

**Independent Test**: V4 demonstrates the ordered workflow through supported mechanisms, distinguishing actual external operations from fixtures.

**Acceptance Scenarios**:

1. **Given** a failure and available primary evidence, **When** the replacement entry point runs under applicable authority, **Then** it performs evidence-based investigation/RCA → focused issue creation/readback → separate read-only review of the actual body against original intent/evidence → evaluation and narrow correction of actionable findings → independent readback and report of URL, review result and uncertainty. The reviewer does not author new product requirements.
2. **Given** an uncertain cause, exact existing duplicate, unavailable/failed reviewer, or concurrent body change, **When** the workflow reaches that boundary, **Then** it respectively records verified facts/hypotheses and next useful investigation without indefinite RCA blocking; uses existing duplicate/scoped-update behavior; reports review incomplete without fabricated review or blind expensive retry; or preserves concurrent content and defers unsafe overwrite with a corrective action.

### User Story 5 - Valid review location ranges reach the repair flow (#27) (Priority: P2)

As an owner awaiting final review, I need ordinary line-range and single-line citations to convey the same valid rejection, without losing findings to a format error.

**Why this priority**: Citation compatibility should not prevent the existing review/fix process from receiving a substantive rejection.

**Independent Test**: V5 uses synthetic responses at the existing parser/review-flow seam.

**Acceptance Scenarios**:

1. **Given** otherwise valid rejected review output citing `path:717 - defect` or `path:717-723 - defect`, **When** it is consumed, **Then** the rejection and exact finding text reach the existing rejected-review/repair flow rather than a failed-format outcome. Neither form proves the finding correct or the implementation approved.
2. **Given** malformed output, invalid types or genuinely missing locations, **When** it is consumed, **Then** existing invalid-output protections remain effective and no success is inferred.

### User Story 6 - Authorized recovery-file handoff preserves existing work (#28) (Priority: P1)

As an owner continuing work on a specifically identified recovery file, I need a supported handoff into task ownership that preserves the existing bytes, allows the intended edit and includes only the owned result in its focused checkpoint.

**Why this priority**: Removing the current blocker must not weaken protection of unrelated or unknown work.

**Independent Test**: V6 exercises real ownership/edit/checkpoint behavior for both untracked and modified tracked pre-existing files in disposable repositories.

**Acceptance Scenarios**:

1. **Given** an explicitly authorized handoff of a specifically identified pre-existing recovery file, **When** the receiving task takes ownership and makes the intended correction, **Then** the pre-handoff content is preserved except for that intended edit and the focused checkpoint includes the owned result. Both untracked and modified tracked files work without repeated permission for the established handoff.
2. **Given** unrelated dirty files or an unapproved dirty target merely covered by a broad `owned_paths` entry, **When** handoff/edit/checkpoint is attempted, **Then** unrelated content stays unchanged and unstaged and the unapproved target is refused with its filename, affected operation and actionable supported correction. A broad allowlist alone never authorizes adoption of unknown bytes.

### Edge Cases

- An unsuccessful return can include useful edits or green checks against unchanged baseline content; neither makes unmet task acceptance complete.
- Required command failure may be repaired safely in the same task; real rerun success is needed before relying on the repaired result. Missing optional commands are not failures.
- Later scoped authority resolves an agent-created routine-consent demand, not an actual owner limit or a material unresolved authority conflict.
- A worker reply cannot widen ownership. Coordinator repair must use explicit separate scope and coordinate overlapping edits, not bypass the worker boundary or prohibit owner-authorized concurrency wholesale.
- Issue mutation may succeed while readback fails; preserve uncertainty and reconcile the exact issue rather than blindly repeat mutation. Reviewer availability does not determine whether an already-created issue exists.
- Citation-format acceptance preserves the verdict/findings; it does not adjudicate them, reopen a session, or relabel an old review.
- Recovery-file handoff is not a dirty-work inventory or automatic adoption; only specifically identified authorized content is eligible.

## Requirements *(mandatory)*

### Functional Requirements

#### Completion and authored commands — #23/#19

- **FR-001**: The execution boundary MUST distinguish invocation return, successful task completion and semantic acceptance. Explicit blocked, failed and incomplete results MUST prevent completion, dependent release and success-path final-review/automatic-fixer dispatch, for no-change and partial-work returns (Story 1; V1).
- **FR-002**: Authored deterministic required commands MUST survive task generation/handoff in existing executable fields/mechanisms and execute with real command results/exit status. Known failed or unrun required acceptance MUST remain unmet. Do not translate description prose into shell commands, require a shell command for every task, or replace agent semantic judgment with universal machine verification (Story 1; V1).
- **FR-003**: Preserve successful no-command/no-change work, optional/unconfigured checks, normal safe setup/tool corrections and existing required-check correction. Keep the six task-intake rules only: readable file; parsed task list; ID/work description; unique IDs; existing dependency references; acyclic dependencies. Apply the smallest compatible completion boundary; no prescribed keyword scanner, new result schema or additional model call. Change resume behavior only if a focused regression demonstrates a bypass of this correction (Story 1; V1).

#### Routine authority — #24

- **FR-004**: Reconcile affected task/recovery instructions with current scoped owner direction and shared routine permissions, so earlier agent-authored exact-resource/rerun consent demands do not override later applicable approval. Reasonable fixture size, disposable setup and finite windows remain routine technical choices, not invented universal limits or renewal gates. Inspect the current causal instructions before choosing changes; do not patch every layer by assumption (Story 2; V2).
- **FR-005**: Preserve [ADR-0003](../../docs/decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md): current authorized launch governs assigned scope over historical planning-only wording; executable tasks remain authorization-neutral, with phase status in approval records. Preserve requirements/manual gates and material authority conflict escalation. A returned execution is not acceptance; that historical ADR explicitly did not fix false completion. Preserve [ADR-0004](../../docs/decisions/ADR-0004-shared-routine-worker-permissions.md): use the existing shared `_ROUTINE_AUTHORITY` defaults for ordinary scoped fixes, isolated tests/databases/local servers, necessary local/in-project dependency setup and task artifact lifecycle without repeated consent; no new permission service/schema or universal resource/spending ceilings. Authorization never proves verification passed (Stories 1–3; V1–V3).

#### Coordinator repair and continuation — #25

- **FR-006**: The coordinator MUST inspect the actual blocker and failed invocation, then automatically delegate an understood, authorized scoped repair with explicit necessary paths and retained selected executor settings when the current worker cannot make it. Use existing delegation/continuation and suitable retained sessions where practical. Runtime changes need an established concrete limitation, not speculation (Story 3; V3).
- **FR-007**: Before continuation, inspect the repair diff, run relevant checks and complete the focused checkpoint; preserve partial/unrelated work and coordinate overlap through existing ownership/locking mechanisms. Continue unfinished work without replay, preserve actual acceptance and final independent review, and carry autonomous routine question triage through the resumed workflow. Clarify the conflict with “No automatic resume” without permitting blind retries, worker delegation or uninspected expensive relaunches (Story 3; V3).

#### Issue workflow replacement — #26

- **FR-008**: Replace the existing issue-tracking entry point, not add a competing permanent tracker, with the ordered investigation/RCA, creation/readback, independent actual-body review and actionable correction/readback behavior in Story 4. Update only affected routing/callers needed to make the replacement usable; keep reusable assets independent of project target/path/model (V4).
- **FR-009**: Investigation MUST distinguish observations, verified causes, hypotheses and remaining uncertainty. Review MUST use a separate read-only context, original intent, relevant evidence and actual created body; check ambiguity/conflicts, omissions, promoted assumptions, scope creep and over-prescribed mechanisms/checks. Use the selected reviewer configuration, not a hardcoded model. Evaluate findings against original intent; correct ordinary in-scope wording without routine reapproval, but return material outcome changes to the owner. No automatic multi-round review loop or extra planning/approval ceremony (Story 4; V4).
- **FR-010**: Preserve canonical-target discovery/confirmation, actual scoped mutation authority, full open/closed duplicate discovery, sensitive-data protection, narrow field updates, immediate pre-overwrite reinspection, concurrent-content preservation and independent mutation readback. Missing capability/authority defers the affected operation, never creates a fallback tracker. Unknown mutation/readback outcomes require reconciliation; failed/unavailable review must be reported incomplete, not fabricated or blindly retried (Story 4; V4).

#### Citation compatibility — #27

- **FR-011**: Accept ordinary single-line and line-range finding locations while preserving rejection text and existing review/repair flow. Retain malformed JSON/type/missing-location rejection. Do not change verdict meaning, infer approval, repair the historical substantive findings or rewrite old outcomes (Story 5; V5).

#### Explicit pre-existing file handoff — #28

- **FR-012**: Provide a supported exact-file handoff for explicitly authorized, specifically identified untracked and modified tracked recovery files, preserving existing bytes and allowing intended correction plus focused checkpoint. Preserve the guard for unapproved dirty targets; broad `owned_paths` is not handoff authority. Refusals MUST name the file, operation and supported corrective action without repeating established file-specific permission (Story 6; V6).

#### Shared scope and protection constraints

- **FR-013**: Preserve task-owned boundaries, unrelated dirty/staged work, hooks/signing, existing history and fresh independent final review. As required by ADR-0004, unknown/pre-existing bytes MUST NOT be adopted or deleted; FR-012 permits only the specifically authorized, identified handoff, not blanket adoption. Follow [memory owner guidance](../../memory/MEMORY.md#routine-technical-decisions-and-review-scope): routine technical decisions stay autonomous; product/material scope decisions and actual explicit permission gates remain with the owner; correction-only review stays on affected behavior. Preserve real manual/paid/security/data-loss/external boundaries, owner limits, credential protection and restrictions on global/auth changes, deployment, push and unrelated deletion (V1–V6 as applicable).
- **FR-014**: Deliver a lean first iteration, “not a cross-layer workflow redesign”. Source owner direction: “This must be a lean solution. A first small iteration to remove things that can be executed from agents and place it as executable contracts among other things. It is crucial that agents do not add tons of checks that end up making the workflow don't run at all. Checks must be few and principled.” Checks target actual changed boundaries and material failure risks, not speculative startup machinery. No extra runtime model calls for #23/#24/#27/#28; #26's separate issue reviewer is explicitly required, and #25 retains its requested repair delegation.

### Required Acceptance Evidence

These demonstrations are future delivery acceptance, **NOT RUN** during specification production. They do not add application startup checks. Use existing tests/controlled supported exercises, with concrete commands/results and pass/fail observables; do not claim instruction assertions establish live model judgment. Keep acceptance with its supported outcome unless a demonstrated dependency requires separation.

| Evidence | Required observable and lowest sufficient layer | Applicability and authority |
| --- | --- | --- |
| **V1 — Stories 1 / FR-001–003,005** | Fail-before/pass-after disposable-Git regressions around the **actual engine** with a stub adapter: unsuccessful A (no edits and partial edits), B not dispatched, A not complete, no success-path review/fixer; delivered-answer/blocked-return case; actual required-command failure and known worker-reported required failure cannot certify success. Exercise the authored task-generation/handoff seam through an existing executable command field, including real failing exit status. Positive controls cover successful required work, genuine completed no-command/no-change work, optional/unconfigured checks and harmless corrected errors. Reuse existing authority/check/engine tests; a new helper alone is insufficient. | Offline fixtures suffice; no live Cerca/provider run. Inspect resume only for a focused demonstrated bypass, not a recovery matrix. Report correction-induced failures and fix them; report unrelated baseline failures separately without weakening assertions. |
| **V2 — Story 2 / FR-004–005** | Inspect/reproduce the affected instruction precedence conflict; focused handoff/contract coverage shows later scoped owner authority reconciled with earlier agent-created exact-setup/rerun restrictions and preserves genuine owner limits. Check both ordinary setup and corrective/resumed instructions only where changed. Distinguish delivery/text evidence from agent-obedience evidence. | No new permission framework or paid calls. The source incident supplies the scenario, not proof that the exact application wording is currently in this repository. No historical application repair required. |
| **V3 — Story 3 / FR-005–007** | One representative supported repair/check/resume exercise: needed in-scope file outside current worker paths → coordinator investigates/delegates with explicit ownership and selected settings → repair diff/checks/focused checkpoint verified → unfinished work resumes without replay or routine approval → another routine question resolved autonomously. Add focused regressions only where behavior changes. Prompt assertions alone do not establish the behavioral sequence. | Use the smallest suitable existing test or controlled exercise and report exactly which actors/actions were actual versus simulated. Any live delegation/continuation requires current applicable implementation authority and inspected state; this specification grants none. Historical monitor restart is not required. |
| **V4 — Story 4 / FR-008–010** | One representative end-to-end supported use: failure/evidence-based RCA → issue create/readback → separate reviewer checks actual body against original intent → actionable drift finding evaluated/corrected/read back. Focused changed-seam coverage includes uncertain RCA, unavailable review and retained target/auth/unrelated-content protections. | Explicitly distinguish actual external/reviewer behavior from offline/stubbed coverage. Live issue writes require scoped target/operation authority; delegation requires usable selected configuration. Neither is granted here. If required exercise authority/capability is absent, report NOT RUN/UNAVAILABLE and retain the outstanding requirement; do not silently waive it or expand permission. |
| **V5 — Story 5 / FR-011** | Synthetic otherwise identical valid rejections using single-line and range citations reach existing rejected-review/repair handling with findings unchanged, not failed-format review. Existing invalid-output checks still reject malformed output. | Offline parser/flow fixtures suffice; no paid calls, private session import or retained workflow replay. |
| **V6 — Story 6 / FR-012–013** | Real ownership/edit/checkpoint fixtures in disposable Git: approved exact untracked handoff and approved modified tracked handoff preserve starting bytes except intended edits and checkpoint owned results; unrelated dirty files unchanged/unstaged; unapproved dirty target refused actionably, including broad allowlist not being authorization. | Offline fixtures suffice; preserve normal hooks/signing and unrelated-work protection. No filesystem inventory or broad adoption. |

### Source Evidence and Confidence

All seven actual issue bodies were read through read-only `gh issue view --repo elsonidoq/skills` on 2026-10-26; all were OPEN. The six requested issues remain distinct outcome owners; [#19](https://github.com/elsonidoq/skills/issues/19) overlaps [#23](https://github.com/elsonidoq/skills/issues/23) and is consolidated only into Story 1, not a second implementation. Original source links for [#24](https://github.com/elsonidoq/skills/issues/24), [#25](https://github.com/elsonidoq/skills/issues/25), [#26](https://github.com/elsonidoq/skills/issues/26), [#27](https://github.com/elsonidoq/skills/issues/27), [#28](https://github.com/elsonidoq/skills/issues/28) retain their evidence and exclusions.

Current repository inspection at baseline `967249182a8bae111a5c71563256b34340769574` establishes the following anchors; these support bounded requirements, not a prescribed design or an executed reproduction:

| Source | Verified observation → requirement and proof |
| --- | --- |
| [Engine.invoke, lines 1019–1129](https://github.com/elsonidoq/skills/blob/967249182a8bae111a5c71563256b34340769574/runtime/coherence_workflow/engine.py#L1019-L1129) | Normal worker return is stored as summary after checks/checkpoint and task marked complete; no unsuccessful-result boundary is present in this inspected path → FR-001 / V1. Existing correction loops must remain usable. |
| [verification.commands/run_checks, lines 16–24, 80–105](https://github.com/elsonidoq/skills/blob/967249182a8bae111a5c71563256b34340769574/runtime/coherence_workflow/verification.py#L16-L105); [task-generation, lines 199–238](../../skills/task-generation/SKILL.md#structured-executable-handoff-both-adapters) | Commands already come from `checks`, `check`, `required[].check`, not descriptions; actual subprocess status is retained and nonzero checks raise failure. Authoring contract says specified checks run, with fields optional, but this is not proof that all authored commands reach executable fields → FR-002–003 / V1 handoff proof. No prose compiler needed. |
| [engine authority blocks, lines 69–90](https://github.com/elsonidoq/skills/blob/967249182a8bae111a5c71563256b34340769574/runtime/coherence_workflow/engine.py#L69-L90); [test_worker_authority.py](../../runtime/tests/test_worker_authority.py) | Shared current-launch/routine defaults already exist; tests explicitly establish prompt wiring, not obedience → preserve FR-005 and target the actual conflict in FR-004 / V2. Exact Cerca task/quickstart/recovery wording reported by #24 is **UNVERIFIED in this checkout**, not an established present code cause. The reverted patch is not an accepted solution. |
| [coordinator Question triage / Recover Context](../../skills/coordinate-implementation/SKILL.md#question-triage); [same-task required correction, engine lines 1050–1074](https://github.com/elsonidoq/skills/blob/967249182a8bae111a5c71563256b34340769574/runtime/coherence_workflow/engine.py#L1050-L1074) | Routine coordinator decisions are authorized, but “No automatic resume” is also stated; same-task correction retains task scope. This supports a contract ambiguity/boundary mismatch, **not proven model causation or a demonstrated missing runtime API** → FR-006–007 / V3. |
| [track-open-issue contract](../../skills/track-open-issue/SKILL.md) | Current entry point handles target, authorization, overlap, narrow mutation and readback, without an explicit pre-creation RCA and independent issue-quality-review stage → FR-008–010 / V4. Preserve useful safeguards rather than create another tracker. |
| [Engine._review_value, lines 590–613](https://github.com/elsonidoq/skills/blob/967249182a8bae111a5c71563256b34340769574/runtime/coherence_workflow/engine.py#L590-L613); [test_review_chain malformed coverage](../../runtime/tests/test_review_chain.py) | Location pattern requires whitespace after first line number, rejecting ranges; invalid-type/location tests already exist → FR-011 / V5. Private historical reviewer claims were not independently rechecked and are not requested fixes. |
| [FocusedGit.__init__/claim, lines 82–109](https://github.com/elsonidoq/skills/blob/967249182a8bae111a5c71563256b34340769574/runtime/coherence_workflow/git_effects.py#L82-L109); [test_git_effects.py](../../runtime/tests/test_git_effects.py) | Resume facts supply prior paths; pre-existing dirty targets outside those facts are refused even if `owned_paths` includes them. Existing tests protect that guard and focused checkpoints → FR-012–013 / V6, not removal of protection. |

Historical incident facts are evidence, not additional workstreams or newly imposed execution conditions. In particular #23 records **T002 scratch PostgreSQL: 3 passed, twice**; that does not establish the missing T001/native prerequisite. Authorization for isolated/native testing existed but native proof did not. Partial implementation was retained, not accepted. Historical monitor repair and failure claims in #25 likewise do not establish current application failures or completion. No raw private sessions are imported, and no history is to be rewritten.

### Key Entities

- **Task result**: Successful or unsuccessful task work, distinct from invocation return, retained edits/checkpoint and semantic acceptance.
- **Required command**: An authored deterministic acceptance operation carried through an existing executable task field, with actual execution outcome; distinct from semantic criteria or optional absent checks.
- **Scoped repair**: Diagnosed authorized correction with explicit paths, verification and checkpoint, supporting continuation of unfinished work without widening the original worker's boundary.
- **Tracked issue and review**: Canonically identified issue body/evidence plus an independent assessment against original intent; review completeness is distinct from creation/readback success.
- **Exact recovery-file handoff**: Explicit authorization for specifically identified existing content to become owned task work; neither a broad path allowlist nor permission to adopt other unknown bytes.

### Exclusions

No cross-layer workflow redesign, cancellation/unsolicited steering API, recovery subsystem/matrix, historical migration/rewrite/relabeling, evidence registry/catalogue/receipts, new permission schema/service, approval ledger, filesystem inventory, budget/watchdog/quotas/timers, extra startup checklist or admission gates, broad cleanup, automatic install/auth refresh/reload/restart, or new general orchestration/test framework. No universal per-task command or machine-verification requirement, invented thresholds, optional-telemetry veto, prose-to-shell compiler or mandatory predecessor-summary distribution. No historical issue migration, unrelated issue rewriting, competing/local fallback tracker, automatic multi-round issue review, or underlying application repair through #26. No session-recovery subsystem or repair of historical substantive findings through #27. No broad owned-path adoption through #28. No historical Cerca/monitor restart, production operation, deploy, index rebuild, paid application API use, acceptance relaxation or historical approval renewal is authorized. Adjacent issues referenced by sources remain context, not dependencies to solve.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Owners observe unsuccessful no-change and partial results remaining unsuccessful, without dependent work or success-path final delivery starting; genuinely completed no-change/no-command work still proceeds (Story 1 / V1).
- **SC-002**: Specified deterministic required commands actually run and report their real outcome; missing/failed required acceptance is never replaced by consent, invocation success or a checkpoint (Story 1 / V1).
- **SC-003**: Already-approved routine isolated testing proceeds without renewed exact-setup/rerun consent, while actual owner restrictions and evidence obligations remain intact (Story 2 / V2).
- **SC-004**: The representative repair sequence delivers a verified scoped correction and continued unfinished work, without replay or routine reapproval, including the subsequent routine question (Story 3 / V3).
- **SC-005**: The representative issue workflow yields an evidence-backed issue independently assessed against original intent, with an actionable drift correction read back and uncertainty accurately reported; uncertain causes and unavailable review are not disguised as confirmed causes or completed review (Story 4 / V4).
- **SC-006**: Equivalent single-line and range-cited rejections retain their findings and reach normal rejected-review handling, while malformed outputs remain rejected (Story 5 / V5).
- **SC-007**: Specifically authorized existing recovery files can be corrected and checkpointed without losing their earlier work, adopting unapproved targets or changing/staging unrelated work (Story 6 / V6).

## Assumptions

- **Repository-derived choice, not a new owner requirement**: Existing runner fields, delegation/continuation, shared authority and Git mechanisms are the starting point. Current source supports specification without selecting a new dependency or version. Repository-first research suffices at this stage; no consequential external API/design unknown requires new internet research. Planning must inspect actual installed APIs if its chosen approach makes them consequential, rather than rely on remembered capabilities.
- **Independence**: The six outcomes are independently testable; no cross-issue dependency is established. A future plan may add a causal dependency only with evidence, not because the outcomes share runtime files. Overlapping edit ownership still needs coordination.
- **Risk/proof choice**: No separate speculative prototype is warranted. The known completion, citation and ownership seams need permanent actual-engine/helper/flow regressions; instruction/coordinator/issue behavior needs the proportionate contract coverage and representative demonstrations in V2–V4. Proof is applicable only to its tested revision/environment and observed boundary; failed/unrun evidence cannot release reliance, and changed scope/acceptance returns to affected review/approval. Retain any disposable proof until its consumers are validated; do not create a proof/report/cleanup chain.
- **Outstanding delivery gates, not specification ambiguity**: No implementation, live issue-write or historical workflow continuation authority is granted. V3/V4 demonstrations remain required under their actual capability/permission boundaries; they are not completed or waived by this draft. No unresolved product question is identified for specification production; independent review and current-specification approval remain pending.
