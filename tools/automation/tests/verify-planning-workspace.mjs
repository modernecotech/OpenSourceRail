import {expect} from '@playwright/test';
import {launchBrowser} from './browser-launch.mjs';
import {spawn} from 'node:child_process';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {gunzipSync} from 'node:zlib';
const root=process.cwd(),output=path.resolve(process.argv[2]||'build/planning-browser');await mkdir(output,{recursive:true});
const server=spawn('tools/automation/osr-python',['tools/automation/planning-workspace.py','serve','--port','0'],{cwd:root,stdio:['ignore','pipe','pipe']});
let browser,stderr='';server.stderr.on('data',b=>stderr+=b);server.on('error',e=>stderr+=e.message);
try{
 const url=await new Promise((resolve,reject)=>{let text='';const timeout=setTimeout(()=>reject(Error('Planning startup timeout: '+stderr)),1800000);server.stdout.on('data',b=>{text+=b;const m=text.match(/http:\/\/127\.0\.0\.1:\d+\/docs\/workbench\/planning\//);if(m){clearTimeout(timeout);resolve(m[0]);}});server.on('exit',code=>{clearTimeout(timeout);reject(Error('Planning server ended '+code+': '+stderr));});});
 browser=await launchBrowser();const page=await browser.newPage({viewport:{width:1400,height:1000}}),errors=[],external=[];
 page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(!r.url().startsWith(new URL(url).origin)&&!r.url().startsWith('blob:'))external.push(r.url());});
 await page.goto(url);await expect(page.locator('#status')).toContainText('bytes verified',{timeout:180000});
 const count=await page.locator('#city option').count();expect(count).toBe(266);expect(await page.locator('#layers input').count()).toBe(16);
 for(const city of ['kisangani','lubumbashi','garissa','baghdad']){await page.selectOption('#city',city);await expect(page.locator('#status')).toContainText('bytes verified');await expect(page.locator('#map-caption')).toContainText(city);expect(await page.locator('#map circle').count()).toBeGreaterThan(5);}
 const stop=page.locator('#stop');await stop.selectOption({index:1});const original=Number(await page.locator('#chainage').inputValue());
 await page.locator('#chainage').fill(String(original+10));await page.click('#move');await expect(page.locator('#edit-status')).toContainText('1 proposed changes');
 await page.locator('#headway').fill('30');await page.click('#service');await expect(page.locator('#issues')).toContainText('below the retained packet’s earlier planning screen');
 const proposalBase=new URL('../../design-engine/ferrite-maglev/planning-platform/',url).href,index=JSON.parse(await (await page.request.get(proposalBase+'index.json')).text()),baghdad=index.cities.find(c=>c.city==='baghdad');
 const cityPlan=JSON.parse(gunzipSync(Buffer.from(await (await page.request.get(proposalBase+baghdad.plan)).body())).toString());
 const selectedLineId=await page.locator('#line').inputValue(),selectedLine=cityPlan.lines.find(l=>l.id===selectedLineId),selectedStop=await stop.inputValue(),stopIndex=selectedLine.stops.findIndex(s=>s.id===selectedStop);
 expect(stopIndex).toBeGreaterThan(0);const insertion=(selectedLine.stops[stopIndex-1].chainage_m+Number(await page.locator('#chainage').inputValue()))/2;
 await page.locator('#chainage').fill(String(insertion));await page.locator('#new-stop-id').fill('proposal-stop-browser-check');await page.click('#add-stop');await expect(page.locator('#edit-status')).toContainText('3 proposed changes');
 await page.click('#retire-stop');await expect(page.locator('#edit-status')).toContainText('4 proposed changes');
 const download=page.waitForEvent('download');await page.click('#export');const file=await download;await file.saveAs(path.join(output,'edits.json'));
 const edits=JSON.parse(await readFile(path.join(output,'edits.json'),'utf8'));expect(edits.edits).toHaveLength(4);expect(edits.base_revision_sha256).toMatch(/^[0-9a-f]{64}$/);
 await page.click('#reset');await expect(page.locator('#export')).toBeDisabled();await expect(page.locator('#edit-status')).toContainText('discarded');
 await page.locator('#import').setInputFiles(path.join(output,'edits.json'));await expect(page.locator('#edit-status')).toContainText('4 proposed changes');
 // Import errors are transactional and cannot leave half an applied proposal.
 const stale=path.join(output,'stale.json');await writeFile(stale,JSON.stringify({...edits,base_revision_sha256:'f'.repeat(64)}));
 await page.locator('#import').setInputFiles(stale);await expect(page.locator('#edit-status')).toContainText('Stale');await expect(page.locator('#export')).toBeEnabled();
 const baseUrl=proposalBase;
 const manifest=await (await page.request.get(baseUrl+'manifest.json')).json();
 await page.route(baseUrl+baghdad.plan,async route=>{const response=await route.fetch(),bytes=Buffer.from(await response.body());bytes[bytes.length-1]^=1;await route.fulfill({response,body:bytes});});
 await page.selectOption('#city','garissa');await expect(page.locator('#status')).toContainText('bytes verified');
 await page.selectOption('#city','baghdad');await expect(page.locator('#status')).toContainText('differs from its receipt');expect(await page.locator('#map>*').count()).toBe(0);await expect(page.locator('#import')).toBeDisabled();
 await page.reload();await expect(page.locator('#status')).toContainText('differs from its receipt');await expect(page.locator('#move')).toBeDisabled();await page.unrouteAll();
 await page.reload();await expect(page.locator('#status')).toContainText('bytes verified');
 await page.screenshot({path:path.join(output,'planning-desktop.png'),fullPage:false});
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(output,'planning-mobile.png'),fullPage:false});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
 for(const privatePath of ['/build/maglev-pilot-native/private.env','/.git/config','/engineering/ferrite_maglev/data/candidate-protection-equipment.json'])expect((await page.request.get(new URL(privatePath,url).href)).status()).toBe(404);
 expect(errors).toEqual([]);expect(external).toEqual([]);
 const result={passed:true,cities:count,layers:16,browser_environment:browser.osrRendering,proposal_export_import:true,stale_import_refused:true,headway_hold_visible:true,payload_tamper_held:true,mobile:true,private_paths_rejected:true,errors,external,physical_release:false};
 await writeFile(path.join(output,'checks.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{await browser?.close();server.kill('SIGTERM');}
