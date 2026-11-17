// Offline installed-SDK lifecycle -> production bridge/socket -> adapter/history.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {piSdk} from '../pi-host/sdk.mjs';
import bridge from '../pi-extensions/coordinate-implementation-bridge.js';
import {installSteeringProvider} from './fixtures/steering_adapter_fixture.mjs';

const repository = fileURLToPath(new URL('../../', import.meta.url));
const {DefaultResourceLoader, SettingsManager, ModelRuntime, SessionManager, createAgentSession} = piSdk;

test('installed SDK tool hooks preserve actual parent facts through socket and reopened history', {timeout: 30000}, async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'parent-trace-'));
  const provider = installSteeringProvider('parent-trace', root);
  let session;
  try {
    await fs.mkdir(path.join(root, 'scripts'));
    await fs.writeFile(path.join(root, 'scripts/coordinate-implementation'), `#!/usr/bin/env python3
import json, os, sys
from unittest.mock import patch
sys.path.insert(0, ${JSON.stringify(path.join(repository, 'runtime'))})
from coherence_workflow.store import Authority
from coherence_workflow.pi_adapter import parent_question, drain_parent_trace
from coherence_workflow.trace_capture import persist_parent_events
import subprocess
subprocess.run(['git','init','-q'],check=True)
owner=Authority(os.getcwd())
store=owner.store
first=[]
def observer(run, events):
 if not first: first.extend(events)
 persist_parent_events(store, run, events)
# Simulate an acknowledgement lost before the bridge receives it, after the
# batch committed. Reopening then draining must preserve IDs, not duplicate rows.
import socket
real_socket=socket.socket
class LostAck:
 def __init__(self, *args, **kwargs): self.sock=real_socket(*args, **kwargs)
 def __enter__(self): return self
 def __exit__(self, *args): self.sock.close()
 def connect(self, *args): return self.sock.connect(*args)
 def sendall(self, data):
  if json.loads(data)['type']=='trace_ack': raise OSError('fixture ack loss')
  return self.sock.sendall(data)
 def makefile(self, *args, **kwargs): return self.sock.makefile(*args, **kwargs)
with patch('coherence_workflow.pi_adapter.socket.socket', LostAck):
 assert parent_question('worker wording', trace_observer=observer)=='coordinator resolution'
owner.close()
owner=Authority(os.getcwd())
store=owner.store
again=[]
def reobserve(run, events):
 again.extend(events)
 persist_parent_events(store, run, events)
assert drain_parent_trace(reobserve, final=True)
assert {e['id'] for e in first} <= {e['id'] for e in again}
assert any(e['kind']=='gap' and e['tool_call_id']=='owner-missing' for e in again)
# An abandoned pending request is a transport gap, not a synthetic reply.
import time, uuid
with real_socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
 client.connect(os.environ['COHERENCE_PARENT_BRIDGE_SOCKET'])
 client.sendall((json.dumps({'type':'question','request_id':'lost-request',
  'run_id':os.environ['COHERENCE_PARENT_BRIDGE_RUN'], 'session_id':os.environ['COHERENCE_PARENT_BRIDGE_SESSION'],
  'token':os.environ['COHERENCE_PARENT_BRIDGE_TOKEN'], 'question':'abandoned'})+'\\n').encode())
 time.sleep(.1)
time.sleep(.1)
from pathlib import Path
limit=time.monotonic()+10
while not Path('reply-failed').exists():
 assert time.monotonic()<limit, 'reply failure fixture timed out'
 time.sleep(.01)
assert drain_parent_trace(reobserve, final=True)
assert any(e['kind']=='gap' and e.get('request_id')=='lost-request' and 'transport lost' in e['reason'] for e in again)
rows=[json.loads(r[0]) for r in store.db.execute("select details from execution_history where kind='parent_trace' order by seq")]
assert len(rows)>=7, rows
assert any(r['event']['kind']=='coordinator_reply' and r['event']['answer']=='coordinator resolution' for r in rows)
assert {r['event']['tool_call_id'] for r in rows if r['event']['kind']=='owner_result'}=={'owner-one','owner-two','owner-error'}
owner.close()
owner=Authority(os.getcwd())
store=owner.store
assert store.db.execute("select count(*) from execution_history where kind='parent_trace'").fetchone()[0]==len(rows)
owner.close()
`, {mode: 0o700});
    const messages = [];
    let releaseMissing;
    const missing = new Promise(resolve => { releaseMissing = resolve; });
    const started = [];
    const loader = new DefaultResourceLoader({cwd: root, agentDir: root, settingsManager: SettingsManager.inMemory(),
      noSkills: true, noPromptTemplates: true, noThemes: true, noContextFiles: true, noExtensions: true,
      extensionFactories: [bridge, pi => pi.registerTool({name: 'ask_user', label: 'Owner', description: 'offline owner',
        parameters: {type: 'object', properties: {question: {type: 'string'}}, required: ['question']},
        execute: async (id, args) => {
          started.push(id);
          if (id === 'owner-missing') await missing;
          if (id === 'owner-error') throw new Error('fixture owner tool failure');
          return {content: [{type: 'text', text: `actual ${id}`}],
            details: {question: args.question, response: {selection: id, freeform: 'owner freeform', comment: 'owner comment'}, cancelled: id === 'owner-two'}};
        }})]});
    await loader.reload();
    const runtime = await ModelRuntime.create({});
    const model = runtime.getModel('openai', 'gpt-4o-mini');
    const manager = SessionManager.create(root, path.join(root, 'sessions'));
    ({session} = await createAgentSession({cwd: root, modelRuntime: runtime, model, thinkingLevel: 'off',
      tools: ['ask_user', 'coordinate_implementation_start', 'coordinate_implementation_reply'], sessionManager: manager, resourceLoader: loader}));
    await session.bindExtensions({});
    const loaded = loader.getExtensions();
    loaded.runtime.sendMessage = message => messages.push(message);
    const ext = loaded.extensions.find(item => item.tools.has('coordinate_implementation_start'));
    const ctx = {cwd: root, sessionManager: manager};
    const call = (name, args) => ext.tools.get(name).definition.execute(name, args, undefined, undefined, ctx);
    await call('coordinate_implementation_start', {run: 'parent-run', tasks: 'unused', executor: 'unused'});
    const wait = async pred => { const end = Date.now() + 15000; while (!pred()) { assert.ok(Date.now() < end, 'bridge event timeout'); await new Promise(r => setTimeout(r, 10)); } };
    await wait(() => messages.some(m => m.customType === 'coordinate_implementation_question'));
    const prompting = session.prompt('offline owner questions');
    await wait(() => started.length === 4);
    const question = messages.find(m => m.customType === 'coordinate_implementation_question');
    await call('coordinate_implementation_reply', {run: 'parent-run', request_id: question.details.request_id, answer: 'coordinator resolution'});
    await wait(() => messages.some(m => m.customType === 'coordinate_implementation_question' && m.details.request_id === 'lost-request'));
    await new Promise(resolve => setTimeout(resolve, 200));
    await assert.rejects(call('coordinate_implementation_reply', {run: 'parent-run', request_id: 'lost-request', answer: 'not delivered'}), /no matching pending/);
    await fs.writeFile(path.join(root, 'reply-failed'), 'observed');
    await wait(() => messages.some(m => m.customType === 'coordinate_implementation_complete'));
    assert.match(messages.find(m => m.customType === 'coordinate_implementation_complete').content, /exit 0/);
    releaseMissing();
    await prompting;
    const {stdout} = await import('node:child_process').then(({execFileSync}) => ({stdout: execFileSync('python3', ['-c', `import sqlite3,json,sys
r=sqlite3.connect(sys.argv[1]).execute("select details from execution_history where kind='parent_trace'").fetchall()
print(json.dumps([json.loads(x[0]) for x in r]))`, path.join(root, '.coherence/workflow/workflow.sqlite')], {encoding: 'utf8'})}));
    const events = JSON.parse(stdout).map(row => row.event);
    assert.deepEqual(events.filter(e => e.kind === 'owner_call').map(e => e.tool_call_id), ['owner-one', 'owner-two', 'owner-missing', 'owner-error']);
    assert.ok(events.findIndex(e => e.kind === 'owner_call' && e.tool_call_id === 'owner-two') <
      events.findIndex(e => e.kind === 'owner_result' && e.tool_call_id === 'owner-one'), 'SDK calls interleave before results');
    assert.equal(events.find(e => e.tool_call_id === 'owner-one' && e.kind === 'owner_result').content[0].text, 'actual owner-one');
    assert.equal(events.find(e => e.tool_call_id === 'owner-one' && e.kind === 'owner_result').details.response.comment, 'owner comment');
    assert.equal(events.find(e => e.tool_call_id === 'owner-two' && e.kind === 'owner_result').details.cancelled, true);
    assert.equal(events.find(e => e.tool_call_id === 'owner-error' && e.kind === 'owner_result').is_error, true);
    assert.ok(events.some(e => e.kind === 'coordinator_reply' && e.answer === 'coordinator resolution'));
  } finally {
    session?.dispose();
    provider.mock.restore();
    await fs.rm(root, {recursive: true, force: true});
  }
});

test('conflicting SDK IDs remain gaps rather than false result pairings', {timeout: 15000}, async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'parent-conflict-'));
  const handlers = new Map(), tools = new Map(), messages = [];
  const pi = {on: (name, fn) => handlers.set(name, fn), registerTool: tool => tools.set(tool.name, tool),
    getActiveTools: () => [...tools.keys()], sendMessage: value => messages.push(value)};
  try {
    await fs.mkdir(path.join(root, 'scripts'));
    await fs.writeFile(path.join(root, 'scripts/coordinate-implementation'), `#!/usr/bin/env python3
import json,sys,time
from pathlib import Path
sys.path.insert(0, ${JSON.stringify(path.join(repository, 'runtime'))})
from coherence_workflow.store import Store
from coherence_workflow.trace_capture import persist_parent_events
from coherence_workflow.pi_adapter import drain_parent_trace
class Authority:
 def assert_held(self): pass
store=Store('history.sqlite',Authority())
limit=time.monotonic()+10
while not Path('ready').exists():
 assert time.monotonic()<limit
 time.sleep(.01)
assert drain_parent_trace(lambda run, events: persist_parent_events(store,run,events),final=True)
events=[json.loads(row[0])['event'] for row in store.db.execute("select details from execution_history where kind='parent_trace'")]
assert any(e['kind']=='gap' and 'conflicting' in e['reason'] for e in events)
assert not any(e['kind']=='owner_result' for e in events)
store.close()
`, {mode: 0o700});
    bridge(pi);
    await tools.get('coordinate_implementation_start').execute('start', {run: 'conflict', tasks: 'unused', executor: 'unused'}, undefined, undefined,
      {cwd: root, sessionManager: {getSessionId: () => 'session'}});
    const call = {toolName: 'ask_user', toolCallId: 'same', input: {question: 'first'}};
    handlers.get('tool_call')(call);
    handlers.get('tool_call')({...call, input: {question: 'different'}});
    handlers.get('tool_result')({...call, content: [{type: 'text', text: 'ambiguous'}], details: {}, isError: false});
    await fs.writeFile(path.join(root, 'ready'), 'ready');
    const end = Date.now() + 10000;
    while (!messages.some(m => m.customType === 'coordinate_implementation_complete')) {
      assert.ok(Date.now() < end); await new Promise(resolve => setTimeout(resolve, 10));
    }
    assert.match(messages.find(m => m.customType === 'coordinate_implementation_complete').content, /exit 0/);
  } finally {
    await handlers.get('session_shutdown')?.();
    await fs.rm(root, {recursive: true, force: true});
  }
});
