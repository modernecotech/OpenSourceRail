import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/frontend",
  outputDir: "./build/playwright/results",
  workers: 1,
  fullyParallel: false,
  retries: 0,
  timeout: 120_000,
  expect: { timeout: 15_000 },
  reporter: [
    ["line"],
    ["json", { outputFile: "build/playwright/report.json" }],
    ["html", { outputFolder: "build/playwright/html", open: "never" }],
  ],
  use: {
    browserName: "chromium",
    headless: true,
    viewport: { width: 1440, height: 1000 },
    locale: "en-GB",
    timezoneId: "Europe/London",
    colorScheme: "dark",
    reducedMotion: "reduce",
    serviceWorkers: "block",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "off",
  },
  webServer: [
    {
      command: "python3 -m http.server 4174 --bind 127.0.0.1 --directory build/frontend/sim",
      url: "http://127.0.0.1:4174/",
      reuseExistingServer: false,
      timeout: 30_000,
    },
    {
      command: "python3 -m http.server 4175 --bind 127.0.0.1 --directory build/frontend/occ",
      url: "http://127.0.0.1:4175/",
      reuseExistingServer: false,
      timeout: 30_000,
    },
    {
      command: "python3 tools/automation/ops-core-server.py --host 127.0.0.1 --port 4176 --db build/playwright/ops-core.sqlite3 --reset-db",
      url: "http://127.0.0.1:4176/docs/operations-portal/",
      reuseExistingServer: false,
      timeout: 30_000,
    },
    {
      command: "exec python3 tools/automation/workbench-server.py --host 127.0.0.1 --port 4177 --city-port 4178 --db build/playwright/workbench.sqlite3 --reset-db --isolated-project cities/workspaces/samawah",
      url: "http://127.0.0.1:4177/",
      reuseExistingServer: false,
      timeout: 60_000,
    },
  ],
});
