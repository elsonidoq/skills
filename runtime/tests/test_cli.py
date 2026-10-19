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
from test_intake import approved_fixture
from test_pi_adapter import manifest
from test_custody import IsolatedCustody

ROOT=Path(__file__).resolve().parents[2]


def live_sequence(case):
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
    case.assertTrue((project/'.coherence/workflow/workflow.sqlite').is_file(),proc.stdout+proc.stderr)
    db=sqlite3.connect(project/'.coherence/workflow/workflow.sqlite');db.row_factory=sqlite3.Row
    try:
        for row in db.execute('SELECT containment FROM wf_processes WHERE containment IS NOT NULL'):
            receipt=json.loads(row[0])
            if receipt not in case.receipts:case.receipts.append(receipt)
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
        case.assertEqual(len(checkrows),2);case.assertTrue(all(row['collected']==1 and row['status']=='satisfied' for row in checkrows))
        # A separate process queries SQL without launching Node or changing projections.
        status=subprocess.run([str(ROOT/'scripts/coordinate-implementation'),'status','--project',str(project),'--run','sequence'],
                              env=env,capture_output=True,text=True,timeout=20)
        case.assertEqual(status.returncode,0,status.stdout+status.stderr)
        case.assertFalse(json.loads(status.stdout)['accepted'])
        print(canonical({'proof':'actual-cli-sdk-two-tasks','argv':argv,'exit':proc.returncode,'checkpoints':checkpoints,
                         'observed':observed,'checks':checkrows,'event_order':[(r['seq'],r['kind']) for r in events],
                         'source_revision':git(ROOT,'rev-parse','HEAD').decode().strip()}))
    finally:
        db.close()


class SequentialCliTests(IsolatedCustody):
    def test_real_two_task_sequence(self):
        live_sequence(self)
