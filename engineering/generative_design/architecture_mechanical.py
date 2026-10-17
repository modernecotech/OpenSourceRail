"""Explicit provisional LM3 architecture feedback with conserved axle loading.

This module branches from the retained three-car reference. It never updates
that reference, approves an axle map, or transfers its steel mass to Baghdad's
separate 111 m six-car planning architecture. Original forces retain their
historical gravity convention; newly added mass has its own declared gravity.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path
import re

from engineering.generative_design import mechanical_systems as mechanical

ROOT = Path(__file__).resolve().parents[2]
TRACE = ROOT / "engineering/industrialisation/vehicle-civil-load-trace.json"
LEGACY_GRAVITY_M_S2 = 9.81
ADDED_MASS_GRAVITY_M_S2 = 9.80665


def _digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def added_mass_support_reactions(mass_kg, cg_x_m, support_x_m):
    """Two-support static equilibrium, before equal sharing within each bogie.

    A negative reaction is retained as a failed no-uplift check, never clipped.
    The assumed centre of gravity and equal axle sharing need actual acceptance.
    """
    left, right = support_x_m
    if (
        not all(math.isfinite(v) for v in [mass_kg, cg_x_m, left, right])
        or mass_kg < 0
        or right <= left
    ):
        raise ValueError(
            "finite nonnegative mass and ordered support positions required"
        )
    weight = mass_kg * ADDED_MASS_GRAVITY_M_S2
    reaction_right = weight * (cg_x_m - left) / (right - left)
    reaction_left = weight - reaction_right
    return dict(
        mass_kg=mass_kg,
        weight_n=weight,
        cg_x_m=cg_x_m,
        support_x_m=[left, right],
        reactions_n=[reaction_left, reaction_right],
        no_uplift=min(reaction_left, reaction_right) >= 0,
        vertical_equilibrium_error_n=reaction_left + reaction_right - weight,
        first_moment_equilibrium_error_nm=reaction_left * left
        + reaction_right * right
        - weight * cg_x_m,
    )


def _source(ctx):
    trace = json.loads(TRACE.read_text())["reference"]
    c = ctx["c"]
    length = c["PROMOTED_LIGHT_METRO_CAR_LENGTH_MM"] / 1000
    if trace["body_count"] != 3 or trace["axle_count"] != 12:
        raise ValueError("LM3 source must remain exactly three bodies/twelve axles")
    ids = [a["id"] for a in trace["axle_pattern"]]
    if len(ids) != len(set(ids)) or len(ids) != 12:
        raise ValueError("LM3 source axle identities must be twelve unique IDs")
    cars = []
    for car in range(1, 4):
        pattern = []
        for axle in trace["axle_pattern"]:
            match = re.fullmatch(
                r"reference-car-(\d+)-bogie-(\d+)-axle-(\d+)", axle["id"]
            )
            if match is None:
                raise ValueError("unrecognised LM3 axle identity")
            if int(match[1]) == car:
                pattern.append(
                    dict(
                        id=axle["id"],
                        bogie=axle["bogie"],
                        bogie_index=int(match[2]),
                        local_x_m=axle["x_m"] - (car - 1) * length,
                        original_source_x_m=axle["x_m"],
                        force_n=axle["static_load_kn"] * 1000,
                    )
                )
        if len(pattern) != 4:
            raise ValueError("four source axle positions required per car")
        bogies = {}
        for bogie_index in [1, 2]:
            members = [a for a in pattern if a["bogie_index"] == bogie_index]
            if len(members) != 2:
                raise ValueError("source bogies require two axles each")
            bogies[bogie_index] = sum(a["local_x_m"] for a in members) / 2
        mass = sum(a["force_n"] for a in pattern) / LEGACY_GRAVITY_M_S2
        cg = sum(a["force_n"] * a["local_x_m"] for a in pattern) / sum(
            a["force_n"] for a in pattern
        )
        cars.append(
            dict(
                car_index=car,
                axles=pattern,
                support_x_m=[bogies[1], bogies[2]],
                source_mass_kg=mass,
                source_force_cg_local_x_m=cg,
            )
        )
    total_mass = sum(c["source_mass_kg"] for c in cars)
    if not math.isclose(total_mass, trace["total_mass_kg"], abs_tol=1e-7):
        raise ValueError("historical 9.81 source mass checksum failed")
    return dict(trace=trace, cars=cars, body_length_m=length, total_mass_kg=total_mass)


def lighter_shared_frame_search(ctx, source):
    """Bounded built-up-I side-sill alternatives with the same spine envelope.

    Side sills are proposed three-plate I sections. The centre spine is an
    explicitly assumed hollow fabrication inside its actual CAD outer envelope.
    All proposed gross member mass is ADDED to the full source car mass: no
    unidentified original structure is subtracted. Rigid transverse ties impose
    common curvature and EI-proportional sharing. The full weight is relocated
    uniformly onto the unchanged bogie support span; no overhang load vanishes.
    """
    spine = mechanical.source_spine_dimensions(ctx)
    sill = ctx["pdr"]["LM3-BDY-P010"]["design_reference_envelope_mm"]
    width = sill[1] / 1000
    side_length = sill[0] / 1000
    source_height = sill[2] / 1000
    span = source["cars"][0]["support_x_m"][1] - source["cars"][0]["support_x_m"][0]
    density = ctx["a"]["steel_density_kg_m3"]
    modulus = ctx["a"]["young_modulus_pa"]
    source_car_force = sum(a["force_n"] for a in source["cars"][0]["axles"])
    domain = dict(
        side_height_m=[source_height, 0.45, 0.6, 0.75],
        flange_thickness_m=[0.016, 0.025, 0.032, 0.04],
        web_thickness_m=[0.008, 0.012, 0.016],
        spine_wall_m=[0.008, 0.012, 0.016, 0.025],
    )
    candidates = []
    for values in itertools.product(*domain.values()):
        variables = dict(zip(domain, values))
        h, tf, tw, tc = values
        side_area = 2 * width * tf + tw * (h - 2 * tf)
        side_i = (width * h**3 - (width - tw) * (h - 2 * tf) ** 3) / 12
        bc, hc = spine["width_m"], spine["height_m"]
        centre_area = bc * hc - (bc - 2 * tc) * (hc - 2 * tc)
        centre_i = (bc * hc**3 - (bc - 2 * tc) * (hc - 2 * tc) ** 3) / 12
        gross_mass = (
            2 * side_area * side_length + centre_area * spine["length_m"]
        ) * density
        inertias = [side_i, centre_i, side_i]
        total_i = sum(inertias)
        force = source_car_force + gross_mass * ADDED_MASS_GRAVITY_M_S2
        q = force / span
        deflection = 5 * q * span**4 / (384 * modulus * total_i)
        shares = [i / total_i for i in inertias]
        moment = q * span**2 / 8
        checks = [
            dict(
                id="local_three_member_stiffness",
                status="passed" if deflection <= span / 1000 else "failed",
                basis="Full historical car force plus every new member weight; rigid ties; unchanged support span; E200GPa and L/1000 research target only",
            ),
            dict(
                id="existing_sill_height_envelope",
                status="passed" if h <= source_height else "failed",
                basis="LM3-BDY-P010 source260mm height. Taller I-section proposals require new floor, doorway, bolster and shell architecture.",
            ),
            dict(
                id="strength_stability_connections_and_manufacture",
                status="unknown",
                basis="No certified steel, flange/web local buckling, shear/torsional stability, weld/bolster/crossbearer fatigue, interruption at doorways, machining, distortion/NDT or first-article acceptance.16m flanges require a proven stock/cutting/joint route.",
            ),
            dict(
                id="net_mass_and_vehicle_integration",
                status="unknown",
                basis="All new gross steel is added without removing original structure. Actual replacement delta, vertical/lateral CG, axle ratings, bogie/suspension/brake/traction/civil demand and route gauge remain unaccepted.",
            ),
        ]
        identity = (
            "lm3-frame-i-"
            + hashlib.sha256(
                json.dumps(variables, sort_keys=True).encode()
            ).hexdigest()[:12]
        )
        candidates.append(
            dict(
                id=identity,
                variables=variables,
                proposed_gross_addition_per_car_kg=gross_mass,
                member_inertias_m4=inertias,
                member_load_shares=shares,
                nominal_compatible_deflection_m=deflection,
                research_deflection_limit_m=span / 1000,
                nominal_member_stresses_pa=[
                    moment * shares[0] * h / 2 / side_i,
                    moment * shares[1] * hc / 2 / centre_i,
                    moment * shares[2] * h / 2 / side_i,
                ],
                member_end_reactions_n=[force * fraction / 2 for fraction in shares],
                modeled_car_force_n=force,
                ideal_web_clear_height_to_thickness_ratio=(h - 2 * tf) / tw,
                side_flange_stock_each_m=[side_length, width, tf],
                side_web_stock_each_m=[side_length, h - 2 * tf, tw],
                source_spine_outer_m=[spine["length_m"], bc, hc],
                checks=checks,
                local_stiffness_screen_passed=checks[0]["status"] == "passed",
                existing_configuration_compatible=checks[1]["status"] == "passed",
                accepted_loading=False,
                engineering_design_complete=False,
                physical_release=False,
            )
        )
    local_passes = [c for c in candidates if c["local_stiffness_screen_passed"]]
    proposal = min(
        local_passes,
        key=lambda c: (c["proposed_gross_addition_per_car_kg"], c["id"]),
        default=None,
    )
    return dict(
        id="lm3-lighter-shared-frame-research",
        variable_space=domain,
        candidates=candidates,
        proposed_candidate_ids=[] if proposal is None else [proposal["id"]],
        selected_existing_configuration_ids=[],
        termination=dict(
            reason="bounded_domain_exhausted",
            evaluations=len(candidates),
            local_stiffness_pass_count=len(local_passes),
            source_compatible_local_stiffness_pass_count=sum(
                c["existing_configuration_compatible"] for c in local_passes
            ),
        ),
        engineering_design_complete=False,
        physical_release=False,
    )


def _case(identity, gap, added_per_car, frame_id, source):
    body_length = source["body_length_m"]
    cars, axles = [], []
    for original_car in source["cars"]:
        number = original_car["car_index"]
        start = (number - 1) * (body_length + gap)
        # New members are assumed symmetric about the body midpoint. This is
        # a calculation hypothesis, not an inferred measured mass-property.
        added_cg = body_length / 2
        reactions = added_mass_support_reactions(
            added_per_car, added_cg, original_car["support_x_m"]
        )
        per_bogie = dict(zip([1, 2], reactions["reactions_n"]))
        car_axles = []
        for original_axle in original_car["axles"]:
            addition = per_bogie[original_axle["bogie_index"]] / 2
            axle = dict(
                id=original_axle["id"],
                architecture_id="LM3",
                car_index=number,
                bogie=original_axle["bogie"],
                x_m=start + original_axle["local_x_m"],
                local_x_m=original_axle["local_x_m"],
                source_force_n=original_axle["force_n"],
                added_force_n=addition,
                force_n=original_axle["force_n"] + addition,
                source_mass_kg=original_axle["force_n"] / LEGACY_GRAVITY_M_S2,
                added_mass_kg=addition / ADDED_MASS_GRAVITY_M_S2,
                accepted_loading=False,
            )
            axles.append(axle)
            car_axles.append(axle)
        cars.append(
            dict(
                id=f"LM3-car-{number}",
                start_x_m=start,
                centre_x_m=start + body_length / 2,
                end_x_m=start + body_length,
                source_mass_kg=original_car["source_mass_kg"],
                added_gross_frame_mass_kg=added_per_car,
                modeled_mass_kg=original_car["source_mass_kg"] + added_per_car,
                assumed_added_cg_local_x_m=added_cg,
                added_mass_support_equilibrium=reactions,
                source_axle_local_positions_m=[a["local_x_m"] for a in car_axles],
                baseline_plus_added_force_n=sum(a["force_n"] for a in car_axles),
                accepted_loading=False,
            )
        )
    total_mass = source["total_mass_kg"] + 3 * added_per_car
    total_force = sum(a["force_n"] for a in axles)
    expected_force = (
        sum(a["force_n"] for car in source["cars"] for a in car["axles"])
        + 3 * added_per_car * ADDED_MASS_GRAVITY_M_S2
    )
    expected_moment = sum(
        sum(
            a["force_n"] * (car["start_x_m"] + a["local_x_m"])
            for a in source_car["axles"]
        )
        + added_per_car
        * ADDED_MASS_GRAVITY_M_S2
        * (car["start_x_m"] + car["assumed_added_cg_local_x_m"])
        for car, source_car in zip(cars, source["cars"])
    )
    actual_moment = sum(a["force_n"] * a["x_m"] for a in axles)
    preserved_ids = {a["id"] for car in source["cars"] for a in car["axles"]}
    actual_ids = {a["id"] for a in axles}
    preserved = (
        len(axles) == 12 and len(actual_ids) == 12 and actual_ids == preserved_ids
    )
    physical_mass_moment = sum(
        (a["source_mass_kg"] + a["added_mass_kg"]) * a["x_m"] for a in axles
    )
    length = 3 * body_length + 2 * gap
    unchanged = gap == 0 and added_per_car == 0
    return dict(
        id=identity,
        architecture_id="LM3",
        architecture_scope="Three16.5m bodies/six bogies/twelve source axles; separate from Baghdad111m six-car planning",
        body_count=3,
        bogie_count=6,
        axle_count=12,
        body_length_m=body_length,
        inter_car_gap_m=gap,
        train_length_m=length,
        total_mass_kg=total_mass,
        mass_scope="Original AW2 planning mass PLUS full hypothetical new frame gross mass. Original frame mass is not removed; new gangway/carrier/service growth mass is NOT yet included.",
        mass_is_provisional_model_subtotal=True,
        source_aw2_mass_kg=source["total_mass_kg"],
        modeled_added_frame_mass_kg=3 * added_per_car,
        unclosed_gangway_and_gap_equipment_mass_kg=None,
        accepted_replacement_net_steel_mass_kg=None,
        referenced_frame_candidate_id=frame_id,
        cars=cars,
        axles=axles,
        horizontal_mass_cg_x_m=physical_mass_moment / total_mass,
        vertical_cg_m=None,
        lateral_cg_m=None,
        force_cg_x_m=sum(a["force_n"] * a["x_m"] for a in axles) / total_force,
        mixed_convention_total_force_n=total_force,
        expected_source_plus_delta_force_n=expected_force,
        force_balance_error_n=total_force - expected_force,
        expected_source_plus_delta_first_moment_nm=expected_moment,
        first_moment_balance_error_nm=actual_moment - expected_moment,
        unqualified_60m_platform_total_length_margin_m=60 - length,
        source_frozen_baseline=False,
        source_reference_geometry_unchanged=unchanged,
        existing_configuration_compatible=unchanged,
        accepted_loading=False,
        source_force_gravity_m_s2=LEGACY_GRAVITY_M_S2,
        addition_force_gravity_m_s2=ADDED_MASS_GRAVITY_M_S2,
        checks=[
            dict(
                id="source_axle_identity_and_load_preservation",
                status="passed" if preserved else "failed",
                basis="All twelve original IDs/local offsets and original forces retained; only declared car translation and equilibrium-derived added force change the branch",
            ),
            dict(
                id="vertical_and_first_moment_equilibrium",
                status=(
                    "passed"
                    if abs(total_force - expected_force) < 1e-6
                    and abs(actual_moment - expected_moment) < 1e-5
                    else "failed"
                ),
                basis="Original force contributions plus new-mass force/first moment, with unchanged bogie supports and equal sharing within each two-axle bogie",
            ),
            dict(
                id="existing_architecture_compatibility",
                status="passed" if unchanged else "failed",
                basis="Nonzero inter-car spacing and750mm side-frame proposals require a new configuration; original catalogue remains unchanged",
            ),
            dict(
                id="accepted_mass_loading_and_manufacturing",
                status="unknown",
                basis="Provisional AW2+gross-frame mass/CG model only. New gap equipment/net replacement mass, verticalCG, structure/joints/buckling, axle/suspension/brake/traction capacities, moving civil loads, platform/route and manufacturing acceptance remain open.",
            ),
        ],
        engineering_design_complete=False,
        physical_release=False,
    )


def run():
    ctx = mechanical.context()
    source = _source(ctx)
    frame = mechanical.evaluate(
        "chassis_shared", dict(section_height_m=0.75, wall_m=0.025), ctx
    )
    addition = frame["metrics"]["proposed_three_member_gross_mass_kg"]
    if not math.isclose(addition, 14463.625, abs_tol=1e-7):
        raise ValueError(
            "source750x25 frame addition changed; review architecture feedback"
        )
    payload = json.dumps(
        ["chassis_shared", frame["variables"]], sort_keys=True, separators=(",", ":")
    )
    frame_id = "chassis_shared-" + hashlib.sha256(payload.encode()).hexdigest()[:12]
    cases = [
        _case("lm3-source-reference", 0, 0, None, source),
        _case("lm3-gap-1p8", 1.8, 0, None, source),
        _case("lm3-gap-2p0", 2.0, 0, None, source),
        _case("lm3-gap-1p8-frame-750x25", 1.8, addition, frame_id, source),
        _case("lm3-gap-2p0-frame-750x25", 2.0, addition, frame_id, source),
    ]
    lighter = lighter_shared_frame_search(ctx, source)
    for identity in lighter["proposed_candidate_ids"]:
        proposal = next(c for c in lighter["candidates"] if c["id"] == identity)
        cases.append(
            _case(
                "lm3-gap-1p8-lighter-built-up-i",
                1.8,
                proposal["proposed_gross_addition_per_car_kg"],
                identity,
                source,
            )
        )
    hashes = dict(ctx["source_sha256"])
    hashes[str(Path(__file__).relative_to(ROOT))] = _digest(__file__)
    return dict(
        schema="osr-provisional-lm3-architecture-mechanical/1",
        architecture_id="LM3",
        cases=cases,
        retained_heavy_frame_candidate=frame,
        lighter_frame_study=lighter,
        source_sha256=hashes,
        source_references=[
            dict(path=str(TRACE.relative_to(ROOT)), object="reference", accepted=False),
            dict(
                path=str((mechanical.CAD / "baseline.py").relative_to(ROOT)),
                object="PROMOTED_LIGHT_METRO_*",
                accepted=False,
            ),
            dict(
                path=str((mechanical.CAD / "product_geometry.py").relative_to(ROOT)),
                object="_underframe centre-spine220x380mm outer envelope",
                accepted=False,
            ),
            dict(
                path=str(mechanical.DATA.relative_to(ROOT)),
                object="chassis_shared 750mm/25mm and proposed inter-car gaps",
                accepted=False,
            ),
        ],
        research_basis=dict(
            source_force_gravity_m_s2=LEGACY_GRAVITY_M_S2,
            added_mass_force_gravity_m_s2=ADDED_MASS_GRAVITY_M_S2,
            retained_frame_reference_calculation_gravity_m_s2=ctx["a"]["gravity_m_s2"],
            added_mass_cg="Each symmetric proposed frame is assumed centred longitudinally in its own car; actual vertical/lateral CG unclosed",
            support_model="Original two bogie pivots per car from averages of each actual two-axle local pattern; static support reactions balance added mass/first moment; half each bogie reaction assigned to each axle",
            source_members_retained="Full new gross member mass is added without subtracting unidentified existing frame mass; conservative mass hypothesis, not a released replacement delta",
            dynamic_effects="Not included. New gap hardware/verticalCG/traction/braking/running/structural/civil and manufacturing limits remain unaccepted",
        ),
        six_car_transfer=dict(
            architecture="Baghdad111m/sixcar planning",
            lm3_frame_delta_transferred=False,
            accepted_axle_distribution=None,
            accepted_loading=False,
            basis="No multiplication or transfer of LM3 changes establishes a six-car vehicle design. Its architecture/loading must be reconciled separately.",
        ),
        input_trace_accepted=False,
        source_frozen_baseline=False,
        engineering_design_complete=False,
        physical_release=False,
    )
