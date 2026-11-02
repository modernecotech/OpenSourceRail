"""Source-bound Class C replacement ledger for a civil research composition.

The vehicle and its conditional service demand are retained by exact identity.
Civil geometry, manufacture, delivery and lifecycle costs belong to a new
research composition. Neither the old beam screen nor physical acceptance is
transferred. Baselines are computed once, then validated before every trial.
"""
from copy import deepcopy
from math import ceil, fsum, isclose, isfinite
from pathlib import Path
import platform
import sys

from engineering.station_rail.common import digest, identity
from . import model_cost as model
from . import topology_geometry as geometry, topology_cost

PRODUCER = 'engineering/design_search/topology_system_cost.py'
CASES = model.CASES
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    manufacturing_release=False, operating_release=False,
    selected_reference_changed=False, installed_mass_complete=False,
    physical_journey_completed=False, service_qualified=False)
GUIDEWAY_KEYS = frozenset(('precast-beam-concrete-recipe', 'precast-reinforcement',
    'precast-prestress', 'precast-prestress-anchorage', 'precast-rails',
    'rail-fastener-sets', 'beam-fabrication-crew-machine-and-QA',
    'beam-factory-machine-QA-overhead'))
REPLACE_KEYS = frozenset(('precast-production-cells', 'precast-beam-mould-sets',
    'beam-heavy-haul-to-site', 'erection-rail-installation-and-temporary-works',
    'planned-maintenance-and-spares-lifecycle', 'bounded-asset-replacements',
    'end-of-life-decommissioning-proxy'))


def _seal(value, key='evaluation_id'):
    value[key] = identity({k: v for k, v in value.items() if k != key})
    return value


def _check(value, key='evaluation_id'):
    if not isinstance(value, dict) or value.get(key) != identity({k: v for k, v in value.items() if k != key}):
        raise ValueError('Invalid sealed record: ' + key)


def _number(value, *, positive=False):
    try:
        valid = type(value) in (int, float) and isfinite(value) and value >= 0 and (not positive or value > 0)
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError('Finite nonnegative quantity required')
    return float(value)


def _tools():
    import numpy
    import scipy
    return dict(python=platform.python_version(), implementation=platform.python_implementation(),
        executable_sha256=digest(Path(sys.executable).resolve()),
        numpy=numpy.__version__, scipy=scipy.__version__)


def _source_check(sources, root):
    if not isinstance(sources, dict) or not sources:
        raise ValueError('Nonempty source map required')
    root = Path(root).resolve()
    for name, sha in sources.items():
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file() or digest(path) != sha:
            raise ValueError('Stale or absent baseline source: ' + name)


def _sources(root):
    from engineering.development_baseline import system_cost
    value = {**system_cost.sources(root), **model.sources(root)}
    for name in (PRODUCER, geometry.PRODUCER, topology_cost.PRODUCER):
        value[name] = digest(Path(root) / name)
    for name, module_path in ((PRODUCER, __file__), (geometry.PRODUCER, geometry.__file__),
            (topology_cost.PRODUCER, topology_cost.__file__),
            (model.PRODUCER, model.__file__), (system_cost.PRODUCER, system_cost.__file__)):
        if value[name] != digest(Path(module_path)):
            raise ValueError('Executed producer differs from requested source root: ' + name)
    return value


def _lines(lines, candidate_id):
    if not isinstance(lines, list) or not lines:
        raise ValueError('Complete baseline cost ledger required')
    indexed = {}
    for row in lines:
        _check(row, 'line_id')
        key = row.get('line_key')
        if (not isinstance(key, str) or not key or key in indexed
                or row.get('candidate_id') != candidate_id or row.get('currency') != 'IQD'
                or row.get('scope') not in model.SCOPES or set(row.get('scenario_iqd', {})) != set(CASES)):
            raise ValueError('Duplicate, mixed or incomplete baseline line')
        for value in row['scenario_iqd'].values():
            _number(value)
        indexed[key] = row
    if {key for key, row in indexed.items() if row['scope'] == 'guideway'} != GUIDEWAY_KEYS:
        raise ValueError('Guideway replacement needs the exact corrected canonical keys')
    required = REPLACE_KEYS | {'foundation-footing-pier-proxy', 'retained-equipment/selected-service-battery-and-services'}
    if not required <= set(indexed):
        raise ValueError('Missing canonical replacement/dependency line')
    if {r['scope'] for r in lines} != set(model.SCOPES):
        raise ValueError('All fourteen cost scopes required')
    return indexed


def _load_context(context, selected, cases, root):
    from engineering.station_rail import civil
    _check(context, 'context_id')
    _source_check(context['source_sha256'], root)
    for field, target in [('vehicle_candidate_id', selected['candidate_id']),
            ('selection_id', selected['selection_id']), ('vehicle_evaluation_id', selected['vehicle_evaluation_id']),
            ('support_component_id', selected['support_component_id']),
            ('propulsion_component_id', selected['propulsion_component_id'])]:
        if context.get(field) != target:
            raise ValueError('Load context differs from canonical selected component: ' + field)
    if context.get('mass_cases_complete_installed') is not False or context.get('dynamic_factor_applied_once') != 1.3:
        raise ValueError('Explicit provisional mass and single dynamic factor required')
    rows = context.get('cases', [])
    if len(rows) != 9 or {(r['vehicle_mass_case'], r['name']) for r in rows} != {
            (m, c) for m in CASES for c in ('empty', 'normal', 'crowd_control')}:
        raise ValueError('Exactly nine train load cases required')
    offsets, _ = civil.axle_train(selected['vehicle'], 'normal')
    for row in rows:
        bundle = cases[row['vehicle_mass_case']]['bundle']
        mass = bundle['mass']['accounted_tare_kg_per_car']
        loaded = mass + {'empty': 0., 'normal': 3450., 'crowd_control': 12000.}[row['name']]
        if (not isclose(row['tare_kg_per_car'], mass, rel_tol=1e-12)
                or not isclose(row['loaded_kg_per_car'], loaded, rel_tol=1e-12)
                or not isclose(row['full_axle_force_N'], loaded*civil.G/4*1.3, rel_tol=1e-12)
                or row['offsets_m'] != offsets):
            raise ValueError('Load context mass, axle force or offsets differ')


def make_baseline(root, load_context):
    """Compute a fresh corrected canonical baseline, including all mass ledgers."""
    from engineering.development_baseline import evaluate, selection, system_cost, vehicle_cost
    root = Path(root).resolve()
    source_epoch = _sources(root)
    record = evaluate.build(root)
    vehicle = selection.load(root)['vehicle']
    vehicle_prices = vehicle_cost.evaluate(record, root)
    result, cases = system_cost.evaluate(record, root, vehicle_prices, return_case_records=True)
    selected = {key: result[key] for key in ('candidate_id', 'body_candidate_id',
        'support_component_id', 'propulsion_component_id', 'selection_id', 'vehicle_evaluation_id')}
    # The system-cost field historically names the whole development evaluation;
    # the civil context names the actual vehicle evaluation. Preserve both.
    selected['development_evaluation_id'] = result['vehicle_evaluation_id']
    selected['vehicle_evaluation_id'] = vehicle['evaluation_id']
    selected['vehicle'] = deepcopy(vehicle)
    _load_context(load_context, selected, cases, root)
    minimal = {}
    for name, case in cases.items():
        cost = case['cost']
        # The source evaluation identities retain the full upstream artifacts;
        # individual manufacturing occurrence routes are not a cached evaluator.
        cost_ledger = {k:deepcopy(v) for k,v in cost.items()
            if k not in {'provisional_manufacturing_plan','evaluation_id'}}
        cost_ledger.update(schema='osr-topology-canonical-cost-ledger/1',
            source_evaluation_id=cost['evaluation_id'])
        _seal(cost_ledger)
        minimal[name] = dict(bundle=deepcopy(case['bundle']),
            civil_design_basis=deepcopy(case['civil_design_basis']),
            architecture_evaluation_id=case['architecture']['evaluation_id'],
            motion_evaluation_id=case['motion']['evaluation_id'],
            cost=cost_ledger,
            renewal_line=deepcopy(case['renewal_line']), renewal_schedule=deepcopy(case['renewal_schedule']))
    sources = {**source_epoch, **record.get('source_sha256', {}),
        **vehicle_prices.get('source_sha256', {}), **result.get('source_sha256', {}),
        **load_context['source_sha256']}
    if source_epoch != _sources(root):
        raise ValueError('Source epoch changed during canonical baseline computation')
    value = dict(schema='osr-topology-system-baseline/1', selected=selected,
        selected_vehicle_candidate_id=selected['candidate_id'],
        canonical_system_cost_estimate_id=result['cost_estimate_id'],
        canonical_vehicle_cost_estimate_id=vehicle_prices['cost_estimate_id'],
        assumptions=model.assumptions(root), load_context=deepcopy(load_context),
        load_context_id=load_context['context_id'], cases=minimal,
        source_sha256=sources, tool_context=_tools(), **FLAGS)
    _seal(value, 'baseline_id')
    validate_baseline(value, root)
    return value


def validate_baseline(baseline, root, *, require_current_tools=True):
    """Validate the complete cache seal, current rates, sources, tools and rows."""
    _check(baseline, 'baseline_id')
    if baseline.get('schema') != 'osr-topology-system-baseline/1' or any(baseline.get(k) is not False for k in FLAGS):
        raise ValueError('Non-promoting canonical baseline required')
    _source_check(baseline['source_sha256'], root)
    if any(baseline['source_sha256'].get(k) != v for k, v in _sources(root).items()):
        raise ValueError('Baseline producer epoch differs')
    if type(require_current_tools) is not bool:
        raise ValueError('Explicit boolean tool-reuse policy required')
    if ((require_current_tools and baseline['tool_context'] != _tools())
            or baseline['assumptions'] != model.assumptions(root)):
        raise ValueError('Baseline numerical tools or rate assumptions differ')
    from engineering.development_baseline import selection
    current = selection.load(root)
    if (baseline['selected']['vehicle'] != current['vehicle']
            or baseline['selected']['selection_id'] != current['selection_id']
            or baseline['selected']['vehicle_evaluation_id'] != current['vehicle']['evaluation_id']
            or baseline.get('selected_vehicle_candidate_id') != current['vehicle']['candidate_id']):
        raise ValueError('Baseline selected physical definition differs')
    if set(baseline['cases']) != set(CASES) or baseline['load_context_id'] != baseline['load_context']['context_id']:
        raise ValueError('Complete matching mass and load context required')
    _load_context(baseline['load_context'], baseline['selected'], baseline['cases'], root)
    for name, case in baseline['cases'].items():
        cost = case['cost']; bundle = case['bundle']
        _check(cost)
        indexed = _lines(cost['cost_line_items'], bundle['candidate_id'])
        if (bundle['body_candidate_id'] != baseline['selected']['body_candidate_id']
                or cost['corridor_basis']['span_m'] != 20.
                or bundle['mass_sensitivity_case']['name'] != name):
            raise ValueError('Cross-candidate or incompatible baseline case')
        plan = model.renewal_plan(cost['cost_line_items'], baseline['assumptions'])
        if indexed['bounded-asset-replacements']['quantity'].get('renewal_plan_id') != plan['plan_id']:
            raise ValueError('Fresh disjoint canonical renewal plan required')
        fasteners = indexed['rail-fastener-sets']['quantity']
        if fasteners.get('counted_hardware_mass_kg', 0) <= 0 or fasteners.get('sets', 0) <= 0:
            raise ValueError('Complete-set price must retain positive hardware quantities')
    return baseline


def composition(candidate, baseline):
    """Physical composition excludes financial hypotheses and evaluation IDs."""
    geometry.validate(candidate)
    selected = baseline['selected']
    physical = dict(schema='osr-topology-railway-research-composition/1',
        vehicle_components={k: selected[k] for k in ('candidate_id', 'body_candidate_id',
            'support_component_id', 'propulsion_component_id')},
        civil_candidate_id=candidate['candidate_id'],
        route=deepcopy(baseline['cases']['base']['bundle']['architecture_case']['physical_definition']['route']),
        civil_interfaces=dict(span_m=20., deck_width_m=2., rail_interfaces_retained=True))
    return dict(physical_definition=physical, candidate_id=identity(physical))


def _support(support, candidate, quantity, baseline, masses, root):
    from engineering.station_rail import civil
    _check(support)
    _source_check(support['source_sha256'], root)
    expected = dict(candidate_id=candidate['candidate_id'], geometry_id=candidate['geometry_id'],
        quantity_evaluation_id=quantity['evaluation_id'], baseline_id=baseline['baseline_id'],
        selected_vehicle_candidate_id=baseline['selected']['candidate_id'], load_context_id=baseline['load_context_id'])
    if any(support.get(k) != v for k, v in expected.items()) or set(support.get('cases', {})) != set(CASES):
        raise ValueError('Support-demand ancestry or case coverage differs')
    for mass in CASES:
        loads = support['cases'][mass]['load_cases']
        if set(loads) != {'empty', 'normal', 'crowd_control'}:
            raise ValueError('Complete support load cases required')
        for load in loads.values():
            rows = load['financial_cases']
            if set(rows) != set(CASES):
                raise ValueError('Complete support financial cases required')
            for i, name in enumerate(CASES):
                row = rows[name]
                if (not isclose(_number(row['accounted_span_mass_kg'], positive=True), masses[i], rel_tol=1e-12)
                        or row.get('unknown_pier_selfweight') is not True
                        or set(row['minimum_gravity_bearing_area_m2_by_pressure_kpa']) != {'300', '200', '100'}):
                    raise ValueError('Support mass or site-unknown declaration differs')
                for k in ('per_span_gravity_N', 'interior_support_vertical_reaction_N'):
                    _number(row[k], positive=True)
                if not isclose(row['per_span_gravity_N'], masses[i]*civil.G, rel_tol=1e-10):
                    raise ValueError('Accounted gravity arithmetic differs')
                for pressure, area in row['minimum_gravity_bearing_area_m2_by_pressure_kpa'].items():
                    if not isclose(_number(area, positive=True), row['interior_support_vertical_reaction_N']/(1000*float(pressure)), rel_tol=1e-10):
                        raise ValueError('Support pressure/area arithmetic differs')
    if _support_replay(candidate, quantity, baseline, root) != support:
        raise ValueError('Support demands do not replay their source-bound live-reaction/context arithmetic')


def _support_replay(candidate, quantity, baseline, root):
    """Replay the exact declared gravity recipe; never accept a self-sealed load."""
    from . import civil_topology
    producer = civil_topology.PRODUCER
    path = Path(root)/producer
    if not path.is_file():
        raise ValueError('Current support-demand producer file required')
    actual = digest(path)
    if (baseline['source_sha256'].get(producer) != actual
            or digest(Path(civil_topology.__file__)) != actual):
        raise ValueError('Current executed support-demand producer digest required')
    return civil_topology.support_demands(candidate, quantity, baseline, civil_topology.specification(root))


def _wrap(row, candidate_id, baseline_id):
    value = deepcopy(row)
    value.update(candidate_id=candidate_id, origin_line_id=row['line_id'],
        origin_candidate_id=row['candidate_id'], baseline_id=baseline_id,
        reuse_reason='Exact unchanged vehicle/service or explicit unchanged Class C site-price scenario; no civil structural acceptance transferred')
    value.pop('line_id')
    return _seal(value, 'line_id')


def _add(lines, cid, key, scope, amounts, stage, source_ids, *, quantity, basis, group=None, components=None):
    model._line(lines, candidate_id=cid, scope=scope, key=key, quantity=quantity,
        unit='declared-corridor', totals=amounts, stage=stage, basis=basis,
        source_ids=source_ids, components=components)
    if group:
        lines[-1]['renewal_asset_group'] = group
        _seal(lines[-1], 'line_id')


def _totals(lines, *, require_complete=True):
    stages = [('factory_gate_cost_iqd', {'factory-gate'}),
        ('delivered_cost_iqd', {'factory-gate', 'delivered'}),
        ('model_based_installed_CAPEX_iqd', model.INITIAL_COST_STAGES),
        ('model_based_whole_life_NPV_iqd', model.INITIAL_COST_STAGES | {'lifecycle'})]
    value = {key: [round(fsum(r['scenario_iqd'][c] for r in lines if r['cost_stage'] in included), 2)
        for c in CASES] for key, included in stages}
    value['scope_totals_iqd'] = {scope: [round(fsum(r['scenario_iqd'][c] for r in lines if r['scope'] == scope), 2)
        for c in CASES] for scope in model.SCOPES}
    if require_complete and any(values[1] <= 0 for values in value['scope_totals_iqd'].values()):
        raise ValueError('All fourteen scopes require positive declared base estimates')
    return value


def compose(candidate, quantity, span_cost, baseline, support_demands, *, root, require_current_tools=True):
    """Replace complete civil scopes, then recalculate dependent lifecycle rows."""
    from engineering.development_baseline import system_cost
    validate_baseline(baseline, root, require_current_tools=require_current_tools)
    geometry.validate(candidate)
    _check(quantity); _check(span_cost)
    a_record = baseline['assumptions']; a = a_record['assumptions']
    if topology_cost.estimate(candidate, quantity, span_cost['topology_spec'], a_record) != span_cost:
        raise ValueError('Topology cost does not reproduce current geometry, quantities and rates')
    physical = composition(candidate, baseline); cid = physical['candidate_id']
    base_cost = baseline['cases']['base']['cost']; corridor = base_cost['corridor_basis']
    n = _number(corridor['span_count'], positive=True)
    indexed = _lines(base_cost['cost_line_items'], base_cost['candidate_id'])
    rail_mass = indexed['precast-rails']['quantity']['mass_kg']/n
    set_mass = indexed['rail-fastener-sets']['quantity']['counted_hardware_mass_kg']/n
    masses = [x+rail_mass+set_mass for x in quantity['accounted_mass_kg_cases']]
    _support(support_demands, candidate, quantity, baseline, masses, root)
    spec = span_cost['topology_spec']; rows = span_cost['cases']
    if [r['case'] for r in rows] != list(CASES):
        raise ValueError('Ordered financial cases required')
    hours = [n*r['total_factory_person_hours'] for r in rows]
    capacity_per_operator = (a_record['production_years']*a_record['production_days_per_year']*
        a_record['production_shifts_per_day']*a_record['production_hours_per_shift']*a_record['productive_utilisation'])
    crew_capacity = [capacity_per_operator*people for people in spec['production_crew_people']]
    cells = [max(1, ceil(h/crew_capacity[i])) for i,h in enumerate(hours)]
    # One tooling set per parallel cell; deck mould cycles remain a separately
    # declared, retained Class C hypothesis, not a prestressing plant.
    moulds = [max(1, ceil(n*a['beam_mould_cycle_days'][i]/(a_record['production_years']*a_record['production_days_per_year']))) for i in range(3)]
    outputs = {}
    for mass_name, case in baseline['cases'].items():
        cost = case['cost']; old = _lines(cost['cost_line_items'], cost['candidate_id'])
        if cost['corridor_basis'] != corridor:
            raise ValueError('Mass-case route/service/fleet basis differs')
        lines = [_wrap(r, cid, baseline['baseline_id']) for r in cost['cost_line_items']
            if r['line_key'] not in REPLACE_KEYS and (r['scope'] != 'guideway' or r['line_key'] in {'precast-rails', 'rail-fastener-sets'})]
        foundation = next(r for r in lines if r['line_key'] == 'foundation-footing-pier-proxy')
        foundation['quantity'].update(gravity_support_evaluation_id=support_demands['evaluation_id'],
            gravity_support_cases=deepcopy(support_demands['cases'][mass_name]),
            price_proxy_mass_coupled=False, site_capacity_verified=False, pier_selfweight_unknown=True)
        _seal(foundation, 'line_id')
        ancestors = [baseline['baseline_id'], span_cost['evaluation_id'], quantity['evaluation_id'], support_demands['evaluation_id']]
        _add(lines, cid, 'topology-span-factory-gate', 'guideway', [n*r['factory_gate_iqd'] for r in rows], 'factory-gate', ancestors,
            quantity=dict(spans=n, per_span_factory_cases=[dict(case=r['case'],
                factory_line_items_iqd=r['factory_line_items_iqd'], factory_overhead_iqd=r['factory_overhead_iqd'],
                factory_gate_iqd=r['factory_gate_iqd'], total_factory_person_hours=r['total_factory_person_hours']) for r in rows]),
            basis='Actual topology blank, reserve, process, QA, coating and one overhead; rails and complete sets retained separately; no plant amortisation', group='guideway')
        _add(lines, cid, 'topology-steel-production-cells', 'factory-tooling', [cells[i]*r['dedicated_plant_capital_iqd'] for i, r in enumerate(rows)], 'capital', ancestors,
            quantity=dict(factory_cells=cells, required_person_hours=hours,
                productive_person_hours_per_cell=crew_capacity, declared_operators_per_cell=spec['production_crew_people'],
                productive_hours_per_operator=capacity_per_operator,
                machine_cycle_and_precedence_throughput_resolved=False),
            basis='Equipped steel crew-cells: total person-hours divided by declared operators per cell times two-shift productive operator capacity; machine/precedence throughput unresolved; no repeated per-piece capital')
        steel_tooling = [cells[i]*r['tooling_capital_iqd'] for i, r in enumerate(rows)]
        deck_moulds = [moulds[i]*a['beam_mould_iqd_each'][i] for i in range(3)]
        _add(lines, cid, 'topology-steel-tooling-and-deck-moulds', 'factory-tooling', [steel_tooling[i]+deck_moulds[i] for i in range(3)], 'capital', ancestors,
            quantity=dict(steel_tool_sets=cells, deck_mould_sets=moulds, deck_mould_cycle_days=a['beam_mould_cycle_days']),
            basis='One steel tooling set per workcell plus separate deck mould capacity; unchanged Class C deck mould rate/cycle, no prestressing plant', components=dict(steel_tooling=steel_tooling, deck_moulds=deck_moulds))
        haul = [n*masses[i]/1000*spec['transport_distance_km']*spec['transport_iqd_per_tonne_km'][i] for i in range(3)]
        _add(lines, cid, 'topology-accounted-module-and-rail-haul', 'construction', haul, 'delivered', ancestors,
            quantity=dict(span_count=n, accounted_span_mass_kg=masses, rail_mass_kg_per_span=rail_mass, fastener_mass_kg_per_span=set_mass,
                haul_km=spec['transport_distance_km']), basis='Accounted geometry plus bounded hardware reserves, rails and sets once; complete installed mass and route permits unknown')
        labour = [n*r['installation_labour_iqd'] for r in rows]
        pieces = max(quantity['handling']['actual_cut_pieces'], quantity['handling']['plate_handling_modules'])+1
        cranes = [n*pieces*r['installation_crane_iqd'] for r in rows]
        rail_install = old['erection-rail-installation-and-temporary-works']['components_iqd']['rail_installation']
        direct = [labour[i]+cranes[i]+rail_install[i] for i in range(3)]
        contingency = [direct[i]*a['construction_contingency_fraction'][i] for i in range(3)]
        _add(lines, cid, 'topology-module-erection-rail-and-temporary-works', 'construction', [direct[i]+contingency[i] for i in range(3)], 'installed', ancestors,
            quantity=dict(spans=n, crane_lifts_per_span=pieces, person_hours=[n*r['installation_person_hours'] for r in rows], rail_installation_reused_once=True),
            basis='Provisional module and deck lifts, topology erection labour, retained rail installation and one contingency; rigging/assembly acceptance open',
            components=dict(crane=cranes, labour=labour, rail_installation=rail_install, contingency=contingency))
        years = a_record['design_life_years']; rate = a_record['real_discount_rate']
        annuity = fsum((1+rate)**(-y) for y in range(1, years+1))
        maintainable = [fsum(r['scenario_iqd'][c] for r in lines if r['scope'] in {'rolling-stock', 'guideway', 'stations-power'} and r['cost_stage'] in model.INITIAL_COST_STAGES) for c in CASES]
        annual = [maintainable[i]*a['maintenance_fraction_per_year'][i]*a_record['operating_hours_per_day_cases'][i]/a_record['maintenance_reference_operating_hours_per_day'] for i in range(3)]
        _add(lines, cid, 'planned-maintenance-and-spares-lifecycle', 'maintenance', [x*annuity for x in annual], 'lifecycle', ancestors,
            quantity=dict(maintainable_scope_iqd=maintainable, annual_cost_iqd=annual), basis='Canonical maintenance fraction/duty on replaced disjoint initial assets; scoped topology maintenance not added')
        plan = model.renewal_plan(lines, a_record)
        _add(lines, cid, 'bounded-asset-replacements', 'renewals', plan['renewal_NPV_iqd'], 'lifecycle', ancestors+[plan['plan_id']],
            quantity=dict(renewal_plan_id=plan['plan_id'], renewal_plan=plan), basis='Shared disjoint asset-group renewal plan, each initial component once')
        extra = []; extra_npv = []
        group = next(g for g in plan['asset_groups'] if g['asset_group'] == 'guideway')
        for i, name in enumerate(CASES):
            whole = [e['year'] for e in group['cases'][i]['events']]
            events = []
            resets = []
            assets = [('coating', spec['coating_renewal_years'][i],
                rows[i]['scoped_installed_iqd']*spec['coating_renewal_fraction'][i]),
                ('bearings', spec['bearing_renewal_years'][i],
                 rows[i]['reserve_cost_iqd']['bearings']+rows[i]['installation_labour_iqd']*.25)]
            for asset, life, basis in assets:
                timing = system_cost.component_renewal_schedule(years, life, whole)
                resets.append(dict(asset=asset, schedule_id=timing['evaluation_id'],
                    component_life_years=life, parent_replacement_years=whole,
                    coincidence_tolerance_years=timing['coincidence_tolerance_years'], age_resets=timing['age_resets']))
                for event in timing['events']:
                    covered = event['covered_by_parent_replacement']
                    pv = 0. if covered else basis/(1+rate)**event['year']
                    events.append(dict(**event, asset=asset, undiscounted_iqd=basis,
                        present_value_iqd=pv, spans=n, covered_by_complete_guideway_replacement=covered,
                        corridor_present_value_iqd=n*pv))
            events.sort(key=lambda event:(event['year'],event['asset']))
            extra.append(dict(case=name, events=events, component_age_reset_schedules=resets))
            extra_npv.append(fsum(e['corridor_present_value_iqd'] for e in events))
        _add(lines, cid, 'topology-coating-and-bearing-renewals', 'renewals', extra_npv, 'lifecycle', ancestors,
            quantity=dict(event_schedule=extra), basis='Whole-guideway replacement supplies new coating/bearings and resets component ages; coincident expiry rows have zero incremental cost; scoped lifecycle total/maintenance/disposal never added')
        pack, pack_schedule = system_cost._account_renewal(cid, dict(cost_line_items=lines), a_record)
        lines.append(pack)
        installed = _totals(lines, require_complete=False)['model_based_installed_CAPEX_iqd']
        disposal = [installed[i]*a['decommissioning_fraction_of_installed_CAPEX'][i]/(1+rate)**years for i in range(3)]
        _add(lines, cid, 'end-of-life-decommissioning-proxy', 'disposal', disposal, 'lifecycle', ancestors,
            quantity=dict(base_installed_CAPEX_iqd=installed, year=years), basis='Canonical year30 removal fraction of new total CAPEX; no duplicate scoped disposal')
        production = deepcopy(cost['production_plan'])
        erection_hours = [n*r['installation_person_hours'] for r in rows]
        crew_days = [ceil(erection_hours[i]/(spec['civil_crew_people'][i]*2*8*a_record['productive_utilisation'])) for i in range(3)]
        crane_shifts = [ceil(n*pieces/a['spans_per_crane_shift'][i]) for i in range(3)]
        erection_days = [max(crew_days[i], ceil(crane_shifts[i]/2)) for i in range(3)]
        schedule = production['construction_schedule_days']
        schedule.update(span_erection=erection_days, span_erection_work_shifts=crane_shifts,
            topology_erection_person_hours=erection_hours, precedence_and_resource_conflicts_resolved=False)
        critical = [max(schedule[k][i] for k in ('foundations', 'span_erection', 'rail_installation', 'stations')) for i in range(3)]
        schedule['critical_path_duration'] = critical
        production.update(guideway_factory_hours=hours, required_guideway_workcells=cells,
            guideway_workcell_basis=dict(declared_operators_per_cell=spec['production_crew_people'],
                productive_person_hours_per_cell=crew_capacity, productive_hours_per_operator=capacity_per_operator,
                kind='equipped-crew-cell', baseline_vehicle_and_station_cells_are_one_person_equivalents=True,
                machine_cycle_and_precedence_throughput_resolved=False),
            guideway_mould_sets=moulds, construction_duration_days=critical,
            required_parallel_workcells=[production['required_vehicle_workcells'][i]+cells[i]+production['required_station_power_workcells'][i] for i in range(3)],
            factory_gate_vehicle_and_guideway_IQD=[round(fsum(r['scenario_iqd'][c] for r in lines if r['scope'] in {'rolling-stock', 'guideway'} and r['cost_stage']=='factory-gate'), 2) for c in CASES])
        output = dict(candidate_id=cid, vehicle_mass_case=mass_name, cost_line_items=lines,
            **_totals(lines), production_plan=production, corridor_basis=deepcopy(corridor),
            annual_maintenance_iqd=[round(x, 2) for x in annual], renewal_plan=plan,
            service_pack_renewal_schedule=pack_schedule, topology_renewal_schedule=extra,
            retained_conditional_model_ids=dict(bundle_definition_id=case['bundle']['definition_id'],
                architecture_evaluation_id=case['architecture_evaluation_id'], motion_evaluation_id=case['motion_evaluation_id']),
            support_demand_evaluation_id=support_demands['evaluation_id'], **FLAGS)
        output['lifecycle'] = deepcopy(cost.get('lifecycle', {}))
        output['lifecycle'].update(years=years, real_discount_rate=rate,
            maintenance_NPV_iqd=[round(x*annuity,2) for x in annual],
            renewal_NPV_iqd=[round(fsum(r['scenario_iqd'][c] for r in lines if r['scope']=='renewals'),2) for c in CASES],
            disposal_NPV_iqd=[round(x,2) for x in disposal], initial_installed_CAPEX_iqd=installed)
        for key in ('annual_energy_iqd', 'annual_operations_iqd', 'annual_reliability_iqd', 'annual_electricity_kwh'):
            if key in cost:
                output[key] = deepcopy(cost[key])
        output['retained_vehicle_service_inputs'] = {k:deepcopy(case['bundle'][k]) for k in (
            'reference_candidate_id', 'body_candidate_id', 'support_component_id', 'propulsion_component_id',
            'requirements', 'mass', 'mass_sensitivity_case', 'rotating_equivalent_kg_per_car',
            'brake_definition', 'motor_definition', 'physical_definition', 'architecture_case') if k in case['bundle']}
        output['unchanged_model_reuse_reason'] = ('Only the civil research composition changes. Exact vehicle components, '
            'conditional force/braking/charging demand inputs, route/service/platform/propulsion/fleet scope remain fixed. '
            'Neither available-force feasibility nor the original concrete beam validation is reused.')
        _seal(output); outputs[mass_name] = output
    value = dict(schema='osr-topology-system-cost/1', **physical, baseline_id=baseline['baseline_id'],
        replay_context=dict(current_tools_required=require_current_tools, baseline_tools=baseline['tool_context'],
            ledger_replay_tools=_tools(), baseline_tool_reuse_check_enforced=require_current_tools,
            native_evaluator_admission=False),
        geometry_id=candidate['geometry_id'], quantity_evaluation_id=quantity['evaluation_id'],
        span_cost_evaluation_id=span_cost['evaluation_id'], support_demands_evaluation_id=support_demands['evaluation_id'],
        load_context_id=baseline['load_context_id'], selected_vehicle_components=deepcopy(physical['physical_definition']['vehicle_components']),
        cases=outputs, estimate_class='C', currency='IQD', model_cost_complete_for_declared_scope=True,
        source_sha256={**baseline['source_sha256'], **span_cost['source_sha256'], **support_demands['source_sha256']},
        holds=['Unresolved installed mass/CG, vehicle joints, LIM force/current/thermal maps, braking, charging acceptance and service energy remain open',
            'No old box-beam structural screen transferred; topology material, buckling, fatigue, splices, lifting and load transfer unqualified',
            'Foundation price proxies unchanged; new gravity demands do not establish site capacity or include unknown pier selfweight',
            'Same normal capacity, dwell/headway, full-tail clearance, grade, charging/reserve, platforms, powered zones, grid, fleet and recovery assumptions retained; affordability and service unqualified',
            'Schedules are two-shift capacity bounds without resolved precedence, procurement, cranes or crew conflicts'], **FLAGS)
    topology_cost._finite_cost(value)
    _seal(value)
    return value


def compare(candidate, quantity, span_cost, baseline, support_demands, *, root, require_current_tools=True):
    result = compose(candidate, quantity, span_cost, baseline, support_demands, root=root,
        require_current_tools=require_current_tools)
    deltas = {}
    for mass, row in result['cases'].items():
        old = baseline['cases'][mass]
        old_whole = [old['cost']['model_based_whole_life_NPV_iqd'][i]+old['renewal_line']['scenario_iqd'][c] for i, c in enumerate(CASES)]
        deltas[mass] = dict(installed_CAPEX_delta_iqd=[round(row['model_based_installed_CAPEX_iqd'][i]-old['cost']['model_based_installed_CAPEX_iqd'][i], 2) for i in range(3)],
            whole_life_NPV_delta_iqd=[round(row['model_based_whole_life_NPV_iqd'][i]-old_whole[i], 2) for i in range(3)])
    result['comparison_to_corrected_canonical_baseline'] = deltas
    return _seal(result)
