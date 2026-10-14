"""Coherent subsystem alternatives without stealing mass from residual budgets."""

from copy import deepcopy
import json
from osr_mech.engineering_definition import (
    model_mass_properties,
    fingerprint,
    validate,
    verification_register,
)
from engineering.twin_design.compiler import compile_design, DATA
from engineering.civil_exploration.spatial_vehicle import SpatialVehicle


def hvac(values):
    baseline_inputs = json.loads((DATA / "design-inputs.json").read_text())
    baseline = compile_design(baseline_inputs)
    inputs = deepcopy(baseline_inputs)
    inputs["hvac"]["module_count_per_car"] = values["hvac_modules"]
    inputs["hvac"]["carrier_thickness_m"] = values["carrier_thickness_m"]
    result = compile_design(inputs, experimental_hvac_topology=True)
    old = {p["id"]: p for p in baseline["model"]["instances"]}
    changes = []
    for part in result["model"]["instances"]:
        if part["id"].endswith("/body"):
            prior = part["properties"]["design"]["mass_kg"]
            part["properties"]["design"] = deepcopy(
                old[part["id"]]["properties"]["design"]
            )
            changes.append(
                dict(
                    instance=part["id"],
                    baseline_remaining_residual_kg=part["properties"]["design"][
                        "mass_kg"
                    ],
                    discarded_compensating_residual_kg=prior,
                    basis="same fixed baseline residual retained; support/module changes cannot be free",
                )
            )
    model = result["model"]
    validate(model)
    result["mass_properties"] = model_mass_properties(model)
    vehicle = SpatialVehicle(model, result["spatial_configuration"]["joint_laws"])
    baseline_vehicle = SpatialVehicle(
        baseline["model"], baseline["spatial_configuration"]["joint_laws"]
    )
    result["review"].update(
        configuration_sha256=fingerprint(model),
        total_train_mass_kg=vehicle.total_mass,
        baseline_remaining_residuals_frozen=True,
        residual_free_hardware_prevented=True,
        residual_changes=changes,
        additional_study_train_mass_kg=vehicle.total_mass
        - baseline["review"]["total_train_mass_kg"],
        mass_reallocation_residual_kg=vehicle.total_mass
        - sum(g["mass"] for g in vehicle.groups.values()),
        static_reaction_balance_n=sum(r["static_n"] for r in vehicle.contacts)
        - vehicle.total_mass * 9.81,
        minimum_static_contact_n=min(r["static_n"] for r in vehicle.contacts),
        carbody_dynamics=[
            dict(
                id=g["id"],
                mass_kg=g["mass"],
                cg_m=g["cg"].tolist(),
                inertia_kg_m2=g["inertia"].tolist(),
                cg_change_m=(g["cg"] - baseline_vehicle.groups[g["id"]]["cg"]).tolist(),
            )
            for g in vehicle.groups.values()
            if g["kind"] == "carbody"
        ],
        residual_budget=[
            dict(
                car=r["instance"].split("/")[0],
                remaining_residual_kg=r["baseline_remaining_residual_kg"],
                basis=r["basis"],
            )
            for r in changes
        ],
    )
    result["verification"] = verification_register(
        model, implementation_hashes=result["review"]["source_sha256"]
    )
    # Every representation and inspection package is rebound to the one physical
    # candidate, rather than keeping pre-overlay source identities.
    for name in ("interfaces", "coverage", "joint_register", "verification"):
        if "configuration_sha256" in result[name]:
            result[name]["configuration_sha256"] = fingerprint(model)
    from .electrical_installation import installation_report

    result["installation"] = installation_report(result, kind="twin")
    return result
