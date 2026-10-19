"""Versioned SQL-derived projections. Never used for workflow decisions."""
import json
import os
from pathlib import Path
import sqlite3
import uuid

from .containment import validate_process
from .registry import validate_schema
from .store import Blocked, canonical, digest, private_file, safe_path


def alarm_record(db, row, *, historical=False):
    operation = db.execute('SELECT * FROM wf_operations WHERE op_id=?',(row['op_id'],)).fetchone()
    process = db.execute('SELECT * FROM wf_processes WHERE op_id=?',(row['op_id'],)).fetchone()
    return {'alarm_id':row['alarm_id'],'kind':'ORPHAN_PROCESS','task_id':operation['node_id'],
        'operation_id':row['op_id'],'scope_kind':'task_tools','scope_ref':process['name'],
        'identity_hash':digest(json.loads(process['containment'])),'state':'active' if historical else row['state'],
        'replacement_allowed':False if historical or row['state']=='active' else True,
        'reconciliation_ref':None if historical or row['state']=='active' else row['alarm_id']+':resolution'}


def state_record(db, run):
    row=db.execute('SELECT * FROM wf_runs WHERE run_id=?',(run,)).fetchone()
    if not row:raise Blocked('unknown run')
    seq=db.execute('SELECT COALESCE(MAX(seq),0) FROM wf_events WHERE run_id=?',(run,)).fetchone()[0]
    controller=db.execute('SELECT * FROM wf_controllers WHERE run_id=?',(run,)).fetchone()
    active=False
    if controller and controller['phase']=='active':
        identity=json.loads(controller['identity'])
        try:validate_process(identity,identity['nonce']);active=True
        except Blocked:pass
    alarms=[alarm_record(db,r) for r in db.execute('SELECT a.* FROM wf_alarms a JOIN wf_operations o USING(op_id) WHERE o.run_id=?',(run,))]
    complete=db.execute("SELECT 1 FROM wf_events WHERE run_id=? AND kind='implementation_complete'",(run,)).fetchone()
    accepted=db.execute("SELECT seq,payload FROM wf_events WHERE run_id=? AND kind='workflow_accepted' ORDER BY seq DESC LIMIT 1",(run,)).fetchone()
    blocked=db.execute("SELECT seq,payload FROM wf_events WHERE run_id=? AND kind='workflow_blocked' ORDER BY seq DESC LIMIT 1",(run,)).fetchone()
    accepted_current=bool(accepted and (not blocked or accepted['seq']>blocked['seq']))
    status=('blocked' if any(a['state']=='active' for a in alarms) else 'accepted' if accepted_current else
            ('final_failure' if json.loads(blocked['payload']).get('final_failure') else 'blocked') if blocked else
            'implementation_complete' if complete and not active else row['state'] if active else 'interrupted')
    active_op=db.execute("""SELECT o.* FROM wf_operations o JOIN wf_events e ON e.op_id=o.op_id AND e.kind='intent'
        WHERE o.run_id=? AND o.phase!='completed' ORDER BY e.seq DESC LIMIT 1""",(run,)).fetchone()
    active_details=json.loads(active_op['intent']) if active_op else {}
    task=None; checkpoint=None;gate=None
    if db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_tasks'").fetchone():
        task=db.execute("SELECT * FROM wf_tasks WHERE run_id=? AND state NOT IN ('checkpointed','read_only_complete') ORDER BY approved_order LIMIT 1",(run,)).fetchone()
        last=db.execute('SELECT checkpoint FROM wf_tasks WHERE run_id=? AND checkpoint IS NOT NULL ORDER BY approved_order DESC LIMIT 1',(run,)).fetchone()
        checkpoint=json.loads(last[0])['sha'] if last else None
    if db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_gates'").fetchone():
        pending=db.execute("SELECT gate_id FROM wf_gates WHERE run_id=? AND state!='approve' LIMIT 1",(run,)).fetchone();gate=pending[0] if pending else None
    finding_blocked=False
    if db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_findings'").fetchone():
        finding_blocked=bool(db.execute("SELECT 1 FROM wf_findings f JOIN wf_reviews r USING(review_id) WHERE r.run_id=? AND f.disposition!='resolved' LIMIT 1",(run,)).fetchone())
    if gate or finding_blocked:
        accepted_current=False;status='blocked'
    blocker=('ORPHAN_PROCESS' if any(a['state']=='active' for a in alarms) else 'unmet original manual gate' if gate else
             'unresolved review findings' if finding_blocked else None if accepted_current else
             json.loads(blocked['payload'])['reason'] if blocked else 'independent review required' if complete else
             'controller not live; explicit authorized recovery required' if not active else None)
    if db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_questions'").fetchone():
        question=db.execute("SELECT gate_id,stage FROM wf_questions WHERE run_id=? AND stage NOT IN ('continued','cancelled') ORDER BY rowid DESC LIMIT 1",(run,)).fetchone()
        if question and not any(a['state']=='active' for a in alarms):
            gate=question['gate_id'];accepted_current=False
            status='waiting_owner_input' if question['stage'] in ('pending','answered') else 'blocked'
            blocker='owner answer pending' if question['stage']=='pending' else 'original answer accepted; explicit original continuation required' if question['stage']=='answered' else 'question/delivery reconciliation required; no replay'
    if row['state'] in ('paused','cancelled') and not any(a['state']=='active' for a in alarms):
        accepted_current=False;status=row['state'];blocker='owner '+row['state']+'; partial work retained'
    cursor=0
    if db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_projections'").fetchone():
        c=db.execute('SELECT seq FROM wf_projections WHERE run_id=?',(run,)).fetchone();cursor=c[0] if c else 0
    payload={'status':status,'acceptance':'accepted' if accepted_current and status=='accepted' else 'blocked','config_hash':row['config_hash'],'checkpoint_ref':checkpoint,
        'task_id':task['task_id'] if task else None,'node_id':active_op['node_id'] if active_op else None,
        'attempt_id':active_details.get('attempt_id'),'gate_ref':gate,
        'blocker':blocker,
        'projection_lag':max(0,seq-cursor),'alarms':alarms}
    if status=='waiting_owner_input':payload['pending_question_ref']=gate
    record={'schema_version':1,'run_id':run,'seq':seq,'record_id':run+':state:'+str(seq),
            'timestamp':'unknown:event-timestamps-not-recorded','kind':'state','payload':payload}
    validate_schema('projection.schema.json',record)
    return record


def observation(value, source, reason='unavailable'):
    return {'value':value,'source':source,'unknown_reason':None if value is not None else reason}


def metric_record(event, operation, segment):
    before,after=segment.get('before') or {},segment.get('after') or {}
    agent=operation['kind']=='sdk-turn'
    profile=before.get('requested') if agent else None
    if profile is not None and not all(k in profile for k in ('provider','model','effort','observer_id','observer_version')):profile=None
    runtime=before.get('runtime')
    binding=lambda value: {'provider':value.get('provider'),'model':value.get('model'),'effort':value.get('effort'),
                           'source':'sdk-runtime','mapping_version':'1'} if value else None
    requests=segment.get('request_observed',[])
    request=requests[-1] if requests else None
    payload={'task_id':segment.get('task_id',operation['node_id']),'attempt_id':segment.get('attempt_id',operation['op_id']),
        'node_id':segment.get('node_id',operation['node_id']),'role':segment.get('role','code') if agent else 'code',
        'requested_profile':profile,'observed_runtime':binding(runtime) if agent else None,
        'observed_request':{'provider':request.get('provider'),'model':request.get('model'),'effort':request.get('wire_effort'),
                            'source':'final-payload','mapping_version':request.get('mapping')} if request else None,
        'provider_acknowledged':None,'skill_requested':None,'skill_observed':None,
        'session_id':before.get('session_id') if agent else None,'context_group':segment.get('compatibility',{}).get('affinity'),
        'reused':bool(segment.get('selection',{}).get('session_id')) if agent else None,
        'selection_reason':segment.get('selection',{}).get('reason','non_agent_node'),
        'started_at':str(segment['started_ns']) if segment.get('started_ns') else None,
        'ended_at':str(segment['ended_ns']) if segment.get('ended_ns') else None,
        'elapsed_ms':segment['elapsed_ns']/1e6 if segment.get('elapsed_ns') is not None else None,
        'outcome':segment.get('outcome','audited') if agent else 'audited', 'retry_count':segment.get('retry_count',0),'repair_count':segment.get('selection',{}).get('repair_count',0),
        'evidence_refs':[],'baseline_sha':segment.get('baseline_sha'),'result_sha':segment.get('result_sha'),
        'telemetry_provenance':'sdk-segment' if agent else 'non_agent_node',
        'unknown_reasons':{'provider_acknowledged':'not_available','requested_profile':'not_retained_in_segment',
                           'skill_requested':'not_retained_in_segment','skill_observed':'not_retained_in_segment',
                           'result_sha':'checkpoint_not_attributed_to_segment'},'supersedes':None}
    if agent:
        skills=before.get('skills',[])
        payload['skill_requested']=skills[0]['name'] if len(skills)==1 else None
        payload['skill_observed']=payload['skill_requested'] if requests and all(r.get('skill_expanded') for r in requests) else None
        for key in ('requested_profile','skill_requested','skill_observed','result_sha'):
            if payload[key] is not None:payload['unknown_reasons'].pop(key,None)
    for key,token in [('input_tokens','input'),('output_tokens','output'),('cache_read_tokens','cacheRead'),('cache_write_tokens','cacheWrite')]:
        value=segment.get('tokens',{}).get(token,{})
        payload[key]=observation(value.get('value'),'sdk-counter-delta' if agent else 'non_agent_node',value.get('unknown_reason') or 'non_agent_node')
    for label,source in [('start',before),('end',after)]:
        for field,key in [('context','occupancy'),('threshold','threshold'),('headroom','headroom')]:
            payload[field+'_'+label]=observation(source.get(key) if agent else None,'sdk-telemetry' if agent else 'non_agent_node')
    return {'schema_version':1,'run_id':event['run_id'],'seq':event['seq'],'record_id':event['event_id']+':metric',
            'timestamp':'unknown:event-timestamps-not-recorded','kind':'metric','payload':payload}


def records(db,run):
    events=[];metrics=[]
    for row in db.execute('SELECT * FROM wf_events WHERE run_id=? ORDER BY seq',(run,)):
        details={'payload_hash':digest(json.loads(row['payload']))};schema='event-digest.v1'
        if row['kind']=='ORPHAN_PROCESS':
            alarm=db.execute('SELECT * FROM wf_alarms WHERE original_seq=?',(row['seq'],)).fetchone()
            if not alarm:raise Blocked('missing original alarm projection proof')
            details=alarm_record(db,alarm,historical=True);schema='alarm.v1'
        event={'schema_version':1,'run_id':run,'seq':row['seq'],'record_id':row['event_id'],
            'timestamp':'unknown:event-timestamps-not-recorded','kind':'event',
            'payload':{'kind':row['kind'],'operation_ref':row['op_id'],'attempt_ref':None,'details_schema':schema,'details':details}}
        validate_schema('projection.schema.json',event);events.append(event)
        if row['op_id'] and row['kind'] in ('completed','sdk_interrupted'):
            op=db.execute('SELECT * FROM wf_operations WHERE op_id=?',(row['op_id'],)).fetchone()
            if op['kind'] in ('sdk-turn','graph'):
                metric=metric_record(row,op,json.loads(row['payload']))
                validate_schema('projection.schema.json',metric);metrics.append(metric)
        if row['kind']=='task_checkpointed':
            checkpoint=json.loads(row['payload'])
            for op in db.execute("""SELECT o.* FROM wf_operations o JOIN wf_events e ON e.op_id=o.op_id AND e.kind='completed'
                WHERE o.run_id=? AND o.kind='sdk-turn' AND o.phase='completed' ORDER BY e.seq""",(run,)):
                segment=json.loads(op['result'])
                if segment.get('task_id')!=checkpoint['task_id']:continue
                source=db.execute("SELECT * FROM wf_events WHERE op_id=? AND kind='completed' AND seq<?",(op['op_id'],row['seq'])).fetchone()
                if not source:continue
                segment['result_sha']=checkpoint['sha']
                metric=metric_record(row,op,segment)
                metric['record_id']=row['event_id']+':'+op['op_id']+':metric'
                metric['payload']['supersedes']=source['event_id']+':metric'
                known={r[0] for r in db.execute('SELECT evidence_id FROM wf_checks WHERE run_id=? AND task_id=?',(run,checkpoint['task_id']))}
                metric['payload']['evidence_refs']=[payload['evidence_id'] for event in db.execute(
                    "SELECT payload FROM wf_events WHERE run_id=? AND kind='check_observed' AND seq<? ORDER BY seq",(run,row['seq']))
                    if (payload:=json.loads(event[0])).get('evidence_id') in known]
                validate_schema('projection.schema.json',metric);metrics.append(metric)
    return events,metrics


def latest_metrics(records):
    by_id={r['record_id']:r for r in records}
    superseded={r['payload']['supersedes'] for r in records if r['payload']['supersedes']}
    return [r for id,r in by_id.items() if id not in superseded]


class Publisher:
    def __init__(self,authority,run):
        self.authority,self.store,self.run=authority,authority.store,run
        self.root=safe_path(authority.project,'.coherence/workflow/runs/'+run)
        self.root.mkdir(parents=True,mode=0o700,exist_ok=True)
        self.store.db.execute('CREATE TABLE IF NOT EXISTS wf_projections(run_id TEXT PRIMARY KEY REFERENCES wf_runs,seq INTEGER NOT NULL)')

    def _append(self,name,expected,hook):
        path=safe_path(self.root,name)
        if not path.exists():
            fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_WRONLY,0o600);os.close(fd)
        private_file(path)
        data=path.read_bytes();complete=data.rsplit(b'\n',1)[0]+b'\n' if b'\n' in data else b''
        tail=data[len(complete):]
        if tail:
            archive=self.root/(name+'.torn-'+uuid.uuid4().hex)
            fd=os.open(archive,os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_WRONLY,0o600)
            with os.fdopen(fd,'wb') as out:out.write(tail);out.flush();os.fsync(out.fileno())
            with path.open('r+b') as out:out.truncate(len(complete));out.flush();os.fsync(out.fileno())
        lines=complete.splitlines(keepends=True)
        wanted=[(canonical(record)+'\n').encode() for record in expected]
        if lines!=wanted[:len(lines)] or len(lines)>len(wanted):
            raise Blocked('non-tail projection mismatch; explicit rebuild required')
        with path.open('ab') as out:
            for line in wanted[len(lines):]:out.write(line)
            out.flush();os.fsync(out.fileno())
        hook('appended',name)

    def publish(self,phase_hook=None):
        self.authority.assert_held();hook=phase_hook or (lambda phase,name:None)
        events,metrics=records(self.store.db,self.run)
        self._append('events.jsonl',events,hook);self._append('metrics.jsonl',metrics,hook)
        state=state_record(self.store.db,self.run);state['payload']['projection_lag']=0
        tmp=self.root/('state-'+uuid.uuid4().hex+'.tmp')
        fd=os.open(tmp,os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_WRONLY,0o600)
        with os.fdopen(fd,'w') as out:out.write(canonical(state)+'\n');out.flush();os.fsync(out.fileno())
        os.replace(tmp,self.root/'state.json')
        fd=os.open(self.root,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(fd)
        finally:os.close(fd)
        hook('state_published','state.json')
        with self.store.transaction() as db:
            db.execute('INSERT INTO wf_projections VALUES(?,?) ON CONFLICT(run_id) DO UPDATE SET seq=excluded.seq',(self.run,state['seq']))
        return state
