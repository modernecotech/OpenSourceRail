"""Bounded nonlinear 2D screens; never a finite train or control qualification.

The field solver is the retained transverse PDE with its declared steel proxy.
The conservative comparison uses the smaller of two sampled air-contour lifts.
First-pass mesh/domain convergence remains unassessed, even for converged PDEs.
"""
from copy import deepcopy
from hashlib import sha256
import argparse
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from engineering.design_search.storage import atomic_immutable
from engineering.passive_suspension import fields
from . import candidates as catalogue

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "osr-halbach-scaling-transverse-screen/1"
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             configuration_adopted=False, installed_mass_complete=False,
             force_map_generated=False, hover_executed=False)
SETTINGS = dict(mesh_size_m=.006, outer_margin_m=.25, max_nodes=120000,
                steel_model="nonlinear_repo_proxy", check_convergence=False,
                nonlinear_max_iterations=100, nonlinear_relaxation=.35,
                nonlinear_tolerance=2e-4, max_solves=1)


def _write(path, value):
    return atomic_immutable(Path(path), catalogue.encoded(value))


def _hash(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def source_snapshot(root=ROOT):
    result = catalogue.source_snapshot(root)
    paths = [Path(__file__).resolve(), ROOT/'engineering/halbach_scaling/__init__.py',
             ROOT/'engineering/__init__.py']
    for path in paths:
        if path.is_file():
            if path.is_symlink():raise ValueError("ordinary screen sources required")
            result[path.relative_to(ROOT).as_posix()] = _hash(path)
    return dict(sorted(result.items()))


def _settings(settings):
    result = dict(SETTINGS)
    if settings:
        if set(settings)-{'mesh_size_m','outer_margin_m'}:
            raise ValueError("only bounded mesh/domain sensitivity overrides are supported")
        result.update(settings)
    if not .004 <= result['mesh_size_m'] <= .012 or not .15 <= result['outer_margin_m'] <= .4:
        raise ValueError("mesh/domain sensitivity outside declared bounds")
    return result


def _scenario(bundle, gap_m, temperature_C, currents_A):
    for value in (gap_m, temperature_C):
        if type(value) not in (float,int) or not math.isfinite(value):
            raise ValueError("finite gap and temperature required")
    if not .008 <= gap_m <= .060 or not 20 <= temperature_C <= 80:
        raise ValueError("outside exploratory 8..60 mm / 20..80 C domain")
    ids = {c['id'] for c in bundle['circuits']}
    currents = dict(currents_A or {})
    if set(currents)-ids:
        raise ValueError("undeclared control circuit")
    for key, value in currents.items():
        if type(value) not in (float,int) or not math.isfinite(value) or abs(value)>15:
            raise ValueError("authority current outside declared +/-15 A DC comparison")
    return dict(gap_m=float(gap_m), temperature_C=float(temperature_C),
                lateral_m=0., roll_rad=0., currents_A=currents,
                greater_gap_scope="Exploratory clearance only; stroke/platform/curve/capture interfaces are not accepted")


def _comparison(bundle, raw, scenario):
    grade = bundle['materials'][bundle['grade_id']]
    hlimit = grade['demag_hcj_fraction_limit']*grade['hcj_20c_a_m']*(
        1+grade['hcj_temperature_coefficient_per_k']*(scenario['temperature_C']-20))
    forces = raw['diagnostics']['contour_forces']
    if len(forces)!=2 or any(not math.isfinite(float(r[k])) for r in forces for k in ('F_z_N','F_y_N','M_x_Nm')):
        raise ValueError("two finite air-contour force/moment records required")
    lower = min(r['F_z_N'] for r in forces)
    current_density = {}
    losses20 = {};losses = {}
    alpha = fields.material_reference()['copper']['resistance_temperature_coefficient_per_k']
    for coil in bundle['circuits']:
        current = scenario['currents_A'].get(coil['id'],0.)
        current_density[coil['id']] = abs(current)/coil['conductor_area_m2']/1e6
        losses20[coil['id']] = current**2*coil['resistance_20c_ohm']
        losses[coil['id']] = losses20[coil['id']]*(1+alpha*(scenario['temperature_C']-20))
    converged = raw['numerical_status']=='converged'
    fill = max(bundle['winding_definition']['copper_fill_by_circuit'].values())
    ceiling = max(0.,24*lower/(1.3*9.80665)) if converged else None
    return dict(F_z_N=raw['F_z_N'],F_y_N=raw['F_y_N'],M_x_Nm=raw['M_x_Nm'],
        conservative_contour_Fz_N=lower if converged else None,
        reported_contour_Fz_N=[f['F_z_N'] for f in forces],
        own_counted_module_weight_N=bundle['stock']['train_known_mass_kg_per_module']*9.80665,
        counted_own_weight_screen_pass=converged and lower>=bundle['stock']['train_known_mass_kg_per_module']*9.80665,
        conditional_1_3_aw3_ceiling_kg_per_car=ceiling,
        conditional_aw3_ceiling_after_counted_support_kg=(None if ceiling is None else ceiling-bundle['stock']['train_known_mass_kg_per_car']),
        counted_support_stock_kg_per_car=bundle['stock']['train_known_mass_kg_per_car'],
        complete_installed_car_mass_kg=None,
        PM_H_parallel_min_A_per_m=raw['PM_H_parallel_min_A_per_m'],
        demag_proxy_limit_A_per_m=hlimit,
        demag_proxy_margin_A_per_m=raw['PM_H_parallel_min_A_per_m']+hlimit,
        demag_proxy_screen_pass=raw['PM_H_parallel_min_A_per_m']+hlimit>=0,
        steel_B_peak_T=raw['steel_B_peak_T'],steel_2p2T_screen_pass=raw['steel_B_peak_T']<=2.2,
        copper_fill=fill,copper_fill_screen_pass=fill<=.55,
        current_density_A_per_mm2=current_density,
        DC_current_density_screen_pass=all(j<=3.75+1e-12 for j in current_density.values()),
        copper_I2R_20C_W_by_circuit=losses20,
        copper_I2R_operating_C_W_by_circuit=losses,
        copper_I2R_20C_W_per_module=math.fsum(losses20.values()),
        copper_I2R_operating_C_W_per_module=math.fsum(losses.values()),
        copper_I2R_80C_W_per_module=math.fsum(losses20.values())*(1+alpha*60),
        numerical_status=raw['numerical_status'],
        air_contour_relative_difference=raw['diagnostics']['contour_relative_difference'],
        air_contour_check_pass=raw['diagnostics']['contour_check_pass'],
        mesh_domain_convergence_assessed=False,
        next_experiment_sample_screen_pass=(converged and raw['material_model_domain_pass']
            and raw['PM_H_parallel_min_A_per_m']+hlimit>=0
            and raw['steel_B_peak_T']<=2.2 and fill<=.55
            and all(j<=3.75+1e-12 for j in current_density.values())),
        continuous_cooling_W=None,thermal_equilibrium_C=None,
        force_control_authority_qualified=False,stable_hover_established=False,
        scope="Necessary counted-mass/static comparison only; infinite x, unvalidated steel proxy, no full map, installed fit, dynamics or thermal qualification",**FLAGS)


def evaluate_point(bundle, *, gap_m=.012, temperature_C=80., currents_A=None,
                   root=ROOT, settings=None):
    """Evaluate one point; caller must enforce its own process/runtime budget."""
    catalogue.validate(bundle,root)
    scenario = _scenario(bundle,gap_m,temperature_C,currents_A)
    cfg = _settings(settings);before = source_snapshot(root)
    geometry = catalogue.field_geometry(bundle,root)
    request = dict(candidate_id=bundle['physical_id'],bundle_sha256=bundle['bundle_sha256'],
                   geometry_id=fields._digest(geometry),scenario=scenario,settings=cfg,source_sha256=before)
    result = fields.solve(geometry,gap_m=scenario['gap_m'],temperature_C=scenario['temperature_C'],
                          currents_A=scenario['currents_A'],settings=cfg)
    if before!=source_snapshot(root):raise ValueError("screen sources changed during evaluation")
    return dict(schema=SCHEMA,evaluation_id=catalogue.identity(request),request=request,
                candidate_id=bundle['physical_id'],recipe_id=bundle['recipe_id'],
                execution_status="completed",numerical_status=result['numerical_status'],
                raw_result=result,comparison=_comparison(bundle,result,scenario),**FLAGS)


def _check_point(point, request, root):
    bundle=request['candidate'];catalogue.validate(bundle,root)
    geometry=catalogue.field_geometry(bundle,root);scenario=request['scenario'];cfg=request['settings']
    expected=dict(candidate_id=bundle['physical_id'],bundle_sha256=bundle['bundle_sha256'],
                  geometry_id=fields._digest(geometry),scenario=scenario,settings=cfg,
                  source_sha256=request['source_sha256'])
    if point.get('request')!=expected or point.get('evaluation_id')!=catalogue.identity(expected):
        raise ValueError("point evaluation input/source identity differs")
    raw=point['raw_result'];copy=deepcopy(raw);digest=copy.pop('result_id')
    if raw.get('schema')!=fields.SCHEMA or raw.get('physical_accepted') is not False or raw.get('material_correlated') is not False or raw.get('interpolation_usable') is not False:
        raise ValueError("raw first-pass field scope/acceptance differs")
    if raw['diagnostics'].get('validation_solves')!=1 or any(raw['diagnostics'].get(k)!='not_assessed' for k in ('mesh_check','boundary_check')):
        raise ValueError("raw first-pass convergence scope differs")
    if digest!=fields._digest(copy) or raw['geometry_id']!=expected['geometry_id']:
        raise ValueError("raw field result/geometry identity differs")
    operating={k:scenario[k] for k in ('gap_m','temperature_C','lateral_m','roll_rad','currents_A')}
    if raw['operating_point']!=operating or raw['settings']!=fields._settings(cfg):
        raise ValueError("raw field operating point/settings differ")
    if raw['source_sha256']!=fields.sources() or raw['steel_model']!='nonlinear_repo_proxy':
        raise ValueError("raw field implementation/material hypothesis differs")
    if raw['declared_material_definitions']!=geometry['materials']:
        raise ValueError("raw field material definition differs")
    if raw['F_z_N']!=raw['diagnostics']['contour_forces'][0]['F_z_N']:
        raise ValueError("reported force differs from its first air contour")
    if point.get('candidate_id')!=bundle['physical_id'] or point.get('recipe_id')!=bundle['recipe_id']:
        raise ValueError("point candidate linkage differs")
    if point.get('comparison')!=_comparison(bundle,raw,scenario) or point.get('numerical_status')!=raw['numerical_status']:
        raise ValueError("derived force/current/mass screen differs")
    if point.get('execution_status')!='completed' or any(point.get(k) is not v for k,v in FLAGS.items()):
        raise ValueError("point disposition/acceptance flags differ")
    return point


def validate_point(point,bundle,root=ROOT):
    """Public strict read-back guard for a retained single-point evaluation."""
    request=point.get('request',{})
    if point.get('schema')!=SCHEMA or request.get('source_sha256')!=source_snapshot(root):
        raise ValueError("point schema/current source snapshot differs")
    original=request['scenario']
    scenario=_scenario(bundle,original['gap_m'],original['temperature_C'],original['currents_A'])
    cfg=request['settings'];expected=_settings({k:cfg[k] for k in ('mesh_size_m','outer_margin_m')})
    if cfg!=expected or original!=scenario:raise ValueError("point scenario or fixed nonlinear settings differ")
    return _check_point(point,dict(candidate=bundle,scenario=scenario,settings=cfg,
                                  source_sha256=request['source_sha256']),root)


def _inventory(output):
    result={}
    for path in sorted(Path(output).rglob('*')):
        if path.is_symlink():raise ValueError("ordinary immutable run files required")
        if path.is_file() and path.name!='manifest.json':result[path.relative_to(output).as_posix()]=_hash(path)
    return result


def _terminate(process):
    try:os.killpg(process.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    process.wait(timeout=5)


def _execute(directory,request,root,seconds):
    directory.mkdir();_write(directory/'input.json',request)
    if seconds<=0:
        return dict(execution_status='not-run',numerical_status='unknown',
                    error='Whole campaign wall-clock budget exhausted',candidate_id=request['candidate']['physical_id'],**FLAGS)
    command=[sys.executable,'-m','engineering.halbach_scaling.screen','--worker',str(directory/'input.json'),'--output',str(directory/'point.json')]
    started=time.monotonic();env=dict(os.environ,PYTHONPATH=str(ROOT)+os.pathsep+str(Path(root).resolve()),OSR_HALBACH_SOURCE_ROOT=str(Path(root).resolve()),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    with (directory/'stdout.log').open('wb') as stdout,(directory/'stderr.log').open('wb') as stderr:
        process=subprocess.Popen(command,cwd=ROOT,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
        try:code=process.wait(timeout=seconds);timed_out=False
        except subprocess.TimeoutExpired:_terminate(process);code=process.returncode;timed_out=True
    execution=dict(command=command,returncode=code,timed_out=timed_out,elapsed_s=time.monotonic()-started,deadline_s=seconds)
    _write(directory/'execution.json',execution)
    if code==0 and not timed_out and (directory/'point.json').is_file():
        try:return dict(_check_point(json.loads((directory/'point.json').read_bytes()),request,root),execution=execution)
        except (ValueError,KeyError,TypeError) as error:return dict(execution_status='failed',numerical_status='unknown',error=str(error),execution=execution,candidate_id=request['candidate']['physical_id'],**FLAGS)
    return dict(execution_status='interrupted' if timed_out else 'failed',numerical_status='unknown',
        error='Wall-clock deadline' if timed_out else 'Numerical worker failed',execution=execution,
        candidate_id=request['candidate']['physical_id'],**FLAGS)


def run(output,root=ROOT,candidates=None):
    """At most 36 nominal plus four extra authority solves, with a 900 s cap."""
    root=Path(root).resolve();output=Path(output).absolute()
    values=catalogue.candidates(root) if candidates is None else list(candidates)
    if not 1<=len(values)<=36 or len({v['physical_id'] for v in values})!=len(values):
        raise ValueError("one to thirty-six unique declared proposals required")
    for value in values:catalogue.validate(value,root)
    before=source_snapshot(root)
    if output.is_symlink() or any(p.is_symlink() for p in output.parents):raise ValueError("ordinary fresh run directory required")
    output.mkdir(parents=True,exist_ok=False)
    authority=[v for v in values if v['winding_definition']['layout']=='differential' and v['parameters']['magnet_volume_m3'] in (.012,.024)]
    request=dict(schema=SCHEMA,candidates=values,authority_candidate_ids=[v['physical_id'] for v in authority],
        source_sha256=before,settings=SETTINGS,root=str(root),
        budget=dict(max_geometries=36,max_field_solves=42,seconds_per_trial=300,whole_campaign_seconds=900,numerical_workers=1),**FLAGS)
    request['request_id']=catalogue.identity(request);_write(output/'request.json',request)
    started=time.monotonic();rows=[];extra=[]
    def point(value,current,directory):
        scenario=_scenario(value,.012,80.,{} if current==0 else {c['id']:current for c in value['circuits']})
        r=dict(candidate=value,scenario=scenario,settings=SETTINGS,source_sha256=before)
        return _execute(output/directory,r,root,min(300,max(0,900-(time.monotonic()-started))))
    for number,value in enumerate(values):
        row=point(value,0,f'nominal-{number:02d}');row['case']=f'nominal-{number:02d}';rows.append(row)
    for value in authority:
        base=next(row for row in rows if row['candidate_id']==value['physical_id'])
        for current in (-15.,0.,15.):
            label=f"authority-{len(extra):02d}"
            if current==0:
                row=dict(base);row['reused_nominal_zero_current']=True
            else:
                row=point(value,current,label);row['reused_nominal_zero_current']=False
            row['case']=label;row['common_current_A']=current;extra.append(row)
    if source_snapshot(root)!=before:raise ValueError("sources changed during bounded screen")
    result=dict(schema=SCHEMA,request_id=request['request_id'],source_sha256=before,
        rows=rows,authority_rows=extra,
        counts=_counts(values,rows,extra),
        scope='Transverse static/authority screening only. No complete mass, equilibrium, guidance, dynamic stability, cooling, 3D or physical acceptance.',**FLAGS)
    result['screen_id']=catalogue.identity(result);_write(output/'result.json',result)
    _write(output/'manifest.json',dict(schema=SCHEMA,request_id=request['request_id'],source_sha256=before,files_sha256=_inventory(output),**FLAGS))
    verify(output,root);return result


def verify(output,root=ROOT):
    """Check bytes, identities and derived screens; does not repeat a PDE solve."""
    output=Path(output);request=json.loads((output/'request.json').read_bytes());result=json.loads((output/'result.json').read_bytes());manifest=json.loads((output/'manifest.json').read_bytes())
    if request['request_id']!=catalogue.identity({k:v for k,v in request.items() if k!='request_id'}):raise ValueError("screen request identity differs")
    if manifest['files_sha256']!=_inventory(output) or manifest['source_sha256']!=source_snapshot(root) or request['source_sha256']!=source_snapshot(root):raise ValueError("screen source/payload inventory differs")
    if result['source_sha256']!=request['source_sha256'] or result['request_id']!=request['request_id'] or manifest['request_id']!=request['request_id'] or result['screen_id']!=catalogue.identity({k:v for k,v in result.items() if k!='screen_id'}):raise ValueError("screen result linkage differs")
    for record in (request,result,manifest):
        if record.get('schema')!=SCHEMA or any(record.get(k) is not v for k,v in FLAGS.items()):raise ValueError("screen scope/acceptance differs")
    values=request['candidates']
    if not 1<=len(values)<=36 or len({v['physical_id'] for v in values})!=len(values):raise ValueError("bounded unique physical proposals required")
    for value in values:catalogue.validate(value,root)
    if len(result['rows'])!=len(values):raise ValueError("nominal result inventory differs")
    for number,(row,value) in enumerate(zip(result['rows'],values)):
        directory=output/f'nominal-{number:02d}';entry=json.loads((directory/'input.json').read_bytes())
        if entry!=dict(candidate=value,scenario=_scenario(value,.012,80.,{}),settings=SETTINGS,source_sha256=request['source_sha256']):raise ValueError("nominal input differs")
        if row['candidate_id']!=value['physical_id'] or row['case']!=directory.name:raise ValueError("nominal membership differs")
        if row['execution_status']=='completed':
            point=json.loads((directory/'point.json').read_bytes());_check_point(point,entry,root)
            if row!={**point,'execution':json.loads((directory/'execution.json').read_bytes()),'case':directory.name}:raise ValueError("nominal derived point differs")
        elif row.get('comparison') or row.get('numerical_status')!='unknown':raise ValueError("failed/unexecuted point cannot receive force credit")
    authority=[v for v in values if v['winding_definition']['layout']=='differential' and v['parameters']['magnet_volume_m3'] in (.012,.024)]
    if request['authority_candidate_ids']!=[v['physical_id'] for v in authority] or len(result['authority_rows'])!=3*len(authority):raise ValueError("authority inventory differs")
    for index,row in enumerate(result['authority_rows']):
        value=authority[index//3];current=(-15.,0.,15.)[index%3]
        if row['case']!=f'authority-{index:02d}' or row['candidate_id']!=value['physical_id'] or row['common_current_A']!=current:raise ValueError("authority membership differs")
        if current==0:
            original=next(r for r in result['rows'] if r['candidate_id']==value['physical_id'])
            expected={**original,'case':row['case'],'common_current_A':0.,'reused_nominal_zero_current':True}
            if row!=expected:raise ValueError("zero-current reuse differs")
        else:
            directory=output/row['case'];entry=json.loads((directory/'input.json').read_bytes())
            if entry!=dict(candidate=value,scenario=_scenario(value,.012,80.,{c['id']:current for c in value['circuits']}),settings=SETTINGS,source_sha256=request['source_sha256']):raise ValueError("authority input differs")
            if row['execution_status']=='completed':
                point=json.loads((directory/'point.json').read_bytes());_check_point(point,entry,root)
                expected={**point,'execution':json.loads((directory/'execution.json').read_bytes()),'case':row['case'],'common_current_A':current,'reused_nominal_zero_current':False}
                if row!=expected:raise ValueError("authority derived point differs")
            elif row.get('comparison') or row.get('numerical_status')!='unknown':raise ValueError("failed authority cannot receive force credit")
    if request['budget']!=dict(max_geometries=36,max_field_solves=42,seconds_per_trial=300,whole_campaign_seconds=900,numerical_workers=1) or request['settings']!=SETTINGS:raise ValueError("screen budget/model contract differs")
    if result['counts']!=_counts(values,result['rows'],result['authority_rows']):raise ValueError("recomputed screen counts differ")
    return dict(current=True,screen_id=result['screen_id'],counts=result['counts'],scope='Byte/input/derived-screen verification; no repeated PDE solve',**FLAGS)


def _counts(values,rows,extra):
    return dict(physical_geometries=len(values),nominal_records=len(rows),authority_records=len(extra),
                reused_zero_current_records=sum(r.get('reused_nominal_zero_current',False) for r in extra),
                field_solves_started=sum('execution' in r for r in rows)+sum('execution'in r and not r.get('reused_nominal_zero_current') for r in extra),
                numerical_nominal_converged=sum(r.get('numerical_status')=='converged' for r in rows))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--worker',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    request=json.loads(args.worker.read_bytes());root=Path(os.environ.get('OSR_HALBACH_SOURCE_ROOT',ROOT))
    if request['source_sha256']!=source_snapshot(root):raise ValueError("worker source snapshot differs")
    scenario=request['scenario'];point=evaluate_point(request['candidate'],gap_m=scenario['gap_m'],temperature_C=scenario['temperature_C'],currents_A=scenario['currents_A'],settings={k:request['settings'][k] for k in ('mesh_size_m','outer_margin_m')},root=root)
    _check_point(point,request,root);_write(args.output,point)
    print(json.dumps(dict(candidate_id=point['candidate_id'],execution_status=point['execution_status'],numerical_status=point['numerical_status'])),flush=True)


if __name__=='__main__':main()
