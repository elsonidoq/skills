"""Independent read-only assertions over retained real evidence and scratch files."""
import hashlib
import json
import os
from pathlib import Path
import unittest
from controller import live

LOGS=Path(__file__).resolve().parents[1]/'logs'

class Recorded(unittest.TestCase):
    def test_real_metrics_and_final_payloads(self):
        r=json.loads((LOGS/'results.json').read_text())
        self.assertEqual(len(r['real']),2)
        self.assertEqual(len({t['sessionId'] for t in r['real']}),1)
        for t,text in zip(r['real'],['hello\n','hello world\n']):
            self.assertEqual(t['fileSha256'],hashlib.sha256(text.encode()).hexdigest())
            for key,value in t['delta'].items():
                self.assertEqual(value,t['after']['tokens'][key]-t['before']['tokens'][key])
            self.assertTrue(t['after']['skillMarker'])
            self.assertTrue(t['after']['idle'])
            self.assertEqual(t['after']['headroom'],483616-t['after']['context']['tokens'])
        rows=[json.loads(line) for line in (LOGS/'reuse.jsonl').read_text().splitlines()]
        guards=[x for x in rows if x['type']=='outbound_guard' and not x['synthetic']]
        self.assertEqual(len(guards),4)
        self.assertTrue(all(x['valid'] and x['observed']=={'model':'gpt-6.1-sol','effort':'medium'} for x in guards))
        self.assertEqual(r['synthetic_guard']['sends'],0)
        self.assertFalse(r['synthetic_guard']['forbiddenExists'])
    def test_real_tool_processes_drained(self):
        root=Path(os.environ['RECORDED_ROOT'])
        r=json.loads((LOGS/'results.json').read_text())
        for record in r['interruptions']:
            self.assertTrue(record['replacementAdmitted'])
            self.assertEqual(record['partialBytes'][0],record['partialBytes'][1])
            self.assertEqual(record['liveGroupAfter'],[])
            self.assertTrue(all(not live(p) for p in record['identities']))
            toy=root/record['mode']
            self.assertEqual((toy/'partial.txt').stat().st_size,record['partialBytes'][-1])
            self.assertEqual((toy/'replacement.txt').read_text(),'admitted after reconciliation\n')
        killed=r['interruptions'][1]
        self.assertTrue(killed['orphanLiveAfterHostKill'])
        self.assertGreater(killed['postKillBytes'],killed['initialBytes'])

if __name__=='__main__':unittest.main(verbosity=2)
