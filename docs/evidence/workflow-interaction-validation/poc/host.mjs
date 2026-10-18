// One bounded real Pi turn group per process; deterministic controller owns transitions.
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import crypto from 'node:crypto';
const root=path.resolve(process.env.POC_ROOT), phase=process.env.POC_PHASE;
const pkg=process.env.PI_SDK_ROOT;
const sdk=await import(path.join(pkg,'dist/index.js'));
const {Type}=createRequire(path.join(pkg,'package.json'))('typebox');
if(JSON.parse(fs.readFileSync(path.join(pkg,'package.json'))).version!=='0.87.1') throw Error('SDK version');
const binding=JSON.parse(fs.readFileSync(path.join(root,'binding.json')));
const emit=x=>process.stdout.write(JSON.stringify({v:1,at:Date.now(),phase,...x})+'\n');
const credential=sdk.readStoredCredential('openai-codex',process.env.PI_AUTH_PATH);
if(!credential || credential.type!=='oauth' || credential.expires<Date.now()+600000) throw Error('BLOCKED credential; no refresh');
const credentials={read:async id=>id==='openai-codex'?credential:undefined,list:async()=>[{providerId:'openai-codex',type:'oauth'}],
 modify:async()=>{throw Error('forbidden credential write');},delete:async()=>{throw Error('forbidden');}};
const catalogs=new Map(Object.entries(JSON.parse(fs.readFileSync(process.env.PI_MODELS_STORE_PATH))));
const runtime=await sdk.ModelRuntime.create({credentials,modelsStore:{read:async id=>catalogs.get(id),write:async(id,v)=>catalogs.set(id,v),delete:async id=>catalogs.delete(id)},modelsPath:null,allowModelNetwork:false});
const model=runtime.getModel('openai-codex','gpt-6.1-sol');
if(!model) throw Error('BLOCKED exact model unavailable');
const settings=sdk.SettingsManager.inMemory({cacheWarming:'off',transport:'sse',enableInstallTelemetry:false,compaction:{enabled:false},retry:{enabled:false,provider:{maxRetries:0,timeoutMs:30000}}});
let session, gate, steered=false;
const result=(text,details,terminate=false)=>({content:[{type:'text',text}],details,terminate});
const tools=[{ executionMode:'sequential',
 name:'request_owner_input',label:'Request product input',description:'Only manager-answerable product choice. Routine technical mechanics/tests must be resolved autonomously within approval. Scope changes need a distinct approval, never this cosmetic gate.',
 parameters:Type.Object({category:Type.String(),question:Type.String(),explanation:Type.String(),options:Type.Array(Type.String()),impact:Type.String()}),
 execute:async(id,p)=>{
  if(phase!=='ask' || gate || p.category!=='product' || JSON.stringify(p.options)!==JSON.stringify(['Release note','Progress note']) || !p.explanation || !p.impact) throw Error('ineligible question');
  gate={...binding,session:session.sessionId,sessionFile:session.sessionFile,toolCallId:id,category:p.category,question:p.question,explanation:p.explanation,options:p.options,impact:p.impact,nonce:crypto.randomBytes(16).toString('hex')};
  emit({type:'gate_created',gate});
  return result('PARKED. The controller will deliver the owner answer into this original conversation before continuation.',{gate},true);
 }
},{ executionMode:'sequential',
 name:'controlled_wait',label:'Yield for steering',description:'Call once before writing to allow the preapproved live steering test. No external side effects.',parameters:Type.Object({}),
 execute:async(id,_p,signal)=>{
  emit({type:'active_ready',session:session.sessionId,toolCallId:id});
  const until=Date.now()+120000;
  while(Date.now()<until && !signal?.aborted){
   const f=path.join(root,'steer.json');
   if(fs.existsSync(f)){
    const c=JSON.parse(fs.readFileSync(f));
    if(c.session!==session.sessionId || c.nonce!==binding.nonce || c.sourceHash!==binding.sourceHash || c.message!=='Include the sentence: Steering received.') throw Error('wrong steering binding');
    await session.steer(c.message); steered=true;
    emit({type:'steer_enqueued',session:session.sessionId,messageId:c.messageId,attempt:binding.attempt});
    return result('Released after SDK steering enqueue. Read the incoming steering message at the next execution boundary.',{messageId:c.messageId});
   }
   await new Promise(r=>setTimeout(r,100));
  }
  throw Error('BLOCKED no steering before bounded hold deadline');
 }
},{ executionMode:'sequential',
 name:'write_note',label:'Write toy note',description:'Write only toy-note.txt. Use exact owner-selected title, include received steering sentence, and acknowledge answer/steering IDs.',
 parameters:Type.Object({title:Type.String(),body:Type.String(),answerId:Type.String(),messageId:Type.String()}),
 execute:async(id,p)=>{
  const answer=JSON.parse(fs.readFileSync(path.join(root,'answer.json'))), steer=JSON.parse(fs.readFileSync(path.join(root,'steer.json')));
  if(phase!=='resume' || !steered || p.title!==answer.choice || !p.body.includes('Steering received.') || p.answerId!==answer.answerId || p.messageId!==steer.messageId) throw Error('answer/steer not acknowledged');
  fs.writeFileSync(path.join(root,'toy-note.txt'),p.title+'\n'+p.body+'\n');
  emit({type:'worker_acknowledged',session:session.sessionId,answerId:p.answerId,messageId:p.messageId,toolCallId:id});
  return result('Toy note written; acknowledgements recorded.',{answerId:p.answerId,messageId:p.messageId});
 }
}];
const loader=new sdk.DefaultResourceLoader({cwd:root,agentDir:path.join(root,'agent'),settingsManager:settings,noExtensions:true,noSkills:true,noPromptTemplates:true,noThemes:true,noContextFiles:true,
 systemPrompt:'You are a bounded toy note worker. Use only supplied tools. Never ask about routine implementation or approved tiny tests. You may ask one manager-answerable cosmetic product question via request_owner_input. Never call ask_user. Tools are serial; stop after parking. On answer, first controlled_wait, then write_note using incoming steering and receipt IDs. No other work or tools. Keep responses short.'});
await loader.reload();
const manager=binding.sessionFile?sdk.SessionManager.open(binding.sessionFile,path.join(root,'sessions')):sdk.SessionManager.create(root,path.join(root,'sessions'));
const created=await sdk.createAgentSession({cwd:root,agentDir:path.join(root,'agent'),modelRuntime:runtime,model,thinkingLevel:'medium',settingsManager:settings,resourceLoader:loader,tools:tools.map(t=>t.name),customTools:tools,sessionManager:manager});
session=created.session;
if(created.modelFallbackMessage || session.thinkingLevel!=='medium' || (phase==='resume' && session.sessionId!==binding.session)) throw Error('BLOCKED identity/profile mismatch');
if(JSON.stringify(session.getActiveToolNames().sort())!==JSON.stringify(tools.map(t=>t.name).sort())) throw Error('BLOCKED tool activation mismatch');
const original=session.agent.streamFunction, transform=session.agent.onPayload;
let calls=0;
session.agent.streamFunction=(m,c,o={})=>original(m,c,{...o,maxRetries:0,timeoutMs:30000,transport:'sse',onPayload:async(p,rm)=>{
 const out=(await (o.onPayload??transform)?.(p,rm))??p;
 const effort=model.thinkingLevelMap?.medium??'medium';
 if(m.provider!=='openai-codex'||m.id!==model.id||out.model!==model.id||out.reasoning?.effort!==effort) throw Error('OUTBOUND_BINDING_MISMATCH');
 if(++calls>5) throw Error('bounded fixture call cap');
 emit({type:'outbound_guard',model:out.model,effort:out.reasoning.effort,call:calls,tokenCapEnforced:false});return out;
}});
session.subscribe(e=>{if(['agent_start','agent_end','agent_settled','tool_execution_start','tool_execution_end'].includes(e.type))emit({type:'sdk_event',event:e.type,tool:e.toolName??null});});
emit({type:'opened',session:session.sessionId,sessionFile:session.sessionFile,reopened:phase==='resume',pid:process.pid,storedMessages:session.messages.length});
try{
 const answer=phase==='resume'?JSON.parse(fs.readFileSync(path.join(root,'answer.json'))):null;
 const prompt=phase==='ask'?'Ask the owner which toy note title to use: Release note or Progress note. Category product, options exactly ["Release note","Progress note"], explain cosmetic label only, no scope or cost impact. Call request_owner_input once, then stop.':
  'OWNER ANSWER ENVELOPE '+JSON.stringify(answer)+'\nThis is the answer to the parked gate in THIS original conversation. First call controlled_wait; afterwards use the incoming steering message, then write_note and acknowledge both IDs. Steering message ID will be steering-1. End briefly.';
 await session.prompt(prompt);await session.waitForIdle();
 const last=[...session.messages].reverse().find(m=>m.role==='assistant');
 emit({type:'settled',session:session.sessionId,idle:session.isIdle,stopReason:last?.stopReason??null,gate:gate??null,calls,stats:session.getSessionStats().tokens,cost:session.getSessionStats().cost,
  answerInConversation:answer?session.messages.some(m=>m.role==='user'&&JSON.stringify(m.content).includes(answer.answerId)):false,
  steerInConversation:session.messages.some(m=>m.role==='user'&&JSON.stringify(m.content).includes('Include the sentence: Steering received.'))});
}finally{session.dispose();}
