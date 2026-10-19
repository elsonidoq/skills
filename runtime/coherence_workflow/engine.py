"""Validated YAML -> actual LangGraph; application receipts precede sync checkpoints."""
from importlib.resources import files
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import TypedDict

from jsonschema import Draft202012Validator
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
import yaml

from .registry import schemas, validate_schema
from .store import Blocked, canonical, digest, safe_path


class StrictLoader(yaml.SafeLoader):
    def compose_node(self, parent, index):
        event = self.peek_event()
        if isinstance(event, yaml.AliasEvent) or getattr(event, 'anchor', None) is not None or getattr(event,'tag',None) is not None:
            raise Blocked('YAML tags/anchors/aliases forbidden')
        return super().compose_node(parent,index)

    def construct_mapping(self, node, deep=False):
        result = {}
        for key, value in node.value:
            k = self.construct_object(key,deep=deep)
            if not isinstance(k,str) or k in result:
                raise Blocked('duplicate/non-string YAML mapping key')
            result[k] = self.construct_object(value,deep=deep)
        return result


def load_workflow(registry, source=None, resource_root=None):
    """Validate every reference before opening a store or performing tool effects."""
    raw = files('coherence_workflow').joinpath('workflows/coordinate.yaml').read_bytes() if source is None else source
    if isinstance(raw,str):
        raw = raw.encode()
    if not isinstance(raw,bytes) or len(raw) > 262144:
        raise Blocked('workflow byte limit')
    try:
        config = yaml.load(raw,Loader=StrictLoader)
        validate_schema('workflow.schema.json',config)
        # Bound nesting/collections after parser size bound; no aliases can expand input.
        if len(config['nodes']) > 128:
            raise Blocked('workflow node limit')
        canonical(config)
    except (yaml.YAMLError, ValueError, RecursionError) as exc:
        raise Blocked('invalid bounded YAML') from exc
    if config['registry_version'] != registry.version:
        raise Blocked('unknown registry version')
    if not set(config['permissions']) <= registry.permissions or not set(config['tool_capabilities']) <= registry.tools:
        raise Blocked('unregistered permission/tool')
    if config['containment_capability'] is not None and config['containment_capability'] not in registry.containments:
        raise Blocked('unavailable containment capability')
    if config['interaction']['mode'] != 'standalone':
        raise Blocked('interactive capability unavailable until interaction delivery')
    if config['storage'] != {'checkpoint':'.coherence/workflow/workflow.sqlite','event_root':'.coherence/workflow/runs'}:
        raise Blocked('storage cannot override worktree authority')
    for profile_id, value in config['profiles'].items():
        if registry.profiles.get(profile_id) != value:
            raise Blocked('unknown/unavailable exact profile: '+profile_id)
    root = Path(resource_root).resolve(strict=True) if resource_root is not None else None
    for skill_id, value in config['skills'].items():
        if registry.skills.get(skill_id) != value:
            raise Blocked('unknown/unavailable skill: '+skill_id)
        if root is None:
            raise Blocked('approved resource root required')
        p = safe_path(root,value['path'])
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != value['sha256']:
            raise Blocked('skill content drift')
    if root is None:
        raise Blocked('approved resource root required')
    manifest = safe_path(root,config['settings_manifest']['path'])
    if not manifest.is_file() or hashlib.sha256(manifest.read_bytes()).hexdigest() != config['settings_manifest']['sha256']:
        raise Blocked('settings manifest drift')
    nodes = {n['id']:n for n in config['nodes']}
    if len(nodes) != len(config['nodes']) or config['start'] not in nodes:
        raise Blocked('duplicate node or unknown start')
    handlers = {id:registry.handler(node) for id,node in nodes.items()}
    for id,node in nodes.items():
        if not set(node['transitions'].values()) <= nodes.keys():
            raise Blocked('unknown transition target')
        if node['type']=='agent':
            if node['profile'] not in config['profiles'] or node['skill'] not in config['skills']:
                raise Blocked('unknown node profile/skill')
            if not set(node['tools']) <= set(config['tool_capabilities']) or not set(node['permissions']) <= set(config['permissions']):
                raise Blocked('node permission/tool escalation')
            if node['role']=='review' and (set(node['side_effects']) - {'read'} or node['session_policy']['reuse_preference'] not in ('own_reviewer','role_default')):
                raise Blocked('review must be independent read-only')
        if handlers[id].stage == 'repair' and (node['type'] != 'agent' or node.get('role') != 'repair'):
            raise Blocked('repair cycle requires configured repair role')
        # Graph transport retries never authorize replay of an uncertain external effect.
        if node.get('max_retries',0):
            raise Blocked('retry capability unavailable; no blind external replay')
    selectors = [id for id, handler in handlers.items() if handler.stage == 'task_select']
    if len(selectors) > 1:
        raise Blocked('one bounded task-progress selector required')
    progress = selectors[0] if selectors else None
    required = ('intake','authority','custody','verification','checkpoint','review')
    reached = set()
    validated = set()

    def walk(id, stack, stages):
        if id in stack:
            previous = handlers[stack[-1]].stage
            if (id == progress and ((stages == required[:5] and previous == 'checkpoint') or
                                    (stages == required[:3] and previous == 'correction_authority'))):
                return
            if (stages == required[:4] and ((handlers[id].stage == 'verification' and previous == 'repair') or
                                           (handlers[id].stage == 'repair' and previous == 'verification'))):
                return
            raise Blocked('unbounded/unsupported graph cycle')
        key = (id,stages)
        if key in validated:
            return
        reached.add(id)
        handler = handlers[id]
        stage = handler.stage
        if progress and id == progress and stages == required[:3]:
            # The done edge can reach final review without manufacturing an empty
            # task/checkpoint; the work edge is checked separately below.
            for outcome, target in nodes[id]['transitions'].items():
                walk(target, stack+(id,), required[:5] if outcome == 'done' else stages)
            validated.add(key)
            return
        if stage == 'correction_authority':
            if stages != required:
                raise Blocked('correction authority must follow full-range review')
            stages = required[:3]
        if stage in required:
            index = required.index(stage)
            if index != len(stages):
                raise Blocked('safety stage ordering/bypass')
            stages = stages+(stage,)
        if nodes[id]['type']=='terminal':
            if handler.id in registry.success_terminals and stages != required:
                raise Blocked('successful terminal bypasses mandatory safety nodes')
            validated.add(key)
            return
        for target in set(nodes[id]['transitions'].values()):
            walk(target,stack+(id,),stages)
        validated.add(key)
    walk(config['start'],(),())
    if reached != nodes.keys():
        raise Blocked('unreachable node')
    if progress:
        node = nodes[progress]
        if (handlers[progress].outcomes != ('work','done') or
                not any(handlers[n].stage == 'checkpoint' and progress in nodes[n]['transitions'].values() for n in nodes)):
            raise Blocked('invalid task-progress cycle')
    return config


class GraphState(TypedDict):
    trace: list
    outcome: str


class Engine:
    def __init__(self, authority, run_id, config, registry, resource_root, phase_hook=None, *, max_task_visits=None, input_identity=None):
        self.authority, self.store = authority, authority.store
        config = load_workflow(registry, yaml.safe_dump(config), resource_root)
        self.run_id, self.config, self.registry = run_id, config, registry
        self.registry_hash, self.config_hash = registry.identity(), digest(config)
        self.resource_root = resource_root
        self.schemas_hash = digest(schemas())
        self.code_hash = self._runtime_code_hash()
        self.input_identity = input_identity
        self.input_hash = digest(input_identity)
        # Revalidate even programmatic configs; callers cannot bypass the YAML seam.
        self.hash = digest({'config':config,'registry':registry.identity(),'schemas':schemas(),
                            'engine':'0.1.0','langgraph':'1.2.16','saver':'3.1.2',
                            'inputs':input_identity, 'task_visit_bound':max_task_visits,
                            'code':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in files('coherence_workflow').iterdir() if p.name.endswith('.py')}})
        self.progress = any(registry.handler(n).stage == 'task_select' for n in config['nodes'])
        if self.progress and (type(max_task_visits) is not int or max_task_visits < 0):
            raise Blocked('bounded approved task count required')
        self.max_task_visits = max_task_visits
        self.hook = phase_hook or (lambda phase, op: None)
        self.store.reserve(run_id,self.hash)
        self.saver_db = sqlite3.connect(authority.database,check_same_thread=False,timeout=5)
        self.saver_db.execute('PRAGMA journal_mode=WAL')
        self.saver_db.execute('PRAGMA synchronous=FULL')
        self.saver_db.execute('PRAGMA foreign_keys=ON')
        self.saver = SqliteSaver(self.saver_db)
        graph = StateGraph(GraphState)
        for node in config['nodes']:
            registry.handler(node)
            graph.add_node(node['id'], self._node(node))
        graph.add_edge(START,config['start'])
        for node in config['nodes']:
            if node['type']=='terminal':
                graph.add_edge(node['id'],END)
            else:
                graph.add_conditional_edges(node['id'],lambda state: state['outcome'],node['transitions'])
        self.graph = graph.compile(checkpointer=self.saver)
        self.thread = {'configurable':{'thread_id':run_id},'recursion_limit':256 if not self.progress else 16+8*max_task_visits}

    def _node(self, node):
        handler = self.registry.handler(node)
        def execute(state):
            self.authority.assert_held()
            self._assert_pins()
            self.store.assert_dispatchable(self.run_id)
            trace_before = state.get('trace',[])
            visit = sum(item['node'] == node['id'] for item in trace_before)
            if self.progress and visit > self.max_task_visits:
                raise Blocked('task-progress visit bound exhausted')
            logical = node['id'] + ':' + str(visit) if self.progress else node['id']
            args = {'config_hash':self.hash,'node':node,'trace':trace_before}
            details = {'handler':handler.id,'version':handler.version,'input_hash':digest(args)}
            old = self.store.db.execute('SELECT * FROM wf_operations WHERE run_id=? AND node_id=? AND kind=?',
                                         (self.run_id,logical,'graph')).fetchone()
            op = self.store.intent(self.run_id,logical,'graph',args,details)
            if old:
                if op['phase'] != 'completed' or op['result'] is None:
                    raise Blocked('uncertain graph effect; explicit reconciliation required')
                result = json.loads(op['result'])
                proof = {row['kind']:row for row in self.store.db.execute(
                    "SELECT kind,payload,seq FROM wf_events WHERE op_id=? AND kind IN ('intent','completed')",(op['op_id'],))}
                if ('intent' not in proof or 'completed' not in proof or
                    json.loads(proof['intent']['payload']) != details or
                    json.loads(proof['completed']['payload']) != result or
                    proof['intent']['seq'] >= proof['completed']['seq']):
                    raise Blocked('replayed result lacks ordered application proof')
                if handler.side_effects and not handler.reconcile({'node':node,'operation_id':op['op_id']},result):
                    raise Blocked('recorded effect result no longer applicable; no replay')
            else:
                context = {'node':node,'run_id':self.run_id,'operation_id':op['op_id']}
                Draft202012Validator(handler.input_schema).validate(context)
                if self.store.db.in_transaction:
                    raise Blocked('application transaction spans external wait')
                result = handler.function(context)
                Draft202012Validator(handler.result_schema).validate(result)
                if node['type']!='terminal' and result['outcome'] not in handler.outcomes:
                    raise Blocked('illegal handler result outcome')
                self.store.transition(op['op_id'],'intent','completed',result)
                self.hook('application_result',op['op_id'])
            Draft202012Validator(handler.result_schema).validate(result)
            if node['type']!='terminal' and result['outcome'] not in handler.outcomes:
                raise Blocked('illegal recorded handler outcome')
            trace = state.get('trace',[])+[{'node':node['id'],'handler':handler.id,
                     'profile':node.get('profile'), 'skill':node.get('skill'), 'config_hash':self.hash,
                     'operation_id':op['op_id']}]
            return {'outcome':result['outcome'],'trace':trace}
        return execute

    @staticmethod
    def _runtime_code_hash():
        return digest({p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in files('coherence_workflow').iterdir() if p.name.endswith('.py')})

    def _assert_pins(self):
        if self._runtime_code_hash() != self.code_hash or digest(schemas()) != self.schemas_hash:
            raise Blocked('active runtime/schema content drift')
        if (self.registry.identity() != self.registry_hash or digest(self.config) != self.config_hash or
                digest(self.input_identity) != self.input_hash):
            raise Blocked('active registry/config drift; renewal required')
        load_workflow(self.registry,yaml.safe_dump(self.config),self.resource_root)

    def invoke(self):
        self.authority.assert_held()
        self._assert_pins()
        if self.store.db.in_transaction:
            raise Blocked('application transaction held across saver')
        state = self.graph.get_state(self.thread)
        if state.values and not state.next:
            self.audit(state.values)
            return state.values
        result = self.graph.invoke(None if state.values else {'trace':[],'outcome':''},self.thread,durability='sync')
        self.audit(result)
        return result

    def audit(self, state):
        self.store.assert_dispatchable(self.run_id)
        nodes = {node['id']:node for node in self.config['nodes']}
        expected = self.config['start']
        prefix = []
        for item in state.get('trace',[]):
            if expected is None or item['node'] != expected or item['config_hash'] != self.hash:
                raise Blocked('graph route/config proof mismatch')
            node = nodes[expected]
            handler = self.registry.handler(node)
            op = self.store.operation(item['operation_id'])
            args = {'config_hash':self.hash,'node':node,'trace':prefix}
            visit = sum(entry['node'] == item['node'] for entry in prefix)
            logical = item['node'] + ':' + str(visit) if self.progress else item['node']
            if (op['run_id'] != self.run_id or op['node_id'] != logical or
                op['phase']!='completed' or not op['result'] or op['args_hash'] != digest(args)):
                raise Blocked('graph success without applicable application proof')
            result = json.loads(op['result'])
            Draft202012Validator(handler.result_schema).validate(result)
            event = self.store.db.execute("SELECT payload,seq FROM wf_events WHERE op_id=? AND kind='completed'",(op['op_id'],)).fetchone()
            intent = self.store.db.execute("SELECT payload,seq FROM wf_events WHERE op_id=? AND kind='intent'",(op['op_id'],)).fetchone()
            expected_intent = {'handler':handler.id,'version':handler.version,'input_hash':digest(args)}
            if (not event or json.loads(event[0]) != result or not intent or
                json.loads(intent[0]) != expected_intent or intent[1] >= event[1] or
                op['intent'] != canonical(expected_intent)):
                raise Blocked('application intent/result/event proof missing or conflicting')
            if handler.side_effects and not handler.reconcile({'node':node,'operation_id':op['op_id']},result):
                raise Blocked('effect applicability audit failed')
            if node['type']=='terminal':
                expected = None
            else:
                if result['outcome'] not in node['transitions']:
                    raise Blocked('application outcome proof invalid')
                expected = node['transitions'][result['outcome']]
            prefix = prefix+[item]
        if not prefix or expected is not None:
            raise Blocked('incomplete graph route/application proof')

    def close(self):
        self.saver_db.close()
