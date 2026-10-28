"""Actual IFC and bounded native CAD for component occurrences.

An envelope is exported as an envelope, never as a calculated installed mass.
Round-trip geometry checks do not qualify joints, clearances or a vehicle.
"""
from pathlib import Path
from math import isclose, pi
import json
import os
import shutil
import subprocess
import tempfile
import resource
from itertools import product as cartesian_product

import numpy as np

from engineering.station_rail.common import identity, digest, encoded
from engineering.component_registry import validate_registry, geometry_properties
from .vehicles import FLAGS

PRODUCER='engineering/reference_cell/geometry.py'


def _validate(vehicle):
    validate_registry(vehicle['registry'])
    if (vehicle['candidate_id']!=vehicle['registry']['candidate_id'] or
        vehicle.get('evaluation_id')!=identity({k:v for k,v in vehicle.items() if k!='evaluation_id'}) or
        any(vehicle.get(k) is not False for k in FLAGS)):
        raise ValueError('Exact unaccepted vehicle/registry identity required')
    return vehicle['registry']


def _source(vehicle):
    return {**vehicle.get('source_sha256',{}),PRODUCER:digest(__file__),
        'engineering/railway_twin/geometry.py':digest(Path(__file__).resolve().parents[2]/'engineering/railway_twin/geometry.py')}


def _file(vehicle, output):
    path=Path(output)
    return path if path.suffix.lower()=='.ifc' else path/(vehicle['vehicle_id']+'.ifc')


def _ordinary(path):
    if path.is_symlink() or any(p.is_symlink() for p in path.parents):
        raise ValueError('Ordinary geometry paths required')


def _guid(value):
    import ifcopenshell.guid
    return ifcopenshell.guid.compress(identity(value)[:32])


def _pset(file, name, values):
    properties=[]
    for key,value in values.items():
        properties.append(file.create_entity('IfcPropertySingleValue',Name=key,
            NominalValue=file.create_entity('IfcText',str(value))))
    return file.create_entity('IfcPropertySet',GlobalId=_guid(dict(name=name,values=values)),Name=name,HasProperties=properties)


def export_ifc(vehicle, output):
    """Write all six-car occurrences with reused, typed primitive definitions."""
    import ifcopenshell
    registry=_validate(vehicle);path=_file(vehicle,output);_ordinary(path)
    if path.exists():raise ValueError('Fresh immutable IFC output required')
    path.parent.mkdir(parents=True,exist_ok=True)
    f=ifcopenshell.file(schema='IFC4')
    origin=f.create_entity('IfcCartesianPoint',Coordinates=(0.,0.,0.))
    axis=f.create_entity('IfcAxis2Placement3D',Location=origin)
    context=f.create_entity('IfcGeometricRepresentationContext',ContextIdentifier='Model',ContextType='Model',
        CoordinateSpaceDimension=3,Precision=1e-8,WorldCoordinateSystem=axis)
    units=f.create_entity('IfcUnitAssignment',Units=[f.create_entity('IfcSIUnit',UnitType='LENGTHUNIT',Name='METRE')])
    project=f.create_entity('IfcProject',GlobalId=_guid(['project',vehicle['candidate_id']]),Name=vehicle['vehicle_id'],
        RepresentationContexts=[context],UnitsInContext=units)
    site=f.create_entity('IfcSite',GlobalId=_guid(['site',vehicle['candidate_id']]),Name='Unsurveyed research train')
    f.create_entity('IfcRelAggregates',GlobalId=_guid(['project-site',vehicle['candidate_id']]),RelatingObject=project,RelatedObjects=[site])
    candidate=_pset(f,'OSR_Candidate',dict(candidate_id=vehicle['candidate_id'],registry_id=registry['registry_id'],
        scope='Research nominal primitives and purchased bounding envelopes',physical_accepted=False,
        manufacturing_release=False,complete_installed_geometry=False))
    f.create_entity('IfcRelDefinesByProperties',GlobalId=_guid(['candidate-properties',vehicle['candidate_id']]),RelatedObjects=[site],RelatingPropertyDefinition=candidate)
    mats={m['material_id']:m for m in registry['materials']}
    types={};rows={}
    for part in registry['parts']:
        pid=part['physical_definition_id'];g=part['geometry'];d=g['dimensions_m']
        if g['kind'] in ('box','envelope'):
            profile=f.create_entity('IfcRectangleProfileDef',ProfileType='AREA',XDim=float(d[0]),YDim=float(d[1]));length=d[2]
        elif g['kind']=='cylinder':
            profile=f.create_entity('IfcCircleProfileDef',ProfileType='AREA',Radius=float(d['radius']));length=d['length']
        elif g['kind']=='tube':
            profile=f.create_entity('IfcCircleHollowProfileDef',ProfileType='AREA',Radius=float(d['outer_radius']),
                WallThickness=float(d['outer_radius']-d['inner_radius']));length=d['length']
        else:raise ValueError('Explicit supported net primitive or purchased envelope required')
        start=f.create_entity('IfcAxis2Placement3D',Location=f.create_entity('IfcCartesianPoint',Coordinates=(0.,0.,-float(length)/2)))
        solid=f.create_entity('IfcExtrudedAreaSolid',SweptArea=profile,Position=start,
            ExtrudedDirection=f.create_entity('IfcDirection',DirectionRatios=(0.,0.,1.)),Depth=float(length))
        representation=f.create_entity('IfcShapeRepresentation',ContextOfItems=context,RepresentationIdentifier='Body',RepresentationType='SweptSolid',Items=[solid])
        mapped=f.create_entity('IfcRepresentationMap',MappingOrigin=axis,MappedRepresentation=representation)
        properties=_pset(f,'OSR_Part',dict(part_id=part['part_id'],physical_definition_id=pid,
            revision_id=part['revision_id'],material_id=part['material_id'],
            material_evaluation_id=part.get('material_evaluation_id'),geometry_kind=g['kind'],
            net_volume_m3=g['net_volume_m3'],envelope_is_installed_mass=False))
        typ=f.create_entity('IfcBuildingElementProxyType',GlobalId=_guid(['part-type',vehicle['candidate_id'],pid]),
            Name=part['part_id'],HasPropertySets=[properties],RepresentationMaps=[mapped],PredefinedType='NOTDEFINED')
        if part['material_id'] is not None:
            material=f.create_entity('IfcMaterial',Name=mats[part['material_id']]['grade_id'])
            f.create_entity('IfcRelAssociatesMaterial',GlobalId=_guid(['material',vehicle['candidate_id'],pid]),RelatedObjects=[typ],RelatingMaterial=material)
        types[pid]=(typ,mapped);rows[pid]=[]
    products=[]
    for occurrence in registry['occurrences']:
        matrix=occurrence['transform'];pid=occurrence['part_definition_id'];typ,mapped=types[pid]
        place=f.create_entity('IfcAxis2Placement3D',Location=f.create_entity('IfcCartesianPoint',Coordinates=tuple(float(matrix[i][3]) for i in range(3))),
            Axis=f.create_entity('IfcDirection',DirectionRatios=tuple(float(matrix[i][2]) for i in range(3))),
            RefDirection=f.create_entity('IfcDirection',DirectionRatios=tuple(float(matrix[i][0]) for i in range(3))))
        placement=f.create_entity('IfcLocalPlacement',RelativePlacement=place)
        target=f.create_entity('IfcCartesianTransformationOperator3D',LocalOrigin=origin,Scale=1.)
        item=f.create_entity('IfcMappedItem',MappingSource=mapped,MappingTarget=target)
        representation=f.create_entity('IfcShapeRepresentation',ContextOfItems=context,RepresentationIdentifier='Body',RepresentationType='MappedRepresentation',Items=[item])
        product=f.create_entity('IfcBuildingElementProxy',GlobalId=_guid(['occurrence',vehicle['candidate_id'],occurrence['occurrence_id']]),
            Name=typ.Name,ObjectType=occurrence['scope'],ObjectPlacement=placement,
            Representation=f.create_entity('IfcProductDefinitionShape',Representations=[representation]),
            Tag=occurrence['occurrence_id'],PredefinedType='NOTDEFINED')
        products.append(product);rows[pid].append(product)
    for pid,(typ,_) in types.items():
        f.create_entity('IfcRelDefinesByType',GlobalId=_guid(['type-relation',vehicle['candidate_id'],pid]),RelatedObjects=rows[pid],RelatingType=typ)
    f.create_entity('IfcRelContainedInSpatialStructure',GlobalId=_guid(['site-products',vehicle['candidate_id']]),RelatedElements=products,RelatingStructure=site)
    f.header.file_name.name=path.name;f.header.file_name.time_stamp='1970-01-01T00:00:00'
    f.write(str(path))
    reopened=_inspect_ifc(vehicle,path)
    receipt=dict(schema='osr-reference-cell-ifc/1',candidate_id=vehicle['candidate_id'],registry_id=registry['registry_id'],
        source_sha256=_source(vehicle),file=path.name,file_sha256=digest(path),ifcopenshell_version=ifcopenshell.version,
        reopened=reopened,complete_installed_geometry=False,**FLAGS)
    receipt['receipt_id']=identity(receipt)
    path.with_suffix('.ifc.receipt.json').write_bytes(encoded(receipt));return receipt


def _values(pset):
    return {p.Name:p.NominalValue.wrappedValue for p in pset.HasProperties}


def _mesh_volume(vertices,faces):
    v=np.asarray(vertices,dtype=float).reshape(-1,3);t=np.asarray(faces,dtype=int).reshape(-1,3)
    return abs(float(np.einsum('ij,ij->',v[t[:,0]],np.cross(v[t[:,1]],v[t[:,2]]))/6))


def _inspect_ifc(vehicle,path):
    import ifcopenshell
    import ifcopenshell.geom
    import ifcopenshell.util.placement
    registry=_validate(vehicle);f=ifcopenshell.open(str(path))
    if f.schema!='IFC4':raise ValueError('Explicit metre-based IFC4 required')
    projects=f.by_type('IfcProject')
    if len(projects)!=1 or len(projects[0].UnitsInContext.Units)!=1:
        raise ValueError('One explicit length unit required')
    unit=projects[0].UnitsInContext.Units[0]
    if unit.UnitType!='LENGTHUNIT' or unit.Name!='METRE' or unit.Prefix is not None:raise ValueError('IFC length scaling differs')
    candidate=[p for p in f.by_type('IfcPropertySet') if p.Name=='OSR_Candidate']
    if len(candidate)!=1 or _values(candidate[0]).get('candidate_id')!=vehicle['candidate_id'] or _values(candidate[0]).get('registry_id')!=registry['registry_id']:
        raise ValueError('IFC physical candidate/registry differs')
    for key in ('physical_accepted','manufacturing_release','complete_installed_geometry'):
        if _values(candidate[0]).get(key)!='False':raise ValueError('IFC cannot promote acceptance')
    expected={p['physical_definition_id']:p for p in registry['parts']};types={};linked={}
    material={r.RelatedObjects[0].id():r.RelatingMaterial.Name for r in f.by_type('IfcRelAssociatesMaterial')}
    mats={m['material_id']:m for m in registry['materials']}
    for relation in f.by_type('IfcRelDefinesByType'):
        typ=relation.RelatingType;psets=[p for p in typ.HasPropertySets if p.Name=='OSR_Part']
        if len(psets)!=1:raise ValueError('One canonical type definition required')
        values=_values(psets[0]);pid=values.get('physical_definition_id');part=expected.get(pid)
        if part is None or pid in types or values!=dict(part_id=part['part_id'],physical_definition_id=pid,
            revision_id=part['revision_id'],material_id=str(part['material_id']),material_evaluation_id=str(part.get('material_evaluation_id')),
            geometry_kind=part['geometry']['kind'],net_volume_m3=str(part['geometry']['net_volume_m3']),envelope_is_installed_mass='False'):
            raise ValueError('IFC part revision/material/geometry identity differs')
        actual_material=material.get(typ.id())
        expected_material=None if part['material_id'] is None else mats[part['material_id']]['grade_id']
        if actual_material!=expected_material:raise ValueError('IFC material association differs')
        types[pid]=typ
        for product in relation.RelatedObjects:
            if product.id() in linked:raise ValueError('Multiple physical part types on one occurrence')
            linked[product.id()]=pid
    products=f.by_type('IfcBuildingElementProxy');actual={p.Tag:p for p in products}
    if len(actual)!=len(products) or set(actual)!={o['occurrence_id'] for o in registry['occurrences']} or set(types)!=set(expected):
        raise ValueError('IFC part/physical occurrence inventory differs')
    first={}
    for occurrence in registry['occurrences']:
        product=actual[occurrence['occurrence_id']];pid=occurrence['part_definition_id']
        if linked.get(product.id())!=pid or product.ObjectType!=occurrence['scope']:
            raise ValueError('IFC occurrence/part/scope differs')
        placement=ifcopenshell.util.placement.get_local_placement(product.ObjectPlacement)
        if not np.allclose(placement,occurrence['transform'],rtol=0.,atol=1e-9):raise ValueError('Actual IFC rigid placement differs')
        items=product.Representation.Representations[0].Items
        if len(items)!=1 or not items[0].is_a('IfcMappedItem') or items[0].MappingSource!=types[pid].RepresentationMaps[0]:
            raise ValueError('IFC uses another mapped physical shape')
        if not np.allclose(ifcopenshell.util.placement.get_mappeditem_transformation(items[0]),np.eye(4),rtol=0.,atol=1e-12):
            raise ValueError('IFC shape mapping modifies the declared solid')
        first.setdefault(pid,product)
    settings=ifcopenshell.geom.settings();settings.set('mesher-linear-deflection',1e-6);settings.set('mesher-angular-deflection',.1)
    errors=[];known_volume=envelope_volume=0.
    for pid,product in first.items():
        part=expected[pid];g=part['geometry'];properties=geometry_properties(g)
        shape=ifcopenshell.geom.create_shape(settings,product)
        volume=_mesh_volume(shape.geometry.verts,shape.geometry.faces)
        d=properties['envelope_dimensions_m'];expected_volume=float(np.prod(d)) if g['kind']=='envelope' else properties['volume_m3']
        tolerance=.002 if g['kind'] in ('cylinder','tube') else 1e-7
        if not isclose(volume,expected_volume,rel_tol=tolerance,abs_tol=1e-11):raise ValueError('Reopened IFC primitive volume differs')
        vertices=np.asarray(shape.geometry.verts).reshape(-1,3)
        if not np.allclose(vertices.min(axis=0),-np.asarray(d)/2,rtol=0.,atol=2e-6) or not np.allclose(vertices.max(axis=0),np.asarray(d)/2,rtol=0.,atol=2e-6):
            raise ValueError('Reopened IFC local bounds/centroid differ')
        count=sum(o['part_definition_id']==pid for o in registry['occurrences'])
        if g['kind']=='envelope':envelope_volume+=expected_volume*count
        else:known_volume+=expected_volume*count
        errors.append(abs(volume-expected_volume)/expected_volume)
    return dict(physical_occurrences=len(products),unique_part_shapes=len(first),
        nominal_net_stock_volume_m3=known_volume,purchased_bounding_volume_m3=envelope_volume,
        purchased_bounding_volume_is_material_or_mass=False,maximum_mesh_relative_volume_error=max(errors),
        placement_check='Every occurrence rigid transform and shared representation inspected',
        current_verifier_ifcopenshell_version=ifcopenshell.version,complete_installed_geometry=False,**FLAGS)


def verify_ifc(vehicle,output):
    path=_file(vehicle,output);receipt_path=path.with_suffix('.ifc.receipt.json')
    _ordinary(path);_ordinary(receipt_path)
    if path.stat().st_size>512*1024**2:raise ValueError('Bounded IFC file required')
    receipt=json.loads(receipt_path.read_bytes())
    if (receipt.get('schema')!='osr-reference-cell-ifc/1' or receipt.get('receipt_id')!=identity({k:v for k,v in receipt.items() if k!='receipt_id'})
        or receipt.get('candidate_id')!=vehicle['candidate_id'] or receipt.get('registry_id')!=vehicle['registry']['registry_id']
        or receipt.get('source_sha256')!=_source(vehicle) or receipt.get('file')!=path.name or receipt.get('file_sha256')!=digest(path)
        or receipt.get('complete_installed_geometry') is not False or any(receipt.get(k) is not False for k in FLAGS)):
        raise ValueError('IFC source, payload, identity or disposition differs')
    actual=_inspect_ifc(vehicle,path)
    old=receipt['reopened'].copy();new=actual.copy();old.pop('current_verifier_ifcopenshell_version');new.pop('current_verifier_ifcopenshell_version')
    previous_error=old.pop('maximum_mesh_relative_volume_error');current_error=new.pop('maximum_mesh_relative_volume_error')
    if not isclose(previous_error,current_error,rel_tol=1e-6,abs_tol=1e-9):raise ValueError('Reopened IFC mesh diagnostic differs')
    if old!=new:raise ValueError('Actual reopened IFC geometry differs from receipt')
    return dict(verified=True,candidate_id=vehicle['candidate_id'],receipt_id=receipt['receipt_id'],
        actual_reopened=True,native_reuse_eligible=False,**actual)


_NATIVE_SCRIPT=r'''
import os,json,resource
import FreeCAD as App, Part
FOLDER=globals().get('FOLDER',os.getcwd())
VERIFY_ONLY=globals().get('VERIFY_ONLY',False)
data=json.load(open(os.path.join(FOLDER,'native-input.json')))
def details(shape):
    b=shape.BoundBox;c=shape.CenterOfMass
    return dict(volume_m3=shape.Volume/1e9,centroid_m=[c.x/1000,c.y/1000,c.z/1000],
        bounds_min_m=[b.XMin/1000,b.YMin/1000,b.ZMin/1000],bounds_max_m=[b.XMax/1000,b.YMax/1000,b.ZMax/1000])
if not VERIFY_ONLY:
    doc=App.newDocument('ReferenceCell');shapes={}
    for item in data['items']:
        g=item['geometry'];d=g['dimensions_m'];key=item['part_definition_id']
        if key not in shapes:
            if g['kind'] in ('box','envelope'):
                shape=Part.makeBox(d[0]*1000,d[1]*1000,d[2]*1000,App.Vector(-d[0]*500,-d[1]*500,-d[2]*500))
            else:
                r=d.get('outer_radius',d.get('radius'));length=d['length']*1000
                shape=Part.makeCylinder(r*1000,length,App.Vector(0,0,-length/2))
                if g['kind']=='tube':shape=shape.cut(Part.makeCylinder(d['inner_radius']*1000,length,App.Vector(0,0,-length/2)))
            if shape.isNull() or not shape.isValid():raise ValueError('Invalid native primitive')
            shapes[key]=shape
        obj=doc.addObject('PartDesign::Feature','P'+str(len(doc.Objects)))
        obj.Shape=shapes[key].copy();m=[list(row) for row in item['transform']]
        for i in range(3):m[i][3]*=1000
        obj.Placement=App.Placement(App.Matrix(*[x for row in m for x in row]))
        for name,value in (('OccurrenceId',item['occurrence_id']),('PartDefinitionId',key),
            ('PartRevisionId',item['part_revision_id']),('GeometryScope',g['kind'])):
            obj.addProperty('App::PropertyString',name);setattr(obj,name,value)
    doc.recompute();doc.saveAs(os.path.join(FOLDER,'vehicle.FCStd'))
    Part.export(list(doc.Objects),os.path.join(FOLDER,'vehicle.step'));App.closeDocument(doc.Name)
doc=App.openDocument(os.path.join(FOLDER,'vehicle.FCStd'))
rows=[]
for obj in doc.Objects:
    if hasattr(obj,'Shape') and not obj.Shape.isNull():
        row=details(obj.Shape);row.update(occurrence_id=obj.OccurrenceId,part_definition_id=obj.PartDefinitionId,
            part_revision_id=obj.PartRevisionId,geometry_kind=obj.GeometryScope);rows.append(row)
App.closeDocument(doc.Name)
step=Part.read(os.path.join(FOLDER,'vehicle.step'))
result=dict(candidate_id=data['candidate_id'],cars=data['cars'],FreeCAD_version=list(App.Version()),
    enforced_address_space_limit_bytes=resource.getrlimit(resource.RLIMIT_AS)[0],
    FCStd_occurrences=rows,STEP_solids=[details(s) for s in step.Solids],complete_installed_geometry=False,
    physical_accepted=False,manufacturing_release=False)
output=globals().get('OUTPUT',os.path.join(FOLDER,'native-result.json'))
with open(output,'w') as stream:json.dump(result,stream,sort_keys=True,allow_nan=False)
'''


def _native_items(vehicle,cars):
    registry=_validate(vehicle)
    if not isinstance(cars,(list,tuple)) or not cars or len(set(cars))!=len(cars) or any(type(n) is not int or not 1<=n<=6 for n in cars):
        raise ValueError('Explicit unique car numbers one to six required')
    parts={p['physical_definition_id']:p for p in registry['parts']};items=[]
    for occurrence in registry['occurrences']:
        if not any(occurrence['occurrence_id'].startswith('car-'+str(n)+'/') for n in cars):continue
        part=parts[occurrence['part_definition_id']]
        items.append(dict(occurrence_id=occurrence['occurrence_id'],part_definition_id=part['physical_definition_id'],
            part_revision_id=part['revision_id'],geometry=part['geometry'],transform=occurrence['transform']))
    if not items:raise ValueError('Selected cars have no physical occurrences')
    return items


def _native_command(script):
    # The retained helper only discovers an installed command. No retained
    # source is edited and no old numerical/CAD receipt is inherited.
    from engineering.railway_twin.geometry import _native_command as discover
    return discover(script)


def _run_native(command,folder,timeout_s,memory_bytes):
    def limit():resource.setrlimit(resource.RLIMIT_AS,(memory_bytes,memory_bytes))
    return subprocess.run(command,cwd=folder,capture_output=True,timeout=timeout_s,preexec_fn=limit,
        env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','QT_QPA_PLATFORM':'offscreen'})


def _check_native(items,result,candidate_id,cars,memory_bytes):
    if (result.get('candidate_id')!=candidate_id or result.get('cars')!=list(cars)
        or result.get('enforced_address_space_limit_bytes')!=memory_bytes or result.get('physical_accepted') is not False
        or result.get('manufacturing_release') is not False or result.get('complete_installed_geometry') is not False):
        raise ValueError('Native physical scope or actual resource contract differs')
    actual={r['occurrence_id']:r for r in result['FCStd_occurrences']}
    if len(actual)!=len(items) or set(actual)!={p['occurrence_id'] for p in items}:
        raise ValueError('Reopened FreeCAD occurrence inventory differs')
    expected=[]
    for item in items:
        props=geometry_properties(item['geometry']);d=np.asarray(props['envelope_dimensions_m'])
        matrix=np.asarray(item['transform']);centre=matrix[:3,3];extent=np.abs(matrix[:3,:3])@d
        if item['geometry']['kind'] in ('cylinder','tube'):
            dimensions=item['geometry']['dimensions_m'];radius=dimensions.get('outer_radius',dimensions.get('radius'));axis=matrix[:3,2]
            extent=2*radius*np.sqrt(np.maximum(0.,1-axis*axis))+dimensions['length']*np.abs(axis)
        volume=float(np.prod(d)) if item['geometry']['kind']=='envelope' else props['volume_m3']
        row=dict(volume_m3=volume,centroid_m=centre.tolist(),bounds_min_m=(centre-extent/2).tolist(),bounds_max_m=(centre+extent/2).tolist())
        current=actual[item['occurrence_id']]
        if any(current[k]!=item[k] for k in ('part_definition_id','part_revision_id')) or current['geometry_kind']!=item['geometry']['kind']:
            raise ValueError('Native part revision or envelope scope differs')
        if not _matching(current,row):raise ValueError('Actual reopened FreeCAD solid placement/volume differs')
        expected.append(row)
    # STEP loses application identities; compare the complete physical multiset
    # with neighbouring spatial bins, retaining identical colocated pieces.
    buckets={};cell=1e-5
    def bucket(row):return tuple(int(np.floor(x/cell)) for x in row['centroid_m'])
    for row in expected:buckets.setdefault(bucket(row),[]).append(row)
    if len(result['STEP_solids'])!=len(expected):raise ValueError('Reopened STEP solid count differs')
    for row in result['STEP_solids']:
        anchor=bucket(row);found=False
        for delta in cartesian_product((-1,0,1),repeat=3):
            group=buckets.get(tuple(a+b for a,b in zip(anchor,delta)),[])
            for index,source in enumerate(group):
                if _matching(row,source):group.pop(index);found=True;break
            if found:break
        if not found:raise ValueError('Reopened STEP volume/placement multiset differs')


def _matching(actual,expected):
    return (isclose(actual['volume_m3'],expected['volume_m3'],rel_tol=1e-7,abs_tol=1e-11)
        and all(np.allclose(actual[k],expected[k],rtol=0.,atol=2e-7) for k in ('centroid_m','bounds_min_m','bounds_max_m')))


def export_native(vehicle,output,*,cars=(1,),timeout_s=240,memory_bytes=4*1024**3):
    """Explicit bounded native job; root decides which actual cars to execute."""
    items=_native_items(vehicle,cars)
    if type(timeout_s) is not int or not 1<=timeout_s<=240 or type(memory_bytes) is not int or not 1024**3<=memory_bytes<=8*1024**3:
        raise ValueError('One to240 seconds and one to8GiB native resources required')
    folder=Path(output);_ordinary(folder)
    if folder.exists() and any(folder.iterdir()):raise ValueError('Fresh immutable native directory required')
    folder.mkdir(parents=True,exist_ok=True)
    command=_native_command(folder/'native-worker.py')
    if command is None:return dict(execution='not-run',candidate_id=vehicle['candidate_id'],cars=list(cars),reason='No actual headless FreeCAD tool',complete_installed_geometry=False,**FLAGS)
    data=dict(candidate_id=vehicle['candidate_id'],registry_id=vehicle['registry']['registry_id'],cars=list(cars),items=items,
        timeout_s=timeout_s,memory_bytes=memory_bytes,source_sha256=_source(vehicle))
    (folder/'native-input.json').write_bytes(encoded(data));(folder/'native-worker.py').write_text(_NATIVE_SCRIPT)
    try:
        proc=_run_native(command,folder,timeout_s,memory_bytes)
        (folder/'stdout.log').write_bytes(proc.stdout);(folder/'stderr.log').write_bytes(proc.stderr)
    except subprocess.TimeoutExpired as error:
        (folder/'stdout.log').write_bytes(error.stdout or b'');(folder/'stderr.log').write_bytes(error.stderr or b'')
        raise RuntimeError('Native deadline exceeded; inputs, logs and partial files retained') from error
    if proc.returncode or not (folder/'native-result.json').is_file():raise RuntimeError('Native geometry failed; exact inputs/logs retained')
    result=json.loads((folder/'native-result.json').read_bytes());_check_native(items,result,vehicle['candidate_id'],cars,memory_bytes)
    receipt=dict(schema='osr-reference-cell-native/1',execution='completed',candidate_id=vehicle['candidate_id'],registry_id=vehicle['registry']['registry_id'],cars=list(cars),
        source_sha256=_source(vehicle),input_id=identity(data),FreeCAD_version=result['FreeCAD_version'],
        files_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()},native_reopened=True,complete_installed_geometry=False,**FLAGS)
    receipt['receipt_id']=identity(receipt);(folder/'native-receipt.json').write_bytes(encoded(receipt));return receipt


def verify_native(vehicle,output,receipt=None):
    _validate(vehicle);folder=Path(output);_ordinary(folder)
    if any(p.is_symlink() for p in folder.iterdir()):raise ValueError('Ordinary native files required')
    receipt=receipt or json.loads((folder/'native-receipt.json').read_bytes())
    if (receipt.get('schema')!='osr-reference-cell-native/1' or receipt.get('receipt_id')!=identity({k:v for k,v in receipt.items() if k!='receipt_id'})
        or receipt.get('candidate_id')!=vehicle['candidate_id'] or receipt.get('registry_id')!=vehicle['registry']['registry_id']
        or receipt.get('source_sha256')!=_source(vehicle) or receipt.get('execution')!='completed' or receipt.get('native_reopened') is not True
        or receipt.get('complete_installed_geometry') is not False or any(receipt.get(k) is not False for k in FLAGS)
        or receipt.get('files_sha256')!={p.name:digest(p) for p in folder.iterdir() if p.is_file() and p.name!='native-receipt.json'}):
        raise ValueError('Native source/payload/identity/disposition differs')
    data=json.loads((folder/'native-input.json').read_bytes());items=_native_items(vehicle,receipt['cars'])
    if (data['items']!=items or data['source_sha256']!=_source(vehicle) or identity(data)!=receipt['input_id']
        or (folder/'native-worker.py').read_text()!=_NATIVE_SCRIPT):raise ValueError('Native exact source and input differ')
    with tempfile.TemporaryDirectory(prefix='osr-native-reopen-',dir=folder.parent) as temporary:
        temporary=Path(temporary);target=temporary/'reopened.json';script=temporary/'reopen.py'
        script.write_text('FOLDER='+repr(str(folder.resolve()))+'\nVERIFY_ONLY=True\nOUTPUT='+repr(str(target))+'\n'+_NATIVE_SCRIPT)
        command=_native_command(script)
        if command is None:raise ValueError('Actual FreeCAD tool required to reopen native files')
        proc=_run_native(command,temporary,data['timeout_s'],data['memory_bytes'])
        if proc.returncode or not target.is_file():raise ValueError('Independent native file reopening failed')
        actual=json.loads(target.read_bytes());_check_native(items,actual,vehicle['candidate_id'],receipt['cars'],data['memory_bytes'])
    return dict(verified=True,actual_reopened=True,candidate_id=vehicle['candidate_id'],cars=receipt['cars'],
        occurrences=len(items),recorded_FreeCAD_version=receipt['FreeCAD_version'],current_verifier_FreeCAD_version=actual['FreeCAD_version'],
        native_reuse_eligible=False,complete_installed_geometry=False,**FLAGS)
