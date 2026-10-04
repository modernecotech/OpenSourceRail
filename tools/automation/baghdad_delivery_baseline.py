#!/usr/bin/env python3
"""Reconcile Baghdad's delivery scope without treating unverified prices as quotes."""
from __future__ import annotations
import argparse
from copy import deepcopy
import csv
import hashlib
import html
import json
import math
from pathlib import Path
import random
import statistics
import tomllib

ROOT = Path(__file__).resolve().parents[2]
CITY = ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
OUT = CITY/'engineering/delivery-baseline'
CONFIG = ROOT/'lib/templates/baghdad-delivery-baseline.toml'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text())

def trainset_reference_cost():
    return tomllib.loads((ROOT/'lib/templates/capex-costs.toml').read_text())['trainset_unit_usd']['metro-6car']

def clock_minutes(value):
    hour, minute = map(int, value.split(':'))
    return hour*60+minute

def windows(fleet):
    for window in fleet['schedule']:
        start, end = clock_minutes(window['from']), clock_minutes(window['to'])
        if end <= start:
            end += 1440
        yield start, end, window['headway_min']

def validate(config):
    for section in config.values():
        for key,value in section.items():
            if isinstance(value,(int,float)) and (not math.isfinite(value) or value<0):
                raise ValueError('Invalid nonnegative assumption: '+key)
    if not 0<config['depot']['workshop_availability']<=1:
        raise ValueError('Workshop availability outside (0,1]')
    for key in ('charger_efficiency','storage_charge_efficiency','storage_discharge_efficiency'):
        if not 0<config['energy'][key]<=1:
            raise ValueError('Invalid energy efficiency')
    for key in ('risk_shared_fraction',):
        if not 0<=config['model'][key]<=1:
            raise ValueError('Invalid shared risk fraction')
    w=config['workforce']
    if w['paid_hours_per_year']<=sum(w[k] for k in ('leave_hours','training_hours','sickness_hours','travel_handover_hours')):
        raise ValueError('No productive workforce hours')
    if not all(0<=w[k]<1 for k in ('recruitment_attrition_fraction',)):
        raise ValueError('Invalid recruitment attrition')
    if not all(0<w[k]<=1 for k in ('assessment_first_pass_fraction','assessment_repeat_pass_fraction')):
        raise ValueError('Invalid assessment pass rates')
    positive={'model':['iqd_per_usd_reference','risk_trials'],
        'depot':['positions_per_track','workshop_days_per_year','workshop_hours_per_day'],
        'workforce':['remote_assist_trains_per_post','station_team_stations_per_lead','customer_service_stations_per_post','trainer_learners_per_group'],
        'fleet':['opening_peak_headway_minutes','opening_offpeak_headway_minutes','opening_late_headway_minutes'],
        'rental_delivery':['inspection_closure_interval_months']}
    for section,keys in positive.items():
        for key in keys:
            if config[section][key]<=0:
                raise ValueError('Positive assumption required: '+key)
    for key in ('tenant_funded_fitout_fraction','tenant_rent_discount_fraction','concession_landlord_receipt_fraction','concession_landlord_opex_fraction'):
        if not 0<=config['rental_delivery'][key]<=1:
            raise ValueError('Invalid rental allocation: '+key)
    for key in ('storage_min_soc_fraction','storage_initial_soc_fraction','storage_annual_degradation','wheeling_loss_fraction'):
        if not 0<=config['energy'][key]<1:
            raise ValueError('Invalid energy fraction: '+key)
    if config['energy']['storage_initial_soc_fraction']<config['energy']['storage_min_soc_fraction']:
        raise ValueError('Initial storage below minimum SOC')

def depot_package(design, scenario, stabling, depot_scope, config):
    c=config['depot'];length=scenario['consist']['length_m']+10
    fleets={r['line']:r['trainset_count'] for r in design['fleets']}
    alternatives={}
    for variant in ('retained_declared_bays','workload_bays'):
        sites=[];items=[]
        for requirement in stabling['hybrid_allocation']['depot_requirements']:
            line=requirement['lines'][0];positions=requirement['stabling_positions_required']
            tracks=math.ceil(positions/c['positions_per_track'])
            bays=max(1,math.ceil(fleets[line]*c['workshop_bay_hours_per_train_year']/(c['workshop_days_per_year']*c['workshop_hours_per_day']*c['workshop_availability']))) if variant=='workload_bays' else requirement['workshop_bays']
            yard_area=positions*length*c['track_spacing_m']*c['access_land_multiplier']
            workshop_area=bays*length*c['workshop_width_m']
            site=dict(station=requirement['station'],line=line,stabling_positions=positions,
                storage_tracks=tracks,positions_per_track_maximum=c['positions_per_track'],
                storage_usable_track_m=positions*length,turnouts=tracks+2,workshop_bays=bays,
                declared_workshop_bays=requirement['workshop_bays'],yard_area_m2=yard_area,
                workshop_shell_m2=workshop_area,surveyed_land_area_m2=None,layout_accepted=False,
                storage_positions_are_workshop_bays=False,interline_transfer_assumed=False)
            site['heavy_maintenance_strategy']=dict(
                method='Line-local covered lifting, bogie exchange, wheel servicing and body overhaul',
                available_local_bays=bays,
                required_local_bays=math.ceil(fleets[line]*c['workshop_bay_hours_per_train_year']/(c['workshop_days_per_year']*c['workshop_hours_per_day']*c['workshop_availability'])),
                interline_train_transfer_available=False,
                road_transfer_scope='Removed bogies/components only; no intact train road movement assumed',
                mobile_tools_replace_covered_bays=False,
                additional_facility_capital_usd=None if bays==0 else 0,
                supplier_lift_and_wheel_method=None,accepted=False)
            sites.append(site)
            quantities=[('storage-track',positions*length,'m',c['track_usd_per_m'],'Running track/bed; excludes turnouts, site drainage and land'),
                ('turnouts',tracks+2,'each',c['turnout_usd'],'Fan plus two throat points; geometry/interlocking unqualified'),
                ('yard-drainage-access',yard_area,'m2',c['drainage_access_usd_per_m2'],'Drainage and access only; excludes land purchase and track'),
                ('workshop-shell',workshop_area,'m2',c['workshop_shell_usd_per_m2'],'Shell only; no process equipment'),
                ('workshop-equipment',bays,'bay',c['workshop_equipment_usd_per_bay'],'Draft isolation/lifting/inspection equipment allowance'),
                ('rescue-isolation',1,'site',c['isolation_rescue_usd_per_site'],'Line-local rescue interface; actual vehicle/route needs quotes'),
                ('battery-quarantine',1,'site',c['quarantine_usd_per_site'],'Separated quarantine allowance; fire design unaccepted'),
                ('inspection-pad',1,'site',c['inspection_pad_usd_per_site'],'Line-local inspection even where workshop bays are zero')]
            for key,quantity,unit,rate,inclusion in quantities:
                items.append(dict(id=requirement['station']+':'+key,site=requirement['station'],scope=key,
                    quantity=quantity,unit=unit,reference_rate_usd=rate,reference_cost_usd=quantity*rate,
                    inclusions=inclusion,price_date=None,quotation=None,rate_quality='editable-unquoted-allowance',
                    responsible_estimator_role='Infrastructure estimator and asset director',named_estimator=None))
        for depot in depot_scope['depots']:
            for key,quantity,rate,unit in [('depot-pv-equipment',depot['pv_nameplate_kw'],700,'kW'),('depot-storage-equipment',depot['storage_capacity_kwh'],75,'kWh')]:
                items.append(dict(id=depot['station']+':'+key,site=depot['station'],scope=key,quantity=quantity,
                    unit=unit,reference_rate_usd=rate,reference_cost_usd=quantity*rate,
                    inclusions='Full depot equipment quantity; installation/compound/renewal excluded',
                    price_date=None,quotation=None,rate_quality='existing-equipment-rate-not-installed-quote',
                    responsible_estimator_role='Energy estimator',named_estimator=None))
        gross=sum(r['reference_cost_usd'] for r in items)
        alternatives[variant]=dict(sites=sites,items=items,gross_reference_cost_usd=gross,
            existing_depot_allowance_usd=design['costs']['depots_usd'],
            incremental_after_full_depot_allowance_credit_usd=max(0,gross-design['costs']['depots_usd']),
            additional_cost_if_no_allowance_overlap_usd=gross,
            allowance_overlap_accepted=False,charging_allowance_overlap_accepted=False,
            unpriced=['land/title','utility relocation','geotechnical/foundations','site-specific chargers/feeders beyond existing site equipment',
                'power conversion/protection installation','throat/interlocking connection','road access approvals','drainage outfall','fire authority changes','tax/duties'],
            actual_layout_released=False,adopted=False)
    return dict(status='quantity-based-unquoted-alternatives',station_trainsets=stabling['hybrid_allocation']['station_trainsets'],
        depot_trainsets=stabling['hybrid_allocation']['depot_trainsets'],fleet_trainsets=sum(fleets.values()),
        original_allocation_passed=stabling['hybrid_allocation']['allocation_passed'],
        missing_morning_directions=stabling['hybrid_allocation']['missing_morning_directions'],
        alternatives=alternatives,station_storage_cost_included_elsewhere_unverified=True,
        physical_release=False)

def family_baseline(design,scenario,detail,factory,config):
    profile=detail['family_profile'];cars=profile['cars'];count=sum(r['trainset_count'] for r in design['fleets'])
    system=scenario['consist']['systems'];c=config['sixcar']
    components=[('carbody-structure',cars,'car',c['structure_kg_per_car'],420000,'New 18.5 m structure; strength/fatigue/fire; no LM3 structural release'),
        ('bogie-running-gear',2*cars,'bogie',c['bogie_running_gear_kg_per_car']/2,300000,'Axle/brake/suspension/load supplier freeze'),
        ('traction-controls',profile['traction_controller_count'],'controller',c['traction_kg_per_car']*cars/profile['traction_controller_count'],180000,'Motor/inverter thermal/EMC; 675 V interfaces'),
        ('battery-modules',cars,'225 kWh gross module',c['battery_kg_per_car'],270000,'1350 kWh gross/1080 usable; supplier thermal/fire/isolation evidence'),
        ('interior-doors-glazing',cars,'car kit',c['interior_doors_windows_kg_per_car'],240000,'Accessible doors, glazing, retention and egress'),
        ('thermal-roof-services',cars,'car kit',c['thermal_roof_services_kg_per_car'],90000,'50 C heat rejection; segregated cabin air/battery cooling'),
        ('trainline-couplers',1,'six-car system',c['trainline_couplers_kg_per_train'],70000,'Five inter-car interfaces; redundant trainline and common failure assessment'),
        ('assembly-qa-logistics',1,'consist',0,110000,'Embedded payroll, routine QA and logistics; not extra operating payroll')]
    rows=[]
    price=trainset_reference_cost();allocation_total=sum(part[4] for part in components)
    for key,quantity,unit,mass,cost,closure in components:
        cost=cost*price/allocation_total
        rows.append(dict(part_id='M6-'+key,quantity_per_consist=quantity,network_quantity=quantity*count,
            unit=unit,planning_mass_kg_each=mass,planning_mass_kg_per_consist=quantity*mass,
            cost_allocation_per_consist_usd=cost,rate_usd_per_unit=cost/quantity,
            quotation=None,supplier_part_number=None,mass_evidence=None,
            lm3_applicability='architecture reference only; six-car qualification required',
            lm3_credit_accepted=False,closure=closure,engineering_released=False))
    modelled=sum(r['planning_mass_kg_per_consist'] for r in rows);tare=profile['tare_mass_t']*1000
    route=[]
    for stage in factory['stages']:
        hours=stage['cycle_working_days']*stage['crew_per_cell']*8
        route.append(dict(package=stage['package'],work_center=stage['work_center'],cells=stage['cells'],
            reference_person_hours_per_consist=hours,network_person_hours=hours*count,
            reference_cycle_days=stage['cycle_working_days'],measured_cycle_days=None,
            rework_hours_included=False,labour_in_train_procurement=True,
            work_order=None,job_card=None,acceptance_evidence=None))
    interfaces=[dict(id='M6-I-'+str(i+1).zfill(2),interface=title,evidence=None,accepted=False) for i,title in enumerate([
        'wheel/rail and axle loads','coupler strength and five inter-car joints','braking propagation and evacuation',
        'redundant trainline and fault isolation','675 V battery/inverter/charger envelope','door/platform gap and interlocking',
        'HVAC/battery separation and 50 C duty','fire/smoke materials and egress','EMC/earthing and harness segregation',
        'first-article structural/load/thermal/braking/charging tests'])]
    qualification_weights=[.08,.10,.12,.10,.12,.06,.10,.10,.08,.14]
    qualification=[dict(interface_id=r['id'],work_package=r['interface'],
        reference_budget_usd=c['qualification_budget_usd']*weight,quotation=None,
        evidence=None,accepted=False,overlap_with_factory_allowance_accepted=False)
        for r,weight in zip(interfaces,qualification_weights)]
    return dict(family='metro-6car',configuration_revision='M6-A-DRAFT',trainsets=count,cars=cars,vehicle_modules=cars*count,
        controlled_profile=profile,bom=rows,labour_routes=route,interfaces=interfaces,qualification_work_packages=qualification,
        doors_per_consist=system['door_cassettes_per_car']*cars,windows_per_consist=system['window_cassettes_per_car']*cars,
        planning_mass_subtotal_kg=modelled,controlled_tare_kg=tare,unallocated_mass_reserve_kg=tare-modelled,
        axle_count=4*cars,tare_axle_load_average_t=tare/(4*cars)/1000,
        full_load_axle_load_average_t=(tare+profile['crush_capacity']*75)/(4*cars)/1000,
        axle_load_distribution_evidence=None,cost_allocations_reconcile_usd=sum(r['cost_allocation_per_consist_usd'] for r in rows),
        qualification_reference_budget_usd=c['qualification_budget_usd'],
        factory_design_training_qualification_allowance_usd=factory['cost_allowances_usd']['design_training_qualification'],
        qualification_incremental_cost_usd=None,qualification_allowance_overlap_accepted=False,
        production_bom=None,first_article_accepted=False,engineering_release=False)

def hourly_duty(design,scenario,annual_energy):
    lengths={r['name']:r['length_m']/1000 for r in design['lines']}
    weights=[0.]*24
    for fleet in scenario['fleets']:
        for start,end,headway in windows(fleet):
            for minute in range(start,end):
                weights[(minute//60)%24]+=2*lengths[fleet['line']]/headway
    total=sum(weights)
    return [annual_energy/365*value/total for value in weights]

def dispatch_energy(generation,load, *, storage_kwh, power_kw, grid_kw, config, capacity_fraction=1.):
    """Hourly bus-energy conservation with usable SoC and connection limits."""
    if len(generation)!=len(load) or any(not math.isfinite(v) or v<0 for v in [*generation,*load,storage_kwh,power_kw,grid_kw,capacity_fraction]):
        raise ValueError('Invalid hourly energy input')
    if not 0<config['storage_charge_efficiency']<=1 or not 0<config['storage_discharge_efficiency']<=1 or not 0<=config['storage_min_soc_fraction']<=config['storage_initial_soc_fraction']<=1:
        raise ValueError('Invalid storage conversion or SoC bounds')
    capacity=storage_kwh*capacity_fraction;floor=capacity*config['storage_min_soc_fraction']
    soc=capacity*config['storage_initial_soc_fraction'];rows=[]
    ce=config['storage_charge_efficiency'];de=config['storage_discharge_efficiency']
    for index,(pv,demand) in enumerate(zip(generation,load)):
        opening=soc;direct=min(pv,demand);surplus=pv-direct
        charge=min(surplus,power_kw,max(0,(capacity-soc)/ce));soc+=charge*ce
        remaining=demand-direct;discharge=min(remaining,power_kw,max(0,(soc-floor)*de));soc-=discharge/de
        remaining-=discharge;imports=min(remaining,grid_kw);unserved=remaining-imports;curtailed=surplus-charge
        loss=charge*(1-ce)+discharge*(1/de-1)
        residual=pv+imports+opening-demand+unserved-curtailed-loss-soc
        if abs(residual)>1e-6:raise ValueError('Hourly energy balance fails')
        rows.append(dict(hour=index,generation_kwh=pv,demand_kwh=demand,opening_soc_kwh=opening,
            direct_kwh=direct,storage_charge_kwh=charge,storage_discharge_kwh=discharge,
            grid_import_kwh=imports,unserved_kwh=unserved,curtailed_kwh=curtailed,
            conversion_loss_kwh=loss,closing_soc_kwh=soc,energy_residual_kwh=residual))
    return rows

def chronological_energy(design,scenario,finance,config):
    c=config['energy'];costs=tomllib.loads((ROOT/'lib/templates/capex-costs.toml').read_text())
    rates=costs['solar_power_plant'];solar_rate=rates['utility_pv_usd_per_kw']+rates['interconnection_usd_per_kw']
    plant_kw=finance['capex_usd']['timetable_sized_dedicated_solar']/solar_rate
    onsite_kw=sum(r['pv_nameplate_kw'] for r in scenario['sites'])
    storage=sum(r['storage_capacity_kwh'] for r in scenario['sites'])
    power=min(sum(r['storage_max_charge_kw'] for r in scenario['sites']),sum(r['storage_max_discharge_kw'] for r in scenario['sites']))
    grid=sum(r['grid_import_kw'] for r in scenario['sites'])
    demand=finance['operations_basis']['annual_train_km_including_non_revenue']*scenario['consist']['car_count']*finance['operations_basis']['energy_kwh_per_car_km_hot_climate_planning']
    daily=hourly_duty(design,scenario,demand)
    solar_hours=[max(0,math.sin(math.pi*(hour+.5-6)/12)) for hour in range(24)]
    sun=scenario['climate']['peak_sun_hours'];cases={}
    for weather,factor,age in [('synthetic_reference',1.,0),('synthetic_poor_year',c['poor_year_yield_factor'],0),('synthetic_aged_year_10',1.,10)]:
        raw=[];loads=[]
        for day in range(365):
            season=1+.25*math.sin(2*math.pi*(day-80)/365)
            poor=c['poor_spell_yield_factor'] if 5<=day<5+c['poor_spell_days'] else 1.
            for hour in range(24):
                raw.append((plant_kw+onsite_kw)*sun*season*factor*poor*solar_hours[hour]/sum(solar_hours)*c['pv_performance_ratio']*(1-c['wheeling_loss_fraction']))
                loads.append(daily[hour]/c['charger_efficiency'])
        for arrangement in ('owned_solar','contracted_solar','hybrid_storage'):
            extra=c['hybrid_additional_storage_kwh'] if arrangement=='hybrid_storage' else 0
            extra_power=c['hybrid_additional_power_kw'] if extra else 0
            rows=dispatch_energy(raw,loads,storage_kwh=storage+extra,power_kw=power+extra_power,grid_kw=grid,
                config=c,capacity_fraction=(1-c['storage_annual_degradation'])**age)
            imports=sum(r['grid_import_kwh'] for r in rows);generation=sum(raw)
            delivered=sum(r['direct_kwh']+r['storage_discharge_kwh'] for r in rows)
            purchases=imports*c['import_purchase_usd_per_kwh']
            wheeling=generation*c['wheeling_usd_per_kwh'];balancing=sum(loads)*c['balancing_usd_per_kwh'];connection=grid*c['connection_usd_per_kw_year']
            ppa=generation*c['contracted_solar_usd_per_kwh'] if arrangement=='contracted_solar' else 0.
            own_maintenance=0. if arrangement=='contracted_solar' else finance['annual_opex_usd']['components']['solar_plant_maintenance']
            capex=0. if arrangement=='contracted_solar' else finance['capex_usd']['timetable_sized_dedicated_solar']
            extra_cost=extra*c['storage_usd_per_kwh']+extra_power*c['storage_power_usd_per_kw']
            annual=purchases+wheeling+balancing+connection+ppa+own_maintenance
            cases[weather+':'+arrangement]=dict(weather_basis=weather,arrangement=arrangement,hourly=rows,
                traction_demand_kwh=demand,charging_bus_demand_kwh=sum(loads),generation_delivered_to_bus_kwh=generation,
                solar_used_kwh=delivered,grid_import_kwh=imports,curtailment_kwh=sum(r['curtailed_kwh'] for r in rows),
                unserved_kwh=sum(r['unserved_kwh'] for r in rows),storage_losses_kwh=sum(r['conversion_loss_kwh'] for r in rows),
                generation_conversion_and_wheeling_loss_kwh=generation/(c['pv_performance_ratio']*(1-c['wheeling_loss_fraction']))-generation,
                electricity_purchase_usd=purchases,wheeling_usd=wheeling,balancing_usd=balancing,connection_usd=connection,
                solar_ppa_usd=ppa,owned_solar_maintenance_usd=own_maintenance,annual_energy_cost_usd=annual,
                annual_opex_increment_over_existing_energy_usd=annual-finance['annual_opex_usd']['components']['solar_plant_maintenance'],
                dedicated_solar_capex_usd=capex,additional_hybrid_equipment_usd=extra_cost,
                twenty_year_resource_pv_usd=capex+extra_cost+sum(annual*1.05**year/1.134**(year+1) for year in range(20)),
                comparison_price_escalation_fraction=.05,comparison_discount_fraction=.134,
                replacements_and_site_installation_priced=False,connection_contract=None,service_delivered=sum(r['unserved_kwh'] for r in rows)<.01,
                service_accepted=False,bankable_annual_purchase_forecast=False)
    return dict(status='synthetic-hourly-screen-not-site-dispatch',plant_kw=plant_kw,onsite_pv_kw=onsite_kw,
        existing_storage_kwh=storage,existing_storage_power_kw=power,aggregate_import_limit_kw=grid,
        annual_traction_demand_kwh=demand,ten_percent_purchase_sensitivity_usd=demand*.10*.10,
        initial_storage_energy_not_free=True,aggregate_pooling_unestablished=True,
        limitations=['Synthetic representative reference, poor and aged years; no measured hourly weather or OD duty',
            'Aggregate pooling is optimistic; per-charger network/arrival queues and interconnection need physical replay',
            'Energy balance includes charger loss; thermal auxiliary addition beyond the hot-climate intensity requires measurements',
            'No export revenue; curtailed energy is not sold; PPA pays all generated energy, including curtailment',
            'Extra hybrid equipment, installation, replacements and PPA contract costs are not a complete lifecycle quotation',
            'Unserved energy means the assumed service is unmet; no reduced-service case earns unchanged fares'],cases=cases)

def phase_fleet(design,scenario,risk,config):
    price=trainset_reference_cost()
    c=config['fleet'];profiles={r['line']:r for r in design['fleets']};lengths={r['name']:r['length_m']/1000 for r in design['lines']}
    openings={p['line']:p['opening_month'] for p in risk['cases']['calendar_baseline']['phases']};rows=[]
    for fleet in scenario['fleets']:
        current=profiles[fleet['line']];minimum=min(w['headway_min'] for w in fleet['schedule'])
        cycle=current['peak_count']*minimum
        peak=math.ceil(cycle/max(minimum,c['opening_peak_headway_minutes']));spares=math.ceil(peak*c['spare_fraction']);new=peak+spares+current['cold_reserve_count']
        base_trips=new_trips=0.
        for start,end,headway in windows(fleet):
            base_trips+=2*(end-start)/headway
            for minute in range(start,end):
                civil_minute=minute%1440
                opening=c['opening_peak_headway_minutes'] if 420<=civil_minute<540 or 900<=civil_minute<1020 else (c['opening_late_headway_minutes'] if civil_minute>=1410 or civil_minute<330 else c['opening_offpeak_headway_minutes'])
                opening=max(headway,opening) # Phasing never increases an already slower service.
                new_trips+=2/opening
        rows.append(dict(line=fleet['line'],route_km=lengths[fleet['line']],conditional_full_line_opening_month=openings[fleet['line']],
            baseline_peak_count=current['peak_count'],baseline_trainsets=current['trainset_count'],
            opening_peak_count=peak,opening_spares=spares,opening_cold_reserves=current['cold_reserve_count'],opening_trainsets=new,
            deferred_trainsets=max(0,current['trainset_count']-new),opening_train_capital_usd=new*price,
            additional_trainsets=max(0,new-current['trainset_count']),
            deferred_train_capital_usd=max(0,current['trainset_count']-new)*price,
            additional_train_capital_usd=max(0,new-current['trainset_count'])*price,
            inferred_baseline_cycle_minutes=cycle,cycle_basis='Peak-fleet/headway inference; conflict-aware cycle and turnbacks unaccepted',
            baseline_daily_train_km=base_trips*lengths[fleet['line']],opening_daily_train_km=new_trips*lengths[fleet['line']],
            opening_daily_directional_capacity=round(new_trips*scenario['consist']['passenger_capacity']),
            expansion_load_trigger=c['expansion_load_trigger'],observation_days=c['expansion_observation_days'],
            od_demand=None,access_population=None,commercial_corridor_rank=None,adopted=False))
    return dict(status='service-supply-comparison-demand-unverified',lines=rows,
        baseline_fleet=sum(r['baseline_trainsets'] for r in rows),opening_fleet=sum(r['opening_trainsets'] for r in rows),
        deferred_fleet=sum(r['deferred_trainsets'] for r in rows),deferred_train_capital_usd=sum(r['deferred_train_capital_usd'] for r in rows),
        additional_fleet=sum(r['additional_trainsets'] for r in rows),additional_train_capital_usd=sum(r['additional_train_capital_usd'] for r in rows),
        first_corridor_selected=False,unchanged_fares_claimed=False,factory_resize_accepted=False,
        required_demand_inputs=['OD by time and corridor','paid boarding vs transfers','walk/feeder access and population overlap',
            'fare affordability and elasticity','measured cycle/turnback and junction occupancy','standalone OPEX and first-phase civil/utility dependencies'],
        limitations=['Fleet saving is deferred procurement, not cancellation or a proven investment saving',
            'Factory capacity and opening times cannot be improved without re-running finite resources and physical acceptance',
            'First line by schedule is not necessarily the best commercial corridor; no unsupported ranking or fare revenue'])

def workforce(design,scenario,finance,risk,factory,config):
    c=config['workforce'];roles=tomllib.loads((ROOT/'lib/templates/workforce.toml').read_text())['role']
    stations=len(design['stations']);lines=len(design['lines']);fleet=sum(r['trainset_count'] for r in design['fleets'])
    peak=sum(r['peak_count'] for r in design['fleets']);km=sum(r['length_m'] for r in design['lines'])/1000
    service=finance['workforce']['service_hours_per_day'];days=c['service_days'];post_hours=service*days
    productive=c['paid_hours_per_year']-sum(c[k] for k in ('leave_hours','training_hours','sickness_hours','travel_handover_hours'))
    # Minimum simultaneous posts are separate from annual task-hour workloads.
    demands={
        'occ-lead':(1,post_hours,'One watch lead during every service hour'),
        'dispatcher':(lines,lines*post_hours,'One dispatcher per line during service'),
        'remote-assist':(math.ceil(peak/c['remote_assist_trains_per_post']),math.ceil(peak/c['remote_assist_trains_per_post'])*post_hours,'Peak fleet / explicit concurrent remote-assist ratio'),
        'station-lead':(math.ceil(stations/c['station_team_stations_per_lead']),math.ceil(stations/c['station_team_stations_per_lead'])*post_hours,'Mobile team supervision; site travel allowance separate'),
        'platform-assistance':(stations,stations*post_hours,'One assistance post per station during service; crowding may require more'),
        'customer-service':(math.ceil(stations/c['customer_service_stations_per_post']),math.ceil(stations/c['customer_service_stations_per_post'])*post_hours,'Shared service posts; measure access/travel and queue demand'),
        'station-cleaning':(0,stations*c['station_cleaning_person_hours_per_day']*days,'Measured station task hours required; canopy is not cleaning area'),
        'workshop-lead':(lines,lines*16*260,'Line-local workshop supervision, 16 hours x 260 days'),
        'fleet-mechanical':(0,fleet*c['train_mechanical_person_hours_per_year'],'Annual task-hour placeholder; revise from task/asset duty'),
        'fleet-electrical':(0,fleet*c['train_electrical_person_hours_per_year'],'Battery/HV/diagnostic task-hour placeholder'),
        'fleet-finish-cleaning':(0,fleet*c['train_cleaning_person_hours_per_day']*days,'Daily fleet cleaning including setup; product/scope trials pending'),
        'infrastructure-lead':(lines,lines*8*260,'One infrastructure supervisor per line, working-day cover'),
        'civil-track':(0,km*c['civil_person_hours_per_route_km_year'],'Civil/track inspection person-hours; access windows unaccepted'),
        'solar-storage':(0,len(scenario['sites'])*c['energy_person_hours_per_site_year'],'Meter/isolation/PV/battery tasks; solar-plant workload additional unknown'),
        'wayside-comms':(0,stations*c['wayside_person_hours_per_station_year'],'Wayside/control/charging communications task-hours'),
        'city-director':(1,productive,'One accountable leadership role, emergency relief still required'),
        'chief-engineer':(1,productive,'One design authority role, specialist checking separately required'),
        'quality-safety':(0,km*40+fleet*20,'Independent checking/incident task hours; not production-owned release'),
        'training':(0,(stations+fleet)*40,'Recurring assessor/training task-hour proxy; induction programme separately costed'),
        'procurement-stores':(0,(stations+fleet)*30,'Stores/procurement transaction hours; production stores paid in train/factory scope'),
        'finance-people':(0,(stations+fleet)*20,'Payroll/people/finance administration task-hour proxy')}
    rows=[]
    for role in roles:
        posts,hours,basis=demands[role['id']];fte=math.ceil(hours/productive)
        grade='frontline' if role['id'] in {'platform-assistance','customer-service','station-cleaning','fleet-finish-cleaning'} else ('lead' if 'lead' in role['id'] or role['id'] in {'city-director','chief-engineer','quality-safety'} else 'technical')
        wage=c[grade+'_monthly_iqd'];cost=fte*wage*12*(1+c['employer_cost_fraction']+c['overtime_allowance_fraction'])
        rows.append(dict(role_id=role['id'],title=role['title'],department=role['group'],unit=role['id'],reports_to=role['reports_to'],
            minimum_concurrent_posts=posts,annual_workload_person_hours=hours,annual_productive_hours_per_fte=productive,
            required_fte=fte,grade=grade,monthly_base_iqd=wage,annual_loaded_payroll_iqd=cost,
            quantity_basis=basis,workload_measured=False,pay_terms_accepted=False,named_manager=None,
            baseline_group_fte=finance['workforce']['groups_fte'][role['group']],native_cost_centre=None))
    phases=risk['cases']['calendar_baseline']['phases']
    station_lines={r['id']:r['line'] for r in design['stations']}
    line_fleets={r['line']:r for r in design['fleets']}
    central={'occ-lead','city-director','chief-engineer','quality-safety','training','procurement-stores','finance-people'}
    allocations={};units=[]
    for role in rows:
        weights={}
        for phase in phases:
            line=phase['line']
            if role['role_id'] in central:weight=int(phase['opening_month']==min(p['opening_month'] for p in phases))
            elif role['role_id'] in {'dispatcher','workshop-lead','infrastructure-lead'}:weight=1
            elif role['role_id']=='remote-assist':weight=math.ceil(line_fleets[line]['peak_count']/c['remote_assist_trains_per_post'])
            elif role['department'] in {'fleet_maintenance'}:weight=line_fleets[line]['trainset_count']
            elif role['role_id']=='civil-track':weight=next(r['length_m'] for r in design['lines'] if r['name']==line)
            elif role['role_id']=='solar-storage':weight=sum(station_lines[s['station']]==line for s in scenario['sites'])
            else:weight=sum(s['line']==line for s in design['stations'])
            weights[line]=weight
        allocations[role['role_id']]={}
        for line,weight in weights.items():
            hours=role['annual_workload_person_hours']*weight/sum(weights.values())
            target=math.ceil(hours/productive) if weight else 0
            allocations[role['role_id']][line]=target
            if target:units.append(dict(department=role['department'],unit=role['role_id']+':'+line,line=line,
                annual_workload_person_hours=hours,required_fte=target,accountable_manager=None,weekly_deliverable='Accepted task/asset output and handback',
                permits_accepted=False,roster_accepted=False,asset_backlog=None))
        role['required_fte']=sum(allocations[role['role_id']].values())
        role['annual_loaded_payroll_iqd']=role['required_fte']*role['monthly_base_iqd']*12*(1+c['employer_cost_fraction']+c['overtime_allowance_fraction'])
    cohorts=[]
    lead=sum(c[k] for k in ('selection_months','joining_months','training_months','assessment_months','repeat_assessment_months','supervised_experience_months'))
    pass_fraction=c['assessment_first_pass_fraction']+(1-c['assessment_first_pass_fraction'])*c['assessment_repeat_pass_fraction']
    for index,phase in enumerate(sorted(phases,key=lambda p:p['opening_month'])):
        for role in rows:
            target=allocations[role['role_id']][phase['line']]
            if not target:continue
            offers=math.ceil(target/((1-c['recruitment_attrition_fraction'])*pass_fraction))
            request=phase['opening_month']-lead;selected=request+c['selection_months'];joined=selected+c['joining_months'];trained=joined+c['training_months'];assessed=trained+c['assessment_months'];reassessed=assessed+c['repeat_assessment_months'];authorised=reassessed+c['supervised_experience_months']
            expected_joined=offers*(1-c['recruitment_attrition_fraction'])
            wage=role['monthly_base_iqd']*(1+c['employer_cost_fraction']+c['overtime_allowance_fraction'])
            training_pay=expected_joined*wage*(c['training_months']+c['assessment_months']+c['repeat_assessment_months']+c['supervised_experience_months'])
            groups=math.ceil(expected_joined/c['trainer_learners_per_group'])
            trainer_cost=groups*(c['induction_training_hours']+c['practical_training_hours'])*c['trainer_hourly_iqd']+expected_joined*(1+(1-c['assessment_first_pass_fraction']))*c['assessment_hours']*c['trainer_hourly_iqd']
            cohorts.append(dict(line=phase['line'],role_id=role['role_id'],target_authorised_staff=target,
                requisition_month=request,selection_complete_month=selected,join_month=joined,training_complete_month=trained,
                first_assessment_month=assessed,repeated_assessment_month=reassessed,supervised_experience_complete_month=authorised,
                authorised_available_month=authorised,required_line_opening_month=phase['opening_month'],offers_required=offers,
                expected_joined=expected_joined,expected_authorised=expected_joined*pass_fraction,
                paid_preopening_training_iqd=training_pay,trainer_assessor_iqd=trainer_cost,
                additional_commissioning_payroll_iqd=0.,commissioning_scope='Operating supervised trainees already paid above; additional specialists separate',
                recruitment_evidence=None,assessment_evidence=None,appointment=None,available=False))
    # Real pilot demand; identities and authorisations must be supplied locally.
    roster=[]
    for day in range(7):
        for start,duration in [(5.5,8),(13.5,8),(21.5,4.5)]:
            roster.append(dict(day=day,start_hour=start,end_hour=start+duration,paid_duration_hours=duration,
                department='OCC',unit='first-corridor-watch',role_id='occ-lead',location='Baghdad OCC',
                native_employee=None,worker_id=None,supervisor=None,eligible=False,status='unfilled',
                method_revision='pilot-rulebook-pending',access=None,permit=None,tools=None,materials=None,
                verifier=None,accepted_output=None,blocked_reason='No appointed, assessed and task-authorised worker'))
    training=[]
    curricula=[('IND','Common induction','Report hazards; follow access, emergency and revision controls','Arabic rulebook and reporting exercises'),
        ('OCC','OCC and incident response','Demonstrate normal/degraded/emergency decisions','Dispatcher simulator and independent observation'),
        ('STA','Stations and accessibility','Demonstrate boarding assistance, crowding and evacuation','Accessible mock platform and observed evacuation'),
        ('FLT','Fleet maintenance','Isolate, inspect, diagnose and repair controlled equipment','Six-car training rig and isolation/measurement tools'),
        ('CIV','Civil and energy','Execute permitted inspection and electrical/track-access work','Track access, drainage, electrical and fall-protection rigs'),
        ('FAC','Factory production','Execute revision-controlled traveller with traceable measurements','Work Order/Job Card, gauges, process samples'),
        ('SUP','Supervision and assessment','Allocate eligible staff; verify handover; assess and escalate','Roster exercises, independent assessment and defect handback')]
    for key,title,outcome,equipment in curricula:
        training.append(dict(module_id='BAG-TRN-'+key,title=title,prerequisites=[] if key=='IND' else ['BAG-TRN-IND'],
            controlled_lesson_revision='A-DRAFT',outcome=outcome,equipment=equipment,
            exercises=['Normal task to controlled method','Degraded/unsafe input and stop/escalate','Document evidence and handback'],
            assessment_criteria=['All critical steps observed','No unsafe action','Correct isolation/revision/evidence','Independent assessor records outcome'],
            assessor_requirements='Current scoped practical competence and appointed assessment authority; independent where required',
            retraining_triggers=['method/asset change','expiry','suspension','failed observation','skill fade','incident learning'],
            practical_hours=c['practical_training_hours'] if key!='IND' else c['induction_training_hours'],
            arabic_material_status='draft-glossary-only-native-review-required',attendance_is_competence=False,
            competence_is_task_authorisation=False,training_program=None,training_event=None,training_result=None,accepted=False))
    annual=sum(r['annual_loaded_payroll_iqd'] for r in rows)
    commissioning=[dict(line=p['line'],temporary_specialist_posts=c['commissioning_additional_specialist_posts_per_line'],
        start_month=p['opening_month']-c['commissioning_months'],end_month=p['opening_month'],
        reference_payroll_iqd=c['commissioning_additional_specialist_posts_per_line']*c['lead_monthly_iqd']*(1+c['employer_cost_fraction']+c['overtime_allowance_fraction'])*c['commissioning_months'],
        separate_from_operating_trainees=True,actual_appointments=None,pay_terms_accepted=False) for p in phases]
    return dict(status='workload-derived-unmeasured-establishment',roles=rows,units=units,recruitment_cohorts=cohorts,pilot_roster=roster,
        curricula=training,arabic_glossary=[dict(english=en,arabic=ar,accepted=False) for en,ar in [
            ('competence','الكفاءة'),('task authorisation','التصريح بأداء المهمة'),('isolation','العزل'),('handover','التسليم'),
            ('hazard','الخطر'),('independent verification','التحقق المستقل'),('permit to work','تصريح العمل')]],
        current_budget_fte=finance['workforce']['total_fte'],current_labour_usd=finance['workforce']['annual_labour_usd'],
        current_average_monthly_allowance_usd=finance['workforce']['annual_labour_usd']/finance['workforce']['total_fte']/12,
        reference_required_fte=sum(r['required_fte'] for r in rows),reference_annual_loaded_payroll_iqd=annual,
        reference_annual_loaded_payroll_usd=annual/config['model']['iqd_per_usd_reference'],reference_payroll_delta_usd=annual/config['model']['iqd_per_usd_reference']-finance['workforce']['annual_labour_usd'],
        productive_hours_per_fte=productive,
        training_recruitment_cash_iqd=sum(r['paid_preopening_training_iqd']+r['trainer_assessor_iqd'] for r in cohorts),
        temporary_commissioning_payroll_iqd=sum(r['reference_payroll_iqd'] for r in commissioning),temporary_commissioning_cohorts=commissioning,
        preopening_cost_in_existing_epc_unverified=True,unpriced=['hiring agency/checks','training rigs/facilities','PPE','employment taxes/duties beyond placeholder employer cost','construction crew counts','solar plant specialist hours'],
        factory_direct_positions_per_staffed_shift=factory['direct_production_crew_fte'],
        factory_payroll_in_train_procurement=True,factory_payroll_added_to_operating_payroll=False,
        construction_staff_separate=True,commissioning_staff_separate=True,named_workers=0,roster_released=False,
        sources=[{'title':'Frappe HR staffing plan','url':'https://docs.frappe.io/hr/staffing-plan'},
            {'title':'ORR competence management reference, not Iraqi approval','url':'https://www.orr.gov.uk/guide-rogs/7-managing-safety-critical-work'}])

def scope_register(design,finance,programme,depots,family,people,config):
    buckets=finance['capex_usd']['procurement_origin_buckets'];rows=[]
    quantities={'civil':sum(r['length_m'] for r in design['lines'])/1000,'stations':len(design['stations']),
        'depots':len(design['depots']),'rolling_stock':sum(r['trainset_count'] for r in design['fleets']),
        'solar_plant':finance['capex_usd']['timetable_sized_dedicated_solar']/sum(tomllib.loads((ROOT/'lib/templates/capex-costs.toml').read_text())['solar_power_plant'][k] for k in ('utility_pv_usd_per_kw','interconnection_usd_per_kw')),
        'signalling':sum(r['length_m'] for r in design['lines'])/1000,'charging_microgrid':1,'epc_overhead':1}
    for bucket in buckets:
        key=bucket['bucket'];quantity=quantities[key]
        rows.append(dict(wbs='BASE-'+key,scope=key,quantity=quantity,unit={'civil':'route-km','stations':'station','rolling_stock':'six-car consist','solar_plant':'kW','signalling':'route-km','depots':'declared depot'}.get(key,'allowance'),
            reference_rate_usd=bucket['total_usd']/quantity,base_estimate_usd=bucket['total_usd'],price_date=None,
            payment_currency='USD import / IQD local allocation; actual contract pending',source='engineering/finance/summary.json',
            source_quality='category-planning-estimate',rate_basis='implied blended reconciliation rate, not a quantity-survey quote',
            imported_fraction=bucket['imported_share'],origin_evidence=None,responsible_estimator_role='Finance estimator and relevant design authority',
            named_estimator=None,inclusions='Existing category allowance; itemised inclusions require signed estimator reconciliation',
            exclusions='Unverified additional scope recorded separately',quotation=None,uncertainty='uncalibrated',estimate_accepted=False))
    for key,value in [('factory-direct',programme['factory']['cost_usd']),('factory-epc',programme['factory']['epc_usd'])]:
        rows.append(dict(wbs='BASE-'+key,scope=key,quantity=1,unit='plant',reference_rate_usd=value,base_estimate_usd=value,
            price_date=None,payment_currency='IQD with qualified import invoices in USD',source='finance/baghdad-programme.json',
            source_quality='factory-sizing-allowance',rate_basis='reconciled existing allowance',imported_fraction=None,origin_evidence=None,
            responsible_estimator_role='Manufacturing estimator',named_estimator=None,inclusions='Buildings, equipment, design/training/qualification and existing contingency; EPC separate',
            exclusions='Supplier/first-article closure',quotation=None,uncertainty='uncalibrated',estimate_accepted=False))
    missing=[('land-rights','Survey/title and actual parcel/lease/easement cost','Infrastructure and commercial'),
        ('utility-diversion','Surveyed utility conflict schedule and relocation agreements','Infrastructure'),
        ('tax-duties','Actual invoice tax/duty and exemptions review','Finance and Iraqi counsel'),
        ('owner-costs','Owner team, audit, insurance and administration outside EPC','Finance'),
        ('preopening-people','Training/recruitment/commissioning payroll and overlap with EPC','People and finance'),
        ('product-qualification','Six-car first article and common-module applicability; overlap with factory 20m','Manufacturing and safety'),
        ('installed-control','Exact pilot hardware, harness, power, thermal, installation and HIL costs','Digital and safety'),
        ('initial-spares','Priced initial spares and warranty allocation distinct from renewal reserve','Asset and commercial'),
        ('working-capital','Initial stores, prepaid insurance and operating/DSRA capital timing','Finance'),
        ('civil-station-investigation','Corridor geotechnics, foundations, drainage, access, evacuation and temporary works','Chief engineer'),
        ('maintenance-renewals','Task/person-hour/spare/interval schedule; reconcile battery and civil envelopes','Asset'),
        ('cyber-deployment','Site identity, secrets, signed updates, recovery and incident ownership','Digital')]
    for key,closure,owner in missing:
        rows.append(dict(wbs='GAP-'+key,scope=key,quantity=None,unit=None,reference_rate_usd=None,base_estimate_usd=None,
            price_date=None,payment_currency=None,source='attached review reconciled against current scope',source_quality='unpriced-scope-gap',
            rate_basis=None,imported_fraction=None,origin_evidence=None,responsible_estimator_role=owner,named_estimator=None,
            inclusions=closure,exclusions=None,quotation=None,uncertainty='unbounded-unpriced',estimate_accepted=False))
    base=sum(r['base_estimate_usd'] or 0 for r in rows)
    if abs(base-programme['total_capex_usd'])>.02:raise ValueError('Published base estimate does not reconcile')
    alternatives={}
    for name,depot in depots['alternatives'].items():
        alternatives[name]=dict(base_programme_usd=base,depot_allowance_removed_once_usd=design['costs']['depots_usd'],
            depot_gross_reference_usd=depot['gross_reference_cost_usd'],
            provisional_reference_total_if_replacement_usd=base-design['costs']['depots_usd']+depot['gross_reference_cost_usd'],
            overlap_status='Depot replacement illustration; charging/PV/EPC inclusions unresolved',
            unpriced_scope_count=len(missing)+len(depot['unpriced']),complete_delivery_budget=False,adopted=False)
    obligations=['Design and coordination','Construction supervision','Survey and technical checking','Document/configuration control',
        'Programme controls and procurement','Commissioning and handback','Owner insurance/audit interface']
    epc=[dict(obligation=title,current_epc_envelope_usd=design['costs']['epc_overhead_usd'],allocated_cost_usd=None,
        inclusion_accepted=False,contract_deliverable=None,named_estimator=None) for title in obligations]
    return dict(status='base-estimate-plus-explicit-scope-gaps',base_programme_usd=base,rows=rows,
        city_subtotal_usd=finance['capex_usd']['reconciled_project_total'],factory_with_epc_usd=programme['factory']['cost_usd']+programme['factory']['epc_usd'],
        cost_price_date_unknown=True,complete_delivery_budget=False,unpriced_scope_count=len(missing),
        alternatives=alternatives,epc_obligations=epc,
        known_embedded_allowances=dict(factory_contingency_usd=read(CITY/'engineering/factory/summary.json')['cost_allowances_usd']['contingency'],
            factory_design_training_qualification_usd=family['factory_design_training_qualification_allowance_usd'],
            train_assembly_qa_logistics_per_consist_usd=110000),
        cost_risk_is_not_added_twice=True,government_capital_scope_unchanged=True)

def correlated_risk(scope,config):
    c=config['model'];rng=random.Random(c['risk_seed']);rows=[]
    # Shared quantile creates correlated cost and delay without pretending to
    # calibrate construction risk from unavailable surveys or contract history.
    def triangle(u,low,mode,high):
        cut=(mode-low)/(high-low)
        return low+math.sqrt(u*(high-low)*(mode-low)) if u<cut else high-math.sqrt((1-u)*(high-low)*(high-mode))
    for trial in range(c['risk_trials']):
        shared=rng.random();delay=triangle(shared,c['risk_delay_low_months'],c['risk_delay_mode_months'],c['risk_delay_high_months'])
        total=0.
        for row in scope['rows']:
            if row['base_estimate_usd'] is None:continue
            u=shared if rng.random()<c['risk_shared_fraction'] else rng.random()
            factor=triangle(u,c['risk_cost_low'],c['risk_cost_mode'],c['risk_cost_high'])
            # Factory's declared contingency and all existing allowances stay
            # embedded; this is a stress of the base, not another cost item.
            total+=row['base_estimate_usd']*factor*(1+c['construction_inflation'])**(delay/12)
        rows.append(dict(trial=trial,delay_months=delay,stressed_known_base_usd=total))
    ordered=sorted(r['stressed_known_base_usd'] for r in rows)
    return dict(status='uncalibrated-correlated-sensitivity',seed=c['risk_seed'],trials=rows,
        shared_risk_fraction=c['risk_shared_fraction'],p50_known_scope_usd=statistics.median(ordered),
        p80_known_scope_usd=ordered[math.ceil(.8*len(ordered))-1],
        unpriced_scope_included=False,approved_contingency_usd=None,probability_based_delivery_budget_accepted=False,
        source='https://www.gao.gov/products/gao-20-195g',
        limitations=['Illustrative distribution and dependence; no calibrated event probabilities','Unpriced scope is excluded, not zero cost',
            'Stress includes declared factory contingency; do not add this stress output to the base or depot alternative',
            'Escalation is a whole-known-budget delay sensitivity, not an invoice-timing/financing forecast'])

def table(headers,rows):
    clean=lambda value:str(value).replace('|','/').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |',
        *['| '+' | '.join(clean(v) for v in row)+' |' for row in rows]])

def reports(scope,depots,family,energy,people,phases,risk,mobilisation):
    outputs={}
    outputs['ESTIMATE.md']=f'''# Baghdad delivery estimate and scope reconciliation

The published **USD {scope['base_programme_usd']/1e9:.6f}bn equivalent** is a base planning estimate, not a complete delivery budget. City subtotal is USD {scope['city_subtotal_usd']/1e9:.6f}bn and the one Baghdad factory including its EPC is USD {scope['factory_with_epc_usd']/1e6:.3f}m. [Scope register](scope-register.csv) retains quantity, implied rate, currency/source quality, inclusions, exclusions, estimator role and uncertainty. Every actual price date, quotation and named estimator remains unknown. Category implied rates reconcile the baseline; they are not surveyed rates.

{table(['Baseline WBS','Quantity','USD m equivalent','Evidence'],[(r['scope'],f"{r['quantity']:,.3f}",f"{r['base_estimate_usd']/1e6:,.3f}",r['source_quality']) for r in scope['rows'] if r['base_estimate_usd'] is not None])}

{scope['unpriced_scope_count']} additional scope records retain **null costs**, not zero: land/title, utility diversions, duties/tax, owner costs, pre-opening people, six-car qualification, installed control/HIL, initial spares, working capital, civil/station investigations, task-derived maintenance and cyber deployment. Each requires a signed inclusion/quotation decision before financing is recalculated. Surveyed grade separation, foundations, standard spans, temporary works/erection, passenger access/evacuation, road interfaces and station functions must be investigated by corridor; civil and station standards alone do not resolve them.

EPC has [identified delivery obligations](epc-obligations.json), with individual priced contracts still null. Their sum cannot be asserted from the existing percentage. Factory contingency **USD {scope['known_embedded_allowances']['factory_contingency_usd']/1e6:.3f}m**, factory design/training/qualification **USD {family['factory_design_training_qualification_allowance_usd']/1e6:.1f}m**, routine train QA/labour/logistics and factory EPC are already embedded and must not be added twice. Initial stock, battery renewal cash dates, labour/maintenance contracts and working-capital reserves need account-level reconciliation.

{table(['Depot alternative','Gross priced reference USD m','Provisional replacement total USD bn'],[(n,f"{v['depot_gross_reference_usd']/1e6:.3f}",f"{v['provisional_reference_total_if_replacement_usd']/1e9:.6f}") for n,v in scope['alternatives'].items()])}

Replacement illustrations subtract the old depot allowance once, then add the gross quantity-based reference. They remain incomplete: charging/PV/EPC overlaps and unpriced work are unresolved. No alternative is adopted into the published funding programme; government/import shares, loans and opening dates remain conditional on the original scope. Retained property additions remain their existing separate scenarios, not automatically added to this base.

The seeded [correlated cost-and-delay sensitivity](cost-schedule-risk.json) combines a shared risk quantile with idiosyncratic cost events and delay escalation. Illustrative known-scope P50 is USD {risk['p50_known_scope_usd']/1e9:.3f}bn and P80 USD {risk['p80_known_scope_usd']/1e9:.3f}bn. **These are uncalibrated distributions, not an approved probabilistic budget.** Unpriced scope is excluded rather than priced at zero; existing contingencies remain embedded; stress outputs are alternatives and cannot be added to the base. Calibrate from investigations, contract evidence, event-level dependencies and actual invoice dates. [GAO estimating guidance](https://www.gao.gov/products/gao-20-195g) supports technical baseline, WBS, data, alternatives, risk analysis and updates; it does not validate OSR's rates. Reference checked 4 October 2026.
'''
    outputs['DEPOT-PACKAGE.md']=f'''# Baghdad line-local depot and stabling quantity package

The original allocation remains **{depots['station_trainsets']} station trains + {depots['depot_trainsets']} depot/storage trains = {depots['fleet_trainsets']}** and its morning-direction check remains failed. The {len(depots['missing_morning_directions'])} missing directional starts require an operating/stabling revision with conflict-aware evening returns, morning launches, recovery and degraded charging. This package does not turn storage capacity arithmetic into a physically accepted allocation.

{table(['Line','Station storage ID','Storage positions','Usable track m','Tracks / turnouts','Declared / workload bays'],[(r['line'],r['station'],r['stabling_positions'],f"{r['storage_usable_track_m']:,.0f}",f"{r['storage_tracks']} / {r['turnouts']}",f"{r['declared_workshop_bays']} / {depots['alternatives']['workload_bays']['sites'][i]['workshop_bays']}") for i,r in enumerate(depots['alternatives']['retained_declared_bays']['sites'])])}

The planning arrangement uses at most three 121 m usable train slots per storage track, separate fan/throat turnouts and 5 m track spacing, with a 1.8 access/land multiplier. Track metres are single-track storage lengths, not route-km or workshop bays. Yard geometry is not located on a surveyed parcel. Storage charging shares existing powered sites; connecting tracks, peak chargers/feeders, protection, rescue access and quarantine need site engineering.

One alternative retains the declared 125 main-depot bays and zero workshop bays at eight line-local sites. Another derives line-local bays from an explicit **400 bay-hours/train/year** sensitivity, 260 days/year, 16 hours/day and 70% bay availability. Neither is a released maintenance requirement. Bogie changes, heavy inspections, isolation, lifting, wash/cleaning, tools, stores and travel must establish actual bay occupation; person-hours are not bay-hours. The second alternative avoids assuming an unestablished interline move to the main workshop. Both price line-local inspection, rescue/isolation, quarantine, storage track/points, drainage/access, workshop shells/equipment and full depot PV/storage equipment quantities.

[Detailed items](depot-items.csv) show reference quantities and unquoted rates. The existing energy report's USD 5.93m **increment above the catalogue equipment** and 33,333 m² PV module requirement versus 4,000 m² canopy remain open. This package prices **full** 5 MW PV / 40 MWh equipment once; it does not also add the USD 5.93m delta. Equipment is not installed plant cost. PV placement, foundations/soil, battery fire spacing, DC protection, racking, utility connection and renewals are unpriced. Signed overlap decisions must reconcile the USD 8m depot and USD 67.6m charging allowances before adopting any replacement budget.
'''
    outputs['SIX-CAR-BASELINE.md']=f'''# Baghdad controlled six-car planning product

Configuration **{family['configuration_revision']}**, family metro-6car, covers **{family['trainsets']} consists / {family['vehicle_modules']} cars** at 111 m, 204 t controlled tare, 720 passengers / 960 crush, 1,350 kWh gross / 1,080 usable battery, 675 V nominal and 50 C HVAC ambient. [Family BOM](six-car-bom.csv) and [interface/qualification register](six-car.json) are separate from LM3's detailed 120-product manufacturing reference. Every quote, supplier part, mass evidence, production BOM and acceptance remains null/unaccepted. Common architectural ideas do not grant six-car applicability.

{table(['Six-car cost/mass category','Count / unit','Mass kg/consist','Allocated USD/consist'],[(r['part_id'],f"{r['quantity_per_consist']} {r['unit']}",f"{r['planning_mass_kg_per_consist']:,.0f}",f"{r['cost_allocation_per_consist_usd']:,.0f}") for r in family['bom']])}

Cost allocations sum to the existing **USD {family['cost_allocations_reconcile_usd']:,.0f}/train**. These are a control allocation of the price ceiling, not supplier estimates. The category mass subtotal is {family['planning_mass_subtotal_kg']:,.0f} kg and unallocated controlled-tare reserve {family['unallocated_mass_reserve_kg']:,.0f} kg; no weighed closure is claimed. There are 24 reference axles: average tare load {family['tare_axle_load_average_t']:.2f} t and crush load {family['full_load_axle_load_average_t']:.2f} t using an explicit 75 kg/passenger assumption. Individual axle/bogie imbalance, payload distribution and structural limits require calculations and weighing. The system schedule has {family['doors_per_consist']} door cassettes and {family['windows_per_consist']} window cassettes. Five inter-car interfaces, trainline/brake propagation, accessible platform/door interfaces, redundant controls, HV/charging, thermal/fire/EMC/harness interfaces each carry an acceptance requirement.

[Labour routes](six-car-labour-routing.csv) use the actual Baghdad factory stages, reference crew and cycle days. None is a measured six-car cycle. Rework, supplier queues and the current test-path throughput margin need trials; scaling an LM3 cycle is not evidence. Factory production payroll stays within train procurement, separate from railway operating payroll and factory capital. Work Order / Job Card references remain null until production BOMs, method revisions, calibrated tools, qualified operators and independent inspections exist.

The first-article qualification work breakdown has a **USD {family['qualification_reference_budget_usd']/1e6:.1f}m unquoted reference**. Its incremental funding is null because overlap with the factory's USD {family['factory_design_training_qualification_allowance_usd']/1e6:.1f}m design/training/qualification allowance remains unresolved. No automatic extra qualification or train premium is added. Supplier quotes, a detailed child-part BOM, structural/braking/trainline/thermal testing, acceptance labour and series-release authority must replace the planning controls before manufacture.
'''
    metrics=[(name,v) for name,v in energy['cases'].items()]
    outputs['HOURLY-ENERGY.md']=f'''# Baghdad chronological charging-energy and cost screen

The base traction intensity and timetable imply **{energy['annual_traction_demand_kwh']/1e6:,.1f} GWh/year**. The dedicated plant is {energy['plant_kw']/1000:,.1f} MW, plus existing on-site PV and {energy['existing_storage_kwh']/1000:,.0f} MWh storage. The base model's annual generation netting is not firm delivered charging. Ten percent of traction purchased at USD 0.10/kWh is **USD {energy['ten_percent_purchase_sensitivity_usd']/1e6:.3f}m/year**, an arithmetic sensitivity, not a forecast.

[Hourly CSVs](chronological-energy.json) contain three 8,760-hour synthetic representative weather/age years for each of owned solar, contracted solar and additional hybrid storage. They use the same timetable-derived service duty, with overnight schedules split across midnight; charger loss, PV performance/wheeling loss, storage charge/discharge losses, SoC floor, age degradation, import limits and curtailment are explicit. A seven-day poor-production spell is included. Initial storage sits at its protected floor, supplying no free energy. End storage is recorded and not sold.

{table(['Synthetic case','Grid GWh','Unserved GWh','Annual energy USD m','Extra hybrid equipment USD m'],[(name,f"{v['grid_import_kwh']/1e6:.1f}",f"{v['unserved_kwh']/1e6:.3f}",f"{v['annual_energy_cost_usd']/1e6:.3f}",f"{v['additional_hybrid_equipment_usd']/1e6:.1f}") for name,v in metrics])}

Electricity purchase, wheeling, balancing, capacity connection and owned-plant maintenance / contracted-solar payment are separate. PPA pays generated output even if curtailed; no surplus power sale is booked. The contracted case removes dedicated solar ownership capital and O&M, not existing station equipment. Hybrid storage adds its priced equipment once, with installed compound/protection, disposal and replacement costs still unquoted. Twenty-year indexed discounted cost is a **partial comparison**, not lifecycle bankability; no contract or tariffs are accepted. Unserved demand means the assumed service is unmet: no unchanged fares are credited to that service.

Aggregate connection and storage pooling are optimistic and unestablished. This screen does not supply site-specific wheeling rights or instantaneous charger arrival/queue proof. Measured multi-year weather/soiling, per-site feeder/charger duty, auxiliary loads, storage cycling/degradation, grid outages and binding backup contracts must be replayed before changing the funding programme's electricity allowance or selecting an ownership option.
'''
    outputs['WORKFORCE-COMPETENCE.md']=f'''# Baghdad workload, recruitment and competence pilot

The prior **{people['current_budget_fte']:,} FTE / USD {people['current_labour_usd']/1e6:.3f}m/year** allowance is USD {people['current_average_monthly_allowance_usd']:.2f}/person/month. The existing 21-role weighted split remains a budget allocation, not shift cover. This separate [establishment](workforce-establishment.csv) derives posts/task hours, {people['productive_hours_per_fte']} productive hours per FTE after leave, training, sickness and travel/handovers, integer cover and editable grade pay with employer/overtime allowances.

{table(['Function','Annual workload h','Concurrent posts','Reference FTE','Loaded annual IQD m'],[(r['role_id'],f"{r['annual_workload_person_hours']:,.0f}",r['minimum_concurrent_posts'],r['required_fte'],f"{r['annual_loaded_payroll_iqd']/1e6:,.1f}") for r in people['roles']])}

Reference total is **{people['reference_required_fte']:,} operating FTE**, loaded payroll **USD {people['reference_annual_loaded_payroll_usd']/1e6:.3f}m/year equivalent**. Quantities are explicit task-hour/post assumptions, **not measured local work or accepted Iraqi pay/rest terms**. Higher overtime, emergency cover, queues, simultaneous faults and actual maintenance could change them. The dedicated solar plant specialist workload is unpriced. Maintenance contracts and payroll must be reconciled to avoid adding contractor labour twice to existing envelopes. No revised OPEX is silently adopted.

Factory {people['factory_direct_positions_per_staffed_shift']:,} direct staffed-shift positions are separate; their production payroll is already in train procurement. Construction crew counts remain unknown and separate, rather than scheduled task slots called people. Temporary commissioning has its own cash requirement.

[Recruitment cohorts](recruitment-cohorts.csv) work backwards from each conditional line opening through requisition, selection, joining, training, first/repeated assessment and supervised experience. Offers allow 15% pre-join attrition and 80% first-pass / 75% repeat-pass assumptions. Hiring alone provides zero authorised productive capacity. Paid pre-opening training plus trainer/assessor reference cash is IQD {people['training_recruitment_cash_iqd']/1e9:.3f}bn; additional three-month commissioning payroll is IQD {people['temporary_commissioning_payroll_iqd']/1e9:.3f}bn. These are distinct pre-opening uses, with overlap against EPC still unverified; rigs, agency fees and local terms remain unquoted. No trained/appointed person is invented.

[Seven controlled curriculum drafts](training-curricula.json) cover induction, OCC, stations/accessibility, fleet, civil/energy, factory and supervisors/assessors. Each lists prerequisites, method revision, equipment, practical exercises, critical assessment criteria, assessor requirements and retraining triggers. [Arabic glossary](arabic-glossary.json) is a draft requiring native technical review; full Arabic lessons are pending. Attendance, practical competence and scoped task authorisation are separate records.

The [seven-day first-corridor OCC roster](pilot-roster.json) contains actual service-hour coverage requirements and **zero named workers**. Every slot is blocked pending appointments and task-specific authorisation. The executable [eligibility evaluator](../../../../../../../engineering/analysis/workforce_checks.py) checks worker record, assessed task/asset-family/location/method scope, validity, suspension, skill fade, availability, checked rest, access, permits, tools/materials, competent supervision and independent verification. Evaluate both at planning and task start; changed or expired evidence blocks eligibility. It creates no assignment or operational release.

Department owns outcomes/budget/risk; unit owns assets/backlog; crew owns executable access-window work; worker owns a scoped method/evidence; verifier owns independent acceptance/handback. [Native ERP mappings](native-workforce-map.json) retain Staffing Plan/recruitment/Employee/onboarding/training/shift records, manufacturing Work Order/Job Card and maintenance Asset Maintenance/Asset Repair, with Project/Task for programme evidence. Dashboards track accepted output, blocks, competence expiry, shortages, overdue hazards and forecast cost; attendance or Task closure never counts as physical acceptance. Deploy permissions/recovery/rest rules against actual records before enabling assignment.

[Frappe staffing documentation](https://docs.frappe.io/hr/staffing-plan) supports administrative records. [ORR competence guidance](https://www.orr.gov.uk/guide-rogs/7-managing-safety-critical-work) is a useful reference for assessment/monitoring/reassessment, not Iraqi legal approval. References checked 4 October 2026.
'''
    outputs['FIRST-PHASE.md']=f'''# Baghdad comparable opening fleet and corridor requirements

Demand is capacity-led in the existing model; population coverage is an access proxy. This [line-specific supply comparison](first-phase.csv) tests 6-minute opening peak service, 12-minute off-peak and 15-minute late service, 10% spares and retained cold reserves. Cycle time is inferred from the current peak fleet x minimum headway, not independently proved junction/turnback occupancy. Each line retains its published conditional full-line opening date.

{table(['Line','Opening month','Full fleet','Opening fleet','Deferred trains','Opening daily capacity'],[(r['line'],r['conditional_full_line_opening_month'],r['baseline_trainsets'],r['opening_trainsets'],r['deferred_trainsets'],f"{r['opening_daily_directional_capacity']:,}") for r in phases['lines']])}

The reference opening fleet is {phases['opening_fleet']} versus {phases['baseline_fleet']}, deferring {phases['deferred_fleet']} trains / USD {phases['deferred_train_capital_usd']/1e6:.3f}m gross equivalent, while requiring {phases['additional_fleet']} extra train / USD {phases['additional_train_capital_usd']/1e6:.3f}m to meet the rounded spare policy on line 9. Net reduction is {phases['baseline_fleet']-phases['opening_fleet']} trains at the current planning unit price. **This is deferred procurement, not a validated saving or adopted service cut.** Train-km and directional capacity fall with the new service; unchanged fares/revenue are never assumed. Expansion requires measured peak demand above 70% for 90 days, conflict-aware capacity, accepted spares and a newly financed delivery tranche.

Commercial corridor ranks, OD, access population and paid trips remain null. Compare actual origins/destinations/time, transfers vs paid boardings, accessibility/feeder catchments, fares, useful interchanges and standalone OPEX before choosing a first corridor. The existing 14.034 km outer-line demonstrator remains unproven commercially. Shared factory/civil/utility/control dependencies, accepted vehicles, staffing and operating release must accompany any opening. No earlier date or factory resize is asserted from vehicle subtraction alone. Existing acceleration/recovery cost-NPV trade-offs remain unchanged.
'''
    outputs['README.md']=f'''# Baghdad delivery reconciliation — 4 October 2026

The original Baghdad estimate is **USD {scope['base_programme_usd']/1e9:.6f}bn equivalent**, with an incomplete delivery scope. This package turns the attached review into reproducible quantity/cost/workload comparisons and six budgeted evidence workstreams. It adds no assumed passengers, leases, supplier quotes, appointments or approval, and does not replace the published finance case before scope is accepted.

- [Base estimate, exclusions, EPC and correlated cost/schedule sensitivity](ESTIMATE.md)
- [Line-local storage/depot quantities and alternative workshop scopes](DEPOT-PACKAGE.md)
- [Six-car BOM, mass/axle ledger, interfaces, labour and qualification](SIX-CAR-BASELINE.md)
- [Chronological generation/charging/storage and ownership comparisons](HOURLY-ENERGY.md)
- [Opening fleet and first-corridor demand requirements](FIRST-PHASE.md)
- [Workload establishment, recruitment, curricula and eligibility pilot](WORKFORCE-COMPETENCE.md)
- [Baghdad-specific governance instance](mobilisation.json)
- [Six 90-day evidence workstreams and budgets](90-day-work-programme.json)

The governance instance is tailored to Baghdad with accountable functions and closure work, while **{mobilisation['summary']['roles_ready']}/13 appointments, {mobilisation['summary']['management_systems_ready']}/11 systems and {mobilisation['summary']['gates_accepted']}/8 gates remain ready/accepted**. Names, appointment/competence evidence, legal entity and delegations remain pending. Role allocation is not a real appointment. Native ERP evidence Tasks remain open and do not approve budgets, manufacture or operation. Cybersecurity identity/secrets/updates/recovery/incident ownership and observation-only supervision boundaries retain their existing deployment gates.

Fresh-checkout validation: install the existing project test/render dependencies, then run `.venv/bin/python tools/automation/bootstrap_baghdad_tests.py` before the Baghdad tests. It selectively restores the exact ignored operations input from the tracked, hash-bound proposal archive, rejects drift/duplicate entries and preserves any differing workspace payload. It does not resynthesise the city or change controlled station IDs. Run the bootstrap with `--check` to verify only.

Regenerate `.venv/bin/python tools/automation/baghdad_delivery_baseline.py`, then the proposal. `--check` verifies all input/output hashes. None of the calculated alternatives has been accepted as an investment-ready budget.
'''
    return outputs

def rental_delivery_options(portfolio,rental_config,config):
    """Compare allocation, preserving total fit-out and separating rent credit."""
    c=config['rental_delivery'];discount=rental_config['model']['nominal_discount_rate']
    cases={}
    for name,capital_share,rent_share,opex_share in [
        ('landlord_funded',1.,1.,1.),
        ('tenant_funded_shell',1-c['tenant_funded_fitout_fraction'],1-c['tenant_rent_discount_fraction'],1.),
        ('developer_concession',0.,c['concession_landlord_receipt_fraction'],c['concession_landlord_opex_fraction'])]:
        rows=[]
        for r in portfolio['monthly']:
            month=r['month'];closed_area=0.
            for cohort in portfolio['cohorts']:
                age=month-cohort['handover_month']
                if age>=c['inspection_closure_interval_months'] and month<cohort['lease_end_month'] and age%c['inspection_closure_interval_months']<c['inspection_closure_months']:
                    closed_area+=cohort['lettable_m2']
            closed_fraction=min(1.,closed_area/r['active_lettable_m2']) if r['active_lettable_m2'] else 0.
            loss=r['rent_collected_usd']*closed_fraction;receipts=r['rent_collected_usd']-loss
            capital=r['physical_fitout_capital_usd'];refurb=r['refurbishment_usd']
            routine=r['landlord_opex_usd']-refurb
            landlord=receipts*rent_share-routine*opex_share-(capital+refurb)*capital_share
            partner=receipts*(1-rent_share)-routine*(1-opex_share)-(capital+refurb)*(1-capital_share)
            rows.append(dict(month=month,total_physical_fitout_usd=capital,landlord_fitout_usd=capital*capital_share,
                partner_fitout_usd=capital*(1-capital_share),maintenance_interruption_rent_loss_usd=loss,
                landlord_before_tax_cash_usd=landlord,partner_before_tax_cash_or_avoided_rent_usd=partner,
                combined_before_tax_value_usd=landlord+partner,landlord_rent_receipts_usd=receipts*rent_share,
                partner_receipts_or_avoided_rent_usd=receipts*(1-rent_share)))
        def pv(key):return sum(r[key]/(1+discount)**(r['month']/12) for r in rows)
        cases[name]=dict(monthly=rows,total_physical_fitout_usd=sum(r['total_physical_fitout_usd'] for r in rows),
            landlord_fitout_usd=sum(r['landlord_fitout_usd'] for r in rows),partner_fitout_usd=sum(r['partner_fitout_usd'] for r in rows),
            landlord_before_tax_npv_usd=pv('landlord_before_tax_cash_usd'),partner_before_tax_value_npv_usd=pv('partner_before_tax_cash_or_avoided_rent_usd'),
            combined_before_tax_value_npv_usd=pv('combined_before_tax_value_usd'),
            maintenance_interruption_rent_loss_usd=sum(r['maintenance_interruption_rent_loss_usd'] for r in rows),
            partner_value_is_avoided_rent=name=='tenant_funded_shell',actual_commitments=0,adopted=False)
    return dict(cases=cases,original_before_tax_npv_usd=portfolio['metrics']['resource_npv_before_tax_usd'],
        actual_local_enquiries=None,inspection_access_accepted=False,inspection_work_cost_usd=None,
        tax_and_contract_terms_accepted=False,additional_government_cash_usd=0,additional_chinese_credit_usd=0,
        limitations=['Equal physical resources; allocation creates no project saving or investor subscription',
            'Tenant benefit is avoided rent, not new landlord cash; tenant trading economics unmodelled',
            'Concession splits projected receipts/costs; actual bidding, guarantees, tax and rights unpriced',
            'Closure haircut is proportional to active area and collected cash; cohort arrears and legal compensation need accepted leases',
            'Inspection costs and access remain unpriced; no deposits counted as income or terminal sale'])

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.check:
        s=read(OUT/'summary.json')
        for base,key in ((ROOT,'sources_sha256'),(OUT,'outputs_sha256')):
            for path,sha in s[key].items():
                if digest(base/path)!=sha:raise ValueError('Stale delivery baseline: '+path)
        for path,sha in s['external_outputs_sha256'].items():
            if digest(ROOT/path)!=sha:raise ValueError('Stale current review: '+path)
        print('Delivery reconciliation source/output hashes pass');return
    config=tomllib.loads(CONFIG.read_text());validate(config)
    inputs=[Path(__file__),CONFIG,CITY/'design.toml',CITY/'baghdad.toml',
        CITY/'engineering/finance/summary.json',CITY/'engineering/stabling/summary.json',
        CITY/'engineering/depot-scope/summary.json',CITY/'engineering/detail/register.json',
        CITY/'engineering/factory/summary.json',CITY/'engineering/delivery-risk/summary.json',
        CITY.parent/'finance/baghdad-programme.json',ROOT/'lib/templates/capex-costs.toml',
        ROOT/'lib/templates/rolling-stock.toml',ROOT/'lib/templates/workforce.toml',
        ROOT/'lib/templates/owner-builder-operator-mobilisation.toml',
        ROOT/'tools/automation/validate-owner-builder-operator-mobilisation.py',
        ROOT/'tools/automation/bootstrap_baghdad_tests.py',ROOT/'engineering/analysis/workforce_checks.py',
        ROOT/'deployment/erpnext/apps/osr_erpnext/osr_erpnext/workforce_rules.py',
        ROOT/'deployment/erpnext/apps/osr_erpnext/osr_erpnext/workforce.py',
        CITY/'engineering/viaduct-rentals/medium.json',ROOT/'lib/templates/baghdad-viaduct-rentals.toml']
    sources={p.relative_to(ROOT).as_posix():digest(p) for p in inputs}
    revision=hashlib.sha256(json.dumps(sources,sort_keys=True).encode()).hexdigest()
    design=tomllib.loads(inputs[2].read_text());scenario=tomllib.loads(inputs[3].read_text())
    finance,stabling,existing_depot,detail,factory,delivery,programme=(read(p) for p in inputs[4:11])
    depots=depot_package(design,scenario,stabling,existing_depot,config)
    family=family_baseline(design,scenario,detail,factory,config)
    energy=chronological_energy(design,scenario,finance,config)
    people=workforce(design,scenario,finance,delivery,factory,config)
    phases=phase_fleet(design,scenario,delivery,config)
    scope=scope_register(design,finance,programme,depots,family,people,config)
    risk=correlated_risk(scope,config)
    OUT.mkdir(parents=True,exist_ok=True);outputs=[]
    def save(name,value):
        path=OUT/name;path.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n');outputs.append(path)
    def csvout(name,rows):
        path=OUT/name
        with path.open('w',newline='') as handle:
            writer=csv.DictWriter(handle,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
        outputs.append(path)
    # Instantiate governance, retaining real appointments and approvals empty.
    text=inputs[14].read_text().replace('Reference full railway delivery and operation; tailor responsibilities and evidence to the selected deployment',
        'Baghdad, Iraq: nine-line delivery and operation; future national projects excluded')
    text=text.replace('template_revision = "2026-09-09"','template_revision = "2026-10-04"').replace('project_id = ""','project_id = "BAGHDAD-DELIVERY"').replace('jurisdiction = ""','jurisdiction = "Iraq"')
    native_template=OUT/'mobilisation.toml';native_template.write_text(text);outputs.append(native_template)
    import importlib.util
    spec=importlib.util.spec_from_file_location('baghdad_mobilisation',inputs[15]);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    mobilisation=module.build_status(native_template)
    mobilisation.update(actual_full_network_conditional_opening_month=max(p['opening_month'] for p in delivery['cases']['calendar_baseline']['phases']),
        reference_template_windows_adopted=False,named_appointments=0)
    save('mobilisation.json',mobilisation)
    save('scope-register.json',scope);csvout('scope-register.csv',scope['rows']);save('epc-obligations.json',scope['epc_obligations'])
    save('depot-package.json',depots)
    csvout('depot-items.csv',[dict(alternative=name,**r) for name,variant in depots['alternatives'].items() for r in variant['items']])
    csvout('depot-sites.csv',[dict(alternative=name,**r) for name,variant in depots['alternatives'].items() for r in variant['sites']])
    save('six-car.json',family);csvout('six-car-bom.csv',family['bom']);csvout('six-car-labour-routing.csv',family['labour_routes'])
    for name,case in energy['cases'].items():
        hourly=case.pop('hourly');filename='energy-'+name.replace(':','-')+'-hourly.csv';csvout(filename,hourly);case['hourly_file']=filename
    save('chronological-energy.json',energy)
    save('workforce.json',people);csvout('workforce-establishment.csv',people['roles']);csvout('workforce-units.csv',people['units']);csvout('recruitment-cohorts.csv',people['recruitment_cohorts'])
    csvout('temporary-commissioning.csv',people['temporary_commissioning_cohorts'])
    save('training-curricula.json',people['curricula']);save('arabic-glossary.json',people['arabic_glossary']);save('pilot-roster.json',people['pilot_roster'])
    save('first-phase.json',phases);csvout('first-phase.csv',phases['lines']);save('cost-schedule-risk.json',risk)
    rentals=rental_delivery_options(read(inputs[-2]),tomllib.loads(inputs[-1].read_text()),config)
    for name,case in rentals['cases'].items():
        csvout('rental-'+name+'-monthly.csv',case.pop('monthly'))
        case['monthly_file']='rental-'+name+'-monthly.csv'
    save('rental-delivery-options.json',rentals)
    rental_report=OUT/'RENTAL-DELIVERY.md'
    rental_report.write_text('# Rental delivery allocation sensitivities\n\nThe existing medium portfolio retains identical physical fit-out and timing. These unquoted arrangements allocate costs and receipts; they create no extra funding, accepted tenant demand or macroeconomic saving.\n\n'+
        table(['Option','Landlord capital USD m','Partner capital USD m','Landlord before-tax NPV USD m','Partner value NPV USD m','Combined value NPV USD m'],
        [(name,f"{case['landlord_fitout_usd']/1e6:.3f}",f"{case['partner_fitout_usd']/1e6:.3f}",f"{case['landlord_before_tax_npv_usd']/1e6:.3f}",f"{case['partner_before_tax_value_npv_usd']/1e6:.3f}",f"{case['combined_before_tax_value_npv_usd']/1e6:.3f}") for name,case in rentals['cases'].items()])+
        '\n\nTenant-funded shells assume tenants pay 40% of fit-out/refurbishment for a 20% rent discount; their value column is avoided rent minus costs, not cash receipts or trading profit. The developer concession allocates 35% of collected rent and 20% of routine costs to the landlord; the developer funds fit-out/refurbishment. No concessions or subscriptions are signed.\n\nAll options lose two months of proportional rent every ten years after each cohort handover for structural inspection access. Routine costs continue. Maintenance work, compensation, tax, actual interruption dates and contract terms remain unpriced. [Monthly ledgers and limitations](rental-delivery-options.json) keep each party and combined value separate. The existing property/finance cases remain unchanged. Actual market enquiries and a small accepted pilot must determine selection.\n')
    outputs.append(rental_report)
    native_types=['Staffing Plan','Job Requisition','Job Opening','Job Applicant','Interview','Job Offer','Employee','Employee Onboarding',
        'Training Program','Training Event','Training Result','Employee Skill Map','Shift Assignment','Work Order','Job Card','Asset Maintenance','Asset Repair','Task']
    save('native-workforce-map.json',dict(status='draft-no-hiring-or-authorisation-records',record_types=native_types,
        schema_verified_on_local_instance_as_of='2026-10-04',native_record_ids=None,
        departments_units=[dict(department=r['department'],unit=r['unit'],manager=None,cost_centre=None,scope=r['quantity_basis']) for r in people['roles']],
        read_only_preview='osr_erpnext.workforce.preview_assignment',
        authorisation_packet=dict(project_revision=None,task_reference=None,worker=dict(worker_id=None,native_employee=None,
            evidence_revision=None,available=False,suspended=True,rest_checked=False,rest_compliant=False,location=None,authorisations=[]),
            task=dict(task_id=None,asset_id=None,isolation_scope=None,task_kind=None,asset_family='metro-6car',location=None,method_revision=None,maximum_skill_idle_days=90,independent_verification_required=True,
                required_tools=None,required_materials=None),resources={}),
        snapshot_validation_only=True,authoritative_revocation_resolved=False,live_start_check=False,
        boundary='Private controlled Employee File and native read permissions; snapshot result cannot establish live eligibility, assignment or work release',
        dashboard_metrics=['accepted-output','blocked-work','overdue-safety-actions','staff-shortages','competence-expiry','forecast-cost'],
        attendance_is_acceptance=False,observations_control_trains=False))
    streams=[('ESTIMATE','Finance and chief engineer','Signed complete scope/rates/inclusions/exclusions and correlated cost/schedule review',15,90),
        ('DEPOT','Operations and infrastructure','Surveyed line-local storage/points/charging/workshop/rescue/quarantine layouts and priced overlap reconciliation',15,75),
        ('DEMAND','Planning and operations','OD/access/fares and comparable useful first corridor, service/fleet/civil/dependency and standalone OPEX cases',15,75),
        ('PRODUCT','Manufacturing and engineering','Supplier-frozen six-car BOM, axle/mass, interfaces, measured labour/cycles, first article/qualification and factory path margins',15,90),
        ('PEOPLE','People and operating departments','Measured posts/task hours, local grade/employer/rest terms, recruitment/curricula and independently assessed eligible roster',15,90),
        ('PUBLICATION','Digital and configuration','Current front-door figures and exact-input clean-checkout/render/permission/recovery validation',1,30)]
    work=[]
    for key,owner,closure,start,due in streams:
        work.append(dict(id='BAG-EVID-DL90-'+key,accountable_function=owner,named_owner=None,start_day=start,due_day=due,
            day_basis='Days from approved workstream start; no calendar approval supplied',closure_evidence=closure,
            reference_estimator_person_days=120,reference_day_rate_usd=500,reference_closure_budget_usd=60000,
            budget_committed=False,existing_epc_overlap_accepted=False,physical_quote_budget_usd=None,
            status='not-demonstrated',evidence=None,source_revision=revision,
            acceptance_rule='Independent evidence and actual accountable signoff; generated arithmetic is not acceptance'))
    save('90-day-work-programme.json',dict(work_packages=work,reference_total_closure_budget_usd=360000,
        budget_in_existing_epc_unverified=True,actual_funding=None,external_contacts_made=False,operational_release=False))
    tasks=[dict(subject=w['id']+' — '+w['accountable_function'],status='Open',priority='High',
        description='<pre>'+html.escape(json.dumps(w,indent=2))+'</pre>') for w in work]
    save('erpnext-tasks.json',dict(doctype='Task',status='draft-import-package-not-live-records',tasks=tasks));csvout('erpnext-task-import.csv',tasks)
    texts=reports(scope,depots,family,energy,people,phases,risk,mobilisation)
    texts['README.md']+='\n- [Rental fit-out allocation and inspection-interruption comparison](RENTAL-DELIVERY.md)\n'
    for filename,text in texts.items():
        path=OUT/filename;path.write_text(text);outputs.append(path)
    current_review=ROOT/'docs/baghdad-delivery-review-2026-10-04.md'
    ref=energy['cases']['synthetic_reference:owned_solar']
    capital_periods=sum(r['capex_usd']>0 for r in programme['monthly'])
    opening_months=', '.join(str(r['opening_month']) for r in delivery['cases']['calendar_baseline']['phases'])
    current_review.write_text(f'''# Current Baghdad delivery review — 4 October 2026

Reviewed baseline: `135e249e20f0630f92f426764ea72d21e46c2a68`. This source-bound reconciliation supersedes the current-state Baghdad figures in [the historical October 3 codebase review](codebase-and-iraq-review-2026-10-03.md). It is a targeted delivery review, not a line-by-line audit or investment/construction release.

The controlled city remains {len(design['lines'])} lines, {sum(r['length_m'] for r in design['lines'])/1000:.4f} km, {len(design['stations'])} stations and {family['trainsets']} six-car trains. Published city capital is **USD {scope['city_subtotal_usd']/1e9:.6f}bn**, and one Baghdad factory including EPC brings the programme to **USD {scope['base_programme_usd']/1e9:.6f}bn**. Its monthly capital table has {capital_periods} periods and conditional full-line openings are {opening_months} months; the facility's {factory['readiness_months_from_ntp']} months starts at proposed NTP. The older 347-month rollout and earlier funding totals are historical and superseded. Proposed government funding remains 25% of original capital, imports 50% government USD / 50% Chinese USD loan, with other funds in IQD. No wider national revenue is added.

The [delivery package](../cities/catalogue/west-asia/Iraq/Baghdad/engineering/delivery-baseline/README.md) reconciles baseline WBS, exclusions, depot quantities, six-car product, chronological energy, demand/fleet phasing and workload/competence. None of its unquoted alternatives is adopted into debt, fares or official capital. Depot layouts, land/utility/title, local pay/workload, OD, equipment quotations and six-car first-article release remain open. Named owners cannot be manufactured by a role generator.

The current depot allowance is USD 8m, despite the full generated fleet, line-local storage/maintenance requirements and unresolved workshop sites and a failed morning-direction check. The new storage/workshop alternatives are quantity-based, with explicit baseline-overlap and unpriced-cost fields. The six-car allocation sums to USD 1.68m/train but does not imply qualified LM3 applicability or supplier quotations.

Hourly synthetic owned-solar reference purchases {ref['grid_import_kwh']/1e6:.1f} GWh, costing USD {ref['electricity_purchase_usd']/1e6:.3f}m/year before separately identified wheeling/balancing/connection/O&M. These are sensitivity outputs from synthetic weather and aggregate pooling, not a Baghdad forecast. Unserved energy and per-site physical/contract constraints remain visible. Staffing uses explicit workload/shift cover rather than dividing the existing USD 15.002m labour budget; pay, productive hours and roster authorisations remain unaccepted.

Fresh checkout: run `.venv/bin/python tools/automation/bootstrap_baghdad_tests.py`, then `.venv/bin/python -m pytest tools/automation/tests design/component-catalogue/tests -q`. The bootstrap validates the tracked proposal archive and selectively restores the exact ignored operations payload. It preserves differing workspace data and does not resynthesise designs. Install the existing test/render dependencies, including `mistune` and `reportlab`, before publication tests. Validate the delivery package and proposal with their generators' `--check` modes.

Six local ERP evidence drafts carry estimator work budgets, accountable functions, source revisions and independent exit evidence. No appointment, quote, lease, lender commitment, physical permission or railway authority is granted. Existing observation-only integration remains intact. The full Rust/browser/hardware suites are outside this targeted calculation change; verification results are reported with its commit.
''')
    summary=dict(schema='baghdad-delivery-reconciliation/1',as_of=config['model']['as_of'],source_revision=revision,
        sources_sha256=sources,outputs_sha256={p.name:digest(p) for p in outputs},
        external_outputs_sha256={current_review.relative_to(ROOT).as_posix():digest(current_review)},
        base_programme_usd=scope['base_programme_usd'],unpriced_scope_count=scope['unpriced_scope_count'],
        depot_reference_alternatives=scope['alternatives'],opening_fleet=phases['opening_fleet'],deferred_fleet=phases['deferred_fleet'],
        additional_fleet=phases['additional_fleet'],net_fleet_reduction=phases['baseline_fleet']-phases['opening_fleet'],
        reference_operating_fte=people['reference_required_fte'],reference_loaded_payroll_usd=people['reference_annual_loaded_payroll_usd'],
        owned_solar_reference_electricity_purchase_usd=ref['electricity_purchase_usd'],
        named_workers=0,appointed_roles=0,complete_delivery_budget=False,operational_release=False)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('Generated scope/depot/six-car/hourly energy/fleet/workforce/governance controls and six evidence drafts')

if __name__=='__main__':
    main()
