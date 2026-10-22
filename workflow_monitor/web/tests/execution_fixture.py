"""Disposable recorded execution fixture + production HTTP; no model/provider calls."""
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'runtime')]
sys.path.append('/usr/lib/python3/dist-packages')  # Prepared system PyYAML, after venv packages.
from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.monitoring import Recorder, descriptor
from coherence_workflow.metric_artifacts import create_artifact
from coherence_workflow.store import Authority, git
from workflow_monitor.app import create_app
from workflow_monitor.reader import Reader
import uvicorn


def emit(recorder, occurrence, phase, kind, *, task='one', **facts):
    recorder.emit(occurrence, phase, kind, task_id=task, facts=facts)


def metric_record(run, invocation, mode, actual, *, partial=False):
    field = lambda value: {'value': value, 'unknown_reason': None, 'provenance': 'fixture'}
    before = {'counters': {'input': 10, 'output': 20, 'cacheRead': 0, 'cacheWrite': 0, 'total': 30}, 'estimated_usd': .25,
              'context': {'context_window': 100, 'effective_reserve': 20, 'occupancy': 90, 'compaction_enabled': False, 'compaction_applicable': True}, 'compaction_entry_ids': []}
    after = {'counters': {'input': 15, 'output': 27, 'cacheRead': 0, 'cacheWrite': 0, 'total': 42}, 'estimated_usd': .5,
             'context': {'context_window': 100, 'effective_reserve': 20, 'occupancy': 110, 'compaction_enabled': True, 'compaction_applicable': True}, 'compaction_entry_ids': ['compact-one']}
    interval = {'session_id': 'session-one', 'branch': 'branch-one', 'epoch': 'epoch-one', 'outcome': 'settled',
                'tokens': {'input': field(5), 'output': field(7), 'cache_read': field(0), 'cache_write': field(0)},
                'total_tokens': field(12), 'estimated_usd': field(.25),
                'compactions': {'entry_ids': ['compact-one'], 'count': 1, 'unknown_reason': None},
                'summary_overhead': {'entries': [{'entry_id': 'compact-one', 'unknown_reason': None, 'usage': {'input': 1, 'output': 2, 'cacheRead': 0, 'cacheWrite': 0, 'totalTokens': 3, 'cacheWrite1h': 0, 'reasoning': 1, 'cost': {'input': 0, 'output': 0, 'cacheRead': 0, 'cacheWrite': 0, 'total': 0}}}], 'unknown_reason': None, 'included_in_sdk_deltas': True}}
    if partial:
        interval['tokens']['output'] = {'value': None, 'unknown_reason': 'missing_end', 'provenance': 'fixture'}
    return {'version': 1, 'run_id': run, 'invocation_id': invocation, 'task_id': 'one', 'role': 'worker', 'outcome': 'settled', 'fixing_round': None, 'review_ordinal': None, 'interval': interval, 'before': before, 'after': after, 'selected_session_mode': mode, 'session_selection_reason': 'fixture-selection', 'actual_session_mode': actual, 'actual_session_id': 'session-one'}


with tempfile.TemporaryDirectory(prefix='monitor-execution-fixture-') as temporary:
    project = Path(temporary)
    git(project, 'init', '-q')
    git(project, 'config', 'user.name', 'Offline fixture')
    git(project, 'config', 'user.email', 'fixture@example.invalid')
    (project / 'tracked').write_text('offline fixture\n')
    git(project, 'add', 'tracked'); git(project, 'commit', '-qm', 'fixture')
    base = git(project, 'rev-parse', 'HEAD').decode().strip()
    presentation = descriptor({'tasks': [{'id': 'one', 'depends': []}, {'id': 'two', 'depends': ['one']}, {'id': 'three', 'depends': []}], 'monitor': {'tasks': {'one': {'label': 'T001'}, 'two': {'label': 'T002'}, 'three': {'label': 'T003'}}}}, {})
    # Simulate already-retained prose; no producer behavior is changed.
    presentation['tasks'][0]['work_description'] = '<img src=x onerror=alert(1)> Recorded workflow explanation opaque-invocation-identity ' * 12
    presentation['tasks'][1]['work_description'] = None
    with Authority(project) as owner:
        class CorrectionAdapter:
            calls = 0
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, **kwargs):
                self.last_interval = metric_record('engine-correction', 'supplied-interval', 'fresh', 'fresh')['interval']
                if kwargs.get('read_only'):
                    return '{"approved":true,"findings":[]}'
                CorrectionAdapter.calls += 1
                kwargs['claim']('correction.txt')
                (project/'correction.txt').write_text('broken' if CorrectionAdapter.calls == 1 else 'fixed')
                return 'offline correction'
        Engine(owner, 'engine-correction', admit({'monitor': {'correction_of': {'run_id': 'original', 'review_execution_id': 'review-id'}},
            'tasks': [{'id': 'fix', 'description': 'Correct original result', 'owned_paths': ['correction.txt'],
                       'checks': [['/bin/sh', '-c', 'test "$(cat correction.txt)" = fixed']]}]}),
            {'provider': 'fixture', 'model': 'offline', 'effort': 'medium', 'reviewer': {'provider': 'fixture', 'model': 'offline', 'effort': 'medium'}}, adapter=CorrectionAdapter,
            question=lambda _: 'fixture correction', paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
        for run in ('stopping', 'before-agent', 'waiting', 'success', 'metrics-reused', 'metrics-continued', 'metrics-unknown', 'metrics-partial', 'metrics-composed', 'merged-edge', 'review-dispatched', 'review-started', 'review-waiting', 'review-returned', 'review-conflict', 'answered-paged', 'booleans-true', 'booleans-false', 'manual-waiting', 'manual-answered', 'manual-delivery', 'manual-stopped', 'slash/%? #東京', 'actual(run)', '...'):
            owner.store.start(run, base)
            recorder = Recorder(owner.store, run)
            recorder.register(descriptor({'tasks': [{'id': 'edge', 'description': 'Prepare usable input'}],
                'monitor': {'tasks': {'edge': {'label': 'Prepare result'}}}}, {}) if run == 'merged-edge' else presentation)
            emit(recorder, 'terminal', 'terminal', 'started', task=None, baseline=base)
            if run == 'merged-edge':
                inputs = [{'checkpoint_occurrence_id': 'edge-checkpoint', 'task_id': 'edge',
                           'producer_invocation_id': 'edge-first', 'correction_chain': ['edge-first']}]
                for identity, kind, selected, chain in [('edge-first', 'task_worker', [], ['edge-first']),
                        ('edge-second', 'corrective_worker', inputs, ['edge-first', 'edge-second'])]:
                    if identity == 'edge-second':
                        emit(recorder, 'edge-checkpoint', 'checkpoint', 'passed', task='edge', baseline=base, head=base,
                             no_change=True, producer_invocation_id='edge-first', correction_chain=['edge-first'])
                    for state in ('started', 'returned'):
                        emit(recorder, identity, 'worker', state, task='edge', role='worker', invocation_id=identity,
                             invocation_kind=kind, selected_input_checkpoints=selected, correction_chain=chain)
                continue
            if run.startswith('review-'):
                owner.store.review_dispatch(run, 'private-review-two', role='reviewer', review_ordinal=2, fixing_round=1, review_base=base, review_head=base)
                if run != 'review-dispatched':
                    facts = {'role': 'reviewer', 'execution_id': 'private-review-two', 'review_ordinal': 2, 'review_base': base, 'review_head': base}
                    emit(recorder, 'review-two', 'review', 'started', task=None, **facts)
                    if run == 'review-waiting':
                        emit(recorder, 'review-question', 'review', 'question_requested', task=None, parent_occurrence_id='review-two')
                    if run in ('review-returned', 'review-conflict'):
                        emit(recorder, 'review-two', 'review', 'returned', task=None, **facts)
                        owner.store.review_outcome(run, 'private-review-two', 'rejected', findings=['Correct the result'], references={'base': base, 'head': base})
                    if run == 'review-conflict':
                        emit(recorder, 'review-two', 'review', 'failed', task=None, **facts)
                continue
            if run == 'metrics-composed':
                conflicting_record = None
                artifact = create_artifact(project, run, authority=owner)
                for identity, task, role, kind, record_role in [('initial', 'one', 'worker', 'task_worker', 'worker'), ('correction', 'one', 'worker', 'corrective_worker', 'corrective_worker'), ('missing', 'one', 'worker', 'corrective_worker', 'corrective_worker'), ('other', 'two', 'worker', 'task_worker', 'worker'), ('wrong', 'one', 'worker', 'task_worker', 'worker'), ('conflict', 'one', 'worker', 'task_worker', 'worker'), ('reviewer', None, 'reviewer', None, 'reviewer')]:
                    identity_facts = {'execution_id': identity, 'review_base': base, 'review_head': base, 'review_ordinal': 1} if role == 'reviewer' else {'invocation_id': identity, 'invocation_kind': kind, 'correction_chain': [identity]}
                    if role == 'reviewer':
                        owner.store.review_dispatch(run, identity, role='reviewer', review_ordinal=1, fixing_round=0, review_base=base, review_head=base)
                        owner.store.review_outcome(run, identity, 'approved', findings=[], references={'base': base, 'head': base})
                    else:
                        owner.store.history(run, task, 'worker_invocation', 'started', {'invocation_id': identity})
                    for state in ('started', 'returned'):
                        emit(recorder, identity, 'review' if role == 'reviewer' else 'worker', state, task=task, role=role, selected_input_checkpoints=[], **identity_facts)
                    if identity == 'missing':
                        continue
                    record = metric_record(run, identity, 'fresh', 'fresh')
                    record.update(task_id='two' if identity == 'wrong' else task, role=record_role)
                    if role == 'reviewer':
                        record['review_ordinal'] = 1
                    artifact.append(record)
                    if identity == 'conflict':
                        conflicting_record = record
                # Inject external corruption only after the legitimate writer is done;
                # its ownership checks must not be bypassed for a later append.
                import json
                conflicting_record['interval']['total_tokens']['value'] = 999
                with artifact.path.open('a') as output:
                    output.write(json.dumps(conflicting_record) + '\n')
                owner.store.history(run, None, 'metric_artifact', 'failed', {'status': 'failed', 'path': str(artifact.path.relative_to(project)), 'error': '/PRIVATE/error'})
                continue
            if run == 'before-agent':
                emit(recorder, 'prepare', 'prepare', 'started')
                emit(recorder, 'prepare', 'prepare', 'failed', error_category='blocked')
                emit(recorder, 'terminal', 'terminal', 'failed', task=None)
            elif run.startswith('manual-'):
                for ordinal in range(49):
                    emit(recorder, f'noise-{ordinal}', 'check', 'started', task=None, ordinal=ordinal)
                emit(recorder, 'gate', 'gate', 'started', ordinal=1)
                emit(recorder, 'gate-question', 'gate', 'question_requested', ordinal=1, parent_occurrence_id='gate')
                if run == 'manual-answered':
                    emit(recorder, 'gate-question', 'gate', 'answer_returned', ordinal=1, parent_occurrence_id='gate')
                    emit(recorder, 'gate', 'gate', 'passed', ordinal=1)
                elif run == 'manual-delivery':
                    emit(recorder, 'gate-question', 'gate', 'delivery_failed', ordinal=1, parent_occurrence_id='gate', error_category='blocked')
                    emit(recorder, 'gate', 'gate', 'failed', ordinal=1, error_category='blocked')
                elif run == 'manual-stopped':
                    emit(recorder, 'terminal', 'terminal', 'failed', task=None)
            else:
                invocation = f'{run}-worker' if run in ('success', 'waiting') or run.startswith('metrics-') else None
                if invocation:
                    owner.store.history(run, 'one', 'worker_invocation', 'started', {'invocation_id': invocation})
                worker_facts = {'role': 'worker', **({'invocation_id': invocation, 'invocation_kind': 'task_worker', 'selected_input_checkpoints': [], 'correction_chain': [invocation]} if invocation else {})}
                emit(recorder, 'worker', 'worker', 'started', **worker_facts)
                if run == 'waiting':
                    emit(recorder, 'question', 'worker', 'question_requested', parent_occurrence_id='worker')
                elif run.startswith('booleans-'):
                    value = run == 'booleans-true'
                    for ordinal in range(48):
                        emit(recorder, f'check-{ordinal}', 'check', 'passed', ordinal=ordinal, exit_code=0)
                    emit(recorder, 'worker', 'worker', 'returned', role='worker')
                    emit(recorder, 'checkpoint', 'checkpoint', 'passed', baseline=base, head=base, no_change=value)
                    emit(recorder, 'review', 'review', 'passed' if value else 'failed', task=None, role='reviewer',
                         approved=value, finding_count=0 if value else 1, review_base=base, review_head=base)
                    emit(recorder, 'terminal', 'terminal', 'passed', task=None, head=base)
                elif run == 'answered-paged':
                    # The request is the 50th retained record; its answers are on page two.
                    for ordinal in range(47):
                        emit(recorder, f'check-{ordinal}', 'check', 'passed', ordinal=ordinal, exit_code=0)
                    emit(recorder, 'question', 'worker', 'question_requested', parent_occurrence_id='worker')
                    emit(recorder, 'question', 'worker', 'answer_returned', parent_occurrence_id='worker')
                    emit(recorder, 'question', 'worker', 'answer_sent', parent_occurrence_id='worker')
                    emit(recorder, 'worker', 'worker', 'returned', role='worker')
                    emit(recorder, 'terminal', 'terminal', 'passed', task=None, head=base)
                else:
                    emit(recorder, 'worker', 'worker', 'returned', **worker_facts)
                    if run == 'success':
                        emit(recorder, 'recovered-check', 'check', 'failed', ordinal=0, exit_code=1)
                    emit(recorder, 'check', 'check', 'started', ordinal=1)
                    emit(recorder, 'check', 'check', 'failed' if run == 'stopping' else 'passed', ordinal=1, exit_code=1 if run == 'stopping' else 0)
                    if run == 'success':
                        emit(recorder, 'checkpoint', 'checkpoint', 'passed', baseline=base, head=base, no_change=True)
                        # A typed rejecting verdict is a returned reviewer execution, not acceptance.
                        emit(recorder, 'review', 'review', 'started', task=None, role='reviewer', review_base=base, review_head=base)
                        emit(recorder, 'review', 'review', 'failed', task=None, role='reviewer', approved=False, finding_count=2, review_base=base, review_head=base)
                    emit(recorder, 'terminal', 'terminal', 'failed' if run == 'stopping' else 'passed', task=None, head=base)
            if run == 'success' or run.startswith('metrics-'):
                modes = {'success': ('fresh', 'fresh'), 'metrics-reused': ('reused_from_earlier_task', 'reused_from_earlier_task'), 'metrics-continued': ('continued_same_task', 'continued_same_task'), 'metrics-unknown': ('unknown', 'unknown'), 'metrics-partial': ('fresh', 'fresh')}
                artifact = create_artifact(project, run, authority=owner)
                artifact.append(metric_record(run, f'{run}-worker', *modes[run], partial=run == 'metrics-partial'))
                if run == 'metrics-partial':
                    # A retained malformed tail makes coverage partial while the valid
                    # invocation above remains safely visible through the production reader.
                    with artifact.path.open('a') as output:
                        output.write('{invalid metric record}\n')
            owner.store.db.execute('UPDATE execution_runs SET state=? WHERE run_id=?', ('failed' if run in ('stopping', 'before-agent') else 'completed', run))
    uvicorn.run(create_app(Reader(project), ROOT / 'workflow_monitor/web/dist', 4174), host='127.0.0.1', port=4174, access_log=False, log_level='critical')
