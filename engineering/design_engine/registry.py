"""Controlled functional charters over existing domain solvers."""

from copy import deepcopy
from pathlib import Path
import hashlib

from .contracts import problem

ROOT = Path(__file__).resolve().parents[2]
PART_CHECKS = [
    "geometry",
    "nominal_deflection",
    "mesh_refinement",
    "single_attachment_loss",
    "combined_pressure_fault",
    "joint_strength",
    "fatigue",
    "fire",
    "hot_wet_properties",
    "complete_installed_inventory",
    "physical_correlation",
]
ASSEMBLY_CHECKS = [
    "geometry",
    "mass_inertia",
    "interfaces",
    "service",
    "degraded_service",
    "refinement",
    "complete_installed_inventory",
    "supplier_calibration",
    "physical_correlation",
    "independent_acceptance",
]


def charter(
    identifier, adapter, function, variables, *, loads=None, checks=None, domain=None
):
    return problem(
        dict(
            schema="osr-design-problem/1",
            id=identifier,
            revision="1",
            adapter=adapter,
            applicability=dict(
                function=function,
                environment=["simulation", "training", "physical"],
                model_domain=domain
                or [
                    "source-qualified research model; physical qualification remains separate"
                ],
                loads=loads
                or [
                    dict(
                        id="research-load",
                        quantity=dict(
                            value=None,
                            unit="N",
                            state="unknown",
                            basis="define deployment loads before physical qualification",
                        ),
                    )
                ],
                interfaces=[
                    "existing physical part and datum identities; unresolved supplier connections remain explicit"
                ],
                service_life={"cycles": None, "years": None, "state": "unknown"},
                manufacturing=[
                    "existing controlled geometry, joints, process and inspection definitions"
                ],
                mandatory_checks=checks or ASSEMBLY_CHECKS,
            ),
            variables=variables,
            objectives=[
                "defined_mass_kg",
                "installed_cost",
                "lifecycle_cost",
                "production_time",
                "disruption",
                "imported_content",
            ],
            budget=dict(
                evaluations=256, wall_seconds=3600, memory_mib=6144, artifact_mib=512
            ),
            scope="Research candidate comparison; no adopted financial, manufacturing or railway release",
        )
    )


def choice(unit, *values):
    return dict(kind="choice", unit=unit, choices=list(values))


def real(unit, low, high):
    return dict(kind="real", unit=unit, bounds=[low, high])


def problems():
    from .design_alternatives import civil_variables, vehicle_variables

    panel_variables = dict(
        support_span_m=choice("m", 1.0, 0.5, 0.33, 0.2),
        grade_density=choice("kg/m3", 60, 80, 100),
        core_m=choice("m", 0.02, 0.0246, 0.03),
        skin_m=choice("m", 0.0015, 0.002),
    )
    loads = [
        dict(
            id="nominal-pressure",
            quantity=dict(
                value=2000,
                unit="Pa",
                state="synthetic",
                basis="provisional development pressure",
            ),
        ),
        dict(
            id="holdout-pressure",
            quantity=dict(
                value=3500,
                unit="Pa",
                state="synthetic",
                basis="independent combined-fault holdout pressure",
            ),
        ),
    ]
    rows = [
        charter(
            "clipped-side-bay",
            "panel",
            "Fixed 0.994 m × 3.45 m trimmed clipped side bay",
            panel_variables,
            loads=loads,
            checks=PART_CHECKS,
            domain=[
                "flat mapped MITC4 plate, actual discrete clips, hollow elastic rails; no local contact/strength qualification"
            ],
        ),
        charter(
            "clipped-roof-bay",
            "roof",
            "Fixed 0.994 m × 2.35 m roof chord, 0.05 m crown",
            panel_variables,
            loads=loads,
            checks=PART_CHECKS,
            domain=[
                "curved laminate geometry; roof requires shell confirmation; flat plate results are inapplicable"
            ],
        ),
        charter(
            "bogie-interface",
            "interface",
            "Fixed underframe/bogie mounting and battery-carrier interface",
            dict(preload_factor=choice("1", 0.8, 1.0, 1.2)),
        ),
        charter(
            "battery-installation",
            "battery",
            "Fixed metro-6car per-car battery installation and failed-module electrical/thermal duty",
            dict(
                series_modules=choice("ea", 24, 28, 32),
                parallel_strings=choice("ea", 2, 3, 4),
                enclosure_thickness_m=choice("m", 0.003, 0.004, 0.005),
            ),
        ),
        charter(
            "roof-hvac",
            "twin",
            "Fixed metro-6car installed rooftop HVAC/PV arrangement and degraded thermal service",
            dict(
                hvac_modules=choice("ea", 3, 4, 5),
                carrier_thickness_m=choice("m", 0.003, 0.004, 0.005),
            ),
        ),
        charter(
            "full-train",
            "vehicle",
            "Fixed metro-6car whole reference assembly, contacts and service cases",
            dict(family=choice("1", "metro-6car")),
        ),
        charter(
            "vehicle-assembly",
            "vehicle-assembly",
            "Complete fixed metro-6car assembly with alternative installed battery/HVAC/equipment and joint hypotheses",
            vehicle_variables(),
        ),
        charter(
            "viaduct-bay",
            "viaduct",
            "Fixed 20 m double-track deck/pier/bearing and construction-stage package",
            dict(
                pier_height_m=choice("m", 6, 8, 10),
                pile_length_m=choice("m", 12, 15, 18),
                pile_spacing_m=choice("m", 1.5, 2.0, 2.5),
            ),
        ),
        charter(
            "foundation-site",
            "foundation",
            "Site-qualified foundation/junction/station applicability with fixed route scope",
            dict(
                pile_length_m=choice("m", 12, 15, 18),
                pile_spacing_m=choice("m", 1.5, 2.0, 2.5),
            ),
        ),
        charter(
            "civil-campaign",
            "civil",
            "Existing complete coupled civil candidates with their exact route, train and ground profile",
            dict(profile=choice("1", "reference")),
        ),
        charter(
            "civil-system-alternatives",
            "civil-alternatives",
            "Fixed 100 m, five 20 m spans, two tracks and unchanged reference train; alternative deck, pier, material and foundation families",
            civil_variables(),
        ),
        charter(
            "city-options",
            "city-options",
            "Existing controlled city service/energy/topology options",
            dict(city=choice("1", "samawah", "mosul")),
        ),
        charter(
            "engineering-change",
            "engineering-change",
            "Existing source-bound CAD/ERP change review; preparation only",
            dict(city=choice("1", "samawah", "mosul")),
        ),
    ]
    return {r["id"]: r for r in rows}


def get(identifier):
    try:
        return deepcopy(problems()[identifier])
    except KeyError:
        raise ValueError("unknown controlled design problem: " + identifier)


def dependencies(adapter):
    """Physics/adapter/material inputs, deliberately excluding prose and outputs.

    Existing campaign formats retain their own narrower native dependency maps.
    The common envelope additionally binds the adapter and contract implementation.
    """
    shared = {
        "__init__",
        "contracts",
        "bom",
        "engineering_inputs",
        "input_revisions",
        "review",
        "registry",
        "adapters",
        "manufacturing",
        "manufacturing_rules",
        "optimization",
        "interaction_study",
        "uncertainty",
        "runtime",
        "store",
        "publication",
    }
    domain = {
        "roof": "roof_shell",
        "twin": "subsystems",
        "vehicle": "passage",
        "viaduct": "civil_confirmation",
        "foundation": "civil_confirmation",
    }
    if adapter in domain:
        shared.add(domain[adapter])
    if adapter in {"battery", "twin"}:
        shared.add("electrical_installation")
    if adapter in {"viaduct", "foundation"}:
        shared.add("civil_qualification")
        shared.add("foundation_response")
    if adapter in {"vehicle", "vehicle-assembly"}:
        shared.add("vehicle_confirmation")
        shared.add("passage")
    if adapter in {"vehicle-assembly", "civil-alternatives"}:
        shared.add("design_alternatives")
    if adapter == "vehicle-assembly":
        shared.add("electrical_installation")
    paths = {ROOT / "engineering/design_engine" / (name + ".py") for name in shared}
    paths.add(ROOT / "tools/automation/design-engine.py")
    paths.update((ROOT / "design/component-catalogue/src/osr_mech").rglob("*.py"))
    paths.update((ROOT / "design/component-catalogue/schemas").glob("*.json"))
    paths.update((ROOT / "lib/templates").glob("rolling-stock*.toml"))
    if adapter in {
        "panel",
        "roof",
        "interface",
        "viaduct",
        "foundation",
        "civil-alternatives",
    }:
        paths.update((ROOT / "engineering/design_consistency").glob("*.py"))
        paths.add(ROOT / "engineering/composite_panels/config/development.json")
    if adapter in {"panel", "roof"}:
        paths.update((ROOT / "engineering/panel_response").glob("*.py"))
    if adapter in {
        "battery",
        "twin",
        "vehicle",
        "civil",
        "foundation",
        "civil-alternatives",
        "vehicle-assembly",
    }:
        paths.update((ROOT / "engineering/civil_exploration").glob("*.py"))
        paths.update((ROOT / "engineering/reference-parts").glob("*.json"))
        paths.update((ROOT / "engineering/integration_programme").glob("*.py"))
    if adapter in {"twin", "vehicle", "vehicle-assembly"}:
        paths.update((ROOT / "engineering/twin_design").glob("*.py"))
        paths.update((ROOT / "engineering/twin_design/data").glob("*.json"))
        paths.update((ROOT / "engineering/best_practice/data").glob("*.json"))
    if adapter in {"civil", "civil-alternatives"}:
        paths.update((ROOT / "engineering/civil_exploration/config").glob("*.json"))
    if adapter in {"viaduct", "foundation"}:
        paths.add(ROOT / "engineering/industrialisation/vehicle-civil-load-trace.json")
    if adapter in {"city-options", "engineering-change"}:
        directory = ROOT / (
            "engineering/design-options"
            if adapter == "city-options"
            else "engineering/changes"
        )
        paths.update(directory.rglob("*.json"))
        paths.update(directory.rglob("*.toml"))
        paths.update(directory.rglob("*.py"))
    return {
        p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(paths)
    }
