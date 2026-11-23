"""Rebuild prototype geometry and load cases using the existing vehicle and viaduct evaluators."""
import argparse
import csv
import io
import json
import math
from pathlib import Path
import sys
import tomllib

HERE = Path(__file__).resolve().parent
CITY = HERE.parents[1]
ROOT = CITY.parents[1]
MECH = CITY / "engineering/mechanical"
# These existing, standalone design scripts import their drawing helpers by local name.
# Keep their import environment in the numerical worker only.
sys.path[:0] = [str(ROOT), str(MECH / "vehicle"), str(MECH)]
from cities.Baghdad.engineering.mechanical.vehicle import develop_vehicle as vehicle
from cities.Baghdad.engineering.mechanical.civil import develop_civil
from cities.Baghdad.engineering.mechanical import develop
from cities.Baghdad.engineering.prototype import car
from cities.Baghdad import airport_integration
import numpy as np


def prism(name, lo, hi):
    vertices = np.array([[x,y,z] for z in (lo[2],hi[2]) for x,y in (
        (lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1]))])
    faces = [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    return name, vertices, faces


def rounded(row):
    return [round(float(x), 6) for x in row]


def door_equipment(spec, geom, stock):
    liners, travel = [], []
    sy = stock["body"]["side_axis_y_m"]
    for side in (-1, 1):
        for cx in geom["door_centres_m"]:
            for hand in (-1, 1):
                x = cx + hand * spec["rough_opening_m"]/2
                x2 = x - hand * spec["liner_thickness_m"]
                y = side * sy
                z = spec["liner_bottom_m"]
                half = spec["liner_width_m"]/2
                liners.append(prism("jamb_liner", [min(x,x2),y-half,z],
                                    [max(x,x2),y+half,z+spec["liner_height_m"]]))
                x2 = cx + hand*(spec["leaf_travel_m"] + spec["leaf_closed_width_m"])
                y = side*spec["leaf_plane_y_m"]
                z = spec["leaf_bottom_m"]
                half = spec["leaf_thickness_m"]/2
                travel.append(prism("leaf_sweep", [min(cx,x2),y-half,z],
                                    [max(cx,x2),y+half,z+spec["leaf_height_m"]]))
    return liners, travel


def describe(parts):
    rows = []
    bg = {"bogie_side", "primary_underside", "transom", "saddle", "secondary_top"}
    for i,(name,v,_) in enumerate(parts):
        bogie = ("bogie-A" if v[:,0].mean()<0 else "bogie-B") if name in bg else None
        rows.append(dict(id=f"{name}_{i:03d}", part=name, assembly=bogie or "body",
                         lower_m=rounded(v.min(axis=0)), upper_m=rounded(v.max(axis=0))))
    return rows


def check_travel(parts, travel):
    contacts = []
    least = math.inf
    for i,(_,leaf,_) in enumerate(travel):
        gaps = []
        for j,(name,v,_) in enumerate(parts):
            d = np.maximum(v.min(axis=0) - leaf.max(axis=0), leaf.min(axis=0)-v.max(axis=0))
            gaps.append(float(np.linalg.norm(np.maximum(0,d))))
            if max(d) <= 1e-8:
                contacts.append((i, f"{name}_{j:03d}"))
        least = min(least, *gaps)
    return {"sweeps": len(travel), "conservative_stock_box_intersections": contacts,
            "minimum_sweep_to_stock_box_gap_m": round(least,6),
            "scope": "Full continuous straight translation from closed to fully open, checked against each stock piece's enclosing box. Vendor carriages, hanging hardware, seals, interior lining, passenger reach, dynamic motion and wiring need fitted geometry."}


def bom_csv(rows):
    out = io.StringIO(newline="")
    writer = csv.writer(out,lineterminator="\n")
    writer.writerow(["assembly","part","nominal_stock_mm","cuts_per_assembly","cut_length_m","nominal_kg_per_m","gross_mass_kg"])
    writer.writerows(rows)
    return out.getvalue().encode()


def loaded_clearances(stock, geom, jambs, ends, weight, rough, spec):
    """Find the extrema of relative horizontal Hermite displacement through each lined jamb."""
    model, xx = vehicle.body_model(stock, geom, jambs, ends, weight, True)
    result = vehicle.frame.evaluate(model)
    z0 = stock["body"]["sill_axis_z_m"]
    height = stock["body"]["cantrail_axis_z_m"]-z0
    bounds = [(spec["liner_bottom_m"]-z0)/height,
              (spec["liner_bottom_m"]+spec["liner_height_m"]-z0)/height]
    if not 0 <= bounds[0] < bounds[1] <= 1:
        raise ValueError("Liner extends past modelled jamb")
    widths = []
    for left,right in zip(jambs[::2],jambs[1::2],strict=True):
        def delta(chord,key,component):
            return result[key][f"{chord}-{xx.index(right)}"][component] - result[key][f"{chord}-{xx.index(left)}"][component]
        lo,hi = [delta(chord,"displacements_m",0) for chord in ("sill","cantrail")]
        slo,shi = [height*delta(chord,"rotations_rad",1) for chord in ("sill","cantrail")]
        # u(s) = a*s^3 + b*s^2 + c*s + lo; positive rotation about y moves a vertical tangent towards +x.
        a,b,c = 2*(lo-hi)+slo+shi,3*(hi-lo)-2*slo-shi,slo
        points = list(bounds)
        for root in np.roots([3*a,2*b,c]):
            if abs(root.imag)<1e-9 and bounds[0]<root.real<bounds[1]:
                points.append(float(root.real))
        widths.append(round(1000*(rough+min(((a*t+b)*t+c)*t+lo for t in points)),4))
    return {"deformed_minimum_bare_width_mm_by_portal":widths,
            "worst_width_loss_mm":round(max(0,rough*1000-min(widths)),4),
            "combined_allocated_width_loss_mm":round(2000*spec["loaded_distortion_per_edge_m"],4),
            "scope":"Each portal's minimum first-order horizontal jamb-centreline spacing less nominal post depth, from cubic beam shape between loaded sill and header. Plane gravity only; fittings, 3D twist, fabrication and commissioning require measurements."}


def civil_meshes(settings, geom, beam, platform):
    b, p, k = settings["box"], settings["platform"], settings["pier"]
    length, width, height = beam["length_m"], b["width_m"], b["depth_m"]
    end, web, slab = b["solid_end_m"], b["web_m"], b["slab_m"]
    # Non-overlapping volumes of a single monolithic casting. Local z=0 at soffit.
    beam_parts = [
        prism("solid_end", [0,-width/2,0], [end,width/2,height]),
        prism("solid_end", [length-end,-width/2,0], [length,width/2,height]),
        prism("web", [end,-width/2,0], [length-end,-width/2+web,height]),
        prism("web", [end,width/2-web,0], [length-end,width/2,height]),
        prism("bottom_slab", [end,-width/2+web,0], [length-end,width/2-web,slab]),
        prism("top_slab", [end,-width/2+web,height-slab], [length-end,width/2-web,height])]
    panels = []
    island = geom["island_width_m"]
    pitch = island / p["panels_across"]
    for i in range(p["panels_across"]):
        y = -island/2 + (i+0.5)*pitch
        half = platform["panel_width_m"]/2
        panel = prism("panel", [0,y-half,-p["panel_thickness_m"]],
                      [platform["panel_length_m"],y+half,0])
        panel[1][:,2] -= (island/2-np.abs(panel[1][:,1]))*p["fall_to_centre_fraction"]
        panels.append(panel)
    f, c = k["footing_width_m"]/2, k["column_width_m"]/2
    fd, ch = k["footing_depth_m"], k["column_height_m"]
    pier = [
        prism("footing", [-f,-f,0], [f,f,fd]),
        prism("column", [-c,-c,fd], [c,c,fd+ch]),
        prism("cap", [-k["cap_length_m"]/2,-k["cap_width_m"]/2,fd+ch],
              [k["cap_length_m"]/2,k["cap_width_m"]/2,fd+ch+k["cap_depth_m"]])]
    gross_support = sum(beam["pier_gravity_screen"][key] for key in ("footing_volume_m3","column_volume_m3","cap_volume_m3"))
    members = {}
    data = {}
    for n,components,volume,datum in [
        ("track-span",beam_parts,beam["gross_concrete_m3"],"x from stock end; y from track centreline; z from soffit"),
        ("platform-bay",panels,p["panels_across"]*platform["panel_volume_m3"],
        "x from first panel end; y from island centre; z from platform edge top plane"),
        ("pier",pier,gross_support,"x along track; y across track; z from underside of trial footing")]:
        mesh, v = vehicle.stock_mesh.serialize(components)
        if not math.isclose(v,volume,abs_tol=1e-7):
            raise ValueError("Concrete volume differs for "+n)
        data[n+".obj"] = mesh.replace("Baghdad quotation revision B. Metres. x forward, y left, z up, rail head z=0.",
                                     f"Baghdad prototype {n} stock in metres. {datum}.",1).encode()
        members[n] = {"datum":datum,"counted_volume_m3":round(v,8),"objects":len(components)}
    return data,members


def calculate(parent):
    stock, rig, cfg, _, schedule, _, old_jambs, ends, bom = vehicle.design()
    g = cfg["vehicle_geometry"]
    s = tomllib.loads((HERE / "doorway.toml").read_text())
    rough = s["rough_opening_m"]
    half_jamb = vehicle.section(stock,"jamb")["height_m"]/2
    jambs = sorted(round(x+hand*(rough/2+half_jamb),6) for x in g["door_centres_m"] for hand in (-1,1))
    old_braces = list(vehicle.bracing(stock,old_jambs,ends))
    braces = list(vehicle.bracing(stock,jambs,ends))
    old_mesh = vehicle.stock_mesh.assembly(stock,rig,g,old_jambs,ends,old_braces)
    parent_obj, old_volume = vehicle.stock_mesh.serialize(old_mesh)
    if parent_obj.encode() != (MECH / "vehicle/braced-frame.obj").read_bytes():
        raise ValueError("Reproduced parent mesh differs")
    parts = vehicle.stock_mesh.assembly(stock,rig,g,jambs,ends,braces)
    liners, travel = door_equipment(s,g,stock)
    parts.extend(liners)
    mesh, vol = vehicle.stock_mesh.serialize(parts)
    density = stock["material_assumptions"]["density_kg_m3"]
    brace_area = vehicle.frame.section_properties(vehicle.section(stock,"brace"))["area_m2"]
    brace_rows = [r for r in bom if r[1]=="brace"]
    if len(brace_rows)!=len(braces):
        raise ValueError("Brace cuts and solid wall panels disagree")
    for row,(_,_,length) in zip(brace_rows,braces,strict=True):
        row[4] = round(length,6)
        row[6] = round(row[3]*length*brace_area*density,4)
    unit = s["liner_thickness_m"]*s["liner_width_m"]*density
    bom.append(["body_door_addition","jamb_liner",f'flat {s["liner_width_m"]*1000:g}x{s["liner_thickness_m"]*1000:g}',
                len(liners),s["liner_height_m"],unit,round(unit*s["liner_height_m"]*len(liners),4)])
    gross = sum(r[-1]*(2 if r[0]=="bogie" else 1) for r in bom)
    if abs(gross-vol*density)>0.01 or len(parts)!=sum(r[3]*(2 if r[0]=="bogie" else 1) for r in bom):
        raise ValueError("Mesh/BOM gross stock reconciliation failed")
    obj = mesh.replace("quotation revision B", "first-article lined jamb revision",1).encode()
    artifacts = {"car-and-bogies.obj":obj,"revised-cuts.csv":bom_csv(bom)}
    swept_mesh,_ = vehicle.stock_mesh.serialize(travel)
    artifacts["door-leaf-travel.obj"] = swept_mesh.replace("quotation revision B","sliding leaf space reservations",1).encode()
    positions = describe(parts)
    rough_from_mesh = []
    for face in (-1,1):
        js = sorted((p["lower_m"][0],p["upper_m"][0]) for p in positions
                    if p["part"]=="jamb" and p["lower_m"][1]*face>0)
        rough_from_mesh.extend(round(b[0]-a[1],6) for a,b in zip(js[::2],js[1::2],strict=True))
    if len(rough_from_mesh)!=8 or any(not math.isclose(m,rough) for m in rough_from_mesh):
        raise ValueError("Jamb faces disagree with the drawing")
    allowances = {k:s[k] for k in ("liner_thickness_m","seal_projection_per_edge_m","fabrication_inward_per_edge_m",
                                   "loaded_distortion_per_edge_m","fitting_and_wear_per_edge_m")}
    minimum = min(rough_from_mesh)-2*sum(allowances.values())
    clear = g["door_clear_width_m"]
    sweep = check_travel(parts, travel)
    if min(minimum, 2*s["leaf_travel_m"]) < clear or sweep["conservative_stock_box_intersections"]:
        raise ValueError("Revised portal or proposed door travel fails the dimensional screen")
    mass = {"parent_cut_kg_per_car": round(old_volume*density,4), "cut_kg_per_car":round(vol*density,4),
            "counted_delta_kg_per_car":round((vol-old_volume)*density,4), "liner_blank_kg_per_car":bom[-1][-1],
            "mesh_minus_cut_kg_per_car":round(vol*density-gross,6),"complete_installed_tare_kg":None,
            "basis":"Gross square-corner cut stock and undrilled liners. Unknown joints, removed stock, moving equipment, finishes and workshop waste have no measured mass."}
    p_case = parent["opening"]
    cars = p_case["bundle"]["formation_cars"]
    mass_t = p_case["power"]["vehicle"]["mass_t"] + mass["counted_delta_kg_per_car"]*cars/1000
    weight = mass_t*1000/cars*stock["evaluation"]["gravity_m_s2"]
    bodies = {}
    for factor in stock["evaluation"]["vertical_factors"]:
        bodies[str(factor)] = vehicle.body_screen(stock,g,jambs,ends,weight*factor,True)
        bodies[str(factor)]["door_width"] = loaded_clearances(stock,g,jambs,ends,weight*factor,rough,s)
    axial = mass_t*9.80665/p_case["power"]["vehicle"]["driven_axles"]
    track = schedule["viaduct"].copy()
    axles = [cx+a for cx in schedule["train"]["car_centres_m"] for a in schedule["train"]["body_axle_x_m"]]
    quote = tomllib.loads((MECH/"quotation.toml").read_text())
    track["moving_gravity_only"] = develop.moving_load(axles,track["effective_span_m_hypothesis"],
        quote["screen"]["load_step_m"],axial,track["moving_gravity_only"]["stock_overhang_per_end_m"])
    concrete = tomllib.loads((MECH/"civil/concept.toml").read_text())
    beam = develop_civil.box_screen(concrete["box"],concrete["materials"],track,concrete["pier"])
    civil_parent = json.loads((MECH/"civil/section-results.json").read_bytes())
    civil_files, civil_mesh = civil_meshes(concrete,cfg["station_geometry"],beam,civil_parent["platform"])
    artifacts.update(civil_files)
    geometry = {k:v for k,v in s.items() if k not in {"name", "fabrication_inward_per_edge_m",
                "loaded_distortion_per_edge_m","fitting_and_wear_per_edge_m"}}
    frame_id = car.identity({"parent_frame_revision":parent["assembly"]["frame_revision"],"geometry":geometry,
                             "mesh_sha256":car.sha(obj),"cuts_sha256":car.sha(artifacts["revised-cuts.csv"])})
    result = {"frame_revision":frame_id, "parent_frame_revision":parent["assembly"]["frame_revision"],
              "parent_candidate_id":p_case["candidate_id"], "parent_evaluation_id":p_case["evaluation_id"],
              "parent_service_evaluation_id":parent["service"]["evaluation_id"],
              "pieces":positions,"doorway":{"required_fitted_m":clear,"rough_widths_m":rough_from_mesh,
              "per_edge_allowances_m":allowances,"minimum_fitted_under_allocations_m":round(minimum,6),
              "residual_m":round(minimum-clear,6), "parent_rough_width_m":clear,
              "rough_jamb_axes_x_m":jambs,"specification":s,"leaf_sweep":sweep},
              "mass":mass,"planning_crowd_train_t":mass_t,"equal_static_axle_kn":axial,
              "body_vertical_screens":bodies,"civil":{"track":beam,"meshes":civil_mesh,"moving_load":track["moving_gravity_only"],
              "station_bay":civil_parent["platform"],"parent_physical_id":civil_parent["physical_id"],
              "foundation_delta_kpa": beam["pier_gravity_screen"]["uniform_soil_contact_pressure_kpa"]-
              civil_parent["track"]["pier_gravity_screen"]["uniform_soil_contact_pressure_kpa"]},
              "bogie_translations_m":g["bogie_centres_m"],"frame_axis":"Railhead z=0. x forward, y left, z up. OBJ coordinates are in metres in a single car frame.",
              "interfaces":car.interfaces(g,rig,s,positions,schedule), "proposed_service_inventory":car.service_inventory(len(liners),s),
              "fabrication_released":False,"physical_accepted":False}
    artifacts["portal-detail.svg"] = car.portal_drawing(result).encode()
    result["source_sha256"] = car.source_hashes()
    result["artifact_sha256"] = {n:car.sha(raw) for n,raw in artifacts.items()}
    result["evaluation_id"] = car.identity(result)
    artifacts["article.json"] = car.encode(result)
    return artifacts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write",action="store_true")
    args = parser.parse_args()
    items = calculate(airport_integration.build())
    if args.write:
        car.write_compact(items)
    else:
        stored = car.read_compact()
        for name,data in items.items():
            if stored.get(name) != data:
                raise ValueError(f"Stale prototype artifact {name}")
    print(json.loads(items["article.json"])["evaluation_id"])


if __name__ == "__main__":
    main()
