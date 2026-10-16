import { expect, test } from "@playwright/test";

for (const lang of ["en", "ar"]) {
  test(`refinement execution and validation remain separate in ${lang}`, async ({
    page,
  }) => {
    await page.goto("http://127.0.0.1:4177/docs/design-engine/");
    await page.evaluate(async (language) => {
      localStorage.setItem("osr:ui:language", language);
      const { refinementCampaigns } =
        await import("/docs/design-engine/refinement-campaign.js");
      const root = document.createElement("div");
      root.id = "refinement-browser-fixture";
      document.body.prepend(root);
      refinementCampaigns(root, {
        definition: {
          independent_refinement_campaigns: {
            "labelled-browser-fixture": {
              planned: 5,
              executed: 2,
              validated: 0,
              cases: {
                baseline: { state: "completed", full_passage_coverage: true },
                time: { state: "completed", full_passage_coverage: true },
                deck: { state: "not-run" },
              },
              comparison: {
                baseline_provenance_verified: true,
                cases: [
                  {
                    id: "time",
                    state: "unknown",
                    provenance_verified: false,
                    provenance_issues: [
                      "solver toolchain identity differs from baseline",
                    ],
                  },
                ],
              },
            },
          },
        },
      });
    }, lang);
    const root = page.locator("#refinement-browser-fixture");
    await expect(root.getByRole("heading")).toHaveText(
      lang === "en"
        ? "Independent passage refinement"
        : "تنقيح مستقل لعبور القطار",
    );
    const time = root
      .locator("tbody tr")
      .filter({ has: page.getByRole("cell", { name: "time", exact: true }) });
    await expect(time).toContainText("completed");
    await expect(time).toContainText("toolchain identity differs");
    await expect(time.locator(".state-unknown")).toHaveCount(2);
    await expect(
      root.locator("table").first().locator("tbody tr td"),
    ).toHaveText(["labelled-browser-fixture", "5", "2", "0"]);
  });
}
