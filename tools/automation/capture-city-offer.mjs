#!/usr/bin/env node

import { mkdir } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { chromium } from "@playwright/test";

function argument(name, fallback = undefined) {
  const index = process.argv.indexOf(`--${name}`);
  return index === -1 ? fallback : process.argv[index + 1];
}

const city = argument("city", "baghdad");
const country = argument("country", "Iraq");
const region = argument("region", "west-asia");
const baseUrl = argument("base-url", "http://127.0.0.1:8090").replace(/\/$/, "");
const output = argument(
  "output",
  `cities/catalogue/${region}/${country}/${city[0].toUpperCase()}${city.slice(1)}/engineering/screenshots`,
);

await mkdir(output, { recursive: true });

const dataPath = `/cities/catalogue/${region}/${country}/${city[0].toUpperCase()}${city.slice(1)}`
  + `/operations/${city}-operations.json.gz`;
const query = new URLSearchParams({
  data: dataPath,
  schema_version: "1",
  city,
  environment: "simulation",
  mode: "training",
  role: "reviewer",
  actor: `${city[0].toUpperCase()}${city.slice(1)} Proposal`,
});
const url = `${baseUrl}/operations/?${query.toString()}`;

const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({
    viewport: { width: 1600, height: 1000 },
    deviceScaleFactor: 1,
  });
  await page.goto(url, { waitUntil: "networkidle", timeout: 60_000 });
  await page.getByText("Operations Portal", { exact: true }).waitFor();
  await page.getByText(city[0].toUpperCase() + city.slice(1), { exact: true }).first().waitFor();

  const captures = [
    ["Dashboard", `${city}-operations-dashboard.png`],
    ["Project Twin", `${city}-project-twin.png`],
    ["QA Gates", `${city}-qa-gates.png`],
  ];
  for (const [tab, file] of captures) {
    await page.getByText(tab, { exact: true }).first().click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: path.join(output, file), fullPage: false });
  }
} finally {
  await browser.close();
}

console.log(`Captured ${city} offer screenshots in ${output}`);
