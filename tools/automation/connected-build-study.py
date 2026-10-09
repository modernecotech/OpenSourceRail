#!/usr/bin/env python3
"""Generate a connected, qualified-as-study station/civil/battery city package."""
from __future__ import annotations
import argparse
from collections import Counter
from dataclasses import asdict, replace
from datetime import date, timedelta
import gzip
import hashlib
import importlib.util
import json
import math
from osr_mech.provenance import stable_sum as sum
from pathlib import Path
import subprocess
import sys
import tomllib
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(ROOT/'design/component-catalogue/src'))
sys.path.insert(0,str(ROOT/'deployment/erpnext/apps/osr_erpnext'))
sys.path.insert(0,str(ROOT))
from osr_mech.provenance import input_revision, deterministic_gzip
from osr_mech.service_trace import encode_sections
from osr_mech.station.layout import station_layout, step_free_reachability
from osr_mech.station.passenger_demand import station_passenger_demand
from osr_mech.station_capacity import station_capacity_screen
from osr_mech.handling_assurance import beam_stage_assurance
from osr_mech.delivery_commercial import quote_register,procurement_requirements,partial_cashflow_sensitivity
from osr_mech.industrialisation import production_balance,service_finance_gate
from connected_delivery_register import build_register
from osr_mech.buildable_stations import station_variant
from osr_mech.common import StationArchetype, ConsistFamily
from osr_mech.civil.quantity_model import station_structure_quantities
from osr_mech.civil.decked_pi import manufacturing_specification, suspended_load_kg, construction_stage_reactions
from osr_mech.civil.construction import erection_resources, ErectionMethod
from osr_mech.civil.supply import Evidence, SupplierCapacity, validate_supplier_allocations, ErectionFront, DeliveryRoute
from osr_mech.civil.shift_schedule import ShiftCycle, simulate_erection, support_requirements
from osr_mech.civil.span_layout import plan_spans, span_quantities
from osr_mech.civil.calendar import WorkingCalendar
from osr_mech.civil.supply_chain import ComponentDemand, ConstructionSupplyChain
from osr_mech.civil.costing import station_access_cost, reconcile_installed_rate, island_net_saving
from osr_mech.battery_profiles import vehicle_profile, chronological_energy, resolve_profile
from osr_mech.network_energy_duty import network_duty
from osr_mech.network_energy_control import controlled_network_energy
from engineering.interchange.station_ifc import export_variant
from osr_erpnext.construction_fleet import asset_draft, fleet_economics
from engineering.analysis.city_geometry import load_line_coordinates, line_geometry, point_at, local_lonlat


def encode(value):
    raw=(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    # Large expanded networks retain every record in ordinary JSON. Formatting
    # is compact above 45 MiB so source-bound evidence fits repository limits.
    if len(raw)>45*1024*1024:
        raw=(json.dumps(value,separators=(',',':'),sort_keys=True,allow_nan=False)+'\n').encode()
    if len(raw)>50*1024*1024:raise ValueError('Connected artifact needs a lossless partition')
    return raw


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return tomllib.loads(path.read_text()) if path.suffix=='.toml' else json.loads(path.read_text())


def merge(intervals):
    result=[]
    for a,b in sorted(intervals):
        if result and a <= result[-1][1]:
            result[-1][1]=max(result[-1][1],b)
        else:
            result.append([a,b])
    return result


def subtract(intervals, exclusions):
    result=[]
    for a,b in intervals:
        cursor=a
        for x,y in merge(exclusions):
            if y<=cursor or x>=b:
                continue
            if x>cursor:
                result.append((cursor,min(x,b)))
            cursor=max(cursor,y)
            if cursor>=b:
                break
        if cursor<b:
            result.append((cursor,b))
    return result


def corridor_point(route, chainage):
    """Extend terminal tangents so entrance offsets match local CAD datums."""
    distance=chainage*route['geometry_per_chainage']
    points=route['points']
    if distance<0:
        a,b=points[0],points[1];base=a;offset=distance
    elif distance>route['geometry_length_m']:
        a,b=points[-2],points[-1];base=b;offset=distance-route['geometry_length_m']
    else:
        return point_at(points,distance)
    dx,dy=b[0]-a[0],b[1]-a[1];norm=math.hypot(dx,dy)
    return base[0]+dx/norm*offset,base[1]+dy/norm*offset


def split_front(intervals):
    """Two fronts by working length; discontinuous intervals stay explicit."""
    remaining=sum(math.ceil((b-a)/25) for a,b in intervals)//2
    result=[[],[]]
    for a,b in intervals:
        bays=math.ceil((b-a)/25)
        take=min(remaining,bays)
        if take == bays:
            result[0].append((a,b))
        elif take == 0:
            result[1].append((a,b))
        else:
            cut=a+take*25
            result[0].append((a,cut));result[1].append((cut,b))
        remaining-=take
    return result


def beam_demand():
    spec=manufacturing_specification(25.0)
    return ComponentDemand('pi-beam-family',spec['manufactured_study_mass_kg']/1000,25.0,2.9)


def study_supply_chain(fronts, cycle, cfg, logistics, as_of):
    """Requirements for the sensitivity, explicitly separate from real suppliers."""
    total=2*sum(len(f.planned_spans) if f.planned_spans else sum(math.ceil((b-a)/25) for a,b in f.work_intervals_m) for f in fronts)
    machines=len({f.launcher for f in fronts})
    nominal=machines*cycle.bays_launcher_day*2
    evidence=Evidence('components/day, components, t, m, h',
        'RFC 0034 required aggregate supply/haulage capacity; no identified factory or confirmed spare capacity',
        as_of,'low','study-assumed-not-qualified','user-selected-scenario')
    pool=SupplierCapacity(id='assumed-contract-capacity',location='aggregate planning requirement, not a factory',
        delivery_catchment=('study-fronts',),relevant_products=('pi-beam-family',),prestressing_qualified=True,
        beds=None,moulds=None,handling_limit_t=logistics['handling_limit_t'],maximum_length_m=logistics['maximum_length_m'],
        maximum_width_m=logistics['maximum_width_m'],demonstrated_cycle_days=None,total_plant_units_day=nominal,
        contracted_units_day={'pi-beam-family':nominal},storage_units=logistics['factory_buffer_beams'],
        dispatch_units_day=machines*cfg['transport_capacity_beams_day_per_front'],
        existing_commitments='unknown; this is a requirement only',qualification='study-assumed',
        required_upgrades=('actual factory/product qualification and contracted capacity',),
        delivered_prices_usd={},commercial_terms='no quotation or contract',evidence=evidence)
    routes=[DeliveryRoute(id=f.id+'-assumed-route',supplier=pool.id,front=f.id,
        journey_hours=logistics['journey_hours'],trailers=logistics['trailers_per_front'],
        payload_t=logistics['payload_t'],trips_per_trailer_day=logistics['trips_per_trailer_day'],
        delivery_window_hours=logistics['delivery_window_hours'],loading_hours=logistics['loading_hours'],
        unloading_hours=logistics['unloading_hours'],maximum_length_m=logistics['maximum_length_m'],
        bridge_limit_t=logistics['bridge_gross_limit_t'],buffer_beams=cfg['buffer_beams_per_front'],
        access_released=True,turning_space_released=True,loading_equipment_released=True,unloading_equipment_released=True,
        vehicle_tare_t=logistics['vehicle_tare_t'],maximum_width_m=logistics['maximum_width_m'],
        rejection_fraction=logistics['transport_rejection_fraction'],
        fleet_id=f.launcher+'-assumed-haulage',fleet_daily_trips=cfg['transport_capacity_beams_day_per_front'],
        evidence=evidence) for f in fronts]
    return ConstructionSupplyChain([pool],[dict(supplier=pool.id,product='pi-beam-family',units_day=nominal,
        production_start_day=cycle.mobilisation_days+1,acceptance_delay_days=logistics['acceptance_delay_days'],
        manufacturing_rejection_fraction=logistics['manufacturing_rejection_fraction'])],routes,beam_demand(),total,
        allow_study_assumptions=True)


def bind_launcher_pool(fronts, machines):
    """Retain every workfront while sequencing reuse of finite physical plant."""
    if machines<1:raise ValueError('launcher pool must be positive')
    result=[];last={}
    for index,front in enumerate(fronts):
        launcher=f'launcher-{index%machines+1:02d}'
        parents=tuple(dict.fromkeys((*front.predecessors,*([last[launcher]] if launcher in last else []))))
        result.append(replace(front,launcher=launcher,predecessors=parents))
        last[launcher]=front.id
    return result


def foundation_release_calendar(fronts, cycle, cfg, horizon, calendar=None):
    """One support-release team per machine pool slot, following its front queue."""
    queues={};remaining={};releases={}
    for front in fronts:
        queues.setdefault(front.launcher,[]).append(front)
        requirements=support_requirements(front)
        remaining[front.id]=max(0,requirements[-1]-front.available_foundations)
    for day in range(1,horizon+1):
        releases[day]={}
        if calendar and calendar.hours(day,cycle)<=0:continue
        for queue in queues.values():
            front=next((f for f in queue if day>=f.planned_start_day and remaining[f.id]>0),None)
            if front is None:continue
            quantity=min(remaining[front.id],cfg['foundation_release_supports_day_per_front'])
            releases[day][front.id]=quantity;remaining[front.id]-=quantity
    return releases


def conditional_schedule(fronts, cycle, cfg, logistics, as_of, horizon=3650, calendar=None):
    chain=study_supply_chain(fronts,cycle,cfg,logistics,as_of)
    # A transferred machine brings its support-release team and transport fleet;
    # additional front records do not create additional daily resources.
    releases=foundation_release_calendar(fronts,cycle,cfg,horizon,calendar)
    return simulate_erection(fronts,cycle,accepted_beams_day={},delivered_beams_day={},
        supports_released_day=releases,buffer_capacity={f.id:cfg['buffer_beams_per_front'] for f in fronts},
        maximum_days=horizon,supply_chain=chain,calendar=calendar)


def reassigned_ring_fronts(fronts, fixed_finish, ring_line, cfg):
    """Conditional access sensitivity, without asserting feasible site releases."""
    ring=[f for f in fronts if f.line==ring_line]
    last_use={f.launcher:f for f in fronts}
    donors=sorted((f for f in last_use.values() if f.line!=ring_line),key=lambda f:(fixed_finish[f.id],f.id))[:6]
    spans=sorted((s for f in ring for s in f.planned_spans),key=lambda s:s['start_chainage_m'])
    donors=donors[:max(0,len(spans)-2)]
    count=len(donors)+2
    if len(ring)!=2 or not donors:
        raise ValueError('ring sensitivity requires two initial fronts and available radial machines')
    chunks=[spans[i*len(spans)//count:(i+1)*len(spans)//count] for i in range(count)]
    result=[f for f in fronts if f.line!=ring_line]
    assignments=[ring[0],*donors,ring[1]]
    for index,(chunk,original) in enumerate(zip(chunks,assignments)):
        transferred=index not in (0,count-1)
        fid=f'{ring_line}-additional-front-{index}' if transferred else original.id
        f=replace(original,id=fid,line=ring_line,start_chainage_m=chunk[0]['start_chainage_m'],
            end_chainage_m=chunk[-1]['end_chainage_m'],direction=-1 if index==count-1 else 1,
            work_intervals_m=tuple((s['start_chainage_m'],s['end_chainage_m']) for s in chunk),planned_spans=tuple(chunk),
            available_foundations=0 if transferred else original.available_foundations,
            planned_start_day=fixed_finish[original.id]+1 if transferred else 1,
            predecessors=(original.id,) if transferred else (),
            delivery_access=fid+'-conditional-access-unverified',sequential_path=fid+'-conditional-path')
        result.append(f)
    return result


def build(city_dir):
    config=read(ROOT/'lib/templates/accelerated-build.toml')
    delivery_evidence=read(ROOT/'lib/templates/connected-delivery-evidence.json')
    industrial_programme=read(ROOT/'design/industrialisation/programme.json')
    industrial_vendors=read(ROOT/'design/industrialisation/vendor-candidates.json')
    design=read(city_dir/'design.toml')
    passenger_register=read(ROOT/'lib/templates/station-passenger-assignment.json')
    passenger_demand=station_passenger_demand(design,read(city_dir/f"{design['city']['slug']}.toml"),passenger_register)
    templates=read(ROOT/'lib/templates/stations.toml')['archetypes']
    access=read(ROOT/'lib/templates/accessibility.toml')
    costs=read(ROOT/'lib/templates/civil-cost-model.toml')
    packs=read(ROOT/'lib/templates/battery-profiles.json')
    suppliers_raw=read(ROOT/'lib/templates/precast-suppliers.json')
    logistics_raw=read(ROOT/'lib/templates/precast-logistics.json')
    suppliers=[]
    for row in suppliers_raw['suppliers']:
        values=dict(row);values['evidence']=Evidence(**values['evidence'])
        for key in ('delivery_catchment','relevant_products','required_upgrades'):
            values[key]=tuple(values[key])
        suppliers.append(SupplierCapacity(**values))
    validate_supplier_allocations(suppliers,suppliers_raw['allocations'])
    slug=design['city']['slug']
    coordinates=load_line_coordinates(city_dir/f'{slug}.corridor.geojson')
    lon0=sum(s['lon'] for s in design['stations'])/len(design['stations'])
    lat0=sum(s['lat'] for s in design['stations'])/len(design['stations'])
    exclusions={l['name']:[] for l in design['lines']}
    station_rows=[];entrance_features=[];approach_features=[];variants={};geometry_lines={}
    line_by_id={l['name']:l for l in design['lines']}
    for line in design['lines']:
        geometry_lines[line['name']]=line_geometry(coordinates[line['name']],sorted([s for s in design['stations'] if s['line']==line['name']],key=lambda s:s['s_m']),line['length_m'],lon0,lat0)
    for station in design['stations']:
        archetype=station['archetype'];line=line_by_id[station['line']]
        elevated=archetype=='interchange-elevated' or any(s['line']==station['line'] and s['class']=='elevated' and s['from_station_m']<=station['s_m']<=s['to_station_m'] for s in design['civil_segments'])
        params={**templates[archetype],**{k:v for k,v in station.items() if k in ('platform_layout','platform_count','platform_width_m','elevated_height_m','minimum_clear_width_m','layout_exception_reason','levels_m','additional_access_equipment','access_equipment','entrances')},
                'elevation':'elevated' if elevated else 'at-grade','platform_length_m':station['platform_length_m']}
        if elevated and params['platform_layout']!='stacked' and not params.get('layout_exception_reason'):
            params.update(platform_layout='island',platform_count=1,platform_width_m=config['station']['platform_width_m'])
        layout=station_layout(params)
        access_cost=station_access_cost(layout,access)
        civil=station_structure_quantities(layout,station['platform_length_m'],config['station']['transition_length_m']) if elevated else None
        if elevated:
            half=station['platform_length_m']/2+config['station']['transition_length_m']
            exclusions[station['line']].append((max(0,station['s_m']-half),min(line['length_m'],station['s_m']+half)))
        key=(archetype,line['rolling_stock'],elevated,json.dumps(params,sort_keys=True))
        if key not in variants:
            variants[key]=asdict(station_variant(StationArchetype(archetype),params,ConsistFamily(line['rolling_stock'])))
        variant=variants[key]
        variant_id=f'variant-{list(variants).index(key)+1:03d}'
        station_rows.append(dict(id=station['id'],line=station['line'],s_m=station['s_m'],archetype=archetype,
                                 layout=layout.payload(),civil=civil,access_cost=access_cost,product_variant=variant_id,
                                 passenger_demand=passenger_demand['stations'][station['id']],
                                 bidirectional_flow_passengers_hour=None,
                                 separate_stress_case_passengers_hour_each_direction=config['station']['passengers_per_hour_each_direction'],
                                 one_lift_unavailable_study={e.id:step_free_reachability(layout,{e.id}) for e in layout.equipment if e.kind=='lift'},
                                 passenger_flow_accepted=False,evacuation_accepted=False,
                                 additional_street_barriers_assessed=False,
                                 net_island_saving_usd=island_net_saving(0,access_cost['installed_total_usd'],None,None,None)))
        if elevated:
            half_platform=station['platform_length_m']/2
            transition=config['station']['transition_length_m']
            for face in layout.faces:
                points=[]
                sign=1 if face.track_centre_y_mm>=0 else -1
                for step in range(41):
                    relative=-(half_platform+transition)+2*(half_platform+transition)*step/40
                    blend=min(1,max(0,(half_platform+transition-abs(relative))/transition))
                    quintic=10*blend**3-15*blend**4+6*blend**5
                    offset=sign*2.0+(face.track_centre_y_mm/1000-sign*2.0)*quintic
                    chainage=station['s_m']+relative
                    route=geometry_lines[line['name']]
                    x,y=corridor_point(route,chainage)
                    a=corridor_point(route,chainage-1)
                    b=corridor_point(route,chainage+1)
                    dx,dy=b[0]-a[0],b[1]-a[1];norm=math.hypot(dx,dy) or 1
                    lon,lat=local_lonlat([(x-dy/norm*offset,y+dx/norm*offset)],lon0,lat0)[0]
                    points.append([lon,lat])
                approach_features.append(dict(type='Feature',geometry=dict(type='LineString',coordinates=points),
                    properties=dict(station=station['id'],face=face.id,level=face.level,top_of_rail_relative_ground_m=face.top_of_rail_z_mm/1000,
                                    door_side=face.door_side,psd_side=face.psd_side,transition_m=transition,qualified=False)))
        for entrance in layout.entrances:
            # Project along the actual corridor, then offset in its transverse
            # direction. These are proposed locations, never surveyed entrances.
            chainage=station['s_m']+entrance['x_mm']/1000
            x,y=corridor_point(geometry_lines[line['name']],chainage)
            before=corridor_point(geometry_lines[line['name']],chainage-1)
            after=corridor_point(geometry_lines[line['name']],chainage+1)
            dx,dy=after[0]-before[0],after[1]-before[1]
            norm=math.hypot(dx,dy) or 1
            offset=entrance['y_mm']/1000
            # +y is left of increasing station chainage.
            x-=dy/norm*offset;y+=dx/norm*offset
            lon,lat=local_lonlat([(x,y)],lon0,lat0)[0]
            entrance_features.append(dict(type='Feature',geometry=dict(type='Point',coordinates=[lon,lat]),
                properties=dict(station=station['id'],entrance=entrance['id'],level=entrance['level'],
                                surveyed=False,accessible_route_accepted=False,coverage_requires_recheck=True)))
    e=config['erection'];fronts=[];civil_lines=[];all_spans=[]
    if not 1<=e['working_days_per_week']<=7:
        raise ValueError('working days per week must be in [1,7]')
    calendar_config=config['calendar']
    calendar=WorkingCalendar(start_date=e['conditional_ready_date'],
        weekdays=tuple(calendar_config.get('weekdays',range(e['working_days_per_week']))),holidays=tuple(calendar_config['holidays']),
        maintenance_days=tuple(calendar_config['maintenance_days']),
        permitted_hours_by_date=tuple(tuple(row) for row in calendar_config.get('permitted_hours_by_date',[])),
        night_shift_permitted=calendar_config['night_shift_permitted'],
        qualified=False,night_permission_record=calendar_config.get('night_permission_record'),
        relief_roster_record=calendar_config.get('relief_roster_record'))
    for line in design['lines']:
        intervals=merge([(s['from_station_m'],s['to_station_m']) for s in design['civil_segments'] if s['line']==line['name'] and s['class']=='elevated'])
        running=subtract(intervals,exclusions[line['name']])
        planned=plan_spans(line['name'],running)
        all_spans.extend(planned)
        quantities=span_quantities(planned)
        standard=[span for span in planned if span['beam_variant']]
        station_overlap=sum(b-a for a,b in intervals)-sum(b-a for a,b in running)
        civil_lines.append(dict(line=line['name'],elevated_total_m=sum(b-a for a,b in intervals),
            running_elevated_m=sum(b-a for a,b in running),station_and_transition_elevated_m=station_overlap,
            running_bays=quantities['catalogue_bays'],running_support_lines=quantities['proposed_supports'],
            span_quantities=quantities,legacy_rounded_bays=sum(math.ceil((b-a)/25) for a,b in running),station_exclusion_intervals_m=merge(exclusions[line['name']]),
            station_structures_count=sum(s['line']==line['name'] and s['civil'] is not None for s in station_rows)))
        groups=[standard[:len(standard)//2],standard[len(standard)//2:]]
        for index,spans in enumerate(groups,1):
            work=[(span['start_chainage_m'],span['end_chainage_m']) for span in spans]
            if not work:
                continue
            fid=f"{line['name']}-front-{index}"
            interruptions=tuple(range(100,100+e['station_interruption_days_per_front']))
            fronts.append(ErectionFront(fid,line['name'],work[0][0],work[-1][1],1 if index==1 else -1,
                f'launcher-{len(fronts)+1:02d}',f'{fid}-delivery-access-unverified',f'{fid}-sequential-path',
                e['foundation_initial_ahead']+1,interruptions_days=interruptions,
                relocation_days=e['relocation_days'],section_relocation_days=e['relocation_days'],work_intervals_m=tuple(work),planned_spans=tuple(spans)))
            requirements=support_requirements(fronts[-1])
            fronts[-1]=replace(fronts[-1],available_foundations=requirements[min(e['foundation_initial_ahead'],len(requirements))-1])
    fronts=bind_launcher_pool(fronts,e['launchers'])
    scenarios={};files={}
    sensitivities=list(config['sensitivities'])
    if any(line.get('shape')=='ring' for line in design['lines']) and len({f.line for f in fronts})>1:
        sensitivities.append({**sensitivities[0],'id':'initial-accelerated-reassigned'})
    sensitivities.append({**sensitivities[0],'id':'initial-six-day-calendar'})
    for sensitivity in sensitivities:
        case_fronts=fronts
        if sensitivity['id']=='initial-accelerated-reassigned':
            ring_line=next(line['name'] for line in design['lines'] if line.get('shape')=='ring')
            case_fronts=reassigned_ring_fronts(fronts,scenarios['initial-accelerated']['finish_days'],ring_line,e)
        average=sensitivity['assumed_bays_launcher_day']
        productive=(e['shifts_day']*e['hours_shift']-(e['shifts_day']-1)*e['handover_hours']-e['maintenance_hours_day'])*e['productive_fraction']
        bay_hours=productive/average
        cycle=ShiftCycle(shifts_day=e['shifts_day'],hours_shift=e['hours_shift'],productive_fraction=e['productive_fraction'],
                         handover_hours=e['handover_hours'],maintenance_hours_day=e['maintenance_hours_day'],
                         placement_hours_beam=bay_hours*0.25,securing_hours_beam=bay_hours*0.125,advance_hours_bay=bay_hours*0.25,
                         weather_availability=e['weather_availability'],permitted_hours_day=e['permitted_hours_day'],
                         mobilisation_days=e['mobilisation_days'],ramp_up_days=e['ramp_up_days'])
        case_calendar=replace(calendar,weekdays=(0,1,2,3,4,5)) if sensitivity['id']=='initial-six-day-calendar' else calendar
        result=conditional_schedule(case_fronts,cycle,e,config['logistics'],config['schema']['as_of'],calendar=case_calendar)
        day0=date.fromisoformat(e['conditional_ready_date'])
        start_days={}
        for day in result['daily']:
            for row in day['fronts']:
                if row['limiting_resource']=='erection':
                    start_days.setdefault(row['front'],day['day'])
        deployments=[]
        for f in case_fronts:
            finish=result['finish_days'].get(f.id)
            deployments.append({**asdict(f),'available_foundations':None,
                'span_storage_order':'increasing-chainage',
                'installation_order':'increasing-chainage' if f.direction==1 else 'decreasing-chainage',
                'initial_assembly_chainage_m':f.start_chainage_m if f.direction==1 else f.end_chainage_m,
                'final_assembly_chainage_m':f.end_chainage_m if f.direction==1 else f.start_chainage_m,
                'readiness':'hypothetical-released-supports-for-sensitivity',
                'conditional_mobilised_date':(day0+timedelta(days=cycle.mobilisation_days)).isoformat(),
                'conditional_start_date':(day0+timedelta(days=start_days[f.id]-1)).isoformat() if f.id in start_days else None,
                'conditional_finish_date':(day0+timedelta(days=finish-1)).isoformat() if finish else None,
                'conditional_relocation_start_date':(day0+timedelta(days=finish)).isoformat() if finish else None,
                'conditional_recommission_date':(day0+timedelta(days=finish+e['relocation_days'])).isoformat() if finish else None,
                'subsequent_city':None,'compatibility_accepted':False})
        daily=result.pop('daily')
        bottlenecks={f.id:dict(Counter(row['limiting_resource'] for day in daily for row in day['fronts'] if row['front']==f.id)) for f in case_fronts}
        files[f"schedule-{sensitivity['id']}.json.gz"]=deterministic_gzip(encode(daily))
        scenarios[sensitivity['id']]={**result,'assumed_bays_launcher_day':average,
            'assumed_beam_demand_day':len({f.launcher for f in case_fronts})*average*2,
            'scope':'identified catalogue planning spans only; unresolved closures, station structures and special crossings remain separate gates',
            'qualified_supplier_allocation':False,'assumed_accepted_supply_beams_day':len(fronts)*average*2,
            'allocation_strategy':'finite launcher pool; queued line fronts and conditional ring transfers after the final donor assignment' if case_fronts is not fronts else 'two fronts per line queued through the finite launcher pool',
            'added_ring_access_accepted':False,'maximum_launchers':len({f.launcher for f in case_fronts}),
            'assumed_transporters':len({f.launcher for f in case_fronts})*config['logistics']['trailers_per_front'],
            'section_relocation_allowance_days':e['relocation_days'],
            'night_shift_cash_sensitivity_usd':sum(counts.get('erection',0) for counts in bottlenecks.values())*config['finance']['night_shift_cost_usd_per_front_shift'],
            'peak_accepted_factory_buffer_beams':max((r['accepted_factory_stock'] for r in daily),default=0),
            'front_limiting_resource_days':bottlenecks,
            'deployments':deployments,'opening_stages':[
                dict(line=l['name'],conditional_opening_date=(day0+timedelta(days=max((result['finish_days'].get(f.id,3650) for f in case_fronts if f.line==l['name']),default=0)+config['finance']['opening_fitout_days'])).isoformat(),
                     revenue_start_date=None,opening_accepted=False,qualification='running-span-finish-plus-fitout-study; stations-special-crossings-and-rolling-stock-unreleased')
                for l in design['lines']]}
    actual_allocations=[r for r in suppliers_raw['allocations'] if r['product']=='pi-beam-family']
    actual_routes=[]
    for row in logistics_raw['routes']:
        if row['product']=='pi-beam-family':
            parameters=dict(row['parameters'])
            parameters['evidence']=Evidence(**row['evidence'])
            actual_routes.append(DeliveryRoute(**parameters))
    actual_chain=ConstructionSupplyChain(suppliers,actual_allocations,actual_routes,beam_demand(),
        2*sum(len(f.planned_spans) for f in fronts))
    actual=simulate_erection([replace(f,available_foundations=0,planned_start_day=1,relocation_days=0) for f in fronts],
        ShiftCycle(),accepted_beams_day={},delivered_beams_day={},supports_released_day={},
        buffer_capacity={f.id:e['buffer_beams_per_front'] for f in fronts},maximum_days=1,supply_chain=actual_chain)
    beams=[manufacturing_specification(span) for span in (20.0,25.0)]
    for spec in beams:
        spec['lifting_gear_study_kg']=4000
        spec['suspended_study_load_kg']=suspended_load_kg(spec,4000)
        spec['construction_stage_screen']=construction_stage_reactions(spec['suspended_study_load_kg'],120000,spec['span_m'],spec['span_m']/2,2.0,120000)
    files['stations.json']=encode(station_rows)
    files['station-capacity.json']=encode(dict(stations=[station_capacity_screen(s,
        next(d['platform_length_m'] for d in design['stations'] if d['id']==s['id']),delivery_evidence['station_assessments'].get(s['id'])) for s in station_rows],engineering_qualified=False))
    files['beam-stage-assurance.json']=encode(dict(variants=[beam_stage_assurance(span,delivery_evidence['lifting_arrangements'].get(f'OSR-Pi{span:g}')) for span in (20.,25.)],structural_and_lifting_release=False))
    files['station-passenger-demand.json']=encode(passenger_demand)
    files['span-layout.json']=encode(dict(spans=all_spans,quantities=span_quantities(all_spans),
        pier_locations_surveyed=False,construction_design_released=False,
        production_mix_assumption='Pi20/Pi25 aggregate throughput; transport sized conservatively for Pi25. SKU-specific contract and casting-bed assignments remain required.',
        unsupported_closures_excluded_from_catalogue_orders=True))
    product_variants=[{**variant,'archetype':f'variant-{i:03d}','source_archetype':variant['archetype']} for i,variant in enumerate(variants.values(),1)]
    files['station-products.json']=encode(dict(variants=product_variants))
    scratch=ROOT/'build'
    scratch.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='connected-ifc-',dir=scratch) as temporary:
        for variant in product_variants:
            target=Path(temporary)/f"station-{variant['archetype']}.ifc"
            export_variant(variant,target)
            files['ifc/'+target.name]=target.read_bytes()
    files['entrances.geojson']=encode(dict(type='FeatureCollection',features=entrance_features))
    files['station-approaches.geojson']=encode(dict(type='FeatureCollection',features=approach_features))
    files['civil.json']=encode(dict(lines=civil_lines,beams=beams,
        erection_options={method.value:erection_resources(method,sum(l['running_bays'] for l in civil_lines)) for method in ErectionMethod},
        actual_evidence_schedule=actual,conditional_scenarios=scenarios))
    network_plan=ROOT/'engineering/network-planning'/slug/'network-integration.json'
    if network_plan.is_file():
        integrated=read(network_plan)
        if integrated['baseline_native_design_sha256']!=digest(city_dir/'design.toml'):
            raise ValueError('coordinated network input does not match the current line design')
        files['junction-and-residential-interfaces.json']=encode(dict(
            source=network_plan.relative_to(ROOT).as_posix(),source_sha256=digest(network_plan),
            structural_interfaces=integrated['interfaces'],bounded_station_complexes=integrated['bounded_complexes'],
            residential_plan=integrated['population'],new_operating_routes_adopted=False,
            construction_released=False,rail_crossings_are_not_implicit_track_switches=True))
    scenario=read(city_dir/f'{slug}.toml')
    energy=config['energy']
    movement=json.loads(subprocess.check_output(['cargo','run','--quiet','-p','osr-sim','--bin','osr-movement-profiles','--',str(city_dir/f'{slug}.toml')],cwd=ROOT))
    files['movement-profiles.json']=encode(movement)
    duty=network_duty(design,scenario,average_speed_kmh=energy['average_speed_kmh'],
        initial_soc=energy['train_initial_soc'],auxiliary_kw_per_car=energy['auxiliary_kw_per_car'],
        regen_fraction=energy['regenerative_fraction'],minutes=energy['duration_minutes'],movement_profiles=movement)
    trains,sites,visits,departures,mass=(duty[k] for k in ('trains','sites','visits','departures','mass'))
    sites={sid:{**site,'allow_grid_storage_recharge':energy['stationary_grid_replenishment'],
        'storage_recharge_target_soc':energy['stationary_recharge_target_soc']} for sid,site in sites.items()}
    rolling=read(ROOT/'lib/templates/rolling-stock.toml')['profiles']
    for line in design['lines']:
        resolve_profile(rolling[line['rolling_stock']],packs,'onboard')
    reference=packs['profiles']['lfp-onboard-study']
    energy_results={};controlled_results={}
    for case,selection in packs['cases'].items():
        onboard=packs['profiles'][selection['onboard']];stationary=packs['profiles'][selection['stationary']]
        vehicle_rows={name:vehicle_profile(row['reference_mass_kg'],row['cars'],reference,onboard) for name,row in mass.items()}
        selected_trains={tid:{**t,'mass_factor':vehicle_rows[tid.rsplit('-train-',1)[0]]['energy_mass_factor']} for tid,t in trains.items()}
        runs=[]
        for solar in energy['seasonal_solar_factors']:
            result=chronological_energy(onboard,stationary,selected_trains,sites,visits,departures,energy['duration_minutes'],
                ambient_c=energy['ambient_c'],seasonal_solar_factor=solar,cleaning_factor=energy['cleaning_factor'],
                outages=set(range(energy['grid_outage_start_minute'],energy['grid_outage_start_minute']+energy['grid_outage_duration_minutes'])),
                reserve_soc=energy['reserve_soc'],setup_seconds=energy['setup_seconds'],retain_shortfalls=False)
            # All counts and deficits remain; retaining every reserve tick adds
            # no information to this compact comparison.
            shortfalls=result.pop('shortfalls')
            result.update(shortfall_examples=shortfalls[:20],
                seasonal_solar_factor=solar,study_grid_energy_cost_usd=result['totals']['grid_kwh']*config['finance']['energy_usd_kwh'])
            runs.append(result)
        energy_results[case]=dict(profiles=selection,vehicles=vehicle_rows,runs=runs)
        controlled_results[case]=controlled_network_energy(design,scenario,movement,onboard,stationary,selected_trains,sites,energy['duration_minutes'],
            ambient_c=energy['ambient_c'],seasonal_solar_factor=energy['seasonal_solar_factors'][0],cleaning_factor=energy['cleaning_factor'],
            reserve_soc=energy['reserve_soc'],setup_seconds=energy['setup_seconds'],regen_fraction=energy['regenerative_fraction'],
            outages=set(range(energy['grid_outage_start_minute'],energy['grid_outage_start_minute']+energy['grid_outage_duration_minutes'])),
            retain_section_events=True)
        section_events=controlled_results[case].pop('completed_section_events')
        trace_name=f'energy-section-events-{case}.jsonl.gz'
        files[trace_name]=encode_sections(section_events)
        controlled_results[case]['section_event_trace']=dict(path=trace_name,rows=len(section_events),
            sha256=hashlib.sha256(files[trace_name]).hexdigest(),unit='completed train section event')
    small=dict(reference);small.update(nameplate_kwh=75,usable_kwh=60,pack_mass_kg=750,pack_volume_m3=0.45,installed_cost_usd=11250,replacement_cost_usd=9000,id='lfp-small-onboard-separate-duty-study',charge_max_kw=reference['charge_max_kw']/3,discharge_max_kw=reference['discharge_max_kw']/3)
    small_trains={tid:{**t,'mass_factor':(mass[tid.rsplit('-train-',1)[0]]['reference_mass_kg']+t['cars']*(small['pack_mass_kg']-reference['pack_mass_kg']))/mass[tid.rsplit('-train-',1)[0]]['reference_mass_kg']} for tid,t in trains.items()}
    small_result=chronological_energy(small,packs['profiles']['lfp-stationary-study'],small_trains,sites,visits,departures,energy['duration_minutes'],
        ambient_c=energy['ambient_c'],setup_seconds=energy['setup_seconds'],reserve_soc=energy['reserve_soc'],
        cleaning_factor=energy['cleaning_factor'],seasonal_solar_factor=energy['seasonal_solar_factors'][0],
        outages=set(range(energy['grid_outage_start_minute'],energy['grid_outage_start_minute']+energy['grid_outage_duration_minutes'])),retain_shortfalls=False)
    small_shortfalls=small_result.pop('shortfalls');small_result.update(shortfall_examples=small_shortfalls[:20])
    files['energy-control.json']=encode(dict(cases=controlled_results,profiles_supplier_qualified=False))
    files['compact-summary.json']=encode(dict(
        station_count=len(station_rows),station_quantities={key:sum(s['layout']['quantities'].get(key,0) for s in station_rows)
            for key in ('platform_count','boarding_face_count','lift_count','escalator_count','staircase_count','shaft_count')},
        construction_cases={name:{k:case[k] for k in ('days','completed_bays','required_bays','scope','allocation_strategy')}
            for name,case in scenarios.items()},
        energy_cases={name:{k:case[k] for k in ('totals','minimum_soc','dispatch_opportunities','completed_journeys',
            'distinct_energy_held_journeys','service_by_line','section_event_trace')} for name,case in controlled_results.items()},
        expanded_records_preserved=['civil.json','energy.json','energy-control.json'],engineering_release=False))
    envelope_rows=[]
    for identity in ('lfp-onboard-study','sodium-ion-onboard-study'):
        for charge_kw in (180,360,540):
            for ambient in (25,45,50):
                profile={**packs['profiles'][identity],'charge_max_kw':charge_kw}
                probe=chronological_energy(profile,packs['profiles']['lfp-stationary-study'],
                    {'probe':dict(cars=1,initial_soc=.3,energy_kwh_km=3,mass_factor=1,auxiliary_kw=0)},
                    {'site':dict(initial_soc=.8,modules=1,pv_kw=0,grid_kw=550,charger_kw=550)},
                    [dict(train='probe',site='site',arrival_min=0,departure_min=2,required_charge_kwh=0)],[],2,
                    ambient_c=ambient,setup_seconds=energy['setup_seconds'],retain_shortfalls=False)
                envelope_rows.append(dict(base_profile=identity,assumed_charge_max_kw=charge_kw,ambient_c=ambient,
                    two_minute_charger_energy_kwh=probe['totals']['charger_kwh'],final_soc=probe['trains']['probe']['energy']/profile['usable_kwh']))
    files['battery-envelope-sensitivity.json']=encode(dict(rows=envelope_rows,qualification='parameter sweep only; not supplier performance or a network acceptance duty',
        fixed_inputs=dict(usable_kwh=180,initial_soc=.3,grid_kw=550,charger_kw=550,visit_minutes=2,setup_seconds=energy['setup_seconds']),
        overrides='Charge maxima swept independently of chemistry; inherited thermal, taper and efficiency assumptions remain explicit and unqualified.'))
    files['energy.json']=encode(dict(cases=energy_results,small_onboard_separate_option=small_result,
        duty_basis='Declared network stations, fleets, dispatch locations, service headways, station dwell and installed energy-site capacities; native osr-sim rest-to-rest section timing; fixed dispatch assignment diagnostic, not a conflict-qualified timetable.',
        scheduled_dispatch_shortfalls=duty['missed_dispatches'],operating_distance_findings=duty['distance_findings'],
        distance_basis=duty['distance_basis'],journeys=duty['journeys'],train_count=len(trains),site_count=len(sites),charging_visits=len(visits),
        duration_minutes=energy['duration_minutes'],stationary_grid_replenishment=energy['stationary_grid_replenishment'],
        service_disruption_feedback_modelled=False,controlled_feedback_report='energy-control.json',supplier_performance_claim=False))
    # Keep installed reference and incremental cash separately: no removal
    # credit, blanket station saving or unverified factory saving is invented.
    elevated_km=sum(l['running_elevated_m'] for l in civil_lines)/1000
    allowance=costs['procurement']['launcher_whole_beam']['central_cash_allowance_usd']
    reconciliation=reconcile_installed_rate(elevated_km*costs['civil_usd_per_km']['elevated'],None,
        dict(launcher_purchase=allowance))
    files['costs.json']=encode(dict(installed_rate_reconciliation=reconciliation,
        installed_running_scope_allocation_usd={k:v*elevated_km for k,v in costs['construction_scope']['elevated_usd_per_km'].items()},
        station_installed_access_gross_usd=sum(s['access_cost']['installed_total_usd'] for s in station_rows),
        station_annual_access_energy_kwh=sum(s['access_cost']['annual_energy_kwh'] for s in station_rows),
        station_annual_access_maintenance_usd=sum(s['access_cost']['annual_maintenance_usd'] for s in station_rows),
        station_access_replacement_usd=sum(s['access_cost']['replacement_cost_usd'] for s in station_rows),
        station_structure_exceptions_and_special_crossings_usd=None,net_station_savings_usd=None,
        factory_reconciliation=costs['factory_reconciliation'],make_or_buy=[dict(scope=k,contracted_buy_usd=None,new_factory_make_usd=None,comparison_accepted=False) for k in ('delivered-components','project-tooling','factory-upgrades-beds','storage-dispatch','new-factory')],
        launcher_allowance=costs['procurement']['launcher_whole_beam'],
        unpriced_logistics_requirements=dict(transporters=len(fronts)*config['logistics']['trailers_per_front'],
            factory_buffer_beams=config['logistics']['factory_buffer_beams'],
            front_buffer_beams=len(fronts)*e['buffer_beams_per_front'],
            haulage_storage_loading_and_inspection_cash_usd=None,
            source=config['logistics']['source'],qualification=config['logistics']['qualification']),
        reusable_fleet=fleet_economics(allowance,0,1.0,0,0),residual_value_basis='zero-credit sensitivity; quotation/asset valuation absent',
        replacement_costs_separate=True,complete_installed_budget=False,financing_required_usd=None,
        identified_initial_fleet_cash_requirement_usd=allowance,
        payments=[dict(scope='18 launcher deposit',date=(date.fromisoformat(e['conditional_ready_date'])-timedelta(days=e['mobilisation_days'])).isoformat(),cash_usd=allowance*config['finance']['launcher_payment_deposit_fraction'],supplier=None,committed=False),
                  dict(scope='18 launcher commissioning balance',date=e['conditional_ready_date'],cash_usd=allowance*config['finance']['launcher_payment_commissioning_fraction'],supplier=None,committed=False)],
        adopted_finance_comparator='engineering/programme-recalculation/local_positive.json',
        revised_revenue_start_accepted=False))
    quotes=quote_register(delivery_evidence['quotations'],delivery_evidence['as_of'],evidence_root=ROOT)
    requirements=procurement_requirements(span_quantities(all_spans),e['launchers'],len({f.launcher for f in fronts})*config['logistics']['trailers_per_front'])
    files['procurement-evidence.json']=encode(dict(quotations=quotes,requirements=requirements,
        installed_beam_requirements_source='span-layout.json: each catalogue span has identified track-component IDs',
        provisional_launcher_scope=costs['procurement']['launcher_whole_beam'],supplier_capacity_created_by_quotes=False,complete_budget_accepted=False))
    payments=json.loads(files['costs.json'])['payments']
    cash_cases={}
    for name,case in scenarios.items():
        opening=max(row['conditional_opening_date'] for row in case['opening_stages'])
        cash_cases[name]={str(rate):partial_cashflow_sensitivity(payments,opening,rate) for rate in (.04,.08,.12)}
    files['cashflow-sensitivities.json']=encode(dict(cases=cash_cases,priced_scope='unquoted purchase-only launcher allowance; all other unknown scopes excluded',
        annual_rates_are_assumptions=True,complete_financing_usd=None,accepted_revenue_usd=None))
    files['remaining-work.json']=encode(build_register(ROOT,delivery_evidence['acceptance_records']))
    files['industrialisation-programme.json']=encode(dict(
        programme_revision=industrial_programme['revision'],selected_configuration=industrial_programme['selected_configuration'],
        work_packages=industrial_programme['work_packages'],stage_gates=industrial_programme['stages'],
        possible_vendor_ids=[v['id'] for v in industrial_vendors['vendors']],
        production_chain=[production_balance(industrial_programme['supply_chain'],rate,independent_fronts=len(fronts))
            for rate in industrial_programme['supply_chain']['illustrative_bays_launcher_working_day']],
        delivered_service_finance=service_finance_gate(industrial_programme['accepted_services']),
        vehicle_mass_axle_civil_trace='../../../../../../../engineering/industrialisation/vehicle-civil-load-trace.json',
        reference_vehicle_is_not_a_selected_city_configuration=True,
        controlled_city_rolling_stock_families=sorted({line['rolling_stock'] for line in design['lines']}),
        complete_installed_costs_adopted=False,physical_and_commercial_acceptance=False))
    assets=[asset_draft(f'launcher-{i:02d}','whole-beam-launcher',fronts[i-1].id if i<=len(fronts) else None) for i in range(1,e['launchers']+1)]
    for f in fronts:
        assets.extend(asset_draft(f'{f.id}-transporter-{i+1:02d}','long-load-transporter',f.id) for i in range(config['logistics']['trailers_per_front']))
        assets.append(asset_draft(f'{f.id}-lifting-frame','beam-lifting-frame',f.id))
    responsibilities=['erection-supervisor','lifting-supervisor','operator','rigger','signaller','survey','quality-inspector','mechanical-maintenance','electrical-maintenance','delivery-coordinator','factory-production','factory-acceptance']
    crews=[]
    for f in fronts:
        for shift in range(1,e['shifts_day']+1):
            crews.append(dict(department='Civil construction',unit=f.line,crew=f'{f.id}-shift-{shift}',front=f.id,shift=shift,
                equipment=f.launcher,required_roles=responsibilities,qualified_workers=[],native_records=['Department','Employee','Training Program','Project','Task'],
                required_role_quantities={role:2 if role=='rigger' else 1 for role in responsibilities},
                handover_hours=e['handover_hours'],relief_and_leave_coverage_required=True,competency_expiry_checked=True,
                supervised_commissioning_required=True,equipment_specific_assessment_required=True,tasks=['accept-beams','release-supports','place-secure-paired-beams','advance-launcher'],allocation_approved=False))
    transfer_case=scenarios.get('initial-accelerated-reassigned',{})
    transfers=[]
    for deployment in transfer_case.get('deployments',[]):
        if not deployment['predecessors']:
            continue
        parent=deployment['predecessors'][0]
        source=next(d for d in transfer_case['deployments'] if d['id']==parent)
        transfers.append(dict(asset=deployment['launcher'],from_front=parent,to_front=deployment['id'],
            source_finish=source['conditional_finish_date'],destination_start=deployment['conditional_start_date'],
            transporters=[f'{parent}-transporter-{i+1:02d}' for i in range(config['logistics']['trailers_per_front'])],
            lifting_frame=f'{parent}-lifting-frame',transfer_days=e['relocation_days'],
            mobilisation_days=e['mobilisation_days'],access_accepted=False,compatibility_accepted=False,
            foundation_release_basis='transferred support team, assumed rate; no site evidence',
            scenario='initial-accelerated-reassigned',allocation_approved=False))
    files['erp-drafts.json']=encode(dict(assets=assets,crews=crews,conditional_baghdad_reassignments=transfers,
        subsequent_city_transfers=[],transfers_accepted=False))
    files['suppliers.json']=encode(suppliers_raw)
    files['logistics.json']=encode(dict(actual_register=logistics_raw,study_requirements=config['logistics'],
        conditional_cases={name:case['supply_chain'] for name,case in scenarios.items()},
        actual_supply_chain=actual['supply_chain']))
    first=scenarios['initial-accelerated']
    comparison_rows='\n'.join(f"| {name} | {case['runs'][0]['minimum_soc']:.1%} | {case['runs'][0]['totals']['unserved_traction_kwh']:,.0f} | {case['runs'][0]['distinct_energy_affected_journeys']:,} | {case['runs'][0]['reserve_violation_train_minutes']:,} |" for name,case in energy_results.items())
    construction_rows='\n'.join(f"| {name} | {case['days']} | {case['maximum_launchers']} | {case['assumed_transporters']} |" for name,case in scenarios.items())
    files['README.md']=(f'''# {slug.title()} connected construction and battery study

Generated from RFC 0034; {config['schema']['as_of']}. These are unquoted, conditional sensitivities, with no accepted supplier capacity or structural/access releases.

The package has {len(station_rows)} stations, {sum(s['layout']['quantities']['platform_count'] for s in station_rows)} physical platforms and {sum(s['layout']['quantities']['boarding_face_count'] for s in station_rows)} boarding faces. Elevated islands use individually identified lifts, escalators, stairs and shafts; their flow/evacuation/one-lift-out approvals remain open. [Station-specific passenger assignment](station-passenger-demand.json) accepts sourced OD legs, preserves paid journeys versus transfer boardings and links station accumulation to its declared service window. Empty evidence means unknown demand; 3,000 pax/h is a separately labelled stress case. Measured access throughput, assisted rescue and lift-out capacity remain open. [Station quantities and access costs](stations.json), [track-spreading approaches](station-approaches.geojson) and [proposed entrances](entrances.geojson) derive from the same layout. Coverage from accepted accessible entrances remains unknown; the existing centroid-based archive cannot close that assessment.

[Running civil quantities and conditional deployment](civil.json) exclude station and spreading-approach zones. [Identified planning spans and beam requirements](span-layout.json) now conserve interval lengths; non-catalogue closures are explicitly excluded from ordinary beam orders. Pier chainages are proposed and require survey/structural acceptance. The {len(fronts)} workfronts share {len({f.launcher for f in fronts})} configured launchers, with explicit predecessors for queued reuse. Each line has two candidate fronts where running work exists. Each disconnected section has a seven-day assumed relocation allowance; crossing feasibility remains unaccepted. A conditional case transfers available released radial launchers to additional ring fronts while retaining the same active machine/transport fleet. Added access and foundations are hypothetical, and transfer/mobilisation delays remain explicit. Two-shift 1.5, 1.8 and 2.0 bays/day sensitivities use the identified active launchers. Configured spare machines create no independent-front output; each case reports its actual fleet demand. Integer daily schedules are in `schedule-*.json.gz`. The explicit calendar gates working dates for casting, QA, transport, foundations and erection; night restrictions cap erection hours. Supplier-specific shifts, permits, relief and holidays remain unqualified. A six-day sensitivity is reported separately. The initial case completes its running bays in {first['days']} days under its explicit hypothetical supply/readiness inputs; special crossings, station structures, rolling stock and permits remain separate opening gates. The evidence-backed schedule reads the supplier and route registers and completes zero bays because accepted supplier capacity and released supports are absent.

| Construction case | Running-span days | Launchers | Assumed transporters |
| --- | ---: | ---: | ---: |
{construction_rows}

[Supplier register](suppliers.json) records the sourcing basis that Iraq already has many precast facilities and production expertise. No named facility, available beam capacity or assumed contract is adopted. The [logistics plan](logistics.json) now feeds casting, acceptance holds, dispatch limits, gross vehicle/bridge loads, journeys, shared fleets and factory/front buffer limits into the same erection schedule. Rejected components require replacement; blocked storage pauses production. Each front reports days limited by casting, acceptance, transport, foundations or erection. The assumed pool is a resource requirement, not an identified supplier or confirmed spare capacity; real routes and contracts remain in separate registers.

[Supplier quotation and scope requirements](procurement-evidence.json) keep preliminary, firm and contracted prices separate from qualified factory output. [Partial cashflow sensitivities](cashflow-sensitivities.json) link identified purchase payments to each conditional schedule at assumed 4/8/12% simple ACT/365 interest; complete CAPEX/finance and revenue remain unknown. The identified span register provides each catalogue beam requirement; no special span is ordered as an ordinary member.

[Costs and cash sensitivities](costs.json) keep the $9m launcher purchase allowance and exclusions visible. Embedded erection in installed civil rates is unverified, so no net saving or complete financing total is claimed. Gross access equipment, maintenance, replacement, factory scope and night-shift sensitivities remain separate; rolling-stock/electronics factory allowances are retained. Payment dates are conditional cash planning, not purchase orders.

[Energy comparisons](energy.json) cover three continuous service days with overnight state carry-over, and a study policy for grid replenishment of stationary storage within remaining site import capacity. They use explicit pack identities, mass-adjusted traction, shared chargers, setup time, temperature/SOC limits, seasonal solar/cleaning, hot auxiliaries, missed charges, outage/reserve duties and degradation. All three matched chemistry cases report minimum SOC and service shortfalls. The small onboard pack is a separate option. The full-network chronology uses declared stations, fleets, headways, dwell and site capacities with [native section movement timing](movement-profiles.json); it requires timetable qualification and makes no supplier chemistry claim. The fixed-assignment diagnostic retains its declared duties even when energy is missing. The separate [coupled control study](energy-control.json) holds trains at their actual stations when reserve or discharge power is insufficient, continues charging and propagates their unavailability into later dispatches. It reports served/missed opportunities, distinct held journeys and hold minutes. Conflict authorities, berth/depot access, transient traction and field calibration remain unqualified.

The planning duty schedules {len(trains)} trainsets and {len(sites)} energy sites. There are {len(duty['missed_dispatches'])} dispatches without a ready trainset. All matched cases below have service shortfalls under the selected hot-weather assumptions; none qualifies the declared service.

| Case (lower-solar duty) | Minimum SOC | Unserved traction kWh | Distinct energy-affected journeys | Reserve-violation train-minutes |
| --- | ---: | ---: | ---: | ---: |
{comparison_rows}

[ERP planning drafts](erp-drafts.json) identify reusable machines and distinct front/shift crews, with purchase, commissioning, inspection, maintenance, competence and transfer gates. Native Task/ToDo transition hooks require submitted allocation review, current controlled Employee/Asset evidence, shifts, leave, holidays, rest and exclusive allocations. Pack-specific commissioning bindings also feed the native onboard evaluator; study profiles cannot populate them. No live ERP allocation or battery commissioning is approved by this package. Cash purchase, project allocation and residual value are distinct.

[Battery charge/thermal sensitivities](battery-envelope-sensitivity.json) sweep 180/360/540 kW and 25/45/50 °C on two-minute shared-site visits. These parameter probes expose the effect of charge maxima and inherited thermal/taper/efficiency assumptions; they are not supplier claims or full-network service acceptance.

[Structural/handling stage screens](beam-stage-assurance.json) report gross-section properties, selfweight, lift/storage/transport reactions, sling force and launcher-position envelopes. Prestress, reinforcement, release strengths, bearings, fatigue, stability and supplier charts remain unresolved; screens grant no release. [Station area/capacity screens](station-capacity.json) union shared-layout equipment footprints, report unoccupied envelopes and circulation lanes, and accept sourced criteria/lift rates. Evacuation, rescue, walking catchments and site approvals remain open.

[Complete remaining-work register](remaining-work.json) traces all 20 review areas, including rolling-stock/electronics release, redundancy, deployment, workforce, other cities and governance. Missing records and appointments stay open; input receipts cannot authenticate an authority or create acceptance.

[Coordinated industrialisation](industrialisation-programme.json) links the vehicle/bogie interface freeze, staged local manufacture, ordinary/special viaduct packages, accepted production chain, urban access and delivered-service finance. HÜBNER/CRRC and alternative vendors remain proposed; exact products, rights, prices and approvals are open. The LM3 axle-load reference is a study comparator and does not replace this city's configured stock.

[Manifest](manifest.json) hashes every source and output and identifies the source revision and assumption register. Existing finance/proposal packages are retained comparators pending scope-matched adoption; this study is the current connected scenario, not an accepted replacement budget. Regenerate with `.venv/bin/python tools/automation/connected-build-study.py --city {slug}`; verify using `--check`.
''').encode()
    if network_plan.is_file():
        files['README.md']+=b'\n[Coordinated junction and residential interfaces](junction-and-residential-interfaces.json) bind crossings, shared corridors, bounded station complexes and expansion studies to this design. [Per-line foundation and assembly plans](../../../../../../../engineering/network-planning/baghdad/README.md) identify every support, both beam parents, directed launcher sequence and junction-design hold. Proposed access/expansion does not adopt operating service or additional finance.\n'
    sources=[Path(__file__),city_dir/'design.toml',city_dir/f'{slug}.toml',city_dir/f'{slug}.corridor.geojson']
    if network_plan.is_file():sources.append(network_plan)
    sources += [ROOT/'lib/templates'/name for name in ('connected-delivery-evidence.json','station-passenger-assignment.json','precast-logistics.json','accelerated-build.toml','stations.toml','accessibility.toml','rolling-stock.toml','energy-sites.toml','battery-profiles.json','precast-suppliers.json','civil-cost-calibration.toml','civil-cost-model.toml')]
    sources += [ROOT/'design/component-catalogue/src/osr_mech'/name for name in ('station_capacity.py','handling_assurance.py','delivery_commercial.py')]
    sources += [ROOT/'tools/automation/connected_delivery_register.py']
    sources += [ROOT/'design/industrialisation'/name for name in ('programme.json','vendor-candidates.json')]
    sources += [ROOT/'design/component-catalogue/src/osr_mech/industrialisation.py']
    sources += [ROOT/'design/component-catalogue/src/osr_mech/service_trace.py']
    sources += sorted((ROOT/'crates/osr-bms/src').glob('*.rs'))
    sources += [ROOT/'crates/osr-sim/src'/name for name in ('battery.rs','onboard.rs','scenario_file.rs','physics.rs','sim.rs','bin/osr-movement-profiles.rs')]
    sources += [ROOT/'Cargo.toml',ROOT/'Cargo.lock',ROOT/'crates/osr-sim/Cargo.toml',ROOT/'crates/osr-bms/Cargo.toml',ROOT/'crates/osr-core/src/consist.rs']
    sources += [ROOT/'deployment/erpnext/apps/osr_erpnext/osr_erpnext'/name for name in ('construction_execution.py','hooks.py','workforce_rules.py')]
    sources += sorted((ROOT/'design/component-catalogue/src/osr_mech/civil').glob('*.py'))
    sources += sorted((ROOT/'design/component-catalogue/src/osr_mech/station').glob('*.py'))
    sources += [ROOT/'design/component-catalogue/src/osr_mech/cad.py',ROOT/'design/component-catalogue/src/osr_mech/common.py']
    sources += [ROOT/'design/component-catalogue/src/osr_mech'/name for name in ('station/layout.py','station/product_geometry.py','buildable_stations.py','battery_profiles.py','network_energy_duty.py','network_energy_control.py','provenance.py')]
    sources += [ROOT/'design/component-catalogue/src/osr_mech/freecad_station_library.py',ROOT/'engineering/interchange/station_ifc.py',ROOT/'deployment/erpnext/apps/osr_erpnext/osr_erpnext/setup.py',ROOT/'deployment/erpnext/apps/osr_erpnext/osr_erpnext/construction_fleet.py',ROOT/'engineering/analysis/city_geometry.py',ROOT/'docs/rfcs/0034-connected-station-production-and-battery-model.md']
    cad_root=city_dir/'engineering/connected-build/cad'
    cad_index=cad_root/'station-library.index.json'
    native_cad=dict(status='not-generated')
    if cad_index.is_file():
        index=read(cad_index)
        native_cad=dict(status='current' if index['manifest_sha256']==hashlib.sha256(files['station-products.json']).hexdigest() and all(digest(ROOT/path)==sha for path,sha in index.get('geometry_sources_sha256',{}).items()) else 'stale',
                       manifest_sha256=index['manifest_sha256'],reopen_validated=index['passed'],
                       files_sha256={p.relative_to(city_dir/'engineering/connected-build').as_posix():digest(p) for p in sorted(cad_root.iterdir()) if p.suffix in ('.FCStd','.json')})
    source_hashes={p.relative_to(ROOT).as_posix():digest(p) for p in sources}
    manifest=dict(native_cad=native_cad,schema=2,source_revision=input_revision(source_hashes),source_revision_kind='sha256-input-content',
        assumptions=config,source_sha256=source_hashes,
        output_sha256={name:hashlib.sha256(data).hexdigest() for name,data in files.items()},
        current_connected_study=True,engineering_qualified=False,supplier_quotations=len(quotes),
        adopted_archive_status='prior finance/coverage/proposals retained as comparators; no scope-matched acceptance',
        unresolved=['station structural and launcher clearances','full passenger flow/evacuation and one-lift-out assessment','supplier contracted capacity and product qualification','delivery routes and bridge/access restrictions','embedded installed-rate erection credit','complete chronological network timetable','accessible-entrance population coverage','procurement and financing commitments'])
    files['manifest.json']=encode(manifest)
    return files


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--city',default='baghdad')
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--refresh-cad',action='store_true',help='regenerate native FreeCAD station study variants after writing the package')
    args=parser.parse_args()
    matches=[p.parent for p in (ROOT/'cities/catalogue').glob('*/*/*/design.toml') if read(p)['city']['slug']==args.city]
    if len(matches)!=1:
        raise SystemExit('city must resolve to one design')
    city=matches[0];output=city/'engineering/connected-build'
    files=build(city)
    if args.check:
        stale=[name for name,data in files.items() if not (output/name).is_file() or (output/name).read_bytes()!=data]
        native=json.loads(files['manifest.json'])['native_cad']
        if native['status'] != 'current' or not native.get('reopen_validated'):
            stale.append('native CAD requires --refresh-cad')
        if stale:
            raise SystemExit('stale connected package: '+', '.join(stale))
        print('current connected package: '+args.city)
        return
    output.mkdir(parents=True,exist_ok=True)
    for name,data in files.items():
        (output/name).parent.mkdir(parents=True,exist_ok=True)
        (output/name).write_bytes(data)
    if args.refresh_cad:
        subprocess.run([str(ROOT/'design/component-catalogue/scripts/freecad_station_library.sh'),
                        '--manifest',str(output/'station-products.json'),'--output-root',str(output/'cad')],cwd=ROOT,check=True)
        manifest=read(output/'manifest.json')
        index=read(output/'cad/station-library.index.json')
        manifest['native_cad']=dict(status='current',manifest_sha256=index['manifest_sha256'],reopen_validated=index['passed'],
            files_sha256={p.relative_to(output).as_posix():digest(p) for p in sorted((output/'cad').iterdir()) if p.suffix in ('.FCStd','.json')})
        (output/'manifest.json').write_bytes(encode(manifest))
    print(f'Generated {len(files)} connected study artifacts for {args.city}')


if __name__=='__main__':
    main()
