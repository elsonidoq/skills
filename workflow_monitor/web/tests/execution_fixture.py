"""Disposable recorded execution fixture + production HTTP; no model/provider calls."""
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'runtime')]
from coherence_workflow.monitoring import Recorder, descriptor
from coherence_workflow.store import Authority, git
from workflow_monitor.app import create_app
from workflow_monitor.reader import Reader
import uvicorn


def emit(recorder, occurrence, phase, kind, *, task='one', **facts):
    recorder.emit(occurrence, phase, kind, task_id=task, facts=facts)


with tempfile.TemporaryDirectory(prefix='monitor-execution-fixture-') as temporary:
    project = Path(temporary)
    git(project, 'init', '-q')
    git(project, 'config', 'user.name', 'Offline fixture')
    git(project, 'config', 'user.email', 'fixture@example.invalid')
    (project / 'tracked').write_text('offline fixture\n')
    git(project, 'add', 'tracked'); git(project, 'commit', '-qm', 'fixture')
    base = git(project, 'rev-parse', 'HEAD').decode().strip()
    presentation = descriptor({'tasks': [{'id': 'one', 'depends': []}], 'monitor': {'tasks': {'one': {'label': 'T001'}}}}, {})
    with Authority(project) as owner:
        for run in ('stopping', 'before-agent', 'waiting', 'success'):
            owner.store.start(run, base)
            recorder = Recorder(owner.store, run)
            recorder.register(presentation)
            emit(recorder, 'terminal', 'terminal', 'started', task=None, baseline=base)
            if run == 'before-agent':
                emit(recorder, 'prepare', 'prepare', 'started')
                emit(recorder, 'prepare', 'prepare', 'failed', error_category='blocked')
                emit(recorder, 'terminal', 'terminal', 'failed', task=None)
            else:
                emit(recorder, 'worker', 'worker', 'started', role='worker')
                if run == 'waiting':
                    emit(recorder, 'question', 'worker', 'question_requested', parent_occurrence_id='worker')
                else:
                    emit(recorder, 'worker', 'worker', 'returned', role='worker')
                    if run == 'success':
                        emit(recorder, 'recovered-check', 'check', 'failed', ordinal=0, exit_code=1)
                    emit(recorder, 'check', 'check', 'started', ordinal=1)
                    emit(recorder, 'check', 'check', 'failed' if run == 'stopping' else 'passed', ordinal=1, exit_code=1 if run == 'stopping' else 0)
                    if run == 'success':
                        emit(recorder, 'checkpoint', 'checkpoint', 'passed', baseline=base, head=base, no_change=True)
                        emit(recorder, 'review', 'review', 'started', task=None, role='reviewer', review_base=base, review_head=base)
                        emit(recorder, 'review', 'review', 'passed', task=None, role='reviewer', approved=True, finding_count=0, review_base=base, review_head=base)
                    emit(recorder, 'terminal', 'terminal', 'failed' if run == 'stopping' else 'passed', task=None, head=base)
            owner.store.db.execute('UPDATE execution_runs SET state=? WHERE run_id=?', ('failed' if run in ('stopping', 'before-agent') else 'completed', run))
    uvicorn.run(create_app(Reader(project), ROOT / 'workflow_monitor/web/dist', 4174), host='127.0.0.1', port=4174, access_log=False, log_level='critical')
