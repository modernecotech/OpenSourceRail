#!/usr/bin/env python3
"""Native occupied-material verification of refined side-bay arrangements."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
import FreeCAD as App
import Part
import numpy as np
from osr_mech.automated_geometry import native_shape,primitive_volume
from osr_mech.engineering_definition import fingerprint
from osr_mech.freecad_assembly_review import _canonicalise_fcstd
# Source hashing has no solver-side dependencies; avoid importing SciPy in FreeCAD.
paths=sorted((ROOT/'engineering/panel_response').glob('*.py'))+[ROOT/'engineering/composite_panels/config/development.json',ROOT/'tools/automation/panel-response-study.py',Path(__file__)]
paths += [ROOT/'engineering/design_consistency'/p for p in ('demonstrators.py','contracts.py')]
paths += [ROOT/'design/component-catalogue/src/osr_mech'/p for p in ('automated_geometry.py','engineering_definition.py','section_contract.py','rolling_stock/composite_panels.py')]
source_hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}
OUT=ROOT/'engineering/panel_response/examples';cad=OUT/'cad';cad.mkdir(parents=True,exist_ok=True)


def run():
    records=[];files={}
    for name in ('baseline','closer-supports','dense-supports','tight-supports','deeper-rails'):
        model=json.loads((OUT/(name+'.json')).read_text());doc=App.newDocument(name.replace('-','_'));shapes=[];errors=[]
        for i,p in enumerate(model['parts']):
            if p['placement']['translation_m']!=[0,0,0]or p['placement']['rotation']!=np.eye(3).tolist():raise ValueError('side-bay adapter requires identity placements')
            shape=native_shape(p['manufacturing'],Part,App);expected=sum(primitive_volume(q)for q in p['manufacturing']['primitives'])*1e9;error=abs(shape.Volume/expected-1)
            if not shape.isValid()or error>1e-7:raise ValueError('native material region differs: '+p['id'])
            obj=doc.addObject('Part::Feature',f'Part_{i}');obj.Label=p['id'];obj.Shape=shape
            for field,value in [('PhysicalPartId',p['id']),('MaterialIdentity',p['material']),('GeometrySHA256',p['analysis']['geometry_sha256']),('LaminatePly',json.dumps(p.get('laminate_ply')))]:
                obj.addProperty('App::PropertyString',field);setattr(obj,field,value)
            obj.addProperty('App::PropertyBool','ProductionReleased');obj.ProductionReleased=False
            shapes.append((p['id'],shape));errors.append(error)
        for i,(identity,shape)in enumerate(shapes):
            for other,other_shape in shapes[i+1:]:
                if shape.BoundBox.intersect(other_shape.BoundBox)and shape.common(other_shape).Volume>1e-3:raise ValueError('native material overlap: '+identity+' / '+other)
        doc.recompute();objects=doc.Objects;path=cad/(name+'.FCStd');step=cad/(name+'.step');Part.export(objects,str(step));doc.saveAs(str(path));App.closeDocument(doc.Name);_canonicalise_fcstd(path)
        restored=App.openDocument(str(path));features=[o for o in restored.Objects if 'PhysicalPartId'in o.PropertiesList]
        expected_ids={p['id']for p in model['parts']}
        if {o.PhysicalPartId for o in features}!=expected_ids or any(not o.Shape.isValid()or o.ProductionReleased for o in features):raise ValueError('restored material/part identities differ')
        App.closeDocument(restored.Name);imported=Part.read(str(step));volume=sum(s.Volume for _,s in shapes)
        if not imported.isValid()or abs(imported.Volume/volume-1)>1e-7:raise ValueError('STEP material volume changed')
        records.append(dict(name=name,contract_sha256=fingerprint(model),physical_region_count=len(shapes),maximum_volume_relative_error=max(errors),material_overlaps=False,native_reopened=True,step_volume_reconciled=True))
        for p in (path,step):files[p.relative_to(OUT).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
        print('Verified native refined side bay',name,flush=True)
    (cad/'verification.json').write_text(json.dumps(dict(schema='osr-native-refined-panel-cad/1',source_sha256=source_hashes,output_sha256=files,records=records,freecad_version=App.Version(),physical_validation=False,production_released=False),indent=2,sort_keys=True)+'\n')
try:run()
except Exception:
    import traceback
    traceback.print_exc();sys.exit(1)
