# Code Review Contract

Provide this contract to the available reviewer. Replace each bracketed field with accessible context rather than assuming a particular repository host, agent, branch, or revision scheme.

## Inputs

- **Change:** [summary and exact code or diff scope]
- **Requirements:** [acceptance criteria, issue, plan, or specification]
- **Verification:** [checks run and results]
- **Constraints:** [compatibility, migration, policy, or environment limits]

If an input is unavailable, identify the gap and limit the verdict accordingly. Review read-only unless explicitly authorized to make changes.

## Review Focus

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

## Executable review binding

For runner review use the supplied packaged agent-result.schema.json, exact task/attempt/
contract identity and range_base/range_head. Return kind review and pass/correction/blocked
with stable finding IDs, severity, criterion_ref, location, evidence, proposed_action and scope.
Narrative cannot select graph outcomes. Remain read-only; never become the repair producer,
commit or weaken REQUIRED/manual/permission gates. Review the entire committed range with
source/tasks/approval and current item proof. First final review is fresh independent context;
later rounds may reuse only eligible own-review lineage. Questions use request_owner_input,
not direct ask_user; original-only answer continuity and owner scope gates still apply.

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
