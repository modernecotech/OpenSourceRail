"""Event-resolved analytical traction/brake demand, never available propulsion.

The six-car point-mass target uses actual translation and rotating-equivalent
mass separately. Powered windows are commanded *full-engagement leading-nose*
intervals; the caller must derive installed winding extents and count all motor,
energy and protection equipment. There is no partial-overlap force scaling.
Positive grade is uphill, consistent with station_rail.operations.profile.
"""
from math import isfinite
from pathlib import Path

from engineering.station_rail.common import digest, identity

PRODUCER='engineering/design_search/architecture_demand.py'
G=9.80665
FLAGS=dict(physical_journey_completed=False,complete_installed_mass=False,
    physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
    manufacturing_release=False,operating_release=False)


def _number(value,*,positive=False,nonnegative=False):
    return (type(value) in (int,float) and isfinite(value)
        and (not positive or value>0) and (not nonnegative or value>=0))


def _windows(value,distance):
    if not isinstance(value,(list,tuple)):raise ValueError('Explicit powered windows required; no hidden launch or booster')
    result=[]
    for pair in value:
        if not isinstance(pair,(list,tuple)) or len(pair)!=2 or any(not _number(x,nonnegative=True) for x in pair):raise ValueError('Finite ordered powered interval pairs required')
        lo,hi=map(float,pair)
        if lo>=hi or hi>distance:raise ValueError('Powered windows must lie within the declared route')
        if result and lo<result[-1][1]:raise ValueError('Powered windows must be sorted and nonoverlapping')
        if result and lo==result[-1][1]:result[-1][1]=hi
        else:result.append([lo,hi])
    return result


def _rk4(state,h,rate):
    k1=rate(state);k2=rate([x+h*k/2 for x,k in zip(state,k1)])
    k3=rate([x+h*k/2 for x,k in zip(state,k2)]);k4=rate([x+h*k for x,k in zip(state,k3)])
    return [x+h*(a+2*b+2*c+d)/6 for x,a,b,c,d in zip(state,k1,k2,k3,k4)]


def _root(function,h):
    """A sign-changing scalar event inside an already bounded step."""
    low=0.;high=h;f0=function(low)
    for _ in range(55):
        mid=(low+high)/2
        if (function(mid)>=0)==(f0>=0):low=mid
        else:high=mid
    return (low+high)/2


def demand(distance_m,mass_kg_per_car,rotating_mass_kg_per_car,*,powered_windows,
           cars=6,speed_cap_m_s=20.,acceleration_m_s2=.4,deceleration_m_s2=.6,
           grade=0.,headwind=0.,dt=.2,rolling_coefficient=.0025,
           constant_resistance_N_per_car=50.,aero_coefficient_N_s2_m2=1.8,
           maximum_runtime_s=600.,maximum_steps=10000):
    """Compute required launch/hold and independent mechanical-brake forces.

    No force limit, efficiency, adhesion, motor current or thermal capability is
    assumed to be available. Inside declared windows target net acceleration is
    imposed up to the cap; outside them only resistance and gravity act, except
    mechanical braking for downhill cap protection and the final stopping target.
    A completed target trajectory is not a physical journey or capacity result.
    """
    if any(not _number(v,positive=True) for v in (distance_m,mass_kg_per_car,speed_cap_m_s,acceleration_m_s2,deceleration_m_s2,dt,maximum_runtime_s)):
        raise ValueError('Positive finite distance, mass, speed, acceleration and time required')
    if any(not _number(v,nonnegative=True) for v in (rotating_mass_kg_per_car,headwind,rolling_coefficient,constant_resistance_N_per_car,aero_coefficient_N_s2_m2)) or not _number(grade):
        raise ValueError('Finite grade and nonnegative inertia, headwind and drag required')
    if type(cars) is not int or cars<1 or type(maximum_steps) is not int or not 1<=maximum_steps<=10000 or maximum_runtime_s>600 or dt>2:
        raise ValueError('Integer formation and bounded <=600s/10000-step demand calculation required')
    windows=_windows(powered_windows,distance_m);m=float(mass_kg_per_car);mr=float(rotating_mass_kg_per_car);me=m+mr
    cap=float(speed_cap_m_s);a=float(acceleration_m_s2);b=float(deceleration_m_s2)
    gravity=-m*G*grade
    inputs=dict(distance_m=distance_m,mass_kg_per_car=m,rotating_mass_kg_per_car=mr,effective_inertial_mass_kg_per_car=me,
        cars=cars,speed_cap_m_s=cap,acceleration_m_s2=a,deceleration_m_s2=b,powered_windows=windows,
        grade_fraction_uphill=grade,headwind_m_s=headwind,dt_s=dt,rolling_coefficient=rolling_coefficient,
        constant_resistance_N_per_car=constant_resistance_N_per_car,aero_coefficient_N_s2_m2=aero_coefficient_N_s2_m2,
        maximum_runtime_s=maximum_runtime_s,maximum_steps=maximum_steps)
    def resistance(v):return rolling_coefficient*m*G+constant_resistance_N_per_car+aero_coefficient_N_s2_m2*(v+headwind)**2
    def powered(x):return any(lo-1e-8<=x<hi-1e-8 for lo,hi in windows)
    def natural(v):return (gravity-resistance(v))/me
    def controls(v,mode):
        acceleration=a if mode=='powered-acceleration' else -b if mode=='final-braking' else 0. if mode in ('powered-cap-hold','downhill-cap-braking') else natural(v)
        force=me*acceleration+resistance(v)-gravity
        # An unpowered coast has exactly zero commanded traction/braking.
        if mode=='unpowered-coast':force=0.
        return acceleration,max(0.,force),max(0.,-force)
    def rates(mode):
        def rate(state):
            v=state[1];acc,traction,brake=controls(v,mode)
            return [v,acc,traction*v,brake*v,resistance(v)*v,gravity*v]
        return rate
    trace=[];events=[];state=[0.,0.,0.,0.,0.,0.];t=0.;steps=0;braking=False;reachable=False;reason=None
    peak_force=peak_power=peak_brake=peak_brake_power=peak_speed=0.
    phase_distance={};phase_time={}
    def record(mode):
        nonlocal peak_force,peak_power,peak_brake,peak_brake_power,peak_speed
        x,v=state[:2];acc,traction,brake=controls(v,mode)
        peak_force=max(peak_force,traction);peak_power=max(peak_power,traction*v)
        peak_brake=max(peak_brake,brake);peak_brake_power=max(peak_brake_power,brake*v);peak_speed=max(peak_speed,v)
        trace.append(dict(time_s=t,position_m=x,speed_m_s=v,phase=mode,within_powered_window=powered(x),
            acceleration_m_s2=acc,required_traction_force_N_per_car=traction,
            required_friction_brake_force_N_per_car=brake,resistance_N_per_car=resistance(v),gravity_force_N_per_car=gravity,
            required_traction_power_W_train=traction*v*cars,required_friction_brake_power_W_train=brake*v*cars,
            traction_mechanical_energy_J_train=state[2]*cars,friction_brake_energy_J_train=state[3]*cars,
            rolling_aero_dissipation_J_train=state[4]*cars,gravity_work_J_train=state[5]*cars))
    initial_mode='powered-acceleration' if powered(0.) else 'unpowered-coast';record(initial_mode)
    while steps<maximum_steps and t<maximum_runtime_s-1e-10:
        x,v=state[:2]
        if x>=distance_m-1e-7 and v<=1e-7:
            state[0]=float(distance_m);state[1]=0.;reachable=True;reason='analytical_target_requires_actual_drive_brake_energy_and_protection_evidence';break
        active=powered(x)
        if v<=1e-8 and not active and natural(0.)<=0:
            reason='stalled_off_powered_window';break
        margin=distance_m-x-v*v/(2*b)
        if not braking and margin<=1e-8:
            braking=True;events.append(dict(kind='final-brake-trigger',time_s=t,position_m=x,speed_m_s=v,stopping_margin_m=margin))
        if braking:
            mode='final-braking'
            if not active and me*(-b)+resistance(v)-gravity>1e-7:
                reason='constant_net_braking_target_requires_off_zone_traction';break
        elif active:mode='powered-acceleration' if v<cap-1e-9 else 'powered-cap-hold'
        elif v>=cap-1e-9 and natural(v)>0:mode='downhill-cap-braking'
        else:mode='unpowered-coast'
        # Record each control transition at its true event, preserving both
        # one-sided force demands rather than hiding instantaneous changes.
        if trace[-1]['phase']!=mode:record(mode)
        h=min(dt,maximum_runtime_s-t)
        if braking:h=min(h,v/b)
        rate=rates(mode)
        advance=lambda step:_rk4(state,step,rate)
        trial=advance(h);options=[]
        boundaries=[z for w in windows for z in w if z>x+1e-8]
        if boundaries and trial[0]>=min(boundaries):
            boundary=min(boundaries);options.append((_root(lambda s:advance(s)[0]-boundary,h),'powered-window-boundary'))
        if mode=='powered-acceleration' or (mode=='unpowered-coast' and natural(v)>0):
            if v<cap-1e-9 and trial[1]>=cap:options.append((_root(lambda s:advance(s)[1]-cap,h),'speed-cap'))
        if v>1e-8 and trial[1]<=0:options.append((_root(lambda s:advance(s)[1],h),'zero-speed'))
        if not braking and margin>1e-8 and distance_m-trial[0]-trial[1]**2/(2*b)<=0:
            options.append((_root(lambda s:distance_m-advance(s)[0]-advance(s)[1]**2/(2*b),h),'final-brake-trigger'))
        if not braking and trial[0]>=distance_m and x<distance_m-1e-8:
            options.append((_root(lambda s:advance(s)[0]-distance_m,h),'destination'))
        event=None
        if options:h,event=min(options,key=lambda p:p[0])
        if h<1e-11:
            reason='unresolved_zero_duration_event';break
        oldx=x;state=advance(h);t+=h;steps+=1
        if abs(state[1])<1e-8:state[1]=0.
        if state[1]==0. and abs(state[0]-distance_m)<1e-7:state[0]=float(distance_m)
        phase_distance[mode]=phase_distance.get(mode,0.)+state[0]-oldx;phase_time[mode]=phase_time.get(mode,0.)+h
        record(mode)
        if event:
            events.append(dict(kind=event,time_s=t,position_m=state[0],speed_m_s=state[1]))
            if event=='final-brake-trigger':braking=True
        if state[0]>=distance_m-1e-7 and state[1]<=1e-7 or state[0]>distance_m+1e-7:
            if state[1]<=1e-7:
                state[0]=float(distance_m);state[1]=0.;reachable=True;reason='analytical_target_requires_actual_drive_brake_energy_and_protection_evidence'
            else:reason='destination_crossed_without_stop'
            break
        if state[1]<-1e-8:
            reason='backward_motion_refused';break
    if reason is None:reason='bounded_runtime_or_step_budget_exhausted'
    kinetic=.5*me*state[1]**2;residual=state[2]-state[3]-state[4]+state[5]-kinetic
    scale=max(1.,abs(state[2]),abs(state[3]),abs(state[4]),abs(state[5]),kinetic)
    result=dict(schema='osr-architecture-analytical-demand/1',inputs=inputs,
        execution='interrupted' if reason=='bounded_runtime_or_step_budget_exhausted' else 'completed',
        evidence='analytical-demand-only',evidence_maturity='analytical',reachable=reachable,reachability='target-reached' if reachable else 'target-not-reached',reason=reason,
        numerical_validity='valid' if abs(residual)/scale<1e-6 else 'invalid',runtime_s=t,steps=steps,
        final_position_m=state[0],final_speed_m_s=state[1],destination_error_m=distance_m-state[0],peak_speed_m_s=peak_speed,
        peak_required_force_N_per_car=peak_force,peak_required_force_N_train=peak_force*cars,
        peak_required_power_W_per_car=peak_power,peak_required_power_W_train=peak_power*cars,
        peak_friction_brake_force_N_per_car=peak_brake,peak_friction_brake_power_W_train=peak_brake_power*cars,
        traction_mechanical_energy_J_per_car=state[2],traction_mechanical_energy_J_train=state[2]*cars,
        friction_brake_energy_J_per_car=state[3],friction_brake_energy_J_train=state[3]*cars,
        rolling_aero_dissipation_J_per_car=state[4],rolling_aero_dissipation_J_train=state[4]*cars,
        grade_work_J_per_car=state[5],grade_work_J_train=state[5]*cars,
        grade_work_convention='Signed work by gravity; positive grade is uphill',
        grade_potential_change_J_train=m*G*grade*state[0]*cars,
        final_translation_plus_rotor_kinetic_energy_J_train=kinetic*cars,
        energy_residual_J_per_car=residual,energy_residual_J_train=residual*cars,relative_energy_residual=abs(residual)/scale,
        phase_distance_m=phase_distance,phase_time_s=phase_time,trace=trace,events=events,
        available_force=None,actual_protection_headway_s=None,complete_installed_cost_USD=None,
        caveats=['Required forces are targets, not supplied LIM/wheel-traction or brake forces',
            'Independent mechanical brake demand assumes no demonstrated adhesion, WSP, fade or thermal capability',
            'No couplers, wheel/rail lateral motion, finite motor overlap, controller dynamics or electrical efficiency',
            'Constant grade and nonnegative headwind; no hidden intermediate propulsion'],
        source_sha256={PRODUCER:digest(Path(__file__)), 'engineering/station_rail/common.py':digest(Path(__file__).parents[1]/'station_rail/common.py')},**FLAGS)
    result['demand_id']=identity(result);return result
