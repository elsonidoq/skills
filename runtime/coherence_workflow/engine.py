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
from langgraph.types import Command
import yaml

from .registry import schemas, validate_schema
from .store import Blocked, canonical, digest, safe_path, git


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
        transport=registry.question_transports.get(config['interaction']['question_transport'])
        if transport is None:
            raise Blocked('registered actually preflighted interactive capability unavailable')
        transport.validate_config(config['interaction'])
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
    required = ('intake','custody','verification','checkpoint','review')
    reached = set()
    validated = set()

    def walk(id, stack, stages):
        if id in stack:
            previous = handlers[stack[-1]].stage
            if handlers[id].stage == 'owner_input' and previous == 'continue_original':
                if not progress or nodes[stack[-1]].get('role') not in ('implement','repair','review'):
                    raise Blocked('unbounded question continuation')
                return
            if (id == progress and ((stages == required[:4] and previous == 'checkpoint') or
                                    (stages == required[:2] and previous == 'correction'))):
                return
            if (stages == required[:3] and ((handlers[id].stage == 'verification' and (previous == 'repair' or previous == 'continue_original' and nodes[stack[-1]].get('role') == 'repair')) or
                                           (handlers[id].stage == 'repair' and previous == 'verification'))):
                return
            raise Blocked('unbounded/unsupported graph cycle')
        key = (id,stages)
        if key in validated:
            return
        reached.add(id)
        handler = handlers[id]
        stage = handler.stage
        if progress and id == progress and stages == required[:2]:
            # The done edge can reach final review without manufacturing an empty
            # task/checkpoint; the work edge is checked separately below.
            for outcome, target in nodes[id]['transitions'].items():
                walk(target, stack+(id,), required[:4] if outcome == 'done' else stages)
            validated.add(key)
            return
        if stage == 'correction':
            if stages != required:
                raise Blocked('correction scheduling must follow full-range review')
            stages = required[:2]
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
    def __init__(self, authority, run_id, config, registry, resource_root, phase_hook=None, *, max_task_visits=None, input_identity=None, boundary_hook=None, workflow_source=None):
        self.authority, self.store = authority, authority.store
        admitted = load_workflow(registry, workflow_source if workflow_source is not None else yaml.safe_dump(config), resource_root)
        if admitted != config:
            raise Blocked('retained workflow differs from configured graph')
        config = admitted
        self.run_id, self.config, self.registry = run_id, config, registry
        self.resource_root = resource_root
        # Compatibility is declared protocol/configuration/authority, not source bytes.
        self.input_identity = input_identity
        self.max_task_visits = max_task_visits
        self.hash = self.compatibility_hash(config, registry, input_identity, max_task_visits)
        self.revision = self.runtime_revision()
        self.progress = any(registry.handler(n).stage == 'task_select' for n in config['nodes'])
        if self.progress and (type(max_task_visits) is not int or max_task_visits < 0):
            raise Blocked('bounded approved task count required')
        self.hook = phase_hook or (lambda phase, op: None)
        self.boundary_hook = boundary_hook or (lambda: None)
        self.store.reserve_attempt(run_id, self.hash, self.revision, config,
                                   workflow_source.decode() if isinstance(workflow_source, bytes) else workflow_source or yaml.safe_dump(config))
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

    @staticmethod
    def compatibility_hash(config, registry, input_identity, max_task_visits):
        return digest({'config':config,'registry':registry.identity(),
                            'engine_protocol':2,'application_schema':1,'schemas':schemas(),
                            'inputs':input_identity,'task_visit_bound':max_task_visits})

    def _node(self, node):
        handler = self.registry.handler(node)
        def execute(state):
            self.authority.assert_held()
            self.boundary_hook()
            trace_before = state.get('trace',[])
            visit = sum(item['node'] == node['id'] for item in trace_before)
            if self.progress and visit > self.max_task_visits:
                raise Blocked('task-progress visit bound exhausted')
            logical = node['id'] + ':' + str(visit) if self.progress else node['id']
            args = {'config_hash':self.hash,'node':node,'trace':trace_before}
            details = {'handler':handler.id,'version':handler.version,'input_hash':digest(args)}
            # Interrupt is pure and precedes the graph operation intent: LangGraph
            # restarts an interrupted node from its beginning, never replaying an
            # uncertain question/dispatch effect.
            parked_result = handler.function({'node':node,'run_id':self.run_id,'operation_id':'park'}) if handler.stage == 'owner_input' else None
            old = self.store.db.execute('SELECT * FROM wf_operations WHERE run_id=? AND node_id=? AND kind=?',
                                         (self.run_id,logical,'graph')).fetchone()
            if handler.stage not in ('owner_input','continue_original'):
                parked_replay = (old and old['phase']=='completed' and old['result'] and
                                 json.loads(old['result']).get('outcome')=='owner_input_required')
                if parked_replay:
                    gate=self.store.db.execute("SELECT pin FROM wf_questions WHERE run_id=? AND stage IN ('pending','answered')",(self.run_id,)).fetchone()
                    if not gate or json.loads(gate['pin']).get('graph_op') != old['op_id']:
                        raise Blocked('parked graph replay lacks exact original operation pin')
                else:
                    self.store.assert_dispatchable(self.run_id)
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
                result = parked_result if parked_result is not None else handler.function(context)
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
    def runtime_revision():
        """Observation only: installed packages without Git honestly lack a revision."""
        try:
            return git(Path(__file__).resolve().parent, 'rev-parse', 'HEAD').decode().strip()
        except Blocked:
            return None

    def invoke(self):
        self.authority.assert_held()
        if self.compatibility_hash(self.config, self.registry, self.input_identity, self.max_task_visits) != self.hash:
            raise Blocked('configuration/registry/authority drift; construct a compatible attempt before invocation')
        self.boundary_hook()
        if self.store.db.execute("SELECT 1 FROM wf_operations WHERE run_id=? AND kind!='graph' AND phase!='completed'", (self.run_id,)).fetchone():
            raise Blocked('incomplete SDK/tool/Git effect; reconcile original operation before replay')
        if self.store.db.in_transaction:
            raise Blocked('application transaction held across saver')
        state = self.graph.get_state(self.thread)
        if state.values and not state.next:
            self.audit(state.values)
            return state.values
        incoming = None if state.values else {'trace':[],'outcome':''}
        pauses=[pause for task in state.tasks for pause in getattr(task,'interrupts',())]
        ready=bool(pauses) and all(isinstance(pause.value,dict) and
            self.store.db.execute("SELECT 1 FROM wf_questions WHERE run_id=? AND gate_id=? AND stage='answered'",(self.run_id,pause.value.get('gate_id'))).fetchone() for pause in pauses)
        if pauses and not ready:
            result={**state.values,'__interrupt__':pauses}
            checkpoint=state
        else:
            if pauses:incoming = Command(resume={'source':'runner_revalidated'})
            result = self.graph.invoke(incoming,self.thread,durability='sync')
            checkpoint = self.graph.get_state(self.thread)
        if checkpoint.next and result.get('__interrupt__'):
            for task in checkpoint.tasks:
                for paused in task.interrupts:
                    value=paused.value
                    if not isinstance(value,dict) or 'gate_id' not in value:raise Blocked('unknown graph owner interrupt')
                    gate=self.store.db.execute('SELECT * FROM wf_questions WHERE run_id=? AND gate_id=?',(self.run_id,value['gate_id'])).fetchone()
                    if not gate or gate['stage']!='pending':raise Blocked('graph park lacks pending SQL gate')
                    pin=json.loads(gate['pin'])
                    if not any(entry['operation_id']==pin['graph_op'] for entry in checkpoint.values.get('trace',[])):
                        raise Blocked('graph park lacks original completed visit')
                    checkpoint_id=checkpoint.config['configurable']['checkpoint_id']
                    with self.store.transaction() as db:
                        old=db.execute('SELECT * FROM wf_question_parks WHERE gate_id=?',(gate['gate_id'],)).fetchone()
                        if not old:
                            db.execute('INSERT INTO wf_question_parks VALUES(?,?,?,?)',(gate['gate_id'],checkpoint_id,task.name,pin['graph_op']))
                            self.store.event(db,self.run_id,None,'question_graph_parked',{'gate_id':gate['gate_id'],'checkpoint_id':checkpoint_id,'node_id':task.name,'original_graph_op':pin['graph_op']})
                        elif old['original_graph_op']!=pin['graph_op'] or old['node_id']!=task.name:
                            raise Blocked('graph park identity drift')
            return {**result, 'outcome':'waiting_owner_input'}
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
