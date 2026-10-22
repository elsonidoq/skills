import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath} from 'node:url';
import bridge from '../../.pi/extensions/coordinate-implementation-bridge.js';
import {DefaultResourceLoader, SettingsManager} from '../pi-host/node_modules/@earendil-works/pi-coding-agent/dist/index.js';

const repository = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const source = path.join(repository, '.pi/extensions/coordinate-implementation-bridge.js');

test('global and checkout links load the bridge only once', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'global-bridge-discovery-'));
  try {
    const agent = path.join(root, 'agent'), cwd = path.join(root, 'project');
    for (const dir of [path.join(agent, 'extensions'), path.join(cwd, '.pi/extensions')]) {
      await fs.mkdir(dir, {recursive: true});
      await fs.symlink(source, path.join(dir, 'coordinate-implementation-bridge.js'));
    }
    const loader = new DefaultResourceLoader({cwd, agentDir: agent,
      settingsManager: SettingsManager.inMemory({defaultProjectTrust: 'always'}),
      noSkills: true, noPromptTemplates: true, noThemes: true, noContextFiles: true});
    await loader.reload();
    const loaded = loader.getExtensions();
    assert.deepEqual(loaded.errors, []);
    assert.equal(loaded.extensions.filter(item => item.tools.has('coordinate_implementation_start')).length, 1);
  } finally { await fs.rm(root, {recursive: true, force: true}); }
});

for (const resume of [false, true]) test(`shared runner on PATH keeps target cwd and ${resume ? 'resume' : 'start'} inputs`, async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'global-bridge-runner-'));
  const originalPath = process.env.PATH;
  const tools = new Map(), messages = [];
  const pi = {registerTool(tool) {tools.set(tool.name, tool);},
    getActiveTools() {return [...tools.keys()];},
    on(event, handler) {if (event === 'session_shutdown') this.shutdown = handler;},
    sendMessage(message) {messages.push(message);}};
  try {
    const bin = path.join(root, 'bin'), cwd = path.join(root, 'project');
    await fs.mkdir(bin); await fs.mkdir(cwd);
    await fs.writeFile(path.join(bin, 'coordinate-implementation'), '#!/bin/sh\npwd > smoke-cwd\nprintf "%s\\n" "$@" > smoke-args\n', {mode: 0o700});
    process.env.PATH = bin + path.delimiter + originalPath;
    bridge(pi);
    const params = resume ? {run: 'global-smoke', resume: true} : {run: 'global-smoke', tasks: '/tmp/tasks.json', executor: '/tmp/executor.json'};
    await tools.get('coordinate_implementation_start').execute('smoke', params, undefined, undefined,
      {cwd, sessionManager: {getSessionId: () => 'global-parent'}});
    const deadline = Date.now() + 10000;
    while (!messages.some(item => item.customType === 'coordinate_implementation_complete')) {
      assert.ok(Date.now() < deadline, 'runner did not complete');
      await new Promise(resolve => setTimeout(resolve, 10));
    }
    assert.match(messages.at(-1).content, /exit 0/);
    assert.equal((await fs.readFile(path.join(cwd, 'smoke-cwd'), 'utf8')).trim(), cwd);
    assert.deepEqual((await fs.readFile(path.join(cwd, 'smoke-args'), 'utf8')).trim().split('\n'),
      resume ? ['resume', '--project', cwd, '--run', 'global-smoke'] :
        ['start', '--project', cwd, '--tasks', params.tasks, '--executor', params.executor, '--run', 'global-smoke']);
  } finally {
    process.env.PATH = originalPath;
    await pi.shutdown?.();
    await fs.rm(root, {recursive: true, force: true});
  }
});
