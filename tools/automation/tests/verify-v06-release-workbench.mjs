// Check the supported Workbench surface while keeping a stale integrated
// engineering packet visibly held. The separate Journey A verifier exercises
// the full editable Samawah calculation and exports.
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdtemp, rm } from "node:fs/promises";
import { delimiter, join, resolve } from "node:path";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";
import { launchBrowser } from "./browser-launch.mjs";

const root = resolve(
  process.env.OSR_ROOT || fileURLToPath(new URL("../../../", import.meta.url)),
);
const python = process.env.OSR_PYTHON || join(root, ".venv/bin/python");
const scratch = await mkdtemp(join(tmpdir(), "osr-v06-workbench-smoke-"));
const env = {
  ...process.env,
  PYTHONPATH: [root, process.env.PYTHONPATH].filter(Boolean).join(delimiter),
  PYTHONDONTWRITEBYTECODE: "1",
};
const server = spawn(
  python,
  [
    "-u",
    "-m",
    "engineering.development_baseline.server",
    "--root",
    root,
    "--host",
    "127.0.0.1",
    "--port",
    "0",
    "--no-browser",
    "--city-study-store",
    join(scratch, "city-studies"),
    "--trip-store",
    join(scratch, "trip-studies"),
  ],
  { cwd: root, env, stdio: ["ignore", "pipe", "pipe"] },
);
let serverLog = "";
let origin;
server.stdout.on("data", (chunk) => {
  serverLog += chunk.toString();
  origin ||= serverLog.match(/http:\/\/127\.0\.0\.1:\d+/)?.[0];
});
server.stderr.on("data", (chunk) => {
  serverLog += chunk.toString();
});

let browser;
const pageErrors = [];
const externalRequests = [];
const mutations = [];
const report = { schema: "osr-v06-release-workbench-smoke/1", physical_accepted: false };
try {
  const deadline = Date.now() + 30000;
  while (!origin && Date.now() < deadline) {
    if (server.exitCode !== null) throw Error("Workbench server exited: " + serverLog);
    await new Promise((resolveDelay) => setTimeout(resolveDelay, 100));
  }
  assert(origin, "Workbench server did not publish a loopback address");

  const currentResponse = await fetch(origin + "/api/default-design");
  assert.equal(currentResponse.status, 200);
  const current = await currentResponse.json();
  assert.equal(current.development_default, true);
  assert.equal(current.family, "wheel_rail_vehicle_reference");
  assert.match(current.selection_id, /^[a-f0-9]{64}$/);
  for (const key of [
    "candidate_id",
    "body_candidate_id",
    "support_component_id",
    "propulsion_component_id",
  ]) assert.match(current[key], /^[a-f0-9]{64}$/);
  for (const key of [
    "physical_accepted",
    "engineering_accepted",
    "installed_mass_complete",
    "manufacturing_release",
    "operating_release",
  ]) assert.equal(current[key], false);
  assert(["current", "hold"].includes(current.publication_state));
  if (current.publication_state === "hold") {
    assert.equal(typeof current.hold_reason, "string");
    assert.equal(current.publication, undefined);
  }
  report.publication_state = current.publication_state;
  report.hold_reason = current.hold_reason || null;
  report.selection_id = current.selection_id;

  const catalogueResponse = await fetch(origin + "/api/cities");
  assert.equal(catalogueResponse.status, 200);
  const catalogue = await catalogueResponse.json();
  assert.equal(catalogue.schema, "osr-workbench-city-options/1");
  assert.equal(catalogue.selection_id, current.selection_id);
  assert.equal(catalogue.cities.length, 266);
  assert(catalogue.cities.some((row) => row.slug === "samawah"));
  assert.equal(catalogue.physical_accepted, false);
  report.city_count = catalogue.cities.length;

  const cityResponse = await fetch(origin + "/api/city/samawah");
  assert.equal(cityResponse.status, 503);
  const city = await cityResponse.json();
  assert.equal(city.schema, "osr-current-city-hold/1");
  assert.equal(city.selection_id, current.selection_id);
  assert.equal(city.candidate_id, current.candidate_id);
  assert.equal(city.execution, "held");
  assert.equal(city.performance_evaluated, false);
  assert.equal(city.totals, null);
  assert.equal(city.geography.city_json_sha256.length, 64);
  assert.equal(city.physical_accepted, false);

  const workbenchResponse = await fetch(origin + "/docs/workbench/current/");
  assert.equal(workbenchResponse.status, 200);
  assert.match(await workbenchResponse.text(), /id="design"/);

  browser = await launchBrowser();
  report.browser = browser.osrRendering;
  const context = await browser.newContext({ viewport: { width: 1440, height: 1100 } });
  const page = await context.newPage();
  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("request", (request) => {
    if (!new Set(["GET", "HEAD"]).has(request.method())) mutations.push(request.url());
  });
  await context.route("**/*", async (route) => {
    if (new URL(route.request().url()).origin !== origin) {
      externalRequests.push(route.request().url());
      await route.abort();
    } else {
      await route.continue();
    }
  });
  await page.goto(origin + "/", { waitUntil: "domcontentloaded" });
  await page.locator("#design").waitFor({ state: "visible", timeout: 30000 });
  assert.match(await page.locator("#identities").innerText(), new RegExp(current.selection_id));
  if (current.publication_state === "hold") {
    assert.match(await page.locator("#active-propulsion-status").innerText(), /Integrated engineering publication held/);
    assert.match(await page.locator("#vehicle-cost-status").innerText(), /Held/);
  }
  await page.locator("#city").selectOption("samawah");
  await page.waitForFunction(() =>
    document.querySelector("#city-status")?.textContent.startsWith("Outline available above."),
  );
  assert.match(await page.locator("#city-link").innerText(), /Open city planning/);
  assert.match(await page.locator("#city-details").innerText(), /city_json_sha256/);
  assert.deepEqual(pageErrors, []);
  assert.deepEqual(externalRequests, []);
  assert.deepEqual(mutations, []);
  report.page_errors = pageErrors;
  report.external_requests = externalRequests;
  report.mutations = mutations;
  report.result = "pass-for-selected-reference-and-held-city-geography";
  await context.close();
  await browser.close();
  browser = undefined;
  console.log(JSON.stringify(report, null, 2));
} catch (error) {
  report.result = "failed";
  report.error = String(error?.stack || error);
  report.server_log = serverLog;
  throw error;
} finally {
  if (browser) await browser.close();
  if (server.exitCode === null) {
    server.kill("SIGINT");
    await new Promise((resolveExit) => {
      const timer = setTimeout(resolveExit, 5000);
      server.once("exit", () => {
        clearTimeout(timer);
        resolveExit();
      });
    });
  }
  await rm(scratch, { recursive: true, force: true });
}
