"""Feedback-driven Pi20/Pi25 research variations; no design/release acceptance.

The historical three-car axle forces and existing loss/handling assumptions are
reused. New dimensions are proposals, never edits to the canonical beam family.
"""

from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
import math
from pathlib import Path

from engineering.design_engine.civil_qualification import elastic_shortening
from engineering.design_engine import factory_beam
from engineering.factory_examples.models import part, volume

ROOT = Path(__file__).resolve().parents[2]
SPACE = Path(__file__).with_name("data") / "civil-space.json"
G = factory_beam.G


def _read(path):
    return json.loads(path.read_text())


def section(variables):
    """Exact centroid/inertia of three nonoverlapping rectangular solids."""
    cfg = _read(SPACE)["geometry"]
    d, w, t, b = (
        variables["depth_m"],
        variables["stem_width_m"],
        cfg["flange_thickness_m"],
        cfg["deck_width_m"],
    )
    h = d - t
    pieces = [(b, t, h + t / 2), (w, h, h / 2), (w, h, h / 2)]
    area = sum(bi * hi for bi, hi, z in pieces)
    zc = sum(bi * hi * z for bi, hi, z in pieces) / area
    inertia = sum(bi * hi**3 / 12 + bi * hi * (z - zc) ** 2 for bi, hi, z in pieces)
    return dict(area_m2=area, centroid_z_m=zc, inertia_x_m4=inertia, depth_m=d)


def strand_points(variables):
    cfg = _read(SPACE)
    m = cfg["manufacturing"]
    per_stem = variables["strand_count"] // 2
    nlow = (
        round(per_stem * variables["lower_strand_fraction"] / m["columns_per_stem"])
        * m["columns_per_stem"]
    )
    points = []
    for stem_y in cfg["geometry"]["stem_centres_y_m"]:
        for region, count in (("lower", nlow), ("upper", per_stem - nlow)):
            for k in range(count):
                row, col = divmod(k, m["columns_per_stem"])
                z = (
                    m["bottom_axis_cover_m"] + row * m["strand_pitch_m"]
                    if region == "lower"
                    else variables["depth_m"]
                    - m["top_axis_cover_m"]
                    - row * m["strand_pitch_m"]
                )
                y = (
                    stem_y
                    + (col - (m["columns_per_stem"] - 1) / 2) * m["strand_pitch_m"]
                )
                points.append(dict(y_m=y, z_m=z, region=region))
    return points


@lru_cache(maxsize=2)
def _live(span):
    trace = _read(ROOT / "engineering/industrialisation/vehicle-civil-load-trace.json")[
        "reference"
    ]
    axles = trace["axle_pattern"]
    if (
        trace["body_count"] != 3
        or trace["axle_count"] != 12
        or not math.isclose(
            sum(r["static_load_kn"] * 1000 / 9.81 for r in axles),
            trace["total_mass_kg"],
            rel_tol=1e-10,
        )
    ):
        raise ValueError("historical three-car axle identity/mass balance changed")
    return factory_beam.section_envelope(
        span,
        [span * i / 40 for i in range(41)],
        [r["x_m"] - axles[0]["x_m"] for r in axles],
        [r["static_load_kn"] * 1000 for r in axles],
        [],
    )


def _check(ok, basis):
    return dict(status="passed" if ok else "failed", basis=basis)


def _unknown(basis):
    return dict(status="unknown", basis=basis)


def assess(variables):
    cfg = _read(SPACE)
    for name in (
        "depth_m",
        "stem_width_m",
        "strand_count",
        "lower_strand_fraction",
        "lift_fraction",
    ):
        if variables[name] not in cfg[name]:
            raise ValueError("outside bounded civil design space: " + name)
    a = _read(ROOT / "engineering/factory_examples/data/basis.json")["assumptions"]
    sec, pts, m = section(variables), strand_points(variables), cfg["manufacturing"]
    A, I, zc, depth = (
        sec[k] for k in ("area_m2", "inertia_x_m4", "centroid_z_m", "depth_m")
    )
    radius = m["strand_envelope_diameter_m"] / 2
    cover = min(
        min(
            p["z_m"] - radius,
            depth - p["z_m"] - radius,
            variables["stem_width_m"] / 2
            - abs(
                p["y_m"]
                - min(
                    cfg["geometry"]["stem_centres_y_m"], key=lambda y: abs(y - p["y_m"])
                )
            )
            - radius,
        )
        for p in pts
    )
    gap = min(
        math.hypot(p["y_m"] - q["y_m"], p["z_m"] - q["z_m"])
        - m["grip_envelope_diameter_m"]
        for j, p in enumerate(pts)
        for q in pts[j + 1 :]
    )
    row_counts = {}
    for p in pts:
        row_counts[p["z_m"]] = row_counts.get(p["z_m"], 0) + 1
    groups = [
        dict(
            metallic_area_m2=n * a["strand_area_m2"],
            pretransfer_stress_pa=a["strand_initial_stress_pa"],
            steel_modulus_pa=a["strand_modulus_pa"],
            eccentricity_m=zc - z,
        )
        for z, n in sorted(row_counts.items())
    ]
    scenarios = []
    for L in cfg["span_pair_m"]:
        h = depth - cfg["geometry"]["flange_thickness_m"]
        q = (
            A * 2500
            + len(pts) * a["strand_area_m2"] * (a["steel_density_kg_m3"] - 2500)
        ) * G
        patch_q = (
            (cfg["geometry"]["deck_width_m"] - 2 * variables["stem_width_m"])
            * h
            * 2500
            * G
        )
        e = cfg["geometry"]["end_fill_length_m"]
        segments = [(0, L, q), (0, e, patch_q), (L - e, L, patch_q)]
        W, first = factory_beam.distributed_resultants(segments)
        lift = factory_beam.handling(
            L,
            segments,
            variables["lift_fraction"],
            a["lifting_dynamic_factor"],
            a["rigging_mass_kg"],
            0,
            30,
        )
        # Exact handling extrema are included; railway stress remains sampled.
        stations = sorted(
            set(
                [r["x_m"] for r in _live(L)["stations"]]
                + [r["x_m"] for r in lift["diagram"]]
            )
        )
        live_rows = {r["x_m"]: r for r in _live(L)["stations"]}
        transfer, service, handling_values = [], [], []
        for x in stations:
            dead = factory_beam.gravity_moment(x, segments, W - first / L)
            losses = elastic_shortening(
                groups,
                area_m2=A,
                inertia_m4=I,
                concrete_modulus_pa=a["concrete_transfer_modulus_pa"],
                self_weight_moment_nm=max(dead, 0),
            )
            forces = [
                g["metallic_area_m2"] * (g["pretransfer_stress_pa"] - loss)
                for g, loss in zip(groups, losses)
            ]
            P = sum(forces)
            Pe = sum(f * g["eccentricity_m"] for f, g in zip(forces, groups))

            def stress(moment, factor=1):
                return [
                    P * factor / A - (Pe * factor - moment) * (depth - zc) / I,
                    P * factor / A + (Pe * factor - moment) * zc / I,
                ]

            transfer.extend(stress(dead))
            if x in live_rows:
                live = live_rows[x]["maximum_live_moment_nm"]
                service.extend(
                    stress(dead, 1 - a["additional_prestress_loss_fraction"])
                )
                service.extend(
                    stress(dead + live, 1 - a["additional_prestress_loss_fraction"])
                )
            # Self-weight support changes, with retained transfer shortening
            # hypothesis frozen at this station; no loss recalibration credit.
            sa, sb = lift["support_x_m"]
            R = W / 2
            hm = (
                R * max(x - sa, 0)
                + R * max(x - sb, 0)
                - sum(
                    qq / 2 * (max(x - u, 0) ** 2 - max(x - v, 0) ** 2)
                    for u, v, qq in segments
                )
            ) * a["lifting_dynamic_factor"]
            handling_values.extend(stress(hm))
        scenarios.append(
            dict(
                span_m=L,
                known_concrete_plus_strand_mass_kg=W / G,
                hook_equivalent_kg=lift["hook_equivalent_load_n"] / G,
                diagnostic_peak_live_moment_nm=_live(L)["continuous_peak"]["moment_nm"],
                minimum_transfer_compression_pa=min(transfer),
                minimum_service_compression_pa=min(service),
                minimum_handling_compression_pa=min(handling_values),
                maximum_compression_demand_pa=max(transfer + service + handling_values),
                handling_negative_moment_nm=lift["minimum_bending_moment_nm"],
                nominal_four_leg_tension_n=lift["nominal_equalized_leg_tension_n"],
                two_effective_leg_tension_n=lift["two_effective_leg_tension_n"],
                handling_station_x_m=lift["support_x_m"],
                longitudinal_spreader_span_m=lift["longitudinal_rig_span_m"],
                upper_rig_headroom_m=lift[
                    "geometric_headroom_above_longitudinal_end_units_m"
                ],
            )
        )
    metrics = dict(
        minimum_transfer_compression_pa=min(
            r["minimum_transfer_compression_pa"] for r in scenarios
        ),
        minimum_service_compression_pa=min(
            r["minimum_service_compression_pa"] for r in scenarios
        ),
        minimum_handling_compression_pa=min(
            r["minimum_handling_compression_pa"] for r in scenarios
        ),
        minimum_geometric_cover_m=cover,
        minimum_grip_surface_gap_m=gap,
        maximum_hook_equivalent_kg=max(r["hook_equivalent_kg"] for r in scenarios),
        maximum_compression_demand_pa=max(
            r["maximum_compression_demand_pa"] for r in scenarios
        ),
        initial_bed_force_n=len(pts)
        * a["strand_area_m2"]
        * a["strand_initial_stress_pa"],
        original_48_strand_bed_force_n=48
        * a["strand_area_m2"]
        * a["strand_initial_stress_pa"],
        initial_force_per_strand_n=a["strand_area_m2"] * a["strand_initial_stress_pa"],
        tendon_centroid_above_soffit_m=sum(p["z_m"] for p in pts) / len(pts),
        tendon_eccentricity_below_concrete_centroid_m=zc
        - sum(p["z_m"] for p in pts) / len(pts),
        initial_prestress_moment_about_concrete_centroid_nm=sum(
            (zc - p["z_m"]) * a["strand_area_m2"] * a["strand_initial_stress_pa"]
            for p in pts
        ),
        accepted_concrete_compression_limit_pa=None,
        accepted_crane_capacity_kg=None,
        accepted_bed_capacity_n=None,
    )
    checks = {
        name: _check(
            metrics[key] >= -1e-6,
            "Compression-positive sampled gross-section full-force straight-tendon research diagnostic; not material/code acceptance",
        )
        for name, key in (
            ("transfer_no_tension", "minimum_transfer_compression_pa"),
            ("three_car_service_no_tension", "minimum_service_compression_pa"),
            ("handling_no_tension", "minimum_handling_compression_pa"),
        )
    }
    checks.update(
        geometric_cover=_check(
            cover >= m["concrete_research_cover_m"] - 1e-10,
            "Nominal clear geometric cover against 50 mm research reservation; accepted durability/fire/rebar cover unknown",
        ),
        grip_spacing=_check(
            gap >= m["grip_research_gap_m"] - 1e-10,
            "50 mm candidate grip envelope plus 5 mm research gap; actual strand/grip/jack qualification unknown",
        ),
        handling_envelope=_check(
            metrics["maximum_hook_equivalent_kg"]
            <= m["handling_research_hook_equivalent_kg"],
            "125 t existing runway research reservation; unknown reinforcement and rig mass make this a lower-bound screen",
        ),
        prismatic_section_geometry=_check(
            variables["stem_width_m"] < 1.435,
            "Three nonoverlapping prismatic section rectangles; no geometric demouldability, formwork resistance or casting access acceptance inferred",
        ),
    )
    unknowns = {
        name: _unknown(basis)
        for name, basis in dict(
            six_car_loading="Accepted six-car axle allocation, dynamic factors and load combinations absent",
            material_limits="Concrete/strand transfer and service resistances and timed losses absent",
            end_zone="Full force at beam ends is diagnostic; transmission, bond, bursting and anchorage qualification absent",
            shear_fatigue_deflection="Reinforcement, shear, torsion, cracking, fatigue, deflection/camber and dynamic interaction unresolved",
            lifting_and_transport="Insert/breakout resistance, unequal sharing, tilt, suction, wind, full rig mass, accepted rig configuration and route absent",
            bed_and_mould="Increased bed force/return axis, strongback, restraint, foundations and split mould stiffness/access need actual redesign",
            track_and_substructure="Rail fastening, bearings, seismic/site/geotechnical and civil interfaces unresolved",
            manufacturing_qualification="Rebar/grip/jack access, tolerances, process trials, curing/transfer strength, traceability and qualified suppliers absent",
            demould_route="End diaphragms obstruct longitudinal core withdrawal; split removable or collapsible intrados forms, draft, clearance and demould/lift trials require explicit tooling design",
        ).items()
    }
    return dict(
        id="civil-"
        + sha256(json.dumps(variables, sort_keys=True).encode()).hexdigest()[:12],
        variables=dict(variables),
        section=sec,
        strand_points=pts,
        tendon_rows=[
            dict(
                z_m=z,
                total_strands=n,
                strands_each_stem=n // 2,
                initial_force_n=n * a["strand_area_m2"] * a["strand_initial_stress_pa"],
            )
            for z, n in sorted(row_counts.items())
        ],
        scenarios=scenarios,
        metrics=metrics,
        checks=checks,
        remaining_gates=unknowns,
        conditional_feasible=all(r["status"] == "passed" for r in checks.values()),
        design_complete=False,
        physical_release=False,
    )


def _key(v):
    return tuple(
        v[k]
        for k in (
            "depth_m",
            "stem_width_m",
            "strand_count",
            "lower_strand_fraction",
            "lift_fraction",
        )
    )


def search(*, budget=128):
    if type(budget) is not int or not 1 <= budget <= 2048:
        raise ValueError("civil candidate budget must be an integer in 1..2048")
    cfg = _read(SPACE)
    seed = dict(
        depth_m=1.155,
        stem_width_m=0.3,
        strand_count=48,
        lower_strand_fraction=2 / 3,
        lift_fraction=0.2,
    )
    queue = [(seed, None, 0, "retained balanced-48 geometry seed")]
    seen = set()
    rows = []
    while queue and len(rows) < budget:
        v, parent, generation, reason = queue.pop(0)
        if _key(v) in seen:
            continue
        seen.add(_key(v))
        row = assess(v)
        row.update(
            id="civil-"
            + sha256(json.dumps(v, sort_keys=True).encode()).hexdigest()[:12],
            parent_id=parent,
            generation=generation,
            mutation_reason=reason,
        )
        rows.append(row)
        # Failures drive the priority of bounded one-coordinate neighbours.
        failed = [k for k, c in row["checks"].items() if c["status"] == "failed"]
        priority = (
            (
                "strand_count",
                "depth_m",
                "lower_strand_fraction",
                "lift_fraction",
                "stem_width_m",
            )
            if "three_car_service_no_tension" in failed
            else (
                "lower_strand_fraction",
                "lift_fraction",
                "depth_m",
                "strand_count",
                "stem_width_m",
            )
        )
        if "geometric_cover" in failed or "grip_spacing" in failed:
            priority = (
                "stem_width_m",
                "depth_m",
                "strand_count",
                "lower_strand_fraction",
                "lift_fraction",
            )
        for name in priority:
            values = cfg[name]
            index = values.index(v[name])
            # Both directions retained. Count and depth upward first, so failures
            # receive increased capacity before local mass minimisation.
            for index2 in (index + 1, index - 1):
                if 0 <= index2 < len(values):
                    child = dict(v)
                    child[name] = values[index2]
                    if _key(child) not in seen:
                        queue.append(
                            (
                                child,
                                row["id"],
                                generation + 1,
                                "respond to "
                                + (
                                    ", ".join(failed)
                                    or "conditional pass: explore neighbouring mass/process alternatives"
                                ),
                            )
                        )
    feasible = [r for r in rows if r["conditional_feasible"]]
    # Retain at most two distinct geometries for native follow-through.
    selected = []
    for r in sorted(
        feasible,
        key=lambda r: (
            r["metrics"]["maximum_hook_equivalent_kg"],
            -min(
                r["metrics"]["minimum_transfer_compression_pa"],
                r["metrics"]["minimum_service_compression_pa"],
                r["metrics"]["minimum_handling_compression_pa"],
            ),
        ),
    ):
        if len(selected) < 2 and not any(
            _key(r["variables"])[:2] == _key(s["variables"])[:2] for s in selected
        ):
            selected.append(r)
    return dict(
        schema="osr-generative-civil-search/1",
        search_method="deterministic failure-prioritised breadth-first bounded neighbour search",
        candidate_budget=budget,
        candidate_count=len(rows),
        design_space=cfg,
        candidates=rows,
        selected_candidate_ids=[r["id"] for r in selected],
        conditional_feasible_count=len(feasible),
        termination=(
            "bounded_space_exhausted" if not queue else "candidate_budget_exhausted"
        ),
        diagnostic_load=dict(
            id="legacy-three-car-AW2-12-axle",
            accepted=False,
            reference_mass_to_force_g_m_s2=9.81,
            self_weight_g_m_s2=G,
            accepted_six_car_axle_loads_n=None,
        ),
        limitations=[
            "Search passes are conditional research screens only; unknown gates remain unknown and are excluded from conditional ranking",
            "41 railway stations; expanded handling stations include exact gravity moment extrema but fibre stresses remain sampled",
            "Gross uncracked prismatic concrete, simultaneous straight pretensioning and inherited research elastic/loss properties; no code/material resistance adoption",
            "Known mass excludes conventional reinforcement/attachments; 2 t rigging is a retained assumption",
            "New geometries and strand counts require new moulds, stressing bed, strongback and supplier integration; current native bed is not requalified",
        ],
        design_complete=False,
        physical_release=False,
    )


def native_model(candidate, span=25.0):
    cfg = _read(SPACE)
    if span not in cfg["span_pair_m"]:
        raise ValueError("native span outside declared Pi20/Pi25 pair")
    v = candidate["variables"]
    d = v["depth_m"]
    w = v["stem_width_m"]
    t = cfg["geometry"]["flange_thickness_m"]
    h = d - t
    b = cfg["geometry"]["deck_width_m"]
    parts = [part("flange", [span, b, t], [0, -b / 2, h])]
    for j, y in enumerate(cfg["geometry"]["stem_centres_y_m"]):
        parts.append(part(f"stem-{j}", [span, w, h], [0, y - w / 2, 0]))
    intervals = [
        (-b / 2, -0.7175 - w / 2),
        (-0.7175 + w / 2, 0.7175 - w / 2),
        (0.7175 + w / 2, b / 2),
    ]
    e = cfg["geometry"]["end_fill_length_m"]
    for k, x in enumerate((0, span - e)):
        for j, (lo, hi) in enumerate(intervals):
            parts.append(part(f"end-fill-{k}-{j}", [e, hi - lo, h], [x, lo, 0]))
    for j, p in enumerate(candidate["strand_points"]):
        dia = cfg["manufacturing"]["strand_envelope_diameter_m"]
        parts.append(
            part(
                f"strand-{j}",
                [dia, dia, span],
                [0, p["y_m"] - dia / 2, p["z_m"] - dia / 2],
                kind="cylinder",
                cylinder_axis="x",
                role="strand-envelope",
            )
        )
    return dict(
        id=candidate["id"] + f"-pi{span:g}",
        parts=parts,
        notes="Proposed beam geometry and overlapping strand clearance envelopes; concrete is gross, strand voids/rebar/insert/mould details not represented",
        physical_release=False,
    )


def write_artifacts(report, output: Path):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "search.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    artifacts = []
    for row in report["candidates"]:
        if row["id"] in report["selected_candidate_ids"]:
            folder = output / row["id"]
            folder.mkdir(exist_ok=True)
            path = folder / "model.json"
            path.write_text(
                json.dumps(native_model(row), indent=2, sort_keys=True) + "\n"
            )
            artifacts.append(dict(candidate_id=row["id"], span_m=25.0, model=str(path)))
    return artifacts
