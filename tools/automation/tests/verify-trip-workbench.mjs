// Browser contract tests run without numerical solvers. Optional real-service
// smoke check uses OSR_TRIP_ORIGIN and submits only a bounded evidence preflight.
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,extname} from 'node:path';
import {createHash,randomUUID} from 'node:crypto';
import {launchBrowser} from './browser-launch.mjs';

const root=resolve(import.meta.dirname,'../../..');
const output=resolve(process.argv[2]||'build/trip-workbench-browser');
await mkdir(output,{recursive:true});
const ids=['a'.repeat(64),'b'.repeat(64)];
const vehicles=[{candidate_id:ids[0],label:'Canonical comparison',body_family:'retained frame',magnetic_family:'ferrite',comparison_empty_kg_per_car:25618.59,comparison_aw3_kg_per_car:37618.59,installed_empty_kg_per_car:null,cg_m:null,inertia_kg_m2:null,unknown_installed_inventory:['Equipped locations and installed inertia unknown']},{candidate_id:ids[1],label:'GFRP / NdFeB <source option>',body_family:'GFRP',magnetic_family:'N35UH',comparison_empty_mass_band_kg:[15826,16066],comparison_aw3_mass_band_kg:[27826,28066],installed_empty_kg_per_car:null,cg_m:null,inertia_kg_m2:null}];
const summary={completed_evidence_preflights:9,chrono_benchmarks_executed:5,integrated_journeys_executed:0,campaign_id:'c'.repeat(64),physical_accepted:false};
const programme={tasks:[{id:'equipped-car',question:'Close the equipped car inventory',completion:'Every installed item is counted and positioned; unknown stock prevents completion.',prerequisites:[],budget:{max_variants:3,maximum_solver_seconds_per_trial:300,maximum_numerical_workers:2}}]};
const minimalPNG=Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a3ioAAAAASUVORK5CYII=','base64');
let plot=minimalPNG;
for(const candidate of [resolve(root,'docs/design-engine/trip-dynamics/benchmark-traces.png'),resolve(root,'../../../..','docs/design-engine/trip-dynamics/benchmark-traces.png')]){try{plot=await readFile(candidate);break;}catch{}}
const payloads={'summary.json':Buffer.from(JSON.stringify(summary)),'digital-programme.json':Buffer.from(JSON.stringify(programme)),'benchmark-traces.png':plot};
const manifest={files_sha256:Object.fromEntries(Object.entries(payloads).map(([key,value])=>[key,createHash('sha256').update(value).digest('hex')]))};
const jobs=new Map(),requests=[];let failStatus=false;
function send(response,code,data,type='application/json'){response.writeHead(code,{'Content-Type':type,'Cache-Control':'no-cache','Content-Security-Policy':"default-src 'self'; connect-src 'self' blob:; img-src 'self' blob:; style-src 'self'; object-src 'none'; base-uri 'none'"});response.end(type==='application/json'?JSON.stringify(data):data);}
function complete(job){
  if(job.action==='campaign'||!['queued','running'].includes(job.state))return;
  job.state='completed';job.finished_at=new Date().toISOString();job.progress={phase:'finished',message:'Interface fixture only — no solver execution'};
  if(job.action==='probe'){job.result={execution_status:'refused',reason:'Unsupported probe in this interface fixture; no solver was launched.'};return;}
  if(job.action.startsWith('validate-')){job.result={execution_status:'completed',validation:{schema_valid:true,numerical_checks:true,checked_source_execution:false},physical_accepted:false};return;}
  job.result={execution_status:'completed',mode:job.parameters.mode,scenario_id:'d'.repeat(64),result:job.parameters.mode==='benchmark'?{state:'completed',summary:{elapsed_simulation_s:100,actual_steps:200000,terminal_max_distance_error_m:.00001,terminal_max_speed_m_s:.000001,work_energy_residual_J:100},physical_accepted:false}:{metrics:{dynamic_execution:'not-run'},constraints:[{id:'equipped-mass-properties',status:'unknown',reason:'Installed distribution incomplete'},{id:'nonlinear-force-map',status:'unknown'}],physical_accepted:false}};
  if(job.parameters.mode==='benchmark')job.outputs=[{path:'trace.png',bytes:plot.length,url:`/api/trip/jobs/${job.job_id}/files/trace.png`},{path:'result.json',bytes:10,url:`/api/trip/jobs/${job.job_id}/files/result.json`},{path:'unsafe.html',bytes:1,url:'https://example.invalid/escape'}];
}
const server=createServer(async(request,response)=>{
 try{
  const url=new URL(request.url,'http://localhost');const path=url.pathname;
  if(path==='/api/trip/status'){if(failStatus)return send(response,503,{error:'Status service unavailable'});return send(response,200,{status:'Interface fixture — no solver execution',tools:{Chrono:{available:true,version:'fixture'},Code_Aster:{available:false,reason:'Template only'}},server:{publication_integrity:{current:true}},jobs:[...jobs.values()],limits:{max_workers:2,max_jobs:32,request_bytes:4194304},physical_accepted:false});}
  if(path==='/api/trip/catalogue')return send(response,200,{vehicles,magnets:[{id:'magnet-source',label:'N35UH comparison',grade:'N35UH',scope:'Unqualified material comparison'}],equipment:{HVAC:{known_package_hardware_kg:384,complete_installed_mass_kg:null},doors:{retained_openings:4},glazing:{solar_factor:.55}},source_sha256:{'source.py':'e'.repeat(64)},errors:[],physical_accepted:false});
  if(path==='/api/trip/jobs'&&request.method==='GET')return send(response,200,{jobs:[...jobs.values()]});
  if(path==='/api/trip/jobs'&&request.method==='POST'){
   let raw='';for await(const chunk of request)raw+=chunk;const body=JSON.parse(raw);requests.push(body);
   if(body.action==='fixture')return send(response,503,{error:'Fixture worker unavailable'});
   const id=randomUUID();const job={job_id:id,...body,state:'running',progress:{phase:'running',message:'Bounded interface fixture'},created_at:new Date().toISOString(),request_id:'f'.repeat(64),result:null,outputs:[],physical_accepted:false};jobs.set(id,job);return send(response,202,job);
  }
  const match=path.match(/^\/api\/trip\/jobs\/([^/]+)(.*)$/);
  if(match){const job=jobs.get(match[1]);if(!job)return send(response,404,{error:'Unknown job'});if(match[2]==='/cancel'&&request.method==='POST'){job.state='cancelled';job.progress={phase:'cancelled',message:'Cancellation recorded'};return send(response,200,job);}if(match[2]==='/logs')return send(response,200,{text:`Interface fixture ${url.searchParams.get('stream')} log`,truncated:false});if(match[2].startsWith('/files/'))return send(response,200,match[2].endsWith('.png')?plot:{physical_accepted:false},match[2].endsWith('.png')?'image/png':'application/json');complete(job);return send(response,200,job);}
  if(path==='/docs/design-engine/trip-dynamics/manifest.json')return send(response,200,manifest);
  const payload=payloads[path.replace('/docs/design-engine/trip-dynamics/','')];if(path.startsWith('/docs/design-engine/trip-dynamics/')&&payload)return send(response,200,payload,path.endsWith('.png')?'image/png':'application/octet-stream');
  const relative=path==='/docs/workbench/trip/'?'docs/workbench/trip/index.html':path.slice(1);const file=resolve(root,relative);if(!file.startsWith(resolve(root,'docs/workbench/trip')+'/'))return send(response,404,{error:'Unowned path'});const data=await readFile(file);return send(response,200,data,{'.html':'text/html','.js':'application/javascript','.css':'text/css'}[extname(file)]||'application/octet-stream');
 }catch(e){send(response,500,{error:String(e)});}
});
await new Promise((accept,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',accept);});
const origin=`http://127.0.0.1:${server.address().port}`;let browser;
try{
 browser=await launchBrowser();const page=await browser.newPage({viewport:{width:1440,height:1100}});const errors=[],external=[];page.on('pageerror',e=>errors.push(String(e)));page.on('request',request=>{if(!request.url().startsWith(origin+'/')&&!request.url().startsWith('blob:'+origin+'/'))external.push(request.url());});
 await page.goto(origin+'/docs/workbench/trip/');await page.waitForFunction(()=>!document.querySelector('#run-fields').disabled);
 await page.waitForFunction(()=>document.querySelector('#publication-status').textContent.includes('bytes match'));
 assert.equal(await page.locator('#vehicle option').count(),2);assert.ok((await page.locator('.scope-notice').innerText()).includes('No qualified train'));
 assert.ok((await page.locator('#tools').innerText()).includes('Template-only'));assert.ok((await page.locator('#digital-plan').innerText()).includes('Every installed item'));
 await page.selectOption('#vehicle',ids[1]);await page.selectOption('#mode','benchmark');await page.selectOption('#distance','1500');await page.selectOption('#load','empty');await page.selectOption('#temperature','50');await page.selectOption('#timestep','0.0005');
 assert.ok((await page.locator('#vehicle-detail').innerText()).includes('GFRP / NdFeB <source option>'));assert.equal(await page.locator('#vehicle-detail script').count(),0);assert.ok((await page.locator('#vehicle-detail').innerText()).includes('Unknown'));
 await page.click('#run-experiment');await page.waitForFunction(()=>document.querySelector('#result-summary').textContent.includes('Ideal benchmark result'),undefined,{timeout:15000});
 assert.deepEqual(requests.at(-1),{action:'experiment',parameters:{vehicle_id:ids[1],mode:'benchmark',distance_m:1500,load_case:'empty',temperature_C:50,mechanical_step_s:.0005}});
 await page.waitForFunction(()=>document.querySelector('#result-plot').complete&&document.querySelector('#result-plot').naturalWidth>0);assert.equal(await page.locator('#job-files a[href^="https:"]').count(),0);assert.ok((await page.locator('#result-summary').innerText()).includes('No actual magnetic lift'));
 await page.screenshot({path:resolve(output,'desktop-benchmark.png'),fullPage:true});
 await page.selectOption('#mode','evidence');await page.click('#run-experiment');await page.waitForFunction(()=>document.querySelector('#result-summary').textContent.includes('motion not run'));
 assert.ok((await page.locator('#result-summary').innerText()).includes('equipped-mass-properties: unknown'));assert.equal(await page.locator('#result-figure').isHidden(),true);
 await page.click('[data-action=probe]');await page.waitForFunction(()=>document.querySelector('#job-status').textContent.includes('refused'));assert.ok((await page.locator('#result-summary').innerText()).includes('Unsupported probe'));
 await page.selectOption('#fixture','current');await page.click('#run-fixture');await page.waitForFunction(()=>document.querySelector('#request-error').textContent.includes('Fixture worker unavailable'));assert.equal(requests.at(-1).parameters.fixture,'current');
 await page.click('[data-action=campaign]');await page.waitForFunction(()=>!document.querySelector('#cancel-job').disabled);await page.click('#cancel-job');await page.waitForFunction(()=>document.querySelector('#job-status').textContent.includes('cancelled'));assert.equal(await page.locator('#cancel-job').isDisabled(),true);
 const before=requests.length;await page.setInputFiles('#model-file',{name:'broken.json',mimeType:'application/json',buffer:Buffer.from('{broken')});await page.click('#import-form button');await page.waitForFunction(()=>document.querySelector('#request-error').textContent.includes('valid JSON'));assert.equal(requests.length,before);
 await page.setInputFiles('#model-file',{name:'map.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify({schema:'fixture-force-map/1',values:[1,2]}))});await page.click('#import-form button');await page.waitForFunction(()=>document.querySelector('#result-summary').textContent.includes('Imported-data check'));
 assert.deepEqual(requests.at(-1),{action:'validate-map',parameters:{model_data:{schema:'fixture-force-map/1',values:[1,2]},vehicle_id:ids[1],load_case:'empty',temperature_C:50}});assert.ok((await page.locator('#result-summary').innerText()).includes('do not establish checked source execution'));
 await page.selectOption('#import-kind','validate-modal');await page.click('#import-form button');await page.waitForFunction(()=>document.querySelector('#job-status').textContent.startsWith('validate modal'));assert.equal(requests.at(-1).action,'validate-modal');
 await page.click('[data-action=setup-tools]');await page.waitForFunction(()=>document.querySelector('#job-status').textContent.startsWith('setup tools'));assert.deepEqual(requests.at(-1),{action:'setup-tools',parameters:{}});
 await page.click('[data-action=verify]');await page.waitForFunction(()=>document.querySelector('#job-status').textContent.startsWith('verify'));assert.deepEqual(requests.at(-1),{action:'verify',parameters:{}});
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:resolve(output,'mobile.png'),fullPage:true});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true,'No horizontal overflow on mobile');
 failStatus=true;await page.click('#refresh');await page.waitForFunction(()=>document.querySelector('#connection-status').textContent.includes('unavailable'));assert.equal(await page.locator('#run-fields').isDisabled(),true);
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);await writeFile(resolve(output,'interface-contract.json'),JSON.stringify({passed:true,scope:'Instrumented local HTTP API fixtures; no numerical solver execution',requests,screenshots:['desktop-benchmark.png','mobile.png'],rendering:browser.osrRendering},null,2)+'\n');
 if(process.env.OSR_TRIP_ORIGIN){const real=new URL(process.env.OSR_TRIP_ORIGIN);assert.ok(['127.0.0.1','localhost'].includes(real.hostname));const live=await browser.newPage({viewport:{width:1440,height:1000}});await live.goto(real.origin+'/docs/workbench/trip/');await live.waitForFunction(()=>!document.querySelector('#run-fields').disabled,undefined,{timeout:60000});await live.selectOption('#mode','evidence');await live.click('#run-experiment');await live.waitForFunction(()=>document.querySelector('#job-status').textContent.includes('completed')||document.querySelector('#job-status').textContent.includes('failed')||document.querySelector('#job-status').textContent.includes('refused'),undefined,{timeout:60000});assert.ok((await live.locator('#result-summary').innerText()).includes('motion not run'));await live.screenshot({path:resolve(output,'real-evidence-preflight.png'),fullPage:true});await live.close();}
 console.log(JSON.stringify({passed:true,requests:requests.length,output,real_service_smoke:!!process.env.OSR_TRIP_ORIGIN}));
}finally{if(browser)await browser.close();await new Promise(accept=>server.close(accept));}
