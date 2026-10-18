"""Single fixture LangGraph + SQLite runner. Never import this into production."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import TypedDict
from uuid import uuid4
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.sqlite import SqliteSaver
from notify import DATA, ROOT, RUN, PARENT, HASH, atomic, notify

HERE = Path(__file__).resolve().parent
CONFIG = {'configurable': {'thread_id': RUN}}

class State(TypedDict, total=False):
    gate: dict
    answer: dict
    result: dict

def log(row):
    with (DATA/'events.jsonl').open('a') as f: f.write(json.dumps({'at':time.time(),**row})+'\n')

def relay(kind, sequence, session, nonce, source_hash):
    # Optional UI delivery cannot decide workflow state; local CLI remains usable.
    try:notify(kind,sequence,session,nonce,source_hash)
    except Exception as error:
        log(dict(type='notification_unavailable',kind=kind,sequence=sequence,errorType=type(error).__name__,durable=True))

def policy(category, explanation, options, impact):
    return category=='product' and bool(explanation) and options==['Release note','Progress note'] and bool(impact)

def preflight(permission=True, approved=True):
    if not permission or not approved: raise ValueError('BLOCKED preflight: outside declared authority; no dispatch')
    if hashlib.sha256((HERE/'approved-source.txt').read_bytes()).hexdigest()!=HASH: raise ValueError('BLOCKED source changed')
    if not (DATA/'probe-ack.json').exists(): raise ValueError('BLOCKED no actual parent transport ACK')
    return {'model':'openai-codex/gpt-6.1-sol','effort':'medium','smallTestsApproved':True,'permission':True,'maxCallsPerHost':5,'tokenCapEnforced':False,'verbosity':'low','requestTimeoutMs':30000}

def host(phase):
    config_path=DATA/'runtime-config.json'
    if not config_path.exists():
        if not os.environ.get('PI_PACKAGE_DIR'):raise RuntimeError('BLOCKED runtime path missing before host dispatch')
        atomic(config_path,dict(sdk=os.environ['PI_PACKAGE_DIR'],auth=str(Path.home()/'.pi/agent/auth.json'),models=str(Path.home()/'.pi/agent/models-store.json')))
    runtime=json.loads(config_path.read_text())
    env={**os.environ,'POC_ROOT':str(DATA),'POC_PHASE':phase,'PI_OFFLINE':'1',
         'PI_SDK_ROOT':runtime['sdk'], 'PI_AUTH_PATH':runtime['auth'],
         'PI_MODELS_STORE_PATH':runtime['models'], 'TMPDIR':str(DATA/'tmp')}
    (DATA/'tmp').mkdir(exist_ok=True)
    with (DATA/f'{phase}-stderr.log').open('w') as err:
        p=subprocess.Popen(['node',str(HERE/'host.mjs')],env=env,stdout=subprocess.PIPE,stderr=err,text=True)
        log(dict(type='host_start',phase=phase,pid=p.pid))
        settled=None
        for line in p.stdout:
            row=json.loads(line); log(row)
            if row['type']=='active_ready':
                gate=json.loads((DATA/'binding.json').read_text())
                atomic(DATA/'active.json',dict(v=1,session=row['session'],nonce=gate['nonce'],state='active',pid=p.pid))
                relay('active',3,row['session'],gate['nonce'],gate['sourceHash'])
            if row['type']=='settled': settled=row
        p.wait(timeout=10)
        if p.returncode or not settled or not settled['idle']: raise RuntimeError('BLOCKED host failed; inspect stderr/events; no retry')
        if phase=='ask' and not settled['gate']: raise RuntimeError('BLOCKED no parked gate')
        if phase=='resume' and (settled['stopReason']!='stop' or not (DATA/'toy-note.txt').exists()): raise RuntimeError('BLOCKED no completed toy output')
        return settled

def graph(saver):
    def ask(_s):
        facts=preflight();log(dict(type='preflight',facts=facts))
        if not (DATA/'binding.json').exists():
            atomic(DATA/'binding.json',dict(v=1,run=RUN,parent=PARENT,task='toy-note',gate='note-title',sourceHash=HASH,attempt=1))
        row=host('ask');gate=row['gate']
        if not policy(gate['category'],gate['explanation'],gate['options'],gate['impact']):raise RuntimeError('invalid question')
        atomic(DATA/'binding.json',gate)
        return {'gate':gate}
    def park(s):
        answer=interrupt(s['gate'])
        return {'answer':answer}
    def continue_original(s):
        gate=s['gate']
        # Pending session never substitutes a fresh session based on headroom.
        if not Path(gate['sessionFile']).is_file():raise RuntimeError('BLOCKED original session missing; owner recovery')
        if json.loads((DATA/'answer.json').read_text())!=s['answer']:raise RuntimeError('wrong answer checkpoint')
        return {'result':host('resume')}
    g=StateGraph(State);g.add_node('ask',ask);g.add_node('park',park);g.add_node('continue_original',continue_original)
    g.add_edge(START,'ask');g.add_edge('ask','park');g.add_edge('park','continue_original');g.add_edge('continue_original',END)
    return g.compile(checkpointer=saver)

def validate_binding(gate, session, nonce, source_hash):
    if gate['session']!=session or gate['nonce']!=nonce or gate['sourceHash']!=source_hash or source_hash!=HASH or hashlib.sha256((HERE/'approved-source.txt').read_bytes()).hexdigest()!=HASH:
        raise ValueError('REJECT wrong/stale gate/session/source binding')

def exclusive_json(path, value):
    with path.open('x') as f:f.write(json.dumps(value)+'\n')

def spawn_resume():
    with (DATA/'resume-runner.log').open('a') as out:
        p=subprocess.Popen([sys.executable,str(HERE/'runner.py'),'resume'],stdout=out,stderr=out,start_new_session=True,env=os.environ)
    log(dict(type='resume_queued',pid=p.pid))

def main():
    p=argparse.ArgumentParser();p.add_argument('op',choices=['launch','resume','status','answer','steer','negative-tests'])
    for name in ['session','nonce','source-hash','choice','reference','parent']:p.add_argument('--'+name)
    a=p.parse_args();DATA.mkdir(parents=True,exist_ok=True)
    if a.op=='negative-tests':
        outcomes=[]
        for perm,approved in [(False,True),(True,False)]:
            try:preflight(perm,approved)
            except ValueError:outcomes.append('preflight blocked before host')
        assert len(outcomes)==2
        assert not policy('technical','approved small test',['Release note','Progress note'],'none')
        fake=dict(session='original',nonce='right',sourceHash=HASH)
        for session,nonce,h in [('wrong','right',HASH),('original','wrong',HASH),('original','right','0'*64)]:
            try:validate_binding(fake,session,nonce,h)
            except ValueError:outcomes.append('wrong/stale binding rejected')
        assert len(outcomes)==5
        # Explicit synthetic safe resume policy, not real compaction/headroom measurement.
        original_session_usable=lambda exists,headroom:exists and headroom is not None
        assert not original_session_usable(True,None) and not original_session_usable(False,200000)
        print(json.dumps(dict(synthetic=True,passed=outcomes+['technical question rejected','unknown headroom/missing original blocks; no fresh fallback'])));return
    if a.op in ['answer','steer']:
        with (DATA/'input.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            gate=json.loads((DATA/'binding.json').read_text());validate_binding(gate,a.session,a.nonce,a.source_hash)
            if a.parent!=PARENT:raise ValueError('REJECT wrong parent')
            if a.op=='answer':
                if a.choice not in gate['options'] or not a.reference:raise ValueError('REJECT choice/reference')
                with SqliteSaver.from_conn_string(str(DATA/'checkpoint.sqlite')) as saver:
                    state=graph(saver).get_state(CONFIG)
                    if state.next!=('park',):raise ValueError('REJECT no pending question')
                answer=dict(v=1,run=RUN,task='toy-note',gate='note-title',session=gate['session'],nonce=gate['nonce'],sourceHash=HASH,
                            choice=a.choice,answerId='answer-1',parent=PARENT,reference=a.reference)
                exclusive_json(DATA/'answer.json',answer);log(dict(type='answer_accepted',answer=answer));spawn_resume()
                print('ANSWER accepted; original-session resume queued')
            else:
                if not (DATA/'active.json').exists() or (DATA/'result.json').exists():raise ValueError('REJECT no active worker')
                c=dict(session=gate['session'],nonce=gate['nonce'],sourceHash=HASH,message='Include the sentence: Steering received.',messageId='steering-1')
                exclusive_json(DATA/'steer.json',c);log(dict(type='steer_queued',**c));print('STEER queued; await SDK delivery and worker acknowledgement')
        return
    if a.op=='status':
        with SqliteSaver.from_conn_string(str(DATA/'checkpoint.sqlite')) as saver:
            state=graph(saver).get_state(CONFIG)
            print(json.dumps(dict(run=RUN,next=state.next,gate=state.values.get('gate'),pending=bool(state.interrupts),
              answerAccepted=(DATA/'answer.json').exists(),active=(DATA/'active.json').exists() and not (DATA/'result.json').exists(),done=(DATA/'result.json').exists()),indent=2))
        return
    with (DATA/'runner.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        with SqliteSaver.from_conn_string(str(DATA/'checkpoint.sqlite')) as saver:
            g=graph(saver);state=g.get_state(CONFIG)
            if a.op=='launch':
                if state.values:raise ValueError('REJECT already launched; no duplicate worker')
                g.invoke({},CONFIG);gate=g.get_state(CONFIG).values['gate']
                log(dict(type='durable_pending',session=gate['session'],checkpointNext=list(g.get_state(CONFIG).next)))
                relay('question',2,gate['session'],gate['nonce'],gate['sourceHash']);print('PENDING durable; host exited')
            else:
                if state.next not in [('park',),('continue_original',)] or (DATA/'result.json').exists():raise ValueError('REJECT no original gate to resume')
                answer=json.loads((DATA/'answer.json').read_text())
                validate_binding(state.values['gate'],answer['session'],answer['nonce'],answer['sourceHash'])
                # Explicit operator retry after inspected mechanical failure can continue the
                # already-checkpointed answer, never consume it twice or create a fresh session.
                result=g.invoke(Command(resume=answer) if state.next==('park',) else None,CONFIG)
                atomic(DATA/'result.json',result['result']);log(dict(type='workflow_done',session=result['result']['session']))
                relay('done',4,result['result']['session'],answer['nonce'],HASH)

if __name__=='__main__':main()
