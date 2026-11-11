// Exercise the actual Samawah form, bounded worker, cache, exports and replay.
import assert from "node:assert/strict";
import { execFileSync, spawn, spawnSync } from "node:child_process";
import {
  lstat,
  mkdir,
  readdir,
  rename,
  rm,
  stat,
  statfs,
  writeFile,
} from "node:fs/promises";
import { delimiter, join, resolve } from "node:path";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";
import { launchBrowser } from "./browser-launch.mjs";

const root = resolve(
  process.env.OSR_ROOT || fileURLToPath(new URL("../../../", import.meta.url)),
);
const output = resolve(
  process.argv[2] || join(tmpdir(), "osr-v06-samawah-journey-a"),
);
assert.notEqual(
  output,
  root,
  "Journey evidence must stay outside the source checkout",
);
assert(
  !output.startsWith(root + "/"),
  "Journey evidence must stay outside the source checkout",
);
await mkdir(output, { recursive: true });
assert(
  !(await lstat(output)).isSymbolicLink(),
  "Output directory must not be a symbolic link",
);
const outputEntries = await readdir(output);
assert.equal(
  outputEntries.length,
  0,
  "Use a new or empty output directory; existing evidence is preserved",
);

const store = join(output, ".city-study-store");
const tripStore = join(output, ".trip-study-store");
const evidence = join(output, "journey-a");
const python =
  process.env.OSR_PYTHON ||
  (process.platform === "win32" ? "python" : join(root, ".venv/bin/python"));
const env = {
  ...process.env,
  PYTHONPATH: [root, process.env.PYTHONPATH].filter(Boolean).join(delimiter),
  PYTHONDONTWRITEBYTECODE: "1",
};
const sourceStatusBefore = execFileSync(
  "git",
  ["status", "--porcelain", "--untracked-files=all"],
  { cwd: root, encoding: "utf8" },
).trim();
assert.equal(
  sourceStatusBefore,
  "",
  "Journey evidence must be produced from a clean source checkout",
);
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
    store,
    "--trip-store",
    tripStore,
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
const report = {
  schema: "osr-v06-software-journey-a/1",
  journey:
    "Editable Samawah mapped city, same-input warm reuse, changed-input identity, source-bound cost and delivery export",
  source_commit: execFileSync("git", ["rev-parse", "HEAD"], {
    cwd: root,
    encoding: "utf8",
  }).trim(),
  physical_accepted: false,
  engineering_accepted: false,
  manufacturing_release: false,
  movement_authority: false,
  operating_release: false,
};
let browser;
let serverStopped = false;
const pageErrors = [];
const externalRequests = [];
const mutations = [];
const submissions = [];
let peakStoreAllocatedBytes = 0;
let allocationObserver;

function freeBytes(path) {
  const fs = statfs(path, { bigint: true });
  return fs.then((value) => Number(value.bavail * value.bsize));
}

async function allocatedBytes(path) {
  let total = 0;
  for (const entry of await readdir(path, { withFileTypes: true })) {
    const item = join(path, entry.name);
    if (entry.isDirectory()) total += await allocatedBytes(item);
    else if (entry.isFile()) {
      const metadata = await stat(item, { bigint: true });
      total += Number(metadata.blocks * 512n);
    }
  }
  return total;
}

async function apiJson(context, pathname) {
  const response = await context.request.get(origin + pathname);
  assert.equal(response.status(), 200, `${pathname}: ${await response.text()}`);
  return response.json();
}

async function submit(page, expectedHeadway, timeout = 150000) {
  const status = page.locator("#city-study-status");
  await page
    .locator('#city-study-options input[name="maximum_headway_s"]')
    .fill(String(expectedHeadway));
  const responsePromise = page.waitForResponse(
    (response) =>
      response.request().method() === "POST" &&
      new URL(response.url()).pathname === "/api/city-studies",
  );
  const start = Date.now();
  await page.locator("#city-study-start").click();
  const response = await responsePromise;
  assert([200, 202].includes(response.status()), await response.text());
  const submitted = await response.json();
  submissions.push(submitted);
  await page
    .locator("#city-study-result")
    .waitFor({ state: "visible", timeout });
  await page.waitForFunction(
    (value) => {
      const text =
        document.querySelector("#city-study-status")?.textContent || "";
      return text.startsWith(
        value === "warm"
          ? "Reused the identical verified calculation"
          : "Calculation complete",
      );
    },
    submitted.cache_hit ? "warm" : "cold",
    { timeout },
  );
  assert.equal(await page.locator(".atlas-cost-table tbody tr").count(), 14);
  return {
    submitted,
    ui_status: await status.innerText(),
    browser_wall_seconds: (Date.now() - start) / 1000,
  };
}

async function stopServer() {
  if (serverStopped || server.exitCode !== null) return;
  serverStopped = true;
  const exited = new Promise((resolveExit) => server.once("exit", resolveExit));
  server.kill("SIGINT");
  let timeout;
  const timer = new Promise((resolveExit) => {
    timeout = setTimeout(() => resolveExit("timeout"), 10000);
  });
  const outcome = await Promise.race([exited, timer]);
  clearTimeout(timeout);
  if (outcome === "timeout") server.kill("SIGKILL");
}

try {
  const startDeadline = Date.now() + 30000;
  while (!origin && Date.now() < startDeadline) {
    if (server.exitCode !== null)
      throw Error("Workbench server exited before readiness: " + serverLog);
    await new Promise((resolveDelay) => setTimeout(resolveDelay, 100));
  }
  assert(
    origin,
    "Workbench server did not publish a loopback address: " + serverLog,
  );
  const freeBefore = await freeBytes(output);
  assert(
    freeBefore >= 4 * 1024 ** 3,
    "The journey requires the configured 4 GiB output reserve",
  );
  peakStoreAllocatedBytes = await allocatedBytes(store);
  allocationObserver = setInterval(() => {
    void allocatedBytes(store)
      .then((size) => {
        peakStoreAllocatedBytes = Math.max(peakStoreAllocatedBytes, size);
      })
      .catch(() => {});
  }, 250);
  browser = await launchBrowser();
  report.browser = browser.osrRendering;
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1100 },
  });
  await context.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.origin !== origin) {
      externalRequests.push(url.href);
      await route.abort();
    } else if (url.pathname === "/api/portfolios/current") {
      // The 112-candidate library is unrelated to this single-city journey.
      await route.abort();
    } else {
      await route.continue();
    }
  });
  const page = await context.newPage();
  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("request", (request) => {
    if (!new Set(["GET", "HEAD"]).has(request.method()))
      mutations.push(request.url());
  });
  const firstRenderStarted = Date.now();
  await page.goto(origin + "/", { waitUntil: "domcontentloaded" });
  await page.locator("#design").waitFor({ state: "visible", timeout: 30000 });
  report.workbench_first_render_seconds =
    (Date.now() - firstRenderStarted) / 1000;

  await page.locator("#city-outline-load").click();
  await page
    .locator("#city-outline-select option[value='samawah']")
    .waitFor({ state: "attached", timeout: 120000 });
  await page.locator("#city-outline-select").selectOption("samawah");
  await page
    .locator(".atlas-cost-table tbody tr")
    .nth(13)
    .waitFor({ state: "attached", timeout: 120000 });
  assert.equal(await page.locator(".atlas-cost-table tbody tr").count(), 14);
  const baseline = await apiJson(context, "/api/city-atlas/samawah");
  assert.equal(baseline.schema, "osr-city-atlas/1");
  report.city = baseline.city;
  report.published_outline_evaluation_id =
    baseline.identity.outline_evaluation_id;
  report.baseline_packet_id = baseline.packet_id;
  assert(
    baseline.lines.length > 0,
    "The published Samawah network must contain mapped lines",
  );

  const cold = await submit(page, 120);
  assert.equal(cold.submitted.state, "running");
  assert.equal(cold.submitted.cache_hit, false);
  assert.equal(cold.submitted.resource_admission.admitted, true);
  assert.equal(cold.submitted.resource_admission.root, store);
  assert(
    cold.submitted.resource_admission.filesystem_free_bytes >= 4 * 1024 ** 3,
  );
  assert.equal(cold.submitted.resource_budget.minimum_free_reserve_gib, 4);
  assert.equal(
    cold.submitted.resource_budget.maximum_output_bytes,
    64 * 1024 * 1024,
  );
  assert.equal(cold.submitted.resource_budget.native_solver_jobs, 0);
  const coldId = cold.submitted.job_id;
  const coldFinal = await apiJson(context, `/api/city-studies/${coldId}`);
  assert.equal(coldFinal.state, "completed");
  const coldSummary = await apiJson(
    context,
    `/api/city-studies/${coldId}/artifacts/summary.json`,
  );
  const coldManifest = await apiJson(
    context,
    `/api/city-studies/${coldId}/artifacts/manifest.json`,
  );
  const coldResult = await apiJson(
    context,
    `/api/city-studies/${coldId}/artifacts/result.json`,
  );
  const coldPerformance = await apiJson(
    context,
    `/api/city-studies/${coldId}/artifacts/performance.json`,
  );
  const coldDelivery = await apiJson(
    context,
    `/api/city-studies/${coldId}/artifacts/delivery-plan.json`,
  );
  const coldBusiness = await apiJson(
    context,
    `/api/city-studies/${coldId}/artifacts/business-drafts.json`,
  );
  assert.equal(coldSummary.calculation_complete, true);
  assert.equal(
    coldSummary.source_outline_evaluation_id,
    report.published_outline_evaluation_id,
  );
  assert.equal(Object.keys(coldSummary.scope_totals_usd).length, 14);
  assert.equal(coldResult.request.service.maximum_headway_s, 120);
  assert.equal(
    Object.keys(coldResult.city_outline.cost.scope_totals_usd).length,
    14,
  );
  assert.equal(
    coldDelivery.city_record_evaluation_id,
    coldResult.city_outline.evaluation_id,
  );
  assert.equal(coldBusiness.source_plan_id, coldDelivery.plan_id);
  assert.equal(coldManifest.evaluation_id, coldSummary.evaluation_id);
  assert.equal(coldManifest.manifest_id, coldFinal.manifest_id);
  assert(coldPerformance.elapsed_s > 0 && coldPerformance.cpu_s >= 0);
  assert(coldPerformance.worker_elapsed_s >= coldPerformance.elapsed_s);
  assert(coldPerformance.worker_cpu_s >= coldPerformance.cpu_s);
  assert.equal(coldPerformance.native_solver_jobs, 0);
  assert(coldPerformance.peak_rss_bytes > 0);
  assert(coldPerformance.artifact_payload_bytes > 0);
  assert(coldFinal.summary.service_lines.length > 0);
  const coldPacket = await apiJson(context, `/api/city-atlas/study/${coldId}`);
  assert.equal(
    coldPacket.identity.workflow_evaluation_id,
    coldSummary.evaluation_id,
  );
  assert.equal(
    coldPacket.identity.research_configuration_id,
    coldSummary.research_configuration_id,
  );
  report.cold = {
    job_id: coldId,
    manifest_id: coldManifest.manifest_id,
    evaluation_id: coldSummary.evaluation_id,
    request_headway_s: 120,
    browser_wall_seconds: cold.browser_wall_seconds,
    evaluation_wall_seconds: coldPerformance.elapsed_s,
    evaluation_cpu_seconds: coldPerformance.cpu_s,
    worker_wall_seconds: coldPerformance.worker_elapsed_s,
    worker_cpu_seconds: coldPerformance.worker_cpu_s,
    peak_rss_bytes: coldPerformance.peak_rss_bytes,
    artifact_payload_bytes: coldPerformance.artifact_payload_bytes,
    preflight: cold.submitted.resource_admission,
    budget: cold.submitted.resource_budget,
    cost_scope_count: Object.keys(coldSummary.scope_totals_usd).length,
    service_line_count: coldSummary.service_lines.length,
    delivery_plan_id: coldDelivery.plan_id,
    physical_accepted: coldSummary.physical_accepted,
  };
  assert.equal(coldSummary.physical_accepted, false);
  for (const label of [
    "City calculation summary",
    "Complete calculated result",
    "Production and construction schedule",
    "Disabled business-system drafts",
    "Sources and artifact identities",
  ]) {
    assert(
      (await page.locator("#city-study-links").innerText()).includes(label),
      `Missing export link: ${label}`,
    );
  }

  const warm = await submit(page, 120);
  assert.equal(warm.submitted.cache_hit, true);
  assert.equal(warm.submitted.job_id, coldId);
  assert.equal(warm.submitted.manifest_id, coldManifest.manifest_id);
  assert.equal(warm.submitted.summary.evaluation_id, coldSummary.evaluation_id);
  report.warm = {
    job_id: warm.submitted.job_id,
    cache_hit: warm.submitted.cache_hit,
    evaluation_id: warm.submitted.summary.evaluation_id,
    browser_wall_seconds: warm.browser_wall_seconds,
    ui_status: warm.ui_status,
  };

  await page
    .locator('#city-study-options input[name="peak_demand_pphpd"]')
    .fill("9000");
  const changed = await submit(page, 120);
  assert.equal(changed.submitted.cache_hit, false);
  assert.equal(changed.submitted.resource_admission.admitted, true);
  assert.notEqual(changed.submitted.job_id, coldId);
  const changedId = changed.submitted.job_id;
  const changedSummary = await apiJson(
    context,
    `/api/city-studies/${changedId}/artifacts/summary.json`,
  );
  const changedManifest = await apiJson(
    context,
    `/api/city-studies/${changedId}/artifacts/manifest.json`,
  );
  const changedResult = await apiJson(
    context,
    `/api/city-studies/${changedId}/artifacts/result.json`,
  );
  const changedPacket = await apiJson(
    context,
    `/api/city-atlas/study/${changedId}`,
  );
  assert.equal(changedResult.request.service.maximum_headway_s, 120);
  assert.equal(changedResult.request.service.peak_demand_pphpd, 9000);
  assert.notEqual(changedSummary.evaluation_id, coldSummary.evaluation_id);
  assert.notEqual(changedManifest.manifest_id, coldManifest.manifest_id);
  assert(
    changedSummary.trainsets !== coldSummary.trainsets ||
      Object.entries(changedSummary.scope_totals_usd).some(([scope, cases]) =>
        Object.keys(cases).some(
          (caseName) =>
            cases[caseName] !== coldSummary.scope_totals_usd[scope][caseName],
        ),
      ),
    "The changed demand case must expose a fleet or cost effect",
  );
  assert.equal(
    changedPacket.identity.workflow_evaluation_id,
    changedSummary.evaluation_id,
  );
  report.changed = {
    job_id: changedId,
    manifest_id: changedManifest.manifest_id,
    evaluation_id: changedSummary.evaluation_id,
    request_headway_s: 120,
    request_peak_demand_pphpd: 9000,
    trainsets: changedSummary.trainsets,
    distinct_from_cold:
      changedSummary.evaluation_id !== coldSummary.evaluation_id,
    cost_scope_count: Object.keys(changedSummary.scope_totals_usd).length,
    changed_cost_scopes: Object.entries(changedSummary.scope_totals_usd)
      .filter(([scope, cases]) =>
        Object.keys(cases).some(
          (caseName) =>
            cases[caseName] !== coldSummary.scope_totals_usd[scope][caseName],
        ),
      )
      .map(([scope]) => scope),
    scope_totals_usd: changedSummary.scope_totals_usd,
    whole_life_npv_delta_usd: Object.fromEntries(
      Object.entries(changedResult.city_outline.cost.whole_life_npv_usd).map(
        ([caseName, amount]) => [
          caseName,
          amount - coldResult.city_outline.cost.whole_life_npv_usd[caseName],
        ],
      ),
    ),
    physical_accepted: changedSummary.physical_accepted,
  };
  report.city_study_posts = submissions.length;
  report.external_requests = externalRequests;
  report.mutations = mutations;
  report.page_errors = pageErrors;
  assert.equal(submissions.length, 3);
  assert.equal(externalRequests.length, 0);
  assert.equal(
    mutations.length,
    3,
    "Only the three typed local city-study POSTs are permitted",
  );
  assert.equal(pageErrors.length, 0, pageErrors.join("; "));
  assert(page.url().endsWith("/docs/workbench/current/"));
  await new Promise((resolveDelay) => setTimeout(resolveDelay, 300));
  clearInterval(allocationObserver);
  allocationObserver = undefined;
  peakStoreAllocatedBytes = Math.max(
    peakStoreAllocatedBytes,
    await allocatedBytes(store),
  );
  await page.screenshot({
    path: join(output, "journey-a-desktop.png"),
    fullPage: true,
  });

  await mkdir(evidence, { recursive: false });
  for (const [id, name] of [
    [coldId, "cold"],
    [changedId, "changed"],
  ]) {
    await mkdir(join(evidence, name), { recursive: false });
    await rename(
      join(store, id, "artifacts"),
      join(evidence, name, "artifacts"),
    );
  }
  const artifactBytes = {};
  for (const name of ["cold", "changed"]) {
    artifactBytes[name] = await allocatedBytes(
      join(evidence, name, "artifacts"),
    );
    assert(
      artifactBytes[name] <= 64 * 1024 * 1024,
      `${name} artifacts exceed the 64 MiB output budget`,
    );
  }
  await browser.close();
  browser = undefined;
  await stopServer();

  const replayCode =
    "import json,sys; from engineering.outline import city_workflow; m=city_workflow.verify(sys.argv[1],root=sys.argv[2],replay=sys.argv[3]=='true'); print(json.dumps({'manifest_id':m['manifest_id'],'evaluation_id':m['evaluation_id'],'replay':sys.argv[3]=='true'}))";
  const replay = spawnSync(
    python,
    ["-c", replayCode, join(evidence, "cold/artifacts"), root, "true"],
    {
      cwd: root,
      env,
      encoding: "utf8",
      timeout: 180000,
      maxBuffer: 2 * 1024 * 1024,
    },
  );
  assert.equal(replay.status, 0, replay.stderr || replay.stdout);
  report.independent_replay = JSON.parse(
    replay.stdout.trim().split("\n").at(-1),
  );
  assert.equal(report.independent_replay.manifest_id, coldManifest.manifest_id);
  const changedCheck = spawnSync(
    python,
    ["-c", replayCode, join(evidence, "changed/artifacts"), root, "false"],
    {
      cwd: root,
      env,
      encoding: "utf8",
      timeout: 60000,
      maxBuffer: 2 * 1024 * 1024,
    },
  );
  assert.equal(
    changedCheck.status,
    0,
    changedCheck.stderr || changedCheck.stdout,
  );
  report.changed_artifact_verification = JSON.parse(
    changedCheck.stdout.trim().split("\n").at(-1),
  );
  assert.deepEqual(await readdir(tripStore), [".service.lock"]);
  await rm(store, { recursive: true, force: false });
  await rm(tripStore, { recursive: true, force: false });
  const sourceStatusAfter = execFileSync(
    "git",
    ["status", "--porcelain", "--untracked-files=all"],
    { cwd: root, encoding: "utf8" },
  ).trim();
  assert.equal(
    sourceStatusAfter,
    "",
    "Journey must leave no tracked or visible untracked files in the source checkout",
  );
  const freeAfter = await freeBytes(output);
  report.storage = {
    output_filesystem_free_before_bytes: freeBefore,
    output_filesystem_free_after_bytes: freeAfter,
    peak_worker_store_allocated_bytes: peakStoreAllocatedBytes,
    preserved_verified_artifact_allocated_bytes: await allocatedBytes(evidence),
    verified_job_artifact_allocated_bytes: artifactBytes,
    worker_store_removed_after_independent_verification: true,
    trip_service_store_removed_after_shutdown: true,
    source_checkout_generated_files: sourceStatusAfter
      ? sourceStatusAfter.split("\n")
      : [],
  };
  report.software_journey_result = "pass-for-Journey-A-only";
  await writeFile(
    join(output, "journey-a.json"),
    JSON.stringify(report, null, 2) + "\n",
  );
  console.log(JSON.stringify(report, null, 2));
} catch (error) {
  report.software_journey_result = "failed";
  report.error = String(error?.stack || error);
  report.server_log = serverLog;
  await writeFile(
    join(output, "journey-a-failure.json"),
    JSON.stringify(report, null, 2) + "\n",
  );
  throw error;
} finally {
  if (allocationObserver) clearInterval(allocationObserver);
  if (browser) await browser.close();
  await stopServer();
}
