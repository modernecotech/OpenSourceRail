#!/usr/bin/env python3
"""Run in FreeCADCmd; audit shared part solids, placements, inertia and occupied volume."""
from pathlib import Path
import hashlib,importlib.util,json,math,sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
import FreeCAD as App
import Part
import numpy as np
from osr_mech.automated_geometry import native_shape,aggregate,primitive_volume
from osr_mech.freecad_assembly_review import _canonicalise_fcstd
spec=importlib.util.spec_from_file_location('study',ROOT/'tools/automation/design-consistency-study.py');study=importlib.util.module_from_spec(spec);spec.loader.exec_module(study)
OUT=ROOT/'engineering/design_consistency/examples';cad=OUT/'cad';cad.mkdir(parents=True,exist_ok=True)


def run():
    records=[];files={}
    for name in ('side','roof','interface','viaduct'):
        model=json.loads((OUT/(name+'.json')).read_text());document=App.newDocument('Consistency_'+name);shapes=[];checks=[]
        for i,p in enumerate(model['parts']):
            shape=native_shape(p['manufacturing'],Part,App);obj=document.addObject('Part::Feature',f'Part_{i}');obj.Label=p['id'];obj.Shape=shape
            matrix=App.Matrix()
            for a in range(3):
                for b in range(3):setattr(matrix,f'A{a+1}{b+1}',p['placement']['rotation'][a][b])
            obj.Placement=App.Placement(App.Vector(*(v*1000 for v in p['placement']['translation_m'])),App.Rotation(matrix))
            obj.addProperty('App::PropertyString','PhysicalPartId');obj.PhysicalPartId=p['id']
            obj.addProperty('App::PropertyString','GeometrySHA256');obj.GeometrySHA256=p['analysis']['geometry_sha256']
            for field,value in [('PartRevision',p['revision']),('MaterialIdentity',p['material']),
                ('MaterialBasis',model['materials'][p['material']]['basis']),
                ('ManufacturingLimits',json.dumps(p['manufacturing_limits'],sort_keys=True)),
                ('InspectionCharacteristics',json.dumps(p['inspection_characteristics'])),
                ('LaminatePly',json.dumps(p.get('laminate_ply'),sort_keys=True)),
                ('DefinitionFile',name+'.json')]:
                obj.addProperty('App::PropertyString',field);setattr(obj,field,value)
            obj.addProperty('App::PropertyFloat','DensityKgM3');obj.DensityKgM3=model['materials'][p['material']]['density_kg_m3']
            obj.addProperty('App::PropertyBool','ProductionReleased');obj.ProductionReleased=False
            density=model['materials'][p['material']]['density_kg_m3'];expected=p['properties'];shape=obj.Shape
            mass=shape.Volume/1e9*density
            centres=[np.array([s.CenterOfMass.x,s.CenterOfMass.y,s.CenterOfMass.z])/1000 for s in shape.Solids]
            masses=[s.Volume/1e9*density for s in shape.Solids];cg=sum((m*c for m,c in zip(masses,centres)),np.zeros(3))/mass
            inertia=np.zeros((3,3))
            for s,m,c in zip(shape.Solids,masses,centres):
                own=np.array([[getattr(s.MatrixOfInertia,f'A{a+1}{b+1}')for b in range(3)]for a in range(3)])*density/1e15
                delta=c-cg;inertia+=own+m*((delta@delta)*np.eye(3)-np.outer(delta,delta))
            err=abs(mass/expected['mass_kg']-1);cgerr=float(np.linalg.norm(cg-expected['cg_m']));ierr=float(np.linalg.norm(inertia-expected['inertia_tensor_kg_m2'])/np.linalg.norm(expected['inertia_tensor_kg_m2']))
            if not shape.isValid()or err>1e-7 or cgerr>1e-7 or ierr>1e-7:raise ValueError((name,p['id'],err,cgerr,ierr))
            for a,solid in enumerate(shape.Solids):
                for other in shape.Solids[a+1:]:
                    if solid.BoundBox.intersect(other.BoundBox)and solid.common(other).Volume>1e-3:raise ValueError('internal material overlap '+p['id'])
            checks.append(dict(physical_part_id=p['id'],volume_mass_relative_error=err,cg_error_m=cgerr,inertia_relative_error=ierr));shapes.append((p['id'],shape))
        intersections=[]
        for i,(identity,shape)in enumerate(shapes):
            for other,other_shape in shapes[i+1:]:
                if shape.BoundBox.intersect(other_shape.BoundBox):
                    volume=shape.common(other_shape).Volume
                    if volume>1e-3:intersections.append(dict(left=identity,right=other,volume_mm3=volume))
        if intersections:raise ValueError((name,'physical material overlap',intersections[:12]))
        document.recompute();objects=[o for o in document.Objects if 'PhysicalPartId'in o.PropertiesList]
        # Inspection drawings show the generated assembly; drawing issue remains false.
        page=document.addObject('TechDraw::DrawPage','InspectionDrawing');template=document.addObject('TechDraw::DrawSVGTemplate','InspectionTemplate')
        template.Template=str(sorted((Path(App.getResourceDir())/'Mod/TechDraw/Templates').glob('*.svg'))[0]);page.Template=template
        view=document.addObject('TechDraw::DrawViewPart','AssemblyElevation');view.Source=objects;view.Direction=App.Vector(0,-1,0);view.X=148;view.Y=105;view.Scale=.009 if name=='viaduct'else .045;page.addView(view)
        page.addProperty('App::PropertyBool','DrawingIssued');page.DrawingIssued=False;document.recompute()
        edges=len(view.getVisibleEdges())
        if not edges:raise ValueError('empty inspection projection')
        native=cad/(name+'.FCStd');step=cad/(name+'.step');Part.export(objects,str(step));document.saveAs(str(native));App.closeDocument(document.Name);_canonicalise_fcstd(native)
        restored=App.openDocument(str(native));reopened=[o for o in restored.Objects if 'PhysicalPartId'in o.PropertiesList]
        expected_parts={p['id']:p for p in model['parts']}
        if len(reopened)!=len(expected_parts)or any(not o.Shape.isValid()for o in reopened):raise ValueError('reopened native part map differs')
        for obj in reopened:
            p=expected_parts[obj.PhysicalPartId]
            if obj.MaterialIdentity!=p['material']or obj.PartRevision!=p['revision']or obj.DensityKgM3!=model['materials'][p['material']]['density_kg_m3']or json.loads(obj.LaminatePly)!=p.get('laminate_ply')or obj.ProductionReleased:raise ValueError('reopened native material/revision differs')
        App.closeDocument(restored.Name)
        # STEP reimport checks the actual neutral geometry, not just file presence.
        imported=Part.read(str(step));expected_volume=sum(primitive_volume(q)for p in model['parts']for q in p['manufacturing']['primitives'])*1e9
        if not imported.isValid()or abs(imported.Volume/expected_volume-1)>1e-7:raise ValueError('STEP material volume differs')
        for path in (native,step):files[path.relative_to(OUT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
        records.append(dict(model=name,part_count=len(checks),checks=checks,material_intersections=intersections,inspection_projection_edges=edges,drawing_issued=False,native_reopened=True,step_reimport_volume_reconciled=True))
        print('Verified native research assembly:',name,len(checks),flush=True)
    receipt=dict(schema='osr-shared-native-representations/1',source_sha256=study.sources(),output_sha256=files,records=records,
        freecad_version=App.Version(),opencascade_version=Part.OCC_VERSION,physical_validation=False,production_released=False)
    (cad/'verification.json').write_bytes(study.encode(receipt))
try:run()
except Exception:
    import traceback
    traceback.print_exc();sys.exit(1)
