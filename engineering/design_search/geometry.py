"""Rigid stock placement, material collision witnesses and conservative motion.

OBBs include drilled voids and cylinder corners, so their overlap alone never
proves material interference. Continuous separation applies only to the declared
linear-translation/shortest-geodesic path between the supplied samples.
"""
from itertools import combinations,product
import math
import numpy as np

EPS=1e-10


def _numeric(value):
    return isinstance(value,(int,float,np.integer,np.floating)) and not isinstance(value,(bool,np.bool_)) and math.isfinite(value)


def _vector(value,name):
    a=np.asarray(value,dtype=float)
    if a.shape!=(3,) or not np.isfinite(a).all():raise ValueError('finite3-vector required: '+name)
    return a


def rigid_transform(rotation_matrix=None,translation_m=None):
    R=np.eye(3) if rotation_matrix is None else np.asarray(rotation_matrix,dtype=float)
    t=np.zeros(3) if translation_m is None else _vector(translation_m,'translation')
    if (R.shape!=(3,3) or not np.isfinite(R).all() or not np.allclose(R.T@R,np.eye(3),rtol=0,atol=1e-10)
            or not math.isclose(float(np.linalg.det(R)),1.,rel_tol=0,abs_tol=1e-10)):
        raise ValueError('finite proper orthonormal rotation required')
    return dict(rotation_matrix=R.tolist(),translation_m=t.tolist())


def _transform(value):
    if value is None:return rigid_transform()
    if not isinstance(value,dict) or set(value)-{'rotation_matrix','translation_m','time_s'}:raise ValueError('explicit rigid rotation/translation required')
    return rigid_transform(value.get('rotation_matrix'),value.get('translation_m'))


def compose_transform(parent,child):
    p,c=_transform(parent),_transform(child);R=np.asarray(p['rotation_matrix']);Q=np.asarray(c['rotation_matrix'])
    return rigid_transform(R@Q,R@np.asarray(c['translation_m'])+p['translation_m'])


def _placement(part,transform=None):return compose_transform(transform,part.get('rigid_transform'))


def _local_bounds(part):
    if not isinstance(part,dict) or part.get('kind') not in {'box','cylinder'}:raise ValueError('bounded box or cylinder stock required')
    at=_vector(part['at_m'],'primitive origin');size=_vector(part['size_m'],'primitive size')
    if np.any(size<=0):raise ValueError('positive primitive dimensions required')
    if part['kind']=='cylinder':
        if part.get('cylinder_axis','z') not in ('x','y','z'):raise ValueError('cylinder axis required')
        axis='xyz'.index(part.get('cylinder_axis','z'));diameter=size[0];length=size[2]
        size=np.full(3,diameter);size[axis]=length
    return at,at+size


def _corners(lo,hi):return np.asarray(list(product(*zip(lo,hi))),dtype=float)


def transformed_bounds(part,transform=None):
    lo,hi=_local_bounds(part);pose=_placement(part,transform)
    world=_corners(lo,hi)@np.asarray(pose['rotation_matrix']).T+pose['translation_m']
    return world.min(axis=0),world.max(axis=0)


def _obb(part,transform=None,padding=0.):
    lo,hi=_local_bounds(part);pose=_placement(part,transform);R=np.asarray(pose['rotation_matrix'])
    return R@((lo+hi)/2)+pose['translation_m'],R,(hi-lo)/2+padding


def obb_overlap(first,second,first_transform=None,second_transform=None,clearance_m=0.):
    if type(clearance_m) not in (int,float) or not math.isfinite(clearance_m) or clearance_m<0:raise ValueError('finite nonnegative clearance required')
    a,A,ha=_obb(first,first_transform,clearance_m/2);b,B,hb=_obb(second,second_transform,clearance_m/2)
    for axis in [*A.T,*B.T,*[np.cross(x,y) for x in A.T for y in B.T]]:
        norm=float(np.linalg.norm(axis))
        if norm<1e-12:continue
        axis=axis/norm;extent=float(np.abs(axis@A)@ha+np.abs(axis@B)@hb)
        if abs(float(axis@(b-a)))>=extent-EPS:return False
    return True


def _prepared_material(part,transform=None):
    lo,hi=_local_bounds(part);pose=_placement(part,transform);holes=[]
    for hole in part.get('holes',[]):
        if hole.get('axis','z') not in ('x','y','z'):raise ValueError('drill axis required')
        axis='xyz'.index(hole.get('axis','z'));cross=[i for i in range(3) if i!=axis]
        diameter=hole['diameter_m'];length=hole.get('length_m',hi[axis]-lo[axis]);start=lo[axis]+hole.get('start_m',0.)
        offsets=[hole['xyz'[i]+'_m'] for i in cross]
        if not all(_numeric(x) for x in [diameter,length,start,*offsets]) or diameter<=0 or length<=0:raise ValueError('finite positive drilled dimensions/location required')
        holes.append((axis,cross,start,start+length,[lo[i]+offset for i,offset in zip(cross,offsets)],diameter/2))
    cylinder_axis='xyz'.index(part.get('cylinder_axis','z')) if part['kind']=='cylinder' else None
    return lo,hi,np.asarray(pose['rotation_matrix']).T,np.asarray(pose['translation_m']),holes,cylinder_axis


def _contains(point,prepared,margin):
    lo,hi,R,t,holes,cylinder_axis=prepared;p=R@(np.asarray(point)-t)
    if np.any(p<=lo+margin) or np.any(p>=hi-margin):return False
    if cylinder_axis is not None:
        cross=[i for i in range(3) if i!=cylinder_axis];centre=(lo+hi)/2;radius=(hi[cross[0]]-lo[cross[0]])/2
        if sum((p[i]-centre[i])**2 for i in cross)>=(radius-margin)**2:return False
    for axis,cross,start,end,centre,radius in holes:
        if start-margin<=p[axis]<=end+margin and sum((p[i]-q)**2 for i,q in zip(cross,centre))<(radius+margin)**2:return False
    return True


def inside_material(point,part,transform=None,interior_margin_m=0.):
    if not _numeric(interior_margin_m) or interior_margin_m<0:raise ValueError('nonnegative material interior margin required')
    return _contains(_vector(point,'material point'),_prepared_material(part,transform),interior_margin_m)


def _intersection_vertices(first,second,first_transform,second_transform):
    Rfirst=np.asarray(_placement(first,first_transform)['rotation_matrix']);Rsecond=np.asarray(_placement(second,second_transform)['rotation_matrix'])
    if all(np.allclose(np.max(abs(R),axis=0),1.,rtol=0.,atol=1e-12) for R in (Rfirst,Rsecond)):
        alo,ahi=transformed_bounds(first,first_transform);blo,bhi=transformed_bounds(second,second_transform)
        return list(_corners(np.maximum(alo,blo),np.minimum(ahi,bhi)))
    normals=[];bounds=[]
    for part,transform in ((first,first_transform),(second,second_transform)):
        centre,R,half=_obb(part,transform)
        for i,axis in enumerate(R.T):
            for sign in (-1,1):normals.append(sign*axis);bounds.append(float(sign*axis@centre+half[i]))
    N=np.asarray(normals);b=np.asarray(bounds);vertices=[]
    for indices in combinations(range(12),3):
        matrix=N[list(indices)]
        if abs(float(np.linalg.det(matrix)))<1e-12:continue
        point=np.linalg.solve(matrix,b[list(indices)])
        if np.all(N@point<=b+EPS):vertices.append(point)
    return vertices


def collision_witness(first,second,first_transform=None,second_transform=None):
    """A point in both actual materials, or None without clearance credit."""
    if not obb_overlap(first,second,first_transform,second_transform):return None
    alo,ahi=transformed_bounds(first,first_transform);blo,bhi=transformed_bounds(second,second_transform)
    lo,hi=np.maximum(alo,blo),np.minimum(ahi,bhi)
    prepared_first=_prepared_material(first,first_transform);prepared_second=_prepared_material(second,second_transform)
    fractions=product((.5,.1,.9,.3,.7),(.5,.1,.9),(.5,.1,.9))
    for xyz in fractions:
        point=lo+(hi-lo)*np.asarray(xyz)
        if _contains(point,prepared_first,EPS) and _contains(point,prepared_second,EPS):return dict(point_m=point.tolist(),overlap_bounds_m=[lo.tolist(),hi.tolist()])
    vertices=_intersection_vertices(first,second,first_transform,second_transform)
    if vertices:
        centre=np.mean(vertices,axis=0)
        for point in [centre,*[(1-f)*centre+f*v for f in (.25,.5,.75) for v in vertices]]:
            if _contains(point,prepared_first,EPS) and _contains(point,prepared_second,EPS):return dict(point_m=point.tolist(),overlap_bounds_m=[lo.tolist(),hi.tolist()])
    return None


def _angle(first,second):
    R=np.asarray(first['rotation_matrix']).T@np.asarray(second['rotation_matrix'])
    return math.acos(float(np.clip((np.trace(R)-1)/2,-1,1)))


def swept_clearance(moving_parts,fixed_parts,poses,*,max_translation_step_m=.05,max_rotation_step_rad=.02,clearance_m=0.,maximum_samples=10000):
    """Sample material and conservatively enclose each declared motion segment."""
    if (type(maximum_samples) is not int or not 1<=maximum_samples<=10000 or not isinstance(poses,(list,tuple))
            or not 1<=len(poses)<=maximum_samples):raise ValueError('bounded nonempty sampled rigid path required')
    if not moving_parts or not fixed_parts:raise ValueError('explicit nonempty moving and fixed stock required')
    for parts in (moving_parts,fixed_parts):
        ids=[p.get('id') for p in parts]
        if any(not isinstance(x,str) or not x for x in ids) or len(set(ids))!=len(ids):raise ValueError('unique named stock parts required')
    for x in (max_translation_step_m,max_rotation_step_rad):
        if type(x) not in (int,float) or not math.isfinite(x) or x<=0:raise ValueError('positive finite path resolution required')
    if max_rotation_step_rad>math.pi:raise ValueError('shortest rotation step cannot exceed pi')
    if type(clearance_m) not in (int,float) or not math.isfinite(clearance_m) or clearance_m<0:raise ValueError('finite nonnegative clearance required')
    samples=[_transform(p) for p in poses];timed=[p.get('time_s') for p in poses]
    if any(t is not None for t in timed):
        if not all(type(t) in (int,float) and math.isfinite(t) for t in timed) or any(b<=a for a,b in zip(timed,timed[1:])):raise ValueError('strictly increasing finite path times required')
    segments=[]
    for first,second in zip(samples,samples[1:]):
        delta=float(np.linalg.norm(np.asarray(second['translation_m'])-first['translation_m']));angle=_angle(first,second)
        if delta>max_translation_step_m+EPS or angle>max_rotation_step_rad+EPS:raise ValueError('path samples exceed declared translation/rotation resolution')
        segments.append((first,second,delta,angle))
    findings=[];unresolved_samples=0
    for index,pose in enumerate(samples):
        for moving in moving_parts:
            for fixed in fixed_parts:
                if not obb_overlap(moving,fixed,pose,None,clearance_m):continue
                witness=collision_witness(moving,fixed,pose)
                if witness:findings.append(dict(sample=index,first=moving['id'],second=fixed['id'],**witness))
                else:unresolved_samples+=1
    unresolved_segments=[]
    for index,(first,second,delta,angle) in enumerate(segments):
        for moving in moving_parts:
            lo,hi=_local_bounds(moving);base=_placement(moving)
            vertices=_corners(lo,hi)@np.asarray(base['rotation_matrix']).T+base['translation_m']
            radius=float(np.linalg.norm(vertices,axis=1).max());sag=radius*(1-math.cos(angle/2))
            low0,high0=transformed_bounds(moving,first);low1,high1=transformed_bounds(moving,second)
            low=np.minimum(low0,low1)-sag-clearance_m/2;high=np.maximum(high0,high1)+sag+clearance_m/2
            for fixed in fixed_parts:
                flo,fhi=transformed_bounds(fixed)
                if np.all(np.minimum(high,fhi+clearance_m/2)-np.maximum(low,flo-clearance_m/2)>-EPS):
                    unresolved_segments.append(dict(segment=index,first=moving['id'],second=fixed['id'],rotation_sagitta_bound_m=sag,swept_bounds_m=[low.tolist(),high.tolist()]))
    discrete=not findings and unresolved_samples==0;continuous=discrete and not unresolved_segments
    return dict(samples=len(samples),segments=len(segments),findings=findings,material_interference_count=len(findings),unresolved_sample_envelope_overlaps=unresolved_samples,
        unresolved_segment_enclosures=unresolved_segments,sampled_envelopes_clear=discrete,continuous_envelopes_separated=continuous,path_clearance_screen_pass=continuous,
        interpolation='linear-translation-shortest-geodesic-rotation',tolerance_m=clearance_m,clearance_qualified=False,
        scope='Conservative primitive OBB and intersample AABB enclosures; actual material witnesses prove collision, unresolved envelopes block clearance. Native tolerances, deformation and installed acceptance remain open.')
