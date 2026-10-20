// Offline SDK/tool behavior; not a mocked live-provider success claim.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { test } from 'node:test';
import { createReadTool, createEditTool, createWriteTool, createBashTool } from '../pi-host/node_modules/@earendil-works/pi-coding-agent/dist/index.js';
import { createWorkflowSession, mutationTools, promptSession } from '../pi-host/host.mjs';

test('actual SDK worker exposes ask_owner while independent reviewer remains read-only', async () => {
  const project = await fs.mkdtemp(path.join(os.tmpdir(), 'coherence-owner-tools-'));
  try {
    // Resolve local model metadata only: no prompt, provider request or authentication refresh.
    const executor = {provider: 'openai', model: 'gpt-4o-mini', effort: 'medium'};
    for (const readOnly of [false, true]) {
      const session = await createWorkflowSession({project, executor, readOnly}, async () => ({answer: 'fixture'}));
      try {
        const tools = session.getActiveToolNames();
        if (readOnly) assert.deepEqual([...tools].sort(), ['find', 'grep', 'ls', 'read']);
        else assert.ok(tools.includes('ask_owner'), 'registered ask_owner must also be active for workers');
      } finally { session.dispose(); }
    }
  } finally { await fs.rm(project, {recursive: true, force: true}); }
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

test('SDK command cancellation handles its own subprocess without cgroups', {timeout: 10000}, async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'coherence-simplification-03-cancel-'));
  const controller = new AbortController();
  try {
    const pending = createBashTool(root).execute('cancel', {command: 'echo ready > started; sleep 1000'}, controller.signal);
    while (true) {
      try { await fs.access(path.join(root, 'started')); break; }
      catch { await new Promise(resolve => setTimeout(resolve, 10)); }
    }
    controller.abort();
    await assert.rejects(() => pending, /abort/i);
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
      const output = execFileSync(path.join(repository, '.pi/workflow-validation/venv/bin/python'),
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
