// T002 shipped host tests. Offline guards use real provider builder, fake credential,
// counting fetch sentinel; live mode is explicitly opt-in and uses actual credentials.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { test } from 'node:test';
import { createHost, guardedStream, observer, Decoder, hash } from '../pi-host/host.mjs';
import { createAgentSession, DefaultResourceLoader, ModelRuntime, SettingsManager, SessionManager,
  shouldCompact } from '../pi-host/node_modules/@earendil-works/pi-coding-agent/dist/index.js';
import { stream } from '../pi-host/node_modules/@earendil-works/pi-coding-agent/node_modules/@earendil-works/pi-ai/dist/api/openai-codex-responses.js';
const profile={provider:'openai-codex',model:'gpt-6.1-sol',effort:'medium',observer_id:'codex-final-payload',observer_version:'1'};
const model={provider:'openai-codex',id:'gpt-6.1-sol',api:'openai-codex-responses',baseUrl:'https://invalid.invalid',
  reasoning:true,contextWindow:500000,maxTokens:32000,input:['text'],cost:{input:0,output:0,cacheRead:0,cacheWrite:0}};
const token=['e30',Buffer.from(JSON.stringify({'https://api.openai.com/auth':{chatgpt_account_id:'offline-fixture'}})).toString('base64url'),'signature'].join('.');

test('bounded UTF8 decoder and exact observer reject unsupported mappings',()=>{
  const records=[];const decoder=new Decoder(v=>records.push(v),10);
  decoder.feed(Buffer.from('{"a":'));decoder.feed(Buffer.from('1}\n'));decoder.end();assert.deepEqual(records,[{a:1}]);
  assert.throws(()=>decoder.feed(Buffer.alloc(11,65)),/too large/);
  const invalid=new Decoder(()=>{});assert.throws(()=>invalid.feed(Buffer.from([255,10])));
  assert.throws(()=>observer({...profile,effort:'high'}),/unsupported/);
  assert.throws(()=>observer({...profile,observer_id:'unknown'}),/unsupported/);
  assert.throws(()=>observer({...profile,observer_version:'2'}),/unsupported/);
});

test('version, settings, trust and unsupported exact profile fail before provider access',async()=>{
  const config=JSON.parse(fs.readFileSync(process.env.COHERENCE_HOST_MANIFEST,'utf8'));
  let sends=0;const before=globalThis.fetch;globalThis.fetch=async()=>{sends++;throw Error('zero-send sentinel');};
  try {
    for(const patch of [{sdk_version:'0.88.0'},{profile:{...profile,effort:'high'}},
      {profile:{...profile,observer_id:'unknown'}},{settings_hash:'wrong'},{trust:'global-override'}]) {
      await assert.rejects(createHost({...config,...patch},()=>{},async()=>{}));
    }
    const fake={thinkingLevel:'high',agent:{streamFunction:()=>assert.fail('runtime mismatch reached builder')}};
    assert.throws(()=>guardedStream(fake,profile,()=>{})(model,{messages:[]}),/runtime binding mismatch/);
    assert.equal(sends,0);
  }finally{globalThis.fetch=before;}
});

test('actual SettingsManager merge, model override and effective threshold, no writes',()=>{
  let writes=0;
  const global={compaction:{enabled:true,reserveTokens:16000,modelOverrides:{'openai-codex/gpt-6.1-sol':{reserveTokens:20000}}}};
  const project={compaction:{reserveTokens:10000,keepRecentTokens:3000}};
  const settings=SettingsManager.fromStorage({withLock(scope,fn){if(fn(JSON.stringify(scope==='global'?global:project))!==undefined)writes++;}},{projectTrusted:true});
  const effective=settings.getCompactionSettings(model);
  assert.equal(effective.reserveTokens,20000);assert.equal(effective.keepRecentTokens,3000);
  assert.equal(settings.getCompactionSettings({...model,id:'other'}).reserveTokens,10000);
  assert.equal(shouldCompact(480000,500000,effective),false);assert.equal(shouldCompact(480001,500000,effective),true);
  assert.equal(shouldCompact(999999,500000,{...effective,enabled:false}),false);
  assert.throws(()=>SettingsManager.inMemory({compaction:{reserveTokens:-1}}).getCompactionSettings(model));
  assert.equal(writes,0);
});

test('final guard uses actual provider builder, per-call before guard, summary SDK hook fallback; zero sends',async()=>{
  let sends=0,transforms=0;
  const fetchBefore=globalThis.fetch;
  globalThis.fetch=async()=>{sends++;throw new Error('counting offline transport');};
  try {
    for(const summary of [false,true]) {
      const fake={thinkingLevel:'medium',agent:{streamFunction:(m,c,o)=>stream(m,c,{...o,apiKey:token,reasoningEffort:'medium',transport:'sse',maxRetries:0}),
        onPayload:async payload=>{transforms++;return {...payload,reasoning:{effort:'high'}};}}};
      const guarded=guardedStream(fake,profile,()=>assert.fail('mismatch must not be observed valid'));
      const response=await guarded(model,{messages:[{role:'user',content:'offline',timestamp:0}]},
        summary?{}:{onPayload:fake.agent.onPayload}).result();
      assert.equal(response.stopReason,'error');assert.match(response.errorMessage,/binding mismatch/);
    }
    assert.equal(transforms,2);assert.equal(sends,0);
    console.log(JSON.stringify({proof:'actual-provider-builder-normal-summary',transforms,sends}));
  }finally{globalThis.fetch=fetchBefore;}
});

test('actual SDK swallowed extension throw cannot bypass final guard',async()=>{
  const root=process.env.COHERENCE_NODE_FIXTURE;
  assert.ok(root,'isolated fixture required');
  let swallowed=0,sends=0;
  const fetchBefore=globalThis.fetch;
  globalThis.fetch=async()=>{sends++;throw new Error('offline sentinel');};
  const settings=SettingsManager.inMemory({compaction:{enabled:false},cacheWarming:'off',retry:{enabled:false},transport:'sse'});
  const runtime=await ModelRuntime.create({credentials:{read:async provider=>provider==='openai-codex'?({type:'oauth',access:token,refresh:'offline',expires:Date.now()+3600000}):undefined,list:async()=>[{providerId:'openai-codex',type:'oauth'}],modify:async()=>{throw Error('no writes');},delete:async()=>{}},modelsPath:null,allowModelNetwork:false});
  const loader=new DefaultResourceLoader({cwd:root,agentDir:root,settingsManager:settings,noContextFiles:true,noSkills:true,noPromptTemplates:true,noThemes:true,
    extensionFactories:[pi=>{
      pi.on('before_provider_request',event=>({...event.payload,reasoning:{effort:'high'}}));
      pi.on('before_provider_request',()=>{swallowed++;throw Error('deliberate extension throw');});
    }]});
  await loader.reload();
  const {session}=await createAgentSession({cwd:root,agentDir:root,modelRuntime:runtime,model,thinkingLevel:'medium',settingsManager:settings,
    resourceLoader:loader,sessionManager:SessionManager.inMemory(root),tools:[]});
  session.agent.streamFunction=guardedStream(session,profile,()=>assert.fail('guard bypass'));
  try {
    await session.prompt('offline fixture');
    assert.equal(session.messages.at(-1).stopReason,'error');
    assert.equal(swallowed,1);assert.equal(sends,0);
    console.log(JSON.stringify({proof:'actual-sdk-extension-swallowed-throw',swallowed,sends}));
  }finally{session.dispose();globalThis.fetch=fetchBefore;}
});

if(process.env.COHERENCE_LIVE==='1') {
  test('authorized actual shipped summary and SDK agent retry path with injected transient 503, no pressure token burn',async()=>{
    const config=JSON.parse(fs.readFileSync(process.env.COHERENCE_HOST_MANIFEST,'utf8'));
    const trace=[];let sends=0,inject=false,injected=0;
    const fetchBefore=globalThis.fetch;
    globalThis.fetch=async(...args)=>{
      sends++;
      if(inject){inject=false;injected++;return new Response(JSON.stringify({error:{message:'controlled transient overloaded'}}),{status:503});}
      return fetchBefore(...args);
    };
    const host=await createHost(config,e=>trace.push(e),async()=>{throw Error('no tools in summary fixture');});
    try {
      inject=true;
      await host.run({text:'Reply with the skill marker only.',skill:config.skills[0].name,generation:1});
      assert.equal(injected,1);
      assert.ok(trace.some(e=>e.type==='auto_retry_start'),'actual SDK retry not observed');
      assert.ok(trace.some(e=>e.type==='auto_retry_end'));
      const summary=await host.compact('Preserve the marker only. Be very concise.');
      assert.ok(summary.summary_entries>0,'actual SDK compaction entry required');
      assert.ok(summary.summary_usage.some(u=>u?.totalTokens>0),'actual summary provider usage required');
      assert.equal(summary.occupancy,null,'post-compaction occupancy must not reuse old billing counters');
      assert.ok(host.poisoned,'compaction does not authorize session reuse');
      const observations=trace.filter(e=>e.type==='request_observation');
      assert.ok(observations.length>=3);
      assert.equal(sends,3,'503 fixture + actual retry + actual summary via SSE');
      assert.ok(observations.every(e=>e.model===profile.model && e.wire_effort==='medium'));
      console.log(JSON.stringify({proof:'live-sdk-summary-retry',injected_fault:'503-once',actual_sdk_retry:true,
        events:trace.map(({type,generation,model,wire_effort})=>({type,generation,model,wire_effort})),summary,sends}));
    }finally{
      console.log(JSON.stringify({proof:'summary-retry-trace',sends,injected,events:trace.map(e=>({type:e.type,generation:e.generation}))}));
      await host.close();globalThis.fetch=fetchBefore;
    }
  });
}
