"""Source-bound reduced forward method after trusted operating-map admission.

This derivative preserves the retained force/current/brake/thermal equations.
Its midpoint can never query behind a stationary train, and insufficient launch
force terminates at rest. No initial hold/ramp controller is invented. Voltage
is a nonnegative magnitude. The supplied gate is trusted application output,
never an admission record deserialized from a user evidence file.
"""
from copy import deepcopy
from math import sqrt
from engineering.station_rail import braking
from engineering.station_rail.common import digest, identity
from engineering.design_search import system_motion as retained
from . import FLAGS

PRODUCER='engineering/railway_completion/motion.py'
ANCESTOR='engineering/design_search/system_motion.py'
ANCESTOR_SHA256='e19eaeb7f389636c514c0c8ad4bec0aca1660f999521c37a69ecc24a098ea02a'
FIELDS=retained.FIELDS
sample_map=retained.sample_map
_bundle=retained._bundle
_brake_definition=retained._brake_definition
_mass=retained._mass


def _gate(bundle,force_map,case,admission):
    if not isinstance(admission,dict):
        raise ValueError('Trusted application operating admission required')
    if admission.get('admitted') is not True:
        return deepcopy(admission)
    if (admission.get('schema')!='osr-wheel-operating-admission/1'
        or admission.get('admission_id')!=identity({k:v for k,v in admission.items() if k!='admission_id'})
        or admission.get('evidence_ready') is not True
        or type(admission.get('test_only')) is not bool
        or any(admission.get(k) is not False for k in FLAGS)):
        raise ValueError('Trusted operating admission identity or disposition differs')
    if not isinstance(force_map,dict) or force_map.get('evaluation_id')!=identity({k:v for k,v in force_map.items() if k!='evaluation_id'}):
        raise ValueError('Operating map content identity differs')
    if case!=retained.scenario(bundle,case):
        raise ValueError('Forward scenario differs from bounded constructor')
    if (force_map.get('candidate_id')!=bundle['candidate_id']
        or force_map.get('motor_component_id')!=bundle['propulsion_component_id']
        or force_map.get('scenario_id')!=case['scenario_id']):
        raise ValueError('Map belongs to a different candidate, motor or scenario')
    bindings=dict(candidate_id=bundle['candidate_id'],bundle_definition_id=bundle.get('definition_id'),
        motor_component_id=bundle['propulsion_component_id'],scenario_id=case['scenario_id'],
        map_evaluation_id=force_map['evaluation_id'])
    if any(admission.get(key)!=expected for key,expected in bindings.items()):
        raise ValueError('Admission belongs to a different candidate, map or scenario')
    test=admission['test_only']
    if (test and force_map.get('evidence_kind')!='synthetic-method-test'
        or not test and (force_map.get('evidence_kind')!='verified-numerical-operating-map' or 'definition_id' not in bundle)):
        raise ValueError('Method and operating evidence scopes differ')
    return deepcopy(admission)


def forward(bundle,force_map,case,*,admission,current_source_sha256=None):
    if digest(retained.__file__)!=ANCESTOR_SHA256:
        raise ValueError('Retained motion ancestor changed; independent method comparison required')
    bundle=_bundle(bundle);spec=_brake_definition(bundle)
    admission=_gate(bundle,force_map,case,admission)
    result=dict(execution='not-run',admission=admission,predicted_stop_within_berth=False,available_motor_map_id=None,**FLAGS)
    if admission.get('admitted') is not True:return result
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
                    midv=max(0.,v+acceleration*h/2);midx=max(x,x+v*h/2+acceleration*h*h/8)
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
                if v==0. and a<=0.:
                    state='stalled';reason='Available launch force does not overcome declared resistance and grade at rest'
                    break
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
            if not 0<=sample['voltage_V']<=limits['maximum_voltage_V']+1e-8:state='electrical-limit';reason='map voltage magnitude outside admitted bus';break
            if state=='stalled':break
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
        source_sha256={PRODUCER:digest(__file__),ANCESTOR:ANCESTOR_SHA256},
        scope='Force-driven point train and scalar thermal/current envelopes; no native Chrono, flexible body, hardware WSP, faults or protected-service acceptance')
    return result


