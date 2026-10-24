"""SI candidate, evaluation and result contracts; unknown stock is never zero."""
from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import PurePosixPath

UNITS = dict(length='m', mass='kg', time='s', temperature='degC', force='N', inertia='kg*m^2')
EXECUTION = {'not-run', 'running', 'interrupted', 'executed', 'refused', 'error'}
NUMERICAL = {'not-assessed', 'converged', 'nonconverged', 'invalid', 'unknown'}
SCREENS = {'not-assessed', 'pass', 'fail', 'unknown'}
MATURITY = {'definition': 0, 'numerical-screen': 1, 'coupled-numerical': 2,
            'rig-correlated': 3, 'independently-reviewed': 4}
PURPOSES = {'diagnostic', 'next-experiment', 'integrated-baseline', 'confirmation'}
FLAGS = dict(physical_accepted=False, engineering_accepted=False, configuration_adopted=False)
PHYSICAL_KEYS = ('architecture', 'frames', 'materials', 'geometry', 'interfaces', 'installed_inventory')


class UnknownInstalledStock(ValueError):
    pass


def encoded(value):
    def scalar(item):
        if type(item).__module__.startswith('numpy'):
            return item.tolist() if hasattr(item,'tolist') else item.item()
        raise TypeError('non-JSON design value: '+type(item).__name__)
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False,default=scalar)+'\n').encode()


def identity(value):return sha256(encoded(value)).hexdigest()


def finite(value, name, positive=False):
    if type(value) not in (int, float) or not math.isfinite(value) or (positive and value <= 0):
        raise ValueError('finite '+('positive ' if positive else '')+name+' required')
    return float(value)


def vector(value, name):
    if not isinstance(value, (list, tuple)) or len(value) != 3:raise ValueError('3D '+name+' required')
    return [finite(x, name) for x in value]


def _matmul(a,b):return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def _transpose(a):return [list(row) for row in zip(*a)]
def _mv(a,v):return [sum(a[i][j]*v[j] for j in range(3)) for i in range(3)]


def _rotation(value):
    if not isinstance(value,list) or len(value)!=3:raise ValueError('3x3 rotation required')
    value=[vector(row,'rotation row') for row in value];product=_matmul(value,_transpose(value))
    det=sum(value[0][j]*(value[1][(j+1)%3]*value[2][(j+2)%3]-value[1][(j+2)%3]*value[2][(j+1)%3]) for j in range(3))
    if any(abs(product[i][j]-(i==j))>1e-9 for i in range(3) for j in range(3)) or abs(det-1)>1e-9:
        raise ValueError('right-handed orthonormal frame required')
    return value


def _unique(rows,name):
    if not isinstance(rows,list) or any(not isinstance(row,dict) or not isinstance(row.get('id'),str) or not row['id'] for row in rows):
        raise ValueError('identified '+name+' list required')
    if len({row['id'] for row in rows})!=len(rows):raise ValueError('unique '+name+' identifiers required')
    return {row['id']:row for row in rows}


def _psd(matrix):
    scale=max(1.,*(abs(value) for row in matrix for value in row));tolerance=1e-10
    if any(matrix[i][i]<-tolerance*scale for i in range(3)):return False
    if any(matrix[i][i]*matrix[j][j]-matrix[i][j]**2<-tolerance*scale**2 for i in range(3) for j in range(i+1,3)):return False
    determinant=sum(matrix[0][j]*(matrix[1][(j+1)%3]*matrix[2][(j+2)%3]-matrix[1][(j+2)%3]*matrix[2][(j+1)%3]) for j in range(3))
    return determinant>=-tolerance*scale**3


def frame_transform(candidate, frame_id):
    frames={row['id']:row for row in candidate['frames']};seen=set()
    def resolve(name):
        if name in seen:raise ValueError('cyclic coordinate frames')
        if name not in frames:raise ValueError('unknown coordinate frame: '+name)
        seen.add(name);frame=frames[name];r=_rotation(frame['rotation_matrix']);o=vector(frame['origin_m'],'frame origin')
        if frame.get('parent_id') is not None:
            pr,po=resolve(frame['parent_id']);o=[a+b for a,b in zip(po,_mv(pr,o))];r=_matmul(pr,r)
        seen.remove(name);return r,o
    return resolve(frame_id)


def validate_candidate(candidate):
    if candidate.get('schema')!='osr-design-candidate/1' or candidate.get('units')!=UNITS:raise ValueError('explicit SI candidate required')
    if not isinstance(candidate.get('requirement_revision'),str) or not candidate['requirement_revision']:raise ValueError('requirement revision required')
    if any(candidate.get(flag) is not False for flag in FLAGS):raise ValueError('candidate cannot assert acceptance')
    frames=_unique(candidate['frames'],'frame');materials=_unique(candidate['materials'],'material')
    geometry=_unique(candidate['geometry'],'geometry');_unique(candidate['interfaces'],'interface');inventory=_unique(candidate['installed_inventory'],'inventory')
    if not frames:raise ValueError('coordinate frame required')
    for name in frames:frame_transform(candidate,name)
    for material in materials.values():
        if material.get('density_kg_m3') is not None:finite(material['density_kg_m3'],'material density',True)
        if not material.get('basis'):raise ValueError('material basis required')
    for part in geometry.values():
        if part.get('frame_id') not in frames or part.get('material_id') not in materials:raise ValueError('geometry frame/material required')
        if not part.get('kind'):raise ValueError('geometric primitive required')
        if part['kind']=='box':
            if len(part.get('size_m',[]))!=3:raise ValueError('3D box dimensions required')
            for dimension in part['size_m']:finite(dimension,'box dimension',True)
            vector(part.get('at_m'),'box origin')
    for row in inventory.values():
        if row.get('status') not in ('known','unknown'):raise ValueError('known/unknown stock status required')
        if type(row.get('quantity')) is not int or row['quantity']<1:raise ValueError('positive integer quantity required')
        if not row.get('scope') or not row.get('basis'):raise ValueError('inventory scope/basis required')
        if row['status']=='unknown':
            if row.get('unit_mass_kg') is not None:raise ValueError('unknown stock cannot assert mass')
        elif finite(row.get('unit_mass_kg'),'unit mass')<0:raise ValueError('nonnegative mass required')
        if row.get('frame_id') not in frames:raise ValueError('inventory frame required')
        if row.get('geometry_id') is not None and row['geometry_id'] not in geometry:raise ValueError('unknown inventory geometry')
        if row.get('cg_m') is not None:vector(row['cg_m'],'stock CG')
        inertia=row.get('inertia_kg_m2')
        if inertia is not None:
            if len(inertia)!=3:raise ValueError('3x3 stock inertia required')
            inertia=[vector(axis,'inertia row') for axis in inertia]
            if any(abs(inertia[i][j]-inertia[j][i])>1e-8 for i in range(3) for j in range(3)) or any(inertia[i][i]<0 for i in range(3)):
                raise ValueError('symmetric nonnegative inertia required')
            covariance=[[sum(inertia[k][k] for k in range(3))/2*(i==j)-inertia[i][j] for j in range(3)] for i in range(3)]
            if not _psd(inertia) or not _psd(covariance):raise ValueError('physical PSD inertia and principal-moment triangle condition required')
        if row['status']=='known' and row.get('geometry_id') is not None:
            part=geometry[row['geometry_id']];density=materials[part['material_id']].get('density_kg_m3')
            if part['kind']=='box' and density is not None:
                expected=math.prod(part['size_m'])*density
                if not math.isclose(row['unit_mass_kg'],expected,rel_tol=1e-9,abs_tol=1e-8):raise ValueError('inventory mass differs from physical box/material')
    def check(value):
        if isinstance(value,dict):
            if {'evaluation_hypothesis','flux_allocation_hypothesis','solver_settings','selection_policy'}&value.keys():
                raise ValueError('hypothesis/policy belongs outside physical candidate')
            for item in value.values():check(item)
        elif isinstance(value,list):
            for item in value:check(item)
    physical={key:candidate[key] for key in PHYSICAL_KEYS};check(physical)
    if candidate.get('candidate_id')!=identity(dict(units=UNITS,**physical)):raise ValueError('candidate physical identity differs')
    encoded(candidate);return candidate


def make_candidate(*, requirement_revision, architecture, frames, materials, geometry, interfaces, installed_inventory, lineage=None, label='', source_bindings=None):
    physical=deepcopy(dict(architecture=architecture,frames=frames,materials=materials,geometry=geometry,interfaces=interfaces,installed_inventory=installed_inventory))
    value=dict(schema='osr-design-candidate/1',candidate_id=identity(dict(units=UNITS,**physical)),requirement_revision=requirement_revision,
        label=label,units=deepcopy(UNITS),lineage=deepcopy(lineage or dict(parent_candidate_ids=[],operation='authored-definition')),
        source_bindings=deepcopy(source_bindings or {}),**physical,**FLAGS)
    return validate_candidate(json.loads(encoded(value)))


def bind_context(physical,*,requirement_revision,lineage=None,label='',source_bindings=None):
    if physical.get('schema') not in ('osr-design-physical-candidate/1','osr-design-candidate/1'):
        raise ValueError('physical candidate record required')
    candidate=make_candidate(requirement_revision=requirement_revision,lineage=lineage,label=label,source_bindings=source_bindings,
        **{key:physical[key] for key in PHYSICAL_KEYS})
    if candidate['candidate_id']!=physical['candidate_id']:raise ValueError('physical record identity differs')
    return candidate


def mass_properties(candidate, scope='vehicle-per-car'):
    validate_candidate(candidate)
    return _mass_properties(candidate,scope)


def _mass_properties(candidate,scope):
    known=[];unknown=[];unlocated=[];missing_inertia=[]
    for row in candidate['installed_inventory']:
        if row['scope']!=scope:continue
        if row['status']=='unknown':unknown.append(row['id']);continue
        mass=row['unit_mass_kg']*row['quantity']
        if row.get('cg_m') is None:unlocated.append(row['id']);known.append((mass,None,None));continue
        r,o=frame_transform(candidate,row['frame_id']);cg=[a+b for a,b in zip(o,_mv(r,row['cg_m']))]
        local=row.get('inertia_kg_m2');inertia=None if local is None else [[row['quantity']*v for v in axis] for axis in _matmul(_matmul(r,local),_transpose(r))]
        if inertia is None:missing_inertia.append(row['id'])
        known.append((mass,cg,inertia))
    if not known and not unknown:raise ValueError('inventory scope missing: '+scope)
    subtotal=math.fsum(row[0] for row in known);complete=not unknown;cg=None
    if complete and not unlocated and subtotal>0:cg=[math.fsum(m*centre[i] for m,centre,_ in known)/subtotal for i in range(3)]
    inertia=None
    if cg is not None and not missing_inertia:
        inertia=[[0.]*3 for _ in range(3)]
        for mass,centre,local in known:
            d=[centre[i]-cg[i] for i in range(3)];square=sum(v*v for v in d)
            for i in range(3):
                for j in range(3):inertia[i][j]+=local[i][j]+mass*((square if i==j else 0.)-d[i]*d[j])
    return dict(scope=scope,known_mass_subtotal_kg=subtotal,total_mass_kg=subtotal if complete else None,cg_m=cg,inertia_kg_m2=inertia,
        unknown_stock_ids=unknown,unlocated_stock_ids=unlocated,missing_inertia_ids=missing_inertia,
        complete_installed_distribution=complete and cg is not None and inertia is not None,unknown_is_zero=False,physical_accepted=False)


def inventory_summary(candidate):
    validate_candidate(candidate)
    scopes=sorted({row['scope'] for row in candidate['installed_inventory']})
    values={scope:_mass_properties(candidate,scope) for scope in scopes}
    return dict(scopes=values,unknown_stock_ids=[name for value in values.values() for name in value['unknown_stock_ids']],
        unlocated_stock_ids=[name for value in values.values() for name in value['unlocated_stock_ids']],
        complete_installed_distribution=all(value['complete_installed_distribution'] for value in values.values()),unknown_is_zero=False)


def _validate_sources(sources):
    if not isinstance(sources,dict) or not sources:raise ValueError('evaluator source bindings required')
    for name,digest in sources.items():
        if not isinstance(name,str) or not name or PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts or '\\' in name or PurePosixPath(name).as_posix()!=name:
            raise ValueError('repository-relative evaluator source required')
        if not isinstance(digest,str) or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):raise ValueError('source SHA256 required')


def make_evaluation_request(candidate, *, evaluator_id, evaluator_sources, hypothesis=None, settings=None, mesh=None, scenario=None, environment=None, purpose='diagnostic'):
    validate_candidate(candidate)
    if purpose not in PURPOSES or not evaluator_id:raise ValueError('evaluator sources/purpose required')
    _validate_sources(evaluator_sources)
    payload=dict(candidate_id=candidate['candidate_id'],requirement_revision=candidate['requirement_revision'],evaluator_id=evaluator_id,
        evaluator_sources=deepcopy(evaluator_sources),hypothesis=deepcopy(hypothesis or {}),settings=deepcopy(settings or {}),mesh=deepcopy(mesh or {}),
        scenario=deepcopy(scenario or {}),environment=deepcopy(environment or {}),purpose=purpose)
    return dict(schema='osr-design-evaluation-request/1',evaluation_id=identity(payload),**payload)


def validate_request(request):
    if request.get('schema')!='osr-design-evaluation-request/1':raise ValueError('evaluation request required')
    payload={key:value for key,value in request.items() if key not in ('schema','evaluation_id')}
    if request.get('evaluation_id')!=identity(payload):raise ValueError('evaluation identity differs')
    if request.get('purpose') not in PURPOSES:raise ValueError('evaluation purpose required')
    _validate_sources(request.get('evaluator_sources'))
    return request


def make_result(request, *, execution_status, numerical_status, screen_status, maturity='definition', metrics=None, constraints=None, diagnostics=None, confirmations=None):
    validate_request(request)
    value=dict(schema='osr-design-evaluation-result/1',evaluation_id=request['evaluation_id'],candidate_id=request['candidate_id'],requirement_revision=request['requirement_revision'],
        purpose=request['purpose'],request=deepcopy(request),execution_status=execution_status,numerical_status=numerical_status,screen_status=screen_status,maturity=maturity,
        metrics=deepcopy(metrics or {}),constraints=deepcopy(constraints or []),diagnostics=deepcopy(diagnostics or []),confirmation_evaluation_ids=list(confirmations or []),**FLAGS)
    value=json.loads(encoded(value));value['result_sha256']=identity(value)
    return validate_result(value)


def validate_result(value):
    if value.get('schema')!='osr-design-evaluation-result/1':raise ValueError('evaluation result required')
    if value.get('result_sha256')!=identity({key:item for key,item in value.items() if key!='result_sha256'}):raise ValueError('evaluation result payload digest differs')
    request=validate_request(value['request'])
    if any(value.get(key)!=request[key] for key in ('evaluation_id','candidate_id','requirement_revision','purpose')):raise ValueError('result/request binding differs')
    if value['execution_status'] not in EXECUTION or value['numerical_status'] not in NUMERICAL or value['screen_status'] not in SCREENS or value['maturity'] not in MATURITY:raise ValueError('typed states required')
    if value['screen_status']=='pass' and (value['execution_status']!='executed' or value['numerical_status']!='converged'):raise ValueError('unexecuted/nonconverged result cannot pass')
    if any(value.get(key) is not False for key in FLAGS):raise ValueError('numerical result cannot assert acceptance')
    encoded(value);return value
