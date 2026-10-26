"""V0.6 adapters with exact upstream evidence, tool identities and failure types."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from functools import lru_cache
import json,os,sys
from . import contracts as k,wheel_families
from engineering.station_rail import ROOT
IDS=('wheel-definition','wheel-body','wheel-motor','wheel-brakes','wheel-civil','wheel-system')
DEPENDENCIES={'wheel-definition':[],'wheel-body':['wheel-definition'],'wheel-motor':['wheel-definition'],
    'wheel-brakes':['wheel-definition'],'wheel-civil':['wheel-definition'],
    'wheel-system':['wheel-definition','wheel-body','wheel-motor','wheel-brakes','wheel-civil']}
PRODUCER='engineering/design_search/wheel_evaluators.py'


def catalogue():return [dict(id=n,dependencies=DEPENDENCIES[n],role='electrical' if n=='wheel-motor' else 'mechanical' if n=='wheel-body' else 'service',maximum_maturity='numerical-screen',physical_accepted=False,uses_current_candidate_stock=True,ideal_force_channel=False) for n in IDS]


def source_snapshot(name):
    if name not in IDS:raise ValueError('Registered wheel evaluator required')
    paths=[p for p in (Path(__file__).parent).glob('wheel*.py')]
    paths += [ROOT/'engineering/design_search/contracts.py',ROOT/'engineering/design_search/whole_system.py']
    paths += [ROOT/'engineering/station_rail'/n for n in ('vehicle.py','common.py','brief.toml','body_frame.py','body_solid_frame.py','body_floor_fit.py','station_motor.py','long_motor.py','braking.py','operations.py','civil.py','electrical.py')]
    result={p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
    for path,expected in wheel_families._base()['source_sha256'].items():
        actual=sha256((ROOT/path).read_bytes()).hexdigest()
        if actual!=expected or path in result and result[path]!=expected:raise ValueError('Cached base source differs: '+path)
        result[path]=expected
    return dict(sorted(result.items()))


@lru_cache(maxsize=16)
def _tool_digest(path,signature):return sha256(Path(path).read_bytes()).hexdigest()


def toolchain():
    import gmsh
    paths={'getdp':ROOT/'build/trip-dynamics/tools/getdp-3.5.0-Linux64/bin/getdp','calculix':Path('/usr/bin/ccx')}
    value=dict(gmsh=gmsh.__version__)
    for name,p in paths.items():
        stat=p.stat();value[name]=dict(binary_sha256=_tool_digest(str(p),(stat.st_size,stat.st_mtime_ns)),path=str(p))
    return value


def request_for(candidate,name,*,purpose='diagnostic',hypothesis=None,settings=None,scenario=None,mesh=None,environment=None):
    import numpy as np,platform
    env=dict(python=sys.version.split()[0],numpy=np.__version__,system=platform.system(),machine=platform.machine(),native_tools=toolchain())
    if environment is not None:
        if environment!=env:raise ValueError('Native tool/environment identity differs')
    value=deepcopy(settings or {});value['motor_evaluation']=deepcopy(candidate['evaluation_plan']['motor'])
    return k.make_evaluation_request(candidate,evaluator_id=name,evaluator_sources=source_snapshot(name),purpose=purpose,
        hypothesis=hypothesis or {},settings=value,scenario=scenario or {},mesh=mesh,environment=env)


def validate_dependencies(candidate,request):
    deps=request['settings'].get('dependency_results',{})
    if not isinstance(deps,dict) or set(deps)!=set(DEPENDENCIES[request['evaluator_id']]):raise ValueError('Exact dependency result inventory required')
    for name,result in deps.items():
        k.validate_result(result)
        if result['candidate_id']!=candidate['candidate_id'] or result['requirement_revision']!=candidate['requirement_revision'] or result['request']['evaluator_id']!=name:raise ValueError('Mixed dependency candidate or evaluator')
        if result['request']['evaluator_sources']!=source_snapshot(name):raise ValueError('Dependency sources differ')
        if result['execution_status'] not in ('executed','refused'):raise ValueError('Unfinished/error dependency cannot be consumed')
        if result['request']['environment']['native_tools']!=request['environment']['native_tools']:raise ValueError('Mixed dependency native tools')
    return deps


def failure(kind,reason,**extra):return dict(failure_class=kind,reason=reason,**extra)


def evaluate(candidate,request):
    k.validate_candidate(candidate);k.validate_request(request);deps=validate_dependencies(candidate,request)
    if request['evaluator_sources']!=source_snapshot(request['evaluator_id']):raise ValueError('Wheel method sources changed')
    if request['environment']['native_tools']!=toolchain():raise ValueError('Wheel native tool identity changed')
    car=wheel_families.materialize(candidate);params=wheel_families._parameters(candidate);name=request['evaluator_id']
    output=Path.cwd()/'native';diagnostics=[];constraints=[];metrics={};num='converged';screen='unknown'
    if name=='wheel-definition':
        props=k.inventory_summary(candidate);metrics=dict(known_vehicle_mass_kg=k.mass_properties(candidate)['known_mass_subtotal_kg'])
        constraints=[dict(id='same-stock-identity-and-account',state='pass'),dict(id='complete-installed-inventory',state='unknown')]
        diagnostics=[failure('evidence-gap','Unlocated reference accounts, joining hardware and supplier equipment prevent complete installed mass/CG/inertia',inventory=props)]
    elif name=='wheel-body':
        from . import wheel_body
        raw=wheel_body.evaluate(car,params['body'],output,root=ROOT,confirmation=False)
        invalid=(raw.get('execution') not in ('completed','executed') or any(c.get('force_balance_relative_error',1)>1e-4 for c in raw.get('cases',[])))
        num='invalid' if invalid else 'converged' if raw.get('numerical_validity')=='mesh_confirmed' else 'unknown'
        diagnostics=[failure('numerical-failure' if num!='converged' else 'design-failure' if raw.get('engineering_screen')=='fail' else 'evidence-gap','Candidate-specific native body result',native=raw)]
        screen='fail' if raw.get('engineering_screen')=='fail' else 'unknown'
        constraints=[dict(id='generated-frame-and-panel-stiffness',state=screen),dict(id='joint-strength-buckling-fatigue-modes',state='unknown')]
    elif name=='wheel-motor':
        from . import wheel_motor
        from engineering.station_rail import operations,braking
        rotor=braking.rotating_stock(car)['equivalent_inertial_mass_kg_per_car']
        profile=operations.profile(2000,car['mass']['accounted_cap_loaded_kg_per_car'],rotating_equivalent_mass_kg_per_car=rotor)
        raw=wheel_motor.evaluate(params['motor'],profile['peak_launch_force_N_per_car'],output,root=ROOT)
        invalid=any(r.get('numerical_validity')!='valid' for r in raw['cases'])
        outside=any(r.get('model_domain')=='outside_linear_material_hypothesis' for r in raw['cases'])
        num='invalid' if invalid or outside else 'converged'
        screen='fail' if raw['failure_reasons'] else 'unknown'
        kind='numerical-failure' if invalid else 'numerical-failure' if outside else 'design-failure' if screen=='fail' else 'evidence-gap'
        diagnostics=[failure(kind,'Native current-excited finite primary; no installed force map',native=raw)]
        constraints=[dict(id='force-field-current-voltage-necessary-screens',state=screen),dict(id='nonlinear-3D-thermal-entry-exit-map',state='unknown')]
    elif name=='wheel-brakes':
        from . import wheel_brakes
        raw=wheel_brakes.evaluate(car,params['brakes'],stopping_budget_m=request['scenario'].get('brake_stopping_budget_m',1000.))
        num='converged' if raw['model_valid'] else 'invalid';screen='fail' if any(c['necessary_stopping_screen']=='fail' for c in raw['cases']) else 'unknown'
        diagnostics=[failure('system-incompatibility' if c['case']=='adhesion-incompatible' else c['failure_class'],c['case'],native=c) for c in raw['cases']]
        constraints=[dict(id='declared-independent-stop-budget',state=screen),dict(id='supplier-fade-real-WSP-installation',state='unknown')]
    elif name=='wheel-civil':
        from engineering.station_rail import civil
        guide=params['guideway'];selected=car['selected_civil']
        rows=[civil.alternative(car,guide['span_m'],guide['family'],load,fixed_strands=selected['prestress_strands']) for load in ('empty','normal','crowd_control')]
        if selected['physical_civil_component_id']!=candidate['architecture']['selected_civil_id']:raise ValueError('Civil physical identity differs')
        screen='fail' if any(r['necessary_longitudinal_screen']=='fail' for r in rows) else 'unknown'
        diagnostics=[failure('design-failure' if screen=='fail' else 'evidence-gap','Same generated wheel loads drive the selected beam, piers and declared ground bounds',selected=selected,load_checks=rows)]
        constraints=[dict(id='fixed-physical-beam-moving-load-screen',state='fail' if screen=='fail' else 'pass'),dict(id='civil-site-fatigue-torsion-installed-cost',state='unknown')]
    elif name=='wheel-system':
        from . import whole_system
        response=whole_system.evaluate_wheel(candidate,car,params,deps,request);metrics=response['metrics'];constraints=response['constraints'];diagnostics=response['diagnostics'];num=response['numerical_status'];screen=response['screen_status']
    else:raise ValueError('Unknown wheel evaluator')
    if request['evaluator_sources']!=source_snapshot(name):raise ValueError('Wheel method changed during execution')
    return k.make_result(request,execution_status='executed',numerical_status=num,screen_status=screen,maturity='numerical-screen',
        metrics=metrics,constraints=constraints,diagnostics=diagnostics)
