"""Demand-led, counted-fleet terminal plans for subsequent native fleet replay.

This event planner uses explicit travel-time hypotheses. It does not replace the
force-driven fleet evaluator, stored-energy event ordering or protected controls.
"""
from collections import deque
from math import ceil,acos,sqrt,isfinite,fsum
from heapq import heappush,heappop
from pathlib import Path
import json
from engineering.station_rail.common import identity,digest
from . import ROOT,FLAGS

BRIEF='engineering/railway_closure/brief.json'


def brief(root=ROOT):
    p=json.loads((Path(root)/BRIEF).read_bytes())
    if p.get('schema')!='osr-railway-closure-brief/1':raise ValueError('Explicit closure brief required')
    if p['route_length_m']<=0 or p['passenger_places']<=0 or not 0<p['planning_occupancy']<=1:
        raise ValueError('Positive route and passenger design required')
    return p


def _number(v,label,positive=False):
    if type(v) not in (int,float) or not isfinite(v) or (v<=0 if positive else v<0):
        raise ValueError('Finite '+('positive ' if positive else 'nonnegative ')+label+' required')
    return float(v)


def _seal(v):v['evaluation_id']=identity(v);return v


def terminal_geometry(p,train_length_m=105.25):
    """Proposed geometric envelope, not an independently approved track layout."""
    L=_number(train_length_m,'train length',True);platform=p['station_platform_length_m']
    spacing=p['station_track_centres_m'];radius=p['crossover_radius_m_hypothesis']
    if platform<L+4 or spacing<=2.5+p['station_platform_width_m'] or spacing>=4*radius:
        raise ValueError('Train/platform and declared crossover envelopes do not fit')
    angle=acos(1-spacing/(2*radius));arc=2*radius*angle
    dx=2*radius*__import__('math').sin(angle)
    curve_accel=p['terminal_speed_cap_m_s']**2/radius
    # Two main tracks extend through the terminal platforms beyond both stops.
    main_track_m=2*(p['route_length_m']+platform)
    pocket_track_m=2*p['terminal_pocket_length_m']
    crossover_track_m=2*arc
    v=dict(schema='osr-pilot-terminal-geometry/1',units='m',
        train_reference='fixed train geometric centre; not a direction-dependent nose or certified stopping reference',
        body_coordinates='nose-to-tail stock x; world_x=centre+L/2-body_x eastbound, centre-L/2+body_x westbound',
        station_reference_centres_m=dict(A=0.,B=p['route_length_m']),
        platform_length_m=platform,train_length_m=L,stopping_tolerance_m=2.,
        nominal_end_margin_m=(platform-L)/2,station_track_centres_m=spacing,
        boarding_platforms_per_station=2,platform_width_m=p['station_platform_width_m'],
        one_sided_doors='Both boarding faces placed on the declared physical door side; not assumed usable from either side',
        pocket_capacity_trainsets_per_station=1,station_parked_capacity_trainsets=3,
        crossover=dict(radius_m=radius,angle_rad=angle,arc_length_m=arc,
            longitudinal_projection_m=dx,lateral_acceleration_at_speed_cap_m_s2=curve_accel,
            dynamic_ride_guidance_acceptance=False),
        track_quantities=dict(main_and_platform_track_m=main_track_m,pocket_track_m=pocket_track_m,
            crossover_track_m=crossover_track_m,total_track_m=main_track_m+pocket_track_m+crossover_track_m),
        turnout_switch_units=4,
        scope='One counted terminal pocket and crossover per station, with two boarding faces. Exact turnout, crossing, clearances, accessibility and structural design remain to be verified.',
        geometry_verified=False,**FLAGS)
    v['geometry_id']=identity(v);return v


def _gap(start,duration,bookings):
    """First nonoverlapping interval; departure reservations are explicit inputs."""
    t=start
    for a,b in sorted(bookings):
        if t+duration<=a:break
        if t<b and t+duration>a:t=b
    return t


def plan(candidate_id,travel_times,p,*,headway_s,phase_b_s,active_trainsets):
    if len(candidate_id)!=64 or any(c not in '0123456789abcdef' for c in candidate_id):raise ValueError('Explicit system candidate required')
    h=_number(headway_s,'headway',True);phase=_number(phase_b_s,'opposite phase')
    if phase>=h or type(active_trainsets) is not int or active_trainsets<2 or active_trainsets>8:
        raise ValueError('Bounded explicit initial active fleet and phase required')
    if set(travel_times)!={'A','B'}:raise ValueError('Both station departure travel times required')
    times={s:_number(t,'travel time',True) for s,t in travel_times.items()}
    if max(times.values())>3600:raise ValueError('Travel-time planning domain exceeded')
    n=p['nominal_departures_per_direction'];dwell=p['dwell_s'];turn=p['turnaround_maneuver_s'];clear=p['route_release_allowance_s']
    # These reservations count a conservative shared terminal movement resource.
    # The 30 s departure clearance is a declared hypothesis, not a signalling limit.
    departure_clear=30.
    slots=[dict(id=f'{s}-{i:03d}',station=s,time_s=i*h+(phase if s=='B' else 0.)) for i in range(n) for s in ('A','B')]
    bookings={s:[(r['time_s'],r['time_s']+departure_clear) for r in slots if r['station']==s] for s in ('A','B')}
    ready={s:[] for s in ('A','B')};trains=[];stationary={s:0 for s in ready};events=[];queue=[];sequence=0
    def push(t,priority,kind,payload):
        nonlocal sequence
        sequence+=1;heappush(queue,(t,priority,sequence,kind,payload))
    for s,count in (('A',ceil(active_trainsets/2)),('B',active_trainsets//2)):
        for i in range(count):
            name=s+'-'+str(i+1)
            first=phase if s=='B' else 0.
            at=0. if i==0 else _gap(first+departure_clear,turn,bookings[s])+turn
            if i>0:bookings[s].append((at-turn,at))
            train=dict(id=name,initial_station_id=s,initial_position_m=0.,ready_at_s=at,role='active')
            trains.append(train);stationary[s]+=1;push(at,0,'ready',dict(train_id=name,station=s))
    for s in slots:push(s['time_s'],2,'departure',s)
    occupied_until={s:0. for s in ready};departures=[];peak_parked=dict(stationary)
    while queue:
        now,priority,seq,kind,data=heappop(queue)
        s=data.get('station')
        if kind=='ready':
            ready[s].append((now,data['train_id']));ready[s].sort()
            events.append(dict(kind='train-ready',time_s=now,station=s,train_id=data['train_id']));continue
        if kind=='arrival':
            stationary[s]+=1;peak_parked[s]=max(peak_parked[s],stationary[s])
            at=_gap(now+dwell,turn,bookings[s]);bookings[s].append((at,at+turn))
            events.append(dict(kind='arrival',time_s=now,station=s,train_id=data['train_id'],
                maneuver_start_s=at,maneuver_end_s=at+turn))
            push(at+turn,0,'ready',dict(train_id=data['train_id'],station=s));continue
        reason=None
        if not ready[s]:reason='no-counted-train-ready'
        elif now<occupied_until[s]:reason='same-direction-route-still-occupied'
        if reason:
            departures.append(dict(slot_id=data['id'],departure_station_id=s,time_s=now,train_id=None,state='held',reason=reason));continue
        _,tid=ready[s].pop(0);stationary[s]-=1;other='B' if s=='A' else 'A'
        arrived=now+times[s];occupied_until[s]=arrived+clear
        departures.append(dict(slot_id=data['id'],departure_station_id=s,arrival_station_id=other,
            departure_time_s=now,arrival_time_hypothesis_s=arrived,train_id=tid,state='planned',reason=None))
        push(arrived,1,'arrival',dict(station=other,train_id=tid))
    capacity=p['passenger_places']*3600/h*p['planning_occupancy']
    demand=capacity>=p['peak_demand_pphpd'];complete=all(d['state']=='planned' for d in departures)
    parked_ok=max(peak_parked.values())<=3
    spare=max(1,ceil(active_trainsets*p['spare_fraction']))
    value=dict(schema='osr-pilot-service-plan/1',candidate_id=candidate_id,headway_s=h,opposite_phase_s=phase,
        planning_capacity_pphpd=capacity,peak_demand_pphpd=p['peak_demand_pphpd'],
        active_trainsets=active_trainsets,spare_trainsets=spare,total_trainsets=active_trainsets+spare,
        counted_initial_trains=trains,departures=departures,terminal_events=events,
        terminal_resource_bookings={s:sorted(rows) for s,rows in bookings.items()},peak_parked_trainsets=peak_parked,
        tests=dict(demand=demand,maximum_wait=h<=p['maximum_wait_s'],
            journey_time=max(times.values())<=p['maximum_pair_journey_s'],all_slots_have_counted_ready_train=complete,
            station_parked_capacity=parked_ok),
        planned_service_complete=demand and complete and parked_ok and h<=p['maximum_wait_s'] and max(times.values())<=p['maximum_pair_journey_s'],
        hypotheses=dict(travel_times_s=times,dwell_s=dwell,turnaround_maneuver_s=turn,
            route_release_allowance_s=clear,departure_terminal_clearance_s=departure_clear),
        native_force_driven_fleet_replayed=False,station_store_timing_evaluated=False,
        protected_service_qualified=False,
        scope='Nominal event/resource plan using supplied travel-time and terminal maneuver hypotheses. Native causal fleet replay, braking/faults, actual turnout geometry and operational protection remain separate.',**FLAGS)
    return _seal(value)


def explore(candidate_id,travel_times,*,root=ROOT):
    p=brief(root);rows=[]
    for h in p['headway_options_s']:
        for phase in p['opposite_departure_phase_options_s']:
            if phase>=h:continue
            for fleet in p['initial_active_fleet_options']:
                rows.append(plan(candidate_id,travel_times,p,headway_s=h,phase_b_s=phase,active_trainsets=fleet))
    return rows
