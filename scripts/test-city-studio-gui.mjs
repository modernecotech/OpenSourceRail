#!/usr/bin/env node

import { spawn } from "node:child_process";
import { createServer } from "node:net";
import { mkdir, cp, readFile, writeFile, rm } from "node:fs/promises";
import path from "node:path";
import process from "node:process";

const root = path.resolve(import.meta.dirname, "..");
const sourceProject = path.join(root, "projects", "samawah");
const runToken = `${process.pid}-${Date.now().toString(36)}`;
const slug = `samawah-e2e-${runToken}`;
const fixture = path.join(root, "projects", `.city-studio-e2e-${runToken}`);
const chromeProfile = path.join(root, "build", "gui-acceptance", `.chrome-${runToken}`);
const reportDir = path.join(root, "build", "gui-acceptance");
const reportPath = path.join(reportDir, "city-studio-gui-report.json");
const screenshotPath = path.join(reportDir, "city-studio-gui.png");
const executable = path.join(root, "target", "debug", "osr-city-studio");

const checks = [];
const startedAt = new Date();
let cityProcess;
let chromeProcess;
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

class DevTools {
  constructor(socket) {
    this.socket = socket;
    this.sequence = 0;
    this.pending = new Map();
    socket.addEventListener("message", (event) => {
      const message = JSON.parse(event.data);
      if (!message.id) return;
      const operation = this.pending.get(message.id);
      if (!operation) return;
      this.pending.delete(message.id);
      if (message.error) operation.reject(new Error(message.error.message));
      else operation.resolve(message.result);
    });
  }

  command(method, params = {}) {
    const id = ++this.sequence;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.socket.send(JSON.stringify({ id, method, params }));
    });
  }

  async evaluate(expression) {
    const result = await this.command("Runtime.evaluate", {
      expression,
      awaitPromise: true,
      returnByValue: true,
      userGesture: true,
    });
    if (result.exceptionDetails) {
      throw new Error(result.exceptionDetails.exception?.description || result.exceptionDetails.text);
    }
    return result.result.value;
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

async function startChrome(debugPort, cityUrl) {
  const chrome = spawn("google-chrome", [
    "--headless=new",
    "--no-sandbox",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    `--remote-debugging-port=${debugPort}`,
    `--user-data-dir=${chromeProfile}`,
    "--window-size=1600,1200",
    "about:blank",
  ], { cwd: root, stdio: ["ignore", "ignore", "pipe"] });
  await waitForHttp(`http://127.0.0.1:${debugPort}/json/version`);
  const target = await fetch(`http://127.0.0.1:${debugPort}/json/new?${encodeURIComponent(cityUrl)}`, {
    method: "PUT",
  }).then((response) => response.json());
  const socket = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    socket.addEventListener("open", resolve, { once: true });
    socket.addEventListener("error", reject, { once: true });
  });
  const tools = new DevTools(socket);
  await tools.command("Page.enable");
  await tools.command("Runtime.enable");
  await tools.wait("typeof view === 'object' && view?.snapshot?.stations?.length > 0", "initial project render");
  return { chrome, tools };
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
  const debugPort = await freePort();
  cityProcess = await startCityStudio(cityPort);
  const browser = await startChrome(debugPort, `http://127.0.0.1:${cityPort}/`);
  chromeProcess = browser.chrome;
  cdp = browser.tools;

  const baseline = await cdp.evaluate(`({
    stations: view.snapshot.summary.station_count,
    lines: view.snapshot.lines.length,
    services: view.service_plan.line_plans.length,
    findings: view.snapshot.findings.filter(item => item.severity === 'error').length,
  })`);
  assert(baseline.stations >= 20 && baseline.lines >= 3, "initial network rendered", `${baseline.stations} stations, ${baseline.lines} lines`);
  assert(baseline.services >= baseline.lines * 3, "line/day service plans rendered", `${baseline.services} plans`);
  assert(baseline.findings === 0, "baseline validation has no errors");

  const movedStation = await cdp.evaluate("view.snapshot.stations.find(item => item.state === 'generated').id");
  await click(`circle.station[data-id="${movedStation}"]`);
  const movedCoordinates = await cdp.evaluate("({ lat: selectedStation.lat + .00012, lon: selectedStation.lon + .00012 })");
  await form("#station-form", {
    "station-lat": movedCoordinates.lat.toFixed(7),
    "station-lon": movedCoordinates.lon.toFixed(7),
    "station-state": "preferred",
    "station-reason": "GUI acceptance movement for persistent regeneration",
  });
  await delay(600);
  const stationSaveDebug = await cdp.evaluate(`({
    toast: document.querySelector('#toast').textContent,
    state: view.snapshot.stations.find(item => item.id === ${JSON.stringify(movedStation)})?.state,
    selected: selectedStation?.id,
  })`);
  if (stationSaveDebug.state !== "preferred") {
    throw new Error(`Station form save failed: ${JSON.stringify(stationSaveDebug)}`);
  }
  await cdp.wait(`view.snapshot.stations.find(item => item.id === ${JSON.stringify(movedStation)})?.state === 'preferred'`, "station edit persistence in model");
  record("generated station moved and promoted");

  await createOnLine("station");
  const manualStation = await cdp.evaluate("selectedStation.id");
  await form("#station-form", {
    "station-name": "GUI Acceptance Station",
    "station-archetype": "major",
    "station-reason": "Interactive candidate station created by browser acceptance",
  });
  await delay(800);
  const manualStationDebug = await cdp.evaluate(`({
    station: view.snapshot.stations.find(item => item.id === ${JSON.stringify(manualStation)}),
    toast: document.querySelector('#toast').textContent,
    valid: document.querySelector('#station-form').checkValidity(),
    invalid: [...document.querySelector('#station-form').elements].filter(item => !item.checkValidity()).map(item => ({ id: item.id, value: item.value, message: item.validationMessage })),
  })`);
  if (manualStationDebug.station?.name !== "GUI Acceptance Station") {
    throw new Error(`Manual station form save failed: ${JSON.stringify(manualStationDebug)}`);
  }
  await cdp.wait(`view.snapshot.stations.find(item => item.id === ${JSON.stringify(manualStation)})?.name === 'GUI Acceptance Station'`, "manual station edit");
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
  await delay(800);
  const demandState = await cdp.evaluate(`({
    line: view.snapshot.lines.find(item => item.id === ${JSON.stringify(demandLine)}),
    toast: document.querySelector('#toast').textContent,
  })`);
  if (demandState.line?.routing_method !== "demand-aware") {
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

  await click("#compile");
  await cdp.wait("document.querySelector('#operation-result').textContent.includes('Candidate compiled')", "candidate compilation", 90_000);
  await cdp.wait("document.querySelector('#toast').textContent.includes('Candidate compiled with its content hash')", "candidate reload completion", 90_000);
  record("candidate compiled through GUI");

  const jobIds = {};
  jobIds.gis = await runAdapter("gis-export");
  jobIds.simulation = await runAdapter("simulation");
  jobIds.alignment = await runAdapter("alignment-exchange");
  jobIds.civil = await runAdapter("civil-bim", 240_000);
  await openArtifact(jobIds.gis, "gis-network");
  await openArtifact(jobIds.simulation, "simulation-result");
  await openArtifact(jobIds.alignment, "landxml");
  await openArtifact(jobIds.civil, "civil-bim-index");

  const ifcObjectCount = await cdp.evaluate("selectedArtifactPreview.content.objects.length");
  assert(ifcObjectCount > 20, "IFC object inspector populated", `${ifcObjectCount} objects`);
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
    "approval-reference": "https://github.com/OpenSourceRail/OpenSourceRail/pull/99999",
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
  await cdp.command("Page.reload", { ignoreCache: true });
  await cdp.wait("typeof view === 'object' && view?.snapshot?.stations?.length > 0", "render after server restart", 60_000);
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
  assert(persisted.jobs >= 5, "engineering job history survived restart", `${persisted.jobs} succeeded jobs`);

  await cdp.evaluate("window.confirm = () => true");
  await click(`circle.station[data-id="${manualStation}"]`);
  await click("#delete-station");
  await cdp.wait(`!view.snapshot.stations.some(item => item.id === ${JSON.stringify(manualStation)})`, "manual station retirement");
  await cdp.evaluate(`selectLine(${JSON.stringify(directLine)})`);
  await click("#delete-line");
  await cdp.wait(`!view.snapshot.lines.some(item => item.id === ${JSON.stringify(directLine)})`, "manual line retirement");
  record("manual station and line retirement persisted to intent");

  const screenshot = await cdp.command("Page.captureScreenshot", {
    format: "png",
    captureBeyondViewport: true,
  });
  await writeFile(screenshotPath, Buffer.from(screenshot.data, "base64"));
  record("browser screenshot captured", path.relative(root, screenshotPath));

  const overrides = await readFile(path.join(fixture, "network", "overrides.toml"), "utf8");
  const coordination = await readFile(path.join(fixture, "coordination", "issues.toml"), "utf8");
  const approvals = await readFile(path.join(fixture, "approvals", "reviews.toml"), "utf8");
  const services = await readFile(path.join(fixture, "services", "service-plan.toml"), "utf8");
  assert(overrides.includes(manualStation) && overrides.includes('state = "retired"'), "retirement is explicit in TOML intent");
  assert(coordination.includes(issueId) && coordination.includes('status = "in-progress"'), "coordination TOML contains saved decision");
  assert(approvals.includes(approvalId) && approvals.includes(`revision_id = "${revisionId}"`), "approval TOML references immutable revision");
  assert(services.includes(`headway_min = ${serviceState.headway}`), "service TOML contains edited headway");

  const report = {
    schema: "org.opensourcerail.city-studio-gui-acceptance.v1",
    passed: true,
    started_at: startedAt.toISOString(),
    finished_at: new Date().toISOString(),
    browser: "Google Chrome headless via DevTools Protocol",
    isolated_project: path.relative(root, fixture),
    checks,
    persistence: { movedStation, manualStation, controlId, directLine, demandLine, issueId, revisionId, approvalId },
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
  terminate(chromeProcess);
  await delay(250);
  if (process.env.KEEP_GUI_FIXTURE !== "1") {
    await rm(fixture, { recursive: true, force: true });
  } else {
    process.stderr.write(`Preserved isolated fixture: ${fixture}\n`);
  }
  await rm(chromeProfile, { recursive: true, force: true });
  await rm(path.join(root, "build", "city-studio", slug), { recursive: true, force: true });
}
