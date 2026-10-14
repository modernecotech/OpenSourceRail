"""Bounded dimensional DFM rules, never production or physical qualification.

Optional ``manufacturing_plan`` inputs belong to the dimensional definition:
part_rules, tool_envelopes, removal_paths, tolerance_stacks and tooling. Every
constraint needs a basis_reference. References identify inputs; their presence
does not verify a supplier, workshop, measured tolerance or inspection record.
Sweeps are conservative axis-aligned bounding boxes in the assembly frame.
Intersection means the proposed envelope is not demonstrated clear, rather than
an assertion that two curved solids physically collide.
"""

from itertools import product
import math

from .contracts import fingerprint


def number(value, name, *, minimum=0):
    if type(value) not in (int, float) or not math.isfinite(value) or value < minimum:
        raise ValueError(f"finite {name} >= {minimum} required")
    return value


def vector(value, name):
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f"three {name} coordinates required")
    return [number(v, name, minimum=-float("inf")) for v in value]


def bounds(value):
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError("lower and upper assembly bounds required")
    lo, hi = (vector(v, "bounds") for v in value)
    if any(a >= b for a, b in zip(lo, hi)):
        raise ValueError("positive box dimensions required")
    return [lo, hi]


def _primitive_bounds(p):
    kind = p["kind"]
    c = p["centre_m"]
    if kind in {"box", "plate", "perforated-plate"}:
        half = [v / 2 for v in p["dimensions_m"]]
        return [[c[i] - half[i] for i in range(3)], [c[i] + half[i] for i in range(3)]]
    if kind in {"tube", "cylinder", "perforated-cylinder"}:
        half = [p["radius_m"]] * 3
        half["xyz".index(p["axis"])] = p["length_m"] / 2
        return [[c[i] - half[i] for i in range(3)], [c[i] + half[i] for i in range(3)]]
    if kind == "curved-layer":
        a, b = p["theta_start"], p["theta_end"]
        angles = [a, b]
        # Include every sin/cos extremum; never approximate curvature with a chord.
        if b - a >= 2 * math.pi:
            angles += [0, math.pi / 2, math.pi, 3 * math.pi / 2]
        else:
            angles += [
                k * math.pi / 2
                for k in range(
                    math.ceil(a * 2 / math.pi), math.floor(b * 2 / math.pi) + 1
                )
            ]
        points = [
            [c[0] + x, c[1] + r * math.sin(t), c[2] + r * math.cos(t)]
            for x, r, t in product(
                (-p["length_m"] / 2, p["length_m"] / 2),
                (p["radius_m"] + p["z_lower_m"], p["radius_m"] + p["z_upper_m"]),
                angles,
            )
        ]
        return _union(points)
    raise ValueError("unsupported manufacturing primitive")


def _union(points):
    return [
        [min(p[i] for p in points) for i in range(3)],
        [max(p[i] for p in points) for i in range(3)],
    ]


def part_bounds(part):
    spec = part.get("manufacturing") or {}
    if not spec.get("primitives"):
        return None
    from osr_mech.automated_geometry import validate_spec

    validate_spec(spec)
    placement = part.get("placement") or {}
    rotation = placement.get("rotation", [[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    translation = placement.get("translation_m", [0, 0, 0])
    points = []
    for primitive in spec["primitives"]:
        lo, hi = _primitive_bounds(primitive)
        for point in product(*zip(lo, hi)):
            points.append(
                [
                    sum(rotation[i][j] * point[j] for j in range(3)) + translation[i]
                    for i in range(3)
                ]
            )
    return _union(points)


def _thickness(p):
    if p["kind"] in {"box", "plate", "perforated-plate"}:
        return min(p["dimensions_m"])
    if p["kind"] == "curved-layer":
        return p["z_upper_m"] - p["z_lower_m"]
    if p["kind"] == "tube":
        return p["radius_m"] - p["inner_radius_m"]
    return None


def _state(passed):
    return "passed" if passed else "failed"


def _intersects(a, b):
    return all(max(a[0][i], b[0][i]) < min(a[1][i], b[1][i]) for i in range(3))


def evaluate(model):
    physical = model.get("parts", model.get("instances", []))
    by_id = {p["id"]: p for p in physical}
    envelopes = {p["id"]: part_bounds(p) for p in physical}
    plan = model.get("manufacturing_plan", {})
    if not isinstance(plan, dict):
        raise ValueError("manufacturing plan must be an object")
    if plan and plan.get("schema") != "osr-manufacturing-plan/1":
        raise ValueError("versioned manufacturing plan required")
    allowed = {
        "schema",
        "part_rules",
        "tool_envelopes",
        "removal_paths",
        "tolerance_stacks",
        "tooling",
    }
    if set(plan) - allowed:
        raise ValueError("unknown manufacturing plan fields")
    for key in allowed - {"schema"}:
        rows = plan.get(key, [])
        if not isinstance(rows, list) or len(rows) > 1024:
            raise ValueError("bounded manufacturing rule list required")
    checks = []

    def emit(identifier, state, **data):
        checks.append(dict(id=identifier, state=state, **data))

    for p in physical:
        primitives = (p.get("manufacturing") or {}).get("primitives", [])
        minimum = (p.get("manufacturing_limits") or {}).get("minimum_wall_m")
        walls = [
            t for primitive in primitives if (t := _thickness(primitive)) is not None
        ]
        if minimum is None or not walls:
            emit(
                p["id"] + "/minimum-wall",
                "unknown",
                physical_id=p["id"],
                basis="no applicable dimensional minimum supplied",
            )
        else:
            number(minimum, "minimum wall", minimum=1e-12)
            emit(
                p["id"] + "/minimum-wall",
                _state(min(walls) >= minimum),
                physical_id=p["id"],
                observed_minimum_m=min(walls),
                required_minimum_m=minimum,
                basis="primitive wall/ply dimensions against the declared research limit",
            )

    def input_row(row, required):
        if (
            not isinstance(row, dict)
            or set(row) != required
            or not isinstance(row.get("basis_reference"), str)
            or not row["basis_reference"].strip()
        ):
            raise ValueError(
                "exact manufacturing rule fields and basis reference required"
            )
        if row.get("physical_id") not in by_id:
            raise ValueError("manufacturing rule refers to absent physical part")

    for row in plan.get("part_rules", []):
        input_row(
            row, {"physical_id", "stock_bounds_m", "minimum_wall_m", "basis_reference"}
        )
        stock = vector(row["stock_bounds_m"], "stock")
        if any(v <= 0 for v in stock):
            raise ValueError("positive stock dimensions required")
        lohi = envelopes[row["physical_id"]]
        if lohi is None:
            emit(
                row["physical_id"] + "/stock-process",
                "unknown",
                physical_id=row["physical_id"],
                basis="manufacturing primitives absent; stock fit cannot be assessed",
            )
            continue
        minimum = number(row["minimum_wall_m"], "minimum wall", minimum=1e-12)
        walls = [
            t
            for p in by_id[row["physical_id"]]["manufacturing"]["primitives"]
            if (t := _thickness(p)) is not None
        ]
        # Fixed supplied stock orientation; rotated/nested cutting needs its own plan.
        dimensions = [lohi[1][i] - lohi[0][i] for i in range(3)] if lohi else None
        ok = (
            dimensions is not None
            and all(a <= b for a, b in zip(dimensions, stock))
            and bool(walls)
            and min(walls) >= minimum
        )
        emit(
            row["physical_id"] + "/stock-process",
            _state(ok),
            dimensions_m=dimensions,
            physical_id=row["physical_id"],
            stock_bounds_m=stock,
            minimum_wall_m=minimum,
            basis_reference=row["basis_reference"],
        )

    for key in ("tool_envelopes", "removal_paths"):
        for index, row in enumerate(plan.get(key, [])):
            fields = {"physical_id", "bounds_m", "keepout_part_ids", "basis_reference"}
            if key == "removal_paths":
                fields |= {"translation_m"}
            input_row(row, fields)
            box = bounds(row["bounds_m"])
            keepouts = row["keepout_part_ids"]
            if (
                not isinstance(keepouts, list)
                or not keepouts
                or any(not isinstance(p, str) for p in keepouts)
                or len(keepouts) != len(set(keepouts))
                or not set(keepouts) <= set(by_id)
                or row["physical_id"] in keepouts
            ):
                raise ValueError(
                    "explicit distinct keepout parts required; moved part cannot obstruct itself"
                )
            if key == "removal_paths":
                actual = envelopes[row["physical_id"]]
                if actual is None or any(
                    box[0][i] > actual[0][i] or box[1][i] < actual[1][i]
                    for i in range(3)
                ):
                    raise ValueError(
                        "removal envelope must contain the actual installed part"
                    )
                shift = vector(row["translation_m"], "removal translation")
                if not any(shift):
                    raise ValueError("nonzero removal translation required")
                box = [
                    [box[0][i] + min(0, shift[i]) for i in range(3)],
                    [box[1][i] + max(0, shift[i]) for i in range(3)],
                ]
            missing = [p for p in keepouts if envelopes[p] is None]
            conflicts = [
                p
                for p in keepouts
                if envelopes[p] is not None and _intersects(box, envelopes[p])
            ]
            state = "failed" if conflicts else "unknown" if missing else "passed"
            emit(
                f"{row['physical_id']}/{key}/{index}",
                state,
                bounds_m=box,
                conflicting_keepouts=conflicts,
                unmodelled_keepouts=missing,
                basis_reference=row["basis_reference"],
                physical_id=row["physical_id"],
                scope="conservative declared keepouts only; tool function, vehicle surroundings and actual service procedure remain unqualified",
            )

    for index, row in enumerate(plan.get("tolerance_stacks", [])):
        input_row(
            row,
            {
                "physical_id",
                "nominal_clearance_m",
                "required_clearance_m",
                "contributors",
                "basis_reference",
            },
        )
        clearance = number(row["nominal_clearance_m"], "nominal clearance")
        required = number(row["required_clearance_m"], "required clearance")
        contributors = row["contributors"]
        if not isinstance(contributors, list) or not 1 <= len(contributors) <= 64:
            raise ValueError("bounded nonempty tolerance contributors required")
        if any(
            not isinstance(c, dict)
            or set(c) != {"physical_id", "plus_minus_m"}
            or c["physical_id"] not in by_id
            for c in contributors
        ):
            raise ValueError("tolerance contributors must reference actual parts")
        if len({c["physical_id"] for c in contributors}) != len(contributors):
            raise ValueError("tolerance contributor must be counted once")
        total = sum(number(c["plus_minus_m"], "tolerance") for c in contributors)
        emit(
            f"{row['physical_id']}/tolerance/{index}",
            _state(clearance - total >= required),
            physical_id=row["physical_id"],
            worst_case_clearance_m=clearance - total,
            required_clearance_m=required,
            tolerance_sum_m=total,
            basis_reference=row["basis_reference"],
            basis="worst-case arithmetic stack; no independent-distribution/RSS assumption",
        )

    tooling = []
    for row in plan.get("tooling", []):
        if (
            not isinstance(row, dict)
            or set(row)
            != {"id", "kind", "count", "physical_part_ids", "basis_reference"}
            or not isinstance(row["id"], str)
            or not row["id"].strip()
            or row["kind"] not in {"mould", "fixture"}
            or type(row["count"]) is not int
            or not 1 <= row["count"] <= 1024
            or not isinstance(row["basis_reference"], str)
            or not row["basis_reference"].strip()
        ):
            raise ValueError(
                "identified positive bounded mould/fixture count and basis required"
            )
        if (
            not isinstance(row["physical_part_ids"], list)
            or not row["physical_part_ids"]
            or any(not isinstance(p, str) for p in row["physical_part_ids"])
            or not set(row["physical_part_ids"]) <= set(by_id)
            or len(row["physical_part_ids"]) != len(set(row["physical_part_ids"]))
        ):
            raise ValueError("tooling must map distinct actual physical parts")
        if row["id"] in {t["id"] for t in tooling}:
            raise ValueError("tooling identity must be unique")
        tooling.append({**row, "qualified_process": False})
    states = [c["state"] for c in checks]
    supplied = {key: len(plan.get(key, [])) for key in allowed - {"schema"}}
    return dict(
        schema="osr-dimensional-manufacturing-checks/1",
        physical_definition_sha256=fingerprint(model),
        checks=checks,
        tooling=tooling,
        supplied_rule_counts=supplied,
        state=(
            "failed"
            if "failed" in states
            else (
                "unknown"
                if "unknown" in states or any(v == 0 for v in supplied.values())
                else "passed"
            )
        ),
        complete_vehicle_keepout_coverage=False,
        source_references_verified=False,
        qualified_workshop=False,
        production_released=False,
        physical_release=False,
    )


def panel_details(model):
    parameters = model.get("panel_parameters")
    network = model.get("support_network")
    if not parameters or not network:
        return None
    parts = model["parts"]
    ids = {p["id"] for p in parts}
    width, height = parameters["width_m"], parameters["height_m"]
    crown = parameters["crown_m"]
    if crown:
        from osr_mech.rolling_stock.composite_panels import roof_arc

        height = roof_arc(height, crown)["arc_length_m"]
    aperture_length = sum(
        2 * ((x1 - x0) + (y1 - y0)) for x0, y0, x1, y1 in parameters["holes"]
    )
    clips = [p for p in parts if "-clip-" in p["id"] and "-clip-bolt-" not in p["id"]]
    bolts = [p for p in parts if "-clip-bolt-" in p["id"]]
    missing_heads = [
        p["id"]
        for p in bolts
        if not any(q["id"] == "head" for q in p["manufacturing"]["primitives"])
    ]
    mass_groups = {}
    for p in parts:
        identifier = p["id"]
        group = (
            "clip_bolts"
            if "-clip-bolt-" in identifier
            else (
                "clips"
                if "-clip-" in identifier
                else (
                    "frame_fasteners"
                    if "-fastener-" in identifier
                    else (
                        "brackets"
                        if "-bracket-" in identifier
                        else (
                            "inserts"
                            if identifier.startswith("insert-")
                            else (
                                "potting"
                                if identifier.startswith("potting-")
                                else (
                                    "rails"
                                    if identifier in {r["id"] for r in network["rails"]}
                                    else (
                                        "aperture_frame"
                                        if identifier.startswith("aperture-")
                                        else "panel_material_regions"
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
        entry = mass_groups.setdefault(group, dict(quantity=0, defined_mass_kg=0))
        entry["quantity"] += 1
        entry["defined_mass_kg"] += p["properties"]["mass_kg"]
    return dict(
        schema="osr-panel-installed-details/1",
        defined_clip_count=len(clips),
        defined_clip_bolt_count=len(bolts),
        attachment_site_count=network["panel_attachment_count"],
        defined_insert_count=len([i for i in ids if i.startswith("insert-")]),
        defined_mass_groups=mass_groups,
        defined_inventory_mass_kg=sum(
            g["defined_mass_kg"] for g in mass_groups.values()
        ),
        perimeter_seal=dict(
            required_path_length_m=2 * (width + height) + aperture_length,
            aperture_path_length_m=aperture_length,
            profile=None,
            material=None,
            installed_mass_kg=None,
            basis="developed perimeter including aperture; splice/compression and frame gap details remain open",
        ),
        missing_clip_head_part_ids=missing_heads,
        thread_engagement_m=None,
        locking_inventory=None,
        secondary_retention=None,
        curved_insert_contact_lands=(
            "unknown"
            if crown
            else "flat insert solids defined; local contact and pull-out remain unqualified"
        ),
        unresolved_allocations=model.get("unresolved_part_allocations", []),
        complete_installed_mass_kg=None,
        complete_installed_kit=False,
        physical_release=False,
        production_released=False,
    )
