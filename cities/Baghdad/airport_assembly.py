"""Airport procurement lots drawn from the opening train, frame and civil articles."""

import csv
import json
from collections import Counter, defaultdict
from hashlib import sha256
from math import isclose
from pathlib import Path
import tomllib

from engineering.outline import baghdad_viaduct
from cities.Baghdad.engineering.mechanical.compare_returns import verified_record
from cities.Baghdad.engineering.mechanical.vehicle.power_interface import identity, mass_return

CITY = Path(__file__).resolve().parent
ROOT = CITY.parents[1]
MECH = CITY / "engineering/mechanical"
FRAME = MECH / "vehicle/result.json"
CUTS = MECH / "vehicle/cut-list.csv"
CIVIL = MECH / "civil/section-results.json"
SCHEDULE = MECH / "schedule.json"


def cut_schedule(frame, cars):
    with CUTS.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    groups = Counter()
    for row in rows:
        group = row["assembly"]
        if group not in frame["cut_stock_mass_kg"]:
            raise ValueError(f"Unexpected Airport stock group {group}")
        copies = 2 if group == "bogie" else 1
        groups[group] += float(row["mass_kg"])
        row["cut_count_per_car"] = copies * int(row["cuts_per_assembly"])
        row["cut_count_per_train"] = cars * row["cut_count_per_car"]
        row["cut_stock_kg_per_car"] = copies * float(row["mass_kg"])
    if (
        any(
            not isclose(groups[name], mass, abs_tol=0.002)
            for name, mass in frame["cut_stock_mass_kg"].items()
        )
        or sum(row["cut_count_per_car"] for row in rows) != frame["braced_mesh_component_count"]
    ):
        raise ValueError("Steel cut schedule differs from the braced frame record")
    return rows


def assembly(case, cfg, mass_account):
    """Transfer the shared six-car article geometry; take all fleet quantities from this opening."""
    frame = verified_record(FRAME, ROOT)
    civil = verified_record(CIVIL, CITY)
    system = verified_record(CITY / "system-results.json", ROOT)["networks"]["first"]
    schedule = json.loads(SCHEDULE.read_bytes())
    for name, digest in schedule["sources_sha256"].items():
        path = (CITY if name in ("system.toml", "system-results.json") else MECH) / name
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"Mechanical schedule needs rebuilding after {name} changed")
    geometry = cfg["vehicle_geometry"]
    bundle, power = case["bundle"], case["power"]
    braced = frame["braced_revision_id"]
    parent = system["selected_candidate_id"]
    mass_basis = mass_account["weight_return"]["basis"]
    if (
        case["candidate_id"] != identity(bundle)
        or case["parent"] != parent
        or bundle["parent"] != parent
        or frame["parent_train_id"] != parent
        or schedule["parent_selected_candidate_id"] != parent
        or schedule["parent_evaluation_id"] != system["selected_evaluation_id"]
        or frame["parent_interface_study_id"] != schedule["study_physical_id"]
        or civil["parent_physical_id"] != schedule["study_physical_id"]
        or civil["parent_evaluation_id"] != schedule["study_evaluation_id"]
        or bundle["vehicle_revision"] != braced
        or mass_basis.get("braced_revision") != braced
        or mass_basis.get("first_network_id") != parent
        or power["parent_candidate_id"] != case["candidate_id"]
        or bundle["supply"] != power["option"]
        or power["option"] != "protected_conductor"
        or bundle["pier_family"] != "separate-track"
        or bundle["span_m"] != civil["track"]["length_m"]
        or geometry != system["selected_station_interfaces"]["vehicle"]
        or cfg["station_geometry"] != system["selected_station_interfaces"]["station"]
    ):
        raise ValueError("Airport assembly needs matching opening, parent, frame, mass and civil revisions")
    cars = bundle["formation_cars"]
    fleet = bundle["active_sets"] + bundle["spares"]
    controls = case["controls"]
    bogies = len(schedule["train"]["body_bogie_x_m"])
    axles = len(schedule["train"]["body_axle_x_m"])
    doors = 2 * len(geometry["door_centres_m"])
    if (
        cars != len(schedule["train"]["car_centres_m"])
        or cars != cfg["vehicle"]["cars_per_train"]
        or fleet != power["common_service"]["fleet_trainsets"]
        or cars * axles != power["vehicle"]["driven_axles"]
        or controls["door_controllers"] != doors * cars * fleet
        or controls["brake_controllers"] != bogies * cars * fleet
    ):
        raise ValueError("Airport fleet and per-car running gear or door quantities disagree")
    if mass_return(mass_account["weight_return"], mass_basis) != mass_account:
        raise ValueError("Rebuild the Airport mass account from its supplier return")
    weighed_kg = mass_account["returned_crowd_train_kg"]
    if weighed_kg is not None and not isclose(weighed_kg / 1000, power["vehicle"]["mass_t"], abs_tol=1e-6):
        raise ValueError(
            "Propagate the returned train weight to the Airport vehicle before producing the BOM"
        )
    cuts = cut_schedule(frame, cars)
    counts = Counter()
    for row in cuts:
        counts[row["part"]] += row["cut_count_per_car"]
    parts = []

    def add(parent_assembly, name, per_car, detail, unit="each"):
        per_train = None if per_car is None else per_car * cars
        parts.append(
            {
                "assembly": parent_assembly,
                "item": name,
                "unit": unit,
                "per_car": per_car,
                "per_train": per_train,
                "fleet_quantity": None if per_train is None else fleet * per_train,
                "evidence_scope": detail,
            }
        )

    add("Car", "Braced steel body", 1, "Finished tare requires welds, inserts, fasteners and coating")
    add("Car", "Removable powered bogie", bogies, "Article geometry covers frames and seat plates")
    add("Powered bogie", "Wheelset", axles, "Two axle positions per bogie")
    add(
        "Powered bogie",
        "Axlebox bearing positions",
        2 * axles,
        "Bearing count and retention within each position by supplier",
    )
    add(
        "Powered bogie",
        "Axle drive module",
        axles,
        "One drive duty per driven axle. Quote motor, gearing, mount, inverter, cooling and harness",
    )
    add(
        "Powered bogie",
        "Primary spring interface",
        counts["primary_underside"],
        "Seat plate locations. Return spring, stop and damping quantities",
    )
    add("Car", "Secondary spring interface", counts["secondary_body"], "Opposed seat pair per location")
    add(
        "Powered bogie",
        "Brake controller",
        bogies,
        "Disc, caliper, actuator, hoses and parking mechanism to be itemised",
    )
    add(
        "Car",
        "Door opening and controller",
        doors,
        "Both installed sides. Specify slides, locks, retention, stops, harness and door leaves",
    )
    add(
        "Car",
        "Roof HVAC module",
        2,
        "Quotation arrangement. Return mass, fluids, electrical and lifting interfaces",
    )
    add(
        "Car",
        "Independent stopping and parking brake hardware",
        None,
        "Return friction pairs, actuation, wear limits, stored energy, duty, inspection and rescue interfaces",
    )
    add(
        "Car",
        "Drive and HVAC cooling circuits",
        None,
        "Return pumps, heat exchangers, branch isolation, flexible joints and operating fluids",
    )
    add(
        "Body joints",
        "Chord splice",
        counts["sill"] + counts["cantrail"] - 4,
        "Inspect full-strength longitudinal splices",
    )
    add(
        "Body joints",
        "Post-end joint",
        2 * (counts["jamb"] + counts["end_post"]),
        "Check jamb distortion and door clear aperture under load",
    )
    add(
        "Body joints",
        "Crossmember-end joint",
        2 * sum(counts[k] for k in ("floor_tie", "roof_tie", "end_tie", "bolster")),
        "Check bolster load transfer and access",
    )
    add("Body joints", "Brace-end connection", 2 * counts["brace"], "Two triangular gussets per connection")
    add(
        "Bogie joints",
        "Transom and saddle ends",
        2 * (counts["transom"] + counts["saddle"]),
        "Confirm weld access, fatigue detail and inspection",
    )
    add(
        "Bogie joints",
        "Primary and secondary pad attachments",
        counts["primary_underside"] + counts["secondary_top"],
        "Measure seat coplanarity before and after welding",
    )
    add(
        "Car",
        "Floor, skin, glazing, seats, wheelchair fittings and insulation",
        None,
        "Return item counts, materials, mounting, fire evidence and installed mass",
    )
    add(
        "Car",
        "Flexible wiring, hoses, couplers, bonds, fasteners and cooling",
        None,
        "Return lengths, sections, connector keys, bend radii, clamp counts, fluids and retention",
    )
    # Control packages are a train-level allocation; the doors and brake controllers above already cover theirs.
    for name in (
        "atp_channels",
        "radio_links",
        "tcms_nodes",
        "shoe_status_channels",
        "inverter_control_units",
        "train_service_power_units",
    ):
        total = controls[name]
        if total % fleet:
            raise ValueError(f"Incomplete control set for {name}")
        parts.append(
            {
                "assembly": "Train controls",
                "item": name,
                "unit": "each",
                "per_car": None,
                "per_train": total // fleet,
                "fleet_quantity": total,
                "evidence_scope": "Opening control allocation",
            }
        )
    rig = tomllib.loads((MECH / "quotation.toml").read_text())["rig"]
    track = case["civil"]
    quant = {
        "beam_count": track["beam_count"],
        "support_positions": track["pier_foundation_count"],
        "bearing_allowance": track["bearing_unit_allowance"],
        "trial_section_volume_m3_per_beam": civil["track"]["gross_concrete_m3"],
        "trial_bearing_xy_m": civil["track"]["bearing_xy_m"],
        "panel_count_per_uninterrupted_trial_island": civil["platform"]["panel_count_template"],
        "station_sites": len(bundle["stops"]),
        "grid_sites": bundle["grid_sites"],
        "section_gateways": controls["section_control_gateways"],
        "casting_yards": case["delivery"]["factory_yards_needed_at_declared_rate"],
        "erection_fronts": case["delivery"]["erection_fronts_needed_at_declared_rate"],
    }
    sources = [
        Path(__file__),
        CUTS,
        MECH / "vehicle/braced-frame.obj",
        FRAME,
        CIVIL,
        SCHEDULE,
        MECH / "quotation.toml",
        CITY / "VEHICLE.md",
        MECH / "vehicle/README.md",
        MECH / "vehicle/power_interface.py",
        MECH / "compare_returns.py",
        MECH / "vehicle/section-trial.toml",
        Path(baghdad_viaduct.__file__),
    ]
    result = {
        "candidate_id": case["candidate_id"],
        "opening_evaluation_id": case["evaluation_id"],
        "parent": parent,
        "frame_revision": braced,
        "civil_article_revision": civil["physical_id"],
        "source_sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in sources},
        "parts": parts,
        "cut_list": cuts,
        "cut_stock_kg_per_car": frame["braced_body_and_two_bogie_cut_stock_kg_per_car"],
        "mass_account": mass_account,
        "civil": quant,
        "datums": {
            "axes": "Straight level pose in metres. Origin at car centreline on rail head, x forwards, y left, z upwards.",
            "car_to_train_x_m": schedule["train"]["car_centres_m"],
            "bogie_to_car_x_m": schedule["train"]["body_bogie_x_m"],
            "straight_pose_rotation_degrees": [0, 0, 0],
            "axle_centres_car_x_m": schedule["train"]["body_axle_x_m"],
            "secondary_seat_y_plus_minus_m": rig["secondary_seat_lateral_m"],
            "primary_seat_y_plus_minus_m": rig["primary_seat_lateral_m"],
            "body_and_door_geometry": geometry,
            "vehicle_exchange": schedule["bogie_exchange"],
            "curve_screens": schedule["train"]["curve_screen"],
        },
        "production": production_lots(case, quant),
        "service_battery_per_train": {
            key: system["selected_service_power"][key]
            for key in (
                "nominal_battery_kwh_per_train",
                "declared_usable_kwh",
                "required_usable_kwh_with_reserve",
                "battery_mass_allowance_within_base_t",
                "outage_hours",
                "continuous_essential_kw",
                "scope",
            )
        },
        "load_distribution": {
            "opening_planning_gross_t": power["vehicle"]["mass_t"],
            "equal_split_t_per_car_sensitivity": power["vehicle"]["mass_t"] / cars,
            "equal_split_t_per_axle_sensitivity": power["vehicle"]["mass_t"] / (cars * axles),
            "returned_individual_axle_loads_kg": None,
            "return": "Weigh all wheel positions in the same tare and payload cases. Map HVAC, luggage, doors, wheelchair bays and the service battery to measured car datums.",
        },
        "demonstrator": demonstrator(case, cfg, frame, system),
        "interface_controls": interface_controls(cfg, civil),
        "geometric_budgets": geometric_budgets(geometry, civil),
        "alternatives": {
            "study": "cities/Baghdad/engineering/mechanical/vehicle/README.md#comparing-three-ways-to-build-the-body",
            "comparison": "Require equal openings, suspension datums, load and repair access. Compare weighed welded steel with a separately identified aluminium/GFRP body, its tooling, bonding, inspection, fire evidence, spare lead times and witnessed repair.",
            "hybrid_installed_mass_kg": None,
            "hybrid_installed_price_usd": None,
        },
        "holds": [
            "Approve interface tolerances and as-built inspection records before fabrication release.",
            "Weigh each installed mass group, load case and axle distribution. Re-run loads, energy, braking, structure and cost after a change.",
            "Release platform openings, complete bogie and car swept volumes, electrical isolation and site foundations against measured interfaces.",
        ],
        "physical_accepted": False,
        "fabrication_released": False,
    }
    result["evaluation_id"] = identity(result)
    return result


def production_lots(case, quantities):
    fleet = case["power"]["common_service"]["fleet_trainsets"]
    lots = [
        (
            "Representative car",
            1,
            "Jig sill and bolster datums, weld and inspect splices, fit doors and roof equipment, weigh completed car.",
            "Measure jamb diagonals, loaded threshold and roof removal clearance. Supply drawing, weld procedure, load case and repair trial.",
        ),
        (
            "Powered bogie",
            1,
            "Jig and weld frame, machine and inspect seats, install wheelsets, drive, brakes and disconnectable lines.",
            "Record wheel/seat alignment, bearing fits, torque retention and brake force. Demonstrate loaded roll-out on the intended pallet.",
        ),
        (
            "Viaduct beam",
            1,
            "Qualify mould and rebar cage, approve prestress and release strengths, cast and inspect before pick, ship, erect and survey.",
            "Return reinforcement schedule, tendon forces and losses, bearing rotation, lift anchors, ground report and erection-stage limits.",
        ),
        (
            "Accessible station bay",
            1,
            "Cast panels, form drainage and board edge, fit access and isolation equipment and check swept clearances.",
            "Measure platform gap, step, drainage, wheelchair circulation and door alignment under loaded, worn and thermal cases.",
        ),
        (
            "Traction and control module",
            1,
            "Assemble replaceable cabinets and contact interface, label terminals and verify wiring, isolation and protection.",
            "Submit single-line, terminal and connector schedule, heat rejection, fault interruption, safe egress and witnessed station visit.",
        ),
    ]
    return {
        "opening_trainsets": fleet,
        "production_beams": quantities["beam_count"],
        "draft_work_orders": [
            {
                "doctype": "Work Order",
                "docstatus": 0,
                "article": name,
                "qty": qty,
                "candidate_id": case["candidate_id"],
                "production_item": None,
                "bom_no": None,
                "routing": route,
                "inspection_and_handoff": checks,
            }
            for name, qty, route, checks in lots
        ],
        "issue_condition": "Workshop to allocate approved item/BOM and drawing revision, workstations, tooling, time, serials, warehouse and company before ERP entry. Quote pilot units separately from repeat series. Return calibration, inspection results, spares and maintainers' instructions.",
    }


def geometric_budgets(geometry, civil):
    """Direct mesh checks in the car frame; installed hardware and tolerance stacks remain open."""
    jambs = defaultdict(list)
    name = None
    for line in (MECH / "vehicle/braced-frame.obj").read_text().splitlines():
        if line.startswith("o "):
            name = line[2:].strip()
        elif name and name.startswith("jamb_") and line.startswith("v "):
            _, x, y, _ = line.split()
            jambs[name].append((float(x), float(y)))
    widths = []
    for sign in (-1, 1):
        posts = sorted(
            (min(x for x, _ in vertices), max(x for x, _ in vertices))
            for vertices in jambs.values()
            if vertices[0][1] * sign > 0
        )
        if len(posts) != 2 * len(geometry["door_centres_m"]):
            raise ValueError("Braced mesh must have a pair of jambs at each doorway")
        widths.extend(round(right[0] - left[1], 6) for left, right in zip(posts[::2], posts[1::2]))
    remaining = round(min(widths) - geometry["door_clear_width_m"], 6)
    return {
        "bare_steel_doorway_widths_m": widths,
        "remaining_combined_intrusion_and_tolerance_m": remaining,
        "door_return": "A positive seal, lining or door-guide intrusion requires a revised jamb layout or recessed hardware. Allocate welding and load distortion before freezing the fitted aperture.",
        "pad_geometric_end_margin_m": civil["track"]["pad_end_margin_m"],
        "pad_geometric_side_margin_m": civil["track"]["pad_side_margin_m"],
        "bearing_return": "These are distances to the stock edge for a centred pad. Deduct engineer-required bearing edge distance, movement, rotation and placement uncertainty before setting a tolerance.",
    }


def interface_controls(cfg, civil):
    """Nominals are article coordinates. Numerical acceptance tolerances require interface owners."""
    geom, station = cfg["vehicle_geometry"], cfg["station_geometry"]
    limits = [
        (
            "Door clear opening",
            geom["door_clear_width_m"],
            "m",
            "Door builder and accessibility lead",
            "Measure the unobstructed aperture after fitting and again under body load.",
        ),
        (
            "Straight platform gap at nominal car centre",
            station["straight_platform_edge_offset_m"] - geom["body_width_m"] / 2,
            "m",
            "Track, vehicle and accessibility leads",
            "Budget wheel wear, track and edge position, suspension travel, body sway, curved sweep and stopping error. Check a loaded boarding rig.",
        ),
        (
            "Bogie seat and wheelset alignment",
            geom["bogie_centres_m"],
            "m longitudinal centres",
            "Bogie and carbody engineers",
            "Survey seat planes and axle squareness before and after welding. Gauge bearing seats against the selected bearing fits.",
        ),
        (
            "Shoe and conductor alignment",
            geom["contact_rail_outboard_offset_m"],
            "m lateral datum",
            "Traction and track engineers",
            "Measure contact overlap and uplift throughout the suspension stroke, curvature and insulated gap. Prove isolation and electrical clearance.",
        ),
        (
            "Beam bearing centres",
            civil["track"]["bearing_xy_m"],
            "m local coordinates",
            "Civil and bearing engineers",
            "Survey pad elevations, support rotation, erection offsets, contact and jack access. Obtain concrete strength and alignment before release.",
        ),
    ]
    return [
        {
            "interface": name,
            "design_nominal": nominal,
            "unit": unit,
            "limit_owner": owner,
            "approved_tolerance": None,
            "inspection_and_limit_basis": method,
        }
        for name, nominal, unit, owner, method in limits
    ]


def demonstrator(case, cfg, frame, first):
    """Separately scoped procurement option for a 1.8 km instrumented, non-revenue trial."""
    route_km = 1.8
    geom = cfg["vehicle_geometry"]
    bundle = {
        "family": "Baghdad non-revenue demonstrator",
        "shared_frame_revision": frame["braced_revision_id"],
        "route_km": route_km,
        "track_count": 2,
        "span_m": 10,
        "pier_family": "separate-track",
        "instrumented_cars": 1,
        "test_berths": 1,
        "energised_tracks": 1,
        "separately_isolatable_sections": 2,
        "civil_load_basis_t": case["power"]["vehicle"]["mass_t"],
    }
    candidate = identity(bundle)
    works = baghdad_viaduct.evaluate(
        {"Demonstrator": route_km},
        span_m=10,
        common_pier=False,
        physical_candidate_id=candidate,
        train_crowd_mass_t=bundle["civil_load_basis_t"],
        rates=baghdad_viaduct.PlanningRates(**cfg["civil_rates"]),
        target_years=1,
        civil_start_year=1,
    )
    track_km = route_km * bundle["track_count"]
    civil_usd = works["prices"]["changed_elevated_scope_usd"]
    track_usd = track_km * cfg["capital_rates_usd_m"]["track_and_walkway_per_track_km"] * 1e6
    conductor_usd = route_km * cfg["power_price_allowances_usd_m"]["protected_conductor_per_track_km"] * 1e6
    cost = {
        "elevated_beams_supports_and_erection": civil_usd,
        "track_and_walkway": track_usd,
        "protected_conductor_equipment_one_track": conductor_usd,
    }
    published_train = first["selected_control_electronics"]["installed_train_items"]
    speed = cfg["vehicle"]["speed_cap_kmh"] / 3.6
    accel = cfg["power_assumptions"]["required_net_accel_m_s2"]
    brake = tomllib.loads((MECH / "vehicle/section-trial.toml").read_text())["braking_deceleration_m_s2"]
    # The coast interval is an illustrative test case. Net braking on a downgrade
    # is reduced and speed can increase during the coast. No credit for drag.
    coast_s = 2.0
    terminal_reserve = 120.0
    sensitivity = []
    for grade in (0, cfg["power_assumptions"]["adverse_grade"]):
        downhill = 9.80665 * grade
        if brake <= downhill:
            raise ValueError("No finite demonstrator stopping distance at assumed grade/deceleration")
        brake_entry = speed + coast_s * downhill
        coast_m = speed * coast_s + 0.5 * downhill * coast_s**2
        brake_m = brake_entry**2 / (2 * (brake - downhill))
        runup = speed**2 / (2 * accel)
        required = runup + coast_m + brake_m + geom["car_body_length_m"] + 2 * terminal_reserve
        sensitivity.append(
            {
                "downgrade_fraction": grade,
                "speed_at_withdrawal_m_s": speed,
                "coast_s_assumed": coast_s,
                "brake_entry_m_s": brake_entry,
                "runup_m": runup,
                "coast_m": coast_m,
                "braking_distance_m": brake_m,
                "terminal_reserve_m_each_end_assumed": terminal_reserve,
                "straight_length_required_m": required,
                "remaining_length_m": route_km * 1000 - required,
            }
        )
    result = {
        "candidate_id": candidate,
        "bundle": bundle,
        "civil_evaluation_id": works["evaluation_id"],
        "selection_purpose": "Separate prototype quotation option",
        "track_km": track_km,
        "conductor_track_km": route_km,
        "isolatable_section_lengths_km": [route_km / 2] * 2,
        "civil": works["quantities"],
        "article_and_controls": {
            "bogies": 2,
            "driven_axles": 4,
            "representative_door_controllers": cfg["vehicle"]["door_openings_per_car_each_side"] * 2,
            "bogie_brake_controllers": 2 * cfg["control_electronics"]["brake_controllers_per_bogie"],
            "car_io_nodes": cfg["control_electronics"]["tcms_nodes_per_car"],
            "station_dispatch_cabinets": 1,
            "train_end_protection_channels_for_bench": published_train["atp_channel"],
            "single_car_shoe_and_inverter_layout": None,
            "test_car_weighed_mass_kg": None,
            "single_car_service_battery_capacity_kwh": None,
        },
        "kinematic_screen": sensitivity,
        "screen_scope": "1.8 km tangent length includes both end reserves and one car. The 72 km/h case starts coasting at the speed cap. The downhill case accelerates during coast and would require a lower starting speed to enforce the cap. Measured stopping, detection latency, grade, overlaps, adhesion and containment govern permission for each speed step.",
        "priced_direct_scopes_usd": cost,
        "priced_direct_subtotal_usd": sum(cost.values()),
        "complete_installed_usd": None,
        "unpriced": [
            "Land, utilities, power connection, rectifier/protection and return network, test berth, cabinets and installation",
            "Equipped single test car, ballast, spares, instrumented restraint, recovery, independent logging and tools",
            "Survey, particular foundations and crossings, temporary works, assurance and commissioning",
        ],
        "stages": [
            "Select site and survey gradient, ground, utilities, road crossings, grid, evacuation, handling and recovery access.",
            "Verify welds, bearing seats, measured vehicle mass and installed load distribution. Test door, brake, drive and essential supply under restraint. Demonstrate manual recovery and isolation.",
            "Survey the completed track, establish physical stop limits and instrument both section boundaries. Witness breaker discrimination, backfeed, loss of one feed, return continuity and touch-voltage tests under approved applied loads.",
            "Use a separately reviewed speed ladder from crawl. Measure intervention latency and full independent stopping under degraded adhesion and zero line receptivity before advancing. Repeat at ballast extremes and through the powered-to-isolated boundary.",
            "Inspect joints, bearings, bogie retention, thermal duty and alignment after repeated cycles. Record removal, refit and local repair. The representative car does not establish six-car dynamics or passenger operation.",
        ],
        "fabrication_released": False,
        "physical_accepted": False,
    }
    result["evaluation_id"] = identity(result)
    return result
