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
                 minutes: int = 1560) -> dict:
    if average_speed_kmh<=0 or not 0<=initial_soc<=1 or not 0<=regen_fraction<=1:
        raise ValueError('invalid network duty assumptions')
    station_cfg={s['id']:s for s in scenario['stations']}
    sites={s['station']:dict(initial_soc=s['storage_initial_soc'],modules=s['storage_capacity_kwh']/s['storage_module_kwh'],
        pv_kw=s['pv_nameplate_kw'],grid_kw=s['grid_import_kw'],charger_kw=s['charger_max_kw'],
        charger_efficiency=s.get('charger_efficiency',0.98),contact_count=s.get('charger_contact_count',2),
        charger_bus_voltage_v=s.get('charger_bus_voltage_v',650.0),charger_max_current_a=s.get('charger_max_current_a',825.0)) for s in scenario['sites']}
    trains={};visits=[];departures=[];missed_dispatches=[];mass={}
    cars=scenario['consist']['car_count']
    for fleet in scenario['fleets']:
        line=next(l for l in design['lines'] if l['name']==fleet['line'])
        ordered=sorted([s for s in design['stations'] if s['line']==fleet['line']],key=lambda s:s['s_m'])
        is_ring=line.get('shape')=='ring'
        pool=[]
        for i in range(fleet['trainset_count']):
            tid=f"{fleet['line']}-train-{i+1:03d}"
            trains[tid]=dict(cars=cars,initial_soc=initial_soc,energy_kwh_km=scenario['consist']['energy_kwh_per_car_km']*cars,
                             auxiliary_kw=auxiliary_kw_per_car*cars,mass_factor=1.0,service_intervals=[])
            pool.append(dict(id=tid,ready=0.0,heading='forward' if is_ring or i%2==0 else 'reverse'))
        service_start=clock_minutes(fleet['service_start'])
        dispatches=[]
        for phase in fleet['schedule']:
            start=clock_minutes(phase['from']);end=clock_minutes(phase['to'])
            if start<service_start:start+=1440
            if end<=start:end+=1440
            for minute in range(start,min(end,minutes),phase['headway_min']):
                for point in fleet['dispatch_points']:
                    dispatches.append((minute,point['heading']))
        for start,heading in sorted(dispatches):
            available=[t for t in pool if t['ready']<=start and t['heading']==heading]
            if not available:
                missed_dispatches.append(dict(line=fleet['line'],minute=start,heading=heading,reason='trainset-not-ready-at-dispatch-terminus'))
                continue
            stock=min(available,key=lambda t:(t['ready'],t['id']))
            tid=stock['id'];t=float(start)
            route=ordered if heading=='forward' else list(reversed(ordered))
            if is_ring:
                route=route+[route[0]]
            for i,station in enumerate(route):
                dwell=station_cfg[station['id']]['dwell_seconds']/60
                departure=t+dwell
                if station['id'] in sites and t<minutes:
                    visits.append(dict(train=tid,site=station['id'],arrival_min=t,departure_min=min(departure,minutes),
                                       required_charge_kwh=0.0,missed=720<=t<726))
                if i<len(route)-1:
                    target=route[i+1]
                    distance=abs(target['s_m']-station['s_m'])/1000
                    if is_ring and i==len(route)-2:
                        distance=(line['length_m']-station['s_m']+target['s_m']+line.get('ring_wrap_length_m',0))/1000
                    travel=max(0.5,distance/average_speed_kmh*60)
                    if departure<minutes:
                        demand=distance*trains[tid]['energy_kwh_km']
                        departures.append(dict(train=tid,minute=math.ceil(departure),distance_km=distance,
                            travel_minutes=travel,arrival_minute=math.ceil(departure+travel),regenerative_kwh=demand*regen_fraction))
                    t=departure+travel
                else:
                    t=departure
            trains[tid]['service_intervals'].append((start,min(t,minutes)))
            stock['ready']=t;stock['heading']=heading if is_ring else 'reverse' if heading=='forward' else 'forward'
        mass[fleet['line']]=dict(reference_mass_kg=scenario['consist']['mass_kg'],cars=cars)
    return dict(trains=trains,sites=sites,visits=visits,departures=departures,mass=mass,
                missed_dispatches=missed_dispatches,average_speed_kmh=average_speed_kmh,
                timetable_accepted=False)
