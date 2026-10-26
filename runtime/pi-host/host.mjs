// SDK transport only. SDK owns tools, retries, compaction and conversation state.
import crypto from 'node:crypto';
import path from 'node:path';
import { isDeepStrictEqual } from 'node:util';
import { constants } from 'node:fs';
import { access, mkdir, readFile, writeFile, realpath } from 'node:fs/promises';
import readline from 'node:readline';
import { fileURLToPath } from 'node:url';
import { createAgentSession, createEditToolDefinition, createWriteToolDefinition,
  DefaultResourceLoader, getAgentDir, ModelRuntime, SessionManager }
  from '@earendil-works/pi-coding-agent';

function enforceExactAssignment(session, requested) {
  const observed = {provider: session.model?.provider, model: session.model?.id,
    effort: session.thinkingLevel};
  if (observed.provider !== requested.provider || observed.model !== requested.model ||
      observed.effort !== requested.effort) {
    throw new Error('workflow executor prompt operation exact SDK assignment mismatch before provider prompt: requested ' +
      `${requested.provider}/${requested.model} effort ${requested.effort}; observed ` +
      `${observed.provider ?? 'missing'}/${observed.model ?? 'missing'} effort ${observed.effort ?? 'missing'}. ` +
      'Correct the executor model and effort to an SDK-supported exact assignment.');
  }
}

export async function promptSession(session, prompt, emit) {
  if (session.coherenceRequestedAssignment) enforceExactAssignment(session, session.coherenceRequestedAssignment);
  const unsubscribe = session.subscribe(event => {
    if (['tool_execution_start', 'tool_execution_end', 'compaction_start', 'compaction_end',
      'auto_compaction_start', 'auto_compaction_end', 'auto_retry_start', 'auto_retry_end'].includes(event.type)) {
      emit({type: 'event', event: event.type, tool: event.toolName,
        isError: event.isError});
    }
  });
  try {
    await session.prompt(prompt);
    // A resolved prompt alone is not a reusable/disposable boundary.
    if (typeof session.waitForIdle === 'function') await session.waitForIdle();
    const last = [...session.messages].reverse().find(m => m.role === 'assistant');
    if (last?.stopReason === 'error' || last?.stopReason === 'aborted') {
      throw new Error(last.errorMessage || last.stopReason);
    }
    return session.getLastAssistantText() || '';
  } finally {
    unsubscribe();
  }
}

export function mutationTools(project, ask) {
  const claim = async absolutePath => {
    // Operations receive the SDK's effective path, after all SDK normalization.
    const answer = await ask({type: 'claim', path: path.relative(project, absolutePath)});
    if (answer.error) throw new Error(answer.error);
  };
  const write = createWriteToolDefinition(project);
  return [
    {
      ...write,
      execute: (id, args, signal, onUpdate, ctx) => createWriteToolDefinition(project, {
        operations: {
          // The SDK supplies only the directory here. Defer mkdir until writeFile
          // supplies the full effective target, so consent precedes EVERY mutation.
          mkdir: async () => {},
          writeFile: async (absolutePath, content) => {
            await claim(absolutePath);
            if (signal?.aborted) throw new Error('Operation aborted');
            await mkdir(path.dirname(absolutePath), {recursive: true});
            if (signal?.aborted) throw new Error('Operation aborted');
            await writeFile(absolutePath, content, 'utf-8');
          },
        },
      }).execute(id, args, signal, onUpdate, ctx),
    },
    {
      ...createEditToolDefinition(project),
      execute: (id, args, signal, onUpdate, ctx) => createEditToolDefinition(project, {
        operations: {
          access: absolutePath => access(absolutePath, constants.R_OK | constants.W_OK),
          readFile,
          writeFile: async (absolutePath, content) => {
            await claim(absolutePath);
            if (signal?.aborted) throw new Error('Operation aborted');
            await writeFile(absolutePath, content, 'utf-8');
          },
        },
      }).execute(id, args, signal, onUpdate, ctx),
    },
  ];
}

export async function createWorkflowSession({project, executor, readOnly = false, savedSession, reuseKey = null, reviewRepair = false}, ask) {
  const sessionDir = path.join(project, '.coherence', 'workflow', 'sessions');
  await mkdir(sessionDir, {recursive: true});
  const canonicalSessionDir = await realpath(sessionDir);
  if (reuseKey !== null && typeof reuseKey !== 'string') throw new Error('saved session reuse key must be a string');
  const compatibility = {project: path.resolve(project), provider: executor.provider,
    model: executor.model, effort: executor.effort, readOnly, reuseKey};
  // Only the runner's explicit review→repair handoff may enable mutation in a
  // previously read-only session. All other effective resources stay identical.
  if (reviewRepair && (readOnly || !savedSession || savedSession.compatibility?.readOnly !== true)) {
    throw new Error('review repair requires a saved read-only reviewer and writable target');
  }
  const sourceCompatibility = reviewRepair ? {...compatibility, readOnly: true} : compatibility;
  // Retain the reviewer's resource policy after writer tools are enabled, also
  // on subsequent corrective prompts. Old saved reviews gain this marker here.
  const reviewerContext = readOnly || reviewRepair || savedSession?.reviewerContext === true;
  let reportedOutcome = null;
  let sessionManager;
  if (savedSession) {
    if (typeof savedSession !== 'object' || typeof savedSession.id !== 'string' ||
        typeof savedSession.file !== 'string' || !isDeepStrictEqual(savedSession.compatibility, sourceCompatibility)) {
      throw new Error('saved session identity or effective resources mismatch');
    }
    const sessionFile = await realpath(savedSession.file);
    if (path.dirname(sessionFile) !== canonicalSessionDir) throw new Error('saved session file is outside runner-private storage');
    sessionManager = SessionManager.open(sessionFile, canonicalSessionDir, project);
    if (sessionManager.getSessionId() !== savedSession.id) throw new Error('saved session identity mismatch');
  } else {
    sessionManager = SessionManager.create(project, canonicalSessionDir);
  }
  const modelRuntime = await ModelRuntime.create({
    ...(process.env.COHERENCE_AUTH_PATH ? {authPath: process.env.COHERENCE_AUTH_PATH} : {}),
    ...(process.env.COHERENCE_CATALOG_PATH ? {modelsStorePath: process.env.COHERENCE_CATALOG_PATH} : {}),
  });
  const model = modelRuntime.getModel(executor.provider, executor.model);
  if (!model) throw new Error(`Model not found: ${executor.provider}/${executor.model}`);
  const resourceLoader = new DefaultResourceLoader({
    cwd: project, agentDir: getAgentDir(),
    // No ambient extension may add a writer to the independent reviewer or
    // bypass the runner's focused checkpoint. Ordinary context/skills still load.
    noExtensions: true,
    noSkills: reviewerContext,
    noPromptTemplates: true,
    extensionFactories: [pi => {
      if (!readOnly) for (const tool of mutationTools(project, ask)) pi.registerTool(tool);
      pi.on('tool_call', async event => {
        if (event.toolName === 'bash') {
          const answer = await ask({type: 'command', phase: 'start', call: event.toolCallId});
          if (answer.error) return {block: true, reason: answer.error};
        }
      });
      pi.on('tool_result', async event => {
        if (event.toolName === 'bash') {
          const answer = await ask({type: 'command', phase: 'end', call: event.toolCallId});
          if (answer.error) return {isError: true, content: [{type: 'text', text: answer.error}]};
        }
      });
      if (!readOnly) pi.registerTool({
        name: 'cleanup_artifact', label: 'Clean known task artifact',
        description: 'Selectively remove one runner-known generated file; never a directory or unknown output.',
        parameters: {type: 'object', properties: {path: {type: 'string'}}, required: ['path']},
        execute: async (_id, args) => {
          const answer = await ask({type: 'cleanup', path: args.path});
          if (answer.error) throw new Error(answer.error);
          return {content: [{type: 'text', text: 'Removed known task artifact: ' + args.path}], details: {}};
        },
      });
      if (!readOnly) pi.registerTool({
        name: 'report_task_outcome', label: 'Report unsuccessful task outcome',
        description: 'Report that this task is blocked, failed, or incomplete. Use this when required acceptance is known failed or unrun; do not use it for corrected errors.',
        parameters: {type: 'object', properties: {status: {type: 'string', enum: ['blocked', 'failed', 'incomplete']}}, required: ['status']},
        execute: async (_id, args) => {
          reportedOutcome = args.status;
          return {content: [{type: 'text', text: 'Reported task outcome: ' + args.status}], details: {}};
        },
      });
      if (!readOnly) pi.registerTool({
        name: 'ask_owner', label: 'Ask owner',
        description: 'Ask a material scope or permission question; do not invent an answer.',
        parameters: {type: 'object', properties: {question: {type: 'string'}}, required: ['question']},
        execute: async (_id, args) => {
          const answer = await ask({type: 'question', question: args.question});
          if (answer.error) throw new Error(answer.error);
          return {content: [{type: 'text', text: answer.answer}], details: {}};
        },
      });
    }],
  });
  await resourceLoader.reload();
  const {session} = await createAgentSession({
    cwd: project, modelRuntime, model, thinkingLevel: executor.effort,
    tools: readOnly ? ['read', 'grep', 'find', 'ls'] : ['read', 'grep', 'find', 'ls', 'edit', 'write', 'bash', 'ask_owner', 'cleanup_artifact', 'report_task_outcome'],
    sessionManager, resourceLoader,
  });
  try {
    await session.bindExtensions({});
    enforceExactAssignment(session, executor);
    if (!readOnly && !session.getActiveToolNames().includes('ask_owner')) {
      throw new Error('Worker ask_owner tool unavailable; enable it in the SDK worker tool list before execution');
    }
    // Only runner-private identity is retained. Every open above recreated the
    // current task's resource loader, callbacks, tools, and mutation scope.
    session.coherenceRequestedAssignment = {...executor};
    session.coherenceSavedSession = {id: sessionManager.getSessionId(), file: sessionManager.getSessionFile(), compatibility,
      ...(reviewerContext ? {reviewerContext: true} : {})};
    session._coherenceSessionManager = sessionManager;
    session.coherenceTaskOutcome = () => reportedOutcome;
    return session;
  } catch (error) {
    session.dispose();
    throw error;
  }
}

function observation(session) {
  const usage = session.getContextUsage?.();
  const stats = session.getSessionStats?.();
  // Resolve reserve through the SDK's model-specific precedence, not a parallel
  // workflow default. Missing optional settings remain unknown (fresh routing).
  let compaction;
  try { compaction = session.settingsManager?.getCompactionSettings(session.model); }
  catch { /* optional observation only */ }
  const headroom = {
    context_window: usage?.contextWindow ?? null,
    effective_reserve: compaction?.reserveTokens ?? null,
    occupancy: usage?.tokens ?? null,
    compaction_enabled: compaction?.enabled ?? null,
    compaction_applicable: session.model && Number.isFinite(usage?.contextWindow)
      ? usage.contextWindow > 0 : null,
  };
  const entries = session._coherenceSessionManager?.getEntries?.() ?? [];
  // Persisted compaction entries, rather than start/end events, are the only
  // accounting evidence: an aborted compaction never creates an entry here.
  const compactionEntries = [...new Map(entries
    .filter(entry => entry?.type === 'compaction' && typeof entry.id === 'string')
    .map(entry => [entry.id, {id: entry.id, summary_usage: entry.usage ?? null}])).values()];
  // These are SDK construction observations, not provider-side execution proof.
  // Keep requested and SDK-exposed values distinct even after exact-match guards.
  const requested = session.coherenceRequestedAssignment;
  const sdkObservedAssignment = {
    provider: session.model?.provider ?? null,
    model: session.model?.id ?? null,
    effort: session.thinkingLevel ?? null,
  };
  return {
    requested_assignment: {
      provider: requested?.provider ?? null,
      model: requested?.model ?? null,
      effort: requested?.effort ?? null,
    },
    sdk_observed_assignment: sdkObservedAssignment,
    session_id: session.coherenceSavedSession?.id ?? null,
    branch: session.sessionId ?? session.coherenceSavedSession?.id ?? null,
    epoch: session.coherenceEpoch,
    entry: session._coherenceSessionManager?.getLeafId() ?? null,
    counters: stats?.tokens ?? null,
    costs: {estimated_usd: stats?.cost ?? null},
    compaction_entries: compactionEntries,
    headroom,
    context_tokens: usage?.tokens ?? null,
    context_window: usage?.contextWindow ?? null,
  };
}

export function sessionObservationRecord(request, session) {
  // Old controllers accept only event/question/result/error records. Newer
  // adapters opt in before the host emits this standalone recovery record.
  if (request.sessionObservations !== true) return null;
  return {type: 'session', session: session.coherenceSavedSession, before: observation(session)};
}

function validTarget(value) {
  return value && typeof value === 'object' && ['run_id', 'task_id', 'invocation_id']
    .every(key => typeof value[key] === 'string' && value[key].length > 0) &&
    ['task_worker', 'corrective_worker', 'fixer'].includes(value.role);
}

function directionEnvelope(requestId, instruction) {
  // Prefixing makes even a leading slash inert to the SDK command parser while
  // retaining the owner instruction verbatim in the conversation.
  return `[owner-direction id=${requestId}]\n${instruction}`;
}

export function steeringTarget(request, session) {
  if (!validTarget(request.steering)) return null;
  return {...request.steering, session_id: session.coherenceSavedSession.id};
}

export function steeringController(request, session, emit) {
  const target = steeringTarget(request, session);
  if (!target) return null;
  let active = true;
  const requests = new Map();
  const sameTarget = candidate => validTarget(candidate) &&
    ['run_id', 'task_id', 'invocation_id', 'session_id', 'role'].every(key => candidate[key] === target[key]);
  const report = (requestId, status, extra = {}) =>
    emit({type: 'steer', request_id: requestId, status, target, ...extra});
  const close = (reason, status = 'failed-unavailable') => {
    if (!active) return;
    active = false;
    for (const [requestId, entry] of requests) {
      if (entry.status === 'queued') report(requestId, status, {reason});
    }
  };
  const unsubscribe = session.subscribe(event => {
    if (event.type === 'message_start' && event.message?.role === 'user') {
      const text = event.message.content?.filter(part => part.type === 'text').map(part => part.text).join('') ?? '';
      for (const [requestId, entry] of requests) {
        if (entry.status === 'queued' && text === entry.envelope) {
          entry.status = 'consumed';
          report(requestId, 'consumed');
        }
      }
    } else if (event.type === 'agent_settled') {
      // agent_end may be followed by SDK retry, compaction, or queued input.
      close('target settled before observed consumption');
    }
  });
  emit({type: 'target', status: 'active', target});
  return {
    async steer(control) {
      const requestId = control?.request_id;
      if (typeof requestId !== 'string' || requestId.length === 0) return;
      const prior = requests.get(requestId);
      if (prior) {
        report(requestId, prior.status);
        return;
      }
      if (!active || !sameTarget(control.target)) {
        report(requestId, 'failed-unavailable', {reason: !active ? 'target is closed' : 'exact active target required'});
        return;
      }
      if (typeof control.instruction !== 'string') {
        report(requestId, 'failed-unavailable', {reason: 'owner direction instruction must be text'});
        return;
      }
      const entry = {status: 'accepted', envelope: directionEnvelope(requestId, control.instruction)};
      requests.set(requestId, entry);
      report(requestId, 'accepted');
      try {
        await session.steer(entry.envelope, undefined, {source: 'interactive'});
        entry.status = 'queued';
        report(requestId, 'queued');
      } catch (error) {
        entry.status = 'failed-unavailable';
        report(requestId, 'failed-unavailable', {reason: error.message});
      }
    },
    close(reason = 'host input closed', status) { close(reason, status); unsubscribe(); },
  };
}

export async function execute(request, emit, ask, controls = null) {
  const session = await createWorkflowSession(request, ask);
  session.coherenceEpoch = crypto.randomUUID();
  // Preserve the existing session identity before an invocation can fail. The
  // adapter can then expose that failed call/cause for inspection, never retry it.
  const sessionRecord = sessionObservationRecord(request, session);
  if (sessionRecord) emit(sessionRecord);
  const steering = steeringController(request, session, emit);
  controls?.setSteering(steering);
  let aborting;
  const cancel = () => { aborting ??= Promise.resolve(session.abort()); };
  process.on('SIGTERM', cancel);
  process.on('SIGINT', cancel);
  try {
    const before = observation(session);
    const text = await promptSession(session, request.prompt, emit);
    session.coherenceSavedSession = {...session.coherenceSavedSession,
      file: session._coherenceSessionManager.getSessionFile()};
    return {text, outcome: session.coherenceTaskOutcome?.() ?? 'completed',
      session: session.coherenceSavedSession, before, after: observation(session)};
  } finally {
    process.off('SIGTERM', cancel);
    process.off('SIGINT', cancel);
    // Do not dispose/release the host while its owned SDK abort is still
    // draining an active tool invocation.
    if (aborting) await aborting.catch(() => {});
    steering?.close('host disposed');
    session.dispose();
  }
}

async function main() {
  const lines = readline.createInterface({input: process.stdin});
  const iterator = lines[Symbol.asyncIterator]();
  const next = async () => {
    const line = await iterator.next();
    if (line.done) throw new Error('SDK transport input closed');
    return JSON.parse(line.value);
  };
  const emit = value => process.stdout.write(JSON.stringify(value) + '\n');
  try {
    const request = await next();
    // Old adapters retain their one-at-a-time uncorrelated callback protocol.
    if (!validTarget(request.steering)) {
      const result = await execute(request, emit, async value => { emit(value); return next(); });
      emit({type: 'result', ...result});
      return;
    }
    let steering, resolveSteering;
    const steeringReady = new Promise(resolve => { resolveSteering = resolve; });
    const callbacks = new Map();
    let callbackSequence = 0;
    const ask = value => new Promise((resolve, reject) => {
      const requestId = `callback-${++callbackSequence}`;
      callbacks.set(requestId, {resolve, reject});
      emit({...value, request_id: requestId});
    });
    const operation = execute(request, emit, ask, {setSteering(value) { steering = value; resolveSteering(value); }});
    const input = (async () => {
      try {
        while (true) {
          const value = await next();
          if (value?.type === 'steer') await (steering ?? await steeringReady)?.steer(value);
          else if (value?.type === 'reply' && typeof value.request_id === 'string') {
            const pending = callbacks.get(value.request_id);
            if (pending) { callbacks.delete(value.request_id); pending.resolve(value.reply); }
          }
        }
      } catch (error) {
        steering?.close('host input closed', 'unknown');
        for (const pending of callbacks.values()) pending.reject(error);
        callbacks.clear();
      }
    })();
    const result = await operation;
    emit({type: 'result', ...result});
    // The result closes the host protocol; stdin may remain open in callers.
    lines.close();
    await input;
  } catch (error) {
    emit({type: 'error', message: error.message});
    process.exitCode = 1;
  } finally {
    lines.close();
  }
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await main();
