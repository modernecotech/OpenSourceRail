import sys,runpy
sys.path[:0]=['/home/hayder/Documents/OpenSourceRail', '/home/hayder/Documents/OpenSourceRail/design/component-catalogue/src']
module=runpy.run_path('/home/hayder/Documents/OpenSourceRail/engineering/design_engine/native_cad.py')
module["native"]('/home/hayder/.local/state/opensourcerail/assembly-design/epochs/a31b519b4a3700575ff57cd78c58fcd958d36c3ef8cefadc4da0fbc123e322bb/closure-studies-attempt/panels/roof-aluminium-sandwich/definition.json','/home/hayder/.local/state/opensourcerail/assembly-design/epochs/a31b519b4a3700575ff57cd78c58fcd958d36c3ef8cefadc4da0fbc123e322bb/closure-studies-attempt/panels/roof-aluminium-sandwich/native')
import json,hashlib
from pathlib import Path
import FreeCAD as App
definition=json.loads(Path('/home/hayder/.local/state/opensourcerail/assembly-design/epochs/a31b519b4a3700575ff57cd78c58fcd958d36c3ef8cefadc4da0fbc123e322bb/closure-studies-attempt/panels/roof-aluminium-sandwich/definition.json').read_text())
unit_map={p["id"]:p["manufacturing_unit_id"] for p in definition["parts"] if p.get("manufacturing_unit_id")}
if unit_map:
    path=Path('/home/hayder/.local/state/opensourcerail/assembly-design/epochs/a31b519b4a3700575ff57cd78c58fcd958d36c3ef8cefadc4da0fbc123e322bb/closure-studies-attempt/panels/roof-aluminium-sandwich/native')
    doc=App.openDocument(str(path/"candidate.FCStd"))
    for obj in doc.Objects:
        if hasattr(obj,"PhysicalPartId") and obj.PhysicalPartId in unit_map:
            if not hasattr(obj,"ManufacturingUnitId"): obj.addProperty("App::PropertyString","ManufacturingUnitId")
            obj.ManufacturingUnitId=unit_map[obj.PhysicalPartId]
    doc.save();App.closeDocument(doc.Name)
    doc=App.openDocument(str(path/"candidate.FCStd"))
    actual={obj.PhysicalPartId:obj.ManufacturingUnitId for obj in doc.Objects if hasattr(obj,"PhysicalPartId") and hasattr(obj,"ManufacturingUnitId")}
    App.closeDocument(doc.Name)
    proof=json.loads((path/"native-cad.json").read_text());proof["manufacturing_unit_ids_preserved"]=(actual==unit_map)
    proof["files_sha256"]={name:hashlib.sha256((path/name).read_bytes()).hexdigest() for name in proof["files_sha256"]}
    (path/"native-cad.json").write_text(json.dumps(proof,sort_keys=True,indent=2)+"\n")
