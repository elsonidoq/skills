# Planner Approval UX Follow-up

## Owner-observed behavior and approved correction

The owner tested the installed planner on a contained requirement and reported:
1. No brief bulleted executive summary before the artifact approval question.
2. Approval did not automatically start the next phase.

No test-project transcript was supplied; these are owner-observed runtime failures, not
locally reproduced model traces. Inspection found an unspecified brief format and the
planner's conditional “If execution was requested” handoff. The owner explicitly chose:
final approval starts implementation unless planning-only was requested.

## Changes and boundaries

- All artifact approvals/renewals require 4–6 short owner-visible bullets BEFORE `ask_user`:
  outcome, scope/exclusions, decisions, risks/deferrals, real review results and exact
  authority/next phase. Context inside the question is not a substitute.
- Affirmative depth choice/approval immediately starts the next authorized phase in the
  same session. Dispatch async work before returning; routine continuation needs no new
  question. Standard specification approval starts planning. Final TinySpec/Standard
  approval supplies the complete handoff and invokes coordinator preflight.
- Explicit planning-only/separate-session boundaries remain respected and must be stated
  before consent. Older preparation-only approvals are not execution authority.
- Denied/cancelled/ambiguous answers, missing capabilities and material owner gates still
  stop. Coordinator execution/model/delegation/commit/review policy remains unchanged.

## Regression evidence

- New instruction/trace tests failed before correction: three failures recorded at
  `/tmp/planner-approval-ux-before.log`.
- Named mutations now cover bullet-format omission, lost automatic continuation,
  continued separate-execution-request policy and Standard approval-to-plan transition.
- A mutation exposed TinySpec checks leaking into the Standard subsection. Heading-level
  section extraction now isolates both routes, with a regression test for that boundary.
- Trace fixtures reject prose-only/empty briefs and approved-but-idle transitions, require
  next-phase dispatch before returning control, and preserve denial/planning-only boundaries.
  Supervisor maps exact approval responses to actual next-tool predicates; no invented phase API.
- `bash scripts/check-skills-lint.sh`: PASS (23 skills; 66 offline tests across six suites).
  `git diff --check`: PASS. Output: `/tmp/planner-approval-ux-after.log`.
- Static/synthetic checks are not a retest of live model obedience. The owner must reload and
  repeat the actual workflow. Installed links point directly to this feature worktree.
- Initial independent Astra UX review accepted the skill behavior but found two oracle
  defects: denied/pending continuation escaped checks, and an empty final bullet block
  inherited an earlier count. See [initial review](reviews/planner-approval-ux-initial-review.md).
- New fixtures reproduced three failures (`/tmp/planner-ux-oracle-before.log`). Corrections
  separate the affirmative dispatch deadline from unauthorized-action scanning across
  settled events; a real mapped renewed approval is needed to supersede denial. Empty
  blocks now replace prior counts. Pending/denied/renewed-consent fixtures cover this.
- Post-correction suite: PASS, 70 offline tests across six suites, with Python compilation
  and diff whitespace checks. Output: `/tmp/planner-ux-oracle-verification.log`.
- Independent targeted Astra corrective review: READY with owner live-retest follow-up;
  UX1/UX2 fixed, no remaining issues found in the corrective scope. See
  [final recheck](reviews/planner-approval-ux-final-recheck.md). Live model UX remains
  unverified locally; run `/reload` and repeat the owner workflow.
