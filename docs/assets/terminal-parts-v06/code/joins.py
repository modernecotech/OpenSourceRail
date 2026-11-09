"""Numerical join serialization only. Never replaces a physical definition.

No distance/engineering tolerance: one adjacent float step, checked in BOTH SI
and native mm, and an exact source-bound construction witness is required for
nonzero edges. Unregistered finite near-zero edges HOLD rather than coarsen.
"""
from fractions import Fraction as F
from math import ulp,isfinite
from copy import deepcopy
from geometry import identity,DomainError,bbox
def exact_metrics(points):
    q=[[F(x) for x in p] for p in points];terms=[a[0]*b[1]-b[0]*a[1] for a,b in zip(q,q[1:]+q[:1])];twice=sum(terms)
    if not twice:raise DomainError('Zero area polygon is not a numerical join')
    c=[sum((a[j]+b[j])*v for a,b,v in zip(q,q[1:]+q[:1],terms))/(3*twice) for j in (0,1)]
    return twice/2,c,[[min(p[j] for p in q) for j in (0,1)],[max(p[j] for p in q) for j in (0,1)]]
def fraction(v):return dict(numerator=str(v.numerator),denominator=str(v.denominator),float_value=float(v))
def near(a,b):return all(abs(x-y)<=max(ulp(x),ulp(y)) for x,y in zip(a,b))
def normalize(points,allowed=(),*,witness=None):
    original=deepcopy(points)
    if len(points)<3 or any(len(p)!=2 or any(type(x) not in (int,float) or not isfinite(x) for x in p) for p in points):raise DomainError('Finite 2D polygon required')
    if len(points)>4096:raise DomainError('Bounded literal profile required')
    allowed={tuple(p) for p in allowed};keep=[];events=[];bounds=F(0)
    for i,p in enumerate(points):
        if keep:
            j,a=keep[-1];same=a==p
            # Underflow in serialization is not permission to delete material.
            si=near(a,p);native=near([x*1000 for x in a],[x*1000 for x in p])
            if same or si or a!=p and [x*1000 for x in a]==[x*1000 for x in p]:
                if not same and ((j,i) not in allowed or witness is None or not si or not native):raise DomainError('Unsupported finite tiny feature/curve join; no blanket coarsening')
                c=points[(i+1)%len(points)];dy=F(p[0])-F(a[0]);dz=F(p[1])-F(a[1]);cy=F(c[0])-F(a[0]);cz=F(c[1])-F(a[1]);area_bound=(abs(dy)*abs(cz)+abs(dz)*abs(cy))/2;bounds+=area_bound
                events.append(dict(kind='exact-adjacent-duplicate' if same else 'source-bound-one-ULP-curve-join',kept_original_index=j,removed_original_index=i,kept_point_yz_m=a,removed_point_yz_m=p,source_delta_m=[p[k]-a[k] for k in (0,1)],coordinate_ULP_bound_m=[max(ulp(x),ulp(y)) for x,y in zip(a,p)],native_kept_point_mm=[x*1000 for x in a],native_removed_point_mm=[x*1000 for x in p],coordinate_ULP_bound_mm=[max(ulp(x*1000),ulp(y*1000)) for x,y in zip(a,p)],local_area_change_bound_m2=fraction(area_bound),construction_witness=witness if not same else None))
                continue
        keep.append((i,deepcopy(p)))
    # Closed marker is not a finite segment; other repeated vertices are held.
    if len(keep)>3 and keep[-1][1]==keep[0][1]:
        i,p=keep.pop();events.append(dict(kind='explicit-exact-closing-marker',kept_original_index=keep[0][0],removed_original_index=i,kept_point_yz_m=keep[0][1],removed_point_yz_m=p,source_delta_m=[0.,0.]))
    new=[p for i,p in keep]
    if len(new)<3 or len({tuple(p) for p in new})!=len(new):raise DomainError('Nonconsecutive repeated vertex/self-touch is not normalized')
    if near(new[-1],new[0]):raise DomainError('Unsupported finite near-zero closing feature; no circular coarsening')
    a,c,b=exact_metrics(original);na,nc,nb=exact_metrics(new)
    if a*na<=0 or abs(na-a)>bounds:raise DomainError('Exact area residual exceeds ULP-derived local join bound')
    report=dict(original_vertices_yz_m=original,serialized_vertices_yz_m=new,kept_original_indices=[i for i,p in keep],events=events,vertices_moved=0,exact_signed_area_before_m2=fraction(a),exact_signed_area_after_m2=fraction(na),exact_signed_area_residual_m2=fraction(na-a),exact_area_residual_bound_m2=fraction(bounds),exact_centroid_before_m=[fraction(x) for x in c],exact_centroid_after_m=[fraction(x) for x in nc],exact_centroid_residual_m=[fraction(y-x) for x,y in zip(c,nc)],exact_bounds_before_m=[[fraction(x) for x in p] for p in b],exact_bounds_after_m=[[fraction(x) for x in p] for p in nb],exact_bounds_residual_m=[[fraction(y-x) for x,y in zip(p,q)] for p,q in zip(b,nb)],physical_source_unchanged=True,dimensional_tolerance_relaxed=False)
    return new,report
def primitive(p,spec,registry):
    g=deepcopy(p['geometry']);reports=[]
    matches=[r for r in registry['entries'] if r['primitive_id']==p['id'] and r['source_geometry_evaluation_id']==spec['source_geometry_evaluation_id']]
    if len(matches)>1:raise DomainError('Ambiguous join construction witness')
    r=matches[0] if matches else None
    if r and (r['source_entity_sha256']!=p['source_entity_sha256'] or r['geometry_sha256']!=identity(g) or g.get('ideal_geometry',{}).get('kind')!=r['ideal_geometry_kind'] or len(g.get('points_yz_m',[]))!=r['original_vertex_count'] or g['points_yz_m'][1]!=r['source_anchor_yz_m']):raise DomainError('Exact join source/anchor witness differs')
    def visit(v,path):
        if v['kind']=='difference':visit(v['outer'],path+'/outer');visit(v['void'],path+'/void')
        elif v['kind']=='profile-prism':
            new,record=normalize(v['points_yz_m'],r['allowed_adjacent_curve_join_pairs'] if r and path=='geometry' else (),witness=r if r and path=='geometry' else None);v['points_yz_m']=new
            reports.append(dict(primitive_id=p['id'],native_body_id=p['native_body_id'],geometry_path=path,**record))
    visit(g,'geometry');return g,reports
