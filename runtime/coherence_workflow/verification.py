"""Runner checks and scoped manual STOPs; agent confidence is never evidence."""
import copy
import io
import json
import platform
import time
import unittest
import uuid

from jsonschema import Draft202012Validator

from .store import Blocked, canonical, digest, git, safe_path
from .intake import content_hash


def environment_identity():
    return {'python': platform.python_version(), 'platform': platform.platform()}


def item_identity(project, task, item, environment):
    check=item.get('check',{})
    direct=check.get('args',{}).get('path') if check.get('id') in ('workflow.FileBytes','workflow.PythonAnswer') else None
    if direct is not None:safe_path(project,direct)
    paths=([direct] if check.get('id')=='workflow.FileBytes' and direct else
           sorted(set(task['owned_paths']) | ({direct} if direct else set())))
    return digest({'item': item, 'paths': {name: content_hash(safe_path(project, name))
                   if safe_path(project, name).is_file() else None for name in paths},
                   'environment': environment})


class Verification:
    def __init__(self, authority, run, checks, environment=None):
        self.authority, self.store, self.run = authority, authority.store, run
        self.checks = checks
        self.environment = environment or environment_identity()
        self.store.db.executescript('''
        CREATE TABLE IF NOT EXISTS wf_checks(
          evidence_id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES wf_runs,
          task_id TEXT NOT NULL, item_id TEXT NOT NULL, applicability TEXT NOT NULL,
          receipt TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS wf_gates(
          gate_id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES wf_runs,
          binding TEXT NOT NULL, state TEXT NOT NULL, answer TEXT);
        ''')

    def request_sample(self, task, gate, sample_path, config_hash):
        """Inspectable current bytes, nonce and scoped question precede any full work."""
        path = safe_path(self.authority.project, sample_path)
        if not path.is_file() or sample_path not in task['owned_paths']:
            raise Blocked('sample must be an existing owned artifact')
        binding = {'task_id': task['id'], 'task_hash': digest(task), 'gate': copy.deepcopy(gate),
                   'sample_path': sample_path, 'sample_hash': content_hash(path),
                   'config_hash': config_hash, 'nonce': uuid.uuid4().hex}
        id = uuid.uuid4().hex
        with self.store.transaction() as db:
            db.execute("INSERT INTO wf_gates VALUES(?,?,?,'pending',NULL)", (id, self.run, canonical(binding)))
            self.store.event(db, self.run, None, 'manual_stop_requested', {'gate_id': id, **binding})
        return {'gate_id': id, **binding}

    def answer_sample(self, request, answer, *, verify_owner):
        """verify_owner is an authenticated external input adapter, never a worker callback."""
        row = self.store.db.execute('SELECT * FROM wf_gates WHERE gate_id=? AND run_id=?',
                                    (request['gate_id'], self.run)).fetchone()
        if not row or row['binding'] != canonical({k: v for k, v in request.items() if k != 'gate_id'}):
            raise Blocked('wrong manual STOP binding')
        if row['state'] != 'pending':
            raise Blocked('manual STOP already answered; no duplicate continuation')
        if answer.get('binding_hash') != digest(request) or answer.get('action') not in ('approve', 'deny', 'cancel'):
            raise Blocked('wrong/stale manual answer')
        if content_hash(safe_path(self.authority.project, request['sample_path'])) != request['sample_hash']:
            raise Blocked('manual sample content drift')
        verify_owner(answer)
        with self.store.transaction() as db:
            cur = db.execute("UPDATE wf_gates SET state=?,answer=? WHERE gate_id=? AND state='pending'",
                             (answer['action'], canonical(answer), request['gate_id']))
            if cur.rowcount != 1:
                raise Blocked('manual answer compare-and-set failed')
            self.store.event(db, self.run, None, 'manual_stop_answered',
                             {'gate_id': request['gate_id'], 'action': answer['action'], 'binding_hash': digest(request)})
        return answer['action']

    def require_sample(self, request, task, config_hash):
        row = self.store.db.execute('SELECT * FROM wf_gates WHERE gate_id=? AND run_id=?',
                                    (request['gate_id'], self.run)).fetchone()
        if (not row or row['state'] != 'approve' or row['binding'] != canonical({k: v for k, v in request.items() if k != 'gate_id'}) or
                request['task_hash'] != digest(task) or request['config_hash'] != config_hash or
                content_hash(safe_path(self.authority.project, request['sample_path'])) != request['sample_hash']):
            raise Blocked('unmet/denied/cancelled/stale manual sample STOP')
        return True

    def run_checks(self, task):
        self.authority.assert_held()
        self.store.assert_dispatchable(self.run)
        results, shared = [], {}
        for item in task['required']:
            identity = item_identity(self.authority.project, task, item, self.environment)
            check = item['check']
            spec = self.checks.get(check['id'])
            receipt = {'item_ids': [], 'revision': git(self.authority.project, 'rev-parse', 'HEAD').decode().strip(),
                       'environment': self.environment, 'check': check, 'status': 'insufficient-evidence',
                       'reason': 'registered check unavailable', 'exit_code': None, 'collected': 0}
            if spec and spec['version'] == check['version']:
                Draft202012Validator(spec['schema']).validate(check['args'])
                key = digest(check)
                if key not in shared:
                    start = time.time_ns()
                    try:
                        observed = spec['execute'](copy.deepcopy(check['args']))
                    except Exception as exc:
                        observed = {'exit_code': None, 'collected': 0, 'output': '',
                                    'unknown_reason': 'oracle unavailable: ' + type(exc).__name__}
                    # Only registered oracles may demonstrate a violation; missing/unrun
                    # observations cannot be promoted by worker output or exit 0 alone.
                    valid = (type(observed.get('collected')) is int and observed['collected'] > 0 and
                             type(observed.get('exit_code')) is int and isinstance(observed.get('output'), str))
                    shared[key] = {**receipt, **observed, 'started_ns': start, 'ended_ns': time.time_ns(),
                                   'status': ('satisfied' if observed['exit_code'] == 0 else 'failed') if valid else 'insufficient-evidence',
                                   'reason': None if valid else 'empty/unrun/invalid oracle proof'}
                receipt = copy.deepcopy(shared[key])
            receipt['item_ids'] = [other['id'] for other in task['required'] if other['check'] == check]
            receipt['applicability'] = identity
            with self.store.transaction() as db:
                id = uuid.uuid4().hex
                db.execute('INSERT INTO wf_checks VALUES(?,?,?,?,?,?)',
                           (id, self.run, task['id'], item['id'], identity, canonical(receipt)))
                self.store.event(db, self.run, None, 'check_observed', {'evidence_id': id, 'item_id': item['id'], **receipt})
            results.append({'item_id': item['id'], 'evidence_id': id, **receipt})
        return results

    def audit(self, task, evidence):
        by_item = {}
        for receipt in evidence:
            by_item.setdefault(receipt['item_id'], []).append(receipt)
        dispositions = []
        for item in task['required']:
            receipts = by_item.get(item['id'], [])
            status, reason = 'insufficient-evidence', 'missing/conflicting/stale proof'
            if len(receipts) == 1:
                receipt = receipts[0]
                row = self.store.db.execute('SELECT * FROM wf_checks WHERE evidence_id=? AND run_id=? AND task_id=? AND item_id=?',
                    (receipt['evidence_id'], self.run, task['id'], item['id'])).fetchone()
                expected = {k: v for k, v in receipt.items() if k not in ('evidence_id', 'item_id')}
                if (row and json.loads(row['receipt']) == expected and
                        row['applicability'] == item_identity(self.authority.project, task, item, self.environment)):
                    status, reason = receipt['status'], receipt['reason']
            dispositions.append({'item_id': item['id'], 'status': status, 'reason': reason})
        return dispositions


def unittest_oracle(args):
    """Trusted registered selectors only; zero collection is not a passing oracle."""
    if not args.get('selector'):
        raise Blocked('empty test selector')
    module = args['test_file'].removesuffix('.py').replace('/', '.')
    suite = unittest.defaultTestLoader.loadTestsFromName(module + '.' + args['selector'])
    if unittest.defaultTestLoader.errors:
        unittest.defaultTestLoader.errors.clear()
        return {'exit_code': None, 'collected': 0, 'output': 'test loader unavailable'}
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return {'exit_code': None if result.errors or result.skipped else 0 if result.wasSuccessful() else 1,
            'collected': result.testsRun, 'output': stream.getvalue()[:32768]}


class ReviewRepair:
    """Persistent original-failure budgets and independently audited review authority."""
    def __init__(self, coordinate):
        self.coordinate=coordinate
        self.store,self.run=coordinate.store,coordinate.run
        self.store.db.executescript('''
        CREATE TABLE IF NOT EXISTS wf_repair_budgets(
          run_id TEXT NOT NULL REFERENCES wf_runs, failure_key TEXT NOT NULL,
          maximum INTEGER NOT NULL, used INTEGER NOT NULL, PRIMARY KEY(run_id,failure_key));
        CREATE TABLE IF NOT EXISTS wf_reviews(
          review_id TEXT PRIMARY KEY,run_id TEXT NOT NULL REFERENCES wf_runs,
          base_sha TEXT NOT NULL,head_sha TEXT NOT NULL,host_op TEXT NOT NULL REFERENCES wf_operations,
          result TEXT NOT NULL,independent INTEGER NOT NULL CHECK(independent=1));
        CREATE TABLE IF NOT EXISTS wf_findings(
          review_id TEXT NOT NULL REFERENCES wf_reviews,finding_id TEXT NOT NULL,
          finding TEXT NOT NULL,disposition TEXT NOT NULL,correction_id TEXT,
          PRIMARY KEY(review_id,finding_id));
        CREATE TABLE IF NOT EXISTS wf_corrections(
          run_id TEXT NOT NULL REFERENCES wf_runs,task_id TEXT NOT NULL,original_task_id TEXT NOT NULL,
          failure_key TEXT NOT NULL,authority TEXT NOT NULL,PRIMARY KEY(run_id,task_id));
        ''')

    def failure_key(self, task):
        row=self.store.db.execute('SELECT failure_key FROM wf_corrections WHERE run_id=? AND task_id=?',(self.run,task['id'])).fetchone()
        return row[0] if row else 'task:'+task['id']

    def maximum(self, key):
        nodes=self.coordinate.config['nodes']
        maximum=next(n['max_repair_attempts'] for n in nodes if n['handler']=='repair')
        if key=='review-final':maximum=min(maximum,next(n['max_repair_attempts'] for n in nodes if n['handler']=='review'))
        return maximum

    def budget(self, key, maximum, *, consume=False):
        if type(maximum) is not int or maximum<0:raise Blocked('invalid repair budget')
        with self.store.transaction() as db:
            db.execute('INSERT OR IGNORE INTO wf_repair_budgets VALUES(?,?,?,0)',(self.run,key,maximum))
            row=db.execute('SELECT * FROM wf_repair_budgets WHERE run_id=? AND failure_key=?',(self.run,key)).fetchone()
            if row['maximum']!=maximum:raise Blocked('original repair budget/config drift')
            if row['used']>=maximum:raise Blocked('repair budget exhausted for original failure '+key)
            next_count=row['used']+1
            if consume:
                db.execute('UPDATE wf_repair_budgets SET used=? WHERE run_id=? AND failure_key=?',(next_count,self.run,key))
                self.store.event(db,self.run,None,'repair_dispatched',{'failure_key':key,'count':next_count,'maximum':maximum})
        return next_count

    def diagnose(self, task, evidence):
        audited=self.coordinate.verification.audit(task,evidence)
        if any(d['status']=='insufficient-evidence' for d in audited):
            raise Blocked('unknown/environment/capability evidence; no blind repair')
        failures={d['item_id'] for d in audited if d['status']=='failed'}
        if not failures or any(e.get('diagnosis')!='implementation' for e in evidence if e['item_id'] in failures):
            raise Blocked('failure requires inspected implementation diagnosis before repair')
        self.coordinate.gates_satisfied(task)
        with self.store.transaction() as db:
            self.store.event(db,self.run,None,'repair_diagnosed',{'failure_key':self.failure_key(task),'items':sorted(failures),'evidence_refs':[e['evidence_id'] for e in evidence]})
        return True

    def range(self):
        first=self.store.db.execute('SELECT baseline FROM wf_tasks WHERE run_id=? ORDER BY approved_order LIMIT 1',(self.run,)).fetchone()
        head=git(self.coordinate.authority.project,'rev-parse','HEAD').decode().strip()
        return (json.loads(first[0])['head'] if first and first[0] else head),head

    def refresh_evidence(self):
        """Later approved tasks may change producer inputs without changing criteria."""
        for original in self.coordinate.contract['tasks']:
            self.coordinate.gates_satisfied(original)
            correction=self.store.db.execute('SELECT t.* FROM wf_tasks t JOIN wf_corrections c USING(run_id,task_id) WHERE c.run_id=? AND c.original_task_id=? ORDER BY t.approved_order DESC LIMIT 1',(self.run,original['id'])).fetchone()
            row=correction or self.store.db.execute('SELECT * FROM wf_tasks WHERE run_id=? AND task_id=?',(self.run,original['id'])).fetchone()
            if row['state'] not in ('checkpointed','read_only_complete'):raise Blocked('unfinished producer cannot enter final review')
            task=json.loads(row['contract']);evidence=json.loads(row['evidence'])
            audited=self.coordinate.verification.audit(task,evidence)
            stale={d['item_id'] for d in audited if d['status']=='insufficient-evidence'}
            if stale:
                subset={**task,'required':[item for item in task['required'] if item['id'] in stale]}
                evidence=[e for e in evidence if e['item_id'] not in stale]+self.coordinate.verification.run_checks(subset)
                with self.store.transaction() as db:
                    db.execute('UPDATE wf_tasks SET evidence=? WHERE run_id=? AND task_id=?',(canonical(evidence),self.run,task['id']))
                    self.store.event(db,self.run,None,'task_evidence_refreshed',{'task_id':task['id'],'item_ids':sorted(stale),'evidence_refs':[e['evidence_id'] for e in evidence]})
            if any(d['status']!='satisfied' for d in self.coordinate.verification.audit(task,evidence)):
                raise Blocked('final current REQUIRED evidence failed/insufficient; inspect before repair')

    def bundle(self):
        base,head=self.range()
        tasks=[{'task_id':r['task_id'],'state':r['state'],'contract':json.loads(r['contract']),
                'evidence':json.loads(r['evidence']) if r['evidence'] else None,
                'checkpoint_sha':json.loads(r['checkpoint'])['sha'] if r['checkpoint'] else None}
               for r in self.store.db.execute('SELECT * FROM wf_tasks WHERE run_id=? ORDER BY approved_order',(self.run,))]
        findings=[dict(r) for r in self.store.db.execute('SELECT f.* FROM wf_findings f JOIN wf_reviews r USING(review_id) WHERE r.run_id=?',(self.run,))]
        patch=git(self.coordinate.authority.project,'diff','--no-ext-diff','--no-textconv','--binary',base+'..'+head).decode()
        names={s['path'] for s in self.coordinate.contract['sources']} | {r['record_ref'] for r in self.coordinate.contract['approval_refs']}
        source_content={name:safe_path(self.coordinate.authority.project,name).read_text() for name in names}
        result={'range_base':base,'range_head':head,'source_tasks_approvals':self.coordinate.contract,'source_content':source_content,'task_receipts':tasks,
                'finding_history':findings,'full_committed_diff':patch}
        if len(canonical(result).encode())>120000:raise Blocked('complete review bundle exceeds supported bound; no truncation')
        return result

    def record_review(self, result, host_op):
        from .registry import validate_schema
        validate_schema('agent-result.schema.json',result)
        base,head=self.range()
        if result['kind']!='review' or result['range_base']!=base or result['range_head']!=head:
            raise Blocked('missing/stale full-range independent review')
        host=self.store.operation(host_op)
        ready=self.store.db.execute("SELECT payload FROM wf_events WHERE op_id=? AND kind='host_ready'",(host_op,)).fetchone()
        if host['phase']!='completed' or not ready:raise Blocked('review host custody not settled')
        provenance=json.loads(ready[0])
        tools=provenance['snapshot']['tools']
        configured=[node for node in self.coordinate.config['nodes'] if node.get('role')=='review' and
                    set(node['tools'])==set(tools) and len(node['tools'])==len(tools) and
                    set(tools)<=set(node['permissions'])]
        admission=self.store.db.execute("SELECT payload FROM wf_events WHERE op_id=? AND kind='host_admission'",(host_op,)).fetchone()
        if (provenance['compatibility']['role']!='review' or provenance['compatibility'].get('review_lineage')!=base or
                sorted(tools) not in (['read_file'],['read_file','request_owner_input']) or not configured or
                not admission or json.loads(admission[0])['compatibility']!=provenance['compatibility']):
            raise Blocked('review was not independent read-only with exact configured/admitted tools')
        if len({f['id'] for f in result['findings']})!=len(result['findings']):raise Blocked('duplicate review finding IDs')
        review_id=uuid.uuid4().hex
        with self.store.transaction() as db:
            db.execute('INSERT INTO wf_reviews VALUES(?,?,?,?,?,?,1)',(review_id,self.run,base,head,host_op,canonical(result)))
            for finding in result['findings']:
                db.execute("INSERT INTO wf_findings VALUES(?,?,?,'unresolved',NULL)",(review_id,finding['id'],canonical(finding)))
            if result['outcome']=='pass':
                for row in db.execute("SELECT f.review_id,f.finding_id,f.correction_id FROM wf_findings f JOIN wf_reviews r USING(review_id) WHERE r.run_id=? AND f.disposition='accepted_focused'",(self.run,)).fetchall():
                    task=db.execute('SELECT state FROM wf_tasks WHERE run_id=? AND task_id=?',(self.run,row['correction_id'])).fetchone()
                    if not task or task['state'] not in ('checkpointed','read_only_complete'):raise Blocked('review passed with unfinished correction')
                    db.execute("UPDATE wf_findings SET disposition='resolved' WHERE review_id=? AND finding_id=?",(row['review_id'],row['finding_id']))
                    self.store.event(db,self.run,None,'finding_resolved',dict(row))
            self.store.event(db,self.run,None,'review_recorded',{'review_id':review_id,'base':base,'head':head,'outcome':result['outcome'],'host_op':host_op})
        return review_id

    def authorize_corrections(self):
        review=self.store.db.execute('SELECT * FROM wf_reviews WHERE run_id=? ORDER BY rowid DESC LIMIT 1',(self.run,)).fetchone()
        if not review:raise Blocked('missing review')
        result=json.loads(review['result'])
        if result['outcome']!='correction':raise Blocked('not a correction review')
        _,head=self.range()
        if head!=review['head_sha']:raise Blocked('stale-head correction authority')
        rules=self.coordinate.catalog.get('workflow_correction_rules',[])
        original={t['id']:t for t in self.coordinate.contract['tasks']}
        plans=[]
        for finding in result['findings']:
            path=finding['location'].split(':',1)[0]
            candidates=[r for r in rules if r.get('criterion_ref')==finding['criterion_ref'] and r.get('path')==path]
            if finding['scope']!='in_scope' or len(candidates)!=1:
                raise Blocked('finding requires explicit scoped owner correction contract')
            rule=candidates[0];producer=original.get(rule.get('original_task_id'));template=rule.get('task')
            if template:
                from .registry import validate_schema
                validate_schema('task.schema.json',{**self.coordinate.contract,'tasks':[template]})
            if (not producer or not template or not rule.get('actor') or not rule.get('provenance') or
                    rule.get('scope_hash')!=digest(template) or template['required']!=producer['required'] or
                    template['gates']!=producer['gates'] or template['optional']!=producer['optional'] or
                    template['owned_paths']!=producer['owned_paths'] or path not in producer['owned_paths'] or
                    template['context_group']!=producer['context_group'] or
                    template['authorization_envelope_id']!=producer['authorization_envelope_id']):
                raise Blocked('correction contract widens scope/weakens original items/gates')
            self.coordinate.gates_satisfied(producer)
            self.budget('review-final',self.maximum('review-final'))
            task=copy.deepcopy(template)
            task['id']=template['id']+'/'+review['review_id']+'/'+finding['id']
            task['order']=self.store.db.execute('SELECT COALESCE(MAX(approved_order),-1) FROM wf_tasks WHERE run_id=?',(self.run,)).fetchone()[0]+1+len(plans)
            if task['gates']:raise Blocked('original gates need correction-bound renewal before dispatch')
            plans.append((task,producer,rule,finding))
        with self.store.transaction() as db:
            for task,producer,rule,finding in plans:
                db.execute("INSERT INTO wf_tasks VALUES(?,?,?,?,'pending',NULL,NULL,NULL)",(self.run,task['id'],task['order'],canonical(task)))
                authority={'rule_hash':digest(rule),'source_approval_hash':digest(self.coordinate.contract['approval_refs']),
                           'finding_id':finding['id'],'review_id':review['review_id'],'range_head':head}
                db.execute('INSERT INTO wf_corrections VALUES(?,?,?,?,?)',(self.run,task['id'],producer['id'],'review-final',canonical(authority)))
                db.execute("UPDATE wf_findings SET disposition='accepted_focused',correction_id=? WHERE review_id=? AND finding_id=?",(task['id'],review['review_id'],finding['id']))
                self.store.event(db,self.run,None,'correction_authorized',{'task_id':task['id'],'contract_hash':digest(task),**authority})
        return plans

    def acceptance(self):
        _,head=self.range()
        review=self.store.db.execute('SELECT * FROM wf_reviews WHERE run_id=? ORDER BY rowid DESC LIMIT 1',(self.run,)).fetchone()
        if not review or review['head_sha']!=head or json.loads(review['result'])['outcome']!='pass':
            raise Blocked('current full-range independent review required')
        if self.store.db.execute("SELECT 1 FROM wf_findings f JOIN wf_reviews r USING(review_id) WHERE r.run_id=? AND disposition!='resolved'",(self.run,)).fetchone():
            raise Blocked('unresolved review findings')
        for task in self.coordinate.contract['tasks']:
            self.coordinate.gates_satisfied(task)
            correction=self.store.db.execute('SELECT t.* FROM wf_tasks t JOIN wf_corrections c USING(run_id,task_id) WHERE c.run_id=? AND c.original_task_id=? ORDER BY t.approved_order DESC LIMIT 1',(self.run,task['id'])).fetchone()
            row=correction or self.store.db.execute('SELECT * FROM wf_tasks WHERE run_id=? AND task_id=?',(self.run,task['id'])).fetchone()
            current_task=json.loads(row['contract'])
            if row['state'] not in ('checkpointed','read_only_complete') or not row['checkpoint'] or any(d['status']!='satisfied' for d in self.coordinate.verification.audit(current_task,json.loads(row['evidence']))):
                raise Blocked('current REQUIRED items/checkpoints do not permit acceptance')
        for gate in self.store.db.execute('SELECT * FROM wf_gates WHERE run_id=?',(self.run,)):
            binding=json.loads(gate['binding']);request={'gate_id':gate['gate_id'],**binding}
            if gate['state']!='approve' or content_hash(safe_path(self.coordinate.authority.project,binding['sample_path']))!=binding['sample_hash']:
                raise Blocked('unmet/stale original manual STOP')
        self.coordinate.reconcile_effect({}, {})
        with self.store.transaction() as db:self.store.event(db,self.run,None,'workflow_accepted',{'head':head,'review_id':review['review_id']})
        return {'outcome':'accepted'}
