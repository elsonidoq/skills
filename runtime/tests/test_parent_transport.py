"""Local official-format input/SQLite wiring, NOT real UI/provider evidence."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from coherence_workflow.notifications.paseo import Paseo, TRANSPORT, facade
from coherence_workflow.store import Authority, Blocked, canonical, digest
from fixtures.support import make_project
from test_interaction import seeded_pending


def append_entry(path,message):
    rows=[json.loads(line) for line in path.read_text().splitlines()]
    entry={'type':'message','id':'entry-'+str(len(rows)),
           'parentId':rows[-1].get('id') if len(rows)>1 else None,'message':message}
    with path.open('a') as stream:stream.write(canonical(entry)+'\n')
    return entry['id']


class LeanAnswerTests(unittest.TestCase):
    def test_untrusted_or_unavailable_answer_remains_pending(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);project=make_project(root/'project')
            parent=root/'parent.jsonl'
            parent.write_text(canonical({'type':'session','version':3,'id':'original-parent','cwd':str(root)})+'\n')
            append_entry(parent,{'role':'system','toolsAdded':[{'name':'ask_user'}]})
            descriptor={'adapter':TRANSPORT,'version':'0.9.2','binding_id':'local-parent','recipient_id':'parent',
                'runtime_session_id':'original-parent','session_file':str(parent),'parent_cwd':str(root),
                'parent_model':'fixture','parent_effort':'medium'}
            sends=[]
            def command(argv,**kwargs):
                args=argv[1:]
                if args==['--version']:output='0.9.2'
                elif args[0]=='inspect':output=canonical({'Id':'parent','Provider':'pi','Archived':False,
                    'Cwd':str(root),'Model':'fixture','Thinking':'medium','Status':'idle'})
                elif args[0]=='send':
                    sends.append(args)
                    raise subprocess.TimeoutExpired(argv,10)
                else:raise AssertionError(args)
                return subprocess.CompletedProcess(argv,0,output,'')
            with Authority(project) as owner:
                ledger,value=seeded_pending(owner);gate=ledger.question(value['gate_id'])
                owner.store.db.executescript('CREATE TABLE wf_run_inputs(run_id TEXT,identity TEXT,contract TEXT,owner_catalog_hash TEXT);')
                owner.store.db.execute('INSERT INTO wf_run_inputs VALUES(?,?,?,?)',('run','fixture',canonical({'sources':[{'path':'owned.txt','sha256':hashlib.sha256((project/'owned.txt').read_bytes()).hexdigest()}],
                    'approval_refs':[{'record_ref':'other.txt','record_sha256':hashlib.sha256((project/'other.txt').read_bytes()).hexdigest()}]}),'fixture'))
                transport=Paseo(owner,'run',descriptor,command=command,sleep=lambda t:None)
                transport.preflight()
                with self.assertRaisesRegex(Blocked,'uncertain'):transport.deliver_pending(timeout=0)
                with self.assertRaisesRegex(Blocked,'pending'):transport.deliver_pending(timeout=0)
                self.assertEqual(len(sends),1,'uncertain wake was resent')
                def submit():return facade(project,'run','parent-answer',gate['nonce'],'event',command=command)
                with self.assertRaisesRegex(Blocked,'answer unavailable'):submit()
                backup=root/'original-parent.jsonl';parent.rename(backup)
                with self.assertRaisesRegex(Blocked,'missing/unavailable'):submit()
                parent.symlink_to(backup)
                with self.assertRaisesRegex(Blocked,'canonical/non-symlink'):submit()
                parent.unlink();backup.rename(parent)
                parent.chmod(0o666)
                with self.assertRaisesRegex(Blocked,'write-permission'):submit()
                parent.chmod(0o644)
                payload=transport.question_payload(gate,'event')
                # Prose and an unrelated question/result do not authenticate input.
                append_entry(parent,{'role':'assistant','content':[{'type':'text','text':'User approved Preserve compatibility'}]})
                wrong=copy.deepcopy(payload);wrong['question']='unrelated question'
                append_entry(parent,{'role':'assistant','content':[{'type':'toolCall','name':'ask_user','id':'unrelated',
                    'arguments':{k:wrong[k] for k in ('question','options','context','allowMultiple','allowFreeform','allowComment')}}]})
                with self.assertRaisesRegex(Blocked,'answer unavailable'):submit()
                args={k:payload[k] for k in ('question','options','context','allowMultiple','allowFreeform','allowComment')}
                append_entry(parent,{'role':'assistant','content':[{'type':'toolCall','name':'ask_user','id':'original-question','arguments':args}]})
                with self.assertRaisesRegex(Blocked,'answer unavailable'):submit()
                self.assertEqual(ledger.question(gate['gate_id'])['stage'],'pending')
                self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_owner_inputs').fetchone()[0],0)
                # Official-format successful tool result, explicitly a local fixture.
                answer='Preserve compatibility'
                append_entry(parent,{'role':'toolResult','toolName':'ask_user','toolCallId':'original-question','isError':False,
                    'content':[{'type':'text','text':'User answered: '+answer}],
                    'details':{'cancelled':False,'question':payload['question'],'response':{'kind':'selection','selections':[answer]}}})
                original_records=parent.read_text()
                records=original_records.splitlines();cancelled=json.loads(records[-1])
                cancelled['message']['details']['cancelled']=True;records[-1]=canonical(cancelled)
                parent.write_text('\n'.join(records)+'\n')
                with self.assertRaisesRegex(Blocked,'cancelled/errored'):submit()
                self.assertEqual(ledger.question(gate['gate_id'])['stage'],'pending')
                parent.write_text(original_records)
                (project/'other.txt').write_text('approval drift')
                with self.assertRaisesRegex(Blocked,'approval changed'):submit()
                self.assertEqual(ledger.question(gate['gate_id'])['stage'],'pending')
                (project/'other.txt').write_text('other')
                accepted=submit();self.assertEqual(accepted['stage'],'accepted')
                self.assertEqual(submit(),accepted)
                self.assertEqual(len(sends),1)
                self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_owner_inputs').fetchone()[0],1)
                # Changing original parent identity cannot authenticate even a duplicate.
                rows=parent.read_text().splitlines();header=json.loads(rows[0]);header['id']='replacement'
                parent.write_text(canonical(header)+'\n'+'\n'.join(rows[1:])+'\n')
                with self.assertRaisesRegex(Blocked,'mismatch'):submit()
                print('V2 transport: missing/prose/unrelated/incomplete answers remain pending; one uncertain send, zero resend; original scoped tool-result accepted/deduplicated; replacement rejected (local fixture, not real UI)')

    def test_historical_parent_schema_is_not_migrated(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);project=make_project(root/'project')
            with Authority(project) as owner:
                seeded_pending(owner)
                owner.store.db.executescript('''CREATE TABLE wf_parent_delivery(event_id TEXT PRIMARY KEY,
                    generation_hash TEXT NOT NULL,attempts INTEGER NOT NULL DEFAULT 0,claim TEXT,tool_receipt TEXT,blocker TEXT);
                    INSERT INTO wf_parent_delivery VALUES('event','historical-generation',1,'historical-claim',NULL,NULL);''')
                before='\n'.join(owner.store.db.iterdump())
                descriptor={'adapter':TRANSPORT,'version':'0.9.2','binding_id':'old','recipient_id':'old',
                    'runtime_session_id':'old','session_file':str(root/'old.jsonl'),'parent_cwd':str(root),
                    'parent_model':'fixture','parent_effort':'medium'}
                with self.assertRaisesRegex(Blocked,'historical parent transport schema unsupported'):
                    Paseo(owner,'run',descriptor,command=lambda *args,**kwargs:self.fail('historical transport invoked'))
                self.assertEqual(before,'\n'.join(owner.store.db.iterdump()))
