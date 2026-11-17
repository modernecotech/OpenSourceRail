"""Joint-free 10 m civil quotation screen using the current box-beam evaluator.

The result is a necessary-bound gross-elastic study, never structural approval.
The same crowd-sized physical beam stock is evaluated at normal and crowd load.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from math import isclose, sqrt
from pathlib import Path

from engineering.development_baseline import selection
from engineering.design_search.craft_backends import civil_moving_load
from engineering.station_rail import civil
from engineering.station_rail.common import digest, identity


ROOT = Path(__file__).resolve().parents[2]
INPUT = Path("docs/design-engine/v07-simple-span/input.json")
OUTPUT = Path("docs/design-engine/v07-simple-span/plan.json")
POWERED = Path("docs/design-engine/v07-powered-vehicle/plan.json")
SERVICE = Path("docs/design-engine/v07-architecture-decision/result.json")
SEGMENTED = Path("docs/design-engine/v07-segmented-span/plan.json")
PRODUCER = Path("engineering/design_search/simple_span_prototype.py")
SOURCE_FILES = (
    INPUT, POWERED, SERVICE, SEGMENTED, PRODUCER,
    Path("engineering/development-baseline.toml"),
    Path("engineering/development_baseline/selection.py"),
    Path("engineering/development_baseline/propulsion_policy.py"),
    Path("engineering/station_rail/brief.toml"),
    Path("engineering/station_rail/civil.py"),
    Path("engineering/station_rail/vehicle.py"),
    Path("engineering/station_rail/common.py"),
    Path("engineering/design_search/craft_backends/civil_moving_load.py"),
)


def encoded(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def _read(root: Path, path: Path) -> dict:
    file = root / path
    if file.is_symlink() or not file.is_file():
        raise ValueError("Regular source packet required: " + str(path))
    return json.loads(file.read_bytes())


def _case(row: dict) -> dict:
    """Keep all local sections, but no unrelated evaluator implementation state."""
    return {
        "load_case": row["load_case"],
        "physical_civil_component_id": row["physical_civil_component_id"],
        "alternative_evaluation_id": row["alternative_id"],
        "accounted_span_stock_mass_kg": row["total_counted_span_mass_kg"],
        "concrete_m3": row["concrete_m3"],
        "counted_steel_kg": row["counted_steel_kg"],
        "prestress_strands": row["prestress_strands"],
        "initial_prestress_N_hypothesis": row["prestress_initial_N"],
        "effective_prestress_N_hypothesis": row["prestress_effective_N"],
        "maximum_live_moment_Nm": row["maximum_live_moment_Nm"],
        "maximum_service_tension_Pa": row["max_service_tension_Pa"],
        "maximum_service_compression_Pa": row["max_service_compression_Pa"],
        "maximum_transfer_tension_Pa": row["max_release_tension_Pa"],
        "maximum_transfer_compression_Pa": row["max_release_compression_Pa"],
        "gross_elastic_deflection_envelope_m": row["deflection_upper_bound_m"],
        "provisional_model_screen": row["necessary_longitudinal_screen"],
        "screen_is_structural_acceptance": False,
        "moving_load_local_envelope": [
            {key: section[key] for key in (
                "x_m", "max_live_moment_Nm", "max_service_tension_Pa",
                "max_service_compression_Pa", "max_release_tension_Pa",
                "max_release_compression_Pa")}
            for section in row["moving_load_envelope"]
        ],
    }


def build(root: Path = ROOT) -> dict:
    root = Path(root)
    inp = _read(root, INPUT)
    powered = _read(root, POWERED)
    service = _read(root, SERVICE)
    segmented = _read(root, SEGMENTED)
    selected = selection.load(root)
    parent = selected["vehicle"]
    if (inp["schema"] != "osr-v07-simple-span-input/1"
            or inp["parent_selected_vehicle_candidate_id"] != parent["candidate_id"]
            or powered["physical_candidate_id"] != inp["powered_vehicle_child_id"]
            or powered["selected_parent_candidate_id"] != parent["candidate_id"]
            or service["selected_reference_vehicle_candidate_id"] != parent["candidate_id"]
            or segmented["physical_candidate_id"] != inp["segmented_20m_comparator_id"]
            or inp["span_m"] != 10.0 or inp["route_m"] != 2000 or inp["tracks"] != 2
            or inp["rail_gauge_mm"] != 1435 or inp["train_cars"] != 6
            or inp["design_load_case"] != "crowd_control"
            or inp["bearing_units_per_beam_hypothesis"] != 4
            or inp["mandatory_safety_accessibility_unrelaxed"] is not True):
        raise ValueError("Explicit research identity or construction scope differs")
    added = inp["powered_equipment_mass_allowance_kg_per_car"]
    if (added != service["powered_wheel_mass_sensitivity"]["added_equipment_mass_hypothesis_kg_per_car"]
            or not 0 < added <= 10000
            or powered["physical_accepted"] is not False
            or segmented["physical_accepted"] is not False):
        raise ValueError("Powered mass allowance or research evidence differs")
    vehicle = deepcopy(parent)
    vehicle["candidate_id"] = powered["physical_candidate_id"]
    for key in ("accounted_tare_kg_per_car", "accounted_cap_loaded_kg_per_car",
                "accounted_160_control_kg_per_car"):
        vehicle["mass"][key] += added
    if not isclose(vehicle["mass"]["accounted_cap_loaded_kg_per_car"], 25071.998134341986, abs_tol=1e-6):
        raise ValueError("Powered normal load context changed")
    crowd = civil.alternative(vehicle, 10.0, "box-beam", "crowd_control")
    normal = civil.alternative(vehicle, 10.0, "box-beam", "normal",
                               fixed_strands=crowd["prestress_strands"])
    if normal["physical_civil_component_id"] != crowd["physical_civil_component_id"]:
        raise ValueError("Normal and crowd evaluations must use one beam stock")
    axles = civil_moving_load.axle_positions(vehicle)
    axle_N = vehicle["mass"]["accounted_160_control_kg_per_car"] * civil.G / 4 * 1.3
    independent = civil_moving_load.envelope(10.0, axles, axle_N, [], 0.25)
    if not isclose(independent["max_moment"]["moment_Nm"],
                   crowd["maximum_live_moment_Nm"], rel_tol=1e-10):
        raise ValueError("Independent moving-load moment differs")
    beams_per_track = inp["route_m"] // int(inp["span_m"])
    beam_count = beams_per_track * inp["tracks"]
    supports = (beams_per_track + 1) * inp["tracks"]
    bearings = beam_count * inp["bearing_units_per_beam_hypothesis"]
    if (beam_count, supports, bearings) != (400, 402, 1600):
        raise ValueError("Straight-span quantity basis differs")
    comparator = segmented["straight_span_quantities"]["demonstrator_2km"]
    if (comparator["beam_spans"], comparator["required_piece_lifts"],
            comparator["independent_supports"], comparator["bearings"]) != (200, 400, 202, 800):
        raise ValueError("Segmented comparator quantity basis differs")
    beam_mass = crowd["construction"]["reference_max_piece_kg"]
    hook = beam_mass * (1 + inp["rigging_and_hoist_fraction_hypothesis"])
    reaction = crowd["foundation_scenarios"][1]["dead_plus_train_support_reaction_N"]
    footing_t = inp["footing_thickness_m_gravity_only_hypothesis"]
    gravity = []
    for soil in inp["soil_allowable_kPa_sensitivities"]:
        min_area = reaction / (soil * 1000 - 2500 * civil.G * footing_t)
        gravity.append({"soil_allowable_kPa_hypothesis": soil,
                        "minimum_square_width_m_including_footing_self_weight": sqrt(min_area),
                        "minimum_area_m2_including_footing_self_weight": min_area,
                        "soil_and_settlement_approved": False})
    physical = {
        "schema": "osr-v07-joint-free-civil-physical-research/1",
        "beam_section_and_stock_id": crowd["physical_civil_component_id"],
        "span_m": 10.0, "track_gauge_mm": inp["rail_gauge_mm"],
        "independent_two_track_beams": True,
        "beam_to_beam_midspan_joint": "none",
        "bearing_units_per_beam_hypothesis": inp["bearing_units_per_beam_hypothesis"],
        "support_family": "independent simply supported beam seats at each 10 m line",
        "foundation_geometry": None,
    }
    civil_id = identity(physical)
    if civil_id == segmented["physical_candidate_id"]:
        raise ValueError("Joint-free revision must have distinct physical identity")
    source_map = {str(path): digest(root / path) for path in SOURCE_FILES}
    result = {
        "schema": "osr-v07-joint-free-span-prototype-plan/1",
        "input_id": identity(inp),
        "physical_candidate_id": civil_id,
        "physical_definition": physical,
        "beam_component_id": crowd["physical_civil_component_id"],
        "vehicle_research_child_id": powered["physical_candidate_id"],
        "vehicle_load_scope": "24 motor axles with +2.4 t/car preliminary equipment; not complete installed mass or axle distribution",
        "load_model": {
            "axles_per_car": 4,
            "peak_crowd_dynamic_axle_N": axle_N,
            "dynamic_load_factor_hypothesis": 1.3,
            "speed_cap_kmh": inp["speed_cap_kmh"],
            "wheel_load_distribution_or_track_dynamics_measured": False,
            "maximum_support_shear_N": None,
            "shear_capacity_verified": False,
        },
        "parent_selected_vehicle_id": parent["candidate_id"],
        "selected_reference_changed": False,
        "normal_accounted_mass_kg_per_car": vehicle["mass"]["accounted_cap_loaded_kg_per_car"],
        "crowd_control_accounted_mass_kg_per_car": vehicle["mass"]["accounted_160_control_kg_per_car"],
        "complete_installed_mass_kg_per_car": None,
        "normal_load": _case(normal),
        "crowd_control_load": _case(crowd),
        "independent_crowd_moving_load_check": {
            "section_step_m": 0.25,
            "maximum_live_moment_Nm": independent["max_moment"]["moment_Nm"],
            "force_residual_N": independent["maximum_balance_residual_N"],
            "matches_primary_model": True,
        },
        "torsion": {
            "ideal_equal_rail_vertical_torsion_Nm": 0.0,
            "one_axle_all_load_on_one_rail_torsion_demand_Nm_hypothesis": axle_N * inp["rail_gauge_mm"] / 2000,
            "actual_unequal_rail_torsion_envelope_Nm": None,
            "cross_section_torsional_resistance_Nm": None,
        },
        "prestress_transfer": {
            "crowd_sized_strands": crowd["prestress_strands"],
            "normal_same_stock_confirmed": True,
            "gross_release_tension_Pa_hypothesis": crowd["max_release_tension_Pa"],
            "gross_release_compression_Pa_hypothesis": crowd["max_release_compression_Pa"],
            "anchorage_zone_and_bond_verified": False,
            "local_shear_and_fatigue_verified": False,
        },
        "handling": {
            "one_piece_bare_kg_accounted": beam_mass,
            "hook_kg_with_25pct_hypothesis": hook,
            "provisional_road_payload_kg": inp["provisional_road_payload_kg"],
            "minimum_one_beam_per_trip_haul_movements_hypothesis": beam_count,
            "road_axle_permits_and_swept_path_verified": False,
            "provisional_crane_radius_m": inp["provisional_crane_radius_m"],
            "provisional_crane_chart_kg_at_12m": inp["provisional_crane_chart_capacity_kg_at_radius"],
            "actual_chart_at_radius_and_ground_verified": False,
            "lift_insert_and_temporary_lateral_stability_verified": False,
        },
        "foundation": {
            "peak_interior_support_reaction_N_excluding_pier_and_footing_self_weight": reaction,
            "soil_hypothesis_gravity_only": gravity,
            "site_ground_and_settlement": None,
            "lateral_uplift_scour_and_seismic": None,
            "footing_and_pier_physical_definition": None,
            "shared_two_track_crosshead_alternative_evaluated": False,
        },
        "deformation_feedback": {
            "gross_beam_crowd_vertical_upper_m": crowd["deflection_upper_bound_m"],
            "approved_rail_or_OLE_relative_motion_budget_m": None,
            "actual_twist_creep_settlement_and_bearing_rotation": None,
            "magnetic_support_gap_selected": False,
        },
        "straight_two_track_2km_quantities": {
            "newly_designed_10m_beams": beam_count,
            "one_piece_lifts": beam_count,
            "independent_pier_and_foundation_supports": supports,
            "bearing_units_hypothesis": bearings,
            "midspan_structural_joints": 0,
            "midspan_joint_towers": 0,
            "temporary_lateral_bracing_design_required": True,
            "accounted_beam_concrete_m3": beam_count * crowd["concrete_m3"],
            "accounted_beam_steel_kg": beam_count * crowd["counted_steel_kg"],
            "direct_fastener_sets": beam_count * crowd["direct_fastener_sets"],
            "rail_stock_m": inp["route_m"] * inp["tracks"] * 2,
            "actual_support_and_erection_cost_usd": None,
        },
        "jointed_20m_comparator_counts": {
            "physical_candidate_id": segmented["physical_candidate_id"],
            "beam_spans": comparator["beam_spans"],
            "piece_lifts": comparator["required_piece_lifts"],
            "independent_supports": comparator["independent_supports"],
            "bearings": comparator["bearings"],
            "structural_midspan_joints": comparator["beam_spans"],
            "temporary_tower_placements": comparator["temporary_tower_placements"],
            "same_powered_load_and_installed_cost": None,
        },
        "erection_cycle_comparison": {
            "joint_free_beam_lifts_per_10m_track_span": 1,
            "joint_free_midspan_joint_operations": 0,
            "jointed_20m_beam_lifts_per_20m_track_span": 2,
            "jointed_midspan_joint_operations_per_20m_track_span": 1,
            "field_hours_per_cycle": None,
            "temporary_bracing_and_crane_moves_per_cycle": None,
        },
        "construction_sequence": [
            "Survey utilities, ground, two-track centreline, station transitions and crane standing/haul route.",
            "Design and cast site-specific footings, piers, independent beam seats and protected access; cure to approved strength.",
            "Fabricate one 10 m joint-free box per track/span with approved cage, tendons, anchors, end diaphragms, lifting inserts and rail/bearing datums.",
            "Verify crane chart, lift points, road axle/turning limits, weather and temporary lateral bracing before each single-piece lift.",
            "Land beams on surveyed bearings, brace and survey seats, rails, OLE mount and accessible maintenance envelope.",
            "Install continuous rails, drainage, protected access, return/earthing and overhead supply after isolation and clearance design.",
            "Proof-load representative span, measure deflection/twist/bearing and ground settlement, then independently review before prototype construction release.",
        ],
        "quote_and_qa_requests": [
            "Precast beam and tendon/anchor design, one-piece factory hours, mould cycle, local material and repair method.",
            "Site-specific 402 support/foundation and 1600 bearing-unit quotation with land, utilities, drainage, access and settlement limits.",
            "Certified 30 t-class piece haul route/permit and configuration-specific crane chart at measured radius; rigging and lift insert proof.",
            "Temporary lateral stability, bearing seat and rail/OLE fixation tolerances, full-load proof and fatigue/inspection plan.",
        ],
        "native_solver": {
            "status": "held-before-admission",
            "reason": "No controlled tendon/rebar/anchor-zone/seat geometry, lateral and braking loads, bearing stiffness, cracked material law or site soil; a Code_Aster/CalculiX solve now would not close those obligations.",
            "next_exact_input": "Approved 10 m shop model with tendon/rebar/anchor and lift inserts, bearing/rail/OLE coordinates, load combinations, material tests, site soil and resource request.",
            "jobs_executed": 0,
        },
        "single_installed_price_usd": None,
        "whole_life_cost_usd": None,
        "evidence_maturity": "analytical necessary-bound and quotation planning",
        "engineering_screen": "held",
        "physical_accepted": False,
        "manufacturing_release": False,
        "operating_release": False,
        "source_sha256": source_map,
    }
    result["evaluation_id"] = identity(result)
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "check"))
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    raw = encoded(build())
    target = args.output
    if args.action == "build":
        if target.exists():
            raise ValueError("Fresh output path required")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    elif target.read_bytes() != raw:
        raise ValueError("Simple-span packet differs from current sources")
    data = json.loads(raw)
    print(json.dumps({"evaluation_id": data["evaluation_id"],
                      "physical_candidate_id": data["physical_candidate_id"],
                      "physical_accepted": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
