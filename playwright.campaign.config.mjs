import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/frontend",
  testMatch: "campaign-review.spec.mjs",
  outputDir: "./build/playwright/campaign-review/results",
  workers: 1,
  fullyParallel: false,
  retries: 0,
  timeout: 60_000,
  expect: { timeout: 15_000 },
  reporter: [
    ["line"],
    ["json", { outputFile: "build/playwright/campaign-review/report.json" }],
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
        baseURL: "http://127.0.0.1:4181/",
        viewport: { width: 1440, height: 1000 },
      },
    },
    {
      name: "repository-mobile",
      metadata: { staticRoot: "repository" },
      use: {
        baseURL: "http://127.0.0.1:4181/",
        viewport: { width: 390, height: 844 },
      },
    },
    {
      name: "docs-desktop",
      metadata: { staticRoot: "docs" },
      use: {
        baseURL: "http://127.0.0.1:4182/",
        viewport: { width: 1440, height: 1000 },
      },
    },
    {
      name: "docs-mobile",
      metadata: { staticRoot: "docs" },
      use: {
        baseURL: "http://127.0.0.1:4182/",
        viewport: { width: 390, height: 844 },
      },
    },
  ],
  webServer: [
    {
      command: "python3 -m http.server 4181 --bind 127.0.0.1 --directory .",
      url: "http://127.0.0.1:4181/docs/design-engine/campaign-review/",
      reuseExistingServer: false,
      timeout: 30_000,
    },
    {
      command: "python3 -m http.server 4182 --bind 127.0.0.1 --directory docs",
      url: "http://127.0.0.1:4182/design-engine/campaign-review/",
      reuseExistingServer: false,
      timeout: 30_000,
    },
  ],
});
