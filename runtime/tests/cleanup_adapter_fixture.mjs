// Zero-send actual host/SDK tool fixture, consumed by Python transport tests.
import assert from 'node:assert/strict';
import readline from 'node:readline';
import {mock} from 'node:test';
import {piSdk} from '../pi-host/host.mjs';
const {AgentSession} = piSdk;

// When loaded with NODE_OPTIONS this patches only the local SDK provider seam;
// the child still executes the production host stdin dispatcher.
if (process.env.COHERENCE_HOST_PRELOAD === '1') {
  mock.method(AgentSession.prototype, 'prompt', async function () {
    const tool = this.getToolDefinition('ask_owner');
    assert.ok(this.getActiveToolNames().includes('ask_owner'));
    await tool.execute('legacy-question', {question: 'fixture callback'});
  });
  mock.method(AgentSession.prototype, 'getLastAssistantText', () => 'legacy complete');
} else {
  const {execute} = await import('../pi-host/host.mjs');
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
}
