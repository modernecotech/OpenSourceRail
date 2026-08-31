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

async function opsLogin(page, username, password) {
  await expect(page.locator("#loginPanel")).toBeVisible();
  await page.locator("#loginUsername").fill(username);
  await page.locator("#loginPassword").fill(password);
  await page.locator('#loginForm button[type="submit"]').click();
  await expect(page.locator("#loginPanel")).toBeHidden();
}

async function opsLogout(page) {
  await page.locator("#logoutButton").click();
  await expect(page.locator("#loginPanel")).toBeVisible();
}

for (const frontend of [
  {
    name: "simulator GUI",
    url: "http://127.0.0.1:4174/",
    canvas: "#osr_sim_canvas",
    app: "simulator",
    details: {
      invariantViolations: 0,
      tcmsMovementInhibits: 0,
      habdWarnings: 0,
      habdRestrictionTicks: 0,
      baliseAuditFindings: 0,
      fareGateDenials: 0,
      occActiveHolds: 0,
      crossingCount: 0,
    },
    positiveDetails: [
      "events", "trains", "controllerTicks", "embeddedTicks", "t2gTransmissions",
      "stationTicks", "waysideTicks",
      "backendSamples", "analyticsMetrics", "ptpTicks", "habdPassages",
      "baliseFixes",
      "fareGateGrants",
      "occReports",
      "energySiteEvaluations", "regenArbiterTicks",
      "protoFrames",
      "switchTicks",
      "selftestPasses",
    ],
  },
  {
    name: "OCC console",
    url: "http://127.0.0.1:4175/",
    canvas: "#osr_occ_canvas",
    app: "occ",
    details: {
      tcmsMovementInhibits: 0,
      habdWarnings: 0,
      habdRestrictionTicks: 0,
      baliseAuditFindings: 0,
      fareGateDenials: 0,
      occActiveHolds: 0,
      crossingCount: 0,
    },
    positiveDetails: [
      "recordedEvents", "trains", "alerts", "intrusions", "embeddedTicks", "t2gTransmissions",
      "stationTicks", "waysideTicks",
      "backendSamples", "analyticsMetrics", "ptpTicks", "habdPassages",
      "baliseFixes",
      "fareGateGrants",
      "occReports",
      "energySiteEvaluations", "regenArbiterTicks",
      "protoFrames",
      "switchTicks",
      "selftestPasses",
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

test("operations portal persists inspected and independently approved closeout", async ({ page }) => {
  const failures = capturePageFailures(page);
  const data = "/cities/catalogue/west-asia/Iraq/Samawah/operations/samawah-operations.json.gz";
  await page.goto(`http://127.0.0.1:4176/docs/operations-portal/?data=${encodeURIComponent(data)}`);
  await opsLogin(page, "planner", "Planner-pass-123!");
  await expect(page.locator("#cityName")).toHaveText("Samawah");
  await expect(page.locator("#coreStorageStatus")).toContainText("SQLite");
  await expect(page.locator("#metrics .metric")).toHaveCount(8);

  for (const tab of [
    "dashboard", "projectTwin", "core", "qa", "manufacturing", "maintenance", "assets",
    "occ", "simulator", "backoffice",
  ]) {
    await page.locator(`.tab[data-tab="${tab}"]`).click();
    await expect(page.locator(`#${tab}`)).toHaveClass(/active/);
  }

  await page.locator('.tab[data-tab="projectTwin"]').click();
  await expect(page.locator("#twinMetrics .metric")).toHaveCount(6);
  await expect(page.locator("#twinCashflowTable tr").first()).toBeVisible();
  await page.locator("#twinOrderTable [data-adopt-purchase-order]").first().click();
  await expect(page.locator("#twinOrderTable [data-adopt-purchase-order]").first()).toHaveText("Adopted");

  await page.locator('.tab[data-tab="core"]').click();
  const asset = await page.locator("#coreAssetOptions option").first().getAttribute("value");
  expect(asset).toBeTruthy();
  await page.locator("#coreAssetInput").fill(asset);
  await page.locator("#coreTitle").fill("Deterministic Playwright inspection");
  await page.locator("#coreDueDate").fill("2030-01-02");
  await page.locator('#workOrderForm button[type="submit"], button[form="workOrderForm"]').click();
  await expect(page.locator("#coreWorkTable")).toContainText("Deterministic Playwright inspection");

  await opsLogout(page);
  await opsLogin(page, "inspector", "Inspector-pass-123!");
  await page.locator('.tab[data-tab="core"]').click();
  await page.locator("#coreWorkTable tr", { hasText: "Deterministic Playwright inspection" }).locator("[data-select-wo]").click();
  await page.locator("#inspectionReading").fill("8.2 mm within acceptance band");
  await page.locator("#inspectionEvidence").fill("evidence://playwright/inspection-1");
  await page.locator("#inspectionFiles").setInputFiles({
    name: "inspection-photo.txt",
    mimeType: "text/plain",
    buffer: Buffer.from("deterministic inspection evidence\n"),
  });
  await page.locator("#inspectionNote").fill("Inspection complete and fit for handback.");
  await page.locator('button[form="inspectionForm"]').click();
  await expect(page.locator("#approvalStatus")).toContainText("Independent handback required");

  await opsLogout(page);
  await opsLogin(page, "approver", "Approver-pass-123!");
  await page.locator('.tab[data-tab="core"]').click();
  await page.locator("#coreWorkTable tr", { hasText: "Deterministic Playwright inspection" }).locator("[data-select-wo]").click();
  await page.locator("#approvalEvidence").fill("approval://playwright/handback-1");
  await page.locator("#approvalComment").fill("Latest inspection and evidence reviewed.");
  await page.locator("#approvalDeclaration").check();
  await page.locator('button[form="approvalForm"]').click();
  await expect(page.locator("#approvalStatus")).toContainText("Playwright verifier");

  const workRow = page.locator("#coreWorkTable tr", { hasText: "Deterministic Playwright inspection" });
  await workRow.locator("[data-advance-wo]").click();
  await expect(workRow).toContainText("closed");

  await opsLogout(page);
  await opsLogin(page, "controller", "Controller-pass-123!");
  await page.locator('.tab[data-tab="core"]').click();
  await page.locator("#documentId").fill("LM3-TEST-001");
  await page.locator("#documentTitle").fill("Deterministic controlled evidence");
  await page.locator("#documentRevision").fill("A");
  await page.locator("#documentFile").setInputFiles({
    name: "controlled-evidence.txt",
    mimeType: "text/plain",
    buffer: Buffer.from("controlled document revision A\n"),
  });
  await page.locator('#documentForm button[type="submit"]').click();
  await expect(page.locator("#documentTable")).toContainText("LM3-TEST-001");

  await page.reload();
  await expect(page.locator("#cityName")).toHaveText("Samawah");
  await page.locator('.tab[data-tab="core"]').click();
  const persistedRow = page.locator("#coreWorkTable tr", { hasText: "Deterministic Playwright inspection" });
  await expect(persistedRow).toContainText("closed");
  await persistedRow.locator("[data-select-wo]").click();
  await expect(page.locator("#approvalStatus")).toContainText("Playwright verifier");
  await page.locator('.tab[data-tab="projectTwin"]').click();
  await expect(page.locator("#twinOrderTable [data-adopt-purchase-order]").first()).toHaveText("Adopted");
  const saved = await page.request.get("http://127.0.0.1:4176/api/ops-core/samawah");
  expect(saved.ok()).toBeTruthy();
  const savedState = (await saved.json()).state;
  expect(savedState.approvals).toEqual(expect.arrayContaining([
    expect.objectContaining({
      decision: "approved",
      approved_by: "Playwright verifier",
      signed_by_user_id: "approver-test",
      signature: expect.objectContaining({ scheme: "HMAC-SHA256/server-attestation-v1" }),
    }),
  ]));
  expect(savedState.inspections[0]).toMatchObject({
    signed_by_user_id: "inspector-test",
    managed_evidence: [expect.objectContaining({ file_name: "inspection-photo.txt" })],
  });
  expect(savedState.documents[0]).toMatchObject({
    document_id: "LM3-TEST-001",
    revision: "A",
    signed_by_user_id: "controller-test",
  });
  expect(failures).toEqual([]);
});
