import { execFile } from "node:child_process";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { promisify } from "node:util";
import { expect, test } from "@playwright/test";

const execFileAsync = promisify(execFile);
const root = path.resolve(import.meta.dirname, "../..");
const childEnv = { ...process.env, PLAYWRIGHT_CHANNEL: "" };
delete childEnv.FORCE_COLOR;
delete childEnv.NO_COLOR;

test("City Studio passes its isolated edit, adapter, restart, and persistence acceptance", async () => {
  test.setTimeout(15 * 60_000);
  const { stdout, stderr } = await execFileAsync(
    process.execPath,
    ["scripts/test-city-studio-gui.mjs"],
    {
      cwd: root,
      env: childEnv,
      maxBuffer: 8 * 1024 * 1024,
      timeout: 14 * 60_000,
    },
  );
  expect(stderr).toBe("");
  expect(stdout).toContain("GUI acceptance checks passed");
  const report = JSON.parse(
    await readFile(path.join(root, "build/gui-acceptance/city-studio-gui-report.json"), "utf8"),
  );
  expect(report.passed).toBe(true);
  expect(report.browser).toBe("Playwright Chromium");
  expect(report.checks).toHaveLength(111);
  expect(report.checks.every((check) => check.passed)).toBe(true);
});
