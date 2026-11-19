import assert from 'node:assert/strict';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve, join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {launchBrowser} from '../../../tools/automation/tests/browser-launch.mjs';

const root = fileURLToPath(new URL('../../../', import.meta.url));
const here = fileURLToPath(new URL('.', import.meta.url));
const out = resolve(process.argv[2] || here);
const origin = new URL(process.env.OSR_WORKBENCH || 'http://127.0.0.1:8090');
assert.equal(origin.hostname, '127.0.0.1');
await mkdir(out, {recursive:true});
const browser = await launchBrowser();
const page = await browser.newPage({viewport:{width:1440,height:960}, locale:'en-US', timezoneId:'UTC', deviceScaleFactor:1});
const records = {};
const digest = bytes => createHash('sha256').update(bytes).digest('hex');
const source = async name => digest(await readFile(join(root,name)));
async function capture(name, selector, sources, maxHeight = 960, lastSelector = null) {
  const target = page.locator(selector).first();
  await target.waitFor({state:'visible'});
  await page.evaluate(() => document.fonts.ready);
  const box = await target.evaluate((element, lastSelector) => {
    element.scrollIntoView({block:'start',behavior:'instant'});
    const r = element.getBoundingClientRect();
    const end = lastSelector ? document.querySelector(lastSelector).getBoundingClientRect().bottom : r.bottom;
    return {x:r.left, y:r.top, width:r.width, height:Math.min(end-r.top, innerHeight-r.top)};
  }, lastSelector);
  assert(box.width > 240 && box.height > 60, name);
  const clip = {x:Math.floor(box.x),y:Math.floor(box.y),width:Math.floor(box.width),height:Math.floor(Math.min(maxHeight,box.height))};
  const bytes = await page.screenshot({path:join(out,name+'.png'),clip,animations:'disabled'});
  records[name] = {view:selector, width:bytes.readUInt32BE(16),height:bytes.readUInt32BE(20),sha256:digest(bytes),
    sources:Object.fromEntries(await Promise.all(sources.map(async file => [file,await source(file)])))};
  console.log(name, clip.width, clip.height);
}
const workbench = 'engineering/development_baseline/web/';
const cityAtlas = 'docs/design-engine/city-atlas/cities/samawah.json.gz';
try {
  await page.goto(new URL('/docs/operator-review/screens/supervision.html',origin).href);
  await page.selectOption('#event','2');
  assert.equal(await page.locator('#stale').innerText(),'1');
  assert.equal(await page.locator('#alarms').innerText(),'1');
  await capture('section-alarm','body',[
    'docs/operator-review/screens/supervision.html','docs/operator-review/screens/replay-data.js',
    'docs/operator-review/screens/replay.py','docs/operator-review/screens/supervision.js','docs/operator-review/screens/supervision.css','services/integration/osr_integration/store.py',
    'services/integration/osr_integration/v07_supervision.py','control-electronics/interface-schedule.json']);
  await page.goto(new URL('/docs/design-engine/station-pair/index.html',origin).href);
  await page.locator('#trace-chart svg').waitFor();
  await capture('train-movement','#traces',['docs/design-engine/station-pair/summary.json','docs/design-engine/station-pair/app.js']);
  await page.goto(new URL('/docs/workbench/current/?outlineCity=samawah',origin).href);
  await page.locator('.atlas-service-table tbody tr').first().waitFor({timeout:60000});
  await capture('route-inspector','.atlas-layout',[cityAtlas,workbench+'city-atlas.js'],820);
  const journey = page.locator('.atlas-journeys');
  await journey.locator('select').last().selectOption({index:2});
  await journey.locator('button').click();
  assert(await journey.locator('ol li').count() > 0);
  await capture('passenger-journey','.atlas-journeys',[cityAtlas,workbench+'city-journeys.js']);
  await page.locator('.atlas-finance summary').click();
  await page.locator('.atlas-finance input').nth(0).fill('10000000');
  await page.locator('.atlas-finance input').nth(1).fill('0.75');
  await page.locator('.atlas-finance button').click();
  assert.match(await page.locator('.atlas-finance').innerText(),/cost-covering average fare/i);
  await capture('fare-scenario','.atlas-finance',[cityAtlas,workbench+'city-atlas.js']);
  const doorResponse = page.waitForResponse(r => new URL(r.url()).pathname === '/api/v07/door-module');
  await page.locator('#samawah-door-module button').first().click();
  await page.locator('#samawah-door-part').waitFor();
  await page.locator('#samawah-door-part').selectOption({index:1});
  await capture('door-workshop','label:has(#samawah-door-part)',[workbench+'city-atlas.js','engineering/vehicle_parts/door_module.py'],960,'.atlas-door-part');
  const door = await (await doorResponse).json();
  records['door-workshop'].part = await page.locator('#samawah-door-part').inputValue();
  records['door-workshop'].identity = Object.fromEntries(Object.entries(door).filter(([key,value]) => key.endsWith('_id') && typeof value === 'string'));
  const baghdadResponse = page.waitForResponse(r => new URL(r.url()).pathname === '/api/v07/baghdad-system' && r.request().method() === 'POST');
  await page.locator('#baghdad-system-edit button').click();
  await page.locator('#baghdad-system-measures tr').first().waitFor();
  await capture('baghdad-options','#baghdad-system',['cities/Baghdad/system.toml',workbench+'index.html'],530,'#baghdad-system-status');
  await capture('baghdad-system','#baghdad-system-results table',['cities/Baghdad/system.toml','cities/Baghdad/system-results.json',workbench+'app.js','engineering/outline/baghdad_system.py']);
  const result = await (await baghdadResponse).json();
  records['baghdad-system'].identity = {physical:result.physical_candidate_id,civil:result.civil.physical_candidate_id,evaluation:result.evaluation_id};
  if (process.env.OSR_ERP_FIXTURE) {
    const credentials = JSON.parse(await readFile(process.env.OSR_ERP_FIXTURE,'utf8')).users.inspector;
    const response = await page.request.post('http://127.0.0.1:18088/api/method/login',{data:{usr:credentials.user,pwd:credentials.password}});
    assert(response.ok(),'Local fixture login failed');
    await page.goto('http://127.0.0.1:18088/maglev-pilot');
    const card = page.locator('.pilot-card').first();
    await card.locator('summary').click();
    await capture('erp-serial-history','.pilot-card',['deployment/erpnext/apps/osr_erpnext/osr_erpnext/www/maglev-pilot.html']);
  }
  await writeFile(join(out,'captures.json'),JSON.stringify({browser:browser.version(),records},null,2)+'\n');
} finally { await browser.close(); }
