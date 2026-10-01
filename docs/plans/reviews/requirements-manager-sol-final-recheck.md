# T012 Final Independent Recheck

## Review

**Verdict: NOT_READY — Merge verdict: BLOCK.**

The operational skill corrections substantially address the original review. However, F4 remains partially unresolved: the actual checker and mutations still do not satisfy T009–T010. Constitution repair also remains incomplete, and completion metadata retains a minor contradiction.

No files were edited, commands executed, commits made, agents delegated, or tasks marked.

### Finding R1 — P1: F4 operational/mutation protection remains incomplete

**Locations:** `scripts/check-requirements-manager-workflow.py:42–78`; `scripts/test-requirements-manager-workflow-mutations.py:25–58`.

**Verified improvements:** Stage-local labels/classes, gate transition, created-plan review, task ownership, and several restored safeguards now have specific diagnostics. The gate-body mutation genuinely removes its body while retaining the heading and diagram. Mandatory-plan and automatic-split mutations now insert contradictory instructions while preserving valid wording.

**Remaining concrete defects:**

1. **The reorder mutation still swaps heading names, not intact blocks.** Lines 32–33 replace `### spec_create` and `### plan_create`, leaving their bodies in place. This repeats the original F4 defect and does not meet the explicit intact-block-reorder requirement.

2. **Some operational bodies remain protected only by labels.** For example, `epic_brainstorm_fix` is checked for four labels, the brief-contract phrase, and its class—not its decision-application instructions. Replacing that section’s substantive contents with its unchanged heading, those four labels, and `stage brief/handoff contract` preserves every checker predicate. The shared skill still contains its global decision-application phrase, so `brainstorm` also passes. This is a static counterexample derived directly from the complete predicate inventory, not an executed mutation.

3. **Specification approval removal is not diagnosed.** Removing `spec_create`’s instruction to obtain and durably record explicit current specification approval, while retaining its labels and briefing phrase, satisfies all predicates. The checker checks overall-review approval but not that specification-approval obligation.

4. **Independent final-review omission is not diagnosed.** Removing the coordinator’s instruction to obtain a fresh independent final review from a non-implementation session, while retaining `No per-task reviews` and the following full-range instruction, satisfies `commit-review` at line 72. Availability of a reviewer elsewhere is not an instruction to perform that review.

5. **Contradiction checks do not cover all carrying contracts.** Inserting the exact tested sentence `Direct requirements must have a plan.` into the coordinator or shared task-generation contract leaves the checker predicates unchanged: line 76 rejects it only in `requirements`. Likewise, upstream automatic-split contradictions in task-generation are outside line 77’s coordinator-only rejection.

6. **Required negative tests remain absent.** The complete six-method mutation file lacks actual omission mutations for per-task commits, independent final review, async-only delegation, specification approval/renewal, capability stops, threshold/class-context eligibility, and upstream coherence. Foreground/parallel/batch-commit *insertions* are useful but do not replace these required omission tests.

**Impact:** Routine validation can still pass after required operational instructions disappear or shared/downstream contracts contradict the approved workflow.

**Smallest correction:** Add the missing section-local obligations and diagnostics; move intact stage blocks in the reorder mutation; add the specified omission mutations and contradictions at every applicable carrier. Continue running these through routine lint. No architectural rewrite or live model trial is necessary.

**Contract evidence:** `docs/plans/requirements-manager-tasks.md:127,135` explicitly requires actual operational bodies, intact order/transitions, approval/capability safeguards, omission mutations, and specific diagnostics.

### Finding R2 — P1: F2 detects invalid constitution content but does not require repairing it before proceeding

**Location:** `skills/epics-manager/SKILL.md:28–35`.

The correction checks missing/template-only constitution content and obtains owner principles, but only instructs recording them “in the established project convention.” It does not require using the detected constitution capability to repair the required constitution or verifying that its content is now valid.

**Concrete compliant failure path:** Detect a template-only required constitution, collect principles, record them in a decision artifact, and proceed to specification work. The stated stop condition—absent question capability or missing owner principles—no longer applies, although the required constitution remains unusable.

**Impact:** The original constitution-content safeguard is only partially restored.

**Smallest correction:** When required constitution content is invalid, apply owner-derived principles through the observed constitution capability and verify the detected constitution is usable; otherwise stop before specification work.

**Original protection:** `/tmp/requirements-manager-prechange/skills/epics-manager/SKILL.md:91–95` expressly requires using the detected constitution capability.

### Finding R3 — P2: F10 current-state prose still contradicts completed FR3

**Location:** `docs/plans/requirements-manager-execution.md:5,72`.

The current-state paragraph says “FR3 evidence pending,” while the correction table marks FR3 completed in this commit. The supplied commit evidence confirms FR3 commit `c50d91368fc91af40fdea34de3336fb0d457caa0`.

**Impact:** Fresh-session recovery still receives inconsistent correction status, though T012 correctly remains pending.

**Smallest correction:** State that FR1–FR3 are committed and only parent T012 disposition/recheck evidence remains pending. Label the T006 dispatch-era statement at line 62 historical when reconciling the tracker.

## Original finding dispositions

“FIXED” below means inspected prompt/code behavior, not demonstrated runtime obedience.

| Finding | Disposition | Current evidence |
|---|---|---|
| F1 | **FIXED** | `epics-manager:140–143` prohibits unresolved material defaults and retains mechanical resolution; actual contradiction mutation at `test-requirements-manager-workflow-mutations.py:67–68`. |
| F2 | **PARTIAL** | Missing/template inspection and owner principles restored at `epics-manager:28–35`; required constitution repair remains absent: R2. |
| F3 | **FIXED** | Mandatory reference, missing-install stop, admission rationale, substantive-scope decision and documentation exception at `epics-manager:22–26`; same sizing authority at `requirements-manager:20–27`. |
| F4 | **PARTIAL** | Real gate-body deletion, class checks and contradiction insertions added; intact-block reorder and important operational/negative coverage remain absent: R1. |
| F5 | **FIXED** | Reusable reading/handoff/interruption contract at `epics-manager:44–54`, referenced by all stages; flagged recovery and originating correction context at `:143–146`. |
| F6 | **FIXED** | Preparation authorization distinguished from final approval at `task-generation:14–27`, `requirements-manager:58–75`, and `epics-manager:123–125`; coordinator implementation approvals remain enforced. |
| F7 | **FIXED** | Same-session created-plan review/correction at `epics-manager:106–119`; stage-local `plan-transition` diagnostic and mutation exist. |
| F8 | **FIXED** | Stage-specific prose/end-turn fallback and mandatory-preflight exception agree in `epic-brainstorming:13–20,56–58`, `REQUIREMENTS.md:13`, and coverage capability inventory. No inferred answer is permitted. |
| F9 | **FIXED** | Suite checks run only for the selected suite directory; custom-tree checks explicitly report SKIP at `check-skills-lint.sh:55–61`; custom-directory test at mutation file `:60–65`. |
| F10 | **PARTIAL** | T001–T011 completion and pending T012 reconciled; obsolete task closing instruction made historical. FR3 pending/completed contradiction remains: R3. |
| F11 | **FIXED** | Specification/clarification briefing immediately before approval at `epics-manager:100–102`; outcome/plan-phase briefing at `:147–149`. |

**Additional T003 boundary: FIXED.** `skills/task-generation/scripts/check-task-order.py:53–54` rejects a first task other than T001. `test_check_task_order.py:69–74` specifically covers lone T002 with `Depends: none`. Existing dependency/story validation remains present.

## Requirement classification

**P:** preserved; **C:** deliberately changed; **R:** deliberately removed; **A:** required component incomplete. References are current skill lines unless noted.

| Rows | Classification and inspected carrier |
|---|---|
| B01–B04 | **P** — Shared exact gate, bounded agenda, orchestrator dialogue, approved bounded application, deferrals and recovery: `epic-brainstorming:27–75`; EPIC conditional transitions `:67–90`. |
| B05 | **P** — Every-stage brief/read/handoff contract: `epics-manager:44–54` and stage entries. |
| B06 | **P + A** — Observed SpecKit, source/specification approval retained; constitution repair incomplete, R2. |
| B07 | **C** — Fixed opus-class combined specification/plan review/create/fix and approval renewal: `epics-manager:104–119`. |
| B08 | **P** — Create-only tasking and overall-review correction ownership: `epics-manager:121–132`. |
| B09–B11 | **P/C** — Independent observed review, material-only flags, mechanical resolution, decisions/deferrals and interrupted correction recovery: `epics-manager:134–149`. |
| B12 | **P** — Earliest-stale recovery, current-content evidence and done revalidation: `epics-manager:40–42,151–158`. |
| B13 | **C** — All eight operational stages exist in canonical order with required portable classes: `epics-manager:67–158`. |
| B14 | **P** — Observed SpecKit capabilities/instructions, reporting and unavailable-stage stops: `epics-manager:28–38`; R2 qualifies constitution content. |
| B15 | **P** — Admission/scope-change/reference and documentation exception restored: `epics-manager:22–26`, `requirements-manager:20–27`, `create-epic:66–85`. |
| B16–B18 | **P** — Common task semantics, sole validator, T001 boundary, manual implicit dependencies, sonnet default, bounded opus/30% exception and format fallback: `task-generation:29–69` and validator/tests. |
| B19 | **P** — EPIC specification/plan/two current approvals/review/provenance intake: `coordinate-implementation:27–48`. |
| B20 | **C** — Direct requirement→tasks without plan/SpecKit, with preparation/final approval distinction: `requirements-manager:56–85`, coordinator `:50–55`. |
| B21 | **P/C** — Usable capabilities and owner-selected bindings; mandatory manager/coordinator stops versus permitted stage fallback: coordinator `:73–97`, shared brainstorming `:13–20`. |
| B22 | **C** — Complete-list three/four boundary, local class/context fit and retained strategy on resume: coordinator `:101–119`. |
| B23 | **P** — One graph, producer-before-consumer order and producer-review defect return: coordinator `:138–165`. |
| B24–B25 | **C** — Consecutive same-class continuity across shared files/internal dependencies/headings; real class/gate/context/scope/integration splits; async-only sequential delegation: coordinator `:146–160`. |
| B26 | **C** — Matching retained context, observed headroom, conservative rotation and inspected failures: coordinator `:200–211`. |
| B27 | **C** — Verified per-task commits, no per-task reviews, one fresh independent full-range review: coordinator `:245–260,272–289`. Regression protection incomplete, R1. |
| B28 | **P** — Durable requirement, traceability review, current authorization and explicit origin handoff: `requirements-manager:35–100`. |
| B29 | **P + A** — Routine checker/mutations wired at `check-skills-lint.sh:53–61`; operational/mutation completeness remains deficient, R1. |
| B30 | **R** — Historical platforms, resolver/schema and named bindings remain excluded; unauthorized material defaults removed. |

### Historical and capability inventory

- **Preserved/approved changes:** Gate; optional orchestrator brainstorm; exact decision application; per-stage source/constraints/authorities; specification and conditional clarification; combined plan pass; create-only tasks; independent overall review; flag categories/never-flag/mechanical rules; owner decisions/deferrals; originating-context correction and interruption recovery; handoff propagation; done/current-approval checks; fixed portable classes.
- **Incomplete:** Required constitution repair; operational regression/mutation inventory identified in R1.
- **Removed deliberately:** Historical platform commands/paths, resolver, rigid JSON state, provider/agent bindings, and speculative material defaults.
- **Capabilities:** Observed SpecKit and unavailable-stage stops, usable questions/delegation, selected class bindings, applicable memory/principles, independent reviewers, and context/session observation are carried. Constitution content is qualified by R2.
- **Shared boundary:** Both managers reuse the same brainstorming and task-generation contracts. EPIC stages remain wrappers around observed SpecKit; direct tasking does not fabricate specification/plan artifacts.
- **Documentation/routing:** README, create-epic, adoption instructions and dynamic discovery preserve the lightweight route and documentation-initialization EPIC exception.

Coverage’s blanket verified statuses must remain qualified by this recheck: **B06 and B29 are incomplete**, and corresponding tracker “corrected” dispositions are not final semantic acceptance.

## Evidence and verification gaps

Read the complete 2,374-line corrected aggregate diff, source plan/tasks, tracker/coverage, original review, exact historical EPIC, all supplied pre-change files, current affected skills/tests, review contract, AGENTS, sizing reference and installation/discovery context.

The range packet contains ordered commit identities rather than a literal two-endpoint range. Together with the complete aggregate diff and supplied commit evidence, it was treated as the authoritative review packet—not independently queried Git history. `watchdog_diff` reported no working-tree changes against `c50d91368fc9`; this was not substituted for committed-diff review.

**Raw reported evidence:** correction verification log shows 24 skills/0 failures, operational checker PASS, six mutation methods passing, and task-order PASS. It does **not** contain raw focused-contract/validator-unit output or command-labelled diff-check output; those remain tracker attestations.

**Supervisor validation after corrections:** run routine lint, the complete mutation suite, all adjacent focused contract tests, seven validator units, and approved-task ordering; retain command-labelled output. Execute the static counterexamples above as new negative tests.

Static tests and semantic review cannot establish model obedience, live owner dialogue, SpecKit execution, async scheduling, session headroom/resumption, or actual reviewer independence. No live trial or paid discovery probe was performed.

**Parent action:** Resolve R1/R2, reconcile R3 and coverage/dispositions, then perform the bounded final recheck. Parent alone records T012 and commits final evidence. Run `/reload` inside pi after loading changed skills.