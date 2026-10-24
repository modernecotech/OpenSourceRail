// Exercise the actual primary server and default UI, including city changes.
import { launchBrowser } from './browser-launch.mjs';
import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { createHash } from 'node:crypto';
import { gunzipSync, gzipSync } from 'node:zlib';
import assert from 'node:assert/strict';

const costTerms=['repeat_fleet_allowance_usd','ordinary_elevated_allowance_usd','terminal_civil_allowance_usd','station_electrical_allowance_usd','conditional_foundation_increment_usd','booster_electrical_allowance_usd','booster_mount_allowance_usd','rescue_kit_allowance_usd'];
const root = resolve(import.meta.dirname, '../../..');
const output = resolve(process.argv[2] || 'build/maglev-workbench-browser');
await mkdir(output, { recursive: true });
const server = spawn('tools/automation/osr-python', ['tools/automation/maglev-workbench.py', '--port', '0'], {cwd:root, stdio:['ignore','pipe','pipe']});
let browser;
let stderr = '';
server.stderr.on('data', chunk => { stderr += String(chunk); });
try {
  const origin = await new Promise((accept,reject) => {
    // The server verifies every source-bound packet before binding. The expanded
    // native body, pilot and hub checks can exceed ten minutes on a cold process.
    // Allow thirty minutes for complete verification; UI assertion bounds stay unchanged.
    const timer = setTimeout(() => reject(Error('Primary server startup timeout: '+stderr)),1800000);
    server.stdout.on('data', chunk => {
      const match = String(chunk).match(/http:\/\/127\.0\.0\.1:\d+/);
      if (match) { clearTimeout(timer); accept(match[0]); }
    });
    server.once('exit', code => { clearTimeout(timer); reject(Error(`Server exited ${code}: ${stderr}`)); });
  });
  browser = await launchBrowser({headless:true});
  const page = await browser.newPage({viewport:{width:1440,height:1000}});
  const errors=[], failures=[], external=[];
  page.on('pageerror', error => errors.push(String(error)));
  page.on('requestfailed', request => failures.push(request.url()));
  page.on('request', request => { if (!request.url().startsWith(origin+'/') && !request.url().startsWith('blob:'+origin+'/')) external.push(request.url()); });
  await page.goto(origin+'/');
  await page.waitForURL('**/docs/workbench/maglev/**');
  await page.waitForFunction(() => document.querySelector('#city-status').textContent.includes('Baghdad'));
  await page.waitForFunction(() => document.querySelector('#pilot-status').textContent.includes('connected digital packets verified'));
  const pilotPath=origin+'/docs/design-engine/ferrite-maglev/pilot-delivery/';
  const pilotManifest=await (await page.request.get(pilotPath+'manifest.json')).json();
  const pilotBytes=await (await page.request.get(pilotPath+'study.json')).body();
  assert.equal(createHash('sha256').update(pilotBytes).digest('hex'),pilotManifest.files_sha256['study.json']);
  const pilotStudy=JSON.parse(pilotBytes.toString('utf8'));
  assert.equal(pilotStudy.components.length,9);
  assert.equal(await page.locator('#pilot-view option').count(),9);
  assert.equal(await page.locator('#pilot-deliverables tr').count(),6);
  assert.ok((await page.locator('#pilot-detail').innerText()).includes('component-accounted tare'));
  async function pilotView(id,imageCount) {
    const component=pilotStudy.components.find(row=>row.id===id);
    assert.ok(component,'declared pilot view '+id);
    await page.selectOption('#pilot-view',id);
    await page.waitForFunction(({id,readme,imageCount})=>{
      const images=[...document.querySelectorAll('#pilot-detail img')];
      return document.querySelector('#pilot-view').value===id &&
        document.querySelector('#pilot-status').textContent.includes('connected digital packets verified') &&
        [...document.querySelectorAll('#pilot-detail a')].some(a=>a.getAttribute('href')===readme) &&
        images.length===imageCount && images.every(image=>image.complete && image.naturalWidth>0);
    },{id,readme:'/'+component.packet+'/README.md',imageCount});
    return component.summary;
  }
  await pilotView('assurance-profiles',0);
  assert.ok((await page.locator('#pilot-detail').innerText()).includes('control-formal'));
  await pilotView('capability-migration',0);
  assert.ok((await page.locator('#pilot-detail').innerText()).includes('missing'));
  await pilotView('candidate-finance',2);
  const candidate=pilotStudy.components.find(row=>row.id==='candidate-finance').summary;
  assert.equal(candidate.assembly_media.configuration_sha256,candidate.configuration_sha256);
  assert.equal(candidate.assembly_media.physical_accepted,false);
  assert.ok((await page.locator('#pilot-detail img').last().getAttribute('alt')).includes('Exact larger-winding candidate'));
  const candidateVideo=page.locator('#pilot-detail a').filter({hasText:'View current-candidate replacement translations'});
  const candidateVideoURL=await candidateVideo.getAttribute('href');
  assert.ok(candidateVideoURL.startsWith('blob:'+origin+'/'));
  const candidateVideoBytes=await page.evaluate(async url=>Array.from(new Uint8Array(await (await fetch(url)).arrayBuffer())),candidateVideoURL);
  const candidateRow=pilotStudy.components.find(row=>row.id==='candidate-finance');
  const candidateReceipt=await (await page.request.get(origin+'/'+candidateRow.packet+'/manifest.json')).json();
  assert.equal(createHash('sha256').update(Buffer.from(candidateVideoBytes)).digest('hex'),candidateReceipt.files_sha256[candidate.assembly_media.files.video]);
  const candidateText=await page.locator('#pilot-detail').innerText();
  assert.ok(candidateText.includes(candidate.configuration_sha256));
  assert.ok(candidateText.includes(candidate.base_configuration_sha256));
  assert.ok(candidateText.includes('Separate retained base capital'));
  assert.ok(candidateText.includes('no city-default adoption or physical qualification'));
  if (candidate.financial_view) {
    const dollars=new Intl.NumberFormat('en-GB',{style:'currency',currency:'USD',maximumFractionDigits:0});
    assert.ok(candidateText.includes(dollars.format(candidate.financial_view.capital_usd)));
    assert.ok(candidateText.includes(dollars.format(candidate.financial_view.annual_opex_usd)));
    assert.ok(candidateText.includes(dollars.format(candidate.base_reference.capital_usd)));
  } else assert.ok(candidateText.includes('Candidate finance remains held'));
  await page.setViewportSize({width:390,height:844});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'exact candidate identities must fit the mobile evidence view');
  await page.screenshot({path:output+'/candidate-mobile.png',fullPage:true});
  await page.setViewportSize({width:1440,height:1000});
  const coupled=await pilotView('coupled-actuators',2);
  const coupledText=await page.locator('#pilot-detail').innerText();
  for (const hold of coupled.holds) assert.ok(coupledText.includes(hold),'coupled view must expose '+hold);
  const measurement=new Intl.NumberFormat('en-GB',{maximumFractionDigits:1});
  for (const repair of coupled.repair_candidates) {
    assert.ok(coupledText.includes(repair.body_variant+' / '+repair.winding_variant));
    assert.ok(coupledText.includes(measurement.format(repair.magnetic_geometry.assumed_gap_pole_area_m2*1e6)+' mm²'));
    assert.ok(coupledText.includes(measurement.format(repair.magnetic_geometry.winding_inner_aperture_m2*1e6)+' mm²'));
  }
  assert.ok(coupledText.includes('Unreconciled') && coupledText.includes('Unqualified'));
  assert.ok(coupledText.includes('Independent actual module-force screen'));
  assert.ok(coupledText.includes(measurement.format(pilotStudy.coupled_actual_module_force.observed_peak_n)+' N'));
  assert.ok(coupledText.includes(measurement.format(pilotStudy.coupled_actual_module_force.limit_n)+' N'));
  assert.ok((await page.locator('#pilot-detail img').last().getAttribute('alt')).includes('Larger-winding candidate bay'));
  await page.screenshot({path:output+'/coupled-actuators.png',fullPage:true});
  await pilotView('pilot-corridor',1);
  assert.ok((await page.locator('#pilot-detail').innerText()).includes('Protected minimum separation'));
  assert.ok((await page.locator('#pilot-detail img').getAttribute('alt')).includes('open-map walk network'));
  await pilotView('resource-delivery',1);
  assert.ok((await page.locator('#pilot-detail img').getAttribute('alt')).includes('finite capacity'));
  const launchOptions=await pilotView('launch-options',0);
  const launchText=await page.locator('#pilot-detail').innerText();
  assert.ok(launchOptions.research_recommendation,'retained launch recommendation is required');
  assert.ok(launchText.includes('Research groups per direction') && launchText.includes('Winding heat per trip'));
  assert.ok(launchText.includes('has not passed moving local-phase and handover constraints'));
  assert.ok(launchText.includes('remain unqualified'));
  const native=await pilotView('native-lifecycle',1);
  assert.equal(native.native.state,'executed-current');
  assert.ok((await page.locator('#pilot-detail img').getAttribute('alt')).includes('Actual authenticated current-maglev pilot Workbench'));
  const nativeDimensions=await page.locator('#pilot-detail img').evaluate(image=>({width:image.naturalWidth,height:image.naturalHeight}));
  assert.ok(nativeDimensions.width>500 && nativeDimensions.height>500,'genuine native Workbench screenshot must not be a placeholder');
  await pilotView('controlled-product',1);
  assert.ok((await page.locator('#pilot-detail').innerText()).includes('reference-bay'));
  assert.equal(await page.locator('#city option').count(),266);
  await page.waitForFunction(() => [...document.images].every(image => image.complete && image.naturalWidth>0));
  await page.waitForFunction(()=>{const image=document.querySelector('#pilot-detail img');return image?.complete && image.naturalWidth>0;});
  assert.equal(await page.locator('#city-map, #hub-map, .cards img').count(),10);
  const hubPath=origin+'/docs/design-engine/ferrite-maglev/interchange-hubs/';
  const hubManifest=await (await page.request.get(hubPath+'manifest.json')).json();
  const hubBytes=await (await page.request.get(hubPath+'study.json.gz')).body();
  assert.equal(createHash('sha256').update(hubBytes).digest('hex'),hubManifest.files_sha256['study.json.gz']);
  const hubStudy=JSON.parse(gunzipSync(hubBytes).toString('utf8'));
  const hubConflicts=hubStudy.baseline.line_screens.reduce((sum,line)=>sum+line.spacing_conflicts.length,0);
  assert.ok((await page.locator('#hub-status').innerText()).includes(`${hubStudy.baseline.operating_station_count} proposed stops and ${hubConflicts} spacing conflicts`));
  assert.match(await page.locator('#hub-status').innerText(),/none selected/);
  assert.equal(await page.locator('#hub-map').getAttribute('src'),'/docs/design-engine/ferrite-maglev/interchange-hubs/overview.svg');
  await page.getByText('Operating stops, capacity and coasting holds',{exact:true}).click();
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
    assert.equal(await page.locator('[data-metric="terminal-civil"]').innerText(),dollars.format(base.terminal_civil_allowance_usd));
    assert.equal(await page.locator('[data-metric="foundation-increment"]').innerText(),dollars.format(base.conditional_foundation_increment_usd));
    assert.equal(await page.locator('[data-metric="booster-electrical"]').innerText(),dollars.format(base.booster_electrical_allowance_usd));
    assert.equal(await page.locator('[data-metric="booster-mounts"]').innerText(),dollars.format(base.booster_mount_allowance_usd));
    assert.equal(await page.locator('[data-metric="rescue-cost"]').innerText(),dollars.format(base.rescue_kit_allowance_usd));
    assert.equal(await page.locator('[data-metric="booster-zones"]').innerText(),String(summary.totals.powered_top_up_zones));
    assert.equal(await page.locator('[data-metric="rescue-kits"]').innerText(),String(summary.totals.rescue_kits));
    assert.equal(await page.locator('[data-metric="spacing-conflicts"]').innerText(),String(summary.totals.transfer_spacing_conflicts));
    assert.match(await page.locator('[data-metric="eligible-designs"]').innerText(),/^0/);
    assert.ok(Math.abs(base.priced_scope_subtotal_usd-costTerms.reduce((sum,key)=>sum+base[key],0))<.01);
    assert.equal(await page.locator('[data-metric="retained-stops"]').innerText(),String(summary.totals.retained_station_records));
    assert.equal(await page.locator('[data-metric="operating-stops"]').innerText(),String(summary.totals.station_records));
    assert.equal(await page.locator('[data-metric="terminal-zones"]').innerText(),String(summary.totals.added_terminal_service_zones));
    assert.equal(await page.locator('[data-metric="capacity-shortfalls"]').innerText(),String(summary.lines.filter(line=>!line.retained_capacity_target_met).length));
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
    assert.equal(await page.locator('#city-service li[data-hold]').count(),summary.lines.reduce((sum,line)=>sum+Math.min(8,line.kinematic_holds.length),0));
    assert.equal(await page.locator('#city-service li[data-design-hold]').count(),summary.lines.reduce((sum,line)=>sum+Math.min(5,line.system_design_holds.length),0));
    assert.equal(await page.locator('#city-service li[data-spacing-hold]').count(),summary.lines.reduce((sum,line)=>sum+Math.min(5,line.operating_plan.spacing_conflicts.length),0));
    for(const line of summary.lines){
      assert.ok(line.selected_peak_headway_seconds>=180);
      assert.ok(line.selected_peak_headway_seconds>=line.retained_peak_headway_seconds);
      assert.ok(line.selected_peak_headway_seconds>=line.planning_minimum_headway_seconds);
      assert.equal(line.station_powered_kinematic_screen_pass,line.kinematic_holds.length===0);
      const displayed=await page.locator('#city-service li[data-line]').filter({hasText:line.line+':'}).innerText();
      assert.ok(displayed.includes(`${line.operating_plan.operating_station_count} proposed mainline stops versus ${line.operating_plan.retained_station_count} original access records`));
      assert.equal(line.retained_capacity_target_met,line.aw2_capacity_per_direction_hour>=line.source_aw2_capacity_per_direction_hour);
      assert.equal(line.charging.rating_selected,false);
      assert.ok(line.charging.source_input_kw_per_car>0);
      assert.equal(line.charging.conversion_efficiency_study,.9);
      assert.equal(line.charging.converted_output_kw_per_car,line.charging.source_input_kw_per_car*line.charging.conversion_efficiency_study);
      assert.equal(line.selected_eligible_operating_design,null);
      assert.equal(line.operating_plan.physical_train_switches_proposed,0);
      assert.equal(line.passenger_spacing_screen_pass,line.operating_plan.spacing_conflicts.length===0);
      assert.ok(line.operating_plan.powered_top_up_zones.every(zone=>zone.mechanical_takeoff.passenger_station===false));
      assert.ok(line.operating_plan.rescue_nodes.every(node=>node.access_approved===false));
    }
    assert.equal(bill.station_electrical_rating_qualified,false);
    assert.equal(await page.locator('[data-metric="partial-subtotal"]').innerText(),dollars.format(base.priced_scope_subtotal_usd));
    assert.match(await page.locator('[data-metric="complete-cost"]').innerText(),/Unknown.*unpriced/);
    const budget=summary.affordability.cases.find(item=>item.id==='base');
    assert.equal(await page.locator('[data-metric="budget-capex"]').innerText(),dollars.format(budget.budget_capex_sensitivity_usd));
    if(budget.energy_data_complete) {
      assert.equal(await page.locator('[data-metric="budget-opex"]').innerText(),dollars.format(budget.annual_opex_sensitivity_usd));
      assert.equal(await page.locator('[data-metric="budget-debt"]').innerText(),dollars.format(budget.financing.annual_level_debt_service_usd));
      assert.equal(await page.locator('[data-metric="lifetime-cash"]').innerText(),dollars.format(budget.financing.undiscounted_public_cash_usd));
      assert.equal(await page.locator('[data-metric="foreign-debt"]').innerText(),dollars.format(budget.financing.foreign_currency_debt_usd));
    } else assert.match(await page.locator('[data-metric="budget-debt"]').innerText(),/^HOLD/);
    const briefResponse=await page.request.get(origin+'/'+link.split('/').filter(Boolean).slice(0,-3).join('/')+'/README.md');
    assert.equal(briefResponse.status(),200);
    const brief=await briefResponse.text();
    for(const text of ['## Lines and service','Annual OPEX','Annual debt service','Station-led GOA4','Domestic productive capacity']) assert.ok(brief.includes(text));
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
    exercised.push({city,retained_access_records:summary.totals.retained_station_records,operating_stops:summary.totals.station_records,terminal_motor_zones:summary.totals.added_terminal_service_zones,base_partial_subtotal_usd:base.priced_scope_subtotal_usd,station_electrical_target_usd:base.station_electrical_allowance_usd,held_coasting_cases:heldCases,complete_city_programme_usd:null,process_routes:bill.process_routes.length});
  }
  for (const href of await page.locator('a').evaluateAll(nodes => nodes.map(node => node.href))) {
    if (href.startsWith('blob:'+origin+'/')) {
      const length=await page.evaluate(async url=>(await (await fetch(url)).arrayBuffer()).byteLength,href);
      assert.ok(length>0,'verified video Blob must contain actual bytes');
      continue;
    }
    const response = await page.request.get(href);
    assert.equal(response.status(),200,href);
  }
  // The connected study and child receipts stay genuine. Only delivered visual
  // bytes change: neither an image nor a stale success status may survive.
  const poisonedVisuals=[
    {id:'controlled-product',path:'pilot-product/bay-views.svg',body:Buffer.from('<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80"><text x="0" y="20">CORRUPTED BAY</text></svg>'),contentType:'image/svg+xml'},
    {id:'candidate-finance',path:'pilot-variants/candidate-bay-poster.png',body:Buffer.from('corrupt candidate poster'),contentType:'image/png'},
    {id:'candidate-finance',path:'pilot-variants/candidate-bay-replacement.mp4',body:Buffer.from('corrupt candidate video'),contentType:'video/mp4'},
    {id:'native-lifecycle',path:'pilot-lifecycle/native-workbench.png',body:Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=','base64'),contentType:'image/png'},
  ];
  assert.equal(pilotStudy.components.find(r=>r.id==='native-lifecycle').summary.native.state,'executed-current');
  for (const visual of poisonedVisuals) {
    const url=origin+'/docs/design-engine/ferrite-maglev/'+visual.path;
    let replaced=false;
    await page.route(url,async route=>{replaced=true;await route.fulfill({body:visual.body,contentType:visual.contentType});});
    await page.selectOption('#pilot-view','assurance-profiles');
    await page.waitForFunction(()=>document.querySelector('#pilot-status').textContent.includes('connected digital packets verified'));
    await page.selectOption('#pilot-view',visual.id);
    await page.waitForFunction(()=>document.querySelector('#pilot-status').textContent.includes('differs from its receipt'));
    assert.ok(replaced,visual.path+' must exercise the delivered image route');
    assert.equal(await page.locator('#pilot-detail img').count(),0,'corrupt image must not be inserted');
    assert.equal(await page.locator('#pilot-detail a').count(),0,'failed view must not leave links or video');
    await page.unroute(url);
    await page.selectOption('#pilot-view','assurance-profiles');
    await page.waitForFunction(()=>document.querySelector('#pilot-detail').textContent.includes('control-formal'));
    await page.waitForFunction(()=>document.querySelector('#pilot-status').textContent.includes('connected digital packets verified'));
    assert.ok(!(await page.locator('#pilot-status').innerText()).includes('differs from its receipt'),'successful selection must clear stale error');
  }
  // Rehash parent/child metadata while emptying only the video digest. The image
  // remains valid: this separately proves that a missing digest cannot opt out.
  const productRow=pilotStudy.components.find(r=>r.id==='controlled-product');
  const productManifestURL=origin+'/'+productRow.packet+'/manifest.json';
  const missingVideoManifest=await (await page.request.get(productManifestURL)).json();
  missingVideoManifest.files_sha256['bay-replacement.mp4']='';
  const missingVideoManifestBytes=JSON.stringify(missingVideoManifest);
  const missingVideoStudy=structuredClone(pilotStudy);
  missingVideoStudy.components.find(r=>r.id==='controlled-product').manifest_sha256=createHash('sha256').update(missingVideoManifestBytes).digest('hex');
  const missingVideoStudyBytes=JSON.stringify(missingVideoStudy),missingVideoRoot=structuredClone(pilotManifest);
  missingVideoRoot.files_sha256['study.json']=createHash('sha256').update(missingVideoStudyBytes).digest('hex');
  await page.route(pilotPath+'manifest.json',route=>route.fulfill({json:missingVideoRoot}));
  await page.route(pilotPath+'study.json',route=>route.fulfill({body:missingVideoStudyBytes,contentType:'application/json'}));
  await page.route(productManifestURL,route=>route.fulfill({body:missingVideoManifestBytes,contentType:'application/json'}));
  await page.reload();
  await page.waitForFunction(()=>document.querySelector('#pilot-status').textContent.includes('Missing pilot payload identity'));
  assert.equal(await page.locator('#pilot-detail img').count(),0);
  assert.equal(await page.locator('#pilot-detail a').count(),0);
  await page.unroute(pilotPath+'manifest.json');await page.unroute(pilotPath+'study.json');await page.unroute(productManifestURL);
  await page.reload();
  await page.waitForFunction(()=>document.querySelector('#pilot-status').textContent.includes('connected digital packets verified'));
  await page.waitForFunction(()=>{const image=document.querySelector('#pilot-detail img');return image?.complete && image.naturalWidth>0;});
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
  // Even self-consistent byte receipts cannot omit a priced component from the
  // eight-term bill. Exercise the arithmetic guard independently of hashes.
  const indexURL=origin+'/engineering/ferrite_maglev/city-index.json';
  const forgedIndex=await (await page.request.get(indexURL)).json();
  const forgedRow=forgedIndex.cities.find(row=>row.city==='baghdad');
  const forgedPath='/'+forgedRow.package_path+'/';
  const forgedSummary=await (await page.request.get(origin+forgedPath+'summary.json')).json();
  const forgedBill=await (await page.request.get(origin+forgedPath+'manufacturing.json')).json();
  const forgedBase=forgedBill.scenarios.find(row=>row.scenario==='base');
  assert.ok(forgedBase.rescue_kit_allowance_usd>0);
  forgedBase.priced_scope_subtotal_usd=costTerms.filter(key=>key!=='rescue_kit_allowance_usd').reduce((sum,key)=>sum+forgedBase[key],0);
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
  // Rehashed lifecycle cash must not double-count financed capital.
  const badFinance=await (await page.request.get(origin+forgedPath+'summary.json')).json();
  badFinance.affordability.cases[1].financing.undiscounted_public_cash_usd+=badFinance.affordability.cases[1].financing.debt_principal_usd;
  const badFinanceBytes=JSON.stringify(badFinance);
  forgedRow.summary_sha256=createHash('sha256').update(badFinanceBytes).digest('hex');
  await page.route(indexURL,route=>route.fulfill({json:forgedIndex}));
  await page.route(origin+forgedPath+'summary.json',route=>route.fulfill({body:badFinanceBytes,contentType:'application/json'}));
  await page.goto(origin+'/docs/workbench/maglev/?city=baghdad');
  await page.waitForFunction(()=>document.querySelector('#city-status').textContent.includes('Inconsistent lifecycle cash accounting'));
  assert.equal(await page.locator('#city-metrics dd').count(),0);
  await page.unroute(indexURL);await page.unroute(origin+forgedPath+'summary.json');
  // A changed investigation payload must hide its map and counts independently
  // of the still-valid city plan.
  const corruptHubs=hubPath+'study.json.gz';
  await page.route(corruptHubs,async route=>{const response=await route.fetch();const body=Buffer.from(await response.body());body[body.length-1]^=1;await route.fulfill({response,body});});
  await page.goto(origin+'/docs/workbench/maglev/?city=baghdad');
  await page.waitForFunction(()=>document.querySelector('#hub-status').textContent.includes('Interchange investigation held:'));
  assert.equal(await page.locator('#hub-map').isHidden(),true);
  assert.ok(!(await page.locator('#hub-status').innerText()).includes('proposed stops'));
  await page.unroute(corruptHubs);
  // Rehash a highly compressible oversized stream so checksum validation passes.
  // Its output must stop at the declared raw budget before JSON accumulation.
  const inflatedBody=gzipSync(Buffer.alloc(2*1024*1024,32));
  const undersizedManifest=structuredClone(hubManifest);
  undersizedManifest.raw_bytes=1024;undersizedManifest.compressed_bytes=inflatedBody.length;
  undersizedManifest.files_sha256['study.json.gz']=createHash('sha256').update(inflatedBody).digest('hex');
  await page.route(hubPath+'manifest.json',route=>route.fulfill({json:undersizedManifest}));
  await page.route(corruptHubs,route=>route.fulfill({body:inflatedBody,contentType:'application/gzip'}));
  await page.goto(origin+'/docs/workbench/maglev/?city=baghdad');
  await page.waitForFunction(()=>document.querySelector('#hub-status').textContent.includes('raw size exceeds its budget'));
  assert.equal(await page.locator('#hub-map').isHidden(),true);
  assert.ok(!(await page.locator('#hub-status').innerText()).includes('proposed stops'));
  await page.unroute(hubPath+'manifest.json');await page.unroute(corruptHubs);
  await page.goto(origin+'/docs/workbench/maglev/?city=baghdad');
  await page.waitForFunction(() => document.querySelector('#city-status').textContent.includes('Baghdad'));
  await page.waitForFunction(() => document.querySelector('#city-map').complete && document.querySelector('#city-map').naturalWidth>0);
  await page.waitForFunction(()=>document.querySelector('#hub-map').complete && document.querySelector('#hub-map').naturalWidth>0);
  await page.setViewportSize({width:390,height:844});
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth<=innerWidth),'mobile horizontal overflow');
  await page.screenshot({path:output+'/mobile.png',fullPage:true});
  for (const path of ['/.git/config','/var/ops-core.sqlite3','/build/maglev-workflow/latest.json']) {
    assert.equal((await page.request.get(origin+path)).status(),404);
  }
  assert.deepEqual(errors,[]); assert.deepEqual(failures,[]); assert.deepEqual(external,[]);
  const result={browser_environment:browser.osrRendering,primary_ui:true,cities:266,exercised,images:10,pilot_packets:9,candidate_finance_separate:true,current_candidate_media_verified:true,coupled_images_and_magnetic_holds:true,independent_module_force_visible:true,pilot_access_and_resource_charts:true,native_workbench_screenshot:true,pilot_visual_tampering_held:true,missing_video_digest_held:true,pilot_image_decode_required:true,pilot_error_recovery:true,unselected_interchange_investigation:true,interchange_payload_tampering_held:true,interchange_inflate_budget_held:true,quantity_costs:true,eight_term_subtotal:true,operating_access_and_capacity:true,station_electrical_separate:true,headway_and_coast_holds:true,omitted_rescue_cost_rejected:true,fixed_line_transfer_conflicts_visible:true,complete_cost_unknown:true,manufacturing_and_map_links:true,receipt_tampering_held:true,links:true,mobile:true,private_paths_rejected:true,errors,external,physical_release:false};
  await writeFile(output+'/checks.json',JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify(result));
} finally {
  await browser?.close();
  server.kill('SIGTERM');
}
