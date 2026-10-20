"""T002/V1,V3 actual shipped SDK and custody integration; opt-in live tests fail, not skip.

Run with COHERENCE_LIVE=1, read-only auth/catalog refs and approved cgroup parent.
Offline class checks use the actual provider builder with a zero-send sentinel.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from coherence_workflow.pi_adapter import Decoder, Lifecycle, PiAdapter
from coherence_workflow.sessions import select_session
from coherence_workflow.store import Authority, Blocked, canonical, digest
from coherence_workflow.tools import Gateway, ProcessTool
from fixtures.support import make_project
from fixtures.custody_support import process_tool
from test_custody import IsolatedCustody
from test_sessions import request as session_request, candidate as session_candidate

HOST=Path(__file__).resolve().parents[1]/'pi-host'/'host.mjs'
NODE_TEST=Path(__file__).with_name('test_host.mjs').resolve()


def manifest(project, *, tools=True):
    private=project/'.coherence'/'workflow'/'sdk'
    private.mkdir(parents=True,mode=0o700,exist_ok=True)
    for name in ('agent','sessions','skill'):(private/name).mkdir(mode=0o700,exist_ok=True)
    skill=private/'skill'/'SKILL.md'
    skill.write_text('---\nname: bounded-proof\ndescription: Bounded integration test instructions.\n---\n'
                     'The integration marker is SDK_T002_MARKER. When asked to invoke fixture, call it exactly once with mode quick and exit 0. '
                     'Otherwise reply only SDK_T002_MARKER. Never use any other tool.\n')
    tool=process_tool(project)
    config=dict(sdk_version='0.87.1',cwd=str(project),agent_dir=str(private/'agent'),session_dir=str(private/'sessions'),
       profile=dict(provider='openai-codex',model='gpt-6.1-sol',effort='medium',observer_id='codex-final-payload',observer_version='1'),
       skills=[dict(path=str(skill),sha256=hashlib.sha256(skill.read_bytes()).hexdigest(),name='bounded-proof')],
       tools=[dict(name='fixture',version='1',description='Run the registered bounded fixture only.',parameters=tool.arguments,permission='fixture-test')] if tools else [],
       settings=dict(compaction=dict(enabled=True,reserveTokens=16384,keepRecentTokens=0,
                    modelOverrides={'openai-codex/gpt-6.1-sol':{'reserveTokens':16384}}),
                    retry=dict(enabled=True,maxRetries=1,baseDelayMs=1,provider=dict(maxRetries=0)),cacheWarming='off',transport='sse'),
       trust='explicit-resources-only',permissions=['fixture-test'] if tools else [],
       auth_path=os.environ.get('COHERENCE_AUTH_PATH',''),catalog_path=os.environ.get('COHERENCE_CATALOG_PATH',''),
       system_prompt='You are an isolated integration assistant. Follow the explicitly expanded skill. Do not access other resources.',
       pressure_policy=dict(min_free_tokens_before_compaction=150000,monitor_interval_ms=100))
    config['settings_hash']=digest(config['settings'])
    config['resource_hash']=digest({k:config[k] for k in ('skills','tools','permissions','trust','system_prompt')})
    return config


def environment():
    return {k:v for k,v in os.environ.items() if k in ('PATH','PYTHONPATH','TMPDIR','HOME','PI_OFFLINE','PYTHONDONTWRITEBYTECODE')}


def captured_adapter(case,gateway,*args,**kwargs):
    """Keep every durable fixture scope receipt even if SDK initialization fails."""
    try:
        return PiAdapter(gateway,*args,**kwargs)
    finally:
        for row in gateway.store.db.execute('SELECT containment FROM wf_processes WHERE containment IS NOT NULL'):
            receipt=json.loads(row[0])
            if receipt not in case.receipts:case.receipts.append(receipt)


class BindingTests(IsolatedCustody):
    def adapter(self,a,config=None,node='host',reopen_from=None):
        gateway=self.gateway(a)
        config=config or manifest(self.project)
        adapter=captured_adapter(self,gateway,config,node=node,environment=environment(),
            session_context=dict(role='implement',affinity='story',review_lineage=None),reopen_from=reopen_from)
        row=a.store.db.execute('SELECT containment FROM wf_processes WHERE op_id=?',(adapter.host_op,)).fetchone()
        if json.loads(row[0]) not in self.receipts:self.receipts.append(json.loads(row[0]))
        def emergency_cleanup():
            if not adapter.closed:
                # Fixture failure cleanup can run after its Authority context closed.
                # Kill only the already-captured own-child receipt, never guess a PID.
                self.capability.drain(json.loads(row[0]));adapter.proc.wait(timeout=5)
                if adapter.command_w>=0:os.close(adapter.command_w)
                os.close(adapter.event_r);adapter.selector.close();adapter.closed=True
        self.addCleanup(emergency_cleanup)
        return adapter

    def require_live(self):
        self.assertEqual(os.environ.get('COHERENCE_LIVE'),'1','REQUIRED actual SDK integration not authorized/enabled; NOT VERIFIED')
        for name in ('COHERENCE_AUTH_PATH','COHERENCE_CATALOG_PATH'):
            self.assertTrue(Path(os.environ.get(name,'')).is_file(),name+' unavailable')

    def test_actual_provider_builder_guards_and_sdk_settings(self):
        config=manifest(self.project)
        source=self.project/'.coherence'/'workflow'/'offline-manifest.json';source.write_text(canonical(config))
        env=dict(os.environ,COHERENCE_NODE_FIXTURE=str(self.root),COHERENCE_LIVE='0',COHERENCE_HOST_MANIFEST=str(source))
        proc=subprocess.run(['node','--test',str(NODE_TEST)],env=env,text=True,capture_output=True,timeout=60)
        print(proc.stdout)
        self.assertEqual(proc.returncode,0,proc.stderr+proc.stdout)
        self.assertIn('# tests 5',proc.stdout)

    def test_live_exact_skill_tools_two_turns_and_saved_conversation_open(self):
        self.require_live()
        refs=[Path(os.environ[k]) for k in ('COHERENCE_AUTH_PATH','COHERENCE_CATALOG_PATH')]
        hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in refs]
        with Authority(self.project) as authority:
            config=manifest(self.project)
            adapter=self.adapter(authority,config)
            start=adapter.snapshot
            self.assertEqual(start['runtime'],dict(provider='openai-codex',model='gpt-6.1-sol',effort='medium'))
            self.assertEqual(start['tools'],['fixture'])
            self.assertEqual(start['threshold'],483616)
            one=adapter.prompt(node='one',task_id='one',attempt_id='one',role='implement',text='Invoke fixture exactly once, then reply with the marker.',
                skill='bounded-proof',contract_hash=digest('one'),selection={'reason':'fresh'})
            self.assertIn('SDK_T002_MARKER',one['output'])
            self.assertNotEqual((self.project/'owned.txt').read_text(),'base')
            choice=select_session(session_request(**adapter.compatibility),[session_candidate(id=one['snapshot']['session_id'],telemetry=one['snapshot'],**adapter.compatibility)],
                now_ns=time.time_ns(),max_age_ns=10_000_000_000)
            self.assertEqual(choice['session_id'],one['snapshot']['session_id'])
            two=adapter.prompt(node='two',task_id='two',attempt_id='two',role='implement',text='No tool needed. Reply with the marker only.',
                skill='bounded-proof',contract_hash=digest('two'),selection=choice)
            self.assertIn('SDK_T002_MARKER',two['output'])
            self.assertEqual(one['snapshot']['session_id'],two['snapshot']['session_id'])
            for turn in (one,two):
                self.assertTrue(turn['segment']['elapsed_ns']>0)
                self.assertTrue(all(v['value'] is not None for v in turn['segment']['tokens'].values()))
                self.assertEqual(turn['snapshot']['skills'][0]['sha256'],config['skills'][0]['sha256'])
                self.assertNotEqual(turn['snapshot']['occupancy'],turn['snapshot']['counters']['input'])
            observations=[r['payload'] for r in adapter.records if r['type']=='request_observation']
            self.assertGreaterEqual(len(observations),3)
            self.assertTrue(all(o['model']=='gpt-6.1-sol' and o['wire_effort']=='medium' and o['skill_expanded'] and o['outgoing_tools']==['fixture'] for o in observations))
            final=two['snapshot'];adapter.close()
            session_file=Path(final['session_file'])
            saved=session_file.read_text()
            self.assertIn('<skill',saved)
            self.assertIn('SDK_T002_MARKER',saved)
            config['open']=dict(file=str(session_file),session_id=final['session_id'],leaf=final['leaf'],sha256=hashlib.sha256(session_file.read_bytes()).hexdigest())
            process_count=authority.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0]
            for field,value in [('leaf','wrong'),('sha256','0'*64)]:
                changed=copy.deepcopy(config);changed['open'][field]=value
                with self.assertRaises(Blocked):self.adapter(authority,changed,node='bad-'+field,reopen_from=adapter.host_op)
            with self.assertRaises(Blocked):
                PiAdapter(adapter.gateway,config,node='review-contamination',environment=environment(),
                    session_context=dict(role='review',affinity='story',review_lineage='independent'),reopen_from=adapter.host_op)
            changed=copy.deepcopy(config);changed['permissions'].append('new')
            with self.assertRaises(Blocked):self.adapter(authority,changed,node='resource-drift',reopen_from=adapter.host_op)
            self.assertEqual(authority.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],process_count)
            reopened=self.adapter(authority,config,node='reopened',reopen_from=adapter.host_op)
            self.assertEqual(reopened.snapshot['session_id'],final['session_id'])
            self.assertEqual(reopened.snapshot['leaf'],final['leaf'])
            self.assertNotEqual(reopened.snapshot['epoch'],final['epoch'])
            self.assertEqual(reopened.snapshot['counters'],final['counters'])
            print(canonical({'proof':'actual-two-turn-open','start':start,'one':one['segment'],'two':two['segment'],
                             'observations':observations,'reopened':reopened.snapshot}))
            reopened.close()
        self.assertEqual(hashes,[hashlib.sha256(p.read_bytes()).hexdigest() for p in refs],'shared auth/catalog modified')

    def test_live_actual_shipped_compaction_and_retry(self):
        self.require_live()
        config=manifest(self.project,tools=False)
        source=self.project/'.coherence'/'workflow'/'summary-manifest.json';source.write_text(canonical(config));source.chmod(0o600)
        env=dict(os.environ,COHERENCE_NODE_FIXTURE=str(self.root),COHERENCE_LIVE='1',COHERENCE_HOST_MANIFEST=str(source))
        # No mutating/process tools in the direct module summary fixture. Actual
        # host process/tool containment is separately exercised through PiAdapter.
        proc=subprocess.run(['node','--test',str(NODE_TEST)],env=env,text=True,capture_output=True,timeout=180)
        print(proc.stdout)
        self.assertEqual(proc.returncode,0,proc.stderr+proc.stdout)
        self.assertIn('live-sdk-summary-retry',proc.stdout)


class LeanToolTests(unittest.TestCase):
    def test_scoped_tools_continue_after_safe_error(self):
        from coherence_workflow.pi_adapter import PiAdapter
        tool=ProcessTool('read','1',{},lambda args:['/usr/bin/true'],(),{},
                         lambda args, receipt: (_ for _ in ()).throw(Blocked('authorized read unavailable')))
        output=PiAdapter.tool_output(tool,{}, {'replacement_allowed':True}, 0, 'op')
        self.assertEqual(output['error']['operation'],'tool result read')
        self.assertIn('continue',output['error']['correction'])

    def test_unsettled_effect_blocks_replacement(self):
        # Exercise the actual poll boundary: no tool result is returned and the
        # pending effect remains when the Gateway refuses replacement.
        from types import SimpleNamespace
        adapter=object.__new__(PiAdapter)
        adapter.pending={'call':{'proc':SimpleNamespace(poll=lambda:0),'op':'unsettled',
                                 'tool':SimpleNamespace(result_reader=None),'args':{}}}
        adapter.tool_queue=[];adapter.lifecycle=SimpleNamespace(generation=1)
        adapter.gateway=SimpleNamespace(settle=lambda op, code:{'replacement_allowed':False})
        adapter.send=lambda *args,**kwargs: self.fail('unsettled effect was released to the prompt')
        with self.assertRaisesRegex(Blocked,'ORPHAN_PROCESS'):
            adapter._poll_tools()
        self.assertIn('call',adapter.pending)


class LifecycleTests(IsolatedCustody):
    def test_decoder_bounded_utf8_and_partial_eof(self):
        d=Decoder(8)
        self.assertEqual(d.feed(b'{"a":'),[])
        self.assertEqual(d.feed(b'1}\n'),[{'a':1}])
        d.end()
        with self.assertRaises(Blocked):d.feed(b'x'*9)
        with self.assertRaises(UnicodeDecodeError):Decoder().feed(b'\xff\n')
        d=Decoder();d.feed(b'{')
        with self.assertRaises(Blocked):d.end()

    def test_generation_promise_settled_idle_fence(self):
        life=Lifecycle();life.begin()
        with self.assertRaises(Blocked):life.event({'type':'agent_settled','generation':0})
        life.event({'type':'agent_settled','generation':1})
        self.assertFalse(life.settled)
        life.event({'type':'agent_start','generation':1})
        life.event({'type':'agent_end','generation':1})
        self.assertFalse(life.settled)
        life.event({'type':'auto_retry_start','generation':1})
        life.event({'type':'agent_start','generation':1})
        life.event({'type':'agent_settled','generation':1})
        life.finish({'generation':1,'promise_done':True,'idle':True})
        self.assertFalse(life.active)
        life.begin();life.event({'generation':2,'type':'agent_start'})
        life.event({'generation':2,'type':'agent_settled'})
        life.event({'generation':2,'type':'compaction_start'})
        with self.assertRaises(Blocked):life.finish({'generation':2,'promise_done':True,'idle':True})
        with self.assertRaises(Blocked):life.begin()

    def test_trusted_host_pipes_membership_admission_invalid_fds_and_eof(self):
        with Authority(self.project) as authority:
            gateway=self.gateway(authority)
            script="import os,sys; data=os.read(int(sys.argv[1]),64); os.write(int(sys.argv[2]),data); sys.exit(0 if data else 125)"
            rd,wr=os.pipe();out_r,out_w=os.pipe()
            tool=ProcessTool('pipe','1',{'type':'object','additionalProperties':False},
                lambda args:[str(Path(sys.executable).resolve()),'-c',script,str(rd),str(out_w)],(),environment())
            gateway.tools['pipe']=tool
            try:
                with self.assertRaises(Blocked):gateway.launch('bad-scope','pipe','1',{},scope_kind='unknown')
                with self.assertRaises(Blocked):gateway.launch('bad-fd','pipe','1',{},inherited_fds=(1,))
                with open(self.project/'owned.txt') as f:
                    with self.assertRaises(Blocked):gateway.launch('file-fd','pipe','1',{},inherited_fds=(f.fileno(),))
                op,proc=gateway.launch('host-pipe','pipe','1',{},scope_kind='host',inherited_fds=(rd,out_w))
                row,receipt=gateway._record(op);self.receipts.append(receipt)
                self.assertEqual(row['scope_kind'],'host')
                with self.assertRaises(Blocked):authority.store.assert_dispatchable('run')
                authority.store.assert_dispatchable('run',admitted_host_ops=(op,))
                for ids in [('unknown',),(op,op)]:
                    with self.assertRaises(Blocked):authority.store.assert_dispatchable('run',admitted_host_ops=ids)
                with self.assertRaises(Blocked):authority.store.assert_dispatchable('wrong-run',admitted_host_ops=(op,))
                os.write(wr,b'authenticated-pipe');os.close(wr);wr=-1
                self.assertEqual(os.read(out_r,64),b'authenticated-pipe')
                proc.wait(timeout=5)
                with self.assertRaises(Blocked):authority.store.assert_dispatchable('run',admitted_host_ops=(op,))
                self.assertTrue(gateway.settle(op,proc.returncode)['replacement_allowed'])
                with self.assertRaises(Blocked):authority.store.assert_dispatchable('run',admitted_host_ops=(op,))
                # Real inherited EOF is cancellation, not successful host initialization.
                op2,proc2=gateway.launch('host-eof','pipe','1',{},scope_kind='host',inherited_fds=(rd,out_w))
                self.receipts.append(gateway._record(op2)[1]);self.assertEqual(proc2.wait(timeout=5),125)
                gateway.settle(op2,125)
            finally:
                for fd in (rd,wr,out_r,out_w):
                    if fd>=0:os.close(fd)

    def test_actual_inherited_protocol_nonce_replay_generation_and_sequence_rejection(self):
        for failure in ('initialization','nonce','replay','generation','sequence'):
            project=make_project(self.root/('protocol-'+failure))
            with Authority(project) as authority:
                authority.store.reserve('run','fixture')
                gateway=Gateway(authority,'run',self.parent,{})
                config=manifest(project,tools=False)
                if failure=='initialization':
                    config['sdk_version']='unsupported'
                    with self.assertRaises(Blocked):
                        captured_adapter(self,gateway,config,node='host',environment=environment(),
                            session_context=dict(role='implement',affinity='story',review_lineage=None))
                    self.assertTrue(self.receipts)
                    self.assertEqual(self.capability.populated(self.receipts[-1]),0)
                    continue
                adapter=captured_adapter(self,gateway,config,node='host',environment=environment(),
                    session_context=dict(role='implement',affinity='story',review_lineage=None))
                try:
                    if failure=='replay':
                        command=adapter.send('telemetry',{'generation':0},operation_id=adapter.host_op,attempt_id='offline')
                        adapter.wait_response(command,10)
                        os.write(adapter.command_w,(canonical(adapter.request_bindings[command])+'\n').encode())
                    else:
                        adapter.sequence+=1;command='negative-'+failure
                        record={'protocol_version':1,**adapter.binding,'sequence':adapter.sequence,'command_id':command,
                            'operation_id':adapter.host_op,'attempt_id':'offline','session_id':adapter.session_id,
                            'type':'command','op':'telemetry','payload_schema':'sdk-v1','payload':{'generation':0}}
                        if failure=='nonce':record['nonce']='wrong'
                        if failure=='generation':record['payload']['generation']=1
                        if failure=='sequence':record['sequence']+=1
                        adapter.request_bindings[command]=record
                        os.write(adapter.command_w,(canonical(record)+'\n').encode())
                    with self.assertRaises(Blocked):adapter.wait_response(command,10)
                    self.assertTrue(adapter.lifecycle.poisoned)
                    with self.assertRaises(Blocked):adapter.telemetry()
                finally:adapter.close(force=True)

    def test_host_lifetime_tool_chain_and_negative_receipts(self):
        for failure in (None,'missing_event','tampered_result','unrelated_drift','task_as_host','tampered_identity'):
            with self.subTest(failure=failure):
                project=make_project(self.root/('chain-'+str(failure)))
                with Authority(project) as authority:
                    authority.store.reserve('run','fixture')
                    gateway=Gateway(authority,'run',self.parent,{'fixture':process_tool(project)})
                    rd,wr=os.pipe()
                    gateway.tools['host']=ProcessTool('host','1',{'type':'object','additionalProperties':False},
                        lambda args:[str(Path(sys.executable).resolve()),'-c','import os,sys;os.read(int(sys.argv[1]),1)',str(rd)],(),environment())
                    try:
                        host,hostproc=gateway.launch('host','host','1',{},scope_kind='host',inherited_fds=(rd,))
                        self.receipts.append(gateway._record(host)[1])
                        op,proc=gateway.launch('write','fixture','1',{'mode':'quick','exit':0},admitted_host_ops=(host,))
                        self.receipts.append(gateway._record(op)[1]);proc.wait(timeout=5)
                        if failure=='task_as_host':
                            with self.assertRaises(Blocked):authority.store.assert_dispatchable('run',admitted_host_ops=(host,op))
                        gateway.settle(op,proc.returncode)
                        if failure=='tampered_identity':
                            row=authority.store.db.execute('SELECT identity FROM wf_processes WHERE op_id=?',(host,)).fetchone()
                            identity=json.loads(row[0]);identity['nonce']='forged'
                            authority.store.db.execute('UPDATE wf_processes SET identity=? WHERE op_id=?',(canonical(identity),host))
                            with self.assertRaises(Blocked):authority.store.assert_dispatchable('run',admitted_host_ops=(host,))
                            authority.store.db.execute('UPDATE wf_processes SET identity=? WHERE op_id=?',(row[0],host))
                        if failure=='missing_event':authority.store.db.execute("DELETE FROM wf_events WHERE op_id=? AND kind='completed'",(op,))
                        if failure=='tampered_result':authority.store.db.execute("UPDATE wf_operations SET result='{}' WHERE op_id=?",(op,))
                        if failure=='unrelated_drift':(project/'other.txt').write_text('unexplained')
                        os.write(wr,b'x');hostproc.wait(timeout=5)
                        if failure in ('missing_event','tampered_result','unrelated_drift'):
                            with self.assertRaises(Blocked):gateway.settle(host,0)
                        else:
                            result=gateway.settle(host,0)
                            self.assertEqual(result['task_tool_chain'],[op]);self.assertTrue(result['replacement_allowed'])
                    finally:os.close(rd);os.close(wr)

    def test_live_abort_drain_current_prompt_tool_and_host_death(self):
        self.exercise_live_stop('pressure')

    def test_live_host_death_survivor_alarm_then_gateway_drain(self):
        self.exercise_live_stop('host_death')

    def exercise_live_stop(self,mode):
        self.assertEqual(os.environ.get('COHERENCE_LIVE'),'1','REQUIRED SDK abort integration NOT VERIFIED')
        with Authority(self.project) as authority:
            gateway=self.gateway(authority)
            config=manifest(self.project)
            # The actual model requests quick; trusted fixture maps it to a bounded
            # live mutation loop to exercise SDK abort while a gateway tool is active.
            base=gateway.tools['fixture']
            gateway.tools['fixture']=ProcessTool(base.id,base.version,base.arguments,
                lambda args:base.argv(dict(mode='survivor_hang',exit=0)),base.owned_paths,base.environment)
            adapter=captured_adapter(self,gateway,config,node='abort-host',environment=environment(),
                session_context=dict(role='implement',affinity='story',review_lineage=None))
            try:
                def pressure(a):
                    for pending in a.pending.values():
                        receipt=gateway._record(pending['op'])[1]
                        if receipt not in self.receipts:self.receipts.append(receipt)
                    ready=bool(a.pending) and (self.project/'owned.txt').read_text()!='base'
                    if ready and mode=='host_death':
                        gateway.containment.drain(self.receipts[0]);adapter.proc.wait(timeout=5)
                        for pending in a.pending.values():
                            alarm=gateway.settle(pending['op'],None)
                            self.assertEqual(alarm['alarm'],'ORPHAN_PROCESS')
                            self.assertFalse(alarm['replacement_allowed'])
                        with self.assertRaises(Blocked):authority.store.assert_dispatchable('run')
                    return ready
                with self.assertRaises(Blocked):adapter.prompt(node='interrupted',task_id='interrupted',attempt_id='interrupted',role='implement',
                    text='Invoke fixture exactly once.',skill='bounded-proof',contract_hash=digest('abort'),selection={'reason':'fresh'},interrupt=pressure)
                self.assertGreater(len(self.receipts),1,'actual SDK tool never entered gateway')
                self.assertTrue(adapter.lifecycle.poisoned)
                with self.assertRaises(Blocked):adapter.telemetry()
                for receipt in self.receipts:self.assertEqual(gateway.containment.populated(receipt),1 if mode=='pressure' and receipt==self.receipts[0] else 0)
                if mode=='host_death':
                    alarms=authority.store.db.execute('SELECT state FROM wf_alarms').fetchall()
                    self.assertTrue(alarms);self.assertTrue(all(row['state']=='resolved' for row in alarms))
                    self.assertEqual(authority.store.db.execute("SELECT state FROM wf_runs WHERE run_id='run'").fetchone()[0],'blocked')
                partial=(self.project/'owned.txt').read_bytes();time.sleep(.1)
                self.assertEqual((self.project/'owned.txt').read_bytes(),partial)
                print(canonical({'proof':'actual-sdk-abort-gateway-drain','stop_mode':mode,'events':[
                    {'type':r['type'],'generation':r['payload'].get('generation'),'event':r['payload'].get('type')}
                    for r in adapter.records], 'empty_task_receipts':self.receipts[1:]}))
                # Abrupt host death: no automatic fresh/reuse, validated host drain.
                gateway.containment.drain(self.receipts[0]);adapter.proc.wait(timeout=5)
                with self.assertRaises(Blocked):authority.store.assert_dispatchable('run',admitted_host_ops=(adapter.host_op,))
            finally:adapter.close(force=True)


class ToolBatchTests(IsolatedCustody):
    """Offline real-host/gateway transport tests; no prompt/provider send occurs."""
    def batch_adapter(self,authority):
        gateway=self.gateway(authority)
        arguments={'type':'object','additionalProperties':False,
            'properties':{'path':{'enum':['owned.txt','other.txt']},'padding':{'type':'string','maxLength':65536}},'required':['path']}
        tool=ProcessTool('read_fixture','1',arguments,lambda args:['/usr/bin/sleep','0.15'],(),environment(),
                         lambda args,receipt:(self.project/args['path']).read_text())
        gateway.tools={'read_fixture':tool}
        config=manifest(self.project,tools=False)
        config['tools']=[{'name':tool.id,'version':'1','description':'Offline bounded read fixture.','parameters':arguments,'permission':tool.id}]
        config['permissions']=[tool.id]
        config['resource_hash']=digest({k:config[k] for k in ('skills','tools','permissions','trust','system_prompt')})
        adapter=captured_adapter(self,gateway,config,node='offline-batch-host',environment=environment(),
            session_context={'role':'review','affinity':'offline-batch','review_lineage':'offline-batch'})
        initial_generation=adapter.snapshot['generation']
        op=authority.store.intent('run','offline-batch','sdk-turn',{'contract_hash':digest('offline')},{'fixture':'no provider prompt'})
        adapter.current={'operation_id':op['op_id'],'attempt_id':'offline-batch:0','command_id':'offline-no-send'}
        adapter.lifecycle.begin()
        adapter.lifecycle.event({'generation':adapter.lifecycle.generation,'type':'agent_start'})
        original=adapter.send;adapter.tool_results=[]
        def send(kind,payload,**kwargs):
            if kind=='tool':adapter.tool_results.append(payload);return 'offline-tool-result'
            if kind=='abort':payload={**payload,'generation':initial_generation}
            return original(kind,payload,**kwargs)
        adapter.send=send
        def cleanup():
            try:
                if not adapter.closed:adapter.close(force=True)
            finally:
                for row in authority.store.db.execute('SELECT containment FROM wf_processes WHERE containment IS NOT NULL'):
                    receipt=json.loads(row[0])
                    if receipt not in self.receipts:self.receipts.append(receipt)
        return adapter,cleanup

    def request(self,adapter,call,path='owned.txt',**args):
        return {**adapter.binding,'command_id':adapter.current['command_id'],'operation_id':adapter.current['operation_id'],
                'attempt_id':adapter.current['attempt_id'],'session_id':adapter.session_id,
                'payload':{'call':call,'tool':'read_fixture','version':'1','generation':adapter.lifecycle.generation,
                           'args':{'path':path,**args}}}

    def test_parallel_reads_are_fifo_one_active_process_and_queue_blocks_settlement(self):
        with Authority(self.project) as owner:
            adapter,cleanup=self.batch_adapter(owner)
            try:
                adapter._launch_tool(self.request(adapter,'one','owned.txt'))
                adapter._launch_tool(self.request(adapter,'two','other.txt'))
                self.assertEqual(len(adapter.pending),1);self.assertEqual(len(adapter.tool_queue),1)
                adapter.lifecycle.event({'generation':1,'type':'agent_settled'})
                with self.assertRaisesRegex(Blocked,'pending/queued'):adapter._settle_prompt({'generation':1,'promise_done':True,'idle':True})
                with self.assertRaises(Blocked):adapter.telemetry()
                deadline=time.monotonic()+10
                while adapter.pending or adapter.tool_queue:
                    adapter._poll_tools()
                    active=owner.store.db.execute("SELECT COUNT(*) FROM wf_operations o JOIN wf_processes p USING(op_id) WHERE p.scope_kind='task_tools' AND o.phase!='completed'").fetchone()[0]
                    self.assertLessEqual(active,1)
                    if time.monotonic()>deadline:self.fail('bounded FIFO did not drain')
                    time.sleep(.01)
                self.assertEqual([p['call'] for p in adapter.tool_results],['one','two'])
                self.assertTrue(all(p['result']['details']['quiescent'] for p in adapter.tool_results))
                states=[json.loads(row[0])['state'] for row in owner.store.db.execute("SELECT payload FROM wf_events WHERE kind LIKE 'sdk_tool_%' ORDER BY seq")]
                self.assertEqual(states,['queued','launched','queued','launched'])
                self.assertFalse(any(r['type']=='request_observation' for r in adapter.records))
                self.assertEqual(owner.store.operation(adapter.current['operation_id'])['phase'],'intent')
            finally:cleanup()

    def test_duplicate_stale_wrong_target_version_schema_and_review_mutation_reject(self):
        from dataclasses import replace
        from jsonschema.exceptions import ValidationError
        with Authority(self.project) as owner:
            adapter,cleanup=self.batch_adapter(owner)
            try:
                adapter._launch_tool(self.request(adapter,'one'))
                with self.assertRaisesRegex(Blocked,'duplicate'):adapter._launch_tool(self.request(adapter,'one'))
                for field,value in [('session_id','wrong'),('operation_id','wrong'),('attempt_id','wrong'),('nonce','wrong')]:
                    record=self.request(adapter,'wrong-'+field);record[field]=value
                    with self.assertRaisesRegex(Blocked,'outside current'):adapter._launch_tool(record)
                stale=self.request(adapter,'stale');stale['payload']['generation']=0
                with self.assertRaisesRegex(Blocked,'outside current'):adapter._launch_tool(stale)
                wrong=self.request(adapter,'version');wrong['payload']['version']='2'
                with self.assertRaisesRegex(Blocked,'binding'):adapter._launch_tool(wrong)
                with self.assertRaises(ValidationError):adapter._launch_tool(self.request(adapter,'schema','not-approved'))
                original=adapter.gateway.tools['read_fixture']
                adapter.gateway.tools['read_fixture']=replace(original,owned_paths=('owned.txt',))
                with self.assertRaisesRegex(Blocked,'review tool mutation'):adapter._launch_tool(self.request(adapter,'mutation'))
                adapter.gateway.tools['read_fixture']=original
                self.assertEqual(len(adapter.pending),1);self.assertEqual(adapter.tool_queue,[])
                adapter.abort();self.assertTrue(adapter.lifecycle.poisoned)
                self.assertEqual(owner.store.operation(adapter.current['operation_id'])['phase'],'intent')
            finally:cleanup()

    def test_cancel_receipt_failure_still_drains_active_tools_and_blocks_reuse(self):
        with Authority(self.project) as owner:
            adapter,cleanup=self.batch_adapter(owner)
            try:
                adapter._launch_tool(self.request(adapter,'active'))
                adapter._launch_tool(self.request(adapter,'never-launched'))
                original=adapter._tool_disposition
                def fail_cancel(record,state,**details):
                    if state=='cancelled':raise RuntimeError('fixture-only receipt write failure')
                    return original(record,state,**details)
                adapter._tool_disposition=fail_cancel
                with self.assertRaisesRegex(Blocked,'cancellation receipt unavailable'):adapter.abort()
                self.assertEqual(adapter.pending,{})
                self.assertEqual(adapter.tool_queue,[])
                self.assertTrue(adapter.lifecycle.poisoned)
                rows=owner.store.db.execute("SELECT * FROM wf_processes WHERE scope_kind='task_tools'").fetchall()
                self.assertEqual(len(rows),1)
                self.assertTrue(all(json.loads(row['empty_receipt'])['populated']==0 for row in rows))
                self.assertEqual(owner.store.operation(adapter.current['operation_id'])['phase'],'intent')
            finally:cleanup()

    def test_overflow_blocks_then_abort_cancels_never_launched_requests(self):
        with Authority(self.project) as owner:
            adapter,cleanup=self.batch_adapter(owner)
            try:
                adapter._launch_tool(self.request(adapter,'active'))
                padding='x'*65536
                for index in range(3):adapter._launch_tool(self.request(adapter,'queued-'+str(index),padding=padding))
                self.assertEqual(len(adapter.tool_queue),3)
                with self.assertRaisesRegex(Blocked,'queue byte limit'):adapter._launch_tool(self.request(adapter,'overflow',padding=padding))
                self.assertEqual(len(adapter.tool_queue),3)
                adapter.abort()
                self.assertEqual(adapter.tool_queue,[]);self.assertEqual(adapter.queued_tool_bytes,0);self.assertEqual(adapter.pending,{})
                cancelled=[json.loads(r[0]) for r in owner.store.db.execute("SELECT payload FROM wf_events WHERE kind LIKE 'sdk_tool_cancelled:%'")]
                self.assertEqual(len(cancelled),3)
                self.assertEqual(owner.store.db.execute("SELECT COUNT(*) FROM wf_processes WHERE scope_kind='task_tools'").fetchone()[0],1)
                self.assertEqual(adapter.tool_results,[],'cancelled requests were falsely reported as executed')
                self.assertEqual(owner.store.operation(adapter.current['operation_id'])['phase'],'intent')
                self.assertFalse(any(r['type']=='request_observation' for r in adapter.records))
            finally:cleanup()
