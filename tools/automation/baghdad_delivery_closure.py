#!/usr/bin/env python3
"""Complete repository deliverables while retaining external acceptance gates."""
from __future__ import annotations
import argparse
from collections import defaultdict
from copy import deepcopy
import csv
import gzip
import hashlib
import html
import json
import math
from pathlib import Path
import sys
import tomllib

from baghdad_delivery_baseline import ROOT, CITY, dispatch_energy, hourly_duty, workforce, table, trainset_reference_cost
from baghdad_delivery_stress import schedule, finance
from baghdad_funding_analysis import capital_projection, simulate
from baghdad_viaduct_comparison import bearing_index_delta_contracts

OUT=CITY/'engineering/delivery-closure'
CONFIG=ROOT/'lib/templates/baghdad-delivery-closure.toml'

def read(path):return json.loads(path.read_text())
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def pv(rows,key,rate):return sum(r[key]/(1+rate)**(r['month']/12) for r in rows)

def validate(c):
    for section in c.values():
        for key,value in section.items():
            if isinstance(value,(float,int)) and (isinstance(value,bool) or not math.isfinite(value) or value<0):
                raise ValueError('Invalid assumption: '+key)
    for section,keys in {'slab_factory':['working_days_per_year','utilisation','mould_cycle_working_days','panel_length_m','fastener_pitch_max_m'],
        'maintenance':['wheel_interval_km','bogie_interval_km','body_interval_years'],
        'mobilisation':['maximum_shift_hours','maximum_hours_rolling_7_days','pilot_worker_pool','trainees_per_external_mentor']}.items():
        if any(c[section][key]<=0 for key in keys):raise ValueError('Positive assumptions required: '+section)
    for key in ('depot_import_share','preopening_epc_credit_fraction','qualification_factory_credit_fraction','depot_energy_allowance_credit_fraction'):
        if not 0<=c['model'][key]<=1:raise ValueError('Invalid allocation '+key)
    if not 0<c['slab_factory']['utilisation']<=1:raise ValueError('Invalid mould utilisation')
    if c['mobilisation']['pilot_service_end_hour']<=c['mobilisation']['pilot_service_start_hour']:raise ValueError('Invalid service span')
    if any(isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) or v<=0 for v in c['corridors']['base_fare_sensitivities_iqd']):raise ValueError('Invalid base fare')

def depot_layouts(depots,design,phases,c):
    """Local-coordinate planning rectangles and explicit track/slot identifiers."""
    s=c['slab_factory'];openings={r['line']:r['conditional_full_line_opening_month'] for r in phases['lines']}
    stations={r['id']:r for r in design['stations']};sites=[];tracks=[];slots=[]
    for site in depots['alternatives']['workload_bays']['sites']:
        n=int(site['line'].split('-')[-1]);count=site['stabling_positions'];remaining=count
        longest=0;yard_width=site['storage_tracks']*5*1.8
        for index in range(site['storage_tracks']):
            positions=min(3,remaining);remaining-=positions;length=positions*121
            identifier=f'BAG-L{n}-ST{index+1:03d}'
            panels=math.ceil(length/s['panel_length_m'])
            # Standard panels plus one cut/end panel; no concrete beyond the usable track.
            seats_per_rail=sum(math.ceil(min(s['panel_length_m'],length-i*s['panel_length_m'])/s['fastener_pitch_max_m']) for i in range(panels))
            tracks.append(dict(id=identifier,line=site['line'],station=site['station'],usable_length_m=length,
                slots=positions,x0_m=0,y0_m=index*5,rail_m=2*length,slab_panel_positions=panels,
                concrete_reference_m3=length*(s['yard_panel_width_m']*s['yard_base_thickness_m']+2*s['plinth_width_m']*s['plinth_height_m']),
                fastener_seat_kits=2*seats_per_rail,turnout_geometry=None,constructed=False,accepted=False))
            for position in range(positions):slots.append(dict(id=identifier+f'-P{position+1}',track=identifier,
                line=site['line'],start_chainage_m=position*121,end_chainage_m=(position+1)*121,
                train_length_m=111,clearance_total_m=10,actual_asset_assignment=None,charger_circuit=None,physical_verified=False))
            longest=max(longest,length)
        if remaining:raise ValueError('Storage slots do not reconcile')
        columns=min(5,site['workshop_bays']);rows=math.ceil(site['workshop_bays']/columns)
        workshop_length=columns*121;workshop_width=rows*10
        sites.append(dict(**site,planning_yard_rectangle_length_m=longest,planning_yard_rectangle_width_m=yard_width,
            planning_yard_rectangle_m2=longest*yard_width,workshop_rectangle_length_m=workshop_length,
            workshop_rectangle_width_m=workshop_width,workshop_unused_bay_positions=columns*rows-site['workshop_bays'],
            workshop_rectangle_m2=workshop_length*workshop_width,station_reference=stations[site['station']],
            pv_module_area_m2=33333.333333333336 if n==6 else None,pv_ground_compound_area_m2=None,
            bess_fire_separation_m=None,inspection_rescue_quarantine_area_m2=None,
            delivered_panel_positions=sum(t['slab_panel_positions'] for t in tracks if t['line']==site['line']),
            panels_required_month=openings[site['line']]-s['installation_lead_months'],land_title=None,
            egress_and_turnout_clearances_accepted=False,survey_datum=None))
    capacity=0.;required=0;prefix=0;programme=[]
    for site in sorted(sites,key=lambda r:r['panels_required_month']):
        prefix+=site['delivered_panel_positions'];available=(site['panels_required_month']-s['ready_month'])*s['working_days_per_year']/12
        if available<=0:raise ValueError('Slab plant is not ready before installation')
        required=max(required,math.ceil(prefix*s['mould_cycle_working_days']/(available*s['utilisation'])))
        programme.append(dict(line=site['line'],deadline_month=site['panels_required_month'],panels=site['delivered_panel_positions'],
            cumulative_panels=prefix,available_working_days=available,minimum_mould_cells_at_prefix=required))
    capacity=required*s['utilisation']/s['mould_cycle_working_days']
    for row in programme:row['cumulative_capacity_margin_panels']=capacity*row['available_working_days']-row['cumulative_panels']
    return dict(sites=sites,tracks=tracks,slots=slots,total_storage_positions=len(slots),
        total_usable_track_m=sum(t['usable_length_m'] for t in tracks),rail_m=sum(t['rail_m'] for t in tracks),
        concrete_reference_m3=sum(t['concrete_reference_m3'] for t in tracks),fastener_seat_kits=sum(t['fastener_seat_kits'] for t in tracks),
        slab_factory=dict(minimum_parallel_mould_cells=required,programme=programme,ready_month=s['ready_month'],
            capital_allowance_usd=None,actual_cure_cycle_qualified=False,scope='Additional yard slabs only; main-line production remains separate'),
        physical_release=False,limitations=['Local diagram coordinates are not surveyed parcels or point alignment',
            'Rectangular packing includes spare positions; it does not reduce the itemised storage/workshop quantities',
            'PV/BESS/roads/outfalls/fire/turnout geometry and installation land remain unpriced',
            'Turnouts and sidings are not inferred from station passenger platforms'])

def layout_svg(site):
    """Vector design study; extents follow quantities without claiming alignment."""
    line=html.escape(site['line']);yard_length=site['planning_yard_rectangle_length_m'];yard_width=site['planning_yard_rectangle_width_m']
    ratio=min(380/max(yard_length,site['workshop_rectangle_length_m']),210/max(1,yard_width,site['workshop_rectangle_width_m']));width=yard_length*ratio;height=yard_width*ratio
    paths=[]
    for index in range(site['storage_tracks']):
        y=95+(index+.5)*5*ratio
        positions=min(3,site['stabling_positions']-index*3);x=90+positions*121*ratio
        paths.append(f'<path d="M90 {y:.2f} H{x:.2f}" stroke="#34495e" stroke-width="2"/>')
        for slot in range(positions):paths.append(f'<rect x="{90+(slot*121+5)*ratio:.2f}" y="{y-2:.2f}" width="{111*ratio:.2f}" height="4" fill="#168477"/>')
    workshop=f'<rect x="500" y="95" width="{site["workshop_rectangle_length_m"]*ratio:.2f}" height="{site["workshop_rectangle_width_m"]*ratio:.2f}" fill="#e5effa" stroke="#316caa"/>'
    for index in range(site['workshop_bays']):
        column=index%min(5,site['workshop_bays']);row=index//min(5,site['workshop_bays'])
        workshop+=f'<rect x="{500+column*121*ratio:.2f}" y="{95+row*10*ratio:.2f}" width="{121*ratio:.2f}" height="{10*ratio:.2f}" fill="none" stroke="#316caa" stroke-width="0.5"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="530" viewBox="0 0 900 530">
<rect width="900" height="530" fill="white"/><g font-family="sans-serif" fill="#17324d">
<text x="30" y="30" font-size="21">Baghdad {line}: storage and workshop planning study</text>
<text x="30" y="57" font-size="13">Local coordinates only. NOT a surveyed, structurally released or operationally authorised layout.</text>
<rect x="85" y="90" width="{width+10:.2f}" height="{height+10:.2f}" fill="#edf5f3" stroke="#168477"/>
{''.join(paths)}
{workshop}<text x="500" y="80" font-size="12">Workshop packing; internal track access unresolved</text>
<text x="30" y="355">{site['storage_tracks']} storage tracks / {site['stabling_positions']} slots / {site['storage_usable_track_m']:.0f} usable track m</text>
<text x="30" y="382">Yard packing envelope {yard_length:.0f} x {yard_width:.0f} m; access/point/land geometry unresolved</text>
<text x="30" y="409">Workshop: {site['workshop_bays']} bays; shell packing {site['workshop_rectangle_length_m']:.0f} x {site['workshop_rectangle_width_m']:.0f} m</text>
<text x="30" y="436">Inspection, rescue, battery quarantine, PV/BESS, drainage outfall and fire access require located design.</text>
<text x="30" y="465">Green blocks: 111 m trains + 10 m slot clearance. Actual train assignments and charger circuits remain empty.</text>
<text x="30" y="497">No drawing footprint is credited as acquired land or accepted turnout geometry.</text></g></svg>'''

def expanded_bom(scenario,family,detail):
    systems=scenario['consist']['systems'];cars=family['cars'];count=family['trainsets']
    items=[('carbody-module',cars,'carbody-structure','Controlled six-car body module; structure drawing required'),
        ('bogie',2*cars,'bogie-running-gear','Bogie supplier and axle load distribution required'),
        ('wheelset',4*cars,'bogie-running-gear','Two axles per bogie; tread, bearings, brakes unqualified'),
        ('wheel',8*cars,'bogie-running-gear','Two wheels per wheelset'),
        ('traction-controller',detail['family_profile']['traction_controller_count'],'traction-controls','Motor/inverter pairing and power evidence required'),
        ('battery-225kwh-module',cars,'battery-modules','225 kWh gross allocation; cell/pack count unquoted'),
        ('door-cassette',systems['door_cassettes_per_car']*cars,'interior-doors-glazing','Door/platform/fire/accessibility qualification'),
        ('window-cassette',systems['window_cassettes_per_car']*cars,'interior-doors-glazing','Retention, thermal and fire tests'),
        ('service-rail',systems['service_rails_per_car']*cars,'interior-doors-glazing','Controlled mounting/load interfaces'),
        ('main-light',systems['main_light_modules_per_car']*cars,'interior-doors-glazing','Thermal, EMC and lux'),
        ('emergency-light',systems['emergency_light_modules_per_car']*cars,'interior-doors-glazing','Independent emergency supply/autonomy'),
        ('threshold-light',systems['door_threshold_light_modules_per_car']*cars,'interior-doors-glazing','Doorway light integration'),
        ('thermal-interface',cars,'thermal-roof-services','24 kW thermal/car reference; compressor/refrigerant design unqualified'),
        ('inter-car-interface',cars-1,'trainline-couplers','Mechanical/electrical/braking joint; actual coupler halves required')]
    rows=[dict(id='M6-C-'+key,parent='M6-'+parent,quantity_per_train=quantity,network_quantity=quantity*count,
        unit='each',quantity_basis='six-car profile / system counts',interface=interface,supplier=None,
        unit_price_usd=None,unit_mass_kg=None,allocation_is_inside_parent=True,additional_capital_usd=0,
        drawing=None,qualification_accepted=False) for key,quantity,parent,interface in items]
    for key,parent,interface in [('structural-joints','carbody-structure','Fatigue/weld/bolt/adhesive and inspectability'),
        ('brake-equipment','bogie-running-gear','Independent braking and fail-safe propagation'),
        ('hv-isolation','battery-modules','Contactors, fuses, precharge, service isolator, earthing'),
        ('lv-power-distribution','traction-controls','Redundant 24 V supply, protection, connectors and harnesses'),
        ('cab-passenger-controls','trainline-couplers','Driverless operational/safety interfaces and human handback'),
        ('tacs-dual-controller','trainline-couplers','Dual independent control channels; module count/maturity must be frozen'),
        ('t-obs-sensing','trainline-couplers','100 W bench reference is not an installed qualified assembly'),
        ('communications-cyber','trainline-couplers','Authenticated links, time, updates, logs and recovery'),
        ('fire-emergency','interior-doors-glazing','Detection/isolation, evacuation equipment and labelled procedures')]:
        rows.append(dict(id='M6-C-'+key,parent='M6-'+parent,quantity_per_train=None,network_quantity=None,
            unit='supplier-schedule-required',quantity_basis='unresolved-interface-not-zero',interface=interface,
            supplier=None,unit_price_usd=None,unit_mass_kg=None,allocation_is_inside_parent=True,
            additional_capital_usd=None,drawing=None,qualification_accepted=False))
    return dict(parts=rows,parent_allocations=family['bom'],parent_total_per_train_usd=family['cost_allocations_reconcile_usd'],
        qualification_work_packages=family['qualification_work_packages'],supplier_quotes=0,engineering_release=False,
        unknown_child_prices_are_not_zero=True,software_allocations=detail['software_allocations'])

def site_energy(design,scenario,city_finance,baseline_config):
    """Explicit synthetic station-duty allocation; no unconstrained city pooling."""
    c=baseline_config['energy'];station_lines={s['id']:s['line'] for s in design['stations']}
    total=city_finance['operations_basis']['annual_train_km_including_non_revenue']*scenario['consist']['car_count']*city_finance['operations_basis']['energy_kwh_per_car_km_hot_climate_planning']
    fleets={r['line']:r for r in scenario['fleets']};line_weights={}
    from baghdad_delivery_baseline import windows
    for line in design['lines']:
        trips=sum((end-start)/headway*2 for start,end,headway in windows(fleets[line['name']]))
        line_weights[line['name']]=trips*line['length_m']/1000
    plant_costs=tomllib.loads((ROOT/'lib/templates/capex-costs.toml').read_text())['solar_power_plant']
    plant=city_finance['capex_usd']['timetable_sized_dedicated_solar']/(plant_costs['utility_pv_usd_per_kw']+plant_costs['interconnection_usd_per_kw'])
    sun=[max(0,math.sin(math.pi*(h+.5-6)/12)) for h in range(24)];sun_sum=sum(sun)
    cases={};lines=defaultdict(list)
    for site in scenario['sites']:lines[station_lines[site['station']]].append(site)
    for weather,yield_factor,age in [('reference',1,0),('poor',c['poor_year_yield_factor'],0),('aged10',1,10)]:
        records=[];hourly_by_line={};shortages=[];annual_charging=0
        for line in design['lines']:
            name=line['name'];energy=total*line_weights[name]/sum(line_weights.values());duty=hourly_duty(dict(lines=[line]),dict(fleets=[fleets[name]]),energy)
            pool=lines[name];weight=sum(s['charger_max_kw'] for s in pool)
            aggregates=[dict(hour=h,line=name,demand_kwh=0.,generation_kwh=0.,grid_import_kwh=0.,unserved_kwh=0.,curtailed_kwh=0.,closing_soc_kwh=0.) for h in range(8760)]
            for site in pool:
                share=site['charger_max_kw']/weight;utility_kw=plant*line_weights[name]/sum(line_weights.values())*share
                loads=[];generation=[];local_generation=[];remote_generation=[]
                for day in range(365):
                    season=1+.25*math.sin(2*math.pi*(day-80)/365)
                    poor=c['poor_spell_yield_factor'] if 5<=day<5+c['poor_spell_days'] else 1.
                    for hour in range(24):
                        loads.append(duty[hour]*share/site['charger_efficiency'])
                        shape=scenario['climate']['peak_sun_hours']*c['pv_performance_ratio']*season*yield_factor*poor*sun[hour]/sun_sum
                        local_generation.append(site['pv_nameplate_kw']*shape)
                        remote_generation.append(utility_kw*shape)
                        generation.append(local_generation[-1]+remote_generation[-1]*(1-c['wheeling_loss_fraction']))
                rows=dispatch_energy(generation,loads,storage_kwh=site['storage_capacity_kwh'],
                    power_kw=min(site['storage_max_charge_kw'],site['storage_max_discharge_kw']),grid_kw=site['grid_import_kw'],
                    config=c,capacity_fraction=(1-c['storage_annual_degradation'])**age)
                grid=sum(r['grid_import_kwh'] for r in rows);unserved=sum(r['unserved_kwh'] for r in rows)
                upgrade=max(r['unserved_kwh'] for r in rows);charger_upgrade=max(0,max(loads)*site['charger_efficiency']-site['charger_max_kw'])
                gross_utility=sum(remote_generation)
                delivered=sum(min((r['demand_kwh']-r['unserved_kwh'])*site['charger_efficiency'],site['charger_max_kw']) for r in rows)
                for r in rows:
                    charger_shortage=max(0,(r['demand_kwh']-r['unserved_kwh'])*site['charger_efficiency']-site['charger_max_kw'])
                    if r['unserved_kwh']>1e-7 or charger_shortage>1e-7:
                        shortages.append(dict(station=site['station'],line=name,hour=r['hour'],day=r['hour']//24,
                            local_pv_kwh=local_generation[r['hour']],remote_pv_before_wheeling_kwh=remote_generation[r['hour']],
                            demand_kwh=r['demand_kwh'],grid_limit_kw=site['grid_import_kw'],grid_import_kwh=r['grid_import_kwh'],
                            storage_power_limit_kw=min(site['storage_max_charge_kw'],site['storage_max_discharge_kw']),
                            opening_soc_kwh=r['opening_soc_kwh'],closing_soc_kwh=r['closing_soc_kwh'],
                            unserved_bus_kwh=r['unserved_kwh'],charger_limit_kw=site['charger_max_kw'],
                            charger_delivery_shortfall_kwh=charger_shortage,
                            diagnosis='Installed charger limit' if r['unserved_kwh']<=1e-7 else 'Grid limit plus unavailable stored energy/power',
                            accepted=False))
                cost=(grid+unserved)*c['import_purchase_usd_per_kwh']+gross_utility*c['wheeling_usd_per_kwh']+sum(loads)*c['balancing_usd_per_kwh']+(site['grid_import_kw']+upgrade)*c['connection_usd_per_kw_year']
                records.append(dict(station=site['station'],line=name,allocated_traction_kwh=energy*share,charging_demand_kwh=sum(loads),
                    allocated_utility_pv_kw=utility_kw,gross_utility_generation_kwh=gross_utility,local_generation_kwh=sum(local_generation),generation_kwh=sum(generation),grid_import_kwh=grid,unserved_kwh=unserved,
                    installed_deliverable_traction_upper_bound_kwh=delivered,installed_service_energy_fraction=delivered/(energy*share),
                    curtailment_kwh=sum(r['curtailed_kwh'] for r in rows),storage_loss_kwh=sum(r['conversion_loss_kwh'] for r in rows),
                    grid_upgrade_minimum_kw=upgrade,charger_upgrade_minimum_kw=charger_upgrade,grid_and_charger_upgrade_capex_usd=None,
                    firm_purchase_topup_kwh=unserved,annual_firm_energy_services_usd=cost,
                    hourly_maximum_energy_residual_kwh=max(abs(r['energy_residual_kwh']) for r in rows),
                    allocation_basis='Line timetable train-km; within line proportional installed charger kW; charging event/queue evidence absent',
                    actual_wheeling_rights=None,physical_release=False))
                for target,r in zip(aggregates,rows):
                    for key in ('demand_kwh','generation_kwh','grid_import_kwh','unserved_kwh','curtailed_kwh','closing_soc_kwh'):target[key]+=r[key]
                annual_charging+=sum(loads)
            hourly_by_line[name]=aggregates
        annual_cost=sum(r['annual_firm_energy_services_usd'] for r in records)+city_finance['annual_opex_usd']['components']['solar_plant_maintenance']
        cases[weather]=dict(sites=records,hourly_by_line=hourly_by_line,shortage_hours=shortages,
            site_charger_or_bus_shortage_hour_count=len(shortages),bus_shortage_distinct_hours=len({r['hour'] for r in shortages if r['unserved_bus_kwh']>1e-7}),
            installed_deliverable_traction_upper_bound_kwh=sum(r['installed_deliverable_traction_upper_bound_kwh'] for r in records),
            traction_demand_kwh=total,charging_bus_demand_kwh=annual_charging,
            grid_import_kwh=sum(r['grid_import_kwh'] for r in records),unserved_kwh=sum(r['unserved_kwh'] for r in records),
            firm_purchase_topup_kwh=sum(r['firm_purchase_topup_kwh'] for r in records),annual_firm_energy_cost_usd=annual_cost,
            grid_upgrade_minimum_kw=sum(r['grid_upgrade_minimum_kw'] for r in records),
            charger_upgrade_minimum_kw=sum(r['charger_upgrade_minimum_kw'] for r in records),
            actual_upgrade_capex_usd=None,physical_release=False)
    return dict(weather_basis='Synthetic shape, not measured Baghdad climate',cases=cases,allocation_accepted=False,
        limitations=['No city-wide pooling; each node retains its own storage/connection',
            'Firm cost sensitivity purchases unmet energy and pays expanded connection charges; upgrade CAPEX remains null',
            'Charger overload is recorded separately; no forecast of achieved trips until physical upgrades and queues are accepted',
            'No PV export income; site duty and utility allocations are editable hypotheses'])

def maintenance(design,scenario,people,finance,phases,c):
    m=c['maintenance'];rows=[];renewals=[];line_lookup={r['line']:r for r in phases['lines']}
    total_km=finance['operations_basis']['annual_train_km_including_non_revenue']
    weights={r['line']:r['baseline_daily_train_km'] for r in phases['lines']}
    for fleet in design['fleets']:
        line=fleet['line'];trains=fleet['trainset_count'];annual_km=total_km*weights[line]/sum(weights.values());per_train=annual_km/trains
        length=next(r['length_m']/1000 for r in design['lines'] if r['name']==line);roundtrips=annual_km/(2*length)
        tasks=[('rs-daily',365*trains,m['daily_mechanical_hours'],m['daily_electrical_hours'],'train inspection'),
            ('rs-weekly',math.ceil(365/7)*trains,m['weekly_mechanical_hours'],m['weekly_electrical_hours'],'train inspection'),
            ('rs-monthly',12*trains,m['monthly_mechanical_hours'],m['monthly_electrical_hours'],'train inspection'),
            ('rs-turnaround-service',roundtrips,m['turnaround_mechanical_hours'],m['turnaround_electrical_hours'],'round trip; cleaning already separate'),
            ('rs-wheel-reprofile',annual_km/m['wheel_interval_km']*24,m['wheel_reprofile_hours_per_wheelset'],0,'24 wheelsets/train'),
            ('rs-bogie-overhaul',annual_km/m['bogie_interval_km']*12,m['bogie_overhaul_hours_per_bogie'],0,'12 bogies/train'),
            ('rs-body-overhaul',trains/m['body_interval_years'],m['body_overhaul_hours_per_train'],0,'Average workload; actual overhaul date separate')]
        for identifier,events,mech,elect,basis in tasks:rows.append(dict(line=line,task=identifier,annual_events_reference=events,
            mechanical_person_hours=events*mech,electrical_person_hours=events*elect,basis=basis,
            annual_train_km=annual_km,annual_train_km_per_consist=per_train,measured_duration=None,
            parts_allowance_usd=None,asset_id=None,native_work_order=None,accepted=False))
        cycle=finance['renewal_policy']['train_battery_cycle_years'];opening=line_lookup[line]['conditional_full_line_opening_month']
        annual_reserve=trains*m['battery_replacement_cost_usd_per_train']/cycle
        for age in range(cycle,31,cycle):renewals.append(dict(line=line,month=opening+age*12,trainsets=trains,
            reference_replacement_usd=trains*m['battery_replacement_cost_usd_per_train'],reference_annual_reserve_usd=annual_reserve,
            existing_renewal_reserve_included=True,incremental_opex_usd=0,actual_serial_delivery_dates=None,accepted=False))
    available={r['role_id']:r['annual_workload_person_hours'] for r in people['roles']}
    return dict(tasks=rows,battery_renewals=renewals,mechanical_person_hours=sum(r['mechanical_person_hours'] for r in rows),
        electrical_person_hours=sum(r['electrical_person_hours'] for r in rows),
        existing_mechanical_workload_hours=available['fleet-mechanical'],existing_electrical_workload_hours=available['fleet-electrical'],
        existing_total_rolling_maintenance_and_reserve_usd=finance['annual_opex_usd']['components']['rolling_stock_maintenance_including_battery_renewal_reserve'],
        reference_annual_battery_reserve_usd=sum(f['trainset_count'] for f in design['fleets'])*m['battery_replacement_cost_usd_per_train']/finance['renewal_policy']['train_battery_cycle_years'],
        initial_battery_spare_reference_usd=sum(f['trainset_count'] for f in design['fleets'])*m['battery_replacement_cost_usd_per_train']*m['initial_battery_spare_fraction'],
        initial_spares_allowance_inclusion=None,additional_payroll_or_reserve_adopted=False,
        limitations=['Person-hours are editable task assumptions; outages, faults, major repairs and actual bay-hours are unpriced',
            'Overhaul events from distance are workload averages; serial-specific mileage/date evidence must set cash dates',
            'Battery replacement cash is a use of the existing reserve, not additional annual maintenance CAPEX',
            'Condition-based work, tools/calibration, supplier spares and contractor/payroll overlap remain open'])

def battery_cash(maintenance_data,phases,options,horizon=444):
    """Restricted reserve cash; never available for voluntary loan repayment."""
    rows=[];growth=options['fares']['opex_inflation'];renewals=maintenance_data['battery_renewals']
    for phase in phases['lines']:
        line=phase['line'];opening=phase['conditional_full_line_opening_month'];balance=0
        events={r['month']:r for r in renewals if r['line']==line}
        annual=next(r['reference_annual_reserve_usd'] for r in renewals if r['line']==line)
        for month in range(horizon):
            index=(1+growth)**(month//12);active=opening<=month<horizon-1
            contribution=annual/12*index if active else 0
            replacement=events.get(month,{}).get('reference_replacement_usd',0)*index
            topup=max(0,replacement-balance-contribution);closing=balance+contribution+topup-replacement
            rows.append(dict(line=line,month=month,opening_restricted_cash_usd=balance,
                contribution_inside_existing_maintenance_usd=contribution,replacement_usd=replacement,
                inflation_topup_required_usd=topup,closing_restricted_cash_usd=closing,
                balance_residual_usd=balance+contribution+topup-replacement-closing,
                legal_reserve_account=None,available_for_early_debt_repayment=False))
            balance=closing
    return dict(monthly=rows,total_topups_usd=sum(r['inflation_topup_required_usd'] for r in rows),
        terminal_restricted_cash_usd=sum(r['closing_restricted_cash_usd'] for r in rows if r['month']==horizon-1),
        accepted_reserve_split=False,limitations=['Reserve contribution is an assumed split of existing rolling maintenance, not an extra annual charge',
            'Zero reserve interest; inflation can leave a cash shortfall at replacement',
            'Replacement months use line opening proxy; delivered battery serial ages/condition remain required',
            'Restricted cash is not terminal sale income or distributable surplus'])

def opening_scenario(design,scenario,phases):
    from baghdad_delivery_baseline import windows
    d=deepcopy(design);s=deepcopy(scenario);by_line={r['line']:r for r in phases['lines']}
    for fleet in d['fleets']:
        ref=by_line[fleet['line']]
        fleet.update(trainset_count=ref['opening_trainsets'],peak_count=ref['opening_peak_count'],spare_count=ref['opening_spares'])
    for fleet in s['fleets']:
        ref=by_line[fleet['line']];new=[]
        for start,end,headway in windows(fleet):
            cursor=start
            while cursor<end:
                finish=min(end,(cursor//60+1)*60);hour=(cursor//60)%24
                desired=6 if 7<=hour<9 or 15<=hour<17 else (15 if hour>=21 or hour<5.5 else 12)
                new.append(dict(**{'from':f'{(cursor//60)%24:02d}:{cursor%60:02d}','to':f'{(finish//60)%24:02d}:{finish%60:02d}'},headway_min=max(headway,desired)))
                cursor=finish
        fleet.update(schedule=new,trainset_count=ref['opening_trainsets'],spare_count=ref['opening_spares'])
    return d,s

def corridor_cases(design,scenario,phases,finance_data,factory,baseline_config,closure_config,energy,programme):
    rows=[]
    for phase in phases['lines']:
        line=phase['line'];d=deepcopy(design);s=deepcopy(scenario)
        for key in ('lines','fleets'):d[key]=[r for r in d[key] if r.get('name',r.get('line'))==line]
        d['stations']=[r for r in d['stations'] if r['line']==line]
        s['fleets']=[r for r in s['fleets'] if r['line']==line];ids={r['id'] for r in d['stations']}
        s['sites']=[r for r in s['sites'] if r['station'] in ids]
        risk=dict(cases=dict(calendar_baseline=dict(phases=[dict(line=line,opening_month=phase['conditional_full_line_opening_month'],weight=1.)])))
        people=workforce(d,s,finance_data,risk,factory,baseline_config)
        km=d['lines'][0]['length_m']/1000;fare=programme['comparison']['fare_iqd'];nonfare=programme['operating_receipts']['existing_nonfare_annual_usd']*len(d['stations'])/len(design['stations'])
        costs=finance_data['annual_opex_usd']['components']
        energy_cost=sum(r['annual_firm_energy_services_usd'] for r in energy['cases']['reference']['sites'] if r['line']==line)
        solar_share=costs['solar_plant_maintenance']*phase['opening_daily_train_km']/sum(r['opening_daily_train_km'] for r in phases['lines'])
        maintenance_cost=costs['civil_station_depot_maintenance']*km/(sum(r['length_m'] for r in design['lines'])/1000)+costs['signalling_maintenance']*km/(sum(r['length_m'] for r in design['lines'])/1000)+costs['rolling_stock_maintenance_including_battery_renewal_reserve']*phase['opening_trainsets']/phases['baseline_fleet']
        opex=people['reference_annual_loaded_payroll_usd']+maintenance_cost+energy_cost+solar_share
        capacity=phase['opening_daily_directional_capacity']*365;cash_required=max(0,opex-nonfare)
        neutral_trips=cash_required*closure_config['model']['iqd_per_usd']/fare
        proxy_trips=capacity*closure_config['corridors']['paid_trip_share_of_capacity']
        break_fare=cash_required*closure_config['model']['iqd_per_usd']/proxy_trips
        rows.append(dict(line=line,route_km=km,stations=len(d['stations']),opening_fleet=phase['opening_trainsets'],
            annual_directional_capacity=capacity,reference_standalone_fte=people['reference_required_fte'],
            reference_standalone_payroll_usd=people['reference_annual_loaded_payroll_usd'],reference_annual_opex_usd=opex,
            allocated_existing_nonfare_usd=nonfare,base_yield_iqd=fare,operating_break_even_paid_trips=neutral_trips,
            operating_break_even_capacity_use=neutral_trips/capacity,assumed_paid_trips_sensitivity=proxy_trips,
            operating_break_even_fare_iqd=break_fare,monthly_44_trip_cost_income_share=break_fare*closure_config['corridors']['affordability_trip_count_monthly']/closure_config['corridors']['income_proxy_monthly_iqd'],
            actual_od_demand=None,actual_access_population=None,commercial_rank=None,
            land_and_station_site_specific_costs_usd=None,allocated_borrower_debt_service_usd=None,
            infrastructure_and_solar_share_basis='Existing unverified maintenance/solar allowances allocated by route/duty; shared assets not assumed free',
            adopted=False))
    return dict(cases=rows,first_corridor_selected=False,comparison_scope='Standalone operation before debt/tax; same reference fare and 20% capacity-use sensitivity',
        investigations=[dict(line=r['line'],od_counts=None,peak_loading=None,interchange_paid_transfers=None,
            pedestrian_feeder_access=None,station_parcel=None,utilities=None,geotechnical_boreholes=None,
            evacuation_flow=None,temporary_works=None,investigation_quote=None,appointed_owner=None) for r in rows])

def pilot_roster(c):
    """Synthetic slot feasibility; placeholders cannot pass actual eligibility."""
    m=c['mobilisation'];pool={f'UNAPPOINTED-{i+1}':[] for i in range(m['pilot_worker_pool'])};rows=[]
    for day in range(m['pilot_days']):
        cursor=day*24+m['pilot_service_start_hour'];end=day*24+m['pilot_service_end_hour']
        while cursor<end:
            finish=min(end,cursor+m['maximum_shift_hours'])
            candidates=[]
            for worker,history in pool.items():
                rest=cursor-history[-1][1] if history else math.inf
                hours=sum(max(0,min(b,finish)-max(a,finish-168)) for a,b in history)+finish-cursor
                if rest>=m['minimum_rest_hours'] and hours<=m['maximum_hours_rolling_7_days']:candidates.append((sum(b-a for a,b in history),worker,rest,hours))
            if not candidates:raise ValueError('Pilot staffing pool cannot meet shift/rest limits')
            _,worker,rest,hours=min(candidates);pool[worker].append((cursor,finish))
            rows.append(dict(day=day,start_hour_from_week=cursor,end_hour_from_week=finish,
                planning_position=worker,prior_rest_hours=None if not math.isfinite(rest) else rest,
                hours_rolling_7_days=hours,maximum_shift_hours=m['maximum_shift_hours'],
                native_employee=None,actual_authorisation=None,eligible=False,physical_work_release=False))
            cursor=finish
    return dict(slots=rows,planning_positions=len(pool),actual_appointments=0,
        required_weekly_cover_hours=sum(r['end_hour_from_week']-r['start_hour_from_week'] for r in rows),
        limits_are_accepted_iraqi_employment_terms=False,roster_released=False)

def reconstruct_inputs(paths, operating_phases=None):
    from osr_scenario.iraq_finance import city_funding_config
    config=city_funding_config(tomllib.loads(paths['funding'].read_text()),'baghdad')
    options=tomllib.loads(paths['options'].read_text());programme=read(paths['programme']);city_finance=read(paths['finance'])
    factory=read(paths['factory']);risk=tomllib.loads(paths['risk_config'].read_text());stress=read(paths['stress'])
    payload=json.loads(gzip.decompress(paths['operations'].read_bytes()))
    city_finance['_contracts']=payload['project_twin']['budget_contracts']
    task_lines={r['manufacturing_uid']:r['line'] for r in payload['manufacturing_tasks']}
    settings=deepcopy(stress['cases']['calendar_baseline']['settings']);settings['export_model_inputs']=True
    delivery=schedule(payload['manufacturing_tasks'],factory,settings)
    if operating_phases is not None:
        delivery['phases']=deepcopy(operating_phases)
    result=finance(delivery,settings,(config,options,programme,city_finance,factory,risk))
    reference=read(paths['reference'])
    for key in ('peak_supplemental_balance_iqd','total_capital_usd','terminal_cash_iqd'):
        if operating_phases is None and abs(result['metrics'][key]-reference['metrics'][key])>.02:raise ValueError('Reference reconstruction differs: '+key)
    return result['model_inputs'],delivery['phases'],task_lines,programme

def mobilisation_capacity(people,bc,c):
    """Fund interim leadership and schedule purchased teaching/mentoring capacity."""
    w=bc['workforce'];m=c['mobilisation'];first=min(r['authorised_available_month'] for r in people['recruitment_cohorts'])
    joined=min(r['join_month'] for r in people['recruitment_cohorts'])
    if not m['training_head_start_month']<=m['training_rigs_required_month']<=joined:
        raise ValueError('Training leadership/rigs must precede operating cohorts')
    roles={r['role_id']:r for r in people['roles']};head_month=m['training_head_start_month']
    posts=[dict(role_id=k,posts=1,start_month=0,handover_month=first,
        monthly_loaded_payroll_iqd=roles[k]['annual_loaded_payroll_iqd']/roles[k]['required_fte']/12,
        scope='Interim development authority; operating successor trainees funded separately',named_incumbent=None,named_successor=None,
        signed_handover=None) for k in ('city-director','chief-engineer')]
    posts.append(dict(role_id='development-training-head',posts=1,start_month=head_month,handover_month=first,
        monthly_loaded_payroll_iqd=w['technical_monthly_iqd']*(1+w['employer_cost_fraction']+w['overtime_allowance_fraction']),
        scope='Training procurement, lesson/Arabic review, rig and assessor mobilisation',named_incumbent=None,named_successor=None,signed_handover=None))
    months=defaultdict(lambda:dict(teaching_person_hours=0.,assessment_person_hours=0.,mentor_person_hours=0.,
        existing_trainer_assessor_cash_iqd=0.,additional_mentor_cash_iqd=0.,additional_development_cash_iqd=0.))
    hours_per_month=people['productive_hours_per_fte']/12
    mapping={r['role_id']:('OCC' if r['department']=='occ_remote_assist' else 'STA' if r['department'] in {'station_platform','passenger_service'} else
        'FLT' if r['department']=='fleet_maintenance' else 'CIV' if r['department']=='infrastructure_energy' else 'SUP') for r in people['roles']}
    plans=[]
    for cohort in people['recruitment_cohorts']:
        learners=cohort['offers_required']*(1-w['recruitment_attrition_fraction'])
        groups=math.ceil(learners/w['trainer_learners_per_group'])
        teaching=groups*(w['induction_training_hours']+w['practical_training_hours'])
        assessment=learners*(2-w['assessment_first_pass_fraction'])*w['assessment_hours']
        for month in range(cohort['join_month'],cohort['training_complete_month']):
            months[month]['teaching_person_hours']+=teaching/(cohort['training_complete_month']-cohort['join_month'])
        for month in range(cohort['training_complete_month'],cohort['repeated_assessment_month']):
            months[month]['assessment_person_hours']+=assessment/(cohort['repeated_assessment_month']-cohort['training_complete_month'])
        for month in range(cohort['join_month'],cohort['repeated_assessment_month']):
            months[month]['existing_trainer_assessor_cash_iqd']+=cohort['trainer_assessor_iqd']/(cohort['repeated_assessment_month']-cohort['join_month'])
        for month in range(cohort['repeated_assessment_month'],cohort['authorised_available_month']):
            mentor=learners*hours_per_month/m['trainees_per_external_mentor']
            months[month]['mentor_person_hours']+=mentor
            months[month]['additional_mentor_cash_iqd']+=mentor*(w['technical_monthly_iqd']*(1+w['employer_cost_fraction']+w['overtime_allowance_fraction'])/hours_per_month)
        plans.append(dict(line=cohort['line'],role_id=cohort['role_id'],modules=['BAG-TRN-IND','BAG-TRN-'+mapping[cohort['role_id']]],
            start_month=cohort['join_month'],teaching_end_month=cohort['training_complete_month'],assessment_end_month=cohort['repeated_assessment_month'],
            supervised_end_month=cohort['authorised_available_month'],learner_groups=groups,expected_joined=learners,
            teaching_person_hours=teaching,assessment_person_hours=assessment,actual_equipment=None,appointed_assessor=None,accepted=False))
    for post in posts:
        for month in range(post['start_month'],post['handover_month']):
            months[month]['additional_development_cash_iqd']+=post['posts']*post['monthly_loaded_payroll_iqd']
    monthly=[]
    for month,values in sorted(months.items()):
        monthly.append(dict(month=month,**values,
            minimum_external_teaching_posts=math.ceil(values['teaching_person_hours']/hours_per_month),
            minimum_external_assessor_posts=math.ceil(values['assessment_person_hours']/hours_per_month),
            minimum_external_mentor_posts=math.ceil(values['mentor_person_hours']/hours_per_month),
            qualified_internal_capacity_credited=0,actual_capacity_accepted=False))
    return dict(development_posts=posts,training_rigs_required_month=m['training_rigs_required_month'],rig_capital_usd=None,
        cohort_lesson_schedule=plans,monthly=monthly,role_coverage=[dict(role_id=r['role_id'],required_fte=r['required_fte'],
            concurrent_posts=r['minimum_concurrent_posts'],annual_workload_person_hours=r['annual_workload_person_hours'],
            lesson_modules=['BAG-TRN-IND','BAG-TRN-'+mapping[r['role_id']]],native_employee=None,rest_roster_accepted=False) for r in people['roles']],
        existing_trainer_assessor_cash_iqd=sum(r['trainer_assessor_iqd'] for r in people['recruitment_cohorts']),
        additional_preopening_cash_iqd=sum(r['additional_mentor_cash_iqd']+r['additional_development_cash_iqd'] for r in monthly),
        named_handover_accepted=False,roster_released=False,
        limitations=['Teaching/assessment hours schedule the existing contracted allowance; it is not charged a second time',
            'Independent external mentors and interim leadership add cash before opening; EPC credit remains explicitly unaccepted',
            'Operating recruits are not credited as qualified teachers, assessors or mentors',
            'Hour-derived staffing is a minimum: rig access, competence, concurrent observation and daily/rest rosters remain unaccepted',
            'Factory production curricula and workforce remain in factory procurement; these are operating cohorts'])

def preopening_cash(people,horizon,fx,options):
    rows=[0.]*horizon
    for cohort in people['recruitment_cohorts']:
        for month in range(cohort['join_month'],cohort['authorised_available_month']):
            rows[month]+=cohort['paid_preopening_training_iqd']/fx/(cohort['authorised_available_month']-cohort['join_month'])
        for month in range(cohort['join_month'],cohort['repeated_assessment_month']):
            rows[month]+=cohort['trainer_assessor_iqd']/fx/(cohort['repeated_assessment_month']-cohort['join_month'])
    for cohort in people['temporary_commissioning_cohorts']:
        for month in range(cohort['start_month'],cohort['end_month']):
            rows[month]+=cohort['reference_payroll_iqd']/fx/(cohort['end_month']-cohort['start_month'])
    for row in people['development_mobilisation']['monthly']:
        rows[row['month']]+=(row['additional_development_cash_iqd']+row['additional_mentor_cash_iqd'])/fx
    return [value*(1+options['fares']['opex_inflation'])**(month//12) for month,value in enumerate(rows)]

def opening_factory_replay(paths,phases,settings):
    payload=json.loads(gzip.decompress(paths['operations'].read_bytes()));original=payload['manufacturing_tasks']
    by_line=defaultdict(dict)
    for row in original:
        if row['asset_type']=='rolling-stock':
            by_line[row['line']][row['asset_id']]=min(row['planned_start_day'],by_line[row['line']].get(row['asset_id'],float('inf')))
    selected=set();added=[];lineage={}
    for phase in phases['lines']:
        assets=sorted(by_line[phase['line']],key=lambda a:(by_line[phase['line']][a],a))
        selected.update(assets[:phase['opening_trainsets']])
        for index in range(max(0,phase['opening_trainsets']-len(assets))):
            source=[r for r in original if r['asset_id']==assets[-1]]
            new_id=assets[-1]+f'-OPENING-EXTRA-{index+1}'
            uid_map={r['manufacturing_uid']:r['manufacturing_uid'].replace(r['asset_id'],new_id) for r in source}
            for row in source:
                clone=deepcopy(row);clone['asset_id']=new_id;clone['manufacturing_uid']=uid_map[row['manufacturing_uid']]
                clone['planned_start_day']+=1
                for key in ('predecessor_uids','schedule_predecessor_uids'):
                    clone[key]=';'.join(uid_map.get(p.strip(),p.strip()) for p in row[key].split(';') if p.strip())
                lineage[clone['manufacturing_uid']]=row['manufacturing_uid'];added.append(clone)
    tasks=[deepcopy(r) for r in original if r['asset_type']!='rolling-stock' or r['asset_id'] in selected]+added
    kept={r['manufacturing_uid'] for r in tasks};lanes={}
    # Rebuild the selected factory queues; dropped procurement is not secretly
    # manufactured through the old full-fleet resource predecessor chain.
    for row in sorted(tasks,key=lambda r:(r['planned_start_day'],r['manufacturing_uid'])):
        pred=[p.strip() for p in row['schedule_predecessor_uids'].split(';') if p.strip() and p.strip() in kept]
        if row['asset_type']=='rolling-stock':
            pred=[p for p in pred if p!=row['resource_predecessor_uid']]
            lane=(row['resource_pool'],row['resource_lane'])
            if lane in lanes:pred.append(lanes[lane])
            lanes[lane]=row['manufacturing_uid']
        row['schedule_predecessor_uids']=';'.join(dict.fromkeys(pred))
    factory=read(paths['factory']);delivery=schedule(tasks,factory,settings)
    return dict(delivery=delivery,added_task_lineage=lineage,
        selected_rolling_task_uids=[r['manufacturing_uid'] for r in tasks if r['asset_type']=='rolling-stock'],
        selected_trainsets=len(selected)+len({r['asset_id'] for r in added}),
        retained_factory_capital_usd=factory['budgeted_plant_direct_usd']+factory['budgeted_plant_epc_usd'],
        factory_ready_month=factory['readiness_months_from_ntp'],factory_repriced=False,accepted=False,
        finance_dates_policy='Open no earlier than retained civil dates and replayed fleet acceptance; propagate later dates to all operating cash',
        limitations=['Planned selected asset IDs are not purchase orders or accepted train deliveries',
            'Full expansion-capable factory/equipment retained and paid once; no invented cheaper factory',
            'Factory queues replay selected orders and one new spare; civil scope and independent acceptance remain unchanged'])

def reconciled_finance(inputs,phases,task_lines,depots,family,people,opening_people,energy,opening_energy,first_phase,batteries,opening_batteries,c,opening_factory):
    config=inputs['config'];options=inputs['options'];fx=config['model']['iqd_per_usd'];eligible=set(options['green']['candidate_buckets'])
    base_contracts=inputs['contracts']+inputs['factory_contracts'];costs=read(CITY/'engineering/finance/summary.json')['annual_opex_usd']['components']
    cases={};rate=(1+config['model']['discount_rate'])*(1+options['fares']['general_price_inflation'])-1
    for name in ('reference','reconciled_full_fleet','reconciled_fixed_original_government','reconciled_without_uncommitted_income','opening_fleet_supply_scaled','contracted_solar','installed_energy_supply_bound','simple_span_bearing_index'):
        cfg=deepcopy(config);opt=deepcopy(options);contracts=deepcopy(base_contracts);op=deepcopy(inputs['operating']);is_reference=name=='reference';opening=name=='opening_fleet_supply_scaled';ppa=name=='contracted_solar'
        installed=name=='installed_energy_supply_bound'
        case_phases=opening_factory['delivery']['phases'] if opening else phases
        if opening:op=deepcopy(opening_factory['operating_inputs']['operating'])
        line_openings={r['line']:r['opening_month'] for r in case_phases}
        first=min(line_openings.values());last=max(line_openings.values())
        ppl=opening_people if opening else people;power=opening_energy if opening else energy;prepay=preopening_cash(ppl,len(op),fx,opt)
        energy_ratios={p['line']:sum(r['installed_deliverable_traction_upper_bound_kwh'] for r in power['cases']['reference']['sites'] if r['line']==p['line'])/sum(r['allocated_traction_kwh'] for r in power['cases']['reference']['sites'] if r['line']==p['line']) for p in phases}
        energy_config=tomllib.loads((ROOT/'lib/templates/baghdad-delivery-baseline.toml').read_text())['energy']
        cap_inclusions=[]
        if not is_reference:
            contracts=[r for r in contracts if r['bucket']!='depots' and not (ppa and r['bucket']=='solar_plant')]
            for site in depots['alternatives']['workload_bays']['sites']:
                line=site['line'];amount=sum(r['reference_cost_usd'] for r in depots['alternatives']['workload_bays']['items'] if r['site']==site['station'])
                energy_amount=sum(r['reference_cost_usd'] for r in depots['alternatives']['workload_bays']['items'] if r['site']==site['station'] and r['scope'].startswith('depot-'))
                amount-=energy_amount*c['model']['depot_energy_allowance_credit_fraction']
                finish=(line_openings[line]-2)*260/12-30;start=max(0,finish-22*260/12)
                contracts.append(dict(bucket='reconciled_depot',budget_usd=amount,imported_share=c['model']['depot_import_share'],planned_start_day=int(start),planned_finish_day=int(finish)))
            if name=='simple_span_bearing_index':
                design=tomllib.loads((CITY/'design.toml').read_text())
                civil_cost=tomllib.loads((ROOT/'lib/templates/civil-cost-model.toml').read_text())
                contracts+=bearing_index_delta_contracts(base_contracts,task_lines,design,civil_cost)
            extra_direct=sum(r['budget_usd'] for r in contracts if r['bucket'] in {'reconciled_depot','bearing_index_delta'})-8000000
            extra_epc=max(0,extra_direct)*c['model']['incremental_epc_fraction']
            extra_qualification=family['qualification_reference_budget_usd']*(1-c['model']['qualification_factory_credit_fraction'])
            for bucket,amount in [('incremental_epc',extra_epc),('incremental_qualification',extra_qualification)]:
                if amount:contracts.append(dict(bucket=bucket,budget_usd=amount,imported_share=0,planned_start_day=0,planned_finish_day=18*260//12-30))
            if opening:
                original_contracts={r['manufacturing_uid']:r for r in contracts if r['bucket']=='rolling_stock'}
                selected=set(opening_factory['selected_rolling_task_uids'])
                contracts=[r for r in contracts if r['bucket']!='rolling_stock' or r['manufacturing_uid'] in selected]
                for uid,source in opening_factory['added_task_lineage'].items():
                    if source in original_contracts:
                        clone=deepcopy(original_contracts[source]);clone['manufacturing_uid']=uid;contracts.append(clone)
                timings={r['manufacturing_uid']:r for r in opening_factory['delivery']['tasks']}
                selected_task_lines={r['manufacturing_uid']:r['line'] for r in opening_factory['delivery']['tasks']}
                line_budgets=defaultdict(float)
                for contract in contracts:
                    if contract['bucket']=='rolling_stock':line_budgets[selected_task_lines[contract['manufacturing_uid']]]+=contract['budget_usd']
                # Original task cost weights differ slightly by line. Retain invoice
                # timing, but price the reduced fleet at the declared consist cost.
                ratios={r['line']:r['opening_trainsets']*family['cost_allocations_reconcile_usd']/line_budgets[r['line']] for r in first_phase['lines']}
                for contract in contracts:
                    if contract['bucket']=='rolling_stock':
                        uid=contract['manufacturing_uid'];contract['budget_usd']*=ratios[selected_task_lines[uid]]
                        contract['planned_start_day']=math.floor(timings[uid]['start_hour']/8)
                        contract['planned_finish_day']=math.ceil(timings[uid]['end_hour']/8)-1
            cap_inclusions=[dict(bucket=r['bucket'],budget_usd=r['budget_usd']) for r in contracts if r['bucket'] in {'reconciled_depot','incremental_epc','incremental_qualification','bearing_index_delta'}]
        capital=capital_projection(contracts,cfg,eligible)
        # Preserve factory draw shares used by the common reserve/fee calculation.
        for month,row in capital_projection(inputs['factory_contracts'],cfg,eligible).items():capital[month].update(factory_capex=row['capex'],factory_imports=row['imports'])
        if name=='reconciled_fixed_original_government':
            cfg['capital_sources']=dict(government_share=.25*sum(r['capex'] for r in inputs['capital'].values())/sum(r['capex'] for r in capital.values()),chinese_import_share=.5,government_import_share=.5,residual_bond_share=.75)
        line_pay=defaultdict(float);pay_by_role={r['role_id']:r for r in ppl['roles']}
        for unit in ppl['units']:
            role=pay_by_role[unit['unit'].split(':')[0]]
            line_pay[unit['line']]+=unit['required_fte']*role['annual_loaded_payroll_iqd']/role['required_fte']/fx
        topup_by_month=defaultdict(float)
        for row in (opening_batteries if opening else batteries)['monthly']:topup_by_month[row['month']]+=row['inflation_topup_required_usd']
        component_rows=[]
        for row in op:
            month=row['month'];index=(1+opt['fares']['opex_inflation'])**(month//12)
            active=first<=month<last+cfg['model']['operating_years']*12
            opened=sum(p['weight'] for p in case_phases if month>=p['opening_month']) if active else 0
            weight=cfg['model']['phased_fixed_opex_share']+(1-cfg['model']['phased_fixed_opex_share'])*opened if active else 0
            payroll=sum(pay for line,pay in line_pay.items() if month>=line_openings[line])*index/12 if active else 0
            power_annual=power['cases']['reference']['annual_firm_energy_cost_usd']
            if installed:
                power_annual-=sum(r['unserved_kwh']*energy_config['import_purchase_usd_per_kwh']+r['grid_upgrade_minimum_kw']*energy_config['connection_usd_per_kw_year'] for r in power['cases']['reference']['sites'])
            if ppa:
                utility_generation=sum(r['gross_utility_generation_kwh'] for r in power['cases']['reference']['sites'])
                power_annual+=utility_generation*.045-costs['solar_plant_maintenance']
            power_cash=power_annual*weight*index/12
            additional=0.;supply_ratio=1.
            if not is_reference:
                additional=payroll-costs['labour']*weight*index/12+power_cash-costs['solar_plant_maintenance']*weight*index/12
                additional+=prepay[month]*(1-c['model']['preopening_epc_credit_fraction'])+topup_by_month[month]
                if opening or installed:
                    if opening:
                        reduction=costs['rolling_stock_maintenance_including_battery_renewal_reserve']*(1-first_phase['opening_fleet']/first_phase['baseline_fleet'])
                        additional-=reduction*weight*index/12
                    ramp=cfg['model']['revenue_ramp'];denom=numerator=0.
                    for phase in case_phases:
                        if month>=phase['opening_month']:
                            r=next(r for r in first_phase['lines'] if r['line']==phase['line'])
                            w=phase['weight']*ramp[min((month-phase['opening_month'])//12,len(ramp)-1)]
                            denom+=w;numerator+=w*(energy_ratios[phase['line']] if installed else r['opening_daily_train_km']/r['baseline_daily_train_km'])
                    supply_ratio=numerator/denom if denom else 1.
                    for key in ('fare_revenue_usd','nonfare_revenue_usd','revenue_usd'):row[key]*=supply_ratio
                    row['additional_income_multiplier']=supply_ratio
                row['opex_usd']+=additional
            if not is_reference:
                row['chinese_commitment_fee_usd']=0
                cohort=sorted(m for m,r in capital.items() if m//12==month//12 and r['imports']>0)
                if cohort and month>=cohort[0]:row['chinese_commitment_fee_usd']=sum(.5*capital[m]['imports'] for m in cohort if m>month)*cfg['chinese_export_credit']['undrawn_commitment_fee']/12
            component_rows.append(dict(month=month,opening_weight=opened,base_opex_weight=weight,
                workload_payroll_usd=payroll,firm_energy_usd=power_cash,preopening_cash_usd=prepay[month] if not is_reference else 0,
                asset_reserve_topup_usd=topup_by_month[month] if not is_reference else 0,
                incremental_opex_usd=additional,supply_income_multiplier=supply_ratio))
        extras=name!='reconciled_without_uncommitted_income'
        result=simulate(capital,op,cfg,opt,green='blended' if extras else None,extras=extras,
            bridge_rate=opt['liquidity']['concessional_annual_rate'],bridge_fee=opt['liquidity']['concessional_draw_fee'],repayment_policy='cost_priority')
        if name=='simple_span_bearing_index':
            result['bearing_index_delta_contracts']=[r for r in contracts if r['bucket']=='bearing_index_delta']
        result.update(capital_components=cap_inclusions,opex_components=component_rows,operating_phases=deepcopy(case_phases),
            service_basis='Original annual-netting comparator, unverified service' if is_reference else 'Installed energy/charger throughput upper bound; trip feasibility remains unaccepted' if installed else 'Conditional service requiring priced/accepted electrical upgrades',
            shareholder_distributions=dict(modelled_total_dividends_iqd=0,dividend_permission=False,
                retained_project_cash_iqd=result['metrics']['terminal_cash_iqd'],
                company_distributable_after_tax_profit_iqd=None,
                basis='Surpluses retained after debt/reserve/buffer waterfall; audited distributable profits, covenants and approval unresolved'),
            company_cash_npv_before_finance_usd=sum((r['revenue_usd']-r['opex_usd']-capital.get(r['month'],{}).get('capex',0))/(1+rate)**(r['month']/12) for r in op),
            nominal_discount_rate=rate,physical_energy_upgrade_capex_usd=None,unpriced_scope_included=False,
            external_provider_plant_capex_reference_usd=read(CITY/'engineering/finance/summary.json')['capex_usd']['timetable_sized_dedicated_solar'] if ppa else 0,
            comparable_total_resource_npv_usd=None,government_policy='Fixed original cash ceiling' if name=='reconciled_fixed_original_government' else '25% of scenario capital; change requires appropriation',
            uncommitted_additional_income_included=extras,financing_committed=False,operational_release=False,
            deferred_expansion_fleet_funding_usd=None if opening else 0.,expansion_demand_trigger_dates=None,
            limitations=['Unquoted depot origin/EPC/overlap assumptions; land, duties, utility and electrical upgrades remain unpriced',
                'Fares have existing 5% indexation and elasticity; no new actual OD or lender commitments',
                'Only supplemental/topup cash is added: payroll/solar OPEX and depot allowance replaced once',
                'Factory 18-month and finite-resource baseline unchanged; no reduction in factory cost from fewer trains',
                'Opening fleet case reduces receipts with supply; expansion fleet/dates remain an unfunded future scope',
                'Cash appraisal uses budgeted reserve contributions; it is not a complete economic-resource appraisal'])
        result['metrics']['debt_clearance_without_unfunded_support_month']=result['metrics']['all_debt_cleared_month'] if result['metrics']['uncovered_support_iqd']/fx<.02 else None
        if name=='reconciled_full_fleet':
            base_fare=read(CITY.parent/'finance/baghdad-programme.json')['comparison']['fare_iqd'];sweep=[]
            for fare in c['corridors']['base_fare_sensitivities_iqd']:
                ratio=fare/base_fare;demand_ratio=min(opt['fares']['maximum_demand_multiplier'],ratio**opt['fares']['price_elasticity'])
                priced=deepcopy(op)
                for row in priced:
                    row['fare_revenue_usd']*=ratio*demand_ratio;row['nonfare_revenue_usd']*=demand_ratio
                    row['revenue_usd']=row['fare_revenue_usd']+row['nonfare_revenue_usd']
                trial=simulate(capital,priced,cfg,opt,green='blended',extras=True,
                    bridge_rate=opt['liquidity']['concessional_annual_rate'],bridge_fee=opt['liquidity']['concessional_draw_fee'],repayment_policy='cost_priority')
                cash_npv=sum((r['revenue_usd']-r['opex_usd']-capital.get(r['month'],{}).get('capex',0))/(1+rate)**(r['month']/12) for r in priced)
                sweep.append(dict(base_fare_iqd=fare,paid_demand_multiplier=demand_ratio,
                    monthly_44_trip_income_share=fare*c['corridors']['affordability_trip_count_monthly']/c['corridors']['income_proxy_monthly_iqd'],
                    company_cash_npv_before_finance_usd=cash_npv,
                    debt_clearance_without_unfunded_support_month=trial['metrics']['all_debt_cleared_month'] if trial['metrics']['uncovered_support_iqd']/fx<.02 else None,
                    peak_gap_debt_iqd=trial['metrics']['peak_supplemental_balance_iqd'],
                    terminal_gap_debt_iqd=trial['metrics']['terminal_supplemental_balance_iqd'],
                    uncovered_support_iqd=trial['metrics']['uncovered_support_iqd'],
                    metrics=trial['metrics'],actual_od_and_affordability_accepted=False,adopted=False))
            result['fare_sensitivities']=sweep
        cases[name]=result
    return cases

def closure_packets(scope,depots,bom,corridors,people):
    """Reviewable field-work forms; preparing a form does not obtain its evidence."""
    forms=[]
    for item in scope['rows']:
        if item['base_estimate_usd'] is None:
            forms.append(dict(id=item['wbs'],kind='scope-inclusion-quotation',quantity=None,unit=None,unit_rate=None,
                currency='IQD-or-USD-quote-required',price_date=None,quotation_reference=None,supplier_or_estimator=None,
                included_in_existing_wbs=None,baseline_credit_usd=None,tax_and_duty_treatment=None,
                physical_dependency=None,actual_owner=None,independent_acceptance=None))
    requests=[dict(part_id=r['id'],parent=r['parent'],quantity_per_train=r['quantity_per_train'],
        programme_quantity=r['network_quantity'],supplier=None,origin_country=None,manufacturing_location=None,
        drawing_revision=None,interface_revision='M6-A-DRAFT',quoted_unit_price=None,quoted_currency=None,
        price_date=None,delivery_month=None,incoterms=None,duties_excluded=None,warranty=None,
        qualification_evidence=None,local_assembly_labour_hours=None,actual_payment_terms=None,
        chinese_credit_eligible=None,accepted=False) for r in bom['parts']]
    methods={
        'ESTIMATE':['Register every invoice-level use and inclusion decision','Match exclusions and credits to signed WBS scope','Collect price/currency/date/origin and conditions','Calibrate dependencies/risk using investigations','Reconcile capital, funding and operating cash independently'],
        'DEPOT':['Survey parcel, datum, title, utility and access','Freeze point radii/throat, track IDs/lengths and train slots','Locate workshop, PV/BESS, rescue, quarantine, drainage and egress','Confirm supplier footprints and installed electrical scope','Replay selected startup/returns and obtain independent physical signoff'],
        'DEMAND':['Count OD and time-of-day loads across corridors','Separate fare-paying boardings and transfers','Survey walk/feeder access, disability needs and affordability','Price standalone corridor and shared dependencies','Choose corridor only after demand/civil/energy comparison'],
        'PRODUCT':['Freeze six-car child parts, mass/axles and joint/interface drawings','Request compatible bogie/battery/door/glazing/control offers','Measure labour, rework and factory test-path cycle','Execute first article and qualification work packages','Release serial manufacture only through actual authorities'],
        'PEOPLE':['Measure task/post and relief workloads','Confirm local grade/employer/rest and recruitment terms','Nominate actual managers/assessors and controlled lesson revisions','Assess practical exercises and obtain scoped authorisation','Fill and recheck roster/permits/tools/materials at actual task start'],
        'PUBLICATION':['Restore exact archive-bound test input in empty checkout','Run calculation, permissions, recovery and scale checks','Reconcile headline/source/output/archive hashes','Publish controlled proposal and reader book','Keep field acceptance distinct from repository verification']}
    descriptions={
        'ESTIMATE':'Scope, reference/cost-reconciled funding, six-month subscriptions and reserve cash',
        'DEPOT':'Nine local planning layouts, labelled storage tracks/slots and yard slab manufacture quantities',
        'DEMAND':'Nine standalone operating break-even comparisons and OD/site investigation forms',
        'PRODUCT':'Six-car child parts/interface RFQs, 12m qualification WBS and actual quote/applicability fields',
        'PEOPLE':'Task-derived maintenance, reserve ledger, backward cohorts, practical lesson cards and rest-limited pilot slots',
        'PUBLICATION':'Exact-input restore, automated checks, native read-only ERP probe and isolated backup recovery receipt'}
    baseline=read(CITY/'engineering/delivery-baseline/90-day-work-programme.json')
    work=[]
    for item in baseline['work_packages']:
        key=item['id'].split('-')[-1]
        work.append(dict(item,repository_deliverable=descriptions[key],procedures=methods[key],
            repository_artifacts_prepared=True,field_work_completed=False,actual_accepted_evidence=None,
            status='repository-package-prepared-field-acceptance-open',external_contact_authorised=False))
    return dict(scope_inclusion_forms=forms,supplier_rfq_forms=requests,work_packages=work,
        actual_quotes=0,actual_surveyed_parcels=0,actual_demand_counts=0,named_appointments=0,
        required_actual_evidence=['Land/title/survey and utilities','Supplier/interface/cost/origin/payment evidence',
            'OD/fares/access and tenant enquiries','Appointments/local employment/assessor authorities',
            'Iraqi approvals, appropriations, actual subscriptions and loan terms'],
        organisational_approval=False,operational_release=False)

def maintenance_register(design,scenario,intervals):
    quantities={'rolling-stock':sum(r['trainset_count'] for r in design['fleets']),
        'stations':len(design['stations']),'energy':len(scenario['sites']),
        'track-civil':sum(r['length_m'] for r in design['lines'])/1000}
    return [dict(row,programme_asset_family_quantity_reference=quantities.get(row['domain']),
        quantity_unit='route-km' if row['domain']=='track-civil' else 'family positions; not installed asset records',
        measured_task_duration_hours=None,parts_quantity=None,parts_cost=None,
        native_asset=None,native_maintenance_plan=None,assigned_employee=None,
        work_permit=None,independent_handback=None,accepted=False) for row in intervals]

def startup_alternatives(design,stabling):
    rows=[]
    for fleet in design['fleets']:
        points={(r['station'],r['heading']) for r in stabling['hybrid_allocation']['allocations'] if r['line']==fleet['line'] and r['location_type']=='station'}
        points.update((r['station'],r['heading']) for r in stabling['hybrid_allocation']['missing_morning_directions'] if r['line']==fleet['line'])
        stations=len({station for station,heading in points});required=len(points)
        deficit=max(0,required-fleet['peak_count']);extra_spares=max(0,math.ceil(required*.1)-fleet['spare_count']) if deficit else 0
        rows.append(dict(line=fleet['line'],frozen_baseline_dispatch_direction_count=required,
            frozen_dispatch_points=[dict(station=station,heading=heading) for station,heading in sorted(points)],
            baseline_revenue_trains=fleet['peak_count'],revenue_position_deficit=deficit,
            maximum_both_direction_start_stations_without_using_reserves=min(stations,fleet['peak_count']//2),
            minimum_additional_revenue_trains=deficit,additional_10_percent_spares=extra_spares,
            additional_train_reference_capital_usd=(deficit+extra_spares)*trainset_reference_cost(),
            selected_start_station_ids=None,turnback_charger_and_cycle_accepted=False,
            extra_depot_capacity_and_funding_usd=None,adopted=False,operational_release=False))
    return dict(cases=rows,alternatives=['Select fewer stations for two-direction startup and replay access/cycles',
        'Procure additional revenue trains and spares, then reprice depot/factory/energy/finance'],
        scope='Frozen original candidate station-direction counts only; adding trains must not silently expand selected dispatch points. No proof of feasible startup or movement authority')

def lesson_cards(people):
    exercises={
        'IND':('Find a superseded method and an unapproved access request','لا تبدأ العمل قبل التحقق من التعليمات والتصريح'),
        'OCC':('Radio loss and conflicting/stale authority; escalation and human handback','تحقق من الاتصال والصلاحية وأبلغ المشرف عند وجود خلل'),
        'STA':('Wheelchair assistance with boarding gap and crowd/evacuation constraint','حافظ على مسار الإخلاء وساعد الركاب وفق التعليمات المعتمدة'),
        'FLT':('Battery insulation alarm; controlled isolation, diagnosis and independent checks','لا تفتح معدات البطارية قبل العزل والتحقق من سلامة العمل'),
        'CIV':('Expired track/electrical permit, damaged drain and unsafe inspection access','تحقق من تصريح العمل والعزل وإمكانية الوصول الآمن'),
        'FAC':('Wrong part revision, tool calibration overdue and failed measurement','تحقق من رقم الجزء والمراجعة وصلاحية معايرة الأداة'),
        'SUP':('Absent assessor, rested-but-unqualified worker and incomplete handback','لا تسند المهمة دون التحقق من الكفاءة والتصريح والموارد')}
    rows=[]
    for module in people['curricula']:
        identifier=module['module_id'];key=next((k for k in exercises if k in identifier),None)
        if key is None:
            # Curricula use stream names in their controlled IDs.
            mapping={'common-induction':'IND','occ-incident':'OCC','stations-accessibility':'STA','fleet-maintenance':'FLT','civil-energy':'CIV','factory-production':'FAC','supervisors-assessors':'SUP'}
            key=mapping[identifier]
        exercise,arabic=exercises[key]
        rows.append(dict(module=identifier,revision='A-DRAFT',prerequisites=module['prerequisites'],
            practical_exercise=exercise,apparatus=module['equipment'],controlled_method=None,
            candidate=None,assessor=None,assessor_authority=None,attendance_record=None,
            critical_observations=[dict(step=step,observed=None,passed=None) for step in module['assessment_criteria']],
            arabic_draft_instruction=arabic,arabic_native_review=None,practical_assessment_result=None,
            task_asset_location_authorisation=None,retraining_triggers=module['retraining_triggers'],
            attendance_is_competence=False,operational_release=False))
    return rows

def report_files(layouts,bom,energy,maintenance_data,batteries,corridors,cases,roster,packets):
    ref=energy['cases']['reference'];finance_rows=[]
    for name,case in cases.items():
        m=case['metrics'];finance_rows.append((name,f"{m['total_capital_usd']/1e9:.3f}",f"{m['government_capital_usd_equivalent']/1e9:.3f}",f"{m['peak_supplemental_balance_iqd']/1e12:.3f}",f"{m['uncovered_support_iqd']/1e12:.3f}",m['debt_clearance_without_unfunded_support_month'],f"{case['company_cash_npv_before_finance_usd']/1e9:.3f}"))
    return {
        'README.md':'''# Baghdad remaining-work delivery packages

This continuation completes repository calculations, concept layouts, RFQ/field forms, financial sensitivities and competence/recovery checks. **It does not complete surveys, obtain quotes, appoint people, sign leases/loans or release a railway.** The original financing and engineering examples remain their controlled baseline. All alternatives are unquoted/uncommitted and retain unknown costs.

- [Depot track/slot layout and yard slab production](DEPOTS-SLAB-MANUFACTURE.md)
- [Six-car child parts, interfaces and supplier request forms](SIX-CAR-PROCUREMENT.md)
- [Per-site hourly energy and upgrade requirements](SITE-ENERGY.md)
- [Maintenance tasks, renewal dates and restricted reserve cash](MAINTENANCE-RENEWALS.md)
- [Comparable standalone corridor break-even and field investigations](CORRIDOR-COMPARISON.md)
- [Reconciled monthly funding, six-month bonds/loans and repayment](FINANCE-RECONCILIATION.md)
- [Practical training, department/unit allocation and rest-limited roster](WORKFORCE-PILOT.md)
- [Remaining evidence and six native ERP work packages](FIELD-WORK-PACKETS.md)

Run `.venv/bin/python tools/automation/baghdad_delivery_closure.py`, then rebuild the proposal. `--check` rejects source/output drift. Existing `bootstrap_baghdad_tests.py` restores the exact test input. Native personal records and recovery receipts remain private in `var/erpnext/`.
''',
        'DEPOTS-SLAB-MANUFACTURE.md':f'''# Nine depot/storage design studies and Iraqi slab manufacture

[Located track and slot register](depot-layouts.json) identifies **{layouts['total_storage_positions']} storage positions**, {len(layouts['tracks'])} tracks, {layouts['total_usable_track_m']:,.0f} usable track metres, {layouts['rail_m']:,.0f} rail metres and {layouts['fastener_seat_kits']:,} reference fixation-seat kits. {layouts['concrete_reference_m3']:,.1f} m³ concrete is a geometric reference for yard slabs, excluding foundations, reinforcement, grout/stray-current systems and point panels. Existing track/package costs are not supplemented by these quantities a second time.

{table(['Line','Slots','Storage tracks','Workshop bays','Layout'],[(s['line'],s['stabling_positions'],s['storage_tracks'],s['workshop_bays'],f"[SVG](depot-{s['line']}.svg)") for s in layouts['sites']])}

Drawings use local planning coordinates and distinguish storage slots from workshop bays. Rectangular packing can include unused end positions; it creates no acquired parcel or released alignment. Throat radii, bypass/escape tracks, drainage/outfalls, road/fire/evacuation access, utilities, lifting/inspection/rescue/quarantine areas and grid connection need actual surveys and supplier footprints. Line 6 requires about 33,333m² PV module area; no 4,000m² canopy is credited as adequate.

The yard-only slab production study requires **{layouts['slab_factory']['minimum_parallel_mould_cells']} parallel mould cells** at a one-working-day cycle/75% utilisation, ready month 18 and delivering two months before each opening. Its [prefix-capacity programme](depot-layouts.json) includes cut/end panels and never casts beyond usable lengths. Moulds, curing/QA, batching, reinforcement, transport, lifting and installation require quantities/quotes and measured cycles. Factory CAPEX is null, not free. Main-line slab manufacture is a different existing production requirement; these cells cannot be represented as its total capacity. Iraqi casting/assembly remains a proposed procurement route, not a qualified plant.
''',
        'SIX-CAR-PROCUREMENT.md':f'''# Six-car child parts and procurement/qualification work

[Child parts](six-car-child-bom.csv) expand the eight parent allocations without duplicating their USD {bom['parent_total_per_train_usd']:,.0f}/train budget. Body modules, 12 bogies, 24 wheelsets/48 wheels, battery interfaces, traction controllers, doors/windows, mounting rails, lighting and thermal/trainline interfaces derive from the actual six-car system counts. Harnesses, protection, braking, redundant control and installed sensing quantities remain null where the supplier/design schedule is absent. Price, mass, drawing and applicability are not inferred from the LM3 reference.

[Supplier RFQ forms](supplier-rfq.csv) require drawing/revision, interface, price/currency/date, country/invoice origin, delivery, duties, warranty, payment terms, local labour and actual Chinese-credit eligibility. None has been sent or answered. [Qualification work packages](six-car-procurement.json) retain the existing USD 12m unquoted reference and unresolved overlap with the factory's USD 20m design/training allowance. Routine assembly/QA wages already in train procurement are not added to OPEX. Software/runtime/bench evidence remains observation/reference evidence until the target family and installed interfaces are qualified.
''',
        'SITE-ENERGY.md':f'''# Chronological site-limited energy and installed upgrades

Each station retains its own storage capacity/power and grid limit. Timetable train-km allocate duty between lines; installed charger kW allocate duty within a line. **This is a synthetic allocation, not measured charger events or a queue/feeder acceptance test.** The utility plant is allocated by duty, on-site PV has no wheeling loss, and utility PV has the explicit loss/charge. Each node conserves hourly energy and preserves losses, curtailment, shortages and SoC.

{table(['Weather','Imports GWh','Unserved GWh','Firm energy services USD m/year','Required grid upgrade MW','Charger overload MW'],[(name,f"{case['grid_import_kwh']/1e6:.1f}",f"{case['unserved_kwh']/1e6:.1f}",f"{case['annual_firm_energy_cost_usd']/1e6:.3f}",f"{case['grid_upgrade_minimum_kw']/1000:.3f}",f"{case['charger_upgrade_minimum_kw']/1000:.3f}") for name,case in energy['cases'].items()])}

The firm-service cash sensitivity buys unmet energy and pays the increased connection charges. It **requires physical connection and charger upgrades whose capital is unpriced**. It does not claim a trip can be served by paying a bill. [Site totals](site-energy.json) and reference line-hourly ledgers expose every node requirement. Whole-grid pooling is removed; within-line duty allocation, site transformer/feeder limits, rights/outages, charging times, installed storage ageing and weather still need measurements. Original annual-netting finance remains unchanged, with no export income or energy ownership proceeds invented.
''',
        'MAINTENANCE-RENEWALS.md':f'''# Task-derived maintenance and reserve cash

[Task workload](maintenance-tasks.csv) covers daily/weekly/monthly inspections, every-roundtrip safety/diagnostic checks, wheel reprofile at 150,000km, bogie overhaul at 600,000km and body overhaul at ten years. Six-car quantities are 24 wheelsets and 12 bogies/train. Reference workload is {maintenance_data['mechanical_person_hours']:,.0f} mechanical and {maintenance_data['electrical_person_hours']:,.0f} electrical person-hours/year, compared with existing workload allowances {maintenance_data['existing_mechanical_workload_hours']:,.0f} / {maintenance_data['existing_electrical_workload_hours']:,.0f}. Durations, defects, access queues, equipment, parts and non-fleet tasks remain unmeasured; lower reference hours do not authorise staff reductions.

Battery replacement stays on the existing **12-year** cycle. Reference annual reserve is USD {maintenance_data['reference_annual_battery_reserve_usd']/1e6:.3f}m within the existing USD {maintenance_data['existing_total_rolling_maintenance_and_reserve_usd']/1e6:.3f}m rolling maintenance envelope. [Monthly reserve ledger](battery-reserve-monthly.csv) separates indexed contributions, replacement withdrawals, required top-ups and closing restricted cash. At 5% inflation/zero reserve interest, reference top-ups total USD {batteries['total_topups_usd']/1e6:.3f}m nominal; terminal restricted cash is USD {batteries['terminal_restricted_cash_usd']/1e6:.3f}m. It cannot repay loans/bonds or become terminal sale income. The replacement bill is not added to annual reserve spending a second time.

Initial 2% battery-spare stock is USD {maintenance_data['initial_battery_spare_reference_usd']/1e6:.3f}m reference; existing allowance inclusion is unknown. Serial-specific service/mileage/cell-health dates must replace line-opening proxies. Native Asset Maintenance/Asset Repair, calibration/parts and independent handback records remain required. No actual asset, spare, Work Order or accepted Job Card is invented.
''',
        'CORRIDOR-COMPARISON.md':'''# Comparable standalone opening corridors

Each corridor pays for its own workload/shift cover including central leadership, existing maintenance/solar shares and per-site energy service assumptions. The price test uses the same current fare, 20% capacity-use sensitivity and existing station commercial revenue allocation. Debt, tax, land, parcel-specific works, interchange effects and grid upgrades remain outside this operating-only break-even. OD and access evidence remain null, so no commercial rank or first-corridor selection is fabricated.

'''+table(['Line','Fleet','FTE','OPEX USD m/year','Operating-neutral paid trips m/year','Neutral capacity use','Fare at 20% use IQD'],[(r['line'],r['opening_fleet'],r['reference_standalone_fte'],f"{r['reference_annual_opex_usd']/1e6:.3f}",f"{r['operating_break_even_paid_trips']/1e6:.3f}",f"{r['operating_break_even_capacity_use']:.1%}",f"{r['operating_break_even_fare_iqd']:.0f}") for r in corridors['cases']])+'''

[Detailed cases and investigation forms](corridor-comparison.json) retain fares, affordability, OD/transfers, paid demand, pedestrian/feeder catchments, interchange and standalone debt-service fields. The affordability column prices 44 monthly trips against the historical model income proxy; it is not surveyed disposable income. Lower vehicle procurement reduces service/capacity; unchanged receipts and earlier openings are not assumed. Surveyed ground, utilities, foundations, drainage, erection/temporary works, evacuation/access and actual shared dependencies must accompany selection. A 10% civil opportunity is not claimed as a saving.
''',
        'FINANCE-RECONCILIATION.md':'''# Delivery-cost financial reconciliation

These executable sensitivities preserve the original reference, then replace the original depot allowance once and replace labour/solar OPEX once. Incremental EPC is an explicit 7% allowance; qualification credit against the existing factory allowance is explicit. Paid training/assessment/supervised experience and additional commissioning specialists are separate pre-opening cash; no factory production wages are duplicated. Battery top-ups add only the shortfall above reserve contributions already in maintenance. Land, duties, utility diversions, spare inclusion, actual owner insurance and grid/charger upgrade capital remain unpriced.

'''+table(['Case','Capital USD bn','Government USD bn equivalent','Peak gap debt IQD tn','Unfunded support IQD tn','Debt clear without unfunded cash month','Company before-finance cash NPV USD bn'],finance_rows)+'''

The fixed-government case retains the original absolute government contribution and reallocates its USD downpayment within that ceiling. Other cases use 25% of their own capital; increased appropriation is not committed. In every case imports are funded 50% government USD/50% proposed Chinese USD credit; ordinary/green bonds, bank and gap credit remain IQD. All debt/reserve/buffer/principal/cash residuals reconcile. **Six-month bond units are placement requirements, not subscriptions.** Climate/rights/additional local income remain uncommitted in conditional cases; the dedicated case removes all these targets and green pricing benefits.

Opening-fleet procurement follows the selected supply case and its extra spare. Factory cost/capacity is retained, and opening dates follow the later of civil readiness and replayed fleet acceptance; paid receipts scale with reduced timetable supply and ramps. Future expansion dates and funding remain null. Contracted solar removes city-owned plant CAPEX but keeps provider plant resources visible and charges generation; a private provider, rights, prices and firm deliverability are not established. Company cash NPVs are not like-for-like complete resource NPVs.

[Summary and source-bound cases](finance-summary.json) include full monthly native-currency ledgers, six-month bond/loan sale and repayment schedules, fees, grace, early principal, buffers and terminal debt/cash. Only genuine surplus after all obligations and buffers can fund contractual voluntary repayment; uncovered support cannot fund it. No new public subsidy or tariff adoption is claimed. Baseline fares and OPEX retain 5% growth and the existing elasticity/income assumptions.
''',
        'WORKFORCE-PILOT.md':f'''# Workforce, practical training and a rest-limited pilot

The [seven lesson cards](lesson-cards.json) provide practical scenarios, prerequisites/apparatus, critical observations, assessor authority, retraining and Arabic draft instructions. Attendance, practical assessment and task/asset/location authorisation stay separate. All actual candidate/assessor outcomes and native Arabic review remain null. The draft must not become an operational rulebook through generation.

[Pilot schedule](pilot-roster.json) covers {roster['required_weekly_cover_hours']:.1f} OCC hours over seven days with {roster['planning_positions']} unnamed planning positions, maximum 8-hour shifts, minimum 11-hour rest and maximum 40 hours per rolling seven days. These are editable scheduling assumptions, not accepted Iraqi employment terms. No worker identity is invented; every slot remains ineligible until real Employee/assessment/authorisation/resources and a fresh start check exist. Leave/sickness/annual relief, supervised staffing, tools/permits and independent checks remain necessary.

Department/unit/role budgets, recruitment cohorts, task workload and native HR/Work Order/Job Card/Asset Maintenance/Asset Repair records remain linked to the existing workload package. Read-only administrative previews require native role/document permissions and a baseline-bound private employee packet; human work-release authority remains separate. [Frappe staffing documentation](https://docs.frappe.io/hr/staffing-plan) describes the native administration; it does not appoint Baghdad staff.
''',
        'FIELD-WORK-PACKETS.md':'''# Field investigations, quotations and actual appointments

[Scope inclusion forms](scope-inclusion-forms.csv), [supplier requests](supplier-rfq.csv), [corridor investigations](corridor-comparison.json) and [six work packages](closure-packets.json) turn unresolved items into defined data collection and independent exit criteria. No external contact has been made. Existing USD 360,000 estimator-work budget is an unquoted closure allowance with EPC overlap unknown, not committed funding or priced boreholes/equipment tests.

Repository artifacts are prepared; all six native evidence Tasks remain open, preserving actual owner/project/dates/status. Actual survey, qualified suppliers, OD/tenant enquiries, Iraqi appointments/approvals, signed finance and subscriptions remain pending. Honest nulls must be replaced by independently accepted evidence before those workstreams can close. [GAO estimating guidance](https://www.gao.gov/products/gao-20-195g) supports technical scope, WBS, data, alternatives/risk and actual-cost updates; it does not validate these rates or release the scheme.
'''}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.check:
        summary=read(OUT/'summary.json')
        for base,key in ((ROOT,'sources_sha256'),(OUT,'outputs_sha256')):
            for path,sha in summary[key].items():
                if digest(base/path)!=sha:raise ValueError('Stale delivery closure: '+path)
        print('Delivery closure sources/outputs pass');return
    paths=dict(generator=Path(__file__),config=CONFIG,baseline_generator=ROOT/'tools/automation/baghdad_delivery_baseline.py',
        funding_logic=ROOT/'tools/automation/baghdad_funding_analysis.py',delivery_logic=ROOT/'tools/automation/baghdad_delivery_stress.py',
        funding=ROOT/'lib/templates/iraq-funding.toml',options=ROOT/'lib/templates/baghdad-finance-options.toml',risk_config=ROOT/'lib/templates/baghdad-delivery-risk.toml',
        baseline_config=ROOT/'lib/templates/baghdad-delivery-baseline.toml',design=CITY/'design.toml',scenario=CITY/'baghdad.toml',
        finance=CITY/'engineering/finance/summary.json',factory=CITY/'engineering/factory/summary.json',stress=CITY/'engineering/delivery-risk/summary.json',
        programme=CITY.parent/'finance/baghdad-programme.json',operations=CITY/'operations/baghdad-operations.json.gz',
        reference=CITY/'engineering/financing-redesign/reference.json',baseline=CITY/'engineering/delivery-baseline/summary.json',
        detail=CITY/'engineering/detail/register.json',maintenance=ROOT/'lib/templates/maintenance-schedule.toml',
        electronics=ROOT/'control-electronics/reference-integration.json',slab_design=ROOT/'design/component-catalogue/src/osr_mech/civil/slab.py',
        finance_engine=ROOT/'design/city-generation/src/osr_scenario/iraq_finance.py')
    paths['stabling']=CITY/'engineering/stabling/summary.json'
    paths.update(viaduct_comparison_generator=ROOT/'tools/automation/baghdad_viaduct_comparison.py',
        civil_cost=ROOT/'lib/templates/civil-cost-model.toml')
    paths.update(erp_probe=ROOT/'deployment/erpnext/apps/osr_erpnext/osr_erpnext/delivery_admin.py',
        restore_probe=ROOT/'tools/automation/verify_baghdad_erp_restore.py')
    for name in ('depot-package','six-car','workforce','first-phase','scope-register'):
        paths[name]=CITY/'engineering/delivery-baseline'/(name+'.json')
    baseline=read(paths['baseline'])
    for base,key in ((ROOT,'sources_sha256'),(paths['baseline'].parent,'outputs_sha256')):
        for path,sha in baseline[key].items():
            if digest(base/path)!=sha:raise ValueError('Refresh original reconciliation: '+path)
    sources={p.relative_to(ROOT).as_posix():digest(p) for p in paths.values()}
    sources.update(baseline['sources_sha256'])
    revision=hashlib.sha256(json.dumps(sources,sort_keys=True).encode()).hexdigest()
    c=tomllib.loads(CONFIG.read_text());validate(c);bc=tomllib.loads(paths['baseline_config'].read_text());d=tomllib.loads(paths['design'].read_text());s=tomllib.loads(paths['scenario'].read_text())
    depots,family,people,phases,scope=(read(paths[key]) for key in ('depot-package','six-car','workforce','first-phase','scope-register'))
    factory=read(paths['factory']);city_finance=read(paths['finance']);risk=read(paths['stress'])
    layouts=depot_layouts(depots,d,phases,c);bom=expanded_bom(s,family,read(paths['detail']))
    energy=site_energy(d,s,city_finance,bc)
    opening_d,opening_s=opening_scenario(d,s,phases);opening_finance=deepcopy(city_finance)
    opening_finance['operations_basis']['annual_train_km_including_non_revenue']*=sum(r['opening_daily_train_km'] for r in phases['lines'])/sum(r['baseline_daily_train_km'] for r in phases['lines'])
    opening_people=workforce(opening_d,opening_s,opening_finance,risk,factory,bc)
    people['development_mobilisation']=mobilisation_capacity(people,bc,c)
    opening_people['development_mobilisation']=mobilisation_capacity(opening_people,bc,c)
    opening_energy=site_energy(opening_d,opening_s,opening_finance,bc)
    maintenance_data=maintenance(d,s,people,city_finance,phases,c)
    opening_phases=deepcopy(phases)
    for row in opening_phases['lines']:row['baseline_daily_train_km']=row['opening_daily_train_km']
    opening_maintenance=maintenance(opening_d,opening_s,opening_people,opening_finance,opening_phases,c)
    inputs,delivery_phases,task_lines,programme=reconstruct_inputs(paths)
    if not inputs['config']['model']['iqd_per_usd']==bc['model']['iqd_per_usd_reference']==c['model']['iqd_per_usd']:
        raise ValueError('Reconcile financial/workforce/corridor exchange-rate assumptions before publication')
    opening_factory=opening_factory_replay(paths,phases,deepcopy(risk['cases']['calendar_baseline']['settings']))
    baseline_openings={p['line']:p['opening_month'] for p in delivery_phases}
    # Preserve full-fleet demand weights: reduced service is applied separately
    # below. A smaller order must never invent earlier civil commissioning.
    demand_weights={p['line']:p['weight'] for p in delivery_phases}
    for phase in opening_factory['delivery']['phases']:
        phase['opening_month']=max(phase['opening_month'],baseline_openings[phase['line']])
        phase['weight']=demand_weights[phase['line']]
    actual_openings={p['line']:p['opening_month'] for p in opening_factory['delivery']['phases']}
    opening_inputs,_,_,_=reconstruct_inputs(paths,opening_factory['delivery']['phases'])
    opening_factory['operating_inputs']=opening_inputs
    opening_risk=deepcopy(risk)
    opening_risk['cases']['calendar_baseline']['phases']=opening_factory['delivery']['phases']
    opening_people=workforce(opening_d,opening_s,opening_finance,opening_risk,factory,bc)
    opening_people['development_mobilisation']=mobilisation_capacity(opening_people,bc,c)
    for row in opening_phases['lines']:
        row['conditional_full_line_opening_month']=actual_openings[row['line']]
    opening_maintenance=maintenance(opening_d,opening_s,opening_people,opening_finance,opening_phases,c)
    batteries=battery_cash(maintenance_data,phases,inputs['options'],len(inputs['operating']))
    opening_batteries=battery_cash(opening_maintenance,opening_phases,inputs['options'],len(opening_inputs['operating']))
    corridors=corridor_cases(opening_d,opening_s,phases,city_finance,factory,bc,c,opening_energy,programme)
    cases=reconciled_finance(inputs,delivery_phases,task_lines,depots,family,people,opening_people,energy,opening_energy,phases,batteries,opening_batteries,c,opening_factory)
    reference=read(paths['reference'])
    for key in ('total_capital_usd','terminal_cash_iqd','peak_supplemental_balance_iqd'):
        if abs(cases['reference']['metrics'][key]-reference['metrics'][key])>.02:raise ValueError('Saved reference case changed: '+key)
    roster=pilot_roster(c);packets=closure_packets(scope,depots,bom,corridors,people)
    OUT.mkdir(parents=True,exist_ok=True);outputs=[]
    def save(name,value):
        path=OUT/name;path.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n');outputs.append(path)
    def csvout(name,rows,fields=None):
        path=OUT/name
        with path.open('w',newline='') as stream:
            columns=fields if fields is not None else list(rows[0]) if rows else []
            writer=csv.DictWriter(stream,fieldnames=columns,lineterminator='\n');writer.writeheader();writer.writerows(rows)
        outputs.append(path)
    save('depot-layouts.json',layouts);csvout('depot-tracks.csv',layouts['tracks']);csvout('depot-slots.csv',layouts['slots'])
    for site in layouts['sites']:
        path=OUT/('depot-'+site['line']+'.svg');path.write_text(layout_svg(site));outputs.append(path)
    save('six-car-procurement.json',bom);csvout('six-car-child-bom.csv',bom['parts'])
    save('development-training-mobilisation.json',people['development_mobilisation'])
    save('opening-factory-replay.json',{k:v for k,v in opening_factory.items() if k!='operating_inputs'})
    csvout('development-training-monthly.csv',people['development_mobilisation']['monthly'])
    with (paths['baseline'].parent/'energy-synthetic_reference-owned_solar-hourly.csv').open() as stream:
        reader=csv.DictReader(stream);aggregate_fields=reader.fieldnames
        aggregate_shortages=[row for row in reader if float(row['unserved_kwh'])>1e-7]
    csvout('aggregate-reference-shortage-hours.csv',aggregate_shortages,aggregate_fields)
    for label,model in [('full',energy),('opening',opening_energy)]:
        for weather,case in model['cases'].items():
            shortage_rows=case.pop('shortage_hours')
            if label=='full' and weather=='reference':csvout('energy-site-shortage-hours.csv',[{k:format(v,'.12g') if isinstance(v,float) else v for k,v in row.items()} for row in shortage_rows])
            for line,rows in case.pop('hourly_by_line').items():
                if label=='full' and weather=='reference':csvout('energy-'+line+'-hourly.csv',rows)
            csvout('energy-'+label+'-'+weather+'-sites.csv',case['sites'])
        save('site-energy.json' if label=='full' else 'opening-site-energy.json',model)
    save('opening-workforce.json',opening_people);save('maintenance.json',maintenance_data);csvout('maintenance-tasks.csv',maintenance_data['tasks']);csvout('battery-renewals.csv',maintenance_data['battery_renewals'])
    csvout('battery-reserve-monthly.csv',batteries.pop('monthly'));save('battery-reserve.json',batteries)
    save('opening-maintenance.json',opening_maintenance)
    csvout('opening-battery-reserve-monthly.csv',opening_batteries.pop('monthly'));save('opening-battery-reserve.json',opening_batteries)
    interval_register=maintenance_register(d,s,tomllib.loads(paths['maintenance'].read_text())['maintenance_interval'])
    save('maintenance-interval-register.json',interval_register)
    startup=startup_alternatives(d,read(paths['stabling']))
    save('startup-policy-alternatives.json',startup)
    save('corridor-comparison.json',corridors);csvout('corridor-comparison.csv',corridors['cases'])
    save('pilot-roster.json',roster);save('lesson-cards.json',lesson_cards(people));save('closure-packets.json',packets)
    csvout('scope-inclusion-forms.csv',packets['scope_inclusion_forms']);csvout('supplier-rfq.csv',packets['supplier_rfq_forms'])
    metrics={}
    for name,case in cases.items():
        case['status']='unquoted-delivery-sensitivity-not-approved'
        save('finance-'+name+'.json',case);csvout('finance-'+name+'-monthly.csv',case['monthly']);csvout('finance-'+name+'-semiannual.csv',case['semiannual'])
        metrics[name]=dict(metrics=case['metrics'],company_cash_npv_before_finance_usd=case['company_cash_npv_before_finance_usd'],government_policy=case['government_policy'])
    save('finance-summary.json',dict(cases=metrics,baseline_reconstructed_exactly=True,adopted=False,complete_delivery_budget=False))
    fare_sweep=cases['reconciled_full_fleet']['fare_sensitivities'];save('fare-sensitivities.json',fare_sweep)
    csvout('fare-sensitivities.csv',[{k:v for k,v in row.items() if k!='metrics'} for row in fare_sweep])
    task_rows=[]
    for work in packets['work_packages']:
        description=dict(**work,closure_source_revision=revision)
        task_rows.append(dict(subject=work['id']+' — '+work['accountable_function'],status='Open',priority='High',description='<pre>'+html.escape(json.dumps(description,indent=2))+'</pre>'))
    save('erpnext-tasks.json',dict(doctype='Task',status='draft-import-package-not-live-records',tasks=task_rows));csvout('erpnext-task-import.csv',task_rows)
    reports=report_files(layouts,bom,energy,maintenance_data,batteries,corridors,cases,roster,packets)
    mobilisation=people['development_mobilisation']
    reports['DEVELOPMENT-TRAINING.md']='# Development leadership and training mobilisation\n\n'+table(
        ['Interim function','Start month','Operating handover month','Loaded IQD/month'],
        [(r['role_id'],r['start_month'],r['handover_month'],f"{r['monthly_loaded_payroll_iqd']:,.0f}") for r in mobilisation['development_posts']])+f'''

Interim development authorities begin at NTP. The training head mobilises at month {c['mobilisation']['training_head_start_month']}; rigs must be ready by month {mobilisation['training_rigs_required_month']}, before operating cohorts join. [Cohort lesson schedules and all operating roles](development-training-mobilisation.json) distinguish teaching, initial/repeat assessment, supervised experience and handover. Named incumbents/successors, qualified assessors, equipment and signed handovers remain absent.

[Monthly capacity and cash](development-training-monthly.csv) buys the existing contracted teaching/assessment allowance once. New interim leadership and external supervision add IQD {mobilisation['additional_preopening_cash_iqd']/1e9:.3f}bn before inflation, explicitly included in the integrated financing cases. Operating trainees supply zero qualified teaching/assessor/mentor capacity. These hour-derived minimum posts require actual competence, rig availability, observation ratios and daily/rest schedules; they do not establish an operating roster. The OCC pilot remains an anonymous rest-constrained example; all 21 roles have coverage and lesson requirements, with actual full rosters still unaccepted.

The native Employee attachment preview validates a controlled snapshot only. It returns `snapshot_eligible` for those assertions, keeps `eligible` and `live_start_check` false, and does not resolve current authoritative revocation. Real task start requires current permits, calibration, stock release, competence, availability and human work-release authority.
'''
    reports['SITE-ENERGY.md']+=f'\n[All {len(aggregate_shortages)} aggregate shortage hours](aggregate-reference-shortage-hours.csv) remain an explicit pooled comparator. [Site-specific shortage hours](energy-site-shortage-hours.csv) expose grid/charger limits, opening/closing stored energy, local PV and remote generation before wheeling. Local PV never incurs remote wheeling losses/charges. The installed-throughput case reduces fare, station and additional commercial receipts; it is an energy upper bound, not a validated achieved timetable.\n'
    reports['FINANCE-RECONCILIATION.md']+=f"\n[Opening factory replay](opening-factory-replay.json) manufactures exactly {opening_factory['selected_trainsets']} planned trains, including the extra line-9 spare, with rebuilt finite factory queues. Dropped orders are removed from manufacturing and invoice cash; original expansion-capable factory CAPEX is retained. Openings are the later of civil readiness and replayed fleet acceptance; later dates flow through receipts, payroll, reserves and the operating horizon. Depots retain full eventual-network capacity; staffing, maintenance, reserve and site energy follow the lower supply. All sensitivities retain zero modelled dividends; retained cash is not distributable profit without taxes, covenants and approvals.\n"
    reports['FINANCE-RECONCILIATION.md']+='\nThe `simple_span_bearing_index` sensitivity removes the bearing reduction only from existing standard Pi25 length, then adds the declared incremental EPC once. It inherits original civil invoice dates and procurement-origin proportions as assumptions, keeps government at 25%, splits assumed imports 50% USD government cash / 50% Chinese USD credit, and retains all other funding in IQD. Monthly/six-month ledgers, interest, fees, reserves and early repayment are recalculated. This is an unquoted index counterfactual, not a bearing supplier offer; finite end effects, connection costs, actual import eligibility and consequential foundations remain unpriced. OSR-US and special segments do not inherit Pi25 bearing quantities.\n'
    reports['DEPOTS-SLAB-MANUFACTURE.md']+='\n![Line 6 storage and workshop packing study](depot-line-6.svg)\n'
    startup_ring=next(row for row in startup['cases'] if row['line']=='line-9')
    reports['DEPOTS-SLAB-MANUFACTURE.md']+=f"\n[Startup alternatives](startup-policy-alternatives.json) compare the existing revenue fleet with the frozen original dispatch-point set, including {startup_ring['revenue_position_deficit']} missing line-9 directions. Holding that set fixed requires {startup_ring['minimum_additional_revenue_trains']} extra revenue trains and {startup_ring['additional_10_percent_spares']} extra spares: USD {startup_ring['additional_train_reference_capital_usd']/1e6:.2f}m vehicle reference, before consequential costs. Adding trains must not silently expand dispatch-point selection. Reserving fewer start points or buying trains requires a separate selected-start, cycle, turnback, depot/charging and funding replay; neither changes the baseline nor closes the existing failed gate.\n"
    reports['MAINTENANCE-RENEWALS.md']+=f"\n[All {len(interval_register)} controlled interval records](maintenance-interval-register.json) also retain station, civil/track/structures, energy, wayside, tooling, finish/joint/wash and soiling work. Condition-based tasks have no invented frequency or labour cost. [Opening-fleet reserve cash](opening-battery-reserve-monthly.csv) uses {opening_factory['selected_trainsets']} trainsets and adds its own indexed shortfalls to the reduced-supply financing case.\n"
    reports['FINANCE-RECONCILIATION.md']+='\n\n## Fare/demand/affordability sensitivities\n\n'+table(
        ['Base fare IQD','Paid-demand multiplier','44-trip income share','Debt-clear month','Terminal gap IQD tn','Before-finance cash NPV USD bn'],
        [(r['base_fare_iqd'],f"{r['paid_demand_multiplier']:.3f}",f"{r['monthly_44_trip_income_share']:.1%}",r['debt_clearance_without_unfunded_support_month'],f"{r['terminal_gap_debt_iqd']/1e12:.3f}",f"{r['company_cash_npv_before_finance_usd']/1e9:.3f}") for r in fare_sweep])+'''

[Full results](fare-sensitivities.json) change the base fare once, retain existing peak/off-peak pricing and 5% annual fare/OPEX/income growth, reduce paid trips with the existing uncalibrated elasticity, and scale existing station commercial receipts with demand. Debt clearance and cash NPV are different tests. Conditional green/grant/rights/local-income targets and cheap IQD gap credit remain uncommitted. An assumed higher fare is not a sustainable tariff until OD, distributional affordability and actual service/credit conditions are accepted. The 44-trip share uses the historical income proxy and base fare before variable-price weighting, not measured disposable income.
'''
    for name,text in reports.items():
        path=OUT/name;path.write_text(text);outputs.append(path)
    summary=dict(schema='baghdad-delivery-closure/1',as_of=c['model']['as_of'],source_revision=revision,
        sources_sha256=sources,outputs_sha256={p.name:digest(p) for p in outputs},finance_cases=metrics,
        repository_work_packages_prepared=6,field_work_packages_accepted=0,actual_quotes=0,named_appointments=0,
        complete_delivery_budget=False,operational_release=False)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('Prepared depot/corridor cases, parts/RFQs, site shortage diagnostics, development/training capacity and eight financial sensitivities')

if __name__=='__main__':main()
