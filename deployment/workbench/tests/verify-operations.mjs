/** Isolated real gateway/browser acceptance, including offline shell and IndexedDB. */
import {chromium, expect} from '@playwright/test';
import {spawn} from 'node:child_process';
import {readFile, mkdir} from 'node:fs/promises';
import path from 'node:path';
import {setTimeout as delay} from 'node:timers/promises';
const root=process.cwd(), output=path.join(root,'build/operations-browser',String(process.pid));
await mkdir(output,{recursive:true});
const port=Number(process.env.OSR_OPERATIONS_TEST_PORT||8199), gatewayPort=port+1;
const server=spawn(process.env.OSR_TEST_PYTHON||'python3',['tools/automation/operations-pilot.py','--serve','--out',output,'--port',String(port),'--gateway-port',String(gatewayPort)],{cwd:root,stdio:['ignore','pipe','pipe']});
let logs='';server.stdout.on('data',data=>logs+=data);server.stderr.on('data',data=>logs+=data);
let browser;
try{
  let ready=false;
  for(let attempt=0;attempt<60;attempt++){
    if(server.exitCode!==null)throw new Error('Pilot server stopped: '+logs);
    try{ready=(await fetch(`http://127.0.0.1:${gatewayPort}/health`)).ok;}catch{}
    if(ready)break;await delay(250);
  }
  if(!ready)throw new Error('Pilot server unavailable: '+logs);
  const credentials=JSON.parse(await readFile(path.join(output,'credentials.json'),'utf8'));
  browser=await chromium.launch({headless:true});
  const context=await browser.newContext({serviceWorkers:'allow',viewport:{width:1440,height:1100}});
  const page=await context.newPage();const failures=[];page.on('pageerror',error=>failures.push(error.message));
  await page.goto(`http://127.0.0.1:${port}/docs/operating/operations/`);
  await page.locator('#credential').fill(credentials.operator);await page.locator('#connect').click();
  await expect(page.locator('#baseline')).toContainText('3 services');
  await page.locator('#trains input[value="T2"]').check();await page.locator('#workers input[value="W1"]').check();
  await page.locator('#resource').selectOption('AB');await page.locator('#closureEnd').fill('800');await page.locator('#addClosure').click();
  await page.locator('#resource').selectOption('charge-B-1');await page.locator('#closureEnd').fill('3600');await page.locator('#addClosure').click();
  await page.locator('#plan').click();await expect(page.locator('#planSummary')).toContainText('3 services retained');
  await expect(page.locator('#rosterTable')).not.toContainText('W1');await expect(page.locator('#fleetTable')).toContainText('charging');
  await page.screenshot({path:path.join(output,'planning.png'),fullPage:true});
  await page.locator('[data-view="exchange"]').click();
  const downloadPromise=page.waitForEvent('download');await page.locator('#format').selectOption('gtfs-rt');await page.locator('#export').click();
  const download=await downloadPromise;await download.saveAs(path.join(output,'trip-updates.pb'));
  await page.locator('[data-view="field"]').click();await page.locator('#credential').fill(credentials.maintainer);await page.locator('#refreshWork').click();
  await expect(page.locator('#workList')).toContainText('PILOT-WORK');
  await page.evaluate(()=>navigator.serviceWorker.ready);await page.waitForFunction(()=>!!navigator.serviceWorker.controller);
  await context.setOffline(true);
  await page.getByRole('button',{name:'Record work',exact:true}).click();
  await page.locator('input[data-reading="voltage"]').fill('48');await page.locator('input[data-reading="isolated"]').check();
  await page.locator('#photos').setInputFiles({name:'evidence.png',mimeType:'image/png',buffer:Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=','base64')});
  await page.getByRole('button',{name:'Save performed work for inspection'}).click();
  await expect(page.locator('#queue')).toContainText('queued');
  await page.reload();await page.locator('[data-view="field"]').click();await expect(page.locator('#queue')).toContainText('queued');
  await context.setOffline(false);await page.locator('#credential').fill(credentials.maintainer);await page.locator('#sync').click();
  await expect(page.locator('#queue')).toContainText('pending');
  await page.screenshot({path:path.join(output,'field-work.png'),fullPage:true});
  if(failures.length)throw new Error(failures.join('\n'));
  console.log(JSON.stringify({planning_and_combined_recovery:true,official_feed_download:true,offline_shell_reload:true,typed_readings_and_photo:true,indexeddb_queue:true,reconnect_gateway_acceptance:true,native_erp_delivery:false,output}));
}finally{
  if(browser)await browser.close();server.kill('SIGTERM');
  await new Promise(resolve=>{if(server.exitCode!==null)resolve();else{server.once('exit',resolve);setTimeout(()=>{server.kill('SIGKILL');resolve();},5000).unref();}});
}
