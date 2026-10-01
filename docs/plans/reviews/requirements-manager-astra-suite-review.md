# ASTRA connected-suite review — consolidated

## Review

**Overall verdict: NOT_READY — Merge verdict: BLOCK.**

The architecture is coherent: two task producers reuse shared brainstorming/task semantics and converge on one coordinator. FR1–FR3 materially improved the contracts. Remaining deficiencies concern operational regression coverage, constitution repair, the newly authorized small-EPIC recommendation, and several integration/documentation details.

- **Correct:** plan-free direct tasking, preparation-versus-implementation authorization, origin-specific intake gates, the three-task execution boundary, context-coherent batching, per-task commits, and independent full-range final review.
- **Fixed by this reviewer:** none; read-only.
- **Findings:** three P1 and three P2 findings below.
- **Evidence qualification:** static source/patch review, not executed workflow or model-obedience proof.

The subsequently supplied Sol recheck was read as additional evidence. Its remaining test, constitution, and metadata findings agree with this review. It did not replace the independent property derivation or broader integration inspection.

## 1. Scope and evidence

### Reviewed snapshot

- Baseline supplied by the original range export:  
  `e21a6b27aed02192aecac739e5ef033e6ce61dcf`
- Corrected tip supplied by the corrected commit/range exports:  
  `c50d91368fc91af40fdea34de3336fb0d457caa0`

The corrected range file contains an ordered commit list rather than a literal two-endpoint range. These identities and the supplied aggregate patch were reviewed as exported evidence, not independently queried Git history.

Read completely:

- AGENTS, approved plan including diagram, current tasks, coverage and execution tracker.
- Original semantic review and historical task-review records.
- Complete **2,374-line corrected implementation patch**.
- Exact historical EPIC and every supplied pre-change export.
- All named connected skills, relevant brainstorming/review/handoff/memory/closeout contracts.
- README, REQUIREMENTS, authoritative SDD reference and documentation index.
- Installer, discovery probe, lint, workflow checker/mutations and focused workflow/validator tests.
- Corrected commit evidence and raw verification log.
- Subsequent `/tmp/requirements-manager-final-recheck.md`.

`watchdog_diff` reported no working-tree changes against reviewer-launch HEAD. This was **not** substituted for committed-patch review.

### Evidence limits

The raw correction log reports:

- 24 skills checked, zero lint failures.
- Workflow checker PASS.
- Six mutation test methods passing.
- Task-order PASS.

It does not contain raw output for every focused test or command-labelled diff check attested by the tracker. Commit identities establish the exported commit structure, not independent proof that every commit followed verification.

No commands, edits, commits, installations, delegates or paid probes were performed by this reviewer.

## 2. Findings

### A1 — P1: Required operational and mutation coverage remains incomplete

**Classification:** incomplete original scope; residual F4.  
**Locations:** `scripts/check-requirements-manager-workflow.py:43–78`; `scripts/test-requirements-manager-workflow-mutations.py:25–58`; `scripts/check-skills-lint.sh:57–60`.

FR2 adds meaningful protections, but ordinary validation still permits expressly prohibited omissions and contradictions.

Concrete counterexamples derived from the complete predicate inventory:

1. **Shared invocation removal:** removing Requirements Manager’s operational shared-brainstorm section (`skills/requirements-manager/SKILL.md:47–54`) leaves routine predicates satisfied. Its prerequisite list still mentions the skill, also satisfying the focused name-presence test.
2. **Label-only stage body:** `epic_brainstorm_fix` can lose its substantive decision-application instructions while retaining its heading/class, four labels and stage-brief phrase. No stage-local predicate requires its actual application behavior.
3. **Conditional transition:** changing the brainstorm output destination from `epic_brainstorm_fix` to `spec_create` is not diagnosed.
4. **Specification approval:** removing the instruction to obtain durable current specification approval before planning, while retaining the briefing and labels, is not diagnosed.
5. **Final independent review:** removing the coordinator’s instruction to obtain a fresh independent final review, while retaining “No per-task reviews” and the full-range sentence, satisfies `commit-review`.
6. **Contradictions in other carriers:** the exact tested sentence “Direct requirements must have a plan.” is rejected only in Requirements Manager—not TG or the coordinator. Upstream automatic-split contradictions likewise escape the coordinator-only rejection.
7. **EPIC intake:** the routine checker does not enforce the EPIC specification/plan/two-approval intake obligations covered by the separately invoked focused intake test.
8. **Reorder mutation:** lines 32–34 still exchange heading names instead of moving intact stage blocks.

The six-method mutation file also lacks required omission cases for per-task commits, independent final review, async-only delegation, specification approval/renewal, capability stops, threshold/class-context eligibility, and upstream coherence. Contradiction insertions are useful but do not replace those omission tests.

**Impact:** routine validation can pass after essential operational instructions disappear or shared/downstream contracts contradict the workflow.

**Smallest correction:** add section-local behavioral predicates and named diagnostics; move intact blocks for the reorder mutation; add the specified omissions and contradictions at every applicable carrier; wire relevant focused checks into ordinary validation or consolidate them there.

**Qualification:** these are source-proven static counterexamples, not reviewer-executed mutations. The independent Sol recheck corroborates the principal cases.

---

### A2 — P1: Constitution detection does not complete repair and validation

**Classification:** incomplete preservation of original scope; residual F2.  
**Location:** `skills/epics-manager/SKILL.md:28–35`.

The manager detects missing/template-only constitution content and obtains owner principles, but only requires recording them in the established project convention. It does not require applying them through the detected constitution capability or verifying the resulting constitution before specification.

The pre-change contract explicitly required using that capability (`/tmp/requirements-manager-prechange/skills/epics-manager/SKILL.md:91–95`).

**Compliant failure path:** detect template-only constitution → obtain principles → record them in a decision artifact → continue, although the required constitution remains unusable.

**Impact:** downstream SpecKit work can receive invalid governing input or fail later.

**Smallest correction:** when required constitution content is invalid, apply owner-derived principles through the observed constitution capability and verify the detected constitution is usable; otherwise stop before specification. Do not reopen a valid settled constitution.

---

### A3 — P1: Newly authorized small-EPIC recommendation is not explicit

**Classification:** **new owner-authorized routing addition**, not a retroactive defect in the earlier implementation scope.  
**Location:** `skills/epics-manager/SKILL.md:22–26`.

EPIC Manager references sizing guidance but never names `requirements-manager`, explicitly recommends it for genuinely small fresh work, or defines that owner-choice handoff. The reference recommends direct tasks; the named cross-skill route remains implicit.

**Impact:** direct EPIC entry need not discover the intended lightweight producer.

**Smallest correction:** add one admission branch before EPIC-only capability checks:

- Recommend `requirements-manager` when newly assessed work does not justify the pipeline under the shared reference.
- Ask and preserve the owner’s route choice.
- Preserve the source and valid artifacts.
- Preserve the documentation-initialization exception.
- Do not reclassify admitted/resumed work merely because uncertainty was resolved.
- Reconsider admission only for substantive scope change or explicit owner direction.
- Test fresh-small, exception and admitted/resumed cases.

Reference the existing sizing guidance; do not copy its thresholds.

---

### A4 — P2: Delegated architectural planning is disconnected

**Classification:** original-scope integration omission introduced by the EPIC rewrite; helper fallback policies are preexisting.  
**Locations:** `skills/epics-manager/SKILL.md:104–119`; `skills/delegating-architectural-planning/SKILL.md:31–38,59–68`.

The pre-change EPIC manager conditionally invoked `delegating-architectural-planning` when approved work called for it (`prechange epics-manager:137–141`). The restored stage no longer references it.

If reconnected, the helper’s standalone fallback policies need explicit precedence: choosing an observed agent or offering local planning plus separate review must not override EPIC’s fixed opus-class, owner-selected binding, stop rules and same-pass plan review/fix.

**Impact:** the connected suite contains two planning contracts without an explicit adapter boundary; an existing conditional integration disappeared.

**Smallest correction:** restore the conditional reference and specify that manager stage constraints govern when called from `plan_create`. Include upstream context-coherence requirements in that brief.

---

### A5 — P2: FR3 completion metadata contradicts itself

**Classification:** incomplete correction of original F10.  
**Locations:** `docs/plans/requirements-manager-execution.md:5,72`.

The current-state paragraph says “FR3 evidence pending,” while the table marks FR3 completed and the supplied commit evidence confirms its commit.

**Smallest correction:** state that FR1–FR3 are committed and only review disposition remains pending. Explicitly label the T006 dispatch-era statement at line 62 historical.

---

### A6 — P2: Sizing criteria remain duplicated

**Classification:** preexisting suite-level duplication, not introduced by FR1–FR3.  
**Locations:** `skills/create-epic/SKILL.md:68–70`; `docs/best_practices_spec_driven_development.md:63–69`.

`create-epic` reads the authoritative reference but repeats its three-condition rule. The copies agree today.

**Impact:** the latest single-source sizing property is only partially satisfied.

**Smallest correction:** reference the authoritative sizing section instead of repeating its conditions; retain adapter-specific verdict, exception, owner-choice and handoff instructions.

## 3. Source-derived property matrix

### Derivation and notation

Invariant families were derived before inspecting corrected replacement skills from the latest owner request, approved plan/diagram, historical EPIC, pre-change protections and review history.

Sources:

- **O:** owner properties/additions in this request.
- **P:** `docs/plans/requirements-manager.md`.
- **T:** current task artifact.
- **H:** exact historical EPIC export.
- **E0/C0:** pre-change EPIC/coordinator.
- **SDD:** authoritative best-practices reference.

Carrier abbreviations expand to `skills/<name>/SKILL.md`: **E** epics-manager; **RM** requirements-manager; **B** epic-brainstorming; **TG** task-generation; **C** coordinate-implementation; **CE** create-epic; **DAP** delegating-architectural-planning.

**W/M:** routine checker/mutation files. **Focused:** inspected adjacent tests. **Manual:** this static inspection. **PASS does not mean runtime execution.**

| # | Source | Precise invariant | Carrier / evidence | Status and limitation |
|---|---|---|---|---|
| 1 | O1; SDD:63–91 | Fresh small EPIC recommends RM, asks route choice, preserves artifacts/admission/exception | E:22–26; manual | **FAIL**, A3 |
| 2 | O2; P:102–114 | EPIC-sized requirement uses shared sizing evidence and owner route choice, not count-only conversion | RM:20–27; focused route test/manual | **PASS**; explicit named destination would improve clarity |
| 3 | E0:100–115; SDD:84–91 | Record admission rationale; resolved uncertainty does not invalidate admission; substantive scope change reopens route | E:22–26 plus mandatory SDD reference | **PASS**, indirectly carried by required reference |
| 4 | O1; T008 | Documentation-init EPIC exception survives routing | CE:72–78; E:26; RM:24–25; initialize-documentation:116–119 | **PASS**, W/manual |
| 5 | P:21–22,102–114 | Durable requirement→tasks without intermediate spec/plan or SpecKit | RM:35–65; TG:22–27 | **PASS**, W/focused |
| 6 | P:102–114 | Preserve scope, criteria, exclusions, constraints, evidence, decisions and deferrals | RM:35–45 | **PASS**, focused/manual |
| 7 | H:289–377; P:55–66; O8 | Both managers invoke one original shared gate/session/application mechanism | E:67–90; RM:47–54; B:27–75 | **PASS** carrier; omission protection incomplete, A1 |
| 8 | H gate; P:59–62 | Exact outputs; skip settled/mechanical uncertainty; trigger material unresolved direction/tradeoffs | B:27–42 | **PASS**, focused B |
| 9 | H:331–345; O8 | Agenda ≤3, alternatives/recommendation, orchestrator one-question-at-a-time dialogue | B:40–58 | **PASS**, focused B |
| 10 | H:349–377; P:63–64 | Exact approved bounded application; preserve structure/deferrals, invent no scope | B:60–66; E:84–90 | **PASS**, focused/manual |
| 11 | H:155–163,255–277 | Persist agenda/answers/deferrals/handoff; recover pending questions and changed source | B:68–75; E:44–54 | **PASS**, focused/W/manual |
| 12 | H pipeline; P:82–100; T004 | Executable canonical stages and optional branch, not diagram-only | E:56–158 | **PASS** carrier; transition/body tests partial |
| 13 | P:20,66,82–100; O6 | Gate/fix/spec/tasks sonnet, plan opus; dialogue orchestrator-owned; selected independent reviewer | E headings:67–134 | **PASS**, W/focused |
| 14 | H:165–186; T004 | Every stage receives source, verbatim settled constraints, authorities, principles/instructions and prior handoff | E:44–54 and stage inputs | **PASS**, restored reusable brief contract |
| 15 | H:103–107; E0:91–95 | Required constitution usable before spec; repair through detected capability or stop | E:28–35 | **PARTIAL**, A2 |
| 16 | E0 capabilities; P:98–100 | EPIC wraps observed installed SpecKit capabilities and stops when required capability is absent | E:28–38,94–149 | **PASS** static; live toolkit untested |
| 17 | E0:100–107; O7 | Read/apply authoritative SDD reference; missing reference stops; installation resolves it | E:22–24,94–97; installer:33,78–81,143–153 | **PASS** source inspection; installer not run |
| 18 | O7 | Sizing has one referenced authority, not copied independent rules | E:22–26; RM:20–25; CE:68–70 | **PARTIAL**, A6 |
| 19 | P:98; E0 approval | Conditional clarification; spec briefing and explicit current approval before planning | E:98–107 | **PASS** carrier; routine approval assertion missing |
| 20 | H plan; P:96; T004 | One opus pass reviews/fixes spec, creates and reviews/fixes plan; owner material gates | E:104–119 | **PASS**, W/focused/manual |
| 21 | E0:137–141; O suite scope | Approved delegated architectural planning composes with EPIC constraints | E:104–119; DAP:31–68 | **PARTIAL**, A4 |
| 22 | H tasks; P:96; T004 | Task creation create-only; later overall review owns correction | E:121–149; TG:62–69 | **PASS**, W/focused |
| 23 | P diagram; original F6; O | Preparation authorization suffices; final approval follows production/review | TG:14–27; RM:58–61,73–85; E:123–125 | **PASS**, focused/W |
| 24 | H flags; E0 decisions; P:100 | No speculative material defaults; resolve mechanics; preserve owner answers/correction context | E:114–119,140–149,160–168 | **PASS**, W/M/manual |
| 25 | E0:169–193; O | Overall briefing, independent review evidence, current approval and durable fresh-session handoff | E:134–158 | **PASS**, focused/W/manual |
| 26 | E0 resume; P:98,111–114 | Content/revision approval, renewal and stale/unverifiable stop | E:40–42,116,148–158; RM:43–45,82–85; C:26–60 | **PASS**, focused/manual |
| 27 | P:68–80; O6 | Every task has outcome, prerequisites, files/interfaces, evidence, capabilities, class and rationale | TG:34–45 | **PASS** manual; automated field coverage limited |
| 28 | P:73; E0 tasks; O6 | Sonnet default, opus only nondecomposable; >30% needs recorded exception | TG:42–45 | **PASS** manual; W checks only part |
| 29 | P:20,73; O6 | Task complexity, fixed stage classes and concrete runtime model selection remain distinct | TG:36–45; E headings; C:91–97 | **PASS**, structural separation; no changed-skill provider IDs |
| 30 | P:74–76; O5 | Complete scope/exclusions/docs/integration coverage and independent evidence/story acceptance | TG:36–60; RM:62–80; E:110–130 | **PASS**, focused/manual |
| 31 | P:75,78; T003 | One validator; T001, contiguous IDs, earlier dependencies/ranges/story continuity; manual implicit/stage checks | TG:47–69; validator:17–86 | **PASS** inspection; seven units, arbitrary stage/setup continuity manual |
| 32 | P:76; AGENTS | Discover project formats; no global private state/schema/path requirement | TG:14–20,47–52; RM:14–18; E:37–42 | **PASS**, manual |
| 33 | P:120–124 | EPIC intake retains spec/plan/tasks/two approvals/review/provenance/stage evidence | C:33–48 | **PASS** carrier/focused; routine protection incomplete |
| 34 | P:120–124 | RM/standalone require durable source/tasks/current review/authorization; ambiguous origin blocks | C:14–31,50–60 | **PASS**, focused/W/manual |
| 35 | P:124; O | Installed SpecKit alone imposes no plan on direct inputs; applicable unavailable fallbacks honest | C:62–70 | **PASS**, focused/manual |
| 36 | P:23,128–134; O3 | ≤3 local only with selected current model/class, bounded scope and observed context fit | C:99–119,184–190 | **PASS**, W/focused; no live execution |
| 37 | P:126,134; O4 | >3 delegates; complete implementation count excludes reviews; remaining count does not downgrade | C:101–119 | **PASS**, W/focused |
| 38 | P:116–141; O4 | One graph/tracker/integration algorithm; sequencing defects return to producer | C:137–180 | **PASS**, focused/manual |
| 39 | P:132; O4 | Consecutive homogeneous producers/consumers may share files/headings in sequential batch | C:146–156 | **PASS**, focused/W/M |
| 40 | P:132; O4 | Real class/gate/context/incompatible/external boundary splits; 5–7 guidance only; no padding | C:151–160; TG:54–60 | **PASS**, focused/W/M/manual |
| 41 | O4–5; T005 | Plans/tasks prepared for context coherence; coordinator owns batching | E:110–130; TG:54–60; RM:63–65,91–94 | **PARTIAL** across whole suite, DAP gap A4 |
| 42 | T policy; O4 | Async/background delegation only; sequential implementation batches | C:158–160,81–84 | **PASS**, W/M/focused |
| 43 | P:137–139; AGENTS | Supported matching useful-context resume; observed headroom; conservative rotation; no blind retry/model switch | C:184–211 | **PASS**, focused/W/manual |
| 44 | P:140; O3–4 | Verify/integrate/commit each task before next; owner resolves commit conflict; no per-task reviews | C:231–268,272–274 | **PASS**, focused/W/manual |
| 45 | P:141; O | Fresh independent final full-range review; missing reviewer blocks; fixes verified/committed separately | C:81–97,270–289 | **PASS** carrier; required omission test missing |
| 46 | REQUIREMENTS; AGENTS; T008 | Applicable memory/docs owners constrain work; adoption does not invent facts | E:15–18; RM:14–18,29–33,67–80; C:16–19; install-memory:30–78 | **PASS** static connected-skill inspection |
| 47 | Original F8; REQUIREMENTS:13 | Mandatory stage stops coexist with permitted prose-and-end-turn fallback; never infer answers | B:13–20,56–58; E:35–37,162–165; C:74–84 | **PASS**, focused/W/manual |
| 48 | P:181,219; T008 | Dynamic installation/discovery, distributed reference and reload guidance | installer:85–153; probe:10–12; README:14–26,124 | **PASS** static; live discovery **NOT_RUN** |
| 49 | P:162–183; T009–T010 | Ordinary checks enforce actual operational obligations and real named mutations | W:37–78; M:25–70; lint:53–63 | **PARTIAL**, A1 |
| 50 | Original F9; O | Custom candidate lint does not claim checkout workflow results | lint:55–63; M:60–65 | **PASS**, explicit SKIP; no candidate workflow assurance |
| 51 | T001/T011/T012; O | Coverage separates static/semantic/live evidence; current state truthful | coverage:3–18,91–111; execution:5,72–95 | **PARTIAL**, A1/A5 qualifications |
| 52 | P exclusions; AGENTS | No duplicate graph/brainstorm prompt, obsolete platform state or fixed skill model bindings | Full patch/current skills | **PASS**, sizing duplication separately identified |
| 53 | O walkthroughs | Live dialogue, SpecKit, obedience, scheduling, context and installed discovery demonstrated | No live workflow evidence supplied | **NOT_RUN** |

## 4. End-to-end static walkthroughs

These trace instructions; they are **not live workflow executions**.

| Scenario | Inspected outcome | Result |
|---|---|---|
| Fresh small EPIC entered directly | Shared reference prefers direct tasks; explicit E→RM recommendation/handoff absent | **PARTIAL — A3** |
| Small documentation-init EPIC | Explicit exception passed by initialization, recorded by CE, preserved downstream | **PASS** |
| Admitted/resumed EPIC with newly settled design | Required reference preserves admission; resolution alone does not trigger conversion | **PASS**; A3 fix must preserve this |
| Large requirement | Shared admission guidance, evidence explanation and owner route choice | **PASS** |
| Well-specified direct requirement | Durable capture→shared NO gate→direct tasks→review→approval→coordinator | **PASS** carrier; removal under-tested |
| Materially ambiguous requirement | Bounded agenda→one owner answer at a time→exact bounded application→deferrals | **PASS** |
| Interrupted pending question | Re-present saved item; apply answer in originating context or durable correction handoff | **PASS** |
| Direct task production | Preparation authorization sufficient; final approval follows review | **PASS** |
| SpecKit task production | Current spec approval/preparation authorization; no premature final plan/task approval | **PASS** |
| One suitable bounded task | Provenance/review/approval/reviewer preflight retained; local permitted; integration and commit required | **PASS** |
| Three mixed-class tasks | Suitable local segments permitted; mismatched segments delegated in approved order | **PASS** |
| Three context-heavy tasks | Insufficient observed context defeats local eligibility; delegate or stop if unavailable | **PASS** |
| Four coherent shared-file cross-heading tasks | Full count mandates delegation; may stay one homogeneous sequential batch; producer checks/task commits retained | **PASS** |
| Genuine class/gate/context/scope/external boundary | Evidence-backed split; no dependency reorder/distant padding | **PASS** |
| Delegated list resumes with three remaining | Complete approved count retains delegation | **PASS** |
| Resume after artifact/model/workspace drift | Current approvals, capabilities and workspace revalidated; affected gate renewed | **PASS** |
| Failure or unsupported resumption | Inspect failure before retry; unknown cause stops; bounded durable handoff when appropriate | **PASS** |
| No SpecKit | Direct path remains viable; EPIC stops on required missing capabilities | **PASS** |
| Installed SpecKit with direct input | Installation does not introduce plan prerequisites | **PASS** |
| Missing mandatory reference | Missing-install stop; installer distributes reference | **PASS** static |
| Invalid constitution, principles supplied | Principles may be recorded without repairing actual required constitution | **PARTIAL — A2** |
| Missing questions/delegation/model/reviewer | Required-stage stop; permitted prose fallback ends turn; no inferred answer/self-certification | **PASS** |
| Forward dependency/resumed story | Validator rejects explicit defects; manual implicit check remains; producer review corrects ordering | **PASS** inspection |
| Opus share >30% | Recorded owner exception required | **PASS** |
| Conflicting commit policy | Owner decides explicit exception; no silent omitted commit | **PASS** |
| Custom candidate lint | Explicit workflow SKIP, not checkout result attributed to candidate | **PASS with limitation** |

## 5. Cross-skill composition

### Working connections

- E and RM converge through B/TG into **one coordinator**.
- FR1 removes the premature-approval cycle: preparation precedes final implementation approval.
- Shared validation “before approval” composes with E’s create-only tasking because correction belongs to overall review.
- RM explicitly forbids substituting generic brainstorming for the shared EPIC mechanism.
- Generic review’s self-review fallback does not waive C’s explicit independent-review acceptance gate.
- Generic handoff supports applicable artifacts; C independently preserves producer-specific gates.
- Documentation initialization’s approved plan/EPIC exception does not become a general RM plan requirement.

### Remaining gaps

- Named E→RM recommendation: A3.
- Conditional E→DAP integration and policy precedence: A4.
- Constitution repair completion: A2.
- Copied sizing rule: A6.
- Routine validation across all contract carriers: A1.

No execution-time circular dependency was found. Returns to producer review are intentional defect-routing edges, not approval cycles.

No copied brainstorming implementation or second batching algorithm was found.

## 6. Source/history inventory

| Historical/current protection | Corrected disposition |
|---|---|
| Gate, bounded agenda, owner dialogue, exact application | **Preserved/extracted** into one shared skill |
| Optional gate/session/fix transitions | **Preserved operationally**, incompletely regression-protected |
| Fixed stage classes | **Preserved with portable names**; gate deliberately sonnet-class |
| Per-stage settled constraints/authorities/prior handoff | **Restored** through reusable stage brief |
| Pending flags, answers, deferrals, interruption recovery | **Restored**, durable fallback when resumption unavailable |
| SpecKit as EPIC provider | **Preserved**, no Markdown substitute |
| Required SDD reference | **Restored**, missing-install stop present |
| Constitution validity | **Partially restored**, A2 |
| Specification and overall approval briefings | **Restored** |
| Current-content approvals/stale stops | **Preserved/restored** |
| Same-pass spec review/plan production/produced-plan correction | **Restored** |
| Create-only tasks; overall-review corrections | **Preserved** |
| Conditional delegated architectural planning | **Removed without explicit replacement accounting**, A4 |
| Historical speculative material defaults | **Deliberately removed**, correctly replaced by owner decisions |
| Task complexity standards | **Centralized** in TG; concrete bindings remain runtime selections |
| Historical plan-level model-assignment detail | **Not restored separately**; final task complexity belongs to TG, planning prepares coherent work |
| Universal implementation delegation | **Deliberately changed** to bounded ≤3 local eligibility |
| Isolation-first file/heading/dependency splits | **Deliberately changed** to context-coherent sequential batching |
| Per-batch commits | **Deliberately changed** to per-task commits |
| Forced one-session-per-class reuse | **Explicitly rejected** |
| Task-only coordinator rejection | **Deliberately removed**, replaced by origin-specific authorization |
| Resolver/rigid state/platform paths/historical bindings | **Deliberately removed**, not resurrected |
| Documentation-init EPIC exception | **Preserved** |
| New small-EPIC→RM recommendation | **Authorized now; not explicit yet**, A3 |

Coverage should qualify B06/B29 for A2/A1 and account explicitly for A4. Blanket “no unaccounted removal” language is too strong until those dispositions are recorded.

## 7. Additional Sol evidence

The scoped recheck independently reports:

- Operational/mutation gaps, including label-only brainstorm-fix, missing approval/final-review assertions and contradictions outside RM.
- Incomplete detected-constitution repair.
- FR3 pending/completed metadata drift.

These corroborate A1, A2 and A5. This broader review additionally evaluates the owner’s new routing addition, architectural-planning integration, sizing duplication, and the complete property/scenario inventory.

Both reviews distinguish source inspection and reported static results from live execution.

## 8. Verification follow-up and verdict

After corrections, the supervisor should run:

- `bash scripts/check-skills-lint.sh`
- `python3 scripts/check-requirements-manager-workflow.py`
- `python3 scripts/test-requirements-manager-workflow-mutations.py`
- All seven focused workflow/validator test files.
- `python3 skills/task-generation/scripts/check-task-order.py docs/plans/requirements-manager-tasks.md`
- `git diff --check`

Retain command-labelled output. Add A1’s counterexamples and A3’s routing cases as named tests before claiming complete static coverage. No paid probe or live SpecKit trial is necessary to correct these findings.

**Final verdict: NOT_READY.** Resolve A1–A3 and disposition A4–A6. The execution architecture is sound in the inspected contracts, but whole-suite acceptance is premature.

After skill changes, remind the owner to run **`/reload` inside pi**.