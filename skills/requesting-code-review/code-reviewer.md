# Code Review Contract

Provide this contract to the available reviewer. Replace each bracketed field with accessible context rather than assuming a particular repository host, agent, branch, or revision scheme.

## Inputs

- **Change:** [summary and exact code or diff scope]
- **Requirements:** [acceptance criteria, issue, plan, or specification]
- **Verification:** [checks run and results]
- **Constraints:** [compatibility, migration, policy, or environment limits]
- **For repair review:** [prior findings, examined/passing coverage, remaining gaps, prior reviewed head and actual repair changes]

If an input is unavailable, identify the gap and limit the verdict accordingly. Review read-only unless explicitly authorized to make changes.

## Review Focus

Apply [Parsimony and Actionable Checks](../planner/references/parsimony.md). Review
additions as well as omissions: identify absent source basis for invented safeguards,
false blocking and legitimate behavior prevented. Distinguish original requirements,
necessary choices and optional hardening; concrete serious security/data-loss risks and
actual platform limits retain protection. Changing approved REQUIRED acceptance returns
through existing producing review/approval, never a reviewer waiver.

For direct reviews in fresh or resumed contexts, consult [save-adr](../save-adr/SKILL.md)'s
**Consult and propagate** contract when a discovered decision owner or supplied accepted
constraints apply. Re-establish applicable authority from the supplied outcome/mechanism
constraints and source links or the whole discovered index, relevant accepted records, and
needed supersession links; do not rely on parent context or a prior-read claim. Compare the
actual diff, including deletion or simplification, against each applicable accepted outcome
and explicit mechanism constraint. A capability removal that conflicts with an accepted
outcome, or removal of an explicitly accepted mechanism, requires existing approved
supersession; compatible helper deletion that preserves the outcome needs no new gate.
Proposed and superseded records are not current policy. Contradictory accepted authority or
uncertain current supersession stops only the affected verdict pending an owner decision.

Check:

- behavior and requirement alignment
- correctness, edge cases, and failure handling
- security, privacy, and data-loss risks
- compatibility and migration impact
- maintainability without speculative abstraction
- performance or scalability risks supported by the changed path
- test quality and missing verification
- integration with surrounding code

Read the changed code and enough surrounding context to substantiate each finding. Do not infer success solely from a summary or reported test result.

## Executable review

Initially review the actual full committed base/head range against the requested tasks and
relevant project checks. Start final review in a fresh independent context. After repairs,
independently review the repair changes and affected interactions, confirm addressed findings,
and check for new defects. Carry forward previously examined, unaffected passing coverage
instead of rereviewing the original range wholesale. If repairs invalidate an earlier
conclusion, explain why and revisit that conclusion. Return updated cumulative passing
coverage, removing invalidated conclusions until re-established. Retain unresolved findings
and initial coverage gaps; fix-only review cannot certify unchecked original work. Missing
historical coverage is a gap to examine, not implicit passing coverage. Remain read-only: report concrete findings, do not implement them or
invent check results or owner answers. Include precise locations and failure scenarios.
The runner consumes its ordinary approval/findings result; no packaged evidence schema,
SQL receipt, original-session pin or graph-outcome protocol is required.

## Output

List findings first, ordered by severity. For each finding include:

- severity: blocking, important, or minor
- file and line, symbol, or other precise location
- observed problem
- impact or failure scenario
- suggested correction when it is not obvious

Then provide:

- **Examined and passing:** concrete areas examined and found working, including still-valid prior coverage on repair reviews; no claims for unchecked areas
- **Open questions:** ambiguities or inaccessible evidence that affect the verdict
- **Verdict:** ready, ready with stated follow-up, or not ready
- **Verification gaps:** checks still needed

Report passing coverage as factual review evidence, not praise. Do not add style preferences or hypothetical scope unrelated to the change. If there are no findings, say so explicitly and still state residual risks or verification gaps.
