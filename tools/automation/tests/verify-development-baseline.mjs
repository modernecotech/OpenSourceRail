// Exercise the real current server, selected APIs, desktop/mobile UI and fail-closed states.
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { launchBrowser } from "./browser-launch.mjs";

const root = resolve(
  process.env.OSR_ROOT || fileURLToPath(new URL("../../../", import.meta.url)),
);
const sourceRoot = resolve(process.env.OSR_SOURCE_ROOT || root);
const output = resolve(
  process.argv[2] || root + "/build/development-baseline-browser",
);
await mkdir(output, { recursive: true });
const python = process.env.OSR_PYTHON || root + "/.venv/bin/python";
const server = spawn(
  python,
  [
    "-u",
    "-m",
    "engineering.development_baseline.server",
    "--root",
    root,
    "--port",
    "0",
    "--no-browser",
  ],
  {
    cwd: sourceRoot,
    env: { ...process.env, PYTHONPATH: sourceRoot + ":" + root },
    stdio: ["ignore", "pipe", "pipe"],
  },
);
let log = "",
  origin,
  browser;
server.stdout.on("data", (chunk) => {
  log += chunk.toString();
  origin = log.match(/http:\/\/127\.0\.0\.1:\d+/)?.[0];
});
server.stderr.on("data", (chunk) => {
  log += chunk.toString();
});
const errors = [],
  mutations = [],
  external = [];
const report = {
  schema: "osr-current-workbench-browser/1",
  scope:
    "Real source-bound server and browser integration; method evidence, not physical qualification",
  physical_accepted: false,
};
try {
  const deadline = Date.now() + 30000;
  while (!origin && Date.now() < deadline) {
    if (server.exitCode !== null) throw Error("Current server exited: " + log);
    await new Promise((r) => setTimeout(r, 100));
  }
  assert(origin, "Current server did not publish an origin");
  browser = await launchBrowser();
  report.rendering = browser.osrRendering;
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1100 },
  });
  const page = await context.newPage();
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) => {
    if (!["GET", "HEAD"].includes(request.method()))
      mutations.push(request.url());
    if (
      !request.url().startsWith(origin + "/") &&
      !request.url().startsWith("data:")
    )
      external.push(request.url());
  });
  const api = await context.request.get(origin + "/api/default-design");
  assert.equal(api.status(), 200, await api.text());
  const current = await api.json();
  report.selection_id = current.selection_id;
  report.candidate_id = current.candidate_id;
  assert.equal(current.development_default, true);
  assert.equal(current.publication_state, "current");
  assert.equal(current.service.launch_speed_cap_m_s, 20);
  assert.equal(current.service.headway_s, 120);
  assert.equal(current.service.normal_capacity_pphpd_arithmetic, 8280);
  assert.equal(current.vehicle.fixed_seats_per_car, 44);
  assert.equal(current.vehicle.wheelchair_places_per_car, 2);
  assert.equal(current.vehicle.standing_passengers_per_car, 0);
  for (const key of [
    "physical_accepted",
    "engineering_accepted",
    "installed_mass_complete",
    "manufacturing_release",
    "operating_release",
  ])
    assert.equal(current[key], false);
  await page.goto(origin + "/", { waitUntil: "networkidle" });
  await page.locator("#design").waitFor({ state: "visible" });
  assert(page.url().endsWith("/docs/workbench/current/"));
  assert.equal(await page.locator("#speed").innerText(), "72");
  assert.equal(await page.locator("#headway").innerText(), "120");
  assert.equal(await page.locator("#capacity").innerText(), "8,280");
  assert.match(await page.locator("#physical").innerText(), /not established/);
  assert.match(await page.locator("#vehicle-facts").innerText(), /17\.36 t/);
  assert.match(await page.locator("#vehicle-facts").innerText(), /20\.81 t/);
  assert.match(await page.locator("#network-facts").innerText(), /906/);
  assert((await page.locator("#gates tr").count()) >= 1);
  assert.equal(await page.locator("#gates .screen.fail").count(), 2);
  assert.match(await page.locator("#gates").innerText(), /capture-energy/);
  assert.match(await page.locator("#gates").innerText(), /roof-hot-core/);
  assert.match(
    await page.locator("#city-status").innerText(),
    /selected-design analytical planning/,
  );
  assert.equal(await page.locator("#city").inputValue(), "baghdad");
  assert((await page.locator("#city option").count()) > 1);
  const cityResponse = await context.request.get(origin + "/api/city/baghdad");
  assert.equal(cityResponse.status(), 200, await cityResponse.text());
  const city = await cityResponse.json();
  assert.equal(city.selection_id, current.selection_id);
  assert.equal(city.candidate_id, current.candidate_id);
  assert.equal(city.totals.total_trainsets, 906);
  report.city_count = await page.locator("#city option").count();
  report.baghdad_trainsets = city.totals.total_trainsets;
  await page.screenshot({ path: output + "/desktop.png", fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  assert.equal(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
    true,
    "Mobile page overflows horizontally",
  );
  await page.screenshot({ path: output + "/mobile.png", fullPage: true });
  assert.match(
    await page.locator('a[href="/docs/workbench/maglev/"]').innerText(),
    /Historical/,
  );
  assert.equal(
    (
      await context.request.post(origin + "/api/default-design", {
        data: { run: true },
      })
    ).status(),
    405,
  );
  assert.equal(
    (await context.request.get(origin + "/api/hardware")).status(),
    410,
  );
  // A forged disposition or mixed candidate must hide every design result.
  for (const mutation of ["acceptance", "identity"]) {
    await page.route("**/api/default-design", async (route) => {
      const value = structuredClone(current);
      if (mutation === "acceptance") value.physical_accepted = true;
      else value.publication.body_candidate_id = "0".repeat(64);
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(value),
      });
    });
    await page.reload({ waitUntil: "networkidle" });
    assert.equal(await page.locator("#error").isVisible(), true);
    assert.equal(await page.locator("#design").isVisible(), false);
    assert.match(await page.locator("#error").innerText(), /held/);
    await page.unroute("**/api/default-design");
  }
  // Missing current data also holds, even while archived pages exist.
  await page.route("**/api/default-design", (route) =>
    route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({
        reason: "Current packet deliberately unavailable in browser fixture",
      }),
    }),
  );
  await page.reload({ waitUntil: "networkidle" });
  assert.equal(await page.locator("#design").isVisible(), false);
  assert.match(
    await page.locator("#error").innerText(),
    /no historical fallback/,
  );
  await page.screenshot({ path: output + "/held.png", fullPage: true });
  assert.deepEqual(errors, []);
  assert.deepEqual(mutations, []);
  assert.deepEqual(external, []);
  report.execution = "completed";
  report.screen = "pass";
  report.checks = [
    "current default identities",
    "72kmh/120s/8280",
    "906 Baghdad fleet",
    "current city source bindings",
    "desktop/mobile rendering",
    "read-only API",
    "forged acceptance rejection",
    "mixed identity rejection",
    "missing current packet hold",
  ];
  await context.close();
} catch (error) {
  report.execution = "failed";
  report.error = error.stack || String(error);
  throw error;
} finally {
  if (browser) await browser.close();
  server.kill("SIGTERM");
  await writeFile(output + "/server.log", log);
  await writeFile(
    output + "/result.json",
    JSON.stringify(report, null, 2) + "\n",
  );
}
console.log(JSON.stringify(report, null, 2));
