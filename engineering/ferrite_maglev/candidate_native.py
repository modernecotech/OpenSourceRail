"""Native exact candidate module and honest final-position assembly visibility."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip
import json
import math
from . import model,candidate_magnetics as magnetics,candidate_media as media,station_native,delivery_platform as platform
from engineering.factory_examples import native,models
ROOT=model.ROOT
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/candidate-native'
SCHEMA='osr-candidate-native/1'
FILES={'definition.json','model.FCStd','model.step.gz','native-cad.json','native-mesh.json.gz','overview.png','assembly-visibility.mp4','visual-receipt.json','geometry-properties.json','README.md'}


def source_paths():return sorted({Path(__file__),Path(native.__file__),Path(models.__file__),Path(media.__file__),Path(station_native.__file__),*magnetics.source_paths(),ROOT/'engineering/analysis/tests/test_ferrite_maglev_candidate_native.py'})
def sources():return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in source_paths()}
def sha(p):return sha256(Path(p).read_bytes()).hexdigest()


def definition():
    d=magnetics.definition();parts=deepcopy(d['module']['parts']);groups={k:[] for k in ('core-and-cradle','ferrite','physical-coil-packs','housing-cooling-connectors')}
    for p in parts:
        p['source_material']=p['material'];p['source_component_scope']=p['component_scope'];p['role']=p['component_scope'];mat=p['material'].lower()
        p['material']='ferrite' if 'tdk' in mat else 'winding-envelope' if 'copper' in mat or 'fluid' in mat else 'aluminium' if mat=='aluminium' else 'gfrp' if 'epoxy' in mat else 'steel'
        p['basis']='Exact candidate material-region/envelope; effective coil-pack density accounts copper fill; complete wire routing is not modelled'
        key='ferrite' if p['material']=='ferrite' else 'physical-coil-packs' if p['source_component_scope']=='new-winding' else 'core-and-cradle' if p['source_component_scope'] in {'new-core','new-lowered-module-attachment'} else 'housing-cooling-connectors'
        groups[key].append(p['id'])
    return dict(id='OSR-CANDIDATE-DIMENSIONED-MAGNETIC-MODULE',configuration_sha256=d['configuration_sha256'],parts=parts,
        construction_stages=[dict(id=k,parts=v) for k,v in groups.items() if v],retain_native_tessellation=True,interference_roles=[],
        modelled_material_mass_kg=d['module']['mass_kg'],scope='One module, actual source solids/voids and allocated connector/cooling envelopes; no complete train or production-ready winding/PCB',
        interference_scope='No assembled interference or swept motion acceptance from this export; candidate structural/clearance evaluators retain their own failures.',**platform.FLAGS)


MESH_VOLUME_REL_TOL=.01
MESH_CENTROID_ABS_TOL_M=2e-6
VERTEX_SURFACE_TOL_M=1e-8


def _extent(part):
    import numpy as np
    low=np.asarray(part['at_m'],float);size=np.asarray(part['size_m'],float)
    if part['kind']=='cylinder':
        extent=np.full(3,size[0]);extent['xyz'.index(part.get('cylinder_axis','z'))]=size[2]
    elif part['kind']=='box':extent=size
    else:raise ValueError('candidate mesh source must be a box/cylinder')
    return low,low+extent


def _source_surface(part,points,tolerance):
    """Source primitive/void boundary and occupied-domain membership."""
    import numpy as np
    points=np.asarray(points,float);low,high=_extent(part);inside=np.all((points>=low-tolerance)&(points<=high+tolerance),axis=1)
    if part['kind']=='box':distance=np.min(np.minimum(abs(points-low),abs(points-high)),axis=1)
    else:
        axis='xyz'.index(part.get('cylinder_axis','z'));other=[i for i in range(3) if i!=axis];radius=part['size_m'][0]/2;centre=(low+high)/2
        radial=np.linalg.norm(points[:,other]-centre[other],axis=1);inside&=radial<=radius+tolerance
        distance=np.minimum(abs(radial-radius),np.minimum(abs(points[:,axis]-low[axis]),abs(points[:,axis]-high[axis])))
    for hole in part.get('holes',[]):
        axis='xyz'.index(hole.get('axis','z'));other=[i for i in range(3) if i!=axis];centre=[low[k]+hole['xyz'[k]+'_m'] for k in other]
        radius=hole['diameter_m']/2;radial=np.linalg.norm(points[:,other]-centre,axis=1);start=low[axis]+hole.get('start_m',0);end=start+hole.get('length_m',high[axis]-low[axis]);coord=points[:,axis]
        active=(coord>=start-tolerance)&(coord<=end+tolerance);caps=np.zeros(len(points),bool)
        if start>low[axis]+tolerance:
            caps|=(abs(coord-start)<=tolerance)&(radial<=radius+tolerance)
            distance=np.minimum(distance,np.where(radial<=radius+tolerance,abs(coord-start),np.inf))
        if end<high[axis]-tolerance:
            caps|=(abs(coord-end)<=tolerance)&(radial<=radius+tolerance)
            distance=np.minimum(distance,np.where(radial<=radius+tolerance,abs(coord-end),np.inf))
        inside&=~((radial<radius-tolerance)&active&~caps)
        distance=np.minimum(distance,np.where(active,abs(radial-radius),np.inf))
    return inside&(distance<=tolerance)


def mesh_properties(part,mesh):
    """Actual topology, source geometry, signed volume and first moments."""
    import numpy as np
    vertices=np.asarray(mesh.get('vertices_m',[]),float);raw=mesh.get('triangles',[])
    if vertices.ndim!=2 or vertices.shape[1:]!=(3,) or not 4<=len(vertices)<=200000 or not np.isfinite(vertices).all():raise ValueError('nonempty finite native vertices required')
    if not isinstance(raw,list) or not 4<=len(raw)<=200000 or any(not isinstance(t,list) or len(t)!=3 or any(type(i)is not int for i in t) for t in raw):raise ValueError('nonempty integral native triangles required')
    triangles=np.asarray(raw,int)
    if triangles.min()<0 or triangles.max()>=len(vertices) or set(triangles.ravel())!=set(range(len(vertices))):raise ValueError('native triangle indices/unused vertices differ')
    if mesh.get('material')!=part['material']:raise ValueError('native tessellation material differs')
    if not np.all(_source_surface(part,vertices,VERTEX_SURFACE_TOL_M)):raise ValueError('native vertices do not lie on source material/void surfaces')
    # Weld only coincident tessellation seams; unused/duplicate faces cannot
    # supply fake bounds or an apparently closed but open source surface.
    welded={};mapping=[]
    for v in vertices:
        key=tuple(np.round(v,10));mapping.append(welded.setdefault(key,len(welded)))
    t=np.asarray(mapping)[triangles];edges={};faces=set()
    for tri in t:
        if len(set(tri))!=3:raise ValueError('native welded triangle is degenerate')
        face=tuple(sorted(tri))
        if face in faces:raise ValueError('duplicate native face')
        faces.add(face)
        for u,v in zip(tri,np.roll(tri,-1)):
            edge=(min(u,v),max(u,v));edges.setdefault(edge,[]).append(1 if u<v else -1)
    if any(len(v)!=2 or sum(v)!=0 for v in edges.values()):raise ValueError('native mesh is not a closed oriented two-manifold')
    points=vertices[triangles];cross=np.cross(points[:,1]-points[:,0],points[:,2]-points[:,0])
    if np.any(np.linalg.norm(cross,axis=1)<=1e-16):raise ValueError('native triangle has no area')
    radii=[h['diameter_m']/2 for h in part.get('holes',[])]
    if part['kind']=='cylinder':radii.append(part['size_m'][0]/2)
    chord=max([VERTEX_SURFACE_TOL_M,*[.01*r for r in radii]])
    # Tessellated curved walls are chords. Their interior samples may depart
    # from the curved surface by at most1% of the source radius; plane-only
    # parts keep the exact vertex tolerance. The exporter10mm setting is NOT
    # treated as permission to deform this small candidate's material regions.
    samples=np.concatenate([points.mean(1),.5*(points[:,0]+points[:,1]),.5*(points[:,1]+points[:,2]),.5*(points[:,2]+points[:,0])])
    if not np.all(_source_surface(part,samples,chord)):raise ValueError('native triangles bridge source voids or leave source boundaries')
    low,high=_extent(part);bounds=np.array([vertices.min(0),vertices.max(0)])
    if np.max(abs(bounds-np.array([low,high])))>chord:raise ValueError('native mesh bounds differ from source')
    origin=vertices.mean(0);local=points-origin;signed=np.einsum('ij,ij->i',local[:,0],np.cross(local[:,1],local[:,2]))/6;volume=float(signed.sum())
    if volume<=0 or not math.isclose(volume,part['volume_m3'],rel_tol=MESH_VOLUME_REL_TOL):raise ValueError('actual signed native mesh volume differs')
    centre=origin+(signed[:,None]*local.sum(1)/4).sum(0)/volume
    if np.max(abs(centre-np.asarray(part['cg_m'])))>MESH_CENTROID_ABS_TOL_M:raise ValueError('actual signed native mesh centroid differs')
    return dict(triangles=len(triangles),vertices=len(vertices),closed_oriented_manifold=True,source_surface_verified=True,
        signed_volume_m3=volume,volume_relative_error=abs(volume/part['volume_m3']-1),centroid_m=centre.tolist(),bounds_m=bounds.tolist(),
        volume_relative_tolerance=MESH_VOLUME_REL_TOL,centroid_absolute_tolerance_m=MESH_CENTROID_ABS_TOL_M,curved_chord_tolerance_m=chord)


def properties(value,receipt,mesh):
    by={p['id']:p for p in value['parts']};seen={p['id']:p for p in mesh['parts']};rows=[]
    if len(by)!=len(value['parts']) or len(seen)!=len(mesh['parts']) or len(receipt['parts'])!=len(by) or set(by)!=set(seen) or set(by)!={p['id'] for p in receipt['parts']}:raise ValueError('native candidate part identity differs')
    if sum(len(p.get('triangles',[])) for p in mesh['parts'])>250000 or sum(len(p.get('vertices_m',[])) for p in mesh['parts'])>250000:raise ValueError('bounded candidate tessellation required')
    for actual in receipt['parts']:
        p=by[actual['id']];expected=models.volume(p);volume=actual['volume_m3'];item=seen[p['id']];centroid=item['centre_of_volume_m'];density=p['mass_kg']/p['volume_m3']
        if not math.isclose(expected,volume,rel_tol=1e-7) or not math.isclose(volume,p['volume_m3'],rel_tol=1e-7) or not math.isclose(item['volume_m3'],volume,rel_tol=1e-7):raise ValueError('native candidate occupied BRep volume differs')
        if len(centroid)!=3 or not all(math.isfinite(x) for x in centroid) or max(abs(a-b) for a,b in zip(centroid,p['cg_m']))>1e-8:raise ValueError('native candidate BRep centroid differs')
        audit=mesh_properties(p,item)
        rows.append(dict(id=p['id'],native_volume_m3=volume,density_basis_kg_m3=density,native_mass_kg=volume*density,native_centroid_m=centroid,source_mass_kg=p['mass_kg'],mesh=audit))
    mass=math.fsum(r['native_mass_kg'] for r in rows);cg=[math.fsum(r['native_mass_kg']*r['native_centroid_m'][i] for r in rows)/mass for i in range(3)]
    if not math.isclose(mass,value['modelled_material_mass_kg'],rel_tol=1e-7):raise ValueError('native candidate module mass differs')
    return dict(configuration_sha256=value['configuration_sha256'],module_mass_kg=mass,module_centroid_m=cg,parts=rows,
        scope='Native BRep volume/centroid times source effective density; tessellation independently checked for topology, source surfaces, bounds, signed volume/centroid.1% tessellation volume tolerance; BRep remains1e-7. No measured density, complete train inertia or physical acceptance.',**platform.FLAGS)


def _native_geometry(output,value):
    """Retain exact existing CAD/STEP when definition/exporter bytes agree.

    New geometry is generated in an isolated temporary folder. The media-only
    upgrade does not rewrite genuine same-input native files or claim a new
    physical/native execution from an old boolean.
    """
    import shutil,tempfile
    expected=platform.encoded(value);names={'model.FCStd','model.step.gz','native-mesh.json.gz'}
    if all((output/name).is_file() and not (output/name).is_symlink() for name in names|{'definition.json','native-cad.json'}):
        r=json.loads((output/'native-cad.json').read_bytes())
        same=(output/'definition.json').read_bytes()==expected and r.get('input_sha256')==sha256(expected).hexdigest() and r.get('exporter_sha256')==sha(Path(native.__file__)) and r.get('geometry_helpers_sha256')==sha(Path(models.__file__))
        if same:
            if set(r['files_sha256'])!=names or any(sha(output/name)!=r['files_sha256'][name] for name in names) or not r.get('fcstd_reopened') or not r.get('step_reopened'):raise ValueError('retained native candidate geometry provenance differs')
            with gzip.open(output/'model.step.gz','rb') as stream:raw=stream.read(128*1024*1024+1)
            if len(raw)>128*1024*1024 or sha256(raw).hexdigest()!=r['step_uncompressed_sha256']:raise ValueError('retained STEP payload differs')
            with gzip.open(output/'native-mesh.json.gz','rb') as stream:raw=stream.read(128*1024*1024+1)
            if len(raw)>128*1024*1024:raise ValueError('retained candidate mesh expansion exceeds bound')
            mesh=json.loads(raw);properties(value,r,mesh)
            return r,True
    work=ROOT/'build/candidate-native-export';work.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='fresh-',dir=work) as temporary:
        temporary=Path(temporary);(temporary/'definition.json').write_bytes(expected);r=native.generate(temporary/'definition.json',temporary,ROOT);raw=(temporary/'model.step').read_bytes();(temporary/'model.step.gz').write_bytes(gzip.compress(raw,mtime=0));r['files_sha256'].pop('model.step');r['files_sha256']['model.step.gz']=sha(temporary/'model.step.gz');r['step_uncompressed_sha256']=sha256(raw).hexdigest()
        for name in names:shutil.copyfile(temporary/name,output/name)
        (output/'definition.json').write_bytes(expected);(output/'native-cad.json').write_bytes(platform.encoded(r))
    return r,False


def publish(output=OUTPUT):
    before=sources();output=Path(output)
    if output.is_symlink():raise ValueError('ordinary native candidate packet required')
    output.mkdir(parents=True,exist_ok=True)
    if set(p.name for p in output.iterdir())-FILES-{'manifest.json'} or any(p.is_symlink() for p in output.iterdir()):raise ValueError('owned native candidate inventory required')
    value=definition();r,reused=_native_geometry(output,value)
    mesh=json.loads(gzip.decompress((output/'native-mesh.json.gz').read_bytes()));props=properties(value,r,mesh);(output/'geometry-properties.json').write_bytes(platform.encoded(props));media.native_views(output)
    (output/'README.md').write_text('# Exact candidate native module\n\nFreeCAD and STEP occupied volumes/centroids recover the same module mass from declared densities. Existing exact same-definition CAD/STEP and their reopen receipts are retained unchanged when their exporter/source hashes agree.\n\nRetained native triangles are independently checked for finite nonempty closed oriented topology, exact source/void surface membership, bounds, signed volume and centroid. Tessellation volume tolerance is1%; BRep remains1e-7. The deterministic orthographic image is checked pixel-for-pixel in its geometry viewport. All96 decoded frames of the four-second/four-stage video are checked against native geometry masks/material colours; fonts and encoder bytes are excluded from semantic matching.\n\nThe clip is final-position part visibility, not motion, collision, lifting or assembly-procedure simulation. Complete wire routing, cooling, connectors, fit and physical qualification remain open. No manufacturing or physical release is claimed.\n\n[Image](overview.png) · [Assembly visibility video](assembly-visibility.mp4) · [FreeCAD](model.FCStd) · [STEP](model.step.gz) · [Geometry audit](geometry-properties.json)\n')
    if before!=sources():raise ValueError('native candidate sources changed during export')
    m=dict(schema=SCHEMA,configuration_sha256=value['configuration_sha256'],source_sha256=before,files_sha256={n:sha(output/n) for n in FILES},movie=station_native._probe(output/'assembly-visibility.mp4'),native_geometry_reused_unmodified=reused,**platform.FLAGS);(output/'manifest.json').write_bytes(platform.encoded(m));return verify(output)


def verify(output=OUTPUT):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes())
    if m.get('schema')!=SCHEMA or m['source_sha256']!=sources() or set(m['files_sha256'])!=FILES or set(p.name for p in output.iterdir())!=FILES|{'manifest.json'}:raise ValueError('native candidate source/inventory differs')
    if any(m.get(k) is not False for k in platform.FLAGS):raise ValueError('native CAD cannot release candidate')
    for n,h in m['files_sha256'].items():
        if (output/n).is_symlink() or not (output/n).is_file() or (output/n).stat().st_size>64*1024*1024 or sha(output/n)!=h:raise ValueError('native candidate bytes altered')
    value=json.loads((output/'definition.json').read_bytes());r=json.loads((output/'native-cad.json').read_bytes());visual=json.loads((output/'visual-receipt.json').read_bytes())
    if r.get('physical_release') is not False or visual.get('physical_release') is not False or r.get('exporter_sha256')!=sha(Path(native.__file__)) or r.get('geometry_helpers_sha256')!=sha(Path(models.__file__)):raise ValueError('candidate native exporter/release provenance differs')
    with gzip.open(output/'native-mesh.json.gz','rb') as stream:raw=stream.read(128*1024*1024+1)
    if len(raw)>128*1024*1024:raise ValueError('candidate mesh expansion exceeds bound')
    mesh=json.loads(raw);props=properties(value,r,mesh)
    if mesh.get('schema')!='osr-native-tessellation/1' or mesh.get('input_sha256')!=sha(output/'definition.json') or mesh.get('physical_release')is not False:raise ValueError('native candidate tessellation provenance differs')
    if value!=definition() or json.loads((output/'geometry-properties.json').read_bytes())!=props or not r['fcstd_reopened'] or not r['step_reopened'] or r['input_sha256']!=sha(output/'definition.json'):raise ValueError('native candidate geometry/reopen differs')
    if any(sha(output/n)!=h for record in (r,visual) for n,h in record['files_sha256'].items()):raise ValueError('nested candidate native provenance differs')
    if visual['definition_sha256']!=sha(output/'definition.json') or visual['mesh_sha256']!=sha(output/'native-mesh.json.gz') or visual['renderer_sha256']!=sha(Path(media.__file__)) or visual['stages']!=value['construction_stages']:raise ValueError('candidate native media provenance differs')
    media.verify_views(output,value,mesh)
    if station_native._probe(output/'assembly-visibility.mp4')!=m['movie']:raise ValueError('candidate assembly video metadata differs')
    return m


def read_summary(output=OUTPUT):
    verify(output);p=json.loads((Path(output)/'geometry-properties.json').read_bytes())
    return dict(configuration_sha256=p['configuration_sha256'],module_mass_kg=p['module_mass_kg'],native_parts=len(p['parts']),native_reopened=True,actual_mesh_topology_geometry_verified=True,semantic_media_verified=True,decoded_visibility_frames=96,assembly_visibility_only=True,**platform.FLAGS)
