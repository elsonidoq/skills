// Offline parent-extension fixture: real runner/adapter framing, no provider call.
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath, pathToFileURL } from 'node:url';

const repository = fileURLToPath(new URL('../../', import.meta.url));
const bridgeModule = pathToFileURL(path.join(repository, '.pi/extensions/coordinate-implementation-bridge.mjs')).href;

function mockPi(messages, tools) {
  return {
    registerTool(tool) { tools.set(tool.name, tool); },
    on(event, handler) { if (event === 'session_shutdown') this.shutdown = handler; },
    sendMessage(message, options) { messages.push({message, options}); },
  };
}

async function fixture() {
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
  await fs.writeFile(tasks, JSON.stringify([{id: 'question', description: 'Ask then continue'}]));
  await fs.writeFile(executor, JSON.stringify({provider: 'fixture', model: 'offline', effort: 'medium'}));
  await fs.writeFile(host, `import json, sys
request=json.loads(input())
if request['readOnly']:
 print(json.dumps({'type':'result','text':'{"approved":true,"findings":[]}'}), flush=True)
else:
 print(json.dumps({'type':'question','question':'Fixture owner question?'}), flush=True)
 assert json.loads(input()) == {'answer':'yes'}
 print(json.dumps({'type':'result','text':'continued'}), flush=True)
`);
  await fs.writeFile(node, `#!/bin/sh\nexec python3 ${JSON.stringify(host)}\n`, {mode: 0o700});
  return {root, project, tasks, executor, host, node};
}

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
