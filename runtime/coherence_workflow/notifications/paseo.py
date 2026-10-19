"""Pinned public Paseo wake transport plus selective official Pi provenance.

Session JSONL is READ-ONLY evidence, never a messaging channel or workflow store.
The boundary trusts the local operator and registered tools, not malicious same-UID
processes. No private supervisor APIs, global settings writes or provider calls.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import shlex
import sys
import sqlite3
import stat
import subprocess
import time
import uuid

from ..interaction import Interaction, OwnerChannel
from ..store import Blocked, canonical, digest, private_file, safe_path

VERSION = '0.9.2'
TRANSPORT = 'paseo-0.9.2'
PREFIX = 'COHERENCE_PARENT_FACADE_V1'


def text(content):
    return content if isinstance(content,str) else '\n'.join(b.get('text','') for b in content or [] if b.get('type')=='text')


def shell_matches(arguments, marker, required):
    command=arguments.get('command')
    if not isinstance(command,str) or marker not in command:return False
    try:tokens=shlex.split(command,comments=True)
    except ValueError:return False
    return all(part in tokens or part in command for part in required)


class ParentEvidence:
    """Bounded active-branch metadata/tool receipts only; no transcript export."""
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
                    identity.st_mode & 0o022 or identity.st_size>32*1024*1024):
                raise Blocked('parent evidence ownership/type/write-permission/size unavailable')
            with os.fdopen(os.dup(fd),'rb') as source:
                lines=[]
                while line:=source.readline(1024*1024+1):
                    if len(line)>1024*1024:raise Blocked('parent evidence record limit')
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
            if not {'bash','ask_user'}<=tools.keys():raise Blocked('actual parent registered bash/ask_user capability unavailable')
            after=os.fstat(fd)
            if (after.st_dev,after.st_ino)!=(identity.st_dev,identity.st_ino):raise Blocked('parent evidence identity changed')
            self.identity={'device':identity.st_dev,'inode':identity.st_ino,'uid':identity.st_uid,
                           'session_id':self.header['id'],'cwd':self.header['cwd'],'tools_hash':digest(tools)}
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

    def shell(self, marker, required):
        call=self.calls('bash',lambda args:shell_matches(args,marker,required),unique=False)
        if not call or not call['result']:return None
        result=call['result']['message']
        if result.get('isError') is not False or marker not in text(result.get('content')):
            raise Blocked('parent facade tool failed/cancelled or lacks bound completed outcome')
        return {'call_id':call['call_id'],'call_entry':call['call_entry'],'arguments_hash':call['arguments_hash'],
                'result_entry':call['result']['id'],'result_hash':digest(result),'tool':'bash'}

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
    """Registered capability. Only deterministic facade events are sent."""
    def __init__(self, authority, run, descriptor, *, command=None, sleep=time.sleep):
        self.authority,self.store,self.run=authority,authority.store,run
        self.descriptor=copy.deepcopy(descriptor)
        required={'adapter','version','binding_id','recipient_id','runtime_session_id','session_file','parent_cwd','parent_model','parent_effort','generation','launch_nonce'}
        if (set(descriptor)!=required or descriptor['adapter']!=TRANSPORT or descriptor['version']!=VERSION or
                type(descriptor['generation']) is not int or descriptor['generation']<1 or
                not all(isinstance(descriptor[k],str) and descriptor[k] for k in required-{'generation'})):
            raise Blocked('closed registered parent descriptor required')
        if Path(descriptor['session_file']).is_relative_to(authority.project):raise Blocked('parent evidence cannot be worker-written project input')
        self.binary=str(Path(shutil.which('paseo') or '').resolve(strict=True))
        self.command=command or subprocess.run;self.sleep=sleep;self.ready=None
        self.code_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        self.store.db.executescript('''
        CREATE TABLE IF NOT EXISTS wf_parent_preflight(
          run_id TEXT PRIMARY KEY, descriptor TEXT NOT NULL, identity TEXT NOT NULL,
          nonce TEXT NOT NULL UNIQUE, stage TEXT NOT NULL, launch_receipt TEXT NOT NULL,
          ready_receipt TEXT, blocker TEXT);
        CREATE TABLE IF NOT EXISTS wf_parent_delivery(
          event_id TEXT PRIMARY KEY REFERENCES wf_outbox, generation_hash TEXT NOT NULL,
          attempts INTEGER NOT NULL DEFAULT 0, claim TEXT, tool_receipt TEXT, blocker TEXT);
        CREATE TABLE IF NOT EXISTS wf_parent_attempts(
          seq INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL, event_id TEXT,
          action TEXT NOT NULL, outcome TEXT NOT NULL);
        ''')
        if self._command(['--version']).strip()!=VERSION:raise Blocked('unsupported public Paseo version')

    def _command(self, args):
        try:
            result=self.command([self.binary,*args],capture_output=True,text=True,timeout=10)
        except (OSError,subprocess.TimeoutExpired) as exc:raise Blocked('Paseo transport unavailable/timeout') from exc
        if result.returncode:raise Blocked('Paseo public command unavailable; no successful delivery claim')
        if len(result.stdout.encode())>262144:raise Blocked('Paseo response byte limit')
        return result.stdout

    def inspect(self):
        value=json.loads(self._command(['inspect',self.descriptor['recipient_id'],'--json']))
        if (value.get('Id')!=self.descriptor['recipient_id'] or value.get('Provider')!='pi' or value.get('Archived') or
                value.get('Cwd')!=self.descriptor['parent_cwd'] or value.get('Model')!=self.descriptor['parent_model'] or value.get('Thinking')!=self.descriptor['parent_effort']):
            raise Blocked('actual launching parent recipient/runtime/cwd mismatch; no silent rebind')
        return {key:value[key] for key in ('Id','Provider','Cwd','Model','Thinking','Status')}

    def evidence(self):
        self.inspect()
        evidence=ParentEvidence(self.descriptor)
        saved=self.store.db.execute('SELECT identity FROM wf_parent_preflight WHERE run_id=?',(self.run,)).fetchone()
        if saved and saved[0]!=canonical(evidence.identity):raise Blocked('parent runtime/generation/tool identity changed; explicit rebind required')
        return evidence

    def attempt(self, action, outcome, event=None):
        with self.store.transaction() as db:
            db.execute('INSERT INTO wf_parent_attempts(run_id,event_id,action,outcome) VALUES(?,?,?,?)',(self.run,event,action,outcome))

    def send(self, payload, *, attempts=40, interval=.5):
        event=payload.get('event_id')
        last=None
        for unused in range(attempts):
            try:
                observed=self.inspect()
                if observed['Status']!='idle':
                    self.attempt('inspect','busy',event);last='parent busy; bounded idle retry';self.sleep(interval);continue
                self.evidence()
                root=safe_path(self.authority.project,'.coherence/workflow/parent-events');root.mkdir(mode=0o700,exist_ok=True)
                path=root/(digest(payload)+'.json')
                if not path.exists():
                    fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
                    with os.fdopen(fd,'w') as f:f.write(PREFIX+'\n'+canonical(payload)+'\n');f.flush();os.fsync(f.fileno())
                result=json.loads(self._command(['send','--no-wait',self.descriptor['recipient_id'],'--prompt-file',str(path),'--json']))
                if result.get('agentId')!=self.descriptor['recipient_id'] or result.get('status')!='sent':raise Blocked('Paseo queued receipt missing/correlated incorrectly')
                self.attempt('send','transport_queued',event)
                return {'recipient_id':self.descriptor['recipient_id'],'payload_hash':digest(payload),'status':'transport_queued'}
            except (Blocked,ValueError) as exc:
                last=str(exc);self.attempt('send','unavailable',event);self.sleep(interval)
        raise Blocked(last or 'required parent transport unavailable')

    def facade_command(self, operation, nonce, event=None):
        # Use the actual approved interpreter/package, not a source-checkout-relative script.
        argv=[sys.executable,'-m','coherence_workflow.cli',operation,'--project',str(self.authority.project),
              '--run',self.run,'--nonce',nonce]
        if event:argv+=['--event',event]
        label={'parent-ready':'READY','parent-received':'RECEIVED','parent-answer':'ANSWER'}[operation]
        return shlex.join(argv)+' # COHERENCE_PARENT_'+label+':'+(event or nonce)

    def preflight(self, *, timeout=90):
        evidence=self.evidence()
        marker='COHERENCE_LAUNCH_RECEIPT:'+self.descriptor['launch_nonce']
        deadline=time.monotonic()+timeout
        launch=None
        while time.monotonic()<deadline:
            launch=evidence.shell(marker,[str(self.authority.project),self.run,'coordinate-implementation','start'])
            if launch:break
            self.sleep(.1);evidence=self.evidence()
        if not launch:raise Blocked('actual completed registered parent launch provenance unavailable')
        with self.store.transaction() as db:
            old=db.execute('SELECT * FROM wf_parent_preflight WHERE run_id=?',(self.run,)).fetchone()
            if old:
                if old['descriptor']!=canonical(self.descriptor) or old['launch_receipt']!=canonical(launch):raise Blocked('parent launch descriptor/provenance drift')
                nonce=old['nonce']
            else:
                nonce=uuid.uuid4().hex
                db.execute("INSERT INTO wf_parent_preflight VALUES(?,?,?,?,'challenge_recorded',?,NULL,NULL)",
                           (self.run,canonical(self.descriptor),canonical(evidence.identity),nonce,canonical(launch)))
        old=self.store.db.execute('SELECT * FROM wf_parent_preflight WHERE run_id=?',(self.run,)).fetchone()
        payload={'kind':'ready','run_id':self.run,'project':str(self.authority.project),'nonce':nonce,
                 'recipient_id':self.descriptor['recipient_id'],'runtime_session_id':self.descriptor['runtime_session_id'],
                 'command':self.facade_command('parent-ready',nonce),
                 'instruction':'Prescribed facade only: execute the exact command field through registered bash, then stop. No task/model/session/outcome choice.'}
        if old['stage']!='ready':self.send(payload)
        while time.monotonic()<deadline:
            ready=self.evidence().shell('COHERENCE_PARENT_READY:'+nonce,['parent-ready',str(self.authority.project),self.run,nonce])
            if ready:
                with self.store.transaction() as db:
                    db.execute("UPDATE wf_parent_preflight SET stage='ready',ready_receipt=?,blocker=NULL WHERE run_id=?",(canonical(ready),self.run))
                self.ready={'descriptor_hash':digest(self.descriptor),'identity':evidence.identity,'launch':launch,'ready':ready,'nonce':nonce}
                return self.ready
            self.sleep(.2)
        raise Blocked('same-parent actual readiness ACK unavailable; no interactive reliance')

    def identity(self):
        return {'adapter':TRANSPORT,'version':VERSION,'source_hash':self.code_hash,'ready':self.ready}

    def validate_config(self, config):
        if (self.ready is None or hashlib.sha256(Path(__file__).read_bytes()).hexdigest()!=self.code_hash or
                config!={'mode':'interactive_parent','question_transport':TRANSPORT,'parent_binding_ref':self.descriptor['binding_id'],'question_tool':'ask_user'}):
            raise Blocked('registered actually preflighted parent/question capability required')

    def question_payload(self, gate, event):
        request=json.loads(gate['request'])
        prompt=request['question']+'\n[workflow '+self.run+' event '+event+' nonce '+gate['nonce']+']'
        return {'kind':'question','project':str(self.authority.project),'run_id':self.run,'event_id':event,'nonce':gate['nonce'],
                'question':prompt,'context':canonical({k:request[k] for k in ('why_owner_needed','recommendation','impact')}),
                'options':[{'title':option} for option in request['options']],
                'allowMultiple':False,'allowFreeform':False,'allowComment':False,
                'received_command':self.facade_command('parent-received',gate['nonce'],event),
                'answer_command':self.facade_command('parent-answer',gate['nonce'],event),
                'instruction':'Prescribed facade only: parent-received; if ask_allowed true invoke actual registered ask_user with these exact question/options/flags, then parent-answer. Never choose workflow task/model/session/outcome.'}

    def deliver_pending(self, *, timeout=120):
        row=self.store.db.execute("""SELECT o.event_id,q.* FROM wf_outbox o JOIN wf_questions q USING(gate_id)
            JOIN wf_question_parks p USING(gate_id) WHERE o.run_id=? AND q.stage IN ('pending','answered') ORDER BY q.rowid LIMIT 1""",(self.run,)).fetchone()
        if not row:raise Blocked('no graph-parked parent question eligible')
        gate=dict(row);event=gate['event_id'];identity=digest(self.ready)
        with self.store.transaction() as db:
            db.execute('INSERT OR IGNORE INTO wf_parent_delivery(event_id,generation_hash) VALUES(?,?)',(event,identity))
            delivery=db.execute('SELECT * FROM wf_parent_delivery WHERE event_id=?',(event,)).fetchone()
            if delivery['generation_hash']!=identity:raise Blocked('outbox parent generation changed; no rebind')
        payload=self.question_payload(gate,event)
        if gate['stage']=='answered':return True
        delivery=self.store.db.execute('SELECT * FROM wf_parent_delivery WHERE event_id=?',(event,)).fetchone()
        if not delivery['claim']:
            with self.store.transaction() as db:db.execute('UPDATE wf_parent_delivery SET attempts=attempts+1 WHERE event_id=?',(event,))
            queued=self.send(payload)
            with self.store.transaction() as db:
                changed=db.execute("UPDATE wf_outbox SET stage='transport_queued',receipt=? WHERE event_id=? AND stage='recorded'",(canonical(queued),event))
                if changed.rowcount:self.store.event(db,self.run,None,'parent_transport_queued',{'event_id':event,'receipt':queued})
        deadline=time.monotonic()+timeout
        try:
            while time.monotonic()<deadline:
                evidence=self.evidence()
                received=evidence.shell('COHERENCE_PARENT_RECEIVED:'+event,['parent-received',str(self.authority.project),self.run,event,gate['nonce']])
                call,answer=evidence.question(payload['question'],json.loads(gate['request'])['options'],payload['context'])
                record_delivery_provenance(self.store,self.run,event,received,call)
                current_gate=Interaction(self.store,self.run,initialize=False).question(gate['gate_id'])
                if current_gate['stage']=='answered':return True
                if current_gate['stage']=='cancelled':raise Blocked('owner cancelled pending question')
                self.sleep(.2)
            raise Blocked('parent delivery/tool answer unavailable; durable pending, no blind reask')
        except Blocked as exc:
            with self.store.transaction() as db:db.execute('UPDATE wf_parent_delivery SET blocker=? WHERE event_id=?',(str(exc),event))
            raise

    def optional_status(self, payload):
        try:self.send({'kind':'status','run_id':self.run,'facts':payload},attempts=1,interval=0)
        except Exception:return False
        return True


class ParentChannel(OwnerChannel):
    """Runner facade input channel; readiness exists before workflow reservation."""
    def __init__(self, project, run):
        project=Path(project)
        if project!=project.resolve(strict=True):raise Blocked('parent channel project must be canonical')
        self.project=project
        self.path=safe_path(project,'.coherence/workflow/workflow.sqlite');self.identity=private_file(self.path)
        self.db=sqlite3.connect(self.path.as_uri()+'?mode=rw',uri=True,isolation_level=None,timeout=5)
        self.db.row_factory=sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON');self.db.execute('PRAGMA synchronous=FULL');self.db.execute('PRAGMA busy_timeout=5000')
        if not self.db.execute('SELECT 1 FROM wf_parent_preflight WHERE run_id=?',(run,)).fetchone():
            self.db.close();raise Blocked('no registered parent preflight for facade input')
        self.store=self


def record_delivery_provenance(store, run, event, received, call):
    if not received:return
    with store.transaction() as db:
        current=db.execute('SELECT stage FROM wf_outbox WHERE event_id=? AND run_id=?',(event,run)).fetchone()[0]
        if current=='recorded':
            proof={'reconciled_from_actual_parent_received':received}
            db.execute("UPDATE wf_outbox SET stage='transport_queued',receipt=? WHERE event_id=?",(canonical(proof),event))
            store.event(db,run,None,'parent_transport_queued',{'event_id':event,'receipt':proof})
            current='transport_queued'
        if current=='transport_queued':
            db.execute("UPDATE wf_outbox SET stage='parent_received',receipt=? WHERE event_id=?",(canonical(received),event))
            store.event(db,run,None,'parent_received',{'event_id':event,'receipt':received})
            current='parent_received'
        if call:
            db.execute('UPDATE wf_parent_delivery SET tool_receipt=? WHERE event_id=?',(canonical(call),event))
            if current=='parent_received':
                db.execute("UPDATE wf_outbox SET stage='question_tool_invoked' WHERE event_id=?",(event,))
                store.event(db,run,None,'parent_question_tool_invoked',{'event_id':event,'receipt':call})


def facade(project, run, operation, nonce, event=None, *, command=None):
    """Prescribed registered parent actions only. No tasks/models/graph decisions."""
    channel=ParentChannel(project,run)
    try:
        preflight=channel.db.execute('SELECT * FROM wf_parent_preflight WHERE run_id=?',(run,)).fetchone()
        capability=Paseo(channel,run,json.loads(preflight['descriptor']),command=command)
        evidence=capability.evidence()
        if operation=='parent-ready':
            if nonce!=preflight['nonce']:raise Blocked('wrong/stale parent readiness nonce')
            marker='COHERENCE_PARENT_READY:'+nonce
            call=evidence.calls('bash',lambda args:shell_matches(args,marker,['parent-ready',str(project),run,nonce]),unique=False)
            if not call:raise Blocked('actual registered parent readiness invocation unavailable')
            # The executing bash result cannot yet be finalized. The runner will
            # independently verify its completed marker/result before reliance.
            return {'marker':marker,'stage':'ack_received','call_id':call['call_id']}
        if preflight['stage']!='ready' or not preflight['ready_receipt']:raise Blocked('actual parent readiness not complete')
        capability.ready={'descriptor_hash':digest(capability.descriptor),'identity':json.loads(preflight['identity']),
                          'launch':json.loads(preflight['launch_receipt']),'ready':json.loads(preflight['ready_receipt']),'nonce':preflight['nonce']}
        row=channel.db.execute("""SELECT q.*,o.event_id FROM wf_questions q JOIN wf_outbox o USING(gate_id)
            JOIN wf_question_parks p USING(gate_id) WHERE o.run_id=? AND o.event_id=?""",(run,event)).fetchone()
        if not row or row['nonce']!=nonce:raise Blocked('wrong/stale event/gate nonce or missing graph park')
        gate=dict(row);payload=capability.question_payload(gate,event)
        delivery=channel.db.execute('SELECT * FROM wf_parent_delivery WHERE event_id=?',(event,)).fetchone()
        if not delivery or delivery['generation_hash']!=digest(capability.ready) or delivery['attempts']<1:
            raise Blocked('facade has no recorded automatic transport obligation')
        if operation=='parent-received':
            marker='COHERENCE_PARENT_RECEIVED:'+event
            call=evidence.calls('bash',lambda args:shell_matches(args,marker,['parent-received',str(project),run,event,nonce]),unique=False)
            if not call:raise Blocked('actual registered parent receipt invocation unavailable')
            with channel.transaction() as db:
                current=db.execute('SELECT claim FROM wf_parent_delivery WHERE event_id=?',(event,)).fetchone()[0]
                if current:return {'marker':marker,'ask_allowed':False,'reason':'durable claim exists; reconcile actual invocation/answer, never blindly reask'}
                if gate['stage']!='pending':raise Blocked('question not pending; no ask allowed')
                claim={'call_id':call['call_id'],'call_entry':call['call_entry'],'arguments_hash':call['arguments_hash']}
                db.execute('UPDATE wf_parent_delivery SET claim=? WHERE event_id=? AND claim IS NULL',(canonical(claim),event))
                channel.event(db,run,None,'parent_question_claimed',{'event_id':event,'claim':claim})
            return {'marker':marker,'ask_allowed':True}
        if operation!='parent-answer':raise Blocked('unknown prescribed parent operation')
        marker='COHERENCE_PARENT_ANSWER:'+event
        submitted=evidence.calls('bash',lambda args:shell_matches(args,marker,['parent-answer',str(project),run,event,nonce]),unique=False)
        if not submitted or not delivery['claim']:raise Blocked('actual parent answer submission/claim unavailable')
        receipt,answer=evidence.question(payload['question'],json.loads(gate['request'])['options'],payload['context'])
        if not receipt or answer is None:raise Blocked('actual completed ask_user answer unavailable; never fabricate or reask')
        received=evidence.shell('COHERENCE_PARENT_RECEIVED:'+event,['parent-received',str(project),run,event,nonce])
        if not received:raise Blocked('actual completed parent receipt unavailable')
        record_delivery_provenance(channel,run,event,received,receipt)
        if json.loads(gate['request'])['category']=='unexpected_material_change':
            raise Blocked('genuine material answer retained in tool provenance; producing approval renewal required before continuation')
        inputs=channel.db.execute('SELECT contract FROM wf_run_inputs WHERE run_id=?',(run,)).fetchone()
        if not inputs:raise Blocked('original admitted source authority unavailable')
        contract=json.loads(inputs[0])
        for source in contract['sources']:
            if hashlib.sha256(safe_path(project,source['path']).read_bytes()).hexdigest()!=source['sha256']:
                raise Blocked('source changed; producing renewal required')
        for ref in contract['approval_refs']:
            if hashlib.sha256(safe_path(project,ref['record_ref']).read_bytes()).hexdigest()!=ref['record_sha256']:
                raise Blocked('approval changed; producing renewal required')
        value={'schema_version':1,'kind':'owner_answer','binding':json.loads(gate['binding']),'input_id':'parent-answer:'+event,
               'gate_id':gate['gate_id'],'nonce':nonce,'pin_policy':'original_only','answer':answer,
               'receipt':{'source':'parent_ask_user','actor':'parent:'+capability.descriptor['runtime_session_id'],
                   'record_ref':'pi-tool-result:'+receipt['result_entry'],'record_sha256':digest(receipt),'authority_ref':digest(capability.ready)},
               'delivery':'accepted','original_session_ref':json.loads(gate['pin'])['snapshot']['session_file'],'delivery_ref':None}
        ledger=Interaction(channel,run,initialize=False)
        accepted=ledger.answer(value,verify_owner=lambda v:{'input_hash':digest(v),'scope':'within_envelope'},current_binding=json.loads(gate['binding']))
        with channel.transaction() as db:
            db.execute("UPDATE wf_outbox SET stage='answered',receipt=? WHERE event_id=?",(canonical(receipt),event))
        return {'marker':marker,'stage':accepted['stage'],'input_id':accepted['input_id'],'actual_tool_receipt':receipt}
    finally:channel.close()
