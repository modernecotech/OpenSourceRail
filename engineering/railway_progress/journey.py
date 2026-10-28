"""Conditional force-driven mechanical launch/coast/brake research trajectories.

Industrial shaft ratings and proposed clamps/grips are capacity hypotheses. They
are NOT admitted operating maps. This integrator exposes that distinction while
allowing real coupled work/kinetic/brake/auxiliary calculations and failure tests.
"""
from math import isfinite,pi,fsum
from copy import deepcopy
from . import identity,digest,FLAGS
from . import alternatives

CODE='engineering/railway_progress/journey.py'


def scenario(**changes):
    s=dict(load='normal',mass_bound='upper',force_bound='lower',distance_m=2000.,grade_fraction=0.,wind_m_s=0.,
        ambient_C=50.,rolling_coefficient=.003,CdA_m2=8.,rho_air_kg_m3=1.2,
        acceleration_request_m_s2=.4,speed_cap_m_s=20.,service_deceleration_request_m_s2=.6,
        adhesion_coefficient=.12,condition='nominal',failed_banks=[],power_interrupt_at_s=None,
        emergency_at_m=None,dt_s=.1,maximum_s=360.,auxiliary_W_per_car=6200.)
    if set(changes)-set(s):raise ValueError('Explicit journey scenario variables required')
    s.update(deepcopy(changes))
    if s['load'] not in ('empty','normal','crowd-control') or s['mass_bound'] not in ('lower','upper') or s['force_bound'] not in ('lower','upper') or s['condition'] not in ('nominal','wet','low-friction'):
        raise ValueError('Declared mass/load/contact context required')
    for k,v in s.items():
        if k in ('load','mass_bound','force_bound','condition','failed_banks','power_interrupt_at_s','emergency_at_m'):continue
        if type(v) not in (float,int) or not isfinite(v):raise ValueError('Finite numeric scenario required: '+k)
    if s['distance_m'] not in (1500.,2000.) or not .025<=s['dt_s']<=.25 or not 0<s['maximum_s']<=600:
        raise ValueError('Bounded1.5/2km time-domain study required')
    if (s['acceleration_request_m_s2'],s['speed_cap_m_s'],s['service_deceleration_request_m_s2'])!=(.4,20.,.6):
        raise ValueError('This evaluator keeps the declared reference service requests')
    if not -.04<=s['grade_fraction']<=.04 or s['wind_m_s']<0 or not 0<s['adhesion_coefficient']<=1 or min(s['rolling_coefficient'],s['CdA_m2'],s['auxiliary_W_per_car'])<0 or s['rho_air_kg_m3']<=0:
        raise ValueError('Physical resistance/adhesion domains required')
    for k in ('power_interrupt_at_s','emergency_at_m'):
        if s[k] is not None and (type(s[k]) not in (float,int) or not isfinite(s[k]) or s[k]<0):raise ValueError('Nonnegative explicit fault event required')
    if not isinstance(s['failed_banks'],list):raise ValueError('Explicit failed-bank list required')
    s['scenario_id']=identity(s);return s


def evaluate(bundle,alternative,*,context=None):
    if bundle.get('definition_id')!=identity({k:v for k,v in bundle.items() if k!='definition_id'}):
        raise ValueError('Exact sealed cell/vehicle definition required')
    s=scenario(**({k:v for k,v in context.items() if k!='scenario_id'} if context else {}))
    if alternative['body_candidate_id']!=bundle['body_candidate_id'] or alternative['physical_definition']['service']['distance_m']!=s['distance_m'] or bundle['architecture_case']['physical_definition']['route']['station_spacing_m']!=s['distance_m']:
        raise ValueError('Exact body and physical station spacing required')
    if bundle.get('progress_architecture',{}).get('alternative_candidate_id')!=alternative['candidate_id']:
        raise ValueError('Canonical cell must bind this station-launch alternative')
    force=alternatives.force_model(alternative)
    bound=0 if s['mass_bound']=='lower' else 1
    force_index=0 if s['force_bound']=='lower' else 1
    passengers={'empty':0,'normal':276,'crowd-control':960}[s['load']]
    mass=bundle['mass_interval_kg_per_car'][bound]*6+75*passengers+alternative['added_counted_onboard_mass_kg']
    # Rope and tug kinetic energy is included where owned; delivered bearings,
    # gearbox/rotor spin-up, opposing drag and equipment missing masses stay open.
    coupled_external_mass=0.
    if alternative['kind']=='cable-launch-tug':
        coupled_external_mass=alternative['parameters']['tug_mass_kg']+alternative['mechanism']['rope_mass_kg']
    rotating=6*bundle['rotating_equivalent_kg_per_car'];effective=mass+rotating+coupled_external_mass
    brake=bundle['brake_definition'];R=brake['rotors']['radius_m'];discs=brake['discs_per_car']*6
    disc_mass=brake['counted_disc_stock_kg_per_car']*6
    max_pressure=brake['maximum_pressure_Pa_hypothesis']
    force_per_Pa=discs*brake['opposed_pistons_per_caliper_hypothesis']*pi*brake['piston_diameter_m_hypothesis']**2/4*brake['pad_friction_coefficient_hypothesis']*brake['effective_friction_radius_m']/R
    g=9.80665;D=s['distance_m'];x=v=t=pressure=0.;command_time=None;braking=False;trace=[]
    work={k:0. for k in ('traction','aerodynamic','rolling','gravity','brake','auxiliary')}
    maxima=dict(traction_N=0.,brake_N=0.,shaft_power_W=0.,speed_m_s=0.,acceleration_m_s2=0.,deceleration_m_s2=0.,coupler_bound_N=0.)
    result_state='time-budget';stopped=False;temperature=s['ambient_C'];last_save=-1.
    # Query once also validates named failed-bank indices on held/offline models.
    initial=force(0.,0.,condition=s['condition'],power_enabled=True,failed_banks=s['failed_banks'])
    if initial['force_N'] is None:
        r=dict(schema='osr-conditional-mechanical-journey/1',candidate_id=bundle['candidate_id'],alternative_candidate_id=alternative['candidate_id'],scenario=s,
            body_candidate_id=bundle['body_candidate_id'],bundle_definition_id=bundle['definition_id'],
            source_sha256={**bundle['source_sha256'],CODE:digest(__file__),**alternative['source_sha256']},
            execution='held-no-conditional-mechanical-model',conditional_numerical_arrival=False,admitted_operating_map=False,
            qualified_numerical_arrival=False,trajectory=[],reason=initial['state'],**FLAGS)
        r['evaluation_id']=identity(r);return r
    model=alternative['conditional_force_model'];events=[0.,500.]
    if s['emergency_at_m'] is not None:events.append(s['emergency_at_m'])
    if model['kind'].startswith('pinch'):
        events.extend(pos+104.5-end for bank,index,pos in model['positions'] for segment in model['train_drive_segments_m'] for end in segment)
    else:events.extend(model['launch_front_window_m'])
    events=sorted(set(events))
    while t<s['maximum_s']:
        remaining=D-x
        emergency=s['emergency_at_m'] is not None and x>=s['emergency_at_m']
        trigger=v*v/(2*.45)+v*(brake['pressure_response_delay_s_hypothesis']+brake['pressure_rise_time_s_hypothesis'])+2.
        if emergency or remaining<=trigger:
            braking=True
            if command_time is None:command_time=t
        drag=.5*s['rho_air_kg_m3']*s['CdA_m2']*(v+s['wind_m_s'])**2
        rolling=mass*g*s['rolling_coefficient'];gravity=mass*g*s['grade_fraction']
        resistance=drag+rolling+gravity
        step_dt=min(s['dt_s'],s['maximum_s']-t)
        if s['power_interrupt_at_s'] is not None and t<s['power_interrupt_at_s']<t+step_dt:
            step_dt=s['power_interrupt_at_s']-t
        power_on=(s['power_interrupt_at_s'] is None or t<s['power_interrupt_at_s']) and x+1e-9<500. and not braking and v<20.-1e-8
        # Conservative end-step speed enforces the nameplate power cap across
        # the step. A right-hand contact query avoids lingering at exit events.
        caps=force(x+1e-9,min(v+.4*step_dt,20.),condition=s['condition'],power_enabled=power_on,failed_banks=s['failed_banks'])
        capacity=caps['force_N'][force_index];requested=max(0.,effective*.4+resistance)
        traction=min(requested,capacity,max(0.,effective*(20.-v)/step_dt+resistance)) if power_on else 0.
        target_deceleration=min(.6,v*v/(2*max(remaining,.02))) if braking else 0.
        desired_brake=max(0.,effective*target_deceleration-resistance)
        requested_pressure=max_pressure if emergency else min(max_pressure,desired_brake/force_per_Pa)
        dt=step_dt
        active_command=braking and t-command_time>=brake['pressure_response_delay_s_hypothesis']
        if active_command:
            rate=max_pressure/brake['pressure_rise_time_s_hypothesis'];delta=requested_pressure-pressure
            pressure+=max(-rate*dt,min(rate*dt,delta))
        else:pressure=0.
        braking_force=min(pressure*force_per_Pa,mass*g*s['adhesion_coefficient'])
        a=(traction-resistance-braking_force)/effective
        if power_on or not braking and s['emergency_at_m'] is not None:
            next_event=next((z for z in events if z>x+1e-8),None)
            if next_event is not None and v*dt+.5*a*dt*dt>next_event-x:
                distance=next_event-x
                dt=(2*distance/(v+(max(0.,v*v+2*a*distance))**.5)) if abs(a)>1e-12 else distance/max(v,1e-12)
        if v<=1e-10 and a<=0:
            result_state='stalled';stopped=True;break
        if v+a*dt<0:dt=v/-a
        vn=max(0.,v+a*dt);dx=(v+vn)*dt/2
        # No reset/clamp of position or kinetic energy at the destination.
        for k,F in (('traction',traction),('aerodynamic',drag),('rolling',rolling),('gravity',gravity),('brake',braking_force)):work[k]+=F*dx
        work['auxiliary']+=6*s['auxiliary_W_per_car']*dt
        temperature=s['ambient_C']+work['brake']/(disc_mass*brake['steel_specific_heat_J_kg_K_hypothesis'])
        maxima['traction_N']=max(maxima['traction_N'],traction);maxima['brake_N']=max(maxima['brake_N'],braking_force)
        maxima['shaft_power_W']=max(maxima['shaft_power_W'],traction*(v+vn)/2)
        maxima['acceleration_m_s2']=max(maxima['acceleration_m_s2'],a);maxima['deceleration_m_s2']=max(maxima['deceleration_m_s2'],-a)
        # Conservative longitudinal force request for a cut behind a driven car;
        # actual local contact sharing and coupler fatigue require multibody data.
        maxima['coupler_bound_N']=max(maxima['coupler_bound_N'],traction+abs(resistance))
        x+=dx;t+=dt;v=vn
        maxima['speed_m_s']=max(maxima['speed_m_s'],v)
        if t-last_save>=.5 or v<1e-8:
            trace.append(dict(time_s=t,front_m=x,speed_m_s=v,acceleration_m_s2=a,traction_N=traction,
                available_conditional_force_N=capacity,brake_N=braking_force,brake_pressure_Pa=pressure,
                active_motor_count=caps.get('active_motor_count'),shaft_power_W=traction*v,
                adiabatic_counted_disc_temperature_C=temperature,grade_force_N=gravity));last_save=t
        if braking and v<1e-8:result_state='stopped';stopped=True;break
        if x>D+100:result_state='overrun';break
    kinetic=.5*effective*v*v
    net_work=work['traction']-work['aerodynamic']-work['rolling']-work['gravity']-work['brake']
    error=x-D;arrival=stopped and abs(error)<=.5 and s['emergency_at_m'] is None
    axle_weight=mass*g/24
    r=dict(schema='osr-conditional-mechanical-journey/1',candidate_id=bundle['candidate_id'],alternative_candidate_id=alternative['candidate_id'],
        bundle_definition_id=bundle['definition_id'],
        body_candidate_id=bundle['body_candidate_id'],scenario=s,execution=result_state,maturity='conditional-unqualified',
        mass_scope='Registry bound plus counted strip/attachments and passengers; delivered installed mass remains unknown',
        translating_train_mass_kg=mass,effective_mass_kg=effective,counted_rotor_equivalent_mass_kg=rotating,
        externally_coupled_rope_tug_mass_kg=coupled_external_mass,trajectory=trace,journey_time_s=t,final_front_m=x,
        stopping_error_m=error,final_speed_m_s=v,conditional_numerical_arrival=arrival,
        requested_service_screen_passed=arrival and maxima['speed_m_s']<=20.+1e-7 and maxima['acceleration_m_s2']<=.4+1e-7 and maxima['deceleration_m_s2']<=.6+1e-7,
        speed_cap_exceeded=maxima['speed_m_s']>20.+1e-7,
        qualified_numerical_arrival=False,admitted_operating_map=False,energy_J=work,kinetic_energy_J=kinetic,
        discrete_work_kinetic_residual_J=net_work-kinetic,adiabatic_counted_disc_temperature_C=temperature,
        brake_fade_or_temperature_limit_C=None,motor_current_A=None,motor_temperature_C=None,
        supply_voltage_V=None,maximums=maxima,axle_static_weight_hypothesis_N=axle_weight,
        axle_route_offsets_from_leading_nose_m=deepcopy(bundle['route_axle_offsets_from_leading_nose_m']),
        headway_target_s=120.,protected_occupancy_s=None,protected_headway_qualified=False,
        open_items=['Measured force/contact/handoff/slip, spin-up and opposing drag; conditional force is an upper-cap model',
            'Motor/inverter current and repeated electrothermal duty/cooling and protection',
            'Actual installed mass/rotating bearing inertia, drag and grade/site profile',
            'Actual brake pressure, friction/fade/adhesion/WSP, cooling and independent stopping review',
            'Local strip attachments/couplers, wheel-rail multibody reactions, sensing/HIL and protected recovery'],
        source_sha256={**bundle['source_sha256'],CODE:digest(__file__),**alternative['source_sha256']},**FLAGS)
    r['evaluation_id']=identity(r);return r
