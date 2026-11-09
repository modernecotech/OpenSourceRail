"""Normalize exact621 header research outlines without body/native admission.

This source-specific adapter preserves bounded source material and required
blind joints. It does not call the composer, upstream outline or any CAD tool.
Unsupported physical domains remain named holds in a non-admitted draft.
"""
from copy import deepcopy
from hashlib import sha256
from itertools import product
from math import fsum, isfinite, pi, ulp
import json

SOURCE_COMMIT='62184b182d1c0f56483f96c4cdf98ddfa556a93d'
SOURCE_SHA256='74e20731b3a9277c0c1e0a6ee44df8ef3b785173033809bf5d516627b89fd9ab'
SOURCE_FAMILY='research/header-Al-endplate-isolated-blind-steel-joint/2'
P6=dict(physical_id='ce1b8b222b06a6479f7738d9409d74a5333514b79b7baf5dffc7c8510b73e044',evaluation_id='8fffa3254dab9b737e8785de7d781325dde3cec028a89b14a3e8371b04cc6289',raw_sha256='3984b2a7ad9966b8d74fec2da9d0530cea66d3557071e964816f55fefebb9df5')
I=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
Y_ROUND=[[0.,0.,1.],[1.,0.,0.],[0.,1.,0.]]
CASES=('low','base','high')
FLAGS=dict(physical_accepted=False,engineering_accepted=False,native_eligible=False,
    installed_assembly_accepted=False,canonical_admitted=False,manufacturing_release=False,
    operating_release=False,selected_reference_changed=False,release_approved=False)


def identity(v):return sha256((json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()
def sealed(v):
    if v.get('evaluation_id')!=identity({k:x for k,x in v.items() if k!='evaluation_id'}):raise ValueError('Source evaluation seal differs')
def number(v,positive=False):
    if type(v) not in (int,float) or not isfinite(v) or positive and v<=0:raise ValueError('Finite nonboolean SI value required')
    return float(v)
def vector(v):
    if not isinstance(v,(list,tuple)) or len(v)!=3:raise ValueError('Three explicit coordinates required')
    return [number(x) for x in v]
def proper(R):
    if not isinstance(R,list) or len(R)!=3:raise ValueError('Proper frame required')
    R=[vector(r) for r in R]
    if any(abs(sum(R[k][i]*R[k][j] for k in range(3))-(1 if i==j else 0))>1e-10 for i in range(3) for j in range(3)):raise ValueError('Rigid frame required')
    d=R[0][0]*(R[1][1]*R[2][2]-R[1][2]*R[2][1])-R[0][1]*(R[1][0]*R[2][2]-R[1][2]*R[2][0])+R[0][2]*(R[1][0]*R[2][1]-R[1][1]*R[2][0])
    if abs(d-1)>1e-10:raise ValueError('Reflected frame refused')
    return R

def mul(A,B):return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def apply(R,p):return [sum(R[i][k]*p[k] for k in range(3)) for i in range(3)]
def add(a,b):return [x+y for x,y in zip(a,b)]
def transpose(R):return [[R[j][i] for j in range(3)] for i in range(3)]
def close(a,b):return abs(a-b)<=1e-14+1e-10*max(abs(a),abs(b))
def cases(v):
    if not isinstance(v,dict) or set(v)!=set(CASES):raise ValueError('Explicit three material labels required')
    for x in v.values():number(x,True)
    return v

def hexid(v):
    if not isinstance(v,str) or len(v)!=64 or any(c not in '0123456789abcdef' for c in v):raise ValueError('Exact64hex identity required')


def _union(cuts,size):
    """Independent canonical sourceY coaxial/disjoint subtraction domain."""
    if not isinstance(cuts,list) or len(cuts)>256:raise ValueError('Complete bounded void list required')
    size=vector(size)
    if min(size)<=0:raise ValueError('Positive blank dimensions required')
    cs=[]
    for h in cuts:
        if not isinstance(h,dict) or set(h)!={'axis','at_m','radius_m','length_m'} or type(h['axis']) is not int or h['axis']!=1:raise ValueError('Supported exact sourceY void required')
        p=vector(h['at_m']);r=number(h['radius_m'],True);L=number(h['length_m'],True)
        if any(abs(p[k])+[r,L/2,r][k]>size[k]/2+1e-10 for k in range(3)):raise ValueError('Void exits source stock')
        cs.append(dict(axis=1,at_m=p,radius_m=r,length_m=L))
    for i,a in enumerate(cs):
        for b in cs[i+1:]:
            d=((a['at_m'][0]-b['at_m'][0])**2+(a['at_m'][2]-b['at_m'][2])**2)**.5
            overlap=min(a['at_m'][1]+a['length_m']/2,b['at_m'][1]+b['length_m']/2)-max(a['at_m'][1]-a['length_m']/2,b['at_m'][1]-b['length_m']/2)
            if d and d<a['radius_m']+b['radius_m'] and overlap>0:raise ValueError('Unsupported noncoaxial void union')
    out=[]
    for x,z in sorted({(c['at_m'][0],c['at_m'][2]) for c in cs}):
        group=[c for c in cs if (c['at_m'][0],c['at_m'][2])==(x,z)];ends=sorted({c['at_m'][1]+s*c['length_m']/2 for c in group for s in (-1,1)});runs=[]
        for a,b in zip(ends,ends[1:]):
            radii=[c['radius_m'] for c in group if c['at_m'][1]-c['length_m']/2<=a+1e-14 and c['at_m'][1]+c['length_m']/2>=b-1e-14]
            if not radii:continue
            r=max(radii)
            if runs and runs[-1][1]==a and runs[-1][2]==r:runs[-1][1]=b
            else:runs.append([a,b,r])
        out.extend(dict(axis=1,at_m=[x,(a+b)/2,z],radius_m=r,length_m=b-a) for a,b,r in runs)
    return out


def _moments(cuts):
    vs=[pi*c['radius_m']**2*c['length_m'] for c in cuts]
    return fsum(vs),[fsum(v*c['at_m'][k] for v,c in zip(vs,cuts)) for k in range(3)]


def _same_union(a,b):
    """Only axial arithmetic replay allowance; received source bytes stay exact.

    Reconstructing centre+/-length/2 then recomputing centre/length can differ
    by a few floating-point ULPs. Transverse centres and radii remain exact;
    this is not a fit, stock, position or manufacturing tolerance waiver.
    """
    if len(a)!=len(b):return False
    for x,y in zip(a,b):
        if x['axis']!=y['axis'] or x['radius_m']!=y['radius_m'] or any(x['at_m'][k]!=y['at_m'][k] for k in (0,2)):return False
        for u,v in ((x['at_m'][1],y['at_m'][1]),(x['length_m'],y['length_m'])):
            if abs(u-v)>8*max(ulp(u),ulp(v)):return False
    return True


def _finished(row):
    g=row['geometry']
    if g.get('kind')!='bounded-box-minus-sourceY-circular-union' or g.get('complete_void_model') is not True:raise ValueError('Complete explicit bounded finished source required')
    size=vector(g['size_m']);lo=_union(g['minimum_void_union'],size);hi=_union(g['maximum_void_union'],size)
    if not _same_union(lo,g['minimum_void_union']) or not _same_union(hi,g['maximum_void_union']):raise ValueError('Canonical complete void unions required')
    # Low removal must be contained in high, not merely have a smaller volume.
    if not _same_union(_union(lo+hi,size),hi):raise ValueError('Finished removal bounds not nested')
    vl,ml=_moments(lo);vh,mh=_moments(hi);gross=size[0]*size[1]*size[2];m=row['material_properties'];rho=number(m['density_hypothesis_kg_m3'],True)
    if not 0<gross-vh<=gross-vl:raise ValueError('Positive remaining material required')
    if len(m['bounding_shape_conservation'])!=2 or len(m['net_volume_interval_m3'])!=2 or len(m['mass_interval_kg'])!=2:raise ValueError('Both complete material bounds required')
    for actual,expected in zip(m['net_volume_interval_m3'],(gross-vh,gross-vl)):
        if not close(number(actual,True),expected):raise ValueError('Finished net volume conservation differs')
    for actual,expected in zip(m['mass_interval_kg'],((gross-vh)*rho,(gross-vl)*rho)):
        if not close(number(actual,True),expected):raise ValueError('Finished mass interval differs')
    for b,v,moment in zip(m['bounding_shape_conservation'],(vl,vh),(ml,mh)):
        if not close(b['void_volume_m3'],v) or not close(b['net_volume_m3']+v,gross) or not close(b['mass_kg'],rho*(gross-v)):raise ValueError('Finished mass conservation differs')
        if any(not close(x,-y) for x,y in zip(vector(b['net_local_first_moment_m4']),moment)) or any(not close(x,-rho*y) for x,y in zip(vector(b['net_local_mass_first_moment_kg_m']),moment)):raise ValueError('Finished firstmoment conservation differs')
    if row['prior_physical_cut_roster'] is not None or row['measured_hole_free'] is not False or not row['complete_future_drawing']:raise ValueError('New drawing cannot authenticate old hardware')
    budget=row['gross_budget'];cases(budget['mass_kg']);cases(budget['direct_allowance_USD']);cases(budget['total_successor_direct_USD'])
    if not close(number(budget['volume_m3'],True),gross):raise ValueError('Source gross blank budget volume differs')
    if budget['quantity_transferred']!=1 or isinstance(budget['quantity_transferred'],bool) or budget['additional_raw_material_purchase_USD']!=0 or budget['physical_refund_or_salvage_credit_USD']!=0 or budget['transfer_applied_to_live_body'] is not False:raise ValueError('Once-only unmanufactured source budget transfer required')
    for i,k in enumerate(CASES):
        if not close(budget['mass_kg'][k],gross*rho) or not close(budget['total_successor_direct_USD'][k],budget['direct_allowance_USD'][k]+budget['additional_process_QA_USD'][i]):raise ValueError('Source blank/process budget conservation differs')
    return deepcopy(row)


def _round(g,R):
    if set(g)-{'kind','axis','length_m','outer_radius_m','inner_radius_m','units'}:raise ValueError('Unsupported round feature cannot be discarded')
    if g.get('axis')!=1 or type(g.get('axis')) is not int:raise ValueError('Source round axis must be explicitV')
    L=number(g['length_m'],True);ro=number(g['outer_radius_m'],True);ri=number(g['inner_radius_m'])
    if not 0<=ri<ro:raise ValueError('Positive annular material required')
    return dict(kind='annulus',units='m',size_m=[L,2*ro,2*ro],outer_radius_m=ro,inner_radius_m=ri),mul(R,Y_ROUND)


def _weld_pieces(p):
    g=p['geometry'];out=[]
    if g.get('kind')!='finite-triangular-weld-drawing' or len(g.get('profiles',[]))!=3:raise ValueError('Three finite weld profiles required')
    for n,q in enumerate(g['profiles']):
        ax=q['extrusion_axis'];a,b=q['section_axes'];interval=q['interval_m'];tri=q['vertices_m']
        if any(type(v) is not int for v in (ax,a,b)) or sorted([ax,a,b])!=[0,1,2] or len(tri)!=3 or any(len(x)!=2 for x in tri):raise ValueError('Explicit weld extrusion frame required')
        L=number(interval[1]-interval[0],True);pts=[[number(v) for v in t] for t in tri];area=abs(sum(x[0]*y[1]-x[1]*y[0] for x,y in zip(pts,pts[1:]+pts[:1])))/2
        if not area:raise ValueError('Positive weld triangle required')
        columns=[[float(k==v) for k in range(3)] for v in (a,b,ax)];Q=transpose(columns)
        try:proper(Q);flip=1.
        except ValueError:columns[1]=[-v for v in columns[1]];Q=transpose(columns);proper(Q);flip=-1.
        ca=(min(t[0] for t in pts)+max(t[0] for t in pts))/2;cb=(min(t[1] for t in pts)+max(t[1] for t in pts))/2;origin=[0.,0.,0.];origin[a]=ca;origin[b]=cb;origin[ax]=(interval[0]+interval[1])/2
        vs=[[x-ca,flip*(y-cb),z] for z in (-L/2,L/2) for x,y in pts];size=[max(x[k] for x in vs)-min(x[k] for x in vs) for k in range(3)]
        out.append(dict(id=p['id']+'/piece'+str(n),geometry=dict(kind='triangle-prism',units='m',vertices_m=vs,size_m=size),at_m=add(p['at_m'],apply(p['rotation'],origin)),rotation=mul(p['rotation'],Q),volume_m3=area*L))
    total=fsum(x['volume_m3'] for x in out)
    if not all(close(total,x) for x in p['net_volume_bounds_m3']):raise ValueError('Weld pieces do not conserve one filler owner')
    for x in out:x['owner_fraction']=x['volume_m3']/total
    return out


def _projection(raw):
    p=raw['physical_definition'];required={'family','parent_physical_id','source_geometry','frame','new_parts','source_finished_geometry','planned_source_machining','welds'}
    if set(p)!=required or p['family']!=SOURCE_FAMILY or p['parent_physical_id']!=P6['physical_id']:raise ValueError('Exact621 physical source schema required')
    expected=[{k:deepcopy(x[k]) for k in ('id','material','quantity','frame','geometry','at_m','rotation','role')} for x in raw['parts']]
    if p['new_parts']!=expected:raise ValueError('Raw/newpart physical projection differs')
    expected=[{k:deepcopy(x[k]) for k in ('source_id','material_id','frame','at_m','rotation','geometry')} for x in raw['source_finished_successors']]
    if p['source_finished_geometry']!=expected:raise ValueError('Finished source physical projection differs')
    expected=[{k:deepcopy(x[k]) for k in ('material','parents','paths_m','profiles','leg_m')} for x in raw['welds']]
    if p['welds']!=expected:raise ValueError('Weld physical projection differs')
    if len(raw['machining'])!=2 or len(p['planned_source_machining'])!=2:raise ValueError('Complete source machining projection required')
    finished={x['source_id']:x for x in raw['source_finished_successors']}
    for a,b in zip(p['planned_source_machining'],raw['machining']):
        expected={k:deepcopy(b[k]) for k in ('part_id','new_pilots_or_through_cuts','major_thread_envelopes')}
        expected['thread_specification']=deepcopy(finished[b['part_id']]['geometry']['thread_specification'])
        if a!=expected:raise ValueError('Machining/thread physical projection differs')
    if len(raw['welds'])!=2:raise ValueError('Two compatible weld stock owners required')
    by={x['id']:x for x in raw['parts']}
    for i,weld in enumerate(raw['welds']):
        part=by['weld/'+str(i)]
        if part['material']!=weld['material'] or any(part['geometry'][k]!=weld[k] for k in ('profiles','paths_m','leg_m')):raise ValueError('Weld part/attachment drawings disagree')
    return p


def _interval_pose(m,at,R):
    """Conservative interval transformation; no fabricated pointCG/tensor."""
    mass=m['mass_interval_kg'];rho=m['density_hypothesis_kg_m3'];unc=m['placement_uncertainty_m']
    if unc is None:return dict(frame='joint-local-UVW',centroid_interval_m=None,mass_first_moment_interval_kg_m=None,placement_unknown=True)
    number(unc);cg=m['local_centroid_interval_m'];mom=m['local_volume_first_moment_interval_m4']
    outcg=[];outmom=[]
    for k in range(3):
        cs=[sum(R[k][q]*v[q] for q in range(3)) for v in product(*cg)]
        ms=[rho*sum(R[k][q]*v[q] for q in range(3)) for v in product(*mom)]
        delta=unc*fsum(abs(x) for x in R[k]);offset=[at[k]*x for x in mass]
        outcg.append([at[k]+min(cs)-delta,at[k]+max(cs)+delta])
        outmom.append([min(ms)+min(offset)-mass[1]*delta,max(ms)+max(offset)+mass[1]*delta])
    return dict(frame='joint-local-UVW',centroid_interval_m=outcg,mass_first_moment_interval_kg_m=outmom,
        placement_unknown=False,source_component_local_axes_preserved=True,exact_point_CG_or_tensor=False,
        method='Conservative transformed source-local volume moments and density plus separate placement cube; correlation not discarded into realizable label scenarios')


def _nominal_contract(raw,parts,finished,frame):
    """Check real nominal source entities/voids, not only reported stack values."""
    def pose(p,at):
        if any(not close(a,b) for a,b in zip(vector(p['at_m']),at)) or proper(p['rotation'])!=I:raise ValueError('Nominal source stack pose differs')
    pad=parts['isolation-pad'];pose(pad,[0.,.00075,0.])
    if set(pad['geometry'])-{'kind','size_m','holes','units'} or pad['geometry']['size_m']!=[.2,.0015,.18] or len(pad['geometry']['holes'])!=4:raise ValueError('Complete isolation pad geometry required')
    layers=(('GFRPwasher',.0265,.0285,.010),('steelwasher',.0285,.030,.008),('spacer',.030,.032,.008),('lock0',.032,.033,.008),('lock1',.033,.034,.008))
    for u in (-.08,.08):
        for w in (-.05,.05):
            suffix=f'{u}/{w}';bolt=parts['M8x40/'+suffix];pose(bolt,[u,.034,w]);g=bolt['geometry']
            if g['kind']!='fullythreaded-bolt-envelope' or type(g['axis']) is not int or g['axis']!=1 or g['direction']!=-1 or not close(g['underhead_length_m'],.04) or not close(g['major_diameter_m'],.008):raise ValueError('Actual blind bolt model differs')
            bush=parts['bush/'+suffix];pose(bush,[u,.01325,w]);g=bush['geometry']
            if g['axis']!=1 or not close(g['length_m'],.0265) or not close(g['outer_radius_m'],.006) or not close(g['inner_radius_m'],.00425):raise ValueError('Isolation bush cannot span or enter blindreceiver')
            hs=[h for h in pad['geometry']['holes'] if all(close(a,b) for a,b in zip(vector(h['at_m']),[u,0.,w]))]
            if len(hs)!=1 or set(hs[0])!={'axis','at_m','radius_m','length_m'} or type(hs[0]['axis']) is not int or hs[0]['axis']!=1 or not close(hs[0]['radius_m'],.0061) or not close(hs[0]['length_m'],.0015):raise ValueError('Actual pad bore differs')
            for name,a,b,ro in layers:
                p=parts[name+'/'+suffix];pose(p,[u,(a+b)/2,w]);g=p['geometry']
                if g['axis']!=1 or not close(g['length_m'],b-a) or not close(g['outer_radius_m'],ro) or not close(g['inner_radius_m'],.00425):raise ValueError('Actual bearing layer differs')
    by={x['source_id']:x for x in finished};mach={x['part_id']:x for x in raw['machining']}
    if len(mach)!=2 or set(mach)!=set(by):raise ValueError('Exact machining/source counterpart map required')
    for key in ('endplate','cleat'):
        c=raw['physical_definition']['source_geometry'][key];x=by[c['id']];m=mach[c['id']]
        if x['at_m']!=c['at_m'] or x['rotation']!=c['rotation'] or x['material_id']!=c['material_id'] or x['geometry']['size_m']!=c['geometry']['size_m']:raise ValueError('Finishing cannot relocate or substitute source material')
        cuts=m['new_pilots_or_through_cuts'];majors=m['major_thread_envelopes'];size=x['geometry']['size_m'];base=raw['manufacturing_definition']['base_void_unions'][c['id']]
        if len(cuts)!=4 or len(majors)!=(4 if key=='cleat' else 0):raise ValueError('Complete four source drilling/thread drawing required')
        Rpart=mul(transpose(frame['rotation']),proper(c['rotation']));at=apply(transpose(frame['rotation']),[c['at_m'][k]-frame['origin_m'][k] for k in range(3)]);found=set()
        for h in cuts:
            q=add(at,apply(Rpart,h['at_m']));match=next(((u,w) for u in (-.08,.08) for w in (-.05,.05) if close(q[0],u) and close(q[2],w)),None)
            if match is None or match in found or not close(q[1],.014 if key=='endplate' else -.0045) or not close(h['radius_m'],.0061 if key=='endplate' else .0034) or not close(h['length_m'],.025 if key=='endplate' else .009):raise ValueError('Actual source bore datum/size differs')
            found.add(match)
        minimum=deepcopy(cuts)
        if key=='cleat':
            if x['geometry']['thread_specification']['flat_bottom_corner_radius_hypothesis_m']!=.00005:raise ValueError('Exact finitecorner drawing required')
            minimum=[];side=frame['side'];corner=.00005
            for h in cuts:
                a=deepcopy(h);a['length_m']-=corner;a['at_m'][1]+=side*corner/2
                b=deepcopy(h);b['radius_m']-=corner;b['length_m']=corner;b['at_m'][1]-=side*(h['length_m']-corner)/2;minimum.extend((a,b))
            for h in majors:
                q=add(at,apply(Rpart,h['at_m']))
                if not close(q[1],-.0035) or not close(h['radius_m'],.004) or not close(h['length_m'],.007):raise ValueError('Thread envelope datum/size differs')
        if not _same_union(_union(base+minimum,size),x['geometry']['minimum_void_union']) or not _same_union(_union(base+cuts+majors,size),x['geometry']['maximum_void_union']):raise ValueError('Complete future void/corner/thread union differs')


def _physical_geometry(value):
    """Keep material geometry; source verification labels are evaluation data.

    These three keys describe the provenance/verification of the source stock,
    not its dimensions, voids, material, or placement. Unknown geometry keys
    remain physical. Complete received records are retained in the draft and
    evaluation; this projection does not edit or authenticate the source.
    """
    if isinstance(value,dict):
        # Only the declared source-stock records have these annotation fields.
        # The same names in an opaque future physical record stay physical.
        stock=value.get('kind') in ('box','drilled-box','rhs')
        out={}
        for k,v in value.items():
            if stock and k in ('finished_geometry_verified','exact_stock'):
                if type(v) is not bool:raise ValueError('Source stock evidence flag must be boolean')
                continue
            if stock and k=='definition_basis':
                if not isinstance(v,str):raise ValueError('Source stock evidence basis must be text')
                continue
            out[k]=_physical_geometry(v)
        return out
    if isinstance(value,list):return [_physical_geometry(v) for v in value]
    return deepcopy(value)


def normalize(raw,*,pin,request_id):
    """Return a sealed normal form and deliberately non-admitted component draft.

    Input bytes/authenticated execution pins belong to the caller. This pure
    API accepts one already-produced outline; it never generates another one.
    """
    hexid(request_id);sealed(raw)
    for k in ('evaluation_id','physical_definition_id','source_request_id','source_execution_id'):hexid(pin[k])
    if pin.get('source_commit')!=SOURCE_COMMIT or pin.get('source_module_sha256')!=SOURCE_SHA256 or pin['evaluation_id']!=raw['evaluation_id'] or pin['physical_definition_id']!=raw['physical_definition_id'] or raw['physical_definition_id']!=identity(raw['physical_definition']):raise ValueError('Exact621 source/content/physical pins required')
    if raw['source_binding']['request_id']!=pin['source_request_id'] or raw['source_p6']!=P6:raise ValueError('Exact source request and parent P6 binding required')
    hexid(raw['source_context_id'])
    if raw['source_context_id']!=raw['source_binding']['context_id']:raise ValueError('Source context identity differs')
    if raw['schema']!='osr-header-isolated-blind-joint-source-outline/2' or raw['units']!='m,kg,N,Nm,Pa,USD':raise ValueError('Exact metre621 outline schema required')
    if any(raw[k] is not False for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release','selected_reference_changed','native_evaluator_admitted','installed_mass_complete')):raise ValueError('Source cannot confer admission')
    mfg=raw['manufacturing_definition']
    if mfg['mode']!='new-build-drawing' or mfg['prior_physical_cut_roster'] is not None or mfg['measured_hole_free'] is not False or raw['manufacturing_definition_id']!=identity(mfg):raise ValueError('Explicit complete future drawing only; no existing-hardware evidence substitution')
    drawing=mfg['new_drawing']
    if drawing['state']!='budget-only, unmanufactured' or drawing['prior_physical_cut_roster'] is not None or drawing['measured_hole_free'] is not False:raise ValueError('Unmanufactured drawing provenance required')
    p=_projection(raw);frame=p['frame'];R=proper(frame['rotation']);origin=vector(frame['origin_m']);side=frame['side']
    if type(side) is not int or side not in (-1,1) or R!=(I if side==1 else [[-1.,0.,0.],[0.,-1.,0.],[0.,0.,1.]]):raise ValueError('Pinned proper signed joint frame required')
    parts={x['id']:x for x in raw['parts']};accounts={x['part_id']:x for x in raw['materials']['rows']}
    names={'isolation-pad','weld/0','weld/1','seal-top-and-sides','steel-weld-repair-finish','thread-compound'}
    suffixes=[f'{u}/{w}' for u in (-.08,.08) for w in (-.05,.05)]
    names|={kind+'/'+q for kind in ('bush','GFRPwasher','steelwasher','spacer','lock0','lock1','M8x40','head-weathercap') for q in suffixes}
    if len(parts)!=38 or len(raw['parts'])!=38 or set(parts)!=names or set(accounts)!=names or len(accounts)!=len(raw['materials']['rows']):raise ValueError('Complete38part and once-only material-account coverage required')
    finished=[_finished(x) for x in raw['source_finished_successors']]
    if len(finished)!=2 or len({x['source_id'] for x in finished})!=2 or {x['source_id'] for x in finished}!={p['source_geometry'][k]['id'] for k in ('endplate','cleat')}:raise ValueError('Exact two finishing counterparts required')
    if set(mfg['source_records'])!={x['source_id'] for x in finished} or any(x['source_record_id']!=mfg['source_records'][x['source_id']] for x in finished):raise ValueError('Exact predecessor record ownership required')
    _nominal_contract(raw,parts,finished,frame)
    holds=[dict(code='canonical-geometry-domain',reason='Current composer does not validate complete boundedbox/minmaxvoid/corner/thread or unknown supplier material graphs; no filledbox substitution'),dict(code='blind-isolated-stack',reason='Required blindreceiver is not the historical through-sleeve contract; nominal stack retained but substrate/fit/strength unresolved'),dict(code='source-key-map',reason='Exact canonicalparent/source_key map and finish_new_source_blank disposition are not supplied; conceptual budgets are not installed or paid hardware'),dict(code='bounded-mass-properties',reason='Thread/corner/supplier mass-centroid-inertia intervals cannot become exact canonical point-CG/tensors'),dict(code='native-structural-access',reason='No CAD/FEM/contact/WPS/grade/creep/preload/finite-tool/wholebody-removal/physical qualification inherited')]
    entities=[];stocks=[];mapping={};policy=raw['materials']['price_policy']
    for name,x in parts.items():
        if x['quantity']!=1 or isinstance(x['quantity'],bool) or x['frame']!='joint-local-UVW':raise ValueError('Explicit single local stock occurrences required')
        at=vector(x['at_m']);RR=proper(x['rotation']);g=x['geometry'];converted=[]
        if g.get('units','m')!='m':raise ValueError('Unconverted part geometry units refused')
        bounds=x['net_volume_bounds_m3']
        if len(bounds)!=2 or not 0<number(bounds[0],True)<=number(bounds[1],True)<=number(x['gross_volume_m3'],True):raise ValueError('Positive owned net/gross stock required')
        if g['kind']=='finite-triangular-weld-drawing':converted=_weld_pieces(x)
        elif g['kind']=='annulus':
            gg,RR=_round(g,RR);converted=[dict(id=name,geometry=gg,at_m=at,rotation=RR,owner_fraction=1.)]
            V=pi*(gg['outer_radius_m']**2-gg['inner_radius_m']**2)*gg['size_m'][0]
            if any(not close(v,V) for v in bounds):raise ValueError('Annular material volume differs')
        elif g['kind']=='drilled-box':
            gg=deepcopy(g);gg['kind']='box';gg['units']='m';gg['holes']=[dict(axis=h['axis'],centre_m=vector(h['at_m']),radius_m=number(h['radius_m'],True),length_m=number(h['length_m'],True)) for h in g['holes']];converted=[dict(id=name,geometry=gg,at_m=at,rotation=RR,owner_fraction=1.)]
            V=g['size_m'][0]*g['size_m'][1]*g['size_m'][2]-fsum(pi*h['radius_m']**2*h['length_m'] for h in g['holes'])
            if any(not close(v,V) for v in bounds):raise ValueError('Drilled pad material volume differs')
        else:
            # Preserve every bounded/source field. No fabricated exact solid,
            # pointcentroid or zero inertia for an unfamiliar supplier form.
            converted=[dict(id=name,geometry=dict(kind='unresolved-material-graph',source_geometry=deepcopy(g),source_role=x['role']),at_m=at,rotation=RR,owner_fraction=1.)]
            holds.append(dict(code='unsupported-part-material-graph',entity=name,source_kind=g['kind'],reason='Source physical fields preserved in full; no filled primitive or invented exact centroid/inertia'))
        a=accounts[name];mass=a['mass_bounds_kg'];cost=None if a['gross_material_USD'] is None or a['process_QA_USD'] is None else [u+v for u,v in zip(a['gross_material_USD'],a['process_QA_USD'])]
        rho=None if policy is None or policy.get(x['material']) is None else policy[x['material']]['density_kg_m3']
        if mass is None or cost is None or rho is None:holds.append(dict(code='unknown-stock-price-or-density',entity=name,reason='Unknown staysNone; no zero price/mass substitution'))
        else:
            if len(mass)!=3 or len(cost)!=3 or len(rho)!=3:raise ValueError('Three explicit stock labels required')
            vs=[x['net_volume_bounds_m3'][0],sum(x['net_volume_bounds_m3'])/2,x['net_volume_bounds_m3'][1]]
            if any(not close(number(v,True),vs[i]*number(rho[i],True)) for i,v in enumerate(mass)):raise ValueError('Source material account netmass differs')
            for v in cost:number(v,True)
        ids=[]
        for e in converted:
            frac=e.pop('owner_fraction');ids.append(e['id']);e.update(material_id=x['material'],frame='joint-local-UVW',scope='installed',functions=['header-attachment-material'],source_owner_id=name,owner_fraction=frac,mass_label_cases_kg=None if mass is None else dict(zip(CASES,[v*frac for v in mass])),mass_properties=dict(method='Declared source material/geometry domain; exact or interval details retained, not measured',centroid_local_m=None,inertia_exact=False),source_net_volume_bounds_m3=deepcopy(x['net_volume_bounds_m3']),geometry_model_is_not_native_admission=True);entities.append(e)
        mapping[name]=ids
        stocks.append(dict(id='new/'+name,entity_ids=ids,procurement_quantity=1,source_owner_id=name,scope='installed',net_volume_bounds_m3=deepcopy(x['net_volume_bounds_m3']),gross_volume_m3=x['gross_volume_m3'],net_mass_label_cases_kg=deepcopy(mass),gross_mass_label_cases_kg=None if rho is None else [x['gross_volume_m3']*v for v in rho],gross_material_label_cases_USD=deepcopy(a['gross_material_USD']),process_QA_label_cases_USD=deepcopy(a['process_QA_USD']),direct_cost_label_cases_USD=cost,cost_shares={e['id']:e['owner_fraction'] for e in entities if e['id'] in ids},basis='One sourcepart owner; weld drawing pieces allocate this same stock/process once'))
    contexts={}
    for key,c in p['source_geometry'].items():
        if key in ('endplate','cleat'):continue
        cid='context/'+c['id'];contexts[c['id']]=cid;entities.append(dict(id=cid,scope='context',source_id=c['id'],material_id=c['material_id'],geometry=deepcopy(c['geometry']),at_m=apply(transpose(R),[c['at_m'][k]-origin[k] for k in range(3)]),rotation=mul(transpose(R),proper(c['rotation'])),frame='joint-local-UVW',functions=['retained-substrate-context'],stock_owner=None,source_key_binding=None))
    for x in finished:
        e=dict(id=x['successor_id'],scope='installed',source_id=x['source_id'],material_id=x['material_id'],geometry=deepcopy(x['geometry']),at_m=apply(transpose(R),[x['at_m'][k]-origin[k] for k in range(3)]),rotation=mul(transpose(R),proper(x['rotation'])),frame='joint-local-UVW',functions=['finished-header-counterpart'],source_material_properties=deepcopy(x['material_properties']),source_key_binding=None)
        e['normal_form_mass_properties']=_interval_pose(x['material_properties'],e['at_m'],e['rotation'])
        entities.append(e);contexts[x['source_id']]=e['id'];stocks.append(dict(id='finish/'+x['source_id'],entity_ids=[e['id']],scope='installed',procurement_quantity=1,budget_transfer=deepcopy(x['gross_budget']),source_predecessor=x['source_id'],source_record_id=x['source_record_id'],disposition='finish_new_source_blank_REQUIRED_NOT_APPLIED',cost_shares={e['id']:1.},additional_raw_material_purchase_USD=0.))
    stack=raw['stack']
    for k,v in (('bolt_count',4),('nut_count',0),('grip_m',.034),('bolt_underhead_m',.040),('nominal_engagement_m',.006),('minimum_engagement_after_0p3mm_budget_m',.0057),('pilot_depth_m',.009),('backweb_after_0p3mm_budget_m',.0007)):
        if not close(number(stack[k]),v):raise ValueError('Fixed nominal blind stack differs: '+k)
    interfaces=[]
    for suffix in suffixes:
        u,w=map(float,suffix.split('/'));ids=[*mapping['M8x40/'+suffix],*mapping['bush/'+suffix],*mapping['GFRPwasher/'+suffix],*mapping['steelwasher/'+suffix],*mapping['spacer/'+suffix],*mapping['lock0/'+suffix],*mapping['lock1/'+suffix],*mapping['isolation-pad'],contexts[p['source_geometry']['endplate']['id']],contexts[p['source_geometry']['cleat']['id']]]
        stack_shape={k:deepcopy(stack[k]) for k in ('bearing_layer_intervals_m','grip_m','bolt_underhead_m','nominal_engagement_m','usable_thread_m','pilot_depth_m','backweb_m')}
        interfaces.append(dict(id='blind-M8/'+suffix,schema='osr-header-blind-isolated-stack/1',units='m',part_ids=ids,frame='joint-local-UVW',axis=[0.,1.,0.],point_m=[u,0.,w],physical_specification=dict(bolt_underhead_m=.040,underhead_plane_v_m=.034,tip_v_m=-.006,receiver_depth_m=.009,thread_envelope_depth_m=.007,nominal_engagement_m=.006,minimum_engagement_hypothesis_m=.0057,isolation_bush_interval_v_m=[0.,.0265],receiver_interval_v_m=[-.010,0.],bush_does_not_span_blind_receiver=True,source_stack=stack_shape),source_stack_evidence=deepcopy(stack),status='required-unresolved-contract',counterpart_substrate_bindings_pending=True,physical_qualified=False))
    for i,weld in enumerate(raw['welds']):interfaces.append(dict(id='weld-substrates/'+str(i),schema='osr-header-finite-compatible-weld/1',units='m',part_ids=mapping['weld/'+str(i)]+[contexts[x] for x in weld['parents']],frame='joint-local-UVW',physical_specification={k:deepcopy(weld[k]) for k in ('material','parents','profiles','paths_m','leg_m')},status='required-unresolved-substrate-contract',physical_qualified=False))
    physical=dict(schema='osr-header-component-normalform-physical/2',units='m',placement_in_source_frame=dict(frame='body',at_m=origin,rotation=R),entities=[{k:(_physical_geometry(e[k]) if k=='geometry' else deepcopy(e[k])) for k in ('id','scope','material_id','frame','at_m','rotation','geometry','functions')} for e in entities],interfaces=[{k:deepcopy(c[k]) for k in ('id','schema','units','part_ids','frame','axis','point_m','physical_specification') if k in c} for c in interfaces])
    holds.append(dict(code='lifecycle-tools-fixture',reason='Shared family/workshop tools and fixture stay separate; unknown supplier price/geometry/WLL is not zero or an installed charge'))
    packet=dict(schema='osr-header-component-normalization/1',units='m',component_geometry_id=identity(physical),physical_definition=physical,source_pin=deepcopy(pin),source_evaluation_id=raw['evaluation_id'],source_physical_id=raw['physical_definition_id'],request_id=request_id,canonical_definition=None,canonical_draft=dict(schema='osr-header-component-nonadmitted-draft/1',entities=entities,stock_groups=stocks,physical_interfaces=interfaces,required_counterpart_ids=[x['id'] for x in interfaces],all_required_interfaces_resolved=False,placement_in_source_frame=deepcopy(physical['placement_in_source_frame'])),source_finished_budget_transfers_applied=False,held_facts=holds,shared_workshop_allocations=deepcopy(raw['tools_and_sequence'].get('shared_fixture')),shared_tools=deepcopy(raw['tools_and_sequence'].get('shared_tools')),source_material_account=deepcopy(raw['materials']),source_machining=deepcopy(raw['machining']),source_manufacturing_definition=deepcopy(mfg),source_ownership=deepcopy(raw['source_ownership']),source_service_and_removal_obligations=deepcopy(raw['tools_and_sequence']),source_preservation=deepcopy(raw['source_preservation']),source_holds=deepcopy(raw['holds']),unlocated_old_joinery_credit=deepcopy(raw['source_ownership'].get('old_joinery_mass_credit')),upstream_validation_inherited=False,**FLAGS)
    packet['lifecycle_allocations']=[dict(id='header-family/shared-fixture',scope='lifecycle',quantity_per_family=1,source_allocation=deepcopy(raw['tools_and_sequence'].get('shared_fixture')),charged_in_installed_stock=False),dict(id='header-family/shared-tools',scope='lifecycle',source_allocation=deepcopy(raw['tools_and_sequence'].get('shared_tools')),charged_in_installed_stock=False,deduplicate_by_family_owner_before_any_project_cost=True)]
    packet['evaluation_id']=identity(packet);return packet
