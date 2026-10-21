// SDK transport only. SDK owns tools, retries, compaction and conversation state.
import crypto from 'node:crypto';
import path from 'node:path';
import { constants } from 'node:fs';
import { access, mkdir, readFile, writeFile, realpath } from 'node:fs/promises';
import readline from 'node:readline';
import { fileURLToPath } from 'node:url';
import { createAgentSession, createEditToolDefinition, createWriteToolDefinition,
  DefaultResourceLoader, getAgentDir, ModelRuntime, SessionManager }
  from '@earendil-works/pi-coding-agent';

export async function promptSession(session, prompt, emit) {
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

export async function createWorkflowSession({project, executor, readOnly = false, savedSession, reuseKey = null}, ask) {
  const sessionDir = path.join(project, '.coherence', 'workflow', 'sessions');
  await mkdir(sessionDir, {recursive: true});
  const canonicalSessionDir = await realpath(sessionDir);
  if (reuseKey !== null && typeof reuseKey !== 'string') throw new Error('saved session reuse key must be a string');
  const compatibility = {project: path.resolve(project), provider: executor.provider,
    model: executor.model, effort: executor.effort, readOnly, reuseKey};
  let sessionManager;
  if (savedSession) {
    if (typeof savedSession !== 'object' || typeof savedSession.id !== 'string' ||
        typeof savedSession.file !== 'string' || JSON.stringify(savedSession.compatibility) !== JSON.stringify(compatibility)) {
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
    noSkills: readOnly,
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
    tools: readOnly ? ['read', 'grep', 'find', 'ls'] : ['read', 'grep', 'find', 'ls', 'edit', 'write', 'bash', 'ask_owner'],
    sessionManager, resourceLoader,
  });
  await session.bindExtensions({});
  if (!readOnly && !session.getActiveToolNames().includes('ask_owner')) {
    session.dispose();
    throw new Error('Worker ask_owner tool unavailable; enable it in the SDK worker tool list before execution');
  }
  // Only runner-private identity is retained. Every open above recreated the
  // current task's resource loader, callbacks, tools, and mutation scope.
  session.coherenceSavedSession = {id: sessionManager.getSessionId(), file: sessionManager.getSessionFile(), compatibility};
  session._coherenceSessionManager = sessionManager;
  return session;
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
  return {
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

export async function execute(request, emit, ask) {
  const session = await createWorkflowSession(request, ask);
  session.coherenceEpoch = crypto.randomUUID();
  // Preserve the existing session identity before an invocation can fail. The
  // adapter can then expose that failed call/cause for inspection, never retry it.
  const sessionRecord = sessionObservationRecord(request, session);
  if (sessionRecord) emit(sessionRecord);
  let aborting;
  const cancel = () => { aborting ??= Promise.resolve(session.abort()); };
  process.on('SIGTERM', cancel);
  process.on('SIGINT', cancel);
  try {
    const before = observation(session);
    const text = await promptSession(session, request.prompt, emit);
    session.coherenceSavedSession = {...session.coherenceSavedSession,
      file: session._coherenceSessionManager.getSessionFile()};
    return {text, session: session.coherenceSavedSession, before, after: observation(session)};
  } finally {
    process.off('SIGTERM', cancel);
    process.off('SIGINT', cancel);
    // Do not dispose/release the host while its owned SDK abort is still
    // draining an active tool invocation.
    if (aborting) await aborting.catch(() => {});
    session.dispose();
  }
}

async function main() {
  const lines = readline.createInterface({input: process.stdin});
  const iterator = lines[Symbol.asyncIterator]();
  const receive = async () => {
    const line = await iterator.next();
    if (line.done) throw new Error('SDK transport input closed');
    return JSON.parse(line.value);
  };
  const emit = value => process.stdout.write(JSON.stringify(value) + '\n');
  const ask = async value => { emit(value); return receive(); };
  try {
    const request = await receive();
    const result = await execute(request, emit, ask);
    emit({type: 'result', ...result});
  } catch (error) {
    emit({type: 'error', message: error.message});
    process.exitCode = 1;
  } finally {
    lines.close();
  }
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await main();
