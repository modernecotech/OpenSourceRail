"""Source-bound Airport car mass, fit, traction and independent-stop screens."""
import argparse
import csv
from copy import deepcopy
from hashlib import sha256
import io
from itertools import product
import json
import math
from pathlib import Path
import tomllib
from zipfile import ZipFile

from cities.Baghdad.engineering.prototype import car, commercial, weights
from cities.Baghdad.engineering.simulation import airport_alignment, vehicle_civil

CITY = vehicle_civil.CITY
ROOT = CITY.parents[1]
PROTO = vehicle_civil.PROTOTYPE
GA = PROTO / "vehicle-factory/installed-ga.json"
BOM = GA.with_name("installed-fitout-bom.csv")
TRIAL = CITY / "engineering/mechanical/vehicle/section-trial.toml"
SYSTEM = CITY / "system.toml"
G = 9.80665
KWH = 3.6e6
MODULE_COMPARATOR_KN = 14.6  # VEHICLE.md, rounded demand at the original crowd mass
PHYSICAL_RETURNS = {
    "installed_mass": "Complete serialised item mass/CG and installed fluids; calibrated tare and ballast/loaded group and 4N axle records with checked balance, wheel-side split and orientation.",
    "traction": "Driven axle assignments/failed inverter mapping, hot tractive effort and duration versus speed and rail condition, instrumented axle loads, slip recovery and cooling.",
    "braking": "Command-to-force trace, wheel-slide series and independent rail force versus speed, at both load extremes, dry/contaminated rail, downgrade, lost axle/module and zero line receptivity; show the stopping position.",
    "brake_thermal": "Per-module duty, engagement energy, mount/disc/pad/rail thermal traces, allowable limits, cool-down, thermal fade, rail damage and inspection after repeated stops.",
    "brake_containment": "Wheel/rail and rail-brake compatibility, air gap and wear, all swept poses, stow and parking retention, common-cause protection, force transfer and protected tow.",
    "battery": "End-of-life hot/aged deliverable capacity and power through the two-hour outage, brake excitation and accessible egress; log voltage, current, retention, isolation and recharge.",
    "door_boarding": "Serialised loaded and empty fitted widths, leaf/guide/stop/lock/anti-drop and cable sweep, force and cycles; survey platform step and gap through yaw, roll, wheel wear and stopping error, including assisted boarding.",
    "suspension_exchange": "Survey all four secondary gaps, stacks, primary guides and stops, jounce/rebound and retained travel. Witness equipped extraction and reinstallation with hoses, wiring, slings, pallet, stands and tools.",
    "route_protection": "Survey direction-specific grade and speed transitions, detection and control latencies, authorised stopping limit and overlap, full-tail release and turnout protection.",
}


def sha(raw):
    return sha256(raw).hexdigest()


def source_data():
    members = ("mechanical.json", "civil-article.json", "fitout-interfaces.json",
               "opening.json", "revised-cuts.csv", "returns/weights.json", "returns/fitout.csv")
    with ZipFile(PROTO / "airport-prototype.zip") as packet:
        manifest_raw = packet.read("manifest.json")
        manifest = json.loads(manifest_raw)
        data = {name: packet.read(name) for name in members}
    hashes = {name: sha(raw) for name, raw in data.items()}
    if any(manifest["sha256"][name] != digest for name, digest in hashes.items()):
        raise ValueError("Airport article packet member hash mismatch")
    ga_raw, bom_raw = GA.read_bytes(), BOM.read_bytes()
    ga = json.loads(ga_raw)
    mechanical, cage, fit, opening = (json.loads(data[name]) for name in members[:4])
    parent = opening["candidate_id"]
    if (any(record["candidate_id"] != parent for record in (manifest, mechanical, cage, fit, ga))
            or ga["mechanical_evaluation_id"] != mechanical["evaluation_id"]
            or ga["opening_evaluation_id"] != opening["evaluation_id"]
            or ga["fitout_evaluation_id"] != fit["evaluation_id"]
            or ga["frame_revision"] != opening["bundle"]["vehicle_revision"]
            or ga["frame_revision"] != mechanical["frame_revision"]
            or ga["frame_revision"] != fit["frame_revision"]
            or fit["article_evaluation_id"] != mechanical["evaluation_id"]
            or cage["mechanical_evaluation_id"] != mechanical["evaluation_id"]
            or ga["evaluation_id"] != car.identity({key: value for key, value in ga.items() if key != "evaluation_id"})
            or any(manifest["sha256"][name] != digest for name, digest in ga["packet_member_sha256"].items())
            or ga["outputs_sha256"][BOM.name] != sha(bom_raw)):
        raise ValueError("Installed BOM, GA and Airport article ancestry differ")
    for path in (SYSTEM, TRIAL):
        if opening["sources"][path.relative_to(ROOT).as_posix()] != sha(path.read_bytes()):
            raise ValueError(f"Airport opening scenario source changed: {path.name}")
    files = (Path(__file__), Path(vehicle_civil.__file__), Path(weights.__file__),
             Path(commercial.__file__), Path(car.__file__), SYSTEM, TRIAL, GA, BOM, CITY / "VEHICLE.md",
             CITY / "airport_assembly.py", CITY / "engineering/mechanical/README.md")
    sources = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in files}
    sources.update({"prototype:" + name: value for name, value in hashes.items()})
    sources["prototype:manifest.json"] = sha(manifest_raw)
    cuts = csv.DictReader(io.StringIO(data["revised-cuts.csv"].decode()))
    bogie_stock = 2 * sum(float(row["gross_mass_kg"]) for row in cuts if row["assembly"] == "bogie")
    return mechanical, cage, fit, opening, ga, list(csv.DictReader(io.StringIO(bom_raw.decode()))), bogie_stock, sources


def mass_cases(record, bogie, service, cars, material, centres, battery_position=(-2.0, .85), saloon=None):
    axle_offsets = record["interfaces"]["body_from_axle_x_m"]
    cases = {}
    for state in vehicle_civil.STATES:
        crowd = saloon is not None and state == "high"
        people_per_car = None if saloon is None else saloon["places_per_car"]
        if crowd:
            people_per_car = max(700 / 6, people_per_car)
        row = vehicle_civil.load_case(
            record, bogie, service, cars, material, state, passengers_per_car=people_per_car,
            passenger_centroid_x_m=None if saloon is None or crowd else saloon["passenger_centroid_x_m"],
            battery_position=battery_position)
        groups = {key: (x, z) for key, (_, z, x) in vehicle_civil.GROUPS.items()}
        groups.update(body_stock=(0, 1.8), bogie_frame_stock=(0, .55),
                      independent_service_pack=battery_position)
        allocations = {key: dict(mass_kg_per_car=mass, car_from_centroid_m=[groups[key][0], None, groups[key][1]])
                       for key, mass in row["group_kg_per_car"].items()}
        payload = (row["loaded_train_kg"] - row["tare_train_kg"]) / cars
        allocations["payload"] = dict(mass_kg_per_car=payload,
                                      car_from_centroid_m=[row["passenger_centroid_x_m"], None, 1.6])
        tare = row["tare_train_kg"] / cars
        tare_x = sum(a["mass_kg_per_car"] * a["car_from_centroid_m"][0]
                     for key, a in allocations.items() if key != "payload") / tare
        pivot = record["bogie_translations_m"][1]
        front = tare * (.5 + tare_x / (2 * pivot))
        tare_axles = [(tare - front) / 2] * 2 + [front / 2] * 2
        axle_rows = {}
        for i, centre in enumerate(centres, 1):
            for j, (offset, empty, loaded) in enumerate(zip(axle_offsets, tare_axles, row["axle_kg_per_car"], strict=True), 1):
                axle_rows[f"C{i}-A{j}"] = dict(train_x_m=centre + offset, car_x_m=offset, tare_kg=empty,
                                               loaded_kg=loaded, loaded_reaction_kn=loaded * G / 1000)
        cases[state] = {**row, "group_allocations": allocations, "axles": axle_rows, "tare_car_cg_x_m": tare_x,
                        "max_loaded_static_axle_kg": max(row["axle_kg_per_car"]),
                        "load_purpose": "retained_Airport_high_crowd_comparator" if crowd else "normal_service_cap" if saloon is not None else "legacy_planning_case"}
    return cases


def stop(speed, delay, slope_accel, mass, wheel_kn, rail_kn):
    """Constant force after a coast delay; brake work includes downhill gravity."""
    entry = speed + delay * slope_accel
    coast = delay * (speed + entry) / 2
    net = (wheel_kn + rail_kn) * 1000 / mass - slope_accel
    distance = entry**2 / (2 * net) if net > 0 else None
    return dict(net_deceleration_m_s2=net, build_up_entry_speed_m_s=entry, delay_distance_m=coast,
                stop_distance_m=coast + distance if distance is not None else None,
                stop_time_s=delay + entry / net if distance is not None else None,
                wheel_dissipation_kwh=wheel_kn * 1000 * distance / KWH if distance is not None else None,
                rail_dissipation_kwh=rail_kn * 1000 * distance / KWH if distance is not None else None,
                work_energy_residual_kwh=((wheel_kn + rail_kn) * 1000 * distance
                    - mass * (speed**2 / 2 + slope_accel * (coast + distance))) / KWH if distance is not None else None)


def brake_case(row, speed, delay, grade, mu, modules, target, stop_room, overlap, length):
    mass = row["loaded_train_kg"]
    downhill = G * grade
    failed_axle = max(row["axles"], key=lambda name: row["axles"][name]["loaded_kg"])
    lost_kg = row["axles"][failed_axle]["loaded_kg"]
    cases = {}
    for wheel, active in product(("all", "one_out", "none"), (modules, modules - 1)):
        supported = {"all": mass, "one_out": mass - lost_kg, "none": 0.0}[wheel]
        wheel_force = mu * supported * G / 1000
        required = max(0.0, mass * (target + downhill) / 1000 - wheel_force)
        target_stop = stop(speed, delay, downhill, mass, min(wheel_force, mass * (target + downhill) / 1000), required)
        comparator = stop(speed, delay, downhill, mass, wheel_force, active * MODULE_COMPARATOR_KN)
        unassisted = stop(speed, delay, downhill, mass, wheel_force, 0)
        room_for_braking = None if stop_room is None or overlap is None else stop_room - overlap
        entry = target_stop["build_up_entry_speed_m_s"]
        target_distance = target_stop["stop_distance_m"]
        compare_distance = comparator["stop_distance_m"]
        cases[f"{wheel}_wheel_brakes/{modules - active}_rail_modules_out"] = dict(
            wheel_mode=wheel, rail_modules_available=active, wheel_force_upper_bound_kn=wheel_force,
            required_rail_force_kn=required, required_force_per_available_module_kn=required / active,
            proposed_comparator_per_module_kn=MODULE_COMPARATOR_KN,
            comparator_force_margin_per_module_kn=MODULE_COMPARATOR_KN - required / active,
            required_rail_energy_per_module_kwh=target_stop["rail_dissipation_kwh"] / active,
            required_peak_rail_interface_kw_per_module=required * entry / active,
            stop_at_target=target_stop, stop_at_comparator=comparator, stop_wheel_only=unassisted,
            all_rail_demand_kn=mass * (target + downhill) / 1000,
            target_front_stop_plus_train_and_overlap_m=None if overlap is None else target_distance + length + overlap,
            comparator_front_stop_plus_train_and_overlap_m=None if overlap is None or compare_distance is None
                else compare_distance + length + overlap,
            target_stop_room_margin_m=None if room_for_braking is None else room_for_braking - target_distance,
            comparator_stop_room_margin_m=None if room_for_braking is None or compare_distance is None
                else room_for_braking - compare_distance,
            documented_rail_interface_limit_kw=None, documented_repeat_duty=None)
    return dict(wheel_adhesion_assumed=mu, downgrade_pct=100 * grade, coast_delay_s=delay,
                target_net_deceleration_m_s2=target, lost_wheel_brake_axle=failed_axle, cases=cases)


def traction_case(row, power, grade, speed_kmh=72.0):
    mass = row["loaded_train_kg"]
    mu = power["low_adhesion_mu"]
    demand = (power["required_net_accel_m_s2"] + power["resistance_accel_m_s2"] + G * grade) * mass
    factored = demand * power["adhesion_force_margin"]
    # Identical cars, with each powered pair sharing a bogie. For a partial-drive
    # layout show both bogie choices, retaining the heavier loss for each layout.
    patterns = [(0, 1), (2, 3), (0, 1, 2, 3)]
    axles = row["axle_kg_per_car"]
    cars = len(row["axles"]) // len(axles)
    layout = []
    for positions in patterns:
        nominal = cars * sum(axles[j] for j in positions)
        failed = max(positions, key=axles.__getitem__)
        for fault, supported in (("all_available", nominal), ("heaviest_driven_axle_out", nominal - axles[failed])):
            force = supported * G * mu
            layout.append(dict(driven_positions_per_car=[j + 1 for j in positions], fault=fault,
                               driven_axle_count=cars * len(positions) - (fault != "all_available"),
                               driven_static_load_fraction=supported / mass, adhesion_upper_bound_kn=force / 1000,
                               required_adhesion_with_margin=factored / (supported * G),
                               margin_kn=(force - factored) / 1000))
    declared = [item for item in layout if item["driven_positions_per_car"] == [1, 2, 3, 4]]
    # With every axle driven, the failed axle is the largest static reaction.
    # This is a necessary load-distribution bound at the unchanged duty, not a
    # proposal to remove the acceleration obligation or add uncounted ballast.
    permitted_lost_kg = mass - factored / (mu * G)
    largest_kg = max(axles)
    reduction_per_heaviest_axle_kg = max(0.0, largest_kg - permitted_lost_kg)
    heaviest_positions = [j + 1 for j, value in enumerate(axles) if math.isclose(value, largest_kg)]
    degraded_supported_kg = mass - largest_kg
    speed = speed_kmh / 3.6
    correction = dict(
        purpose="Preliminary corrective load and traction quote envelope for a revised physical candidate; the present candidate remains failed.",
        required_net_accel_m_s2=power["required_net_accel_m_s2"],
        upgrade_pct=100 * grade, resistance_accel_m_s2=power["resistance_accel_m_s2"],
        adhesion_assumed=mu, adhesion_force_margin=power["adhesion_force_margin"],
        maximum_lost_driven_axle_static_kg=permitted_lost_kg,
        present_heaviest_driven_axle_static_kg=largest_kg,
        present_heaviest_positions_per_car=heaviest_positions,
        minimum_reaction_transfer_from_each_heaviest_axle_kg=reduction_per_heaviest_axle_kg,
        minimum_reaction_transfer_per_car_kg=len(heaviest_positions) * reduction_per_heaviest_axle_kg,
        required_adhesion_if_loads_unchanged=factored / (degraded_supported_kg * G),
        minimum_hot_wheel_force_after_one_axle_out_kn=demand / 1000,
        minimum_factored_adhesion_force_after_one_axle_out_kn=factored / 1000,
        force_curve_speed_range_kmh=[0.0, speed * 3.6],
        constant_force_at_speed_cap_wheel_power_kw=demand * speed / 1000,
        constant_force_at_speed_cap_electrical_input_kw=demand * speed / (1000 * power["traction_efficiency"]),
        quote_required=["Installed axle-load distribution and CG at both load extremes",
                        "Hot tractive-effort/current versus speed and duration after one axle or converter channel fails",
                        "Rail condition, slip recovery, cooling and thermal repetition",
                        "Motor, inverter, cabling, protection and cooling installed mass and price delta"],
        changed_installed_mass_kg=None, changed_price_usd=None,
        scope="Force and power assume constant full acceleration through the declared speed cap as an equipment envelope, not a timetable claim. Load transfer changes CG and all axle reactions; any mass or hardware revision must be re-evaluated with braking, civil, energy and cost. Supplier evidence cannot be attached to this physical ID as an installed remedy.")
    return dict(upgrade_pct=100 * grade, roll_resistance_m_s2=power["resistance_accel_m_s2"],
                adhesion_assumed=mu, required_train_force_kn=demand / 1000, factored_train_force_kn=factored / 1000,
                min_driven_static_load_fraction=factored / (mass * G * mu), layouts=layout,
                declared_physical_layout=declared,
                corrective_procurement=correction,
                declared_static_adhesion_necessary_screen_passes=all(item["margin_kn"] >= 0 for item in declared),
                layout_scope="Only the four-axle-per-car layout belongs to this physical candidate. Pair-drive rows are offline static necessary-bound comparisons without revised installed mass, bogies, braking, protection or cost. Even a positive margin would not prove hot tractive effort, inverter independence or slip control.")


def battery_case(cfg, alternative=None, baseline_service=None):
    service = cfg["service_power"]
    load = service["control_continuous_kw"] + service["other_essential_continuous_kw"]
    demand = (load * service["protected_outage_hours"] + service["brake_event_kwh"]
              + service["door_egress_event_kwh"]) * (1 + service["energy_reserve_fraction"])
    nominal = service["battery_nominal_kwh"]
    usable = service["usable_fraction"]
    retained = .8 if alternative is None else alternative["retained_capacity_fraction"]
    hot_factors = (1.0, .9, .8)  # Capacity sensitivity only; no supplier hot data.
    eol_usable = nominal * usable * retained
    required_hot_factor = demand / eol_usable
    # Existing mass/price are an allocation for 65 kWh, not a validated
    # specific energy or a supplier price curve for a larger fitted pack.
    original = service if baseline_service is None else baseline_service
    correction = dict(
        purpose="Preliminary replacement-pack quote envelope; the 65 kWh reference pack fails hot end-of-life energy.",
        protected_continuous_load_kw=load,
        protected_outage_hours=service["protected_outage_hours"],
        continuous_load_energy_kwh=load * service["protected_outage_hours"],
        brake_event_allocation_kwh=service["brake_event_kwh"],
        accessible_egress_event_allocation_kwh=service["door_egress_event_kwh"],
        energy_reserve_fraction=service["energy_reserve_fraction"],
        minimum_hot_end_of_life_deliverable_kwh=demand,
        retention_fraction_hypothesis=retained,
        usable_fraction_hypothesis=usable,
        minimum_nominal_kwh_by_hot_capacity_factor={str(factor): demand / (usable * retained * factor)
                                                   for factor in hot_factors},
        minimum_continuous_hot_discharge_kw=load,
        required_brake_excitation_peak_kw=None,
        required_egress_peak_kw=None,
        required_combined_hot_discharge_peak_kw=None,
        baseline_nominal_kwh=original["battery_nominal_kwh"],
        baseline_installed_mass_allowance_kg=original["battery_mass_allowance_t"] * 1000,
        baseline_price_allocation_usd=original["battery_price_allocation_usd_m_per_train"] * 1e6,
        replacement_installed_mass_kg=None, replacement_price_usd=None,
        changed_installed_mass_kg=None, changed_price_usd=None,
        quote_required=["Hot and aged usable energy at the stated retention and duty",
                        "Voltage/current and continuous plus brake/egress peak discharge duration",
                        "Recharge acceptance and cooling at the two-hour turnaround",
                        "Complete fitted pack, BMS, enclosure, isolation, wiring, mounts, cooling and fire protection mass, CG, dimensions and price",
                        "Service life, replacement cost, local repair route and safe rescue behaviour"],
        scope="Nominal energy sizes the energy necessary bound only. Brake and egress peak power cannot be inferred from event kWh. A quoted pack replaces the 500 kg/$100,000 planning allocation; its mass/price delta and resulting axle loads, traction, braking, civil and economics remain unknown until installed data and a new candidate evaluation.")
    result = dict(scope="One fixed per-train service pack in both studied formations; actual equipment position and consumption await evidence.",
                usable_new_kwh=nominal * usable, usable_at_80pct_retention_kwh=nominal * usable * .8,
                retained_capacity_fraction=retained, modeled_retained_usable_kwh=eol_usable,
                modeled_retained_margin_kwh=eol_usable - demand,
                demand_with_reserve_kwh=demand, new_margin_kwh=nominal * usable - demand,
                end_of_life_margin_kwh=nominal * usable * .8 - demand,
                minimum_nominal_kwh_at_80pct_retention=demand / (usable * .8),
                minimum_nominal_kwh_at_modeled_retention=demand / (usable * retained),
                minimum_retention_fraction=demand / (nominal * usable),
                hot_end_of_life=dict(capacity_factor_measured=None, deliverable_energy_kwh=None,
                    minimum_capacity_factor_required=required_hot_factor,
                    energy_possible_with_capacity_factor_at_most_one=required_hot_factor <= 1,
                    sensitivity=[dict(assumed_hot_capacity_factor=factor,
                                      usable_kwh=eol_usable * factor,
                                      energy_margin_kwh=eol_usable * factor - demand,
                                      minimum_nominal_kwh=demand / (usable * retained * factor))
                                 for factor in hot_factors],
                    scope="Analytical hot capacity derating after the modeled retention fraction. Factors are hypothetical or quoted study inputs, not measured hot performance. Discharge power, voltage and brake excitation duration remain unverified."),
                nominal_kwh=nominal, continuous_kw=load, recharge_input_kw=nominal / (
                    service["recharge_hours"] * service["recharge_efficiency"]),
                brake_electrical_input_vs_4kwh_allocation=None, required_hot_discharge_peak_kw=None,
                corrective_procurement=correction)
    if alternative is not None:
        hot_energy = nominal * usable * retained * alternative["hot_capacity_factor"]
        baseline_mass = original["battery_mass_allowance_t"] * 1000
        baseline_price = original["battery_price_allocation_usd_m_per_train"] * 1e6
        result["alternative"] = dict(
            basis_kind=alternative["basis_kind"], supplier_reference=alternative["supplier_reference"],
            quote_source_sha256=alternative["quote_source_sha256"],
            source_document_verified=alternative.get("source_document") is not None,
            quoted_hot_end_of_life_usable_kwh=hot_energy, hot_energy_necessary_screen_passes=hot_energy >= demand,
            quoted_hot_continuous_discharge_kw=alternative["hot_continuous_discharge_kw"],
            continuous_power_necessary_screen_passes=alternative["hot_continuous_discharge_kw"] >= load,
            quoted_hot_peak_discharge_kw=alternative["hot_peak_discharge_kw"],
            quoted_peak_duration_s=alternative["peak_duration_s"],
            brake_and_egress_peak_power_screen_passes=None,
            installed_mass_kg=alternative["installed_mass_kg"], mass_delta_kg=alternative["installed_mass_kg"] - baseline_mass,
            installed_price_usd=alternative["installed_price_usd"], price_delta_usd=alternative["installed_price_usd"] - baseline_price,
            installed_car_x_m=alternative["car_x_m"], installed_car_z_m=alternative["car_z_m"],
            full_nominal_recharge_input_kw=nominal / (service["recharge_hours"] * service["recharge_efficiency"]),
            status="Identified study configuration; no authenticated installation, peak duty match, thermal test or physical acceptance.")
        correction.update(replacement_installed_mass_kg=alternative["installed_mass_kg"],
                          replacement_price_usd=alternative["installed_price_usd"],
                          changed_installed_mass_kg=alternative["installed_mass_kg"] - baseline_mass,
                          changed_price_usd=alternative["installed_price_usd"] - baseline_price)
    return result


def validate_battery_alternative(value, cfg, battery_directory=None):
    if value is None:
        return None
    fields = {"basis_kind", "supplier_reference", "quote_source_sha256", "nominal_kwh", "usable_fraction",
              "retained_capacity_fraction", "hot_capacity_factor", "installed_mass_kg",
              "installed_price_usd", "car_x_m", "car_z_m", "hot_continuous_discharge_kw",
              "hot_peak_discharge_kw", "peak_duration_s"}
    if not isinstance(value, dict) or set(value) - {"source_document"} != fields:
        raise ValueError("Battery alternative requires the complete identified supplier, installed and hot-duty bundle")
    if value["basis_kind"] not in ("planning-estimate", "supplier-quote"):
        raise ValueError("Battery alternative basis must be planning-estimate or supplier-quote")
    if not isinstance(value["supplier_reference"], str) or not value["supplier_reference"].strip():
        raise ValueError("Battery alternative needs a supplier reference")
    digest = value["quote_source_sha256"]
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError("Battery alternative needs a SHA-256 quote source digest")
    source_document = value.get("source_document")
    if value["basis_kind"] == "supplier-quote" and source_document is None:
        raise ValueError("Supplier quote requires the source document for hash verification")
    if source_document is not None:
        path = Path(source_document)
        if not path.is_absolute() and battery_directory is not None:
            path = Path(battery_directory) / path
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise ValueError("Battery alternative source document is missing or changed")
    for key in fields - {"basis_kind", "supplier_reference", "quote_source_sha256"}:
        number = value[key]
        if isinstance(number, bool) or not isinstance(number, (int, float)) or not math.isfinite(number):
            raise ValueError("Battery alternative has a non-finite or missing numeric field: " + key)
    for key in ("nominal_kwh", "installed_mass_kg", "installed_price_usd", "hot_continuous_discharge_kw",
                "hot_peak_discharge_kw", "peak_duration_s"):
        if value[key] <= 0:
            raise ValueError("Battery alternative requires positive " + key)
    for key in ("usable_fraction", "retained_capacity_fraction", "hot_capacity_factor"):
        if not 0 < value[key] <= 1:
            raise ValueError("Battery alternative fraction must be between zero and one: " + key)
    if value["hot_peak_discharge_kw"] < value["hot_continuous_discharge_kw"]:
        raise ValueError("Battery peak power cannot be below continuous power")
    if abs(value["car_x_m"]) > cfg["vehicle_geometry"]["car_body_length_m"] / 2 or value["car_z_m"] < 0:
        raise ValueError("Battery installed centroid lies outside the declared car length or below rail")
    return dict(value)


def validate_saloon_layout(value, cfg, parent_candidate_id, layout_directory=None):
    """Check a single-car floor allocation; unallocated floor has no places."""
    if value is None:
        return None
    required = {"schema", "parent_candidate_id", "source_sha256", "inner_length_m", "inner_width_m",
                "standing_density_person_m2", "seat_area_m2_per_place", "wheelchair_area_m2_per_place",
                "clear_aisle_width_m", "allocations"}
    if not isinstance(value, dict) or set(value) - {"source_document"} != required or value["schema"] != "airport-saloon-layout/1":
        raise ValueError("Saloon layout needs the complete airport-saloon-layout/1 bundle")
    if value["parent_candidate_id"] != parent_candidate_id:
        raise ValueError("Saloon layout belongs to a different Airport article")
    digest = value["source_sha256"]
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError("Saloon layout needs a source SHA-256")
    if "source_document" in value:
        path = Path(value["source_document"])
        if not path.is_absolute() and layout_directory is not None:
            path = Path(layout_directory) / path
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise ValueError("Saloon layout source document is missing or changed")
    length, width, density, seat_area, wheelchair_area, aisle_width = (value[k] for k in (
        "inner_length_m", "inner_width_m", "standing_density_person_m2", "seat_area_m2_per_place",
        "wheelchair_area_m2_per_place", "clear_aisle_width_m"))
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in (
            length, width, density, seat_area, wheelchair_area, aisle_width)):
        raise ValueError("Saloon dimensions and standing density must be finite")
    if not (0 < length <= cfg["vehicle_geometry"]["car_body_length_m"]
            and 0 < width <= cfg["vehicle_geometry"]["body_width_m"]
            and density >= 0 and seat_area > 0 and wheelchair_area > 0 and aisle_width > 0):
        raise ValueError("Saloon dimensions exceed the body or allocation assumptions are not positive")
    rows = value["allocations"]
    if not isinstance(rows, list) or not rows:
        raise ValueError("Saloon layout needs allocated rectangles")
    allowed = {"seat", "wheelchair", "aisle", "door_access", "standing", "equipment"}
    parsed = []
    packed_furniture = True
    for row in rows:
        base_keys = {"kind", "x0_m", "x1_m", "y0_m", "y1_m"}
        footprint_keys = {"footprint_length_m", "footprint_width_m", "allow_rotation"}
        if not isinstance(row, dict) or not base_keys <= set(row) or (
                set(row) - base_keys - {"places"} not in (set(), footprint_keys)):
            raise ValueError("Saloon allocation requires kind and one rectangle")
        kind = row["kind"]
        if kind not in allowed:
            raise ValueError("Unknown saloon allocation kind")
        x0, x1, y0, y1 = (row[k] for k in ("x0_m", "x1_m", "y0_m", "y1_m"))
        if any(type(v) not in (int, float) or not math.isfinite(v) for v in (x0, x1, y0, y1)):
            raise ValueError("Saloon rectangle coordinates must be finite")
        if not (-length/2 <= x0 < x1 <= length/2 and -width/2 <= y0 < y1 <= width/2):
            raise ValueError("Saloon rectangle lies outside the declared interior")
        places = row.get("places", 0)
        if (kind in ("seat", "wheelchair") and (type(places) is not int or places <= 0)) or (
                kind not in ("seat", "wheelchair") and "places" in row):
            raise ValueError("Only seat and wheelchair rectangles carry positive whole places")
        area = (x1-x0)*(y1-y0)
        if kind == "seat" and area < seat_area * places - 1e-9:
            raise ValueError("Seat allocation is below its declared area per place")
        if kind == "wheelchair" and area < wheelchair_area * places - 1e-9:
            raise ValueError("Wheelchair allocation is below its declared area per place")
        if kind == "aisle" and min(x1-x0, y1-y0) < aisle_width - 1e-9:
            raise ValueError("Clear aisle segment is below its declared study width")
        if kind in ("seat", "wheelchair"):
            if footprint_keys <= set(row):
                fl, fw = row["footprint_length_m"], row["footprint_width_m"]
                if (type(fl) not in (int, float) or type(fw) not in (int, float)
                        or not math.isfinite(fl) or not math.isfinite(fw) or fl <= 0 or fw <= 0
                        or type(row["allow_rotation"]) is not bool):
                    raise ValueError("Furniture footprint needs positive finite dimensions and a rotation choice")
                along = math.floor((x1-x0+1e-9)/fl) * math.floor((y1-y0+1e-9)/fw)
                across = math.floor((x1-x0+1e-9)/fw) * math.floor((y1-y0+1e-9)/fl)
                if max(along, across if row["allow_rotation"] else 0) < places:
                    raise ValueError("Furniture count exceeds whole footprint packing in its rectangle")
            else:
                packed_furniture = False
        elif footprint_keys & set(row):
            raise ValueError("Only furniture can declare a footprint")
        parsed.append((kind, x0, x1, y0, y1, places, area))
    for i, a in enumerate(parsed):
        for b in parsed[:i]:
            if min(a[2], b[2]) - max(a[1], b[1]) > 1e-9 and min(a[4], b[4]) - max(a[3], b[3]) > 1e-9:
                raise ValueError("Saloon allocations overlap")
    door_centres = cfg["vehicle_geometry"]["door_centres_m"]
    door_width = cfg["vehicle_geometry"]["door_clear_width_m"]
    doors = [r for r in parsed if r[0] == "door_access"]
    if len(doors) != len(door_centres) or any(not any(r[1] <= centre-door_width/2+1e-9
            and r[2] >= centre+door_width/2-1e-9 and r[3] <= -width/2+1e-9
            and r[4] >= width/2-1e-9 for r in doors) for centre in door_centres):
        raise ValueError("Saloon door access must cover every documented opening across the interior")
    def adjacent(a, b):
        return ((abs(a[2]-b[1]) <= 1e-9 or abs(b[2]-a[1]) <= 1e-9)
                and min(a[4], b[4])-max(a[3], b[3]) > 1e-9) or (
                (abs(a[4]-b[3]) <= 1e-9 or abs(b[4]-a[3]) <= 1e-9)
                and min(a[2], b[2])-max(a[1], b[1]) > 1e-9)
    clear = [r for r in parsed if r[0] in ("aisle", "door_access")]
    reached = {i for i, r in enumerate(clear) if r[0] == "door_access"}
    while True:
        extended = reached | {i for i, r in enumerate(clear)
                              if any(adjacent(r, clear[j]) for j in reached)}
        if extended == reached:
            break
        reached = extended
    if len(reached) != len(clear) or any(not any(adjacent(r, clear[j]) for j in reached)
                                            for r in parsed if r[0] == "wheelchair"):
        raise ValueError("A wheelchair or clear aisle is isolated from the door access network")
    seats = sum(r[5] for r in parsed if r[0] == "seat")
    wheelchairs = sum(r[5] for r in parsed if r[0] == "wheelchair")
    if wheelchairs < 2:
        raise ValueError("Saloon layout must retain at least two wheelchair places per car")
    standing_area = sum(r[6] for r in parsed if r[0] == "standing")
    standees = math.floor(standing_area * density + 1e-9)
    places = seats + wheelchairs + standees
    if places <= 0:
        raise ValueError("Saloon layout has no passenger places")
    seat_moment = sum(r[5] * (r[1]+r[2])/2 for r in parsed if r[0] in ("seat", "wheelchair"))
    stand_moment = (sum(r[6] * standees / standing_area * (r[1]+r[2])/2
                        for r in parsed if r[0] == "standing") if standing_area else 0.0)
    centroid = (seat_moment + stand_moment) / places
    return dict(source=value, seats_per_car=seats, wheelchair_places_per_car=wheelchairs,
                standing_area_m2_per_car=standing_area, standing_places_per_car=standees,
                places_per_car=places, passenger_centroid_x_m=centroid,
                reference_seats_per_car=20, reference_wheelchair_places_per_car=2,
                seat_count_delta_per_car=seats-20, wheelchair_place_delta_per_car=wheelchairs-2,
                changed_seat_and_accessibility_hardware_mass_kg=None,
                changed_seat_and_accessibility_hardware_price_usd=None,
                furniture_whole_footprint_packing_screen_passes=True if packed_furniture else None,
                wheelchair_to_door_rectangle_connectivity_passes=True,
                allocated_area_m2=sum(r[6] for r in parsed), unallocated_area_m2=length*width-sum(r[6] for r in parsed),
                physical_qualified=False,
                scope="Rectangle and door bounds only. Drawings, seat pitch, wheelchair maneuvering, continuous accessible path, egress and crowd approval remain open.")


def fit_case(record, cage, fit, ga, rows, material):
    door = record["doorway"]
    edges = door["per_edge_allowances_m"]
    aperture = min(door["rough_widths_m"])
    allocated = aperture - 2 * sum(edges.values()) - door["required_fitted_m"]
    gap = min(pad["stock_face_gap_mm"] for bogie in fit["bogies"]
              for pad in bogie["pads"] if pad["type"] == "secondary_top")
    pivot = record["bogie_translations_m"][1]
    compression = {}
    for state, row in rows.items():
        payload = row["group_allocations"]["payload"]["mass_kg_per_car"]
        load_kn = payload * G / 2000 * (.5 + abs(row["passenger_centroid_x_m"]) / (2 * pivot))
        compression[state] = {str(k): dict(payload_compression_mm=load_kn / k,
                                           trial_40mm_stroke_margin_mm=40 - load_kn / k)
                              for k in (.6, 1.0, 1.6)}
    return dict(
        scope="Steel stock geometry at its nominal pose. Alternatives have no released aperture, joint or stack geometry."
        if material != "steel" else "Steel stock and passive-travel sensitivities. Installed interfaces need measurements.",
        steel_stock_door_sweep=door["leaf_sweep"], aperture_planes=ga["geometry"]["door_apertures"],
        nominal_allocated_portal_margin_mm=1000 * allocated,
        doubled_loaded_distortion_margin_mm=1000 * (allocated - 2 * edges["loaded_distortion_per_edge_m"]),
        straight_platform_gap_mm=1000 * cage["station_interfaces"]["static_level_horizontal_gap_m"],
        measured_boarding_pose=None, minimum_stock_secondary_gap_mm=gap,
        static_stack_margin_mm={str(s): gap - s for s in (145, 155, 165)},
        passive_incremental_payload_cases=compression, bogie_stock_transforms_and_sweeps=fit["bogies"],
        equipped_exchange_verified=False, installed_door_and_suspension_verified=False)


def assess_return(basis, submission, directory, *, route_bound=False):
    if submission is None:
        return dict(submission_id=None, claim=None, documents={}, submitted={}, missing=list(PHYSICAL_RETURNS),
                    physical_accepted=False)
    if (not isinstance(submission, dict) or submission.keys() != {"basis", "kind", "documents", "returns"}
            or submission["basis"] != basis
            or submission["kind"] not in ("supplier-declaration", "physical-measurement", "synthetic-fixture")):
        raise ValueError("Bind the evidence return to this exact vehicle and duty")
    docs = commercial.evidence(submission["documents"], directory)
    rows = submission["returns"]
    if not isinstance(rows, dict) or rows.keys() - PHYSICAL_RETURNS.keys():
        raise ValueError("Use the named vehicle evidence scopes")
    if "route_protection" in rows and not route_bound:
        raise ValueError("Bind the route protection return to an evaluated alignment")
    for scope, row in rows.items():
        if (not isinstance(row, dict) or row.keys() != {"document", "article_serial", "procedure_revision", "witness"}
                or not commercial.has_document(row["document"], docs)
                or not all(isinstance(row[k], str) and row[k].strip() for k in ("article_serial", "procedure_revision", "witness"))):
            raise ValueError(f"Incomplete candidate-specific attachment citation for {scope}")
    return dict(submission_id=car.identity(submission), claim=submission["kind"], documents=docs, submitted=rows,
                missing=sorted(PHYSICAL_RETURNS.keys() - rows.keys()), physical_accepted=False,
                scope="Attachment custody only. Authentication, approved limits, suitability for the exact duty and independent review remain open.")


def evaluate(*, cars=6, material="steel", grade_pct=None, available_stop_m=None, overlap_m=None,
             route=None, alignment=None, evidence_return=None, evidence_directory=None,
             battery_alternative=None, battery_directory=None, saloon_layout=None, saloon_directory=None):
    """Audit a studied formation. A distance allowance includes the withheld overlap."""
    if type(cars) is not int or cars not in (3, 6) or material not in vehicle_civil.MATERIAL:
        raise ValueError("Choose a supported Airport train formation and body material")
    record, cage, fit, opening, ga, bom, bogie, sources = source_data()
    cfg = tomllib.loads(SYSTEM.read_text())
    battery_alternative = validate_battery_alternative(battery_alternative, cfg, battery_directory)
    saloon = validate_saloon_layout(saloon_layout, cfg, opening["candidate_id"], saloon_directory)
    baseline_service = deepcopy(cfg["service_power"])
    battery_position = (-2.0, .85)
    if battery_alternative is not None:
        cfg["service_power"].update(battery_nominal_kwh=battery_alternative["nominal_kwh"],
                                    usable_fraction=battery_alternative["usable_fraction"],
                                    battery_mass_allowance_t=battery_alternative["installed_mass_kg"] / 1000)
        battery_position = (battery_alternative["car_x_m"], battery_alternative["car_z_m"])
    design_grade = cfg["power_assumptions"]["adverse_grade"]
    if alignment is not None:
        if route is not None:
            raise ValueError("Supply one Airport alignment basis")
        airport_alignment.validate(alignment)
        if alignment["parent_candidate_id"] != opening["candidate_id"]:
            raise ValueError("Alignment and vehicle audit identify different Airport candidates")
    if route is not None:
        stops = [(s["id"], s["chainage_km"], s["register_id"]) for s in route["stops"]]
        route_basis = dict(parent=opening["candidate_id"], stops=stops, grade_pct=route["grade_pct"], cars=cars)
        if (route["candidate_id"] != vehicle_civil.digest(route_basis) or route["cars"] != cars
                or route["parent_candidate_id"] != opening["candidate_id"]
                or route["opening_evaluation_id"] != opening["evaluation_id"]
                or (grade_pct is not None and grade_pct != abs(route["grade_pct"]))):
            raise ValueError("Route and vehicle audit identify different candidates or grades")
        grade_pct = abs(route["grade_pct"])
    grade_pct = design_grade * 100 if grade_pct is None else grade_pct
    for value, label in ((grade_pct, "grade"), (available_stop_m, "stop allowance"), (overlap_m, "overlap")):
        if value is not None:
            commercial.number(value, label)
    if grade_pct > 100 * design_grade or (available_stop_m is not None and overlap_m is not None and overlap_m > available_stop_m):
        raise ValueError("Outside the Airport stopping-screen domain")

    pitch = ga["geometry"]["formation_body_from_car_x_m"][1] - ga["geometry"]["formation_body_from_car_x_m"][0]
    centres = [(i - (cars - 1) / 2) * pitch for i in range(cars)]
    length = cfg["vehicle_geometry"]["car_body_length_m"] + (cars - 1) * pitch
    cases = mass_cases(record, bogie, cfg["service_power"], cars, material, centres, battery_position, saloon)
    speed = cfg["vehicle"]["speed_cap_kmh"] / 3.6
    net = tomllib.loads(TRIAL.read_text())["braking_deceleration_m_s2"]
    trial_inputs = dict(grade_pct=grade_pct, speed_kmh=speed * 3.6, available_stop_m=available_stop_m,
                        overlap_m=overlap_m, brake_delays_s=[0.0, 2.0], wheel_adhesions=[.08, cfg["power_assumptions"]["low_adhesion_mu"]],
                        net_decelerations_m_s2=[net, 1.0], rail_modules_per_car=2, published_comparator_kn=MODULE_COMPARATOR_KN,
                        route_candidate_id=None if route is None else route["candidate_id"])
    if saloon is not None:
        trial_inputs["saloon_normal_places_per_train"] = saloon["places_per_car"] * cars
        trial_inputs["saloon_source_sha256"] = saloon_layout["source_sha256"]
    if alignment is not None:
        trial_inputs.update(alignment_id=alignment["alignment_id"], alignment_record_id=alignment["record_id"])
    physical = dict(parent_candidate_id=opening["candidate_id"], frame_revision=ga["frame_revision"],
                    formation_cars=cars, material=material, car_centres_train_x_m=centres,
                    length_m=length, powered_axle_positions_per_car=[1, 2, 3, 4], supply="protected_conductor")
    if battery_alternative is not None:
        physical["replacement_service_battery"] = {key: battery_alternative[key] for key in (
            "nominal_kwh", "usable_fraction", "installed_mass_kg", "car_x_m", "car_z_m",
            "hot_continuous_discharge_kw", "hot_peak_discharge_kw", "peak_duration_s")}
    if saloon is not None:
        physical["saloon_geometry"] = {key: saloon_layout[key] for key in (
            "inner_length_m", "inner_width_m", "allocations")}
    candidate_id = car.identity(physical)
    duty_id = car.identity(dict(candidate_id=candidate_id, controls=trial_inputs, sources=sources))
    basis = dict(physical_candidate_id=candidate_id, duty_id=duty_id, frame_revision=ga["frame_revision"],
                 opening_evaluation_id=opening["evaluation_id"], mechanical_evaluation_id=record["evaluation_id"])
    grades_pct = sorted({0., float(grade_pct), 100 * design_grade})
    braking = {state: [brake_case(row, speed, delay, grade / 100, mu, 2 * cars, target, available_stop_m, overlap_m, length)
                       for grade, delay, mu, target in product(grades_pct, trial_inputs["brake_delays_s"],
                           trial_inputs["wheel_adhesions"], trial_inputs["net_decelerations_m_s2"])]
               for state, row in cases.items() if state != "low"}
    level_force_reference = [{
        "downgrade_pct": grade, "coast_delay_s": delay,
        **stop(speed, delay, G * grade / 100, cases["central"]["loaded_train_kg"],
               cases["central"]["loaded_train_kg"] * net / 1000, 0),
    } for grade, delay in product(grades_pct, trial_inputs["brake_delays_s"])]
    selected = dict(candidate_id=candidate_id, physical=physical, inputs=trial_inputs, duty_id=duty_id, basis=basis,
                    source_sha256=sources, installed_ga_evaluation_id=ga["evaluation_id"],
                    parent_fitout_evaluation_id=fit["evaluation_id"], parent_civil_article_evaluation_id=cage["evaluation_id"],
                    room_scope="Front-to-protected-limit distance must come from the alignment and signalling design. Interstation distance cannot establish an overlap.",
                    mass_cases=cases, measured_installed_mass_kg=None,
                    mass_scope="Low and central use the layout normal service cap when supplied; high retains at least the Airport 700-per-six high-load comparator with its adverse longitudinal distribution. The separate 160-person/car v0.6 structural control is not silently applied to this Airport candidate. Gross cut stock is untrimmed. No complete installed weight or certified axle bounds.",
                    released_bom_basis="Steel six-car article. Quantities label the source release even for other study formations. Blank installed masses remain unknown.",
                    released_steel_bom=[{**row, "installed_mass_kg": float(row["installed_mass_kg"]) if row["installed_mass_kg"] else None}
                                        for row in bom],
                    braking=braking, level_service_force_reference=level_force_reference,
                    traction={state: traction_case(row, cfg["power_assumptions"], grade_pct / 100, speed * 3.6)
                                              for state, row in cases.items() if state != "low"},
                    high_load_adverse_traction=traction_case(cases["high"], cfg["power_assumptions"], design_grade, speed * 3.6),
                    battery=battery_case(cfg, battery_alternative, baseline_service), fit=fit_case(record, cage, fit, ga, cases, material),
                    saloon_layout=None if saloon is None else {**saloon, "places_per_train": saloon["places_per_car"] * cars},
                    return_assessment=assess_return(basis, evidence_return, evidence_directory,
                                                    route_bound=alignment is not None or route is not None),
                    return_template=dict(basis=basis, kind=None, documents={}, returns={}),
                    physical_measurements_required=PHYSICAL_RETURNS,
                    braking_scope="Static-load adhesion upper bounds, worst single-axle failure, constant-force analytical sensitivities with gravity during coast, no drag or regeneration. Rail-contact dissipation includes the rail and shoe; train excitation and equipment heat split are unknown.",
                    documented_weight_return="Use the prototype weights intake for a complete candidate-specific train-weight recalculation.",
                    physical_accepted=False)
    return {**selected, "evaluation_id": car.identity(selected)}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--cars", type=int, choices=(3, 6), default=6)
    cli.add_argument("--material", choices=vehicle_civil.MATERIAL, default="steel")
    cli.add_argument("--grade-pct", type=float)
    cli.add_argument("--available-stop-m", type=float)
    cli.add_argument("--overlap-m", type=float)
    cli.add_argument("--evidence-return", type=Path)
    cli.add_argument("--battery-alternative", type=Path, help="JSON identified study bundle replacing the 65 kWh service pack")
    cli.add_argument("--saloon-layout", type=Path, help="JSON per-car saloon allocation study")
    args = vars(cli.parse_args())
    path = args.pop("evidence_return")
    battery_path = args.pop("battery_alternative")
    saloon_path = args.pop("saloon_layout")
    if battery_path is not None:
        args["battery_alternative"] = json.loads(battery_path.read_bytes())
        args["battery_directory"] = battery_path.parent
    if saloon_path is not None:
        args["saloon_layout"] = json.loads(saloon_path.read_bytes())
        args["saloon_directory"] = saloon_path.parent
    if path is not None:
        args.update(evidence_return=json.loads(path.read_bytes()), evidence_directory=path.parent)
    print(json.dumps(evaluate(**args), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
