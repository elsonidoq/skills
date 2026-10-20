"""Actual standalone CLI/SDK/SQLite/Git composition, isolated and owner-authorized."""
import copy
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import unittest
import tempfile

import yaml

from coherence_workflow.intake import approval_scope, content_hash
from coherence_workflow.cli import Coordinate
from coherence_workflow.store import Authority, Blocked, canonical, digest, git
from coherence_workflow.tools import snapshot
from test_intake import approved_fixture, declare_builtin_actions
from test_pi_adapter import environment, manifest
from test_custody import IsolatedCustody

ROOT=Path(__file__).resolve().parents[2]


def retain_failure(case, result, inputs):
    """Private read-only diagnostic copy, never a resumable authority/worktree."""
    import hashlib
    import shutil
    import uuid
    root=Path(tempfile.gettempdir())/'coherence-lean-T001-diagnostics'
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
    selected=config['profiles']['sol-medium']
    contract['execution_intent']['compatible_bindings']=[{**{k:selected[k] for k in ('provider','model','effort')},
        'assessment':'isolated selected configuration','provenance':'current authorized live exercise'}]
    contract['authorization_envelope']['profiles']=[selected]
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


class A2LiveDeliveryTests(IsolatedCustody):
    def test_single_task_terra_read_continuation_safe_error_check_and_commit(self):
        self.assertEqual(os.environ.get('COHERENCE_LIVE'),'1','REQUIRED A2 live execution unavailable; NOT VERIFIED')
        config=yaml.safe_load((ROOT/'runtime/coherence_workflow/workflows/coordinate.yaml').read_text())
        terra={**config['profiles']['sol-medium'],'model':'gpt-5.6-terra'}
        config['profiles']['terra-medium']=terra
        for node in config['nodes']:
            if node['type']=='agent': node['profile']='terra-medium'
        import uuid
        token=uuid.uuid4().hex
        large=self.project/'large.py'
        large.write_text('# Project source: scoped continuation and exact region editing.\n'*700+
                         '# continuation token: '+token+'\n')
        owned_source='# Application source: preserve this existing implementation commentary.\n'*700+"RESULT = 'pending'\n"
        (self.project/'owned.txt').write_text(owned_source)
        git(self.project,'add','--','owned.txt');git(self.project,'commit','-qm','large project source baseline')
        check_script=self.project/'check_project.py'
        check_script.write_text('import runpy\nfrom pathlib import Path\n'
            'expected=Path("large.py").read_text().split("# continuation token: ")[1].strip()\n'
            'assert runpy.run_path("owned.txt")["RESULT"] == expected\n'
            'print("project command: continuation-derived RESULT validated")\n')
        unavailable=self.project/'read-error.txt';unavailable.write_text('remove after admission')
        sdk=manifest(self.project,tools=False)
        sdk['profile']=terra
        sdk['skills']=[{'path':str(ROOT/'skills/coordinate-implementation/SKILL.md'),
                        'sha256':config['skills']['coordinate']['sha256'],'name':'coordinate-implementation'}]
        sdk['resource_hash']=digest({k:sdk[k] for k in ('skills','tools','permissions','trust','system_prompt')})
        for private in (self.project/'.coherence', self.project/'.coherence/workflow', self.project/'.coherence/workflow/sdk'):
            private.chmod(0o700)
        contract,catalog=approved_fixture(self.project,digest(config))
        task=contract['tasks'][0];contract['tasks']=[task]
        task['outcome']=(
            'First read read-error.txt; correct its safe unavailable error in this SAME attempt by reading large.py. '
            'Read large.py from offset 0 using limit 32768, then use returned continuation to read the tail. '
            'Extract the continuation token from the actual returned tail text. '
            'Read/search owned.txt (a large Python source), then use edit_file to replace the unique exact '
            'region RESULT = '+repr('pending')+' with RESULT = followed by the quoted extracted token. '
            'Preserve every other byte; do NOT replace the whole large file. '
            'Use run_check for the approved REQUIRED item '+task['required'][0]['id']+'.')
        task['required'][0]['check']={'id':'workflow.Command','version':'1',
            'args':{'argv':[str(Path(sys.executable).resolve()),str(check_script)]}}
        task['required'][0]['pass_condition']='real project command validates the continuation-derived source result'
        contract['sources'] += [{'path':p.name,'section':None,'sha256':content_hash(p),'kind':'source'}
                                for p in (large,unavailable,check_script)]
        contract['execution_intent']['compatible_bindings']=[{**{k:terra[k] for k in ('provider','model','effort')},
            'assessment':'single isolated A2 configured binding','provenance':'current owner-authorized A2 exercise'}]
        contract['authorization_envelope']['profiles']=[terra]
        declare_builtin_actions(contract)
        for ref in contract['approval_refs']:
            ref['scope_hash']=(approval_scope(contract,digest(config)) if ref['gate_kind']=='implementation' else digest(contract['sources']))
            catalog[ref['authority_ref']]['scope_hash']=ref['scope_hash']
        with Authority(self.project) as authority:
            authority.store.reserve('a2',digest(config))
            coordinate=Coordinate(authority,'a2',contract,catalog,config,self.parent,sdk,environment())
            coordinate.intake({})
            unavailable.unlink()  # Authorized path remains readable but safely unavailable at tool use.
            self.assertEqual(coordinate.authority_check({}),{'outcome':'ok'})
            self.assertEqual(coordinate.select({}),{'outcome':'work'})
            observed_tools=[];factory=coordinate._tools
            from dataclasses import replace
            def capture_tools(*args,**kwargs):
                tools=factory(*args,**kwargs)
                def capture(tool):
                    reader=tool.result_reader
                    def observed(args,receipt):
                        event={'tool':tool.id,'args':dict(args)};observed_tools.append(event)
                        try:
                            result=reader(args,receipt)
                            if tool.id in ('read_file','search_file'):
                                event['result']=result
                            elif tool.id=='run_check':event['statuses']=[r['status'] for r in result]
                            else:event['result']=result
                            return result
                        except Exception as exc:
                            event['error']=str(exc);raise
                    return replace(tool,result_reader=observed)
                return {key:capture(tool) for key,tool in tools.items()}
            coordinate._tools=capture_tools
            node=next(n for n in config['nodes'] if n['id']=='implement')
            self.assertEqual(coordinate.implement({'node':node,'operation_id':'a2-implement'}),{'outcome':'ok'})
            verification=coordinate.verify({})
            self.assertEqual(verification,{'outcome':'ok'}, canonical({'verification':verification,
                'owned':(self.project/'owned.txt').read_text(), 'tools':observed_tools,
                'evidence':[json.loads(row[0]) for row in authority.store.db.execute("SELECT receipt FROM wf_checks WHERE run_id='a2'")]}))
            self.assertEqual(coordinate.checkpoint({}),{'outcome':'ok'})
            row=authority.store.db.execute("SELECT checkpoint FROM wf_tasks WHERE run_id='a2' AND task_id='A'").fetchone()
            checkpoint=json.loads(row[0]);self.assertFalse(checkpoint['read_only'])
            self.assertEqual((self.project/'owned.txt').read_text(),owned_source.replace("RESULT = 'pending'","RESULT = "+repr(token)))
            failed=[e for e in observed_tools if e['args'].get('path')=='read-error.txt' and 'error' in e]
            self.assertTrue(failed,observed_tools)
            reads=[e for e in observed_tools if e['tool']=='read_file' and e['args']['path']=='large.py' and 'result' in e]
            self.assertTrue(any(e['args'].get('offset',0)==0 for e in reads))
            self.assertTrue(any(e['args'].get('offset',0)>=32768 and token in e['result']['text'] for e in reads))
            self.assertTrue(any(e['tool']=='edit_file' and 'result' in e for e in observed_tools))
            self.assertTrue(any(e['tool']=='run_check' and e.get('statuses')==['satisfied'] for e in observed_tools))
            processes=authority.store.db.execute('SELECT o.phase,p.containment FROM wf_processes p JOIN wf_operations o USING(op_id)').fetchall()
            for process in processes:
                self.assertEqual(process['phase'],'completed')
                receipt=json.loads(process['containment'])
                self.assertEqual(coordinate.gateway.containment.populated(receipt),0)
                if receipt not in self.receipts:self.receipts.append(receipt)
            self.assertEqual(authority.store.db.execute("SELECT COUNT(*) FROM wf_operations WHERE kind='sdk-turn' AND phase='completed'").fetchone()[0],1)
            observed=[json.loads(row[0]) for row in authority.store.db.execute("SELECT payload FROM wf_events WHERE kind LIKE 'sdk:%'")]
            self.assertTrue(any(value.get('model')=='gpt-5.6-terra' and value.get('wire_effort')=='medium' for value in observed))
            print(canonical({'proof':'a2-single-task','binding':terra,
                'observed_binding':next({k:value[k] for k in ('provider','model','wire_effort') if k in value} for value in observed if value.get('model')=='gpt-5.6-terra' and value.get('wire_effort')=='medium'),
                'attempt_id':json.loads(authority.store.db.execute("SELECT intent FROM wf_operations WHERE kind='sdk-turn' AND phase='completed'").fetchone()[0])['attempt_id'],
                'baseline':checkpoint['parent'],
                'result':checkpoint['sha'],'check':json.loads(authority.store.db.execute("SELECT receipt FROM wf_checks WHERE run_id='a2'").fetchone()[0]),
                'tool_operations':[{**e,'result':({k:v for k,v in e['result'].items() if k!='text'} if isinstance(e.get('result'),dict) else e.get('result'))} for e in observed_tools],
                'diff':git(self.project,'diff',checkpoint['parent'],checkpoint['sha'],'--stat').decode(),
                'owned_diff':git(self.project,'diff','--unified=1',checkpoint['parent'],checkpoint['sha'],'--','owned.txt').decode(),
                'process_tools':[json.loads(row[0])['tool'] for row in authority.store.db.execute("SELECT intent FROM wf_operations WHERE kind='process'")],
                'settled_processes':len(processes),'custody':'all recorded process scopes settled before checkpoint'}))


class SequentialCliTests(IsolatedCustody):
    def test_real_two_task_sequence(self):
        live_sequence(self)


class DiagnosticRetentionTests(IsolatedCustody):
    def test_offline_invalid_arguments_return_correctable_error_without_process_or_poison(self):
        from types import SimpleNamespace
        from coherence_workflow.pi_adapter import PiAdapter
        from test_review_repair import coordinate_fixture
        from unittest.mock import patch
        with Authority(self.project) as owner:
            coordinate=coordinate_fixture(self.project,owner)
            tool=coordinate._tools(coordinate.contract['tasks'][0])['read_file']
            adapter=object.__new__(PiAdapter)
            adapter.gateway=coordinate.gateway;adapter.gateway.tools={tool.id:tool}
            adapter.manifest={'tools':[{'name':tool.id,'version':'1','parameters':tool.arguments}]}
            adapter.lifecycle=SimpleNamespace(active=True,poisoned=False,generation=1)
            adapter.compatibility={'role':'implement'};adapter.binding={'run_id':'run'}
            adapter.current={'operation_id':'offline','attempt_id':'A:0','command_id':'offline-command'}
            adapter.session_id='offline-session';adapter.tool_calls_seen=set();adapter.question_gate=None
            replies=[];dispositions=[]
            adapter.send=lambda *args,**kwargs:replies.append((args,kwargs))
            adapter._tool_disposition=lambda record,state,**kwargs:dispositions.append(state)
            record={**adapter.binding,**adapter.current,'session_id':adapter.session_id,
                'payload':{'generation':1,'call':'invalid','tool':tool.id,'version':'1','args':{'path':'../escape'}}}
            with patch.object(adapter.gateway,'launch',side_effect=AssertionError('invalid arguments launched process')):
                adapter._launch_tool(record)
            output=json.loads(replies[0][0][1]['result']['content'][0]['text'])
            self.assertIn('invalid arguments',output['error']['message'])
            self.assertIn('continue',output['error']['correction'])
            self.assertEqual(dispositions,['invalid_arguments']);self.assertFalse(adapter.lifecycle.poisoned)
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)


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
            self.assertEqual(set(actual),{'read_file','search_file','write_file','edit_file','run_check'})
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

    def test_upfront_gap_output_aggregates_profile_check_and_git_without_dispatch(self):
        from coherence_workflow.store import Authority, Blocked
        from test_review_repair import coordinate_fixture
        with Authority(self.project) as owner:
            coordinate=coordinate_fixture(self.project,owner)
            hook=self.project/'.git/hooks/post-index-change';hook.write_text('#!/bin/sh\nexit 99\n');hook.chmod(0o700)
            coordinate.contract['tasks'][0]['required'][0]['check']['id']='workflow.NotRegistered'
            with self.assertRaisesRegex(Blocked,'known admission gaps') as error:coordinate.authority_check({})
            gaps=json.loads(str(error.exception).split(': ',1)[1])
            self.assertTrue({'profile','check','git_capability'} <= {gap['kind'] for gap in gaps})
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


class LeanReadinessTests(unittest.TestCase):
    def test_five_facts_and_invalidation_boundaries(self):
        from coherence_workflow.store import Authority
        from coherence_workflow.engine import load_workflow
        from test_review_repair import coordinate_fixture
        from unittest.mock import patch
        from fixtures.support import make_project
        with tempfile.TemporaryDirectory() as temporary:
            project=make_project(Path(temporary)/'project')
            def setup(contract):
                config=yaml.safe_load((ROOT/'runtime/coherence_workflow/workflows/coordinate.yaml').read_text())
                contract['authorization_envelope']['profiles']=[config['profiles']['sol-medium']]
            with Authority(project) as authority:
                c=coordinate_fixture(project,authority,task_setup=setup)
                self.assertEqual(load_workflow(c.registry(),resource_root=ROOT),c.config)
                self.assertEqual(c.authority_check({}),{'outcome':'ok'})
                original=copy.deepcopy(c.contract)
                c.contract['tasks'][0]['depends']=['B']
                with self.assertRaises(Blocked):c.intake({})
                c.contract=copy.deepcopy(original)
                approval=project/c.contract['approval_refs'][0]['record_ref']
                saved=approval.read_bytes();approval.write_text('not the approved record')
                with self.assertRaisesRegex(Blocked,'approval record content drift'):c.intake({})
                approval.write_bytes(saved)
                profile=c.manifest['profile'];c.manifest['profile']={**profile,'model':'unavailable'}
                with self.assertRaisesRegex(Blocked,'known admission gaps'):c.authority_check({})
                c.manifest['profile']=profile
                check=c.contract['tasks'][0]['required'][0]['check']
                c.contract['tasks'][0]['required'][0]['check']={**check,'id':'workflow.Unavailable'}
                with self.assertRaisesRegex(Blocked,'REQUIRED oracle unavailable|known admission gaps'):c.authority_check({})
                c.contract=copy.deepcopy(original)
                # A second actual authority and dirty owned overlap both stop selection.
                with self.assertRaises(Blocked):Authority(project)
                owned=project/'owned.txt';saved=owned.read_bytes();owned.write_text('unrelated preexisting edit')
                with self.assertRaisesRegex(Blocked,'dirty owned overlap'):c.select({})
                owned.write_bytes(saved)
                self.assertEqual(c.select({}),{'outcome':'work'})
                c.agent_node=next(n for n in c.config['nodes'] if n['id']=='implement')
                c.gateway.tools=c._tools(c.contract['tasks'][0])
                # Tool calls do not recursively re-admit the whole contract.
                with patch('coherence_workflow.cli.admit',side_effect=AssertionError('repeated intake')):
                    self.assertEqual(c.gateway.direct('read_file',{'path':'owned.txt'})['text'],'base')
                c.contract['tasks'][0]['outcome']='changed after intake'
                with self.assertRaisesRegex(Blocked,'contract drift'):
                    c.gateway.direct('read_file',{'path':'owned.txt'})
                self.assertEqual(authority.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)


class LeanCheckpointTests(unittest.TestCase):
    def test_required_check_and_gate_precede_commit(self):
        from coherence_workflow.store import Authority
        from fixtures.support import make_project
        from test_review_repair import coordinate_fixture
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as temporary:
            project=make_project(Path(temporary)/'project')
            with Authority(project) as authority:
                c=coordinate_fixture(project,authority)
                c.select({});task=c.contract['tasks'][0]
                c.agent_node=next(n for n in c.config['nodes'] if n['id']=='implement')
                c.gateway.tools=c._tools(task)
                with patch.object(c.gateway,'launch',side_effect=AssertionError('commit before REQUIRED/gates')):
                    # Actual failed REQUIRED receipt; original (empty) gates are true.
                    self.assertTrue(c.gates_satisfied(task))
                    self.assertNotEqual(c.verify({}),{'outcome':'ok'})
                    evidence=json.loads(c.current()['evidence'])
                    self.assertEqual(c.verification.audit(task,evidence)[0]['status'],'failed')
                    with self.assertRaisesRegex(Blocked,'REQUIRED evidence/original gates'):c.checkpoint({})
                    # Correct the source and collect a genuine satisfied receipt.
                    c.gateway.direct('write_file',{'path':'owned.txt','text':'first\n'})
                    self.assertEqual(c.verify({}),{'outcome':'ok'})
                    evidence=json.loads(c.current()['evidence'])
                    self.assertEqual(c.verification.audit(task,evidence)[0]['status'],'satisfied')
                    with patch.object(c,'gates_satisfied',return_value=False):
                        with self.assertRaisesRegex(Blocked,'REQUIRED evidence/original gates'):c.checkpoint({})
                self.assertEqual(authority.store.db.execute("SELECT COUNT(*) FROM wf_operations WHERE kind='git-checkpoint'").fetchone()[0],0)
                self.assertEqual(authority.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)


class InternalPythonBindingTests(IsolatedCustody):
    def test_actual_registered_write_read_helpers_bind_runtime_but_project_test_imports_remain_project_code(self):
        from coherence_workflow.cli import Coordinate
        from coherence_workflow.store import Authority
        from test_review_repair import coordinate_fixture
        from test_intake import declare_builtin_actions
        from unittest.mock import patch
        shadow=self.project/'coherence_workflow';shadow.mkdir();marker=self.project/'SHADOW_INTERNAL'
        (shadow/'__init__.py').write_text('from pathlib import Path\nPath('+repr(str(marker))+').write_text("shadow")\nraise RuntimeError("SHADOW_INTERNAL")\n')
        (self.project/'project_values.py').write_text('VALUE=1\n')
        (self.project/'answer.py').write_text('from project_values import VALUE\ndef answer(): return VALUE\n')
        config=yaml.safe_load((ROOT/'runtime/coherence_workflow/workflows/coordinate.yaml').read_text())
        def setup(contract):
            contract['authorization_envelope']['profiles']=[config['profiles']['sol-medium']]
            task=contract['tasks'][0]
            task['required'].append({**copy.deepcopy(task['required'][0]),'id':'A/Python',
                'check':{'id':'workflow.PythonAnswer','version':'1','args':{'path':'answer.py','expected':1}}})
        with Authority(self.project) as owner:
            c=coordinate_fixture(self.project,owner,task_setup=setup)
            self.assertEqual(c.authority_check({}),{'outcome':'ok'})
            c.select({});task=c.contract['tasks'][0];c.agent_node=next(n for n in c.config['nodes'] if n['id']=='implement')
            c.gateway.tools=c._tools(task)
            original=Path.cwd()
            try:
                os.chdir(self.project)
                for index,path in enumerate((None,str(self.project))):
                    env=dict(os.environ);env.pop('PYTHONPATH',None)
                    if path:env['PYTHONPATH']=path
                    with patch.dict(os.environ,env,clear=True):
                        # Root task-origin custody permits the second understood owned write.
                        if index==0:c.gateway.audit_task_boundary(task['owned_paths'],json.loads(c.current()['baseline']))
                        c.gateway.direct('write_file',{'path':'owned.txt','text':'first\n'})
                        self.assertEqual(c.gateway.direct('read_file',{'path':'owned.txt'})['text'],'first\n')
                self.assertFalse(marker.exists())
                # Distinct explicit oracle capability intentionally executes trusted project imports.
                evidence=c.verification.run_checks(task)
                self.assertTrue(all(row['status']=='satisfied' for row in evidence))
                self.assertFalse(marker.exists(),'system module resolution fell through to project code')
            finally:
                os.chdir(original)
                for row in owner.store.db.execute('SELECT containment FROM wf_processes WHERE containment IS NOT NULL'):
                    receipt=json.loads(row[0])
                    if receipt not in self.receipts:self.receipts.append(receipt)
