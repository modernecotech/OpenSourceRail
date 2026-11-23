const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const {test} = require("node:test");
const {pathToFileURL} = require("node:url");

const read = file => fs.readFileSync(path.join(__dirname, file), "utf8");
const data = file => JSON.parse(read(file));
const context = {module: {exports: {}}};
vm.runInNewContext(read("workshop.js"), context);
const {identity, lessons, assess, replay, record} = context.module.exports;

test("training inputs match the issued Airport files and resource workload", () => {
  const fleet = data("../sourcing-estimate.json").lots.find(l => l.lot_id === "fleet");
  const factory = data("../factory-routes.json");
  for (const key of ["candidate_id", "frame_revision", "opening_evaluation_id", "estimate_evaluation_id"]) {
    assert.equal(identity[key], factory[key]);
  }
  assert.equal(identity.factory_evaluation_id, factory.evaluation_id);
  const d = factory.opening_drivers;
  const values = {
    buy: fleet.quantity * 9000000 - fleet.base_usd,
    cam: d["@cut"] - d["@saw"],
    vehicle: factory.resources.find(r => r.id === "vehicle-body-bed").required_units,
    precast: 2 * factory.resources.find(r => r.id === "civil-beam-position").required_units,
    electrical: d.grid_protection_gateways + d.section_control_gateways + d.station_dispatch_controllers,
    quality: 1298 - 1300,
    instructor: 2,
  };
  for (const l of lessons) assert.equal(l.expected, values[l.id]);
  assert.equal(replay(data("evidence-template.json")).length, 0);
});

test("each case independently checks the quantity and action, preserving unsuccessful attempts", () => {
  for (const l of lessons) {
    const wrong = (l.correct + 1) % l.actions.length;
    assert.equal(assess(l.id, l.expected + 1, l.correct).calculation_ok, false);
    assert.equal(assess(l.id, l.expected, wrong).disposition_ok, false);
    const log = record([assess(l.id, l.expected + 1, wrong), assess(l.id, l.expected, l.correct)]);
    log.attempts[0].disposition_ok = true;
    const replayed = replay(log);
    assert.equal(replayed.length, 2);
    assert.equal(replayed[0].disposition_ok, false);
    assert.equal(replayed[1].calculation_ok && replayed[1].disposition_ok, true);
  }
});

test("replay rejects changed identities, invalid scope, missing answers and unlisted actions", () => {
  const log = record([]);
  for (const key of [...Object.keys(identity), "evidence_class"]) {
    assert.throws(() => replay({...log, [key]: "stale"}));
  }
  for (const attempt of [null, {id: "other", answer: 1, action: 1}, {id: "buy", answer: "", action: 0},
    {id: "buy", answer: 1, action: 99}, {id: "buy", answer: Infinity, action: 1}]) {
    assert.throws(() => replay({...log, attempts: [attempt]}));
  }
});

test("offline browser, keyboard radios, review, download and replay", {skip: !process.env.OSR_TEST_BROWSER}, async () => {
  const {chromium} = require("playwright");
  const browser = await chromium.launch({executablePath: process.env.OSR_TEST_BROWSER, args: ["--no-sandbox"]});
  try {
    const page = await browser.newPage({viewport: {width: 360, height: 740}});
    const requests = [];
    page.on("request", r => requests.push(r.url()));
    await page.context().setOffline(true);
    await page.goto(pathToFileURL(path.join(__dirname, "index.html")).href);
    await page.getByLabel("Choose your role").selectOption("quality");
    await page.getByRole("button", {name:"Check this attempt"}).click();
    assert.equal(await page.locator("#history li").count(), 0);
    await page.getByRole("spinbutton", {name: /signed clearance margin/}).fill("-2");
    const hold = page.getByRole("radio", {name: /Hold handback/});
    await hold.focus();
    await page.keyboard.press("Space");
    await page.keyboard.press("Tab");
    assert.equal(await page.evaluate(() => document.activeElement.id || document.activeElement.type), "submit");
    await page.keyboard.press("Enter");
    await page.getByRole("status").filter({hasText:"Correct disposition"}).waitFor();
    assert.equal(await page.locator("#history li").count(), 1);
    const download = page.waitForEvent("download");
    await page.getByRole("button", {name:"Save attempts as JSON"}).click();
    const downloadPath = await (await download).path();
    const evidence = JSON.parse(fs.readFileSync(downloadPath, "utf8"));
    assert.equal(evidence.factory_evaluation_id, data("../factory-routes.json").evaluation_id);
    assert.deepEqual(evidence.attempts, [{id:"quality", answer:-2, action:0, calculation_ok:true, disposition_ok:true}]);
    assert.deepEqual(Object.keys(evidence).sort(), Object.keys(data("evidence-template.json")).sort());
    await page.reload();
    await page.getByLabel("Replay a saved attempt file").setInputFiles(downloadPath);
    await page.getByRole("status").filter({hasText:"1 attempt replayed"}).waitFor();
    assert.equal(await page.locator("#history li").count(), 1);
    const wrong = {...evidence, frame_revision: "wrong-frame"};
    await page.getByLabel("Replay a saved attempt file").setInputFiles({
      name:"stale.json", mimeType:"application/json", buffer:Buffer.from(JSON.stringify(wrong)),
    });
    await page.getByRole("status").filter({hasText:"Import failed"}).waitFor();
    assert.equal(await page.locator("#history li").count(), 1);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    assert.equal(requests.some(url => /^https?:/.test(url)), false);
  } finally {
    await browser.close();
  }
});
