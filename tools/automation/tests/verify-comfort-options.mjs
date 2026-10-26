// Exercise the actual Workbench handler, selectors and integrity failure.
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {mkdir,writeFile} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {launchBrowser} from './browser-launch.mjs';
const root=resolve(import.meta.dirname,'../../..'),out=resolve(process.argv[2]||'build/comfort-browser');
await mkdir(out,{recursive:true});
const python=existsSync(resolve(root,'.venv/bin/python'))?resolve(root,'.venv/bin/python'):'python3';
const host=`import importlib.util,sys
from pathlib import Path
from http.server import ThreadingHTTPServer
root=Path(sys.argv[1]);sys.path.insert(0,str(root))
spec=importlib.util.spec_from_file_location('comfort_workbench',root/'tools/automation/maglev-workbench.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
from engineering.trip_dynamics.interactive import TripService
from engineering.trip_dynamics.interface_integrity import primary_integrity
server=ThreadingHTTPServer(('127.0.0.1',0),module.Handler)
server.publication_integrity=primary_integrity(root)
server.trip_service=TripService(root,output_root=Path(sys.argv[2])/'private-jobs',max_workers=1)
print('http://127.0.0.1:'+str(server.server_port),flush=True)
try:server.serve_forever()
finally:server.trip_service.close();server.server_close()
`;
const server=spawn(python,['-u','-c',host,root,out],{cwd:root,stdio:['ignore','pipe','pipe']});
let logs='',browser;
server.stdout.on('data',b=>logs+=b);server.stderr.on('data',b=>logs+=b);
try{
 const origin=await new Promise((yes,no)=>{const timer=setTimeout(()=>no(new Error(logs)),30000);server.stdout.on('data',b=>{const m=String(b).match(/http:\/\/127\.0\.0\.1:\d+/);if(m){clearTimeout(timer);yes(m[0]);}});server.once('exit',c=>{clearTimeout(timer);no(new Error('Server exited '+c+logs));});});
 browser=await launchBrowser();const page=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[],requests=[];
 page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>requests.push({url:r.url(),method:r.method()}));
 await page.goto(origin+'/docs/workbench/trip/readiness/comfort/');
 await page.locator('#integrity').filter({hasText:'Retained comfort payload verified'}).waitFor();
 assert.match(await page.locator('#metrics').innerText(),/44 \+ 2/);assert.match(await page.locator('#tradeoff').innerText(),/5,520/);assert.match(await page.locator('#tradeoff').innerText(),/69 seconds/);
 assert.match(await page.locator('#bench-note').innerText(),/4 wall-bench/);assert.equal(await page.locator('#components tr').count(),30);
 await page.locator('#recipe').selectOption('wheelchair-door-bay-alternative');assert.match(await page.locator('#metrics').innerText(),/48 \+ 2/);assert.match(await page.locator('#tradeoff').innerText(),/75 seconds/);
 await page.locator('#recipe').selectOption('door-bench-default');
 const windows=await page.locator('#window option').evaluateAll(opts=>opts.map(o=>({id:o.value,label:o.textContent})));
 const thin=windows.find(o=>o.label.includes('6 mm'));await page.locator('#window').selectOption(thin.id);assert.match(await page.locator('#glazing-note').innerText(),/outside_small_deflection_domain/);
 const pc=windows.find(o=>o.label.includes('12 mm'));await page.locator('#window').selectOption(pc.id);await page.locator('#hvac').selectOption('4');
 assert.match(await page.locator('#identity').innerText(),/Candidate [a-f0-9]{64}/);
 await page.screenshot({path:resolve(out,'desktop.png'),fullPage:true});
 await page.setViewportSize({width:390,height:844});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);await page.screenshot({path:resolve(out,'mobile.png'),fullPage:true});
 await page.route('**/comfort-options/summary.json',route=>route.fulfill({status:200,contentType:'application/json',body:'{"comparisons":[]}'}));
 await page.reload();await page.locator('#integrity').filter({hasText:'Evidence unavailable'}).waitFor();
 assert.equal(await page.locator('#recipe').isDisabled(),true);assert.equal(await page.locator('#metrics').innerText(),'');assert.equal(await page.locator('#plan').isHidden(),true);
 assert.equal(errors.length,0,errors.join('\n'));assert.equal(requests.some(r=>r.method==='POST'),false);assert.equal(requests.some(r=>!r.url.startsWith(origin+'/')),false);
 await writeFile(resolve(out,'result.json'),JSON.stringify({passed:true,actual_workbench_handler:true,candidate_selectors:true,tampered_payload_refused:true,mobile_overflow:false,solver_jobs_started:0,errors},null,2)+'\n');
 console.log('Comfort Workbench passed: actual handler, linked capacity/geometry, all selectors, mobile and tamper refusal.');
}finally{if(browser)await browser.close();server.kill('SIGTERM');await writeFile(resolve(out,'server.log'),logs);}
