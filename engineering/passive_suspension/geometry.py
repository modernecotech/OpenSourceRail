"""Exact stock geometry for an unqualified onboard-PM/passive-facing campaign.

The field unit is ONE local two-pole module on ONE bank.  Twelve occurrences
per bank and two banks per car are explicit.  Only steel is added to the
guideway; ordinary concrete and station propulsion remain separate interfaces.
2-D winding regions are homogenised current windows, not solid copper blocks.
The stock/native ledger instead contains each rectangular conductor leg and
end turn.  Neither ledger is a complete installed suspension.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "osr-passive-facing-geometry/1"
FHWA_TOLERANCES = "https://www.fhwa.dot.gov/bridge/prefab/if09010/01a.cfm"
FHWA_BEARINGS = "https://www.fhwa.dot.gov/bridge/prefab/if09010/02c.cfm"
DLR_FLEXURES = "https://elib.dlr.de/196584/1/s11340-023-00982-7.pdf"
FLAGS = dict(design_complete=False, engineering_accepted=False,
             physical_validation=False, manufacturing_release=False,
             physical_release=False, adopted=False)

DEFAULTS = dict(length_x_m=1.0, reference_gap_m=.012, facing_width_m=.50,
                facing_thickness_m=.035, pole_width_m=.12, pole_gap_m=.08,
                pm_thickness_m=.05, pole_shoe_thickness_m=.018,
                pole_shoe_overhang_m=.008, return_thickness_m=.05,
                turns=60, shunt_turns=60, conductor_side_m=.002,
                conductor_insulation_m=.0002, winding_clearance_m=.002,
                pm_block_max_x_m=.10, pm_block_max_y_m=.06,
                modules_per_bank=12, bank_offset_m=.88,
                car_length_m=17., beam_span_m=25., carrier_plate_m=.008,
                flexure_length_m=.20, flexure_width_m=.04,
                flexure_thickness_m=.002, flexures_per_module=4,
                carrier_lateral_stroke_m=.15)


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       allow_nan=False) + "\n").encode()


def _positive(value, name):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError(name + " requires a finite positive number")
    return float(value)


def _finite(value, name):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(name + " requires a finite number")
    return float(value)


def material_table(root=ROOT):
    """Retain named canonical material provenance; do not rename FB9B as Y35."""
    path = Path(root) / "engineering/ferrite_maglev/candidate-magnetics.toml"
    raw = tomllib.loads(path.read_text())["materials"]
    result = {key: deepcopy(raw[key]) for key in ("steel", "ferrite", "copper")}
    # The magnetic steel curve is a proxy for cut/stack stock and particularly
    # for solid facing steel.  No DC loss or solid-facing grade is qualified.
    for key, value in result.items():
        value["provisional"] = True
        value["source_input"] = path.relative_to(Path(root)).as_posix()
        value["source_input_sha256"] = sha256(path.read_bytes()).hexdigest()
    result["steel"]["facing_grade_hold"] = "Solid facing grade, B-H curve, joints, corrosion and eddy losses unqualified"
    return result


def _box(identity, size, at, material, density, group, role, **extra):
    if len(size) != 3 or len(at) != 3:
        raise ValueError("three-dimensional stock required")
    size = [_positive(v, identity) for v in size]
    at = [_finite(v, identity) for v in at]
    volume = math.prod(size)
    mass = volume * density
    return dict(id=identity, kind="box", size_m=size, at_m=at,
                material=material, group=group, role=role,
                volume_m3=volume, density_kg_m3=density, mass_kg=mass,
                cg_m=[at[i] + size[i] / 2 for i in range(3)],
                inertia_kg_m2=[[mass * sum(size[j] ** 2 for j in range(3) if j != i) / 12
                                if i == k else 0. for k in range(3)] for i in range(3)],
                **extra)


def _region(identity, material, group, bounds, **extra):
    y0, y1, z0, z1 = bounds
    if not all(math.isfinite(v) for v in bounds) or y1 <= y0 or z1 <= z0:
        raise ValueError("nonempty finite rectangular field region required")
    return dict(id=identity, material=material, group=group,
                bounds_yz_m=list(bounds), Br_y_T=0., Br_z_T=0.,
                J_x_A_m2=0., **extra)


def _winding(identity, centre_y, width, z0, height, turns, p, rho,
             *, polarity=1):
    """Disjoint rectangular-wire rings; straight corners omit bend allowance.

    Finite end turns clear both PM ends.  The magnetic current windows smear
    the same signed N turns over the declared pack area.  Insulation, leadouts,
    minimum bend radius, joints and clamps are unresolved installed stock.
    """
    wire = p["conductor_side_m"]
    pitch = wire + 2 * p["conductor_insulation_m"]
    rows = math.floor((height + 1e-12) / pitch)
    if rows < 1:
        raise ValueError("conductor does not fit winding height")
    layers = math.ceil(turns / rows)
    clear = p["winding_clearance_m"]
    pack = layers * pitch
    inner_x = p["length_x_m"] + 2 * clear
    inner_y = width + 2 * clear
    regions = []
    for side in (-1, 1):
        lo = centre_y + side * inner_y / 2
        bounds = [lo - pack, lo, z0, z0 + rows * pitch] if side < 0 else [lo, lo + pack, z0, z0 + rows * pitch]
        regions.append(_region(identity + f"/window-{side}", "copper", "train", bounds,
                               circuit_id=identity, turns_per_m2=side * polarity * turns / (pack * rows * pitch),
                               winding_representation="homogenised signed-turn window; actual copper is the stock ledger"))
    parts = []
    for turn in range(turns):
        layer, row = divmod(turn, rows)
        outer_x = inner_x + 2 * (layer + 1) * pitch
        outer_y = inner_y + 2 * (layer + 1) * pitch
        z = z0 + row * pitch + p["conductor_insulation_m"]
        for side in (-1, 1):
            y = centre_y - outer_y / 2 if side < 0 else centre_y + outer_y / 2 - wire
            parts.append(_box(identity + f"/turn-{turn:03d}/leg-{side}",
                              [outer_x - 2 * wire, wire, wire],
                              [-outer_x / 2 + wire, y, z], "copper", rho, "train", "winding-conductor"))
            x = -outer_x / 2 if side < 0 else outer_x / 2 - wire
            parts.append(_box(identity + f"/turn-{turn:03d}/end-{side}",
                              [wire, outer_y, wire], [x, centre_y - outer_y / 2, z],
                              "copper", rho, "train", "winding-conductor"))
    volume = math.fsum(q["volume_m3"] for q in parts)
    length = volume / wire ** 2
    return regions, parts, dict(id=identity, turns=turns,
        conductor_area_m2=wire ** 2, conductor_length_m=length,
        copper_volume_m3=volume, copper_mass_kg=volume * rho,
        resistance_20c_ohm=1.724e-8 * length / wire ** 2,
        current_density_A_m2_per_A=1 / wire ** 2,
        window_pack_width_m=pack, window_height_m=rows * pitch,
        signed_window_turns=[-polarity * turns, polarity * turns],
        physical_outer_length_m=inner_x + 2 * layers * pitch,
        topology="rectangular series rings; leadouts and turn-to-turn transitions unknown",
        qualified=False)


def _unknown(identity, scope, reason, quantity=None):
    return dict(id=identity, scope=scope, status="unknown", quantity=quantity,
                mass_kg=None, cg_m=None, reason=reason)


def candidate(label, params=None, *, root=ROOT):
    """Return a source-bound physical geometry, not a force/installed design.

    A: lift/damping coupon plus unresolved separate side-guidance reference.
    B: same finite facing; shared passive alignment must be evaluated.
    C: B plus counted onboard shorted/shunt winding.
    D: B plus counted plate/leaf stock for independently compliant modules.
    B-segmented: one bounded, rotated-PM alternative; no optimality claim.
    """
    if label not in {"A", "B", "C", "D", "B-segmented"}:
        raise ValueError("unknown passive suspension family")
    p = deepcopy(DEFAULTS)
    extra = {} if params is None else dict(params)
    if set(extra) - set(p):
        raise ValueError("unknown geometry parameter: " + str(sorted(set(extra) - set(p))))
    p.update(extra)
    for key in p:
        if key in {"turns", "shunt_turns", "modules_per_bank", "flexures_per_module"}:
            if type(p[key]) is not int or not 1 <= p[key] <= 240:
                raise ValueError("bounded positive integer required: " + key)
        else:
            p[key] = _positive(p[key], key)
    if p["length_x_m"] > 1.2 or p["reference_gap_m"] > .05:
        raise ValueError("bounded local module length/gap required")
    if p["flexures_per_module"] != 4:
        raise ValueError("this bounded carrier drawing has exactly four leaf locations")
    if 2 * p["bank_offset_m"] + p["facing_width_m"] > 2.65:
        raise ValueError("facing banks exceed retained 2.65m body reference")
    mats = material_table(root)
    ferrite = mats["ferrite"]
    br = ferrite["br_20c_t"]
    L, gap = p["length_x_m"], p["reference_gap_m"]
    width, sep = p["pole_width_m"], p["pole_width_m"] + p["pole_gap_m"]
    outer = sep + width
    yoke_width = outer + 2 * p["pole_shoe_overhang_m"]
    shoe_bottom = -gap - p["pole_shoe_thickness_m"]
    pm_bottom = shoe_bottom - p["pm_thickness_m"]
    yoke_bottom = pm_bottom - p["return_thickness_m"]
    regions, parts, coils = [], [], []

    def solid(identity, mat, bounds, group="train", **kw):
        r = _region(identity, mat, group, bounds)
        r.update(kw)
        regions.append(r)
        a, b, c, d = bounds
        nx = math.ceil(L / p["pm_block_max_x_m"]) if mat == "ferrite" else 1
        ny = math.ceil((b - a) / p["pm_block_max_y_m"]) if mat == "ferrite" else 1
        for i in range(nx):
            for j in range(ny):
                suffix = f"/block-{i}-{j}" if mat == "ferrite" else ""
                parts.append(_box(identity + suffix, [L/nx, (b-a)/ny, d-c],
                    [-L/2+i*L/nx, a+j*(b-a)/ny, c],
                    mat, mats[mat]["density_kg_m3"], group,
                    "passive-facing" if group == "guideway" else "magnetic-stock",
                    **({"Br_y_T": r["Br_y_T"], "Br_z_T": r["Br_z_T"],
                         "block_joints": "Nominal touching blocks; adhesive/retention tolerances unknown"}
                       if mat == "ferrite" else {})))

    solid("guideway/facing", "steel", [-p["facing_width_m"] / 2,
          p["facing_width_m"] / 2, 0., p["facing_thickness_m"]], "guideway")
    solid("train/return-yoke", "steel", [-yoke_width / 2, yoke_width / 2,
          yoke_bottom, pm_bottom])
    for side in (-1, 1):
        cy = side * sep / 2
        solid(f"train/pole-shoe-{side}", "steel",
              [cy - width / 2 - p["pole_shoe_overhang_m"], cy + width / 2 + p["pole_shoe_overhang_m"], shoe_bottom, -gap])
        if label == "B-segmented":
            # Three equal rectangular pieces per pole.  Direction rotates by
            # +/-45deg about the centre pole axis: a declared Halbach-like
            # perturbation, not an analytically perfect or optimised Halbach.
            for segment, angle in enumerate((-math.pi / 4, 0., math.pi / 4)):
                left = cy - width / 2 + segment * width / 3
                solid(f"train/pm-{side}/segment-{segment}", "ferrite",
                      [left, left + width / 3, pm_bottom, shoe_bottom],
                      Br_y_T=side * br * math.sin(angle), Br_z_T=side * br * math.cos(angle))
        else:
            solid(f"train/pm-{side}", "ferrite", [cy - width / 2, cy + width / 2, pm_bottom, shoe_bottom], Br_z_T=side * br)
        r, q, winding = _winding(f"damping-{side}", cy, width,
            pm_bottom, p["pm_thickness_m"], p["turns"], p,
            mats["copper"]["density_kg_m3"], polarity=side)
        regions.extend(r); parts.extend(q); coils.append(winding)
    if label == "C":
        r, q, winding = _winding("shunt", 0., yoke_width, yoke_bottom,
            p["return_thickness_m"], p["shunt_turns"], p,
            mats["copper"]["density_kg_m3"])
        regions.extend(r); parts.extend(q); coils.append(winding)
        winding["connection"] = "onboard closed passive circuit; resistance known, inductance/control coupling unvalidated"
    if label == "D":
        rho = mats["steel"]["density_kg_m3"]
        plate_z = yoke_bottom - .03 - p["carrier_plate_m"]
        parts.append(_box("carrier/plate", [L, yoke_width + .10, p["carrier_plate_m"]],
             [-L / 2, -(yoke_width + .10) / 2, plate_z], "steel", rho, "train", "carrier-stock"))
        for i in range(p["flexures_per_module"]):
            side = -1 if i % 2 == 0 else 1
            x = (-.25 if (i // 2) % 2 == 0 else .25) * L
            parts.append(_box(f"carrier/leaf-{i}",
                [p["flexure_length_m"], p["flexure_thickness_m"], p["flexure_width_m"]],
                [x - p["flexure_length_m"] / 2,
                 side * (yoke_width / 2 + .025) - p["flexure_thickness_m"] / 2,
                 plate_z - .01 - p["flexure_width_m"]],
                "steel", rho, "train", "elastic-leaf-stock"))
        # Only the longitudinally continuous carrier plate belongs in this
        # transverse 2D section.  Intermittent leaves remain in the stock ledger;
        # their 3D magnetic effects cannot be represented by an invented mu.
        for q in parts:
            if q["role"] == "carrier-stock":
                y, z = q["at_m"][1:]
                regions.append(_region(q["id"], "steel", "train",
                    [y, y + q["size_m"][1], z, z + q["size_m"][2]],
                    field_approximation="Continuous carrier plate; intermittent leaves/end effects unresolved in 3D"))
    train_parts = [q for q in parts if q["group"] == "train"]
    train_mass = math.fsum(q["mass_kg"] for q in train_parts)
    module_envelope_x = max(q["at_m"][0] + q["size_m"][0] for q in train_parts) - min(q["at_m"][0] for q in train_parts)
    pitch = p["car_length_m"] / p["modules_per_bank"]
    if module_envelope_x > pitch:
        raise ValueError("physical coil/end-turn envelope exceeds module packing pitch")
    by_material = {m: math.fsum(q["mass_kg"] for q in train_parts if q["material"] == m)
                   for m in ("steel", "ferrite", "copper")}
    facing_linear = p["facing_width_m"] * p["facing_thickness_m"] * mats["steel"]["density_kg_m3"]
    unknown = [_unknown("module/retention-and-fasteners", "per-module", "PM retention, conductor clamps, leadouts, insulation and electrical connections not drawn", 1),
               _unknown("module/cooling", "per-module", "No coldplate, pipes, pump, coolant or heat rejection geometry established", 1),
               _unknown("car/sensors-controls-protection", "per-car", "Damping electronics, redundant sensors and fault protection not sized", 1),
               _unknown("guideway/cast-in-anchors-grout-shims", "per-beam-span", "Cast-in anchorage, plate attachment, grout and shim quantities require concrete design", 1)]
    if label == "A":
        unknown.append(_unknown("car/separate-side-guidance-reference", "per-car", "Separate onboard guidance modules and passive side steel facings required; counts, geometry, forces and mass not established"))
    if label == "D":
        unknown.append(_unknown("carrier/stops-retention-joints", "per-module", "Leaf stock alone does not define a load-retaining multiaxis independent carrier", 1))
    result = dict(schema=SCHEMA, label=label, parameters=p,
        length_x_m=L, reference_gap_m=gap, origin_yz_m=[0., -gap],
        regions=regions, materials=mats, circuits=coils,
        units_per_car=2*p["modules_per_bank"],
        br_basis=dict(grade="TDK-FB9B-recoil-proxy", reference_temperature_c=20.,
                      br_T=br, temperature_curve_qualified=False),
        stock_parts=parts,
        packing=dict(field_unit="one local two-pole module on ONE facing bank",
                     banks_per_car=2, modules_per_bank=p["modules_per_bank"],
                     modules_per_car=2 * p["modules_per_bank"],
                     bank_centres_y_m=[-p["bank_offset_m"], p["bank_offset_m"]],
                     module_centres_x_m=[(i + .5) * pitch - p["car_length_m"] / 2 for i in range(p["modules_per_bank"])],
                     pitch_m=pitch, physical_module_envelope_x_m=module_envelope_x,
                     longitudinal_clearance_m=pitch-module_envelope_x,
                     rigid_frame_length_m=p["car_length_m"], independent_carriers=label == "D"),
        stock=dict(train_known_mass_kg_per_module=train_mass,
                   train_known_mass_kg_per_car=train_mass * 2 * p["modules_per_bank"],
                   train_material_mass_kg_per_module=by_material,
                   guideway_facing_kg_per_m_per_bank=facing_linear,
                   guideway_facing_kg_per_route_m=2 * facing_linear,
                   guideway_facing_kg_per_beam_span=2 * facing_linear * p["beam_span_m"],
                   beam_span_m=p["beam_span_m"],
                   pole_face_area_m2_per_module=2 * L * (width + 2 * p["pole_shoe_overhang_m"]),
                   return_section_m2=L * p["return_thickness_m"],
                   scope="Exact listed stock only; guideway excluded from train mass; all unresolved hardware remains unknown"),
        unknown_installed_inventory=unknown, installed_mass_kg_per_car=None,
        installed_cg_m=None, ordinary_concrete_guidebeam="External retained civil design; no permanent magnets or powered suspension/guidance equipment wayside",
        separate_guidance_reference=(dict(required=True, established=False,
            train_equipment="Independent onboard guidance PM/coil units, unsized",
            guideway_equipment="Passive ordinary steel side facings, unsized") if label == "A" else None),
        required_evaluations=["lift/gap/demagnetisation", "lateral and roll force gradients", "active damping and fault response", "full thermal duty", "attachment and retention", "curve swept clearance"],
        limitations=["2D extruded field unit; finite x end effects and solid facing losses open",
                     "Winding signed current windows homogenise discrete conductor positions",
                     "Rectangular wire corner, leadout, insulation, retention and cooling details incomplete",
                     "Intermittent carrier leaves are counted stock but omitted from transverse PDE; their 3D magnetic effects remain unknown",
                     "Shared finite-facing lateral restoring force is a question for the field solver, not an assumed constraint"],
        **FLAGS)
    result["stock_quantities"] = deepcopy(result["stock"])
    result["unknown_stock"] = deepcopy(unknown)
    result["physical_geometry_sha256"] = sha256(encoded(physical_definition(result))).hexdigest()
    result["identity_scope"] = "physical_geometry_sha256 excludes material-model/temperature/current hypotheses; geometry_sha256 binds the complete diagnostic payload"
    result["geometry_sha256"] = sha256(encoded(result)).hexdigest()
    return result


def physical_definition(value):
    """Physical geometry only; empirical material laws belong to evaluations."""
    regions = []
    for row in value["regions"]:
        r = {k: deepcopy(row[k]) for k in ("id", "material", "group", "bounds_yz_m")}
        magnitude = math.hypot(row["Br_y_T"], row["Br_z_T"])
        if magnitude:
            r["magnetisation_direction_yz"] = [row["Br_y_T"]/magnitude, row["Br_z_T"]/magnitude]
        if "circuit_id" in row:
            r.update(circuit_id=row["circuit_id"], turns_per_m2=row["turns_per_m2"])
        regions.append(r)
    return dict(label=value["label"], parameters=deepcopy(value["parameters"]),
        materials={k: v.get("id", "nominal-"+k) for k,v in value["materials"].items()},
        regions=regions, stock_parts=[{k: deepcopy(p[k]) for k in
            ("id", "kind", "size_m", "at_m", "material", "group", "role")}
            for p in value["stock_parts"]],
        units_per_car=value["units_per_car"],
        unknown_stock=[{k: deepcopy(v[k]) for k in ("id","scope","quantity")}
                       for v in value["unknown_stock"]])


def bounded_variants(*, root=ROOT):
    """Eight declared samples plus one segmented PM comparison; no optimiser."""
    rows = []
    for family in ("A", "B", "C", "D"):
        for name, facing in (("edge-facing", .34), ("wide-facing", .50)):
            value = candidate(family, {"facing_width_m": facing}, root=root)
            value["sample_id"] = family + "/" + name
            rows.append(value)
    value = candidate("B-segmented", {"facing_width_m": .34}, root=root)
    value["sample_id"] = "B/segmented-edge-facing"
    rows.append(value)
    return rows


def native_definition(value):
    """Actual stock boxes for one local coupon, compatible with native.generate.

    The 2D copper windows are deliberately NOT emitted as solid copper.  Every
    conductor/end-turn box carries its actual density/mass.  No cosmetic box is
    assigned unknown hardware mass.  The concrete beam is an external assembly.
    """
    _validate(value)
    return dict(id="OSR-PASSIVE-FACING-" + value["label"],
                geometry_sha256=value["geometry_sha256"],
                parts=deepcopy(value["stock_parts"]),
                modelled_material_mass_kg=math.fsum(q["mass_kg"] for q in value["stock_parts"]),
                train_known_mass_kg=value["stock"]["train_known_mass_kg_per_module"],
                retain_native_tessellation=True, interference_roles=[],
                unknown_installed_inventory=deepcopy(value["unknown_installed_inventory"]),
                scope="One local module and one same-length facing coupon, not a complete car/guideway or installed acceptance", **FLAGS)


def _validate(value):
    if value.get("schema") != SCHEMA:
        raise ValueError("passive-facing geometry schema required")
    raw = deepcopy(value)
    expected = raw.pop("geometry_sha256", None)
    raw.pop("sample_id", None)
    if expected != sha256(encoded(raw)).hexdigest():
        raise ValueError("physical geometry/stock identity differs")
    if value.get("physical_geometry_sha256") != sha256(encoded(physical_definition(value))).hexdigest():
        raise ValueError("physical geometry identity differs")
    if any(value.get(k) is not False for k in FLAGS):
        raise ValueError("geometry cannot release physical hardware")


def curve_screen(value, radius_m, *, lateral_displacement_m=.006):
    """Exact planar chord/radius necessary overlap, not a vehicle dynamics test."""
    _validate(value)
    R = _positive(radius_m, "radius_m")
    lateral = abs(_finite(lateral_displacement_m, "lateral_displacement_m"))
    p, packing = value["parameters"], value["packing"]
    pole_outer = 2 * p["pole_width_m"] + p["pole_gap_m"] + 2 * p["pole_shoe_overhang_m"]
    inner_radius = R - p["bank_offset_m"] - pole_outer / 2
    frame = p["car_length_m"]
    if inner_radius <= frame / 2:
        raise ValueError("curve radius must exceed bank/frame envelope")
    occupied_half = max(abs(x) for x in packing["module_centres_x_m"]) + packing["physical_module_envelope_x_m"] / 2
    # Exact minimax translation for a straight frame: solving residual at x=0
    # = minus residual at endpoint gives t=x_end^2/(4*inner_radius).
    rigid_error = occupied_half ** 2 / (4 * inner_radius)
    short_error = (packing["physical_module_envelope_x_m"] / 2) ** 2 / (4 * inner_radius)
    # Rationalised sagitta avoids catastrophic cancellation at large radii.
    chord_sagitta = (frame / 2) ** 2 / (inner_radius + math.sqrt(inner_radius ** 2 - (frame / 2) ** 2))
    centre_sagittae = [x ** 2 / (inner_radius + math.sqrt(inner_radius ** 2 - x ** 2)) for x in packing["module_centres_x_m"]]
    recenter = (max(centre_sagittae) + min(centre_sagittae)) / 2
    slide = max(abs(s - recenter) for s in centre_sagittae)
    yaw = max(abs(math.asin(x / inner_radius)) for x in packing["module_centres_x_m"])
    allowance = (p["facing_width_m"] - pole_outer) / 2
    independent = packing["independent_carriers"]
    error = short_error if independent else rigid_error
    margin = allowance - lateral - error
    return dict(radius_m=R, pole_outer_width_m=pole_outer,
        facing_edge_allowance_m=allowance, lateral_test_m=lateral,
        rigid_frame_chord_sagitta_m=chord_sagitta,
        same_rigid_frame_module_error_m=rigid_error,
        independent_local_module_error_m=short_error,
        independently_required_centre_slide_m=slide,
        independently_required_yaw_rad=yaw,
        declared_carrier_lateral_stroke_m=p["carrier_lateral_stroke_m"] if independent else None,
        selected_envelope_error_m=error, necessary_overlap_margin_m=margin,
        necessary_overlap_pass=margin >= 0 and (not independent or slide <= p["carrier_lateral_stroke_m"]),
        shared_rigid_frame_warning="Short blocks on the same rigid frame retain the whole frame's radial error",
        scope="Necessary horizontal overlap only; stroke/load retention, bogie/body dynamics, vertical grade and roll remain open", **FLAGS)


def attachment_screen(value, force_z_n, *, lateral_force_n=0., anchor_pitch_x_m=.5,
                      anchor_rows_y_m=.24, anchors_per_group=4,
                      load_height_m=.15, elastic_modulus_pa=200e9,
                      allowable_stress_pa=235e6/1.5):
    """Necessary strip-bending/anchor-tension demand; no anchorage capacity."""
    _validate(value)
    force = _positive(force_z_n, "force_z_n")
    Fy = abs(_finite(lateral_force_n, "lateral_force_n"))
    ax = _positive(anchor_pitch_x_m, "anchor_pitch_x_m")
    ay = _positive(anchor_rows_y_m, "anchor_rows_y_m")
    E = _positive(elastic_modulus_pa, "elastic_modulus_pa")
    allowable = _positive(allowable_stress_pa, "allowable_stress_pa")
    h = _positive(load_height_m, "load_height_m")
    if type(anchors_per_group) is not int or anchors_per_group < 2 or anchors_per_group % 2:
        raise ValueError("even positive anchor group required")
    p = value["parameters"]
    if ay > p["facing_width_m"]:
        raise ValueError("anchor rows exceed facing width")
    pressure = force / (p["length_x_m"] * p["facing_width_m"])
    thickness = p["facing_thickness_m"]
    moment_per_m = pressure * ay ** 2 / 8
    stress = 6 * moment_per_m / thickness ** 2
    deflection = 5 * pressure * ay ** 4 / (32 * E * thickness ** 3)
    group_load = force * min(ax / p["length_x_m"], 1.)
    # Moment raises one anchor row's demand; no fictitious concrete strength.
    row_tension = group_load / 2 + Fy * min(ax / p["length_x_m"], 1.) * h / ay
    return dict(assumed_pressure_pa=pressure, plate_strip_moment_n_m_per_m=moment_per_m,
        plate_bending_stress_pa=stress, plate_deflection_m=deflection,
        plate_elastic_necessary_pass=stress <= allowable,
        anchor_group_vertical_load_n=group_load,
        most_loaded_anchor_tension_n=row_tension / (anchors_per_group / 2),
        concrete_anchorage_capacity_n=None, concrete_anchorage_qualified=False,
        installed_anchor_mass_kg=None,
        load_path=["magnetic traction to downward steel facing", "facing plate strip to cast-in steel attachments", "cast-in anchorage/reinforcement to concrete beam", "beam/bearings to substructure"],
        omitted=["prying/contact pressure distribution", "local pole loads", "anchor/concrete breakout and splitting", "fatigue/corrosion/fire", "cast-in detail and grout/shim load transfer"],
        sources=[FHWA_BEARINGS], **FLAGS)


def flexure_screen(value, angle_rad, *, lateral_translation_m=0.,
                   elastic_modulus_pa=200e9, allowable_stress_pa=235e6/1.5):
    """Constant-section elastic leaf, pure bending and clamped translation bounds.

    The yaw leaf is not assumed to carry vertical vehicle load in its weak
    buckling direction.  No fatigue, retention or multi-axis capacity is passed.
    """
    _validate(value)
    theta = abs(_finite(angle_rad, "angle_rad"))
    delta = abs(_finite(lateral_translation_m, "lateral_translation_m"))
    E = _positive(elastic_modulus_pa, "elastic_modulus_pa")
    allowable = _positive(allowable_stress_pa, "allowable_stress_pa")
    p = value["parameters"]
    L, b, t = p["flexure_length_m"], p["flexure_width_m"], p["flexure_thickness_m"]
    I = b * t ** 3 / 12
    bending = E * t * theta / (2 * L)
    translation = 3 * E * t * delta / L ** 2
    # Summation is a conservative necessary scalar bound, not an actual
    # combined nonlinear hinge/translation mechanism calculation.
    return dict(leaf_second_moment_m4=I, per_leaf_rotational_stiffness_n_m_rad=E * I / L,
        leaves=p["flexures_per_module"], pure_bending_stress_pa=bending,
        clamped_translation_stress_pa=translation,
        summed_elastic_stress_bound_pa=bending + translation,
        elastic_necessary_pass=bending + translation <= allowable,
        pinned_weak_axis_euler_load_n_per_leaf=math.pi ** 2 * E * I / L ** 2,
        fatigue_qualified=False, multiaxis_load_capacity_n=None,
        retention_qualified=False, geometry_nonlinearity_open=(theta > .1 or delta > L * .05),
        scope="First elastic bounds only; actual material, transitions, end restraint, parasitic motion, buckling and fatigue require tests",
        sources=[DLR_FLEXURES], **FLAGS)


def factory_datums(value):
    _validate(value)
    return dict(records=[
        dict(id="beam/seat", datum="surveyed concrete cast-in seat", measured_m=None,
             adjustment="cast-in seat/grout datum; concrete tolerance not magnetic-gap tolerance"),
        dict(id="facing/underside", datum="factory-ground facing underside z=0", measured_m=None,
             proposed_flatness_m=.0005, acceptance_approved=False),
        dict(id="facing/site-shim", datum="underside relative to beam survey", measured_m=None,
             proposed_shim_range_m=[-.015,.015], shim_material_mass_kg=None, acceptance_approved=False),
        dict(id="train/pole", datum="module pole top z=-reference_gap", measured_m=None,
             reference_gap_m=value["reference_gap_m"], proposed_gap_survey_error_m=.001,
             acceptance_approved=False)],
        scope="Proposed datum/adjustment records, not FHWA numeric tolerance adoption or measured site fit",
        sources=[FHWA_TOLERANCES, FHWA_BEARINGS], **FLAGS)


def replacement_mass_comparison(value, *, root=ROOT):
    """Replace ONLY the actually counted canonical support module stock.

    Keep the canonical residual allocation and passive propulsion band intact.
    Guideway steel is never subtracted from a vehicle.  Unknown new hardware
    prevents this material subtotal becoming an installed car mass or CG.
    """
    _validate(value)
    from engineering.ferrite_maglev import candidate_magnetics as canonical
    if Path(canonical.ROOT).resolve() != Path(root).resolve():
        raise ValueError("canonical replacement comparison source root differs")
    old = canonical.definition()
    old_count = len(old["module_placements_m"])
    removed = old_count * old["module"]["mass_kg"]
    added = value["stock"]["train_known_mass_kg_per_car"]
    return dict(source_configuration_sha256=old["configuration_sha256"],
        source_input_sha256=old["source_sha256"],
        original_counted_module_mass_kg=old["module"]["mass_kg"],
        original_module_count_per_car=old_count,
        removed_counted_stock_kg_per_car=removed,
        added_known_stock_kg_per_car=added,
        canonical_tare_kg_per_car=old["controlled_tare_kg"],
        canonical_aw3_kg_per_car=old["controlled_aw3_kg"],
        material_subtotal_tare_kg_per_car=old["controlled_tare_kg"] - removed + added,
        material_subtotal_aw3_kg_per_car=old["controlled_aw3_kg"] - removed + added,
        retained_allocations_unchanged=True, removed_guideway_mass_kg=0.,
        unknown_installed_inventory=deepcopy(value["unknown_installed_inventory"]),
        installed_tare_kg_per_car=None, installed_aw3_kg_per_car=None,
        installed_cg_m=None, scope="Material replacement comparison only; no installed mass or guidance elimination saving", **FLAGS)
