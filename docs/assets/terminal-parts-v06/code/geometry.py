"""Independent expected material geometry from SEALED entities, no producers.

Analytic boxes/prisms/cylinders and contained CSG voids. A cylindrical cut is
subtracted only after proving its whole bounding cylinder lies in material and
does not overlap any other cut. Unproved intersections are a model-domain HOLD.
"""
from math import pi,sqrt,isfinite
from hashlib import sha256
from pathlib import Path
from copy import deepcopy
import json
EPS=1e-12
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False,selected_reference_changed=False,movement_authority=False)
I=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
class DomainError(ValueError):pass
def encoded(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def identity(x):return sha256(encoded(x)).hexdigest()
def digest(p):
    h=sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024**2),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def seal(x,key='evaluation_id'):
    x=dict(x);x.pop(key,None);x[key]=identity(x);return x
def check(x,key='evaluation_id'):
    if x[key]!=identity({k:v for k,v in x.items() if k!=key}):raise ValueError('Canonical identity differs: '+key)
    return x
def write(p,x):
    with Path(p).open('xb') as f:f.write(encoded(x))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def plus(a,b):return [x+y for x,y in zip(a,b)]
def vec(R,p):return [dot(r,p) for r in R]
def world(g,p):return plus(g['at_m'],vec(g['rotation'],p))
def local(g,p):return [sum(g['rotation'][i][j]*(p[i]-g['at_m'][i]) for i in range(3)) for j in range(3)]
def corners(b):return [[b[x][0],b[y][1],b[z][2]] for x in (0,1) for y in (0,1) for z in (0,1)]
def bbox(points):return [[min(p[k] for p in points) for k in range(3)],[max(p[k] for p in points) for k in range(3)]]
def separated(a,b):return max(max(a[0][k]-b[1][k],b[0][k]-a[1][k]) for k in range(3))
def polygon(poly):
    terms=[a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1])];s=sum(terms)
    if abs(s)<1e-20:raise DomainError('Positive polygon area required')
    c=[sum((a[k]+b[k])*v for a,b,v in zip(poly,poly[1:]+poly[:1],terms))/(3*s) for k in (0,1)]
    return abs(s)/2,c
def inpoly(P,poly):
    inside=False
    for A,B in zip(poly,poly[1:]+poly[:1]):
        u=[B[k]-A[k] for k in (0,1)];w=[P[k]-A[k] for k in (0,1)]
        if abs(u[0]*w[1]-u[1]*w[0])<=EPS*max(1.,sqrt(dot(u,u))) and all(min(A[k],B[k])-EPS<=P[k]<=max(A[k],B[k])+EPS for k in (0,1)):return True
        if (A[1]>P[1])!=(B[1]>P[1]) and P[0]<(B[0]-A[0])*(P[1]-A[1])/(B[1]-A[1])+A[0]:inside=not inside
    return inside
def edge_hits_open_rect(A,B,rect):
    lo=0.;hi=1.
    for k in (0,1):
        lower=rect[0][k]+EPS;upper=rect[1][k]-EPS;d=B[k]-A[k]
        if lower>=upper:return False
        if abs(d)<1e-30:
            if not lower<A[k]<upper:return False
        else:
            p=(lower-A[k])/d;q=(upper-A[k])/d;lo=max(lo,min(p,q));hi=min(hi,max(p,q))
    return lo<hi
def rect_in_poly(rect,poly):
    points=[[rect[x][0],rect[y][1]] for x in (0,1) for y in (0,1)]
    return all(inpoly(p,poly) for p in points) and not any(edge_hits_open_rect(A,B,rect) for A,B in zip(poly,poly[1:]+poly[:1]))
def as_csg(g):
    if g['kind']!='rhs':return g
    L,w,h=g['size_m'];t=g['wall_m']
    if min(L,w,h,t)<=0 or 2*t>=min(w,h):raise DomainError('Positive RHS wall required')
    return dict(kind='difference',outer=dict(kind='box',size_m=[L,w,h],at_m=g['at_m'],rotation=g['rotation']),void=dict(kind='box',size_m=[L,w-2*t,h-2*t],at_m=g['at_m'],rotation=g['rotation']))
def extrema(g):
    g=as_csg(g);k=g['kind']
    if k=='difference':return extrema(g['outer'])
    if k=='box':return [world(g,p) for p in corners([[-x/2 for x in g['size_m']],[x/2 for x in g['size_m']]])]
    if k=='profile-prism':return [world(g,[a,p[0],p[1]]) for a in (-g['length_m']/2,g['length_m']/2) for p in g['points_yz_m']]
    if k=='annulus':
        u=[g['rotation'][j][0] for j in range(3)];L=g['length_m'];r=g['outer_diameter_m']/2;out=[]
        for k in range(3):
            d=[(1. if j==k else 0.)-u[k]*u[j] for j in range(3)];norm=sqrt(dot(d,d))
            for sign in (-1,1):
                q=[sign*r*x/norm if norm>1e-15 else 0. for x in d];ax=sign*(1 if u[k]>=0 else -1)*L/2;out.append(plus(g['at_m'],[u[j]*ax+q[j] for j in range(3)]))
        return out
    raise DomainError('Unsupported material primitive '+k)
def inside(g,p):
    g=as_csg(g)
    if g['kind']=='box':return all(abs(q)<=s/2+EPS for q,s in zip(local(g,p),g['size_m']))
    if g['kind']=='profile-prism':q=local(g,p);return abs(q[0])<=g['length_m']/2+EPS and inpoly(q[1:],g['points_yz_m'])
    raise DomainError('Void containment proof only supports box/profile prisms')
def contains_box(g,b):
    g=as_csg(g);k=g['kind']
    if k=='difference':return contains_box(g['outer'],b) and separated(b,bbox(extrema(g['void'])))>=-EPS
    pts=[local(g,p) for p in corners(b)];q=bbox(pts)
    if k=='box':return all(q[0][j]>=-g['size_m'][j]/2-EPS and q[1][j]<=g['size_m'][j]/2+EPS for j in range(3))
    if k=='profile-prism':return q[0][0]>=-g['length_m']/2-EPS and q[1][0]<=g['length_m']/2+EPS and rect_in_poly([[q[0][1],q[0][2]],[q[1][1],q[1][2]]],g['points_yz_m'])
    return False
def stock(g):
    g=as_csg(g);k=g['kind']
    if k=='difference':
        a=stock(g['outer']);v=stock(g['void'])
        if not all(inside(g['outer'],p) for p in extrema(g['void'])):raise DomainError('CSG void containment unsupported')
        V=a['volume_m3']-v['volume_m3']
        if V<=0:raise DomainError('CSG removed all material')
        C=[(a['volume_m3']*a['centroid_m'][j]-v['volume_m3']*v['centroid_m'][j])/V for j in range(3)]
    elif k=='box':V=g['size_m'][0]*g['size_m'][1]*g['size_m'][2];C=g['at_m']
    elif k=='profile-prism':A,c=polygon(g['points_yz_m']);V=A*g['length_m'];C=world(g,[0,*c])
    elif k=='annulus':V=pi/4*(g['outer_diameter_m']**2-g['inner_diameter_m']**2)*g['length_m'];C=g['at_m']
    else:raise DomainError('Unsupported primitive '+k)
    return dict(volume_m3=V,centroid_m=C,bounds_m=bbox(extrema(g)))
def holebox(h):
    a=h['axis'];L=h['length_m'];r=h['diameter_m']/2;C=[h['at_m'][j]+a[j]*L/2 for j in range(3)];E=[abs(a[j])*L/2+r*sqrt(max(0,1-a[j]*a[j])) for j in range(3)]
    return [[C[j]-E[j] for j in range(3)],[C[j]+E[j] for j in range(3)]]
def hole_contains_point(h,p):
    d=[p[j]-h['at_m'][j] for j in range(3)];s=dot(d,h['axis']);rad=sqrt(sum((d[j]-s*h['axis'][j])**2 for j in range(3)))
    return EPS<s<h['length_m']-EPS and rad<h['diameter_m']/2-EPS
def disjoint_holes(a,b):
    if abs(abs(dot(a['axis'],b['axis']))-1)<1e-12:
        d=[b['at_m'][j]-a['at_m'][j] for j in range(3)];z=dot(d,a['axis']);rad=sqrt(sum((d[j]-z*a['axis'][j])**2 for j in range(3)));end=z+dot(a['axis'],b['axis'])*b['length_m'];overlap=min(a['length_m'],max(z,end))-max(0.,min(z,end))
        return overlap<=EPS or rad>=(a['diameter_m']+b['diameter_m'])/2-EPS
    return separated(holebox(a),holebox(b))>=-EPS
def expected(g,holes):
    s=stock(g);V=s['volume_m3'];M=[V*x for x in s['centroid_m']];cut=0.
    for i,h in enumerate(holes):
        if not contains_box(g,holebox(h)):raise DomainError('Full cylindrical cut containment not established')
        if any(not disjoint_holes(h,q) for q in holes[:i]):raise DomainError('Overlapping cutter volumes cannot be subtracted twice')
        v=pi/4*h['diameter_m']**2*h['length_m'];C=[h['at_m'][j]+h['axis'][j]*h['length_m']/2 for j in range(3)];cut+=v;M=[M[j]-v*C[j] for j in range(3)]
    verts=extrema(g);remaining=[p for p in verts if not any(hole_contains_point(h,p) for h in holes)]
    if any(abs(a-b)>EPS for A,B in zip(bbox(remaining),s['bounds_m']) for a,b in zip(A,B)):raise DomainError('Machining may change extrema; unsupported bounds')
    V-=cut
    if V<=0:raise DomainError('Positive machined material required')
    return dict(volume_m3=V,centroid_m=[x/V for x in M],bounds_m=s['bounds_m'],full_cylinder_removed_m3=cut,intersection_domain='Entire cutter conservatively contained in material; pairwise cut volumes disjoint',threads='Pilot cylinders only; nominal thread forms remain pending')
def extract_entities(record,eligible):
    es={e['id']:e for e in record['entities']};primitives=[];parts=[]
    for parent in eligible:
        e=es[parent]
        if e['geometry'] is None:raise ValueError('Unknown part cannot enter native input')
        pieces=e['geometry'].get('pieces') if e['geometry']['kind']=='union-material' else [e['geometry']]
        routed=[[] for _ in pieces]
        for h in e['holes']:
            hits=[j for j,p in enumerate(pieces) if contains_box(p,holebox(h))]
            if len(hits)!=1:raise DomainError('Unambiguous cut-to-material-primitive routing required')
            routed[hits[0]].append(h)
        ids=[]
        for j,g in enumerate(pieces):
            name='TN'+str(len(primitives)).zfill(3);pid=parent+'::'+str(j);ids.append(pid)
            primitives.append(dict(id=pid,parent_entity_id=parent,native_body_id=name,geometry=deepcopy(g),holes=deepcopy(routed[j]),expected=expected(g,routed[j]),source_entity_sha256=identity(e)))
        parts.append(dict(id=parent,primitive_ids=ids,volume_m3=sum(p['expected']['volume_m3'] for p in primitives if p['parent_entity_id']==parent),compound_fusion_claim=False))
    return primitives,parts
