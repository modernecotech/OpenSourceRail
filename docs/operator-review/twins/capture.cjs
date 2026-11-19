// Run with the repository's Playwright and a locally installed Chrome or Chromium.
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const path = require("node:path");
const { pathToFileURL } = require("node:url");
(async () => {
  const executablePath = process.env.CHROME_PATH || "/usr/bin/google-chrome";
  const browser = await chromium.launch({
    executablePath,
    args: ["--no-sandbox", "--disable-dev-shm-usage"],
  });
  try {
    const page = await browser.newPage({
      viewport: { width: 1440, height: 870 },
      deviceScaleFactor: 1,
    });
    const errors = [];
    page.on("pageerror", (e) => errors.push(String(e)));
    for (const [model, view, file] of [
      ["core", "bogie", "core-bogie.png"],
      ["baghdad", "station", "baghdad-station.png"],
      ["baghdad", "door", "baghdad-boarding.png"],
      ["frame", "frame", "baghdad-steel-frame.png"],
    ]) {
      await page.goto(
        pathToFileURL(path.join(__dirname, "index.html")).href +
          "#model=" +
          model +
          "&view=" +
          view,
      );
      await page
        .locator(
          view === "frame"
            ? '#stock-study[aria-pressed="true"]'
            : '[data-view="' + view + '"][aria-pressed="true"]',
        )
        .waitFor();
      assert.ok((await page.locator("#occurrence option").count()) > 3);
      await page
        .locator("main")
        .screenshot({ path: path.join(__dirname, file) });
    }
    for (const model of ["core", "baghdad"]) {
      await page.locator('[data-model="' + model + '"]').click();
      for (const view of [
        "station",
        "car",
        "bogie",
        "door",
        "civil",
        "control",
      ]) {
        await page.locator('[data-view="' + view + '"]').click();
        assert.ok(await page.locator("#occurrence").inputValue());
        await page.locator("#occurrence").selectOption({ index: 1 });
        assert.ok(await page.locator("#dimensions").innerText());
        const source = await page.locator("#source").getAttribute("href");
        assert.ok(
          require("node:fs").existsSync(path.resolve(__dirname, source)),
          source,
        );
      }
    }
    assert.deepEqual(errors, []);
    console.log(
      "Twelve model/view combinations, keyboard-selectable records and source targets checked.",
    );
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
