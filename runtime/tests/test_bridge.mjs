// Offline parent-extension fixture: real runner/adapter framing, no provider call.
import assert from 'node:assert/strict';
import { execFile, execFileSync } from 'node:child_process';
import { promisify } from 'node:util';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath, pathToFileURL } from 'node:url';

const repository = fileURLToPath(new URL('../../', import.meta.url));
const bridgeModule = pathToFileURL(path.join(repository, 'runtime/pi-extensions/coordinate-implementation-bridge.js')).href;

// Exercise Pi's normal global discovery, not a direct import of the factory.
test('Pi discovers the global bridge and registers its tools without explicit paths', async () => {
  const {piSdk: {DefaultResourceLoader, SettingsManager}} = await import('../pi-host/sdk.mjs');
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'coordinate-discovery-'));
  try {
    const project = path.join(root, 'project');
    await fs.mkdir(project, {recursive: true});
    await fs.mkdir(path.join(root, 'agent/extensions'), {recursive: true});
    await fs.symlink(new URL(bridgeModule), path.join(root, 'agent/extensions/coordinate-implementation-bridge.js'));
    const loader = new DefaultResourceLoader({
      cwd: project, agentDir: path.join(root, 'agent'),
      settingsManager: SettingsManager.inMemory(),
      noSkills: true, noPromptTemplates: true, noThemes: true, noContextFiles: true,
    });
    await loader.reload();
    const loaded = loader.getExtensions();
    assert.deepEqual(loaded.errors, []);
    const bridge = loaded.extensions.find(extension =>
      extension.tools.has('coordinate_implementation_start'));
    assert.ok(bridge, 'normal global discovery must register the bridge start tool');
    assert.ok(bridge.tools.has('coordinate_implementation_reply'));
    assert.ok(bridge.tools.has('coordinate_implementation_owner_reply'));
    assert.ok(bridge.tools.has('coordinate_implementation_steer'));
  } finally {
    await fs.rm(root, {recursive: true, force: true});
  }
});

test('registered parent steering tool reaches the production adapter, host and real SDK queue while its question waits', {timeout: 20000}, async () => {
  const {piSdk: {DefaultResourceLoader, SettingsManager}} = await import('../pi-host/sdk.mjs');
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'coordinate-real-steering-'));
  const messages = [];
  const abort = new AbortController();
  const previous = {...process.env};
  try {
    await fs.mkdir(path.join(root, 'parent-agent/extensions'), {recursive: true});
    await fs.symlink(new URL(bridgeModule), path.join(root, 'parent-agent/extensions/coordinate-implementation-bridge.js'));
    await fs.mkdir(path.join(root, 'scripts'));
    // Only the launcher is a fixture: it exercises one production PiAdapter
    // prompt, not an implementation workflow or replacement host dispatcher.
    const python = execFileSync(process.env.COHERENCE_PYTHON || 'python3',
      ['-c', 'import sys; print(sys.executable)'], {encoding: 'utf8'}).trim();
    await fs.writeFile(path.join(root, 'scripts/coordinate-implementation'), `#!${python}\nimport sys,os\nsys.path.insert(0, ${JSON.stringify(path.join(repository, 'runtime'))})\nfrom coherence_workflow.pi_adapter import PiAdapter,parent_question\ntarget={'run_id':'offline-steering','task_id':'T010','invocation_id':'exact-call','role':'task_worker'}\nadapter=PiAdapter(os.getcwd(), {'provider':'openai','model':'gpt-4o-mini','effort':'off'}, question=parent_question)\nassert adapter.enable_parent_steering(target)\nassert adapter.prompt('controlled offline prompt',steering=target)=='steering complete'\nassert adapter.steering_states['direction-1']=='consumed'\nassert adapter.steering_states['direction-2']=='consumed'\n`, {mode: 0o700});
    process.env.NODE_OPTIONS = '--import=' + path.join(repository, 'runtime/tests/fixtures/steering_adapter_fixture.mjs');
    process.env.COHERENCE_HOST_PRELOAD = '1';
    process.env.COHERENCE_NODE = process.execPath;
    process.env.PI_CODING_AGENT_DIR = path.join(root, 'private-agent');
    const loader = new DefaultResourceLoader({cwd: root, agentDir: path.join(root, 'parent-agent'),
      settingsManager: SettingsManager.inMemory(), noSkills: true, noPromptTemplates: true, noThemes: true, noContextFiles: true});
    await loader.reload();
    const loaded = loader.getExtensions();
    assert.deepEqual(loaded.errors, []);
    const extension = loaded.extensions.find(item => item.tools.has('coordinate_implementation_steer'));
    assert.ok(extension, 'normal global discovery registered the actual steering tool');
    const wakeups = [];
    loaded.runtime.sendMessage = (message, options) => {
      messages.push(message);
      wakeups.push({message, options});
    };
    loaded.runtime.getActiveTools = () => [...extension.tools.keys()];
    const ctx = {cwd: root, sessionManager: {getSessionId: () => 'offline-parent'}};
    const call = (name, params, signal) => extension.tools.get(name).definition.execute(name, params, signal, undefined, ctx);
    const until = async predicate => {
      const end = Date.now() + 15000;
      while (!predicate()) {
        assert.ok(Date.now() < end, `timed out waiting for real SDK/bridge event: ${JSON.stringify(messages)}`);
        await new Promise(resolve => setTimeout(resolve, 10));
      }
    };
    await call('coordinate_implementation_start', {tasks: 'unused', executor: 'unused', run: 'offline-steering'}, abort.signal);
    await until(() => messages.some(item => item.customType === 'coordinate_implementation_question') && messages.some(item => item.customType === 'coordinate_implementation_target'));
    const target = messages.find(item => item.customType === 'coordinate_implementation_target').details;
    assert.equal(target.task_id, 'T010'); assert.equal(target.invocation_id, 'exact-call');
    const direction = {request_id: 'direction-1', run: 'offline-steering', task_id: target.task_id, invocation_id: target.invocation_id, instruction: '/inert identical direction'};
    await assert.rejects(call('coordinate_implementation_steer', {...direction, invocation_id: 'successor'}), /exact active worker target unavailable/);
    assert.equal((await call('coordinate_implementation_steer', direction)).details.status, 'accepted');
    await until(() => messages.some(item => item.customType === 'coordinate_implementation_steering_status' && item.details.status === 'queued'));
    assert.equal((await call('coordinate_implementation_steer', direction)).details.status, 'queued', 'same ID is idempotent');
    await call('coordinate_implementation_steer', {...direction, request_id: 'direction-2'});
    await until(() => messages.some(item => item.details?.request_id === 'direction-2' && item.details.status === 'queued'));
    assert.equal(messages.some(item => item.details?.status === 'consumed'), false, 'steering cannot answer the pending owner question');
    const question = messages.find(item => item.customType === 'coordinate_implementation_question');
    await call('coordinate_implementation_reply', {run: 'offline-steering', request_id: question.details.request_id, answer: 'ordinary callback'});
    await until(() => messages.some(item => item.customType === 'coordinate_implementation_complete'));
    assert.match(messages.find(item => item.customType === 'coordinate_implementation_complete').content, /exit 0/);
    for (const id of ['direction-1', 'direction-2']) {
      const states = messages.filter(item => item.customType === 'coordinate_implementation_steering_status' && item.details.request_id === id);
      assert.equal(states.at(-1).details.status, 'consumed');
      assert.ok(states.every(item => item.details.task_id === 'T010' && item.details.invocation_id === 'exact-call'));
    }
    await assert.rejects(call('coordinate_implementation_steer', direction), /no matching active/);
    for (const {message, options} of wakeups) {
      const shouldWake = ['coordinate_implementation_question', 'coordinate_implementation_complete'].includes(message.customType);
      assert.equal(options.triggerTurn, shouldWake, message.customType);
      assert.equal(options.deliverAs, shouldWake ? 'followUp' : undefined, message.customType);
    }
  } finally {
    abort.abort();
    for (const key of ['NODE_OPTIONS', 'COHERENCE_HOST_PRELOAD', 'COHERENCE_NODE', 'PI_CODING_AGENT_DIR']) {
      if (previous[key] === undefined) delete process.env[key]; else process.env[key] = previous[key];
    }
    await fs.rm(root, {recursive: true, force: true});
  }
});

test('runner output stays off the parent RPC stdout channel', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'coordinate-rpc-output-'));
  try {
    await fs.mkdir(path.join(root, 'scripts'));
    await fs.writeFile(path.join(root, 'scripts/coordinate-implementation'),
      '#!/bin/sh\nprintf "RUNNER-STDOUT\\n"\nprintf "RUNNER-STDERR\\n" >&2\n', {mode: 0o700});
    const code = `
      import bridge from ${JSON.stringify(bridgeModule)};
      const tools = new Map();
      bridge({registerTool: tool => tools.set(tool.name, tool), getActiveTools: () => [...tools.keys()], on() {},
        sendMessage(message) { process.stdout.write(JSON.stringify({type: message.customType}) + '\\n'); }});
      await tools.get('coordinate_implementation_start').execute('start',
        {tasks: 'unused', executor: 'unused', run: 'output-probe'}, undefined, undefined,
        {cwd: ${JSON.stringify(root)}, sessionManager: {getSessionId: () => 'output-parent'}});
    `;
    const {stdout, stderr} = await promisify(execFile)(process.execPath, ['--input-type=module', '-e', code]);
    assert.deepEqual(stdout.trim().split('\n').map(line => JSON.parse(line)),
      [{type: 'coordinate_implementation_complete'}]);
    assert.match(stderr, /RUNNER-STDOUT/);
    assert.match(stderr, /RUNNER-STDERR/);
  } finally { await fs.rm(root, {recursive: true, force: true}); }
});

function mockPi(messages, tools) {
  return {
    registerTool(tool) { tools.set(tool.name, tool); },
    getActiveTools() { return [...tools.keys()]; },
    on(event, handler) { if (event === 'session_shutdown') this.shutdown = handler; },
    sendMessage(message, options) { messages.push({message, options}); },
  };
}

async function fixture({hold = false, paidScope = false, paidApis = []} = {}) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'coordinate-bridge-'));
  const project = path.join(root, 'project');
  await fs.mkdir(path.join(project, 'scripts'), {recursive: true});
  await fs.symlink(path.join(repository, 'scripts/coordinate-implementation'), path.join(project, 'scripts/coordinate-implementation'));
  execFileSync('git', ['init', '-q', project]);
  execFileSync('git', ['-C', project, 'config', 'user.name', 'Fixture']);
  execFileSync('git', ['-C', project, 'config', 'user.email', 'fixture@example.invalid']);
  await fs.writeFile(path.join(project, 'base.txt'), 'base\n');
  execFileSync('git', ['-C', project, 'add', '--', '.']);
  execFileSync('git', ['-C', project, 'commit', '-qm', 'base']);
  const tasks = path.join(root, 'tasks.json');
  const executor = path.join(root, 'executor.json');
  const host = path.join(root, 'offline-host.py');
  const node = path.join(root, 'offline-node');
  const marker = path.join(root, 'host-started');
  await fs.writeFile(tasks, JSON.stringify({...(paidScope ? {paid_scope: {approved: true, agent_providers: ['fixture'], apis: ['fixture test API']}} : {}), paid_apis: paidApis, tasks: [{id: 'question', description: 'Ask then continue'}]}));
  await fs.writeFile(executor, JSON.stringify({provider: 'fixture', model: 'offline', effort: 'medium',
    reviewer: {provider: 'fixture', model: 'offline', effort: 'medium'}}));
  await fs.writeFile(host, hold ? `import os, pathlib, sys, time
json = __import__('json')
request=json.loads(input())
if request['readOnly']:
 print(json.dumps({'type':'result','text':'{"approved":true,"findings":[]}'}), flush=True)
else:
 pathlib.Path(${JSON.stringify(marker)}).write_text(str(os.getpid()))
 time.sleep(1000)
` : `import json, sys
request=json.loads(input())
if request['readOnly']:
 print(json.dumps({'type':'result','text':'{"approved":true,"findings":[]}'}), flush=True)
else:
 print(json.dumps({'type':'question','question':'Fixture owner question?'}), flush=True)
 assert json.loads(input()) == {'answer':'yes'}
 print(json.dumps({'type':'result','text':'continued'}), flush=True)
`);
  await fs.writeFile(node, `#!/bin/sh\nexec python3 ${JSON.stringify(host)}\n`, {mode: 0o700});
  return {root, project, tasks, executor, host, node, marker};
}

test('missing parent reply capability stops the actual CLI before storage or SDK launch', async () => {
  const value = await fixture({hold: true});
  const messages = [], tools = new Map();
  const pi = mockPi(messages, tools);
  pi.getActiveTools = () => ['coordinate_implementation_start'];
  const {default: bridge} = await import(bridgeModule);
  const originalNode = process.env.COHERENCE_NODE;
  process.env.COHERENCE_NODE = value.node;
  try {
    bridge(pi);
    await tools.get('coordinate_implementation_start').execute('start',
      {tasks: value.tasks, executor: value.executor, run: 'not-ready'}, undefined, undefined,
      {cwd: value.project, sessionManager: {getSessionId: () => 'parent-session'}});
    while (!messages.some(item => item.message.customType === 'coordinate_implementation_complete'))
      await new Promise(resolve => setTimeout(resolve, 10));
    assert.match(messages.at(-1).message.content, /exit 2/);
    assert.equal(messages.at(-1).options.triggerTurn, true, 'terminal errors must wake the parent');
    await assert.rejects(fs.access(value.marker), {code: 'ENOENT'});
    await assert.rejects(fs.access(path.join(value.project, '.coherence')), {code: 'ENOENT'});
    assert.equal(messages.some(item => item.message.customType === 'coordinate_implementation_question'), false);
  } finally {
    if (originalNode === undefined) delete process.env.COHERENCE_NODE; else process.env.COHERENCE_NODE = originalNode;
    await pi.shutdown?.();
    await fs.rm(value.root, {recursive: true, force: true});
  }
});

test('bridge asks for unapproved paid APIs before launching the provider', async () => {
  const value = await fixture({hold: true, paidApis: ['fixture paid API']});
  const messages = [], tools = new Map();
  const pi = mockPi(messages, tools);
  const originalNode = process.env.COHERENCE_NODE;
  process.env.COHERENCE_NODE = value.node;
  try {
    const {default: bridge} = await import(bridgeModule);
    bridge(pi);
    const ctx = {cwd: value.project, sessionManager: {getSessionId: () => 'parent-session'}};
    await tools.get('coordinate_implementation_start').execute('start', {tasks: value.tasks, executor: value.executor, run: 'paid-scope'}, undefined, undefined, ctx);
    while (!messages.some(item => item.message.customType === 'coordinate_implementation_question')) await new Promise(resolve => setTimeout(resolve, 10));
    const question = messages.find(item => item.message.customType === 'coordinate_implementation_question');
    assert.match(question.message.content, /Approve paid application\/test APIs: fixture paid API/);
    assert.doesNotMatch(question.message.content, /agent-provider/);
    await assert.rejects(fs.access(value.marker), {code: 'ENOENT'});
    await tools.get('coordinate_implementation_reply').execute('reply', {request_id: question.message.details.request_id, run: 'paid-scope', answer: 'no'}, undefined, undefined, ctx);
    while (!messages.some(item => item.message.customType === 'coordinate_implementation_complete')) await new Promise(resolve => setTimeout(resolve, 10));
    assert.match(messages.at(-1).message.content, /exit 2/);
    await assert.rejects(fs.access(value.marker), {code: 'ENOENT'});
  } finally {
    if (originalNode === undefined) delete process.env.COHERENCE_NODE; else process.env.COHERENCE_NODE = originalNode;
    await pi.shutdown?.();
    await fs.rm(value.root, {recursive: true, force: true});
  }
});

test('bridge session shutdown cancels and waits for only its owned runner', async () => {
  const value = await fixture({hold: true});
  const messages = [], tools = new Map();
  const pi = mockPi(messages, tools);
  const {default: bridge} = await import(bridgeModule);
  const originalNode = process.env.COHERENCE_NODE;
  process.env.COHERENCE_NODE = value.node;
  try {
    bridge(pi);
    const ctx = {cwd: value.project, sessionManager: {getSessionId: () => 'parent-session'}};
    await tools.get('coordinate_implementation_start').execute('start', {tasks: value.tasks, executor: value.executor, run: 'cancelled'}, undefined, undefined, ctx);
    while (!(await fs.stat(value.marker).then(() => true, () => false))) await new Promise(resolve => setTimeout(resolve, 10));
    const hostPid = Number(await fs.readFile(value.marker, 'utf8'));
    await pi.shutdown();
    assert.throws(() => process.kill(hostPid, 0), {code: 'ESRCH'});
    execFileSync('python3', ['-c', "import fcntl; f=open('.git/coherence-workflow.lock', 'r+'); fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)"], {cwd: value.project});
  } finally {
    if (originalNode === undefined) delete process.env.COHERENCE_NODE; else process.env.COHERENCE_NODE = originalNode;
    await fs.rm(value.root, {recursive: true, force: true});
  }
});

test('bridge start abort signal cancels the retained owned runner after launch', async () => {
  const value = await fixture({hold: true});
  const messages = [], tools = new Map();
  const pi = mockPi(messages, tools);
  const {default: bridge} = await import(bridgeModule);
  const controller = new AbortController();
  const originalNode = process.env.COHERENCE_NODE;
  process.env.COHERENCE_NODE = value.node;
  try {
    bridge(pi);
    const ctx = {cwd: value.project, sessionManager: {getSessionId: () => 'parent-session'}};
    await tools.get('coordinate_implementation_start').execute('start', {tasks: value.tasks, executor: value.executor, run: 'aborted'}, controller.signal, undefined, ctx);
    while (!(await fs.stat(value.marker).then(() => true, () => false))) await new Promise(resolve => setTimeout(resolve, 10));
    controller.abort();
    while (!messages.some(item => item.message.customType === 'coordinate_implementation_complete')) await new Promise(resolve => setTimeout(resolve, 10));
    execFileSync('python3', ['-c', "import fcntl; f=open('.git/coherence-workflow.lock', 'r+'); fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)"], {cwd: value.project});
  } finally {
    if (originalNode === undefined) delete process.env.COHERENCE_NODE; else process.env.COHERENCE_NODE = originalNode;
    await pi.shutdown?.();
    await fs.rm(value.root, {recursive: true, force: true});
  }
});

test('bridge launches explicit same-run resume without replacement task inputs', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'coordinate-resume-bridge-'));
  try {
    await fs.mkdir(path.join(root, 'scripts'));
    await fs.writeFile(path.join(root, 'scripts/coordinate-implementation'),
      '#!/bin/sh\nprintf "%s\\n" "$@" > resume-args\n', {mode: 0o700});
    const messages = [], tools = new Map();
    const pi = mockPi(messages, tools);
    const {default: bridge} = await import(bridgeModule);
    bridge(pi);
    await tools.get('coordinate_implementation_start').execute('resume', {run: 'failed-run', resume: true}, undefined, undefined,
      {cwd: root, sessionManager: {getSessionId: () => 'parent-session'}});
    while (!messages.some(item => item.message.customType === 'coordinate_implementation_complete'))
      await new Promise(resolve => setTimeout(resolve, 10));
    assert.deepEqual((await fs.readFile(path.join(root, 'resume-args'), 'utf8')).trim().split('\n'),
      ['resume', '--project', root, '--run', 'failed-run']);
  } finally { await fs.rm(root, {recursive: true, force: true}); }
});

for (const mode of ['idle', 'busy']) test(`bridge wakes ${mode} parent and returns the correlated answer`, async () => {
  const value = await fixture();
  const messages = [], tools = new Map();
  const pi = mockPi(messages, tools);
  const {default: bridge} = await import(bridgeModule);
  const originalNode = process.env.COHERENCE_NODE;
  process.env.COHERENCE_NODE = value.node;
  process.env.COHERENCE_AUTH_PATH = '';
  try {
    bridge(pi);
    const ctx = {cwd: value.project, sessionManager: {getSessionId: () => 'parent-session'}};
    await tools.get('coordinate_implementation_start').execute('start', {tasks: value.tasks, executor: value.executor, run: `run-${mode}`}, undefined, undefined, ctx);
    while (!messages.some(item => item.message.customType === 'coordinate_implementation_question')) await new Promise(resolve => setTimeout(resolve, 10));
    const question = messages.find(item => item.message.customType === 'coordinate_implementation_question');
    assert.equal(question.options.triggerTurn, true);
    assert.equal(question.options.deliverAs, 'followUp');
    assert.match(question.message.content, /Fixture owner question\?/);
    const requestId = question.message.details.request_id;
    await tools.get('coordinate_implementation_reply').execute('reply', {request_id: requestId, run: `run-${mode}`, answer: 'yes'}, undefined, undefined, ctx);
    await assert.rejects(() => tools.get('coordinate_implementation_reply').execute('duplicate', {request_id: requestId, run: `run-${mode}`, answer: 'yes'}, undefined, undefined, ctx), /no matching pending/);
    await assert.rejects(() => tools.get('coordinate_implementation_reply').execute('wrong-session', {request_id: requestId, run: `run-${mode}`, answer: 'yes'}, undefined, undefined, {...ctx, sessionManager: {getSessionId: () => 'other'}}), /no matching pending/);
    while (!messages.some(item => item.message.customType === 'coordinate_implementation_complete')) await new Promise(resolve => setTimeout(resolve, 10));
    const database = await fs.readFile(path.join(value.project, '.coherence/workflow/workflow.sqlite'));
    assert.equal(database.includes(Buffer.from('Fixture owner question?')), false);
    assert.equal(database.includes(Buffer.from('yes')), false);
  } finally {
    if (originalNode === undefined) delete process.env.COHERENCE_NODE; else process.env.COHERENCE_NODE = originalNode;
    await pi.shutdown?.();
    await fs.rm(value.root, {recursive: true, force: true});
  }
});
