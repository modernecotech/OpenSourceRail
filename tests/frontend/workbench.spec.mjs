import { expect, test } from "@playwright/test";

test("Workbench carries an approved revision through simulation, OCC replay, and Ops Core", async ({ page }, testInfo) => {
  test.setTimeout(5 * 60_000);
  const browserFailures = [];
  page.on("pageerror", (error) => browserFailures.push(error.message));
  page.on("requestfailed", (request) => browserFailures.push(`${request.url()}: ${request.failure()?.errorText}`));

  await page.goto("http://127.0.0.1:4177/?module=studio&mode=design&role=designer&actor=Playwright%20Operator");
  await expect(page.locator("h1")).toHaveText("Workbench");
  await expect(page.locator("#actor")).toHaveValue("Playwright Operator");
  await expect(page.locator("#safetyBanner")).toContainText("PLANNING");

  const module = page.frameLocator("#moduleFrame");
  await expect(module.locator("#summary .summary-card").first()).toBeVisible({ timeout: 60_000 });
  await module.locator("#network-map .station").first().click();
  await expect(page.locator("#contextAsset")).not.toHaveText("none");
  const selectedAsset = await page.locator("#contextAsset").textContent();

  await module.locator("#revision").click();
  await expect(page.locator("#contextRevision")).toHaveText(/^osr-[a-f0-9]{16}$/);
  const revision = await page.locator("#contextRevision").textContent();

  await expect(module.locator("#approval-revision")).toHaveValue(revision);
  await module.locator("#approval-status").selectOption("approved");
  await module.locator("#approval-reviewer").fill("Playwright reviewer");
  await module.locator("#approval-role").fill("Owner engineer");
  await module.locator("#approval-date").fill("2030-01-02");
  await module.locator("#approval-reference").fill("test://workbench/approval");
  await module.locator("#approval-comment").fill("Deterministic Workbench acceptance approval.");
  await module.locator('#approval-form button[type="submit"]').click();
  await expect(page.locator("#contextBaseline")).toHaveText(/^[a-f0-9]{16}$/);

  await expect(module.locator("#open-simulator")).toBeVisible();
  await module.locator("#open-simulator").click();
  await expect(page.locator("#moduleFrame")).toHaveAttribute("src", /\/simulator\//);
  await expect.poll(
    () => module.locator("body").evaluate(() => window.__OSR_FRONTEND__),
    { timeout: 120_000 },
  ).toMatchObject({ app: "simulator", ready: true, error: null });
  const simulatorState = await module.locator("body").evaluate(() => window.__OSR_FRONTEND__);
  expect(simulatorState.details.embeddedTicks).toBeGreaterThan(0);
  expect(simulatorState.details.t2gTransmissions).toBeGreaterThan(0);
  expect(simulatorState.details.stationTicks).toBeGreaterThan(0);
  expect(simulatorState.details.waysideTicks).toBeGreaterThan(0);
  expect(simulatorState.details.backendSamples).toBeGreaterThan(0);
  expect(simulatorState.details.analyticsMetrics).toBeGreaterThan(0);
  expect(simulatorState.details.ptpTicks).toBeGreaterThan(0);
  expect(simulatorState.details.habdPassages).toBeGreaterThan(0);
  expect(simulatorState.details.habdWarnings).toBe(0);
  expect(simulatorState.details.habdRestrictionTicks).toBe(0);
  expect(simulatorState.details.tcmsMovementInhibits).toBe(0);
  await expect(page.locator("#contextRun")).toHaveText(/^run-[a-f0-9]{16}$/);
  const runId = await page.locator("#contextRun").textContent();

  await page.locator("#occHandoff").click();
  await expect(page.locator("#safetyBanner")).toContainText("TRAINING");
  await expect(page.locator("#moduleFrame")).toHaveAttribute("src", /\/occ\//);
  await expect.poll(
    () => module.locator("body").evaluate(() => window.__OSR_FRONTEND__),
    { timeout: 120_000 },
  ).toMatchObject({ app: "occ", ready: true, error: null });
  const occState = await module.locator("body").evaluate(() => window.__OSR_FRONTEND__);
  expect(occState.details.embeddedTicks).toBeGreaterThan(0);
  expect(occState.details.t2gTransmissions).toBeGreaterThan(0);
  expect(occState.details.stationTicks).toBeGreaterThan(0);
  expect(occState.details.waysideTicks).toBeGreaterThan(0);
  expect(occState.details.backendSamples).toBeGreaterThan(0);
  expect(occState.details.analyticsMetrics).toBeGreaterThan(0);
  expect(occState.details.ptpTicks).toBeGreaterThan(0);
  expect(occState.details.habdPassages).toBeGreaterThan(0);
  expect(occState.details.habdWarnings).toBe(0);
  expect(occState.details.habdRestrictionTicks).toBe(0);
  expect(occState.details.tcmsMovementInhibits).toBe(0);
  await expect.poll(
    () => module.locator("body").evaluate(() => window.__OSR_FRONTEND__.context.actor),
  ).toBe("Playwright Operator");
  await expect(page.locator("#contextRun")).toHaveText(runId);

  await page.locator('[data-module="operations"]').click();
  await expect(page.locator("#moduleFrame")).toHaveAttribute("src", /\/operations\//);
  await expect(module.locator("#cityName")).toHaveText("Samawah");
  await expect(module.locator("#coreStorageStatus")).toContainText("SQLite");
  await expect(module.locator("#coreAssetInput")).toHaveValue(selectedAsset);
  await module.locator("#coreTitle").fill("Inspect simulated asset handoff");
  await module.locator("#coreDueDate").fill("2030-01-03");
  await module.locator('button[form="workOrderForm"]').click();
  await expect(module.locator("#coreWorkTable")).toContainText("Inspect simulated asset handoff");

  await page.reload();
  await expect(page.locator("#contextRevision")).toHaveText(revision);
  await expect(page.locator("#contextRun")).toHaveText(runId);
  await expect(page.locator("#moduleFrame")).toHaveAttribute("src", /\/operations\//);
  await expect(module.locator("#coreWorkTable")).toContainText("Inspect simulated asset handoff");

  const persisted = await page.request.get("http://127.0.0.1:4177/api/ops-core/samawah");
  expect(persisted.ok()).toBe(true);
  const workOrders = (await persisted.json()).state.workOrders;
  const linked = workOrders.find((item) => item.title === "Inspect simulated asset handoff");
  expect(linked).toMatchObject({
    asset_id: expect.any(String),
    revision_id: revision,
    run_id: runId,
  });
  expect(linked.baseline_sha256).toMatch(/^[a-f0-9]{64}$/);

  await testInfo.attach("integrated-workbench", {
    body: await page.screenshot(),
    contentType: "image/png",
  });

  await page.locator("#role").selectOption("dispatcher");
  await page.locator("#mode").selectOption("live");
  await expect(page.locator("#safetyBanner")).toContainText("LIVE CONTROL");
  await expect(page.locator('[data-module="studio"]')).toBeDisabled();
  await expect(page.locator('[data-module="simulator"]')).toBeDisabled();
  expect(browserFailures).toEqual([]);
});

test("Workbench refuses live mode without an approved baseline", async ({ page }) => {
  await page.goto("http://127.0.0.1:4177/?module=occ&mode=live&role=dispatcher&actor=Boundary%20Test");
  await expect(page.locator("#mode")).toHaveValue("training");
  await expect(page.locator("#contextBaseline")).toHaveText("not approved");
  await expect(page.locator("#safetyBanner")).toContainText("TRAINING");
});
