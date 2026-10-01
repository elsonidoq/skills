# Second final independent recheck

## Review

**NOT_READY — Merge verdict: BLOCK.** Review-only; no commands, edits, commits, or delegation performed.

Reviewed the complete 2,953-line exported implementation diff for `e21a6b27aed02192aecac739e5ef033e6ce61dcf..8b14df9bdecc81c69635ff64058f3ab72182e977`, supplied commit evidence, approved plan/tasks, tracker/coverage, historical and relevant pre-change sources, original/Astra/Sol reports, correction handoff, actual predicates/mutations, and verification logs. Exported history was not independently queried.

### Findings

**P1 — A1/R1 remains PARTIAL: two previously identified false negatives survive.**

Locations: `scripts/check-requirements-manager-workflow.py:49–65`; `skills/requirements-manager/scripts/test_contract.py:18–22`; `scripts/test-requirements-manager-workflow-mutations.py:36–61`.

Source-proven counterexamples:

- Delete Requirements Manager’s entire operational brainstorming section, `skills/requirements-manager/SKILL.md:47–54`. The checker requires no operational invocation there. Its focused test still finds `epic-brainstorming` in prerequisites; all other assertions and lint predicates remain satisfied.
- Change the brainstorm output destination at `skills/epics-manager/SKILL.md:86` from `epic_brainstorm_fix` to `spec_create`, leaving headings, diagram, and bodies otherwise intact. Neither the checker nor focused tests require this transition. The fix-to-spec destination at line 94 is likewise unprotected.

The mutation suite adds substantive safeguards but still omits these shared-invocation/conditional-transition mutations. Its eligibility mutation removes only “scope is clear”; separate class/context/full-count omission mutations requested by the recheck are absent.

**Impact:** ordinary validation can still pass after removing shared brainstorming execution or bypassing decision application. This contradicts T009–T010 acceptance, not merely arbitrary natural-language completeness.

**Smallest correction:** require the invocation within RM’s operational section and both conditional output destinations within their EPIC sections; add named mutations. Add explicit class/context/full-count omission cases. Qualify A1/F4/B29 completion claims until these pass.

**Evidence limit:** counterexamples derived from the complete predicate inventory, not executed by this reviewer.

---

**P2 — A4 adapter restoration introduces duplicate planning.**

Location: `skills/epics-manager/SKILL.md:112–119`.

The manager invokes the architectural helper, then explicitly says “Otherwise, or after that adapter returns” to create the plan again. The helper already runs the planning capability and returns generated outputs (`skills/delegating-architectural-planning/SKILL.md:40–49,92–94`).

**Impact:** the delegated path prescribes a second planning execution rather than one combined review/create/fix pass.

**Smallest correction:** require the adapter to perform the complete manager-governed pass; use the direct pass only when no adapter is invoked. After return, inspect its evidence/outputs rather than recreate them. Fixed opus binding, stops, precedence, and context-coherence instructions are otherwise restored.

---

**P2 — A5/R3 metadata reconciliation remains PARTIAL.**

Locations: `docs/plans/requirements-manager-execution.md:62,72–82`.

- Line 74 assigns **SR1** `77b501a` and **SR2** `d9e0ad5` to **FR1/FR2**, contradicting the table at lines 70–71 and supplied commit evidence (`29c64ed`, `1cbfd24`).
- Line 82 claims the T006 dispatch-era paragraph is labelled historical, but line 62 remains unlabelled.
- FR3 still says “this commit”; SR1–SR3 lack a distinct committed-task table.

**Impact:** fresh-session recovery receives inaccurate correction provenance despite the corrected current-state paragraph.

**Smallest correction:** restore FR identities, separately record SR1–SR3 and their actual SHAs, replace FR3’s relative reference, and explicitly label the T006 paragraph historical. Retain T012 as pending parent disposition.

### Dispositions

| Finding | Disposition | Inspected evidence |
|---|---|---|
| A1 / Sol R1 / F4 | **PARTIAL** | Section-local fix application, spec approval, renewal, constitution stop, intake, commits/final review, async, threshold and upstream predicates added; surviving gaps above. |
| A2 / Sol R2 / F2 | **FIXED** | `epics-manager:35–40` requires observed-capability repair, usable-constitution verification before specification, and stop on failure. |
| A3 | **FIXED** | `epics-manager:22–30` explicitly recommends RM before EPIC-only checks, preserves owner choice/source/artifacts, exception and admitted/resumed work. Focused assertions at `test_workflow_contract.py:54–64`. |
| A4 | **PARTIAL** | Conditional helper and manager precedence restored at `epics-manager:112–117`; duplicate planning above. |
| A5 / Sol R3 / F10 | **PARTIAL** | Current-state pending-FR3 contradiction removed; correction provenance remains inaccurate. |
| A6 | **FIXED** | `create-epic:66–70` references authoritative sizing instead of duplicating thresholds. |
| Other previously fixed Sol findings | **FIXED, preserved** | No new weakening found in the inspected source/authorization, briefing, recovery, task ownership, fallback, or validator contracts. |

### Correct and verification evidence

- The reorder mutation genuinely exchanges intact spec/plan blocks, preserving their bodies and the diagram: `test-requirements-manager-workflow-mutations.py:32–34`.
- Mandatory-direct-plan contradictions cover RM/shared tasks/coordinator; automatic-split insertions cover shared tasks/EPIC/coordinator: `:63–75`.
- Plan-free direct tasking, preparation versus final approval, origin-specific EPIC gates, ≤3 class/context eligibility, >3 complete-count delegation, coherent sequential batching, per-task commits, and fresh independent full-range review remain explicit in the implementation.
- Routine lint invokes the checker, mutations, and all seven focused entry points: `scripts/check-skills-lint.sh:57–68`.

The command-labelled writer log reports exit-zero lint (24 skills), checker, seven mutation methods, all seven focused entry points, task-order, diff check, and empty status. Parent validation corroborates static lint/test/order passes. These results do not refute the untested counterexamples.

**Residual risks:** static checks do not prove live model obedience, owner dialogue, SpecKit execution, async scheduling, context/resumption behavior, or actual runtime reviewer independence. Parent owns T012 acceptance. Run `/reload` inside pi after loading changed skills.