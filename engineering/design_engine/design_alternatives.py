"""Selectable existing research assemblies with a fixed required function.

These are compiler-backed alternatives, not supplier designs. The civil scope
is always 100 m, five 20 m spans and two tracks under the same reference train.
The vehicle scope is always the complete metro-6car family. Existing synthetic
materials and joint hypotheses stay explicitly unqualified.
"""

from copy import deepcopy
import json
import math
from pathlib import Path

from .contracts import canonical, fingerprint

ROOT = Path(__file__).resolve().parents[2]


def _choice(unit, *values):
    return dict(kind="choice", unit=unit, choices=list(values))


def _options():
    return json.loads(
        (ROOT / "engineering/civil_exploration/config/system-options.json").read_text()
    )


def civil_variables():
    options = _options()
    return dict(
        deck_family=_choice("1", *[r["id"] for r in options["beams"]]),
        pier_family=_choice("1", *[r["id"] for r in options["piers"]]),
        material=_choice("1", *options["materials"]),
        foundation_family=_choice("1", *[r["id"] for r in options["foundations"]]),
    )


def vehicle_variables():
    return dict(
        family=_choice("1", "metro-6car"),
        series_modules=_choice("ea", 24, 28, 32),
        parallel_strings=_choice("ea", 2, 3, 4),
        enclosure_thickness_m=_choice("m", 0.003, 0.004, 0.005),
        hvac_modules=_choice("ea", 3, 4, 5),
        carrier_thickness_m=_choice("m", 0.003, 0.004, 0.005),
        door_carrier_thickness_m=_choice("m", 0.006, 0.008, 0.010),
        cabinet_thickness_m=_choice("m", 0.0015, 0.002, 0.0025),
        joint_option=_choice(
            "1",
            "reference",
            "secondary-minus-20-percent",
            "articulation-stiffness-doubled",
        ),
    )


def _values(values, variables, defaults):
    if not isinstance(values, dict) or set(values) - variables.keys():
        raise ValueError("unknown or changed-function alternative variables")
    result = {**defaults, **deepcopy(values)}
    if set(result) != set(variables):
        raise ValueError("every alternative variable needs an explicit selection")
    for key, spec in variables.items():
        if not any(
            type(result[key]) is type(v) and result[key] == v for v in spec["choices"]
        ):
            raise ValueError("unregistered assembly alternative: " + key)
    return result


def civil_defaults():
    return dict(
        deck_family="pi",
        pier_family="solid",
        material="normal",
        foundation_family="reference-four",
    )


def vehicle_defaults():
    return dict(
        family="metro-6car",
        series_modules=28,
        parallel_strings=4,
        enclosure_thickness_m=0.004,
        hvac_modules=4,
        carrier_thickness_m=0.004,
        door_carrier_thickness_m=0.008,
        cabinet_thickness_m=0.002,
        joint_option="reference",
    )


def _midpoints(row):
    return {
        key: int(round((a + b) / 2)) if key == "rib_count" else (a + b) / 2
        for key, (a, b) in row["bounds"].items()
    }


def _civil_contract(candidate, study):
    from osr_mech.civil.exploration import assembly_parts
    from engineering.design_consistency.contracts import box, part, summary

    materials = {
        "deck-concrete": deepcopy(candidate["material"]),
        "support-concrete": deepcopy(candidate["support_material"]),
        "foundation-concrete": deepcopy(candidate["foundation_material"]),
        **deepcopy(candidate["material_records"]),
    }
    physical = []
    for row in assembly_parts(
        candidate["definition"], candidate["foundation"], study["route_length_m"]
    ):
        material = row["material"]
        if material == "concrete":
            material = (
                "deck-concrete"
                if row["kind"] == "deck"
                else (
                    "foundation-concrete"
                    if row["kind"] in {"foundation", "pile"}
                    else "support-concrete"
                )
            )
        if row["shape"] == "box":
            primitive = box(row["id"], *row["dimensions_m"], row["centre_m"])
        else:
            primitive = dict(
                id=row["id"],
                kind="tube" if row["shape"] == "annulus" else "cylinder",
                centre_m=row["centre_m"],
                radius_m=row["diameter_m"] / 2,
                length_m=row["length_m"],
                axis="z",
            )
            if row["shape"] == "annulus":
                primitive["inner_radius_m"] = row["inner_diameter_m"] / 2
        physical.append(
            part(
                row["id"],
                material,
                dict(
                    role=row["kind"]
                    + " research material region; connected fabrication detailing open",
                    primitives=[primitive],
                ),
                materials,
            )
        )
    contract = dict(
        schema="osr-engineering-representations/1",
        revision="CIVIL-ALTERNATIVE-" + candidate["id"][:12],
        parts=physical,
        materials=materials,
        assembly_joints=[],
        construction_stages=[],
        mandatory_evidence=[
            "reinforcement and tendon detailing",
            "joint and bearing resistance",
            "ground resistance and settlement",
            "independent review",
        ],
        unresolved_part_allocations=[
            "reinforcement/prestress/inserts remain takeoff allowances",
            "bearings and joints remain unresolved hardware allocations",
            "track and fastener installation is a superimposed dead-load allowance",
        ],
        physical_validation=False,
        production_released=False,
    )
    return contract, summary(contract)


def compile_civil(values):
    """Compile a selected existing civil family at one unchanged reference scope."""
    from osr_mech.civil.exploration import geometry
    from engineering.civil_exploration.contracts import validate_study
    from engineering.civil_exploration.workflow import candidate, validate_candidate
    from engineering.civil_exploration.model import takeoff
    from engineering.civil_exploration.systems import validate_options

    selected = _values(values, civil_variables(), civil_defaults())
    options = _options()
    validate_options(options)
    beam = next(row for row in options["beams"] if row["id"] == selected["deck_family"])
    pier = next(row for row in options["piers"] if row["id"] == selected["pier_family"])
    if selected["material"] not in beam["materials"]:
        raise ValueError("material does not apply to the selected deck family")
    definition = dict(
        name="common-fixed-scope-alternative",
        deck=dict(family=beam["id"], span_m=20, parameters=_midpoints(beam)),
        pier=dict(family=pier["id"], height_m=8, parameters=_midpoints(pier)),
    )
    study = json.loads(
        (ROOT / "engineering/civil_exploration/config/reference.json").read_text()
    )
    # The native campaign contract requires at least four distinct controls.
    # Keep the selected design first, then same-span reference geometries under
    # exactly the selected material/foundation/train assumptions.
    campaign_candidates = [definition]
    seen = {fingerprint({key: definition[key] for key in ("deck", "pier")})}
    for control in study["candidates"]:
        control = deepcopy(control)
        control["deck"]["span_m"] = 20
        control["name"] = "fixed20-control-" + control["name"]
        geometry_hash = fingerprint({key: control[key] for key in ("deck", "pier")})
        if geometry_hash not in seen:
            seen.add(geometry_hash)
            campaign_candidates.append(control)
        if len(campaign_candidates) == 4:
            break
    study.update(
        name="Common fixed 100m reference alternative; not a Baghdad qualification",
        candidates=campaign_candidates,
        route_length_m=100,
        track_count=2,
        material=deepcopy(options["materials"][selected["material"]]),
        material_records=deepcopy(options["material_roles"]),
        support_material=deepcopy(options["materials"]["normal"]),
        foundation_material=deepcopy(options["materials"]["normal"]),
        foundation=deepcopy(
            next(
                row["parameters"]
                for row in options["foundations"]
                if row["id"] == selected["foundation_family"]
            )
        ),
        connection_scheme="simple-span",
    )
    if beam["id"] in {"steel-composite-I", "frp-composite-I"}:
        study["mass_allowances"]["prestress_kg_m"] = 0
        study["mass_allowances"][
            "basis"
        ] += " Existing composite-I study has no tendon allocation; connection detailing remains open."
    validate_study(study)
    compiled = candidate(definition, study)
    validate_candidate(compiled)
    quantities = takeoff(compiled, study)
    contract, correspondence = _civil_contract(compiled, study)
    allowance_mass = sum(
        quantities[key]
        for key in (
            "reinforcement_allowance_kg",
            "prestress_allowance_kg",
            "embedded_allowance_kg",
            "superimposed_dead_allowance_kg",
        )
    )
    residual = (
        quantities["installed_study_mass_kg"]
        - correspondence["mass_kg"]
        - allowance_mass
    )
    if not math.isclose(residual, 0, abs_tol=1e-6):
        raise ValueError(
            "civil physical materials and unresolved mass allowances do not reconcile"
        )
    return dict(
        study=study,
        civil_candidate=compiled,
        geometry=geometry(compiled["definition"]),
        contract=contract,
        correspondence=correspondence,
        quantities=quantities,
        selected_alternatives=selected,
        alternatives_review=dict(
            required_function=dict(
                route_length_m=100,
                span_m=20,
                track_count=2,
                reference_train_sha256=fingerprint(study["train"]),
            ),
            material_property_status="existing synthetic research hypotheses; not measured material or resistance",
            defined_material_mass_kg=correspondence["mass_kg"],
            unresolved_allowance_mass_kg=allowance_mass,
            mass_balance_residual_kg=residual,
            complete_installed_cg_m=None,
            complete_installed_inertia_kg_m2=None,
            installed_mass_distribution_state="unknown: material solids reconcile; allowance placement and final hardware remain open",
            complete_installed_kit=False,
            physical_validation=False,
        ),
    )


def confirm_civil(definition, output):
    """Execute the selected study through its actual native, bounded campaign."""
    from engineering.civil_exploration.workflow import run_campaign
    from .store import write_new

    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    config = output / "selected-study.json"
    write_new(config, definition["study"])
    manifest = run_campaign(config, output / "native-campaign")
    comparison = json.loads((output / "native-campaign/comparison.json").read_text())
    return dict(
        manifest=manifest,
        comparison=comparison,
        candidate_id=definition["civil_candidate"]["id"],
        study_sha256=fingerprint(definition["study"]),
        physical_validation=False,
    )


def compile_vehicle(values):
    """Compile real geometry, mass and ports for complete six-car alternatives."""
    from osr_mech.engineering_definition import (
        model_mass_properties,
        validate,
        verification_register,
        fingerprint as model_fingerprint,
    )
    from osr_mech.joint_design import definitions
    from engineering.civil_exploration.variant_compiler import (
        CHOICES_PATH,
        validate_interfaces,
    )
    from engineering.civil_exploration.spatial_demo import configuration
    from engineering.civil_exploration.spatial_vehicle import SpatialVehicle
    from engineering.civil_exploration.shared_demo import variants
    from engineering.twin_design.compiler import compile_design, DATA

    selected = _values(values, vehicle_variables(), vehicle_defaults())
    choices = json.loads(CHOICES_PATH.read_text())
    choices["family"] = selected["family"]
    choices["battery"].update(
        {
            key: selected[key]
            for key in ("series_modules", "parallel_strings", "enclosure_thickness_m")
        }
    )
    baseline_inputs = json.loads((DATA / "design-inputs.json").read_text())
    baseline = compile_design(baseline_inputs, variant_choices=choices)
    inputs = deepcopy(baseline_inputs)
    inputs["hvac"].update(
        module_count_per_car=selected["hvac_modules"],
        carrier_thickness_m=selected["carrier_thickness_m"],
    )
    inputs["doors"]["carrier_thickness_m"] = selected["door_carrier_thickness_m"]
    inputs["electrical"]["cabinet_thickness_m"] = selected["cabinet_thickness_m"]
    result = compile_design(
        inputs, variant_choices=choices, experimental_hvac_topology=True
    )
    baseline_parts = {row["id"]: row for row in baseline["model"]["instances"]}
    residual_changes = []
    for row in result["model"]["instances"]:
        if row["id"].endswith("/body"):
            row["properties"]["design"] = deepcopy(
                baseline_parts[row["id"]]["properties"]["design"]
            )
            residual_changes.append(
                dict(
                    physical_id=row["id"],
                    remaining_mass_kg=row["properties"]["design"]["mass_kg"],
                )
            )
    model = result["model"]
    if selected["joint_option"] != "reference":
        model = variants(model)[selected["joint_option"]]
    model["revision"] = "COMMON-VEHICLE-" + fingerprint(selected)[:12]
    for row in [*model["instances"], *model["joints"]]:
        row["revision"] = model["revision"]
    validate(model)
    result["model"] = model
    result["spatial_configuration"] = configuration(model)
    vehicle = SpatialVehicle(model, result["spatial_configuration"]["joint_laws"])
    baseline_vehicle = SpatialVehicle(
        baseline["model"], baseline["spatial_configuration"]["joint_laws"]
    )
    result["mass_properties"] = model_mass_properties(model)
    result["joint_register"] = definitions(model)
    for key in ("interfaces", "coverage", "joint_register"):
        result[key]["configuration_sha256"] = model_fingerprint(model)
    validate_interfaces(result["interfaces"], model)
    result["verification"] = verification_register(
        model, implementation_hashes=result["review"]["source_sha256"]
    )
    balance = vehicle.total_mass - sum(
        group["mass"] for group in vehicle.groups.values()
    )
    if not math.isclose(balance, 0, abs_tol=1e-7):
        raise ValueError("vehicle installed masses and dynamic groups disagree")
    result["review"].update(
        configuration_sha256=model_fingerprint(model),
        total_train_mass_kg=vehicle.total_mass,
        total_mass_kg=vehicle.total_mass,
        mass_reallocation_residual_kg=balance,
        static_reaction_balance_n=sum(row["static_n"] for row in vehicle.contacts)
        - vehicle.total_mass * 9.81,
        minimum_static_contact_n=min(row["static_n"] for row in vehicle.contacts),
        residual_budget=residual_changes,
        baseline_remaining_residuals_frozen=True,
        additional_study_train_mass_kg=vehicle.total_mass - baseline_vehicle.total_mass,
        carbody_dynamics=[
            dict(
                id=group["id"],
                mass_kg=group["mass"],
                cg_m=group["cg"].tolist(),
                inertia_kg_m2=group["inertia"].tolist(),
            )
            for group in vehicle.groups.values()
            if group["kind"] == "carbody"
        ],
    )
    result["selected_alternatives"] = selected
    result["alternatives_review"] = dict(
        required_function=dict(
            family=model["family"],
            car_count=model["family_definition"]["car_count"],
            family_definition_sha256=fingerprint(model["family_definition"]),
        ),
        joint_property_status="existing synthetic joint hypotheses; supplier/calibration/capacity remain unknown",
        remaining_body_and_frame_properties="synthetic residual allocations; no geometry-derived structural stiffness claim",
        physical_validation=False,
        production_released=False,
    )
    from .electrical_installation import installation_report

    result["installation"] = installation_report(result, kind="twin")
    canonical(result)
    return result
