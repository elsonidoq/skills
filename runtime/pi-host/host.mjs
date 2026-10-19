// Thin pinned SDK host. No workflow selection, approval, Git or local process tools.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { createAgentSession, createExtensionRuntime, ModelRuntime, SessionManager,
  SettingsManager, loadSkills } from '@earendil-works/pi-coding-agent';

export const VERSION = '0.87.1';
export const MAX_RECORD = 262144;
const canonical = v => Array.isArray(v) ? v.map(canonical) : v && typeof v==='object' ? Object.fromEntries(Object.keys(v).sort().map(k=>[k,canonical(v[k])])) : v;
export const hash = v => crypto.createHash('sha256').update(typeof v === 'string' ? v : JSON.stringify(canonical(v))).digest('hex');
const check = (ok, reason) => { if (!ok) { const error=new Error(reason);error.safeCode=reason;throw error; } };
export function closed(value, required, optional=[]) {
  check(value && typeof value==='object' && !Array.isArray(value), 'object required');
  check(required.every(k=>Object.hasOwn(value,k)) && Object.keys(value).every(k=>[...required,...optional].includes(k)), 'closed payload mismatch');
}
export class Decoder {
  constructor(consume, limit=MAX_RECORD) { this.buffer=Buffer.alloc(limit); this.used=0; this.consume=consume; }
  feed(chunk) {
    for (const byte of chunk) {
      if (byte===10) {
        check(this.used>0,'empty record');
        const text=new TextDecoder('utf-8',{fatal:true}).decode(this.buffer.subarray(0,this.used));
        this.used=0; this.consume(JSON.parse(text));
      } else {
        check(this.used<this.buffer.length,'record too large'); this.buffer[this.used++]=byte;
      }
    }
  }
  end() { check(this.used===0,'incomplete record'); }
}
export function observer(profile) {
  closed(profile,['provider','model','effort','observer_id','observer_version']);
  check(profile.observer_id==='codex-final-payload' && profile.observer_version==='1' && profile.provider==='openai-codex' &&
    profile.model==='gpt-6.1-sol' && profile.effort==='medium','unsupported exact binding/observer');
  return body => {
    const observation={provider:profile.provider,model:body?.model??null,
      wire_effort:body?.reasoning?.effort??null,mapping:profile.observer_id+':'+profile.observer_version};
    check(observation.model===profile.model && observation.wire_effort===profile.effort,'final binding mismatch');
    return observation;
  };
}
export function guardedStream(session, profile, record, admitted=()=>true) {
  const validate=observer(profile), original=session.agent.streamFunction;
  return (model, context, options={}) => {
    check(admitted(),'request outside active operation');
    check(model.provider===profile.provider && model.id===profile.model && session.thinkingLevel===profile.effort,'runtime binding mismatch');
    check(options.transport===undefined || options.transport==='sse','transport settings override');
    check(options.maxRetries===undefined || options.maxRetries===0,'hidden provider retries forbidden');
    const transform=options.onPayload ?? session.agent.onPayload;
    return original(model,context,{...options,transport:'sse',maxRetries:0,onPayload:async payload=>{
      const transformed=transform ? (await transform(payload,model) ?? payload) : payload;
      // Deliberately outside extension runner's swallowed exception boundary.
      const observation=validate(transformed);
      check(admitted(),'request admission revoked');
      record(observation,transformed);
      return transformed;
    }});
  };
}
function canonicalDirectory(p) {
  check(typeof p==='string' && path.isAbsolute(p) && fs.realpathSync(p)===p,'noncanonical directory');
  check(fs.statSync(p).isDirectory(),'directory required'); return p;
}
function readBounded(p, maximum=MAX_RECORD) {
  const fd=fs.openSync(p,fs.constants.O_RDONLY|fs.constants.O_NOFOLLOW);
  try {
    const s=fs.fstatSync(fd); check(s.isFile() && s.size<=maximum,'invalid resource size/type');
    return fs.readFileSync(fd,'utf8');
  } finally { fs.closeSync(fd); }
}
export async function createHost(config, emit, proxy) {
  closed(config,['sdk_version','cwd','agent_dir','session_dir','profile','skills','tools','settings','settings_hash',
    'trust','permissions','resource_hash','auth_path','catalog_path','system_prompt','pressure_policy'],['open']);
  check(config.sdk_version===VERSION,'unsupported SDK version');
  const [major,minor,patch]=process.versions.node.split('.').map(Number);
  check(major===22 && (minor>23 || minor===23 && patch>=3),'unsupported Node version');
  const packageVersion=JSON.parse(readBounded(new URL('./node_modules/@earendil-works/pi-coding-agent/package.json',import.meta.url))).version;
  check(packageVersion===VERSION,'installed SDK version mismatch');
  observer(config.profile);
  canonicalDirectory(config.cwd); canonicalDirectory(config.agent_dir); canonicalDirectory(config.session_dir);
  check(config.trust==='explicit-resources-only','unsupported trust');
  check(hash(config.settings)===config.settings_hash,'settings hash mismatch');
  closed(config.settings,['compaction','retry','cacheWarming','transport']);
  check(config.settings.cacheWarming==='off' && config.settings.transport==='sse','background/transport override');
  closed(config.settings.retry,['enabled','maxRetries','baseDelayMs','provider']);
  check(Number.isSafeInteger(config.settings.retry.maxRetries) && config.settings.retry.maxRetries>=0 &&
    config.settings.retry.maxRetries<=3 && config.settings.retry.provider.maxRetries===0,'unsupported retry policy');
  check(Array.isArray(config.permissions) && config.permissions.every(x=>typeof x==='string'),'permissions required');
  const credentials=JSON.parse(readBounded(config.auth_path));
  const credential=credentials[config.profile.provider];
  check(credential?.type==='oauth' && credential.expires>Date.now()+300000,'credential unavailable/expired; refresh forbidden');
  const credentialStore={
    read:async provider=>{ if(provider!==config.profile.provider)return undefined;check(credential.expires>Date.now()+300000,'credential expiry'); return structuredClone(credential); },
    list:async()=>[{providerId:config.profile.provider,type:'oauth'}],
    modify:async()=>{ throw new Error('credential modification/refresh forbidden'); },
    delete:async()=>{ throw new Error('credential deletion forbidden'); },
  };
  const catalog=JSON.parse(readBounded(config.catalog_path,4*1024*1024));
  const modelsStore={read:async provider=>structuredClone(catalog[provider]),
    write:async()=>{throw new Error('catalog write forbidden');},delete:async()=>{throw new Error('catalog delete forbidden');}};
  const runtime=await ModelRuntime.create({credentials:credentialStore,modelsStore,modelsPath:null,allowModelNetwork:false});
  check(!runtime.getError(),'model runtime unavailable');
  const model=runtime.getModel(config.profile.provider,config.profile.model);
  check(model && model.api==='openai-codex-responses','exact cached model unavailable');
  closed(config.pressure_policy,['min_free_tokens_before_compaction','monitor_interval_ms']);
  check(Number.isSafeInteger(config.pressure_policy.min_free_tokens_before_compaction) && config.pressure_policy.min_free_tokens_before_compaction>=0 &&
    Number.isSafeInteger(config.pressure_policy.monitor_interval_ms) && config.pressure_policy.monitor_interval_ms>=10 && config.pressure_policy.monitor_interval_ms<=10000,'invalid pressure policy');
  const settings=SettingsManager.inMemory(config.settings);
  const skills=[];
  for (const resource of config.skills) {
    closed(resource,['path','sha256','name']);
    check(fs.realpathSync(resource.path)===resource.path && hash(readBounded(resource.path))===resource.sha256,'skill identity mismatch');
    const loaded=loadSkills({cwd:config.cwd,agentDir:config.agent_dir,skillPaths:[resource.path],includeDefaults:false});
    check(!loaded.diagnostics.length && loaded.skills.length===1 && loaded.skills[0].name===resource.name,'skill load mismatch');
    skills.push(loaded.skills[0]);
  }
  check(hash({skills:config.skills,tools:config.tools,permissions:config.permissions,trust:config.trust,system_prompt:config.system_prompt})===config.resource_hash,'resource manifest mismatch');
  const names=new Set();
  const customTools=config.tools.map(tool=>{
    closed(tool,['name','version','description','parameters','permission']);
    check(/^[a-z][a-z0-9_]{0,63}$/.test(tool.name) && !['bash','powershell','git','ask_user','edit','write','request_owner_input'].includes(tool.name) &&
      !names.has(tool.name) && config.permissions.includes(tool.permission),'unapproved tool');
    names.add(tool.name);
    return {name:tool.name,label:tool.name,description:tool.description,parameters:tool.parameters,
      execute:async(call,args,signal)=>proxy({call,tool:tool.name,version:tool.version,args},signal)};
  });
  const loader={getExtensions:()=>({extensions:[],errors:[],runtime:createExtensionRuntime()}),
    getSkills:()=>({skills,diagnostics:[]}),getPrompts:()=>({prompts:[],diagnostics:[]}),
    getThemes:()=>({themes:[],diagnostics:[]}),getAgentsFiles:()=>({agentsFiles:[]}),
    getSystemPrompt:()=>config.system_prompt,getSystemPromptSource:()=>undefined,
    getAppendSystemPrompt:()=>[],getAppendSystemPromptSources:()=>[],extendResources:()=>{},reload:async()=>{}};
  let manager;
  if (config.open) {
    closed(config.open,['file','session_id','leaf','sha256']);
    check(path.dirname(config.open.file)===config.session_dir && hash(readBounded(config.open.file,16*1024*1024))===config.open.sha256,'saved conversation identity mismatch');
    manager=SessionManager.open(config.open.file,config.session_dir,config.cwd);
    check(manager.getSessionId()===config.open.session_id && manager.getLeafId()===config.open.leaf && manager.getCwd()===config.cwd,'saved conversation branch mismatch');
    const context=manager.buildSessionContext();
    check(context.model?.provider===config.profile.provider && context.model?.modelId===config.profile.model && context.thinkingLevel===config.profile.effort,'saved conversation profile mismatch');
  } else manager=SessionManager.create(config.cwd,config.session_dir);
  const result=await createAgentSession({cwd:config.cwd,agentDir:config.agent_dir,modelRuntime:runtime,model,
    thinkingLevel:config.profile.effort,settingsManager:settings,sessionManager:manager,resourceLoader:loader,
    tools:[...names],customTools});
  const session=result.session;
  check(!result.modelFallbackMessage && session.model?.id===model.id && session.model.provider===model.provider && session.thinkingLevel===config.profile.effort,'fallback/clamped binding');
  check(JSON.stringify(session.getActiveToolNames().sort())===JSON.stringify([...names].sort()),'active tools mismatch');
  const epoch=crypto.randomUUID();
  let generation=0, active=false, poisoned=false, started=false, settled=false, promiseDone=false, mode=null;
  let requestSequence=0, acknowledged=null,invokedSkill=null;
  const notify=(type,data={})=>emit({type,generation,...data});
  session.subscribe(event=>{
    if (event.type==='agent_start') { started=true; settled=false; }
    if (event.type==='agent_settled' && started && active) settled=true;
    if (event.type==='message_end' && event.message.role==='assistant') {
      const m=event.message;
      acknowledged={model:m.responseModel??null,effort:m.providerThinkingLevel??null};
      if (['error','aborted'].includes(m.stopReason)) {
        const reason=['skill not expanded into current prompt','final tool binding mismatch','final binding mismatch','request admission revoked',
          'runtime binding mismatch','transport settings override','hidden provider retries forbidden'].find(code=>m.errorMessage?.includes(code))??'provider_or_sdk_failure';
        notify('assistant_failure',{stop_reason:m.stopReason,reason});
      }
    }
    if (['agent_start','agent_end','agent_settled','compaction_start','compaction_end','auto_retry_start','auto_retry_end',
      'tool_execution_start','tool_execution_end','summarization_retry_scheduled','summarization_retry_finished'].includes(event.type)) {
      if (['compaction_start','auto_retry_start'].includes(event.type)) settled=false;
      notify(event.type);
    }
  }); // Subscription precedes every possible prompt.
  function pressureReason() {
    const effective=settings.getCompactionSettings(session.model),usage=session.getContextUsage();
    if (!effective.enabled || usage?.tokens==null || !Number.isSafeInteger(usage.contextWindow)) return 'unknown_pressure_telemetry';
    return usage.contextWindow-effective.reserveTokens-usage.tokens<config.pressure_policy.min_free_tokens_before_compaction ? 'low_headroom' : null;
  }
  const monitor=setInterval(()=>{
    if(active && mode==='prompt' && !poisoned) {
      let reason;try{reason=pressureReason();}catch(_){reason='unknown_pressure_telemetry';}
      if(reason){poisoned=true;notify('pressure',{reason});void session.abort().catch(()=>{});}
    }
  },config.pressure_policy.monitor_interval_ms);
  monitor.unref();
  session.agent.streamFunction=guardedStream(session,config.profile,(observation,body)=>{
    const outgoingTools=(body.tools??[]).map(t=>t.name).sort();
    check(JSON.stringify(outgoingTools)===JSON.stringify(mode==='summary'?[]:[...names].sort()),'final tool binding mismatch');
    const latestUser=[...session.messages].reverse().find(m=>m.role==='user');
    const textOf=content=>typeof content==='string'?content:(content??[]).filter(b=>b.type==='text'||b.type==='input_text').map(b=>b.text??'').join('\n');
    const expanded=textOf(latestUser?.content);
    const delivered=(body.input??[]).filter(m=>m.role==='user').map(m=>textOf(m.content));
    const skillExpanded=mode==='prompt' && invokedSkill!==null && expanded.includes(`<skill name="${invokedSkill}"`) && delivered.some(text=>text.includes(expanded));
    check(mode==='summary' || skillExpanded,'skill not expanded into current prompt');
    notify('request_observation',{...observation,outgoing_tools:outgoingTools,skill_expanded:skillExpanded,
      expanded_prompt_hash:mode==='prompt'?hash(expanded):null,request_sequence:++requestSequence});
  },()=>active && !poisoned && (mode==='summary' || pressureReason()===null));
  function telemetry() {
    check(!active && !poisoned,'telemetry requires known settled idle boundary');
    const effective=settings.getCompactionSettings(session.model), usage=session.getContextUsage();
    const threshold=effective.enabled && Number.isSafeInteger(usage?.contextWindow) ? usage.contextWindow-effective.reserveTokens : null;
    const occupancy=usage?.tokens??null;
    return {session_id:session.sessionId,session_file:session.sessionFile,
      session_file_hash:session.sessionFile && fs.existsSync(session.sessionFile)?hash(readBounded(session.sessionFile,16*1024*1024)):null,leaf:manager.getLeafId(),
      branch:session.sessionId,epoch,generation,observed_ns:Date.now()*1000000,reliable:occupancy!==null && threshold>0,
      enabled:effective.enabled,threshold,occupancy,headroom:threshold!==null && occupancy!==null ? threshold-occupancy:null,
      provenance:'pi-0.87.1/SettingsManager.getCompactionSettings(model)/AgentSession.getContextUsage',
      effective_compaction:effective,settings_hash:config.settings_hash,resource_hash:config.resource_hash,
      counters:session.getSessionStats().tokens,cost:session.getSessionStats().cost,
      requested:config.profile,runtime:{provider:session.model.provider,model:session.model.id,effort:session.thinkingLevel},
      provider_acknowledged:acknowledged,skills:config.skills.map(s=>({name:s.name,sha256:s.sha256})),
      tools:session.getActiveToolNames(),system_prompt_hash:hash(session.systemPrompt),sdk_version:VERSION};
  }
  async function run(prompt) {
    closed(prompt,['text','skill','generation']);
    check(!active && !poisoned && prompt.generation===generation+1,'prompt generation/phase');
    check(skills.some(s=>s.name===prompt.skill) && !prompt.text.startsWith('/'),'explicit skill required');
    for (const resource of config.skills) check(hash(readBounded(resource.path))===resource.sha256,'skill drift');
    generation=prompt.generation; active=true; mode='prompt';invokedSkill=prompt.skill; started=false; settled=false; promiseDone=false;
    try {
      await session.prompt(`/skill:${prompt.skill} ${prompt.text}`); promiseDone=true;
      await session.waitForIdle();
      check(promiseDone && started && settled && !session.isStreaming && !session.isCompacting && session.pendingMessageCount===0,'incomplete SDK settlement');
      const last=[...session.messages].reverse().find(m=>m.role==='assistant');
      check(last && !['error','aborted','length'].includes(last.stopReason),'assistant unsuccessful');
      active=false;mode=null;
      const snapshot=telemetry();
      notify('settled',{snapshot,output:session.getLastAssistantText()??'',promise_done:true,idle:true});
      return snapshot;
    } catch (_) { poisoned=true; notify('poisoned',{reason:'prompt_failed_or_interrupted'}); throw new Error('prompt failed; reconciliation required'); }
    finally { active=false;mode=null; }
  }
  async function abort() {
    poisoned=true; await session.abort(); await session.waitForIdle();
    check(!session.isStreaming && !session.isCompacting && session.pendingMessageCount===0,'abort idle unknown');
    notify('drained',{idle:true,task_tools_quiescent:null});
    // SDK idle is not a cgroup empty/file reconciliation receipt.
    return {idle:true,task_tools_quiescent:null,poisoned:true};
  }
  async function compact(instructions) {
    check(!active && !poisoned,'summary boundary unavailable');
    generation++;active=true;mode='summary';
    try { await session.compact(instructions); await session.waitForIdle(); }
    finally { active=false;mode=null;poisoned=true; }
    return {summary_entries:manager.getEntries().filter(e=>e.type==='compaction').length,
      request_sequence:requestSequence,occupancy:session.getContextUsage()?.tokens??null,
      summary_usage:manager.getEntries().filter(e=>e.type==='compaction').map(e=>e.usage??null)};
  }
  return {session,telemetry,run,abort,compact,get active(){return active;},get generation(){return generation;},
    get poisoned(){return poisoned;},get mode(){return mode;},close:async()=>{clearInterval(monitor);await abort();session.dispose();}};
}

async function main() {
  process.umask(0o077);
  const [bootstrapFd,inputFd,outputFd]=process.argv.slice(2).map(Number);
  for (const fd of [bootstrapFd,inputFd,outputFd]) check(Number.isInteger(fd) && fd>2 && fs.fstatSync(fd).isFIFO(),'inherited pipes required');
  const boot=Buffer.alloc(MAX_RECORD);let used=0;
  for (;;) {
    check(used<MAX_RECORD,'bootstrap too large');
    const n=fs.readSync(bootstrapFd,boot,used,MAX_RECORD-used,null);
    if (!n) break; used+=n;
  }
  fs.closeSync(bootstrapFd);
  const binding=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(boot.subarray(0,used)));
  closed(binding,['host_id','run_id','nonce']);
  let outbound=0,inbound=0,current=null,host=null,creating=false;
  const ids=new Set(), tools=new Map();
  function send(type,payload,command=current) {
    check(command,'missing command binding');
    const record={protocol_version:1,...binding,sequence:++outbound,command_id:command.command_id,
      operation_id:command.operation_id,attempt_id:command.attempt_id,session_id:host?.session.sessionId??null,
      type,op:command.op,payload_schema:'sdk-v1',payload:{generation:host?.generation??0,...payload}};
    const bytes=Buffer.from(JSON.stringify(record)+'\n');check(bytes.length<=MAX_RECORD,'outbound record too large');
    let written=0;while(written<bytes.length)written+=fs.writeSync(outputFd,bytes,written,bytes.length-written);
  }
  async function command(c) {
    closed(c,['protocol_version','host_id','run_id','nonce','sequence','command_id','operation_id','attempt_id','session_id','type','op','payload_schema','payload']);
    check(c.protocol_version===1 && c.type==='command' && c.payload_schema==='sdk-v1' &&
      Object.keys(binding).every(k=>c[k]===binding[k]) && c.sequence===++inbound && !ids.has(c.command_id),'envelope authentication/sequence');
    check(['command_id','operation_id','attempt_id'].every(k=>typeof c[k]==='string' && /^[A-Za-z0-9][A-Za-z0-9._:/-]*$/.test(c[k])) &&
      Number.isSafeInteger(c.sequence) && c.sequence>0,'invalid command identifiers');
    ids.add(c.command_id); check(ids.size<=10000,'host command lifetime exceeded');
    if (c.op==='tool') {
      closed(c.payload,['generation','call','result']);
      const pending=tools.get(c.payload.call);
      check(pending && c.operation_id===pending.command.operation_id && c.attempt_id===pending.command.attempt_id &&
        c.payload.generation===host.generation,'tool correlation');
      tools.delete(c.payload.call); pending.resolve(c.payload.result);send('response',{ok:true},c);return;
    }
    if (['create','open'].includes(c.op)) {
      check(!host && !creating && c.session_id===null,'duplicate create/open');creating=true;current=c;
      host=await createHost(c.payload,event=>{
        const type=event.type==='settled'?'settled':event.type==='request_observation'?'request_observation':'lifecycle';
        send(type,event);
      },(request,signal)=>new Promise((resolve,reject)=>{
        check(host.active && !host.poisoned && !tools.has(request.call),'tool phase');
        const command=current;
        tools.set(request.call,{resolve,reject,command});
        signal?.addEventListener('abort',()=>{tools.delete(request.call);reject(new Error('tool aborted; runner drain required'));},{once:true});
        send('tool_request',{...request,generation:host.generation},command);
      }));
      send('response',{ok:true,snapshot:host.telemetry()},c);return;
    }
    check(host && c.session_id===host.session.sessionId,'session binding');
    if (c.op==='prompt') {
      check(!host.active,'prompt overlap');current=c;
      send('response',{ok:true,accepted:true},c);
      await host.run(c.payload);return;
    }
    if (['abort','drain'].includes(c.op)) { closed(c.payload,['generation']);check(c.payload.generation===host.generation,'abort generation');send('response',{ok:true,...await host.abort()},c);return; }
    if (c.op==='telemetry') {closed(c.payload,['generation']);check(c.payload.generation===host.generation,'telemetry generation');send('response',{ok:true,snapshot:host.telemetry()},c);return;}
    if (c.op==='close') {closed(c.payload,['generation']);check(!host.active && tools.size===0,'close requires drain');await host.close();send('response',{ok:true},c);process.exit(0);}
    throw new Error('unsupported operation');
  }
  const decoder=new Decoder(c=>{command(c).catch(error=>{if(host) void host.abort().catch(()=>{});send('response',{ok:false,error:error.safeCode??'protocol_or_sdk_blocker'},c);});});
  const input=fs.createReadStream(null,{fd:inputFd,highWaterMark:4096,autoClose:true});
  input.on('data',chunk=>{try {decoder.feed(chunk);}catch(_){void host?.abort();process.exitCode=2;input.destroy();}});
  input.on('end',()=>{try {decoder.end();}finally {if(host) void host.close().finally(()=>process.exit(2));else process.exit(2);}});
}
if (process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) main().catch(()=>process.exit(2));
