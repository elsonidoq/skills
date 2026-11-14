// Local provider responses only. SDK prompt, tools, steer queue and events stay real.
import assert from 'node:assert/strict';
import {mock} from 'node:test';
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
            const first = (pauseFixture ? !priorQuestion : calls++ === 0) && !reviewer;
            stream.push({type: 'start', partial: message});
            if (callback === 'graph-pause' && !reviewer && !priorEffect) {
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
              } else if (!reviewer) {
                const directions = context.messages.filter(item => item.role === 'user' && JSON.stringify(item.content).includes('[owner-direction id='));
                assert.ok(directions.length, 'real SDK loop must consume queued direction before next provider request');
                const reply = context.messages.find(item => item.role === 'toolResult' && item.toolCallId === 'callback-tool');
                assert.ok(reply && !reply.isError, 'own tool reply must reach the SDK before direction consumption');
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
