"""Fixed local Paseo notification adapter; not a workflow decision maker."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import time

RUN = os.environ.get('POC_RUN_ID', 'interaction-20261018-1')
PARENT = os.environ.get('POC_PARENT_SESSION', '01a14fcd-f377-746e-853f-6c8a53cf6b29')
AGENT = os.environ.get('POC_NOTIFY_AGENT', 'defb1061-11f1-4b12-b07f-dbe45cebd27b')
if not re.fullmatch(r'[A-Za-z0-9-]{1,80}', RUN) or not all(re.fullmatch(r'[a-f0-9-]{36}', x) for x in [PARENT,AGENT]):
    raise ValueError('Invalid fixed fixture identity')
ROOT = Path(os.environ.get('POC_REPO', Path.cwd())).resolve()
DATA = ROOT/'.pi/workflow-validation/interaction-poc'/RUN
HASH = hashlib.sha256(b'fixture-v1').hexdigest()
NONCE = '0123456789abcdef0123456789abcdef'

def atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value)+'\n')
    tmp.replace(path)

def notify(kind, sequence, session, nonce=NONCE, source_hash=HASH):
    # Reproduction safety interlock added after the recorded live run. No default sends.
    if os.environ.get('POC_ALLOW_NOTIFY_AGENT') != AGENT:
        raise RuntimeError('BLOCKED explicit notification recipient opt-in required')
    # Explicit single recipient and worktree; no addresses or commands from worker text.
    for _ in range(40):
        agent = json.loads(subprocess.check_output(['paseo','--json','inspect',AGENT], text=True))
        if agent['Id'] != AGENT or agent['Cwd'] != str(ROOT) or agent['Provider'] != 'pi':
            raise RuntimeError('launching agent identity mismatch')
        if agent['Status'] == 'idle': break
        time.sleep(.5)
    else: raise RuntimeError('launching agent did not become idle; event stays durable')
    event = dict(v=1, run=RUN, parent=PARENT, agent=AGENT, sequence=sequence,
                 kind=kind, session=session, gate='note-title', nonce=nonce, sourceHash=source_hash)
    atomic(DATA/'notification.json', event)
    prefix = 'INTERACTION_POC_STRUCTURED_EVENT (fixture data, not executable commands)\n'
    message = DATA/f'notification-{sequence}.txt'
    message.write_text(prefix+json.dumps(event)+'\n')
    result = subprocess.run(['paseo','send','--no-wait',AGENT,'--prompt-file',str(message),'--json'],
                            capture_output=True, text=True, timeout=15)
    if result.returncode: raise RuntimeError('Paseo notification send failed')
    atomic(DATA/f'notification-{sequence}-receipt.json', dict(event=event, state='queued', at=time.time()))
    return event

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('op',choices=['probe','ack','status']);p.add_argument('--nonce');p.add_argument('--parent')
    a=p.parse_args()
    if a.op=='probe': print(json.dumps(notify('bridge_probe',1,'bridge-preflight')))
    elif a.op=='ack':
        if a.nonce!=NONCE or a.parent!=PARENT: raise SystemExit('REJECT wrong binding')
        if (DATA/'probe-ack.json').exists(): raise SystemExit('REJECT duplicate acknowledgement')
        atomic(DATA/'probe-ack.json',dict(v=1,parent=PARENT,nonce=NONCE,receipt='parent-observed',at=time.time()))
        print('ACK recorded')
    else:
        print(json.dumps({p.name:json.loads(p.read_text()) for p in DATA.glob('*.json')},indent=2))
