"""Feedback-driven connected frame/bolster research, with unclosed release gates.

Two distinct configurations are evaluated from their own loads and dimensions.
A useful local result is a proposed assembly definition, never a completed rail
vehicle or an accepted strength, stiffness, welding or production assessment.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

from . import architecture_mechanical, mechanical_systems

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(__file__).with_name("data") / "mechanical-detail-space.json"
_CONTEXT_CACHE = {}


def _digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _inputs():
    return json.loads(DATA.read_text())


def contexts():
    """Never transfer an LM3 member mass, acceptance or envelope to six cars."""
    ctx = mechanical_systems.context()
    source = architecture_mechanical._source(ctx)
    spine = mechanical_systems.source_spine_dimensions(ctx)
    sill = ctx["pdr"]["LM3-BDY-P010"]["design_reference_envelope_mm"]
    lm3 = dict(
        id="LM3",
        configuration_id="LM3",
        body_length_m=source["body_length_m"],
        side_member_length_m=sill[0] / 1000,
        side_member_width_m=sill[1] / 1000,
        side_depth_envelope_m=sill[2] / 1000,
        centre_member_length_m=spine["length_m"],
        centre_member_width_m=spine["width_m"],
        centre_member_depth_m=spine["height_m"],
        support_x_m=source["cars"][0]["support_x_m"],
        source_car_force_n=sum(a["force_n"] for a in source["cars"][0]["axles"]),
        source_car_mass_kg=source["cars"][0]["source_mass_kg"],
        source_force_gravity_m_s2=9.81,
        body_count=3,
        axle_count=12,
        work_package_ids=["LM3-FRP-010", "BUY-LM3-CAR-A900"],
        source_sha256=ctx["source_sha256"],
        envelope_basis="Existing LM3 260 mm side-sill / 220x380 mm centre-spine review envelopes, not certified fabricated sections.",
        accepted_loading=False,
    )
    integration_path = DATA.with_name("integration-systems.json")
    qualification_path = (
        ROOT
        / "engineering/civil_exploration/examples/baghdad-qualification/qualification.json"
    )
    from .evidence_store import read_json

    planning = read_json(qualification_path)["planning_train"]
    integration = json.loads(integration_path.read_text())
    if planning["cars"] != 6 or planning["axles"] != 24:
        raise ValueError("six-car context must retain six cars and 24 axles")
    length = planning["length_m"] / planning["cars"]
    mass = planning["infrastructure_full_train_allowance_t"] * 1000 / planning["cars"]
    six = dict(
        id="metro-6car-planning",
        configuration_id="metro-6car-planning",
        body_length_m=length,
        side_member_length_m=length - 0.5,
        side_member_width_m=0.24,
        side_depth_envelope_m=None,
        centre_member_length_m=length - 0.7,
        centre_member_width_m=0.3,
        centre_member_depth_m=0.5,
        support_x_m=[
            integration["bogie_centre_inset_m"],
            length - integration["bogie_centre_inset_m"],
        ],
        source_car_force_n=mass * 9.80665,
        source_car_mass_kg=mass,
        source_force_gravity_m_s2=9.80665,
        source_mass_label="384t infrastructure allowance, not AW2/AW3 vehicle mass",
        planning_train_mass_sensitivities_kg={
            "AW2": planning["aw2_mass_t"] * 1000,
            "AW3": planning["aw3_mass_t"] * 1000,
            "infrastructure_allowance": planning[
                "infrastructure_full_train_allowance_t"
            ]
            * 1000,
        },
        body_count=6,
        axle_count=24,
        work_package_ids=["BASIS-CONFIGURATION"],
        source_sha256={
            str(p.relative_to(ROOT)): _digest(p)
            for p in [integration_path, qualification_path]
        },
        envelope_basis="Independent six-car planning-only hypothesis: 240 mm side width and 300x500 mm centre spine, not LM3 geometry or a supplier vehicle; no accepted depth/gauge/floor envelope exists.",
        accepted_loading=False,
    )
    for item in [lm3, six]:
        item["load_basis"] = (
            "Full original per-car force PLUS all proposed assembly gross steel; no unidentified original frame mass is subtracted. Symmetric UDL across the complete body including overhangs. Static only; no accepted rail load combinations."
        )
        item["source_sha256"].update(
            {
                str(p.relative_to(ROOT)): _digest(p)
                for p in [Path(__file__), DATA, Path(architecture_mechanical.__file__)]
            }
        )
    six["load_basis"] = (
        "384t infrastructure allowance distributed equally across six cars as an "
        "explicit stress-test hypothesis, not a measured AW2/AW3 vehicle mass. "
        "All proposed assembly gross steel is additionally added without a "
        "replacement deduction. Symmetric UDL across each complete body including "
        "overhangs; no accepted rail load combinations or axle distribution."
    )
    result = [lm3, six]
    # Cache definitions, not an unchecked assertion of freshness. Public assess
    # compares exact values and hashes every dependency's current bytes again.
    _CONTEXT_CACHE.clear()
    _CONTEXT_CACHE.update({item["configuration_id"]: deepcopy(item) for item in result})
    return result


def seed(context):
    if context["configuration_id"] not in {"LM3", "metro-6car-planning"}:
        raise ValueError("unknown mechanical detail configuration")
    return dict(_inputs()["seed"])


def i_section(width, height, flange, web):
    if (
        not all(math.isfinite(v) and v > 0 for v in [width, height, flange, web])
        or height <= 2 * flange
        or width <= web
    ):
        raise ValueError("positive nondegenerate I section required")
    area = 2 * width * flange + (height - 2 * flange) * web
    inertia = (width * height**3 - (width - web) * (height - 2 * flange) ** 3) / 12
    return dict(area_m2=area, inertia_m4=inertia)


def box_section(width, height, wall):
    if (
        not all(math.isfinite(v) and v > 0 for v in [width, height, wall])
        or min(width, height) <= 2 * wall
    ):
        raise ValueError("positive nondegenerate box section required")
    return dict(
        area_m2=width * height - (width - 2 * wall) * (height - 2 * wall),
        inertia_m4=(width * height**3 - (width - 2 * wall) * (height - 2 * wall) ** 3)
        / 12,
    )


def overhang_beam(length, supports, force, ei):
    """Exact uniform load over full length, two symmetric interior supports.

    Piecewise Macaulay integration; find all deflection extrema by bracketing
    slope zeros on intervals split at bending-moment zeros. No sampled maximum
    is silently treated as a continuous bound. Positive y is upward here.
    """
    a, b = supports
    if (
        not (0 <= a < b <= length)
        or not math.isclose(a, length - b, abs_tol=1e-9)
        or not all(math.isfinite(v) and v > 0 for v in [length, force, ei])
    ):
        raise ValueError("positive beam data and symmetric supports required")
    q, reaction = force / length, force / 2

    def base(x):
        return (
            -q * x**4 / 24
            + reaction * max(0.0, x - a) ** 3 / 6
            + reaction * max(0.0, x - b) ** 3 / 6
        )

    c1 = (base(a) - base(b)) / (b - a)
    c2 = -base(a) - c1 * a

    def y(x):
        return (base(x) + c1 * x + c2) / ei

    def slope(x):
        return (
            -q * x**3 / 6
            + reaction * max(0.0, x - a) ** 2 / 2
            + reaction * max(0.0, x - b) ** 2 / 2
            + c1
        ) / ei

    def moment(x):
        return -q * x * x / 2 + reaction * max(0.0, x - a) + reaction * max(0.0, x - b)

    split = [0.0, a, b, length]
    # In each segment M=A*x^2+B*x+C; its roots bound monotone slope intervals.
    for low, high, active in [(0.0, a, []), (a, b, [a]), (b, length, [a, b])]:
        aa, bb, cc = -q / 2, reaction * len(active), -reaction * sum(active)
        disc = bb * bb - 4 * aa * cc
        if disc >= 0:
            for x in [
                (-bb - math.sqrt(disc)) / (2 * aa),
                (-bb + math.sqrt(disc)) / (2 * aa),
            ]:
                if low < x < high:
                    split.append(x)
    split = sorted(set(split))
    extrema = list(split)
    for low, high in zip(split, split[1:]):
        if slope(low) * slope(high) < 0:
            left, right = low, high
            for _ in range(70):
                mid = (left + right) / 2
                if slope(left) * slope(mid) <= 0:
                    right = mid
                else:
                    left = mid
            extrema.append((left + right) / 2)
    # M extrema occur at supports, free ends and V=0; symmetry puts it at midspan.
    ms = [0.0, a, b, length, length / 2]
    shears = [-q * a, reaction - q * a, reaction - q * b, 2 * reaction - q * b]
    return dict(
        reactions_n=[reaction, reaction],
        maximum_abs_deflection_m=max(abs(y(x)) for x in extrema),
        deflection_at_supports_m=[y(a), y(b)],
        maximum_abs_moment_nm=max(abs(moment(x)) for x in ms),
        maximum_abs_shear_n=max(map(abs, shears)),
        deflection_extrema_x_m=sorted(set(extrema)),
        force_balance_error_n=2 * reaction - force,
        first_moment_balance_error_nm=reaction * a + reaction * b - force * length / 2,
        uniform_load_n_m=q,
        ei_n_m2=ei,
    )


def _plate(identifier, size, at, **extra):
    return dict(
        id=identifier,
        kind="box",
        role="provisional-fabricated-plate",
        size_m=list(size),
        at_m=list(at),
        **extra,
    )


def _geometry(v, c, a):
    """Physical cut-plate members, both bolsters, support diaphragms and pads."""
    h, tf, tw, tc = [
        v[k]
        for k in [
            "side_depth_m",
            "plate_thickness_m",
            "web_thickness_m",
            "spine_wall_m",
        ]
    ]
    ys = a["longitudinal_centres_y_m"]
    cbw, cbh, cbt = a["crossbearer_section_m"]
    length = c["body_length_m"]
    parts = []
    # Longitudinal plate segments stop at butt interfaces: no overlapping stock.
    for member, y, member_length, width, height, ft, wt, box in [
        (
            "side-left",
            ys[0],
            c["side_member_length_m"],
            c["side_member_width_m"],
            h,
            tf,
            tw,
            False,
        ),
        (
            "spine",
            ys[1],
            c["centre_member_length_m"],
            c["centre_member_width_m"],
            c["centre_member_depth_m"],
            tc,
            tc,
            True,
        ),
        (
            "side-right",
            ys[2],
            c["side_member_length_m"],
            c["side_member_width_m"],
            h,
            tf,
            tw,
            False,
        ),
    ]:
        n = math.ceil(member_length / v["maximum_stock_piece_length_m"])
        piece = member_length / n
        for j in range(n):
            x = (length - member_length) / 2 + j * piece
            for name, z in [("lower", 0.0), ("upper", height - ft)]:
                parts.append(
                    _plate(
                        f"{member}-{name}-{j+1}",
                        [piece, width, ft],
                        [x, y - width / 2, z],
                        joint_route=(
                            "full-penetration transverse butt weld at each segment boundary; qualification unknown"
                            if n > 1
                            else "unspliced long stock"
                        ),
                    )
                )
            web_ys = [y - width / 2, y + width / 2 - wt] if box else [y - wt / 2]
            for k, wy in enumerate(web_ys):
                parts.append(
                    _plate(
                        f"{member}-web-{j+1}-{k+1}",
                        [piece, wt, height - 2 * ft],
                        [x, wy, ft],
                    )
                )
        if box:
            for j, x in enumerate(
                [(length - member_length) / 2, (length + member_length) / 2 - wt]
            ):
                parts.append(
                    _plate(
                        f"{member}-end-closure-{j+1}",
                        [wt, width - 2 * wt, height - 2 * ft],
                        [x, y - width / 2 + wt, ft],
                    )
                )
    # Two transverse I bolsters below the longitudinal lower flanges.
    bolster_span = ys[-1] - ys[0] + c["side_member_width_m"]
    hb = v["bolster_depth_m"]
    for j, x in enumerate(c["support_x_m"]):
        for name, z in [("lower", -hb), ("upper", -tf)]:
            parts.append(
                _plate(
                    f"bolster-{j+1}-{name}",
                    [0.30, bolster_span, tf],
                    [x - 0.15, -bolster_span / 2, z],
                )
            )
        parts.append(
            _plate(
                f"bolster-{j+1}-web",
                [tw, bolster_span, hb - 2 * tf],
                [x - tw / 2, -bolster_span / 2, -hb + tf],
            )
        )
        # Vertical load enters full-width webs with transverse stiffener planes
        # at the bolster edges; side I stiffeners terminate at their centre web.
        for member, y, width, height, ft, wt, is_box in [
            ("left", ys[0], c["side_member_width_m"], h, tf, tw, False),
            (
                "centre",
                0.0,
                c["centre_member_width_m"],
                c["centre_member_depth_m"],
                tc,
                tc,
                True,
            ),
            ("right", ys[2], c["side_member_width_m"], h, tf, tw, False),
        ]:
            for k, dx in enumerate([-0.15, 0.15]):
                if is_box:
                    parts.append(
                        _plate(
                            f"diaphragm-{j+1}-{member}-{k}",
                            [
                                v["diaphragm_thickness_m"],
                                width - 2 * wt,
                                height - 2 * ft,
                            ],
                            [
                                x + dx - v["diaphragm_thickness_m"] / 2,
                                y - width / 2 + wt,
                                ft,
                            ],
                        )
                    )
                else:
                    half = (width - wt) / 2
                    for side, wy in enumerate([y - width / 2, y + wt / 2]):
                        parts.append(
                            _plate(
                                f"diaphragm-{j+1}-{member}-{k}-{side}",
                                [v["diaphragm_thickness_m"], half, height - 2 * ft],
                                [x + dx - v["diaphragm_thickness_m"] / 2, wy, ft],
                            )
                        )
        px, py, pt = a["support_pad_size_m"]
        count = v["bolts_per_support"]
        pitch = a["support_bolt_pitch_m"]
        holes = [
            dict(
                axis="z",
                diameter_m=v["bolt_diameter_m"] * a["bolt_hole_diameter_ratio"],
                x_m=px / 2 + dx,
                y_m=py / 2 + dy,
            )
            for dx in [-pitch / 2, pitch / 2]
            for dy in [
                -pitch / 2 + k * pitch / (count / 2 - 1) for k in range(count // 2)
            ]
        ]
        parts.append(
            _plate(
                f"bogie-interface-pad-{j+1}",
                [px, py, pt],
                [x - px / 2, -py / 2, -hb - pt],
                holes=holes,
            )
        )
        # Hold-downs penetrate BOTH the pad and the bolster lower flange.
        # The open sides of the fabricated I bolster allow a socket route;
        # the bolt's actual nut/wrench envelope still requires trial fitting.
        flange = next(p for p in parts if p["id"] == f"bolster-{j+1}-lower")
        flange["holes"] = [
            dict(
                axis="z",
                diameter_m=hole["diameter_m"],
                x_m=hole["x_m"] + 0.15 - px / 2,
                y_m=hole["y_m"] + bolster_span / 2 - py / 2,
            )
            for hole in holes
        ]
        # Bolster web stiffeners over the bearing footprint, two sides of web.
        for k, wy in enumerate([-py / 2, py / 2 - v["diaphragm_thickness_m"]]):
            for z, xx in enumerate([x - 0.15, x + tw / 2]):
                parts.append(
                    _plate(
                        f"bolster-pad-stiffener-{j+1}-{k}-{z}",
                        [(0.30 - tw) / 2, v["diaphragm_thickness_m"], hb - 2 * tf],
                        [xx, wy, -hb + tf],
                    )
                )
    # Crossbearers are clear pieces between longitudinal member faces; no
    # apparent geometric intersections are used to imply a qualified joint.
    count = math.ceil((length - 1.0) / v["crossbearer_pitch_m"]) - 1
    xs = [0.5 + (k + 1) * (length - 1.0) / (count + 1) for k in range(count)]
    xs = [x for x in xs if all(abs(x - s) > 0.15 + cbw / 2 for s in c["support_x_m"])]
    for j, x in enumerate(xs):
        for k, (ya, yb) in enumerate(
            [
                (ys[0] + c["side_member_width_m"] / 2, -c["centre_member_width_m"] / 2),
                (c["centre_member_width_m"] / 2, ys[2] - c["side_member_width_m"] / 2),
            ]
        ):
            parts.append(
                dict(
                    id=f"crossbearer-{j+1}-{k+1}",
                    kind="tube",
                    role="provisional-crossbearer",
                    size_m=[cbw, yb - ya, cbh],
                    at_m=[x - cbw / 2, ya, 0.0],
                    axis=1,
                    wall_m=cbt,
                )
            )
    return dict(parts=parts, crossbearer_x_m=xs, bolster_span_m=bolster_span)


def _volume(p):
    v = math.prod(p["size_m"])
    if p["kind"] == "tube":
        inside = [
            s if k == p["axis"] else s - 2 * p["wall_m"]
            for k, s in enumerate(p["size_m"])
        ]
        v -= math.prod(inside)
    for hole in p.get("holes", []):
        v -= math.pi * hole["diameter_m"] ** 2 / 4 * p["size_m"][2]
    return v


def _assign_material_requests(parts, plate_request, fastener_request):
    """Keep proposed fastener property class distinct from structural plate."""
    for part in parts:
        is_fastener = (
            part.get("material_family") == "fastener"
            or part.get("role")
            in {
                "fastener",
                "fastener-envelope",
                "provisional-fastener-envelope",
                "provisional-bolt-envelope",
                "provisional-bolt-head-envelope",
            }
            or part["id"].startswith(("bolt-", "hold-down-bolt-"))
        )
        part["material_request"] = fastener_request if is_fastener else plate_request
        part["material_request_accepted"] = False


def _require_context(context):
    if not _CONTEXT_CACHE:
        contexts()
    current = (
        _CONTEXT_CACHE.get(context.get("configuration_id"))
        if isinstance(context, dict)
        else None
    )
    try:
        valid = (
            current is not None
            and context == current
            and all(
                _digest(ROOT / name) == digest
                for name, digest in current["source_sha256"].items()
            )
        )
    except OSError:
        valid = False
    if not valid:
        raise ValueError("exact current mechanical context and source hashes required")
    return current


def _stiffness_bound(context):
    if context["configuration_id"] != "LM3":
        return None
    cfg = _inputs()
    b = context["side_member_width_m"]
    h = context["side_depth_envelope_m"]
    centre_b = context["centre_member_width_m"]
    full_h = context["centre_member_depth_m"]
    offset = (full_h - h) / 2
    # I_NA is the minimum over possible reference axes. Thus inertia about the
    # fixed common-envelope mid-height axis upper-bounds I_NA. Filling every
    # rectangle with steel and maximizing each side centroid's offset gives
    # an upper bound even if the two side members have different elevations.
    upper_i = 2 * (b * h**3 / 12 + b * h * offset**2) + centre_b * full_h**3 / 12
    beam = overhang_beam(
        context["body_length_m"],
        context["support_x_m"],
        context["source_car_force_n"],
        cfg["material"]["young_modulus_pa"] * upper_i,
    )
    target = (context["support_x_m"][1] - context["support_x_m"][0]) / cfg[
        "research_limits"
    ]["deflection_span_divisor"]
    return dict(
        schema="osr-lm3-constant-section-stiffness-family-bound/1",
        configuration_id="LM3",
        side_solid_rectangles_m=[[b, h], [b, h]],
        centre_solid_rectangle_m=[centre_b, full_h],
        common_vertical_envelope_m=full_h,
        fixed_reference_axis_z_m=full_h / 2,
        maximum_side_centroid_offset_m=offset,
        parallel_axis_terms_included=True,
        inertia_upper_bound_m4=upper_i,
        young_modulus_pa=cfg["material"]["young_modulus_pa"],
        modeled_source_force_n=context["source_car_force_n"],
        added_self_mass_for_bound_kg=0,
        body_length_m=context["body_length_m"],
        support_x_m=list(context["support_x_m"]),
        deflection_lower_bound_within_constant_ei_family_m=beam[
            "maximum_abs_deflection_m"
        ],
        unaccepted_research_deflection_target_m=target,
        research_family_screen_incompatible=beam["maximum_abs_deflection_m"] > target,
        hypotheses=[
            "Only two 180x260mm side rectangles and one 220x380mm spine rectangle; all steel stays inside those widths and a common 380mm vertical envelope.",
            "Every rectangle is completely SOLID with E200GPa; ideal rigid transverse compatibility, no joint/shear/bolster compliance and zero added steel self-weight.",
            "Every filled rectangle optimistically extends over the complete body with CONSTANT SECTION/EI, including absent native member ends; symmetric original supports and complete-body uniform original car force are unchanged.",
            "Side members may occupy either edge of the common vertical envelope. Fixed-axis parallel-axis terms upper-bound actual neutral-axis inertia, including top-aligned/bottom-aligned or opposite side elevations.",
        ],
        limitation="Incompatibility of this declared constant-EI research family with its unaccepted L/1000 target only. Does not prove a complete physical vehicle infeasible, nor bound arbitrary variable-EI geometry, shell/truss/composite action, changed loading/supports, material, envelopes or authority criteria.",
        required_decision="Review a different structural load path/envelope or accepted criterion; enlarging the bounded search cannot close this particular constant-section family while retaining these hypotheses.",
        accepted_properties=False,
        accepted_loading=False,
        engineering_design_complete=False,
        manufacturing_release=False,
        physical_release=False,
    )


def stiffness_bound(context):
    """Transparent analytical-family bound; six-car geometry is not adopted."""
    return _stiffness_bound(_require_context(context))


def assess(variables, context):
    """Re-evaluate an exact current context and all declared load sensitivities."""
    current = _require_context(context)
    result = _evaluate(variables, current)
    result["basis"]["constant_ei_family_stiffness_bound"] = _stiffness_bound(current)
    baseline_mass = current["source_car_mass_kg"] * current["body_count"]
    responses = [
        dict(
            id=(
                "LM3-source-force"
                if current["configuration_id"] == "LM3"
                else "planning-six-car-384000kg"
            ),
            original_train_mass_kg=baseline_mass,
            added_gross_steel_per_car_kg=result["objectives"]["mass_kg"],
            beam=result["metrics"]["beam"],
            member_stresses_pa=result["metrics"]["member_stresses_pa"],
            connections=result["connections"],
        )
    ]
    if current["configuration_id"] == "metro-6car-planning":
        case = _inputs()["additional_sixcar_load_case"]
        if not math.isclose(
            baseline_mass * case["baseline_allowance_multiplier"],
            case["planning_train_mass_kg"],
            abs_tol=1e-8,
        ):
            raise ValueError(
                "declared six-car load sensitivity no longer matches source"
            )
        envelope_context = deepcopy(current)
        envelope_context["source_car_mass_kg"] = (
            case["planning_train_mass_kg"] / current["body_count"]
        )
        envelope_context["source_car_force_n"] = (
            envelope_context["source_car_mass_kg"]
            * current["source_force_gravity_m_s2"]
        )
        envelope = _evaluate(variables, envelope_context)
        if result["geometry"] != envelope["geometry"]:
            raise ValueError("sensitivity must use the exact same assembly geometry")
        load_dependent = {
            "global_service_deflection",
            "gross_member_normal_stress",
            "gross_web_shear",
            "side_flange_elastic_plate_buckling",
            "side_web_elastic_plate_buckling",
            "centre_plate_elastic_buckling",
            "bolster_bending",
            "bolster_tip_deflection",
            "support_diaphragm_nominal_compression",
            "intersection_weld_nominal_shear",
            "longitudinal_flange_weld_shear_flow",
            "support_bolt_combined_nominal_stress",
            "support_pad_bearing",
            "crossbearer_floor_tributary_stress",
            "crossbearer_floor_tributary_deflection",
        }
        for check in envelope["checks"]:
            if check["id"] in load_dependent:
                copied = dict(check)
                copied["id"] = case["id"] + "/" + check["id"]
                copied["basis"] = case["basis"] + " " + check["basis"]
                result["checks"].append(copied)
        responses.append(
            dict(
                id=case["id"],
                original_train_mass_kg=case["planning_train_mass_kg"],
                added_gross_steel_per_car_kg=envelope["objectives"]["mass_kg"],
                beam=envelope["metrics"]["beam"],
                member_stresses_pa=envelope["metrics"]["member_stresses_pa"],
                connections=envelope["connections"],
                accepted_loading=False,
            )
        )
        result["failed_check_ids"] = [
            check["id"] for check in result["checks"] if check["state"] == "fail"
        ]
        result["local_calculated_checks_passed"] = not result["failed_check_ids"]
        result["next_actions"] = [
            "Repair local check: " + name for name in result["failed_check_ids"]
        ] + [
            "Resolve qualification gate: " + name
            for name in result["unknown_check_ids"]
        ]
    result["metrics"]["load_case_responses"] = responses
    return result


def _evaluate(variables, context):
    """Private numerical core; public assess rejects unbound caller contexts."""
    cfg = _inputs()
    m, a = cfg["material"], cfg["research_limits"]
    v = dict(variables)
    c = context
    if set(v) != set(cfg["bounds"]) or any(
        v[k] not in choices for k, choices in cfg["bounds"].items()
    ):
        raise ValueError("variation outside explicit bounded domain")
    h, tf, tw, tc = [
        v[k]
        for k in [
            "side_depth_m",
            "plate_thickness_m",
            "web_thickness_m",
            "spine_wall_m",
        ]
    ]
    side = i_section(c["side_member_width_m"], h, tf, tw)
    spine = box_section(c["centre_member_width_m"], c["centre_member_depth_m"], tc)
    geometry = _geometry(v, c, a)
    gross_mass = sum(_volume(p) * m["density_kg_m3"] for p in geometry["parts"])
    force = c["source_car_force_n"] + gross_mass * a["added_mass_gravity_m_s2"]
    inertias = [side["inertia_m4"], spine["inertia_m4"], side["inertia_m4"]]
    total_i = sum(inertias)
    shares = [i / total_i for i in inertias]
    beam = overhang_beam(
        c["body_length_m"], c["support_x_m"], force, m["young_modulus_pa"] * total_i
    )
    fac = a["vertical_strength_multiplier"]
    stress = [
        beam["maximum_abs_moment_nm"] * fac * share * depth / 2 / inertia
        for share, depth, inertia in zip(
            shares, [h, c["centre_member_depth_m"], h], inertias
        )
    ]
    shear = [
        beam["maximum_abs_shear_n"] * fac * shares[k] / webarea
        for k, webarea in enumerate(
            [
                tw * (h - 2 * tf),
                2 * tc * (c["centre_member_depth_m"] - 2 * tc),
                tw * (h - 2 * tf),
            ]
        )
    ]
    poisson = m["poisson_ratio"]
    plate_factor = math.pi**2 * m["young_modulus_pa"] / (12 * (1 - poisson**2))
    flange_b = (c["side_member_width_m"] - tw) / 2
    flange_critical = 0.43 * plate_factor * (tf / flange_b) ** 2
    web_critical = 4 * plate_factor * (tw / (h - 2 * tf)) ** 2
    # Research elastic plate screens include centre top plate and centre webs.
    centre_flange_critical = (
        4 * plate_factor * (tc / (c["centre_member_width_m"] - 2 * tc)) ** 2
    )
    centre_web_critical = (
        4 * plate_factor * (tc / (c["centre_member_depth_m"] - 2 * tc)) ** 2
    )
    side_reaction = beam["reactions_n"][0] * shares[0] * fac
    centre_reaction = beam["reactions_n"][0] * shares[1] * fac
    lever = abs(a["longitudinal_centres_y_m"][0])
    bolster = i_section(0.30, v["bolster_depth_m"], tf, tw)
    bolster_moment = side_reaction * lever
    bolster_stress = bolster_moment * v["bolster_depth_m"] / 2 / bolster["inertia_m4"]
    bolster_delta = (
        side_reaction * lever**3 / (3 * m["young_modulus_pa"] * bolster["inertia_m4"])
    )
    diaphragm = max(
        side_reaction
        / (2 * v["diaphragm_thickness_m"] * (c["side_member_width_m"] - tw)),
        centre_reaction
        / (2 * v["diaphragm_thickness_m"] * (c["centre_member_width_m"] - 2 * tc)),
    )
    weld = max(
        side_reaction / (2 * v["weld_throat_m"] * c["side_member_width_m"]),
        centre_reaction / (2 * v["weld_throat_m"] * c["centre_member_width_m"]),
    )
    q_side = c["side_member_width_m"] * tf * (h / 2 - tf / 2)
    longitudinal_weld_flow = (
        beam["maximum_abs_shear_n"] * fac * shares[0] * q_side / side["inertia_m4"]
    )
    longitudinal_weld_stress = longitudinal_weld_flow / (2 * v["weld_throat_m"])
    # Pad bears vertical reaction. Bolts transfer horizontal inertia plus
    # overturning about the pad, not a fictitious vertical bolt shear load.
    horizontal = (
        (c["source_car_mass_kg"] + gross_mass) * a["horizontal_acceleration_m_s2"] / 2
    )
    n = v["bolts_per_support"]
    pitch = a["support_bolt_pitch_m"]
    bolt_key = format(v["bolt_diameter_m"], ".3f")
    bolt_area = cfg["bolt_request"]["tensile_stress_area_m2"][bolt_key]
    tension = horizontal * a["horizontal_force_height_above_pad_m"] / (n * pitch / 2)
    bolt_shear = horizontal / n
    bolt_eq = math.sqrt((tension / bolt_area) ** 2 + 3 * (bolt_shear / bolt_area) ** 2)
    hole = v["bolt_diameter_m"] * a["bolt_hole_diameter_ratio"]
    edge = (min(a["support_pad_size_m"][:2]) - pitch) / 2
    socket = 1.7 * v["bolt_diameter_m"] + 0.012
    hole_spacing = pitch / (n / 2 - 1)
    pad_bearing = (
        beam["reactions_n"][0]
        * fac
        / (math.prod(a["support_pad_size_m"][:2]) - n * math.pi * hole**2 / 4)
    )
    cbw, cbh, cbt = a["crossbearer_section_m"]
    cb = box_section(cbw, cbh, cbt)
    actual_x = (
        [0.0]
        + geometry["crossbearer_x_m"]
        + list(c["support_x_m"])
        + [c["body_length_m"]]
    )
    pitch_actual = max(y - x for x, y in zip(sorted(actual_x), sorted(actual_x)[1:]))
    halfspan = (geometry["bolster_span_m"] - c["side_member_width_m"]) / 2
    transverse_q = force / c["body_length_m"] * pitch_actual / (2 * halfspan)
    cb_delta = (
        5
        * transverse_q
        * halfspan**4
        / (384 * m["young_modulus_pa"] * cb["inertia_m4"])
    )
    cb_stress = fac * transverse_q * halfspan**2 / 8 * (cbh / 2) / cb["inertia_m4"]
    equipment = cfg["supplier_evidence"][0]
    flat = [p for p in geometry["parts"] if p["kind"] == "box"]
    plate_load = max(math.prod(p["size_m"]) * m["density_kg_m3"] for p in flat)
    largest_length = max(sorted(p["size_m"])[2] for p in flat)
    largest_width = max(sorted(p["size_m"])[1] for p in flat)
    thickness = max(
        (
            p["size_m"][2]
            if "web" not in p["id"]
            and "diaphragm" not in p["id"]
            and "stiffener" not in p["id"]
            else min(p["size_m"])
        )
        for p in flat
    )
    # Actual cutting thickness is the smallest plate dimension for every plate,
    # independent of how the plate is oriented in the assembly.
    thickness = max(min(p["size_m"]) for p in flat)
    span = c["support_x_m"][1] - c["support_x_m"][0]
    checks = []

    def check(identifier, value, limit, units, basis, passed=None):
        state = (
            "unknown"
            if value is None or limit is None
            else ("pass" if (value <= limit if passed is None else passed) else "fail")
        )
        checks.append(
            dict(
                id=identifier,
                state=state,
                value=value,
                limit=limit,
                units=units,
                basis=basis,
            )
        )

    check(
        "global_service_deflection",
        beam["maximum_abs_deflection_m"],
        span / a["deflection_span_divisor"],
        "m",
        "Full body UDL and overhang equilibrium; three EI-proportional members under rigid-tie hypothesis. L/1000 is an unaccepted research target.",
    )
    check(
        "gross_member_normal_stress",
        max(stress),
        m["research_normal_stress_limit_pa"],
        "Pa",
        "Elastic stress under explicit 1.25 vertical multiplier, not rail-standard load combinations or accepted design resistance.",
    )
    check(
        "gross_web_shear",
        max(shear),
        m["research_normal_stress_limit_pa"] / math.sqrt(3),
        "Pa",
        "Average web shear; stress concentration, openings and shear buckling interaction not represented.",
    )
    check(
        "side_flange_elastic_plate_buckling",
        stress[0],
        flange_critical,
        "Pa",
        "Ideal isolated outstand k=0.43, elastic plate formula; diagnostic only, no railway member buckling qualification.",
    )
    check(
        "side_web_elastic_plate_buckling",
        stress[0],
        web_critical,
        "Pa",
        "Ideal internal plate under uniform compression k=4 used conservatively versus maximum bending stress; actual stress-gradient/shear interaction unknown.",
    )
    check(
        "centre_plate_elastic_buckling",
        stress[1],
        min(centre_flange_critical, centre_web_critical),
        "Pa",
        "Ideal simply-supported internal plate k=4; no postbuckling, imperfections or fabricated corner resistance adopted.",
    )
    check(
        "bolster_bending",
        bolster_stress,
        m["research_normal_stress_limit_pa"],
        "Pa",
        "Transverse half-bolster cantilever carrying EI-proportional side-member reaction into central support pad.",
    )
    check(
        "bolster_tip_deflection",
        bolster_delta,
        a["bolster_tip_deflection_m"],
        "m",
        "Local cantilever displacement diagnostic; finite transverse stiffness still requires shell/beam model of actual joint compatibility.",
    )
    check(
        "support_diaphragm_nominal_compression",
        diaphragm,
        m["research_normal_stress_limit_pa"],
        "Pa",
        "Two stiffener planes per intersection, full-width plate area excluding centre web; local crippling and diaphragm weld qualification remain unknown.",
    )
    check(
        "intersection_weld_nominal_shear",
        weld,
        m["research_weld_shear_limit_pa"],
        "Pa",
        "Two effective weld runs across each longitudinal-member width carry vertical reaction; no fatigue or eccentricity resistance assumed.",
    )
    check(
        "longitudinal_flange_weld_shear_flow",
        longitudinal_weld_stress,
        m["research_weld_shear_limit_pa"],
        "Pa",
        "VQ/I divided between two longitudinal flange-web fillet throats, with same vertical multiplier.",
    )
    check(
        "weld_size_thinner_plate",
        v["weld_throat_m"],
        a["weld_throat_to_thinner_plate_max"]
        * min(tf, tw, tc, v["diaphragm_thickness_m"]),
        "m",
        "Research fabrication throat/thinner-plate limit; increasing weld without plate thickness can introduce a new failed check.",
    )
    check(
        "support_bolt_combined_nominal_stress",
        bolt_eq,
        m["research_bolt_equivalent_stress_limit_pa"],
        "Pa",
        "Two-row bolt group, explicit 0.3g horizontal hypothesis and 1m moment arm. sqrt(sigma^2+3*tau^2), not a connection-code interaction or crash assessment; pad bears vertical load.",
    )
    check(
        "support_pad_bearing",
        pad_bearing,
        m["research_normal_stress_limit_pa"],
        "Pa",
        "Vertical reaction divided by net pad footprint; bogie mating body, contact pressure distribution and prying not qualified.",
    )
    check(
        "bolt_hole_edge_distance",
        1.5 * hole,
        edge,
        "m",
        "Research edge >= 1.5 hole diameters; actual bolt standard and fatigue layout require acceptance.",
    )
    check(
        "socket_neighbour_access",
        socket + 0.005,
        hole_spacing,
        "m",
        "1.7d+12mm assumed socket outside diameter plus 5mm gap; actual wrench sweep and service access not proven.",
    )
    check(
        "crossbearer_floor_tributary_stress",
        cb_stress,
        m["research_normal_stress_limit_pa"],
        "Pa",
        "Full body load treated as uniform floor demand on largest actual bearer spacing; each side half-span simply supported.",
    )
    check(
        "crossbearer_floor_tributary_deflection",
        cb_delta,
        a["crossbearer_deflection_m"],
        "m",
        "Local floor bearer deflection under largest actual tributary pitch; shell participation not claimed.",
    )
    check(
        "source_side_depth_envelope",
        h,
        c["side_depth_envelope_m"],
        "m",
        c["envelope_basis"],
    )
    check(
        "xp4000_plate_length",
        largest_length,
        equipment["published_cutting_area_m"][0],
        "m",
        "Every proposed plate must fit published XP4000 cutting envelope; long stock cannot be processed as if a 4m machine were a 16m machine.",
    )
    check(
        "xp4000_plate_width",
        largest_width,
        equipment["published_cutting_area_m"][1],
        "m",
        "Rotation allowed on the flat cutting bed, not an assumed larger cutting table.",
    )
    check(
        "xp4000_plate_thickness",
        thickness,
        equipment["published_maximum_thickness_m"],
        "m",
        "Specific XP brochure states 32mm maximum; power source, grade, piercing and finish capability still need vendor confirmation.",
    )
    check(
        "xp4000_individual_plate_load",
        plate_load,
        equipment["published_maximum_supported_load_kg"],
        "kg",
        "Largest individual plate, not a whole loaded nesting sheet. A complete nest load and extraction trial remain unaccepted.",
    )
    check(
        "proposed_fixture_length",
        c["body_length_m"],
        a["fixture_length_m"],
        "m",
        "20m assembly fixture reservation only; origin, capacity, stiffness and anchorage unknown.",
    )
    check(
        "proposed_fixture_payload",
        gross_mass,
        a["fixture_payload_kg"],
        "kg",
        "25t placeholder assembly fixture payload is not offered rated equipment; total suspended load/lifting plan unaccepted.",
    )
    for identifier, basis in [
        (
            "end_load_transfer_and_stiffness_geometry",
            "Constant EI extends over the full 16.5/18.5m body, whereas native side and centre members terminate 0.25m and 0.35m before each body end. End framing, load introduction and piecewise stiffness are absent. The beam is a declared analytical abstraction, not verified exact native geometry performance.",
        ),
        (
            "bolster_underfloor_gauge_and_source_compatibility",
            "Proposed bolster is below the longitudinal members. Its vertical placement, suspension travel, floor height and swept gauge are not reconciled with the complete source assembly; source side-depth alone does not demonstrate source compatibility.",
        ),
        (
            "accepted_materials_and_rail_loads",
            "Certified grade/subgrade/through-thickness, minimum properties by thickness and temperature, AW3/crash/track-twist/braking/fatigue load combinations and authority acceptance missing.",
        ),
        (
            "lateral_torsional_and_connection_stability",
            "Lateral-torsional buckling, local crippling, connection eccentricity/prying, floor discontinuities, elastic load sharing and full 3D nonlinear model unverified.",
        ),
        (
            "qualified_plate_splices_and_welds",
            "All long-plate segment boundaries require detailed groove, stagger/avoidance of stress hotspots, fatigue class, WPS/PQR, distortion and NDT acceptance; no butt weld is treated as qualified by geometry.",
        ),
        (
            "bogie_mating_interface_and_bolt_qualification",
            "Bogie mating pad/bolt supplier drawing, bolt grade/pretension/slip/fatigue/bearing/net section, pad bending, prying and rotation remain unknown.",
        ),
        (
            "machine_and_stock_order_configuration",
            "Dalzell lead does not establish live plate supply or UK melt origin. Offered XP4000 power source, full nest load, plate flatness, supplier samples and tolerance capability absent.",
        ),
        (
            "complete_assembled_mass_and_fastener_origin",
            "Net plate/RHS geometry mass includes finished holes, but bolt/nut/washer, deposited weld metal, coating and remaining vehicle masses are not modeled. Full as-built mass/CG, certified property class, M27 availability where proposed, offered fastener geometry and British manufacturing origin remain unconfirmed.",
        ),
        (
            "vehicle_system_and_mass_closure",
            "All gross proposed steel was added to the original car load. Replacement delta, certified axle ratings, CG, crashworthiness, route gauge, doors, floor, traction, brakes, electrical/fire systems and first article remain open.",
        ),
    ]:
        check(identifier, None, None, "not evaluated", basis)
    payload = json.dumps(
        [c["configuration_id"], v], sort_keys=True, separators=(",", ":")
    )
    identity = "mechanical-detail-" + hashlib.sha256(payload.encode()).hexdigest()[:14]
    failures = [x["id"] for x in checks if x["state"] == "fail"]
    unknown = [x["id"] for x in checks if x["state"] == "unknown"]
    parts = geometry["parts"]
    _assign_material_requests(
        parts,
        m["designation_requested"],
        cfg["bolt_request"]["property_class_requested"],
    )
    return dict(
        id=identity,
        candidate_family="connected-underframe-bolster",
        configuration_id=c["configuration_id"],
        work_package_ids=list(c["work_package_ids"]),
        component_ids=(
            ["LM3-BDY-P010", "LM3-BDY-P020", "LM3-BDY-P021", "LM3-BDY-P030"]
            if c["configuration_id"] == "LM3"
            else ["sixcar-proposed-underframe", "sixcar-proposed-bolster"]
        ),
        interfaces=[
            dict(
                id="frame-to-bogie-pad", state="unknown", revision="proposed-unaccepted"
            ),
            dict(
                id="frame-to-floor-gauge",
                state="unknown",
                revision="proposed-unaccepted",
            ),
            dict(
                id="plate-to-weld-process",
                state="unknown",
                revision="proposed-unaccepted",
            ),
        ],
        variables=v,
        variable_units=cfg["units"],
        checks=checks,
        objectives=dict(mass_kg=gross_mass, cost=None),
        geometry=geometry,
        materials=dict(
            request=m["designation_requested"],
            fastener_request=cfg["bolt_request"],
            assumed_properties=m,
            accepted=False,
        ),
        connections=dict(
            load_path=[
                "Body UDL and full proposed steel -> three longitudinal members",
                "Rigid transverse compatibility hypothesis -> EI shares at two bogie stations",
                "Side reactions -> transverse I bolsters; centre reaction -> central pad",
                "Stiffeners/flange-web welds -> pads in bearing -> unverified bogie mating body",
                "Horizontal inertia and overturning -> two-row hold-down bolt groups",
            ],
            bolts_per_support=n,
            bolt_nominal_diameter_m=v["bolt_diameter_m"],
            bolt_tensile_area_m2=bolt_area,
            requested_bolt_property_class=cfg["bolt_request"][
                "property_class_requested"
            ],
            bolt_coarse_pitch_m=cfg["bolt_request"]["coarse_pitch_m"][bolt_key],
            bolt_order_grade_origin_and_clearance_accepted=False,
            bolt_tension_per_bolt_n=tension,
            bolt_shear_per_bolt_n=bolt_shear,
            weld_throat_m=v["weld_throat_m"],
            vertical_reactions_n=beam["reactions_n"],
            longitudinal_reaction_shares=shares,
            qualified=False,
        ),
        metrics=dict(
            proposed_gross_addition_per_car_kg=gross_mass,
            modeled_car_mass_kg=c["source_car_mass_kg"] + gross_mass,
            modeled_car_force_n=force,
            beam=beam,
            member_stresses_pa=stress,
            bolster_stress_pa=bolster_stress,
            bolster_tip_deflection_m=bolster_delta,
            maximum_actual_crossbearer_pitch_m=pitch_actual,
            plate_piece_count=len(flat),
            butt_interfaces_per_longitudinal_plate=max(
                0,
                math.ceil(c["side_member_length_m"] / v["maximum_stock_piece_length_m"])
                - 1,
            ),
        ),
        manufacturing=dict(
            bom=[
                dict(
                    part_id=p["id"],
                    material_request=p["material_request"],
                    material_request_accepted=False,
                    quantity=1,
                    shape=p["kind"],
                    size_m=p["size_m"],
                    net_part_mass_kg=_volume(p) * m["density_kg_m3"],
                    stock_blank_mass_kg=math.prod(p["size_m"]) * m["density_kg_m3"],
                    cutting_route=(
                        "flat plate profile and finish holes"
                        if p["kind"] == "box"
                        else "cut purchased or fabricated sharp-corner RHS; exact mill geometry unknown"
                    ),
                )
                for p in parts
            ],
            datums=[
                dict(
                    id="A",
                    definition="Two machined bogie support pad lower faces; common plane, not raw welded flange",
                ),
                dict(
                    id="B",
                    definition="Longitudinal vehicle centre plane through support pad centre marks",
                ),
                dict(
                    id="C", definition="Forward bogie support station transverse plane"
                ),
            ],
            tolerances=dict(
                state="proposed-unaccepted",
                support_face_coplanarity_m=0.0005,
                support_station_distance_m=0.001,
                bolt_hole_position_relative_to_A_B_C_m=0.00025,
                cut_profile_allowance_m=0.003,
                exact_machine_capability_demonstrated=False,
            ),
            sequence=[
                "Obtain certified stock/heat trace and accepted drawings; dry nest to verify sheet footprint and total bed load.",
                "Profile segmented plates on UK-manufactured XP4000 lead only where dimensions pass; leave 3mm finish allowance at datum/bolt interfaces.",
                "Prepare and qualify transverse butt joints; join long strips with controlled sequence before I/box assembly. Inspect every research splice before closing box.",
                "Assemble on proposed 20m datum fixture; fit centre-box internal diaphragms before closing top. Weld opposite seams in a balanced sequence and record distortion.",
                "Fit side stiffener halves and transverse bolsters; keep pad interfaces as machining allowance until weld inspection and dimensional survey.",
                "Machine pads to common datum A with portable milling/boring process whose machine, reach and capacity are still unspecified; drill/ream bolt holes from datums B/C. Plasma holes are not accepted finished fatigue holes.",
                "Inspect welds by an approved VT/MT/UT plan, measure complete frame datums, trial fit bogie mating parts, conduct approved proof/fatigue/first-article programme before release.",
            ],
            machine_leads=cfg["supplier_evidence"],
            fixture=dict(
                size_m=[a["fixture_length_m"], a["fixture_width_m"]],
                payload_reservation_kg=a["fixture_payload_kg"],
                rated_capacity_accepted=False,
            ),
            released=False,
        ),
        source_sha256=dict(c["source_sha256"]),
        basis=dict(
            configuration=c["envelope_basis"],
            loading=c["load_basis"],
            source_force_gravity_m_s2=c["source_force_gravity_m_s2"],
            proposed_added_mass_gravity_m_s2=a["added_mass_gravity_m_s2"],
            rigid_transverse_compatibility_accepted=False,
            no_original_structure_mass_subtracted=True,
        ),
        next_actions=["Repair local check: " + x for x in failures]
        + ["Resolve qualification gate: " + x for x in unknown],
        local_calculated_checks_passed=not failures,
        failed_check_ids=failures,
        unknown_check_ids=unknown,
        accepted_loading=False,
        engineering_design_complete=False,
        manufacturing_release=False,
        physical_release=False,
    )


def _repair_proposals(candidate, context):
    """Targeted neighbouring edits driven by the present failed checks only.

    Multi-variable repairs increase required connected plate/weld dimensions
    together; independent thickness/depth alternatives remain separate branches.
    Every child is re-evaluated, including increased self-weight and new failures.
    """
    cfg = _inputs()
    bounds = cfg["bounds"]
    v = candidate["variables"]
    failed = {name.split("/", 1)[-1] for name in candidate["failed_check_ids"]}
    proposals = []

    def changed(keys, reason):
        out = dict(v)
        for key in keys:
            choices = bounds[key]
            idx = choices.index(v[key])
            if idx + 1 < len(choices):
                out[key] = choices[idx + 1]
        if out != v:
            proposals.append(dict(variables=out, reason=reason))

    if failed & {
        "global_service_deflection",
        "gross_member_normal_stress",
        "side_web_elastic_plate_buckling",
    }:
        changed(
            ["side_depth_m", "web_thickness_m"],
            "Increase side depth/web together after stiffness or plate-stress failure; retain any source-envelope conflict.",
        )
        changed(
            ["plate_thickness_m", "spine_wall_m"],
            "Increase flange/spine thickness inside current outer envelopes; recompute all added mass and reactions.",
        )
    if "bolster_bending" in failed or "bolster_tip_deflection" in failed:
        changed(
            ["bolster_depth_m"],
            "Increase transverse bolster depth after local transfer stiffness/strength failure.",
        )
    if (
        "intersection_weld_nominal_shear" in failed
        or "longitudinal_flange_weld_shear_flow" in failed
    ):
        changed(
            [
                "weld_throat_m",
                "plate_thickness_m",
                "web_thickness_m",
                "spine_wall_m",
                "diaphragm_thickness_m",
            ],
            "Increase weld and connected thin plates together, keeping weld-size feasibility coupled to self-weight.",
        )
    if "weld_size_thinner_plate" in failed:
        changed(
            [
                "plate_thickness_m",
                "web_thickness_m",
                "spine_wall_m",
                "diaphragm_thickness_m",
            ],
            "Thicker connected plates required for proposed throat; increasing weld alone would worsen failure.",
        )
    if "support_diaphragm_nominal_compression" in failed:
        changed(
            ["diaphragm_thickness_m"],
            "Increase support load-introduction plate thickness after nominal compression failure.",
        )
    if "support_bolt_combined_nominal_stress" in failed:
        changed(
            ["bolt_diameter_m"],
            "Increase bolt tensile area after overturning/shear demand failure; recalculate access and net pad area.",
        )
        changed(
            ["bolts_per_support"],
            "Try additional bolts independently; retain socket-spacing failure if group becomes crowded.",
        )
    if "socket_neighbour_access" in failed and v["bolts_per_support"] > 4:
        out = dict(v)
        out["bolts_per_support"] = 4
        proposals.append(
            dict(
                variables=out,
                reason="Remove crowded extra row and retain/recompute per-bolt demand; diameter must address strength separately.",
            )
        )
    if failed & {
        "crossbearer_floor_tributary_stress",
        "crossbearer_floor_tributary_deflection",
    }:
        choices = bounds["crossbearer_pitch_m"]
        idx = choices.index(v["crossbearer_pitch_m"])
        if idx > 0:
            out = dict(v)
            out["crossbearer_pitch_m"] = choices[idx - 1]
            proposals.append(
                dict(
                    variables=out,
                    reason="Reduce actual tributary floor-bearer spacing after local stress/deflection failure; include added bearer mass.",
                )
            )
    if "xp4000_plate_length" in failed:
        choices = bounds["maximum_stock_piece_length_m"]
        idx = choices.index(v["maximum_stock_piece_length_m"])
        if idx > 0:
            out = dict(v)
            out["maximum_stock_piece_length_m"] = choices[idx - 1]
            proposals.append(
                dict(
                    variables=out,
                    reason="Shorten stock pieces to fit published 4m cutting bed; preserve new butt joints as an unknown qualification gate.",
                )
            )
    unique = {json.dumps(p["variables"], sort_keys=True): p for p in proposals}
    return list(unique.values())


def propose(candidate, context):
    """Return plain bounded variable dictionaries for an external orchestrator."""
    return [p["variables"] for p in _repair_proposals(candidate, context)]


def model_definition(candidate):
    """Exact proposed cut plate geometry, not supplier/internal vehicle geometry."""
    return dict(
        id=candidate["id"],
        parts=deepcopy(candidate["geometry"]["parts"]),
        mass_kg=candidate["objectives"]["mass_kg"],
        geometry_basis="Research connected frame plate definition with sharp corners and finished pad holes only. Bolts, threads, weld beads/grooves, fillet radii, prying and bogie internals omitted; no production release.",
        configuration_id=candidate["configuration_id"],
        manufacturing_release=False,
        physical_release=False,
    )


def _score(candidate):
    """Research prioritisation within one configuration, never a release score."""
    excess = sum(
        max(0.0, check["value"] / check["limit"] - 1)
        for check in candidate["checks"]
        if check["state"] == "fail"
        and isinstance(check["value"], (float, int))
        and isinstance(check["limit"], (float, int))
        and check["limit"] > 0
    )
    return (
        len(candidate["failed_check_ids"]),
        excess,
        candidate["objectives"]["mass_kg"],
        candidate["id"],
    )


def run(output=None):
    cfg = _inputs()
    cases = contexts()
    all_candidates = []
    histories = []
    selections = []
    for ctx in cases:
        limit = cfg["termination"]["maximum_candidates_per_configuration"]
        initial = assess(seed(ctx), ctx)
        initial.update(
            parent_id=None,
            round=0,
            repair_reason="Initial connected assembly within existing LM3 side-depth envelope; distinct six-car hypothesis evaluated independently.",
        )
        records = [initial]
        seen = {initial["id"]}
        frontier = [initial]
        for round_number in range(1, cfg["termination"]["maximum_rounds"] + 1):
            children = []
            # Least failed research checks first, but never erase failed parents.
            for parent in sorted(frontier, key=_score):
                for repair in _repair_proposals(parent, ctx):
                    reason = repair["reason"]
                    child = assess(repair["variables"], ctx)
                    if child["id"] in seen:
                        continue
                    if len(records) >= limit:
                        break
                    child.update(
                        parent_id=parent["id"], round=round_number, repair_reason=reason
                    )
                    seen.add(child["id"])
                    records.append(child)
                    children.append(child)
                if len(records) >= limit:
                    break
            if not children or len(records) >= limit:
                break
            # Three active feedback branches; alternatives are retained in records.
            frontier = sorted(children, key=_score)[:3]
        ranked = sorted(records, key=_score)
        proposal = ranked[0]
        selections.append(
            dict(
                configuration_id=ctx["configuration_id"],
                candidate_id=proposal["id"],
                purpose="Fewest failed checks, then summed relative exceedance, then gross mass within this configuration only; review proposal, not an engineering solution or production selection.",
                all_calculated_checks_passed=proposal["local_calculated_checks_passed"],
                accepted=False,
            )
        )
        histories.append(
            dict(
                configuration_id=ctx["configuration_id"],
                evaluations=len(records),
                rounds=max(x["round"] for x in records),
                termination_reason=(
                    "candidate_budget_reached"
                    if len(records) >= limit
                    else (
                        "round_budget_reached"
                        if max(x["round"] for x in records)
                        >= cfg["termination"]["maximum_rounds"]
                        else "active_feedback_frontier_exhausted"
                    )
                ),
                remaining_failed_checks=proposal["failed_check_ids"],
                remaining_unknown_checks=proposal["unknown_check_ids"],
                completed_design=False,
                full_cartesian_domain_exhausted=False,
                active_frontier_width=3,
            )
        )
        all_candidates.extend(records)
    result = dict(
        schema="osr-feedback-mechanical-detail/1",
        configuration_contexts=cases,
        candidates=all_candidates,
        proposed_review_candidates=selections,
        iteration_history=histories,
        coverage=dict(
            work_package_ids=sorted({p for x in cases for p in x["work_package_ids"]}),
            representative_assemblies="One connected underframe/bolster assembly per distinct configuration; no claim to solve the complete 120-part vehicle or all 34 mechanical packages.",
            other_mechanical_packages="Remain explicit in master system coverage; purchased equipment/interface investigations are not replaced by this frame model.",
        ),
        technical_references=cfg["technical_references"],
        supplier_evidence=cfg["supplier_evidence"],
        candidate_state_counts=dict(
            Counter(
                "local-fail" if x["failed_check_ids"] else "local-pass-unqualified"
                for x in all_candidates
            )
        ),
        manufacturing_release=False,
        physical_release=False,
        engineering_design_complete=False,
    )
    if output is not None:
        path = Path(output)
        path.mkdir(parents=True, exist_ok=True)
        (path / "mechanical-detail.json").write_text(
            json.dumps(result, sort_keys=True, indent=2) + "\n"
        )
        for selection in selections:
            row = next(
                x for x in all_candidates if x["id"] == selection["candidate_id"]
            )
            (path / (row["id"] + "-model.json")).write_text(
                json.dumps(model_definition(row), sort_keys=True, indent=2) + "\n"
            )
    return result
