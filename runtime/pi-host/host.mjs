// SDK transport only. SDK owns tools, retries, compaction and conversation state.
import path from 'node:path';
import { constants } from 'node:fs';
import { access, mkdir, readFile, writeFile } from 'node:fs/promises';
import readline from 'node:readline';
import { fileURLToPath } from 'node:url';
import { createAgentSession, createEditToolDefinition, createWriteToolDefinition,
  DefaultResourceLoader, getAgentDir, ModelRuntime, SessionManager }
  from '@earendil-works/pi-coding-agent';

export async function promptSession(session, prompt, emit) {
  const unsubscribe = session.subscribe(event => {
    if (['tool_execution_start', 'tool_execution_end', 'auto_compaction_start',
      'auto_compaction_end', 'auto_retry_start', 'auto_retry_end'].includes(event.type)) {
      emit({type: 'event', event: event.type, tool: event.toolName,
        isError: event.isError});
    }
  });
  try {
    await session.prompt(prompt);
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

export async function createWorkflowSession({project, executor, readOnly = false}, ask) {
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
    sessionManager: SessionManager.inMemory(project), resourceLoader,
  });
  await session.bindExtensions({});
  if (!readOnly && !session.getActiveToolNames().includes('ask_owner')) {
    session.dispose();
    throw new Error('Worker ask_owner tool unavailable; enable it in the SDK worker tool list before execution');
  }
  return session;
}

export async function execute(request, emit, ask) {
  const session = await createWorkflowSession(request, ask);
  const cancel = () => { void session.abort(); };
  process.on('SIGTERM', cancel);
  process.on('SIGINT', cancel);
  try {
    return await promptSession(session, request.prompt, emit);
  } finally {
    process.off('SIGTERM', cancel);
    process.off('SIGINT', cancel);
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
    emit({type: 'result', text: await execute(request, emit, ask)});
  } catch (error) {
    emit({type: 'error', message: error.message});
    process.exitCode = 1;
  } finally {
    lines.close();
  }
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await main();
