"""Readable current city and national dossiers from one authenticated outline."""
from collections import defaultdict
from math import atan2, degrees, fsum
from pathlib import Path
from urllib.parse import quote
import os
import re

CASES=('low','base','high')


def text(value):
    if value is None:return 'Unestablished'
    return str(value).replace('|',' / ').replace('\n',' ')


def number(value,places=0):
    if value is None:return 'Unestablished'
    return f'{value:,.{places}f}'


def money(value):
    if value is None:return 'Unestablished'
    if abs(value)>=1e9:return f'${value/1e9:,.3f}bn'
    if abs(value)>=1e6:return f'${value/1e6:,.2f}m'
    return f'${value:,.0f}'


def label(key):
    return key.replace('_',' ').replace('-',' ').capitalize().replace('Usd','US$').replace('Fte','FTE').replace('Kwh','kWh')


def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join('---' for _ in headers)+'|',
        *['| '+' | '.join(text(x) for x in row)+' |' for row in rows]])


def cases(values):
    return [money(values.get(c)) for c in CASES]


def link(directory,target):
    return quote(Path(os.path.relpath(target,directory)).as_posix(),safe='/-._?=')


def _natural(value):
    return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)',value)]


def _endpoints(line,centre):
    stops=line.get('operational_stops') or line.get('original_stops') or []
    if not stops:return 'Unassigned'
    def compass(stop):
        lon,lat=stop.get('lon'),stop.get('lat')
        if lon is None or lat is None:return 'Mapped stop'
        angle=(degrees(atan2(lon-centre[0],lat-centre[1]))+360)%360
        return ['N','NE','E','SE','S','SW','W','NW'][int((angle+22.5)//45)%8]
    if line.get('shape')=='ring':return 'Ring / closed circuit'
    return compass(stops[0])+' terminal ↔ '+compass(stops[-1])+' terminal'


def _flat_rows(rows, maximum=8):
    if not rows:return 'No rows are established by the current source.'
    keys=list(dict.fromkeys(k for r in rows for k,v in r.items() if not isinstance(v,(dict,list))
        and not k.endswith('_id') and k not in ('basis','source','source_sha256')))
    if len(keys)>8:keys=keys[:8]
    return table([label(k) for k in keys],[[number(v,2) if isinstance(v,(int,float)) and not isinstance(v,bool) else v
        for v in [r.get(k) for k in keys]] for r in rows[:maximum]])


def _finance(finance):
    if not finance.get('enabled'):return ['No passenger-receipt scenario is enabled.','']
    a=finance['assumptions'];rows=finance['scenario_rows']
    base=[r for r in rows if r['cost_case']=='base']
    out=[table(['Demand sensitivity','Assumed annual paid trips','Fare US$','Annual receipts','Operating balance','30-year receipts less costs NPV','Post-grace DSCR'],[
        (number(r['demand_multiplier']*100)+'%',number(r['assumed_annual_paid_linked_trips']/1e6,2)+'m',
         number(r['fare_usd_per_paid_trip'],2),money(r['annual_revenue_usd']),money(r['annual_operating_balance_usd']),
         money(r['unfinanced_revenue_less_whole_life_cost_npv_usd']),number(r.get('illustrative_post_grace_DSCR'),2)) for r in base]),'',
        'This table holds the engineering cost case at **base** and varies demand and fare. A negative balance is retained as a financing/design warning. '
        'Operating balance excludes scheduled renewal capital and debt service; the whole-life NPV column uses the complete unfinanced cost.','',
        table(['Demand hypothesis','Value'],[
            ('Counter-direction peak fraction',number(a['reverse_direction_peak_fraction']*100)+'%'),
            ('Mean section / peak section loading',number(a['mean_section_to_peak_section_load_ratio']*100)+'%'),
            ('Average trip / line length',number(a['average_trip_fraction_of_line_length']*100)+'%'),
            ('Boardings per linked trip',number(a['boardings_per_linked_trip'],2)),
            ('Paid collection fraction',number(a['collection_fraction']*100)+'%'),
            ('Daily profile','; '.join(number(z['fraction_of_service_hours']*100,1)+'% of hours at '+number(z['peak_flow_fraction']*100)+'% peak flow' for z in a['time_profile'])),
        ]),'']
    financing=finance.get('financing',{})
    if financing.get('debt_modelled'):
        debt=financing['assumptions']
        out += ['**Illustrative funding overlay:** '+number(debt['financed_share']*100)+'% financed, '+number(debt['real_interest_rate']*100)+'% real annual interest, '
            +str(debt['term_years'])+' years including '+str(debt['grace_years'])+' years without payments and with capitalised interest. '
            'The model draws the entire loan at year zero; a real construction draw schedule requires its own dated plan. DSCR compares annual receipts less operating provision with level post-grace debt service; no lender acceptance is implied.','']
        unique={r['cost_case']:r for r in rows}
        out += [table(['Cost case','Illustrative loan principal','Equity / grant requirement','Post-grace annual debt service'],[
            (c,money(unique[c]['illustrative_financed_principal_usd']),money(unique[c]['illustrative_equity_or_grant_requirement_usd']),
             money(unique[c]['illustrative_annual_debt_service_after_grace_usd'])) for c in CASES]),'']
    return out


def _drive_comparison(packet,detail):
    outlines={x['line_id']:x for x in detail['line_outlines']}
    rows=[];reasons=[]
    for line in sorted(packet['lines'],key=lambda x:_natural(x['line_id'])):
        h=line['propulsion_hypothesis'];s=line['service']
        rows.append((line['line_id'],str(h.get('traction_motors_per_car'))+' / '+number(h.get('traction_rated_kw_per_car'),1)+' kW',
            number(h.get('continuous_feed_route_m',0)/1000,2)+' km',
            number(s.get('peak_train_force_N')/1000,1)+' kN' if s.get('peak_train_force_N') is not None else 'Unestablished',
            number(s.get('peak_train_mechanical_power_W')/1e6,2)+' MW' if s.get('peak_train_mechanical_power_W') is not None else 'Unestablished',
            number(s.get('jerk_full_train_fin_launch_envelope_m'),1)+' m' if h.get('kind')=='station-launch-reference' else 'Other interface',
            'Unestablished' if s.get('actual_available_force_map') is None else 'Declared map; inspect its evidence'))
        failed=outlines[line['line_id']].get('known_reference_failures',[])
        if failed:
            worst=max(failed,key=lambda x:x.get('distance_m',0));profile=worst.get('reference_profile',{})
            reason=profile.get('reason',worst.get('status','See source failure'))
            reasons.append((line['line_id'],len(failed),label(reason),number(worst.get('distance_m'),1)+' m',
                number(profile.get('maximum_flat_coast_reach_m'),1)+' m'))
    out=[table(['Line','Motors/car / rated kW per car','Continuous feed','Required train force','Required mechanical peak','Station-fin comparison envelope','Actual force map'],rows),'',
        'These are declared requirements and equipment hypotheses, not measured motor capability. A station-launch row retains an unselected wayside mechanism and priced equipment provision. '
        'The station-fin comparison envelope does not prescribe installed motor length or apply to an onboard-traction interface. '
        'Independent friction braking, collector/electrical protection and protected recovery remain required for every concept.','']
    if reasons:
        out += ['### Why some lines use a research alternative','',
            'The table retains the rejected station-only reference screen. An alternative is selected for conditional outline calculation where that reference cannot meet the declared leg; '
            'this does not prove every station-powered design impossible or qualify the replacement hardware.','',
            table(['Line','Affected reference legs','Necessary-bound failure','Longest affected leg','Reference flat coast reach'],reasons),'']
    return out


def _organisation(model):
    policy=model['assumptions']['policy']['staffing']
    ops=next(x for x in model['workforce'] if x['domain']=='operations' and x['case']=='base')
    controllers=policy['controllers_per_shift'][1];access=ops['positions_per_shift']-controllers
    fte_per_position=ops['paid_fte_equivalent']/ops['positions_per_shift']
    return [table(['Function / skills','Base coverage posts','Paid FTE','Authority / staffing boundary'],[
        ('Control room / dispatch / response',number(controllers),number(controllers*fte_per_position,1),'Source control/access coverage; operations authority requires separate assurance'),
        ('Station and access-site service',number(access),number(access*fte_per_position,1),'Source access coverage; accessible assistance and local duties require roster design'),
        ('Vehicle workshop / electrical / brakes','Unestablished','Unestablished','Maintenance budget envelope exists; detailed roles, competence and productive hours require routing'),
        ('Civil infrastructure / track / inspections','Unestablished','Unestablished','Maintenance scope exists; inspection tasks and geographic workload require a site plan'),
        ('Station power / propulsion / controls','Unestablished','Unestablished','Qualified equipment-specific maintenance and protection work'),
        ('Cleaning / security / passenger emergencies','Unestablished','Unestablished','Site/service responsibilities and employee/contractor allocation remain to be sized'),
        ('Programme management / procurement / finance / HR','Unestablished','Unestablished','Business entity, reporting lines and operating overhead allocation require review'),
        ('Training / competence / independent assurance','Unestablished','Unestablished','Independent release authority and competence records remain mandatory'),
    ]),'',
    '**Staffing boundary:** the operations rows size control-room and access-site coverage only. They are not the complete operating company. '
    'Unallocated maintenance/support functions have budget envelopes or open allocation; their unknown FTE is not zero. No recruitment or complete-organisation claim follows from this table.','']


def _civil_price_comparison(model):
    comparison=model['costs'].get('civil_comparison')
    if not comparison:return []
    return ['### Civil classification comparison','',
        'The headline retains the mapped civil allowances. A separate alternative uses the retained '
        'WorldCover/OSM water evidence to distinguish water crossings from other bridge allowances. '
        'Dry land does not establish that a bridge is unnecessary: roads, utilities, clearances and ground conditions remain unsurveyed.','',
        table(['Same-route, same-service estimate','Low','Base','High'],[
            ['Headline installed capital',*cases(model['costs']['installed_capital_usd'])],
            ['Water-evidence alternative capital',*cases(comparison['installed_capital_usd'])],
            ['Alternative capital / route-km',*cases(comparison['price_per_route_km_usd'])],
            ['Alternative whole-life NPV',*cases(comparison['whole_life_npv_usd'])],
            ['Included non-water obstruction reserve',*cases(comparison['obstruction_reserve_usd'])],
        ]),'',
        number(comparison['dry_bridge_reclassified_m']/1000,2)+' km of legacy bridge allowance is represented as elevated construction plus an explicit obstruction reserve in this alternative. '
        +str(comparison['interface_hold_count'])+' water/civil interface holds require investigation. '
        'The reserve is a provisional estimate, not evidence that the crossing work is fully sized. '
        'Historical evidence revision: `'+comparison['historical_revision'][:12]+'`. '
        'This comparison does not select a new alignment, civil design or physical baseline.','']


def city(model,packet,detail,row,root):
    directory=Path(row['path']);city=packet['city'];name=city['name'];slug=city['slug']
    p='engineering/outline/';policy=packet['assumptions']['policy'];cost=packet['costs'];r=packet['resources'];q=packet['civil']['quantities']
    lines=sorted(packet['lines'],key=lambda x:_natural(x['line_id']));stats=packet['summary'];w=detail['delivery_draft']['workforce']
    centres=[pt for line in lines for pt in (line['coordinates'][0],line['coordinates'][-1])]
    centre=(fsum(pt[0] for pt in centres)/len(centres),fsum(pt[1] for pt in centres)/len(centres))
    rel=lambda target:link(directory,target)
    out=[f'# {name} — railway design and city programme','',
        f"**{city['country']} · Calculated outline complete · Class C estimates · Physical verification pending**",'',
        f"[City index]({rel('cities/catalogue/README.md')}) · [National programme](../NATIONAL-BRIEF.md) · "
        f"[Interactive map]({rel('docs/workbench/current/index.html?outlineCity='+slug)}) · "
        f"[Planning workspace]({rel('docs/workbench/planning/index.html?city='+slug)}) · "
        f"[Methods and assumptions]({rel('docs/design-engine/city-dossiers/README.md')})",'',
        f'![{name} current calculated railway network with operational platforms and geographic context]({p}network.svg)','',
        f'[Open full-size map]({p}network.svg) · [Download GIS bundle]({p}gis.zip) · [Complete dossier data]({p}summary.json)','',
        '## City and network','',
        'This city programme uses its exact selected mapped alignment, vehicle reference, service calculation and cost ledger. '
        'Demand, site and unit-rate assumptions support a complete outline for comparison; they do not substitute for surveys, detailed engineering or operational approval.','']
    population=city.get('population_retained_unaccepted')
    network=model.get('network',{})
    out += [table(['Network measure','Current outline'],[
        ('Population context',number(population)+' — retained planning input; not a demand survey' if population is not None else 'Unestablished'),
        ('Selected alignment',label(packet['identity']['selected_alignment_kind'])),
        ('Route length / trackways',number(stats['route_km'],2)+' km / '+str(policy.get('trackways',2))+' trackways'),
        ('Lines / operational platform groups',str(stats['lines'])+' / '+str(stats['operational_station_complexes'])),
        ('Original access markers / separately costed access sites',str(stats['original_stop_records'])+' / '+str(r['access_sites'])),
        ('Explicit interchange references',len(packet['interchanges'])),
        ('Fleet including reserve',str(stats['total_trainsets'])+' six-car trainsets'),
        ('Train distance',number(stats['train_km_per_day'])+' train-km/day; '+number(stats['annual_train_km'])+' /year'),
        ('Service span',str(policy['operating_hours_per_day'])+' h/day, '+str(policy['operating_days_per_year'])+' days/year; clock timetable not yet assigned'),
        ('Peak demand brief',number(policy['peak_demand_pphpd'])+' passengers/h/direction per line — assumed, not additive network ridership'),
        ('Planning occupancy / availability',number(policy['planning_occupancy']*100,0)+'% / '+number(policy['planning_availability_assumption']*100,0)+'% — assumptions'),
    ]),'',
    'Operational platform groups are counted per line. Interchange access sites and original markers are separate quantities; none is silently treated as a unique city-wide station count. '
    'Catchment and access scenarios are described below; authenticated population coverage and demand forecasts remain open.','',
    '### Lines, service and fleet','',table(['Line','Route km','Platform groups','Headway s','One-way / circuit min','Active + reserve','Usable pphpd','Mapped termini'],[
        (line['line_id'],number(line['route_m']/1000,2),len(line.get('operational_stops',[])),
         number(line['metrics']['headway_s']),number(line['metrics']['one_way_s']/60,1),
         str(line['metrics']['active_trainsets'])+' + '+str(line['metrics']['spare_trainsets']),
         number(line['metrics']['planning_usable_capacity_pphpd']),_endpoints(line,centre)) for line in lines]),'',
    'Compass termini describe mapped endpoint positions relative to the network centre; official station names require local planning. '
    'The six-car reference provides 276 normal passenger places, including wheelchair places, with no planned standing. '
    'Headway is a calculated service choice. Journey times are conditional calculations; protected signalling timetables and actual available thrust remain separate work.','',
    f'[Line details and energy]({p}lines.csv) · [Station and access register]({p}stations.csv)','']
    if network.get('connected_line_components') is not None:
        components=network['connected_line_components']
        out += ['### Connections and access','',
            'Declared transfer graph: '+str(len(components))+' connected line group(s): '+'; '.join(', '.join(z) for z in components)+'. '
            'These are explicit planned connections; walking paths and accessible interchange layouts are not yet surveyed.','']
    access=model.get('access',{})
    if access:
        out += ['<details><summary>Access and catchment assumptions</summary>','',
            'Geometric access scenarios are separate from measured population coverage. Full assumptions and outputs are in the dossier data.','',
            _flat_rows(access.get('scenarios',[])), '', '</details>','']
    energy=model['energy']
    priced_energy=energy.get('priced_supply_scenarios',{}).get('cases',{})
    cost_inputs=model['costs'].get('local_cost_inputs',{})
    out += ['## Energy and propulsion','',table(['Energy measure','Daily','Annual'],[
        ('Mechanical traction work',number(energy.get('mechanical_traction_kwh_per_day'))+' kWh mechanical',number(energy.get('mechanical_traction_kwh_per_year')/1e6,2)+' GWh mechanical' if energy.get('mechanical_traction_kwh_per_year') is not None else 'Unestablished'),
        ('Nominal auxiliary load',number(energy.get('auxiliary_load_kwh_per_day'))+' kWh',number(energy.get('auxiliary_load_kwh_per_year')/1e6,2)+' GWh' if energy.get('auxiliary_load_kwh_per_year') is not None else 'Unestablished'),
        ('Auxiliary supply including scenario charging losses',number(energy.get('auxiliary_grid_kwh_per_day'))+' kWh',number(energy.get('auxiliary_grid_kwh_per_year')/1e6,2)+' GWh' if energy.get('auxiliary_grid_kwh_per_year') is not None else 'Unestablished'),
        ('Reserve-fleet auxiliary supply scenario','See annual budget',number(priced_energy.get('base',{}).get('reserve_vehicle_aux_grid_kwh',0.)/1e6,2)+' GWh' if priced_energy else 'Unestablished'),
        ('Total priced grid-supply scenario','See annual budget',number(priced_energy.get('base',{}).get('total_grid_kwh',0.)/1e6,2)+' GWh' if priced_energy else 'Unestablished'),
        ('Physically supported total grid demand','Unestablished','Unestablished'),
    ]),'',table(['Annual electricity budget','Low','Base','High'],[
        ['Priced supply/efficiency scenario',*cases(r['annual_energy_usd'])]]),'',
    'Mechanical work is distinct from electricity purchased. The monetary electricity scenarios include declared efficiency and site-load assumptions; '
    'they do not establish a measured motor map, solar plant, storage installation or self-sufficient energy supply. '
    'Each line retains its candidate-specific launch, braking and recovery requirements in the complete record.','',
    table(['Line','Propulsion research concept','Additional traction mass / car','Additional reserve / car'],[
        (line['line_id'],label(line['propulsion_hypothesis'].get('kind','Unestablished')),
         number(line['service'].get('added_research_traction_mass_kg_per_car'))+' kg',
         number(line['service'].get('added_vehicle_mass_reserve_kg_per_car'))+' kg') for line in lines]),'',
    'The city research configuration is separate from the selected passive reference vehicle. Onboard-traction comparisons carry their own additional mass and cost assumptions; '
    'they do not silently change that reference or establish complete installed equipment.','',
    *_drive_comparison(packet,detail),
    '## Civil works, depot and manufacture','',table(['Quantity / resource','Calculated requirement'],[
        *[(label(k)+' route',number(v/1000,2)+' km') for k,v in q['class_route_m'].items()],
        ('Precast span stock',number(q['span_count'])+' spans'),('Independent supports',number(q['independent_supports'])),
        ('Running rail',number(q['rail_m']/1000,2)+' rail-km / '+number(q['rail_kg']/1000)+' t'),
        ('Complete fastening sets',number(q['fastener_sets'])),('Protected at-grade crossing packages',number(q['at_grade_crossing_packages'])),
        ('Bridge runs / tunnel portals',str(q['bridge_runs'])+' / '+str(q['tunnel_portals'])),
        ('Additional station track',number(q['additional_station_track_m'])+' m'),
        ('Access connector allowance',number(r['access_repair_walkway_m'],1)+' m; actual accessible paths require survey'),
        ('Pooled depot area',number(r['depot_area_m2'])+' m²; location and line connections require a site plan'),
        ('Factory / civil working pattern',str(r['production_shifts'])+' / '+str(r['civil_shifts'])+' shifts/day'),
    ]),'',
    'Civil classes and quantities follow the mapped scenario. Foundation capacities, bearings, erection stability, river crossings, utilities and ground conditions require site-specific design. '
    'The depot allowance includes pooled storage/workshop scope and budgeted connections; it does not identify an acquired or physically connected depot site.','',
    '### Factory capacity and make/buy','',table(['Factory investment','Low','Base','High'],[
        ['Vehicle equipment, tooling and premises',*cases(r['vehicle_campaign_capital_usd'])],
        ['Civil production campaign',*cases(r['civil_campaign_capital_usd'])],
    ]),'',
    'Factory capital is already included in the city capital ledger. It must not be added a second time. '
    'Make/buy comparisons use committed city volume, equipment/tooling, material, labour, yield and productive capacity; no speculative future-city discount is assumed.','',
    table(['Component / process','Provisional route'],[
        (z.get('item'),z.get('selected_route')) for z in model.get('tables',{}).get('make_buy',[]) if 'case' not in z]),'',
    table(['Precast case','Selected route','Parallel cells','Required cell-hours','Productive person-hours','Paid person-hours'],[
        (z['case'],z.get('selected_route'),number(z.get('cell_count')),number(z.get('required_cell_hours')),
         number(z.get('productive_person_hours')),number(z.get('paid_person_hours')))
        for z in model.get('tables',{}).get('make_buy',[]) if 'case' in z]),'',
    f'[Complete manufacturing routes and comparisons]({p}make_buy.csv) · [Quantities and delivery requirements]({p}delivery_requirements.csv) · '
    f'[Vehicle, station and civil 3D models]({rel('docs/engineering-models/README.md')})','',
    '## Workforce and construction programme','',
    'Production and civil works use two shifts. The operating case uses '+str(w['operations_hours_per_day'])+' service hours/day and a '+str(w['operations_shifts'])+'-shift planning convention; '
    'named-worker rosters, shift lengths, relief and local employment requirements need an approved calendar. Extended operation can require three shifts.','',
    table(['Domain / case','Covered positions per shift','Two-shift people floor','Paid person-hours','Paid FTE equivalent'],[
        (('Control room and access-site coverage' if z.get('domain')=='operations' else label(z.get('domain','')))+' / '+text(z.get('case')),number(z.get('positions_per_shift')),
         number(z.get('distinct_two_shift_people')),
         number(z.get('paid_person_hours')),number(z.get('paid_fte_equivalent'),1)) for z in model.get('workforce',[])]),'',
    'Paid FTE is a budgeting convention, distinct from simultaneous posts and named employees. Source labour and relief are already in the priced model; this staffing view does not add another payroll charge.','',
    *_organisation(model),
    'The provisional delivery sequence is: '+ ' → '.join(label(x) for x in detail['delivery_draft']['phase_order'])+'. '
    'Factories, field crews and access must be checked together. Aggregate resource envelopes are distinct from resource-levelled, site-approved construction schedules.','',
    f'[Workforce cases]({p}workforce.csv) · [Production and construction requirements]({p}delivery_requirements.csv)','',
    '## Capital, operating costs and whole-life economics','',
    table(['Programme estimate','Low','Base','High'],[
        ['Installed capital',*cases(cost['installed_capital_usd'])],
        ['Installed capital / route-km',*cases(cost['price_per_route_km_usd'])],
        [str(policy['accounting_horizon_years'])+'-year whole-life NPV',*cases(cost['whole_life_npv_usd'])],
        ['Annual operating provision',*cases(model['costs']['annual_opex_usd'])],
    ]),'',
    'US dollars, '+number(policy['real_discount_rate']*100)+'% real discount rate, '+str(policy['accounting_horizon_years'])+'-year horizon. '
    'Low/base/high are assumption cases, not statistical confidence intervals. Transferred sourcing and construction rates require local calibration.','',
    table(['Scope','Installed capital · base','Whole-life NPV · base'],[
        (label(scope),money(model['costs']['capital_by_scope_usd'].get(scope,{}).get('base')),
         money(values['base'])) for scope,values in model['costs']['whole_life_by_scope_usd'].items()]),'',
    f'[Full capital and lifecycle ledger]({p}costs.csv)','',
    '### Price inputs and confidence','',
    'These are calculated v0.6-derived outline prices. Country-specific demand, ground conditions, local contracts and supplier quotations are not established by this calculation. '
    'The price includes the declared mixed propulsion research configurations shown above; it is not a quotation for an already proven station-powered railway.','',
    table(['Operating input','Low','Base','High'],[
        ['Electricity · US$/kWh',*[number(v,3) for v in cost_inputs.get('values',{}).get('electricity_usd_per_kwh',[None]*3)]],
        ['Loaded operating wage · US$/paid hour',*[number(v,2) for v in cost_inputs.get('values',{}).get('operations_loaded_paid_wage_usd_h',[None]*3)]],
    ]),'',
    'Input status: '+text(cost_inputs.get('status','Reference transfer, not locally verified'))+'. '
    'Scoped local tariff/wage overrides can replace those accounts; they do not apply a blanket discount to imported equipment or civil quantities. '
    'Reserve-fleet auxiliary consumption and charging losses are included in the electricity budget.','',
    table(['Largest capital allowance','Base estimate','Share of capital'],[
        [label(r['key']),money(r['base_usd']),number(100*r['capital_share'],1)+'%']
        for r in model['costs'].get('estimate_review',{}).get('largest_capital_accounts',[])]),'',
    f'[Annual energy budget]({p}energy_budget.csv) · [Local operating inputs]({p}local_cost_inputs.csv)','',
    *_civil_price_comparison(model),
    '### Passenger receipts and funding scenarios','',
    'The following sensitivities use explicitly assumed daily demand profiles, average trip length, transfers, paid-trip collection and fares. '
    'They are calculated planning scenarios, not surveyed ridership or an approved financing plan. Import origin and financing source are distinct: '
    'no local/import share or foreign-turnkey saving is asserted without an evidenced procurement allocation.','',
    *_finance(model.get('finance',{})),
    f'[All demand, fare and funding sensitivities]({p}finance.csv). Assumptions, cost-covering fares and financing treatment are in [the complete dossier]({p}summary.json). '
    'Funding charges are separate from the canonical unfinanced engineering cost; a loan scenario does not change the railway capital ledger.','',
    '## Site, engineering and delivery evidence','',
    table(['Work package','Current basis','Next evidence / action'],[
        ('Network and alignment','Mapped selected proposal and explicit interchange references','Survey alignment, land/access, gradients, clearances and crossing interfaces'),
        ('Demand and accessibility','Declared peak-flow brief and outline passenger configuration','Local OD/demand validation, station naming, accessible walking and evacuation layouts'),
        ('Ground, flood and utilities','Mapped civil classes and bounded site allowances','Survey control, utility records, geotechnical investigation, flood/drainage and foundation design'),
        ('Vehicle and civil structure','Identified reference parts, mass allowances and priced quantities','Installed mass/CG, joints, fatigue, stability, bearings, moving loads and erection checks'),
        ('Propulsion, energy and braking','Conditional force/energy/service model','Achievable force/thermal maps, independent braking, protected recovery and degraded journeys'),
        ('Manufacturing and workforce','Calculated make/buy, tooling, shifts and resource envelopes','Detailed routing, QA, crew/workstation calendar, supplier confirmation and trial production'),
        ('Business execution','Candidate-bound disabled procurement/BOM/HR drafts','Target-system schema validation, reviewed masters, permissions and approved release'),
    ]),'',
    'Outline completion is recorded positively. Physical engineering, prototype validation, procurement approval, manufacturing release and movement authority remain separate. '
    f'[Candidate-bound physical evidence record](engineering/current/README.md).','',
    '## Files and reproduction','',
    table(['File','Contents'],[
        (f'[Summary]({p}summary.json)','Complete calculation-linked dossier and scenario policy'),
        (f'[Map]({p}network.svg)','Selected network over verified geographic context'),
        (f'[Lines]({p}lines.csv) / [stations]({p}stations.csv)','Service, fleet, section/stop/access references'),
        (f'[GIS bundle]({p}gis.zip)','Eight GeoJSON layers: routes, platforms, stations, original markers, interchanges, connectors, civil classes and unlocated requirements'),
        (f'[Costs]({p}costs.csv) / [finance]({p}finance.csv)','Canonical budgets and separate passenger/funding sensitivities'),
        (f'[Workforce]({p}workforce.csv) / [make-buy]({p}make_buy.csv)','Shift, resource and production comparisons'),
        (f'[Delivery requirements]({p}delivery_requirements.csv)','Provisional phase/resource and site tasks'),
        (f'[Delivery and business drafts]({p}delivery-draft.json.gz)','Source-bound procurement packages, provisional BOM/routing and disabled ERPNext/Frappe HR records'),
        (f'[Source identities]({p}manifest.json)','Presentation, atlas, outline, physical candidate and output hashes'),
        (f'[Current outline record]({rel('docs/design-engine/city-atlas/cities/'+slug+'.json.gz')})','Same-candidate service, costs and selected geometry'),
        ('[Geographic source](city.json) / [context](map-context.json.gz)','Planning inputs and attribution'),
    ]),'',
    '```sh','python -m engineering.city_reports.publication publish','python -m engineering.city_reports.publication verify','```','',
    'A recalculated local study can be opened, edited and exported in the Workbench. The published city page remains bound to the selected published outline until regenerated.','',
    f"[Earlier city source dossier](https://github.com/modernecotech/OpenSourceRail/tree/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/{quote(row['path'],safe='/')}) preserves the former reports and downloads under their own vehicle, energy and finance assumptions. Those results are not used as current evidence.",'',
    '<details><summary>Candidate and calculation identities</summary>','',
    table(['Identity','Value'],[(k,'`'+str(v)+'`') for k,v in packet['identity'].items() if not isinstance(v,dict)]),
    '',f"Atlas packet `{packet['packet_id']}`. Physical reference `{packet['identity']['reference_candidate_ids']['candidate_id']}`.",'',
    '</details>','',f"[Project introduction]({rel('README.md')}) · [Current engineering]({rel('docs/design-engine/current/README.md')})",'']
    if slug=='samawah':
        out += ['[Earlier Line 1 native model and animation](https://github.com/modernecotech/OpenSourceRail/blob/205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e/cities/catalogue/west-asia/Iraq/Samawah/engineering/digital-twin/README.md) remains available as source history with its original configuration.','']
    return '\n'.join(out)


def nations(rows,root):
    groups=defaultdict(list)
    for row in rows:groups[Path(row['path']).parent].append(row)
    output={}
    for directory,cities in groups.items():
        country=directory.name;linkto=lambda path:link(directory,path)
        totals={c:fsum(z['installed_capital_usd'][c] for z in cities) for c in CASES}
        out=[f'# {country} — city railway outline programme','',
            f'{len(cities)} calculated city programmes · {number(fsum(z["route_km"] for z in cities),1)} route-km · '
            f'{sum(z["trainsets"] for z in cities):,} trainsets including reserves.','',
            table(['Standalone city capital total','Low','Base','High'],[['Arithmetic sum',*cases(totals)]]),'',
            'These are standalone city outlines with explicit estimates. Shared factories, inter-city connections, overlapping catchments, national demand and funding must be co-designed before treating this sum as an optimised national programme. Physical approvals remain separate.','',
            table(['City','Route km','Lines','Platform groups','Trainsets','Base installed US$'],[
                ('['+z['city']['name']+']('+linkto(z['path']+'/README.md')+')',number(z['route_km'],1),z['lines'],z['station_complexes'],z['trainsets'],money(z['installed_capital_usd']['base']))
                for z in sorted(cities,key=lambda x:x['city']['name'])]),'',
            f"[All cities]({linkto('cities/catalogue/README.md')}) · [Calculation and scenario methods]({linkto('docs/design-engine/city-dossiers/README.md')}) · [Project introduction]({linkto('README.md')})",'']
        output[(directory/'NATIONAL-BRIEF.md').as_posix()]='\n'.join(out)
    return output
