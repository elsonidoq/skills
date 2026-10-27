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
assert parent_question('After the inspected fixture repair/checkpoint, provide the later routine technical diagnosis') == 'Inspected broken fixture pipe; repair its transport'
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
    assert.match(question.content, /After the inspected fixture repair\/checkpoint/);
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

test('production engine consumes a bridge owner answer once per additional pair', {timeout: 15000}, async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'owner-engine-'));
  const tools = new Map(), messages = [], ownerQuestions = [];
  const pi = {
    registerTool(tool) { tools.set(tool.name, tool); },
    getActiveTools() { return [...tools.keys()]; },
    on(event, handler) { if (event === 'session_shutdown') this.shutdown = handler; },
    sendMessage(message, options) { messages.push({message, options}); },
  };
  // Offline owner-tool answer fixture, not a live human participation claim.
  tools.set('ask_user', {async execute(context) { ownerQuestions.push(context); return 'yes'; }});
  try {
    await fs.mkdir(path.join(root, 'scripts'));
    await fs.writeFile(path.join(root, 'scripts/coordinate-implementation'), `#!/usr/bin/env python3
import json, pathlib, sys
sys.path.insert(0, ${JSON.stringify(path.join(repository, 'runtime'))})
from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.store import Authority, git
from coherence_workflow.pi_adapter import parent_question
project=pathlib.Path.cwd()
git(project, 'init', '-q')
git(project, 'config', 'user.name', 'Fixture')
git(project, 'config', 'user.email', 'fixture@invalid')
(project/'.gitignore').write_text('.coherence/\\n')
(project/'owned.txt').write_text('baseline\\n')
git(project, 'add', '--', '.gitignore', 'owned.txt')
git(project, 'commit', '-qm', 'baseline')
base=git(project, 'rev-parse', 'HEAD').decode().strip()
class Adapter:
    reviews=0
    fixes=0
    def __init__(self, *args, **kwargs): pass
    def prompt(self, prompt, **kwargs):
        if kwargs.get('read_only'):
            Adapter.reviews+=1
            return json.dumps({'approved':Adapter.reviews==4, 'coverage':['fixture examined'], 'coverage_gaps':[], 'findings':[] if Adapter.reviews==4 else ['owned.txt:1 - missing input crashes requests']})
        if 'Actionable findings:' in prompt:
            Adapter.fixes+=1
        return 'offline fixture'
executor={'provider':'fixture','model':'offline','effort':'medium','reviewer':{'provider':'fixture','model':'offline-review','effort':'medium'}}
with Authority(project) as owner:
    result=Engine(owner, 'composed-owner', admit([{'id':'task','description':'offline fixture'}]), executor,
                  adapter=Adapter, question=parent_question).invoke()
    assert result['status']=='complete'
    assert (Adapter.reviews, Adapter.fixes)==(4,3)
    grants=[json.loads(row['details']) for row in owner.store.db.execute("SELECT details FROM execution_history WHERE kind='review_pair_grant' ORDER BY seq")]
    reservations=[json.loads(row['details']) for row in owner.store.db.execute("SELECT details FROM execution_history WHERE kind='review_pair_reservation' AND state='fixer_reserved' ORDER BY seq")]
    assert len(grants)==len(reservations)==2
    assert len({item['rejecting_execution_id'] for item in grants})==2
    assert [item['grant_id'] for item in grants]==[item['grant_id'] for item in reservations]
    assert all(item['review_base']==base for item in grants)
    assert all(item['references']['base']==base for item in owner.store.review_chain('composed-owner')['executions'])
`, {mode: 0o700});
    bridge(pi);
    const ctx = {cwd: root, sessionManager: {getSessionId: () => 'engine-parent'}};
    const call = (name, args) => tools.get(name).execute(name, args, undefined, undefined, ctx);
    const until = async predicate => {
      const deadline = Date.now() + 10000;
      while (!predicate()) {
        assert.ok(Date.now() < deadline, 'expected composed owner event did not arrive');
        await new Promise(resolve => setTimeout(resolve, 10));
      }
    };
    await call('coordinate_implementation_start', {run: 'composed-owner', tasks: 'unused', executor: 'unused'});
    for (let ordinal = 0; ordinal < 2; ordinal++) {
      await until(() => messages.filter(item => item.message.customType === 'coordinate_implementation_question').length > ordinal);
      const question = messages.filter(item => item.message.customType === 'coordinate_implementation_question')[ordinal];
      assert.equal(question.message.details.owner_only, true);
      assert.equal(question.options.triggerTurn, true);
      assert.match(question.message.details.decision_context.effect, /exactly one.*no repeat/i);
      const reply = {run: 'composed-owner', request_id: question.message.details.request_id, answer: 'yes'};
      await assert.rejects(call('coordinate_implementation_reply', reply), /owner-only decision requires/);
      const answer = await tools.get('ask_user').execute(question.message.details.decision_context);
      await call('coordinate_implementation_owner_reply', {...reply, answer});
    }
    await until(() => messages.some(item => item.message.customType === 'coordinate_implementation_complete'));
    assert.match(messages.find(item => item.message.customType === 'coordinate_implementation_complete').message.content, /exit 0/);
    assert.equal(ownerQuestions.length, 2);
    assert.notEqual(ownerQuestions[0].rejecting_execution, ownerQuestions[1].rejecting_execution);
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
