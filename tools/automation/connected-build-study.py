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
from pathlib import Path
import subprocess
import sys
import tomllib
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'design/component-catalogue/src'))
sys.path.insert(0,str(ROOT/'deployment/erpnext/apps/osr_erpnext'))
sys.path.insert(0,str(ROOT))
from osr_mech.station.layout import station_layout, step_free_reachability
from osr_mech.buildable_stations import station_variant
from osr_mech.common import StationArchetype, ConsistFamily
from osr_mech.civil.quantity_model import station_structure_quantities
from osr_mech.civil.decked_pi import manufacturing_specification, suspended_load_kg, construction_stage_reactions
from osr_mech.civil.construction import erection_resources, ErectionMethod
from osr_mech.civil.supply import Evidence, SupplierCapacity, validate_supplier_allocations, ErectionFront, DeliveryRoute
from osr_mech.civil.shift_schedule import ShiftCycle, simulate_erection, support_requirements
from osr_mech.civil.supply_chain import ComponentDemand, ConstructionSupplyChain
from osr_mech.civil.costing import station_access_cost, reconcile_installed_rate, island_net_saving
from osr_mech.battery_profiles import vehicle_profile, chronological_energy, resolve_profile
from osr_mech.network_energy_duty import network_duty
from engineering.interchange.station_ifc import export_variant
from osr_erpnext.construction_fleet import asset_draft, fleet_economics
from engineering.analysis.city_geometry import load_line_coordinates, line_geometry, point_at, local_lonlat


def encode(value):
    return (json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()


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
    return ComponentDemand('pi-beam25',spec['manufactured_study_mass_kg']/1000,25.0,2.9)


def study_supply_chain(fronts, cycle, cfg, logistics, as_of):
    """Requirements for the sensitivity, explicitly separate from real suppliers."""
    total=sum(2*sum(math.ceil((b-a)/25) for a,b in f.work_intervals_m) for f in fronts)
    nominal=len(fronts)*cycle.bays_launcher_day*2
    evidence=Evidence('components/day, components, t, m, h',
        'RFC 0034 required aggregate supply/haulage capacity; no identified factory or confirmed spare capacity',
        as_of,'low','study-assumed-not-qualified','user-selected-scenario')
    pool=SupplierCapacity(id='assumed-contract-capacity',location='aggregate planning requirement, not a factory',
        delivery_catchment=('study-fronts',),relevant_products=('pi-beam25',),prestressing_qualified=True,
        beds=None,moulds=None,handling_limit_t=logistics['handling_limit_t'],maximum_length_m=logistics['maximum_length_m'],
        maximum_width_m=logistics['maximum_width_m'],demonstrated_cycle_days=None,total_plant_units_day=nominal,
        contracted_units_day={'pi-beam25':nominal},storage_units=logistics['factory_buffer_beams'],
        dispatch_units_day=len(fronts)*cfg['transport_capacity_beams_day_per_front'],
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
        fleet_id=f.id+'-assumed-haulage',fleet_daily_trips=cfg['transport_capacity_beams_day_per_front'],
        evidence=evidence) for f in fronts]
    return ConstructionSupplyChain([pool],[dict(supplier=pool.id,product='pi-beam25',units_day=nominal,
        production_start_day=cycle.mobilisation_days+1,acceptance_delay_days=logistics['acceptance_delay_days'],
        manufacturing_rejection_fraction=logistics['manufacturing_rejection_fraction'])],routes,beam_demand(),total,
        allow_study_assumptions=True)


def conditional_schedule(fronts, cycle, cfg, logistics, as_of, horizon=3650):
    chain=study_supply_chain(fronts,cycle,cfg,logistics,as_of)
    releases={day:{f.id:cfg['foundation_release_supports_day_per_front'] for f in fronts} for day in range(1,horizon+1)}
    return simulate_erection(fronts,cycle,accepted_beams_day={},delivered_beams_day={},
        supports_released_day=releases,buffer_capacity={f.id:cfg['buffer_beams_per_front'] for f in fronts},
        maximum_days=horizon,supply_chain=chain)


def build(city_dir):
    config=read(ROOT/'lib/templates/accelerated-build.toml')
    design=read(city_dir/'design.toml')
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
                                 bidirectional_flow_passengers_hour=config['station']['passengers_per_hour_each_direction'],
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
    e=config['erection'];fronts=[];civil_lines=[]
    if e['working_days_per_week'] != 7:
        raise ValueError('connected sensitivity uses a seven-day calendar; supply/work windows must be rescheduled for other calendars')
    for line in design['lines']:
        intervals=merge([(s['from_station_m'],s['to_station_m']) for s in design['civil_segments'] if s['line']==line['name'] and s['class']=='elevated'])
        running=subtract(intervals,exclusions[line['name']])
        station_overlap=sum(b-a for a,b in intervals)-sum(b-a for a,b in running)
        civil_lines.append(dict(line=line['name'],elevated_total_m=sum(b-a for a,b in intervals),
            running_elevated_m=sum(b-a for a,b in running),station_and_transition_elevated_m=station_overlap,
            running_bays=sum(math.ceil((b-a)/25) for a,b in running),running_support_lines=sum(math.ceil((b-a)/25)+1 for a,b in running),station_exclusion_intervals_m=merge(exclusions[line['name']]),
            station_structures_count=sum(s['line']==line['name'] and s['civil'] is not None for s in station_rows)))
        for index,work in enumerate(split_front(running),1):
            if not work:
                continue
            fid=f"{line['name']}-front-{index}"
            interruptions=tuple(range(100,100+e['station_interruption_days_per_front']))
            fronts.append(ErectionFront(fid,line['name'],work[0][0],work[-1][1],1 if index==1 else -1,
                f'launcher-{len(fronts)+1:02d}',f'{fid}-delivery-access-unverified',f'{fid}-sequential-path',
                e['foundation_initial_ahead']+1,interruptions_days=interruptions,
                relocation_days=e['relocation_days'],work_intervals_m=tuple(work)))
            requirements=support_requirements(fronts[-1])
            fronts[-1]=replace(fronts[-1],available_foundations=requirements[min(e['foundation_initial_ahead'],len(requirements))-1])
    if len(fronts)>e['launchers']:
        raise ValueError('independent fronts exceed available launcher fleet')
    scenarios={};files={}
    for sensitivity in config['sensitivities']:
        average=sensitivity['assumed_bays_launcher_day']
        productive=(e['shifts_day']*e['hours_shift']-(e['shifts_day']-1)*e['handover_hours']-e['maintenance_hours_day'])*e['productive_fraction']
        bay_hours=productive/average
        cycle=ShiftCycle(shifts_day=e['shifts_day'],hours_shift=e['hours_shift'],productive_fraction=e['productive_fraction'],
                         handover_hours=e['handover_hours'],maintenance_hours_day=e['maintenance_hours_day'],
                         placement_hours_beam=bay_hours*0.25,securing_hours_beam=bay_hours*0.125,advance_hours_bay=bay_hours*0.25,
                         weather_availability=e['weather_availability'],permitted_hours_day=e['permitted_hours_day'],
                         mobilisation_days=e['mobilisation_days'],ramp_up_days=e['ramp_up_days'])
        result=conditional_schedule(fronts,cycle,e,config['logistics'],config['schema']['as_of'])
        day0=date.fromisoformat(e['conditional_ready_date'])
        start_days={}
        for day in result['daily']:
            for row in day['fronts']:
                if row['limiting_resource']=='erection':
                    start_days.setdefault(row['front'],day['day'])
        deployments=[]
        for f in fronts:
            finish=result['finish_days'].get(f.id)
            deployments.append({**asdict(f),'available_foundations':None,
                'readiness':'hypothetical-released-supports-for-sensitivity',
                'conditional_mobilised_date':(day0+timedelta(days=cycle.mobilisation_days)).isoformat(),
                'conditional_start_date':(day0+timedelta(days=start_days[f.id]-1)).isoformat() if f.id in start_days else None,
                'conditional_finish_date':(day0+timedelta(days=finish-1)).isoformat() if finish else None,
                'conditional_relocation_start_date':(day0+timedelta(days=finish)).isoformat() if finish else None,
                'conditional_recommission_date':(day0+timedelta(days=finish+e['relocation_days'])).isoformat() if finish else None,
                'subsequent_city':None,'compatibility_accepted':False})
        daily=result.pop('daily')
        bottlenecks={f.id:dict(Counter(row['limiting_resource'] for day in daily for row in day['fronts'] if row['front']==f.id)) for f in fronts}
        files[f"schedule-{sensitivity['id']}.json.gz"]=gzip.compress(encode(daily),mtime=0)
        scenarios[sensitivity['id']]={**result,'assumed_bays_launcher_day':average,
            'assumed_beam_demand_day':sensitivity['assumed_beam_demand_day'],
            'scope':'running spans only; station structures and special crossings are separate unreleased paths',
            'qualified_supplier_allocation':False,'assumed_accepted_supply_beams_day':len(fronts)*average*2,
            'night_shift_cash_sensitivity_usd':sum(result['finish_days'].values())*config['finance']['night_shift_cost_usd_per_front_shift'],
            'peak_accepted_factory_buffer_beams':max((r['accepted_factory_stock'] for r in daily),default=0),
            'front_limiting_resource_days':bottlenecks,
            'deployments':deployments,'opening_stages':[
                dict(line=l['name'],conditional_opening_date=(day0+timedelta(days=max((result['finish_days'].get(f.id,3650) for f in fronts if f.line==l['name']),default=0)+config['finance']['opening_fitout_days'])).isoformat(),
                     revenue_start_date=None,opening_accepted=False,qualification='running-span-finish-plus-fitout-study; stations-special-crossings-and-rolling-stock-unreleased')
                for l in design['lines']]}
    actual_allocations=[r for r in suppliers_raw['allocations'] if r['product']=='pi-beam25']
    actual_routes=[]
    for row in logistics_raw['routes']:
        if row['product']=='pi-beam25':
            parameters=dict(row['parameters'])
            parameters['evidence']=Evidence(**row['evidence'])
            actual_routes.append(DeliveryRoute(**parameters))
    actual_chain=ConstructionSupplyChain(suppliers,actual_allocations,actual_routes,beam_demand(),
        2*sum(sum(math.ceil((b-a)/25) for a,b in f.work_intervals_m) for f in fronts))
    actual=simulate_erection([replace(f,available_foundations=0,planned_start_day=1,relocation_days=0) for f in fronts],
        ShiftCycle(),accepted_beams_day={},delivered_beams_day={},supports_released_day={},
        buffer_capacity={f.id:e['buffer_beams_per_front'] for f in fronts},maximum_days=1,supply_chain=actual_chain)
    beams=[manufacturing_specification(span) for span in (20.0,25.0)]
    for spec in beams:
        spec['lifting_gear_study_kg']=4000
        spec['suspended_study_load_kg']=suspended_load_kg(spec,4000)
        spec['construction_stage_screen']=construction_stage_reactions(spec['suspended_study_load_kg'],120000,spec['span_m'],spec['span_m']/2,2.0,120000)
    files['stations.json']=encode(station_rows)
    product_variants=[{**variant,'archetype':f'variant-{i:03d}','source_archetype':variant['archetype']} for i,variant in enumerate(variants.values(),1)]
    files['station-products.json']=encode(dict(variants=product_variants))
    with tempfile.TemporaryDirectory(prefix='connected-ifc-',dir=ROOT/'build') as temporary:
        for variant in product_variants:
            target=Path(temporary)/f"station-{variant['archetype']}.ifc"
            export_variant(variant,target)
            files['ifc/'+target.name]=target.read_bytes()
    files['entrances.geojson']=encode(dict(type='FeatureCollection',features=entrance_features))
    files['station-approaches.geojson']=encode(dict(type='FeatureCollection',features=approach_features))
    files['civil.json']=encode(dict(lines=civil_lines,beams=beams,
        erection_options={method.value:erection_resources(method,sum(l['running_bays'] for l in civil_lines)) for method in ErectionMethod},
        actual_evidence_schedule=actual,conditional_scenarios=scenarios))
    scenario=read(city_dir/f'{slug}.toml')
    energy=config['energy']
    duty=network_duty(design,scenario,average_speed_kmh=energy['average_speed_kmh'],
        initial_soc=energy['train_initial_soc'],auxiliary_kw_per_car=energy['auxiliary_kw_per_car'],
        regen_fraction=energy['regenerative_fraction'],minutes=energy['duration_minutes'])
    trains,sites,visits,departures,mass=(duty[k] for k in ('trains','sites','visits','departures','mass'))
    rolling=read(ROOT/'lib/templates/rolling-stock.toml')['profiles']
    for line in design['lines']:
        resolve_profile(rolling[line['rolling_stock']],packs,'onboard')
    reference=packs['profiles']['lfp-onboard-study']
    energy_results={}
    for case,selection in packs['cases'].items():
        onboard=packs['profiles'][selection['onboard']];stationary=packs['profiles'][selection['stationary']]
        vehicle_rows={name:vehicle_profile(row['reference_mass_kg'],row['cars'],reference,onboard) for name,row in mass.items()}
        selected_trains={tid:{**t,'mass_factor':vehicle_rows[tid.rsplit('-train-',1)[0]]['energy_mass_factor']} for tid,t in trains.items()}
        runs=[]
        for solar in energy['seasonal_solar_factors']:
            result=chronological_energy(onboard,stationary,selected_trains,sites,visits,departures,energy['duration_minutes'],
                ambient_c=energy['ambient_c'],seasonal_solar_factor=solar,cleaning_factor=energy['cleaning_factor'],
                outages=set(range(energy['grid_outage_start_minute'],energy['grid_outage_start_minute']+energy['grid_outage_duration_minutes'])),
                reserve_soc=energy['reserve_soc'],setup_seconds=energy['setup_seconds'])
            # All counts and deficits remain; retaining every reserve tick adds
            # no information to this compact comparison.
            shortfalls=result.pop('shortfalls')
            result.update(shortfall_events=len(shortfalls),shortfall_examples=shortfalls[:20],
                seasonal_solar_factor=solar,study_grid_energy_cost_usd=result['totals']['grid_kwh']*config['finance']['energy_usd_kwh'])
            runs.append(result)
        energy_results[case]=dict(profiles=selection,vehicles=vehicle_rows,runs=runs)
    small=dict(reference);small.update(nameplate_kwh=75,usable_kwh=60,pack_mass_kg=750,pack_volume_m3=0.45,installed_cost_usd=11250,replacement_cost_usd=9000,id='lfp-small-onboard-separate-duty-study',charge_max_kw=reference['charge_max_kw']/3,discharge_max_kw=reference['discharge_max_kw']/3)
    small_trains={tid:{**t,'mass_factor':(mass[tid.rsplit('-train-',1)[0]]['reference_mass_kg']+t['cars']*(small['pack_mass_kg']-reference['pack_mass_kg']))/mass[tid.rsplit('-train-',1)[0]]['reference_mass_kg']} for tid,t in trains.items()}
    small_result=chronological_energy(small,packs['profiles']['lfp-stationary-study'],small_trains,sites,visits,departures,energy['duration_minutes'],
        ambient_c=energy['ambient_c'],setup_seconds=energy['setup_seconds'],reserve_soc=energy['reserve_soc'],
        cleaning_factor=energy['cleaning_factor'],seasonal_solar_factor=energy['seasonal_solar_factors'][0],
        outages=set(range(energy['grid_outage_start_minute'],energy['grid_outage_start_minute']+energy['grid_outage_duration_minutes'])))
    small_shortfalls=small_result.pop('shortfalls');small_result.update(shortfall_events=len(small_shortfalls),shortfall_examples=small_shortfalls[:20])
    files['energy.json']=encode(dict(cases=energy_results,small_onboard_separate_option=small_result,
        duty_basis='Declared network stations, fleets, dispatch locations, service headways, station dwell and installed energy-site capacities; explicit average-speed planning chronology, not a validated timetable.',
        scheduled_dispatch_shortfalls=duty['missed_dispatches'],train_count=len(trains),site_count=len(sites),charging_visits=len(visits),
        supplier_performance_claim=False))
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
                handover_hours=e['handover_hours'],relief_and_leave_coverage_required=True,competency_expiry_checked=True,
                supervised_commissioning_required=True,equipment_specific_assessment_required=True,tasks=['accept-beams','release-supports','place-secure-paired-beams','advance-launcher'],allocation_approved=False))
    files['erp-drafts.json']=encode(dict(assets=assets,crews=crews,subsequent_city_transfers=[],transfers_accepted=False))
    files['suppliers.json']=encode(suppliers_raw)
    files['logistics.json']=encode(dict(actual_register=logistics_raw,study_requirements=config['logistics'],
        conditional_cases={name:case['supply_chain'] for name,case in scenarios.items()},
        actual_supply_chain=actual['supply_chain']))
    first=scenarios['initial-accelerated']
    comparison_rows='\n'.join(f"| {name} | {case['runs'][0]['minimum_soc']:.1%} | {case['runs'][0]['totals']['unserved_traction_kwh']:,.0f} | {case['runs'][0]['shortfall_events']:,} |" for name,case in energy_results.items())
    files['README.md']=(f'''# {slug.title()} connected construction and battery study

Generated from RFC 0034; {config['schema']['as_of']}. These are unquoted, conditional sensitivities, with no accepted supplier capacity or structural/access releases.

The package has {len(station_rows)} stations, {sum(s['layout']['quantities']['platform_count'] for s in station_rows)} physical platforms and {sum(s['layout']['quantities']['boarding_face_count'] for s in station_rows)} boarding faces. Elevated islands use individually identified lifts, escalators, stairs and shafts; their flow/evacuation/one-lift-out approvals remain open. [Station quantities and access costs](stations.json), [track-spreading approaches](station-approaches.geojson) and [proposed entrances](entrances.geojson) derive from the same layout. Coverage from accepted accessible entrances remains unknown; the existing centroid-based archive cannot close that assessment.

[Running civil quantities and conditional deployment](civil.json) exclude station and spreading-approach zones. The {len(fronts)} independent fronts initially use two launchers per line where running work exists. The 18-machine/two-shift 1.5, 1.8 and 2.0 bays/day sensitivities retain 54, 64.8 and 72 beams/day as average fleet demands. Integer daily schedules are in `schedule-*.json.gz`. The initial case completes its running bays in {first['days']} days under its explicit hypothetical supply/readiness inputs; special crossings, station structures, rolling stock and permits remain separate opening gates. The evidence-backed schedule reads the supplier and route registers and completes zero bays because accepted supplier capacity and released supports are absent.

[Supplier register](suppliers.json) records the sourcing basis that Iraq already has many precast facilities and production expertise. No named facility, available beam capacity or assumed contract is adopted. The [logistics plan](logistics.json) now feeds casting, acceptance holds, dispatch limits, gross vehicle/bridge loads, journeys, shared fleets and factory/front buffer limits into the same erection schedule. Rejected components require replacement; blocked storage pauses production. Each front reports days limited by casting, acceptance, transport, foundations or erection. The assumed pool is a resource requirement, not an identified supplier or confirmed spare capacity; real routes and contracts remain in separate registers.

[Costs and cash sensitivities](costs.json) keep the $9m launcher purchase allowance and exclusions visible. Embedded erection in installed civil rates is unverified, so no net saving or complete financing total is claimed. Gross access equipment, maintenance, replacement, factory scope and night-shift sensitivities remain separate; rolling-stock/electronics factory allowances are retained. Payment dates are conditional cash planning, not purchase orders.

[Energy comparisons](energy.json) use explicit pack identities, mass-adjusted traction, shared chargers, setup time, temperature/SOC limits, seasonal solar/cleaning, hot auxiliaries, missed charges, outage/reserve duties and degradation. All three matched chemistry cases report minimum SOC and service shortfalls. The small onboard pack is a separate option. The full-network chronology uses declared stations, fleets, headways, dwell and site capacities with an explicit average-speed screen; it requires timetable qualification and makes no supplier chemistry claim.

The planning duty schedules {len(trains)} trainsets and {len(sites)} energy sites. There are {len(duty['missed_dispatches'])} dispatches without a ready trainset. All matched cases below have service shortfalls under the selected hot-weather assumptions; none qualifies the declared service.

| Case (lower-solar duty) | Minimum SOC | Unserved traction kWh | Shortfall events |
| --- | ---: | ---: | ---: |
{comparison_rows}

[ERP planning drafts](erp-drafts.json) identify reusable machines and distinct front/shift crews, with purchase, commissioning, inspection, maintenance, competence and transfer gates. No live ERP purchase/allocation is approved by this package. Cash purchase, project allocation and residual value are distinct.

[Manifest](manifest.json) hashes every source and output and identifies the source revision and assumption register. Existing finance/proposal packages are retained comparators pending scope-matched adoption; this study is the current connected scenario, not an accepted replacement budget. Regenerate with `.venv/bin/python tools/automation/connected-build-study.py --city {slug}`; verify using `--check`.
''').encode()
    sources=[Path(__file__),city_dir/'design.toml',city_dir/f'{slug}.toml',city_dir/f'{slug}.corridor.geojson']
    sources += [ROOT/'lib/templates'/name for name in ('precast-logistics.json','accelerated-build.toml','stations.toml','accessibility.toml','rolling-stock.toml','energy-sites.toml','battery-profiles.json','precast-suppliers.json','civil-cost-calibration.toml','civil-cost-model.toml')]
    sources += sorted((ROOT/'crates/osr-bms/src').glob('*.rs'))
    sources += sorted((ROOT/'design/component-catalogue/src/osr_mech/civil').glob('*.py'))
    sources += sorted((ROOT/'design/component-catalogue/src/osr_mech/station').glob('*.py'))
    sources += [ROOT/'design/component-catalogue/src/osr_mech/cad.py',ROOT/'design/component-catalogue/src/osr_mech/common.py']
    sources += [ROOT/'design/component-catalogue/src/osr_mech'/name for name in ('station/layout.py','station/product_geometry.py','buildable_stations.py','battery_profiles.py','network_energy_duty.py')]
    sources += [ROOT/'design/component-catalogue/src/osr_mech/freecad_station_library.py',ROOT/'engineering/interchange/station_ifc.py',ROOT/'deployment/erpnext/apps/osr_erpnext/osr_erpnext/setup.py',ROOT/'deployment/erpnext/apps/osr_erpnext/osr_erpnext/construction_fleet.py',ROOT/'engineering/analysis/city_geometry.py',ROOT/'docs/rfcs/0034-connected-station-production-and-battery-model.md']
    cad_root=city_dir/'engineering/connected-build/cad'
    cad_index=cad_root/'station-library.index.json'
    native_cad=dict(status='not-generated')
    if cad_index.is_file():
        index=read(cad_index)
        native_cad=dict(status='current' if index['manifest_sha256']==hashlib.sha256(files['station-products.json']).hexdigest() and all(digest(ROOT/path)==sha for path,sha in index.get('geometry_sources_sha256',{}).items()) else 'stale',
                       manifest_sha256=index['manifest_sha256'],reopen_validated=index['passed'],
                       files_sha256={p.relative_to(city_dir/'engineering/connected-build').as_posix():digest(p) for p in sorted(cad_root.iterdir()) if p.suffix in ('.FCStd','.json')})
    manifest=dict(native_cad=native_cad,schema=1,source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        assumptions=config,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in sources},
        output_sha256={name:hashlib.sha256(data).hexdigest() for name,data in files.items()},
        current_connected_study=True,engineering_qualified=False,supplier_quotations=0,
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
