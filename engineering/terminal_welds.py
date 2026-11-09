"""Finite terminal weld proposals with explicit source material contact faces.

Pure definition API, not an installed-body/native/WPS evaluator. It never picks
an orientation from a centreline or replaces an unknown parent with a box.
External right-angle fillets on declared box/RHS faces are supported. Existing
unresolved grooves, unknown parent CSG, touching void bounds or missing bindings
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
    """Convex polyhedron SAT; numerical1e-10m separation domain, no native claim."""
    if not bounds_overlap(bounds(a['vertices']),bounds(b['vertices'])):return False
    axes=_normals(a)+_normals(b)+[cross(e,f) for e in _edges(a) for f in _edges(b)]
    for axis in axes:
        length=norm(axis)
        if length<1e-18:continue
        axis=scale(axis,1/length);x=[dot(v,axis) for v in a['vertices']];y=[dot(v,axis) for v in b['vertices']]
        if min(max(x),max(y))-max(min(x),min(y))<=EPS:return False
    return True

def _parent(parent):
    """Only authenticated local box/RHS material; no filled allowance envelope."""
    pid=name(parent['id']);mat=name(parent['material_id']);T=vector(parent['at_m']);R=rotation(parent['rotation']);g=parent['geometry']
    if parent.get('frame')!='terminal-local-UVW':raise DefinitionHold('parent-frame-unsupported:'+pid)
    if parent.get('exact_CSG_entity') is not None or parent.get('physical_drawing') is not None:raise DefinitionHold('parent-finished-CSG-needs-independent-face-adapter:'+pid)
    if not isinstance(g,dict) or g.get('kind') not in ('box','rhs'):raise DefinitionHold('parent-material-domain-unsupported:'+pid)
    allowed={'kind','size_m','holes'}|({'wall_m'} if g['kind']=='rhs' else set())
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
    voids=[]
    for h in g.get('holes',[]):
        if set(h)!={'axis','centre_m','radius_m','length_m'} or type(h['axis']) is not int or h['axis'] not in (0,1,2):raise DefinitionHold('parent-bore-domain-unsupported:'+pid)
        c=vector(h['centre_m']);radius=scalar(h['radius_m'],True);L=scalar(h['length_m'],True);a=[c[k]-(L/2 if k==h['axis'] else radius) for k in range(3)];b=[c[k]+(L/2 if k==h['axis'] else radius) for k in range(3)]
        # This conservative cut bounding box is an exclusion, never a cylinder filled as material.
        voids.append(bounds(_box(a,b,T,R)['vertices']))
    return dict(id=pid,material_id=mat,T=T,R=R,source_hash=identity(parent),physical=dict(id=pid,material_id=mat,geometry=deepcopy(g),at_m=T,rotation=deepcopy(R)),cells=cells,void_bounds=voids)


def _face(contact,parents):
    if set(contact)!={'parent_id','source_parent_sha256','cell_id','axis','sign'}:raise ValueError('Explicit source material face selector required')
    p=parents[name(contact['parent_id'])]
    if digest(contact['source_parent_sha256'])!=p['source_hash']:raise ValueError('Source parent epoch mismatch')
    if type(contact['axis']) is not int or contact['axis'] not in (0,1,2) or type(contact['sign']) is not int or contact['sign'] not in (-1,1):raise ValueError('Signed source face axis required')
    cell=next((c for c in p['cells'] if c['id']==contact['cell_id']),None)
    if cell is None:raise ValueError('Unknown parent material cell')
    axis=contact['axis'];sgn=contact['sign'];normal=[0.,0.,0.];normal[axis]=sgn
    return dict(parent=p,cell=cell,axis=axis,sign=sgn,plane=cell['hi' if sgn==1 else 'lo'][axis],normal=direction(normal,p['R']))

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

    Prepared-groove records are deliberately held until a separate counted parent
    cut/member revision supplies their material faces. No bevel is invented here.
    """
    old=deepcopy(entity);owner=deepcopy(stock);binding=deepcopy(assignment);pattern=pattern_for(old['id']);drawing=old.get('physical_drawing',{})
    if drawing.get('kind')!='triangular-weld-seams':raise DefinitionHold('source-weld-drawing-unsupported')
    if old.get('frame')!='terminal-local-UVW' or old.get('scope')!='installed':raise ValueError('Exact local installed weld frame required')
    if old['geometry'].get('kind')!='envelope':raise ValueError('Expected original unresolved weld allowance, not a silently revised solid')
    if set(binding)!={'source_entity_id','source_entity_sha256','source_stock_sha256','seams','parent_preparations'}:raise ValueError('Complete one-weld assignment required')
    if binding['source_entity_id']!=old['id'] or digest(binding['source_entity_sha256'])!=identity(old) or digest(binding['source_stock_sha256'])!=identity(owner):raise ValueError('Source weld/stock identity mismatch')
    if owner['entity_ids']!=[old['id']] or type(owner.get('quantity')) is not int or owner['quantity']!=1:raise ValueError('Original once-only weld stock owner required')
    if binding['parent_preparations'] or drawing.get('in_prepared_grooves') is not False:raise DefinitionHold('counted-parent-groove-or-bevel-revision-required')
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
        faces=[_face(c,parents) for c in s['contacts']];a,b=[f['normal'] for f in faces];tangent=unit(sub(q,p))
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
    # Report, never silently inherit, the old supplied proxy centroid residual.
    declaredC=vector(p['centroid_local_m']);correct_old_C=scale(hole_moment,-1/beforeV)
    return seal(dict(schema='osr-terminal-fabricated-butt-revision-proposal/1',physical_definition=physical,physical_definition_id=identity(physical),source_parent=p,source_weld=w,grooves=grooves,parent_new_volume_m3=net,parent_new_centroid_local_m=C,filler_new_volume_m3=new_removed,filler_new_centroid_local_m=fillerC,combined_net_volume_m3=net+new_removed,combined_first_volume_moment_m4=combinedM,combined_volume_conservation_residual_m3=net+new_removed-(fullV-hole_volume),combined_first_moment_residual_m4=sub(add(scale(world(C,T,R),net),scale(world(fillerC,T,R),new_removed)),combinedM),source_parent_centroid_model_residual_m=sub(declaredC,correct_old_C),accounting=accounting,holds=['Joint-centred groove is a new physical drawing; no original native/body/FEM evidence inherited','Proposed cutter/WPS/root penetration/HAZ/fatigue/static/crash/fire and prototype evidence unresolved','1mm nominal root thickness for3mm wall is not a strength or penetration qualification','Trimmed bead/groove ends and their load transfer require joint-specific review','Source gross material and old process/QA ownership retained once; revised tool/setup/additional QA hours unknown, not zero','No canonical material-kernel, neighbouring terminal fit, tool access, full-body or installed cost admission'],**FLAGS))
