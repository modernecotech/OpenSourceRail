"""Configuration conflicts and provisional six-car/interface investigations.

No load or supplier evidence is manufactured. Planning geometry and mass
scenarios are explicit sensitivities, separate from the retained LM3 axle trace.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
import json
import math
from pathlib import Path

from engineering.design_engine import factory_beam
from engineering.design_engine.civil_qualification import elastic_shortening
from . import civil
from .coverage import ROOT, sha

SPACE = Path(__file__).with_name("data") / "integration-systems.json"
QUALIFICATION = (
    "engineering/civil_exploration/examples/baghdad-qualification/qualification.json"
)
TRAIN = "design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json"
STATIONS = (
    "design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json"
)
DETAILS = "engineering/models/bim/design-detail-register.json"
G = 9.80665


def read(name):
    from .evidence_store import read_json

    return read_json(ROOT / name)


def planning_axles(total_mass_kg, cg_offset_m, *, multiplier=1):
    cfg = json.loads(SPACE.read_text())
    planning = read(QUALIFICATION)["planning_train"]
    if (
        not all(math.isfinite(v) for v in (total_mass_kg, cg_offset_m, multiplier))
        or total_mass_kg <= 0
        or multiplier <= 0
    ):
        raise ValueError("finite positive provisional mass/multiplier required")
    cars, length = planning["cars"], planning["length_m"]
    car = length / cars
    front, rear = cfg["bogie_centre_inset_m"], car - cfg["bogie_centre_inset_m"]
    cg = car / 2 + cg_offset_m
    if not front < cg < rear:
        raise ValueError("car CG outside provisional bogie supports")
    wheelbase = cfg["bogie_wheelbase_m"]
    if not 0 < wheelbase < min(2 * front, rear - front):
        raise ValueError("provisional bogie geometry overlaps/outside car")
    car_weight = total_mass_kg / cars * G * multiplier
    right = car_weight * (cg - front) / (rear - front)
    left = car_weight - right
    axles = [
        dict(
            id=f"car-{k+1}/bogie-{b+1}/axle-{j+1}",
            x_m=k * car + x + d,
            force_n=reaction / 2,
        )
        for k in range(cars)
        for b, (x, reaction) in enumerate(((front, left), (rear, right)))
        for j, d in enumerate((-wheelbase / 2, wheelbase / 2))
    ]
    if len(axles) != planning["axles"] or len({a["x_m"] for a in axles}) != len(axles):
        raise ValueError("provisional axle identity differs")
    total = math.fsum(a["force_n"] for a in axles)
    first = math.fsum(a["force_n"] * a["x_m"] for a in axles)
    if not math.isclose(
        total, total_mass_kg * G * multiplier, rel_tol=1e-12
    ) or not math.isclose(first / total, length / 2 + cg_offset_m, abs_tol=1e-10):
        raise ValueError("provisional axle mass/CG equilibrium differs")
    return dict(
        architecture="metro-6car-provisional-planning",
        cars=cars,
        axle_count=len(axles),
        total_mass_kg=total_mass_kg,
        longitudinal_cg_offset_m=cg_offset_m,
        sensitivity_multiplier=multiplier,
        force_g_m_s2=G,
        axles=axles,
        accepted_supplier_pattern=False,
        supplier_pattern=None,
        geometry_basis="Equal-length cars, equal per-car mass, two symmetric bogies/car and two equally loaded axles/bogie; explicit assumed geometry, no supplier adoption",
    )


@lru_cache(maxsize=1)
def live_envelopes():
    cfg = json.loads(SPACE.read_text())
    train = read(QUALIFICATION)["planning_train"]
    masses = {
        "AW2-planning": train["aw2_mass_t"] * 1000,
        "AW3-planning": train["aw3_mass_t"] * 1000,
        "infrastructure-allowance-sensitivity": train[
            "infrastructure_full_train_allowance_t"
        ]
        * 1000,
    }
    reference_mass = masses["AW2-planning"]
    bases = {}
    for cg in cfg["longitudinal_car_cg_offsets_m"]:
        axles = planning_axles(reference_mass, cg)["axles"]
        for span in (20.0, 25.0):
            bases[cg, span] = factory_beam.section_envelope(
                span,
                [span * i / 40 for i in range(41)],
                [a["x_m"] for a in axles],
                [a["force_n"] for a in axles],
                [],
            )
    cases, worst = [], {span: [] for span in (20.0, 25.0)}
    for label, mass in masses.items():
        for cg in cfg["longitudinal_car_cg_offsets_m"]:
            for multiplier in cfg["axle_sensitivity_multipliers"]:
                pattern = planning_axles(mass, cg, multiplier=multiplier)
                scale = mass / reference_mass * multiplier
                responses = {}
                for span in (20.0, 25.0):
                    base = bases[cg, span]
                    responses[str(span)] = dict(
                        maximum_live_reaction_n=base["maximum_total_reaction_n"]
                        * scale,
                        peak_live_moment_nm=base["continuous_peak"]["moment_nm"]
                        * scale,
                        stations=[
                            dict(
                                x_m=r["x_m"],
                                live_moment_nm=r["maximum_live_moment_nm"] * scale,
                                train_origin_m=r["governing_origin_m"],
                            )
                            for r in base["stations"]
                        ],
                    )
                case = dict(
                    id=f"{label}/cg-{cg:g}/mult-{multiplier:g}",
                    load_label=label,
                    pattern=pattern,
                    responses=responses,
                )
                cases.append(case)
    for span in worst:
        for k in range(41):
            governing = max(
                cases,
                key=lambda c: c["responses"][str(span)]["stations"][k][
                    "live_moment_nm"
                ],
            )
            worst[span].append(
                {
                    **governing["responses"][str(span)]["stations"][k],
                    "governing_case": governing["id"],
                }
            )
    return dict(
        cases=cases,
        station_envelope=worst,
        method="Exact live moving-load events; uniform force scaling reuses homogeneous influence response. Stress assessed only at 41 stations/span.",
        accepted_six_car_loading=False,
        physical_release=False,
    )


def beam_under_planning(candidate, envelope=None):
    envelope = envelope or live_envelopes()
    cfg = json.loads(civil.SPACE.read_text())
    a = read("engineering/factory_examples/data/basis.json")["assumptions"]
    sec, points = candidate["section"], candidate["strand_points"]
    area, I, zc, depth = [
        sec[k] for k in ("area_m2", "inertia_x_m4", "centroid_z_m", "depth_m")
    ]
    counts = Counter(p["z_m"] for p in points)
    groups = [
        dict(
            metallic_area_m2=n * a["strand_area_m2"],
            pretransfer_stress_pa=a["strand_initial_stress_pa"],
            steel_modulus_pa=a["strand_modulus_pa"],
            eccentricity_m=zc - z,
        )
        for z, n in sorted(counts.items())
    ]
    rows = []
    for L in (20.0, 25.0):
        q = (
            area * 2500
            + len(points) * a["strand_area_m2"] * (a["steel_density_kg_m3"] - 2500)
        ) * G
        patch = (
            (2.9 - 2 * candidate["variables"]["stem_width_m"])
            * (depth - cfg["geometry"]["flange_thickness_m"])
            * 2500
            * G
        )
        e = cfg["geometry"]["end_fill_length_m"]
        segments = [(0, L, q), (0, e, patch), (L - e, L, patch)]
        W, first = factory_beam.distributed_resultants(segments)
        for live in envelope["station_envelope"][L]:
            x = live["x_m"]
            dead = factory_beam.gravity_moment(x, segments, W - first / L)
            loss = elastic_shortening(
                groups,
                area_m2=area,
                inertia_m4=I,
                concrete_modulus_pa=a["concrete_transfer_modulus_pa"],
                self_weight_moment_nm=max(dead, 0),
            )
            forces = [
                g["metallic_area_m2"] * (g["pretransfer_stress_pa"] - v)
                for g, v in zip(groups, loss)
            ]
            P = sum(forces) * (1 - a["additional_prestress_loss_fraction"])
            Pe = sum(f * g["eccentricity_m"] for f, g in zip(forces, groups)) * (
                1 - a["additional_prestress_loss_fraction"]
            )
            moment = dead + live["live_moment_nm"]
            rows.append(
                dict(
                    span_m=L,
                    x_m=x,
                    governing_case=live["governing_case"],
                    top_minimum_compression_pa=P / area
                    - (Pe - dead) * (depth - zc) / I,
                    top_maximum_compression_pa=P / area
                    - (Pe - moment) * (depth - zc) / I,
                    soffit_minimum_compression_pa=P / area + (Pe - moment) * zc / I,
                    soffit_maximum_compression_pa=P / area + (Pe - dead) * zc / I,
                )
            )
    minimum = min(
        min(r["top_minimum_compression_pa"], r["soffit_minimum_compression_pa"])
        for r in rows
    )
    maximum = max(
        max(r["top_maximum_compression_pa"], r["soffit_maximum_compression_pa"])
        for r in rows
    )
    return dict(
        candidate_id=candidate["id"],
        variables=candidate["variables"],
        minimum_sampled_service_compression_pa=minimum,
        maximum_sampled_compression_demand_pa=maximum,
        zero_tension_planning_screen=minimum >= 0,
        station_count=len(rows),
        accepted_material_limit_pa=None,
        accepted_loading=False,
        physical_release=False,
    )


def platform_variations():
    cfg = json.loads(SPACE.read_text())
    train = read(QUALIFICATION)["planning_train"]
    need = train["length_m"] + 2 * cfg["platform_end_allowance_m_each"]
    result = []
    for variant in read(STATIONS)["variants"]:
        p = variant["parameters"]
        choices = sorted(
            set([p["platform_length_m"], *cfg["proposed_platform_lengths_m"]])
        )
        rows = [
            dict(
                platform_length_m=L,
                required_research_length_m=need,
                minimum_end_allowance_m=(L - train["length_m"]) / 2,
                six_car_length_screen=L >= need,
                six_metre_panels_per_track=math.ceil(
                    L / cfg["platform_module_length_m"]
                ),
                site_fit_accepted=False,
                egress_accepted=False,
            )
            for L in choices
        ]
        feasible = [r for r in rows if r["six_car_length_screen"]]
        result.append(
            dict(
                archetype=variant["archetype"],
                source_consist=variant["consist"],
                source_platform_length_m=p["platform_length_m"],
                target_train_length_m=train["length_m"],
                candidates=rows,
                selected_preliminary_length_m=(
                    min(r["platform_length_m"] for r in feasible) if feasible else None
                ),
                configuration_conflict="LM3 catalogue length cannot be adopted as a six-car station; no source baseline changed",
            )
        )
    return result


def graph_and_interfaces():
    model = read(TRAIN)
    assemblies = {a["id"]: a for a in model["assemblies"]}
    products = {p["id"]: p for p in model["product_items"]}
    known = set(assemblies) | set(products)
    missing = [
        dict(assembly=a["id"], child=child)
        for a in assemblies.values()
        for child in a["children"]
        if child not in known
    ]
    orphan = [p["id"] for p in products.values() if p["parent"] not in known]
    active, done = set(), set()

    def visit(key):
        if key in active:
            raise ValueError("cyclic physical assembly graph")
        if key in done or key not in assemblies:
            return
        active.add(key)
        for child in assemblies[key]["children"]:
            visit(child)
        active.remove(key)
        done.add(key)

    for key in assemblies:
        visit(key)
    interfaces = read(DETAILS)["mechanical_interfaces"]
    return dict(
        product_count=len(products),
        assembly_count=len(assemblies),
        missing_children=missing,
        orphan_parents=orphan,
        graph_closed=not missing and not orphan,
        interfaces=[
            dict(
                id=r["id"],
                title=r["title"],
                source_ids=r["source_product_ids"],
                tolerance_status=r["tolerance_status"],
                source_id_gaps=sorted(set(r["source_product_ids"]) - known),
                accepted_tolerance_stack=False,
                accepted_reactions=False,
            )
            for r in interfaces
        ],
        manufacturing_release=False,
        physical_release=False,
    )


def run(*, civil_report=None):
    parent = "docs/design-engine/generative-campaign/civil/search.json"
    report = civil_report or read(parent)
    selected = [
        c for c in report["candidates"] if c["id"] in report["selected_candidate_ids"]
    ]
    envelope = live_envelopes()
    checks = [beam_under_planning(c, envelope) for c in report["candidates"]]
    base_by_id = {c["id"]: c for c in report["candidates"]}
    cfg = json.loads(SPACE.read_text())
    options = []
    for response in checks:
        original = base_by_id[response["candidate_id"]]
        other_checks = all(
            row["status"] == "passed"
            for name, row in original["checks"].items()
            if name != "handling_envelope"
        )
        if not response["zero_tension_planning_screen"] or not other_checks:
            continue
        hook = original["metrics"]["maximum_hook_equivalent_kg"]
        for ceiling in cfg["crane_hook_planning_envelopes_kg"]:
            if hook <= ceiling:
                options.append(
                    dict(
                        **response,
                        hook_equivalent_lower_bound_kg=hook,
                        proposed_hook_planning_envelope_kg=ceiling,
                        initial_bed_force_n=original["metrics"]["initial_bed_force_n"],
                        previous_125t_handling_screen=original["checks"][
                            "handling_envelope"
                        ]["status"],
                        complete_rig_mass_kg=None,
                        accepted_crane_capacity_kg=None,
                    )
                )
                break
    shortlist = sorted(
        options,
        key=lambda r: (
            r["proposed_hook_planning_envelope_kg"],
            r["hook_equivalent_lower_bound_kg"],
            r["candidate_id"],
        ),
    )[:2]
    unresolved = [
        "Supplier-defined six-car masses/CG/axles/dynamics and adopted load combinations",
        "Material compression, transfer/end zones, reinforcement, shear/fatigue/deflection and complete load path",
        "Complete rig/crane/bed/mould capacities and site/platform/egress/route geometry acceptance",
    ]
    packages = [
        dict(
            work_package_id="BASIS-CONFIGURATION",
            investigations=[
                dict(
                    id="six-car-provisional-load-cases",
                    load_case_count=len(envelope["cases"]),
                    assumption_space=json.loads(SPACE.read_text()),
                    planning_train=read(QUALIFICATION)["planning_train"],
                    accepted_supplier_pattern=read(QUALIFICATION)["supplier_pattern"],
                    source_selected_beam_responses=[
                        r
                        for r in checks
                        if r["candidate_id"] in report["selected_candidate_ids"]
                    ],
                    generated_beam_response_count=len(checks),
                    provisional_shortlist=shortlist,
                )
            ],
            generated_artifacts=[],
            unresolved_gates=unresolved,
            engineering_design_complete=False,
        ),
        dict(
            work_package_id="SYSTEM-ROUTE",
            investigations=[
                dict(
                    id="six-car-platform-length-variations",
                    variants=platform_variations(),
                )
            ],
            generated_artifacts=[],
            unresolved_gates=unresolved,
            engineering_design_complete=False,
        ),
        dict(
            work_package_id="SYSTEM-INTEGRATION",
            investigations=[
                dict(id="physical-graph-and-icd-coverage", **graph_and_interfaces())
            ],
            generated_artifacts=[],
            unresolved_gates=unresolved,
            engineering_design_complete=False,
        ),
    ]
    return dict(
        schema="osr-queued-integration-study/1",
        packages=packages,
        load_envelopes=envelope,
        all_beam_responses=checks,
        provisional_six_car_beam_shortlist=shortlist,
        inherited_civil_report_sha256=(
            sha(ROOT / parent) if civil_report is None else None
        ),
        source_sha256={
            name: sha(ROOT / name) for name in (QUALIFICATION, TRAIN, STATIONS, DETAILS)
        },
        engineering_design_complete=False,
        physical_release=False,
    )
