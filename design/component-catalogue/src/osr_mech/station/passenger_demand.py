"""Station/section peak loads from explicit OD legs and the declared service.

Partial cohort counts do not establish a complete station demand forecast. An
empty register yields unknown demand, never the common 3,000 pax/h preset.
"""
import math
from ..network_energy_duty import clock_minutes


def station_passenger_demand(design,scenario,register):
    city=design['city']['slug'];data=register.get('cities',{}).get(city,{})
    cohorts=data.get('assignments',[])
    if cohorts and (not data.get('survey_source') or not data.get('survey_date')):
        raise ValueError('passenger assignment requires a source and survey date')
    window_start=clock_minutes(data['peak_window_start']) if cohorts else None
    window_end=clock_minutes(data['peak_window_end']) if cohorts else None
    if cohorts and window_end<=window_start:window_end+=1440
    stations={s['id']:s for s in design['stations']}
    flows={sid:dict(recorded_boardings_hour=0,recorded_alightings_hour=0,boarding_by_heading={'forward':0,'reverse':0}) for sid in stations}
    sections={};seen=set();journeys=0;boardings=0
    transfers={frozenset((a,b)) for interchange in design.get('interchanges',[]) for a in interchange['platforms'] for b in interchange['platforms'] if a!=b}
    for cohort in cohorts:
        if cohort['id'] in seen:raise ValueError('duplicate passenger cohort')
        seen.add(cohort['id']);rate=cohort['passengers_hour'];legs=cohort['legs']
        if not math.isfinite(rate) or rate<0 or not legs:raise ValueError('invalid passenger rate or route')
        for previous,current in zip(legs,legs[1:]):
            if frozenset((previous['to_station'],current['from_station'])) not in transfers:
                raise ValueError('OD legs use an undeclared station transfer')
        for leg in legs:
            origin=stations[leg['from_station']];destination=stations[leg['to_station']];heading=leg['heading']
            if origin['line']!=destination['line'] or origin['id']==destination['id'] or heading not in ('forward','reverse'):
                raise ValueError('invalid station pair or heading')
            line=next(l for l in design['lines'] if l['name']==origin['line'])
            route=sorted((s for s in stations.values() if s['line']==line['name']),key=lambda s:s['s_m'])
            index=next(i for i,s in enumerate(route) if s['id']==origin['id']);target=next(i for i,s in enumerate(route) if s['id']==destination['id'])
            direction=1 if heading=='forward' else -1
            while index!=target:
                nxt=index+direction
                if not 0<=nxt<len(route):
                    if line.get('shape')!='ring':raise ValueError('OD direction cannot reach the radial destination')
                    nxt%=len(route)
                key=(line['name'],heading,route[index]['id'],route[nxt]['id'])
                sections[key]=sections.get(key,0)+rate;index=nxt
            flows[origin['id']]['recorded_boardings_hour']+=rate
            flows[origin['id']]['boarding_by_heading'][heading]+=rate
            flows[destination['id']]['recorded_alightings_hour']+=rate
            boardings+=rate
        journeys+=rate
    for sid,flow in flows.items():
        fleet=next(f for f in scenario['fleets'] if f['line']==stations[sid]['line'])
        windows=[]
        if cohorts:
            a_window=window_start;b_window=window_end
            if a_window<clock_minutes(fleet['service_start']):a_window+=1440;b_window+=1440
            for phase in fleet['schedule']:
                a=clock_minutes(phase['from']);b=clock_minutes(phase['to'])
                if a<clock_minutes(fleet['service_start']):a+=1440
                if b<=a:b+=1440
                if max(a,a_window)<min(b,b_window):windows.append(phase['headway_min'])
        headway=max(windows) if windows else None
        flow.update(service_peak_headway_minutes=headway,
            peak_waiting_accumulation_pax=flow['recorded_boardings_hour']*headway/60 if headway is not None else None,
            demand_coverage_complete=data.get('coverage_complete') is True,demand_accepted=False,
            one_lift_out_capacity_pax_hour=None,evacuation_and_rescue_accepted=False)
        if not cohorts:
            flow.update(recorded_boardings_hour=None,recorded_alightings_hour=None,boarding_by_heading=None)
    return dict(stations=flows,section_peak_loads=[dict(line=k[0],heading=k[1],from_station=k[2],to_station=k[3],recorded_passengers_hour=v) for k,v in sorted(sections.items())],
        recorded_paid_journeys_hour=journeys if cohorts else None,recorded_train_boardings_hour=boardings if cohorts else None,
        source=data.get('survey_source'),survey_date=data.get('survey_date'),forecast_accepted=False,
        basis='Explicit station OD legs; transfers count additional boardings, not additional paid journeys. Recorded cohorts may be incomplete. Peak headway accumulation is a screen, not circulation or evacuation acceptance.')
