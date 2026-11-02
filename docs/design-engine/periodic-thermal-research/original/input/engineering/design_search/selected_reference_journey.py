"""Selection-bound adapter for a conditional P1 journey on the v0.6 vehicle.

The selected vehicle remains the physical candidate. Route and assumed LIM
inputs are a separate evaluation context; this adapter never rewrites the
vehicle identity to make it look like one of the grammar-generated bodies.
"""
from copy import deepcopy
from pathlib import Path

from engineering.development_baseline import selection
from engineering.station_rail import ROOT, braking
from engineering.station_rail.common import digest, identity
from . import railway_architecture

PRODUCER = "engineering/design_search/selected_reference_journey.py"
SCHEMA = "osr-coupled-railway-bundle/1"
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             configuration_adopted=False, manufacturing_release=False,
             operating_release=False, physical_journey_completed=False)


def _case(root, vehicle_value):
    spec = railway_architecture.load_spec(root)
    case = railway_architecture._configuration(
        "P1", 6, 2000.0, 20.0, {"launch_m": 500.0}, spec, vehicle_value)
    requirements = case["requirements"]
    formation = case["physical_definition"]["formation"]
    route = case["physical_definition"]["route"]
    if (formation["cars"] != 6 or formation["car_length_m"] != 17.0
            or formation["seats_per_car"] != 44
            or formation["wheelchair_places_per_car"] != 2
            or route["station_spacing_m"] != 2000.0
            or requirements["speed_cap_m_s"] != 20.0
            or requirements["acceleration_m_s2"] != 0.4
            or requirements["target_headway_s"] != 120.0
            or case["reference_candidate_id"] != vehicle_value["candidate_id"]):
        raise ValueError("Selected-reference P1 evaluation differs from the current v0.6 service")
    return spec, case


def build(root=ROOT):
    root = Path(root).resolve()
    selected = selection.load(root)
    vehicle_value = selected["vehicle"]
    spec, case = _case(root, vehicle_value)
    rotor = braking.rotating_stock(vehicle_value)
    brake_vehicle = deepcopy(vehicle_value)
    brake_vehicle["candidate_id"] = case["candidate_id"]
    brake = braking.definition(brake_vehicle)
    source_sha256 = {
        **selected["source_sha256"],
        **vehicle_value["source_sha256"],
        railway_architecture.PRODUCER: digest(root / railway_architecture.PRODUCER),
        "engineering/station_rail/braking.py": digest(root / "engineering/station_rail/braking.py"),
        "engineering/development_baseline/selection.py": digest(root / "engineering/development_baseline/selection.py"),
        PRODUCER: digest(root / PRODUCER),
    }
    value = dict(
        schema=SCHEMA,
        bundle_kind="selected-development-reference",
        candidate_id=case["candidate_id"],
        bundle_id=case["candidate_id"],
        reference_candidate_id=vehicle_value["candidate_id"],
        body_candidate_id=vehicle_value["body_candidate_id"],
        support_component_id=vehicle_value["support_component_id"],
        propulsion_component_id=vehicle_value["propulsion_component_id"],
        selection_id=selected["selection_id"],
        vehicle_evaluation_id=vehicle_value["evaluation_id"],
        vehicle_physical_definition_id=identity(vehicle_value["physical_definition"]),
        family_id="P1",
        cars=case["physical_definition"]["formation"]["cars"],
        architecture_case=case,
        architecture_specification=spec,
        architecture_evaluation_candidate_id=case["candidate_id"],
        motor_definition=dict(
            schema="osr-selected-passive-secondary-reference/1",
            motor_component_id=vehicle_value["propulsion_component_id"],
            physical_definition=deepcopy(vehicle_value["physical_definition"]["propulsion"]),
            available_force_map_id=None,
        ),
        brake_definition=brake,
        mass={key: vehicle_value["mass"][key] for key in (
            "accounted_tare_kg_per_car", "accounted_cap_loaded_kg_per_car",
            "accounted_160_control_kg_per_car")},
        mass_scope="Selected vehicle accounting; complete installed mass remains unknown",
        rotating_equivalent_kg_per_car=rotor["equivalent_inertial_mass_kg_per_car"],
        rotor_definition_id=identity(rotor),
        physical_definition=deepcopy(case["physical_definition"]),
        reference_vehicle_physical_definition=deepcopy(vehicle_value["physical_definition"]),
        retained_equipment_accounts=[],
        component_substitutions=[],
        unweighed_architecture_equipment=["Wayside LIM primary, power electronics, wiring, cooling, protection and installation are assumption-only or unlocated"],
        known_body_stock_kg=None,
        normal_sprung_mass_hypothesis_kg=None,
        crowd_sprung_mass_hypothesis_kg=None,
        requirement_revision=case["requirement_revision"],
        source_sha256=source_sha256,
        complete_installed_mass_kg=None,
        complete_installed_CG_m=None,
        complete_installed_inertia_kg_m2=None,
        **FLAGS,
    )
    value["definition_id"] = identity(value)
    return validate(value, root)


def validate(bundle, root=ROOT):
    root = Path(root).resolve()
    if bundle.get("schema") != SCHEMA or bundle.get("bundle_kind") != "selected-development-reference":
        raise ValueError("Selected-reference conditional bundle schema differs")
    if bundle.get("definition_id") != identity(
            {key: value for key, value in bundle.items() if key != "definition_id"}):
        raise ValueError("Selected-reference bundle definition identity differs")
    selected = selection.load(root)
    vehicle_value = selected["vehicle"]
    spec, case = _case(root, vehicle_value)
    rotor = braking.rotating_stock(vehicle_value)
    expected_source = {
        **selected["source_sha256"],
        **vehicle_value["source_sha256"],
        railway_architecture.PRODUCER: digest(root / railway_architecture.PRODUCER),
        "engineering/station_rail/braking.py": digest(root / "engineering/station_rail/braking.py"),
        "engineering/development_baseline/selection.py": digest(root / "engineering/development_baseline/selection.py"),
        PRODUCER: digest(root / PRODUCER),
    }
    expected = {
        "candidate_id": case["candidate_id"],
        "bundle_id": case["candidate_id"],
        "reference_candidate_id": vehicle_value["candidate_id"],
        "body_candidate_id": vehicle_value["body_candidate_id"],
        "support_component_id": vehicle_value["support_component_id"],
        "propulsion_component_id": vehicle_value["propulsion_component_id"],
        "selection_id": selected["selection_id"],
        "vehicle_evaluation_id": vehicle_value["evaluation_id"],
        "vehicle_physical_definition_id": identity(vehicle_value["physical_definition"]),
        "architecture_case": case,
        "architecture_specification": spec,
        "architecture_evaluation_candidate_id": case["candidate_id"],
        "motor_definition": dict(
            schema="osr-selected-passive-secondary-reference/1",
            motor_component_id=vehicle_value["propulsion_component_id"],
            physical_definition=vehicle_value["physical_definition"]["propulsion"],
            available_force_map_id=None,
        ),
        "brake_definition": braking.definition(dict(vehicle_value, candidate_id=case["candidate_id"])),
        "mass": {key: vehicle_value["mass"][key] for key in (
            "accounted_tare_kg_per_car", "accounted_cap_loaded_kg_per_car",
            "accounted_160_control_kg_per_car")},
        "rotating_equivalent_kg_per_car": rotor["equivalent_inertial_mass_kg_per_car"],
        "rotor_definition_id": identity(rotor),
        "physical_definition": case["physical_definition"],
        "reference_vehicle_physical_definition": vehicle_value["physical_definition"],
        "requirement_revision": case["requirement_revision"],
        "source_sha256": expected_source,
        "mass_scope": "Selected vehicle accounting; complete installed mass remains unknown",
        "retained_equipment_accounts": [],
        "component_substitutions": [],
        "unweighed_architecture_equipment": ["Wayside LIM primary, power electronics, wiring, cooling, protection and installation are assumption-only or unlocated"],
        "known_body_stock_kg": None,
        "normal_sprung_mass_hypothesis_kg": None,
        "crowd_sprung_mass_hypothesis_kg": None,
    }
    for key, expected_value in expected.items():
        if bundle.get(key) != expected_value:
            raise ValueError("Selected-reference bundle differs from current selection: " + key)
    if (bundle.get("family_id") != "P1" or bundle.get("cars") != 6
            or bundle.get("candidate_id") != case["candidate_id"]
            or any(bundle.get(key) is not False for key in FLAGS)
            or any(bundle.get(key) is not None for key in (
                "complete_installed_mass_kg", "complete_installed_CG_m",
                "complete_installed_inertia_kg_m2"))):
        raise ValueError("Selected-reference adapter cannot grant completeness or release")
    return bundle
