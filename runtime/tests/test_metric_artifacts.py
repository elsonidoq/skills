"""Real-file contract tests for the optional closed metrics artifact."""
import os
from contextlib import nullcontext
import json
from unittest.mock import patch

from coherence_workflow.engine import Engine
from coherence_workflow.git_effects import MetricArtifactFinalizer
from coherence_workflow.intake import admit
from coherence_workflow.metric_artifacts import (MetricArtifactError, artifact_relative,
                                                  create_artifact, read_artifact,
                                                  summarize_artifact)
from coherence_workflow.metrics import interval_record
from coherence_workflow.store import Authority, git
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'offline-reviewer', 'effort': 'medium'}}


def observation(input=10, *, output=5, cache_read=2, cache_write=1, usd=.1):
    return {'session_id': 'private-session', 'branch': 'b', 'epoch': 'e',
            'counters': {'input': input, 'output': output, 'cacheRead': cache_read, 'cacheWrite': cache_write},
            'costs': {'estimated_usd': usd}, 'compaction_entries': []}


def snapshot(value):
    return {'counters': {'input': value, 'output': 5, 'cacheRead': 2, 'cacheWrite': 1, 'total': value + 8},
            'estimated_usd': .1,
            'context': {'context_window': 100, 'effective_reserve': 10, 'occupancy': 20,
                        'compaction_enabled': True, 'compaction_applicable': True},
            'compaction_entry_ids': []}


def record(run='run/with unicode π', invocation='call-1', *, after=True):
    return {'version': 1, 'run_id': run, 'invocation_id': invocation, 'task_id': 'T011',
            'role': 'worker', 'outcome': 'settled', 'fixing_round': None, 'review_ordinal': None,
            'interval': interval_record(observation(), observation(12)) if after else interval_record(observation(), None),
            'before': snapshot(10), 'after': snapshot(12) if after else None,
            'selected_session_mode': 'reused_from_earlier_task', 'session_selection_reason': 'latest_successful_settlement',
            'actual_session_mode': 'unknown' if not after else 'reused_from_earlier_task',
            'actual_session_id': None if not after else 'session-actual'}


class MetricArtifactTests(ProjectTest):
    def test_closed_jsonl_round_trip_preserves_exact_ids_unknown_failure_and_safe_values(self):
        run = 'run/with unicode π'
        self.assertTrue(artifact_relative(run).endswith('.jsonl'))
        self.assertNotIn(run, artifact_relative(run))
        with Authority(self.project) as authority:
            artifact = create_artifact(self.project, run, authority=authority)
            artifact.append(record(run))
            artifact.append(record(run, 'call-2', after=False) | {'outcome': 'failed'})
        data = read_artifact(self.project, run)
        self.assertEqual([row['invocation_id'] for row in data['records']], ['call-1', 'call-2'])
        self.assertEqual(data['records'][1]['after'], None)
        self.assertEqual(data['records'][1]['actual_session_mode'], 'unknown')
        self.assertEqual(data['records'][0]['interval']['tokens']['input']['value'], 2)
        summary = summarize_artifact(self.project, run, expected_invocation_ids=['call-1', 'call-2'])
        self.assertEqual(summary['token_subtotal']['input'], 2)
        self.assertEqual(summary['coverage'], 'partial')

    def test_rejects_arbitrary_nested_payload_and_does_not_upgrade_selected_mode(self):
        with Authority(self.project) as authority:
            artifact = create_artifact(self.project, 'closed', authority=authority)
            bad = record('closed')
            bad['before']['private_payload'] = {'credential': 'no'}
            with self.assertRaisesRegex(MetricArtifactError, 'invalid metric fields'):
                artifact.append(bad)
            selected_only = record('closed')
            selected_only['actual_session_mode'] = 'unknown'
            selected_only['actual_session_id'] = None
            artifact.append(selected_only)
        row = read_artifact(self.project, 'closed')['records'][0]
        self.assertEqual(row['selected_session_mode'], 'reused_from_earlier_task')
        self.assertEqual(row['actual_session_mode'], 'unknown')

    def test_collision_symlink_drift_and_incomplete_tail_preserve_existing_bytes(self):
        run = 'safety'
        path = self.project / artifact_relative(run)
        path.parent.mkdir(parents=True)
        path.write_text('preexisting\n')
        with Authority(self.project) as authority:
            with self.assertRaisesRegex(MetricArtifactError, 'already exists'):
                create_artifact(self.project, run, authority=authority)
            path.unlink()
            outside = self.project / 'outside'
            outside.write_text('x')
            path.symlink_to(outside)
            with self.assertRaisesRegex(MetricArtifactError, 'symlink'):
                create_artifact(self.project, run, authority=authority)
            path.unlink()
            artifact = create_artifact(self.project, run, authority=authority)
            artifact.append(record(run))
            original = path.read_bytes()
            with open(path, 'ab') as handle:
                handle.write(b'{"partial":')
            partial = read_artifact(self.project, run)
            self.assertEqual(partial['coverage'], 'partial')
            self.assertIn('incomplete_tail', partial['reasons'])
            with self.assertRaisesRegex(MetricArtifactError, 'incomplete_tail'):
                artifact.append(record(run, 'later'))
            self.assertEqual(path.read_bytes(), original + b'{"partial":')

    def test_replaced_artifact_is_refused_without_touching_replacement(self):
        run = 'drift'
        with Authority(self.project) as authority:
            artifact = create_artifact(self.project, run, authority=authority)
            artifact.append(record(run))
            artifact.path.unlink()
            artifact.path.write_text('replacement\\n')
            with self.assertRaises(MetricArtifactError):
                artifact.append(record(run, 'later'))
            self.assertEqual(artifact.path.read_text(), 'replacement\\n')

    def test_runner_finalizer_commits_only_metric_file_and_preserves_unrelated_index(self):
        run = 'finalize'
        # The production rule ignores only private workflow state; metrics stay trackable.
        self.write('.gitignore', '.coherence/workflow/\n')
        git(self.project, 'add', '--', '.gitignore')
        git(self.project, 'commit', '-qm', 'track metrics')
        self.write('other.txt', 'unrelated staged bytes\n')
        git(self.project, 'add', '--', 'other.txt')
        staged = git(self.project, 'show', ':other.txt')
        with Authority(self.project) as authority:
            artifact = create_artifact(self.project, run, authority=authority)
            artifact.append(record(run))
            result = MetricArtifactFinalizer(
                self.project, artifact_relative(run),
                lambda: read_artifact(self.project, run, strict=True)).commit()
        self.assertFalse(result['no_change'])
        self.assertEqual(git(self.project, 'rev-parse', result['sha'] + '^').decode().strip(), result['parent'])
        self.assertEqual(git(self.project, 'show', '--name-only', '--format=', result['sha']).decode().splitlines(),
                         [artifact_relative(run)])
        self.assertEqual(git(self.project, 'show', ':other.txt'), staged)

    def test_engine_commits_metrics_after_final_reviewer_without_changing_reviewed_sha(self):
        self.write('.gitignore', '.coherence/workflow/\n')
        git(self.project, 'add', '--', '.gitignore')
        git(self.project, 'commit', '-qm', 'track metrics')
        class Adapter:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, **kwargs):
                return '{"approved":true,"findings":[]}' if kwargs.get('read_only') else '{"status":"completed","summary":"done"}'

        with Authority(self.project) as authority:
            result = Engine(authority, 'terminal-calls', admit([{'id': 'metric', 'description': 'fixture'}]),
                            EXECUTOR, adapter=Adapter).invoke()
        artifact = result['metric_artifact']
        self.assertEqual(artifact['status'], 'committed')
        self.assertNotEqual(result['sha'], artifact['sha'])
        self.assertEqual(artifact['parent'], result['sha'])
        self.assertEqual([row['role'] for row in read_artifact(self.project, 'terminal-calls')['records']],
                         ['worker', 'reviewer'])

    def test_controlled_worker_failure_still_finalizes_its_terminal_metric(self):
        self.write('.gitignore', '.coherence/workflow/\n')
        git(self.project, 'add', '--', '.gitignore')
        git(self.project, 'commit', '-qm', 'track metrics')
        class FailingAdapter:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, **_kwargs):
                raise RuntimeError('controlled worker failure')

        with Authority(self.project) as authority:
            with self.assertRaisesRegex(RuntimeError, 'controlled worker failure'):
                Engine(authority, 'failed-terminal-call', admit([{'id': 'metric', 'description': 'fixture'}]),
                       EXECUTOR, adapter=FailingAdapter).invoke()
        rows = read_artifact(self.project, 'failed-terminal-call')['records']
        self.assertEqual([(row['role'], row['outcome']) for row in rows], [('worker', 'failed')])
        self.assertEqual(git(self.project, 'show', '--name-only', '--format=', 'HEAD').decode().splitlines(),
                         [artifact_relative('failed-terminal-call')])

    def test_finalizer_faults_preserve_original_success_or_worker_error(self):
        original_finalize = Engine._finalize_metric_artifact
        for fault in ('missing', 'replaced', 'symlink', 'constructor'):
            for failing in (False, True):
                with self.subTest(fault=fault, failing=failing):
                    run = f'fault-{fault}-{failing}'
                    original_error = RuntimeError('original worker error')
                    class Adapter:
                        def __init__(self, *_args, **_kwargs): pass
                        def prompt(self, _prompt, **kwargs):
                            if failing:
                                raise original_error
                            return '{"approved":true,"findings":[]}' if kwargs.get('read_only') else '{"status":"completed","summary":"done"}'
                    retained = {}
                    def finalize(engine, result=None):
                        path = engine.metric_artifact.path
                        retained['original'] = path.read_bytes()
                        if fault != 'constructor':
                            path.unlink()
                            if fault == 'replaced':
                                path.write_bytes(retained['original'])
                            elif fault == 'symlink':
                                target = self.project / f'{run}-target'
                                target.write_bytes(retained['original'])
                                path.symlink_to(target)
                        return original_finalize(engine, result)
                    with Authority(self.project) as authority:
                        engine = Engine(authority, run, admit([{'id': 'metric', 'description': 'fixture'}]),
                                        EXECUTOR, adapter=Adapter)
                        head = git(self.project, 'rev-parse', 'HEAD')
                        with patch.object(Engine, '_finalize_metric_artifact', finalize):
                            with patch('coherence_workflow.engine.MetricArtifactFinalizer', side_effect=RuntimeError('constructor fault')) if fault == 'constructor' else nullcontext():
                                if failing:
                                    with self.assertRaises(RuntimeError) as caught:
                                        engine.invoke()
                                    self.assertIs(caught.exception, original_error)
                                else:
                                    result = engine.invoke()
                                    self.assertEqual(result['metric_artifact']['status'], 'failed')
                        row = authority.store.db.execute("SELECT details FROM execution_history WHERE run_id=? AND kind='metric_artifact' ORDER BY seq DESC LIMIT 1", (run,)).fetchone()
                        self.assertEqual(json.loads(row['details'])['status'], 'failed')
                        self.assertEqual(git(self.project, 'rev-parse', 'HEAD'), head)
                        self.assertEqual(git(self.project, 'diff', '--cached', '--name-only'), b'')
                        path = engine.metric_artifact.path
                        if fault == 'missing':
                            self.assertFalse(path.exists())
                        else:
                            self.assertEqual(path.read_bytes(), retained['original'])
                            self.assertEqual(path.is_symlink(), fault == 'symlink')

    def test_staged_collision_and_expected_coverage_are_qualified(self):
        run = 'staged'
        path = self.project / artifact_relative(run)
        path.parent.mkdir(parents=True)
        path.write_text('x')
        git(self.project, 'add', '-f', '--', artifact_relative(run))
        with Authority(self.project) as authority:
            with self.assertRaisesRegex(MetricArtifactError, 'dirty or staged'):
                create_artifact(self.project, run, authority=authority)
            git(self.project, 'reset', '-q', '--', artifact_relative(run))
            path.unlink()
            artifact = create_artifact(self.project, run, authority=authority)
            artifact.append(record(run))
            summary = summarize_artifact(self.project, run, expected_invocation_ids=['call-1', 'missing'])
            self.assertEqual(summary['coverage'], 'partial')
            self.assertIn('missing_expected_invocations', summary['reasons'])
