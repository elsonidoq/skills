// SDK transport only. SDK owns tools, retries, compaction and conversation state.
import path from 'node:path';
import readline from 'node:readline';
import { fileURLToPath } from 'node:url';
import { createAgentSession, DefaultResourceLoader, getAgentDir, ModelRuntime, SessionManager }
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

export async function execute(request, emit, ask) {
  const {project, executor, prompt, readOnly = false} = request;
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
      pi.on('tool_call', async event => {
        if (event.toolName === 'bash') {
          const answer = await ask({type: 'command', phase: 'start', call: event.toolCallId});
          if (answer.error) return {block: true, reason: answer.error};
        }
        if (event.toolName === 'edit' || event.toolName === 'write') {
          const name = path.relative(project, path.resolve(project, event.input.path));
          const answer = await ask({type: 'claim', path: name});
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
    tools: readOnly ? ['read', 'grep', 'find', 'ls'] : ['read', 'grep', 'find', 'ls', 'edit', 'write', 'bash'],
    sessionManager: SessionManager.inMemory(project), resourceLoader,
  });
  await session.bindExtensions({});
  const cancel = () => { void session.abort(); };
  process.on('SIGTERM', cancel);
  process.on('SIGINT', cancel);
  try {
    return await promptSession(session, prompt, emit);
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
