// Offline SDK/tool behavior; not a mocked live-provider success claim.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { execFileSync, spawn } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { mock, test } from 'node:test';
import readline from 'node:readline';
import { AgentSession, createReadTool, createEditTool, createWriteTool, createBashTool } from '../pi-host/node_modules/@earendil-works/pi-coding-agent/dist/index.js';
import { createWorkflowSession, mutationTools, promptSession, steeringController } from '../pi-host/host.mjs';
import {installSteeringProvider} from './fixtures/steering_adapter_fixture.mjs';

test('actual SDK worker exposes ask_owner while independent reviewer remains read-only', async () => {
  const project = await fs.mkdtemp(path.join(os.tmpdir(), 'coherence-owner-tools-'));
  try {
    // Resolve local model metadata only: no prompt, provider request or authentication refresh.
    const executor = {provider: 'openai', model: 'gpt-4o-mini', effort: 'off'};
    for (const readOnly of [false, true]) {
      const session = await createWorkflowSession({project, executor, readOnly}, async () => ({answer: 'fixture'}));
      try {
        const tools = session.getActiveToolNames();
        if (readOnly) assert.deepEqual([...tools].sort(), ['find', 'grep', 'ls', 'read']);
        else assert.ok(tools.includes('ask_owner'), 'registered ask_owner must also be active for workers');
      } finally { session.dispose(); }
    }
    const missingTool = mock.method(AgentSession.prototype, 'getActiveToolNames', () => []);
    try {
      await assert.rejects(createWorkflowSession({project, executor}, async () => ({})), /Worker ask_owner tool unavailable/);
    } finally { missingTool.mock.restore(); }
  } finally { await fs.rm(project, {recursive: true, force: true}); }
});

test('exact SDK assignment rejects missing or clamped effort and post-construction drift before prompt', async () => {
  const project = await fs.mkdtemp(path.join(os.tmpdir(), 'coherence-exact-assignment-'));
  let promptCalls = 0;
  const prompt = mock.method(AgentSession.prototype, 'prompt', async () => { promptCalls++; });
  try {
    for (const executor of [
      {provider: 'openai', model: 'missing-model', effort: 'off'},
      {provider: 'openai', model: 'gpt-4o-mini', effort: 'medium'},
    ]) {
      await assert.rejects(createWorkflowSession({project, executor}, async () => ({})),
        /Model not found|exact SDK assignment mismatch/);
    }
    assert.equal(promptCalls, 0, 'invalid construction must not reach a provider prompt');

    const executor = {provider: 'openai', model: 'gpt-5', effort: 'medium'};
    const session = await createWorkflowSession({project, executor}, async () => ({}));
    try {
      assert.equal(session.model.id, executor.model);
      assert.equal(session.thinkingLevel, executor.effort);
      session.setThinkingLevel('low');
      await assert.rejects(() => promptSession(session, 'must not prompt', () => {}),
        /requested openai\/gpt-5 effort medium; observed openai\/gpt-5 effort low/);
      const auth = mock.method(session.modelRuntime, 'checkAuth', async () => ({}));
      try {
        await session.setModel(session.modelRuntime.getModel('openai', 'gpt-4o-mini'));
      } finally { auth.mock.restore(); }
      await assert.rejects(() => promptSession(session, 'must not prompt', () => {}),
        /requested openai\/gpt-5 effort medium; observed openai\/gpt-4o-mini effort off/);
      assert.equal(promptCalls, 0, 'last prompt boundary must reject post-construction drift');
    } finally { session.dispose(); }
  } finally {
    prompt.mock.restore();
    await fs.rm(project, {recursive: true, force: true});
  }
});

test('saved worker ignores mismatched persisted SDK assignment while retaining requested exact binding', async () => {
  const project = await fs.mkdtemp(path.join(os.tmpdir(), 'coherence-session-order-'));
  const executor = {provider: 'openai', model: 'gpt-4o-mini', effort: 'off'};
  const request = {project, executor, reuseKey: 'same-task'};
  try {
    const created = await createWorkflowSession(request, async () => ({}));
    let savedSession;
    try {
      created._coherenceSessionManager.appendMessage({role: 'assistant', content: [], stopReason: 'stop',
        api: 'test', provider: 'fixture', model: 'fixture', usage: {}});
      // A stale transcript must not override the explicit executor assignment.
      created._coherenceSessionManager.appendModelChange('openai', 'gpt-5');
      created._coherenceSessionManager.appendThinkingLevelChange('low');
      savedSession = JSON.parse(JSON.stringify(created.coherenceSavedSession));
    } finally { created.dispose(); }
    savedSession.compatibility = Object.fromEntries(Object.entries(savedSession.compatibility).sort());
    const reopened = await createWorkflowSession({...request, savedSession}, async () => ({}));
    try {
      assert.equal(reopened.coherenceSavedSession.id, savedSession.id);
      assert.equal(reopened.model.id, executor.model);
      assert.equal(reopened.thinkingLevel, executor.effort);
    } finally { reopened.dispose(); }
    for (const [key, value] of Object.entries({project: '/different', provider: 'different', model: 'different',
      effort: 'low', readOnly: true, reuseKey: 'different', extra: true})) {
      await assert.rejects(createWorkflowSession({...request,
        savedSession: {...savedSession, compatibility: {...savedSession.compatibility, [key]: value}}},
      async () => ({})), /saved session identity or effective resources mismatch/);
    }
  } finally { await fs.rm(project, {recursive: true, force: true}); }
});

test('explicit review repair retains transcript and identity while enabling only scoped writer tools', async () => {
  const project = await fs.mkdtemp(path.join(os.tmpdir(), 'coherence-review-repair-'));
  const skillDescription = 'REPAIR_SKILL_DISCOVERY_MUST_STAY_DISABLED';
  const executor = {provider: 'openai', model: 'gpt-4o-mini', effort: 'off'};
  const request = {project, executor};
  try {
    const skillDir = path.join(project, '.pi', 'skills', 'repair-fixture');
    await fs.mkdir(skillDir, {recursive: true});
    await fs.writeFile(path.join(skillDir, 'SKILL.md'),
      `---\nname: repair-fixture\ndescription: ${skillDescription}\n---\nFixture instructions.\n`);
    const worker = await createWorkflowSession(request, async () => ({}));
    try { assert.ok(worker.systemPrompt.includes(skillDescription)); }
    finally { worker.dispose(); }
    const reviewer = await createWorkflowSession({...request, readOnly: true}, async () => ({}));
    let savedSession;
    try {
      assert.ok(!reviewer.systemPrompt.includes(skillDescription));
      reviewer._coherenceSessionManager.appendMessage({role: 'assistant',
        content: [{type: 'text', text: 'warm review findings'}], stopReason: 'stop',
        api: 'test', provider: 'fixture', model: 'fixture', usage: {}});
      savedSession = structuredClone(reviewer.coherenceSavedSession);
      assert.equal(savedSession.reviewerContext, true);
      // Historical read-only identities have no resource-policy marker.
      delete savedSession.reviewerContext;
    } finally { reviewer.dispose(); }
    await assert.rejects(createWorkflowSession({...request, savedSession}, async () => ({})),
      /effective resources mismatch/);
    const repaired = await createWorkflowSession({...request, savedSession, reviewRepair: true}, async () => ({}));
    try {
      assert.equal(repaired.coherenceSavedSession.id, savedSession.id);
      assert.equal(repaired.getLastAssistantText(), 'warm review findings');
      assert.ok(!repaired.systemPrompt.includes(skillDescription));
      const continued = await createWorkflowSession({...request,
        savedSession: structuredClone(repaired.coherenceSavedSession)}, async () => ({}));
      try {
        assert.equal(continued.coherenceSavedSession.id, savedSession.id);
        assert.ok(!continued.systemPrompt.includes(skillDescription));
        assert.ok(continued.getActiveToolNames().includes('edit'));
      } finally { continued.dispose(); }
      assert.ok(repaired.getActiveToolNames().includes('edit'));
      assert.ok(repaired.getActiveToolNames().includes('bash'));
      assert.equal(repaired.coherenceSavedSession.compatibility.readOnly, false);
      await assert.rejects(createWorkflowSession({...request, savedSession: repaired.coherenceSavedSession,
        reviewRepair: true}, async () => ({})), /saved read-only reviewer/);
    } finally { repaired.dispose(); }
    for (const changed of [{readOnly: true}, {executor: {...executor, effort: 'low'}}, {reuseKey: 'other'}]) {
      await assert.rejects(createWorkflowSession({...request, savedSession, reviewRepair: true, ...changed},
        async () => ({})), /saved read-only reviewer|effective resources mismatch/);
    }
    const final = await createWorkflowSession({...request, readOnly: true}, async () => ({}));
    try {
      assert.notEqual(final.coherenceSavedSession.id, savedSession.id);
      assert.deepEqual([...final.getActiveToolNames()].sort(), ['find', 'grep', 'ls', 'read']);
    } finally { final.dispose(); }
  } finally { await fs.rm(project, {recursive: true, force: true}); }
});

test('provider-bound routine authority reaches the SDK prompt without sending a provider request', async () => {
  let received;
  const session = {
    messages: [{role: 'assistant', stopReason: 'stop'}],
    subscribe() { return () => {}; },
    async prompt(value) { received = value; },
    getLastAssistantText() { return 'offline'; },
  };
  const authority = 'Routine authority: isolated tests and local servers need no owner question.';
  assert.equal(await promptSession(session, authority, () => {}), 'offline');
  assert.equal(received, authority);
});

test('steering uses the installed SDK queue and matching user event, not queue insertion as consumption', {timeout: 15000}, async () => {
  const project = await fs.mkdtemp(path.join(os.tmpdir(), 'coherence-steering-sdk-'));
  const events = [];
  try {
    const provider = installSteeringProvider('question', project);
    let enter, release;
    const entered = new Promise(resolve => { enter = resolve; });
    const answer = new Promise(resolve => { release = resolve; });
    const session = await createWorkflowSession({project,
      executor: {provider: 'openai', model: 'gpt-4o-mini', effort: 'off'}}, async () => { enter(); return answer; });
    try {
      const sdkEvents = [];
      session.subscribe(event => sdkEvents.push(event));
      // The registered provider emits an actual ask_owner tool call. Only the
      // provider response is controlled; public steer and SDK events are real.
      const prompting = promptSession(session, 'offline steering', () => {});
      await entered;
      const target = {run_id: 'run', task_id: 'T009', invocation_id: 'invocation', role: 'task_worker'};
      const controller = steeringController({steering: target}, session, event => events.push(event));
      const control = {type: 'steer', request_id: 'direction-1', target: {...target,
        session_id: session.coherenceSavedSession.id}, instruction: '/do not execute'};
      await controller.steer(control);
      assert.deepEqual(events.filter(event => event.type === 'steer').map(event => event.status), ['accepted', 'queued']);
      await controller.steer(control); // same ID must not insert twice
      const second = {...control, request_id: 'direction-2'};
      await controller.steer(second);
      assert.equal(events.some(event => event.status === 'consumed'), false, 'pending owner reply remains a gate');
      release({answer: 'ordinary callback'});
      assert.equal(await prompting, 'steering complete');
      const directions = sdkEvents.filter(event => event.type === 'message_start' && event.message.role === 'user' && JSON.stringify(event.message.content).includes('owner-direction'));
      assert.equal(directions.length, 2, 'real SDK emits exactly one user message for each unique request ID');
      assert.ok(directions.every(event => JSON.stringify(event.message.content).includes('/do not execute')));
      const toolEnd = sdkEvents.findIndex(event => event.type === 'tool_execution_end');
      assert.ok(toolEnd >= 0 && sdkEvents.indexOf(directions[0]) > toolEnd, 'consumption follows the actual tool reply');
      assert.deepEqual([...new Set(events.filter(event => event.type === 'steer' && event.status === 'consumed')
        .map(event => event.request_id))].sort(), ['direction-1', 'direction-2'],
      'identical owner text with a new ID remains distinct');
      controller.close();
    } finally { session.dispose(); provider.mock.restore(); }
  } finally { await fs.rm(project, {recursive: true, force: true}); }
});

test('opted-in host dispatches a control while a correlated callback remains pending', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'coherence-steering-host-'));
  const host = fileURLToPath(new URL('../pi-host/host.mjs', import.meta.url));
  const preload = fileURLToPath(new URL('cleanup_adapter_fixture.mjs', import.meta.url));
  const child = spawn(process.execPath, [host], {cwd: root, stdio: ['pipe', 'pipe', 'pipe'], env: {
    ...process.env, COHERENCE_HOST_PRELOAD: '1', NODE_OPTIONS: `--import=${preload}`,
    PI_CODING_AGENT_DIR: path.join(root, 'private-agent'),
  }});
  const target = {run_id: 'run', task_id: 'T009', invocation_id: 'invocation', role: 'task_worker'};
  const records = [];
  const send = value => child.stdin.write(JSON.stringify(value) + '\n');
  try {
    send({project: root, executor: {provider: 'openai', model: 'gpt-4o-mini', effort: 'off'},
      prompt: 'fixture', steering: target});
    const lines = readline.createInterface({input: child.stdout});
    for await (const line of lines) {
      const record = JSON.parse(line);
      records.push(record);
      if (record.type === 'target') send({type: 'steer', request_id: 'direction', target: record.target, instruction: '/inert'});
      if (record.type === 'question') {
        assert.equal(record.request_id, 'callback-1');
        // The control was already handled; this reply can only resolve its callback.
        send({type: 'reply', request_id: record.request_id, reply: {answer: 'ordinary callback'}});
      }
      if (record.type === 'result') break;
    }
    assert.equal(records.at(-1).type, 'result');
    assert.deepEqual(records.filter(record => record.type === 'steer').map(record => record.status).slice(0, 2), ['accepted', 'queued']);
    if (child.exitCode === null) await new Promise((resolve, reject) => child.once('exit', code =>
      code === 0 ? resolve() : reject(new Error(`host exit ${code}`))));
    else assert.equal(child.exitCode, 0);
  } finally {
    child.stdin.end();
    if (child.exitCode === null) child.kill('SIGTERM');
    await fs.rm(root, {recursive: true, force: true});
  }
});

test('steering rejects mismatched or closed targets without retargeting', async () => {
  const subscriptions = [];
  const events = [];
  const session = {coherenceSavedSession: {id: 'session'}, subscribe(fn) {
    subscriptions.push(fn); return () => subscriptions.splice(subscriptions.indexOf(fn), 1);
  }, async steer() { throw new Error('must not steer another target'); }};
  const target = {run_id: 'run', task_id: 'T009', invocation_id: 'invocation', role: 'task_worker'};
  const controller = steeringController({steering: target}, session, event => events.push(event));
  await controller.steer({type: 'steer', request_id: 'wrong', instruction: 'hello', target: {...target, task_id: 'other', session_id: 'session'}});
  subscriptions[0]({type: 'agent_settled'});
  await controller.steer({type: 'steer', request_id: 'closed', instruction: 'hello', target: {...target, session_id: 'session'}});
  assert.deepEqual(events.filter(event => event.type === 'steer').map(event => event.status),
    ['failed-unavailable', 'failed-unavailable']);
  controller.close();
});

test('SDK compaction events continue to actual prompt completion without telemetry or deadline', async () => {
  let callback, removed = false;
  const events = [];
  const session = {
    messages: [{role: 'assistant', stopReason: 'stop'}],
    subscribe(fn) { callback = fn; return () => { removed = true; }; },
    async prompt() {
      callback({type: 'auto_compaction_start'});
      callback({type: 'auto_compaction_end'});
      callback({type: 'tool_execution_end', toolName: 'read', isError: true});
      callback({type: 'tool_execution_end', toolName: 'read', isError: false});
    },
    getLastAssistantText() { return 'continued'; },
  };
  assert.equal(await promptSession(session, 'fixture', e => events.push(e)), 'continued');
  assert.equal(events.length, 4);
  assert.equal(removed, true);
});

test('actual SDK read error is correctable, long read permits continuation, edit/write/bash work', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'coherence-simplification-03-sdk-tools-'));
  try {
    const read = createReadTool(root);
    await assert.rejects(() => read.execute('missing', {path: 'missing.txt'}));
    await createWriteTool(root).execute('write', {path: 'answer.txt', content: 'before\n'});
    const result = await read.execute('corrected', {path: 'answer.txt'});
    assert.match(result.content[0].text, /before/);
    await createEditTool(root).execute('edit', {path: 'answer.txt', edits: [{oldText: 'before', newText: 'after'}]});
    assert.equal(await fs.readFile(path.join(root, 'answer.txt'), 'utf8'), 'after\n');
    await createBashTool(root).execute('check', {command: 'test "$(cat answer.txt)" = after'});
    await fs.writeFile(path.join(root, 'long.txt'), Array.from({length: 5000}, (_, i) => `line-${i}`).join('\n'));
    const first = await read.execute('long', {path: 'long.txt'});
    assert.match(first.content[0].text, /offset|lines|truncat/i);
    const tail = await read.execute('continued', {path: 'long.txt', offset: 4999, limit: 2});
    assert.match(tail.content[0].text, /line-4999/);
  } finally { await fs.rm(root, {recursive: true, force: true}); }
});

test('actual SDK assistant error is an operation error, not successful prompt completion', async () => {
  const session = {
    subscribe() { return () => {}; }, async prompt() {},
    messages: [{role: 'assistant', stopReason: 'error', errorMessage: 'fixture provider error'}],
    getLastAssistantText() { return ''; },
  };
  await assert.rejects(() => promptSession(session, 'fixture', () => {}), /fixture provider error/);
});

test('SDK command cancellation drains its owned subprocess without cgroups', {timeout: 10000}, async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'coherence-simplification-03-cancel-'));
  const controller = new AbortController();
  try {
    const pending = createBashTool(root).execute('cancel', {command: 'echo $$ > tool.pid; exec sleep 1000'}, controller.signal);
    const pidPath = path.join(root, 'tool.pid');
    while (true) {
      try { await fs.access(pidPath); break; }
      catch { await new Promise(resolve => setTimeout(resolve, 10)); }
    }
    const pid = Number(await fs.readFile(pidPath, 'utf8'));
    controller.abort();
    await assert.rejects(() => pending, /abort/i);
    assert.throws(() => process.kill(pid, 0), {code: 'ESRCH'});
  } finally { await fs.rm(root, {recursive: true, force: true}); }
});

// Real SDK definitions/operations plus the real Python claim boundary, offline.
// Every filesystem/Git mutation is confined to this disposable fixture.
const repository = fileURLToPath(new URL('../../', import.meta.url));
async function mutationFixture(run) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'coherence-simplification-fix01-paths-'));
  const project = path.join(root, 'project');
  try {
    await fs.mkdir(project);
    await fs.writeFile(path.join(project, 'dirty file.txt'), 'base\n');
    await fs.writeFile(path.join(project, 'clean file.txt'), 'before\n');
    execFileSync('git', ['init', '-q', project]);
    execFileSync('git', ['-C', project, 'add', '--', '.']);
    execFileSync('git', ['-C', project, '-c', 'user.name=Fixture',
      '-c', 'user.email=fixture@example.invalid', '-c', 'commit.gpgsign=false',
      'commit', '-qm', 'fixture']);
    await fs.writeFile(path.join(project, 'dirty file.txt'), 'dirty work\n');
    await fs.writeFile(path.join(root, 'outside.txt'), 'outside work\n');
    await fs.symlink(root, path.join(project, 'escape'));
    const claims = [];
    const tools = limits => mutationTools(project, async request => {
      claims.push(request.path);
      const output = execFileSync(process.env.COHERENCE_PYTHON || path.join(repository, 'runtime/.venv/bin/python'),
        ['-B', '-c', `import json,sys
from coherence_workflow.git_effects import FocusedGit
from coherence_workflow.store import Blocked
project,name,limits = json.load(sys.stdin)
try:
    FocusedGit(project, {'owned_paths': limits} if limits is not None else {}).claim(name)
    print(json.dumps({'ok': True}))
except Blocked as error:
    print(json.dumps({'error': str(error)}))
`], {input: JSON.stringify([project, request.path, limits ?? null]),
          env: {...process.env, PYTHONDONTWRITEBYTECODE: '1', PYTHONPATH: path.join(repository, 'runtime')},
          encoding: 'utf8'});
      return JSON.parse(output);
    });
    await run({root, project, claims, tools});
  } finally { await fs.rm(root, {recursive: true, force: true}); }
}

for (const toolName of ['write', 'edit']) {
  const args = name => toolName === 'write' ? {path: name, content: 'after\n'} :
    {path: name, edits: [{oldText: 'before', newText: 'after'}]};
  test(`${toolName}: SDK effective aliases cannot mutate dirty/outside/symlink targets`, async () => {
    await mutationFixture(async ({root, project, claims, tools}) => {
      const tool = tools().find(tool => tool.name === toolName);
      // All spaces the actual SDK normalizes, plus @, URL and home aliases.
      const spaces = ['\u00a0', ...Array.from({length: 11}, (_, i) => String.fromCharCode(0x2000 + i)),
        '\u202f', '\u205f', '\u3000'];
      const dirtyAliases = ['@dirty file.txt', ...spaces.map(space => `dirty${space}file.txt`),
        pathToFileURL(path.join(project, 'dirty file.txt')).href,
        `~/${path.relative(os.homedir(), path.join(project, 'dirty file.txt'))}`];
      for (const alias of dirtyAliases) {
        // edit must reach its write operation to demonstrate denial before mutation.
        const input = toolName === 'edit' ?
          {path: alias, edits: [{oldText: 'dirty work', newText: 'after'}]} : args(alias);
        await assert.rejects(() => tool.execute('dirty', input), /pre-existing dirty path/);
        assert.equal(claims.at(-1), 'dirty file.txt', alias);
        assert.equal(await fs.readFile(path.join(project, 'dirty file.txt'), 'utf8'), 'dirty work\n');
      }
      const outside = path.join(root, 'outside.txt');
      const aliases = [outside, '@' + outside, pathToFileURL(outside).href,
        `~/${path.relative(os.homedir(), outside)}`, 'escape/outside.txt'];
      for (const alias of aliases) {
        const input = toolName === 'edit' ?
          {path: alias, edits: [{oldText: 'outside work', newText: 'after'}]} : args(alias);
        await assert.rejects(() => tool.execute('outside', input), /unsafe relative path|symlink path component/);
        assert.equal(await fs.readFile(outside, 'utf8'), 'outside work\n');
      }
      if (toolName === 'write') {
        for (const alias of [pathToFileURL(path.join(root, 'new-dir/file.txt')).href,
          `~/${path.relative(os.homedir(), path.join(root, 'new-dir/file.txt'))}`,
          '@escape/new-dir/file.txt']) {
          await assert.rejects(() => tool.execute('mkdir', args(alias)), /unsafe relative path|symlink path component/);
          await assert.rejects(() => fs.access(path.join(root, 'new-dir')), /ENOENT/);
        }
      }
    });
  });

  test(`${toolName}: clean aliases honor effective owned_paths; SDK errors remain correctable`, async () => {
    // Separate fixtures keep each successful alias clean at claim time.
    for (const aliasKind of ['at', 'unicode', 'url', 'home']) {
      await mutationFixture(async ({project, claims, tools}) => {
        const target = path.join(project, 'clean file.txt');
        const alias = {at: '@clean file.txt', unicode: 'clean\u202ffile.txt',
          url: pathToFileURL(target).href, home: `~/${path.relative(os.homedir(), target)}`}[aliasKind];
        const outOfScope = tools(['other.txt']).find(tool => tool.name === toolName);
        await assert.rejects(() => outOfScope.execute('scope', args(alias)), /outside optional owned_paths/);
        assert.equal(await fs.readFile(target, 'utf8'), 'before\n');
        const tool = tools(['clean file.txt']).find(tool => tool.name === toolName);
        if (toolName === 'edit') {
          await assert.rejects(() => tool.execute('bad-text', {path: alias,
            edits: [{oldText: 'absent text', newText: 'after'}]}), /Could not find/);
          await assert.rejects(() => tool.execute('missing', args('missing.txt')), /Could not edit file/);
        }
        await tool.execute('corrected', args(alias));
        assert.equal(claims.at(-1), 'clean file.txt');
        assert.equal(await fs.readFile(target, 'utf8'), 'after\n');
      });
    }
  });
}

test('write: claim precedes recursive mkdir, and clean new directories still work', async () => {
  await mutationFixture(async ({project, claims, tools}) => {
    const tool = tools(['nested']).find(tool => tool.name === 'write');
    await assert.rejects(() => tool.execute('scope', {path: '@forbidden/new/file.txt', content: 'no'}),
      /outside optional owned_paths/);
    await assert.rejects(() => fs.access(path.join(project, 'forbidden')), /ENOENT/);
    await tool.execute('allowed', {path: '@nested/new/file.txt', content: 'yes'});
    assert.equal(claims.at(-1), 'nested/new/file.txt');
    assert.equal(await fs.readFile(path.join(project, 'nested/new/file.txt'), 'utf8'), 'yes');
  });
});

test('write/edit: cancellation while awaiting claim cannot mutate afterward', async () => {
  await mutationFixture(async ({project}) => {
    for (const name of ['write', 'edit']) {
      const controller = new AbortController();
      const tool = mutationTools(project, async () => {
        controller.abort();
        return {ok: true};
      }).find(tool => tool.name === name);
      const args = name === 'write' ? {path: '@new-dir/file.txt', content: 'after'} :
        {path: '@clean file.txt', edits: [{oldText: 'before', newText: 'after'}]};
      await assert.rejects(() => tool.execute('cancel-claim', args, controller.signal), /Operation aborted/);
      await assert.rejects(() => fs.access(path.join(project, 'new-dir')), /ENOENT/);
      assert.equal(await fs.readFile(path.join(project, 'clean file.txt'), 'utf8'), 'before\n');
    }
  });
});
