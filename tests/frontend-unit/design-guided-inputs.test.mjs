import assert from "node:assert/strict";
import test from "node:test";
import {
  manufacturingRule,
  appendManufacturingRule,
  inputLabels,
} from "../../docs/design-engine/engineering-inputs.js";
import {
  partReferences,
  failedObservables,
  assemblyLabels,
  physicalParts,
} from "../../docs/design-engine/assembly-inspector.js";
import {
  scopeLabels,
  exactResearchScope,
} from "../../docs/design-engine/scope-controls.js";
import {
  eligibleRevisionRecords,
  revisionLink,
  revisionLabels,
} from "../../docs/design-engine/input-revisions.js";
import {
  operationReadiness,
  operationLabels,
  requestedOperations,
  recursiveTuning,
} from "../../docs/design-engine/operation-preflight.js";

const parts = ["panel", "rail", "bolt"];
const reference = {
  physical_id: "panel",
  basis_reference: "Fixture workshop envelope, not qualified",
};

test("physical inventory includes generated model parts without inventing installed mass", () => {
  const generated = {
    id: "cleat",
    quantity: 1,
    material: "research-steel",
    properties: { mass_kg: 0.928, cg_m: [0.1, 0, 0] },
    placement: {
      translation_m: [0, 0, 0],
      rotation: [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
      ],
    },
  };
  const candidate = {
    definition: {
      model: {
        parts: [generated],
        materials: { "research-steel": { yield_strength_pa: null } },
      },
    },
    complete_installed_mass_kg: null,
  };
  assert.deepEqual(physicalParts(candidate), [generated]);
  assert.equal(candidate.complete_installed_mass_kg, null);
  assert.equal(
    candidate.definition.model.materials[generated.material].yield_strength_pa,
    null,
  );
  assert.deepEqual(
    physicalParts({
      definition: { model: { instances: [{ id: "existing-instance" }] } },
    }),
    [{ id: "existing-instance" }],
  );
  assert.deepEqual(
    physicalParts({
      definition: {
        contract: { parts: [{ id: "existing-contract" }] },
        model: { parts: [generated] },
      },
    }),
    [{ id: "existing-contract" }],
  );
});

test("guided manufacturing forms preserve SI values and explicit source while rejecting missing facts", () => {
  const stock = manufacturingRule(
    "part_rules",
    { ...reference, stockX: "2", stockY: "3", stockZ: ".1", wall: ".001" },
    parts,
  );
  assert.deepEqual(stock.stock_bounds_m, [2, 3, 0.1]);
  assert.equal(stock.minimum_wall_m, 0.001);
  for (const patch of [
    { wall: "" },
    { stockX: "Infinity" },
    { stockY: "-1" },
    { wall: false },
    { basis_reference: "" },
    { physical_id: "invented-part" },
  ])
    assert.throws(() =>
      manufacturingRule(
        "part_rules",
        {
          ...reference,
          stockX: 2,
          stockY: 3,
          stockZ: 0.1,
          wall: 0.001,
          ...patch,
        },
        parts,
      ),
    );
});

test("tool and removal envelopes retain explicit obstacles and nonzero movement", () => {
  const values = {
    ...reference,
    lowX: 0,
    lowY: 0,
    lowZ: 0,
    highX: 1,
    highY: 2,
    highZ: 3,
    keepout_part_ids: ["rail"],
    shiftX: 0,
    shiftY: 0,
    shiftZ: 1,
  };
  assert.deepEqual(
    manufacturingRule("removal_paths", values, parts).translation_m,
    [0, 0, 1],
  );
  for (const patch of [
    { keepout_part_ids: [] },
    { keepout_part_ids: ["panel"] },
    { keepout_part_ids: ["rail", "rail"] },
    { highX: 0 },
    { shiftZ: 0 },
  ])
    assert.throws(() =>
      manufacturingRule("removal_paths", { ...values, ...patch }, parts),
    );
  const tolerance = manufacturingRule(
    "tolerance_stacks",
    {
      ...reference,
      nominal: ".005",
      required: ".002",
      plusMinus: ".001",
      contributor: "rail",
    },
    parts,
  );
  assert.deepEqual(tolerance.contributors, [
    { physical_id: "rail", plus_minus_m: 0.001 },
  ]);
  assert.throws(() =>
    manufacturingRule(
      "tooling",
      { ...reference, toolId: "fixture", toolKind: "fixture", count: 1.5 },
      parts,
    ),
  );
});

test("adding guided rules removes untouched blank template rows and retains entered unknown drafts", () => {
  const draft = {
    schema: "osr-manufacturing-plan/1",
    part_rules: [
      {
        physical_id: "panel",
        stock_bounds_m: [null, null, null],
        minimum_wall_m: null,
        basis_reference: null,
      },
    ],
    tooling: [
      {
        id: null,
        kind: null,
        count: null,
        physical_part_ids: ["panel"],
        basis_reference: null,
      },
    ],
    tolerance_stacks: [
      {
        physical_id: "rail",
        nominal_clearance_m: 0,
        required_clearance_m: null,
        basis_reference: null,
      },
    ],
  };
  const row = manufacturingRule(
    "part_rules",
    { ...reference, stockX: 2, stockY: 3, stockZ: 1, wall: 0.001 },
    parts,
  );
  const result = appendManufacturingRule(draft, "part_rules", row);
  assert.deepEqual(result.part_rules, [row]);
  assert.deepEqual(result.tooling, []);
  assert.deepEqual(result.tolerance_stacks, draft.tolerance_stacks);
  assert.equal(draft.part_rules[0].basis_reference, null);
});

test("part linkage uses exact declared IDs and failure explanation retains actual observables", () => {
  assert.deepEqual(
    partReferences(
      {
        id: "joint",
        definition: {
          ends: ["panel", "rail"],
          basis: "bolt is mentioned in prose",
        },
      },
      parts,
    ),
    ["panel", "rail"],
  );
  const failures = failedObservables({
    checks: {
      deflection: {
        state: "failed",
        value: 0.006,
        limit: 0.005,
        unit: "m",
        basis: "Fixture only",
      },
      missing: { state: "unknown", value: null },
      contact: { state: "outside-domain", basis: "No valid contact" },
    },
  });
  assert.equal(failures.length, 2);
  assert.equal(failures[0].value, 0.006);
  assert.equal(failures[1].limit, null);
  assert.equal(
    failures.some((row) => row.name === "missing"),
    false,
  );
});

test("revision UI source choices require the exact candidate and physical definition", () => {
  const candidate = {
    id: "candidate-a",
    definition: {
      installed_register: { physical_definition_sha256: "a".repeat(64) },
    },
  };
  const applicable = {
    id: "source-a",
    state: "verified",
    applicability: {
      candidate_id: "candidate-a",
      definition_sha256: "a".repeat(64),
    },
  };
  assert.deepEqual(
    eligibleRevisionRecords(
      [
        applicable,
        {
          ...applicable,
          id: "another-candidate",
          applicability: {
            ...applicable.applicability,
            candidate_id: "candidate-b",
          },
        },
        {
          ...applicable,
          id: "another-definition",
          applicability: {
            ...applicable.applicability,
            definition_sha256: "b".repeat(64),
          },
        },
        { ...applicable, id: "unverified", state: "draft" },
      ],
      candidate,
    ),
    [applicable],
  );
  const link = new URL(
    revisionLink(
      {
        city: "samawah",
        project: "project-a",
        environment: "simulation",
        configuration_revision: "new-r2",
        baseline_sha256: "c".repeat(64),
      },
      { id: "new-job" },
      "http://localhost/docs/design-engine/?revision=old&lang=ar",
    ),
  );
  assert.equal(link.searchParams.get("project"), "project-a");
  assert.equal(link.searchParams.get("revision"), "new-r2");
  assert.equal(link.searchParams.get("baseline_sha256"), "c".repeat(64));
  assert.equal(link.searchParams.get("lang"), "ar");
});

test("project, baseline and part scope changes cannot inherit comparison or evidence context", () => {
  const identity = {
    city: "samawah",
    project: "project-a",
    environment: "simulation",
    configuration_revision: "r1",
    baseline_sha256: "a".repeat(64),
    run_id: null,
    asset_id: null,
    part_id: null,
  };
  assert.equal(exactResearchScope({ identity }, identity), true);
  for (const patch of [
    { project: "project-b" },
    { baseline_sha256: null },
    { part_id: "different-part" },
    { configuration_revision: "r2" },
  ])
    assert.equal(
      exactResearchScope({ identity: { ...identity, ...patch } }, identity),
      false,
    );
  assert.equal(
    exactResearchScope(
      { city: "samawah", environment: "simulation" },
      identity,
    ),
    false,
  );
});

test("operation prerequisites distinguish screening from native confirmation and optimisation", () => {
  const operations = {
    screen: { available: true, missing: [] },
    optimise: { available: false, missing: ["pymoo"] },
    confirm: { available: false, missing: ["CalculiX"] },
  };
  assert.equal(operationReadiness(operations, null, {}).available, true);
  assert.equal(
    operationReadiness(operations, null, { search: true }).available,
    false,
  );
  assert.equal(
    operationReadiness(operations, null, { refine: true }).available,
    false,
  );
  assert.equal(
    operationReadiness(null, { available: true }, {}).available,
    true,
  );
  assert.equal(
    operationReadiness(null, { available: true }, { search: true }).available,
    false,
  );
  assert.deepEqual(
    operationReadiness(operations, null, {
      search: true,
      refine: true,
    }).rows.map((row) => row.operation),
    ["screen", "optimise", "confirm"],
  );
});

test("every new guided form, scope and assembly string has English and Arabic text", () => {
  for (const labels of [
    inputLabels,
    assemblyLabels,
    scopeLabels,
    revisionLabels,
    operationLabels,
  ])
    for (const pair of Object.values(labels)) {
      assert.equal(pair.length, 2);
      assert.ok(pair[0].trim());
      assert.match(pair[1], /[\u0600-\u06ff]/);
    }
});

test("recursive iteration requires its own native preflight and fixed check-preserving tuning", () => {
  const operations = {
    screen: { available: true, missing: [] },
    optimise: { available: false, missing: ["pymoo"] },
    confirm: { available: true, missing: [] },
    iterate: { available: false, missing: ["Gmsh"] },
  };
  assert.deepEqual(
    requestedOperations({ iterate: true, search: true, refine: true }),
    ["screen", "iterate"],
  );
  assert.equal(
    operationReadiness(operations, null, { iterate: true }).available,
    false,
  );
  assert.equal(
    operationReadiness(
      { ...operations, iterate: { available: true, missing: [] } },
      null,
      { iterate: true },
    ).available,
    true,
  );
  assert.equal(
    operationReadiness(null, { available: true }, { iterate: true }).available,
    false,
  );
  for (const adapter of ["mechanical-cleat", "civil-steel-beam"])
    assert.deepEqual(recursiveTuning({ adapter }), {
      evaluations: 32,
      iterations: 32,
      confirmations: 12,
      finite_exhaustive: true,
    });
  assert.equal(recursiveTuning({ adapter: "panel" }).finite_exhaustive, false);
  assert.equal(
    "screening_checks" in recursiveTuning({ adapter: "panel" }),
    false,
  );
  assert.equal(
    "physical_checks" in recursiveTuning({ adapter: "panel" }),
    false,
  );
});
