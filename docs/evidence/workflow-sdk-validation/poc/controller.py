"""Deterministic disposable controller; standard library only. Never run on existing roots."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import queue
import signal
import subprocess
import threading
import time

HERE = Path(__file__).resolve().parent

def admit(f):
    return bool(f.get('idle') and f.get('effective', {}).get('enabled') is True
                and isinstance(f.get('headroom'), (int, float)) and math.isfinite(f['headroom'])
                and f['headroom'] >= 150000)

def proc(pid):
    try:
        raw = Path(f'/proc/{pid}/stat').read_text()
        fields = raw[raw.rfind(')')+2:].split()
        return dict(pid=pid, ppid=int(fields[1]), pgid=int(fields[2]), state=fields[0], start=fields[19])
    except FileNotFoundError:
        return None

def descendants(pid):
    allp = [p for name in Path('/proc').iterdir() if name.name.isdigit() and (p := proc(int(name.name)))]
    owned = {pid}
    while True:
        newer = owned | {p['pid'] for p in allp if p['ppid'] in owned}
        if newer == owned:
            return [p for p in allp if p['pid'] in owned]
        owned = newer

def live(identity):
    p = proc(identity['pid'])
    return p is not None and p['start'] == identity['start'] and p['state'] != 'Z'

class Host:
    def __init__(self, root, log):
        root.mkdir(parents=True, exist_ok=False)
        self.root = root
        self.log = log
        self.q = queue.Queue()
        self.rows = []
        self.err = (root/'host-stderr.log').open('w')
        self.p = subprocess.Popen(['node', str(HERE/'host.mjs')], env={**os.environ, 'POC_ROOT': str(root)},
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.err, text=True, start_new_session=True)
        def reader():
            for line in self.p.stdout:
                row = json.loads(line)
                self.rows.append(row)
                with log.open('a') as out:
                    out.write(json.dumps(row).replace(str(root), '<TOY_ROOT>')+'\n')
                self.q.put(row)
            self.q.put({'type':'EOF'})
        self.reader = threading.Thread(target=reader, daemon=True)
        self.reader.start()
    def send(self, ident, op, **kwargs):
        self.p.stdin.write(json.dumps(dict(v=1, id=ident, op=op, **kwargs))+'\n')
        self.p.stdin.flush()
    def wait(self, kind, ident=None, timeout=90):
        end = time.monotonic()+timeout
        while time.monotonic() < end:
            row = self.q.get(timeout=max(.01, end-time.monotonic()))
            if row['type']=='EOF':
                raise EOFError('host exited: reconcile before replacement')
            if row['type']==kind and (ident is None or row.get('id')==ident):
                return row
        raise TimeoutError(kind)
    def request(self, ident, op, **kwargs):
        self.send(ident, op, **kwargs)
        row = self.wait('response', ident)
        assert row['ok'], row
        return row['data']
    def init(self, tools):
        return self.request('init', 'init', provider='openai-codex', model='gpt-6.1-sol', effort='medium',
                            skill=str(HERE/'toy-skill'), tools=tools)
    def close(self):
        if self.p.poll() is None:
            self.request('close', 'close')
            self.p.wait(timeout=15)
        self.reader.join(timeout=5)
        assert not self.reader.is_alive(), 'reader did not drain'
        self.p.stdout.close()
        if not self.p.stdin.closed:
            self.p.stdin.close()
        self.err.close()


def run(root, logs):
    root.mkdir(parents=True, exist_ok=False)
    logs.mkdir(parents=True, exist_ok=True)
    evidence = {'synthetic_cutoff': [], 'real': [], 'interruptions': []}
    for free in [150000,149999,None]:
        f = dict(idle=True,effective={'enabled':True},headroom=free)
        evidence['synthetic_cutoff'].append(dict(headroom=free,reuse=admit(f)))
    assert [r['reuse'] for r in evidence['synthetic_cutoff']] == [True,False,False]
    assert not admit(dict(idle=True,effective={'enabled':False},headroom=999999))
    h = Host(root/'reuse',logs/'reuse.jsonl')
    try:
        before = h.init(['write'])
        assert before['effective']['reserveTokens']==16384
        assert before['effective']['keepRecentTokens']==20000
        assert before['threshold']==before['model']['contextWindow']-16384
        for ident, text in [('t1','hello\n'),('t2','hello world\n')]:
            if ident=='t2':
                assert admit(before)
            h.send(ident,'prompt',text=f'/skill:toy-skill Use write to write toy.txt exactly {text!r}. Change nothing else.')
            accepted = h.wait('response',ident)
            assert accepted['ok'] and accepted['data']['accepted']
            after = h.wait('settled',ident)
            assert after['successful'] and after['skillMarker'] and after['idle'], after
            assert after['sessionId']==before['sessionId']
            assert (h.root/'toy.txt').read_text()==text
            delta={k:after['tokens'][k]-before['tokens'][k] for k in ['input','output','cacheRead','cacheWrite']}
            assert delta['input']>0 and all(v>=0 for v in delta.values())
            assert after['context']['tokens'] != after['tokens']['total']
            evidence['real'].append(dict(task=ident,sessionId=after['sessionId'],before=before,after=after,delta=delta,
                fileSha256=hashlib.sha256((h.root/'toy.txt').read_bytes()).hexdigest()))
            before=after
        guarded=h.request('guard','synthetic_guard')
        assert guarded['sends']==0 and guarded['guards']==2 and not guarded['forbiddenExists'], guarded
        assert guarded['normal']['errorMatched'] and guarded['summary']['errorMatched'], guarded
        evidence['synthetic_guard']=guarded
        h.send('bad-version','status'); # Valid status requires no LLM.
        status=h.wait('response','bad-version'); assert status['ok']
        h.p.stdin.write('{"v":99,"id":"wrong","op":"prompt","text":"do not run"}\n'); h.p.stdin.flush()
        invalid=h.wait('response','wrong'); assert not invalid['ok']
        evidence['protocol']={'invalid_version_rejected':True,'status_without_llm':True,'status_wire_count':status['data']['wireCount']}
    finally:
        h.close()
    for mode in ['abort','kill']:
        h=Host(root/mode,logs/f'{mode}.jsonl')
        identities=[]
        try:
            h.init(['bash'])
            # Real standard bash descendant writes for at most 12 seconds.
            (h.root/'child.sh').write_text('echo "$BASHPID" > child.pid\nfor i in $(seq 1 120); do printf x >> partial.txt; sleep 0.1; done\n')
            (h.root/'loop.sh').write_text('bash child.sh &\necho "$!" > launched.pid\nwait\n')
            h.send('active','prompt',text='/skill:toy-skill Run exactly bash loop.sh using bash with timeout 15 seconds. Do not execute anything else.')
            assert h.wait('response','active')['ok']
            end=time.monotonic()+60
            while not (h.root/'child.pid').exists() or not (h.root/'partial.txt').exists():
                if time.monotonic()>end: raise TimeoutError('real tool did not start')
                if h.p.poll() is not None: raise EOFError('host exited during tool')
                time.sleep(.02)
            child=int((h.root/'child.pid').read_text())
            identities=descendants(h.p.pid)
            assert any(p['pid']==child for p in identities), 'tool child not observed under host'
            child_identity=next(p for p in identities if p['pid']==child)
            pgid=child_identity['pgid']
            assert pgid!=os.getpgrp() and pgid!=h.p.pid
            initial=(h.root/'partial.txt').stat().st_size
            started=time.time()
            if mode=='abort':
                abort=h.request('abort','abort')
                assert abort['settled'] and abort['idle']
                response_time=time.time()
                cleanup='SDK abort + waitForIdle'
            else:
                h.p.kill(); h.p.wait(timeout=5)
                response_time=time.time()
                time.sleep(.3)
                post_kill=(h.root/'partial.txt').stat().st_size
                orphan_live=live(child_identity)
                # Reconcile exact identities recorded BEFORE host death. Never kill
                # a group solely because its old host PID no longer exists.
                current_group=[p for name in Path('/proc').iterdir() if name.name.isdigit() and (p:=proc(int(name.name))) and p['pgid']==pgid and p['state']!='Z']
                # Descendant sleep processes can have changed; require known owned
                # group leader or child still alive with unchanged start identity.
                assert any(live(p) and p['pgid']==pgid for p in identities)
                assert current_group and all(p['pgid']==pgid for p in current_group)
                os.killpg(pgid,signal.SIGKILL)
                cleanup='supervisor killed previously observed owned tool process group'
            end=time.monotonic()+5
            while any(live(p) for p in identities if p['pid']!=h.p.pid) and time.monotonic()<end:
                time.sleep(.05)
            remaining=[p for p in identities if p['pid']!=h.p.pid and live(p)]
            group_live=[p for name in Path('/proc').iterdir() if name.name.isdigit() and (p:=proc(int(name.name))) and p['pgid']==pgid and p['state']!='Z']
            size1=(h.root/'partial.txt').stat().st_size
            time.sleep(.6)
            size2=(h.root/'partial.txt').stat().st_size
            admitted=not remaining and not group_live and size1==size2
            record=dict(mode=mode,hostPid=h.p.pid,toolChildPid=child,identities=identities,pgid=pgid,requestedAt=started,
                settlementOrHostExitAt=response_time,initialBytes=initial,partialBytes=[size1,size2],observationSeconds=.6,
                liveKnownAfter=remaining,liveGroupAfter=group_live,cleanup=cleanup,replacementAdmitted=admitted)
            if mode=='kill': record.update(orphanLiveAfterHostKill=orphan_live,postKillBytes=post_kill)
            evidence['interruptions'].append(record)
            assert admitted, 'BLOCKED: uncertain tool quiescence; no replacement admitted'
            # Deterministic replacement writer only AFTER observed drain + stable
            # partial-file reconciliation; no claim of workflow exactly-once.
            (h.root/'replacement.txt').write_text('admitted after reconciliation\n')
        finally:
            # Failure is blocking; only kill processes whose recorded identity is
            # still live, not arbitrary PIDs or guessed descendant groups.
            for p in identities:
                if p['pid']!=h.p.pid and live(p):
                    os.kill(p['pid'],signal.SIGKILL)
            h.close()
    (logs/'results.json').write_text(json.dumps(evidence,indent=2).replace(str(root),'<RUN_ROOT>')+'\n')
    print(json.dumps({'result':'PASS executed assertions','real_tasks':2,'interruptions':2,
                      'real_transport_calls':evidence['real'][-1]['after']['wireCount'],'logs':str(logs)}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['run','status']);p.add_argument('--root',type=Path);p.add_argument('--logs',type=Path,required=True)
    a=p.parse_args()
    if a.command=='status': print((a.logs/'results.json').read_text())
    else: run(a.root.resolve(),a.logs.resolve())
