// Local provider responses only. SDK prompt, tools, steer queue and events stay real.
import assert from 'node:assert/strict';
import {mock} from 'node:test';
import {appendFile, readFile} from 'node:fs/promises';
import {setTimeout as delay} from 'node:timers/promises';
import {piSdk, importPiDependency} from '../../pi-host/sdk.mjs';
const {ModelRuntime} = piSdk;
const {createAssistantMessageEventStream, getCurrentTools} = await importPiDependency('@earendil-works/pi-ai');

export function installSteeringProvider(callback = 'question', directory = process.env.PI_CODING_AGENT_DIR) {
  const create = ModelRuntime.create.bind(ModelRuntime);
  return mock.method(ModelRuntime, 'create', async function (options) {
    assert.ok(directory, 'offline provider needs fixture-owned storage');
    const runtime = await create({...options, authPath: `${directory}/offline-auth.json`,
      modelsStorePath: `${directory}/offline-models.json`, modelsPath: null, refreshOnCreate: false});
    let calls = 0;
    runtime.registerProvider('openai', {
      api: 'openai-completions', apiKey: 'offline-fixture-not-a-credential',
      models: [{id: 'gpt-4o-mini', name: 'Offline fixture', reasoning: false, input: ['text'],
        cost: {input: 0, output: 0, cacheRead: 0, cacheWrite: 0}, contextWindow: 128000, maxTokens: 1024}],
      streamSimple(model, context, options) {
        const stream = createAssistantMessageEventStream();
        queueMicrotask(async () => {
          const message = {role: 'assistant', api: model.api, provider: model.provider, model: model.id,
            timestamp: Date.now(), content: [], stopReason: 'pending',
            usage: {input: 0, output: 0, cacheRead: 0, cacheWrite: 0, totalTokens: 0,
              cost: {input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0}}};
          try {
            await options?.onPayload?.({offline: true}, model);
            assert.ok(!options?.signal?.aborted, 'fixture was aborted');
            const reviewer = !getCurrentTools(context.messages).some(tool => tool.name === 'ask_owner');
            const pauseFixture = callback === 'pause' || callback === 'graph-pause';
            const priorEffect = context.messages.some(item => item.role === 'toolResult' && item.toolCallId === 'prior-tool');
            const priorQuestion = context.messages.some(item => item.role === 'assistant' &&
              item.content?.some(part => part.type === 'toolCall' && part.id === 'callback-tool'));
            const first = (pauseFixture ? !priorQuestion : calls++ === 0) && (!reviewer || callback === 'parent-trace');
            stream.push({type: 'start', partial: message});
            if (callback === 'parent-trace') {
              if (first) {
                for (const [index, id] of ['owner-one', 'owner-two', 'owner-missing', 'owner-error'].entries()) {
                  const args = {question: `owner question ${index + 1}`};
                  const toolCall = {type: 'toolCall', id, name: 'ask_user', arguments: args};
                  message.content.push(toolCall);
                  stream.push({type: 'toolcall_start', contentIndex: index, partial: message});
                  stream.push({type: 'toolcall_delta', contentIndex: index, delta: JSON.stringify(args), partial: message});
                  stream.push({type: 'toolcall_end', contentIndex: index, toolCall, partial: message});
                }
                message.stopReason = 'toolUse';
              } else {
                const text = 'parent fixture complete';
                message.content.push({type: 'text', text});
                stream.push({type: 'text_start', contentIndex: 0, partial: message});
                stream.push({type: 'text_delta', contentIndex: 0, delta: text, partial: message});
                stream.push({type: 'text_end', contentIndex: 0, content: text, partial: message});
                message.stopReason = 'stop';
              }
            } else if (callback === 'graph-parallel') {
              const latest = context.messages.filter(item => item.role === 'user').at(-1);
              const text = typeof latest?.content === 'string' ? latest.content
                : latest?.content?.filter(part => part.type === 'text').map(part => part.text).join('\n');
              const task = !reviewer ? JSON.parse(text.match(/Task: (\{[^\n]+\})/)[1]) : null;
              const id = task?.id;
              const log = process.env.COHERENCE_WAVE_EVENTS;
              const toolDone = name => context.messages.some(item => item.role === 'toolResult' && item.toolCallId === name);
              const emitTool = (name, args, toolId) => {
                const toolCall = {type: 'toolCall', id: toolId, name, arguments: args};
                message.content.push(toolCall);
                stream.push({type: 'toolcall_start', contentIndex: 0, partial: message});
                stream.push({type: 'toolcall_delta', contentIndex: 0, delta: JSON.stringify(args), partial: message});
                stream.push({type: 'toolcall_end', contentIndex: 0, toolCall, partial: message});
                message.stopReason = 'toolUse';
              };
              if (!reviewer && !toolDone(`wave-write-${id}`)) {
                await appendFile(log, `start ${id}\n`);
                if (process.env.COHERENCE_WAVE_BARRIER === '1' && ['A', 'B'].includes(id)) {
                  const until = Date.now() + 10000; // bounded fixture deadlock diagnostic, not runtime policy
                  while (true) {
                    const events = await readFile(log, 'utf8');
                    if (['A', 'B'].every(peer => events.includes(`start ${peer}\n`))) break;
                    assert.ok(Date.now() < until, 'directed SDK fixture workers did not overlap');
                    await delay(10);
                  }
                }
                emitTool('write', {path: task.owned_paths[0], content: `fixture ${id}\n`}, `wave-write-${id}`);
              } else if (!reviewer && process.env.COHERENCE_WAVE_FAIL === id && !toolDone(`wave-fail-${id}`)) {
                await appendFile(log, `failed ${id}\n`);
                emitTool('report_task_outcome', {status: 'incomplete'}, `wave-fail-${id}`);
              } else {
                if (!reviewer) await appendFile(log, `finish ${id}\n`);
                const text = reviewer ? '{"approved":true,"findings":[],"coverage":["local fixture only"],"coverage_gaps":[]}' : `finished ${id}`;
                message.content.push({type: 'text', text});
                stream.push({type: 'text_start', contentIndex: 0, partial: message});
                stream.push({type: 'text_delta', contentIndex: 0, delta: text, partial: message});
                stream.push({type: 'text_end', contentIndex: 0, content: text, partial: message});
                message.stopReason = 'stop';
              }
            } else if (callback === 'graph-pause' && !reviewer && !priorEffect) {
              const toolCall = {type: 'toolCall', id: 'prior-tool', name: 'write',
                arguments: {path: 'prior.txt', content: 'settled once\n'}};
              message.content.push(toolCall);
              stream.push({type: 'toolcall_start', contentIndex: 0, partial: message});
              stream.push({type: 'toolcall_delta', contentIndex: 0, delta: JSON.stringify(toolCall.arguments), partial: message});
              stream.push({type: 'toolcall_end', contentIndex: 0, toolCall, partial: message});
              message.stopReason = 'toolUse';
            } else if (first) {
              const tool = callback === 'claim' ? {name: 'write', arguments: {path: 'steering-owned.txt', content: 'offline fixture\n'}}
                : callback === 'command' ? {name: 'bash', arguments: {command: 'true'}}
                  : {name: 'ask_owner', arguments: {question: 'fixture callback'}};
              const toolCall = {type: 'toolCall', id: 'callback-tool', ...tool};
              message.content.push(toolCall);
              stream.push({type: 'toolcall_start', contentIndex: 0, partial: message});
              stream.push({type: 'toolcall_delta', contentIndex: 0, delta: JSON.stringify(tool.arguments), partial: message});
              stream.push({type: 'toolcall_end', contentIndex: 0, toolCall, partial: message});
              if (pauseFixture) {
                const premature = {type: 'toolCall', id: 'premature-tool', name: 'write',
                  arguments: {path: 'premature.txt', content: 'must not run'}};
                message.content.push(premature);
                stream.push({type: 'toolcall_start', contentIndex: 1, partial: message});
                stream.push({type: 'toolcall_delta', contentIndex: 1, delta: JSON.stringify(premature.arguments), partial: message});
                stream.push({type: 'toolcall_end', contentIndex: 1, toolCall: premature, partial: message});
              }
              message.stopReason = 'toolUse';
            } else {
              const answerText = JSON.stringify(context.messages.filter(item => item.role === 'user').at(-1));
              const effectDone = context.messages.some(item => item.role === 'toolResult' && item.toolCallId === 'gated-tool');
              if (pauseFixture && !reviewer && answerText.includes('actual consent') && !effectDone) {
                const toolCall = {type: 'toolCall', id: 'gated-tool', name: 'write',
                  arguments: {path: 'steering-owned.txt', content: 'consented\n'}};
                message.content.push(toolCall);
                stream.push({type: 'toolcall_start', contentIndex: 0, partial: message});
                stream.push({type: 'toolcall_delta', contentIndex: 0, delta: JSON.stringify(toolCall.arguments), partial: message});
                stream.push({type: 'toolcall_end', contentIndex: 0, toolCall, partial: message});
                message.stopReason = 'toolUse';
              } else {
              if (pauseFixture && !reviewer) {
                const reply = context.messages.find(item => item.role === 'toolResult' && item.toolCallId === 'callback-tool');
                assert.ok(reply, 'saved question tool identity must survive reopen');
                const answer = context.messages.filter(item => item.role === 'user').at(-1);
                assert.match(JSON.stringify(answer), /actual consent|actual denial/, 'continuation must carry the actual answer');
              } else if (!reviewer && callback !== 'sync-question') {
                const directions = context.messages.filter(item => item.role === 'user' && JSON.stringify(item.content).includes('[owner-direction id='));
                assert.ok(directions.length, 'real SDK loop must consume queued direction before next provider request');
                const prompt = context.messages.find(item => item.role === 'user');
                const worker = JSON.stringify(prompt).match(/worker-[12]/)?.[0];
                if (worker) assert.ok(directions.every(item => JSON.stringify(item).includes(worker)), 'direction must reach only its selected context');
                const reply = context.messages.find(item => item.role === 'toolResult' && item.toolCallId === 'callback-tool');
                assert.ok(reply && !reply.isError, 'own tool reply must reach the SDK before direction consumption');
                if (worker) assert.ok(JSON.stringify(reply).includes(`answer-${worker}`), 'reply must reach its selected context');
              }
              const text = reviewer ? '{"approved":true,"findings":[]}' : 'steering complete';
              message.content.push({type: 'text', text});
              stream.push({type: 'text_start', contentIndex: 0, partial: message});
              stream.push({type: 'text_delta', contentIndex: 0, delta: text, partial: message});
              stream.push({type: 'text_end', contentIndex: 0, content: text, partial: message});
              message.stopReason = 'stop';
              }
            }
            Object.assign(message.usage, {input: 1, output: 1, totalTokens: 2});
            stream.push({type: 'done', reason: message.stopReason, message});
            stream.end();
          } catch (error) {
            message.stopReason = options?.signal?.aborted ? 'aborted' : 'error';
            message.errorMessage = String(error);
            stream.push({type: 'error', reason: message.stopReason, error: message});
            stream.end();
          }
        });
        return stream;
      },
    });
    return runtime;
  });
}

if (process.env.COHERENCE_HOST_PRELOAD === '1') {
  installSteeringProvider(process.env.COHERENCE_STEERING_CALLBACK ?? 'question');
}
