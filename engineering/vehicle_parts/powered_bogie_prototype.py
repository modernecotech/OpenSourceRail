"""Bounded powered-bogie research child of the selected passive-wheel car.

The allocations are quotation envelopes, not installed component measurements.
No selected-reference or physical-acceptance state is changed here.
"""
from __future__ import annotations

import argparse
import gzip
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN = "docs/design-engine/v07-representative-car/plan.json"
EVALUATION = "docs/design-engine/current/evaluation.json.gz"
MANIFEST = "docs/design-engine/current/manifest.json"
G = 9.81


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode()


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def _source(root):
    plan = json.loads((root / PLAN).read_text())
    plan_identity = {key: value for key, value in plan.items() if key != "plan_id"}
    if sha256(encode(plan_identity)).hexdigest() != plan.get("plan_id"):
        raise ValueError("Selected representative-car plan identity differs")
    for path, expected in plan["source_sha256"].items():
        if digest(root / path) != expected:
            raise ValueError("Representative-car plan source changed: " + path)
    selected = json.load(gzip.open(root / EVALUATION, "rt"))
    manifest = json.loads((root / MANIFEST).read_text())
    for key in ("candidate_id", "evaluation_id", "selection_id"):
        if plan[key] != selected[key] or selected[key] != manifest[key]:
            raise ValueError("Selected candidate/evaluation/selection chain differs")
    if digest(root / EVALUATION) != manifest["files_sha256"]["evaluation.json.gz"]:
        raise ValueError("Selected evaluation is not sealed by current manifest")
    if selected["physical_accepted"] or selected["installed_mass_complete"]:
        raise ValueError("Expected an unqualified selected reference")
    return plan, selected


def _mass_rows(axles, roof_top):
    return [
        dict(id="motor-gear-cartridge", count_per_car=4, mass_each_budget_kg=[85, 180],
             nominal_centres_car_m=[[x, 0, 0.52] for x in axles],
             make_buy="buy rated motor/gear; make torque arm and mount locally after validation",
             scope="motor, reduction gear, torque reaction, housing and local fixings"),
        dict(id="inverter-cooled-rack", count_per_car=2, mass_each_budget_kg=[140, 280],
             nominal_centres_car_m=[[-2.2, -0.55, 0.63], [2.2, 0.55, 0.63]],
             make_buy="buy semiconductor and control core; make enclosure and coolant rack locally",
             scope="traction inverter, rack cooling and local protection; coolant flex tails excluded"),
        dict(id="roof-collector", count_per_car=1, mass_each_budget_kg=[100, 220],
             nominal_centres_car_m=[[0, 0, roof_top + 0.20]],
             make_buy="buy safety-rated collector; make roof mount locally after tests",
             scope="collector, insulators and roof mounting; OLE and contact wire excluded"),
        dict(id="roof-hv-isolation", count_per_car=1, mass_each_budget_kg=[65, 160],
             nominal_centres_car_m=[[1.6, 0, roof_top + 0.18]],
             make_buy="buy breakers and surge components; make enclosure locally",
             scope="surge, isolation, protection and enclosure; feeder equipment excluded"),
        dict(id="independent-rail-brake-bogie", count_per_car=2, mass_each_budget_kg=[200, 315],
             nominal_centres_car_m=[[-6.4, 0, 0.17], [6.4, 0, 0.17]],
             make_buy="buy qualified magnet/shoe for prototype; make support structure locally after rail tests",
            scope="two nominal 1 m rail shoes, actuator, retention and local fixings per bogie"),
        dict(id="traction-cables-and-flex-tails", count_per_car=1,
             mass_each_budget_kg=[90, 200], nominal_centres_car_m=None,
             make_buy="make harness locally from sourced rated cable and connectors",
             scope="HV cable, earthing, flexible bogie and cooling connections; route not laid out"),
        dict(id="mounts-and-fasteners", count_per_car=1,
             mass_each_budget_kg=[70, 180], nominal_centres_car_m=None,
             make_buy="make locally after material, fatigue and torque qualification",
             scope="structural brackets, bolts, retention, guards and access covers; not detailed"),
    ]


def _located_budget_cg(rows):
    placed = [r for r in rows if r["nominal_centres_car_m"] is not None]
    cases = []
    for choice in product((0, 1), repeat=len(placed)):
        masses = [r["mass_each_budget_kg"][end] for r, end in zip(placed, choice)]
        total = sum(m * r["count_per_car"] for m, r in zip(masses, placed))
        moments = [sum(m * sum(c[axis] for c in r["nominal_centres_car_m"])
                       for m, r in zip(masses, placed)) for axis in range(3)]
        cases.append([x / total for x in moments])
    return dict(placed_mass_budget_kg=[
                    sum(r["count_per_car"] * r["mass_each_budget_kg"][end]
                        for r in placed) for end in (0, 1)],
                point_allocation_CG_bounds_car_xyz_m=[
                    [min(c[axis] for c in cases), max(c[axis] for c in cases)]
                    for axis in range(3)],
                excluded="traction cables, flexible cooling, mounts, selected residual and removed secondary")


def build(root=ROOT):
    root = Path(root)
    plan, selected = _source(root)
    vehicle = selected["vehicle"]
    axles = plan["nominal_geometry"]["axle_x_m"]
    if axles != [-7.45, -5.35, 5.35, 7.45]:
        raise ValueError("Selected axle datums changed")
    if plan["formation"] != dict(axles_per_car=4, boarding_side="+y",
            bogies_per_car=2, car_body_length_m=17.0, cars=6, doors_per_car=2,
            fixed_seats_per_car=44, planned_standing=0,
            wheelchair_places_per_car=2):
        raise ValueError("Selected passenger/running reference changed")
    brake_discs = [p for p in vehicle["geometry_parts"]
                   if p["id"].startswith("bogie/0/brake/0/") and p["id"].endswith("/disc")]
    if len(brake_discs) != 2:
        raise ValueError("Selected wheel-brake disc geometry changed")
    left = max(p["at_m"][1] + p["length_m"] for p in brake_discs if p["at_m"][1] < 0)
    right = min(p["at_m"][1] for p in brake_discs if p["at_m"][1] > 0)
    disc_gap = right - left
    swept_half_y = 0.26 + 0.05  # Proposed 50 mm lateral reservation, unapproved.
    side_margin = min(-swept_half_y - left, right - swept_half_y)
    if side_margin <= 0 or disc_gap < 0.62:
        raise ValueError("No nominal swept drive width between retained brake discs")
    floor_underside = vehicle["clearance"]["floor_underside_m"]
    motor_swept_top = 0.78 + 0.05
    if floor_underside <= motor_swept_top:
        raise ValueError("Motor allocation intersects selected floor envelope")
    roof = [p for p in vehicle["geometry_parts"]
            if p["id"].startswith("comfort-shell/roof/") and p["kind"] == "box"]
    roof_top = max(p["at_m"][2] + p["size_m"][2] for p in roof)
    passive_fin = sum(p["mass_kg"] for p in vehicle["geometry_parts"]
                      if p["id"].startswith("station-secondary/"))
    if abs(passive_fin - 275.342775) > 1e-5:
        raise ValueError("Counted passive secondary material changed")

    physical = dict(schema="osr-v07-powered-bogie-research-child/1",
        parent_candidate_id=plan["candidate_id"],
        parent_selection_id=plan["selection_id"],
        configuration="six individually powered cars, four motorised axles/car",
        cars=6, body_length_m=17.0, normal_places_per_car=46,
        boarding_side="+y", rail_gauge_m=1.435,
        bogie_centres_car_x_m=[-6.4, 6.4], axle_centres_car_x_m=axles,
        driven_axles_per_car=4, driven_axles_per_train=24,
        electrical_pickup="one 1.5 kV DC roof collector per car; rigid protected overhead contact",
        traction_store="none selected; retained 82.8 kWh/car service battery remains service-only",
        station_limiter="retire centre passive aluminium fin and wayside LIM primary in this child",
        independent_brake="one two-shoe rail-contact module per bogie; required forces only",
        bogie_module=dict(frame="car x forward, y left, z up; rail running surface z=0",
            motor_box_size_m=[0.64, 0.52, 0.52],
            motor_box_centres_car_m=[[x, 0, 0.52] for x in axles],
            motor_rigid_rotation_car=[1, 0, 0, 0, 1, 0, 0, 0, 1],
            bogie_to_car_translations_m=[[-6.4, 0, 0], [6.4, 0, 0]],
            axle_to_bogie_translations_m=[[-1.05, 0, 0], [1.05, 0, 0]],
            proposed_sweep_reservation_xyz_m=[0.05, 0.05, 0.05],
            axle_shaft_interface="retained shaft axis z=0.38 m, but motor bore/gear coupling unapproved"),
        track_brake_module=dict(count_per_bogie=1, shoes_per_module=2,
            centres_car_m=[[-6.4, 0, 0.17], [6.4, 0, 0.17]],
            shoe_centres_y_m=[-0.7175, 0.7175],
            shoe_reference_size_m=[1.0, 0.106, 0.115],
            stowed_pair_box_size_m=[1.0, 1.70, 0.115],
            stowed_pair_box_bottom_m=0.12, deployed_rail_contact_z_m=0,
            deployment_and_track_clearance_verified=False),
        roof_collector=dict(base_centre_car_m=[0, 0, round(roof_top, 6)],
            stowed_box_size_m=[1.30, 0.80, 0.40],
            proposed_deployed_top_above_rail_m=4.80,
            controlled_contact_wire_height_m=None),
        selected_door_centres_x_m=[-4.5, 4.5],
        selected_door_width_m=1.4)
    child_id = sha256(encode(physical)).hexdigest()
    rows = _mass_rows(axles, roof_top)
    for row in rows:
        row.update(supplier=None, quoted_unit_price_usd=None,
                   local_value_added_fraction=None, process_hours=None,
                   approved_drawing_id=None)
    lo = sum(r["count_per_car"] * r["mass_each_budget_kg"][0] for r in rows)
    hi = sum(r["count_per_car"] * r["mass_each_budget_kg"][1] for r in rows)
    accounted = plan["mass_account"]["accounted_tare_kg_per_car"]
    normal = selected["vehicle"]["mass"]["accounted_cap_loaded_kg_per_car"]
    child_normal_hi = (normal + hi - passive_fin) * 6
    stop_force = child_normal_hi * (0.6 + G * .02)
    one_out_module = stop_force / 11
    stop_distance = 20**2 / (2 * .6)
    source = {path: digest(root / path) for path in (PLAN, EVALUATION, MANIFEST)}
    source["engineering/vehicle_parts/powered_bogie_prototype.py"] = digest(Path(__file__))
    result = dict(schema="osr-v07-powered-vehicle-prototype-plan/1",
        physical_candidate_id=child_id,
        selected_parent_candidate_id=plan["candidate_id"],
        selected_parent_evaluation_id=plan["evaluation_id"],
        selected_parent_selection_id=plan["selection_id"],
        research_selection_id=None, physical_definition=physical,
        electrical_architecture_component_id=None,
        same_candidate_service_and_mass_evaluation_verified=False,
        coordinator_join="Pending exact electrical configuration/source linkage and re-evaluation at this child mass; mechanical child is not the electrical demand candidate",
        source_sha256=source,
        nominal_geometry_screen=dict(
            inner_brake_disc_gap_m=disc_gap,
            motor_swept_lateral_clearance_each_side_m=side_margin,
            motor_swept_top_to_floor_underside_m=floor_underside - motor_swept_top,
            motor_worn_wheel_bottom_above_rail_m=0.26 - 0.05 - (0.76 - 0.68) / 2,
            roof_top_above_rail_m=roof_top,
            full_bogie_yaw_suspension_and_curves_verified=False,
            motor_bore_and_gear_fit_verified=False,
            track_brake_sweep_verified=False,
            roof_collector_to_structure_and_OLE_verified=False),
        mass_budget=dict(rows=rows,
            provisional_equipment_allocation_kg_per_car=[lo, hi],
            located_allocation_only=_located_budget_cg(rows),
            counted_removed_secondary_kg_per_car=passive_fin,
            conditional_accounted_tare_arithmetic_kg_per_car=[accounted + lo - passive_fin,
                                                                accounted + hi - passive_fin],
            selected_accounted_tare_kg_per_car=accounted,
            selected_unlocated_account_kg_per_car=plan["mass_account"]["residual_reference_or_unlocated_kg_per_car"],
            installed_tare_kg_per_car=None, installed_CG_m=None,
            installed_axle_reactions_N=None,
            reason="Budget ranges are unquoted and cable/mount CGs unlocated; selected residual and service-pack fit remain open"),
        independent_brake_demand=dict(
            basis="high conditional normal-load arithmetic, 2% downgrade, 0.6 m/s2 net stop, all wheel brakes unavailable",
            normal_train_mass_kg=child_normal_hi,
            required_total_rail_brake_force_N=stop_force,
            required_per_module_N_with_one_of_twelve_unavailable=one_out_module,
            required_per_shoe_N_with_one_module_unavailable=one_out_module / 2,
            peak_thermal_power_per_active_module_W=one_out_module * 20,
            stop_energy_per_active_module_J=one_out_module * stop_distance,
            brake_excitation_power_W_per_module=None,
            protected_energy_for_OLE_loss_J=None,
            actuator_drop_and_stow_verified=False,
            independent_fail_safe_parking_verified=False,
            service_battery_certified_for_brake_excitation=False,
            verified_adhesion=False, verified_rail_compatibility=False,
            verified_hot_stop=False),
        rail_brake_catalogue_reference=dict(
            source="Knorr-Bremse MagnetAct P-1269, April 2024",
            url="https://rail.knorr-bremse.com/media/2000-products/product-broschures/p-1269-magnetact.pdf",
            rigid_shoe_dimensions_mm=[106, 115, 1000],
            rigid_shoe_mass_kg_per_m=75,
            rigid_shoe_attractive_force_kN_per_m=72,
            count_two_shoes_per_bogie=24,
            bare_reference_shoe_mass_kg_per_train=1800,
            longitudinal_braking_force_N=None,
            note="Attractive force is not rail-direction braking force; vendor and rail compatibility unselected"),
        interface_control=[
            dict(id="axle-motor-gear", datum="selected four axle axes at z=0.38 m",
                 nominal_box_m=[0.64, 0.52, 0.52], approved_tolerance_m=None,
                 loads="peak/repeated torque, bearing reaction, fatigue, one-axle isolation"),
            dict(id="carbody-bogie-rack", datum="bogie centres ±6.4 m and floor underside 0.9357 m",
                 nominal_box_m=[1.0, 0.45, 0.35], approved_tolerance_m=None,
                 loads="rack gravity, vibration, cooling leakage, train dynamic envelope"),
            dict(id="rail-contact-brake", datum="rail centres ±0.7175 m, two 1 m shoes/bogie",
                 nominal_box_m=[1.0, 1.70, 0.115], approved_tolerance_m=None,
                 loads="longitudinal stop force, protected excitation during OLE loss, actuator release, fail-safe parking, hot rail contact, turnout crossing"),
            dict(id="roof-collector-OLE", datum=f"roof top {roof_top:.4f} m above rail",
                 nominal_box_m=[1.30, 0.80, 0.40], approved_tolerance_m=None,
                 loads="contact force, uplift, section gaps, earthing and civil electrical clearance"),
            dict(id="service-battery-isolation", datum="retained service-only 82.8 kWh pack",
                 nominal_box_m=None, approved_tolerance_m=None,
                 loads="separate traction fault isolation and auxiliary/rescue supply"),
        ],
        provisional_quote_interface_counts_per_car=dict(
            motor_gear_cartridges=4, axle_coupling_kits=4,
            torque_reaction_arms=4, compliant_motor_mount_bushes=8,
            motor_cartridge_mount_bolts=32,
            inverter_cooled_racks=2, rack_mount_bolts=16,
            roof_collectors=1, collector_mount_bolts=8,
            roof_isolation_boxes=1, isolation_mount_bolts=8,
            track_brake_modules=2, rail_shoes=4,
            brake_lifting_actuators=4, brake_guide_slides=4,
            brake_retention_pins=8, brake_end_stops=8,
            brake_shoe_mount_bolts=16,
            flexible_bogie_hv_loops=4, flexible_bogie_earth_loops=2,
            flexible_cooling_supply_return_hoses=4,
            bearing_counts="vendor gearbox, motor and axle bearing design unknown; not assumed zero",
            status="minimum quotation interface counts, not released manufacturing BOM"),
        assembly_and_repair=dict(
            sequence=[
                "Fixture existing bogie and axle datums; survey disc, bolster and suspension clearances.",
                "Fit axle coupling, motor/gear cartridge, torque arm and eight proposed fasteners per axle; gauge swept travel.",
                "Fit two rail-contact brake shoes, guides, stops, actuators and retention on each bogie; prove fail-safe stow.",
                "Fit two cooled inverter racks underfloor with guarded isolation and route flexible HV, earth and coolant loops.",
                "Strengthen and inspect roof collector and protection mounts; prove safe earthing and insulation boundaries.",
                "Marry bogies to carbody, gauge both door openings and all service/evacuation routes, then weigh each car.",
                "Run guarded low-speed traction and independent-stop tests before hot-duty or full-speed tests."],
            removal=[
                "Isolate and earth overhead feed; lock out traction DC, service battery, brake energy and coolant pressure.",
                "Support carbody on approved lifting points and isolate one bogie; disconnect labelled flex tails at dry-break points.",
                "Remove track-brake shoes downward only over a service pit, with module retention supported.",
                "Remove motor/gear cartridge laterally between existing brake discs after axle-coupling release; 52 mm nominal swept side margin is not tool access approval.",
                "Replace parts with serial/lot and torque/insulation records, then repeat axle, brake and clearance QA."],
            qa_hold_points=[
                "Survey mating datums and finite bogie travel before machining brackets.",
                "Approve axle torque reaction, fastener class/torque, gear bearing and fatigue evidence.",
                "Measure rail-brake longitudinal force, one-module-out stopping, heat and rail damage on selected rail.",
                "Measure collector contact, section-gap behaviour, insulation and earthing on representative overhead line.",
                "Weigh complete installed car and record CG and each axle reaction before service-envelope acceptance."],
            approved_lifting_points=None, minimum_tool_sweep_verified=False,
            supplier_assembly_hours=None, measured_repair_hours=None),
        quote_and_test_holds=[
            "Supply motor/gear dimensions, masses, speed/torque and axle-coupling drawings for four driven axles per car.",
            "Measure finite bogie yaw, roll, heave, wheel wear and curve envelopes; the 50 mm sweep is only a reservation.",
            "Size motor and gearbox bearings, torque arms, resilient mounts, fasteners, guards and extraction path.",
            "Approve inverter/cooling racks, DC breakers, roof collector insulation, earthing and rigid OLE civil envelope.",
            "Detail flexible bogie HV/earth/cooling loops at full travel, separation, strain relief and replacement access.",
            "Test two-shoe track brake on the actual rail and crossing/turnout family under one-module-out, hot and faulted stops.",
            "Weigh and locate all new equipment, the removed fin, and the selected 10,090.2 kg residual before whole-car CG or axle loads.",
            "Keep service battery for independently sized services; separately prove emergency movement or protected tow.",
            "Check six roof collectors, sectioning, arcing, regenerative sink and safe isolation; one-per-two-car pickup is a future cost alternative.",
        ],
        complete_installed_BOM=False, installed_mass_complete=False,
        engineering_accepted=False, manufacturing_release=False,
        operating_release=False, physical_accepted=False,
        selected_reference_changed=False)
    result["evaluation_id"] = sha256(encode(result)).hexdigest()
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "check"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = encode(build())
    if args.action == "build":
        if args.output.exists():
            raise ValueError("Fresh output path required")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
    elif args.output.read_bytes() != payload:
        raise ValueError("Powered-vehicle plan differs from current sources")
    print(json.dumps({"verified": True, "evaluation_id": json.loads(payload)["evaluation_id"],
                      "physical_accepted": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
