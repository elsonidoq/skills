"""Authenticated inherited-pipe SDK transport and runner-owned telemetry segments.

No task scheduler/approval/Git authority. Trusted callers supply verified manifests and
T001 Gateway; unknown host/tool state poisons reuse and remains durably unreconciled.
"""
import copy
import json
import math
import os
from pathlib import Path
import selectors
import shutil
import time
import uuid

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from .store import Blocked, canonical, digest, git, safe_path, private_file
from .tools import ProcessTool
from .registry import validate_schema

MAX_RECORD = 262144
TOKEN_FIELDS = ('input','output','cacheRead','cacheWrite')


def failure_diagnostic(exc, *, phase, host_op, operation_id, pending):
    """Allowlisted causal metadata only: never provider text, arguments or transcripts."""
    classes={'Blocked','ValidationError','JSONDecodeError','TimeoutError','BrokenPipeError',
             'FileNotFoundError','PermissionError','OSError','RuntimeError','ValueError'}
    names=[];seen=set();cause=exc
    while cause is not None and id(cause) not in seen and len(names)<4:
        seen.add(id(cause));name=type(cause).__name__
        names.append(name if name in classes else 'unclassified_exception')
        cause=cause.__cause__ or cause.__context__
    category='tool_or_record_schema' if isinstance(exc,ValidationError) else 'unclassified_failure'
    known={'SDK host EOF; task tools require reconciliation':'host_eof',
           'SDK prompt deadline':'prompt_deadline','SDK prompt failed':'sdk_prompt_failed',
           'controlled pressure/pause':'controlled_interrupt',
           'SDK context pressure/compaction; drain and owner recovery required':'context_pressure',
           'unregistered tool binding':'tool_binding','tool outside current prompt':'tool_correlation',
           'ORPHAN_PROCESS: tool result cannot release prompt':'orphan_process',
           'unreconciled process operation; replacement_allowed=false':'unsettled_process_admission',
           'task-tool queue byte limit; no request dropped or released':'tool_queue_limit',
           'duplicate/invalid tool call identity':'tool_call_identity',
           'review tool mutation denied':'review_tool_scope',
           'settlement with pending/queued task tools':'unsettled_tool_batch'}
    if isinstance(exc,Blocked):category=known.get(str(exc),'local_guard_or_protocol_blocker')
    validator=exc.validator if isinstance(exc,ValidationError) and exc.validator in ('enum','type','required','additionalProperties','const','maxLength','oneOf') else None
    return {'classification':category,'exception_types':names,'schema_validator':validator,
            'phase':phase,'host_op':host_op,'operation_id':operation_id,'pending_tool_operations':sorted(pending)}


def host_resource():
    """One shipped host, in a source suite or installed wheel data (never provisioning)."""
    source=Path(__file__).resolve().parents[1]/'pi-host/host.mjs'
    if source.is_file():
        return source.resolve(strict=True)
    from importlib.metadata import distribution, PackageNotFoundError
    try:
        installed=distribution('coherence-workflow')
        import sysconfig
        # pip --target places wheel data beneath the target; normal prefix installs
        # use the interpreter's data scheme. RECORD may omit relocated --target data.
        relative='share/coherence-workflow/pi-host/host.mjs'
        candidates=[installed.locate_file(relative),Path(sysconfig.get_path('data'))/relative]
        candidates += [installed.locate_file(p) for p in installed.files or []
                       if str(p).endswith('/pi-host/host.mjs')]
        for candidate in candidates:
            if candidate.is_file():return candidate.resolve(strict=True)
    except PackageNotFoundError:
        pass
    raise Blocked('packaged pinned SDK host unavailable; explicit isolated setup required')


class Decoder:
    def __init__(self, limit=MAX_RECORD):
        self.limit, self.buffer = limit, bytearray()

    def feed(self, chunk):
        records = []
        for part in chunk.split(b'\n')[:-1]:
            if len(self.buffer)+len(part)>self.limit:
                raise Blocked('host record too large')
            self.buffer.extend(part)
            records.append(json.loads(self.buffer.decode('utf-8')))
            self.buffer.clear()
        tail = chunk.rsplit(b'\n',1)[-1]
        if len(self.buffer)+len(tail)>self.limit:
            raise Blocked('host record too large')
        self.buffer.extend(tail)
        return records

    def end(self):
        if self.buffer:
            raise Blocked('incomplete host record')


def usage_segment(before, after, *, exclusive=True, outcome='settled'):
    """No subtraction across reopen, branch/reset, ambiguity, interruption or missing data."""
    reason = None
    if not before or not after:
        reason = 'missing_or_killed_final_observation'
    elif not exclusive:
        reason = 'nonexclusive_operation'
    elif outcome != 'settled':
        reason = 'interrupted_or_ambiguous_summary'
    elif any(before.get(k) is None or before.get(k)!=after.get(k) for k in ('session_id','branch','epoch')):
        reason = 'session_branch_or_counter_epoch_changed'
    deltas = {}
    for key in TOKEN_FIELDS:
        a,b=(before or {}).get('counters',{}).get(key),(after or {}).get('counters',{}).get(key)
        field_reason = reason
        if not field_reason and (type(a) is not int or type(b) is not int or min(a,b)<0 or max(a,b)>2**53-1):
            field_reason = 'missing_invalid_counter'
        if not field_reason and b<a:
            field_reason = 'counter_reset'
        deltas[key] = {'value':None if field_reason else b-a,'unknown_reason':field_reason}
    cost = None
    cost_reason = reason
    a,b=(before or {}).get('cost'),(after or {}).get('cost')
    if not cost_reason and all(type(v) in (int,float) and math.isfinite(v) for v in (a,b)) and b>=a>=0:
        cost=b-a
    else:
        cost_reason=cost_reason or 'missing_or_reset_cost'
    return {'tokens':deltas,'cost':{'value':cost,'unknown_reason':cost_reason},
            'before':before,'after':after,'outcome':outcome}


def non_agent_segment(kind):
    if kind not in ('code','gate','terminal'):
        raise Blocked('not a non-agent node')
    return {'session_id':None,'context':None,'tokens':None,'cost':None,'unknown_reason':'non_agent_node'}


class Lifecycle:
    """Current-generation fence; agent_end or acceptance never grants completion."""
    def __init__(self):
        self.generation=0
        self.poisoned=False
        self.active=False
        self.started=False
        self.settled=False

    def begin(self):
        if self.active or self.poisoned:
            raise Blocked('host unavailable pending reconciliation')
        self.generation+=1
        self.active=True
        self.started=self.settled=False
        return self.generation

    def event(self, payload):
        if payload.get('generation') != self.generation or not self.active:
            raise Blocked('stale/early lifecycle generation')
        kind=payload.get('type')
        if kind=='agent_start':
            self.started=True;self.settled=False
        if kind in ('auto_retry_start','compaction_start'):
            self.settled=False
        if kind=='agent_settled' and self.started:
            self.settled=True
        if kind in ('poisoned','assistant_failure'):
            # A transient failed assistant can be followed by an SDK retry. Do not
            # settle on it; final failure is represented by host poisoned.
            self.settled=False
            if kind=='poisoned': self.poisoned=True

    def finish(self,payload):
        if (self.poisoned or not self.active or payload.get('generation')!=self.generation or
            not self.started or not self.settled or payload.get('promise_done') is not True or payload.get('idle') is not True):
            self.poisoned=True
            raise Blocked('uncertain SDK settlement')
        self.active=False


class PiAdapter:
    """One host, one active prompt. Caller owns authorization and manifest provenance."""
    def __init__(self,gateway,manifest,*,node,environment,session_context,reopen_from=None,host_path=None,interaction=None,question_binding=None):
        gateway.authority.assert_held()
        self.gateway=gateway
        self.manifest=copy.deepcopy(manifest)
        self.interaction, self.question_binding = interaction, copy.deepcopy(question_binding)
        self.question_gate = None
        if manifest.get('cwd') != str(gateway.authority.project):
            raise Blocked('SDK worktree mismatch')
        private_root=safe_path(gateway.authority.project,'.coherence/workflow')
        for key in ('agent_dir','session_dir'):
            p=Path(manifest[key])
            if not p.is_relative_to(private_root) or p != p.resolve(strict=True):
                raise Blocked('SDK conversation directories must be private worktree runtime storage')
            s=p.stat()
            if s.st_uid!=os.getuid() or s.st_mode & 0o077:
                raise Blocked('SDK directory not private/owned')
        if 'open' in manifest:
            try:private_file(Path(manifest['open']['file']))
            except OSError as exc:
                raise Blocked('original saved conversation unavailable; explicit owner recovery required') from exc
        if (set(session_context) != {'role','affinity','review_lineage'} or
            any(not isinstance(session_context[k],str) or not session_context[k] for k in ('role','affinity')) or
            session_context['review_lineage'] is not None and not isinstance(session_context['review_lineage'],str)):
            raise Blocked('closed session role/affinity/lineage context required')
        for spec in manifest['tools']:
            if spec['name'] == 'request_owner_input':
                from .interaction import QUESTION_SCHEMA
                if (interaction is None or question_binding is None or spec['parameters'] != QUESTION_SCHEMA or
                        spec['version'] != '1' or spec['permission'] != 'request_owner_input'):
                    raise Blocked('question tool lacks runner interaction binding')
                continue
            tool=gateway.tools.get(spec['name'])
            if (not tool or tool.version!=spec['version'] or tool.arguments!=spec['parameters'] or
                session_context['role']=='review' and tool.owned_paths):
                raise Blocked('SDK tool manifest differs from registered role-safe gateway')
        from .sessions import manifest_compatibility
        self.compatibility=manifest_compatibility(manifest,gateway.authority.project,**session_context)
        if 'open' in manifest:
            if not reopen_from:raise Blocked('exact prior host custody reference required')
            prior=gateway.store.operation(reopen_from)
            if prior['run_id']!=gateway.run or prior['phase']!='completed':raise Blocked('prior host not reconciled')
            gateway.verify_closed_host(reopen_from)
            ready=gateway.store.db.execute("SELECT payload FROM wf_events WHERE op_id=? AND kind='host_ready'",(reopen_from,)).fetchone()
            if not ready:raise Blocked('prior host role/resource provenance missing')
            old=json.loads(ready[0])['compatibility']
            family=lambda r:'implement' if r in ('implement','repair') else r
            if family(old['role'])!=family(self.compatibility['role']) or any(old[k]!=v for k,v in self.compatibility.items() if k!='role'):
                raise Blocked('reopen role/resource/worktree drift')
            matches=[]
            for row in gateway.store.db.execute("SELECT result FROM wf_operations WHERE run_id=? AND kind='sdk-turn' AND phase='completed'",(gateway.run,)):
                result=json.loads(row[0])
                if result.get('host_op')==reopen_from:matches.append(result)
            if not matches:raise Blocked('prior settled conversation telemetry missing')
            last=max(matches,key=lambda x:x['generation'])['after']
            expected=manifest['open']
            if any(expected[k]!=last[v] for k,v in (('file','session_file'),('session_id','session_id'),('leaf','leaf'),('sha256','session_file_hash'))):
                raise Blocked('saved conversation differs from durable settled telemetry')
        elif reopen_from is not None:
            raise Blocked('prior reference only applies to exact open')
        self.binding={'host_id':uuid.uuid4().hex,'run_id':gateway.run,'nonce':uuid.uuid4().hex}
        self.lifecycle=Lifecycle()
        self.sequence=self.in_sequence=0
        self.session_id=None
        self.current=None
        self.pending={}
        self.tool_queue=[]
        self.queued_tool_bytes=0
        self.tool_calls_seen=set()
        self.decoder=Decoder()
        self.queue=[]
        self.closed=False
        self.records=[]
        self.snapshot=None
        self.host_path=Path(host_path).resolve(strict=True) if host_path is not None else host_resource()
        node_binary=Path(shutil.which('node') or '').resolve(strict=True)
        boot_r,boot_w=os.pipe();command_r,self.command_w=os.pipe();self.event_r,event_w=os.pipe()
        fds=(boot_r,command_r,event_w)
        tool_id='sdk-host-'+self.binding['host_id']
        gateway.tools[tool_id]=ProcessTool(tool_id,'1',{'type':'object','additionalProperties':False},
            lambda args:[str(node_binary),str(self.host_path),*[str(fd) for fd in fds]],(),dict(environment))
        try:
            os.write(boot_w,(canonical(self.binding)+'\n').encode());os.close(boot_w);boot_w=-1
            self.host_op,self.proc=gateway.launch(node,tool_id,'1',{},scope_kind='host',inherited_fds=fds)
        except BaseException:
            os.close(self.command_w);os.close(self.event_r)
            raise
        finally:
            for fd in (*fds,boot_w):
                if fd>=0:os.close(fd)
            gateway.tools.pop(tool_id,None)
        self.selector=selectors.DefaultSelector();self.selector.register(self.event_r,selectors.EVENT_READ)
        self.request_bindings={}
        self.control_commands={}
        self.control_acknowledgements={}
        try:
            self._persist('host_admission',{'compatibility':self.compatibility,'manifest_hash':digest(self.manifest)},self.host_op)
            command=self.send('open' if 'open' in manifest else 'create',self.manifest,operation_id=self.host_op,attempt_id=node)
            response=self.wait_response(command,30)
            self.snapshot=response['snapshot']
            # A settled, exact-compatible original may be reused even when optional
            # context telemetry is absent or low.  The snapshot remains recorded.
            self.session_id=self.snapshot['session_id']
            self._persist('host_ready',{'host_op':self.host_op,'snapshot':self.snapshot,'compatibility':self.compatibility},self.host_op)
        except BaseException:
            self.lifecycle.poisoned=True
            self.close(force=True)
            raise

    def _persist(self,kind,payload,op=None):
        with self.gateway.store.transaction() as db:
            self.gateway.store.event(db,self.gateway.run,op,kind,payload)

    def send(self,op,payload,*,operation_id=None,attempt_id=None):
        if self.closed:raise Blocked('closed host')
        self.sequence+=1
        id=uuid.uuid4().hex
        record={'protocol_version':1,**self.binding,'sequence':self.sequence,'command_id':id,
            'operation_id':operation_id or self.current['operation_id'],'attempt_id':attempt_id or self.current['attempt_id'],
            'session_id':self.session_id,'type':'command','op':op,'payload_schema':'sdk-v1','payload':payload}
        data=(canonical(record)+'\n').encode()
        if len(data)>MAX_RECORD:raise Blocked('command too large')
        self.request_bindings[id]=record
        view=memoryview(data)
        while view:
            count=os.write(self.command_w,view);view=view[count:]
        return id

    def receive(self,timeout):
        if not self.queue:
            if not self.selector.select(timeout): return None
            chunk=os.read(self.event_r,4096)
            if not chunk:
                self.lifecycle.poisoned=True
                self.decoder.end()
                raise Blocked('SDK host EOF; task tools require reconciliation')
            try:self.queue.extend(self.decoder.feed(chunk))
            except Exception as exc:
                self.lifecycle.poisoned=True
                raise Blocked('malformed SDK record') from exc
        if not self.queue:return None
        record=self.queue.pop(0)
        try:validate_schema('host.schema.json',record)
        except Exception as exc:
            self.lifecycle.poisoned=True
            raise Blocked('invalid SDK envelope schema') from exc
        required={'protocol_version','host_id','run_id','nonce','sequence','command_id','operation_id','attempt_id','session_id','type','op','payload_schema','payload'}
        if (set(record)!=required or record['protocol_version']!=1 or record['payload_schema']!='sdk-v1' or
            any(record[k]!=v for k,v in self.binding.items()) or record['sequence']!=self.in_sequence+1):
            self.lifecycle.poisoned=True;raise Blocked('host envelope/sequence mismatch')
        self.in_sequence+=1
        command=self.request_bindings.get(record['command_id'])
        if not command or any(record[k]!=command[k] for k in ('operation_id','attempt_id','op')):
            self.lifecycle.poisoned=True;raise Blocked('host request correlation mismatch')
        if self.session_id is not None and record['session_id']!=self.session_id:
            self.lifecycle.poisoned=True;raise Blocked('host session mismatch')
        self.records.append(record)
        return record

    def wait_response(self,command,timeout):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            record=self.receive(min(.1,max(0,deadline-time.monotonic())))
            if record and record['command_id']==command and record['type']=='response':
                if record['payload'].get('ok') is not True:
                    self.lifecycle.poisoned=True
                    raise Blocked('SDK command failed; no replay: '+record['payload'].get('error','unknown'))
                return record['payload']
            if record and record['type']!='response':
                if record['type']=='lifecycle' and record['payload'].get('type')=='drained':
                    continue
                self.lifecycle.poisoned=True
                raise Blocked('unexpected lifecycle outside prompt')
        self.lifecycle.poisoned=True
        raise Blocked('SDK response deadline')

    @staticmethod
    def _tool_record_size(record):
        return len(json.dumps(record,ensure_ascii=False,separators=(',',':')).encode())

    def _tool_disposition(self, record, state, **details):
        p=record['payload']
        self._persist('sdk_tool_'+state+':'+digest(p['call']),
            {'state':state,'call_hash':digest(p['call']),'args_hash':digest(p['args']),
             'generation':p['generation'],'tool':p['tool'],'version':p['version'],**details},self.current['operation_id'])

    def _launch_tool(self,record):
        """Admit a same-prompt request; serialize effects, not workflow decisions."""
        self.failure_phase='tool_admission'
        p=record['payload'];call=p.get('call')
        if (not self.lifecycle.active or self.lifecycle.poisoned or record['command_id']!=self.current['command_id'] or
            any(record.get(k)!=v for k,v in self.binding.items()) or
            record.get('operation_id')!=self.current['operation_id'] or record.get('attempt_id')!=self.current['attempt_id'] or
            record.get('session_id')!=self.session_id or p.get('generation')!=self.lifecycle.generation):
            raise Blocked('tool outside current prompt')
        if not isinstance(call,str) or not call or len(call)>1024 or call in self.tool_calls_seen:
            raise Blocked('duplicate/invalid tool call identity')
        name=p.get('tool'); spec=next((t for t in self.manifest['tools'] if t['name']==name),None)
        if self.question_gate:
            raise Blocked('tool after question admission freeze')
        if name == 'request_owner_input':
            if not spec or spec['version'] != p.get('version') or self.interaction is None:
                raise Blocked('unregistered question tool')
            if self.pending or self.tool_queue:
                raise Blocked('question batch has unsettled task tools')
            # Replay IDs span the prompt; they are not the current batch's liveness.
            # A completed earlier tool is safe only with durable process quiescence.
            self.gateway.store.assert_dispatchable(self.gateway.run, admitted_host_ops=(self.host_op,))
            Draft202012Validator(spec['parameters']).validate(p['args'])
            binding = {**self.question_binding, 'session_id': self.session_id}
            result = self.interaction.request(self.current['operation_id'], call, binding, p['args'], batch=p.get('batch'))
            self.question_gate = result['gate_id']
            self.tool_calls_seen.add(call)
            self._tool_disposition(record, 'question_terminating')
            self.send('tool', {'generation': self.lifecycle.generation, 'call': call,
                'result': {'content': [{'type': 'text', 'text': canonical(result)}],
                           'details': result, 'terminate': True}})
            return
        tool=self.gateway.tools.get(name)
        if not spec or not tool or tool.version!=p.get('version') or spec['version']!=tool.version:
            raise Blocked('unregistered tool binding')
        if self.compatibility['role']=='review' and tool.owned_paths:
            raise Blocked('review tool mutation denied')
        try:
            Draft202012Validator(spec['parameters']).validate(p['args'])
        except ValidationError as exc:
            # Invalid arguments have no effect and are correctable in this turn.
            self.tool_calls_seen.add(call)
            output={'error':{'operation':name,'message':'invalid arguments ('+exc.validator+')',
                'correction':'use the declared tool schema and authorized paths, then continue'}}
            self.send('tool',{'generation':self.lifecycle.generation,'call':call,
                'result':{'content':[{'type':'text','text':canonical(output)}],
                          'details':{'operation_id':None,'quiescent':True}}})
            self._tool_disposition(record,'invalid_arguments')
            return
        size=self._tool_record_size(record)
        if self.queued_tool_bytes+size>MAX_RECORD:
            raise Blocked('task-tool queue byte limit; no request dropped or released')
        self.tool_calls_seen.add(call)
        self._tool_disposition(record,'queued')
        self.tool_queue.append(record);self.queued_tool_bytes+=size
        self._start_next_tool()

    def _start_next_tool(self):
        if self.pending or not self.tool_queue:return
        record=self.tool_queue.pop(0);self.queued_tool_bytes-=self._tool_record_size(record)
        p=record['payload'];tool=self.gateway.tools.get(p['tool'])
        spec=next((t for t in self.manifest['tools'] if t['name']==p['tool']),None)
        if (not tool or not spec or tool.version!=p['version'] or tool.arguments!=spec['parameters'] or
                self.compatibility['role']=='review' and tool.owned_paths):
            self._tool_disposition(record,'cancelled')
            raise Blocked('queued registered tool drift; renewal required')
        if tool.build_argv is None:
            # Scoped reads/searches have no child effect. Validate and return
            # their actual bounded result directly instead of spawning a no-op.
            self.gateway.admit_direct(tool.id,p['args'],admitted_host_ops=(self.host_op,))
            output=self.tool_output(tool,p['args'],{'admitted_host_ops':(self.host_op,)},0,None)
            self.send('tool',{'generation':self.lifecycle.generation,'call':p['call'],
                'result':{'content':[{'type':'text','text':canonical(output)}],
                          'details':{'operation_id':None,'quiescent':True}}})
            self._tool_disposition(record,'direct_settled')
            self._start_next_tool()
            return
        try:
            op,proc=self.gateway.launch(self.current['attempt_id']+':'+p['call'],tool.id,tool.version,p['args'],
                                        admitted_host_ops=(self.host_op,))
        except BaseException:
            self._tool_disposition(record,'launch_uncertain')
            raise
        self.pending[p['call']]={'op':op,'proc':proc,'tool':tool,'args':p['args']}
        self._tool_disposition(record,'launched',process_operation=op)

    @staticmethod
    def tool_output(tool, args, receipt, code, operation_id):
        """Return a correctable local tool error without poisoning a settled turn."""
        output = {'exit_code':code,'operation_id':operation_id}
        if tool.result_reader is not None:
            try:
                output['output'] = tool.result_reader(args, receipt)
            except (Blocked, OSError, UnicodeError, ValueError) as exc:
                output['error'] = {'operation':'tool result read','message':str(exc),
                                   'correction':'adjust the authorized path or arguments and continue'}
        if len(canonical(output).encode()) > 65536:
            return {'exit_code':code,'operation_id':operation_id,
                    'error':{'operation':'tool result read','message':'tool result exceeds consumer limit',
                             'correction':'request a smaller range and continue'}}
        return output

    def _poll_tools(self):
        for call,tool in list(self.pending.items()):
            code=tool['proc'].poll()
            if code is None:continue
            receipt=self.gateway.settle(tool['op'],code)
            if not receipt.get('replacement_allowed'):
                raise Blocked('ORPHAN_PROCESS: tool result cannot release prompt')
            output = self.tool_output(tool['tool'], tool['args'], receipt, code, tool['op'])
            self.send('tool',{'generation':self.lifecycle.generation,'call':call,
                'result':{'content':[{'type':'text','text':canonical(output)}],
                          'details':{'operation_id':tool['op'],'quiescent':True}}})
            del self.pending[call]
        self._start_next_tool()

    def _settle_prompt(self, payload):
        if self.pending or self.tool_queue or self.control_commands:
            raise Blocked('settlement with pending/queued task tools or unconfirmed control enqueue')
        self.lifecycle.finish(payload)

    def prompt(self,*,node,task_id,attempt_id,role,text,skill,contract_hash,selection,timeout=120,interrupt=None):
        if self.pending or self.tool_queue:raise Blocked('pending/queued task tools prevent a new prompt')
        self.gateway.store.assert_dispatchable(self.gateway.run,admitted_host_ops=(self.host_op,))
        family=lambda r:'implement' if r in ('implement','repair') else r
        if family(role)!=family(self.compatibility['role']):raise Blocked('session role isolation')
        before=self.snapshot
        if not before:raise Blocked('missing initial telemetry')
        generation=self.lifecycle.begin()
        self.tool_calls_seen.clear()
        self.question_gate = None
        details={'run_id':self.gateway.run,'task_id':task_id,'node_id':node,'role':role,
                 'host_op':self.host_op,'attempt_id':attempt_id,'contract_hash':contract_hash,
                 'generation':generation,'selection':selection,'compatibility':self.compatibility,'before':before,'started_ns':time.time_ns(),
                 'baseline_sha':git(self.gateway.authority.project,'rev-parse','HEAD').decode().strip(),
                 'result_sha':None,'result_sha_unknown_reason':'runner_checkpoint_not_yet_performed',
                 'check_evidence':[]}
        operation=self.gateway.store.intent(self.gateway.run,node,'sdk-turn',{'contract_hash':contract_hash},details)
        if operation['phase']!='intent':raise Blocked('uncertain prompt operation; no replay')
        self.current={'operation_id':operation['op_id'],'attempt_id':attempt_id}
        self.snapshot=None
        started=time.monotonic_ns()
        self.failure_phase='prompt_send'
        try:
            command=self.send('prompt',{'generation':generation,'text':text,'skill':skill})
            self.current['command_id']=command
            deadline=time.monotonic()+timeout
            while time.monotonic()<deadline:
                self.failure_phase='tool_poll'
                self._poll_tools()
                if interrupt and interrupt(self):raise Blocked('controlled pressure/pause')
                self.failure_phase='record_receive'
                record=self.receive(.05)
                if not record:continue
                if record['command_id']!=command:
                    if record['command_id'] in self.control_commands and record['type']=='response':
                        input_id=self.control_commands.pop(record['command_id'])
                        if record['payload'].get('ok') is not True or record['payload'].get('input_id')!=input_id or record['payload'].get('sdk_enqueued') is not True:
                            raise Blocked('SDK control enqueue not confirmed')
                        self.interaction.control_stage(input_id,'queued','sdk_delivered',
                            {'command_id':record['command_id'],'host_op':self.host_op,'session_id':self.session_id,'generation':generation})
                        self._flush_control_ack(input_id)
                        continue
                    if record['type']=='response' and record['payload'].get('ok') is True:continue
                    raise Blocked('interleaved operation mismatch')
                p=record['payload']
                if record['type']=='response':
                    if not p.get('ok'):raise Blocked('SDK prompt failed')
                    continue
                if record['type']=='tool_request':self._launch_tool(record);continue
                # Persist only allowlisted facts, never tool arguments, raw text/auth.
                safe={k:v for k,v in p.items() if k in ('type','generation','provider','model','wire_effort','mapping','request_sequence','reason','stop_reason','idle','promise_done','outgoing_tools','skill_expanded','expanded_prompt_hash')}
                self._persist('sdk:'+str(record['sequence']),safe,operation['op_id'])
                if record['type']=='lifecycle':
                    if p.get('type')=='control_acknowledged':
                        self.control_acknowledgements[p['input_id']]={k:p[k] for k in ('input_id','user_entry_id','assistant_entry_id')}
                        self._flush_control_ack(p['input_id'])
                    self.lifecycle.event(p)
                    if p.get('type') in ('pressure','compaction_start'):
                        raise Blocked('SDK context pressure/compaction; drain and owner recovery required')
                if record['type']=='settled':
                    self.failure_phase='settlement'
                    self._settle_prompt(p)
                    self.gateway.store.assert_dispatchable(self.gateway.run,admitted_host_ops=(self.host_op,))
                    self.snapshot=p['snapshot']
                    segment=usage_segment(before,self.snapshot)
                    retries=sum(1 for r in self.records if r['command_id']==command and r['payload'].get('type')=='auto_retry_start')
                    segment.update(details,ended_ns=time.time_ns(),elapsed_ns=time.monotonic_ns()-started,retry_count=retries,
                        request_observed=[r['payload'] for r in self.records if r['command_id']==command and r['type']=='request_observation'])
                    self.gateway.store.transition(operation['op_id'],'intent','completed',segment)
                    return {'snapshot':self.snapshot,'segment':segment,'output':p.get('output',''), 'question_gate': self.question_gate}
            raise Blocked('SDK prompt deadline')
        except BaseException as exc:
            self.lifecycle.poisoned=True
            diagnostic=failure_diagnostic(exc,phase=self.failure_phase,host_op=self.host_op,
                operation_id=operation['op_id'],pending=[tool['op'] for tool in self.pending.values()])
            diagnostic_recorded=True
            try:self._persist('sdk_failure_diagnostic',diagnostic,operation['op_id'])
            except Exception:diagnostic_recorded=False
            try:
                self.abort()
            except Exception:
                self._persist('sdk_drain_unknown',{'host_op':self.host_op,'reason':'host_or_sdk_drain_unavailable'},operation['op_id'])
            finally:
                segment=usage_segment(before,None,outcome='interrupted')
                segment.update(details,ended_ns=None,end_unknown_reason='prompt_or_host_interrupted',
                    stopped_observed_ns=time.time_ns(),elapsed_ns=time.monotonic_ns()-started)
                self._persist('sdk_interrupted',segment,operation['op_id'])
            raise Blocked('SDK turn interrupted/uncertain; no replay or reuse; cause='+diagnostic['classification']+
                          '; phase='+diagnostic['phase']+'; operation='+operation['op_id']+
                          '; diagnostic_recorded='+str(diagnostic_recorded).lower()) from exc

    def abort(self):
        self.lifecycle.poisoned=True
        cancellation_unrecorded=False
        for record in self.tool_queue:
            try:self._tool_disposition(record,'cancelled')
            except Exception:cancellation_unrecorded=True
        self.tool_queue.clear();self.queued_tool_bytes=0
        # Drain tools first: SDK abort alone does not quiesce child descendants.
        for call,tool in list(self.pending.items()):
            receipt=self.gateway.resolve(tool['op'])
            tool['proc'].wait(timeout=5)
            if not receipt.get('replacement_allowed'):raise Blocked('task drain unknown')
            del self.pending[call]
        command=self.send('abort',{'generation':self.lifecycle.generation})
        deadline=time.monotonic()+15
        while time.monotonic()<deadline:
            record=self.receive(.1)
            if record and record['command_id']==command and record['type']=='response':
                if not record['payload'].get('ok') or not record['payload'].get('idle'):raise Blocked('SDK drain unknown')
                self.lifecycle.active=False
                self._persist('sdk_drained',{'host_op':self.host_op,'idle':True,'tools_empty':True})
                if cancellation_unrecorded:raise Blocked('queued cancellation receipt unavailable; no reuse')
                return
        raise Blocked('SDK abort deadline; custody unresolved')

    def enqueue_control(self, value):
        if (self.interaction is None or self.question_gate or not self.lifecycle.active or self.lifecycle.poisoned or
                value['binding']['session_id']!=self.session_id or value['binding']['role']!=self.compatibility['role']):
            raise Blocked('control target no longer active; no retarget')
        self.interaction.control_stage(value['input_id'],'received','queued')
        command=self.send(value['action'],{k:value[k] for k in ('input_id','binding','message')})
        self.control_commands[command]=value['input_id']
        return command

    def _flush_control_ack(self, input_id):
        receipt=self.control_acknowledgements.get(input_id)
        if not receipt:return
        row=self.gateway.store.db.execute('SELECT stage FROM wf_owner_inputs WHERE input_id=? AND run_id=?',(input_id,self.gateway.run)).fetchone()
        if row and row['stage']=='sdk_delivered':
            self.interaction.control_stage(input_id,'sdk_delivered','worker_acknowledged',
                {**receipt,'host_op':self.host_op,'session_id':self.session_id})
            self.control_acknowledgements.pop(input_id,None)

    def deliver_answer(self, value):
        if ('open' not in self.manifest or value['binding']['session_id'] != self.session_id or
                value['binding']['role'] != self.compatibility['role'] or self.lifecycle.active or
                self.lifecycle.poisoned or self.pending or self.tool_queue):
            raise Blocked('answer requires exact reopened original idle role/conversation')
        command = self.send('owner_answer', {k: value[k] for k in ('input_id','answer','binding')},
                            operation_id=self.host_op, attempt_id='owner-answer:'+value['input_id'])
        receipt = self.wait_response(command, 10)['receipt']
        if receipt['input_id'] != value['input_id'] or receipt['session_id'] != self.session_id:
            raise Blocked('answer original entry identity mismatch')
        self.snapshot = receipt['snapshot']
        self._persist('host_answer_entry', receipt, self.host_op)
        return receipt

    def telemetry(self):
        if self.lifecycle.active or self.lifecycle.poisoned or self.pending or self.tool_queue:raise Blocked('telemetry not settled')
        command=self.send('telemetry',{'generation':self.lifecycle.generation},operation_id=self.host_op,attempt_id='telemetry')
        self.snapshot=self.wait_response(command,10)['snapshot']
        return self.snapshot

    def close(self,force=False):
        if self.closed:return
        try:
            if (self.lifecycle.active or self.pending or self.tool_queue) and self.proc.poll() is None:self.abort()
            if not force:
                command=self.send('close',{'generation':self.lifecycle.generation},operation_id=self.host_op,attempt_id='close')
                self.wait_response(command,10)
                # Node's pipe read may occupy an fs thread; EOF is required even
                # after close ACK so SDK/native shutdown cannot wait on our writer.
                os.close(self.command_w);self.command_w=-1
                self.proc.wait(timeout=10)
                self.gateway.settle(self.host_op,self.proc.returncode)
            else:
                # Only T001 validated own-child drain, never PID-only kill.
                self.gateway.resolve(self.host_op)
                self.proc.wait(timeout=10)
        except BaseException:
            self.lifecycle.poisoned=True
            self.gateway.resolve(self.host_op)
            self.proc.wait(timeout=10)
            raise
        finally:
            self.closed=True
            if self.command_w>=0:os.close(self.command_w)
            os.close(self.event_r)
            if hasattr(self,'selector'):self.selector.close()
