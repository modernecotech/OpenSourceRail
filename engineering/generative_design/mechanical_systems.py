"""Bounded, source-bound detailed investigations of every LM3 production package.

Calculations are explicit research models of one named interface/demand. They
retain failed variants and never turn a modelled subset into product acceptance.
No CAD modules are imported: numeric CAD constants are read through a restricted
AST interpreter, avoiding expensive geometry rebuilding and executable imports.
"""

from __future__ import annotations

import ast
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(__file__).with_name("data") / "mechanical-systems.json"
CAT = ROOT / "design/component-catalogue/catalog/buildable-trainset"
CAD = ROOT / "design/component-catalogue/src/osr_mech/rolling_stock"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _number(node, values):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name):
        return values[node.id]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_number(node.operand, values)
    if isinstance(node, ast.BinOp):
        left, right = _number(node.left, values), _number(node.right, values)
        for operator, operation in [
            (ast.Add, lambda: left + right),
            (ast.Sub, lambda: left - right),
            (ast.Mult, lambda: left * right),
            (ast.Div, lambda: left / right),
        ]:
            if isinstance(node.op, operator):
                return operation()
    raise ValueError("not a numeric constant expression")


def constants(paths):
    values = {}
    for path in paths:
        for statement in ast.parse(path.read_text()).body:
            if (
                isinstance(statement, ast.Assign)
                and len(statement.targets) == 1
                and isinstance(statement.targets[0], ast.Name)
            ):
                try:
                    values[statement.targets[0].id] = _number(statement.value, values)
                except (KeyError, ValueError, TypeError, ZeroDivisionError):
                    pass
    return values


def context():
    inputs = json.loads(DATA.read_text())
    source_paths = [
        CAD / "baseline.py",
        CAD / "car_body.py",
        CAD / "sensor_cowl.py",
        CAD / "systems.py",
        CAD / "small_components.py",
        CAD / "bogie/wheelset.py",
        CAD / "bogie/motor.py",
        CAD / "bogie/gearbox.py",
        CAD / "bogie/frame.py",
        CAD / "bogie/suspension.py",
        CAD / "bogie/assembly.py",
        CAD / "trainset.py",
    ]
    manifest = json.loads((CAT / "buildable-trainset-manifest.json").read_text())
    pdr = json.loads((CAT / "production-data-release-register.json").read_text())
    scope = json.loads(
        (ROOT / "engineering/generative_design/data/system-scope.json").read_text()
    )
    anchors = json.loads((CAT / "supplier-anchors.json").read_text())
    trace_path = ROOT / "engineering/industrialisation/vehicle-civil-load-trace.json"
    trace = json.loads(trace_path.read_text())["reference"]
    source_paths += [
        CAD / "product_geometry.py",
        DATA,
        CAT / "buildable-trainset-manifest.json",
        CAT / "production-data-release-register.json",
        ROOT / "engineering/generative_design/data/system-scope.json",
        CAT / "supplier-anchors.json",
        trace_path,
        Path(__file__),
    ]
    return dict(
        inputs=inputs,
        a=inputs["assumptions"],
        c=constants(source_paths[:12]),
        products={
            p["id"]: p for p in manifest["product_items"] + manifest["assemblies"]
        },
        pdr={p["product_id"]: p for p in pdr["products"]},
        scope={p["id"]: p for p in scope["work_packages"]},
        anchors=anchors["anchor"],
        trace=trace,
        source_sha256={str(p.relative_to(ROOT)): digest(p) for p in source_paths},
    )


def legacy_mass(ctx):
    """Force-preserving original 9.81 convention; never a six-car mass."""
    assert ctx["trace"]["axle_count"] == 12
    return sum(x["static_load_kn"] * 1000 / 9.81 for x in ctx["trace"]["axle_pattern"])


def rotation(point, yaw_deg=0, pitch_deg=0, roll_deg=0):
    """Active Rz(yaw) Ry(pitch) Rx(roll), angles in degrees."""
    yaw, pitch, roll = map(math.radians, (yaw_deg, pitch_deg, roll_deg))
    x, y, z = point
    y, z = y * math.cos(roll) - z * math.sin(roll), y * math.sin(roll) + z * math.cos(
        roll
    )
    x, z = x * math.cos(pitch) + z * math.sin(pitch), -x * math.sin(
        pitch
    ) + z * math.cos(pitch)
    return [
        x * math.cos(yaw) - y * math.sin(yaw),
        x * math.sin(yaw) + y * math.cos(yaw),
        z,
    ]


def articulation_demands(ctx, variables):
    """Exact rigid transformations of all eight gangway envelope corners."""
    c = ctx["c"]
    length = c["ARTICULATION_MODULE_LENGTH_MM"] / 1000
    width = c["ARTICULATION_PASSAGE_WIDTH_MM"] / 1000
    height = 2.0  # research passage envelope: supplier finished height is unclosed
    points = list(
        itertools.product(
            [0, length], [-width / 2, width / 2], [-height / 2, height / 2]
        )
    )
    transformed = [
        rotation(
            p,
            variables.get("yaw_deg", 0),
            variables.get("pitch_deg", 0),
            variables.get("roll_deg", 0),
        )
        for p in points
    ]
    displacement = [math.dist(p, q) for p, q in zip(points, transformed)]
    return dict(
        maximum_corner_displacement_m=max(displacement),
        swept_min_m=[min(p[i] for p in transformed) for i in range(3)],
        swept_max_m=[max(p[i] for p in transformed) for i in range(3)],
        module_length_m=length,
        passage_width_m=width,
        assumed_passage_height_m=height,
        transformed_corners_m=transformed,
    )


def continuous_gangway_longitudinal_bound(ctx):
    """Triangle-inequality bound for the FULL +/-yaw/pitch/roll box.

    For Rz Ry Rx, |Rxx|<=1, |Rxy|<=sin(p)sin(r)+sin(y),
    |Rxz|<=sin(p)+sin(y)sin(r). Multiplication by the three box
    dimensions bounds its longitudinal extent for every intermediate angle.
    """
    c = ctx["c"]
    yaw, pitch, roll = (
        math.radians(c[k])
        for k in [
            "ARTICULATION_YAW_CLEARANCE_DEG",
            "ARTICULATION_PITCH_CLEARANCE_DEG",
            "ARTICULATION_ROLL_CLEARANCE_DEG",
        ]
    )
    return (
        c["ARTICULATION_MODULE_LENGTH_MM"] / 1000
        + c["ARTICULATION_PASSAGE_WIDTH_MM"]
        / 1000
        * (math.sin(pitch) * math.sin(roll) + math.sin(yaw))
        + 2 * (math.sin(pitch) + math.sin(yaw) * math.sin(roll))
    )


def source_spine_dimensions(ctx):
    """Read the centre-spine width from actual _underframe box construction."""
    tree = ast.parse((CAD / "product_geometry.py").read_text())
    function = next(
        n
        for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name == "_underframe"
    )
    widths = []
    for node in ast.walk(function):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_box"
            and node.args
            and isinstance(node.args[0], ast.Tuple)
        ):
            dims = node.args[0].elts
            if (
                len(dims) == 3
                and isinstance(dims[1], ast.Constant)
                and dims[1].value == 220
            ):
                widths.append(dims[1].value / 1000)
    if widths != [0.22]:
        raise ValueError(
            "centre-spine construction changed: review geometric hypothesis"
        )
    envelope = ctx["pdr"]["LM3-BDY-P020"]["design_reference_envelope_mm"]
    return dict(
        length_m=envelope[0] / 1000,
        width_m=widths[0],
        height_m=envelope[2] / 1000,
        representation="Source solid review envelope; analysis proposes a hollow fabricated section, not certified source material or section properties",
    )


def continuous_corner_displacement_bound(ctx):
    """Bound the displacement under ANY signs/intermediate joint angles.

    Rotation distance is at most sum(|yaw|,|pitch|,|roll|); chord distance
    for any corner radius r is <=2r sin(angle_sum/2), for this <pi domain.
    """
    c = ctx["c"]
    radius = math.sqrt(
        (c["ARTICULATION_MODULE_LENGTH_MM"] / 1000) ** 2
        + (c["ARTICULATION_PASSAGE_WIDTH_MM"] / 2000) ** 2
        + 1**2
    )
    angle = sum(
        math.radians(c[k])
        for k in [
            "ARTICULATION_YAW_CLEARANCE_DEG",
            "ARTICULATION_PITCH_CLEARANCE_DEG",
            "ARTICULATION_ROLL_CLEARANCE_DEG",
        ]
    )
    return 2 * radius * math.sin(angle / 2)


def evaluate(family, v, ctx):
    a, c = ctx["a"], ctx["c"]
    metrics, checks, details = {}, [], []

    def check(name, condition, basis):
        checks.append(
            dict(
                id=name,
                status=(
                    "unknown"
                    if condition is None
                    else "passed" if condition else "failed"
                ),
                basis=basis,
            )
        )

    mass = legacy_mass(ctx)
    g = a["gravity_m_s2"]
    bodylength = c["PROMOTED_LIGHT_METRO_CAR_LENGTH_MM"] / 1000
    bodywidth = c["PROMOTED_LIGHT_METRO_CAR_WIDTH_MM"] / 1000
    if family in {"glazing", "door_window", "side_glazing"}:
        if family == "side_glazing":
            # Exact _window_zones construction: two doors per side at +/-L/6.
            # End zones and centre zone differ; calculate the governing width.
            end_zone = (
                bodylength / 3
                - c["DOOR_WIDTH_MM"] / 2000
                - 2 * c["WINDOW_MARGIN_MM"] / 1000
            )
            centre_zone = (
                bodylength / 3
                - c["DOOR_WIDTH_MM"] / 1000
                - 2 * c["WINDOW_MARGIN_MM"] / 1000
            )
            width = max(end_zone, centre_zone)
            height = c["WINDOW_HEIGHT_MM"] / 1000
            metrics.update(
                side_window_zone_widths_m=[end_zone, centre_zone, end_zone],
                pdr_side_window_reference_envelope_m=[
                    x / 1000
                    for x in ctx["pdr"]["LM3-WIN-P010"]["design_reference_envelope_mm"]
                ],
            )
        else:
            width = c["PANORAMIC_GLASS_WIDTH_MM"] / 1000
            height = c["PANORAMIC_GLASS_HEIGHT_MM"] / 1000
        metrics.update(assessed_glass_width_m=width, assessed_glass_height_m=height)
        growth = (
            (a["aluminium_alpha_1_k"] - a["glass_alpha_1_k"])
            * a["temperature_swing_k"]
            * max(width, height)
            / 2
        )
        residual = v["edge_clearance_m"] - a["dimensional_tolerance_m"] - growth
        compression_min = (0.012 - v["seal_gap_m"] - v["seal_gap_tolerance_m"]) / 0.012
        compression_max = (0.012 - v["seal_gap_m"] + v["seal_gap_tolerance_m"]) / 0.012
        inflow = a["rainfall_m_hr"] / 3600 * width * height
        # Two drains with a declared 50% total blockage allowance.
        outflow = (
            2
            * math.pi
            * v["drain_diameter_m"] ** 2
            / 4
            * a["orifice_coefficient"]
            * math.sqrt(2 * g * a["drain_head_m"])
            * (1 - a["drain_blocked_fraction"])
        )
        metrics.update(
            thermal_half_edge_differential_m=growth,
            residual_edge_clearance_m=residual,
            minimum_seal_compression_fraction=compression_min,
            maximum_seal_compression_fraction=compression_max,
            rain_inflow_m3_s=inflow,
            blocked_orifice_capacity_m3_s=outflow,
            pressure_resultant_n=width * height * a["pressure_pa"],
            seal_free_height_m=0.012,
        )
        check(
            "thermal_and_tolerance_clearance",
            residual >= 0,
            "Worst-case frame/glass differential expansion and 1 mm dimensional stack; assumed properties, not a released glass design",
        )
        check(
            "seal_compression",
            compression_min >= a["seal_compression_min"]
            and compression_max <= a["seal_compression_max"],
            "Research 20–35% compression window for a proposed 12 mm seal; supplier compression curve required",
        )
        check(
            "blocked_gravity_drain",
            outflow >= inflow,
            "50 mm/hr incident rainfall, 10 mm head and 50% blockage, Cd0.6 ideal orifices; hoses/vehicle pitch and water test absent",
        )
        if family == "side_glazing":
            proposed_width = v.get(
                "pressure_frame_width_m",
                ctx["pdr"]["LM3-WIN-P010"]["design_reference_envelope_mm"][0] / 1000,
            )
            metrics["proposed_pressure_frame_width_m"] = proposed_width
            check(
                "side_pane_pressure_frame_fit",
                proposed_width >= width + 2 * v["edge_clearance_m"] + 0.08,
                "Actual CAD3600mm governing pane plus edge gaps and40mm profile each side. Existing1650mm PDR frame FAILS.",
            )
            check(
                "existing_side_frame_envelope",
                proposed_width
                <= ctx["pdr"]["LM3-WIN-P010"]["design_reference_envelope_mm"][0] / 1000,
                "3750mm replacement pressure-frame proposal fails unchanged1650mm PDR envelope; revise frame/body opening and all linked products before adoption.",
            )
        else:
            proposed_height = v.get(
                "carrier_height_m",
                ctx["pdr"]["LM3-FAS-P010"]["design_reference_envelope_mm"][2] / 1000,
            )
            actual_height = (c["PANORAMIC_GLASS_HEIGHT_MM"] + 230) / 1000
            metrics["proposed_carrier_height_m"] = proposed_height
            check(
                "front_carrier_geometry_fit",
                proposed_height >= actual_height,
                "Actual CAD carrier outer height2010mm must fit proposed envelope; existing1780mm PDR height FAILS.",
            )
            check(
                "existing_front_carrier_envelope",
                proposed_height
                <= ctx["pdr"]["LM3-FAS-P010"]["design_reference_envelope_mm"][2] / 1000,
                "2100mm replacement carrier proposal fails unchanged1780mm PDR height; cowl/carrier/frame geometry and source envelopes need a new accepted revision.",
            )
        details = [
            dict(
                part="proposed-header-or-sill",
                quantity=2,
                cut_length_m=width + 2 * v["edge_clearance_m"] + 0.08,
            ),
            dict(
                part="proposed-stile",
                quantity=2,
                cut_length_m=height + 2 * v["edge_clearance_m"],
            ),
            dict(
                part="proposed-drain", quantity=2, bore_diameter_m=v["drain_diameter_m"]
            ),
        ]
        check(
            "glass_retention_and_seal_qualification",
            None,
            "Glass stack/impact, setting blocks, frame/bond, fire, retention fasteners and water test unavailable; PDR/CAD width discrepancy retained",
        )
    elif family == "lamp":
        lamp_width = c["HEADLIGHT_WIDTH_MM"] / 1000
        lamp_height = c["HEADLIGHT_HEIGHT_MM"] / 1000
        arm = 0.12
        angle = math.atan2(v["aiming_half_travel_m"], arm)
        metrics.update(
            lamp_aperture_m=[lamp_width, lamp_height],
            aiming_half_angle_rad=angle,
            beam_offset_at_25m_m=25 * math.tan(angle),
            rear_service_clearance_m=v["rear_service_clearance_m"],
            lamp_pair_overall_width_m=2 * 0.53 + lamp_width,
        )
        check(
            "cassette_extraction_width",
            v["service_hatch_width_m"] >= lamp_width + 0.04,
            "Proposed extraction aperture at least lamp width plus 20 mm each side; exact lamp depth/connectors remain unknown",
        )
        check(
            "aiming_research_range",
            angle >= math.radians(3),
            "Proposed +/-3 degree aiming geometry on 120 mm adjuster arm; photometric approval not supplied",
        )
        check(
            "rear_tool_access",
            v["rear_service_clearance_m"] >= 0.08,
            "OSR 80 mm axial tool/service allowance, pending full swept removal trial",
        )
        details = [
            dict(
                part="research-lamp-plate",
                width_m=lamp_width + 0.06,
                height_m=lamp_height + 0.06,
                thickness_m=0.004,
                holes_xy_m=[
                    [0.02, 0.02],
                    [lamp_width + 0.04, 0.02],
                    [0.02, lamp_height + 0.04],
                    [lamp_width + 0.04, lamp_height + 0.04],
                ],
                hole_diameter_m=0.0065,
            )
        ]
        check(
            "cowl_laminate_insert_and_lamp_acceptance",
            None,
            "No laminate allowables, potted-insert pull-out, offered lamp GA, EMC, ingress or photometry accepted",
        )
    elif family == "door":
        aperture = c["DOOR_WIDTH_MM"] / 1000
        leaf = (aperture - 0.03) / 2
        inner = 0.008  # exact CAD leaf-centre offset in _door_leaves
        opening = 2 * min(aperture / 2, inner + v["leaf_travel_m"])
        plug_required = (
            c["DOOR_LEAF_INSET_MM"] - c["DOOR_LEAF_THICKNESS_MM"] / 2
        ) / 1000 + 0.01
        metrics.update(
            clear_opening_m=opening,
            requested_opening_m=aperture,
            leaf_width_m=leaf,
            required_leaf_travel_m=aperture / 2 - inner,
            required_plug_travel_m=plug_required,
            leaf_swept_overall_width_m=2 * (leaf + inner + v["leaf_travel_m"]),
            window_margin_overlap_m=max(
                0, v["leaf_travel_m"] - c["WINDOW_MARGIN_MM"] / 1000
            ),
        )
        check(
            "clear_passage",
            opening >= aperture - 1e-12,
            "Two CAD leaves start 8 mm from centreline; displace to aperture edges",
        )
        check(
            "plug_clears_body",
            v["plug_travel_m"] >= plug_required - 1e-12,
            "CAD inset minus half leaf thickness plus 10 mm research reserve",
        )
        check(
            "complete_door_supplier_qualification",
            None,
            "Operator/track GA, four-shoe tolerance, closing force, obstruction, emergency release, life and safety evidence unaccepted; operator width is not leaf travel capacity",
        )
    elif family == "traction":
        velocity = v["speed_km_hr"] / 3.6
        radius = v["wheel_diameter_m"] / 2
        omega = velocity / radius * v["gear_ratio"]
        power = c["PROMOTED_MOTOR_CONTINUOUS_KW"] * 1000
        torque = power / omega
        axle_force = power * a["gear_efficiency"] / velocity
        heat = power * (1 / a["motor_efficiency"] - 1)
        metrics.update(
            motor_speed_rpm=omega * 60 / (2 * math.pi),
            constant_power_motor_torque_nm=torque,
            axle_torque_nm=torque * v["gear_ratio"] * a["gear_efficiency"],
            six_driven_axle_force_n=6 * axle_force,
            motor_loss_w=heat,
            motor_coolant_flow_kg_s=heat
            / (a["coolant_cp_j_kg_k"] * a["coolant_delta_t_k"]),
            legacy_powered_adhesion_limit_n=mass / 2 * g * a["wheel_rail_mu_research"],
            mechanical_continuous_power_w=power,
        )
        check(
            "research_motor_speed",
            metrics["motor_speed_rpm"] <= a["motor_max_rpm_research"],
            "Compare kinematic RPM with 6000 rpm research ceiling; supplier actual limit/map unaccepted",
        )
        check(
            "legacy_adhesion_sensitivity",
            6 * axle_force <= metrics["legacy_powered_adhesion_limit_n"],
            "Legacy three-car equal mass, half driven axles and mu0.15 sensitivity, not a verified adhesion/traction controller design",
        )
        check(
            "motor_gearbox_and_thermal_qualification",
            None,
            "250kW continuous is a planning assumption despite350kW identifier. Torque-speed map, winding/cooling, coupling, axle load, duty, EMC and gearbox6.5 ratio not released",
        )
    elif family == "running_unit":
        velocity = a["speed_km_hr"] / 3.6
        axle = mass * g / 12
        energy = 0.5 * mass * velocity**2 * v["brake_energy_share"] / 12
        journal = c["AXLE_JOURNAL_DIAMETER_MM"] / 1000
        metrics.update(
            legacy_equal_axle_static_force_n=axle,
            legacy_bearing_static_force_n=axle / 2,
            primary_pack_force_n=axle / 4,
            primary_pack_secant_stiffness_n_m=axle
            / 4
            / v["primary_static_deflection_m"],
            disc_energy_per_stop_j=energy,
            wheel_speed_rpm=velocity / (math.pi * v["wheel_diameter_m"]) * 60,
            wheel_wear_radius_change_m=(
                c["WHEEL_DIAMETER_NEW_MM"] / 1000 - v["wheel_diameter_m"]
            )
            / 2,
            nominal_journal_shear_pa=axle / 2 / (math.pi * journal**2 / 4),
            ideal_stop_distance_m=velocity**2 / (2 * a["braking_deceleration_m_s2"]),
            ideal_stop_time_s=velocity / a["braking_deceleration_m_s2"],
        )
        check(
            "wheel_wear_geometry",
            c["WHEEL_DIAMETER_WORN_MM"] / 1000
            <= v["wheel_diameter_m"]
            <= c["WHEEL_DIAMETER_NEW_MM"] / 1000,
            "Source new/worn diameters; no wheel profile/flange/back-to-back acceptance",
        )
        check(
            "primary_suspension_packaging",
            v["primary_static_deflection_m"] <= c["CHEVRON_HEIGHT_MM"] / 1000 * 0.2,
            "Research maximum compression20% of110mm CAD chevron height, not compound load-deflection acceptance",
        )
        check(
            "rail_running_and_braking_qualification",
            None,
            "Disc thermal mass/friction/cooling, WSP, stopping/parking cases, journal fatigue, bearing L10, certified wheels/axles/spring curves and dynamics absent",
        )
    elif family == "bogie_frame":
        # CAD gearbox is centred at axle, limiting ground clearance when worn.
        worn = c["WHEEL_DIAMETER_WORN_MM"] / 2000
        gear_low = worn - c["GEARBOX_HOUSING_HEIGHT_MM"] / 2000 - v["vertical_motion_m"]
        lateral = (v["frame_width_m"] - c["AXLE_LENGTH_MM"] / 1000) / 2
        metrics.update(
            worn_wheel_gearbox_ground_clearance_m=gear_low,
            frame_to_axle_nominal_half_margin_m=lateral,
            legacy_bogie_static_force_n=mass * g / 6,
            cad_frame_m=[
                c["FRAME_LENGTH_MM"] / 1000,
                c["FRAME_WIDTH_MM"] / 1000,
                c["FRAME_HEIGHT_MM"] / 1000,
            ],
            pdr_frame_envelope_m=[
                x / 1000
                for x in ctx["pdr"]["LM3-BOG-P010"]["design_reference_envelope_mm"]
            ],
        )
        check(
            "gearbox_ground_research_reserve",
            gear_low >= 0.08,
            "Worn wheel radius minus half CAD gearbox height and assumed vertical motion;80mm reserve research only",
        )
        check(
            "axle_frame_lateral_envelope",
            lateral >= 0.15,
            "Nominal axle-length/frame-width bound, not full steering/bearing swept clearance",
        )
        proposed_length = v.get("frame_length_m", c["FRAME_LENGTH_MM"] / 1000)
        pdr_frame = ctx["pdr"]["LM3-BOG-P010"]["design_reference_envelope_mm"]
        metrics["proposed_frame_length_m"] = proposed_length
        check(
            "pdr_frame_envelope_fit",
            proposed_length <= pdr_frame[0] / 1000
            and v["frame_width_m"] <= pdr_frame[1] / 1000,
            "Existing CAD3500mm frame exceeds PDR3400mm:FAILED baseline. Compact3400mm frame is a proposed new geometry.",
        )
        check(
            "existing_bogie_geometry",
            abs(proposed_length - c["FRAME_LENGTH_MM"] / 1000) < 1e-12
            and abs(v["frame_width_m"] - c["FRAME_WIDTH_MM"] / 1000) < 1e-12,
            "Changes from CAD3500x2400mm require new frame/seat/motor/brake mount design, drawings and whole-bogie motion acceptance.",
        )
        check(
            "research_wheelbase_frame_margin",
            proposed_length >= 2.1 + c["WHEEL_DIAMETER_NEW_MM"] / 1000 + 0.3,
            "Reference2100mm bogie wheelbase plus760mm wheel diameter and150mm each-end frame reserve; local envelope only.",
        )
        details = [
            dict(
                part="proposed-bogie-side-beam",
                quantity=2,
                length_m=proposed_length,
                width_m=c["SIDE_BEAM_WIDTH_MM"] / 1000,
                height_m=c["FRAME_HEIGHT_MM"] / 1000,
                source_product_ids=["LM3-BOG-P010", "LM3-BOG-P020"],
                qualification="Outer envelopes only; no wall/plate/weld resistance or revised mount geometry accepted",
            )
        ]
        check(
            "bogie_frame_and_body_connection_release",
            None,
            "PDR3400x2500x620 differs from CAD3500x2400x280; reconcile coordinate/envelope scope. Weld fatigue, primary/secondary suspension, yaw/roll motion and exact mounts unaccepted",
        )
    elif family in {"articulation", "gangway"}:
        metrics.update(articulation_demands(ctx, v))
        gap = v.get("body_gap_m", c["COUPLING_GAP_MM"] / 1000)
        bound = continuous_gangway_longitudinal_bound(ctx)
        reserve = 2 * (
            a["clearance_reserve_m"] + a["articulation_assembly_tolerance_each_end_m"]
        )
        required = bound + reserve
        trainlength = 3 * bodylength + 2 * gap
        metrics.update(
            configured_body_gap_m=gap,
            continuous_longitudinal_motion_bound_m=bound,
            total_tolerance_and_research_reserve_m=reserve,
            required_full_motion_body_gap_m=required,
            body_gap_margin_m=gap - required,
            proposed_three_car_length_m=trainlength,
            length_growth_over_catalogue_m=trainlength
            - c["PROMOTED_LIGHT_METRO_TRAINSET_LENGTH_M"],
            proposed_body_centre_stations_m=[
                0,
                bodylength + gap,
                2 * (bodylength + gap),
            ],
            new_service_crossing_extension_each_joint_m=gap
            - c["COUPLING_GAP_MM"] / 1000,
            concept_55p5m_platform_remaining_length_m=55.5 - trainlength,
        )
        check(
            "separate_bodies_module_clearance",
            gap >= required,
            "Explicit proposed car spacing contains continuous rigid-box yaw/pitch/roll bound plus10mm assembly tolerance and20mm research reserve EACH end. Current0gap fails; this is not catalogue adoption or a deformable-bellows qualification.",
        )
        check(
            "articulation_gangway_qualified_motion",
            None,
            "Combined yaw/pitch/roll rigid envelope only; no deformed bellows, turntable overlaps, pinch guards, load proof, bearing/anti-lift fatigue, fire or optional train-to-train approval",
        )
    elif family == "service_loop":
        positive_diagnostic = articulation_demands(
            ctx, dict(yaw_deg=12, pitch_deg=6, roll_deg=5)
        )["maximum_corner_displacement_m"]
        demand = continuous_corner_displacement_bound(ctx)
        bend = a["hv_cable_diameter_m_research"] * a["hv_bend_multiple_research"]
        gap = v.get("body_gap_m", 0)
        straight = v.get("straight_service_length_m", 0)
        loop_length = math.pi * v["loop_radius_m"] + v["reserve_length_m"] + straight
        required_straight = max(0, gap - 2 * v["loop_radius_m"]) + 0.1
        metrics.update(
            required_research_bend_radius_m=bend,
            semicircle_and_reserve_length_m=math.pi * v["loop_radius_m"]
            + v["reserve_length_m"],
            rigid_corner_displacement_bound_m=demand,
            positive_only_corner_diagnostic_m=positive_diagnostic,
            required_straight_lead_total_m=required_straight,
            developed_service_length_m=loop_length,
            available_extra_over_gap_m=loop_length - gap,
            configured_body_gap_m=gap,
            loop_footprint_m=[2 * v["loop_radius_m"], v["loop_radius_m"]],
        )
        check(
            "research_dynamic_bend_radius",
            v["loop_radius_m"] >= bend - 1e-12,
            "35mm research HV cable with10D dynamic radius; actual cable/hose/chain ratings required",
        )
        check(
            "service_loop_length_reserve",
            loop_length - gap >= demand,
            "Developed length minus actual proposed body gap must exceed continuous signed-angle chord bound; not a deformed cable/energy-chain collision qualification",
        )
        check(
            "service_loop_straight_leads",
            straight >= required_straight - 1e-12,
            "Straight leads bridge bodygap minus semicircular loop diameter, plus50mm termination lead each end.",
        )
        check(
            "service_loop_joint_space",
            gap >= 2 * v["loop_radius_m"] + 0.1,
            "Research external loop packaging in explicit inter-car gap; existing0gap fails, embedded routing would need a separate model.",
        )
        details = [
            dict(
                part="proposed-intercar-service-route",
                loop_radius_m=v["loop_radius_m"],
                straight_total_m=straight,
                developed_length_m=loop_length,
                body_gap_m=gap,
                source_product_ids=["LM3-ART-P024", "LM3-ART-P030"],
                required_motion_reserve_m=demand,
                qualification="Semicircle-plus-straight length reservation only; actualHV/LV/hose segregation, routing shape and cable/chain dynamic ratings unaccepted",
            )
        ]
        check(
            "trainline_carrier_qualification",
            None,
            "HV/LV/coolant segregation, actual bend/torsion, loop-to-structure sweep, clamps, current derating, fire and hose pressure evidence unaccepted",
        )
    elif family == "chassis":
        span = c["PROMOTED_LIGHT_METRO_BOGIE_CENTRE_SPACING_MM"] / 1000
        b, h, t = 0.18, v["section_height_m"], v["wall_m"]
        inertia = (b * h**3 - (b - 2 * t) * (h - 2 * t) ** 3) / 12
        q = mass * g / 3 / bodylength / 2
        moment = q * span**2 / 8
        deflection = 5 * q * span**4 / (384 * a["young_modulus_pa"] * inertia)
        metrics.update(
            nominal_two_rail_moment_each_nm=moment,
            ideal_rhs_inertia_m4=inertia,
            nominal_bending_stress_pa=moment * h / 2 / inertia,
            nominal_uniform_load_deflection_m=deflection,
            legacy_car_load_n=mass * g / 3,
        )
        check(
            "research_chassis_stiffness",
            deflection <= span / 1000,
            "Ideal two simply supported RHS rails, no joints, overhangs/holes/secondary framing; L/1000 research target, not adopted service criterion",
        )
        check(
            "chassis_strength_crash_and_floor_release",
            None,
            "Accepted loads, material/joint fatigue, end-ring interfaces, floor/step transfer, crash/exceptional cases and full shell model unavailable",
        )
    elif family == "chassis_shared":
        spine = source_spine_dimensions(ctx)
        sill = ctx["pdr"]["LM3-BDY-P010"]["design_reference_envelope_mm"]
        span = c["PROMOTED_LIGHT_METRO_BOGIE_CENTRE_SPACING_MM"] / 1000
        t = v["wall_m"]
        side_width = sill[1] / 1000
        side_height = v["section_height_m"]

        def rhs(width, height):
            return (
                (width * height**3 - (width - 2 * t) * (height - 2 * t) ** 3) / 12,
                width * height - (width - 2 * t) * (height - 2 * t),
            )

        side_i, side_area = rhs(side_width, side_height)
        centre_i, centre_area = rhs(spine["width_m"], spine["height_m"])
        inertias = [side_i, centre_i, side_i]
        total_i = sum(inertias)
        shares = [i / total_i for i in inertias]
        generated_mass = (
            2 * side_area * sill[0] / 1000 + centre_area * spine["length_m"]
        ) * a["steel_density_kg_m3"]
        # Retain the FULL existing car load and add all proposed members. This
        # deliberately overcounts the unseparated original member mass instead
        # of silently lowering the load when a heavier hypothesis is introduced.
        supported_mass = mass / 3 + generated_mass
        # Conservative load relocation: put ALL car/member weight uniformly
        # between the same two bogie supports; do not discard the overhang load.
        q = supported_mass * g / span
        moment = q * span**2 / 8
        deflection = 5 * q * span**4 / (384 * a["young_modulus_pa"] * total_i)
        metrics.update(
            legacy_full_car_mass_kg=mass / 3,
            proposed_three_member_gross_mass_kg=generated_mass,
            conservative_loaded_car_mass_kg=supported_mass,
            total_common_curvature_inertia_m4=total_i,
            member_inertias_m4=inertias,
            member_load_share_fractions=shares,
            member_uniform_loads_n_m=[q * x for x in shares],
            member_midspan_moments_nm=[moment * x for x in shares],
            member_end_reactions_n=[q * span / 2 * x for x in shares],
            total_uniform_load_n_m=q,
            nominal_compatible_deflection_m=deflection,
            research_deflection_limit_m=span / 1000,
            side_rail_height_m=side_height,
            source_side_rail_height_m=sill[2] / 1000,
            side_rail_depth_growth_m=side_height - sill[2] / 1000,
            source_centre_spine_m=[
                spine["length_m"],
                spine["width_m"],
                spine["height_m"],
            ],
            member_nominal_stress_pa=[
                moment * shares[0] * side_height / 2 / side_i,
                moment * shares[1] * spine["height_m"] / 2 / centre_i,
                moment * shares[2] * side_height / 2 / side_i,
            ],
        )
        check(
            "research_three_member_stiffness",
            deflection <= span / 1000,
            "Rigid transverse compatibility, common curvature and EI-proportional sharing of complete legacy car load PLUS all proposed member mass; ideal supports at unchanged12.3m bogie spacing",
        )
        check(
            "existing_side_sill_envelope",
            side_height <= sill[2] / 1000,
            "LM3-BDY-P010 source height260mm. Taller600/750mm proposals fail current envelope and require new architecture; affected floor/door/crossbearer descendants remain unqualified",
        )
        check(
            "shared_frame_load_path_and_manufacturing_release",
            None,
            "Proposed hollow sections within source centre-spine OUTER envelope; source solid boxes supply no certified I/grade. Rigid-tie/bolster reactions, torsion, crossbearer/weld fatigue, door cutouts, floor/route envelope, mass ledger/axle growth, crash and other load cases unaccepted",
        )
        details = [
            dict(
                part="proposed-hollow-centre-spine",
                source_product_id="LM3-BDY-P020",
                **spine,
                wall_m=t,
            ),
            dict(
                part="proposed-hollow-side-sill",
                source_product_id="LM3-BDY-P010",
                affected_product_ids=[
                    "LM3-BDY-P021",
                    "LM3-BDY-P030",
                    "LM3-BDY-P060",
                    "LM3-BDY-P061",
                    "LM3-BDY-P070",
                    "LM3-BDY-P100",
                    "LM3-DOOR-P010",
                    "LM3-BDY-P050",
                    "LM3-BDY-P120",
                ],
                quantity=2,
                length_m=sill[0] / 1000,
                width_m=side_width,
                height_m=side_height,
                wall_m=t,
            ),
        ]
    elif family == "exterior":
        height = ctx["pdr"]["LM3-BDY-P130"]["design_reference_envelope_mm"][2] / 1000
        area = height * 1
        count = 2 * (math.ceil(height / v["clip_pitch_m"]) + 1)
        metrics.update(
            one_metre_panel_area_m2=area,
            pressure_resultant_n=area * v["pressure_pa"],
            equal_share_clip_demand_n=area * v["pressure_pa"] / count,
            vertical_edge_clip_count=count,
            retention_pitch_m=v["clip_pitch_m"],
        )
        check(
            "clip_grid_research_spacing",
            v["clip_pitch_m"] <= 0.25,
            "Proposed250mm maximum grid spacing; no clip/laminate resistance inferred from distribution",
        )
        check(
            "panel_retention_laminate_and_vehicle_clearance",
            None,
            "Wind/train pressure, peel/pry/anti-lift, clipped load sharing, batch laminate/fire/UV, gaps/thermal motion, mounts and mass unaccepted",
        )
        details = [
            dict(
                part="research-edge-clip-position",
                side=side,
                z_m=i * height / (count / 2 - 1),
            )
            for side in [-1, 1]
            for i in range(count // 2)
        ]
    elif family == "roof":
        pvlength = bodylength - 0.9
        pvwidth = bodywidth - 0.3
        cols = c["PROMOTED_ROOF_SOLAR_MODULES_PER_CAR"] // 2
        module_l = pvlength / cols - 0.07
        module_w = pvwidth / 2 - 0.07
        metrics.update(
            current_pv_module_m=[module_l, module_w],
            current_pv_gap_m=0.07,
            proposed_roof_centre_walkway_m=v["centre_walkway_m"],
            available_pv_width_each_side_m=(pvwidth - v["centre_walkway_m"]) / 2,
            remaining_roof_length_m=bodylength
            - 2 * v["end_service_clearance_m"]
            - cols * module_l
            - (cols - 1) * 0.07,
        )
        check(
            "pv_walkway_fit",
            2 * module_w + v["centre_walkway_m"] <= pvwidth,
            "Exact CAD-derived12-panel grid checked against research central walkway; HVAC overlapping zones not resolved",
        )
        check(
            "pv_end_service_fit",
            metrics["remaining_roof_length_m"] >= 0,
            "Two requested end access zones against existing six-column panel length",
        )
        check(
            "roof_equipment_and_access_release",
            None,
            "HVAC/PV curbs, antenna keep-outs, installed heights, uplift, leak/fire test, ducts/cables and safe access need supplier GAs and swept service checks",
        )
    elif family == "interior":
        battery = 0.32
        clearance = bodywidth - 2 * (battery + v["seat_depth_m"]) - v["aisle_width_m"]
        metrics.update(
            remaining_cross_section_width_m=clearance,
            requested_aisle_width_m=v["aisle_width_m"],
            side_battery_strake_width_m=battery,
        )
        check(
            "research_seat_aisle_fit",
            clearance >= 0.1,
            "Conservative battery strake plus seat depth on both sides and100mm total trim/structure reserve; no adopted accessibility/seat retention criterion",
        )
        check(
            "interior_fire_retention_and_egress_release",
            None,
            "Full seat/handrail/PIS/trim layout, wheelchair/egress, fire, passenger loads, battery isolation and service-access qualification unaccepted",
        )
    elif family == "service_rail":
        pitch = c["SERVICE_RAIL_DATUM_PITCH_MM"] / 1000
        length = ctx["pdr"]["LM3-FIX-P010"]["design_reference_envelope_mm"][0] / 1000
        points = [
            v["edge_offset_m"] + pitch * i
            for i in range(math.floor((length - 2 * v["edge_offset_m"]) / pitch) + 1)
        ]
        edge = min(points[0], length - points[-1]) - v["bolt_hole_diameter_m"] / 2
        metrics.update(
            rail_length_m=length,
            datum_pitch_m=pitch,
            hole_count=len(points),
            minimum_end_hole_edge_m=edge,
            rail_width_m=c["SERVICE_RAIL_WIDTH_MM"] / 1000,
        )
        check(
            "rail_end_edge_research",
            edge >= 0.012,
            "Proposed12mm clear hole-edge distance; exact rail section, nut and fastener resistance unaccepted",
        )
        details = [
            dict(
                part="research-rail-drill",
                x_m=x,
                y_m=c["SERVICE_RAIL_WIDTH_MM"] / 2000,
                hole_diameter_m=v["bolt_hole_diameter_m"],
            )
            for x in points
        ]
        check(
            "service_rail_mount_release",
            None,
            "Current source prohibits M6 captive fasteners for primary door/glazing/crash/seat retention; exact drawings/torques/thread/rail strength still required",
        )
    elif family == "film":
        width = 1 + 2 * v["trim_allowance_each_side_m"]
        height = (
            ctx["pdr"]["LM3-BDY-P130"]["design_reference_envelope_mm"][2] / 1000
            + 2 * v["trim_allowance_each_side_m"]
        )
        metrics.update(
            research_panel_plot_blank_m=[width, height],
            film_area_per_module_m2=width * height,
            seam_overlap_m=v["seam_overlap_m"],
        )
        check(
            "film_seam_trim_allowance",
            v["trim_allowance_each_side_m"] >= v["seam_overlap_m"],
            "Planning trim margin must contain the specified seam overlap; final seams use actual3D cast flattening",
        )
        check(
            "film_substrate_fire_and_graphics_release",
            None,
            "Existing3M rail-film anchor remains a family only; colour/ink/overlaminate/fire/UV, substrate adhesion, developed artwork and edge repair unaccepted",
        )
    elif family == "coating":
        alpha = min(1, v["solar_absorptance"] * v["surface_soiling_factor"])
        heat = alpha * a["coating_irradiance_w_m2"]
        metrics.update(
            absorbed_solar_flux_w_m2=heat,
            convection_only_temperature_rise_k=heat / a["coating_h_w_m2_k"],
            roof_absorbed_heat_w=heat * (bodylength - 0.9) * (bodywidth - 0.3),
        )
        check(
            "research_coating_temperature_rise",
            metrics["convection_only_temperature_rise_k"] <= 40,
            "Convection-only bound at800W/m2/h8;40K research target; NO radiative-cooling performance credit",
        )
        check(
            "coating_qualification",
            None,
            "Purdue anchor is a research formulation, not orderable rail coating; emissivity/weathering/UV/fire/adhesion/coupon and one-car evidence absent",
        )
    elif family == "lifting":
        demand = (
            mass
            * g
            / 3
            / v["effective_jacks"]
            * v["dynamic_multiplier"]
            * v["load_imbalance_multiplier"]
        )
        metrics.update(
            legacy_car_mass_kg=mass / 3,
            nominal_load_each_effective_jack_n=demand,
            four_point_equal_load_n=mass * g / 12,
        )
        check(
            "research_effective_supports",
            v["effective_jacks"] >= 3,
            "Three/four active support sensitivity; centre of gravity and actual reaction redistribution remain unknown",
        )
        check(
            "lifting_towing_rerailing_qualification",
            None,
            "Proof cases, lifted mass/CG, jacking-pad structure, anti-drop locks, synchronisation, rerail/tow directions and supplier rating unaccepted",
        )
    elif family == "hv_hardware":
        cells = 8
        modules_per_side = cells / 2
        length = modules_per_side * c["BATTERY_MODULE_LENGTH_MM"] / 1000
        tray = ctx["pdr"]["LM3-HV-P010"]["design_reference_envelope_mm"][0] / 1000
        # Research heat rejection from both continuous traction motors in one car.
        losses = (
            2
            * c["PROMOTED_MOTOR_CONTINUOUS_KW"]
            * 1000
            * (1 / a["motor_efficiency"] - 1)
        )
        flow = losses / (a["coolant_cp_j_kg_k"] * a["coolant_delta_t_k"])
        velocity = flow / 1000 / (math.pi * v["service_hose_diameter_m"] ** 2 / 4)
        metrics.update(
            four_battery_module_train_length_m=length,
            pdr_tray_length_m=tray,
            battery_tray_length_difference_m=tray - length,
            ideal_coolant_mass_flow_kg_s=flow,
            ideal_combined_coolant_velocity_m_s=velocity,
            nominal_support_count=math.ceil(length / v["support_pitch_m"]) + 1,
            planning_nominal_dc_current_a=2
            * c["PROMOTED_MOTOR_CONTINUOUS_KW"]
            * 1000
            / a["motor_efficiency"]
            / c["PROMOTED_BATTERY_NOMINAL_VOLTAGE_V"],
        )
        check(
            "research_hose_velocity",
            velocity <= 3,
            "3m/s research upper screening target at assumed motor heat only; battery/controller heat/pipe loss/cavitation/ambient omitted",
        )
        proposed_length = v.get("tray_length_m", tray)
        proposed_height = v.get(
            "tray_height_m",
            ctx["pdr"]["LM3-HV-P010"]["design_reference_envelope_mm"][2] / 1000,
        )
        module_height = c["BATTERY_MODULE_HEIGHT_MM"] / 1000
        bay_length = (
            ctx["pdr"]["LM3-BDY-P050"]["design_reference_envelope_mm"][0] / 1000
        )
        metrics.update(
            proposed_tray_length_m=proposed_length,
            proposed_tray_height_m=proposed_height,
            module_dimensions_m=[
                c["BATTERY_MODULE_LENGTH_MM"] / 1000,
                c["BATTERY_MODULE_WIDTH_MM"] / 1000,
                module_height,
            ],
            proposed_length_growth_m=proposed_length - tray,
            battery_bay_length_m=bay_length,
        )
        check(
            "four_modules_tray_length",
            proposed_length >= length + 0.1 - 1e-12,
            "Four1450mm modules plus50mm end clearances need5900mm:current5400mm local-hardware PDR tray FAILS.",
        )
        check(
            "module_tray_height",
            proposed_height >= module_height + 0.02,
            "370mm CAD module plus20mm total vertical service/installation allowance; current320mm PDR tray FAILS.",
        )
        check(
            "battery_bay_packaging",
            proposed_length <= bay_length
            and proposed_height <= c["BATTERY_STRAKE_HEIGHT_MM"] / 1000,
            "Proposed tray must remain within source6200mm battery-support bay and450mm strake height. Full3D mounts/vent/seat clearance unqualified.",
        )
        check(
            "existing_hv_tray_envelope",
            proposed_length <= tray
            and proposed_height
            <= ctx["pdr"]["LM3-HV-P010"]["design_reference_envelope_mm"][2] / 1000,
            "Extended5900mmx400mm tray is a source-changing proposal; current5400mmx320mm PDR envelope cannot be labelled compatible.",
        )
        details = [
            dict(
                part="proposed-side-battery-tray",
                quantity=2,
                length_m=proposed_length,
                height_m=proposed_height,
                module_quantity=4,
                module_length_m=c["BATTERY_MODULE_LENGTH_MM"] / 1000,
                module_width_m=c["BATTERY_MODULE_WIDTH_MM"] / 1000,
                module_height_m=module_height,
                source_product_ids=["LM3-HV-P010", "LM3-BDY-P050", "LM3-TRC-P040"],
                affected_product_ids=["LM3-HV-P020", "LM3-HV-P030", "LM3-INT-P010"],
                qualification="Tray OUTER envelope only, not a pressure/fire barrier or released formed/welded design",
            )
        ]
        check(
            "hv_pack_and_local_hardware_release",
            None,
            "4x1450mm CAD modules total5800mm versus5400mm PDR tray: reconcile scope. Battery/fire/mist, DC fault/isolation/clearance, cooling duty, vent path and structural acceptance open",
        )
    elif family == "lv_harness":
        length = ctx["pdr"]["LM3-CTRL-P040"]["design_reference_envelope_mm"][0] / 1000
        resistance = 2 * length * a["wire_rho_ohm_mm2_m"] / v["wire_area_mm2"]
        drop = resistance * v["branch_current_a"]
        metrics.update(
            round_trip_copper_length_m=2 * length,
            loop_resistance_ohm=resistance,
            drop_v=drop,
            drop_fraction=drop / a["lv_voltage_v"],
            wire_heat_w=v["branch_current_a"] ** 2 * resistance,
        )
        check(
            "research_branch_voltage_drop",
            drop <= a["lv_voltage_v"] * a["lv_drop_fraction_research"],
            "24V/8m one-way copper branch at assumed resistivity;5% research drop target. Temperature, connectors and protective device not included",
        )
        check(
            "harness_electrical_and_fire_qualification",
            None,
            "Cable ampacity/fire/EMC, fusing, connector pinout/keying/strain relief, fault/safety separation, actual formboard and100% electrical tests required",
        )
    elif family == "lighting":
        count = c["LIGHT_MODULES_PER_CAR"]
        emergency = c["EMERGENCY_LIGHT_MODULES_PER_CAR"]
        power = count * v["module_power_w_research"]
        epower = emergency * v["emergency_module_power_w_research"]
        metrics.update(
            main_module_count_per_car=count,
            main_light_power_w=power,
            main_light_nominal_current_a=power / a["lv_voltage_v"],
            emergency_energy_wh=epower * a["emergency_duration_hr_research"],
            two_rows_installed_length_each_m=count
            / 2
            * c["LIGHT_MODULE_LENGTH_MM"]
            / 1000,
            remaining_longitudinal_margin_each_row_m=bodylength
            - count / 2 * c["LIGHT_MODULE_LENGTH_MM"] / 1000,
        )
        check(
            "main_light_row_length",
            metrics["remaining_longitudinal_margin_each_row_m"] >= 0,
            "22 actual1.2m cassettes per car split two rows; no routing/obstruction or photometric acceptance",
        )
        check(
            "light_function_and_emergency_qualification",
            None,
            "Wattages/duration are research demands, not offered modules; independent feed/keying, photometry/lux, emergency battery discharge, ingress/fire and shock evidence absent",
        )
    elif family == "coupler":
        demand = mass * (v["recovery_acceleration_m_s2"] + g * v["grade_fraction"])
        metrics.update(
            legacy_recovery_draw_force_n=demand,
            legacy_train_mass_kg=mass,
            coupler_face_height_m=c["COUPLER_FACE_HEIGHT_MM"] / 1000,
        )
        check(
            "recovery_direction_defined",
            v["grade_fraction"] >= 0,
            "Longitudinal forward/up-grade force only; no rolling resistance or dynamic snatch, buff/crash/derailment considered",
        )
        check(
            "coupler_crash_sensor_and_rescue_release",
            None,
            "No energy absorber curve, coupler draw/buff/vertical rating, rescue compatibility, crush load path, sensor optical FOV/alignment, recovery procedure or exact origin accepted",
        )
    elif family == "vehicle":
        trainlength = 3 * bodylength + 2 * v["body_gap_m"]
        wheel_drop = (c["WHEEL_DIAMETER_NEW_MM"] / 1000 - v["wheel_diameter_m"]) / 2
        metrics.update(
            three_car_body_and_gap_length_m=trainlength,
            current_promoted_train_length_m=c["PROMOTED_LIGHT_METRO_TRAINSET_LENGTH_M"],
            train_length_discrepancy_m=trainlength
            - c["PROMOTED_LIGHT_METRO_TRAINSET_LENGTH_M"],
            wheel_wear_floor_height_change_m=wheel_drop,
            three_car_legacy_mass_kg=mass,
            promoted_planning_tare_kg=c["PROMOTED_LIGHT_METRO_TRAINSET_MASS_KG"],
        )
        check(
            "embedded_articulation_length_consistency",
            abs(metrics["train_length_discrepancy_m"]) < 1e-12,
            "Promoted49.5m equals three16.5m bodies at0gap; zero gap does not accept the1120mm articulation architecture",
        )
        check(
            "integrated_complete_car_acceptance",
            None,
            "Configuration, tolerance/kinematic gauges, mass/CG/axles, HVAC/fire/egress, control/braking/charging, depot and route interfaces require accepted integration evidence",
        )
    elif family == "electronics":
        flow = v["heat_w_research"] / (1.2 * 1005 * v["allowable_air_rise_k_research"])
        metrics.update(
            ideal_cabinet_airflow_m3_s=flow,
            ideal_cabinet_airflow_m3_hr=flow * 3600,
            assumed_heat_w=v["heat_w_research"],
        )
        check(
            "research_cabinet_airflow",
            flow * 3600 <= 200,
            "200m3/h research service-envelope target; no actual cabinet/fan curve/filter/dust allowance adopted",
        )
        check(
            "control_and_safety_electronics_acceptance",
            None,
            "This calculation is cabinet thermal demand only. No functional safety, braking logic, secure communications, EMC or controller software qualification inferred",
        )
    else:
        raise ValueError("unknown mechanical investigation family: " + family)
    if family in {"articulation", "gangway", "service_loop"}:
        check(
            "existing_intercar_spacing",
            abs(v.get("body_gap_m", 0) - c["COUPLING_GAP_MM"] / 1000) < 1e-12,
            "Source trainset COUPLING_GAP_MM=0. Nonzero gap is an explicit new car-spacing/service-routing proposal requiring a new accepted architecture; it is incompatible with the unchanged catalogue.",
        )
    source_compatibility_checks = {
        "existing_side_frame_envelope",
        "existing_front_carrier_envelope",
        "existing_bogie_geometry",
        "existing_hv_tray_envelope",
        "existing_side_sill_envelope",
        "existing_intercar_spacing",
    }
    existing_geometry_checks = source_compatibility_checks | {
        "side_pane_pressure_frame_fit",
        "front_carrier_geometry_fit",
        "pdr_frame_envelope_fit",
        "four_modules_tray_length",
        "module_tray_height",
        "separate_bodies_module_clearance",
    }
    return dict(
        variables=dict(v),
        metrics=metrics,
        checks=checks,
        manufacturing_definitions=details,
        local_model_screen_feasible=not any(
            x["status"] == "failed" and x["id"] not in source_compatibility_checks
            for x in checks
        ),
        existing_configuration_compatible=not any(
            x["status"] == "failed" and x["id"] in existing_geometry_checks
            for x in checks
        ),
        conditional_screen_feasible=not any(x["status"] == "failed" for x in checks),
        engineering_design_complete=False,
        physical_release=False,
    )


def variants(family, ctx):
    actual_family = "glazing" if family == "door_window" else family
    space = ctx["inputs"]["variable_spaces"][actual_family]
    keys = list(space)
    candidates = []
    for combination in itertools.product(*(space[k] for k in keys)):
        variables = dict(zip(keys, combination))
        candidate = evaluate(actual_family, variables, ctx)
        payload = json.dumps(
            [actual_family, variables], sort_keys=True, separators=(",", ":")
        )
        candidate["id"] = (
            actual_family + "-" + hashlib.sha256(payload.encode()).hexdigest()[:12]
        )
        candidates.append(candidate)
    return candidates


def run():
    ctx = context()
    packages = []
    cache = {}
    for entry in ctx["inputs"]["packages"]:
        identity, family = entry["work_package_id"], entry["family"]
        wbs = ctx["scope"][identity]
        families = (
            ["glazing", "door", "side_glazing"] if family == "door_window" else [family]
        )
        if identity == "BUY-LM3-CWL-SA710":
            families += ["glazing"]
        if identity == "LM3-FRP-010":
            families += ["chassis_shared"]
        if identity in {"BUY-LM3-BOG-SA610", "LM3-FRP-130"}:
            families += ["traction", "running_unit"]
        if identity in {"BUY-LM3-BOG-SA620", "LM3-FRP-140"}:
            families += ["running_unit"]
        if identity == "BUY-LM3-CAR-A900":
            families += ["door", "roof", "interior"]
        products = []
        for source in wbs["authoritative_sources"]:
            if source["path"].endswith("buildable-trainset-manifest.json"):
                products.extend(source["ids"])
        # Explicit assembly descendants prevent a top-level purchased assembly
        # from hiding its individual supplier and locally made interfaces.
        pending = list(products)
        expanded = set()
        while pending:
            pid = pending.pop()
            if pid in expanded:
                continue
            expanded.add(pid)
            pending.extend(ctx["products"][pid].get("children", []))
        audit = []
        for pid in sorted(expanded):
            product = ctx["products"][pid]
            pdr = ctx["pdr"].get(pid)
            audit.append(
                dict(
                    product_id=pid,
                    source_scope=(
                        "direct-authoritative-row"
                        if pid in products
                        else "authoritative-assembly-descendant"
                    ),
                    title=product["title"],
                    route=product.get("route", "assembly"),
                    quantity_per_trainset=product.get("quantity_per_trainset"),
                    source_row_sha256=hashlib.sha256(
                        json.dumps(product, sort_keys=True).encode()
                    ).hexdigest(),
                    pdr_reference_envelope_mm=(
                        None if pdr is None else pdr["design_reference_envelope_mm"]
                    ),
                    pdr_release_status=None if pdr is None else pdr["release_status"],
                    pdr_artifact_ids=(
                        []
                        if pdr is None
                        else [x["artifact_id"] for x in pdr["required_artifacts"]]
                    ),
                    supplier_anchor_ids=[
                        x["id"] for x in ctx["anchors"] if pid in x["product_ids"]
                    ],
                )
            )
        investigations = []
        for f in families:
            if f not in cache:
                cache[f] = variants(f, ctx)
            candidates = cache[f]
            feasible = [
                x
                for x in candidates
                if x["conditional_screen_feasible"]
                and x["existing_configuration_compatible"]
            ]
            source_changing_proposals = [
                x
                for x in candidates
                if x["local_model_screen_feasible"]
                and not x["existing_configuration_compatible"]
            ]
            investigations.append(
                dict(
                    id=f,
                    basis="Exhaustive deterministic finite parameter enumeration of named research submodel; failed candidates retained, unknown never passes",
                    variable_space=ctx["inputs"]["variable_spaces"][
                        "glazing" if f == "door_window" else f
                    ],
                    candidates=candidates,
                    selected_candidate_ids=[] if not feasible else [feasible[0]["id"]],
                    proposed_candidate_ids=(
                        []
                        if not source_changing_proposals
                        else [source_changing_proposals[0]["id"]]
                    ),
                    termination=dict(
                        reason="finite_domain_exhausted",
                        evaluations=len(candidates),
                        conditional_screen_feasible_count=len(feasible),
                        source_changing_local_solution_count=len(
                            source_changing_proposals
                        ),
                    ),
                    scope_limit="Only the reported predicates/demands are investigated. Every authoritative child, drawing, load case and manufacturing approval remains subject to package release gates.",
                )
            )
        package = dict(
            work_package_id=identity,
            title=wbs["title"],
            source_products=audit,
            authoritative_sources=wbs["authoritative_sources"],
            package_release_requirements=wbs["required_gates"],
            investigations=investigations,
            generated_artifacts=[
                identity + "/candidate-demands.csv",
                identity + "/source-product-audit.json",
            ],
            unresolved_gates=sorted(
                set(
                    x["basis"]
                    for i in investigations
                    for x in i["candidates"][0]["checks"]
                    if x["status"] == "unknown"
                )
            )
            + [
                "Exact product material/process allowables, issued/check-approved drawings, all PDR artifacts and first-article evidence remain unaccepted."
            ],
            engineering_design_complete=False,
            physical_release=False,
        )
        packages.append(package)
    return dict(
        schema="osr-generative-mechanical-systems/1",
        architecture_boundary=ctx["inputs"]["boundary"],
        packages=packages,
        source_sha256=ctx["source_sha256"],
        supplier_leads=ctx["inputs"]["supplier_leads"],
        assumptions=ctx["a"],
        source_discrepancies=[
            dict(
                id="front-carrier-pdr-vs-cad",
                work_package_id="LM3-FRP-030",
                pdr_reference_envelope_mm=[2300, 260, 1780],
                cad_carrier_outer_width_height_mm=[
                    ctx["c"]["PANORAMIC_GLASS_WIDTH_MM"] + 210,
                    ctx["c"]["PANORAMIC_GLASS_HEIGHT_MM"] + 230,
                ],
                state="unreconciled-envelope-scope",
            ),
            dict(
                id="side-window-pdr-vs-cad",
                work_package_id="LM3-FRP-110",
                pdr_reference_envelope_mm=[1650, 140, 1250],
                cad_window_widths_mm=[3600, 2900, 3600],
                cad_window_height_mm=ctx["c"]["WINDOW_HEIGHT_MM"],
                state="unreconciled-envelope-scope",
            ),
            dict(
                id="bogie-frame-pdr-vs-cad",
                work_package_id="LM3-FRP-130",
                pdr_reference_envelope_mm=[3400, 2500, 620],
                cad_frame_mm=[
                    ctx["c"]["FRAME_LENGTH_MM"],
                    ctx["c"]["FRAME_WIDTH_MM"],
                    ctx["c"]["FRAME_HEIGHT_MM"],
                ],
                state="unreconciled-envelope-scope",
            ),
            dict(
                id="zero-body-gap-articulation-module",
                work_package_id="LM3-FRP-120",
                cad_body_gap_mm=ctx["c"]["COUPLING_GAP_MM"],
                cad_articulation_module_length_mm=ctx["c"][
                    "ARTICULATION_MODULE_LENGTH_MM"
                ],
                state="embedding-or-car-spacing-unresolved",
            ),
            dict(
                id="battery-module-tray-length",
                work_package_id="LM3-FRP-150",
                four_modules_mm=4 * ctx["c"]["BATTERY_MODULE_LENGTH_MM"],
                pdr_tray_mm=ctx["pdr"]["LM3-HV-P010"]["design_reference_envelope_mm"][
                    0
                ],
                state="unreconciled-envelope-scope",
            ),
        ],
        summary=dict(
            package_count=len(packages),
            unique_investigation_families=len(cache),
            unique_candidates=sum(len(x) for x in cache.values()),
            all_queued_packages_investigated=True,
            all_engineering_designs_complete=False,
        ),
        engineering_design_complete=False,
        physical_release=False,
    )


def write_artifacts(report, output: Path):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)

    def write(path, obj):
        path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")

    for package in report["packages"]:
        directory = output / package["work_package_id"]
        directory.mkdir(exist_ok=True)
        write(directory / "source-product-audit.json", package["source_products"])
        rows = []
        definitions = []
        for investigation in package["investigations"]:
            for candidate in investigation["candidates"]:
                for name, value in candidate["metrics"].items():
                    if isinstance(value, (int, float)):
                        rows.append(
                            dict(
                                candidate_id=candidate["id"],
                                investigation=investigation["id"],
                                quantity=name,
                                value=value,
                                conditional_screen_feasible=candidate[
                                    "conditional_screen_feasible"
                                ],
                            )
                        )
                if (
                    candidate["id"]
                    in investigation["selected_candidate_ids"]
                    + investigation["proposed_candidate_ids"]
                    and candidate["manufacturing_definitions"]
                ):
                    definitions.append(
                        dict(
                            investigation=investigation["id"],
                            candidate_id=candidate["id"],
                            status=(
                                "proposed-source-envelope-change-unreleased"
                                if candidate["id"]
                                in investigation["proposed_candidate_ids"]
                                else "research-dimensioned-definition-unreleased"
                            ),
                            definitions=candidate["manufacturing_definitions"],
                        )
                    )
        with (directory / "candidate-demands.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "candidate_id",
                    "investigation",
                    "quantity",
                    "value",
                    "conditional_screen_feasible",
                ],
            )
            writer.writeheader()
            writer.writerows(rows)
        if definitions:
            write(directory / "manufacturing-definitions.json", definitions)
            package["generated_artifacts"].append(
                package["work_package_id"] + "/manufacturing-definitions.json"
            )
            for definition in definitions:
                for part in definition["definitions"]:
                    if part["part"] == "research-lamp-plate":
                        width, height = part["width_m"] * 1000, part["height_m"] * 1000
                        circles = "".join(
                            f'<circle cx="{x*1000:.3f}" cy="{y*1000:.3f}" r="{part["hole_diameter_m"]*500:.3f}" fill="white" stroke="black"/>'
                            for x, y in part["holes_xy_m"]
                        )
                        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="650" viewBox="-30 -40 {width+60} {height+90}"><rect x="0" y="0" width="{width}" height="{height}" fill="#dce8f2" stroke="black"/>{circles}<g font-family="sans-serif" font-size="8" fill="black"><text x="0" y="-20">UNRELEASED RESEARCH: LM3-FAS-P020 lamp plate</text><text x="0" y="{height+17}">{width:.0f} x {height:.0f} x {part["thickness_m"]*1000:.0f} mm; four holes diameter6.5 mm</text><text x="0" y="{height+30}">Hole centres:20 mm from edges. Grade/finish/joint and tolerances OPEN.</text></g></svg>'
                        (directory / "lamp-plate.svg").write_text(svg + "\n")
                        package["generated_artifacts"].append(
                            package["work_package_id"] + "/lamp-plate.svg"
                        )
                    if part["part"] == "research-rail-drill":
                        # Full drill coordinates already retained in JSON; CSV
                        # supports import into a CAM review without being NC code.
                        path = directory / "service-rail-drill.csv"
                        with path.open("w", newline="") as handle:
                            writer = csv.DictWriter(
                                handle, fieldnames=["x_m", "y_m", "hole_diameter_m"]
                            )
                            writer.writeheader()
                            writer.writerows(
                                {
                                    key: value
                                    for key, value in p.items()
                                    if key != "part"
                                }
                                for p in definition["definitions"]
                            )
                        package["generated_artifacts"].append(
                            package["work_package_id"] + "/service-rail-drill.csv"
                        )
                        break
        package["generated_artifacts"] = list(
            dict.fromkeys(package["generated_artifacts"])
        )
    write(output / "report.json", report)
    return [
        output / path for p in report["packages"] for path in p["generated_artifacts"]
    ]
