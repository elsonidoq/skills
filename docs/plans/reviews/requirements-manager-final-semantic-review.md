# T012 Final Semantic Review

## Review — findings

### F1 — P1: Material speculative defaults were restored
**Location:** `skills/epics-manager/SKILL.md:113–118`

Overall review flags material friction or specification deviation with a “recommended **applied default**.” This contradicts the prohibition on speculative material defaults at lines 89–90 and 137–138, the approved plan at `docs/plans/requirements-manager.md:100`, and the pre-change decision rule at `/tmp/requirements-manager-prechange/skills/epics-manager/SKILL.md:205`.

**Impact:** A reviewer is instructed to apply an unresolved product/specification choice before the owner decides. Later approval does not undo that unauthorized mutation.

**Smallest correction:** Recommend—but do not apply—unresolved material alternatives. Apply only mechanical corrections or recorded owner decisions.

### F2 — P1: Constitution-content validation disappeared
**Location:** `skills/epics-manager/SKILL.md:15–27`

Preflight checks governing principles and installed constitution capabilities, but no longer checks whether a required constitution is missing or still template text. The pre-change workflow explicitly handled that condition and obtained owner-defined principles before proceeding (`/tmp/requirements-manager-prechange/skills/epics-manager/SKILL.md:91–95`).

**Impact:** Installed commands/assets can satisfy the rewritten preflight despite an unusable constitution. B06’s claimed preserved principles safeguard is incomplete.

**Smallest correction:** Restore a portable content-validity checkpoint: inspect the detected constitution; obtain missing principles from the owner through the detected capability, or stop. Do not restore fixed paths or invent policy.

### F3 — P1: EPIC admission/scope-change safeguards and the required reference were removed
**Location:** `skills/epics-manager/SKILL.md:73–79`

The mandatory, linked spec-driven-development reference became “apply the spec-driven reference where installed.” The EPIC skill contains no admission-sizing validation, recorded sizing rationale, scope-change route decision, or documentation-initialization exception.

Those checks existed at `/tmp/requirements-manager-prechange/skills/epics-manager/SKILL.md:100–115` and must remain under `docs/plans/requirements-manager.md:98`. Requirements Manager also refers to “existing sizing guidance” without identifying its authoritative reference (`skills/requirements-manager/SKILL.md:20`).

**Impact:** Direct EPIC entry/resume no longer enforces these protections. `create-epic` retaining them does not protect callers entering `epics-manager` directly.

**Smallest correction:** Restore the required reference and EPIC admission/reconsideration checkpoints; reference the same sizing owner from Requirements Manager rather than duplicating it.

### F4 — P1: Operational regression and mutation coverage does not meet the approved contract
**Locations:**  
- `scripts/check-requirements-manager-workflow.py:25–63`
- `scripts/test-requirements-manager-workflow-mutations.py:18–58`
- `scripts/check-skills-lint.sh:53–56`

The routine checker searches globally for phrases and ordered headings; it does not validate each stage’s operational body or transitions. The mutation named “remove operational body with diagram intact” removes only the **heading** (`:27–28`). Reordering swaps heading names, not intact stage blocks (`:30–34`). “Reinstate mandatory direct plan” and “automatic heading/file/dependency split” merely replace permissive phrases with `REMOVED`, rather than inserting the contradictory policies.

**Concrete static counterexamples:**
- Removing the `brainstorm_gate` body at `skills/epics-manager/SKILL.md:48–53`, while retaining its heading, leaves every routine checker predicate satisfied.
- Changing `spec_create`’s class to `opus-class` leaves the routine checker satisfied: it requires that stage’s heading, but not its class. The focused class test is not invoked by routine lint.
- Adding a mandatory-plan or automatic-split instruction while retaining the checked phrases is not rejected.

Named mutations/checks are also missing for gate transitions, plan review/fix, owner-approval removal, stale-approval handling, and several historical source/recovery obligations required by T009–T010 (`docs/plans/requirements-manager-tasks.md:127,135`).

**Impact:** A passing routine check can coexist with missing operational stages or contradictory policy. B29’s “verified” status overstates protection.

**Smallest correction:** Check requirements inside their operational sections, including transitions and contradictory instructions. Add actual body/block deletion, intact-block reorder, class-change, gate-bypass, and contradictory-policy mutations with specific diagnostics. Wire the required checks into routine validation. These remain static prompt checks—not proof of model obedience.

### F5 — P1: The every-stage source/handoff contract and flagged-review recovery are incomplete
**Locations:** `skills/epics-manager/SKILL.md:15–20,83–94,109–119,130–138`

The historical contract required **every delegated stage** to read the selected source, settled/non-obvious constraints, cited authorities, instructions/principles, and receive the prior handoff (`/tmp/requirements-manager-historical-epics-manager.md:165–185,254–278`). The replacement specifies a manager preflight read, but does not impose that complete reading/handoff contract on every assigned stage.

Historical flagged-item recovery also persisted pending items/answers and returned owner overrides to the originating correction context (`historical export:155–159,238–251`). The new plan stage mentions same-context correction; overall review has no corresponding owner-answer application or interrupted-flag recovery rule.

**Impact:** B05/B11 are only partially preserved. An isolated stage can lose authoritative constraints or previous reasoning; interrupted review lacks a defined pending-question recovery path.

**Smallest correction:** Add one reusable stage-brief contract and reference it from every stage. Define portable persistence/re-presentation of pending flags and same-context application of owner answers where supported, with durable handoff otherwise. No historical JSON schema is needed.

### F6 — P1: Shared tasking requires approval before the producer establishes it
**Locations:**  
- `skills/task-generation/SKILL.md:14–24`
- `skills/requirements-manager/SKILL.md:33–43,54–77`
- `skills/epics-manager/SKILL.md:98`

The shared adapter requires an approved durable requirement and applicable current approval evidence before generating tasks. Requirements Manager preserves the requirement, resolves decisions, and generates tasks **before** its explicit requirement/tasks approval step. It establishes no preceding requirement-approval checkpoint. EPIC task entry similarly calls the source/specification/plan “current approved,” although plan approval is not established before tasking.

**Impact:** Literal compliance stops task production before the workflow can reach its documented approval gate, or introduces an undocumented extra approval.

**Smallest correction:** Distinguish authorization to prepare tasks and already-applicable upstream approvals from final requirement/task implementation approval. Do not require final producer approval before its artifacts exist; retain the coordinator’s current-approval checks.

### F7 — P2: Same-turn plan review/fix is not fully operational
**Location:** `skills/epics-manager/SKILL.md:83–94`

The stage reviews/fixes the specification and creates a plan, but provides no step to review/correct the created plan within that pass. Revision-4 T004 explicitly requires “same-turn plan spec-review/create/review/fix” (`docs/plans/requirements-manager-tasks.md:80`).

**Impact:** This portion of the accepted stage contract is absent, although overall review still provides a later check.

**Smallest correction:** Explicitly review and mechanically correct the produced plan in the same stage/context, retaining owner gates and approval renewal.

### F8 — P2: Question-capability fallback guidance is inconsistent
**Locations:** `skills/epic-brainstorming/SKILL.md:13–18,54–55`; `REQUIREMENTS.md:13,20`

The shared mechanism stops when question capability is missing. The runtime table still instructs “Ask in prose and end the turn,” and requires dependency statements to remain synchronized. The historical and pre-change EPIC owner-communication rules also described that fallback.

**Impact:** Runtime/adoption guidance and the new workflow disagree about the unavailable-tool path. Coverage’s capability inventory does not resolve the discrepancy.

**Smallest correction:** Document the intended stage-specific stop/fallback policy consistently in REQUIREMENTS, skills, and coverage. Never infer an owner answer.

### F9 — P2: Custom-directory lint validates workflow contracts from the wrong tree
**Location:** `scripts/check-skills-lint.sh:5,53–56`

The existing `[skills-dir]` interface lints the supplied directory, but the newly invoked workflow checker loads skills from its own repository root (`scripts/check-requirements-manager-workflow.py:9–17,71–76`).

**Impact:** A custom candidate skills tree receives workflow results for the checked-out suite instead. The results can miss candidate regressions or fail for unrelated checkout conditions.

**Smallest correction:** Pass the selected tree to the workflow checks, or explicitly restrict these suite-wide checks to the default suite-tree invocation.

### F10 — P2: Completion metadata still describes implementation as unstarted/incomplete
**Locations:** `docs/plans/requirements-manager-execution.md:5`; `docs/plans/requirements-manager-tasks.md:162`

The execution tracker’s current-state paragraph says batch 3 is next, while its batch/task tables mark it completed. The task artifact’s closing instructions say “No skill implementation has begun,” despite T001–T011 being checked complete.

**Impact:** Fresh-session recovery receives conflicting current-state instructions.

**Smallest correction:** Reconcile current-state prose with the completed implementation tables while leaving T012 pending for parent disposition. Label preparation-era statements historical where retained.

### F11 — P2: Required approval briefings were removed
**Location:** `skills/epics-manager/SKILL.md:78–79,117–119`

The rewritten approval checkpoints require approval but omit the specification/clarification summary and the outcome-plus-plan-phase briefing required immediately before approval in the pre-change workflow (`/tmp/requirements-manager-prechange/skills/epics-manager/SKILL.md:118–120,169–173`). General question-tone guidance does not require those briefings.

**Impact:** Approval remains explicit and durable, but its required owner-facing context has weakened.

**Smallest correction:** Restore concise manager-level briefings immediately before the two approval requests.

## Scope and evidence

Read completely:
- Review contract, AGENTS, approved plan, revision-4 tasks, execution tracker, coverage matrix.
- Complete `/tmp/requirements-manager-implementation.diff` (1,963 lines).
- Exact historical EPIC and every file in `/tmp/requirements-manager-prechange/`.
- Current changed skills, tests, routine wiring, and relevant discovery/adoption/reference context.

Reviewed exported committed range:

`e21a6b27aed02192aecac739e5ef033e6ce61dcf..1a067b02b45747d907619f9f5aebe7643208dd73`

`watchdog_diff` reports no working-tree changes; that was **not** used as a substitute for committed-range review. No edits, commands, commits, delegation, or task marking were performed.

## Per-row classification

**P:** preserved. **C:** changed-deliberate. **R:** removed-deliberate. **A:** required component absent/incompletely preserved. Classifications describe inspected prose, not live execution.

| Row | Classification | Inspected carrier / qualification |
|---|---|---|
| B01 | P | Shared gate `epic-brainstorming:25–40`; EPIC transitions `:46–53`. Test protection incomplete: F4. |
| B02 | P | Shared bounded agenda and orchestrator dialogue `:38–54`. |
| B03 | P | Exact bounded application `:57–63`; both managers invoke it. |
| B04 | P | Shared agenda/answer/deferral persistence and recovery `:65–72`. |
| B05 | P + A | Manager reads retained; every-stage source/handoff obligation incomplete: F5. |
| B06 | P + A | SpecKit/spec approval retained; constitution validity and readiness/admission safeguards incomplete: F2/F3. |
| B07 | C + A | Opus spec review/plan production and renewal retained; combined plan review/fix incomplete: F7. |
| B08 | P | Create-only EPIC tasking and overall-review correction ownership `:98–105`. |
| B09 | P/C + A | Independent owner-selected review and durable approvals retained; speculative defaults/briefing/recovery defects: F1/F5/F11. |
| B10 | P, contradicted | Never-flag mechanical list and single-option resolution retained; material applied-default rule conflicts: F1. |
| B11 | P + A | Decisions/deferrals and plan correction context retained; overall-review pending-flag recovery incomplete: F5. |
| B12 | P | Earliest-stale recovery and done revalidation `:31–33,122–128`. |
| B13 | C | All eight operational headings in canonical order; portable fixed stage classes retained. Not diagram-only. |
| B14 | P | Observed SpecKit commands/assets, evidence and stage stops `:22–29`; constitution content is separate F2. |
| B15 | P + A | Create-epic/Requirements sizing retained; EPIC admission/change/exception checks absent: F3. |
| B16 | P | Common task contract `task-generation:34–38,62–67`. |
| B17 | P | Sole relocated validator, earlier dependencies/story checks, manual implicit/stage checks. Automated T001-start limitation noted below. |
| B18 | P | Sonnet default, bounded decomposition, 30% exception, local format/fallback `:40–50`. |
| B19 | P | EPIC spec/plan/two approvals/review/provenance intake `coordinate-implementation:27–48`. |
| B20 | C, with contradiction | Direct no-plan/no-SpecKit intake is explicit; producer preapproval ordering conflicts: F6. |
| B21 | P/C, with drift | Callable selections and capability stops retained; local eligibility deliberately changes delegation requirements; question fallback inconsistent: F8. |
| B22 | C | Complete implementation count, three/four boundary, class/context fit and retained resume strategy `:101–119`. |
| B23 | P | One graph, fixed prerequisite order and producer-review return `:138–165`. |
| B24 | C | Consecutive homogeneous context-coherent batches; internal dependencies/files/headings permitted `:146–156`. |
| B25 | C | Evidenced splits, sequential implementation batches, async/background delegation `:152–160`. |
| B26 | C | Matching retained context, observed headroom, conservative rotation, inspected failures `:200–211`. |
| B27 | C | Separate verified task commits; no per-task reviews; fresh full-range final review `:245–260,272–289`. |
| B28 | P, with contradiction | Durable requirement, review, approval and origin-marked handoff retained; premature shared approval requirement: F6. |
| B29 | P + A | Routine wiring exists; required operational/mutation coverage incomplete: F4. |
| B30 | R, not fully achieved | Obsolete platforms/paths/state/bindings remain removed; speculative material defaults were reintroduced: F1. |

The blanket “all rows verified/no unaccounted removal” statements at `docs/plans/requirements-manager-coverage.md:91–109` should be revised to reflect these partial/absent components.

## Operational and historical inventory

| Stage / inventory item | Classification |
|---|---|
| Gate → optional brainstorm → bounded decision application | P/C: executable shared mechanism; gate class deliberately portable sonnet-class. |
| Specification creation and optional clarification | P/C: explicit operational stage; clarification conditional as approved. Reference/admission safeguards A. |
| Plan spec-review/create/review/fix | C + A: fixed opus-class and spec review present; created-plan review/fix absent. |
| Create-only tasking → overall review | P: operational ownership present; task approval precondition conflicts with producer order. |
| Overall review → done | P/C: independent review, current approval and fresh handoff present; material-default and recovery defects remain. |
| Reading settled/non-obvious facts and cited authorities at every stage | A in part: manager preflight retained, complete per-stage brief contract missing. |
| Flag categories / never-flag list / single-option mechanics | P in overall review; material speculative default is an unauthorized restoration. |
| Owner dialogue / decision capture / deferrals | P; unavailable-question fallback guidance inconsistent. |
| Same-context owner correction / interrupted flagged-item recovery | P for plan correction; A for the complete overall-review recovery protocol. |
| Handoff context capture and propagation | P for capture; A for explicit every-stage propagation. |
| Done report / stale artifact and approval detection | P. |
| Obsolete resolver, rigid JSON state, platform commands/paths, historical provider/agent bindings | R as approved. |

The source-first baseline derivation is **attested** by the artifacts. The exported aggregate diff does not independently establish intermediate authoring order; I found no evidence proving circular derivation. However, its summaries omit historical operational detail and its “verified” labels do not compensate for F2–F7.

## Capability/fallback inventory

| Inventory row | Classification |
|---|---|
| SpecKit discovery, observed instructions, unavailable-stage stops | P; constitution-content handling A. |
| Question/delegation tools | P/C; question fallback drift F8. |
| Owner class/model bindings | P: usable observed selections required, no skill hard-coded provider/model IDs. |
| Applicable memory and principles | P through applicable project conventions; constitution validity A. Coordinator explicitly checks discoverable memory capability. |
| Independent reviewer | P/C: observed owner-selected EPIC reviewer and fresh final implementation reviewer; unavailable reviewer blocks acceptance. |
| Context/session observation | C: matching context/headroom, supported resume, conservative rotation and failure inspection retained. |

## Current protection comparison

- **Retained:** durable content/revision approvals, stale/unverifiable-approval stops, EPIC’s two approvals, required source/review lineage, workspace preservation, dependency ordering, documentation/acceptance coverage, 30% opus exception, unavailable-capability reporting.
- **Deliberately changed:** direct requirement/tasks intake, bounded local eligibility, mandatory delegation above three, context-continuity batches, context-aware rotation, per-task commits and one final review.
- **Weakened/unaccounted:** constitution validity, EPIC admission/reference checks, complete stage reading/handoff/flag recovery, approval briefings and operational regression coverage.
- **Routing/discovery:** README, create-epic, adoption guidance and dynamic discovery support the lightweight route. No stale active validator caller was found; old-path references are historical review records.
- **Direct-input authorization:** No concrete implementation authorization bypass found. Coordinator independently requires current durable requirement/task review and owner authorization, and blocks ambiguous origin. F6 is an ordering conflict, not permission to implement unapproved tasks.

## Verification and limitations

**Reported implementation runs**, not rerun by this reviewer:
- 29 focused tests: brainstorming 4; task contract 2; validator 6; EPIC 4; batching 3; intake 6; Requirements Manager 4.
- Operational checker and five mutation test methods.
- Suite lint, approved task-order check and diff check.
- Shell syntax/static routing/discovery checks.

**Static walkthroughs:** Coverage records scenarios for local/delegated boundaries, resumed counts, context rotation, coherent shared-file batches, approvals, missing capabilities and SpecKit applicability. These are prompt inspections, not executed scheduling or owner-dialogue trials.

**Missing/unavailable live evidence:** model obedience, owner question execution, SpecKit stages, async scheduling, child resumption/context observation, installed discovery probe. This fresh semantic review does not supply those trials.

**Additional inherited limitation:** the unchanged relocated task validator checks consecutive numbering only after a preceding task (`skills/task-generation/scripts/check-task-order.py:51–52`); a lone `T002` with `Depends: none` is not rejected. The new prose requires T001, so that boundary still needs manual inspection. This is not charged as a newly introduced validator defect.

Per-task commit identities and raw test logs are not present in the supplied tracker; its commit column says “recorded with T… change.” The full review range is supplied, but separate verified task-commit history cannot be independently attested from this aggregate diff alone.

## Verdict

**NOT_READY — Merge verdict: BLOCK.**

Disposition F1–F6 before readiness; address or explicitly disposition the P2 findings. Update coverage/evidence classifications after corrections. Do not treat static passes as proof of runtime behavior. Parent should record T012 and any scoped fixes; this reviewer has not marked tasks.