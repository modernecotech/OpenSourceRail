"""Pure, source-bound isolated-solid point probes; never launches FreeCAD.

Plans validate internal case/oracle seals. The caller must also authenticate the
exact byte files and source/evaluation ancestry in a separately reviewed request.
Finite point checks supplement B-rep metrics; they are not shape equivalence,
interpart collision, installed fit, strength or physical acceptance evidence.
"""
from copy import deepcopy
from hashlib import sha256
import inspect
import json
from math import fsum, isfinite, pi, prod, sqrt
from pathlib import Path

FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             installed_vehicle_admitted=False, native_evaluator_admitted=False,
             manufacturing_release=False, operating_release=False,
             selected_reference_changed=False, movement_authority=False)
MIN_CLEARANCE_M = 1e-6
INSIDE_TOLERANCE_MM = 1e-5
BASE_MODULE_SHA256 = '2f593f3987f447083eec2b65b33b66633177475f78bc2007e6b2a6ef64919447'
BASE_WORKER_SHA256 = '2ee59db47c6e7a18bf1dd79a5a858577013159c1c742993a508fc816a0eb82b6'


def encoded(x):
    return (json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def identity(x):
    return sha256(encoded(x)).hexdigest()


def _number(x, positive=False):
    if type(x) not in (int, float) or not isfinite(x) or (positive and x <= 0):
        raise ValueError('Finite nonboolean SI scalar required')
    return float(x)


def _vector(x):
    if not isinstance(x, (list, tuple)) or len(x) != 3:
        raise ValueError('Explicit three-coordinate metre vector required')
    return [_number(v) for v in x]


def _digest(x):
    if not isinstance(x, str) or len(x) != 64 or any(v not in '0123456789abcdef' for v in x):
        raise ValueError('Exact source/component identity required')


def _name(x):
    if not isinstance(x, str) or not x.strip() or len(x) > 512 or any(ord(v) < 32 for v in x):
        raise ValueError('Unique printable material identity required')


def _axis(x):
    if type(x) is not int or x not in (0, 1, 2):
        raise ValueError('Nonboolean primitive axis required')
    return x


def _measure(s):
    """Validate normalized primitive domain and reproduce its nominal oracle."""
    _name(s.get('id')); _name(s.get('material'))
    if s.get('shape') == 'box':
        if set(s) != {'id', 'material', 'shape', 'corner_m', 'size_m', 'cuts'}:
            raise ValueError('Unknown normalized box feature')
        lo = _vector(s['corner_m']); size = [_number(v, True) for v in _vector(s['size_m'])]
        hi = [x+y for x, y in zip(lo, size)]; center = [(a+b)/2 for a, b in zip(lo, hi)]
        if not isinstance(s['cuts'], list) or len(s['cuts']) > 64:
            raise ValueError('Explicit bounded cuts required')
        removed = []; cuts = []
        for c in s['cuts']:
            if set(c) != {'axis', 'base_m', 'radius_m', 'length_m'}:
                raise ValueError('Unknown cut feature')
            a, base = _axis(c['axis']), _vector(c['base_m'])
            r, L = _number(c['radius_m'], True), _number(c['length_m'], True)
            if (L > size[a]+1e-12 or min(abs(base[a]-lo[a]), abs(base[a]+L-hi[a])) > 1e-12
                    or any(base[k]-r < lo[k]-1e-12 or base[k]+r > hi[k]+1e-12 for k in range(3) if k != a)):
                raise ValueError('Cut not contained/from a declared material face')
            for b in cuts:
                if any(min(base[k]+(L if k == a else r), b['base_m'][k]+(b['length_m'] if k == b['axis'] else b['radius_m'])) <=
                       max(base[k] if k == a else base[k]-r, b['base_m'][k] if k == b['axis'] else b['base_m'][k]-b['radius_m']) for k in range(3)):
                    continue
                if a == b['axis'] and fsum((base[k]-b['base_m'][k])**2 for k in range(3) if k != a) >= (r+b['radius_m'])**2:
                    continue
                raise ValueError('Intersecting/unresolved cut union')
            cuts.append(c)
            V = pi*r*r*L; cc = [base[k]+(L/2 if k == a else 0.) for k in range(3)]
            removed.append((V, cc))
        V = prod(size)-fsum(x[0] for x in removed)
        if V <= 0: raise ValueError('No positive net material')
        center = [(prod(size)*center[k]-fsum(v*c[k] for v, c in removed))/V for k in range(3)]
    elif s.get('shape') == 'cylinder':
        if set(s) != {'id', 'material', 'shape', 'axis', 'start_m', 'length_m', 'radius_m', 'inner_radius_m'}:
            raise ValueError('Unknown round feature')
        a, start = _axis(s['axis']), _vector(s['start_m'])
        L, r, ri = _number(s['length_m'], True), _number(s['radius_m'], True), _number(s['inner_radius_m'])
        if not 0 <= ri < r: raise ValueError('Positive round material required')
        V = pi*(r*r-ri*ri)*L
        center = [start[k]+(L/2 if k == a else 0.) for k in range(3)]
        lo = [start[k] if k == a else start[k]-r for k in range(3)]
        hi = [start[k]+L if k == a else start[k]+r for k in range(3)]
    else:
        raise ValueError('Unknown/unresolved material solid')
    return dict(volume_m3=V, center_of_mass_m=center, bbox_m=dict(min=lo, max=hi))


def nominal_state(s, point):
    """Nominal membership and conservative distance to a boundary, in metres."""
    p = _vector(point)
    if s['shape'] == 'box':
        lo = s['corner_m']; hi = [a+b for a, b in zip(lo, s['size_m'])]
        gaps = [max(a-v, v-b, 0.) for a, b, v in zip(lo, hi, p)]
        if any(gaps): return False, sqrt(fsum(v*v for v in gaps))
        outer = min(min(v-a, b-v) for a, b, v in zip(lo, hi, p))
        distances = []
        for c in s['cuts']:
            a, base, r, L = c['axis'], c['base_m'], c['radius_m'], c['length_m']
            radial = sqrt(fsum((p[k]-base[k])**2 for k in range(3) if k != a))
            t = p[a]-base[a]
            if 0 <= t <= L and radial <= r:
                return False, min(r-radial, t, L-t)
            distances.append(sqrt(max(radial-r, 0.)**2+max(-t, t-L, 0.)**2))
        return True, min([outer]+distances)
    a, base, L, r, ri = s['axis'], s['start_m'], s['length_m'], s['radius_m'], s['inner_radius_m']
    t = p[a]-base[a]; radial = sqrt(fsum((p[k]-base[k])**2 for k in range(3) if k != a))
    if 0 <= t <= L and ri <= radial <= r:
        return True, min(t, L-t, r-radial, radial-ri if ri else r)
    if ri and radial < ri and 0 < t < L:
        return False, min(ri-radial, t, L-t)
    return False, sqrt(max(ri-radial, radial-r, 0.)**2+max(-t, t-L, 0.)**2)


def _probes(s):
    out = []
    def add(tag, point, inside):
        actual, clearance = nominal_state(s, point)
        if actual is not inside or clearance < MIN_CLEARANCE_M:
            raise ValueError('Unsupported/boundary probe '+s['id']+'/'+tag)
        out.append(dict(id=tag, point_m=list(point), inside=inside, clearance_m=clearance))
    if s['shape'] == 'box':
        lo, size = s['corner_m'], s['size_m']; hi = [a+b for a, b in zip(lo, size)]
        material = None
        for fractions in ((a,b,c) for a in (.125,.5,.875) for b in (.125,.5,.875) for c in (.125,.5,.875)):
            point = [a+f*b for a,f,b in zip(lo,fractions,size)]
            state, margin = nominal_state(s,point)
            if state and margin >= MIN_CLEARANCE_M: material=point; break
        if material is None: raise ValueError('No robust interior material witness')
        add('material/interior', material, True)
        for i,c in enumerate(s['cuts']):
            a, base, r, L = c['axis'], c['base_m'], c['radius_m'], c['length_m']
            for frac in (.25,.5,.75):
                point=base[:];point[a]+=L*frac;add(f'cut/{i}/void/{frac}',point,False)
            rims=0
            for k in range(3):
                if k == a: continue
                for sign in (-1,1):
                    land=(hi[k]-base[k] if sign==1 else base[k]-lo[k])-r
                    delta=min(r/2,land/2)
                    if delta < MIN_CLEARANCE_M: continue
                    point=base[:];point[a]+=L/2;point[k]+=sign*(r+delta)
                    state,margin=nominal_state(s,point)
                    if state and margin >= MIN_CLEARANCE_M:
                        add(f'cut/{i}/rim/{k}/{sign}',point,True);rims+=1
            if not rims: raise ValueError('No supported material rim for bore')
            through=abs(L-size[a])<=1e-12
            minimum_entry=abs(base[a]-lo[a])<=1e-12
            step=min(r,L,min(size))/4
            entry=base[:];entry[a]=(lo[a]-step if minimum_entry else hi[a]+step)
            add(f'cut/{i}/entry-outside',entry,False)
            if not through:
                remaining=size[a]-L
                end=base[:];end[a]=(base[a]+L+remaining/2 if minimum_entry else base[a]-remaining/2)
                add(f'cut/{i}/blind-end-material',end,True)
    else:
        a,L,r,ri=s['axis'],s['length_m'],s['radius_m'],s['inner_radius_m']
        middle=s['start_m'][:];middle[a]+=L/2
        trans=[k for k in range(3) if k!=a]
        radius=(r+ri)/2 if ri else r/2
        for k in trans:
            for sign in (-1,1):
                point=middle[:];point[k]+=sign*radius;add(f'round/material/{k}/{sign}',point,True)
        if ri: add('round/annular-void',middle,False)
        else: add('round/axis-material',middle,True)
        point=middle[:];point[trans[0]]+=r+min(r,L)/4;add('round/radial-outside',point,False)
        point=middle[:];point[trans[0]]+=radius;point[a]=s['start_m'][a]-min(r,L)/4
        add('round/axial-outside',point,False)
    return out


def _validate(case, expected):
    if case.get('schema')!='osr-local-chair-native-geometry/1' or case.get('units')!='m' or case.get('frame')!='coupon-local':
        raise ValueError('Exact coupon-local metre case required')
    for flag in ('physical_accepted','engineering_accepted','native_evaluator_admitted','installed_mass_complete',
                 'manufacturing_release','operating_release','selected_reference_changed','movement_authority'):
        if case.get(flag) is not False: raise ValueError('Probe plan cannot grant acceptance')
    for key in ('source_physical_definition_id','source_execution_id','component_geometry_id'): _digest(case.get(key))
    if identity({k:case[k] for k in ('schema','units','frame','entities')}) != case['component_geometry_id']:
        raise ValueError('Component geometry seal differs')
    es=case.get('entities')
    if not isinstance(es,list) or not 1<=len(es)<=3500 or not isinstance(expected,dict):
        raise ValueError('Bounded explicit source/oracle records required')
    ids=[e.get('id') for e in es]
    if len(set(ids))!=len(ids) or set(ids)!=set(expected): raise ValueError('Missing/duplicate/extra material oracle')
    for s in es:
        measured=_measure(s);e=expected[s['id']]
        if not isinstance(e,dict) or e.get('source_material')!=s['material'] or e.get('complete_installed') is not False:
            raise ValueError('Exact unqualified material oracle required')
        volume=_number(e.get('volume_m3'),True)
        if abs(volume-measured['volume_m3'])>1e-14+measured['volume_m3']*1e-10: raise ValueError('Oracle volume differs')
        for key in ('center_of_mass_m',):
            if max(abs(a-b) for a,b in zip(_vector(e.get(key)),measured[key]))>1e-10: raise ValueError('Oracle centroid differs')
        for key in ('min','max'):
            if max(abs(a-b) for a,b in zip(_vector(e.get('bbox_m',{}).get(key)),measured['bbox_m'][key]))>1e-10: raise ValueError('Oracle bounds differ')
    return es


def compile_probe_plan(case, expected):
    es=_validate(case,expected)
    records=[dict(id=s['id'],expected=deepcopy(expected[s['id']]),probes=_probes(s)) for s in es]
    if sum(len(r['probes']) for r in records)>30000: raise ValueError('Probe count budget exceeded')
    value=dict(schema='osr-chair-isolated-solid-probe-plan/1',units='m',native_units='mm',
        scope='Individual source material solid only; no interpart collision/fit/strength/installation',
        case=deepcopy(case),oracle=deepcopy(expected),records=records,
        bindings={k:case[k] for k in ('source_physical_definition_id','source_execution_id','component_geometry_id')},
        case_record_id=identity(case),oracle_record_id=identity(expected),
        minimum_clearance_m=MIN_CLEARANCE_M,inside_tolerance_mm=INSIDE_TOLERANCE_MM,
        native_point_scale_mm_per_m=1000.,on_boundary_argument=True,
        matching=dict(volume_relative=1e-7,volume_absolute_m3=1e-12,coordinate_absolute_m=1e-7),
        implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        source_provenance='Caller must bind exact frozen byte files/source request; these are internally validated record identities',**FLAGS)
    value['plan_id']=identity(value);return value


def evaluate_probes(plan, bodies, contains):
    """Pure runtime used both by mocks and by the instrumented B-rep worker."""
    import math
    records=plan['records'];by_source={r['id']:r for r in records};mapping={};issues=[]
    def vector(v):
        return isinstance(v,(list,tuple)) and len(v)==3 and all(type(x) in (int,float) and math.isfinite(x) for x in v)
    def matches(a,b):
        if (b.get('valid') is not True or b.get('closed') is not True or b.get('all_solids_closed_valid') is not True or b.get('solid_count')!=1):return False
        v=b.get('volume_m3')
        if type(v) not in (int,float) or not math.isfinite(v) or v<=0:return False
        if abs(a['volume_m3']-v)>a['volume_m3']*1e-7+1e-12:return False
        if not vector(b.get('center_of_mass_m')) or max(abs(x-y) for x,y in zip(a['center_of_mass_m'],b['center_of_mass_m']))>1e-7:return False
        box=b.get('bbox_m',{})
        return all(vector(box.get(k)) and max(abs(x-y) for x,y in zip(a['bbox_m'][k],box[k]))<=1e-7 for k in ('min','max'))
    for r in records:
        options=[b for b in bodies if matches(r['expected'],b)]
        if len(options)!=1:
            issues.append(dict(source_id=r['id'],reason='Missing/ambiguous metric mapping',candidates=[b.get('native_name') for b in options]));continue
        b=options[0];name=b.get('native_name')
        if not isinstance(name,str) or not name or name in [x['native_name'] for x in mapping.values()]:
            issues.append(dict(source_id=r['id'],reason='Duplicate/missing native solid mapping'));continue
        mapping[r['id']]=dict(native_name=name,native_label=b.get('id'))
    if len(bodies)!=len(records):issues.append(dict(reason='Native/source body count differs'))
    raw_labels=[b.get('id') for b in bodies]
    strict_names=len(raw_labels)==len(set(raw_labels)) and set(raw_labels)==set(by_source)
    results=[]
    for source,m in mapping.items():
        for probe in by_source[source]['probes']:
            row=dict(source_id=source,native_name=m['native_name'],probe_id=probe['id'],point_m=probe['point_m'],expected_inside=probe['inside'],clearance_m=probe['clearance_m'])
            try:
                inside=contains(m['native_name'],probe['point_m'])
                if type(inside) is not bool:raise ValueError('Native membership result is not boolean')
                row.update(actual_inside=inside,passed=inside is probe['inside'])
            except Exception as e:row.update(passed=False,error=type(e).__name__+': '+str(e))
            results.append(row)
    mismatches=[r for r in results if r['passed'] is not True]
    return dict(execution='completed',geometry_verification='passed' if not issues and not mismatches else 'held',
        strict_native_name_identity='passed' if strict_names else 'failed',strict_name_failure=None if strict_names else 'STEP source occurrence identity/count differs',
        mapping=mapping,mapping_issues=issues,planned_probe_count=sum(len(r['probes']) for r in records),executed_probe_count=len(results),
        results=results,mismatches=mismatches,method='OCC per-isolated-solid isInside; finite interior/void samples supplement metric correspondence',
        physical_accepted=False,engineering_accepted=False,native_evaluator_admitted=False,installed_vehicle_admitted=False)


def instrument_freecad_worker(base_worker, plan):
    """Return explicitly changed worker text/metadata; never executes it."""
    if not isinstance(base_worker,str) or sha256(base_worker.encode()).hexdigest()!=BASE_WORKER_SHA256:
        raise ValueError('Exact pinned FreeCAD base WORKER required')
    if plan.get('plan_id')!=identity({k:v for k,v in plan.items() if k!='plan_id'}): raise ValueError('Probe plan seal differs')
    if plan.get('schema')!='osr-chair-isolated-solid-probe-plan/1' or plan.get('units')!='m' or plan.get('native_units')!='mm':
        raise ValueError('Probe plan unit/schema contract differs')
    if any(plan.get(k) is not False for k in FLAGS): raise ValueError('Probe plan cannot grant acceptance')
    es=_validate(plan['case'],plan['oracle'])
    if (plan['bindings']!={k:plan['case'][k] for k in ('source_physical_definition_id','source_execution_id','component_geometry_id')}
            or plan['implementation_sha256']!=sha256(Path(__file__).read_bytes()).hexdigest()
            or plan['matching']!=dict(volume_relative=1e-7,volume_absolute_m3=1e-12,coordinate_absolute_m=1e-7)):
        raise ValueError('Probe source/method/oracle comparison binding differs')
    expected_records=[dict(id=s['id'],expected=deepcopy(plan['oracle'][s['id']]),probes=_probes(s)) for s in es]
    if plan['records']!=expected_records or plan['case_record_id']!=identity(plan['case']) or plan['oracle_record_id']!=identity(plan['oracle']):
        raise ValueError('Probe plan source/oracle/features changed')
    if (plan['minimum_clearance_m']!=MIN_CLEARANCE_M or plan['inside_tolerance_mm']!=INSIDE_TOLERANCE_MM or
        plan['native_point_scale_mm_per_m']!=1000. or plan['on_boundary_argument'] is not True):
        raise ValueError('Probe units/tolerance/strict interior contract differs')
    before='    doc = App.newDocument(\'IndependentSTEPReference\')'
    marker='except BaseException as error:'
    if base_worker.count(before)!=1 or base_worker.count(marker)!=1: raise ValueError('Base worker instrumentation anchors differ')
    limits="    resource.setrlimit(resource.RLIMIT_CPU, (120, 120))\n    if resource.getrlimit(resource.RLIMIT_AS) != (2147483648, 2147483648):\n        raise ValueError('Instrumented reference requires observed2GiB address-space limits')\n"
    runtime=inspect.getsource(evaluate_probes)
    code='\n'+''.join('    '+line+'\n' for line in runtime.splitlines())
    code+='    _probe_plan = json.loads('+repr(encoded(plan).decode())+')\n'
    code+="    def _source_solid_contains(native_name, point_m):\n        shape = doc.getObject(native_name).Shape\n        point = App.Vector(*(v*1000.0 for v in point_m))\n        return bool(shape.isInside(point, 0.00001, True))\n"
    code+="    result['point_probes'] = evaluate_probes(_probe_plan, bodies, _source_solid_contains)\n"
    code+="    import hashlib\n    result['probe_instrumentation'] = dict(plan_id=_probe_plan['plan_id'], base_module_sha256="+repr(BASE_MODULE_SHA256)+", base_worker_sha256="+repr(BASE_WORKER_SHA256)+", method_source_sha256="+repr(sha256(Path(__file__).read_bytes()).hexdigest())+", actual_worker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), native_point_scale_mm_per_m=1000.0, inside_tolerance_mm=0.00001, on_boundary_argument=True, CPU_limit_s=list(resource.getrlimit(resource.RLIMIT_CPU)), AS_limit_bytes=list(resource.getrlimit(resource.RLIMIT_AS)))\n"
    worker=base_worker.replace(before,limits+before).replace(marker,code+marker)
    compile(worker,'instrumented-freecad-probe-worker','exec')
    return dict(worker=worker,worker_sha256=sha256(worker.encode()).hexdigest(),base_module_sha256=BASE_MODULE_SHA256,
        base_worker_sha256=BASE_WORKER_SHA256,probe_plan_id=plan['plan_id'],method_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        actual_native_calls=0,actual_probe_execution=False,**FLAGS)
