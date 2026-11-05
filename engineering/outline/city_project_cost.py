"""Complete bounded city-network outline accounts, not operating approval."""
from copy import deepcopy
from math import ceil, fsum, isfinite
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity
from engineering.design_search import line_benchmark as budget, model_cost, compact_launch
from . import city_civil, vehicle_supply, supply_economics

PRODUCER='engineering/outline/city_project_cost.py'
CASES=('low','base','high')
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
    operating_release=False,procurement_approved=False,selected_reference_changed=False,movement_authority=False)
DEFAULTS=dict(version='CITY-PROJECT-OUTLINE-1',pricing_scenario='project-make-buy',station_launch_mode='cable-capstan',
    interchange_transfer_usd=[250000.,1000000.,4000000.],
    feeder_usd_route_m=[100.,300.,1000.],traction_motor_converter_usd_kw=[110.,180.,320.],
    traction_collector_protection_usd_car=[3000.,8000.,20000.],traction_added_mass_process_usd_kg=[3.,6.,15.],
    feeder_substation_spacing_m=3000.,feeder_substation_usd=[300000.,800000.,2000000.],
    depot_connection_m_per_line=[100.,500.,1500.],
    powered_axle_electrical_efficiency=[.9,.85,.75],
    foreign_local_rate_transfer=[.75,1.,1.75])


def _settings(policy):
    p=deepcopy(DEFAULTS);over=(policy or {}).get('project',{})
    if set(over)-set(p):raise ValueError('Unknown city project policy key')
    p.update(over)
    if p['pricing_scenario'] not in ('china-bulk-buy','project-make-buy'):raise ValueError('Explicit city supply scenario required')
    if p['station_launch_mode'] not in budget.MODES:raise ValueError('Unknown station launch mechanism')
    for k,v in p.items():
        nums=v if isinstance(v,list) else [v] if type(v) in (int,float) else []
        if isinstance(v,list) and len(v)!=3:raise ValueError('Three project sensitivity cases required')
        if any(type(z) not in (int,float) or not isfinite(z) or z<=0 for z in nums):raise ValueError('Positive finite project assumptions required')
    return p


def _access_sites(city):
    ids=[s['id'] for line in city['lines'] for s in line['stops']]
    if len(ids)!=len(set(ids)):raise ValueError('Unique line-platform stop identities required')
    parent={s:s for s in ids}
    def find(s):
        while parent[s]!=s:parent[s]=parent[parent[s]];s=parent[s]
        return s
    seen=set()
    for row in city.get('interchanges',[]):
        if row['id'] in seen:raise ValueError('Duplicate interchange identity')
        seen.add(row['id']);platforms=row.get('platforms',[])
        if any(s not in parent for s in platforms):raise ValueError('Interchange contains unknown platform')
        for a,b in zip(platforms,platforms[1:]):parent[find(b)]=find(a)
    return len({find(s) for s in ids}),len(seen)


def evaluate_city_cost(city_input,line_services,context,policy=None,root=ROOT):
    """Price actual network service, one committed fleet and one production setup.

    Unknown locality and detailed engineering remain bounded transferred planning
    hypotheses. Neither historical passenger capacity nor old city cost is used.
    """
    root=Path(root);p=_settings(policy);city=deepcopy(city_input);services=deepcopy(line_services)
    ids=[z['line_id'] for z in city['lines']]
    if set(ids)!={z['line_id'] for z in services} or len(services)!=len(ids):raise ValueError('Exactly one service per mapped line required')
    if any(z.get('city_input_id',city['input_id'])!=city['input_id'] for z in services):raise ValueError('Mixed city/service identities')
    by={z['line_id']:z for z in services};spec=deepcopy(context['spec']);d=spec['design'];a=spec['capital'];l=spec['lifecycle'];fx=spec['currency']['iqd_per_usd']
    fleet=sum(z['service']['total_trainsets'] for z in services);cars=sum(z['service']['totalcars'] for z in services)
    if type(fleet) is not int or fleet<=0 or cars!=fleet*6:raise ValueError('Explicit positive six-car network fleet required')
    civil_context=dict(context);civil_context['spec']=deepcopy(spec)
    extra_traction=max(z.get('propulsion_hypothesis',{}).get('added_traction_mass_kg_per_car',0.) for z in services)
    civil_context['spec']['design']['added_vehicle_mass_kg_per_car']+=extra_traction
    civil=city_civil.evaluate(city,civil_context,policy,root)
    v=vehicle_supply.revalue(context['vehicle_cost'],dict(totalcars=cars,total_trainsets=fleet),p['pricing_scenario'],root=root)
    vc=v['vehicle_cost'];vehicle_unit=budget.fixed_mass_vehicle_price(vc)['fixed_mass_per_train_iqd']
    capital=deepcopy(civil['capital_lines']);life=[]
    def add(target,key,scope,q,costs,basis,years=None):
        amounts=[float(z) for z in costs]
        if scope not in model_cost.SCOPES or any(not isfinite(z) or z<0 for z in amounts):raise ValueError('Invalid disjoint city account')
        row=dict(key=key,scope=scope,quantity=q,costs_usd=dict(zip(CASES,amounts)),basis=basis,source_class='C',life_years=years)
        row['line_id']=identity(row);target.append(row)
    add(capital,'network-delivered-assembled-fleet','rolling-stock',dict(trainsets=fleet,cars=cars),[fleet*vehicle_unit[c]/fx for c in CASES],
        'Same provisional vehicle inventory at total committed city volume; supplier/owned factories are counted once separately.',l['vehicle_life_years'])
    add(capital,'network-common-installed-interface-reserve','rolling-stock',dict(cars=cars,kg_per_car=d['added_vehicle_mass_kg_per_car']),
        [cars*d['added_vehicle_mass_kg_per_car']*z/fx for z in a['vehicle_interface_iqd_per_kg']],
        'Retained common installation/coupler/protection mass reserve priced once; no unverified removal credit.',l['vehicle_life_years'])
    station_rows=sum(len(z['stops']) for z in city['lines']);access_sites,interchanges=_access_sites(city)
    platform_area=2*station_rows*d['platform_length_m']*d['platform_width_m']
    stat=context['assumptions']['assumptions'];transfer=p['foreign_local_rate_transfer']
    add(capital,'line-platform-structures','stations-power',dict(platform_edges=2*station_rows,area_m2=platform_area),
        [platform_area*stat['station_platform_iqd_per_m2'][i]/fx*transfer[i] for i in range(3)],'Current 120 m platform planning envelope per line/direction; old short platform sizes are not inherited.',[40.,30.,20.])
    add(capital,'shared-access-and-transfer-complexes','stations-power',dict(access_sites=access_sites,interchanges=interchanges),
        [(access_sites*(stat['station_access_iqd_each'][i]+stat['station_control_iqd_each'][i]+stat['station_install_iqd_each'][i])/fx
          +interchanges*p['interchange_transfer_usd'][i])*transfer[i] for i in range(3)],'Shared access charged once for explicit interchange platform groups; each line platform remains. Accessibility, fire, circulation and transfer interfaces are mandatory budget scope.',[20.,15.,10.])
    launch_ids=[];fallback_ids=[];drive_sources={};drive_energy={c:0. for c in CASES};fleet_mass_t=6*(context['vehicle']['mass']['accounted_cap_loaded_kg_per_car']+d['added_vehicle_mass_kg_per_car'])/1000
    for line in city['lines']:
        row=by[line['line_id']];service=row['service'];ss=deepcopy(spec);ss['requirements']=deepcopy(row['requirements']);ss['design']=deepcopy(row['design']);kind=row.get('propulsion_hypothesis',{}).get('kind','station-launch-reference')
        prefix=line['line_id']+'/'
        if kind=='station-launch-reference':
            launch_ids.append(line['line_id']);service.setdefault('jerk_bound',compact_launch.jerk_bound(ss['design']['speed_m_s'],ss['design']['acceleration_m_s2'],ss['design']['jerk_m_s3']))
            revised,drive=supply_economics._electrical(ss,service,p['station_launch_mode'],root,civil['unit_rates'])
            lines,_=budget._drive(revised,service,civil['unit_rates'],p['station_launch_mode'])
            for z in lines:add(capital,prefix+z['key'],z['scope'],z['quantity'],[z['costs_iqd'][c]/fx for c in CASES],z['basis'],z['life_years'])
            departures=service['departure_sites']*3600/ss['requirements']['headway_s']*ss['requirements']['operating_hours_per_day']*ss['requirements']['operating_days_per_year']
            efficiency=ss['lim']['efficiency'] if p['station_launch_mode']=='compact-launch-LIM' else ss['rotary']['transmission_efficiency']*ss['rotary']['motor_efficiency']*ss['rotary']['vfd_efficiency']
            for case in CASES:drive_energy[case]+=departures*service['mechanical_work_kwh_per_departure']/efficiency
        elif kind=='powered-axle-continuous-research':
            fallback_ids.append(line['line_id']);h=row['propulsion_hypothesis'];kw=h['traction_rated_kw_per_car'];ncar=service['totalcars'];mass=h['added_traction_mass_kg_per_car'];route=line['route_m']
            if min(kw,mass)<=0:raise ValueError('Nonzero powered-axle equipment and installed mass reserve required')
            add(capital,prefix+'powered-axle-traction-collector-protection','rolling-stock',dict(cars=ncar,rated_kw_per_car=kw,added_mass_kg_per_car=mass),
                [ncar*(kw*p['traction_motor_converter_usd_kw'][i]+p['traction_collector_protection_usd_car'][i]+mass*p['traction_added_mass_process_usd_kg'][i]) for i in range(3)],
                'Explicit new powered-axle research configuration: motors/converters, collector/protection, structural installation and added-mass process allowance; no inherited propulsion qualification.',[25.,20.,15.])
            add(capital,prefix+'continuous-feed-and-substations','stations-power',dict(route_m=route,substations=ceil(route/p['feeder_substation_spacing_m'])),
                [route*p['feeder_usd_route_m'][i]+ceil(route/p['feeder_substation_spacing_m'])*p['feeder_substation_usd'][i] for i in range(3)],
                'Nonzero protected conductor supply, feeder/installation and substations; no traction-battery substitution or free power network.',[30.,25.,20.])
            departures=service['departure_sites']*3600/ss['requirements']['headway_s']*ss['requirements']['operating_hours_per_day']*ss['requirements']['operating_days_per_year']
            for i,case in enumerate(CASES):drive_energy[case]+=departures*service['mechanical_work_kwh_per_departure']/p['powered_axle_electrical_efficiency'][i]
        else:raise ValueError('Unknown propulsion configuration cannot inherit a price')
        # Only radial lines have terminal turnbacks; rings have a priced access
        # and recovery junction provision but never two invented termini.
        ends=0 if line['shape']=='ring' else 2
        add(capital,prefix+'terminal-and-line-controls','stations-power',dict(terminals=ends,positions_per_end=service['minimum_turnback_positions_per_end'],route_m=line['route_m']),
            [(ends*a['terminal_layout_iqd_per_end'][i]+line['route_m']/1000*a['route_control_iqd_per_km'][i])/fx*transfer[i] for i in range(3)],
            'Radial protected turnback/crossover and line controls; ring has zero terminal layouts. Conflict-free movement is unproven.',[20.,15.,10.])
    charger_kw=2*station_rows*6*d['charger_kw_per_car']
    add(capital,'network-auxiliary-charging','stations-power',dict(boarding_edges=2*station_rows,kw=charger_kw),
        [charger_kw*(a['charger_usd_per_kw'][i]*(1+a['charger_install_fraction'][i])+spec['rotary']['grid_protection_usd_per_kva'][i]) for i in range(3)],
        'Charging and separate grid capacity retained at every line platform; no unproven sharing credit for continuous-supply research.',l['electronics_life_years'])
    # Project-owned vehicle equipment/tooling and assembly capacity once at fleet volume.
    production_h=[]
    for i,case in enumerate(CASES):
        production_h.append(fsum(z['quantity'].get('process_hours_per_train',[0,0,0])[i]/(vc['mass_reserve_sensitivity']['case_factors'][case] if z['line_key'].startswith('unlocated-account/') else 1.)
            +6*z['quantity'].get('process_hours_per_car',[0,0,0])[i]+z['quantity'].get('cars',0)*z['quantity'].get('labour_hours_per_car',[0,0,0])[i] for z in vc['lines'])*fleet)
    positions=[ceil(h/9000) for h in production_h];assembly=[max(1,ceil(fleet*h/(9000*a['assembly_crew_per_bay']))) for h in (48.,144.,480.)]
    vehicle_floor=[(v['cell_floor_m2'][i]+max(200.,positions[i]*a['workspace_area_m2'])+assembly[i]*a['assembly_bay_area_m2'])*a['factory_storage_area_factor'] for i in range(3)]
    vehicle_campaign=[v['owned_factory_capital_usd'][case]+vehicle_floor[i]*a['factory_building_iqd_per_m2'][i]/fx
        +(a['vehicle_fixture_sets']*a['vehicle_fixture_iqd'][i]+assembly[i]*a['assembly_crew_per_bay']*a['workplace_tooling_iqd'][i])/fx for i,case in enumerate(CASES)]
    civil_campaign=[civil['owned_factory_capital_usd'][case]+civil['precast_floor_m2'][i]*a['factory_building_iqd_per_m2'][i]/fx+civil['precast_yard_m2'][i]*a['precast_yard_iqd_per_m2'][i]/fx for i,case in enumerate(CASES)]
    add(capital,'citywide-production-equipment-tools-buildings-yards','factory-tooling',dict(committed_cars=cars,committed_spans=civil['quantities']['span_count'],vehicle_operator_positions_per_shift=positions,two_shift_employee_floor=[2*n for n in positions],production_years=3,productive_hours_per_workplace=9000,assembly_bays=assembly,vehicle_floor_m2=vehicle_floor,precast_floor_m2=civil['precast_floor_m2'],precast_yard_m2=civil['precast_yard_m2']),
        [vehicle_campaign[i]+civil_campaign[i] for i in range(3)],'One citywide production campaign; existing purchased factories remain in unit prices; no speculative later-city amortisation.',None)
    # One pooled depot, with all line connection spurs explicitly budgeted.
    bays=max(1,ceil(fleet*a['depot_workshop_fraction_of_fleet']));storage=fleet*a['depot_storage_length_per_train_m']*a['depot_storage_track_pitch_m'];workshop=bays*a['depot_bay_length_m']*a['depot_bay_width_m'];depot_area=(storage+workshop)*(1+a['depot_circulation_fraction'])
    depot_tracks=[(fleet*a['depot_storage_length_per_train_m']+bays*a['depot_bay_length_m'])*(1+a['depot_circulation_fraction'])+len(ids)*p['depot_connection_m_per_line'][i] for i in range(3)]
    depot=[];land=[];route=civil['quantities']['route_m'];turnouts=ceil(fleet/5)+4+2*len(ids)
    for i,case in enumerate(CASES):
        u=civil['unit_rates'][case];track=depot_tracks[i]
        depot.append((storage*a['depot_earthworks_iqd_per_m2'][i]+workshop*a['depot_building_iqd_per_m2'][i]
            +track*(a['depot_trackbed_iqd_per_track_m'][i]+120.42*u['rail_factory_iqd_kg']+3.5*u['complete_8kg_fastener_factory_iqd_set']+u['rail_field_install_iqd_track_m'])
            +2*max(0,ceil(track/20)-1)*[75000.,200000.,700000.][i]+turnouts*a['depot_turnout_iqd_each'][i]+bays*a['depot_workshop_equipment_iqd_per_bay'][i]+a['depot_services_iqd'][i])/fx*transfer[i])
        footprint=route*a['row_width_m']*a['new_row_acquisition_fraction'][i]+depot_area+vehicle_floor[i]+civil['precast_yard_m2'][i]
        land.append((footprint*a['land_iqd_per_m2'][i]+route/1000*a['utilities_iqd_per_route_km'][i])/fx*transfer[i])
    add(capital,'pooled-depot-connections-maintenance','land-utilities-depot',dict(area_m2=depot_area,bays=bays,track_m=depot_tracks,turnouts=turnouts),depot,'Pooled storage/shop plus separate line access spurs and turnout packages; feasible physical interconnections remain a design task.',[40.,30.,20.])
    add(capital,'corridor-land-and-utilities','land-utilities-depot',dict(route_m=route,area_basis='Declared partial acquisition; overlapping corridors have no assumed free land credit'),land,'Explicit transferred land/utility scenarios, not local valuations, permits or surveyed diversions.',None)
    rolling=[fsum(z['costs_usd'][c] for z in capital if z['scope']=='rolling-stock') for c in CASES]
    add(capital,'fleet-spares-commissioning','fleet',dict(trainsets=fleet,spares_in_fleet=True),[rolling[i]*stat['fleet_spares_fraction'][i]+fleet*stat['fleet_commission_iqd_per_train'][i]/fx for i in range(3)],'Component spares and commissioning; reserve trainsets already in purchased fleet.',None)
    rescue=ceil(route/15000)
    add(capital,'network-protected-recovery-assets','recovery',dict(units=rescue),[rescue*z/fx for z in stat['rescue_iqd_each']],'Protected recovery asset quantities; tow/access/response unqualified.',[25.,20.,15.])
    direct=[fsum(z['costs_usd'][c] for z in capital) for c in CASES]
    add(capital,'design-prototypes-independent-review','construction',dict(direct_usd=direct),[direct[i]*a['engineering_testing_fraction'][i] for i in range(3)],'Nonzero design/survey/prototype and independent-review provision; factory QA already in component prices.')
    # All explicitly landed costs already include scenario duty. A separate
    # residual-only allowance covers packages without a declared landing scope.
    residual=[fsum(z['costs_usd'][c] for z in capital if z['scope']=='stations-power')*.25 for c in CASES]
    add(capital,'unallocated-package-tax-duty','construction',dict(residual_unlanded_fraction=.25),[residual[i]*a['tax_duty_provision_fraction'][i] for i in range(3)],'Bounded duty on unallocated site packages only; no second duty on landed rails, fasteners, vehicle raw materials or modules.')
    before_risk=[fsum(z['costs_usd'][c] for z in capital) for c in CASES]
    add(capital,'city-project-risk-contingency','construction',dict(pre_contingency_usd=before_risk),[before_risk[i]*a['project_contingency_fraction'][i] for i in range(3)],'Explicit remaining quantities/site/interface/development risk; no scope reduction.')
    years=30;discount=spec['requirements']['real_discount_rate'];annuity=fsum((1+discount)**-y for y in range(1,years+1))
    annual_km=fsum(z['service']['train_km_per_day']*z['requirements']['operating_days_per_year'] for z in services)
    annual_energy=[];annual_ops=[];annual_maintenance=[]
    operating_hours=max(z['requirements']['operating_hours_per_day'] for z in services)
    operating_days=max(z['requirements']['operating_days_per_year'] for z in services)
    exposure=operating_hours/18.
    for i,case in enumerate(CASES):
        auxiliary=fsum(z['service']['active_trainsets']*6*z['design']['aux_kw_per_car']*z['requirements']['operating_hours_per_day']*z['requirements']['operating_days_per_year']/z['design']['charge_efficiency'] for z in services)
        station_aux=(access_sites*l['station_aux_kw_each'][i]+l['depot_aux_kw'][i])*operating_hours*operating_days
        annual_energy.append((drive_energy[case]+auxiliary+station_aux)*stat['electricity_iqd_per_kwh'][i]/fx)
        covered=stat['controllers_per_shift'][i]+access_sites*stat['station_staff_per_station_per_shift'][i]
        hours=max(z['requirements']['operating_hours_per_day'] for z in services);shifts=2 if hours<=18 else 3
        wage=context['assumptions']['benchmark_rates_iqd']['wage_skilled_iqd_per_h']*stat['wage_burden_multipliers'][i]*(1+(stat['second_shift_wage_premium'][i]+(stat['third_shift_wage_premium'][i] if shifts==3 else 0))/shifts)
        annual_ops.append(covered*hours*operating_days*stat['operations_reliever_multiplier'][i]*wage/fx*transfer[i])
        maintained=fsum(z['costs_usd'][case] for z in capital if z['scope'] in ('rolling-stock','guideway','stations-power','land-utilities-depot'))
        annual_maintenance.append(maintained*l['maintenance_fraction'][i]*hours/18)
    for key,scope,annual,basis in [('network-electricity','energy',annual_energy,'Actual line service train-km, launch work or separately labelled powered-axle energy range, auxiliaries and station/depot loads.'),('network-workforce','operations',annual_ops,'Covered controls and unique access-site staff, two/three shifts, employer burden and relief.'),('network-routine-maintenance','maintenance',annual_maintenance,'Routine work/consumables reserve separated from scheduled replacements.'),('network-corrective-disruption','reliability',[annual_km*z/fx for z in stat['reliability_iqd_per_train_km']],'Train-km corrective/disruption reserve, no demonstrated availability.'),('network-recovery-standby','recovery',[rescue*z/fx for z in stat['rescue_standby_iqd_per_year']],'Nonzero standby for separately purchased protected recovery assets.')]:
        add(life,key,scope,dict(annual_usd=annual,annuity=annuity),[v*annuity for v in annual],basis)
    renewal=[0.,0.,0.];events=[]
    for row in capital:
        if row['life_years'] is None:continue
        for i,case in enumerate(CASES):
            for year in model_cost.replacement_event_times(years,row['life_years'][i]/exposure):
                amount=row['costs_usd'][case]
                if row['key']=='network-delivered-assembled-fleet':amount+=vehicle_campaign[i]
                pv=amount/(1+discount)**year;renewal[i]+=pv;events.append(dict(line_id=row['line_id'],case=case,year=year,present_value_usd=pv))
    # Service-battery account resets when complete fleet is renewed.
    services_account=next(z for z in vc['lines'] if z['line_key']=='unlocated-account/services')
    from engineering.development_baseline.system_cost import component_renewal_schedule
    for i,case in enumerate(CASES):
        parents=model_cost.replacement_event_times(years,l['vehicle_life_years'][i]/exposure);schedule=component_renewal_schedule(years,l['service_battery_life_years'][i]/exposure,parents)
        for e in schedule['events']:
            if e.get('covered_by_parent_replacement',False):continue
            amount=services_account['cost_iqd'][case]/vc['mass_reserve_sensitivity']['case_factors'][case]*fleet/fx/(1+discount)**e['year'];renewal[i]+=amount;events.append(dict(component='service-battery-account',case=case,year=e['year'],present_value_usd=amount))
    add(life,'disjoint-scheduled-renewals','renewals',dict(events=events),renewal,'Initial disjoint asset lives; full fleet renewal includes one new vehicle production campaign; service-account age resets at fleet replacement.')
    totals={c:fsum(z['costs_usd'][c] for z in capital) for c in CASES}
    add(life,'final-removal-disposal','disposal',dict(year=30),[totals[c]*l['decommission_fraction'][i]/(1+discount)**30 for i,c in enumerate(CASES)],'Nonzero year-30 removal/disposal; no speculative salvage.')
    scopes={s:{c:fsum(z['costs_usd'][c] for z in capital+life if z['scope']==s) for c in CASES} for s in model_cost.SCOPES}
    if any(scopes[s]['base']<=0 for s in model_cost.SCOPES):raise ValueError('All fourteen city cost scopes must be represented')
    sources={**context.get('sources',{}),**city.get('source_sha256',{}),**civil['source_sha256'],**v['source_sha256'],PRODUCER:digest(root/PRODUCER)}
    for row in services:sources.update(row.get('source_sha256',{}))
    result=dict(schema='osr-city-project-cost/1',city_input_id=city['input_id'],city=city['city'],capital_lines=capital,lifecycle_lines=life,
        scope_totals_usd=scopes,installed_capital_usd=totals,whole_life_npv_usd={c:totals[c]+fsum(z['costs_usd'][c] for z in life) for c in CASES},
        price_per_route_km_usd={c:totals[c]/(route/1000) for c in CASES},
        resources=dict(network_route_km=route/1000,network_lines=len(ids),radial_lines=sum(z['shape']=='radial' for z in city['lines']),ring_lines=sum(z['shape']=='ring' for z in city['lines']),line_stop_records=station_rows,access_sites=access_sites,interchanges=interchanges,total_trainsets=fleet,totalcars=cars,depot_area_m2=depot_area,production_positions_per_shift=positions,vehicle_campaign_capital_usd=dict(zip(CASES,vehicle_campaign)),civil_campaign_capital_usd=dict(zip(CASES,civil_campaign)),annual_train_km=annual_km,annual_energy_usd=dict(zip(CASES,annual_energy)),annual_operations_usd=dict(zip(CASES,annual_ops)),production_shifts=2,civil_shifts=2,accounting_years=30),
        assumptions=dict(policy=p,civil=civil['assumptions'],pricing_basis='Class C source-bound Iraq/China material, equipment and process templates with explicit foreign transfer ranges; not verified local city prices or supplier quotes.',
            quantities_derived_from='Mapped line lengths, complete civil classes, actual line service/fleet and explicit interchange platform grouping',costs_borrowed='Current selected vehicle accounts; CSO process/wage/concrete and China finished/material observations; scenario rates remain provisional.',
            station_launch_lines=launch_ids,powered_axle_research_lines=fallback_ids,bounded_chosen_concept_not_global_optimum=True,
            central_depot_connections_unqualified=True,civil_added_mass_kg_per_car_hypothesis=civil_context['spec']['design']['added_vehicle_mass_kg_per_car'],civil_uses_maximum_declared_traction_mass_across_lines=True,no_historical_capacity_or_cost_results_used=True,
            source_country=city['city'].get('country'),local_rates_verified=False,native_solvers=0),
        civil=civil,production_supply=v,source_sha256=sources,sources=sources,pricing_basis='calculated-outline-Class-C',**FLAGS)
    result['evaluation_id']=identity(result);return result
