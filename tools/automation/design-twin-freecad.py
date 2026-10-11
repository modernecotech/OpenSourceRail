#!/usr/bin/env python3
"""Native train/federation geometry, joint solve, reopened solid and STEP audits."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]


def build_train(model):
    """Build the native installed assembly directly, then draw only study details."""
    import FreeCAD as App
    import Part,JointObject
    from osr_mech.engineering_definition import validate,fingerprint
    from osr_mech.automated_geometry import from_source,native_shape
    from osr_mech.freecad_occ_bridge import SourceGeometry,freecad_shape_from_source,safe_name
    validate(model);doc=App.newDocument('BestPracticeTwin')
    root=doc.addObject('Assembly::AssemblyObject','TrainAssembly');root.Type='Assembly'
    joints=root.newObject('Assembly::JointGroup','Joints');features={};cache={}
    def placement(t):
        matrix=App.Matrix()
        for i in range(3):
            for j in range(3):setattr(matrix,f'A{i+1}{j+1}',t['rotation'][i][j])
        return App.Placement(App.Vector(*(v*1000 for v in t['translation_m'])),App.Rotation(matrix))
    for row in model['instances']:
        feature=root.newObject('Part::Feature',safe_name(row['id']));feature.Label=row['id']
        spec=from_source(row['geometry'])
        if spec is not None:feature.Shape=native_shape(spec,Part,App)
        else:
            src=SourceGeometry('car-body-17m',model['family_definition']['car_length_m']*1000) if row['part_id']=='LM3-CAR-A900' else SourceGeometry('product:'+row['part_id'])
            feature.Shape=freecad_shape_from_source(src,part_module=Part,cache=cache,temp_dir=ROOT/'build')
        feature.Placement=placement(row['transform'])
        for name,value in [('InstanceId',row['id']),('PartId',row['part_id']),('PartRevision',row['revision']),('ConfigurationHash',fingerprint(model)),('Datums',json.dumps(row['datums']))]:
            feature.addProperty('App::PropertyString',name,'OSR Study');setattr(feature,name,value)
        feature.addProperty('App::PropertyBool','ProductionReleased','OSR Study');feature.ProductionReleased=False
        features[row['id']]=feature
    ground=joints.newObject('App::FeaturePython','GroundedBody');JointObject.GroundedJoint(ground,features[model['instances'][0]['id']])
    instances={row['id']:row for row in model['instances']};objects=[]
    for row in model['joints']:
        kind=1 if row['type'] in ('revolute','articulation') else 3 if row['type'] in ('slider','suspension') else 0
        joint=joints.newObject('App::FeaturePython',safe_name(row['id']));joint.Label=row['id'];JointObject.Joint(joint,kind)
        joint.Detach1=True;joint.Detach2=True
        for i,e in enumerate(row['endpoints'],1):
            setattr(joint,'Reference'+str(i),(features[e['instance']],['']))
            setattr(joint,'Placement'+str(i),placement(instances[e['instance']]['datums'][e['datum']]))
        joint.addProperty('App::PropertyString','EngineeringJointId','OSR Study');joint.EngineeringJointId=row['id'];objects.append(joint)
    doc.recompute();solved=root.solve();doc.recompute();residuals=[]
    for row,joint in zip(model['joints'],objects):
        a,b=row['endpoints'];pa=features[a['instance']].Placement.multiply(joint.Placement1);pb=features[b['instance']].Placement.multiply(joint.Placement2)
        delta=pb.Base-pa.Base
        position=(delta.x*delta.x+delta.y*delta.y)**.5 if joint.JointType=='Slider' else delta.Length
        orientation=(pa.Rotation.multVec(App.Vector(0,0,1))-pb.Rotation.multVec(App.Vector(0,0,1))).Length if joint.JointType=='Revolute' else pa.Rotation.inverted().multiply(pb.Rotation).Angle
        residuals.append(dict(joint_id=row['id'],datum_residual_mm=position,orientation_residual=orientation))
    if solved!=0 or any(r['datum_residual_mm']>1e-5 or r['orientation_residual']>1e-8 for r in residuals):
        raise ValueError('native installed assembly constraints differ')
    return doc,dict(native_solver_result=str(solved),joints=residuals)


def native(package,output):
    import FreeCAD as App
    import Part
    from osr_mech.engineering_definition import load_definition,fingerprint
    from osr_mech.freecad_assembly_review import _canonicalise_fcstd
    from osr_mech.automated_geometry import native_shape,primitive_volume,primitive_inertia
    import numpy as np
    model=load_definition(package/'model.json');infra=load_definition(package/'infrastructure.json')
    features=load_definition(package/'features.json');review=load_definition(package/'review.json')
    doc,initial=build_train(model);group=doc.addObject('App::DocumentObjectGroup','InfrastructureStudy')
    added=[];infra_features=[];train={o.InstanceId:o for o in doc.Objects if 'InstanceId' in o.PropertiesList}
    for row in infra['items']:
        feature=doc.addObject('Part::Feature','Infra_'+str(len(infra_features)));feature.Label=row['id']
        feature.Shape=native_shape(row['geometry'],Part,App)
        # Adjacent study section displayed below the train, using an explicit view offset.
        p=row['transform']['translation_m'];feature.Placement.Base=App.Vector(p[0]*1000,(p[1]+5)*1000,p[2]*1000)
        for key,value in [('InstanceId',row['id']),('PartId',row['part_id']),('GeometryRole',row['role']),('Sources',json.dumps(row['source_ids']))]:
            feature.addProperty('App::PropertyString',key,'OSR Study');setattr(feature,key,value)
        feature.addProperty('App::PropertyBool','ProductionReleased','OSR Study');feature.ProductionReleased=False
        group.addObject(feature);infra_features.append(feature)
    for row in features:
        feature=train[row['instance_id']]
        feature.addProperty('App::PropertyString','ResearchSources','OSR Study');feature.ResearchSources=json.dumps(row['source_ids'])
        feature.addProperty('App::PropertyString','PracticeIds','OSR Study');feature.PracticeIds=json.dumps(row['practice_ids'])
        feature.addProperty('App::PropertyFloat','StudyMassKg','OSR Study');feature.StudyMassKg=row['mass_kg']
        if row['instance_id'].startswith('car-1/'):added.append(feature)
    page=doc.addObject('TechDraw::DrawPage','DesignDetailDrawing');template=doc.addObject('TechDraw::DrawSVGTemplate','DesignDetailTemplate')
    resources=Path(App.getResourceDir())/'Mod/TechDraw/Templates';template.Template=str(sorted(resources.glob('*.svg'))[0]);page.Template=template
    infra_detail=[o for o in infra_features if o.InstanceId in ('infra/seat-1-1','infra/bearing-1--1','infra/jack-1--1--0.3','infra/jack-1--1-0.3')]
    for name,objects,direction,x,y,scale in [('CarDesignPlan',added,(0,0,1),148.,150.,.013),
            ('CarDesignElevation',added,(0,-1,0),148.,100.,.013),('RailSeatAndBearingPlan',infra_detail,(0,0,1),148.,50.,.08)]:
        view=doc.addObject('TechDraw::DrawViewPart',name);view.Source=objects;view.Direction=App.Vector(*direction)
        view.X=x;view.Y=y;view.Scale=scale;page.addView(view)
    page.addProperty('App::PropertyBool','DrawingIssued','OSR Study');page.DrawingIssued=False
    doc.recompute();edges={name:len(doc.getObject(name).getVisibleEdges()) for name in ('CarDesignPlan','CarDesignElevation','RailSeatAndBearingPlan')}
    if any(v==0 for v in edges.values()):raise ValueError('design drawing projection empty')
    Part.export(added+infra_features,str(output.with_suffix('.step')))
    doc.saveAs(str(output.resolve()));App.closeDocument(doc.Name);_canonicalise_fcstd(output)
    doc=App.openDocument(str(output.resolve()));train={o.InstanceId:o for o in doc.Objects if 'InstanceId' in o.PropertiesList and not o.InstanceId.startswith('infra/')}
    solver=doc.TrainAssembly.solve();doc.recompute()
    if solver != 0:raise ValueError('restored native assembly did not solve')
    checks=[]
    for row in features:
        feature=train[row['instance_id']];spec=row['geometry'];expected=sum(primitive_volume(p) for p in spec['primitives'])*1e9
        error=abs(feature.Shape.Volume/expected-1)
        if not feature.Shape.isValid() or error>1e-8:raise ValueError('saved native design solid differs')
        p=next(r['transform']['translation_m'] for r in model['instances'] if r['id']==row['instance_id'])
        delta=(feature.Placement.Base-App.Vector(*(v*1000 for v in p))).Length
        if delta>1e-5:raise ValueError('saved study placement differs')
        checks.append(dict(instance_id=row['instance_id'],solid_count=len(feature.Shape.Solids),volume_error=error,placement_error_mm=delta))
    infra_objects={o.InstanceId:o for o in doc.InfrastructureStudy.Group}
    for row in infra['items']:
        feature=infra_objects[row['id']];expected=sum(primitive_volume(p) for p in row['geometry']['primitives'])*1e9
        if not feature.Shape.isValid() or abs(feature.Shape.Volume/expected-1)>1e-8:
            raise ValueError('saved infrastructure solid differs')
    # Independent OCC integrals and occupied-volume checks for each unique study design.
    integral_checks=0;inertia_errors=[];internal_collisions=[];seen_specs=set()
    for row in features+infra['items']:
        spec=row['geometry'];key=fingerprint(spec)
        if key in seen_specs:continue
        seen_specs.add(key);solids=[]
        for p in spec['primitives']:
            solid=native_shape(dict(role='integral-audit',primitives=[p]),Part,App).Solids[0]
            expected=primitive_inertia(p,1.);matrix=solid.MatrixOfInertia
            actual=np.array([[getattr(matrix,f'A{i+1}{j+1}') for j in range(3)] for i in range(3)])/solid.Volume/1e6
            error=float(np.linalg.norm(actual-expected)/np.linalg.norm(expected));inertia_errors.append(error)
            if error>1e-8:raise ValueError('native study primitive inertia differs')
            integral_checks+=1;solids.append((p,solid))
        for i,(a,sa) in enumerate(solids):
            for b,sb in solids[i+1:]:
                if sa.BoundBox.intersect(sb.BoundBox):
                    volume=sa.common(sb).Volume
                    if volume>1e-3:internal_collisions.append(dict(role=spec['role'],left=a['id'],right=b['id'],intersection_mm3=volume))
    # Check actual occupied solids across declared design envelopes; the old body is an unresolved context envelope.
    collisions=[];selected=[train[r['instance_id']] for r in features if r['instance_id'].startswith('car-1/')]
    for i,a in enumerate(selected):
        for b in selected[i+1:]:
            if a.Shape.BoundBox.intersect(b.Shape.BoundBox):
                volume=a.Shape.common(b.Shape).Volume
                if volume>1e-3:collisions.append(dict(left=a.InstanceId,right=b.InstanceId,intersection_mm3=volume))
    # STEP is independently read back; its geometry must retain the exported occupied volume.
    step_shape=Part.Shape();step_shape.read(str(output.with_suffix('.step')))
    expected_step_volume=sum(o.Shape.Volume for o in selected)+sum(o.Shape.Volume for o in doc.InfrastructureStudy.Group)
    step_error=abs(step_shape.Volume/expected_step_volume-1)
    if not step_shape.isValid() or step_error>1e-8:raise ValueError('STEP round trip geometry differs')
    result=dict(schema='osr-native-best-practice-design-twin/1',configuration_sha256=fingerprint(model),
        compiler_review_sha256=hashlib.sha256((package/'review.json').read_bytes()).hexdigest(),
        generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),freecad_version=list(App.Version()),
        native_train_instance_count=len(train),new_train_design_instance_count=len(checks),
        infrastructure_instance_count=len(infra['items']),native_solver_result=initial['native_solver_result'],reopened_solver_result=solver,
        joints=initial['joints'],infrastructure_display_offset_m=[0.,5.,0.],
        drawing_edges=edges,design_solids=checks,new_car_component_collisions=collisions,
        intra_component_collisions=internal_collisions,independent_occ_integral_checks=integral_checks,
        maximum_relative_primitive_inertia_error=max(inertia_errors),
        context_body_fit_qualified=False,step_roundtrip_relative_volume_error=step_error,
        fcstd_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),step_sha256=hashlib.sha256(output.with_suffix('.step').read_bytes()).hexdigest(),
        drawing_issued=False,production_released=False,physical_validation=False)
    App.closeDocument(doc.Name)
    output.with_suffix('.native.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    if collisions or internal_collisions:raise ValueError('new design components collide; review native receipt')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--package',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--native',action='store_true');args=parser.parse_args()
    if args.native:native(args.package,args.output);return
    subprocess.run([sys.executable,str(ROOT/'tools/automation/design-best-practice-twin.py'),'verify','--output',str(args.package)],check=True)
    if args.output.exists():raise ValueError('use a fresh native output path')
    runtime=shutil.which('FreeCADCmd') or shutil.which('freecadcmd')
    command=[runtime] if runtime else ['flatpak','run','--filesystem='+str(ROOT),'--command=FreeCADCmd','org.freecad.FreeCAD']
    with tempfile.TemporaryDirectory(prefix='design-twin-',dir=ROOT/'build') as folder:
        script=Path(folder)/'run.py';ok=Path(folder)/'ok'
        argv=[str(Path(__file__).resolve()),'--native','--package',str(args.package.resolve()),'--output',str(args.output.resolve())]
        script.write_text('import runpy,sys,traceback\nfrom pathlib import Path\nsys.argv='+repr(argv)+'\ntry:\n    runpy.run_path(sys.argv[0],run_name="__main__")\n    Path('+repr(str(ok))+').write_text("ok")\nexcept Exception:\n    traceback.print_exc()\n    raise SystemExit(1)\n')
        subprocess.run(command+[str(script)],check=True)
        if not ok.exists():raise RuntimeError('native design generation failed; inspect traceback')
    if not args.output.with_suffix('.native.json').exists():raise RuntimeError('native receipt missing')
    print(args.output)


if __name__=='__main__':main()
