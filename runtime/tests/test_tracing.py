"""Final-wire local OTLP privacy and actual graph continuation checks; no service."""
import contextlib
import io
import json
import os
from pathlib import Path
import threading
import unittest
from unittest.mock import patch

import requests
from langsmith._httpx import httpx as langsmith_httpx
from google.protobuf.json_format import MessageToDict
from opentelemetry import baggage, context, trace
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
from opentelemetry.trace import NonRecordingSpan, SpanContext, TraceFlags, TraceState

from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.metrics import interval_record
from coherence_workflow.store import Authority, git
from coherence_workflow.tracing import ENDPOINT, LocalTracing, record_interval
from fixtures.support import ProjectTest

PRIVATE = 'PRIVATE_SENTINEL'
AUTH = 'Bearer explicit-local-token'
ENV = {
    'OTEL_EXPORTER_OTLP_ENDPOINT': 'https://remote.invalid/' + PRIVATE,
    'OTEL_EXPORTER_OTLP_TRACES_ENDPOINT': 'https://remote.invalid/' + PRIVATE,
    'OTEL_EXPORTER_OTLP_HEADERS': 'authorization=ambient-' + PRIVATE + ',x-private=' + PRIVATE,
    'OTEL_EXPORTER_OTLP_TRACES_HEADERS': 'cookie=' + PRIVATE + ',x-token=' + PRIVATE,
    'OTEL_RESOURCE_ATTRIBUTES': 'host.name=' + PRIVATE + ',service.name=' + PRIVATE,
    'OTEL_EXPORTER_OTLP_TRACES_COMPRESSION': 'gzip',
    'OTEL_PYTHON_EXPORTER_OTLP_HTTP_TRACES_CREDENTIAL_PROVIDER': PRIVATE,
    'OTEL_SERVICE_NAME': PRIVATE,
    'OTEL_PYTHON_SDK_INTERNAL_METRICS_ENABLED': 'true',
    'LANGSMITH_TRACING': 'true', 'LANGCHAIN_TRACING_V2': 'true',
    'LANGSMITH_ENDPOINT': 'https://remote.invalid/' + PRIVATE,
    'LANGSMITH_API_KEY': PRIVATE,
    'HTTP_PROXY': 'http://proxy.invalid:1234', 'HTTPS_PROXY': 'http://proxy.invalid:1234',
    'ALL_PROXY': 'http://proxy.invalid:1234', 'NO_PROXY': '',
}
SETTINGS = {'enabled': True, 'endpoint': ENDPOINT}
EXECUTOR = {'provider': 'fixture', 'model': 'fixture-model', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'review-model', 'effort': 'medium'}}


class Wire:
    def __init__(self, code=200, error=None):
        self.requests = []
        self.send_options = []
        self.unexpected = []
        self.code, self.error = code, error
        self._original_send = requests.Session.send

    def session_send(self, session, request, **kwargs):
        self.send_options.append((session.trust_env, session.auth, kwargs.copy()))
        return self._original_send(session, request, **kwargs)

    def adapter_send(self, adapter, request, **kwargs):
        self.requests.append((request, kwargs))
        if self.error:
            raise self.error
        response = requests.Response()
        response.status_code = self.code
        response.reason = PRIVATE
        response._content = PRIVATE.encode()
        response.url = request.url
        if self.code == 302:
            response.headers['Location'] = 'https://remote.invalid/' + PRIVATE
        response.headers['Set-Cookie'] = 'private=' + PRIVATE
        return response

    @contextlib.contextmanager
    def intercept(self):
        def unexpected(_client, request, **_kwargs):
            self.unexpected.append(str(request.url))
            raise AssertionError('unexpected hosted monitoring request')
        async def unexpected_async(_client, request, **_kwargs):
            return unexpected(_client, request, **_kwargs)
        with patch.object(requests.Session, 'send', lambda session, request, **kw: self.session_send(session, request, **kw)), \
             patch.object(requests.adapters.HTTPAdapter, 'send', lambda adapter, request, **kw: self.adapter_send(adapter, request, **kw)), \
             patch.object(langsmith_httpx.Client, 'send', unexpected), \
             patch.object(langsmith_httpx.AsyncClient, 'send', unexpected_async):
            yield self
        if self.unexpected:
            raise AssertionError('unexpected hosted monitoring request')

    def decoded(self):
        messages = []
        for req, _ in self.requests:
            message = ExportTraceServiceRequest()
            message.ParseFromString(req.body)
            messages.append(message)
        return messages

    def spans(self):
        return [span for msg in self.decoded() for resource in msg.resource_spans
                for scope in resource.scope_spans for span in scope.spans]

    def assert_safe(self, case, authorization=AUTH):
        case.assertTrue(self.requests)
        for (req, kwargs), (trust_env, auth, options) in zip(self.requests, self.send_options):
            case.assertEqual(req.url, ENDPOINT)
            case.assertEqual(req.method, 'POST')
            case.assertFalse(trust_env)
            case.assertIsNone(auth)
            case.assertFalse(options['allow_redirects'])
            case.assertFalse(kwargs.get('proxies'))
            headers = {k.lower(): v for k, v in req.headers.items()}
            case.assertEqual(headers.get('content-type'), 'application/x-protobuf')
            case.assertEqual(headers.get('authorization'), authorization)
            case.assertLessEqual(set(headers), {'content-type', 'content-length', 'authorization'})
            case.assertNotIn(PRIVATE, str(headers))
            case.assertNotIn(PRIVATE.encode(), req.body)
        for message in self.decoded():
            case.assertNotIn(PRIVATE, str(MessageToDict(message)))
            for resource in message.resource_spans:
                case.assertEqual({a.key: a.value.string_value for a in resource.resource.attributes},
                                 {'service.name': 'coherence-workflow'})
                for scope in resource.scope_spans:
                    for span in scope.spans:
                        case.assertEqual(len(span.events), 0)
                        case.assertEqual(span.status.message, '')
                        case.assertLessEqual({a.key for a in span.attributes}, {
                            'openinference.span.kind', 'coherence.run_id', 'coherence.task_id',
                            'coherence.invocation_id', 'coherence.phase', 'coherence.role',
                            'coherence.model', 'coherence.outcome', 'coherence.tokens.input',
                            'coherence.tokens.output', 'coherence.tokens.cache_read',
                            'coherence.tokens.cache_write', 'coherence.total_tokens', 'coherence.estimated_usd'})


def attributes(span):
    return {a.key: (a.value.string_value if a.value.WhichOneof('value') == 'string_value'
                    else a.value.int_value if a.value.WhichOneof('value') == 'int_value'
                    else a.value.double_value) for a in span.attributes}


class TracingTests(ProjectTest):
    def setUp(self):
        super().setUp()
        credential = self.root / ('private-' + PRIVATE)
        credential.write_text(AUTH)
        environment = patch.dict(os.environ, {'COHERENCE_PHOENIX_AUTHORIZATION_FILE': str(credential)})
        environment.start()
        self.addCleanup(environment.stop)

    def test_final_wire_hierarchy_isolated_from_ambient_and_error(self):
        wire = Wire()
        ambient = SpanContext(123, 456, False, TraceFlags(1), TraceState())
        ctx = trace.set_span_in_context(NonRecordingSpan(ambient))
        ctx = baggage.set_baggage('private', PRIVATE, context=ctx)
        token = context.attach(ctx)
        try:
            with patch.dict(os.environ, ENV), wire.intercept():
                tracer = LocalTracing(SETTINGS, AUTH)
                with tracer.boundary('worker', task_id='caller-' + PRIVATE, invocation=True,
                                     role='worker', model='fixture-model'):
                    before = {'session_id': PRIVATE, 'branch': PRIVATE, 'epoch': PRIVATE,
                              'counters': {'input': 100, 'output': 30, 'cacheRead': 5, 'cacheWrite': 0},
                              'costs': {'estimated_usd': 1.0}}
                    after = {**before, 'counters': {'input': 105, 'output': 32, 'cacheRead': 5, 'cacheWrite': 0},
                             'costs': {'estimated_usd': 1.25}}
                    record_interval(interval_record(before, after), 'worker', 'settled')
                # Finished invocation/task have already reached the final transport while root remains open.
                spans_before_close = wire.spans()
                self.assertEqual([s.name for s in spans_before_close], ['workflow.invocation', 'workflow.task'])
                with self.assertRaisesRegex(ValueError, PRIVATE):
                    with tracer.boundary('worker', task_id='caller-' + PRIVATE, invocation=True):
                        record_interval(interval_record(before, None), 'worker', 'failed')
                        raise ValueError(PRIVATE + ' prompt response tool path')
                tracer.close()
        finally:
            context.detach(token)
        wire.assert_safe(self)
        spans = wire.spans()
        root = next(s for s in spans if s.name == 'workflow.run')
        self.assertFalse(root.parent_span_id)
        self.assertNotEqual(root.trace_id, (123).to_bytes(16, 'big'))
        task = next(s for s in spans if s.name == 'workflow.task')
        call = next(s for s in spans if s.name == 'workflow.invocation')
        self.assertEqual(task.parent_span_id, root.span_id)
        self.assertEqual(call.parent_span_id, task.span_id)
        self.assertEqual(call.trace_id, root.trace_id)
        self.assertEqual(attributes(call)['coherence.tokens.input'], 5)
        self.assertEqual(attributes(call)['coherence.estimated_usd'], .25)
        failed = [s for s in spans if s.name == 'workflow.invocation'][1]
        self.assertNotIn('coherence.tokens.input', attributes(failed))
        self.assertEqual(attributes(failed)['coherence.outcome'], 'failed')

    def test_no_explicit_authorization_or_response_cookie_is_reused(self):
        wire = Wire()
        with patch.dict(os.environ, ENV), wire.intercept():
            tracer = LocalTracing(SETTINGS)
            with tracer.boundary('worker', task_id=PRIVATE, invocation=True): pass
            tracer.close()
        wire.assert_safe(self, authorization=None)
        self.assertGreater(len(wire.requests), 1)

    def test_disabled_nonlocal_and_redirect_do_not_send_elsewhere(self):
        wire = Wire(code=302)
        stderr = io.StringIO()
        with patch.dict(os.environ, ENV), wire.intercept(), contextlib.redirect_stderr(stderr):
            disabled = LocalTracing(None, AUTH)
            with disabled.boundary('worker', task_id=PRIVATE, invocation=True): pass
            disabled.close()
            invalid = LocalTracing({'enabled': True, 'endpoint': 'https://remote.invalid/' + PRIVATE}, AUTH)
            invalid.close()
            self.assertEqual(wire.requests, [])
            tracer = LocalTracing(SETTINGS, AUTH)
            with tracer.boundary('worker', task_id=PRIVATE, invocation=True): pass
            tracer.close()
        wire.assert_safe(self)
        self.assertEqual(len(wire.requests), 3)
        self.assertNotIn(PRIVATE, stderr.getvalue())
        self.assertIn('export unavailable', stderr.getvalue())

    def test_real_graph_checks_git_and_hosted_suppression_with_unavailable_export(self):
        wire = Wire(error=requests.ConnectionError(PRIVATE))
        project = self.project
        class Adapter:
            def __init__(self, *_args, **_kwargs):
                self.last_interval = self.last_observation = self.opened_session = self.saved_session = None
            def prompt(self, prompt, **kwargs):
                from langsmith import utils
                assert not utils.tracing_is_enabled()
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["examined"],"coverage_gaps":[],"findings":[]}'
                assert PRIVATE in prompt
                kwargs['claim']('owned.txt')
                project.joinpath('owned.txt').write_text('actual edit\n')
                return PRIVATE + ' response tool payload'
        contract = admit({'local_monitoring': SETTINGS, 'tasks': [{'id': PRIVATE,
                           'description': PRIVATE + ' prompt tool path', 'owned_paths': ['owned.txt'],
                           'checks': [['python3', '-c', "from pathlib import Path; assert Path('owned.txt').read_text() == 'actual edit\\n'"]]}]})
        stderr = io.StringIO()
        with patch.dict(os.environ, ENV), wire.intercept(), contextlib.redirect_stderr(stderr):
            with Authority(project) as owner:
                result = Engine(owner, 'private-' + PRIVATE, contract, EXECUTOR, adapter=Adapter).invoke()
        self.assertEqual(result['status'], 'complete')
        self.assertNotEqual(git(project, 'rev-parse', 'HEAD').decode().strip(), self.base)
        self.assertEqual(project.joinpath('owned.txt').read_text(), 'actual edit\n')
        self.assertNotIn(PRIVATE, stderr.getvalue())
        self.assertIn('export unavailable', stderr.getvalue())
        wire.assert_safe(self)
        self.assertTrue(any(s.name == 'workflow.invocation' for s in wire.spans()))

    def test_graph_private_worker_exception_is_not_exported(self):
        wire, project = Wire(), self.project
        class Adapter:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, **_kwargs):
                raise ValueError(PRIVATE + ' response tool error path')
        contract = admit({'local_monitoring': SETTINGS,
                          'tasks': [{'id': PRIVATE, 'description': PRIVATE}]})
        stderr = io.StringIO()
        with patch.dict(os.environ, ENV), wire.intercept(), contextlib.redirect_stderr(stderr):
            with Authority(project) as owner:
                with self.assertRaisesRegex(ValueError, PRIVATE):
                    Engine(owner, PRIVATE, contract, EXECUTOR, adapter=Adapter).invoke()
        self.assertNotIn(PRIVATE, stderr.getvalue())
        wire.assert_safe(self)
        failed = [s for s in wire.spans() if s.name == 'workflow.invocation']
        self.assertTrue(failed)
        self.assertEqual(attributes(failed[0])['coherence.outcome'], 'failed')

    def test_graph_reused_session_usage_and_incremental_final_wire(self):
        wire, project, calls = Wire(), self.project, []
        case = self
        headroom = {'context_window': 250001, 'effective_reserve': 50000, 'occupancy': 50000,
                    'compaction_enabled': True, 'compaction_applicable': True}
        class Adapter:
            def __init__(self, *_args, **_kwargs):
                self.saved_session = self.opened_session = self.last_observation = self.last_interval = None
            def prompt(self, prompt, *, claim=None, read_only=False, saved_session=None, **_kwargs):
                from langsmith import utils
                case.assertFalse(utils.tracing_is_enabled())
                if read_only:
                    return '{"approved":true,"coverage":["examined"],"coverage_gaps":[],"findings":[]}'
                calls.append(saved_session)
                if len(calls) == 2:
                    case.assertEqual(saved_session['id'], 'session-' + PRIVATE)
                    observed = wire.spans()
                    case.assertTrue(any(s.name == 'workflow.invocation' for s in observed))
                    case.assertFalse(any(s.name == 'workflow.run' for s in observed))
                n = len(calls)
                path = 'first.txt' if n == 1 else 'second.txt'
                claim(path)
                project.joinpath(path).write_text(str(n))
                self.saved_session = self.opened_session = {'id': 'session-' + PRIVATE, 'file': '/private/' + PRIVATE}
                def observation(counter):
                    return {'session_id': 'session-' + PRIVATE, 'branch': 'branch-' + PRIVATE,
                            'epoch': 'epoch-' + PRIVATE, 'headroom': headroom,
                            'counters': {'input': counter, 'output': 0, 'cacheRead': 0, 'cacheWrite': 0},
                            'costs': {'estimated_usd': 1.0}}
                self.last_observation = {'before': observation(100 if n == 1 else 105),
                                         'after': observation(105 if n == 1 else 112)}
                return 'response-' + PRIVATE
        tasks = [{'id': 'one-' + PRIVATE, 'description': PRIVATE, 'context_group': 'shared', 'owned_paths': ['first.txt']},
                 {'id': 'two-' + PRIVATE, 'description': PRIVATE, 'context_group': 'shared',
                  'depends': ['one-' + PRIVATE], 'owned_paths': ['second.txt']}]
        with patch.dict(os.environ, ENV), wire.intercept():
            with Authority(project) as owner:
                result = Engine(owner, 'run-' + PRIVATE, admit({'tasks': tasks, 'local_monitoring': SETTINGS}),
                                EXECUTOR, adapter=Adapter).invoke()
        self.assertEqual(result['status'], 'complete')
        self.assertIsNone(calls[0])
        self.assertEqual(len(calls), 2)
        wire.assert_safe(self)
        workers = [attributes(s) for s in wire.spans() if s.name == 'workflow.invocation'
                   and attributes(s).get('coherence.role') == 'worker']
        self.assertEqual([item['coherence.tokens.input'] for item in workers], [5, 7])

    def test_parallel_workers_keep_context_and_wire_private(self):
        wire, project, barrier = Wire(), self.project, threading.Barrier(2)
        class Adapter:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, prompt, *, read_only=False, **kwargs):
                from langsmith import utils
                assert not utils.tracing_is_enabled()
                if read_only:
                    return '{"approved":true,"coverage":["examined"],"coverage_gaps":[],"findings":[]}'
                name = 'a.txt' if 'a.txt' in prompt else 'b.txt'
                kwargs['claim'](name)
                barrier.wait(timeout=10)
                project.joinpath(name).write_text(name)
                return PRIVATE
        tasks = [{'id': 'A', 'description': PRIVATE, 'owned_paths': ['a.txt']},
                 {'id': 'B', 'description': PRIVATE, 'owned_paths': ['b.txt']}]
        with patch.dict(os.environ, ENV), wire.intercept():
            with Authority(project) as owner:
                result = Engine(owner, 'parallel-private', admit({'local_monitoring': SETTINGS, 'tasks': tasks}),
                                EXECUTOR, adapter=Adapter, parallel=True).invoke()
        self.assertEqual(result['status'], 'complete')
        wire.assert_safe(self)
        workers = [s for s in wire.spans() if s.name == 'workflow.invocation'
                   and attributes(s).get('coherence.role') == 'worker']
        self.assertEqual(len(workers), 2)
        self.assertEqual(len({s.span_id for s in workers}), 2)

    def test_disabled_graph_suppresses_hosted_tracing(self):
        wire, project = Wire(), self.project
        class Adapter:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, *, read_only=False, **kwargs):
                from langsmith import utils
                assert not utils.tracing_is_enabled()
                if read_only:
                    return '{"approved":true,"coverage":["examined"],"coverage_gaps":[],"findings":[]}'
                kwargs['claim']('owned.txt')
                project.joinpath('owned.txt').write_text('disabled')
                return PRIVATE
        tasks = admit([{'id': PRIVATE, 'description': PRIVATE, 'owned_paths': ['owned.txt']}])
        with patch.dict(os.environ, ENV), wire.intercept():
            with Authority(project) as owner:
                result = Engine(owner, 'disabled', tasks, EXECUTOR, adapter=Adapter).invoke()
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(wire.requests, [])

    def test_initialization_and_serialization_gaps_are_safe(self):
        wire = Wire()
        stderr = io.StringIO()
        with patch.dict(os.environ, ENV), wire.intercept(), contextlib.redirect_stderr(stderr):
            with patch('coherence_workflow.tracing.TracerProvider', side_effect=ValueError(PRIVATE)):
                tracer = LocalTracing(SETTINGS, AUTH)
                with tracer.boundary('checks'): pass
                tracer.close()
            with patch('coherence_workflow.tracing.encode_spans', side_effect=ValueError(PRIVATE)):
                tracer = LocalTracing(SETTINGS, AUTH)
                with tracer.boundary('checks'): pass
                tracer.close()
        self.assertEqual(wire.requests, [])
        self.assertIn('initialization unavailable', stderr.getvalue())
        self.assertIn('serialization unavailable', stderr.getvalue())
        self.assertNotIn(PRIVATE, stderr.getvalue())

    def test_initialization_and_serialization_failures_allow_real_checks_and_git(self):
        project, wire = self.project, Wire()
        for number, target in enumerate(('coherence_workflow.tracing.TracerProvider',
                                         'coherence_workflow.tracing.encode_spans',
                                         'coherence_workflow.tracing.configured_tracing')):
            class Adapter:
                def __init__(self, *_args, **_kwargs): pass
                def prompt(self, _prompt, *, read_only=False, **kwargs):
                    if read_only:
                        return '{"approved":true,"coverage":["examined"],"coverage_gaps":[],"findings":[]}'
                    kwargs['claim']('owned.txt')
                    project.joinpath('owned.txt').write_text(str(number))
                    return 'done'
            contract = admit({'local_monitoring': SETTINGS, 'tasks': [{'id': 'task', 'description': 'edit',
                'owned_paths': ['owned.txt'], 'checks': [['python3', '-c',
                    "from pathlib import Path; assert Path('owned.txt').read_text() == '" + str(number) + "'"]]}]})
            before = git(project, 'rev-parse', 'HEAD')
            stderr = io.StringIO()
            with patch.dict(os.environ, ENV), wire.intercept(), contextlib.redirect_stderr(stderr), \
                 patch(target, side_effect=ValueError(PRIVATE)):
                with Authority(project) as owner:
                    result = Engine(owner, 'gap-' + str(number), contract, EXECUTOR, adapter=Adapter).invoke()
            self.assertEqual(result['status'], 'complete')
            self.assertNotEqual(git(project, 'rev-parse', 'HEAD'), before)
            self.assertNotIn(PRIVATE, stderr.getvalue())
            self.assertIn('serialization unavailable' if number == 1 else 'initialization unavailable', stderr.getvalue())
        self.assertEqual(wire.requests, [])

    def test_configuration_and_operating_guide(self):
        root = Path(__file__).resolve().parents[2]
        env = (root / 'runtime/phoenix.env.example').read_text()
        doc = (root / 'docs/coordinate-implementation.md').read_text()
        for line in ('PHOENIX_WORKING_DIR=/data', 'PHOENIX_TELEMETRY_ENABLED=false',
                     'PHOENIX_ALLOW_EXTERNAL_RESOURCES=false'):
            self.assertIn(line, env)
        for phrase in ('sha256:1f9a144a5357b4973e93a15718f050247cb7a4ee7b7c6c06ecb91b5eed3fbaad',
                       '127.0.0.1:6006:6006', 'authentication', 'SQLite', 'PROJECT_KEY', 'credentials'):
            self.assertIn(phrase, doc)
        self.assertNotIn(AUTH, env + doc)


if __name__ == '__main__':
    unittest.main()
