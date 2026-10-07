"""Dispatch/energy coupling with physical station identity and held-stock feedback.

Declared dispatch opportunities use native section timing. A train that cannot
retain reserve after its next leg stays at that station and continues charging;
it cannot appear at a later terminus or serve a concurrent dispatch. Minute
resolution, berth assumptions and absent conflict authorities remain study gates.
"""
from collections import defaultdict
import math
from .battery_profiles import chronological_energy,discharge_limit_kw
from .network_energy_duty import clock_minutes


def controlled_network_energy(design,scenario,movement_profiles,onboard,stationary,trains,sites,minutes,*,
        ambient_c=45,seasonal_solar_factor=.65,cleaning_factor=.9,reserve_soc=.2,setup_seconds=20,outages=None,regen_fraction=.15,
        retain_section_events=False):
    edges={(r['line'],r['heading'],r['from_station'],r['to_station']):r for r in movement_profiles['sections']}
    station_cfg={s['id']:s for s in scenario['stations']};actors={};opportunities=defaultdict(list);routes={}
    for fleet in scenario['fleets']:
        line=fleet['line'];layout=next(l for l in design['lines'] if l['name']==line)
        ordered=sorted((s for s in design['stations'] if s['line']==line),key=lambda s:s['s_m'])
        for i in range(fleet['trainset_count']):
            tid=f'{line}-train-{i+1:03d}';point=fleet['dispatch_points'][i%len(fleet['dispatch_points'])]
            actors[tid]=dict(line=line,station=point['station'],heading=point['heading'],ready=0,arrival=0,journey=None,moving=None,route=[],index=0)
        for point in fleet['dispatch_points']:
            route=ordered if point['heading']=='forward' else list(reversed(ordered))
            if layout.get('shape')=='ring':
                index=next(i for i,s in enumerate(route) if s['id']==point['station'])
                route=route[index:]+route[:index];route=route+[route[0]]
            elif route[0]['id']!=point['station']:
                raise ValueError('controlled radial dispatch must use its declared terminus')
            routes[(line,point['station'],point['heading'])]=[s['id'] for s in route]
        for phase in fleet['schedule']:
            start=clock_minutes(phase['from']);end=clock_minutes(phase['to'])
            if start<clock_minutes(fleet['service_start']):start+=1440
            if end<=start:end+=1440
            for day in range(math.ceil(minutes/1440)):
                for minute in range(start+day*1440,min(end+day*1440,minutes),phase['headway_min']):
                    for point in fleet['dispatch_points']:opportunities[minute].append((line,point['station'],point['heading']))
    if set(actors)!=set(trains):raise ValueError('controlled duty fleet identities differ from battery state')
    state=None;totals=defaultdict(float);missed=[];journeys=[];held=set();hold_minutes=0;completed=0;shortfall_events=0;reserve_minutes=0;minimum_soc=1
    sections=[];line_service={l['name']:dict(dispatch_opportunities=0,dispatched_journeys=0,
        completed_journeys=0,completed_train_km=0.,departed_train_km=0.) for l in design['lines']}

    def can_depart(tid,target):
        actor=actors[tid];edge=edges[(actor['line'],actor['heading'],actor['station'],target)];train=trains[tid]
        battery=state['trains'][tid] if state else dict(energy=train['initial_soc']*onboard['usable_kwh']*train['cars'],soh=1)
        cap=onboard['usable_kwh']*train['cars']*battery['soh']
        demand=edge['distance_m']/1000*train['energy_kwh_km']*train['mass_factor']
        auxiliary=(train.get('auxiliary_kw',0)*max(1,ambient_c/30)+onboard['cooling_kw']*train['cars'])*math.ceil(edge['travel_seconds']/60)/60
        power=discharge_limit_kw(onboard,battery['energy']/cap,ambient_c,battery['soh'])*train['cars']*edge['travel_seconds']/3600
        return battery['energy']-demand-auxiliary>=reserve_soc*cap and power+1e-9>=demand+auxiliary

    for minute in range(minutes):
        legs=[];visits=[]
        for tid,actor in actors.items():
            move=actor['moving']
            if move and minute>=move['arrival']:
                line_service[actor['line']]['completed_train_km']+=move['distance_m']/1000
                if retain_section_events:
                    sections.append(dict(journey=actor['journey'],train=tid,line=actor['line'],heading=actor['heading'],
                        from_station=actor['station'],to_station=move['target'],depart_minute=move['depart_minute'],
                        arrival_minute=minute,distance_m=move['distance_m']))
                actor.update(station=move['target'],arrival=minute,ready=minute+station_cfg[move['target']]['dwell_seconds']/60,moving=None,index=actor['index']+1)
                legs.append(dict(train=tid,minute=0,distance_km=0,travel_minutes=1,arrival_minute=0,regenerative_kwh=move['regeneration'],journey=actor['journey']))
                if actor['index']==len(actor['route'])-1:
                    line_service[actor['line']]['completed_journeys']+=1
                    completed+=1;journeys[actor['record']]['finish_minute']=minute
                    layout=next(l for l in design['lines'] if l['name']==actor['line'])
                    actor.update(journey=None,heading=actor['heading'] if layout.get('shape')=='ring' else 'reverse' if actor['heading']=='forward' else 'forward')
        for line,station,heading in opportunities.get(minute,[]):
            line_service[line]['dispatch_opportunities']+=1
            route=routes[(line,station,heading)]
            available=[tid for tid,a in actors.items() if a['line']==line and a['station']==station and a['heading']==heading and a['journey'] is None and a['moving'] is None and a['ready']<=minute]
            eligible=[tid for tid in available if can_depart(tid,route[1])]
            identity=f'{line}-{minute}-{station}-{heading}'
            if not eligible:
                missed.append(dict(id=identity,line=line,station=station,heading=heading,minute=minute,reason='energy-reserve-or-power' if available else 'stock-not-ready'))
                continue
            tid=min(eligible);actor=actors[tid]
            line_service[line]['dispatched_journeys']+=1
            actor.update(journey=identity,route=route,index=0,record=len(journeys))
            journeys.append(dict(id=identity,train=tid,line=line,heading=heading,start_station=station,start_minute=minute,finish_minute=None))
        for tid,actor in actors.items():
            if actor['journey'] and actor['moving'] is None and actor['ready']<=minute:
                target=actor['route'][actor['index']+1]
                if can_depart(tid,target):
                    edge=edges[(actor['line'],actor['heading'],actor['station'],target)]
                    demand=edge['distance_m']/1000*trains[tid]['energy_kwh_km']*trains[tid]['mass_factor']
                    legs.append(dict(train=tid,minute=0,distance_km=edge['distance_m']/1000,travel_minutes=edge['travel_seconds']/60,journey=actor['journey']))
                    line_service[actor['line']]['departed_train_km']+=edge['distance_m']/1000
                    actor['moving']=dict(target=target,arrival=minute+edge['travel_seconds']/60,regeneration=demand*regen_fraction,
                        depart_minute=minute,distance_m=edge['distance_m'])
                else:
                    held.add(actor['journey']);hold_minutes+=1
            battery=state['trains'][tid] if state else None
            capacity=onboard['usable_kwh']*trains[tid]['cars']*(battery['soh'] if battery else 1)
            needs_charge=(battery['energy'] if battery else trains[tid]['initial_soc']*capacity)<capacity-1e-9
            if actor['moving'] is None and actor['station'] in sites and needs_charge:
                visits.append(dict(train=tid,site=actor['station'],arrival_min=actor['arrival']-minute,departure_min=1,required_charge_kwh=0))
        visits.sort(key=lambda v:(v['arrival_min'],v['train']))
        step_trains={tid:{**train,'service_intervals':[(0,1)] if actors[tid]['journey'] else [],
            'service_journeys':[(0,1,actors[tid]['journey'])] if actors[tid]['journey'] else []} for tid,train in trains.items()}
        state=chronological_energy(onboard,stationary,step_trains,sites,visits,legs,1,initial_state=state,minute_offset=minute,
            ambient_c=ambient_c,seasonal_solar_factor=seasonal_solar_factor,cleaning_factor=cleaning_factor,
            reserve_soc=reserve_soc,setup_seconds=setup_seconds,outages=outages,retain_shortfalls=False)
        for key,value in state['totals'].items():totals[key]+=value
        shortfall_events+=state['shortfall_events'];reserve_minutes+=state['reserve_violation_train_minutes'];minimum_soc=min(minimum_soc,state['minimum_soc'])
    return dict(totals=dict(totals),minimum_soc=minimum_soc,dispatch_opportunities=sum(len(v) for v in opportunities.values()),
        service_by_line=line_service,completed_section_events=sections if retain_section_events else None,
        dispatched_journeys=len(journeys),completed_journeys=completed,missed_dispatches=missed,
        distinct_energy_held_journeys=len(held),energy_hold_train_minutes=hold_minutes,journeys=journeys,
        reserve_violation_train_minutes=reserve_minutes,shortfall_events=shortfall_events,
        final_train_locations={tid:dict(station=a['station'],moving=a['moving'] is not None,journey=a['journey']) for tid,a in actors.items()},
        final_energy_state={k:state[k] for k in ('trains','storage_kwh','storage_soh','storage_replacements')} if state else {},
        movement_basis=movement_profiles['basis'],service_disruption_feedback_modelled=True,
        study_assumptions=['minute resolution','charging access for held/idle stock at declared sites; berth/delivery qualification required',
            'leg energy intensity and average discharge-power screen; transient traction calibration open',
            'conflict-capable timetable and depot access approval remain open'],service_qualified=False,time_step_seconds=60)
