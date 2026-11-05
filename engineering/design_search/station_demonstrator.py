"""Selected-reference station demand and unexecuted evidence handoff.

This adapter reads the selected vehicle's actual schema. It does not project it
onto a generated body's identity or import a synthetic map as available thrust.
Builds are compact planning records; they neither run a campaign nor admit a
physical article to the qualification workflow.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import stat

from engineering import development_baseline, station_rail
from engineering.development_baseline import selection
from engineering.station_rail import ROOT, braking, civil, common, electrical, operations, vehicle
from engineering.station_rail.common import brief, digest, encoded, identity, source_map
from . import capabilities, conditional_journey_study, railway_architecture, requirement_policy
from . import selected_reference_journey, test_readiness

PRODUCER = "engineering/design_search/station_demonstrator.py"
OUTPUT = "build/station-demonstrator"
MAX_RESULT_BYTES = 2 * 1024**2  # Reader resource limit, not an engineering limit.
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             configuration_adopted=False, manufacturing_release=False,
             operating_release=False, physical_journey_completed=False,
             installed_mass_complete=False, native_dispatch_allowed=False)
LINKS = {
    "T05": ("functional.integrated_service", "physical.temperature"),
    "T07": ("safety.independent_stop",),
    "T08": ("functional.integrated_service", "accessibility.boarding_egress"),
}
NEXT = {
    "T05": [
        "Bind installed primary/secondary geometry and transforms before transferring any component result",
        "Obtain thrust/loss versus speed, position, gap, current and temperature within the electromagnetic model domain",
        "Close repeated-duty current, voltage, cooling and thermal limits with authenticated correlation",
    ],
    "T07": [
        "Size independent brake hardware and establish adhesion, latency, degraded channels, stopping and holding envelopes",
        "Verify power-loss stopping, rollback protection and recovery without crediting synthetic LIM thrust",
    ],
    "T08": [
        "Resolve full-train section handoff, phase branches, localisation uncertainty, berth and tail clearance",
        "Check controller-speed-limit failures before further conditional journey refinement",
        "Establish protected station occupation and repeated service under adverse conditions before claiming headway",
    ],
}
MODULES = (
    (development_baseline, "engineering/development_baseline/__init__.py"),
    (selection, "engineering/development_baseline/selection.py"),
    (station_rail, "engineering/station_rail/__init__.py"),
    (braking, "engineering/station_rail/braking.py"),
    (civil, "engineering/station_rail/civil.py"),
    (common, "engineering/station_rail/common.py"),
    (electrical, "engineering/station_rail/electrical.py"),
    (operations, "engineering/station_rail/operations.py"),
    (vehicle, "engineering/station_rail/vehicle.py"),
    (capabilities, "engineering/design_search/capabilities.py"),
    (railway_architecture, railway_architecture.PRODUCER),
    (test_readiness, test_readiness.PRODUCER),
    (requirement_policy, requirement_policy.PRODUCER),
    (conditional_journey_study, conditional_journey_study.PRODUCER),
    (selected_reference_journey, selected_reference_journey.PRODUCER),
)
LOADED_SOURCE_SHA256 = {name: digest(module.__file__) for module, name in MODULES}
LOADED_SOURCE_SHA256[PRODUCER] = digest(__file__)


def _executing_sources(root):
    """Reject a different source tree or source edits after this process loaded."""
    for module, name in MODULES:
        expected = LOADED_SOURCE_SHA256[name]
        if digest(module.__file__) != expected or digest(root / name) != expected:
            raise ValueError("Executing station dependency differs from source root: " + name)
    if digest(__file__) != LOADED_SOURCE_SHA256[PRODUCER] or digest(root / PRODUCER) != LOADED_SOURCE_SHA256[PRODUCER]:
        raise ValueError("Executing station demonstrator differs from source root")
    return dict(LOADED_SOURCE_SHA256)


def build(bundle=None, *, root=ROOT):
    """Bind the selected reference to demand, geometry and T05/T07/T08 requests."""
    root = Path(root).resolve()
    executing_sources = _executing_sources(root)
    if bundle is None:raise ValueError('Explicit candidate-specific station bundle required; no installed propulsion is selected')
    selected_reference_journey.validate(bundle, root)
    config = brief(root)
    case = bundle["architecture_case"]
    formation = case["physical_definition"]["formation"]
    route = case["physical_definition"]["route"]
    requirements = case["requirements"]
    propulsion = bundle["motor_definition"]["physical_definition"]
    if (propulsion["family"] != "wayside-double-sided-linear-induction"
            or propulsion["all_powered_traction_equipment_wayside"] is not True):
        raise ValueError("Selected wheel/station-LIM protocol scope differs")

    service = config["service"]
    demand = operations.profile(
        route["station_spacing_m"], bundle["mass"]["accounted_cap_loaded_kg_per_car"],
        speed_cap_m_s=requirements["speed_cap_m_s"],
        acceleration_m_s2=requirements["acceleration_m_s2"],
        service_deceleration_m_s2=service["service_deceleration_m_s2"],
        rolling_coefficient=service["rolling_coefficient_hypothesis"],
        bearing_drag_N_per_car=service["bearing_drag_N_per_car_hypothesis"],
        quadratic_drag_N_per_car_per_m_s_squared=service["quadratic_drag_N_per_car_per_m_s_squared_hypothesis"],
        grade_fraction=service["mainline_grade_fraction_hypothesis"],
        cars=formation["cars"], loading="normal",
        rotating_equivalent_mass_kg_per_car=bundle["rotating_equivalent_kg_per_car"])
    zones = [operations.station_zone(
        demand, length, train_length_m=formation["train_length_m"],
        car_length_m=formation["car_length_m"], secondary_length_m=propulsion["secondary_length_m"],
        dwell_s=service["dwell_s"], headway_s=requirements["target_headway_s"],
        section_length_m=service["station_section_length_m"],
        independent_train_phase_branches=service["minimum_independent_train_phase_branches_per_direction"])
        for length in service["retired_station_winding_library_m"]]
    survivors = [z for z in zones if z["nominal_resource_screen"] == "pass"]
    reference_zone = min(survivors, key=lambda z: z["length_m"]) if survivors else None
    binding = dict(
        vehicle_candidate_id=bundle["reference_candidate_id"],
        vehicle_evaluation_id=bundle["vehicle_evaluation_id"],
        selection_id=bundle["selection_id"],
        journey_adapter_id=bundle["candidate_id"],
        bundle_definition_id=bundle["definition_id"],
        body_candidate_id=bundle["body_candidate_id"],
        support_component_id=bundle["support_component_id"],
        propulsion_component_id=bundle["propulsion_component_id"],
        brake_definition_id=bundle["brake_definition"]["brake_definition_id"],
        requirement_revision=bundle["requirement_revision"])
    policy = requirement_policy.catalogue()
    definitions = test_readiness.definitions(root)
    protocols = []
    for template in definitions["protocols"]:
        if template["id"] not in LINKS:
            continue
        row = deepcopy(template)
        row["subject_binding"] = deepcopy(binding)
        if row["id"] == "T05":
            row["subject_binding"].update(
                passive_secondary_component_id=bundle["propulsion_component_id"],
                wayside_primary_candidate_id=None,
                complete_primary_secondary_article_defined=False)
        row["requirement_policy_links"] = [dict(id=k, category=policy["criteria"][k]["category"])
                                           for k in LINKS[row["id"]]]
        row["article_binding"] = dict(as_built_candidate_id=None, article_configuration_sha256=None,
                                     as_built_revision_required=True,
                                     numerical_parent_is_not_an_as_built_record=True)
        row["planning_context"] = dict(
            cars=formation["cars"], car_length_m=formation["car_length_m"],
            station_spacing_m=route["station_spacing_m"],
            normal_people_per_car=formation["seats_per_car"] + formation["wheelchair_places_per_car"],
            headway_target_s=requirements["target_headway_s"],
            speed_cap_target_m_s=requirements["speed_cap_m_s"],
            complete_installed_mass_kg=None, approved_operating_limits=False)
        if row["id"] == "T05":
            row["coordinate_definition"] = dict(
                position="Secondary longitudinal start relative to fixed primary, not route leading-nose position",
                forces="Primary-fixed longitudinal/transverse/vertical axes",
                conversion_to_train_route="Requires actual installed secondary transforms, car offsets and wayside section locations")
        elif row["id"] == "T08":
            row["coordinate_definition"] = dict(
                position="Train leading-nose route chainage; authenticated localisation/datum and uncertainty required")
        row["next_requests"] = NEXT[row["id"]].copy()
        row["native_dispatch_allowed"] = False
        row["evidence_request_id"] = identity(row)
        protocols.append(row)

    assumptions = conditional_journey_study.specification(root)
    sources = dict(bundle["source_sha256"])
    sources.update(source_map(root, (
        PRODUCER, operations.__name__.replace(".", "/") + ".py",
        civil.PRODUCER, railway_architecture.SPEC,
        capabilities.__name__.replace(".", "/") + ".py",
        test_readiness.PRODUCER, test_readiness.DEFINITIONS, requirement_policy.PRODUCER,
        conditional_journey_study.PRODUCER, conditional_journey_study.CONFIG)))
    sources.update(executing_sources)
    _executing_sources(root)

    value = dict(
        schema="osr-selected-station-demonstrator/1", subject_binding=binding,
        purpose="next-experiment planning; no integrated selection or physical release",
        analytical_demand=demand, reference_shared_winding=reference_zone,
        reference_winding_scope="Kinematic shared-winding hypothesis; no installed primary candidate or equivalence to the journey adapter established",
        winding_library_screens=zones,
        conditional_journey_context=dict(
            assumption_id=assumptions["assumption_id"],
            commanded_leading_point_windows_m=deepcopy(case["commanded_power_windows_m"]),
            adapter_installed_track_intervals_m=deepcopy(case["physical_definition"]["wayside"]["installed_linear_track_intervals_per_leg_m"]),
            coordinate_scope="Commanded leading-point windows are not full-train installed winding geometry",
            reference_geometry_equivalence_established=False,
            available_motor_map_id=None, journey_results_imported=False,
            simulation_execution="not-run-by-this-handoff",
            synthetic_results_are_not_available_thrust=True),
        service_targets=dict(headway_s=requirements["target_headway_s"],
            normal_people_per_train=formation["cars"] * (formation["seats_per_car"] + formation["wheelchair_places_per_car"]),
            normal_passengers_per_hour_per_direction_arithmetic=formation["cars"] * (formation["seats_per_car"] + formation["wheelchair_places_per_car"]) * 3600 / requirements["target_headway_s"],
            protected_headway_demonstrated=False),
        complete_installed_mass_kg=None, accepted_available_force_map_id=None,
        integrated_selection=None, executed_physical_tests=0,
        requirement_policy_id=policy["policy_id"], protocols=protocols,
        scope="Three station protocols only; the complete vehicle test programme and external qualification workflow remain required",
        unresolved=[
            "Installed vehicle, primary, supply, cooling and protection geometry/mass remain incomplete",
            "Analytical required force is not available thrust; no component result is transferred here",
            "Kinematic winding/resource screens do not establish electrical duty, safe headway or physical feasibility",
            "Assumed brake/thermal/force maps require separate engineering models, measurements and independent review",
        ], source_sha256=sources, **FLAGS)
    value["evaluation_id"] = identity(value)
    return value


def write(output=None, *, root=ROOT):
    """Write a fresh immutable planning record; refuse an existing destination."""
    root = Path(root).resolve()
    value = build(root=root)
    target = Path(output) if output is not None else root / OUTPUT
    target.mkdir(parents=True, exist_ok=False)
    (target / "result.json").write_bytes(encoded(value))
    return dict(output=str(target), evaluation_id=value["evaluation_id"], **FLAGS)


def verify(output=None, *, root=ROOT):
    root = Path(root).resolve()
    target = Path(output) if output is not None else root / OUTPUT
    if target.is_symlink() or not target.is_dir():
        raise ValueError("Regular station handoff directory required")
    path = target / "result.json"
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except OSError as exc:
        raise ValueError("Regular non-symlink station handoff file required") from exc
    with os.fdopen(descriptor, "rb") as handle:
        metadata = os.fstat(handle.fileno())
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError("Regular non-symlink station handoff file required")
        if metadata.st_size > MAX_RESULT_BYTES:
            raise ValueError("Station handoff exceeds reader size budget")
        raw = handle.read(MAX_RESULT_BYTES + 1)
        if len(raw) > MAX_RESULT_BYTES:
            raise ValueError("Station handoff exceeds reader size budget")
    # Exact regeneration catches resealed edits as well as stale dependencies.
    if raw != encoded(build(root=root)):
        raise ValueError("Station handoff differs from the selected reference, sources or unexecuted evidence")
    return dict(verified=True, **FLAGS)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "verify"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    print(json.dumps((write if args.action == "build" else verify)(args.output), sort_keys=True))


if __name__ == "__main__":
    main()
