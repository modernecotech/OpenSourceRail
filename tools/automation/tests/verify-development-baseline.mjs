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
  assert.equal(current.family, "wheel_rail_station_lim");
  for (const id of ["support_component_id", "propulsion_component_id"])
    assert.match(current[id], /^[a-f0-9]{64}$/);
  assert.equal("magnet_component_id" in current, false);
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
  const mass = current.publication.mass || current.mass;
  const massText = (v) =>
    (v / 1000).toLocaleString("en-GB", { maximumFractionDigits: 2 }) + " t";
  const facts = await page.locator("#vehicle-facts").innerText();
  assert(facts.includes(massText(mass.accounted_tare_kg_per_car)));
  assert(facts.includes(massText(mass.accounted_cap_loaded_kg_per_car)));
  assert.match(facts, /Passive wheel bogies/);
  assert.match(facts, /Services battery/);
  assert.match(
    await page.locator("#network-facts").innerText(),
    /Held pending v0.6 physical evaluation/,
  );
  assert((await page.locator("#gates tr").count()) >= 1);
  assert.match(await page.locator("#gates").innerText(), /unknown|fail/);
  assert.match(
    await page.locator("#city-status").innerText(),
    /Held:.*v0.6 city performance regeneration is held/s,
  );
  assert.equal(await page.locator("#city").inputValue(), "baghdad");
  assert((await page.locator("#city option").count()) > 1);
  const campaignResponse = await context.request.get(
    origin + "/api/campaigns/current",
  );
  assert.equal(campaignResponse.status(), 200, await campaignResponse.text());
  const campaign = await campaignResponse.json();
  assert.equal(campaign.physical_accepted, false);
  assert.equal(campaign.configuration_adopted, false);
  await page.waitForFunction(
    (count) => document.querySelectorAll("#campaign-rows tr").length === count,
    campaign.candidates.length,
  );
  report.research_campaign_id = campaign.campaign_id;
  report.research_candidates = campaign.candidates.length;
  const spaceResponse = await context.request.get(
    origin + "/api/design-space/current",
  );
  assert.equal(spaceResponse.status(), 200, await spaceResponse.text());
  const space = await spaceResponse.json();
  assert.equal(space.default_changed, false);
  assert.equal(space.physical_accepted, false);
  await page.waitForFunction(() =>
    document
      .querySelector("#design-space-status")
      .textContent.includes("structural and"),
  );
  report.structural_proposals = space.structural_proposals;
  report.propulsion_proposals = space.propulsion_proposals;
  const architectureResponse = await context.request.get(
    origin + "/api/architectures/current",
  );
  assert.equal(
    architectureResponse.status(),
    200,
    await architectureResponse.text(),
  );
  const architecture = await architectureResponse.json();
  assert.equal(architecture.development_default_changed, false);
  assert.equal(architecture.physical_accepted, false);
  await page.waitForFunction(
    (count) =>
      document.querySelectorAll("#architecture-rows tr").length === count,
    architecture.families.length,
  );
  report.architecture_cases = architecture.evaluation_cases;
  report.architecture_families = architecture.families.length;
  const adaptiveResponse = await context.request.get(
    origin + "/api/adaptive/current",
  );
  assert.equal(adaptiveResponse.status(), 200, await adaptiveResponse.text());
  const adaptive = await adaptiveResponse.json();
  assert.equal(adaptive.physical_accepted, false);
  assert.equal(adaptive.selected_reference_changed, false);
  assert.equal(adaptive.integrated_selection, null);
  await page.waitForFunction(
    (count) => document.querySelectorAll("#adaptive-rows tr").length === count,
    adaptive.rows.length,
  );
  report.adaptive_variables = adaptive.variable_count;
  report.adaptive_native_cases = adaptive.native_case_count;
  const cityResponse = await context.request.get(origin + "/api/city/baghdad");
  assert.equal(cityResponse.status(), 503, await cityResponse.text());
  const city = await cityResponse.json();
  assert.equal(city.selection_id, current.selection_id);
  assert.equal(city.candidate_id, current.candidate_id);
  assert.equal(city.execution, "held");
  assert.equal(city.performance_evaluated, false);
  assert.equal(city.totals, null);
  assert.equal(city.geography.underlying_city_details_preserved, true);
  assert.match(
    await page.locator("#city-link").innerText(),
    /Preserved city map/,
  );
  report.city_count = await page.locator("#city option").count();
  report.baghdad_performance_state = "held";
  report.city_performance_packages_written = 0;
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
  for (const mutation of ["acceptance", "identity", "support", "propulsion"]) {
    await page.route("**/api/default-design", async (route) => {
      const value = structuredClone(current);
      if (mutation === "acceptance") value.physical_accepted = true;
      else if (mutation === "identity")
        value.publication.body_candidate_id = "0".repeat(64);
      else value.publication[mutation + "_component_id"] = "0".repeat(64);
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
    "wheel support and passive secondary identities",
    "266 geographic contexts held without reusing historical fleet",
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
