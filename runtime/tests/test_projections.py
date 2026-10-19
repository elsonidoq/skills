"""T004/V3 actual SQL/file/read-only-process projection recovery."""
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from coherence_workflow.projections import Publisher, latest_metrics, records, state_record
from coherence_workflow.registry import validate_schema
from coherence_workflow.store import Authority, Blocked, canonical, digest
from fixtures.support import make_project


class ProjectionRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.project=make_project(self.root/'project')
        self.owner=Authority(self.project);self.addCleanup(self.owner.close)
        self.owner.store.reserve('run',digest('config'))
        self.owner.store.register_controller('run')
        op=self.owner.store.intent('run','code','graph',{},{});self.owner.store.transition(op['op_id'],'intent','completed',{'outcome':'ok'})
        self.owner.store.settle_controller('run','interrupted')

    def test_real_torn_tail_append_before_cursor_dedup_and_nontail_block(self):
        publisher=Publisher(self.owner,'run');state=publisher.publish()
        self.assertEqual(state['payload']['status'],'interrupted')
        events=publisher.root/'events.jsonl';original=events.read_bytes()
        with events.open('ab') as out:out.write(b'{torn')
        publisher.publish();self.assertEqual(events.read_bytes(),original)
        self.assertEqual(len(list(publisher.root.glob('events.jsonl.torn-*'))),1)
        with self.owner.store.transaction() as db:self.owner.store.event(db,'run',None,'new_fact',{'value':1})
        before=self.owner.store.db.execute('SELECT seq FROM wf_projections').fetchone()[0]
        def crash(phase,name):
            if phase=='appended' and name=='events.jsonl':raise RuntimeError('append-before-cursor crash')
        with self.assertRaises(RuntimeError):publisher.publish(crash)
        self.assertEqual(self.owner.store.db.execute('SELECT seq FROM wf_projections').fetchone()[0],before)
        appended=events.read_bytes();publisher.publish();self.assertEqual(events.read_bytes(),appended)
        events.write_bytes(events.read_bytes().replace(b'event-digest.v1',b'bad-digest.v1',1))
        with self.assertRaisesRegex(Blocked,'non-tail projection mismatch'):publisher.publish()
        print('projection SQL events',self.owner.store.db.execute('SELECT COUNT(*) FROM wf_events').fetchone()[0])

    def test_separate_status_process_no_agents_or_projection_mutations(self):
        publisher=Publisher(self.owner,'run');publisher.publish()
        before={p.name:p.read_bytes() for p in publisher.root.iterdir()}
        root=Path(__file__).resolve().parents[2]
        command=[str(root/'scripts/coordinate-implementation'),'status','--project',str(self.project),'--run','run']
        result=subprocess.run(command,env=dict(os.environ,COHERENCE_PYTHON=sys.executable,COHERENCE_AUTH_PATH='/unavailable',COHERENCE_CATALOG_PATH='/unavailable'),capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        output=json.loads(result.stdout);self.assertEqual(output['state'],'interrupted');self.assertFalse(output['accepted'])
        validate_schema('projection.schema.json',output['projection'])
        self.assertEqual(before,{p.name:p.read_bytes() for p in publisher.root.iterdir()})
        print('separate status',result.returncode,output['state'],output['projection']['seq'])

    def test_metric_revisions_supersede_not_double_count_and_nonagent_nulls(self):
        store=self.owner.store
        segment={'task_id':'A','attempt_id':'A:0','node_id':'implement','role':'implement','outcome':'settled',
            'before':{'session_id':'fixture-session','requested':None,'counters':{'input':0},'occupancy':0},
            'after':{'occupancy':3},'tokens':{key:{'value':0,'unknown_reason':None} for key in ('input','output','cacheRead','cacheWrite')},
            'selection':{'reason':'fixture-only','session_id':None},'elapsed_ns':1,'started_ns':1,'ended_ns':2}
        op=store.intent('run','agent','sdk-turn',{},{});store.transition(op['op_id'],'intent','completed',segment)
        store.db.execute('CREATE TABLE wf_checks(evidence_id TEXT,run_id TEXT,task_id TEXT)')
        with store.transaction() as db:store.event(db,'run',None,'task_checkpointed',{'task_id':'A','sha':'fixture-sha'})
        _,metrics=records(store.db,'run')
        self.assertEqual(len(metrics),3)
        current=latest_metrics(metrics);self.assertEqual(len(current),2)
        agent=next(r for r in current if r['payload']['role']=='implement')
        self.assertEqual(agent['payload']['cache_read_tokens']['value'],0)
        self.assertEqual(agent['payload']['result_sha'],'fixture-sha')
        code=next(r for r in current if r['payload']['role']=='code')
        self.assertIsNone(code['payload']['session_id']);self.assertIsNone(code['payload']['input_tokens']['value'])
        self.assertIsNotNone(code['payload']['input_tokens']['unknown_reason'])
