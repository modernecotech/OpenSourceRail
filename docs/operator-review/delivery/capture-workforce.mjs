import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";
import { chromium } from "playwright";

const folder = new URL("./", import.meta.url);
const input = JSON.parse(await readFile(new URL("quantities.json", folder), "utf8"));
const htmlFile = new URL("index.html", folder);
const dataFile = new URL("workforce-data.js", folder);
const current = "// Generated from quantities.json by capture-workforce.mjs\nconst workforceStudy = " +
                JSON.stringify(input, null, 2) + ";\n";
if (process.argv.includes("--refresh")) await writeFile(dataFile, current);
else assert.equal(await readFile(dataFile, "utf8"), current, "Refresh the local study data with --refresh");
const workbenchOrigin = process.argv.find(arg => arg.startsWith("--workbench-origin="))?.split("=")[1];
if (workbenchOrigin) assert.equal(new URL(workbenchOrigin).hostname, "127.0.0.1");

const browser = await chromium.launch({ executablePath: process.env.OSR_BROWSER_EXECUTABLE || chromium.executablePath(),
                                       headless: true });
try {
  const context = await browser.newContext({ offline: !workbenchOrigin, viewport: {width: 1440, height: 970},
                                             deviceScaleFactor: 1, locale: "en-US" });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", error => errors.push(error.message));
  const violations = [];
  page.on("console", message => {
    if (/content security policy/i.test(message.text())) violations.push(message.text());
  });
  const url = workbenchOrigin ? new URL("/docs/operator-review/delivery/index.html", workbenchOrigin) : htmlFile;
  const response = await page.goto(url.href);
  if (workbenchOrigin) {
    assert.equal(response.status(), 200);
    assert.match(response.headers()["content-security-policy"], /script-src 'self'/);
    assert.match(response.headers()["content-security-policy"], /style-src 'self'/);
  }
  assert.equal(await page.locator("header").evaluate(node => getComputedStyle(node).backgroundColor), "rgb(21, 62, 61)");
  for (const key of ["core", "metropolitan", "first"]) {
    await page.selectOption("#railway", key);
    for (const mode of ["supervised", "assisted", "goa4"]) {
      await page.selectOption("#mode", mode);
      const expected = input.studies[key].workforce_scenarios[mode].total_fte.toLocaleString("en-US");
      assert.equal(await page.locator("#establishment").textContent(), expected);
    }
    assert.equal(await page.locator("#revised-cost").textContent(), "Pending");
    assert.equal(await page.locator("#transfer").getAttribute("href"), null);
  }
  assert.equal(await page.locator("#pay").textContent(), "Unpriced");
  await page.fill("#hours", "0");
  assert.equal(await page.locator("#establishment").textContent(), "—");
  await page.fill("#hours", "1600");
  const hours = Object.values(input.studies.first.workforce_scenarios.goa4.duty_hours_per_year);
  const revised = hours.reduce((total, h) => total + Math.ceil(h / 1600), 0);
  assert.equal(await page.locator("#establishment").textContent(), revised.toLocaleString("en-US"));
  await page.fill("#hours", "1720");
  await page.fill("#salary", "24000");
  assert.equal(await page.locator("#pay").textContent(), "$36,624,000");
  assert.equal(await page.locator("#instructors").textContent(), "10,240");
  assert.equal(await page.locator("#mentored").textContent(), "122,080");
  const stationPay = page.getByLabel("station duty and passenger assistance loaded annual pay in USD");
  await stationPay.fill("25000");
  assert.equal(await page.locator("#pay").textContent(), "$37,358,000");
  await page.selectOption("#mode", "assisted");
  assert.equal(await stationPay.inputValue(), "25000");
  await stationPay.fill("");
  await page.selectOption("#mode", "goa4");
  const included = name => page.getByLabel(name + " embedded annual payroll in USD millions", {exact:true});
  await included("Station operations").fill("25");
  await included("Non-energy train operations").fill("12");
  assert.equal(await page.locator("#revised-cost").textContent(), "Pending");
  await included("Power maintenance").fill("6");
  assert.equal(await page.locator("#revised-cost").textContent(), "Pending");
  await included("Power maintenance").fill("0");
  assert.equal(await page.locator("#revised-cost").textContent(), "$196.602m");
  await page.selectOption("#mode", "supervised");
  assert.equal(await page.locator("#transfer").getAttribute("href"), null);
  assert.match(await page.locator("#cost-status").textContent(), /actual period/);
  await page.selectOption("#mode", "goa4");
  const transfer = new URL(await page.locator("#transfer").evaluate(node => node.href));
  assert.equal(transfer.searchParams.get("network"), "first");
  const expected = input.studies.first.opex.baseline_usd_m_year - 37 + 36.624;
  assert.ok(Math.abs(Number(transfer.searchParams.get("opex")) - expected) < 1e-9);
  await page.selectOption("#railway", "core");
  assert.equal(await page.locator("#revised-cost").textContent(), "Pending");
  assert.equal(await page.locator("#transfer").getAttribute("href"), null);
  await page.selectOption("#railway", "first");
  await included("Station operations").fill("25");
  await included("Non-energy train operations").fill("12");
  await included("Power maintenance").fill("0");
  await page.locator("#cost-status").click();
  await page.screenshot({path:fileURLToPath(new URL("workforce.png",folder)),fullPage:true});
  await page.locator("#transfer").click();
  assert.equal(await page.locator("#network").inputValue(), "first");
  assert.equal(await page.locator("#opex").textContent(), "$196.6m");
  await page.locator("#restore-budget").click();
  assert.equal(await page.locator("#opex").textContent(), "$197.0m");
  assert.deepEqual(errors, []);
  assert.deepEqual(violations, []);
  console.log(browser.version(), input.study_evaluation_sha256, url.protocol, "roster, payroll, OPEX and finance handover verified");
} finally {
  await browser.close();
}
