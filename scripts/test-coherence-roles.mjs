// Offline integration with installed pi-subagents file discovery; no model calls.
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

  // Exercise the real install.sh role-link block in an isolated home/suite.
  const suite = path.join(temp, 'suite');
  for (const dir of ['scripts', 'roles', 'skills', 'docs']) fs.mkdirSync(path.join(suite, dir), {recursive: true});
  for (const script of ['install.sh', 'install-links.py']) fs.copyFileSync(path.resolve('scripts', script), path.join(suite, 'scripts', script));
  fs.writeFileSync(path.join(suite, 'docs/best_practices_spec_driven_development.md'), 'fixture');
  fs.writeFileSync(path.join(suite, 'scripts/check-skills-lint.sh'), '#!/bin/sh\nexit 0\n', {mode: 0o755});
  for (const name of ['coherence-producer', 'coherence-reviewer']) fs.copyFileSync(path.resolve('roles', `${name}.md`), path.join(suite, 'roles', `${name}.md`));
  const bin = path.join(temp, 'bin');
  fs.mkdirSync(bin);
  fs.writeFileSync(path.join(bin, 'pi'), '#!/bin/sh\nprintf "pi-subagents pi-ask-user\\n"\n', {mode: 0o755});
  const home = path.join(temp, 'install-home');
  fs.mkdirSync(home);
  const env = {...process.env, HOME: home, PI_CODING_AGENT_DIR: path.join(home, '.pi/agent'), PATH: `${bin}:${process.env.PATH}`};
  const install = () => execFileSync('bash', [path.join(suite, 'scripts/install.sh')], {env, stdio: 'pipe'});
  install(); install();
  for (const name of ['coherence-producer', 'coherence-reviewer']) assert.equal(fs.readlinkSync(path.join(home, '.agents', `${name}.md`)), path.join(suite, 'roles', `${name}.md`));
  const conflict = path.join(home, '.agents/coherence-reviewer.md');
  fs.unlinkSync(conflict);
  fs.writeFileSync(conflict, 'foreign');
  assert.throws(install);
  assert.equal(fs.readFileSync(conflict, 'utf8'), 'foreign');
  fs.unlinkSync(conflict); fs.symlinkSync(path.join(temp, 'absent'), conflict);
  assert.throws(install);
  assert.equal(fs.readlinkSync(conflict), path.join(temp, 'absent'));

  const agentDir = path.join(temp, 'agent');
  const userAgents = path.join(temp, '.agents');
  fs.mkdirSync(agentDir);
  fs.mkdirSync(userAgents);
  for (const name of ['coherence-producer', 'coherence-reviewer']) {
    fs.symlinkSync(path.resolve('roles', `${name}.md`), path.join(userAgents, `${name}.md`));
  }
  fs.writeFileSync(path.join(userAgents, 'reviewer.md'), '---\nname: reviewer\ndescription: foreign reviewer\n---\nFOREIGN GLOBAL PROMPT\n');
  process.env.PI_CODING_AGENT_DIR = agentDir;
  process.env.HOME = temp;
  const {discoverAgents} = await import(pathToFileURL(path.join(root, 'src/agents/agents.js')));
  const discovered = discoverAgents(project, 'both');
  const producer = discovered.agents.find(a => a.name === 'coherence-producer');
  assert(producer, 'producer must be discovered without runtime registration');
  assert.equal(producer.source, 'user');
  assert(producer.systemPrompt.includes('After successfully writing the report to the runtime-bound output file'));
  assert(producer.systemPrompt.includes('Report written to the bound output path.'));
  assert.equal(producer.defaultContext, 'fresh');
  assert.equal(producer.acceptanceRole, 'writer');
  assert.equal(producer.inheritSkills, true);
  assert(producer.tools.includes('write'));
  const reviewer = discovered.agents.find(a => a.name === 'coherence-reviewer');
  assert(reviewer, 'reviewer must be discovered without runtime registration');
  assert.equal(reviewer.source, 'user');
  assert(reviewer.systemPrompt.includes('Derived obligations remain reviewable'));
  assert(!reviewer.systemPrompt.includes('FOREIGN GLOBAL PROMPT'));
  assert.equal(reviewer.defaultContext, 'fresh');
  assert.equal(reviewer.acceptanceRole, 'read-only');
  assert.equal(reviewer.inheritSkills, false);
  assert(!reviewer.tools.includes('write'));
  assert(discovered.agents.find(a => a.name === 'reviewer').systemPrompt.includes('FOREIGN GLOBAL PROMPT'));

  // Previously activated projects must not add colliding runtime registrations.
  const source = fs.readFileSync(link, 'utf8');
  const {default: extension} = await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'));
  extension({on() { throw new Error('legacy extension must not register session handlers'); }, events: {emit() { throw new Error('legacy extension must not register runtime roles'); }}});
  assert(!fs.existsSync(path.join(project, '.pi/agents')), 'no project-specific role installation required');
  console.log('PASS: installer repeat/conflict preservation; fresh-process file discovery for both roles; preserved prompts, permissions and foreign reviewer; legacy activation cannot register duplicates');
} finally { fs.rmSync(temp, {recursive: true, force: true}); }
