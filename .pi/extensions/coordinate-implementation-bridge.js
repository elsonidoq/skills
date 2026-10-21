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
    tasks: {type: 'string'}, executor: {type: 'string'}, run: {type: 'string'}, resume: {type: 'boolean'},
  }, required: ['run'],
};
const replyParameters = {
  type: 'object', additionalProperties: false,
  properties: {
    request_id: {type: 'string'}, run: {type: 'string'}, answer: {type: 'string'},
  }, required: ['request_id', 'run', 'answer'],
};
const steerParameters = {
  type: 'object', additionalProperties: false,
  properties: {
    request_id: {type: 'string'}, run: {type: 'string'}, task_id: {type: 'string'},
    invocation_id: {type: 'string'}, instruction: {type: 'string'},
  }, required: ['request_id', 'run', 'task_id', 'invocation_id', 'instruction'],
};

function textResult(text, details = undefined) {
  return {content: [{type: 'text', text}], details};
}

export default function coordinateImplementationBridge(pi) {
  let active;

  const close = async (bridge, cancel = false) => {
    if (bridge.closing) return bridge.closing;
    bridge.closing = (async () => {
      if (cancel && bridge.child && bridge.child.exitCode === null && !bridge.child.killed) {
        bridge.child.kill('SIGTERM');
        await bridge.exited;
      }
      if (bridge.abortSignal) bridge.abortSignal.removeEventListener('abort', bridge.abort);
      if (active === bridge) active = undefined;
      bridge.server.close();
      for (const socket of bridge.sockets) socket.destroy();
      await rm(bridge.directory, {recursive: true, force: true});
    })();
    return bridge.closing;
  };

  const send = (socket, value) => {
    if (!socket.destroyed) socket.end(JSON.stringify(value) + '\n');
  };
  const write = (socket, value) => {
    return !socket.destroyed && socket.write(JSON.stringify(value) + '\n');
  };
  const exactTarget = value => value && typeof value === 'object' &&
    ['run_id', 'task_id', 'invocation_id', 'session_id', 'role'].every(key => typeof value[key] === 'string' && value[key]) &&
    ['task_worker', 'corrective_worker', 'fixer'].includes(value.role);
  const sameTarget = (left, right) => exactTarget(left) && exactTarget(right) &&
    ['run_id', 'task_id', 'invocation_id', 'session_id', 'role'].every(key => left[key] === right[key]);
  const settleUnknown = (bridge, target) => {
    for (const [requestId, direction] of bridge.directions) {
      if (direction.target === target && ['accepted', 'queued'].includes(direction.status)) {
        direction.status = 'unknown';
        pi.sendMessage({customType: 'coordinate_implementation_steering_status', display: true,
          content: `Coordinate implementation direction ${requestId}: unknown.`,
          details: {run: bridge.run, request_id: requestId, status: 'unknown',
            task_id: target.task_id, invocation_id: target.invocation_id}},
          {triggerTurn: true, deliverAs: 'followUp'});
      }
    }
  };

  const receive = (bridge, socket, line) => {
    let request;
    try { request = JSON.parse(line); } catch { send(socket, {error: 'invalid bridge request'}); return; }
    if (request && ['steering_target', 'steering_status', 'steering_closed'].includes(request.type)) {
      if (request.token !== bridge.token || request.session_id !== bridge.session || request.run_id !== bridge.run) {
        send(socket, {error: 'bridge request does not target this parent session and run'}); return;
      }
      if (request.type === 'steering_target') {
        if (!exactTarget(request.target) || request.target.run_id !== bridge.run) { send(socket, {error: 'invalid active steering target'}); return; }
        bridge.target = {target: request.target, socket};
        pi.sendMessage({customType: 'coordinate_implementation_target', display: true,
          content: `Coordinate implementation active target: ${request.target.task_id}/${request.target.invocation_id}.`,
          details: {run: bridge.run, task_id: request.target.task_id, invocation_id: request.target.invocation_id, role: request.target.role}},
          {triggerTurn: true, deliverAs: 'followUp'});
        return;
      }
      if (request.type === 'steering_closed') {
        if (bridge.target?.socket === socket && sameTarget(request.target, bridge.target.target)) {
          settleUnknown(bridge, bridge.target.target);
          bridge.target = undefined;
        }
        return;
      }
      if (typeof request.request_id !== 'string' || typeof request.status !== 'string' ||
          bridge.target?.socket !== socket || !sameTarget(request.target, bridge.target.target)) { send(socket, {error: 'invalid steering status'}); return; }
      const direction = bridge.directions.get(request.request_id);
      if (!direction) return;
      direction.status = request.status;
      pi.sendMessage({customType: 'coordinate_implementation_steering_status', display: true,
        content: `Coordinate implementation direction ${request.request_id}: ${request.status}.`,
        details: {run: bridge.run, request_id: request.request_id, status: request.status,
          task_id: direction.target.task_id, invocation_id: direction.target.invocation_id}},
        {triggerTurn: true, deliverAs: 'followUp'});
      return;
    }
    if (!request || !['ready', 'question'].includes(request.type) || request.token !== bridge.token ||
        request.session_id !== bridge.session || request.run_id !== bridge.run ||
        typeof request.request_id !== 'string' || !request.request_id ||
        (request.type === 'question' && typeof request.question !== 'string')) {
      send(socket, {request_id: request?.request_id, error: 'bridge request does not target this parent session and run'});
      return;
    }
    if (!pi.getActiveTools().includes('coordinate_implementation_reply')) {
      send(socket, {request_id: request.request_id, error: 'parent reply tool unavailable; enable coordinate_implementation_reply before launch'});
      return;
    }
    if (request.type === 'ready') {
      send(socket, {request_id: request.request_id, ready: true});
      return;
    }
    if (bridge.pending) {
      send(socket, {request_id: request.request_id, error: 'parent owner bridge already has a pending question'});
      return;
    }
    bridge.pending = {request_id: request.request_id, socket};
    pi.sendMessage({
      customType: 'coordinate_implementation_question', display: true,
      content: `Coordinate implementation requires owner input before continuing: ${request.question}\n\nAsk the user, then call coordinate_implementation_reply with request_id ${request.request_id} and run ${bridge.run}.`,
      details: {request_id: request.request_id, run: bridge.run},
    }, {triggerTurn: true, deliverAs: 'followUp'});
  };

  pi.registerTool({
    name: 'coordinate_implementation_start', label: 'Start coordinate implementation',
    description: 'Launch the approved coordinate-implementation runner through this parent session.',
    parameters: startParameters, executionMode: 'sequential',
    async execute(_id, params, signal, _update, ctx) {
      if (active) throw new Error('coordinate implementation bridge already has an active run');
      if (!params.resume && (typeof params.tasks !== 'string' || typeof params.executor !== 'string'))
        throw new Error('start requires tasks and executor; resume requires only the retained run ID');
      const directory = await mkdtemp(path.join(tmpdir(), 'coordinate-implementation-'));
      const endpoint = path.join(directory, 'bridge.sock');
      const session = ctx.sessionManager.getSessionId();
      const token = randomBytes(32).toString('hex');
      const sockets = new Set();
      const bridge = {directory, endpoint, session, token, run: params.run, sockets, pending: undefined, target: undefined,
        directions: new Map(), server: undefined, child: undefined, exited: undefined, closing: undefined, abortSignal: signal, abort: undefined};
      try {
        await chmod(directory, 0o700);
        const server = createServer(socket => {
          sockets.add(socket);
          let data = '';
          socket.setEncoding('utf8');
          socket.on('data', chunk => {
            data += chunk;
            let end;
            while ((end = data.indexOf('\n')) >= 0) {
              const line = data.slice(0, end);
              data = data.slice(end + 1);
              receive(bridge, socket, line);
            }
          });
          socket.on('close', () => {
            sockets.delete(socket);
            if (bridge.pending?.socket === socket) bridge.pending = undefined;
            if (bridge.target?.socket === socket) {
              settleUnknown(bridge, bridge.target.target);
              bridge.target = undefined;
            }
          });
          socket.on('error', () => {});
        });
        bridge.server = server;
        await new Promise((resolve, reject) => server.once('error', reject).listen(endpoint, resolve));
        await chmod(endpoint, 0o600);
        active = bridge;
        // Parent stdout belongs to Pi's RPC protocol; preserve runner diagnostics on stderr.
        const child = spawn(path.join(ctx.cwd, 'scripts/coordinate-implementation'), params.resume ? [
          'resume', '--project', ctx.cwd, '--run', params.run,
        ] : [
          'start', '--project', ctx.cwd, '--tasks', params.tasks, '--executor', params.executor, '--run', params.run,
        ], {cwd: ctx.cwd, stdio: ['ignore', 2, 2], env: {...process.env,
          COHERENCE_PARENT_BRIDGE_SOCKET: endpoint, COHERENCE_PARENT_BRIDGE_TOKEN: token,
          COHERENCE_PARENT_BRIDGE_SESSION: session, COHERENCE_PARENT_BRIDGE_RUN: params.run}});
        bridge.child = child;
        bridge.exited = new Promise(resolve => {
          child.once('exit', (...result) => resolve(result));
          child.once('error', () => resolve());
        });
        // This also cleanly interrupts a runner waiting on its inherited worktree lock;
        // it never replaces or signals the lock holder.
        bridge.abort = () => { void close(bridge, true); };
        signal?.addEventListener('abort', bridge.abort, {once: true});
        if (signal?.aborted) bridge.abort();
        child.once('error', async error => {
          await close(bridge);
          pi.sendMessage({customType: 'coordinate_implementation_complete', display: true,
            content: `Coordinate implementation ${params.run} could not start: ${error.message}`, details: {run: params.run}},
            {triggerTurn: true, deliverAs: 'followUp'});
        });
        child.once('exit', async (code, childSignal) => {
          await close(bridge);
          pi.sendMessage({customType: 'coordinate_implementation_complete', display: true,
            content: `Coordinate implementation ${params.run} finished (exit ${code}${childSignal ? `, ${childSignal}` : ''}).`, details: {run: params.run}},
            {triggerTurn: true, deliverAs: 'followUp'});
        });
        return textResult(`Started coordinate implementation run ${params.run}.`, {run: params.run});
      } catch (error) {
        if (bridge.server) await close(bridge);
        else await rm(directory, {recursive: true, force: true});
        throw error;
      }
    },
  });

  pi.registerTool({
    name: 'coordinate_implementation_steer', label: 'Steer active coordinate implementation worker',
    description: 'Relay an owner direction to one exact active worker/fixer invocation; returns queue status, never compliance.',
    parameters: steerParameters, executionMode: 'sequential',
    async execute(_id, params, _signal, _update, ctx) {
      if (!active || ctx.sessionManager.getSessionId() !== active.session || params.run !== active.run) {
        throw new Error('no matching active coordinate-implementation run');
      }
      const target = active.target;
      if (!target || target.target.task_id !== params.task_id || target.target.invocation_id !== params.invocation_id) {
        throw new Error('exact active worker target unavailable; inspect the current target before sending');
      }
      const prior = active.directions.get(params.request_id);
      if (prior) {
        if (prior.target !== target.target) throw new Error('direction request ID already targets another invocation');
        return textResult(`Direction ${params.request_id} is ${prior.status}.`, {request_id: params.request_id, status: prior.status});
      }
      const direction = {target: target.target, status: 'accepted'};
      active.directions.set(params.request_id, direction);
      if (!write(target.socket, {type: 'steer', request_id: params.request_id, target: target.target, instruction: params.instruction})) {
        direction.status = 'unknown';
        return textResult(`Direction ${params.request_id} status is unknown: the active target connection closed.`,
          {request_id: params.request_id, status: 'unknown', task_id: params.task_id, invocation_id: params.invocation_id});
      }
      return textResult(`Direction ${params.request_id} accepted for the exact active worker; awaiting queue status.`,
        {request_id: params.request_id, status: 'accepted', task_id: params.task_id, invocation_id: params.invocation_id});
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

  pi.on('session_shutdown', () => active && close(active, true));
}
