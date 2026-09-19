# Global Agent Instructions

## Expensive Subagent Failures

Never relaunch an expensive subagent, including `opus`, after a failure unless the failure cause
has been inspected and a retry directly addresses that cause. A generic tool abort, cancellation,
timeout, or missing error detail is not evidence that retrying will work.

Before any relaunch:

1. Inspect the existing task session and the failed tool invocation.
2. Determine whether the subagent can be resumed with a targeted correction.
3. Resume the existing session when it retains relevant analysis or work.
4. If the cause is unavailable or uncertain, stop and report the blocker to the owner.

Only launch a new expensive subagent after the owner explicitly requests it or the inspected
failure proves that a fresh session is necessary.
