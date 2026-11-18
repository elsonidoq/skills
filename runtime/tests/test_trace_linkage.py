"""Offline production gh subprocess linkage checks, not live GitHub proof."""
import unittest

import test_trace_publication as fixture
from coherence_workflow.trace_publication import confirm_delivery_links, _has_url
from coherence_workflow.trace_projection import project_trace

ISSUE, PR, API = fixture.ISSUE, fixture.PR, fixture.API
PR2 = 'https://github.com/owner/repo/pull/8'


class LinkageTests(unittest.TestCase):
    setUp = fixture.PublicationTests.setUp
    remote = fixture.PublicationTests.remote
    update = fixture.PublicationTests.update
    publish = fixture.PublicationTests.publish
    rows = fixture.PublicationTests.rows
    part_wire = fixture.PublicationTests.part_wire

    def setup_remote(self, pr_hosted=False, split=False):
        # Extend the T006 actual-subprocess fixture, preserving its intent checks.
        script = fixture.FAKE.replace("obj = {'number':n,", "obj = {'body':s.get('bodies',{}).get(str(n), ''), 'number':n,")
        script = script.replace("('/repos/owner/repo/issues/45', '/repos/owner/repo/issues/9')", "('/repos/owner/repo/issues/45', '/repos/owner/repo/issues/9', '/repos/owner/repo/issues/8')")
        script = script.replace("'/pull/9' if n==9", "'/pull/'+str(n) if n!=45")
        script = script.replace("if n==9: obj['pull_request']", "if n!=45: obj['pull_request']")
        script = script.replace("endpoint == '/repos/owner/repo/pulls/9'", "endpoint in ('/repos/owner/repo/pulls/9', '/repos/owner/repo/pulls/8')")
        script = script.replace("respond({'number':9, 'html_url':web+'/pull/9', 'issue_url':api+'/issues/9'})", "n=int(endpoint.rsplit('/',1)[1]); respond({'number':n, 'html_url':web+'/pull/'+str(n), 'issue_url':api+'/issues/'+str(n)})")
        script = script.replace("'/pull/9' if number==9", "'/pull/'+str(number) if number!=45")
        script = script.replace("items = s['comments'] if not s.get('pages') else s['pages'].get(str(page),[])", "items = ([c for c in s['comments'] if c['issue_url']==api+'/issues/'+endpoint.split('/')[5]] if not s.get('pages') else s['pages'].get(str(page),[]))")
        script = script.replace("str(s.get('destination',45))", "endpoint.split('/')[5]")
        (self.root/'gh').write_text(script)
        options = {'target':PR, 'known_linked_prs':[PR], 'authority':{**self.grant, 'target':PR}} if pr_hosted else {}
        if split:
            self.update(post_error=422, error_on=1, error_message='fixture length rejected; no effect')
            options['length_proofs'] = [fixture.PublicationTests.proof(self)]
        published = self.publish(**options)
        self.assertEqual(published['state'], 'confirmed', published)
        self.sid = published['snapshot_id']
        self.trace_urls = published['urls']
        self.grants = [{**self.grant, 'target':url, 'operations':['link_comment']} for url in (ISSUE, PR, PR2)]

    def link(self, **kwargs):
        return confirm_delivery_links(self.store, 'run', **{
            'issue':ISSUE, 'known_prs':[PR], 'snapshot_id':self.sid,
            'authorities':self.grants, 'gh':self.gh, **kwargs})

    def add_comment(self, target, body):
        remote = self.remote()
        identity = remote['next_id']
        number = target.rsplit('/', 1)[1]
        self.update(next_id=identity+1, comments=remote['comments']+[
            {'id':identity, 'url':API+'/issues/comments/'+str(identity),
             'html_url':target+'#issuecomment-'+str(identity),
             'issue_url':API+'/issues/'+number, 'body':body}])

    def test_issue_hosted_and_repeat_late_finish_never_resends_trace(self):
        self.setup_remote()
        before = project_trace(self.store, 'run')
        out = self.link()
        self.assertEqual(out['state'], 'confirmed', out)
        self.assertEqual(out['associations'], [{'issue':ISSUE, 'pr':PR}])
        self.assertEqual(self.remote()['posts'], 3)  # trace and two missing links
        self.assertEqual(self.link()['state'], 'confirmed')
        self.assertEqual(self.remote()['posts'], 3)
        self.assertEqual(project_trace(self.store, 'run'), before)
        # A later known PR adds only two links; existing trace/review untouched.
        out = self.link(known_prs=[PR, PR2])
        self.assertEqual(out['state'], 'confirmed', out)
        self.assertEqual(self.remote()['posts'], 5)
        self.assertEqual(self.link(known_prs=[PR, PR2])['state'], 'confirmed')
        self.assertEqual(self.remote()['posts'], 5)
        self.assertEqual(sum('coherence-trace:' in c['body'] for c in self.remote()['comments']), 1)

    def test_pr_hosted_trace_requires_issue_to_every_trace_part_and_reciprocity(self):
        self.setup_remote(pr_hosted=True)
        out = self.link()
        self.assertEqual(out['state'], 'confirmed', out)
        issue_comment = next(c for c in self.remote()['comments'] if c['issue_url']==API+'/issues/45')
        self.assertIn(PR, issue_comment['body'])
        for url in self.trace_urls:
            self.assertIn(url, issue_comment['body'])
        self.assertEqual(self.link()['state'], 'confirmed')
        self.assertEqual(self.remote()['posts'], 3)

    def test_pr_hosted_multipart_trace_links_also_discover_pr_without_extra_comment(self):
        self.setup_remote(pr_hosted=True, split=True)
        self.assertEqual(len(self.trace_urls), 2)
        self.update(bodies={'45':'\n'.join(self.trace_urls), '9':ISSUE})
        out = self.link(authorities=[])
        self.assertEqual(out['state'], 'confirmed', out)
        self.assertEqual(self.remote()['posts'], 3)  # rejected whole, two confirmed parts only
        self.assertEqual(out['trace_urls'], self.trace_urls)
        self.assertEqual(self.link(authorities=[])['state'], 'confirmed')
        self.assertEqual(self.remote()['posts'], 3)

    def test_missing_multipart_discovery_adds_only_missing_part_link(self):
        self.setup_remote(pr_hosted=True, split=True)
        self.update(bodies={'45':self.trace_urls[0], '9':ISSUE})
        out = self.link()
        self.assertEqual(out['state'], 'confirmed', out)
        new = self.remote()['comments'][-1]
        self.assertIn(self.trace_urls[1], new['body'])
        self.assertNotIn(self.trace_urls[0], new['body'])
        self.assertEqual(self.remote()['posts'], 4)
        self.assertEqual(self.link()['state'], 'confirmed')
        self.assertEqual(self.remote()['posts'], 4)

    def test_rejected_link_send_requires_reconciliation_and_targeted_recovery(self):
        self.setup_remote()
        self.update(post_error=403, error_on=2)
        out = self.link()
        self.assertEqual(out['state'], 'incomplete', out)
        self.assertIn('HTTP 403', out['correction'])
        self.assertEqual(self.remote()['posts'], 2)
        self.update(post_error=None)
        self.assertEqual(self.link()['state'], 'confirmed')
        self.assertEqual(self.remote()['posts'], 4)
        self.assertEqual(len(self.remote()['comments']), 3)

    def test_existing_body_and_paginated_comment_links_reused_without_scope(self):
        self.setup_remote()
        self.update(bodies={'9':'Delivery issue: '+ISSUE})
        self.add_comment(ISSUE, 'Known PR: ['+PR+']('+PR+')')
        comment = self.remote()['comments'][-1]
        self.update(pages={'1':[], '2':[comment]})
        # PR body already covers issue, so target-specific comments are unnecessary.
        out = self.link(authorities=[])
        self.assertEqual(out['state'], 'confirmed', out)
        self.assertEqual(self.remote()['posts'], 1)
        self.assertTrue(any('page=2' in c['endpoint'] for c in self.remote()['calls']))
        self.assertTrue(any(c['endpoint'].endswith('/issues/comments/'+str(comment['id'])) for c in self.remote()['calls']))

    def test_absent_or_wrong_target_operation_scope_never_writes(self):
        self.setup_remote()
        for grants in ([], [self.grant], [{**self.grants[0], 'run_id':'wrong'}],
                       [{**self.grants[0], 'target':PR}], [{**self.grants[0], 'approval_ref':''}]):
            out = self.link(authorities=grants)
            self.assertEqual(out['state'], 'incomplete', out)
            self.assertIn('link_comment authority', out['correction'])
            self.assertEqual(self.remote()['posts'], 1)

    def test_wrong_target_and_unconfirmed_trace_are_incomplete(self):
        self.setup_remote()
        for options in ({'known_prs':[ISSUE]}, {'issue':ISSUE+'0'}, {'snapshot_id':'absent'}):
            self.assertEqual(self.link(**options)['state'], 'incomplete')
        self.update(target_drift=True)
        self.assertEqual(self.link()['state'], 'incomplete')
        self.assertEqual(self.remote()['posts'], 1)

    def test_partial_authority_reports_incomplete_then_only_missing_pr_link(self):
        self.setup_remote()
        out = self.link(authorities=self.grants[:1])
        self.assertEqual(out['state'], 'incomplete', out)
        self.assertEqual(self.remote()['posts'], 2)
        self.assertEqual(self.link()['state'], 'confirmed')
        self.assertEqual(self.remote()['posts'], 3)

    def test_lost_send_response_reconciles_exact_link_without_duplicate(self):
        self.setup_remote()
        self.update(lost_response=True)
        self.assertEqual(self.link()['state'], 'incomplete')
        self.assertEqual(self.remote()['posts'], 2)
        out = self.link()
        self.assertEqual(out['state'], 'confirmed', out)
        self.assertEqual(self.remote()['posts'], 3)
        self.assertTrue(any(r.get('type')=='link' and r['state']=='confirmed' for r in self.rows()))

    def test_lost_link_readback_and_incomplete_scan_prevent_duplicates(self):
        self.setup_remote()
        underlying = self.gh
        class LoseLinkRead:
            def request(_, target, method, endpoint, body=None):
                if method=='POST':
                    self.update(readback_mismatch=True)
                return underlying.request(target, method, endpoint, body)
        out = self.link(gh=LoseLinkRead())
        self.assertEqual(out['state'], 'incomplete', out)
        self.assertEqual(self.remote()['posts'], 2)
        self.update(readback_mismatch=False, pages={'1':[], '2':[]}, incomplete_page=True)
        self.assertEqual(self.link()['state'], 'incomplete')
        self.assertEqual(self.remote()['posts'], 2)
        self.update(pages=None, incomplete_page=False)
        self.assertEqual(self.link()['state'], 'confirmed')
        self.assertEqual(self.remote()['posts'], 3)

    def test_pending_marker_collision_stops_link_mutation(self):
        self.setup_remote()
        self.update(lost_response=True)
        self.link()
        comments = self.remote()['comments']
        comments[-1]['body'] += '\nchanged'
        self.update(comments=comments)
        out = self.link()
        self.assertEqual(out['state'], 'incomplete', out)
        self.assertEqual(self.remote()['posts'], 2)

    def test_link_target_matching_rejects_suffix_and_other_comment(self):
        for suffix in ('0', '/files', '?other', '#issuecomment-55'):
            self.assertFalse(_has_url('See '+ISSUE+suffix, ISSUE))
        for body in ('See '+ISSUE, '['+ISSUE+']('+ISSUE+')', ISSUE+'\n', '<a href="'+ISSUE+'">issue</a>'):
            self.assertTrue(_has_url(body, ISSUE))
        for body in ('`'+ISSUE+'`', '<!-- '+ISSUE+' -->', '```json\n"'+ISSUE+'"\n```\n',
                     '<!-- coherence-trace:part -->\nTrace continuation\n"'+ISSUE+'"'):
            self.assertFalse(_has_url(body, ISSUE))


if __name__ == '__main__':
    unittest.main()
