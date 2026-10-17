import assert from "node:assert/strict";
import test from "node:test";
import {
  filterCandidates,
  comparisonNotice,
  screenLabel,
  valueText,
  expandReview,
} from "../../docs/design-engine/campaign-review/model.js";

const data = {
  cases: [
    { id: "lm3", architecture: "LM3", label: "Three cars" },
    { id: "six", architecture: "six-car", label: "Six cars" },
  ],
  candidates: [
    {
      id: "a",
      candidate_id: "beam-a",
      case: "lm3",
      family: "civil",
      packet: "old",
      screen: "failed",
      packages: ["CIV-100"],
      failed_checks: ["stress"],
      unknown_gates: ["material"],
      variables: { depth_m: 1.4 },
      selected_local: false,
    },
    {
      id: "b",
      candidate_id: "beam-b",
      case: "six",
      family: "civil",
      packet: "new",
      screen: "local-pass",
      packages: [],
      failed_checks: [],
      unknown_gates: ["load"],
      variables: { depth_m: 1.7 },
      selected_local: true,
    },
    {
      id: "c",
      candidate_id: "frame-c",
      case: "lm3",
      family: "chassis",
      packet: "new",
      screen: "failed",
      packages: ["FRAME"],
      failed_checks: ["envelope"],
      unknown_gates: ["weld"],
      variables: { height: 0.75 },
      proposed_configuration: true,
      source_configuration_compatible: false,
    },
  ],
};

test("filters keep architecture, known failures and proposal status separate", () => {
  assert.deepEqual(
    filterCandidates(data, { architecture: "LM3", screen: "failed" }).map(
      (r) => r.id,
    ),
    ["a", "c"],
  );
  assert.deepEqual(
    filterCandidates(data, { query: "CIV-100" }).map((r) => r.id),
    ["a"],
  );
  assert.deepEqual(
    filterCandidates(data, { packet: "new", shortlisted: true }).map(
      (r) => r.id,
    ),
    ["b", "c"],
  );
  assert.equal(
    filterCandidates(data, { case: "six", family: "chassis" }).length,
    0,
  );
});

test("comparison warns across load cases and source-changing proposals", () => {
  assert.match(
    comparisonNotice(data.candidates[0], data.candidates[1]),
    /Different configurations/,
  );
  assert.match(
    comparisonNotice(data.candidates[2], {
      ...data.candidates[2],
      id: "other",
    }),
    /changes the source configuration/,
  );
  assert.match(
    comparisonNotice(data.candidates[0], {
      ...data.candidates[0],
      id: "other",
    }),
    /no manufacturing release/,
  );
  assert.match(comparisonNotice(data.candidates[0]), /second/);
});

test("local success never becomes complete qualification and unknown is not zero", () => {
  assert.equal(screenLabel(data.candidates[1]), "Local screen passed only");
  assert.equal(valueText(null), "Not evaluated / unknown");
  assert.equal(valueText(undefined), "Not evaluated / unknown");
  assert.equal(valueText(NaN), "Not evaluated / unknown");
  assert.equal(valueText(0), "0");
  assert.equal(valueText(22176000, 1e6, " MN"), "22.176 MN");
});

test("compact references preserve known zero, failed checks and detailed unknowns", () => {
  const compact = {
    schema: "osr-campaign-review-compact/1",
    columns: [
      "candidate_id",
      "packet",
      "case",
      "family",
      "screen",
      "variables_ref",
      "gates_ref",
      "metric_keys_ref",
      "metric_values",
      "failures_ref",
      "action_ref",
      "source_ref",
    ],
    records: [
      ["beam", "new", "six", "civil", "failed", 0, 0, 0, [0, -2e6], 0, 0, 0],
    ],
    tables: {
      variables: [{ depth_m: 1.4 }],
      gates: [["material: test strength absent"]],
      metric_keys: [["zero", "minimum_service_compression_pa"]],
      failures: [["service_no_tension"]],
      actions: ["Repair failed stress predicate."],
      sources: ["../packet/civil.json"],
    },
  };
  const row = expandReview(compact).candidates[0];
  assert.equal(row.id, "new:six:civil:beam");
  assert.equal(row.metrics.zero, 0);
  assert.equal(row.metrics.minimum_service_compression_pa, -2e6);
  assert.deepEqual(row.unknown_gates, ["material: test strength absent"]);
  assert.deepEqual(row.failed_checks, ["service_no_tension"]);
  assert.equal(row.manufacturing_release, false);
  const missing = structuredClone(compact);
  missing.records[0][5] = 9;
  assert.throws(() => expandReview(missing), /Invalid compact/);
  const shortened = structuredClone(compact);
  shortened.records[0][8] = [0];
  assert.throws(() => expandReview(shortened), /Incomplete compact metric/);
});
