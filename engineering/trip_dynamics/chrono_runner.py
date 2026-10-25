"""Project Chrono benchmark backend. No substitute integrator is available.

Six rigid bodies run through one fixed launch zone and one receiving zone.
Support/guidance are ideal five-DOF constraints, not a magnetic force map. Force
allocation uses body-envelope overlap as an explicit ideal pickup hypothesis;
installed winding geometry, current, voltage and force density are unbounded.
"""
from functools import lru_cache
from hashlib import sha256
import importlib
import json
import math
from pathlib import Path
import sys
import time

from . import formation

OFFICIAL_SOURCES=[
 'https://api.projectchrono.org/10.0.0/pychrono_installation.html',
 'https://github.com/projectchrono/chrono/blob/10.0.0/src/demos/python/mbs/demo_MBS_spring.py',
 'https://api.projectchrono.org/10.0.0/classchrono_1_1_ch_link_mate_generic.html']


class BackendUnavailable(RuntimeError):pass


def _chrono():
    try:
        module=importlib.import_module('pychrono')
        for name in ('ChSystemNSC','ChBody','ChVector3d','ChLinkTSDA','ChLinkMateGeneric','ChSolverMINRES','ChTimestepperEulerImplicitLinearized'):
            if not hasattr(module,name):raise ImportError('missing Chrono API '+name)
        return module
    except (ImportError,OSError) as exc:
        raise BackendUnavailable('Genuine Project Chrono/PyChrono backend unavailable; use the pinned isolated environment') from exc


def _hash(path):return sha256(Path(path).read_bytes()).hexdigest()


@lru_cache(maxsize=1)
def solver_info():
    try:chrono=_chrono()
    except BackendUnavailable as exc:return dict(available=False,backend='Project Chrono',reason=str(exc),fallback=False)
    records=list((Path(sys.prefix)/'conda-meta').glob('pychrono-*.json'))
    if len(records)!=1:raise BackendUnavailable('one explicit PyChrono conda package receipt required')
    package=json.loads(records[0].read_bytes())
    if not package.get('url','').startswith('https://conda.anaconda.org/projectchrono/'):
        raise BackendUnavailable('PyChrono package is not from the official projectchrono channel')
    binaries=sorted(Path(chrono.__file__).parent.glob('_core*.so'))
    if not binaries:raise BackendUnavailable('native Chrono core shared object missing')
    result=dict(available=True,backend='Project Chrono/PyChrono',version=package['version'],build=package['build'],
        package_url=package['url'],package_sha256=package.get('sha256'),python=sys.version,
        executable=str(Path(sys.executable).resolve()),native_binary_sha256={p.name:_hash(p) for p in binaries},
        system='ChSystemNSC',solver='ChSolverMINRES',solver_tolerance=1e-12,solver_iterations=200,
        timestepper='ChTimestepperEulerImplicitLinearized',fallback=False,official_sources=OFFICIAL_SOURCES)
    result['solver_id']=formation.identity(result)
    return result


def new_system():
    c=_chrono();system=c.ChSystemNSC();system.SetGravitationalAcceleration(c.ChVector3d(0,0,-9.80665))
    solver=c.ChSolverMINRES();solver.SetMaxIterations(200);solver.SetTolerance(1e-12);system.SetSolver(solver)
    system.SetTimestepper(c.ChTimestepperEulerImplicitLinearized(system));return c,system


def _scenario(scenario,dt_s):
    if not isinstance(scenario,dict):raise ValueError('explicit scenario object required')
    allowed={'schema','case_id','scenario_id','candidate_id','vehicle_id','distance_m','cars','car_length_m','powered_zone_m','max_speed_m_s','acceleration_m_s2','mechanical_step_s','mode','load_case','temperature_C','fault','coupling_gap_m','coupler_stiffness_N_per_m','coupler_damping_Ns_per_m','vector_force_id'}
    if set(scenario)-allowed:raise ValueError('unknown scenario fields: '+str(sorted(set(scenario)-allowed)))
    if scenario.get('mode')!='benchmark':raise ValueError('benchmark backend cannot execute evidence/exploration modes')
    if scenario.get('schema','osr-trip-scenario/1')!='osr-trip-scenario/1':raise ValueError('trip scenario schema differs')
    if scenario.get('candidate_id') is not None or scenario.get('fault') is not None:raise ValueError('ideal benchmark cannot stand for a physical candidate or fault trajectory')
    if scenario.get('cars',6)!=6 or scenario.get('car_length_m',17.)!=17.:raise ValueError('six 17m bodies required')
    if scenario.get('distance_m') not in (1500,2000):raise ValueError('benchmark requires a 1500m or 2000m translation')
    if scenario.get('load_case','AW3') not in ('empty','AW3','asymmetric'):raise ValueError('unknown load case')
    if type(dt_s) not in (int,float) or not math.isfinite(dt_s) or not .0001<=dt_s<=.02:raise ValueError('finite timestep0.0001..0.02s required')
    raw={k:v for k,v in scenario.items() if k!='scenario_id'};input_id=formation.identity(raw)
    if scenario.get('scenario_id',input_id)!=input_id:raise ValueError('scenario identity differs from complete request')
    value=dict(schema='osr-trip-scenario/1',case_id='straight-ideal-benchmark',cars=6,car_length_m=17.,powered_zone_m=350.,max_speed_m_s=20.,acceleration_m_s2=.8,load_case='AW3',temperature_C=20.,mode='benchmark',candidate_id=None,fault=None)
    value.update(raw);value['scenario_id']=input_id
    for k in ('powered_zone_m','max_speed_m_s','acceleration_m_s2'):
        if type(value[k]) not in (int,float) or not math.isfinite(value[k]) or value[k]<=0:raise ValueError('finite positive '+k+' required')
    if 'mechanical_step_s' in scenario and not math.isclose(scenario['mechanical_step_s'],dt_s,rel_tol=0,abs_tol=1e-15):raise ValueError('requested and executed mechanical timesteps differ')
    return value


def _xyz(v):return [float(v.x),float(v.y),float(v.z)]


def _state(bodies):return [dict(position_m=_xyz(b.GetPos()),velocity_m_s=_xyz(b.GetPosDt()),angular_velocity_rad_s=_xyz(b.GetAngVelParent())) for b in bodies]


def _overlap(x,L,zone):return max(0.,min(x+L/2,zone[1])-max(x-L/2,zone[0]))


def compare_timesteps(coarse,fine):
    physical=lambda result:{k:v for k,v in result['inputs']['scenario'].items() if k not in ('scenario_id','mechanical_step_s')}
    if physical(coarse)!=physical(fine) or coarse['inputs']['vehicle_id']!=fine['inputs']['vehicle_id']:
        raise ValueError('timestep comparison requires identical scenario/vehicle inputs')
    if not fine['dt_s']<coarse['dt_s']:raise ValueError('confirmation timestep must be smaller')
    a,b=coarse['final_state'],fine['final_state']
    coarse_samples={round(row['time_s'],6):row for row in coarse['trace']}
    fine_samples={round(row['time_s'],6):row for row in fine['trace']}
    common=sorted(set(coarse_samples)&set(fine_samples))
    trajectory_difference=max(abs(x['position_m'][0]-y['position_m'][0]) for t in common for x,y in zip(coarse_samples[t]['cars'],fine_samples[t]['cars']))
    return dict(executed=True,matched_trace_samples=len(common),maximum_sampled_trajectory_difference_m=trajectory_difference,
        maximum_coupler_peak_difference_N=max(abs(x-y) for x,y in zip(coarse['summary']['peak_coupler_force_N'],fine['summary']['peak_coupler_force_N'])),
        maximum_coupler_extension_difference_m=max(abs(x-y) for x,y in zip(coarse['summary']['peak_coupler_extension_m'],fine['summary']['peak_coupler_extension_m'])),coarse_scenario_id=coarse['inputs']['scenario_id'],fine_scenario_id=fine['inputs']['scenario_id'],coarse_dt_s=coarse['dt_s'],fine_dt_s=fine['dt_s'],
        maximum_position_difference_m=max(abs(x['position_m'][0]-y['position_m'][0]) for x,y in zip(a,b)),
        maximum_speed_difference_m_s=max(abs(x['velocity_m_s'][0]-y['velocity_m_s'][0]) for x,y in zip(a,b)),
        work_residual_difference_J=abs(coarse['summary']['work_energy_residual_J']-fine['summary']['work_energy_residual_J']),
        physical_accepted=False,scope='Two executed numerical samples; no continuum convergence proof')


def run_benchmark(scenario,masses_kg,*,dt_s=.001,vector_force=None):
    started=time.monotonic();s=_scenario(scenario,dt_s);info=solver_info()
    if not info['available']:raise BackendUnavailable(info['reason'])
    masses=list(masses_kg)
    if len(masses)!=6:raise ValueError('six explicit per-car masses required')
    if vector_force is not None and not s.get('vector_force_id'):raise ValueError('callback requires source-bound vector_force_id')
    c,system=new_system();parameters={k:s[k] for k in ('coupling_gap_m','coupler_stiffness_N_per_m','coupler_damping_Ns_per_m') if k in s}
    train=formation.build(system,c,masses,body_length_m=s['car_length_m'],**parameters);bodies=train['bodies'];links=train['couplers'];initial=train['initial_positions_m'];definition=train['definition'];L=definition['body_length_m'];M=sum(masses)
    D=s['distance_m'];a=s['acceleration_m_s2'];v=s['max_speed_m_s'];t_acc=v/a;d_acc=v*v/(2*a)
    if 2*d_acc>D:raise ValueError('speed/acceleration profile does not fit route distance')
    t_coast=(D-2*d_acc)/v;t_brake=t_acc+t_coast;t_end=t_brake+t_acc
    if t_end/dt_s>2000000 or t_end>300:raise ValueError('benchmark numerical budget exceeded')
    rear=initial[-1]-L/2;launch=[rear,rear+s['powered_zone_m']];receive=[D+L/2-s['powered_zone_m'],D+L/2]
    zones=dict(launch_m=launch,receiving_m=receive,scope='Two common fixed spatial zones, body-length pickup-envelope hypothesis; actual module/winding overlap unqualified')
    trace=[];outside_overlap=False;next_sample=0.;sample_interval=.1;external_work=absolute_work=damper_heat=impulse=0.;peak_force=[0.]*6;peak_density=[0.]*6;peak_coupler=[0.]*5;peak_extension=[0.]*5;maximum_com_error=constraint_error=0.;minimum_overlap=L;steps=0;status='completed';error=None
    def sample(t,states,forces,phase):
        trace.append(dict(time_s=t,phase=phase,cars=[dict(state,translation_m=state['position_m'][0]-x0,station_force_N=forces[i]) for i,(state,x0) in enumerate(zip(states,initial))],couplers=[dict(extension_m=l.GetLength()-l.GetRestLength(),force_N=l.GetForce()) for l in links]))
    states=_state(bodies);initial_energy=sum(.5*m*sum(v*v for v in q['velocity_m_s']) for m,q in zip(masses,states));sample(0.,states,[0.]*6,'initial');next_sample=sample_interval
    while system.GetChTime()<t_end-1e-10:
        if time.monotonic()-started>295:status='interrupted';error='295s wall-clock budget exceeded';break
        t=system.GetChTime();h=min(dt_s,t_end-t)
        # Land exactly on commanded phase boundaries instead of smearing a
        # discontinuity across an integration step.
        for boundary in (t_acc,t_brake):
            if t<boundary-1e-10:h=min(h,boundary-t)
        mid=t+h/2;phase='launch' if mid<t_acc else 'coast' if mid<t_brake else 'receiving';command=a if phase=='launch' else -a if phase=='receiving' else 0.;zone=launch if phase=='launch' else receive
        old=states;overlaps=[_overlap(q['position_m'][0],L,zone) if command else 0. for q in old];weights=[m*overlap/L for m,overlap in zip(masses,overlaps)];den=sum(weights)
        if command and den==0:status='held';error='No train pickup-envelope overlap with common powered zone';break
        forces=[M*command*w/den if command else 0. for w in weights]
        added=vector_force(t,old,dict(scenario=s,zones=zones,vehicle=definition)) if vector_force else [dict(force_N=[0.,0.,0.],torque_Nm=[0.,0.,0.]) for _ in bodies]
        if not isinstance(added,(list,tuple)) or len(added)!=6:raise ValueError('callback must return six force/torque vectors')
        old_rates=[l.GetVelocity() for l in links];applied=[]
        for i,(body,idx,F,extra) in enumerate(zip(bodies,train['accumulators'],forces,added)):
            f=extra.get('force_N');torque=extra.get('torque_Nm')
            if any(not isinstance(q,(list,tuple)) or len(q)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in q) for q in (f,torque)):raise ValueError('callback requires finite SI global force_N/torque_Nm xyz vectors')
            f=[f[0]+F,f[1],f[2]];applied.append(f);body.EmptyAccumulator(idx);body.AccumulateForce(idx,c.ChVector3d(*f),body.GetPos(),False);body.AccumulateTorque(idx,c.ChVector3d(*torque),False)
            peak_force[i]=max(peak_force[i],abs(F))
            if F:
                if overlaps[i]<=0:raise ValueError('station force outside common powered zone')
                peak_density[i]=max(peak_density[i],abs(F)/overlaps[i]);minimum_overlap=min(minimum_overlap,overlaps[i])
        # Chrono caches applied force at Update: without this explicit refresh,
        # a changed accumulator is delayed by one step at phase boundaries.
        system.Update();system.DoStepDynamics(h);steps+=1;states=_state(bodies)
        if any(F and _overlap(q['position_m'][0],L,zone)<=0 for F,q in zip(forces,states)):
            outside_overlap=True;status='held';error='A forced integration interval left the powered body-overlap envelope'
        if any(not math.isfinite(x) for q in states for name in ('position_m','velocity_m_s','angular_velocity_rad_s') for x in q[name]):status='failed';error='Nonfinite Chrono state';break
        external_work+=sum(sum(f[j]*(new['position_m'][j]-prev['position_m'][j]) for j in range(3))-m*9.80665*(new['position_m'][2]-prev['position_m'][2]) for f,new,prev,m in zip(applied,states,old,masses))
        absolute_work+=sum(abs(sum(f[j]*(new['position_m'][j]-prev['position_m'][j]) for j in range(3))) for f,new,prev in zip(applied,states,old))
        impulse+=sum(f[0] for f in applied)*h
        damper_heat+=sum(definition['coupler_damping_Ns_per_m']*.5*(before**2+l.GetVelocity()**2)*h for before,l in zip(old_rates,links))
        for i,l in enumerate(links):peak_coupler[i]=max(peak_coupler[i],abs(l.GetForce()));peak_extension[i]=max(peak_extension[i],abs(l.GetLength()-l.GetRestLength()))
        end=system.GetChTime();expected=.5*a*end*end if end<t_acc else d_acc+v*(end-t_acc) if end<t_brake else D-.5*a*(t_end-end)**2
        translation=sum(m*(q['position_m'][0]-x0) for m,q,x0 in zip(masses,states,initial))/M;maximum_com_error=max(maximum_com_error,abs(translation-expected));constraint_error=max(constraint_error,max(abs(q['position_m'][j]) for q in states for j in (1,2)))
        if end>=next_sample-1e-10 or end>=t_end-1e-10:sample(end,states,forces,phase);next_sample+=sample_interval
        if outside_overlap:break
    end=system.GetChTime()
    if abs(trace[-1]['time_s']-end)>1e-12:sample(end,states,[0.]*6,'final')
    kinetic=sum(.5*m*sum(v*v for v in q['velocity_m_s']) for m,q in zip(masses,states));spring=sum(.5*definition['coupler_stiffness_N_per_m']*(l.GetLength()-l.GetRestLength())**2 for l in links);residual=kinetic+spring-initial_energy-external_work+damper_heat
    distance_error=max(abs(q['position_m'][0]-x0-D) for q,x0 in zip(states,initial));speed_error=max(abs(q['velocity_m_s'][0]) for q in states)
    summary=dict(completed=status=='completed',elapsed_simulation_s=end,actual_steps=steps,terminal_max_distance_error_m=distance_error,terminal_max_speed_m_s=speed_error,terminal_distance_tolerance_m=.2,terminal_speed_tolerance_m_s=.05,terminal_screen_pass=status=='completed' and distance_error<=.2 and speed_error<=.05,maximum_COM_trajectory_error_m=maximum_com_error,maximum_support_constraint_position_error_m=constraint_error,external_work_J=external_work,absolute_external_work_J=absolute_work,damper_heat_J=damper_heat,final_kinetic_energy_J=kinetic,final_coupler_spring_energy_J=spring,work_energy_residual_J=residual,relative_work_energy_residual=abs(residual)/max(absolute_work,damper_heat,1.),longitudinal_impulse_residual_Ns=sum(m*q['velocity_m_s'][0] for m,q in zip(masses,states))-impulse,peak_station_force_N_per_car=peak_force,peak_station_force_density_N_per_m_per_car=peak_density,minimum_nonzero_active_body_overlap_m=minimum_overlap,peak_coupler_force_N=peak_coupler,peak_coupler_extension_m=peak_extension,station_force_outside_active_body_overlap=outside_overlap)
    source_paths=[Path(__file__),Path(formation.__file__)];inputs=dict(scenario=s,scenario_id=s['scenario_id'],effective_scenario_id=formation.identity(s),vehicle=definition,vehicle_id=definition['vehicle_id'],source_vehicle_id=s.get('vehicle_id'),solver_id=info['solver_id'],source_sha256={p.name:_hash(p) for p in source_paths})
    result=dict(schema='osr-chrono-trip-benchmark/1',state=status,error=error,backend=info,inputs=inputs,dt_s=dt_s,zones=zones,summary=summary,final_state=states,trace=trace,sample_interval_s=sample_interval,every_step_accounting=True,timestep_convergence=dict(executed=False,reason='requires independent smaller-step execution'),execution_wall_s=time.monotonic()-started,scope='Genuine Chrono rigid-body/coupler integration with prescribed ideal station force and ideal support; benchmark only',unresolved=['magnetic lift/guidance and gap dynamics','actual coil/module overlap','thrust/current/voltage and electrical transients','thermal duty and cooling','transverse/rotational DOFs constrained','flexible bodies/guidebeam','capture/contact and faults','actual coupler/inertia properties'],engineering_qualified=False,physical_accepted=False,journey_accepted=False)
    result['evaluation_id']=formation.identity(dict(inputs=inputs,dt_s=dt_s,zones=zones))
    return result


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--info',action='store_true')
    parser.add_argument('--input',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.info:
        print(json.dumps(solver_info(),sort_keys=True,indent=2));return
    if args.input is None or args.output is None:parser.error('--input and --output required')
    if args.output.exists():raise FileExistsError('refusing to overwrite retained benchmark output')
    request=json.loads(args.input.read_bytes())
    if set(request)-{'scenario','masses_kg','dt_s'}:raise ValueError('unknown benchmark request keys')
    result=run_benchmark(request['scenario'],request['masses_kg'],dt_s=request.get('dt_s',.001))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(state=result['state'],evaluation_id=result['evaluation_id'],summary=result['summary']),sort_keys=True))


if __name__=='__main__':main()
