"""T006/V3: actual CLI input/SDK enqueue/public ACK and owned-scope pause.

SQL-only negatives are explicitly fixtures; live cases require the approved SDK
and delegated cgroup capability. No stopped-worker ACK is synthesized.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time

from coherence_workflow.cli import ROOT
from coherence_workflow.interaction import Interaction
from coherence_workflow.pi_adapter import PiAdapter
from coherence_workflow.store import Authority, Blocked, canonical, digest
from coherence_workflow.tools import ProcessTool
from test_custody import IsolatedCustody
from test_interaction import binding, seeded_pending, standing_authority
from test_pi_adapter import manifest, environment
from test_review_repair import coordinate_fixture


def control_value(bound, action, input_id, *, active=True):
    return {'schema_version':1,'kind':'owner_control','binding':bound,'input_id':input_id,'action':action,
            'scope':'within_envelope','message':'Acknowledge this isolated receipt only; no scope change.',
            'owner_authority_ref':'standing-isolated-test-authority','stage':'received','evidence_ref':None,
            'target_scope':'active_session' if active else 'run'}


def control_manifest(project):
    config=manifest(project)
    skill=Path(config['skills'][0]['path'])
    skill.write_text('---\nname: bounded-proof\ndescription: Bounded authorized control test.\n---\n'
                     'Follow the explicit fixture mode requested in the current test prompt exactly, including hang for the pause test. '
                     'Use only the registered fixture tool and no other tool. Do not ask routine technical/test questions. '
                     'When bound control messages request an observable CONTROL_ACK token, include that exact token in public output; it is receipt only, not compliance.\n')
    config['skills'][0]['sha256']=hashlib.sha256(skill.read_bytes()).hexdigest()
    config['resource_hash']=digest({k:config[k] for k in ('skills','tools','permissions','trust','system_prompt')})
    return config


class ControlDeliveryTests(IsolatedCustody):
    def submit_cli(self, value):
        incoming=self.root/(value['input_id']+'.json');incoming.write_text(canonical(value))
        authority=self.root/(value['input_id']+'-authority.json')
        authority.write_text(canonical({'input_hash':digest(value),'scope':'within_envelope','authority_ref':value['owner_authority_ref']}));authority.chmod(0o600)
        result=subprocess.run([str(ROOT/'scripts/coordinate-implementation'),'control','--project',str(self.project),'--run','run',
            '--input',str(incoming),'--input-authority',str(authority)],env=dict(os.environ,COHERENCE_PYTHON=sys.executable),
            capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        return json.loads(result.stdout)

    def capture_all(self, owner):
        for row in owner.store.db.execute('SELECT containment FROM wf_processes WHERE containment IS NOT NULL'):
            receipt=json.loads(row[0])
            if receipt not in self.receipts:self.receipts.append(receipt)

    def test_live_cli_plain_steer_followup_enqueue_and_actual_public_ack_are_distinct(self):
        self.assertEqual(os.environ.get('COHERENCE_LIVE'),'1','NOT VERIFIED: actual SDK control test not enabled')
        with Authority(self.project) as owner:
            coordinate=coordinate_fixture(self.project,owner)
            coordinate.publish_run_binding();coordinate.select({})
            config=control_manifest(self.project)
            from fixtures.custody_support import process_tool
            prototype=process_tool(self.project)
            coordinate.gateway.tools={'fixture':ProcessTool('fixture','1',prototype.arguments,
                lambda args:[str(Path(sys.executable).resolve()),'-c','import time;time.sleep(3)'],(),environment())}
            adapter=PiAdapter(coordinate.gateway,config,node='control-host',environment=environment(),
                session_context={'role':'implement','affinity':'story','review_lineage':None},interaction=coordinate.interaction)
            bound={**binding(adapter.session_id),'task_id':'A','attempt_id':'A:0','config_hash':digest(coordinate.config),
                   'source_hash':digest(coordinate.contract['sources']),'approval_hash':digest(coordinate.contract['approval_refs']),
                   'task_hash':digest(coordinate.contract['tasks'][0])}
            with owner.store.transaction() as db:db.execute('INSERT INTO wf_active_targets VALUES(?,?)',('run',canonical(bound)))
            submitted=[]
            def poll(current):
                if current.pending and not submitted:
                    for action in ('steer','follow_up'):
                        value=control_value(bound,action,'live-'+action)
                        receipt=self.submit_cli(value);submitted.append(value['input_id'])
                        self.assertEqual(receipt['stage'],'received')
                    # Actual CLI inputs persisted while this process holds the
                    # exclusive execution lock. No facade selected a new target.
                return coordinate.controls_boundary(current)
            try:
                turn=adapter.prompt(node='control-turn',task_id='A',attempt_id='A:0',role='implement',
                    text='Invoke fixture once with mode quick and exit 0, then reply briefly. Observe any bound control messages and acknowledge their exact CONTROL_ACK identifiers in public output.',
                    skill='bounded-proof',contract_hash=digest('control'),selection={'reason':'isolated-live'},interrupt=poll)
                print(canonical({'diagnostic':'public-control-output','output':turn['output'],'snapshot_session':turn['snapshot']['session_id']}))
                self.assertEqual(len(submitted),2)
                rows=[dict(r) for r in owner.store.db.execute('SELECT input_id,stage,receipt FROM wf_owner_inputs ORDER BY rowid')]
                self.assertEqual([r['stage'] for r in rows],['worker_acknowledged','worker_acknowledged'])
                events=[dict(r) for r in owner.store.db.execute("SELECT seq,kind,payload FROM wf_events WHERE kind LIKE 'control_%' ORDER BY seq")]
                for id in submitted:
                    stages=[e for e in events if json.loads(e['payload']).get('input_id')==id]
                    self.assertEqual([s['kind'] for s in stages],['control_received','control_queued','control_sdk_delivered','control_worker_acknowledged'])
                    receipt=json.loads(rows[submitted.index(id)]['receipt'])
                    self.assertTrue(receipt['user_entry_id'] and receipt['assistant_entry_id'])
                observations=turn['segment']['request_observed']
                self.assertGreaterEqual(len(observations),2)
                self.assertTrue(all(r['skill_expanded'] for r in observations),'plain controls broke current-generation skill delivery')
                print(canonical({'item':'T006/V3','scope':'actual CLI/SDK plain steer+followUp/public ACK; not semantic compliance',
                                 'events':events,'original_session':adapter.session_id,'controls':rows}))
            finally:
                adapter.close(force=adapter.lifecycle.poisoned)
                self.capture_all(owner)

    def test_live_active_tool_pause_drains_cgroup_and_reconciles_partial_files_without_worker_ack(self):
        self.assertEqual(os.environ.get('COHERENCE_LIVE'),'1','NOT VERIFIED: actual SDK pause test not enabled')
        with Authority(self.project) as owner:
            coordinate=coordinate_fixture(self.project,owner)
            coordinate.publish_run_binding();coordinate.select({})
            from fixtures.custody_support import process_tool
            coordinate.gateway.tools={'fixture':process_tool(self.project)}
            config=control_manifest(self.project)
            adapter=PiAdapter(coordinate.gateway,config,node='pause-host',environment=environment(),
                session_context={'role':'implement','affinity':'story','review_lineage':None},interaction=coordinate.interaction)
            bound={**binding(adapter.session_id),'task_id':'A','attempt_id':'A:0','config_hash':digest(coordinate.config),
                   'source_hash':digest(coordinate.contract['sources']),'approval_hash':digest(coordinate.contract['approval_refs']),
                   'task_hash':digest(coordinate.contract['tasks'][0])}
            with owner.store.transaction() as db:db.execute('INSERT INTO wf_active_targets VALUES(?,?)',('run',canonical(bound)))
            submitted=[]
            def poll(current):
                if current.pending and self.project.joinpath('owned.txt').read_text()!='base' and not submitted:
                    value=control_value(bound,'pause','live-pause')
                    self.submit_cli(value);submitted.append(value)
                return coordinate.controls_boundary(current)
            try:
                with self.assertRaisesRegex(Blocked,'interrupted/uncertain'):
                    adapter.prompt(node='pause-turn',task_id='A',attempt_id='A:0',role='implement',
                        text='For the isolated pause test, invoke fixture exactly once with mode hang and exit 0. Do not call anything else.',
                        skill='bounded-proof',contract_hash=digest('pause'),selection={'reason':'isolated-live'},interrupt=poll)
            finally:
                adapter.close(force=True);self.capture_all(owner)
            self.assertEqual(len(submitted),1)
            coordinate.finish_stop(submitted[0])
            row=owner.store.db.execute('SELECT * FROM wf_owner_inputs WHERE input_id=?',('live-pause',)).fetchone()
            self.assertEqual(row['stage'],'reconciled')
            evidence=json.loads(row['receipt'])
            self.assertFalse(evidence['worker_acknowledged'])
            self.assertTrue(evidence['scopes'] and all(r['populated']==0 for r in evidence['scopes']))
            self.assertNotEqual(self.project.joinpath('owned.txt').read_text(),'base')
            self.assertEqual(owner.store.db.execute('SELECT state FROM wf_runs').fetchone()[0],'paused')
            self.assertEqual(owner.store.db.execute("SELECT COUNT(*) FROM wf_operations WHERE kind='git-checkpoint'").fetchone()[0],0)
            print(canonical({'item':'T006/V3','scope':'actual active process pause','evidence':evidence,'partial_files_retained':True}))

    def test_standalone_idle_cli_applies_inquiry_pause_cancel_without_agent_or_polling(self):
        from coherence_workflow.cli import status
        with Authority(self.project) as owner:
            coordinate=coordinate_fixture(self.project,owner)
            run_binding=coordinate.publish_run_binding()
        for action in ('inquire','pause','cancel'):
            value=control_value(run_binding,action,'standalone-'+action,active=False)
            result=self.submit_cli(value)
            self.assertNotEqual(result['stage'],'worker_acknowledged')
            self.assertIsNotNone(result['receipt'])
            if action!='inquire':
                self.assertEqual(result['stage'],'reconciled')
                self.assertEqual(status(self.project,'run')['state'],'paused' if action=='pause' else 'cancelled')
        with Authority(self.project) as owner:
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_active_targets').fetchone()[0],0)

    def test_idle_inquiry_pause_cancel_have_no_worker_identity_or_ack(self):
        for action in ('inquire','pause','cancel'):
            with self.subTest(action=action),Authority(self.project) as owner:
                if not owner.store.db.execute('SELECT 1 FROM wf_runs').fetchone():
                    coordinate=coordinate_fixture(self.project,owner)
                    run_binding=coordinate.publish_run_binding()
                else:
                    # Reuse only the same harmless run fixture; this test exercises
                    # independent run-scoped controls, not workflow dispatch.
                    coordinate=coordinate_fixture(self.project,owner)
                    run_binding=coordinate.publish_run_binding()
                    with owner.store.transaction() as db:db.execute("UPDATE wf_runs SET state='running'")
                value=control_value(run_binding,action,'idle-'+action,active=False)
                receipt=self.submit_cli(value)
                self.assertEqual(receipt['stage'],'received')
                if action=='inquire':coordinate.controls_boundary()
                else:
                    with self.assertRaisesRegex(Blocked,'no worker ACK'):coordinate.controls_boundary()
                row=owner.store.db.execute('SELECT * FROM wf_owner_inputs WHERE input_id=?',(value['input_id'],)).fetchone()
                self.assertNotEqual(row['stage'],'worker_acknowledged')
                self.assertTrue(all(value['binding'][k] is None for k in ('task_id','attempt_id','node_id','session_id','role','task_hash')))

    def test_wrong_stale_scope_duplicate_and_pending_pin_controls_never_retarget(self):
        with Authority(self.project) as owner:
            ledger,answer=seeded_pending(owner)
            bound=answer['binding']
            with owner.store.transaction() as db:db.execute('INSERT INTO wf_active_targets VALUES(?,?)',('run',canonical(bound)))
            value=control_value(bound,'steer','wrong')
            with self.assertRaisesRegex(Blocked,'pending original question pin'):
                ledger.control(value,verify_owner=standing_authority,current_binding=bound)
            with owner.store.transaction() as db:db.execute("UPDATE wf_questions SET stage='continued'")
            invalid=copy.deepcopy(value);invalid['binding']['session_id']='wrong'
            with self.assertRaisesRegex(Blocked,'stale/wrong'):
                ledger.control(invalid,verify_owner=standing_authority,current_binding=bound)
            invalid=copy.deepcopy(value);invalid['scope']='requires_approval';invalid['stage']='blocked'
            with self.assertRaisesRegex(Blocked,'producing approval'):
                ledger.control(invalid,verify_owner=standing_authority,current_binding=bound)
            one=ledger.control(value,verify_owner=standing_authority,current_binding=bound)
            self.assertEqual(one,ledger.control(value,verify_owner=standing_authority,current_binding=bound))
            invalid={**value,'message':'conflict'}
            with self.assertRaisesRegex(Blocked,'conflicting duplicate'):
                ledger.control(invalid,verify_owner=standing_authority,current_binding=bound)
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_owner_inputs').fetchone()[0],1)
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)
