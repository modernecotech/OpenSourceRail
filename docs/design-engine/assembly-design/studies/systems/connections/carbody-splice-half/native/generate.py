import sys,runpy
sys.path[:0]=['/home/hayder/Documents/OpenSourceRail', '/home/hayder/Documents/OpenSourceRail/design/component-catalogue/src']
module=runpy.run_path('/home/hayder/Documents/OpenSourceRail/engineering/design_engine/native_cad.py')
module["native"]('/home/hayder/.local/state/opensourcerail/assembly-design/epochs/01825e46f50c03880b426ab2dcefc5bf7c8a0f969c25320251aee1f02aee75d2/closure-studies-attempt/systems/connections/carbody-splice-half/definition.json','/home/hayder/.local/state/opensourcerail/assembly-design/epochs/01825e46f50c03880b426ab2dcefc5bf7c8a0f969c25320251aee1f02aee75d2/closure-studies-attempt/systems/connections/carbody-splice-half/native')
import json,hashlib
from pathlib import Path
import FreeCAD as App
definition=json.loads(Path('/home/hayder/.local/state/opensourcerail/assembly-design/epochs/01825e46f50c03880b426ab2dcefc5bf7c8a0f969c25320251aee1f02aee75d2/closure-studies-attempt/systems/connections/carbody-splice-half/definition.json').read_text())
unit_map={p["id"]:p["manufacturing_unit_id"] for p in definition["parts"] if p.get("manufacturing_unit_id")}
if unit_map:
    path=Path('/home/hayder/.local/state/opensourcerail/assembly-design/epochs/01825e46f50c03880b426ab2dcefc5bf7c8a0f969c25320251aee1f02aee75d2/closure-studies-attempt/systems/connections/carbody-splice-half/native')
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
