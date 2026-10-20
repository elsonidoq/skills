// Offline SDK/tool behavior; not a mocked live-provider success claim.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { test } from 'node:test';
import { createReadTool, createEditTool, createWriteTool, createBashTool } from '../pi-host/node_modules/@earendil-works/pi-coding-agent/dist/index.js';
import { promptSession } from '../pi-host/host.mjs';

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
