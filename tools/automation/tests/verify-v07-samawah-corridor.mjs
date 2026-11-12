// Real Workbench station-edit comparison, using existing bounded city workers.
import assert from 'node:assert/strict';
import {execFileSync, spawn} from 'node:child_process';
import {mkdir, readdir, writeFile} from 'node:fs/promises';
import {resolve, join} from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';
import {launchBrowser} from './browser-launch.mjs';

const root = resolve(process.env.OSR_ROOT || fileURLToPath(new URL('../../../', import.meta.url)));
const output = resolve(process.argv[2] || join(tmpdir(), 'osr-v07-samawah-corridor'));
assert(output !== root && !output.startsWith(root + '/'), 'Use external evidence output');
await mkdir(output, {recursive: true});
assert.equal((await readdir(output)).length, 0, 'Preserve previous runs; use a fresh output directory');
const git = (...args) => execFileSync('git', args, {cwd: root, encoding: 'utf8'}).trim();
assert.equal(git('status', '--porcelain', '--untracked-files=all'), '', 'Clean source required');
const started = performance.now();
const source = git('rev-parse', 'HEAD');
const python = process.env.OSR_PYTHON || join(root, '.venv/bin/python');
const studyStore = resolve(process.env.OSR_CITY_STUDY_STORE || join(output, 'city-studies'));
const server = spawn(python, ['-B', '-u', '-m', 'engineering.development_baseline.server',
  '--root', root, '--host', '127.0.0.1', '--port', '0', '--no-browser',
  '--city-study-store', studyStore, '--trip-store', join(output, 'trip-studies')],
  {cwd: root, env: {...process.env, PYTHONPATH: root, PYTHONDONTWRITEBYTECODE: '1',
    OPENBLAS_NUM_THREADS: '1', OMP_NUM_THREADS: '1', MKL_NUM_THREADS: '1'}, stdio: ['ignore', 'pipe', 'pipe']});
let log = '', origin, browser, page;
const errors = [], external = [];
server.stdout.on('data', b => {log += b; origin ||= log.match(/http:\/\/127\.0\.0\.1:\d+/)?.[0];});
server.stderr.on('data', b => {log += b;});
try {
  const deadline = performance.now() + 30000;
  while (!origin && performance.now() < deadline) {
    assert(server.exitCode === null, log);
    await new Promise(r => setTimeout(r, 100));
  }
  assert(origin, 'Server startup failed: ' + log);
  browser = await launchBrowser();
  const context = await browser.newContext({viewport: {width: 1440, height: 1100}});
  await context.route('**/*', async route => {
    if (new URL(route.request().url()).origin !== origin) {external.push(route.request().url()); await route.abort();}
    else await route.continue();
  });
  page = await context.newPage(); page.on('pageerror', error => errors.push(error.message));
  await page.goto(origin + '/', {waitUntil: 'domcontentloaded'});
  await page.locator('#city-outline-load').click();
  await page.locator('#city-outline-select option[value="samawah"]').waitFor({state: 'attached'});
  await page.locator('#city-outline-select').selectOption('samawah');
  await page.locator('#samawah-merge-compare').waitFor({state: 'visible', timeout: 30000});
  const coldStart = performance.now();
  await page.locator('#samawah-merge-compare').click();
  await page.waitForFunction(() => /Comparison complete|Unable to compare/.test(document.querySelector('#samawah-merge-status')?.textContent || ''), null, {timeout: 300000});
  assert.match(await page.locator('#samawah-merge-status').innerText(), /^Comparison complete/);
  const coldSeconds = (performance.now() - coldStart) / 1000;
  const before = await page.locator('#samawah-station-merge').getAttribute('data-baseline-job');
  const after = await page.locator('#samawah-station-merge').getAttribute('data-revised-job');
  const url = `${origin}/api/city-studies/comparisons/${before}/${after}`;
  const response = await context.request.get(url); assert(response.ok());
  const envelope = await response.json(), report = envelope.report;
  const metrics = Object.fromEntries(report.metrics.map(row => [row.key, row]));
  assert.deepEqual([metrics.raw_marker_count.before, metrics.raw_marker_count.after], [26, 25]);
  assert.deepEqual([metrics.operational_stop_count.before, metrics.operational_stop_count.after], [25, 25]);
  assert.equal(metrics.route_m.delta, 0);
  assert.equal(Object.keys(report.cost_scopes).length, 14);
  assert.equal(report.reference_candidate_ids.body_candidate_id, '9489e4f2666fd3b3c73232c86df3f12adf42a5531eb27373834cf3fecb1a3117');
  assert.equal(report.reuse.vehicle_definition_unchanged, true);
  assert.equal(report.performance.before.native_solver_jobs, 0);
  assert.equal(report.performance.after.native_solver_jobs, 0);
  assert.equal(report.physical_accepted, false);
  assert.equal(await page.locator('.samawah-merge-costs tbody tr').count(), 14);
  // Preserve original Python number spellings: JSON.stringify changes 20.0 to 20.
  await writeFile(join(output, 'comparison.json'), await response.body());
  execFileSync(python, ['-B', '-c',
    'import json,sys; from engineering.v07_project import from_comparison; from_comparison(json.load(open(sys.argv[1]))["report"])',
    join(output, 'comparison.json')], {cwd: root, env: {...process.env, PYTHONPATH: root}});
  const projectResponse = await context.request.get(`${origin}/api/city-studies/projects/${before}/${after}`);
  assert(projectResponse.ok()); const project = await projectResponse.json();
  assert.equal(project.cases.after.composition_complete, false);
  assert(project.cases.after.missing_stages.includes('vehicle'));
  const doorResponse = await context.request.get(`${origin}/api/v07/door-module`);
  assert(doorResponse.ok()); const door = await doorResponse.json();
  assert.equal(door.parent_candidate_id, report.reference_candidate_ids.candidate_id);
  assert.notEqual(door.candidate_id, door.parent_candidate_id);
  assert.equal(door.opening_count_per_train, 12);
  assert.equal(door.installed_mass_kg_per_opening, null);
  assert.equal(door.fleet, null); assert.equal(door.manufacturing_release, false);
  await writeFile(join(output, 'door-module.json'), await doorResponse.body());
  await page.locator('#samawah-door-open').click();
  await page.waitForFunction(id => document.querySelector('#samawah-door-module')?.dataset.moduleId === id, door.module_id);
  assert.equal(await page.locator('#samawah-door-part option').count(), door.parts.length);
  assert.match(await page.locator('.atlas-door-part').innerText(), /Removal and maintenance/);
  assert.match(await page.locator('#samawah-door-module').innerText(), /Installed mass and centre of gravity remain unknown/);
  const electrical = door.parts.find(part => part.assembly_id === 'services/door-electrical');
  await page.locator('#samawah-door-part').selectOption(electrical.id);
  assert.match(await page.locator('.atlas-door-part').innerText(), /approved limit and observed result required/);

  await page.locator('#samawah-station-merge').screenshot({path: join(output, 'comparison-desktop.png')});
  const warmStart = performance.now();
  await page.locator('#samawah-merge-compare').click();
  await page.waitForFunction(() => document.querySelector('#samawah-station-merge')?.dataset.cacheReused === 'true' && document.querySelector('#samawah-merge-status')?.textContent.startsWith('Comparison complete'), null, {timeout: 60000});
  const warmSeconds = (performance.now() - warmStart) / 1000;
  assert.equal(await page.locator('#samawah-station-merge').getAttribute('data-baseline-job'), before);
  assert.equal(await page.locator('#samawah-station-merge').getAttribute('data-revised-job'), after);
  const warm = await (await context.request.get(url)).json();
  assert.equal(warm.cache_hit, true); assert.equal(warm.report.comparison_id, report.comparison_id);
  await page.setViewportSize({width: 390, height: 844});
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 2), 'Mobile page overflow');
  await page.locator('#samawah-station-merge').screenshot({path: join(output, 'comparison-mobile.png')});
  assert.deepEqual(errors, []); assert.deepEqual(external, []);
  assert.equal(git('status', '--porcelain', '--untracked-files=all'), '');
  await writeFile(join(output, 'journey.json'), JSON.stringify({schema: 'osr-v07-samawah-corridor-browser/1',
    source_commit: source, source_tree: git('rev-parse', 'HEAD^{tree}'), comparison_id: report.comparison_id,
    before_job_id: before, after_job_id: after, first_browser_seconds: coldSeconds, warm_browser_seconds: warmSeconds,
    study_store: studyStore, reused_prior_store: Boolean(process.env.OSR_CITY_STUDY_STORE),
    same_verified_jobs_reused: true, total_wall_seconds: (performance.now() - started) / 1000,
    metrics: report.metrics, native_solver_jobs: 0, browser: browser.osrRendering,
    page_errors: errors, external_requests: external, result: 'pass-for-first-Samawah-corridor-milestone'}, null, 2) + '\n');
  console.log(JSON.stringify({output, coldSeconds, warmSeconds, metrics: report.metrics}));
} catch (error) {
  await writeFile(join(output, 'failure.json'), JSON.stringify({source_commit: source, error: String(error.stack || error), page_errors: errors, external_requests: external, server_log: log}, null, 2) + '\n');
  throw error;
} finally {
  if (browser) await browser.close();
  if (server.exitCode === null) {
    server.kill('SIGINT');
    await new Promise(resolve => {const timer = setTimeout(() => {server.kill('SIGKILL'); resolve();}, 5000); server.once('exit', () => {clearTimeout(timer); resolve();});});
  }
  await writeFile(join(output, 'server.log'), log);
}
