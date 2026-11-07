import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const require=createRequire(import.meta.url),{chromium}=require('playwright');
const root=process.cwd(),input=path.resolve(process.env.OSR_PARTS_HTML||'docs/design-engine/vehicle-parts/index.html');
const output=process.env.OSR_PARTS_CAPTURE;const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1500,height:1100},deviceScaleFactor:1});const errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(process.env.OSR_PARTS_URL||pathToFileURL(input).href);await page.getByRole('heading',{name:'Vehicle parts and assembly',exact:true}).waitFor();
 const model=JSON.parse(await page.locator('#data').textContent());
 assert.equal(model.parts.length,605);assert.equal(model.assemblies.length,40);
 assert.equal(await page.locator('#rows tr').count(),model.parts.length);
 await page.locator('#assembly').selectOption('running/passenger-gangway');
 const gangways=model.parts.filter(p=>p.assembly_id==='running/passenger-gangway');
 assert.equal(await page.locator('#rows tr').count(),gangways.length);
 await page.locator('button.part').first().click();assert.match(await page.locator('#detail').textContent(),/per train/);
 await page.locator('#assembly').selectOption('');await page.locator('#search').fill('services/led-board');
 assert.equal(await page.locator('#rows tr').count(),1);await page.locator('button.part').click();
 assert.match(await page.locator('#detail').textContent(),/24V regulated12W LED/);
 await page.locator('#search').fill('no-such-part-xyz');assert.equal(await page.locator('#rows tr').count(),0);assert.equal(await page.locator('#empty').isVisible(),true);
 await page.locator('#search').fill('');await page.locator('#make').selectOption('local-fabricate');
 assert.equal(await page.locator('#rows tr').count(),model.parts.filter(p=>p.make_buy==='local-fabricate').length);
 await page.locator('#make').selectOption('');await page.locator('#assembly').selectOption('body/underframe');
 await page.locator('button.part[data-id="body/side-sill"]').click();
 assert.match(await page.locator('.stock').textContent(),/17,000 mm/);
 if(output){fs.mkdirSync(output,{recursive:false});await page.screenshot({path:path.join(output,'catalogue-preview.png'),fullPage:false})}
 await page.setViewportSize({width:390,height:844});
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Mobile page overflows horizontally');
 assert.equal(await page.locator('#detail h2').textContent(),'Full-length lower side sill');
 if(output)await page.screenshot({path:path.join(output,'catalogue-mobile.png'),fullPage:true});
 assert.deepEqual(errors,[]);
 console.log(JSON.stringify({verified:true,candidate_id:model.candidate_id,bundle_id:model.bundle_id,parts:model.parts.length,assemblies:model.assemblies.length,desktop_mobile:true,filter_selection_stock_sketch:true,native_execution:false}));
}finally{await browser.close()}
