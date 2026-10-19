"""T007/V1 actual registered parent launch/wake/ask_user/original continuation.

The public client package-root API is TEST-ONLY UI automation. Shipped wake uses
only public Paseo inspect/send. No dummy tool, supervisor transport or manual
polling causes a wake. Standing owner authority permits this exact test answer.
"""
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import sqlite3
import subprocess
import sys
import time
import unittest
import uuid

import yaml

from coherence_workflow.cli import ROOT
from coherence_workflow.intake import approval_scope
from coherence_workflow.store import Authority, Blocked, canonical, digest, git
from coherence_workflow.containment import Cgroup, process_identity
from coherence_workflow.notifications.paseo import Paseo, ParentEvidence, TRANSPORT
from fixtures.support import make_project
from test_intake import approved_fixture, declare_builtin_actions
from test_interaction import question
from test_pi_adapter import manifest


def prepare_live(root, descriptor):
    root=Path(root);root.mkdir(parents=True,mode=0o700)
    (root/'tmp').mkdir(mode=0o700)
    project=make_project(root/'project')
    (project/'.coherence/workflow').mkdir(parents=True,mode=0o700)
    run='parent-'+uuid.uuid4().hex
    config=yaml.safe_load((ROOT/'runtime/coherence_workflow/workflows/coordinate.yaml').read_text())
    config['interaction']={'mode':'interactive_parent','question_transport':TRANSPORT,'parent_binding_ref':descriptor['binding_id'],'question_tool':'ask_user'}
    contract,catalog=approved_fixture(project,digest(config));contract['tasks']=contract['tasks'][:1]
    contract['tasks'][0]['outcome']=(
        'Mandatory isolated parent UI roundtrip test. BEFORE any file mutation, invoke request_owner_input exactly once as the ONLY tool in its batch with this exact JSON: '+canonical(question())+
        '. After a bound_owner_answer in the SAME original conversation, do not reask. If the answer is Preserve compatibility, read owned.txt and write exactly first\\n (f i r s t newline). Otherwise stop blocked. No routine technical/test questions.')
    contract['authorization_envelope']['profiles']=[config['profiles']['sol-medium']]
    declare_builtin_actions(contract)
    for ref in contract['approval_refs']:
        if ref['gate_kind']=='implementation':ref['scope_hash']=approval_scope(contract,digest(config));catalog[ref['authority_ref']]['scope_hash']=ref['scope_hash']
    sdk=manifest(project,tools=False)
    sdk['skills']=[{'path':str(ROOT/'skills/coordinate-implementation/SKILL.md'),'sha256':config['skills']['coordinate']['sha256'],'name':'coordinate-implementation'}]
    sdk['resource_hash']=digest({k:sdk[k] for k in ('skills','tools','permissions','trust','system_prompt')})
    values={'workflow.yaml':yaml.safe_dump(config),'tasks.json':canonical(contract),'catalog.json':canonical(catalog),
            'manifest.json':canonical(sdk),'parent.json':canonical(descriptor)}
    for name,content in values.items():p=root/name;p.write_text(content);p.chmod(0o600)
    args=['start','--project',str(project),'--run',run,'--workflow',str(root/'workflow.yaml'),'--tasks',str(root/'tasks.json'),
          '--owner-catalog',str(root/'catalog.json'),'--manifest',str(root/'manifest.json'),'--containment',os.environ['COHERENCE_TEST_CGROUP_PARENT'],
          '--parent-binding',str(root/'parent.json')]
    env=['env','PYTHONDONTWRITEBYTECODE=1','PI_OFFLINE=1','COHERENCE_LIVE=1','PYTHONPATH='+str(ROOT/'runtime')+':'+str(ROOT/'runtime/tests'),
         'COHERENCE_PYTHON='+sys.executable,'COHERENCE_PARENT_LIVE_ROOT='+str(root),'COHERENCE_TEST_CGROUP_PARENT='+os.environ['COHERENCE_TEST_CGROUP_PARENT'],
         'TMPDIR='+str(root/'tmp')]
    setsid=shutil.which('setsid')
    if not setsid:raise Blocked('isolated controller launch capability setsid unavailable')
    command='set -eu\n'+shlex.join([*env,setsid,sys.executable,'-m','test_interaction_live','--driver','coordinate-implementation',*args])+ ' >'+shlex.quote(str(root/'runner.log'))+' 2>&1 </dev/null &\nprintf \'%s\\n\' '+shlex.quote('COHERENCE_LAUNCH_RECEIPT:'+descriptor['launch_nonce'])
    record={'project':str(project),'run_id':run,'descriptor':descriptor,'launch_command':command,'answer':'Preserve compatibility',
            'source_revision':git(ROOT,'rev-parse','HEAD').decode().strip(),'scope':'standing owner preapproved mandatory isolated test and exact automatic UI answer; not production approval'}
    (root/'fixture.json').write_text(canonical(record));(root/'fixture.json').chmod(0o600)
    return record


def live_start(argv):
    """Trusted test-only injected local command outage, then actual public reconnect."""
    from coherence_workflow.cli import main
    original=Paseo._command;faulted=False
    root=Path(os.environ['COHERENCE_PARENT_LIVE_ROOT'])
    (root/'runner-identity.json').write_text(canonical(process_identity(os.getpid(),'t007-live-controller')))
    def command(self, args):
        nonlocal faulted
        if not faulted and self.ready is not None and args[0]=='inspect':
            faulted=True
            self.attempt('isolated_fault','controlled_command_outage')
            raise Blocked('controlled isolated command outage; next attempt must revalidate actual parent')
        return original(self,args)
    Paseo._command=command
    code=None
    try:code=main(argv)
    finally:
        (root/'done.json').write_text(canonical({'exit_code':code,'controlled_command_outage':faulted,
            'source_revision':git(ROOT,'rev-parse','HEAD').decode().strip()}))
    return code


UI_DRIVER=r'''
import fs from 'node:fs';
import crypto from 'node:crypto';
const spec=JSON.parse(process.argv[2]);
const {createPaseoClient}=await import(spec.module);
const hash=v=>crypto.createHash('sha256').update(v).digest('hex');
const make=()=>createPaseoClient({url:spec.url,clientId:'coherence-t007-ui-'+crypto.randomUUID(),reconnect:{enabled:false},connectTimeoutMs:5000});
function matched(agent) {
 if(agent.id!==spec.agent || agent.cwd!==spec.cwd)throw Error('actual public parent identity mismatch');
 const matches=(agent.pendingPermissions??[]).filter(p=>p.kind==='question' && p.input?.questions?.length===1 &&
  p.input.questions[0].question===spec.question && p.input.questions[0].header==='Response' &&
  JSON.stringify(p.input.questions[0].options.map(o=>o.label))===JSON.stringify(spec.options) && !p.input.questions[0].multiSelect);
 if(matches.length>1)throw Error('ambiguous actual UI request; do not answer');
 return matches[0]??null;
}
let client=make();let permission=null;
try {
 await client.connect();const agent=client.agents.ref(spec.agent);const deadline=Date.now()+90000;
 while(Date.now()<deadline) {
  await agent.refresh();permission=matched(agent);if(permission)break;
  await new Promise(resolve=>setTimeout(resolve,300));
 }
 if(!permission)throw Error('actual bound registered ask_user UI request unavailable');
 const requestId=permission.id;
 // Real public-client disconnect/reconnect at the load-bearing answer seam.
 await client.close();client=make();await client.connect();
 const reopened=client.agents.ref(spec.agent);await reopened.refresh();
 if(matched(reopened)?.id!==requestId)throw Error('UI request changed across reconnect; no response');
 if(!spec.options.includes(spec.answer))throw Error('preapproved test answer not an offered choice');
 await reopened.respondToPermission({requestId,response:{behavior:'allow',updatedInput:{answers:{Response:spec.answer}}}});
 console.log(JSON.stringify({source:'actual public @getpaseo/client 0.9.2 root API',agent_id:spec.agent,
  permission_request_id:requestId,question_hash:hash(spec.question),answer_hash:hash(spec.answer),
  reconnected_and_revalidated:true,scope:'exact standing-authorized isolated test request only; no --all or fabricated user event'}));
} finally {await client.close();}
'''


def public_ui_spec(record, prompt, context, options):
    binary=Path(shutil.which('paseo') or '').resolve(strict=True)
    cli=next((p for p in binary.parents if (p/'package.json').is_file() and json.loads((p/'package.json').read_text()).get('name')=='@getpaseo/cli'),None)
    if cli is None:raise Blocked('installed public Paseo client package location unavailable')
    package=cli/'node_modules/@getpaseo/client/package.json';metadata=json.loads(package.read_text())
    if metadata['version']!='0.9.2':raise Blocked('unsupported UI test client version')
    module=(package.parent/metadata['exports']['.']['default']).resolve(strict=True)
    status=json.loads(subprocess.check_output(['paseo','status','--json'],text=True))
    if status.get('daemonVersion')!='0.9.2':raise Blocked('actual local daemon version mismatch')
    host,port=status['listen'].rsplit(':',1)
    if host not in ('0.0.0.0','127.0.0.1','localhost'):raise Blocked('unsupported test-only public local WebSocket endpoint')
    d=record['descriptor']
    return {'module':module.as_uri(),'url':'ws://127.0.0.1:'+port+'/ws','agent':d['recipient_id'],'cwd':d['parent_cwd'],
            'question':prompt+'\n\nContext:\n'+context,'options':options,'answer':record['answer']}


class ParentRoundtripTests(unittest.TestCase):
    def test_actual_registered_parent_wake_tool_answer_original_continuation_and_reconnect(self):
        self.assertEqual(os.environ.get('COHERENCE_LIVE'),'1','NOT VERIFIED: actual parent test not enabled')
        root=Path(os.environ.get('COHERENCE_PARENT_LIVE_ROOT','')).resolve(strict=True)
        self.assertTrue(root.is_relative_to(ROOT/'.pi/workflow-validation/implementation/t007'),'explicit current owned live fixture required')
        record=json.loads((root/'fixture.json').read_text());project=Path(record['project']);database=project/'.coherence/workflow/workflow.sqlite'
        ui=None;deadline=time.monotonic()+240
        try:
            while time.monotonic()<deadline and not (root/'done.json').exists():
                if database.is_file() and ui is None:
                    db=sqlite3.connect(database.as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
                    try:
                        if db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_outbox'").fetchone():
                            gate=db.execute("SELECT q.*,o.event_id FROM wf_questions q JOIN wf_outbox o USING(gate_id) JOIN wf_question_parks p USING(gate_id) WHERE q.stage='pending'").fetchone()
                            if gate:
                                request=json.loads(gate['request'])
                                prompt=request['question']+'\n[workflow '+record['run_id']+' event '+gate['event_id']+' nonce '+gate['nonce']+']'
                                context=canonical({k:request[k] for k in ('why_owner_needed','recommendation','impact')})
                                spec=public_ui_spec(record,prompt,context,request['options'])
                                driver=root/'ui-client.mjs';driver.write_text(UI_DRIVER)
                                # Polling is ONLY test UI response driving after SQL+graph
                                # park. The shipped adapter already causes the actual wake.
                                ui=subprocess.run(['node',str(driver),canonical(spec)],capture_output=True,text=True,timeout=110)
                                (root/'ui-driver-output.log').write_text(ui.stdout+ui.stderr)
                                self.assertEqual(ui.returncode,0,ui.stdout+ui.stderr)
                    finally:db.close()
                time.sleep(.2)
            self.assertTrue((root/'done.json').exists(),'actual runner not settled; inspect retained fixture, never blindly relaunch')
            done=json.loads((root/'done.json').read_text())
            self.assertEqual(done['exit_code'],0,(root/'runner.log').read_text()[-10000:])
            self.assertTrue(done['controlled_command_outage'])
            self.assertIsNotNone(ui,'no actual UI request was exercised')
            ui_receipt=json.loads(ui.stdout);self.assertTrue(ui_receipt['reconnected_and_revalidated'])
            db=sqlite3.connect(database.as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
            try:
                preflight=db.execute('SELECT * FROM wf_parent_preflight').fetchone()
                self.assertEqual(preflight['stage'],'ready')
                launch=json.loads(preflight['launch_receipt']);ready=json.loads(preflight['ready_receipt'])
                gate=db.execute('SELECT * FROM wf_questions').fetchone();self.assertEqual(gate['stage'],'continued')
                owner=db.execute('SELECT * FROM wf_owner_inputs').fetchone();value=json.loads(owner['payload'])
                self.assertEqual(value['receipt']['source'],'parent_ask_user')
                self.assertEqual(value['answer'],record['answer'])
                outbox=db.execute('SELECT * FROM wf_outbox').fetchone();self.assertEqual(outbox['stage'],'answered')
                tool=json.loads(db.execute('SELECT tool_receipt FROM wf_parent_delivery').fetchone()[0])
                self.assertEqual(tool['tool'],'ask_user');self.assertTrue(tool['result_entry'])
                evidence=ParentEvidence(record['descriptor']);self.assertEqual(evidence.header['id'],record['descriptor']['runtime_session_id'])
                turns=[json.loads(r[0]) for r in db.execute("SELECT result FROM wf_operations WHERE kind='sdk-turn' ORDER BY rowid")]
                self.assertEqual(turns[0]['after']['session_id'],turns[1]['before']['session_id'])
                self.assertNotEqual(turns[0]['host_op'],turns[1]['host_op'])
                self.assertEqual(turns[1]['selection']['reason'],'original_question_pin')
                events=[dict(r) for r in db.execute('SELECT seq,kind,payload FROM wf_events ORDER BY seq')]
                def seq(kind):return next(e['seq'] for e in events if e['kind']==kind)
                self.assertLess(seq('question_pending'),seq('question_graph_parked'))
                self.assertLess(seq('question_graph_parked'),seq('parent_transport_queued'))
                self.assertLess(seq('parent_transport_queued'),seq('parent_received'))
                self.assertLess(seq('parent_received'),seq('parent_question_tool_invoked'))
                self.assertLess(seq('parent_question_tool_invoked'),seq('owner_answer_accepted'))
                self.assertLess(seq('owner_answer_accepted'),seq('original_answer_entry'))
                next_requests=[e['seq'] for e in events if e['kind'].startswith('sdk:') and json.loads(e['payload']).get('wire_effort') and e['seq']>seq('original_answer_entry')]
                self.assertTrue(next_requests)
                self.assertEqual(db.execute('SELECT COUNT(*) FROM wf_owner_inputs').fetchone()[0],1)
                attempts=[dict(r) for r in db.execute('SELECT * FROM wf_parent_attempts ORDER BY seq')]
                self.assertTrue(any(a['outcome']=='controlled_command_outage' for a in attempts))
                self.assertTrue(any(a['outcome']=='transport_queued' and a['event_id'] for a in attempts))
                self.assertEqual(project.joinpath('owned.txt').read_text(),'first\n')
                self.assertEqual(db.execute('SELECT state FROM wf_runs').fetchone()[0],'accepted')
                proof={'items':['T007/V1','T007/V2','T007/V3'],'source_revision':done['source_revision'],
                    'actual_parent_session':record['descriptor']['runtime_session_id'],'actual_recipient':record['descriptor']['recipient_id'],
                    'launch':launch,'ready':ready,'actual_ask_user':tool,'public_ui_response':ui_receipt,
                    'original_worker_session':turns[0]['after']['session_id'],'answer_before_request':True,
                    'stages':[(e['seq'],e['kind']) for e in events if e['kind'] in ('question_pending','question_graph_parked','parent_transport_queued','parent_received','parent_question_tool_invoked','owner_answer_accepted','original_answer_entry')],
                    'attempts':attempts,'scope':'actual shipped runner/parent tools/public UI; automatic test answer under genuine standing preapproval, not a human click',
                    'active_controls':'reuse T006 actual CLI/SDK plain steer/followUp/public ACK proof; unchanged host/adapter/control consumer'}
                (root/'proof.json').write_text(canonical(proof));print(canonical(proof))
            finally:db.close()
        finally:
            # Retain this whole known-owned fixture for audit/recovery. Cleanup
            # only receipt-validated empty scopes after controller completion.
            if (root/'done.json').exists() and database.is_file():
                db=sqlite3.connect(database.as_uri()+'?mode=ro',uri=True)
                try:
                    for row in db.execute('SELECT containment FROM wf_processes WHERE containment IS NOT NULL'):
                        receipt=json.loads(row[0]);capability=Cgroup(receipt['parent'])
                        if (Path(receipt['parent'])/receipt['name']).exists():
                            self.assertEqual(capability.populated(receipt),0,'live task scope retained; do not invent quiescence')
                            capability.remove(receipt)
                finally:db.close()


if __name__=='__main__':
    if sys.argv[1:3]!=['--driver','coordinate-implementation']:raise SystemExit('explicit isolated driver invocation required')
    raise SystemExit(live_start(sys.argv[3:]))
