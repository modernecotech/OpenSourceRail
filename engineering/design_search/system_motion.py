"""Available-map admission and bounded forward longitudinal research method.

Required force is never available thrust. Current linear LIM and generic DC
fixtures cannot enter this adapter as an available station motor. Synthetic
maps exercise the method only. Even a map-driven reduced trajectory does not
establish a physically qualified train, WSP, flexible-body or protected service.
"""
from copy import deepcopy
from itertools import product
from bisect import bisect_right
from math import isfinite,sqrt,prod
from pathlib import Path
import re
from engineering.station_rail.common import identity,digest
from engineering.station_rail import braking
from . import architecture_demand

PRODUCER='engineering/design_search/system_motion.py'
AXES=('position_m','speed_m_s','current_A','temperature_C')
FIELDS=('thrust_N_train','electrical_input_W_train','loss_W_train','voltage_V','vertical_force_N_train')
FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
    manufacturing_release=False,operating_release=False,physical_journey_completed=False)


def _number(x,nonnegative=False):return type(x) in (int,float) and isfinite(x) and (not nonnegative or x>=0)

def _sha(x):return isinstance(x,str) and re.fullmatch('[0-9a-f]{64}',x) is not None

def _bundle(bundle):
    b=deepcopy(bundle)
    if b.get('schema')!='osr-coupled-railway-bundle/1' or b.get('bundle_id',b.get('candidate_id'))!=b.get('candidate_id') or any(not _sha(b.get(k)) for k in ('candidate_id','body_candidate_id','support_component_id','propulsion_component_id')):raise ValueError('Canonical same-candidate bundle required')
    if b.get('motor_definition',{}).get('motor_component_id')!=b.get('propulsion_component_id'):raise ValueError('Motor definition differs from candidate bundle')
    if type(b.get('cars')) is not int or b['cars']<1 or not _number(b.get('rotating_equivalent_kg_per_car'),True):raise ValueError('Explicit formation and counted rotating-equivalent mass required')
    for key in ('accounted_tare_kg_per_car','accounted_cap_loaded_kg_per_car','accounted_160_control_kg_per_car'):
        if not _number(b.get('mass',{}).get(key)) or b['mass'][key]<=0:raise ValueError('Accounted empty/normal/crowd mass hypotheses required')
    if not b.get('requirement_revision'):raise ValueError('Separate requirement revision required')
    return b


def scenario(bundle,overrides=None):
    case=bundle.get('architecture_case',{});rq=case.get('requirements',{})
    value=dict(distance_m=case.get('physical_definition',{}).get('route',{}).get('station_spacing_m',2000.),
        powered_windows=deepcopy(case.get('commanded_power_windows_m',[])),speed_cap_m_s=rq.get('speed_cap_m_s',20.),
        acceleration_m_s2=rq.get('acceleration_m_s2',.4),deceleration_m_s2=rq.get('service_deceleration_m_s2',.6),
        load='normal',grade_up_fraction=0.,headwind_m_s=0.,dt_s=.05,maximum_time_s=600.,
        current_command_A=0.,initial_current_A=0.,brake_start_m=None,rail_adhesion=.05,available_discs=8,
        berth_tolerance_m=2.,rolling_coefficient=.0025,bearing_N_per_car=50.,aero_N_s2_m2_per_car=1.8)
    value.update(overrides or {})
    value.pop('scenario_id',None)
    if value['load'] not in ('empty','normal','crowd'):raise ValueError('Explicit empty/normal/crowd loading required')
    for key in ('distance_m','speed_cap_m_s','acceleration_m_s2','deceleration_m_s2','dt_s','maximum_time_s'):
        if not _number(value[key]) or value[key]<=0:raise ValueError('Positive finite scenario values required')
    if value['dt_s']>.2 or value['maximum_time_s']>600:raise ValueError('Forward method budget <=600s and step <=.2s')
    if not _number(value['grade_up_fraction']) or abs(value['grade_up_fraction'])>.1 or not _number(value['headwind_m_s'],True):raise ValueError('Reference grade/headwind domain exceeded')
    if any(not _number(value[k],True) for k in ('rolling_coefficient','bearing_N_per_car','aero_N_s2_m2_per_car','rail_adhesion','berth_tolerance_m')):raise ValueError('Finite nonnegative drag/brake hypotheses required')
    if value['brake_start_m'] is not None and (not _number(value['brake_start_m'],True) or value['brake_start_m']>value['distance_m']):raise ValueError('Explicit fixed brake initiation position required')
    if any(not _number(value[k]) for k in ('current_command_A','initial_current_A')) or type(value['available_discs']) is not int or not 0<=value['available_discs']<=8:raise ValueError('Finite current commands and zero to eight brake discs required')
    architecture_demand._windows(value['powered_windows'],value['distance_m'])
    value['scenario_id']=identity(value);return value


def admit_map(bundle,force_map,case,*,allow_synthetic=False,current_source_sha256=None):
    """A source/model/domain gate; references still require external review."""
    if force_map is None:return dict(admitted=False,reasons=['No actual available force/current/temperature/position map'],test_only=False)
    m=force_map;reasons=[];test=m.get('evidence_kind')=='synthetic-method-test'
    if m.get('schema')!='osr-station-available-force-map/1':reasons.append('Unknown force-map schema')
    if m.get('evaluation_id')!=identity({k:v for k,v in m.items() if k!='evaluation_id'}):reasons.append('Force-map evaluation identity differs')
    for key,expected in [('candidate_id',bundle['candidate_id']),('motor_component_id',bundle['propulsion_component_id']),('scenario_id',case['scenario_id'])]:
        if m.get(key)!=expected:reasons.append('Force map mismatches '+key)
    if test and not allow_synthetic:reasons.append('Synthetic maps are test-only; explicit method opt-in required')
    if not test:
        if m.get('evidence_kind')!='verified-numerical-operating-map' or m.get('model_family')!='nonlinear-moving-LIM':reasons.append('Linear phasor or generic DC evidence is not an available moving nonlinear motor')
        required=('independent_benchmarks','mesh_time_convergence','finite_overlap','zero_force_outside_windows','current_circuit_control','thermal_duty','normal_force_interface')
        if any(m.get('validation',{}).get(k)!='supported' for k in required):reasons.append('Missing independent moving/electrical/thermal/interface validation')
        if m.get('execution')!='completed' or m.get('numerical_validity')!='converged' or m.get('model_domain')!='supported':reasons.append('Map numerical/model state is unsupported')
        sources=m.get('source_sha256',{});current=current_source_sha256 or bundle.get('source_sha256',{})
        if not sources or any(current.get(n)!=h for n,h in sources.items()):reasons.append('Force-map solver/source epoch differs')
        if not _sha(m.get('review_record_id')) or not _sha(m.get('interface_state_id')):reasons.append('Reviewed exact operating interface state required')
        if bundle.get('brake_definition') is None:reasons.append('Independent candidate-bound brake plant required before a numerical journey')
    if m.get('powered_windows')!=case['powered_windows']:reasons.append('Map station engagement windows differ; no overlap scaling permitted')
    axes=m.get('axes',{})
    for axis in AXES:
        values=axes.get(axis,[])
        if not values or any(not _number(v) for v in values) or any(b<=a for a,b in zip(values,values[1:])):reasons.append('Invalid sampled axis '+axis)
    if reasons:return dict(admitted=False,reasons=reasons,test_only=test)
    if axes['position_m'][0]>0 or axes['position_m'][-1]<case['distance_m'] or axes['speed_m_s'][0]>0 or axes['speed_m_s'][-1]<case['speed_cap_m_s']:reasons.append('Map does not cover the declared position/speed operating envelope')
    if any(not axes['current_A'][0]<=case[k]<=axes['current_A'][-1] for k in ('current_command_A','initial_current_A')):reasons.append('Current command outside sampled map domain')
    if prod(len(axes[a]) for a in AXES)>16384:return dict(admitted=False,reasons=['Map exceeds this bounded surrogate interpolation budget'],test_only=test)
    expected=set(product(*(axes[a] for a in AXES)));samples=m.get('samples',[]);actual=[]
    for row in samples:
        if not isinstance(row,dict) or any(not _number(row.get(a)) for a in AXES):reasons.append('Missing/nonfinite map sample coordinates');continue
        key=tuple(row[a] for a in AXES);actual.append(key)
        if any(not _number(row.get(f)) for f in FIELDS) or row['loss_W_train']<0:reasons.append('Missing/nonfinite force, power or loss sample')
        elif abs(row['electrical_input_W_train']-row['thrust_N_train']*row['speed_m_s']-row['loss_W_train'])>max(1.,abs(row['electrical_input_W_train']))*1e-5:reasons.append('Sample electrical/mechanical/loss work identity fails')
        if abs(row.get('vertical_force_N_train',0.))>1e-6:reasons.append('Nonzero motor normal force requires a coupled wheel-load adapter')
    if len(actual)!=len(set(actual)) or set(actual)!=expected:reasons.append('Complete Cartesian samples required; no hull extrapolation')
    thermal=m.get('thermal_model',{});electrical=m.get('electrical_limits',{})
    if not all(_number(thermal.get(k)) for k in ('capacity_J_K','ambient_C','initial_C','maximum_C','heat_rejection_W_K')) or thermal.get('capacity_J_K',0)<=0 or thermal.get('heat_rejection_W_K',-1)<0:reasons.append('Explicit thermal inventory/model required')
    if not all(_number(electrical.get(k)) and electrical[k]>0 for k in ('maximum_voltage_V','maximum_current_A','current_slew_A_s')):reasons.append('Explicit electrical/control envelope required')
    if all(_number(thermal.get(k)) for k in ('initial_C','maximum_C')) and not axes['temperature_C'][0]<=thermal['initial_C']<=thermal['maximum_C']<=axes['temperature_C'][-1]:reasons.append('Thermal envelope outside sampled map domain')
    return dict(admitted=not reasons,reasons=reasons,test_only=test,evaluation_id=m.get('evaluation_id'))


def sample_map(force_map,**state):
    """Multilinear sampled-state interpolation, with no extrapolation/scaling."""
    choices=[]
    for axis in AXES:
        values=force_map['axes'][axis];x=state[axis]
        if x<values[0]-1e-9 or x>values[-1]+1e-9:raise ValueError('Map state outside sampled '+axis)
        if len(values)==1:
            if abs(x-values[0])>1e-9:raise ValueError('Map axis has one fixed supported state')
            choices.append([(values[0],1.)]);continue
        i=min(len(values)-2,max(0,bisect_right(values,x)-1));weight=(x-values[i])/(values[i+1]-values[i]);choices.append([(values[i],1-weight),(values[i+1],weight)])
    table={tuple(row[a] for a in AXES):row for row in force_map['samples']};result={f:0. for f in FIELDS}
    for terms in product(*choices):
        weight=1.
        for value,w in terms:weight*=w
        row=table[tuple(v for v,w in terms)]
        for f in FIELDS:result[f]+=weight*row[f]
    return result


def _mass(bundle,load):return bundle['mass'][dict(empty='accounted_tare_kg_per_car',normal='accounted_cap_loaded_kg_per_car',crowd='accounted_160_control_kg_per_car')[load]]


def _brake_definition(bundle):
    spec=bundle.get('brake_definition')
    if spec is None:return None
    if any(spec.get(k)!=bundle.get(k) for k in ('candidate_id','body_candidate_id','support_component_id','propulsion_component_id')) or abs(spec['rotors']['equivalent_inertial_mass_kg_per_car']-bundle['rotating_equivalent_kg_per_car'])>1e-8:raise ValueError('Brake definition or rotor basis differs from canonical candidate')
    return spec


def brake_screens(bundle,case):
    spec=_brake_definition(bundle)
    if spec is None:return dict(execution='not-run',reason='Actual candidate-bound brake/rotor definition missing',cases=[],qualified_braking_floor=False)
    rows=[];dt=.05
    for loading in ('empty','normal','crowd'):
        mass=_mass(bundle,loading);effective=mass+bundle['rotating_equivalent_kg_per_car']
        for name,mu,grade,discs in [('wet-downhill',.05,.02,8),('one-channel-loss',.05,.02,4),('insufficient-adhesion-control',.03,.04,8)]:
            x=t=heat=work=0.;v=case['speed_cap_m_s'];initial=.5*effective*v*v;state='time-budget';reason=None
            for step in range(8000):
                f=braking.force_state(spec,mass,v,t+dt/2,rail_adhesion=mu,grade_down_fraction=grade,available_discs=discs)
                if not f['valid']:state='outside-model-domain';reason=f['reason'];break
                a=f['acceleration_m_s2'];h=min(dt,v/-a) if a<0 else dt;new=max(0.,v+a*h);dx=(v+new)*h/2
                x+=dx;t+=h;heat+=f['torque_equivalent_brake_force_N_per_car']*dx;work+=f['downhill_gravity_N_per_car']*dx;v=new
                if v<=1e-8:state='stopped-in-reduced-hypothesis';break
                if t>5 and a>=0:state='cannot-stop-in-declared-hypothesis';break
            capacity=spec.get('counted_disc_stock_kg_per_car');specific=spec.get('steel_specific_heat_J_kg_K_hypothesis');ambient=spec.get('ambient_C_hypothesis')
            temp=ambient+heat/(capacity*discs/8*specific) if all(_number(k) for k in (capacity,specific,ambient)) and min(capacity,specific)>0 else None
            rows.append(dict(loading=loading,case=name,state=state,reason=reason,distance_m=x,time_s=t,final_speed_m_s=v,
                physical_mass_kg_per_car=mass,rotating_equivalent_kg_per_car=bundle['rotating_equivalent_kg_per_car'],working_discs_per_car=discs,
                disc_heat_J_per_car=heat,lumped_disc_temperature_C_hypothesis=temp,friction_fade_curve_qualified=False,
                energy_residual_J_per_car=initial+work-heat-.5*effective*v*v))
    return dict(execution='completed',cases=rows,qualified_braking_floor=False,scope='Frozen brake torque/response and ideal WSP hypotheses; no resistance credit, supplier fade or hardware qualification',**FLAGS)


def forward(bundle,force_map,case,*,allow_synthetic=False,current_source_sha256=None):
    bundle=_bundle(bundle);spec=_brake_definition(bundle)
    admission=admit_map(bundle,force_map,case,allow_synthetic=allow_synthetic,current_source_sha256=current_source_sha256)
    result=dict(execution='not-run',admission=admission,predicted_stop_within_berth=False,available_motor_map_id=None,**FLAGS)
    if not admission['admitted']:return result
    mass=_mass(bundle,case['load']);cars=bundle['cars'];effective=(mass+bundle['rotating_equivalent_kg_per_car'])*cars
    D=case['distance_m'];h0=case['dt_s'];v=x=t=0.;current=case['initial_current_A'];T=force_map['thermal_model']['initial_C'];thermal=force_map['thermal_model'];limits=force_map['electrical_limits']
    electrical=heat=drag_work=gravity_work=brake_heat=mechanical=0.;trace=[];state='time-budget';reason=None;brake_t=None
    initial_energy=0.;window_edges=sorted({edge for pair in case['powered_windows'] for edge in pair})
    for step in range(12000):
        active=any(a-1e-9<=x<b-1e-9 for a,b in case['powered_windows']);braking_now=case['brake_start_m'] is not None and x>=case['brake_start_m']-1e-9
        if braking_now and brake_t is None:brake_t=t
        command=case['current_command_A'] if active and not braking_now and v<case['speed_cap_m_s'] else 0.
        delta=max(-limits['current_slew_A_s']*h0,min(limits['current_slew_A_s']*h0,command-current));next_current=current+delta
        if abs(next_current)>limits['maximum_current_A']+1e-8:state='electrical-limit';reason='current command exceeds admitted electrical envelope';break
        h=min(h0,case['maximum_time_s']-t)
        if h<=1e-10:break
        boundaries=[z for z in window_edges+[D]+([case['brake_start_m']] if case['brake_start_m'] is not None else []) if z>x+1e-8]
        edge=min(boundaries) if boundaries else D
        # Upper acceleration bound prevents a trial lookup outside a finite
        # map/window before the implicit force event has been resolved.
        upper=max(0.,max(row['thrust_N_train'] for row in force_map['samples']) if active else 0.)/effective+max(0.,-cars*mass*braking.G*case['grade_up_fraction'])/effective
        if v>0 or upper>0:
            denom=v+sqrt(max(0.,v*v+2*upper*(edge-x)))
            if denom>0:h=min(h,2*(edge-x)/denom)
        # Midpoint fixed-point force quadrature; no prescribed acceleration.
        acceleration=0.;sample=None;R=mass*braking.G*case['rolling_coefficient']+case['bearing_N_per_car'];brakeQ=0.
        try:
            for event_iteration in range(20):
                delta=max(-limits['current_slew_A_s']*h,min(limits['current_slew_A_s']*h,command-current));next_current=current+delta
                for iteration in range(10):
                    midv=max(0.,v+acceleration*h/2);midx=x+v*h/2+acceleration*h*h/8
                    sample=sample_map(force_map,position_m=midx,speed_m_s=midv,current_A=(current+next_current)/2,temperature_C=T) if active else {f:0. for f in FIELDS}
                    resistance=cars*(R+case['aero_N_s2_m2_per_car']*(midv+case['headwind_m_s'])**2)
                    gravity=-cars*mass*braking.G*case['grade_up_fraction']/sqrt(1+case['grade_up_fraction']**2)
                    if spec is not None:
                        f=braking.force_state(spec,mass,midv,(t-brake_t+h/2) if braking_now else 0.,pressure_Pa=None if braking_now else 0.,grade_down_fraction=-case['grade_up_fraction'],rail_adhesion=case['rail_adhesion'],available_discs=case['available_discs'],wayside_force_N=(sample['thrust_N_train']-resistance)/cars)
                        if not f['valid']:raise ValueError(f['reason'])
                        brakeQ=f['torque_equivalent_brake_force_N_per_car']*cars
                    elif braking_now:raise ValueError('Independent candidate-bound brake plant required')
                    a=(sample['thrust_N_train']-resistance+gravity-brakeQ)/effective
                    if abs(a-acceleration)<1e-10:break
                    acceleration=a
                else:raise ValueError('Force/current midpoint did not converge')
                newv=v+a*h
                if newv<0 and a<0:
                    shorter=v/-a
                    if shorter<h-1e-10:h=shorter;continue
                boundaries=[z for z in window_edges+[D]+([case['brake_start_m']] if case['brake_start_m'] is not None else []) if z>x+1e-8]
                edge=min(boundaries) if boundaries else D;dx=(v+max(0.,newv))*h/2
                if x+dx>edge+1e-8 and dx>0:
                    target=edge-x
                    shorter=2*target/(v+sqrt(max(0.,v*v+2*a*target))) if abs(a)>1e-12 else target/v
                    if shorter<h-1e-10:h=shorter;continue
                break
            else:raise ValueError('Finite-window/stop event did not converge')
            if sample['voltage_V']>limits['maximum_voltage_V']+1e-8:state='electrical-limit';reason='map voltage exceeds admitted bus';break
            newv=max(0.,v+a*h);dx=(v+newv)*h/2
            if abs(x+dx-edge)<1e-8:dx=edge-x
            if newv>case['speed_cap_m_s']+1e-7:state='controller-speed-limit';reason='Available current/force controller could not enforce cap';break
            if v==0 and newv==0 and a<=0:state='stalled';break
            speed=(v+newv)/2;balance=sample['electrical_input_W_train']-sample['thrust_N_train']*speed-sample['loss_W_train']
            if active and abs(balance)>max(1.,abs(sample['electrical_input_W_train']))*1e-3:raise ValueError('Interpolated map power identity outside numerical tolerance')
            newT=T+h*(sample['loss_W_train']-thermal['heat_rejection_W_K']*(T-thermal['ambient_C']))/thermal['capacity_J_K']
            if newT>thermal['maximum_C']+1e-9:state='thermal-limit';reason='thermal envelope exceeded';break
            electrical+=sample['electrical_input_W_train']*h;heat+=sample['loss_W_train']*h;mechanical+=sample['thrust_N_train']*dx;drag_work+=resistance*dx;gravity_work+=gravity*dx;brake_heat+=brakeQ*dx
            x+=dx;t+=h;v=newv;current=next_current;T=newT
            trace.append(dict(time_s=t,position_m=x,speed_m_s=v,current_A=current,temperature_C=T,thrust_N_train=sample['thrust_N_train'],electrical_input_W_train=sample['electrical_input_W_train'],brake_force_N_train=brakeQ))
            if x>=D-1e-8:state='destination-boundary';break
            if v<=1e-8 and brake_t is not None:state='stopped';break
        except ValueError as error:state='outside-model-domain';reason=str(error);break
    kinetic=.5*effective*v*v;stopped=v<=1e-7 and abs(x-D)<=case['berth_tolerance_m']
    result.update(execution='completed-method-test' if admission['test_only'] else 'completed-reduced-model',state=state,reason=reason,
        test_only=admission['test_only'],predicted_stop_within_berth=stopped,available_motor_map_id=None if admission['test_only'] else force_map['evaluation_id'],
        final_position_m=x,final_speed_m_s=v,elapsed_s=t,temperature_C=T,trace=trace,
        electrical_energy_J=electrical,magnetic_loss_energy_J=heat,mechanical_propulsion_work_J=mechanical,friction_brake_heat_J=brake_heat,
        energy_residual_J=initial_energy+mechanical+gravity_work-drag_work-brake_heat-kinetic,
        electrical_work_residual_J=electrical-heat-mechanical,
        engineering_screen='unknown',numerical_timestep_s=h0,
        scope='Force-driven point train and scalar thermal/current envelopes; no native Chrono, flexible body, hardware WSP, faults or protected-service acceptance')
    return result


def evaluate(candidate_bundle,available_map=None,*,scenario_overrides=None,allow_synthetic=False,current_source_sha256=None):
    b=_bundle(candidate_bundle);s=scenario(b,scenario_overrides);mass=_mass(b,s['load'])
    required=architecture_demand.demand(s['distance_m'],mass,b['rotating_equivalent_kg_per_car'],cars=b['cars'],powered_windows=s['powered_windows'],speed_cap_m_s=s['speed_cap_m_s'],acceleration_m_s2=s['acceleration_m_s2'],deceleration_m_s2=s['deceleration_m_s2'],grade=s['grade_up_fraction'],headwind=s['headwind_m_s'])
    raw_id=required.pop('demand_id');trace=required.pop('trace');required.update(raw_demand_id=raw_id,trace_sha256=identity(trace),schema='osr-required-motion-index/1');required['demand_id']=identity(required)
    motion=forward(b,available_map,s,allow_synthetic=allow_synthetic,current_source_sha256=current_source_sha256)
    tasks=[] if motion['admission']['admitted'] else ['Develop nonlinear transient moving-conductor A-u force/current/overlap map for this exact motor and candidate',
        'Confirm linear limit, zero/current-reversal controls, work balance and mesh/time convergence independently',
        'Resolve actual normal-force wheel loads, inverter/current transients, loss partition and repeated thermal duty']
    result=dict(schema='osr-coupled-longitudinal-research/1',candidate_id=b['candidate_id'],body_candidate_id=b.get('body_candidate_id'),propulsion_component_id=b['propulsion_component_id'],requirement_revision=b['requirement_revision'],scenario=s,
        mass_scope=b.get('mass_scope','accounted hypotheses; complete installed mass unknown'),required_demand=required,braking=brake_screens(b,s),forward_motion=motion,
        model_tasks=tasks,complete_installed_mass_kg=None,complete_installed_cost_USD=None,
        source_sha256={PRODUCER:digest(Path(__file__)), 'engineering/station_rail/braking.py':digest(Path(braking.__file__)), 'engineering/design_search/architecture_demand.py':digest(Path(architecture_demand.__file__))},**FLAGS)
    result['evaluation_id']=identity(result);return result
