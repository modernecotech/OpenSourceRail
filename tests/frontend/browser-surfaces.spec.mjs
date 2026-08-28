import { expect, test } from "@playwright/test";

function capturePageFailures(page) {
  const failures = [];
  page.on("pageerror", (error) => failures.push(`pageerror: ${error.message}`));
  page.on("console", (message) => {
    if (message.type() === "error") failures.push(`console: ${message.text()}`);
  });
  page.on("requestfailed", (request) => {
    failures.push(`request: ${request.url()} — ${request.failure()?.errorText || "failed"}`);
  });
  return failures;
}

for (const frontend of [
  {
    name: "simulator GUI",
    url: "http://127.0.0.1:4174/",
    canvas: "#osr_sim_canvas",
    app: "simulator",
    details: { invariantViolations: 0 },
    positiveDetails: [
      "events", "trains", "controllerTicks", "embeddedTicks", "t2gTransmissions",
      "stationTicks", "waysideTicks",
    ],
  },
  {
    name: "OCC console",
    url: "http://127.0.0.1:4175/",
    canvas: "#osr_occ_canvas",
    app: "occ",
    details: {},
    positiveDetails: [
      "recordedEvents", "trains", "alerts", "intrusions", "embeddedTicks", "t2gTransmissions",
      "stationTicks", "waysideTicks",
    ],
  },
]) {
  test(`${frontend.name} boots its production WASM bundle`, async ({ page }, testInfo) => {
    const failures = capturePageFailures(page);
    await page.goto(frontend.url, { waitUntil: "domcontentloaded" });
    await expect.poll(
      () => page.evaluate(() => window.__OSR_FRONTEND__),
      { timeout: 120_000 },
    ).toMatchObject({ app: frontend.app, ready: true, error: null });
    const state = await page.evaluate(() => window.__OSR_FRONTEND__);
    expect(state.details).toMatchObject(frontend.details);
    for (const field of frontend.positiveDetails) {
      expect(state.details[field], `${frontend.name} ${field}`).toBeGreaterThan(0);
    }
    await expect(page.locator("#loading")).toBeHidden();
    const canvas = page.locator(frontend.canvas);
    await expect(canvas).toBeVisible();
    const box = await canvas.boundingBox();
    expect(box?.width).toBeGreaterThan(1000);
    expect(box?.height).toBeGreaterThan(700);
    await canvas.click({ position: { x: 80, y: 80 } });
    await page.waitForTimeout(250);
    expect(failures).toEqual([]);
    await testInfo.attach(`${frontend.app}-canvas`, {
      body: await page.screenshot(),
      contentType: "image/png",
    });
  });
}

test("operations portal loads every tab and persists an Ops Core work order", async ({ page }) => {
  const failures = capturePageFailures(page);
  const data = "/designs/west-asia/Iraq/Samawah/operations/samawah-operations.json.gz";
  await page.goto(`http://127.0.0.1:4176/docs/operations-portal/?data=${encodeURIComponent(data)}`);
  await expect(page.locator("#cityName")).toHaveText("Samawah");
  await expect(page.locator("#coreStorageStatus")).toContainText("SQLite");
  await expect(page.locator("#metrics .metric")).toHaveCount(8);

  for (const tab of [
    "dashboard", "core", "qa", "manufacturing", "maintenance", "assets",
    "occ", "simulator", "backoffice",
  ]) {
    await page.locator(`.tab[data-tab="${tab}"]`).click();
    await expect(page.locator(`#${tab}`)).toHaveClass(/active/);
  }

  await page.locator('.tab[data-tab="core"]').click();
  const asset = await page.locator("#coreAssetOptions option").first().getAttribute("value");
  expect(asset).toBeTruthy();
  await page.locator("#coreAssetInput").fill(asset);
  await page.locator("#coreTitle").fill("Deterministic Playwright inspection");
  await page.locator("#coreDueDate").fill("2030-01-02");
  await page.locator('#workOrderForm button[type="submit"], button[form="workOrderForm"]').click();
  await expect(page.locator("#coreWorkTable")).toContainText("Deterministic Playwright inspection");

  await page.reload();
  await expect(page.locator("#cityName")).toHaveText("Samawah");
  await page.locator('.tab[data-tab="core"]').click();
  await expect(page.locator("#coreWorkTable")).toContainText("Deterministic Playwright inspection");
  expect(failures).toEqual([]);
});
