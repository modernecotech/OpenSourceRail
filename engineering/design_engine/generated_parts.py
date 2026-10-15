"""Two bounded, subtractive solid families for native part-design research.

The fixture and load are fixed functions. Clearance holes are geometry, not a
verified bolt connection. Steel properties and displacement limits are explicit
research assumptions; no strength, fatigue or physical acceptance is implied.
"""

from __future__ import annotations

from copy import deepcopy
import math

import numpy as np

from .contracts import fingerprint

FAMILIES = ("mechanical-cleat", "civil-steel-beam")
MATERIAL = dict(
    density_kg_m3=7850.0,
    young_pa=210e9,
    poisson_ratio=0.3,
    basis="Nominal isotropic research steel; no batch or supplier qualification",
    yield_strength_pa=None,
    fatigue_resistance=None,
)
CHECKS = (
    "geometry",
    "mass_inertia",
    "manufacturing",
    "linear_service",
    "load_equilibrium",
    "mesh_refinement",
    "independent_benchmark",
    "physical_correlation",
    "independent_acceptance",
)


def variables(family):
    if family == "mechanical-cleat":
        return dict(
            thickness_m=dict(kind="choice", unit="m", choices=[0.010, 0.012, 0.016]),
            topology=dict(
                kind="choice", unit="1", choices=["solid-web", "lightened-web"]
            ),
        )
    if family == "civil-steel-beam":
        return dict(
            wall_m=dict(kind="choice", unit="m", choices=[0.004, 0.006, 0.008]),
            topology=dict(kind="choice", unit="1", choices=["rhs", "i-section"]),
        )
    raise ValueError("unregistered generated-part family")


def defaults(family):
    variables(family)
    return (
        dict(thickness_m=0.012, topology="solid-web")
        if family == "mechanical-cleat"
        else dict(wall_m=0.006, topology="rhs")
    )


def _properties(components, density):
    """Signed exact primitive integrals, translated to the occupied-solid CG."""
    volumes, centres, inertias = [], [], []
    for component in components:
        sign = 1 if component["operation"] == "add" else -1
        centre = np.asarray(component["centre_m"], dtype=float)
        if component["shape"] == "box":
            x, y, z = component["dimensions_m"]
            volume = x * y * z
            inertia = (
                np.diag([y * y + z * z, x * x + z * z, x * x + y * y]) * volume / 12
            )
        elif component["shape"] == "cylinder-z":
            radius, length = component["radius_m"], component["length_m"]
            volume = math.pi * radius**2 * length
            inertia = (
                np.diag([(3 * radius**2 + length**2) / 12] * 2 + [radius**2 / 2])
                * volume
            )
        else:
            raise ValueError("unsupported controlled solid primitive")
        volumes.append(sign * volume)
        centres.append(centre)
        inertias.append(sign * inertia)
    volume = math.fsum(volumes)
    if volume <= 0:
        raise ValueError("nonpositive occupied material volume")
    cg = sum((v * c for v, c in zip(volumes, centres)), np.zeros(3)) / volume
    inertia = np.zeros((3, 3))
    for v, c, own in zip(volumes, centres, inertias):
        delta = c - cg
        inertia += own + v * ((delta @ delta) * np.eye(3) - np.outer(delta, delta))
    if np.linalg.eigvalsh(inertia).min() <= 0:
        raise ValueError("nonpositive physical inertia")
    return dict(
        volume_m3=volume,
        mass_kg=volume * density,
        cg_m=cg.tolist(),
        inertia_tensor_kg_m2=(inertia * density).tolist(),
    )


def _box(dimensions, centre, operation="subtract"):
    return dict(
        shape="box",
        operation=operation,
        dimensions_m=list(dimensions),
        centre_m=list(centre),
    )


def _model(family, selected, length, width, height, components, force, limit, section):
    material = deepcopy(MATERIAL)
    geometry = dict(
        units="m", components=components, envelope_m=[length, width, height]
    )
    properties = _properties(components, material["density_kg_m3"])
    identity = "cleat" if family == "mechanical-cleat" else "civil-beam"
    part = dict(
        id=identity,
        quantity=1,
        material="research-steel",
        geometry=geometry,
        geometry_sha256=fingerprint(geometry),
        properties=properties,
        placement=dict(translation_m=[0.0, 0.0, 0.0], rotation=np.eye(3).tolist()),
        revision="RESEARCH-1",
        production_released=False,
        inspection_characteristics=[
            "envelope",
            "wall or plate thickness",
            "cut positions and diameters",
        ],
        manufacturing_limits=dict(
            minimum_wall_m=0.004,
            minimum_ligament_m=0.004,
            minimum_cut_radius_m=0.003,
            tolerance_m=None,
        ),
    )
    result = dict(
        schema="osr-generated-solid-definition/1",
        family=family,
        variables=deepcopy(selected),
        parts=[part],
        materials={"research-steel": material},
        section=section,
        supports=[
            dict(
                id="root",
                kind="ideal-full-face-clamp",
                plane_axis="x",
                coordinate_m=0.0,
                constrained_dofs=[1, 2, 3],
            )
        ],
        loads=[
            dict(
                id="service",
                kind="uniform-end-face-traction",
                plane_axis="x",
                coordinate_m=length,
                force_n=[0.0, 0.0, -force],
            )
        ],
        displacement_limit_m=limit,
        limit_basis="Provisional research assumption, fixed before native runs; no accepted serviceability criterion",
        manufacturing_rules=dict(
            minimum_wall_m=0.004,
            minimum_ligament_m=0.004,
            tool_radius_m=0.003,
            welding_and_bolt_contact="unknown",
        ),
        mandatory_checks=list(CHECKS),
        unresolved=[
            "yield and nonlinear response",
            "fatigue",
            "bolt/contact or bearing connection",
            "corrosion and tolerances",
            "material batch",
            "physical correlation",
            "independent acceptance",
        ],
        unresolved_part_allocations=[
            "fixture/support hardware",
            "bolts and contact interfaces",
        ],
        physical_validation=False,
        production_released=False,
    )
    result["physical_definition_sha256"] = fingerprint(result)
    return result


def compile_definition(family, values=None):
    """Return a raw immutable-by-digest one-part model, suitable for a model wrapper."""
    specs = variables(family)
    if values is not None and (
        not isinstance(values, dict) or set(values) - set(specs)
    ):
        raise ValueError("unknown generated-part variable or changed function")
    selected = {**defaults(family), **(values or {})}
    for key, spec in specs.items():
        if not any(
            type(selected[key]) is type(v) and selected[key] == v
            for v in spec["choices"]
        ):
            raise ValueError("generated-part selection outside finite domain: " + key)
    if family == "mechanical-cleat":
        length, width, height = 0.20, 0.05, selected["thickness_m"]
        components = [_box((length, width, height), (length / 2, 0, 0), "add")]
        for y in (-0.012, 0.012):
            components.append(
                dict(
                    shape="cylinder-z",
                    operation="subtract",
                    radius_m=0.003,
                    length_m=height,
                    centre_m=[0.025, y, 0],
                )
            )
        if selected["topology"] == "lightened-web":
            components.append(
                dict(
                    shape="cylinder-z",
                    operation="subtract",
                    radius_m=0.008,
                    length_m=height,
                    centre_m=[0.11, 0, 0],
                )
            )
        section = dict(
            area_m2=width * height,
            iy_m4=width * height**3 / 12,
            basis="Unperforated reference only; holes require the actual 3D solid solve",
        )
        return _model(
            family, selected, length, width, height, components, 500.0, 0.001, section
        )
    length, width, height, wall = 1.5, 0.10, 0.14, selected["wall_m"]
    components = [_box((length, width, height), (length / 2, 0, 0), "add")]
    if selected["topology"] == "rhs":
        components.append(
            _box((length, width - 2 * wall, height - 2 * wall), (length / 2, 0, 0))
        )
        area = width * height - (width - 2 * wall) * (height - 2 * wall)
        iy = (width * height**3 - (width - 2 * wall) * (height - 2 * wall) ** 3) / 12
    else:
        for sign in (-1, 1):
            components.append(
                _box(
                    (length, (width - wall) / 2, height - 2 * wall),
                    (length / 2, sign * (width + wall) / 4, 0),
                )
            )
        area = width * height - (width - wall) * (height - 2 * wall)
        iy = (width * height**3 - (width - wall) * (height - 2 * wall) ** 3) / 12
    section = dict(
        area_m2=area,
        iy_m4=iy,
        basis="Exact prismatic geometric section; shear coefficient remains a research approximation",
    )
    return _model(
        family, selected, length, width, height, components, 10000.0, 0.008, section
    )


def validate_definition(definition):
    if definition.get("schema") != "osr-generated-solid-definition/1":
        raise ValueError("generated solid definition required")
    without_digest = {
        k: v for k, v in definition.items() if k != "physical_definition_sha256"
    }
    if fingerprint(without_digest) != definition.get("physical_definition_sha256"):
        raise ValueError("generated physical definition digest changed")
    if (
        definition.get("physical_validation") is not False
        or definition.get("production_released") is not False
    ):
        raise ValueError("generated part cannot grant qualification")
    part = definition["parts"][0]
    if (
        len(definition["parts"]) != 1
        or fingerprint(part["geometry"]) != part["geometry_sha256"]
    ):
        raise ValueError("one correspondingly defined part required")
    expected = _properties(
        part["geometry"]["components"],
        definition["materials"][part["material"]]["density_kg_m3"],
    )
    if fingerprint(expected) != fingerprint(part["properties"]):
        raise ValueError("analytical solid properties do not match geometry/material")
    if fingerprint(definition) != fingerprint(
        compile_definition(definition["family"], definition["variables"])
    ):
        raise ValueError(
            "generated part changed its fixed function, material, or geometry domain"
        )
    return definition


def screen_definition(definition):
    validate_definition(definition)
    part = definition["parts"][0]
    checks = {
        name: dict(
            state="unknown", basis="Requires native solve or independent evidence"
        )
        for name in CHECKS
    }
    checks["geometry"] = dict(
        state="passed",
        basis="Controlled finite primitive layout; native validity still required",
    )
    checks["mass_inertia"] = dict(
        state="passed",
        basis="Exact signed box/cylinder integrals; native correspondence still required",
    )
    checks["manufacturing"] = dict(
        state="passed",
        basis="Declared research wall/ligament/cutter envelope; fabrication qualification open",
    )
    for name in (
        "linear_service",
        "load_equilibrium",
        "mesh_refinement",
        "independent_benchmark",
    ):
        checks[name] = dict(
            state="not-run", basis="Actual native CAD/Gmsh/CalculiX execution required"
        )
    length = part["geometry"]["envelope_m"][0]
    force = abs(definition["loads"][0]["force_n"][2])
    section = definition["section"]
    young = definition["materials"][part["material"]]["young_pa"]
    return dict(
        checks=checks,
        metrics=dict(
            defined_mass_kg=part["properties"]["mass_kg"],
            defined_volume_m3=part["properties"]["volume_m3"],
            attachment_count=1,
            reference_unperforated_eb_deflection_m=force
            * length**3
            / (3 * young * section["iy_m4"]),
            loaded_face_deflection_m=None,
            maximum_displacement_m=None,
            peak_von_mises_pa=None,
        ),
        physical_release=False,
    )


def toolchain():
    from .generated_parts_native import toolchain as inspect

    return inspect()
