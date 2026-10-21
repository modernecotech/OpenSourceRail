// Browser acceptance for the static primary study; no external requests or live I/O.
import { chromium } from "@playwright/test";
import { spawn } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { gunzipSync } from "node:zlib";
import { createHash } from "node:crypto";
import assert from "node:assert/strict";

const root = resolve(import.meta.dirname, "../../..");
const output = resolve(process.argv[2] || "/tmp/osr-maglev-browser");
await mkdir(output, { recursive: true });
const server = spawn(
  "python3",
  ["-m", "http.server", "0", "--bind", "127.0.0.1", "--directory", root],
  {
    stdio: ["ignore", "pipe", "pipe"],
    env: { ...process.env, PYTHONUNBUFFERED: "1" },
  },
);
let browser;
try {
  const port = await new Promise((accept, reject) => {
    const timer = setTimeout(
      () => reject(new Error("HTTP startup timeout")),
      10000,
    );
    server.stdout.on("data", (chunk) => {
      const match = String(chunk).match(/port (\d+)/);
      if (match) {
        clearTimeout(timer);
        accept(Number(match[1]));
      }
    });
    server.once("exit", (code) => {
      clearTimeout(timer);
      reject(new Error(`HTTP exit ${code}`));
    });
  });
  browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1000 },
  });
  const errors = [],
    external = [],
    failures = [];
  page.on("pageerror", (error) => errors.push(String(error)));
  page.on("requestfailed", (req) => failures.push(req.url()));
  page.on("request", (req) => {
    if (!req.url().startsWith(`http://127.0.0.1:${port}/`))
      external.push(req.url());
  });
  const response = await page.goto(
    `http://127.0.0.1:${port}/docs/design-engine/ferrite-maglev/reference/index.html`,
  );
  assert.equal(response.status(), 200);
  await page.locator("img").last().waitFor();
  await page.waitForFunction(() =>
    [...document.images].every((image) => image.complete),
  );
  const images = await page.locator("img").evaluateAll((nodes) =>
    nodes.map((n) => ({
      src: n.getAttribute("src"),
      loaded: n.complete && n.naturalWidth > 0,
    })),
  );
  const expectedImages = [
    "../baghdad-reference/station/overview.png",
    "guidebeam-sections.svg",
    "duty-energy.svg",
    "../native/interface/overview.png",
    "../native/interface/cartridge-detail.png",
    "../native/civil-bay/overview.png",
    "field-study.png",
    "../beam-only/overview.png",
    "evacuation-envelope.svg",
    "../system-development/entry/overview.png",
    "../system-development/compact-support/overview.png",
    "../station-native/overview.png",
    "../station-powered/overview.svg",
    "../station-powered/power.svg",
    "../station-structure/comparison.svg",
    "../iterative/progress.svg",
  ];
  assert.deepEqual(
    images.map((image) => image.src).sort(),
    expectedImages.sort(),
  );
  assert.equal(images.length, 16);
  assert.ok(images.every((i) => i.loaded));
  assert.match(await page.locator("h1").innerText(), /Ferrite-maglev/);
  const origin = `http://127.0.0.1:${port}`;
  const report = `${origin}/docs/design-engine/ferrite-maglev/reference/`;
  const assets = new Map();
  async function asset(relative) {
    const url = new URL(relative, report);
    assert.equal(url.origin, origin, "report assets must stay local");
    if (!assets.has(url.href)) {
      const linked = await page.request.get(url.href);
      assert.equal(
        linked.status(),
        200,
        `missing report asset: ${url.pathname}`,
      );
      assets.set(url.href, {
        pathname: url.pathname,
        status: linked.status(),
        contentType: linked.headers()["content-type"],
        body: await linked.body(),
      });
    }
    return assets.get(url.href);
  }
  async function jsonAsset(relative) {
    return JSON.parse((await asset(relative)).body.toString("utf8"));
  }
  const data = await jsonAsset("result.json");
  assert.equal(data.version, "0.5.2");
  const digest = body => createHash("sha256").update(body).digest("hex");
  async function checkedPacket(relative) {
    const manifest = await jsonAsset(relative+"manifest.json");
    assert.ok(Object.keys(manifest.files_sha256).length > 0);
    for (const [name, expected] of Object.entries(manifest.files_sha256)) {
      assert.match(expected,/^[a-f0-9]{64}$/);
      assert.ok(!name.startsWith("/") && !name.split("/").includes(".."));
      assert.equal(digest((await asset(relative+name)).body),expected,relative+name);
    }
    const sources=manifest.sources_sha256 || manifest.source_sha256;
    assert.ok(sources && Object.keys(sources).length>0);
    for (const [name,expected] of Object.entries(sources)) {
      assert.ok(!name.startsWith("/") && !name.split("/").includes(".."));
      assert.equal(digest((await asset("/"+name)).body),expected,"stale source "+name);
    }
    for(const flag of ["design_complete","physical_validation","manufacturing_release","physical_release"])
      assert.equal(manifest[flag],false);
    return manifest;
  }
  const stationPoweredManifest=await checkedPacket("../station-powered/");
  const stationPowered=JSON.parse(gunzipSync((await asset("../station-powered/result.json.gz")).body).toString("utf8"));
  assert.deepEqual(stationPowered.source_sha256,stationPoweredManifest.sources_sha256);
  assert.deepEqual(stationPowered.cases.map(row=>row.name),["reference-90s","economy-100s","uphill-2-percent","uphill-5-percent","downhill-5-percent"]);
  const operation=data.station_powered, trajectory=operation.trajectory;
  assert.equal(trajectory.inputs.cars,6);
  assert.equal(trajectory.inputs.car_mass_kg,26200);
  assert.equal(trajectory.inputs.train_mass_kg,157200);
  assert.equal(trajectory.inputs.distance_m,1000);
  assert.equal(trajectory.inputs.runtime_s,90);
  assert.equal(trajectory.inputs.jerk_m_s3,.6);
  assert.equal(trajectory.energy_balance.passed,true);
  assert.ok(Math.abs(trajectory.energy_balance.residual_j)<1);
  assert.ok(trajectory.phases.coast.distance_m>0);
  assert.ok(Math.abs(Object.values(trajectory.phases).reduce((sum,phase)=>sum+phase.distance_m,0)-1000)<1e-5);
  const coast=trajectory.trace.filter(row=>row.phase==="coast");
  assert.ok(coast.length>10);
  assert.ok(coast.every(row=>row.motor_force_n===0 && row.mechanical_kw===0));
  assert.ok(Math.abs(trajectory.peak_traction_input_kw-2346)<5);
  assert.equal(operation.charging.moving_services_kwh,9);
  assert.equal(operation.charging.disconnected_dwell_s,15);
  assert.equal(operation.charging.battery_supplied_seconds_per_cycle,105);
  assert.equal(operation.charging.replacement_kwh_per_train,10.5);
  assert.equal(operation.charging.battery_charging_kw_per_train,840);
  assert.equal(operation.charging.connected_interface_kw_per_train,1200);
  assert.equal(operation.charging.charger_losses_included,false);
  assert.equal(operation.battery.gross_kwh_per_car,30);
  assert.equal(operation.battery.accepted,false);
  assert.equal(operation.traffic.scheduled_headway_s,190);
  assert.ok(operation.traffic.planning_headway_margin_s>10);
  assert.equal(operation.traffic.timer_is_clearance_proof,false);
  assert.equal(operation.traffic.release_requires_positive_full_consist_evidence,true);
  assert.equal(operation.magnetic_overlap.magnetic_bands_relative_to_front_m.length,6);
  assert.equal(operation.magnetic_overlap.installed_direction_m_per_two_direction_station,400);
  assert.equal(operation.magnetic_overlap.installed_face_m_per_two_direction_station,800);
  assert.equal(operation.magnetic_overlap.force_map_validated,false);
  assert.equal(operation.magnetic_overlap.engineering_force_reserve_accepted,false);
  assert.equal(operation.station_power.brake_reuse_credited,false);
  for(const name of ["uphill-5-percent","downhill-5-percent"]){
    const adverse=stationPowered.cases.find(row=>row.name===name).result;
    assert.equal(adverse.study_pass,false);
    assert.equal(adverse.status,"hold");
  }
  assert.equal(stationPowered.engineering_accepted_count,0);
  const structureManifest=await checkedPacket("../station-structure/");
  const structure=await jsonAsset("../station-structure/result.json");
  assert.equal(structure.source_epoch_sha256,structureManifest.source_epoch_sha256);
  const centralBody=structure.body_cases.find(row=>row.case==="central");
  assert.equal(centralBody.tare_target_kg,14200);
  assert.equal(centralBody.passenger_doors_per_car,4);
  assert.ok(Math.abs(centralBody.calculated_equipped_mass_kg-5198.0725)<1e-6);
  assert.equal(centralBody.complete_part_bom,false);
  assert.equal(centralBody.cg_m,null);
  assert.equal(structure.civil_families.length,5);
  const balanced=structure.civil_families.find(row=>row.id==="balanced-25m");
  assert.equal(balanced.qualified_foundation_selection,null);
  assert.ok(Math.abs(balanced.beam.concrete_m3-14.22)<1e-9);
  assert.ok(Math.abs(balanced.beam.concrete_plus_iron_kg-43055.856)<1e-6);
  assert.equal(structure.magnetic_screens.useful_rail_force_gain,null);
  assert.equal(structure.magnetic_screens.ring_reference.automatic_gain_credit,false);
  assert.ok(structure.magnetic_screens.linear_orientation_candidates.candidates.every(row=>row.support_force_n===null && row.propulsion_force_n===null));
  assert.equal(structure.production.conditional_route_m_per_planned_workday,56.25);
  assert.equal(structure.production.production_release_allowed,false);
  assert.ok(structure.production.strength_and_handover_gates.every(gate=>!gate.accepted));
  assert.ok(Math.abs(structure.civil_cost_comparison.target_listed_scope_usd-3313016.96)<1e-6);
  assert.equal(structure.civil_cost_comparison.complete_installed_price_usd,null);
  assert.equal(structure.civil_cost_comparison.costs_are_supplier_quotes,false);
  const stationNativeManifest=await checkedPacket("../station-native/");
  const stationNativeDefinition=await jsonAsset("../station-native/definition.json");
  const stationNativeReceipt=await jsonAsset("../station-native/native-cad.json");
  assert.equal(stationNativeReceipt.part_count,stationNativeDefinition.parts.length);
  assert.equal(stationNativeManifest.part_count,stationNativeDefinition.parts.length);
  assert.equal(stationNativeReceipt.input_sha256,digest((await asset("../station-native/definition.json")).body));
  assert.equal(stationNativeReceipt.fcstd_reopened,true);
  assert.equal(stationNativeReceipt.step_reopened,true);
  assert.equal(stationNativeManifest.complete_body_mass_modelled,false);
  assert.equal(stationNativeDefinition.qualified_foundation_selection,null);
  const protocolManifest=await checkedPacket("../station-protocol/");
  const protocol=await jsonAsset("../station-protocol/replay.json");
  assert.deepEqual(protocol.source_sha256,protocolManifest.source_sha256);
  assert.deepEqual(protocol.execution,protocolManifest.execution);
  assert.equal(protocol.binary_sha256,protocolManifest.binary_sha256);
  assert.match(protocol.binary_sha256,/^[a-f0-9]{64}$/);
  assert.equal(protocol.release_authority,false);
  const controller=protocol.controller_replay;
  const requiredControllerChecks=["launch","replay_rejected","stale_phase_rejected","zero_thrust_coast","resistor_braking","receiver_fault_requires_independent_recovery","uncommitted_launch_rejected","insufficient_overlap_rejected","physical_outputs_disabled_and_support_preserved"];
  assert.deepEqual(Object.keys(controller.checks).sort(),requiredControllerChecks.sort());
  assert.ok(Object.values(controller.checks).every(value=>value===true));
  assert.equal(controller.all_passed,true);
  assert.equal(controller.physical_output_authorised,false);
  assert.equal(controller.measured_motor_map,false);
  const execution=JSON.parse(gunzipSync((await asset("../station-protocol/executed-tests.txt.gz")).body).toString("utf8"));
  assert.deepEqual(Object.keys(execution).sort(),["build","compiler","run","tests"]);
  for(const [name,entry] of Object.entries(execution)){
    assert.equal(entry.returncode,0);
    assert.equal(protocol.execution[name].stdout_sha256,digest(Buffer.from(entry.stdout)));
    assert.equal(protocol.execution[name].stderr_sha256,digest(Buffer.from(entry.stderr)));
  }
  assert.ok(execution.build.command.includes("station_replay"));
  assert.ok(execution.tests.command.includes("station_launch"));
  assert.ok(protocol.required_executed_tests.length>=13);
  for(const name of protocol.required_executed_tests)
    assert.ok(execution.tests.stdout.includes("test "+name+" ... ok"),name);
  assert.match(execution.tests.stdout,/test result: ok\. 13 passed; 0 failed/);
  assert.equal(data.source_specification.requirements.length,100);
  assert.equal(data.source_specification.accepted_requirements,0);
  assert.equal(digest((await asset("/"+data.source_specification.source)).body),data.source_specification.source_sha256);
  assert.equal(data.applicable_requirements.requirements.length,179);
  assert.equal(data.applicable_requirements.accepted_requirements,0);
  assert.ok(data.applicable_requirements.requirements.every(row=>row.accepted===false));
  assert.equal(data.applicable_requirements.requirements.filter(row=>row.id.startsWith("SP-")).length,100);
  const adaptiveManifest = await jsonAsset("../iterative/manifest.json");
  const adaptiveRaw = await asset("../iterative/result.json.gz");
  assert.equal(createHash("sha256").update(adaptiveRaw.body).digest("hex"), adaptiveManifest.files_sha256["result.json.gz"]);
  const adaptive = JSON.parse(gunzipSync(adaptiveRaw.body).toString("utf8"));
  assert.ok(adaptive.selected_candidate_id);
  assert.ok(adaptive.history.length >= 2);
  const winner = adaptive.candidates.find(r => r.candidate_id === adaptive.selected_candidate_id);
  assert.equal(winner.confirmation_state, "passed");
  assert.equal(winner.eligible_for_research_recommendation, true);
  assert.equal(adaptive.physical_release, false);
  assert.ok(adaptive.confirmations.find(r => r.candidate_id === winner.candidate_id).cases.every(c => c.passed));
  for (const flag of [
    "design_complete",
    "physical_validation",
    "manufacturing_release",
    "physical_release",
  ])
    assert.equal(data[flag], false);
  assert.equal(data.civil_section_candidates.length, 27);
  assert.equal(data.localisation.local_fraction, null);
  assert.ok(data.gates.every((g) => g.accepted === false));
  assert.ok(data.transition_inventory.total_source_items > 0);
  assert.equal(data.requirements.length, data.transition_inventory.requirements);
  assert.equal(data.work_packages.length, data.transition_inventory.primary_work_packages);
  assert.equal(data.city_catalogue.city_count, 266);
  assert.equal(data.city_catalogue.catalogue_complete, true);
  assert.equal(data.city_catalogue.planning_acceptance, false);
  const optimisation = data.whole_system_optimisation;
  assert.equal(optimisation.candidate_count, 432);
  assert.ok(optimisation.numerical_screen_pass_count > 0);
  assert.equal(optimisation.acceptance_eligible_candidate_count, 0);
  assert.equal(optimisation.design_complete, false);
  assert.equal(optimisation.local_value_added_fraction, null);
  assert.ok(optimisation.unchanged_scope_floor_usd_dual_km > 0);
  assert.equal(optimisation.fully_coupled_optimisation, false);
  assert.equal(
    optimisation.research_extrema.fastest_construction_candidate_id,
    null,
  );
  assert.ok(
    optimisation.research_extrema.lowest_counted_concrete_mass_candidate_id,
  );
  const score =
    optimisation.minimum_indexed_allowance_candidate.system_scorecard;
  assert.equal(score.installed_cost_usd_dual_route_km, null);
  assert.equal(score.factory_gate_cost_usd_reference_train, null);
  assert.equal(score.moving_assemblies_count, null);
  assert.ok(score.hot_aw3_no_regen_cycle_kwh_per_car > 0);
  assert.equal(
    optimisation.beam_only_minimum_gross_allowance_candidate.system_scorecard
      .hot_aw3_no_regen_cycle_kwh_per_car,
    null,
  );
  assert.match(
    await page.locator("body").innerText(),
    /Whole-system comparison scorecards/,
  );
  assert.equal(optimisation.beam_only_candidate_count, 432);
  assert.equal(optimisation.beam_only_reference_champion_eligible, false);
  assert.equal(optimisation.beam_only_net_system_saving_usd, null);
  const beamOnlyDefinition=await jsonAsset("../beam-only/definition.json");
  assert.equal(data.onboard_evacuation.beam_only_part_count,beamOnlyDefinition.parts.length);
  assert.equal(data.onboard_evacuation.walkway_removal_approved, false);
  assert.equal(
    data.onboard_evacuation.operational_deployment_authorised,
    false,
  );
  const beamOnlyManifest = await jsonAsset("../beam-only/manifest.json");
  assert.equal(beamOnlyManifest.evacuation_accepted, false);
  assert.equal(beamOnlyManifest.walkway_removal_approved, false);
  assert.equal(beamOnlyManifest.manufacturing_release, false);
  const beamImage = await asset("../beam-only/overview.png");
  assert.equal(
    createHash("sha256").update(beamImage.body).digest("hex"),
    beamOnlyManifest.files_sha256["overview.png"],
  );
  const evacuation = JSON.parse(
    gunzipSync((await asset("evacuation-study.json.gz")).body).toString("utf8"),
  );
  assert.match(evacuation.preferred_candidate, /vertical-controlled-descent/);
  assert.deepEqual(
    evacuation.chute_envelopes.map((e) => e.height_m),
    [8, 12, 20, 30],
  );
  assert.equal(evacuation.chute_operating_height_approved_m, null);
  assert.equal(evacuation.chute_descent_simulation_performed, false);
  assert.equal(evacuation.onboard_installation_requirements.length, 7);
  assert.ok(
    evacuation.onboard_installation_requirements.every(
      (r) => !r.accepted && r.state === "open",
    ),
  );
  assert.equal(
    evacuation.variable_height_research.discrete_exit_counterexample.state,
    "rejected",
  );
  assert.equal(
    evacuation.variable_height_research.continuous_height_coverage_proved,
    false,
  );
  assert.equal(
    evacuation.chute_supplier_comparison[0]
      .installed_transport_reference_verified,
    false,
  );
  assert.ok(
    evacuation.chute_supplier_comparison.every(
      (s) => s.railway_accepted === false,
    ),
  );
  assert.ok(
    evacuation.chute_landing_cases
      .filter((c) => c.surface !== "controlled-safe-dry-ground")
      .every((c) => c.state === "rejected"),
  );
  assert.equal(
    evacuation.chute_outward_extended_standoff_path.assessment.state,
    "hold",
  );
  assert.equal(evacuation.procurement_and_lifetime_cost_usd, null);
  assert.equal(evacuation.net_system_saving_usd, null);
  assert.ok(
    evacuation.landing_cases
      .filter((c) => c.surface !== "controlled-safe-dry-ground")
      .every((c) => c.state === "rejected"),
  );
  assert.ok(evacuation.landing_cases.every((c) => c.accepted === false));

  const transition = JSON.parse(
    gunzipSync((await asset("systems-register.json.gz")).body).toString(
      "utf8",
    ),
  );
  assert.equal(transition.schema, "osr-ferrite-maglev-systems/1");
  assert.equal(transition.items.length, data.transition_inventory.total_source_items);
  assert.equal(new Set(transition.items.map((item) => item.id)).size, transition.items.length);
  assert.equal(transition.work_packages.length, data.work_packages.length);
  assert.equal(transition.accepted_item_count, 0);
  assert.equal(transition.accepted_physical_release_count, 0);
  assert.ok(
    transition.items.every((item) => !item.accepted && !item.physical_release),
  );

  const nativeManifest = await jsonAsset("../native/manifest.json");
  assert.equal(nativeManifest.schema, "osr-maglev-native-packet/1");
  assert.equal(nativeManifest.physical_release, false);
  assert.equal(nativeManifest.manufacturing_release, false);
  const nativeReceipts = [];
  for (const name of ["interface", "civil-bay"]) {
    const receipt = await jsonAsset(`../native/${name}/native-cad.json`);
    assert.equal(receipt.schema, "osr-factory-native-cad/1");
    assert.equal(receipt.fcstd_reopened, true);
    assert.equal(receipt.step_reopened, true);
    assert.equal(receipt.physical_release, false);
    assert.match(receipt.input_sha256, /^[a-f0-9]{64}$/);
    const definition=await jsonAsset(`../native/${name}/definition.json`);
    assert.equal(receipt.part_count,definition.parts.length);
    assert.equal(receipt.input_sha256,digest((await asset(`../native/${name}/definition.json`)).body));
    if(name==="interface") assert.equal(receipt.part_count,data.geometric_interface.parts);
    else assert.ok(receipt.part_count>0);
    nativeReceipts.push({
      name,
      part_count: receipt.part_count,
      reopened: true,
    });
  }
  const coupledReceipt = await jsonAsset("../coupled/receipt.json");
  const coupledAsset = await asset("../coupled/result.json");
  const coupled = JSON.parse(coupledAsset.body.toString("utf8"));
  assert.equal(coupledReceipt.schema, "osr-coupled-guideway-publication/1");
  assert.equal(coupled.schema, "osr-coupled-guideway-result/1");
  assert.deepEqual(coupled.source_sha256, coupledReceipt.source_sha256);
  assert.deepEqual(coupled.execution, coupledReceipt.execution);
  assert.match(coupledReceipt.execution.bridge_sha256, /^[a-f0-9]{64}$/);
  assert.ok(coupledReceipt.execution.build_command.includes("coupled_bridge"));
  assert.equal(
    createHash("sha256").update(coupledAsset.body).digest("hex"),
    coupledReceipt.files_sha256["result.json"],
  );
  assert.equal(coupled.coupled_replay.virtual_duration_s, 3);
  assert.equal(coupled.coupled_replay.retained_vertical_beam_modes, 6);
  assert.equal(coupled.coupled_replay.beam_assumptions.elements, 50);
  assert.equal(
    coupled.coupled_replay.status,
    "hypothetical-two-way-offline-cosimulation",
  );
  for (const record of [coupledReceipt, coupled, coupled.coupled_replay]) {
    assert.equal(record.physical_output_authorised, false);
    assert.equal(record.structural_acceptance, false);
  }
  const links = [];
  for (const href of await page
    .locator("a")
    .evaluateAll((nodes) => nodes.map((n) => n.href))) {
    const linked = await asset(href);
    links.push({ href: linked.pathname, status: linked.status });
  }
  const expectedVideos = [
    "../native/interface/assembly-visibility.mp4",
    "../native/civil-bay/assembly-visibility.mp4",
  ];
  expectedVideos.push(
    "../system-development/entry/assembly-visibility.mp4",
    "../system-development/compact-support/assembly-visibility.mp4",
  );
  expectedVideos.push("../baghdad-reference/station/assembly-visibility.mp4");
  expectedVideos.push("../station-native/assembly-visibility.mp4");
  const stationManifest = await jsonAsset("../baghdad-reference/manifest.json");
  const stationStudy = await jsonAsset("../baghdad-reference/study.json");
  assert.equal(stationStudy.cars_per_train,6);
  assert.equal(stationStudy.station.lift_threshold_step_m,0);
  assert.equal(stationStudy.station_installed_cost_usd,null);
  const systemManifest = await jsonAsset("../system-development/manifest.json");
  assert.equal(systemManifest.manufacturing_release, false);
  const development = data.linked_system_development;
  assert.equal(development.entry_hardware_part_count, 20);
  const supportStudyAsset=await asset("../system-development/study.json.gz");
  assert.equal(digest(supportStudyAsset.body),systemManifest.files_sha256["study.json.gz"]);
  const supportStudy=JSON.parse(gunzipSync(supportStudyAsset.body).toString("utf8"));
  assert.equal(development.support_case_count,supportStudy.support_case_count);
  assert.equal(development.support_case_count,supportStudy.support_cases.length);
  assert.deepEqual([...new Set(supportStudy.support_cases.map(row=>row.load_case))].sort(),
    ["both-trains","empty","one-beam-erection","one-train"]);
  assert.ok(supportStudy.support_cases.every(row=>row.accepted===false && row.capacity_utilisation===null));
  assert.equal(development.erection_working_days_saved, null);
  const replay = await jsonAsset("../system-development/software-replay.json");
  assert.equal(replay.physical_output_authorised, false);
  assert.equal(replay.cases.length, 4);
  assert.equal(replay.cases[0].replay.frames.at(-1).phase, "CompleteHold");
  for (const c of replay.cases.slice(1))
    assert.ok(
      c.replay.frames.every(
        (f) =>
          !["Ready", "DeploymentStudy", "FlowStudy", "CompleteHold"].includes(
            f.phase,
          ),
      ),
    );
  const matched = await jsonAsset(
    "../system-development/native-derived-coupling.json",
  );
  const civilDefinition=await jsonAsset("../native/civil-bay/definition.json");
  const span=data.inputs.civil.reference_span_m;
  const nativeLineMass=civilDefinition.parts.filter(part=>part.id.startsWith("beam-1/")).reduce((sum,part)=>sum+part.modelled_mass_kg,0)/span;
  assert.ok(Math.abs(matched.native_beam_line_mass_kg_m-nativeLineMass)<1e-5);
  assert.ok(Math.abs(nativeLineMass-1722.23424)<1e-5);
  assert.equal(
    matched.replay.beam_assumptions.line_mass_kg_m,
    matched.native_beam_line_mass_kg_m,
  );
  assert.equal(matched.complete_egress_system_included, false);
  assert.equal(matched.replay.car_mass_kg, matched.car_mass_kg);
  const referenceAw2=data.selected_configuration.configuration.vehicle.baseline_tare_kg_per_car+data.inputs.vehicle.aw2_passengers_per_car*data.inputs.vehicle.passenger_mass_screen_kg;
  assert.equal(referenceAw2,23200);
  assert.ok(Math.abs(matched.car_mass_kg-referenceAw2-matched.partial_entry_hardware_mass_added_kg)<1e-6);
  const videoLinks = await page
    .locator('a[href$=".mp4"]')
    .evaluateAll((nodes) => nodes.map((node) => node.getAttribute("href")));
  assert.deepEqual(videoLinks.sort(), expectedVideos.sort());
  const videos = [];
  for (const href of videoLinks) {
    const video = await asset(href);
    assert.match(video.contentType, /^video\/mp4(?:;|$)/);
    assert.ok(
      video.body.length > 1024,
      "assembly video must contain media bytes",
    );
    assert.equal(video.body.subarray(4, 8).toString("ascii"), "ftyp");
    const productVideo=href.startsWith("../station-native/");
    const stationVideo = href.startsWith("../baghdad-reference/");
    const systemVideo = href.startsWith("../system-development/");
    const name = href.replace(
      productVideo ? "../station-native/" : stationVideo ? "../baghdad-reference/" : systemVideo ? "../system-development/" : "../native/",
      "",
    );
    assert.equal(
      createHash("sha256").update(video.body).digest("hex"),
      (productVideo ? stationNativeManifest : stationVideo ? stationManifest : systemVideo ? systemManifest : nativeManifest).files_sha256[name],
    );
    videos.push({
      href: video.pathname,
      status: video.status,
      bytes: video.body.length,
    });
  }
  for (const image of images) {
    const loaded = await asset(image.src);
    assert.ok(loaded.body.length > 0);
    if (image.src.startsWith("../system-development/")) {
      const name = image.src.replace("../system-development/", "");
      assert.equal(
        createHash("sha256").update(loaded.body).digest("hex"),
        systemManifest.files_sha256[name],
      );
    }
    for(const [prefix,manifest] of [["../station-native/",stationNativeManifest],["../station-powered/",stationPoweredManifest],["../station-structure/",structureManifest],["../iterative/",adaptiveManifest]]){
      if(image.src.startsWith(prefix)) assert.equal(digest(loaded.body),manifest.files_sha256[image.src.slice(prefix.length)]);
    }
    if (image.src.startsWith("../native/")) {
      const name = image.src.replace("../native/", "");
      assert.equal(
        createHash("sha256").update(loaded.body).digest("hex"),
        nativeManifest.files_sha256[name],
      );
    }
  }
  await page.screenshot({
    path: resolve(output, "primary-study-desktop.png"),
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({
    path: resolve(output, "primary-study-mobile.png"),
    fullPage: true,
  });
  assert.equal(
    await page.evaluate(
      () => document.documentElement.scrollWidth > window.innerWidth,
    ),
    false,
  );
  assert.deepEqual(errors, []);
  assert.deepEqual(external, []);
  assert.deepEqual(failures, []);
  const proof = {
    version: data.version,
    images,
    videos,
    links,
    source_item_count: transition.items.length,
    work_package_count: transition.work_packages.length,
    city_count: data.city_catalogue.city_count,
    accepted_item_count: transition.accepted_item_count,
    native_receipts: nativeReceipts,
    station_powered: { charging_kw_per_train: operation.charging.connected_interface_kw_per_train, reference_headway_s:operation.traffic.scheduled_headway_s, grade_holds_retained:true, actual_protocol_checks:requiredControllerChecks.length, actual_protocol_tests:protocol.required_executed_tests.length, source_specification_requirements:data.source_specification.requirements.length, native_parts:stationNativeDefinition.parts.length, physical_release:false },
    coupled_receipt: {
      schema: coupledReceipt.schema,
      bridge_sha256: coupledReceipt.execution.bridge_sha256,
      virtual_duration_s: coupled.coupled_replay.virtual_duration_s,
      physical_output_authorised: false,
      structural_acceptance: false,
    },
    javascript_errors: errors,
    external_requests: external,
    failed_requests: failures,
    mobile_overflow: false,
    acceptance_gates_open: data.gates.length,
  };
  await writeFile(
    resolve(output, "browser-check.json"),
    JSON.stringify(proof, null, 2) + "\n",
  );
  process.stdout.write(JSON.stringify(proof, null, 2) + "\n");
} finally {
  if (browser) await browser.close();
  server.kill("SIGTERM");
}
