"""Bounded, one-solid STEP to named tet10 MED candidate component mesh."""
import argparse
import hashlib
import json
from pathlib import Path

import gmsh
import numpy as np


def close(actual, expected, *, relative=1e-6, absolute=2e-7):
    return abs(actual-expected) <= max(absolute, relative*abs(expected))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--request',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    request=json.loads(args.request.read_text())
    output=args.output.resolve()
    step=output/'assembly.step'
    expected=request['geometry']
    axis='xyz'.index(request['load_axis'])
    gmsh.initialize()
    try:
        gmsh.option.setNumber('General.Terminal',1)
        gmsh.option.setNumber('General.NumThreads',1)
        gmsh.option.setString('Geometry.OCCTargetUnit','M')
        gmsh.model.occ.importShapes(str(step))
        gmsh.model.occ.synchronize()
        volumes=gmsh.model.getEntities(3)
        if len(volumes)!=1:raise ValueError('One connected closed imported STEP solid required')
        tag=volumes[0][1]
        name=gmsh.model.getEntityName(3,tag)
        if expected['product_name'] not in name:
            raise ValueError('Expected STEP product name absent from imported solid')
        bounds=list(gmsh.model.occ.getBoundingBox(3,tag))
        reference=expected['bounds_m']['min']+expected['bounds_m']['max']
        if not all(close(a,b) for a,b in zip(bounds,reference)):
            raise ValueError('Imported STEP bounds differ from candidate definition')
        volume=float(gmsh.model.occ.getMass(3,tag))
        if not close(volume,expected['volume_m3'],relative=1e-5,absolute=1e-9):
            raise ValueError('Imported STEP volume differs from candidate definition')
        gmsh.model.addPhysicalGroup(3,[tag],1)
        gmsh.model.setPhysicalName(3,1,'SOLID')
        planes={side:reference[axis+3*side] for side in (0,1)}
        groups={}
        for label,side in (('FIXED',request['fixed_side']),('LOADED',request['loaded_side'])):
            plane=planes[side]
            faces=[]
            for dimension,face in gmsh.model.getEntities(2):
                box=gmsh.model.occ.getBoundingBox(dimension,face)
                if close(box[axis],plane,absolute=1e-7) and close(box[axis+3],plane,absolute=1e-7):
                    faces.append(face)
            if not faces:raise ValueError('Declared '+label+' end face absent')
            area=sum(gmsh.model.occ.getMass(2,face) for face in faces)
            if area<=0:raise ValueError('Nonpositive '+label+' face area')
            groups[label]=dict(tags=faces,area_m2=float(area))
            gmsh.model.addPhysicalGroup(2,faces,2 if label=='FIXED' else 3)
            gmsh.model.setPhysicalName(2,2 if label=='FIXED' else 3,label)
        mesh_size=request['mesh_size_m']
        gmsh.option.setNumber('Mesh.MeshSizeMin',mesh_size)
        gmsh.option.setNumber('Mesh.MeshSizeMax',mesh_size)
        gmsh.model.mesh.generate(3)
        gmsh.option.setNumber('Mesh.SecondOrderLinear',1)
        gmsh.model.mesh.setOrder(2)
        gmsh.write(str(output/'candidate.med'))
        gmsh.write(str(output/'candidate.msh'))
        ids,xyz,_=gmsh.model.mesh.getNodes()
        coords={int(ids[i]):np.asarray(xyz[3*i:3*i+3]) for i in range(len(ids))}
        kinds,elements,connectivity=gmsh.model.mesh.getElements(3)
        if list(kinds)!=[11]:raise ValueError('Only tet10 candidate solids admitted')
        tetra=np.asarray(connectivity[0]).reshape(-1,10)
        corner_volume=sum(float(abs(np.linalg.det(np.stack([coords[int(n)]-coords[int(e[0])] for n in e[1:4]])))/6) for e in tetra)
        quality=gmsh.model.mesh.getElementQualities(elements[0],'minSJ')
        if not len(quality) or not min(quality)>0:raise ValueError('Nonpositive tetra Jacobian')
        if not close(corner_volume,volume,relative=.015,absolute=1e-8):
            raise ValueError('Mesh corner volume differs from STEP solid')
        summary=dict(schema='osr-code-aster-candidate-mesh/1',step_sha256=hashlib.sha256(step.read_bytes()).hexdigest(),
            step_volume_m3=volume,step_bounds_m=bounds,step_centroid_m=list(gmsh.model.occ.getCenterOfMass(3,tag)),
            imported_entity_name=name,mesh_corner_tet_volume_m3=corner_volume,min_scaled_jacobian=float(min(quality)),
            node_count=len(ids),tet10_count=len(tetra),face_groups={label:dict(area_m2=record['area_m2'],
                triangle_count=sum(sum(len(v) for v in gmsh.model.mesh.getElements(2,face)[1]) for face in record['tags']))
                for label,record in groups.items()},gmsh_version=gmsh.__version__,
            gmsh_python_path=str(Path(gmsh.__file__).resolve()),gmsh_library_path=str(Path(gmsh.lib._name).resolve()),
            gmsh_python_sha256=hashlib.sha256(Path(gmsh.__file__).read_bytes()).hexdigest(),
            gmsh_library_sha256=hashlib.sha256(Path(gmsh.lib._name).read_bytes()).hexdigest())
        (output/'mesh-summary.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n')
    finally:
        gmsh.finalize()


if __name__=='__main__':main()
