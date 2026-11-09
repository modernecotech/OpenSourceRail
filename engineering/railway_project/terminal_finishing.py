"""Complete bounded material rebuild of the fe2/e849 local finishing family.

The old hardpoint pocket reserve is accounting ancestry, never a second void.
Moment bounds are outward-rounded marginal research enclosures, not correlated
scenarios, measured properties, exact pointCG or centroidal inertia tensors.
"""
from copy import deepcopy
from hashlib import sha256
import json
from math import fsum, isfinite, nextafter, inf, pi, sqrt

I = [[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
CASES = ('low','base','high')
FRAME = 'terminal-local-UVW'
FLAGS = dict(canonical_admitted=False, native_eligible=False, physical_accepted=False,
             installed_assembly_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             selected_reference_changed=False, release_approved=False)


def identity(x):return sha256((json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()
def noLF(x):return sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def seal(x):return dict(deepcopy(x),evaluation_id=identity(x))
def number(x,positive=False):
    if type(x) not in (int,float) or not isfinite(x) or positive and x<=0:raise ValueError('Finite nonboolean SI scalar required')
    return float(x)
def vector(x):
    if not isinstance(x,list) or len(x)!=3:raise ValueError('Three explicit coordinates required')
    return [number(v) for v in x]
def integer(x):
    if type(x) is not int or x<0:raise ValueError('Nonboolean nonnegative count required')
    return x
def hexid(x):
    if not isinstance(x,str) or len(x)!=64 or any(c not in '0123456789abcdef' for c in x):raise ValueError('Explicit64hex identity required')
    return x
def checkseal(x):
    if x['evaluation_id']!=identity({k:v for k,v in x.items() if k!='evaluation_id'}):raise ValueError('Stale evaluation seal')
def near(a,b):return abs(number(a)-number(b))<=1e-13+1e-9*max(abs(a),abs(b))
def same(a,b):
    if len(a)!=len(b) or not all(near(x,y) for x,y in zip(a,b)):raise ValueError('Source dimension/pose contract differs')
def index(xs):
    out={}
    for x in xs:
        k=x['id']
        if not isinstance(k,str) or not k or k in out:raise ValueError('Explicit unique source identifiers required')
        out[k]=x
    return out

# Every arithmetic operation expands one floating-point step outward.
def down(x):return nextafter(x,-inf)
def up(x):return nextafter(x,inf)
def point(x):x=number(x);return [x,x]
def interval(x):
    if not isinstance(x,list) or len(x)!=2 or number(x[0])>number(x[1]):raise ValueError('Ordered explicit bounds required')
    return list(x)
def plus(a,b):return [down(a[0]+b[0]),up(a[1]+b[1])]
def minus(a,b):return [down(a[0]-b[1]),up(a[1]-b[0])]
def times(a,b):
    z=[x*y for x in a for y in b];return [down(min(z)),up(max(z))]
def divide(a,b):
    if b[0]<=0:raise ValueError('Positive denominator interval required')
    return times(a,[down(1/b[1]),up(1/b[0])])
def square(a):return [0. if a[0]<=0<=a[1] else down(min(x*x for x in a)),up(max(x*x for x in a))]
def total(xs):
    ans=[0.,0.]
    for x in xs:ans=plus(ans,x)
    return ans

def box_moments(size,centre):
    s=[point(number(x,True)) for x in size];C=[interval(c) for c in centre];V=times(times(s[0],s[1]),s[2]);F=[times(V,c) for c in C];Q=[]
    for i in range(3):Q.append([times(V,plus(times(C[i],C[j]),divide(square(s[i]),point(12.))) if i==j else times(C[i],C[j])) for j in range(3)])
    return dict(V=V,F=F,Q=Q)

def cylinder_moments(L,r,centre):
    L=interval(L);r=interval(r);C=[interval(c) for c in centre]
    if min(L+r)<=0:raise ValueError('Positive finite cylinder domain required')
    V=times(times([down(pi),up(pi)],square(r)),L);F=[times(V,c) for c in C];Q=[]
    for i in range(3):
        variance=divide(square(L),point(12.)) if i==0 else divide(square(r),point(4.))
        Q.append([times(V,plus(times(C[i],C[j]),variance) if i==j else times(C[i],C[j])) for j in range(3)])
    return dict(V=V,F=F,Q=Q)

def subtract(a,b):return dict(V=minus(a['V'],b['V']),F=[minus(x,y) for x,y in zip(a['F'],b['F'])],Q=[[minus(a['Q'][i][j],b['Q'][i][j]) for j in range(3)] for i in range(3)])
def support_box(size,T):return [[down(T[k]-size[k]/2),up(T[k]+size[k]/2)] for k in range(3)]
def corner_C(x):return [point(v) for v in x]

def properties(moments,rho,uncertainty,support):
    V=moments['V']
    if V[0]<=0:raise ValueError('Positive complete remaining material required')
    U=vector(uncertainty)
    if min(U)<0:raise ValueError('Nonnegative source position uncertainty required')
    D=[[-v,v] for v in U];F=moments['F'];Q=moments['Q'];FU=[plus(F[i],times(V,D[i])) for i in range(3)];QU=[]
    for i in range(3):QU.append([plus(plus(plus(Q[i][j],times(D[i],F[j])),times(D[j],F[i])),times(V,times(D[i],D[j]))) for j in range(3)])
    def report(ff,qq,bb):
        cg=[divide(f,V) for f in ff]
        for k in range(3):cg[k]=[max(cg[k][0],bb[k][0]),min(cg[k][1],bb[k][1])]
        tensor=[]
        for i in range(3):
            row=[]
            for j in range(3):
                x=total(qq[k][k] for k in range(3) if k!=i) if i==j else times(point(-1),qq[i][j]);x=times(point(rho),x)
                if i==j:x[0]=max(0.,x[0])
                row.append(x)
            tensor.append(row)
        return dict(first_moment_interval_kg_m=[times(point(rho),f) for f in ff],centroid_interval_m=cg,inertia_about_terminal_origin_interval_kg_m2=tensor,exact_point_CG_m=None,centroidal_tensor_kg_m2=None)
    return dict(net_volume_interval_m3=V,mass_interval_kg=times(point(rho),V),nominal_datum=report(F,Q,support),with_source_position_uncertainty=report(FU,QU,[[down(support[k][0]-U[k]),up(support[k][1]+U[k])] for k in range(3)]),source_position_uncertainty_m=U,
                method='Outward marginal interval arithmetic on complete material; uncertain thread phase/independent ports and pose translations are enclosed, correlations not promoted to point scenarios',uniform_density_research_kg_m3=rho,physical_mass_CG_qualification=None)

def account_cases(v):
    if v is None:return None
    if not isinstance(v,dict) or set(v)!=set(CASES):raise ValueError('Known case labels or explicitunknown required')
    values=[number(v[c]) for c in CASES]
    if min(values)<0 or values!=sorted(values):raise ValueError('Known nonnegative ordered price required')
    return deepcopy(v)


def identity_frame(R):
    if not isinstance(R,list) or len(R)!=3:raise ValueError('Explicit sourceI rotation required')
    for row in R:vector(row)
    if R!=I:raise ValueError('Unsupported source rotation domain')
    return R


BOX_FIELDS={'kind','size_m','at_m','rotation'}
COMMON_CSG_FIELDS={'id','part_id','material','geometry','holes','geometry_hold','old_entity_sha256'}
HARDPOINT_CSG_FIELDS=COMMON_CSG_FIELDS|{'actual_insert_geometry_held','insert_pocket_max_depth_m','insert_pocket_max_diameter_m'}
RING_CSG_FIELDS=COMMON_CSG_FIELDS|{'compound_mitres_and_welds_unqualified'}
COMMON_OPERATION_FIELDS={'id','kind','material','source_entity_id','source_stock_owner_id','source_geometry','complete_void_union','cost_USD','mode','operations','person_process_h','person_QA_h','source_credit_USD','original_paid_blank_retained','independent_cut_union_and_mass_update_required','stock_mass_application','incremental_removed_volume_bounds_m3','incremental_removed_mass_bounds_kg','incremental_removed_first_moment_bounds_kg_m','incremental_removed_centroid_box_m'}
HARDPOINT_OPERATION_FIELDS=COMMON_OPERATION_FIELDS|{'maximum_pocket_depth_m','minimum_annular_rear_web_m','removed_centroid_basis','source_cylinder_position_convention','unchanged_original_through_void'}
SOURCE_CYLINDER_POSITION_CONVENTION='at_m is base; signed axis points into cut'
RING_OPERATION_FIELDS=COMMON_OPERATION_FIELDS|{'source_cylinder_position_convention','access_diameter_m','diameter_tolerance_m','axis_position_tolerance_m','blank_owner_count','new_stock_purchase_count','cut_count','moment_basis','nominal_removed_centroid_m','process_time_basis','unchanged_original_voids'}
COMMON_PHYSICAL_FIELDS={'id','kind','source_entity_id','source_stock_owner_id','complete_void_union','source_material_geometry'}


def supported_box(g):
    if not isinstance(g,dict) or set(g)!=BOX_FIELDS or g['kind']!='box':raise ValueError('Closed source box geometry grammar required; unknown physical feature unsupported')
    size=vector(g['size_m']);vector(g['at_m']);identity_frame(g['rotation'])
    if min(size)<=0:raise ValueError('Positive explicit source box dimensions required')


def source_geometry_contract(c,kind):
    allowed=HARDPOINT_CSG_FIELDS if kind=='hardpoint' else RING_CSG_FIELDS
    if not isinstance(c,dict) or set(c)-allowed or not {'id','material','geometry','holes'}<=set(c):raise ValueError('Closed source material/geometry wrapper required')
    if not isinstance(c['id'],str) or not c['id'] or c['material']!='al5083' or not isinstance(c['holes'],list):raise ValueError('Explicit source material/void roster required')
    if 'old_entity_sha256' in c:hexid(c['old_entity_sha256'])
    if 'part_id' in c and (not isinstance(c['part_id'],str) or not c['part_id']):raise ValueError('Explicit source part identity required')
    for key in ('actual_insert_geometry_held','compound_mitres_and_welds_unqualified'):
        if key in c and type(c[key]) is not bool:raise ValueError('Typed historical source assessment required')
    for key in ('insert_pocket_max_depth_m','insert_pocket_max_diameter_m'):
        if key in c:number(c[key],True) # prior unknown-reserve ancestry, not an extra physical void
    g=c['geometry']
    if kind=='hardpoint':supported_box(g)
    else:
        if not isinstance(g,dict) or set(g)!={'kind','outer','void'} or g['kind']!='difference':raise ValueError('Closed ring difference geometry required')
        supported_box(g['outer']);supported_box(g['void'])
    if c.get('geometry_hold') is not None:raise ValueError('Unsupported source geometry/domain hold')
    return dict(material_id=c['material'],geometry=deepcopy(g),holes=deepcopy(c['holes']))


def bind_physical_operation(op,physical):
    """Authenticate evaluated bounds to every accepted physical declaration.

    Known administrative fields stay evaluation-bound at this exact wrapper.
    Unknown fields are refused, never erased by a recursive denylist.
    """
    source=op['source_operation'];kind=source['kind'];hard=kind=='hardpoint-thread-pocket'
    if kind not in ('hardpoint-thread-pocket','ring-access-port-enlargement'):raise ValueError('Unsupported finishing operation kind')
    allowed=HARDPOINT_OPERATION_FIELDS if hard else RING_OPERATION_FIELDS
    if set(source)-allowed:raise ValueError('Unconsumed source operation field/domain')
    if (not hard or 'source_cylinder_position_convention' in source) and source.get('source_cylinder_position_convention')!=SOURCE_CYLINDER_POSITION_CONVENTION:raise ValueError('Explicit signed-BASE source cylinder convention required')
    required={'id','kind','material','source_entity_id','source_stock_owner_id','source_geometry','complete_void_union','cost_USD'}
    if not required<=set(source):raise ValueError('Complete source-operation identity/void contract required')
    for key in ('id','source_entity_id','source_stock_owner_id'):
        if source[key]!=op[key] or physical[key]!=op[key]:raise ValueError('Physical/evaluated operation source identity differs')
    if source['complete_void_union']!=op['source_complete_void_union'] or physical['complete_void_union']!=op['source_complete_void_union'] or physical['kind']!=kind:raise ValueError('Physical/evaluated complete void union differs')
    if source['material']!='al5083':raise ValueError('Physical/evaluated source material differs')
    keys={'maximum_pocket_depth_m','minimum_annular_rear_web_m'} if hard else {'access_diameter_m','diameter_tolerance_m','axis_position_tolerance_m'}
    expected=COMMON_PHYSICAL_FIELDS|keys|({'material'} if not hard else set())
    optional={'cut_count','blank_owner_count','new_stock_purchase_count'} if not hard else set()
    if set(physical)-expected-optional or not expected<=set(physical):raise ValueError('Closed physical finishing grammar required')
    for key in keys:
        if number(physical[key],True)!=number(source[key],True):raise ValueError('Physical/evaluated bound-driving parameter differs:'+key)
    if 'material' in physical and physical['material']!=source['material']:raise ValueError('Physical source material differs')
    for key in optional:
        if key in physical and integer(physical[key])!=integer(source[key]):raise ValueError('Physical/evaluated operation count differs')
    c=source['source_geometry'];source_geometry_contract(c,'hardpoint' if hard else 'ring');pg=physical['source_material_geometry']
    if not isinstance(pg,dict) or set(pg)-{'geometry','holes','material','insert_pocket_max_depth_m','insert_pocket_max_diameter_m'} or not {'geometry','holes'}<=set(pg):raise ValueError('Closed physical source-material projection required')
    if pg['geometry']!=c['geometry'] or pg['holes']!=c['holes']:raise ValueError('Physical/evaluated nominal source geometry/holes differ')
    if 'material' in pg and pg['material']!=c['material']:raise ValueError('Physical/evaluated nominal material differs')
    for key in ('insert_pocket_max_depth_m','insert_pocket_max_diameter_m'):
        if key in pg and (key not in c or number(pg[key],True)!=number(c[key],True)):raise ValueError('Physical/source prior pocket-bound ancestry differs')


def source_outer(e,kind):
    identity_frame(e['rotation'])
    if e['frame']!=FRAME or e['material_id']!='al5083' or e['rotation']!=I:raise ValueError('Supported source-specific local Al5083/I frame required')
    c=e['exact_CSG_entity'];source_geometry_contract(c,kind);g=c['geometry'];outer=g if kind=='hardpoint' else g['outer']
    identity_frame(outer['rotation'])
    if outer['kind']!='box' or outer['rotation']!=I:raise ValueError('Explicit source box pose required')
    T=vector(outer['at_m']);size=vector(outer['size_m']);same(T,e['at_m'])
    if 'geometry' in e:
        packaging=e['geometry']
        if not isinstance(packaging,dict) or set(packaging)!={'kind','size_m'} or packaging['kind']!='envelope':raise ValueError('Closed canonical packaging descriptor required; never interpreted as material')
        same(vector(packaging['size_m']),size)
    if min(size)<=0 or c.get('geometry_hold') is not None:raise ValueError('Unsupported source geometry/domain hold')
    if c.get('material')!='al5083':raise ValueError('Exact sourceCSG material must be Al5083')
    U=vector(e['uncertainty_m'])
    if min(U)<0:raise ValueError('Explicit nonnegative prior placement bounds required')
    return c,g,outer,T,size,U

def through(h,T,size,radius=None):
    if set(h)!={'kind','at_m','axis','diameter_m','length_m','purpose'} or h['kind']!='cylinder-cut' or vector(h['axis'])!=[1.,0.,0.]:raise ValueError('Explicit signed+X source through-bore required')
    base=vector(h['at_m']);same([base[0],h['length_m']],[T[0]-size[0]/2,size[0]]);r=number(h['diameter_m'],True)/2
    if radius is not None and not near(r,radius):raise ValueError('Through-bore source radius differs')
    return [T[0],base[1],base[2]],r

def canon_piece(L,r,C):return dict(axis=0,centre_m=list(C),length_m=L,radius_m=r)
def void_graph(p):return dict(kind='finite-cylinder-void',**deepcopy(p))

def canonical_moments(pieces):
    m=None
    for p in pieces:
        x=cylinder_moments(point(p['length_m']),point(p['radius_m']),corner_C(p['centre_m']))
        if m is None:m=x
        else:m=dict(V=plus(m['V'],x['V']),F=[plus(a,b) for a,b in zip(m['F'],x['F'])],Q=[[plus(m['Q'][i][j],x['Q'][i][j]) for j in range(3)] for i in range(3)])
    return m

def compare_circular(actual,expected):
    if len(actual)!=len(expected):raise ValueError('Complete circular union coverage differs')
    key=lambda p:tuple(p['centre_m'])+(p['radius_m'],p['length_m'])
    for a,b in zip(sorted(actual,key=key),sorted(expected,key=key)):
        if set(a)!={'axis','centre_m','length_m','radius_m'} or type(a['axis']) is not int or a['axis']!=0:raise ValueError('Explicit circular cut normal form required')
        same(a['centre_m'],b['centre_m']);same([a['length_m'],a['radius_m']],[b['length_m'],b['radius_m']])

def hardpoint(e,op,rho):
    c,g,outer,T,size,U=source_outer(e,'hardpoint');same(size,[.012,.025,.025])
    if len(c['holes'])!=1:raise ValueError('One retained hardpoint through-bore required')
    C,r=through(c['holes'][0],T,size,.003);same(C,T)
    complete=op['source_complete_void_union']
    if complete.get('kind')!='union' or len(complete['pieces'])!=2 or complete['pieces'][0]!=c['holes'][0]:raise ValueError('Hardpoint full void must retain original through-bore')
    h=complete['pieces'][1]
    keys={'kind','at_m','axis','major_diameter_m','pilot_diameter_m','pitch_m','depth_m','depth_tolerance_m','full_thread_depth_m','flat_bottom'}
    if set(h)!=keys or h['kind']!='thread-bounded-cut' or vector(h['axis'])!=[-1.,0.,0.] or h['flat_bottom'] is not True:raise ValueError('Exact stopped-thread cut domain required')
    same(vector(h['at_m']),[T[0]+size[0]/2,T[1],T[2]])
    same([h['major_diameter_m'],h['pilot_diameter_m'],h['pitch_m'],h['depth_m'],h['depth_tolerance_m'],h['full_thread_depth_m']],[.008,.007,.001,.0087,.0003,.0077])
    dmin=h['depth_m']-h['depth_tolerance_m'];dmax=h['depth_m']+h['depth_tolerance_m'];
    same([op['source_operation']['maximum_pocket_depth_m'],op['source_operation']['minimum_annular_rear_web_m']],[dmax,size[0]-dmax])
    x0=T[0]-size[0]/2;x1=T[0]+size[0]/2
    def pieces(d,radius):return [canon_piece(size[0]-d,r,[x0+(size[0]-d)/2,T[1],T[2]]),canon_piece(d,radius,[x1-d/2,T[1],T[2]])]
    lo=pieces(dmin,.0035);hi=pieces(dmax,.004);compare_circular(op['minimum_circular_cut_union'],lo);compare_circular(op['maximum_circular_cut_union'],hi)
    base=box_moments(size,corner_C(T));small=canonical_moments(lo);large=canonical_moments(hi);Mmax=subtract(base,small);Mmin=subtract(base,large)
    # Actual material = maximum material minus an unknown subset of the bounded
    # thread/depth shell. Full radial/axial support, never a point annulus.
    delta=max(0.,up(large['V'][1]-small['V'][0]));Dsupport=[[down(x1-dmax),up(x1)],[down(T[1]-.004),up(T[1]+.004)],[down(T[2]-.004),up(T[2]+.004)]]
    F=[minus(Mmax['F'][i],times([0.,delta],Dsupport[i])) for i in range(3)];Q=[]
    for i in range(3):Q.append([minus(Mmax['Q'][i][j],times([0.,delta],square(Dsupport[i]) if i==j else times(Dsupport[i],Dsupport[j]))) for j in range(3)])
    bounded=dict(V=[Mmin['V'][0],Mmax['V'][1]],F=F,Q=Q)
    known=subtract(base,cylinder_moments(point(size[0]),point(r),corner_C(T)))
    return dict(kind='hardpoint-stopped-thread',minimum_material_graph=dict(kind='difference',outer=deepcopy(outer),cuts=[void_graph(canon_piece(size[0],r,T)),void_graph(hi[1])]),maximum_material_graph=dict(kind='difference',outer=deepcopy(outer),cuts=[void_graph(canon_piece(size[0],r,T)),void_graph(lo[1])]),complete_source_void_union=deepcopy(complete),analytic_disjoint_void_partitions=dict(minimum_void=lo,maximum_void=hi),set_envelope_scope='Retained fullthrough+stoppedthread union; analytic quantities use explicit disjoint partitions once. Nested coaxial pilot/major+depth material bounds; unknown threadphase not an exact helix',bounded_properties=properties(bounded,rho,U,support_box(size,T)),known_old_material_volume_interval_m3=known['V'],unknown_thread_removed_shell_volume_upper_m3=delta,unknown_thread_full_support_m=Dsupport)

def ring(e,op,rho):
    c,g,outer,T,size,U=source_outer(e,'ring');same(size,[.006,1.7,1.2])
    if g['kind']!='difference' or set(g)!={'kind','outer','void'}:raise ValueError('Complete original ring outer/aperture CSG required')
    aperture=g['void']
    identity_frame(aperture['rotation'])
    if aperture['kind']!='box' or aperture['rotation']!=I:raise ValueError('Explicit ring aperture pose required')
    same(aperture['at_m'],T);same(aperture['size_m'],[.006,1.56,1.06]);holes=c['holes']
    if len(holes)!=12:raise ValueError('Exactly12oldring voids required')
    centres=[]
    for h in holes:
        C,r=through(h,T,size,.00275)
        if C in centres:raise ValueError('Duplicate ring port source')
        centres.append(C)
    sourceop=op['source_operation'];same([sourceop['access_diameter_m'],sourceop['diameter_tolerance_m'],sourceop['axis_position_tolerance_m']],[.012,.00005,.0001])
    if integer(sourceop['blank_owner_count'])!=1 or integer(sourceop['new_stock_purchase_count'])!=0 or integer(sourceop['cut_count'])!=12:raise ValueError('One paid ring/12machining ports,not12purchases')
    complete=op['source_complete_void_union'];ps=complete.get('pieces',[])
    if complete.get('kind')!='union' or len(ps)!=25 or ps[0]!=aperture or ps[1:13]!=holes:raise ValueError('Complete ring aperture/old12/new12void roster required')
    for old,new in zip(holes,ps[13:]):
        through(new,T,size,.006)
        if new['at_m']!=old['at_m'] or new['axis']!=old['axis'] or new['length_m']!=old['length_m'] or not near(new['diameter_m'],.012):raise ValueError('Ring new port/source centre mismatch')
    rmin=down((.012-.00005)/2);rmax=up((.012+.00005)/2);pos=.0001;spread=up(sqrt(2)*pos)
    if rmin-spread<=.00275:raise ValueError('Original ring through-void not contained in every new port tolerance case')
    for i,C in enumerate(centres):
        if any(abs(C[k]-T[k])+rmax+spread>size[k]/2 for k in [1,2]):raise ValueError('Ring tolerance envelope leaves outer stock')
        if not any(abs(C[k]-T[k])-rmax-spread>aperture['size_m'][k]/2 for k in [1,2]):raise ValueError('Ring port/aperture tolerance union unsupported')
        for D in centres[:i]:
            if sqrt(sum((C[k]-D[k])**2 for k in [1,2]))<=2*(rmax+spread):raise ValueError('Ring port tolerance envelopes overlap')
    compare_circular(op['minimum_circular_cut_union'],[canon_piece(size[0],rmin,C) for C in centres]);compare_circular(op['maximum_circular_cut_union'],[canon_piece(size[0],rmax,C) for C in centres])
    base=subtract(box_moments(size,corner_C(T)),box_moments(aperture['size_m'],corner_C(T)))
    bounded=deepcopy(base);old=deepcopy(base)
    for C in centres:
        bounded=subtract(bounded,cylinder_moments(point(size[0]),[rmin,rmax],[point(C[0]),[down(C[1]-pos),up(C[1]+pos)],[down(C[2]-pos),up(C[2]+pos)]]))
        old=subtract(old,cylinder_moments(point(size[0]),point(.00275),corner_C(C)))
    # These are set envelopes for all translated cylinders. Tight quantity
    # intervals above integrate actual r/position domains, not envelope volumes.
    small=[canon_piece(size[0],down(rmin-spread),C) for C in centres];large=[canon_piece(size[0],up(rmax+spread),C) for C in centres]
    return dict(kind='ring-through-ports',minimum_material_graph=dict(kind='difference',outer=deepcopy(outer),cuts=[deepcopy(aperture)]+[void_graph(p) for p in large]),maximum_material_graph=dict(kind='difference',outer=deepcopy(outer),cuts=[deepcopy(aperture)]+[void_graph(p) for p in small]),complete_source_void_union=deepcopy(complete),set_envelope_scope='Transverse axis-position uncertainty conservatively interpreted as independentY/Z±0.1mm; radius envelopes use sqrt(2)*positionbound. Net quantities use actual independently varying radii/centres, not set-envelope volumes.',axis_position_interpretation=dict(evaluation_hypothesis=True,exact_source_GDT_meaning_asserted=False,Y_m=[-pos,pos],Z_m=[-pos,pos],axial_fullthrough_drawing_retained=True,actual_drill_stroke_qualified=False),bounded_properties=properties(bounded,rho,U,support_box(size,T)),known_old_material_volume_interval_m3=old['V'])


def rebuild(terminal,weld,hardware,*,input_pin,request_id):
    """Source-specific13→2 draft replacements; not a planner or native call."""
    hexid(request_id)
    for v in [terminal,weld,hardware,input_pin]:identity(v)
    if input_pin.get('schema')!='osr-terminal-finishing-input-pin/1' or set(input_pin['sources'])!={'terminal','weld','hardware'}:raise ValueError('Exact three-input source pin required')
    for label,v in [('terminal',terminal),('weld',weld),('hardware',hardware)]:
        checkseal(v)
        if v.get('schema')!={'terminal':'osr-terminal-canonical-normalization-packet/1','weld':'osr-terminal-finite-full-revision-proposal/1','hardware':'osr-terminal-hardware-component-normalization/1'}[label]:raise ValueError('Unsupported source-specific input schema')
        if input_pin['sources'][label]['evaluation_id']!=v['evaluation_id']:raise ValueError('Input evaluation pin differs')
        hexid(input_pin['sources'][label]['raw_sha256'])
    common=terminal['source_pin'];raw=weld['source_proposal'];original=hardware['source_original_definition'];checkseal(raw)
    if common!=weld['source_pin'] or common!=original['parent'] or raw['candidate_id']!=common['candidate_id'] or raw['evaluation_id']!=common['evaluation_id']:raise ValueError('Mixed local source epochs')
    if identity(terminal['source_physical_definition'])!=common['candidate_id'] or terminal['source_physical_definition']!=raw['physical_definition']:raise ValueError('Terminal/weld/common physical source projection differs')
    if noLF({k:v for k,v in original.items() if k!='evaluation_id'})!=original['evaluation_id'] or noLF(original['physical_definition'])!=original['candidate_id'] or original['candidate_id']!=hardware['source_candidate_id'] or original['evaluation_id']!=hardware['source_evaluation_id']:raise ValueError('Original hardware noLF physical/evaluation source differs')
    if identity(weld['physical_definition'])!=weld['physical_definition_id'] or identity(hardware['physical_definition'])!=hardware['component_geometry_id']:raise ValueError('Normalized physical projection differs')
    if any(v.get(k) is True for v in [terminal,weld,hardware] for k in FLAGS) or hardware['source_owner_transactions_applied'] is not False or weld['accounting']['transaction_applied'] is not False:raise ValueError('Already applied/accepted inputs refused')
    E=index(terminal['canonical_draft']['entities']);G=index(terminal['canonical_draft']['stock_groups']);ops=index(hardware['canonical_draft']['required_source_finishing']);ownerrows=hardware['canonical_draft']['source_finishing_owner_dispositions'];physicalops=index(hardware['physical_definition']['source_finishing'])
    if len(ops)!=13 or len(ownerrows)!=2 or set(ops)!=set(physicalops):raise ValueError('Exact13operations/twopaidowners required')
    changed=set(weld['final_changed_parent_entities']);changedowners=set(weld['accounting']['parent_stock_owner_revisions']);seen=set();seenparents=set();seenowners=set();rows=[];ownerrecords=[];price_records=[]
    for owner in ownerrows:
        oid=owner['source_owner_id']
        if oid in seenowners or oid not in G or G[oid]!=owner['source'] or integer(owner['paid_blank_count'])!=1 or integer(owner['stock_purchase_count'])!=0 or owner['source_mass_and_moment_update_applied'] is not False:raise ValueError('Exact paid source group retained once required')
        if oid in changedowners:raise ValueError('Unhandled weld/finishing paid-owner overlap requires combined source revision')
        seenowners.add(oid);group=G[oid];account_cases(group['direct_cost_usd']);account=group['source_account'];rho=account['density_cases_kg_m3']
        if not isinstance(rho,list) or len(rho)!=3 or any(number(x)!=2660. for x in rho):raise ValueError('Authenticated parent2660/allcases required; no Hglobal density debit')
        local=[]
        for opid in owner['operation_ids']:
            if opid in seen or opid not in ops:raise ValueError('Missing/duplicate operation owner')
            seen.add(opid);op=ops[opid];eid=op['source_entity_id']
            if eid in seenparents or eid not in E or eid not in group['entity_ids'] or eid in changed or op['source_stock_owner_id']!=oid or op['frame']!=FRAME or op['units']!='m':raise ValueError('Duplicate/mixed/unhandled weld source member/frame')
            seenparents.add(eid);e=E[eid]
            if e['exact_CSG_entity']!=op['source_operation']['source_geometry'] or op['paid_blank_retained_once'] is not True or op['remaining_net_mass_and_CG'] is not None or op['source_complete_void_union']!=physicalops[opid]['complete_void_union'] or physicalops[opid]['source_entity_id']!=eid or physicalops[opid]['source_stock_owner_id']!=oid:raise ValueError('Complete finishing source CSG/void/properties differ')
            account_cases(op['source_operation']['cost_USD']);
            if op['source_operation'].get('material')!='al5083':raise ValueError('Finishing/source parent material mismatch')
            bind_physical_operation(op,physicalops[opid])
            kind=op['source_operation']['kind'];material=hardpoint(e,op,2660.) if kind=='hardpoint-thread-pocket' else ring(e,op,2660.) if kind=='ring-access-port-enlargement' else None
            if material is None:raise ValueError('Unsupported source finishing family')
            if material['kind'].startswith('hardpoint'):
                reserve=account['additional_drill_removal_each_m3']['insert_pocket_extra_unknown_interval_m3'];same(reserve,[0.,4.523893421169303e-7]);same([account['net_before_extra_machining_each_m3']],[(material['known_old_material_volume_interval_m3'][0]+material['known_old_material_volume_interval_m3'][1])/2])
                prior=material['known_old_material_volume_interval_m3'];old_volumes=[prior[0]-reserve[1],(prior[0]+prior[1]-reserve[0]-reserve[1])/2,prior[1]-reserve[0]]
            else:reserve=None;prior=material['known_old_material_volume_interval_m3'];old_volumes=[sum(prior)/2]*3
            for case,V in zip(CASES,old_volumes):
                if not near(group['net_mass_kg'][case],V*2660.*len(group['entity_ids'])):raise ValueError('Prior owner reserve/material mass context differs')
            record=dict(source_entity_id=eid,source_stock_owner_id=oid,source_entity_sha256=identity(e),source_owner_sha256=identity(group),material_id='al5083',frame=FRAME,source_pose=dict(at_m=deepcopy(e['at_m']),rotation=deepcopy(e['rotation'])),source_entity_ancestry=deepcopy(e),source_finishing_operation=deepcopy(op),old_pocket_reserve_accounting_ancestry=deepcopy(reserve),old_incremental_H_removal_is_not_debited=True,complete_material_rebuild=material,transaction_applied=False)
            rows.append(record);local.append(record);price_records.append(dict(operation_id=opid,source_H_allowance=deepcopy(op['source_operation']['cost_USD']),source_process_QA_machine_scope=deepcopy(op['source_operation']),additive_with_source_finished_price_approved=False))
        if set(group['entity_ids'])!={r['source_entity_id'] for r in local} or integer(account['quantity'])!=len(local):raise ValueError('Complete source paid-group constituent map required')
        net=total(r['complete_material_rebuild']['bounded_properties']['mass_interval_kg'] for r in local);gross=group['gross_mass_kg']
        if any(not near(gross[c],gross['base']) for c in CASES) or net[1]>gross['base']:raise ValueError('Source gross/finished stock budget differs')
        ownerrecords.append(dict(source_owner_id=oid,source_owner_sha256=identity(group),source_owner_ancestry=deepcopy(group),source_occurrence_ids=sorted(group['entity_ids']),paid_blank_group_count=1,new_stock_purchase_count=0,paid_gross_mass_kg=deepcopy(gross),complete_rebuilt_net_mass_interval_kg=net,rebuilt_scrap_mass_interval_kg=minus(point(gross['base']),net),source_direct_price_retained_once=deepcopy(group['direct_cost_usd']),source_finished_process_split_unknown=True,finishing_allowances_overlap_status='Named possible overlap with source finished-price process/QA scope; do not sum or credit without reconciliation',new_material_charge=False,source_price_credit=False,transaction_applied=False))
    if seen!=set(ops) or len(seenparents)!=13 or len([r for r in rows if r['complete_material_rebuild']['kind']=='hardpoint-stopped-thread'])!=12:raise ValueError('Complete12hardpoints/one ring material coverage required')
    # Only authenticated nominal geometry/declared machining parameters enter
    # physical identity. Derived interval supports/Minkowski graphs and the
    # ambiguous axis-position interpretation above remain evaluation evidence.
    physical=dict(schema='osr-terminal-complete-finishing-material-physical/1',units='m',frame=FRAME,
        parents=[dict(id=r['source_entity_id'],material_id='al5083',source_pose=r['source_pose'],
            nominal_source_geometry=dict(material_id='al5083',geometry=deepcopy(r['source_entity_ancestry']['exact_CSG_entity']['geometry']),holes=deepcopy(r['source_entity_ancestry']['exact_CSG_entity']['holes'])),
            source_declared_finishing=deepcopy(physicalops[r['source_finishing_operation']['id']]))
            for r in sorted(rows,key=lambda r:r['source_entity_id'])])
    return seal(dict(schema='osr-terminal-finishing-material-rebuild/1',request_id=request_id,source_input_pin=deepcopy(input_pin),source_local_epoch=deepcopy(common),source_terminal_evaluation_id=terminal['evaluation_id'],source_weld_evaluation_id=weld['evaluation_id'],source_hardware_evaluation_id=hardware['evaluation_id'],physical_definition=physical,component_geometry_id=identity(physical),pending_draft_replacements=rows,source_owner_conservation=ownerrecords,counts=dict(finishing_operations=13,material_occurrences=13,hardpoints=12,backing_rings=1,paid_owner_groups=2,new_stock_purchases=0),manufacturing_accounts=dict(source_finished_owner_prices_retained_once=True,H_finishing_allowance_records=price_records,complete_installed_cost=False,process_overlap_hold=True,shared_tools_lifecycle_reference=deepcopy(hardware['lifecycle_allocations'])),pending_contracts=['Complete analytic material/moment hypotheses require independent numerical/source review','Unknown helix phase,manufacturing tolerance correlations,compound grade,20mm sourceposeuncertainty and actual drilling/access/tool/WPS/strength/thermal qualification remainopen','Existing finished-price and additional Hprocess/QA/machine scopes may overlap; oldsplit unknown, no assumed double invoice/discount','Current b8weld overlap is authenticated/refused if changed; wholeterminal/body integration and canonical transactions remainseparate'],canonical_definition=None,source_transactions_applied=False,complete_installed_cost=False,complete_installed_mass=False,**FLAGS))
