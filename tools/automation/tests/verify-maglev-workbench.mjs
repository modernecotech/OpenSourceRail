// Exercise the actual primary server and default UI, including city changes.
import { chromium } from '@playwright/test';
import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';

const root = resolve(import.meta.dirname, '../../..');
const output = resolve(process.argv[2] || 'build/maglev-workbench-browser');
await mkdir(output, { recursive: true });
const server = spawn('tools/automation/osr-python', ['tools/automation/maglev-workbench.py', '--port', '0'], {cwd:root, stdio:['ignore','pipe','pipe']});
let browser;
let stderr = '';
server.stderr.on('data', chunk => { stderr += String(chunk); });
try {
  const origin = await new Promise((accept,reject) => {
    const timer = setTimeout(() => reject(Error('Primary server startup timeout: '+stderr)),30000);
    server.stdout.on('data', chunk => {
      const match = String(chunk).match(/http:\/\/127\.0\.0\.1:\d+/);
      if (match) { clearTimeout(timer); accept(match[0]); }
    });
    server.once('exit', code => { clearTimeout(timer); reject(Error(`Server exited ${code}: ${stderr}`)); });
  });
  browser = await chromium.launch({headless:true});
  const page = await browser.newPage({viewport:{width:1440,height:1000}});
  const errors=[], failures=[], external=[];
  page.on('pageerror', error => errors.push(String(error)));
  page.on('requestfailed', request => failures.push(request.url()));
  page.on('request', request => { if (!request.url().startsWith(origin+'/')) external.push(request.url()); });
  await page.goto(origin+'/');
  await page.waitForURL('**/docs/workbench/maglev/**');
  await page.waitForFunction(() => document.querySelector('#city-status').textContent.includes('Baghdad'));
  assert.equal(await page.locator('#city option').count(),266);
  await page.waitForFunction(() => [...document.images].every(image => image.complete && image.naturalWidth>0));
  assert.equal(await page.locator('img').count(),6);
  await page.getByText('Headway and coasting holds',{exact:true}).click();
  await page.getByText('Manufacturing and erection processes',{exact:true}).click();
  await page.getByText('UK industry equipment candidates and origin',{exact:true}).click();
  await page.screenshot({path:output+'/desktop.png',fullPage:true});
  const exercised=[];
  for (const city of ['kisangani','lubumbashi','garissa','baghdad']) {
    await page.selectOption('#city',city);
    await page.waitForFunction(city => new URL(location.href).searchParams.get('city') === city,city);
    const link = await page.locator('#city-links a[data-kind="summary"]').getAttribute('href');
    const response = await page.request.get(new URL(link, origin).href);
    const summary = await response.json();
    assert.equal(summary.city,city);
    assert.equal(summary.architecture,'ferrite-pm-maglev-study');
    assert.equal(summary.physical_release,false);
    const manufacturingLink = await page.locator('#city-links a[data-kind="manufacturing"]').getAttribute('href');
    const billResponse = await page.request.get(new URL(manufacturingLink, origin).href);
    assert.equal(billResponse.status(),200);
    const bill = await billResponse.json();
    const base = bill.scenarios.find(row => row.scenario === 'base');
    const dollars = new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0});
    assert.equal(await page.locator('[data-metric="fleet"]').innerText(),dollars.format(base.repeat_fleet_allowance_usd));
    assert.equal(await page.locator('[data-metric="civil"]').innerText(),dollars.format(base.ordinary_elevated_allowance_usd));
    assert.equal(await page.locator('[data-metric="station-electrical"]').innerText(),dollars.format(base.station_electrical_allowance_usd));
    assert.ok(base.station_electrical_allowance_usd > 0);
    assert.ok(Math.abs(base.priced_scope_subtotal_usd-base.repeat_fleet_allowance_usd-base.ordinary_elevated_allowance_usd-base.station_electrical_allowance_usd)<.01);
    const range = values => {
      const low=Math.min(...values),high=Math.max(...values);
      const text=v=>Number.isInteger(v)?String(v):v.toFixed(1);
      return low===high ? `${text(low)} s` : `${text(low)}–${text(high)} s`;
    };
    assert.equal(await page.locator('[data-metric="source-headway"]').innerText(),range(summary.lines.map(line=>line.retained_peak_headway_seconds)));
    assert.equal(await page.locator('[data-metric="selected-headway"]').innerText(),range(summary.lines.map(line=>line.selected_peak_headway_seconds)));
    const heldCases=summary.lines.reduce((sum,line)=>sum+line.kinematic_holds.length,0);
    assert.equal(await page.locator('[data-metric="coasting-holds"]').innerText(),String(heldCases));
    assert.equal(await page.locator('#city-service li[data-line]').count(),summary.lines.length);
    assert.equal(await page.locator('#city-service li[data-hold]').count(),heldCases);
    for(const line of summary.lines){
      assert.ok(line.selected_peak_headway_seconds>=190);
      assert.ok(line.selected_peak_headway_seconds>=line.retained_peak_headway_seconds);
      assert.ok(line.selected_peak_headway_seconds>=line.planning_minimum_headway_seconds);
      assert.equal(line.station_powered_kinematic_screen_pass,line.kinematic_holds.length===0);
    }
    assert.equal(bill.station_electrical_rating_qualified,false);
    assert.equal(await page.locator('[data-metric="partial-subtotal"]').innerText(),dollars.format(base.priced_scope_subtotal_usd));
    assert.match(await page.locator('[data-metric="complete-cost"]').innerText(),/Unknown.*unpriced/);
    assert.equal(bill.complete_city_programme_usd,null);
    assert.equal(await page.locator('#city-processes li').count(),bill.process_routes.length);
    assert.equal(await page.locator('#city-equipment li').count(),bill.equipment_candidates.length);
    assert.match(await page.locator('#city-equipment').innerText(),/UK manufacture/);
    const networkLink = await page.locator('#city-links a[data-kind="network"]').getAttribute('href');
    assert.equal(await page.locator('#city-map').getAttribute('src'),networkLink);
    const network = await page.request.get(new URL(networkLink, origin).href);
    assert.equal(network.status(),200);
    assert.match(await network.text(),/<svg/);
    await page.waitForFunction(() => document.querySelector('#city-map').complete && document.querySelector('#city-map').naturalWidth>0);
    exercised.push({city,base_partial_subtotal_usd:base.priced_scope_subtotal_usd,station_electrical_target_usd:base.station_electrical_allowance_usd,held_coasting_cases:heldCases,complete_city_programme_usd:null,process_routes:bill.process_routes.length});
  }
  for (const href of await page.locator('a').evaluateAll(nodes => nodes.map(node => node.href))) {
    const response = await page.request.get(href);
    assert.equal(response.status(),200,href);
  }
  // Corrupt a delivered bill while retaining its summary receipt. The UI must hold,
  // not show the injected cost or any previous city's result.
  const corruptedBill = '**/Kisangani/engineering/maglev/manufacturing.json';
  await page.route(corruptedBill, async route => {
    const response = await route.fetch();
    const body = await response.json();
    body.scenarios.find(row => row.scenario === 'base').priced_scope_subtotal_usd = 1;
    await route.fulfill({response,json:body});
  });
  await page.selectOption('#city','kisangani');
  await page.waitForFunction(() => document.querySelector('#city-status').textContent.includes('differ from their receipt'));
  assert.equal(await page.locator('#city-metrics dd').count(),0);
  assert.equal(await page.locator('#city-links a').count(),0);
  assert.equal(await page.locator('#city-map').isHidden(),true);
  await page.unroute(corruptedBill);
  // Even self-consistent byte receipts cannot turn a two-component subtotal
  // into a valid fleet+civil+station electrical bill. Exercise that UI guard.
  const indexURL=origin+'/engineering/ferrite_maglev/city-index.json';
  const forgedIndex=await (await page.request.get(indexURL)).json();
  const forgedRow=forgedIndex.cities.find(row=>row.city==='baghdad');
  const forgedPath='/'+forgedRow.package_path+'/';
  const forgedSummary=await (await page.request.get(origin+forgedPath+'summary.json')).json();
  const forgedBill=await (await page.request.get(origin+forgedPath+'manufacturing.json')).json();
  const forgedBase=forgedBill.scenarios.find(row=>row.scenario==='base');
  forgedBase.priced_scope_subtotal_usd=forgedBase.repeat_fleet_allowance_usd+forgedBase.ordinary_elevated_allowance_usd;
  const forgedBillBytes=JSON.stringify(forgedBill);
  forgedSummary.manufacturing_sha256=createHash('sha256').update(forgedBillBytes).digest('hex');
  const forgedSummaryBytes=JSON.stringify(forgedSummary);
  forgedRow.summary_sha256=createHash('sha256').update(forgedSummaryBytes).digest('hex');
  await page.route(indexURL,route=>route.fulfill({json:forgedIndex}));
  await page.route(origin+forgedPath+'summary.json',route=>route.fulfill({body:forgedSummaryBytes,contentType:'application/json'}));
  await page.route(origin+forgedPath+'manufacturing.json',route=>route.fulfill({body:forgedBillBytes,contentType:'application/json'}));
  await page.goto(origin+'/docs/workbench/maglev/?city=baghdad');
  await page.waitForFunction(()=>document.querySelector('#city-status').textContent.includes('Inconsistent partial cost scope'));
  assert.equal(await page.locator('#city-metrics dd').count(),0);
  assert.equal(await page.locator('#city-service li').count(),0);
  assert.equal(await page.locator('#city-map').isHidden(),true);
  await page.unroute(indexURL);
  await page.unroute(origin+forgedPath+'summary.json');
  await page.unroute(origin+forgedPath+'manufacturing.json');
  await page.goto(origin+'/docs/workbench/maglev/?city=baghdad');
  await page.waitForFunction(() => document.querySelector('#city-status').textContent.includes('Baghdad'));
  await page.waitForFunction(() => document.querySelector('#city-map').complete && document.querySelector('#city-map').naturalWidth>0);
  await page.setViewportSize({width:390,height:844});
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth<=innerWidth),'mobile horizontal overflow');
  await page.screenshot({path:output+'/mobile.png',fullPage:true});
  for (const path of ['/.git/config','/var/ops-core.sqlite3','/build/maglev-workflow/latest.json']) {
    assert.equal((await page.request.get(origin+path)).status(),404);
  }
  assert.deepEqual(errors,[]); assert.deepEqual(failures,[]); assert.deepEqual(external,[]);
  const result={primary_ui:true,cities:266,exercised,images:6,quantity_costs:true,station_electrical_separate:true,headway_and_coast_holds:true,omitted_station_cost_rejected:true,complete_cost_unknown:true,manufacturing_and_map_links:true,receipt_tampering_held:true,links:true,mobile:true,private_paths_rejected:true,errors,external,physical_release:false};
  await writeFile(output+'/checks.json',JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify(result));
} finally {
  await browser?.close();
  server.kill('SIGTERM');
}
