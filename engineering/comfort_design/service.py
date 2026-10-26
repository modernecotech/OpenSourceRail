"""Two-minute comfort service: unpowered coast, station resources and protection.

The moving profiles solve a declared resistance hypothesis. They are neither
levitated-train trajectories nor measured brake curves. Native replay exercises
the existing protection contract with its explicitly synthetic detector/gap data.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip
import json
import math
import os
import subprocess
import tomllib

from . import ROOT, FLAGS
from engineering.ferrite_maglev import line_capacity, station

SCHEMA='osr-comfort-two-minute-service/1'
CITY='cities/catalogue/west-asia/Iraq/Baghdad/engineering/maglev/summary.json'
HEADWAY=120.
CARS=6
PASSENGERS=46
ZONE_LENGTHS=(350.,450.,600.)
DRAG_CONSTANTS=(250.,500.,1000.)
SOURCE_FILES=('engineering/comfort_design/__init__.py','engineering/comfort_design/brief.json','engineering/ferrite_maglev/line_capacity.py',
    'engineering/ferrite_maglev/line-capacity.toml','engineering/ferrite_maglev/station.py',
    'engineering/ferrite_maglev/station.toml',CITY)


def encoded(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def identity(value):return sha256(encoded(value)).hexdigest()


def _positive(value,name):
    if type(value) not in (int,float) or not math.isfinite(value) or value<=0:
        raise ValueError('finite positive '+name+' required')
    return float(value)


def sources(root=ROOT,*,native=False):
    root=Path(root)
    names=set(SOURCE_FILES)
    if native:
        names|={'Cargo.toml','Cargo.lock','rust-toolchain.toml'}
        for crate in ('osr-core','osr-interlocking'):
            names.add('crates/'+crate+'/Cargo.toml')
            names.update(p.relative_to(root).as_posix() for p in (root/'crates'/crate/'src').rglob('*.rs'))
        names.add('crates/osr-interlocking/examples/line_capacity_replay.rs')
    result={name:sha256((root/name).read_bytes()).hexdigest() for name in sorted(names)}
    result['engineering/comfort_design/service.py']=sha256(Path(__file__).read_bytes()).hexdigest()
    return result


def _vehicle(value):
    for key in ('candidate_id','body_candidate_id','magnet_component_id'):
        if not isinstance(value.get(key),str) or len(value[key])!=64:
            raise ValueError('explicit candidate/body/magnet identity required')
    tare=_positive(value['mass']['accounted_tare_kg_per_car'],'accounted tare')
    loaded=_positive(value['mass']['accounted_cap_loaded_kg_per_car'],'accounted loaded mass')
    if not math.isclose(loaded-tare,75*PASSENGERS,abs_tol=1e-6):
        raise ValueError('service requires exact46-person75kg comparison load')
    return tare,loaded


def motion_profile(distance_m,speed_cap_m_s,acceleration_m_s2,deceleration_m_s2,
                   car_mass_kg,constant_drag_N_per_car=1000.,quadratic_drag_N_per_car=1.8):
    """Exact constant net launch/brake, analytic unpowered C+Qv² coasting.

    Find arrival speed from distance, rather than keep coast speed constant.
    C is an uncertain *force*, so a lighter train can coast less far at equal
    speed under this retained hypothesis. This effect is deliberately visible.
    """
    D,V,a,b,m,C,Q=(_positive(x,n) for x,n in zip(
        (distance_m,speed_cap_m_s,acceleration_m_s2,deceleration_m_s2,car_mass_kg,
         constant_drag_N_per_car,quadratic_drag_N_per_car),
        ('distance','speed','acceleration','deceleration','mass','constant drag','quadratic drag')))
    if b<=(C+Q*V*V)/m:
        raise ValueError('declared braking must exceed drag-only deceleration for this fixture')
    peak=min(V,math.sqrt(2*D/(1/a+1/b)))
    d_acc=peak*peak/(2*a)
    def coast_distance(end):return m/(2*Q)*math.log((C+Q*peak*peak)/(C+Q*end*end))
    max_coast=coast_distance(0.)
    common=dict(distance_m=D,speed_cap_m_s=V,peak_speed_m_s=peak,acceleration_m_s2=a,
        deceleration_m_s2=b,car_mass_kg=m,constant_drag_N_per_car=C,
        quadratic_drag_N_per_car_per_m_s_squared=Q,acceleration_distance_m=d_acc,
        maximum_unpowered_coast_distance_m=max_coast,
        maximum_reachable_distance_before_stop_m=d_acc+max_coast,
        resistance_is_measured=False,force_map_driven=False,physical_trajectory=False,
        jerk_limits_modelled=False,grade=0.,coast_powered=False)
    if D>d_acc+max_coast+1e-8:
        return dict(common,engineering_screen='fail',failure='coasts-to-rest-before-receiving-station',
            runtime_s=None,arrival_speed_before_braking_m_s=None,braking_distance_m=None,
            coast_distance_m=max_coast,coast_duration_s=None,
            shortfall_m=D-d_acc-max_coast)
    lo,hi=0.,peak
    for _ in range(70):
        mid=(lo+hi)/2
        if d_acc+coast_distance(mid)+mid*mid/(2*b)>D:lo=mid
        else:hi=mid
    arrival=(lo+hi)/2
    d_coast=coast_distance(arrival);d_brake=arrival*arrival/(2*b)
    t_acc=peak/a;t_brake=arrival/b
    t_coast=m/math.sqrt(C*Q)*(math.atan(peak*math.sqrt(Q/C))-math.atan(arrival*math.sqrt(Q/C)))
    runtime=t_acc+t_coast+t_brake
    initial_ke=.5*m*peak*peak;arrival_ke=.5*m*arrival*arrival
    # Exact coast work follows the differential kinetic-energy balance.
    drag_coast=initial_ke-arrival_ke
    launch_drag=C*d_acc+Q*peak**4/(4*a)
    brake_drag=C*d_brake+Q*arrival**4/(4*b)
    station_launch=initial_ke+launch_drag
    recoverable=max(0.,arrival_ke-brake_drag)
    return dict(common,engineering_screen='conditional-kinematic-pass',failure=None,
        arrival_speed_before_braking_m_s=arrival,braking_distance_m=d_brake,coast_distance_m=d_coast,
        acceleration_duration_s=t_acc,coast_duration_s=t_coast,braking_duration_s=t_brake,runtime_s=runtime,
        distance_residual_m=d_acc+d_coast+d_brake-D,
        launch_mechanical_kWh_per_train=6*station_launch/3.6e6,
        coast_drag_work_kWh_per_train=6*drag_coast/3.6e6,
        arrival_kinetic_kWh_per_train=6*arrival_ke/3.6e6,
        brake_drag_work_kWh_per_train=6*brake_drag/3.6e6,
        theoretically_recoverable_mechanical_kWh_per_train=6*recoverable/3.6e6,
        net_station_work_kWh_per_train=6*(station_launch-recoverable)/3.6e6,
        energy_balance_residual_J_per_car=station_launch-recoverable-launch_drag-drag_coast-brake_drag,
        actual_electrical_energy_kWh=None)


def position_at(profile,time_s):
    if profile['runtime_s'] is None:raise ValueError('reaching motion profile required')
    t=min(max(float(time_s),0.),profile['runtime_s']);v=profile['peak_speed_m_s']
    a=profile['acceleration_m_s2'];b=profile['deceleration_m_s2'];ta=profile['acceleration_duration_s']
    tc=profile['coast_duration_s'];D=profile['distance_m']
    if t<=ta:return dict(position_m=.5*a*t*t,speed_m_s=a*t)
    if t<ta+tc:
        C=profile['constant_drag_N_per_car'];Q=profile['quadratic_drag_N_per_car_per_m_s_squared'];m=profile['car_mass_kg']
        w=max(0.,math.sqrt(C/Q)*math.tan(math.atan(v*math.sqrt(Q/C))-(t-ta)*math.sqrt(C*Q)/m))
        x=profile['acceleration_distance_m']+m/(2*Q)*math.log((C+Q*v*v)/(C+Q*w*w))
        return dict(position_m=x,speed_m_s=w)
    left=profile['runtime_s']-t
    return dict(position_m=D-.5*b*left*left,speed_m_s=b*left)


def time_at_position(profile,position_m):
    x=min(max(float(position_m),0.),profile['distance_m'])
    a=profile['acceleration_m_s2'];b=profile['deceleration_m_s2']
    if x<=profile['acceleration_distance_m']:return math.sqrt(2*x/a)
    before_brake=profile['distance_m']-profile['braking_distance_m']
    if x>=before_brake:return profile['runtime_s']-math.sqrt(2*(profile['distance_m']-x)/b)
    C=profile['constant_drag_N_per_car'];Q=profile['quadratic_drag_N_per_car_per_m_s_squared'];m=profile['car_mass_kg'];v=profile['peak_speed_m_s']
    w=math.sqrt(max(0.,((C+Q*v*v)*math.exp(-2*Q*(x-profile['acceleration_distance_m'])/m)-C)/Q))
    return profile['acceleration_duration_s']+m/math.sqrt(C*Q)*(math.atan(v*math.sqrt(Q/C))-math.atan(w*math.sqrt(Q/C)))


def stopping_distance_m(speed_m_s,brake_m_s2=.6,*,grade_permille=0,reaction_s=.2):
    return line_capacity.stopping_envelope_mm(math.ceil(speed_m_s*1000),
        deceleration_mmps2=round(brake_m_s2*1000),reaction_ms=round(reaction_s*1000),
        maximum_acceleration_mmps2=1000,downhill_permille=grade_permille)/1000.


def motor_zone(profile,length_m,train_length_m,dwell_s):
    length=_positive(length_m,'winding length');L=_positive(train_length_m,'train length')
    left=-L-profile['braking_distance_m']-5.;right=profile['acceleration_distance_m']+5.
    centre=(left+right)/2;start=centre-length/2;end=centre+length/2
    pitch=17.5;band=12.;offset=2.5
    def overlap(front):
        return sum(max(0.,min(front-offset-i*pitch,end)-max(front-offset-band-i*pitch,start)) for i in range(CARS))
    m=profile['car_mass_kg'];C=profile['constant_drag_N_per_car'];Q=profile['quadratic_drag_N_per_car_per_m_s_squared']
    peaks=[];loss=False
    for direction,duration in (('launch',profile['acceleration_duration_s']),('receiving',profile['braking_duration_s'])):
        for k in range(101):
            t=duration*k/100
            if direction=='launch':
                v=profile['acceleration_m_s2']*t;x=.5*profile['acceleration_m_s2']*t*t
                force=CARS*(m*profile['acceleration_m_s2']+C+Q*v*v)
            else:
                v=profile['arrival_speed_before_braking_m_s']-profile['deceleration_m_s2']*t
                x=-v*v/(2*profile['deceleration_m_s2'])
                force=CARS*max(0.,m*profile['deceleration_m_s2']-C-Q*v*v)
            active=overlap(x)
            if active<=1e-9 and force>1:loss=True;continue
            peaks.append(dict(phase=direction,time_s=t,front_relative_station_m=x,speed_m_s=v,
                overlapping_band_m=active,required_force_N=force,
                required_force_density_N_per_active_band_m=force/active,
                required_force_N_per_equivalent_fully_engaged_car=force*band/active,
                mechanical_power_kW=force*v/1000.))
    entry=time_at_position(profile,profile['distance_m']+start)-profile['runtime_s']
    exit=time_at_position(profile,L+end+5.)
    occupied=-entry+dwell_s+exit+2.
    def crossing(offset):
        return (time_at_position(profile,profile['distance_m']+offset)-profile['runtime_s']
                if offset<0 else dwell_s+time_at_position(profile,offset))
    sections=[]
    for index in range(math.ceil(length/12.5)):
        x0=start+index*12.5;x1=min(end,x0+12.5)
        sections.append(dict(section=index,start_m=x0,end_m=x1,
            front_entry_before_arrival_s=crossing(x0),
            rear_clear_relative_arrival_s=crossing(x1+L+5.)+2.,
            occupation_interval_s=crossing(x1+L+5.)+2.-crossing(x0)))
    platform_interval=(dwell_s+time_at_position(profile,L+5.)+2.
        -(time_at_position(profile,profile['distance_m']-L-5.)-profile['runtime_s']))
    sectioned=max(platform_interval,max(r['occupation_interval_s'] for r in sections))
    physical=dict(schema='osr-comfort-station-winding/1',length_m=length,start_m=start,end_m=end,
        car_magnetic_band_m=band,station_datum='Stopped train nose; +x direction of travel',
        sections_per_direction=math.ceil(length/12.5),electrical_section_m=12.5,
        motor_faces_per_direction=2,directions=2,installed_direction_metres=2*length,
        installed_motor_face_metres=4*length,full_train_length_m=L,
        receiving_and_launch_use_same_winding=True,
        power_resource_architecture='independently-addressed12.5m-sections',
        minimum_concurrent_train_phase_current_branches_per_direction=2,
        active_section_ownership='Positive identified full-train-tail clearance; independent phase/current routing required')
    exclusive=dict(physical,power_resource_architecture='one-exclusive-whole-zone-lease',
        minimum_concurrent_train_phase_current_branches_per_direction=1)
    return dict(physical,station_id=identity(physical),full_engagement_bound_m=right-left,
        geometry_full_engagement=length>=right-left-1e-9,
        force_density_requirement_N_m=max((r['required_force_density_N_per_active_band_m'] for r in peaks),default=None),
        required_peak_force_per_fully_engaged_car_N=max((r['required_force_N_per_equivalent_fully_engaged_car'] for r in peaks),default=None),
        required_peak_train_mechanical_kW=max((r['mechanical_power_kW'] for r in peaks),default=None),
        no_powered_overlap_during_required_force=loss,
        force_samples=[max((r for r in peaks if r['phase']==p),key=lambda r:r['required_force_density_N_per_active_band_m']) for p in ('launch','receiving') if any(r['phase']==p for r in peaks)],
        whole_zone_entry_before_arrival_s=entry,whole_zone_tail_clear_after_departure_s=exit,
        release_allowance_s=2.,minimum_nominal_resource_interval_s=sectioned,
        nominal_120_s_margin_s=HEADWAY-sectioned,
        nominal_resource_screen='pass' if sectioned<=HEADWAY and not loss else 'fail',
        addressed_sections=sections,platform_occupation_interval_s=platform_interval,
        exclusive_control_station_id=identity(exclusive),exclusive_control_physical_definition=exclusive,
        whole_zone_exclusive_minimum_interval_s=occupied,
        whole_zone_exclusive_120_s_margin_s=HEADWAY-occupied,
        independently_addressed_hardware_and_phase_routing_qualified=False,
        phase_routing_requirements=[
            'Each energised section has one identified train owner and compatible phase/current command',
            'Full-tail proof releases a section; a future predicted position cannot release it',
            'Two independent train phase/current branches per direction; no shared single phase command for simultaneous trains',
            'Dead time, switch isolation, failed section de-energisation and bus fault containment remain to be verified',
            'Brake/capture remain available without receiving grid power; not demonstrated by this scheduler'],
        branch_count_scope='Two independent train branches are proposed for concurrent or disturbed receiving/launch; observed nominal demand can be one.',
        safe_120_s_headway_verified=False,actual_force_current_voltage_thermal_envelope=None,
        peak_scope='Required mechanical force/density under declared trajectory and drag, not available thrust',
        guaranteed_independent_braking_verified=False,station_outputs_qualified=False)


def _resource_events(profile,zone,dwell_s,*,delay_first_dwell_s=0.,architecture='section-addressed'):
    T=profile['runtime_s'];D=profile['distance_m'];events=[]
    for train in range(3):
        delayed=0.
        for stop in range(1,4):
            arrival=train*HEADWAY+(stop-1)*(T+dwell_s)+T+delayed
            extra=delay_first_dwell_s if train==0 and stop==1 else 0.
            departure=arrival+dwell_s+extra
            for resource,offset_in,offset_out in (
                ('whole-station-winding',zone['whole_zone_entry_before_arrival_s'],zone['whole_zone_tail_clear_after_departure_s']+2.),
                ('platform',time_at_position(profile,D-109.5)-T,time_at_position(profile,109.5)+2.),
                ('receiving-power-group',-profile['braking_duration_s'],0.),
                ('launch-power-group',0.,profile['acceleration_duration_s'])):
                begins=departure if resource=='launch-power-group' else arrival+offset_in
                ends=arrival if resource=='receiving-power-group' else departure+offset_out
                events.append(dict(train=train+1,station=stop,resource=resource,start_s=begins,end_s=ends,
                    rear_clearance_included=resource in ('whole-station-winding','platform'),
                    enforced=resource!='whole-station-winding' or architecture=='whole-zone-exclusive'))
            if architecture=='section-addressed':
                def crossing(offset):
                    return (arrival+time_at_position(profile,D+offset)-T if offset<0
                            else departure+time_at_position(profile,offset))
                for section in zone['addressed_sections']:
                    events.append(dict(train=train+1,station=stop,resource='winding-section-'+str(section['section']),
                        start_s=crossing(section['start_m']),end_s=crossing(section['end_m']+104.5+5.)+2.,
                        rear_clearance_included=True,enforced=True))
            delayed+=extra
    conflicts=[];minimum_gap=None
    # Conflict arrays are public evaluation inputs. A hash-seeded set order
    # would give identical physics a different evaluation identity per process.
    for resource in sorted({(r['station'],r['resource']) for r in events if r['enforced']}):
        rows=sorted([r for r in events if (r['station'],r['resource'])==resource and r['enforced']],key=lambda r:r['start_s'])
        for first,second in zip(rows,rows[1:]):
            gap=second['start_s']-first['end_s'];minimum_gap=gap if minimum_gap is None else min(minimum_gap,gap)
            if gap< -1e-8:conflicts.append(dict(station=resource[0],resource=resource[1],lead_train=first['train'],following_train=second['train'],overlap_s=-gap))
    maximum_power_branches=0
    for stop in range(1,4):
        boundaries=[]
        for r in events:
            if r['station']==stop and r['resource'] in ('receiving-power-group','launch-power-group'):
                boundaries.extend(((r['start_s'],1),(r['end_s'],-1)))
        active=0
        for _,change in sorted(boundaries):active+=change;maximum_power_branches=max(maximum_power_branches,active)
    return dict(trains=3,station_arrivals_per_train=3,events=events,conflicts=conflicts,
        minimum_resource_gap_s=minimum_gap,screen='pass' if not conflicts else 'fail',
        architecture=architecture,maximum_simultaneous_train_power_branches_per_direction=maximum_power_branches,
        delay_first_dwell_s=delay_first_dwell_s,dispatch_recovery_required=bool(conflicts),
        departure_headway_s=HEADWAY,phase_tracking_and_control_latency_qualified=False,
        physical_detectors_and_releases_qualified=False)


def _fleet(root,profile,dwell_s,tare):
    data=json.loads((Path(root)/CITY).read_bytes());rows=[]
    for line in data['lines']:
        # Recalculate every retained mainline event at this proposal's launch
        # speed/drag. Terminal loop duties remain separate retained quantities.
        events=line['duty']['arrival_events_per_circuit'];seconds=0.;failed=[];main_stops=loops=0
        proposal_seconds=0.;proposal_failure=[];additional_sites=set();proposal_main_stops=0
        zone_counts={str(int(z)):0 for z in ZONE_LENGTHS};zone_failures=[]
        for ev in events:
            if ev['terminal_loop_allowance']:
                seconds+=ev['moving_seconds']+dwell_s;proposal_seconds+=ev['moving_seconds']+dwell_s;loops+=1
            else:
                p=motion_profile(ev['distance_m'],profile['speed_cap_m_s'],.4,.6,profile['car_mass_kg'],profile['constant_drag_N_per_car'])
                if p['runtime_s'] is None:failed.append(dict(distance_m=ev['distance_m'],reason=p['failure']))
                else:seconds+=p['runtime_s']+dwell_s
                main_stops+=1
                pieces=max(1,math.ceil(ev['distance_m']/2000.))
                split=motion_profile(ev['distance_m']/pieces,profile['speed_cap_m_s'],.4,.6,
                    profile['car_mass_kg'],profile['constant_drag_N_per_car'])
                if split['runtime_s'] is None:proposal_failure.append(dict(distance_m=ev['distance_m']/pieces,reason=split['failure']))
                else:
                    proposal_seconds+=pieces*(split['runtime_s']+dwell_s)
                    needed=[motor_zone(split,z,104.5,dwell_s) for z in ZONE_LENGTHS]
                    passing=[z for z in needed if z['geometry_full_engagement'] and z['nominal_resource_screen']=='pass']
                    if passing:
                        chosen=min(passing,key=lambda z:z['length_m']);zone_counts[str(int(chosen['length_m']))]+=pieces
                    else:zone_failures.append(dict(distance_m=ev['distance_m']/pieces,reason='No complete-engagement library winding/resource survivor'))
                proposal_main_stops+=pieces
                first,last=ev['origin_station'],ev['destination_station']
                for k in range(1,pieces):
                    fraction=k/pieces if first<last else 1-k/pieces
                    additional_sites.add((min(first,last),max(first,last),round(fraction,12)))
        peak=math.ceil(seconds/HEADWAY) if not failed else None
        spare=math.ceil(.12*peak) if peak is not None else None
        cold=1 if peak is not None else None
        total=peak+spare+cold if peak is not None else None
        old=line['fleet']['total']
        proposal_peak=math.ceil(proposal_seconds/HEADWAY) if not proposal_failure else None
        proposal_spare=math.ceil(.12*proposal_peak) if proposal_peak is not None else None
        proposal_total=proposal_peak+proposal_spare+1 if proposal_peak is not None else None
        rows.append(dict(line=line['line'],retained_total_trainsets=old,
            retained_headway_s=line['selected_peak_headway_seconds'],
            proposed_headway_s=HEADWAY,proposed_peak_trainsets=peak,proposed_spare_trainsets=spare,
            proposed_cold_reserve_trainsets=cold,proposed_total_trainsets=total,
            calculated_circuit_s=seconds if not failed else None,mainline_arrival_events=main_stops,
            retained_terminal_loop_events=loops,terminal_timing_reused_not_qualified=True,
            failed_mainline_events=failed,
            conditional_unit_train_cost_ratio_for_equal_fleet_capex=None if total is None else old/total,
            max2000m_stop_spacing_alternative=dict(peak_trainsets=proposal_peak,spare_trainsets=proposal_spare,
                cold_reserve_trainsets=1,total_trainsets=proposal_total,
                circuit_s=proposal_seconds if not proposal_failure else None,
                additional_passenger_station_sites=len(additional_sites),
                new_sites=[dict(between_station_ids=list(pair[:2]),fraction_along_id_order=pair[2],located_design_qualified=False) for pair in sorted(additional_sites)],
                mainline_stop_events_per_circuit=proposal_main_stops,failed_events=proposal_failure,
                required_winding_library_counts_per_mainline_circuit=zone_counts,
                total_required_direction_winding_m_per_mainline_circuit=sum(float(k)*v for k,v in zone_counts.items()),
                station_library_failures=zone_failures,
                winding_count_scope='One directional station winding per mainline arrival in the circuit; terminal loop service windings are additional. New sites are chainage proposals only.',
                cost_break_even_unit_trainset_price_ratio=None if proposal_total is None else old/proposal_total,
                station_construction_access_power_and_land_cost_USD=None,
                civil_and_passenger_plan_adopted=False),
            actual_trainset_price_USD=None,complete_city_service_qualified=False))
    totals=[r['proposed_total_trainsets'] for r in rows]
    proposals=[r['max2000m_stop_spacing_alternative']['total_trainsets'] for r in rows]
    proposed_total=sum(proposals) if all(v is not None for v in proposals) else None
    return dict(lines=rows,retained_total_trainsets=data['totals']['trainsets'],
        proposed_total_trainsets=sum(totals) if all(v is not None for v in totals) else None,
        lines_with_unreachable_mainline_events=sum(bool(r['failed_mainline_events']) for r in rows),
        max2000m_spacing_alternative=dict(total_trainsets=proposed_total,
            additional_passenger_station_sites=sum(r['max2000m_stop_spacing_alternative']['additional_passenger_station_sites'] for r in rows),
            unit_trainset_price_ratio_for_equal_fleet_capex=None if proposed_total is None else data['totals']['trainsets']/proposed_total,
            winding_library_counts_per_mainline_circuit={str(int(z)):sum(r['max2000m_stop_spacing_alternative']['required_winding_library_counts_per_mainline_circuit'][str(int(z))] for r in rows) for z in ZONE_LENGTHS},
            total_required_direction_winding_m_per_mainline_circuit=sum(r['max2000m_stop_spacing_alternative']['total_required_direction_winding_m_per_mainline_circuit'] for r in rows),
            comparison='Explicit added-stop proposal; no retained line, city map or station baseline is overwritten',
            actual_complete_CAPEX_USD=None,physical_accepted=False),
        all_lines_qualified=False,actual_fleet_purchase_cost_USD=None,
        cost_claim='Low-cost trainsets are a design objective, not a verified price. Fleet arithmetic does not include revised depot, chargers, crews, renewals or financing.',
        operating_reserve_fraction_hypothesis=.12,terminal_cold_reserve_per_line_hypothesis=1)


def evaluate(vehicle,root=ROOT):
    root=Path(root).resolve();tare,mass=_vehicle(vehicle)
    a=tomllib.loads((root/'engineering/ferrite_maglev/station.toml').read_text())
    length=CARS*a['vehicle']['body_length_m']+(CARS-1)*a['vehicle']['coupling_gap_m']
    scenarios=[]
    for distance in (1000.,1500.,2000.):
        for speed in (10.,12.,15.,20.):
            for dwell in (30.,35.,45.,60.):
                for drag in DRAG_CONSTANTS:
                    inputs=dict(distance_m=distance,speed_cap_m_s=speed,acceleration_m_s2=.4,
                        deceleration_m_s2=.6,dwell_s=dwell,headway_s=HEADWAY,train_length_m=length,
                        constant_drag_N_per_car=drag,quadratic_drag_N_per_car_per_m_s_squared=1.8,
                        accounted_cap_loaded_kg_per_car=mass,passengers_per_car=PASSENGERS)
                    sid=identity(dict(candidate_id=vehicle['candidate_id'],inputs=inputs))
                    p=motion_profile(distance,speed,.4,.6,mass,drag)
                    zones=[]
                    if p['runtime_s'] is not None:
                        zones=[motor_zone(p,z,length,dwell) for z in ZONE_LENGTHS]
                    scenarios.append(dict(scenario_id=sid,inputs=inputs,profile=p,motor_zone_options=zones,
                        execution='completed',evidence_maturity='analytic-unpowered-coast-and-resource-hypotheses',
                        numerical_validity='valid-for-declared-ODE',physical_accepted=False))
    # Preserve full Pareto alternatives; choose a conservative-retained-drag
    # station-design experiment, never an operating or cheapest-system baseline.
    shortlist=[]
    for speed in (10.,12.,15.,20.):
        r=next(s for s in scenarios if s['inputs']['distance_m']==2000 and s['inputs']['speed_cap_m_s']==speed and s['inputs']['dwell_s']==35 and s['inputs']['constant_drag_N_per_car']==1000)
        possible=[z for z in r['motor_zone_options'] if z['geometry_full_engagement'] and z['nominal_resource_screen']=='pass']
        if possible:
            z=min(possible,key=lambda z:z['length_m']);shortlist.append(dict(scenario_id=r['scenario_id'],station_id=z['station_id'],runtime_s=r['profile']['runtime_s'],winding_length_m=z['length_m']))
    chosen=min(shortlist,key=lambda r:(r['winding_length_m'],r['runtime_s'])) if shortlist else None
    if chosen is None:raise ValueError('No declared two-kilometre station prototype survivor; retain failure campaign instead of silent fallback')
    selected=next(r for r in scenarios if r['scenario_id']==chosen['scenario_id'])
    zone=next(z for z in selected['motor_zone_options'] if z['station_id']==chosen['station_id'])
    timing=[_resource_events(selected['profile'],zone,selected['inputs']['dwell_s'],delay_first_dwell_s=delay,
        architecture=architecture) for architecture in ('section-addressed','whole-zone-exclusive') for delay in (0.,15.,60.)]
    formations=[dict(cars=n,passengers_per_car=46,people_per_train=n*46,headway_s=120.,
        capacity_pphpd=n*46*30,body_length_subtotal_m=17*n,
        formation_length_assumption_m=17*n+.5*(n-1),platform_and_power_qualified=False) for n in (6,8,10,11,12)]
    service=dict(cars=6,seats_per_car=44,wheelchair_places_per_car=2,standing_per_car=0,
        people_per_train=276,target_headway_s=120.,capacity_pphpd=8280.,
        mean_regular_interval_wait_s=60.,previous_180s_same_capacity_pphpd=5520.,
        earlier_120person_normal_reference_pphpd=14400.,earlier_reference_headway_s=180.,
        capacity_reduction_vs_14400_fraction=1-8280/14400,
        departure_frequency_ratio_to_180s=1.5,
        capacity_14400_at120s_minimum_cars=11,
        formation_alternatives=formations,actual_safe_headway_s=None,
        whole_line_operations_qualified=False)
    bound=dict(candidate_id=vehicle['candidate_id'],body_candidate_id=vehicle['body_candidate_id'],magnet_component_id=vehicle['magnet_component_id'])
    value=dict(schema=SCHEMA,**bound,source_sha256=sources(root),
        assumptions=dict(grade=0.,acceleration_m_s2=.4,service_deceleration_m_s2=.6,
            independent_brake_lower_bound_hypothesis_m_s2=.6,independent_brake_measured=False,
            resistance_constants_N_per_car=list(DRAG_CONSTANTS),retained_resistance_control_N_per_car=1000.,
            coast_is_unpowered=True,jerk_and_full_current_dynamics_included=False,
            motion_models_are_railway_qualification=False),
        budget=dict(primary_scenarios=144,motor_zone_subcomparisons=sum(len(s['motor_zone_options']) for s in scenarios),
            maximum_motor_options_per_reaching_scenario=3,native_method_cases=6),
        scenarios=scenarios,selection=dict(selected_scenario_id=chosen['scenario_id'],selected_station_id=chosen['station_id'],
            purpose='Next service/station design prototype',shortlist=shortlist,
            policy='At2km,35s dwell and retained1000N/car drag, retain full-band-engagement120s resource survivors; select shortest shared winding, then shortest runtime. Installed cost and physical feasibility remain unknown.',
            integrated_operating_design_selected=False),
        selected_scenario=deepcopy(selected),selected_station=deepcopy(zone),
        station_resource_campaign=timing,service=service,
        protection=dict(stopping_bound_at_launch_speed_m=stopping_distance_m(selected['profile']['peak_speed_m_s']),
            stopping_bound_at_receiving_speed_m=stopping_distance_m(selected['profile']['arrival_speed_before_braking_m_s']),
            downhill10permille_bound_at_launch_speed_m=stopping_distance_m(selected['profile']['peak_speed_m_s'],grade_permille=10),
            assumptions='Independent brake remains available during receiving-power loss; this assumption is unverified for the vehicle.',
            actual_receiving_power_loss_response='not-qualified',actual_support_power_loss_response='not-qualified',
            safe_operation_permitted=False,nominal_headway_is_not_a_protection_release=True),
        fleet=_fleet(root,selected['profile'],35.,tare),
        equal_cycle_train_price_break_even=dict(relative_to180s_unit_price_ratio=2/3,
            reason='At an unchanged cycle and no rounding,120s needs1.5times the180s fleet, so unit price must fall byone-third just to hold fleet purchase cost.',
            actual_trainset_price_USD=None,guideway_station_energy_finance_effects_included=False),
        engineering_screen='nominal-resource-and-coast-hypotheses-only; physical-operation-unknown',**FLAGS)
    value['selection']['selection_id']=identity(value['selection'])
    value['evaluation_id']=identity(value)
    return value


def validate(value,vehicle,root=ROOT):
    expected=evaluate(vehicle,root)
    if value!=expected:raise ValueError('service candidate, sources, physics or selection differs')
    return True


def summary(value):
    """Stable concise contract for the dossier and Workbench."""
    rows=[]
    for s in value['scenarios']:
        i=s['inputs'];p=s['profile']
        for z in s['motor_zone_options'] or [None]:
            rows.append(dict(scenario_id=s['scenario_id'],station_id=None if z is None else z['station_id'],
                spacing_m=i['distance_m'],launch_speed_m_s=p['peak_speed_m_s'],
                arrival_speed_m_s=p['arrival_speed_before_braking_m_s'],runtime_s=p['runtime_s'],
                dwell_s=i['dwell_s'],drag_N_per_car=i['constant_drag_N_per_car'],
                shared_winding_m=None if z is None else z['length_m'],
                required_mechanical_kW=None if z is None else z['required_peak_train_mechanical_kW'],
                whole_zone_resource_interval_s=None if z is None else z['minimum_nominal_resource_interval_s'],
                headway_120_margin_s=None if z is None else z['nominal_120_s_margin_s'],
                full_band_engagement=None if z is None else z['geometry_full_engagement'],
                coast_screen=p['engineering_screen'],failure=p['failure'],
                resource_screen='not-evaluated' if z is None else z['nominal_resource_screen']))
    return dict(candidate_id=value['candidate_id'],body_candidate_id=value['body_candidate_id'],
        magnet_component_id=value['magnet_component_id'],evaluation_id=value['evaluation_id'],
        selection=value['selection'],service=value['service'],selected_scenario=value['selected_scenario'],
        selected_station=value['selected_station'],station_resource_campaign=value['station_resource_campaign'],
        fleet=value['fleet'],comparison_rows=rows,equal_cycle_train_price_break_even=value['equal_cycle_train_price_break_even'],
        actual_safe_headway_s=None,**FLAGS)


def native_request(vehicle,service,case='nominal'):
    """Exact trajectories feed unchanged Rust; virtual gaps are method fixtures."""
    _vehicle(vehicle)
    if service['candidate_id']!=vehicle['candidate_id']:raise ValueError('native service candidate mismatch')
    cases={'nominal':'contract-180','journal':'contract-journal','receiving-authority-loss':'contract-closed-arrival',
           'independent-brake-loss':'contract-brake-loss','support-gap-fault':'contract-gap-fault','integrity-loss':'contract-integrity-loss'}
    if case not in cases:raise ValueError('bounded native case required')
    s=service['selected_scenario'];p=s['profile'];T=math.ceil(p['runtime_s']/.1)*.1;dwell=s['inputs']['dwell_s'];D=p['distance_m']
    a=deepcopy(line_capacity.load());a.update(urban_distance_m=D,urban_legs=4,minimum_deceleration_m_s2=.6,headway_s=120.)
    model,cfg,bounds,berths=line_capacity.deployment(a,'urban',block_length_m=500.)
    cfg=list(bytes.fromhex(identity(dict(candidate_id=vehicle['candidate_id'],scenario_id=s['scenario_id']))))
    for train in model['trains']:train['config']['configuration']=cfg
    step=.1;horizon=240+T+10.;frames=[]
    for tick in range(1,math.ceil(horizon/step)+1):
        time=tick*step;now=1_000_000_000+round(time*1e9);positions=[]
        for j in range(3):
            elapsed=time-j*120-step
            if elapsed< -1e-8:continue
            remaining=max(0.,elapsed);position=speed=0.;legidx=None
            for leg in range(4):
                if remaining<T-1e-8:
                    legidx=leg
                    state=position_at(p,0. if remaining<1e-7 else remaining);position=leg*D+state['position_m'];speed=state['speed_m_s'];break
                position=(leg+1)*D;remaining-=T
                if remaining<dwell-1e-8:break
                remaining=max(0.,remaining-dwell)
            else:raise ValueError('native horizon extends past declared route')
            positions.append(dict(train=101+j,front_mm=round((position+150)*1000),velocity_mmps=math.ceil(speed*1000),observed_ns=now,
                integrity_proved=True,independent_brake_ready=True,launch_leg=legidx))
        frames.append(dict(now_ns=now,positions=positions))
    return dict(model=model,configuration=cfg,frames=frames,maximum_acceleration_mmps2=1000,sample_ns=100_000_000,
        exclusive_leg=False,delayed_clear_resource=None,delay_until_ns=0,competing_train=False,
        contract=dict(control=cases[case],fault_at_ns=71_000_000_000,receiving_berth=berths[1],
            policy=dict(maximum_acceleration_mmps2=1000,maximum_sample_ns=100_000_000,velocity_error_mmps=100,minimum_gap_um=3000,maximum_gap_um=13000)))


def _native_assess(case,result,request):
    base=(result.get('schema')=='osr-progressive-departure-replay/1' and result.get('physical_output_authorised') is False
          and result.get('whole_line_capacity_accepted') is False and result.get('durable_event_replay_equal') is True)
    if case in ('nominal','journal'):
        return bool(base and result.get('study_pass') is True and result.get('failure') is None
            and result['frames_executed']==len(request['frames']) and result['maximum_active_trains']==3
            and result['committed_departures']>=3 and result['stopped_arrivals']>=3 and result['full_tail_releases']>0
            and result['minimum_train_separation_mm']>0 and result['minimum_stopping_authority_margin_mm']>=0)
    if case=='receiving-authority-loss':
        return bool(base and result.get('study_pass') is False and (result.get('failure') or {}).get('kind')=='progressive-arrival-authority-held'
                    and result.get('braking_plant_pass') is True)
    return bool(base and result.get('study_pass') is False and (result.get('failure') or {}).get('kind')=='progressive-evidence-held'
                and result.get('retained_owners') and any(r['phase']=='Held' and r['stop_required'] for r in result.get('retained_contracts',[])))


def run_native(vehicle,service,output,root=ROOT):
    root=Path(root).resolve();output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False)
    before=sources(root,native=True)
    build=subprocess.run(line_capacity.BUILD,cwd=root,capture_output=True,text=True,timeout=240,env=dict(os.environ,CARGO_TERM_COLOR='never'))
    (output/'build.stdout.log').write_text(build.stdout);(output/'build.stderr.log').write_text(build.stderr)
    if build.returncode:raise RuntimeError('native protection compilation failed; logs retained')
    artifacts=[r['executable'] for line in build.stdout.splitlines() if (r:=json.loads(line)).get('reason')=='compiler-artifact' and r.get('target',{}).get('name')=='line_capacity_replay' and r.get('executable')]
    if len(artifacts)!=1:raise ValueError('one compiled Rust replay artifact required')
    executable=Path(artifacts[0]);rows=[]
    for case in ('nominal','journal','receiving-authority-loss','independent-brake-loss','support-gap-fault','integrity-loss'):
        request=native_request(vehicle,service,case);raw=encoded(request)
        (output/(case+'-request.json.gz')).write_bytes(gzip.compress(raw,mtime=0))
        run=subprocess.run([str(executable)],input=raw,capture_output=True,cwd=root,timeout=120)
        (output/(case+'-stdout.json')).write_bytes(run.stdout);(output/(case+'-stderr.log')).write_bytes(run.stderr)
        if run.returncode:rows.append(dict(case=case,execution='tool-error',returncode=run.returncode,control_pass=False));continue
        result=json.loads(run.stdout);rows.append(dict(case=case,execution='completed',returncode=0,control_pass=_native_assess(case,result,request),
            request_sha256=sha256(raw).hexdigest(),output_sha256=sha256(run.stdout).hexdigest(),
            result_summary={k:result.get(k) for k in ('study_pass','failure','frames_executed','committed_departures','stopped_arrivals','full_tail_releases','maximum_active_trains','minimum_train_separation_mm','minimum_stopping_authority_margin_mm','braking_plant_pass')}))
    result=dict(schema='osr-comfort-service-native/1',candidate_id=vehicle['candidate_id'],service_evaluation_id=service['evaluation_id'],
        scenario_id=service['selection']['selected_scenario_id'],station_id=service['selection']['selected_station_id'],
        source_sha256=before,rows=rows,all_controls_pass=all(r['control_pass'] for r in rows),
        executable_sha256=sha256(executable.read_bytes()).hexdigest(),
        compiler=subprocess.run(['rustc','--version'],capture_output=True,text=True,check=True).stdout.strip(),
        tool='Existing osr-interlocking line_capacity_replay; no kernel source mutation',
        synthetic_gap_range_um=[6000,8000],synthetic_detector_integrity_and_brake_ready=True,
        physical_gap_response_simulated=False,actual_vehicle_stable_hover_verified=False,
        physical_headway_qualified=False,scope='Bounded protection-software method fixtures; not moving-train or station-power qualification',**FLAGS)
    if sources(root,native=True)!=before:raise ValueError('native protection sources changed during execution')
    result['evaluation_id']=identity(result);(output/'result.json').write_bytes(encoded(result))
    files={p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir()) if p.is_file()}
    (output/'manifest.json').write_bytes(encoded(dict(source_sha256=before,files_sha256=files,evaluation_id=result['evaluation_id'],**FLAGS)))
    return result


def verify_native(vehicle,service,output,root=ROOT):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes());r=json.loads((output/'result.json').read_bytes())
    if m['source_sha256']!=sources(root,native=True):raise ValueError('native protection source snapshot differs')
    if r['candidate_id']!=vehicle['candidate_id'] or r['service_evaluation_id']!=service['evaluation_id']:raise ValueError('native protection belongs to another candidate/evaluation')
    if r['evaluation_id']!=identity({k:v for k,v in r.items() if k!='evaluation_id'}):raise ValueError('native protection evaluation identity differs')
    if r.get('schema')!='osr-comfort-service-native/1' or any(r.get(k) is not v or m.get(k) is not v for k,v in FLAGS.items()):
        raise ValueError('native protection cannot assert physical or operating acceptance')
    cases={'nominal','journal','receiving-authority-loss','independent-brake-loss','support-gap-fault','integrity-loss'}
    if len(r['rows'])!=6 or {row['case'] for row in r['rows']}!=cases:
        raise ValueError('exact native method/control case set required')
    actual={p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir()) if p.is_file() and p.name!='manifest.json'}
    if actual!=m['files_sha256']:raise ValueError('native protection payload differs')
    for row in r['rows']:
        case=row['case'];request=native_request(vehicle,service,case)
        raw=gzip.decompress((output/(case+'-request.json.gz')).read_bytes())
        if raw!=encoded(request) or row['request_sha256']!=sha256(raw).hexdigest():raise ValueError('native request does not reproduce exact candidate/profile')
        result=json.loads((output/(case+'-stdout.json')).read_bytes())
        if row['output_sha256']!=sha256((output/(case+'-stdout.json')).read_bytes()).hexdigest():raise ValueError('native output digest differs')
        if row['control_pass']!=_native_assess(case,result,request):raise ValueError('native control disposition differs')
    if not r['all_controls_pass'] or not all(row['control_pass'] for row in r['rows']):raise ValueError('native protection control failed')
    return dict(current=True,controls=len(r['rows']),evaluation_id=r['evaluation_id'],physical_headway_qualified=False)
