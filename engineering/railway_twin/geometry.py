"""Actual primitive stock geometry and independent native round-trip checks.

Only explicitly located stock is exported.  Neither geometric validity nor a
native file establishes complete equipment, manufactured fit or acceptance.
"""
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import math
import re
import shutil
import subprocess
import tempfile

import numpy as np

PRODUCER = 'engineering/railway_twin/geometry.py'
IFC_NAME = 'railway-twin.ifc'
NATIVE_FILES = ('railway-twin.FCStd', 'railway-twin.step', 'native-input.json',
                'native-worker.py', 'native-result.json', 'native-stdout.log', 'native-stderr.log')
FLAGS = dict(complete_installed_geometry=False, engineering_accepted=False,
             physical_accepted=False, manufacturing_release=False, operating_release=False)


def _encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def _identity(value):
    return sha256(_encoded(value)).hexdigest()


def _hash(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def _number(value, name, positive=False):
    if (not isinstance(value, (int, float, np.integer, np.floating)) or isinstance(value, (bool, np.bool_))
            or not math.isfinite(value) or (positive and value <= 0)):
        raise ValueError('Finite ' + ('positive ' if positive else '') + name + ' required')
    return float(value)


def _vector(value, name):
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError('Finite three-vector required: ' + name)
    return np.array([_number(x, name) for x in value])


def _basis(axis):
    w = _vector(axis.tolist() if isinstance(axis, np.ndarray) else axis, 'axis')
    length = float(np.linalg.norm(w))
    if abs(length - 1.) > 1e-9:
        raise ValueError('Unit primitive axis required')
    w /= length
    u = np.cross([0., 0., 1.], w)
    if np.linalg.norm(u) < 1e-10:
        u = np.array([1., 0., 0.])
    u /= np.linalg.norm(u)
    return np.column_stack([u, np.cross(w, u), w])


def _box_bounds(at, size):
    return np.array(at), np.array(at) + size


def _disjoint(voids):
    for index, first in enumerate(voids):
        for second in voids[index + 1:]:
            if np.all(np.minimum(first['hi'], second['hi']) - np.maximum(first['lo'], second['lo']) > 1e-10):
                raise ValueError('Intersecting void envelopes need an explicit boolean mass evaluator')


def _primitive(part):
    """Exact nominal volume/centroid and bounds for supported stock and voids."""
    kind = part.get('kind')
    voids = []
    if kind in ('box', 'box-with-rectangular-cutouts'):
        at, size = _vector(part['at_m'], 'box origin'), _vector(part['size_m'], 'box size')
        if np.any(size <= 0):
            raise ValueError('Positive box dimensions required')
        lo, hi = _box_bounds(at, size)
        volume = float(np.prod(size))
        moment = volume * (at + size / 2)
        for hole in part.get('holes', []):
            if hole.get('axis', 'z') not in ('x', 'y', 'z'):
                raise ValueError('Axis-aligned drill required')
            index = 'xyz'.index(hole.get('axis', 'z'))
            start = at.copy()
            for i in range(3):
                if i != index:
                    start[i] += _number(hole.get('xyz'[i] + '_m', 0.), 'drill offset')
            start[index] += _number(hole.get('start_m', 0.), 'drill start')
            length = _number(hole.get('length_m', size[index]), 'drill length', True)
            radius = _number(hole['diameter_m'], 'drill diameter', True) / 2
            vlo, vhi = start.copy(), start.copy()
            for i in range(3):
                if i != index:
                    vlo[i] -= radius
                    vhi[i] += radius
            vhi[index] += length
            if np.any(vlo < lo - 1e-10) or np.any(vhi > hi + 1e-10):
                raise ValueError('Drill must be contained; clipped bores need an explicit boolean evaluator')
            axis = np.eye(3)[index]
            v = math.pi * radius**2 * length
            voids.append(dict(kind='cylinder', at=start, axis=axis, radius=radius,
                              length=length, volume=v, cg=start + axis * length / 2, lo=vlo, hi=vhi))
        for cut in part.get('rectangular_cutouts', []):
            cat, cs = _vector(cut['at_m'], 'cut origin'), _vector(cut['size_m'], 'cut size')
            if np.any(cs <= 0):
                raise ValueError('Positive rectangular cut dimensions required')
            clo, chi = np.maximum(lo, cat), np.minimum(hi, cat + cs)
            if np.any(chi <= clo):
                raise ValueError('Rectangular cut must remove material')
            cv = float(np.prod(chi - clo))
            voids.append(dict(kind='box', at=clo, size=chi - clo, volume=cv,
                              cg=(clo + chi) / 2, lo=clo, hi=chi))
        _disjoint(voids)
        for cut in voids:
            volume -= cut['volume']
            moment -= cut['volume'] * cut['cg']
        if volume <= 0:
            raise ValueError('Stock must retain positive material')
        # A cut touching a complete face can shrink the actual bounds. Reject
        # that domain rather than calling the original envelope exact bounds.
        for cut in voids:
            if cut['kind'] == 'box':
                full = [i for i in range(3) if abs(cut['lo'][i]-lo[i]) < 1e-10 and abs(cut['hi'][i]-hi[i]) < 1e-10]
                if len(full) >= 2:
                    raise ValueError('Face-removing cut needs an explicit changed-stock primitive')
        result = dict(volume=volume, cg=moment / volume, lo=lo, hi=hi, voids=voids)
    elif kind == 'oriented-RHS':
        a, b = _vector(part['start_m'], 'RHS start'), _vector(part['end_m'], 'RHS end')
        length = float(np.linalg.norm(b-a))
        if length <= 0:
            raise ValueError('Positive RHS length required')
        width, height, wall = [_number(part[key], key, True) for key in ('width_m', 'height_m', 'wall_m')]
        if 2*wall >= min(width, height):
            raise ValueError('RHS void must retain positive dimensions')
        basis = _basis((b-a)/length)
        points = np.array([a+basis@np.array(x) for x in product((-width/2,width/2),(-height/2,height/2),(0.,length))])
        result = dict(volume=length*(width*height-(width-2*wall)*(height-2*wall)),
                      cg=(a+b)/2, lo=points.min(axis=0), hi=points.max(axis=0),
                      origin=a, basis=basis, length=length, width=width, height=height, wall=wall, voids=[])
    elif kind in ('cylinder', 'annular-cylinder'):
        at = _vector(part['at_m'], 'cylinder origin')
        basis = _basis(part['axis'])
        axis = basis[:, 2]
        radius = _number(part['radius_m'], 'radius', True)
        inner = _number(part.get('inner_radius_m', 0.), 'inner radius')
        length = _number(part['length_m'], 'cylinder length', True)
        if not 0 <= inner < radius:
            raise ValueError('Positive annular material required')
        radial = radius*np.sqrt(np.maximum(0., 1-axis**2))
        end = at + axis*length
        result = dict(volume=math.pi*(radius**2-inner**2)*length, cg=(at+end)/2,
                      lo=np.minimum(at,end)-radial, hi=np.maximum(at,end)+radial,
                      origin=at, basis=basis, length=length, radius=radius, inner=inner, voids=[])
    else:
        raise ValueError('Unsupported stock primitive: ' + str(kind))
    declared = _number(part['volume_m3'], 'declared volume', True)
    if not math.isclose(result['volume'], declared, rel_tol=1e-7, abs_tol=1e-10):
        raise ValueError('Declared volume differs from actual primitive')
    return result


def validate_scene(scene):
    if scene.get('schema') != 'osr-railway-twin-scene/1' or scene.get('complete_installed_geometry') is not False:
        raise ValueError('Explicit incomplete railway research scene required')
    if any(key in scene and scene[key] is not False for key in (*FLAGS,'configuration_adopted','physical_journey_completed','selected_reference_changed')):
        raise ValueError('Research geometry cannot carry engineering acceptance or release')
    if not isinstance(scene.get('candidate_id'), str) or not re.fullmatch('[0-9a-f]{64}', scene['candidate_id']):
        raise ValueError('Explicit candidate identity required')
    occurrences = scene.get('occurrences')
    if not isinstance(occurrences, list) or not 1 <= len(occurrences) <= 50000:
        raise ValueError('One to 50000 explicit stock occurrences required')
    names = set()
    rows, primitive_cache = [], {}
    for row in occurrences:
        name = row.get('id')
        if not isinstance(name, str) or not name or name in names:
            raise ValueError('Unique named stock occurrences required')
        names.add(name)
        if not isinstance(row.get('component_definition_id'), str) or not re.fullmatch('[0-9a-f]{64}', row['component_definition_id']):
            raise ValueError('Explicit component definition identity required')
        if not isinstance(row.get('system'), str) or not row['system'] or row.get('scope') not in ('nominal-stock', 'equivalent-volume-stock'):
            raise ValueError('Explicit system and stock scope required')
        shift = _vector(row['translation_m'], 'occurrence translation')
        geometry_id = _identity(row['geometry'])
        if geometry_id not in primitive_cache:
            primitive_cache[geometry_id] = _primitive(row['geometry'])
        p = primitive_cache[geometry_id]
        mass = _number(row['mass_kg'], 'occurrence stock mass', True)
        if 'mass_kg' in row['geometry'] and not math.isclose(mass, _number(row['geometry']['mass_kg'], 'geometry mass', True), rel_tol=1e-9, abs_tol=1e-8):
            raise ValueError('Occurrence and source geometry mass differ')
        if 'density_kg_m3' in row['geometry']:
            density=_number(row['geometry']['density_kg_m3'],'declared stock density',True)
            if not math.isclose(mass,p['volume']*density,rel_tol=1e-7,abs_tol=1e-8):
                raise ValueError('Stock mass differs from actual primitive volume and declared density')
        rows.append(dict(id=name, component_definition_id=row['component_definition_id'], system=row['system'],
            scope=row['scope'], geometry_id=geometry_id, volume_m3=p['volume'], mass_kg=mass,
            centroid_m=(p['cg']+shift).tolist(), bounds_min_m=(p['lo']+shift).tolist(), bounds_max_m=(p['hi']+shift).tolist(),
            material_reference=row['geometry'].get('material_id', row['geometry'].get('material'))))
    mass = sum(row['mass_kg'] for row in rows)
    return dict(schema='osr-railway-twin-scene-properties/1', candidate_id=scene['candidate_id'], scene_id=_identity(scene),
        occurrences=rows, occurrence_count=len(rows), known_stock_mass_kg=mass,
        known_stock_volume_m3=sum(row['volume_m3'] for row in rows),
        known_stock_CG_m=(sum(row['mass_kg']*np.array(row['centroid_m']) for row in rows)/mass).tolist(),
        bounds_min_m=np.min([row['bounds_min_m'] for row in rows],axis=0).tolist(),
        bounds_max_m=np.max([row['bounds_max_m'] for row in rows],axis=0).tolist(),
        scope='Located nominal/equivalent stock only; omitted equipment, fabricated cuts and installed fit remain open', **FLAGS)


def _ordinary_folder(folder):
    folder = Path(folder)
    if any(p.is_symlink() for p in (folder, *folder.parents)):
        raise ValueError('Ordinary owned geometry output path required')
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _ordinary_files(folder, names):
    folder=Path(folder)
    if any(p.is_symlink() for p in (folder,*folder.parents)) or any((folder/name).is_symlink() for name in names):
        raise ValueError('Ordinary native geometry files required')


def _ifc_shape(f, geometry):
    p = _primitive(geometry)
    def point(v):
        return f.create_entity('IfcCartesianPoint', Coordinates=tuple(float(x) for x in v))
    def direction(v):
        return f.create_entity('IfcDirection', DirectionRatios=tuple(float(x) for x in v))
    def placement(origin, basis=np.eye(3)):
        return f.create_entity('IfcAxis2Placement3D',Location=point(origin),Axis=direction(basis[:,2]),RefDirection=direction(basis[:,0]))
    def extrude(profile, origin, length, basis=np.eye(3)):
        return f.create_entity('IfcExtrudedAreaSolid',SweptArea=profile,Position=placement(origin,basis),
                               ExtrudedDirection=direction((0.,0.,1.)),Depth=float(length))
    def rectangle(width, height):
        return f.create_entity('IfcRectangleProfileDef',ProfileType='AREA',XDim=float(width),YDim=float(height))
    def circle(radius):
        return f.create_entity('IfcCircleProfileDef',ProfileType='AREA',Radius=float(radius))
    if geometry['kind'] in ('box','box-with-rectangular-cutouts'):
        at, size = np.array(geometry['at_m']), np.array(geometry['size_m'])
        solid=extrude(rectangle(size[0],size[1]),at+np.array([size[0]/2,size[1]/2,0.]),size[2])
        for cut in p['voids']:
            if cut['kind']=='box':
                size=cut['size'];tool=extrude(rectangle(size[0],size[1]),cut['at']+np.array([size[0]/2,size[1]/2,0.]),size[2])
            else:
                tool=extrude(circle(cut['radius']),cut['at'],cut['length'],_basis(cut['axis']))
            solid=f.create_entity('IfcBooleanResult',Operator='DIFFERENCE',FirstOperand=solid,SecondOperand=tool)
        return solid
    if geometry['kind']=='oriented-RHS':
        profile=f.create_entity('IfcRectangleHollowProfileDef',ProfileType='AREA',XDim=p['width'],YDim=p['height'],WallThickness=p['wall'])
    else:
        profile=circle(p['radius']) if not p['inner'] else f.create_entity('IfcCircleHollowProfileDef',ProfileType='AREA',Radius=p['radius'],WallThickness=p['radius']-p['inner'])
    return extrude(profile,p['origin'],p['length'],p['basis'])


def _signature(entity):
    """Entity-number-independent signature of actual IFC geometry/placements."""
    if hasattr(entity, 'is_a'):
        return dict(type=entity.is_a(),attributes=[_signature(value) for value in entity])
    if isinstance(entity, (tuple,list)):
        return [_signature(x) for x in entity]
    return entity


def write_ifc(scene, folder):
    import ifcopenshell
    import ifcopenshell.api
    properties=validate_scene(scene);folder=_ordinary_folder(folder);path=folder/IFC_NAME
    if path.exists():
        raise ValueError('Fresh IFC output required')
    api=ifcopenshell.api.run;f=api('project.create_file',version='IFC4')
    project=api('root.create_entity',f,ifc_class='IfcProject',name='OpenSourceRail research stock twin')
    length=api('unit.add_si_unit',f,unit_type='LENGTHUNIT');api('unit.assign_unit',f,units=[length])
    model=api('context.add_context',f,context_type='Model')
    context=api('context.add_context',f,context_type='Model',context_identifier='Body',target_view='MODEL_VIEW',parent=model)
    site=api('root.create_entity',f,ifc_class='IfcSite',name='Declared research route coordinate frame')
    api('aggregate.assign_object',f,products=[site],relating_object=project)
    materials={};representations={};objects=[];material_objects={}
    for occurrence,row in zip(scene['occurrences'],properties['occurrences']):
        obj=api('root.create_entity',f,ifc_class='IfcBuildingElementProxy',name=occurrence['id'])
        objects.append(obj)
        point=f.create_entity('IfcCartesianPoint',Coordinates=tuple(float(x) for x in occurrence['translation_m']))
        obj.ObjectPlacement=f.create_entity('IfcLocalPlacement',RelativePlacement=f.create_entity('IfcAxis2Placement3D',Location=point))
        if row['geometry_id'] not in representations:
            item=_ifc_shape(f,occurrence['geometry'])
            representation=f.create_entity('IfcShapeRepresentation',ContextOfItems=context,RepresentationIdentifier='Body',
                RepresentationType='CSG' if item.is_a('IfcBooleanResult') else 'SweptSolid',Items=(item,))
            representations[row['geometry_id']]=f.create_entity('IfcProductDefinitionShape',Representations=(representation,))
        obj.Representation=representations[row['geometry_id']]
        ps=api('pset.add_pset',f,product=obj,name='OSR_Research_Identity')
        values=dict(candidate_id=scene['candidate_id'],occurrence_id=row['id'],component_definition_id=row['component_definition_id'],
            geometry_id=row['geometry_id'],system=row['system'],scope=row['scope'],stock_mass_kg=row['mass_kg'],
            stock_volume_m3=row['volume_m3'],material_reference=row['material_reference'] or 'unassigned',**FLAGS)
        api('pset.edit_pset',f,pset=ps,properties=values)
        material_name=row['material_reference'] or 'Unassigned research material'
        if material_name not in materials:
            materials[material_name]=f.create_entity('IfcMaterial',Name=material_name)
        material_objects.setdefault(material_name,[]).append(obj)
    f.create_entity('IfcRelContainedInSpatialStructure',GlobalId=ifcopenshell.guid.new(),RelatedElements=tuple(objects),RelatingStructure=site)
    for name,items in sorted(material_objects.items()):
        f.create_entity('IfcRelAssociatesMaterial',GlobalId=ifcopenshell.guid.new(),RelatedObjects=tuple(items),RelatingMaterial=materials[name])
    for entity in f.by_type('IfcRoot'):
        entity.GlobalId=ifcopenshell.guid.compress(sha256((properties['scene_id']+entity.is_a()+str(entity.id())).encode()).hexdigest()[:32])
    # SET ordering is immaterial; sort it for byte reproducibility as well.
    for relation in f.by_type('IfcRelContainedInSpatialStructure'):
        relation.RelatedElements=tuple(sorted(relation.RelatedElements,key=lambda x:x.Name or ''))
    f.header.file_name.name=IFC_NAME;f.header.file_name.time_stamp='2026-10-28T00:00:00'
    f.write(str(path))
    receipt=dict(schema='osr-railway-twin-IFC/1',candidate_id=scene['candidate_id'],scene_id=properties['scene_id'],
        execution='completed',native_reopened=True,file=IFC_NAME,sha256=_hash(path),
        source_sha256={PRODUCER:_hash(__file__)},ifcopenshell_version=ifcopenshell.version,
        occurrence_count=len(properties['occurrences']),geometry_tolerance_m=2e-5,relative_volume_tolerance=.002,
        scope='Actual IFC swept/boolean stock solids; installed geometry and physical acceptance remain open',**FLAGS)
    receipt['receipt_id']=_identity(receipt)
    verify_ifc(scene,folder,receipt)
    return receipt


def verify_ifc(scene, folder, receipt):
    import ifcopenshell
    import ifcopenshell.geom
    from ifcopenshell.util.element import get_material,get_pset
    from ifcopenshell.util.placement import get_local_placement
    from ifcopenshell.util.shape import get_volume
    properties=validate_scene(scene);path=Path(folder)/IFC_NAME
    _ordinary_files(folder,(IFC_NAME,))
    if (receipt.get('schema')!='osr-railway-twin-IFC/1' or receipt.get('receipt_id')!=_identity({k:v for k,v in receipt.items() if k!='receipt_id'})
            or receipt.get('candidate_id')!=scene['candidate_id'] or receipt.get('scene_id')!=properties['scene_id']
            or receipt.get('file')!=IFC_NAME or receipt.get('sha256')!=_hash(path)
            or receipt.get('source_sha256')!={PRODUCER:_hash(__file__)}
            or receipt.get('ifcopenshell_version')!=ifcopenshell.version
            or receipt.get('execution')!='completed' or receipt.get('native_reopened') is not True
            or receipt.get('occurrence_count')!=len(properties['occurrences'])
            or receipt.get('geometry_tolerance_m')!=2e-5 or receipt.get('relative_volume_tolerance')!=.002
            or any(receipt.get(k) is not v for k,v in FLAGS.items())):
        raise ValueError('IFC source, receipt, candidate or non-promoting disposition differs')
    f=ifcopenshell.open(str(path));objects=f.by_type('IfcBuildingElementProxy')
    expected={r['id']:(o,r) for o,r in zip(scene['occurrences'],properties['occurrences'])}
    if len(objects)!=len(expected) or {obj.Name for obj in objects}!=set(expected):
        raise ValueError('IFC occurrence inventory differs')
    settings=ifcopenshell.geom.settings();settings.set(settings.USE_WORLD_COORDS,True)
    settings.set(settings.MESHER_LINEAR_DEFLECTION,1e-5)
    maximum_error=0.
    # Build independent expected primitive definitions in a different IFC file.
    independent=ifcopenshell.file(schema='IFC4');expected_signatures={};actual_signatures={};mesh_metrics={}
    for obj in objects:
        source,row=expected[obj.Name];ps=get_pset(obj,'OSR_Research_Identity')
        for key,value in dict(candidate_id=scene['candidate_id'],occurrence_id=row['id'],component_definition_id=row['component_definition_id'],
                geometry_id=row['geometry_id'],system=row['system'],scope=row['scope'],stock_mass_kg=row['mass_kg'],
                stock_volume_m3=row['volume_m3'],material_reference=row['material_reference'] or 'unassigned',**FLAGS).items():
            if ps.get(key)!=value:
                raise ValueError('IFC occurrence identity, material, mass or scope differs: '+obj.Name)
        pose=get_local_placement(obj.ObjectPlacement)
        if not np.allclose(pose[:3,:3],np.eye(3),atol=1e-12,rtol=0) or not np.allclose(pose[:3,3],source['translation_m'],atol=1e-9,rtol=0):
            raise ValueError('IFC occurrence placement differs: '+obj.Name)
        representations=obj.Representation.Representations
        if len(representations)!=1 or len(representations[0].Items)!=1:
            raise ValueError('IFC actual primitive geometry differs: '+obj.Name)
        item=representations[0].Items[0]
        if item.id() not in actual_signatures:
            actual_signatures[item.id()]=_signature(item)
        if row['geometry_id'] not in expected_signatures:
            expected_signatures[row['geometry_id']]=_signature(_ifc_shape(independent,source['geometry']))
        if actual_signatures[item.id()]!=expected_signatures[row['geometry_id']]:
            raise ValueError('IFC actual primitive geometry differs: '+obj.Name)
        material=get_material(obj)
        if material is None or material.Name!=(row['material_reference'] or 'Unassigned research material'):
            raise ValueError('IFC material association differs: '+obj.Name)
        shift=np.array(source['translation_m'])
        if item.id() not in mesh_metrics:
            shape=ifcopenshell.geom.create_shape(settings,obj)
            vertices=np.array(shape.geometry.verts).reshape((-1,3))-shift
            volume=abs(get_volume(shape.geometry))
            faces=np.array(shape.geometry.faces).reshape((-1,3))
            origin=np.array(row['centroid_m'])-shift
            triangles=vertices[faces]-origin
            signed=np.einsum('ij,ij->i',triangles[:,0],np.cross(triangles[:,1],triangles[:,2]))/6
            centroid=origin+(signed[:,None]*triangles.sum(axis=1)/4).sum(axis=0)/signed.sum()
            mesh_metrics[item.id()]=(volume,vertices.min(axis=0),vertices.max(axis=0),centroid)
        volume,lo,hi,centroid=mesh_metrics[item.id()]
        error=abs(volume-row['volume_m3'])/row['volume_m3'];maximum_error=max(maximum_error,error)
        # Circular meshing approximates the exact swept profile. The actual
        # profile/placement signature above is exact; bounds catch moved stock.
        if error>.002 or not np.allclose(lo+shift,row['bounds_min_m'],atol=2e-5,rtol=0) or not np.allclose(hi+shift,row['bounds_max_m'],atol=2e-5,rtol=0):
            raise ValueError('Reopened IFC stock bounds or volume differ: '+obj.Name)
        if not np.allclose(centroid+shift,row['centroid_m'],atol=2e-5,rtol=0):
            raise ValueError('Reopened IFC stock centroid differs: '+obj.Name)
    return dict(verified=True,candidate_id=scene['candidate_id'],scene_id=properties['scene_id'],
        occurrence_count=len(objects),maximum_relative_volume_error=maximum_error,native_reopened=True,**FLAGS)


def _native_command(script):
    direct=shutil.which('FreeCADCmd') or shutil.which('freecadcmd')
    if direct:
        return [direct,str(script)]
    flatpak=shutil.which('flatpak')
    if flatpak:
        return [flatpak,'run','--filesystem='+str(Path(script).parent),'--command=FreeCADCmd','org.freecad.FreeCAD',str(script)]
    return None


def export_native(scene, folder, timeout_s=240):
    """Native export is explicit; unavailable tools never produce fake files."""
    validate_scene(scene)
    if type(timeout_s) is not int or not 1<=timeout_s<=240:
        raise ValueError('Bounded native timeout of one to240 seconds required')
    folder=_ordinary_folder(folder)
    if any((folder/name).exists() for name in ('railway-twin.FCStd','railway-twin.step','native-input.json')):
        raise ValueError('Fresh native geometry output required')
    command=_native_command(folder/'native-worker.py')
    if command is None:
        return dict(execution='not-run',reason='FreeCADCmd/Flatpak unavailable; no substitute CAD issued',
                    candidate_id=scene['candidate_id'],scene_id=_identity(scene),**FLAGS)
    (folder/'native-input.json').write_bytes(_encoded(scene))
    (folder/'native-worker.py').write_text(_NATIVE_WORKER)
    try:
        proc=subprocess.run(command,cwd=folder,capture_output=True,timeout=timeout_s)
    except subprocess.TimeoutExpired as error:
        (folder/'native-stdout.log').write_bytes(error.stdout or b'')
        (folder/'native-stderr.log').write_bytes(error.stderr or b'')
        raise RuntimeError('Native geometry timeout; exact inputs and logs retained') from error
    (folder/'native-stdout.log').write_bytes(proc.stdout);(folder/'native-stderr.log').write_bytes(proc.stderr)
    if proc.returncode or not (folder/'native-result.json').is_file():
        raise RuntimeError('Native geometry export failed; exact inputs and logs retained')
    value=json.loads((folder/'native-result.json').read_bytes())
    _check_native_results(scene,value)
    receipt=dict(schema='osr-railway-twin-native/1',candidate_id=scene['candidate_id'],scene_id=_identity(scene),
        execution='completed',native_reopened=True,source_sha256={PRODUCER:_hash(__file__)},
        files_sha256={name:_hash(folder/name) for name in NATIVE_FILES},
        FreeCAD_version=value['FreeCAD_version'],scope='Actual FreeCAD and STEP nominal stock only',**FLAGS)
    receipt['receipt_id']=_identity(receipt)
    return receipt


def _check_native_results(scene,result):
    properties=validate_scene(scene)
    expected={r['id']:r for r in properties['occurrences']}
    if result.get('candidate_id')!=scene['candidate_id'] or len(result.get('FCStd_occurrences',[]))!=len(expected):
        raise ValueError('Native CAD candidate or occurrence inventory differs')
    actual={r['id']:r for r in result['FCStd_occurrences']}
    if set(actual)!=set(expected) or len(actual)!=len(expected):
        raise ValueError('Native CAD occurrence inventory differs')
    for name,row in actual.items():
        source=expected[name]
        if row.get('component_definition_id')!=source['component_definition_id'] or row.get('geometry_id')!=source['geometry_id']:
            raise ValueError('Native CAD component geometry identity differs')
        for key in ('centroid_m','bounds_min_m','bounds_max_m'):
            if not np.allclose(row[key],source[key],rtol=0,atol=2e-7):
                raise ValueError('Reopened native occurrence placement or bounds differ: '+name)
        if not math.isclose(row['volume_m3'],source['volume_m3'],rel_tol=1e-7,abs_tol=1e-10):
            raise ValueError('Reopened native occurrence volume differs: '+name)
    step=result.get('STEP_solids',[])
    if len(step)!=len(expected):
        raise ValueError('Reopened STEP solid count, placement, bounds or volume differ')
    # Match the multiset with tolerances, including neighbouring spatial bins.
    # Rounding whole metric tuples would falsely reject legitimate STEP values
    # which land on opposite sides of a decimal rounding boundary.
    buckets={};cell=1e-5
    def key(row):return tuple(math.floor(float(x)/cell) for x in row['centroid_m'])
    for row in expected.values():buckets.setdefault(key(row),[]).append(row)
    for row in step:
        anchor=key(row);matched=False
        for delta in product((-1,0,1),repeat=3):
            bucket=buckets.get(tuple(a+d for a,d in zip(anchor,delta)),[])
            for index,source in enumerate(bucket):
                if (all(np.allclose(row[name],source[name],rtol=0,atol=2e-7) for name in ('centroid_m','bounds_min_m','bounds_max_m'))
                        and math.isclose(row['volume_m3'],source['volume_m3'],rel_tol=1e-7,abs_tol=1e-10)):
                    bucket.pop(index);matched=True;break
            if matched:break
        if not matched:
            raise ValueError('Reopened STEP solid count, placement, bounds or volume differ')


def verify_native(scene, folder, receipt):
    folder=Path(folder);validate_scene(scene)
    _ordinary_files(folder,NATIVE_FILES)
    if receipt.get('execution')=='not-run':
        if (receipt.get('candidate_id')!=scene['candidate_id'] or receipt.get('scene_id')!=_identity(scene)
                or not isinstance(receipt.get('reason'),str) or not receipt['reason']
                or any(receipt.get(k) is not v for k,v in FLAGS.items())
                or any((folder/name).exists() for name in ('railway-twin.FCStd','railway-twin.step'))):
            raise ValueError('Unexecuted native export cannot contain CAD substitutes')
        return dict(verified=True,execution='not-run',candidate_id=scene['candidate_id'],**FLAGS)
    if (receipt.get('schema')!='osr-railway-twin-native/1' or receipt.get('receipt_id')!=_identity({k:v for k,v in receipt.items() if k!='receipt_id'})
            or receipt.get('candidate_id')!=scene['candidate_id'] or receipt.get('scene_id')!=_identity(scene)
            or receipt.get('source_sha256')!={PRODUCER:_hash(__file__)} or receipt.get('native_reopened') is not True
            or any(receipt.get(k) is not v for k,v in FLAGS.items())
            or receipt.get('files_sha256')!={name:_hash(folder/name) for name in NATIVE_FILES}
            or (folder/'native-input.json').read_bytes()!=_encoded(scene)
            or (folder/'native-worker.py').read_text()!=_NATIVE_WORKER):
        raise ValueError('Native source, input, payload, candidate or disposition differs')
    # Fresh FreeCAD process reopens the actual retained files, not a saved result.
    scratch=Path(tempfile.mkdtemp(prefix='osr-twin-native-verify-'))
    script=scratch/'verify.py';script.write_text('FOLDER='+repr(str(folder.resolve()))+'\n'+_NATIVE_VERIFY)
    command=_native_command(script)
    if command is None:
        raise ValueError('FreeCAD required to verify actual native files')
    # The Flatpak process must read the retained package as well as its script.
    if 'run' in command:
        command.insert(command.index('run')+1,'--filesystem='+str(folder.resolve()))
    try:
        proc=subprocess.run(command,cwd=scratch,capture_output=True,timeout=240)
        (scratch/'stdout.log').write_bytes(proc.stdout);(scratch/'stderr.log').write_bytes(proc.stderr)
        if proc.returncode or not (scratch/'verified.json').is_file():
            raise ValueError('Actual native reopen failed; logs retained at '+str(scratch))
        _check_native_results(scene,json.loads((scratch/'verified.json').read_bytes()))
    except subprocess.TimeoutExpired as error:
        (scratch/'stdout.log').write_bytes(error.stdout or b'');(scratch/'stderr.log').write_bytes(error.stderr or b'')
        raise ValueError('Actual native verification timed out; logs retained at '+str(scratch)) from error
    else:
        shutil.rmtree(scratch)
    return dict(verified=True,candidate_id=scene['candidate_id'],scene_id=_identity(scene),native_reopened=True,**FLAGS)


_NATIVE_COMMON = r'''
import FreeCAD as A,Part,Import,json,pathlib,math
def metric(shape):
    b=shape.BoundBox;solids=shape.Solids;volume=sum(s.Volume for s in solids)
    if not volume:raise ValueError('Native material solid required')
    c=A.Vector()
    for solid in solids:c=c+solid.CenterOfMass*(solid.Volume/volume)
    return dict(volume_m3=volume/1e9,centroid_m=[c.x/1000,c.y/1000,c.z/1000],bounds_min_m=[b.XMin/1000,b.YMin/1000,b.ZMin/1000],bounds_max_m=[b.XMax/1000,b.YMax/1000,b.ZMax/1000])
def reopen(folder,data):
    doc=A.openDocument(str(folder/'railway-twin.FCStd'));rows=[]
    for obj in doc.Objects:
        if not hasattr(obj,'Shape'):continue
        if obj.CandidateID!=data['candidate_id'] or not obj.Shape.isValid():raise ValueError('Invalid native occurrence/candidate')
        rows.append(dict(id=obj.OccurrenceID,component_definition_id=obj.ComponentDefinitionID,geometry_id=obj.GeometryID,**metric(obj.Shape)))
    A.closeDocument(doc.Name);step=Part.Shape();step.read(str(folder/'railway-twin.step'))
    if not step.isValid():raise ValueError('Invalid reopened STEP')
    return dict(candidate_id=data['candidate_id'],FCStd_occurrences=rows,STEP_solids=[metric(s) for s in step.Solids],FreeCAD_version=list(A.Version()))
'''

_NATIVE_WORKER = _NATIVE_COMMON + r'''
from hashlib import sha256
def ident(v):return sha256((json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()
out=pathlib.Path(__file__).parent;data=json.loads((out/'native-input.json').read_text());doc=A.newDocument('OSR_Railway_Research_Twin');objects=[];cache={}
for index,row in enumerate(data['occurrences']):
    p=row['geometry'];key=ident(p)
    if key not in cache:
        if p['kind'] in ('box','box-with-rectangular-cutouts'):
            shape=Part.makeBox(*[v*1000 for v in p['size_m']],A.Vector(*[v*1000 for v in p['at_m']]))
            for hole in p.get('holes',[]):
                axis='xyz'.index(hole.get('axis','z'));start=list(p['at_m']);direction=[0.,0.,0.];direction[axis]=1.
                for j in range(3):start[j]+=hole.get('start_m',0.) if j==axis else hole.get('xyz'[j]+'_m',0.)
                shape=shape.cut(Part.makeCylinder(hole['diameter_m']*500,hole.get('length_m',p['size_m'][axis])*1000,A.Vector(*[v*1000 for v in start]),A.Vector(*direction)))
            for cut in p.get('rectangular_cutouts',[]):shape=shape.cut(Part.makeBox(*[v*1000 for v in cut['size_m']],A.Vector(*[v*1000 for v in cut['at_m']])))
        elif p['kind']=='oriented-RHS':
            a=A.Vector(*p['start_m']);b=A.Vector(*p['end_m']);w=b-a;L=w.Length;w.normalize();u=A.Vector(0,0,1).cross(w)
            if u.Length<1e-10:u=A.Vector(1,0,0)
            u.normalize();v=w.cross(u);m=A.Matrix()
            for r in range(3):
                for c,basis in enumerate((u,v,w)):setattr(m,'A'+str(r+1)+str(c+1),getattr(basis,'xyz'[r]))
            width,height,wall=[p[k]*1000 for k in ('width_m','height_m','wall_m')]
            shape=Part.makeBox(width,height,L*1000,A.Vector(-width/2,-height/2,0)).cut(Part.makeBox(width-2*wall,height-2*wall,L*1000,A.Vector(-width/2+wall,-height/2+wall,0)))
            shape.transformShape(m);shape.translate(a*1000)
        else:
            at=A.Vector(*[v*1000 for v in p['at_m']]);axis=A.Vector(*p['axis']);shape=Part.makeCylinder(p['radius_m']*1000,p['length_m']*1000,at,axis)
            if p.get('inner_radius_m',0):shape=shape.cut(Part.makeCylinder(p['inner_radius_m']*1000,p['length_m']*1000,at,axis))
        if not shape.isValid():raise ValueError('Invalid native primitive')
        cache[key]=shape
    shape=cache[key].copy();shape.translate(A.Vector(*[v*1000 for v in row['translation_m']]))
    obj=doc.addObject('PartDesign::Feature','Occurrence_'+str(index));obj.Label=row['id'];obj.Shape=shape
    for name,value in [('CandidateID',data['candidate_id']),('OccurrenceID',row['id']),('ComponentDefinitionID',row['component_definition_id']),('GeometryID',key)]:obj.addProperty('App::PropertyString',name);setattr(obj,name,value)
    objects.append(obj)
doc.recompute();doc.saveAs(str(out/'railway-twin.FCStd'))
# Import.export can apply the user's single-object origin-reset preference.
# Export an explicit world-space compound through the native Part writer so
# every retained solid keeps its actual placement, independent of GUI settings.
Part.makeCompound([obj.Shape for obj in objects]).exportStep(str(out/'railway-twin.step'))
A.closeDocument(doc.Name)
(out/'native-result.json').write_text(json.dumps(reopen(out,data),sort_keys=True)+'\n')
'''

_NATIVE_VERIFY = _NATIVE_COMMON + r'''
folder=pathlib.Path(FOLDER);data=json.loads((folder/'native-input.json').read_text())
(pathlib.Path(__file__).parent/'verified.json').write_text(json.dumps(reopen(folder,data),sort_keys=True)+'\n')
'''
