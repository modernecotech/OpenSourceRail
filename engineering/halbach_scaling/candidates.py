"""Counted larger Halbach proposals against one unchanged passive steel facing.

These bundles describe stock and a local magnetic interface, not an equipped
vehicle. Numerical models and their hypotheses receive separate identities.
"""
from copy import deepcopy
from hashlib import sha256
import math
from pathlib import Path

from engineering.vehicle_optimisation import magnets

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "osr-halbach-scaling-candidates/1"
PARENT_ID = "ff677ea60334a09828e70df8e89f8a9a8726e38da171cfc0f73c5f60221d2c0e"
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             configuration_adopted=False, installed_mass_complete=False,
             force_map_generated=False, hover_executed=False)


def encoded(value):
    return magnets.encoded(value)


def identity(value):
    return magnets.identity(value)


def source_paths():
    return sorted(set([Path(__file__).resolve(), *magnets.source_paths()]))


def source_snapshot(root=ROOT):
    """Executing implementation and explicitly rooted material bytes must agree."""
    root = Path(root).resolve()
    result = {}
    for path in source_paths():
        if path.is_symlink():
            raise ValueError("ordinary candidate implementation/material sources required")
        name = path.relative_to(ROOT).as_posix()
        digest = sha256(path.read_bytes()).hexdigest()
        other = root/name
        if not name.startswith("engineering/halbach_scaling/") and (
                not other.is_file() or other.is_symlink() or sha256(other.read_bytes()).hexdigest() != digest):
            raise ValueError("candidate source workspaces differ: " + name)
        result[name] = digest
    return result


def recipes():
    """Thirty-six physical proposals, including the exact retained half-volume control."""
    rows = []
    for volume in (.006, .012, .018, .024):
        for width in (.32, .40, .44):
            for segments in (8, 16):
                rows.append(dict(magnet_volume_m3=volume, width_m=width,
                                 segments=segments, periods=1, yoke_m=0., winding_layout="uniform"))
    for volume in (.012, .018, .024):
        for segments, periods, yoke, winding in ((8, 2, 0., "uniform"), (8, 1, .012, "uniform"),
                                                 (8, 1, 0., "differential")):
            rows.append(dict(magnet_volume_m3=volume, width_m=.40,
                             segments=segments, periods=periods, yoke_m=yoke, winding_layout=winding))
    for volume in (.012, .024):
        rows.append(dict(magnet_volume_m3=volume, width_m=.40, segments=16,
                         periods=2, yoke_m=0., winding_layout="uniform"))
    rows.append(dict(magnet_volume_m3=.012, width_m=.40, segments=4,
                     periods=1, yoke_m=0., winding_layout="uniform"))
    assert len(rows) == 36
    for row in rows:
        row["id"] = (f"HS-V{round(row['magnet_volume_m3']*1000):03d}"
                     f"-W{round(row['width_m']*100):02d}-H{row['segments']}"
                     f"-P{row['periods']}-Y{round(row['yoke_m']*1000):02d}"
                     f"-{'D' if row['winding_layout']=='differential' else 'U'}")
    return rows


def rotating_directions(segments, periods=1, phase_rad=0.):
    """Cell-centred complete rotations; the stronger free-air side is upward."""
    if type(segments) is not int or segments not in (4, 8, 16) or periods not in (1, 2):
        raise ValueError("four/eight/sixteen segments and one/two complete periods required")
    if not math.isfinite(phase_rad):
        raise ValueError("finite magnetization phase required")
    return [[-math.sin(-math.pi*periods + 2*math.pi*(j+.5)/segments+phase_rad),
             math.cos(-math.pi*periods + 2*math.pi*(j+.5)/segments+phase_rad)]
            for j in range(segments*periods)]


def free_air_seed_T(*, br_T, thickness_m, width_m, gap_m, segments, periods):
    """Infinite periodic, unit-recoil free-air fundamental; no steel-force bound."""
    if any(type(v) not in (int, float) or not math.isfinite(v) or v <= 0
           for v in (br_T, thickness_m, width_m)) or not math.isfinite(gap_m) or gap_m < 0:
        raise ValueError("finite positive dimensions/remanence and nonnegative gap required")
    rotating_directions(segments, periods)
    k = 2*math.pi*periods/width_m
    factor = math.sin(math.pi/segments)/(math.pi/segments)
    return br_T*(-math.expm1(-k*thickness_m))*math.exp(-k*gap_m)*factor


def _build(recipe):
    custom = {k: v for k, v in recipe.items() if k not in {"id", "winding_layout"}}
    parent = magnets._build(("N35-H8-half-no-yoke", "planar-halbach", "Arnold-N35UH",
                            dict(segments=8, magnet_volume_m3=.006)))
    if parent["physical_id"] != PARENT_ID:
        raise ValueError("retained parent physical definition changed")
    baseline = custom == dict(magnet_volume_m3=.006, width_m=.32, segments=8, periods=1, yoke_m=0.)
    if baseline:
        value = deepcopy(parent)
        value["sample_id"] = recipe["id"]
    else:
        params = dict(custom, backing_m=.006, turns=60, winding_layout=recipe["winding_layout"],
                      conductor_side_m=.002, conductor_insulation_m=.0004,
                      central_slot_m=.05 if recipe["winding_layout"]=="differential" else 0.,
                      phase_rad=math.pi/2 if recipe["winding_layout"]=="differential" else 0.)
        thickness = params["magnet_volume_m3"]/(params["width_m"]-params["central_slot_m"])
        params["pm_thickness_m"] = thickness
        gap = .012
        bottom = -gap-thickness
        mats = magnets.passive.material_table()
        regions = [magnets.passive._region("guideway/facing", "steel", "guideway", [-.25,.25,0.,.035])]
        parts = [magnets._box("guideway/facing", [1.,.5,.035], [-.5,-.25,0.],
                              "steel", mats["steel"]["density_kg_m3"], "guideway", "passive-facing")]
        directions = rotating_directions(params["segments"], params["periods"], params["phase_rad"])
        cell_width = (params["width_m"]-params["central_slot_m"])/len(directions)
        for j, direction in enumerate(directions):
            y = -params["width_m"]/2+j*cell_width+(params["central_slot_m"] if j>=len(directions)//2 else 0.)
            uid = f"train/pm-{j:02d}"
            regions.append(dict(id=uid, material="ferrite", group="train",
                                bounds_yz_m=[y, y+cell_width, bottom, -gap],
                                Br_y_T=direction[0], Br_z_T=direction[1], J_x_A_m2=0.))
            for k in range(20):
                parts.append(magnets._box(uid+f"/block-{k}", [.05, cell_width, thickness],
                    [-.5+k*.05, y, bottom], "ferrite", 5000., "train",
                    "rotating-permanent-magnet", block_joints="Nominal touching 50 mm blocks; coating/retention/end effects unresolved"))
        if params["yoke_m"]:
            uid="train/back-yoke"
            regions.append(magnets.passive._region(uid,"steel","train",[-params["width_m"]/2,params["width_m"]/2,bottom-params["yoke_m"],bottom]))
            parts.append(magnets._box(uid,[1.,params["width_m"],params["yoke_m"]],[-.5,-params["width_m"]/2,bottom-params["yoke_m"]],"steel",mats["steel"]["density_kg_m3"],"train","back-yoke"))
        backing_bottom=bottom-params["yoke_m"]-params["backing_m"]
        regions.append(magnets.passive._region("train/backing","aluminium","train",[-params["width_m"]/2-.02,params["width_m"]/2+.02,backing_bottom,backing_bottom+params["backing_m"]]))
        parts.append(magnets._box("train/backing",[1.,params["width_m"]+.04,params["backing_m"]],[-.5,-params["width_m"]/2-.02,backing_bottom],"aluminium",2700.,"train","nonmagnetic-stock-backing"))
        winding_params=dict(magnets.passive.DEFAULTS,length_x_m=1.,conductor_insulation_m=.0004)
        winding_specs=[("array-control",0.,params["width_m"],1)]
        if params["winding_layout"]=="differential":
            half=(params["width_m"]-params["central_slot_m"])/2
            centre=(params["width_m"]+params["central_slot_m"])/4
            winding_specs=[("array-left-control",-centre,half,-1),("array-right-control",centre,half,1)]
        circuits=[]
        for uid,centre,width,polarity in winding_specs:
            rr,pp,coil=magnets.passive._winding(uid,centre,width,bottom,thickness,params["turns"],winding_params,mats["copper"]["density_kg_m3"],polarity=polarity)
            regions.extend(rr);parts.extend(pp);circuits.append(coil)
        value = magnets._finish(recipe["id"], "planar-halbach", "Arnold-N35UH", params,
                                regions, parts, circuits, deepcopy(parent["packing"]),
                                deepcopy(parent["unknown_installed_inventory"]))
    value.pop("bundle_sha256")
    value["candidate_id"] = value["physical_id"]
    value["search_schema"] = SCHEMA
    value["recipe_id"] = recipe["id"]
    value["material_model_id"] = identity(value["materials"])
    value["lineage"] = dict(parent_magnet_id=PARENT_ID,
        purpose="Larger magnetic stock and matched layout alternatives; no inherited force result",
        parent_force_transferable=False)
    value["interface"] = dict(facing_width_m=.50, facing_thickness_m=.035,
        module_length_m=1., reference_gap_m=.012, modules_per_car=24,
        train_cars=6, car_length_m=17., aw3_payload_kg_per_car=12000.,
        ordinary_guideway="Concrete with passive steel facings; no guideway PM or powered suspension",
        complete_carrier_and_concrete_attachment_fit=None,
        bank_placement_scope="Inherited local bank centres; not a qualified complete car/concrete-beam installation")
    grade = value["materials"][value["grade_id"]]
    value["free_air_seed_80C_T"] = None if recipe["winding_layout"]=="differential" else free_air_seed_T(
        br_T=grade["br_20c_t"]*(1+60*grade["br_temperature_coefficient_per_k"]),
        thickness_m=value["parameters"]["pm_thickness_m"], width_m=recipe["width_m"],
        gap_m=.012, segments=recipe["segments"], periods=recipe["periods"])
    value["seed_scope"] = "Infinite periodic free-air fundamental only; neither actual steel-facing field nor a force bound"
    value["winding_definition"] = dict(
        layout=recipe["winding_layout"],
        copper_fill_by_circuit={c["id"]:c["turns"]*c["conductor_area_m2"]/(c["window_pack_width_m"]*c["window_height_m"]) for c in value["circuits"]},
        maximum_continuous_current_density_A_per_mm2=3.75,
        maximum_authority_trial_current_A=15.,
        common_current_connection={c["id"]:1 for c in value["circuits"]},
        baseline_control=baseline,
        insulation_mass_kg=None,thermal_equilibrium_C=None,
        scope="Opposite winding polarities are encoded in the differential windows; the common signed current never changes physical geometry")
    value.update(FLAGS)
    value["bundle_sha256"] = identity(value)
    return value


def candidates(root=ROOT):
    source_snapshot(root)
    values = [_build(recipe) for recipe in recipes()]
    if len({v["physical_id"] for v in values}) != 36:
        raise ValueError("physical proposal identities must be distinct")
    return values


def validate(value, root=ROOT):
    source_snapshot(root)
    recipe = next((r for r in recipes() if r["id"] == value.get("recipe_id")), None)
    if recipe is None or value != _build(recipe):
        raise ValueError("unsupported or modified Halbach stock/material/interface bundle")
    return value


def field_geometry(value, root=ROOT):
    """Explicit NdFeB recoil adapter for the existing generic PM PDE branch."""
    validate(value, root)
    grade = deepcopy(value["materials"][value["grade_id"]])
    materials = deepcopy(value["materials"])
    grade.update(kind="ferrite", relative_permeability=grade["recoil_relative_permeability"])
    materials[value["grade_id"]] = grade
    materials["ferrite"] = deepcopy(grade)
    result = {k: deepcopy(value[k]) for k in
              ("length_x_m", "reference_gap_m", "origin_yz_m", "regions", "circuits")}
    result["materials"] = materials
    result["recoil_adapter"] = dict(active_material_id=value["grade_id"],
        active_chemistry=grade["chemistry"], computational_kind="linear-recoil-permanent-magnet",
        frozen_solver_branch="ferrite", alias_creates_stock=False)
    return result
