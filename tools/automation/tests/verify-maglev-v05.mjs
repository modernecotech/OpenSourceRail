// Browser acceptance for the static primary study; no external requests or live I/O.
import { chromium } from "@playwright/test";
import { spawn } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import assert from "node:assert/strict";

const root = resolve(import.meta.dirname, "../../..");
const output = resolve(process.argv[2] || "/tmp/osr-maglev-browser");
await mkdir(output, { recursive: true });
const server = spawn(
  "python3",
  ["-m", "http.server", "0", "--bind", "127.0.0.1", "--directory", root],
  {
    stdio: ["ignore", "pipe", "pipe"],
    env: { ...process.env, PYTHONUNBUFFERED: "1" },
  },
);
let browser;
try {
  const port = await new Promise((accept, reject) => {
    const timer = setTimeout(
      () => reject(new Error("HTTP startup timeout")),
      10000,
    );
    server.stdout.on("data", (chunk) => {
      const match = String(chunk).match(/port (\d+)/);
      if (match) {
        clearTimeout(timer);
        accept(Number(match[1]));
      }
    });
    server.once("exit", (code) => {
      clearTimeout(timer);
      reject(new Error(`HTTP exit ${code}`));
    });
  });
  browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1000 },
  });
  const errors = [],
    external = [],
    failures = [];
  page.on("pageerror", (error) => errors.push(String(error)));
  page.on("requestfailed", (req) => failures.push(req.url()));
  page.on("request", (req) => {
    if (!req.url().startsWith(`http://127.0.0.1:${port}/`))
      external.push(req.url());
  });
  const response = await page.goto(
    `http://127.0.0.1:${port}/docs/design-engine/ferrite-maglev/reference/index.html`,
  );
  assert.equal(response.status(), 200);
  await page.locator("img").last().waitFor();
  const images = await page.locator("img").evaluateAll((nodes) =>
    nodes.map((n) => ({
      src: n.getAttribute("src"),
      loaded: n.complete && n.naturalWidth > 0,
    })),
  );
  assert.equal(images.length, 2);
  assert.ok(images.every((i) => i.loaded));
  assert.match(await page.locator("h1").innerText(), /Ferrite-maglev/);
  const data = await (
    await page.request.get(
      `http://127.0.0.1:${port}/docs/design-engine/ferrite-maglev/reference/result.json`,
    )
  ).json();
  assert.equal(data.version, "0.5.0");
  assert.equal(data.design_complete, false);
  assert.equal(data.civil_section_candidates.length, 27);
  assert.equal(data.localisation.local_fraction, null);
  assert.ok(data.gates.every((g) => g.accepted === false));
  const links = [];
  for (const href of await page
    .locator("a")
    .evaluateAll((nodes) => nodes.map((n) => n.href))) {
    const linked = await page.request.get(href);
    links.push({ href: new URL(href).pathname, status: linked.status() });
    assert.equal(linked.status(), 200);
  }
  await page.screenshot({
    path: resolve(output, "primary-study-desktop.png"),
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({
    path: resolve(output, "primary-study-mobile.png"),
    fullPage: true,
  });
  assert.equal(
    await page.evaluate(
      () => document.documentElement.scrollWidth > window.innerWidth,
    ),
    false,
  );
  assert.deepEqual(errors, []);
  assert.deepEqual(external, []);
  assert.deepEqual(failures, []);
  const proof = {
    version: data.version,
    images,
    links,
    javascript_errors: errors,
    external_requests: external,
    failed_requests: failures,
    mobile_overflow: false,
    acceptance_gates_open: data.gates.length,
  };
  await writeFile(
    resolve(output, "browser-check.json"),
    JSON.stringify(proof, null, 2) + "\n",
  );
  process.stdout.write(JSON.stringify(proof, null, 2) + "\n");
} finally {
  if (browser) await browser.close();
  server.kill("SIGTERM");
}
