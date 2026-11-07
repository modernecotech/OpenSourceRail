import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {mkdir,readFile,realpath,writeFile} from 'node:fs/promises';
import {extname,resolve,sep} from 'node:path';
import {launchBrowser} from './tests/browser-launch.mjs';

// Read-only presentation check. A private site override supports explicitly
// labelled synthetic UI fixtures; neither mode runs railway calculations.
const root=resolve(process.env.OSR_ROOT || process.cwd());
const site=resolve(process.env.OSR_STATION_CYCLE_SITE || resolve(root,'docs/design-engine/station-cycle'));
const prefix='/docs/design-engine/station-cycle/';
const summary=JSON.parse(await readFile(resolve(site,'summary.json'),'utf8'));
const capture=process.env.OSR_STATION_CYCLE_CAPTURE;
const receipt={study_id:summary.study_id,presentation_fixture:summary.presentation_fixture===true,
  assertions:[],candidate_inputs_modified:false,physical_acceptance_conferred:false,
  scope:'Static presentation, links and responsive layout only. This is not a numerical or engineering verification.'};
const errors=[];
const mime={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.gz':'application/gzip','.md':'text/markdown'};
const server=createServer(async(request,response)=>{
  if(request.url==='/favicon.ico'){response.writeHead(204);response.end();return;}
  try{
    let name=decodeURIComponent(new URL(request.url,'http://localhost').pathname);
    const fromSite=name.startsWith(prefix);let base=fromSite?site:root;
    name=fromSite?name.slice(prefix.length):'.'+name;
    if(name===''||name.endsWith('/'))name+='index.html';
    const path=await realpath(resolve(base,name));
    if(!path.startsWith(base+sep)){response.writeHead(403);response.end();return;}
    response.writeHead(200,{'content-type':mime[extname(path)]||'application/octet-stream',
      'content-security-policy':"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'"});
    response.end(await readFile(path));
  }catch{response.writeHead(404);response.end();}
});
await new Promise(done=>server.listen(0,'127.0.0.1',done));
const url=`http://127.0.0.1:${server.address().port}${prefix}`;
let browser;
const record=text=>receipt.assertions.push(text);
try{
  browser=await launchBrowser();receipt.browser=browser.osrRendering;
  const page=await browser.newPage({viewport:{width:1500,height:1050}});
  page.on('pageerror',error=>errors.push(String(error)));
  page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
  await page.goto(url);await page.locator('#study-content:not([hidden])').waitFor();
  assert.equal(await page.locator('#comparison-body tr').count(),Math.max(1,summary.rows.length));
  assert.equal(await page.locator('#study-id').innerText(),summary.study_id);
  assert.equal(await page.locator('#candidate-picker option').count(),summary.rows.length);
  record('Nominal rows and candidate picker retain the exact exported study identity');
  for(const technology of ['baseline','steel','hydraulic']){
    await page.selectOption('#technology-filter',technology);
    const expected=summary.rows.filter(row=>technology==='baseline'?row.technology===null:row.technology===technology);
    assert.equal(await page.locator('#comparison-body tr').count(),Math.max(1,expected.length));
  }
  await page.getByRole('button',{name:'Reset filters'}).click();
  await page.selectOption('#recovery-filter','on');
  assert.equal(await page.locator('#comparison-body tr').count(),Math.max(1,summary.rows.filter(row=>row.storage_enabled).length));
  await page.selectOption('#recovery-filter','off');
  assert.equal(await page.locator('#comparison-body tr').count(),Math.max(1,summary.rows.filter(row=>!row.storage_enabled).length));
  await page.getByRole('button',{name:'Reset filters'}).click();
  record('Technology and recovery filters preserve paired hardware and bare comparisons');
  await page.locator('.source-details summary').click();
  const unknown=summary.rows.findIndex(row=>!Number.isFinite(row.cost?.whole_life_NPV_usd?.base));
  for(let index=0;index<summary.rows.length;index++){
    const row=summary.rows[index];await page.selectOption('#candidate-picker',String(index));
    assert((await page.locator('#identities').innerText()).includes(row.candidate_id));
    assert.equal(await page.locator('#legs-body tr').count(),Math.max(1,row.legs.length));
    assert.equal(await page.locator('#energy-flow .flow-step').count(),4);
    assert.equal(await page.locator('#cost-body tr').count(),14);
    const faults=summary.faults.filter(f=>f.candidate_id===row.candidate_id);
    assert.equal(await page.locator('#fault-body tr').count(),Math.max(1,faults.length));
  }
  record('Selected candidates retain all leg, station-energy, fourteen-scope and fault records');
  if(unknown>=0){
    await page.selectOption('#candidate-picker',String(unknown));
    assert((await page.locator('#cost-cards').innerText()).includes('Unknown'));
    assert((await page.locator('#cost-cards').innerText()).includes('Known lifecycle subtotal'));
    record('Unknown complete NPV stays distinct from a priced subtotal');
  }
  await page.selectOption('#fault-filter','all');
  assert.equal(await page.locator('#fault-body tr').count(),Math.max(1,summary.faults.length));
  record('All supplied fault and sensitivity results remain accessible');
  const traceRow=summary.rows.findIndex(row=>row.legs.some(leg=>Array.isArray(leg.journey?.trace)&&leg.journey.trace.length>1));
  if(traceRow>=0){
    await page.selectOption('#candidate-picker',String(traceRow));
    assert.equal(await page.locator('#motion-chart svg').count(),1);
    const paths=await page.locator('#motion-chart path').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('d')));
    assert(paths.every(path=>path&&!/NaN|Infinity|undefined/.test(path)));
  }
  const emptyRow=summary.rows.findIndex(row=>row.legs.some(leg=>!leg.journey||!leg.journey.trace?.length));
  if(emptyRow>=0){
    const row=summary.rows[emptyRow];await page.selectOption('#candidate-picker',String(emptyRow));
    const index=row.legs.findIndex(leg=>!leg.journey||!leg.journey.trace?.length);
    await page.selectOption('#leg-picker',String(index));
    assert.equal(await page.locator('#motion-chart svg').count(),0);
    assert((await page.locator('#motion-chart').innerText()).includes('No source-linked motion trace'));
  }
  record('Available traces render finite geometry; held legs never acquire invented curves');
  const links=await page.locator('.download-links a').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('href')));
  for(const name of ['summary.json','study.json.gz','delivery-draft.json.gz','README.md']){
    assert(links.includes(name));const response=await page.request.get(new URL(name,url).href);assert.equal(response.status(),200);
  }
  assert(links.includes('../station-pair/'));
  assert(links.includes('../../archives/station-pair-fixed-control-20261107/README.md'));
  record('Source downloads and retained comparison/history links are present');
  const text=await page.locator('main').innerText();
  for(const phrase of ['serial shuttle','not a 30 km','Independent stopping','no free launch energy','Propulsion remains unselected']) assert(text.toLowerCase().includes(phrase.toLowerCase()));
  for(const [name,width,height] of [['desktop',1500,1050],['mobile',390,844]]){
    await page.setViewportSize({width,height});
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth+1),false,`${name} page overflows`);
    if(capture){await mkdir(capture,{recursive:true});await page.screenshot({path:resolve(capture,`${name}.png`),fullPage:true});}
  }
  record('Desktop/mobile layouts keep service, approval and pilot-price limitations visible without page overflow');
  assert.deepEqual(errors,[]);receipt.state='passed';receipt.console_errors=errors;
  console.log(JSON.stringify(receipt,null,2));
}catch(error){receipt.state='failed';receipt.reason=String(error);receipt.console_errors=errors;throw error;}
finally{
  if(capture){await mkdir(capture,{recursive:true});await writeFile(resolve(capture,'browser-result.json'),JSON.stringify(receipt,null,2)+'\n');}
  await browser?.close();await new Promise(done=>server.close(done));
}
