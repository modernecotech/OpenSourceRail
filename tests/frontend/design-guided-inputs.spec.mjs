import { test, expect } from "@playwright/test";

const origin = process.env.OSR_GUIDED_TEST_URL || "http://127.0.0.1:4177";
for (const lang of ["en", "ar"])
  test(`guided manufacturing and exact evidence applicability in ${lang}`, async ({
    page,
  }) => {
    const identity = {
      schema: "osr-design-identity/1",
      city: "samawah",
      project: "fixture-project",
      environment: "simulation",
      configuration_revision: "fixture-r1",
      baseline_sha256: "b".repeat(64),
      run_id: null,
      asset_id: null,
      part_id: null,
    };
    const candidate = {
      id: "fixture-candidate",
      identity,
      definition_sha256: "d".repeat(64),
      variables: { support_span_m: 0.5 },
      metrics: { defined_mass_kg: 12 },
      checks: {
        geometry: { state: "passed", basis: "Browser fixture only" },
        nominal_deflection: {
          state: "failed",
          basis: "Fixture recorded limit",
          value: 0.006,
          limit: 0.005,
          unit: "m",
        },
      },
      definition: {
        contract: {
          parts: [
            {
              id: "panel",
              revision: "fixture-r1",
              material: "gfrp",
              properties: { mass_kg: 10, cg_m: [0, 0, 0] },
            },
            {
              id: "rail",
              revision: "fixture-r1",
              material: "steel",
              properties: { mass_kg: 2, cg_m: [1, 0, 0] },
            },
          ],
        },
        installed_register: {
          physical_definition_sha256: "a".repeat(64),
          parts: [
            {
              physical_id: "panel",
              part_id: "PANEL",
              quantity: 1,
              unit: "ea",
              defined_mass_kg: 10,
              material: "gfrp",
            },
            {
              physical_id: "rail",
              part_id: "RAIL",
              quantity: 1,
              unit: "ea",
              defined_mass_kg: 2,
              material: "steel",
            },
          ],
          joints: [
            { id: "fixture-joint", physical_part_ids: ["panel", "rail"] },
          ],
          dimensional_manufacturing: {
            checks: [
              {
                id: "rail/stock",
                physical_id: "rail",
                state: "failed",
                basis: "Fixture stock too short",
              },
            ],
          },
          unresolved_allocations: ["Fixture unresolved seal"],
        },
      },
    };
    const records = [
      {
        id: "fixture-source",
        revision: "source-r1",
        kind: "inspection",
        state: "verified",
        creator: "fixture-author",
        applicability: {
          candidate_id: candidate.id,
          physical_part_id: null,
          material_batch: null,
          definition_sha256: "a".repeat(64),
        },
        payload: { source_reference: "fixture only" },
      },
    ];
    let submitted;
    let proposalRequest;
    let proposals = [];
    let currentActor = {
      username: "fixture-planner",
      display_name: "Fixture planner",
      csrf: "fixture-csrf",
      roles: ["planner"],
    };
    await page.route("**/api/ops-auth/session", (route) =>
      route.fulfill({ json: { actor: currentActor } }),
    );
    await page.route("**/api/ops-auth/login", (route) => {
      currentActor = {
        username: "fixture-approver",
        display_name: "Fixture approver",
        csrf: "fixture-approver-csrf",
        roles: ["approver", "planner"],
      };
      return route.fulfill({ json: { actor: currentActor } });
    });
    await page.route("**/api/design/**", (route) => {
      const url = new URL(route.request().url());
      const path = url.pathname;
      let json = {};
      if (path.endsWith("/problems"))
        json = {
          problems: [
            {
              id: "fixture-problem",
              variables: {},
              budget: { evaluations: 2 },
              applicability: { function: "Fixture only" },
            },
          ],
          preflight: {
            "fixture-problem": {
              available: false,
              missing: ["No fixture solver"],
            },
          },
        };
      else if (path.endsWith("/review-schema"))
        json = {
          kinds: { appointment: ["person_name"] },
          accounts_configured: true,
        };
      else if (path.endsWith("/parts")) json = { sources: {}, parts: [] };
      else if (path.endsWith("/jobs"))
        json = {
          jobs: [
            {
              id: "fixture-job",
              status: "completed",
              phase: "completed",
              progress: 100,
              source_state: "current",
              request: { identity, problem: { id: "fixture-problem" } },
            },
          ],
        };
      else if (path.endsWith("/work-queue")) json = { entries: [] };
      else if (path.endsWith("/comparison"))
        json = { identity, source_state: "current", candidates: [candidate] };
      else if (path.endsWith("/qualification-draft"))
        json = { draft_sha256: "e".repeat(64), physical_release: false };
      else if (
        path.endsWith("/input-revisions") &&
        route.request().method() === "POST"
      ) {
        proposalRequest = route.request().postDataJSON();
        const row = {
          id: "inputs-fixture",
          parent_job: "fixture-job",
          creator: "fixture-planner",
          state: "proposed",
          proposal_sha256: "f".repeat(64),
          target_identity: {
            ...identity,
            configuration_revision: "fixture-r2",
          },
          proposal: {
            parent_candidate: candidate.id,
            invalidated: ["geometry", "BOM", "optimisation"],
          },
        };
        proposals.push(row);
        json = row;
      } else if (path.endsWith("/input-revisions"))
        json = { revisions: proposals, identity };
      else if (path.endsWith("/review")) {
        proposals[0].state = "reviewed-input";
        json = proposals[0];
      } else if (path.endsWith("/run"))
        json = {
          job: { id: "fixture-child-job" },
          child_identity: { ...identity, configuration_revision: "fixture-r2" },
          baseline_modified: false,
          physical_release: false,
        };
      else if (path.endsWith("/records") && route.request().method() === "GET")
        json = { records };
      else if (path.endsWith("/records")) {
        submitted = route.request().postDataJSON();
        json = { id: "fixture-retained-record" };
      }
      return route.fulfill({ json });
    });
    const sources = page.waitForResponse(
      (response) => new URL(response.url()).pathname === "/api/design/records",
    );
    await page.goto(
      `${origin}/docs/design-engine/?city=samawah&project=fixture-project&revision=fixture-r1&baseline_sha256=${identity.baseline_sha256}&view=jobs&lang=${lang}`,
    );
    await sources;
    await page
      .getByRole("button", { name: "Inspect results", exact: true })
      .click();
    await expect(page.locator(".candidate-reasons")).toContainText(".006");
    await expect(page.locator(".candidate-reasons")).toContainText(".005");
    await page
      .getByRole("button", { name: "Inspect physical parts", exact: true })
      .click();
    await expect(page.locator(".assembly-schematic")).toBeVisible();
    await expect(page.locator(".assembly-schematic circle")).toHaveCount(2);
    await page
      .locator("[data-assembly-detail] summary")
      .filter({ hasText: "fixture-joint" })
      .click();
    await page
      .locator("[data-assembly-detail]")
      .getByRole("button", { name: "rail", exact: true })
      .click();
    await expect(page.locator("[data-assembly-detail]")).toContainText(
      "Fixture stock too short",
    );
    await page.locator("[data-guided-source]").selectOption("fixture-source");
    for (const [field, value] of [
      ["stockX", "2"],
      ["stockY", "3"],
      ["stockZ", ".1"],
    ])
      await page.locator(`[data-guided-field="${field}"]`).fill(value);
    await page.locator("[data-guided-add]").click();
    await expect(page.locator('[data-guided-field="wall"]')).toHaveAttribute(
      "aria-invalid",
      "true",
    );
    await page.locator('[data-guided-field="wall"]').fill(".001");
    await page.locator("[data-guided-add]").click();
    const plan = JSON.parse(
      await page.locator("#qualificationInput").inputValue(),
    );
    expect(plan.part_rules).toEqual([
      {
        physical_id: "panel",
        basis_reference: "fixture-source",
        stock_bounds_m: [2, 3, 0.1],
        minimum_wall_m: 0.001,
      },
    ]);
    expect(plan.tooling).toEqual([]);
    await page.locator('[data-view="evidence"]').click();
    await page.locator("#recordApplicability button").click();
    expect(
      await page
        .locator('[data-applicability-field="candidate_id"]')
        .inputValue(),
    ).toBe(candidate.id);
    expect(
      await page
        .locator('[data-applicability-field="physical_part_id"]')
        .inputValue(),
    ).toBe("rail");
    await page
      .locator('[data-applicability-field="material_batch"]')
      .fill("Fixture batch; not measured");
    await page
      .locator('[data-appointment-field="person_name"]')
      .fill("Browser fixture person");
    await page.locator("#recordForm>button").click();
    await expect
      .poll(() => submitted?.identity?.project)
      .toBe("fixture-project");
    expect(submitted.identity).toEqual(identity);
    expect(submitted.applicability).toEqual({
      candidate_id: candidate.id,
      physical_part_id: "rail",
      material_batch: "Fixture batch; not measured",
      definition_sha256: "a".repeat(64),
    });
    await page.locator('[data-view="parts"]').click();
    await page.locator("#qualificationValidate").click();
    await expect(page.locator("[data-revision-draft]")).toHaveCount(1);
    await page.locator("[data-revision-record]").check();
    await page.locator("[data-input-revision-name]").fill("fixture-r2");
    await page
      .locator("[data-input-revision-rationale]")
      .fill("Fixture source use for numerical research only");
    await page.locator("#inputRevisionForm>button").click();
    await expect(page.locator("[data-input-proposal]")).toHaveCount(1);
    expect(proposalRequest.identity).toEqual(identity);
    expect(proposalRequest.drafts).toEqual(["e".repeat(64)]);
    expect(proposalRequest.records).toEqual([
      {
        id: records[0].id,
        revision: records[0].revision,
        applicability: records[0].applicability,
      },
    ]);
    const reviewButton = page.locator("[data-input-proposal] > button").first();
    await expect(reviewButton).toBeDisabled();
    await page.locator("#login").locator("..").locator("summary").click();
    await page
      .locator('#login input[name="username"]')
      .fill("Fixture approver");
    await page
      .locator('#login input[name="password"]')
      .fill("Fixture password");
    await page.locator("#login button").click();
    await expect(reviewButton).toBeEnabled();
    await page
      .locator("[data-input-review-rationale]")
      .fill("Independent fixture permission for numerical use only");
    await reviewButton.click();
    await expect(page.locator("[data-input-proposal]")).toContainText(
      "reviewed-input",
    );
    await page.locator("[data-input-proposal] > div button").click();
    const childLink = page.locator("#inputRevisionForm a");
    await expect(childLink).toHaveAttribute("href", /revision=fixture-r2/);
    expect(
      new URL(await childLink.getAttribute("href")).searchParams.get(
        "baseline_sha256",
      ),
    ).toBe(identity.baseline_sha256);
    await expect(page.locator("html")).toHaveAttribute(
      "dir",
      lang === "ar" ? "rtl" : "ltr",
    );
    await page.setViewportSize({ width: 390, height: 844 });
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth + 1,
      ),
    ).toBe(true);
  });

test("operation preflight separates screen search confirmation CAD and foundation inputs", async ({
  page,
}) => {
  const identity = {
    schema: "osr-design-identity/1",
    city: "samawah",
    project: "preflight-fixture",
    environment: "simulation",
    configuration_revision: "fixture-r1",
    baseline_sha256: "b".repeat(64),
    run_id: null,
    asset_id: null,
    part_id: null,
  };
  let cadQuery;
  const foundation = {
    schema: "fixture-foundation-only",
    method: "UI fixture, not foundation resistance",
    axial_load_n: null,
  };
  const candidate = {
    id: "fixture-foundation-candidate",
    variables: {},
    metrics: { defined_mass_kg: 1 },
    checks: { geometry: { state: "passed", basis: "UI fixture only" } },
    definition: {
      contract: { parts: [{ id: "fixture-pile", revision: "fixture-r1" }] },
      installed_register: { physical_definition_sha256: "a".repeat(64) },
      civil_input_templates: {
        site_input: { schema: "fixture-site" },
        prestress_input: { schema: "fixture-prestress" },
        foundation_input: foundation,
      },
    },
  };
  await page.route("**/api/ops-auth/session", (route) =>
    route.fulfill({ json: { actor: null } }),
  );
  await page.route("**/api/design/**", (route) => {
    const url = new URL(route.request().url());
    const path = url.pathname;
    let json = {};
    if (path.endsWith("/problems"))
      json = {
        problems: [
          {
            id: "fixture-problem",
            variables: {},
            budget: { evaluations: 2 },
            applicability: { function: "UI fixture only" },
          },
        ],
        preflight: { "fixture-problem": { available: true, missing: [] } },
        operations: {
          "fixture-problem": {
            screen: { available: true, missing: [] },
            optimise: { available: false, missing: ["pymoo"] },
            confirm: { available: false, missing: ["CalculiX"] },
          },
        },
      };
    else if (path.endsWith("/preflight")) {
      cadQuery = url.searchParams;
      json = {
        operation: "cad-export",
        available: false,
        missing: ["FreeCAD"],
      };
    } else if (path.endsWith("/review-schema"))
      json = {
        kinds: { appointment: ["person_name"] },
        accounts_configured: false,
      };
    else if (path.endsWith("/parts")) json = { sources: {}, parts: [] };
    else if (path.endsWith("/records")) json = { records: [] };
    else if (path.endsWith("/jobs"))
      json = {
        jobs: [
          {
            id: "fixture-job",
            status: "completed",
            phase: "completed",
            progress: 100,
            source_state: "current",
            request: { identity, problem: { id: "fixture-problem" } },
          },
        ],
      };
    else if (path.endsWith("/work-queue")) json = { entries: [] };
    else if (path.endsWith("/comparison"))
      json = { identity, source_state: "current", candidates: [candidate] };
    else if (path.endsWith("/input-revisions")) json = { revisions: [] };
    return route.fulfill({ json });
  });
  await page.goto(
    `${origin}/docs/design-engine/?city=samawah&project=preflight-fixture&revision=fixture-r1&baseline_sha256=${identity.baseline_sha256}`,
  );
  await expect(page.locator("#run")).toBeEnabled();
  await page.locator("#search").check();
  await expect(page.locator("#run")).toBeDisabled();
  await expect(page.locator("#preflight")).toContainText("pymoo");
  await page.locator("#search").uncheck();
  await page.locator("#refine").check();
  await expect(page.locator("#run")).toBeDisabled();
  await expect(page.locator("#preflight")).toContainText("CalculiX");
  await page.locator("#refine").uncheck();
  await expect(page.locator("#run")).toBeEnabled();
  await page.locator("#cadPreflight").click();
  await expect(page.locator("#cadPreflightStatus")).toContainText("FreeCAD");
  expect(cadQuery.get("problem")).toBe("fixture-problem");
  expect(cadQuery.get("operation")).toBe("cad-export");
  expect(cadQuery.get("project")).toBe("preflight-fixture");
  await page.locator('[data-view="jobs"]').click();
  await page
    .getByRole("button", { name: "Inspect results", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Inspect physical parts", exact: true })
    .click();
  await page.locator("#qualificationKind").selectOption("foundation");
  expect(
    JSON.parse(await page.locator("#qualificationInput").inputValue()),
  ).toEqual(foundation);
  await expect(page.locator("#guidedManufacturing")).toBeHidden();
});
