// Disposable SDK seam probe. No workflow routing or durable workflow state.
import fs from 'node:fs';
import path from 'node:path';
import readline from 'node:readline';
import {pathToFileURL} from 'node:url';
const root = path.resolve(process.env.POC_ROOT);
const pkg = path.resolve(process.env.PI_SDK_ROOT);
const version = JSON.parse(fs.readFileSync(path.join(pkg, 'package.json'))).version;
if (version !== '0.87.1') throw Error('SDK version mismatch');
const sdk = await import(pathToFileURL(path.join(pkg, 'dist/index.js')));
const emit = x => process.stdout.write(JSON.stringify({v:1, at:Date.now(), ...x})+'\n');
let session, active, poisoned=false, injection=false, wireCount=0, guardCount=0, transforms=0;
const nativeFetch = globalThis.fetch;
globalThis.fetch = (...args) => { wireCount++; return nativeFetch(...args); };
const response = (id, data) => emit({type:'response',id,ok:true,data});
function facts() {
  const stats=session.getSessionStats(), model=session.model;
  const effective=session.settingsManager.getCompactionSettings(model);
  const context=stats.contextUsage ?? null;
  const threshold=effective.enabled && model.contextWindow>0 ? model.contextWindow-effective.reserveTokens : null;
  return {sessionId:session.sessionId, model:{provider:model.provider,id:model.id,contextWindow:model.contextWindow,thinkingLevelMap:model.thinkingLevelMap ?? null},effort:session.thinkingLevel,
    tools:session.getActiveToolNames(),effective,context,tokens:stats.tokens,cost:stats.cost,
    threshold,headroom:threshold!==null && context?.tokens!=null ? threshold-context.tokens : null,
    provenance:'SDK getSessionStats.contextUsage current projected estimate; tokens cumulative; settingsManager.getCompactionSettings(session.model)',wireCount,guardCount,transforms,idle:session.isIdle};
}
async function init(c) {
  if(session) throw Error('already initialized');
  if(c.provider!=='openai-codex'||c.model!=='gpt-6.1-sol'||c.effort!=='medium') throw Error('unapproved profile');
  // Official public read helper; no file-backed credential store/refresh writes.
  const credential=sdk.readStoredCredential(c.provider,process.env.PI_AUTH_PATH);
  if(!credential || credential.type!=='oauth' || credential.expires<Date.now()+600000) throw Error('credential unavailable or near expiry; no refresh authorized');
  const credentials={read:async id=>id===c.provider?credential:undefined,
    list:async()=>[{providerId:c.provider,type:credential.type}],
    modify:async()=>{throw Error('credential mutation forbidden');},delete:async()=>{throw Error('credential mutation forbidden');}};
  // Restore the installed catalog read-only; this selected model is not in the
  // bundled static catalog. SDK may update only this private in-memory copy.
  const catalogs=new Map(Object.entries(JSON.parse(fs.readFileSync(process.env.PI_MODELS_STORE_PATH,'utf8'))));
  const modelsStore={read:async id=>catalogs.get(id),write:async(id,e)=>{catalogs.set(id,e);},delete:async id=>{catalogs.delete(id);}};
  const runtime=await sdk.ModelRuntime.create({credentials,modelsStore,modelsPath:null,allowModelNetwork:false});
  const model=runtime.getModel(c.provider,c.model);
  if(!model) throw Error('exact model unavailable');
  const settings=sdk.SettingsManager.inMemory({cacheWarming:'off',transport:'sse',enableInstallTelemetry:false,
    compaction:{enabled:true,reserveTokens:9999,keepRecentTokens:20000,modelOverrides:{[`${c.provider}/${c.model}`]:{reserveTokens:16384}}},
    retry:{enabled:false,provider:{maxRetries:0,timeoutMs:30000}}});
  const skills=sdk.loadSkills({cwd:root,agentDir:path.join(root,'agent'),skillPaths:[c.skill],includeDefaults:false});
  if(skills.diagnostics.length || skills.skills.length!==1) throw Error('skill load failed');
  const loader=new sdk.DefaultResourceLoader({cwd:root,agentDir:path.join(root,'agent'),settingsManager:settings,
    noExtensions:true,noSkills:true,noPromptTemplates:true,noThemes:true,noContextFiles:true,
    skillsOverride:()=>skills,
    systemPrompt:`You are a tiny toy-file worker. Only change files within ${root}. Never run git. Follow explicit task and stop.`,
    extensionFactories:[pi=>{
      pi.on('before_provider_request',e=>{transforms++; const p={...e.payload,text:{...e.payload.text,verbosity:'low'}};
        if(injection) p.reasoning={...p.reasoning,effort:'high'}; return p;});
      pi.on('before_provider_request',()=>{if(injection) {emit({type:'synthetic_extension_throw',id:active});throw Error('synthetic swallowed extension error');}});
    }]});
  await loader.reload();
  const result=await sdk.createAgentSession({cwd:root,agentDir:path.join(root,'agent'),modelRuntime:runtime,model,
    thinkingLevel:c.effort,settingsManager:settings,resourceLoader:loader,tools:c.tools,
    sessionManager:sdk.SessionManager.create(root,path.join(root,'sessions'))});
  session=result.session;
  if(result.modelFallbackMessage || session.thinkingLevel!==c.effort) throw Error('fallback/clamp forbidden');
  const expectedWireEffort=model.thinkingLevelMap?.[c.effort] ?? c.effort;
  const originalStream=session.agent.streamFunction;
  const originalTransform=session.agent.onPayload;
  // streamFunction is public. Covers session AND summarization calls, which do
  // not inherit agent.onPayload. Existing per-call transforms run before guard.
  session.agent.streamFunction=(m,context,options={})=>originalStream(m,context,{...options,
    transport:'sse',maxRetries:0,onPayload:async(payload,requestModel)=>{
      const transform=options.onPayload ?? originalTransform;
      const transformed=(await transform?.(payload,requestModel)) ?? payload;
      guardCount++;
      const observed={model:transformed.model,effort:transformed.reasoning?.effort ?? null};
      const valid=m.provider===c.provider && m.id===c.model && observed.model===c.model && observed.effort===expectedWireEffort;
      emit({type:'outbound_guard',id:active,synthetic:injection,observed,expected:{model:c.model,effort:expectedWireEffort},valid,guardCount,wireCount,transforms});
      if(!valid) throw Error('OUTBOUND_BINDING_MISMATCH');
      return transformed;
    }});
  session.subscribe(e=>{
    if(['agent_start','agent_end','agent_settled','tool_execution_start','tool_execution_end','auto_compaction_start','auto_compaction_end','auto_retry_start'].includes(e.type))
      emit({type:'event',id:active,event:e.type,tool:e.toolName ?? null});
  });
  return {sdk:version,node:process.version,skill:skills.skills.map(s=>({name:s.name,filePath:s.filePath})),requested:c,...facts()};
}
async function command(c) {
  if(c.v!==1 || typeof c.id!=='string') throw Error('protocol version/id mismatch');
  if(poisoned && c.op!=='close' && c.op!=='status') throw Error('poisoned; reconcile first');
  if(c.op==='init') return response(c.id,await init(c));
  if(c.op==='close' && !session) {response(c.id,{closed:true});process.exit(0);}
  if(!session) throw Error('not initialized');
  if(c.op==='status') return response(c.id,facts());
  if(c.op==='close') {await session.abort();await session.waitForIdle();session.dispose();response(c.id,{closed:true});process.exit(0);}
  if(c.op==='abort') {emit({type:'abort_requested',id:c.id,active});await session.abort();await session.waitForIdle();return response(c.id,{settled:true,...facts()});}
  if(c.op==='prompt') {
    if(active) throw Error('writer active');
    active=c.id;response(c.id,{accepted:true});
    try {
      await session.prompt(c.text); await session.waitForIdle();
      const last=[...session.messages].reverse().find(m=>m.role==='assistant');
      const successful=last?.stopReason==='stop';
      const marker=session.getLastAssistantText()?.trim()==='SDK_SKILL_OBSERVED';
      if(!successful && last?.stopReason!=='aborted') poisoned=true;
      emit({type:'settled',id:c.id,successful,stopReason:last?.stopReason ?? null,skillMarker:marker,...facts()});
    } catch {poisoned=true;emit({type:'settled',id:c.id,successful:false,error:'prompt exception; reconcile',...facts()});}
    finally {active=undefined;}
    return;
  }
  if(c.op==='synthetic_guard') {
    if(active) throw Error('writer active');
    injection=true; const startWire=wireCount, startGuard=guardCount;
    // Instrument transport to prove zero sends, even if a regression breaks guard.
    globalThis.fetch=async()=>{wireCount++;throw Error('SYNTHETIC_TRANSPORT_SENTINEL');};
    try {
      active=c.id;
      await session.prompt('Write forbidden.txt with bad.'); await session.waitForIdle();
      const last=[...session.messages].reverse().find(m=>m.role==='assistant');
      const normal={stopReason:last?.stopReason,errorMatched:last?.errorMessage?.includes('OUTBOUND_BINDING_MISMATCH')===true};
      // Rare sequencing fixture: real SDK stream function called as summary route
      // (no onPayload in options), official provider builds actual wire body.
      const stream=await session.agent.streamFunction(session.model,{messages:[{role:'user',content:'Synthetic summary',timestamp:Date.now()}]},
        {reasoning:'medium',sessionId:'synthetic-summary',apiKey:credentialForFixture(),transport:'sse'});
      const summary=await stream.result();
      const data={synthetic:true,normal,summary:{stopReason:summary.stopReason,errorMatched:summary.errorMessage?.includes('OUTBOUND_BINDING_MISMATCH')===true},
        sends:wireCount-startWire,guards:guardCount-startGuard,forbiddenExists:fs.existsSync(path.join(root,'forbidden.txt'))};
      poisoned=true;response(c.id,data);
    } finally {injection=false;active=undefined;globalThis.fetch=(...args)=>{wireCount++;return nativeFetch(...args);};}
    return;
  }
  throw Error('unknown operation');
}
function credentialForFixture(){return 'synthetic.'+Buffer.from(JSON.stringify({'https://api.openai.com/auth':{chatgpt_account_id:'synthetic-account'}})).toString('base64url')+'.fixture';}
const rl=readline.createInterface({input:process.stdin,crlfDelay:Infinity});
rl.on('line',line=>{
  if(Buffer.byteLength(line)>16384){poisoned=true;emit({type:'error',error:'oversize'});return;}
  let c;try{c=JSON.parse(line);}catch{poisoned=true;emit({type:'error',error:'invalid JSON'});return;}
  command(c).catch(e=>{poisoned=true;process.stderr.write(`${c.op}: ${e.message}\n`);emit({type:'response',id:c.id,ok:false,error:'command failed closed'});});
});
rl.on('close',async()=>{poisoned=true;if(session){await session.abort();await session.waitForIdle();session.dispose();}process.exit(0);});
