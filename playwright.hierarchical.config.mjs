import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/frontend",
  testMatch: "hierarchical-review.spec.mjs",
  outputDir: "./build/playwright/hierarchical-review/results",
  workers: 1,
  fullyParallel: false,
  retries: 0,
  timeout: 60_000,
  expect: { timeout: 15_000 },
  reporter: [
    ["line"],
    [
      "json",
      { outputFile: "build/playwright/hierarchical-review/report.json" },
    ],
  ],
  use: {
    browserName: "chromium",
    headless: true,
    locale: "en-GB",
    timezoneId: "Europe/London",
    colorScheme: "light",
    reducedMotion: "reduce",
    serviceWorkers: "block",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "repository-desktop",
      metadata: { staticRoot: "repository" },
      use: {
        baseURL: "http://127.0.0.1:4186/",
        viewport: { width: 1440, height: 1000 },
      },
    },
    {
      name: "repository-mobile",
      metadata: { staticRoot: "repository" },
      use: {
        baseURL: "http://127.0.0.1:4186/",
        viewport: { width: 390, height: 844 },
      },
    },
    {
      name: "docs-desktop",
      metadata: { staticRoot: "docs" },
      use: {
        baseURL: "http://127.0.0.1:4187/",
        viewport: { width: 1440, height: 1000 },
      },
    },
    {
      name: "docs-mobile",
      metadata: { staticRoot: "docs" },
      use: {
        baseURL: "http://127.0.0.1:4187/",
        viewport: { width: 390, height: 844 },
      },
    },
  ],
  webServer: [
    {
      command: "python3 -m http.server 4186 --bind 127.0.0.1 --directory .",
      url: "http://127.0.0.1:4186/docs/design-engine/hierarchical-pilot-2026-10-17/",
      reuseExistingServer: false,
      timeout: 30_000,
    },
    {
      command: "python3 -m http.server 4187 --bind 127.0.0.1 --directory docs",
      url: "http://127.0.0.1:4187/design-engine/hierarchical-pilot-2026-10-17/",
      reuseExistingServer: false,
      timeout: 30_000,
    },
  ],
});
