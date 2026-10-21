"""T012/V2 synthetic usage persistence and safe CLI reporting."""
import json
import sqlite3
from unittest.mock import patch

from coherence_workflow.cli import status
from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.store import Authority
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium'}


def interval(session, input_tokens, usd):
    return {
        'session_id': session, 'branch': 'main', 'epoch': 'one', 'outcome': 'settled',
        'tokens': {name: {'value': value, 'unknown_reason': None, 'provenance': 'fixture'}
                   for name, value in {'input': input_tokens, 'output': 2,
                                       'cache_read': 1, 'cache_write': 0}.items()},
        'total_tokens': {'value': input_tokens + 3, 'unknown_reason': None, 'provenance': 'fixture'},
        'estimated_usd': {'value': usd, 'unknown_reason': None, 'provenance': 'fixture'},
        'compactions': {'entry_ids': [], 'count': 0, 'unknown_reason': None},
        'summary_overhead': {'entries': [], 'unknown_reason': None, 'included_in_sdk_deltas': True},
    }


class UsageReportingTests(ProjectTest):
    def test_engine_store_and_cli_keep_distinct_membership_and_reviewer_totals_private(self):
        project = self.project

        class Adapter:
            def __init__(self, *_args, **_kwargs):
                self.last_interval = None
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    self.last_interval = interval('review-session', 7, .07)
                    return '{"approved":true,"findings":[]}'
                if 'REQUIRED check' in prompt:
                    project.joinpath('ready').write_text('ready\n')
                    self.last_interval = interval('worker-session', 3, .03)
                    return 'corrected'
                kwargs['claim']('owned.txt')
                project.joinpath('owned.txt').write_text('done\n')
                self.last_interval = interval('worker-session', 5, .05)
                return 'synthetic worker PRIVATE-ANSWER'

        contract = admit({'tasks': [{'id': 'usage', 'description': 'PRIVATE TASK TEXT',
                                     'owned_paths': ['owned.txt'],
                                     'checks': [["python3", "-B", "-c", "from pathlib import Path; assert Path('ready').exists()"]]}]})
        with Authority(project) as owner:
            result = Engine(owner, 'usage', contract, EXECUTOR, adapter=Adapter).invoke()
        self.assertEqual(result['usage']['memberships'], ['usage'])
        self.assertEqual(result['usage']['interval_count'], 3)
        self.assertEqual(result['usage']['worker_totals']['input'], 8)
        self.assertEqual(result['usage']['reviewer_totals']['input'], 7)
        self.assertEqual(result['usage']['worker_totals']['estimated_usd'], .08)
        observed = status(project, 'usage')
        self.assertEqual(observed['usage']['reviewer_totals']['estimated_usd'], .07)
        self.assertNotIn('PRIVATE TASK TEXT', json.dumps(observed))
        self.assertNotIn('PRIVATE-ANSWER', json.dumps(observed))
        db = sqlite3.connect(project/'.coherence/workflow/workflow.sqlite')
        self.assertEqual(db.execute("SELECT count(*) FROM execution_usage_memberships WHERE run_id='usage'").fetchone()[0], 1)
        self.assertEqual(db.execute("SELECT count(*) FROM execution_usage_intervals WHERE run_id='usage' AND role='reviewer' AND task_id IS NULL").fetchone()[0], 1)
        db.close()

    def test_optional_usage_failure_keeps_actual_task_outcome_and_legacy_is_unknown(self):
        project = self.project
        class Adapter:
            def __init__(self, *_args, **_kwargs): self.last_interval = interval('worker', 1, .01)
            def prompt(self, _prompt, **kwargs):
                return '{"approved":true,"findings":[]}' if kwargs.get('read_only') else 'done'
        with Authority(project) as owner:
            with patch.object(owner.store, 'usage_interval', return_value=False):
                result = Engine(owner, 'gap', admit([{'id': 'task', 'description': 'synthetic'}]),
                                EXECUTOR, adapter=Adapter).invoke()
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(result['usage']['state'], 'partial')
        with Authority(project) as owner:
            owner.store.start('legacy', 'legacy-base')
        self.assertEqual(status(project, 'legacy')['usage'], {'state': 'unknown', 'reason': 'usage_unavailable'})
