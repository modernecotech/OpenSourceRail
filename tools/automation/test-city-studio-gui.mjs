#!/usr/bin/env node

import { spawn } from "node:child_process";
import { createServer } from "node:net";
import { mkdir, cp, readFile, writeFile, rm } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { chromium } from "@playwright/test";

const root = path.resolve(import.meta.dirname, "..", "..");
const sourceProject = path.join(root, "cities/workspaces", "samawah");
const runToken = `${process.pid}-${Date.now().toString(36)}`;
const slug = `samawah-e2e-${runToken}`;
const fixture = path.join(root, "cities/workspaces", `.city-studio-e2e-${runToken}`);
const reportDir = path.join(root, "build", "gui-acceptance");
const reportPath = path.join(reportDir, "city-studio-gui-report.json");
const screenshotArg = process.argv.indexOf("--screenshot");
const screenshotPath = screenshotArg >= 0 && process.argv[screenshotArg + 1]
  ? path.resolve(root, process.argv[screenshotArg + 1])
  : path.join(reportDir, "city-studio-gui.png");
const executable = path.join(root, "target", "debug", "osr-city-studio");

const checks = [];
const startedAt = new Date();
let cityProcess;
let browser;
let cdp;

function record(name, detail = "") {
  checks.push({ name, detail, passed: true, at: new Date().toISOString() });
  process.stdout.write(`PASS  ${name}${detail ? ` — ${detail}` : ""}\n`);
}

function assert(value, name, detail = "") {
  if (!value) throw new Error(`${name}${detail ? `: ${detail}` : ""}`);
  record(name, detail);
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function freePort() {
  return await new Promise((resolve, reject) => {
    const server = createServer();
    server.on("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      server.close(() => resolve(address.port));
    });
  });
}

async function waitForHttp(url, timeoutMs = 30_000) {
  const deadline = Date.now() + timeoutMs;
  let lastError;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(url);
      if (response.ok) return;
      lastError = new Error(`HTTP ${response.status}`);
    } catch (error) {
      lastError = error;
    }
    await delay(100);
  }
  throw new Error(`Timed out waiting for ${url}: ${lastError?.message || "unknown error"}`);
}

function terminate(child) {
  if (!child || child.exitCode !== null) return;
  child.kill("SIGTERM");
}

async function startCityStudio(port) {
  const child = spawn(executable, ["--project", fixture, "serve", "--host", "127.0.0.1", "--port", String(port)], {
    cwd: root,
    stdio: ["ignore", "pipe", "pipe"],
  });
  let diagnostics = "";
  child.stdout.on("data", (chunk) => { diagnostics += chunk; });
  child.stderr.on("data", (chunk) => { diagnostics += chunk; });
  child.on("exit", (code) => {
    if (code && cityProcess === child) process.stderr.write(diagnostics);
  });
  await waitForHttp(`http://127.0.0.1:${port}/api/project`);
  return child;
}

class PlaywrightDriver {
  constructor(page) {
    this.page = page;
  }

  async evaluate(expression) {
    return await this.page.evaluate((source) => (0, eval)(source), expression);
  }

  async wait(expression, label, timeoutMs = 60_000) {
    const deadline = Date.now() + timeoutMs;
    let lastError;
    while (Date.now() < deadline) {
      try {
        if (await this.evaluate(expression)) return;
      } catch (error) {
        lastError = error;
      }
      await delay(150);
    }
    throw new Error(`Timed out waiting for ${label}${lastError ? `: ${lastError.message}` : ""}`);
  }
}

async function startBrowser(cityUrl) {
  const launched = await chromium.launch({
    headless: true,
    channel: process.env.PLAYWRIGHT_CHANNEL || undefined,
  });
  const context = await launched.newContext({
    viewport: { width: 1600, height: 1200 },
    locale: "en-GB",
    timezoneId: "Europe/London",
    reducedMotion: "reduce",
  });
  const page = await context.newPage();
  await page.goto(cityUrl, { waitUntil: "domcontentloaded" });
  const tools = new PlaywrightDriver(page);
  await tools.wait("typeof view === 'object' && view?.snapshot?.stations?.length > 0", "initial project render");
  return { browser: launched, tools, page };
}

async function form(selector, values) {
  const payload = JSON.stringify(values);
  await cdp.evaluate(`(() => {
    const target = document.querySelector(${JSON.stringify(selector)});
    const values = ${payload};
    for (const [key, value] of Object.entries(values)) {
      const input = target.querySelector('#' + CSS.escape(key)) || target.elements.namedItem(key);
      if (!input) throw new Error('Missing form field ' + key);
      input.value = String(value);
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.dispatchEvent(new Event('change', { bubbles: true }));
    }
    target.requestSubmit();
    return true;
  })()`);
}

async function click(selector) {
  await cdp.evaluate(`(() => {
    const node = document.querySelector(${JSON.stringify(selector)});
    if (!node) throw new Error('Missing clickable element: ' + ${JSON.stringify(selector)});
    if (typeof node.click === 'function') node.click();
    else node.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    return true;
  })()`);
}

async function createOnLine(mode) {
  const beforeExpression = mode === "station"
    ? "view.snapshot.summary.manual_station_count"
    : "view.snapshot.line_control_points.length";
  const before = await cdp.evaluate(beforeExpression);
  await click(`[data-mode="${mode}"]`);
  const clickGeometry = await cdp.evaluate(`(() => {
    const line = document.querySelector('.network-line');
    const box = line.getBoundingClientRect();
    const point = line.getPointAtLength(line.getTotalLength() * .42);
    const screen = new DOMPoint(point.x, point.y).matrixTransform(line.getScreenCTM());
    line.dispatchEvent(new MouseEvent('click', {
      bubbles: true,
      clientX: screen.x,
      clientY: screen.y,
    }));
    return { line: line.dataset.line, left: box.left, top: box.top, width: box.width, height: box.height };
  })()`);
  try {
    await cdp.wait(`${beforeExpression} > ${before}`, `${mode} creation`, 60_000);
    await cdp.wait(
      mode === "station" ? "selectedStation?.state === 'manual'" : "selectedControl?.id && selectedControl?.line",
      `${mode} selection after persistence`,
      60_000,
    );
  } catch (error) {
    const message = await cdp.evaluate("document.querySelector('#toast').textContent");
    throw new Error(`${mode} creation failed at ${JSON.stringify(clickGeometry)}: ${message || 'no UI error'}`);
  }
}

async function createLine(routing, firstIndex, secondIndex) {
  const before = await cdp.evaluate("view.snapshot.summary.manual_line_count");
  const previousSelection = await cdp.evaluate("selectedLine?.id || null");
  await cdp.evaluate(`document.querySelector('#line-routing').value = ${JSON.stringify(routing)}`);
  await click('[data-mode="line"]');
  await cdp.evaluate(`(() => {
    const stations = view.snapshot.stations.filter(item => item.state !== 'retired');
    const chosen = [stations[${firstIndex} % stations.length], stations[${secondIndex} % stations.length]];
    const map = document.querySelector('#network-map');
    const rect = map.getBoundingClientRect();
    for (const station of chosen) {
      const [x, y] = projection.point(station.lon, station.lat);
      map.dispatchEvent(new MouseEvent('click', {
        bubbles: true,
        clientX: rect.left + x / 1000 * rect.width,
        clientY: rect.top + y / 620 * rect.height,
      }));
    }
    return true;
  })()`);
  await cdp.wait(`view.snapshot.summary.manual_line_count > ${before}`, `${routing} line creation`, 90_000);
  await cdp.wait(`selectedLine?.state === 'manual' && selectedLine?.id !== ${JSON.stringify(previousSelection)}`, `${routing} line inspector`, 60_000);
  return await cdp.evaluate("selectedLine.id");
}

async function runAdapter(adapter, timeoutMs = 180_000) {
  const before = await cdp.evaluate("jobView.jobs.length");
  await click(`[data-job-adapter="${adapter}"]`);
  try {
    await cdp.wait(`jobView.jobs.length > ${before}`, `${adapter} job queued`);
  } catch (error) {
    const debug = await cdp.evaluate(`({
      toast: document.querySelector('#toast').textContent,
      jobs: jobView.jobs.map(item => ({ id: item.id, status: item.status, error: item.error })),
      adapterButton: !!document.querySelector('[data-job-adapter="${adapter}"]'),
    })`);
    throw new Error(`${adapter} did not queue: ${JSON.stringify(debug)}`);
  }
  const id = await cdp.evaluate("jobView.jobs[0].id");
  await cdp.wait(`["succeeded", "failed"].includes(jobView.jobs.find(item => item.id === ${JSON.stringify(id)})?.status)`, `${adapter} job completion`, timeoutMs);
  const completed = await cdp.evaluate(`jobView.jobs.find(item => item.id === ${JSON.stringify(id)})`);
  if (completed.status !== "succeeded") {
    throw new Error(`${adapter} job failed: ${completed.error || completed.log_tail || completed.phase}`);
  }
  const count = await cdp.evaluate(`jobView.jobs.find(item => item.id === ${JSON.stringify(id)}).artifacts.length`);
  assert(count > 0, `${adapter} produced artifacts`, `${count} artifact(s)`);
  return id;
}

async function openArtifact(jobId, kind) {
  const index = await cdp.evaluate(`jobView.jobs.find(item => item.id === ${JSON.stringify(jobId)}).artifacts.findIndex(item => item.kind === ${JSON.stringify(kind)})`);
  assert(index >= 0, `${kind} listed in the GUI`);
  await click(`[data-job-id="${jobId}"][data-artifact-index="${index}"]`);
  await cdp.wait(`selectedArtifactPreview?.job_id === ${JSON.stringify(jobId)} && selectedArtifactPreview?.artifact_index === ${index}`, `${kind} preview`);
  const verified = await cdp.evaluate("selectedArtifactPreview.sha256_verified && document.querySelector('#artifact-verification').textContent.includes('verified')");
  assert(verified, `${kind} SHA-256 verification`);
}

async function main() {
  await mkdir(reportDir, { recursive: true });
  await cp(sourceProject, fixture, { recursive: true });
  const projectFile = path.join(fixture, "project.osr.toml");
  const project = (await readFile(projectFile, "utf8"))
    .replace(/^id = "osr-city-iq-samawah"$/m, `id = "osr-city-iq-${slug}"`)
    .replace(/^slug = "samawah"$/m, `slug = "${slug}"`)
    .replace(/^tag_prefix = "city\/samawah\/design\/"$/m, `tag_prefix = "city/${slug}/design/"`);
  await writeFile(projectFile, project);

  const cityPort = await freePort();
  cityProcess = await startCityStudio(cityPort);
  const launched = await startBrowser(`http://127.0.0.1:${cityPort}/`);
  browser = launched.browser;
  cdp = launched.tools;

  const baseline = await cdp.evaluate(`({
    stations: view.snapshot.summary.station_count,
    lines: view.snapshot.lines.length,
    services: view.service_plan.line_plans.length,
    demandPeriods: view.snapshot.demand?.periods?.length || 0,
    findings: view.snapshot.findings.filter(item => item.severity === 'error').length,
  })`);
  assert(baseline.stations >= 20 && baseline.lines >= 3, "initial network rendered", `${baseline.stations} stations, ${baseline.lines} lines`);
  assert(baseline.services >= baseline.lines * 3, "line/day service plans rendered", `${baseline.services} plans`);
  assert(baseline.demandPeriods >= 4, "source-controlled demand periods rendered", `${baseline.demandPeriods} periods`);
  assert(baseline.findings === 0, "baseline validation has no errors");
  await cdp.wait("gisManifest?.layers?.length > 0 && gisLayers.get('routing-demand')?.features?.length > 0", "deterministic GIS workspace");
  const gisState = await cdp.evaluate(`({
    deterministic: gisManifest?.deterministic,
    crs: gisManifest?.coordinate_reference_system,
    layers: gisManifest?.layers?.length,
    hashesValid: gisManifest?.layers?.every(layer => /^[a-f0-9]{64}$/.test(layer.sha256)),
    demandFeatures: gisLayers.get('routing-demand')?.features?.length,
    renderedDemand: document.querySelectorAll('[data-gis-group="routing-demand"] .gis-feature').length,
    roads: document.querySelectorAll('[data-gis-group="context-roads"] .gis-feature').length,
    buildings: document.querySelectorAll('[data-gis-group="context-buildings"] .gis-feature').length,
    water: document.querySelectorAll('[data-gis-group="context-water"] .gis-feature').length,
    existingRail: document.querySelectorAll('[data-gis-group="context-existing-rail"] .gis-feature').length,
    attribution: document.querySelector('#map-attribution').textContent,
    controls: document.querySelectorAll('[data-layer-control]').length,
  })`);
  assert(gisState.deterministic && gisState.crs === "EPSG:4326", "deterministic GIS manifest loaded", gisState.crs);
  assert(gisState.attribution.includes("OpenStreetMap") && gisState.attribution.includes("ODbL"), "OpenStreetMap attribution remains visible on the map");
  assert(gisState.layers === 16 && gisState.hashesValid, "GIS layer catalogue is content hashed", `${gisState.layers} layers`);
  assert(gisState.demandFeatures > 0 && gisState.renderedDemand === gisState.demandFeatures, "locked demand surface rendered behind candidate", `${gisState.demandFeatures} cells`);
  assert(gisState.roads > 1000 && gisState.buildings > 0 && gisState.water > 0 && gisState.existingRail > 0, "locked roads, buildings, water and existing rail render as local context", `${gisState.roads} road features`);
  assert(gisState.controls === gisState.layers, "every GIS layer has visibility and opacity controls");
  await cdp.evaluate(`(() => {
    const control = document.querySelector('[data-layer-control="routing-cost"]');
    const checkbox = control.querySelector('input[type="checkbox"]');
    checkbox.checked = true;
    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
    const opacity = control.querySelector('input[type="range"]');
    opacity.value = '0.55';
    opacity.dispatchEvent(new Event('input', { bubbles: true }));
    return true;
  })()`);
  const costLayer = await cdp.evaluate(`({
    features: document.querySelectorAll('[data-gis-group="routing-cost"] .gis-feature').length,
    opacity: document.querySelector('[data-gis-group="routing-cost"]')?.getAttribute('opacity'),
  })`);
  assert(costLayer.features > 0, "construction-cost planning surface can be enabled", `${costLayer.features} cells`);
  assert(costLayer.opacity === "0.55", "GIS layer opacity updates interactively");
  await click('[data-gis-group="context-anchors"] .gis-feature');
  const inspected = await cdp.evaluate("!document.querySelector('#gis-inspector').hidden && document.querySelector('#gis-inspector').textContent.length > 10");
  assert(inspected, "GIS feature properties are inspectable");
  const beforeZoom = await cdp.evaluate("document.querySelector('#network-map').getAttribute('viewBox')");
  await click("#map-zoom-in");
  const afterZoom = await cdp.evaluate("document.querySelector('#network-map').getAttribute('viewBox')");
  assert(beforeZoom !== afterZoom && afterZoom.includes("720"), "GIS map zoom control updates the deterministic viewport", afterZoom);
  await click('[data-mode="pan"]');
  const mapBox = await cdp.page.locator("#network-map").boundingBox();
  const beforePan = await cdp.evaluate("document.querySelector('#network-map').getAttribute('viewBox')");
  await cdp.page.mouse.move(mapBox.x + mapBox.width * 0.45, mapBox.y + mapBox.height * 0.5);
  await cdp.page.mouse.down();
  await cdp.page.mouse.move(mapBox.x + mapBox.width * 0.55, mapBox.y + mapBox.height * 0.58, { steps: 4 });
  await cdp.page.mouse.up();
  const afterPan = await cdp.evaluate("document.querySelector('#network-map').getAttribute('viewBox')");
  assert(beforePan !== afterPan, "GIS pan tool moves the viewport", afterPan);
  await click("#map-fit");
  await click('[data-mode="select"]');
  const georeferencedLine = await cdp.evaluate("view.snapshot.lines[0].id");

  await cdp.evaluate(`(() => {
    document.querySelector('#civil-unit-spans').value = '5';
    document.querySelector('#civil-mould-cycle').value = '48';
    document.querySelector('#civil-compare-roads').checked = false;
    document.querySelector('#civil-georef-line').value = ${JSON.stringify(georeferencedLine)};
    document.querySelector('#civil-georef-line').dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#civil-georef-enabled').checked = true;
    document.querySelector('#civil-georef-enabled').dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#civil-georef-crs').value = 'EPSG:32638';
    document.querySelector('#civil-georef-source').value = 'GUI acceptance fixture survey control S-04';
    document.querySelector('#civil-georef-eastings').value = '412345.6';
    document.querySelector('#civil-georef-northings').value = '3467890.1';
    document.querySelector('#civil-georef-height').value = '18.25';
    document.querySelector('#civil-georef-abscissa').value = '0.999847695';
    document.querySelector('#civil-georef-ordinate').value = '-0.017452406';
    document.querySelector('#civil-georef-scale').value = '0.99995';
    document.querySelector('#civil-settings-form').requestSubmit();
    return true;
  })()`);
  await cdp.wait("view.snapshot.civil.expansion_unit_spans === 5 && view.snapshot.civil.mould_cycle_target_h === 48 && view.snapshot.civil.compare_road_grade_separation === false", "civil construction settings save");
  await cdp.wait(`view.snapshot.civil.ifc_georeferencing?.find(item => item.line === ${JSON.stringify(georeferencedLine)})?.crs_name === 'EPSG:32638'`, "per-line IFC survey control save");
  await cdp.wait("document.querySelector('#civil-derived').textContent.includes('125 m thermal unit')", "civil construction derived quantities");
  record("civil construction and per-line IFC survey control saved", "5-span unit · EPSG:32638 test transform");

  const movedStation = await cdp.evaluate("view.snapshot.stations.find(item => item.state === 'generated').id");
  await click(`circle.station[data-id="${movedStation}"]`);
  const movedCoordinates = await cdp.evaluate("({ lat: selectedStation.lat + .00012, lon: selectedStation.lon + .00012 })");
  await form("#station-form", {
    "station-lat": movedCoordinates.lat.toFixed(7),
    "station-lon": movedCoordinates.lon.toFixed(7),
    "station-state": "preferred",
    "station-reason": "GUI acceptance movement for persistent regeneration",
  });
  try {
    await cdp.wait(`view.snapshot.stations.find(item => item.id === ${JSON.stringify(movedStation)})?.state === 'preferred'`, "station edit persistence in model", 60_000);
  } catch (error) {
    const stationSaveDebug = await cdp.evaluate(`({
      toast: document.querySelector('#toast').textContent,
      state: view.snapshot.stations.find(item => item.id === ${JSON.stringify(movedStation)})?.state,
      selected: selectedStation?.id,
    })`);
    throw new Error(`Station form save failed: ${JSON.stringify(stationSaveDebug)}`);
  }
  record("generated station moved and promoted");

  await createOnLine("station");
  const manualStation = await cdp.evaluate("selectedStation.id");
  await form("#station-form", {
    "station-name": "GUI Acceptance Station",
    "station-archetype": "major",
    "station-reason": "Interactive candidate station created by browser acceptance",
  });
  try {
    await cdp.wait(`view.snapshot.stations.find(item => item.id === ${JSON.stringify(manualStation)})?.name === 'GUI Acceptance Station'`, "manual station edit", 60_000);
  } catch (error) {
    const manualStationDebug = await cdp.evaluate(`({
      station: view.snapshot.stations.find(item => item.id === ${JSON.stringify(manualStation)}),
      toast: document.querySelector('#toast').textContent,
      valid: document.querySelector('#station-form').checkValidity(),
      invalid: [...document.querySelector('#station-form').elements].filter(item => !item.checkValidity()).map(item => ({ id: item.id, value: item.value, message: item.validationMessage })),
    })`);
    throw new Error(`Manual station form save failed: ${JSON.stringify(manualStationDebug)}`);
  }
  record("manual station created and edited", manualStation);

  await createOnLine("control");
  const controlId = await cdp.evaluate("selectedControl.id");
  await form("#control-form", {
    "control-influence": 2400,
    "control-reason": "GUI acceptance alignment influence",
  });
  await cdp.wait(`view.snapshot.line_control_points.find(item => item.id === ${JSON.stringify(controlId)})?.influence_m === 2400`, "alignment control edit");
  record("alignment control point created and edited", controlId);

  const directLine = await createLine("direct", 1, 10);
  await form("#line-form", {
    "line-name": "GUI Direct Line",
    "line-reason": "Direct fallback line created through map tools",
  });
  await cdp.wait(`view.snapshot.lines.find(item => item.id === ${JSON.stringify(directLine)})?.name === 'GUI Direct Line'`, "direct line edit");
  record("direct line created with terminals and weekly plans", directLine);

  const demandLine = await createLine("demand-aware", 2, 16);
  await form("#line-form", {
    "line-name": "GUI Demand Line",
    "line-reason": "Demand/buildability routed line created through map tools",
  });
  try {
    await cdp.wait(`(() => { const line = view.snapshot.lines.find(item => item.id === ${JSON.stringify(demandLine)}); return line?.routing_method === 'demand-aware' && line?.name === 'GUI Demand Line'; })()`, "demand-aware line edit", 60_000);
  } catch (error) {
    const demandState = await cdp.evaluate(`({
      line: view.snapshot.lines.find(item => item.id === ${JSON.stringify(demandLine)}),
      toast: document.querySelector('#toast').textContent,
    })`);
    throw new Error(`Demand-aware line state failed: ${JSON.stringify(demandState)}`);
  }
  record("demand-aware line created with locked routing sources", demandLine);

  await cdp.evaluate(`(() => {
    const line = document.querySelector('#service-line');
    line.value = ${JSON.stringify(directLine)};
    line.dispatchEvent(new Event('change', { bubbles: true }));
    const day = document.querySelector('#service-day');
    day.value = 'weekday';
    day.dispatchEvent(new Event('change', { bubbles: true }));
    const headway = document.querySelector('.window-headway');
    headway.value = 15;
    document.querySelector('#toast').textContent = '';
    document.querySelector('#service-form').requestSubmit();
    return true;
  })()`);
  await cdp.wait(`view.service_plan.line_plans.find(item => item.line === ${JSON.stringify(directLine)} && item.day_type === 'weekday').windows[0].headway_min === 15`, "manual route service plan edit");
  await cdp.wait("document.querySelector('#toast').textContent.includes('Service plan saved')", "manual route service editor refresh");
  record("new manual route service plan edited and persisted", `${directLine}: 15 min`);

  let serviceState = await cdp.evaluate(`(() => {
    document.querySelector('#toast').textContent = '';
    const select = document.querySelector('#service-line');
    select.value = view.snapshot.lines.find(item => item.state !== 'manual').id;
    select.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#service-day').value = 'weekday';
    document.querySelector('#service-day').dispatchEvent(new Event('change', { bubbles: true }));
    const headway = document.querySelector('.window-headway');
    headway.value = Number(headway.value) === 13 ? 14 : 13;
    const desired = Number(headway.value);
    headway.dispatchEvent(new Event('input', { bubbles: true }));
    document.querySelector('#service-form').requestSubmit();
    return { line: select.value, headway: desired };
  })()`);
  await cdp.wait(`view.service_plan.line_plans.find(item => item.line === ${JSON.stringify(serviceState.line)} && item.day_type === 'weekday').windows[0].headway_min === ${serviceState.headway}`, "service headway save");
  await cdp.wait("document.querySelector('#toast').textContent.includes('Service plan saved')", "service editor refresh");
  record("weekday service variables and regenerated fleet metrics saved", `${serviceState.line}: ${serviceState.headway} min`);

  const bulkHeadway = Math.max(1, Math.min(120, Math.round(serviceState.headway * 1.1)));
  await cdp.evaluate("document.querySelector('#toast').textContent = ''; document.querySelector('#headway-factor').value = '1.1'");
  await click("#apply-headway");
  await cdp.wait(`view.service_plan.line_plans.find(item => item.line === ${JSON.stringify(serviceState.line)} && item.day_type === 'weekday').windows[0].headway_min === ${bulkHeadway}`, "bulk headway adjustment");
  await cdp.wait("document.querySelector('#toast').textContent.includes('Service plan saved')", "bulk service editor refresh");
  serviceState = { ...serviceState, headway: bulkHeadway };
  record("all hourly windows adjusted and saved in one operation", `${bulkHeadway} min first window`);

  await cdp.evaluate("document.querySelector('#copy-service-day').value = 'weekend'");
  await click("#copy-service-plan");
  await cdp.wait(`view.service_plan.line_plans.find(item => item.line === ${JSON.stringify(serviceState.line)} && item.day_type === 'weekend').windows[0].headway_min === ${serviceState.headway}`, "service plan copy to weekend");
  record("complete line service plan copied across day types", `${serviceState.line}: weekday → weekend`);

  const networkScenario = await cdp.evaluate(`(() => {
    const before = Object.fromEntries(view.service_plan.line_plans
      .filter(item => item.day_type === 'weekday')
      .map(item => [item.line, item.windows[0].headway_min]));
    document.querySelector('#toast').textContent = '';
    document.querySelector('#headway-factor').value = '0.9';
    document.querySelector('#headway-scope').value = 'all';
    document.querySelector('#apply-headway').click();
    return {
      before,
      expected: Object.fromEntries(Object.entries(before).map(([line, headway]) => [line, Math.max(1, Math.min(120, Math.round(headway * .9)))])),
    };
  })()`);
  await cdp.wait(`(() => {
    const expected = ${JSON.stringify(networkScenario.expected)};
    return view.service_plan.line_plans
      .filter(item => item.day_type === 'weekday')
      .every(item => item.windows[0].headway_min === expected[item.line]);
  })()`, "atomic all-route weekday adjustment");
  await cdp.wait("document.querySelector('#toast').textContent.includes('route plans adjusted atomically')", "all-route editor refresh");
  serviceState = { ...serviceState, headway: networkScenario.expected[serviceState.line] };
  record("all routes adjusted atomically for one day type", `${Object.keys(networkScenario.expected).length} routes`);

  const odEndpoints = await cdp.evaluate(`(() => {
    const origin = view.snapshot.stations.find(item => item.line === 'line-1');
    const destination = view.snapshot.stations.find(item => item.line === 'line-2');
    return { origin: origin.id, destination: destination.id };
  })()`);
  await form("#demand-form", {
    "demand-period": "weekday-am",
    "demand-origin": odEndpoints.origin,
    "demand-destination": odEndpoints.destination,
    "demand-passengers": 900,
  });
  await cdp.wait("view.snapshot.demand.flows.some(item => item.passengers_per_hour === 900)", "OD demand creation");
  const odFlowId = await cdp.evaluate("view.snapshot.demand.flows.find(item => item.passengers_per_hour === 900).id");
  await cdp.wait(`document.querySelector('[data-demand-edit="${odFlowId}"]')`, "OD demand table refresh");
  const odRender = await cdp.evaluate(`({
    selected: selectedDemandFlowId,
    period: document.querySelector('#demand-period').value,
    rowIds: [...document.querySelectorAll('[data-demand-flow]')].map(item => item.dataset.demandFlow),
    formTitle: document.querySelector('#demand-form-title').textContent,
    toast: document.querySelector('#toast').textContent,
  })`);
  assert(odRender.rowIds.includes(odFlowId), "OD demand row rendered", JSON.stringify(odRender));
  await click(`[data-demand-edit="${odFlowId}"]`);
  await form("#demand-form", { "demand-passengers": 1200 });
  await cdp.wait(`view.snapshot.demand.flows.find(item => item.id === ${JSON.stringify(odFlowId)})?.passengers_per_hour === 1200`, "OD demand edit");
  const odMetric = await cdp.evaluate(`view.snapshot.demand_metrics.find(item => item.flow_id === ${JSON.stringify(odFlowId)})`);
  assert(odMetric.transfers === 1 && odMetric.capacity_pphpd > 0 && odMetric.utilization_percent > 0, "OD transfer and capacity screen regenerated", `${odMetric.capacity_pphpd} pphpd · ${odMetric.utilization_percent.toFixed(1)}%`);
  record("OD demand intent created and edited", odFlowId);

  await click("#compile");
  await cdp.wait("document.querySelector('#operation-result').textContent.includes('Candidate compiled')", "candidate compilation", 90_000);
  await cdp.wait("document.querySelector('#toast').textContent.includes('Candidate compiled with its content hash')", "candidate reload completion", 90_000);
  record("candidate compiled through GUI");

  const jobIds = {};
  jobIds.gis = await runAdapter("gis-export");
  jobIds.fieldEvidence = await runAdapter("field-evidence");
  jobIds.simulation = await runAdapter("simulation");
  jobIds.alignment = await runAdapter("alignment-exchange");
  await cdp.evaluate(`document.querySelector('#service-line').value = ${JSON.stringify(georeferencedLine)}`);
  jobIds.civil = await runAdapter("civil-bim", 240_000);
  await openArtifact(jobIds.gis, "gis-network");
  await openArtifact(jobIds.fieldEvidence, "field-evidence-brief");
  const fieldEvidence = await cdp.evaluate(`({
    datasetCount: selectedArtifactPreview.content.dataset_count,
    briefReady: selectedArtifactPreview.content.brief_ready_for_approval,
    mobilisation: selectedArtifactPreview.content.mobilisation_authorized,
    accepted: selectedArtifactPreview.content.field_evidence_accepted,
  })`);
  assert(fieldEvidence.datasetCount === 11 && fieldEvidence.briefReady && !fieldEvidence.mobilisation && !fieldEvidence.accepted, "field-evidence job issues requirements without claiming external acceptance", `${fieldEvidence.datasetCount} packages`);
  await openArtifact(jobIds.simulation, "simulation-result");
  await openArtifact(jobIds.alignment, "landxml");
  await openArtifact(jobIds.civil, "civil-bim-index");
  const civilGeoreferencing = await cdp.evaluate("selectedArtifactPreview.content.georeferencing");
  assert(civilGeoreferencing.native_ifc_georeferencing && civilGeoreferencing.crs_name === "EPSG:32638", "civil IFC carries selected line map conversion");

  const ifcObjectCount = await cdp.evaluate("selectedArtifactPreview.content.objects.length");
  assert(ifcObjectCount > 20, "IFC object inspector populated", `${ifcObjectCount} objects`);
  const ifcTypeEvidence = await cdp.evaluate(`(() => {
    const content = selectedArtifactPreview.content;
    const index = content.objects.findIndex(item => item.ifc_type_id);
    document.querySelector('.artifact-object-button[data-object-index="' + index + '"]').click();
    return {
      types: content.summary.types,
      typedAssets: content.summary.typed_assets,
      indexedTypes: content.types.length,
      selectedType: content.objects[index].ifc_type_id,
      detail: document.querySelector('.artifact-object-detail').textContent,
      metrics: document.querySelector('#artifact-metrics').textContent,
    };
  })()`);
  assert(
    ifcTypeEvidence.types === 19
      && ifcTypeEvidence.typedAssets === 138
      && ifcTypeEvidence.indexedTypes === 19,
    "native IFC type catalogue indexed",
    `${ifcTypeEvidence.types} types · ${ifcTypeEvidence.typedAssets} typed assets`,
  );
  assert(
    ifcTypeEvidence.selectedType.startsWith("OSR-TYPE-")
      && ifcTypeEvidence.detail.includes(ifcTypeEvidence.selectedType)
      && ifcTypeEvidence.metrics.includes("reusable IFC types"),
    "IFC type identity visible in object inspector",
    ifcTypeEvidence.selectedType,
  );
  const ifcVehicleEvidence = await cdp.evaluate(`(() => {
    const content = selectedArtifactPreview.content;
    const index = content.objects.findIndex(item => item.asset_class === 'rolling-stock.trainset');
    document.querySelector('.artifact-object-button[data-object-index="' + index + '"]').click();
    const vehicle = content.objects[index];
    return {
      vehicles: content.summary.native_rolling_stock_vehicles,
      quantitySets: content.summary.vehicle_base_quantity_sets,
      ifcClass: vehicle.ifc_class,
      typeClass: vehicle.ifc_type_class,
      typePredefinedType: vehicle.ifc_type_predefined_type,
      standardQuantitySets: vehicle.standard_quantity_sets,
      unclaimedOperationalFields: !('capacity_people' in vehicle) && !('availability' in vehicle) && !('serial_number' in vehicle),
      detail: document.querySelector('.artifact-object-detail').textContent,
      metrics: document.querySelector('#artifact-metrics').textContent,
    };
  })()`);
  assert(
    ifcVehicleEvidence.vehicles === 2
      && ifcVehicleEvidence.quantitySets === 2
      && ifcVehicleEvidence.ifcClass === "IfcVehicle"
      && ifcVehicleEvidence.typeClass === "IfcVehicleType"
      && ifcVehicleEvidence.typePredefinedType === "ROLLINGSTOCK"
      && ifcVehicleEvidence.standardQuantitySets.length === 1
      && ifcVehicleEvidence.standardQuantitySets[0] === "Qto_VehicleBaseQuantities"
      && ifcVehicleEvidence.unclaimedOperationalFields,
    "native IFC rolling-stock vehicles and measured base quantities indexed",
    `${ifcVehicleEvidence.vehicles} vehicles · ${ifcVehicleEvidence.quantitySets} quantity sets`,
  );
  assert(
    ifcVehicleEvidence.detail.includes("IfcVehicle")
      && ifcVehicleEvidence.detail.includes("IfcVehicleType · ROLLINGSTOCK")
      && ifcVehicleEvidence.detail.includes("Qto_VehicleBaseQuantities")
      && ifcVehicleEvidence.metrics.includes("native rolling-stock vehicles")
      && ifcVehicleEvidence.metrics.includes("vehicle base-quantity sets"),
    "vehicle type and dimensional evidence visible without invented operations data",
  );
  const ifcBearingEvidence = await cdp.evaluate(`(() => {
    const content = selectedArtifactPreview.content;
    const bearingIndex = content.objects.findIndex(item => item.asset_class === 'civil.bearing');
    document.querySelector('.artifact-object-button[data-object-index="' + bearingIndex + '"]').click();
    const bearing = content.objects[bearingIndex];
    const foundation = content.objects.find(item => item.asset_class === 'civil.foundation-interface');
    return {
      bearings: content.summary.native_bearings,
      foundations: content.summary.foundation_interfaces,
      jackingInterfaces: content.summary.jacking_interfaces,
      pierCaps: content.summary.pier_caps,
      pierColumns: content.summary.pier_columns,
      connectionRelationships: content.summary.bearing_connection_relationships,
      connectionRealizations: content.summary.bearing_connection_realizations,
      connectedBearings: content.summary.connected_bearings,
      connectedPierCaps: content.summary.connected_pier_caps,
      connectedSuperstructure: content.summary.connected_superstructure_assets,
      indexedConnections: content.bearing_connections.length,
      bearingConnectionCount: bearing.bearing_connection_count,
      bearingConnectionIds: bearing.bearing_connection_ids,
      ifcClass: bearing.ifc_class,
      typeClass: bearing.ifc_type_class,
      typePredefinedType: bearing.ifc_type_predefined_type,
      sourcePartRole: bearing.source_part_role,
      bearingStatus: bearing.engineering_status,
      foundationClass: foundation.ifc_class,
      foundationStatus: foundation.engineering_status,
      detail: document.querySelector('.artifact-object-detail').textContent,
      metrics: document.querySelector('#artifact-metrics').textContent,
    };
  })()`);
  assert(
    ifcBearingEvidence.bearings === 36
      && ifcBearingEvidence.foundations === 9
      && ifcBearingEvidence.jackingInterfaces === 36
      && ifcBearingEvidence.pierCaps === 9
      && ifcBearingEvidence.pierColumns === 9
      && ifcBearingEvidence.connectionRelationships === 27
      && ifcBearingEvidence.connectionRealizations === 60
      && ifcBearingEvidence.connectedBearings === 36
      && ifcBearingEvidence.connectedPierCaps === 9
      && ifcBearingEvidence.connectedSuperstructure === 13
      && ifcBearingEvidence.indexedConnections === 27
      && [1, 2].includes(ifcBearingEvidence.bearingConnectionCount)
      && ifcBearingEvidence.bearingConnectionIds.length === ifcBearingEvidence.bearingConnectionCount
      && ifcBearingEvidence.ifcClass === "IfcBearing"
      && ifcBearingEvidence.typeClass === "IfcBearingType"
      && ifcBearingEvidence.typePredefinedType === "ELASTOMERIC"
      && ifcBearingEvidence.sourcePartRole === "bearing"
      && ifcBearingEvidence.bearingStatus.supplier_selection_status === "unresolved"
      && ifcBearingEvidence.foundationClass === "IfcVirtualElement"
      && ifcBearingEvidence.foundationStatus.actual_foundation_depth === "intentionally-not-modelled",
    "pier compounds split into truthful native parts and virtual release interfaces",
    `${ifcBearingEvidence.bearings} bearings · ${ifcBearingEvidence.foundations} foundation interfaces`,
  );
  assert(
    ifcBearingEvidence.detail.includes("civil.bearing")
      && ifcBearingEvidence.detail.includes("elastomeric/PTFE")
      && ifcBearingEvidence.detail.includes("supplier_selection_status")
      && ifcBearingEvidence.detail.includes("bearing connections")
      && ifcBearingEvidence.metrics.includes("native bridge bearings")
      && ifcBearingEvidence.metrics.includes("bearing-realized connections")
      && ifcBearingEvidence.metrics.includes("bearing connection realizations")
      && ifcBearingEvidence.metrics.includes("virtual foundation interfaces"),
    "bearing identity and unresolved engineering boundary visible in object inspector",
  );
  const ifcBearingConnectionEvidence = await cdp.evaluate(`(() => {
    const items = artifactInspectorItems(selectedArtifactPreview);
    const index = items.findIndex(item => item.detail.includes('bearing connection OSR-CONN-'));
    document.querySelector('.artifact-object-button[data-object-index="' + index + '"]').click();
    return {
      count: selectedArtifactPreview.content.bearing_connections.length,
      meta: items[index].meta,
      detail: document.querySelector('.artifact-object-detail').textContent,
    };
  })()`);
  assert(
    ifcBearingConnectionEvidence.count === 27
      && ifcBearingConnectionEvidence.meta.includes("IfcRelConnectsWithRealizingElements")
      && ifcBearingConnectionEvidence.detail.includes("realizing bearings")
      && ifcBearingConnectionEvidence.detail.includes("source bbox face contact")
      && ifcBearingConnectionEvidence.detail.includes("structural release unresolved"),
    "bearing-realized support topology inspectable without invented analytical data",
    `${ifcBearingConnectionEvidence.count} connections`,
  );
  const ifcExternalDecisionEvidence = await cdp.evaluate(`(() => {
    const content = selectedArtifactPreview.content;
    const items = artifactInspectorItems(selectedArtifactPreview);
    const index = items.findIndex(item => item.detail.includes('external engineering decision OSR-DEC-SURVEY-ALIGNMENT'));
    document.querySelector('.artifact-object-button[data-object-index="' + index + '"]').click();
    return {
      count: content.external_engineering_decisions.length,
      closure: content.capability_closure,
      detail: document.querySelector('.artifact-object-detail').textContent,
      metrics: document.querySelector('#artifact-metrics').textContent,
    };
  })()`);
  assert(
    ifcExternalDecisionEvidence.count === 9
      && ifcExternalDecisionEvidence.closure.status === "source-supported-ifc-work-complete"
      && ifcExternalDecisionEvidence.closure.implementable_open_task_count === 0,
    "source-supported IFC capability closure indexed",
    `${ifcExternalDecisionEvidence.count} external decisions · 0 implementable tasks`,
  );
  assert(
    ifcExternalDecisionEvidence.detail.includes("external-evidence-required")
      && ifcExternalDecisionEvidence.detail.includes("project surveyor and alignment engineer")
      && ifcExternalDecisionEvidence.detail.includes("required evidence")
      && ifcExternalDecisionEvidence.detail.includes("blocked capabilities")
      && ifcExternalDecisionEvidence.detail.includes("safe current state")
      && ifcExternalDecisionEvidence.metrics.includes("external engineering decisions")
      && ifcExternalDecisionEvidence.metrics.includes("implementable open IFC tasks")
      && ifcExternalDecisionEvidence.metrics.includes("source-supported-ifc-work-complete"),
    "external authority, evidence, blocked capability, and safe-state boundary visible",
  );
  const ifcMaterialEvidence = await cdp.evaluate(`(() => {
    const content = selectedArtifactPreview.content;
    const index = content.objects.findIndex(item => item.material_id);
    document.querySelector('.artifact-object-button[data-object-index="' + index + '"]').click();
    return {
      materials: content.summary.materials,
      associatedAssets: content.summary.material_associated_assets,
      indexedMaterials: content.materials.length,
      detail: document.querySelector('.artifact-object-detail').textContent,
      metrics: document.querySelector('#artifact-metrics').textContent,
    };
  })()`);
  assert(
    ifcMaterialEvidence.materials === 3
      && ifcMaterialEvidence.associatedAssets === 46
      && ifcMaterialEvidence.indexedMaterials === 3,
    "native IFC material-family catalogue indexed",
    `${ifcMaterialEvidence.materials} families · ${ifcMaterialEvidence.associatedAssets} associated assets`,
  );
  assert(
    ifcMaterialEvidence.detail.includes("OSR-MAT-FAMILY-")
      && ifcMaterialEvidence.detail.includes("grade-and-design-unresolved")
      && ifcMaterialEvidence.metrics.includes("declared material families"),
    "material family and unresolved specification status visible in object inspector",
  );
  const ifcProfileEvidence = await cdp.evaluate(`(() => {
    const content = selectedArtifactPreview.content;
    const index = content.objects.findIndex(item => item.profile_id);
    document.querySelector('.artifact-object-button[data-object-index="' + index + '"]').click();
    return {
      profiles: content.summary.profiles,
      profiledAssets: content.summary.profiled_assets,
      indexedProfiles: content.profiles.length,
      detail: document.querySelector('.artifact-object-detail').textContent,
      metrics: document.querySelector('#artifact-metrics').textContent,
    };
  })()`);
  assert(
    ifcProfileEvidence.profiles === 1
      && ifcProfileEvidence.profiledAssets === 32
      && ifcProfileEvidence.indexedProfiles === 1,
    "native IFC section-profile catalogue indexed",
    `${ifcProfileEvidence.profiles} profile · ${ifcProfileEvidence.profiledAssets} extruded assets`,
  );
  assert(
    ifcProfileEvidence.detail.includes("OSR-PROFILE-UIC-60E1-REVIEW")
      && ifcProfileEvidence.detail.includes("simplified-straight-line-review-polygon")
      && ifcProfileEvidence.metrics.includes("native section profiles"),
    "native profile identity and review-geometry limitation visible in object inspector",
  );
  const ifcClassificationEvidence = await cdp.evaluate(`(() => {
    const content = selectedArtifactPreview.content;
    const classificationIndex = content.objects.length;
    document.querySelector('.artifact-object-button[data-object-index="' + classificationIndex + '"]').click();
    return {
      systems: content.summary.classifications,
      references: content.summary.classification_references,
      classifiedAssets: content.summary.classified_assets,
      indexedReferences: content.classification.references.length,
      codesMatch: content.objects.every(item => item.classification_code === item.asset_class),
      detail: document.querySelector('.artifact-object-detail').textContent,
      metrics: document.querySelector('#artifact-metrics').textContent,
    };
  })()`);
  assert(
    ifcClassificationEvidence.systems === 1
      && ifcClassificationEvidence.references === 15
      && ifcClassificationEvidence.classifiedAssets === 185
      && ifcClassificationEvidence.indexedReferences === 15
      && ifcClassificationEvidence.codesMatch,
    "native OSR asset classification indexed",
    `${ifcClassificationEvidence.references} references · ${ifcClassificationEvidence.classifiedAssets} classified assets`,
  );
  assert(
    ifcClassificationEvidence.detail.includes("OpenSourceRail Asset Classification")
      && ifcClassificationEvidence.detail.includes("internal-deterministic-classification")
      && ifcClassificationEvidence.detail.includes("country-and-client-mapping-not-nominated")
      && ifcClassificationEvidence.metrics.includes("asset-class references"),
    "classification identity, inheritance evidence, and external-mapping boundary visible",
  );
  const ifcGroupEvidence = await cdp.evaluate(`(() => {
    const content = selectedArtifactPreview.content;
    const groupIndex = content.objects.length + content.classification.references.length;
    document.querySelector('.artifact-object-button[data-object-index="' + groupIndex + '"]').click();
    return {
      groups: content.summary.coordination_groups,
      groupedAssets: content.summary.grouped_assets,
      indexedGroups: content.groups.length,
      allAssetsResolve: content.objects.every(item => content.groups.some(group => group.group_id === item.coordination_group_id)),
      detail: document.querySelector('.artifact-object-detail').textContent,
      metrics: document.querySelector('#artifact-metrics').textContent,
    };
  })()`);
  assert(
    ifcGroupEvidence.groups === 5
      && ifcGroupEvidence.groupedAssets === 185
      && ifcGroupEvidence.indexedGroups === 5
      && ifcGroupEvidence.allAssetsResolve,
    "native IFC coordination groups indexed",
    `${ifcGroupEvidence.groups} groups · ${ifcGroupEvidence.groupedAssets} associated assets`,
  );
  assert(
    ifcGroupEvidence.detail.includes("OSR-DT-ZONE-")
      && ifcGroupEvidence.detail.includes("non-spatial-review-group")
      && ifcGroupEvidence.detail.includes("not a surveyed spatial zone")
      && ifcGroupEvidence.detail.includes("not a functional engineering system")
      && ifcGroupEvidence.metrics.includes("native coordination groups"),
    "coordination group identity and semantic boundary visible",
  );
  const ifcLayerEvidence = await cdp.evaluate(`(() => {
    const content = selectedArtifactPreview.content;
    const layerIndex = content.objects.length + content.classification.references.length + content.groups.length;
    document.querySelector('.artifact-object-button[data-object-index="' + layerIndex + '"]').click();
    return {
      layers: content.summary.presentation_layers,
      associatedAssets: content.summary.layer_associated_assets,
      indexedLayers: content.layers.length,
      allAssetsResolve: content.objects.every(item => content.layers.some(layer => layer.layer_id === item.presentation_layer_id)),
      detail: document.querySelector('.artifact-object-detail').textContent,
      metrics: document.querySelector('#artifact-metrics').textContent,
    };
  })()`);
  assert(
    ifcLayerEvidence.layers === 4
      && ifcLayerEvidence.associatedAssets === 185
      && ifcLayerEvidence.indexedLayers === 4
      && ifcLayerEvidence.allAssetsResolve,
    "native IFC presentation layers indexed",
    `${ifcLayerEvidence.layers} layers · ${ifcLayerEvidence.associatedAssets} associated assets`,
  );
  assert(
    ifcLayerEvidence.detail.includes("OSR-LAYER-")
      && ifcLayerEvidence.detail.includes("IfcShapeRepresentation")
      && ifcLayerEvidence.detail.includes("visibility control only")
      && ifcLayerEvidence.metrics.includes("native presentation layers"),
    "presentation-layer identity, assignment scope, and semantic boundary visible",
  );
  const ifcConstraintEvidence = await cdp.evaluate(`(() => {
    const content = selectedArtifactPreview.content;
    const constraintIndex = content.objects.length + content.classification.references.length + content.groups.length + content.layers.length;
    document.querySelector('.artifact-object-button[data-object-index="' + constraintIndex + '"]').click();
    return {
      constraints: content.summary.interface_constraints,
      relatedObjects: content.summary.interface_constraint_related_objects,
      assetLinks: content.summary.interface_constraint_asset_links,
      groupLinks: content.summary.interface_constraint_group_links,
      systemLinks: content.summary.interface_constraint_system_links,
      sourceRelationships: content.summary.constraint_source_document_relationships,
      sourceLinkedConstraintResources: content.summary.source_linked_constraint_resources,
      metricsCount: content.summary.interface_metrics,
      qualitativeOnlyCount: content.summary.qualitative_only_interface_constraints,
      indexedConstraints: content.constraints.length,
      allPass: content.constraints.every(item => item.evaluation_status === 'PASS'),
      detail: document.querySelector('.artifact-object-detail').textContent,
      metrics: document.querySelector('#artifact-metrics').textContent,
    };
  })()`);
  assert(
    ifcConstraintEvidence.constraints === 9
      && ifcConstraintEvidence.indexedConstraints === 9
      && ifcConstraintEvidence.relatedObjects === 107
      && ifcConstraintEvidence.assetLinks === 91
      && ifcConstraintEvidence.groupLinks === 6
      && ifcConstraintEvidence.systemLinks === 1
      && ifcConstraintEvidence.sourceRelationships === 1
      && ifcConstraintEvidence.sourceLinkedConstraintResources === 15
      && ifcConstraintEvidence.metricsCount === 6
      && ifcConstraintEvidence.qualitativeOnlyCount === 3
      && ifcConstraintEvidence.allPass,
    "native IFC interface constraints indexed",
    `${ifcConstraintEvidence.constraints} objectives · ${ifcConstraintEvidence.metricsCount} numeric metrics`,
  );
  assert(
    ifcConstraintEvidence.detail.includes("IfcObjective")
      && ifcConstraintEvidence.detail.includes("HARD")
      && ifcConstraintEvidence.detail.includes("DESIGNINTENT")
      && ifcConstraintEvidence.detail.includes("DESIGN VALIDATION EVIDENCE")
      && ifcConstraintEvidence.detail.includes("OSR-LM3-TEST-001")
      && ifcConstraintEvidence.detail.includes("OSR-DT-ZONE-RST-001")
      && ifcConstraintEvidence.detail.includes("OSR-SYS-ROLLING-STOCK")
      && ifcConstraintEvidence.detail.includes("OSR-DOC-SOURCE-CIVIL-INTEGRATION")
      && ifcConstraintEvidence.detail.includes("IfcExternalReferenceRelationship")
      && ifcConstraintEvidence.detail.includes("no fabricated numeric benchmark")
      && ifcConstraintEvidence.metrics.includes("native interface constraints")
      && ifcConstraintEvidence.metrics.includes("native interface metrics")
      && ifcConstraintEvidence.metrics.includes("constraint evidence links")
      && ifcConstraintEvidence.metrics.includes("source-linked constraint resources"),
    "constraint intent, current evaluation, source, and metric boundary visible",
  );
  const ifcMetricEvidence = await cdp.evaluate(`(() => {
    const content = selectedArtifactPreview.content;
    const constraintOffset = content.objects.length + content.classification.references.length + content.groups.length + content.layers.length;
    const metricConstraintIndex = content.constraints.findIndex(item => item.constraint_id === 'pier-bearing-to-girder-soffit');
    document.querySelector('.artifact-object-button[data-object-index="' + (constraintOffset + metricConstraintIndex) + '"]').click();
    const metricConstraint = content.constraints[metricConstraintIndex];
    return {
      metricStatus: metricConstraint.metric_status,
      metric: metricConstraint.metric,
      detail: document.querySelector('.artifact-object-detail').textContent,
      metrics: document.querySelector('#artifact-metrics').textContent,
    };
  })()`);
  assert(
    ifcMetricEvidence.metricStatus === "structured-native-ifc-metric"
      && ifcMetricEvidence.metric.ifc_class === "IfcMetric"
      && ifcMetricEvidence.metric.benchmark === "EQUALTO"
      && ifcMetricEvidence.metric.observed_value === 9.3
      && ifcMetricEvidence.metric.target_value === 9.3
      && ifcMetricEvidence.metric.measure_type === "IfcLengthMeasure",
    "native numeric interface metric indexed",
    `${ifcMetricEvidence.metric.observed_value} m observed · ${ifcMetricEvidence.metric.target_value} m target`,
  );
  assert(
    ifcMetricEvidence.detail.includes("structured-native-ifc-metric")
      && ifcMetricEvidence.detail.includes("IfcMetric")
      && ifcMetricEvidence.detail.includes("benchmark EQUALTO")
      && ifcMetricEvidence.detail.includes("observed 9.3 m")
      && ifcMetricEvidence.detail.includes("target 9.3 m")
      && ifcMetricEvidence.detail.includes("IfcLengthMeasure")
      && ifcMetricEvidence.detail.includes("no single IFC attribute path")
      && ifcMetricEvidence.metrics.includes("native interface metrics"),
    "native metric benchmark and derivation boundary visible",
  );
  const ifcTemplateEvidence = await cdp.evaluate(`(() => {
    const content = selectedArtifactPreview.content;
    const templateOffset = content.objects.length + content.classification.references.length + content.groups.length + content.layers.length + content.constraints.length;
    const templateIndex = content.property_set_templates.findIndex(item => item.name === 'OSR_MaterialStatus');
    document.querySelector('.artifact-object-button[data-object-index="' + (templateOffset + templateIndex) + '"]').click();
    return {
      templates: content.summary.property_set_templates,
      fields: content.summary.property_templates,
      matchedDefinitions: content.summary.template_matched_definitions,
      linkedDefinitions: content.summary.template_linked_definitions,
      noReservedNames: content.property_set_templates.every(item => !item.name.startsWith('Pset_')),
      detail: document.querySelector('.artifact-object-detail').textContent,
      metrics: document.querySelector('#artifact-metrics').textContent,
    };
  })()`);
  assert(
    ifcTemplateEvidence.templates === 16
      && ifcTemplateEvidence.fields === 99
      && ifcTemplateEvidence.matchedDefinitions === 487
      && ifcTemplateEvidence.linkedDefinitions === 483
      && ifcTemplateEvidence.noReservedNames,
    "native IFC property dictionaries indexed",
    `${ifcTemplateEvidence.templates} templates · ${ifcTemplateEvidence.fields} typed fields`,
  );
  assert(
    ifcTemplateEvidence.detail.includes("OSR_MaterialStatus")
      && ifcTemplateEvidence.detail.includes("PSET_MATERIALDRIVEN")
      && ifcTemplateEvidence.detail.includes("IfcLabel")
      && ifcTemplateEvidence.detail.includes("not-buildingSMART-standard-pset")
      && ifcTemplateEvidence.metrics.includes("native property-set templates"),
    "template applicability, field types, linkage, and custom-set boundary visible",
  );
  const ifcDocumentEvidence = await cdp.evaluate(`(() => {
    const content = selectedArtifactPreview.content;
    const documentIndex = content.objects.length + content.classification.references.length + content.groups.length + content.layers.length + content.constraints.length + content.property_set_templates.length;
    document.querySelector('.artifact-object-button[data-object-index="' + documentIndex + '"]').click();
    const firstDetail = document.querySelector('.artifact-object-detail').textContent;
    const sourceIndex = content.documents.findIndex(item => item.document_id === 'OSR-DOC-SOURCE-CIVIL-INTEGRATION');
    document.querySelector('.artifact-object-button[data-object-index="' + (documentIndex + sourceIndex) + '"]').click();
    const sourceDocument = content.documents[sourceIndex];
    return {
      documents: content.summary.documents,
      linkedAssets: content.summary.document_associated_assets,
      indexedDocuments: content.documents.length,
      allRevisionsLocked: content.documents.every(item => item.revision === 'sha256:' + item.sha256),
      detail: firstDetail,
      sourceConstraintCount: sourceDocument.associated_constraint_count,
      sourceDetail: document.querySelector('.artifact-object-detail').textContent,
      metrics: document.querySelector('#artifact-metrics').textContent,
    };
  })()`);
  assert(
    ifcDocumentEvidence.documents === 15
      && ifcDocumentEvidence.linkedAssets === 185
      && ifcDocumentEvidence.indexedDocuments === 15
      && ifcDocumentEvidence.sourceConstraintCount === 15
      && ifcDocumentEvidence.allRevisionsLocked,
    "native IFC source-document register indexed",
    `${ifcDocumentEvidence.documents} documents · ${ifcDocumentEvidence.linkedAssets} linked assets`,
  );
  assert(
    ifcDocumentEvidence.detail.includes("OSR-DOC-ALIGNMENT-CONTRACT")
      && ifcDocumentEvidence.detail.includes("revision sha256:")
      && ifcDocumentEvidence.detail.includes("docs/civil/osr-aln-format.md")
      && ifcDocumentEvidence.metrics.includes("hash-locked source documents"),
    "hash, repository location, and association scope visible in document inspector",
  );
  assert(
    ifcDocumentEvidence.sourceDetail.includes("OSR-DOC-SOURCE-CIVIL-INTEGRATION")
      && ifcDocumentEvidence.sourceDetail.includes("associated constraints 15")
      && ifcDocumentEvidence.sourceDetail.includes("pier-bearing-to-girder-soffit"),
    "hash-locked civil source document linked to every native interface objective and metric",
  );
  const ifcAlignmentEvidence = await cdp.evaluate(`(() => {
    const content = selectedArtifactPreview.content;
    const alignmentIndex = content.objects.length + content.classification.references.length + content.groups.length + content.layers.length + content.constraints.length + content.property_set_templates.length + content.documents.length;
    document.querySelector('.artifact-object-button[data-object-index="' + alignmentIndex + '"]').click();
    return {
      geometryCurve: content.alignment.geometry_curve,
      controlPoints: content.alignment.control_point_count,
      horizontalSegments: content.alignment.horizontal_segment_count,
      verticalSegments: content.alignment.vertical_segment_count,
      stationingReferents: content.alignment.stationing_referent_count,
      totalLength: content.alignment.total_horizontal_length_m,
      detail: document.querySelector('.artifact-object-detail').textContent,
      metrics: document.querySelector('#artifact-metrics').textContent,
    };
  })()`);
  assert(
    ifcAlignmentEvidence.geometryCurve === "IfcGradientCurve"
      && ifcAlignmentEvidence.controlPoints >= 2
      && ifcAlignmentEvidence.horizontalSegments === ifcAlignmentEvidence.controlPoints - 1
      && ifcAlignmentEvidence.verticalSegments === ifcAlignmentEvidence.controlPoints - 1
      && ifcAlignmentEvidence.stationingReferents === 2
      && ifcAlignmentEvidence.totalLength > 0,
    "native IFC4.3 alignment layouts indexed",
    `${ifcAlignmentEvidence.horizontalSegments} horizontal · ${ifcAlignmentEvidence.verticalSegments} vertical segments`,
  );
  assert(
    ifcAlignmentEvidence.detail.includes("native-ifc4.3-horizontal-and-vertical-layouts")
      && ifcAlignmentEvidence.detail.includes("LINE")
      && ifcAlignmentEvidence.detail.includes("CONSTANTGRADIENT")
      && ifcAlignmentEvidence.detail.includes("cant not-modelled")
      && ifcAlignmentEvidence.detail.includes("transitions not-modelled")
      && ifcAlignmentEvidence.metrics.includes("native horizontal alignment segments")
      && ifcAlignmentEvidence.metrics.includes("alignment stationing referents"),
    "alignment semantics, stationing, and design-release boundary visible",
  );
  const ifcCostEvidence = await cdp.evaluate(`(() => {
    const content = selectedArtifactPreview.content;
    const alignmentIndex = content.objects.length + content.classification.references.length + content.groups.length + content.layers.length + content.constraints.length + content.property_set_templates.length + content.documents.length;
    const scheduleIndex = alignmentIndex + 1;
    document.querySelector('.artifact-object-button[data-object-index="' + scheduleIndex + '"]').click();
    const scheduleDetail = document.querySelector('.artifact-object-detail').textContent;
    const elevatedIndex = content.cost_schedule.items.findIndex(item => item.civil_class === 'elevated');
    document.querySelector('.artifact-object-button[data-object-index="' + (scheduleIndex + 1 + elevatedIndex) + '"]').click();
    const rateDetail = document.querySelector('.artifact-object-detail').textContent;
    const costDocument = content.documents.find(item => item.document_id === 'OSR-DOC-CIVIL-COST-CONTRACT');
    return {
      schedules: content.summary.planning_rate_schedules,
      items: content.summary.planning_rate_items,
      predefinedType: content.cost_schedule.predefined_type,
      currency: content.cost_schedule.currency,
      maturity: content.cost_schedule.maturity,
      rates: Object.fromEntries(content.cost_schedule.items.map(item => [item.civil_class, item.rate_usd_per_route_km])),
      noQuantities: content.cost_schedule.items.every(item => item.quantity_status.startsWith('none;')),
      noAssignments: content.cost_schedule.items.every(item => item.product_assignment_status.startsWith('none;')),
      costDocumentLinked: costDocument.associated_cost_schedule && costDocument.associated_object_count === 2,
      scheduleDetail,
      rateDetail,
      metrics: document.querySelector('#artifact-metrics').textContent,
    };
  })()`);
  assert(
    ifcCostEvidence.schedules === 1
      && ifcCostEvidence.items === 3
      && ifcCostEvidence.predefinedType === "SCHEDULEOFRATES"
      && ifcCostEvidence.currency === "USD"
      && ifcCostEvidence.maturity === "planning-target-not-a-quotation"
      && ifcCostEvidence.rates["at-grade"] === 2584000
      && ifcCostEvidence.rates.elevated === 9748000
      && ifcCostEvidence.rates.bridge === 18000000
      && ifcCostEvidence.noQuantities
      && ifcCostEvidence.noAssignments
      && ifcCostEvidence.costDocumentLinked,
    "native IFC planning schedule of rates indexed",
    `USD ${ifcCostEvidence.rates.elevated.toLocaleString()}/km elevated`,
  );
  assert(
    ifcCostEvidence.scheduleDetail.includes("OSR-COST-RATES-001")
      && ifcCostEvidence.scheduleDetail.includes("no selected scenario")
      && ifcCostEvidence.scheduleDetail.includes("or project total")
      && ifcCostEvidence.rateDetail.includes("OSR-RATE-ELEVATED")
      && ifcCostEvidence.rateDetail.includes("bare_beam_concrete_m3_per_km")
      && ifcCostEvidence.rateDetail.includes("none; schedule-of-rates entry only")
      && ifcCostEvidence.rateDetail.includes("none; alternatives are not selected scope")
      && ifcCostEvidence.metrics.includes("native planning schedules of rates")
      && ifcCostEvidence.metrics.includes("planning unit-rate alternatives"),
    "rate provenance, quantity drivers, and no-estimate boundary visible",
  );
  const ifcSystemEvidence = await cdp.evaluate(`(() => {
    const content = selectedArtifactPreview.content;
    const baseIndex = content.objects.length + content.classification.references.length + content.groups.length + content.layers.length + content.constraints.length + content.property_set_templates.length + content.documents.length;
    const systemIndex = baseIndex + (content.alignment ? 1 : 0) + (content.cost_schedule ? 1 + content.cost_schedule.items.length : 0);
    const trackSystemOffset = content.systems.findIndex(system => system.system_id === 'OSR-SYS-TRACK');
    document.querySelector('.artifact-object-button[data-object-index="' + (systemIndex + trackSystemOffset) + '"]').click();
    return {
      systems: content.summary.functional_systems,
      builtSystems: content.summary.built_systems,
      linkedAssets: content.summary.system_associated_assets,
      spatialReferences: content.summary.system_spatial_part_references,
      indexedSystems: content.systems.length,
      uniqueMembership: content.objects.every(item => typeof item.functional_system_id === 'string' && item.functional_system_id.length > 0)
        && new Set(content.systems.flatMap(system => system.asset_ids)).size === content.objects.length
        && content.systems.reduce((sum, system) => sum + system.asset_count, 0) === content.objects.length,
      systemIds: content.systems.map(system => system.system_id),
      detail: document.querySelector('.artifact-object-detail').textContent,
      metrics: document.querySelector('#artifact-metrics').textContent,
      controls: document.querySelectorAll('[data-civil-system]').length,
    };
  })()`);
  assert(
    ifcSystemEvidence.systems === 6
      && ifcSystemEvidence.linkedAssets === 185
      && ifcSystemEvidence.builtSystems === 3
      && ifcSystemEvidence.spatialReferences === 7
      && ifcSystemEvidence.indexedSystems === 6
      && ifcSystemEvidence.controls === 6
      && ifcSystemEvidence.uniqueMembership
      && ifcSystemEvidence.systemIds.includes("OSR-SYS-CIVIL-INTERFACES")
      && ifcSystemEvidence.systemIds.includes("OSR-SYS-TRACK"),
    "native IFC functional systems cover every asset exactly once",
    `${ifcSystemEvidence.systems} systems · ${ifcSystemEvidence.builtSystems} specialized · ${ifcSystemEvidence.linkedAssets} linked assets`,
  );
  assert(
    ifcSystemEvidence.detail.includes("IFC class IfcBuiltSystem")
      && ifcSystemEvidence.detail.includes("predefined type RAILWAYTRACK")
      && ifcSystemEvidence.detail.includes("railway-part references Track")
      && ifcSystemEvidence.detail.includes("not an IfcSpatialZone")
      && ifcSystemEvidence.detail.includes("not commissioned or operational")
      && ifcSystemEvidence.metrics.includes("native functional systems")
      && ifcSystemEvidence.metrics.includes("specialized built systems")
      && ifcSystemEvidence.metrics.includes("system / railway-part references"),
    "functional-system subtype, spatial service, and release boundary visible",
  );
  const civilReview = await cdp.evaluate(`({
    controls: !document.querySelector('#civil-review-controls').hidden,
    tasks: selectedCivilSequence?.content?.tasks?.length || 0,
    outputTasks: selectedArtifactPreview.content.summary.construction_output_tasks,
    scheduledPhysicalAssets: selectedArtifactPreview.content.summary.scheduled_physical_assets,
    virtualReviewGateAssets: selectedArtifactPreview.content.summary.virtual_review_gate_assets,
    assignmentCounts: Object.fromEntries(Object.entries(selectedCivilSequence?.content?.product_assignments || {}).map(([key, value]) => [key, value.length])),
    reviewGateCounts: Object.fromEntries(Object.entries(selectedCivilSequence?.content?.review_gate_assignments || {}).map(([key, value]) => [key, value.length])),
    sequenceVerified: selectedCivilSequence?.sha256_verified || false,
    paths: document.querySelectorAll('#artifact-canvas [data-object-index]').length,
    firstPath: document.querySelector('#artifact-canvas [data-object-index]')?.getAttribute('d'),
  })`);
  assert(civilReview.controls && civilReview.tasks > 10 && civilReview.sequenceVerified, "verified 4D construction controls loaded", `${civilReview.tasks} tasks`);
  assert(
    civilReview.outputTasks === 5
      && civilReview.scheduledPhysicalAssets === 134
      && civilReview.virtualReviewGateAssets === 45
      && civilReview.assignmentCounts["VIA-05"] === 18
      && civilReview.assignmentCounts["VIA-50"] === 48
      && civilReview.assignmentCounts["VIA-60"] === 54
      && civilReview.reviewGateCounts["VIA-05"] === 9
      && civilReview.reviewGateCounts["VIA-50"] === 36,
    "4D tasks separate physical outputs from virtual review interfaces",
    `${civilReview.scheduledPhysicalAssets} physical outputs · ${civilReview.virtualReviewGateAssets} review gates`,
  );
  const substructureStageEvidence = await cdp.evaluate(`(() => {
    const tasks = selectedCivilSequence.content.tasks;
    const index = tasks.findIndex(task => task.id === 'VIA-05');
    const stage = document.querySelector('#civil-stage');
    stage.value = String(index + 1);
    stage.dispatchEvent(new Event('input', { bubbles: true }));
    return document.querySelector('.civil-stage-label').parentElement.parentElement.textContent;
  })()`);
  assert(
    substructureStageEvidence.includes("18 physical outputs")
      && substructureStageEvidence.includes("9 virtual review interfaces"),
    "substructure-stage output and review-gate counts visible",
  );
  await cdp.evaluate(`(() => {
    const stage = document.querySelector('#civil-stage');
    stage.value = stage.max;
    stage.dispatchEvent(new Event('input', { bubbles: true }));
  })()`);
  assert(civilReview.paths === ifcObjectCount, "full civil federation visible at final stage", `${civilReview.paths} assets`);
  await cdp.evaluate(`(() => {
    const angle = document.querySelector('#civil-view-angle');
    angle.value = '45';
    angle.dispatchEvent(new Event('input', { bubbles: true }));
    return true;
  })()`);
  const rotatedPath = await cdp.evaluate("document.querySelector('#artifact-canvas [data-object-index]')?.getAttribute('d')");
  assert(rotatedPath && rotatedPath !== civilReview.firstPath, "civil federation rotation changes projected geometry");
  const layerVisibility = await cdp.evaluate(`(() => {
    const checkbox = document.querySelector('[data-civil-layer="OSR-LAYER-TRACK"]');
    checkbox.checked = false;
    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
    return document.querySelectorAll('#artifact-canvas [data-object-index]').length;
  })()`);
  assert(layerVisibility === 136, "native IFC presentation-layer visibility filters geometry", `${layerVisibility} non-track assets`);
  await cdp.evaluate(`(() => {
    const checkbox = document.querySelector('[data-civil-layer="OSR-LAYER-TRACK"]');
    checkbox.checked = true;
    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
    return true;
  })()`);
  const groupVisibility = await cdp.evaluate(`(() => {
    const checkbox = document.querySelector('[data-civil-group="OSR-DT-ZONE-VIA-001"]');
    checkbox.checked = false;
    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
    return document.querySelectorAll('#artifact-canvas [data-object-index]').length;
  })()`);
  assert(groupVisibility === 26, "native IFC coordination-group visibility filters geometry", `${groupVisibility} non-viaduct assets`);
  await cdp.evaluate(`(() => {
    const checkbox = document.querySelector('[data-civil-group="OSR-DT-ZONE-VIA-001"]');
    checkbox.checked = true;
    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
    return true;
  })()`);
  const systemVisibility = await cdp.evaluate(`(() => {
    const checkbox = document.querySelector('[data-civil-system="OSR-SYS-GUIDEWAY"]');
    checkbox.checked = false;
    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
    return document.querySelectorAll('#artifact-canvas [data-object-index]').length;
  })()`);
  assert(systemVisibility === 107, "native IFC functional-system visibility filters geometry", `${systemVisibility} non-guideway assets`);
  await cdp.evaluate(`(() => {
    const checkbox = document.querySelector('[data-civil-system="OSR-SYS-GUIDEWAY"]');
    checkbox.checked = true;
    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
    const stage = document.querySelector('#civil-stage');
    stage.value = '0';
    stage.dispatchEvent(new Event('input', { bubbles: true }));
    document.querySelector('#civil-playback').click();
    return true;
  })()`);
  await cdp.wait("civilReviewState.stage > 0", "4D playback advances construction stage", 10_000);
  await click("#civil-playback");
  await cdp.evaluate(`(() => {
    const stage = document.querySelector('#civil-stage');
    stage.value = stage.max;
    stage.dispatchEvent(new Event('input', { bubbles: true }));
    return true;
  })()`);
  await cdp.wait(`document.querySelectorAll('#artifact-canvas [data-object-index]').length === ${ifcObjectCount}`, "4D final stage restoration");
  record("interactive 4D construction playback and final-stage restoration");
  const filterResult = await cdp.evaluate(`(() => {
    const filter = document.querySelector('#artifact-object-filter');
    filter.value = document.querySelector('.artifact-object-button strong').textContent;
    filter.dispatchEvent(new Event('input', { bubbles: true }));
    const visible = [...document.querySelectorAll('[data-object-row]')].filter(row => !row.hidden).length;
    filter.value = '';
    filter.dispatchEvent(new Event('input', { bubbles: true }));
    return visible;
  })()`);
  assert(filterResult > 0 && filterResult < ifcObjectCount, "IFC asset search filters the inspector", `${filterResult} matching objects`);
  await cdp.evaluate(`(() => {
    const boxes = [...document.querySelectorAll('[data-asset-index]')].slice(0, 2);
    boxes.forEach(box => {
      if (!box.checked) box.click();
    });
    return true;
  })()`);
  await cdp.wait("selectedCoordinationAssetIds.size === 2", "two IFC assets selected");
  record("multiple IFC assets selected for one coordination topic");
  await form("#coordination-create-form", {
    title: "GUI acceptance multi-discipline clearance",
    description: "Verify the selected civil asset clearance and document acceptance evidence before issue.",
    assignee: "Civil integration",
  });
  await cdp.wait("view.snapshot.coordination.issues.some(item => item.title === 'GUI acceptance multi-discipline clearance')", "coordination topic creation");
  const issueId = await cdp.evaluate("view.snapshot.coordination.issues.find(item => item.title === 'GUI acceptance multi-discipline clearance').id");
  const issueAssetCount = await cdp.evaluate(`view.snapshot.coordination.issues.find(item => item.id === ${JSON.stringify(issueId)}).asset_ids.length`);
  assert(issueAssetCount === 2, "Git-reviewable coordination topic created from multiple IFC objects", issueId);

  jobIds.civilReissued = await runAdapter("civil-bim", 240_000);
  await openArtifact(jobIds.civilReissued, "civil-bcf3-index");
  await cdp.evaluate(`(() => {
    const index = selectedArtifactPreview.content.topics.findIndex(item => item.issue_id === ${JSON.stringify(issueId)});
    document.querySelector('[data-object-index="' + index + '"]').click();
    return index;
  })()`);
  await form("#coordination-review-form", {
    status: "in-progress",
    assignee: "Civil integration",
    resolution: "",
    reviewed_by: "",
  });
  await cdp.wait(`view.snapshot.coordination.issues.find(item => item.id === ${JSON.stringify(issueId)})?.status === 'in-progress'`, "coordination status save");
  record("BCF coordination status and assignee saved");

  await openArtifact(jobIds.civilReissued, "civil-ids-report");
  const idsPass = await cdp.evaluate("selectedArtifactPreview.content.status === true && selectedArtifactPreview.content.total_checks_pass === selectedArtifactPreview.content.total_checks");
  assert(idsPass, "IDS report passes every delivery check");

  await click("#revision");
  await cdp.wait("document.querySelector('#operation-result').textContent.includes('Revision osr-')", "revision materialization", 90_000);
  await cdp.wait("document.querySelector('#toast').textContent.includes('Immutable revision created')", "revision reload completion", 90_000);
  const revisionId = await cdp.evaluate("revisions.revisions.find(item => item.is_current)?.revision_id || revisions.revisions[0].revision_id");
  record("immutable revision materialized", revisionId);
  await form("#approval-form", {
    "approval-revision": revisionId,
    "approval-status": "approved",
    "approval-date": "2026-08-27",
    "approval-reviewer": "GUI Acceptance Reviewer",
    "approval-role": "Independent design authority",
    "approval-reference": "https://github.com/modernecotech/OpenSourceRail/pull/99999",
    "approval-comment": "Reviewed the immutable revision, engineering artifacts, IDS report, and coordination evidence.",
  });
  await cdp.wait(`view.approvals.decisions.some(item => item.revision_id === ${JSON.stringify(revisionId)} && item.status === 'approved')`, "append-only revision approval");
  const approvalId = await cdp.evaluate(`view.approvals.decisions.find(item => item.revision_id === ${JSON.stringify(revisionId)}).id`);
  const candidateAfterApproval = await cdp.evaluate("(async () => (await api.revisions()).candidate_revision_id)()");
  assert(candidateAfterApproval === revisionId, "approval leaves immutable design hash unchanged", approvalId);
  await click("#compare-revision");
  await cdp.wait("comparison?.base_revision_id?.startsWith('osr-')", "semantic revision comparison");
  record("semantic revision comparison rendered");

  terminate(cityProcess);
  await new Promise((resolve) => cityProcess.once("exit", resolve));
  cityProcess = await startCityStudio(cityPort);
  await cdp.page.reload({ waitUntil: "domcontentloaded" });
  await cdp.wait("typeof view === 'object' && view?.snapshot?.stations?.length > 0", "render after server restart", 60_000);
  await cdp.wait(`document.querySelector('[data-demand-delete="${odFlowId}"]') && gisLayers.get('routing-demand')?.features?.length > 0`, "complete GIS and demand render after restart", 60_000);
  const persisted = await cdp.evaluate(`({
    moved: view.snapshot.stations.find(item => item.id === ${JSON.stringify(movedStation)})?.state,
    station: view.snapshot.stations.find(item => item.id === ${JSON.stringify(manualStation)})?.name,
    control: view.snapshot.line_control_points.find(item => item.id === ${JSON.stringify(controlId)})?.influence_m,
    direct: view.snapshot.lines.find(item => item.id === ${JSON.stringify(directLine)})?.name,
    demand: view.snapshot.lines.find(item => item.id === ${JSON.stringify(demandLine)})?.routing_method,
    headway: view.service_plan.line_plans.find(item => item.line === ${JSON.stringify(serviceState.line)} && item.day_type === 'weekday')?.windows[0]?.headway_min,
    networkHeadways: Object.fromEntries(view.service_plan.line_plans
      .filter(item => item.day_type === 'weekday')
      .map(item => [item.line, item.windows[0].headway_min])),
    issue: view.snapshot.coordination.issues.find(item => item.id === ${JSON.stringify(issueId)})?.status,
    approval: view.approvals.decisions.find(item => item.id === ${JSON.stringify(approvalId)})?.status,
    odPassengers: view.snapshot.demand.flows.find(item => item.id === ${JSON.stringify(odFlowId)})?.passengers_per_hour,
    odCapacity: view.snapshot.demand_metrics.find(item => item.flow_id === ${JSON.stringify(odFlowId)})?.capacity_pphpd,
    civilUnitSpans: view.snapshot.civil.expansion_unit_spans,
    civilMouldCycle: view.snapshot.civil.mould_cycle_target_h,
    civilCompareRoads: view.snapshot.civil.compare_road_grade_separation,
    civilGeoreferencing: view.snapshot.civil.ifc_georeferencing?.find(item => item.line === ${JSON.stringify(georeferencedLine)}),
    jobs: jobView.jobs.filter(item => item.status === 'succeeded').length,
  })`);
  assert(persisted.moved === "preferred", "moved station survived restart");
  assert(persisted.station === "GUI Acceptance Station", "manual station survived restart");
  assert(persisted.control === 2400, "alignment control survived restart");
  assert(persisted.direct === "GUI Direct Line" && persisted.demand === "demand-aware", "both line routing modes survived restart");
  assert(persisted.headway === serviceState.headway, "service-by-day variables survived restart");
  assert(JSON.stringify(persisted.networkHeadways) === JSON.stringify(networkScenario.expected), "atomic all-route scenario survived restart");
  assert(persisted.issue === "in-progress", "coordination decision survived restart");
  assert(persisted.approval === "approved", "append-only approval survived restart");
  assert(persisted.odPassengers === 1200 && persisted.odCapacity > 0, "OD demand and capacity screen survived restart");
  assert(persisted.civilUnitSpans === 5 && persisted.civilMouldCycle === 48 && persisted.civilCompareRoads === false, "civil construction intent survived restart");
  assert(persisted.civilGeoreferencing?.crs_name === "EPSG:32638" && persisted.civilGeoreferencing?.source.includes("S-04"), "per-line IFC survey control survived restart");
  assert(persisted.jobs >= 5, "engineering job history survived restart", `${persisted.jobs} succeeded jobs`);

  await cdp.evaluate("window.confirm = () => true");
  await click(`[data-demand-delete="${odFlowId}"]`);
  await cdp.wait(`!view.snapshot.demand.flows.some(item => item.id === ${JSON.stringify(odFlowId)})`, "OD demand deletion");
  await form("#demand-form", {
    "demand-period": "weekday-am",
    "demand-origin": odEndpoints.origin,
    "demand-destination": odEndpoints.destination,
    "demand-passengers": 1200,
  });
  await cdp.wait(`view.snapshot.demand.flows.some(item => item.id === ${JSON.stringify(odFlowId)})`, "OD demand deterministic recreation");
  record("OD flow deletion and stable-ID recreation persisted", odFlowId);
  await click(`circle.station[data-id="${manualStation}"]`);
  await click("#delete-station");
  await cdp.wait(`!view.snapshot.stations.some(item => item.id === ${JSON.stringify(manualStation)})`, "manual station retirement");
  await cdp.evaluate(`selectLine(${JSON.stringify(directLine)})`);
  await click("#delete-line");
  await cdp.wait(`!view.snapshot.lines.some(item => item.id === ${JSON.stringify(directLine)})`, "manual line retirement");
  record("manual station and line retirement persisted to intent");

  await mkdir(path.dirname(screenshotPath), { recursive: true });
  await cdp.page.screenshot({ path: screenshotPath, fullPage: true });
  record("browser screenshot captured", path.relative(root, screenshotPath));

  const overrides = await readFile(path.join(fixture, "network", "overrides.toml"), "utf8");
  const coordination = await readFile(path.join(fixture, "coordination", "issues.toml"), "utf8");
  const approvals = await readFile(path.join(fixture, "approvals", "reviews.toml"), "utf8");
  const services = await readFile(path.join(fixture, "services", "service-plan.toml"), "utf8");
  const demand = await readFile(path.join(fixture, "demand", "od-matrix.toml"), "utf8");
  const projectIntent = await readFile(path.join(fixture, "project.osr.toml"), "utf8");
  assert(overrides.includes(manualStation) && overrides.includes('state = "retired"'), "retirement is explicit in TOML intent");
  assert(coordination.includes(issueId) && coordination.includes('status = "in-progress"'), "coordination TOML contains saved decision");
  assert(approvals.includes(approvalId) && approvals.includes(`revision_id = "${revisionId}"`), "approval TOML references immutable revision");
  assert(services.includes(`headway_min = ${serviceState.headway}`), "service TOML contains edited headway");
  assert(demand.includes(odFlowId) && demand.includes("passengers_per_hour = 1200"), "demand TOML contains deterministic edited OD flow");
  assert(projectIntent.includes("expansion_unit_spans = 5") && projectIntent.includes("mould_cycle_target_h = 48") && projectIntent.includes("compare_road_grade_separation = false"), "project TOML contains civil construction intent");
  assert(projectIntent.includes("[[civil.ifc_georeferencing]]") && projectIntent.includes('crs_name = "EPSG:32638"'), "project TOML contains per-line IFC survey control");

  const report = {
    schema: "org.opensourcerail.city-studio-gui-acceptance.v1",
    passed: true,
    started_at: startedAt.toISOString(),
    finished_at: new Date().toISOString(),
    browser: "Playwright Chromium",
    isolated_project: path.relative(root, fixture),
    checks,
    persistence: { movedStation, manualStation, controlId, directLine, demandLine, odFlowId, issueId, revisionId, approvalId },
    artifacts: { screenshot: path.relative(root, screenshotPath) },
  };
  await writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`);
  process.stdout.write(`\n${checks.length} GUI acceptance checks passed.\nReport: ${path.relative(root, reportPath)}\nScreenshot: ${path.relative(root, screenshotPath)}\n`);
}

try {
  await main();
} catch (error) {
  const report = {
    schema: "org.opensourcerail.city-studio-gui-acceptance.v1",
    passed: false,
    started_at: startedAt.toISOString(),
    finished_at: new Date().toISOString(),
    error: error.stack || String(error),
    checks,
  };
  await mkdir(reportDir, { recursive: true });
  await writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`);
  process.stderr.write(`\nFAIL  ${error.stack || error}\n`);
  process.exitCode = 1;
} finally {
  terminate(cityProcess);
  if (browser) await browser.close();
  await delay(250);
  if (process.env.KEEP_GUI_FIXTURE !== "1") {
    await rm(fixture, { recursive: true, force: true });
  } else {
    process.stderr.write(`Preserved isolated fixture: ${fixture}\n`);
  }
  await rm(path.join(root, "build", "city-studio", slug), { recursive: true, force: true });
}
