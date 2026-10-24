"""Current Baghdad pilot: open-data access, finite service and financing sensitivity.

OSM walking estimates, synthetic OD, quoted equipment and actual site acceptance
are different evidence classes. No passenger or manufacturing release is granted.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import heapq
import io
import json
import math
import tomllib

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree

from . import configuration,corridor,delivery_schedule as delivery,geometry,model,shared_hub_layout,pilot_product,launch_optimisation

ROOT=model.ROOT
INPUT=Path(__file__).with_name('pilot-corridor.toml')
TEST=ROOT/'engineering/analysis/tests/test_ferrite_maglev_pilot_corridor.py'
CITY=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
SUMMARY=CITY/'engineering/maglev/summary.json'
MAPPING=CITY/'engineering/mapping'
POI=Path(__file__).with_name('data')/'pilot-destinations.json'
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/pilot-corridor'
SCHEMA='osr-baghdad-pilot/1'
FLAGS={**model.FLAGS,'engineering_accepted':False,'route_accepted':False,'city_default_changed':False,'financial_close':False}
FILES={'study.json.gz','access.svg','service.svg','README.md'}
MAX_RAW=32*1024*1024

def encoded(v):return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def source_paths():
    return sorted({Path(__file__),INPUT,TEST,SUMMARY,POI,Path(shared_hub_layout.__file__),*delivery.source_paths(),*pilot_product.source_paths(),*launch_optimisation.source_paths(),
        *(MAPPING/name for name in ('walking-graph.npz.gz','walking-streets.geojson.gz','street-source.json','worldpop-2026-pixels.npz.gz','worldpop-2026-source.json','ghsl-2025-pixels.npz.gz','ghsl-2025-source.json'))})
def sources():return {p.relative_to(ROOT).as_posix():digest(p) for p in source_paths()}
def load():
    a=tomllib.loads(INPUT.read_text())
    if a['schema']!='osr-baghdad-pilot-input/1' or a['line']!='line-14':raise ValueError('exact declared pilot required')
    for key,value in a.items():
        if type(value) in (int,float) and (not math.isfinite(value) or value<=0):raise ValueError('positive finite pilot inputs required')
    if a['simulation_hours']!=4 or a['spare_trains']!=2 or not 0<a['charge_efficiency']<=1:raise ValueError('bounded full-line service assumptions required')
    for key in ('debt_fraction','collection_fraction','nonfare_fraction_of_fares','charge_connected_fraction','normal_lift_fraction_of_passengers'):
        if not 0<a[key]<=1:raise ValueError('pilot fraction exceeds one')
    if not 1<=a['repayment_years']<=30 or not 0<=a['annual_interest']<=.2:raise ValueError('bounded finance assumptions required')
    for key in ('fares_usd','daily_paid_ramp','peak_demand_factors'):
        if not a[key] or any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in a[key]):raise ValueError('positive finite pilot sequence required')
    if any(v>1 for v in a['daily_paid_ramp']) or any(type(v) not in (int,float) or not math.isfinite(v) or v<=0 for v in a['steel_wheel_comparison'].values()):raise ValueError('bounded comparison/ramp inputs required')
    return a
def city_line():return next(r for r in json.loads(SUMMARY.read_bytes())['lines'] if r['line']==load()['line'])
def controlled_line():
    """Copy retained geographic/terminal plan; recompute mainline loss at new mass."""
    from copy import deepcopy
    line=deepcopy(city_line());cfg=pilot_product.configuration_profile();mass=cfg['controlled_aw3_kg'];line['pilot_configuration']=cfg
    profiles={}
    for event in line['duty']['arrival_events_per_circuit']:
        if not event['terminal_loop_allowance']:
            key=(event['distance_m'],event['moving_seconds'])
            if key not in profiles:
                p=corridor.profile(distance_m=key[0],runtime_s=key[1],cars=6,car_mass_kg=mass)
                if not p['study_pass']:raise ValueError('controlled-mass pilot trajectory fails')
                loss=launch_optimisation.selected_cost_energy(profile=p,configuration_id=cfg['id'])
                if loss is None or not loss['controlled_mass_matches']:raise ValueError('no controlled-mass launch design passes numerical limits')
                profiles[key]=(p,loss)
            p,loss=profiles[key];event['station_traction_input_kwh']=loss['dc_import_kwh'];event['launch_profile_sha256']=loss['profile_sha256']
        else:
            event['station_traction_input_kwh']*=mass/city_line()['formation']['aw3_mass_kg']*6
            event['energy_basis']='mass-scaled retained short-loop allowance; exact curved-loop electrical model remains open'
    line['launch_profile']=next(iter(profiles.values()))[0];line['launch_loss']=next(iter(profiles.values()))[1]
    line['formation']['aw3_mass_kg']=6*mass;line['formation']['gross_storage_kwh']=6*cfg['battery_kwh_per_car']
    return line
def npz(path):return np.load(io.BytesIO(gzip.decompress(path.read_bytes())),allow_pickle=False)
def xy(lat,lon):return np.column_stack((np.asarray(lon)*111320*math.cos(math.radians(33.3)),np.asarray(lat)*111320))

def walking_graph():
    """Retain OSM shared-node topology; filter tagged barriers/steps conservatively."""
    g=npz(MAPPING/'walking-graph.npz.gz');street=json.loads((MAPPING/'street-source.json').read_bytes())
    if digest(MAPPING/'walking-graph.npz.gz')!=street['graph_sha256'] or digest(MAPPING/'walking-streets.geojson.gz')!=street['geometry_sha256']:raise ValueError('retained OSM source checksums differ')
    geo=json.loads(gzip.decompress((MAPPING/'walking-streets.geojson.gz').read_bytes()));allowed=set();blocked=set();tagged=0
    def point(p):return (round(p[0],7),round(p[1],7))
    for feature in geo['features']:
        tags=feature['properties'];highway=tags.get('highway');deny=highway in {'steps','motorway','motorway_link','construction','proposed','raceway','no'} or tags.get('foot') in {'no','private'} or tags.get('access') in {'no','private'}
        if highway in {'trunk','trunk_link'} and tags.get('foot') not in {'yes','designated','permissive'}:deny=True
        tagged+=int(deny);target=blocked if deny else allowed
        points=feature['geometry']['coordinates']
        for p,q in zip(points,points[1:]):target.add(tuple(sorted((point(p),point(q)))))
    coords=[(round(lon,7),round(lat,7)) for lat,lon in zip(g['lat'],g['lon'])]
    mask=np.array([tuple(sorted((coords[i],coords[j]))) in allowed and tuple(sorted((coords[i],coords[j]))) not in blocked for i,j in zip(g['first'],g['second'])])
    first=g['first'][mask];second=g['second'][mask];length=g['length_m'][mask]
    matrix=coo_matrix((np.r_[length,length],(np.r_[first,second],np.r_[second,first])),shape=(len(coords),len(coords))).tocsr()
    # Duplicate source edges must not double a walk length in sparse summation.
    if len(first)!=len({tuple(sorted((int(i),int(j)))) for i,j in zip(first,second)}) or matrix.nnz!=2*len(first):raise ValueError('duplicate retained walking edges require explicit reconciliation')
    active=np.unique(np.r_[first,second]);tree=cKDTree(xy(g['lat'][active],g['lon'][active]))
    return g,matrix,active,tree,dict(nodes=len(coords),retained_undirected_edges=len(first),excluded_tagged_ways=tagged,
        snapshot=street['snapshot'],attribution=street['attribution'],license=street['license'],shared_node_ids_preserved=True,
        unknown_surface_width_kerb_grade_and_crossing_rights=True,verified_accessible_edges=0,
        scope='Step-excluded walking estimate; ordinary roads without sidewalks can remain. No wheelchair-passability or safe-crossing certificate.')

def access():
    a=load();line=city_line();stops=line['operating_plan']['stations'];g,matrix,active,tree,meta=walking_graph()
    station_snap,station_idx=tree.query(xy([s['lat'] for s in stops],[s['lon'] for s in stops]));nodes=active[station_idx]
    distances=dijkstra(matrix,directed=False,indices=nodes)
    for j,snap in enumerate(station_snap):
        if snap>a['node_snap_limit_m']:distances[j,:]=np.inf
        else:distances[j,:]+=snap
    lift=(a['platform_height_m']/a['lift_speed_m_s']+a['lift_doors_s']+a['normal_lift_wait_s'])
    results=[];assignment=None
    for dataset in ('worldpop-2026','ghsl-2025'):
        pixels=npz(MAPPING/(dataset+'-pixels.npz.gz'));valid=pixels['valid']&np.isfinite(pixels['counts'])&(pixels['counts']>=0)
        pop=pixels['counts'][valid].astype(float);lat=pixels['lat'][valid];lon=pixels['lon'][valid]
        snap,idx=tree.query(xy(lat,lon));paths=distances[:,active[idx]]+snap
        paths[:,snap>a['node_snap_limit_m']]=np.inf
        minutes=(paths/a['walk_speed_m_s']+lift)/60;wheeling=(paths/a['wheel_speed_m_s']+lift)/60
        best=np.argmin(minutes,axis=0);minimum=np.min(minutes,axis=0);reachable=minimum<=a['access_budget_minutes'];station_pop=[float(pop[reachable&(best==j)].sum()) for j in range(len(stops))]
        one_lift=(np.min(wheeling,axis=0)+(a['outage_lift_wait_s']-a['normal_lift_wait_s'])/60)<=a['access_budget_minutes']
        closed=wheeling.copy();closed[1,:]=np.inf
        results.append(dict(dataset=dataset,modelled_bbox_population=float(pop.sum()),valid_pixels=int(valid.sum()),missing_pixels=int((~valid).sum()),
            walking_catchment_population=float(pop[reachable].sum()),station_exclusive_population=station_pop,
            wheeling_sensitivity_population=float(pop[np.min(wheeling,axis=0)<=a['access_budget_minutes']].sum()),
            single_lift_outage_wheeling_population=float(pop[one_lift].sum()),
            both_lifts_station2_out_population=float(pop[np.min(closed,axis=0)<=a['access_budget_minutes']].sum()),
            verified_accessible_population=None,employment_count=None,each_pixel_counted_once=True))
        if dataset=='worldpop-2026':assignment=dict(pop=station_pop)
    pois=json.loads(POI.read_bytes());destinations=[];counts=[0]*len(stops)
    for poi in pois['elements']:
        coord=poi.get('center',poi)
        if 'lat' not in coord or 'lon' not in coord:continue
        snap,index=tree.query(xy([coord['lat']],[coord['lon']])[0]);cost=distances[:,active[index]]+float(snap)
        if snap>a['node_snap_limit_m']:cost[:]=np.inf
        j=int(np.argmin(cost));walk=(float(cost[j])/a['walk_speed_m_s']+lift)/60;within=math.isfinite(walk) and walk<=a['access_budget_minutes']
        if within:counts[j]+=1
        destinations.append(dict(osm_type=poi['type'],osm_id=poi['id'],name=poi['tags'].get('name'),amenity=poi['tags'].get('amenity'),lat=coord['lat'],lon=coord['lon'],
            nearest_station=stops[j]['id'] if math.isfinite(walk) else None,walking_minutes=walk if math.isfinite(walk) else None,within_budget=bool(within),entrance_or_occupancy_verified=False))
    return dict(graph=meta,station_snaps=[dict(id=s['id'],lat=s['lat'],lon=s['lon'],snap_m=float(snap),osm_node_id=int(g['node_ids'][node]),connector_approved=False) for s,snap,node in zip(stops,station_snap,nodes)],
        population=results,poi_snapshot=pois['osm3s']['timestamp_osm_base'],destinations=destinations,destination_counts=counts,
        walking_budget_minutes=a['access_budget_minutes'],sources_checked='2026-10-23',measured_od=None,measured_employment=None,
        entrance_kerb_width_surface_crossing_and_security_survey_required=True,
        limits=['station and residential pixel snap links up to150m are unsurveyed connectors; not permissions to cross walls/water','residential population is not jobs, mode share, paid trips or a ridership forecast','amenity centres may be inside campuses; gates and opening hours unverified','common-power failure disables paired lifts; stair-only journeys are not an accessible substitute'])

def od_model(access_value,a=None):
    a=load() if a is None else a;pop=access_value['population'][0]['station_exclusive_population'];weights=[1+math.sqrt(v) for v in access_value['destination_counts']];rows=[]
    for i,people in enumerate(pop):
        denominator=sum(weight for j,weight in enumerate(weights) if j!=i)
        for j,weight in enumerate(weights):
            if i!=j:rows.append(dict(origin=i,destination=j,daily_trips=people*a['daily_trips_per_catchment_resident']*weight/denominator))
    return dict(rows=rows,daily_potential_trips=sum(r['daily_trips'] for r in rows),measured=False,
        method='Explicit synthetic production=exclusive residential catchment×0.12 rail trips/person/day; destination weight1+sqrt(mapped amenities), no measured OD/employment claim')

def lift_queues(od,a=None):
    """Finite fluid queues: trips and staffing are assumptions, not measured use."""
    a=load() if a is None else a;cycle=2*a['platform_height_m']/a['lift_speed_m_s']+2*a['lift_doors_s'];rows=[]
    for station in range(4):
        trips=sum(r['daily_trips'] for r in od['rows'] if station in (r['origin'],r['destination']))
        for fraction in (a['normal_lift_fraction_of_passengers'],1.):
            for lifts in (2,1,0):
                capacity=lifts*a['lift_passengers_per_car']*3600/cycle;queue=0.;hours=[]
                for hour,factor in enumerate(a['peak_demand_factors']):
                    arrivals=trips*a['peak_hour_share_of_daily']*factor*fraction;before=queue;served=min(before+arrivals,capacity);queue=before+arrivals-served
                    hours.append(dict(hour=hour,demand=arrivals,served=served,queue_before=before,queue_after=queue,backlog_wait_s=queue/capacity*3600 if capacity else None))
                rows.append(dict(station=station,lift_fraction=fraction,operating_lifts=lifts,capacity_passengers_h=capacity,hours=hours,closing_unserved_queue=queue,
                    strict_accessible_route_available=False,assumed_capacity_not_approved=True))
    return dict(cycle_s=cycle,passengers_per_lift=a['lift_passengers_per_car'],cases=rows,
        method='Explicit fluid/hour queue, shared capacity for ascent/descent; door dwell+round-trip travel counted. No stairs substituted when both lifts fail. Nominal20%lift-use and all-passenger lift-use sensitivities; no measured arrival distribution, priority, wheelchair-space or evacuation certification. Fixed waits in catchments are a separate assumption, not validated by this queue model.')

def network_transfers():
    """Fixed-line journey graph on exact retained shared/coincident stop anchors."""
    lines=json.loads(SUMMARY.read_bytes())['lines'];nodes={};edges={};headways={};transfers=[]
    def link(first,last,seconds,change=False):edges.setdefault(first,[]).append((last,seconds,change))
    for line in lines:
        stops=line['operating_plan']['stations'];headways[line['line']]=line['selected_peak_headway_seconds']
        for stop in stops:nodes[stop['id']]=stop;edges[stop['id']]=[]
        for first,last,event in zip(stops,stops[1:],[e for e in line['duty']['arrival_events_per_circuit'] if not e['terminal_loop_allowance']]):
            seconds=event['moving_seconds']+60.;link(first['id'],last['id'],seconds);link(last['id'],first['id'],seconds)
    values=list(nodes.values())
    for i,first in enumerate(values):
        for last in values[i+1:]:
            if first['line']==last['line']:continue
            shared=set(first['mandatory_junction_ids'])&set(last['mandatory_junction_ids']);distance=math.dist(xy([first['lat']],[first['lon']])[0],xy([last['lat']],[last['lon']])[0])
            if not shared and distance>5.:continue
            # Count the assumed floor/core connector and vertical component;
            # coincident centre coordinates never mean zero passenger transfer.
            walk=distance+60.;vertical=8.;core_s=walk/.6+vertical+15+30
            link(first['id'],last['id'],core_s+headways[last['line']]/2,True);link(last['id'],first['id'],core_s+headways[first['line']]/2,True)
            transfers.append(dict(first=first['id'],last=last['id'],mapped_centre_distance_m=distance,assumed_floor_walk_m=walk,assumed_vertical_m=vertical,accepted=False))
    rows=[]
    for origin in city_line()['operating_plan']['stations']:
        costs={origin['id']:(headways[origin['line']]/2,0)};todo=[(*costs[origin['id']],origin['id'])]
        while todo:
            cost,changes,node=heapq.heappop(todo)
            if (cost,changes)!=costs[node]:continue
            for target,seconds,change in edges[node]:
                new=(cost+seconds,changes+int(change))
                if new<costs.get(target,(math.inf,999)):costs[target]=new;heapq.heappush(todo,(*new,target))
        counts={str(k):sum(changes==k for _,changes in costs.values()) for k in range(4)}
        examples=[dict(destination=node,total_generalised_minutes=seconds/60,transfers=changes) for node,(seconds,changes) in costs.items() if changes>=2]
        rows.append(dict(origin=origin['id'],reachable_stops=len(costs),minimum_transfer_counts=counts,two_or_more_transfer_examples=sorted(examples,key=lambda x:x['total_generalised_minutes'])[:5]))
    return dict(transfer_links=transfers,journeys=rows,initial_and_transfer_wait='half current protected headway under random arrival hypothesis; no coordination credit',
        graph_scope='Open radial legs and declared shared/coincident current stops; ring closure edges omitted conservatively.60m common-core+8m level change are unapproved access assumptions, not fitted hubs.',
        source_geometry_replaced=False,actual_transfer_demand=None)

def verify_berth_replay(actions,horizon):
    """Independent event replay: occupied receivers cannot be promised clear."""
    occupied={};reserved={};legs={};last=-1.
    for row in actions:
        time=row['time_s'];train=row['train'];action=row['action'];berth=row['berth']
        if time<last or not 0<=time<horizon:raise ValueError('berth event time outside finite replay')
        last=time
        if action=='stage-entry':
            if berth in occupied or berth in reserved:raise ValueError('depot staging enters occupied berth')
            occupied[berth]=train
        elif action=='dispatch':
            target=row['receiving_berth'];leg=row['leg']
            if occupied.get(berth)!=train:raise ValueError('dispatch does not own source berth')
            if target in occupied or target in reserved or leg in legs:raise ValueError('occupied receiving berth/leg before dispatch')
            del occupied[berth];reserved[target]=train;legs[leg]=train
        elif action=='arrival':
            leg=row['leg']
            if berth in occupied or reserved.get(berth)!=train or legs.get(leg)!=train:raise ValueError('arrival loses reserved receiver/leg')
            del reserved[berth];del legs[leg];occupied[berth]=train
        elif action=='withdrawal':
            if occupied.get(berth)!=train:raise ValueError('withdrawal does not own safe berth')
            del occupied[berth]
        else:raise ValueError('unknown berth replay action')
    return dict(verified=True,events=len(actions),closing_occupied=len(occupied),closing_reserved=len(reserved),source_release='Actual dispatch only; dwell completion never releases an occupied source berth')

def service(scenario='nominal',*,line=None,a=None):
    """Finite whole-line event replay; conservative pre-reserved receiving berths."""
    a=load() if a is None else a;line=controlled_line() if line is None else line
    if scenario not in {'nominal','variable-dwell','withdrawal','receiver-failure','charger-failure','combined-recovery'}:raise ValueError('declared service scenario required')
    headway=line['selected_peak_headway_seconds'];events=line['duty']['arrival_events_per_circuit'];n=len(line['operating_plan']['stations']);horizon=a['simulation_hours']*3600
    fleet=math.ceil(line['duty']['conservative_cycle_seconds']/headway);ready=[];protected_after={};occupied={};reserved={};legs={};trains={};log=[];withdrawals=[];actions=[];blocked=[];blocked_sample=set();blocked_count=0
    capacity=line['formation']['gross_storage_kwh']*.8;minimum=capacity*.2;maximum=capacity*.8
    for train in range(fleet):trains[train]=dict(energy=maximum,ready_time=train*headway,retired=False,staged=True,moving=False,next_index=0);heapq.heappush(ready,(train*headway,1,train,0))
    duration_by_main={i:float(e['moving_seconds']) for i,e in enumerate(events)}
    recovery_inserted=False
    while ready:
        time,kind,train,index=heapq.heappop(ready)
        if time>=horizon:break
        state=trains[train]
        if state['retired']:continue
        source=f'berth-{(index-1)%len(events):02d}';target=f'berth-{index:02d}';key=f'leg-{index:02d}';event=events[index]
        if kind==0:
            if reserved.get(target)!=train or target in occupied or legs.get(key)!=train:raise ValueError('actual arrival conflicts with receiver')
            del reserved[target];del legs[key];occupied[target]=train;state['moving']=False
            actions.append(dict(action='arrival',time_s=time,train=train,berth=target,leg=key))
            next_index=(index+1)%len(events);state['next_index']=next_index;heapq.heappush(ready,(state['ready_time'],1,train,next_index));continue
        proposed=state['ready_time'];idle=max(0.,time-proposed)
        source_failed_s=max(0.,min(time,5400.)-max(proposed,1800.)) if scenario in {'charger-failure','combined-recovery'} and index==2 else 0.
        idle_services=a['services_kw_per_car']*6*idle/3600;idle_battery=a['services_kw_per_car']*6*source_failed_s/3600;idle_grid=(idle_services-idle_battery)/a['charge_efficiency']
        if scenario in {'withdrawal','combined-recovery'} and train==2 and time>=3600:
            state['retired']=True
            if not state['staged']:
                if occupied.get(source)!=train:raise ValueError('withdrawal cannot remove another train')
                del occupied[source];actions.append(dict(action='withdrawal',time_s=time,train=train,berth=source))
            withdrawals.append(dict(train=train,time_s=time,at_safe_berth=True,initial_depot_staging=state['staged'],idle_services_kwh=idle_services,idle_grid_input_kwh=idle_grid,physical_depot_interface_qualified=False))
            if not recovery_inserted:
                replacement=fleet;trains[replacement]=dict(energy=maximum,ready_time=time+300,retired=False,staged=True,moving=False,next_index=0);heapq.heappush(ready,(time+300,1,replacement,0));recovery_inserted=True
            continue
        receiver_fault=scenario in {'receiver-failure','combined-recovery'} and index==1 and time<2820 and time+event['moving_seconds']>=1800
        source_clear=not state['staged'] or (source not in occupied and source not in reserved)
        receiver_clear=target not in occupied and target not in reserved;leg_clear=key not in legs and time>=protected_after.get(key,0.)
        if not source_clear or not receiver_clear or not leg_clear or receiver_fault:
            blocked_count+=1
            sample=(source,target,occupied.get(target),reserved.get(target),occupied.get(source)==train)
            if not receiver_clear and sample not in blocked_sample and len(blocked)<64:blocked.append(dict(time_s=time,train=train,source_berth=source,receiving_berth=target,occupant=occupied.get(target),reservation=reserved.get(target),source_still_occupied=occupied.get(source)==train));blocked_sample.add(sample)
            heapq.heappush(ready,(max(time+1,protected_after.get(key,0.),2820. if receiver_fault else 0.),1,train,index));continue
        start=time
        if state['staged']:occupied[source]=train;actions.append(dict(action='stage-entry',time_s=start,train=train,berth=source));state['staged']=False
        if occupied.get(source)!=train:raise ValueError('ready train lost its occupied source berth')
        state['energy']=max(0.,state['energy']-idle_battery)
        runtime=duration_by_main[index];dwell=60.+(30. if scenario in {'variable-dwell','combined-recovery'} and (train+index)%3==0 else 0.)
        need=a['services_kw_per_car']*6*(runtime+dwell)/3600
        if state['energy']<minimum+need:
            withdrawals.append(dict(train=train,time_s=start,at_safe_berth=True,idle_services_kwh=idle_services,idle_grid_input_kwh=idle_grid,reason='normal battery window prevents launch; emergency reserve not approved',physical_depot_interface_qualified=False));state['retired']=True;del occupied[source];actions.append(dict(action='withdrawal',time_s=start,train=train,berth=source));continue
        arrival=start+runtime;end=arrival+dwell;before=state['energy'];state['energy']-=need
        failed_charger=scenario in {'charger-failure','combined-recovery'} and index==1 and 1800<=arrival<5400
        charge=0. if failed_charger else min(maximum-state['energy'],a['charge_kw_per_car']*6*a['charge_efficiency']*dwell*a['charge_connected_fraction']/3600)
        state['energy']+=charge;protected_after[key]=start+headway;del occupied[source];reserved[target]=train;legs[key]=train
        actions.append(dict(action='dispatch',time_s=start,train=train,berth=source,receiving_berth=target,leg=key))
        main=not event['terminal_loop_allowance'];direction='forward' if index<n-1 else 'reverse'
        segment=index if index<n-1 else (2*(n-1)+2-index if main else None)
        log.append(dict(train=train,event=index,resource=key,destination=event['destination_station'],source_berth=source,receiving_berth=target,start_s=start,arrival_s=arrival,release_s=end,
            scheduled_ready_s=proposed,delay_s=start-proposed,receiving_berth_clear_before_launch=receiver_clear,receiver_fault_wait=scenario in {'receiver-failure','combined-recovery'} and index==1 and proposed<2820 and arrival>=1800,
            mainline=main,direction=direction if main else 'terminal',segment=segment if main else None,
            runtime_s=runtime,dwell_s=dwell,services_kwh=need,idle_services_kwh=a['services_kw_per_car']*6*idle/3600,
            fixed_traction_kwh=event['station_traction_input_kwh'],charge_delivered_kwh=charge,charger_input_kwh=charge/a['charge_efficiency'],
            idle_grid_input_kwh=idle_grid,source_charger_failed=source_failed_s>0,
            charger_failed=failed_charger,battery_before_kwh=before,battery_after_kwh=state['energy'],normal_minimum_kwh=minimum))
        state['ready_time']=end;state['moving']=True;heapq.heappush(ready,(arrival,0,train,index))
    for key in {r['resource'] for r in log}:
        ordered=sorted((r for r in log if r['resource']==key),key=lambda r:r['start_s'])
        if any(x['arrival_s']>y['start_s']+1e-9 for x,y in zip(ordered,ordered[1:])):raise ValueError('exclusive leg overlap in pilot replay')
    berth_verification=verify_berth_replay(actions,horizon)
    closing_holds=[]
    for train,state in trains.items():
        if state['retired'] or state['moving'] or state['ready_time']>=horizon:continue
        idle=horizon-state['ready_time'];failed=max(0.,min(horizon,5400.)-max(state['ready_time'],1800.)) if scenario in {'charger-failure','combined-recovery'} and state['next_index']==2 else 0.
        services=a['services_kw_per_car']*6*idle/3600;battery=a['services_kw_per_car']*6*failed/3600
        closing_holds.append(dict(train=train,source_berth=None if state['staged'] else f'berth-{(state["next_index"]-1)%len(events):02d}',idle_services_kwh=services,idle_grid_input_kwh=(services-battery)/a['charge_efficiency'],idle_battery_kwh=battery))
    departures={}
    for row in log:
        if row['mainline']:departures.setdefault((row['direction'],row['segment']),[]).append(row['start_s'])
    worst=max((max(np.diff(sorted(times))) for times in departures.values() if len(times)>1),default=0.)
    waits=[]
    for key,times in sorted(departures.items()):
        ordered=sorted(times);gaps=np.diff(ordered);wait=float(np.sum(gaps*gaps)/(2*np.sum(gaps))) if len(gaps) else None
        waits.append(dict(direction=key[0],segment=key[1],random_arrival_wait_between_first_last_s=wait,opening_wait_until_first_s=ordered[0],unserved_after_last_departure_s=max(0.,horizon-ordered[-1])))
    dispatches=sum(r['mainline'] and r['event'] in (0,n+2) for r in log)
    return dict(scenario=scenario,source_policy_headway_s=headway,progressive_180s_adopted=False,fleet_active=fleet,fleet_total=fleet+a['spare_trains'],
        horizon_s=horizon,events=log,withdrawals=withdrawals,mainline_segment_departures=[dict(direction=k[0],segment=k[1],times_s=sorted(v)) for k,v in sorted(departures.items())],
        berth_events=actions,berth_verification=berth_verification,blocked_receiver_examples=blocked,blocked_attempts=blocked_count,closing_holds=closing_holds,
        maximum_observed_headway_s=float(worst),directional_origin_departures=dispatches,
        passenger_wait_sensitivities=waits,
        train_km=sum(events[r['event']]['distance_m']/1000 for r in log),
        services_kwh=sum(r['services_kwh']+r['idle_services_kwh'] for r in log)+sum(r['idle_services_kwh'] for r in withdrawals+closing_holds),
        charger_input_kwh=sum(r['charger_input_kwh']+r['idle_grid_input_kwh'] for r in log)+sum(r['idle_grid_input_kwh'] for r in withdrawals+closing_holds),fixed_traction_kwh=sum(r['fixed_traction_kwh'] for r in log),
        event_energy_balance_kwh=sum(r['battery_before_kwh']-r['services_kwh']+r['charge_delivered_kwh']-r['battery_after_kwh'] for r in log),
        executable_offline_replay=True,actual_rust_whole_line_protocol=False,physical_qualified=False,
        pending_arrivals_at_horizon=sum(r['arrival_s']>=horizon for r in log),energy_accounting='Full movement/dwell/charge attributed to every departure strictly before horizon, including closing in-transit trips; no post-horizon starts. Initial/closing depot, terminal insertion and night positioning are unqualified. Berth actions are replayed only within horizon.',
        boundaries='Resource/energy planning DES; current exclusive leg+actually vacant reserved receiving berth before launch. Source berth remains occupied until actual dispatch, separately keyed by direction/terminal position. Initial trains wait in unqualified depot staging; no progressive credit. Failed receivers hold, withdrawals occur at safe berths; terminal loops and depot insertion remain physically unqualified.')

def passenger_assignment(od,run,*,scale=1.,a=None):
    a=load() if a is None else a;results=[];unserved=served=0.;hours=round(a['simulation_hours']);capacity=city_line()['formation']['aw2_passengers']
    for hour in range(hours):
        availability={};demand={};used={}
        for r in run['mainline_segment_departures']:
            key=(r['direction'],r['segment']);availability[key]=capacity*sum(hour*3600<=t<(hour+1)*3600 for t in r['times_s']);demand[key]=0.;used[key]=0.
        for r in od['rows']:
            i,j=r['origin'],r['destination'];direction='forward' if j>i else 'reverse';segments=range(min(i,j),max(i,j));keys=[(direction,s) for s in segments]
            requested=r['daily_trips']*a['peak_hour_share_of_daily']*a['peak_demand_factors'][hour]*scale
            carried=min([requested]+[max(0.,availability.get(k,0.)-used.get(k,0.)) for k in keys]);served+=carried;unserved+=requested-carried
            for key in keys:demand[key]=demand.get(key,0.)+requested;used[key]=used.get(key,0.)+carried
        for key in sorted(demand):results.append(dict(hour=hour,direction=key[0],segment=key[1],demand=demand[key],carried=used[key],capacity=availability.get(key,0.),unserved_segment_entries=demand[key]-used[key]))
    return dict(scale=scale,segments=results,served_trips=served,unserved_trips=unserved,allocation='deterministic origin/destination order; no passenger priority or measured distribution',daily_served_fraction=served/(served+unserved) if served+unserved else 0.)

def compact_station():
    f=configuration.selected().formation;L=f.assumed_overall_length_m;zone=(-150.,200.);width=18.;obstacles=[([x-2.25,-2.05],[x+2.25,2.05]) for x in (-8.,8.)]+[([19.,-3.3],[34.,3.3])]
    def case(aligned):
        doors={};fronts={};zones=[]
        for direction in (1,-1):
            front=direction*L/2 if aligned else 0.;fronts[str(direction)]=front;doors[direction]=[]
            zones.append(sorted(front+direction*z for z in zone))
            for car in range(f.cars):
                for offset in f.doors_per_side_x_m:
                    along=front+direction*(-f.body_length_m/2-car*(f.body_length_m+f.coupling_gap_assumption_m)+offset)
                    doors[direction].append([along,direction*(width/2-.75)])
        length=L+10 if aligned else 2*L+10;inside=lambda p:abs(p[0])<=length/2-.75 and abs(p[1])<=width/2-.75
        walks=[]
        for p in doors[1]:
            for q in doors[-1]:
                path=shared_hub_layout.visibility_path(p,q,obstacles,inside)
                if path is None:raise ValueError('compact station floor route blocked')
                walks.append(dict(first=p,last=q,length_m=path['length_m']+1.5))
        union=[min(z[0] for z in zones),max(z[1] for z in zones)]
        return dict(direction_specific_front_stops_m=fronts,power_zones_m=zones,common_straight_m=union[1]-union[0],platform_length_m=length,platform_area_m2=width*length,
            opposite_direction_door_pairs=len(walks),minimum_walk_m=min(p['length_m'] for p in walks),maximum_walk_m=max(p['length_m'] for p in walks),walks=walks)
    return dict(old_shared_front=case(False),aligned_body_centres=case(True),station_island_width_m=width,lifts=2,stairs=1,
        approach_flare_and_multiline_common_core_fitted=False,selected=False,
        tradeoff='Aligned bodies shorten platform104.5m but opposite350m power zones require504.5m common straight; old400m fit cannot be reused. Same-level opposite-direction transfer has no lift; cross-line transfer needs separately fitted levels/core.')

def comparison_bom(line,fleet,a,*,topology=None):
    """Independent elevated steel-wheel quantities; never primary configuration."""
    k=a['steel_wheel_comparison'];length=line['operational_route_length_m'];span=25.;bays=math.ceil(length/span);rows=[];rates=delivery.load()['rates']
    def add(uid,q,rate,unit):rows.append(dict(id=uid,quantity=q,unit=unit,unit_rate_usd=rate,cost_usd=q*rate,quote=False))
    concrete=length*(k['deck_width_m']*k['deck_slab_m']+k['girders_per_span']*k['girder_area_m2'])
    add('independent-deck-slab-and-four-girders',concrete,rates['concrete_usd_m3'],'m3');add('deck-reinforcement',concrete*180,rates['steel_usd_kg'],'kg')
    add('rails',length*k['rails_per_route']*k['rails_kg_per_m'],k['rail_usd_kg'],'kg');add('direct-fixings',length*k['direct_fastener_pairs_per_route_m'],k['fastener_pair_usd'],'pair')
    add('third-rail',length*2*k['third_rail_kg_per_track_m'],k['third_rail_usd_kg'],'kg');add('traction-substations',math.ceil(length/1000*k['traction_substation_per_route_km']),k['substation_each_usd'],'substation')
    lifts=bays*k['girders_per_span'] if topology is None else sum(c['spans']*k['girders_per_span']*c['directions']/2 for c in topology['components'])
    add('girder-lifts',lifts,rates['beam_erection_each_usd'],'lift')
    for uid,q,key in [('body',6,'train_body_each_usd'),('bogies',k['bogies_per_train'],'bogie_each_usd'),('wheelsets',k['wheelsets_per_train'],'wheelset_each_usd'),('motors',k['motors_per_train'],'motor_each_usd'),('inverters',k['inverters_per_train'],'inverter_each_usd')]:add(uid,q*fleet,k[key],'each')
    return dict(architecture='steel-wheel-elevated-comparison-only',rows=rows,priced_different_scope_usd=sum(r['cost_usd'] for r in rows),equal_service=dict(stops=4,passengers_per_train=720,fleet=fleet,source_headway_s=line['selected_peak_headway_seconds']),
        comparator_car_mass_kg=k['gross_car_mass_kg'],primary_architecture_changed=False,
        limits=['independent preliminary slab/girder/track/train BOM; no accepted structural gauge/curve or supplier price','common station/site/depot/assurance scope is shared explicitly; foundation and column allowances are a shared-scope hypothesis only: heavier rail deck reactions require independent foundations, columns and ground design before comparison acceptance','rail energy is a separate analytical sensitivity; rolling contact, motors, braking and rail maintenance are unqualified'])

def comparison_common_rows(common):
    excluded=[r for r in common if r['id']=='terminal-service-cabinets'];included=[r for r in common if r['id']!='terminal-service-cabinets']
    return dict(included=included,excluded_maglev_only=excluded,included_cost_usd=sum(r['cost_usd'] for r in included),excluded_cost_usd=sum(r['cost_usd'] for r in excluded),
        scope='Maglev-only non-passenger terminal charging cabinets excluded. Passenger station/site/depot allowances remain an explicit shared-scope hypothesis, not equivalent electrical/structural acceptance.')

def finance(capex,annual_opex,daily_paid_trips,monthly_capex,*,a=None):
    a=load() if a is None else a;debt=capex*a['debt_fraction'];monthly=[];balance=0.;construction_interest=0.
    for r in monthly_capex:
        spend=r['capex_usd'];draw=spend*a['debt_fraction'];interest=(balance+draw/2)*a['annual_interest']/12;balance+=draw;construction_interest+=interest
        monthly.append(dict(month=r['month'],capex_usd=spend,debt_draw_usd=draw,equity_capex_usd=spend-draw,interest_paid_usd=interest,closing_debt_usd=balance))
    if not math.isclose(sum(r['capex_usd'] for r in monthly),capex,rel_tol=1e-10):raise ValueError('monthly capital does not reconcile')
    rate=a['annual_interest'];years=a['repayment_years'];payment=debt/years if rate==0 else debt*rate/(1-(1+rate)**-years)
    repayment=[];outstanding=debt
    for year in range(1,years+1):
        interest=outstanding*rate;principal=min(outstanding,payment-interest);repayment.append(dict(year=year,opening_debt_usd=outstanding,interest_usd=interest,principal_usd=principal,debt_service_usd=principal+interest,closing_debt_usd=max(0.,outstanding-principal)));outstanding=max(0.,outstanding-principal)
    rows=[]
    for fare in a['fares_usd']:
        for year in range(1,years+1):
            ramp=a['daily_paid_ramp'][min(year-1,len(a['daily_paid_ramp'])-1)];fare_revenue=daily_paid_trips*a['annual_operating_days']*ramp*fare*a['collection_fraction'];nonfare=fare_revenue*a['nonfare_fraction_of_fares'];net=fare_revenue+nonfare-annual_opex
            reserve=capex*a['renewal_reserve_fraction_capital'];cfads=net-reserve+a['subsidy_usd_year'];gap=max(0.,payment-cfads)
            fx_cfads=(fare_revenue+nonfare)*.8-annual_opex-reserve+a['subsidy_usd_year']
            rows.append(dict(fare_usd=fare,year=year,ramp=ramp,fare_revenue_usd=fare_revenue,nonfare_usd=nonfare,operating_balance_before_subsidy_usd=net,
                annual_opex_usd=annual_opex,renewal_reserve_usd=reserve,explicit_subsidy_usd=a['subsidy_usd_year'],cfads_usd=cfads,debt_service_usd=payment,
                dscr=cfads/payment if payment else None,annual_funding_gap_usd=gap,additional_support_to_target_dscr_usd=max(0.,a['minimum_dscr']*payment-cfads),
                fixed_local_fare_20pct_fx_loss_dscr=fx_cfads/payment if payment else None,fixed_local_fare_20pct_fx_loss_funding_gap_usd=max(0.,payment-fx_cfads)))
    return dict(capital_usd=capex,debt_principal_usd=debt,equity_capital_usd=capex-debt,construction_interest_paid_usd=construction_interest,
        finance_fee_usd=debt*a['finance_fee_fraction'],monthly_construction_cash=monthly,annual_cases=rows,annual_repayment=repayment,
        fare_affordability=dict(reference_workdays_month=22,return_trips_per_day=2,monthly_fare_burden_usd=[dict(fare_usd=f,monthly_cost_usd=44*f) for f in a['fares_usd']],household_income_distribution=None),
        export_credit=dict(applied_or_approved=False,uk_origin_verified=False,uk_content_eligibility=None,reason='case-by-case buyer/lender/export-contract/UK-content/country-cover enquiry required; debt share is a scenario, not a UKEF offer'),
        price_basis='constant2026USD scenarios;6% is an assumed real financing rate, not a lender quote. FX sensitivity holds local fare fixed while its USD value falls20%; debt/opex conservatively remainUSD.',
        signed_fare_or_subsidy_commitment=False,physical_release=False)

def rail_energy_comparison(line,run,a,annual_factor,capital,staff):
    """Same actual services; independent wheel/motor resistance and work ledger."""
    k=a['steel_wheel_comparison'];profile=line['launch_profile'];duration=profile['inputs']['runtime_s'];mass=6*k['gross_car_mass_kg'];quadratic=profile['resistance']['quadratic_n_per_car_per_m_s_squared']*6
    def work(count):
        times=np.linspace(0,duration,count);samples=[corridor.trajectory_at(profile,float(t)) for t in times];speed=np.array([s['speed_m_s'] for s in samples]);acceleration=np.array([s['acceleration_m_s2'] for s in samples]);force=mass*acceleration+mass*9.81*k['rolling_resistance_fraction']+quadratic*speed**2
        return float(np.trapezoid(np.maximum(force*speed,0.),times))/3.6e6/k['traction_efficiency']
    coarse=work(801);fine=work(1601)
    if abs(coarse-fine)>max(.01,abs(fine)*.002):raise ValueError('rail comparator work quadrature not converged')
    loopspeed=line['topology']['loop_speed_screen_kmh']/3.6
    loop_j=.5*mass*loopspeed**2+mass*9.81*k['rolling_resistance_fraction']*line['duty']['arrival_events_per_circuit'][3]['distance_m']
    moving=sum(fine if r['mainline'] else loop_j/3.6e6/k['traction_efficiency'] for r in run['events'])
    hotel=run['services_kwh']*k['hotel_kw_per_car']/a['services_kw_per_car']/a['charge_efficiency'];annual=(moving+hotel)*annual_factor
    opex=staff*a['annual_staff_salary_usd']+annual*a['energy_usd_kwh']+capital*a['maintenance_fraction_capital']
    return dict(mainline_leg_traction_input_kwh=fine,coarse_quadrature_kwh=coarse,annual_grid_kwh=annual,annual_opex_usd=opex,
        common_actual_departures_and_passengers=True,mass_kg_per_car=k['gross_car_mass_kg'],regeneration_credit_kwh=0.,
        method='Positive integral(m*a+rolling resistance+aerodynamic drag)*speed/motor efficiency on exact same trajectory; same source event/dwell/withdrawal schedule, lower rail hotel assumption explicit.',
        limitations=['rail contact/adhesion, brake/motor thermal, actual route curves, dynamic loads, fitout and substations unqualified','resource/QA/maintenance engineering for rail is not inferred from this analytical comparison; no architecture adoption'])

def economics(line,access_value,od,run,a):
    length=line['operational_route_length_m'];civil=delivery.topology_quantities(line);equivalent_length=civil['requested_route_m'];factory=delivery.factory_allocation(equivalent_length/1000);fleet=run['fleet_total'];_,c,rates=model.load()
    base_vehicle=model.cost_case(c,rates,'base',c['mass']['ferrite_base'],30,cars=6)['vehicle_bill']['total_allowance_usd']
    products=pilot_product.products(line['pilot_configuration']);support_cost=sum(products[0]['bom'][j]['cost_usd'] for j in (2,3,4,5))*24
    substitution=pilot_product.reconcile_allowance('magnetic-equipment-usd-per-car',rates['rates']['magnetic_equipment_per_car'],[dict(id='defined-current-coils-sensors-converters',value=support_cost)])
    vehicle=base_vehicle*fleet+max(0.,substitution['reconciled_total']-rates['rates']['magnetic_equipment_per_car'])*6*fleet*(1+rates['rates']['vehicle_integration_reserve_fraction'])
    # Retain the longer front-aligned reference in the primary budget. The
    # shorter unselected layout lacks a fitted504.5m approach/power-zone union.
    platform=219.*18*4;common=[dict(id='station-platform-concrete',quantity=platform*.25,rate=150.),dict(id='station-platform-reinforcement',quantity=platform*.25*160,rate=1.2),
        dict(id='station-roofs',quantity=platform,rate=a['station_roof_usd_m2']),dict(id='station-lifts',quantity=8,rate=a['station_lift_each_usd']),dict(id='station-services',quantity=4,rate=a['station_services_each_usd']),dict(id='terminal-service-cabinets',quantity=len(line['topology']['terminal_service_zones']),rate=a['station_services_each_usd']),
        dict(id='land-utilities',quantity=length,rate=a['land_utilities_route_m_usd']),dict(id='depot-training-startup',quantity=1,rate=a['depot_training_startup_usd']),dict(id='independent-assurance',quantity=1,rate=a['independent_assurance_usd'])]
    for row in common:row['cost_usd']=row['quantity']*row['rate'];row['quoted']=False
    launch=line['launch_loss'];terminal_positions=len(line['topology']['terminal_service_zones']);electrical=(4+terminal_positions/2)*launch['all_profile_assets_allowance_usd']
    maglev_specific=civil['priced_scope_usd']+vehicle+electrical+a['prototype_vehicle_nre_usd'];common_cost=sum(r['cost_usd'] for r in common)+factory['allocated_factory_usd']+factory['allocated_training_usd']
    capital=(maglev_specific+common_cost)*(1+a['design_risk_reserve_fraction']);comparison_line=dict(line,operational_route_length_m=equivalent_length);rail=comparison_bom(comparison_line,fleet,a,topology=civil)
    # Foundations/site/stations/depot are common; rail deck/track/vehicle differ.
    shared_supports=sum(r['cost_usd'] for r in civil['rows'] if r['id'] in {'foundations','columns-caps'})
    comparison_common=comparison_common_rows(common);rail_common_cost=common_cost-comparison_common['excluded_cost_usd']
    rail_capital=(rail['priced_different_scope_usd']+rail_common_cost+shared_supports+a['prototype_vehicle_nre_usd'])*(1+a['design_risk_reserve_fraction'])
    compact_area=114.5*18*4;compact_saving=(platform-compact_area)*(.25*150+.25*160*1.2+a['station_roof_usd_m2'])*(1+a['design_risk_reserve_fraction'])
    factory_startup_extra=(factory['unallocated_factory_usd']+factory['training_programme_usd']-factory['allocated_training_usd'])*(1+a['design_risk_reserve_fraction'])
    annual_factor=a['operating_hours_day']/a['simulation_hours']*a['annual_operating_days'];departed_events=run['events']
    # Mainline DC input already includes copper/converter heat: never add again.
    mainline=[r for r in departed_events if r['mainline']]
    installed=(4+terminal_positions/2)*launch['station_converter_count']
    if not installed.is_integer():raise ValueError('whole installed converter groups required')
    standby=launch_optimisation.idle_control_energy(physical_station_groups=int(installed),trip_groups=launch['station_converter_count'],
        annual_mainline_legs=len(mainline)*annual_factor,runtime_s=sum(r['runtime_s'] for r in mainline)/len(mainline) if mainline else 0.)
    annual_energy=(run['charger_input_kwh']+run['fixed_traction_kwh'])*annual_factor+standby['annual_idle_reconciliation_kwh']
    staff=4*a['staff_per_shift_station']*a['shifts_per_day']+a['control_maintenance_management_staff'];annual_opex=staff*a['annual_staff_salary_usd']+annual_energy*a['energy_usd_kwh']+capital*a['maintenance_fraction_capital']
    build=delivery.construction(quantity_plan=civil);months=max(12,math.ceil((max(build['completion_calendar_day'],270)+90)/30));cash=[0.]*months
    def pay(day,amount):cash[min(months-1,max(0,math.ceil(day/30)-1))]+=amount
    task_index={t['id']:t for t in build['tasks']};beam_count=build['quantities']['beams']
    for row in civil['rows']:
        if row['id'] in {'foundations','columns-caps'}:
            tasks=[t for t in build['tasks'] if t['id'].endswith('/foundation')]
        else:
            stage={'beam-concrete':'cast','beam-reinforcement':'cast','reaction-faces':'stator','transport':'transport','erection':'erect','qa':'qa','stator':'stator','test':'test'}[row['id']]
            tasks=[t for t in build['tasks'] if t['id'].endswith('/'+stage)]
        for task in tasks:pay(task['end_h']/24,row['cost_usd']/len(tasks))
    for fraction,day in ((.10,0.),(.40,120.),(.40,270.),(.10,months*30)):pay(day,vehicle*fraction)
    pay(0,electrical*.3);pay(120,electrical*.7);pay(0,a['prototype_vehicle_nre_usd'])
    for row in common:pay(30,row['cost_usd']*.3);pay(max(150,build['completion_calendar_day']),row['cost_usd']*.7)
    pay(0,factory['allocated_factory_usd']+factory['allocated_training_usd'])
    if not math.isclose(sum(cash),maglev_specific+common_cost,rel_tol=1e-10):raise ValueError('resource/procurement capital attribution differs')
    monthly=[dict(month=i+1,capex_usd=cost*(1+a['design_risk_reserve_fraction'])) for i,cost in enumerate(cash)]
    served=passenger_assignment(od,run,a=a);paid=od['daily_potential_trips']*served['daily_served_fraction']
    return dict(capital_rows_common=common,maglev_specific_civil=civil,vehicle_fleet_allowance_usd=vehicle,station_electrical_allowance_usd=electrical,
        cost_status='unquoted topology/component budget; closing/curved-unit moulds, joints, fit and acceptance remain held; not an orderable/qualified EPC price',vehicle_equipment_cost_substitution=substitution,shared_factory=factory,capital_with_reserve_usd=capital,
        factory_startup_funding=dict(pooled_budget_usd=capital,standalone_budget_usd=capital+factory_startup_extra,additional_standalone_cash_at_start_usd=factory_startup_extra,other_programme_factory_funding_committed=False,pilot_allocation_is_not_full_startup_cash=True,scope='Pooled reference assumes the remaining100km programme pays its share. A standalone pilot must fund the whole factory and training pool at start; additional cash includes the same30%reserve. No other project funding commitment exists.'),
        terminal_electrical_budget=dict(single_direction_service_positions=terminal_positions,additional_station_equivalents=terminal_positions/2,additional_stator_converter_allowance_usd=terminal_positions/2*launch['all_profile_assets_allowance_usd'],additional_charging_cabinet_allowance_usd=terminal_positions*a['station_services_each_usd'],short_zone_design_qualified=False,basis='Conservative full350m winding/converter half-station allowance per single-direction150m terminal service position; no short-zone material credit. Separate cabinets and full-year group idle counted. Exact short-loop force, converter/current, charging and support/access remain held.'),
        platform_budget=dict(reference_length_m=219.,reference_area_m2=platform,reference_is_accepted_design=False,compact_length_m=114.5,compact_area_m2=compact_area,compact_alternative_selected=False,compact_capital_sensitivity_usd=capital-compact_saving,compact_reduction_with_reserve_usd=compact_saving,compact_gate='504.5m power-zone/approach and flare geometry not fitted; no automatic compact-platform cost credit'),
        comparison=rail,comparison_capital_with_reserve_usd=rail_capital,comparison_common_scope_usd=rail_common_cost+shared_supports,comparison_common_rows=comparison_common,
        comparison_shared_supports=dict(allowance_usd=shared_supports,shared_scope_hypothesis_only=True,structural_equivalence_accepted=False,gate='Independent rail deck dead/live reactions, foundation and column design and ground evidence required'),
        comparison_energy_and_operation=rail_energy_comparison(line,run,a,annual_factor,rail_capital,staff),
        staff_positions=staff,annual_train_km=run['train_km']*annual_factor,annual_energy_kwh=annual_energy,annual_opex_usd=annual_opex,
        additional_idle_energy=dict(**standby,full_year_station_group_idle_kwh=standby['full_year_station_idle_kwh'],already_counted_trip_idle_kwh=standby['idle_already_inside_trip_dc_kwh'],
            physical_energy_removal_credit=False,duplicate_constant_load_allocations_corrected=True),
        launch_loss=launch,loss_scope='Exact controlled-mass leg DC import includes converter/copper losses once; additional idle energy separate. Terminal-loop longitudinal energy is only a mass-scaled allowance and retains an electrical/curved-motion gate.',
        monthly_schedule_cash_basis='Exact civil row cash assigned to actual planned cast/foundation/QA/transport/lift/stator/test finish dates; vehicle10/40/40/10 milestones, electrical30/70 deposit/delivery, station30/70 and risk reserve explicit. No signed payment terms.',
        full_line_construction=dict(calendar_days=build['completion_calendar_day'],tasks=len(build['tasks']),beam_units=build['quantities']['beams'],unique_supports=civil['supports'],curved_units=civil['curved_beam_count'],closing_units=civil['closing_beam_count'],quantity_scope=civil['quantity_scope']),
        full_line_delivery_plan=build,
        phased_opening=[dict(phase='1km non-passenger commissioning section',earliest_month=math.ceil(delivery.construction()['completion_calendar_day']/30)+3,revenue_allowed=False),dict(phase='complete6042m/four-stop pilot',earliest_month=months,revenue_allowed=False,gate='independent safety/site/material/hardware/operating acceptance')],
        synthetic_daily_paid_trips=paid,finance=finance(capital,annual_opex,paid,monthly,a=a))

@lru_cache(maxsize=2)
def _study(source):
    a=load();line=controlled_line();walk=access();od=od_model(walk,a);runs=[service(k,line=line,a=a) for k in ('nominal','variable-dwell','withdrawal','receiver-failure','charger-failure','combined-recovery')]
    value=dict(schema=SCHEMA,source_sha256=json.loads(source),configuration_sha256=line['pilot_configuration']['configuration_sha256'],configuration=line['pilot_configuration'],assumptions=a,pilot_line=dict(id=line['line'],length_m=line['operational_route_length_m'],stops=line['operating_plan']['stations'],source_configuration_revision=json.loads(SUMMARY.read_bytes())['configuration_revision'],formation=line['formation'],terminal_topology=line['topology']),
        access=walk,synthetic_demand=od,station_lift_queues=lift_queues(od,a),fixed_line_transfer_journeys=network_transfers(),service_scenarios=runs,passengers=[dict(scenario=r['scenario'],**passenger_assignment(od,r,a=a)) for r in runs],
        high_demand_capacity_control=passenger_assignment(od,runs[0],scale=20,a=a),compact_station=compact_station(),economics=economics(line,walk,od,runs[0],a),
        external_gates=['actual passenger OD, mode share, jobs and affordability survey','station entrances, kerbs, sidewalks, grades, crossings, lift evacuation/power and all site/land permissions','full route and turnback curves, independent brakes, receiving/charging hardware and actual Rust multi-domain commissioning','exact equipped product configuration/loss/price reconciliation, vendor quotes/origin, lenders and signed public support'],
        selected_for_construction=False,**FLAGS)
    if value['source_sha256']!=sources():raise ValueError('pilot sources changed during calculation')
    return encoded(value)
def study():return json.loads(_study(json.dumps(sources(),sort_keys=True)))
def access_svg(v):
    stops=v['pilot_line']['stops'];points=[(s['lon'],s['lat']) for s in stops];lo=[min(p[j] for p in points)-.008 for j in (0,1)];hi=[max(p[j] for p in points)+.008 for j in (0,1)]
    def point(lon,lat):return 70+(lon-lo[0])/(hi[0]-lo[0])*1000,620-(lat-lo[1])/(hi[1]-lo[1])*500
    rows=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="740"><rect width="1200" height="740" fill="#f4f7fa"/><defs><clipPath id="map"><rect x="70" y="120" width="1000" height="500"/></clipPath></defs><g font-family="sans-serif" fill="#16314b"><text x="30" y="35" font-size="24">Baghdad line14: current proposed stops and OSM destinations</text><text x="30" y="65" font-size="16">Open-data walking estimate; no verified accessible route, land or paid-demand acceptance.</text><g clip-path="url(#map)" stroke="#cbd4dc" stroke-width=".6" fill="none">']
    streets=json.loads(gzip.decompress((MAPPING/'walking-streets.geojson.gz').read_bytes()))
    for feature in streets['features']:
        coords=feature['geometry']['coordinates']
        if any(lo[0]<=p[0]<=hi[0] and lo[1]<=p[1]<=hi[1] for p in coords):
            pixels=' '.join(f'{x:.2f},{y:.2f}' for x,y in (point(*p) for p in coords));rows.append(f'<polyline points="{pixels}"/>')
    rows.append('</g>')
    for d in v['access']['destinations']:
        x,y=point(d['lon'],d['lat']);rows.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3" fill="{"#d58542" if d["within_budget"] else "#a7b3bf"}"/>')
    coords=' '.join(f'{x:.2f},{y:.2f}' for x,y in (point(*p) for p in points));rows.append(f'<polyline points="{coords}" stroke="#167e73" fill="none" stroke-width="6"/>')
    for i,s in enumerate(stops):
        x,y=point(s['lon'],s['lat']);rows.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="9" fill="#203e63"/><text x="{x+12:.2f}" y="{y-12:.2f}" font-size="16">{i+1}</text>')
    pop=v['access']['population'][0];rows.append(f'<text x="30" y="680" font-size="17">Modelled20min catchment: {pop["walking_catchment_population"]:,.0f} residents; POI dots show mapped centres, not approved gates.</text><text x="30" y="711" font-size="16">© OpenStreetMap contributors/Geofabrik, ODbL; WorldPop2026 alpha. Route line connects proposed stop coordinates schematically.</text></g></svg>');return '\n'.join(rows)+'\n'
def service_svg(v):
    rows=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="650"><rect width="1200" height="650" fill="#f4f7fa"/><g font-family="sans-serif" fill="#16314b"><text x="30" y="35" font-size="24">Whole-line pilot event replay: source240s policy, no progressive adoption</text>']
    run=v['service_scenarios'][0]
    for event in run['events']:
        if not event['mainline']:continue
        x=70+event['start_s']/run['horizon_s']*1000;y=100+(event['segment']+(3 if event['direction']=='reverse' else 0))*65
        width=(event['release_s']-event['start_s'])/run['horizon_s']*1000;rows.append(f'<rect x="{x:.2f}" y="{y}" width="{width:.2f}" height="28" fill="#268b7d"/>')
    rows.append('<text x="30" y="575" font-size="17">Rows: three forward and three reverse exclusive legs. Each bar includes receiving dwell.</text><text x="30" y="612" font-size="16">Terminal loops, charging, variable dwell, failed receivers/chargers, safe withdrawal and replacement are retained in raw events.</text></g></svg>');return '\n'.join(rows)+'\n'
def readme(v):
    e=v['economics'];walk=v['access']['population'][0]
    return '# Baghdad current-line pilot delivery study\n\nProposed complete line14: four stops over6.042km, with both retained terminal loops. This is a source-bound planning package, not permission to build or run passengers.\n\n[Open-map access](access.svg) · [Service diagram](service.svg) · [Complete calculations/raw events](study.json.gz) · [Source receipt](manifest.json)\n\n'+f'WorldPop2026 modelled20min walking catchment: {walk["walking_catchment_population"]:,.0f} residents; the independent GHSL2025 model gives {v["access"]["population"][1]["walking_catchment_population"]:,.0f}. This substantial source disagreement is not resolved by averaging. Residential pixels are counted once. Strict verified accessible coverage and employment/OD data remain unknown. Step-excluded OSM routes,150m unsurveyed connectors, wheeling speed and lift outages are explicit sensitivities. Dated WorldPop/Geofabrik/OSM primary data and attribution are retained.\n\n'+f'Current240s minimum separation remains; finite four-hour service includes all12moving/terminal events per circuit. This does not demonstrate240s whole-line service: nominal maximum observed departure gap is {v["service_scenarios"][0]["maximum_observed_headway_s"]:.1f}s, including finite startup and receiving-berth constraints. Nominal fleet {v["service_scenarios"][0]["fleet_total"]} including2spares. Failed receiving/charging sites, variable dwell, safe withdrawal and bounded recovery are separate complete replays. Python resource/energy replay is not the progressive Rust prototype or physical whole-line proof. Synthetic OD and segment capacity/unserved demand are exposed.\n\n'+f'Unquoted pilot capital with reserve: ${e["capital_with_reserve_usd"]:,.0f}; annual operating allowance ${e["annual_opex_usd"]:,.0f}. This reference budgets219m platforms. Unselected114.5m direction-aligned platforms produce a sensitivity of ${e["platform_budget"]["compact_capital_sensitivity_usd"]:,.0f}, conditional on a fitted504.5m power-zone and approaches; no compact saving is adopted. Fares, ramp-up, non-fare revenue, explicit subsidy, renewals, annual debt service/DSCR and funding gaps remain sensitivities, not financing commitments. One shared factory pool is allocated by programme output; no origin or local-value certificate is invented. Independent equal-service elevated steel-wheel deck/track/vehicle quantities are comparison-only. Shared rail foundation/column allowances are an unresolved scope hypothesis; heavier deck reactions require independent structural/ground design.\n\n'+v['compact_station']['tradeoff']+'\n\nRemaining gates:\n\n'+'\n'.join('- '+x for x in v['external_gates'])+'\n'
def publish(output=OUTPUT):
    v=study();p=Path(output);p.mkdir(parents=True,exist_ok=True)
    if p.is_symlink() or any(x.is_symlink() or x.name not in FILES|{'manifest.json'} for x in p.iterdir()):raise ValueError('owned pilot packet required')
    raw=encoded(v)
    if len(raw)>MAX_RAW:raise ValueError('bounded pilot raw payload required')
    payload={'study.json.gz':gzip.compress(raw,mtime=0),'access.svg':access_svg(v).encode(),'service.svg':service_svg(v).encode(),'README.md':readme(v).encode()}
    for name,data in payload.items():(p/name).write_bytes(data)
    m=dict(schema=SCHEMA,source_sha256=v['source_sha256'],files_sha256={name:digest(p/name) for name in FILES},**FLAGS);(p/'manifest.json').write_bytes(encoded(m));return verify(p)
def _verified_payload(output):
    p=Path(output)
    if p.is_symlink() or not p.is_dir() or {x.name for x in p.iterdir()}!=FILES|{'manifest.json'} or any(x.is_symlink() for x in p.iterdir()):raise ValueError('exact pilot packet required')
    m=json.loads((p/'manifest.json').read_bytes())
    if m.get('source_sha256')!=sources() or any(m.get(k) is not False for k in FLAGS):raise ValueError('pilot source or acceptance differs')
    for name in FILES:
        if (p/name).stat().st_size>MAX_RAW or digest(p/name)!=m['files_sha256'][name]:raise ValueError('pilot payload checksum/size differs')
    with gzip.GzipFile(fileobj=io.BytesIO((p/'study.json.gz').read_bytes())) as stream:raw=stream.read(MAX_RAW+1)
    v=study()
    if raw!=encoded(v) or (p/'README.md').read_text()!=readme(v) or (p/'access.svg').read_text()!=access_svg(v) or (p/'service.svg').read_text()!=service_svg(v):raise ValueError('pilot recalculation/presentation differs')
    return m,v
def verify(output=OUTPUT):return _verified_payload(output)[0]
def read_summary(output=OUTPUT):
    _,v=_verified_payload(output);e=v['economics'];f=e['finance'];mature=len(v['assumptions']['daily_paid_ramp']);repay={r['year']:r for r in f['annual_repayment']}
    rows=[{**{k:r[k] for k in ('fare_usd','year','ramp','fare_revenue_usd','cfads_usd','debt_service_usd','dscr','annual_funding_gap_usd','additional_support_to_target_dscr_usd','fixed_local_fare_20pct_fx_loss_dscr')},**{k:repay[r['year']][k] for k in ('interest_usd','principal_usd','closing_debt_usd')}} for r in f['annual_cases'] if r['year'] in (1,mature)]
    return dict(schema=SCHEMA,line=v['pilot_line']['id'],route_length_m=v['pilot_line']['length_m'],walking_population=v['access']['population'][0]['walking_catchment_population'],synthetic_daily_trips=v['synthetic_demand']['daily_potential_trips'],fleet_total=v['service_scenarios'][0]['fleet_total'],capital_usd=e['capital_with_reserve_usd'],annual_opex_usd=e['annual_opex_usd'],
        platform_budget=e['platform_budget'],factory_startup_funding=e['factory_startup_funding'],comparison_capital_usd=e['comparison_capital_with_reserve_usd'],comparison_annual_opex_usd=e['comparison_energy_and_operation']['annual_opex_usd'],comparison_shared_supports=e['comparison_shared_supports'],
        configuration_sha256=v['configuration_sha256'],protected_minimum_separation_s=v['service_scenarios'][0]['source_policy_headway_s'],nominal_maximum_observed_gap_s=v['service_scenarios'][0]['maximum_observed_headway_s'],target_240s_whole_line_service_demonstrated=False,finance=dict(debt_principal_usd=f['debt_principal_usd'],equity_capital_usd=f['equity_capital_usd'],construction_interest_paid_usd=f['construction_interest_paid_usd'],finance_fee_usd=f['finance_fee_usd'],repayment_years=v['assumptions']['repayment_years'],annual_interest=v['assumptions']['annual_interest'],total_principal_repaid_usd=sum(r['principal_usd'] for r in f['annual_repayment']),drawn_debt_usd=sum(r['debt_draw_usd'] for r in f['monthly_construction_cash']),cases=rows),
        financial_view=dict(debt_principal_usd=f['debt_principal_usd'],annual_debt_service_usd=f['annual_repayment'][0]['debt_service_usd'],annual_cases=rows,comparison_capital_usd=e['comparison_capital_with_reserve_usd'],comparison_annual_opex_usd=e['comparison_energy_and_operation']['annual_opex_usd']),**FLAGS)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('publish','verify'),nargs='?',default='publish');args=parser.parse_args();print(json.dumps(globals()[args.action](),indent=2))
