"""Actual family compilers preserve function, material mass and dynamic identity."""

from copy import deepcopy
import math

import pytest

from engineering.design_engine.design_alternatives import (
    civil_defaults,
    civil_variables,
    compile_civil,
    compile_vehicle,
    vehicle_defaults,
    vehicle_variables,
)
from engineering.design_engine.manufacturing import compile_register, reconcile


@pytest.mark.parametrize(
    "field,value",
    [
        (key, value)
        for key, spec in civil_variables().items()
        for value in spec["choices"]
    ],
)
def test_existing_civil_families_compile_same_required_function_and_mass(field, value):
    data = compile_civil({field: value})
    study = data["study"]
    assert study["route_length_m"] == 100 and study["track_count"] == 2
    assert all(row["deck"]["span_m"] == 20 for row in study["candidates"])
    assert len(study["candidates"]) == 4
    assert data["civil_candidate"]["definition"]["deck"]["span_m"] == 20
    assert data["quantities"]["spans"] == 5
    assert abs(data["alternatives_review"]["mass_balance_residual_kg"]) < 1e-6
    assert data["alternatives_review"]["complete_installed_kit"] is False
    assert data["correspondence"]["part_count"] > 100
    register = reconcile(compile_register(data), data)
    assert len(register["parts"]) == data["correspondence"]["part_count"]
    assert math.isclose(
        sum(row["defined_mass_kg"] for row in register["parts"]),
        data["correspondence"]["mass_kg"],
        rel_tol=1e-12,
    )
    assert register["unresolved_allocations"]


def test_civil_alternatives_preserve_reference_train_and_support_material_scope():
    reference = compile_civil(civil_defaults())
    alternative = compile_civil(
        dict(
            deck_family="steel-composite-I",
            pier_family="hollow-tapered",
            material="lightweight",
            foundation_family="hollow-driven-six",
        )
    )
    assert reference["study"]["train"] == alternative["study"]["train"]
    assert (
        reference["study"]["support_material"]
        == alternative["study"]["support_material"]
    )
    assert (
        reference["study"]["foundation_material"]
        == alternative["study"]["foundation_material"]
    )
    assert alternative["study"]["material"]["measured"] is False
    assert alternative["quantities"]["prestress_allowance_kg"] == 0
    assert alternative["correspondence"]["complete_installed_kit"] is False


def test_selected_civil_geometry_executes_in_actual_native_elastic_solver():
    from engineering.civil_exploration.model import System

    data = compile_civil(
        dict(
            deck_family="hollow-box",
            pier_family="hollow-tapered",
            material="normal",
            foundation_family="reference-four",
        )
    )
    study = deepcopy(data["study"])
    study["analysis"]["static_positions"] = 3
    result = System(
        data["civil_candidate"], study, study["ground_scenarios"][0], 4
    ).static_envelope()
    assert result["envelope"]["relative_deck_deflection_m"] > 0
    assert math.isfinite(result["envelope"]["foundation_settlement_m"])


@pytest.fixture(scope="module")
def vehicle_reference():
    return compile_vehicle(vehicle_defaults())


def test_vehicle_reference_is_complete_family_and_has_nonempty_corresponding_installed_register(
    vehicle_reference,
):
    data = vehicle_reference
    assert data["model"]["family"] == "metro-6car"
    assert data["model"]["family_definition"]["car_count"] == 6
    register = reconcile(compile_register(data), data)
    assert len(register["parts"]) == len(data["model"]["instances"]) == 414
    assert abs(data["review"]["mass_reallocation_residual_kg"]) < 1e-7
    assert abs(data["review"]["static_reaction_balance_n"]) < 1e-6
    assert data["review"]["minimum_static_contact_n"] > 0
    assert register["complete_installed_kit"] is False


def test_installed_equipment_changes_geometry_mass_and_cg_without_free_residual_compensation(
    vehicle_reference,
):
    alternative = compile_vehicle(
        dict(
            hvac_modules=5,
            carrier_thickness_m=0.005,
            door_carrier_thickness_m=0.010,
            cabinet_thickness_m=0.0025,
        )
    )
    assert (
        alternative["model"]["family_definition"]
        == vehicle_reference["model"]["family_definition"]
    )
    assert (
        alternative["review"]["total_mass_kg"]
        > vehicle_reference["review"]["total_mass_kg"] + 6 * 125
    )
    old_parts = {row["id"]: row for row in vehicle_reference["model"]["instances"]}
    for row in alternative["model"]["instances"]:
        if row["id"].endswith("/body"):
            assert (
                row["properties"]["design"]
                == old_parts[row["id"]]["properties"]["design"]
            )
    assert len(alternative["model"]["instances"]) > len(
        vehicle_reference["model"]["instances"]
    )
    assert (
        alternative["review"]["carbody_dynamics"][0]["cg_m"]
        != vehicle_reference["review"]["carbody_dynamics"][0]["cg_m"]
    )
    assert alternative["review"]["physical_validation"] is False


def test_battery_and_joint_choices_change_actual_pack_and_shared_dynamic_laws(
    vehicle_reference,
):
    alternative = compile_vehicle(
        dict(
            series_modules=24,
            parallel_strings=4,
            joint_option="secondary-minus-20-percent",
        )
    )
    assert alternative["battery"]["module_count"] == 24 * 4
    assert (
        alternative["battery"]["nominal_energy_kwh"]
        < vehicle_reference["battery"]["nominal_energy_kwh"]
    )
    assert (
        alternative["review"]["total_mass_kg"]
        < vehicle_reference["review"]["total_mass_kg"]
    )
    old_joints = {row["id"]: row for row in vehicle_reference["model"]["joints"]}
    for row in alternative["model"]["joints"]:
        if row["connection"] == "secondary":
            assert (
                row["properties"]["design"]["stiffness_n_m"]
                == 0.8 * old_joints[row["id"]]["properties"]["design"]["stiffness_n_m"]
            )
            old_law = vehicle_reference["spatial_configuration"]["joint_laws"][
                row["id"]
            ]
            new_law = alternative["spatial_configuration"]["joint_laws"][row["id"]]
            assert new_law["stiffness_si"][2][2] == 0.8 * old_law["stiffness_si"][2][2]
    from engineering.civil_exploration.variant_compiler import validate_interfaces
    from osr_mech.engineering_definition import fingerprint

    validate_interfaces(alternative["interfaces"], alternative["model"])
    for key in ("interfaces", "coverage", "verification", "joint_register"):
        assert alternative[key]["configuration_sha256"] == fingerprint(
            alternative["model"]
        )


@pytest.mark.parametrize(
    "compile,invalid",
    [
        (compile_civil, {"span_m": 25}),
        (compile_civil, {"route_length_m": 300}),
        (compile_civil, {"deck_family": "invented-winning-section"}),
        (compile_vehicle, {"family": "lm3"}),
        (compile_vehicle, {"hvac_modules": True}),
        (compile_vehicle, {"joint_option": "qualified"}),
        (compile_vehicle, {"mass_factor": 0.1}),
    ],
)
def test_changed_function_ignored_variables_and_unregistered_alternatives_are_rejected(
    compile, invalid
):
    with pytest.raises(ValueError):
        compile(invalid)


def test_variable_maps_are_bounded_existing_family_choices():
    assert len(civil_variables()["deck_family"]["choices"]) == 10
    assert len(civil_variables()["foundation_family"]["choices"]) == 9
    assert vehicle_variables()["family"]["choices"] == ["metro-6car"]


def test_battery_geometry_rejection_is_retained_in_the_wider_search_domain():
    with pytest.raises(ValueError, match="overlaps reference bogie"):
        compile_vehicle(dict(series_modules=32))


@pytest.mark.parametrize("weak_battery", [False, True])
def test_whole_vehicle_service_does_not_inherit_an_hvac_only_pass(
    vehicle_reference, tmp_path, weak_battery
):
    from engineering.design_engine.adapters import checks, screen
    from engineering.design_engine.registry import get

    data = (
        compile_vehicle(dict(series_modules=24, parallel_strings=2))
        if weak_battery
        else deepcopy(vehicle_reference)
    )
    charter = get("vehicle-assembly")
    candidate = dict(definition=data, metrics={}, checks=checks(charter))
    screened = screen(charter, candidate, lambda count, phase: None, tmp_path)
    duty = data["vehicle_battery_reference_duty"]
    assert data["studies"]["hvac_nominal"]["within_declared_study_limit"]
    assert data["studies"]["hvac_one_module_out"]["within_declared_study_limit"]
    if weak_battery:
        assert duty["research_constraints_passed"] is False
        assert any(not row["constraints"]["current"] for row in duty["history"])
        assert screened["checks"]["service"]["state"] == "failed"
    else:
        assert duty["research_constraints_passed"] is True
        assert screened["checks"]["service"]["state"] == "unknown"
    assert screened["checks"]["degraded_service"]["state"] == "unknown"
    assert "complete vehicle" in screened["checks"]["service"]["basis"]
