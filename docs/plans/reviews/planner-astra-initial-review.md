## Review — findings first

### F1 — P1: Trace oracle accepts a depth choice without observing the question or either option

**Location:** `scripts/planner-trace.py:60–85`, particularly the freeform branch at `:73–77` and completion check at `:85`.

**Failure scenario:** supply a contract identifying `choose`, expecting `TinySpec`, with no approval calls. Supply only a `tool_execution_end` for `choose` whose result contains a successful freeform `"TinySpec"` answer.

The checker:
- Adds `choose` to `ended`.
- Accepts the freeform response despite finding no matching start in `calls`.
- Sets `selected = True`.
- Passes its final check because `choose` is in `ended`.

Thus an incomplete trace can pass without evidence that an `ask_user` call occurred or that both choices were offered. The option checks at `:43–49` execute only when a start event is present.

This is a source-derived counterexample, not a reviewer-executed test. It contradicts the documented oracle scope in `docs/plans/planner-regression.md`, **Trace evidence and executive briefs**: checking both options at the actual choice.

**Smallest correction:**
- Require the matching `ask_user` start before accepting its result.
- Require completed, validated choice arguments.
- Reject orphaned, reversed, or duplicate lifecycle events for tracked gates.
- Add offline fixtures for orphaned freeform results, wrong-tool starts, and end-before-start ordering.

This does not require live testing or semantic classification of arbitrary owner answers.

### F2 — P1: Replacement checks lose the previously established protection against disconnected shared brainstorming

**Locations:**
- `scripts/check-planner-workflow.py:58–75,98–101`
- `scripts/test-planner-workflow.py:45–99`
- Operational instructions currently at `skills/planner/SKILL.md:63–66,91`

**Failure scenario:** delete planner’s operational invocation of `planning-brainstorming` at lines 63–66 and its instruction to apply recorded decisions through the shared mechanism at line 91. Leave prerequisite mentions and the shared skill itself intact.

The inspected checker predicates still hold:
- `choice` checks the read-only/choice wording, not shared invocation.
- `handoff` does not require shared decision application.
- `brainstorm` checks the primitive’s own text, not whether planner calls it.
- Focused brainstorming tests likewise inspect only the primitive.
- No supplied mutation deletes these caller instructions.

This is the same class of coverage failure explicitly repaired previously: `docs/plans/reviews/requirements-manager-targeted-final-recheck.md`, **A1 disposition**, records operational-section checking rather than accepting prerequisite mentions.

The candidate’s actual instructions are correct today. The regression is in replacing a known protection with tests that would permit its removal.

**Smallest correction:**
- Add section-local predicates for planner’s preselection invocation, correct mode/readiness target, and postselection bounded application.
- Add named mutations deleting those operational instructions while preserving prerequisites and the shared skill.
- Likewise check actual TinySpec/direct-task adapter invocation rather than relying only on the existence of the producer files.

Do not attempt exhaustive natural-language validation; preserve this specific, previously demonstrated negative test.

### F3 — P2: Choice-result matching imposes an undocumented first-word title convention

**Location:** `scripts/planner-trace.py:68–72`.

The checker offers-path test accepts titles containing `TinySpec` or `Standard`, but result acceptance requires the selected title’s first space-delimited token to equal the depth.

**Failure scenario:** the agent offers `TinySpec: compact source and tasks` and `Standard: separate SpecKit stages`; the owner selects the former. Both choices satisfy the offer check, but the valid selection is rejected because the first token is `TinySpec:`.

Neither planner’s instructions nor `ask_user` requires this title format.

**Smallest correction:** let the supervisor-authored contract identify the exact expected offered title, separately from normalized depth. Validate that title against the actual options and returned selection. Add punctuation/prefix fixtures; avoid replacing this with loose substring-based consent inference.

---

## Verdict

**NOT READY for final acceptance; targeted offline corrections are needed.**

**Merge verdict: BLOCK** on F1–F2. These findings concern the new regression infrastructure, not an observed loss of the core planning safeguards.

After those corrections, the appropriate status is **ready with explicit validation follow-up**: real-agent behavior, installed SpecKit integration, and global installation remain separately authorized, unrun validation—not prerequisites to pretend have passed now.

No edits or fixes were applied.

---

## What is correct

### Architecture and owner-choice boundary

`skills/planner/SKILL.md:56–84` implements the settled architecture:

- Read-only preselection.
- Session-history answers and recovery by asking.
- Shared proportional brainstorming.
- Both paths regardless of recommendation.
- Explicit tool-mediated selection and stop.
- Preparation authority distinguished from implementation authority.
- No automatic rerouting as uncertainty resolves.

The primitive’s modes agree with that boundary: `skills/planning-brainstorming/SKILL.md:29–36,74–90`. The earlier conflict between durable preselection files and no artifacts has been resolved.

### Evidence and source safeguards

`skills/planner/SKILL.md:15–53` preserves:
- Selected source bounds and ambiguous-provenance stops.
- Project-associated memory retrieval.
- Missing-reference/capability reporting.
- Positive and negative claim verification, especially “already satisfied/no task needed.”
- Source-layer citations and relevant verbatim evidence.
- Explicit deferral of unresolved load-bearing claims.
- Beneficiary, exclusions, and separately scheduled work.
- Bounded inspection rather than an automatic repository-wide audit.

These correspond to the removed `create-epic` behavior rather than merely retaining its former vocabulary.

### TinySpec production and review

`skills/tiny-spec/SKILL.md:11–58` provides the compact authoritative what/how source, accepts established formats, preserves necessary session-only context, returns material blockers, and forbids task generation or execution.

`skills/planner/SKILL.md:103–120` correctly makes:
1. Source production.
2. Separate direct task production.
3. Planner-owned review.
4. One combined source/task/implementation-scope approval.

It does not add an independent TinySpec planning reviewer or a premature source-approval gate. That matches the additional settled owner decision.

### Standard micro-contracts

The new Standard path preserves the important removed-manager obligations at `skills/planner/SKILL.md:122–169`:

- Observed SpecKit instructions, templates, and prerequisites.
- Affected-stage capability stops; no simulated or generic substitutes.
- Missing/template constitution handling through the observed capability and verified output.
- Settled valid principles remain settled.
- Specification creation at sonnet class.
- Conditional clarification.
- Current specification approval before planning.
- Opus-class same-session specification review/fix → one plan creation → plan review/fix.
- Adapter precedence and no post-adapter duplicate plan.
- Create-only task production at sonnet class.
- Independent owner-selected analysis/review.
- Mechanical correction versus material owner decision.
- Approval renewal and unanswered-question recovery.

The architectural helper’s adapter remains coherent at `skills/delegating-architectural-planning/SKILL.md:44–54`.

### Approvals and legacy recovery

`skills/planner/references/approval-and-recovery.md:3–47` makes the executive brief owner-visible and prior to the tool call, including renewals. It covers exact authorization, failed/unavailable checks, denial, cancellation, external records, current content, and non-recursive evidence.

The legacy mapping at `:51–69` addresses the earlier retirement gap:
- Task-embedded legacy requirements remain valid.
- Approved Standard artifacts retain their stronger evidence requirements.
- Approved specification awaiting planning resumes the mapped stage.
- Stale evidence returns to planner-owned checkpoints.
- No invocation of retired managers or fabricated historical depth choice.
- Ambiguous origin cannot be used to downgrade safeguards.

Coordinator intake agrees with this mapping at `skills/coordinate-implementation/SKILL.md:33–73`.

### Shared tasks and execution

The task-generation diff is confined to adapter/source-shape language. IDs, prerequisites, explicit dependency fields, story continuity, model rationale/share, documentation, integration, manual fallback, and traceability obligations remain.

The coordinator diff is confined to intake. Its execution section remains unchanged in the inspected delta. The new baseline digest check at `scripts/check-planner-workflow.py:124–128` adds useful protection against unintended execution changes.

### Documentation and adoption

The non-clean documentation path still requires fresh investigation, explicit approval, bounded shells/indexes, and dirty/concurrent-edit protection. It no longer forces an Epic or Standard selection: `skills/initialize-documentation/SKILL.md:101–129`.

Adoption refresh is proposal-first and bounded to the marked suite section, preserving custom paths and existing memory: `skills/install-memory/SKILL.md:56–82`.

Historical documents were not rewritten into current workflow instructions. The index explicitly labels the historical manager records.

---

## Installer and RPC assessment

### Installer

No additional merge-blocking installer defect found in the inspected change.

`scripts/install-links.py`:
- Preflights current-name conflicts before retiring links.
- Preserves foreign and uncertain retired entries.
- Backs up links resolving to the exact retired target in this checkout.
- Handles broken links.
- Parses settings before link changes.
- Preserves unrelated settings values and permission bits.
- Rechecks settings before replacement.
- Supports repeat installation.

The filesystem fixtures exercise fresh/idempotent operation, owned retirement, foreign preservation, current-name/documentation conflicts, malformed settings, and settings permissions.

**Limit:** those tests exercise the extracted link helper, not a full global installer run. The shell wrapper still performs its existing package-management behavior. Its unrun status is correctly disclosed.

### RPC recorder

The recorder is reasonably bounded for its declared **read-only smoke** purpose.

Verified against the installed Pi interface:
- RPC prompt and correlated UI response mechanism are real.
- `--tools` supports extension tool names, including `ask_user`.
- Explicit skill/extension loading with ambient discovery disabled is supported.
- `--offline` disables startup network operations; it is not a claim that model calls are offline.
- The script checks unexpected dialogs, failed tool/model events, deadlines, and event count.
- Its result explicitly says semantic acceptance has not been evaluated.

The fake-process tests establish pipe framing and driver handling—not live Pi behavior. Documentation correctly states that this runner cannot produce full planning artifacts, delegate stages, or demonstrate a write-capable sandbox. I am not treating those deliberate limitations as defects.

---

## Evidence reviewed and validation limits

### Actual review scope

Reviewed the working-tree delta against `a04e3df68b09`, including the removed skill bodies and all 15 listed untracked files:

- Planning/refactor regression documents.
- New planner, approval/recovery reference, TinySpec, and renamed brainstorming skill/tests.
- New checker, combined offline tests, installer helper, trace oracle, RPC recorder.
- All three synthetic fixtures.

Also inspected the changed shared skills, coordinator intake, documentation/adoption guidance, installer wrapper, lint/probe wiring, requirements, and README.

### Supplied verification

`/tmp/planner-candidate.log` supports:
- 23 skills linted with zero failures.
- Planner static workflow PASS.
- 30 combined offline tests.
- Five focused suites containing 4, 2, 7, 3, and 6 tests.

That totals the reported **52 offline tests across six suites**.

The supplied log does **not** itself contain command-labelled shell-syntax, Python-compilation, standalone fixture-parser, or diff-check output. Those remain supervisor-reported verification; fixture-parser checks are also present inside the combined tests.

I did not run commands. The counterexamples above are established by reading the complete relevant predicates and control flow, not represented as executed reproductions.

### Preservation-ledger qualification

The ledger provides a useful source-to-owner map. Its baseline-before-replacement timing is attested by the author and supplied context; this review cannot independently prove authoring order from a working-tree snapshot.

`test_preservation_ledger_precedes_retirement` checks row presence and retired-file absence, not chronology. Do not use its name as evidence that source-first timing was mechanically verified.

---

## Smallest acceptance follow-up

1. Add lifecycle integrity checks and negative trace fixtures for F1.
2. Restore the specific operational shared-invocation/application checks and deletion mutations for F2.
3. Address F3 or explicitly document the temporary exact-title limitation.
4. Have the supervisor rerun:
   - `bash scripts/check-skills-lint.sh`
   - Both fixture dependency-parser commands.
   - Shell syntax/Python compilation and `git diff --check`.
5. Supply command-labelled output and the narrow corrective diff for recheck.
6. Keep live dialogue, SpecKit, differential scenarios, and global installation marked **NOT RUN** until separately authorized.

The core refactor does not require architectural rework. The remaining acceptance work is a small correction to the regression checks that are intended to protect it.