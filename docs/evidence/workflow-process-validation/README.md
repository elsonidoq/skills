# Disposable local process-containment proof

**Result: PASS**, four real Linux cases in `run.jsonl`. This clears the critical
local lifecycle feasibility question under the currently available delegation;
it does not approve a production design or resume planning. No Pi, model,
provider, SDK, package, service configuration, or remote calls were made by the test.

## Reproduce

From the repository root, with a fresh scratch directory (the script refuses an
existing one):

```sh
mkdir -p .pi/workflow-validation/process-probe/tmp
TMPDIR="$PWD/.pi/workflow-validation/process-probe/tmp" \
  python3 docs/evidence/workflow-process-validation/script.py run \
  .pi/workflow-validation/process-probe/run-1 \
  docs/evidence/workflow-process-validation/run.jsonl
```

The log appends; use a fresh log filename for an independent run. Python stdlib,
Linux cgroup v2, and `/bin/sleep` are the only requirements. This is a throwaway
probe, not a reusable production supervisor or test framework. Tool fixtures
sleep for at most 60 seconds; workers also have a 60-second alarm. The controller
uses five-second exit/empty waits and ten-second host/recovery subprocess limits.

## Observed capability and safety boundary

The current process was in `0::/system.slice/paseo.service`. `findmnt -no
FSTYPE,OPTIONS /sys/fs/cgroup` returned `cgroup2
rw,nosuid,nodev,noexec,relatime,nsdelegate,memory_recursiveprot`.
Actual `stat`/`os.access` inspection, UID 1002:

| Object under `/sys/fs/cgroup/system.slice/paseo.service` | Mode | UID | Writable |
| --- | --- | --- | --- |
| service directory | 0755 | 1002 | yes |
| service `cgroup.procs` | 0644 | 1002 | yes (never written) |
| service `cgroup.kill` | 0200 | 0 | **no; never targeted** |
| service `cgroup.events` | 0444 | 0 | no (readable) |
| each newly owned child `cgroup.procs` | 0644 | 1002 | yes |
| each newly owned child `cgroup.kill` | 0200 | 1002 | yes |
| each newly owned child `cgroup.events` | 0444 | 1002 | no (readable) |

Only four fresh UUID-named immediate child groups were created, populated,
killed, and removed. No ancestor, unknown group, mount, ownership, or service
setting was modified. Before every kill/removal, the receipt must match the
current delegated parent, exact generated name, UID, device and inode. Receipts
are scratch-local ownership evidence for this cooperating experiment, **not an
authenticated production registry**. Invalid/unreadable observations block;
there is no PID-only containment fallback.

The worker writes its own PID to the child group **before spawning tools**,
announces placement, and waits for controller release. The controller verifies
actual membership before release. This is a tested placement handshake, not
proof of atomic OS spawn-and-assign. Kernel inherited cgroup membership and
`cgroup.events populated` are the containment/empty oracle; PID/PGID observations
only demonstrate the scenario. The PID-state check after empty is supplemental,
not the cleanup authority.

## Actual cases and alarm ordering

All event times are retained as wall-clock and monotonic nanoseconds. The table
uses monotonic seconds relative to `RUN_START` (rounded):

| Case | Worker outcome / live tool PID | ORPHAN_PROCESS, admission false | cgroup.kill | populated 0, RECONCILED, admission true |
| --- | --- | --- | --- | --- |
| normal exit 0 | 3049960 exited 0 / 3049961 | +0.051 s | +0.052 s | +0.073 s |
| normal exit 1 | 3049962 exited 1 / 3049963 | +0.131 s | +0.132 s | +0.153 s |
| forced exit | 3049964 killed (-9) / 3049966 | +0.235 s | +0.437 s | +0.458 s |
| host reentry | 3049968 exited 0 / 3049969 | +0.540 s, again +0.605 s on recovery | +0.606 s | +0.627 s |

- Logical success and failure both left the real `/bin/sleep 60` child alive in
  the same group. Both emitted a flushed, fsynced `ORPHAN_PROCESS` history record
  with `replacement_allowed=false`, independent of worker result status.
- The forced case used a child that forked a grandchild. Grandchild 3049966 had
  SID=PGID=3049966, outside the worker's original process group, and installed
  SIGTERM ignore before announcing readiness. After worker SIGKILL, direct
  SIGTERM to the grandchild was insufficient: membership and `populated=1`
  persisted after 200 ms. The group kill reached the surviving descendants
  (including an intermediate child observed during its exit).
- Host/controller process 3049967 exited while the contained sleep remained.
  The outer driver waited for that host's actual exit, then launched independent
  recovery process 3049970. Recovery reopened the persisted receipt, validated
  group identity, independently observed the orphan, and killed/waited empty.
  It did not depend on a surviving host object or its PID for control.
- No true admission was emitted until the actual kernel `populated=0` read.
  `RECONCILED` clears the alarm by disposition without deleting its history.
  Missing/denied/unavailable inputs were **explicitly synthetic** admission-only
  controls, each producing `BLOCKED`/false; no real delegation was sabotaged.
- Independent owned sentinel 3049959 stayed in the service parent and survived
  all four child-group kills. It was then deliberately terminated and reaped
  (-15). All four groups were empty before removal. Every recorded worker/tool
  PID was absent after killing; the code permits a truthful zombie/dead state
  because `populated=0` proves no live tasks, not necessarily PID reaping.
  Final `CLEANUP` recorded no owned groups remaining. A separate directory
  inspection also found no `pi-process-probe-*` groups.

## Limits / remaining requirement

This demonstrates ordinary inherited **local** descendants, including setsid,
TERM resistance, worker SIGKILL, and process-reentry cleanup. It is not a security
sandbox: a malicious same-UID tool with writable ancestor cgroup controls could
migrate itself out. No such migration or ancestor membership write was attempted.
No claims cover remote jobs, containers, different-user/adversarial tools,
PID-reuse simulation, a production durable registry, host reboot/power loss,
fsync crash consistency, or production admission/notification integration.

The minimal continuing capability requirement is writable delegated cgroup-v2
child creation/placement/kill plus readable events, retained trusted ownership
information, and placement before local tool spawn. If unavailable or identity
cannot be validated, the safe outcome remains BLOCKED, not replacement. This
probe supplies lifecycle evidence only; the parent must independently review it
before any planner continuation.
