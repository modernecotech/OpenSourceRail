import { expect, test } from "@playwright/test";
import { createHash } from "node:crypto";

function reviewUrl(info) {
  const base = info.project.use.baseURL || "http://127.0.0.1:4177/";
  const prefix = info.project.metadata?.staticRoot === "docs" ? "" : "docs/";
  return new URL(`${prefix}design-engine/hierarchical-pilot-2026-10-17/`, base)
    .href;
}

async function openReview(page, info) {
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  const response = await page.goto(reviewUrl(info));
  expect(response?.ok()).toBe(true);
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(
    "Hierarchical design pilot",
  );
  const evidence = await page.request.get(
    new URL("report.json", reviewUrl(info)).href,
  );
  expect(evidence.ok()).toBe(true);
  return { report: await evidence.json(), errors };
}

async function fits(page) {
  const size = await page.evaluate(() => ({
    document: document.documentElement.scrollWidth,
    viewport: innerWidth,
  }));
  expect(size.document).toBeLessThanOrEqual(size.viewport + 1);
}

test("hierarchy counts and missing capability holds come from exact report", async ({
  page,
}, info) => {
  const { report, errors } = await openReview(page, info);
  const items = report.plan.items;
  await expect(page.locator(".item")).toHaveCount(items.length);
  await expect(page.locator(".request")).toHaveCount(
    report.plan.missing_capabilities.length,
  );
  const counts = await page.locator(".metrics span").allTextContents();
  expect(Number(counts[0])).toBe(items.length);
  expect(Number(counts[1])).toBe(
    items.filter((row) => row.kind === "work-package").length,
  );
  expect(Number(counts[2])).toBe(report.plan.missing_capabilities.length);
  await expect(page.locator(".notice")).toContainText(
    "manufacturing release and physical release remain false",
  );
  for (const item of [
    page.locator(".request").first(),
    page.locator(".request").last(),
  ]) {
    await item.locator(":scope > summary").click();
    await item.locator(":scope > details > summary").click();
    await expect(item).toContainText("Next action:");
    await expect(item).toContainText("HOLD");
  }
  await fits(page);
  expect(errors).toEqual([]);
});

test("failed candidates, unknown checks and actual parent rejection remain inspectable", async ({
  page,
}, info) => {
  const { report, errors } = await openReview(page, info);
  const expected = ["mechanical", "civil"].flatMap((discipline) =>
    Object.values(report.engineering[discipline]).filter(
      (row) => row && row.id,
    ),
  );
  const articles = page.locator("article.candidate");
  await expect(articles).toHaveCount(expected.length);
  for (let i = 0; i < expected.length; i += 1) {
    const article = articles.filter({
      has: page.locator(".identity", { hasText: expected[i].id }),
    });
    await article
      .getByText("All candidate checks, including unknowns", { exact: true })
      .click();
    await expect(article.locator(".checks > li")).toHaveCount(
      expected[i].checks.length,
    );
    for (const state of ["fail", "unknown"]) {
      await expect(
        article.locator(`.checks > li[data-state=${state}]`),
      ).toHaveCount(
        expected[i].checks.filter((row) => row.state === state).length,
      );
    }
    await expect(article).toContainText("Affected parent:");
    await expect(article).toContainText("Next action:");
  }
  const adverse = page.locator("article.adverse");
  await expect(adverse).toHaveCount(report.engineering.adverse_cases.length);
  for (let i = 0; i < report.engineering.adverse_cases.length; i += 1) {
    await expect(adverse.nth(i)).toContainText(
      report.engineering.adverse_cases[i].disposition,
    );
  }
  await expect(page.locator("#bay")).toContainText("HOLD");
  await expect(page.locator("#bay")).toContainText(
    "Complete bay evaluator executed: False",
  );
  await fits(page);
  await page.screenshot({
    path: `build/playwright/hierarchical-review/${info.project.name}.png`,
  });
  expect(errors).toEqual([]);
});

test("patches, actual logs and promotion decisions have reviewable evidence", async ({
  page,
}, info) => {
  const { report, errors } = await openReview(page, info);
  const links = await page
    .locator('a[href]:not([href^="#"])')
    .evaluateAll((nodes) => [...new Set(nodes.map((node) => node.href))]);
  const receiptResponse = await page.request.get(
    new URL("receipt.json", reviewUrl(info)).href,
  );
  expect(receiptResponse.ok()).toBe(true);
  const receipt = await receiptResponse.json();
  for (const link of links) {
    const response = await page.request.get(link);
    expect(response.ok(), link).toBe(true);
    const relative = decodeURIComponent(
      new URL(link).pathname.slice(new URL(reviewUrl(info)).pathname.length),
    );
    expect(receipt.artifacts[relative], relative).toBeDefined();
    expect(
      createHash("sha256")
        .update(await response.body())
        .digest("hex"),
      link,
    ).toBe(receipt.artifacts[relative]);
  }
  for (const decision of report.promotions || []) {
    const article = page.locator("article.promotion").filter({
      has: page.getByRole("heading", {
        level: 3,
        name: decision.candidate_id,
        exact: true,
      }),
    });
    await expect(article).toContainText(decision.disposition);
    await article.locator("summary").click();
    for (const reason of decision.reasons)
      await expect(article).toContainText(reason);
  }
  await fits(page);
  expect(errors).toEqual([]);
});
