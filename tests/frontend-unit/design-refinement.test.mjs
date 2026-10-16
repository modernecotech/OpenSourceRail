import assert from "node:assert/strict";
import test from "node:test";
import {
  refinementRows,
  refinementLabels,
} from "../../docs/design-engine/refinement-campaign.js";

test("executed native cases do not become validated axis comparisons", () => {
  const candidate = {
    definition: {
      independent_refinement_campaigns: {
        straight: {
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
  };
  const rows = refinementRows(candidate);
  assert.equal(rows[0].comparison, null);
  assert.equal(rows[1].execution, "completed");
  assert.equal(rows[1].comparison, "unknown");
  assert.equal(rows[1].provenance, false);
  assert.equal(rows[1].coverage, true);
  assert.match(rows[1].issues[0], /toolchain/);
  assert.equal(rows[2].execution, "not-run");
  assert.equal(rows[2].coverage, false);
  assert.deepEqual(
    refinementRows({ definition: { paired_refinement: { state: "passed" } } }),
    [],
  );
});

test("refinement progress labels exist in English and Arabic", () => {
  for (const labels of Object.values(refinementLabels)) {
    assert.equal(labels.length, 2);
    assert.match(labels[1], /[\u0600-\u06ff]/);
  }
});
