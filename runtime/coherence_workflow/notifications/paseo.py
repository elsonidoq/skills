"""Public same-parent wake transport and genuine scoped ask_user answers.

Read-only original-session tool results authenticate answers. Queuing is never
answer delivery; an uncertain send is not retried automatically.
"""
import copy
import json
import os
from pathlib import Path
import shutil
import shlex
import sys
import stat
import subprocess
import time

from ..interaction import Interaction, OwnerChannel
from ..store import Blocked, canonical, digest, private_file, safe_path

VERSION = '0.9.2'
TRANSPORT = 'paseo-0.9.2'
PREFIX = 'COHERENCE_PARENT_FACADE_V1'


def text(content):
    return content if isinstance(content,str) else '\n'.join(b.get('text','') for b in content or [] if b.get('type')=='text')


class ParentEvidence:
    """Original active-branch ask_user results only; no transcript export."""
    def __init__(self, descriptor):
        self.descriptor=descriptor
        path=Path(descriptor['session_file'])
        try:
            if not path.is_absolute() or path!=path.resolve(strict=True):raise Blocked('parent evidence path must be canonical/non-symlink')
            fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
        except OSError as exc:raise Blocked('parent evidence missing/unavailable; no receipt') from exc
        try:
            identity=os.fstat(fd)
            if (not stat.S_ISREG(identity.st_mode) or identity.st_uid!=os.getuid() or identity.st_nlink!=1 or
                    identity.st_mode & 0o022):
                raise Blocked('parent evidence ownership/type/write-permission unavailable')
            with os.fdopen(os.dup(fd),'rb') as source:
                lines=[]
                while line:=source.readline():
                    if not line.endswith(b'\n'):raise Blocked('parent evidence partial tail; wait/reconcile, not proof')
                    lines.append(json.loads(line))
            if not lines:raise Blocked('missing parent session header')
            self.header=lines[0]
            if (self.header.get('type')!='session' or self.header.get('version')!=3 or
                    self.header.get('id')!=descriptor['runtime_session_id'] or self.header.get('cwd')!=descriptor['parent_cwd']):
                raise Blocked('parent runtime session/header/cwd mismatch')
            entries={entry['id']:entry for entry in lines[1:] if 'id' in entry}
            if len(entries)!=len(lines)-1:raise Blocked('ambiguous parent entry identities')
            branch=[];current=lines[-1].get('id');seen=set()
            while current is not None:
                if current in seen or current not in entries:raise Blocked('parent branch missing/cyclic')
                seen.add(current);entry=entries[current];branch.append(entry);current=entry.get('parentId')
            self.branch=list(reversed(branch))
            tools={}
            for entry in self.branch:
                message=entry.get('message',{})
                if message.get('role')=='system':
                    if message.get('replace'):tools={}
                    for tool in message.get('toolsAdded',[]):tools[tool['name']]=tool
                    for tool in message.get('toolsRemoved',[]):tools.pop(tool['name'],None)
            if not {'ask_user'}<=tools.keys():raise Blocked('actual parent registered ask_user capability unavailable')
            after=os.fstat(fd)
            if (after.st_dev,after.st_ino)!=(identity.st_dev,identity.st_ino):raise Blocked('parent evidence identity changed')
        except (OSError,ValueError,KeyError) as exc:
            raise Blocked('parent evidence unavailable/invalid; no fabricated receipt') from exc
        finally:os.close(fd)

    def calls(self, tool, predicate, *, unique=True):
        found=[]
        for entry in self.branch:
            message=entry.get('message',{})
            if message.get('role')!='assistant':continue
            for block in message.get('content',[]):
                if block.get('type')=='toolCall' and block.get('name')==tool and predicate(block.get('arguments',{})):
                    results=[item for item in self.branch if item.get('message',{}).get('role')=='toolResult' and
                             item['message'].get('toolCallId')==block['id'] and item['message'].get('toolName')==tool]
                    if len(results)>1:raise Blocked('ambiguous parent tool result')
                    result=results[0] if results else None
                    found.append({'call_id':block['id'],'call_entry':entry['id'],'arguments_hash':digest(block['arguments']),
                                  'result':result,'arguments':block['arguments']})
        if unique and len(found)>1:raise Blocked('ambiguous parent tool invocation; never reask blindly')
        return next((call for call in found if call['result']),found[0] if found else None)

    def question(self, prompt, options, context):
        expected=[{'title':option} for option in options]
        call=self.calls('ask_user',lambda args:args.get('question')==prompt)
        if not call:return None,None
        args=call['arguments']
        if (args.get('context')!=context or args.get('options')!=expected or args.get('allowMultiple',False) or args.get('allowFreeform') is not False or
                args.get('allowComment') is not False):raise Blocked('actual ask_user arguments/options differ from prescribed question')
        receipt={'tool':'ask_user','call_id':call['call_id'],'call_entry':call['call_entry'],'arguments_hash':call['arguments_hash']}
        if not call['result']:return receipt,None
        result=call['result']['message'];details=result.get('details',{})
        response=details.get('response') or {}
        if (result.get('isError') is not False or details.get('cancelled') is not False or details.get('question')!=prompt or
                response.get('kind')!='selection' or len(response.get('selections',[]))!=1 or response['selections'][0] not in options or response.get('comment')):
            raise Blocked('actual ask_user cancelled/errored/unsupported answer; no approval inferred')
        answer=response['selections'][0]
        if text(result.get('content'))!='User answered: '+answer:raise Blocked('actual ask_user result/details conflict')
        receipt.update(result_entry=call['result']['id'],result_hash=digest(result),answer_hash=digest(answer))
        return receipt,answer


class Paseo:
    """One scoped wake obligation; no parent launch/ACK attestation chain."""
    def __init__(self, authority, run, descriptor, *, command=None, sleep=time.sleep):
        self.authority,self.store,self.run=authority,authority.store,run
        self.descriptor=copy.deepcopy(descriptor)
        required={'adapter','version','binding_id','recipient_id','runtime_session_id','session_file','parent_cwd','parent_model','parent_effort'}
        if (set(descriptor)!=required or descriptor['adapter']!=TRANSPORT or descriptor['version']!=VERSION or
                not all(isinstance(descriptor[k],str) and descriptor[k] for k in required)):
            raise Blocked('invalid original-parent binding; supply the scoped operator descriptor')
        if Path(descriptor['session_file']).is_relative_to(authority.project):
            raise Blocked('parent answer evidence must be outside worker-written project')
        binary=shutil.which('paseo')
        if not binary and command is None:raise Blocked('Paseo unavailable; supply transport or select standalone before launch')
        self.binary=str(Path(binary).resolve()) if binary else 'paseo'
        self.command=command or subprocess.run;self.sleep=sleep;self.ready=None
        existing={row['name'] for row in self.store.db.execute('PRAGMA table_info(wf_parent_delivery)')}
        if existing and existing!={'event_id','attempts','tool_receipt','blocker'}:
            raise Blocked('historical parent transport schema unsupported for delivery; use read-only history and obtain scoped renewal before a new run')
        self.store.db.executescript("""
        CREATE TABLE IF NOT EXISTS wf_parent_bindings(run_id TEXT PRIMARY KEY,descriptor TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS wf_parent_delivery(
          event_id TEXT PRIMARY KEY REFERENCES wf_outbox, attempts INTEGER NOT NULL DEFAULT 0,
          tool_receipt TEXT, blocker TEXT);
        """)

    def _command(self,args):
        try:result=self.command([self.binary,*args],capture_output=True,text=True,timeout=10)
        except (OSError,subprocess.TimeoutExpired) as exc:
            raise Blocked('Paseo delivery uncertain/unavailable; reconcile original event before retry') from exc
        if result.returncode:raise Blocked('Paseo command failed; inspect original event before retry')
        return result.stdout

    def inspect(self):
        value=json.loads(self._command(['inspect',self.descriptor['recipient_id'],'--json']))
        if (value.get('Id')!=self.descriptor['recipient_id'] or value.get('Provider')!='pi' or value.get('Archived') or
                value.get('Cwd')!=self.descriptor['parent_cwd'] or value.get('Model')!=self.descriptor['parent_model'] or value.get('Thinking')!=self.descriptor['parent_effort']):
            raise Blocked('original parent unavailable/changed; reconcile binding, never substitute a fresh conversation')
        return value

    def evidence(self):
        self.inspect()
        return ParentEvidence(self.descriptor)

    def preflight(self):
        if self._command(['--version']).strip()!=VERSION:raise Blocked('unsupported Paseo version; supply configured transport')
        self.evidence()
        with self.store.transaction() as db:
            old=db.execute('SELECT descriptor FROM wf_parent_bindings WHERE run_id=?',(self.run,)).fetchone()
            if old and old[0]!=canonical(self.descriptor):raise Blocked('original parent binding changed; explicit renewal required')
            db.execute('INSERT OR IGNORE INTO wf_parent_bindings VALUES(?,?)',(self.run,canonical(self.descriptor)))
        self.ready={'descriptor_hash':digest(self.descriptor)}
        return self.ready

    def identity(self):
        return {'adapter':TRANSPORT,'version':VERSION,'binding':self.descriptor}

    def validate_config(self,config):
        if self.ready is None or config!={'mode':'interactive_parent','question_transport':TRANSPORT,'parent_binding_ref':self.descriptor['binding_id'],'question_tool':'ask_user'}:
            raise Blocked('original parent capability unavailable; verify selected interaction binding')

    def facade_command(self,nonce,event):
        bootstrap='import sys,runpy;sys.path.insert(0,sys.argv.pop(1));runpy.run_module("coherence_workflow.cli",run_name="__main__",alter_sys=True)'
        return shlex.join([sys.executable,'-I','-c',bootstrap,str(Path(__file__).resolve().parents[2]),
            'parent-answer','--project',str(self.authority.project),'--run',self.run,'--nonce',nonce,'--event',event])

    def question_payload(self,gate,event):
        request=json.loads(gate['request'])
        return {'kind':'question','run_id':self.run,'event_id':event,'nonce':gate['nonce'],
            'question':request['question']+'\n[workflow '+self.run+' event '+event+' nonce '+gate['nonce']+']',
            'context':canonical({k:request[k] for k in ('why_owner_needed','recommendation','impact')}),
            'options':[{'title':option} for option in request['options']],
            'allowMultiple':False,'allowFreeform':False,'allowComment':False,
            'answer_command':self.facade_command(gate['nonce'],event),
            'instruction':'Invoke registered ask_user exactly once with these question/options/context/flags, then execute answer_command. If invocation is uncertain, reconcile it; never reask or choose an answer yourself.'}

    def send(self,payload):
        self.evidence()
        root=safe_path(self.authority.project,'.coherence/workflow/parent-events');root.mkdir(mode=0o700,exist_ok=True)
        path=root/(digest(payload)+'.json')
        if not path.exists():
            fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
            with os.fdopen(fd,'w') as f:f.write(PREFIX+'\n'+canonical(payload)+'\n');f.flush();os.fsync(f.fileno())
        private_file(path)
        result=json.loads(self._command(['send','--no-wait',self.descriptor['recipient_id'],'--prompt-file',str(path),'--json']))
        if result.get('agentId')!=self.descriptor['recipient_id'] or result.get('status')!='sent':
            raise Blocked('Paseo send uncertain; reconcile original event, never resend blindly')
        return {'recipient_id':self.descriptor['recipient_id'],'status':'transport_queued'}

    def deliver_pending(self,*,timeout=120):
        row=self.store.db.execute("""SELECT o.event_id,q.* FROM wf_outbox o JOIN wf_questions q USING(gate_id)
            JOIN wf_question_parks p USING(gate_id) WHERE o.run_id=? AND q.stage IN ('pending','answered') ORDER BY q.rowid LIMIT 1""",(self.run,)).fetchone()
        if not row:raise Blocked('no parked original question; reconcile graph before delivery')
        gate=dict(row);event=gate['event_id']
        if gate['stage']=='answered':return True
        payload=self.question_payload(gate,event)
        with self.store.transaction() as db:
            inserted=db.execute('INSERT OR IGNORE INTO wf_parent_delivery(event_id,attempts) VALUES(?,1)',(event,)).rowcount
        if inserted:
            try:
                receipt=self.send(payload)
                with self.store.transaction() as db:
                    db.execute("UPDATE wf_outbox SET stage='transport_queued',receipt=? WHERE event_id=? AND stage='recorded'",(canonical(receipt),event))
            except (Blocked,ValueError) as exc:
                with self.store.transaction() as db:db.execute('UPDATE wf_parent_delivery SET blocker=? WHERE event_id=?',(str(exc),event))
                raise
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            if Interaction(self.store,self.run,initialize=False).question(gate['gate_id'])['stage']=='answered':return True
            self.sleep(.2)
        raise Blocked('original question still pending; reconcile actual ask_user answer, never resend/reask')

    def optional_status(self,payload):
        try:self.send({'kind':'status','run_id':self.run,'facts':payload})
        except Exception:return False
        return True


class ParentChannel(OwnerChannel):
    """Input-only connection; cannot select, launch or replace workers."""
    def __init__(self,project,run):
        super().__init__(project,run)
        self.project=Path(project)
        self.store=self


def facade(project,run,operation,nonce,event=None,*,command=None):
    channel=ParentChannel(project,run)
    try:
        if operation!='parent-answer':raise Blocked('obsolete parent callback; use original scoped parent-answer')
        binding=channel.db.execute('SELECT descriptor FROM wf_parent_bindings WHERE run_id=?',(run,)).fetchone()
        if not binding:raise Blocked('original parent binding unavailable; leave question pending')
        capability=Paseo(channel,run,json.loads(binding[0]),command=command)
        row=channel.db.execute("""SELECT q.*,o.event_id FROM wf_questions q JOIN wf_outbox o USING(gate_id)
            JOIN wf_question_parks p USING(gate_id) WHERE o.run_id=? AND o.event_id=?""",(run,event)).fetchone()
        if not row or row['nonce']!=nonce:raise Blocked('wrong original question/event/nonce; leave pending')
        gate=dict(row);payload=capability.question_payload(gate,event)
        if not channel.db.execute('SELECT 1 FROM wf_parent_delivery WHERE event_id=?',(event,)).fetchone():
            raise Blocked('no original question delivery intent; leave pending')
        receipt,answer=capability.evidence().question(payload['question'],json.loads(gate['request'])['options'],payload['context'])
        if not receipt or answer is None:raise Blocked('genuine original ask_user answer unavailable; leave pending, never reask')
        if json.loads(gate['request'])['category']=='unexpected_material_change':
            raise Blocked('material answer requires producing approval renewal before continuation')
        value={'schema_version':1,'kind':'owner_answer','binding':json.loads(gate['binding']),'input_id':'parent-answer:'+event,
            'gate_id':gate['gate_id'],'nonce':nonce,'pin_policy':'original_only','answer':answer,
            'receipt':{'source':'parent_ask_user','actor':'parent:'+capability.descriptor['runtime_session_id'],
                'record_ref':'pi-tool-result:'+receipt['result_entry'],'record_sha256':digest(receipt),'authority_ref':digest(capability.descriptor)},
            'delivery':'accepted','original_session_ref':json.loads(gate['pin'])['snapshot']['session_file'],'delivery_ref':None}
        accepted=Interaction(channel,run,initialize=False).answer(value,
            verify_owner=lambda v:{'input_hash':digest(v),'scope':'within_envelope'},current_binding=json.loads(gate['binding']))
        with channel.transaction() as db:db.execute('UPDATE wf_parent_delivery SET tool_receipt=?,blocker=NULL WHERE event_id=?',(canonical(receipt),event))
        return {'stage':accepted['stage'],'input_id':accepted['input_id']}
    finally:channel.close()
