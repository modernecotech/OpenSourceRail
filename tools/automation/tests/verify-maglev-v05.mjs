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
    "../moving-train/overview.png",
    "../manufactured-native/overview.png",
    "../system-campaign/overview.svg",
    "../booster-kit/overview.svg",
    "../booster-native/overview.png",
    "../corridor/overview.svg",
    "../corridor/urban-overview.png",
    "../corridor/suburban-overview.png",
    "../interchange-hubs/overview.svg",
    "../line-capacity/overview.svg",
    "../hub-access/overview.svg",
    "../stopped-recovery/overview.svg",
    "../assembled-body/overview.png",
    "../assembled-body/frame-cutaway.png",
    "../assembled-body/six-car.png",
    "../shared-hub-layout/overview.svg",
    "../shared-hub-layout/station-plan.svg",
    "../shared-hub-layout/overview.png",
    "../body-stiffness/overview.svg",
  ];
  assert.deepEqual(
    images.map((image) => image.src).sort(),
    expectedImages.sort(),
  );
  assert.equal(images.length, expectedImages.length);
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
  assert.equal(data.operating_strategy.junction_operation,"passenger-transfer-between-fixed-lines");
  assert.equal(data.operating_strategy.urban_minimum_stop_spacing_m,1500);
  assert.equal(data.operating_strategy.urban_target_stop_spacing_m,2000);
  assert.equal(data.operating_strategy.suburban_minimum_stop_spacing_m,4000);
  assert.equal(data.operating_strategy.suburban_maximum_stop_spacing_m,5000);
  assert.equal(data.inputs.architecture.located_booster_powered_stator,true);
  assert.equal(data.inputs.architecture.interstation_continuous_powered_stator,false);
  assert.match(data.station_powered.evidence_role,/retained-1000m/);
  assert.match(data.moving_six_car.evidence_role,/retained-1000m/);
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
  // The supplied 90s/190s benchmark is preserved independently of the current
  // shared station/city profile. Neither may substitute for the other.
  const authored=stationPowered.cases.find(row=>row.name==="reference-90s").result;
  assert.equal(authored.trajectory.inputs.runtime_s,90);
  assert.equal(authored.traffic.scheduled_headway_s,190);
  assert.equal(authored.charging.connected_interface_kw_per_train,1200);
  assert.equal(authored.charging.charger_losses_included,false);
  const operation=data.station_powered, trajectory=operation.trajectory;
  const primary=data.inputs, selectedCivil=data.selected_configuration.configuration.civil;
  assert.equal(trajectory.inputs.cars,6);
  assert.equal(trajectory.inputs.car_mass_kg,26200);
  assert.equal(trajectory.inputs.train_mass_kg,157200);
  assert.equal(trajectory.inputs.distance_m,1000);
  assert.equal(trajectory.inputs.runtime_s,primary.vehicle.runtime_reference_seconds);
  assert.equal(trajectory.inputs.acceleration_m_s2,primary.vehicle.maximum_initial_acceleration_m_s2);
  assert.equal(trajectory.inputs.jerk_m_s3,primary.vehicle.jerk_study_m_s3);
  assert.equal(trajectory.energy_balance.passed,true);
  assert.ok(Math.abs(trajectory.energy_balance.residual_j)<1);
  assert.ok(trajectory.phases.coast.distance_m>0);
  assert.ok(Math.abs(Object.values(trajectory.phases).reduce((sum,phase)=>sum+phase.distance_m,0)-1000)<1e-5);
  const coast=trajectory.trace.filter(row=>row.phase==="coast");
  assert.ok(coast.length>10);
  assert.ok(coast.every(row=>row.motor_force_n===0 && row.mechanical_kw===0));
  const services=primary.power.hot_hotel_kw_per_car*trajectory.inputs.cars;
  assert.equal(operation.charging.disconnected_dwell_s,primary.power.station_dwell_seconds-primary.power.charger_effective_seconds);
  const batterySeconds=trajectory.inputs.runtime_s+operation.charging.disconnected_dwell_s;
  const replacement=services*batterySeconds/3600;
  assert.equal(operation.charging.battery_supplied_seconds_per_cycle,batterySeconds);
  assert.ok(Math.abs(operation.charging.replacement_kwh_per_train-replacement)<1e-9);
  const interfaceKW=replacement*3600/primary.power.charger_effective_seconds+services;
  assert.ok(Math.abs(operation.charging.connected_interface_kw_per_train-interfaceKW)<1e-8);
  assert.equal(operation.charging.charging_efficiency_assumption,primary.power.station_charger_efficiency_assumption);
  assert.ok(Math.abs(operation.charging.connected_input_kw_per_train-interfaceKW/primary.power.station_charger_efficiency_assumption)<1e-8);
  assert.equal(operation.charging.candidate_input_kw_per_train,6*primary.power.candidate_station_charger_kw_per_car);
  assert.equal(operation.charging.charger_losses_included,true);
  assert.equal(operation.charging.input_rating_screen_pass,true);
  assert.equal(operation.charging.charge_taper_and_repeated_duty_validated,false);
  assert.equal(operation.battery.gross_kwh_per_car,30);
  assert.equal(operation.battery.accepted,false);
  assert.equal(operation.traffic.scheduled_headway_s,primary.vehicle.scheduled_headway_seconds);
  assert.ok(operation.traffic.planning_headway_margin_s>=0);
  assert.equal(operation.traffic.timer_is_clearance_proof,false);
  assert.equal(operation.traffic.release_requires_positive_full_consist_evidence,true);
  assert.equal(operation.magnetic_overlap.magnetic_bands_relative_to_front_m.length,6);
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
  assert.ok(protocol.required_executed_tests.length>=11);
  for(const name of protocol.required_executed_tests)
    assert.ok(execution.tests.stdout.includes("test "+name+" ... ok"),name);
  assert.ok(execution.tests.stdout.includes(`test result: ok. ${protocol.required_executed_tests.length} passed; 0 failed`));
  assert.equal(data.source_specification.requirements.length,100);
  assert.equal(data.source_specification.accepted_requirements,0);
  assert.equal(digest((await asset("/"+data.source_specification.source)).body),data.source_specification.source_sha256);
  assert.equal(data.applicable_requirements.requirements.length,179);
  assert.equal(data.applicable_requirements.accepted_requirements,0);
  assert.ok(data.applicable_requirements.requirements.every(row=>row.accepted===false));
  assert.equal(data.applicable_requirements.requirements.filter(row=>row.id.startsWith("SP-")).length,100);
  const movingManifest=await checkedPacket("../moving-train/");
  const moving=JSON.parse(gunzipSync((await asset("../moving-train/result.json.gz")).body).toString("utf8"));
  const movingVisual=await jsonAsset("../moving-train/visual-receipt.json");
  assert.deepEqual(moving.source_sha256,movingManifest.source_sha256);
  assert.deepEqual(moving.execution,movingManifest.execution);
  const movingRun=moving.moving_run, movingAssumptions=movingRun.assumptions;
  assert.equal(moving.study_pass,true);
  assert.equal(movingRun.formation.cars,6);
  assert.equal(movingRun.formation.assumed_overall_length_m,104.5);
  assert.equal(movingRun.trajectory.inputs.runtime_s,primary.vehicle.runtime_reference_seconds);
  assert.equal(movingRun.trajectory.inputs.acceleration_m_s2,primary.vehicle.maximum_initial_acceleration_m_s2);
  assert.equal(movingAssumptions.guideway_span_m,selectedCivil.span_m);
  assert.equal(movingAssumptions.beam_section_m.depth,selectedCivil.depth_m);
  assert.equal(movingAssumptions.beam_modulus_pa,primary.civil.narrow_box_screen.gross_uncracked_concrete_e_pa);
  assert.equal(movingRun.completed_moving_steps,movingRun.planned_moving_steps);
  assert.ok(movingRun.completed_moving_steps>10000);
  assert.equal(movingRun.executed_duration_s,movingRun.trajectory.inputs.runtime_s);
  assert.ok(movingRun.minimum_gap_m>=movingAssumptions.gap_minimum_m);
  assert.ok(movingRun.maximum_gap_m<=movingAssumptions.gap_maximum_m);
  assert.ok(movingRun.maximum_magnetic_phase_spread_degrees<=5);
  assert.ok(movingRun.longitudinal_energy.relative_residual<1e-5);
  assert.ok(movingRun.load_projection_virtual_power_relative_error<1e-10);
  for(const name of ["independent_moving_load_solution","moving_load_refines","coupler_energy_conservation","coupler_internal_momentum","replayed_frame_rejected","out_of_envelope_gap_rejected","two_way_feedback_negative_control","moving_train_time_refinement","full_run_longitudinal_work_balance","mandatory_adverse_confirmations","physical_gap_bias_counterexample_rejected","sensed_and_physical_gap_bias_consistent"])
    assert.equal(moving.numerical_controls[name],true,name);
  assert.equal(moving.reference_run.study_pass,false);
  assert.equal(moving.disconnected_feedback_negative_control.study_pass,false);
  assert.equal(moving.excessive_sensor_bias_negative_control.study_pass,false);
  assert.deepEqual(moving.mandatory_confirmation_roles,["reduced-stiffness","reduced-stiffness-positive-bias","reduced-stiffness-negative-bias"]);
  for(const role of moving.mandatory_confirmation_roles){
    const confirmation=moving.candidates.find(row=>row.assumptions.candidate_role===role);
    assert.equal(confirmation.study_pass,true,role);
    assert.equal(confirmation.completed_moving_steps,confirmation.planned_moving_steps);
    assert.equal(confirmation.assumptions.beam_modulus_pa,movingAssumptions.beam_modulus_pa*movingAssumptions.beam_modulus_adverse_factor);
    for(const sample of confirmation.trace){
      assert.ok(Math.abs(sample.minimum_sensed_gap_m-sample.minimum_gap_m-confirmation.sensor_bias_m)<1e-10);
      assert.ok(Math.abs(sample.maximum_sensed_gap_m-sample.maximum_gap_m-confirmation.sensor_bias_m)<1e-10);
    }
  }
  assert.equal(moving.shared_field_phase_registration_accepted,false);
  assert.equal(movingRun.structural_acceptance,false);
  assert.equal(movingRun.physical_output_authorised,false);
  assert.equal(movingVisual.candidate_sha256,movingRun.candidate_sha256);
  assert.equal(movingVisual.vertical_displacement_amplification,movingAssumptions.visual_vertical_amplification);
  assert.equal(movingVisual.renderer_sha256,movingManifest.source_sha256['engineering/ferrite_maglev/moving_train.py']);
  const campaignManifest=await checkedPacket("../system-campaign/");
  const campaign=JSON.parse(gunzipSync((await asset("../system-campaign/result.json.gz")).body).toString("utf8"));
  const campaignExecution=JSON.parse(gunzipSync((await asset("../system-campaign/executed.json.gz")).body).toString("utf8"));
  assert.deepEqual(campaign.source_sha256,campaignManifest.source_sha256);
  assert.match(campaign.binary_sha256,/^[a-f0-9]{64}$/);
  assert.equal(campaign.numerical_study_pass,true);
  assert.deepEqual(campaign.cases.map(row=>row.case),["nominal","receiver","sensor","drive","resistor","stale","phase","uncommitted"]);
  assert.equal(campaignExecution.build.returncode,0);
  assert.ok(campaignExecution.build.command.includes('station_campaign'));
  for(const row of campaign.cases){
    assert.equal(row.passed,true);
    const executed=campaignExecution[row.case];
    assert.equal(executed.returncode,0);
    const sent=JSON.parse(executed.stdin),observed=JSON.parse(executed.stdout);
    assert.equal(observed.observations.length,row.frames);
    assert.equal(sent.frames.length,row.frames);
    assert.equal(observed.physical_output_authorised,false);
    for(const [index,frame] of observed.observations.entries()){
      assert.equal(frame.physical_output_authorised,false);
      assert.equal(frame.support_shutdown_requested,false);
      assert.equal(frame.sequence,sent.frames[index].sequence);
      assert.ok(Math.abs(frame.airgap_electrical_power_w-frame.mechanical_power_w)<=Math.max(1e-5,Math.abs(frame.mechanical_power_w)*1e-10));
      if(sent.frames[index].mode===1 || sent.frames[index].mode===3)assert.equal(frame.force_n,0);
    }
  }
  assert.equal(campaign.resource_headway.timer_is_clearance_proof,false);
  assert.equal(campaign.resource_headway.screen_pass,true);
  assert.equal(campaign.measured_motor_map,false);
  assert.equal(campaign.cross_controller_handover_implemented,false);
  assert.ok(campaign.emergency_brake_cases.every(row=>row.screen_pass && !row.engineering_accepted));
  assert.ok(campaign.emergency_brake_cases.some(row=>row.failed_units===1));
  assert.equal(campaign.recovery.battery_energy_screen_pass,true);
  const dossierManifest=await checkedPacket("../manufactured-dossier/");
  const dossier=JSON.parse(gunzipSync((await asset("../manufactured-dossier/dossier.json.gz")).body).toString("utf8"));
  assert.deepEqual(dossier.source_sha256,dossierManifest.source_sha256);
  assert.equal(dossier.closure.requirement_count,data.applicable_requirements.requirements.length);
  assert.equal(dossier.closure.accepted_requirements,0);
  assert.equal(dossier.closure.system_count,53);
  assert.ok(dossier.closure.requirements.every(row=>row.deliverable_ids.length && row.concrete_deliverables.length && row.missing_evaluators_or_external_tests.length && !row.accepted));
  assert.equal(dossier.complete_manufactured_system,false);
  assert.equal(dossier.independent_acceptance,false);
  assert.equal(dossier.primary_frame_families.defined_member_piece_count,63);
  assert.ok(dossier.primary_frame_families.frame_budget_overrun_kg>0);
  const reserve=dossier.primary_frame_families.reserve_allocation;
  const benchmarkEmergency=campaign.emergency_brake_cases.find(row=>row.friction_coefficient_assumption===.25 && row.failed_units===0);
  const emergency=dossier.emergency_brake_case;
  assert.equal(dossier.primary_mass_case.car_mass_kg,26400);
  assert.equal(dossier.primary_mass_case.train_mass_kg,158400);
  assert.equal(dossier.primary_mass_case.tare_kg_per_car,14400);
  assert.equal(emergency.train_mass_kg,158400);
  assert.equal(dossier.retained_30kwh_benchmark.emergency_brake_case.train_mass_kg,benchmarkEmergency.train_mass_kg);
  assert.equal(dossier.retained_30kwh_benchmark.emergency_brake_case.brake_energy_j,benchmarkEmergency.brake_energy_j);
  assert.equal(reserve.additional_pack_mass_already_in_tare_kg,200);
  assert.equal(reserve.nominal_tare_including_existing_reserve_kg,14400);
  assert.ok(Math.abs(reserve.separately_proposed_emergency_kg-emergency.added_mass_kg_per_car)<1e-8);
  assert.ok(Math.abs(reserve.existing_kg-reserve.frame_overrun_kg-reserve.separately_proposed_emergency_kg-reserve.remaining_before_other_system_growth_kg)<1e-8);
  assert.equal(reserve.reserve_is_new_mass_credit,false);
  assert.equal(dossier.moving_profile_candidate.depth_m,selectedCivil.depth_m);
  assert.equal(dossier.moving_profile_candidate.runtime_s,primary.vehicle.runtime_reference_seconds);
  assert.ok(dossier.coupler_detail.assumed_peak_pair_force_n>=movingRun.peak_coupler_force_n);
  assert.equal(dossier.coupler_detail.full_assembly_stiffness_qualified,false);
  assert.equal(dossier.emergency_and_curve_load_path.qualified_foundation_selection,null);
  assert.ok(dossier.foundation_cost_delta.incremental_support_allowance_usd>0);
  assert.equal(dossier.foundation_cost_delta.costs_are_supplier_quotes,false);
  const detailManifest=await checkedPacket("../manufactured-native/");
  const detailDefinition=await jsonAsset("../manufactured-native/definition.json");
  const detailReceipt=await jsonAsset("../manufactured-native/native-cad.json");
  assert.equal(detailReceipt.part_count,detailDefinition.parts.length);
  assert.equal(detailManifest.part_count,detailDefinition.parts.length);
  assert.equal(detailReceipt.input_sha256,digest((await asset("../manufactured-native/definition.json")).body));
  assert.equal(detailReceipt.fcstd_reopened,true);
  assert.equal(detailReceipt.step_reopened,true);
  assert.equal(detailDefinition.complete_body_or_system_modelled,false);
  assert.equal(detailDefinition.modelled_cg_m,null);
  assert.deepEqual(detailDefinition.interference_roles,[]);
  const boosterManifest=await checkedPacket("../booster-kit/");
  const booster=JSON.parse(gunzipSync((await asset("../booster-kit/result.json.gz")).body).toString("utf8"));
  assert.deepEqual(booster.source_sha256,boosterManifest.source_sha256);
  const accelerator=booster.booster_cases.find(row=>row.length_per_direction_m===375);
  assert.equal(accelerator.passenger_station,false);
  assert.equal(accelerator.face_cassettes,600);
  assert.equal(accelerator.mount_bolts,2400);
  assert.equal(accelerator.additional_ordinary_beams_credited,0);
  const recoveryCases=booster.suburban_5km_300s_recovery_cases;
  const oldRecovery=recoveryCases.find(row=>row.pack_kwh_per_car===30 && row.maximum_rescue_node_spacing_m===2500 && row.tow_speed_m_s===.5);
  assert.equal(oldRecovery.numerical_feasible,false);
  assert.ok(oldRecovery.battery_margin_kwh_per_car<0);
  const independentRecovery=recoveryCases.find(row=>row.pack_kwh_per_car===30 && row.maximum_rescue_node_spacing_m===1000 && row.tow_speed_m_s===.5);
  assert.equal(independentRecovery.numerical_feasible,true);
  assert.ok(independentRecovery.quantities.rope_kg>0 && independentRecovery.quantities.foundation_concrete_m3>0);
  assert.ok(independentRecovery.listed_kit_target_usd>0);
  assert.equal(independentRecovery.complete_installed_price_usd,null);
  assert.equal(independentRecovery.qualified_foundation_selection,null);
  assert.equal(independentRecovery.physical_rescue_accepted,false);
  assert.equal(independentRecovery.rope.negative_control_pass,false);
  const boosterNativeManifest=await checkedPacket("../booster-native/");
  const boosterDefinition=await jsonAsset("../booster-native/definition.json");
  const boosterReceipt=await jsonAsset("../booster-native/native-cad.json");
  assert.equal(boosterReceipt.part_count,boosterDefinition.parts.length);
  assert.equal(boosterNativeManifest.part_count,boosterDefinition.parts.length);
  assert.equal(boosterReceipt.input_sha256,digest((await asset("../booster-native/definition.json")).body));
  assert.equal(boosterReceipt.fcstd_reopened,true);
  assert.equal(boosterReceipt.step_reopened,true);
  assert.equal(boosterDefinition.complete_body_or_system_modelled,false);
  assert.deepEqual(boosterDefinition.interference_roles,[]);
  const corridorManifest=await checkedPacket("../corridor/");
  const corridorResult=JSON.parse(gunzipSync((await asset("../corridor/result.json.gz")).body).toString("utf8"));
  assert.equal(corridorManifest.physical_release,false);
  assert.equal(corridorResult.schema,"osr-fixed-corridor-study/1");
  assert.deepEqual(corridorResult.source_sha256,corridorManifest.source_sha256);
  assert.equal(corridorResult.configuration_revision,moving.configuration_revision);
  assert.equal(corridorResult.executed_numerical_study_pass,true);
  assert.equal(corridorResult.study_pass,false);
  assert.equal(corridorResult.capacity_accepted,false);
  assert.equal(data.corridor_powered.manifest_sha256,digest((await asset("../corridor/manifest.json")).body));
  for(const [mode,distance,runtime,charger,dwell] of [["urban",2000,140,400,60],["suburban",5000,375,600,96]]){
    const screen=corridorResult.operations[mode];
    assert.equal(screen.distance_m,distance);assert.equal(screen.runtime_s,runtime);
    assert.equal(screen.service_energy.battery_kwh_per_car,50);
    assert.equal(screen.service_energy.charger_kw_per_car,charger);assert.equal(screen.service_energy.dwell_s,dwell);
    for(const key of ["motion_screen_pass","rating_screen_pass","service_energy_screen_pass","protection_screen_pass","operational_geometry_confirmed"])assert.equal(screen[key],true,mode+key);
    assert.equal(screen.capacity_screen_pass,false);
    assert.ok(screen.headway_lower_bound_s>180);
    assert.ok(screen.installed_zones.filter(zone=>zone.kind==="station").every(zone=>zone.length_m===350));
    if(mode==="suburban"){
      const topup=screen.installed_zones.find(zone=>zone.kind==="top-up");
      assert.equal(topup.passenger,false);assert.equal(topup.length_m,375);
    }
    for(const role of ["nominal","reduced-E-positive-bias","reduced-E-negative-bias"]){
      const run=corridorResult.moving[mode+"/"+role].run;
      assert.equal(run.study_pass,true);assert.equal(run.completed_moving_steps,run.planned_moving_steps);
      assert.equal(run.formation.cars,6);assert.equal(run.trajectory.inputs.runtime_s,runtime);
      assert.equal(run.assumptions.beam_section_m.depth,selectedCivil.depth_m);
      assert.ok(run.minimum_gap_m>=run.assumptions.gap_minimum_m && run.maximum_gap_m<=run.assumptions.gap_maximum_m);
      assert.equal(run.physical_output_authorised,false);assert.equal(run.structural_acceptance,false);
    }
    for(const load of ["AW0","AW2","AW3"]){
      const replay=corridorResult.replays[mode+"/"+load];
      assert.equal(replay.executed,true);assert.equal(replay.exit_status,0);assert.equal(replay.expected_behavior_pass,true);
      assert.equal(replay.raw_replay.executed_frames,replay.frames_requested);
      assert.equal(replay.raw_replay.physical_output_authorised,false);
      assert.ok(replay.raw_replay.power_conservation_max_residual_w<1e-6);
    }
    const visual=await jsonAsset(`../corridor/${mode}-visual-receipt.json`);
    assert.equal(visual.candidate_sha256,corridorResult.moving[mode+"/nominal"].run.candidate_sha256);
    assert.equal(visual.renderer_sha256,corridorManifest.source_sha256['engineering/ferrite_maglev/moving_train.py']);
    assert.equal(visual.files_sha256['overview.png'],corridorManifest.files_sha256[mode+'-overview.png']);
    assert.equal(visual.files_sha256['moving-train.mp4'],corridorManifest.files_sha256[mode+'-motion.mp4']);
  }
  for(const [name,replay] of Object.entries(corridorResult.replays)){
    assert.equal(replay.expected_behavior_pass,true,name);
    if(replay.fault!==null){assert.equal(replay.raw_replay.fault_held,true);assert.equal(replay.raw_replay.incoming_cleared,false);}
  }
  assert.equal(corridorResult.moving['suburban/rejected-2.2m'].run.study_pass,false);
  for(const load of ['AW0','AW2'])assert.equal(corridorResult.faster_load_holds[load].motion_screen_pass,false);

  const hubsManifest=await checkedPacket('../interchange-hubs/');
  const hubs=JSON.parse(gunzipSync((await asset('../interchange-hubs/study.json.gz')).body).toString('utf8'));
  assert.deepEqual(hubs.source_sha256,hubsManifest.source_sha256);
  assert.equal(hubs.schema,'osr-interchange-hub-investigation/1');
  assert.equal(hubs.true_compact_candidate_count,0);
  assert.ok(hubs.variants.length>0 && hubs.coordinated_realignment_concepts.length>0);
  assert.ok(hubs.network_alternatives.every(row=>row.selected===false && row.cost_savings_proved===false && row.complete_net_cost_delta_usd===null));
  for(const concept of hubs.coordinated_realignment_concepts){
    assert.equal(concept.selected,false);assert.equal(concept.train_routing_switches,0);
    assert.equal(concept.actual_internal_transfer_walk_m,null);
    assert.equal(concept.compact_walk_benchmark_assumption.is_computed_layout,false);
    for(const line of concept.line_proposals){
      assert.deepEqual(line.local_chord_coordinates[1],concept.shared_hub_coordinate);
      assert.equal(line.station_tangent_fitted,false);assert.equal(line.old_price_reused,false);
      assert.equal(line.existing_civil_classification_reused,false);
    }
  }
  assert.equal(hubs.engineering_accepted,false);assert.equal(hubs.physical_release,false);
  assert.ok((await page.locator('body').innerText()).includes(`default Baghdad reference remains ${hubs.baseline.operating_station_count} proposed stops`));

  const closureManifests={};
  for(const [folder,key] of [['line-capacity','line_capacity'],['hub-access','hub_access'],['qualification','qualification'],['assembled-body','assembled_body'],['shared-hub-layout','shared_hub_layout'],['body-stiffness','body_stiffness'],['stopped-recovery','stopped_recovery']]){
    const manifest=await checkedPacket('../'+folder+'/');
    closureManifests[folder]=manifest;
    const receipt=(await asset('../'+folder+'/manifest.json')).body;
    assert.equal(data.retained_evidence['docs/design-engine/ferrite-maglev/'+folder+'/manifest.json'],digest(receipt));
    const study=JSON.parse(gunzipSync((await asset('../'+folder+'/study.json.gz')).body).toString('utf8'));
    const boundSources=study.source_sha256 || study.binding.source_sha256;
    assert.deepEqual(boundSources,manifest.source_sha256);
    for(const flag of ['design_complete','physical_validation','manufacturing_release','physical_release']){
      assert.equal(study[flag],false);assert.equal(data.closure_studies[key][flag],false);
    }
    if(folder==='line-capacity'){
      assert.equal(study.executed_controls_pass,true);
      assert.equal(study.whole_line_capacity_accepted,false);
      assert.equal(study.city_default_changed,false);
      assert.ok(study.runs.length>=20 && study.runs.every(run=>run.control_pass===true));
      const summary=data.closure_studies[key];
      assert.equal(summary.legacy_station_launch.legacy_contract_changed,false);
      assert.equal(summary.legacy_station_launch.headway_180s_rejected_while_stopped,true);
      assert.equal(summary.legacy_station_launch.headway_600s_executed_pass,true);
      assert.equal(summary.progressive_departure.protocol,'osr-progressive-departure/1');
      assert.equal(summary.progressive_departure.restored_snapshot_can_authorise_motion,false);
      assert.equal(summary.progressive_departure.reconciliation_resumption_implemented,false);
      assert.ok(summary.progressive_departure.executed_api_tests>=12);
      for(const profile of summary.progressive_departure.profiles){
        assert.equal(profile.headway_s,180);assert.ok(profile.committed_departures>=3);
        assert.ok(profile.stopped_arrivals>0 && profile.full_tail_releases>0);
        assert.ok(profile.minimum_stopping_margin_m>=0 && profile.hold_stopping_margin_m>=0);
        assert.equal(profile.closed_arrival_brake_plant_pass,true);
      }
    }else if(folder==='stopped-recovery'){
      assert.equal(study.protocol,'osr-progressive-stopped-recovery/1');
      assert.equal(study.all_controls_pass,true);assert.equal(study.runs.length,44);
      assert.equal(study.old_contract_resumption,false);
      assert.equal(study.multi_controller_handover_implemented,false);
      assert.equal(study.authenticated_persistence_implemented,false);
      assert.equal(data.closure_studies[key].new_contract_required,true);
      assert.equal(data.closure_studies[key].successful_reconciliations,10);
      assert.equal(data.closure_studies[key].adverse_cases_rejected,34);
      assert.ok(study.runs.every(r=>r.result.snapshot_fenced && r.result.old_contracts_fenced && r.result.exact_event_replay_equal));
    }else if(folder==='qualification'){
      assert.equal(study.coverage.applicable_requirements,data.applicable_requirements.requirements.length);
      assert.equal(study.coverage.accepted_requirements,0);assert.equal(study.coverage.accepted_physical_gates,0);
      assert.deepEqual(study.coverage.uncovered_requirements,[]);assert.deepEqual(study.coverage.uncovered_groups,[]);
      assert.equal(study.coverage.gates,data.gates.length);
      assert.ok(study.coverage.protocols>=15 && study.tasks.length===study.topological_task_order.length);
    }else if(folder==='hub-access'){
      assert.equal(data.closure_studies[key].hub_selected,false);
      assert.ok(data.closure_studies[key].flow_scenarios>0 && data.closure_studies[key].lift_scenarios>0);
    }else if(folder==='assembled-body'){
      const summary=data.closure_studies[key];
      const mass=await jsonAsset('../'+folder+'/mass-properties.json');
      const legacy=await jsonAsset('../'+folder+'/legacy-collision-control.json');
      const native=await jsonAsset('../'+folder+'/native-cad.json');
      assert.equal(study.complete_equipped_vehicle,false);assert.equal(study.default_mass_or_stiffness_changed,false);
      assert.equal(summary.complete_equipped_vehicle,false);assert.equal(summary.default_mass_or_stiffness_changed,false);
      assert.equal(summary.part_count,study.part_count);assert.ok(summary.part_count>1000);
      assert.equal(native.fcstd_reopened,true);assert.equal(native.step_reopened,true);
      assert.equal(summary.all_defined_material_pairs_native_checked,true);assert.equal(summary.unintended_intersection_count,0);
      assert.equal(summary.defined_vehicle_material_mass_kg,mass.defined_vehicle_material_mass_kg);
      assert.deepEqual(summary.defined_vehicle_material_cg_m,mass.defined_vehicle_material_cg_m);
      assert.deepEqual(summary.defined_vehicle_material_inertia_kg_m2,mass.defined_vehicle_material_inertia_kg_m2);
      assert.equal(mass.whole_equipped_vehicle_mass_kg,null);assert.equal(mass.density_assumptions_are_measured,false);
      assert.equal(legacy.expected_failure_observed,true);assert.equal(legacy.eligible_for_assembled_adoption,false);
      assert.ok(legacy.total_common_volume_mm3>0 && legacy.collisions.length>0);
    }else if(folder==='body-stiffness'){
      const summary=data.closure_studies[key];
      assert.equal(summary.case_count,study.cases.length);assert.equal(summary.case_count,5);
      assert.equal(summary.selected_candidate_id,null);assert.equal(summary.automatic_adoption,false);
      assert.equal(summary.city_default_changed,false);assert.equal(summary.joined_body_accepted,false);
      assert.equal(summary.study_pass,false);assert.equal(summary.gfrp_control_above_phase_limit,true);
      assert.deepEqual(summary.cases,study.cases);
      assert.equal(summary.phase_screen_passing_alternatives,study.phase_screen_passing_alternative_ids.length);
      assert.ok(summary.phase_screen_passing_alternatives>0);
      assert.ok(summary.open_gates.length>0);
    }else if(folder==='shared-hub-layout'){
      const summary=data.closure_studies[key];
      assert.equal(summary.hub_selected,false);
      assert.equal(summary.variant_count,study.variant_count);
      assert.equal(summary.geometric_fit_count,study.geometric_fit_count);
      assert.equal(summary.representatives,study.representatives.length);
      assert.equal(summary.required_common_straight_m,study.stop_convention.required_common_straight_m);
      assert.equal(summary.common_platform_length_m,study.stop_convention.common_platform_length_m);
      assert.ok(study.alternatives.some(row=>!row.geometric_research_screen_pass));
      for(const row of study.representatives){
        assert.equal(row.selected,false);
        for(const paths of row.circulation.platform_pair_walks){
          assert.equal(paths.routed_door_pairs,paths.required_door_pairs);
          assert.ok(paths.maximum_horizontal_walk_m>=paths.minimum_horizontal_walk_m && paths.minimum_horizontal_walk_m>=0);
        }
      }
    }
  }

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
  assert.equal(data.civil_section_candidates.length, 45);
  assert.equal(data.localisation.local_fraction, null);
  assert.ok(data.gates.every((g) => g.accepted === false));
  assert.ok(data.transition_inventory.total_source_items > 0);
  assert.equal(data.requirements.length, data.transition_inventory.requirements);
  assert.equal(data.work_packages.length, data.transition_inventory.primary_work_packages);
  assert.equal(data.city_catalogue.city_count, 266);
  assert.equal(data.city_catalogue.catalogue_complete, true);
  assert.equal(data.city_catalogue.planning_acceptance, false);
  const optimisation = data.whole_system_optimisation;
  assert.equal(optimisation.candidate_count, 720);
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
  assert.equal(optimisation.beam_only_candidate_count, 720);
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
  expectedVideos.push("../station-native/assembly-visibility.mp4", "../moving-train/moving-train.mp4", "../manufactured-native/assembly-visibility.mp4", "../booster-native/assembly-visibility.mp4", "../corridor/urban-motion.mp4", "../corridor/suburban-motion.mp4");
  expectedVideos.push("../assembled-body/assembly-visibility.mp4");
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
  assert.ok(nativeLineMass>0);
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
    const mediaPackets=[["../station-native/",stationNativeManifest],["../moving-train/",movingManifest],["../manufactured-native/",detailManifest],["../booster-native/",boosterNativeManifest],["../corridor/",corridorManifest],["../baghdad-reference/",stationManifest],["../system-development/",systemManifest],["../native/",nativeManifest],["../assembled-body/",closureManifests['assembled-body']]];
    const [prefix,manifest]=mediaPackets.find(([prefix])=>href.startsWith(prefix)) || [];
    assert.ok(prefix,"video has no source-bound packet");
    assert.equal(digest(video.body),manifest.files_sha256[href.slice(prefix.length)]);
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
    for(const [prefix,manifest] of [["../station-native/",stationNativeManifest],["../station-powered/",stationPoweredManifest],["../station-structure/",structureManifest],["../iterative/",adaptiveManifest],["../moving-train/",movingManifest],["../manufactured-native/",detailManifest],["../system-campaign/",campaignManifest],["../booster-kit/",boosterManifest],["../booster-native/",boosterNativeManifest],["../corridor/",corridorManifest]]){
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
    station_powered: { charging_kw_per_train: operation.charging.connected_interface_kw_per_train, selected_headway_s:operation.traffic.scheduled_headway_s, authored_headway_s:authored.traffic.scheduled_headway_s, authored_charging_kw:authored.charging.connected_interface_kw_per_train, grade_holds_retained:true, actual_protocol_checks:requiredControllerChecks.length, actual_protocol_tests:protocol.required_executed_tests.length, source_specification_requirements:data.source_specification.requirements.length, native_parts:stationNativeDefinition.parts.length, physical_release:false },
    moving_six_car:{actual_rust_steps:movingRun.completed_moving_steps,physical_gap_range_m:[movingRun.minimum_gap_m,movingRun.maximum_gap_m],adverse_confirmation_roles:moving.mandatory_confirmation_roles,shared_field_phase_accepted:false,physical_release:false},
    integrated_campaign:{actual_rust_cases:campaign.cases.length,cross_controller_handover:false,independent_brake_and_recovery_unqualified:true},
    manufactured_dossier:{requirements:dossier.closure.requirement_count,frame_members:dossier.primary_frame_families.defined_member_piece_count,native_solids:detailDefinition.parts.length,accepted_requirements:0},
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
