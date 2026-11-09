"""Lossless e849 terminal hardware normal form; no canonical/native admission.

The source uses JSON hashes WITHOUT LF; this adapter's identities include LF.
AABB/moment intervals bound individual material graphs, never fill their voids.
The source CSG, bounded threads, free/compressed seal and all old owners survive.
"""
from copy import deepcopy
from hashlib import sha256
from itertools import product
from math import fsum,isfinite,pi,sqrt
import json

SOURCE_COMMIT='e849510e409601297dc3127101a03ba10affe957'
SOURCE_SHA256='89792f4c046f143f1d2a6d22f848af806d1c800870825628316bac05de64c551'
PARENT=dict(candidate_id='339689820cde417f85a426c5ac4dfee96fcdee9db6f69107776f17874caa878b',evaluation_id='91a013cdd8cc6757b06769f963f75d52499cc58c2de1936c7cc52685aa7d9ec0',raw_sha256='cdef7bfebda549f45a4e1c160c58b07f584c610782c56528c541bf8e43bcb82c')
CASES=('low','base','high');I=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
FAMILIES={'M6-nut':24,'M6-washer':48,'M5-glazing-bolt':12,'M5-glazing-insert':12,'M5-glazing-washer':12,'M8-locknut':8,'M8-washer':16,'thread-guard':32,'glazing-retainer':1,'glazing-seal':1,'glazing-bond':1}
FLAGS=dict(physical_accepted=False,engineering_accepted=False,native_eligible=False,installed_assembly_accepted=False,canonical_admitted=False,manufacturing_release=False,operating_release=False,selected_reference_changed=False,release_approved=False)
# Exact source contexts, not a recursive annotation denylist. Unknown geometry,
# ports, materials, contact/thread and structured fields remain physical.
SOURCE_PART_EVAL={'cost_USD','cost_breakdown_USD','person_process_h','person_QA_h','machine_h','source_quote','mass_kg','paid_stock_kg','scrap_kg_bounds'}
PART_PROCUREMENT={'gross_blank_volume_m3','paid_blank','scrap_volume_bounds_m3'}
MATE_EVIDENCE={'strength_qualified','retention_qualified','material_compression_or_cure_qualified','locking_torque_Nm','torque_Nm','retention_force_N'}
KNOWN_MATE_KINDS={'annular bearing faces','internal thread','owned counterbore/ring bonded slip fit','M5x0.8 bolt','headless insert in stopped thread pocket with retained6mm through-void','screw-on tip protection, not fastener lock','twelve removable M5 fasteners','one continuous moulded ring','continuous dispensed cured bond ring'}
TOP_FIELDS={'assembly_sequence','candidate_id','complete_installed_cost','composition_admitted','cost_scope','counted_joints','engineering_accepted','evaluation_id','holds','manufacturing_release','native_eligible','new_parts_cost_USD','new_parts_mass_kg','occurrences','operating_release','original_source_accounting','original_source_coverage','parent','physical_accepted','physical_definition','prototypes','repair_consumables_per_glazing_service','replacement_plan','request_id','schema','selected_reference_changed','selection_id','service_evaluation','shared_workshop_service_kit','source_machining','source_machining_stock_owners','source_stock_owner_replacements','wiring_cooling_and_bearings','workshop'}
PROTO_FIELDS={'schema','candidate_id','physical_definition','family','size','parts','mating','manufactured_piece_count','basis','rates','materials','mass_kg','cost_USD','approvals','holds','nominal_material_AABB_m','mass_property_bounds','evaluation_id'}


def source_identity(x):return sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def identity(x):return sha256((json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()
def seal(x):return dict(deepcopy(x),evaluation_id=identity(x))
def source_seal(x):
    if x.get('evaluation_id')!=source_identity({k:v for k,v in x.items() if k!='evaluation_id'}):raise ValueError('Upstream no-LF evaluation seal differs')
def hexid(x):
    if not isinstance(x,str) or len(x)!=64 or any(c not in '0123456789abcdef' for c in x):raise ValueError('Exact64hex identity required')
def number(x,positive=False):
    if type(x) not in (int,float) or not isfinite(x) or positive and x<=0:raise ValueError('Finite nonboolean SI scalar required')
    return float(x)
def vector(x):
    if not isinstance(x,(list,tuple)) or len(x)!=3:raise ValueError('Three explicit coordinates required')
    return [number(v) for v in x]
def proper(R):
    if not isinstance(R,list) or len(R)!=3:raise ValueError('Explicit proper signed frame required')
    R=[vector(v) for v in R]
    if any(abs(fsum(R[k][i]*R[k][j] for k in range(3))-(1 if i==j else 0))>1e-10 for i in range(3) for j in range(3)):raise ValueError('Nonrigid frame refused')
    d=R[0][0]*(R[1][1]*R[2][2]-R[1][2]*R[2][1])-R[0][1]*(R[1][0]*R[2][2]-R[1][2]*R[2][0])+R[0][2]*(R[1][0]*R[2][1]-R[1][1]*R[2][0])
    if abs(d-1)>1e-10:raise ValueError('Reflected frame refused')
    return R

def apply(R,p):return [fsum(R[k][j]*p[j] for j in range(3)) for k in range(3)]
def add(a,b):return [a[k]+b[k] for k in range(3)]
def sub(a,b):return [a[k]-b[k] for k in range(3)]
def transpose(R):return [[R[j][i] for j in range(3)] for i in range(3)]
def close(a,b):return abs(number(a)-number(b))<=1e-13+1e-9*max(abs(a),abs(b))
def labels(v,*,positive=False):
    if v is None:return None
    if not isinstance(v,dict) or set(v)!=set(CASES):raise ValueError('Explicit low/base/high labels required')
    out=[number(v[c],positive) for c in CASES]
    if min(out)<0 or out!=sorted(out):raise ValueError('Ordered nonnegative labels required')
    return out

def triple(v,*,positive=False):
    if v is None:return None
    if not isinstance(v,(list,tuple)) or len(v)!=3:raise ValueError('Three explicit known labels required')
    out=[number(x,positive) for x in v]
    if min(out)<0 or out!=sorted(out):raise ValueError('Ordered nonnegative known labels required')
    return out

def interval(x,positive=False):
    if not isinstance(x,(list,tuple)) or len(x)!=2:raise ValueError('Two explicit bounds required')
    a,b=[number(v,positive) for v in x]
    if a>b:raise ValueError('Inverted interval refused')
    return [a,b]
def interval_box(x):
    if not isinstance(x,(list,tuple)) or len(x)!=3:raise ValueError('Three interval axes required')
    return [interval(a) for a in x]
def two_corner_box(x):
    if not isinstance(x,(list,tuple)) or len(x)!=2:raise ValueError('Explicit lower/upper corners required')
    a,b=[vector(v) for v in x]
    if any(a[k]>b[k] for k in range(3)):raise ValueError('Inverted material bounds')
    return [[a[k],b[k]] for k in range(3)]
def affine_box(box,T,R):
    box=interval_box(box);T=vector(T);R=proper(R);pts=[add(T,apply(R,v)) for v in product(*box)]
    return [[min(p[k] for p in pts),max(p[k] for p in pts)] for k in range(3)]
def union_boxes(bs):return [[min(b[k][0] for b in bs),max(b[k][1] for b in bs)] for k in range(3)]
def _contains_box(outer,inner):return all(outer[k][0]-1e-12<=inner[k][0]<=inner[k][1]<=outer[k][1]+1e-12 for k in range(3))


def material_bounds(g,depth=0):
    """Conservative containment only, never Boolean/helix/kernel equivalence.

    Source graph is retained unchanged. Unsupported forms return None with a
    named obligation instead of filled packaging or zero material.
    """
    if depth>32 or not isinstance(g,dict):raise ValueError('Bounded explicit material graph required')
    if 'units' in g and g['units']!='m':raise ValueError('Unconverted material units refused')
    kind=g.get('kind');T=vector(g.get('at_m',[0.,0.,0.]));R=proper(g.get('rotation',I));b=None
    if kind in ('box','annulus','profile-prism') and not {'at_m','rotation'}<=set(g):raise ValueError('Explicit primitive local pose required')
    if kind=='box':
        size=vector(g['size_m'])
        if min(size)<=0:raise ValueError('Positive physical box dimensions required')
        b=[[-x/2,x/2] for x in size]
    elif kind=='annulus':
        L=number(g['length_m'],True);ro=number(g['outer_diameter_m'],True)/2;ri=number(g['inner_diameter_m'])/2
        if not 0<=ri<ro:raise ValueError('Positive annular material required')
        b=[[-L/2,L/2],[-ro,ro],[-ro,ro]]
    elif kind=='profile-prism':
        L=number(g['length_m'],True);pts=g['points_yz_m']
        if not isinstance(pts,list) or not 3<=len(pts)<=128 or any(not isinstance(p,(list,tuple)) or len(p)!=2 for p in pts):raise ValueError('Explicit finite profile required')
        pts=[[number(x) for x in p] for p in pts];A=abs(fsum(a[0]*c[1]-a[1]*c[0] for a,c in zip(pts,pts[1:]+pts[:1])))/2
        if not A:raise ValueError('Nondegenerate material profile required')
        b=[[-L/2,L/2],[min(p[0] for p in pts),max(p[0] for p in pts)],[min(p[1] for p in pts),max(p[1] for p in pts)]]
    elif kind=='difference':
        b=material_bounds(g['outer'],depth+1);cuts=g.get('cuts')
        if not isinstance(cuts,list) or len(cuts)>256:raise ValueError('Explicit complete finite subtraction list required')
        for cut in cuts:material_bounds(cut,depth+1)
    elif kind in ('thread-bounded-material','double-thread-bounded-material'):
        lo=material_bounds(g['minimum_material'],depth+1);hi=material_bounds(g['maximum_material'],depth+1)
        if lo is None or hi is None:return None
        b=union_boxes([lo,hi])
        if kind=='thread-bounded-material':
            thread=g['thread'];axis=vector(thread['axis'])
            if axis!=[1.,0.,0.] or thread.get('handedness') not in ('right','left') or type(thread.get('external')) is not bool or thread.get('exact_helix_supported') is not False:raise ValueError('Explicit unsupported-helix thread contract required')
            if not 0<number(thread['pilot_or_root_diameter_m'],True)<number(thread['major_diameter_m'],True):raise ValueError('Thread pilot/root and major must differ')
            number(thread['pitch_m'],True);number(thread['length_m'],True);vector(thread['at_m'])
        else:
            if g.get('exact_helix_supported') is not False:raise ValueError('No exact double helix admission')
            for key in ('external_thread','internal_thread'):
                th=g[key];number(th['pitch_m'],True);number(th['length_m'],True)
                if not 0<number(th['root_m'] if key=='external_thread' else th['pilot_m'],True)<number(th['major_m'],True):raise ValueError('Double thread root/major differs')
    elif kind=='disjoint-material-union':
        ps=g['pieces']
        if not isinstance(ps,list) or not 1<=len(ps)<=256:raise ValueError('Finite source material union required')
        bs=[material_bounds(p,depth+1) for p in ps]
        if any(b is None for b in bs):return None
        b=union_boxes(bs) # Disjointness is a retained source claim, not proved.
    elif kind=='bounded-thread-void-fill':
        if vector(g['axis'])!=[1.,0.,0.] or g.get('exact_distribution') is not None:raise ValueError('Unknown thread-fill distribution must remain explicit')
        span=interval(g['axial_span_m']);r=number(g['outer_diameter_m'],True)/2
        if not 0<number(g['root_diameter_m'],True)<2*r:raise ValueError('Thread compound radial bound differs')
        b=[span,[-r,r],[-r,r]]
    elif kind=='rigid-material-transform':
        # Tool source uses its own explicit physical graph. If a future schema
        # differs it is retained but unsupported, not filled or repositioned.
        return None
    else:return None
    return None if b is None else affine_box(b,T,R)


def containment_moments(box,mass,T=None,R=None):
    """Marginal affine mass/CG/FM/inertia bounds about the named frame origin.

    These intervals are deliberately not a correlated pointCG/tensor. No source
    anatomical passenger/stability result or CAD measure is inherited.
    """
    if box is None or mass is None:return dict(centroid_interval_m=None,mass_first_moment_interval_kg_m=None,inertia_about_frame_origin_interval_kg_m2=None,centroidal_inertia=None,exact_point_CG_m=None,exact_inertia_kg_m2=None,unsupported_or_unknown=True)
    box=interval_box(box);mass=interval(mass,True)
    if T is not None:box=affine_box(box,T,R)
    fm=[[min(m*x for m in mass for x in box[k]),max(m*x for m in mass for x in box[k])] for k in range(3)];inertia=[]
    for i in range(3):
        row=[]
        for j in range(3):
            if i==j:row.append([0.,mass[1]*fsum(max(abs(v) for v in box[k])**2 for k in range(3) if k!=i)])
            else:
                products=[-m*a*b for m in mass for a in box[i] for b in box[j]];row.append([min(products),max(products)])
        inertia.append(row)
    return dict(centroid_interval_m=box,mass_first_moment_interval_kg_m=fm,inertia_about_frame_origin_interval_kg_m2=inertia,centroidal_inertia=None,exact_point_CG_m=None,exact_inertia_kg_m2=None,unsupported_or_unknown=False,method='Nonnegative material containment; marginal interval enclosure, not correlated mass-label scenarios or exact centroid/tensor')


def _part_physical(p):
    # Known stock/process/price fields are excluded only at this exact part
    # wrapper. The same names inside opaque geometry/material records survive.
    excluded=SOURCE_PART_EVAL|PART_PROCUREMENT
    if p['material']=='EPDM-cellular-unqualified' and p.get('mass_volume_factor')==1.25:
        excluded=excluded|{k for k in ('density_basis','deformation_model') if isinstance(p.get(k),str)}
    return {k:deepcopy(v) for k,v in p.items() if k not in excluded}


def exact_simple_volume(g):
    """Only independently explicit primitive or disjoint through-ring domains.

    Unsupported Boolean/thread intersection returns None, not a guessed net.
    The returned value is analytical nominal geometry, never native B-rep proof.
    """
    material_bounds(g);kind=g['kind']
    if kind=='box':return number(g['size_m'][0],True)*number(g['size_m'][1],True)*number(g['size_m'][2],True)
    if kind=='annulus':return pi/4*(number(g['outer_diameter_m'],True)**2-number(g['inner_diameter_m'])**2)*number(g['length_m'],True)
    if kind=='profile-prism':
        pts=g['points_yz_m'];return abs(fsum(a[0]*b[1]-a[1]*b[0] for a,b in zip(pts,pts[1:]+pts[:1])))/2*g['length_m']
    if kind!='difference' or g['outer'].get('kind')!='box' or proper(g['outer']['rotation'])!=I:return None
    outer=g['outer'];size=vector(outer['size_m']);T=vector(outer['at_m']);apertures=[];bores=[]
    for c in g['cuts']:
        if c.get('kind')=='box':
            if proper(c['rotation'])!=I or not close(c['size_m'][0],size[0]) or not close(c['at_m'][0],T[0]):return None
            b=material_bounds(c)
            if not _contains_box(material_bounds(outer),b):return None
            apertures.append(c)
        elif c.get('kind')=='annulus' and c['inner_diameter_m']==0 and proper(c['rotation'])==I and close(c['length_m'],size[0]) and close(c['at_m'][0],T[0]):bores.append(c)
        else:return None
    if len(apertures)!=1:return None
    aperture=material_bounds(apertures[0]);outerb=material_bounds(outer)
    for i,c in enumerate(bores):
        cb=material_bounds(c);r=c['outer_diameter_m']/2;p=c['at_m']
        if not _contains_box(outerb,cb):return None
        d=sqrt(fsum(max(aperture[k][0]-p[k],0.,p[k]-aperture[k][1])**2 for k in (1,2)))
        if d<r-1e-12:return None
        for old in bores[:i]:
            if sqrt(fsum((old['at_m'][k]-p[k])**2 for k in (1,2)))<r+old['outer_diameter_m']/2-1e-12:return None
    return exact_simple_volume(outer)-exact_simple_volume(apertures[0])-fsum(exact_simple_volume(c) for c in bores)

def _mates_physical(mates):
    out=[]
    for m in mates:
        q=deepcopy(m)
        if m.get('kind') in KNOWN_MATE_KINDS:
            for k in MATE_EVIDENCE:
                if k in q and (q[k] is None or type(q[k]) in (bool,int,float)):q.pop(k)
            # Fork-driver geometry is shared workshop data; still retained in
            # full source/contracts/lifecycle, never an installed material slab.
            if m.get('kind')=='headless insert in stopped thread pocket with retained6mm through-void' and isinstance(q.get('fork_driver'),dict):q.pop('fork_driver')
        out.append(q)
    return out


def _cost_components(part,prototype):
    """Reconcile each known subaccount, retaining explicit partial unknowns.

    A correct sum cannot conceal negative QA or reallocated material/process.
    Expected values are diagnostics, never replacements for missing reports.
    """
    fields=('material','process','machine','QA','overhead');total=labels(part.get('cost_USD'));reported=part.get('cost_breakdown_USD');gross=number(part['gross_blank_volume_m3'],True)
    material=prototype['materials'][part['material']];rates=prototype['rates'];rho=triple(material['density_kg_m3'],positive=True);price=triple(material['USD_kg']);ph=triple(part.get('person_process_h'));qh=triple(part.get('person_QA_h'));mh=triple(part.get('machine_h'));labour=triple(rates['labour_USD_h']);machine=triple(rates['machine_USD_h']);qa=triple(rates['QA_USD_h']);overhead=triple(rates['overhead_fraction'])
    if reported is not None and (not isinstance(reported,dict) or set(reported)!=set(CASES)):raise ValueError('Exact low/base/high cost breakdown cases required')
    rows={};unknown=[];unverified=[]
    for i,c in enumerate(CASES):
        row=None if reported is None else reported[c]
        if row is not None and (not isinstance(row,dict) or set(row)!=set(fields)):raise ValueError('Exact five material/process/machine/QA/overhead breakdown keys required')
        actual={}
        for key in fields:
            value=None if row is None else row[key]
            if value is not None:
                value=number(value)
                if value<0:raise ValueError('Known cost component must be nonnegative: '+c+'/'+key)
            else:unknown.append(c+'/'+key)
            actual[key]=value
        expected=dict(material=None if rho is None or price is None else gross*rho[i]*price[i],process=None if ph is None or labour is None else ph[i]*labour[i],machine=None if mh is None or machine is None else mh[i]*machine[i],QA=None if qh is None or qa is None else qh[i]*qa[i])
        base_known=all(v is not None for v in expected.values());expected['overhead']=None if overhead is None or not base_known else fsum(expected.values())*overhead[i]
        verified=[]
        for key in fields:
            if actual[key] is None:continue
            if expected[key] is None:unverified.append(c+'/'+key);continue
            if not close(actual[key],expected[key]):raise ValueError('Known cost component differs from its stock/rate/hour inputs: '+c+'/'+key)
            verified.append(key)
        known_sum=fsum(v for v in actual.values() if v is not None);all_reported=all(v is not None for v in actual.values())
        if total is not None:
            if all_reported and not close(known_sum,total[i]):raise ValueError('Part cost component sum differs from declared total')
            if not all_reported and known_sum>total[i]+1e-13+1e-9*max(abs(known_sum),abs(total[i])):raise ValueError('Known nonnegative cost components exceed declared partial total')
            if all(v is not None for v in expected.values()) and not close(total[i],fsum(expected.values())):raise ValueError('Calculated material/process/machine/QA/overhead total differs')
        rows[c]=dict(reported=deepcopy(actual),expected_from_known_inputs=expected,verified_components=verified,component_sum_reconciled=total is not None and all_reported,reported_total=None if total is None else total[i])
    return dict(cases=rows,unknown_reported_components=unknown,reported_components_with_unknown_inputs=unverified,all_reported_components_reconciled=not unknown and not unverified,scope='Declared direct part material/process/machine/QA/overhead only; no complete installed-cost claim',unknown_reports_filled=False)


def _check_prototype(p):
    source_seal(p)
    if set(p)!=PROTO_FIELDS:raise ValueError('Unsupported unconsumed prototype wrapper fields')
    if p.get('schema')!='osr-terminal-hardware-prototype/1' or p['candidate_id']!=source_identity(p['physical_definition']):raise ValueError('Prototype source physical identity differs')
    parts=p['parts']
    if len(parts)!=p['manufactured_piece_count'] or len({x['id'] for x in parts})!=len(parts):raise ValueError('Prototype part ownership/count differs')
    expected={k:deepcopy(p['physical_definition'][k]) for k in ('schema','family','size','quantity_per_source_end')}
    expected['parts']=[{k:deepcopy(v) for k,v in x.items() if k not in SOURCE_PART_EVAL} for x in parts]
    # Reproduce the upstream's narrow top-level mate projection solely to verify
    # it. Our own context-aware physical projection is independent below.
    expected['mating']=[{k:deepcopy(v) for k,v in m.items() if k not in MATE_EVIDENCE|{'fork_driver'}} for m in p['mating']]
    if expected!=p['physical_definition'] or p['family']!=expected['family'] or p['size']!=expected['size']:raise ValueError('Prototype full material/mating projection differs')
    if any(v is not False for v in p['approvals'].values()):raise ValueError('Prototype cannot confer approval')
    if type(p['physical_definition']['quantity_per_source_end']) is not int or p['physical_definition']['quantity_per_source_end']<1:raise ValueError('Positive explicit source family quantity required')
    for part in parts:
        if part['frame']!='part-X-insertion' or not isinstance(part['material'],str) or not part['material']:raise ValueError('Explicit part axes/material required')
        if type(part.get('source_quote')) is not bool:raise ValueError('Source quotation evidence flag must be boolean; no structured field erasure')
        lo,hi=interval(part['net_volume_bounds_m3'],True);gross=number(part['gross_blank_volume_m3'],True);base=number(part['net_volume_base_m3'],True)
        if hi>gross+1e-12 or not close(base,(lo+hi)/2):raise ValueError('Positive source stock/net bound differs')
        exact=exact_simple_volume(part['geometry'])
        if exact is not None and (not close(lo,exact) or not close(hi,exact)):raise ValueError('Explicit primitive/ring material volume differs from source stock')
        factor=number(part.get('mass_volume_factor',1.),True);density=triple(p['materials'][part['material']]['density_kg_m3'],positive=True);mass=labels(part.get('mass_kg'),positive=True)
        if mass is not None and density is not None and any(not close(m,v*factor*r) for m,v,r in zip(mass,[lo,base,hi],density)):raise ValueError('Part mass/free-state density conservation differs')
        paid=labels(part.get('paid_stock_kg'),positive=True)
        if paid is not None and density is not None and any(not close(m,gross*r) for m,r in zip(paid,density)):raise ValueError('Paid blank material differs')
        if factor!=1.:
            if part['material']!='EPDM-cellular-unqualified' or 'free_shape' not in part or not close(number(part['free_net_volume_m3'],True),base*factor) or not close(number(part['installed_bulk_density_multiplier'],True),factor):raise ValueError('Explicit cellular free/compressed constant-mass model required')
            material_bounds(part['free_shape'])
            free=exact_simple_volume(part['free_shape'])
            if free is not None and not close(free,part['free_net_volume_m3']):raise ValueError('Cellular free shape/material volume differs')
        for key in ('person_process_h','person_QA_h','machine_h'):triple(part.get(key))
        _cost_components(part,p)
        material_bounds(part['geometry'])
    for field,child in (('mass_kg','mass_kg'),('cost_USD','cost_USD')):
        known=[labels(x.get(child),positive=field=='mass_kg') for x in parts];total=labels(p.get(field),positive=field=='mass_kg')
        if total is not None and all(x is not None for x in known) and any(not close(total[i],fsum(x[i] for x in known)) for i in range(3)):raise ValueError('Prototype total material/process counted incorrectly')
    return p


def _cut(h):
    """Signed cylinder BASE -> centre explicitly; component-global source axis."""
    if h.get('kind')!='cylinder-cut':raise ValueError('Explicit source cylinder cut required')
    axis=vector(h['axis']);j=next((j for j in range(3) if abs(axis[j])==1. and all(axis[k]==0 for k in range(3) if k!=j)),None)
    if j is None:raise ValueError('Principal signed source-cut axis required')
    base=vector(h['at_m']);L=number(h['length_m'],True);r=number(h['diameter_m'],True)/2;c=add(base,[v*L/2 for v in axis]);return dict(axis=j,centre_m=c,radius_m=r,length_m=L)

def _cylinder_union(cuts):
    if not cuts:return []
    if len(cuts)>128 or len({x['axis'] for x in cuts})!=1:raise ValueError('Bounded parallel source cut domain required')
    axis=cuts[0]['axis'];other=[k for k in range(3) if k!=axis]
    for i,a in enumerate(cuts):
        for b in cuts[i+1:]:
            d=sqrt(fsum((a['centre_m'][k]-b['centre_m'][k])**2 for k in other));overlap=min(a['centre_m'][axis]+a['length_m']/2,b['centre_m'][axis]+b['length_m']/2)-max(a['centre_m'][axis]-a['length_m']/2,b['centre_m'][axis]-b['length_m']/2)
            if d and d<a['radius_m']+b['radius_m'] and overlap>1e-12:raise ValueError('Noncoaxial overlapping source bores need independent union domain')
    out=[]
    for yz in sorted({tuple(c['centre_m'][k] for k in other) for c in cuts}):
        group=[c for c in cuts if tuple(c['centre_m'][k] for k in other)==yz];ends=sorted({c['centre_m'][axis]+s*c['length_m']/2 for c in group for s in (-1,1)})
        for a,b in zip(ends,ends[1:]):
            radii=[c['radius_m'] for c in group if c['centre_m'][axis]-c['length_m']/2<=a+1e-14 and c['centre_m'][axis]+c['length_m']/2>=b-1e-14]
            if not radii:continue
            centre=[0.,0.,0.];centre[axis]=(a+b)/2
            for k,v in zip(other,yz):centre[k]=v
            out.append(dict(axis=axis,centre_m=centre,radius_m=max(radii),length_m=b-a))
    return out

def _cut_moments(cuts):
    vs=[pi*c['radius_m']**2*c['length_m'] for c in cuts];return fsum(vs),[fsum(v*c['centre_m'][k] for v,c in zip(vs,cuts)) for k in range(3)]


def finishing_plan(op,materials):
    """New-build void union/increment only. No source stock/CG debit applied."""
    if op.get('source_cylinder_position_convention')!='at_m is base; signed axis points into cut' or op.get('original_paid_blank_retained') is not True or number(op.get('source_credit_USD'))!=0.:raise ValueError('Explicit signed-base/once-only paid blank contract required')
    g=op['source_geometry'];outer=g['geometry']['outer'] if op['kind']=='ring-access-port-enlargement' else g['geometry'];b=material_bounds(outer)
    if b is None or outer['kind']!='box' or proper(outer['rotation'])!=I:raise ValueError('Exact supported source finishing blank required')
    old=[_cut(h) for h in g['holes']];before=_cylinder_union(old);pieces=op['complete_void_union']
    if pieces.get('kind')!='union' or not isinstance(pieces.get('pieces'),list):raise ValueError('Complete future source void union required')
    ps=pieces['pieces'];old_geometry=g['geometry'];low=[];high=[];aperture=None
    if op['kind']=='hardpoint-thread-pocket':
        if len(old)!=1 or len(ps)!=2 or ps[0]!=g['holes'][0] or ps[1].get('kind')!='thread-bounded-cut':raise ValueError('Retained through void plus one bounded stopped thread required')
        h=ps[1];axis=vector(h['axis']);depth=number(h['depth_m'],True);tol=number(h['depth_tolerance_m'],True)
        if depth<=tol or h.get('flat_bottom') is not True or not 0<number(h['pilot_diameter_m'],True)<number(h['major_diameter_m'],True):raise ValueError('Explicit positive bounded stopped thread required')
        number(h['pitch_m'],True);number(h['full_thread_depth_m'],True)
        for target,D,L in ((low,h['pilot_diameter_m'],depth-tol),(high,h['major_diameter_m'],depth+tol)):
            target.extend(old);target.append(_cut(dict(kind='cylinder-cut',at_m=h['at_m'],axis=axis,diameter_m=D,length_m=L)))
        if not close(op['maximum_pocket_depth_m'],depth+tol) or not close(op['minimum_annular_rear_web_m'],outer['size_m'][0]-(depth+tol)):raise ValueError('Pocket depth/rear web scope differs')
    elif op['kind']=='ring-access-port-enlargement':
        if op.get('blank_owner_count')!=1 or type(op.get('blank_owner_count')) is not int or op.get('new_stock_purchase_count')!=0 or op.get('cut_count')!=12 or len(old)!=12 or len(ps)!=25 or ps[0]!=old_geometry['void'] or ps[1:13]!=g['holes']:raise ValueError('One retained backing ring/twelve original and enlarged bores required')
        aperture=material_bounds(old_geometry['void']);D=number(op['access_diameter_m'],True);dt=number(op['diameter_tolerance_m'],True)
        for i,h in enumerate(ps[13:]):
            c=_cut(h);o=old[i]
            if c['axis']!=o['axis'] or any(not close(a,b) for a,b in zip(c['centre_m'],o['centre_m'])) or not close(c['length_m'],o['length_m']) or not close(2*c['radius_m'],D):raise ValueError('Backing ring enlargement cannot relocate old axes')
            for target,d in ((low,D-dt),(high,D+dt)):
                if d<=2*o['radius_m']:raise ValueError('Backing ring enlargement bounds must exceed old holes')
                target.append(dict(c,radius_m=d/2))
        low=old+low;high=old+high
    else:raise ValueError('Unknown source finishing operation')
    for c in low+high:
        axis=c['axis'];cb=[[c['centre_m'][k]-(c['length_m']/2 if k==axis else c['radius_m']),c['centre_m'][k]+(c['length_m']/2 if k==axis else c['radius_m'])] for k in range(3)]
        if not _contains_box(b,cb):raise ValueError('New cut exits paid source blank')
        if aperture is not None:
            other=[k for k in range(3) if k!=axis];distance=sqrt(fsum(max(aperture[k][0]-c['centre_m'][k],0.,c['centre_m'][k]-aperture[k][1])**2 for k in other))
            if distance<c['radius_m']-1e-12:raise ValueError('Cut/aperture union outside disjoint source domain')
    lo=_cylinder_union(low);hi=_cylinder_union(high);vb,mb=_cut_moments(before);vl,ml=_cut_moments(lo);vh,mh=_cut_moments(hi);dv=[vl-vb,vh-vb]
    if dv[0]<=0 or dv[1]<dv[0] or any(not close(a,b) for a,b in zip(interval(op['incremental_removed_volume_bounds_m3'],True),dv)):raise ValueError('Incremental source union volume differs; old holes cannot be counted again')
    rho=triple(materials[op['material']]['density_kg_m3'],positive=True);mass=None if rho is None else [dv[0]*rho[0],dv[1]*rho[2]];box=two_corner_box(op['incremental_removed_centroid_box_m']);provided=interval_box(op['incremental_removed_first_moment_bounds_kg_m'])
    if mass is not None:
        if any(not close(a,b) for a,b in zip(interval(op['incremental_removed_mass_bounds_kg'],True),mass)):raise ValueError('Source finishing removed mass differs')
        for k in range(3):
            conservative=[min(m*x for m in mass for x in box[k]),max(m*x for m in mass for x in box[k])]
            if provided[k][0]>conservative[0]+1e-12 or provided[k][1]<conservative[1]-1e-12:raise ValueError('Removed first moment omits declared support bounds')
            for v,moment in ((dv[0],ml[k]-mb[k]),(dv[1],mh[k]-mb[k])):
                if not box[k][0]-1e-12<=moment/v<=box[k][1]+1e-12:raise ValueError('Declared removed centroid bound misses union endpoint')
    return dict(id=op['id'],frame='terminal-local-UVW',units='m',source_entity_id=op['source_entity_id'],source_stock_owner_id=op['source_stock_owner_id'],source_complete_void_union=deepcopy(op['complete_void_union']),minimum_circular_cut_union=lo,maximum_circular_cut_union=hi,retained_original_circular_union=before,retained_aperture=deepcopy(aperture),incremental_removed_volume_bounds_m3=dv,incremental_removed_mass_bounds_kg=mass,incremental_removed_first_moment_interval_kg_m=deepcopy(provided),incremental_removed_centroid_interval_m=box,source_operation=deepcopy(op),paid_blank_retained_once=True,source_mass_and_first_moment_application='REQUIRED_NOT_APPLIED; exact canonical source-key and owner mapping absent',remaining_net_mass_and_CG=None,extra_material_purchase=None,tool_native_qualification=False)


def _physical_source_ops(ops):
    out=[]
    for op in ops:
        g=op['source_geometry'];keys=('geometry','holes','material','insert_pocket_max_depth_m','insert_pocket_max_diameter_m') if op['kind']=='hardpoint-thread-pocket' else ('geometry','holes')
        row={k:deepcopy(op[k]) for k in ('id','kind','source_entity_id','source_stock_owner_id','complete_void_union')};row['source_material_geometry']={k:deepcopy(g[k]) for k in keys}
        if op['kind']=='hardpoint-thread-pocket':row.update({k:op[k] for k in ('maximum_pocket_depth_m','minimum_annular_rear_web_m')})
        else:row.update(access_diameter_m=op['access_diameter_m'],diameter_tolerance_m=op['diameter_tolerance_m'],axis_position_tolerance_m=op['axis_position_tolerance_m'],material='al5083')
        out.append(row)
    return out


def normalize(raw,*,pin,request_id):
    """Normalize one authenticated completed local definition; no generation."""
    hexid(request_id);source_seal(raw)
    if set(raw)!=TOP_FIELDS:raise ValueError('Unsupported unconsumed local hardware wrapper fields')
    for k in ('candidate_id','evaluation_id','raw_sha256','source_request_id','source_execution_id'):hexid(pin[k])
    if pin['source_commit']!=SOURCE_COMMIT or pin['source_module_sha256']!=SOURCE_SHA256 or pin['candidate_id']!=raw['candidate_id'] or pin['evaluation_id']!=raw['evaluation_id'] or pin['source_request_id']!=raw['request_id']:raise ValueError('Exact e849 source/content/execution pins required')
    if raw['schema']!='osr-terminal-hardware-local-proposal/1' or raw['parent']!=PARENT or raw['candidate_id']!=source_identity(raw['physical_definition']):raise ValueError('Exact local hardware physical/parent identity required')
    if any(raw[k] is not False for k in ('physical_accepted','engineering_accepted','native_eligible','manufacturing_release','operating_release','composition_admitted','selected_reference_changed','complete_installed_cost')) or raw['selection_id'] is not None:raise ValueError('Upstream hardware cannot confer acceptance/selection')
    protos={k:_check_prototype(v) for k,v in raw['prototypes'].items()};occ=raw['occurrences'];byocc={o['id']:o for o in occ};counts={k:0 for k in FAMILIES}
    policies={(identity(p['materials']),identity(p['rates'])) for p in protos.values()}
    if len(policies)!=1:raise ValueError('Mixed prototype material/rate policy epochs refused')
    if len(occ)!=sum(FAMILIES.values()) or len(byocc)!=len(occ):raise ValueError('Complete unique hardware placement roster required')
    for o in occ:
        if o['prototype_key'] not in protos:raise ValueError('Missing occurrence prototype')
        p=protos[o['prototype_key']]
        if p['family'] not in counts:raise ValueError('Unknown source hardware family')
        counts[p['family']]+=1
        if o['placement']['frame']!='terminal-local-UVW':raise ValueError('Unchanged terminal frame required')
        vector(o['placement']['at_m']);proper(o['placement']['rotation']);hexid(o['source_entity_sha256'])
        if o['id']!='hardware/'+o['old_entity_id']:raise ValueError('Exact source occurrence namespace required')
    if counts!=FAMILIES or set(protos)!={o['prototype_key'] for o in occ}:raise ValueError('Complete source family/used prototype coverage required')
    for key,p in protos.items():
        if key!=(p['family']+'/'+p['size'] if p['family']=='thread-guard' else p['family']) or sum(o['prototype_key']==key for o in occ)!=p['physical_definition']['quantity_per_source_end']:raise ValueError('Prototype key/physical family quantity differs')
    replacements=raw['replacement_plan'];oldmap={x['old_entity_id']:x for x in replacements};stock_replacements=raw['source_stock_owner_replacements'];owners={x['source_group_id']:x for x in stock_replacements}
    if len(oldmap)!=len(replacements) or len(owners)!=len(stock_replacements) or len(owners)!=len(FAMILIES) or {x['successor_occurrence_id'] for x in replacements}!=set(byocc):raise ValueError('Once-only original replacement/owner map required')
    for o in occ:
        if o['old_entity_id'] not in oldmap:raise ValueError('Missing old occurrence disposition')
        r=oldmap[o['old_entity_id']]
        if r['successor_occurrence_id']!=o['id'] or r['old_stock_group_id'] not in owners or r['old_mass_or_price_added_to_new'] is not False or r['canonical_applied'] is not False or not r['old_part_id']==o['source_part_id']==r['old_entity']['part_id']:raise ValueError('Old material/price disposition cannot be reused/applied')
        g=owners[r['old_stock_group_id']]
        if r['old_entity_id'] not in g['old_entity_ids'] or r['old_entity_id']!=r['old_entity']['id'] or source_identity(r['old_entity'])!=o['source_entity_sha256']:raise ValueError('Exact old occurrence provenance differs')
    seenold=[]
    for oid,g in owners.items():
        if g['source_group']['id']!=oid or set(g['source_group']['entity_ids'])!=set(g['old_entity_ids']) or g['once_only'] is not True or g['applied'] is not False or g['source_price_not_added'] is not True:raise ValueError('Original source stock coverage/disposition differs')
        if len(set(g['old_entity_ids']))!=len(g['old_entity_ids']) or len(set(g['successor_ids']))!=len(g['successor_ids']) or set(g['successor_ids'])!={r['successor_occurrence_id'] for r in replacements if r['old_stock_group_id']==oid}:raise ValueError('Duplicate/missing successor stock membership')
        seenold+=g['old_entity_ids']
    if len(seenold)!=len(set(seenold)) or set(seenold)!=set(oldmap):raise ValueError('Every old occurrence retired once required')
    physical=raw['physical_definition'];expected=dict(schema='osr-terminal-hardware-local-physical/2',parent_candidate_id=PARENT['candidate_id'],fixed_source_interfaces=physical['fixed_source_interfaces'],new_prototypes={k:p['physical_definition'] for k,p in protos.items()},placements=[{k:deepcopy(o[k]) for k in ('id','prototype_key','placement','old_entity_id','source_part_id')} for o in occ],source_machining=_physical_source_ops(raw['source_machining']),prospective_replacements=[dict(old=r['old_entity_id'],new=r['successor_occurrence_id']) for r in replacements])
    if physical!=expected:raise ValueError('Lossless source physical placement/geometry/machining projection differs')
    holds=[dict(code='canonical-source-map',reason='Exact predecessor canonical source-key/finishing owner map and13source owner dispositions require independent composition review; none applied'),dict(code='thread-and-CSG-domain',reason='Min/max thread and Boolean material graphs preserved; helix/locking/contact/native solids not proved'),dict(code='inherited-terminal-contracts',reason='Original183weld/89joint and unchanged terminal obligations remain required; complete IDs/counterpart binding not supplied by hardware-only source'),dict(code='mass-inertia-bounds',reason='Marginal nonnegative-material containment intervals only, no fabricated pointCG/centroidal inertia/stability proof'),dict(code='manufacturing-service-physical',reason='Grades/WPS/thread/preload/creep/glazing/fire/cure/corrosion/whole-assembly continuous tools and repair capacity unqualified')]
    entities=[];stocks=[];interfaces=[];mapping={};total_mass={c:0. for c in CASES};total_cost={c:0. for c in CASES};known_mass=True;known_cost=True
    for o in occ:
        p=protos[o['prototype_key']];T=vector(o['placement']['at_m']);R=proper(o['placement']['rotation']);ids=[];piece_rows=[]
        for part in p['parts']:
            eid=o['id']+'/'+part['id'];ids.append(eid);box=material_bounds(part['geometry']);mass=labels(part.get('mass_kg'),positive=True);cost=labels(part.get('cost_USD'));mi=None if mass is None else [mass[0],mass[2]]
            localmp=containment_moments(box,mi);worldmp=containment_moments(box,mi,T,R)
            account_check=_cost_components(part,p)
            if not account_check['all_reported_components_reconciled']:holds.append(dict(code='partial-cost-component-evidence',entity_id=eid,unknown_components=account_check['unknown_reported_components'],unverified_components=account_check['reported_components_with_unknown_inputs'],reason='None/partial decomposition or unknown rate/hour inputs preserved; no zero or invented allocation'))
            if box is None:holds.append(dict(code='unsupported-material-graph-bound',entity_id=eid,source_kind=part['geometry']['kind'],reason='Full source graph preserved; bound unknown, no filled packaging'))
            if mass is None or cost is None:holds.append(dict(code='unknown-material-or-price',entity_id=eid,reason='None retained; no zero substitution'))
            state={k:deepcopy(part[k]) for k in ('mass_volume_factor','free_shape','free_net_volume_m3','installed_bulk_density_multiplier','finish') if k in part}
            e=dict(id=eid,scope='installed',frame='terminal-local-UVW',material_id=part['material'],at_m=T,rotation=R,geometry=dict(kind='source-bounded-CSG-material',source_graph=deepcopy(part['geometry']),units='m',not_filled_packaging=True),material_state=state,source_part_id=part['id'],source_occurrence_id=o['id'],source_prototype_key=o['prototype_key'],source_stock_owner_id='new/'+o['id'],mass_label_cases_kg=deepcopy(part.get('mass_kg')),mass_properties_part_frame=localmp,mass_properties_terminal_frame=worldmp,source_part=deepcopy(part),cost_component_verification=account_check,**FLAGS);entities.append(e);piece_rows.append(dict(entity_id=eid,part_id=part['id'],source_account=deepcopy(part),mass_label_cases_kg=deepcopy(part.get('mass_kg')),direct_cost_label_cases_USD=deepcopy(part.get('cost_USD')),cost_component_verification=account_check))
        if len(set(ids))!=len(ids):raise ValueError('Duplicate occurrence piece identity')
        pm=labels(p.get('mass_kg'),positive=True);pc=labels(p.get('cost_USD'));known_mass &= pm is not None;known_cost &= pc is not None
        for i,c in enumerate(CASES):
            if pm is not None:total_mass[c]+=pm[i]
            if pc is not None:total_cost[c]+=pc[i]
        stocks.append(dict(id='new/'+o['id'],scope='installed',entity_ids=ids,procurement_quantity=1,old_occurrence_id=o['old_entity_id'],source_owner_group_id=oldmap[o['old_entity_id']]['old_stock_group_id'],mass_label_cases_kg=deepcopy(p.get('mass_kg')),direct_cost_label_cases_USD=deepcopy(p.get('cost_USD')),part_account_rows=piece_rows,parts_are_subtotals_not_extra_payable_rows=True,old_material_or_price_added=False,disposition='prospective-replace-source-occurrence_REQUIRED_NOT_APPLIED',source_key_map=None,complete_installed_cost=False))
        mapping[o['id']]=ids;interfaces.append(dict(id='hardware-contract/'+o['id'],schema='osr-hardware-part-mating/1',frame='part-X-insertion',part_ids=ids,placement=deepcopy(o['placement']),physical_contracts=_mates_physical(p['mating']),source_contracts=deepcopy(p['mating']),source_occurrence=deepcopy(o),status='required-unresolved',all_counterparts_bound=False,physical_qualified=False))
    if len({e['id'] for e in entities})!=len(entities):raise ValueError('Duplicate expanded material occurrence')
    ops=raw['source_machining'];source_owners=raw['source_machining_stock_owners']
    if len(ops)!=13 or len({x['id'] for x in ops})!=13 or len({x['source_entity_id'] for x in ops})!=13:raise ValueError('Complete thirteen unique finishing occurrences required')
    finishes=[finishing_plan(x,next(iter(protos.values()))['materials']) for x in ops]
    if {x['source_stock_owner_id'] for x in ops}!=set(source_owners) or len(source_owners)!=2 or set(source_owners)&set(owners):raise ValueError('Two separate retained finishing paid groups required, not13new purchases')
    for op in ops:
        if op['source_entity_id'] not in source_owners[op['source_stock_owner_id']]['entity_ids']:raise ValueError('Finishing source stock ownership differs')
    ring=[o for o in ops if o['kind']=='ring-access-port-enlargement']
    if len(ring)!=1:raise ValueError('Exactly one paid backing ring required')
    toolkit=raw['shared_workshop_service_kit']
    if toolkit.get('piece_count')!=12 or len(toolkit['parts'])!=12 or len({p['id'] for p in toolkit['parts']})!=12 or type(toolkit.get('count_per_train')) is not int or toolkit['count_per_train']!=1 or toolkit.get('qualified') is not False:raise ValueError('One shared twelve-piece unqualified toolkit required')
    if source_identity(toolkit['physical_definition'])!=toolkit['lifecycle_definition_id']:raise ValueError('Tool lifecycle physical seal differs')
    toolphysical=dict(schema='osr-terminal-workshop-tool-physical/1',scope='One shared workshop kit, not installed railway material',parts=[dict(id=p['id'],material=p['material'],geometry=p['geometry'],paid_blank=p['paid_blank'],gross_volume_m3=p['gross_blank_volume_m3'],net_volume_bounds_m3=p['net_volume_bounds_m3']) for p in toolkit['parts']])
    if toolkit['physical_definition']!=toolphysical:raise ValueError('Complete shared tool material/procurement projection differs')
    # Tool prices do not enter installed material identity, nor do fixture or
    # repair consumables silently become per-end installed hardware purchases.
    lifecycle=[dict(id='terminal-hardware/shared-front-service-kit',scope='lifecycle',count_per_train=1,source=deepcopy(toolkit),charged_in_installed_stock=False),dict(id='terminal-hardware/workshop-residual',scope='lifecycle',source=deepcopy(raw['workshop']),charged_in_installed_stock=False,deduplicate_by_train_owner=True),dict(id='terminal-hardware/repair-consumables',scope='lifecycle',source=deepcopy(raw['repair_consumables_per_glazing_service']),charged_in_installed_stock=False,event_frequency=None)]
    finishing_cost={c:0. for c in CASES};finishing_known=True
    for op in ops:
        cost=labels(op.get('cost_USD'));finishing_known &= cost is not None
        for i,c in enumerate(CASES):
            if cost is not None:finishing_cost[c]+=cost[i]
    if known_mass and raw.get('new_parts_mass_kg') is not None and any(not close(raw['new_parts_mass_kg'][c],total_mass[c]) for c in CASES):raise ValueError('195piece/167owner new mass conservation differs')
    if known_cost and finishing_known and raw.get('new_parts_cost_USD') is not None and any(not close(raw['new_parts_cost_USD'][c],total_cost[c]+finishing_cost[c]) for c in CASES):raise ValueError('Hardware plus once-only finishing cost differs')
    projection=dict(schema='osr-terminal-hardware-component-physical/1',units='m',frame='terminal-local-UVW',entities=[dict(id=e['id'],scope=e['scope'],material_id=e['material_id'],frame=e['frame'],at_m=e['at_m'],rotation=e['rotation'],part_definition=_part_physical(e['source_part'])) for e in entities],source_finishing=deepcopy(physical['source_machining']),interfaces=[dict(id=x['id'],schema=x['schema'],part_ids=x['part_ids'],placement=x['placement'],physical_contracts=x['physical_contracts']) for x in interfaces])
    packet=dict(schema='osr-terminal-hardware-component-normalization/1',units='m',component_geometry_id=identity(projection),physical_definition=projection,request_id=request_id,source_pin=deepcopy(pin),source_candidate_id=raw['candidate_id'],source_evaluation_id=raw['evaluation_id'],source_original_definition=deepcopy(raw),canonical_definition=None,canonical_draft=dict(schema='osr-terminal-hardware-nonadmitted-draft/1',entities=entities,stock_groups=stocks,required_interfaces=interfaces,required_source_finishing=finishes,old_stock_owner_dispositions=[dict(source_owner_id=k,source=deepcopy(v),status='REQUIRED_NOT_APPLIED',canonical_source_key_map=None) for k,v in owners.items()],source_finishing_owner_dispositions=[dict(source_owner_id=k,source=deepcopy(v),operation_ids=[o['id'] for o in ops if o['source_stock_owner_id']==k],paid_blank_count=1,stock_purchase_count=0,source_mass_and_moment_update_applied=False,canonical_source_key_map=None,status='finish-existing-paid-new-build-blank_REQUIRED_NOT_APPLIED') for k,v in source_owners.items()],all_required_interfaces_resolved=False),mapping=mapping,counts=dict(placements=len(occ),material_pieces=len(entities),new_stock_groups=len(stocks),old_owner_groups=len(owners),source_finishing_operations=len(finishes),finishing_source_occurrences=13,finishing_paid_owner_groups=len(source_owners),paid_backing_rings=1,shared_service_tool_pieces=12),known_new_parts_mass_label_cases_kg=total_mass if known_mass else None,known_new_hardware_direct_cost_label_cases_USD=total_cost if known_cost else None,known_source_finishing_direct_cost_label_cases_USD=finishing_cost if finishing_known else None,lifecycle_allocations=lifecycle,held_facts=holds,original_source_contracts_and_holds=deepcopy(raw['holds']),complete_installed_mass=False,complete_installed_cost=False,source_owner_transactions_applied=False,upstream_validation_inherited=False,**FLAGS)
    packet['evaluation_id']=identity(packet);return packet
