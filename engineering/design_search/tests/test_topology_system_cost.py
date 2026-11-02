"""Independent replacement-ledger arithmetic; no native solver or publication."""
from copy import deepcopy
from math import ceil, fsum
from pathlib import Path

import pytest

from engineering.design_search import topology_system_cost as t
from engineering.design_search import topology_geometry as g, topology_cost as c
from engineering.development_baseline import system_cost

ROOT = Path(t.__file__).resolve().parents[2]
CID = 'a'*64


def line(key, scope, value=100., *, stage='factory-gate', quantity=None, components=None):
    rows = []
    t.model._line(rows, candidate_id=CID, scope=scope, key=key,
        quantity=quantity or {}, unit='independent-fixture', totals=[value]*3,
        stage=stage, basis='Independent bounded ledger fixture', source_ids=['b'*64], components=components)
    return rows[0]


def baseline():
    a = t.model.assumptions(ROOT)
    lines = [line(key, 'guideway', quantity=(dict(mass_kg=2408.4*600) if key=='precast-rails'
        else dict(sets=42000, counted_hardware_mass_kg=560.*600) if key=='rail-fastener-sets' else {}))
        for key in sorted(t.GUIDEWAY_KEYS)]
    lines += [line('retained-equipment/selected-service-battery-and-services', 'rolling-stock'),
        line('station-lim-primary-stock', 'stations-power'),
        line('precast-production-cells', 'factory-tooling', stage='capital'),
        line('precast-beam-mould-sets', 'factory-tooling', stage='capital'),
        line('foundation-footing-pier-proxy', 'construction', stage='installed'),
        line('beam-heavy-haul-to-site', 'construction', stage='delivered'),
        line('erection-rail-installation-and-temporary-works', 'construction', 400., stage='installed',
            components=dict(crane=[100.]*3, labour=[100.]*3, rail_installation=[100.]*3, contingency=[100.]*3))]
    present = {r['scope'] for r in lines}
    for scope in t.model.SCOPES:
        if scope not in present and scope not in {'maintenance', 'renewals', 'disposal'}:
            lines.append(line('unchanged-'+scope, scope, stage='capital' if scope in {'land-utilities-depot', 'fleet'} else 'lifecycle'))
    for scope, key in [('maintenance', 'planned-maintenance-and-spares-lifecycle'),
            ('renewals', 'bounded-asset-replacements'), ('disposal', 'end-of-life-decommissioning-proxy')]:
        lines.append(line(key, scope, stage='lifecycle'))
    plan = t.model.renewal_plan(lines, a)
    renewal = next(r for r in lines if r['line_key']=='bounded-asset-replacements')
    renewal['quantity'] = dict(renewal_plan_id=plan['plan_id'], renewal_plan=plan)
    t._seal(renewal, 'line_id')
    corridor = dict(span_m=20., span_count=600, directional_route_m=6000., trackways=2,
        stations=3, support_count=602, cars_per_train=6, normal_trainsets=6,
        spare_trainsets=2, fleet_trainsets=8, fleet_cars=48, target_headway_s=120., offered_capacity_pphpd=8280.)
    production = dict(required_vehicle_workcells=[2]*3, required_station_power_workcells=[3]*3,
        production_shifts_per_day=2, production_hours_per_shift=8,
        civil_shifts_per_day=2, civil_hours_per_shift=8,
        operations_shifts_per_day_cases=[2,2,3],
        construction_schedule_days=dict(foundations=[1]*3, rail_installation=[2]*3, stations=[3]*3))
    cases = {}
    for mass in t.CASES:
        cost = dict(candidate_id=CID, cost_line_items=deepcopy(lines), corridor_basis=corridor,
            production_plan=production, **t._totals(lines))
        t._seal(cost)
        pack, schedule = system_cost._account_renewal(CID, cost, a)
        cases[mass] = dict(cost=cost, renewal_line=pack, renewal_schedule=schedule,
            bundle=dict(candidate_id=CID, body_candidate_id='d'*64, definition_id='e'*64,
                mass=dict(accounted_tare_kg_per_car=20000.), mass_sensitivity_case=dict(name=mass),
                architecture_case=dict(physical_definition=dict(route=dict(directional_ring_length_m=6000., stations=3, station_spacing_m=2000.)))),
            architecture_evaluation_id='f'*64, motion_evaluation_id='1'*64)
    result = dict(schema='osr-topology-system-baseline/1', selected=dict(candidate_id='2'*64,
        body_candidate_id='d'*64, support_component_id='3'*64, propulsion_component_id='4'*64),
        assumptions=a, load_context_id='5'*64, cases=cases, source_sha256={}, tool_context=t._tools(), **t.FLAGS)
    return t._seal(result, 'baseline_id')


@pytest.fixture
def inputs(monkeypatch):
    # Compose arithmetic is exercised against an explicit small ledger. Source,
    # seal, load and current-context validators have separate rejection probes.
    b = baseline(); candidate = g.realize([[1,1,1],[1,0,1],[1,1,1]])
    q = g.quantities(candidate); cost = c.estimate(candidate, q, c.default_spec(), b['assumptions'])
    masses = [x+2408.4+560. for x in q['accounted_mass_kg_cases']]
    support = dict(candidate_id=candidate['candidate_id'], geometry_id=candidate['geometry_id'],
        quantity_evaluation_id=q['evaluation_id'], baseline_id=b['baseline_id'],
        selected_vehicle_candidate_id=b['selected']['candidate_id'], load_context_id=b['load_context_id'],
        source_sha256={'fixture': 'fixture'}, cases={})
    for mass in t.CASES:
        support['cases'][mass] = dict(load_cases={})
        for load in ('empty','normal','crowd_control'):
            support['cases'][mass]['load_cases'][load] = dict(financial_cases={name: dict(
                accounted_span_mass_kg=masses[i], per_span_gravity_N=masses[i]*9.80665,
                interior_support_vertical_reaction_N=1000000.,
                minimum_gravity_bearing_area_m2_by_pressure_kpa={str(p):1000000./(1000*p) for p in (300,200,100)},
                unknown_pier_selfweight=True) for i, name in enumerate(t.CASES)})
    t._seal(support)
    reference=deepcopy(support)
    def replay(candidate,quantity,baseline,root):
        result=deepcopy(reference)
        result['baseline_id']=baseline['baseline_id']
        return t._seal(result)
    monkeypatch.setattr(t, 'validate_baseline', lambda value, root, **kwargs: value)
    monkeypatch.setattr(t, '_source_check', lambda sources, root: None)
    monkeypatch.setattr(t, '_support_replay', replay)
    return candidate, q, cost, b, support


def test_replacement_covers_all_scopes_and_retains_rail_sets_once(inputs):
    candidate, q, cost, b, support = inputs
    before = deepcopy(inputs)
    result = t.compare(*inputs, root=ROOT)
    assert inputs == before
    assert result['candidate_id'] != CID and result['candidate_id'] != candidate['candidate_id']
    for mass, output in result['cases'].items():
        lines = output['cost_line_items']; keys = [r['line_key'] for r in lines]
        assert len(keys) == len(set(keys))
        assert set(output['scope_totals_iqd']) == set(t.model.SCOPES)
        assert set(t.GUIDEWAY_KEYS)&set(keys) == {'precast-rails','rail-fastener-sets'}
        assert all(r['candidate_id']==result['candidate_id'] for r in lines)
        rail = next(r for r in lines if r['line_key']=='precast-rails')
        sets = next(r for r in lines if r['line_key']=='rail-fastener-sets')
        assert rail['scenario_iqd'] == sets['scenario_iqd'] == dict.fromkeys(t.CASES,100.)
        assert rail['origin_line_id'] != rail['line_id']
        assert sets['quantity']['counted_hardware_mass_kg'] == 336000.
        assert sets['quantity']['sets'] == 42000
        pack = next(r for r in lines if r['line_key']=='selected-service-battery-and-services-renewal')
        source = next(r for r in lines if r['line_key']=='retained-equipment/selected-service-battery-and-services')
        assert pack['quantity']['source_account_line_id'] == source['line_id']
        assert pack['quantity']['source_account_line_id'] != source['origin_line_id']
        for i, case in enumerate(t.CASES):
            installed = fsum(r['scenario_iqd'][case] for r in lines if r['cost_stage'] in t.model.INITIAL_COST_STAGES)
            whole = fsum(r['scenario_iqd'][case] for r in lines)
            assert output['model_based_installed_CAPEX_iqd'][i] == round(installed,2)
            assert output['model_based_whole_life_NPV_iqd'][i] == round(whole,2)
        assert all(output[k] is False and result[k] is False for k in t.FLAGS)


def test_independent_factory_haul_erection_and_capacity_arithmetic(inputs):
    candidate, q, cost, b, support = inputs
    output = t.compose(*inputs, root=ROOT)['cases']['base']
    lines = {r['line_key']:r for r in output['cost_line_items']}
    a = b['assumptions']; n=600
    for i, case in enumerate(t.CASES):
        row = cost['cases'][i]
        assert lines['topology-span-factory-gate']['scenario_iqd'][case] == round(n*row['factory_gate_iqd'],2)
        expected_haul = n*(q['accounted_mass_kg_cases'][i]+2408.4+560.)/1000*50*cost['topology_spec']['transport_iqd_per_tonne_km'][i]
        assert lines['topology-accounted-module-and-rail-haul']['scenario_iqd'][case] == round(expected_haul,2)
        crew=cost['topology_spec']['production_crew_people'][i]
        capacity=3*250*2*8*.75*crew
        cells=ceil(n*row['total_factory_person_hours']/capacity)
        assert lines['topology-steel-production-cells']['scenario_iqd'][case] == cells*row['dedicated_plant_capital_iqd']
        assert output['production_plan']['required_guideway_workcells'][i] == cells
        assert cells*capacity >= n*row['total_factory_person_hours']
        assert (cells-1)*capacity < n*row['total_factory_person_hours']
        tooling=lines['topology-steel-tooling-and-deck-moulds']
        moulds=ceil(n*a['assumptions']['beam_mould_cycle_days'][i]/(3*250))
        expected_tooling=cells*row['tooling_capital_iqd']+moulds*a['assumptions']['beam_mould_iqd_each'][i]
        assert tooling['scenario_iqd'][case]==expected_tooling
        assert output['production_plan']['guideway_workcell_basis']['productive_person_hours_per_cell'][i]==capacity
        assert output['production_plan']['guideway_workcell_basis']['kind']=='equipped-crew-cell'
        assert output['production_plan']['guideway_workcell_basis']['machine_cycle_and_precedence_throughput_resolved'] is False
        erection = lines['topology-module-erection-rail-and-temporary-works']
        comp = erection['components_iqd']
        direct = comp['crane'][i]+comp['labour'][i]+comp['rail_installation'][i]
        assert comp['rail_installation'][i] == 100.
        assert erection['scenario_iqd'][case] == round(direct*(1+a['assumptions']['construction_contingency_fraction'][i]),2)
        assert output['production_plan']['construction_duration_days'][i] >= 3
    assert output['production_plan']['operations_shifts_per_day_cases']==[2,2,3]
    assert output['production_plan']['civil_shifts_per_day']==2


def test_maintenance_disposal_and_component_renewal_are_recomputed_once(inputs):
    result = t.compose(*inputs, root=ROOT)
    a = inputs[3]['assumptions']; output = result['cases']['base']
    lines = output['cost_line_items']; bykey = {r['line_key']:r for r in lines}
    for i, case in enumerate(t.CASES):
        maintained = fsum(r['scenario_iqd'][case] for r in lines if r['scope'] in {'rolling-stock','guideway','stations-power'} and r['cost_stage'] in t.model.INITIAL_COST_STAGES)
        annual=maintained*a['assumptions']['maintenance_fraction_per_year'][i]*a['operating_hours_per_day_cases'][i]/18
        assert output['annual_maintenance_iqd'][i] == round(annual,2)
        assert bykey['planned-maintenance-and-spares-lifecycle']['scenario_iqd'][case] == round(fsum(annual/1.04**year for year in range(1,31)),2)
        capex = output['model_based_installed_CAPEX_iqd'][i]
        assert bykey['end-of-life-decommissioning-proxy']['scenario_iqd'][case] == pytest.approx(round(capex*a['assumptions']['decommissioning_fraction_of_installed_CAPEX'][i]/1.04**30,2), abs=.01)
        events = output['topology_renewal_schedule'][i]['events']
        assert len(events)==len(inputs[2]['cases'][i]['lifecycle']['renewals'])
        assert bykey['topology-coating-and-bearing-renewals']['scenario_iqd'][case] == round(fsum(e['corridor_present_value_iqd'] for e in events),2)
    assert output['renewal_plan']['conservation']['every_source_component_allocated_once']
    foundation = bykey['foundation-footing-pier-proxy']
    assert foundation['scenario_iqd'] == dict.fromkeys(t.CASES,100.)
    assert foundation['quantity']['price_proxy_mass_coupled'] is False


@pytest.mark.parametrize('change', ['duplicate','unknown-guideway','missing-guideway','foreign-candidate','raw-fastener'])
def test_strict_baseline_line_contract_rejects_partial_or_old_ledgers(change):
    b=baseline(); lines=b['cases']['base']['cost']['cost_line_items']
    if change=='duplicate': lines.append(deepcopy(lines[0]))
    elif change=='unknown-guideway': lines.append(line('unreviewed-part','guideway'))
    elif change=='missing-guideway': lines.pop(0)
    elif change=='foreign-candidate': lines[0]['candidate_id']='foreign';t._seal(lines[0],'line_id')
    else: lines.append(line('precast-direct-fasteners','guideway'))
    with pytest.raises(ValueError):t._lines(lines,CID)


@pytest.mark.parametrize('change', ['baseline','quantity','geometry','mass','area','missing-case','reaction-with-matching-areas'])
def test_support_ancestry_quantity_and_case_coverage_rejected(inputs,change):
    candidate,q,cost,b,support=inputs
    if change in {'baseline','quantity','geometry'}:support[change+'_id' if change!='quantity' else 'quantity_evaluation_id']='wrong'
    elif change=='missing-case':support['cases'].pop('low')
    else:
        row=support['cases']['base']['load_cases']['normal']['financial_cases']['base']
        if change=='mass':row['accounted_span_mass_kg']+=1
        elif change=='area':row['minimum_gravity_bearing_area_m2_by_pressure_kpa']['200']+=1
        else:
            row['interior_support_vertical_reaction_N']+=1000.
            row['minimum_gravity_bearing_area_m2_by_pressure_kpa']={str(p):row['interior_support_vertical_reaction_N']/(1000*p) for p in (300,200,100)}
    t._seal(support)
    with pytest.raises(ValueError):t.compose(candidate,q,cost,b,support,root=ROOT)


def test_stale_source_and_mutated_seal_rejected(tmp_path):
    path=tmp_path/'input';path.write_text('one')
    t._source_check({'input':t.digest(path)},tmp_path)
    path.write_text('two')
    with pytest.raises(ValueError,match='Stale'):t._source_check({'input':'old'},tmp_path)
    value=t._seal(dict(value=1));value['value']=2
    with pytest.raises(ValueError,match='sealed'):t._check(value)


def test_physical_identity_retains_vehicle_and_changes_civil_only(inputs):
    candidate,q,cost,b,support=inputs
    a=t.composition(candidate,b)
    b['assumptions']['location']='different financial location'
    assert t.composition(candidate,b)==a
    different=g.realize([[1]])
    assert t.composition(different,b)['candidate_id'] != a['candidate_id']
    assert t.composition(different,b)['physical_definition']['vehicle_components']==a['physical_definition']['vehicle_components']


def test_tool_mismatch_requires_explicit_preserved_evidence_replay(monkeypatch):
    from engineering.development_baseline import selection
    b=baseline(); b['selected'].update(vehicle={'evaluation_id':'vehicle-eval','candidate_id':b['selected']['candidate_id']},
        vehicle_evaluation_id='vehicle-eval', selection_id='selection')
    b.update(selected_vehicle_candidate_id=b['selected']['candidate_id'],
        load_context={'context_id':b['load_context_id']})
    t._seal(b,'baseline_id')
    checked=[]
    monkeypatch.setattr(t,'_source_check',lambda sources,root:checked.append(True))
    monkeypatch.setattr(t,'_sources',lambda root:{})
    monkeypatch.setattr(t,'_load_context',lambda *args:None)
    monkeypatch.setattr(t,'_tools',lambda:{'different':'host'})
    monkeypatch.setattr(selection,'load',lambda root:{'vehicle':b['selected']['vehicle'], 'selection_id':'selection'})
    with pytest.raises(ValueError,match='tools'):t.validate_baseline(b,ROOT)
    assert t.validate_baseline(b,ROOT,require_current_tools=False)==b
    assert checked  # Source checking remains mandatory during cross-host replay.
    with pytest.raises(ValueError,match='boolean'):t.validate_baseline(b,ROOT,require_current_tools='false')


def test_coincident_component_events_are_covered_by_whole_guideway_once(inputs):
    candidate,q,span,b,support=inputs
    a=b['assumptions']
    a['assumptions']['asset_life_years']['guideway']=[15.*16/18,10.,7.*24/18]
    t._seal(a,'assumption_id')
    t._seal(b,'baseline_id');support['baseline_id']=b['baseline_id'];t._seal(support)
    span=c.estimate(candidate,q,span['topology_spec'],a)
    result=t.compose(candidate,q,span,b,support,root=ROOT)
    for output in result['cases'].values():
        for row in output['topology_renewal_schedule']:
            coating=[e for e in row['events'] if e['asset']=='coating']
            assert coating and all(e['covered_by_complete_guideway_replacement'] for e in coating)
            assert all(e['corridor_present_value_iqd']==0 for e in coating)


def test_crew_changes_capacity_and_capital_without_erasing_person_hours(inputs):
    candidate,q,span,b,support=inputs
    crew_result=t.compose(candidate,q,span,b,support,root=ROOT)['cases']['base']
    single_spec=deepcopy(span['topology_spec']);single_spec['production_crew_people']=[1.]*3
    single_span=c.estimate(candidate,q,single_spec,b['assumptions'])
    single_result=t.compose(candidate,q,single_span,b,support,root=ROOT)['cases']['base']
    for i,name in enumerate(t.CASES):
        assert span['cases'][i]['total_factory_person_hours']==single_span['cases'][i]['total_factory_person_hours']
        assert span['cases'][i]['factory_gate_iqd']==single_span['cases'][i]['factory_gate_iqd']
        crew_cells=crew_result['production_plan']['required_guideway_workcells'][i]
        single_cells=single_result['production_plan']['required_guideway_workcells'][i]
        assert crew_cells<single_cells
        for key,rate in [('topology-steel-production-cells','dedicated_plant_capital_iqd')]:
            crew_line=next(r for r in crew_result['cost_line_items'] if r['line_key']==key)
            single_line=next(r for r in single_result['cost_line_items'] if r['line_key']==key)
            assert single_line['scenario_iqd'][name]-crew_line['scenario_iqd'][name]==(single_cells-crew_cells)*span['cases'][i][rate]


def test_topology_coating_and_bearings_restart_after_noncoincident_guideway_replacement(inputs):
    candidate,q,span,b,support=inputs
    a=b['assumptions']
    a['assumptions']['asset_life_years']['guideway']=[20*hours/18 for hours in a['operating_hours_per_day_cases']]
    t._seal(a,'assumption_id');t._seal(b,'baseline_id')
    support['baseline_id']=b['baseline_id'];t._seal(support)
    spec=deepcopy(span['topology_spec']);spec['coating_renewal_years']=[8.]*3;spec['bearing_renewal_years']=[6.]*3
    span=c.estimate(candidate,q,spec,a)
    result=t.compose(candidate,q,span,b,support,root=ROOT)
    for output in result['cases'].values():
        for i,row in enumerate(output['topology_renewal_schedule']):
            assert [e['year'] for e in row['events'] if e['asset']=='coating']==[8.,16.,28.]
            assert [e['year'] for e in row['events'] if e['asset']=='bearings']==[6.,12.,18.,26.]
            for reset in row['component_age_reset_schedules']:
                assert [r['year'] for r in reset['age_resets']]==[20.]
            expected=600*fsum(e['undiscounted_iqd']/1.04**e['year'] for e in row['events'])
            line=next(r for r in output['cost_line_items'] if r['line_key']=='topology-coating-and-bearing-renewals')
            assert line['scenario_iqd'][t.CASES[i]]==round(expected,2)


def test_support_replay_requires_the_recorded_and_executed_producer_digest(tmp_path,monkeypatch):
    from engineering.design_search import civil_topology
    producer=civil_topology.PRODUCER
    path=tmp_path/producer;path.parent.mkdir(parents=True)
    path.write_bytes(Path(civil_topology.__file__).read_bytes())
    with pytest.raises(ValueError,match='executed support-demand producer digest'):
        t._support_replay({}, {}, {'source_sha256':{}}, tmp_path)
    recorded={'source_sha256':{producer:t.digest(path)}}
    other=tmp_path/'other.py';other.write_text('different executed source')
    monkeypatch.setattr(civil_topology,'__file__',str(other))
    with pytest.raises(ValueError,match='executed support-demand producer digest'):
        t._support_replay({}, {}, recorded, tmp_path)
