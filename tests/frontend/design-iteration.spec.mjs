import { expect, test } from "@playwright/test";

function reviewUrl(info) {
  // The full frontend suite already owns the Workbench server on 4177.
  // This test's dedicated matrix supplies either repository or docs roots.
  const base = info.project.use.baseURL || "http://127.0.0.1:4177/";
  const prefix = info.project.metadata?.staticRoot === "docs" ? "" : "docs/";
  return new URL(`${prefix}design-engine/generative-detail-2026-10-17/`, base)
    .href;
}

async function openReview(page, info) {
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  const response = await page.goto(reviewUrl(info));
  expect(response?.ok()).toBe(true);
  await expect(
    page.getByRole("heading", {
      level: 1,
      name: "Generative civil and mechanical design team",
    }),
  ).toBeVisible();
  return errors;
}

async function withinViewport(page) {
  const layout = await page.evaluate(() => ({
    documentWidth: document.documentElement.scrollWidth,
    viewportWidth: innerWidth,
  }));
  expect(layout.documentWidth).toBeLessThanOrEqual(layout.viewportWidth + 1);
}

test("all six contexts and 63 open packages preserve partial design scope", async ({
  page,
}, info) => {
  const errors = await openReview(page, info);
  const articles = page.locator("main > article");
  await expect(articles).toHaveCount(6);
  const headings = await articles.locator("h3").allTextContents();
  expect(headings.filter((text) => text.startsWith("mechanical"))).toHaveLength(
    2,
  );
  expect(headings.filter((text) => text.startsWith("civil"))).toHaveLength(4);
  expect(headings.some((text) => text.includes("LM3"))).toBe(true);
  expect(headings.some((text) => text.includes("metro-6car-planning"))).toBe(
    true,
  );
  await expect(page.locator("main > .notice")).toContainText(
    "All 63 packages remain open",
  );
  await expect(page.locator("main > .notice")).toContainText(
    "An unsolved design is retained as unsolved",
  );
  const rows = page.locator("main > .scroll > table tbody tr");
  await expect(rows).toHaveCount(63);
  const identifiers = await rows.locator("td:first-child").allTextContents();
  for (const identifier of [
    "BASIS-CONFIGURATION",
    "CIV-FRP-100",
    "LM3-FRP-010",
    "SYSTEM-ASSURANCE",
  ]) {
    expect(identifiers.some((text) => text.startsWith(identifier))).toBe(true);
  }
  for (const row of await rows.all()) {
    await expect(row.locator("td").nth(2)).toContainText(
      /provisional-detail-investigated|awaiting-qualified-detail-adapter-and-inputs/,
    );
  }
  await expect(page.locator("main")).toContainText(
    "coverage is not completion",
  );
  await expect(page.locator("main")).toContainText("partial detail response");
  await expect(page.locator("main")).toContainText("distinct controlled IDs");
  const civilAllocation = rows
    .filter({
      has: page.locator("td:first-child", { hasText: "CIV-FRP-100" }),
    })
    .getByText("Assigned controlled catalogue IDs", { exact: true });
  await civilAllocation.click();
  await expect(civilAllocation.locator("..").locator("pre")).toContainText(
    "OSR-TYPE-",
  );
  await expect(page.locator("main")).toContainText("472");
  await expect(page.locator("main")).toContainText("416");
  await expect(page.locator("main")).toContainText(
    "0 issued drawing references",
  );
  await expect(rows.first()).toContainText("Proposed research subassembly IDs");
  await expect(page.locator("main > .notice")).toContainText(
    "manufacturing acceptance",
  );
  await expect(rows.first()).toContainText("assigned inventory IDs");
  await withinViewport(page);
  await info.attach("generative-detail-review", {
    body: await page.screenshot(),
    contentType: "image/png",
  });
  expect(errors).toEqual([]);
});

test("failed attempts and unknown qualification remain inspectable with definitions", async ({
  page,
}, info) => {
  const errors = await openReview(page, info);
  const articles = page.locator("main > article");
  for (const article of await articles.all()) {
    await expect(article).toContainText(
      "qualified independent engineering review remains required",
    );
    const definition = article.locator(":scope > details").first();
    await definition.locator("summary").click();
    await expect(definition).toBeVisible();
    await expect(definition).toContainText("unknown");
    for (const field of [
      '"geometry"',
      '"materials"',
      '"connections"',
      '"manufacturing"',
      '"next_actions"',
    ]) {
      await expect(definition.locator("pre")).toContainText(field);
    }
    const variations = article.locator(":scope > details").nth(1);
    await variations.locator("summary").click();
    await expect(variations.locator("table")).toBeVisible();
    expect(await variations.locator("tbody tr").count()).toBeGreaterThan(0);
  }
  // The initial mechanical design fails actual numerical checks and remains in
  // the retained attempt table even if a later candidate passes known checks.
  const firstMechanical = articles
    .filter({
      has: page.locator("h3", { hasText: "mechanical" }),
    })
    .first();
  const initialAttempt = firstMechanical.locator("tbody tr").first();
  await expect(initialAttempt).toContainText("Generation 0");
  await expect(initialAttempt.locator("td").nth(2)).toContainText(
    "global_service_deflection",
  );
  await expect(page.locator("#coupling + ul")).toContainText(
    "Net mass change unknown",
  );
  await expect(page.locator("main")).toContainText(
    "Native geometry verification does not establish",
  );
  await withinViewport(page);
  expect(errors).toEqual([]);
});

test("all six fresh native model pairs download from repository and docs roots", async ({
  page,
  request,
}, info) => {
  const errors = await openReview(page, info);
  const fcstd = page.getByRole("link", {
    name: "FreeCAD assembly",
    exact: true,
  });
  const steps = page.getByRole("link", { name: "STEP assembly", exact: true });
  await expect(fcstd).toHaveCount(6);
  await expect(steps).toHaveCount(6);
  const seen = new Set();
  for (const link of [...(await fcstd.all()), ...(await steps.all())]) {
    const href = await link.getAttribute("href");
    const url = new URL(href, page.url());
    expect(url.origin).toBe(new URL(page.url()).origin);
    expect(seen.has(url.href)).toBe(false);
    seen.add(url.href);
    const response = await request.get(url.href);
    expect(response.status()).toBe(200);
    expect((await response.body()).byteLength).toBeGreaterThan(100);
    await response.dispose();
  }
  for (const article of await page.locator("main > article").all()) {
    await expect(article).toContainText("Native status: passed");
  }
  await withinViewport(page);
  expect(errors).toEqual([]);
});
