"""Conditional return-bed support mechanics; no adopted ground or resistance.

One-axis rigid baseplate contact uses compression-only grout and tension-only
zero-preload anchors. Pad pressure is uniaxial compression-only equilibrium.
These local demand screens do not replace shell, anchorage or soil design.
"""

from __future__ import annotations

import math
import numpy as np

from engineering.factory_examples import models, development


def positive(value, name, *, zero=False):
    if (
        type(value) not in (int, float)
        or not math.isfinite(value)
        or value < 0
        or (not zero and value == 0)
    ):
        raise ValueError(
            "finite " + ("nonnegative " if zero else "positive ") + name + " required"
        )
    return value


def series(*values):
    if any(v is None for v in values):
        return None
    for v in values:
        positive(v, "series stiffness", zero=True)
    return 0.0 if 0 in values else 1 / math.fsum(1 / v for v in values)


def validate_basis(cfg):
    for key in (
        "anchor_proxy_diameter_m",
        "anchor_free_length_m",
        "anchor_hole_diameter_m",
        "washer_outer_diameter_m",
        "washer_thickness_m",
        "grout_thickness_m",
        "post_nominal_fillet_leg_m",
        "nominal_concrete_density_kg_m3",
        "grout_normal_spring_per_area_n_m3",
    ):
        positive(cfg[key], key)
    for key in ("baseplate_m", "pad_reservation_m", "nut_envelope_m"):
        if len(cfg[key]) != 3:
            raise ValueError("three support dimensions required")
        for v in cfg[key]:
            positive(v, key)
    b, d, _ = cfg["baseplate_m"]
    r = cfg["anchor_hole_diameter_m"] / 2
    if (
        cfg["anchor_proxy_diameter_m"] >= 2 * r
        or 2 * r >= cfg["washer_outer_diameter_m"]
    ):
        raise ValueError("positive nominal anchor/washer clearance required")
    if (
        len(cfg["anchor_xy_m"]) != 4
        or len({tuple(row) for row in cfg["anchor_xy_m"]}) != 4
    ):
        raise ValueError("four distinct anchor locations required")
    for x, y in cfg["anchor_xy_m"]:
        if (
            not math.isfinite(x)
            or not math.isfinite(y)
            or abs(x) + r >= b / 2
            or abs(y) + r >= d / 2
        ):
            raise ValueError("anchor clearance hole breaks plate edge")
    if len({row["id"] for row in cfg["interface_cases"]}) != len(
        cfg["interface_cases"]
    ):
        raise ValueError("unique restraint interface cases required")
    for row in cfg["interface_cases"]:
        if row["state"] not in {"unknown", "synthetic"}:
            raise ValueError(
                "unqualified or explicitly synthetic interface state required"
            )
        for key in (
            "lateral_connection_n_m",
            "lateral_ground_n_m",
            "ground_rotation_nm_rad",
            "vertical_connection_n_m",
            "vertical_ground_n_m",
        ):
            if row[key] is not None:
                positive(row[key], key, zero=True)


def contact(width, depth, anchor_xy, grout_k, anchor_k, force, moment, *, strips=96):
    """N positive downward; M is the first moment of compression about plate y.

    Displacement w(y)=u+theta*y is positive downward. Compression-only pressure
    is k_grout*max(w,0). Signed anchor reaction is k_anchor*min(w_anchor,0).
    """
    for name, value in (
        ("width", width),
        ("depth", depth),
        ("grout stiffness", grout_k),
        ("anchor stiffness", anchor_k),
    ):
        positive(value, name)
    if type(strips) is not int or not 8 <= strips <= 512:
        raise ValueError("8..512 contact strips required")
    if not math.isfinite(force) or not math.isfinite(moment) or not anchor_xy:
        raise ValueError("finite force/moment and anchors required")
    points = np.asarray(anchor_xy, dtype=float)
    if (
        points.ndim != 2
        or points.shape[1] != 2
        or not np.isfinite(points).all()
        or len({tuple(row) for row in points}) != len(points)
    ):
        raise ValueError("unique finite anchor coordinates required")
    if np.any(np.abs(points[:, 0]) >= width / 2) or np.any(
        np.abs(points[:, 1]) >= depth / 2
    ):
        raise ValueError("anchor must lie inside plate")
    y = (np.arange(strips) + 0.5) * depth / strips - depth / 2
    B = np.column_stack([np.ones(strips), y])
    A = np.column_stack([np.ones(len(points)), points[:, 1]])
    weight = width * depth / strips
    applied = np.array([force, moment])
    displacement = np.linalg.solve(grout_k * weight * B.T @ B, applied)

    def state(u):
        wc, wa = B @ u, A @ u
        reactions = grout_k * weight * np.maximum(wc, 0)
        anchors = anchor_k * np.minimum(wa, 0)
        residual = B.T @ reactions + A.T @ anchors - applied
        tangent = (
            grout_k * weight * B[wc >= 0].T @ B[wc >= 0]
            + anchor_k * A[wa < 0].T @ A[wa < 0]
        )
        energy = (
            0.5 * grout_k * weight * np.maximum(wc, 0) @ np.maximum(wc, 0)
            + 0.5 * anchor_k * np.minimum(wa, 0) @ np.minimum(wa, 0)
            - applied @ u
        )
        return residual, tangent, energy, reactions, anchors

    scale = max(1, abs(force), abs(moment))
    for iteration in range(80):
        residual, tangent, energy, reactions, anchors = state(displacement)
        if np.linalg.norm(residual, ord=np.inf) <= scale * 1e-9:
            break
        try:
            step = np.linalg.solve(tangent, -residual)
        except np.linalg.LinAlgError as error:
            raise ValueError("unrestrained baseplate contact tangent") from error
        factor = 1.0
        while factor > 2**-30:
            trial = displacement + factor * step
            if (
                state(trial)[2]
                <= energy + 1e-4 * factor * residual @ step + scale * 1e-15
            ):
                displacement = trial
                break
            factor /= 2
        else:
            raise ValueError("baseplate contact line search did not converge")
    else:
        raise ValueError("baseplate contact did not converge")
    residual, tangent, _, reactions, anchors = state(displacement)
    condensed_rotation = tangent[1, 1] - tangent[1, 0] * tangent[0, 1] / tangent[0, 0]
    condensed_vertical = tangent[0, 0] - tangent[0, 1] * tangent[1, 0] / tangent[1, 1]
    return dict(
        downward_translation_m=float(displacement[0]),
        rotation_rad=float(displacement[1]),
        anchor_tensions_n=(-anchors).tolist(),
        contact_compression_n=float(sum(reactions)),
        contact_area_fraction=float(np.count_nonzero(reactions > 0) / strips),
        maximum_sampled_contact_pressure_pa=float(max(reactions) / weight),
        force_residual_n=float(residual[0]),
        moment_residual_nm=float(residual[1]),
        condensed_rotation_nm_rad=float(condensed_rotation),
        condensed_vertical_n_m=float(condensed_vertical),
        iterations=iteration + 1,
        anchor_preload_n=0,
        resistance_qualified=False,
    )


def pad_pressure(width, depth, compression, moment):
    compression, moment = float(compression), float(moment)
    for name, value in (("pad width", width), ("pad depth", depth)):
        positive(value, name)
    if not math.isfinite(compression) or not math.isfinite(moment):
        raise ValueError("finite pad actions required")
    if compression <= 0 or abs(moment) >= compression * depth / 2:
        return dict(
            compression_equilibrium=False,
            contact_length_m=None,
            maximum_pressure_pa=None,
            minimum_pressure_pa=None,
        )
    eccentricity = abs(moment) / compression
    full = eccentricity <= depth / 6
    length = depth if full else 3 * (depth / 2 - eccentricity)
    maximum = (
        compression / (width * depth) * (1 + 6 * eccentricity / depth)
        if full
        else 2 * compression / (width * length)
    )
    return dict(
        compression_equilibrium=True,
        full_contact=full,
        eccentricity_m=eccentricity,
        contact_length_m=length,
        maximum_pressure_pa=maximum,
        minimum_pressure_pa=(
            compression / (width * depth) * (1 - 6 * eccentricity / depth)
            if full
            else 0.0
        ),
        bearing_resistance_pa=None,
        sliding_resistance_n=None,
    )


def weld_group(width, leg, axial, moment, shear):
    """Nominal external square fillet line, no returns/gaps or strength credit."""
    positive(width, "weld-group width")
    positive(leg, "nominal fillet leg")
    if not all(math.isfinite(v) for v in (axial, moment, shear)):
        raise ValueError("finite weld actions required")
    throat = leg / math.sqrt(2)
    area = 4 * width * throat
    inertia = 2 * width**3 * throat / 3
    normal = max(
        abs(axial / area + moment * width / 2 / inertia),
        abs(axial / area - moment * width / 2 / inertia),
    )
    tau = abs(shear) / area
    return dict(
        throat_m=throat,
        throat_area_m2=area,
        line_inertia_m4=inertia,
        maximum_normal_demand_pa=normal,
        average_shear_demand_pa=tau,
        nominal_combined_demand_pa=math.sqrt(normal**2 + 3 * tau**2),
        resistance_pa=None,
        wps_qualified=False,
        native_fillet_geometry_modelled=False,
    )


def support_parts(cfg, strongback_cfg):
    """Two first-station baseplate concepts; remaining fourteen pads unmodelled."""
    validate_basis(cfg)
    parts = []
    b, d, t = cfg["baseplate_m"]
    px, py, pz = cfg["pad_reservation_m"]
    grout = cfg["grout_thickness_m"]
    x = strongback_cfg["restraint_station_m"]
    for side, y in enumerate((-1.85, 1.85)):
        prefix = f"support-{side}"
        holes = [
            dict(
                x_m=ax + b / 2, y_m=ay + d / 2, diameter_m=cfg["anchor_hole_diameter_m"]
            )
            for ax, ay in cfg["anchor_xy_m"]
        ]
        parts.append(
            models.part(
                prefix + "-baseplate",
                [b, d, t],
                [x - b / 2, y - d / 2, -t],
                holes=holes,
                role="support-baseplate-steel",
            )
        )
        parts.append(
            models.part(
                prefix + "-grout",
                [b, d, grout],
                [x - b / 2, y - d / 2, -t - grout],
                role="grout-reservation",
            )
        )
        parts.append(
            models.part(
                prefix + "-pad",
                [px, py, pz],
                [x - px / 2, y - py / 2, -t - grout - pz],
                role="foundation-reservation",
            )
        )
        for index, (ax, ay) in enumerate(cfg["anchor_xy_m"]):
            dia = cfg["anchor_proxy_diameter_m"]
            length = cfg["anchor_free_length_m"]
            parts.append(
                models.part(
                    prefix + f"-anchor-{index}",
                    [dia, dia, length],
                    [x + ax - dia / 2, y + ay - dia / 2, 0.05 - length],
                    kind="cylinder",
                    role="anchor-thread-envelope",
                )
            )
            diameter = cfg["washer_outer_diameter_m"]
            parts.append(
                models.part(
                    prefix + f"-washer-{index}",
                    [diameter, diameter, cfg["washer_thickness_m"]],
                    [x + ax - diameter / 2, y + ay - diameter / 2, 0],
                    kind="cylinder",
                    holes=[
                        dict(
                            x_m=diameter / 2,
                            y_m=diameter / 2,
                            diameter_m=cfg["anchor_hole_diameter_m"],
                        )
                    ],
                    role="support-washer-steel",
                )
            )
            nx, ny, nz = cfg["nut_envelope_m"]
            parts.append(
                models.part(
                    prefix + f"-nut-{index}",
                    [nx, ny, nz],
                    [x + ax - nx / 2, y + ay - ny / 2, cfg["washer_thickness_m"]],
                    role="supplier-nut-envelope",
                )
            )
    return parts


def assess(a, bed, section, strongback, values, cfg):
    """Final-force imperfection cases, signs combined at matching stations only."""
    validate_basis(cfg)
    Lpost = strongback["post_length_m"]
    # Geometry comes from the same strongback section represented by the caller.
    B, wall = cfg["post_outer_m"], cfg["post_wall_m"]
    E = a["steel_elastic_modulus_pa"]
    area = B**2 - (B - 2 * wall) ** 2
    inertia = (B**4 - (B - 2 * wall) ** 4) / 12
    post_lateral = 3 * E * inertia / Lpost**3
    post_vertical = E * area / Lpost
    b, d, thickness = cfg["baseplate_m"]
    anchor_k = (
        E
        * math.pi
        * cfg["anchor_proxy_diameter_m"] ** 2
        / 4
        / cfg["anchor_free_length_m"]
    )
    dead_n = (
        (
            area * Lpost
            + b * d * thickness
            - len(cfg["anchor_xy_m"])
            * math.pi
            * cfg["anchor_hole_diameter_m"] ** 2
            / 4
            * thickness
        )
        * a["steel_density_kg_m3"]
        * 9.80665
    )
    pad_mass = (
        math.prod(cfg["pad_reservation_m"]) * cfg["nominal_concrete_density_kg_m3"]
    )
    H, width, t = [v / 1000 for v in section["side_box_mm"]]
    inertias = dict(
        lateral=section["weak_inertia_m4"],
        vertical=(width * H**3 - (width - 2 * t) * (H - 2 * t) ** 3) / 12,
    )
    stations = [x - bed["origin_x_m"] for x in bed["brace_stations_m"]]
    P = strongback["force_per_strand_n"] * len(
        strongback["points"]
    )  # one half of the strand field
    force_maps = {}
    for plane in ("lateral", "vertical"):
        k = values[plane + "_spring_n_m"]
        response = development.imperfect_column(
            bed["active_length_m"],
            E,
            inertias[plane],
            bed["elements"],
            [(x, k) for x in stations],
            P,
            bed["initial_sway_m"],
        )
        force_maps[plane] = response
    valid = all(v["stable_elastic_tangent"] for v in force_maps.values())
    cases = []
    if valid:
        for lateral, vertical in zip(
            force_maps["lateral"]["brace_reactions"],
            force_maps["vertical"]["brace_reactions"],
            strict=True,
        ):
            if lateral["x_m"] != vertical["x_m"]:
                raise ValueError("restraint load cases must share actual stations")
            for sy in (-1, 1):
                for sz in (-1, 1):
                    Fy, Fz = float(sy * lateral["force_n"]), float(
                        sz * vertical["force_n"]
                    )
                    N, M = dead_n - Fz, Fy * Lpost
                    plate = contact(
                        b,
                        d,
                        cfg["anchor_xy_m"],
                        cfg["grout_normal_spring_per_area_n_m3"],
                        anchor_k,
                        N,
                        M,
                        strips=cfg["contact_strips"],
                    )
                    ground_moment = Fy * (
                        Lpost
                        + thickness
                        + cfg["grout_thickness_m"]
                        + cfg["pad_reservation_m"][2]
                    )
                    pad = pad_pressure(
                        cfg["pad_reservation_m"][0],
                        cfg["pad_reservation_m"][1],
                        N + pad_mass * 9.80665,
                        ground_moment,
                    )
                    cases.append(
                        dict(
                            global_x_m=bed["origin_x_m"] + lateral["x_m"],
                            lateral_sign=sy,
                            vertical_sign=sz,
                            lateral_force_n=Fy,
                            vertical_upward_force_n=Fz,
                            post_downward_force_n=N,
                            post_base_moment_nm=M,
                            nominal_post_normal_extreme_pa=max(
                                abs(N / area + M * B / 2 / inertia),
                                abs(N / area - M * B / 2 / inertia),
                            ),
                            nominal_post_average_shear_pa=abs(Fy) / area,
                            baseplate=plate,
                            post_base_weld=weld_group(
                                B, cfg["post_nominal_fillet_leg_m"], N, M, Fy
                            ),
                            pad=pad,
                        )
                    )
    min_rotation = min(
        (c["baseplate"]["condensed_rotation_nm_rad"] for c in cases), default=None
    )
    min_vertical = min(
        (c["baseplate"]["condensed_vertical_n_m"] for c in cases), default=None
    )
    interfaces = []
    for inputs in cfg["interface_cases"]:
        pads_equilibrate = (
            all(c["pad"]["compression_equilibrium"] for c in cases) if cases else False
        )
        known = inputs["state"] == "synthetic" and valid and pads_equilibrate
        ky = (
            series(
                post_lateral,
                inputs["lateral_connection_n_m"],
                inputs["lateral_ground_n_m"],
                (
                    None
                    if inputs["ground_rotation_nm_rad"] is None
                    else inputs["ground_rotation_nm_rad"] / Lpost**2
                ),
                None if min_rotation is None else min_rotation / Lpost**2,
            )
            if known
            else None
        )
        kz = (
            series(
                post_vertical,
                inputs["vertical_connection_n_m"],
                inputs["vertical_ground_n_m"],
                min_vertical,
            )
            if known
            else None
        )
        row = dict(
            id=inputs["id"],
            state=inputs["state"],
            pad_compression_equilibrium=pads_equilibrate,
            effective_lateral_n_m=ky,
            effective_vertical_n_m=kz,
            lateral_requirement_met=(
                None if ky is None else ky >= values["lateral_spring_n_m"]
            ),
            vertical_requirement_met=(
                None if kz is None else kz >= values["vertical_spring_n_m"]
            ),
            feedback="One conservative tangent sensitivity using the minimum local tangent over selected ideal-spring cases; not a self-consistent nonlinear soil/rail iteration",
        )
        for plane, k in (("lateral", ky), ("vertical", kz)):
            row[plane + "_elastic_load_factor"] = (
                None
                if k is None
                else development.column_buckling(
                    bed["active_length_m"],
                    E,
                    inertias[plane],
                    bed["elements"],
                    [(x, k) for x in stations],
                )
                / P
            )
        interfaces.append(row)
    return dict(
        schema="osr-factory-restraint-assessment/1",
        basis=cfg,
        selected_lateral_requirement_n_m=values["lateral_spring_n_m"],
        selected_vertical_requirement_n_m=values["vertical_spring_n_m"],
        per_side_axial_force_n=P,
        post_and_baseplate_dead_force_n=dead_n,
        pad_selfweight_n=pad_mass * 9.80665,
        ideal_both_planes_stable=valid,
        cases=cases,
        post_lateral_stiffness_n_m=post_lateral,
        post_vertical_stiffness_n_m=post_vertical,
        interface_cases=interfaces,
        maximum_anchor_tension_n=max(
            (max(c["baseplate"]["anchor_tensions_n"]) for c in cases), default=None
        ),
        maximum_post_normal_demand_pa=max(
            (c["nominal_post_normal_extreme_pa"] for c in cases), default=None
        ),
        actual_effective_lateral_n_m=None,
        actual_effective_vertical_n_m=None,
        foundation_connections_qualified=False,
        limitations=[
            "Rigid baseplate and nominal gross-bar springs omit plate flexibility, thread roots, bond/embedment, preload, prying and concrete failure",
            "Gross rectangular grout contact ignores anchor-hole exclusion; nominal weld-line demands omit access, corner/gap effects, stiffness and resistance",
            "Post load is final initial-force rail imperfection response; strongback stressing/release torsion, rail selfweight and operating loads need separate combined stages",
            "Two independent bow signs are combined at each matching station; maxima from different stations are not combined",
            "Pad pressure is a static uniaxial equilibrium demand, not soil resistance, sliding, settlement, reinforcement or anchor design",
            "Actual site, grout, connection and anchor stiffness/resistance are unmeasured; hypothetical interface sensitivity cannot qualify ground springs",
        ],
        physical_release=False,
    )


def machining_cases(cfg, machine, density):
    """Fixed anchor layout; a smaller plate is not automatically a viable part."""
    rows = []
    for width in (0.35, cfg["baseplate_m"][0]):
        depth = width
        thickness = cfg["baseplate_m"][2]
        edge = min(
            min(width / 2 - abs(x), depth / 2 - abs(y))
            - cfg["anchor_hole_diameter_m"] / 2
            for x, y in cfg["anchor_xy_m"]
        )
        mass = (
            (
                width * depth
                - len(cfg["anchor_xy_m"])
                * math.pi
                * cfg["anchor_hole_diameter_m"] ** 2
                / 4
            )
            * thickness
            * density
        )
        rows.append(
            dict(
                width_m=width,
                depth_m=depth,
                thickness_m=thickness,
                fixed_anchor_hole_edge_clearance_m=edge,
                geometric_edge_screen=edge > 0,
                nominal_steel_mass_kg=mass,
                pilot_cv5_diameter_screen=math.hypot(width, depth)
                <= machine["workpiece_diameter_m"],
                pilot_cv5_mass_screen=mass <= machine["workpiece_kg"],
                pilot_cv5_height_screen=thickness <= machine["workpiece_height_m"],
                workholding_and_tool_access_accepted=False,
            )
        )
    return rows
