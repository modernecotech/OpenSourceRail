"""Occurrence-ledger composition of reviewed research definitions, never admission.

No catalogue/geometry producer, pricing service or native evaluator is called.
The caller supplies authenticated inputs and the exact externally reviewed map
identity. This module does not grant authorization or infer unresolved joints.
SI metres, kg and USD are explicit. Existing cost/mass bounds retain their basis.
"""
from copy import deepcopy
import gzip
import json
from math import fsum, isfinite, pi
from pathlib import Path

from engineering.station_rail.common import identity, digest
from engineering.vehicle_installation.model import mass_properties, reactions

CASES = ('low', 'base', 'high')
I = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
GEOMETRY_KEYS = ('kind','shape','size_m','length_m','width_m','depth_m','wall_m','radius_m',
    'outer_radius_m','inner_radius_m','vertices_m','faces','holes','path_m','arc','finished_profile_xz_m',
    'segments','cross_section','features','start_rad','end_rad','bore_steps','source_stock')
FRAME_ROLES = ('body','bogie','gear','wheelset','flexible-body-bogie')
HARDWARE_KEYS = ('manufacturer','model','winding','phase_system','cooling','shaft_option',
                 'pilot_option','mechanical_configuration','mechanical_revision')
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             selected_reference_changed=False, movement_authority=False,
             native_eligible=False, installed_assembly_accepted=False)


def sources():
    root=Path(__file__).resolve().parents[2]
    names=('engineering/railway_project/vehicle_composition.py',
           'engineering/vehicle_installation/model.py','engineering/station_rail/common.py')
    return {n:digest(root/n) for n in names}


def seal(value):
    value = deepcopy(value)
    value.pop('evaluation_id', None)
    value['evaluation_id'] = identity(value)
    return value


def authenticated(value, pin, *, physical=True):
    """Verify contents, not a substituted candidate/evaluation label."""
    if value.get('evaluation_id') != identity({k: v for k, v in value.items() if k != 'evaluation_id'}):
        raise ValueError('Evaluation seal differs')
    if value['evaluation_id'] != pin['evaluation_id']:
        raise ValueError('Pinned evaluation differs')
    if physical:
        if value.get('candidate_id') != identity(value['physical_definition']):
            raise ValueError('Physical seal differs')
        if value['candidate_id'] != pin['candidate_id']:
            raise ValueError('Pinned candidate differs')
    return value


def read_authenticated(path, pin):
    """Read only; raw identity is mandatory at the file boundary."""
    if digest(path) != pin['raw_sha256']:
        raise ValueError('Raw input hash differs')
    data = Path(path).read_bytes()
    value = json.loads(gzip.decompress(data) if str(path).endswith('.gz') else data)
    return authenticated(value, pin)


def vector(value, n=3):
    if not isinstance(value,(list,tuple)) or len(value) != n or any(isinstance(x, bool) or not isinstance(x, (int, float)) or not isfinite(x) for x in value):
        raise ValueError('Finite SI vector required')
    return list(value)


def rotation(R):
    if len(R) != 3:
        raise ValueError('3x3 proper rotation required')
    for row in R:
        vector(row)
    if any(abs(fsum(R[k][a]*R[k][b] for k in range(3))-(a == b)) > 1e-10 for a in range(3) for b in range(3)):
        raise ValueError('Rotation is not orthonormal')
    det = fsum(R[0][j]*(R[1][(j+1)%3]*R[2][(j+2)%3]-R[1][(j+2)%3]*R[2][(j+1)%3]) for j in range(3))
    if abs(det-1.) > 1e-10:
        raise ValueError('Reflection/improper rotation refused')
    return R


def mul(A, B):
    return [[fsum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def transform(p, at, R):
    return [at[i]+fsum(R[i][j]*p[j] for j in range(3)) for i in range(3)]


def tensor(S):
    if len(S) != 3:
        raise ValueError('3x3 inertia per kg required')
    for row in S:
        vector(row)
    if any(abs(S[i][j]-S[j][i]) > 1e-10 for i in range(3) for j in range(3)):
        raise ValueError('Symmetric inertia required')
    # Principal minors: catches nonphysical indefinite input, including shear.
    if min(S[i][i] for i in range(3)) < -1e-10:
        raise ValueError('Negative inertia')
    if min(S[i][i]*S[j][j]-S[i][j]**2 for i in range(3) for j in range(i)) < -1e-10:
        raise ValueError('Indefinite inertia')
    det = fsum(S[0][j]*(S[1][(j+1)%3]*S[2][(j+2)%3]-S[1][(j+2)%3]*S[2][(j+1)%3]) for j in range(3))
    if det < -1e-10 or any(S[i][i] > fsum(S[j][j] for j in range(3) if j != i)+1e-10 for i in range(3)):
        raise ValueError('Nonphysical inertia')
    return S


def rotate_tensor(S, R):
    return [[fsum(R[i][k]*S[k][l]*R[j][l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)]


def cases(value, *, positive=False, ordered=True):
    if set(value) != set(CASES):
        raise ValueError('Explicit low/base/high cases required')
    xs = vector([value[k] for k in CASES])
    if (ordered and xs != sorted(xs)) or min(xs) < 0 or (positive and min(xs) <= 0):
        raise ValueError('Ordered positive/bounded cases required; unknown is not zero')
    return value


def source_key(cid, pattern_id, index):
    if not isinstance(index, int) or isinstance(index, bool) or index < 0:
        raise ValueError('Source occurrence index required')
    return 'source/'+identity([cid, pattern_id, index])


def allocation(value, *, cars=None):
    if not isinstance(value,list) or not value or any(not isinstance(row,(list,tuple)) or len(row)!=2 for row in value):
        raise ValueError('Explicit car allocation required')
    if any(isinstance(c,bool) or not isinstance(c,int) or c<0 or
           isinstance(f,bool) or not isinstance(f,(int,float)) or not isfinite(f) or f<=0 for c,f in value):
        raise ValueError('Explicit car allocation required')
    if len({c for c, f in value}) != len(value) or abs(fsum(f for c, f in value)-1.) > 1e-10:
        raise ValueError('Car allocation must close once')
    if cars is not None:
        if isinstance(cars,bool) or not isinstance(cars,int) or cars<=0 or any(c>=cars for c,f in value):
            raise ValueError('Car allocation outside supported domain')
    return value


def row_domain(row, cars):
    """No installed/scenario mass may vanish outside the support domain."""
    allocation(row['car_allocation'],cars=cars)
    bi=row['bogie_index']
    if bi is not None and (isinstance(bi,bool) or not isinstance(bi,int) or not 0<=bi<2*cars or row['car_allocation']!=[[bi//2,1.]]):
        raise ValueError('Bogie allocation outside/inconsistent with support domain')
    cases(row['mass_kg'],positive=True);vector(row['centroid_m']);tensor(row['shape_I_per_kg'])
    if 'uncertainty_m' in row and min(vector(row['uncertainty_m']))<0:
        raise ValueError('Negative position uncertainty')


def parent_occurrences(parent, frame_map, functions):
    """Expand immutable patterns once; remove pattern covariance from each piece.

    The original pattern's own inertia/centroid uncertainty remains a declared
    source model; expansion does not upgrade a box/envelope approximation.
    """
    parts = {p['id']: p for p in parent['parts']}
    if len(parts) != len(parent['parts']) or set(functions) != set(parts):
        raise ValueError('Unique parts and complete source function map required')
    pats = parent['patterns']
    if len({p['id'] for p in pats}) != len(pats) or set(frame_map) != {p['id'] for p in pats}:
        raise ValueError('Complete unique source pattern/frame map required')
    counts = {k: 0 for k in parts}; out = {}
    for p in pats:
        q = p['count']
        if not isinstance(q, int) or q <= 0 or q != len(p['positions_m']):
            raise ValueError('Pattern count/position mismatch')
        R = rotation(p['rotation']); positions = [vector(x) for x in p['positions_m']]
        mean = [fsum(x[k] for x in positions)/q for k in range(3)]
        C = [[fsum((x[i]-mean[i])*(x[j]-mean[j]) for x in positions)/q for j in range(3)] for i in range(3)]
        trace = fsum(C[i][i] for i in range(3))
        own = tensor([[p['shape_I_per_kg'][i][j]-((trace if i == j else 0.)-C[i][j]) for j in range(3)] for i in range(3)])
        offset = [p['centroid_m'][k]-mean[k] for k in range(3)]
        part = parts[p['part_id']]; f = frame_map[p['id']]
        if not isinstance(f, str) or not f or not functions[part['id']]:
            raise ValueError('Explicit frame/functions required')
        cases(p['mass_kg'], positive=True); cases(p['direct_cost_usd'])
        allocation(p['car_allocation']); vector(p['uncertainty_m'])
        counts[part['id']] += q
        for j, at in enumerate(positions):
            key = source_key(parent['candidate_id'], p['id'], j)
            out[key] = dict(id=key, source_ref=dict(parent_candidate_id=parent['candidate_id'], pattern_id=p['id'], position_index=j,
                source_pattern_sha256=identity(p), source_part_sha256=identity(part)), part_id=part['id'], material_id=part['material_id'],
                geometry=deepcopy(p['geometry']), at_m=at, rotation=deepcopy(R), frame=f, functions=deepcopy(functions[part['id']]),
                car_allocation=deepcopy(p['car_allocation']), bogie_index=p['bogie_index'], centroid_m=[at[k]+offset[k] for k in range(3)],
                shape_I_per_kg=own, mass_kg={k:p['mass_kg'][k]/q for k in CASES}, direct_cost_usd={k:p['direct_cost_usd'][k]/q for k in CASES},
                uncertainty_m=deepcopy(p['uncertainty_m']), inertia_basis='retained-source-pattern model, including any original envelope approximation',
                mass_basis=deepcopy(part.get('mass_basis', 'retained source allowance; not measured')), stock_owner='retained/'+key,
                cost_basis=part.get('cost_basis', 'retained source bounds; no cost acceptance'), scope='installed')
    if any(counts[k] != p['quantity_per_train'] for k, p in parts.items()):
        raise ValueError('Catalogue/pattern conservation failed')
    return out


def entity_physical(e):
    p={k:deepcopy(e[k]) for k in ('id','part_id','material_id','at_m','rotation','frame','functions','hardware_choice') if k in e}
    p['geometry']={k:deepcopy(e['geometry'][k]) for k in GEOMETRY_KEYS if k in e['geometry']}
    return p


def interface_physical(c):
    p={k:deepcopy(c[k]) for k in ('id','schema','units','kind','part_ids','frame','axis','point_m',
        'contact_plane','nominal_thread_m','engagement_m','axis_world','sleeve_id','layers') if k in c}
    if 'layers' in p:
        p['layers']=[{k:deepcopy(x[k]) for k in ('entity_id','bore_index','expected_depth_m') if k in x} for x in p['layers']]
    return p


def _scalar(x, *, positive=False, nonnegative=False):
    if isinstance(x,bool) or not isinstance(x,(int,float)) or not isfinite(x) or (positive and x<=0) or (nonnegative and x<0):
        raise ValueError('Finite physical primitive parameter required')
    return x


def _same_extent(actual,declared):
    # Equivalent normalization only; not manufacturing clearance/tolerance.
    if not isfinite(actual) or not isfinite(declared):return False
    return abs(actual-declared)<=1e-10*max(1.,abs(actual),abs(declared))


def _polygon(points):
    if not isinstance(points,list) or not 3<=len(points)<=256:
        raise ValueError('Supported finite polygon requires3..256vertices')
    ps=[vector(p,2) for p in points]
    if ps[0]==ps[-1]:ps=ps[:-1]
    if len(ps)<3 or len({tuple(p) for p in ps})!=len(ps):
        raise ValueError('Degenerate polygon vertices')
    area=fsum(a[0]*b[1]-a[1]*b[0] for a,b in zip(ps,ps[1:]+ps[:1]))
    if not isfinite(area) or area==0:raise ValueError('Nonzero polygon area required')
    def orient(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    edges=list(zip(ps,ps[1:]+ps[:1]))
    for i,(a,b) in enumerate(edges):
        for j,(c,d) in enumerate(edges):
            if j<=i or j==i+1 or (i==0 and j==len(edges)-1):continue
            overlap=all(max(min(a[k],b[k]),min(c[k],d[k]))<=min(max(a[k],b[k]),max(c[k],d[k])) for k in range(2))
            if overlap and orient(a,b,c)*orient(a,b,d)<=0 and orient(c,d,a)*orient(c,d,b)<=0:
                raise ValueError('Self-intersecting polygon refused')
    return ps


def geometry(g):
    """Supported SI primitives, with explicit parameters consistent with bounds.

    Unknown equipment may remain an explicit positive envelope with bounded
    mass/inertia. An unfamiliar solid/deposit is not repaired into a primitive.
    Full-cylinder bounds are the normalization for round/sector primitives;
    route bounds are point extents plus radius. Polygon extrusion is alongY;
    a triangle-prism has two parallelXYtriangles extruded alongZ.
    """
    kinds=('box','rhs','annulus','cylinder','envelope','route','poly-prism','triangle-prism','annular-sector')
    if not isinstance(g,dict) or g.get('kind') not in kinds or g.get('units','m')!='m':
        raise ValueError('Unsupported finished geometry schema/units')
    k=g['kind'];size=vector(g.get('size_m'))
    if min(size)<=0:raise ValueError('Positive finite geometry size required')
    allowed={'box':set(),'envelope':set(),'rhs':{'wall_m'},'annulus':{'outer_radius_m','inner_radius_m'},
        'cylinder':{'radius_m'},'annular-sector':{'outer_radius_m','inner_radius_m','start_rad','end_rad'},
        'route':{'radius_m','path_m'},'poly-prism':{'finished_profile_xz_m'},'triangle-prism':{'vertices_m'}}[k]
    if allowed-set(g):raise ValueError('Required physical primitive parameters missing')
    declared=set(g)&(set(GEOMETRY_KEYS)-{'kind','size_m','source_stock','length_m','width_m','depth_m','holes'})
    if declared-allowed:raise ValueError('Unsupported physical primitive parameters')
    for key,n in (('length_m',0),('width_m',1),('depth_m',2)):
        if key in g and (not _same_extent(_scalar(g[key],positive=True),size[n])):
            raise ValueError('Primitive dimension/bounds inconsistency')
    if k=='rhs' and not 0<2*_scalar(g['wall_m'],positive=True)<min(size[1:]):
        raise ValueError('Invalid RHS material')
    if k in ('cylinder','annulus','annular-sector'):
        ro=_scalar(g['radius_m'] if k=='cylinder' else g['outer_radius_m'],positive=True)
        if k!='cylinder' and not 0<=_scalar(g['inner_radius_m'],nonnegative=True)<ro:
            raise ValueError('Invalid annular material')
        if any(not _same_extent(x,2*ro) for x in size[1:]):
            raise ValueError('Radius/size bounds inconsistency')
        if k=='annular-sector':
            a=_scalar(g['start_rad']);b=_scalar(g['end_rad'])
            if not 0<b-a<=2*pi:raise ValueError('Invalid annular sector angles')
    if k=='route':
        r=_scalar(g['radius_m'],positive=True);path=g['path_m']
        if not isinstance(path,list) or len(path)<2:raise ValueError('Finite route required')
        ps=[vector(p) for p in path]
        if any(a==b for a,b in zip(ps,ps[1:])):raise ValueError('Degenerate route segment')
        if any(not _same_extent(max(p[i] for p in ps)-min(p[i] for p in ps)+2*r,size[i]) for i in range(3)):
            raise ValueError('Route path/radius bounds inconsistency')
    if k=='poly-prism':
        ps=_polygon(g['finished_profile_xz_m'])
        if not _same_extent(max(p[0] for p in ps)-min(p[0] for p in ps),size[0]) or not _same_extent(max(p[1] for p in ps)-min(p[1] for p in ps),size[2]):
            raise ValueError('Profile/size bounds inconsistency')
    if k=='triangle-prism':
        vs=g['vertices_m']
        if not isinstance(vs,list) or len(vs)!=6:raise ValueError('Six triangle-prism vertices required')
        ps=[vector(p) for p in vs];a=[ps[1][i]-ps[0][i] for i in range(3)];b=[ps[2][i]-ps[0][i] for i in range(3)]
        n=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];offset=[ps[3][i]-ps[0][i] for i in range(3)]
        vector(n);vector(offset)
        if any(not _same_extent(p[2],ps[0][2]) for p in ps[:3]) or any(not _same_extent(offset[i],0.) for i in (0,1)):
            raise ValueError('Unsupported triangle extrusion normalization')
        if not all(_same_extent(ps[j+3][i]-ps[j][i],offset[i]) for j in range(3) for i in range(3)) or fsum(n[i]*offset[i] for i in range(3))==0:
            raise ValueError('Degenerate/inconsistent triangle extrusion')
        if any(not _same_extent(max(p[i] for p in ps)-min(p[i] for p in ps),size[i]) for i in range(3)):
            raise ValueError('Triangle profile/size bounds inconsistency')
    if not isinstance(g.get('holes',[]),list):raise ValueError('Explicit normalized bore list required')
    for h in g.get('holes',[]):
        if not isinstance(h,dict) or set(h)!={'axis','centre_m','radius_m','length_m'} or isinstance(h['axis'],bool) or not isinstance(h['axis'],int) or h['axis'] not in (0,1,2):
            raise ValueError('Unsupported bore normalization')
        vector(h['centre_m']);_scalar(h['radius_m'],positive=True);_scalar(h['length_m'],positive=True)
    identity(g)  # Recursively refuses NaN/nonserializable annotation/features.
    return g


def definition_physical(d):
    return dict(schema='osr-composition-component-physical/1', units=d['units'],
        entities=[entity_physical(e)|dict(scope=e['scope']) for e in d['entities']],
        interfaces=[interface_physical(c) for c in d.get('physical_interfaces', [])])


def validate_definition(d):
    if d['schema'] != 'osr-composition-component/1' or d['units'] != 'm':
        raise ValueError('Supported metre component definition required')
    authenticated(d, {'evaluation_id':d['evaluation_id']}, physical=False)
    if d['definition_id'] != identity(definition_physical(d)):
        raise ValueError('Component physical identity differs')
    es = {e['id']:e for e in d['entities']}
    if len(es) != len(d['entities']):
        raise ValueError('Duplicate component entity')
    owned = set()
    for s in d['stock_groups']:
        if not s.get('basis') or not s.get('cost_basis') or not s['entity_ids']:
            raise ValueError('Explicit stock/price basis required')
        for k in ('net_mass_kg','gross_mass_kg','scrap_mass_kg','direct_cost_usd'):
            cases(s[k], positive=k in ('net_mass_kg','gross_mass_kg'), ordered=k!='scrap_mass_kg')
        for eid in s['entity_ids']:
            if eid in owned or eid not in es or es[eid]['scope'] == 'context':
                raise ValueError('Duplicate/invalid stock ownership')
            owned.add(eid)
        if len({es[x]['scope'] for x in s['entity_ids']}) != 1:
            raise ValueError('Installed/lifecycle stock must be separate')
        for k in CASES:
            if abs(s['gross_mass_kg'][k]-s['net_mass_kg'][k]-s['scrap_mass_kg'][k]) > 1e-8:
                raise ValueError('Gross/net/scrap conservation failed')
            if abs(fsum(es[x]['mass_kg'][k] for x in s['entity_ids'])-s['net_mass_kg'][k]) > 1e-8:
                raise ValueError('Stock/entity net material differs')
        if abs(fsum(es[x]['cost_share'] for x in s['entity_ids'])-1.) > 1e-10:
            raise ValueError('Stock price allocated more/less than once')
    if len({s['id'] for s in d['stock_groups']}) != len(d['stock_groups']):
        raise ValueError('Duplicate stock group')
    for e in es.values():
        if e['scope'] not in ('installed','lifecycle','context'):
            raise ValueError('Unknown inventory scope')
        vector(e['at_m']); rotation(e['rotation']); geometry(e['geometry'])
        if not e.get('frame') or not e.get('functions') or not e.get('material_id') or not e.get('geometry'):
            raise ValueError('Located material/function/geometry required')
        if e['scope'] != 'context':
            cases(e['mass_kg'], positive=True); vector(e['centroid_local_m']); tensor(e['shape_I_per_kg'])
            vector(e['uncertainty_m'])
            if min(e['uncertainty_m']) < 0 or not e.get('inertia_basis') or not e.get('mass_basis') or e['cost_share'] < 0:
                raise ValueError('Declared material/inertia/uncertainty/cost model required')
            if e['id'] not in owned:
                raise ValueError('Unowned installed/lifecycle material')
    _component_contracts(d)
    return d


def _place(d, inst):
    rotation(inst['rotation']); vector(inst['at_m'])
    stocks = {x:s for s in d['stock_groups'] for x in s['entity_ids']}
    out = {}; contexts = []
    for e in d['entities']:
        if e['scope'] == 'lifecycle':
            continue  # Preserve definitions separately; no per-bogie workshop multiplier.
        if e['frame'] not in inst['frames']:
            raise ValueError('Unbound component frame')
        f = inst['frames'][e['frame']]; allocation(f['car_allocation'])
        if not f.get('name') or f['role'] not in FRAME_ROLES or (e['frame'] in FRAME_ROLES and f['role']!=e['frame']) or (f['role'] == 'body' and f['bogie_index'] is not None):
            raise ValueError('Body support allocation/frame differs')
        p = deepcopy(e);p.update(id=inst['id']+'/'+e['id'],at_m=transform(e['at_m'],inst['at_m'],inst['rotation']),
            rotation=mul(inst['rotation'],e['rotation']),frame=f['name'],car_allocation=deepcopy(f['car_allocation']),bogie_index=f['bogie_index'])
        if e['scope'] == 'context':
            contexts.append((e['id'],p));continue
        s = stocks[e['id']]
        p.update(centroid_m=transform(e['centroid_local_m'],p['at_m'],p['rotation']),
            shape_I_per_kg=rotate_tensor(e['shape_I_per_kg'],p['rotation']),
            stock_owner=inst['id']+'/'+s['id'],direct_cost_usd={k:s['direct_cost_usd'][k]*e['cost_share'] for k in CASES},
            cost_basis=s['cost_basis'],definition_id=d['definition_id'])
        out[p['id']] = p
    return out, contexts


def _coaxial_contract(c, rows):
    """Narrow finite primitive contract; unfamiliar fitted joints must refuse.

    A through-bore is local to its owner's geometry. Its axis/centre/length and
    the actual annular sleeve must agree in the common installed frame.
    Numerical epsilon only compares equivalent coordinates; it is no fit waiver.
    """
    if c.get('schema') != 'osr-coaxial-through-stack/1' or c.get('units') != 'm':
        raise ValueError('Unsupported/unresolved counterpart schema')
    a = c['axis_world']
    if isinstance(a,bool) or not isinstance(a,int) or a not in (0,1,2):
        raise ValueError('Counterpart axis required')
    layers=c.get('layers')
    if not isinstance(layers,list) or not layers or any(not isinstance(x,dict) or not isinstance(x.get('entity_id'),str) or not x['entity_id'].strip() or x['entity_id'] not in rows for x in layers):
        raise ValueError('Nonempty actual counterpart layers required')
    if len({x['entity_id'] for x in layers})!=len(layers) or not isinstance(c.get('sleeve_id'),str) or not c['sleeve_id'].strip() or c['sleeve_id'] not in rows or c['sleeve_id'] in {x['entity_id'] for x in layers}:
        raise ValueError('Unique distinct counterpart layer/sleeve references required')
    if 'part_ids' in c and (not isinstance(c['part_ids'],list) or not c['part_ids'] or len(set(c['part_ids']))!=len(c['part_ids']) or any(x not in rows for x in c['part_ids'])):
        raise ValueError('Actual unique counterpart part references required')
    if 'part_ids' in c and not {c['sleeve_id'],*(x['entity_id'] for x in layers)}<=set(c['part_ids']):
        raise ValueError('Counterpart part binding omits actual stack member')
    sleeve = rows[c['sleeve_id']];g = sleeve['geometry']
    geometry(g)
    if g['kind'] != 'annulus' or abs(abs(sleeve['rotation'][a][0])-1.) > 1e-10:
        raise ValueError('Actual coaxial annular sleeve required')
    L = g['size_m'][0];lo=sleeve['at_m'][a]-L/2;hi=sleeve['at_m'][a]+L/2
    if L <= 0 or not 0 < g['inner_radius_m'] < g['outer_radius_m']:
        raise ValueError('Positive sleeve material required')
    intervals=[]
    for layer in layers:
        r = rows[layer['entity_id']];gg = r['geometry']
        if gg['kind'] not in ('box','rhs'):
            raise ValueError('Unsupported counterpart primitive')
        size=vector(gg['size_m']);R=r['rotation'];direction=next((j for j in range(3) if abs(abs(R[a][j])-1.)<1e-10),None)
        if direction is None or min(size) <= 0:
            raise ValueError('Axis-aligned counterpart required')
        left=r['at_m'][a]-size[direction]/2;right=r['at_m'][a]+size[direction]/2
        intervals.append((left,right))
        if abs((right-left)-_scalar(layer['expected_depth_m'],positive=True))>1e-10:
            raise ValueError('Counterpart width/identity substitution')
        bore=layer['bore_index']
        if isinstance(bore,bool) or not isinstance(bore,int) or not 0<=bore<len(gg.get('holes',[])):
            raise ValueError('Actual counterpart bore index required')
        hole=gg['holes'][bore]
        if set(hole) != {'axis','centre_m','radius_m','length_m'}:
            raise ValueError('Unsupported bore schema; explicit normalization required')
        j=hole['axis'];vector(hole['centre_m']);centre=transform(hole['centre_m'],r['at_m'],R)
        if isinstance(j,bool) or not isinstance(j,int) or j not in (0,1,2) or abs(abs(R[a][j])-1.)>1e-10 or _scalar(hole['length_m'],positive=True) <= 0:
            raise ValueError('Bore axis/length differs')
        _scalar(hole['radius_m'],positive=True)
        if any(abs(centre[k]-sleeve['at_m'][k])>1e-10 for k in range(3) if k!=a):
            raise ValueError('Noncoaxial bore')
        if hole['radius_m'] < g['outer_radius_m'] or centre[a]-hole['length_m']/2>left+1e-10 or centre[a]+hole['length_m']/2<right-1e-10:
            raise ValueError('Bore continuity/diameter failed')
        if lo>left+1e-10 or hi<right-1e-10:
            raise ValueError('Sleeve does not span actual counterpart')
    intervals.sort()
    if any(a[1]>b[0]+1e-10 for a,b in zip(intervals,intervals[1:])):
        raise ValueError('Overlapping through-stack layer intervals; explicit material adapter required')


def _component_contracts(d):
    """Resolved status must refer to actual validated local physical contracts."""
    interfaces=d.get('physical_interfaces',[])
    if not isinstance(interfaces,list) or any(not isinstance(x,dict) or not isinstance(x.get('id'),str) or not x['id'].strip() for x in interfaces):
        raise ValueError('Named physical counterpart interfaces required')
    if len({x['id'] for x in interfaces})!=len(interfaces):
        raise ValueError('Duplicate physical interface ID')
    by={x['id']:x for x in interfaces};required=d.get('required_counterpart_ids',[])
    if not isinstance(required,list) or len(set(required))!=len(required) or any(x not in by for x in required):
        raise ValueError('Missing/duplicate physical counterpart obligation')
    rows={x['id']:x for x in d['entities']}
    for cid in required:_coaxial_contract(by[cid],rows)
    for jid,claim in d.get('joint_dispositions',{}).items():
        if claim['status']!='resolved-explicit-contract':continue
        physical=claim.get('physical_interface_ids');counterpart=claim.get('counterpart_ids')
        if any(not isinstance(xs,list) or not xs or len(set(xs))!=len(xs) for xs in (physical,counterpart)):
            raise ValueError('Resolved joint needs linked physical/counterpart contracts')
        if not set(counterpart)<=set(required) or set(physical)!=set(counterpart):
            raise ValueError('Resolved joint counterpart obligation/link differs')
        expected=d.get('source_joint_part_ids',{}).get(jid)
        if not isinstance(expected,list) or not expected or len(set(expected))!=len(expected) or any(x not in rows for x in expected):
            raise ValueError('Resolved joint needs exact source part binding')
        for cid in physical:
            if cid not in by or by[cid].get('source_joint_id')!=jid or set(by[cid].get('part_ids',[]))!=set(expected):
                raise ValueError('Resolved physical contract/source counterpart binding differs')
    return by


def _bound_contract(c, inst, context_bindings):
    out=interface_physical(c);out['id']=inst['id']+'/'+c['id']
    def ref(name):
        return context_bindings.get((inst['id'],name),inst['id']+'/'+name)
    out['sleeve_id']=ref(c['sleeve_id'])
    out['layers']=[dict(x,entity_id=ref(x['entity_id'])) for x in out['layers']]
    if 'part_ids' in out:out['part_ids']=[ref(x) for x in out['part_ids']]
    axis=c['axis_world'];R=inst['rotation']
    mapped=next((i for i in range(3) if abs(abs(R[i][axis])-1.)<1e-10),None)
    if mapped is None:raise ValueError('Unsupported rotated counterpart axis normalization')
    out['axis_world']=mapped
    return out


def _machining_features(old, new, features):
    """Authenticate explicit feature edits, not a Boolean/net-volume evaluator."""
    og=old['geometry'];ng=new['geometry'];bores=[];profile=False
    for f in features:
        if f.get('schema')!='osr-composition-machining/1':
            raise ValueError('Unsupported machining feature schema')
        if f['kind']=='bore':
            j=f['bore_index']
            if not isinstance(j,int) or isinstance(j,bool) or j<0 or j>=len(ng.get('holes',[])):
                raise ValueError('Machining bore not in actual successor geometry')
            h=ng['holes'][j]
            if set(h)!={'axis','centre_m','radius_m','length_m'} or h['axis'] not in (0,1,2) or h['radius_m']<=0 or h['length_m']<=0:
                raise ValueError('Unsupported machining bore geometry')
            vector(h['centre_m']);bores.append(identity(h))
        elif f['kind']=='profile-replacement':
            if profile or f['source_geometry_sha256']!=identity(og) or f['new_geometry_sha256']!=identity(ng):
                raise ValueError('Machining profile identity differs')
            profile=True
        else:
            raise ValueError('Unsupported machining operation; resolved adapter required')
    if len(bores)!=len(set(bores)):
        raise ValueError('Duplicate machining feature loss')
    if not profile:
        before=[identity(h) for h in og.get('holes',[])]
        after=[identity(h) for h in ng.get('holes',[])]
        plain=lambda g:{k:v for k,v in g.items() if k!='holes'}
        if identity(plain(og))!=identity(plain(ng)) or len(after)!=len(set(after)) or set(after)!=set(before)|set(bores) or set(before)&set(bores):
            raise ValueError('Unowned/duplicate machining geometry change')


def layout_datums(parent_layout, rows, revisions):
    """Correct a declared seat datum from counted box faces, without moving stock.

    Older source can carry a1.45m policy alongside already located1.60m pans.
    All explicitly tagged pan faces need exact geometry references. This narrow
    definition check establishes no occupant CG, comfort limit, measured
    tolerance or installed clearance. Other layout changes need their own
    physical/evaluator contract rather than this datum correction.
    """
    layout=deepcopy(parent_layout);receipts=[]
    tagged={key for key,row in rows.items() if 'seat-pan-datum' in row['functions']}
    if not isinstance(revisions,list) or len(revisions)>1:
        raise ValueError('At most one explicit supported layout datum correction')
    if tagged and not revisions:
        raise ValueError('Counted seat datum owners require explicit face bindings')
    for revision in revisions:
        if not isinstance(revision,dict) or set(revision)!={'field','from_m','to_m','basis','face_bindings'} or revision['field']!='seat_pan_z_m':
            raise ValueError('Unsupported physical layout datum correction')
        old=_scalar(revision['from_m'],positive=True);new=_scalar(revision['to_m'],positive=True)
        if layout.get('seat_pan_z_m')!=old or not isinstance(revision['basis'],str) or not revision['basis'].strip():
            raise ValueError('Exact previous datum and explicit correction basis required')
        if not _scalar(layout.get('floor_top_m'),positive=True)<new<_scalar(layout.get('roof_z_m'),positive=True):
            raise ValueError('Seat datum outside explicit floor/roof domain')
        bindings=revision['face_bindings']
        if not isinstance(bindings,list) or not tagged or len(bindings)!=len(tagged):
            raise ValueError('Every counted seat datum owner needs one face binding')
        seen=set();residuals=[]
        for b in bindings:
            if not isinstance(b,dict) or set(b)!={'entity_id','geometry_sha256','face'} or b['entity_id'] in seen or b['entity_id'] not in tagged or b['face'] not in ('z-min','z-max'):
                raise ValueError('Unique exact counted seat box face required')
            seen.add(b['entity_id']);row=rows[b['entity_id']];g=row['geometry']
            if g['kind']!='box' or g.get('holes') or b['geometry_sha256']!=identity(g):
                raise ValueError('Exact unbored seat datum box geometry required')
            if abs(abs(row['rotation'][2][2])-1.)>1e-10:
                raise ValueError('Seat datum face is not horizontal in body coordinates')
            local=[0.,0.,(-1 if b['face']=='z-min' else 1)*g['size_m'][2]/2]
            z=transform(local,row['at_m'],row['rotation'])[2];residual=z-new
            if abs(residual)>1e-10:
                raise ValueError('Counted seat face differs from corrected datum')
            residuals.append(dict(entity_id=b['entity_id'],face_z_m=z,residual_m=residual))
        if seen!=tagged:raise ValueError('Missing counted seat datum owner')
        layout['seat_pan_z_m']=new
        receipts.append(dict(revision=deepcopy(revision),face_residuals=residuals,
            stock_translation_m=0.,occupant_CG_inferred=False,physical_measurement=False))
    return layout,receipts


def compose(parent, definitions, integration, *, parent_pin, reviewed_map_id):
    """Construct one research bundle only after explicit external input review.

    The map must enumerate all definitions/instances, source frames/functions,
    modifications, exact context bindings and every required joint contract.
    This callable contains no permission mechanism and invokes no upstream job.
    """
    before=sources()
    authenticated(parent,parent_pin)
    authenticated(integration,{'evaluation_id':reviewed_map_id},physical=False)
    if integration['schema']!='osr-vehicle-integration-map/1' or integration['units']!='m' or integration['parent']!=parent_pin:
        raise ValueError('Exact parent/metre integration map required')
    if integration.get('unresolved_interfaces'):
        raise ValueError('Unresolved integration interfaces')
    ds={d['definition_id']:validate_definition(d) for d in definitions}
    if len(ds)!=len(definitions) or integration['definitions']!={k:d['evaluation_id'] for k,d in ds.items()}:
        raise ValueError('Definition identity/coverage substitution')
    original=parent_occurrences(parent,integration['source_frames'],integration['functions_by_part'])
    rows=deepcopy(original);added={};contexts=[];stock_groups=[]
    insts=integration['installations']
    if len({x['id'] for x in insts})!=len(insts):
        raise ValueError('Duplicate installation owner')
    for inst in insts:
        d=ds[inst['definition_id']];new,ctx=_place(d,inst)
        if set(added)&set(new) or set(original)&set(new):
            raise ValueError('Duplicate installed occurrence')
        added.update(new);contexts.extend((inst,x,y) for x,y in ctx)
        stock_groups.extend(dict(s,owner_id=inst['id']+'/'+s['id'],entity_ids=[inst['id']+'/'+x for x in s['entity_ids']]) for s in d['stock_groups'] if any(e['scope']=='installed' and e['id'] in s['entity_ids'] for e in d['entities']))
    modified=set();ledger=[]
    for op in integration['operations']:
        if op['kind'] not in ('replace','remove','machine_in_place','relocate') or not op.get('reason') or not op['source_ids']:
            raise ValueError('Explicit source modification required')
        for key in op['source_ids']:
            if key in modified or key not in original or op['source_hashes'].get(key)!=identity(original[key]['source_ref']):
                raise ValueError('Overlapping/missing/stale source ownership')
            modified.add(key)
        successors=op['successor_ids']
        if not successors or len(set(successors))!=len(successors) or any(k not in added for k in successors):
            raise ValueError('Missing functional successor')
        if op['kind'] in ('machine_in_place','relocate') and (len(op['source_ids'])!=1 or len(successors)!=1):
            raise ValueError('In-place operation needs one exact predecessor/successor')
        if op['kind']=='machine_in_place' and not op.get('machining_features'):
            raise ValueError('Explicit resolved machining features required')
        needed={f for k in op['source_ids'] for f in original[k]['functions']}
        supplied={f for k in successors for f in added[k]['functions']}
        if not needed<=supplied:
            raise ValueError('Missing function successor coverage')
        if op['kind'] in ('machine_in_place','relocate'):
            old=original[op['source_ids'][0]];new=added[successors[0]]
            if old['material_id']!=new['material_id'] or old['frame']!=new['frame']:
                raise ValueError('In-place/relocate counterpart material/frame changed')
            if op['kind']=='relocate':
                if identity(old['geometry'])!=identity(new['geometry']) or old['mass_kg']!=new['mass_kg']:
                    raise ValueError('Relocation changed physical stock')
            else:
                if old['at_m']!=new['at_m'] or old['rotation']!=new['rotation'] or any(new['mass_kg'][k]>old['mass_kg'][k]+1e-10 for k in CASES):
                    raise ValueError('In-place machining changed placement or added unowned material')
                group=next(s for s in stock_groups if s['owner_id']==new['stock_owner'])
                _machining_features(old,new,op['machining_features'])
                if group.get('procurement_disposition')!='retain-paid-source' or group.get('predecessor_source_id')!=old['id'] or group.get('parent_paid_cost_usd')!=old['direct_cost_usd']:
                    raise ValueError('Machining must retain exact source procurement ownership')
                cases(group['additional_process_usd'])
                for k in CASES:
                    if group['gross_mass_kg'][k]<old['mass_kg'][k] or abs(group['direct_cost_usd'][k]-old['direct_cost_usd'][k]-group['additional_process_usd'][k])>1e-8:
                        raise ValueError('Machining source gross/cost credit conservation failed')
        for key in op['source_ids']:rows.pop(key)
        ledger.append(deepcopy(op))
    rows.update(added)
    expected={(inst['id'],local) for inst,local,p in contexts}
    supplied={(x['installation_id'],x['local_id']) for x in integration['context_bindings']}
    if expected!=supplied or len(supplied)!=len(integration['context_bindings']):
        raise ValueError('Exact context/source ownership bindings required')
    byctx={(inst['id'],local):p for inst,local,p in contexts}
    for bind in integration['context_bindings']:
        key=bind['source_id'];p=byctx[(bind['installation_id'],bind['local_id'])]
        if key not in rows or key not in original or bind['source_ref_hash']!=identity(original[key]['source_ref']):
            raise ValueError('Context references retired/stale source')
        old=rows[key]
        if identity(p['geometry'])!=identity(old['geometry']) or any(abs(p['at_m'][i]-old['at_m'][i])>1e-10 for i in range(3)) or any(abs(p['rotation'][i][j]-old['rotation'][i][j])>1e-10 for i in range(3) for j in range(3)) or p['material_id']!=old['material_id'] or p['frame']!=old['frame']:
            raise ValueError('Changed counterpart cannot be context-only')
    # Requirements from definitions cannot be dropped by editing only the map.
    required={inst['id']+'/'+k for inst in insts for k in ds[inst['definition_id']].get('required_counterpart_ids',[])}
    if not required<=set(integration['required_counterpart_ids']):
        raise ValueError('Definition counterpart obligation omitted')
    contracts=integration['counterparts']
    if {c['id'] for c in contracts}!=set(integration['required_counterpart_ids']) or len({c['id'] for c in contracts})!=len(contracts):
        raise ValueError('Missing/duplicate resolved counterpart contract')
    bycontract={c['id']:c for c in contracts}
    contextrefs={(x['installation_id'],x['local_id']):x['source_id'] for x in integration['context_bindings']}
    for inst in insts:
        d=ds[inst['definition_id']];localcontracts={c['id']:c for c in d.get('physical_interfaces',[])}
        for cid in d.get('required_counterpart_ids',[]):
            expected=_bound_contract(localcontracts[cid],inst,contextrefs)
            if expected!=interface_physical(bycontract[expected['id']]):
                raise ValueError('Installed counterpart differs from bound physical definition')
    for c in contracts:_coaxial_contract(c,rows)
    installed=sorted(rows.values(),key=lambda r:r['id'])
    for r in installed:
        row_domain(r,parent['policy']['layout']['cars'])
    layout,datum_receipts=layout_datums(parent['policy']['layout'],rows,integration.get('layout_datum_revisions',[]))
    policy=deepcopy(parent['policy']);policy['layout']=layout
    physical=dict(schema='osr-composed-vehicle-physical/1',units='m',layout=deepcopy(layout),
        track_interface=deepcopy(parent['physical_definition'].get('track_interface')),
        occurrences=[entity_physical(r)|dict(car_allocation=r['car_allocation'],bogie_index=r['bogie_index']) for r in installed],
        physical_interfaces=[interface_physical(c) for c in contracts])
    cid=identity(physical)
    # Retained source rows and explicitly provided new entity models only.
    totals={k:mass_properties(installed,k) for k in CASES}
    nominal={k:totals[k]['mass_kg'] for k in CASES}
    direct={k:fsum(r['direct_cost_usd'][k] for r in installed) for k in CASES}
    lifecycle=[dict(definition_id=d['definition_id'],entities=[deepcopy(e) for e in d['entities'] if e['scope']=='lifecycle'],
        stock_groups=[deepcopy(s) for s in d['stock_groups'] if all(next(e for e in d['entities'] if e['id']==x)['scope']=='lifecycle' for x in s['entity_ids'])],multiplicity='unresolved site/lifecycle ownership; never per installed module') for d in definitions]
    # A catalogue bucket is evaluation metadata. Price changes can split it,
    # without changing the geometry-only physical occurrence projection above.
    parts={};patterns=[]
    for r in installed:
        spec={k:deepcopy(r[k]) for k in ('part_id','material_id','geometry')}
        component_id=identity(spec)
        bucket=identity(dict(component_id=component_id,mass_kg=r['mass_kg'],direct_cost_usd=r['direct_cost_usd'],cost_basis=r['cost_basis']))
        pid='composed/'+bucket
        if pid not in parts:
            parts[pid]=dict(id=pid,component_definition_id=component_id,candidate_id=component_id,
                source_part_id=r['part_id'] if 'source_ref' in r else None,material_id=r['material_id'],
                quantity_per_train=0,unit='item',make_buy='explicit-composition-source-route-unresolved',
                mass_each_kg=deepcopy(r['mass_kg']),direct_cost_each_usd=deepcopy(r['direct_cost_usd']),
                mass_basis=deepcopy(r['mass_basis']),cost_basis=r['cost_basis'],stock=deepcopy(r['geometry']))
        parts[pid]['quantity_per_train']+=1
        patterns.append(dict(r,part_id=pid,source_part_id=parts[pid]['source_part_id'],count=1,positions_m=[r['at_m']],
            assembly_id='composition',assembly_occurrence_id=r['id']))
    if sources()!=before:raise ValueError('Composition implementation changed during execution')
    return seal(dict(schema='osr-vehicle-installation/1',composition_schema='osr-occurrence-ledger-composition/1',candidate_id=cid,physical_definition=physical,
        parent_candidate_id=parent['candidate_id'],parent_evaluation_id=parent['evaluation_id'],integration_map_id=reviewed_map_id,
        component_evaluation_ids=integration['definitions'],patterns=patterns,parts=list(parts.values()),total_occurrences=len(patterns),
        parts_scope='Canonical occurrence catalogue; procurement route/BOP mapping remains explicit unresolved metadata',
        ownership_ledger=ledger,retained_source_ids=sorted(set(original)-modified),context_bindings=deepcopy(integration['context_bindings']),
        stock_groups=stock_groups,lifecycle_definitions=lifecycle,nominal_part_mass_kg=nominal,direct_parts_process_usd=direct,
        component_definitions=deepcopy(definitions),
        assembly_plans=dict(status='Current swept/tool/lift/removal evaluation required',
            source_plan_ancestry_sha256=identity(parent.get('assembly_plans')),installations=deepcopy(insts),
            declared_sequences=[dict(definition_id=d['definition_id'],sequences=deepcopy(d.get('assembly_sequences',[]))) for d in definitions],accepted=False),
        tare_mass_properties=totals,mass_scenarios=[],policy=policy,layout_datum_corrections=datum_receipts,selection_id=None,
        source_inputs=dict(parent=deepcopy(parent_pin),integration=reviewed_map_id,definitions=integration['definitions']),
        source_sha256=before,parent_source_sha256=deepcopy(parent.get('source_sha256',{})),
        cost_acceptance=False,fit_validation=None,journey_validation=None,native_validation=None,
        inherited_validations=False,definition_complete=True,loaded_evaluations_complete=False,
        holds=deepcopy(integration['holds'])+['Occupant/reserve scenarios, loaded reactions, actual joint loads, finite swept/tool/removal/lifting access, supplier/qualification and canonical catalogue/CAD/BIM/BOM adapters remain separate.',
            'Source and supplied entity inertia/material/cost bounds are hypotheses; no measured mass or installed cost claim.'],**FLAGS))


def evaluate_static_loads(bundle, scenario_rows, *, scenario_id, policy):
    """Separate explicit load evaluation; never inherit old passenger placement.

    Reuses the rigid two-stage vertical helper only within its six-car domain.
    Extra positive reserve/passenger rows are explicit and have disjoint IDs.
    """
    before=sources()
    authenticated(bundle,dict(candidate_id=bundle['candidate_id'],evaluation_id=bundle['evaluation_id']))
    fixed=dict(cars=6,car_length_m=17.,intercar_gap_m=.65,bogie_centres_local_x_m=[-6.4,6.4],bogie_wheelbase_m=2.1)
    if policy['layout']!=bundle['policy']['layout'] or any(policy['layout'].get(k)!=x for k,x in fixed.items()):
        raise ValueError('Static helper supports explicit unchanged six-car layout only')
    _scalar(policy['evaluation']['gravity_m_s2'],positive=True)
    if not scenario_id or not scenario_rows:
        raise ValueError('Explicit reviewed load/reserve scenario required')
    rows=deepcopy(bundle['patterns'])+deepcopy(scenario_rows)
    if len({r['id'] for r in rows})!=len(rows):raise ValueError('Load/reserve counted twice')
    for r in rows:row_domain(r,6)
    for r in scenario_rows:
        if not r.get('basis'):raise ValueError('Explicit load meaning required')
    results={k:dict(mass_properties=mass_properties(rows,k),reactions=reactions(rows,k,policy)) for k in CASES}
    if sources()!=before:raise ValueError('Static implementation changed during execution')
    return seal(dict(schema='osr-composed-static-loads/1',candidate_id=bundle['candidate_id'],body_evaluation_id=bundle['evaluation_id'],
        scenario_id=scenario_id,scenario_rows=scenario_rows,policy=policy,
        cases=results,source_sha256=before,
        scope='Rigid static vertical transfer only; supplied mass/inertia approximations retained, no dynamics/strength/lateral qualification',**FLAGS))


def adapt_p6_export(prototype, pin, component_map):
    """Source-specific adapter with complete explicit ownership, no guessed joints.

    P6 geometric IDs, geometry and frames are preserved. The reviewed map must
    provide per-entity inertia/centroid/uncertainty/functions and shared stock
    groups. Source quantity!=1, unfamiliar counterpart/bore normalization and
    procurement allocation require an upstream adapter rather than expansion.
    """
    before=sources()
    authenticated(prototype,pin)
    cs={c['id']:c for c in prototype['components']}
    if len(cs)!=len(prototype['components']) or set(component_map['entities'])!=set(cs) or component_map['units']!='m':
        raise ValueError('Complete exact P6 component ownership map required')
    source_joints={j['id'] for j in prototype.get('typed_fixing_joints',[])}
    if len(source_joints)!=len(prototype.get('typed_fixing_joints',[])):
        raise ValueError('Duplicate P6 source fixing joint identity')
    if set(component_map.get('joint_dispositions',{}))!=source_joints or any(not x.get('reason') or x.get('status') not in ('resolved-explicit-contract','qualification-hold-only','context-only') for x in component_map.get('joint_dispositions',{}).values()):
        raise ValueError('Complete explicit P6 joint/counterpart disposition required')
    hardware=prototype.get('hardware',{})
    bindings=component_map.get('hardware_bindings',{})
    if set(bindings)!=set(hardware) or any(not ids or len(ids)!=len(set(ids)) or any(x not in cs or component_map['entities'][x]['scope']!='installed' for x in ids) for ids in bindings.values()):
        raise ValueError('Explicit actual P6 hardware-to-entity binding required')
    for cut in prototype.get('P6_continuous_carrier_cut_groups',[]):
        sections=set(cut['section_occurrence_ids'])
        groups=[s for s in component_map['stock_groups'] if sections&set(s['entity_ids'])]
        if len(groups)!=1 or not sections<=set(groups[0]['entity_ids']) or any(component_map['entities'][x]['scope']!='installed' for x in sections):
            raise ValueError('Continuous P6 carrier cannot become separate/context procurement')
        s=groups[0]
        if (s.get('source_cut_group_id')!=cut['id'] or s.get('procurement_quantity')!=1 or
            s.get('physical_splice_count')!=0 or abs(s.get('cut_length_m',0)-cut['owned_material_length_m'])>1e-10 or
            abs(cut['owned_material_length_m']-cut['free_bend_length_m']-.060)>1e-10 or
            cut['tail_length_each_m']!=.030 or cut['gripped_length_each_m']!=.020 or cut['exposed_projection_each_m']!=.010):
            raise ValueError('Exact P6 continuous cut/tail/grip contract required')
    choices={}
    for name,ids in bindings.items():
        choice={k:deepcopy(hardware[name][k]) for k in HARDWARE_KEYS if k in hardware[name]}
        if not choice:raise ValueError('Unspecified actual P6 hardware choice')
        for cid in ids:
            if cid in choices:raise ValueError('Overlapping P6 hardware ownership')
            choices[cid]=choice
    entities=[]
    for cid,c in cs.items():
        spec=component_map['entities'][cid]
        if c.get('quantity',1)!=1:raise ValueError('Explicit P6 multiplicity adapter required')
        if c['frame']=='workshop' and spec['scope']!='lifecycle':raise ValueError('Workshop cannot become installed/context stock')
        e=dict(id=cid,part_id=c['part_id'],material_id=c['material_id'],geometry=deepcopy(c['geometry']),
            frame=c['frame'],at_m=deepcopy(c['at_m']),rotation=deepcopy(c['rotation']),scope=spec['scope'],functions=deepcopy(spec['functions']))
        if c.get('hardware_choice') is not None:e['hardware_choice']=deepcopy(c['hardware_choice'])
        if cid in choices:
            if 'hardware_choice' in e and e['hardware_choice']!=choices[cid]:raise ValueError('P6 hardware identity substitution')
            e['hardware_choice']=choices[cid]
        if spec['scope']!='context':
            e.update(mass_kg=deepcopy(c['mass_each_kg']),mass_basis=spec['mass_basis'],
                **{k:deepcopy(spec[k]) for k in ('centroid_local_m','shape_I_per_kg','inertia_basis','uncertainty_m','cost_share')})
        entities.append(e)
    d=dict(schema='osr-composition-component/1',units='m',entities=entities,stock_groups=deepcopy(component_map['stock_groups']),
        physical_interfaces=deepcopy(component_map['physical_interfaces']),source_inputs=dict(candidate_id=pin['candidate_id'],evaluation_id=pin['evaluation_id']),
        required_counterpart_ids=deepcopy(component_map.get('required_counterpart_ids',[])),
        joint_dispositions=deepcopy(component_map.get('joint_dispositions',{})),
        source_joint_part_ids={j['id']:deepcopy(j.get('part_ids')) for j in prototype.get('typed_fixing_joints',[])},
        geometry_status=component_map['geometry_status'],upstream_validation_inherited=False)
    d['source_sha256']=before
    d['definition_id']=identity(definition_physical(d));d=seal(d);validate_definition(d)
    if sources()!=before:raise ValueError('P6 adapter implementation changed during execution')
    return d
