"""Expanded beam families under caller-supplied axle architectures.

Exact one-dimensional moving-force events; sampled gross fibre stresses only.
Every material/force-loss/tool/handling assumption is research, not acceptance.
The old finite SPACE and sealed designs are never edited or bypassed as passed.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from itertools import product
import json
import math
from pathlib import Path

from . import civil
from engineering.design_engine import factory_beam
from engineering.design_engine.civil_qualification import elastic_shortening

ROOT = Path(__file__).resolve().parents[2]
G = 9.80665
SPANS = (20.0, 25.0)
DESIGN_SPACE = dict(
    depth_m=[1.155, 1.4, 1.55, 1.7],
    stem_width_m=[0.3, 0.36],
    strand_count=[48, 96, 112, 128, 144, 160],
    lower_strand_fraction=[0.625, 0.75],
    lift_fraction=[0.2, 0.22],
)
SEED = dict(
    depth_m=1.155,
    stem_width_m=0.3,
    strand_count=48,
    lower_strand_fraction=2 / 3,
    lift_fraction=0.2,
)
SOURCES = [
    "engineering/generative_design/architecture_civil.py",
    "engineering/generative_design/civil.py",
    "engineering/generative_design/data/civil-space.json",
    "engineering/factory_examples/data/basis.json",
    "engineering/design_engine/factory_beam.py",
    "engineering/design_engine/civil_qualification.py",
]
REFERENCES = [
    dict(
        url="https://www.fhwa.dot.gov/bridge/lrfd/pscus054.cfm",
        use="Elastic-shortening compatibility and separate timed loss components; no example strengths/allowables adopted",
    ),
    dict(
        url="https://www.fhwa.dot.gov/bridge/lrfd/pscus056.cfm",
        use="Transfer/service fibre stress distinction; no highway design code adopted for this railway",
    ),
    dict(
        url="https://www.cclint.com/wp-content/uploads/2024/02/CCL-Stressomatic-MKII-250-kN_Flyer.pdf",
        use="Actual UK stressing-tool dimensions and strand range differ from compact research envelope; primary equipment case controls configuration assessment",
    ),
]


def _read(path):
    return json.loads(Path(path).read_text())


def source_inventory():
    return [
        dict(path=p, sha256=sha256((ROOT / p).read_bytes()).hexdigest())
        for p in SOURCES
    ]


def _identity(variables):
    return (
        "arch-civil-"
        + sha256(
            json.dumps(variables, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()[:12]
    )


def _variables(candidate):
    v = candidate.get("variables", candidate)
    if set(v) != set(DESIGN_SPACE):
        raise ValueError("exact expanded beam variables required")
    if v != SEED and any(
        type(v[k]) not in (int, float) or v[k] not in choices
        for k, choices in DESIGN_SPACE.items()
    ):
        raise ValueError("outside explicit expanded beam family")
    if type(v["strand_count"]) is not int:
        raise ValueError("integer strand count required")
    return dict(v)


def candidate_family():
    """192 bounded Cartesian variations plus an exact prior48 control genotype."""
    rows = [
        dict(id=_identity(SEED), variables=dict(SEED), role="prior-balanced48-control")
    ]
    names = list(DESIGN_SPACE)
    for values in product(*(DESIGN_SPACE[name] for name in names)):
        v = dict(zip(names, values))
        rows.append(
            dict(id=_identity(v), variables=v, role="expanded-research-variation")
        )
    return rows


def normalise_pattern(pattern, *, sensitivity=1.25):
    """Keep source forces unchanged and record one explicit multiplicative scale."""
    if (
        type(sensitivity) not in (int, float)
        or not math.isfinite(sensitivity)
        or not 1 <= sensitivity <= 2
    ):
        raise ValueError("explicit sensitivity in1..2 required")
    raw = pattern.get("axles") if isinstance(pattern, dict) else pattern
    if not isinstance(raw, list) or not 1 <= len(raw) <= 64:
        raise ValueError("bounded1..64 moving axles required")
    for a in raw:
        if (
            not isinstance(a, dict)
            or any(
                type(a.get(k)) not in (int, float) or not math.isfinite(a[k])
                for k in ("x_m", "force_n")
            )
            or a["force_n"] <= 0
        ):
            raise ValueError("finite axle coordinates and positive forces required")
    if len({a["x_m"] for a in raw}) != len(raw):
        raise ValueError("distinct axle positions required")
    ordered = sorted(raw, key=lambda a: a["x_m"])
    start = ordered[0]["x_m"]
    source = [
        dict(id=a.get("id", f"axle-{i+1}"), x_m=a["x_m"], force_n=a["force_n"])
        for i, a in enumerate(ordered)
    ]
    if len({a["id"] for a in source}) != len(source):
        raise ValueError("distinct axle identities required")
    total = math.fsum(a["force_n"] for a in source)
    return dict(
        source_axles=source,
        axles=[
            dict(id=a["id"], x_m=a["x_m"] - start, force_n=a["force_n"] * sensitivity)
            for a in source
        ],
        source_coordinate_origin_m=start,
        source_total_force_n=total,
        applied_total_force_n=total * sensitivity,
        sensitivity_multiplier=sensitivity,
        source_force_mass_equivalent_kg=total / G,
        new_mass_to_force_g_m_s2=G,
        source_forces_renormalised=False,
        accepted_pattern=False,
        source_metadata=(
            {k: v for k, v in pattern.items() if k != "axles"}
            if isinstance(pattern, dict)
            else {}
        ),
    )


def live_envelope(pattern, *, spans=SPANS, sensitivity=1.25):
    """Exact moving-origin event envelope at41 sections and continuous live peak."""
    if tuple(spans) != SPANS:
        raise ValueError("expanded beam study spans are20m and25m")
    normal = normalise_pattern(pattern, sensitivity=sensitivity)
    offsets = [a["x_m"] for a in normal["axles"]]
    forces = [a["force_n"] for a in normal["axles"]]
    responses = {}
    for L in spans:
        live = factory_beam.section_envelope(
            L, [L * i / 40 for i in range(41)], offsets, forces, []
        )
        responses[str(float(L))] = dict(
            span_m=L,
            maximum_live_reaction_n=live["maximum_total_reaction_n"],
            peak_live_moment_nm=live["continuous_peak"]["moment_nm"],
            continuous_peak=live["continuous_peak"],
            stations=[
                dict(
                    x_m=r["x_m"],
                    live_moment_nm=r["maximum_live_moment_nm"],
                    governing_origin_m=r["governing_origin_m"],
                )
                for r in live["stations"]
            ],
            accepted_loading=False,
        )
    return dict(
        schema="osr-architecture-live-envelope/1",
        pattern=normal,
        responses=responses,
        method="Axle entry/exit/under-section moving-origin events; continuous live sagging peak from piecewise-quadratic branch extrema; zero train-off live moment included separately in stresses",
        accepted_loading=False,
        physical_release=False,
    )


def _geometry(v, points, cfg):
    """Actual minimum distance to the outer Pi section boundary, less radius."""
    d, w = v["depth_m"], v["stem_width_m"]
    h = d - cfg["geometry"]["flange_thickness_m"]
    b = cfg["geometry"]["deck_width_m"]
    ys = cfg["geometry"]["stem_centres_y_m"]
    radius = cfg["manufacturing"]["strand_envelope_diameter_m"] / 2
    outline = [
        (-b / 2, h),
        (ys[0] - w / 2, h),
        (ys[0] - w / 2, 0),
        (ys[0] + w / 2, 0),
        (ys[0] + w / 2, h),
        (ys[1] - w / 2, h),
        (ys[1] - w / 2, 0),
        (ys[1] + w / 2, 0),
        (ys[1] + w / 2, h),
        (b / 2, h),
        (b / 2, d),
        (-b / 2, d),
    ]

    def distance(p, a, b):
        py, pz = p["y_m"], p["z_m"]
        ay, az = a
        by, bz = b
        vy, vz = by - ay, bz - az
        t = max(0, min(1, ((py - ay) * vy + (pz - az) * vz) / (vy * vy + vz * vz)))
        return math.hypot(py - ay - t * vy, pz - az - t * vz)

    covers = []
    for p in points:
        inside = (
            0 <= p["z_m"] <= d
            and abs(p["y_m"]) <= b / 2
            and (p["z_m"] >= h or any(abs(p["y_m"] - y) <= w / 2 for y in ys))
        )
        dist = min(
            distance(p, a, b) for a, b in zip(outline, outline[1:] + outline[:1])
        )
        covers.append((dist if inside else -dist) - radius)
    pitch = min(
        math.hypot(p["y_m"] - q["y_m"], p["z_m"] - q["z_m"])
        for i, p in enumerate(points)
        for q in points[i + 1 :]
    )
    return dict(
        minimum_clear_concrete_cover_m=min(covers),
        minimum_strand_surface_gap_m=pitch - 2 * radius,
        minimum_grip_surface_gap_m=pitch
        - cfg["manufacturing"]["grip_envelope_diameter_m"],
        actual_lower_strand_count=sum(p["region"] == "lower" for p in points),
        actual_lower_fraction=sum(p["region"] == "lower" for p in points) / len(points),
        candidate_jack_to_adjacent_grip_gap_m=pitch - (0.09 + 0.05) / 2,
        jack_dimensions_basis="90mm assumed nose vs50mm candidate grip; actual supplier GA absent",
    )


def fibre_stresses(
    *,
    force_n,
    prestress_moment_nm,
    gravity_moment_nm,
    live_moment_nm,
    section,
    retention=1,
):
    """Compression positive; exact train-off and governing sagging endpoints."""
    A, I, zc, d = [
        section[k] for k in ("area_m2", "inertia_x_m4", "centroid_z_m", "depth_m")
    ]
    P = force_n * retention
    Pe = prestress_moment_nm * retention

    def fibres(moment):
        return dict(
            top_pa=P / A - (Pe - moment) * (d - zc) / I,
            soffit_pa=P / A + (Pe - moment) * zc / I,
        )

    off = fibres(gravity_moment_nm)
    on = fibres(gravity_moment_nm + live_moment_nm)
    return dict(
        train_off=off,
        train_on=on,
        minimum_compression_pa=min(*off.values(), *on.values()),
        maximum_compression_pa=max(*off.values(), *on.values()),
    )


def _key(v):
    return tuple(v[name] for name in DESIGN_SPACE)


def _fingerprint():
    return sha256(json.dumps(source_inventory(), sort_keys=True).encode()).hexdigest()


@lru_cache(maxsize=512)
def _mechanics(key, fingerprint):
    v = dict(zip(DESIGN_SPACE, key))
    cfg = _read(civil.SPACE)
    a = _read(ROOT / "engineering/factory_examples/data/basis.json")["assumptions"]
    sec = civil.section(v)
    points = civil.strand_points(v)
    geo = _geometry(v, points, cfg)
    A, I, zc, d = [
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
    # The simultaneous shortening matrix is constant and its RHS affine in M.
    # Two exact solves give the affine response; no iterative/tolerance shortcut.
    loss0 = elastic_shortening(
        groups,
        area_m2=A,
        inertia_m4=I,
        concrete_modulus_pa=a["concrete_transfer_modulus_pa"],
        self_weight_moment_nm=0,
    )
    loss1 = elastic_shortening(
        groups,
        area_m2=A,
        inertia_m4=I,
        concrete_modulus_pa=a["concrete_transfer_modulus_pa"],
        self_weight_moment_nm=1e6,
    )

    def prestress(M):
        losses = [u + (v - u) * M / 1e6 for u, v in zip(loss0, loss1)]
        forces = [
            g["metallic_area_m2"] * (g["pretransfer_stress_pa"] - loss)
            for g, loss in zip(groups, losses)
        ]
        return dict(
            force_n=sum(forces),
            prestress_moment_nm=sum(
                f * g["eccentricity_m"] for f, g in zip(forces, groups)
            ),
            minimum_retained_strand_stress_pa=min(
                g["pretransfer_stress_pa"] - loss for g, loss in zip(groups, losses)
            ),
        )

    cases = {}
    for L in SPANS:
        q = (
            A * 2500
            + len(points) * a["strand_area_m2"] * (a["steel_density_kg_m3"] - 2500)
        ) * G
        e = cfg["geometry"]["end_fill_length_m"]
        patch = (
            (cfg["geometry"]["deck_width_m"] - 2 * v["stem_width_m"])
            * (d - cfg["geometry"]["flange_thickness_m"])
            * 2500
            * G
        )
        segments = [(0, L, q), (0, e, patch), (L - e, L, patch)]
        W, first = factory_beam.distributed_resultants(segments)
        dead_left = W - first / L
        lift = factory_beam.handling(
            L,
            segments,
            v["lift_fraction"],
            a["lifting_dynamic_factor"],
            a["rigging_mass_kg"],
            0,
            30,
        )
        stations = sorted(
            set([L * j / 40 for j in range(41)] + [r["x_m"] for r in lift["diagram"]])
        )
        data = []
        sa, sb = lift["support_x_m"]
        left, right = [
            r / a["lifting_dynamic_factor"]
            for r in lift["station_vertical_reactions_n"]
        ]
        for x in stations:
            dead = factory_beam.gravity_moment(x, segments, dead_left)
            state = prestress(max(dead, 0))
            transfer = fibre_stresses(
                **{k: state[k] for k in ("force_n", "prestress_moment_nm")},
                gravity_moment_nm=dead,
                live_moment_nm=0,
                section=sec,
            )
            hm = (
                left * max(x - sa, 0)
                + right * max(x - sb, 0)
                - sum(
                    qq / 2 * (max(x - u, 0) ** 2 - max(x - v, 0) ** 2)
                    for u, v, qq in segments
                )
            ) * a["lifting_dynamic_factor"]
            hand = fibre_stresses(
                **{k: state[k] for k in ("force_n", "prestress_moment_nm")},
                gravity_moment_nm=hm,
                live_moment_nm=0,
                section=sec,
            )
            data.append(
                dict(
                    x_m=x,
                    dead_moment_nm=dead,
                    prestress=state,
                    transfer=transfer,
                    handling=hand,
                )
            )
        cases[str(L)] = dict(
            span_m=L,
            known_concrete_plus_strand_mass_kg=W / G,
            dead_end_reaction_n=W / 2,
            stations=data,
            handling=lift,
        )
    return dict(
        id=_identity(v),
        variables=v,
        section=sec,
        strand_points=points,
        tendon_rows=[dict(z_m=z, strands=n) for z, n in sorted(counts.items())],
        geometry=geo,
        initial_bed_force_n=len(points)
        * a["strand_area_m2"]
        * a["strand_initial_stress_pa"],
        initial_force_per_strand_n=a["strand_area_m2"] * a["strand_initial_stress_pa"],
        tendon_centroid_z_m=sum(p["z_m"] for p in points) / len(points),
        service_force_retention=1 - a["additional_prestress_loss_fraction"],
        cases=cases,
        source_fingerprint=fingerprint,
    )


def mechanical_state(candidate):
    v = _variables(candidate)
    return deepcopy(_mechanics(_key(v), _fingerprint()))


def _check(ok, basis):
    return dict(status="passed" if ok else "failed", basis=basis)


def response(candidate, envelope):
    """Apply one live envelope to cached, force-consistent section/handling states."""
    state = _mechanics(_key(_variables(candidate)), _fingerprint())
    scenarios = []
    for L in SPANS:
        static = state["cases"][str(L)]
        live = envelope["responses"][str(L)]
        byx = {r["x_m"]: r for r in static["stations"]}
        service = []
        for live_row in live["stations"]:
            row = byx[live_row["x_m"]]
            p = row["prestress"]
            service.append(
                dict(
                    x_m=row["x_m"],
                    governing_origin_m=live_row["governing_origin_m"],
                    **fibre_stresses(
                        force_n=p["force_n"],
                        prestress_moment_nm=p["prestress_moment_nm"],
                        gravity_moment_nm=row["dead_moment_nm"],
                        live_moment_nm=live_row["live_moment_nm"],
                        section=state["section"],
                        retention=state["service_force_retention"],
                    ),
                )
            )

        def critical(rows, key):
            return (
                min(rows, key=lambda r: r[key])
                if key.startswith("minimum")
                else max(rows, key=lambda r: r[key])
            )

        service_min = critical(service, "minimum_compression_pa")
        service_max = critical(service, "maximum_compression_pa")
        transfer_min = min(
            r["transfer"]["minimum_compression_pa"] for r in static["stations"]
        )
        transfer_max = max(
            r["transfer"]["maximum_compression_pa"] for r in static["stations"]
        )
        handling_min = min(
            r["handling"]["minimum_compression_pa"] for r in static["stations"]
        )
        handling_max = max(
            r["handling"]["maximum_compression_pa"] for r in static["stations"]
        )
        lift = static["handling"]
        scenarios.append(
            dict(
                span_m=L,
                known_concrete_plus_strand_mass_kg=static[
                    "known_concrete_plus_strand_mass_kg"
                ],
                hook_equivalent_kg=lift["hook_equivalent_load_n"] / G,
                maximum_live_reaction_n=live["maximum_live_reaction_n"],
                maximum_total_reaction_n=static["dead_end_reaction_n"]
                + live["maximum_live_reaction_n"],
                continuous_peak_live_moment_nm=live["peak_live_moment_nm"],
                minimum_sampled_transfer_compression_pa=transfer_min,
                maximum_sampled_transfer_compression_pa=transfer_max,
                minimum_sampled_service_compression_pa=service_min[
                    "minimum_compression_pa"
                ],
                maximum_sampled_service_compression_pa=service_max[
                    "maximum_compression_pa"
                ],
                minimum_sampled_handling_compression_pa=handling_min,
                maximum_sampled_handling_compression_pa=handling_max,
                governing_minimum_service_station=service_min,
                governing_maximum_service_station=service_max,
                handling_station_x_m=lift["support_x_m"],
                longitudinal_rig_span_m=lift["longitudinal_rig_span_m"],
                geometric_upper_rig_headroom_m=lift[
                    "geometric_headroom_above_longitudinal_end_units_m"
                ],
                nominal_equalised_lower_leg_tension_n=lift[
                    "nominal_equalized_leg_tension_n"
                ],
                two_effective_lower_leg_tension_n=lift["two_effective_leg_tension_n"],
                handling_negative_moment_nm=lift["minimum_bending_moment_nm"],
                minimum_retained_strand_stress_pa=min(
                    r["prestress"]["minimum_retained_strand_stress_pa"]
                    for r in static["stations"]
                ),
            )
        )
    metrics = dict(
        initial_bed_force_n=state["initial_bed_force_n"],
        initial_force_per_strand_n=state["initial_force_per_strand_n"],
        tendon_centroid_z_m=state["tendon_centroid_z_m"],
        tendon_eccentricity_m=state["section"]["centroid_z_m"]
        - state["tendon_centroid_z_m"],
        maximum_hook_equivalent_kg=max(r["hook_equivalent_kg"] for r in scenarios),
        minimum_transfer_compression_pa=min(
            r["minimum_sampled_transfer_compression_pa"] for r in scenarios
        ),
        minimum_service_compression_pa=min(
            r["minimum_sampled_service_compression_pa"] for r in scenarios
        ),
        minimum_handling_compression_pa=min(
            r["minimum_sampled_handling_compression_pa"] for r in scenarios
        ),
        maximum_compression_demand_pa=max(
            max(
                r[k]
                for k in (
                    "maximum_sampled_transfer_compression_pa",
                    "maximum_sampled_service_compression_pa",
                    "maximum_sampled_handling_compression_pa",
                )
            )
            for r in scenarios
        ),
        maximum_live_reaction_n=max(r["maximum_live_reaction_n"] for r in scenarios),
        maximum_total_reaction_n=max(r["maximum_total_reaction_n"] for r in scenarios),
        minimum_retained_strand_stress_pa=min(
            r["minimum_retained_strand_stress_pa"] for r in scenarios
        ),
        **state["geometry"],
    )
    cfg = _read(civil.SPACE)["manufacturing"]
    checks = dict(
        transfer_no_tension=_check(
            metrics["minimum_transfer_compression_pa"] >= -1e-6,
            "Sampled full-force straight-tendon transfer research screen",
        ),
        service_no_tension=_check(
            metrics["minimum_service_compression_pa"] >= -1e-6,
            "Both train-off and exact eventwise live sagging at41 stations; zero tension research criterion only",
        ),
        handling_no_tension=_check(
            metrics["minimum_handling_compression_pa"] >= -1e-6,
            "Retained transfer-shortening hypothesis under factored handling bending; sampled fibre screen",
        ),
        concrete_geometric_cover=_check(
            metrics["minimum_clear_concrete_cover_m"]
            >= cfg["concrete_research_cover_m"] - 1e-10,
            "Exact Pi outer-boundary distance less strand radius against50mm research reservation; actual rebar/durability/fire cover unknown",
        ),
        grip_spacing=_check(
            metrics["minimum_grip_surface_gap_m"] >= cfg["grip_research_gap_m"] - 1e-10,
            "50mm candidate grip envelope plus5mm research gap; certified grip/jack access unknown",
        ),
        strand_geometry=_check(
            metrics["minimum_strand_surface_gap_m"] > 0,
            "Distinct nonoverlapping15.2mm clearance envelopes",
        ),
        retained_strand_tension=_check(
            metrics["minimum_retained_strand_stress_pa"] > 0,
            "Positive numerical retained strand tension; stress/strain resistance not accepted",
        ),
    )
    return dict(
        id=state["id"],
        variables=dict(state["variables"]),
        section=dict(state["section"]),
        strand_points=[dict(p) for p in state["strand_points"]],
        tendon_rows=[dict(r) for r in state["tendon_rows"]],
        metrics=metrics,
        scenarios=scenarios,
        checks=checks,
        conditional_stress_and_geometry_pass=all(
            c["status"] == "passed" for c in checks.values()
        ),
        remaining_gates=[
            dict(id=k, status="unknown", basis=v)
            for k, v in dict(
                accepted_loading="Caller forces and sensitivity are research only; actual axle/CG/inertial/dynamic/combination evidence absent",
                material_limits="Concrete/strand strength, compression/tension limits, fatigue and timed losses unaccepted; no numeric strength adopted",
                permanent_actions="Known beam mass excludes conventional reinforcement, rails/plinths/fasteners/utilities/attachments and other permanent actions",
                end_zones="Full force at ends is diagnostic; transmission, bond, splitting/bursting, anchors/inserts/bearing zones unresolved",
                structural_system="Reinforcement, shear/torsion/cracking/camber/deflection, nonlinear/rail interaction and seismic/site design unresolved",
                manufacturing="Rebar/grip/jack access and bed/strongback/return/braces/foundations at increased prestress need new design;60mm grid does not fit assumed90mm jack with adjacent grips. Actual CCL stressing-tool body/length/strand compatibility differs further: architecture equipment primary-source case controls; compact tool/tier assumptions are unselected and do not establish manufacturability",
                handling="No accepted crane/rig mass/configuration/insert/unequal-sharing/tilt/suction/wind/transport capacity; hook includes inherited2t rigging assumption",
                mould="Different depth/width/end fills require new mould stiffeners, bearings, tolerances, removable intrados, casting/curing/stripping trials",
            ).items()
        ],
        accepted_compression_limit_pa=None,
        accepted_bed_capacity_n=None,
        accepted_hook_capacity_kg=None,
        engineering_design_complete=False,
        physical_release=False,
    )


def assess_pattern(candidates, pattern, *, sensitivity=1.25):
    if not isinstance(candidates, list) or not 1 <= len(candidates) <= 300:
        raise ValueError("bounded1..300 explicit beam candidates required")
    envelope = live_envelope(pattern, sensitivity=sensitivity)
    rows = [response(candidate, envelope) for candidate in candidates]
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("distinct candidate definitions required")
    passed = [r for r in rows if r["conditional_stress_and_geometry_pass"]]
    selected = sorted(
        passed,
        key=lambda r: (
            r["metrics"]["maximum_hook_equivalent_kg"],
            r["metrics"]["initial_bed_force_n"],
        ),
    )[:2]
    return dict(
        schema="osr-architecture-civil/1",
        candidate_count=len(rows),
        design_space=DESIGN_SPACE,
        control_seed=SEED,
        live_envelope=envelope,
        candidates=rows,
        conditional_stress_geometry_pass_count=len(passed),
        selected_candidate_ids=[r["id"] for r in selected],
        termination="bounded_candidate_family_exhausted",
        source_inventory=source_inventory(),
        primary_references=REFERENCES,
        scope="One-track simple-support gross elastic beam, transfer/service/handling research; moving forces act on one beam without distribution credit. Source axle forces preserved, applied sensitivity recorded once. Concrete+strand displacement only, other permanent loads unknown. Passing research screens supplies no manufacturable/released system acceptance.",
        engineering_design_complete=False,
        physical_release=False,
    )


def model_definition(candidate, *, span=25.0):
    """Actual new section/tendon geometry; does not pass the old bounded assess."""
    return civil.native_model(mechanical_state(candidate), span=span)


def run():
    """Default384t24-axle six-car planning sensitivity; no supplier adoption."""
    from .integration import planning_axles

    report = assess_pattern(
        candidate_family(), planning_axles(384000, 0, multiplier=1), sensitivity=1.25
    )
    report["source_inventory"] += [
        dict(path=p, sha256=sha256((ROOT / p).read_bytes()).hexdigest())
        for p in (
            "engineering/generative_design/integration.py",
            "engineering/generative_design/data/integration-systems.json",
            "engineering/civil_exploration/examples/baghdad-qualification/qualification.json",
        )
    ]
    return report
