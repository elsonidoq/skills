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
