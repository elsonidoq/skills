// T008: official persisted sessions and SDK-idle/compaction observations, offline.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {test} from 'node:test';
import {SessionManager} from '../pi-host/node_modules/@earendil-works/pi-coding-agent/dist/index.js';
import {promptSession, sessionObservationRecord} from '../pi-host/host.mjs';

test('official SessionManager create/open retains a private identity without ambient discovery', async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'coherence-saved-session-'));
  try {
    const sessions = path.join(root, 'private-sessions');
    const created = SessionManager.create(root, sessions);
    // Persistence begins with an actual assistant turn, as it does after host
    // prompt completion; state-only custom entries intentionally stay transient.
    created.appendMessage({role: 'assistant', content: [], stopReason: 'stop',
      api: 'test', provider: 'fixture', model: 'fixture', usage: {}});
    const id = created.getSessionId();
    const file = created.getSessionFile();
    assert.ok(file);
    const reopened = SessionManager.open(file, sessions, root);
    assert.equal(reopened.getSessionId(), id);
    assert.equal(reopened.getEntries().at(-1).type, 'message');
    assert.equal(SessionManager.findById(root, id, sessions), file);
  } finally {
    await fs.rm(root, {recursive: true, force: true});
  }
});

test('new host omits standalone session observations unless the adapter opts in', () => {
  const session = {
    coherenceSavedSession: {id: 'session-1', file: '/private/session-1.jsonl'},
    coherenceEpoch: 'opened',
    sessionId: 'session-1',
    getContextUsage() { return {tokens: 1, contextWindow: 2}; },
    getSessionStats() { return {tokens: {input: 1}}; },
    _coherenceSessionManager: {getLeafId() { return 'entry-1'; }},
  };
  assert.equal(sessionObservationRecord({}, session), null);
  assert.deepEqual(sessionObservationRecord({sessionObservations: true}, session), {
    type: 'session', session: session.coherenceSavedSession,
    before: {session_id: 'session-1', branch: 'session-1', epoch: 'opened', entry: 'entry-1',
      counters: {input: 1}, costs: {estimated_usd: null}, compaction_entries: [],
      context_tokens: 1, context_window: 2},
  });
});

test('persisted compaction entries expose unique IDs and available summary overhead', () => {
  const session = {
    coherenceSavedSession: {id: 'session-1', file: '/private/session-1.jsonl'}, coherenceEpoch: 'opened',
    sessionId: 'session-1', getContextUsage() { return {}; },
    getSessionStats() { return {tokens: {}, cost: 0.25}; },
    _coherenceSessionManager: {getLeafId() { return 'entry-2'; }, getEntries() {
      return [{type: 'compaction', id: 'compact-1', usage: {input: 3}},
        {type: 'compaction', id: 'compact-1', usage: {input: 3}},
        {type: 'message', id: 'message-1'}];
    }},
  };
  assert.deepEqual(sessionObservationRecord({sessionObservations: true}, session).before.compaction_entries,
    [{id: 'compact-1', summary_usage: {input: 3}}]);
  assert.equal(sessionObservationRecord({sessionObservations: true}, session).before.costs.estimated_usd, 0.25);
});

test('prompt waits for SDK idle and reports actual compaction event names', async () => {
  let idle = false;
  let listener;
  const events = [];
  const session = {
    messages: [{role: 'assistant', stopReason: 'stop'}],
    subscribe(fn) { listener = fn; return () => {}; },
    async prompt() { listener({type: 'compaction_start'}); listener({type: 'compaction_end'}); },
    async waitForIdle() { idle = true; },
    getLastAssistantText() { return 'done'; },
  };
  assert.equal(await promptSession(session, 'dummy work', event => events.push(event)), 'done');
  assert.equal(idle, true);
  assert.deepEqual(events.map(event => event.event), ['compaction_start', 'compaction_end']);
});
