#!/usr/bin/env python3
"""Disposable Linux cgroup-v2 lifecycle probe; stdlib only, no model calls."""
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import time
import uuid

SELF = str(Path(__file__).resolve())
BASE = Path('/sys/fs/cgroup') / Path('/proc/self/cgroup').read_text().strip().split('::')[1].lstrip('/')


def emit(log, event, **facts):
    with open(log, 'a') as f:
        f.write(json.dumps(dict(time_ns=time.time_ns(), monotonic_ns=time.monotonic_ns(),
                                event=event, **facts), sort_keys=True) + '\n')
        f.flush()
        os.fsync(f.fileno())


def populated(group):
    return int(dict(line.split() for line in (group / 'cgroup.events').read_text().splitlines())['populated'])


def admit(value):
    # Unknown/unavailable is never evidence of emptiness.
    return value == 0


def validate(receipt):
    r = json.loads(Path(receipt).read_text())
    g = Path(r['group'])
    assert g.parent == BASE and g.name == 'pi-process-probe-' + r['token']
    assert len(r['token']) == 32 and all(c in '0123456789abcdef' for c in r['token'])
    s = g.lstat()
    assert stat.S_ISDIR(s.st_mode) and (s.st_dev, s.st_ino, s.st_uid) == tuple(r['identity'])
    assert s.st_uid == os.getuid()
    return g, r


def observe(receipt, log):
    try:
        g, _ = validate(receipt)
        value = populated(g)
    except (OSError, ValueError, KeyError, AssertionError) as e:
        emit(log, 'BLOCKED', replacement_allowed=False, reason=repr(e))
        raise
    emit(log, 'ORPHAN_PROCESS' if value else 'RECONCILED', group=str(g),
         populated=value, replacement_allowed=admit(value),
         members=(g / 'cgroup.procs').read_text().split())
    return value


def drain(receipt, log):
    g, _ = validate(receipt)
    emit(log, 'CGROUP_KILL', group=str(g), replacement_allowed=False)
    (g / 'cgroup.kill').write_text('1')
    deadline = time.monotonic() + 5
    while populated(g):
        assert time.monotonic() < deadline, 'group did not become empty'
        time.sleep(.02)
    assert observe(receipt, log) == 0
    _, r = validate(receipt)
    for pid in r.get('pids', []):
        try:
            state = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[0]
        except FileNotFoundError:
            state = 'absent'
        emit(log, 'POST_KILL_PID_STATE', pid=pid, state=state)
        assert state in ['absent', 'Z', 'X'], 'owned process still live'
    g.rmdir()
    emit(log, 'GROUP_REMOVED', group=str(g))


def create(scratch, log, case):
    token = uuid.uuid4().hex
    g = BASE / ('pi-process-probe-' + token)
    g.mkdir()
    s = g.stat()
    receipt = scratch / (case + '.json')
    receipt.write_text(json.dumps(dict(group=str(g), token=token,
                                     identity=[s.st_dev, s.st_ino, s.st_uid])))
    facts = {n: dict(mode=oct((g / n).stat().st_mode & 0o777),
                    uid=(g / n).stat().st_uid, writable=os.access(g / n, os.W_OK))
             for n in ['cgroup.procs', 'cgroup.kill', 'cgroup.events']}
    emit(log, 'CREATED', case=case, group=str(g), permissions=facts)
    assert os.access(g / 'cgroup.procs', os.W_OK) and os.access(g / 'cgroup.kill', os.W_OK)
    assert populated(g) == 0
    return receipt, g


def start(g, detached, log):
    p = subprocess.Popen([sys.executable, SELF, 'worker', str(g), str(int(detached))],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    # Child joins before reading release or creating any tool. This is not spawn atomicity.
    placed = json.loads(p.stdout.readline())
    assert placed['pid'] == p.pid and str(p.pid) in (g / 'cgroup.procs').read_text().split()
    emit(log, 'WORKER_PLACED', **placed, group=str(g))
    p.stdin.write('spawn\n')
    p.stdin.flush()
    tool = json.loads(p.stdout.readline())
    assert str(tool['pid']) in (g / 'cgroup.procs').read_text().split()
    emit(log, 'TOOL_READY', **tool, group=str(g), worker_pid=p.pid)
    return p, tool


def case_run(scratch, log, case, detached=False, exit_code=0, leave=False):
    receipt, g = create(scratch, log, case)
    p = None
    try:
        p, tool = start(g, detached, log)
        r = json.loads(receipt.read_text())
        r['pids'] = [p.pid, tool['pid']]
        receipt.write_text(json.dumps(r))
        if detached:
            assert tool['sid'] == tool['pid'] and tool['pgid'] != os.getpgid(p.pid)
            p.kill()
        else:
            p.stdin.write(str(exit_code) + '\n')
            p.stdin.flush()
        result = p.wait(timeout=5)
        assert result == (-signal.SIGKILL if detached else exit_code)
        emit(log, 'WORKER_EXIT', case=case, pid=p.pid, returncode=result)
        assert observe(receipt, log) == 1
        assert str(tool['pid']) in (g / 'cgroup.procs').read_text().split()
        if detached:
            os.kill(tool['pid'], signal.SIGTERM)
            time.sleep(.2)
            assert str(tool['pid']) in (g / 'cgroup.procs').read_text().split()
            assert populated(g) == 1
            emit(log, 'SIGTERM_RESISTED', pid=tool['pid'], populated=1, replacement_allowed=False)
        if leave:
            emit(log, 'HOST_EXIT_WITH_LIVE_GROUP', host_pid=os.getpid(), receipt=str(receipt))
            return
        drain(receipt, log)
    finally:
        if p is not None:
            p.stdin.close()
            p.stdout.close()
        if not leave and g.exists():
            drain(receipt, log)
            if p is not None:
                p.wait(timeout=5)


def worker(group, detached):
    signal.alarm(60)
    (Path(group) / 'cgroup.procs').write_text(str(os.getpid()))
    print(json.dumps(dict(pid=os.getpid())), flush=True)
    assert sys.stdin.readline().strip() == 'spawn'
    if detached:
        # Intermediate child exits; grandchild calls setsid and ignores TERM.
        subprocess.Popen([sys.executable, SELF, 'tool'], stdin=subprocess.DEVNULL).wait(timeout=5)
    else:
        p = subprocess.Popen(['/bin/sleep', '60'], stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL)
        print(json.dumps(dict(pid=p.pid, sid=os.getsid(p.pid), pgid=os.getpgid(p.pid),
                              command='/bin/sleep 60')), flush=True)
    sys.exit(int(sys.stdin.readline().strip()))


def run(scratch, log):
    scratch.mkdir(parents=True, exist_ok=False)
    sentinel = subprocess.Popen(['/bin/sleep', '60'])
    emit(log, 'RUN_START', command=sys.argv, controller_pid=os.getpid(), base=str(BASE),
         sentinel_pid=sentinel.pid, sentinel_cgroup=Path(f'/proc/{sentinel.pid}/cgroup').read_text().strip())
    try:
        for value in [None, 'denied', 'missing']:
            assert not admit(value)
            emit(log, 'BLOCKED', fixture='synthetic unavailable input', input=value, replacement_allowed=False)
        for name, detached, code in [('exit0', False, 0), ('exit1', False, 1), ('forced', True, 0)]:
            case_run(scratch, log, name, detached, code)
            assert sentinel.poll() is None
            emit(log, 'SENTINEL_ALIVE', case=name, pid=sentinel.pid)
        subprocess.run([sys.executable, SELF, 'host', str(scratch), str(log)], check=True, timeout=10)
        receipt = scratch / 'reentry.json'
        emit(log, 'HOST_CONFIRMED_EXITED', receipt=str(receipt))
        subprocess.run([sys.executable, SELF, 'recover', str(receipt), str(log)], check=True, timeout=10)
        assert sentinel.poll() is None
        emit(log, 'SENTINEL_ALIVE', case='reentry', pid=sentinel.pid)
    except Exception as e:
        emit(log, 'BLOCKED', reason=repr(e), replacement_allowed=False)
        raise
    finally:
        for receipt in scratch.glob('*.json'):
            if Path(json.loads(receipt.read_text())['group']).exists():
                drain(receipt, log)
        sentinel.terminate()
        sentinel.wait(timeout=5)
        emit(log, 'CLEANUP', sentinel_returncode=sentinel.returncode,
             owned_groups_remaining=[str(r) for r in scratch.glob('*.json')
                                     if Path(json.loads(r.read_text())['group']).exists()])
    emit(log, 'PASS', cases=['exit0', 'exit1', 'forced', 'reentry'])


if __name__ == '__main__':
    mode, *args = sys.argv[1:]
    if mode == 'worker':
        worker(args[0], bool(int(args[1])))
    elif mode == 'tool':
        if os.fork() == 0:
            os.setsid()
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.alarm(60)
            print(json.dumps(dict(pid=os.getpid(), sid=os.getsid(0), pgid=os.getpgrp(),
                                  command='python stdlib sleep60; setsid; SIGTERM ignored')), flush=True)
            sys.stdout.close()
            time.sleep(60)
    elif mode == 'host':
        case_run(Path(args[0]), Path(args[1]), 'reentry', leave=True)
    elif mode == 'recover':
        emit(args[1], 'RECOVERY_REOPEN', recovery_pid=os.getpid(), receipt=args[0])
        assert observe(args[0], args[1]) == 1
        drain(args[0], args[1])
    elif mode == 'run':
        run(Path(args[0]).resolve(), Path(args[1]).resolve())
    else:
        raise SystemExit('unknown mode')
