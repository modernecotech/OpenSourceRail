import assert from "node:assert/strict";
import { createServer } from "node:http";
import {
  copyFile,
  mkdir,
  mkdtemp,
  readFile,
  rm,
  writeFile,
} from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { launchBrowser } from "../../../../tools/automation/tests/browser-launch.mjs";

const directory = path.dirname(fileURLToPath(import.meta.url));
const baseline = {
  inputs: {
    headway_min: 15,
    cars: 6,
    material: "steel",
    span_m: 10,
    topology: "radial30",
    demand: "central",
    ambient_c: 32,
    grade_pct: 0,
    condition: "normal",
  },
  label: "Airport reference",
  identity: {
    physical_id: "candidate-test",
    evaluation_id: "evaluation1",
    parent_candidate_id: "airport-parent",
  },
  decision: {
    capital_usd: 1124321028,
    annual_opex_usd: 13090963,
    annual_train_km: 640000,
    minimum_voltage_v: 1350,
    peak_power_mw: 8,
    eligible: false,
    holds: ["Open thermal rating"],
  },
  engineering: {
    motion: {
      trace: [
        { time_s: 21600, source_mw: 1, trains: [{ chainage_m: 2400 }] },
        { time_s: 21900, source_mw: 8 },
      ],
      metrics: { completed_passenger_trips: 140, denied_boarding_attempts: 4 },
    },
    vehicle: { loaded_train_kg: 192000, tare_train_kg: 141000 },
  },
};
const alternative = {
  ...baseline,
  label: "Lower frequency",
  inputs: { ...baseline.inputs, headway_min: 30 },
  identity: { ...baseline.identity, evaluation_id: "evaluation2" },
  decision: {
    ...baseline.decision,
    annual_train_km: 325000,
    minimum_voltage_v: null,
  },
};
const fixture =
  "window.AIRPORT_SIMULATION = " +
  JSON.stringify({ cases: [baseline, alternative] }) +
  ";";
const run = [];
const served = new Map();
for (const filename of ["index.html", "scenario.js", "scenario.css"])
  served.set("/" + filename, await readFile(path.join(directory, filename)));
served.set("/scenario-data.js", fixture);
const types = {
  ".html": "text/html",
  ".js": "text/javascript",
  ".css": "text/css",
};
const server = createServer(async (request, response) => {
  if (request.url === "/api/airport-simulation") {
    let body = "";
    for await (const data of request) body += data;
    const submitted = JSON.parse(body);
    run.push(submitted);
    if (submitted.export) {
      response.writeHead(200, { "Content-Type": "application/zip" });
      response.end(Buffer.from([0x50, 0x4b, 0x05, 0x06, ...Array(18).fill(0)]));
    } else if (submitted.inputs.condition === "path_out") {
      response.writeHead(422, { "Content-Type": "application/json" });
      response.end(
        JSON.stringify({ error: "Path outage unavailable for this supply." }),
      );
    } else {
      response.writeHead(200, { "Content-Type": "application/json" });
      response.end(
        JSON.stringify({
          ...baseline,
          label: undefined,
          inputs: submitted.inputs,
          identity: { ...baseline.identity, evaluation_id: "evaluation-live" },
          stages: baseline.engineering,
          provenance: { solver: "<b>verifier</b>" },
        }),
      );
    }
    return;
  }
  const payload = served.get(request.url);
  response.writeHead(payload ? 200 : 404, {
    "Content-Type": types[path.extname(request.url)] || "text/plain",
  });
  response.end(payload);
});
const localRoot = path.resolve("build");
await mkdir(localRoot, { recursive: true });
const tmp = await mkdtemp(path.join(localRoot, "airport-scenario-test-"));
const errors = [];
let browser;
try {
  for (const name of ["index.html", "scenario.js", "scenario.css"])
    await copyFile(path.join(directory, name), path.join(tmp, name));
  await writeFile(path.join(tmp, "scenario-data.js"), fixture);
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  browser = await launchBrowser();
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    acceptDownloads: true,
  });
  const page = await context.newPage();
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("http://127.0.0.1:" + server.address().port + "/index.html");
  await page.getByRole("heading", { name: "Scenario decision" }).waitFor();
  await page.getByText("Open thermal rating", { exact: true }).waitFor();
  await page.getByRole("button", { name: "Add current case" }).click();
  await page.getByLabel("Saved scenarios").selectOption("1");
  await page.getByRole("button", { name: "Add current case" }).click();
  assert.equal(
    await page.getByRole("table").getByRole("columnheader").count(),
    3,
  );
  await page.getByRole("button", { name: "Engineering", exact: true }).click();
  await page
    .getByRole("heading", { name: "Power over the operating day" })
    .waitFor();
  assert(
    (await page.locator("#trace-summary").textContent()).includes(
      "Highest sampled value 8 MW",
    ),
  );
  await page.getByLabel("Trace").selectOption("distance");
  await page
    .getByRole("heading", { name: "Train positions over the operating day" })
    .waitFor();
  await page.getByLabel("Trace").selectOption("power");
  await page.getByLabel("Formation").selectOption("3");
  await page.getByRole("button", { name: "Evaluate scenario" }).click();
  await page
    .getByRole("status")
    .getByText("Scenario evaluated by the local workbench.")
    .waitFor();
  assert.equal(run[0].inputs.cars, 3);
  assert.equal(run[0].inputs.headway_min, 30);
  await page.getByRole("button", { name: "Evidence", exact: true }).click();
  await page.getByText("evaluation-live", { exact: true }).waitFor();
  await page.getByText("Machine-readable provenance").click();
  assert(
    (await page.locator("#provenance").textContent()).includes(
      "<b>verifier</b>",
    ),
  );
  assert.equal(await page.locator("#provenance b").count(), 0);
  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("button", { name: "Export dossier ZIP" }).click(),
  ]);
  assert(download.suggestedFilename().endsWith(".zip"));
  assert.equal(run[1].export, true);
  assert.deepEqual(run[0].inputs, run[1].inputs);
  await page.getByLabel("Operating condition").selectOption("path_out");
  await page.getByRole("button", { name: "Evaluate scenario" }).click();
  await page
    .getByText("Path outage unavailable for this supply.", { exact: false })
    .waitFor();
  await page.getByText("evaluation-live", { exact: true }).waitFor();

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(pathToFileURL(path.join(tmp, "index.html")).href);
  await page.getByText("Offline saved cases", { exact: true }).waitFor();
  await page.getByLabel("Headway").selectOption("20");
  await page.getByRole("button", { name: "Evaluate scenario" }).click();
  await page
    .getByText("No saved scenario matches these inputs.", { exact: false })
    .waitFor();
  await page.getByLabel("Headway").selectOption("30");
  await page.getByRole("button", { name: "Evaluate scenario" }).click();
  await page
    .getByRole("status")
    .getByText("Showing a saved scenario.")
    .waitFor();
  assert.equal(
    await page
      .locator("#decision #metrics")
      .getByText("Open", { exact: true })
      .count(),
    1,
  );
  await page.getByRole("button", { name: "Evidence", exact: true }).click();
  assert.equal(
    await page.getByRole("button", { name: "Export dossier ZIP" }).isDisabled(),
    true,
  );
  assert.equal(
    await page.evaluate(() => document.documentElement.scrollWidth),
    390,
  );
  assert.deepEqual(errors, []);
  console.log(
    "Airport scenario browser checks passed for live, saved and offline cases.",
  );
} finally {
  if (browser) await browser.close();
  if (server.listening) await new Promise((resolve) => server.close(resolve));
  await rm(tmp, { force: true, recursive: true });
}
