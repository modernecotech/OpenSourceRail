"""Factory utility/process alternatives with evidence gaps preserved explicitly.

Published subtotals, unaccepted allowances and project-qualified demand are kept
separate. No sum here establishes a complete supply, fire or lifting design.
"""

from __future__ import annotations

from copy import deepcopy
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(__file__).with_name("data") / "factory-systems.json"
EQUIPMENT = ROOT / "engineering/factory_examples/data/equipment.json"
UTILITIES = ROOT / "engineering/factory_examples/examples/utilities.json"
ROUTES = ROOT / "engineering/factory_examples/examples/process-routes.csv"
SCHEDULE = ROOT / "engineering/design_engine/data/factory-schedule.json"
RETAINED = ROOT / "engineering/factory_examples/examples/report.json"
BASIS = ROOT / "engineering/factory_examples/data/basis.json"
CIVIL_SPACE = Path(__file__).with_name("data") / "civil-space.json"


def read(path):
    return json.loads(Path(path).read_text())


def positive(value, name):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError("positive finite " + name + " required")
    return value


def electrical(cfg, utilities, equipment):
    c = cfg["electric"]
    v = positive(c["line_voltage_v"], "line voltage")
    pf = positive(c["assumed_power_factor"], "power factor")
    loading = positive(c["maximum_transformer_loading_fraction"], "loading fraction")
    if pf > 1 or loading > 1:
        raise ValueError("power factor/loading fraction cannot exceed one")
    known = [
        dict(
            id=u["id"],
            kva=u["input_kva_max"],
            basis="retained published input upper rating, one unit",
        )
        for u in utilities
        if u.get("input_kva_max") is not None
    ]
    # CIJECT's maximum stated voltage times its published input current: apparent
    # input, not shaft output. Do not mistake saw/CNC motor ratings for total input.
    injection = equipment["ciject-1"]["published"]
    known.append(
        dict(
            id="ciject-1",
            kva=max(injection["voltage_v_range"]) * injection["input_a"] / 1000,
            basis="single-phase published maximum voltage times input current, one unit",
        )
    )
    subtotal = sum(positive(r["kva"], "known input") for r in known)
    allowance = sum(
        positive(r["kw"], "planning input") * positive(r["quantity"], "quantity")
        for r in c["planning_loads"]
    )
    connected = subtotal + allowance / pf
    rows = []
    for diversity in c["peak_diversity"]:
        if not 0 < diversity <= 1:
            raise ValueError("diversity must lie in (0,1]")
        peak = subtotal + allowance * diversity / pf
        required = peak / loading
        candidates = [s for s in c["transformer_candidates_kva"] if s >= required]
        transformer = min(candidates) if candidates else None
        full_i = transformer * 1000 / (math.sqrt(3) * v) if transformer else None
        buses = [a for a in c["bus_candidates_a"] if full_i is not None and a >= full_i]
        rows.append(
            dict(
                diversity_hypothesis=diversity,
                published_apparent_subtotal_kva=subtotal,
                assumed_connected_kw=allowance,
                planning_connected_kva=connected,
                planning_peak_kva=peak,
                minimum_transformer_hypothesis_kva=required,
                candidate_transformer_kva=transformer,
                transformer_full_load_current_a=full_i,
                candidate_bus_continuous_rating_a=min(buses) if buses else None,
                transformer_only_terminal_fault_hypotheses_a=(
                    [
                        dict(
                            impedance_pu=z, current_a=full_i / positive(z, "impedance")
                        )
                        for z in c["impedance_hypotheses_pu"]
                    ]
                    if full_i
                    else []
                ),
                screening_status=(
                    "hypothesis-sized"
                    if transformer and buses
                    else "outside-candidate-envelope"
                ),
                actual_peak_kva=None,
                accepted_transformer_kva=None,
                accepted_bus_rating_a=None,
                accepted_fault_duty_a=None,
            )
        )
    return dict(
        id="electrical-demand-and-distribution",
        state="unaccepted-planning-sensitivity",
        published_inputs=known,
        planning_loads=deepcopy(c["planning_loads"]),
        unresolved_utility_equipment_ids=[
            u["id"] for u in utilities if not u["connected_load_complete"]
        ],
        candidates=rows,
        boundary="Includes both factory examples at one hypothetical415V bus; actual sites, feeders, utility voltages and coincidence unaccepted. Supply is not fully enumerated. Fault estimates are transformer-only bolted-terminal sensitivities; upstream impedance, motors, cables and protection omitted.",
        commissioning=[
            "Accepted complete machine load list and Baghdad ambient derating",
            "Utility fault level, vector group, neutral/earthing and motor-start/harmonic study",
            "Independent protection/selectivity/cable/short-circuit/voltage-drop design",
            "Factory routine test, site insulation/earth/protection secondary-injection and staged load tests",
        ],
    )


def air_system(cfg, utilities):
    c = cfg["air"]
    consumers = [
        dict(id=u["id"], l_min=u["air_l_min"], pressure_bar=u["air_bar"])
        for u in utilities
        if u.get("air_l_min") is not None
    ]
    subtotal = sum(r["l_min"] for r in consumers)
    pressure = max(r["pressure_bar"] for r in consumers)
    suppliers = {s["id"]: s for s in cfg["supplier_cases"]}
    evo = suppliers["avelair-evo11"]["published"]
    bambi = suppliers["bambi-vts200d"]["published"]
    cmm = next(r for r in consumers if r["id"] == "aberlink-axiom-900")
    rows, cmm_rows = [], []
    for leak in c["leak_fraction"]:
        if not 0 <= leak < 1:
            raise ValueError("leak fraction must lie in [0,1)")
        reserve = 1 + c["capacity_reserve_fraction"]
        required = subtotal * reserve / (1 - leak)
        cmm_required = cmm["l_min"] * reserve / (1 - leak)
        fad = evo["capacity_10bar_m3_h"] * 1000 / 60
        rows.append(
            dict(
                leak_fraction=leak,
                published_consumer_subtotal_l_min=subtotal,
                unknown_consumers_l_min=c["additional_unknown_consumers_l_min"],
                planning_free_air_required_l_min=required,
                minimum_header_pressure_hypothesis_bar=pressure
                + c["header_drop_allowance_bar"],
                supplier_case="avelair-evo11",
                published_fad_l_min_at10bar=fad,
                required_duty_units=math.ceil(required / fad),
                standby_units_hypothesis=1,
                accepted_delivered_flow_l_min=None,
                receiver_isothermal_l=[
                    dict(
                        autonomy_s=t,
                        volume_l=required
                        * t
                        / 60
                        * c["reference_absolute_pressure_bar"]
                        / c["receiver_pressure_drop_bar"],
                    )
                    for t in c["receiver_autonomy_s"]
                ],
            )
        )
        for units in (1, 2, 3):
            capacity = units * bambi["fad_8bar_l_min"] * bambi["maximum_duty_fraction"]
            cmm_rows.append(
                dict(
                    duty_units=units,
                    standby_units_hypothesis=1,
                    leak_fraction=leak,
                    required_l_min=cmm_required,
                    continuous_time_average_capacity_l_min=capacity,
                    supplier_case="bambi-vts200d",
                    status=(
                        "passed-flow-hypothesis"
                        if capacity >= cmm_required
                        else "failed-flow-hypothesis"
                    ),
                    reason="126L/min@8bar and max50%duty per unit; receiver does not create sustained flow",
                    pressure_drop_allowance_to7bar_consumer_bar=1,
                    accepted_air_quality=None,
                    accepted_receiver_and_pressure_control=False,
                )
            )
    return dict(
        id="compressed-air-pressure-flow-and-receivers",
        state="published-partial-demand-plus-hypotheses",
        consumers=consumers,
        candidates=rows,
        cmm_segregated_candidates=cmm_rows,
        required_air_quality_class=None,
        accepted_total_demand_l_min=None,
        boundary="FAD values are free-air reference volumes.9bar minimum header is only an assumed1bar-loss budget above8bar consumer;10bar compressor rating is not an accepted setpoint. Oil/particle/dewpoint compatibility, dryer derating, duty cycling and pressure-system controls remain open.",
        commissioning=[
            "Log all consumer duty/flow/pressure, including CNC and tools currently unknown",
            "Dryer/filter/receiver sizing and oil/particle/dewpoint acceptance for CMM and resin process",
            "Leak/pressure-drop, dewpoint/particle and simultaneous-demand tests at Baghdad ambient",
            "Relief/pressure-vessel examination and receiver duty/standby transition test",
        ],
    )


def beam_cases(civil_report=None):
    if civil_report is not None:
        if civil_report.get("physical_release") is not False:
            raise ValueError("civil research report must retain physical_release=false")
        selected = set(civil_report["selected_candidate_ids"])
        if not selected:
            raise ValueError("civil report has no selected candidates to transfer")
        if not selected <= {r["id"] for r in civil_report["candidates"]}:
            raise ValueError("civil selected candidate missing")
        space = read(CIVIL_SPACE)
        rows = []
        for row in civil_report["candidates"]:
            if row["id"] not in selected:
                continue
            variables = row["variables"]
            for s in row["scenarios"]:
                L = positive(s["span_m"], "span")
                h = variables["depth_m"] - space["geometry"]["flange_thickness_m"]
                end_fill = (
                    2
                    * space["geometry"]["end_fill_length_m"]
                    * (
                        space["geometry"]["deck_width_m"]
                        - 2 * variables["stem_width_m"]
                    )
                    * h
                )
                rows.append(
                    dict(
                        id=row["id"] + f"-pi{L:g}",
                        span_m=L,
                        mass_kg=positive(
                            s["known_concrete_plus_strand_mass_kg"], "beam mass"
                        ),
                        concrete_m3=row["section"]["area_m2"] * L + end_fill,
                        depth_m=variables["depth_m"],
                        spreader_span_m=s["longitudinal_spreader_span_m"],
                        transferred_hook_equivalent_kg=s["hook_equivalent_kg"],
                        source_candidate_id=row["id"],
                        origin="current-civil-selected-proposal",
                    )
                )
        return rows
    retained = read(RETAINED)["civil"]
    return [
        dict(
            id=f'retained-pi{s["span_m"]:g}',
            span_m=s["span_m"],
            mass_kg=s["developed_mass_kg"],
            concrete_m3=s["bare_volume_m3"]
            + s["optional_solid_end_diaphragms_extra_m3"],
            depth_m=retained["section"]["depth_m"],
            spreader_span_m=0.6 * s["span_m"],
            transferred_hook_equivalent_kg=None,
            source_candidate_id=None,
            origin="historical-retained40strand-mass-lower-bound",
        )
        for s in retained["scenarios"]
    ]


def fluids_and_thermal(cfg, beams):
    c, thermal, extraction = cfg["water"], cfg["thermal"], cfg["extraction"]
    water = []
    for beam, output, mix, wash in itertools.product(
        beams, c["retained_output_beams_day"], c["mix_water_l_m3"], c["washout_l_batch"]
    ):
        batches = math.ceil(beam["concrete_m3"])
        water.append(
            dict(
                beam=beam["id"],
                beams_day_hypothesis=output,
                mix_l_m3=mix,
                washout_l_batch=wash,
                batches_per_beam_at1m3=batches,
                mix_water_m3_day=beam["concrete_m3"] * output * mix / 1000,
                washout_m3_day=batches * output * wash / 1000,
                minimum_process_makeup_m3_day=output
                * (beam["concrete_m3"] * mix + batches * wash)
                / 1000,
                accepted_mix_water_l_m3=None,
                recycled_fraction_accepted=None,
            )
        )
    cooling = []
    for ambient, ach, heat, delta in itertools.product(
        thermal["ambient_hypotheses_c"],
        thermal["cmm_room_infiltration_ach"],
        thermal["process_heat_kw"],
        thermal["chilled_water_delta_k"],
    ):
        dT = ambient - thermal["cmm_room_target_c"]
        sensible = (
            thermal["cmm_room_fabric_ua_w_k"]
            + thermal["air_volumetric_heat_capacity_j_m3_k"]
            * thermal["cmm_room_volume_m3"]
            * ach
            / 3600
        ) * dT + thermal["cmm_room_internal_gain_w"]
        duty = heat * 1000 + sensible
        cooling.append(
            dict(
                ambient_c=ambient,
                infiltration_ach=ach,
                process_heat_hypothesis_kw=heat,
                cmm_room_sensible_kw=sensible / 1000,
                combined_sensible_kw=duty / 1000,
                water_delta_k=delta,
                minimum_sensible_water_l_s=duty
                * 1000
                / (thermal["water_density_kg_m3"] * thermal["water_cp_j_kg_k"] * delta),
                latent_solar_product_cure_load_kw=None,
                selected_chiller_capacity_kw=None,
            )
        )
    lev = []
    for area, velocity, count, duct_v, dp in itertools.product(
        extraction["hood_open_area_m2"],
        extraction["face_velocity_hypotheses_m_s"],
        extraction["simultaneous_hypothetical_hoods"],
        extraction["duct_velocity_hypotheses_m_s"],
        extraction["fan_pressure_hypotheses_pa"],
    ):
        q = area * velocity
        lev.append(
            dict(
                hood_open_area_m2=area,
                face_velocity_hypothesis_m_s=velocity,
                independent_hood_count=count,
                airflow_each_m3_s=q,
                total_energy_balance_airflow_m3_s=q * count,
                separate_branch_duct_diameter_m=math.sqrt(4 * q / (math.pi * duct_v)),
                assumed_branch_duct_velocity_m_s=duct_v,
                assumed_fan_pressure_pa=dp,
                summed_separate_fan_shaft_power_kw=q
                * count
                * dp
                / extraction["fan_efficiency_hypothesis"]
                / 1000,
                shared_dust_fume_header_permitted=False,
                accepted_capture_velocity_m_s=None,
            )
        )
    fire = [
        dict(
            flow_hypothesis_l_min=q,
            duration_hypothesis_min=t,
            theoretical_water_reservation_m3=q * t / 1000,
            accepted_fire_flow_l_min=None,
            accepted_fire_water_reserve_m3=None,
            fire_compliance_established=False,
        )
        for q, t in itertools.product(
            c["fire_flow_hypotheses_l_min"], c["fire_duration_hypotheses_min"]
        )
    ]
    return [
        dict(
            id="concrete-process-water-and-washout",
            candidates=water,
            boundary="Mix-water doses are sensitivity values, not mix design. Separate dirty washout/alkaline reclaim, clean process/curing and potable systems; outfall and reuse require chemical/environmental acceptance.",
        ),
        dict(
            id="cmm-room-and-process-sensible-cooling",
            candidates=cooling,
            boundary="CMM optimum18–22C and rate limits remain constraints. RoomUA/ACH/internal and process heat are hypotheses; latent/solar/oven cure loads unclosed. Water flow is a sensible-only minimum, not chiller selection.",
        ),
        dict(
            id="segregated-extraction-air-and-fan-sensitivities",
            candidates=lev,
            boundary=extraction["basis"],
        ),
        dict(
            id="fire-water-space-and-duration-sensitivity",
            candidates=fire,
            boundary="Space reservation only; no hazard classification, sprinkler/hydrant flow, pump pressure, simultaneous demand, egress or Iraqi approval has been established.",
        ),
    ]


def handling(cfg, beams):
    from engineering.design_engine.factory_beam import G

    a, c = read(BASIS)["assumptions"], cfg["handling"]
    rows = []
    for beam, lower, upper in itertools.product(
        beams, c["lower_sling_degrees"], c["upper_sling_degrees_from_vertical"]
    ):
        hook_eq = (beam["mass_kg"] + a["rigging_mass_kg"]) * a["lifting_dynamic_factor"]
        transferred = beam["transferred_hook_equivalent_kg"]
        if transferred is not None and not math.isclose(
            transferred, hook_eq, rel_tol=1e-9
        ):
            raise ValueError("civil/handling load transfer disagrees")
        factored_beam = beam["mass_kg"] * G * a["lifting_dynamic_factor"]
        headroom = beam["spreader_span_m"] / (2 * math.tan(math.radians(upper)))
        # Product bottom1.5m above floor is an explicit transport/handling hypothesis.
        clear = (
            1.5
            + beam["depth_m"]
            + c["assumed_lower_rig_height_m"]
            + headroom
            + c["assumed_hook_block_height_m"]
            + c["clearance_above_product_m"]
        )
        rows.append(
            dict(
                beam=beam["id"],
                origin=beam["origin"],
                source_candidate_id=beam["source_candidate_id"],
                known_beam_mass_kg=beam["mass_kg"],
                rigging_assumption_kg=a["rigging_mass_kg"],
                hook_equivalent_kg=hook_eq,
                dynamic_factor_hypothesis=a["lifting_dynamic_factor"],
                lower_sling_degrees_from_vertical=lower,
                nominal_four_equalized_leg_tension_n=factored_beam
                / (4 * math.cos(math.radians(lower))),
                two_effective_leg_tension_n=factored_beam
                / (2 * math.cos(math.radians(lower))),
                longitudinal_spreader_span_m=beam["spreader_span_m"],
                upper_sling_degrees_from_vertical=upper,
                upper_leg_tension_n=hook_eq * G / (2 * math.cos(math.radians(upper))),
                longitudinal_spreader_compression_n=hook_eq
                * G
                * math.tan(math.radians(upper))
                / 2,
                upper_rig_geometric_headroom_m=headroom,
                assumed_product_bottom_elevation_m=1.5,
                minimum_clear_building_height_hypothesis_m=clear,
                crane_capacity_scalar_screens=[
                    dict(
                        candidate_kg=k,
                        status=(
                            "passed-lower-bound-scalar"
                            if k >= hook_eq
                            else "failed-lower-bound-scalar"
                        ),
                    )
                    for k in c["candidate_lift_capacity_kg"]
                ],
                building_height_scalar_screens=[
                    dict(
                        candidate_clear_height_m=k,
                        status=(
                            "passed-assumed-envelope"
                            if k >= clear
                            else "failed-assumed-envelope"
                        ),
                    )
                    for k in c["candidate_building_clear_height_m"]
                ],
                accepted_crane_capacity_kg=None,
                accepted_rigging_capacity_n=None,
                accepted_lifting_insert_capacity_n=None,
            )
        )
    return dict(
        id="whole-product-lift-rigging-and-building-envelope",
        candidates=rows,
        boundary="Beam mass excludes conventional reinforcement and attachments; full rig mass is not known. Two-member upper sling geometry is a proposal; angles trade headroom for spreader compression. Insert breakout/unequal sharing/torsion/tilt/suction/wind and transport/erection remain unqualified.100/125/160t are capacity enquiries, not offered load charts.",
        evidence=[
            "Exact product/rebar/insert/full-rig mass and CG",
            "Configured crane hook approach, span, ambient/wind limits and wheel/runway/foundation reactions",
            "Exact spreader length/angle load chart, sling/shackle WLL and complete BOM/origin",
            "Insert/bond/breakout and temporary-state stability calculations",
            "Surveyed haulage route, supports/restraints, axle weights and erection method",
            "Exclusion-zone, trial-lift, emergency and periodic inspection plans",
        ],
    )


def flow(cfg, beams):
    from engineering.design_engine.factory_schedule import schedule

    base, a, f = read(SCHEDULE), read(BASIS)["assumptions"], cfg["flow"]
    largest = max(beams, key=lambda b: b["concrete_m3"])
    finite = []
    for beds, cranes, batch in itertools.product(
        f["bed_positions"], f["crane_counts"], f["useful_batch_output_hypotheses_m3"]
    ):
        case = deepcopy(base)
        case["resources"]["crane"] = cranes
        case["resources"]["crane_crew"] = cranes
        case["batch_output_assumption_m3"] = batch
        r = schedule(case, largest["concrete_m3"], beds, f["accepted_yield_hypothesis"])
        finite.append(
            dict(
                beds=beds,
                cranes=cranes,
                crane_crews=cranes,
                batch_output_hypothesis_m3=batch,
                largest_beam=largest["id"],
                source_schedule=r,
                accepted_cycle_output=False,
            )
        )
    bounds = []
    for target in f["target_beams_day"]:
        gross = target / f["accepted_yield_hypothesis"]
        batches = math.ceil(largest["concrete_m3"] / base["batch_output_assumption_m3"])
        h = base["hours"]
        casting = h["casting_setup_finish"] + batches * (
            h["mix_per_batch"] + h["pour_per_batch"]
        )
        crane = h["cage_lift"] + casting + h["release_demould"] + h["dispatch"]
        operating = base["shift_hours"] * f["availability_fraction"]
        bounds.append(
            dict(
                target_accepted_beams_day_hypothesis=target,
                gross_beams_day_hypothesis=gross,
                crane_policy_hours_per_beam=crane,
                crane_count_aggregate_work_lower_bound=math.ceil(
                    gross * crane / operating
                ),
                casting_crew_aggregate_work_lower_bound=math.ceil(
                    gross * casting / operating
                ),
                reinforcement_bench_work_lower_bound=math.ceil(
                    gross * h["reinforcement"] / operating
                ),
                bed_positions_occupation_lower_bound=math.ceil(
                    gross
                    * a["bed_occupation_working_days"]
                    / f["availability_fraction"]
                ),
                storage_positions_at24h_dwell_lower_bound=math.ceil(
                    gross * base["hours"]["storage_elapsed"] / 24
                ),
                planned_layout_storage_positions=4,
                accepted_throughput_beams_day=None,
            )
        )
    with ROUTES.open() as stream:
        process = list(csv.DictReader(stream))
    return dict(
        id="finite-process-schedules-and-output-resource-bounds",
        finite_cases=finite,
        resource_bounds=bounds,
        process_routes=process,
        all_original_hold_points_open=all(r["completed"] == "no" for r in process),
        boundary="Actual inherited non-preemptive calendar, maintenance and all hold points retained.2m3 batch option requires a different configured mixer/plant and validated continuous-pour window. Aggregate work/occupation bounds are necessary resource counts, not sufficient plant designs, optimal schedules or measured production capacity.",
    )


def package(identifier, investigations, gates):
    return dict(
        work_package_id=identifier,
        investigations=investigations,
        generated_artifacts=[],
        unresolved_gates=gates,
        engineering_design_complete=False,
        manufacturing_release=False,
        physical_release=False,
    )


def run(*, civil_report=None):
    cfg = read(DATA)
    if (
        cfg["schema"] != "osr-generative-factory-systems-basis/1"
        or cfg["state"] != "bounded-unaccepted-planning-hypotheses"
    ):
        raise ValueError("unaccepted controlled factory basis required")
    utilities = read(UTILITIES)
    equipment = {r["id"]: r for r in read(EQUIPMENT)["equipment"]}
    if {u["id"] for u in utilities} != set(equipment):
        raise ValueError("utility/equipment inventory mismatch")
    beams = beam_cases(civil_report)
    electric, air = electrical(cfg, utilities, equipment), air_system(cfg, utilities)
    fluids = fluids_and_thermal(cfg, beams)
    lifts, process = handling(cfg, beams), flow(cfg, beams)
    suppliers = deepcopy(cfg["supplier_cases"])
    commissioning = [
        dict(
            id=u["id"],
            unresolved=list(u["utility_gaps"]),
            required_records=[
                "Exact supplier configuration/origin/GA and interface agreement",
                "Utility/foundation/anchor, guarding and maintenance acceptance",
                "FAT, installed survey, calibrated SAT and emergency/failure-state trials",
                "Material/tool calibration and physical first-article correlation",
            ],
            completed=False,
        )
        for u in utilities
    ]
    packages = [
        package(
            "FACTORY-MEP",
            [electric, air] + fluids,
            [
                "Accepted utility/load, weather/ambient, fire/environmental hazard and site inputs",
                "Detailed coordinated distribution, pressure/head losses, protection/earthing and commissioned performance",
            ],
        ),
        package(
            "FACTORY-EQUIPMENT",
            [
                dict(
                    id="configured-equipment-and-british-origin-routes",
                    equipment_cases=suppliers,
                    retained_equipment_ids=sorted(equipment),
                    accepted_offers=0,
                    supplier_contacted=False,
                )
            ],
            [
                "All14 retained equipment offers and exact current configurations remain unaccepted",
                "Actual British manufacturing origin/component content, Baghdad support and comparable installed quotations",
            ],
        ),
        package("FACTORY-HANDLING", [lifts], lifts["evidence"]),
        package(
            "FACTORY-FLOW",
            [process],
            [
                "Measured accepted task times, workforce, batch/cure/strength, yield and maintenance evidence",
                "Production qualification and full vehicle/civil process inventories; current flow covers representative retained routes",
            ],
        ),
        package(
            "SYSTEM-ENERGY",
            [
                dict(
                    id="factory-energy-versus-railway-energy-boundary",
                    electrical_candidates=electric["candidates"],
                    thermal_candidates=fluids[1]["candidates"],
                    accepted_railway_traction_and_charging_duty=None,
                )
            ],
            [
                "Vehicle traction/regen duty, charging events, battery thermal control and utility coincidence from matching six-car configuration",
                "Factory electrical sensitivities do not qualify railway energy or shared charger capacity",
            ],
        ),
        package(
            "SYSTEM-SAFETY",
            [
                dict(
                    id="segregated-hazards-and-safe-state-test-routes",
                    interfaces=[
                        "Separate welding/sparks, GRP/resin/solvents, batteries, pressure plant and stressing exclusion zones",
                        "LEV streams remain segregated pending dust/fire/explosion assessment; no capture efficiency inferred",
                        "Clean/dirty process water, fire reserve and potable systems separated",
                        "Emergency electrical/HV/pressure/stressing isolation and safe-stop cause/effect matrix",
                    ],
                    fire_reservation_cases=fluids[3]["candidates"],
                    lift_trial_gates=lifts["evidence"],
                    hazards_accepted=False,
                )
            ],
            [
                "Accepted hazard analysis, fire strategy/egress, exposure limits, pressure/lift/machinery safeguards",
                "Iraqi authority and independent system safety approval; no statutory compliance or safety integrity level asserted",
            ],
        ),
        package(
            "SYSTEM-ASSURANCE",
            [
                dict(
                    id="equipment-and-system-commissioning-records",
                    equipment_records=commissioning,
                    tests_performed=0,
                    inspection_measuring_equipment_calibrated=False,
                )
            ],
            [
                "Appointed competent reviewers accept exact revisions and actual witnessed test results",
                "Complete material/lot/as-built/NC/process/inspection provenance and all original hold points closed",
            ],
        ),
    ]
    paths = [
        DATA,
        EQUIPMENT,
        UTILITIES,
        ROUTES,
        SCHEDULE,
        RETAINED,
        BASIS,
        CIVIL_SPACE,
        Path(__file__),
        ROOT / "engineering/design_engine/factory_schedule.py",
        ROOT / "engineering/design_engine/factory_beam.py",
    ]
    return dict(
        schema="osr-generative-factory-systems/1",
        source_sha256={
            p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths
        },
        civil_input_sha256=(
            hashlib.sha256(
                json.dumps(civil_report, sort_keys=True, allow_nan=False).encode()
            ).hexdigest()
            if civil_report is not None
            else None
        ),
        beam_cases=beams,
        packages=packages,
        engineering_design_complete=False,
        supplier_contacted=False,
        physical_release=False,
    )


def write_artifacts(report, output: Path):
    """Write actual schedules/diagrams; link only files emitted by this call."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    by_id = {p["work_package_id"]: p for p in report["packages"]}
    paths = []

    def csv_file(name, rows):
        target = output / name
        fields = list(dict.fromkeys(k for row in rows for k in row))
        with target.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(
                {
                    k: (
                        json.dumps(v, sort_keys=True)
                        if isinstance(v, (dict, list))
                        else v
                    )
                    for k, v in row.items()
                }
                for row in rows
            )
        paths.append(target)
        return name

    mep = by_id["FACTORY-MEP"]
    power = mep["investigations"][0]
    mep["generated_artifacts"] = [
        csv_file("electrical-sizing.csv", power["candidates"])
    ]
    lifts = by_id["FACTORY-HANDLING"]
    lifts["generated_artifacts"] = [
        csv_file("lift-and-headroom.csv", lifts["investigations"][0]["candidates"])
    ]
    f = by_id["FACTORY-FLOW"]
    f["generated_artifacts"] = [
        csv_file(
            "resource-sizing-bounds.csv", f["investigations"][0]["resource_bounds"]
        )
    ]
    tasks = []
    for case in f["investigations"][0]["finite_cases"]:
        identity = f'beds{case["beds"]}-cranes{case["cranes"]}-batch{case["batch_output_hypothesis_m3"]:g}'
        for event in case["source_schedule"]["tasks"]:
            tasks.append(dict(case=identity, **event))
    f["generated_artifacts"].append(csv_file("finite-process-tasks.csv", tasks))
    links = [
        ("415V hypothesis bus", "Machines / local isolation"),
        ("Air header / receivers", "CMM clean-air and resin branches"),
        ("Clean water / thermal loop", "Batch / curing / cooling"),
        ("Dirty washout / reclaim", "Contained treatment / agreed outfall"),
        ("Separate LEV systems", "Weld / GRP / resin source controls"),
        ("Fire reserved space", "Unaccepted fire strategy and duty"),
    ]
    shapes = []
    for i, (left, right) in enumerate(links):
        y = 75 + i * 75
        shapes.append(
            f'<rect x="20" y="{y}" width="280" height="48" rx="5" fill="#e0eef3"/><text x="30" y="{y+29}">{left}</text><path d="M300 {y+24}H360" stroke="#506775" stroke-width="2"/><rect x="360" y="{y}" width="405" height="48" rx="5" fill="#e7eddd"/><text x="370" y="{y+29}">{right}</text>'
        )
    diagram = output / "utility-process-interfaces.svg"
    diagram.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="595" viewBox="0 0 800 595"><rect width="800" height="595" fill="#f7f6f0"/><g font-family="sans-serif" font-size="14" fill="#263946"><text x="20" y="30" font-size="19">Factory utility / process interface investigation</text><text x="20" y="53">Hypotheses only. Sizing, hazards and commissioned performance remain unaccepted.</text>'
        + "".join(shapes)
        + '<text x="20" y="565">Separate process streams; diagram establishes no distribution route, fire compliance or release.</text></g></svg>'
    )
    mep["generated_artifacts"].append(diagram.name)
    paths.append(diagram)
    target = output / "factory-systems.json"
    target.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )
    paths.append(target)
    return paths
