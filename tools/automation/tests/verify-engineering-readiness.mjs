// Real local Workbench route and retained data; no numerical solver is launched.
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {launchBrowser} from './browser-launch.mjs';

const root=resolve(import.meta.dirname,'../../..'),out=resolve(process.argv[2]||'build/readiness-browser');
await mkdir(out,{recursive:true});
const python=existsSync(resolve(root,'.venv/bin/python'))?resolve(root,'.venv/bin/python'):'python3';
const server=spawn(python,['-u','tools/automation/maglev-workbench.py','--port','0'],{cwd:root,stdio:['ignore','pipe','pipe']});
let logs='',browser;
server.stdout.on('data',chunk=>{logs+=chunk;});server.stderr.on('data',chunk=>{logs+=chunk;});
try{
 const origin=await new Promise((accept,reject)=>{const deadline=setTimeout(()=>reject(new Error('Workbench did not listen: '+logs)),30000);const check=chunk=>{const match=String(chunk).match(/http:\/\/127\.0\.0\.1:\d+/);if(match){clearTimeout(deadline);accept(match[0]);}};server.stdout.on('data',check);server.once('exit',code=>{clearTimeout(deadline);reject(new Error('Workbench exited '+code+': '+logs));});});
 browser=await launchBrowser();const page=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[],requests=[];
 page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>requests.push({url:r.url(),method:r.method()}));
 await page.goto(origin+'/docs/workbench/trip/readiness/');
 await page.locator('#integrity').filter({hasText:'Retained payload hashes verified'}).waitFor({timeout:30000});
 assert.equal(await page.locator('#gates tr').count(),8);assert.equal(await page.locator('#methods .method').count(),3);
 assert.equal(await page.locator('#gates .pass').count(),0);assert.match(await page.locator('#identity').innerText(),/complete installed mass unknown/);
 assert.equal(await page.locator('#journeys tr').count(),8);assert.match(await page.locator('#journeys').innerText(),/not-run/);
 await page.screenshot({path:resolve(out,'desktop.png'),fullPage:true});
 await page.locator('#filter').fill('40kn');assert.match(await page.locator('#count').innerText(),/36 of 504/);
 await page.locator('#filter').fill('compact');assert.match(await page.locator('#gates').innerText(),/fails a necessary local member/);
 await page.locator('#filter').fill('no-such-configuration');assert.equal(await page.locator('#candidate').isDisabled(),true);assert.equal(await page.locator('#gates tr').count(),0);
 await page.locator('#filter').fill('');await page.setViewportSize({width:390,height:844});
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
 await page.screenshot({path:resolve(out,'mobile.png'),fullPage:true});
 await page.route('**/engineering-readiness/index.json',route=>route.fulfill({status:200,contentType:'application/json',body:'{"register_id":"tampered"}'}));
 await page.locator('#refresh').click();await page.locator('#integrity').filter({hasText:'Evidence unavailable'}).waitFor();
 assert.equal(await page.locator('#gates tr').count(),0);assert.equal(await page.locator('#candidate').isDisabled(),true);
 await page.unroute('**/engineering-readiness/index.json');await page.locator('#refresh').click();
 await page.locator('#integrity').filter({hasText:'Retained payload hashes verified'}).waitFor();assert.equal(await page.locator('#gates tr').count(),8);
 assert.equal(errors.length,0,errors.join('\n'));assert.equal(requests.some(r=>r.method==='POST'),false,'Readiness display launched a job');
 assert.equal(requests.some(r=>!r.url.startsWith(origin+'/')&&!r.url.startsWith('blob:'+origin+'/')),false,'External data request');
 await writeFile(resolve(out,'result.json'),JSON.stringify({passed:true,scope:'Actual local Workbench and retained register; no solver execution',gates:8,retained_comparisons:504,tampered_payload_refused:true,mobile_overflow:false,errors},null,2)+'\n');
 console.log('Readiness browser checks passed: candidate gates, provenance failure, mobile layout and no job execution.');
}finally{if(browser)await browser.close();server.kill('SIGTERM');await writeFile(resolve(out,'server.log'),logs);}
