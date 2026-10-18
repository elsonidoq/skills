"""Source-named assertions; synthetic negatives are separate from actual integration evidence."""
import json
import os
from unittest.mock import patch
from pathlib import Path
import subprocess
import sys
import unittest
from notify import DATA as LIVE_DATA, HASH, notify
DATA = Path(os.environ.get('POC_EVIDENCE_DIR', LIVE_DATA))
from runner import policy, preflight, validate_binding, relay

class PolicyTests(unittest.TestCase):
    def test_optional_ui_failure_does_not_decide_workflow_state(self):
        with patch('runner.notify',side_effect=RuntimeError('synthetic absent UI')), patch('runner.log') as log:
            relay('question',2,'original','nonce',HASH)
            self.assertEqual(log.call_args.args[0]['type'],'notification_unavailable')
            self.assertTrue(log.call_args.args[0]['durable'])
    def test_reproduction_cannot_notify_old_parent_by_default(self):
        with patch.dict(os.environ, {'POC_ALLOW_NOTIFY_AGENT':''}), patch('notify.subprocess.check_output') as inspect:
            with self.assertRaises(RuntimeError):notify('bridge_probe',1,'bridge-preflight')
            inspect.assert_not_called()
    def test_request_owner_input_category(self):
        self.assertTrue(policy('product','cosmetic label',['Release note','Progress note'],'no scope change'))
        self.assertFalse(policy('technical','how to test',['Release note','Progress note'],'approved'))
        self.assertFalse(policy('scope-change','add feature',['Release note','Progress note'],'new scope'))
    def test_preflight_before_dispatch(self):
        for permission,approval in [(False,True),(True,False)]:
            with self.assertRaises(ValueError):preflight(permission,approval)
    def test_wrong_stale_original_binding(self):
        gate=dict(session='original',nonce='right',sourceHash=HASH)
        for s,n,h in [('wrong','right',HASH),('original','wrong',HASH),('original','right','0'*64)]:
            with self.assertRaises(ValueError):validate_binding(gate,s,n,h)

class RecordedIntegrationTests(unittest.TestCase):
    def test_original_session_reentry_and_acknowledgement(self):
        rows=[json.loads(l) for l in (DATA/'events.jsonl').read_text().splitlines()]
        settled=[r for r in rows if r['type']=='settled']
        self.assertEqual(len(settled),2)
        self.assertEqual(settled[0]['session'],settled[1]['session'])
        self.assertTrue(all(r['idle'] for r in settled))
        self.assertEqual(settled[0]['stopReason'],'toolUse')
        reopened=[r for r in rows if r['type']=='opened' and r['reopened']]
        self.assertEqual(len(reopened),1)
        self.assertNotEqual(reopened[0]['pid'],next(r['pid'] for r in rows if r['type']=='opened'))
        self.assertGreater(reopened[0]['storedMessages'],0)
        self.assertTrue(settled[1]['answerInConversation'])
        self.assertTrue(settled[1]['steerInConversation'])
        order=[r['type'] for r in rows]
        markers=['durable_pending','answer_accepted','active_ready','steer_queued','steer_enqueued','worker_acknowledged','workflow_done']
        self.assertEqual(sorted(markers,key=order.index),markers)
        self.assertEqual(sum(r['type']=='worker_acknowledged' for r in rows),1)
        answer=json.loads((DATA/'answer.json').read_text())
        output=(DATA/'toy-note.txt').read_text()
        self.assertTrue(output.startswith(answer['choice']+'\n'))
        self.assertIn('Steering received.',output)
        self.assertTrue(answer['reference'])
        for r in rows:
            if r['type']=='outbound_guard':
                self.assertEqual((r['model'],r['effort']),('gpt-6.1-sol','medium'))
    def test_real_duplicate_wrong_stale_input_no_new_worker(self):
        if os.environ.get('POC_EVIDENCE_DIR'):
            record=json.loads((DATA/'negative-inputs.json').read_text())
            self.assertTrue(record['realCli'])
            self.assertTrue(record['eventLedgerUnchanged'])
            self.assertEqual(len(record['cases']),4)
            self.assertTrue(all(c['returncode']!=0 and 'REJECT' in c['rejection'] for c in record['cases']))
            return
        gate=json.loads((DATA/'binding.json').read_text())
        base=[sys.executable,str(Path(__file__).with_name('runner.py')),'answer','--session',gate['session'],'--nonce',gate['nonce'],'--source-hash',HASH,
              '--parent',gate['parent'],'--choice','Release note','--reference','negative-only-not-accepted']
        before=(DATA/'events.jsonl').read_bytes()
        for change in [None,('--nonce','0'*32),('--session','wrong'),('--source-hash','0'*64)]:
            cmd=base.copy()
            if change:cmd[cmd.index(change[0])+1]=change[1]
            result=subprocess.run(cmd,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('REJECT',result.stderr)
        self.assertEqual(before,(DATA/'events.jsonl').read_bytes())

if __name__=='__main__':unittest.main()
