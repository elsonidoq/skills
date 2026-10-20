// Parent-session bridge for the existing coordinate-implementation runner.
import { createServer } from 'node:net';
import { mkdtemp, chmod, rm } from 'node:fs/promises';
import { randomBytes } from 'node:crypto';
import { spawn } from 'node:child_process';
import { tmpdir } from 'node:os';
import path from 'node:path';

const startParameters = {
  type: 'object', additionalProperties: false,
  properties: {
    tasks: {type: 'string'}, executor: {type: 'string'}, run: {type: 'string'},
  }, required: ['tasks', 'executor', 'run'],
};
const replyParameters = {
  type: 'object', additionalProperties: false,
  properties: {
    request_id: {type: 'string'}, run: {type: 'string'}, answer: {type: 'string'},
  }, required: ['request_id', 'run', 'answer'],
};

function textResult(text, details = undefined) {
  return {content: [{type: 'text', text}], details};
}

export default function coordinateImplementationBridge(pi) {
  let active;

  const close = async () => {
    if (!active) return;
    const bridge = active;
    active = undefined;
    bridge.server.close();
    for (const socket of bridge.sockets) socket.destroy();
    await rm(bridge.directory, {recursive: true, force: true});
  };

  const send = (socket, value) => {
    if (!socket.destroyed) socket.end(JSON.stringify(value) + '\n');
  };

  const receive = (bridge, socket, line) => {
    let request;
    try { request = JSON.parse(line); } catch { send(socket, {error: 'invalid bridge request'}); return; }
    if (!request || request.type !== 'question' || request.token !== bridge.token ||
        request.session_id !== bridge.session || request.run_id !== bridge.run ||
        typeof request.request_id !== 'string' || !request.request_id ||
        typeof request.question !== 'string') {
      send(socket, {request_id: request?.request_id, error: 'bridge request does not target this parent session and run'});
      return;
    }
    if (bridge.pending) {
      send(socket, {request_id: request.request_id, error: 'parent owner bridge already has a pending question'});
      return;
    }
    bridge.pending = {request_id: request.request_id, socket};
    pi.sendMessage({
      customType: 'coordinate_implementation_question', display: true,
      content: `Coordinate implementation needs an owner answer. Ask the user, then call coordinate_implementation_reply with request_id ${request.request_id} and run ${bridge.run}.`,
      details: {request_id: request.request_id, run: bridge.run},
    }, {triggerTurn: true, deliverAs: 'followUp'});
  };

  pi.registerTool({
    name: 'coordinate_implementation_start', label: 'Start coordinate implementation',
    description: 'Launch the approved coordinate-implementation runner through this parent session.',
    parameters: startParameters, executionMode: 'sequential',
    async execute(_id, params, _signal, _update, ctx) {
      if (active) throw new Error('coordinate implementation bridge already has an active run');
      const directory = await mkdtemp(path.join(tmpdir(), 'coordinate-implementation-'));
      await chmod(directory, 0o700);
      const endpoint = path.join(directory, 'bridge.sock');
      const session = ctx.sessionManager.getSessionId();
      const token = randomBytes(32).toString('hex');
      const sockets = new Set();
      const bridge = {directory, endpoint, session, token, run: params.run, sockets, pending: undefined, server: undefined};
      const server = createServer(socket => {
        sockets.add(socket);
        let data = '';
        let handled = false;
        socket.setEncoding('utf8');
        socket.on('data', chunk => {
          data += chunk;
          const end = data.indexOf('\n');
          if (!handled && end >= 0) {
            handled = true;
            receive(bridge, socket, data.slice(0, end));
          }
        });
        socket.on('close', () => {
          sockets.delete(socket);
          if (bridge.pending?.socket === socket) bridge.pending = undefined;
        });
        socket.on('error', () => {});
      });
      bridge.server = server;
      await new Promise((resolve, reject) => server.once('error', reject).listen(endpoint, resolve));
      await chmod(endpoint, 0o600);
      active = bridge;
      const child = spawn(path.join(ctx.cwd, 'scripts/coordinate-implementation'), [
        'start', '--project', ctx.cwd, '--tasks', params.tasks, '--executor', params.executor, '--run', params.run,
      ], {cwd: ctx.cwd, stdio: 'inherit', env: {...process.env,
        COHERENCE_PARENT_BRIDGE_SOCKET: endpoint, COHERENCE_PARENT_BRIDGE_TOKEN: token,
        COHERENCE_PARENT_BRIDGE_SESSION: session, COHERENCE_PARENT_BRIDGE_RUN: params.run}});
      child.once('error', async error => {
        if (active === bridge) await close();
        pi.sendMessage({customType: 'coordinate_implementation_complete', display: true,
          content: `Coordinate implementation ${params.run} could not start: ${error.message}`, details: {run: params.run}},
          {triggerTurn: true, deliverAs: 'followUp'});
      });
      child.once('exit', async (code, signal) => {
        if (active === bridge) await close();
        pi.sendMessage({customType: 'coordinate_implementation_complete', display: true,
          content: `Coordinate implementation ${params.run} finished (exit ${code}${signal ? `, ${signal}` : ''}).`, details: {run: params.run}},
          {triggerTurn: true, deliverAs: 'followUp'});
      });
      return textResult(`Started coordinate implementation run ${params.run}.`, {run: params.run});
    },
  });

  pi.registerTool({
    name: 'coordinate_implementation_reply', label: 'Reply to coordinate implementation',
    description: 'Return the user answer for the exact pending coordinate-implementation owner question.',
    parameters: replyParameters, executionMode: 'sequential',
    async execute(_id, params, _signal, _update, ctx) {
      if (!active || ctx.sessionManager.getSessionId() !== active.session || params.run !== active.run ||
          !active.pending || params.request_id !== active.pending.request_id) {
        throw new Error('no matching pending coordinate-implementation question');
      }
      const pending = active.pending;
      active.pending = undefined;
      send(pending.socket, {request_id: params.request_id, answer: params.answer});
      return textResult('Returned the owner answer to the waiting worker.', {request_id: params.request_id, run: params.run});
    },
  });

  pi.on('session_shutdown', () => close());
}
