"""One capacity-constrained OD, opening and operating-cost study contract.

Completed section events are supply; train dispatches are not paid journeys.
OD requests may be declared sensitivities or supplied forecasts, never inferred
as observed demand. Finance and engineering adoption require separate evidence.
"""
from collections import defaultdict
from datetime import date
from .provenance import stable_sum
from .industrialisation import nonnegative

OPENING_PACKAGES=('running_structures','stations','specials_and_transitions','track','energy','depots','fleet','testing','approvals')


def line_opening(line, packages):
    extra=set(packages)-set(OPENING_PACKAGES)
    if extra:raise ValueError('unknown line-opening package')
    missing=[];dates={};cash={};unaccepted=[]
    for key in OPENING_PACKAGES:
        row=packages.get(key,{})
        if row.get('completion_date') is None:missing.append(key)
        else:dates[key]=date.fromisoformat(row['completion_date'])
        if row.get('installed_cash_usd') is not None:cash[key]=nonnegative(row['installed_cash_usd'],key+' cash')
        if row.get('accepted') is not True or not row.get('acceptance_record'):unaccepted.append(key)
    latest=max(dates.values()) if dates else None
    return dict(line=line,full_line_opening_date=latest.isoformat() if latest and not missing else None,
        latest_known_package_date=latest.isoformat() if latest else None,
        known_bottleneck_packages=[k for k,v in dates.items() if v==latest],missing_dates=missing,
        missing_costs=[k for k in OPENING_PACKAGES if k not in cash],unaccepted_packages=unaccepted,
        known_scoped_cash_usd=stable_sum(cash.values()),
        complete_scope_cash_usd=stable_sum(cash.values()) if len(cash)==len(OPENING_PACKAGES) else None,
        opening_accepted=not missing and not unaccepted,revenue_opening_adopted=False)


def allocate_od(events, requests, capacities, transfer_pairs=()):
    """FIFO complete-itinerary reservations over actually completed train legs.

    Passengers may split across departures. Seats are reserved on every section;
    connections require explicit transfer walking time and a declared node pair.
    Incomplete itineraries generate no recognised fare in this conservative
    study. This is not a field queue, refund policy or accepted demand forecast.
    """
    events=sorted(events,key=lambda e:(e['depart_minute'],e['train'],e['from_station']))
    journeys=defaultdict(list);remaining={};seen=set();train_last={}
    for i,e in enumerate(events):
        key=(e['journey'],e['from_station'],e['to_station'])
        if key in seen:raise ValueError('duplicate service section event')
        seen.add(key)
        if e['arrival_minute']<=e['depart_minute']:raise ValueError('positive section travel time required')
        nonnegative(e['distance_m'],'section distance')
        capacity=capacities.get(e['train'])
        if type(capacity) is not int or capacity<=0:raise ValueError('positive configured train passenger capacity required')
        if train_last.get(e['train'],-1)>e['depart_minute']:raise ValueError('train section events overlap')
        train_last[e['train']]=e['arrival_minute']
        remaining[i]=capacity;journeys[e['journey']].append(i)
    cache={};allowed={frozenset(p) for p in transfer_pairs}
    def options(leg):
        key=tuple(leg[k] for k in ('line','heading','from_station','to_station'))
        if key not in cache:
            found=[]
            for ids in journeys.values():
                for pos,i in enumerate(ids):
                    start=events[i]
                    if (start['line'],start['heading'],start['from_station'])!=key[:3]:continue
                    route=[];current=key[2];arrival=-1
                    for j in ids[pos:]:
                        event=events[j]
                        if event['from_station']!=current or event['depart_minute']<arrival:break
                        route.append(j);current=event['to_station'];arrival=event['arrival_minute']
                        if current==key[3]:
                            found.append(route);break
            cache[key]=sorted(found,key=lambda ids:(events[ids[-1]]['arrival_minute'],events[ids[0]]['depart_minute']))
        return cache[key]
    rows=[];boarding_events=[];request_ids=set();counts=defaultdict(float)
    for request in sorted(requests,key=lambda r:(r['arrival_minute'],r['id'])):
        if request['id'] in request_ids:raise ValueError('duplicate OD request identity')
        request_ids.add(request['id']);legs=request['legs'];wanted=request['passengers']
        if type(wanted) is not int or wanted<0 or not legs or len(legs)>4:raise ValueError('bounded OD itinerary and integer passengers required')
        fare=nonnegative(request['fare_iqd'],'integrated fare');nonnegative(request['arrival_minute'],'passenger arrival')
        for before,after in zip(legs,legs[1:]):
            if frozenset((before['to_station'],after['from_station'])) not in allowed:
                raise ValueError('OD transfer does not use a declared interchange node pair')
            nonnegative(after['transfer_walk_minutes'],'transfer walk time')
        unserved=wanted;carried=0;wait=0.;km=0.
        while unserved:
            itineraries=[]
            def search(index,earliest,path):
                if index==len(legs):itineraries.append(path);return
                if itineraries:return
                leg=legs[index]
                if index:earliest+=leg['transfer_walk_minutes']
                for route in options(leg):
                    if events[route[0]]['depart_minute']<earliest or not all(remaining[j]>0 for j in route):continue
                    search(index+1,events[route[-1]]['arrival_minute'],path+[route])
                    if itineraries:return
            search(0,request['arrival_minute'],[])
            if not itineraries:break
            itinerary=itineraries[0];indices=[i for leg in itinerary for i in leg]
            if len(set(indices))!=len(indices):raise ValueError('OD itinerary reuses the same service section')
            quantity=min(unserved,*(remaining[i] for i in indices))
            for i in indices:remaining[i]-=quantity
            carried+=quantity;unserved-=quantity
            wait+=quantity*(events[indices[0]]['depart_minute']-request['arrival_minute'])
            km+=quantity*stable_sum(events[i]['distance_m']/1000 for i in indices)
            for route in itinerary:
                e=events[route[0]]
                boarding_events.append(dict(request=request['id'],journey=e['journey'],station=e['from_station'],
                    line=e['line'],heading=e['heading'],minute=e['depart_minute'],passengers=quantity))
        rows.append(dict(id=request['id'],requested_passengers=wanted,completed_paid_journeys=carried,
            unserved_passengers=unserved,train_boardings=carried*len(legs),passenger_km=km,
            total_first_boarding_wait_passenger_minutes=wait,recognised_fare_iqd=carried*fare))
        for k in ('requested_passengers','completed_paid_journeys','unserved_passengers','train_boardings','passenger_km','recognised_fare_iqd'):
            counts[k]+=rows[-1][k]
    return dict(cohorts=rows,totals=dict(counts) if requests else None,boarding_events=boarding_events,
        tariff='one fare per completed OD journey',actual_collected_receipts_iqd=None,
        demand_forecast_accepted=False,operating_acceptance=False,finance_baseline_replaced=False,
        model='complete-itinerary capacity reservations; no partial-trip fare or actual refund policy assumed')


def operating_cost(grid_kwh,train_km,electricity_usd_kwh,maintenance_usd_train_km,fixed_scope_usd):
    values=(grid_kwh,train_km,electricity_usd_kwh,maintenance_usd_train_km,fixed_scope_usd)
    for value,label in zip(values,('grid energy','train distance','electricity rate','maintenance rate','fixed OPEX')):nonnegative(value,label)
    return dict(electricity_usd=grid_kwh*electricity_usd_kwh,variable_maintenance_usd=train_km*maintenance_usd_train_km,
        fixed_scope_usd=fixed_scope_usd,total_modelled_opex_usd=fixed_scope_usd+grid_kwh*electricity_usd_kwh+train_km*maintenance_usd_train_km,
        purchased_grid_and_delivered_train_km_share_scenario=True,installed_investment_and_funding_adopted=False)
