"""Chronological train visits from declared city stations, fleets and headways.

Turnback stock cannot depart before its prior trip finishes at that terminus.
Timings use an explicit average-speed screen and need full timetable validation.
"""
from __future__ import annotations
import math


def clock_minutes(text):
    h,m=map(int,text.split(':'))
    return h*60+m


def network_duty(design: dict, scenario: dict, *, average_speed_kmh: float,
                 initial_soc: float, auxiliary_kw_per_car: float, regen_fraction: float,
                 minutes: int = 1560, movement_profiles: dict | None = None) -> dict:
    if average_speed_kmh<=0 or not 0<=initial_soc<=1 or not 0<=regen_fraction<=1:
        raise ValueError('invalid network duty assumptions')
    station_cfg={s['id']:s for s in scenario['stations']}
    sites={s['station']:dict(initial_soc=s['storage_initial_soc'],modules=s['storage_capacity_kwh']/s['storage_module_kwh'],
        pv_kw=s['pv_nameplate_kw'],grid_kw=s['grid_import_kw'],charger_kw=s['charger_max_kw'],
        charger_efficiency=s.get('charger_efficiency',0.98),contact_count=s.get('charger_contact_count',2),
        charger_bus_voltage_v=s.get('charger_bus_voltage_v',650.0),charger_max_current_a=s.get('charger_max_current_a',825.0)) for s in scenario['sites']}
    trains={};visits=[];departures=[];missed_dispatches=[];mass={};journeys=[];distance_findings=[]
    cars=scenario['consist']['car_count']
    movement={(row['line'],row['heading'],row['from_station'],row['to_station']):row for row in (movement_profiles or {}).get('sections',[])}
    for fleet in scenario['fleets']:
        line=next(l for l in design['lines'] if l['name']==fleet['line'])
        ordered=sorted([s for s in design['stations'] if s['line']==fleet['line']],key=lambda s:s['s_m'])
        is_ring=line.get('shape')=='ring'
        dispatch_points=fleet['dispatch_points']
        if not dispatch_points or any(p['heading'] not in ('forward','reverse') or p['station'] not in {s['id'] for s in ordered} for p in dispatch_points):
            raise ValueError('dispatch points must name a line station and operating direction')
        operating_line=next((l for l in scenario.get('lines',[]) if l['id']==fleet['line']),None)
        edge_distances={}
        if operating_line:
            entries=operating_line['stations']
            for a,b in zip(entries,entries[1:]):
                edge_distances[frozenset((a['id'],b['id']))]=float(b['distance_from_prev_m'])/1000
        wrap_m=float((operating_line or {}).get('ring_wrap_length_m',line.get('ring_wrap_length_m',0)))
        if is_ring:
            if wrap_m<=0:
                wrap_m=line['length_m']-ordered[-1]['s_m']+ordered[0]['s_m']
            edge_distances[frozenset((ordered[-1]['id'],ordered[0]['id']))]=wrap_m/1000
            operating_m=sum(edge_distances.values())*1000 if operating_line else ordered[-1]['s_m']-ordered[0]['s_m']+wrap_m
            if abs(operating_m-line['length_m'])>1:
                distance_findings.append(dict(line=fleet['line'],declared_geometry_m=line['length_m'],controlled_operating_m=operating_m,
                    finding='operating edge distances and declared alignment length require reconciliation'))
        pool=[]
        for i in range(fleet['trainset_count']):
            tid=f"{fleet['line']}-train-{i+1:03d}"
            trains[tid]=dict(cars=cars,initial_soc=initial_soc,energy_kwh_km=scenario['consist']['energy_kwh_per_car_km']*cars,
                             auxiliary_kw=auxiliary_kw_per_car*cars,mass_factor=1.0,service_intervals=[],service_journeys=[])
            point=dispatch_points[i%len(dispatch_points)]
            pool.append(dict(id=tid,ready=0.0,heading=point['heading'],station=point['station']))
        service_start=clock_minutes(fleet['service_start'])
        dispatches=[]
        for phase in fleet['schedule']:
            start=clock_minutes(phase['from']);end=clock_minutes(phase['to'])
            if start<service_start:start+=1440
            if end<=start:end+=1440
            for day in range(math.ceil(minutes/1440)):
                for minute in range(start+day*1440,min(end+day*1440,minutes),phase['headway_min']):
                    for point in fleet['dispatch_points']:
                        dispatches.append((minute,point['heading'],point['station']))
        for start,heading,dispatch_station in sorted(dispatches):
            available=[t for t in pool if t['ready']<=start and t['heading']==heading and t['station']==dispatch_station]
            if not available:
                missed_dispatches.append(dict(line=fleet['line'],minute=start,heading=heading,station=dispatch_station,reason='trainset-not-ready-at-dispatch-terminus'))
                continue
            stock=min(available,key=lambda t:(t['ready'],t['id']))
            tid=stock['id'];t=float(start)
            route=ordered if heading=='forward' else list(reversed(ordered))
            if is_ring:
                index=next(i for i,s in enumerate(route) if s['id']==dispatch_station)
                route=route[index:]+route[:index]
                route=route+[route[0]]
            elif route[0]['id']!=dispatch_station:
                raise ValueError('radial dispatch point must be the departure terminus for its direction')
            journey_id=f'{tid}-departure-{start}-{heading}'
            travelled=0.0
            for i,station in enumerate(route):
                dwell=station_cfg[station['id']]['dwell_seconds']/60
                departure=t+dwell
                if station['id'] in sites and t<minutes:
                    visits.append(dict(journey=journey_id,train=tid,site=station['id'],arrival_min=t,departure_min=min(departure,minutes),
                                       required_charge_kwh=0.0,missed=720<=t<726))
                if i<len(route)-1:
                    target=route[i+1]
                    pair=frozenset((target['id'],station['id']))
                    distance=edge_distances.get(pair,abs(target['s_m']-station['s_m'])/1000)
                    if is_ring and pair==frozenset((ordered[-1]['id'],ordered[0]['id'])):
                        distance=wrap_m/1000
                    if distance<=0:
                        raise ValueError('controlled station-to-station distances must be positive')
                    travelled+=distance
                    if movement_profiles is not None:
                        profile=movement.get((fleet['line'],heading,station['id'],target['id']))
                        if profile is None or abs(profile['distance_m']-distance*1000)>1:
                            raise ValueError('native movement profile is missing or differs from the controlled edge')
                        travel=profile['travel_seconds']/60
                    else:
                        travel=max(0.5,distance/average_speed_kmh*60)
                    if departure<minutes:
                        demand=distance*trains[tid]['energy_kwh_km']
                        departures.append(dict(journey=journey_id,from_station=station['id'],to_station=target['id'],heading=heading,train=tid,minute=math.ceil(departure),distance_km=distance,
                            travel_minutes=travel,arrival_minute=math.ceil(departure+travel),regenerative_kwh=demand*regen_fraction))
                    t=departure+travel
                else:
                    t=departure
            trains[tid]['service_intervals'].append((start,min(t,minutes)))
            trains[tid]['service_journeys'].append((start,min(t,minutes),journey_id))
            journeys.append(dict(id=journey_id,train=tid,line=fleet['line'],heading=heading,dispatch_station=dispatch_station,
                arrival_station=route[-1]['id'],planned_start_minute=start,planned_finish_minute=t,distance_km=travelled))
            stock['ready']=t;stock['station']=route[-1]['id']
            stock['heading']=heading if is_ring else 'reverse' if heading=='forward' else 'forward'
        mass[fleet['line']]=dict(reference_mass_kg=scenario['consist']['mass_kg'],cars=cars)
    return dict(trains=trains,sites=sites,visits=visits,departures=departures,mass=mass,
                missed_dispatches=missed_dispatches,journeys=journeys,distance_findings=distance_findings,
                distance_basis='controlled scenario edge distances and wrap where supplied',average_speed_kmh=average_speed_kmh,
                movement_basis=(movement_profiles or {}).get('basis','average-speed planning screen'),
                timetable_accepted=False)
