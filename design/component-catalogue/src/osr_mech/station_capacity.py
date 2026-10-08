"""Shared-layout station area, circulation and lift-out capacity screens.

No default people density or equipment throughput is presented as a standard.
Surveyed demand and reviewed evacuation/rescue criteria remain separate inputs.
"""
import math
from collections import defaultdict,deque
from osr_mech.provenance import stable_sum as sum
from .station.circulation import continuous_path,continuous_clear_width


def passenger_pulses(boardings):
    """Queue intervals and train-load pulses from the selected OD reservations."""
    changes=defaultdict(lambda:defaultdict(int));departures=defaultdict(lambda:defaultdict(int));arrivals=defaultdict(lambda:defaultdict(int))
    for row in boardings:
        if row['minute']<row['arrival_minute']:raise ValueError('boarding precedes station arrival')
        count=row['passengers']
        if type(count) is not int or count<0:raise ValueError('integer passenger pulse required')
        changes[row['station']][row['arrival_minute']]+=count;changes[row['station']][row['minute']]-=count
        departures[row['station']][row['minute']]+=count
        arrivals[row['destination']][row['alight_minute']]+=count
    rows=[]
    for station in sorted(set(changes)|set(departures)|set(arrivals)):
        waiting=peak=0
        for _,delta in sorted(changes[station].items()):waiting+=delta;peak=max(peak,waiting)
        rows.append(dict(station=station,peak_reserved_waiting_passengers=peak,
            boarding_train_load_pulses=[dict(minute=m,passengers=n) for m,n in sorted(departures[station].items())],
            alighting_train_load_pulses=[dict(minute=m,passengers=n) for m,n in sorted(arrivals[station].items())],
            actual_passenger_forecast_accepted=False,unserved_and_unbooked_station_queues_unknown=True))
    return rows


def footprint_screen(platform,length_m,equipment):
    x0,x1=-length_m/2,length_m/2;y0=(platform['y_mm']-platform['width_mm']/2)/1000;y1=y0+platform['width_mm']/1000
    rectangles=[]
    for e in equipment:
        if platform['level'] not in e['served_levels']:continue
        a=(e['x_mm']-e['length_mm']/2)/1000;b=(e['x_mm']+e['length_mm']/2)/1000
        c=(e['y_mm']-e['width_mm']/2)/1000;d=(e['y_mm']+e['width_mm']/2)/1000
        if d<=y0 or c>=y1:continue  # Equipment on another platform at this level.
        if not x0<=a<b<=x1 or not y0<=c<d<=y1:
            raise ValueError('equipment footprint extends outside platform support envelope')
        if a<b and c<d:rectangles.append((a,b,c,d))
    cuts=sorted({x0,x1,*(a for a,b,c,d in rectangles),*(b for a,b,c,d in rectangles)})
    occupied=0;minimum_gap=y1-y0
    for a,b in zip(cuts,cuts[1:]):
        segments=sorted((c,d) for left,right,c,d in rectangles if left<(a+b)/2<right)
        merged=[]
        for c,d in segments:
            if merged and c<=merged[-1][1]:merged[-1][1]=max(d,merged[-1][1])
            else:merged.append([c,d])
        occupied+=(b-a)*sum(d-c for c,d in merged)
        edges=[y0,*[v for pair in merged for v in pair],y1]
        gaps=[edges[i+1]-edges[i] for i in range(0,len(edges)-1,2)]
        minimum_gap=min(minimum_gap,max(gaps,default=0))
    gross=length_m*(y1-y0)
    return dict(gross_platform_area_m2=gross,equipment_union_area_m2=occupied,unoccupied_envelope_area_m2=gross-occupied,
        narrowest_largest_contiguous_lane_m=minimum_gap,
        continuous_longitudinal_clear_width_m=continuous_clear_width((x0,x1,y0,y1),rectangles),
        basis='contained footprint union and connected longitudinal clearance; site obstacles, entrance routes and crowd dynamics remain separate')


def station_capacity_screen(station,length_m,criteria=None):
    criteria=criteria or {};layout=station['layout'];demand=station.get('passenger_demand',{})
    platforms=[]
    for platform in layout['platforms']:
        area=footprint_screen(platform,length_m,layout['equipment'])
        waiting=criteria.get('waiting_pax_by_platform',{}).get(platform['id'])
        if waiting is None and len(layout['platforms'])==1:waiting=demand.get('peak_waiting_accumulation_pax')
        rate=criteria.get('pedestrian_flow_pax_per_m_min')
        if rate is not None and (not math.isfinite(rate) or rate<=0):raise ValueError('positive sourced circulation rate required')
        density=waiting/area['unoccupied_envelope_area_m2'] if waiting is not None and area['unoccupied_envelope_area_m2']>0 else None
        platforms.append(dict(platform_id=platform['id'],**area,waiting_pax=waiting,waiting_density_pax_m2=density,
            circulation_capacity_pax_hour=area['continuous_longitudinal_clear_width_m']*rate*60 if rate is not None else None,
            crowding_criterion_pax_m2=criteria.get('crowding_criterion_pax_m2'),criteria_accepted=False))
    lift_ids=[e['id'] for e in layout['equipment'] if e['kind']=='lift']
    capacities=criteria.get('lift_capacity_pax_hour',{})
    if any(k not in lift_ids or not math.isfinite(v) or v<=0 for k,v in capacities.items()):
        raise ValueError('lift throughput must identify actual layout lifts with positive sourced rates')
    def capacity_to_level(target,unavailable):
        residual=defaultdict(dict);large=sum(capacities.values())+1
        def edge(a,b,amount):
            residual[a][b]=residual[a].get(b,0)+amount;residual[b].setdefault(a,0)
        for equipment in layout['equipment']:
            if equipment['kind']!='lift' or equipment['id']==unavailable:continue
            inside=equipment['id']+'-in';outside=equipment['id']+'-out'
            edge(inside,outside,capacities[equipment['id']])
            for level in equipment['served_levels']:edge(level,inside,large);edge(outside,level,large)
        flow=0.
        while True:
            parents={'street':None};queue=deque(['street'])
            while queue and target not in parents:
                current=queue.popleft()
                for node,capacity in residual[current].items():
                    if capacity>1e-9 and node not in parents:parents[node]=current;queue.append(node)
            if target not in parents:return flow
            node=target;amount=large
            while parents[node] is not None:amount=min(amount,residual[parents[node]][node]);node=parents[node]
            node=target
            while parents[node] is not None:
                before=parents[node];residual[before][node]-=amount;residual[node][before]+=amount;node=before
            flow+=amount
    outages=[dict(unavailable_lift=k,remaining_station_lift_capacity_pax_hour=sum(capacities[j] for j in lift_ids if j!=k)
        if all(j in capacities for j in lift_ids) else None,
        street_to_platform_capacity_pax_hour={p['id']:capacity_to_level(p['level'],k) if all(j in capacities for j in lift_ids) else None for p in layout['platforms']},
        shared_lift_resource_and_serial_levels_modelled=True,capacity_acceptance=False) for k in lift_ids]
    return dict(station=station['id'],platforms=platforms,one_lift_out_cases=outages,
        measured_criteria_source=criteria.get('source_record'),passenger_demand_complete=demand.get('demand_coverage_complete',False),
        evacuation_seconds=None,assisted_rescue_accepted=False,street_crossings_accepted=False,
        accessible_entrance_walkshed_population=None,station_structure_and_launcher_passage_accepted=False,
        engineering_qualified=False)
