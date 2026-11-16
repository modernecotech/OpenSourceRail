"""One-box exact STEP to named tet10 MED control; invoked in a bounded process."""
import argparse, gmsh, hashlib, json
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument('--step',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
p=args.output.resolve()
p.mkdir(parents=True,exist_ok=True)
gmsh.initialize()
gmsh.option.setNumber('General.Terminal',1)
gmsh.option.setNumber('General.NumThreads',1)
gmsh.option.setString('Geometry.OCCTargetUnit','M')
imported=gmsh.model.occ.importShapes(str(args.step.resolve()))
gmsh.model.occ.synchronize()
vols=gmsh.model.getEntities(3)
if len(vols)!=1:raise ValueError('One closed imported STEP solid required')
imported_name=gmsh.model.getEntityName(3,vols[0][1])
if 'assembly' not in imported_name:
    raise ValueError('Expected assembly product name absent from STEP import')
box=gmsh.model.occ.getBoundingBox(3,vols[0][1])
if any(abs(actual-expected)>2e-7 for actual,expected in zip(box,(0.,0.,0.,1.,.3,.2))):
    raise ValueError('Imported STEP bounds differ from declared one-box control')
if abs(gmsh.model.occ.getMass(3,vols[0][1])-.06)>1e-9:
    raise ValueError('Imported STEP volume differs from declared one-box control')
gmsh.model.addPhysicalGroup(3,[vols[0][1]],1)
gmsh.model.setPhysicalName(3,1,'BOX')
groups={}
for d,t in gmsh.model.getEntities(2):
    b=gmsh.model.occ.getBoundingBox(d,t)
    cx=gmsh.model.occ.getCenterOfMass(d,t)[0]
    if abs(cx)<1e-8:groups['FIXED']=t
    if abs(cx-1)<1e-8:groups['LOADED']=t
if len(groups)!=2:raise ValueError('Unique x end faces required: '+str(groups))
for i,(name,tag) in enumerate(groups.items(),2):
    gmsh.model.addPhysicalGroup(2,[tag],i)
    gmsh.model.setPhysicalName(2,i,name)
gmsh.option.setNumber('Mesh.MeshSizeMin',.1)
gmsh.option.setNumber('Mesh.MeshSizeMax',.1)
gmsh.model.mesh.generate(3)
gmsh.option.setNumber('Mesh.SecondOrderLinear',1)
gmsh.model.mesh.setOrder(2)
gmsh.write(str(p/'box.med'))
gmsh.write(str(p/'box.msh'))
print('ENTITIES',gmsh.model.getPhysicalGroups())
print('MESH',len(gmsh.model.mesh.getNodes()[0]),gmsh.model.mesh.getElements(3)[0])
import numpy as np
node_ids, xyz, _ = gmsh.model.mesh.getNodes()
coords = {int(node_ids[i]): np.asarray(xyz[3*i:3*i+3]) for i in range(len(node_ids))}
element_types, element_ids, connectivity = gmsh.model.mesh.getElements(3)
assert list(element_types) == [11]
tet = np.asarray(connectivity[0]).reshape(-1,10)
volumes = [float(abs(np.linalg.det(np.stack([coords[int(n)]-coords[int(e[0])] for n in e[1:4]])))/6) for e in tet]
quality = gmsh.model.mesh.getElementQualities(element_ids[0], 'minSJ')
summary = dict(step_volume_m3=float(gmsh.model.occ.getMass(3,vols[0][1])),
               step_sha256=hashlib.sha256(args.step.read_bytes()).hexdigest(),
               gmsh_python_sha256=hashlib.sha256(Path(gmsh.__file__).read_bytes()).hexdigest(),
               gmsh_library_sha256=hashlib.sha256(Path(gmsh.lib._name).read_bytes()).hexdigest(),
               gmsh_python_path=str(Path(gmsh.__file__).resolve()),
               gmsh_library_path=str(Path(gmsh.lib._name).resolve()),
               step_centroid_m=list(gmsh.model.occ.getCenterOfMass(3,vols[0][1])),
               step_bounds_m=list(box),
               imported_entity_name=imported_name,
               mesh_corner_tet_volume_m3=sum(volumes),
               min_scaled_jacobian=float(min(quality)),
               nodes=len(node_ids), tets=len(tet),
               fixed_triangles=len(gmsh.model.mesh.getElements(2,groups['FIXED'])[1][0]),
               loaded_triangles=len(gmsh.model.mesh.getElements(2,groups['LOADED'])[1][0]),
               gmsh_version=gmsh.__version__)
print('SUMMARY',summary)
(p/'mesh-summary.json').write_text(json.dumps(summary, sort_keys=True, indent=2)+'\n')
gmsh.finalize()
