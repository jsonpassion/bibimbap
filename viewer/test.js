// node test.js — extracts the DOM-free core <script> from viewer.html, runs derive()/normalizeRaw()/splitsOf() and prints the acceptance table.
const fs=require('fs'),path=require('path'),dir=__dirname;
const html=fs.readFileSync(path.join(dir,'viewer.html'),'utf8');
const blocks=html.split('<script>').slice(1).map(s=>s.split('</script>')[0]);
new Function(blocks.join('\n'));                                   // 1. syntax of all JS blocks (concatenated in order)
const C=new Function(blocks[0]+';return {derive,normalizeRaw,splitsOf,capOf,baseOf,baseLane,BENCH,benchVerdicts,LATEST,RUN_IDS};')();   // 2. core block alone, no DOM
const inlined=[...html.matchAll(/<script type="application\/json" id="(run-\d+)">/g)].map(m=>m[1]);
const load=k=>JSON.parse(fs.readFileSync(path.join(dir,'traces',k+'.json'),'utf8'));
const files=fs.readdirSync(path.join(dir,'traces')).filter(f=>/^run-\d+\.json$/.test(f)).map(f=>f.slice(0,-5)).sort();
console.log('inline blocks:',inlined.join(', '),'| LATEST =',C.LATEST,'| RUN_IDS =',C.RUN_IDS.join(', '),'| JS lines:',blocks.join('\n').split('\n').length,'| file lines:',html.split('\n').length);
const row=(k,T,D)=>{const b=D.base;
  console.log(`${k}${inlined.includes(k)?' (inline)':''} | tokens ${D.total.toLocaleString('en-US')} (${D.prompt.toLocaleString('en-US')}+${D.completion.toLocaleString('en-US')}) | ratio ${b?(D.total/b.tok).toFixed(2)+' → '+(D.total/b.tok).toFixed(1)+'×':'—'} | input ${(D.prompt/D.total*100).toFixed(1)}% | calls ${D.calls.length} | tasks ${D.spans.length} (${D.dupCount}) | dur ${D.dur.toFixed(1)} | plan-ready ${D.plan?D.plan.t:'—'} | first/last call ${D.calls[0].t} / ${D.calls[D.calls.length-1].t}`);
  console.log(`   subtotals ${D.spans.map(s=>`#${s.n} ${(s.prompt+s.completion).toLocaleString('en-US')}·${s.calls.length}·${s.dur.toFixed(2)}s${s.dup?' dup':''}${s.wallDur!=null?' (durationSec '+s.wallDur+')':''}`).join(' · ')} | first→last ${JSON.stringify(D.spans.map(s=>[s.first,s.last]))}`);
  console.log(`   gaps ${JSON.stringify(D.gaps.map(g=>[g.t0,g.t1]))} | flags ${D.flags.length}: ${D.flags.map(i=>D.flag[i]+'@#'+(i+1)).join(' ')} | serialClaim ${D.serialClaim?'non-null':'null'} | agents ${T.agents.length} / with calls ${D.active} (+planner) | planner ${(D.planner||{}).model} | rejected ${T.meta.rejectedPlansBefore} | events ${T.events.length} | trace.tokens.total ${D.traceTotal===D.total?'✓':'✗'}`);};
const DD={};for(const k of files){const T=load(k);DD[k]=C.derive(T);row(k,T,DD[k]);}
// checks against the spec's acceptance table + owner's run-004 numbers
const assert=(c,m)=>{if(!c){console.error('ASSERT FAILED:',m);process.exitCode=1;}};
const a1=DD['run-001'];assert(a1.total===26808&&a1.calls.length===28&&a1.spans.length===3&&a1.dupCount===2&&+a1.dur.toFixed(1)===60.2,'run-001 totals');
assert(JSON.stringify(a1.spans.map(s=>s.prompt+s.completion))==='[10629,4330,11849]','run-001 subtotals');assert(JSON.stringify(a1.spans.map(s=>[s.first,s.last]))==='[[487,1277],[487,758],[522,1196]]','run-001 first/last');
assert(a1.serialClaim!==null&&DD['run-003'].serialClaim===null&&DD['run-004'].serialClaim===null,'serialClaim');assert(a1.flags.length===9&&DD['run-004'].flags.length===2,'flag counts');
if(DD['run-002'])assert(DD['run-002'].total===1564&&DD['run-002'].calls.length===2,'run-002');if(DD['run-003'])assert(DD['run-003'].total===1645&&DD['run-003'].plan.t===12.47,'run-003');
const a4=DD['run-004'];assert(a4.total===1611&&a4.prompt===1501&&a4.completion===110&&a4.calls.length===2&&a4.spans.length===1&&a4.dupCount===0&&a4.plan.t===14.44&&a4.calls[0].t===15.89&&a4.calls[1].t===16.53&&(a4.total/a4.base.tok).toFixed(1)==='2.6','run-004');
const base=C.baseOf(load('run-004'));console.log('baseline lane:',JSON.stringify(C.baseLane(base).label),'| tok',base.tok,'| s',base.s);
console.log('splits v1 → run-003:',JSON.stringify(C.splitsOf(a1,DD['run-003'])));console.log('splits v1 → run-004:',JSON.stringify(C.splitsOf(a1,a4)));console.log('splits 단독 → run-004:',JSON.stringify(C.splitsOf(C.baseLane(base),a4)));
console.log('caption #8 run-001:',C.capOf(load('run-001'),a1,7),'| flag captions run-004:',a4.flags.map(i=>C.capOf(load('run-004'),a4,i)).join(' || '));
// BENCH (owner numbers) + verdict templates
console.log('BENCH:');C.BENCH.tracks.forEach(t=>console.log(`   ${t.name}: base ${t.base?`${t.base.acc}% (n=${t.base.n}) · ${t.base.tok} tok`:'— (not measured)'} → latest ${t.latest.acc}% (n=${t.latest.n}, CI90 ${t.latest.ci.join('–')}%) · ${t.latest.tok.toLocaleString('en-US')} tok${t.ref?' ['+t.ref+']':''}`));
const v=C.benchVerdicts();console.log('   verdict A:',v.A);console.log('   verdict B:',v.B);console.log('   excluded:',C.BENCH.excluded,'| planner:',JSON.stringify(C.BENCH.planner));
// 3. normalizeRaw: rebuild an AI:GO events.jsonl (+ .squad.json) from run-001.json (cumulative counters) and prove drop ingestion yields the same figures
const T1=load('run-001'),pl=T1.agents.find(a=>a.planner);
const squad={config:{name:T1.meta.squad,plannerAgentId:pl.id,agents:T1.agents.map(a=>({id:a.id,name:a.name,role:{value:a.role},modelPreferences:{preferredModelId:'furiosa-ai/'+a.model}}))}};
const payload=e=>{const d=e.detail||{};switch(e.type){
  case'planning-started':return{request:T1.meta.request};case'plan-ready':return{taskCount:d.taskCount,waves:d.waves,autoApprove:d.autoApprove};
  case'execution-started':return{totalTasks:T1.tasks.length,totalWaves:1};case'task-wave-started':return{waveIndex:0,taskIds:d.taskIds};
  case'task-status-changed':{const m=/(\w+) → (\w+)/.exec(e.summary);return{taskId:e.taskId,oldStatus:m[1],newStatus:m[2]};}   // no taskTitle in raw status events → title must come from task-completed (fix 2)
  case'agent-state-changed':return{agentId:e.agentId,state:d.state};case'execution-token-usage':return{promptTokens:e.tokens.cumPrompt,completionTokens:e.tokens.cumCompletion};
  case'token-usage-update':return{agentId:e.agentId,promptTokens:d.cumPrompt,completionTokens:d.cumCompletion,total:d.cumPrompt+d.cumCompletion};
  case'task-completed':return{taskId:e.taskId,taskTitle:T1.tasks.find(t=>t.id===e.taskId).title,success:d.success,taskCounts:d.taskCounts};
  case'aggregation-started':return{taskIds:T1.tasks.map(t=>t.id)};case'execution-completed':return{result:d.result,tokenUsage:{promptTokens:T1.tokens.prompt,completionTokens:T1.tokens.completion}};}};
const rejectedBefore=[{timestamp:'2026-08-22T04:50:00.000000Z',eventType:'squad:planning-started',payload:{request:'x'}},{timestamp:'2026-08-22T04:50:05.000000Z',eventType:'squad:plan-ready',payload:{taskCount:2,waves:[[]]}}];
const jsonl=rejectedBefore.concat(T1.events.map(e=>({timestamp:e.ts,eventType:'squad:'+e.type,payload:payload(e)}))).map(o=>JSON.stringify(o)).join('\n');
const N=C.normalizeRaw(jsonl,squad,load('run-004')),DN=C.derive(N);
console.log('normalizeRaw(events.jsonl from run-001):',`events ${N.events.length} | tokens ${DN.total.toLocaleString('en-US')} (${N.tokens.prompt}+${N.tokens.completion}) | calls ${DN.calls.length} | tasks ${DN.spans.length} (${DN.dupCount}) · insights.duplicateTasks ${N.insights.duplicateTasks} | titles ${[...new Set(DN.spans.map(s=>s.title))].join(',')} | span agents ${[...new Set(DN.spans.map(s=>s.agentName))].join(',')} | first status agentId ${N.events[4].agentName} | rejectedPlansBefore ${N.meta.rejectedPlansBefore} | dur ${N.meta.durationSec} | borrowedBaseline ${N.meta.borrowedBaseline} | subtotals ${JSON.stringify(DN.spans.map(s=>s.prompt+s.completion))} | flags ${DN.flags.length}`);
assert(DN.total===26808&&DN.calls.length===28&&DN.spans.length===3&&DN.dupCount===2&&N.insights.duplicateTasks===2&&DN.spans.every(s=>s.title==='SOLVE')&&N.events[4].agentName==='Math-Solver'&&N.meta.rejectedPlansBefore===1,'normalizeRaw');
console.log(process.exitCode?'SOME ASSERTS FAILED':'ALL ASSERTS PASSED');
