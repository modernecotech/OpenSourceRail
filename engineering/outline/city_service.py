"""Actual-leg conditional city service with explicit traction research fallback."""
from copy import deepcopy
from math import ceil,floor,fsum,isfinite,sqrt
from pathlib import Path

from engineering.station_rail import ROOT,operations,braking
from engineering.station_rail.common import identity,digest
from engineering.design_search import compact_launch,line_benchmark_service as helper
from . import city_inputs

PRODUCER='engineering/outline/city_service.py'
FLAGS=city_inputs.FLAGS
_LOADED={PRODUCER:digest(__file__),city_inputs.PRODUCER:digest(city_inputs.__file__),
    helper.PRODUCER:digest(helper.__file__),'engineering/station_rail/operations.py':digest(operations.__file__),
    'engineering/station_rail/braking.py':digest(braking.__file__),
    'engineering/design_search/compact_launch.py':digest(compact_launch.__file__)}


def _number(value,name,zero=False):
    if type(value) not in (int,float) or not isfinite(value) or (value<0 if zero else value<=0):
        raise ValueError('Finite '+('nonnegative ' if zero else 'positive ')+name+' required')
    return value


def _leg(distance,mass,rotor,d,continuous=False):
    cap=d['speed_m_s'];a=d['acceleration_m_s2'];b=d['service_deceleration_m_s2'];j=d['jerk_m_s3']
    def stroke(v):return compact_launch.jerk_bound(v,a,j)['distance_m']+v*v/(2*b)
    if stroke(cap)>distance:
        low,high=0.,cap
        for _ in range(48):
            mid=(low+high)/2
            if stroke(mid)>distance:high=mid
            else:low=mid
        cap=low*(1-1e-12)
    bound=compact_launch.jerk_bound(cap,a,j)
    timing=operations.profile(distance,mass,speed_cap_m_s=cap,
        acceleration_m_s2=cap/bound['total_time_s'],service_deceleration_m_s2=b,
        rotating_equivalent_mass_kg_per_car=rotor,cars=6,loading='city-outline-declared-normal-mass')
    if not timing['reachable'] and not continuous:
        return dict(distance_m=distance,requested_speed_cap_m_s=d['speed_m_s'],adaptive_speed_cap_m_s=cap,
            status='reference-coast-infeasible',reference_profile=timing)
    # The equivalent profile supplies drag constants only for the exact jerk
    # work integral. Continuous cruise is a separate powered research hypothesis.
    work=helper._jerk_launch_work(timing,bound)
    cruise=max(0.,distance-bound['distance_m']-cap*cap/(2*b)) if continuous else 0.
    runtime=bound['total_time_s']+cruise/cap+cap/b if continuous else timing['runtime_s']
    constant=timing['constant_wheel_drag_N_per_car'];q=1.8
    energy=work['total_J_per_car']+((constant+q*cap*cap)*cruise if continuous else 0.)
    force=(mass+rotor)*a+constant+q*cap*cap
    stop_bound=operations.brake_bound(cap)
    return dict(distance_m=distance,requested_speed_cap_m_s=d['speed_m_s'],adaptive_speed_cap_m_s=cap,
        status='conditional-targets-complete',runtime_s=runtime,scheduled_runtime_s=runtime*(1+d['schedule_running_time_margin_fraction']),
        launch_time_s=bound['total_time_s'],launch_distance_m=bound['distance_m'],
        coast_distance_m=timing.get('coast_distance_m') if not continuous else 0.,powered_cruise_distance_m=cruise,
        braking_distance_m=cap*cap/(2*b) if continuous else timing['braking_distance_m'],
        braking_time_s=cap/b if continuous else timing['braking_time_s'],mechanical_work_kwh_train=energy*6/3.6e6,
        required_peak_force_N_train=force*6,required_peak_power_W_train=force*cap*6,
        jerk_bound=bound,reference_profile=timing,
        independent_braking_necessary_bound=stop_bound,
        braking_necessary_distance_fits_leg=stop_bound['stopping_distance_m'] is not None and stop_bound['stopping_distance_m']<=distance,
        actual_force_brake_thermal_maps_available=False,physical_accepted=False)


def evaluate(city_input,requirements,design,vehicle,root=ROOT):
    if city_input.get('input_id')!=identity({k:v for k,v in city_input.items() if k!='input_id'}):
        raise ValueError('City input identity differs')
    if vehicle.get('candidate_id')!=city_input['reference_candidate_ids']['candidate_id']:
        raise ValueError('City and vehicle candidate differ')
    if vehicle.get('evaluation_id')!=identity({k:v for k,v in vehicle.items() if k!='evaluation_id'}):
        raise ValueError('Vehicle input identity differs')
    formation=vehicle['physical_definition']['vehicle']
    if (formation['cars'],formation['body_length_m'],formation['fixed_seats_per_car'],formation['wheelchair_places_per_car'])!=(6,17.,44,2):
        raise ValueError('City service adapter requires its declared six17m/44+2 reference; a different formation needs an explicit evaluator')
    sources=dict(city_input['source_sha256'])
    for mapping in (vehicle.get('source_sha256',{}),_LOADED):
        for n,h in mapping.items():
            if n in sources and sources[n]!=h:raise ValueError('Mixed city service sources: '+n)
            sources[n]=h
    for n,h in sources.items():
        if digest(Path(root)/n)!=h:raise ValueError('City service source changed: '+n)
    r=deepcopy(requirements);d=deepcopy(design)
    defaults=dict(peak_demand_pphpd=4000.,planning_occupancy=.85,planning_availability_assumption=.99,
        maximum_headway_s=300.,operating_hours_per_day=18.)
    for k,v in defaults.items():r.setdefault(k,v)
    for k in defaults:_number(r[k],k)
    if r['planning_occupancy']>1 or r['planning_availability_assumption']>1 or r['operating_hours_per_day']>24:
        raise ValueError('Bounded occupancy/availability/hours required')
    d.setdefault('schedule_running_time_margin_fraction',.05)
    for k in ('speed_m_s','acceleration_m_s2','service_deceleration_m_s2','jerk_m_s3','aux_kw_per_car','charger_kw_per_car','charge_efficiency'):_number(d[k],k)
    for k in ('terminal_turnback_s','reserve_fraction','added_vehicle_mass_kg_per_car','schedule_running_time_margin_fraction'):_number(d[k],k,zero=True)
    if d['reserve_fraction']>1 or d['charge_efficiency']>1:raise ValueError('Bounded reserve/efficiency required')
    places=6*46;quantum=r.get('headway_quantum_s',10.)
    _number(quantum,'headway quantum')
    headway=floor(min(r['maximum_headway_s'],places*3600*r['planning_occupancy']*r['planning_availability_assumption']/r['peak_demand_pphpd'])/quantum)*quantum
    if headway<=0:raise ValueError('Demand cannot be represented by positive headway quantum')
    base_mass=vehicle['mass']['accounted_cap_loaded_kg_per_car']+d['added_vehicle_mass_kg_per_car']
    rotor=braking.rotating_stock(vehicle)['equivalent_inertial_mass_kg_per_car']
    train_length=6*17+5*.5;fin_offset=4.;records=[]
    for line in city_input['lines']:
        reference=[_leg(x['distance_m'],base_mass,rotor,d) for x in line['legs']]
        failed=[dict(leg_index=i,**x) for i,x in enumerate(reference) if x['status']!='conditional-targets-complete']
        fallback=bool(failed);extra_mass=_number(d.get('research_traction_added_mass_kg_per_car',1000.),'traction added mass') if fallback else 0.
        extra_rotor=_number(d.get('research_traction_equivalent_rotating_mass_kg_per_car',100.),'traction rotating inertia') if fallback else 0.
        mass=base_mass+extra_mass
        legs=[_leg(x['distance_m'],mass,rotor+extra_rotor,d,True) for x in line['legs']] if fallback else reference
        for x,source in zip(legs,line['legs']):x.update(source)
        initial_dwell=_number(r.get('dwell_s',35.),'dwell')
        net=d['charger_kw_per_car']*d['charge_efficiency']-d['aux_kw_per_car']
        if net<=0:raise ValueError('Declared charging cannot sustain hotel duty even at rest')
        need=[ceil(d['aux_kw_per_car']*x['scheduled_runtime_s']/net) for x in legs]
        stop_dwell=[];n=len(line['stops']);ring=line['shape']=='ring'
        for i in range(n):
            incoming=[need[k] for k in ((i-1)%len(legs),i%len(legs))] if ring else [need[k] for k in (i-1,i) if 0<=k<len(need)]
            stop_dwell.append(max(initial_dwell,line['stops'][i].get('dwell_s',initial_dwell),*incoming))
        moving=fsum(x['scheduled_runtime_s'] for x in legs)
        turnback=max(d['terminal_turnback_s'],stop_dwell[0],stop_dwell[-1]) if not ring else 0.
        dwell_total=fsum(stop_dwell) if ring else fsum(stop_dwell[1:-1])
        one=moving+dwell_total
        cycle=one if ring else 2*(one+turnback)
        active=(2*ceil(cycle/headway) if ring else ceil(cycle/headway));spare=ceil(active*d['reserve_fraction']);total=active+spare
        charge=fsum(stop_dwell) if ring else dwell_total+turnback
        gross=d['charger_kw_per_car']*charge/3600
        hotel=d['aux_kw_per_car']*(moving+charge)/3600
        maximum_force=max(x['required_peak_force_N_train'] for x in legs)
        maximum_power=max(x['required_peak_power_W_train'] for x in legs)
        max_launch=max(x['launch_distance_m'] for x in legs)
        tail=max(helper._tail_clearance(train_length,x['adaptive_speed_cap_m_s'],d['acceleration_m_s2'],d['jerk_m_s3']) for x in legs)
        resource=max(x['braking_time_s']+max(stop_dwell)+tail for x in legs)
        mechanisms=['powered-axle-continuous-research'] if fallback else ['station-launch-reference']
        config=dict(kind=mechanisms[0],reference_vehicle_candidate_id=vehicle['candidate_id'],
            city_input_id=city_input['input_id'],line_id=line['line_id'],
            added_traction_mass_kg_per_car=extra_mass,added_rotating_equivalent_mass_kg_per_car=extra_rotor,
            added_traction_mass_bounds_kg_per_car=[.7*extra_mass,extra_mass,1.5*extra_mass],
            traction_motors_per_car=4 if fallback else 0,
            traction_rated_kw_per_car=(maximum_power/6+(mass*operations.G*.02*d['speed_m_s']))/1000/.85 if fallback else 0.,
            continuous_feed_route_m=line['route_m'] if fallback else 0.,
            collector_protection_and_rescue_required=True,independent_friction_braking_required=True,
            actual_available_force_map=None,physical_reference_changed=False,
            interpretation='New calculated research equipment/mass/energy configuration; no reference propulsion qualification inherited' if fallback else 'Conditional station launch requirements; actual drive and braking still unknown')
        config['research_configuration_id']=identity(config)
        req={**r,'route_km':line['route_m']/1000,'stations':n,'trackways':2,'cars_per_train':6,
            'fixed_seats_per_car':44,'wheelchair_places_per_car':2,'headway_s':headway,'dwell_s':max(stop_dwell)}
        chosen={**d,'terminal_turnback_s':turnback,'research_traction_added_mass_kg_per_car':extra_mass}
        service=dict(schema='osr-city-actual-leg-service/1',requirements=req,design=chosen,
            reference_vehicle_candidate_id=vehicle['candidate_id'],reference_vehicle_evaluation_id=vehicle['evaluation_id'],
            provisional_normal_mass_kg_per_car=mass,accounted_reference_mass_kg_per_car=vehicle['mass']['accounted_cap_loaded_kg_per_car'],
            added_vehicle_mass_reserve_kg_per_car=d['added_vehicle_mass_kg_per_car'],added_research_traction_mass_kg_per_car=extra_mass,
            rotating_equivalent_mass_kg_per_car=rotor+extra_rotor,installed_mass_complete=False,
            normal_places_per_train=places,capacity_pphpd=places*3600/headway,
            planning_usable_capacity_pphpd=places*3600/headway*r['planning_occupancy']*r['planning_availability_assumption'],
            one_way_s=one,round_trip_s=cycle,cycle_per_direction_s=cycle,fleet_direction_multiplier=2 if ring else 1,
            active_trainsets=active,spare_trainsets=spare,total_trainsets=total,totalcars=6*total,
            train_km_per_day=2*3600/headway*r['operating_hours_per_day']*line['operational_route_m']/1000,
            departure_sites=2*len(legs),boarding_edges=2*n,minimum_turnback_positions_per_end=max(1,ceil(turnback/headway)) if not ring else 0,
            terminal_additional_positions=2*max(0,ceil(turnback/headway)-1) if not ring else 0,
            peak_train_force_N=maximum_force,peak_train_mechanical_power_W=maximum_power,
            mechanical_work_kwh_per_departure=fsum(x['mechanical_work_kwh_train'] for x in legs)/len(legs),
            mechanical_work_kwh_per_direction_trip=fsum(x['mechanical_work_kwh_train'] for x in legs),
            departures_per_day=2*3600/headway*r['operating_hours_per_day']*len(legs),
            jerk_launch_distance_m=max_launch,jerk_full_train_fin_launch_envelope_m=max_launch+train_length-2*fin_offset,
            train_length_m=train_length,tail_clearance_s_jerk_bound=tail,berth_resource_s=resource,
            berth_headway_necessary_screen='pass' if resource<=headway else 'parallel-protected-berths-required',
            minimum_parallel_berth_resources=ceil(resource/headway),stop_dwell_s=stop_dwell,
            auxiliary=dict(aux_kw_per_car=d['aux_kw_per_car'],requested_charger_kw_per_car=d['charger_kw_per_car'],
                charge_input_kwh_per_car_per_half_cycle=gross,hotel_energy_kwh_per_car_per_half_cycle=hotel,
                energy_margin_kwh_per_car_per_half_cycle=gross*d['charge_efficiency']-hotel,
                energy_balance_screen='pass' if gross*d['charge_efficiency']>=hotel-1e-9 else 'fail',
                actual_charge_map_available=False,transient_SOC_verified=False,thermal_qualified=False),
            shift_info=dict(production_shifts_per_day=2,construction_shifts_per_day=2,
                operations_shifts_per_day=2 if r['operating_hours_per_day']<=18 else 3,
                operating_hours_per_day=r['operating_hours_per_day'],
                operations_hours_per_shift=r['operating_hours_per_day']/(2 if r['operating_hours_per_day']<=18 else 3)),
            actual_available_force_map=None,physical_journey_completed=False,grade_fraction_hypothesis=0.,
            schedule_running_time_margin_fraction=d['schedule_running_time_margin_fraction'],
            timetable_qualified=False,independent_braking_qualified=False,**FLAGS)
        service['evaluation_id']=identity(service)
        record=dict(line_id=line['line_id'],shape=line['shape'],requirements=req,design=chosen,
            service=service,propulsion_hypothesis=config,legs=legs,known_reference_failures=failed,
            interface_holds=[dict(kind='reference-train-platform-spacing',distance_m=x['distance_m'],
                train_length_m=train_length,platform_length_m=d.get('platform_length_m',120.),
                reason='Reference train/platform envelopes overlap adjacent stops; revise stop/formation/layout before physical acceptance')
                for x in legs if x['distance_m']<max(train_length,d.get('platform_length_m',120.))],
            source_schedule_used_as_demand=False,physical_accepted=False)
        record['evaluation_id']=identity(record);records.append(record)
    result=dict(schema='osr-city-service-outline/1',city_input_id=city_input['input_id'],line_services=records,
        assumptions=dict(peak_demand_pphpd_per_line=r['peak_demand_pphpd'],demand_source=r.get('demand_source','declared-planning-example-not-surveyed'),
            planning_occupancy=r['planning_occupancy'],planning_availability_assumption=r['planning_availability_assumption'],
            survey_demand_available=bool(city_input['od']),availability_achieved=False,
            level_track_zero_wind_only=True,actual_grades_unknown=True,adaptive_dwell_and_turnback_for_nominal_hotel_balance=True),
        summary=dict(lines=len(records),total_trainsets=sum(x['service']['total_trainsets'] for x in records),
            totalcars=sum(x['service']['totalcars'] for x in records),reference_coast_failure_legs=sum(len(x['known_reference_failures']) for x in records),
            powered_axle_research_lines=sum(x['propulsion_hypothesis']['kind']=='powered-axle-continuous-research' for x in records)),
        source_sha256=dict(sorted(sources.items())),**FLAGS)
    result['evaluation_id']=identity(result);return result
