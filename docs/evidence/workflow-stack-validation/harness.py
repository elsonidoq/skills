"""Disposable empirical adapter, not a production runner. All runtime paths supplied explicitly."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import queue
import signal
import sqlite3
import subprocess
import threading
import time
from typing import TypedDict
import uuid

import jsonschema
import yaml
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

HERE = Path(__file__).resolve().parent

def run(*args, cwd):
    return subprocess.check_output(args, cwd=cwd, text=True, stderr=subprocess.STDOUT).strip()

def dump(path, obj):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(obj, indent=2) + '\n')
    tmp.replace(path)

def load_config(path):
    c = yaml.safe_load(Path(path).read_text())
    jsonschema.validate(c, json.loads((HERE / 'schema.json').read_text()))
    assert c['start'] in c['nodes']
    for n in c['nodes'].values():
        assert (n['type'], n['handler']) in [('agent','worker'),('code','check'),('code','commit')]
        assert set(n['transitions']) == ({'success','failure','blocked'} if n['handler']=='check' else {'success'})
        assert all(v == 'END' or v in c['nodes'] for v in n['transitions'].values())
        if n['type'] == 'agent':
            assert n['profile'] in c['profiles'] and n['skill'] in c['skills']
    return c

def admit(context, threshold, same_group=True, compatible=True, ready=True, cutoff=150000):
    return bool(ready and same_group and compatible and context is not None and threshold is not None and threshold-context >= cutoff)

class RPC:
    def __init__(self, root, profile, skill):
        self.q = queue.Queue()
        self.err = (root / 'pi-stderr.log').open('a')
        self.p = subprocess.Popen(['pi','--approve','--mode','rpc','--provider',profile['provider'],'--model',profile['model'],
            '--thinking',profile['effort'],'--no-extensions','--no-skills','--no-prompt-templates','--no-context-files',
            '--tools','read,write','--session-dir',str(root/'sessions'),'--append-system-prompt',
            f'All writes MUST be within {root / "toy"}. Never commit. {skill}'],cwd=root/'toy',
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.err,text=True, start_new_session=True)
        def reader():
            for line in self.p.stdout:
                try: self.q.put(json.loads(line))
                except json.JSONDecodeError: pass
        threading.Thread(target=reader,daemon=True).start()
    def request(self, typ, **kw):
        ident = str(uuid.uuid4())
        self.p.stdin.write(json.dumps(dict(id=ident,type=typ,**kw))+'\n'); self.p.stdin.flush()
        end = time.monotonic()+180
        while time.monotonic()<end:
            msg = self.q.get(timeout=max(.1,end-time.monotonic()))
            if msg.get('id') == ident and msg.get('type')=='response':
                assert msg['success'], msg
                return msg.get('data')
        raise TimeoutError(typ)
    def prompt(self, text):
        self.request('prompt',message=text)
        end = time.monotonic()+240
        while time.monotonic()<end:
            msg=self.q.get(timeout=max(.1,end-time.monotonic()))
            if msg.get('type')=='agent_end': return
        raise TimeoutError('agent_end')
    def close(self):
        os.killpg(self.p.pid,signal.SIGTERM); self.p.wait(timeout=15)
        self.p.stdin.close(); self.p.stdout.close(); self.err.close()

class State(TypedDict, total=False):
    task: str
    text: str
    outcome: str
    repairs: int
    sha: str
    events: list
    metrics: list

class Engine:
    def __init__(self, root, config, synthetic=False, crash=None, bad=False):
        self.root=root; self.toy=root/'toy'; self.c=config; self.synthetic=synthetic
        self.crash=crash; self.bad=bad; self.rpc=None; self.previous=None
        self.db=sqlite3.connect(root/'checkpoints.sqlite',check_same_thread=False)
        self.saver=SqliteSaver(self.db)
        g=StateGraph(State)
        for name in config['nodes']:
            g.add_node(name,lambda s,name=name:self.node(name,s))
        g.set_entry_point(config['start'])
        for name,n in config['nodes'].items():
            g.add_conditional_edges(name,lambda s:s['outcome'],{k:END if v=='END' else v for k,v in n['transitions'].items()})
        self.graph=g.compile(checkpointer=self.saver)
    def node(self,name,s):
        n=self.c['nodes'][name]; task=s['task']; op=self.root/f'{task}.operation.json'
        events=list(s.get('events',[])); metrics=list(s.get('metrics',[]))
        baseline=run('git','rev-parse','HEAD',cwd=self.toy)
        outcome='success'; repairs=s.get('repairs',0); sha=s.get('sha','')
        started=time.time()
        if n['handler']=='worker':
            if op.exists():
                receipt=json.loads(op.read_text())
                assert receipt['text']==s['text']
                assert (self.toy/'toy.txt').read_text()==s['text'], 'uncertain partial write: block; never redispatch'
                events.append({'kind':'reconciled-file','task':task,'agent_redispatched':False})
            else:
                if name=='repair': repairs+=1
                profile=self.c['profiles'][n['profile']]; skill=self.c['skills'][n['skill']]
                before=after=observed=None
                reused=False
                dump(op,{'task':task,'text':s['text'],'baseline':baseline,'phase':'intent','synthetic':self.synthetic})
                if self.synthetic:
                    with (self.root/'synthetic-dispatches.jsonl').open('a') as f:f.write(json.dumps({'task':task,'node':name})+'\n')
                    (self.toy/'toy.txt').write_text('bad\n' if self.bad and name!='repair' else s['text'])
                else:
                    if self.rpc:
                        stats=self.rpc.request('get_session_stats')
                        context=stats.get('contextUsage',{}).get('tokens')
                        signature=(profile,skill,'story-1')
                        reused=admit(context,500000-16384,compatible=self.previous==signature,cutoff=self.c['min_free_tokens_before_compaction'])
                        if not reused:self.rpc.close();self.rpc=None
                    if not self.rpc:self.rpc=RPC(self.root,profile,skill)
                    observed=self.rpc.request('get_state')
                    assert observed['model']['id']==profile['model'] and observed['model']['provider']==profile['provider']
                    assert observed['thinkingLevel']==profile['effort']
                    assert observed['autoCompactionEnabled'] is True
                    assert observed['model']['contextWindow']==500000
                    before=self.rpc.request('get_session_stats')
                    self.rpc.prompt(f'{skill}\nTask {task}, context_group story-1. Use write tool to write toy.txt exactly {s["text"]!r}. Do not change any other file. Reply with skill marker only.')
                    after=self.rpc.request('get_session_stats')
                    self.previous=(profile,skill,'story-1')
                dump(op,{'task':task,'text':s['text'],'baseline':baseline,'phase':'file-written','synthetic':self.synthetic})
                metrics.append({'task':task,'attempt':repairs,'node':name,'profile':n['profile'],'requested':profile,'skill':skill,
                    'observed':None if observed is None else {'provider':observed['model']['provider'],'model':observed['model']['id'],'effort':observed['thinkingLevel'],'sessionId':observed.get('sessionId')},
                    'context_group':'story-1','reused':reused,'start':started,'end':time.time(),'elapsed':time.time()-started,
                    'before':before,'after':after,'provenance':'synthetic-no-token-data' if self.synthetic else 'Pi RPC get_session_stats before/after; cumulative tokens; contextUsage current occupancy',
                    'effective_threshold':483616,'threshold_provenance':'Pi 0.87.1 shouldCompact: contextWindow minus project modelOverrides.reserveTokens=16384',
                    'context_start':None if before is None else before['contextUsage']['tokens'],
                    'context_end':None if after is None else after['contextUsage']['tokens'],
                    'headroom_start':None if before is None else 483616-before['contextUsage']['tokens'],
                    'headroom_end':None if after is None else 483616-after['contextUsage']['tokens'],
                    'token_deltas':None if before is None else {k:after['tokens'][k]-before['tokens'][k] for k in ['input','output','cacheRead','cacheWrite']},
                    'baseline':baseline,'synthetic':self.synthetic})
                if self.crash=='file':os.kill(os.getpid(),signal.SIGKILL)
        elif n['handler']=='check':
            ok=(self.toy/'toy.txt').read_text()==s['text']
            if metrics:metrics[-1]['verification']='passed' if ok else 'failed'
            events.append({'kind':'required-check','task':task,'command':'assert toy.txt == task.text','passed':ok})
            if not ok:
                outcome='failure' if repairs < self.c['max_repair_attempts'] else 'blocked'
                # A known failed check permits exactly the configured repair, not uncertain replay.
                if outcome=='failure':op.unlink()
        elif n['handler']=='commit':
            subject=f'toy task {task}'
            matches=run('git','log','--format=%H:%s',cwd=self.toy).splitlines()
            found=[x.split(':',1)[0] for x in matches if x.split(':',1)[1]==subject]
            assert len(found)<=1
            if found:
                sha=found[0]
                assert run('git','show',f'{sha}:toy.txt',cwd=self.toy)==s['text'].strip()
                assert run('git','rev-parse','HEAD',cwd=self.toy)==sha
                assert run('git','rev-parse',f'{sha}^',cwd=self.toy)==json.loads(op.read_text())['baseline']
                assert run('git','diff-tree','--no-commit-id','--name-only','-r',sha,cwd=self.toy)=='toy.txt'
                events.append({'kind':'reconciled-commit','sha':sha,'task':task})
            else:
                run('git','add','--','toy.txt',cwd=self.toy)
                run('git','commit','--only','-m',subject,'--','toy.txt',cwd=self.toy)
                sha=run('git','rev-parse','HEAD',cwd=self.toy)
                if self.crash=='commit':os.kill(os.getpid(),signal.SIGKILL)
            if metrics:metrics[-1].update(result_sha=sha,outcome='success',repair_count=repairs)
            events.append({'kind':'commit','task':task,'sha':sha,'baseline':json.loads(op.read_text())['baseline']})
        events.append({'kind':'node','node':name,'task':task,'outcome':outcome,'sequence':len(events)+1})
        return dict(outcome=outcome,repairs=repairs,sha=sha,events=events,metrics=metrics)
    def execute(self,task,text,resume=False):
        cfg={'configurable':{'thread_id':task}}
        try:
            self.graph.invoke(None if resume else dict(task=task,text=text,repairs=0,events=[],metrics=[]),cfg,durability='sync')
            return self.status(task)
        finally:
            if self.rpc:self.rpc.close();self.rpc=None
    def status(self,task):
        snap=self.graph.get_state({'configurable':{'thread_id':task}})
        value=dict(snap.values)
        dump(self.root/'state.json',{'schema':1,'task':task,'next':snap.next,'values':value})
        # Append-only projections, with stable checkpoint-derived IDs for re-entry.
        # Only SQLite determines transitions; receipts/Git reconcile external effects.
        for key in ['events','metrics']:
            path=self.root/f'{key}.jsonl'
            existing=[json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
            seen={row['projection_id'] for row in existing}
            with path.open('a') as stream:
                for i,v in enumerate(value.get(key,[])):
                    revision=hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest()[:12]
                    ident=f'{task}:{i+1}:{revision}'
                    if ident not in seen:
                        stream.write(json.dumps({**v,'schema':1,'sequence':len(existing)+1,'projection_id':ident})+'\n')
                        existing.append(v);seen.add(ident)
        return {'task':task,'next':snap.next,'outcome':value.get('outcome'),'sha':value.get('sha')}

def init(root):
    root.mkdir(parents=True,exist_ok=False); toy=root/'toy';toy.mkdir()
    run('git','init',cwd=toy)
    (toy/'.pi').mkdir();(toy/'.pi/settings.json').write_text(json.dumps({'compaction':{'enabled':True,'reserveTokens':16384,
        'modelOverrides':{'openai-codex/gpt-6.1-sol':{'reserveTokens':16384}}}}))
    (toy/'seed.txt').write_text('seed\n');run('git','add','seed.txt',cwd=toy);run('git','commit','-m','seed',cwd=toy)
    (toy/'unrelated.txt').write_text('preserve me\n')
    (toy/'seed.txt').write_text('unrelated tracked dirt\n')
    run('git','add','--','unrelated.txt',cwd=toy)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['init','run','status']);p.add_argument('--root',type=Path,required=True)
    p.add_argument('--config',type=Path,default=HERE/'workflow.yaml');p.add_argument('--task',default='t1');p.add_argument('--text',default='hello\n')
    p.add_argument('--synthetic',action='store_true');p.add_argument('--resume',action='store_true');p.add_argument('--bad',action='store_true');p.add_argument('--crash',choices=['file','commit'])
    a=p.parse_args();a.root=a.root.resolve()
    if a.command=='init':init(a.root)
    else:
        with (a.root/'writer.lock').open('w') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            e=Engine(a.root,load_config(a.config),a.synthetic,a.crash,a.bad)
            print(json.dumps(e.status(a.task) if a.command=='status' else e.execute(a.task,a.text,a.resume)))
