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
    assert.equal(await page.locator("#establishment").textContent(),
                 input.studies[key].roster.total_fte.toLocaleString("en-US"));
  }
  assert.equal(await page.locator("#pay").textContent(), "Unpriced");
  await page.fill("#hours", "0");
  assert.equal(await page.locator("#establishment").textContent(), "—");
  await page.fill("#hours", "1600");
  const hours = Object.values(input.studies.first.roster.duty_hours_per_year);
  const revised = hours.reduce((total, h) => total + Math.ceil(h / 1600), 0);
  assert.equal(await page.locator("#establishment").textContent(), revised.toLocaleString("en-US"));
  await page.fill("#hours", "1720");
  await page.fill("#salary", "24000");
  assert.equal(await page.locator("#pay").textContent(), "$46,800,000");
  assert.equal(await page.locator("#instructors").textContent(), "13,040");
  assert.equal(await page.locator("#mentored").textContent(), "156,000");
  assert.deepEqual(errors, []);
  assert.deepEqual(violations, []);
  await page.screenshot({path:fileURLToPath(new URL("workforce.png",folder)),fullPage:true});
  console.log(browser.version(), input.study_evaluation_sha256, url.protocol, "roster, salary and training verified");
} finally {
  await browser.close();
}
