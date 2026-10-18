"""Executed acceptance suite. Runtime roots must be new and under ignored scratch."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
import yaml
import harness as h

ROOT=Path(os.environ['POC_ROOT']).resolve()
PYTHON=sys.executable
SCRIPT=str(h.HERE/'harness.py')

class Acceptance(unittest.TestCase):
    def test_00_rpc_settlement_protocol(self):
        # Synthetic wire ordering only; real integration is test_02.
        rpc=h.RPC.__new__(h.RPC);rpc._init_protocol()
        ready=h.threading.Event();done=h.threading.Event();results=[];errors=[]
        class Wire:
            def write(self, line):
                command=json.loads(line)
                if rpc._prompt_number==1:
                    for typ in ['agent_start','agent_end','agent_settled']:
                        rpc._receive({'type':typ})
                    # Fast lifecycle completes BEFORE the authoritative prompt response.
                    rpc._receive({'type':'response','id':command['id'],'success':True})
                else:
                    rpc._receive({'type':'agent_settled'})  # Stale/idle event, no current start.
                    rpc._receive({'type':'response','id':command['id'],'success':True})
                    rpc._receive({'type':'agent_start'})
                    rpc._receive({'type':'agent_end','willRetry':True})
                    ready.set()
            def flush(self):pass
        rpc.p=type('Process',(),{'stdin':Wire()})()
        first=rpc.prompt('fast')
        self.assertTrue(first['settled']);self.assertEqual(first['agent_ends'],1)
        def second_prompt():
            try:results.append(rpc.prompt('retry/compaction'))
            except BaseException as exc:errors.append(str(exc))
            finally:done.set()
        thread=h.threading.Thread(target=second_prompt);thread.start()
        try:
            self.assertTrue(ready.wait(2))
            self.assertFalse(done.wait(.05),'agent_end or stale settlement completed current prompt')
            rpc._receive({'type':'auto_compaction_start'})
            rpc._receive({'type':'auto_compaction_end'})
            rpc._receive({'type':'agent_start'})
            rpc._receive({'type':'agent_end','willRetry':False})
            self.assertFalse(done.wait(.05),'second low-level agent_end completed prompt')
        finally:
            rpc._receive({'type':'agent_settled'})
            thread.join(timeout=2)
        self.assertFalse(thread.is_alive());self.assertEqual(errors,[])
        self.assertEqual(results,[{'prompt_number':2,'agent_starts':2,'agent_ends':2,'settled':True}])
        evidence={'synthetic':True,'fast_settlement_before_response':first,
            'stale_settlement_ignored':True,'agent_end_did_not_complete_prompt':True,'retry_compaction':results[0]}
        (ROOT/'protocol-settlement.json').write_text(json.dumps(evidence,indent=2)+'\n')

    def cli(self,command,root,*args,kill=False):
        p=subprocess.run([PYTHON,SCRIPT,command,'--root',str(root),*args],capture_output=True,text=True)
        if kill:self.assertEqual(p.returncode,-9)
        else:self.assertEqual(p.returncode,0,p.stderr)
        return p.stdout
    def test_01_configuration_and_cutoff(self):
        c=h.load_config(h.HERE/'workflow.yaml')
        self.assertTrue(h.admit(333616,483616))
        self.assertFalse(h.admit(333617,483616))
        self.assertFalse(h.admit(None,483616))
        self.assertFalse(h.admit(1,483616,compatible=False))
        self.assertFalse(h.admit(1,483616,same_group=False))
        self.assertFalse(h.admit(1,483616,ready=False))
        # Synthetic session factory: no real tokens or model call spent on the cutoff.
        current='synthetic-session-1'; fixtures=[]
        for context in [333616,333617,None]:
            selected=current if h.admit(context,483616) else str(h.uuid.uuid4())
            fixtures.append({'context':context,'previous_session':current,'next_session':selected,'reused':selected==current})
        self.assertEqual([f['reused'] for f in fixtures],[True,False,False])
        (ROOT/'cutoff.json').write_text(json.dumps({'synthetic':True,'threshold':483616,'cutoff':150000,'fixtures':fixtures,'unknown':'fresh','incompatible':'fresh','unready':'fresh'}))
        c['nodes']['implement']['profile']='alternate';c['nodes']['implement']['skill']='alternate'
        c['nodes']['implement']['transitions']['success']='END'
        path=ROOT/'variant.yaml';path.write_text(yaml.safe_dump(c));h.load_config(path)
        root=ROOT/'variant';h.init(root)
        e=h.Engine(root,c,synthetic=True);e.execute('variant','var\n')
        events=json.loads((root/'state.json').read_text())['values']['events']
        self.assertEqual([v['node'] for v in events if v['kind']=='node'],['implement'])
        metric=json.loads((root/'state.json').read_text())['values']['metrics'][0]
        self.assertEqual(metric['profile'],'alternate');self.assertIn('TOY_SKILL_B',metric['skill'])
        self.assertEqual(run_git(root,'rev-list','--count','HEAD'),'1')
        bad=yaml.safe_load(path.read_text());bad['nodes']['implement']['handler']='shell'
        path=ROOT/'invalid.yaml';path.write_text(yaml.safe_dump(bad))
        with self.assertRaises(Exception):h.load_config(path)
    def test_02_real_two_tasks(self):
        root=ROOT/'real';h.init(root);c=h.load_config(h.HERE/'workflow.yaml');e=h.Engine(root,c)
        records=[]
        try:
            for task,text in [('t1','hello\n'),('t2','hello world\n')]:
                cfg={'configurable':{'thread_id':task}}
                e.graph.invoke(dict(task=task,text=text,repairs=0,events=[],metrics=[]),cfg,durability='sync')
                status=e.status(task)
                records.extend(e.graph.get_state(cfg).values['metrics'])
                self.assertEqual(status['outcome'],'success')
                (ROOT/f'{task}-state.json').write_text((root/'state.json').read_text())
                print(self.cli('status',root,'--task',task).strip())
            self.assertEqual([r['lifecycle']['prompt_number'] for r in records],[1,2])
            for record in records:
                self.assertTrue(record['lifecycle']['settled'])
                self.assertGreaterEqual(record['lifecycle']['agent_starts'],1)
                self.assertGreaterEqual(record['lifecycle']['agent_ends'],1)
                self.assertGreater(record['token_deltas']['input'],0)
                self.assertEqual(record['token_deltas']['cacheRead'],record['after']['tokens']['cacheRead']-record['before']['tokens']['cacheRead'])
                self.assertEqual(record['headroom_end'],483616-record['context_end'])
            print('REAL METRIC SHAPE',json.dumps(records,indent=2))
            self.assertEqual(records[0]['observed']['sessionId'],records[1]['observed']['sessionId'])
            self.assertIsNotNone(records[0]['observed']['sessionId'])
            self.assertFalse(records[0]['reused']);self.assertTrue(records[1]['reused'])
            self.assertEqual(run_git(root,'rev-list','--count','HEAD'),'3')
            self.assertEqual((root/'toy/unrelated.txt').read_text(),'preserve me\n')
            self.assertNotIn('unrelated.txt',run_git(root,'ls-tree','--name-only','HEAD'))
            self.assertIn('unrelated.txt',run_git(root,'diff','--cached','--name-only'))
            self.assertEqual((root/'toy/seed.txt').read_text(),'unrelated tracked dirt\n')
            messages=e.rpc.request('get_messages')
            # Retain only skill marker presence, never the full model transcript.
            assistant=[m for m in messages['messages'] if m.get('role')=='assistant']
            markers=[block.get('text') for m in assistant for block in m.get('content',[]) if block.get('type')=='text']
            self.assertEqual(markers.count('TOY_SKILL_A'),2)
            (ROOT/'skill-observed.json').write_text(json.dumps({'marker':'TOY_SKILL_A','assistant_responses':markers,'present_in_get_messages':True}))
            (ROOT/'real-metrics.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in records))
        finally:
            if e.rpc:e.rpc.close();e.rpc=None
    def test_03_crashes(self):
        for point in ['file','commit']:
            root=ROOT/f'crash-{point}';h.init(root)
            self.cli('run',root,'--synthetic','--crash',point,kill=True)
            con=h.sqlite3.connect(root/'checkpoints.sqlite')
            self.assertGreater(con.execute('select count(*) from checkpoints').fetchone()[0],0)
            con.close()
            print('KILLED',point,self.cli('status',root).strip())
            print('RESUMED',point,self.cli('run',root,'--synthetic','--resume').strip())
            self.assertEqual(len((root/'synthetic-dispatches.jsonl').read_text().splitlines()),1)
            self.assertEqual(run_git(root,'rev-list','--count','HEAD'),'2')
            self.assertEqual((root/'toy/unrelated.txt').read_text(),'preserve me\n')
            state=json.loads((root/'state.json').read_text())
            self.assertFalse(state['next'])
            (ROOT/f'crash-{point}-state.json').write_text(json.dumps(state,indent=2))
    def test_04_bounded_repair(self):
        root=ROOT/'repair';h.init(root)
        print(self.cli('run',root,'--synthetic','--bad').strip())
        state=json.loads((root/'state.json').read_text())
        self.assertEqual(state['values']['repairs'],1)
        checks=[x['passed'] for x in state['values']['events'] if x['kind']=='required-check']
        self.assertEqual(checks,[False,True])
        self.assertEqual(run_git(root,'rev-list','--count','HEAD'),'2')
        (ROOT/'repair-state.json').write_text(json.dumps(state,indent=2))

def run_git(root,*args):return h.run('git',*args,cwd=root/'toy')

if __name__=='__main__':
    ROOT.mkdir(parents=True,exist_ok=False)
    unittest.main(verbosity=2)
