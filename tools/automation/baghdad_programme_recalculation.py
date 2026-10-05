#!/usr/bin/env python3
"""Quantity-driven Baghdad staffing, depots, fabrication and funding review."""
from __future__ import annotations
import argparse
from collections import defaultdict
from copy import deepcopy
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import tomllib

from baghdad_delivery_baseline import ROOT, CITY, workforce, table
from baghdad_delivery_closure import reconstruct_inputs, preopening_cash, mobilisation_capacity
from baghdad_funding_analysis import capital_projection
from baghdad_viaduct_comparison import bearing_index_delta_contracts
from baghdad_recalculation_finance import simulate, positive

CONFIG=ROOT/'lib/templates/baghdad-programme-recalculation.toml'
OUT=CITY/'engineering/programme-recalculation'


def read(path):return json.loads(path.read_text())
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def indexed_median(c):
    w=c['wages'];base=positive(w['median_employee_monthly_iqd'],'historical employee median')
    if w['planning_year']<w['observation_year']:raise ValueError('Wage date precedes observation')
    positive(w['annual_index_assumption'],'wage index',zero=True)
    return base*(1+w['annual_index_assumption'])**(w['planning_year']-w['observation_year'])


def validate(c):
    for section in c.values():
        if isinstance(section,dict):
            for key,value in section.items():
                if isinstance(value,(float,int)) and not isinstance(value,bool):positive(value,key,zero=True)
    for p in c['product']:
        for key in ('baseline_unit_usd','imported_input_usd','local_material_usd','person_hours','crew_per_cell','cell_floor_m2','equipment_usd_per_cell'):
            positive(p[key],p['id']+':'+key)
        if not isinstance(p['crew_per_cell'],int):raise ValueError('Crew size must be integer')
    if len({p['id'] for p in c['product']})!=len(c['product']):raise ValueError('Duplicate component process')
    if c['depots']['sites_per_line']!=1 or not c['depots']['store_full_line_fleet']:raise ValueError('Expected one full-fleet depot per line')
    for key in ('positions_per_track','workshop_days_year'):
        if not isinstance(c['depots'][key],int) or c['depots'][key]<1:raise ValueError('Invalid depot count')
    if not c['stations']['retain_service_hours']:raise ValueError('Shorter service requires a fresh timetable/demand replay')
    for section,key in [('industry','availability'),('industry','equipment_import_share'),('industry','bought_component_import_share'),('depots','import_share')]:
        if not 0<c[section][key]<=1:raise ValueError('Invalid fraction: '+key)
    if not 0<c['depots']['workshop_availability']<=1:raise ValueError('Invalid workshop availability')
    if any(v<0 or v>1 for v in c['civil_policy']['penalty_removal_sensitivities']):raise ValueError('Invalid penalty removal')


def revised_workforce(d,s,finance,risk,factory,c,bc):
    config=deepcopy(bc);w=config['workforce'];median=indexed_median(c)
    w.update(frontline_monthly_iqd=median*c['wages']['general_multiplier'],
        technical_monthly_iqd=median*c['wages']['technical_multiplier'],lead_monthly_iqd=median*c['wages']['supervisor_multiplier'],
        employer_cost_fraction=c['wages']['employer_cost_fraction'],overtime_allowance_fraction=c['wages']['overtime_allowance_fraction'],
        customer_service_stations_per_post=1)
    w['trainer_hourly_iqd']=w['technical_monthly_iqd']*12/w['paid_hours_per_year']
    result=workforce(d,s,finance,risk,factory,config)
    grade_map={'city-director':'director','chief-engineer':'senior','quality-safety':'senior','training':'senior'}
    loaded=1+w['employer_cost_fraction']+w['overtime_allowance_fraction']
    for role in result['roles']:
        grade=grade_map.get(role['role_id'],{'frontline':'general','technical':'technical','lead':'supervisor'}[role['grade']])
        old=role['monthly_base_iqd'];new=median*c['wages'][grade+'_multiplier']
        if new<median*1.5-.01:raise ValueError('Pay below dignity floor')
        role.update(grade=grade,monthly_base_iqd=new,median_multiple=c['wages'][grade+'_multiplier'],
            annual_loaded_payroll_iqd=role['required_fte']*new*12*loaded)
        for cohort in result['recruitment_cohorts']:
            if cohort['role_id']==role['role_id']:cohort['paid_preopening_training_iqd']*=new/old
    stations=len(d['stations']);service=finance['workforce']['service_hours_per_day'];normal_hours=c['stations']['normal_shifts']*c['stations']['normal_shift_hours']
    if c['stations']['staff_per_station']!=2 or c['stations']['normal_shifts']!=2:raise ValueError('Expected two station staff and two normal shifts')
    station_roles=[r for r in result['roles'] if r['role_id'] in {'platform-assistance','customer-service'}]
    station_hours=stations*2*service*w['service_days']
    if abs(sum(r['annual_workload_person_hours'] for r in station_roles)-station_hours)>.001:raise ValueError('Station cover does not reconcile')
    result.update(reference_required_fte=sum(r['required_fte'] for r in result['roles']),
        reference_annual_loaded_payroll_iqd=sum(r['annual_loaded_payroll_iqd'] for r in result['roles']),
        wage_basis=dict(observed_median_iqd=c['wages']['median_employee_monthly_iqd'],observation_year=c['wages']['observation_year'],
            indexed_planning_median_iqd=median,index_assumption=c['wages']['annual_index_assumption'],
            general_monthly_floor_iqd=median*1.5,current_median_observed=False,source=c['wages']['source']),
        station_cover=dict(stations=stations,simultaneous_posts=stations*2,normal_daily_shift_assignments=stations*2*2,
            normal_shift_hours=c['stations']['normal_shift_hours'],service_hours=service,
            additional_late_hours_per_station=max(0,service-normal_hours),
            annual_station_cover_person_hours=station_hours,station_cover_fte=sum(r['required_fte'] for r in station_roles),
            normal_shift_only_fte=math.ceil(stations*2*normal_hours*w['service_days']/result['productive_hours_per_fte']),
            no_employee_is_assigned_every_day=True,roster_accepted=False))
    result['reference_annual_loaded_payroll_usd']=result['reference_annual_loaded_payroll_iqd']/c['model']['iqd_per_usd']
    result['reference_payroll_delta_usd']=result['reference_annual_loaded_payroll_usd']-result['current_labour_usd']
    result['training_recruitment_cash_iqd']=sum(r['paid_preopening_training_iqd']+r['trainer_assessor_iqd'] for r in result['recruitment_cohorts'])
    return result,config


def depots(d,s,c,existing,phases):
    dc=c['depots'];length=positive(s['consist']['length_m'],'train length')+positive(dc['train_clearance_m'],'clearance')
    sites=[];items=[];openings={p['line']:p['opening_month'] for p in phases}
    for fleet in d['fleets']:
        line=fleet['line'];count=fleet['trainset_count'];tracks=math.ceil(count/dc['positions_per_track'])
        bays=math.ceil(count*dc['bay_hours_per_train_year']/(dc['workshop_days_year']*dc['workshop_hours_day']*dc['workshop_availability']))
        yard=(tracks*dc['positions_per_track']*length+dc['site_access_track_m'])*dc['track_centres_m']*dc['yard_access_multiplier']
        shell=bays*length*dc['workshop_bay_width_m'];actual_count=count
        allocations=[]
        for track in range(tracks):
            slots=min(dc['positions_per_track'],actual_count);actual_count-=slots
            allocations.append(dict(id=f'{line}-storage-{track+1:03d}',slots=slots,usable_length_m=slots*length,
                train_length_m=s['consist']['length_m'],clearance_per_slot_m=dc['train_clearance_m'],constructed=False))
        if actual_count:raise ValueError('Depot track slots fail fleet reconciliation')
        site=dict(id='BAG-DEP-'+line,line=line,trainsets=count,storage_slots=count,storage_tracks=tracks,
            train_length_m=s['consist']['length_m'],slot_length_m=length,workshop_bays=bays,
            yard_area_m2=yard,workshop_area_m2=shell,office_stores_area_m2=dc['landscape_office_stores_m2_per_site'],
            planning_land_area_m2=yard+shell+dc['landscape_office_stores_m2_per_site'],tracks=allocations,
            workshop_bay_hours_demand=count*dc['bay_hours_per_train_year'],
            workshop_bay_hours_capacity=bays*dc['workshop_days_year']*dc['workshop_hours_day']*dc['workshop_availability'],
            opening_month=openings[line],actual_site=None,land_price_usd=None,connected_depot_track_design=None,
            interline_transfer_assumed=False,station_stabling_required_for_capacity=False,physical_release=False)
        quantities=[('storage-track',count*length,dc['track_usd_per_m']),
            ('workshop-track',bays*length,dc['track_usd_per_m']),
            ('site-access-track',dc['site_access_track_m'],dc['track_usd_per_m']),
            ('turnouts',tracks+bays+2,dc['turnout_usd']),
            ('drainage-access',yard,dc['drainage_access_usd_per_m2']),('workshop-shell',shell,dc['workshop_shell_usd_per_m2']),
            ('workshop-process-equipment',bays,dc['workshop_equipment_usd_per_bay']),
            ('workshop-electrical-mechanical-fire-services',shell,dc['workshop_services_usd_per_m2']),
            ('yard-lighting-fire-services',1,dc['yard_lighting_fire_usd_per_site']),
            ('office-stores',dc['landscape_office_stores_m2_per_site'],dc['office_stores_usd_per_m2']),
            ('wash-plant',1,dc['wash_plant_usd_per_site']),('wheel-lathe',1,dc['wheel_lathe_usd_per_site']),
            ('rescue-quarantine-isolation',1,dc['isolation_rescue_quarantine_usd_per_site'])]
        for key,q,rate in quantities:items.append(dict(id=site['id']+':'+key,line=line,scope=key,quantity=q,reference_rate_usd=rate,
            cost_usd=q*rate,invoice_currency='USD-equivalent-of-IQD-and-import-allowances',quotation=None))
        site['reference_cost_usd']=sum(r['cost_usd'] for r in items if r['line']==line);sites.append(site)
    # Existing depot PV/BESS inventory is retained ONCE, separately from civil/workshop sizing.
    energy_items=[r for r in existing['alternatives']['workload_bays']['items'] if r['scope'].startswith('depot-')]
    for row in energy_items:
        line=next(r['line'] for r in existing['alternatives']['workload_bays']['sites'] if r['station']==row['site'])
        items.append(dict(id='retained:'+row['id'],line=line,scope=row['scope'],quantity=row['quantity'],
            reference_rate_usd=row['reference_rate_usd'],cost_usd=row['reference_cost_usd'],quotation=None))
    for site in sites:site['reference_cost_usd']=sum(r['cost_usd'] for r in items if r['line']==site['line'])
    if len(sites)!=len(d['lines']) or sum(r['storage_slots'] for r in sites)!=sum(f['trainset_count'] for f in d['fleets']):raise ValueError('One depot per line / full fleet storage fails')
    return dict(sites=sites,items=items,number_of_depots=len(sites),full_fleet_storage_slots=sum(r['storage_slots'] for r in sites),
        gross_reference_cost_usd=sum(r['cost_usd'] for r in items),total_land_envelope_m2=sum(r['planning_land_area_m2'] for r in sites),
        removed_original_depot_allowance_usd=d['costs']['depots_usd'],full_trainsets_and_spares_included=True,
        workshop_bays_are_separate_from_storage_slots=True,station_stabling_capacity_credit=0,
        energy_inventory_retained_once=True,land_and_utility_cost_usd=None,complete_installed_budget=False,
        retained_energy_shortage_and_charger_upgrade_gates=True,
        service_launch_from_depots_validated=False,overnight_conflict_and_morning_launch_replay_required=True)


def local_industry(d,s,family,factory,c,people):
    ic=c['industry'];fx=c['model']['iqd_per_usd'];fleet=sum(f['trainset_count'] for f in d['fleets']);cars=s['consist']['car_count']
    median=indexed_median(c);productive=people['productive_hours_per_fte'];loaded=1+c['wages']['employer_cost_fraction']+c['wages']['overtime_allowance_fraction']
    wage=median*c['wages']['technical_multiplier'];hourly=wage*12*loaded/productive/fx
    rate=factory['minimum_steady_output_trainsets_per_year'];available=ic['working_days_year']*ic['shift_hours']*ic['availability']
    production_end=math.ceil(factory['stock_finish_working_day']*12/260)
    production_months=production_end-ic['ready_month']+1
    if production_months<=0:raise ValueError('No factory production period')
    production_years=production_months/12
    budgets={r['part_id']:r['cost_allocation_per_consist_usd'] for r in family['bom']};allocated=defaultdict(float);rows=[]
    for p in c['product']:
        per_car=s['consist']['systems'][p['profile_quantity']] if 'profile_quantity' in p else p['per_car']
        per_train=per_car*cars;quantity=fleet*per_train;annual=rate*per_train
        budget=p['baseline_unit_usd']*per_train;allocated[p['parent']]+=budget
        if allocated[p['parent']]>budgets[p['parent']]+.01:raise ValueError('Child fabrication allocation exceeds original parent: '+p['id'])
        cells=math.ceil(annual*p['person_hours']/(p['crew_per_cell']*available));floor=cells*p['cell_floor_m2']*1.35
        equipment=cells*p['equipment_usd_per_cell']+p['shared_equipment_usd']
        building=floor*ic['building_usd_per_m2'];site=floor*ic['site_floor_multiplier']*ic['serviced_site_usd_per_m2']
        capital=equipment+building+site+ic['qualification_usd_per_product']
        posts=cells*p['crew_per_cell'];fte=math.ceil(posts*available/productive);support=math.ceil(fte*ic['support_staff_fraction'])
        annual_production_payroll=fte*wage*12*loaded/fx
        annual_embedded_production_payroll=quantity*p['person_hours']*hourly/production_years
        annual_capacity_payroll=max(0,annual_production_payroll-annual_embedded_production_payroll)
        annual_fixed=support*wage*12*loaded/fx+annual_capacity_payroll+capital*ic['fixed_plant_maintenance_fraction']
        unit=p['imported_input_usd']+p['local_material_usd']+p['person_hours']*hourly+p['process_overhead_usd']
        saving=p['baseline_unit_usd']-unit;whole_margin=quantity*saving-capital-production_years*annual_fixed
        actual_average_output=quantity/production_years
        break_even=capital/(saving-annual_fixed/actual_average_output) if saving>annual_fixed/actual_average_output else None
        rows.append(dict(id=p['id'],parent=p['parent'],per_train=per_train,network_quantity=quantity,
            annual_required_output=annual,cells=cells,annual_cell_output_capacity=cells*p['crew_per_cell']*available/p['person_hours'],
            concurrent_production_posts=posts,production_fte=fte,support_fte=support,process_person_hours_per_unit=p['person_hours'],
            monthly_base_wage_iqd=wage,loaded_labor_usd_per_hour=hourly,baseline_unit_allocation_usd=p['baseline_unit_usd'],
            local_unit_reference_usd=unit,imported_input_usd_per_unit=p['imported_input_usd'],
            local_material_usd_per_unit=p['local_material_usd'],labour_usd_per_unit=p['person_hours']*hourly,
            process_overhead_usd_per_unit=p['process_overhead_usd'],equipment_usd=equipment,building_usd=building,
            serviced_site_usd=site,qualification_usd=ic['qualification_usd_per_product'],incremental_capital_usd=capital,
            equipment_import_usd=equipment*ic['equipment_import_share'],annual_fixed_factory_cost_usd=annual_fixed,
            annual_production_establishment_payroll_usd=annual_production_payroll,
            annual_production_payroll_in_unit_prices_usd=annual_embedded_production_payroll,
            annual_capacity_payroll_topup_usd=annual_capacity_payroll,
            whole_order_margin_before_finance_tax_risk_usd=whole_margin,break_even_units=break_even,
            economically_positive_before_finance=whole_margin>0,local_scope=p['local_scope'],
            facility_floor_m2=floor,ready_month=ic['ready_month'],supplier_quote=None,technology_license=None,
            first_article_accepted=False,annual_cycle_measured=False,imported_cells_and_electronics_are_not_local=True))
    main_hours=sum(r['reference_person_hours_per_consist'] for r in family['labour_routes'])*fleet
    existing_embedded=sum(r['cost_allocation_per_consist_usd'] for r in family['bom'] if r['part_id']=='M6-assembly-qa-logistics')*fleet*ic['existing_train_assembly_payroll_share']
    main_direct=math.ceil(factory['direct_production_crew_fte']*available/productive)
    main_support=math.ceil(main_direct*ic['factory_support_staff_fraction'])
    main_fixed=main_support*wage*12*loaded/fx*production_years
    main_labor=main_hours*hourly
    main_establishment_payroll=main_direct*wage*12*loaded/fx*production_years
    main_capacity_payroll=max(0,main_establishment_payroll-main_labor)
    return dict(products=rows,trainsets=fleet,cars=cars,battery_gross_network_kwh=s['consist']['battery_capacity_kwh']*fleet,
        production_end_month=production_end,production_months=production_months,paid_production_years=production_years,
        no_cell_manufacturing_plant_assumed=True,existing_factory_direct_posts_per_shift=factory['direct_production_crew_fte'],
        main_factory_production_fte=main_direct,main_factory_support_fte=main_support,
        main_assembly_person_hours=main_hours,main_assembly_variable_payroll_usd=main_labor,
        main_factory_capacity_payroll_topup_usd=main_capacity_payroll,
        main_factory_production_establishment_payroll_usd=main_establishment_payroll,
        main_factory_support_payroll_usd=main_fixed,embedded_assembly_payroll_credit_usd=existing_embedded,
        main_factory_net_payroll_replacement_usd=main_labor+main_capacity_payroll+main_fixed-existing_embedded,
        price_evidence='Unquoted make/buy and process-rate sensitivities, not achieved savings',
        national_sales_and_factory_utilisation_credit=0,procurement_origin_and_export_credit_eligibility_accepted=False)


def alignment_options(d,c,comparison,cost):
    cc=c['civil_policy'];ramp=max(cc['candidate_approach_min_m'],cc['deck_height_m']/cc['maximum_gradient'])
    specials=[r for r in d['civil_segments'] if r.get('viaduct_product')=='REALIGN-OR-SPECIAL']
    windows=defaultdict(list)
    for r in specials:windows[r['line']].append((max(0,r['from_station_m']-ramp),r['to_station_m']+ramp))
    merged={}
    for line,parts in windows.items():
        parts=sorted(parts);result=[]
        for start,end in parts:
            if result and start<=result[-1][1]:result[-1][1]=max(result[-1][1],end)
            else:result.append([start,end])
        merged[line]=result
    conversion=[]
    for segment in d['civil_segments']:
        if segment['class']!='at-grade':continue
        for start,end in merged.get(segment['line'],[]):
            lo=max(start,segment['from_station_m']);hi=min(end,segment['to_station_m'])
            if hi>lo:conversion.append(dict(line=segment['line'],from_m=lo,to_m=hi,length_m=hi-lo,
                current_class='at-grade',candidate_class='elevated',surveyed=False,curve_reduction_verified=False,
                ramp_geometry_verified=False,station_height_and_egress_accepted=False))
    total=sum(r['length_m'] for r in d['lines']);elev=sum(r['to_station_m']-r['from_station_m'] for r in d['civil_segments'] if r['class']=='elevated')
    extra=sum(r['length_m'] for r in conversion);simple_rate=comparison['bearing_index_sensitivity']['simple_span_link_slab_rate_usd_per_km']
    incremental=extra/1000*(simple_rate-cost['civil_usd_per_km']['at_grade'])
    cases=[dict(id='additional_elevation_base_allowance',extra_viaduct_m=extra,
        resulting_elevated_fraction=(elev+extra)/total,incremental_standard_civil_allowance_usd=incremental,
        hypothetical_penalty_removal_usd=0.,net_direct_allowance_change_usd=incremental,
        penalty_removal_fraction=0.,realignment_design_verified=False,achieved_saving=False,
        special_structure_increment_usd=None,complete_installed_budget=False)]
    return dict(policy=cc,current_elevated_fraction=elev/total,candidate_intervals=conversion,alternatives=cases,
        candidate_extra_elevated_m=extra,candidate_elevated_fraction=(elev+extra)/total,
        additional_elevated_within_policy=(elev+extra)/total<=cc['maximum_elevated_fraction'],
        exceptional_segments=len(specials),minimum_gradient_approach_m=ramp,
        policy_is_not_a_route_or_construction_approval=True,
        elevation_alone_removes_no_horizontal_bend=True,penalty_is_not_a_supplier_price=True,
        selected_geometry=None,land_utilities_stations_foundations_and_crossings_usd=None)


def elevated_station_scope(d,c):
    core=read(CITY/'engineering/alignment/core-realignment.json')['core']
    rates=tomllib.loads((ROOT/'lib/templates/capex-costs.toml').read_text())['station_unit_usd']
    policy=c['elevated_stations'];rows=[]
    for station in d['stations']:
        if not core['south']<=station['lat']<=core['north'] or not core['west']<=station['lon']<=core['east']:continue
        base=rates[station['archetype']]
        elevated=(rates['interchange-elevated'] if station['archetype'] in ('interchange','interchange-elevated') else base*policy['non_interchange_structure_multiplier']+policy['vertical_access_allowance_usd'])
        rows.append(dict(station=station['id'],line=station['line'],catalogue_archetype=station['archetype'],
            existing_station_allowance_usd=base,elevated_reference_allowance_usd=elevated,
            incremental_direct_usd=max(0,elevated-base),status='unquoted-core-elevated-platform-and-vertical-access-allowance',
            actual_structure_accessibility_fire_egress_accepted=False))
    return dict(stations=rows,incremental_direct_usd=sum(row['incremental_direct_usd'] for row in rows),
        title_clearance_pier_utility_approval=False,quoted=False)


def revised_contracts(inputs,task_lines,d,depots,industry,c,cost,selection,alignment, *, raw_stress=False, construction_stress=False):
    contracts=deepcopy(inputs['contracts']+inputs['factory_contracts']);old=sum(r['budget_usd'] for r in contracts)
    contracts=[r for r in contracts if r['bucket']!='depots']
    for site in depots['sites']:
        finish=max(0,int((site['opening_month']-2)*260/12-30))
        contracts.append(dict(bucket='revised_depot',line=site['line'],budget_usd=site['reference_cost_usd'],
            imported_share=c['depots']['import_share'],planned_start_day=max(0,finish-22*260//12),planned_finish_day=finish))
    uplift=elevated_station_scope(d,c)
    old_station_contracts=[row for row in contracts if row['bucket']=='stations']
    for line in d['lines']:
        amount=sum(row['incremental_direct_usd'] for row in uplift['stations'] if row['line']==line['name'])
        if amount:
            related=[row for row in old_station_contracts if task_lines.get(row.get('manufacturing_uid'),row.get('line',''))==line['name']]
            if not related:raise ValueError('Missing station work programme for core uplift: '+line['name'])
            contracts.append(dict(bucket='core_elevated_station_upgrade',line=line['name'],budget_usd=amount,
                imported_share=c['elevated_stations']['import_share'],planned_start_day=min(row['planned_start_day'] for row in related),
                planned_finish_day=max(row['planned_finish_day'] for row in related)))
    contracts+=bearing_index_delta_contracts(inputs['contracts']+inputs['factory_contracts'],task_lines,d,cost)
    count=industry['trainsets'];selected=[r for r in industry['products'] if selection=='all' or selection=='positive' and r['economically_positive_before_finance']]
    old_rolling=sum(r['budget_usd'] for r in contracts if r['bucket']=='rolling_stock')
    per_train_delta=industry['main_factory_net_payroll_replacement_usd']/count
    per_train_delta+=sum(r['per_train']*(r['local_unit_reference_usd']-r['baseline_unit_allocation_usd']) for r in selected)
    if raw_stress:
        per_train_delta+=sum(r['per_train']*(r['imported_input_usd_per_unit']+r['local_material_usd_per_unit'])*c['industry']['raw_price_stress_fraction'] for r in selected)
    # Parent budgets are allocations. Input origin changes remove only the imported
    # share already attributed to the replaced component, never its entire value.
    bought_components_per_train=sum(r['per_train']*r['baseline_unit_allocation_usd'] for r in industry['products'])
    origin_credit_per_train=sum(r['per_train']*r['baseline_unit_allocation_usd'] for r in selected)*c['industry']['bought_component_import_share']
    imported_inputs_per_train=sum(r['per_train']*r['imported_input_usd_per_unit'] for r in selected)
    for contract in contracts:
        if contract['bucket']!='rolling_stock':continue
        old_amount=contract['budget_usd'];weight=old_amount/old_rolling;units=count*weight
        new_amount=old_amount+per_train_delta*units
        # Explicit buy case: these five completed products are imported.
        # Preserve the original origin proxy only for the remaining parent scope.
        imports=(old_amount-bought_components_per_train*units)*contract['imported_share']
        imports+=bought_components_per_train*units*c['industry']['bought_component_import_share']
        imports+=imported_inputs_per_train*units*(1+c['industry']['raw_price_stress_fraction'] if raw_stress else 1)-origin_credit_per_train*units
        if not 0<=imports<=new_amount:raise ValueError('Vehicle import schedule does not reconcile')
        contract.update(budget_usd=new_amount,imported_share=imports/new_amount,
            local_production_replacement_trainsets=units,origin_share_is_unverified=True)
    for product in selected:
        amount=product['incremental_capital_usd']
        contracts.append(dict(bucket='component_factory',product=product['id'],budget_usd=amount,
            imported_share=product['equipment_import_usd']/amount,planned_start_day=0,planned_finish_day=390))
    civil_delta=alignment['net_direct_allowance_change_usd'] if alignment else 0
    civil_total=sum(r['budget_usd'] for r in contracts if r['bucket']=='civil')
    if civil_total+civil_delta<0:raise ValueError('Alignment sensitivity removes more than civil scope')
    for contract in contracts:
        if contract['bucket']=='civil':contract['budget_usd']*=1+civil_delta/civil_total
        if construction_stress and contract['bucket'] in {'civil','stations','core_elevated_station_upgrade','revised_depot','component_factory'}:
            contract['budget_usd']*=1+c['construction']['embedded_labour_fraction_stress']*c['construction']['pay_uplift_fraction_stress']
    direct_change=sum(r['budget_usd'] for r in contracts)-old
    epc=direct_change*c['model']['incremental_epc_fraction']
    if epc>=0:contracts.append(dict(bucket='incremental_programme_epc',budget_usd=epc,imported_share=0,planned_start_day=0,planned_finish_day=1))
    else:
        existing_epc=sum(r['budget_usd'] for r in contracts if r['bucket']=='epc_overhead')
        if -epc>existing_epc:raise ValueError('EPC credit exceeds original allowance')
        for r in contracts:
            if r['bucket']=='epc_overhead':r['budget_usd']*=1+epc/existing_epc
    return contracts,selected,dict(original_capital_usd=old,net_direct_change_usd=direct_change,incremental_epc_usd=epc,
        original_depot_removed_once_usd=d['costs']['depots_usd'],rolling_stock_net_change_usd=per_train_delta*count,
        bought_component_import_share=c['industry']['bought_component_import_share'],
        original_vehicle_aggregate_import_share_is_replaced_for_itemised_products=True,
        civil_counterfactual_delta_usd=civil_delta,parent_allocations_are_unquoted=True)


def delay_operating(operating,phases,industry,selected,c):
    """Conservative six-month uniform supplier delay, without earlier revenue."""
    delay=c['industry']['supplier_delay_months'];ready=c['industry']['ready_month'];fx=c['model']['iqd_per_usd']
    later=deepcopy(phases)
    for p in later:p['opening_month']+=delay
    result=[];median=indexed_median(c);loaded=1+c['wages']['employer_cost_fraction']+c['wages']['overtime_allowance_fraction']
    idle_fte=industry['main_factory_production_fte']+sum(p['production_fte'] for p in selected)
    idle_monthly=idle_fte*median*c['wages']['technical_multiplier']*loaded/fx
    for month in range(len(operating)+delay):
        source=month if month<ready else ready if month<ready+delay else month-delay
        row=deepcopy(operating[source]);ratio=1.05**(month//12-source//12)
        for key in ('revenue_usd','opex_usd','fare_revenue_usd','nonfare_revenue_usd','restricted_working_capital_usd'):
            if key in row:row[key]*=ratio
        if ready<=month<ready+delay:row['opex_usd']+=idle_monthly*1.05**(month//12)
        row['month']=month;row['phases']=later;result.append(row)
    return result,later


def operating_projection(inputs,people,bc,depots,industry,selected,c,finance,phases):
    op=deepcopy(inputs['operating']);fx=c['model']['iqd_per_usd'];options=inputs['options'];costs=finance['annual_opex_usd']['components']
    original=read(CITY/'engineering/delivery-closure/finance-simple_span_bearing_index.json')
    # Reuse the reviewed site energy, battery-index topups and development cash;
    # replace operating and pre-opening staff and depot upkeep once.
    inherited=deepcopy(original['monthly']);components=original['opex_components']
    prepay=preopening_cash(people,len(op),fx,options)
    old_people=read(CITY/'engineering/delivery-baseline/workforce.json')
    old_people['development_mobilisation']=read(CITY/'engineering/delivery-closure/development-training-mobilisation.json')
    oldprepay=preopening_cash(old_people,len(op),fx,options)
    openings={p['line']:p['opening_month'] for p in phases};line_pay=defaultdict(float)
    byrole={r['role_id']:r for r in people['roles']}
    for unit in people['units']:
        role=byrole[unit['unit'].split(':')[0]];line_pay[unit['line']]+=unit['required_fte']*role['annual_loaded_payroll_iqd']/role['required_fte']/fx
    core_stations=elevated_station_scope(tomllib.loads((CITY/'design.toml').read_text()),c)
    first=min(openings.values());last=max(openings.values());olddep=read(CITY/'engineering/delivery-baseline/depot-package.json')['alternatives']['workload_bays']['gross_reference_cost_usd']
    # Cash procurement already includes variable component labour/materials;
    # only distinct ongoing support/plant maintenance is added below.
    variable_annual=sum(r['annual_required_output']*r['local_unit_reference_usd'] for r in selected)
    working_capital=variable_annual*c['industry']['working_capital_months']/12
    for month,row in enumerate(op):
        indexed=(1+options['fares']['opex_inflation'])**(month//12)
        active=first<=month<last+inputs['config']['model']['operating_years']*12
        payroll=sum(v for line,v in line_pay.items() if month>=openings[line])*indexed/12 if active else 0
        row['opex_usd']=inherited[month]['opex_iqd']/fx+payroll-components[month]['workload_payroll_usd']+prepay[month]-oldprepay[month]
        if active:
            row['opex_usd']+=sum(station['incremental_direct_usd'] for station in core_stations['stations'] if month>=openings[station['line']])*c['elevated_stations']['annual_maintenance_fraction']*indexed/12
        opened=sum(p['weight'] for p in phases if month>=p['opening_month']) if active else 0
        row['opex_usd']+=(depots['gross_reference_cost_usd']-olddep)*c['depots']['depot_maintenance_fraction']*opened*indexed/12
        # Fixed support, paid capacity above variable unit labour, and
        # plant maintenance end after the actual scheduled Baghdad order.
        production_end=industry['production_end_month']
        if c['industry']['ready_month']<=month<=production_end:
            row['opex_usd']+=sum(p['annual_fixed_factory_cost_usd'] for p in selected)*indexed/12
            row['restricted_working_capital_usd']=working_capital*indexed
        else:row['restricted_working_capital_usd']=0
        row['phases']=deepcopy(phases)
    return op


def integrated_journey_projection(operating, boardings_per_journey):
    if not math.isfinite(boardings_per_journey) or boardings_per_journey < 1:
        raise ValueError('Mean boardings per journey must be finite and at least one')
    result=deepcopy(operating)
    for row in result:
        row['fare_revenue_usd']/=boardings_per_journey
        row['revenue_usd']=row['fare_revenue_usd']+row['nonfare_revenue_usd']
    return result


def construction_people(payload,industry,c,people):
    monthly=defaultdict(lambda:defaultdict(float));productive=people['productive_hours_per_fte'];median=indexed_median(c);lanes={}
    factory_packages={r['package'] for r in read(CITY/'engineering/factory/summary.json')['stages']}
    # Each named trade is a separately funded concurrent post assumption, not a
    # claim that a foreman and an equipment resource are interchangeable people.
    for task in payload['manufacturing_tasks']:
        if task['package_id'] in factory_packages:continue
        roles=[r.strip() for r in task['staff_roles'].split(';') if r.strip()]
        start=task['planned_start_day'];finish=task['planned_finish_day']
        scope=task['budget_bucket'] or 'programme'
        posts=max(len(roles),c['construction'].get(scope+'_crew',c['construction']['programme_crew']))
        lane=(scope,task.get('resource_pool') or task['manufacturing_uid'],str(task.get('resource_lane') or task['manufacturing_uid']))
        for day in range(start,finish+1):
            key=(day,lane);lanes[key]=max(lanes.get(key,0),posts)
    for (day,lane),posts in lanes.items():monthly[max(0,math.floor(day*12/260))][lane[0]]+=posts*8
    rows=[]
    for month,buckets in sorted(monthly.items()):
        for bucket,hours in sorted(buckets.items()):
            fte=math.ceil(hours/(productive/12));grade='technical' if bucket in {'civil','stations','charging_microgrid','signalling'} else 'supervisor'
            wage=median*c['wages'][grade+'_multiplier'];cash=fte*wage*(1+c['wages']['employer_cost_fraction']+c['wages']['overtime_allowance_fraction'])
            rows.append(dict(month=month,scope=bucket,person_hours=hours,planning_fte=fte,grade=grade,monthly_base_iqd=wage,
                monthly_loaded_payroll_iqd=cash,scope_is_configured_lane_crew_screen_not_measured=True,embedded_contractor_payroll_credit_usd=None))
    return dict(monthly=rows,peak_construction_fte=max((sum(r['planning_fte'] for r in rows if r['month']==month) for month in monthly),default=0),
        estimated_total_construction_payroll_iqd=sum(r['monthly_loaded_payroll_iqd'] for r in rows),
        incremental_cash_added_to_financing=0,reason='Civil/station contract rates already include construction labour; unknown wage-content overlap cannot justify a second payroll charge',
        complete_contractor_establishment=False,resource_lane_overlap_counted_once=True,headcounts_are_not_added_to_permanent_operating_fte=True)


def csvout(path,rows):
    if not rows:return
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.check:
        summary=read(OUT/'summary.json')
        for base,key in ((ROOT,'sources_sha256'),(OUT,'outputs_sha256')):
            for name,sha in summary[key].items():
                if digest(base/name)!=sha:raise ValueError('Stale programme recalculation: '+name)
        print('Programme recalculation sources/outputs pass');return
    paths={k:ROOT/v for k,v in dict(funding='lib/templates/iraq-funding.toml',options='lib/templates/baghdad-finance-options.toml',
        programme='cities/catalogue/west-asia/Iraq/finance/baghdad-programme.json',finance='cities/catalogue/west-asia/Iraq/Baghdad/engineering/finance/summary.json',
        factory='cities/catalogue/west-asia/Iraq/Baghdad/engineering/factory/summary.json',risk_config='lib/templates/baghdad-delivery-risk.toml',
        stress='cities/catalogue/west-asia/Iraq/Baghdad/engineering/delivery-risk/summary.json',operations='cities/catalogue/west-asia/Iraq/Baghdad/operations/baghdad-operations.json.gz',
        reference='cities/catalogue/west-asia/Iraq/Baghdad/engineering/financing-redesign/reference.json').items()}
    c=tomllib.loads(CONFIG.read_text());validate(c);bc=tomllib.loads((ROOT/'lib/templates/baghdad-delivery-baseline.toml').read_text())
    d=tomllib.loads((CITY/'design.toml').read_text());s=tomllib.loads((CITY/'baghdad.toml').read_text());factory=read(paths['factory']);finance=read(paths['finance']);risk=read(paths['stress'])
    inputs,phases,task_lines,programme=reconstruct_inputs(paths)
    people,payconfig=revised_workforce(d,s,finance,risk,factory,c,bc)
    people['development_mobilisation']=mobilisation_capacity(people,payconfig,tomllib.loads((ROOT/'lib/templates/baghdad-delivery-closure.toml').read_text()))
    depot=depots(d,s,c,read(CITY/'engineering/delivery-baseline/depot-package.json'),phases)
    industry=local_industry(d,s,read(CITY/'engineering/delivery-baseline/six-car.json'),factory,c,people)
    comparison=read(CITY/'engineering/viaduct-comparison/comparison.json');cost=tomllib.loads((ROOT/'lib/templates/civil-cost-model.toml').read_text())
    alignment=alignment_options(d,c,comparison,cost)
    core_stations=elevated_station_scope(d,c)
    payload=json.loads(gzip.decompress(paths['operations'].read_bytes()));construction=construction_people(payload,industry,c,people)
    cases={}
    variants=[('revised_scope_buy','none',None,False,False),('local_all','all',None,False,False),('local_positive','positive',None,False,False),
        ('local_positive_mezzanine','positive',None,True,False),('local_positive_commercial_gap','positive',None,False,True),
        ('local_positive_mezzanine_stress','positive',None,True,True)]
    variants += [(a['id'],'positive',a,False,False) for a in alignment['alternatives']]
    transfer_cases={'integrated_fare_1_25_boardings':1.25,'integrated_fare_1_5_boardings':1.5,'integrated_fare_2_boardings':2.}
    variants += [(name,'positive',None,False,False) for name in ('local_positive_raw_price_stress','local_positive_supplier_delay','construction_wage_content_stress',*transfer_cases)]
    OUT.mkdir(parents=True,exist_ok=True)
    for legacy in OUT.glob('grade-separation-penalty-*'):
        if legacy.is_file():legacy.unlink()  # retired generated monetary-score sensitivities
    (OUT/'core-elevated-stations.json').write_text(json.dumps(core_stations,indent=2,sort_keys=True)+'\n')
    for name,selection,align,mezz,commercial in variants:
        contracts,selected,bridge=revised_contracts(inputs,task_lines,d,depot,industry,c,cost,selection,align,
            raw_stress=name=='local_positive_raw_price_stress',construction_stress=name=='construction_wage_content_stress')
        if name=='local_positive_supplier_delay':
            for contract in contracts:
                if contract['bucket']=='rolling_stock':
                    contract['planned_start_day']+=c['industry']['supplier_delay_months']*260//12
                    contract['planned_finish_day']+=c['industry']['supplier_delay_months']*260//12
        capital=capital_projection(contracts,inputs['config'],set(inputs['options']['green']['candidate_buckets']))
        op=operating_projection(inputs,people,payconfig,depot,industry,selected,c,finance,phases)
        case_phases=phases
        if name in transfer_cases:op=integrated_journey_projection(op,transfer_cases[name])
        if name=='local_positive_supplier_delay':op,case_phases=delay_operating(op,phases,industry,selected,c)
        settings=deepcopy(c)
        if name.endswith('mezzanine_stress'):
            settings['mezzanine'].update(cash_coupon=c['mezzanine']['rate_stress_cash_coupon'],pik_coupon=c['mezzanine']['rate_stress_pik_coupon'],
                overdue_interest_annual_rate=c['mezzanine']['rate_stress_cash_coupon']+c['mezzanine']['rate_stress_pik_coupon'])
        result=simulate(capital,op,inputs['config'],inputs['options'],settings,mezzanine=mezz,commercial_gap=commercial)
        invoice_rows=[dict(invoice_uid=r.get('manufacturing_uid',f"NEW-{i:05d}"),bucket=r['bucket'],line=task_lines.get(r.get('manufacturing_uid'),r.get('line','')),
            product=r.get('product',''),budget_usd=r['budget_usd'],imported_share=r['imported_share'],
            planned_start_day=r['planned_start_day'],planned_finish_day=r['planned_finish_day']) for i,r in enumerate(contracts)]
        csvout(OUT/(name+'-contracts.csv'),invoice_rows)
        result.update(paid_journey_conversion=dict(tariff='integrated-journey',
            mean_boardings_per_paid_journey=transfer_cases.get(name,1.),mean_boardings_calibrated=False,
            baseline_is_zero_transfer_capacity_upper_bound=name not in transfer_cases,
            demand_forecast_accepted=False,nonfare_receipts_and_service_energy_unchanged=True),capital_bridge=bridge,contract_schedule_file=name+'-contracts.csv',contract_count=len(contracts),
            selected_component_factories=[r['id'] for r in selected],
            conditional_alignment=align,opening_phases=case_phases,complete_delivery_budget=False,
            hourly_energy_and_full_service_acceptance=False,uncommitted_enhanced_income_and_green_terms=True,
            local_supplier_qualification_must_finish_by_month_18=bool(selected),additional_national_sales=0)
        (OUT/(name+'.json')).write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
        csvout(OUT/(name+'-monthly.csv'),result['monthly']);csvout(OUT/(name+'-semiannual.csv'),result['semiannual']);cases[name]=result['metrics']
    for name,data in [('workforce',people),('depots',depot),('industry',industry),('alignment',alignment),('construction-workforce',construction)]:
        (OUT/(name+'.json')).write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+'\n')
    csvout(OUT/'workforce.csv',people['roles']);csvout(OUT/'depot-items.csv',depot['items']);csvout(OUT/'component-make-buy.csv',industry['products'])
    csvout(OUT/'construction-workforce.csv',construction['monthly']);csvout(OUT/'alignment-candidates.csv',alignment['candidate_intervals'])
    drafts=dict(status='planning-drafts-only-no-native-records-written',scope='Baghdad',
        staffing_plan=[dict(role=r['role_id'],required_fte=r['required_fte'],monthly_base_iqd=r['monthly_base_iqd'],
            annual_loaded_payroll_iqd=r['annual_loaded_payroll_iqd'],appointment=None,competence=None) for r in people['roles']],
        depot_asset_projects=[dict(id=r['id'],line=r['line'],storage_slots=r['storage_slots'],train_length_m=r['train_length_m'],
            workshop_bays=r['workshop_bays'],reference_capital_usd=r['reference_cost_usd'],actual_land=None,approved_budget=None) for r in depot['sites']],
        factory_workstations=[dict(product=r['id'],cells=r['cells'],direct_fte=r['production_fte'],support_fte=r['support_fte'],
            monthly_base_iqd=r['monthly_base_wage_iqd'],actual_supplier=None,qualified_process=None) for r in industry['products']],
        supported_native_documents=['Staffing Plan','Job Applicant','Employee','Training Program','Workstation','Project','Budget','Work Order','Job Card','Asset Maintenance'],
        funding_approval_and_railway_release=False)
    (OUT/'erp-planning-drafts.json').write_text(json.dumps(drafts,indent=2,sort_keys=True)+'\n')
    local_rows=read(OUT/'local_positive.json')['monthly']
    capital_sources=[(label,currency,sum(row[key] for row in local_rows)) for label,currency,key in (
        ('Government import cash','USD','government_usd_cash'),
        ('Government local cash','IQD','government_iqd_cash'),
        ('Chinese capital credit','USD','chinese_export_credit_draw_native'),
        ('Ordinary capital bonds','IQD','domestic_bonds_draw_native'),
        ('Green capital bonds','IQD','green_bonds_draw_native'),
        ('Senior bank capital credit','IQD','bank_credit_draw_native'),
        ('Conditional climate capital grant','IQD','climate_grant_iqd'))]
    text=f'''# Baghdad programme recalculation

Controlled planning basis, {c['model']['as_of']}; unquoted and uncommitted. This is the latest staffing/depot/local-production review. Existing cost and financing cases remain historical comparators; no survey, manufacturing qualification or lender commitment is created.

## Operating people and wages

The {len(d['stations'])} stations require two concurrent staff during two normal eight-hour shifts: **{people['station_cover']['normal_daily_shift_assignments']} daily shift assignments**, not a headcount of people working every day. Retaining {people['station_cover']['service_hours']} service hours also requires {people['station_cover']['additional_late_hours_per_station']} hours of separately funded late cover per station. Weekly cover, leave, training, sickness and handovers give **{people['station_cover']['station_cover_fte']} station-cover FTE**, within **{people['reference_required_fte']} permanent operating FTE**. Full-operation loaded payroll is **IQD {people['reference_annual_loaded_payroll_iqd']/1e9:.3f}bn/year** (USD {people['reference_annual_loaded_payroll_usd']/1e6:.3f}m equivalent), indexed thereafter with OPEX.

The employee median is IQD 614,000 from the 2021 Labour Force Survey, cited in the [IMF 2023 report]({c['wages']['source']}). Applying an assumed 5% annual index to 2026 gives IQD {indexed_median(c):,.0f}; the general-worker floor is **IQD {indexed_median(c)*1.5:,.0f}/month**, 50% higher. Technical, supervisor, senior and director roles use 2.25/3/4/5 times that indexed proxy. This is a historical observation plus an editable index, not a measured current national median. Employer costs and overtime are priced separately. [Roles](workforce.csv) and [recruitment/cohorts](workforce.json) retain appointment and competence gates.

[ERP planning drafts](erp-planning-drafts.json) map the revised Staffing Plan, depot Project/Asset budgets and factory Workstations to native business records; they create no Employee, appointment, transaction or approval.

Construction workers, factory production/support workers and permanent operators are separate populations. [Construction](construction-workforce.json) applies explicit trade-crew allowances to actual work-package resource lanes/dates, counting overlapping use of the same lane once; its peak is {construction['peak_construction_fte']} FTE. It is not a measured complete contractor crew schedule; revised depot and upstream factory construction crews still require their own work-package schedules. Construction labour is already inside contract rates; its unknown payroll-content overlap remains unpriced, preventing a duplicate charge. A separate wage-content stress increases assumed labour content (20% of affected contracts) by 50%, with incremental EPC once; it is an overlap sensitivity, not proof of contractor wage contents. Existing assembly wages are replaced using an explicitly assumed embedded payroll credit; component process labour is inside component unit prices. Paid production capacity above those productive hours is added separately, never charged twice.

The final-assembly establishment is {industry['main_factory_production_fte']} production FTE plus {industry['main_factory_support_fte']} support FTE. The scheduled order requires {industry['production_months']} paid months from month 18 through month {industry['production_end_month']}; payroll follows this calendar, rather than dividing the order by a theoretical steady-state rate and losing ramp-up/idle months. Each upstream plant also funds its whole production establishment for that period, with the productive labour already in unit prices deducted once. These jobs are additional to permanent railway operations; no national order or permanent post-order subsidy is assumed.

## One depot per line, full-size trains and fleet

There are **{depot['number_of_depots']} line-local depots**, providing **{depot['full_fleet_storage_slots']} storage slots** for all six-car revenue/spare/reserve trains. Slots use the actual 111 m train plus 10 m clearance. Workshop bays follow annual bay-hour demand and usable bay capacity; parking slots are not maintenance bays. Station storage is an option without any capacity credit in this case. Full overnight-to-morning launch and throat conflicts remain unvalidated.

{table(['Line','Trainsets/storage slots','Tracks','Workshop bays','Land envelope ha','Reference USD m'],[[r['line'],r['trainsets'],r['storage_tracks'],r['workshop_bays'],f"{r['planning_land_area_m2']/1e4:.2f}",f"{r['reference_cost_usd']/1e6:.3f}"] for r in depot['sites']])}

Total depot reference: **USD {depot['gross_reference_cost_usd']/1e6:.3f}m**, replacing the original USD 8m exactly once. Storage, workshop and access tracks, points, drainage/access, workshop shell/equipment/services, yard lighting/fire services, wash plant, wheel lathe, offices/stores and rescue/quarantine are visible. Access-track length is an editable allowance, not a connected site alignment. Existing depot PV/BESS is retained once. Land/title, utility relocation, actual soil/foundations, installed charger/grid upgrades and tax/duties remain unpriced. [Item register](depot-items.csv).

## Core elevated stations

The reworked core has {len(core_stations['stations'])} station platforms with raised-structure/access scope. The register replaces their catalogue allowance with a separately stated elevated reference, adding **USD {core_stations['incremental_direct_usd']/1e6:.3f}m direct**, with incremental EPC and operating maintenance once. Elevated interchange allowances are already present where catalogued; they receive no duplicate uplift. Other core stations use a 30% structure allowance plus USD 1m for vertical access. These are unquoted allowances, not released multi-level junction or station designs. [Core station register](core-elevated-stations.json).

## Iraqi component manufacture

{table(['Product','Network quantity','Required units/year','Cells','Production/support FTE','Factory capital USD m','Unit make/buy USD','Whole-order margin USD m'],[[r['id'],r['network_quantity'],f"{r['annual_required_output']:.0f}",r['cells'],f"{r['production_fte']}/{r['support_fte']}",f"{r['incremental_capital_usd']/1e6:.3f}",f"{r['local_unit_reference_usd']:.0f}/{r['baseline_unit_allocation_usd']:.0f}",f"{r['whole_order_margin_before_finance_tax_risk_usd']/1e6:.3f}"] for r in industry['products']])}

[Make/buy inputs](component-make-buy.csv) price imported process machinery, Iraqi buildings/site work, qualification, residual imported inputs, local materials, graded labour, process overhead, fixed support and plant maintenance. Cells are sized to the existing train factory's required production rate, not a small demonstration line. The order is {industry['battery_gross_network_kwh']/1e6:.3f} GWh of gross onboard packs. Battery **pack assembly** is evaluated; imported cells/BMS remain. Bogie wheels/axles/bearings, motor inverters/magnets, door safety electronics and glazing feedstock also retain imports. Local manufacture does not mean zero USD input.

The buy case itemises these five imported completed products; the old blanket vehicle import percentage is retained only for other parent scope. This prevents replacing already-local scope with a second import credit. The all-product and positive-margin selections are separate unquoted cases. Whole-order margins are before finance/tax/risk; vendor prices, license, QA, process yield, supply commitments and first articles must validate them. No future national order pays Baghdad debt or makes an uneconomic line look profitable. Serial component qualification is assumed within the 18-month readiness target, not proven. A six-month supplier delay shifts rolling-stock invoices and opening/service cash, extends the full operating horizon and prices idle production payroll. A 25% raw-input price stress preserves the same selected facilities. Rejected/reworked product still needs a measured production replay. Existing final assembly tooling remains priced; upstream machinery is added without an unproven overlap credit.

## Paid journeys and transfers

Revenue remains a capacity-led sensitivity rather than a surveyed OD forecast. The reference uses one boarding per paid journey, a zero-transfer upper-bound assumption. Integrated-fare sensitivities use 1.25, 1.5 and 2 boardings per journey: only fare receipts are divided; kiosk/rental/advertising receipts, service, staffing and energy are retained. These are uncalibrated factors, not estimates of Baghdad travel. Physical access and surveyed OD/section loads must qualify any adopted demand forecast. [Demand handoff](../demand-bridge/README.md).

## More elevation and fewer bends

The current main design adopts the straight central elevated alignment. The screening policy allows up to {alignment['policy']['maximum_elevated_fraction']:.0%} elevated and at least {alignment['policy']['minimum_at_grade_fraction']:.0%} at grade, subject to site/design acceptance. Baghdad currently has {alignment['current_elevated_fraction']:.2%} elevated. Investigation windows around all {alignment['exceptional_segments']} exceptional segments add {alignment['candidate_extra_elevated_m']/1000:.3f} km of candidate at-grade conversion, reaching {alignment['candidate_elevated_fraction']:.2%}; overlapping intervals are merged and existing viaduct/bridge lengths excluded. Approach length is at least {alignment['minimum_gradient_approach_m']:.1f} m from assumed height/gradient.

**Elevation alone removes no horizontal bend.** Wider-radius geometry, station moves, ROW, vertical alignment, ramps, egress, ground/utility evidence, crossings and whole-life costs must be designed together. The additional-elevation case includes only its base allowance; routing scores are excluded from money and the old 25%/50% penalty-removal cases are retired. Special designs and consequential installed costs remain unknown. The added standard civil allowance uses the conservative simple-span bearing index. [Candidate intervals](alignment-candidates.csv).

## Funding and mezzanine comparison

Government capital remains exactly 25% of the scenario total. Imported invoices receive 50% government USD cash / 50% Chinese USD credit. Remaining government cash, bonds, senior bank/gap credit and mezzanine are IQD. Government USD payment dates follow machinery/input invoices; the remaining appropriation is allocated proportionally to local invoices, so a machinery-heavy month need not be falsely limited to 25% government cash. Chinese supplier origin and export-credit eligibility are assumptions requiring vendor/lender confirmation. China Exim describes buyer credit for Chinese products, technologies and services; machinery eligibility is not a loan commitment ([official product description](https://english.eximbank.gov.cn/Business/CreditB/SupportingFT/201810/t20181016_6965.html)).

The positive-margin local-production senior case's **capital-only** sources are shown below. They sum to its capital uses; gap credit, interest/fees, reserve funding and operating receipts are additional cashflows in its [monthly ledger](local_positive-monthly.csv) and [six-month placement schedule](local_positive-semiannual.csv). Ordinary and green bonds are separate placements, never added again to a combined bond figure. Bond face units are IQD 1m; rounded placement envelopes are not additional cash raised.

{table(['Capital source','Currency','Native amount','USD equivalent m'],[[label,currency,f'{amount:,.0f}',f"{amount/(1 if currency=='USD' else c['model']['iqd_per_usd'])/1e6:.3f}"] for label,currency,amount in capital_sources])}

Mezzanine replaces 10% of domestic residual capital borrowing; it is not extra capital on top of the uses. The IQD case has 6% cash coupon, 4% PIK, 2% arrangement fee and a 15-year balloon from each draw. Deferred cash coupon and PIK increase outstanding debt until maturity. Thereafter the overdue principal is retained with separately disclosed simple 10% contractual-interest sensitivity; arrears are not compounded and the balloon is not silently extended. Cash junior payments require senior DSCR of 1.20, funded reserves and actual residual cash; new gap draws/unfunded support cannot pay junior debt. No conversion, fresh equity or automatic refinancing is invented. Unpaid maturity balances/defaults remain visible. Mezzanine is structurally junior to senior debt and senior to equity, as described by [UNCITRAL](https://digitallibrary.un.org/record/272622/files/A_CN.9_458_Add.1-EN.pdf); the rates here are project sensitivities.

{table(['Matched case / six-month placement schedule','CAPEX USD bn','USD capital intensity','Peak IQD gap tn','Terminal all debt IQD tn','Unfunded IQD tn','Junior defaulted vintages'],[[f'[{name}]({name}-semiannual.csv)',f"{m['total_capital_usd']/1e9:.3f}",f"{m['usd_capital_intensity']:.2%}",f"{m['peak_gap_iqd']/1e12:.3f}",f"{m['terminal_all_debt_iqd']/1e12:.3f}",f"{m['unfunded_support_iqd']/1e12:.3f}",m['junior_defaulted_vintages']] for name,m in cases.items()])}

The {len(read(OUT/'local_positive.json')['selected_component_factories'])} positive-margin process options reduce capital from USD {cases['revised_scope_buy']['total_capital_usd']/1e9:.3f}bn to USD {cases['local_positive']['total_capital_usd']/1e9:.3f}bn, and imported invoice exposure from USD {cases['revised_scope_buy']['imported_invoices_usd']/1e9:.3f}bn to USD {cases['local_positive']['imported_invoices_usd']/1e9:.3f}bn. Half of that exposure is government USD cash and half Chinese USD credit; all other capital funding is IQD. The historical 148 km / USD 18bn third-party benchmark has a different scope and assumed full foreign-currency financing; this is a planning comparison, not a like-for-like tender saving. The reworked {sum(l['length_m'] for l in d['lines'])/1000:.1f} km network's {programme['comparison']['anchor_weighted_coverage']:.1%} legacy routing-demand cell fraction is not population access. Its former resident multiplication is retired; see the [native population and transfer audit](../access/README.md).

**Current financial conclusion:** the positive-margin senior case records IQD {cases['local_positive']['unfunded_support_iqd']/1e12:.3f}tn of residual unsourced support after assumed facilities and retains IQD {cases['local_positive']['terminal_all_debt_iqd']/1e12:.3f}tn of debt at the horizon. Its company NPV before finance is USD {cases['local_positive']['company_npv_before_finance_usd']/1e9:.3f}bn at the assumed nominal discount rate. Adding mezzanine does not change the underlying operating return: it leaves IQD {cases['local_positive_mezzanine']['terminal_all_debt_iqd']/1e12:.3f}tn of total debt and {cases['local_positive_mezzanine']['junior_defaulted_vintages']} unpaid junior vintages. It is not recommended as a cure for the funding deficit. Fare and OPEX indexation, kiosks/advertising and inherited additional receipts are already included; new verified capital, affordable revenue or accepted scope savings are still needed.

All cases use the same revised staff, depot and indexed fare/OPEX assumptions. Six months of scheduled senior service are reserved from the first draw; three months of OPEX plus explicit industrial working capital are restricted. This revised reserve policy differs from older reference cases, so compare matched cases in this table when judging mezzanine. Concessional 2% gap funding, grants/rights/additional income and enhanced green coupons are uncommitted; the 8% gap and high mezzanine-rate case expose that dependence. There are zero dividends. Cash/principal/PIK identities, maturity risk, monthly draws and six-month bond denominations are retained for every case.

Regenerate with `.venv/bin/python tools/automation/baghdad_programme_recalculation.py`; verify with `--check`. Complete installed scope, construction wage-content adjustment, local-pay survey, validated demand/timetable and supplier/lender agreements remain open.
'''
    (OUT/'README.md').write_text(text)
    paths.update(generator=Path(__file__),config=CONFIG,finance_generator=ROOT/'tools/automation/baghdad_recalculation_finance.py',
        closure_generator=ROOT/'tools/automation/baghdad_delivery_closure.py',baseline_generator=ROOT/'tools/automation/baghdad_delivery_baseline.py',
        funding_generator=ROOT/'tools/automation/baghdad_funding_analysis.py',design=CITY/'design.toml',scenario=CITY/'baghdad.toml',
        baseline_config=ROOT/'lib/templates/baghdad-delivery-baseline.toml',civil_cost=ROOT/'lib/templates/civil-cost-model.toml',
        comparison=CITY/'engineering/viaduct-comparison/comparison.json',depots=CITY/'engineering/delivery-baseline/depot-package.json',
        family=CITY/'engineering/delivery-baseline/six-car.json',people=CITY/'engineering/delivery-baseline/workforce.json',
        full_case=CITY/'engineering/delivery-closure/finance-simple_span_bearing_index.json')
    paths.update(alignment_config=ROOT/'lib/templates/baghdad-alignment.toml',
        alignment_controls=CITY/'engineering/alignment/core-realignment.json',
        alignment_generator=ROOT/'tools/automation/rework-baghdad-alignment.py')
    paths.update(mobilisation=CITY/'engineering/delivery-closure/development-training-mobilisation.json',
        closure_config=ROOT/'lib/templates/baghdad-delivery-closure.toml')
    summary=dict(schema=1,as_of=c['model']['as_of'],scope=c['model']['scope'],finance_cases=cases,
        operating_fte=people['reference_required_fte'],annual_payroll_iqd=people['reference_annual_loaded_payroll_iqd'],
        depot_count=depot['number_of_depots'],depot_storage_slots=depot['full_fleet_storage_slots'],
        supplier_quotes=0,physical_acceptances=0,complete_delivery_budget=False,baseline_design_replaced=True,
        sources_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths.values()},
        outputs_sha256={p.name:digest(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='summary.json'})
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(f"Recalculated {people['reference_required_fte']} operating FTE, {depot['number_of_depots']} depots, five make/buy packages and {len(cases)} funding cases")


if __name__=='__main__':main()
