"""Compile retained geography/demand into separate, unqualified v0.5 city plans.

The outputs are planning quantities. Their straight, level, independent-car duty
screen cannot qualify a route, terminal loop, supplier price or operating fleet.
"""
from __future__ import annotations

import argparse
from concurrent.futures import FIRST_COMPLETED,ProcessPoolExecutor,wait
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
import math
import multiprocessing
import os
from pathlib import Path
import tempfile
import tomllib

from . import model,optimisation,evacuation,manufacturing,cartography,configuration,operating_plan,affordability,city_brief

ROOT = model.ROOT
ASSUMPTIONS = Path(__file__).with_name('city-planning.toml')
INDEX = Path(__file__).with_name('city-index.json')
NOTICE_START=b'<!-- osr-maglev-primary:start -->\n'
NOTICE_END=b'<!-- osr-maglev-primary:end -->\n'


def promote_city_readme(city_dir, report=None):
    """Regenerate a detailed front door from the current primary package."""
    path=Path(city_dir)/'README.md'
    data=json.loads((Path(city_dir)/'city.json').read_text())
    report=report or json.loads((Path(city_dir)/'engineering/maglev/summary.json').read_text())
    if report['city']!=data['city']['slug'] or 'affordability' not in report:
        raise ValueError('current city identity and affordability required for public brief')
    text=NOTICE_START.decode()+city_brief.frontdoor(report,data)+NOTICE_END.decode()
    path.write_text(text)
    return path


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


@lru_cache(maxsize=2048)
def _cached_city_slug(path, size, mtime_ns, ctime_ns):
    # Catalogue metadata is the first city table. Read only that table for this
    # inventory operation; full compilation still parses the complete design.
    slug=json.loads(Path(path).read_text())['city']['slug']
    if not isinstance(slug,str) or not slug:
        raise ValueError('nonempty city slug required: '+path)
    return slug


def city_slug(path):
    path=Path(path).resolve()
    stat=path.stat()
    return _cached_city_slug(str(path),stat.st_size,stat.st_mtime_ns,stat.st_ctime_ns)


def count(value, name):
    if type(value) is not int or value <= 0:
        raise ValueError('positive integer required: ' + name)
    return value


def formation(c, source_consist, profiles):
    """Match both declared passenger loads, including line-specific profiles."""
    v = c['vehicle']
    aw2 = max([count(source_consist['passenger_capacity'], 'AW2')] +
              [count(p['passenger_capacity'], 'profile AW2') for p in profiles])
    aw3 = max([count(source_consist['crush_capacity'], 'AW3')] +
              [count(p['crush_capacity'], 'profile AW3') for p in profiles])
    cars = max(math.ceil(aw2 / v['aw2_passengers_per_car']),
               math.ceil(aw3 / v['aw3_passengers_per_car']))
    cfg=configuration.selected(c,city='planning',cars=cars).formation
    m = model.mass(c, c['mass']['ferrite_base'], c['power']['services_battery_kwh_per_car'])
    return dict(cars=cars, retained_aw2_required=aw2, retained_aw3_required=aw3,
                aw2_passengers=cars*v['aw2_passengers_per_car'], aw3_passengers=cars*v['aw3_passengers_per_car'],
                nominal_body_length_m=cars*v['nominal_car_length_m'], overall_length_m=None,
                overall_length_assumption_m=cfg.assumed_overall_length_m,coupling_gap_assumption_m=cfg.coupling_gap_assumption_m,
                length_basis='Sum of nominal 17 m bodies; coupling pitch and overhang unresolved.',
                tare_mass_kg=cars*m['tare_kg'], aw2_mass_kg=cars*m['aw2_kg'], aw3_mass_kg=cars*m['aw3_kg'],
                gross_storage_kwh=cars*c['power']['services_battery_kwh_per_car'],
                eol_capacity_kwh=cars*c['power']['services_battery_kwh_per_car']*c['power']['eol_capacity_fraction'],
                normal_soc_low=c['power']['normal_soc_low'], normal_soc_high=c['power']['normal_soc_high'],
                eol_normal_window_kwh=cars*m['eol_window_kwh'], protected_emergency_energy_kwh=None,
                cabin_width_m=v['nominal_car_width_m'], full_running_gear_envelope_width_m=None,
                envelope_basis='Cabin width does not bound magnetic lifting faces, guidance arms or below-floor gear. Revalidate full route/platform swept envelope against native geometry.',
                measured_mass=False, formation_qualified=False)


def station_legs(line, stations):
    """Use retained chainages, reconciling a complete ring with its total length."""
    length = model.positive(line['length_m'], 'route length')
    ordered = sorted(stations, key=lambda s: s['s_m'])
    if len(ordered) < 2 or len({s['id'] for s in ordered}) != len(ordered):
        raise ValueError('at least two unique stations required: '+line['name'])
    chainages = [model.positive(s['s_m'], 'chainage', zero=True) for s in ordered]
    if chainages[-1] > length + 1:
        raise ValueError('station beyond retained route length: '+line['name'])
    legs = [b-a for a, b in zip(chainages, chainages[1:])]
    if any(d <= 0 for d in legs):
        raise ValueError('distinct increasing station chainages required')
    if line['shape'] == 'ring':
        closure = length - sum(legs)
        model.positive(closure, 'ring closure')
        legs.append(closure)
    elif line['shape'] == 'radial':
        # Retain unserved ends explicitly; charge/duty uses the full declared route.
        legs[0] += chainages[0]
        legs[-1] += max(0, length-chainages[-1])
        closure = None
    else:
        raise ValueError('unsupported retained topology: '+line['shape'])
    return ordered, legs, closure


def duty_evaluator(c):
    """Cache only within this exact input configuration."""
    mass = model.mass(c, c['mass']['ferrite_base'], c['power']['services_battery_kwh_per_car'])

    @lru_cache(maxsize=None)
    def evaluate(distance, hot=False, regen=True, speed=80.0,*,cars=None):
        configuration = deepcopy(c)
        configuration['power']['station_spacing_study_m'] = distance
        r = model.cycle(configuration, mass['aw3_kg' if hot else 'aw2_kg'], hot=hot, regen=regen, speed_kmh=speed,cars=cars)
        hotel = configuration['power']['hot_hotel_kw_per_car' if hot else 'normal_hotel_kw_per_car']
        return dict(moving_seconds=r['moving_seconds'], moving_energy_kwh=r['cycle_kwh']-
                    hotel*configuration['power']['station_dwell_seconds']/3600,
                    achieved_speed_kmh=r['achieved_speed_kmh'], hotel_kw=hotel,
                    station_traction_input_kwh=r['station_traction_input_kwh'],
                    pure_trajectory_screen_pass=r['pure_trajectory_screen_pass'],
                    station_zone_screen_pass=r['station_zone_screen_pass'],station_zone=r['station_zone'],
                    kinematic_screen_pass=r['kinematic_screen_pass'],kinematic_hold=r['kinematic_hold'])
    def for_formation(cars):
        def bound(distance,hot=False,regen=True,speed=80.0):
            return evaluate(distance,hot,regen,speed,cars=cars)
        return bound
    evaluate.for_formation=for_formation
    return evaluate


def line_plan(c, a, f, line, stations, source_fleet, evaluate,*,operating=None):
    if operating is not None:return operating_line_plan(c,a,f,line,source_fleet,operating)
    if hasattr(evaluate,'for_formation'):evaluate=evaluate.for_formation(f['cars'])
    ordered, distances, closure = station_legs(line, stations)
    schedule = source_fleet.get('schedule', [])
    if not schedule:
        raise ValueError('retained service schedule required: '+line['name'])
    source_headway = min(model.positive(s['headway_min'], 'headway') for s in schedule)*60
    headway=max(source_headway,c['vehicle']['scheduled_headway_seconds'])
    normal = [evaluate(round(d, 6)) for d in distances]
    hot = [evaluate(round(d, 6), True, False) for d in distances]
    hot_regen = [evaluate(round(d, 6), True, True) for d in distances]
    p = a['charging']; charger = model.positive(p['candidate_kw_per_car'], 'charger')
    hotel = c['power']['hot_hotel_kw_per_car']
    if charger <= hotel:
        raise ValueError('charger must exceed stationary services')
    # Charge at each station; dwell covers the worst incoming hot/no-regen leg.
    effective = max((r['moving_energy_kwh']*3600 + hotel*p['connection_overhead_seconds']) /
                    (charger-hotel) for r in hot)
    dwell = max(p['minimum_dwell_seconds'], math.ceil(effective+p['connection_overhead_seconds']))
    ring = line['shape'] == 'ring'
    loop_distance = 0.0
    loop_time = 0.0
    loop_energy = 0.0
    loop_regen_energy = 0.0
    if not ring:
        radius = a['topology']['terminal_loop_radius_screen_m']
        loop_distance = a['topology']['terminal_loop_circumferences_per_roundtrip']*2*math.pi*radius
        speed = a['topology']['terminal_loop_speed_screen_kmh']
        lateral = (speed/3.6)**2/radius
        if lateral > a['topology']['terminal_loop_lateral_acceleration_limit_screen_m_s2']:
            raise ValueError('loop speed exceeds declared lateral acceleration screen')
        loop_duty = evaluate(round(loop_distance/2, 6), True, False, speed)
        loop_time = 2*loop_duty['moving_seconds']
        loop_energy = 2*loop_duty['moving_energy_kwh']
        loop_regen_energy = 2*evaluate(round(loop_distance/2, 6), True, True, speed)['moving_energy_kwh']
        # End loops also consume energy between platform charging events.
        extra = loop_energy/2
        effective = (max(r['moving_energy_kwh'] for r in hot)*3600+extra*3600+
                     hotel*p['connection_overhead_seconds'])/(charger-hotel)
        dwell = max(dwell, math.ceil(effective+p['connection_overhead_seconds']))
    # Protected-zone clearance uses the same nominal jerk/acceleration envelope.
    # It is planning time only; full-tail detection and grade/receiver evidence remain open.
    clearance=math.sqrt(2*(f['overall_length_assumption_m']+75)/c['vehicle']['maximum_initial_acceleration_m_s2'])+c['vehicle']['maximum_initial_acceleration_m_s2']/c['vehicle']['jerk_study_m_s3']
    headway_bound=max(r['moving_seconds'] for r in hot)+dwell+clearance+5.
    headway=max(headway,math.ceil(headway_bound))
    cycle_distance = sum(distances)*(1 if ring else 2)+loop_distance
    cycle_seconds = sum(r['moving_seconds'] for r in hot)*(1 if ring else 2)+loop_time
    # Radials include both terminal stops once per round trip; rings once/lap.
    stops = len(ordered) if ring else 2*len(ordered)-2
    cycle_seconds += stops*dwell
    per_direction = math.ceil(cycle_seconds/headway)
    peak = 2*per_direction if ring else per_direction
    spare = math.ceil(peak*a['formation']['spare_fraction'])
    total = peak+spare+a['formation']['cold_reserve_per_line']
    nominal_slot = f['overall_length_assumption_m']+a['formation']['platform_end_allowance_m']
    hot_cycle = sum(r['moving_energy_kwh'] for r in hot)*(1 if ring else 2)+loop_energy+hotel*stops*dwell/3600
    normal_cycle = sum(r['moving_energy_kwh'] for r in normal)*(1 if ring else 2)
    normal_cycle += c['power']['normal_hotel_kw_per_car']*stops*dwell/3600
    # Normal loop calculation must use the normal load and hotel assumptions.
    if not ring:
        normal_cycle += 2*evaluate(round(loop_distance/2, 6), False, True,
                                 a['topology']['terminal_loop_speed_screen_kmh'])['moving_energy_kwh']
    source_wrap = line.get('ring_wrap_length_m')
    stations_out = [dict(id=s['id'], lat=s['lat'], lon=s['lon'], retained_platform_length_m=s.get('platform_length_m'),
                         provisional_platform_body_plus_allowance_m=nominal_slot,
                         length_shortfall_screen_m=max(0, nominal_slot-s.get('platform_length_m', 0))) for s in ordered]
    charging = dict(candidate_kw_per_car=charger, candidate_kw_per_train=charger*f['cars'],
                    dwell_seconds=dwell, effective_charge_seconds=dwell-p['connection_overhead_seconds'],
                    minimum_screen_passed=dwell <= p['maximum_dwell_screen_seconds'],
                    dwell_exceeds_peak_headway=dwell > headway,
                    minimum_parallel_platform_berths_per_direction=math.ceil(dwell/headway),
                    station_count=len(ordered), all_sites_simultaneous_dc_upper_bound_kw=len(ordered)*2*charger*f['cars'],
                    diversity_applied=False, grid_pv_storage_sizing_accepted=False,
                    conversion_losses_and_taper_included=False, rating_selected=False)
    topology = dict(selected=a['topology']['ring' if ring else 'radial'], mainline_switches=0,
                    terminal_loop_count=0 if ring else 2, added_single_direction_loop_beam_m=loop_distance,
                    loop_radius_screen_m=None if ring else a['topology']['terminal_loop_radius_screen_m'],
                    loop_speed_screen_kmh=None if ring else a['topology']['terminal_loop_speed_screen_kmh'],
                    loop_lateral_acceleration_screen_m_s2=None if ring else lateral,
                    loop_lateral_acceleration_limit_screen_m_s2=a['topology']['terminal_loop_lateral_acceleration_limit_screen_m_s2'],
                    loop_land_and_swept_envelope_accepted=False, depot_access_accepted=False,
                    source_ring_wrap_m=source_wrap, complete_ring_closure_m=closure,
                    ring_wrap_discrepancy_m=None if closure is None or source_wrap is None else closure-source_wrap,
                    exclusive_shuttle_alternative=None if ring else dict(
                        minimum_independent_lanes=math.ceil((cycle_seconds-loop_time)/headway),
                        reversal_allowance_seconds=0,
                        rule='One train per isolated bidirectional lane; no passing or crossover. This lane count is a capacity screen, not a selected civil plan.'),
                    loop_length_basis='Two full-circumference budgeting allowances per radial roundtrip; connection geometry and actual added length unresolved.')
    depot = dict(storage_slots=total, minimum_total_storage_track_m=total*nominal_slot,
                 storage_lanes_screen=math.ceil(total/a['depot']['trains_per_storage_lane_screen']),
                 inspection_bays_screen=math.ceil(total*a['depot']['inspection_bay_fraction_screen']),
                 simultaneous_depot_charge_kw_upper_bound=total*charger*f['cars'],
                 switch_policy=a['depot']['switches'], placement_accepted=False,
                 entry_exit_without_mainline_points_qualified=False, depot_cost_usd=None,
                 access='A moving transfer device or engineered depot-only connection is required and unqualified.')
    arrivals=[]
    sequence=[(i,i+1) for i in range(len(ordered)-1)]
    if ring:
        sequence.append((len(ordered)-1,0))
    else:
        sequence += [(i,i-1) for i in range(len(ordered)-1,0,-1)]
    for origin,destination in sequence:
        leg_index=origin if ring else min(origin,destination)
        terminal_loop=not ring and destination in (0,len(ordered)-1)
        arrivals.append(dict(origin_station=ordered[origin]['id'], destination_station=ordered[destination]['id'],
                             distance_m=distances[leg_index]+(loop_distance/2 if terminal_loop else 0),
                             moving_seconds=hot[leg_index]['moving_seconds']+(loop_time/2 if terminal_loop else 0),
                             hot_no_regen_motion_kwh=(hot[leg_index]['moving_energy_kwh']+(loop_energy/2 if terminal_loop else 0))*f['cars'],
                             hot_regen_motion_kwh=(hot_regen[leg_index]['moving_energy_kwh']+(loop_regen_energy/2 if terminal_loop else 0))*f['cars'],
                             terminal_loop_allowance=terminal_loop))
    return dict(line=line['name'], retained_shape=line['shape'], retained_length_m=line['length_m'],
                retained_schedule=schedule, retained_peak_headway_seconds=source_headway,
                selected_peak_headway_seconds=headway,planning_minimum_headway_seconds=headway_bound,
                source_aw2_capacity_per_direction_hour=f['aw2_passengers']*3600/source_headway,
                pure_trajectory_screen_pass=all(r.get('pure_trajectory_screen_pass',r['kinematic_screen_pass']) for r in hot),
                fixed_station_zone_screen_pass=all(r.get('station_zone_screen_pass',False) for r in hot),
                station_powered_kinematic_screen_pass=all(r['kinematic_screen_pass'] and r.get('station_zone_screen_pass',False) for r in hot),
                intermediate_station_zone_options=[dict(after_station=ordered[min(i,len(ordered)-1)]['id'],leg_distance_m=d,additional_1km_station_zones=max(0,math.ceil(d/1000)-1),located=False,priced=False) for i,d in enumerate(distances) if d>1000],
                kinematic_holds=[dict(leg=i+1,distance_m=distances[i],
                    stage='fixed-station-zone' if r.get('pure_trajectory_screen_pass',r['kinematic_screen_pass']) else 'longitudinal-trajectory',
                    reason=r.get('kinematic_hold') or 'Fixed station-zone feasibility not supplied by the planning evaluator')
                    for i,r in enumerate(hot) if not r['kinematic_screen_pass'] or not r.get('station_zone_screen_pass',False)],
                terminal_loop_propulsion_qualified=False if not ring else None,
                aw2_capacity_per_direction_hour=f['aw2_passengers']*3600/headway,
                formation=f, topology=topology, stations=stations_out,
                duty=dict(cycle_distance_m=cycle_distance, conservative_cycle_seconds=cycle_seconds,
                          moving_seconds=sum(r['moving_seconds'] for r in hot)*(1 if ring else 2)+loop_time,
                          normal_aw2_regen_cycle_kwh=normal_cycle*f['cars'],
                          hot_aw3_no_regen_cycle_kwh=hot_cycle*f['cars'],
                          largest_leg_m=max(distances), minimum_leg_m=min(distances),
                          worst_incoming_leg_hot_no_regen_kwh=max(r['moving_energy_kwh'] for r in hot)*f['cars'],
                          hot_hotel_kw=hotel*f['cars'], arrival_events_per_circuit=arrivals,
                          eol_window_divided_by_cycle_energy=f['eol_normal_window_kwh']/(hot_cycle*f['cars']),
                          route_acceptance=False,
                          exclusions=['grade/curves/wind', 'six-car coupled dynamics', 'shared-train aerodynamic effects',
                                      'loop lateral force and physical geometry', 'emergency reserve', 'missed charge',
                                      'full SOC and low voltage', 'charger taper/grid and battery internal losses']),
                fleet=dict(peak=peak, spare=spare, cold_reserve=a['formation']['cold_reserve_per_line'], total=total,
                           source_fleet_inherited=False,conflict_and_recovery_validated=False,
                           kinematic_profile_closed=all(r['kinematic_screen_pass'] and r.get('station_zone_screen_pass',False) for r in hot),timetable_qualified=False,
                           rule='ceil(services circuit time / selected station-resource headway), two directions for rings,10%spare plusone reserve; held kinematic/routecases remain conditional'),
                charging=charging, depot=depot)


def operating_line_plan(c,a,f,line,source_fleet,operating):
    """Compile located operating stops, real loop arcs and individually charged legs."""
    ordered=operating['stations'];trips=operating['trips'];loops=operating['terminal_loops']
    ring=line['shape']=='ring';policy=operating['policy'];schedule=source_fleet['schedule']
    source_headway=min(model.positive(row['headway_min'],'headway') for row in schedule)*60
    all_trips=[*trips,*[loop['motion'] for loop in loops]]
    dwell=max(a['charging']['minimum_dwell_seconds'],*[row.get('dwell_s',a['charging']['maximum_dwell_screen_seconds']) for row in all_trips])
    charger=max(row.get('charger_input_kw_per_car',a['charging']['candidate_kw_per_car']) for row in all_trips)
    fraction=min((row.get('connected_fraction',.75) for row in all_trips),default=.75)
    bound=max(row.get('runtime_s',100.)+dwell+(row.get('tail_clearance_s') or 100.)+policy['release_allowance_s'] for row in all_trips)
    headway=max(source_headway,policy['minimum_headway_s'],math.ceil(bound/policy['headway_quantum_s'])*policy['headway_quantum_s'])
    arrivals=[]
    edges=[(i,i+1,i) for i in range(len(ordered)-1)]
    if ring:edges.append((len(ordered)-1,0,len(trips)-1))
    else:edges += [(i,i-1,i-1) for i in range(len(ordered)-1,0,-1)]
    def event(origin,destination,motion,*,loop=False):
        hot=operating_plan.duty(c,motion,hot=True)
        normal=operating_plan.duty(c,motion,hot=False)
        arrivals.append(dict(origin_station=origin,destination_station=destination,
            distance_m=motion['distance_m'],moving_seconds=hot['moving_seconds'],
            hot_no_regen_motion_kwh=hot['moving_energy_kwh']*f['cars'],
            hot_regen_motion_kwh=hot['moving_energy_kwh']*f['cars'],
            normal_services_motion_kwh=normal['moving_energy_kwh']*f['cars'],
            station_traction_input_kwh=None if hot['station_traction_input_kwh'] is None else hot['station_traction_input_kwh']*f['cars'],
            terminal_loop_allowance=loop,numerical_motion_pass=motion.get('kinematic_screen_pass',motion['study_pass'])))
    for origin,destination,index in edges:
        event(ordered[origin]['id'],ordered[destination]['id'],trips[index])
        if not ring and destination in (0,len(ordered)-1):
            loop=loops[0 if destination==0 else 1];previous=ordered[destination]['id']
            for i in range(loop['sections']):
                target=loop['service_zones'][i]['id'] if i<len(loop['service_zones']) else ordered[destination]['id']+'-outgoing'
                event(previous,target,loop['motion'],loop=True);previous=target
    moving=sum(row['moving_seconds'] for row in arrivals);cycle=moving+len(arrivals)*dwell
    per_direction=math.ceil(cycle/headway);peak=2*per_direction if ring else per_direction
    spare=math.ceil(peak*a['formation']['spare_fraction']);total=peak+spare+a['formation']['cold_reserve_per_line']
    slot=f['overall_length_assumption_m']+a['formation']['platform_end_allowance_m']
    hotel=c['power']['hot_hotel_kw_per_car']*f['cars'];normal_hotel=c['power']['normal_hotel_kw_per_car']*f['cars']
    hot_cycle=sum(row['hot_no_regen_motion_kwh'] for row in arrivals)+hotel*len(arrivals)*dwell/3600
    normal_cycle=sum(row['normal_services_motion_kwh'] for row in arrivals)+normal_hotel*len(arrivals)*dwell/3600
    holds=[dict(leg=i+1,distance_m=row['distance_m'],stage='located-operating-trajectory-and-winding',reason=row.get('reason','; '.join(row.get('holds',[]))))
           for i,row in enumerate(trips) if not row.get('kinematic_screen_pass',row['study_pass'])]
    design_holds=[dict(leg=i+1,stage='wider-corridor-system',reason=reason) for i,row in enumerate(trips) for reason in row.get('holds',[])]
    design_holds.extend(dict(stage='passenger-transfer-spacing',reason='Mandatory transfer/terminal nodes conflict with declared minimum spacing',details=conflict) for conflict in operating['spacing_conflicts'])
    design_holds.extend(dict(stage='terminal-passenger-transfer-access',reason='Compact terminal transfer connector needs accessible geometry, land, structural design and cost evidence',details=connector)
        for connector in operating.get('terminal_transfer_access_proposals',[]))
    for loop in loops:
        if not loop['motion']['study_pass'] or not loop['geometry']['lateral_screen_pass']:
            holds.append(dict(leg=loop['id'],distance_m=loop['geometry']['length_m'],stage='terminal-curve-motion',
                reason=loop['motion'].get('reason','terminal lateral acceleration screen failed')))
    service_zones=[zone for loop in loops for zone in loop['service_zones']]
    capacity=f['aw2_passengers']*3600/headway;target=f['retained_aw2_required']*3600/source_headway
    charging=dict(candidate_kw_per_car=charger,
        source_input_kw_per_car=charger,
        converted_output_kw_per_car=charger*a['charging']['conversion_efficiency_study'],
        conversion_efficiency_study=a['charging']['conversion_efficiency_study'],
        candidate_kw_per_train=charger*f['cars'],dwell_seconds=dwell,
        effective_charge_seconds=dwell*fraction,connected_fraction=fraction,
        minimum_screen_passed=dwell<=a['charging']['maximum_dwell_screen_seconds'],
        dwell_exceeds_peak_headway=dwell>headway,minimum_parallel_platform_berths_per_direction=math.ceil(dwell/headway),
        station_count=len(ordered),terminal_service_zone_count=len(service_zones),
        all_sites_simultaneous_dc_upper_bound_kw=(len(ordered)*2+len(service_zones))*charger*f['cars'],
        simultaneous_power_scope='Services chargers only; fixed station/booster traction, independent rescue, buildings and external grid losses are additional',
        fixed_zone_traction_peak_grid_input_kw=None,complete_network_grid_rating_kw=None,
        diversity_applied=False,grid_pv_storage_sizing_accepted=False,conversion_loss_allowance_included=True,
        charge_taper_included=False,conversion_losses_and_taper_included=False,rating_selected=False)
    topology=dict(selected='two-independent-directed-circuits' if ring else 'located-tangent-terminal-loops-with-station-powered-blocks',
        mainline_switches=0,terminal_loop_count=len(loops),
        added_single_direction_loop_beam_m=sum(loop['geometry']['length_m'] for loop in loops),
        loop_radius_screen_m=None if ring else policy['terminal_radius_m'],loop_speed_screen_kmh=None if ring else policy['terminal_speed_limit_kmh'],
        loop_lateral_acceleration_screen_m_s2=None if ring else (policy['terminal_speed_limit_kmh']/3.6)**2/policy['terminal_radius_m'],
        loop_lateral_acceleration_limit_screen_m_s2=policy['terminal_lateral_acceleration_screen_m_s2'],
        loop_land_and_swept_envelope_accepted=False,depot_access_accepted=False,
        source_ring_wrap_m=line.get('ring_wrap_length_m'),
        complete_ring_closure_m=trips[-1]['distance_m'] if ring else None,
        ring_wrap_discrepancy_m=None,exclusive_shuttle_alternative=None,
        terminal_service_zone_count=len(service_zones),terminal_service_zones=service_zones,
        terminal_winding_start_m=policy['terminal_winding_start_m'],terminal_winding_end_m=policy['terminal_winding_end_m'],
        terminal_sections_per_loop=policy['terminal_sections'],
        loop_length_basis='Exact tangent-connected R-L-R circular arcs, separate station-only stop-to-stop sections; curve-phase,guidance,land and clearance unqualified.')
    depot=dict(storage_slots=total,minimum_total_storage_track_m=total*slot,
        storage_lanes_screen=math.ceil(total/a['depot']['trains_per_storage_lane_screen']),
        inspection_bays_screen=math.ceil(total*a['depot']['inspection_bay_fraction_screen']),
        simultaneous_depot_charge_kw_upper_bound=total*charging['candidate_kw_per_train'],
        switch_policy=a['depot']['switches'],placement_accepted=False,entry_exit_without_mainline_points_qualified=False,depot_cost_usd=None,
        access='Depot connection/transfer and rescue hardware remain independently unqualified')
    return dict(line=line['name'],retained_shape=line['shape'],retained_length_m=line['length_m'],
        operational_route_length_m=operating['measured_polyline_length_m'],retained_schedule=schedule,
        retained_peak_headway_seconds=source_headway,selected_peak_headway_seconds=headway,
        planning_minimum_headway_seconds=bound,source_aw2_capacity_per_direction_hour=target,
        aw2_capacity_per_direction_hour=capacity,retained_capacity_target_met=capacity>=target,
        capacity_shortfall_passengers_per_direction_hour=max(0.,target-capacity),
        capacity_resolution='Retained demand target is preserved; any shortfall requires a separately qualified capacity/service development, not silent acceptance',
        pure_trajectory_screen_pass=operating['flat_mainline_screen_pass'],fixed_station_zone_screen_pass=operating['flat_mainline_screen_pass'],
        station_powered_kinematic_screen_pass=operating['flat_mainline_screen_pass'],kinematic_holds=holds,
        system_design_holds=design_holds,passenger_spacing_screen_pass=operating['passenger_spacing_screen_pass'],
        service_class=operating['service_class'],selected_eligible_operating_design=None,
        protection_options=[dict(kind='existing-exclusive-whole-leg',minimum_headway_s=bound,capacity_per_direction_hour=capacity,
                retained_target_met=capacity>=target,route_specific_traffic_accepted=False),
            dict(kind='sectioned-multitrain-fixed-line',target_headway_s=source_headway,implemented_and_proved=False,capacity_per_direction_hour=None,additional_cost_usd=None),
            dict(kind='multiple-berths-on-independent-fixed-guideways',implemented_and_proved=False,capacity_per_direction_hour=None,additional_cost_usd=None)],
        intermediate_station_zone_options=[],terminal_loop_propulsion_qualified=False if loops else None,
        terminal_numerical_motion_screen_pass=operating['terminal_longitudinal_screen_pass'],
        formation=f,topology=topology,operating_plan=operating,
        stations=[dict(id=s['id'],lat=s['lat'],lon=s['lon'],s_m=s['s_m'],retained_platform_length_m=None,
            provisional_platform_body_plus_allowance_m=slot,length_shortfall_screen_m=None,
            retained_access_station_ids=s['retained_access_station_ids'],mandatory_junction_ids=s['mandatory_junction_ids'],
            power_winding_length_m=s['power_winding_length_m'],power_winding_start_m=s['power_winding_start_m'],power_winding_end_m=s['power_winding_end_m'],
            site_approved=False) for s in ordered],
        duty=dict(cycle_distance_m=sum(row['distance_m'] for row in arrivals),conservative_cycle_seconds=cycle,moving_seconds=moving,
            normal_aw2_regen_cycle_kwh=normal_cycle,hot_aw3_no_regen_cycle_kwh=hot_cycle,
            largest_leg_m=max(row['distance_m'] for row in trips),minimum_leg_m=min(row['distance_m'] for row in trips),
            worst_incoming_leg_hot_no_regen_kwh=max(row['hot_no_regen_motion_kwh'] for row in arrivals),
            hot_hotel_kw=hotel,arrival_events_per_circuit=arrivals,
            station_main_traction_input_kwh_per_train_circuit=sum(row['station_traction_input_kwh'] or 0. for row in arrivals),
            fixed_station_and_booster_traction_input_kwh_per_train_circuit=sum(row['station_traction_input_kwh'] or 0. for row in arrivals),
            traction_energy_scope='Fixed-zone longitudinal study energy; services battery ledger contains hotel/support services only',
            eol_window_divided_by_cycle_energy=f['eol_normal_window_kwh']/hot_cycle,route_acceptance=False,
            exclusions=['grade,wind,curved six-car guidance/phase/dynamics','land,utilities,foundations and station-site approvals',
                'measured force/current/voltage/thermal hardware','authenticated occupancy and disturbed-network traffic','protected emergency reserve']),
        fleet=dict(peak=peak,spare=spare,cold_reserve=a['formation']['cold_reserve_per_line'],total=total,
            source_fleet_inherited=False,conflict_and_recovery_validated=False,kinematic_profile_closed=not holds,
            timetable_qualified=False,rule='Actual proposed operating-stop and loop-service event circuit / selected protected-resource headway; capacity shortfall remains visible'),
        charging=charging,depot=depot)


GATES = [
    ('retained-geography', 'Survey, utilities, land, water crossings, terrain, ground investigation and alignment reconciliation; retained mapping is geographic evidence only.'),
    ('formation-platform', 'Close coupling pitch, full magnetic lifting-face/guidance-arm/below-floor swept envelope, door/egress layouts, actual mass and equal AW2/AW3 qualification. The 2.65 m cabin width does not bound running gear or platform clearance.'),
    ('field-control', 'Obtain force/loss maps and rig correlation, six-axis stability, target timing and independent support/capture/braking protection.'),
    ('terminal-topology', 'Locate fixed loops/ring closure, qualify curvature, clearance and land, and provide switch-free failure recovery.'),
    ('elevated-alignment', 'Locate the predominantly elevated straight-tangent proposal and verify buildings/air rights, road/utility clearance, wildlife/water passage, piers, station/egress and construction access; no zero-impact claim from elevation alone.'),
    ('civil-release', 'Redesign guidebeam/passive rail, supports/foundations, joints/tolerances, movement, gap dynamics, evacuation and erection.'),
    ('route-duty', 'Run approved grade, curve, wind, hot, low-voltage, full-SOC, no-regen, missed-charge, failed-channel and rescue duty.'),
    ('fleet-timetable', 'Validate headway/conflicts, station berth throughput, dispatch, maintenance rotation, degraded service and reserve.'),
    ('charging-microgrid', 'Place charging interfaces and prove taper, power quality, PV/storage/backup sizing and adverse-weather replenishment.'),
    ('depot-access', 'Locate line-local storage/workshops and qualify depot-only connection/transfer, isolation, inspection, towing and recovery.'),
    ('programme-cost', 'Price all station/land/loop/bridge/at-grade/depot/energy/control/production/QA/NRE/spares/OPEX scope, origin-trace MBOM and apply EPC once.'),
    ('physical-release', 'Close G0–G5 through authenticated independent physical acceptance; planning arithmetic is insufficient.'),
]


def generate(city_dir, context=None, output_dir=None, *, assumptions=None, evaluate=None):
    city_dir = Path(city_dir).resolve()
    _, c, costs = context or model.load()
    a = assumptions or tomllib.loads(ASSUMPTIONS.read_text())
    if a['schema']['family'] != c['metadata']['family'] or a['topology']['loop_geometry_accepted'] is not False:
        raise ValueError('unqualified maglev planning assumptions required')
    if a['topology']['radial'] != 'fixed-terminal-loops' or a['topology']['ring'] != 'two-independent-directed-circuits':
        raise ValueError('unsupported city topology requires its own adapter')
    if a['topology']['terminal_loop_circumferences_per_roundtrip'] != 2:
        raise ValueError('two terminal loop allowances required')
    for group in ('formation', 'topology', 'charging', 'depot'):
        for name, value in a[group].items():
            if type(value) in (int, float):
                model.positive(value, group+'.'+name)
    design_path = city_dir/'city.json'
    design = json.loads(design_path.read_text())
    if design.get('schema')!='osr-maglev-city-input/1':raise ValueError('current city input schema required')
    slug = design['city']['slug']
    use_operating=a.get('operating_plan',{}).get('enabled',False) and (evaluate is None or hasattr(evaluate,'for_formation'))
    if use_operating:
        geographic=json.loads((city_dir/(slug+'.corridor.geojson')).read_text())
    evaluate = evaluate or duty_evaluator(c)
    lines = []
    for line in design['lines']:
        f = formation(c, line['capacity'], [])
        stations = [s for s in design['stations'] if s['line'] == line['name']]
        operating=operating_plan.plan_line(c,f,line,stations,geographic['features'],interchanges=design.get('interchanges',[]),service_class=line.get('maglev_service_class','urban')) if use_operating else None
        lines.append(line_plan(c, a, f,line,operating['stations'] if operating else stations,line['service'],evaluate,operating=operating))
    source_paths = [*calculation_dependencies(),design_path,ASSUMPTIONS,Path(__file__),
                    model.INPUT,model.POLICY,Path(model.__file__),manufacturing.INPUT,Path(manufacturing.__file__),ROOT/'VERSION']
    for name in ('corridors.json', slug+'.stations.json', slug+'.corridor.geojson', 'alignment-policy.toml','site-context.json','map-context.json.gz'):
        path = city_dir/name
        if path.is_file(): source_paths.append(path)
    sources = {p.relative_to(ROOT).as_posix(): digest(p) for p in source_paths}
    station_input = city_dir/(slug+'.stations.json')
    retained_stations = json.loads(station_input.read_text()) if station_input.is_file() else design['stations']
    corridor_path = city_dir/'corridors.json'
    corridor = json.loads(corridor_path.read_text()) if corridor_path.is_file() else {}
    records = dict(city=design['city'], climate=design['climate'], retained_station_demand_records=retained_stations,
                   retained_station_design_records=design['stations'], retained_interchanges=design.get('interchanges', []),
                   retained_lines=design['lines'], retained_service_schedules=[dict(line=l['name'],**l['service']) for l in design['lines']],
                   retained_demand_metadata={k:v for k,v in corridor.items() if k != 'lines'},
                   full_route_geometry_sources=[p for p in sources if p.endswith(('.corridor.geojson', '/corridors.json'))],
                   use='Retained geography and demand only. No physical geometry, fleet, costs, soil or supplier acceptance transfers.')
    fleet = sum(l['fleet']['total'] for l in lines)
    cars = sum(l['fleet']['total']*l['formation']['cars'] for l in lines)
    by_class = {}
    for s in design['civil_segments']:
        by_class[s['class']] = by_class.get(s['class'], 0)+s['to_station_m']-s['from_station_m']
    strategy=optimisation.route_strategy(design,corridor)
    elevated=strategy['ordinary_viaduct_proposal_length_m']/1000
    if use_operating:
        ratios={line['line']:line['operating_plan']['chainage_scale'] for line in lines}
        elevated=sum((s['to_station_m']-s['from_station_m'])*ratios[s['line']] for s in design['civil_segments'] if s['class'] in {'at-grade','elevated'})/1000
        strategy.update(ordinary_cost_quantity_polyline_length_m=elevated*1000,
            cost_quantity_chainage_scale_by_line=ratios,
            cost_quantity_basis='Retained civil-class fractions scaled to measured geodesic route polylines; no surveyed alignment or structure classification approval')
    programme=manufacturing.city_programme(c,costs,lines,elevated)
    cost_rows=programme['scenarios']
    search=optimisation.study(c,costs)
    evac=evacuation.load();bare=search['beam_only_minimum_gross_allowance_candidate']
    packs=cars*evac['train']['doors_per_side_per_car_screen']*evac['train']['sides']
    beam_only=dict(target=evac['architecture']['target'],walkway_removal_approved=False,
        onboard_pack_count_hypothesis=packs,door_configuration_approved=False,
        added_vehicle_mass_kg=None,procurement_and_lifetime_cost_usd=None,net_system_saving_usd=None,
        gross_avoided_viaduct_scope_allowance_usd=bare['gross_avoided_scope_usd_dual_km']*elevated if bare else None,
        minimum_gross_only_candidate_id=bare['id'] if bare else None,
        selection_state='hold; landing at every stop position, accessible alternatives, fire/weather/fault/rescue and supplier acceptance unproved')
    from . import configuration
    for line in lines:configuration.selected(c,city=slug,cars=line['formation']['cars'])
    report = dict(configuration_revision=configuration.selected(c).revision,publication_role='primary-provisional-design',
                  financial_scope='Partial fleet, ordinary/terminal civil, station electrical, conditional foundation increment, fixed top-up electrical/mounts and independent rescue kits; complete installed programme unknown',
                  schema='osr-maglev-city-planning/1', architecture=c['metadata']['family'], version='0.5',
                  city=slug, name=design['name'], status='provisional-planning; physical-acceptance-open',
                  source_sha256=sources, planning_assumptions=a, routing_strategy=strategy, retained_records_file='retained-records.json', lines=lines,
                  diagnostics=dict(ring_closure_discrepancies=[dict(line=l['line'], discrepancy_m=l['topology']['ring_wrap_discrepancy_m'])
                                    for l in lines if l['topology']['ring_wrap_discrepancy_m'] not in (None, 0)],
                                   platform_body_allowance_shortfalls=sum((s['length_shortfall_screen_m'] or 0)>0 for l in lines for s in l['stations']),
                                   unresolved_capacity_targets=[l['line'] for l in lines if l.get('retained_capacity_target_met') is False],
                                   dwell_headway_conflicts=[l['line'] for l in lines if l['charging']['dwell_exceeds_peak_headway']],
                                   excessive_charging_dwell=[l['line'] for l in lines if not l['charging']['minimum_screen_passed']]),
                  totals=dict(lines=len(lines), station_records=sum(len(l['stations']) for l in lines),
                              retained_dense_benchmark_station_records=sum(l['operating_plan']['retained_dense_benchmark']['passenger_stops'] for l in lines) if use_operating else None,
                              retained_station_records=len(design['stations']),
                              added_terminal_service_zones=sum(l['topology'].get('terminal_service_zone_count',0) for l in lines),
                              powered_top_up_zones=sum(len(l['operating_plan']['powered_top_up_zones']) for l in lines) if use_operating else 0,
                              rescue_kits=sum(l['operating_plan']['rescue_kit_count'] for l in lines) if use_operating else 0,
                              transfer_spacing_conflicts=sum(len(l['operating_plan']['spacing_conflicts']) for l in lines) if use_operating else 0,
                              trainsets=fleet, cars=cars, gross_onboard_storage_kwh=cars*c['power']['services_battery_kwh_per_car'],
                              retained_route_length_m=sum(l['length_m'] for l in design['lines']),
                              added_single_direction_loop_beam_m=sum(l['topology']['added_single_direction_loop_beam_m'] for l in lines),
                              retained_civil_class_length_m=by_class),
                  costs=dict(scenarios=cost_rows, city_total_usd=None, beam_only_conditional_option=beam_only,
                             unpriced=['site-specific elevated conversion and clearance premiums', 'bridges and special structures', 'curve/site premiums', 'terminal curved detailing and land',
                                       'stations/platform alterations', 'depot/transfer/recovery equipment', 'charging/PV/storage/grid',
                                       'signalling/control/supervision', 'surveys/design/qualification', 'national production plant',
                                       'NRE and first article', 'EPC', 'initial spares/warranty/renewals/OPEX'],
                             old_city_costs_inherited=False, pilot_and_repeat_fleet_automatically_added=False),
                  gates=[dict(id=k, state='open', accepted=False, closure=v) for k,v in GATES],
                  design_complete=False, physical_validation=False, manufacturing_release=False, physical_release=False)
    report['affordability']=affordability.study(report,design)
    output = Path(output_dir) if output_dir else city_dir/'engineering/maglev'
    output.mkdir(parents=True, exist_ok=True)
    mapped=deepcopy(design)
    if use_operating:mapped['stations']=[s for l in lines for s in l['stations']]
    map_receipt=cartography.render(mapped,city_dir/(slug+'.corridor.geojson'),output/'network.svg')
    report.update(network_file='network.svg',network_sha256=digest(output/'network.svg'),map_context=map_receipt)
    (output/'manufacturing.json').write_text(json.dumps(programme,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    report['manufacturing_file']='manufacturing.json'
    report['manufacturing_sha256']=digest(output/'manufacturing.json')
    (output/'retained-records.json').write_text(json.dumps(records, ensure_ascii=False, sort_keys=True, indent=2)+'\n')
    report['retained_records_sha256'] = digest(output/'retained-records.json')
    (output/'summary.json').write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2)+'\n')
    write_readme(output, report)
    if output_dir is None:
        promote_city_readme(city_dir,report)
    return report


def write_readme(output, report):
    t = report['totals']
    rows = [f"# {report['name']} — v0.5 maglev city planning", '', '![Geographic corridor planning map](network.svg)', '',
            'Provisional planning from retained geography, station demand and service schedules. All physical and manufacturing release flags remain false.', '',
            f"{t['lines']} lines; {t['trainsets']} provisional trainsets / {t['cars']} cars; {t['gross_onboard_storage_kwh']:,.0f} kWh gross onboard storage.", '',
            '| Line | Cars | AW2 / AW3 | Bodies / assumed overall m | Topology | Peak / total trains | Dwell s |',
            '|---|---:|---:|---:|---|---:|---:|']
    for l in report['lines']:
        f=l['formation']
        rows.append(f"| {l['line']} | {f['cars']} | {f['aw2_passengers']} / {f['aw3_passengers']} | {f['nominal_body_length_m']:g} / {f['overall_length_assumption_m']:g} | {l['topology']['selected']} | {l['fleet']['peak']} / {l['fleet']['total']} | {l['charging']['dwell_seconds']:g} |")
    rows+=['','The requested urban plan uses a1.5km minimum and approximately2km average passenger spacing. Suburban4–5km is considered only with an explicit service classification and fixed, priced midway acceleration zones. Existing transfer nodes are retained; incompatible short gaps remain visible. The1km/88s case is a retained component benchmark. Exclusive whole-leg protection gives a conservative comparison headway; a180s sectioned or multiple-berth alternative needs its own proof and cost. No eligible full operating design is asserted.','']
    for line in report['lines']:
        rows.append(f"- {line['line']}: {line.get('service_class','benchmark')} exclusive-model headway {line['selected_peak_headway_seconds']:g}s versus source {line['retained_peak_headway_seconds']:g}s; normal capacity {line['aw2_capacity_per_direction_hour']:,.0f}/hour/direction; {len(line['kinematic_holds'])} held longitudinal cases; {len(line.get('operating_plan',{}).get('spacing_conflicts',[]))} transfer/terminal spacing conflicts.")
        if 'operating_plan' in line:
            p=line['operating_plan']
            rows.append(f"  Proposed operating plan: {p['operating_station_count']} mainline stops versus {p['retained_station_count']} retained access records; {line['topology']['terminal_service_zone_count']} additional terminal service/motor zones. Retained capacity target met: {str(line['retained_capacity_target_met']).lower()}. Consolidated access connections and every station/loop site remain unapproved.")
    rows+=city_brief.usp_markdown()+affordability.markdown(report)+city_brief.dispatch_markdown()
    diagnostics=report['diagnostics']
    if diagnostics['ring_closure_discrepancies']:
        rows += ['', 'Retained ring wrap distances do not close the complete geographic route. Recomputed closure adds the following distances to the input wrap values; actual closure alignment remains open: '+
                 '; '.join(f"{r['line']} {r['discrepancy_m']:,.1f} m" for r in diagnostics['ring_closure_discrepancies'])+'.']
    if diagnostics['platform_body_allowance_shortfalls']:
        rows += ['', f"{diagnostics['platform_body_allowance_shortfalls']} retained station platforms are shorter than the assumed overall-length-plus-10 m planning screen. Coupling envelopes, berthing and platform design require qualification."]
    option=report['costs']['beam_only_conditional_option']
    rows += ['', '**Integrated-beam/no-walkway target:** door-mounted evacuation is a study candidate. Continuous walkway removal is not approved. Necessary iron reaction faces, supports/foundations, joints and protection remain. '+str(option['onboard_pack_count_hypothesis'])+' onboard packs are a provisional door-count hypothesis; new mass, lifetime cost and net savings are unknown. Landing space, accessible alternatives, fire/weather/fault conditions and rescue/maintenance access must be proved along the complete route.', '']
    route=report['routing_strategy']
    rows += ['', f"**Predominantly elevated strategy:** {100*route['target_elevated_mainline_fraction']:g}% mainline elevation target; all ordinary sections proposed elevated. Ordinary viaduct planning length {route['ordinary_viaduct_proposal_length_m']/1000:,.3f} km includes {route['proposed_conversion_from_at_grade_m']/1000:,.3f} km converted from retained at-grade scope. Special crossings remain separate and unpriced.", '',
             'Straight tangents are preferred between demand anchors. Existing geographic alignments have not been rerouted or proved clear. Buildings/air rights, road and utility clearances, piers/foundations, wildlife/water passage, station access and construction access require evidence. Elevation does not establish zero displacement or zero environmental impact.', '']
    rows += ['', 'Formation matches both planning AW2/AW3 loads. Assumed overall length includes the shared configuration’s coupling gaps; body lengths alone exclude them. Platforms are screened against assumed overall length plus 10 m; final tolerances, overhang and berthing require qualification. Fleet is recomputed from hot AW3 services duty and selected station-resource headways, with 10% spares rounded up and one cold reserve per line. Pure trajectory and fixed-winding force feasibility are separate screens; unlocated intermediate-zone hints do not clear either hold.', '',
             'Default plans retain passenger-transfer nodes between independent fixed lines and choose fewer intermediate passenger stops. Ordinary retained stops remain demand/access records. Short transfer gaps remain explicit exceptions; no train switches or junction routing are introduced. Radial terminals have tangent-connected provisional R-L-R loops, three station-powered sections, two added service/motor stops per loop and explicit 150 m winding zones. Their 25 km/h arclength and lateral-acceleration screens do not qualify six-car curve phase, guidance, clearance, land or construction. Rings retain two independent directed circuits. Depot access and recovery remain unqualified.', '',
             'Charging alternatives compare240/400/600kW input per car at90% conversion, with exact connected fractions, hotel load, reserve and computed dwell. The displayed research candidate is not an eligible operating recommendation; changed50/60kWh packs require new formation confirmation. Main traction is supplied by separate station LSM equipment. Dwell is extended for the worst incoming services duty and terminal allowance. Multiple berths implied by dwell/headway require a conflict-free physical layout. Conversion loss is a declared planning allowance; taper, grade, curve forces, emergency reserve and missed charging remain open. No grid/PV/storage or site release is asserted.', '',
             '| Scenario | Repeat fleet allowance USD | Ordinary elevated allowance USD | Terminal civil allowance USD | Station electrical target USD | Foundation proposal increment USD | Booster electrical/mount targets USD | Rescue kits USD | Partial subtotal USD |',
             '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for c in report['costs']['scenarios']:
        rows.append(f"| {c['scenario']} | {c['repeat_fleet_allowance_usd']:,.0f} | {c['ordinary_elevated_allowance_usd']:,.0f} | {c.get('terminal_civil_allowance_usd',0):,.0f} | {c['station_electrical_allowance_usd']:,.0f} | {c['conditional_foundation_increment_usd']:,.0f} | {c.get('booster_electrical_allowance_usd',0)+c.get('booster_mount_allowance_usd',0):,.0f} | {c.get('rescue_kit_allowance_usd',0):,.0f} | {c['priced_scope_subtotal_usd']:,.0f} |")
    rows+=['','Terminal civil allowances use actual proposed arc length, beam/support counts and ordinary section quantity equivalents; curved detailing premiums remain unpriced. Added one-way service zones conservatively carry complete two-direction electrical package targets. The primary priced subtotal includes the conditional 6.5 m foundation proposal increment once; the previous smaller-foundation subtotal is retained only as a comparison. Every fixed booster has separately priced electrical equipment and mount/cabinet stock; rescue nodes have independently priced winch/portal/foundation kits. Higher voltage/current rating premiums, ground capacity, anchorage and access remain unaccepted and unpriced where unknown.','']
    rows += ['', '**Complete city programme cost remains unknown.** Partial allowances price each formation by car, coupling and shared train systems, plus measured section/reaction-steel quantities and explicit process assumptions per ordinary elevated route km. Station electrical rows price unquoted repeated fixed-group equipment targets separately; actual45-second charging and supply/thermal ratings require a configured quote. They exclude site-specific conversion/clearance premiums, terminal curved-detail/land premiums, special/bridge works, station buildings/access, depots, external utility reinforcement, land, NRE/plant, EPC and other scope listed in the structured report. Rates and productivity assumptions require supplier and site validation. Complete project costs and localisation remain unknown.', '',
             'Open acceptance work:', '']
    rows += ['- '+g['id']+': '+g['closure'] for g in report['gates']]
    programme=json.loads((output/'manufacturing.json').read_text())
    rows += ['', '## Manufacture and erection', '', 'Local work is proposed for repeated frames, cartridges, coils, concrete units and system integration. Input origins and local value added remain unverified. Factory capacity and programme duration require measured cycle times, cure/release criteria and site access.', '']
    for process in programme['process_routes']:
        rows += ['- **'+process['id']+'**: '+' → '.join(process['operations'])+'.']
    rows += ['', 'UK equipment candidates are capability leads, not prices or approved purchases. Rotary coil winding and CCL prestressing have explicit UK-manufacture statements; complete configuration, ratings and origin schedules remain open. See the linked manufacturing bill for dated primary sources.', '']
    rows += ['', '[Structured plan](summary.json) · [Preserved geography/demand records](retained-records.json) · [Quantity bills, manufacturing routes and factory equipment](manufacturing.json)', '',
             'The structured plan binds current source bytes and manufacturing bills with SHA-256.', '',
             '[Primary planning method]('+Path(os.path.relpath(ROOT/'engineering/ferrite_maglev/README.md',output)).as_posix().replace(' ','%20')+')', '',
             '<!-- Generated by engineering.ferrite_maglev.cities; primary planning only. -->', '']
    (output/'README.md').write_text('\n'.join(rows))


_CITY_WORKER=None


def _catalogue_designs():
    return sorted((ROOT/'cities/catalogue').glob('*/*/*/city.json'),key=lambda p:(city_slug(p)!='baghdad',str(p)))


def _initialise_city_worker(context,assumptions):
    """One immutable input context and memoised evaluator per spawned process."""
    global _CITY_WORKER
    _CITY_WORKER=(context,assumptions,duty_evaluator(context[1]))


def _generate_city_row(design,output,context,assumptions,evaluate):
    design=Path(design);output=Path(output) if output is not None else None
    report=generate(design.parent,context,output,assumptions=assumptions,evaluate=evaluate)
    package=output or design.parent/'engineering/maglev'
    return dict(city=report['city'],name=report['name'],catalogue_path=design.parent.relative_to(ROOT).as_posix(),
        package_path=package.relative_to(ROOT).as_posix() if package.is_relative_to(ROOT) else str(package),
        summary_sha256=digest(package/'summary.json'),retained_records_sha256=report['retained_records_sha256'],
        network_sha256=report['network_sha256'],readme_sha256=digest(package/'README.md'),manufacturing_sha256=report['manufacturing_sha256'],diagnostics=report['diagnostics'],
        trainsets=report['totals']['trainsets'],cars=report['totals']['cars'],
        open_gate_count=len(report['gates']),complete_city_programme_usd=None,physical_release=False,
        _source_sha256=report['source_sha256'])


def _generate_city_job(job):
    if _CITY_WORKER is None:raise ValueError('city worker was not initialised')
    return _generate_city_row(*job,*_CITY_WORKER)


def _parallel_city_rows(jobs,context,assumptions,workers):
    """Bound active/queued jobs; a failed worker cannot publish an index."""
    rows=[None]*len(jobs);next_job=0;pending={}
    pool=ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('spawn'),
        initializer=_initialise_city_worker,initargs=(context,assumptions))
    try:
        while next_job<len(jobs) or pending:
            while next_job<len(jobs) and len(pending)<workers:
                pending[pool.submit(_generate_city_job,jobs[next_job])]=next_job;next_job+=1
            done,_=wait(pending,return_when=FIRST_COMPLETED)
            # Inspect every completion before scheduling any further work.
            for future in sorted(done,key=lambda f:pending[f]):
                index=pending.pop(future);rows[index]=future.result()
    except BaseException:
        for future in pending:future.cancel()
        pool.shutdown(wait=True,cancel_futures=True)
        raise
    else:pool.shutdown(wait=True)
    return rows


def _verify_completed_city_row(row,design,output,before,current):
    package=Path(output) if output is not None else design.parent/'engineering/maglev'
    expected=package.relative_to(ROOT).as_posix() if package.is_relative_to(ROOT) else str(package)
    if (row.get('catalogue_path')!=design.parent.relative_to(ROOT).as_posix() or row.get('package_path')!=expected
            or row.get('physical_release') is not False or row.get('complete_city_programme_usd') is not None):
        raise ValueError('completed city worker identity or scope differs')
    for filename,key in [('summary.json','summary_sha256'),('retained-records.json','retained_records_sha256'),
                         ('network.svg','network_sha256'),('README.md','readme_sha256'),('manufacturing.json','manufacturing_sha256')]:
        path=package/filename
        if path.is_symlink() or not path.is_file() or digest(path)!=row.get(key):
            raise ValueError('completed city packet changed before index publication: '+str(path))
    recorded=row.pop('_source_sha256',None)
    if not isinstance(recorded,dict) or any(recorded.get(name)!=value for name,value in before.items()):
        raise ValueError('completed city packet used a different shared input revision')
    for relative,expected_hash in recorded.items():
        path=(ROOT/relative).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():raise ValueError('city source missing or outside repository')
        if relative not in current:current[relative]=digest(path)
        if current[relative]!=expected_hash:raise ValueError('city source changed during generation: '+relative)


def _city_calculation_snapshot():
    paths={*calculation_dependencies(),Path(__file__),ASSUMPTIONS,Path(model.__file__),
        model.INPUT,model.POLICY,Path(manufacturing.__file__),manufacturing.INPUT,ROOT/'VERSION'}
    return {path.relative_to(ROOT).as_posix():digest(path) for path in sorted(paths)}


def _publish_city_index(destination,index,markdown):
    """Prepare both files completely, then replace JSON last as batch receipt."""
    temporary=[]
    try:
        for target,text in [(destination.with_suffix('.md'),markdown),
                            (destination,json.dumps(index,ensure_ascii=False,sort_keys=True,indent=2)+'\n')]:
            with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=destination.parent,
                    prefix='.'+target.name+'.',suffix='.tmp',delete=False) as stream:
                temporary.append((Path(stream.name),target));stream.write(text);stream.flush();os.fsync(stream.fileno())
        for source,target in temporary:os.replace(source,target)
    finally:
        for source,_ in temporary:source.unlink(missing_ok=True)


def generate_all(output_root=None,*,workers=None):
    """Compile separate city packets; publish the index after all jobs succeed.

    Canonical generation uses at most four spawned workers. Alternate output
    roots remain serial by default for callers that inject test dependencies.
    """
    if workers is None:workers=4 if output_root is None else 1
    if type(workers) is not int or not 1<=workers<=4:raise ValueError('city workers must be an integer from1to4')
    before=_city_calculation_snapshot()
    context=model.load();assumptions=tomllib.loads(ASSUMPTIONS.read_text())
    designs=_catalogue_designs()
    if not designs:
        raise ValueError('retained catalogue is empty')
    jobs=[]
    for design in designs:
        output=None if output_root is None else Path(output_root)/design.parent.relative_to(ROOT/'cities/catalogue')
        jobs.append((str(design),str(output) if output is not None else None))
    if workers==1:
        evaluate=duty_evaluator(context[1])
        rows=[_generate_city_row(design,output,context,assumptions,evaluate) for design,output in jobs]
    else:rows=_parallel_city_rows(jobs,context,assumptions,workers)
    after=_city_calculation_snapshot()
    if before!=after:raise ValueError('city calculation inputs changed during generation; index not published')
    current=dict(after)
    for row,(design,output) in zip(rows,jobs):_verify_completed_city_row(row,Path(design),output,before,current)
    index = dict(schema='osr-maglev-city-index/1', architecture=context[1]['metadata']['family'],
                 city_count=len(rows), catalogue_design_paths=sorted(p.relative_to(ROOT).as_posix() for p in designs),
                 catalogue_complete=True, cities=rows, physical_release=False,
                 source_sha256={str(p.relative_to(ROOT)):digest(p) for p in (Path(__file__),ASSUMPTIONS,model.INPUT,model.POLICY)})
    destination = INDEX if output_root is None else Path(output_root)/'city-index.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    md=['# v0.5 maglev catalogue planning index', '',
        f'{len(rows)} retained cities have separate provisional maglev packages. Geography and demand are preserved; formation, duty, fleet, charging, depot quantities and partial costs are recomputed. Every physical acceptance gate remains open. Complete city costs remain unknown.', '',
        '| City | Cars | Trainsets | Ring closure discrepancies | Open gates | Planning package |', '|---|---:|---:|---:|---:|---|']
    for row in rows:
        package = ROOT/row['package_path']
        link=Path(os.path.relpath(package/'README.md', destination.parent)).as_posix().replace(' ', '%20')
        md.append(f"| {row['name']} | {row['cars']} | {row['trainsets']} | {len(row['diagnostics']['ring_closure_discrepancies'])} | {row['open_gate_count']} | [plan]({link}) |")
    _publish_city_index(destination,index,'\n'.join(md)+'\n')
    return index


def calculation_dependencies():
    """Transitive shared computational inputs used by generation and replay."""
    from . import station,station_structure,closure
    return [*optimisation.calculation_dependencies(),*cartography.source_paths(),Path(station.__file__),station.INPUT,*station_structure.source_paths(),*operating_plan.source_paths(),*city_brief.source_paths(),Path(closure.__file__),closure.INPUT]


def source_paths():
    """Unique city compiler input/output paths for an enclosing source snapshot.

    Reading this list neither regenerates packages nor edits entry notices.
    Missing generated output is reported by verify_index(), not manufactured.
    """
    paths={*calculation_dependencies(),Path(__file__),ASSUMPTIONS,model.POLICY,model.INPUT,Path(model.__file__),
           Path(manufacturing.__file__),Path(optimisation.__file__),optimisation.INPUT,Path(evacuation.__file__),evacuation.INPUT,ROOT/'VERSION',
           manufacturing.INPUT}
    for design in sorted((ROOT/'cities/catalogue').glob('*/*/*/city.json')):
        directory=design.parent
        slug=city_slug(design)
        paths.update((design,directory/'README.md'))
        for name in ('corridors.json',slug+'.stations.json',slug+'.corridor.geojson','alignment-policy.toml','map-context.json.gz',
                     'engineering/maglev/summary.json','engineering/maglev/retained-records.json','engineering/maglev/manufacturing.json','engineering/maglev/network.svg','engineering/maglev/README.md'):
            candidate=directory/name
            if candidate.is_file():
                paths.add(candidate)
    paths.update(p for p in (INDEX,INDEX.with_suffix('.md')) if p.is_file())
    return sorted(paths)


def verify_index(index_path=INDEX):
    """Read-only coverage, input freshness, output integrity and notice preflight."""
    errors=[]; cache={}; checked_outputs=0

    def read_json(path):
        try:
            result=json.loads(Path(path).read_text())
            if not isinstance(result,dict):
                raise ValueError('JSON object required')
            return result
        except (OSError,ValueError) as exc:
            errors.append(f'{path}: {type(exc).__name__}')
            return {}

    def check_hash(path,expected,label):
        path=Path(path)
        if path not in cache:
            cache[path]=digest(path) if path.is_file() else None
        if cache[path] is None:
            errors.append(label+': missing '+str(path))
        elif cache[path]!=expected:
            errors.append(label+': SHA-256 differs: '+str(path))

    def check_sources(mapping,label):
        if not isinstance(mapping,dict) or not mapping:
            errors.append(label+': source bindings missing')
            return
        for relative,expected in mapping.items():
            path=(ROOT/relative).resolve()
            if not path.is_relative_to(ROOT):
                errors.append(label+': source path outside repository')
            else:
                check_hash(path,expected,label)

    index=read_json(index_path)
    designs=sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/'cities/catalogue').glob('*/*/*/city.json'))
    entries=index.get('cities',[])
    if not isinstance(entries,list) or any(not isinstance(r,dict) for r in entries):
        errors.append('city entry objects missing')
        entries=[]
    if index.get('schema')!='osr-maglev-city-index/1' or index.get('physical_release') is not False:
        errors.append('index schema/release boundary differs')
    if index.get('catalogue_design_paths')!=designs or index.get('city_count')!=len(designs) or len(entries)!=len(designs):
        errors.append('index does not cover the exact current catalogue design-path set')
    expected_directories={str(Path(p).parent) for p in designs}
    entry_directories=[r.get('catalogue_path') for r in entries]
    if len(set(entry_directories))!=len(entries) or set(entry_directories)!=expected_directories:
        errors.append('city entries have missing, extra or duplicate catalogue paths')
    check_sources(index.get('source_sha256',{}),'index')
    for row in entries:
        label=row.get('city','unknown city')
        package=ROOT/row.get('package_path','missing-package')
        if not package.resolve().is_relative_to(ROOT):
            errors.append(label+': output package outside repository')
            continue
        for filename,key in (('summary.json','summary_sha256'),('retained-records.json','retained_records_sha256'),('README.md','readme_sha256'),('manufacturing.json','manufacturing_sha256'),('network.svg','network_sha256')):
            check_hash(package/filename,row.get(key),label)
            checked_outputs+=1
        report=read_json(package/'summary.json')
        if report.get('schema')!='osr-maglev-city-planning/1' or report.get('city')!=row.get('city'):
            errors.append(label+': compiled city identity/schema differs')
        if any(report.get(k) is not False for k in model.FLAGS):
            errors.append(label+': unqualified city release flags differ')
        if not {p.relative_to(ROOT).as_posix() for p in [Path(__file__),*calculation_dependencies()]}<=set(report.get('source_sha256',{})):errors.append(label+': required geometry/configuration source bindings missing')
        check_sources(report.get('source_sha256',{}),label)
        check_hash(package/'retained-records.json',report.get('retained_records_sha256'),label+' retained records')
        check_hash(package/'manufacturing.json',report.get('manufacturing_sha256'),label+' manufacturing')
        check_hash(package/'network.svg',report.get('network_sha256'),label+' map')
        if report.get('affordability',{}).get('schema')!=affordability.SCHEMA:
            errors.append(label+': current affordability scenarios missing')
        entry=ROOT/row.get('catalogue_path','missing-city')/'README.md'
        try:
            body=entry.read_bytes()
            if not body.startswith(NOTICE_START) or NOTICE_END not in body or b'engineering/maglev/README.md' not in body.split(NOTICE_END,1)[0]:
                errors.append(label+': primary entry notice missing or incomplete')
            if 'affordability' in report:
                design=read_json(entry.parent/'city.json')
                expected=NOTICE_START.decode()+city_brief.frontdoor(report,design)+NOTICE_END.decode()
                if body.decode()!=expected:errors.append(label+': detailed public brief differs from current quantities')
        except OSError:
            errors.append(label+': city entry README missing')
    return dict(current=not errors,errors=errors,city_count=len(entries),
                expected_city_count=len(designs),checked_outputs=checked_outputs,physical_release=False)


def replay_city(report, *, cycles=2, start_soc=None, charger_efficiency=0.90,
                regen_available=False, missed_charge_events=(1,)):
    """Replay representative trains through compiled hot duty and charging events.

    Event numbers are one-based per line and continue across circuits. Charging
    efficiency is an explicit DC supply-to-pack allowance; train motion remains
    the declared unqualified duty model. This is an offline energy ledger, not
    a traffic, protection-reserve or physical route acceptance simulation.
    """
    count(cycles, 'replay cycles')
    if cycles>100:
        raise ValueError('at most 100 replay circuits required')
    model.positive(charger_efficiency, 'charger efficiency')
    if charger_efficiency>1 or type(regen_available) is not bool:
        raise ValueError('bounded efficiency and explicit regeneration state required')
    missed=set(missed_charge_events)
    for event in missed:
        count(event, 'missed charge event')
    if report.get('schema')!='osr-maglev-city-planning/1' or report.get('physical_release') is not False:
        raise ValueError('unqualified compiled city plan required')
    declared=report.get('source_sha256',{})
    required={p.relative_to(ROOT).as_posix() for p in [Path(__file__),*calculation_dependencies()]}
    source_current=isinstance(declared,dict) and required<=set(declared) and all((ROOT/p).is_file() and digest(ROOT/p)==h for p,h in declared.items())
    if not source_current:
        raise ValueError('compiled city sources changed; regenerate before replay')
    lines=[]
    for line in report['lines']:
        f=line['formation']; duty=line['duty']; charge=line['charging']
        soc=f['normal_soc_high'] if start_soc is None else start_soc
        if type(soc) not in (int,float) or not math.isfinite(soc) or not 0<=soc<=1:
            raise ValueError('initial SOC in [0,1] required')
        capacity=model.positive(f['eol_capacity_kwh'],'EOL storage')
        lower=capacity*f['normal_soc_low']; upper=capacity*f['normal_soc_high']
        energy=capacity*soc
        initial=energy; elapsed=0.0; trace=[]; breaches=[]
        totals=dict(motion_kwh=0.0, stationary_services_kwh=0.0, supply_dc_kwh=0.0,
                    available_dc_kwh=0.0, curtailed_dc_kwh=0.0,
                    stored_charge_kwh=0.0, charger_loss_kwh=0.0, curtailed_pack_energy_kwh=0.0)
        if not lower<=energy<=upper:
            breaches.append(dict(event=0, reason='initial SOC outside normal window', energy_kwh=energy))
        for circuit in range(cycles):
            for arrival in duty['arrival_events_per_circuit']:
                event=len(trace)+1
                motion=arrival['hot_regen_motion_kwh' if regen_available else 'hot_no_regen_motion_kwh']
                energy-=motion; elapsed+=arrival['moving_seconds']
                arrival_energy=energy
                dwell=charge['dwell_seconds']; effective=charge['effective_charge_seconds']
                overhead=dwell-effective
                hotel=duty['hot_hotel_kw']; services=hotel*dwell/3600
                skipped=event in missed
                available=0.0 if skipped else charge['candidate_kw_per_train']*effective/3600
                offered=available*charger_efficiency
                # No energy is silently created/clipped at the lower bound. A
                # negative ledger is retained as an infeasibility diagnostic.
                before_charging=energy-hotel*overhead/3600
                stored=min(offered,max(0.0,upper-(energy-services)))
                curtailed=offered-stored
                supply=stored/charger_efficiency
                energy=energy-services+stored
                minimum=min(arrival_energy,before_charging,energy)
                if minimum<lower:
                    breaches.append(dict(event=event, reason='below normal SOC floor', minimum_energy_kwh=minimum,
                                         shortfall_kwh=lower-minimum))
                elapsed+=dwell
                totals['motion_kwh']+=motion; totals['stationary_services_kwh']+=services
                totals['supply_dc_kwh']+=supply; totals['stored_charge_kwh']+=stored
                totals['available_dc_kwh']+=available; totals['curtailed_dc_kwh']+=available-supply
                totals['charger_loss_kwh']+=supply-stored; totals['curtailed_pack_energy_kwh']+=curtailed
                trace.append(dict(event=event,circuit=circuit+1,station=arrival['destination_station'],
                                  elapsed_seconds=elapsed, motion_kwh=motion, arrival_energy_kwh=arrival_energy,
                                  stationary_services_kwh=services, missed_charge=skipped,
                                  available_dc_kwh=available, supply_dc_kwh=supply, charger_loss_kwh=supply-stored,
                                  curtailed_dc_kwh=available-supply,
                                  stored_charge_kwh=stored, curtailed_pack_energy_kwh=curtailed,
                                  departure_energy_kwh=energy, departure_soc=energy/capacity,
                                  minimum_event_energy_kwh=minimum, normal_window_passed=minimum>=lower))
        balance=initial-totals['motion_kwh']-totals['stationary_services_kwh']+totals['stored_charge_kwh']
        lines.append(dict(line=line['line'], representative_trains_replayed=1,
                          compiled_fleet_total=line['fleet']['total'], retained_headway_seconds=line['retained_peak_headway_seconds'],selected_headway_seconds=line['selected_peak_headway_seconds'],
                          initial_energy_kwh=initial, final_energy_kwh=energy, minimum_normal_energy_kwh=lower,
                          eol_capacity_kwh=capacity, elapsed_seconds=elapsed, cycles=cycles,
                          energy_ledger_residual_kwh=energy-balance, energy_totals=totals,
                          normal_window_passed=not breaches, breaches=breaches, events=trace,
                          missed_charge_events_requested=sorted(missed),
                          missed_charge_events_outside_replay=sorted(missed-set(range(1,len(trace)+1))),
                          protected_emergency_energy_kwh=None, emergency_reserve_passed=None,
                          route_acceptance=False, force_acceptance=False))
    return dict(schema='osr-maglev-city-replay/1', city=report['city'],
                compiled_plan_sha256=sha256(json.dumps(report,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
                source_sha256=report['source_sha256'], replay_generator_sha256=digest(__file__),
                source_current=True, charger_efficiency=charger_efficiency,
                regeneration_available=regen_available, load='AW3; hot assumed efficiencies', lines=lines,
                normal_window_passed=all(l['normal_window_passed'] for l in lines),
                protected_emergency_energy_kwh=None, emergency_reserve_passed=None,
                physical_release=False, route_acceptance=False, force_acceptance=False,
                exclusions=['fleet traffic/conflicts and charging simultaneity', 'grade/curves/wind and qualified traffic',
                            'battery voltage/thermal/taper and internal losses', 'physical force/control/protection',
                            'grid/PV/storage availability', 'protected emergency reserve'])


def find_city(slug):
    matches=[]
    for path in sorted((ROOT/'cities/catalogue').glob('*/*/*/city.json')):
        if city_slug(path)==slug:
            matches.append(path.parent)
    if len(matches)!=1:
        raise ValueError('expected one retained city for '+slug+f'; found {len(matches)}')
    return matches[0]


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('city',nargs='?',help='retained catalogue city slug')
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--all', action='store_true')
    mode.add_argument('--design', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--simulate',action='store_true',help='write offline hot AW3 SOC replay with a missed first charge')
    parser.add_argument('--cycles',type=int,default=2)
    parser.add_argument('--charger-efficiency',type=float,default=.9)
    parser.add_argument('--missed-charge',type=int,action='append',help='one-based event number per line; default 1')
    parser.add_argument('--regen',action='store_true')
    args=parser.parse_args(argv)
    if sum((bool(args.city),bool(args.all),bool(args.design)))!=1:
        parser.error('choose exactly one city slug, --design or --all')
    if args.simulate and args.all:
        parser.error('choose a single city for representative-train replay')
    try:
        city_dir=None if args.all else (args.design.parent if args.design else find_city(args.city))
        result=generate_all(args.output) if args.all else generate(city_dir, output_dir=args.output)
        if args.simulate:
            replay=replay_city(result,cycles=args.cycles,charger_efficiency=args.charger_efficiency,
                               regen_available=args.regen,missed_charge_events=args.missed_charge or (1,))
            output=args.output or city_dir/'engineering/maglev'
            (output/'replay.json').write_text(json.dumps(replay,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
            print(f"{result['city']}: representative-train offline SOC replay; normal window passed={replay['normal_window_passed']}; emergency reserve unknown; route acceptance=false")
            return 0
    except (ValueError,FileNotFoundError) as exc:
        parser.exit(2,f'{parser.prog}: error: {exc}\n')
    print(f"{result['city_count']} provisional city packages" if args.all else f"{result['city']}: provisional city package")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
