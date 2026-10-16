"""Fabrication iteration: grip fit, staged strongback actions and pin retention.

All geometry and demand screens remain preliminary and physically unreleased.
"""

from __future__ import annotations

import math
from copy import deepcopy

from .models import part, volume, point_beam, positive, bounds


def strands(layout, pitch):
    result = []
    for row, (z, count) in enumerate(layout["rows"]):
        if count % 2:
            raise ValueError("symmetric strand pairs required")
        each = count // 2
        for j in range(each):
            y = 0.7175 + (j - (each - 1) / 2) * pitch
            result.append(dict(id=f"pair-{row}-{j}", z_m=0.8 + z, y_m=y))
    return result


def grip_fit(points, diameter, clearance):
    centres = [(sign * p["y_m"], p["z_m"]) for p in points for sign in (-1, 1)]
    gaps = [
        math.hypot(a[0] - b[0], a[1] - b[1]) - diameter
        for j, a in enumerate(centres)
        for b in centres[j + 1 :]
    ]
    return dict(
        strand_count=len(centres),
        minimum_surface_gap_m=min(gaps),
        required_gap_m=clearance,
        geometric_clearance_screen=min(gaps) >= clearance - 1e-10,
        exact_strand_grip_compatibility=None,
    )


def stressing_sequence(points, force_each, axis_z, *, balanced):
    pending = deepcopy(points)
    chosen = []
    torque = 0
    while pending:
        i = (
            min(
                range(len(pending)),
                key=lambda j: (
                    abs(torque + 2 * force_each * (pending[j]["z_m"] - axis_z)),
                    pending[j]["id"],
                ),
            )
            if balanced
            else 0
        )
        p = pending.pop(i)
        chosen.append(p)
        torque += 2 * force_each * (p["z_m"] - axis_z)
    stages = []
    applied = []
    for pair in chosen:
        # Both half-pair stages retained for a single-jack sequence.
        for sign in (-1, 1):
            applied.append((sign * pair["y_m"] + 1.85, force_each))
            transverse = point_beam(3.7, applied, 210e9, 1, samples=41)
            couple = sum(
                f * (p["z_m"] - axis_z)
                for p in chosen[: len(applied) // 2]
                for f in [2 * force_each]
            )
            if len(applied) % 2:
                couple += force_each * (pair["z_m"] - axis_z)
            stages.append(
                dict(
                    stage=len(applied),
                    strand=pair["id"] + f"-side-{sign}",
                    strand_y_m=sign * pair["y_m"],
                    strand_z_m=pair["z_m"],
                    force_per_strand_n=force_each,
                    total_stressing_force_n=len(applied) * force_each,
                    end_vertical_couple_nm=couple,
                    return_reactions_n=[
                        transverse["left_reaction_n"],
                        transverse["right_reaction_n"],
                    ],
                    transverse_moment_nm=transverse["maximum_abs_moment_nm"],
                )
            )
    return dict(
        stages=stages,
        maximum_abs_end_couple_nm=max(abs(s["end_vertical_couple_nm"]) for s in stages),
        final_end_couple_nm=stages[-1]["end_vertical_couple_nm"],
        simultaneous_pair_stressing_assumed=False,
        sequence_qualified=False,
    )


def strongback(a, cfg, candidate, grip):
    for key, value in cfg.items():
        if value is not None:
            positive(value, key)
    if cfg["front_hole_diameter_m"] >= grip["published"]["diameter_m"]:
        raise ValueError("grip body must bear outside clearance hole")
    if cfg["wall_m"] >= min(cfg["box_depth_x_m"], cfg["box_height_z_m"]) / 2:
        raise ValueError("positive strongback box cavity required")
    pts = strands(candidate, cfg["strand_pitch_m"])
    baseline = strands(candidate, cfg["baseline_pitch_m"])
    axis = sum(p["z_m"] for p in pts) / len(pts)
    grip_radius = grip["published"]["diameter_m"] / 2

    def edge_clearance(height):
        return min(
            min(
                cfg["box_length_y_m"] / 2 - abs(p["y_m"]) - grip_radius,
                p["z_m"] - (axis - height / 2) - grip_radius,
                axis + height / 2 - p["z_m"] - grip_radius,
            )
            for p in pts
        )

    f = a["strand_area_m2"] * a["strand_initial_stress_pa"]
    sequences = {
        "lower_first": stressing_sequence(pts, f, axis, balanced=False),
        "balanced_pairs": stressing_sequence(pts, f, axis, balanced=True),
    }
    d, h, t = cfg["box_depth_x_m"], cfg["box_height_z_m"], cfg["wall_m"]
    iz = (h * d**3 - (h - 2 * t) * (d - 2 * t) ** 3) / 12
    median = (d - t) * (h - t)
    area = d * h - (d - 2 * t) * (h - 2 * t)
    maximum = max(
        s["transverse_moment_nm"] for s in sequences["balanced_pairs"]["stages"]
    )
    stress = maximum * d / 2 / iz
    # Individual-stage nominal combination; not a steel-code resistance check.
    combinations = []
    for stage in sequences["balanced_pairs"]["stages"]:
        normal = stage["transverse_moment_nm"] * d / 2 / iz
        torsion = abs(stage["end_vertical_couple_nm"]) / (2 * median * t)
        shear = max(stage["return_reactions_n"]) / (2 * t * (d - 2 * t))
        combinations.append(math.sqrt(normal**2 + 3 * (shear + torsion) ** 2))
    # Raise return rails to the initial tendon centroid; posts still need real base restraint.
    post_length = axis - 0.25
    B, wall = cfg["post_outer_m"], cfg["post_wall_m"]
    post_I = (B**4 - (B - 2 * wall) ** 4) / 12
    post_k = 3 * a["steel_elastic_modulus_pa"] * post_I / post_length**3
    req = cfg["proposed_ground_spring_n_m"]
    compliance_budget = 1 / req - 1 / post_k
    if compliance_budget <= 0:
        foundation_req = None
    else:
        foundation_req = 1 / compliance_budget
    cover = (
        0.15
        - max(abs(p["y_m"] - 0.7175) for p in pts)
        - cfg["strand_clearance_envelope_diameter_m"] / 2
    )
    support_compliance = [
        post_k,
        cfg["ground_translation_n_m"],
        cfg["connection_translation_n_m"],
    ]
    known = (
        all(v is not None and v > 0 for v in support_compliance)
        and cfg["base_rotation_nm_rad"] is not None
        and cfg["base_rotation_nm_rad"] > 0
    )
    effective = (
        1
        / (
            sum(1 / v for v in support_compliance)
            + post_length**2 / cfg["base_rotation_nm_rad"]
        )
        if known
        else None
    )
    bearing_area = (
        math.pi
        / 4
        * (grip["published"]["diameter_m"] ** 2 - cfg["front_hole_diameter_m"] ** 2)
    )
    return dict(
        axis_z_m=axis,
        grip_outer_diameter_m=grip["published"]["diameter_m"],
        grip_body_length_m=grip["published"]["length_m"],
        points=pts,
        force_per_strand_n=f,
        baseline_grip_fit=grip_fit(
            baseline, grip["published"]["diameter_m"], cfg["grip_clearance_m"]
        ),
        revised_grip_fit=grip_fit(
            pts, grip["published"]["diameter_m"], cfg["grip_clearance_m"]
        ),
        baseline_plate_grip_edge_clearance_m=edge_clearance(
            cfg["baseline_box_height_m"]
        ),
        revised_plate_grip_edge_clearance_m=edge_clearance(cfg["box_height_z_m"]),
        nominal_stem_side_cover_m=cover,
        research_cover_screen=cover >= cfg["minimum_cover_research_m"],
        sequences=sequences,
        box_area_m2=area,
        box_in_plane_inertia_m4=iz,
        nominal_in_plane_bending_demand_pa=stress,
        maximum_stage_nominal_von_mises_demand_pa=max(combinations),
        grip_annular_bearing_demand_pa=f / bearing_area,
        bearing_distribution_qualified=False,
        steel_resistance_pa=None,
        post_length_m=post_length,
        post_cantilever_stiffness_n_m=post_k,
        foundation_translation_required_if_other_interfaces_rigid_n_m=foundation_req,
        base_rotation_required_if_other_interfaces_rigid_nm_rad=(
            None if foundation_req is None else foundation_req * post_length**2
        ),
        combined_effective_ground_restraint_n_m=effective,
        open=[
            "Aligned return axis removes only the final initial-force end couple; individual-strand stressing and release produce temporary couples",
            "Nominal gross bending, average wall shear and thin-wall closed-box torsion omit local grip-plate bending, distortional/local buckling, holes, welds and fatigue",
            "Annular bearing assumes uniform contact and establishes demand only; front-plate stiffening and exact grip seat require supplier design",
            "50 mm grip geometry is a candidate envelope; actual strand/grip compatibility and required operating space remain unknown",
            "Jack nose access is not covered by the grip spacing screen; the matched stressing system remains unselected",
            "Post stiffness assumes fixed base; ground translation, rotation and connection compliance act in series and remain unmeasured",
            "Sequences are planning alternatives; jack selection/calibration, elongations, force tolerances, asymmetry and safe release procedure require specialist approval",
        ],
        physical_release=False,
    )


def strongback_parts(cfg, report):
    d, L, h, t = (
        cfg[k] for k in ("box_depth_x_m", "box_length_y_m", "box_height_z_m", "wall_m")
    )
    axis = report["axis_z_m"]
    z0 = axis - h / 2
    holes = [
        dict(
            axis="x",
            y_m=L / 2 + sign * p["y_m"],
            z_m=p["z_m"] - z0,
            diameter_m=cfg["front_hole_diameter_m"],
        )
        for p in report["points"]
        for sign in (-1, 1)
    ]
    parts = []
    for label, x in (("outer", -0.5 - d), ("inner", -0.5 - t)):
        parts.append(
            part(
                "strongback-" + label,
                [t, L, h],
                [x, -L / 2, z0],
                holes=holes,
                role="strongback-steel",
            )
        )
    for label, z in (("bottom", z0), ("top", z0 + h - t)):
        parts.append(
            part(
                "strongback-" + label,
                [d - 2 * t, L, t],
                [-0.5 - d + t, -L / 2, z],
                role="strongback-steel",
            )
        )
    for y in (-L / 2, L / 2 - t):
        parts.append(
            part(
                f"strongback-end-{y}",
                [d - 2 * t, t, h - 2 * t],
                [-0.5 - d + t, y, z0 + t],
                role="strongback-steel",
            )
        )
    for y in (-1.85, -0.7175, 0, 0.7175, 1.85):
        th = cfg["diaphragm_thickness_m"]
        parts.append(
            part(
                f"internal-diaphragm-{y}",
                [d - 2 * t, th, h - 2 * t],
                [-0.5 - d + t, y - th / 2, z0 + t],
                role="strongback-steel",
            )
        )
    for y in (-1.85, 1.85):
        parts.append(
            part(
                f"aligned-return-stub-{y}",
                [cfg["return_stub_length_m"], 0.3, 0.5],
                [-0.5, y - 0.15, axis - 0.25],
                kind="tube",
                axis=0,
                wall_m=0.016,
                role="return-rail-steel",
            )
        )
        parts.append(
            part(
                f"restraint-post-{y}",
                [cfg["post_outer_m"], cfg["post_outer_m"], report["post_length_m"]],
                [
                    cfg["restraint_station_m"] - cfg["post_outer_m"] / 2,
                    y - cfg["post_outer_m"] / 2,
                    0,
                ],
                kind="tube",
                axis=2,
                wall_m=cfg["post_wall_m"],
                role="post-steel",
            )
        )
    for p in report["points"]:
        for sign in (-1, 1):
            # External grip bodies are operating/fit envelopes, with no internal wedge model.
            y = sign * p["y_m"]
            diameter = report["grip_outer_diameter_m"]
            length = report["grip_body_length_m"]
            parts.append(
                part(
                    p["id"] + f"-grip-{sign}",
                    [diameter, diameter, length],
                    [-0.5 - d - length, y - diameter / 2, p["z_m"] - diameter / 2],
                    kind="cylinder",
                    cylinder_axis="x",
                    role="grip-envelope",
                )
            )
    return parts


def locator_parts(cfg):
    if not (
        0 < cfg["stem_diameter_m"] < cfg["bore_diameter_m"] < cfg["head_diameter_m"]
        and 0
        < cfg["tap_drill_diameter_m"]
        < cfg["retaining_screw_nominal_diameter_m"]
        < cfg["stem_diameter_m"]
        and 0 < cfg["tap_drill_depth_m"] < cfg["stem_length_m"]
    ):
        raise ValueError(
            "nested positive locator bores, stem, head and blind depth required"
        )
    holes = [
        dict(x_m=0.025, y_m=0.15, diameter_m=0.009, start_m=0.095, length_m=0.005),
        dict(x_m=0.025, y_m=0.15, diameter_m=0.022, start_m=0, length_m=0.005),
    ]
    parts = [
        part(
            "crossrail-coupon",
            [0.05, 0.3, 0.1],
            [-0.025, -0.15, 0.7],
            kind="tube",
            axis=1,
            wall_m=0.005,
            holes=holes,
            role="locator-support-steel",
        ),
        part(
            "datum-mount-plate",
            [0.18, 0.12, 0.02],
            [-0.09, -0.06, 0.8],
            holes=[dict(x_m=0.09, y_m=0.06, diameter_m=cfg["bore_diameter_m"])],
            role="locator-support-steel",
        ),
        part(
            "headed-locator-button",
            [cfg["head_diameter_m"]] * 2
            + [cfg["stem_length_m"] + cfg["head_height_m"]],
            [-cfg["head_diameter_m"] / 2, -cfg["head_diameter_m"] / 2, 0.8],
            kind="stepped-cylinder",
            steps=[
                dict(diameter_m=cfg["stem_diameter_m"], length_m=cfg["stem_length_m"]),
                dict(diameter_m=cfg["head_diameter_m"], length_m=cfg["head_height_m"]),
            ],
            holes=[
                dict(
                    x_m=cfg["head_diameter_m"] / 2,
                    y_m=cfg["head_diameter_m"] / 2,
                    diameter_m=cfg["tap_drill_diameter_m"],
                    length_m=cfg["tap_drill_depth_m"],
                )
            ],
            role="locator-machined-steel",
        ),
        part(
            "retaining-washer-envelope",
            [0.016, 0.016, 0.002],
            [-0.008, -0.008, 0.793],
            kind="cylinder",
            holes=[dict(x_m=0.008, y_m=0.008, diameter_m=0.0084)],
            role="locator-support-steel",
        ),
        part(
            "M8-screw-head-envelope",
            [0.013, 0.013, 0.008],
            [-0.0065, -0.0065, 0.785],
            kind="cylinder",
            role="fastener-envelope",
        ),
        part(
            "M8-screw-thread-envelope",
            [0.008, 0.008, cfg["retaining_screw_underhead_length_m"]],
            [-0.004, -0.004, 0.793],
            kind="cylinder",
            role="thread-envelope",
        ),
    ]
    return parts


def locator(cfg, workholding, a):
    gap = cfg["bore_diameter_m"] - cfg["stem_diameter_m"]
    uncertainty = cfg["bore_tolerance_half_m"] + cfg["stem_tolerance_half_m"]
    parts = locator_parts(cfg)
    button = next(p for p in parts if p["id"] == "headed-locator-button")
    reaction = max(max(c["vertical_reactions_n"]) for c in workholding["cases"])
    return dict(
        nominal_diametral_clearance_m=gap,
        worst_case_diametral_clearance_m=[gap - uncertainty, gap + uncertainty],
        button_nominal_mass_kg=volume(button) * a["steel_density_kg_m3"],
        contact_plane_z_m=0.8 + cfg["stem_length_m"] + cfg["head_height_m"],
        nominal_top_contact_pressure_pa=reaction
        / (math.pi * cfg["head_diameter_m"] ** 2 / 4),
        nominal_head_to_plate_annular_bearing_pa=reaction
        / (math.pi / 4 * (cfg["head_diameter_m"] ** 2 - cfg["bore_diameter_m"] ** 2)),
        screw_nominal_engagement_m=0.793
        + cfg["retaining_screw_underhead_length_m"]
        - 0.8,
        thread_geometry="Tap-drill and nominal major-diameter screw envelopes only; helical threads are not modelled",
        thread_resistance_n=cfg["thread_resistance_n"],
        screw_preload_n=cfg["screw_preload_n"],
        open=[
            "Pin material/hardness, surface finish, tapping, heat-treatment distortion and fits require drawing/supplier approval",
            "M8 retention and 22 mm underside access are proposed details; loosening, fatigue, thread stripping and hole effects need design/trials",
            "Contact pressure is nominal full-head compression, not Hertz contact or proof-load acceptance",
            "The coupon demonstrates one locator; actual clamps, all fixture joints, lateral locators and anchors remain separate",
            "Drill-point relief and thread runout remain unspecified; the cylindrical tap-drill envelope does not establish usable threaded depth",
        ],
        physical_release=False,
    )


def manufacturing_routes(suppliers, cfg, strongback_report):
    by_id = {r["id"]: r for r in suppliers["cases"]}
    metal = [
        p
        for p in strongback_parts(cfg, strongback_report)
        if p["role"].endswith("-steel")
    ]
    box = bounds(metal)
    pieces = {
        "runway-baseplate": [0.9, 0.9, 0.05],
        "strongback-box": [4, cfg["box_depth_x_m"], cfg["box_height_z_m"]],
        "strongback-end-steel": [box[j + 3] - box[j] for j in range(3)],
        "runway-girder": [6, 0.45, 1.2],
    }
    rows = []
    for name, dims in pieces.items():
        required = [v + allowance for v, allowance in zip(dims, [0.3, 0.3, 0.2])]
        for identifier, key in (
            ("promil-starcut260", "axis_travel_m"),
            ("responsive-horizontal", "advertised_capacity_m"),
        ):
            available = by_id[identifier]["published"][key]
            rows.append(
                dict(
                    part=name,
                    supplier_case=identifier,
                    part_envelope_m=dims,
                    setup_reservation_m=required,
                    published_range_m=available,
                    geometric_range_screen=all(
                        x <= y for x, y in zip(required, available)
                    ),
                    payload_and_tool_access_accepted=False,
                    price=None,
                    order_placed=False,
                )
            )
    return dict(
        cases=rows,
        fixture_allowance_basis="OSR +300/+300/+200 mm setup reservations, not supplier workholding clearance",
        suppliers=suppliers,
        new_machine_purchase_approved=False,
        asquith_scope="Current Asquith Butler website focuses on spares/service/retrofit. No new-build gantry machine offer inferred.",
        steel_origin_confirmed=False,
        physical_release=False,
    )


def build(a, cfg, candidate, iteration, equipment, suppliers):
    sb = strongback(a, cfg["strongback"], candidate, equipment["ccl-sla15"])
    loc = locator(cfg["locator"], iteration["workholding"], a)
    return dict(
        schema="osr-factory-connections/1",
        revision=cfg["revision"],
        basis=cfg,
        strongback=sb,
        locator=loc,
        manufacturing=manufacturing_routes(suppliers, cfg["strongback"], sb),
        physical_release=False,
    )
