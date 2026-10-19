"""IFC4/IDS information exchange of retained native solids; no design authority.

Coordinates are tessellated native CAD in metres. IDS verifies information only,
never engineering performance, geotechnical suitability or physical acceptance.
"""
from pathlib import Path
import json
import math
import shutil
import subprocess
import uuid

from engineering.twin_workflow import core

PSET='OSR_DesignIdentity'


def global_id(identity,namespace=''):
    import ifcopenshell.guid
    return ifcopenshell.guid.compress(uuid.uuid5(uuid.NAMESPACE_URL,'https://opensource.rail/physical/'+namespace+'/'+identity).hex)


def _namespace(candidate):
    return candidate.get('metadata',{}).get('architecture','baghdad-six-car')+'/'+candidate['kind']


def _properties(candidate,part):
    role=part.get('geometric_role','manufactured-solid')
    ownership='purchased-envelope' if role=='supplier-coordination-envelope' else 'hardware-envelope' if role=='hardware-envelope' else 'owned'
    return dict(PhysicalPartId=part['id'],CandidateRevision=candidate['revision'],PartRevision=part['revision'],
        Material=part['material'],Ownership=ownership,Process=part.get('process_route','unspecified; hold'),
        QAState='unexecuted; acceptance open',InterfaceIds=json.dumps(part.get('joints',[]),sort_keys=True),
        StandardsState='licensed edition/category/project adoption open',
        Architecture=candidate.get('metadata',{}).get('architecture','baghdad-six-car'))


def specification(candidate):
    from ifctester import ids
    document=ids.Ids(title='OSR revision-bound assembly information',version='1.0',
        description='Information-only IDS; no structural or manufacturing acceptance')
    for part in candidate['contract']['parts']:
        spec=ids.Specification(name=part['id'],minOccurs=1,maxOccurs=1,ifcVersion=['IFC4'])
        spec.applicability.append(ids.Entity(name='IFCBUILDINGELEMENTPROXY'))
        spec.applicability.append(ids.Attribute(name='GlobalId',value=global_id(part['id'],_namespace(candidate))))
        spec.requirements.append(ids.Attribute(name='Name',value=part['id']))
        spec.requirements.append(ids.Material(value=part['material']))
        for key,value in _properties(candidate,part).items():
            spec.requirements.append(ids.Property(propertySet=PSET,baseName=key,value=str(value),dataType='IFCLABEL'))
        document.specifications.append(spec)
    return document


def verify(candidate, path, *, ids_path=None):
    import ifcopenshell
    from ifctester import ids
    model=ifcopenshell.open(str(path));products=model.by_type('IfcBuildingElementProxy')
    expected={p['id'] for p in candidate['contract']['parts']}
    names=[p.Name for p in products]
    identity_ok=len(names)==len(expected) and set(names)==expected and all(p.GlobalId==global_id(p.Name,_namespace(candidate)) for p in products)
    document=specification(candidate)
    if ids_path:
        # Execute retained IDS as well as freshly derived exact-revision criteria.
        retained=ids.open(str(ids_path));retained.validate(model)
        retained_ok=all(s.status for s in retained.specifications)
    else:retained_ok=True
    document.validate(model)
    rows=[dict(id=s.name,passed=bool(s.status),failed_entities=[getattr(p,'Name',str(p)) for p in s.failed_entities]) for s in document.specifications]
    passed=identity_ok and retained_ok and all(row['passed'] for row in rows)
    return dict(schema='osr-ifc-ids-verification/1',state='information-pass' if passed else 'failed',
        identity_match=identity_ok,retained_ids_pass=retained_ok,specifications=rows,
        candidate_revision=candidate['revision'],engineering_performance_verified=False,**core.FLAGS)


def _native_mesh(cad,output):
    source=core.ROOT/'engineering/design_delivery/visuals.py';mesh=output/'native-mesh.json';script=output/'tessellate.py'
    script.write_text('import runpy\nrunpy.run_path('+repr(str(source))+')["export_mesh"]('+repr(str(cad))+','+repr(str(mesh))+')\n')
    binary=shutil.which('FreeCADCmd') or shutil.which('freecadcmd')
    command=[binary] if binary else ['flatpak','run','--filesystem='+str(cad.parent),'--filesystem='+str(output.resolve()),
        '--filesystem='+str(source.parent),'--command=FreeCADCmd','org.freecad.FreeCAD']
    with (output/'tessellate.log').open('w') as stream:
        subprocess.run([*command,str(script)],stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=120)
    return core.read(mesh,maximum=60_000_000)


def export(candidate,cad,output,*,meshdata=None):
    import ifcopenshell
    output=Path(output);output.mkdir(parents=True,exist_ok=True);cad=Path(cad).resolve() if cad else None
    for name in ('assembly.ifc','requirements.ids','receipt.json'):
        if (output/name).exists():raise ValueError('IFC export outputs already exist')
    before=core.sha(cad) if cad else None
    supplied_mesh=meshdata is not None
    if not supplied_mesh and cad:
        proof=core.read(cad.parent/'native-cad.json',maximum=10_000_000)
        if proof.get('input_sha256')!=core.digest(candidate['contract']) or proof.get('files_sha256',{}).get(cad.name)!=before:
            raise ValueError('native CAD receipt differs from exact candidate contract/revision')
    if meshdata is None:
        if cad is None:raise ValueError('retained native CAD required')
        meshdata=_native_mesh(cad,output)
    if cad and core.sha(cad)!=before:raise ValueError('native CAD changed during IFC tessellation')
    parts={p['id']:p for p in candidate['contract']['parts']};meshes=meshdata['parts']
    if len(meshes)!=len(parts) or {p['id'] for p in meshes}!=set(parts):raise ValueError('IFC native part identity mismatch')
    model=ifcopenshell.file(schema='IFC4')
    origin=model.create_entity('IfcCartesianPoint',Coordinates=(0.,0.,0.))
    axis=model.create_entity('IfcAxis2Placement3D',Location=origin)
    context=model.create_entity('IfcGeometricRepresentationContext',ContextIdentifier='Model',ContextType='Model',
        CoordinateSpaceDimension=3,Precision=1e-7,WorldCoordinateSystem=axis)
    metre=model.create_entity('IfcSIUnit',UnitType='LENGTHUNIT',Name='METRE')
    units=model.create_entity('IfcUnitAssignment',Units=[metre])
    project=model.create_entity('IfcProject',GlobalId=global_id('project/'+candidate['revision']),Name='OSR provisional assembly information',
        RepresentationContexts=[context],UnitsInContext=units)
    products=[]
    for mesh in meshes:
        part=parts[mesh['id']];vertices=mesh['vertices'];faces=mesh['faces']
        if not vertices or not faces or any(len(v)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in v) for v in vertices):raise ValueError('invalid native mesh coordinates')
        if any(len(f)!=3 or any(type(i) is not int or i<0 or i>=len(vertices) for i in f) for f in faces):raise ValueError('invalid native mesh faces')
        if len(faces)>250000:raise ValueError('IFC mesh triangle budget exceeded')
        points=model.create_entity('IfcCartesianPointList3D',CoordList=[tuple(float(x) for x in v) for v in vertices])
        tessellation=model.create_entity('IfcTriangulatedFaceSet',Coordinates=points,Closed=None,
            CoordIndex=[tuple(i+1 for i in f) for f in faces])
        representation=model.create_entity('IfcShapeRepresentation',ContextOfItems=context,RepresentationIdentifier='Body',
            RepresentationType='Tessellation',Items=[tessellation])
        shape=model.create_entity('IfcProductDefinitionShape',Representations=[representation])
        placement=model.create_entity('IfcLocalPlacement',RelativePlacement=axis)
        product=model.create_entity('IfcBuildingElementProxy',GlobalId=global_id(part['id'],_namespace(candidate)),Name=part['id'],
            ObjectPlacement=placement,Representation=shape,Description='Exchange mesh of retained native geometry; source CAD is authority')
        props=[model.create_entity('IfcPropertySingleValue',Name=key,NominalValue=model.create_entity('IfcLabel',str(value))) for key,value in _properties(candidate,part).items()]
        pset=model.create_entity('IfcPropertySet',GlobalId=global_id(candidate['revision']+'/'+part['id']+'/properties'),Name=PSET,HasProperties=props)
        model.create_entity('IfcRelDefinesByProperties',GlobalId=ifcopenshell.guid.new(),RelatedObjects=[product],RelatingPropertyDefinition=pset)
        material=model.create_entity('IfcMaterial',Name=part['material'])
        model.create_entity('IfcRelAssociatesMaterial',GlobalId=ifcopenshell.guid.new(),RelatedObjects=[product],RelatingMaterial=material)
        products.append(product)
    model.create_entity('IfcRelAggregates',GlobalId=ifcopenshell.guid.new(),RelatingObject=project,RelatedObjects=products)
    path=output/'assembly.ifc';model.write(str(path));document=specification(candidate);document.to_xml(str(output/'requirements.ids'))
    check=verify(candidate,path,ids_path=output/'requirements.ids')
    if check['state']!='information-pass':raise ValueError('exported IFC fails exact-revision IDS')
    core.write(output/'ids-report.json',check)
    receipt=dict(schema='osr-native-ifc-exchange/1',state='information-only',candidate_revision=candidate['revision'],
        source_cad_sha256=before,mesh_basis='supplied fixture mesh; no native correspondence claim' if supplied_mesh else 'retained native CAD tessellation',
        ifc_version='IFC4',ifcopenshell_version=ifcopenshell.version,part_count=len(products),
        ids_verified=True,source_geometry_authority='candidate contract + retained FreeCAD',
        files_sha256={p.name:core.sha(p) for p in output.iterdir() if p.is_file()},**core.FLAGS)
    core.write(output/'receipt.json',receipt)
    return receipt
