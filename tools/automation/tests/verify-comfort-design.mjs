// Read the real Workbench route; verify identity-bound data and honest failure states.
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {mkdir,writeFile} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {launchBrowser} from './browser-launch.mjs';
const root=resolve(import.meta.dirname,'../../..'),out=resolve(process.argv[2]||'build/comfort-design-browser');
await mkdir(out,{recursive:true});const python=existsSync(resolve(root,'.venv/bin/python'))?resolve(root,'.venv/bin/python'):'python3';
const host=`import importlib.util,sys
from pathlib import Path
from http.server import ThreadingHTTPServer
root=Path(sys.argv[1]);sys.path.insert(0,str(root))
spec=importlib.util.spec_from_file_location('comfort_design_workbench',root/'tools/automation/maglev-workbench.py')
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
const server=spawn(python,['-u','-c',host,root,out],{cwd:root,stdio:['ignore','pipe','pipe']});let logs='',browser;
server.stdout.on('data',b=>logs+=b);server.stderr.on('data',b=>logs+=b);
try{
 const origin=await new Promise((yes,no)=>{const timer=setTimeout(()=>no(new Error(logs)),30000);server.stdout.on('data',b=>{const m=String(b).match(/http:\/\/127\.0\.0\.1:\d+/);if(m){clearTimeout(timer);yes(m[0]);}});server.once('exit',c=>{clearTimeout(timer);no(new Error('Server exited '+c+logs));});});
 browser=await launchBrowser();const page=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[],requests=[];
 page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>requests.push({url:r.url(),method:r.method()}));
 await page.goto(origin+'/docs/workbench/trip/readiness/');
 await page.getByRole('link',{name:'Matched comfort design · 120 seconds',exact:true}).click();
 await page.locator('#integrity').filter({hasText:'Retained matched-design payload verified'}).waitFor();
 assert.match(await page.locator('#metrics').innerText(),/8,280/);assert.match(await page.locator('#metrics').innerText(),/120 s/);
 assert.match(await page.locator('#prototype').innerText(),/218\.7/);assert.match(await page.locator('#station').innerText(),/36 independently/);
 assert.equal(await page.locator('#stress tr').count(),6);assert.ok(await page.locator('#gates .fail').count()>=2);
 assert.match(await page.locator('#fleet').innerText(),/1,206/);assert.match(await page.locator('#fleet').innerText(),/120 additional/);
 assert.match(await page.locator('#price').innerText(),/37\.4/);
 assert.ok(await page.locator('#scenarios tr').count()>10);
 await page.locator('#drag').selectOption('250');await page.locator('#dwell').selectOption('60');
 assert.ok(await page.locator('#scenarios tr').count()>10);
 await page.screenshot({path:resolve(out,'desktop.png'),fullPage:true});
 await page.setViewportSize({width:390,height:844});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
 await page.screenshot({path:resolve(out,'mobile.png'),fullPage:true});
 await page.route('**/comfort-design/summary.json',route=>route.fulfill({status:200,contentType:'application/json',body:'{"operating_release":true}'}));
 await page.reload();await page.locator('#integrity').filter({hasText:'Evidence unavailable'}).waitFor();
 assert.equal(await page.locator('#drag').isDisabled(),true);assert.equal(await page.locator('#metrics').innerText(),'');
 assert.equal(await page.locator('#gates tr').count(),0);
 assert.equal(errors.length,0,errors.join('\n'));assert.equal(requests.some(r=>r.method==='POST'),false);
 assert.equal(requests.some(r=>!r.url.startsWith(origin+'/')),false);
 await writeFile(resolve(out,'result.json'),JSON.stringify({passed:true,actual_workbench_handler:true,native_download_links:true,filters:true,known_failures_visible:true,tampered_payload_refused:true,mobile_overflow:false,native_jobs_started:0,errors},null,2)+'\n');
 console.log('Matched comfort design browser passed: actual navigation, filters, known failures, mobile and tamper refusal.');
}finally{if(browser)await browser.close();server.kill('SIGTERM');await writeFile(resolve(out,'server.log'),logs);}
