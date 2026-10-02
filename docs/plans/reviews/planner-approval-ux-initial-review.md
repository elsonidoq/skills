## Review — findings first

### UX1 — P1: Denied continuation can pass if the next-phase action occurs after `agent_settled`

**Location:** `scripts/planner-trace.py:44–57`; regression coverage at `scripts/test-planner-workflow.py:234–242`.

The continuation checker stops collecting matching actions at the first `agent_settled` for **both** affirmative and denied responses.

**Concrete false-pass scenario:**
1. Valid approval question and brief.
2. Owner answers “Request changes.”
3. `agent_settled`.
4. The supervisor-mapped next-phase tool action occurs, with no intervening authorization.

The checker sees no matching action because it stopped at step 3. Since approval was denied, neither error branch fires. Existing tests cover an approved action occurring late and a denied action occurring immediately, but not this combination.

A related gap exists for a mapped action occurring **while approval is pending**: the scan begins only after the result. If the eventual answer is denial, that premature action is also missed.

These are within the documented scope of rejecting the mapped action without affirmative approval—not demands for a complete execution sandbox.

**Smallest correction:**
- Separate the affirmative **continuation deadline** from the unauthorized-action check.
- Require an authorized action before `agent_settled`, as today.
- Also reject mapped actions while the gate is pending or after denial/cancellation, up to a subsequent valid authorization or the scenario boundary.
- Add fixtures for pending-approval action and denial → settled → action without renewed consent.

This is a source-derived counterexample; I did not execute it.

### UX2 — P2: An empty final bullet block can inherit a previous block’s passing count

**Location:** `scripts/planner-trace.py:11–21`.

`last_bullet_count()` remembers the previous non-empty block in `last`. Empty bullet markers are not recognized as a new bullet block, so they cannot replace that remembered count.

**Concrete false-pass input:** four valid progress bullets, followed by an unindented “Approval summary:” heading and four empty `- ` lines. The helper returns **4**, although the last bullet block is empty.

The existing empty-bullet fixture contains no earlier valid block, so it does not expose this fallback.

**Smallest correction:** distinguish recognition of a bullet block from counting its non-empty items. An empty final block must produce zero rather than reuse an earlier block. Add the preceding-valid-block fixture.

Semantic completeness should remain independently reviewed; this correction only makes the stated structural check accurate.

---

## Verdict

**NOT READY for follow-up acceptance until UX1 is corrected.**  
**Merge verdict: BLOCK** on the bounded continuation-oracle defect.

The operational skill changes themselves make the requested UX clear. No architecture change or expansion into live testing is needed. UX2 is a report-only formatting-oracle correction.

## Correct behavior preserved and clarified

- **Brief format:** `skills/planner/references/approval-and-recovery.md:5–19` explicitly requires 4–6 short owner-visible bullets before `ask_user`, covering the substantive dimensions and exact next-phase authority. Tool context, paragraphs, links, or delegated reports cannot substitute.
- **Automatic continuation:** `skills/planner/SKILL.md:86–103` directs same-session continuation, dispatch before returning for asynchronous work, and no routine “shall I continue?” gate.
- **Both routes:** TinySpec’s combined approval at `:137–142`, Standard specification approval at `:159–163`, renewals, and final approval at `:192–196` carry the continuation rule locally.
- **Final handoff:** `skills/planner/SKILL.md:225–231` explicitly invokes coordinator preflight after final approval rather than stopping at readiness.
- **Consent boundaries:** the continuation section and approval reference preserve planning-only/separate-session limits, missing capabilities, material gates, denial/cancellation/ambiguity, and prohibit converting older preparation-only approvals into execution authority.
- **Ancillary approvals:** adoption/documentation approval remains limited to its stated writes; it does not inherit general implementation authority.
- **Execution policy:** the coordinator remains outside this UX change, with its baseline execution digest still checked.

The README, SDD guidance, adoption instructions, and documentation-initialization brief wording agree with those rules.

## Section isolation and mutations

The heading-level boundary in `scripts/check-planner-workflow.py:28–35` fixes the observed TinySpec-to-Standard leakage: a level-three route section stops at the next level-three or higher heading.

`test_route_sections_do_not_overlap` checks both boundaries. The TinySpec-specific mutation now cannot be satisfied by Standard’s continuation wording. Standard specification and overall-review predicates are evaluated in their respective operational stages.

No remaining route-section bleed found in the inspected current structure.

## Verification and limits

Inspected:
- The approved UX follow-up and retained prior review context.
- Targeted operational instructions, checker/oracle code, fixtures, and updated regression documentation.
- `/tmp/planner-approval-ux-before.log`: three failing pre-correction checks.
- `/tmp/planner-approval-ux-verification.log`: 23 skills, zero lint failures; **66 passing offline tests**; Python syntax and diff whitespace PASS.

These are supplied supervisor results, not reviewer-executed commands. The earlier approval was not treated as automatically approving this follow-up.

No edits, commands, agent launches, or live scenarios were performed. The owner’s reported UX failures were not independently reproduced from a supplied transcript. Passing offline checks still does not establish live brief quality or reliable phase continuation.

After the small oracle correction and offline recheck, the appropriate status is **ready with follow-up**: run `/reload` inside pi and repeat the owner’s actual workflow under their authorization. No broader live-test or sandbox work is required by this review.