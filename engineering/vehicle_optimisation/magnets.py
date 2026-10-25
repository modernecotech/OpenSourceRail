"""Named NdFeB and genuine transverse rotating-array research comparisons.

All magnets and coils are onboard. The guideway contains passive steel only.
Four/eight *segments per complete magnetic rotation* are used, rather than
tilting three pieces of an otherwise conventional vertical pole. This is an
infinite-travel-length 2D study; finite ends, joints and travel drag are unknown.
No material certificate, price, origin, installed mass or physical acceptance
is inferred from a manufacturer's published typical/minimum data.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path

from engineering.passive_suspension import fields
from engineering.passive_suspension import geometry as passive
from engineering.design_search import storage

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "osr-vehicle-magnet-candidate/1"
FLAGS = dict(physical_accepted=False, design_complete=False, adopted=False,
             installed_mass_complete=False, manufacturing_release=False)
PDF_BASE = "https://www.arnoldmagnetics.com/wp-content/uploads/2017/11/"
GRADES = {
    "Arnold-N42SH": dict(id="Arnold-N42SH", chemistry="sintered-NdFeB", manufacturer="Arnold Magnetic Technologies",
        grade="N42SH", br_20c_t=1.28, br_nominal_20c_t=1.31, br_max_20c_t=1.34,
        hcj_20c_a_m=1592000., br_temperature_coefficient_per_k=-.0012,
        hcj_temperature_coefficient_per_k=-.0055, maximum_temperature_c=150.,
        source=PDF_BASE+"N42SH-151021.pdf", source_revision="020821",
        remote_pdf_sha256="c0bd4c03ba5896d2de9cbdd4d5ac9a1e16da4815a4cfdd8bcb132918c8953a36"),
    "Arnold-N35UH": dict(id="Arnold-N35UH", chemistry="sintered-NdFeB", manufacturer="Arnold Magnetic Technologies",
        grade="N35UH", br_20c_t=1.17, br_nominal_20c_t=1.21, br_max_20c_t=1.25,
        hcj_20c_a_m=1990000., br_temperature_coefficient_per_k=-.0012,
        hcj_temperature_coefficient_per_k=-.0051, maximum_temperature_c=180.,
        source=PDF_BASE+"N35UH-151021.pdf", source_revision="210607",
        remote_pdf_sha256="015a8654d518c0eb3a6a1718064e4543bbe71ecf716bfce3d0b437b6a33d13f1"),
}
for _grade in GRADES.values():
    _grade.update(density_kg_m3=7600., density_basis="Manufacturer typical 7.6 g/cm3; not a guaranteed batch value",
        br_basis="Published minimum at20C; nominal and maximum retained separately",
        hcj_basis="Published minimum intrinsic coercivity at20C",
        hcj_tolerance_a_m=0., minimum_temperature_c=20.,
        coefficient_basis="Published reversible coefficients over20C to grade temperature limit; linear interpolation is a study approximation",
        recoil_relative_permeability=1.05,
        recoil_basis="Declared linear-recoil study assumption1.05, not measured Arnold batch permeability",
        demag_hcj_fraction_limit=.8,
        demag_basis="Unchanged conservative80% Hcj screening factor; not a measured knee or irreversible-demagnetisation model",
        curve_basis="Manufacturer plotted curves use nominal Br/minimum Hci and depend on size/shape; not digitised or represented as measured coupon data",
        supplier_quote=None, supplier_origin=None, qualified=False)


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)+"\n").encode()


def identity(value):
    return sha256(encoded(value)).hexdigest()


def source_paths():
    return sorted(set([Path(__file__).resolve(), Path(passive.__file__).resolve(),
                       Path(fields.__file__).resolve(), fields.MATERIAL_SOURCE,
                       Path(storage.__file__).resolve()]))


def sources():
    return {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest() for p in source_paths()}


def material_sources():
    """Named grade declarations with minimum/typical distinctions and provenance."""
    value = deepcopy(GRADES)
    ferrite = passive.material_table()["ferrite"]
    ferrite.update(chemistry="hard-ferrite", br_basis="Retained canonical FB9B published proxy",
                   density_basis="Retained canonical nominal5000kg/m3", qualified=False)
    value["TDK-FB9B-recoil-proxy"] = ferrite
    return value


def prior_work():
    """Specific retained implementations; their geometry/results do not transfer."""
    return [dict(path="engineering/ferrite_maglev/candidate_magnetics.py", functions=["_halbach_band","_halbach_coefficients","spatial_band_coupon"],
                 scope="Four-cardinal ferrite propulsion array rotating in travel/local-normal plane; Fourier and independent spatial coupons; demagnetisation failure retained",
                 transferable_force_result=False),
            dict(path="engineering/ferrite_maglev/station_structure.py", function="linear_candidates",
                 scope="Finite block/dipole and orientation seeds; not an executed NdFeB transverse steel-facing qualification",
                 transferable_force_result=False),
            dict(path="engineering/passive_suspension/geometry.py", family="B-segmented",
                 scope="Three tilted pieces per vertical ferrite pole, explicitly only Halbach-like; no full rotating array",
                 transferable_force_result=False),
            dict(finding="No named-grade executed NdFeB train/steel-facing spatial study found in the inspected current engineering sources/history; NdFeB appears in unrelated reference discussion",
                 scope="Repository inspection, not a claim about all possible deleted external work")]


def segmentation_factor(segments):
    if segments not in (4,8):
        raise ValueError("four/eight segments per full rotation required")
    return math.sin(math.pi/segments)/(math.pi/segments)


def analytical_infinite_halbach_field_T(br_T, thickness_m, period_m, gap_m, segments):
    """Fundamental amplitude for unit-recoil infinite periodic free-air slab.

    It is an analytical seed, not the finite-width/steel force or an upper bound
    on every local field. Higher harmonics, ends and magnetic iron are omitted.
    """
    if any(not math.isfinite(v) for v in (br_T,thickness_m,period_m,gap_m)) or min(br_T,thickness_m,period_m)<=0 or gap_m<0:
        raise ValueError("positive finite PM/slab dimensions and nonnegative gap required")
    k = 2*math.pi/period_m
    return br_T*(1-math.exp(-k*thickness_m))*math.exp(-k*gap_m)*segmentation_factor(segments)


def rotating_directions(segments=8, periods=1, *, strong_side="up"):
    """Cell-centred full rotations: My=-sin(ky), Mz=cos(ky) faces up."""
    segmentation_factor(segments)
    if periods not in (1,2) or strong_side not in ("up","down"):
        raise ValueError("one/two periods and up/down strong side required")
    sign = -1 if strong_side == "up" else 1
    return [[sign*math.sin(-math.pi*periods+2*math.pi*(j+.5)/segments),
             math.cos(-math.pi*periods+2*math.pi*(j+.5)/segments)]
            for j in range(segments*periods)]


def _box(uid, size, at, material, density, group, role, **extra):
    return passive._box(uid,size,at,material,density,group,role,**extra)


def _recompute_part(part, density):
    old_density = part["density_kg_m3"]
    part["density_kg_m3"] = density
    part["mass_kg"] = part["volume_m3"]*density
    part["inertia_kg_m2"] = [[v*density/old_density for v in row] for row in part["inertia_kg_m2"]]


CATALOGUE = [
    ("F-iron-equal", "iron-backed", "TDK-FB9B-recoil-proxy", {}),
    ("N42-iron-equal", "iron-backed", "Arnold-N42SH", {}),
    ("N35-iron-equal", "iron-backed", "Arnold-N35UH", {}),
    ("N42-iron-compact", "iron-backed", "Arnold-N42SH", dict(pm_thickness_m=.025,return_thickness_m=.035,pole_shoe_thickness_m=.012)),
    ("N42-H4", "planar-halbach", "Arnold-N42SH", dict(segments=4)),
    ("N42-H8", "planar-halbach", "Arnold-N42SH", dict(segments=8)),
    ("N35-H8", "planar-halbach", "Arnold-N35UH", dict(segments=8)),
    ("N42-H8-yoke", "planar-halbach", "Arnold-N42SH", dict(segments=8,yoke_m=.015)),
    ("N35-H8-yoke", "planar-halbach", "Arnold-N35UH", dict(segments=8,yoke_m=.015)),
    ("N42-H8-half-volume", "planar-halbach", "Arnold-N42SH", dict(segments=8,yoke_m=.015,magnet_volume_m3=.006)),
    ("F-H8", "planar-halbach", "TDK-FB9B-recoil-proxy", dict(segments=8)),
    ("N42-H8-two-period", "planar-halbach", "Arnold-N42SH", dict(segments=8,periods=2)),
]


def _finish(sample, family, grade_id, params, regions, parts, circuits, packing, unknown):
    mats = passive.material_table()
    grade = material_sources()[grade_id]
    materials = {grade_id:grade, "steel":mats["steel"], "copper":mats["copper"],
                 "aluminium":dict(id="declared-aluminium-stock",density_kg_m3=2700.,kind="aluminium",source="Nominal geometry mass assumption, alloy/certificate unconfirmed")}
    for part in parts:
        if part["material"] == "ferrite":
            part["material"] = grade_id
            _recompute_part(part, grade["density_kg_m3"])
    for region in regions:
        if region["material"] == "ferrite":
            direction = [region.get("Br_y_T",0.),region.get("Br_z_T",0.)]
            norm = math.hypot(*direction)
            if norm:
                direction = [v/norm for v in direction]
            region.update(material=grade_id, Br_y_T=direction[0]*grade["br_20c_t"],Br_z_T=direction[1]*grade["br_20c_t"])
    by_id = {r["id"]:r for r in regions}
    for part in parts:
        if part["material"] == grade_id:
            region_id = part["id"].split("/block-")[0]
            r = by_id[region_id]
            direction = [r["Br_y_T"]/grade["br_20c_t"],r["Br_z_T"]/grade["br_20c_t"]]
            part["magnetization_vector"] = [0.,*direction]
            part["Br_y_T"],part["Br_z_T"] = r["Br_y_T"],r["Br_z_T"]
    train = [q for q in parts if q["group"] == "train"]
    mass = math.fsum(q["mass_kg"] for q in train)
    magnet_volume = math.fsum(q["volume_m3"] for q in train if q["material"] == grade_id)
    facing = math.fsum(q["mass_kg"] for q in parts if q["group"] == "guideway")
    envelope = max(q["at_m"][0]+q["size_m"][0] for q in train)-min(q["at_m"][0] for q in train)
    if envelope > 17/12:
        raise ValueError("exact end-turn envelope exceeds17m/12 packing pitch")
    packing = dict(packing, banks_per_car=2,modules_per_bank=12,modules_per_car=24,
                   car_length_m=17.,pitch_m=17/12,physical_module_envelope_x_m=envelope,
                   longitudinal_clearance_m=17/12-envelope)
    value = dict(schema=SCHEMA,sample_id=sample,family=family,grade_id=grade_id,
        parameters=params,length_x_m=1.,reference_gap_m=.012,origin_yz_m=[0.,-.012],
        regions=regions,materials=materials,circuits=circuits,stock_parts=parts,packing=packing,
        stock=dict(train_known_mass_kg_per_module=mass,train_known_mass_kg_per_car=mass*24,
                   magnet_volume_m3_per_module=magnet_volume,magnet_mass_kg_per_module=magnet_volume*grade["density_kg_m3"],
                   copper_mass_kg_per_module=math.fsum(q["mass_kg"] for q in train if q["material"]=="copper"),
                   steel_mass_kg_per_module=math.fsum(q["mass_kg"] for q in train if q["material"]=="steel"),
                   facing_mass_kg_per_m_per_bank=facing,
                   scope="Listed exact stock only; omitted installed hardware stays unknown"),
        unknown_installed_inventory=unknown,installed_mass_kg_per_car=None,
        steel_material_hold="Canonical electrical-steel proxy is not a certified solid facing/yoke DC grade",
        control_hold="Counted winding stock does not establish useful control authority, current, heat or fault response",
        drag_N=None,finite_x_end_joint_losses_W=None,**FLAGS)
    value["physical_id"] = identity(physical_definition(value))
    value["bundle_sha256"] = identity(value)
    return value


def _build(entry):
    sample,family,grade_id,custom = entry
    if family == "iron-backed":
        base = passive.candidate("B",custom)
        return _finish(sample,family,grade_id,deepcopy(base["parameters"]),
                       deepcopy(base["regions"]),deepcopy(base["stock_parts"]),deepcopy(base["circuits"]),
                       deepcopy(base["packing"]),deepcopy(base["unknown_installed_inventory"]))
    p = dict(segments=8,periods=1,width_m=.32,magnet_volume_m3=.012,yoke_m=0.,backing_m=.006,turns=60)
    p.update(custom)
    thickness = p["magnet_volume_m3"]/p["width_m"]
    p["pm_thickness_m"] = thickness
    gap = .012
    bottom = -gap-thickness
    mats = passive.material_table()
    regions = [passive._region("guideway/facing","steel","guideway",[-.25,.25,0.,.035])]
    parts = [_box("guideway/facing",[1.,.5,.035],[-.5,-.25,0.],"steel",mats["steel"]["density_kg_m3"],"guideway","passive-facing")]
    directions = rotating_directions(p["segments"],p["periods"])
    width = p["width_m"]/len(directions)
    for j,direction in enumerate(directions):
        y = -p["width_m"]/2+j*width
        uid = f"train/pm-{j:02d}"
        regions.append(dict(id=uid,material="ferrite",group="train",bounds_yz_m=[y,y+width,bottom,-gap],
                            Br_y_T=direction[0],Br_z_T=direction[1],J_x_A_m2=0.))
        # Discrete50mm longitudinal stock blocks, nominally touching. Their
        # finite-x joints/adhesive remain outside the infinite-x field model.
        for k in range(20):
            parts.append(_box(uid+f"/block-{k}",[.05,width,thickness],[-.5+k*.05,y,bottom],"ferrite",5000.,"train","rotating-permanent-magnet",
                              block_joints="Nominal touching50mm blocks; joint/coating/retention3D effects unknown"))
    if p["yoke_m"]:
        uid = "train/back-yoke"
        regions.append(passive._region(uid,"steel","train",[-p["width_m"]/2,p["width_m"]/2,bottom-p["yoke_m"],bottom]))
        parts.append(_box(uid,[1.,p["width_m"],p["yoke_m"]],[-.5,-p["width_m"]/2,bottom-p["yoke_m"]],"steel",mats["steel"]["density_kg_m3"],"train","back-yoke"))
    bbottom = bottom-p["yoke_m"]-p["backing_m"]
    regions.append(passive._region("train/backing","aluminium","train",[-p["width_m"]/2-.02,p["width_m"]/2+.02,bbottom,bbottom+p["backing_m"]]))
    parts.append(_box("train/backing",[1.,p["width_m"]+.04,p["backing_m"]],[-.5,-p["width_m"]/2-.02,bbottom],"aluminium",2700.,"train","nonmagnetic-stock-backing"))
    winding_params = dict(passive.DEFAULTS,length_x_m=1.)
    rr,pp,coil = passive._winding("array-control",0.,p["width_m"],bottom,thickness,p["turns"],winding_params,mats["copper"]["density_kg_m3"])
    regions.extend(rr);parts.extend(pp)
    unknown = [dict(id="module/retention-coating-adhesive-fasteners",scope="per-module",status="unknown",quantity=1,mass_kg=None,
                    reason="No coating, calibrated retaining preload, adhesive, corrosion barrier or load-certified magnet retention drawn"),
               dict(id="module/cooling-insulation-leadouts-protection",scope="per-module",status="unknown",quantity=1,mass_kg=None,
                    reason="Discrete conductor transitions, insulation, thermal hardware and electrical protection incomplete"),
               dict(id="car/gap-guidance-sensors-control",scope="per-car",status="unknown",quantity=1,mass_kg=None,
                    reason="Exterior coil control authority, damping, sensors, redundancy and fault response not established"),
               dict(id="guideway/anchors-grout-shims",scope="per-beam-span",status="unknown",quantity=1,mass_kg=None,
                    reason="Passive facing attachment to ordinary concrete remains unsized")]
    packing = dict(field_unit="one local transverse array on ONE facing bank",bank_centres_y_m=[-.88,.88])
    return _finish(sample,family,grade_id,p,regions,parts,[coil],packing,unknown)


def candidates():
    return [_build(entry) for entry in CATALOGUE]


def physical_definition(value):
    regions = []
    for r in value["regions"]:
        item = {k:deepcopy(r[k]) for k in ("id","material","group","bounds_yz_m")}
        b = math.hypot(r.get("Br_y_T",0),r.get("Br_z_T",0))
        if b:
            item["magnetisation_direction_yz"] = [r.get("Br_y_T",0)/b,r.get("Br_z_T",0)/b]
        if r.get("turns_per_m2"):
            item.update(circuit_id=r["circuit_id"],turns_per_m2=r["turns_per_m2"])
        regions.append(item)
    return dict(family=value["family"],grade_id=value["grade_id"],parameters=value["parameters"],regions=regions,
                stock_parts=[{k:deepcopy(p[k]) for k in ("id","kind","size_m","at_m","material","group","role")}
                             for p in value["stock_parts"]],packing=value["packing"],
                unknown_stock=[{k:deepcopy(q[k]) for k in ("id","scope","quantity")} for q in value["unknown_installed_inventory"]])


def validate(value):
    if value.get("schema") != SCHEMA or value.get("physical_id") != identity(physical_definition(value)):
        raise ValueError("magnet physical definition differs")
    raw = deepcopy(value)
    digest = raw.pop("bundle_sha256",None)
    if identity(raw) != digest:
        raise ValueError("magnet stock/material bundle differs")
    if value["grade_id"] not in material_sources() or value["materials"][value["grade_id"]] != material_sources()[value["grade_id"]]:
        raise ValueError("unsupported or altered named-grade data")
    for key in FLAGS:
        if value.get(key) is not False:
            raise ValueError("magnet bundle cannot confer physical release")
    entry = next((row for row in CATALOGUE if row[0] == value.get("sample_id")),None)
    if entry is None or value != _build(entry):
        raise ValueError("unsupported modified stock/field/material family bundle")
    return value


def field_geometry(value):
    """Explicit compatibility adapter to the frozen generic recoil PDE branch.

    The old solver's internal branch name is 'ferrite'. It implements isotropic
    linear recoil, not a ferrite-only equation. Actual region material names,
    Br/Hcj/coefficients/density and source remain NdFeB. The additional ferrite
    key is a coercivity-screen compatibility alias, never another stock item.
    """
    validate(value)
    grade = deepcopy(value["materials"][value["grade_id"]])
    mats = deepcopy(value["materials"])
    grade.update(kind="ferrite",relative_permeability=grade["recoil_relative_permeability"])
    mats[value["grade_id"]] = grade
    mats["ferrite"] = deepcopy(grade)
    out = {k:deepcopy(value[k]) for k in ("length_x_m","reference_gap_m","origin_yz_m","regions","circuits")}
    out["materials"] = mats
    out["recoil_adapter"] = dict(active_material_id=value["grade_id"],active_chemistry=grade["chemistry"],
        computational_kind="linear-recoil-permanent-magnet",frozen_solver_branch="ferrite",
        coercivity_alias="materials.ferrite",alias_creates_stock=False,
        inherited_material_proxy_metadata="Frozen solver material_proxy retains its canonical steel/ferrite reference; declared_material_definitions and this adapter specify the active grade")
    return out


def native_definition(value):
    validate(value)
    return dict(id="OSR-VEHICLE-MAGNET-"+value["sample_id"],physical_id=value["physical_id"],
                parts=deepcopy(value["stock_parts"]),modelled_material_mass_kg=math.fsum(p["mass_kg"] for p in value["stock_parts"]),
                train_known_mass_kg=value["stock"]["train_known_mass_kg_per_module"],
                unknown_installed_inventory=deepcopy(value["unknown_installed_inventory"]),
                retain_native_tessellation=True,interference_roles=[],**FLAGS)


def replacement_mass(value, *, base_empty_kg, removed_support_kg, payload_kg=12000.):
    validate(value)
    for amount in (base_empty_kg,removed_support_kg,payload_kg):
        if not math.isfinite(amount) or amount<0:
            raise ValueError("finite nonnegative mass inputs required")
    if removed_support_kg>base_empty_kg:
        raise ValueError("removed support stock cannot exceed source empty mass")
    tare = base_empty_kg-removed_support_kg+value["stock"]["train_known_mass_kg_per_car"]
    return dict(material_subtotal_empty_kg_per_car=tare,material_subtotal_aw3_kg_per_car=tare+payload_kg,
                source_empty_kg_per_car=base_empty_kg,removed_support_kg_per_car=removed_support_kg,
                added_known_support_kg_per_car=value["stock"]["train_known_mass_kg_per_car"],
                installed_mass_kg_per_car=None,unknown_installed_inventory=deepcopy(value["unknown_installed_inventory"]),**FLAGS)


def comparison(value, raw_result, *, aw3_mass_kg_per_car=None):
    validate(value)
    fg = field_geometry(value)
    if raw_result["geometry_id"] != fields._digest(fg):
        raise ValueError("field result belongs to another physical geometry/material adapter")
    payload = deepcopy(raw_result)
    result_id = payload.pop("result_id",None)
    if result_id != fields._digest(payload):
        raise ValueError("field result payload digest differs")
    grade = value["materials"][value["grade_id"]]
    op = raw_result["operating_point"]
    temp = op["temperature_C"]
    hcj = (grade["hcj_20c_a_m"]-grade.get("hcj_tolerance_a_m",0))*(1+grade["hcj_temperature_coefficient_per_k"]*(temp-20))
    margin = raw_result["PM_H_parallel_min_A_per_m"]+grade["demag_hcj_fraction_limit"]*hcj
    demand = None if aw3_mass_kg_per_car is None else 1.3*aw3_mass_kg_per_car*9.80665/value["packing"]["modules_per_car"]
    if aw3_mass_kg_per_car is not None and (not math.isfinite(aw3_mass_kg_per_car) or aw3_mass_kg_per_car<=0):
        raise ValueError("positive finite AW3 comparison mass required")
    result = dict(physical_id=value["physical_id"],sample_id=value["sample_id"],grade_id=value["grade_id"],
                  active_chemistry=grade["chemistry"],operating_point=op,stock=deepcopy(value["stock"]),
                  field_result_id=raw_result["result_id"],F_z_N=raw_result["F_z_N"],
                  steel_B_peak_T=raw_result["steel_B_peak_T"],PM_H_parallel_min_A_per_m=raw_result["PM_H_parallel_min_A_per_m"],
                  PM_recoil_margin_A_per_m=margin,temperature_in_declared_range=grade["minimum_temperature_c"]<=temp<=grade["maximum_temperature_c"],
                  conditional_recoil_screen_pass=margin>=0 and grade["minimum_temperature_c"]<=temp<=grade["maximum_temperature_c"],
                  steel_saturation_screen_pass=raw_result["steel_B_peak_T"]<=2.2,
                  steel_saturation_basis="Unchanged2.2T research guard; linear iron is not validated by satisfying this guard",
                  interpolation_usable=raw_result["interpolation_usable"],numerical_status=raw_result["numerical_status"],
                  comparison_aw3_kg_per_car=aw3_mass_kg_per_car,required_1_3_aw3_N_per_module=demand,
                  lift_to_1_3_aw3_ratio=None if demand is None else raw_result["F_z_N"]/demand,
                  field_scope="One module, infinite travel extent; control/damping,3D/end/joint/drag remain open",**FLAGS)
    return result


def evaluate_reference(value, *, gap_m=.012,temperature_C=20.,settings=None):
    before = sources()
    cfg = dict(mesh_size_m=.005,outer_margin_m=.25,max_nodes=180000,check_convergence=True,steel_model="linear_bound")
    if settings:
        cfg.update(settings)
    raw = fields.solve(field_geometry(value),gap_m=gap_m,temperature_C=temperature_C,settings=cfg)
    if sources()!=before:
        raise ValueError("magnet evaluator sources changed during solve")
    return dict(physical_id=value["physical_id"],source_sha256=before,raw_result=raw,
                comparison=comparison(value,raw),**FLAGS)


def reference_schedule(values=None):
    """32 checked linear points, leaving four of36 for justified follow-up."""
    values = candidates() if values is None else values
    by_name = {v["sample_id"]:v for v in values}
    plan = [(name,.012,temp) for name in by_name for temp in (20.,80.)]
    for name in ("N42-iron-equal","N42-H4","N42-H8","N35-H8"):
        if name in by_name:
            plan.extend((name,gap,20.) for gap in (.008,.020))
    if len(plan)>36:
        raise ValueError("checked field point cap exceeded")
    return plan


def study(output=None):
    """Execute the declared32-point bounded study and retain raw spatial outputs."""
    before = sources()
    values = candidates()
    by_name = {v["sample_id"]:v for v in values}
    rows = []
    output = None if output is None else Path(output)
    if output:
        output.mkdir(parents=True,exist_ok=True)
    for index,(name,gap,temp) in enumerate(reference_schedule(values)):
        try:
            row = dict(execution_status="executed",sample_id=name,gap_m=gap,temperature_C=temp,
                       **evaluate_reference(by_name[name],gap_m=gap,temperature_C=temp))
        except (ValueError,RuntimeError) as error:
            row = dict(execution_status="refused",sample_id=name,gap_m=gap,temperature_C=temp,
                       error_type=type(error).__name__,error=str(error),source_sha256=before,**FLAGS)
        rows.append(row)
        if output:
            storage.atomic_immutable(output/f"case-{index:02d}.json",encoded(row))
    if sources()!=before:
        raise ValueError("magnet study sources changed during execution")
    result = dict(schema="osr-vehicle-magnet-study/1",source_sha256=before,material_sources=material_sources(),
                  prior_work=prior_work(),candidates=values,rows=rows,total_checked_reference_points=len(rows),
                  maximum_checked_reference_points=36,comparison_basis="Equal PM volume .012m3 unless compact/half-volume explicitly named; all listed copper/iron/backing stock counted",
                  physical_confirmation=False,**FLAGS)
    result["study_id"] = identity(result)
    if output:
        storage.atomic_immutable(output/"study.json",encoded(result))
    return result
