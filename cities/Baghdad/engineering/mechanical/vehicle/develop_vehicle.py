"""Build the Baghdad steel frame cut schedule and research screens."""
import argparse
import csv
from hashlib import sha256
from io import StringIO
import json
from math import hypot
import os
from pathlib import Path
import sys
import tomllib

# Bounded small matrix operations for the inherited frame evaluator.
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

HERE = Path(__file__).resolve().parent
CITY = HERE.parents[2]
ROOT = CITY.parents[1]
sys.path.insert(0, str(ROOT))
from engineering.design_search import frame_analysis as frame
import stock_mesh


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode()).hexdigest()


def section(stock, key):
    h, b, t = stock["sections"][key]
    return {"width_m": b/1000, "height_m": h/1000, "wall_m": t/1000}


def design():
    stock = tomllib.loads((HERE / "stock.toml").read_text())
    rig = tomllib.loads((HERE.parent / "quotation.toml").read_text())["rig"]
    controls = tomllib.loads((CITY / "system.toml").read_text())
    result = json.loads((CITY / "system-results.json").read_text())
    schedule = json.loads((HERE.parent / "schedule.json").read_text())
    selected = result["networks"]["first"]
    train = selected["power_cases"]["protected_conductor"]
    if (schedule["parent_selected_candidate_id"] != train["physical_candidate_id"]
            or selected["selected_candidate_id"] != train["physical_candidate_id"]
            or selected["selected_evaluation_id"] != schedule["parent_evaluation_id"]
            or result["source_sha256"]["cities/Baghdad/system.toml"]
            != sha256((CITY / "system.toml").read_bytes()).hexdigest()
            or schedule["sources_sha256"]["quotation.toml"]
            != sha256((HERE.parent / "quotation.toml").read_bytes()).hexdigest()):
        raise ValueError("Regenerate the parent mechanical study for the selected Baghdad candidate")
    geom = controls["vehicle_geometry"]
    body = stock["body"]
    s = lambda name: section(stock, name)
    jamb_half = s("jamb")["height_m"]/2
    half_length = geom["car_body_length_m"]/2
    jambs = sorted(round(x + sign*(geom["door_clear_width_m"]/2 + jamb_half), 6)
                   for x in geom["door_centres_m"] for sign in (-1, 1))
    ends = [-half_length+s("end_post")["height_m"]/2, half_length-s("end_post")["height_m"]/2]
    frame_inner_width = 2*rig["primary_seat_lateral_m"] - s("bogie_side")["width_m"]
    if frame_inner_width <= 0 or 2*rig["primary_seat_lateral_m"]+max(
            s("bogie_side")["width_m"], stock["seat_plates"]["primary_underside"][1]/1000) > rig["frame_width_m"]+1e-9:
        raise ValueError("Bogie stock and parent width disagree")
    if 2*body["side_axis_y_m"]+s("sill")["width_m"] > geom["body_width_m"]:
        raise ValueError("Sills outside carbody envelope")
    density = stock["material_assumptions"]["density_kg_m3"]
    bom = []

    def piece(assembly, key, count, length):
        spec = s(key)
        area = frame.section_properties(spec)["area_m2"]
        h,b,t = stock["sections"][key]
        bom.append([assembly, key, f"RHS {h}x{b}x{t}", count, round(length, 6),
                    round(area*density, 4), round(area*density*length*count, 4)])

    for name in ("sill", "cantrail"):
        splice = body[name+"_splice_x_m"]
        for cut in (half_length + splice, half_length - splice):
            piece("body", name, 2, cut)
    clear_h = body["cantrail_axis_z_m"]-s("cantrail")["height_m"]/2 - (
        body["sill_axis_z_m"]+s("sill")["height_m"]/2)
    piece("body", "jamb", 2*len(jambs), clear_h)
    piece("body", "end_post", 4, clear_h)
    for name, count, longitudinal in (("floor_tie", len(jambs), "sill"),
                                     ("roof_tie", len(jambs)+2, "cantrail"),
                                     ("bolster", len(geom["bogie_centres_m"]), "sill"),
                                     ("end_tie", 2, "sill")):
        piece("body", name, count, 2*body["side_axis_y_m"]-s(longitudinal)["width_m"])
    piece("bogie", "bogie_side", 2, rig["frame_length_m"])
    piece("bogie", "transom", 2, frame_inner_width)
    tx = stock["bogie"]["transom_axis_x_m"]
    piece("bogie", "saddle", 2, 2*tx-s("transom")["width_m"])
    for key, assembly, count in (("primary_underside", "bogie", 4),
                                 ("secondary_top", "bogie", 2), ("secondary_body", "body", 4)):
        l,b,t = stock["seat_plates"][key]
        unit = b*t*1e-6*density
        bom.append([assembly, key, f"plate {b}x{t}", count, l/1000, round(unit,4),
                    round(unit*l/1000*count, 4)])
    for _,_,length in bracing(stock,jambs,ends):
        piece("body_bracing_addition", "brace", 2, length)
    detail = stock["braced_revision"]
    leg, thickness = detail["gusset_leg_m"], detail["gusset_thickness_m"]
    # Two triangular plate blanks per brace end, each cut from half a square.
    gussets = 2*2*2*len(list(bracing(stock,jambs,ends)))
    bom.append(["body_bracing_addition","gusset",f"right triangle {leg*1000:g} x {leg*1000:g} x {thickness*1000:g}",
                gussets, leg, "", round(gussets*leg**2*thickness*density/2,4)])
    return stock, rig, controls, selected, schedule, train, jambs, ends, bom


def bracing(stock, jambs, ends):
    """One square-ended tube inside each solid panel; alternate climb direction."""
    edges = sorted(ends+jambs)
    z = stock["body"]["cantrail_axis_z_m"] - stock["body"]["sill_axis_z_m"]
    extra = stock["braced_revision"]["brace_end_clearance_m"]
    brace_height = section(stock, "brace")["height_m"]
    for i in range(0, len(edges), 2):
        start, end = edges[i:i+2]
        if i % 4:
            start,end = end,start
        dx = abs(end-start)
        length = hypot(dx,z)
        c,s = dx/length, z/length
        # Set back the square-cut end until both corners clear the post
        # and chord faces. Longitudinal coordinate along the tube axis.
        post_depth = section(stock, "jamb")["height_m"]
        post_trim = (post_depth/2+brace_height*s/2+extra)/c
        def trim(chord):
            return max(post_trim, (section(stock,chord)["height_m"]/2+brace_height*c/2+extra)/s)
        cut = length-trim("sill")-trim("cantrail")
        if cut <= 0:
            raise ValueError("Brace trims overlap")
        yield start, end, cut


def floor_tributaries(geom, jambs, ends):
    stations = sorted(jambs+ends+geom["bogie_centres_m"])
    result = {}
    for i,x in enumerate(stations):
        left = (stations[i-1]+x)/2 if i else -geom["car_body_length_m"]/2
        right = (stations[i+1]+x)/2 if i+1<len(stations) else geom["car_body_length_m"]/2
        result[x] = right-left
    return result


def body_model(stock, geom, jambs, ends, weight, braced):
    """One sidewall with planar pin/roller restraints at bolster axes."""
    size = lambda name: section(stock, name)
    b = stock["body"]
    posts = sorted(ends+jambs)
    primary_nodes = sorted(set(posts + geom["bogie_centres_m"]))
    # Split longer chord panels to sample interior curvature under tributary loading.
    xx = sorted(set(primary_nodes + [(a+b)/2 for a,b in zip(primary_nodes, primary_nodes[1:])]))
    material = stock["material_assumptions"]
    model = dict(schema=frame.SCHEMA, joint_hypothesis=frame.JOINT, nodes=[], members=[],
                 loads=[], supports=[], materials={"steel": {
                     "E_Pa": material["elastic_modulus_pa"], "nu": material["poisson_ratio"],
                     "density_kg_m3": material["density_kg_m3"], "law": frame.LAW,
                     "source_basis": "quotation-grade elastic hypothesis"}})
    tributaries = floor_tributaries(geom,jambs,ends)
    for i,x in enumerate(xx):
        for chord in ("sill", "cantrail"):
            nid = f"{chord}-{i}"
            z = b[chord+"_axis_z_m"]
            model["nodes"].append({"id": nid, "at_m": [x,b["side_axis_y_m"],z]})
            fixed = [2,4,6]  # x-z symmetry plane model
            if chord == "sill" and x in geom["bogie_centres_m"]:
                fixed += [3]
                if x == min(geom["bogie_centres_m"]):
                    fixed += [1]
            model["supports"].append({"node_id": nid, "dofs": fixed})
            if i:
                model["members"].append({"id": nid, "material_id": "steel", "section": size(chord),
                    "start_node": f"{chord}-{i-1}", "end_node": nid, "local_y": [0,1,0]})
        if x in posts:
            key = "end_post" if x in ends else "jamb"
            model["members"].append({"id": f"{key}-{i}", "material_id": "steel", "section": size(key),
                "start_node": f"sill-{i}", "end_node": f"cantrail-{i}", "local_y":[0,1,0]})
        if x in tributaries:
            model["loads"].append({"node_id": f"sill-{i}",
                "force_N":[0,0,-0.5*weight*tributaries[x]/geom["car_body_length_m"]], "moment_Nm":[0,0,0]})
    if braced:
        for i,(a,b,_) in enumerate(bracing(stock,jambs,ends)):
            model["members"].append({"id":f"brace-{i}", "material_id":"steel","section":size("brace"),
                "start_node":f"sill-{xx.index(a)}","end_node":f"cantrail-{xx.index(b)}","local_y":[0,1,0]})
    return model, xx


def body_screen(stock, geom, jambs, ends, weight, braced):
    model, xx = body_model(stock, geom, jambs, ends, weight, braced)
    result = frame.evaluate(model)
    if not result["displacements_m"]:
        raise ValueError(result["state"])
    stresses = {}
    for member in model["members"]:
        key = member["id"]
        force = result["member_end_forces_local"][key]
        prop = result["member_properties"][key]
        height = member["section"]["height_m"]
        max_stress = max(abs(force[end])/prop["area_m2"] + abs(force[end+4])*height/2/prop["I_y_m4"]
                         for end in (0,6))
        stresses[key] = max_stress/1e6
    critical = max(stresses, key=stresses.get)
    supports = {f"x_{x:+.2f}": round(result["reactions_N"][f"sill-{xx.index(x)}"][2]/1000, 4)
                for x in geom["bogie_centres_m"]}
    frames = {}
    for pos in geom["door_centres_m"]:
        indices = [xx.index(x) for x in sorted(jambs,key=lambda x:abs(x-pos))[:2]]
        # Mean top translation relative to bottom chord; door racking under this particular load.
        disps = result["displacements_m"]
        frames[str(pos)] = round(sum(disps[f"cantrail-{i}"][0]-disps[f"sill-{i}"][0]
                                       for i in indices)*500, 4)
    brace_compression = []
    for member in model["members"]:
        if member["id"].startswith("brace-"):
            name = member["id"]
            prop = result["member_properties"][name]
            # Start-node local force positive in compression.
            compression = max(0,result["member_end_forces_local"][name][0])
            pin_euler = (3.141592653589793**2*stock["material_assumptions"]["elastic_modulus_pa"]
                         *min(prop["I_y_m4"],prop["I_z_m4"])/prop["length_m"]**2)
            brace_compression.append((compression/pin_euler, name, compression, pin_euler))
    buckling = None
    if brace_compression:
        ratio,member,compression,pin_euler = max(brace_compression)
        buckling = {"member":member,"compression_kn":round(compression/1000,3),
                    "ideal_pinned_euler_kn":round(pin_euler/1000,3),"ratio":round(ratio,4)}
    return {"brace_ideal_column_diagnostic":buckling, "peak_nodal_vertical_mm": round(max(abs(v[2]) for v in result["displacements_m"].values())*1000, 4),
            "max_end_axial_plus_bending_mpa": round(stresses[critical], 3), "governing_member": critical,
            "nominal_yield_exceeded": stresses[critical] > stock["material_assumptions"]["nominal_yield_mpa"],
            "sidewall_bolster_reactions_kn": supports, "mean_door_header_relative_x_mm": frames,
            "load_residual_n": round(max(abs(v) for v in result["force_equilibrium_residual_N"]), 6),
            "joint_model": frame.JOINT, "model_id": result["model_id"]}


def member_screen(stock, key, moment, displacement, axis_description):
    sec = section(stock, key)
    prop = frame.section_properties(sec)
    stress = abs(moment)*sec["height_m"]/2 / prop["I_y_m4"]/1e6
    return {"load_case": axis_description, "maximum_moment_knm": round(moment/1000, 3),
            "nominal_bending_stress_mpa": round(stress, 3),
            "nominal_yield_exceeded": stress > stock["material_assumptions"]["nominal_yield_mpa"],
            "elastic_displacement_mm": round(displacement*1000, 4) if displacement is not None else None}


def local_screens(stock, rig, side_y, seat_load, longest_joist_strip_fraction):
    e = stock["material_assumptions"]["elastic_modulus_pa"]
    def ei(key):
        return e*frame.section_properties(section(stock, key))["I_y_m4"]
    x = stock["bogie"]["transom_axis_x_m"]
    # Each side rail receives two equal transom reactions P/2 at a from its primary seats.
    l = rig["wheelbase_m"]
    a = l/2-x
    d = seat_load*a*(3*l*l-4*a*a)/(48*ei("bogie_side"))
    sides = member_screen(stock,"bogie_side",seat_load*a/2,d,"two equal transom reactions between primary seats")
    # A transom carries P/2 from each saddle. Bearing-line spacing 2*y_primary.
    lt = 2*rig["primary_seat_lateral_m"]
    inset = rig["primary_seat_lateral_m"]-rig["secondary_seat_lateral_m"]
    dt = seat_load*inset*(3*lt*lt-4*inset*inset)/(48*ei("transom"))
    transom = member_screen(stock,"transom",seat_load*inset/2,dt,"two saddle reactions on one transom")
    saddle = member_screen(stock,"saddle",seat_load*2*x/4,seat_load*(2*x)**3/(48*ei("saddle")),
                           "central point load between two transom axes")
    # Two equal sidewall end loads P; two interior spring reactions P.
    overhang = side_y-rig["secondary_seat_lateral_m"]
    bolster = member_screen(stock,"bolster",seat_load*overhang,None,"end-loaded overhangs to secondary seats")
    floor_total = 4*seat_load*longest_joist_strip_fraction
    floor_span = 2*side_y
    floor_tie = member_screen(stock,"floor_tie",floor_total*floor_span/8,
                              5*floor_total*floor_span**3/(384*ei("floor_tie")),
                              "largest ordinary floor-joist tributary strip, uniform line load")
    trial = member_screen(stock,"floor_tie_trial",floor_total*floor_span/8,
                          5*floor_total*floor_span**3/(384*ei("floor_tie_trial")),
                          "superseded isolated 100x60x5 joist, same floor strip")
    return {"superseded_floor_tie_trial":trial,"floor_tie":floor_tie,"bogie_side":sides,"transom":transom,"saddle":saddle,"body_bolster":bolster}


def build():
    stock, rig, cfg, selected, schedule, train, jambs, ends, bom = design()
    mass = {name: round(sum(r[-1] for r in bom if r[0]==name),3) for name in ("body","bogie","body_bracing_addition")}
    parts = stock_mesh.assembly(stock,rig,cfg["vehicle_geometry"],jambs,ends,list(bracing(stock,jambs,ends)))
    mesh, volume = stock_mesh.serialize(parts)
    parent_mesh, _ = stock_mesh.serialize([x for x in parts if x[0] not in ("brace","gusset")])
    physical_stock = {k:v for k,v in stock.items() if k not in ("name","material_assumptions","evaluation","braced_revision")}
    physical_stock["sections"] = {k:v for k,v in physical_stock["sections"].items() if k not in ("brace","floor_tie_trial")}
    unbraced = digest({"parent":schedule["study_physical_id"], "stock":physical_stock,
                       "mesh_sha256":sha256(parent_mesh.encode()).hexdigest(),
                       "cuts":[r[:5] for r in bom if r[0]!="body_bracing_addition"]})
    physical = digest({"parent":unbraced, "brace_section":stock["sections"]["brace"],
                       "bracing":stock["braced_revision"], "braces":list(bracing(stock,jambs,ends)),
                       "mesh_sha256":sha256(mesh.encode()).hexdigest(),
                       "cuts":[r[:5] for r in bom if r[0]=="body_bracing_addition"]})
    settings = stock["evaluation"]
    weight = train["train_crowd_mass_t"]*1000/cfg["vehicle"]["cars_per_train"]*settings["gravity_m_s2"]
    cases = {}
    strips = floor_tributaries(cfg["vehicle_geometry"], jambs, ends)
    floor_fraction = max(strips[x] for x in jambs)/cfg["vehicle_geometry"]["car_body_length_m"]
    for factor in settings["vertical_factors"]:
        bodies = {label: body_screen(stock,cfg["vehicle_geometry"],jambs,ends,weight*factor,braced)
                  for label,braced in (("unbraced_parent",False),("braced_revision",True))}
        spring = weight*factor/4
        cases[str(factor)] = {"applied_car_gravity_kn":round(weight*factor/1000,3),
            "assumed_secondary_seat_load_kn":round(spring/1000,3),"sidewall_cases":bodies,
            "local_members":local_screens(stock,rig,stock["body"]["side_axis_y_m"],spring,floor_fraction)}
    mesh_mass = volume*stock["material_assumptions"]["density_kg_m3"]
    if abs(mesh_mass - (sum(mass.values())+mass["bogie"])) > 0.01:
        raise ValueError("Assembly mesh and cut stock mass differ by more than 10 g")
    source_paths = [HERE/"stock.toml",Path(__file__), Path(frame.__file__), Path(stock_mesh.__file__),
                    CITY/"system.toml",CITY/"system-results.json",HERE.parent/"schedule.json",
                    HERE.parent/"quotation.toml"]
    sources = {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in source_paths}
    output = {"study": stock["name"], "parent_project_id":schedule["parent_project_id"],
              "parent_train_id":train["physical_candidate_id"],"parent_interface_study_id":schedule["study_physical_id"],
              "unbraced_parent_id":unbraced, "braced_revision_id":physical, "evaluation_id": digest([physical,sources,settings,
                  selected["selected_evaluation_id"]]), "purpose":"first-article stock quotation",
              "source_sha256":sources,"cases":cases,"cut_stock_mass_kg":mass,
              "unbraced_body_and_two_bogie_cut_stock_kg_per_car":round(mass["body"]+2*mass["bogie"],3),
              "braced_body_and_two_bogie_cut_stock_kg_per_car":round(sum(mass.values())+mass["bogie"],3),
              "braced_mesh_component_count":len(parts), "braced_mesh_stock_mass_kg":round(mesh_mass,3),
              "complete_installed_mass_kg":None,"physical_accepted":False,"selection":None}
    csv_text = StringIO(newline="")
    writer = csv.writer(csv_text, lineterminator="\n")
    writer.writerow(["assembly","part","nominal_stock_mm","cuts_per_assembly","cut_length_m","nominal_kg_per_m","mass_kg"])
    writer.writerows(bom)
    return {"result.json":json.dumps(output,indent=2,allow_nan=False)+"\n","cut-list.csv":csv_text.getvalue(),"braced-frame.obj":mesh,"frame-overview.svg":stock_mesh.preview(parts)}


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true")
    for_check=p.parse_args().check
    for filename, content in build().items():
        dest=HERE/filename
        if for_check:
            if content != dest.read_text():
                raise SystemExit(f"Stale {filename}")
        else:
            dest.write_text(content)
