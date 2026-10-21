// Zero-send actual host/SDK tool fixture, consumed by the Python adapter test.
import assert from 'node:assert/strict';
import readline from 'node:readline';
import {mock} from 'node:test';
import {AgentSession} from '../pi-host/node_modules/@earendil-works/pi-coding-agent/dist/index.js';
import {execute} from '../pi-host/host.mjs';
const lines = readline.createInterface({input: process.stdin});
const iterator = lines[Symbol.asyncIterator]();
const receive = async () => JSON.parse((await iterator.next()).value);
const emit = value => console.log(JSON.stringify(value));
mock.method(AgentSession.prototype, 'prompt', async function () {
  const tool = this.getToolDefinition('cleanup_artifact');
  assert.ok(this.getActiveToolNames().includes('cleanup_artifact'));
  await assert.rejects(() => tool.execute('unknown', {path: 'web/dist/sentinel.js'}), /unsafe generated-artifact/);
  await tool.execute('known', {path: 'web/dist/known.js'});
});
mock.method(AgentSession.prototype, 'getLastAssistantText', () => 'cleaned');
try {
  const request = await receive();
  const result = await execute(request, emit, async value => { emit(value); return receive(); });
  emit({type: 'result', ...result});
} finally { lines.close(); }
