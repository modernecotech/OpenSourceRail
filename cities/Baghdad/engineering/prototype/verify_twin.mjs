import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { launchBrowser } from "../../../../tools/automation/tests/browser-launch.mjs";

// Inputs: public page, extracted offline START.html, extracted service.json.
const [publicPage, offlinePage, servicePath] = process.argv.slice(2);
assert(
  servicePath,
  "Pass public HTML, offline HTML and the offline service.json",
);
const service = JSON.parse(await readFile(servicePath, "utf8"));
const browser = await launchBrowser();
try {
  for (const file of [publicPage, offlinePage])
    for (const width of [390, 1440]) {
      const page = await browser.newPage({ viewport: { width, height: 880 } });
      const errors = [],
        external = [];
      page.on("pageerror", (e) => errors.push(String(e)));
      await page.route(/^https?:/, (r) => {
        external.push(r.request().url());
        return r.abort();
      });
      await page.goto(pathToFileURL(resolve(file)).href);
      const result = await page.evaluate((service) => {
        const check = (value, label) => {
          if (!value) throw Error(label);
        };
        const $ = (id) => document.getElementById(id);
        const choose = (id, value) => {
          const e = $(id);
          e.value = value;
          e.dispatchEvent(new Event("change"));
        };
        const setClock = (t) => {
          const e = $("clock");
          e.value = String(t);
          e.dispatchEvent(new Event("input"));
          return Object.fromEntries(
            [...$("trains").rows].map((r) => [
              r.cells[0].textContent,
              [r.cells[1].textContent, r.cells[2].textContent],
            ]),
          );
        };
        const data = JSON.parse($("model-data").textContent);
        const counts = {};
        for (const [name, parts] of Object.entries(data.geometry)) {
          choose("model", name);
          check($("piece").options.length === parts.length, name + " pieces");
          check($("datum").textContent === data.datums[name], name + " datum");
          const c = $("car");
          const image = c
            .getContext("2d")
            .getImageData(0, 0, c.width, c.height);
          check(
            image.data.some((v, i) => i % 4 === 3 && v > 0),
            name + " blank canvas",
          );
          for (const part of [parts[0], parts.at(-1)]) {
            choose("group", part.assembly);
            choose("piece", part.id);
            check($("selection").textContent === part.id, "selected piece");
            const expected =
              part.upper_m
                .map((v, k) => Math.round(1000 * (v - part.lower_m[k])))
                .join(" × ") + " mm";
            check(
              $("dimensions").textContent === expected,
              name + " dimensions",
            );
            $("detail").click();
            $("left").click();
            $("reset").click();
          }
          counts[name] = parts.length;
        }
        let tests = 0;
        for (const [id, d, dep, end] of [
          ...service.trips,
          ...service.positioning_trips,
        ]) {
          const x = setClock(dep)[id];
          check(Number(x[1]) === (d ? 12 : 0), id + " departure");
          for (const stop of service.patterns[d].slice(1, -1)) {
            const t = Math.round((stop.arrival_s + stop.departure_s) / 2) + dep;
            const km = (d ? 1 - stop.fraction : stop.fraction) * 12;
            check(
              Math.abs(Number(setClock(t)[id][1]) - km) < 0.006,
              id + " booked dwell",
            );
          }
          const leg = service.leg_profiles[d][0];
          const t = Math.floor(leg.acceleration_s / 2);
          const expected =
            leg.start_km +
            ((d ? -1 : 1) * leg.acceleration_m_s2 * t * t) / 2000;
          check(
            Math.abs(Number(setClock(dep + t)[id][1]) - expected) < 0.006,
            id + " acceleration",
          );
          const group = [...service.trips, ...service.positioning_trips]
            .filter((r) => r[0] === id && r[2] >= end)
            .sort((a, b) => a[2] - b[2]);
          if (group.length) {
            const state = setClock(Math.floor((end + group[0][2]) / 2))[id];
            check(
              state[0] === "At terminus" && Number(state[1]) === (d ? 0 : 12),
              id + " turnback",
            );
          }
          tests++;
        }
        for (const move of service.terminal.yard_moves) {
          const r = setClock(Math.floor((move.start_s + move.end_s) / 2))[
            move.train
          ];
          check(r[0].toLowerCase() === move.kind && r[1] === "—", move.kind);
        }
        let feeds = 0;
        for (const k of ["radial", "paired"]) {
          choose("power-layout", k);
          const cases = data.power[k].outages;
          check(
            $("power-isolation").options.length === cases.length,
            k + " count",
          );
          for (const r of cases) {
            choose(
              "power-isolation",
              r.failed_site === null ? "all" : String(r.failed_site),
            );
            check(
              $("power-result").textContent.includes(
                r.worst.collector_kv.toFixed(4) + " kV",
              ),
              k + " voltage",
            );
            check(
              $("power-result").textContent.includes(
                r.site_rms_ka_upper.toFixed(3) + " kA",
              ),
              k + " RMS",
            );
            feeds++;
          }
        }
        check(
          document.querySelectorAll("h1").length === 1 &&
            document.querySelectorAll("h2").length >= 5,
          "headings",
        );
        check(
          document.documentElement.scrollWidth <= window.innerWidth + 1,
          "overflow",
        );
        return { pieces: counts, trips: tests, feedStates: feeds };
      }, service);
      assert.deepEqual(external, []);
      assert.deepEqual(errors, []);
      console.log(JSON.stringify({ file, width, ...result }));
      await page.close();
    }
} finally {
  await browser.close();
}
