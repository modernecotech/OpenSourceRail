"""Selected-car equilibrium diagnostics and new bounded PM/steel 3D experiments.

A force-curve crossing is a next experiment, never stable hover. The native
scalar-potential kernel has no free-current source: current authority retained
below is explicitly transverse research and is not mixed into the native map.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse
import json
import math
import os
import signal
import subprocess
import sys
import tarfile
import time

from engineering.development_baseline import selection
from engineering.comfort_options import systems
from engineering.comfort_design import interfaces
from engineering.halbach_scaling import finite
from engineering.magnetic_confirmation import analysis
from engineering.suspension_closure import study
from engineering.vehicle_optimisation import magnets

ROOT=Path(__file__).resolve().parents[2]
SCHEMA='osr-selected-support-operating-point/1'
ARCHIVE='docs/design-engine/ferrite-maglev/engineering-readiness/suspension-artifacts.tar.gz'
CODE='engineering/suspension_closure/operating_point.py'
TEST='engineering/suspension_closure/tests/test_operating_point.py'
G=9.80665
FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
           stable_hover_established=False,installed_mass_complete=False,force_map_generated=False,
           operating_release=False,manufacturing_release=False)
SETTINGS=dict(margin_m=.15,near_mesh_size_m=.036,gap_mesh_size_m=.012)
MEDIUM=dict(margin_m=.15,near_mesh_size_m=.032,gap_mesh_size_m=.010)
COUNTS=(128,48,24)


def encoded(value):return selection.encoded(value)
def identity(value):return selection.identity(value)
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def write(path,value):
    path=Path(path)
    if path.exists():raise ValueError('immutable output already exists: '+str(path))
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(encoded(value))


def state(gap_m,temperature_C=80.,facing_thickness_m=.035,currents_A=None):
    for v in (gap_m,temperature_C,facing_thickness_m):
        if type(v) not in (float,int) or not math.isfinite(v):raise ValueError('finite operating state required')
    if not .008<=gap_m<=.060 or not 20<=temperature_C<=80:
        raise ValueError('outside 8–60mm/20–80C evaluation domain')
    if facing_thickness_m not in (.020,.035):raise ValueError('explicit20/35mm facing comparison required')
    if currents_A not in (None,{}):raise ValueError('scalar-potential native kernel has no free-current winding source')
    return dict(gap_m=float(gap_m),temperature_C=float(temperature_C),
                facing_thickness_m=float(facing_thickness_m),currents_A={},
                lateral_m=0.,rotation_rad=[0.,0.,0.])


def specifications():
    return [dict(case=name,state=state(gap,temp,thick),settings=dict(mesh)) for name,gap,temp,thick,mesh in (
        ('reference-80C-40mm',.040,80.,.035,SETTINGS),
        ('reference-80C-50mm',.050,80.,.035,SETTINGS),
        ('thin-facing-80C-40mm',.040,80.,.020,SETTINGS),
        ('reference-20C-40mm',.040,20.,.035,SETTINGS))]


def _member(path,name):
    with tarfile.open(path) as archive:
        matches=[m for m in archive.getmembers() if m.name==name]
        if len(matches)!=1 or not matches[0].isfile() or matches[0].size>32*1024*1024:
            raise ValueError('one bounded ordinary evidence member required')
        return archive.extractfile(matches[0]).read()


def context(root=ROOT):
    root=Path(root).resolve();selected=selection.load(root);car=selected['vehicle']
    item=study.candidates(root)[0]
    if item['component_id']!=car['magnet_component_id'] or car['candidate_id']!=selected['selection']['vehicle_candidate_id']:
        raise ValueError('selected vehicle and exact magnetic component differ')
    parent=systems.parent_evidence(root);thermal=interfaces.thermal_evidence(root)
    raw=_member(root/ARCHIVE,'suspension/result.json');receipt=json.loads(_member(root/ARCHIVE,'suspension/manifest.json'))
    if sha256(raw).hexdigest()!=receipt['files_sha256']['result.json']:raise ValueError('retained transverse payload differs')
    suspension=json.loads(raw)
    for name,expected in suspension['source_sha256'].items():
        if digest(root/name)!=expected:raise ValueError('retained transverse source differs: '+name)
    comparison=next(c for c in suspension['comparisons'] if c['candidate_id']==item['component_id'])
    source=finite.source_snapshot(root)
    for record in (selected,car,parent,thermal,suspension):
        for name,h in record.get('source_sha256',{}).items():
            if name in source and source[name]!=h:raise ValueError('mixed retained source revisions: '+name)
            source[name]=h
    source[ARCHIVE]=digest(root/ARCHIVE)
    return dict(selection_id=selected['selection_id'],vehicle_candidate_id=car['candidate_id'],
        body_candidate_id=car['body_candidate_id'],magnet_component_id=item['component_id'],
        accounted_tare_kg_per_car=car['mass']['accounted_tare_kg_per_car'],
        installed_mass_kg_per_car=None,modules_per_car=24,cars=6,passenger_mass_kg=75.,
        retained_native_samples=parent['samples'],retained_transverse=comparison,
        retained_common_current=thermal['support_winding'],component=item['value'],
        source_sha256=dict(sorted(source.items())),**FLAGS)


def sources(ctx,root):
    result=dict(ctx['source_sha256']);root=Path(root)
    for name in (CODE,TEST):
        path=Path(__file__) if name==CODE else Path(__file__).parent/'tests/test_operating_point.py'
        if path.is_symlink() or path.read_bytes()!=(root/name).read_bytes():
            raise ValueError('executing producer differs from source root: '+name)
        result[name]=digest(path)
    return dict(sorted(result.items()))


def loads(ctx):
    result=[]
    for label,n in [('empty',0),('normal-46',46),('crowd-control-160',160)]:
        mass=ctx['accounted_tare_kg_per_car']+n*ctx['passenger_mass_kg']
        result.append(dict(case=label,passengers_per_car=n,accounted_mass_kg_per_car=mass,
            mean_weight_N_per_module=mass*G/ctx['modules_per_car'],
            reserve_1_3_force_N_per_module=1.3*mass*G/ctx['modules_per_car'],
            six_car_passenger_mass_kg=n*ctx['passenger_mass_kg']*ctx['cars'],
            actual_module_load_distribution_known=False,**FLAGS))
    return result


def crossings(points,target):
    """All piecewise-linear crossings. No extrapolation, smoothing or uniqueness assumption."""
    if not math.isfinite(target) or target<=0:raise ValueError('positive finite force target required')
    if len(points)<2:return dict(status='insufficient-samples',crossings=[],extrapolated=False)
    points=sorted(points)
    if any(not all(math.isfinite(v) for v in pair) for pair in points) or any(a[0]>=b[0] for a,b in zip(points,points[1:])):
        raise ValueError('unique finite ordered gaps required')
    roots=[]
    for (a,fa),(b,fb) in zip(points,points[1:]):
        if fa==fb==target:
            roots.append(dict(gap_bracket_m=[a,b],linear_estimate_gap_m=None,secant_dFz_dgap_N_m=0.,continuum=True))
        elif (fa-target)*(fb-target)<=0 and fa!=fb:
            x=a+(target-fa)*(b-a)/(fb-fa)
            if not any(r['linear_estimate_gap_m'] is not None and abs(r['linear_estimate_gap_m']-x)<1e-12 for r in roots):
                roots.append(dict(gap_bracket_m=[a,b],linear_estimate_gap_m=x,
                    secant_dFz_dgap_N_m=(fb-fa)/(b-a),continuum=False))
    return dict(status='sampled-crossing' if roots else 'outside-sampled-force-range',crossings=roots,
        extrapolated=False,local_derivative_qualified=False,equilibrium_solved=False,
        sampled_force_is_a_confidence_bound=False,scope='Secant next-experiment estimate, not an equilibrium solution or stable hover')


def curve_diagnostics(ctx,native_rows=()):
    samples=[dict(s,source_kind='retained-native') for s in ctx['retained_native_samples']]
    for row in native_rows:
        if row.get('execution_status')=='completed' and row['point'].get('force_credit'):
            p=row['point'];s=p['state']
            if s['facing_thickness_m']==.035 and p['settings']==SETTINGS:
                samples.append(dict(sample_id=p['state_id'],gap_m=s['gap_m'],temperature_C=s['temperature_C'],
                    contour_Fz_N=[r['force_N'][2] for r in p['analysis']['air_contour_results']],
                    source_kind='new-native',numerical_force_convergence_established=False))
    results=[]
    for temp in (20.,80.):
        subset=[s for s in samples if s['temperature_C']==temp]
        for load in loads(ctx):
            estimates=[]
            for contour in range(2):
                points=[(s['gap_m'],s['contour_Fz_N'][contour]) for s in subset]
                diagnostic=crossings(points,load['mean_weight_N_per_module'])
                for root in diagnostic['crossings']:
                    mass=load['accounted_mass_kg_per_car']/24
                    root['uncoupled_uncontrolled_growth_rate_per_s_diagnostic']=math.sqrt(max(0.,-root['secant_dFz_dgap_N_m'])/mass)
                estimates.append(dict(contour=contour,**diagnostic))
            results.append(dict(temperature_C=temp,load=load,samples=subset,contours=estimates,
                minimum_required_installed_current_map=None,operating_gap_selected=False,**FLAGS))
    return results


def current_diagnostics(ctx):
    value=ctx['retained_common_current']
    if value['candidate_id']!=ctx['magnet_component_id']:raise ValueError('current data belongs to another magnetic component')
    result=[]
    for sample in value['samples']:
        if sample['candidate_id']!=ctx['magnet_component_id'] or sample['temperature_C']!=80.:
            raise ValueError('retained current state/component differs')
        I=sample['common_currents_A'];forces=sample['conservative_Fz_N']
        if len(I)!=3 or I!=[-15.,0.,15.] or len(forces)!=3:raise ValueError('exact retained three-point current source required')
        for load in loads(ctx):
            curve=crossings(list(zip(I,forces)),load['mean_weight_N_per_module'])
            diagnostic=deepcopy(curve)
            for root in diagnostic['crossings']:
                root['sampled_current_bracket_A']=root.pop('gap_bracket_m')
                root['linear_estimate_common_current_A']=root.pop('linear_estimate_gap_m')
                root['secant_dFz_dcommon_current_N_A']=root.pop('secant_dFz_dgap_N_m')
                i=root['linear_estimate_common_current_A']
                root['known_copper_DC_loss_W_per_module_diagnostic']=None if i is None else i*i*value['R80_known_copper_ohm_per_module']
            result.append(dict(gap_m=sample['gap_m'],temperature_C=80.,load=load,
                common_connection={'array-left-control':1,'array-right-control':1},
                sampled_currents_A=I,sampled_Fz_N=forces,diagnostic=diagnostic,
                native_3D_current_authority_N=None,actual_current_selected=False,
                scope='Retained2D transverse force/current samples only; no 3D force credit, RMS duty or control qualification',**FLAGS))
    actuator=[]
    for temp in ctx['retained_transverse']['temperatures']:
        derivative=temp['derivative_diagnostics'];gap=derivative.get('gap',{}).get('Fz',[])
        current=derivative.get('current',{}).get('Fz',[])
        rows=[]
        for kz,ki in zip(gap,current):
            rows.append(dict(dFz_dgap_N_per_m=kz,dFz_dcommon_current_N_per_A=ki,
                current_to_cancel_1mm_gap_change_A_diagnostic=None if abs(ki)<1e-12 else .001*abs(kz/ki),
                gap_error_using_all_15A_common_authority_m_diagnostic=None if abs(kz)<1e-12 else 15*abs(ki/kz)))
        actuator.append(dict(temperature_C=temp['temperature_C'],gap_m=.035338,
            common_current_diagnostics=rows,transverse_derivatives=derivative,
            opposed_30A_secant=temp.get('opposed_30A_secant'),
            local_series_RL_diagnostic=temp.get('local_series_RL_diagnostic'),
            scope='Retained2D35.338mm state, recalculated requirements; no transfer to another gap or finite3D map',**FLAGS))
    return dict(common=result,retained_35_338mm_transverse_diagnostics=actuator,
        actual_common_and_differential_3D_authority=None,full_vehicle_control_rank=None,
        redesigned_coil_contract=dict(
            physical_channels_per_module=2,channels_independently_current_regulated=True,
            common_connection={'array-left-control':1,'array-right-control':1},
            opposed_connection={'array-left-control':1,'array-right-control':-1},
            declared_current_domain_A=[-15.,15.],maximum_current_density_A_per_mm2=3.75,
            conductor_cross_section_mm2=4.,turns_each=60,
            required_3D_solver='Vector potential/edge elements with gauge or verified source-field plus scalar-reaction formulation',
            required_winding_geometry='Two closed divergence-free current paths including finite end returns, leads and exactamp-turn counts',
            bench_fixture='Analytical closed rectangular-loop field and force/flux reciprocity, then steel/PM benchmark and mesh/domain refinement',
            force_current_rank_and_dynamic_voltage_reserve=None,required_gain_margin_phase_margin=None,
            measured_RMS_duty_and_heat_rejection=None),**FLAGS)



def physical_interface(component,thickness):
    if component['physical_id']!=systems.MAGNET_ID or identity(magnets.physical_definition(component))!=component['physical_id']:
        raise ValueError('exact selected PM/steel source required')
    value=deepcopy(component)
    if thickness==.035:return value
    if thickness!=.020:raise ValueError('declared20mm interface only')
    region=next(r for r in value['regions'] if r['id']=='guideway/facing');region['bounds_yz_m'][3]=thickness
    i=next(i for i,p in enumerate(value['stock_parts']) if p['id']=='guideway/facing');p=value['stock_parts'][i]
    value['stock_parts'][i]=magnets._box(p['id'],[1.,.5,thickness],[-.5,-.25,0.],p['material'],p['density_kg_m3'],p['group'],p['role'])
    value['physical_id']=identity(magnets.physical_definition(value));value['candidate_id']=value['physical_id']
    value['stock']['facing_mass_kg_per_m_per_bank']=value['stock_parts'][i]['mass_kg']
    value['interface']['facing_thickness_m']=thickness
    value['bundle_sha256']=identity({k:v for k,v in value.items() if k!='bundle_sha256'})
    return value


def effective_value(component,s):
    """Rebase the fixed80C kernel to the requested linear recoil material state.

    Input material tables and physical IDs are preserved separately. The runtime
    clone carries Br(T),HcJ(T) as its reference and zero temperature coefficients,
    so the old kernel's *60 multiplication is exactly unity, not a force scaling.
    The nonlinear steel problem is freshly solved at each actual temperature.
    """
    if s!=state(s['gap_m'],s['temperature_C'],s['facing_thickness_m'],s['currents_A']):raise ValueError('state differs')
    value=finite.pose(physical_interface(component,s['facing_thickness_m']),s['gap_m'])
    grade=value['materials'][value['grade_id']];T=s['temperature_C']
    br_factor=1+(T-20)*grade['br_temperature_coefficient_per_k']
    hcj=(grade['hcj_20c_a_m']-grade.get('hcj_tolerance_a_m',0.))*(1+(T-20)*grade['hcj_temperature_coefficient_per_k'])
    original=deepcopy(grade)
    for region in value['regions']:
        if region['material']==value['grade_id']:
            region['Br_y_T']*=br_factor;region['Br_z_T']*=br_factor
    grade.update(br_20c_t=grade['br_20c_t']*br_factor,br_temperature_coefficient_per_k=0.,
        hcj_20c_a_m=hcj,hcj_temperature_coefficient_per_k=0.,hcj_tolerance_a_m=0.)
    value['evaluation_state_id']=identity(dict(local_interface_candidate_id=value['physical_id'],state=s))
    value['effective_material_rebase']=dict(temperature_C=T,source_grade=original,Br_factor=br_factor,
        physical_material_definition_unchanged=True,kernel_reference_is_effective_temperature=True)
    return value


def _derived(directory,request,row):
    d=Path(directory);value=effective_value(request['component'],request['spec']['state']);mesh=row['mesh'];spec=request['spec']
    expected=dict(case=spec['case'],state=spec['state'],state_id=value['evaluation_state_id'],
        local_interface_candidate_id=value['physical_id'],magnet_component_id=request['component']['physical_id'],
        settings=spec['settings'],coil_current_source_modelled=False,**FLAGS)
    if any(row.get(k)!=v for k,v in expected.items()):raise ValueError('native state/interface identity differs')
    command=[request['getdp']['path'],'coupon.pro','-msh','coupon.msh','-solve','Solve','-pos','Results']
    if row['solver_command']!=command:raise ValueError('native solver command differs')
    guard=finite.validate_mesh(d/'coupon.msh',mesh,value,spec['settings']);boxes=finite.contours(value)
    if read(d/'effective-input.json')!=value or (d/'coupon.pro').read_text()!=finite.formulation(value,mesh,boxes,COUNTS):
        raise ValueError('native executed material/formulation differs')
    parsed=analysis.parse_stages((d/'getdp.stdout.log').read_text())
    result=dict(row,mesh_verification=guard,continuation=parsed,
        force_credit=row['solver_returncode']==0 and parsed['full_source_converged'])
    result['numerical_validity']='PDE-converged-force-unconverged' if result['force_credit'] else 'nonconverged'
    if result['force_credit']:result['analysis']=finite.analyze(d,value,mesh,boxes,COUNTS)
    else:result.pop('analysis',None)
    return result


def worker(request,directory):
    d=Path(directory);s=request['spec'];value=effective_value(request['component'],s['state'])
    write(d/'effective-input.json',value);mesh=finite.mesh_case(value,d,s['settings']);boxes=finite.contours(value)
    (d/'coupon.pro').write_text(finite.formulation(value,mesh,boxes,COUNTS))
    command=[request['getdp']['path'],'coupon.pro','-msh','coupon.msh','-solve','Solve','-pos','Results']
    with (d/'getdp.stdout.log').open('wb') as out,(d/'getdp.stderr.log').open('wb') as err:
        code=subprocess.run(command,cwd=d,stdout=out,stderr=err).returncode
    row=dict(case=s['case'],state=s['state'],state_id=value['evaluation_state_id'],
        magnet_component_id=request['component']['physical_id'],local_interface_candidate_id=value['physical_id'],
        settings=s['settings'],mesh=mesh,solver_returncode=code,solver_command=command,
        coil_current_source_modelled=False,**FLAGS)
    write(d/'point.json',_derived(d,request,row))


def _stop(p):
    try:os.killpg(p.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    p.wait(timeout=5)


def run(output,root=ROOT,getdp=None,seconds_total=600.,seconds_per_case=150.):
    root=Path(root).resolve();output=Path(output).resolve()
    if not 0<seconds_total<=600 or not 0<seconds_per_case<=180:raise ValueError('bounded600s/180s campaign required')
    if output.exists() or output.is_symlink():raise ValueError('fresh ordinary campaign directory required')
    ctx=context(root);before=sources(ctx,root);tool=finite.previous._tool(getdp)
    request=dict(schema=SCHEMA,selection_id=ctx['selection_id'],source_sha256=before,
        vehicle_candidate_id=ctx['vehicle_candidate_id'],body_candidate_id=ctx['body_candidate_id'],
        magnet_component_id=ctx['magnet_component_id'],component=ctx['component'],specifications=specifications(),
        getdp=tool,root=str(root),budget=dict(seconds_total=seconds_total,seconds_per_case=seconds_per_case,numerical_workers=1),**FLAGS)
    request['request_id']=identity(request);output.mkdir(parents=True);write(output/'request.json',request)
    rows=[];start=time.monotonic();code_root=Path(__file__).resolve().parents[2]
    for spec in specifications():
        d=output/spec['case'];d.mkdir();per=dict(schema=SCHEMA,component=ctx['component'],spec=spec,getdp=tool,source_sha256=before)
        write(d/'input.json',per);remaining=seconds_total-(time.monotonic()-start)
        row=dict(case=spec['case'],execution_status='not-run',specification=spec,**FLAGS)
        if remaining>1:
            command=[sys.executable,'-m','engineering.suspension_closure.operating_point','worker','--input',str(d/'input.json'),'--output',str(d)]
            env=dict(os.environ,PYTHONPATH=str(code_root)+os.pathsep+str(root),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
            duration=min(seconds_per_case,remaining);t=time.monotonic()
            with (d/'worker.stdout.log').open('wb') as out,(d/'worker.stderr.log').open('wb') as err:
                p=subprocess.Popen(command,cwd=code_root,env=env,stdout=out,stderr=err,start_new_session=True)
                try:code=p.wait(timeout=duration);timeout=False
                except subprocess.TimeoutExpired:_stop(p);code=p.returncode;timeout=True
            row['execution']=dict(returncode=code,timed_out=timeout,elapsed_s=time.monotonic()-t,deadline_s=duration)
            row['execution_status']='interrupted' if timeout else 'tool-error'
            if code==0 and not timeout and (d/'point.json').is_file():
                point=read(d/'point.json');row.update(execution_status='completed',point=_derived(d,per,point))
        rows.append(row)
    if sources(context(root),root)!=before:raise ValueError('campaign source changed during execution')
    result=dict(schema=SCHEMA,request_id=request['request_id'],selection_id=ctx['selection_id'],
        vehicle_candidate_id=ctx['vehicle_candidate_id'],body_candidate_id=ctx['body_candidate_id'],
        magnet_component_id=ctx['magnet_component_id'],execution='completed',native_rows=rows,
        load_cases=loads(ctx),retained_native_samples=ctx['retained_native_samples'],
        equilibrium_diagnostics=curve_diagnostics(ctx,rows),current_diagnostics=current_diagnostics(ctx),
        maturity_by_subsystem=dict(vertical='analytical',lateral='analytical',roll='concept',pitch='concept',yaw='concept',
            current_authority='analytical',thermal_duty='analytical',coupled_hover='concept'),
        engineering_screen='unknown',native_scalar_potential_has_current_source=False,
        actual_installed_equilibrium=None,actual_stability=None,
        next_required_experiments=['Mesh/domain/air-contour convergence at each equilibrium neighborhood',
            'Vector-potential or magnetic-circuit cohomology winding-current model, benchmarked against controlled coil fixture',
            'Six force/moment outputs against gap,lateral,roll,pitch,yaw,common/opposed currents and temperature',
            'Same installed steel supports/rebar,joints,multiple modules and complete equipped CG/inertia',
            'Coupled current/thermal/flexible-body hover,fault and journey tests'],source_sha256=before,**FLAGS)
    result['evaluation_id']=identity(result);write(output/'result.json',result)
    manifest=dict(schema=SCHEMA,request_id=request['request_id'],evaluation_id=result['evaluation_id'],
        source_sha256=before,files_sha256=finite.inventory(output,('manifest.json',)),**FLAGS)
    write(output/'manifest.json',manifest);verify(output,root);return result


def verify(output,root=ROOT):
    output=Path(output);root=Path(root);r=read(output/'request.json');m=read(output/'manifest.json');v=read(output/'result.json');ctx=context(root)
    if r['request_id']!=identity({k:x for k,x in r.items() if k!='request_id'}) or v['evaluation_id']!=identity({k:x for k,x in v.items() if k!='evaluation_id'}):raise ValueError('request/result identity differs')
    if r['source_sha256']!=sources(ctx,root) or m['source_sha256']!=r['source_sha256'] or m['files_sha256']!=finite.inventory(output,('manifest.json',)):
        raise ValueError('source or payload differs')
    for key in ('vehicle_candidate_id','body_candidate_id','magnet_component_id','selection_id'):
        if r[key]!=ctx[key] or v[key]!=ctx[key]:raise ValueError('mixed selected identity: '+key)
    if r['component']!=ctx['component'] or r['specifications']!=specifications():raise ValueError('physical component/native plan differs')
    if v['request_id']!=r['request_id'] or m['request_id']!=r['request_id'] or m['evaluation_id']!=v['evaluation_id']:raise ValueError('cross-package identity differs')
    if digest(r['getdp']['path'])!=r['getdp']['sha256']:raise ValueError('solver binary differs')
    if len(v['native_rows'])!=len(specifications()):raise ValueError('native case inventory differs')
    for row,spec in zip(v['native_rows'],specifications()):
        d=output/spec['case'];per=read(d/'input.json')
        if row['case']!=spec['case'] or row['specification']!=spec or per!=dict(schema=SCHEMA,component=ctx['component'],spec=spec,getdp=r['getdp'],source_sha256=r['source_sha256']):raise ValueError('case physical input differs')
        if row['execution_status']=='completed':
            p=read(d/'point.json')
            if p!=row['point'] or _derived(d,per,p)!=p or row['execution']['returncode']!=0 or row['execution']['timed_out'] is not False:
                raise ValueError('native field/state/formulation readback differs')
        elif 'point' in row:raise ValueError('unfinished native case cannot supply force')
    if v['load_cases']!=loads(ctx) or v['current_diagnostics']!=current_diagnostics(ctx) or v['equilibrium_diagnostics']!=curve_diagnostics(ctx,v['native_rows']):raise ValueError('derived load/equilibrium/current diagnostics differ')
    for record in (r,m,v,*v['native_rows']):
        if any(record.get(k) is not val for k,val in FLAGS.items()):raise ValueError('research cannot grant acceptance')
    return dict(verified=True,selection_id=ctx['selection_id'],case_count=len(v['native_rows']),
        executed_cases=sum(row['execution_status']=='completed' for row in v['native_rows']),
        PDE_converged_cases=sum(row.get('point',{}).get('force_credit',False) for row in v['native_rows']),**FLAGS)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('run','verify','worker'));p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--output',type=Path,required=True);p.add_argument('--input',type=Path);p.add_argument('--getdp');a=p.parse_args()
    if a.action=='worker':worker(read(a.input),a.output);return
    value=run(a.output,a.root,a.getdp) if a.action=='run' else verify(a.output,a.root)
    print(json.dumps(value if a.action=='verify' else dict(evaluation_id=value['evaluation_id'],native_cases=len(value['native_rows'])),sort_keys=True))


if __name__=='__main__':main()
