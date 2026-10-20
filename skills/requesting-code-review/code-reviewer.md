# Code Review Contract

Provide this contract to the available reviewer. Replace each bracketed field with accessible context rather than assuming a particular repository host, agent, branch, or revision scheme.

## Inputs

- **Change:** [summary and exact code or diff scope]
- **Requirements:** [acceptance criteria, issue, plan, or specification]
- **Verification:** [checks run and results]
- **Constraints:** [compatibility, migration, policy, or environment limits]

If an input is unavailable, identify the gap and limit the verdict accordingly. Review read-only unless explicitly authorized to make changes.

## Review Focus

Apply [Parsimony and Actionable Checks](../planner/references/parsimony.md). Review
additions as well as omissions: identify absent source basis for invented safeguards,
false blocking and legitimate behavior prevented. Distinguish original requirements,
necessary choices and optional hardening; concrete serious security/data-loss risks and
actual platform limits retain protection. Changing approved REQUIRED acceptance returns
through existing producing review/approval, never a reviewer waiver.

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

Review the actual full committed base/head range against the requested tasks and relevant
project checks. Start final review in a fresh independent context; the same reviewer may
recheck corrections. Remain read-only: report concrete findings, do not implement them or
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

- **Open questions:** ambiguities or inaccessible evidence that affect the verdict
- **Verdict:** ready, ready with stated follow-up, or not ready
- **Verification gaps:** checks still needed

Do not add praise, style preferences, or hypothetical scope unrelated to the change. If there are no findings, say so explicitly and still state residual risks or verification gaps.
