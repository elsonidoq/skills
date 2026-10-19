"""Runner-owned question/input ledger. A nonce binds input; it never authenticates it.

The trusted caller verifies owner provenance through the external operator channel.
No method in this module selects a task, model, recipient or replacement conversation.
"""
import copy
import json
import uuid
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from jsonschema import Draft202012Validator

from .registry import schemas, validate_schema
from .store import Blocked, Store, canonical, digest, private_file, safe_path


QUESTION_SCHEMA = schemas()['interaction.schema.json']['$defs']['request']


def validate_question(request):
    """Structural/rationale assistance, NOT a universal semantic necessity oracle."""
    Draft202012Validator(QUESTION_SCHEMA).validate(request)
    if len(canonical(request).encode()) > 16384:
        raise Blocked('question byte limit')
    if request['recommendation'] not in request['options']:
        raise Blocked('question recommendation must identify an offered option')
    return copy.deepcopy(request)


class Interaction:
    def __init__(self, store, run, *, initialize=True, authorize_request=None, require_authorization=False):
        self.store, self.run = store, run
        self.authorize_request = authorize_request
        self.require_authorization = require_authorization
        if not initialize:
            return
        store.db.executescript('''
        CREATE TABLE IF NOT EXISTS wf_questions(
          gate_id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES wf_runs,
          turn_op TEXT NOT NULL UNIQUE REFERENCES wf_operations,
          call_id TEXT NOT NULL, binding TEXT NOT NULL, nonce TEXT NOT NULL UNIQUE,
          request TEXT NOT NULL, stage TEXT NOT NULL,
          pin TEXT, proof TEXT, UNIQUE(run_id,call_id));
        CREATE UNIQUE INDEX IF NOT EXISTS wf_one_question ON wf_questions(run_id)
          WHERE stage IN ('parking','pending','answered','delivering');
        CREATE TABLE IF NOT EXISTS wf_question_parks(
          gate_id TEXT PRIMARY KEY REFERENCES wf_questions, checkpoint_id TEXT NOT NULL,
          node_id TEXT NOT NULL, original_graph_op TEXT NOT NULL REFERENCES wf_operations);
        CREATE TABLE IF NOT EXISTS wf_owner_inputs(
          input_id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES wf_runs,
          gate_id TEXT REFERENCES wf_questions, input_hash TEXT NOT NULL,
          payload TEXT NOT NULL, stage TEXT NOT NULL, receipt TEXT);
        CREATE UNIQUE INDEX IF NOT EXISTS wf_one_answer ON wf_owner_inputs(gate_id)
          WHERE gate_id IS NOT NULL;
        CREATE TABLE IF NOT EXISTS wf_controls(
          input_id TEXT PRIMARY KEY REFERENCES wf_owner_inputs, binding TEXT NOT NULL,
          action TEXT NOT NULL, scope TEXT NOT NULL, message TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS wf_run_bindings(
          run_id TEXT PRIMARY KEY REFERENCES wf_runs, binding TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS wf_active_targets(
          run_id TEXT PRIMARY KEY REFERENCES wf_runs, binding TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS wf_outbox(
          event_id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES wf_runs,
          gate_id TEXT NOT NULL UNIQUE REFERENCES wf_questions,
          stage TEXT NOT NULL, receipt TEXT);
        ''')

    def question(self, gate):
        row = self.store.db.execute('SELECT * FROM wf_questions WHERE run_id=? AND gate_id=?',
                                    (self.run, gate)).fetchone()
        if not row:
            raise Blocked('unknown question')
        return dict(row)

    def pending(self):
        return [dict(row) for row in self.store.db.execute(
            "SELECT * FROM wf_questions WHERE run_id=? AND stage NOT IN ('continued','cancelled') ORDER BY rowid",
            (self.run,))]

    def request(self, turn_op, call, binding, request, *, batch):
        """Persist intent before returning a normal terminating SDK tool result.

        Only an observed exclusive batch is supported. Unknown/mixed batches fail
        closed even when the question happens to be the first completed tool.
        """
        if self.require_authorization and self.authorize_request is None:raise Blocked('question action authority unavailable')
        if self.authorize_request is not None:self.authorize_request(binding)
        validate_question(request)
        if batch != [{'call': call, 'tool': 'request_owner_input'}]:
            raise Blocked('question requires observed exclusive terminating batch')
        operation = self.store.operation(turn_op)
        if operation['run_id'] != self.run or operation['kind'] != 'sdk-turn' or operation['phase'] != 'intent':
            raise Blocked('question outside active SDK turn')
        # Binding only references primitive definitions from shared.schema.json.
        sample = {'schema_version': 1, 'kind': 'owner_question', 'binding': binding,
                  'gate_id': 'validate', 'nonce': 'validate', 'pin_policy': 'original_only',
                  'original_session_ref': 'validate', 'original_branch_ref': 'validate',
                  'request': request, 'stage': 'parking', 'park_proof_ref': None, 'blocker': None}
        validate_schema('interaction.schema.json', sample)
        turn=json.loads(operation['intent'])
        if (binding['run_id'] != self.run or any(binding[k]!=turn.get(k) for k in ('task_id','attempt_id','role')) or
                binding['session_id']!=turn.get('before',{}).get('session_id')):
            raise Blocked('question run/task/attempt/role/session mismatch')
        with self.store.transaction() as db:
            old = db.execute('SELECT * FROM wf_questions WHERE turn_op=?', (turn_op,)).fetchone()
            if old:
                if old['call_id'] != call or old['binding'] != canonical(binding) or old['request'] != canonical(request):
                    raise Blocked('question identity conflict')
                return {'gate_id': old['gate_id'], 'terminate': True}
            gate, nonce = uuid.uuid4().hex, uuid.uuid4().hex
            db.execute("INSERT INTO wf_questions VALUES(?,?,?,?,?,?,?,'parking',NULL,NULL)",
                       (gate, self.run, turn_op, call, canonical(binding), nonce, canonical(request)))
            self.store.event(db, self.run, None, 'question_requested',
                             {'gate_id': gate, 'turn_op': turn_op, 'binding': binding, 'request': request})
        return {'gate_id': gate, 'terminate': True}

    def settled(self, gate, *, pin, proof):
        """Admission requires actual current SDK/app/process receipts, not booleans."""
        question = self.question(gate)
        operation = self.store.operation(question['turn_op'])
        if operation['phase'] != 'completed' or not operation['result']:
            raise Blocked('question SDK turn not durably settled')
        result = json.loads(operation['result'])
        if result['after'] != pin['snapshot'] or result['host_op'] != pin['host_op']:
            raise Blocked('question original snapshot/host mismatch')
        if pin['snapshot']['session_id'] != json.loads(question['binding'])['session_id']:
            raise Blocked('question original session mismatch')
        events = [json.loads(r[0]) for r in self.store.db.execute(
            "SELECT payload FROM wf_events WHERE op_id=? AND kind LIKE 'sdk:%' ORDER BY seq", (operation['op_id'],))]
        types = [e.get('type') for e in events]
        if 'tool_execution_end' not in types or 'agent_settled' not in types or types.index('tool_execution_end') >= types.index('agent_settled'):
            raise Blocked('question normal tool completion/current settlement proof missing')
        if proof != {'turn_op': operation['op_id'], 'snapshot_hash': digest(pin['snapshot'])}:
            raise Blocked('question settlement receipt mismatch')
        # Independently reject live/unknown task scopes and host custody. The
        # adapter must already have closed and reconciled the original host.
        self.store.assert_dispatchable(self.run)
        host = self.store.operation(pin['host_op'])
        if host['phase'] != 'completed' or not json.loads(host['result']).get('replacement_allowed'):
            raise Blocked('question host not closed/reconciled')
        with self.store.transaction() as db:
            current = self.question(gate)
            if current['stage'] == 'pending':
                if current['pin'] != canonical(pin) or current['proof'] != canonical(proof):
                    raise Blocked('question pending proof drift')
                return current
            if current['stage'] != 'parking':
                raise Blocked('question is not parking')
            db.execute("UPDATE wf_questions SET stage='pending',pin=?,proof=? WHERE gate_id=? AND stage='parking'",
                       (canonical(pin), canonical(proof), gate))
            db.execute("INSERT INTO wf_outbox VALUES(?,?,?,'recorded',NULL)", (uuid.uuid4().hex, self.run, gate))
            db.execute("UPDATE wf_runs SET state='waiting_owner_input' WHERE run_id=?", (self.run,))
            self.store.event(db, self.run, None, 'question_pending', {'gate_id': gate, 'proof': proof})
        return self.question(gate)

    def answer(self, value, *, verify_owner, current_binding):
        """Verify external genuine input before UNIQUE/CAS acceptance; never dispatch."""
        validate_schema('interaction.schema.json', value)
        if value['kind'] != 'owner_answer' or value['delivery'] != 'accepted' or value['delivery_ref'] is not None:
            raise Blocked('answer must enter at accepted stage')
        if len(value['answer'].encode()) > 16384:
            raise Blocked('answer byte limit')
        authority = verify_owner(value)
        identity = digest(value)
        if authority != {'input_hash':identity,'scope':'within_envelope'}:
            raise Blocked('scope-changing/unverified input requires producing approval renewal')
        with self.store.transaction() as db:
            old = db.execute('SELECT * FROM wf_owner_inputs WHERE input_id=?', (value['input_id'],)).fetchone()
            if old:
                if old['run_id'] != self.run or old['input_hash'] != identity:
                    raise Blocked('conflicting duplicate input')
                return dict(old)
            gate = self.question(value['gate_id'])
            if not db.execute('SELECT 1 FROM wf_question_parks WHERE gate_id=?',(gate['gate_id'],)).fetchone():
                raise Blocked('question graph park reconciliation required before answer')
            pin = json.loads(gate['pin']) if gate['pin'] else {}
            if (gate['stage'] != 'pending' or value['nonce'] != gate['nonce'] or
                    value['binding'] != json.loads(gate['binding']) or value['binding'] != current_binding or
                    value['original_session_ref'] != pin.get('snapshot', {}).get('session_file')):
                raise Blocked('stale/wrong answer binding or original pin')
            db.execute("INSERT INTO wf_owner_inputs VALUES(?,?,?,?,?,'accepted',NULL)",
                       (value['input_id'], self.run, gate['gate_id'], identity, canonical(value)))
            changed = db.execute("UPDATE wf_questions SET stage='answered' WHERE gate_id=? AND stage='pending'", (gate['gate_id'],))
            if changed.rowcount != 1:
                raise Blocked('answer compare-and-set conflict')
            db.execute("UPDATE wf_outbox SET stage='answered' WHERE gate_id=?", (gate['gate_id'],))
            self.store.event(db, self.run, None, 'owner_answer_accepted',
                             {'gate_id': gate['gate_id'], 'input_id': value['input_id'], 'input_hash': identity})
        return dict(self.store.db.execute('SELECT * FROM wf_owner_inputs WHERE input_id=?', (value['input_id'],)).fetchone())

    def delivery_intent(self, gate):
        """Uncertain delivery remains blocked until original entry reconciliation."""
        with self.store.transaction() as db:
            question = self.question(gate)
            row = db.execute('SELECT * FROM wf_owner_inputs WHERE gate_id=?', (gate,)).fetchone()
            if question['stage'] != 'answered' or not row or row['stage'] != 'accepted':
                raise Blocked('answer delivery uncertain/already attempted; reconcile original entry before resend')
            db.execute("UPDATE wf_owner_inputs SET stage='queued_original' WHERE input_id=? AND stage='accepted'", (row['input_id'],))
            db.execute("UPDATE wf_questions SET stage='delivering' WHERE gate_id=?", (gate,))
            self.store.event(db, self.run, None, 'answer_delivery_intent', {'gate_id': gate, 'input_id': row['input_id']})
        return json.loads(row['payload'])

    def control(self, value, *, verify_owner, current_binding):
        validate_schema('interaction.schema.json',value)
        if value['kind']=='owner_control' and value['scope']=='requires_approval':
            raise Blocked('out-of-envelope control requires producing approval renewal')
        if value['kind']!='owner_control' or value['stage']!='received' or value['evidence_ref'] is not None:
            raise Blocked('control must enter at received stage')
        authority=verify_owner(value)
        identity=digest(value)
        if authority != {'input_hash':identity,'scope':'within_envelope'} or value['scope']!='within_envelope':
            raise Blocked('out-of-envelope control requires producing approval renewal')
        with self.store.transaction() as db:
            old=db.execute('SELECT * FROM wf_owner_inputs WHERE input_id=?',(value['input_id'],)).fetchone()
            if old:
                if old['run_id']!=self.run or old['input_hash']!=identity:raise Blocked('conflicting duplicate control')
                return dict(old)
            if value['binding']!=current_binding or value['binding']['run_id']!=self.run:
                raise Blocked('stale/wrong control target')
            active=db.execute('SELECT binding FROM wf_active_targets WHERE run_id=?',(self.run,)).fetchone()
            worker=value['target_scope']=='active_session'
            if worker and (not active or json.loads(active[0])!=value['binding']):
                raise Blocked('active control target changed')
            if worker and db.execute("SELECT 1 FROM wf_questions WHERE run_id=? AND stage IN ('parking','pending','answered','delivering')",(self.run,)).fetchone():
                raise Blocked('pending original question pin cannot be bypassed by control')
            if not worker and any(value['binding'][k] is not None for k in ('task_id','node_id','attempt_id','session_id','role','task_hash')):
                raise Blocked('idle run control must have null worker fields')
            db.execute("INSERT INTO wf_owner_inputs VALUES(?,?,NULL,?,?,'received',NULL)",
                       (value['input_id'],self.run,identity,canonical(value)))
            db.execute('INSERT INTO wf_controls VALUES(?,?,?,?,?)',(value['input_id'],canonical(value['binding']),value['action'],value['scope'],value['message']))
            self.store.event(db,self.run,None,'control_received',{'input_id':value['input_id'],'binding':value['binding'],'action':value['action']})
        return dict(self.store.db.execute('SELECT * FROM wf_owner_inputs WHERE input_id=?',(value['input_id'],)).fetchone())

    def control_stage(self, input_id, before, after, evidence=None):
        allowed={('received','queued'),('queued','sdk_delivered'),('sdk_delivered','worker_acknowledged'),
                 ('received','reconciled'),('queued','reconciled'),('received','blocked'),('queued','blocked')}
        if (before,after) not in allowed or after in ('sdk_delivered','worker_acknowledged','reconciled') and not evidence:
            raise Blocked('invalid control stage/evidence')
        with self.store.transaction() as db:
            row=db.execute('SELECT i.* FROM wf_owner_inputs i JOIN wf_controls c USING(input_id) WHERE i.input_id=? AND i.run_id=?',(input_id,self.run)).fetchone()
            if not row:raise Blocked('unknown control')
            cur=db.execute('UPDATE wf_owner_inputs SET stage=?,receipt=? WHERE input_id=? AND stage=?',
                           (after,canonical(evidence) if evidence else None,input_id,before))
            if cur.rowcount!=1:raise Blocked('control stage compare-and-set failed')
            self.store.event(db,self.run,None,'control_'+after,{'input_id':input_id,'evidence':evidence})

    def delivered(self, gate, receipt):
        with self.store.transaction() as db:
            question = self.question(gate)
            row = db.execute('SELECT * FROM wf_owner_inputs WHERE gate_id=?', (gate,)).fetchone()
            if (not row or question['stage'] != 'delivering' or row['stage'] != 'queued_original' or
                    receipt.get('input_id') != row['input_id'] or not receipt.get('entry_id') or
                    receipt.get('session_id') != json.loads(question['binding'])['session_id']):
                raise Blocked('original answer entry receipt mismatch')
            db.execute("UPDATE wf_owner_inputs SET stage='sdk_delivered',receipt=? WHERE input_id=?",
                       (canonical(receipt), row['input_id']))
            self.store.event(db, self.run, None, 'original_answer_entry', receipt)
        return receipt


class OwnerChannel:
    """Bounded owner-input SQL channel, usable while the execution lock is held.

    It cannot dispatch, release custody, run graph nodes or change configuration.
    SQLite serializes short input transactions with the sole execution controller.
    Worker tools never receive this channel or its external provenance authority.
    """
    event = Store.event
    operation = Store.operation

    def __init__(self, project, run):
        project=Path(project)
        if project != project.resolve(strict=True):raise Blocked('owner channel project must be canonical')
        self.path=safe_path(project,'.coherence/workflow/workflow.sqlite')
        self.identity=private_file(self.path)
        self.db=sqlite3.connect(self.path.as_uri()+'?mode=rw',uri=True,isolation_level=None,timeout=5)
        self.db.row_factory=sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('PRAGMA busy_timeout=5000')
        try:
            if ([r[0] for r in self.db.execute('SELECT version FROM wf_meta')]!=[1] or
                    not self.db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_questions'").fetchone() or
                    not self.db.execute('SELECT 1 FROM wf_runs WHERE run_id=? AND reservation=1',(run,)).fetchone()):
                raise Blocked('interaction owner channel unavailable for this run')
        except BaseException:
            self.db.close();raise

    @contextmanager
    def transaction(self):
        if private_file(self.path)!=self.identity:raise Blocked('owner channel database identity drift')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            yield self.db
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK');raise

    def close(self):
        self.db.close()
