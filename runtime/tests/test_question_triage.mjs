import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import bridge from '../../.pi/extensions/coordinate-implementation-bridge.js';

const repository = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');

test('parent triages a technical question and returns its own correlated diagnosis', {timeout: 15000}, async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'question-triage-'));
  const tools = new Map(), messages = [];
  const pi = {
    registerTool(tool) { tools.set(tool.name, tool); },
    getActiveTools() { return [...tools.keys()]; },
    on(event, handler) { if (event === 'session_shutdown') this.shutdown = handler; },
    sendMessage(message) { messages.push(message); },
  };
  try {
    await fs.mkdir(path.join(root, 'scripts'));
    await fs.writeFile(path.join(root, 'scripts/coordinate-implementation'), `#!/usr/bin/env python3
import sys
sys.path.insert(0, ${JSON.stringify(path.join(repository, 'runtime'))})
from coherence_workflow.pi_adapter import parent_question
assert parent_question('Provide the inspected technical diagnosis') == 'Inspected broken fixture pipe; repair its transport'
`, {mode: 0o700});
    bridge(pi);
    const ctx = {cwd: root, sessionManager: {getSessionId: () => 'triage-parent'}};
    const call = (name, args, context = ctx) => tools.get(name).execute(name, args, undefined, undefined, context);
    const until = async predicate => {
      const deadline = Date.now() + 10000;
      while (!predicate()) {
        assert.ok(Date.now() < deadline, 'expected bridge event did not arrive');
        await new Promise(resolve => setTimeout(resolve, 10));
      }
    };
    await call('coordinate_implementation_start', {run: 'triage-fixture', tasks: 'unused', executor: 'unused'});
    await until(() => messages.some(item => item.customType === 'coordinate_implementation_question'));
    const question = messages.find(item => item.customType === 'coordinate_implementation_question');
    assert.match(question.content, /Triage this as coordinator/);
    assert.match(question.content, /investigate and reply for routine authorized technical matters/);
    assert.match(question.content, /actual answer only for material product, scope, or permission decisions/);
    assert.doesNotMatch(question.content, /Ask the user, then/);
    assert.match(tools.get('coordinate_implementation_reply').description, /coordinator response/);
    const reply = {run: 'triage-fixture', request_id: question.details.request_id,
      answer: 'Inspected broken fixture pipe; repair its transport'};
    await assert.rejects(call('coordinate_implementation_reply', {...reply, request_id: 'wrong'}), /no matching pending/);
    await assert.rejects(call('coordinate_implementation_reply', {...reply, run: 'wrong'}), /no matching pending/);
    await assert.rejects(call('coordinate_implementation_reply', reply,
      {...ctx, sessionManager: {getSessionId: () => 'wrong'}}), /no matching pending/);
    await call('coordinate_implementation_reply', reply);
    await assert.rejects(call('coordinate_implementation_reply', reply), /no matching pending/);
    await until(() => messages.some(item => item.customType === 'coordinate_implementation_complete'));
    assert.match(messages.find(item => item.customType === 'coordinate_implementation_complete').content, /exit 0/);
  } finally {
    await pi.shutdown?.();
    await fs.rm(root, {recursive: true, force: true});
  }
});

test('parent routes an owner-only continuation through ask_user and rejects routine reply', {timeout: 15000}, async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'owner-question-'));
  const tools = new Map(), messages = [];
  const pi = {
    registerTool(tool) { tools.set(tool.name, tool); },
    getActiveTools() { return [...tools.keys(), 'ask_user']; },
    on(event, handler) { if (event === 'session_shutdown') this.shutdown = handler; },
    sendMessage(message, options) { messages.push({message, options}); },
  };
  try {
    await fs.mkdir(path.join(root, 'scripts'));
    await fs.writeFile(path.join(root, 'scripts/coordinate-implementation'), `#!/usr/bin/env python3
import sys
sys.path.insert(0, ${JSON.stringify(path.join(repository, 'runtime'))})
from coherence_workflow.pi_adapter import parent_question
context={'rejecting_execution':'review-2','review_base':'base','review_head':'head','scope':'original scope','effect':'one repair/review pair; no repeat'}
assert parent_question('Authorize the next pair?', owner_only=True, decision_context=context) == 'yes'
`, {mode: 0o700});
    bridge(pi);
    const ctx = {cwd: root, sessionManager: {getSessionId: () => 'owner-parent'}};
    const call = (name, args, context = ctx) => tools.get(name).execute(name, args, undefined, undefined, context);
    const until = async predicate => {
      const deadline = Date.now() + 10000;
      while (!predicate()) {
        assert.ok(Date.now() < deadline, 'expected owner-only bridge event did not arrive');
        await new Promise(resolve => setTimeout(resolve, 10));
      }
    };
    await call('coordinate_implementation_start', {run: 'owner-fixture', tasks: 'unused', executor: 'unused'});
    await until(() => messages.some(item => item.message.customType === 'coordinate_implementation_question'));
    const question = messages.find(item => item.message.customType === 'coordinate_implementation_question');
    assert.equal(question.options.triggerTurn, true);
    assert.equal(question.message.details.owner_only, true);
    assert.equal(question.message.details.decision_context.review_head, 'head');
    assert.match(question.message.content, /Call registered ask_user/);
    assert.match(question.message.content, /not routine coordinator triage/);
    assert.match(tools.get('coordinate_implementation_owner_reply').description, /actual answer returned by registered ask_user/);
    const reply = {run: 'owner-fixture', request_id: question.message.details.request_id, answer: 'yes'};
    await assert.rejects(call('coordinate_implementation_reply', reply), /owner-only decision requires/);
    await assert.rejects(call('coordinate_implementation_owner_reply', {...reply, request_id: 'wrong'}), /no matching pending owner-only/);
    await assert.rejects(call('coordinate_implementation_owner_reply', {...reply, answer: ' '}), /nonempty actual owner answer/);
    await call('coordinate_implementation_owner_reply', reply);
    await assert.rejects(call('coordinate_implementation_owner_reply', reply), /no matching pending owner-only/);
    await until(() => messages.some(item => item.message.customType === 'coordinate_implementation_complete'));
    assert.match(messages.find(item => item.message.customType === 'coordinate_implementation_complete').message.content, /exit 0/);
  } finally {
    await pi.shutdown?.();
    await fs.rm(root, {recursive: true, force: true});
  }
});

test('owner-only continuation stops when ask_user is unavailable', {timeout: 15000}, async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'owner-question-unavailable-'));
  const tools = new Map(), messages = [];
  const pi = {registerTool(tool) { tools.set(tool.name, tool); }, getActiveTools() { return [...tools.keys()]; },
    on(event, handler) { if (event === 'session_shutdown') this.shutdown = handler; }, sendMessage(message) { messages.push(message); }};
  try {
    await fs.mkdir(path.join(root, 'scripts'));
    await fs.writeFile(path.join(root, 'scripts/coordinate-implementation'), `#!/usr/bin/env python3
import sys
sys.path.insert(0, ${JSON.stringify(path.join(repository, 'runtime'))})
from coherence_workflow.pi_adapter import parent_question
parent_question('Authorize?', owner_only=True, decision_context={'rejecting_execution':'r','review_base':'b','review_head':'h','scope':'s','effect':'one pair; no repeat'})
`, {mode: 0o700});
    bridge(pi);
    await tools.get('coordinate_implementation_start').execute('start', {run: 'unavailable', tasks: 'unused', executor: 'unused'}, undefined, undefined,
      {cwd: root, sessionManager: {getSessionId: () => 'parent'}});
    const deadline = Date.now() + 10000;
    while (!messages.some(item => item.customType === 'coordinate_implementation_complete')) {
      assert.ok(Date.now() < deadline, 'owner-only unavailable run did not finish');
      await new Promise(resolve => setTimeout(resolve, 10));
    }
    assert.match(messages.find(item => item.customType === 'coordinate_implementation_complete').content, /exit 1|exit 2/);
    assert.equal(messages.some(item => item.customType === 'coordinate_implementation_question'), false);
  } finally {
    await pi.shutdown?.();
    await fs.rm(root, {recursive: true, force: true});
  }
});
