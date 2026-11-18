"""Real subprocess offline API fixture. This is not live GitHub delivery proof.

The fixture supports the observed GitHub body-length diagnostic and a legacy
source-backed LengthProof seam. Neither fixture is live GitHub delivery proof.
"""
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from coherence_workflow.store import Store, canonical
from coherence_workflow.trace_projection import project_trace, render_markdown
from coherence_workflow.trace_publication import Gh, LengthProof, digest, publish_trace

ISSUE = 'https://github.com/owner/repo/issues/45'
PR = 'https://github.com/owner/repo/pull/9'
API = 'https://api.github.com/repos/owner/repo'

# Exact body validation observed by the parent at GitHub issue 45 (HTTP 422).
LENGTH_ERROR = {'message': 'Validation Failed', 'errors': [
    {'resource': 'IssueComment', 'code': 'unprocessable', 'field': 'data',
     'message': 'Body is too long (maximum is 65536 characters)'}],
    'documentation_url': 'https://docs.github.com/rest/issues/comments#create-an-issue-comment',
    'status': '422'}

FAKE = r'''#!/usr/bin/env python3
import json, os, sqlite3, sys
from pathlib import Path
path = Path(os.environ['TRACE_FAKE_STATE'])
s = json.loads(path.read_text())
a = sys.argv[1:]
assert a[0] == 'api' and a[1:3] == ['--hostname', 'github.com'], a
assert a[3] == '--method' and a[5] == '--include', a
assert a[6:10] == ['-H', 'Accept: application/vnd.github+json', '-H', 'X-GitHub-Api-Version: 2022-11-28'], a
method, endpoint = a[4], a[10]
assert method in ('GET', 'POST'), method
assert endpoint.startswith('/repos/owner/repo/'), endpoint
stdin = sys.stdin.read() if method == 'POST' else None
body = json.loads(stdin) if stdin is not None else None
assert a[11:] == (['--input', '-'] if method == 'POST' else []), a
s['calls'].append({'method': method, 'endpoint': endpoint, 'stdin': body})
def save(): path.write_text(json.dumps(s))
def respond(data, status=200, headers=None, code=0):
    save()
    print('HTTP/2.0 ' + str(status))
    for key, value in (headers or {}).items(): print(key + ': ' + value)
    print()
    print(json.dumps(data))
    sys.exit(code)
api = 'https://api.github.com/repos/owner/repo'
web = 'https://github.com/owner/repo'
if method == 'GET' and endpoint in ('/repos/owner/repo/issues/45', '/repos/owner/repo/issues/9'):
    if s.get('access_error'): respond({'message':'denied'}, s['access_error'], code=1)
    n = int(endpoint.rsplit('/',1)[1])
    obj = {'number':n, 'url':api+'/issues/'+str(n), 'html_url':web+('/pull/9' if n==9 else '/issues/45')}
    if n==9: obj['pull_request'] = {'url':api+'/pulls/9'}
    if s.get('target_drift'): obj['number'] = 999
    respond(obj)
if method == 'GET' and endpoint == '/repos/owner/repo/pulls/9':
    respond({'number':9, 'html_url':web+'/pull/9', 'issue_url':api+'/issues/9'})
if method == 'POST':
    # Production intent must be independently visible before any remote effect.
    db = sqlite3.connect(os.environ['TRACE_FAKE_DB'], timeout=0)
    db.execute('BEGIN IMMEDIATE')  # proves publisher holds no network transaction
    rows = [(state, json.loads(details)) for state,details in db.execute(
        "SELECT state,details FROM execution_history WHERE kind='trace_publication' ORDER BY seq")]
    assert any(state=='prepared' and r.get('type')=='snapshot' for state,r in rows)
    assert rows[-1][0]=='sending' and rows[-1][1]['body']==body['body'], rows[-1]
    assert rows[-1][1]['body_sha256']==__import__('hashlib').sha256(body['body'].encode()).hexdigest()
    db.rollback(); db.close()
    assert set(body)=={'body'}
    s['posts'] += 1
    if s.get('post_error') and s.get('error_on',s['posts'])==s['posts']:
        respond(s.get('error_data', {'message':s.get('error_message','unrelated validation')}), s['post_error'], code=1)
    if s.get('malformed_error'):
        save(); print('HTTP/2.0 422\n\n{'); sys.exit(1)
    if s.get('length_error') and len(body['body']) > s.get('length_limit', 65536):
        respond(s['length_error'], 422, code=1)
    number = int(endpoint.split('/')[-2])
    identity = s['next_id']; s['next_id'] += 1
    obj = {'id':identity, 'url':api+'/issues/comments/'+str(identity),
           'html_url':web+('/pull/9' if number==9 else '/issues/45')+'#issuecomment-'+str(identity),
           'issue_url':api+'/issues/'+str(number), 'body':body['body']}
    s['comments'].append(obj)
    if s.get('lost_response'):
        s['lost_response']=False; save(); print('lost response'); sys.exit(1)
    respond(obj,201)
if method=='GET' and '/issues/comments/' in endpoint:
    identity = int(endpoint.rsplit('/',1)[1])
    obj = next((dict(c) for c in s['comments'] if c['id']==identity), None)
    if obj is None: respond({'message':'not found'},404,code=1)
    if s.get('readback_mismatch'): obj['body'] += ' mismatch'
    if s.get('readback_wrong_target'): obj['issue_url'] = api+'/issues/999'
    if s.get('readback_wrong_id'): obj['id'] += 1
    if s.get('readback_wrong_url'): obj['html_url'] = web+'/issues/999#issuecomment-'+str(identity)
    respond(obj)
if method=='GET' and '/comments?' in endpoint:
    from urllib.parse import parse_qs, urlsplit
    page = int(parse_qs(urlsplit(endpoint).query)['page'][0])
    if s.get('incomplete_page') and page==2:
        save(); print('HTTP/2.0 200\n\n['); sys.exit(1)
    if s.get('page_error') and page==2: respond({'message':'rate limited'},429,code=1)
    items = s['comments'] if not s.get('pages') else s['pages'].get(str(page),[])
    headers = {}
    if s.get('pages') and page==1:
        headers['Link'] = '<'+api+'/issues/'+str(s.get('destination',45))+'/comments?per_page=100&page=2>; rel="next"'
    if s.get('bad_link'): headers['Link']=s['bad_link']
    respond(items, headers=headers)
raise AssertionError((method,endpoint))
'''


class FakeAuthority:
    def assert_held(self): pass


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = Store(self.root/'history.sqlite', FakeAuthority())
        self.addCleanup(self.store.close)
        self.store.db.execute("INSERT INTO execution_runs VALUES('run','complete','base','head',NULL)")
        self.store.db.execute('INSERT INTO execution_run_inputs VALUES(?,?,?,?,?)',
                              ('run', canonical({'delivery_issue':ISSUE}), '{}', '{}', 'base'))
        self.store.history('run', 'T', 'worker_invocation', 'returned', {
            'invocation_id':'actual', 'submission':{'report':'Ordinary conversation\nanswer “yes” 🦊\n' + 'meaningful long text\n'*40,
                                                   'evidence':[], 'gaps':[]},
            'token':'ACTUAL-CREDENTIAL-SENTINEL',
            'explanation':'known ACTUAL-CREDENTIAL-SENTINEL is excluded; ordinary answer is retained'})
        self.state_path = self.root/'remote.json'
        self.update(calls=[], posts=0, next_id=10, comments=[])
        executable = self.root/'gh'
        executable.write_text(FAKE)
        executable.chmod(0o700)
        self.gh = Gh(executable)
        env = patch.dict(os.environ, {'TRACE_FAKE_STATE':str(self.state_path), 'TRACE_FAKE_DB':str(self.store.path)})
        env.start(); self.addCleanup(env.stop)
        self.grant = {'run_id':'run', 'target':ISSUE, 'operations':['trace_comment'], 'approval_ref':'actual fixture owner scope'}

    def remote(self):
        return json.loads(self.state_path.read_text())

    def update(self, **values):
        old = self.remote() if self.state_path.exists() else {}
        old.update(values)
        self.state_path.write_text(json.dumps(old))

    def publish(self, **kwargs):
        return publish_trace(self.store, 'run',
                             **{'gh':self.gh, 'authority':self.grant, **kwargs})

    def rows(self):
        return [{**json.loads(row['details']), 'state':row['state']}
                for row in self.store.trace_publication_history('run')]

    def part_wire(self, part='1', chunk=None):
        snapshot = project_trace(self.store, 'run')
        marker = '<!-- coherence-trace:'+digest('run')+':'+snapshot['snapshot_id']+':'+part+' -->'
        return marker+'\nTrace continuation '+part+'; concatenate leaf payloads in part order without added separators.\n'+(chunk if chunk is not None else render_markdown(snapshot))

    def proof(self, body=None, message='fixture length rejected; no effect'):
        raw = 'HTTP/2.0 422\n\n'+json.dumps({'message':message})+'\n'
        return LengthProof(digest(body or self.part_wire()), digest(raw),
                           'runtime/tests/test_trace_publication.py: FAKE no-effect length contract',
                           'Inspected fake rejects length before any comment creation.', True)

    def test_whole_roundtrip_intent_independent_read_reopen_and_credentials(self):
        before = project_trace(self.store, 'run')
        outcome = self.publish()
        self.assertEqual(outcome['state'], 'confirmed', outcome)
        remote = self.remote()
        self.assertEqual(remote['posts'], 1)
        comment = remote['comments'][0]
        self.assertEqual(comment['body'], self.part_wire())
        self.assertNotIn('ACTUAL-CREDENTIAL-SENTINEL', comment['body'])
        self.assertIn('Ordinary conversation', comment['body'])
        self.assertIn('answer “yes” 🦊', comment['body'])
        self.assertIn('Known credential', comment['body'])
        self.assertEqual(remote['calls'][-1]['method'], 'GET')
        self.assertIn('/issues/comments/10', remote['calls'][-1]['endpoint'])
        self.assertEqual(project_trace(self.store, 'run'), before)
        self.assertEqual([r['state'] for r in self.rows()], ['prepared','prepared','sending','confirmed','confirmed'])
        # Actual store reopen and recovery re-read, no blind repeat.
        self.store.db.close()
        self.store = Store(self.root/'history.sqlite', FakeAuthority())
        self.addCleanup(self.store.close)
        again = self.publish(snapshot_id=outcome['snapshot_id'])
        self.assertEqual(again['state'], 'confirmed', again)
        self.assertEqual(self.remote()['posts'], 1)
        self.assertEqual(again['urls'], outcome['urls'])

    def test_absent_drifted_operation_scope_has_zero_subprocess_or_mutation(self):
        for grant in (None, {}, {**self.grant, 'run_id':'other'},
                      {**self.grant, 'target':PR}, {**self.grant, 'operations':['link_comment']},
                      {**self.grant, 'approval_ref':''}):
            with self.subTest(grant=grant):
                out = self.publish(authority=grant)
                self.assertEqual(out['state'], 'deferred', out)
                self.assertIn('authority', out['correction'])
        self.assertEqual(self.remote()['calls'], [])
        self.assertEqual(self.rows(), [])

    def test_missing_or_drifted_target_and_unusable_access_zero_posts(self):
        for target in ('', 'owner/repo#45','https://github.com/other/repo/issues/45', PR):
            self.assertEqual(self.publish(target=target)['state'], 'deferred')
        self.update(target_drift=True)
        self.assertEqual(self.publish()['state'], 'deferred')
        self.update(target_drift=False)
        for status in (401,403,404,429):
            self.update(access_error=status)
            out = self.publish()
            self.assertNotEqual(out['state'], 'confirmed')
            self.assertIn(str(status), out['correction'])
        self.assertEqual(self.remote()['posts'], 0)
        self.assertEqual(self.rows(), [])
        # Missing issue is not inferred from credentials or the grant.
        self.store.db.execute('UPDATE execution_run_inputs SET contract=?', ('{}',))
        self.assertEqual(self.publish()['state'], 'deferred')

    def test_explicit_known_linked_pr_only(self):
        grant = {**self.grant,'target':PR}
        out = self.publish(target=PR, authority=grant, known_linked_prs=[PR])
        self.assertEqual(out['state'], 'confirmed', out)
        self.assertIn('/pull/9#issuecomment-', out['urls'][0])
        self.assertTrue(any(c['endpoint'].endswith('/pulls/9') for c in self.remote()['calls']))

    def test_every_part_full_body_identity_and_target_readback(self):
        for fault in ('readback_mismatch','readback_wrong_target','readback_wrong_id','readback_wrong_url'):
            with self.subTest(fault=fault):
                self.update(**{fault:True})
                out = self.publish()
                self.assertEqual(out['state'], 'uncertain', out)
                self.assertIn('readback', out['correction'])
                self.assertEqual(self.remote()['posts'], 1)
                # On recovery mismatch/collision never permits blind duplicates.
                again = self.publish(snapshot_id=out['snapshot_id'])
                self.assertEqual(again['state'], 'uncertain', again)
                self.assertEqual(self.remote()['posts'], 1)
                self.update(**{fault:False})
        self.assertEqual(self.publish()['state'], 'confirmed')
        self.assertEqual(self.remote()['posts'], 1)

    def test_lost_response_complete_paginated_scan_and_exact_candidate_read(self):
        self.update(lost_response=True)
        first = self.publish()
        self.assertEqual(first['state'], 'uncertain', first)
        comment = self.remote()['comments'][0]
        self.update(pages={'1':[], '2':[comment]})
        outcome = self.publish(snapshot_id=first['snapshot_id'])
        self.assertEqual(outcome['state'], 'confirmed', outcome)
        self.assertEqual(self.remote()['posts'], 1)
        calls = self.remote()['calls']
        self.assertTrue(any('page=2' in c['endpoint'] for c in calls))
        self.assertTrue(calls[-1]['endpoint'].endswith('/issues/comments/10'))

    def test_incomplete_or_failed_page_prevents_writes_even_when_candidate_seen(self):
        self.update(lost_response=True)
        first = self.publish()
        comment = self.remote()['comments'][0]
        self.update(pages={'1':[comment], '2':[]}, incomplete_page=True)
        self.assertEqual(self.publish(snapshot_id=first['snapshot_id'])['state'], 'uncertain')
        self.assertEqual(self.remote()['posts'], 1)
        self.update(incomplete_page=False, page_error=True)
        self.assertEqual(self.publish(snapshot_id=first['snapshot_id'])['state'], 'uncertain')
        self.assertEqual(self.remote()['posts'], 1)
        self.update(page_error=False)
        self.assertEqual(self.publish(snapshot_id=first['snapshot_id'])['state'], 'confirmed')

    def test_pagination_drift_skip_repeat_or_malformed_link_stops_writes(self):
        self.update(lost_response=True)
        self.publish()
        for link in (
                '<'+API+'/issues/45/comments?per_page=100&page=1>; rel="next"',
                '<'+API+'/issues/45/comments?per_page=100&page=3>; rel="next"',
                '<https://other.example/repos/owner/repo/issues/45/comments?per_page=100&page=2>; rel="next"',
                '<'+API+'/issues/45/comments?per_page=100&page=2>; rel="next", malformed',
                'truncated Link'):
            with self.subTest(link=link):
                self.update(bad_link=link)
                out = self.publish()
                self.assertEqual(out['state'], 'uncertain', out)
                self.assertEqual(self.remote()['posts'], 1)
        self.update(bad_link=None)
        self.assertEqual(self.publish()['state'], 'confirmed')

    def test_marker_collision_and_exact_duplicates_stop_writes(self):
        self.update(lost_response=True)
        self.publish()
        original = self.remote()['comments'][0]
        changed = {**original, 'body':original['body']+'wrong'}
        self.update(comments=[changed])
        out = self.publish()
        self.assertEqual(out['state'], 'uncertain', out)
        self.assertEqual(self.remote()['posts'], 1)
        duplicate = {**original,'id':11,'url':API+'/issues/comments/11','html_url':ISSUE+'#issuecomment-11'}
        self.update(comments=[original, duplicate])
        out = self.publish()
        self.assertEqual(out['state'], 'uncertain', out)
        self.assertIn('Multiple exact',out['correction'])
        self.assertEqual(self.remote()['posts'], 1)

    def test_complete_zero_match_reconciliation_allows_one_targeted_attempt(self):
        self.update(post_error=503, error_on=1)
        self.assertEqual(self.publish()['state'], 'failed')
        self.update(post_error=None)
        out = self.publish()
        self.assertEqual(out['state'], 'confirmed', out)
        self.assertEqual(self.remote()['posts'], 2)
        calls = self.remote()['calls']
        second_post = [i for i,c in enumerate(calls) if c['method']=='POST'][1]
        self.assertIn('/comments?per_page=100&page=1', calls[second_post-1]['endpoint'])

    def test_only_source_backed_exact_no_effect_length_proof_partitions_losslessly(self):
        proof = self.proof()
        self.update(post_error=422, error_on=1, error_message='fixture length rejected; no effect')
        original = render_markdown(project_trace(self.store, 'run'))
        out = self.publish(length_proofs=[proof])
        self.assertEqual(out['state'], 'confirmed', out)
        parts = [r for r in self.rows() if r.get('type')=='part' and r['state']=='confirmed']
        self.assertEqual([r['part'] for r in parts], ['1.1','1.2'])
        self.assertEqual(''.join(r['chunk'] for r in parts), original)
        split = next(r for r in self.rows() if r['state']=='split')
        self.assertEqual(split['length_proof']['source'], proof.source)
        self.assertEqual(''.join(split['children']), original)
        self.assertEqual(self.remote()['posts'], 3)
        self.assertEqual(len(self.remote()['comments']), 2)
        self.assertEqual(self.publish(snapshot_id=out['snapshot_id'])['state'], 'confirmed')
        self.assertEqual(self.remote()['posts'], 3)

    def test_unrelated_422_auth_rate_and_unverified_length_never_split_or_loop(self):
        for status, message in ((422,'unrelated validation'),(401,'denied'),(403,'rate'),
                                (429,'rate'),(422,'fixture length rejected; no effect')):
            with self.subTest(status=status, message=message):
                before = self.remote()['posts']
                self.update(post_error=status, error_on=before+1, error_message=message)
                out = self.publish()  # no proof; even length-like text is not proof
                self.assertEqual(out['state'], 'failed', out)
                self.assertEqual(self.remote()['posts'], before+1)
                self.assertIn('No recognized IssueComment body-length diagnostic', out['correction'])
        self.assertFalse(any(r['state']=='split' for r in self.rows()))

    def test_length_rejection_incomplete_scan_retains_cause_and_recovers_without_root_resend(self):
        self.update(length_error=LENGTH_ERROR, length_limit=len(self.part_wire())-1,
                    pages={'1': [], '2': []}, incomplete_page=True)
        first = self.publish()
        self.assertEqual(first['state'], 'uncertain', first)
        self.assertEqual(self.remote()['posts'], 1)
        rejected = self.rows()[-1]
        self.assertEqual(rejected['state'], 'rejected')
        self.assertEqual(rejected['length_diagnostic']['message'], LENGTH_ERROR['errors'][0]['message'])
        self.assertFalse(any(r['state'] == 'split' for r in self.rows()))
        self.update(incomplete_page=False, pages=None)
        recovered = self.publish(snapshot_id=first['snapshot_id'])
        self.assertEqual(recovered['state'], 'confirmed', recovered)
        self.assertEqual(self.remote()['posts'], 3)  # No second root rejection.
        self.assertEqual(len(self.remote()['comments']), 2)
        self.assertEqual(''.join(c['body'].split('without added separators.\n', 1)[1]
                                 for c in self.remote()['comments']),
                         next(r['text'] for r in self.rows() if r['type'] == 'snapshot'))

    def test_length_rejection_possible_effect_requires_exact_complete_reconciliation(self):
        self.update(length_error=LENGTH_ERROR, length_limit=1)
        underlying = self.gh
        test = self
        class PossibleEffect:
            def request(self, target, method, endpoint, body=None):
                response = underlying.request(target, method, endpoint, body)
                if method == 'POST':
                    comment = {'id': 10, 'url': API+'/issues/comments/10',
                               'html_url': ISSUE+'#issuecomment-10',
                               'issue_url': API+'/issues/45', 'body': body['body'] + ' collision'}
                    test.update(comments=[comment], pages={'1': [], '2': [comment]})
                return response
        first = self.publish(gh=PossibleEffect())
        self.assertEqual(first['state'], 'uncertain', first)
        self.assertEqual(self.remote()['posts'], 1)
        self.assertFalse(any(r['state'] == 'split' for r in self.rows()))
        comment = self.remote()['comments'][0]
        exact = {**comment, 'body': self.part_wire()}
        self.update(comments=[exact], pages={'1': [], '2': [exact]})
        recovered = self.publish(snapshot_id=first['snapshot_id'])
        self.assertEqual(recovered['state'], 'confirmed', recovered)
        self.assertEqual(self.remote()['posts'], 1)
        self.assertFalse(any(r['state'] == 'split' for r in self.rows()))

    def test_malformed_or_other_validation_is_not_automatic_length_evidence(self):
        error = LENGTH_ERROR['errors'][0]
        variants = [None, [], {'message': 'Validation Failed', 'errors': 'not a list'},
                    {**LENGTH_ERROR, 'errors': [error, {'message': 'another failure'}]},
                    *[{**LENGTH_ERROR, 'errors': [{**error, key: value}]}
                      for key, value in (('resource', 'PullRequest'), ('field', 'body'),
                                         ('code', 'invalid'), ('message', 'Body is too long'),
                                         ('message', 'secret Body is too long (maximum is 65536 characters)'))]]
        for data in variants:
            with self.subTest(data=data):
                count = self.remote()['posts']
                self.update(post_error=422, error_data=data)
                result = self.publish()
                self.assertEqual(result['state'], 'failed', result)
                self.assertEqual(self.remote()['posts'], count+1)
                self.assertNotIn('secret', result['correction'])
        for status in (401, 403, 429, 503):
            self.update(post_error=status, error_data=LENGTH_ERROR)
            self.assertEqual(self.publish()['state'], 'failed')
        self.update(post_error=None, malformed_error=True)
        self.assertEqual(self.publish()['state'], 'uncertain')
        self.assertFalse(any(r['state'] == 'split' for r in self.rows()))
        self.assertEqual(self.remote()['comments'], [])

    def test_minimal_chunk_rejection_reports_actual_cause_without_retry_loop(self):
        self.update(length_error=LENGTH_ERROR, length_limit=1)
        result = self.publish()
        self.assertEqual(result['state'], 'failed', result)
        self.assertIn('Body is too long (maximum is 65536 characters)', result['correction'])
        self.assertIn('minimal continuation cannot progress', result['correction'])
        self.assertEqual(self.remote()['comments'], [])
        self.assertEqual(self.rows()[-1]['chunk'], self.rows()[-1]['body'][-1:])
        self.assertEqual(len(self.rows()[-1]['chunk']), 1)

    def test_proof_drift_does_not_partition(self):
        self.update(post_error=422, error_on=1, error_message='fixture length rejected; no effect')
        wrong = self.proof(body='different request')
        self.assertEqual(self.publish(length_proofs=[wrong])['state'], 'failed')
        self.assertEqual(self.remote()['posts'], 1)
        self.assertFalse(any(r['state']=='split' for r in self.rows()))

    def test_partial_parts_recovery_retains_confirmed_part_without_resend(self):
        # Error first whole body, then fail second continuation via readback loss.
        self.update(post_error=422, error_on=1, error_message='fixture length rejected; no effect')
        # A gh wrapper changes fixture behavior after the first confirmed child.
        underlying = self.gh
        class FailSecondChild:
            def request(_, target, method, endpoint, body=None):
                if method=='POST' and body and ':1.2 -->' in body['body']:
                    self.update(post_error=403, error_on=self.remote()['posts']+1)
                return underlying.request(target, method, endpoint, body)
        out = self.publish(gh=FailSecondChild(), length_proofs=[self.proof()])
        self.assertEqual(out['state'], 'partial', out)
        self.assertEqual(len(out['urls']), 1)
        self.assertFalse(any(r.get('type')=='snapshot_result' for r in self.rows()))
        self.update(post_error=None)
        recovered = self.publish(snapshot_id=out['snapshot_id'])
        self.assertEqual(recovered['state'], 'confirmed', recovered)
        self.assertEqual(len(recovered['urls']), 2)
        self.assertEqual(len(self.remote()['comments']), 2)
        self.assertEqual(self.remote()['posts'], 4)  # whole reject, child1, child2 reject, child2 recovery

    def test_partial_accepted_part_lost_response_reconciles_without_resend(self):
        self.update(post_error=422, error_on=1, error_message='fixture length rejected; no effect')
        underlying = self.gh
        class LoseSecondChild:
            def request(_, target, method, endpoint, body=None):
                if method=='POST' and body and ':1.2 -->' in body['body']:
                    self.update(lost_response=True)
                return underlying.request(target, method, endpoint, body)
        out = self.publish(gh=LoseSecondChild(), length_proofs=[self.proof()])
        self.assertEqual(out['state'], 'partial', out)
        self.assertEqual(self.remote()['posts'], 3)
        self.assertEqual(len(self.remote()['comments']), 2)
        second = self.remote()['comments'][1]
        self.update(pages={'1':[], '2':[second]})
        recovered = self.publish(snapshot_id=out['snapshot_id'])
        self.assertEqual(recovered['state'], 'confirmed', recovered)
        self.assertEqual(len(recovered['urls']), 2)
        self.assertEqual(self.remote()['posts'], 3)
        self.assertEqual(''.join(r['chunk'] for r in self.rows()
                         if r.get('type')=='part' and r['state']=='confirmed'),
                         render_markdown(project_trace(self.store, 'run')))

    def test_no_effect_assertion_without_matching_source_response_is_not_proof(self):
        proof = self.proof()
        variants = [LengthProof(proof.body_sha256, proof.response_sha256, '', proof.explanation, True),
                    LengthProof(proof.body_sha256, proof.response_sha256, proof.source, '', True),
                    LengthProof(proof.body_sha256, proof.response_sha256, proof.source, proof.explanation, False),
                    LengthProof(proof.body_sha256, digest('different response'), proof.source, proof.explanation, True)]
        for variant in variants:
            with self.subTest(proof=variant):
                count = self.remote()['posts']
                self.update(post_error=422, error_on=count+1, error_message='fixture length rejected; no effect')
                out = self.publish(length_proofs=[variant])
                self.assertEqual(out['state'], 'failed', out)
                self.assertEqual(self.remote()['posts'], count+1)
        self.assertFalse(any(r['state']=='split' for r in self.rows()))

    def test_snapshot_and_prepared_target_drift_are_not_new_mutations(self):
        first = self.publish()
        snapshot = project_trace(self.store, 'run')
        snapshot['run_id'] = 'other'
        self.assertEqual(self.publish(snapshot=snapshot)['state'], 'deferred')
        out = self.publish(snapshot_id=first['snapshot_id'], target=PR,
                           authority={**self.grant,'target':PR}, known_linked_prs=[PR])
        self.assertEqual(out['state'], 'deferred', out)
        self.assertEqual(self.remote()['posts'], 1)
        self.assertEqual(self.publish(snapshot_id='missing')['state'], 'deferred')

    def test_partition_section_event_line_and_text_continuations_preserve_unicode(self):
        from coherence_workflow.trace_publication import _partition
        for text in ('# first\nα\n# second\nβ', '{\n    {"event":1}\n    {"event":2}',
                     'ordinary\nconversation\n', '🦊é漢字no-newlines'):
            pieces = _partition(text)
            self.assertEqual(''.join(pieces), text)
            self.assertTrue(all(pieces))
            self.assertTrue(all(len(p)<len(text) for p in pieces))


if __name__ == '__main__':
    unittest.main()
