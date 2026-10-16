"""Gross Pi-beam diagnostic railway and handling demands; no load/resistance adoption."""

from __future__ import annotations

import math
import numpy as np
from engineering.factory_examples import development, models

G = 9.80665


def validate(span, offsets, forces, segments):
    if (
        not math.isfinite(span)
        or span <= 0
        or not 1 <= len(offsets) == len(forces) <= 64
    ):
        raise ValueError("bounded nonempty moving axle definition required")
    if any(not math.isfinite(x) for x in offsets) or any(
        not math.isfinite(p) or p <= 0 for p in forces
    ):
        raise ValueError("finite axle offsets and positive forces required")
    if len(set(offsets)) != len(offsets):
        raise ValueError("distinct axle offsets required")
    for a, b, q in segments:
        if not 0 <= a < b <= span or not math.isfinite(q) or q < 0:
            raise ValueError("finite nonnegative distributed load within beam required")


def distributed_resultants(segments):
    return math.fsum((b - a) * q for a, b, q in segments), math.fsum(
        (b - a) * q * (a + b) / 2 for a, b, q in segments
    )


def gravity_moment(x, segments, reaction):
    return reaction * x - math.fsum(
        q / 2 * (max(x - a, 0) ** 2 - max(x - b, 0) ** 2) for a, b, q in segments
    )


def train_at(span, nose, offsets, forces):
    return [
        (max(0, min(span, nose + d)), p)
        for d, p in zip(offsets, forces)
        if -1e-10 <= nose + d <= span + 1e-10
    ]


def moment_at(span, x, nose, offsets, forces, segments):
    active = train_at(span, nose, offsets, forces)
    W, first = distributed_resultants(segments)
    left = W - first / span + math.fsum(p * (span - a) / span for a, p in active)
    return gravity_moment(x, segments, left) - math.fsum(
        p * max(x - a, 0) for a, p in active
    )


def continuous_peak(span, offsets, forces, segments):
    """Exact piecewise-quadratic global sagging peak for nonnegative loads.

    At a fixed section the live influence is piecewise linear in train origin;
    its maximum is attained at axle entry, exit or an axle under that section.
    On each resulting x interval total moment is quadratic. Evaluate endpoints
    and any interior vertex rather than assuming a fixed position grid is exact.
    """
    validate(span, offsets, forces, segments)
    gravity_knots = [a for a, b, q in segments] + [b for a, b, q in segments]
    branches = [
        ("fixed", t)
        for t in sorted(set([-d for d in offsets] + [span - d for d in offsets]))
    ]
    branches += [("under", d) for d in offsets]
    peak = dict(moment_nm=0.0, x_m=0.0, train_origin_m=-max(offsets), branch=None)
    evaluated = 0
    for kind, t in branches:
        if kind == "fixed":
            knots = [t + d for d in offsets]
        else:
            knots = [t - d for d in offsets] + [span + t - d for d in offsets]
        knots = sorted(
            set([0.0, span] + [max(0.0, min(span, x)) for x in knots + gravity_knots])
        )

        def retain(x):
            nonlocal evaluated, peak
            origin = t if kind == "fixed" else x - t
            value = moment_at(span, x, origin, offsets, forces, segments)
            evaluated += 1
            if value > peak["moment_nm"]:
                peak = dict(moment_nm=value, x_m=x, train_origin_m=origin, branch=kind)
            return value

        for lo, hi in zip(knots, knots[1:]):
            if hi - lo < 1e-9:
                continue
            mid = (lo + hi) / 2
            fl, fm, fr = retain(lo), retain(mid), retain(hi)
            quadratic = 2 * (fl + fr - 2 * fm) / (hi - lo) ** 2
            if quadratic < -1e-8:
                vertex = mid - (fr - fl) / (hi - lo) / (2 * quadratic)
                if lo < vertex < hi:
                    retain(vertex)
    peak.update(
        evaluations=evaluated,
        method="entry/exit/under-axle branches with quadratic stationary points",
    )
    return peak


def section_envelope(span, stations, offsets, forces, segments):
    validate(span, offsets, forces, segments)
    rows = []
    events = [-d for d in offsets] + [span - d for d in offsets]
    W, first = distributed_resultants(segments)
    dead_left = W - first / span
    for x in stations:
        if not 0 <= x <= span:
            raise ValueError("section outside beam")
        origins = events + [x - d for d in offsets]
        values = [moment_at(span, x, t, offsets, forces, segments) for t in origins]
        k = max(range(len(values)), key=values.__getitem__)
        dead = gravity_moment(x, segments, dead_left)
        rows.append(
            dict(
                x_m=x,
                dead_moment_nm=dead,
                maximum_total_moment_nm=values[k],
                maximum_live_moment_nm=values[k] - dead,
                governing_origin_m=origins[k],
            )
        )
    supports = []
    for nose in events:
        active = train_at(span, nose, offsets, forces)
        supports.append(
            (
                dead_left + math.fsum(p * (span - a) / span for a, p in active),
                first / span + math.fsum(p * a / span for a, p in active),
                nose,
            )
        )
    return dict(
        stations=rows,
        maximum_total_reaction_n=max(max(l, r) for l, r, t in supports),
        continuous_peak=continuous_peak(span, offsets, forces, segments),
    )


def handling(span, segments, fraction, factor, rigging_mass, lower_angle, upper_angle):
    if (
        not 0.1 <= fraction <= 0.3
        or factor < 1
        or rigging_mass < 0
        or not 0 <= lower_angle < 60
        or not 0 < upper_angle < 60
    ):
        raise ValueError("bounded declared lifting geometry and load factors required")
    if not all(
        math.isfinite(v)
        for v in [fraction, factor, rigging_mass, lower_angle, upper_angle]
    ):
        raise ValueError("finite handling hypotheses required")
    W, first = distributed_resultants(segments)
    a, b = fraction * span, (1 - fraction) * span
    right = (first - W * a) / (b - a)
    left = W - right
    if min(left, right) <= 0:
        raise ValueError("positive lifting-station reactions required")

    def moment(x):
        return (
            left * max(x - a, 0)
            + right * max(x - b, 0)
            - math.fsum(
                q / 2 * (max(x - u, 0) ** 2 - max(x - v, 0) ** 2)
                for u, v, q in segments
            )
        )

    knots = sorted(
        set([0, span, a, b] + [u for u, v, q in segments] + [v for u, v, q in segments])
    )
    points = list(knots)
    for lo, hi in zip(knots, knots[1:]):
        mid = (lo + hi) / 2
        q = sum(q for u, v, q in segments if u < mid < v)
        shear = (
            (left if mid > a else 0)
            + (right if mid > b else 0)
            - sum(q * max(0, min(mid, v) - u) for u, v, q in segments)
        )
        if q > 0 and lo < mid + shear / q < hi:
            points.append(mid + shear / q)
    nominal_mass = W / G
    hook = (nominal_mass + rigging_mass) * G * factor
    theta = math.radians(lower_angle)
    alpha = math.radians(upper_angle)
    station_span = b - a
    return dict(
        support_x_m=[a, b],
        longitudinal_rig_span_m=station_span,
        transverse_lift_point_separation_m=1.435,
        known_beam_mass_kg=nominal_mass,
        beam_dynamic_factor=factor,
        rigging_mass_assumption_kg=rigging_mass,
        beam_dynamic_weight_n=W * factor,
        hook_equivalent_load_n=hook,
        station_vertical_reactions_n=[left * factor, right * factor],
        minimum_bending_moment_nm=min(moment(x) for x in points) * factor,
        maximum_bending_moment_nm=max(moment(x) for x in points) * factor,
        diagram=[
            dict(x_m=float(x), moment_nm=moment(float(x)) * factor)
            for x in sorted(set(points + np.linspace(0, span, 101).tolist()))
        ],
        lower_sling_angle_from_vertical_deg=lower_angle,
        nominal_equalized_leg_tension_n=W * factor / (4 * math.cos(theta)),
        two_effective_leg_tension_n=W * factor / (2 * math.cos(theta)),
        nominal_equalized_insert_horizontal_force_n=W * factor / 4 * math.tan(theta),
        upper_sling_angle_from_vertical_deg=upper_angle,
        upper_leg_tension_n=hook / (2 * math.cos(alpha)),
        spreader_axial_compression_n=hook / 2 * math.tan(alpha),
        geometric_headroom_above_longitudinal_end_units_m=station_span
        / (2 * math.tan(alpha)),
        complete_rig_mass_kg=None,
        insert_resistance_n=None,
        distribution_accepted=False,
        physical_release=False,
    )


def assess(a, section, candidate, beam, trace, values, basis):
    if (
        basis.get("schema") != "osr-factory-beam-demands/1"
        or basis.get("state") != "synthetic"
    ):
        raise ValueError("explicit beam demand research basis required")
    reference = trace["reference"]
    axles = reference["axle_pattern"]
    if (
        reference["body_count"] != 3
        or reference["axle_count"] != 12
        or len(axles) != 12
    ):
        raise ValueError("retained legacy three-car diagnostic identity changed")
    offsets = [r["x_m"] - axles[0]["x_m"] for r in axles]
    if len({r["id"] for r in axles}) != 12 or not math.isclose(
        math.fsum(r["static_load_kn"] * 1000 / 9.81 for r in axles),
        reference["total_mass_kg"],
        rel_tol=1e-10,
    ):
        raise ValueError("legacy diagnostic axle identity/mass balance differs")
    forces = [
        r["static_load_kn"] * 1000 * values["diagnostic_axle_multiplier"] for r in axles
    ]
    L = values["span_m"]
    count = candidate["strands"]
    A = section["area_m2"]
    I = section["inertia_x_m4"]
    zc = section["centroid_z_m"]
    depth = section["depth_m"]
    q = (
        A * models.pi.CONCRETE_DENSITY_KG_PER_M3
        + count
        * a["strand_area_m2"]
        * (a["steel_density_kg_m3"] - models.pi.CONCRETE_DENSITY_KG_PER_M3)
    ) * G
    patch = (2.9 - 2 * 0.3) * 0.935 * models.pi.CONCRETE_DENSITY_KG_PER_M3 * G
    segments = [(0, L, q), (0, 0.55, patch), (L - 0.55, L, patch)]
    station_x = [r["x_m"] for r in beam["stations"]]
    rail = section_envelope(L, station_x, offsets, forces, segments)
    for row, old in zip(rail["stations"], beam["stations"], strict=True):
        if not math.isclose(
            row["dead_moment_nm"], old["gravity_moment_nm"], abs_tol=1e-6
        ):
            raise ValueError("railway and retained beam gravity definitions differ")
        service = old["service_dead_only"]
        # Retain the same local dead-load shortening/loss hypothesis. Only the
        # additional live bending is superposed; no new loss or transfer credit.
        row["top_maximum_compression_pa"] = (
            service["top_pa"] + row["maximum_live_moment_nm"] * (depth - zc) / I
        )
        # Positive downward axle loading increases top compression. Its minimum
        # over a complete passage therefore occurs with the train off the span.
        row["top_compression_pa"] = service["top_pa"]
        row["soffit_compression_pa"] = (
            service["soffit_pa"] - row["maximum_live_moment_nm"] * zc / I
        )
    lift = handling(
        L,
        segments,
        values["lifting_station_fraction"],
        a["lifting_dynamic_factor"],
        a["rigging_mass_kg"],
        math.degrees(values["lower_sling_angle_rad"]),
        basis["upper_sling_angle_from_vertical_deg"],
    )
    if not math.isclose(
        lift["known_beam_mass_kg"],
        beam["known_concrete_plus_strand_mass_kg"],
        abs_tol=1e-7,
    ):
        raise ValueError("handling and retained beam mass definitions differ")
    minimum = min(
        r[k]
        for r in rail["stations"]
        for k in ["top_compression_pa", "soffit_compression_pa"]
    )
    return dict(
        schema="osr-factory-beam-demand-study/1",
        basis=basis,
        span_m=L,
        prestress_id=candidate["id"],
        diagnostic_load_case=dict(
            id="legacy-lm3-aw2-3car-12axle",
            body_count=3,
            axle_count=12,
            loading=reference["loading"],
            reference_total_mass_kg=reference["total_mass_kg"],
            reference_mass_to_force_g_m_s2=9.81,
            axle_multiplier=values["diagnostic_axle_multiplier"],
            source="engineering/industrialisation/vehicle-civil-load-trace.json",
            accepted=False,
            current_six_car_axle_loads_n=None,
        ),
        railway=rail,
        minimum_sampled_service_compression_pa=minimum,
        zero_tension_diagnostic_screen=minimum >= 0,
        handling=lift,
        concrete_compression_limit_pa=None,
        concrete_tension_limit_pa=None,
        railway_loading_accepted=False,
        physical_release=False,
        limitations=[
            "The diagnostic uses the retained three-car planning reference, not an accepted six-car Baghdad loading. Multiplier is an OSR sensitivity, not a code dynamic factor",
            "Gross prismatic uncracked section, full-force straight tendons and retained local loss hypothesis. Transmission/end zones, compression limits, reinforcement, shear/torsion/fatigue, nonlinear response and railway dynamic interaction remain open",
            "Moving moment/reaction events and continuous sagging peak cover one-dimensional downward axle loads. Fibre stress extrema are sampled at the declared stations; no continuous stress or deflection envelope is claimed",
            "Handling overhang bending and symmetric leg-force hypotheses omit tilt, unequal sharing, local inserts, breakout, transverse torsion, transport, suction and wind. Additional reinforcement/attachments and complete rig mass remain unknown",
            "One long spreader plus two transverse distributors is an enquiry concept. Capacity depends on span, sling angles, component configuration and supplier approval; headline model capacity cannot select the rig",
        ],
    )
