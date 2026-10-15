import { test, expect } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";

const origin = process.env.OSR_GUIDED_TEST_URL || "http://127.0.0.1:4177";

test("actual generated cleat definition reaches the schematic inspector without installed or CAD credit", async ({
  page,
}) => {
  const identity = {
    schema: "osr-design-identity/1",
    city: "samawah",
    project: "generated-inspector-fixture",
    environment: "simulation",
    configuration_revision: "fixture-r1",
    baseline_sha256: "b".repeat(64),
    run_id: null,
    asset_id: null,
    part_id: null,
  };
  const root = fileURLToPath(new URL("../../", import.meta.url));
  const interpreter = fileURLToPath(
    new URL("../../.venv/bin/python", import.meta.url),
  );
  // Real current compiler output; no CAD export, meshing or solver is called.
  const candidate = JSON.parse(
    execFileSync(
      existsSync(interpreter) ? interpreter : "python3",
      [
        "-c",
        `
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path('design/component-catalogue/src').resolve()))
from engineering.design_engine.registry import get
from engineering.design_engine.adapters import compile_candidate
scope=json.loads(sys.stdin.read())
print(json.dumps(compile_candidate(get('mechanical-cleat'),scope,{'thickness_m':0.012,'topology':'lightened-web'})))
`,
      ],
      {
        cwd: root,
        input: JSON.stringify(identity),
        encoding: "utf8",
        timeout: 10000,
      },
    ),
  );
  const part = candidate.definition.model.parts[0];
  expect(candidate.definition.model.parts).toHaveLength(1);
  expect(candidate.complete_installed_mass_kg).toBeNull();
  expect(
    candidate.definition.model.materials[part.material].yield_strength_pa,
  ).toBeNull();
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.route("**/api/ops-auth/session", (route) =>
    route.fulfill({ json: { actor: null } }),
  );
  await page.route("**/api/design/**", (route) => {
    const path = new URL(route.request().url()).pathname;
    let json = {};
    if (path.endsWith("/problems"))
      json = {
        problems: [
          {
            id: "mechanical-cleat",
            variables: {},
            budget: { evaluations: 32 },
            applicability: {
              function: "Real compiler output; browser display fixture only",
            },
          },
        ],
        preflight: {
          "mechanical-cleat": {
            available: false,
            missing: ["No native execution in browser fixture"],
          },
        },
      };
    else if (path.endsWith("/review-schema"))
      json = {
        kinds: { appointment: ["person_name"] },
        accounts_configured: false,
      };
    else if (path.endsWith("/parts")) json = { sources: {}, parts: [] };
    else if (path.endsWith("/records")) json = { records: [] };
    else if (path.endsWith("/work-queue")) json = { entries: [] };
    else if (path.endsWith("/jobs"))
      json = {
        jobs: [
          {
            id: "generated-browser-fixture",
            status: "completed",
            phase: "completed",
            progress: 100,
            source_state: "current",
            request: { identity, problem: { id: "mechanical-cleat" } },
          },
        ],
      };
    else if (path.endsWith("/comparison"))
      json = { identity, source_state: "current", candidates: [candidate] };
    return route.fulfill({ json });
  });
  await page.goto(
    `${origin}/docs/design-engine/?city=samawah&project=generated-inspector-fixture&revision=fixture-r1&baseline_sha256=${identity.baseline_sha256}&view=jobs`,
  );
  await page
    .getByRole("button", { name: "Inspect results", exact: true })
    .click();
  await expect(page.locator("#comparison")).toContainText(
    "Complete installed mass",
  );
  await expect(page.locator("#comparison")).toContainText("unknown");
  await expect(
    page
      .locator("#comparison tr")
      .filter({ hasText: "Complete installed mass" }),
  ).toContainText("unknown");
  await page
    .getByRole("button", { name: "Inspect physical parts", exact: true })
    .click();
  const inspector = page.locator("#inspector");
  await expect(inspector.locator("select option")).toHaveCount(1);
  await expect(inspector.locator("select")).toHaveValue(part.id);
  await expect(inspector.locator("svg circle")).toHaveCount(1);
  expect(
    Number.isFinite(
      Number(await inspector.locator("svg circle").getAttribute("cx")),
    ),
  ).toBe(true);
  await expect(inspector.locator("[data-assembly-detail]")).toContainText(
    `${part.properties.mass_kg} kg`,
  );
  await expect(inspector).toContainText(
    "Schematic of represented part centres",
  );
  await expect(inspector).not.toContainText("No complete physical inventory");
  await inspector
    .getByText("Declared material properties", { exact: true })
    .click();
  await expect(inspector).toContainText('"yield_strength_pa": null');
  await inspector
    .getByText("Unresolved installed allocations", { exact: true })
    .click();
  await expect(inspector).toContainText("fixture/support hardware");
  await expect(inspector).toContainText("bolts and contact interfaces");
  await expect(
    inspector.locator('a[href$=".step"],a[href$=".FCStd"]'),
  ).toHaveCount(0);
  await expect(page.locator("#qualificationDraft")).toBeHidden();
  expect(errors).toEqual([]);
});

for (const lang of ["en", "ar"])
  test(`recursive iteration controls and conditional evidence in ${lang}`, async ({
    page,
  }) => {
    const identity = {
      schema: "osr-design-identity/1",
      city: "samawah",
      project: "recursive-ui-fixture",
      environment: "simulation",
      configuration_revision: "fixture-r1",
      baseline_sha256: "b".repeat(64),
      run_id: null,
      asset_id: null,
      part_id: null,
    };
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    const submitted = [];
    let verified = true;
    const candidate = {
      id: "fixture-verified-candidate",
      identity,
      variables: { thickness_m: 0.012 },
      metrics: { defined_mass_kg: 1 },
      checks: {
        linear_service: {
          state: "passed",
          basis: "Browser numerical fixture only",
        },
        physical_correlation: {
          state: "unknown",
          basis: "Browser fixture supplies no physical evidence",
        },
      },
    };
    await page.route("**/api/ops-auth/session", (route) =>
      route.fulfill({ json: { actor: null } }),
    );
    await page.route("**/api/design/**", (route) => {
      const request = route.request();
      const path = new URL(request.url()).pathname;
      let json = {};
      if (path.endsWith("/problems")) {
        const problems = [
          "mechanical-cleat",
          "civil-steel-beam",
          "no-native-fixture",
        ].map((id) => ({
          id,
          adapter: id,
          variables: {
            thickness_m: { kind: "choice", unit: "m", choices: [0.01, 0.012] },
          },
          budget: { evaluations: 256 },
          applicability: {
            function: "Browser fixture only; no native physics",
          },
        }));
        json = {
          problems,
          preflight: {},
          operations: Object.fromEntries(
            problems.map(({ id }) => [
              id,
              {
                screen: { available: true, missing: [] },
                optimise: { available: false, missing: ["pymoo"] },
                confirm: { available: true, missing: [] },
                iterate: {
                  available: id !== "no-native-fixture",
                  missing: id === "no-native-fixture" ? ["Gmsh"] : [],
                },
              },
            ]),
          ),
        };
      } else if (path.endsWith("/review-schema"))
        json = {
          kinds: { appointment: ["person_name"] },
          accounts_configured: false,
        };
      else if (path.endsWith("/parts")) json = { sources: {}, parts: [] };
      else if (path.endsWith("/records")) json = { records: [] };
      else if (path.endsWith("/work-queue")) json = { entries: [] };
      else if (path.endsWith("/jobs") && request.method() === "POST") {
        submitted.push(request.postDataJSON());
        json = { id: "fixture-recursive-job" };
      } else if (path.endsWith("/jobs"))
        json = {
          jobs: [
            {
              id: "fixture-recursive-job",
              status: "completed",
              phase: "completed",
              progress: 100,
              source_state: "current",
              request: { identity, problem: { id: "mechanical-cleat" } },
            },
          ],
        };
      else if (path.endsWith("/comparison"))
        json = {
          identity,
          source_state: "current",
          candidates: [candidate],
          recursive_search: {
            incumbent_id: verified ? "fixture-verified-candidate" : null,
            termination_reason: verified ? "finite-space-exhausted" : "budget",
            best_verified_in_tested_domain_claimed: verified,
            best_verified_claim_scope: verified
              ? "declared finite choices and numerical checks only"
              : null,
            lineage: [
              {
                index: 0,
                phase: "confirm",
                parent_id: "fixture-parent",
                candidate_id: "fixture-failed",
                variables: { thickness_m: 0.01 },
                outcome: {
                  numerically_verified: false,
                  failed_checks: 1,
                  unresolved_checks: 0,
                },
              },
            ],
          },
        };
      return route.fulfill({ json });
    });
    await page.goto(
      `${origin}/docs/design-engine/?city=samawah&project=recursive-ui-fixture&revision=fixture-r1&baseline_sha256=${identity.baseline_sha256}&lang=${lang}`,
    );
    await expect(page.locator("#run")).toBeEnabled();
    await page.locator("#search").check();
    await expect(page.locator("#run")).toBeDisabled();
    await page.locator("#iterate").check();
    await expect(page.locator("#search")).not.toBeChecked();
    await expect(page.locator("#refine")).toBeDisabled();
    await expect(page.locator("#run")).toBeEnabled();
    await expect(page.locator("#budget")).toHaveValue("32");
    await page.locator("#problem").selectOption("no-native-fixture");
    await expect(page.locator("#run")).toBeDisabled();
    await expect(page.locator("#preflight")).toContainText("Gmsh");
    await page.locator("#problem").selectOption("mechanical-cleat");
    await page.locator("#search").check();
    await expect(page.locator("#iterate")).not.toBeChecked();
    await page.locator("#iterate").check();
    for (const problem of ["mechanical-cleat", "civil-steel-beam"]) {
      await page.locator("#problem").selectOption(problem);
      await page.locator("#run").click();
      await expect
        .poll(() => submitted.length)
        .toBe(problem === "mechanical-cleat" ? 1 : 2);
      const body = submitted.at(-1);
      expect(body.identity).toEqual(identity);
      expect(body.problem).toBe(problem);
      expect(body.search).toBeNull();
      expect(body.refine).toBe(true);
      expect(body.recursive).toEqual({
        evaluations: 32,
        iterations: 32,
        confirmations: 12,
        finite_exhaustive: true,
      });
      expect(body.budget).toEqual({ evaluations: 32 });
      await page.locator('[data-view="design"]').click();
    }
    await page.reload();
    await expect(page.locator("#iterate")).toBeChecked();
    await expect(page.locator("#search")).not.toBeChecked();
    await expect(page.locator("#refine")).toBeDisabled();
    await page.locator('[data-view="jobs"]').click();
    await page
      .getByRole("button", { name: "Inspect results", exact: true })
      .click();
    const results = page.locator("[data-recursive-results]");
    await expect(results).toContainText("fixture-verified-candidate");
    await expect(results).toContainText("finite-space-exhausted");
    await expect(results).toContainText(
      "declared finite choices and numerical checks only",
    );
    await expect(results).toContainText(
      lang === "ar"
        ? "لم يتم إثبات حل أمثل عالمي"
        : "No global optimum or physical release",
    );
    await results.locator("summary").click();
    await expect(results).toContainText("fixture-parent");
    await expect(results).toContainText("fixture-failed");
    await expect(results).toContainText('"failed_checks":1');
    verified = false;
    await page
      .getByRole("button", { name: "Inspect results", exact: true })
      .click();
    await expect(results).toContainText(
      lang === "ar"
        ? "لا يوجد مرشح متحقق عددياً"
        : "No numerically verified candidate",
    );
    await expect(results).toContainText(
      lang === "ar" ? "غير مثبت" : "Not established",
    );
    await expect(results).toContainText("budget");
    await expect(results).not.toContainText("fixture-verified-candidate");
    expect(errors).toEqual([]);
  });
