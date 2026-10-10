"""Native Assembly joints and unissued TechDraw views for shared instances.

The joint solver establishes placement/motion constraints. Mechanical property
records remain separate; native placement solving supplies no load acceptance.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

from .engineering_definition import validate, fingerprint
from .freecad_occ_bridge import SourceGeometry, freecad_shape_from_source, safe_name
from .freecad_assembly_review import _canonicalise_fcstd
from .family_definition import family_definition, ROOT
from .joint_design import definitions as joint_definitions


def build_document(model, output):
    import FreeCAD as App
    import Part
    import JointObject
    import numpy as np
    definition=validate(model)
    if any(r['transform'] is None for r in model['instances']):
        raise ValueError('native assembly needs defined instance transforms')
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists():raise ValueError('native engineering evidence output already exists')
    doc=App.newDocument('SharedEngineering')
    root=doc.addObject('Assembly::AssemblyObject','TrainAssembly');root.Type='Assembly'
    group=root.newObject('Assembly::JointGroup','Joints');features={};cache={}
    def placement(t):
        r=t['rotation'];matrix=App.Matrix()
        for i in range(3):
            for j in range(3):setattr(matrix,f'A{i+1}{j+1}',r[i][j])
        return App.Placement(App.Vector(*(v*1000 for v in t['translation_m'])),App.Rotation(matrix))
    for row in model['instances']:
        if row['part_id']=='LM3-CAR-A900':
            source=SourceGeometry('car-body-17m',definition['car_length_m']*1000)
        else:source=SourceGeometry('product:'+row['part_id'])
        feature=root.newObject('Part::Feature',safe_name(row['id']));feature.Label=row['id']
        if row['geometry']['kind'] in ('released-solid','supplier-installation'):
            reference=row['geometry']['source'][0];path=ROOT/reference['path']
            if path.suffix.lower()!='.brep':raise ValueError('native released geometry adapter requires an explicit BREP solid')
            shape=Part.Shape();shape.read(str(path))
            if not shape.isValid() or not shape.Solids:raise ValueError('released geometry source is not a valid solid')
            feature.Shape=shape
        else:
            feature.Shape=freecad_shape_from_source(source,part_module=Part,cache=cache,temp_dir=output.parent)
        feature.Placement=placement(row['transform'])
        for name,value in [('InstanceId',row['id']),('PartId',row['part_id']),('PartRevision',row['revision']),('ConfigurationHash',fingerprint(model)),
                           ('GeometryStatus',row['geometry']['kind']),('PropertySource',row['property_source']),('Datums',json.dumps(row['datums'],sort_keys=True))]:
            feature.addProperty('App::PropertyString',name,'Shared Engineering');setattr(feature,name,value)
        for name,datum in row['datums'].items():
            property_name='Datum_'+safe_name(name)
            feature.addProperty('App::PropertyPlacement',property_name,'Engineering Datums')
            setattr(feature,property_name,placement(datum))
        feature.addProperty('App::PropertyBool','ProductionReleased','Shared Engineering');feature.ProductionReleased=False
        features[row['id']]=feature
    ground=group.newObject('App::FeaturePython','GroundedBody')
    grounded=next(r['id'] for r in model['instances'] if r['body'])
    JointObject.GroundedJoint(ground,features[grounded])
    joint_objects=[]
    for row in model['joints']:
        kind='Revolute' if row['type'] in ('revolute','articulation') else 'Slider' if row['type'] in ('slider','suspension') else 'Fixed'
        joint=group.newObject('App::FeaturePython',safe_name(row['id']));joint.Label=row['id']
        JointObject.Joint(joint,{'Fixed':0,'Revolute':1,'Slider':3}[kind])
        joint.Detach1=True;joint.Detach2=True
        for index,endpoint in enumerate(row['endpoints'],1):
            instance=next(r for r in model['instances'] if r['id']==endpoint['instance'])
            setattr(joint,'Reference'+str(index),(features[instance['id']],['']))
            setattr(joint,'Placement'+str(index),placement(instance['datums'][endpoint['datum']]))
        joint.addProperty('App::PropertyString','EngineeringJointId','Shared Engineering');joint.EngineeringJointId=row['id']
        joint.addProperty('App::PropertyString','MechanicalDefinition','Shared Engineering');joint.MechanicalDefinition=json.dumps(row,sort_keys=True)
        joint_objects.append(joint)
    doc.recompute();solver_result=root.solve();doc.recompute()
    residuals=[]
    for row,joint in zip(model['joints'],joint_objects):
        locations=[];rotations=[]
        for index,endpoint in enumerate(row['endpoints'],1):
            feature=features[endpoint['instance']];local=getattr(joint,'Placement'+str(index))
            locations.append(feature.Placement.multVec(local.Base))
            rotations.append(feature.Placement.Rotation.multiply(local.Rotation))
        # Fixed/revolute connectors coincide; sliders can retain their installed
        # displacement along the free Z axis, but cannot move off that axis.
        delta=locations[1]-locations[0]
        residual=delta.Length if joint.JointType!='Slider' else (delta.x*delta.x+delta.y*delta.y)**.5
        if joint.JointType=='Revolute':
            a=rotations[0].multVec(App.Vector(0,0,1));b=rotations[1].multVec(App.Vector(0,0,1));rotation_error=(a-b).Length
        else:rotation_error=rotations[0].inverted().multiply(rotations[1]).Angle
        residuals.append(dict(joint_id=row['id'],native_type=joint.JointType,datum_residual_mm=residual,orientation_residual=rotation_error))
    solved=type(solver_result) is int and solver_result==0 and all(r['datum_residual_mm']<1e-5 and r['orientation_residual']<1e-8 for r in residuals)
    if not solved:raise ValueError('native Assembly solver/datum reconciliation failed')
    # An actual generated drawing page references the actual installed geometry.
    # Fit/tolerance/procedure fields remain open and drawing issue stays separate.
    page=doc.addObject('TechDraw::DrawPage','AssemblyDrawing')
    template=doc.addObject('TechDraw::DrawSVGTemplate','DrawingTemplate')
    templates=Path(App.getResourceDir())/'Mod/TechDraw/Templates'
    candidates=list(templates.glob('A4_Landscape*.svg')) or list(templates.glob('*.svg'))
    if not candidates:raise RuntimeError('TechDraw installation lacks drawing templates')
    template.Template=str(sorted(candidates)[0]);page.Template=template
    view=doc.addObject('TechDraw::DrawViewPart','InstalledAssemblyView');view.Source=list(features.values())
    view.Direction=App.Vector(0,-1,0);view.Scale=.005;view.X=148.;view.Y=100.;page.addView(view)
    top=doc.addObject('TechDraw::DrawViewPart','InstalledPlanView');top.Source=list(features.values())
    top.Direction=App.Vector(0,0,1);top.Scale=.005;top.X=148.;top.Y=155.;page.addView(top)
    bogie=next(r for r in model['instances'] if r['part_id']=='LM3-BOG-P010')
    detail=doc.addObject('TechDraw::DrawViewPart','PoweredBogieView')
    detail.Source=[features[r['id']] for r in model['instances'] if r['bogie']==bogie['bogie']]
    detail.Direction=App.Vector(0,-1,0);detail.Scale=.025;detail.X=80.;detail.Y=50.;page.addView(detail)
    section=doc.addObject('TechDraw::DrawViewSection','PoweredBogieSection')
    section.BaseView=detail;section.SectionNormal=App.Vector(1,0,0)
    section.SectionOrigin=placement(bogie['transform']).Base;section.Direction=App.Vector(1,0,0)
    section.XDirection=App.Vector(0,1,0)
    section.Scale=.025;section.X=200.;section.Y=50.;page.addView(section)
    schedule=joint_definitions(model)
    annotation=doc.addObject('TechDraw::DrawViewAnnotation','ManufacturingNotes')
    annotation.Text=['UNISSUED — '+model['revision'],
        'Datums: '+', '.join(sorted({name for r in model['instances'] for name in r['datums']})),
        'Fits/tolerances/procedures: OPEN; refer to physical joint register',
        'Inspection IDs: '+', '.join(r['id'] for r in model['inspections'])]
    annotation.TextSize=2.;annotation.X=148.;annotation.Y=18.;page.addView(annotation)
    page.addProperty('App::PropertyBool','DrawingIssued','Shared Engineering');page.DrawingIssued=False
    page.addProperty('App::PropertyString','ConfigurationHash','Shared Engineering');page.ConfigurationHash=fingerprint(model)
    page.addProperty('App::PropertyString','PhysicalJointSchedule','Shared Engineering');page.PhysicalJointSchedule=json.dumps(schedule,sort_keys=True)
    doc.recompute()
    drawing_edge_counts={v.Name:len(v.getVisibleEdges()) for v in (view,top,detail,section)}
    if any(n==0 for n in drawing_edge_counts.values()):raise RuntimeError('native drawing/section projection contains no geometry')
    doc.saveAs(str(output));App.closeDocument(doc.Name);_canonicalise_fcstd(output)
    result=dict(schema='osr-native-shared-assembly/1',configuration_sha256=fingerprint(model),
                sources_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'design/component-catalogue/src/osr_mech').rglob('*.py'))},
                freecad_version=list(App.Version()),native_assembly_solver_executed=True,native_solver_result=str(solver_result),
                nominal_datums_reconciled=solved,joints=residuals,instance_count=len(features),
                overall_family_length_m=definition['length_m'],represented_car_count=len({r['body'] for r in model['instances'] if r['body']}),
                drawing_generated=True,drawing_issued=False,manufacturing_geometry_released=False,
                drawing_views=['installed elevation','installed plan','powered bogie','powered bogie section'],
                drawing_visible_edges=drawing_edge_counts,
                physical_joint_register=schedule,
                dynamic_properties_verified_by_assembly_solver=False,physical_validation=False,
                fcstd_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    output.with_suffix('.native.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result
