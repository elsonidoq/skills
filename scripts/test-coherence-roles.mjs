// Offline integration with the installed pi-subagents discovery and event API; no model call.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';

const root = process.env.PI_SUBAGENTS_ROOT;
if (!root) throw new Error('Set PI_SUBAGENTS_ROOT to the installed pi-subagents package directory');
const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'coherence-roles-'));
try {
  const project = path.join(temp, 'project');
  fs.mkdirSync(project);
  const helper = path.resolve('scripts/activate-coherence-roles.py');
  execFileSync('python3', [helper, project]);
  execFileSync('python3', [helper, project]);
  const link = path.join(project, '.pi/extensions/coherence-roles.js');
  assert(fs.lstatSync(link).isSymbolicLink());
  fs.unlinkSync(link); fs.writeFileSync(link, 'foreign');
  assert.throws(() => execFileSync('python3', [helper, project], {stdio: 'pipe'}));
  assert.equal(fs.readFileSync(link, 'utf8'), 'foreign');
  fs.unlinkSync(link); execFileSync('python3', [helper, project]);
  const agentDir = path.join(temp, 'agent');
  fs.mkdirSync(path.join(agentDir, 'agents'), {recursive: true});
  fs.writeFileSync(path.join(agentDir, 'agents/reviewer.md'), '---\nname: reviewer\ndescription: foreign reviewer\n---\nFOREIGN GLOBAL PROMPT\n');
  process.env.PI_CODING_AGENT_DIR = agentDir;
  process.env.HOME = temp;
  fs.writeFileSync(path.join(project, '.pi/settings.json'), JSON.stringify({subagents: {agentOverrides: {'coherence-reviewer': {systemPrompt: 'OVERRIDE PROMPT', tools: ['write'], model: 'test/model', thinking: 'high'}}}}));
  const {discoverAgents} = await import(pathToFileURL(path.join(root, 'src/agents/agents.js')));
  const {mergeRuntimeAgents} = await import(pathToFileURL(path.join(root, 'src/agents/runtime-agent-registry.js')));
  const {registerRuntimeAgentEventListener} = await import(pathToFileURL(path.join(root, 'src/agents/runtime-agent-events.js')));
  const handlers = new Map(), listeners = new Map();
  const pi = {on: (name, fn) => handlers.set(name, fn), registerTool() {}, events: {
    on(name, fn) { listeners.set(name, fn); return () => listeners.delete(name); },
    emit(name, value) { listeners.get(name)?.(value); },
  }};
  registerRuntimeAgentEventListener(pi);
  const source = fs.readFileSync(link, 'utf8');
  const {default: extension} = await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'));
  extension(pi); await handlers.get('session_start')();
  const discovered = discoverAgents(project, 'both');
  const merged = mergeRuntimeAgents(pi, discovered, discovered.agents, {cwd: project, scope: 'both'});
  const reviewer = merged.agents.find(a => a.name === 'coherence-reviewer');
  assert.equal(reviewer.source, 'runtime');
  assert(reviewer.systemPrompt.includes('Derived obligations remain reviewable'));
  assert(!reviewer.systemPrompt.includes('FOREIGN GLOBAL PROMPT'));
  assert(!reviewer.systemPrompt.includes('OVERRIDE PROMPT'));
  assert(!reviewer.tools.includes('write'));
  assert.equal(reviewer.model, 'test/model');
  assert.equal(reviewer.thinking, 'high');
  assert(merged.agents.find(a => a.name === 'reviewer').systemPrompt.includes('FOREIGN GLOBAL PROMPT'));
  assert.throws(() => mergeRuntimeAgents(pi, discovered, [...discovered.agents, {name: 'coherence-reviewer'}]), /collides/);
  await handlers.get('session_shutdown')();
  assert(!mergeRuntimeAgents(pi, discovered).agents.some(a => a.name === 'coherence-reviewer'));
  listeners.clear();
  await assert.rejects(handlers.get('session_start')(), /runtime agent registration unavailable/);
  console.log('PASS: real event registration/discovery; runtime prompt and tools resist overrides, model/effort retained; collision and activation preservation');
} finally { fs.rmSync(temp, {recursive: true, force: true}); }
