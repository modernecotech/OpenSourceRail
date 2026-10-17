import { expect, test } from "@playwright/test";
import { expandReview } from "../../docs/design-engine/campaign-review/model.js";

function reviewUrl(info) {
  // The default full frontend suite supplies only its Workbench server4177;
  // the dedicated config supplies both static document-root arrangements.
  const base = info.project.use.baseURL || "http://127.0.0.1:4177/";
  const prefix = info.project.metadata?.staticRoot === "docs" ? "" : "docs/";
  return new URL(`${prefix}design-engine/campaign-review/`, base).href;
}

async function openReview(page, request, info) {
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  const url = reviewUrl(info);
  const response = await page.goto(url);
  expect(response?.ok()).toBe(true);
  await expect(page.locator("#load-status")).toContainText(
    "manufacturing release: false",
  );
  await expect(page.locator("#load-status")).not.toContainText(
    "could not load",
  );
  const payload = await request.get(new URL("data.json", url).href);
  expect(payload.ok()).toBe(true);
  const data = expandReview(await payload.json());
  expect(data.physical_release).toBe(false);
  expect(data.manufacturing_release).toBe(false);
  return { data, errors };
}

test("complete package and history context stays visible under either static root", async ({
  page,
  request,
}, info) => {
  const { data, errors } = await openReview(page, request, info);
  await expect(page.locator("header .notice")).toContainText(
    "does not establish a complete design or manufacturing release",
  );
  expect(data.packages).toHaveLength(63);
  await expect(page.locator("#package-list > details")).toHaveCount(63);
  await expect(page.locator("#audit-summary")).toContainText(
    "63 packages remain open",
  );
  await expect(page.locator("#audit-summary")).toContainText(
    "0 actual result records",
  );
  await expect(page.locator("#audit-summary")).toContainText(
    "0 issued drawing references",
  );
  await expect(page.locator("#applicability-rule")).toContainText(
    "integrity checks do not recompute physics",
  );
  await expect(page.locator("#applicability-rule")).toContainText(
    "not counts of completed components",
  );
  await expect(page.locator("#history-list .history-entry")).toHaveCount(
    data.packets.length,
  );
  for (let index = 0; index < data.packets.length; index++) {
    const packet = data.packets[index];
    expect(["historical", "current-at-generation"]).toContain(
      packet.applicability,
    );
    const card = page.locator("#history-list .history-entry").nth(index);
    await expect(card).toContainText(packet.applicability);
    await expect(card).toContainText("Retained integrity verified");
    const link = card.getByRole("link", {
      name: "Snapshot / archive reference",
    });
    const evidence = await request.get(await link.getAttribute("href"));
    expect(evidence.ok()).toBe(true);
  }
  for (const id of ["initial", "queued"]) {
    expect(data.packets.find((p) => p.id === id).applicability).toBe(
      "historical",
    );
  }
  await page.locator("#package-search").fill("LM3-FRP-150");
  await expect(page.locator("#package-list > details")).toHaveCount(1);
  await page.locator("#package-list summary").click();
  await expect(page.locator("#package-list")).toContainText(
    "Design complete: false. Manufacturing release: false.",
  );
  const layout = await page.evaluate(() => ({
    documentWidth: document.documentElement.scrollWidth,
    viewportWidth: innerWidth,
  }));
  expect(layout.documentWidth).toBeLessThanOrEqual(layout.viewportWidth + 1);
  await info.attach("campaign-review-viewport", {
    body: await page.screenshot(),
    contentType: "image/png",
  });
  expect(errors).toEqual([]);
});

test("architecture and failed screens retain the864 sampled six-car responses", async ({
  page,
  request,
}, info) => {
  const { data, errors } = await openReview(page, request, info);
  const responses = data.candidates.filter(
    (r) => r.family === "six-car-envelope-response",
  );
  expect(responses).toHaveLength(864);
  expect(
    responses.every((r) => r.record_kind === "sampled-stress-response"),
  ).toBe(true);
  const sourceCase = data.cases.find((c) => c.id === responses[0].case);
  expect(sourceCase.architecture).not.toBe("LM3");
  expect(sourceCase.architecture).not.toBe("package-specific-unadopted");
  await page.locator("#packet").selectOption("queued");
  await page.locator("#family").selectOption("six-car-envelope-response");
  await expect(page.locator("#result-count")).toHaveText(/^864 of /);
  await page.locator("#architecture").selectOption(sourceCase.architecture);
  await expect(page.locator("#result-count")).toHaveText(/^864 of /);
  await page.locator("#architecture").selectOption("LM3");
  await expect(page.locator("#result-count")).toHaveText(/^0 of /);
  await expect(page.locator("#candidate-rows")).toContainText(
    "No records match",
  );
  await page.locator("#architecture").selectOption(sourceCase.architecture);
  await page.locator("#screen").selectOption("failed");
  const adverse = responses.find(
    (r) => r.metrics.minimum_service_compression_pa < 0,
  );
  expect(adverse).toBeTruthy();
  expect(adverse.screen).toBe("failed");
  expect(adverse.failed_checks).toContain("isolated_zero_tension_predicate");
  expect(adverse.unknown_gates.length).toBeGreaterThan(0);
  await page.locator("#search").fill(adverse.candidate_id);
  await expect(page.locator("#result-count")).toHaveText(/^1 of /);
  const row = page.locator("#candidate-rows tr");
  await expect(row).toHaveCount(1);
  await expect(row).toContainText("Failed known check");
  const minimumCell = row.locator("td").nth(4);
  await expect(minimumCell).toHaveText(/^-[\d,.]+ MPa$/);
  const displayedMpa = Number(
    (await minimumCell.innerText()).replace(" MPa", "").replaceAll(",", ""),
  );
  expect(
    Math.abs(
      displayedMpa - adverse.metrics.minimum_service_compression_pa / 1e6,
    ),
  ).toBeLessThanOrEqual(0.00051);
  await row.getByRole("checkbox").check();
  await expect(page.locator("#comparison-cards")).toContainText(
    "isolated_zero_tension_predicate",
  );
  await expect(page.locator("#comparison-cards")).toContainText(
    "Manufacturing release: false",
  );
  expect(errors).toEqual([]);
});

test("two-record comparison distinguishes source changes and never promotes a proposal", async ({
  page,
  request,
}, info) => {
  const { data, errors } = await openReview(page, request, info);
  for (const candidate of data.candidates) {
    expect(candidate.selected_local && candidate.proposed_configuration).toBe(
      false,
    );
    if (candidate.selected_local)
      expect(candidate.source_configuration_compatible).not.toBe(false);
    if (candidate.screen === "local-pass")
      expect(candidate.failed_checks).toEqual([]);
  }
  await page.locator("#packet").selectOption("queued");
  await page.locator("#shortlisted").check();
  for (const family of ["gangway", "service_loop"]) {
    const proposal = data.candidates.find(
      (r) =>
        r.packet === "queued" &&
        r.family === family &&
        r.proposed_configuration,
    );
    expect(proposal).toBeTruthy();
    expect(proposal.source_configuration_compatible).toBe(false);
    expect(proposal.selected_local).toBe(false);
    expect(proposal.screen).toBe("failed");
    await page.locator("#family").selectOption(family);
    await page.locator("#search").fill(proposal.candidate_id);
    await expect(page.locator("#candidate-rows tr")).toHaveCount(1);
    await page.locator("#candidate-rows").getByRole("checkbox").check();
  }
  await expect(page.locator("#comparison-cards > article")).toHaveCount(2);
  await expect(page.locator("#comparison-note")).toContainText(
    "changes the source configuration",
  );
  await expect(page.locator("#comparison-note")).not.toContainText(
    "Same declared",
  );
  for (const card of await page.locator("#comparison-cards > article").all()) {
    await expect(card).toContainText("Source configuration conflict");
    await expect(card).toContainText("existing_intercar_spacing");
    await expect(card).toContainText("Manufacturing release: false");
  }
  await page.locator("#family").selectOption("glazing");
  await page.locator("#search").fill("");
  const other = page.locator("#candidate-rows").getByRole("checkbox").first();
  await expect(other).toBeDisabled();
  await page.locator("#clear-comparison").click();
  await expect(page.locator("#comparison-cards > article")).toHaveCount(0);
  await expect(other).toBeEnabled();
  expect(errors).toEqual([]);
});
