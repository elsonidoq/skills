"""Opt-in, local-only, metadata-only OpenTelemetry boundary spans.

This is separate from Pi/provider traffic. No process-wide environment changes or
OpenTelemetry global provider are used. Export is best effort and never changes work.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from langgraph.errors import GraphInterrupt
import math
import os
from pathlib import Path
import re
import sys
import threading
import uuid

from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.exporter.http.transport._requests import RequestsHTTPTransport
from opentelemetry.exporter.otlp.proto.common.trace_encoder import encode_spans
from opentelemetry.metrics import NoOpMeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.sdk.trace.sampling import ALWAYS_ON
import requests

ENDPOINT = 'http://127.0.0.1:6006/v1/traces'
_current_invocation = ContextVar('coherence_trace_invocation', default=None)
_MODEL = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._:/-]*$')
_ROLES = frozenset(('worker', 'corrective_worker', 'fixing_worker', 'reviewer'))
_OUTCOMES = frozenset(('settled', 'failed', 'interrupted', 'passed', 'returned'))


def _gap(category):
    try:
        print('coherence tracing: ' + category, file=sys.stderr, flush=True)
    except Exception:
        pass


class _LocalExporter(SpanExporter):
    """Standard OTLP protobuf encoding and SDK Requests transport, with closed inputs.

    The upstream OTLP exporter merges ambient headers, and logs response/error text.
    Use its standard encoder and transport directly to avoid both behaviors. Requests'
    SDK transport explicitly disables redirects. Never expose response or exception text.
    """
    def __init__(self, authorization):
        session = requests.Session()
        session.trust_env = False
        session.auth = None
        session.headers.clear()
        session.cookies.clear()
        self.transport = RequestsHTTPTransport(session=session, verify=True, cert=None)
        self.session = session
        self.lock = threading.Lock()
        self.headers = {'Content-Type': 'application/x-protobuf'}
        if authorization:
            self.headers['Authorization'] = authorization

    def export(self, spans):
        try:
            payload = encode_spans(spans).SerializePartialToString()
        except Exception:
            _gap('serialization unavailable')
            return SpanExportResult.FAILURE
        try:
            with self.lock:
                self.session.cookies.clear()
                try:
                    result = self.transport.request('POST', ENDPOINT, headers=dict(self.headers),
                                                    timeout=10, data=payload)
                finally:
                    self.session.cookies.clear()
            if result.status_code is None or not 200 <= result.status_code < 300:
                _gap('export unavailable')
                return SpanExportResult.FAILURE
            return SpanExportResult.SUCCESS
        except Exception:
            _gap('export unavailable')
            return SpanExportResult.FAILURE

    def shutdown(self):
        try:
            self.transport.close()
        except Exception:
            _gap('shutdown unavailable')

    def force_flush(self, timeout_millis=30000):
        return True


def _number(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and value >= 0)


def record_interval(interval, role, outcome):
    """Attach only qualified invocation-local values from metrics.interval_record."""
    span = _current_invocation.get()
    if span is None:
        return
    try:
        if role in _ROLES:
            span.set_attribute('coherence.role', role)
        if outcome in _OUTCOMES:
            span.set_attribute('coherence.outcome', outcome)
        if not isinstance(interval, dict):
            return
        tokens = interval.get('tokens') if isinstance(interval.get('tokens'), dict) else {}
        for key in ('input', 'output', 'cache_read', 'cache_write'):
            field = tokens.get(key)
            value = field.get('value') if isinstance(field, dict) else None
            if _number(value):
                span.set_attribute('coherence.tokens.' + key, value)
        for key in ('total_tokens', 'estimated_usd'):
            field = interval.get(key)
            value = field.get('value') if isinstance(field, dict) else None
            if _number(value):
                span.set_attribute('coherence.' + key, value)
    except Exception:
        _gap('span unavailable')


class LocalTracing:
    def __init__(self, settings, authorization=None):
        self.provider = self.tracer = self.root = None
        self.task_ids = {}
        self.lock = threading.Lock()
        if settings is None or settings is False:
            return
        if not isinstance(settings, dict) or settings.get('enabled') is not True:
            if not isinstance(settings, dict) or settings.get('enabled') not in (None, False):
                _gap('configuration invalid; disable monitoring or select the local endpoint')
            return
        if settings.get('endpoint') != ENDPOINT:
            _gap('configuration invalid; select http://127.0.0.1:6006/v1/traces')
            return
        if authorization is not None and (not isinstance(authorization, str) or '\r' in authorization or '\n' in authorization):
            _gap('authorization invalid; supply a private local authorization value')
            return
        try:
            meter = NoOpMeterProvider()
            exporter = _LocalExporter(authorization)
            self.provider = TracerProvider(resource=Resource({'service.name': 'coherence-workflow'}),
                                           sampler=ALWAYS_ON, shutdown_on_exit=False, meter_provider=meter)
            self.provider.add_span_processor(SimpleSpanProcessor(exporter, meter_provider=meter))
            self.tracer = self.provider.get_tracer('coherence.workflow')
            self.root = self.tracer.start_span('workflow.run', context=Context(),
                attributes={'openinference.span.kind': 'CHAIN', 'coherence.run_id': uuid.uuid4().hex},
                record_exception=False, set_status_on_exception=False)
        except Exception:
            _gap('initialization unavailable')
            self.provider = self.tracer = self.root = None

    def _task_identity(self, task_id):
        if not isinstance(task_id, str):
            return None
        with self.lock:
            return self.task_ids.setdefault(task_id, uuid.uuid4().hex)

    @contextmanager
    def boundary(self, name, *, task_id=None, invocation=False, model=None, role=None):
        """A completed task/graph boundary and optional Pi call under the open run."""
        if name not in {'ready', 'worker', 'wait', 'checks', 'checkpoint', 'review', 'repair', 'join'}:
            name = 'ready'
        task = child = token = None
        try:
            if self.tracer is not None and self.root is not None:
                attrs = {'openinference.span.kind': 'CHAIN', 'coherence.phase': name}
                identity = self._task_identity(task_id)
                if identity is not None:
                    attrs['coherence.task_id'] = identity
                task = self.tracer.start_span('workflow.task' if identity else 'workflow.boundary',
                    context=trace.set_span_in_context(self.root, Context()), attributes=attrs,
                    record_exception=False, set_status_on_exception=False)
                if invocation:
                    details = {'openinference.span.kind': 'CHAIN', 'coherence.invocation_id': uuid.uuid4().hex}
                    if role in _ROLES:
                        details['coherence.role'] = role
                    if isinstance(model, str) and _MODEL.fullmatch(model):
                        details['coherence.model'] = model
                    child = self.tracer.start_span('workflow.invocation',
                        context=trace.set_span_in_context(task, Context()), attributes=details,
                        record_exception=False, set_status_on_exception=False)
                    token = _current_invocation.set(child)
        except Exception:
            _gap('span unavailable')
        try:
            yield
        except BaseException as exc:
            outcome = 'interrupted' if isinstance(exc, (GraphInterrupt, KeyboardInterrupt, SystemExit)) else 'failed'
            for span in (child, task):
                if span is not None:
                    try: span.set_attribute('coherence.outcome', outcome)
                    except Exception: _gap('span unavailable')
            raise
        else:
            if task is not None:
                try: task.set_attribute('coherence.outcome', 'returned')
                except Exception: _gap('span unavailable')
        finally:
            if token is not None:
                _current_invocation.reset(token)
            for span in (child, task):
                if span is not None:
                    try: span.end()
                    except Exception: _gap('export unavailable')

    def close(self):
        if self.root is not None:
            try: self.root.end()
            except Exception: _gap('export unavailable')
        if self.provider is not None:
            try: self.provider.shutdown()
            except Exception: _gap('shutdown unavailable')


def configured_tracing(contract):
    settings = contract.get('local_monitoring') if isinstance(contract, dict) else None
    # Only the explicitly named private file supplies auth; never persist its bytes in
    # the task contract or pass the credential itself in the Pi child's environment.
    authorization = None
    if isinstance(settings, dict) and settings.get('enabled') is True:
        path = os.environ.get('COHERENCE_PHOENIX_AUTHORIZATION_FILE')
        if path:
            try:
                authorization = Path(path).read_text(encoding='utf-8').strip()
                if not authorization:
                    raise ValueError('empty authorization')
            except Exception:
                _gap('authorization unavailable; supply a readable private local authorization file')
                return LocalTracing(None)
    return LocalTracing(settings, authorization)
