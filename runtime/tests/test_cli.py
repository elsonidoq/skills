"""Actual standalone CLI/SDK/SQLite/Git composition, isolated and owner-authorized."""
import copy
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

import yaml

from coherence_workflow.intake import approval_scope
from coherence_workflow.store import canonical, digest, git
from coherence_workflow.tools import snapshot
from test_intake import approved_fixture, declare_builtin_actions
from test_pi_adapter import manifest
from test_custody import IsolatedCustody

ROOT=Path(__file__).resolve().parents[2]


def retain_failure(case, result, inputs):
    """Private read-only diagnostic copy, never a resumable authority/worktree."""
    import hashlib
    import shutil
    import uuid
    root=ROOT/'.pi/workflow-validation/implementation/t005/diagnostics'
    root.mkdir(parents=True,exist_ok=True)
    target=root/uuid.uuid4().hex;target.mkdir(mode=0o700)
    empty=[];errors=[]
    for receipt in case.receipts:
        try:empty.append(case.capability.drain(receipt))
        except Exception as exc:errors.append({'scope_name':receipt['name'],'exception_type':type(exc).__name__})
    observed=snapshot(case.project,[])
    shutil.copytree(case.project,target/'project',symlinks=True,
                    ignore=shutil.ignore_patterns('workflow.sqlite','workflow.sqlite-wal','workflow.sqlite-shm'))
    database=case.project/'.coherence/workflow/workflow.sqlite';diagnostics=[]
    if database.is_file():
        source=sqlite3.connect(database.as_uri()+'?mode=ro',uri=True)
        destination=sqlite3.connect(target/'project/.coherence/workflow/workflow.sqlite')
        try:
            source.backup(destination)
            diagnostics=[json.loads(row[0]) for row in source.execute("SELECT payload FROM wf_events WHERE kind='sdk_failure_diagnostic'")]
            case.assertEqual(destination.execute('PRAGMA integrity_check').fetchone()[0],'ok')
        finally:destination.close();source.close()
    (target/'inputs').mkdir(mode=0o700)
    input_hashes={}
    for name,path in inputs.items():
        data=Path(path).read_bytes();(target/'inputs'/name).write_bytes(data)
        input_hashes[name]=hashlib.sha256(data).hexdigest()
    metadata={'purpose':'isolated failure inspection only; copied binding is NOT resumable authority',
        'exit_code':result.returncode,'stdout_sha256':hashlib.sha256(result.stdout.encode()).hexdigest(),
        'stderr_sha256':hashlib.sha256(result.stderr.encode()).hexdigest(),'diagnostics':diagnostics,
        'empty_receipts':empty,'cleanup_errors':errors,'partial_snapshot':observed,'input_hashes':input_hashes,
        'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in (ROOT/'runtime/coherence_workflow').glob('*.py')},
        'environment':{k:os.environ.get(k) for k in ('PYTHONPATH','TMPDIR','PI_OFFLINE','COHERENCE_LIVE')},
        'environment_hash':digest({k:os.environ.get(k) for k in ('PYTHONPATH','TMPDIR','PI_OFFLINE','COHERENCE_LIVE')}),
        'host_sha256':hashlib.sha256((ROOT/'runtime/pi-host/host.mjs').read_bytes()).hexdigest(),
        'credential_hashes':{k:hashlib.sha256(Path(os.environ[k]).read_bytes()).hexdigest()
                             for k in ('COHERENCE_AUTH_PATH','COHERENCE_CATALOG_PATH') if os.environ.get(k)}}
    (target/'metadata.json').write_text(canonical(metadata)+'\n')
    for path in target.rglob('*'):
        if not path.is_symlink():path.chmod(0o700 if path.is_dir() else 0o600)
    print(canonical({'failure_evidence':str(target),'classification':diagnostics,'empty_scope_count':len(empty),'cleanup_errors':errors}))
    return target


def live_sequence(case, *, expected_check_count=2):
    case.assertEqual(os.environ.get('COHERENCE_LIVE'),'1','REQUIRED real CLI/Pi integration unavailable; NOT VERIFIED')
    project=case.project
    (project/'second.txt').write_text('initial second')
    git(project,'add','--','second.txt');git(project,'commit','-qm','isolated second baseline')
    (project/'other.txt').write_text('unrelated stage');git(project,'add','--','other.txt')
    (project/'custom.md').write_text('unrelated unstaged');(project/'untracked-user').write_text('unrelated')
    config=yaml.safe_load((ROOT/'runtime/coherence_workflow/workflows/coordinate.yaml').read_text())
    (project/'.coherence/workflow').mkdir(parents=True,mode=0o700)
    sdk=manifest(project,tools=False)
    sdk['skills']=[{'path':str(ROOT/'skills/coordinate-implementation/SKILL.md'),
                    'sha256':config['skills']['coordinate']['sha256'],'name':'coordinate-implementation'}]
    sdk['resource_hash']=digest({k:sdk[k] for k in ('skills','tools','permissions','trust','system_prompt')})
    contract,catalog=approved_fixture(project,digest(config))
    contract['authorization_envelope']['profiles']=[config['profiles']['sol-medium']]
    declare_builtin_actions(contract)
    for ref in contract['approval_refs']:
        if ref['gate_kind']=='implementation':
            ref['scope_hash']=approval_scope(contract,digest(config));catalog[ref['authority_ref']]['scope_hash']=ref['scope_hash']
    paths={name:case.root/name for name in ('workflow.yaml','tasks.json','catalog.json','manifest.json')}
    paths['workflow.yaml'].write_text(yaml.safe_dump(config));paths['tasks.json'].write_text(canonical(contract))
    paths['catalog.json'].write_text(canonical(catalog));paths['catalog.json'].chmod(0o600)
    paths['manifest.json'].write_text(canonical(sdk))
    before=snapshot(project,['owned.txt','second.txt'])
    argv=[str(ROOT/'scripts/coordinate-implementation'),'start','--project',str(project),'--run','sequence',
          '--workflow',str(paths['workflow.yaml']),'--tasks',str(paths['tasks.json']),
          '--owner-catalog',str(paths['catalog.json']),'--manifest',str(paths['manifest.json']),'--containment',case.parent]
    env=dict(os.environ,COHERENCE_PYTHON=sys.executable)
    proc=subprocess.run(argv,env=env,capture_output=True,text=True,timeout=240)
    print('CLI invocation result',proc.returncode,proc.stdout,proc.stderr)
    if not (project/'.coherence/workflow/workflow.sqlite').is_file():retain_failure(case,proc,paths)
    case.assertTrue((project/'.coherence/workflow/workflow.sqlite').is_file(),proc.stdout+proc.stderr)
    db=sqlite3.connect(project/'.coherence/workflow/workflow.sqlite');db.row_factory=sqlite3.Row
    try:
        for row in db.execute('SELECT containment FROM wf_processes WHERE containment IS NOT NULL'):
            receipt=json.loads(row[0])
            if receipt not in case.receipts:case.receipts.append(receipt)
        if proc.returncode!=0:retain_failure(case,proc,paths)
        case.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)
        rows=[dict(row) for row in db.execute('SELECT * FROM wf_tasks ORDER BY approved_order')]
        case.assertEqual([row['state'] for row in rows],['checkpointed','checkpointed'])
        checkpoints=[json.loads(row['checkpoint']) for row in rows]
        case.assertEqual(checkpoints[0]['parent'],before['head']);case.assertEqual(checkpoints[1]['parent'],checkpoints[0]['sha'])
        after=snapshot(project,['owned.txt','second.txt'])
        for name,value in before['files'].items():
            if name not in ('owned.txt','second.txt'):case.assertEqual(value,after['files'].get(name),name)
        case.assertEqual(git(project,'diff','--cached','--name-only').decode().strip(),'other.txt')
        events=[dict(row) for row in db.execute('SELECT seq,kind,payload FROM wf_events ORDER BY seq')]
        selected=[row for row in events if row['kind']=='task_selected'];committed=[row for row in events if row['kind']=='task_checkpointed']
        case.assertLess(committed[0]['seq'],selected[1]['seq'])
        observations=[json.loads(row['payload']) for row in db.execute("SELECT payload FROM wf_events WHERE kind LIKE 'sdk:%'")]
        observed=[row for row in observations if row.get('wire_effort')]
        case.assertTrue(observed)
        case.assertTrue(all(row['model']=='gpt-6.1-sol' and row['wire_effort']=='medium' for row in observed))
        checkrows=[json.loads(row[0]) for row in db.execute('SELECT receipt FROM wf_checks')]
        case.assertEqual(len(checkrows),expected_check_count);case.assertTrue(all(row['collected']==1 and row['status']=='satisfied' for row in checkrows))
        # A separate process queries SQL without launching Node or changing projections.
        status=subprocess.run([str(ROOT/'scripts/coordinate-implementation'),'status','--project',str(project),'--run','sequence'],
                              env=env,capture_output=True,text=True,timeout=20)
        case.assertEqual(status.returncode,0,status.stdout+status.stderr)
        case.assertTrue(json.loads(status.stdout)['accepted'])
        review=db.execute('SELECT * FROM wf_reviews ORDER BY rowid DESC LIMIT 1').fetchone()
        case.assertEqual(review['base_sha'],before['head']);case.assertEqual(review['head_sha'],checkpoints[-1]['sha'])
        case.assertEqual(json.loads(review['result'])['outcome'],'pass');case.assertEqual(review['independent'],1)
        case.assertEqual(db.execute("SELECT COUNT(*) FROM wf_findings WHERE disposition!='resolved'").fetchone()[0],0)
        ready=json.loads(db.execute("SELECT payload FROM wf_events WHERE op_id=? AND kind='host_ready'",(review['host_op'],)).fetchone()[0])
        case.assertEqual(ready['compatibility']['role'],'review');case.assertEqual(sorted(ready['snapshot']['tools']),sorted(next(n for n in config['nodes'] if n['id']=='review')['tools']))
        print(canonical({'proof':'actual-cli-sdk-two-tasks','argv':argv,'exit':proc.returncode,'checkpoints':checkpoints,
                         'observed':observed,'checks':checkrows,'event_order':[(r['seq'],r['kind']) for r in events],
                         'source_revision':git(ROOT,'rev-parse','HEAD').decode().strip()}))
    finally:
        db.close()


class SequentialCliTests(IsolatedCustody):
    def test_real_two_task_sequence(self):
        live_sequence(self)


class DiagnosticRetentionTests(IsolatedCustody):
    def test_offline_schema_failure_is_sanitized_retained_drained_and_not_released(self):
        from coherence_workflow.pi_adapter import PiAdapter
        from coherence_workflow.store import Authority, Blocked
        from test_pi_adapter import environment
        from fixtures.custody_support import process_tool
        with Authority(self.project) as owner:
            gateway=self.gateway(owner)
            sdk=manifest(self.project)
            adapter=PiAdapter(gateway,sdk,node='offline-diagnostic-host',environment=environment(),
                session_context={'role':'implement','affinity':'story','review_lineage':None})
            for row in owner.store.db.execute('SELECT containment FROM wf_processes WHERE containment IS NOT NULL'):
                self.receipts.append(json.loads(row[0]))
            original_send=adapter.send;initial_generation=adapter.snapshot['generation']
            def inject(op,payload,**kwargs):
                if op=='prompt':
                    adapter.current['command_id']='offline-no-send'
                    adapter._launch_tool({**adapter.binding,'operation_id':adapter.current['operation_id'],
                        'attempt_id':adapter.current['attempt_id'],'session_id':adapter.session_id,
                        'command_id':'offline-no-send','payload':{
                        'generation':adapter.lifecycle.generation,'call':'invalid-schema-fixture','tool':'fixture','version':'1',
                        'args':{'mode':'DO_NOT_LOG_AUTH_SENTINEL','exit':0}}})
                    raise AssertionError('schema fixture unexpectedly admitted')
                # No prompt reached the actual host; drain its observed initial generation.
                if op=='abort':payload={**payload,'generation':initial_generation}
                return original_send(op,payload,**kwargs)
            adapter.send=inject
            with self.assertRaisesRegex(Blocked,'cause=tool_or_record_schema; phase=tool_admission'):
                adapter.prompt(node='offline-schema',task_id='offline-schema',attempt_id='offline-schema:0',role='implement',
                    text='Offline no-send schema fixture.',skill='bounded-proof',contract_hash=digest('offline-schema'),selection={'reason':'offline-no-send'})
            self.assertTrue(adapter.lifecycle.poisoned)
            self.assertFalse(any(r['type']=='request_observation' for r in adapter.records),'offline seam made a provider request')
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],1,'invalid tool launched a process')
            pending=owner.store.db.execute("SELECT * FROM wf_operations WHERE kind='sdk-turn'").fetchone()
            self.assertEqual(pending['phase'],'intent');self.assertIsNone(pending['result'])
            diagnostic=json.loads(owner.store.db.execute("SELECT payload FROM wf_events WHERE kind='sdk_failure_diagnostic'").fetchone()[0])
            self.assertEqual(diagnostic['schema_validator'],'enum')
            self.assertEqual(diagnostic['classification'],'tool_or_record_schema')
            adapter.close(force=True)
            result=subprocess.CompletedProcess(['offline-schema-fixture'],2,'sanitized offline schema blocker','')
            retained=retain_failure(self,result,{})
            metadata=(retained/'metadata.json').read_text()
            self.assertNotIn('DO_NOT_LOG_AUTH_SENTINEL',metadata)
            self.assertFalse(json.loads(metadata)['cleanup_errors'])
            self.assertEqual(json.loads(metadata)['environment_hash'],digest(json.loads(metadata)['environment']))
            self.assertTrue(all(r['populated']==0 for r in json.loads(metadata)['empty_receipts']))
            self.assertTrue((retained/'project/.coherence/workflow/workflow.sqlite').is_file())
            self.assertTrue((retained/'project/.coherence/workflow/sdk/sessions').is_dir())


class CliPreflightTests(IsolatedCustody):
    def test_restrictive_nodes_are_never_widened_before_sdk_launch(self):
        from unittest.mock import patch
        from coherence_workflow.cli import Coordinate
        from coherence_workflow.store import Authority, Blocked
        from test_review_repair import coordinate_fixture
        with Authority(self.project) as owner:
            coordinate=coordinate_fixture(self.project,owner)
            coordinate.select({})
            coordinate.manifest['skills'][0]['sha256']=coordinate.config['skills']['coordinate']['sha256']
            def forbidden_launch(gateway,manifest,**unused):
                raise AssertionError('unauthorized SDK launch manifest: '+canonical({'tools':[t['name'] for t in manifest['tools']],'permissions':manifest['permissions']}))
            with patch('coherence_workflow.cli.PiAdapter',side_effect=forbidden_launch) as launch:
                for role in ('implement','repair'):
                    original=next(n for n in coordinate.config['nodes'] if n['id']==role)
                    for tools,permissions in ((['read_file'],['read_file']),
                                              (['read_file','write_file'],['read_file']),([],[])):
                        node={**original,'tools':tools,'permissions':permissions}
                        with self.subTest(role=role,tools=tools,permissions=permissions):
                            with self.assertRaisesRegex(Blocked,'node tool/permission'):
                                coordinate.implement({'node':node},role=role)
                coordinate.current=lambda:None
                coordinate.reconcile_effect=lambda *unused:True
                coordinate.review_repair.refresh_evidence=lambda:None
                coordinate.review_repair.bundle=lambda:{'range_base':'base','range_head':'head'}
                review=next(n for n in coordinate.config['nodes'] if n['id']=='review')
                for tools,permissions in (([],[]),(['read_file'],[]),(['read_file','write_file'],['read_file','write_file'])):
                    with self.subTest(role='review',tools=tools,permissions=permissions):
                        with self.assertRaisesRegex(Blocked,'node tool/permission'):
                            coordinate.review_boundary({'node':{**review,'tools':tools,'permissions':permissions}})
                launch.assert_not_called()
            task=json.loads(coordinate.store.db.execute('SELECT contract FROM wf_tasks WHERE task_id=?',('A',)).fetchone()[0])
            actual=coordinate._tools(task)
            Coordinate.admit_node_tools({'tools':list(actual),'permissions':list(actual)},actual)
            self.assertEqual(set(actual),{'read_file','write_file'})
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)

    def test_raw_cli_yaml_rejects_alias_duplicate_tag_and_oversize_before_store_or_dispatch(self):
        contract,catalog=approved_fixture(self.project,'not-dispatchable-invalid-workflow')
        paths={name:self.root/name for name in ('tasks.json','catalog.json','manifest.json','workflow.yaml')}
        paths['tasks.json'].write_text(canonical(contract));paths['catalog.json'].write_text(canonical(catalog));paths['catalog.json'].chmod(0o600)
        paths['manifest.json'].write_text('{}')
        argv=[str(ROOT/'scripts/coordinate-implementation'),'start','--project',str(self.project),'--run','invalid',
            '--workflow',str(paths['workflow.yaml']),'--tasks',str(paths['tasks.json']),'--owner-catalog',str(paths['catalog.json']),
            '--manifest',str(paths['manifest.json']),'--containment',self.parent]
        for text in ('start: a\nstart: b\n','x: &alias []\ny: *alias\n','x: !!python/object:forbidden {}\n','#'*262145):
            paths['workflow.yaml'].write_text(text)
            result=subprocess.run(argv,env=dict(os.environ,COHERENCE_PYTHON=sys.executable),capture_output=True,text=True,timeout=20)
            self.assertEqual(result.returncode,2,result.stdout+result.stderr)
            self.assertEqual(json.loads(result.stdout)['status'],'blocked')
            self.assertFalse((self.project/'.coherence/workflow/workflow.sqlite').exists())

    def test_upfront_gap_output_aggregates_profile_check_git_and_gate_without_dispatch(self):
        from coherence_workflow.store import Authority, Blocked
        from test_review_repair import coordinate_fixture
        with Authority(self.project) as owner:
            coordinate=coordinate_fixture(self.project,owner)
            hook=self.project/'.git/hooks/post-index-change';hook.write_text('#!/bin/sh\nexit 99\n');hook.chmod(0o700)
            coordinate.contract['tasks'][0]['required'][0]['check']['id']='workflow.NotRegistered'
            with self.assertRaisesRegex(Blocked,'known admission gaps') as error:coordinate.authority_check({})
            gaps=json.loads(str(error.exception).split(': ',1)[1])
            self.assertTrue({'profile','check','git_capability','gate'} <= {gap['kind'] for gap in gaps})
            self.assertTrue(all(gap['impact'] and gap['options'] for gap in gaps))
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)

    def test_copied_suite_status_unset_caller_flag_has_no_cache_or_worktree_writes(self):
        import shutil
        from coherence_workflow.store import Authority
        suite=self.project/'installed-suite'
        (suite/'runtime').mkdir(parents=True);(suite/'scripts').mkdir()
        shutil.copytree(ROOT/'runtime/coherence_workflow',suite/'runtime/coherence_workflow',
                        ignore=shutil.ignore_patterns('__pycache__'))
        launcher=suite/'scripts/coordinate-implementation';shutil.copy2(ROOT/'scripts/coordinate-implementation',launcher)
        env=dict(os.environ,COHERENCE_PYTHON=sys.executable,COHERENCE_AUTH_PATH='/unavailable',COHERENCE_CATALOG_PATH='/unavailable')
        env.pop('PYTHONDONTWRITEBYTECODE',None);env.pop('PYTHONPATH',None)
        with Authority(self.project) as owner:
            owner.store.reserve('read-only',digest('read-only-status'))
            before=snapshot(self.project,[])
            result=subprocess.run([str(launcher),'status','--project',str(self.project),'--run','read-only'],
                                  env=env,capture_output=True,text=True,timeout=20)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertEqual(json.loads(result.stdout)['state'],'interrupted')
            self.assertEqual(before,snapshot(self.project,[]))
            self.assertEqual(list(suite.rglob('__pycache__')),[])
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)
