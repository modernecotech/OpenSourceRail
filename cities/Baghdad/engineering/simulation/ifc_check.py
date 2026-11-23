"""Reconcile the four Airport IFC stock assemblies with the released article and trial jig."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape
import ifcopenshell.util.unit
import ifcopenshell.validate
import numpy as np

from cities.Baghdad.engineering.prototype.verify_twin import ModelPage
from cities.Baghdad.engineering.simulation.vehicle_civil import evaluate as evaluate_vehicle

HERE = Path(__file__).resolve().parent
PACKET = HERE.parent/"prototype/airport-prototype.zip"


def stock_model(archive, manifest, name, article, entries):
    raw = archive.read(name+".ifc")
    if sha256(raw).hexdigest() != manifest["sha256"][name+".ifc"]:
        raise ValueError("IFC member changed")
    model = ifcopenshell.file.from_string(raw.decode())
    logger = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(model, logger)
    if logger.statements:
        raise ValueError(f"Invalid IFC {name}: {logger.statements[0]}")
    scale = ifcopenshell.util.unit.calculate_unit_scale(model)
    roots = [a for a in model.by_type("IfcElementAssembly") if a.ContainedInStructure]
    if len(roots)!=1 or roots[0].Description!="Airport opening "+article["candidate_id"] or scale != 1.0:
        raise ValueError("Expected the Airport candidate in metre-based project coordinates")
    expected = {e["id"]:e for e in entries}
    products = model.by_type("IfcBuildingElementProxy")
    if len(products)!=len(expected) or {p.Tag for p in products}!=set(expected):
        raise ValueError("Piece register differs")
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords",True)
    counts, bounds, volume, error = Counter(), {}, 0., 0.
    for product in products:
        shape = ifcopenshell.geom.create_shape(settings,product)
        points = np.array(shape.geometry.verts).reshape(-1,3)
        lo, hi = points.min(axis=0), points.max(axis=0)
        entry = expected[product.Tag]
        error = max(error, float(np.max(abs(lo-entry["lower_m"]))), float(np.max(abs(hi-entry["upper_m"]))))
        if len(product.Decomposes)!=1 or product.Decomposes[0].RelatingObject.Name != entry["assembly"]:
            raise ValueError("Incorrect assembly placement")
        counts[entry["assembly"]]+=1
        bounds[product.Tag]=(lo,hi)
        volume += abs(ifcopenshell.util.shape.get_volume(shape.geometry))
    target = (article["mass"]["cut_kg_per_car"]/7850 if name=="car-and-bogies" else
              article["civil"]["meshes"][name]["counted_volume_m3"])
    if error>2e-6 or abs(volume-target)>2e-6:
        raise ValueError(f"Member {name} exceeds stock geometry tolerance: {error}, {volume-target}")
    return dict(file_sha256=sha256(raw).hexdigest(),schema=model.schema,unit_to_metre=scale,
                roots=len(roots),proxy_count=len(products),per_assembly_count=dict(counts),
                world_bbox_max_abs_residual_m=error,native_stock_m3=volume,
                reference_stock_m3=target,native_minus_reference_m3=volume-target),bounds


def exchange(article,bounds):
    """Continuous straight swept AABB of the stock and pallet against four trial stand feet."""
    trials=[]
    for bogie in article["interfaces"]["bogies"]:
        name=bogie["assembly"]
        pieces = [p for p in article["pieces"] if p["assembly"]==name]
        lo=np.min([bounds[p["id"]][0] for p in pieces],axis=0)
        hi=np.max([bounds[p["id"]][1] for p in pieces],axis=0)
        shift=bogie["signed_outward_travel_m"]
        x_range=(min(lo[0],lo[0]+shift),max(hi[0],hi[0]+shift))
        for stand_y in (1.35,1.55,1.85):
            for pallet_width in (2.50,2.90):
                # Add a 0.30 m trial pallet projection beyond either end of the bare stock.
                crossed=[x for x in (-6.9,6.9) if x+.2 >= x_range[0]-.3 and x-.2 <= x_range[1]+.3]
                margin=stand_y-.13-max(abs(lo[1]),abs(hi[1]),pallet_width/2)
                trials.append(dict(bogie=name,travel_x_m=shift,pallet_width_m=pallet_width,
                    bare_swept_x_m=list(map(float,x_range)),stand_y_abs_m=stand_y,
                    encountered_stand_lines_x_m=crossed,minimum_transverse_gap_m=margin,
                    result="geometric interference" if crossed and margin<=0 else "positive nominal clearance"))
    return trials


def evaluate():
    with ZipFile(PACKET) as archive:
        manifest=json.loads(archive.read("manifest.json"))
        for name in ("mechanical.json","START.html"):
            if sha256(archive.read(name)).hexdigest()!=manifest["sha256"][name]:
                raise ValueError("Input member changed")
        article=json.loads(archive.read("mechanical.json"))
        if manifest["candidate_id"]!=article["candidate_id"]:
            raise ValueError("Archive identity differs from mechanical article")
        page=ModelPage()
        page.feed(archive.read("START.html").decode())
        models={}
        for name in ("car-and-bogies","track-span","pier","platform-bay"):
            row,bounds=stock_model(archive,manifest,name,article,page.data["geometry"]["car" if name=="car-and-bogies" else name])
            models[name]=row
            if name=="car-and-bogies":
                trials=exchange(article,bounds)
    vehicle=evaluate_vehicle()
    base=vehicle["selected"]
    tare, loaded = base["tare_train_kg"], base["loaded_train_kg"]
    nominal=vehicle["structure"]["body_vertical"]["central"]["1.0"]["peak_section_stress_mpa"]
    # Linear same member and load shape. Weld-toe stress range and cycle counts unknown.
    tare_nominal=nominal*tare/loaded
    coupled=[]
    for kmh in (3,5,8):
        # Two identical free trains coalesce. Lost kinetic energy is mu*v_rel^2/2.
        energy_j=loaded*(kmh/3.6)**2/4
        coupled.append(dict(relative_kmh=kmh, dissipated_interface_kj=energy_j/1000,
            required_mean_force_kn_if_0p15m_stroke=energy_j/.15/1000))
    return dict(vehicle_civil_evaluation_id=vehicle["evaluation_id"],
        steel_static_range=dict(tare_nominal_mpa=tare_nominal,full_nominal_mpa=nominal,
            same_section_elastic_range_mpa=nominal-tare_nominal,
            welded_fatigue_life_cycles=None, load_basis="Released steel planar load shape, identical sign and governing member."),
        unbraked_equal_train_coupling_enquiry=coupled,
        coupling_scope="Free equal masses after perfectly inelastic coupling. Stroke is a study hypothesis. Actual absorber force/stroke, occupied space, override and deceleration histories are open.",
        four_stand_full_tare_symmetric_kn=tare/6*9.80665/4000,
        parent_candidate_id=article["candidate_id"],mechanical_evaluation_id=article["evaluation_id"],
        reader_version=ifcopenshell.version,packet_sha256=sha256(PACKET.read_bytes()).hexdigest(),
        script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(), assemblies=models, bogie_exchange=trials,
        trial_fixture="Four 0.40 x 0.26 m stand feet at x = +/-6.9 m, positive and negative y, overlapping pallet height. Longitudinal extraction ends at the released stock travel. Adjacent cars removed.",
        open=["Stand load rating, lift pads, local buckling and locking arrangement","Wheelsets, drive, calipers, cooling, cables and pallet hoist as-installed swept envelopes",
              "Weld toe detail, duty spectrum, local stress concentration, fatigue endurance and inspection interval",
              "Braking, collision energy absorption and passenger survivable volume","Jig gauge survey, bearing fits, reinstallation and witnessed brake test"],
        status="Native stock and trial fixturing comparison",physical_acceptance=False)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    output=json.dumps(evaluate(),indent=2,sort_keys=True,allow_nan=False)+"\n"
    if args.check:
        if output!=(HERE/"ifc-results.json").read_text():
            raise SystemExit("IFC comparison differs from the released result")
    else:
        print(output,end="")
