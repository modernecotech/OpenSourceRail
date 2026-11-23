"""Optional native reader for the scenario-specific IFC4 and purchasing exchange."""
import argparse
from collections import Counter
import csv
from hashlib import sha256
import io
import json
from pathlib import Path
from zipfile import ZipFile

import ifcopenshell
import ifcopenshell.geom
from ifcopenshell.util.placement import get_local_placement
from ifcopenshell.util.shape import get_volume
from ifcopenshell.util.unit import calculate_unit_scale


def verify(files):
    meta=json.loads(files["candidate/exchange.json"])
    if any(sha256(files[k]).hexdigest()!=v for k,v in meta["bytes_sha256"].items()):
        raise ValueError("Exchange fingerprint differs")
    model=ifcopenshell.file.from_string(files["candidate/airport-layout.ifc"].decode())
    project=model.by_type("IfcProject")[0]
    if project.Description!=f"physical={meta['physical_id']} evaluation={meta['evaluation_id']}" or calculate_unit_scale(model)!=1:
        raise ValueError("Project identity or units differ")
    products=model.by_type("IfcBuildingElementProxy")
    counts=Counter(p.ObjectType for p in products)
    if counts!=meta["counts"] or len(set(p.GlobalId for p in products))!=len(products):
        raise ValueError("Quantity or GUID mismatch")
    by={p.Tag:p for p in products}
    positions={}
    for kind in sorted(counts):
        group=[p for p in products if p.ObjectType==kind]
        xyz=[get_local_placement(p.ObjectPlacement)[:3,3] for p in group]
        positions[kind]={"first":xyz[0].tolist(),"last":xyz[-1].tolist()}
    settings=ifcopenshell.geom.settings()
    beam=ifcopenshell.geom.create_shape(settings,by["TrackSpan-1-0001"])
    volume=get_volume(beam.geometry)
    if abs(volume-meta["expected_concrete_m3_per_span"])>1e-6:
        raise ValueError("Native span solid volume differs")
    L=meta["span_stock_m"]
    if positions["TrackSpan"]["first"]!=[L/2,-5.425,-1.65] or positions["TrackSpan"]["last"]!=[12000-L/2,5.425,-1.65]:
        raise ValueError("Native beam placement differs")
    pivots=counts["BogiePivot"]
    if pivots!=2*counts["CarEnvelope"] or counts["BearingDatum"]!=4*counts["TrackSpan"]:
        raise ValueError("Vehicle or bearing count mismatch")
    q=meta["fleet_quantity"]
    if not (counts["CarEnvelope"]*q["sets"]==q["cars"] and q["grid_sites"]==counts["FeederChainage"]
            and q["piers"]==counts["PierFooting"]):
        raise ValueError("ERP and drawing occurrence counts differ")
    for name in ("planning-quantities.csv","procurement-lots.csv","production-workcells.csv"):
        rows=list(csv.DictReader(io.StringIO(files["candidate/"+name].decode())))
        if not rows or any(r["physical_id"]!=meta["physical_id"] or r["evaluation_id"]!=meta["evaluation_id"] for r in rows):
            raise ValueError("ERP file bound to different candidate/evaluation")
    return dict(physical_id=meta["physical_id"],evaluation_id=meta["evaluation_id"],ifc_version=ifcopenshell.version,
        schema=model.schema,count=len(products),families=dict(counts),first_last_coordinates_m=positions,
        native_beam_volume_m3=volume,ifc_sha256=meta["bytes_sha256"]["candidate/airport-layout.ifc"],
        scope="Native IFC4 project, all occurrence identities and translations, representative beam solid and CSV references.")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dossier",type=Path)
    args=parser.parse_args()
    with ZipFile(args.dossier) as packet:
        files={k:packet.read(k) for k in packet.namelist() if k.startswith("candidate/")}
    print(json.dumps(verify(files),indent=2))
