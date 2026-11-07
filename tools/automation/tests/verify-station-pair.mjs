import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile, mkdir, writeFile, realpath} from 'node:fs/promises';
import {resolve, extname, sep} from 'node:path';
import {launchBrowser} from './browser-launch.mjs';

// Read-only static HTTP fixture. This does not exercise Workbench APIs or claim
// an OS sandbox around candidate data. Chromium isolation is reported below.
const root = resolve(process.env.OSR_ROOT || process.cwd());
const site = resolve(root, 'docs/design-engine/station-pair');
const summary = JSON.parse(await readFile(resolve(site, 'summary.json'), 'utf8'));
const mime = {'.html':'text/html', '.js':'text/javascript', '.css':'text/css', '.json':'application/json', '.gz':'application/gzip'};
const server = createServer(async (request, response) => {
  // Chromium requests a site-wide icon independently of the exported viewer.
  if (request.url === '/favicon.ico') { response.writeHead(204);response.end();return; }
  try {
    const name = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
    const path = await realpath(resolve(root, '.' + (name.endsWith('/') ? name + 'index.html' : name)));
    if (!path.startsWith(root + sep)) { response.writeHead(403); response.end(); return; }
    response.writeHead(200, {'content-type':mime[extname(path)] || 'application/octet-stream', 'content-security-policy':"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'"});
    response.end(await readFile(path));
  } catch { response.writeHead(404); response.end(); }
});
await new Promise((done) => server.listen(0, '127.0.0.1', done));
const url = `http://127.0.0.1:${server.address().port}/docs/design-engine/station-pair/`;
let browser;
const errors = [];
const capture = process.env.OSR_STATION_PAIR_CAPTURE;
const receipt = {study_id:summary.study_id, url, assertions:[], candidate_inputs_modified:false, physical_acceptance_conferred:false, isolation:'Read-only static file server; source/candidate verification belongs to the campaign verifier, not this presentation test.'};
function record(name) { receipt.assertions.push(name); }
try {
  browser = await launchBrowser();
  receipt.browser = browser.osrRendering;
  const page = await browser.newPage({viewport:{width:1500,height:1050}});
  page.on('pageerror', (error) => errors.push(String(error)));
  page.on('console', (message) => { if (message.type() === 'error') errors.push(message.text()); });
  await page.goto(url);
  await page.locator('#study-content:not([hidden])').waitFor();
  assert.equal(await page.locator('#comparison-body tr').count(), summary.rows.length);
  assert.equal(await page.locator('.family-card').count(), 4);
  assert.equal(await page.locator('#study-id').innerText(), summary.study_id);
  record('Initial row count, all four families, exact exported study identity');
  await page.selectOption('#speed-filter', '60');
  assert.equal(await page.locator('#comparison-body tr').count(),summary.rows.filter((r)=>Math.abs(r.speed_cap_km_h-60)<1e-8).length);
  await page.selectOption('#distance-filter', '1500');
  assert.equal(await page.locator('#comparison-body tr').count(),summary.rows.filter((r)=>r.distance_m===1500 && Math.abs(r.speed_cap_km_h-60)<1e-8).length);
  record('60 km/h filter retains converted floating-point speed values at both spacings');
  await page.selectOption('#speed-filter', '40');
  const expected = summary.rows.filter((r) => r.distance_m === 1500 && r.speed_cap_km_h === 40);
  assert.equal(await page.locator('#comparison-body tr').count(), expected.length);
  record('1.5 km / 40 km/h filter count matches source rows');
  for (const family of ['cable','compact-LIM','hybrid','powered-wheel']) {
    await page.selectOption('#family-filter', family);
    const rows = expected.filter((r) => r.family === family);
    assert.equal(await page.locator('#comparison-body tr').count(), Math.max(1, rows.length));
    if (family === 'compact-LIM' || family === 'hybrid') {
      assert(rows.every((r) => !r.numerical_arrival));
      const text = await page.locator('#comparison-body').innerText();
      assert(text.includes('Not evaluated'));
      assert(text.includes('Unknown') || text.includes('additions unknown'));
      assert(!text.includes('0.000 MW'));
    }
  }
  record('Family filters retain LIM/hybrid holds and missing quantities are not rendered as zero');
  await page.getByRole('button', {name:'Reset filters'}).click();
  await page.waitForFunction((n) => document.querySelectorAll('#comparison-body tr').length === n, summary.rows.length);
  await page.locator('.inspect-button').first().click();
  assert(await page.locator('#candidate-details').getAttribute('open') !== null);
  assert((await page.locator('#candidate-detail-content').innerText()).includes(summary.rows[0].candidate_id));
  record('Candidate inspection retains full physical and evaluation identities');
  if (summary.finalists.length) {
    assert.equal(await page.locator('#trace-a option').count(), summary.finalists.length);
    if (summary.finalists.length > 1) await page.selectOption('#trace-b', '1');
    for (const metric of ['speed','acceleration','force']) {
      await page.selectOption('#trace-metric', metric);
      assert.equal(await page.locator('#trace-chart svg').count(), 1);
      const paths = await page.locator('#trace-chart path').evaluateAll((nodes) => nodes.map((n) => n.getAttribute('d')));
      assert(paths.length >= 2);
      assert(paths.every((d) => d && !/NaN|Infinity|undefined/.test(d)));
    }
    record('Two source-linked traces render all three metrics with finite coordinates');
    for (let i=0;i<summary.finalists.length;i++) {
      await page.selectOption('#checks-finalist', String(i));
      const f = summary.finalists[i], checks=f.checks || [], distance=f.request?.distance_m;
      assert.equal(await page.locator('#checks-body tr').count(), Math.max(1,checks.length));
      if (checks.some((c) => c.final_position_m > distance + summary.brief.berth_tolerance_m)) assert((await page.locator('#checks-body').innerText()).includes('Overran station-pair boundary'));
    }
    record('Fixed-controller check counts and actual route overruns remain visible');
  }
  const links = await page.locator('#download-links a').evaluateAll((nodes) => nodes.map((n) => n.getAttribute('href')));
  assert.equal(links.length,new Set(links).size);
  assert(links.includes('delivery-draft.json.gz'));
  for (const path of links) {
    assert(!/^(?:https?:|\/|\.\.)/.test(path));
    const response = await page.request.get(new URL(path,url).href); assert.equal(response.status(),200);
  }
  record('Relative evidence and combined manufacturing/business draft downloads resolve');
  assert((await page.locator('main').innerText()).includes('not a 30 km city estimate'));
  assert((await page.locator('main').innerText()).includes('Terminal jerk is unresolved'));
  await page.selectOption('#trace-metric','speed');
  for (const [name,width,height] of [['desktop',1500,1050],['mobile',390,844]]) {
    await page.setViewportSize({width,height});
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
    if (overflow) receipt.overflow_elements = await page.evaluate(() => [...document.querySelectorAll('body *')].filter((n) => {
      const b=n.getBoundingClientRect(); return b.width>0 && (b.left < -1 || b.right > window.innerWidth+1) && !n.closest('.table-scroll');
    }).map((n)=>({tag:n.tagName,id:n.id,classes:n.className,width:n.getBoundingClientRect().width,right:n.getBoundingClientRect().right})).slice(0,30));
    assert.equal(overflow,false,`${name} viewport overflows`);
    if(capture) { await mkdir(capture,{recursive:true}); await page.screenshot({path:resolve(capture,`${name}.png`),fullPage:true}); }
  }
  record('Desktop/mobile layout has no page overflow; pilot scope and terminal jerk limitations visible');
  assert.deepEqual(errors,[]);
  receipt.state='passed'; receipt.console_errors=errors;
  console.log(JSON.stringify(receipt,null,2));
} catch(error) {
  receipt.state='failed';receipt.reason=String(error);receipt.console_errors=errors;throw error;
} finally {
  if(capture) { await mkdir(capture,{recursive:true});await writeFile(resolve(capture,'browser-result.json'),JSON.stringify(receipt,null,2)+'\n'); }
  await browser?.close(); await new Promise((done) => server.close(done));
}
