// Controlled local provider seam for Python adapter multiplexing tests.
import assert from 'node:assert/strict';
import {mock} from 'node:test';
import {AgentSession} from '../../pi-host/node_modules/@earendil-works/pi-coding-agent/dist/index.js';

if (process.env.COHERENCE_HOST_PRELOAD === '1') {
  mock.method(AgentSession.prototype, 'prompt', async function () {
    // Use the installed SDK's normal steering entry point. The seam delays its
    // user event until the active owner-tool callback has its own reply.
    this._isAgentRunActive = true;
    let queued;
    this.agent.steer = message => { queued = message; return Promise.resolve(); };
    const tool = this.getToolDefinition('ask_owner');
    assert.ok(this.getActiveToolNames().includes('ask_owner'));
    await tool.execute('correlated-question', {question: 'fixture callback'});
    assert.ok(queued, 'the direction queued while the callback was pending');
    // _handleAgentEvent emits message_start synchronously before its later
    // dispatcher work; do not make this fixture's synthetic prompt await an
    // unrelated agent loop.
    this._handleAgentEvent({type: 'message_start', message: queued});
    this._isAgentRunActive = false;
  });
  mock.method(AgentSession.prototype, 'getLastAssistantText', () => 'steering complete');
}
