// Browser acceptance for the static primary study; no external requests or live I/O.
import { chromium } from "@playwright/test";
import { spawn } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { gunzipSync } from "node:zlib";
import { createHash } from "node:crypto";
import assert from "node:assert/strict";

const root = resolve(import.meta.dirname, "../../..");
const output = resolve(process.argv[2] || "/tmp/osr-maglev-browser");
await mkdir(output, { recursive: true });
const server = spawn(
  "python3",
  ["-m", "http.server", "0", "--bind", "127.0.0.1", "--directory", root],
  {
    stdio: ["ignore", "pipe", "pipe"],
    env: { ...process.env, PYTHONUNBUFFERED: "1" },
  },
);
let browser;
try {
  const port = await new Promise((accept, reject) => {
    const timer = setTimeout(
      () => reject(new Error("HTTP startup timeout")),
      10000,
    );
    server.stdout.on("data", (chunk) => {
      const match = String(chunk).match(/port (\d+)/);
      if (match) {
        clearTimeout(timer);
        accept(Number(match[1]));
      }
    });
    server.once("exit", (code) => {
      clearTimeout(timer);
      reject(new Error(`HTTP exit ${code}`));
    });
  });
  browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1000 },
  });
  const errors = [],
    external = [],
    failures = [];
  page.on("pageerror", (error) => errors.push(String(error)));
  page.on("requestfailed", (req) => failures.push(req.url()));
  page.on("request", (req) => {
    if (!req.url().startsWith(`http://127.0.0.1:${port}/`))
      external.push(req.url());
  });
  const response = await page.goto(
    `http://127.0.0.1:${port}/docs/design-engine/ferrite-maglev/reference/index.html`,
  );
  assert.equal(response.status(), 200);
  await page.locator("img").last().waitFor();
  await page.waitForFunction(() =>
    [...document.images].every((image) => image.complete),
  );
  const images = await page.locator("img").evaluateAll((nodes) =>
    nodes.map((n) => ({
      src: n.getAttribute("src"),
      loaded: n.complete && n.naturalWidth > 0,
    })),
  );
  const expectedImages = [
    "guidebeam-sections.svg",
    "duty-energy.svg",
    "../native/interface/overview.png",
    "../native/interface/cartridge-detail.png",
    "../native/civil-bay/overview.png",
    "field-study.png",
    "../beam-only/overview.png",
    "evacuation-envelope.svg",
  ];
  assert.deepEqual(
    images.map((image) => image.src).sort(),
    expectedImages.sort(),
  );
  assert.equal(images.length, 8);
  assert.ok(images.every((i) => i.loaded));
  assert.match(await page.locator("h1").innerText(), /Ferrite-maglev/);
  const origin = `http://127.0.0.1:${port}`;
  const report = `${origin}/docs/design-engine/ferrite-maglev/reference/`;
  const assets = new Map();
  async function asset(relative) {
    const url = new URL(relative, report);
    assert.equal(url.origin, origin, "report assets must stay local");
    if (!assets.has(url.href)) {
      const linked = await page.request.get(url.href);
      assert.equal(
        linked.status(),
        200,
        `missing report asset: ${url.pathname}`,
      );
      assets.set(url.href, {
        pathname: url.pathname,
        status: linked.status(),
        contentType: linked.headers()["content-type"],
        body: await linked.body(),
      });
    }
    return assets.get(url.href);
  }
  async function jsonAsset(relative) {
    return JSON.parse((await asset(relative)).body.toString("utf8"));
  }
  const data = await jsonAsset("result.json");
  assert.equal(data.version, "0.5.0");
  for (const flag of [
    "design_complete",
    "physical_validation",
    "manufacturing_release",
    "physical_release",
  ])
    assert.equal(data[flag], false);
  assert.equal(data.civil_section_candidates.length, 27);
  assert.equal(data.localisation.local_fraction, null);
  assert.ok(data.gates.every((g) => g.accepted === false));
  assert.equal(data.transition_inventory.total_source_items, 414);
  assert.equal(data.transition_inventory.legacy_work_packages, 63);
  assert.equal(data.requirements.length, 72);
  assert.equal(data.work_packages.length, 11);
  assert.equal(data.city_catalogue.city_count, 266);
  assert.equal(data.city_catalogue.catalogue_complete, true);
  assert.equal(data.city_catalogue.planning_acceptance, false);
  const optimisation = data.whole_system_optimisation;
  assert.equal(optimisation.candidate_count, 432);
  assert.ok(optimisation.numerical_screen_pass_count > 0);
  assert.equal(optimisation.acceptance_eligible_candidate_count, 0);
  assert.equal(optimisation.design_complete, false);
  assert.equal(optimisation.local_value_added_fraction, null);
  assert.ok(optimisation.unchanged_scope_floor_usd_dual_km > 0);
  assert.equal(optimisation.fully_coupled_optimisation, false);
  assert.equal(
    optimisation.research_extrema.fastest_construction_candidate_id,
    null,
  );
  assert.ok(
    optimisation.research_extrema.lowest_counted_concrete_mass_candidate_id,
  );
  const score =
    optimisation.minimum_indexed_allowance_candidate.system_scorecard;
  assert.equal(score.installed_cost_usd_dual_route_km, null);
  assert.equal(score.factory_gate_cost_usd_three_car_train, null);
  assert.equal(score.moving_assemblies_count, null);
  assert.ok(score.hot_aw3_no_regen_cycle_kwh_per_car > 0);
  assert.equal(
    optimisation.beam_only_minimum_gross_allowance_candidate.system_scorecard
      .hot_aw3_no_regen_cycle_kwh_per_car,
    null,
  );
  assert.match(
    await page.locator("body").innerText(),
    /Whole-system comparison scorecards/,
  );
  assert.equal(optimisation.beam_only_candidate_count, 432);
  assert.equal(optimisation.beam_only_reference_champion_eligible, false);
  assert.equal(optimisation.beam_only_net_system_saving_usd, null);
  assert.equal(data.onboard_evacuation.beam_only_part_count, 54);
  assert.equal(data.onboard_evacuation.walkway_removal_approved, false);
  assert.equal(
    data.onboard_evacuation.operational_deployment_authorised,
    false,
  );
  const beamOnlyManifest = await jsonAsset("../beam-only/manifest.json");
  assert.equal(beamOnlyManifest.evacuation_accepted, false);
  assert.equal(beamOnlyManifest.walkway_removal_approved, false);
  assert.equal(beamOnlyManifest.manufacturing_release, false);
  const beamImage = await asset("../beam-only/overview.png");
  assert.equal(
    createHash("sha256").update(beamImage.body).digest("hex"),
    beamOnlyManifest.files_sha256["overview.png"],
  );
  const evacuation = JSON.parse(
    gunzipSync((await asset("evacuation-study.json.gz")).body).toString("utf8"),
  );
  assert.match(evacuation.preferred_candidate, /vertical-controlled-descent/);
  assert.deepEqual(
    evacuation.chute_envelopes.map((e) => e.height_m),
    [8, 12, 20, 30],
  );
  assert.equal(evacuation.chute_operating_height_approved_m, null);
  assert.equal(evacuation.chute_descent_simulation_performed, false);
  assert.equal(evacuation.onboard_installation_requirements.length, 7);
  assert.ok(
    evacuation.onboard_installation_requirements.every(
      (r) => !r.accepted && r.state === "open",
    ),
  );
  assert.equal(
    evacuation.variable_height_research.discrete_exit_counterexample.state,
    "rejected",
  );
  assert.equal(
    evacuation.variable_height_research.continuous_height_coverage_proved,
    false,
  );
  assert.equal(
    evacuation.chute_supplier_comparison[0]
      .installed_transport_reference_verified,
    false,
  );
  assert.ok(
    evacuation.chute_supplier_comparison.every(
      (s) => s.railway_accepted === false,
    ),
  );
  assert.ok(
    evacuation.chute_landing_cases
      .filter((c) => c.surface !== "controlled-safe-dry-ground")
      .every((c) => c.state === "rejected"),
  );
  assert.equal(
    evacuation.chute_outward_extended_standoff_path.assessment.state,
    "hold",
  );
  assert.equal(evacuation.procurement_and_lifetime_cost_usd, null);
  assert.equal(evacuation.net_system_saving_usd, null);
  assert.ok(
    evacuation.landing_cases
      .filter((c) => c.surface !== "controlled-safe-dry-ground")
      .every((c) => c.state === "rejected"),
  );
  assert.ok(evacuation.landing_cases.every((c) => c.accepted === false));

  const transition = JSON.parse(
    gunzipSync((await asset("transition-register.json.gz")).body).toString(
      "utf8",
    ),
  );
  assert.equal(transition.items.length, 414);
  assert.equal(new Set(transition.items.map((item) => item.id)).size, 414);
  assert.equal(transition.legacy_packages.length, 63);
  assert.equal(transition.accepted_item_count, 0);
  assert.equal(transition.accepted_physical_release_count, 0);
  assert.ok(
    transition.items.every((item) => !item.accepted && !item.physical_release),
  );

  const nativeManifest = await jsonAsset("../native/manifest.json");
  assert.equal(nativeManifest.schema, "osr-maglev-native-packet/1");
  assert.equal(nativeManifest.physical_release, false);
  assert.equal(nativeManifest.manufacturing_release, false);
  const nativeReceipts = [];
  for (const name of ["interface", "civil-bay"]) {
    const receipt = await jsonAsset(`../native/${name}/native-cad.json`);
    assert.equal(receipt.schema, "osr-factory-native-cad/1");
    assert.equal(receipt.fcstd_reopened, true);
    assert.equal(receipt.step_reopened, true);
    assert.equal(receipt.physical_release, false);
    assert.match(receipt.input_sha256, /^[a-f0-9]{64}$/);
    if (name === "interface") assert.equal(receipt.part_count, 624);
    else assert.ok(receipt.part_count > 0);
    nativeReceipts.push({
      name,
      part_count: receipt.part_count,
      reopened: true,
    });
  }
  const coupledReceipt = await jsonAsset("../coupled/receipt.json");
  const coupledAsset = await asset("../coupled/result.json");
  const coupled = JSON.parse(coupledAsset.body.toString("utf8"));
  assert.equal(coupledReceipt.schema, "osr-coupled-guideway-publication/1");
  assert.equal(coupled.schema, "osr-coupled-guideway-result/1");
  assert.deepEqual(coupled.source_sha256, coupledReceipt.source_sha256);
  assert.deepEqual(coupled.execution, coupledReceipt.execution);
  assert.match(coupledReceipt.execution.bridge_sha256, /^[a-f0-9]{64}$/);
  assert.ok(coupledReceipt.execution.build_command.includes("coupled_bridge"));
  assert.equal(
    createHash("sha256").update(coupledAsset.body).digest("hex"),
    coupledReceipt.files_sha256["result.json"],
  );
  assert.equal(coupled.coupled_replay.virtual_duration_s, 3);
  assert.equal(coupled.coupled_replay.retained_vertical_beam_modes, 6);
  assert.equal(coupled.coupled_replay.beam_assumptions.elements, 50);
  assert.equal(
    coupled.coupled_replay.status,
    "hypothetical-two-way-offline-cosimulation",
  );
  for (const record of [coupledReceipt, coupled, coupled.coupled_replay]) {
    assert.equal(record.physical_output_authorised, false);
    assert.equal(record.structural_acceptance, false);
  }
  const links = [];
  for (const href of await page
    .locator("a")
    .evaluateAll((nodes) => nodes.map((n) => n.href))) {
    const linked = await asset(href);
    links.push({ href: linked.pathname, status: linked.status });
  }
  const expectedVideos = [
    "../native/interface/assembly-visibility.mp4",
    "../native/civil-bay/assembly-visibility.mp4",
  ];
  const videoLinks = await page
    .locator('a[href$=".mp4"]')
    .evaluateAll((nodes) => nodes.map((node) => node.getAttribute("href")));
  assert.deepEqual(videoLinks.sort(), expectedVideos.sort());
  const videos = [];
  for (const href of videoLinks) {
    const video = await asset(href);
    assert.match(video.contentType, /^video\/mp4(?:;|$)/);
    assert.ok(
      video.body.length > 1024,
      "assembly video must contain media bytes",
    );
    assert.equal(video.body.subarray(4, 8).toString("ascii"), "ftyp");
    const name = href.replace("../native/", "");
    assert.equal(
      createHash("sha256").update(video.body).digest("hex"),
      nativeManifest.files_sha256[name],
    );
    videos.push({
      href: video.pathname,
      status: video.status,
      bytes: video.body.length,
    });
  }
  for (const image of images) {
    const loaded = await asset(image.src);
    assert.ok(loaded.body.length > 0);
    if (image.src.startsWith("../native/")) {
      const name = image.src.replace("../native/", "");
      assert.equal(
        createHash("sha256").update(loaded.body).digest("hex"),
        nativeManifest.files_sha256[name],
      );
    }
  }
  await page.screenshot({
    path: resolve(output, "primary-study-desktop.png"),
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({
    path: resolve(output, "primary-study-mobile.png"),
    fullPage: true,
  });
  assert.equal(
    await page.evaluate(
      () => document.documentElement.scrollWidth > window.innerWidth,
    ),
    false,
  );
  assert.deepEqual(errors, []);
  assert.deepEqual(external, []);
  assert.deepEqual(failures, []);
  const proof = {
    version: data.version,
    images,
    videos,
    links,
    source_item_count: transition.items.length,
    legacy_package_count: transition.legacy_packages.length,
    city_count: data.city_catalogue.city_count,
    accepted_item_count: transition.accepted_item_count,
    native_receipts: nativeReceipts,
    coupled_receipt: {
      schema: coupledReceipt.schema,
      bridge_sha256: coupledReceipt.execution.bridge_sha256,
      virtual_duration_s: coupled.coupled_replay.virtual_duration_s,
      physical_output_authorised: false,
      structural_acceptance: false,
    },
    javascript_errors: errors,
    external_requests: external,
    failed_requests: failures,
    mobile_overflow: false,
    acceptance_gates_open: data.gates.length,
  };
  await writeFile(
    resolve(output, "browser-check.json"),
    JSON.stringify(proof, null, 2) + "\n",
  );
  process.stdout.write(JSON.stringify(proof, null, 2) + "\n");
} finally {
  if (browser) await browser.close();
  server.kill("SIGTERM");
}
