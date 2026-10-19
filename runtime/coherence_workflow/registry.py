"""Trusted versioned capabilities. Workflow data can reference, never create, executable code."""
from dataclasses import dataclass, field
from importlib.resources import files
import json
import hashlib
import inspect
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry as SchemaRegistry, Resource

from .store import Blocked, digest


HANDLER_INPUT_SCHEMA = {'type':'object','additionalProperties':False,
                        'properties':{'node':{'type':'object'},'run_id':{'type':'string'},
                                      'operation_id':{'type':'string'}},
                        'required':['node','run_id','operation_id']}


RESULT_SCHEMA = {'type':'object','additionalProperties':False,
                 'properties':{'outcome':{'type':'string'}, 'value':{'type':'string','maxLength':1024}},
                 'required':['outcome']}


def schemas():
    root = files('coherence_workflow').joinpath('schemas')
    return {p.name: json.loads(p.read_text()) for p in root.iterdir() if p.name.endswith('.schema.json')}


def validate_schema(name, value):
    resources = schemas()
    registry = SchemaRegistry().with_resources((s['$id'],Resource.from_contents(s)) for s in resources.values())
    Draft202012Validator(resources[name], registry=registry).validate(value)


@dataclass(frozen=True)
class Handler:
    id: str
    version: str
    kind: str
    stage: str
    outcomes: tuple
    function: object = None
    side_effects: tuple = ()
    result_schema: dict = field(default_factory=lambda: RESULT_SCHEMA)
    input_schema: dict = field(default_factory=lambda: HANDLER_INPUT_SCHEMA)
    required_capabilities: tuple = ()
    reconcile: object = None


class Registry:
    version = '1'

    def __init__(self):
        self.handlers = {}
        self.profiles = {}
        self.skills = {}
        self.capabilities = set()
        self.permissions = set()
        self.tools = set()
        self.containments = set()
        self.success_terminals = set()
        # Declared future boundaries fail closed, not fake successful implementations.
        for id, kind, stage in (
            ('intake','code','intake'), ('authority','gate','authority'),
            ('custody','code','custody'), ('implement','agent','work'),
            ('verify','code','verification'), ('checkpoint','code','checkpoint'),
            ('review','agent','review'), ('accept','terminal','success')):
            self.handlers[id] = Handler(id,'1',kind,stage,() if kind=='terminal' else ('ok',),
                                        required_capabilities=('runtime.'+id,))
        self.success_terminals.add('accept')

    def handler(self, node):
        handler = self.handlers.get(node['handler'])
        if not handler or handler.version != node['handler_version'] or handler.kind != node['type']:
            raise Blocked('unknown handler/version/type')
        if tuple(node['outcomes']) != handler.outcomes or set(node['transitions']) != set(handler.outcomes):
            raise Blocked('handler outcomes/edges mismatch')
        if set(node['side_effects']) != set(handler.side_effects):
            raise Blocked('handler side effects mismatch')
        if handler.side_effects and handler.reconcile is None:
            raise Blocked('effect handler requires registered applicability reconciliation')
        if handler.function is None or not set(handler.required_capabilities) <= self.capabilities:
            raise Blocked('capability unavailable: '+handler.id)
        return handler

    def identity(self):
        def code_hash(function):
            if function is None:
                return None
            try:
                return {'module_hash':hashlib.sha256(Path(inspect.getfile(function)).read_bytes()).hexdigest(),
                        'callable':function.__qualname__,
                        'source_hash':hashlib.sha256(inspect.getsource(function).encode()).hexdigest()}
            except (TypeError,OSError) as exc:
                raise Blocked('handler source identity unavailable') from exc
        return digest({'version':self.version,
                       'handlers':{k:{'version':h.version,'kind':h.kind,'stage':h.stage,
                                      'outcomes':h.outcomes,'side_effects':h.side_effects,
                                      'input':h.input_schema,'result':h.result_schema,
                                      'capabilities':h.required_capabilities,'code_hash':code_hash(h.function),
                                      'reconcile_hash':code_hash(h.reconcile)}
                                   for k,h in self.handlers.items()},
                       'profiles':self.profiles,'skills':self.skills,
                       'capabilities':sorted(self.capabilities), 'permissions':sorted(self.permissions),
                       'tools':sorted(self.tools),'containments':sorted(self.containments),
                       'success_terminals':sorted(self.success_terminals)})


# Stable T001 selectors and closed argument contracts; no shell selector interpolation.
CHECKS = {
    'workflow.'+selector: {
        'version':'1', 'schema':{'type':'object','additionalProperties':False,
            'properties':{'test_file':{'const':'runtime/tests/'+file},'selector':{'const':selector}},
            'required':['test_file','selector']}}
    for file, selector in [('test_engine.py','ConfigGraphTests'),('test_custody.py','CustodyTests'),
                           ('test_custody.py','LaunchCrashTests'),('test_engine.py','LedgerCheckpointTests'),
                           ('test_intake.py','OriginIntakeTests'),('test_authority.py','AuthorityAdmissionTests'),
                           ('test_verification.py','RequiredEvidenceTests'),('test_git_effects.py','FocusedCheckpointTests')]
}
