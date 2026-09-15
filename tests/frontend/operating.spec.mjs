import { expect, test } from "@playwright/test";

test("Workbench exposes the ERP platform with separate native module links", async ({ page }) => {
  await page.goto("http://127.0.0.1:4177/");
  await expect(page.getByRole("link", { name: "Operating · ERPNext" })).toHaveAttribute("href", "/docs/operating/");
  await page.goto("http://127.0.0.1:4177/docs/operating/");
  await expect(page.locator("#workspace")).toHaveAttribute("href", "http://127.0.0.1:8080/app/opensourcerail");
  await expect(page.locator("#modules article")).toHaveCount(6);
  await expect(page.locator(".boundary")).toContainText("does not release a train or track section");
  await page.screenshot({ path: "build/erpnext/operating.png", fullPage: true });
});

test("Operating page follows configured ERP origin and fails visibly without config", async ({ page }) => {
  await page.route("**/api/operating", route => route.fulfill({
    json: { provider: "erpnext", url: "https://erp.example.test", railway_authority: "opensource-rail" },
  }));
  await page.goto("http://127.0.0.1:4177/docs/operating/");
  await expect(page.locator("#workspace")).toHaveAttribute("href", "https://erp.example.test/app/opensourcerail");
  await expect(page.locator('a[href="https://erp.example.test/app/employee"]')).toBeVisible();
  await page.unroute("**/api/operating");
  await page.route("**/api/operating", route => route.fulfill({ status: 503, json: { error: "unconfigured" } }));
  await page.reload();
  await expect(page.locator("#workspace")).toBeHidden();
  await expect(page.locator("#connection")).toContainText("configuration is unavailable");
});

test("City feedback selects the correct project and makes stale data visible", async ({ page }) => {
  const sample = (city, project, count) => ({
    city, project, company: "Test Operator", engineering_revision: "twin-example", operating_release: "1",
    observed_at: "2020-01-01T00:00:00Z", task_count: count, task_status: { Open: count - 1, Completed: 1 },
    actual_hours: 8, task_cost: 240, currency: "USD", categories: { maintenance: { Open: count - 1, Completed: 1 } },
    asset_work: { [`${city}-asset`]: { Open: 1 } },
    readiness: { overdue: 2, undated: 3, unassigned: 4 },
    business_documents: { "Material Request": { available: true, draft: 2, submitted: 1, cancelled: 0 }, "Budget": { available: false } },
    components: {training: {available: true, states: {Scheduled: 1}}, assignment: {available: false}},
  });
  await page.route("**/api/operating/twins", route => route.fulfill({
    json: { snapshots: [sample("samawah", "PROJ-A", 12), sample("mosul", "PROJ-B", 20)] },
  }));
  await page.goto("http://127.0.0.1:4177/docs/operating/?city=mosul");
  await expect(page.locator("#twinSelector")).toHaveValue("1");
  await expect(page.locator("#twinSummary a")).toHaveAttribute("href", "http://127.0.0.1:8080/app/project/PROJ-B");
  await expect(page.locator("#twinStatus")).toContainText("more than one hour old");
  await expect(page.locator("#twinCategories")).toContainText("maintenance");
  await expect(page.locator("#twinReadiness")).toContainText("2 overdue · 3 without due dates · 4 unassigned");
  await page.locator('#businessFlow summary').click();
  await expect(page.locator('#businessFlowRows')).toContainText('Material Request');
  await expect(page.locator('#businessFlowRows')).toContainText('Unavailable');
  await page.locator('#componentsFlow summary').click();
  await expect(page.locator('#componentsFlowRows')).toContainText('Scheduled: 1');
  await page.locator("#twinSelector").selectOption("0");
  await expect(page.locator("#twinSummary a")).toHaveAttribute("href", "http://127.0.0.1:8080/app/project/PROJ-A");
  await page.unroute("**/api/operating/twins");
  await page.route("**/api/operating/twins", route => route.fulfill({ json: { snapshots: [] } }));
  await page.locator("#refreshTwins").click();
  await expect(page.locator("#twinSummary")).toBeEmpty();
  await expect(page.locator("#twinSelector")).toBeDisabled();
  await expect(page.locator('#twinReadiness')).toBeEmpty();
  await expect(page.locator('#businessFlow')).toBeHidden();
  await expect(page.locator('#componentsFlow')).toBeHidden();
});
