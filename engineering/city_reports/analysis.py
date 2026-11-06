"""Pure, bounded presentation calculations for authenticated current city packets.

The caller authenticates files/manifests before calling ``build``. Internal seals
and cross-links checked here establish consistency, not external authentication.
No historical numeric results, solver execution, cost repricing or release occurs.
"""
from copy import deepcopy
import json
from math import ceil, fsum, isclose, isfinite, pi
from pathlib import Path
import re

from engineering.station_rail.common import identity
from engineering.design_search.model_cost import SCOPES

FLAGS = dict.fromkeys(('physical_accepted','engineering_accepted','manufacturing_release',
    'operating_release','procurement_approved','selected_reference_changed','movement_authority',
    'business_records_submitted','global_optimum_established','installed_mass_complete',
    'physical_journey_completed','procurement_ready','physical_reference_changed',
    'timetable_qualified','independent_braking_qualified'), False)
SCHEMA = 'osr-city-dossier-analysis/1'
CASES = ('low', 'base', 'high')
DEFAULT_POLICY = json.loads(Path(__file__).with_name('planning-policy.json').read_text())


def _sealed(value, key):
    if not isinstance(value, dict) or value.get(key) != identity({k:v for k,v in value.items() if k != key}):
        raise ValueError('Dossier input identity differs: '+key)


def _no_release(value):
    for key in FLAGS:
        if key in value and value[key] is not False:
            raise ValueError('Dossier inputs must retain false release flags: '+key)


def _number(value, name, *, zero=False):
    if type(value) not in (int, float) or not isfinite(value) or (value < 0 if zero else value <= 0):
        raise ValueError('Finite '+('nonnegative ' if zero else 'positive ')+name+' required')
    return value


def _cases(value, name):
    if isinstance(value, list) and len(value) == 3:
        value = dict(zip(CASES, value))
    if not isinstance(value, dict) or set(value) != set(CASES):
        raise ValueError('Three cost cases required: '+name)
    return {c:_number(value[c], name, zero=True) for c in CASES}


def _same(a, b, name):
    if a != b:
        raise ValueError('Mixed dossier '+name)


def _ordered(line):
    return [int(x) if x.isdigit() else x.lower() for x in re.split(r'(\d+)', line['line_id'])]


def _validate(packet, detail, context):
    _sealed(packet, 'packet_id'); _no_release(packet); _no_release(detail)
    if packet.get('schema') != 'osr-city-atlas/1':
        raise ValueError('Current city atlas packet required')
    _same(packet['city'], detail['city'], 'city')
    ids = packet['identity']; seed = detail['planning_seed']; _sealed(seed, 'seed_id'); _no_release(seed)
    pairs = [('outline_evaluation_id', detail['evaluation_id']), ('city_input_id', detail['input_id']),
        ('cost_evaluation_id', detail['city_cost_evaluation_id']),
        ('research_configuration_id', detail['research_configuration_id']),
        ('selected_alignment_id', detail['selected_alignment_id']),
        ('reference_candidate_ids', detail['reference_candidate_ids']), ('seed_id', seed['seed_id'])]
    for key, expected in pairs:
        _same(ids.get(key), expected, key)
    for key, seed_key in [('city_input_id','selected_city_input_id'), ('service_evaluation_id','selected_service_evaluation_id'),
            ('cost_evaluation_id','source_cost_evaluation_id'), ('outline_evaluation_id','source_outline_evaluation_id'),
            ('research_configuration_id','research_configuration_id'), ('reference_candidate_ids','reference_candidate_ids'),
            ('selected_alignment_id','selected_alignment_id'), ('source_result_sha256','source_result_sha256')]:
        _same(ids.get(key), seed.get(seed_key), 'planning seed '+key)
    if 'selection_id' in detail:
        _same(ids['selection_id'], detail['selection_id'], 'selection')
    if not ids.get('selection_id'):
        raise ValueError('Explicit atlas selection identity required')
    for key in ('installed_capital_usd', 'whole_life_npv_usd', 'scope_totals_usd'):
        _same(packet['costs'][key], detail[key], key)
    draft = detail.get('delivery_draft', {})
    if draft:
        # Publication replaces quantity_takeoff with a compact projection while
        # retaining the original draft ID. Authenticate that projection upstream.
        if not draft.get('draft_id'):raise ValueError('Source delivery draft ID required')
        for key, idkey in [('city_input_id','city_input_id'), ('cost_evaluation_id','cost_evaluation_id'),
            ('research_configuration_id','research_configuration_id'), ('reference_candidate_ids','reference_candidate_ids')]:
            _same(draft[key], ids[idkey], 'delivery '+key)
        erp = draft.get('ERPNext', {})
        if erp.get('disabled') != 1 or erp.get('submitted') is not False or erp.get('external_transactions_performed') is not False:
            raise ValueError('Disabled unsubmitted business records required')
        if draft.get('Frappe_HR', {}).get('submitted') is not False:
            raise ValueError('Unsubmitted workforce records required')
    if context is not None:
        _same(context.get('city', {}).get('slug'), packet['city']['slug'], 'context city')
    seen = set()
    for line in packet['lines']:
        if line['line_id'] in seen:
            raise ValueError('Unique dossier line identities required')
        seen.add(line['line_id']); _no_release(line['service']); _no_release(line['propulsion_hypothesis'])
        _same(line['service'].get('reference_vehicle_candidate_id', ids['reference_candidate_ids']['candidate_id']),
            ids['reference_candidate_ids']['candidate_id'], 'line vehicle candidate')
    return ids, seed


def _line_records(packet, context):
    context_lines = {r.get('line_id', r.get('name')):r for r in (context or {}).get('lines', [])}
    names = {r['id']:r.get('name', r['id']) for r in (context or {}).get('stations', [])}
    lines, stations = [], []
    for line in sorted(packet['lines'], key=_ordered):
        m, s, req = line['metrics'], line['service'], line['requirements']
        hours = _number(req['operating_hours_per_day'], 'service hours')
        days = _number(req['operating_days_per_year'], 'service days')
        headway = _number(req['headway_s'], 'headway')
        stops = sorted(line['operational_stops'], key=lambda r:r.get('chainage_m', 0))
        ctx = context_lines.get(line['line_id'], {})
        termini = ctx.get('termini') or [names.get(stops[0]['id'], stops[0]['id']), names.get(stops[-1]['id'], stops[-1]['id'])]
        row = dict(line_id=line['line_id'], name=ctx.get('name', line['line_id']), shape=line['shape'],
            route_km=line['route_m']/1000, operational_route_km=line.get('operational_route_m',line['route_m'])/1000,
            original_stop_records=len(line['original_stops']), operational_station_complexes=len(stops),
            boarding_edges=s.get('boarding_edges'), platform_length_m=line['design'].get('platform_length_m'),
            terminus_from=str(termini[0]), terminus_to=str(termini[-1]),
            termini_basis='Current context names where supplied; otherwise current operational stop IDs. Rings have no termini.' if line['shape']!='ring' else 'Ring; first/last listed stop are not termini.',
            headway_s=headway, departures_per_hour_per_direction=3600/headway,
            normal_places_per_train=m.get('normal_places_per_train'), capacity_pphpd=m.get('capacity_pphpd'),
            planning_usable_capacity_pphpd=m.get('planning_usable_capacity_pphpd'), peak_demand_pphpd=req['peak_demand_pphpd'],
            demand_source=m.get('demand_source',req.get('demand_source')),
            active_trainsets=s['active_trainsets'], spare_trainsets=s.get('spare_trainsets'), total_trainsets=s['total_trainsets'],
            one_way_minutes=m.get('one_way_s',s['one_way_s'])/60,
            round_trip_minutes=m.get('round_trip_s',s['round_trip_s'])/60,
            operating_hours_per_day=hours, operating_days_per_year=days,
            scheduled_direction_journeys_per_day=2*3600/headway*hours,
            scheduled_direction_journeys_per_year=2*3600/headway*hours*days,
            train_km_per_day=m['train_km_per_day'], annual_train_km=m['annual_train_km'],
            propulsion_kind=line['propulsion_hypothesis']['kind'], service_evaluation_id=line['service_evaluation_id'])
        # Retain per-line energy and propulsion requirements in both readable
        # facts and the scalar CSV table. Requirement envelopes are not maps of
        # actual delivered force, installed powered length or physical release.
        propulsion=line['propulsion_hypothesis']
        force_map=propulsion.get('actual_available_force_map',s.get('actual_available_force_map'))
        force_map_available=force_map is not None and force_map is not False
        for key in ('mechanical_traction_kwh_per_day','auxiliary_load_kwh_per_day','auxiliary_grid_kwh_per_day'):
            row[key]=m.get(key)
            row[key.replace('_per_day','_per_year')]=m[key]*days if m.get(key) is not None else None
        row.update(electrical_traction_kwh_per_day=None,electrical_traction_kwh_per_year=None,
            physical_total_grid_kwh_per_day=None,physical_total_grid_kwh_per_year=None,
            energy_basis=m.get('energy_basis','Calculated mechanical and nominal auxiliary requirements; physical electrical traction and total grid energy unestablished.'),
            propulsion_research_configuration_id=propulsion.get('research_configuration_id'),
            actual_available_force_map_available=force_map_available,
            force_map_status='Supplied map; qualification remains separate' if force_map_available else 'Not supplied; calculated required-force envelope only',
            required_peak_train_force_N=m.get('peak_train_force_N',s.get('peak_train_force_N')),
            required_peak_train_mechanical_power_W=m.get('peak_train_mechanical_power_W',s.get('peak_train_mechanical_power_W')),
            jerk_launch_distance_m=s.get('jerk_launch_distance_m'),
            jerk_full_train_fin_launch_envelope_m=s.get('jerk_full_train_fin_launch_envelope_m'),
            launch_envelope_basis='Calculated jerk envelope; installed powered length and actual drive capability remain unqualified',
            recovery_required=propulsion.get('collector_protection_and_rescue_required'),
            recovery_qualified=propulsion.get('recovery_qualified',s.get('recovery_qualified')),
            recovery_status='Required; qualification evidence not supplied' if propulsion.get('collector_protection_and_rescue_required') and propulsion.get('recovery_qualified',s.get('recovery_qualified')) is not True else 'See source recovery evidence; no inferred acceptance',
            independent_friction_braking_required=propulsion.get('independent_friction_braking_required'),
            independent_braking_qualified=s.get('independent_braking_qualified'),
            known_reference_failure_count=len(line.get('known_reference_failures',[])),
            reference_failure_statuses='; '.join(sorted({r.get('status','unspecified') for r in line.get('known_reference_failures',[])})),
            interface_holds_json=json.dumps(line.get('interface_holds',[]),sort_keys=True,separators=(',',':')))
        if line['shape']=='ring': row.update(terminus_from=None,terminus_to=None)
        lines.append(row)
        for station in line['station_complexes']:
            sid=station['operational_stop_id']; xy=station['coordinates']
            stations.append(dict(line_id=line['line_id'],station_id=sid,name=names.get(sid,sid),
                chainage_m=station['chainage_m'],longitude=xy[0],latitude=xy[1],
                original_marker_count=len(station['original_stop_ids']),
                platform_length_m=station.get('boarding_platform_length_m'),
                maximum_added_walk_m=station.get('maximum_added_walk_m'),
                accessible_path_surveyed=False))
    return lines, stations


def _network(packet, lines):
    graph={l['line_id']:set() for l in lines}; original={s['id']:l['line_id'] for l in packet['lines'] for s in l['original_stops']}
    transfers=[]
    for transfer in packet['interchanges']:
        declared=set(transfer['lines']); actual={original.get(s) for s in transfer['platforms']}
        if None in actual or actual != declared or not declared <= graph.keys():
            raise ValueError('Explicit transfer references do not match current line-platform stops')
        for a in declared:graph[a].update(declared-{a})
        transfers.append(dict(interchange_id=transfer['id'],lines=sorted(declared),platform_stop_ids=list(transfer['platforms'])))
    components=[];remaining=set(graph)
    while remaining:
        stack=[min(remaining)];component=set()
        while stack:
            node=stack.pop()
            if node in component:continue
            component.add(node);stack.extend(graph[node]-component)
        components.append(sorted(component));remaining-=component
    return dict(summary=deepcopy(packet['summary']), connected_line_components=components,
        all_lines_reachable_by_declared_transfers=len(components)==1,
        explicit_transfers=transfers, transfer_access_qualified=False,
        reachability_basis='Undirected line graph using only declared current platform-transfer links; schematic connectivity, not a timed or accessible journey guarantee.',
        peak_flows_additive_as_network_demand=False,
        population_context=dict(value=packet['city'].get('population_retained_unaccepted'),
            role='Retained source population for planning context; date/boundary and catchment demand unaccepted',
            surveyed_demand=False))


def _costs(packet):
    cost=packet['costs']; cap=cost['capital_lines']; life=cost['lifecycle_lines']
    allrows=cap+life
    if len({r['line_id'] for r in allrows})!=len(allrows):raise ValueError('Unique ledger lines required')
    if any(r['scope'] not in SCOPES for r in allrows):raise ValueError('Unknown whole-life scope')
    capital={s:{c:fsum(_cases(r['costs_usd'],'ledger')[c] for r in cap if r['scope']==s) for c in CASES} for s in SCOPES}
    total={s:{c:fsum(_cases(r['costs_usd'],'ledger')[c] for r in allrows if r['scope']==s) for c in CASES} for s in SCOPES}
    annual={s:{c:fsum(_cases(r['quantity']['annual_usd'],'annual OPEX')[c] for r in life if r['scope']==s and 'annual_usd' in r.get('quantity',{})) for c in CASES} for s in SCOPES}
    capsum={c:fsum(capital[s][c] for s in SCOPES) for c in CASES}; wholesum={c:fsum(total[s][c] for s in SCOPES) for c in CASES}
    for c in CASES:
        if not isclose(capsum[c],cost['installed_capital_usd'][c],rel_tol=1e-12,abs_tol=1e-6) or not isclose(wholesum[c],cost['whole_life_npv_usd'][c],rel_tol=1e-12,abs_tol=1e-6):
            raise ValueError('Dossier capital or whole-life ledger does not reconcile')
        for s in SCOPES:
            if not isclose(total[s][c],cost['scope_totals_usd'][s][c],rel_tol=1e-12,abs_tol=1e-6):raise ValueError('Dossier scope ledger does not reconcile')
    records=[dict(stage=stage,scope=s,case=c,amount_usd=value[s][c]) for stage,value in [('capital',capital),('whole-life-NPV',total),('annual-OPEX',annual)] for s in SCOPES for c in CASES]
    return dict(installed_capital_usd=capsum, whole_life_npv_usd=wholesum,
        capital_by_scope_usd=capital,whole_life_by_scope_usd=total,annual_opex_by_scope_usd=annual,
        annual_opex_usd={c:fsum(annual[s][c] for s in SCOPES) for c in CASES},
        reconciliation=dict(capital_residual_usd={c:capsum[c]-cost['installed_capital_usd'][c] for c in CASES},
            whole_life_residual_usd={c:wholesum[c]-cost['whole_life_npv_usd'][c] for c in CASES},all_fourteen_scopes_reconciled=True),
        annual_opex_basis='Only lifecycle quantity.annual_usd accounts; scheduled renewals and disposal remain separate present values. No second workforce, factory or interest charge.',
        imported_cost_share=None,domestic_cost_share=None,origin_basis='Make/buy process route does not establish installed cost origin; cost-bound origin evidence unavailable.'),records


def _workforce(packet, policy):
    p=policy['staffing']; d=policy['delivery']; sources=packet['sources']['calculation_sha256']
    for pathkey in ('cost_source','city_cost_source'):
        if sources.get(p[pathkey]) != p[pathkey+'_sha256']:
            raise ValueError('Costed staffing policy requires exact source binding: '+p[pathkey])
    resources=packet['resources']; capital={r['key']:r for r in packet['costs']['capital_lines']}
    rows=[]; hours=max(l['requirements']['operating_hours_per_day'] for l in packet['lines']); days=max(l['requirements']['operating_days_per_year'] for l in packet['lines'])
    horizon=d['production_years']*d['days_per_year']; hday=d['shifts_per_day']*d['hours_per_shift']*d['utilisation']
    q=packet['civil']['quantities'];dec=packet['civil'].get('factory_decision',{}); cells=[]
    ancillary=[r for r in capital.values() if r['scope'] in ('stations-power','construction','land-utilities-depot') and r['key'] not in ('piers-and-foundations','transport-crane-erection-track-install','city-project-risk-contingency','design-prototypes-independent-review','unallocated-package-tax-duty')]
    for i,c in enumerate(CASES):
        covered=p['controllers_per_shift'][i]+resources['access_sites']*p['station_staff_per_station_per_shift'][i]
        before=covered*hours*days;paid=before*p['operations_reliever_multiplier'][i]
        rows.append(dict(domain='operations',case=c,positions_per_shift=covered,shifts_per_day=2 if hours<=18 else 3,
            distinct_two_shift_people=None,productive_person_hours=None,paid_person_hours=paid,
            paid_fte_equivalent=paid/p['fte_paid_hours_per_year'],relief_multiplier=p['operations_reliever_multiplier'][i],
            paid_hours_per_fte=p['fte_paid_hours_per_year'],basis='Existing costed controls/access-site coverage; relief already costed, no extra payroll charge.'))
        positions=resources['production_positions_per_shift'][i]
        rows.append(dict(domain='vehicle-production',case=c,positions_per_shift=positions,shifts_per_day=2,
            distinct_two_shift_people=2*positions,productive_person_hours=None,paid_person_hours=None,paid_fte_equivalent=None,
            productive_capacity_person_hours=positions*horizon*hday,
            basis='Existing pooled positions include assembly; capacity is not measured work or a fixed three-year payroll. Detailed vehicle process hours unavailable in atlas.'))
        available=max(1,horizon-d['engineering_workdays'][i]-d['plant_setup_workdays'][i]-max(d['imported_lead_workdays'][i],d['support_concrete_wait_workdays'][i])-d['final_test_workdays'][i])
        field=q['independent_supports']*d['support_labour_h_each'][i]+q['span_count']*d['erection_labour_h_span'][i]
        ancillary_hours=fsum(r['costs_usd'][c] for r in ancillary)*d['ancillary_labour_budget_fraction'][i]/d['local_loaded_paid_wage_usd_h'][i]*d['utilisation']
        field_positions=max(d['field_crew'],ceil(field/(available*hday))) if field else 0
        ancillary_positions=max(1,ceil(ancillary_hours/(available*hday))) if ancillary else 0
        make=dec.get('comparison',{}).get('cases',{}).get(c,{}).get('make',{})
        precast_positions=make['cell_count']*d['precast_crew'] if q['span_count'] and dec.get('selected_route')=='make' else 0
        precast_h=make.get('labour_hours') if precast_positions else None
        for domain,n,h in [('civil-field',field_positions,field),('civil-other-installation',ancillary_positions,ancillary_hours),('civil-precast',precast_positions,precast_h)]:
            rows.append(dict(domain=domain,case=c,positions_per_shift=n,shifts_per_day=2,distinct_two_shift_people=2*n,
                productive_person_hours=h,paid_person_hours=h/d['utilisation'] if h is not None else None,paid_fte_equivalent=None,
                available_field_workdays=available if domain!='civil-precast' else None,
                basis='New timeboxed delivery resource hypothesis within existing contractor/cell accounts; no additional cost, executable schedule or employment promise.'))
        if make:
            cells.append(dict(item='structural-precast-beam',case=c,selected_route=dec['selected_route'],
                cell_count=make.get('cell_count') if dec['selected_route']=='make' else None,
                required_cell_hours=make.get('required_cell_hours'),productive_person_hours=make.get('labour_hours'),
                paid_person_hours=make.get('charged_labour_hours'),machine_hours=make.get('machine_hours'),
                hours_basis='Make-option comparison; owned only when selected route is make. Not an executable schedule.'))
    return rows,cells


def _finance(packet, lines, costs, p):
    if not p['enabled']:return dict(enabled=False,illustrative=True,scenario_rows=[])
    profile=p['time_profile']
    if not isclose(fsum(r['fraction_of_service_hours'] for r in profile),1,abs_tol=1e-12):raise ValueError('Time-profile fractions must sum to one')
    for r in profile:
        _number(r['fraction_of_service_hours'],'time fraction',zero=True)
        if not 0<=r['peak_flow_fraction']<=1:raise ValueError('Peak profile fractions must be from zero to one')
    for k in ('reverse_direction_peak_fraction','mean_section_to_peak_section_load_ratio','average_trip_fraction_of_line_length','collection_fraction'):
        _number(p[k],k)
        if p[k]>1:raise ValueError('Planning fractions must be at most one')
    _number(p['boardings_per_linked_trip'],'boardings per linked trip')
    if p['boardings_per_linked_trip']<1:raise ValueError('Transfers cannot reduce boardings per trip below one')
    debt=p.get('debt',{}) if p.get('debt_modelled') else None
    if debt is not None:
        share=_number(debt['financed_share'],'financed share')
        rate=_number(debt['real_interest_rate'],'real loan rate',zero=True)
        term=debt['term_years'];grace=debt['grace_years']
        if share>1 or type(term) is not int or type(grace) is not int or not 0<=grace<term<=100:
            raise ValueError('Bounded loan share, integer term and shorter grace required')
    rows=[];trips=[];policy=packet['assumptions']['policy'];years=policy['accounting_horizon_years'];discount=_number(policy['real_discount_rate'],'discount',zero=True)
    annuity=fsum((1+discount)**-y for y in range(1,years+1))
    equivalent_fraction=fsum(r['fraction_of_service_hours']*r['peak_flow_fraction'] for r in profile)
    base_boardings=fsum(l['peak_demand_pphpd']*(1+p['reverse_direction_peak_fraction'])*l['operating_hours_per_day']*equivalent_fraction*p['mean_section_to_peak_section_load_ratio']/p['average_trip_fraction_of_line_length']*l['operating_days_per_year'] for l in lines)
    for multiplier in p['demand_multipliers']:
        _number(multiplier,'demand multiplier')
        if multiplier>1:raise ValueError('Demand sensitivity cannot exceed the declared peak-flow profile')
        annual=base_boardings*multiplier/p['boardings_per_linked_trip']*p['collection_fraction']
        trips.append(dict(demand_multiplier=multiplier,assumed_annual_boardings=base_boardings*multiplier,assumed_annual_paid_linked_trips=annual))
        for c in CASES:
            for fare in p['fares_usd_per_paid_trip']:
                _number(fare,'fare',zero=True);revenue=annual*fare;pv=revenue*annuity
                rows.append(dict(demand_multiplier=multiplier,cost_case=c,fare_usd_per_paid_trip=fare,
                    assumed_annual_paid_linked_trips=annual,annual_revenue_usd=revenue,
                    annual_opex_usd=costs['annual_opex_usd'][c],annual_operating_balance_usd=revenue-costs['annual_opex_usd'][c],
                    operating_cost_covering_fare_usd=costs['annual_opex_usd'][c]/annual,
                    full_life_cost_covering_fare_usd=costs['whole_life_npv_usd'][c]/(annual*annuity),
                    discounted_revenue_usd=pv,unfinanced_revenue_less_whole_life_cost_npv_usd=pv-costs['whole_life_npv_usd'][c],
                    initial_capital_funding_requirement_usd=costs['installed_capital_usd'][c],
                    illustrative=True))
                if debt is not None:
                    principal=costs['installed_capital_usd'][c]*share
                    balance=principal*(1+rate)**grace
                    service=balance*rate/(1-(1+rate)**-(term-grace)) if rate else balance/(term-grace)
                    rows[-1].update(illustrative_financed_principal_usd=principal,
                        illustrative_equity_or_grant_requirement_usd=costs['installed_capital_usd'][c]-principal,
                        illustrative_balance_after_capitalised_grace_usd=balance,
                        illustrative_annual_debt_service_after_grace_usd=service,
                        illustrative_post_grace_DSCR=(revenue-costs['annual_opex_usd'][c])/service if service else None)
    return dict(enabled=True,illustrative=True,not_a_demand_forecast=True,assumed_trips=trips,scenario_rows=rows,
        assumption_version=p['version'],assumptions=deepcopy(p),annual_discount_factor=annuity,
        accounting_horizon_years=years,real_discount_rate=discount,
        formula='Annual boardings = sum(line peak flow × (1+reverse flow fraction) × service hours × profile weighted fraction × mean/peak section load ÷ average trip/line length × operating days × demand multiplier). Paid linked trips = boardings ÷ boardings per linked trip × collection fraction.',
        financing=dict(debt_modelled=debt is not None,assumptions=deepcopy(debt),
            grace_period_debt_service_usd=0 if debt is not None else None,
            DSCR_basis='Illustrative post-grace receipts less canonical annual OPEX divided by level debt service; no DSCR during zero-payment grace. No lender threshold implied.',
            basis='Separate illustrative funding overlay, independent of the unfinanced revenue/cost NPV. No financing charges added to canonical cost; financed share does not establish origin.'))


def build(packet, detail, city_context=None, policy=None):
    """Return a deterministic dossier, preserving the exact current source epoch."""
    p=deepcopy(DEFAULT_POLICY if policy is None else policy)
    if p.get('schema')!=DEFAULT_POLICY['schema']:raise ValueError('Versioned dossier policy required')
    for key in ('cost_source','cost_source_sha256','city_cost_source','city_cost_source_sha256',
            'controllers_per_shift','station_staff_per_station_per_shift','operations_reliever_multiplier'):
        if p['staffing'][key]!=DEFAULT_POLICY['staffing'][key]:
            raise ValueError('Costed staffing literal assumptions cannot be revised in the dossier')
    _number(p['staffing']['fte_paid_hours_per_year'],'paid hours per FTE')
    if p['delivery']!=DEFAULT_POLICY['delivery']:
        raise ValueError('Versioned literal delivery resource policy required')
    ids,seed=_validate(packet,detail,city_context)
    lines,stations=_line_records(packet,city_context);costs,costrows=_costs(packet)
    workforce,cells=_workforce(packet,p);network=_network(packet,lines)
    energy={}
    for key in ('mechanical_traction_kwh_per_day','auxiliary_load_kwh_per_day','auxiliary_grid_kwh_per_day'):
        energy[key]=fsum(l['metrics'][key] for l in packet['lines'])
        energy[key.replace('_per_day','_per_year')]=fsum(l['metrics'][key]*l['requirements']['operating_days_per_year'] for l in packet['lines'])
    energy.update(physical_total_grid_kwh_per_day=None,physical_total_grid_kwh_per_year=None,
        electrical_traction_kwh_per_day=None,priced_annual_energy_usd=deepcopy(costs['annual_opex_by_scope_usd']['energy']),
        basis='Mechanical traction and nominal active-fleet auxiliaries are distinct. Priced lifecycle electricity scenarios include assumed efficiencies and site loads; they do not establish a physical grid total.')
    energy['priced_supply_scenarios']=deepcopy(packet['costs'].get('energy_ledger',{}))
    local=deepcopy(packet['costs'].get('local_cost_inputs',packet['assumptions'].get('cost',{}).get('local_cost_inputs',{})))
    costs['local_cost_inputs']=local
    costs['civil_comparison']=deepcopy(detail.get('civil_comparison'))
    costs['estimate_review']=dict(estimate_class='C',local_prices_verified=False,
        surveyed_demand_available=packet['evidence'].get('surveyed_demand_available',False),
        accounting_horizon_years=packet['resources'].get('accounting_years'),
        real_discount_rate=packet['resources'].get('real_discount_rate'),
        country=packet['city'].get('country'),pricing_basis=packet['costs'].get('pricing_basis'),
        largest_capital_accounts=[dict(key=r['key'],scope=r['scope'],base_usd=r['costs_usd']['base'],
            capital_share=r['costs_usd']['base']/costs['installed_capital_usd']['base'],basis=r.get('basis','Not supplied in this record'))
            for r in sorted(packet['costs']['capital_lines'],key=lambda r:-r['costs_usd']['base'])[:5]],
        civil_classification_basis='Retained mapped planning classes; water evidence alternatives are separate hypotheses, not surveyed structural designs')
    energy_rows=[dict(case=c,**r,physical_grid_demand_verified=False) for c,r in energy['priced_supply_scenarios'].get('cases',{}).items()]
    local_rows=[dict(input=k,unit='USD/kWh' if k=='electricity_usd_per_kwh' else 'USD/paid-person-hour',
        low=v[0],base=v[1],high=v[2],status=local['status'],country=packet['city'].get('country'),local_rates_verified=False)
        for k,v in local.get('values',{}).items()]
    draft=detail.get('delivery_draft',{});capital=packet['costs']['capital_lines']
    factory=next((r['quantity'] for r in capital if r['key']=='citywide-production-equipment-tools-buildings-yards'),{})
    make_buy=[dict(item=r['item'],selected_route=r.get('selected_route'),comparison_id=r.get('comparison_id'),
        cell_count=None,required_cell_hours=None,productive_person_hours=None,
        basis='Current delivery route; detailed comparison cells/hours are not in atlas, origin unspecified.') for r in draft.get('manufacturing_routes',[])]+cells
    reqs=[dict(requirement_id=k,status='open',requirement=v,automatically_satisfied=False) for k,v in [
        ('survey','Authenticated alignment, topography, clearances, demand and origin/destination survey'),
        ('land','Route/depot/station ownership, acquisition and permits'),('utilities','Surveyed utilities, diversions and verified power/grid capacity'),
        ('flood','Flood, drainage, water crossings and scour assessment'),('geotechnics','Ground investigation and foundation design'),
        ('access','Surveyed accessible paths, platforms, evacuation and passenger protection'),
        ('propulsion','Candidate-specific force, charge, thermal, protection and rescue evidence'),
        ('braking','Independent service/emergency braking, adhesion and degraded recovery qualification'),
        ('manufacturing','Installed BOM/mass, drawings, qualified processes, supplier quotes and independent review'),
        ('operations','Conflict-free timetable, staffing roster, maintenance, emergency and acceptance evidence')]]
    access=dict(illustrative=True,enabled=p['access']['enabled'],population_coverage=None,walk_network_verified=False,scenarios=[])
    if access['enabled']:
        for radius in p['access']['illustrative_radii_m']:
            _number(radius,'access radius');speed=_number(p['access']['walking_speed_m_s'],'walking speed')
            access['scenarios'].append(dict(radius_m=radius,straight_line_walk_minutes=radius/speed/60,
                station_circle_area_sum_km2=len(stations)*pi*(radius/1000)**2,
                overlaps_removed=False,population_coverage=None,
                basis='Sum of station-complex circles, overlapping areas included; geometry illustration only, not a union, accessible catchment or population served.'))
    finance=_finance(packet,lines,costs,p['finance'])
    source_ids=dict(atlas_packet_id=packet['packet_id'],completion_detail_id=identity(detail),planning_seed_id=seed['seed_id'],**deepcopy(ids))
    delivery=dict(resources=deepcopy(packet['resources']),factory_quantities=deepcopy(factory),civil_quantities=deepcopy(packet['civil']['quantities']),
        make_buy=make_buy,phase_order=deepcopy(draft.get('phase_order',[])),requirements=reqs,
        procurement_packages=deepcopy(draft.get('procurement_packages',[])),
        resource_envelope_only=True,executable_schedule=False,calendar_dates_assigned=False,
        business_records=dict(disabled=True,submitted=False,external_transactions_performed=False,named_workers_assigned=False))
    result=dict(schema=SCHEMA,city=deepcopy(packet['city']),source_ids=source_ids,sources=deepcopy(packet['sources']),
        context_content_id=identity(city_context) if city_context is not None else None,
        assumptions=dict(policy=p,policy_id=identity(p),staffing_binding='Exact source-cost SHA256 and literal assumptions; two-shift/civil estimates are resource hypotheses',
            no_historical_numeric_results_used=True),network=network,lines=lines,energy=energy,costs=costs,
        workforce=workforce,delivery=delivery,finance=finance,access=access,
        evidence=deepcopy(packet['evidence']),missing_evidence=deepcopy(packet['missing_evidence']),
        tables=dict(stations=stations,lines=deepcopy(lines),costs=costrows,workforce=deepcopy(workforce),finance=deepcopy(finance['scenario_rows']),
            delivery_requirements=deepcopy(reqs),make_buy=deepcopy(make_buy),
            energy_budget=energy_rows,local_cost_inputs=local_rows),**FLAGS)
    result['analysis_id']=identity(result)
    return result
