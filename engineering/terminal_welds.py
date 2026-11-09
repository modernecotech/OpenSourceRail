"""Finite terminal weld proposals with explicit source material contact faces.

Pure definition API, not an installed-body/native/WPS evaluator. It never picks
an orientation from a centreline or replaces an unknown parent with a box.
External and explicit existing-cavity right-angle fillets on declared box/RHS
faces are supported. Unresolved grooves, unknown parent CSG, touching void bounds or missing bindings
remain named holds. A positive flat runout is a physical revision, not a claim
that an interrupted seam supplies a required strength or weather seal.
"""
from copy import deepcopy
from hashlib import sha256
import json
from math import fsum,isfinite,sqrt
import re
import zlib

SOURCE={'candidate_id':'339689820cde417f85a426c5ac4dfee96fcdee9db6f69107776f17874caa878b','evaluation_id':'91a013cdd8cc6757b06769f963f75d52499cc58c2de1936c7cc52685aa7d9ec0','raw_sha256':'cdef7bfebda549f45a4e1c160c58b07f584c610782c56528c541bf8e43bcb82c'}
SOURCE_MODULE_SHA256='f1b83a2ee0c13e14b2bb72a321caab632f72ca14c2f6d7c728d0398c4cee43e9'
I=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
CASES=('low','base','high')
EPS=1e-10
FLAGS=dict(physical_accepted=False,engineering_accepted=False,canonical_admitted=False,native_eligible=False,installed_assembly_accepted=False,manufacturing_release=False,operating_release=False,selected_reference_changed=False)
# Source inventory183/9families/27patterns, not28. No actual source is generated.
PATTERNS=(('floor/boss/*/*/weld',30),('floor/hanger/*/cap-frame-weld',13),('floor/post-bottom/*/post-closure-weld',2),('floor/support/*/long-seams',15),('floor/support/*/root-end-weld',15),('post-clamp/*/*/front-web-weld',6),('post-clamp/*/*/rear-web-weld',6),('roof/fascia-underlap-seam',1),('roof/outrigger-fascia-joint/*',5),('roof/outrigger-weld/*',5),('roof/standoff-weld/*',5),('side-front-cap-root/*/stiffener-weld',2),('side-front-root/*/*/stiffener-weld',6),('side-front-root/*/*/weld',6),('side-outrigger/*/*/weld',6),('side-stiffener/*/*/front/long-seams',6),('side-stiffener/*/*/front/tab-weld',6),('side-stiffener/*/*/front/weld0',6),('side-stiffener/*/*/front/weld1',6),('side-stiffener/*/*/rear/long-seams',6),('side-stiffener/*/*/rear/tab-weld',6),('side-stiffener/*/*/rear/weld0',6),('side-stiffener/*/*/rear/weld1',6),('upper-frame/*/*/boss-weld',4),('upper/*/backbone-lug-seams/*',4),('upper/*/cap-backbone-weld',2),('upper/*/tie-lug-seams',2))

class DefinitionHold(ValueError):
    """Named unsupported source definition; never a zero-mass pass."""


def identity(x):return sha256((json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()
def seal(x):return dict(deepcopy(x),evaluation_id=identity(x))
def scalar(v,positive=False):
    if type(v) not in (int,float) or not isfinite(v) or (positive and v<=0):raise ValueError('Finite nonboolean SI scalar required')
    return float(v)
def vector(v):
    if not isinstance(v,(list,tuple)) or len(v)!=3:raise ValueError('Three explicit SI coordinates required')
    return [scalar(x) for x in v]
def name(v):
    if not isinstance(v,str) or not v or len(v)>256:raise ValueError('Explicit bounded identity required')
    return v
def digest(v):
    if not isinstance(v,str) or not re.fullmatch('[0-9a-f]{64}',v):raise ValueError('Exact SHA256 identity required')
    return v
def add(a,b):return [a[i]+b[i] for i in range(3)]
def sub(a,b):return [a[i]-b[i] for i in range(3)]
def scale(a,s):return [x*s for x in a]
def dot(a,b):return fsum(x*y for x,y in zip(a,b))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def norm(a):return sqrt(dot(a,a))
def unit(a):
    a=vector(a);d=norm(a)
    if d<1e-12:raise ValueError('Nonzero direction required')
    return scale(a,1/d)
def rotation(R):
    if not isinstance(R,list) or len(R)!=3:raise ValueError('Explicit proper frame required')
    for row in R:vector(row)
    if any(abs(fsum(R[k][i]*R[k][j] for k in range(3))-(i==j))>1e-10 for i in range(3) for j in range(3)) or abs(dot(R[0],cross(R[1],R[2]))-1)>1e-10:raise ValueError('Reflection/nonrigid frame refused')
    return R

def world(p,T,R):return [T[i]+dot(R[i],p) for i in range(3)]
def local(p,T,R):return [fsum(R[k][j]*(p[k]-T[k]) for k in range(3)) for j in range(3)]
def direction(p,R):return [dot(R[i],p) for i in range(3)]
def bounds(points):return [[min(p[k] for p in points),max(p[k] for p in points)] for k in range(3)]
def bounds_overlap(a,b):return all(min(a[k][1],b[k][1])-max(a[k][0],b[k][0])>EPS for k in range(3))
def bounds_may_touch(a,b):return all(min(a[k][1],b[k][1])-max(a[k][0],b[k][0])>=-EPS for k in range(3))

def pattern_for(eid):
    name(eid);matches=[p for p,_ in PATTERNS if re.fullmatch(re.escape(p).replace(r'\*',r'[^/]+'),eid)]
    if len(matches)!=1:raise DefinitionHold('source-weld-family-pattern-unsupported:'+eid)
    return matches[0]

def family_templates():
    """Structured requirements, not183 invented parent bindings or solids."""
    return seal(dict(schema='osr-terminal-weld-family-templates/1',source=deepcopy(SOURCE),weld_records=183,families=9,patterns=[dict(pattern=p,source_quantity=q,family=p.split('/')[0],supported_proposal='external orthogonal fillet with explicit source-face binding; prepared groove or unknown parent material remains held',required=['old source entity and stock hashes','one signed parent-face pair and offset per segment','positive explicit flat runout at both ends','same source material/density/rate/process policy','groove/bevel revision needs counted parent cut definition']) for p,q in PATTERNS],**FLAGS))


def _poly(vertices,faces):return dict(vertices=vertices,faces=faces)
def _box(lo,hi,T,R):
    vs=[world([hi[k] if bits&(1<<k) else lo[k] for k in range(3)],T,R) for bits in range(8)]
    return _poly(vs,[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)])
def _edges(poly):return [sub(poly['vertices'][b],poly['vertices'][a]) for face in poly['faces'] for a,b in zip(face,face[1:]+face[:1])]
def _normals(poly):return [cross(sub(poly['vertices'][f[1]],poly['vertices'][f[0]]),sub(poly['vertices'][f[2]],poly['vertices'][f[0]])) for f in poly['faces']]
def interiors_overlap(a,b):
    """Same convex SAT/EPS domain; public pair path computes its own bounds."""
    if not bounds_overlap(bounds(a['vertices']),bounds(b['vertices'])):return False
    return _interiors_overlap_sat(a,b)


def _interiors_overlap_sat(a,b):
    """Unchanged narrow phase; caller must first pass the exact AABB screen."""
    axes=_normals(a)+_normals(b)+[cross(e,f) for e in _edges(a) for f in _edges(b)]
    for axis in axes:
        length=norm(axis)
        if length<1e-18:continue
        axis=scale(axis,1/length);x=[dot(v,axis) for v in a['vertices']];y=[dot(v,axis) for v in b['vertices']]
        if min(max(x),max(y))-max(min(x),min(y))<=EPS:return False
    return True


def _filler_intersections(pieces):
    """Equivalent ordered filler pairs with one finite AABB per occurrence.

    Sweep along terminal U only as a necessary broad phase. Existing >EPS
    three-axis bounds and exact unchanged SAT remain the final predicate. Sort
    successful original indices to reproduce the prior nested-loop pair order;
    never deduplicate geometry/IDs or waive an intended contact. The full caller
    keeps its existing unique-occurrence check before this diagnostic.
    """
    boxes=[bounds(p['poly']['vertices']) for p in pieces]
    if any(not isfinite(x) for b in boxes for axis in b for x in axis):raise ValueError('Finite filler bounds required')
    ordered=sorted(range(len(pieces)),key=lambda i:(boxes[i][0][0],i));active=[];hits=[]
    for j in ordered:
        low=boxes[j][0][0]
        # With previous.low<=current.low, previous.high-current.low<=EPS
        # implies the original min(high)-max(low)<=EPS. No SAT hit is lost.
        active=[i for i in active if boxes[i][0][1]-low>EPS]
        for i in active:
            if bounds_overlap(boxes[i],boxes[j]) and _interiors_overlap_sat(pieces[i]['poly'],pieces[j]['poly']):hits.append((min(i,j),max(i,j)))
        active.append(j)
    hits.sort()
    return [[pieces[i]['id'],pieces[j]['id']] for i,j in hits]


def _parent(parent):
    """Only authenticated local box/RHS material; no filled allowance envelope."""
    pid=name(parent['id']);mat=name(parent['material_id']);T=vector(parent['at_m']);R=rotation(parent['rotation']);g=parent['geometry']
    if parent.get('frame')!='terminal-local-UVW':raise DefinitionHold('parent-frame-unsupported:'+pid)
    if parent.get('exact_CSG_entity') is not None or parent.get('physical_drawing') is not None:raise DefinitionHold('parent-finished-CSG-needs-independent-face-adapter:'+pid)
    if not isinstance(g,dict) or g.get('kind') not in ('box','rhs'):raise DefinitionHold('parent-material-domain-unsupported:'+pid)
    allowed={'kind','size_m','holes','finite_void_prisms','open_round_slot_voids'}|({'wall_m','corner_bevels'} if g['kind']=='rhs' else set())
    if set(g)-allowed:raise DefinitionHold('unconsumed-parent-geometry-fields:'+pid)
    size=vector(g['size_m'])
    if min(size)<1e-5:raise DefinitionHold('parent-dimension-below-10um-model-domain:'+pid)
    lo=scale(size,-.5);hi=scale(size,.5);cells=[]
    if g['kind']=='box':cells=[dict(id='solid',lo=lo,hi=hi)]
    else:
        t=scalar(g['wall_m'],True)
        if not 1e-5<=t<min(size[1:])/2:raise ValueError('Invalid RHS material wall')
        # Four disjoint plates, no corner material counted twice.
        for side,axis in [('y-',1),('y+',1),('z-',2),('z+',2)]:
            a=list(lo);b=list(hi)
            if axis==2:a[1]+=t;b[1]-=t
            if side[-1]=='-':b[axis]=a[axis]+t
            else:a[axis]=b[axis]-t
            cells.append(dict(id=side,lo=a,hi=b))
    voids=[];void_prisms=[]
    corner=g.get('corner_bevels')
    if corner is not None:
        if 'finite_void_prisms' in g or set(corner)!={'count','leg_m','length_m','separately_owned_filler'} or type(corner['count']) is not int or corner['count']!=4 or corner['separately_owned_filler'] is not True or abs(scalar(corner['length_m'],True)-size[0])>EPS:raise DefinitionHold('exact-source-corner-void-roster-required:'+pid)
        b=scalar(corner['leg_m'],True)
        if b>=g['wall_m']:raise DefinitionHold('source-corner-void-exceeds-one-source-sideplate:'+pid)
        for sy in (-1,1):
            for sz in (-1,1):
                y=sy*size[1]/2;z=sz*size[2]/2
                vs=[[x,yy,zz] for x in (-size[0]/2,size[0]/2) for yy,zz in [(y,z),(y-sy*b,z),(y,z-sz*b)]]
                void_prisms.append(dict(id='source-corner/'+str(sy)+'/'+str(sz),kind='triangular-prism',vertices_m=vs))
    for cut in g.get('finite_void_prisms',[]):
        if set(cut)!={'id','kind','vertices_m'} or cut['kind']!='triangular-prism':raise DefinitionHold('explicit-finite-void-prism-required:'+pid)
        name(cut['id']);vs=cut['vertices_m']
        if not isinstance(vs,list) or len(vs)!=6:raise ValueError('Six finite prism vertices required')
        vs=[vector(v) for v in vs];delta=sub(vs[3],vs[0]);normal=cross(sub(vs[1],vs[0]),sub(vs[2],vs[0]))
        if norm(normal)<1e-12 or abs(dot(normal,delta))<1e-15 or any(norm(sub(sub(vs[i+3],vs[i]),delta))>EPS for i in range(3)):raise ValueError('Nondegenerate translated triangular prism required')
        cb=bounds(vs)
        if any(cb[k][0]<lo[k]-EPS or cb[k][1]>hi[k]+EPS for k in range(3)):raise DefinitionHold('source-void-outside-owned-material:'+pid)
        if g['kind']=='rhs':
            inner=[[lo[0],hi[0]],[lo[1]+g['wall_m'],hi[1]-g['wall_m']],[lo[2]+g['wall_m'],hi[2]-g['wall_m']]]
            if bounds_overlap(cb,inner):raise DefinitionHold('source-void-union-with-RHS-cavity-needs-explicit-domain:'+pid)
        void_prisms.append(deepcopy(cut))
    if len({x['id'] for x in void_prisms})!=len(void_prisms):raise ValueError('Duplicate source void owner')
    for cut in void_prisms:
        vb=bounds([world(v,T,R) for v in cut['vertices_m']])
        if any(bounds_may_touch(vb,other) for other in voids):raise DefinitionHold('source-void-union-requires-explicit-disjoint-domain:'+pid)
        voids.append(vb)
    slots=g.get('open_round_slot_voids',[])
    if slots and g['kind']!='box':raise DefinitionHold('open-round-slot-material-provider-is-box-only')
    for slot in slots:
        if set(slot)!={'id','kind','U_centre_m','V_entry_face_m','face_sign','depth_m','W_open_m','W_round_centre_m','radius_m'} or slot['kind']!='open-round-ended-slot' or type(slot['face_sign']) is not int or slot['face_sign'] not in (-1,1):raise ValueError('Explicit source round-ended slot required')
        name(slot['id']);u=scalar(slot['U_centre_m']);entry=scalar(slot['V_entry_face_m']);depth=scalar(slot['depth_m'],True);bottom=scalar(slot['W_open_m']);centre=scalar(slot['W_round_centre_m']);r=scalar(slot['radius_m'],True);side=slot['face_sign']
        if abs(entry-side*size[1]/2)>EPS or abs(bottom+size[2]/2)>EPS or not 0<depth<size[1] or centre<=bottom or centre+r>=size[2]/2 or abs(u)+r>size[0]/2:raise DefinitionHold('contained-open-bottom-round-slot-domain')
        vr=sorted([entry,entry-side*depth]);vb=bounds(_box([u-r,vr[0],bottom],[u+r,vr[1],centre+r],T,R)['vertices'])
        if any(bounds_overlap(vb,old) for old in voids):raise DefinitionHold('slot-void-union-needs-explicit-disjoint-domain')
        voids.append(vb)
    for h in g.get('holes',[]):
        if set(h)!={'axis','centre_m','radius_m','length_m'} or type(h['axis']) is not int or h['axis'] not in (0,1,2):raise DefinitionHold('parent-bore-domain-unsupported:'+pid)
        c=vector(h['centre_m']);radius=scalar(h['radius_m'],True);L=scalar(h['length_m'],True);a=[c[k]-(L/2 if k==h['axis'] else radius) for k in range(3)];b=[c[k]+(L/2 if k==h['axis'] else radius) for k in range(3)]
        # This conservative cut bounding box is an exclusion, never a cylinder filled as material.
        hb=bounds(_box(a,b,T,R)['vertices'])
        if slots and any(bounds_overlap(hb,old) for old in voids):raise DefinitionHold('bore-slot-union-needs-explicit-disjoint-domain')
        voids.append(hb)
    physical=dict(id=pid,material_id=mat,geometry=deepcopy(g),at_m=T,rotation=deepcopy(R))
    if void_prisms:physical['finite_source_void_prisms']=deepcopy(void_prisms)
    return dict(id=pid,material_id=mat,T=T,R=R,source_hash=identity(parent),physical=physical,cells=cells,void_bounds=voids)


def _face(contact,parents):
    if set(contact)!={'parent_id','source_parent_sha256','cell_id','axis','sign'}:raise ValueError('Explicit source material face selector required')
    p=parents[name(contact['parent_id'])]
    if digest(contact['source_parent_sha256'])!=p['source_hash']:raise ValueError('Source parent epoch mismatch')
    if type(contact['axis']) is not int or contact['axis'] not in (0,1,2) or type(contact['sign']) is not int or contact['sign'] not in (-1,1):raise ValueError('Signed source face axis required')
    cell=next((c for c in p['cells'] if c['id']==contact['cell_id']),None);material_depth=None
    if contact['cell_id'] in ('outer-z-','outer-z+'):
        g=p['physical']['geometry'];sgn=-1 if contact['cell_id'].endswith('-') else 1
        if g['kind']!='rhs' or contact['axis']!=2 or contact['sign']!=sgn:raise ValueError('Explicit continuous RHS outerface required')
        size=g['size_m'];cell=dict(id=contact['cell_id'],lo=scale(size,-.5),hi=scale(size,.5));material_depth=g['wall_m']
    if cell is None:raise ValueError('Unknown parent material cell')
    axis=contact['axis'];sgn=contact['sign'];normal=[0.,0.,0.];normal[axis]=sgn
    return dict(parent=p,cell=cell,axis=axis,sign=sgn,plane=cell['hi' if sgn==1 else 'lo'][axis],normal=direction(normal,p['R']),material_depth_m=material_depth if material_depth is not None else cell['hi'][axis]-cell['lo'][axis])

def _on_face(points,face):
    for p in points:
        q=local(p,face['parent']['T'],face['parent']['R'])
        if abs(q[face['axis']]-face['plane'])>EPS:raise DefinitionHold('weld-root-or-toe-not-on-bound-contact-plane')
        if any(q[k]<face['cell']['lo'][k]-EPS or q[k]>face['cell']['hi'][k]+EPS for k in range(3) if k!=face['axis']):raise DefinitionHold('finite-contact-strip-exceeds-real-parent-face')

def _prism(p,q,a,b,leg):
    vertices=[p,add(p,scale(a,leg)),add(p,scale(b,leg)),q,add(q,scale(a,leg)),add(q,scale(b,leg))]
    V=leg*leg*norm(sub(q,p))/2;C=add(scale(add(p,q),.5),scale(add(a,b),leg/3))
    return dict(poly=_poly(vertices,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]),volume_m3=V,centroid_m=C,bounds_m=bounds(vertices))


def _policy(policy,material):
    m=policy['materials'][material]
    if not isinstance(m['density_bounds_kg_m3'],(list,tuple)) or len(m['density_bounds_kg_m3'])!=2:raise ValueError('Two explicit source density bounds required')
    rho=[scalar(m['density_bounds_kg_m3'][0],True),scalar(m['density_kg_m3'],True),scalar(m['density_bounds_kg_m3'][1],True)]
    rates=[scalar(v,True) for v in m['rate_USD_kg']];labour=[scalar(v,True) for v in policy['process']['labour_USD_h']];factor=scalar(policy['process']['weld_procurement_factor'],True)
    if len(rates)!=3 or len(labour)!=3 or rho!=sorted(rho) or rates!=sorted(rates) or labour!=sorted(labour) or factor<1:raise ValueError('Ordered complete source mass/rate/process cases required')
    return rho,rates,labour,factor


def define_record(entity,stock,assignment,parent_entities,policy):
    """Pure one-weld proposal. Bindings must resolve genuine source faces first.

    A source groove flag alone supplies no material. An explicit existing-cavity
    mode requires an actual inner RHS face; new preparations need separately
    counted revisions. No bevel is invented here.
    """
    old=deepcopy(entity);owner=deepcopy(stock);binding=deepcopy(assignment);pattern=pattern_for(old['id']);drawing=old.get('physical_drawing',{})
    if drawing.get('kind')!='triangular-weld-seams':raise DefinitionHold('source-weld-drawing-unsupported')
    if old.get('frame')!='terminal-local-UVW' or old.get('scope')!='installed':raise ValueError('Exact local installed weld frame required')
    if old['geometry'].get('kind')!='envelope':raise ValueError('Expected original unresolved weld allowance, not a silently revised solid')
    if set(binding)!={'source_entity_id','source_entity_sha256','source_stock_sha256','seams','parent_preparations','joint_domain'}:raise ValueError('Complete one-weld assignment required')
    if binding['source_entity_id']!=old['id'] or digest(binding['source_entity_sha256'])!=identity(old) or digest(binding['source_stock_sha256'])!=identity(owner):raise ValueError('Source weld/stock identity mismatch')
    if owner['entity_ids']!=[old['id']] or type(owner.get('quantity')) is not int or owner['quantity']!=1:raise ValueError('Original once-only weld stock owner required')
    if binding['parent_preparations']:raise DefinitionHold('counted-parent-groove-or-bevel-revision-required')
    if type(drawing.get('in_prepared_grooves')) is not bool or binding['joint_domain'] not in ('external-orthogonal-fillet','existing-source-cavity-fillet'):raise DefinitionHold('explicit-source-contact-domain-required')
    if drawing['in_prepared_grooves'] and binding['joint_domain']!='existing-source-cavity-fillet':raise DefinitionHold('counted-parent-groove-or-explicit-existing-cavity-required')
    leg=scalar(drawing['leg_m'],True)
    if leg<1e-5:raise DefinitionHold('leg-below-10um-model-domain')
    T=vector(old['at_m']);R=rotation(old['rotation']);paths=drawing['local_segments_m']
    if not isinstance(paths,list) or not 1<=len(paths)<=128:raise ValueError('Finite source seam roster required')
    if not isinstance(binding['seams'],list) or len(binding['seams'])!=len(paths):raise DefinitionHold('missing-segment-face-or-end-treatment-binding')
    indices=[s.get('source_segment_index') for s in binding['seams']]
    if any(type(i) is not int for i in indices) or sorted(indices)!=list(range(len(paths))):raise ValueError('Every source segment exactly once required')
    if len({p['id'] for p in parent_entities})!=len(parent_entities):raise ValueError('Duplicate source parent')
    parents={p['id']:_parent(p) for p in parent_entities}
    wanted={c['parent_id'] for s in binding['seams'] for c in s['contacts']}
    if set(parents)!=wanted:raise ValueError('Missing or unused parent bindings')
    mat=name(old['material_id']);rho,rates,labour,factor=_policy(policy,mat)
    # Same source Al family is a material hypothesis, never a welding procedure.
    if mat!='al5083' or any(p['material_id'] not in ('al5083','al5754','al6005a') for p in parents.values()):raise DefinitionHold('dissimilar-or-unknown-weld-material-route-required')
    original_length=0.;beads=[]
    for i,line in enumerate(paths):
        if not isinstance(line,list) or len(line)!=2:raise ValueError('Explicit source segment endpoints required')
        p,q=[world(vector(x),T,R) for x in line];length=norm(sub(q,p));original_length+=length
        if length<1e-5:raise ValueError('Nondegenerate source seam required')
        s=next(x for x in binding['seams'] if x['source_segment_index']==i)
        if set(s)!={'source_segment_index','root_offset_m','contacts','end_treatment'} or not isinstance(s['contacts'],list) or len(s['contacts'])!=2:raise ValueError('Explicit oriented seam/face pair required')
        if s['contacts'][0]['parent_id']==s['contacts'][1]['parent_id']:raise DefinitionHold('two-distinct-member-contacts-required')
        faces=[_face(c,parents) for c in s['contacts']]
        inner=[f for f in faces if f['parent']['physical']['geometry']['kind']=='rhs' and f['cell']['id'] in ('y-','y+','z-','z+') and f['axis']==(1 if f['cell']['id'][0]=='y' else 2) and f['sign']==(-1 if f['cell']['id'][1]=='+' else 1)]
        if (binding['joint_domain']=='existing-source-cavity-fillet')!=bool(inner):raise DefinitionHold('declared-cavity-domain-needs-an-actual-source-inner-wall-face')
        a,b=[f['normal'] for f in faces];tangent=unit(sub(q,p))
        if abs(dot(a,b))>1e-10 or abs(dot(a,tangent))>1e-10 or abs(dot(b,tangent))>1e-10:raise DefinitionHold('nonorthogonal-or-nonparallel-fillet-contact-domain')
        end=s['end_treatment']
        if set(end)!={'kind','trim_start_m','trim_end_m'} or end['kind']!='flat-positive-runout':raise DefinitionHold('explicit-positive-flat-runout-required; miter-not-supported')
        start=scalar(end['trim_start_m'],True);finish=scalar(end['trim_end_m'],True)
        if min(start,finish)<1e-6 or start+finish>=length-1e-5:raise DefinitionHold('invalid-runout-or-remaining-seam-domain')
        offset=vector(s['root_offset_m']);p=add(add(p,offset),scale(tangent,start));q=add(add(q,offset),scale(tangent,-finish))
        bead=_prism(p,q,a,b,leg)
        _on_face([p,q,add(p,scale(b,leg)),add(q,scale(b,leg))],faces[0]);_on_face([p,q,add(p,scale(a,leg)),add(q,scale(a,leg))],faces[1])
        for parent in parents.values():
            if any(interiors_overlap(bead['poly'],_box(c['lo'],c['hi'],parent['T'],parent['R'])) for c in parent['cells']):raise DefinitionHold('bead-overlaps-existing-parent-material:'+parent['id'])
            # Conservative refusal, not a claim that all cylindrical cuts are boxes.
            if any(bounds_may_touch(bead['bounds_m'],v) for v in parent['void_bounds']):raise DefinitionHold('bead-or-contact-near-source-bore-needs-exact-cut-check:'+parent['id'])
        beads.append(dict(id=old['id']+'/finite-bead/'+str(i),source_segment_index=i,root_offset_m=offset,end_treatment=deepcopy(end),contacts=deepcopy(s['contacts']),**bead))
    for i,a in enumerate(beads):
        for b in beads[i+1:]:
            if interiors_overlap(a['poly'],b['poly']):raise DefinitionHold('finite-bead-interior-overlap; revise-end-trimming-or-miter')
    oldV=.5*leg*leg*original_length
    if abs(scalar(owner['net_m3'],True)-oldV)>max(1e-14,oldV*1e-10) or abs(scalar(owner['gross_m3'],True)-oldV*factor)>max(1e-14,oldV*factor*1e-10):raise ValueError('Original weld volume/procurement ownership differs')
    ph=scalar(owner['process_h']);qh=scalar(owner['QA_h'])
    if min(ph,qh)<0 or ph+qh<=0:raise ValueError('Declared positive process/QA coverage required')
    for j,c in enumerate(CASES):
        expected=oldV*factor*rho[j]*rates[j]+(ph+qh)*labour[j]
        for field,amount in [('net_mass_kg',oldV*rho[j]),('gross_mass_kg',oldV*factor*rho[j]),('scrap_mass_kg',oldV*(factor-1)*rho[j])]:
            if set(owner[field])!=set(CASES) or abs(scalar(owner[field][c])-amount)>max(1e-12,amount*1e-9):raise ValueError('Source material/mass ownership differs')
        if set(owner['direct_cost_usd'])!=set(CASES) or abs(scalar(owner['direct_cost_usd'][c])-expected)>max(1e-8,expected*1e-9):raise ValueError('Original source cost basis differs; no silent price reassignment')
    V=fsum(b['volume_m3'] for b in beads);C=[fsum(b['volume_m3']*b['centroid_m'][k] for b in beads)/V for k in range(3)]
    physical=dict(schema='osr-terminal-finite-external-weld-physical/1',source_weld_id=old['id'],pattern=pattern,material_id=mat,frame='terminal-local-UVW',parent_material=[p['physical'] for _,p in sorted(parents.items())],parent_preparations=[],beads=[{k:deepcopy(b[k]) for k in ('id','source_segment_index','root_offset_m','end_treatment')}|{'vertices_m':deepcopy(b['poly']['vertices']),'contact_faces':[{k:v for k,v in c.items() if k!='source_parent_sha256'} for c in b['contacts']]} for b in beads])
    accounting=dict(old_owner_id=owner['id'],source_owner_sha256=identity(owner),source_stock_preserved=owner,disposition='proposed one-for-one replacement only; not applied to any candidate ledger',replacement_owner_id='finite-weld-stock/'+old['id'],replacement_entity_ids=[b['id'] for b in beads],quantity=1,net_volume_m3=V,gross_procured_filler_volume_m3=V*factor,noninstalled_filler_reserve_volume_m3=V*(factor-1),net_volume_delta_vs_old_m3=V-oldV,process_h=ph,QA_h=qh,source_process_QA_retained_once=True,extra_setup_rework_QA_h=None,complete_installed_cost=False,policy_unchanged=deepcopy(policy),cases={c:dict(net_mass_kg=V*rho[j],gross_procured_mass_kg=V*factor*rho[j],noninstalled_reserve_mass_kg=V*(factor-1)*rho[j],material_USD=V*factor*rho[j]*rates[j],process_QA_USD=(ph+qh)*labour[j],direct_USD=V*factor*rho[j]*rates[j]+(ph+qh)*labour[j],first_moment_kg_m=scale(C,V*rho[j])) for j,c in enumerate(CASES)})
    return seal(dict(schema='osr-terminal-finite-weld-proposal/1',physical_definition=physical,physical_definition_id=identity(physical),source_entity=old,source_assignment=binding,beads=beads,net_volume_m3=V,centroid_m=C,first_volume_moment_m4=scale(C,V),accounting=accounting,holds=['Finite nominal external fillet definition only; not a qualified weld','Filler chemistry/WPS/HAZ/fatigue/static/crash/fire/corrosion and physical coupon tests unresolved','Positive interrupted runouts are new physical geometry; actual required seam continuity and load transfer not qualified','Full surrounding assembly interference, tooling, torch/access and construction sequence not evaluated','Additional setup/rework/process/QA and integrated replacement cost remain unknown; declared old source hours retained once only'],**FLAGS))


def compile_definition(raw,*,pin,assignments,request_id):
    """Future explicit one-terminal research definition only, never called at import.

    Missing assignments are held and old owners retained. Full completeness is
    impossible unless every source weld and contact domain resolves. Unknown
    parent/groove obligations remain named; no automatic body/ledger application.
    """
    digest(request_id)
    if pin!=SOURCE or not isinstance(raw,bytes) or len(raw)>64*1024**2 or sha256(raw).hexdigest()!=pin['raw_sha256']:raise ValueError('Exact source raw/pin required')
    if raw[:2]==b'\x1f\x8b':
        decoder=zlib.decompressobj(31);data=decoder.decompress(raw,64*1024**2+1)
        if len(data)>64*1024**2 or decoder.unconsumed_tail or not decoder.eof or decoder.unused_data:raise ValueError('Bounded single source gzip member required')
    else:data=raw
    src=json.loads(data)
    if src['evaluation_id']!=pin['evaluation_id'] or identity({k:v for k,v in src.items() if k!='evaluation_id'})!=pin['evaluation_id'] or src['candidate_id']!=pin['candidate_id'] or identity(src['physical_definition'])!=pin['candidate_id']:raise ValueError('Source physical/evaluation identity mismatch')
    if src['source_sha256']['engineering/terminal_installation.py']!=SOURCE_MODULE_SHA256:raise ValueError('Wrong original terminal source epoch')
    cp=src['component_proposal']
    if cp['units']!='m' or cp['local_axes']!=['u outward','v lateral','w up']:raise ValueError('Explicit original metre terminal axes required')
    entities=cp['entities'];byid={e['id']:e for e in entities}
    if len(byid)!=len(entities):raise ValueError('Duplicate source occurrence')
    welds=[e for e in entities if e.get('physical_drawing',{}).get('kind')=='triangular-weld-seams']
    actual={p:0 for p,_ in PATTERNS}
    for e in welds:actual[pattern_for(e['id'])]+=1
    if actual!=dict(PATTERNS):raise ValueError('Exact183/9/27 source inventory required')
    if not isinstance(assignments,dict) or set(assignments)-{e['id'] for e in welds}:raise ValueError('Unknown/extra source weld assignments')
    owners={};groups=cp['stock_groups']
    if len({g['id'] for g in groups})!=len(groups):raise ValueError('Duplicate source stock owner')
    for g in groups:
        for eid in g['entity_ids']:
            if eid in owners:raise ValueError('Source occurrence has multiple paid stock owners')
            owners[eid]=g
    proposals=[];held=[]
    policy=dict(materials=deepcopy(src['materials']),process=deepcopy(src['process_and_QA']))
    for e in welds:
        if e['id'] not in assignments:held.append(dict(source_weld_id=e['id'],reason='explicit-parent-contact-and-trim-binding-missing',old_stock_owner_id=owners[e['id']]['id'],old_source_retained=True));continue
        a=assignments[e['id']];wanted={c['parent_id'] for s in a['seams'] for c in s['contacts']}
        if wanted-set(byid):raise ValueError('Source parent occurrence does not exist')
        try:proposals.append(define_record(e,owners[e['id']],a,[byid[k] for k in sorted(wanted)],policy))
        except DefinitionHold as error:held.append(dict(source_weld_id=e['id'],reason=str(error),old_stock_owner_id=owners[e['id']]['id'],old_source_retained=True))
    expected_count=sum(q for _,q in PATTERNS)
    if len(proposals)+len(held)!=expected_count:raise AssertionError('Weld conservation failure')
    cross_record_intersections=[]
    for i,a in enumerate(proposals):
        for b in proposals[i+1:]:
            for x in a['beads']:
                for y in b['beads']:
                    if interiors_overlap(x['poly'],y['poly']):cross_record_intersections.append([x['id'],y['id']])
    physical=dict(schema='osr-terminal-weld-revision-physical/1',parent_candidate_id=pin['candidate_id'],proposed_welds=[p['physical_definition'] for p in proposals],unresolved_source_weld_ids=[h['source_weld_id'] for h in held])
    return seal(dict(schema='osr-terminal-weld-definition-proposal/1',source_pin=deepcopy(pin),source_request_id=request_id,physical_definition=physical,physical_definition_id=identity(physical),source_proposal_unchanged=src,source_assignments=deepcopy(assignments),proposals=proposals,held=held,cross_record_intersections=cross_record_intersections,source_welds=expected_count,defined_welds=len(proposals),complete_finite_weld_definition=not held and not cross_record_intersections,old_owner_disposition='No ledger changes applied. Each resolved proposal names one old owner replacement; held owners retained without inferred zero or extra charge.',canonical_definition=None,hold='Research family only; full parent cuts, unsupported interfaces, assembly/access, WPS and independent review still required',**FLAGS))


def fabricated_butt_revision(parent,parent_stock,old_weld,old_weld_stock,policy,*,trim_start_m,trim_end_m):
    """Propose joint-centred finite V grooves for four already-paid plates.

    The source removes four triangles at OUTER RHS corners. Those2mm triangles
    stay in the full-height3mm sideplate and do not reach its mate. This revision
    restores that old void budget, then places equal-area grooves on the actual
    plate butt lines. It does not buy another blank or subtract the prior removal
    twice. Positive trimmed ends make parent and filler deltas explicit. The
    proposed2mm-deep/2mm-wide groove is a geometric hypothesis, not a WPS.
    """
    p=deepcopy(parent);pg=deepcopy(parent_stock);w=deepcopy(old_weld);wg=deepcopy(old_weld_stock);g=p['geometry'];pid=name(p['id'])
    if not (re.fullmatch(r'floor/support/[^/]+',pid) or re.fullmatch(r'side-stiffener/[^/]+/[^/]+/(front|rear)',pid)):raise DefinitionHold('fabricated-source-family-unsupported')
    if set(g)-{'kind','size_m','wall_m','corner_bevels','holes'} or g.get('kind')!='rhs':raise DefinitionHold('complete-fabricated-RHS-source-geometry-required')
    if p.get('physical_drawing') is not None or p.get('exact_CSG_entity') is not None:raise DefinitionHold('unconsumed-fabricated-source-CSG')
    L,width,height=vector(g['size_m']);wall=scalar(g['wall_m'],True);bevel=g['corner_bevels'];leg=.002
    if bevel!={'count':4,'leg_m':leg,'length_m':L,'separately_owned_filler':True}:raise ValueError('Exact already-counted source corner bevel required')
    if not 0<leg<wall<min(width,height)/2:raise DefinitionHold('source-bevel-to-joint-line-domain')
    cuts=[[L,height,wall],[L,height,wall],[L,width-2*wall,wall],[L,width-2*wall,wall]]
    if pg['entity_ids']!=[pid] or type(pg.get('quantity')) is not int or pg['quantity']!=1 or pg['individual_plate_cuts_m']!=cuts:raise ValueError('Four disjoint original paid plate cuts required')
    old_removed=4*.5*leg*leg*L
    if abs(scalar(pg['corner_bevel_removal_m3'],True)-old_removed)>1e-14:raise ValueError('Prior corner void/removal budget mismatch')
    if w['id']!=pid+'/long-seams' or wg['entity_ids']!=[w['id']] or type(wg.get('quantity')) is not int or wg['quantity']!=1 or w['material_id']!=p['material_id'] or p['material_id']!='al5083':raise ValueError('Same-material original weld/parent ownership required')
    if w.get('frame')!='terminal-local-UVW' or p.get('frame')!='terminal-local-UVW' or p.get('scope')!='installed' or w.get('scope')!='installed':raise ValueError('Explicit local installed source frames required')
    T=vector(p['at_m']);R=rotation(p['rotation']);WT=vector(w['at_m']);WR=rotation(w['rotation']);d=w['physical_drawing']
    if d.get('kind')!='triangular-weld-seams' or d.get('leg_m')!=leg or d.get('in_prepared_grooves') is not True or len(d['local_segments_m'])!=4:raise ValueError('Exact original unresolved four longitudinal seams required')
    expected=[(world([-L/2,sy*width/2,sz*height/2],T,R),world([L/2,sy*width/2,sz*height/2],T,R)) for sy in (-1,1) for sz in (-1,1)]
    actual=[tuple(world(vector(v),WT,WR) for v in line) for line in d['local_segments_m']]
    matched=[]
    for a,b in actual:
        candidates=[j for j,(x,y) in enumerate(expected) if (norm(sub(a,x))<EPS and norm(sub(b,y))<EPS) or (norm(sub(a,y))<EPS and norm(sub(b,x))<EPS)]
        if len(candidates)!=1 or candidates[0] in matched:raise ValueError('Old source seam does not match its counted outer-corner void')
        matched.append(candidates[0])
    start=scalar(trim_start_m,True);finish=scalar(trim_end_m,True)
    if min(start,finish)<1e-6 or start+finish>=L-1e-5:raise DefinitionHold('finite-butt-groove-runout-domain')
    # Equal area to each prior right triangle: base2mm,depth2mm =2mm².
    half_width=leg/2;depth=leg;net_length=L-start-finish
    if half_width>=min(wall,width/2-wall) or depth>=wall:raise DefinitionHold('joint-centred-groove-exceeds-one-of-its-two-source-plates')
    base=deepcopy(p);base['geometry']=deepcopy(g);base['geometry'].pop('corner_bevels');material=_parent(base)
    hole_volume=0.;hole_moment=[0.,0.,0.];hole_bounds=[]
    for h in g.get('holes',[]):
        axis=h['axis'];centre=vector(h['centre_m']);radius=scalar(h['radius_m'],True);length=scalar(h['length_m'],True)
        lo=[centre[k]-(length/2 if k==axis else radius) for k in range(3)];hi=[centre[k]+(length/2 if k==axis else radius) for k in range(3)]
        if not any(all(lo[k]>=c['lo'][k]-EPS and hi[k]<=c['hi'][k]+EPS for k in range(3)) for c in material['cells']):raise DefinitionHold('source-bore-not-contained-in-one-source-material-plate')
        hb=bounds(_box(lo,hi,T,R)['vertices'])
        if any(bounds_may_touch(hb,other) for other in hole_bounds):raise DefinitionHold('source-bore-union-needs-independent-domain')
        hole_bounds.append(hb);V=3.141592653589793*radius*radius*length;hole_volume+=V;hole_moment=add(hole_moment,scale(centre,V))
    fullV=L*(width*height-(width-2*wall)*(height-2*wall));beforeV=fullV-hole_volume-old_removed
    if abs(scalar(pg['net_m3'],True)-beforeV)>max(1e-14,beforeV*1e-9):raise ValueError('Original net material differs from holes and once-only corner removal')
    if abs(scalar(wg['net_m3'],True)-old_removed)>1e-14:raise ValueError('Original separately paid filler volume differs')
    grooves=[]
    for sy in (-1,1):
        for sz in (-1,1):
            y=sy*(width/2-wall);z=sz*height/2
            # First three points at one end; next three at the other. The butt
            # line y is common to the half-grooves cut from two separate plates.
            tri=[[y-half_width,z],[y+half_width,z],[y,z-sz*depth]]
            vertices=[world([x,yy,zz],T,R) for x in (-L/2+start,L/2-finish) for yy,zz in tri]
            poly=_poly(vertices,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)])
            gb=bounds(vertices)
            if any(bounds_may_touch(gb,hb) for hb in hole_bounds):raise DefinitionHold('new-groove-intersects-or-touches-source-bore-bound')
            V=half_width*depth*net_length;cl=[(start-finish)/2,y,z-sz*depth/3];cw=world(cl,T,R)
            grooves.append(dict(id=pid+'/joint-centred-groove/'+str(sy)+'/'+str(sz),source_cells=['y'+('+' if sy>0 else '-'),'z'+('+' if sz>0 else '-')],vertices_m=vertices,poly=poly,volume_m3=V,centroid_local_m=cl,centroid_m=cw,half_groove_volumes_m3=[V/2,V/2],contact_domain='Two sloped finite groove faces on the actual listed plates, not a centreline or original outer corner'))
    for j,a in enumerate(grooves):
        for b in grooves[j+1:]:
            if interiors_overlap(a['poly'],b['poly']):raise DefinitionHold('finite-joint-groove-interiors-overlap')
    new_removed=fsum(q['volume_m3'] for q in grooves);cutM=[fsum(q['volume_m3']*q['centroid_local_m'][k] for q in grooves) for k in range(3)];net=fullV-hole_volume-new_removed;C=scale(add(scale(hole_moment,-1.),scale(cutM,-1.)),1/net);fillerC=scale(cutM,1/new_removed)
    rho,rates,labour,factor=_policy(policy,p['material_id']);gross=scalar(pg['gross_m3'],True)
    if gross<max(net,beforeV):raise ValueError('Restoring old void cannot exceed its owned gross material')
    for j,c in enumerate(CASES):
        for group,netV in [(pg,beforeV),(wg,old_removed)]:
            if abs(scalar(group['net_mass_kg'][c])-netV*rho[j])>1e-9:raise ValueError('Source material mass policy mismatch')
            gv=scalar(group['gross_m3'],True);ph=scalar(group['process_h']);qh=scalar(group['QA_h'])
            if min(ph,qh)<0 or ph+qh<=0:raise ValueError('Positive original process/QA scope required')
            expected_cost=gv*rho[j]*rates[j]+(ph+qh)*labour[j]
            if abs(scalar(group['direct_cost_usd'][c])-expected_cost)>max(1e-8,expected_cost*1e-9):raise ValueError('Source material/rate/process cost policy mismatch')
            if abs(scalar(group['gross_mass_kg'][c])-gv*rho[j])>1e-9 or abs(scalar(group['scrap_mass_kg'][c])-(gv-netV)*rho[j])>1e-9:raise ValueError('Source gross/net/scrap ownership mismatch')
        if abs(scalar(wg['gross_m3'],True)-old_removed*factor)>1e-14:raise ValueError('Source filler procurement ownership differs')
    physical=dict(schema='osr-terminal-four-plate-butt-groove-revision/1',parent_id=pid,material_id=p['material_id'],frame='terminal-local-UVW',at_m=T,rotation=deepcopy(R),source_plate_cuts_m=cuts,retired_source_corner_bevels=deepcopy(bevel),source_bores=deepcopy(g.get('holes',[])),new_voids=[{k:deepcopy(q[k]) for k in ('id','source_cells','vertices_m')} for q in grooves],new_filler_material_id=w['material_id'],new_filler_vertices_m=[deepcopy(q['vertices_m']) for q in grooves],trim_start_m=start,trim_end_m=finish,root_face_remaining_thickness_m=wall-depth,parent_geometry_mode='Replace four old voids, preserve all four paid plate blanks, apply only new void geometry; do not subtract both rosters')
    accounting=dict(parent_old_owner_id=pg['id'],weld_old_owner_id=wg['id'],old_parent_stock_sha256=identity(pg),old_filler_stock_sha256=identity(wg),source_paid_parent_gross_m3=gross,source_paid_gross_count=1,parent_new_gross_m3=gross,parent_old_net_m3=beforeV,parent_new_net_m3=net,restore_old_removed_volume_m3=old_removed,new_removed_volume_m3=new_removed,net_parent_volume_delta_m3=net-beforeV,old_filler_net_m3=old_removed,new_filler_net_m3=new_removed,net_filler_volume_delta_m3=new_removed-old_removed,old_removal_charge_repeated=False,new_parent_material_purchase_m3=0.,additional_groove_tool_setup_process_QA_h=None,complete_installed_cost=False,source_parent_account=pg,source_filler_account=wg,policy_unchanged=deepcopy(policy),cases={c:dict(parent_net_kg=net*rho[j],filler_net_kg=new_removed*rho[j],parent_gross_kg=gross*rho[j],filler_procured_kg=new_removed*factor*rho[j],filler_material_cost_delta_USD=(new_removed-old_removed)*factor*rho[j]*rates[j],parent_material_cost_delta_USD=0.,parent_first_moment_kg_m=scale(world(C,T,R),net*rho[j]),filler_first_moment_kg_m=scale(world(fillerC,T,R),new_removed*rho[j])) for j,c in enumerate(CASES)})
    combinedC=scale(hole_moment,-1/(fullV-hole_volume));combinedM=scale(world(combinedC,T,R),fullV-hole_volume)
    replacement_parent=deepcopy(p);replacement_parent['geometry'].pop('corner_bevels')
    replacement_parent['geometry']['finite_void_prisms']=[dict(id=q['id'],kind='triangular-prism',vertices_m=[local(v,T,R) for v in q['vertices_m']]) for q in grooves]
    replacement_parent['mass_kg']={c:net*rho[j] for j,c in enumerate(CASES)};replacement_parent['centroid_local_m']=C
    replacement_parent['source_occurrence_revision']=dict(old_source_entity_sha256=identity(p),new_parent_geometry_id=identity(physical),old_void_credit_once=True)
    replacement_parent['inertia_basis']='Retained source outer-box proxy only; new finite cuts and mass are explicit, full installed inertia/canonical approval not inherited'
    replacement_parent.update(FLAGS)
    replacement_stock=deepcopy(pg);replacement_stock.pop('corner_bevel_removal_m3');replacement_stock['net_m3']=net;replacement_stock['scrap_m3']=gross-net
    replacement_stock['source_void_credit_m3']=old_removed;replacement_stock['new_void_removal_m3']=new_removed
    replacement_stock['net_mass_kg']={c:net*rho[j] for j,c in enumerate(CASES)};replacement_stock['scrap_mass_kg']={c:(gross-net)*rho[j] for j,c in enumerate(CASES)}
    replacement_stock['extra_new_tool_process_QA_h']=None;replacement_stock['new_complete_cost_known']=False
    # Report, never silently inherit, the old supplied proxy centroid residual.
    declaredC=vector(p['centroid_local_m']);correct_old_C=scale(hole_moment,-1/beforeV)
    return seal(dict(schema='osr-terminal-fabricated-butt-revision-proposal/1',physical_definition=physical,physical_definition_id=identity(physical),source_parent=p,source_weld=w,replacement_parent_entity=replacement_parent,replacement_parent_stock=replacement_stock,grooves=grooves,parent_new_volume_m3=net,parent_new_centroid_local_m=C,filler_new_volume_m3=new_removed,filler_new_centroid_local_m=fillerC,combined_net_volume_m3=net+new_removed,combined_first_volume_moment_m4=combinedM,combined_volume_conservation_residual_m3=net+new_removed-(fullV-hole_volume),combined_first_moment_residual_m4=sub(add(scale(world(C,T,R),net),scale(world(fillerC,T,R),new_removed)),combinedM),source_parent_centroid_model_residual_m=sub(declaredC,correct_old_C),accounting=accounting,holds=['Joint-centred groove is a new physical drawing; no original native/body/FEM evidence inherited','Proposed cutter/WPS/root penetration/HAZ/fatigue/static/crash/fire and prototype evidence unresolved','1mm nominal root thickness for3mm wall is not a strength or penetration qualification','Trimmed bead/groove ends and their load transfer require joint-specific review','Source gross material and old process/QA ownership retained once; revised tool/setup/additional QA hours unknown, not zero','No canonical material-kernel, neighbouring terminal fit, tool access, full-body or installed cost admission'],**FLAGS))


def endplate_cavity_binding(weld,stock,tube,endplate,*,trim_m):
    """Explicit source endplate perimeter binding, never a guessed groove cut.

    A revised tube must be passed as that exact revised entity so hashes/voids
    propagate. Passing an old tube does not acquire a newer groove's evidence.
    """
    trim=scalar(trim_m,True);pid=name(tube['id']);match=re.fullmatch(re.escape(pid)+r'/weld([01])',weld['id'])
    if not re.fullmatch(r'side-stiffener/[^/]+/[^/]+/(front|rear)',pid) or match is None or endplate['id']!=pid+'/endplate'+match.group(1):raise ValueError('Exact source tube/endplate/weld mapping required')
    material=_parent(tube);plate=_parent(endplate)
    if plate['physical']['geometry']['kind']!='box' or tube['material_id']!=endplate['material_id'] or tube['material_id']!='al5083':raise DefinitionHold('same-material-finite-endplate-required')
    if any(abs(tube['rotation'][i][j]-endplate['rotation'][i][j])>EPS for i in range(3) for j in range(3)):raise DefinitionHold('explicit-common-member-end-frame-required')
    d=weld['physical_drawing'];L,width,height=tube['geometry']['size_m'];wall=tube['geometry']['wall_m'];T=vector(tube['at_m']);R=rotation(tube['rotation']);WT=vector(weld['at_m']);WR=rotation(weld['rotation']);seams=[];sides=[]
    if d.get('kind')!='triangular-weld-seams' or d.get('in_prepared_grooves') is not True or len(d['local_segments_m'])!=4:raise ValueError('Exact source four-edge cavity paths required')
    for i,line in enumerate(d['local_segments_m']):
        if len(line)!=2:raise ValueError('Two source endpoints required')
        a,b=[local(world(vector(v),WT,WR),T,R) for v in line]
        side=1 if abs(a[0]-L/2)<EPS else -1 if abs(a[0]+L/2)<EPS else 0
        if not side or abs(a[0]-b[0])>EPS:raise DefinitionHold('source-weld-not-at-the-real-tube-end-plane')
        sides.append(side);face=None
        for axis,letter,half in [(1,'y',width/2-wall),(2,'z',height/2-wall)]:
            if abs(a[axis]-b[axis])<EPS and abs(abs(a[axis])-half)<EPS:
                sign=1 if a[axis]>0 else -1
                other=2 if axis==1 else 1;expected_half=height/2-wall if other==2 else width/2-wall
                if max(abs(a[other]),abs(b[other]))>expected_half+EPS:raise DefinitionHold('source-perimeter-extends-past-real-inner-wall')
                face=dict(parent_id=pid,source_parent_sha256=identity(tube),cell_id=letter+('+' if sign>0 else '-'),axis=axis,sign=-sign)
        if face is None:raise DefinitionHold('source-path-is-not-on-a-real-inner-RHS-wall')
        seams.append(dict(source_segment_index=i,root_offset_m=[0.,0.,0.],contacts=[face,dict(parent_id=endplate['id'],source_parent_sha256=identity(endplate),cell_id='solid',axis=0,sign=-side)],end_treatment=dict(kind='flat-positive-runout',trim_start_m=trim,trim_end_m=trim)))
    if len(set(sides))!=1:raise DefinitionHold('mixed-source-tube-end-planes')
    return dict(source_entity_id=weld['id'],source_entity_sha256=identity(weld),source_stock_sha256=identity(stock),parent_preparations=[],joint_domain='existing-source-cavity-fillet',seams=seams)


SOURCE_CUT_AUTHORITY_SHA256='a8473d0bb627122c8721f7be33726dd4da14cd1af5a5f944e54d5a8268a355d1'


def legacy_parent_view(entity,*,cut_authority_sha256):
    """Exact source box/RHS material view; never use its packaging envelope.

    The pinned legacy CAD authority uses h.at_m as a signed cylinder BASE. This
    method takes the mid-point first, then converts into the true solid frame.
    It changes no installed datum, material, stock, mass or cost account.
    """
    e=deepcopy(entity);eid=name(e['id'])
    if cut_authority_sha256!=SOURCE_CUT_AUTHORITY_SHA256:raise ValueError('Exact legacy signed-BASE CAD authority required')
    if not re.fullmatch(r'legacy/(post/(-1|1)|header/0|lower-rail/0)',eid) or e.get('frame')!='terminal-local-UVW':raise DefinitionHold('legacy-parent-source-family-or-frame-unsupported')
    c=e.get('exact_CSG_entity')
    required={'id','part_id','material','geometry','geometry_hold','holes','old_entity_sha256','source_machining_list'}
    if not isinstance(c,dict) or set(c)!=required or c['geometry_hold'] is not None or c['material']!=e['material_id']:raise DefinitionHold('complete-known-legacy-box-RHS-source-contract-required')
    digest(c['old_entity_sha256']);g=c['geometry']
    allowed={'kind','at_m','rotation','size_m'}|({'wall_m'} if g.get('kind')=='rhs' else set())
    if g.get('kind') not in ('box','rhs') or set(g)!=allowed:raise DefinitionHold('unconsumed-legacy-source-material-geometry')
    T=vector(g['at_m']);R=rotation(g['rotation']);size=vector(g['size_m']);holes=[]
    for h in c['holes']:
        if set(h)!={'kind','at_m','axis','diameter_m','length_m','purpose'} or h['kind']!='cylinder-cut':raise DefinitionHold('explicit-legacy-cylinder-BASE-source-contract-required')
        base=vector(h['at_m']);axis=vector(h['axis']);D=scalar(h['diameter_m'],True);L=scalar(h['length_m'],True);name(h['purpose'])
        if abs(norm(axis)-1)>EPS:raise ValueError('Unit source bore axis required')
        centre=add(base,scale(axis,L/2));direction_local=[fsum(R[k][j]*axis[k] for k in range(3)) for j in range(3)];nz=[j for j,a in enumerate(direction_local) if abs(a)>EPS]
        if len(nz)!=1 or abs(abs(direction_local[nz[0]])-1)>EPS:raise DefinitionHold('noncardinal-local-source-cylinder-needs-explicit-provider')
        holes.append(dict(axis=nz[0],centre_m=local(centre,T,R),radius_m=D/2,length_m=L))
    if len({identity(h) for h in holes})!=len(holes):raise DefinitionHold('legacy-source-cylinder-union-not-disjoint')
    # Every existing machining row must have its explicit source-cylinder count;
    # no extra anonymous vent or a summary-only zero/assumed bore.
    declared={};observed={}
    for row in c['source_machining_list']:
        if set(row)-{'diameter_m','length_m','quantity','purpose'} or type(row.get('quantity')) is not int or row['quantity']<=0:raise ValueError('Explicit original machining quantity required')
        key=(scalar(row['diameter_m'],True),scalar(row['length_m'],True));declared[key]=declared.get(key,0)+row['quantity']
    for h in c['holes']:
        key=(h['diameter_m'],h['length_m']);observed[key]=observed.get(key,0)+1
    if declared!=observed:raise DefinitionHold('legacy-actual-hole-and-machining-count-disagreement')
    oldT=vector(e['at_m']);oldR=rotation(e['rotation']);Q=[[fsum(R[k][i]*oldR[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    if e.get('centroid_local_m') is not None:e['centroid_local_m']=local(world(vector(e['centroid_local_m']),oldT,oldR),T,R)
    else:e['centroid_local_m']=None
    for key in ('uncertainty_m','centroid_model_uncertainty_m','centroid_uncertainty_m'):
        if e.get(key) is not None:
            u=vector(e[key])
            if min(u)<0:raise ValueError('Nonnegative explicit source proxy bounds required')
            e[key]=[fsum(abs(Q[i][j])*u[j] for j in range(3)) for i in range(3)]
    inertia=e.get('shape_I_per_kg')
    if inertia is not None:
        if not isinstance(inertia,list) or len(inertia)!=3:raise ValueError('Explicit source inertia proxy tensor required')
        for row in inertia:vector(row)
        e['shape_I_per_kg']=[[fsum(Q[i][k]*inertia[k][l]*Q[j][l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)]
        e['inertia_basis']='Same declared source proxy tensor rigidly re-expressed; no new model, physical measurement or validation inherited'
    e.pop('exact_CSG_entity');e['geometry']={k:deepcopy(g[k]) for k in ('kind','size_m','wall_m') if k in g};e['geometry']['holes']=holes;e['at_m']=T;e['rotation']=deepcopy(R)
    e['legacy_source_view']=dict(source_entity_sha256=identity(entity),exact_CSG_entity=deepcopy(c),source_cut_at_m='signed-base',cut_authority_sha256=cut_authority_sha256,body_placement_or_stock_changed=False,source_proxy_T_m=oldT,source_proxy_rotation=deepcopy(oldR),source_proxy_centroid_local_m=deepcopy(entity.get('centroid_local_m')),source_proxy_inertia_per_kg=deepcopy(entity.get('shape_I_per_kg')),proxy_frame_reexpressed=True)
    e.update(FLAGS);_parent(e) # supported material domain, no renderer/native call
    return e


# New unmanufactured-post drawing. The immutable fe2 inputs remain historical.
POST_BORE_REVISION='terminal-post-full-wall-additions/r1'
POST_SOURCE_BINDINGS={
 'legacy/post/-1':dict(entity_sha256='0bd407718786a72c6a9ed297dfd183ea3b1865b833f9a32eaec5c9920662c10e',owner_sha256='1bdc1d456f37c7834c5fb1de4a92bada1514eda32bbced7e76166877c4d12b19'),
 'legacy/post/1':dict(entity_sha256='2785bfb7f5c944ac37c7a968cc28943e477d04ae77bafdfd15c89322cd800184',owner_sha256='1bdc1d456f37c7834c5fb1de4a92bada1514eda32bbced7e76166877c4d12b19')}


def prospective_post_revision(entity,stock,*,cut_authority_sha256):
    """Authenticated NEW hardware drawing, never reinterpret historical BASE.

    A two-post shared owner already debits these two cylinders/post at their
    full4mm length. Original signedBASE starts2mm into the wall and exits2mm
    outside. Move only the two new BASEs inward2mm, preserving the inherited14,
    dimensions/material/axes and counted group price. Actual old partial cuts,
    original mass proxy and failure remain visible; no native proof inherited.
    """
    pid=entity.get('id');binding=POST_SOURCE_BINDINGS.get(pid)
    if binding is None or identity(entity)!=binding['entity_sha256'] or identity(stock)!=binding['owner_sha256']:raise ValueError('Exact prospective post occurrence/shared-owner source binding required')
    return _post_bore_revision(entity,stock,cut_authority_sha256=cut_authority_sha256)


def _post_bore_revision(entity,stock,*,cut_authority_sha256):
    """Pure finite fixed-interface kernel; invented fixtures test this domain."""
    if cut_authority_sha256!=SOURCE_CUT_AUTHORITY_SHA256:raise ValueError('Exact signed-BASE authority required')
    old=deepcopy(entity);owner=deepcopy(stock);pid=name(old['id'])
    if pid not in ('legacy/post/-1','legacy/post/1') or old.get('frame')!='terminal-local-UVW' or old.get('scope')!='installed' or old.get('material_id')!='al6005a':raise DefinitionHold('fixed-new-post-source-frame-material-domain')
    side=int(pid.rsplit('/',1)[1]);c=deepcopy(old.get('exact_CSG_entity'));g=c.get('geometry') if isinstance(c,dict) else None
    if not isinstance(g,dict) or c.get('geometry_hold') is not None or c.get('material')!='al6005a' or g.get('kind')!='rhs' or set(g)!={'kind','at_m','rotation','size_m','wall_m'}:raise DefinitionHold('complete-known-post-source-drawing-required')
    T=vector(g['at_m']);R=rotation(g['rotation']);size=vector(g['size_m']);wall=scalar(g['wall_m'],True)
    expectedR=[[0.,1.,0.],[0.,0.,1.],[1.,0.,0.]]
    if norm(sub(T,[-.050,side*1.165,.005]))>EPS or any(abs(a-b)>EPS for a,b in zip(size,[2.190,.100,.100])) or abs(wall-.004)>EPS or R!=expectedR:raise DefinitionHold('fixed-post-outer-stock-datum-domain')
    hs=c.get('holes');decl=c.get('source_machining_list')
    if not isinstance(hs,list) or len(hs)!=16 or not isinstance(decl,list) or len(decl)!=3:raise DefinitionHold('exact-inherited14-plus2-post-cut-roster-required')
    inherited=hs[:14];additions=hs[14:];observed={};stated={}
    for h in inherited:
        if set(h)!={'kind','at_m','axis','diameter_m','length_m','purpose'} or h['kind']!='cylinder-cut':raise DefinitionHold('complete-inherited-post-cylinder-required')
        key=(scalar(h['diameter_m'],True),scalar(h['length_m'],True));observed[key]=observed.get(key,0)+1
    for row in decl:
        if set(row)-{'diameter_m','length_m','quantity','purpose'} or type(row.get('quantity')) is not int or row['quantity']<=0:raise DefinitionHold('inherited-post-operation-summary-domain')
        key=(scalar(row['diameter_m'],True),scalar(row['length_m'],True));stated[key]=stated.get(key,0)+row['quantity']
    if observed!=stated or observed!={(.0142,.004):6,(.0065,.004):6,(.003,.004):2}:raise DefinitionHold('inherited14-post-cut-operation-difference')
    expected_ids=['legacy/post/-1','legacy/post/1']
    if owner.get('entity_ids')!=expected_ids or owner.get('source_account',{}).get('quantity')!=2 or owner.get('additional_process_h')!=.4 or owner.get('additional_QA_h') is not None:raise DefinitionHold('one-shared-post-owner-already-priced-rework-domain')
    rho=[scalar(x,True) for x in owner['source_account']['density_cases_kg_m3']]
    if len(rho)!=3 or rho!=sorted(rho):raise ValueError('Explicit source density cases required')
    for case in CASES:
        if scalar(owner['direct_cost_usd'][case],True)<=0 or scalar(owner['gross_mass_kg'][case],True)<=0:raise ValueError('Known positive shared post stock/price required')
    proposed=deepcopy(old);pc=proposed['exact_CSG_entity'];changes=[]
    outer=abs(T[1])+size[2]/2;inner=outer-wall
    for j,(h,u) in enumerate(zip(additions,(-.070,-.030))):
        expected=dict(kind='cylinder-cut',diameter_m=.0082,length_m=.004,at_m=[u,side*1.213,1.020],axis=[0.,float(side),0.],purpose='owned detachable upper-frame bore,outer postwall only')
        if h!=expected:raise DefinitionHold('exact-two-prospective-post-addition-cuts-required')
        new=deepcopy(h);new['at_m']=[u,side*inner,1.020];pc['holes'][14+j]=new
        oldlo=abs(h['at_m'][1]);oldhi=oldlo+h['length_m'];overlap=max(0.,min(oldhi,outer)-max(oldlo,inner));A=3.141592653589793*(h['diameter_m']/2)**2
        if abs(overlap-.002)>EPS:raise DefinitionHold('historical-partial-post-cut-domain-changed')
        changes.append(dict(source_hole_index=14+j,source_hole_sha256=identity(h),historical_signed_BASE=deepcopy(h),new_signed_BASE=deepcopy(new),BASE_translation_m=sub(new['at_m'],h['at_m']),actual_old_wall_overlap_m=overlap,old_declared_removed_volume_m3=A*h['length_m'],old_actual_wall_removed_volume_m3=A*overlap,new_actual_wall_removed_volume_m3=A*wall,new_through_wall=True))
    # The material adapter's geometry-region cover is explicitly proposed. It
    # does NOT replace the inherited operation ledger or add an invoice row.
    pc['source_machining_list']=deepcopy(decl)+[dict(diameter_m=.0082,length_m=.004,quantity=2,purpose='NEW physical drawing regions; already within shared0.4h PEREND allowance; process split/QA unknown')]
    material=legacy_parent_view(proposed,cut_authority_sha256=cut_authority_sha256)
    material['prospective_post_material_view']=material.pop('legacy_source_view')
    mp=_parent(material);regions=[];voidV=0.;voidM=[0.,0.,0.];voidbounds=[]
    for i,h in enumerate(material['geometry']['holes']):
        axis=h['axis'];C=vector(h['centre_m']);r=scalar(h['radius_m'],True);L=scalar(h['length_m'],True);lo=[C[k]-(L/2 if k==axis else r) for k in range(3)];hi=[C[k]+(L/2 if k==axis else r) for k in range(3)]
        if not any(all(lo[k]>=cell['lo'][k]-EPS and hi[k]<=cell['hi'][k]+EPS for k in range(3)) for cell in mp['cells']):raise DefinitionHold('corrected-post-cylinder-not-contained-in-one-real-wall')
        bb=list(zip(lo,hi))
        if any(bounds_may_touch(bb,v) for v in voidbounds):raise DefinitionHold('post-cylinder-union-not-separated')
        voidbounds.append(bb);V=3.141592653589793*r*r*L;voidV+=V;voidM=add(voidM,scale(C,V));regions.append(dict(index=i,volume_m3=V,centre_intrinsic_m=C,first_volume_moment_m4=scale(C,V)))
    fullV=size[0]*(size[1]*size[2]-(size[1]-2*wall)*(size[2]-2*wall));net=fullV-voidV
    if net<=0:raise DefinitionHold('positive-new-post-material-required')
    C=scale(voidM,-1/net);CW=world(C,T,R);nominal={case:net*rho[i] for i,case in enumerate(CASES)}
    for case in CASES:
        if abs(scalar(old['mass_kg'][case],True)-nominal[case])>max(1e-9,nominal[case]*1e-9):raise DefinitionHold('new-full-wall-post-material-does-not-match-already-debited-source-mass')
    uncertainty=old.get('uncertainty_m')
    if uncertainty is None:raise DefinitionHold('unknown-post-position-uncertainty-must-remain-open')
    U=vector(uncertainty)
    if min(U)<0:raise ValueError('Nonnegative source spatial bounds required')
    material['mass_kg']=nominal;material['centroid_local_m']=C;material['centroid_terminal_cases_m']={case:deepcopy(CW) for case in CASES};material['shape_I_per_kg']=None
    material['mass_basis']='New nominal complete RHS-minus16-disjoint-cylinder drawing under retained source density hypotheses; not weighed installed mass'
    material['inertia_basis']='Revised finite cut positions require new inertia evaluation; no old tensor inherited'
    material['mass_centroid_basis']='Exact nominal uniform-material cut integral; inherited20mm/source uncertainty remains, not a measured installed CG'
    physical=dict(schema='osr-prospective-post-through-wall-physical/1',revision=POST_BORE_REVISION,source_occurrence_id=pid,material=_parent(material)['physical'],inherited_cut_count=14,new_corrected_cut_count=2)
    actual_old_extra=fsum(x['old_actual_wall_removed_volume_m3'] for x in changes);declared_extra=fsum(x['old_declared_removed_volume_m3'] for x in changes)
    accounting=dict(source_owner_id=owner['id'],source_owner_sha256=identity(owner),shared_occurrence_ids=expected_ids,owner_quantity_scope='ONE shared source post owner/PEREND; two source occurrences, not two purchases',paid_gross_and_direct_source_price_retained_once=True,source_owner=owner,prior_declared_mass_kg=deepcopy(old['mass_kg']),new_nominal_mass_kg=nominal,new_minus_previous_declared_mass_kg={case:nominal[case]-old['mass_kg'][case] for case in CASES},old_partial_wall_vs_declared_overdebit_m3=declared_extra-actual_old_extra,old_partial_wall_hypothesis_mass_kg={case:nominal[case]+(declared_extra-actual_old_extra)*rho[i] for i,case in enumerate(CASES)},new_mass_not_a_weight_saving_claim=True,additional_purchase_USD=0.,existing_shared_process_allowance_h=.4,allowance_applied_once_per_shared_owner=True,per_hole_process_or_QA_split_h=None,new_BASE_location_fixture_tool_QA_h=None,new_BASE_location_fixture_tool_QA_USD=None,complete_installed_cost=False,transaction_applied=False)
    material['prospective_post_revision']=dict(revision=POST_BORE_REVISION,original_source_entity_sha256=identity(old),original_source_owner_sha256=identity(owner),new_physical_definition_id=identity(physical),original_cut_records_retained_in_receipt=True)
    return seal(dict(schema='osr-prospective-post-through-wall-revision/1',physical_definition=physical,physical_definition_id=identity(physical),original_source_entity=old,original_source_owner=owner,replacement_parent_entity=material,inherited_machining_summary=deepcopy(decl),inherited_cut_records=deepcopy(inherited),new_cut_drawing_records=changes,proposed_geometry_region_roster=deepcopy(pc['source_machining_list']),geometry_region_roster_is_not_a_second_process_charge=True,nominal_material=dict(gross_finished_rhs_volume_m3=fullV,all_void_volume_m3=voidV,net_volume_m3=net,cut_regions=regions,centroid_intrinsic_m=C,centroid_terminal_m=CW,first_moment_kg_m={case:scale(CW,nominal[case]) for case in CASES},source_spatial_uncertainty_m=U,centroid_terminal_bounds_m=[[CW[k]-U[k],CW[k]+U[k]] for k in range(3)],first_moment_bounds_kg_m={case:[[nominal[case]*(CW[k]-U[k]),nominal[case]*(CW[k]+U[k])] for k in range(3)] for case in CASES},source_density_kg_m3=dict(zip(CASES,rho)),uniform_material_is_research_hypothesis=True),accounting=accounting,holds=['NEW unmanufactured post drawing; original signedBASE failure and source retained without reinterpretation','Existing0.4h/PEREND shared allowance retained once; extra fixture/tool/QA allocation unknown, not zero or an additional invoice','Bore/sleeve/isolation/tolerance/tool/swept assembly/removal and neighbouring contacts still require own evidence','Source material grade/density/CG uncertainty, loads/strength/WPS/HAZ/fatigue/fire and physical tests unqualified','No original native/body/canonical/installed evidence inherited'],**FLAGS))


def _all_faces(parent):
    g=parent['physical']['geometry'];out=[]
    for cell in parent['cells']:
        for axis in range(3):
            for sign in (-1,1):
                plane=cell['hi' if sign>0 else 'lo'][axis]
                # A real RHS outer flat face continues across disjoint-cell
                # bookkeeping boundaries. Do not expose it as duplicate partial
                # alternatives or invent a filled hollow END face.
                if g['kind']=='rhs' and axis==2 and abs(plane-sign*g['size_m'][2]/2)<EPS:continue
                out.append(dict(parent_id=parent['id'],source_parent_sha256=parent['source_hash'],cell_id=cell['id'],axis=axis,sign=sign))
    if g['kind']=='rhs':
        for sign in (-1,1):out.append(dict(parent_id=parent['id'],source_parent_sha256=parent['source_hash'],cell_id='outer-z'+('+' if sign>0 else '-'),axis=2,sign=sign))
    return out


def _contained_in_RHS_material_union(points,parent):
    g=parent['physical']['geometry']
    if g['kind']!='rhs':return False
    cb=bounds(points);size=g['size_m'];t=g['wall_m']
    if any(cb[k][0]<-size[k]/2-EPS or cb[k][1]>size[k]/2+EPS for k in range(3)):return False
    inner=[[-size[0]/2,size[0]/2],[-size[1]/2+t,size[1]/2-t],[-size[2]/2+t,size[2]/2-t]]
    return not bounds_may_touch(cb,inner)


def propose_bound_faces(weld,stock,parent_entities,*,root_offsets_m,trim_start_m,trim_end_m,joint_domain):
    """Propose one UNIQUE supported contact pair from two declared real members.

    Both named members, their exact faces/material/voids and explicit proposed
    offsets are inputs. A centreline alone cannot create a connection. Gaps,
    ambiguous contact orientations and conservative cut-bound uncertainty hold.
    This is neither a body clash evaluator nor a strength/WPS acceptance test.
    """
    if len(parent_entities)!=2 or len({p['id'] for p in parent_entities})!=2:raise ValueError('Exactly two distinct explicitly named members required')
    if joint_domain not in ('external-orthogonal-fillet','existing-source-cavity-fillet'):raise ValueError('Explicit supported contact domain required')
    parents={p['id']:_parent(p) for p in parent_entities};pp=[parents[p['id']] for p in parent_entities];drawing=weld['physical_drawing']
    if drawing.get('kind')!='triangular-weld-seams':raise DefinitionHold('finite-source-seam-record-required')
    paths=drawing['local_segments_m'];leg=scalar(drawing['leg_m'],True);start=scalar(trim_start_m,True);end=scalar(trim_end_m,True)
    if not isinstance(root_offsets_m,list) or len(root_offsets_m)!=len(paths) or min(start,end)<1e-6:raise ValueError('Every source segment needs explicit offset and positive runout')
    if all(p['physical']['geometry']['kind']=='box' and not p['void_bounds'] for p in pp):
        if interiors_overlap(_box(pp[0]['cells'][0]['lo'],pp[0]['cells'][0]['hi'],pp[0]['T'],pp[0]['R']),_box(pp[1]['cells'][0]['lo'],pp[1]['cells'][0]['hi'],pp[1]['T'],pp[1]['R'])):raise DefinitionHold('declared-uncut-box-members-have-definite-interior-overlap')
    T=vector(weld['at_m']);R=rotation(weld['rotation']);seams=[]
    for index,line in enumerate(paths):
        if not isinstance(line,list) or len(line)!=2:raise ValueError('Two explicit source endpoints required')
        a,b=[world(vector(v),T,R) for v in line];L=norm(sub(b,a))
        if L-start-end<1e-5:raise DefinitionHold('proposed-trims-consume-source-segment')
        tangent=unit(sub(b,a));offset=vector(root_offsets_m[index]);a=add(add(a,offset),scale(tangent,start));b=add(add(b,offset),scale(tangent,-end));accepted=[];cut_uncertainty=False
        for first in _all_faces(pp[0]):
            fa=_face(first,parents)
            try:_on_face([a,b],fa)
            except DefinitionHold:continue
            for second in _all_faces(pp[1]):
                fb=_face(second,parents);na=fa['normal'];nb=fb['normal']
                if abs(dot(na,nb))>EPS or abs(dot(na,tangent))>EPS or abs(dot(nb,tangent))>EPS:continue
                inner=any(f['parent']['physical']['geometry']['kind']=='rhs' and f['cell']['id'] in ('y-','y+','z-','z+') and f['axis']==(1 if f['cell']['id'][0]=='y' else 2) and f['sign']==(-1 if f['cell']['id'][1]=='+' else 1) for f in (fa,fb))
                if inner!=(joint_domain=='existing-source-cavity-fillet'):continue
                try:_on_face([a,b,add(a,scale(nb,leg)),add(b,scale(nb,leg))],fa);_on_face([a,b,add(a,scale(na,leg)),add(b,scale(na,leg))],fb)
                except DefinitionHold:continue
                bead=_prism(a,b,na,nb,leg)
                if any(interiors_overlap(bead['poly'],_box(c['lo'],c['hi'],p['T'],p['R'])) for p in pp for c in p['cells']):continue
                if any(bounds_may_touch(bead['bounds_m'],vb) for p in pp for vb in p['void_bounds']):cut_uncertainty=True;continue
                accepted.append([first,second])
        if len(accepted)!=1:raise DefinitionHold('segment'+str(index)+':'+('conservative-cut-bound-domain; ' if cut_uncertainty else '')+'unique-real-finite-contact-not-established; candidates='+str(len(accepted)))
        seams.append(dict(source_segment_index=index,root_offset_m=offset,contacts=accepted[0],end_treatment=dict(kind='flat-positive-runout',trim_start_m=start,trim_end_m=end)))
    return dict(source_entity_id=weld['id'],source_entity_sha256=identity(weld),source_stock_sha256=identity(stock),parent_preparations=[],joint_domain=joint_domain,seams=seams)


def revise_source_paths(entity,stock,policy,*,segments_terminal_m,joint_domain,reason):
    """Counted prospective bead-path revision; never erase/reuse the old owner.

    A missing or unsupported source segment can be replaced only by an explicit
    new physical path roster. Old inputs remain embedded; new filler quantity is
    calculated at the unchanged material rates and reserve factor. This does not
    prove that shorter/different welds carry any required load.
    """
    e=deepcopy(entity);old_stock=deepcopy(stock);pattern_for(e['id']);d=e['physical_drawing'];name(reason)
    if d.get('kind')!='triangular-weld-seams' or e.get('frame')!='terminal-local-UVW' or e.get('scope')!='installed':raise ValueError('Known installed source seam contract required')
    if stock['entity_ids']!=[e['id']] or type(stock.get('quantity')) is not int or stock['quantity']!=1:raise ValueError('Original weld stock owner must be retired exactly once')
    if joint_domain not in ('external-orthogonal-fillet','existing-source-cavity-fillet'):raise ValueError('Explicit proposed path contact domain required')
    if not isinstance(segments_terminal_m,list) or not 1<=len(segments_terminal_m)<=128:raise ValueError('Complete finite proposed path roster required')
    paths=[]
    for line in segments_terminal_m:
        if not isinstance(line,list) or len(line)!=2:raise ValueError('Two explicit proposed endpoints required')
        a,b=[vector(x) for x in line]
        if norm(sub(b,a))<1e-5:raise DefinitionHold('proposed-source-path-below-model-domain')
        paths.append([a,b])
    leg=scalar(d['leg_m'],True);oldL=fsum(norm(sub(vector(b),vector(a))) for a,b in d['local_segments_m']);oldV=.5*leg*leg*oldL;newL=fsum(norm(sub(b,a)) for a,b in paths);newV=.5*leg*leg*newL
    rho,rates,labour,factor=_policy(policy,e['material_id']);ph=scalar(stock['process_h']);qh=scalar(stock['QA_h'])
    if min(ph,qh)<0 or ph+qh<=0 or abs(scalar(stock['net_m3'],True)-oldV)>max(1e-14,oldV*1e-9) or abs(scalar(stock['gross_m3'],True)-oldV*factor)>max(1e-14,oldV*factor*1e-9):raise ValueError('Original path/owned filler budget differs')
    for j,c in enumerate(CASES):
        expected=oldV*factor*rho[j]*rates[j]+(ph+qh)*labour[j]
        if abs(scalar(stock['direct_cost_usd'][c])-expected)>max(1e-8,expected*1e-9) or abs(scalar(stock['net_mass_kg'][c])-oldV*rho[j])>1e-9:raise ValueError('Original material/rate/process ownership differs')
    oldR=rotation(e['rotation']);oldT=vector(e['at_m']);initial_local=[[local(p,oldT,oldR) for p in line] for line in paths];bb=bounds([p for line in initial_local for p in line]);centre_local=[(a+b)/2 for a,b in bb];mid=world(centre_local,oldT,oldR)
    # Use the source proper rotation; all source terminal metre coordinates stay
    # unchanged. Only the new local origin follows the explicit proposed paths.
    e['at_m']=mid;e['rotation']=deepcopy(oldR);local_paths=[[local(p,mid,oldR) for p in line] for line in paths]
    localbounds=bounds([p for line in local_paths for p in line]);e['geometry']=dict(kind='envelope',size_m=[max(leg,x[1]-x[0]+2*leg) for x in localbounds]);e['physical_drawing']=dict(kind='triangular-weld-seams',leg_m=leg,local_segments_m=local_paths,in_prepared_grooves=joint_domain=='existing-source-cavity-fillet',exact_triangle_orientation_and_runout_resolved=False)
    e['mass_kg']={c:newV*rho[j] for j,c in enumerate(CASES)};e['centroid_local_m']=[fsum(norm(sub(b,a))*(a[k]+b[k])/2 for a,b in local_paths)/newL for k in range(3)];e['centroid_model_uncertainty_m']=[leg]*3;e['shape_I_per_kg']=None;e['inertia_basis']='New path mass distribution unresolved until finite beads; old source inertia is not inherited'
    provenance=dict(original_source_entity_sha256=identity(entity),original_source_stock_sha256=identity(stock),original_entity=deepcopy(entity),original_stock=old_stock,reason=reason,additional_revised_process_QA_h=None,old_owner_retired_once=True,business_transaction_applied=False)
    e['path_revision']=provenance;e.update(FLAGS);g=deepcopy(stock);g.update(net_m3=newV,gross_m3=newV*factor,scrap_m3=newV*(factor-1),net_mass_kg={c:newV*rho[j] for j,c in enumerate(CASES)},gross_mass_kg={c:newV*factor*rho[j] for j,c in enumerate(CASES)},scrap_mass_kg={c:newV*(factor-1)*rho[j] for j,c in enumerate(CASES)},direct_cost_usd={c:newV*factor*rho[j]*rates[j]+(ph+qh)*labour[j] for j,c in enumerate(CASES)},source_path_revision=deepcopy(provenance),complete_installed_cost=False)
    physical=dict(schema='osr-terminal-source-weld-path-revision/1',source_weld_id=e['id'],material_id=e['material_id'],segments_terminal_m=paths,leg_m=leg)
    return seal(dict(schema='osr-terminal-path-revision-proposal/1',physical_definition=physical,physical_definition_id=identity(physical),replacement_entity=e,replacement_stock=g,old_source_entity=deepcopy(entity),old_source_stock=old_stock,source_policy=deepcopy(policy),old_nominal_filler_volume_m3=oldV,new_nominal_filler_volume_m3=newV,nominal_filler_volume_delta_m3=newV-oldV,joint_domain=joint_domain,holds=['Explicit prospective path revision, not automatic historical result reuse','Shortened/moved/added paths need actual load/WPS/HAZ/fatigue and access evidence','Original process/QA baseline retained once; additional revised work remains unknown','Finite orientation/end treatments and all neighbouring interfaces still need explicit checked definitions'],**FLAGS))


def _face_normal_points(parent,normal,points):
    candidates=[]
    for selector in _all_faces(parent):
        f=_face(selector,{parent['id']:parent})
        if norm(sub(f['normal'],normal))>EPS:continue
        try:_on_face(points,f)
        except DefinitionHold:continue
        candidates.append(f)
    if len(candidates)!=1:raise DefinitionHold('unique-finite-real-parent-end-or-surface-face-not-established')
    return candidates[0]


def finite_surface_butt_revision(parent_negative,parent_positive,stock_negative,stock_positive,source_weld,source_weld_stock,policy,*,root_segments_terminal_m,joint_direction_m,surface_normals_m,half_width_m,depth_m,trim_start_m,trim_end_m,additional_process_h,additional_QA_h):
    """Finite prospective V-groove across two real coplanar plate end faces.

    Parent-negative material lies behind -joint_direction, parent-positive in +.
    A separate half-void is removed from each paid parent; one filler prism fills
    the union. Old weld owner is replaced once. Existing parent voids/gross stock
    are retained, never subtracted/charged a second time. No WPS/load approval.
    """
    a=deepcopy(parent_negative);b=deepcopy(parent_positive);wa=deepcopy(source_weld);wg=deepcopy(source_weld_stock);parents=[a,b];raw_groups=[deepcopy(stock_negative),deepcopy(stock_positive)]
    if a['id']==b['id']:raise ValueError('Two distinct butt-joint members required')
    if any(p['id'] not in g['entity_ids'] for p,g in zip(parents,raw_groups)):raise ValueError('Explicit original parent stock ownership required')
    if raw_groups[0]['id']==raw_groups[1]['id'] and raw_groups[0]!=raw_groups[1]:raise ValueError('Shared stock owner has contradictory source records')
    material=[_parent(p) for p in parents];J=unit(joint_direction_m);hw=scalar(half_width_m,True);depth=scalar(depth_m,True);start=scalar(trim_start_m,True);end=scalar(trim_end_m,True);ph=scalar(additional_process_h,True);qh=scalar(additional_QA_h,True)
    if min(hw,depth)<1e-5 or min(start,end)<1e-6 or not isinstance(root_segments_terminal_m,list) or not 1<=len(root_segments_terminal_m)<=128 or len(surface_normals_m)!=len(root_segments_terminal_m):raise ValueError('Finite explicit joint/profile/runout/process definition required')
    if wa.get('frame')!='terminal-local-UVW' or wa['physical_drawing'].get('kind')!='triangular-weld-seams' or wg['entity_ids']!=[wa['id']] or type(wg.get('quantity')) is not int or wg['quantity']!=1:raise ValueError('One exact original weld owner required')
    if wa['material_id']!='al5083' or any(p['material_id'] not in ('al5083','al5754','al6005a') for p in parents):raise DefinitionHold('explicit-qualified-dissimilar-material-route-required')
    old_leg=scalar(wa['physical_drawing']['leg_m'],True);oldL=fsum(norm(sub(vector(y),vector(x))) for x,y in wa['physical_drawing']['local_segments_m']);oldV=.5*old_leg**2*oldL;rho,rates,labour,factor=_policy(policy,wa['material_id']);oldph=scalar(wg['process_h']);oldqh=scalar(wg['QA_h'])
    if abs(scalar(wg['net_m3'],True)-oldV)>max(1e-14,oldV*1e-9) or abs(scalar(wg['gross_m3'],True)-oldV*factor)>max(1e-14,oldV*factor*1e-9) or min(oldph,oldqh)<0 or oldph+oldqh<=0:raise ValueError('Original filler/process budget differs')
    for j,c in enumerate(CASES):
        if abs(scalar(wg['direct_cost_usd'][c])-(oldV*factor*rho[j]*rates[j]+(oldph+oldqh)*labour[j]))>1e-8:raise ValueError('Original weld cost/rate scope differs')
    pieces=[];cuts=[[],[]];contacts=[]
    for index,line in enumerate(root_segments_terminal_m):
        if len(line)!=2:raise ValueError('Two explicit root endpoints required')
        p,q=[vector(v) for v in line];tangent=unit(sub(q,p));L=norm(sub(q,p));N=unit(surface_normals_m[index])
        if abs(dot(J,N))>EPS or abs(dot(J,tangent))>EPS or abs(dot(N,tangent))>EPS or L-start-end<1e-5:raise DefinitionHold('explicit-orthogonal-butt-profile-and-finite-span-required')
        p=add(p,scale(tangent,start));q=add(q,scale(tangent,-end));mid=scale(add(p,q),.5)
        end_faces=[];surface_faces=[]
        for side,mp in zip((-1,1),material):
            end_faces.append(_face_normal_points(mp,scale(J,-side),[p,q,add(p,scale(N,-depth)),add(q,scale(N,-depth))]))
            surface_faces.append(_face_normal_points(mp,N,[p,q,add(p,scale(J,side*hw)),add(q,scale(J,side*hw))]))
        if any(f['material_depth_m']-depth<=EPS for f in surface_faces):raise DefinitionHold('positive-remaining-parent-root-outside-this-groove-model-domain')
        full_vertices=[sub(p,scale(J,hw)),add(p,scale(J,hw)),sub(p,scale(N,depth)),sub(q,scale(J,hw)),add(q,scale(J,hw)),sub(q,scale(N,depth))]
        fullpoly=_poly(full_vertices,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]);V=hw*depth*(L-start-end);C=sub(mid,scale(N,depth/3))
        for number,(side,mp) in enumerate(zip((-1,1),material)):
            tri=[add(p,scale(J,side*hw)),p,sub(p,scale(N,depth))];tri_end=[add(q,scale(J,side*hw)),q,sub(q,scale(N,depth))];vertices=tri+tri_end;poly=_poly(vertices,fullpoly['faces']);local_vertices=[local(v,mp['T'],mp['R']) for v in vertices]
            if not any(all(cell['lo'][k]-EPS<=v[k]<=cell['hi'][k]+EPS for v in local_vertices for k in range(3)) for cell in mp['cells']) and not _contained_in_RHS_material_union(local_vertices,mp):raise DefinitionHold('half-groove-not-contained-in-real-source-material-union')
            if any(bounds_may_touch(bounds(vertices),vb) for vb in mp['void_bounds']):raise DefinitionHold('half-groove-source-void-union-outside-conservative-domain')
            if any(interiors_overlap(poly,previous['poly']) for previous in cuts[number]):raise DefinitionHold('new-parent-half-groove-interiors-overlap')
            halfC=add(sub(mid,scale(N,depth/3)),scale(J,side*hw/3))
            cuts[number].append(dict(id=wa['id']+'/new-half-groove/'+str(index)+'/'+str(side),kind='triangular-prism',vertices_m=local_vertices,vertices_terminal_m=vertices,poly=poly,volume_m3=V/2,centroid_terminal_m=halfC))
        if any(interiors_overlap(fullpoly,previous['poly']) for previous in pieces):raise DefinitionHold('new-finite-butt-filler-interiors-overlap')
        pieces.append(dict(id=wa['id']+'/finite-butt/'+str(index),poly=fullpoly,vertices_m=full_vertices,volume_m3=V,centroid_terminal_m=C))
        contacts.append(dict(source_end_faces=[dict(parent_id=f['parent']['id'],cell_id=f['cell']['id'],axis=f['axis'],sign=f['sign']) for f in end_faces],source_surface_faces=[dict(parent_id=f['parent']['id'],cell_id=f['cell']['id'],axis=f['axis'],sign=f['sign']) for f in surface_faces],new_root_remaining_m=[f['material_depth_m']-depth for f in surface_faces]))
    replacements=[];machining=[];owner_records={}
    for source,mp,oldgroup,parent_cuts in zip(parents,material,raw_groups,cuts):
        cutV=fsum(c['volume_m3'] for c in parent_cuts);cutM=[fsum(c['volume_m3']*c['centroid_terminal_m'][k] for c in parent_cuts) for k in range(3)];prho,_,_,_=_policy(policy,source['material_id'])
        if source.get('centroid_local_m') is None:raise DefinitionHold('explicit-source-mass-and-centroid-proxy-required-before-debit')
        oldC=world(vector(source['centroid_local_m']),mp['T'],mp['R']);mass=source.get('mass_kg')
        if not isinstance(mass,dict) or set(mass)!=set(CASES):raise DefinitionHold('explicit-source-mass-and-centroid-proxy-required-before-debit')
        new=deepcopy(source);new['geometry']=deepcopy(source['geometry']);existing=deepcopy(mp['physical'].get('finite_source_void_prisms',[]));new['geometry'].pop('corner_bevels',None);new['geometry']['finite_void_prisms']=existing+[{k:deepcopy(c[k]) for k in ('id','kind','vertices_m')} for c in parent_cuts];new_mass={};new_C={}
        for j,case in enumerate(CASES):
            original=scalar(mass[case],True);remaining=original-cutV*prho[j]
            if remaining<=0:raise DefinitionHold('new-parent-preparation-exceeds-source-positive-mass')
            new_mass[case]=remaining;new_C[case]=[(original*oldC[k]-prho[j]*cutM[k])/remaining for k in range(3)]
        new['mass_kg']=new_mass;new['centroid_local_m']=local(new_C['base'],mp['T'],mp['R']);new['centroid_terminal_cases_m']=new_C;new['mass_centroid_basis']='Declared source mass/CG proxy minus exact new groove debit; source uncertainty/physical qualification not removed';new['source_preparation_revision']=dict(source_entity_sha256=identity(source),source_stock_owner_id=oldgroup['id'],cut_volume_m3=cutV,cut_first_volume_moment_m4=cutM);new.update(FLAGS);_parent(new)
        replacements.append(new);machining.append(dict(parent_id=source['id'],source_entity_sha256=identity(source),source_stock_owner_id=oldgroup['id'],source_owner_sha256=identity(oldgroup),new_removed_volume_m3=cutV,new_removed_first_volume_moment_m4=cutM,removed_mass_kg={c:cutV*prho[j] for j,c in enumerate(CASES)},paid_gross_m3=oldgroup.get('gross_m3'),paid_gross_retained_once=True,additional_parent_material_purchase_m3=0.,scrap_credit_USD=0.,basis='New cut debit only; original paid source stock and any pre-existing void roster retained once, not another purchase or duplicate subtraction'))
        if oldgroup['id'] not in owner_records:owner_records[oldgroup['id']]=dict(source_owner=oldgroup,source_owner_sha256=identity(oldgroup),machined_parent_ids=[])
        owner_records[oldgroup['id']]['machined_parent_ids'].append(source['id'])
    V=fsum(p['volume_m3'] for p in pieces);C=[fsum(p['volume_m3']*p['centroid_terminal_m'][k] for p in pieces)/V for k in range(3)]
    physical=dict(schema='osr-terminal-finite-coplanar-end-butt-physical/1',source_weld_id=wa['id'],parent_materials=[p['physical'] for p in material],new_parent_voids=[[{k:deepcopy(c[k]) for k in ('id','kind','vertices_m')} for c in row] for row in cuts],filler_material_id=wa['material_id'],filler_vertices_m=[deepcopy(p['vertices_m']) for p in pieces],joint_direction_m=J,surface_normals_m=[unit(n) for n in surface_normals_m],half_width_m=hw,depth_m=depth,trim_start_m=start,trim_end_m=end)
    account=dict(old_weld_owner_id=wg['id'],old_weld_stock=wg,retire_old_weld_owner_once=True,source_parent_owners=list(owner_records.values()),parent_machining=machining,new_filler_net_volume_m3=V,new_filler_procured_volume_m3=V*factor,new_filler_volume_delta_m3=V-oldV,additional_preparation_process_h=ph,additional_preparation_QA_h=qh,original_weld_process_h=oldph,original_weld_QA_h=oldqh,hour_ownership='Old weld process/QA retained once plus one explicit new preparation process+QA allowance for this joint record, not once per parent',cases={c:dict(new_filler_net_kg=V*rho[j],new_filler_gross_kg=V*factor*rho[j],new_filler_material_USD=V*factor*rho[j]*rates[j],retained_weld_process_QA_USD=(oldph+oldqh)*labour[j],new_preparation_process_QA_USD=(ph+qh)*labour[j],calculated_weld_and_preparation_subtotal_USD=V*factor*rho[j]*rates[j]+(oldph+oldqh+ph+qh)*labour[j]) for j,c in enumerate(CASES)},new_tool_machine_disposal_cost_USD=None,complete_installed_cost=False,live_business_transaction_applied=False)
    return seal(dict(schema='osr-terminal-finite-butt-revision-proposal/1',physical_definition=physical,physical_definition_id=identity(physical),source_parents=parents,source_weld=wa,source_policy=deepcopy(policy),replacement_parent_entities=replacements,parent_machining=machining,filler_pieces=pieces,filler_net_volume_m3=V,filler_centroid_terminal_m=C,filler_first_volume_moment_m4=scale(C,V),accounting=account,holds=['Finite nominal two-parent groove/filler geometry and counted research machining only','Parent updated CG is source proxy minus exact new debit, not a measured or independently qualified installed CG','Source depositedAl5083 is an accounting/material hypothesis; actual filler/WPS/HAZ/root penetration/fatigue/static/crash/fire and tests unresolved','New tool/machine/disposal and whole-body/access costs remain unknown; direct subtotal is incomplete','No source native/body evidence automatically inherited and no global candidate/stock transaction applied'],**FLAGS))


def side_front_connector_revision(row,root,root_stock,endplate,endplate_stock,old_weld,old_weld_stock,policy,*,binding_data_id):
    """Fixed10x70x6 connector with one combined old-filler replacement owner.

    The caller authenticates the full six-row outline before this pure leaf.
    Each row also binds all original member/stock hashes. Fixtures use a distinct
    synthetic binding ID. No quantity is multiplied by cars or terminal count.
    """
    digest(binding_data_id);cid=name(row['id']);parents=[root,endplate]
    for descriptor,p,g in [(row['source_root'],root,root_stock),(row['source_endplate'],endplate,endplate_stock),(row['old_weld_to_replace_once'],old_weld,old_weld_stock)]:
        if descriptor['id']!=p['id'] or descriptor['sha256']!=identity(p) or descriptor['stock_id']!=g['id'] or descriptor['stock_sha256']!=identity(g) or g['entity_ids']!=[p['id']] or type(g.get('quantity')) is not int or g['quantity']!=1:raise ValueError('Exact connector member/paid-owner binding required')
    for p in parents:
        if p['frame']!='terminal-local-UVW' or p['geometry']['kind']!='box' or p['rotation']!=I or p['material_id']!='al5083' or p.get('physical_drawing') is not None or p.get('exact_CSG_entity') is not None:raise DefinitionHold('fixed-source-Al-box-connector-interface-required')
    if any(abs(x-y)>EPS for x,y in zip(vector(root['geometry']['size_m']),[.1505,.070,.006])) or any(abs(x-y)>EPS for x,y in zip(vector(endplate['geometry']['size_m']),[.012,.020,.120])):raise ValueError('Unreviewed connector parent drawing dimensions')
    rb=[[root['at_m'][k]-root['geometry']['size_m'][k]/2,root['at_m'][k]+root['geometry']['size_m'][k]/2] for k in range(3)];eb=[[endplate['at_m'][k]-endplate['geometry']['size_m'][k]/2,endplate['at_m'][k]+endplate['geometry']['size_m'][k]/2] for k in range(3)]
    for measured,declared in [(rb,row['source_face_bounds']['root']),(eb,row['source_face_bounds']['endplate'])]:
        if any(abs(measured[k][j]-scalar(declared[k][j]))>EPS for k in range(3) for j in range(2)):raise ValueError('Connector source face bounds changed')
    gap=rb[0][0]-eb[0][1];proposal=row['new_connector_stock_proposal'];size=[gap,.070,.006];T=[(rb[0][0]+eb[0][1])/2,root['at_m'][1],root['at_m'][2]];blank=[.012,.072,.006]
    if abs(gap-.010)>EPS or any(abs(x-y)>EPS for x,y in zip(vector(proposal['geometry']['size_m']),size)) or any(abs(x-y)>EPS for x,y in zip(vector(proposal['at_m']),T)) or proposal['rotation']!=I or proposal['material_id']!='al5083' or proposal['paid_blank_size_m']!=blank or type(proposal['stock_owner_count']) is not int or proposal['stock_owner_count']!=1 or proposal['geometry']['kind']!='box' or proposal['id']!=cid or proposal['procurement_required'] is not True:raise ValueError('Fixed counted connector stock/pose drawing differs')
    rho,rates,labour,factor=_policy(policy,'al5083');gross=blank[0]*blank[1]*blank[2];uncut=size[0]*size[1]*size[2]
    if abs(scalar(proposal['finished_gross_volume_m3'],True)-uncut)>1e-14 or abs(scalar(proposal['paid_blank_volume_m3'],True)-gross)>1e-14 or proposal['existing_stock_credit_USD']!=0.:raise ValueError('Connector paidblank/uncut stock budget differs')
    hours=row['manufacturing_estimate_inputs'];cut_h=[scalar(x,True) for x in hours['connector_cut_and_deburr_person_h']];setup_h=[scalar(x,True) for x in hours['new_joint_setup_person_h']];qa_h=[scalar(x,True) for x in hours['additional_QA_person_h']]
    if any(len(x)!=3 or x!=sorted(x) for x in (cut_h,setup_h,qa_h)) or hours['machine_rate_USD_h'] is not None:raise ValueError('Ordered declared process/QA bounds and unknown machine rate required')
    connector=dict(id=cid,part_id=cid,material_id='al5083',frame='terminal-local-UVW',scope='installed',at_m=T,rotation=deepcopy(I),geometry=dict(kind='box',size_m=size),mass_kg={c:uncut*rho[j] for j,c in enumerate(CASES)},centroid_local_m=[0.,0.,0.],shape_I_per_kg=None,inertia_basis='Unknown; no source tensor inherited for new connector',**FLAGS)
    cg=dict(id='stock/'+cid,entity_ids=[cid],quantity=1,net_m3=uncut,gross_m3=gross,net_mass_kg={c:uncut*rho[j] for j,c in enumerate(CASES)},gross_mass_kg={c:gross*rho[j] for j,c in enumerate(CASES)},scrap_mass_kg={c:(gross-uncut)*rho[j] for j,c in enumerate(CASES)},direct_cost_usd={c:gross*rho[j]*rates[j]+cut_h[j]*labour[j] for j,c in enumerate(CASES)},process_h_cases=dict(zip(CASES,cut_h)),QA_h=None,QA_owner_id=old_weld_stock['id'],QA_scope='Additional family QA counted once with combined joint, not another zero/charge in new stock')
    if cg['id'] in (root_stock['id'],endplate_stock['id'],old_weld_stock['id']) or cid in (root['id'],endplate['id'],old_weld['id']):raise ValueError('New connector identity collides with an existing owner/member')
    roots=[];normals=[]
    right=row['new_right_opposed_butt_grooves']
    if len(right)!=2:raise ValueError('Two opposed counted grooves required')
    for sign,q in zip((-1,1),right):
        if q['half_cut_parent_ids']!=[cid,root['id']] or q['section_axes']!=[0,2] or q['extrusion_axis']!=1 or q['prior_void_credit']!=0. or abs(q['nominal_root_between_opposed_grooves_m']-.002)>EPS:raise ValueError('Opposed connector groove/member/removal contract differs')
        vertices=[[rb[0][0]-.001,T[2]+sign*.003],[rb[0][0]+.001,T[2]+sign*.003],[rb[0][0],T[2]+sign*.001]]
        if any(abs(scalar(q['vertices_UW_m'][j][k])-vertices[j][k])>EPS for j in range(3) for k in range(2)) or any(abs(scalar(q['interval_m'][j])-[rb[1][0]+.002,rb[1][1]-.002][j])>EPS for j in range(2)):raise ValueError('Fixed2mmx2mm,66mm connector groove vertices changed')
        roots.append([[rb[0][0],rb[1][0],T[2]+sign*.003],[rb[0][0],rb[1][1],T[2]+sign*.003]]);normals.append([0.,0.,float(sign)])
    # Geometry/cut method only. Its intermediate price calculation is NOT another
    # payable row; authoritative family ownership is rebuilt once below.
    right_result=finite_surface_butt_revision(connector,root,cg,root_stock,old_weld,old_weld_stock,policy,root_segments_terminal_m=roots,joint_direction_m=[1.,0.,0.],surface_normals_m=normals,half_width_m=.001,depth_m=.002,trim_start_m=.002,trim_end_m=.002,additional_process_h=setup_h[1],additional_QA_h=qa_h[1])
    final_connector=right_result['replacement_parent_entities'][0];final_root=right_result['replacement_parent_entities'][1];material=[_parent(endplate),_parent(final_connector)];left=[];overlap=[max(rb[1][0],eb[1][0]),min(rb[1][1],eb[1][1])]
    if abs(overlap[1]-overlap[0]-.020)>EPS or len(row['new_left_fillets'])!=2:raise ValueError('Exact20mm real endplate/connector overlap required')
    for sign,q in zip((-1,1),row['new_left_fillets']):
        points=[[eb[0][1],overlap[0]+.002,T[2]+sign*.003],[eb[0][1],overlap[1]-.002,T[2]+sign*.003]];na=[1.,0.,0.];nb=[0.,0.,float(sign)]
        if q['contact_parent_ids']!=[endplate['id'],cid] or q['leg_m']!=.003 or q['flat_runout_each_m']!=.002 or q['outward_face_normals']!=[na,nb] or any(abs(scalar(q['root_line_m'][j][k])-points[j][k])>EPS for j in range(2) for k in range(3)):raise ValueError('Fixed3mm,16mm left contact drawing changed')
        p,s=points;fa=_face_normal_points(material[0],na,[p,s,add(p,scale(nb,.003)),add(s,scale(nb,.003))]);fb=_face_normal_points(material[1],nb,[p,s,add(p,scale(na,.003)),add(s,scale(na,.003))]);bead=_prism(p,s,na,nb,.003)
        if any(interiors_overlap(bead['poly'],_box(c['lo'],c['hi'],m['T'],m['R'])) for m in material for c in m['cells']) or any(bounds_may_touch(bead['bounds_m'],vb) for m in material for vb in m['void_bounds']):raise DefinitionHold('connector-left-fillet-material-or-conservative-cut-domain')
        left.append(dict(id=q['id'],vertices_m=bead['poly']['vertices'],poly=bead['poly'],volume_m3=bead['volume_m3'],centroid_terminal_m=bead['centroid_m'],source_faces=[dict(parent_id=f['parent']['id'],cell_id=f['cell']['id'],axis=f['axis'],sign=f['sign']) for f in (fa,fb)]))
    fillers=right_result['filler_pieces']+left
    for j,x in enumerate(fillers):
        for y in fillers[j+1:]:
            if interiors_overlap(x['poly'],y['poly']):raise DefinitionHold('connector-filler-interior-overlap')
    if len({p['id'] for p in fillers})!=len(fillers):raise ValueError('Duplicate new finite filler occurrence identity')
    V=fsum(x['volume_m3'] for x in fillers);C=[fsum(x['volume_m3']*x['centroid_terminal_m'][k] for x in fillers)/V for k in range(3)];debits=right_result['parent_machining'];conn_cut=debits[0]['new_removed_volume_m3'];root_cut=debits[1]['new_removed_volume_m3'];net=uncut-conn_cut;oldV=scalar(old_weld_stock['net_m3'],True)
    if any(abs(x-y)>max(1e-14,abs(y)*1e-9) for x,y in [(V,row['new_filler_volume_m3']),(net,proposal['net_volume_m3']),(conn_cut,proposal['connector_new_cut_volume_m3']),(root_cut,row['retained_root_new_cut_volume_m3'])]):raise ValueError('Connector finite net/cut/filler quantities differ from pinned outline')
    mass_delta={c:(uncut-conn_cut-root_cut+V-oldV)*rho[j] for j,c in enumerate(CASES)}
    if any(abs(mass_delta[c]-row['net_material_delta_vs_old_weld_kg'][c])>1e-10 for c in CASES):raise ValueError('Connector whole-local netmass reconciliation differs')
    cg.update(net_m3=net,scrap_m3=gross-net,net_mass_kg=deepcopy(final_connector['mass_kg']),scrap_mass_kg={c:(gross-net)*rho[j] for j,c in enumerate(CASES)},source_row_sha256=identity(row),paid_blank_size_m=blank,quantity_scope='ONE new connector per source row/per terminal, never per car')
    max_W=max(abs(v[2]-T[2]) for piece in fillers for v in piece['vertices_m'])
    if max_W>.006+EPS or len(row['known_source_tool_bounds'])!=2:raise ValueError('Fixed connector projection/tool roster differs')
    for control in row['known_source_tool_bounds']:
        name(control['source_joint_id']);digest(control['source_joint_sha256'])
        if scalar(control['tool_radius_m'],True)!=.010 or scalar(control['insertion_m'],True)!=.080 or abs(scalar(control['minimum_radial_projection_separation_m'])-(.020-.010-max_W))>EPS:raise ValueError('Declared4mm source radial projection control differs')
    additional_QA_scope='One declared family additional QA case; includes new connector/combined joint review, no second stock QA charge'
    cases={c:dict(connector_material_USD=gross*rho[j]*rates[j],connector_cut_deburr_USD=cut_h[j]*labour[j],combined_filler_material_USD=V*factor*rho[j]*rates[j],retained_old_weld_process_QA_USD=(old_weld_stock['process_h']+old_weld_stock['QA_h'])*labour[j],new_joint_setup_QA_USD=(setup_h[j]+qa_h[j])*labour[j],calculated_known_component_subtotal_USD=gross*rho[j]*rates[j]+V*factor*rho[j]*rates[j]+(cut_h[j]+old_weld_stock['process_h']+old_weld_stock['QA_h']+setup_h[j]+qa_h[j])*labour[j]) for j,c in enumerate(CASES)}
    filler_stock=dict(id=old_weld_stock['id'],entity_ids=[piece['id'] for piece in fillers],quantity=1,net_m3=V,gross_m3=V*factor,net_mass_kg={c:V*rho[j] for j,c in enumerate(CASES)},gross_mass_kg={c:V*factor*rho[j] for j,c in enumerate(CASES)},scrap_mass_kg={c:V*(factor-1)*rho[j] for j,c in enumerate(CASES)},direct_cost_usd={c:cases[c]['combined_filler_material_USD']+cases[c]['retained_old_weld_process_QA_USD']+cases[c]['new_joint_setup_QA_USD'] for c in CASES},process_h_cases={c:old_weld_stock['process_h']+setup_h[j] for j,c in enumerate(CASES)},QA_h_cases={c:old_weld_stock['QA_h']+qa_h[j] for j,c in enumerate(CASES)},original_source_owner_sha256=identity(old_weld_stock),disposition='Replace original filler owner once; includes both left and right beads and the one additional family QA scope')
    payable=[dict(owner_id=cg['id'],direct_cost_usd=deepcopy(cg['direct_cost_usd'])),dict(owner_id=filler_stock['id'],direct_cost_usd=deepcopy(filler_stock['direct_cost_usd']))]
    if any(abs(sum(p['direct_cost_usd'][c] for p in payable)-cases[c]['calculated_known_component_subtotal_USD'])>1e-10 for c in CASES):raise AssertionError('Connector derived subtotal/payable rows conservation')
    physical=dict(schema='osr-terminal-side-front-connector-physical/1',connector_geometry=deepcopy(final_connector['geometry']),connector_at_m=T,connector_rotation=deepcopy(I),connector_material_id='al5083',retained_root_material=deepcopy(final_root['geometry']),retained_root_at_m=deepcopy(final_root['at_m']),retained_root_rotation=deepcopy(final_root['rotation']),retained_root_material_id=root['material_id'],endplate_material=_parent(endplate)['physical'],filler_material_id=old_weld['material_id'],filler_vertices_m=[deepcopy(x['vertices_m']) for x in fillers])
    return seal(dict(schema='osr-terminal-six-connector-leaf-proposal/1',physical_definition=physical,physical_definition_id=identity(physical),source_binding_data_id=binding_data_id,source_row=deepcopy(row),source_policy=deepcopy(policy),source_root=deepcopy(root),source_endplate=deepcopy(endplate),source_old_weld=deepcopy(old_weld),new_connector_entity=final_connector,new_connector_stock=cg,replacement_weld_stock=filler_stock,replacement_root_entity=final_root,parent_machining=debits,filler_pieces=fillers,filler_net_volume_m3=V,filler_centroid_terminal_m=C,nominal_remaining_root_between_opposed_grooves_m=.002,remaining_root_strength_qualified=False,net_mass_delta_kg=mass_delta,accounting=dict(new_stock_owner_count=1,new_connector_stock_id=cg['id'],old_weld_owner_id=old_weld_stock['id'],old_weld_owner_sha256=identity(old_weld_stock),retire_old_weld_once=True,one_combined_filler_owner=True,old_endplate_owner_retained_once=endplate_stock['id'],old_root_owner_retained_once=root_stock['id'],known_cases=cases,known_cases_are_derived_subtotals_not_extra_payable_rows=True,payable_rows=payable,additional_QA_scope=additional_QA_scope,right_geometry_method_price_is_not_another_charge=True,machine_rate_USD_h=None,complete_installed_cost=False,transaction_applied=False),known_source_tool_projection_controls=deepcopy(row['known_source_tool_bounds']),quantity_scope='One of six connectors per terminal-local template; train multiplicity not applied',holds=['Source-defined nominal finite contact/cut/material/stock only','Tool4mm radial projection separation is a declared bound, not a full assembly/swept tool/path approval','Old weld is geometrically replaced, no WPS/load equivalence inferred from source hours or path lengths','New machine/tool/disposal/final assembly costs unknown; known component subtotal not a quotation or complete installed cost','Fullbody/native/canonical/HAZ/fatigue/crash/fire/testing approval remains separate'],**FLAGS))


def upper_tie_parent_view(entity):
    """Lossless fixed source tie box minus two bores and four rounded slots.

    It preserves the already-counted material and price; it does not subtract
    those slots again. Only the declared source drawing is supported, never an
    arbitrary envelope with a conveniently empty contact region.
    """
    e=deepcopy(entity);match=re.fullmatch(r'upper/(-1|1)/frame-tie',e['id']);d=e.get('physical_drawing')
    if match is None or e.get('frame')!='terminal-local-UVW' or e['rotation']!=I or e['material_id']!='al5083':raise DefinitionHold('fixed-upper-tie-source-frame-required')
    keys={'kind','original_box_size_m','bores','slot_spec','slot_U_centres_local_m','bolt_W_local_m','opening','removed_centroids_local_m','remaining_netsection_qualification'}
    if not isinstance(d,dict) or set(d)!=keys or d['kind']!='tie-with-two-bores-and-four-open-roundended-extractor-slots' or d['original_box_size_m']!=[.070,.006,.120] or set(e['geometry'])!={'kind','size_m','holes'} or e['geometry']['kind']!='envelope' or e['geometry']['size_m']!=d['original_box_size_m'] or e['geometry']['holes']!=d['bores']:raise DefinitionHold('exact-known-tie-source-drawing-required')
    side=int(match.group(1));slot=d['slot_spec'];known={'width_m','depth_m','bottom_W_m','round_end_centre_W_m','closed_end_W_m','end_radius_m','section_area_m2','removed_volume_m3','removed_centroid_W_m','tool','remaining_tie_depth_m','source_bore_radial_ligament_m','local_wall_strength_qualified','slot_process_h_each','slot_QA_h_each','added_finish_surface_upper_reference_m2'}
    if set(slot)!=known or len(d['bores'])!=2 or (len(d['slot_U_centres_local_m'])!=4 or any(abs(scalar(a)-b)>EPS for a,b in zip(d['slot_U_centres_local_m'],[-.026,-.014,.014,.026]))) or d['bolt_W_local_m']!=-.030:raise DefinitionHold('unconsumed-or-revised-tie-slot-definition')
    width=scalar(slot['width_m'],True);depth=scalar(slot['depth_m'],True);bottom=scalar(slot['bottom_W_m']);centre=scalar(slot['round_end_centre_W_m']);radius=scalar(slot['end_radius_m'],True)
    if any(abs(a-b)>EPS for a,b in zip([width,depth,bottom,centre,radius],[.003,.0024,-.030,.0015,.0015])):raise DefinitionHold('fixed-source-round-slot-profile-changed')
    pi=3.141592653589793;A=width*(centre-bottom)+pi*radius*radius/2;cw=(width*(centre-bottom)*(bottom+centre)/2+(pi*radius*radius/2)*(centre+4*radius/(3*pi)))/A
    if any(abs(scalar(slot[k])-v)>EPS for k,v in [('closed_end_W_m',centre+radius),('section_area_m2',A),('removed_volume_m3',A*depth),('removed_centroid_W_m',cw),('remaining_tie_depth_m',.006-depth),('source_bore_radial_ligament_m',.0004)]):raise ValueError('Source slot section/volume/centroid arithmetic differs')
    if sorted(h['centre_m'][0] for h in d['bores'])!=[-.020,.020]:raise ValueError('Exact two source bore stations required')
    for h in d['bores']:
        if set(h)!={'axis','centre_m','radius_m','length_m'} or type(h['axis']) is not int or h['axis']!=1 or any(abs(a-b)>EPS for a,b in zip(vector(h['centre_m'])[1:],[0.,-.030])) or scalar(h['radius_m'],True)!=.0041 or scalar(h['length_m'],True)!=.006:raise DefinitionHold('exact-source-throughbores-required')
    expected=[[u,side*(.003-depth/2),-.030+cw] for u in d['slot_U_centres_local_m']]
    if len(d['removed_centroids_local_m'])!=4 or any(abs(vector(v)[k]-x[k])>EPS for v,x in zip(d['removed_centroids_local_m'],expected) for k in range(3)):raise ValueError('Source slot sign/frame/centroid disagrees')
    slots=[dict(id=e['id']+'/source-slot/'+str(i),kind='open-round-ended-slot',U_centre_m=u,V_entry_face_m=side*.003,face_sign=side,depth_m=depth,W_open_m=-.030+bottom,W_round_centre_m=-.030+centre,radius_m=radius) for i,u in enumerate(d['slot_U_centres_local_m'])]
    e['geometry']=dict(kind='box',size_m=[.070,.006,.120],holes=deepcopy(d['bores']),open_round_slot_voids=slots);e.pop('physical_drawing');e['source_drawing_material_view']=dict(source_entity_sha256=identity(entity),source_drawing=deepcopy(d),already_counted_voids_preserved_once=True,new_removal_or_price_charge=False);e.update(FLAGS);_parent(e)
    return e


# These are prospective drawing revisions, not a source-producer rerun. All
# dimensions are SI and all roots below are in the unchanged terminal frame.
CONNECTOR_BINDING_ID='97fbb0ad76e27cec67f15b9c64cb7316d596521150b0272f6da6e8536cddf8a6'
FULL_REVISION='terminal-finite-183/post-through-bore-r2'


def _terminal_paths(e):
    d=e['physical_drawing']
    if d.get('kind')!='triangular-weld-seams':raise DefinitionHold('explicit-source-weld-paths-required')
    return [[world(vector(v),vector(e['at_m']),rotation(e['rotation'])) for v in line] for line in d['local_segments_m']]


def _axis_bounds(e):
    p=_parent(e);s=p['physical']['geometry']['size_m']
    return bounds(_box(scale(s,-.5),scale(s,.5),p['T'],p['R'])['vertices'])


def _rectangle(axis,a,b,ranges):
    # Four explicit sides; endpoint ordering is preserved, not an inferred miter.
    other=[k for k in range(3) if k!=axis];out=[]
    corners=[]
    for x,y in ((0,0),(1,0),(1,1),(0,1)):
        q=[0.,0.,0.];q[axis]=a;q[other[0]]=ranges[0][x];q[other[1]]=ranges[1][y];corners.append(q)
    for i in range(4):out.append([corners[i],corners[(i+1)%4]])
    return out


def route_record(weld,parents):
    """Explicit27-pattern source routing; no wildcard best-fit parent search.

    The caller supplies authenticated material views. This method does not run a
    native kernel, create material across voids or infer adequate weld strength.
    The original paths and nominal owner remain available even when revised.
    """
    eid=name(weld['id']);p=pattern_for(eid);t=eid.split('/');old=_terminal_paths(weld)
    def member(k):
        if k not in parents:raise DefinitionHold('explicit-source-parent-missing:'+k)
        return parents[k]
    def spec(kind,ids,paths=None,domain='external-orthogonal-fillet',trim=.002,reason=None,**extra):
        for k in ids:member(k)
        return dict(source_weld_id=eid,pattern=p,method=kind,parent_ids=ids,segments_terminal_m=deepcopy(old if paths is None else paths),joint_domain=domain,trim_start_m=trim,trim_end_m=trim,reason=reason,**extra)
    if p in ('floor/support/*/long-seams','side-stiffener/*/*/front/long-seams','side-stiffener/*/*/rear/long-seams'):
        return spec('fabricated-four-plate-butt',[eid.rsplit('/',1)[0]])
    if p in ('side-stiffener/*/*/front/weld0','side-stiffener/*/*/front/weld1','side-stiffener/*/*/rear/weld0','side-stiffener/*/*/rear/weld1'):
        base=eid.rsplit('/',1)[0];return spec('endplate-cavity',[base,base+'/endplate'+t[-1][-1]],domain='existing-source-cavity-fillet')
    if p=='side-front-root/*/*/weld':
        return spec('counted-gap-connector',[eid.rsplit('/',1)[0]],reason='Explicit10mm gap: new counted connector, no unsupported bead spanning empty space')
    if p=='floor/boss/*/*/weld':
        boss=eid.rsplit('/',1)[0];b=member(boss)
        if b['geometry']['kind']!='box' or any(abs(x-y)>EPS for x,y in zip(b['geometry']['size_m'],[.020,.014,.006])):raise DefinitionHold('retained14mm-floor-boss-drawing-required')
        if len(old)!=4:raise ValueError('Four original floor boss paths required')
        return spec('fillet',[boss,'floor/support/'+t[2]],paths=[old[1],old[3]],domain='existing-source-cavity-fillet',reason='Retain14mm boss/thread/axis/paidblank; replace four unsupported top paths by two supported U-end fillets. Rejected10mm width would reduce lateral thread ligament. Reduced weld/load/HAZ remains unqualified',nominal_thread_geometry=dict(major_diameter_m=.004,major_depth_m=.00485,pilot_diameter_m=.0033,pilot_depth_m=.00065,bottom_web_m=.0005,lateral_major_ligament_m=.005,nearest_end_fillet_to_major_m=.008))
    if p=='floor/hanger/*/cap-frame-weld':
        block='floor/hanger/'+t[2]+'/block';b=member(block);side=1 if b['at_m'][1]>0 else -1
        other='floor/post-bottom/'+str(side)+'/closure' if abs(b['geometry']['size_m'][1]-.14)<EPS else 'legacy/lower-rail/0'
        if len(old)!=4:raise ValueError('Four original hanger paths required')
        return spec('fillet',[block,other],paths=old[:3],trim=.003,reason='Drop unsupported flush rear-U perimeter side; three real backed sides retained, reduced weld/load unqualified')
    if p=='floor/post-bottom/*/post-closure-weld':
        return spec('butt',['floor/post-bottom/'+t[2]+'/closure','legacy/post/'+t[2]],joint_direction_m=[0.,0.,1.],surface_normals_m=[[-1.,0.,0.],[0.,-1.,0.],[0.,1.,0.]],reason='Three explicit counted plate/post grooves replace unbacked perimeter fillets')
    if p=='floor/support/*/root-end-weld':
        j=int(t[2]);return spec('fillet',['floor/support/'+t[2],'floor/hanger/'+str(1 if j==0 else 13 if j==14 else j)+'/block'],domain='existing-source-cavity-fillet',trim=.003)
    if p in ('post-clamp/*/*/front-web-weld','post-clamp/*/*/rear-web-weld'):
        label=t[-1].split('-')[0];prefix='/'.join(t[:3]);offset=-.002 if label=='front' else .002
        paths=[[add(v,[offset,0.,0.]) for v in line] for line in old]
        return spec('fillet',[prefix+'/'+label,prefix+'/outer-web'],paths=paths,reason='Root moved from plate centre to its actual inner-U face')
    if p=='roof/fascia-underlap-seam':
        return spec('fillet',['fascia/central','roof/underlap'],paths=[[add(v,[0.,0.,-.001]) for v in line] for line in old],trim=.0015,reason='Root on actual underlap bottom, not plate midplane')
    if p=='roof/standoff-weld/*':return spec('fillet',['roof/standoff/'+t[2],'legacy/header/0'],trim=.003)
    if p=='roof/outrigger-weld/*':
        tube=member('roof/outrigger/'+t[2]);b=_axis_bounds(tube);wall=scalar(tube['geometry']['wall_m'],True)
        paths=_rectangle(0,b[0][0],None,[[b[k][0]+wall,b[k][1]-wall] for k in (1,2)])
        return spec('fillet',['roof/outrigger/'+t[2],'roof/standoff/'+t[2]],paths=paths,domain='existing-source-cavity-fillet',trim=.003,reason='Inner24x54 cavity perimeter has actual standoff backing; old outer perimeter does not')
    if p=='roof/outrigger-fascia-joint/*':
        tube=member('roof/outrigger/'+t[2]);b=_axis_bounds(tube);fb=_axis_bounds(member('roof/fascia-stiffener'));wall=scalar(tube['geometry']['wall_m'],True);w=[max(b[2][0]+wall,fb[2][0]),min(b[2][1]-wall,fb[2][1])]
        paths=[[[b[0][1],v,w[0]],[b[0][1],v,w[1]]] for v in (b[1][0]+wall,b[1][1]-wall)]
        return spec('fillet',['roof/outrigger/'+t[2],'roof/fascia-stiffener'],paths=paths,domain='existing-source-cavity-fillet',trim=.003,reason='Two vertical inner-sidewall roots on real fascia backing; no fictitious RHS endcap')
    if p=='side-front-root/*/*/stiffener-weld':return spec('fillet',[eid.rsplit('/',1)[0],'side-front-stiffener/'+t[1]])
    if p=='side-front-cap-root/*/stiffener-weld':
        cap=eid.rsplit('/',1)[0];e=member(cap);b=_axis_bounds(e);wall=scalar(e['geometry']['wall_m'],True)
        paths=_rectangle(0,b[0][1],None,[[b[k][0]+wall,b[k][1]-wall] for k in (1,2)])
        return spec('fillet',[cap,'side-front-stiffener/'+t[1]],paths=paths,domain='existing-source-cavity-fillet',reason='Inner34x34 cavity perimeter replaces unsupported outer cap perimeter')
    if p=='side-outrigger/*/*/weld':
        side=int(t[1]);bracket=eid.rsplit('/',1)[0];b=_axis_bounds(member(bracket));v=b[1][0] if side==1 else b[1][1]
        paths=[[[b[0][1],v,b[2][0]],[b[0][1],v,b[2][1]]]]
        return spec('fillet',[bracket,'legacy/post/'+t[1]],paths=paths,trim=.003,reason='One actual vertical plate/post contact replaces30mm-wide root on6mm plate; reduced load capacity unresolved')
    if p in ('side-stiffener/*/*/front/tab-weld','side-stiffener/*/*/rear/tab-weld'):
        side=int(t[1]);base=eid.rsplit('/',1)[0];tab=base+'/clamp-weld-tab';web='/'.join(['post-clamp',t[1],t[2],'outer-web']);label=t[3];ep=base+('/endplate1' if label=='front' else '/endplate0');b=_axis_bounds(member(tab));v=b[1][1] if side==1 else b[1][0]
        pairs=[[web,tab],[tab,ep]] if label=='front' else [[ep,tab],[tab,web]]
        paths=[[[u,v,b[2][0]],[u,v,b[2][1]]] for u in (b[0][0],b[0][1])]
        return spec('two-butt-jobs',[tab,web,ep],paths=paths,pairs=pairs,joint_direction_m=[1.,0.,0.],surface_normals_m=[[0.,float(side),0.]]*2,reason='Two counted2mm-deep outer-V grooves replace2mm fillets with only1mm backing; retain stock/pads and1mm nominal tab root, unqualified WPS/load')
    if p=='upper-frame/*/*/boss-weld':return spec('fillet',[eid.rsplit('/',1)[0]+'/boss','legacy/post/'+t[1]],domain='existing-source-cavity-fillet')
    if p in ('upper/*/tie-lug-seams','upper/*/backbone-lug-seams/*','upper/*/cap-backbone-weld'):
        side=int(t[1]);pre='upper/'+t[1];v=side*1.221
        if p=='upper/*/tie-lug-seams':
            ids=[pre+'/frame-tie',pre+'/0/lug'];b=_axis_bounds(member(ids[1]));z=b[2][0];paths=[[[b[0][0],v,z],[b[0][1],v,z]]];J=[0.,0.,1.]
        elif p=='upper/*/backbone-lug-seams/*':
            k=int(t[-1]);ids=[pre+'/0/lug',pre+'/backbone'] if k==0 else [pre+'/backbone',pre+'/1/lug'];b=_axis_bounds(member(pre+'/backbone'));z=b[2][0] if k==0 else b[2][1];paths=[[[b[0][0],v,z],[b[0][1],v,z]]];J=[0.,0.,1.]
        else:
            ids=[pre+'/backbone',pre+'/cap-inner-arm'];a=_axis_bounds(member(ids[0]));b=_axis_bounds(member(ids[1]));u=a[0][1];paths=[[[u,v,max(a[2][0],b[2][0])],[u,v,min(a[2][1],b[2][1])]]];J=[1.,0.,0.]
        return spec('butt',ids,paths=paths,joint_direction_m=J,surface_normals_m=[[0.,float(side),0.]],reason='Counted finite common outer-V butt groove; no unbacked edge fillet or additional unowned stock')
    raise DefinitionHold('unimplemented-source-pattern:'+p)


def aggregate_parent_cuts(parent,stock,contributions,policy):
    """Union separately proposed DISJOINT new cuts against one original owner.

    Never debit sequential replacement parents or duplicate a shared paid blank.
    Source centroid/proxy is retained as a declared starting estimate, not proved
    by exact new cut integrals. Existing holes/slots/voids remain counted once.
    """
    source=deepcopy(parent);mp=_parent(source)
    if source['id'] not in stock['entity_ids']:raise ValueError('Source parent/stock ownership mismatch')
    if not contributions:raise ValueError('Explicit nonempty parent cut contributions required')
    existing=deepcopy(mp['physical'].get('finite_source_void_prisms',[]));existing_ids={c['id'] for c in existing};cuts=[];seen=set()
    for contribution in contributions:
        if set(contribution)!={'source_parent_sha256','source_stock_sha256','source_weld_id','cuts'} or contribution['source_parent_sha256']!=identity(source) or contribution['source_stock_sha256']!=identity(stock):raise ValueError('Aggregate cut source epoch mismatch')
        name(contribution['source_weld_id'])
        for cut in contribution['cuts']:
            if set(cut)!={'id','kind','vertices_m','volume_m3','centroid_terminal_m'} or cut['kind']!='triangular-prism':raise ValueError('Complete finite new cut measure required')
            cid=name(cut['id'])
            if cid in seen or cid in existing_ids:raise ValueError('Duplicate new/existing cut ownership')
            seen.add(cid);vs=[vector(v) for v in cut['vertices_m']]
            if len(vs)!=6:raise ValueError('Six explicit half-prism vertices required')
            V=abs(dot(cross(sub(vs[1],vs[0]),sub(vs[2],vs[0])),sub(vs[3],vs[0])))/2;C=world([fsum(v[k] for v in vs)/6 for k in range(3)],mp['T'],mp['R'])
            if V<=1e-18 or abs(V-scalar(cut['volume_m3'],True))>max(1e-15,V*1e-9) or norm(sub(C,vector(cut['centroid_terminal_m'])))>EPS:raise ValueError('New cut analytic volume/first moment mismatch')
            poly=_poly([world(v,mp['T'],mp['R']) for v in vs],[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)])
            if any(bounds_may_touch(bounds(poly['vertices']),v) for v in mp['void_bounds']):raise DefinitionHold('aggregate-new-cut-near-existing-source-void-outside-conservative-domain')
            if any(interiors_overlap(poly,c['poly']) for c in cuts):raise DefinitionHold('aggregate-new-parent-cut-interior-overlap')
            cuts.append(dict(**deepcopy(cut),poly=poly))
    result=deepcopy(source);result['geometry'].pop('corner_bevels',None);result['geometry']['finite_void_prisms']=existing+[{k:deepcopy(c[k]) for k in ('id','kind','vertices_m')} for c in cuts];_parent(result)
    V=fsum(c['volume_m3'] for c in cuts);M=[fsum(c['volume_m3']*c['centroid_terminal_m'][k] for c in cuts) for k in range(3)];rho,_,_,_=_policy(policy,source['material_id']);oldC=world(vector(source['centroid_local_m']),mp['T'],mp['R']);cases={}
    for j,c in enumerate(CASES):
        m=scalar(source['mass_kg'][c],True);net=m-rho[j]*V
        if net<=0:raise DefinitionHold('aggregate-cut-exceeds-positive-source-parent-mass')
        cases[c]=dict(mass_kg=net,centroid_terminal_m=[(m*oldC[k]-rho[j]*M[k])/net for k in range(3)],removed_mass_kg=rho[j]*V,removed_first_moment_kg_m=scale(M,rho[j]))
    result['mass_kg']={c:cases[c]['mass_kg'] for c in CASES};result['centroid_local_m']=local(cases['base']['centroid_terminal_m'],mp['T'],mp['R']);result['centroid_terminal_cases_m']={c:cases[c]['centroid_terminal_m'] for c in CASES};result['mass_centroid_basis']='Declared original source proxy minus union of exact disjoint new cut integrals; not independently measured installed CG';result['shape_I_per_kg']=None;result['inertia_basis']='Changed finite cuts require a new inertia approximation/qualification; old tensor not silently inherited';result['source_preparation_revision']=dict(source_entity_sha256=identity(source),source_stock_owner_id=stock['id'],cut_owner_ids=[c['id'] for c in cuts],new_removed_volume_m3=V,new_removed_first_volume_moment_m4=M);result.update(FLAGS)
    return seal(dict(schema='osr-terminal-parent-cut-union/1',source_parent=source,source_stock=deepcopy(stock),contributions=deepcopy(contributions),replacement_parent_entity=result,new_removed_volume_m3=V,new_removed_first_volume_moment_m4=M,cases=cases,paid_gross_retained_once=True,additional_material_purchase_m3=0.,scrap_credit_USD=0.,**FLAGS))


def _filler_owner(old,policy,pieces,*,extra_process_h=0.,extra_QA_h=0.,unknown_additional_work=True):
    """One authoritative old filler owner, irrespective of internal joint count."""
    if len({p['id'] for p in pieces})!=len(pieces) or not pieces:raise ValueError('Unique positive finite filler occurrences required')
    rho,rates,labour,factor=_policy(policy,'al5083');V=fsum(scalar(p['volume_m3'],True) for p in pieces);M=[fsum(p['volume_m3']*p['centroid_terminal_m'][k] for p in pieces) for k in range(3)];ph=scalar(old['process_h']);qh=scalar(old['QA_h']);extra_process_h=scalar(extra_process_h);extra_QA_h=scalar(extra_QA_h)
    if min(ph,qh,extra_process_h,extra_QA_h)<0 or ph+qh<=0:raise ValueError('Original process/QA ownership and nonnegative explicit revision hours required')
    return dict(id=old['id'],source_owner_sha256=identity(old),entity_ids=[p['id'] for p in pieces],quantity=1,net_m3=V,gross_m3=V*factor,scrap_m3=V*(factor-1),net_mass_kg={c:V*rho[j] for j,c in enumerate(CASES)},gross_mass_kg={c:V*factor*rho[j] for j,c in enumerate(CASES)},scrap_mass_kg={c:V*(factor-1)*rho[j] for j,c in enumerate(CASES)},direct_cost_usd={c:V*factor*rho[j]*rates[j]+(ph+qh+extra_process_h+extra_QA_h)*labour[j] for j,c in enumerate(CASES)},process_h=ph+extra_process_h,QA_h=qh+extra_QA_h,retained_original_process_h=ph,retained_original_QA_h=qh,additional_process_h=extra_process_h,additional_QA_h=extra_QA_h,extra_setup_tool_machine_disposal_USD=None if unknown_additional_work else 'Declared joint process only; machine/tool/disposal still unknown',first_moment_kg_m={c:scale(M,rho[j]) for j,c in enumerate(CASES)},complete_installed_cost=False,old_owner_retired_once=True)


def _extract_new_cuts(job,parent):
    """Extract only newly owned cuts from a supported two-parent revision."""
    pid=parent['id'];rep=next(p for p in job['replacement_parent_entities'] if p['id']==pid);base=_parent(parent);prior={c['id'] for c in base['physical'].get('finite_source_void_prisms',[])};out=[]
    for c in rep['geometry']['finite_void_prisms']:
        if c['id'] in prior:continue
        vs=c['vertices_m'];worldvs=[world(v,base['T'],base['R']) for v in vs];V=abs(dot(cross(sub(vs[1],vs[0]),sub(vs[2],vs[0])),sub(vs[3],vs[0])))/2;C=[fsum(v[k] for v in worldvs)/6 for k in range(3)];out.append(dict(**deepcopy(c),volume_m3=V,centroid_terminal_m=C))
    return out


def _decode_full_source(raw,pin):
    if pin!=SOURCE or not isinstance(raw,bytes) or len(raw)>64*1024**2 or sha256(raw).hexdigest()!=pin['raw_sha256']:raise ValueError('Exact full terminal source raw/pin required')
    if raw[:2]==b'\x1f\x8b':
        decoder=zlib.decompressobj(31);data=decoder.decompress(raw,64*1024**2+1)
        if len(data)>64*1024**2 or decoder.unconsumed_tail or not decoder.eof or decoder.unused_data:raise ValueError('Bounded single source gzip member required')
    else:data=raw
    src=json.loads(data)
    if src['evaluation_id']!=pin['evaluation_id'] or identity({k:v for k,v in src.items() if k!='evaluation_id'})!=pin['evaluation_id'] or src['candidate_id']!=pin['candidate_id'] or identity(src['physical_definition'])!=pin['candidate_id'] or src['source_sha256']['engineering/terminal_installation.py']!=SOURCE_MODULE_SHA256:raise ValueError('Full source physical/evaluation/source epoch mismatch')
    cp=src['component_proposal']
    if cp['units']!='m' or cp['local_axes']!=['u outward','v lateral','w up']:raise ValueError('Unchanged terminal metre frame required')
    entities=cp['entities'];byid={e['id']:e for e in entities};owners={};groups={}
    if len(byid)!=len(entities):raise ValueError('Duplicate original source occurrence')
    for g in cp['stock_groups']:
        if g['id'] in groups or len(set(g['entity_ids']))!=len(g['entity_ids']):raise ValueError('Duplicate original stock owner/occurrence')
        groups[g['id']]=g
        for eid in g['entity_ids']:
            if eid not in byid or eid in owners:raise ValueError('Missing or duplicate original paid-stock occurrence')
            owners[eid]=g
    welds=[e for e in entities if e.get('physical_drawing',{}).get('kind')=='triangular-weld-seams'];inventory={p:0 for p,_ in PATTERNS}
    for e in welds:
        inventory[pattern_for(e['id'])]+=1
        if e['id'] not in owners or owners[e['id']]['entity_ids']!=[e['id']] or type(owners[e['id']]['quantity']) is not int or owners[e['id']]['quantity']!=1:raise ValueError('One original filler stock owner per weld required')
    if inventory!=dict(PATTERNS):raise ValueError('Exact183 records/27 source patterns required')
    return src,byid,owners,groups,welds


def compile_full_definition(raw,*,pin,connector_binding,cut_authority_sha256,request_id):
    """One prospective183-record terminal definition, never canonical admission.

    Parent preparations run first against original material views. New cuts are
    aggregated once before any dependent cavity/fillet is evaluated. Unsupported
    definitions are preserved as named holds, never old-parent fallback passes.
    No prior062 native/subset output is consumed by this new whole-source call.
    """
    digest(request_id)
    if cut_authority_sha256!=SOURCE_CUT_AUTHORITY_SHA256:raise ValueError('Exact signed-BASE source authority required')
    src,byid,owners,groups,welds=_decode_full_source(raw,pin)
    if connector_binding.get('evaluation_id')!=CONNECTOR_BINDING_ID or identity({k:v for k,v in connector_binding.items() if k!='evaluation_id'})!=CONNECTOR_BINDING_ID:raise ValueError('Exact six-connector read-only binding data required')
    rows=connector_binding['rows'];rowmap={r['old_weld_to_replace_once']['id']:r for r in rows}
    if len(rows)!=6 or len(rowmap)!=6:raise ValueError('Six distinct connector source owners required')
    return _compile_routed_source(src,byid,owners,groups,welds,pin=pin,connector_binding=connector_binding,cut_authority_sha256=cut_authority_sha256,request_id=request_id,expected_records=183)


def _compile_routed_source(src,byid,owners,groups,welds,*,pin,connector_binding,cut_authority_sha256,request_id,expected_records):
    """Internal assembly stage; fixtures may exercise small invented rosters.

    Public entry authenticates the exact183 source and six binding rows BEFORE
    reaching here. A small fixture roster cannot relax that public contract.
    """
    if type(expected_records) is not int or expected_records<1 or len(welds)!=expected_records:raise ValueError('Explicit exact source record count required')
    policy=dict(materials=deepcopy(src['materials']),process=deepcopy(src['process_and_QA']));rowmap={r['old_weld_to_replace_once']['id']:r for r in connector_binding['rows']}
    parents={};views=[];routes={};held={};proposals={};contributions={};base_revisions={};new_stock={};failed_parents=set();new_parts={};job_receipts=[];parent_replacements={};post_revisions={};failed_views={}
    # Only named source material parents are adapted. Unknown equipment/envelopes
    # are retained context; they are never filled or silently promoted to solids.
    def getparent(pid):
        if pid in parents:return parents[pid]
        if pid not in byid:raise DefinitionHold('source-parent-missing:'+pid)
        e=byid[pid];owner=owners.get(pid)
        key=(pid,identity(e),identity(owner),cut_authority_sha256,POST_BORE_REVISION)
        if key in failed_views:raise DefinitionHold(failed_views[key])
        try:
            if pid in POST_SOURCE_BINDINGS:
                if owner is None:raise ValueError('Source post lacks exact paid owner')
                revision=prospective_post_revision(e,owner,cut_authority_sha256=cut_authority_sha256);p=revision['replacement_parent_entity'];post_revisions[pid]=revision;views.append(dict(id=pid,method='NEW-post-through-wall-drawing',source_sha256=identity(e),view_sha256=identity(p),revision_id=revision['evaluation_id']))
            elif pid.startswith('legacy/'):
                p=legacy_parent_view(e,cut_authority_sha256=cut_authority_sha256);views.append(dict(id=pid,method='legacy-signed-base-material-view',source_sha256=identity(e),view_sha256=identity(p)))
            elif re.fullmatch(r'upper/(-1|1)/frame-tie',pid):
                p=upper_tie_parent_view(e);views.append(dict(id=pid,method='exact-rounded-slot-material-view',source_sha256=identity(e),view_sha256=identity(p)))
            else:p=deepcopy(e);_parent(p)
            if pid not in owners:raise ValueError('Source parent lacks explicit paid owner:'+pid)
        except DefinitionHold as error:
            # Exact immutable source/owner/authority/revision failed-view memo.
            # Every route still gets its own identical hold and disposition.
            failed_views[key]=str(error);raise
        parents[pid]=p;return p
    # Resolve routing using lazy, explicit parent lookup, not all unknown source
    # entities. This also makes missing dependencies concrete and auditable.
    class ParentViews(dict):
        def __contains__(self,k):return k in byid
        def __getitem__(self,k):return getparent(k)
    roster=ParentViews()
    for weld in welds:
        eid=weld['id']
        try:routes[eid]=route_record(weld,roster)
        except DefinitionHold as error:held[eid]=dict(source_weld_id=eid,phase='source-route',reason=str(error),old_source_retained=True)
    def hold(eid,phase,error,ids):
        held[eid]=dict(source_weld_id=eid,phase=phase,reason=str(error),parent_ids=deepcopy(ids),old_source_retained=True);failed_parents.update(ids)
    def contribute(job,p,eid):
        contributions.setdefault(p['id'],[]).append(dict(source_parent_sha256=identity(p),source_stock_sha256=identity(owners[p['id']]),source_weld_id=eid,cuts=_extract_new_cuts(job,p)))
    # Preparations are evaluated against original source views, not another
    # joint's replacement. Union/mass/stock debit happens once below.
    for weld in welds:
        eid=weld['id'];r=routes.get(eid)
        if r is None:continue
        method=r['method'];ids=r['parent_ids']
        if method not in ('fabricated-four-plate-butt','butt','two-butt-jobs','counted-gap-connector'):continue
        try:
            if method=='fabricated-four-plate-butt':
                p=getparent(ids[0]);j=fabricated_butt_revision(p,owners[p['id']],weld,owners[eid],policy,trim_start_m=.002,trim_end_m=.002);base_revisions[p['id']]=j;pieces=[dict(id=g['id']+'/filler',poly=deepcopy(g['poly']),vertices_m=deepcopy(g['vertices_m']),volume_m3=g['volume_m3'],centroid_terminal_m=g['centroid_m']) for g in j['grooves']];proposals[eid]=dict(method=method,jobs=[j],pieces=pieces,extra_process_h=0.,extra_QA_h=0.)
            elif method=='counted-gap-connector':
                if eid not in rowmap:raise ValueError('Missing exact source connector data row')
                row=rowmap[eid];root=getparent(row['source_root']['id']);ep=getparent(row['source_endplate']['id']);j=side_front_connector_revision(row,root,owners[root['id']],ep,owners[ep['id']],weld,owners[eid],policy,binding_data_id=CONNECTOR_BINDING_ID)
                if j['new_connector_entity']['id'] in byid or j['new_connector_entity']['id'] in new_parts or j['new_connector_stock']['id'] in groups or j['new_connector_stock']['id'] in new_stock:raise ValueError('New connector occurrence/paid-stock identity collision')
                parent_replacements[root['id']]=j['replacement_root_entity'];new_parts[j['new_connector_entity']['id']]=j['new_connector_entity'];new_stock[j['new_connector_stock']['id']]=j['new_connector_stock'];proposals[eid]=dict(method=method,jobs=[j],pieces=j['filler_pieces'],authoritative_owner=j['replacement_weld_stock'])
            else:
                pairs=r.get('pairs',[ids]);jobs=[];pieces=[]
                for n,pair in enumerate(pairs):
                    a,b=[getparent(k) for k in pair];paths=[r['segments_terminal_m'][n]] if method=='two-butt-jobs' else r['segments_terminal_m'];normals=[r['surface_normals_m'][n]] if method=='two-butt-jobs' else r['surface_normals_m'];j=finite_surface_butt_revision(a,b,owners[a['id']],owners[b['id']],weld,owners[eid],policy,root_segments_terminal_m=paths,joint_direction_m=r['joint_direction_m'],surface_normals_m=normals,half_width_m=.001,depth_m=.002,trim_start_m=.002,trim_end_m=.002,additional_process_h=.04,additional_QA_h=.02)
                    # Internal multi-joint measures are not multiple filler or
                    # old process owners. Give each finite piece a unique ID.
                    joint_pieces=deepcopy(j['filler_pieces'])
                    if method=='two-butt-jobs':
                        for q in joint_pieces:q['id']+='/joint'+str(n)
                    jobs.append(j);pieces+=joint_pieces
                for j in jobs:
                    for p in j['source_parents']:contribute(j,p,eid)
                proposals[eid]=dict(method=method,jobs=jobs,pieces=pieces,extra_process_h=.04,extra_QA_h=.02)
            job_receipts.append(dict(source_weld_id=eid,method=method,job_ids=[j['evaluation_id'] for j in proposals[eid]['jobs']]))
        except DefinitionHold as error:hold(eid,'parent-preparation',error,ids)
    # A shared parent with incompatible preparation modes must be redesigned,
    # not silently selected by dictionary overwrite.
    if set(base_revisions)&(set(contributions)|set(parent_replacements)) or set(contributions)&set(parent_replacements):raise DefinitionHold('shared-parent-mixed-preparation-routes-require-explicit-union')
    final=deepcopy(parents);unions={}
    for pid,j in base_revisions.items():final[pid]=j['replacement_parent_entity']
    for pid,p in parent_replacements.items():final[pid]=p
    for pid,cs in contributions.items():
        try:unions[pid]=aggregate_parent_cuts(parents[pid],owners[pid],cs,policy);final[pid]=unions[pid]['replacement_parent_entity']
        except DefinitionHold as error:
            failed_parents.add(pid)
            for c in cs:hold(c['source_weld_id'],'parent-cut-union',error,[pid])
    # Every prepared joint bound to a failed parent is held as well. No orphaned
    # filler is admitted while its intended material revision failed.
    propagate=True
    while propagate:
        before=len(failed_parents);propagate=False
        for eid,r in routes.items():
            if set(r['parent_ids'])&failed_parents:
                if eid not in held:held[eid]=dict(source_weld_id=eid,phase='dependency',reason='required-parent-preparation-held',parent_ids=r['parent_ids'],old_source_retained=True)
                if r['method'] in ('butt','two-butt-jobs','fabricated-four-plate-butt','counted-gap-connector'):failed_parents.update(r['parent_ids'])
        propagate=len(failed_parents)!=before
    for weld in welds:
        eid=weld['id'];r=routes.get(eid)
        if eid in held or eid in proposals:continue
        ids=r['parent_ids']
        try:
            ps=[final[k] for k in ids];e=weld;g=owners[eid];revision=None
            if r['method']=='endplate-cavity':a=endplate_cavity_binding(e,g,ps[0],ps[1],trim_m=.002)
            else:
                if r['segments_terminal_m']!=_terminal_paths(e) or r['joint_domain']=='existing-source-cavity-fillet' and not e['physical_drawing']['in_prepared_grooves']:
                    revision=revise_source_paths(e,g,policy,segments_terminal_m=r['segments_terminal_m'],joint_domain=r['joint_domain'],reason=r['reason'] or 'Explicit source contact-domain revision');e=revision['replacement_entity'];g=revision['replacement_stock']
                a=propose_bound_faces(e,g,ps,root_offsets_m=[[0.,0.,0.] for _ in e['physical_drawing']['local_segments_m']],trim_start_m=r['trim_start_m'],trim_end_m=r['trim_end_m'],joint_domain=r['joint_domain'])
            j=define_record(e,g,a,ps,policy);pieces=[dict(id=b['id'],poly=b['poly'],vertices_m=b['poly']['vertices'],volume_m3=b['volume_m3'],centroid_terminal_m=b['centroid_m']) for b in j['beads']];proposals[eid]=dict(method=r['method'],jobs=[j],path_revision=revision,pieces=pieces,extra_process_h=0.,extra_QA_h=0.)
        except DefinitionHold as error:held[eid]=dict(source_weld_id=eid,phase='final-parent-fillet',reason=str(error),parent_ids=ids,old_source_retained=True)
    # Final callable receipts and original context are returned even on partial
    # definition success. No failed owner is turned into zero or billed twice.
    defined={k:v for k,v in proposals.items() if k not in held};filler_owners={};allpieces=[]
    # A held connector never becomes a new payable/installed part merely because
    # its local geometry method returned before another dependency held it.
    allowed_new_ids={p['jobs'][0]['new_connector_entity']['id'] for p in defined.values() if p['method']=='counted-gap-connector'}
    new_parts={k:v for k,v in new_parts.items() if k in allowed_new_ids};new_stock={k:v for k,v in new_stock.items() if set(v['entity_ids'])<=allowed_new_ids}
    for eid,p in defined.items():
        filler_owners[eid]=deepcopy(p['authoritative_owner']) if 'authoritative_owner' in p else _filler_owner(owners[eid],policy,p['pieces'],extra_process_h=p['extra_process_h'],extra_QA_h=p['extra_QA_h']);allpieces+=p['pieces']
    if len({p['id'] for p in allpieces})!=len(allpieces):raise ValueError('Duplicate finite filler occurrence across original owners')
    collisions=_filler_intersections(allpieces)
    # Parent owner net deltas are grouped once, including a shared legacy owner.
    # Paid gross/rate/process entries are copied unchanged; additional prep is
    # owned by the one source weld replacement, never repeated on each parent.
    changed={pid:final[pid] for pid in set(base_revisions)|set(parent_replacements)|set(unions) if pid not in failed_parents}
    # Later held weld preparations cannot resurrect the historical partial bore.
    # Retain the new basepost but discard its failed downstream cut/filler.
    for pid,revision in post_revisions.items():
        if pid not in changed:changed[pid]=deepcopy(revision['replacement_parent_entity'])
    parent_owner_rows={}
    for pid,p in changed.items():
        owner=owners[pid];oid=owner['id']
        if oid not in parent_owner_rows:parent_owner_rows[oid]=dict(source_owner=deepcopy(owner),source_owner_sha256=identity(owner),changed_parent_ids=[],net_mass_delta_kg={c:0. for c in CASES})
        row=parent_owner_rows[oid];row['changed_parent_ids'].append(pid)
        for c in CASES:row['net_mass_delta_kg'][c]+=p['mass_kg'][c]-(byid[pid]['mass_kg'][c] if pid in post_revisions else parents[pid]['mass_kg'][c])
    for row in parent_owner_rows.values():
        old=row['source_owner'];row['replacement_owner']=deepcopy(old);row['paid_gross_count']=1;row['material_purchase_delta_USD']={c:0. for c in CASES};row['machining_credit_USD']=0.;row['additional_machining_cost_unknown']=True
        for c in CASES:
            net=scalar(old['net_mass_kg'][c],True)+row['net_mass_delta_kg'][c]
            if net<=0 or net>scalar(old['gross_mass_kg'][c],True)+EPS:raise DefinitionHold('aggregate-parent-stock-net-outside-paid-gross')
            row['replacement_owner']['net_mass_kg'][c]=net;row['replacement_owner']['scrap_mass_kg'][c]=old['gross_mass_kg'][c]-net
        if old.get('net_m3') is not None:
            base_mass=scalar(old['net_mass_kg']['base'],True);rho=base_mass/scalar(old['net_m3'],True);dv=row['net_mass_delta_kg']['base']/rho;row['replacement_owner']['net_m3']=old['net_m3']+dv
            if old.get('gross_m3') is not None:row['replacement_owner']['scrap_m3']=old['gross_m3']-row['replacement_owner']['net_m3']
    dispositions=[dict(source_weld_id=e['id'],old_owner_id=owners[e['id']]['id'],old_owner_sha256=identity(owners[e['id']]),status='defined-one-for-one-replacement' if e['id'] in defined else 'held-original-retained',replacement_owner_id=filler_owners[e['id']]['id'] if e['id'] in defined else None) for e in welds]
    if len(dispositions)!=expected_records or len({x['old_owner_id'] for x in dispositions})!=expected_records or len(defined)+len(held)!=expected_records:raise AssertionError('Original weld owner conservation failed')
    physical=dict(schema='osr-terminal-finite-full-revision-physical/1',revision=FULL_REVISION,parent_candidate_id=pin['candidate_id'],changed_parents=[_parent(p)['physical'] for _,p in sorted(changed.items())],new_parts=[_parent(p)['physical'] for _,p in sorted(new_parts.items())],filler=[dict(id=p['id'],material_id='al5083',vertices_terminal_m=p['poly']['vertices']) for p in allpieces],unresolved_original_weld_ids=sorted(held),interpart_domain='Individual declared mating faces and new finite filler/cut unions only; full surrounding assembly not evaluated')
    return seal(dict(schema='osr-terminal-finite-full-revision-proposal/1',source_pin=deepcopy(pin),request_id=request_id,source_proposal=src,source_connector_binding=deepcopy(connector_binding),source_policy=policy,source_material_views=views,source_post_revisions=post_revisions,failed_parent_view_memo=[dict(source_id=k[0],source_entity_sha256=k[1],source_owner_sha256=k[2],cut_authority_sha256=k[3],revision=k[4],reason=v) for k,v in failed_views.items()],source_routes=routes,preparation_job_receipts=job_receipts,parent_preparation_receipts=proposals,parent_cut_unions=unions,final_changed_parent_entities=changed,new_part_entities=new_parts,defined_welds=sorted(defined),held=list(held.values()),source_weld_count=expected_records,defined_weld_count=len(defined),held_weld_count=len(held),filler_occurrence_count=len(allpieces),cross_record_filler_intersections=collisions,complete_finite_weld_definition=not held and not collisions,physical_definition=physical,physical_definition_id=identity(physical),accounting=dict(old_weld_dispositions=dispositions,filler_replacement_owners=filler_owners,parent_stock_owner_revisions=parent_owner_rows,source_post_owner_dispositions={oid:dict(source_owner_sha256=row['source_owner_sha256'],source_occurrence_ids=sorted(pid for pid in row['changed_parent_ids'] if pid in post_revisions),paid_gross_count=1,old_shared_owner_replaced_once=True,additional_material_invoice=False,additional_process_QA_split_h=None) for oid,row in parent_owner_rows.items() if any(pid in post_revisions for pid in row['changed_parent_ids'])},new_stock_owners=new_stock,untouched_source_owner_ids=sorted(set(groups)-{owners[eid]['id'] for eid in defined}-{x for x in parent_owner_rows}),process_QA_basis='One old weld baseline retained per original owner; multi-butt internal calculations are geometry receipts, not additional payable rows; explicit butt0.04h+QA0.02h per record, connector declared case bounds once; other additional work unknown',complete_installed_cost=False,transaction_applied=False),canonical_definition=None,holds=['Prospective finite drawing/material/accounting definition only; no integrated body acceptance','Original historical source, failed paths and exact material/price provenance preserved','Unknown additional setup/tool/machine/torch access/inspection and neighbouring equipment domains remain open','Reduced or relocated welds,1mm roots, thread HAZ and discontinuous runouts require actual loads/WPS/HAZ/fatigue/corrosion/fire and physical evidence','Prior062 subset/native geometry is not inherited by this changed whole-source request','Full terminal/canonical vehicle assembly, installed inertia,qualification and release are separate tasks'],**FLAGS))
