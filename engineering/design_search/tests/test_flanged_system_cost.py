"""Same-service cost and scope controls, without structural acceptance."""
from copy import deepcopy
from math import ceil, fsum
from pathlib import Path
import gzip,json

import pytest
from engineering.design_search import flanged_system_cost as f, flanged_span as s, topology_cost, model_cost
from engineering.station_rail.common import identity

ROOT=Path(__file__).resolve().parents[3]
BASELINE_MANIFEST_ID='294de81f3b1cca8215a95704287cfedf74ddfac596232027dee3c030163fdc43'


@pytest.fixture(scope='module')
def actual():
    baseline=json.load(gzip.open(ROOT/'docs/design-engine/civil-topology/baseline.json.gz','rt'))
    p=ROOT/'docs/design-engine/flanged-span-study/original/baseline'
    request=json.loads((p/'request.json').read_bytes());raw=json.loads((p/'result.json').read_bytes())
    args=(request['candidate'],raw['quantities'],raw['cost'],baseline,request['context'])
    return args,f.compare(*args,root=ROOT,expected_baseline_manifest_id=BASELINE_MANIFEST_ID,require_current_tools=baseline['tool_context']==f.base._tools())


def test_current_vehicle_route_load_axes_and_nonpromoting_identity(actual):
    (candidate,quantity,scoped,baseline,context),result=actual
    assert result['candidate_id']==identity(result['physical_definition'])
    assert result['candidate_id'] not in {candidate['candidate_id'],context['vehicle_candidate_id']}
    assert result['physical_definition']['civil_candidate_id']==candidate['candidate_id']
    assert result['physical_definition']['vehicle_components']['candidate_id']==context['vehicle_candidate_id']
    assert result['physical_definition']['route']==baseline['cases']['base']['bundle']['architecture_case']['physical_definition']['route']
    assert result['baseline_id']==baseline['baseline_id']
    assert result['baseline_publication']['manifest_id']==BASELINE_MANIFEST_ID
    assert result['normalized_span_cost']['scoped_cost_evaluation_id']==scoped['evaluation_id']
    assert result['span_cost_evaluation_id']==scoped['evaluation_id']
    assert result['integrated_selection'] is None
    assert result['whole_life_comparison_ready'] is False and result['whole_life_ranking_allowed'] is False
    assert result['replay_context']['native_evaluator_admission'] is False
    assert result['replay_context']['baseline_tool_reuse_check_enforced']==(baseline['tool_context']==f.base._tools())
    assert set(result['cases'])==set(model_cost.CASES)
    assert all(result[k] is False for k in f.FLAGS)
    for mass,row in result['cases'].items():
        assert set(row['scope_totals_iqd'])==set(model_cost.SCOPES)
        assert len(row['scope_totals_iqd'])==14
        assert row['corridor_basis']['span_count']==600
        assert row['corridor_basis']['fleet_trainsets']==8
        assert row['corridor_basis']['offered_capacity_pphpd']==8280
        assert row['candidate_id']==result['candidate_id']
        assert all(row[k] is False for k in f.FLAGS)
        assert all(line['candidate_id']==result['candidate_id'] for line in row['cost_line_items'])
        assert len({line['line_key'] for line in row['cost_line_items']})==len(row['cost_line_items'])
        assert all(v[1]>0 for v in row['scope_totals_iqd'].values())


def test_factory_quantities_are_repriced_from_real_process_not_original_prices(actual):
    (candidate,q,scoped,b,_),result=actual;normalized=result['normalized_span_cost'];a=b['assumptions']['assumptions'];bench=b['assumptions']['benchmark_rates_iqd'];ts=topology_cost.default_spec();raw=scoped['cases'];n=600
    assert all(r['rails_and_fastener_cost_excluded'] for r in normalized['cases'])
    output=result['cases']['base'];lines={r['line_key']:r for r in output['cost_line_items']}
    for i,name in enumerate(model_cost.CASES):
        r=normalized['cases'][i];source=raw[name];items=r['factory_items_iqd']
        steel=q['source_quantities']['by_material']['structural_steel']['mass_kg']
        assert items['main_steel']==pytest.approx(steel/ts['steel_purchase_yield'][i]*a['steel_iqd_per_kg'][i])
        policy=normalized['reserve_process_spec']
        assert items['reserve_deck_rebar']==pytest.approx(q['reserve_mass_kg']['deck_rebar'][i]/policy['steel_material_yield'][i]*bench['rebar_iqd_per_kg']*a['material_rate_sensitivity'][i])
        assert items['reserve_bearings']==pytest.approx(q['reserve_mass_kg']['bearings'][i]*a['finished_equipment_iqd_per_kg'][i])
        assert r['actual_process_hours']==source['factory_labour_hours']
        added=r['added_reserve_process_person_hours']
        assert all(x>0 for x in added.values()) and r['added_reserve_machine_hours']>0
        assert added['rebar_cut_bend_tie']==pytest.approx(q['reserve_mass_kg']['deck_rebar'][i]*policy['rebar_cut_bend_tie_person_hours_per_kg'][i])
        assert added['bracing_cut_weld']==pytest.approx(q['reserve_mass_kg']['bracing'][i]*policy['bracing_cut_weld_person_hours_per_kg'][i])
        assert source['factory_labour_hours']['full_moment_splice_weld']>0 and source['factory_labour_hours']['qa']>0
        assert r['total_factory_person_hours']==pytest.approx(fsum(source['factory_labour_hours'].values())+r['added_coating_person_hours']+fsum(added.values()))
        assert r['machine_operating_hours']==pytest.approx(source['machine_operating_hours']+r['added_reserve_machine_hours'])
        assert items['process_labour']==pytest.approx(r['total_factory_person_hours']*r['shared_loaded_wage_iqd_per_h'])
        assert r['factory_gate_iqd']==pytest.approx(fsum(items.values())*(1+a['factory_overhead_fraction'][i]))
        assert lines['flanged-span-factory-gate']['scenario_iqd'][name]==pytest.approx(round(n*r['factory_gate_iqd'],2),abs=.01)
        assert 'running_rails' not in items and 'fastener_sets' not in items
        # Original illustrative prices differ and are preserved, not added a second time.
        assert r['factory_gate_iqd'] != source['factory_gate_iqd']


def test_rails_reserves_transport_and_erection_are_counted_once(actual):
    (_,q,scoped,b,_),result=actual;row=result['cases']['base'];lines={r['line_key']:r for r in row['cost_line_items']};original={r['line_key']:r for r in b['cases']['base']['cost']['cost_line_items']};n=600
    assert set(f.base.GUIDEWAY_KEYS)&set(lines)=={'precast-rails','rail-fastener-sets'}
    assert lines['precast-rails']['scenario_iqd']==original['precast-rails']['scenario_iqd']
    assert lines['rail-fastener-sets']['scenario_iqd']==original['rail-fastener-sets']['scenario_iqd']
    assert lines['rail-fastener-sets']['quantity']['sets']==n*q['fastener_set_count']
    assert lines['rail-fastener-sets']['quantity']['counted_hardware_mass_kg']==n*q['fastener_mass_kg']
    for i,name in enumerate(model_cost.CASES):
        x=result['normalized_span_cost']['cases'][i];old=scoped['cases'][name];spec=scoped['assumptions']
        assert old['civil_labour_hours']==pytest.approx(x['erection_person_hours']+x['rail_person_hours_excluded'])
        assert x['rail_person_hours_excluded']==pytest.approx(q['fastener_set_count']*spec['rates']['rail_install_h_set'][i])
        haul=n*x['accounted_mass_kg']/1000*x['transport_distance_km']*x['transport_iqd_per_tonne_km']
        assert lines['flanged-accounted-module-and-rail-haul']['scenario_iqd'][name]==pytest.approx(round(haul,2),abs=.01)
        c=lines['flanged-erection-rail-and-temporary-works']['components_iqd']
        assert c['rail_installation'][i]==original['erection-rail-installation-and-temporary-works']['components_iqd']['rail_installation'][i]
        assert c['labour'][i]==pytest.approx(n*x['erection_person_hours']*x['shared_loaded_wage_iqd_per_h'])
        shifts=ceil(n*x['crane_hours']/(8*b['assumptions']['productive_utilisation']))
        assert c['crane'][i]==pytest.approx(shifts*x['crane_iqd_per_shift'])
        assert lines['flanged-erection-rail-and-temporary-works']['quantity']['paid_crane_shifts'][i]==shifts
        if name=='base':
            assert shifts==1600 and n*x['crane_hours']/8==1200
            assert c['crane'][i]-1200*x['crane_iqd_per_shift']==400*x['crane_iqd_per_shift']
        assert lines['flanged-erection-rail-and-temporary-works']['scenario_iqd'][name]==pytest.approx(round(sum(c[k][i] for k in ('labour','crane','rail_installation','contingency')),2),abs=.02)


def test_support_is_explicit_scenario_and_foundation_prices_are_not_represented_as_site_design(actual):
    (_,q,_,b,context),result=actual;support=result['support_demands']
    assert support['quantity_evaluation_id']==q['evaluation_id'] and support['load_context_id']==context['context_id']
    assert 'no finite-bearing amplification' in support['basis'] and 'physical upper bound' in support['basis']
    for mass,container in support['cases'].items():
        assert set(container['load_cases'])=={'empty','normal','crowd_control'}
        for vehicle in container['load_cases'].values():
            for finance,row in vehicle['financial_cases'].items():
                assert row['accounted_span_mass_kg']==q['accounted_mass_kg_cases'][finance]
                assert row['adjacent_span_dead_reaction_N']==pytest.approx(row['accounted_span_mass_kg']*f.civil.G)
                assert row['interior_support_vertical_reaction_N']==pytest.approx(row['adjacent_span_dead_reaction_N']+row['ideal_point_bearing_live_reaction_N'])
                for pressure,area in row['minimum_gravity_area_m2_by_assumed_pressure_kpa'].items():
                    assert area==pytest.approx(row['interior_support_vertical_reaction_N']/(int(pressure)*1000))
                assert row['actual_foundation_quantity'] is None and not row['soil_capacity_verified']
        line=next(x for x in result['cases'][mass]['cost_line_items'] if x['line_key']=='foundation-footing-pier-proxy')
        prior=next(x for x in b['cases'][mass]['cost']['cost_line_items'] if x['line_key']=='foundation-footing-pier-proxy')
        assert line['scenario_iqd']==prior['scenario_iqd']
        assert line['quantity']['price_proxy_mass_coupled'] is False
        assert line['quantity']['site_capacity_verified'] is False


def test_shift_capacity_and_disjoint_lifecycle_arithmetic(actual):
    (_,_,scoped,b,_),result=actual;a=b['assumptions'];spec=scoped['assumptions'];n=600
    for row in result['cases'].values():
        p=row['production_plan'];assert p['production_shifts_per_day']==p['civil_shifts_per_day']==2
        assert p['production_hours_per_shift']==p['civil_hours_per_shift']==8
        assert p['operations_shifts_per_day_cases']==[2,2,3]
        assert not p['guideway_workcell_basis']['machine_cycle_and_precedence_throughput_resolved']
        assert not p['construction_schedule_days']['precedence_and_resource_conflicts_resolved']
        assert row['renewal_plan']['conservation']['every_source_component_allocated_once']
        assert result['comparison_to_corrected_canonical_baseline'][row['vehicle_mass_case']]['whole_life_NPV_delta_iqd'] is None
        assert result['comparison_to_corrected_canonical_baseline'][row['vehicle_mass_case']]['whole_life_rankable'] is False
        lines={r['line_key']:r for r in row['cost_line_items']}
        assert lines['planned-maintenance-and-spares-lifecycle']['quantity']['capital_renewal_events_excluded_by_assumption'] is True
        assert lines['selected-service-battery-and-services-renewal']['quantity']['source_account_line_id']==lines['retained-equipment/selected-service-battery-and-services']['line_id']
        for i,name in enumerate(model_cost.CASES):
            hours=n*result['normalized_span_cost']['cases'][i]['total_factory_person_hours'];capacity=a['production_years']*a['production_days_per_year']*16*a['productive_utilisation']*spec['production_crew_per_shift']
            assert p['guideway_factory_hours'][i]==pytest.approx(hours)
            assert p['required_guideway_workcells'][i]==ceil(hours/capacity)
            assert row['model_based_installed_CAPEX_iqd'][i]==pytest.approx(round(fsum(x['scenario_iqd'][name] for x in row['cost_line_items'] if x['cost_stage'] in model_cost.INITIAL_COST_STAGES),2),abs=.01)
            assert row['model_based_whole_life_NPV_iqd'][i]==pytest.approx(round(fsum(x['scenario_iqd'][name] for x in row['cost_line_items']),2),abs=.01)
            assert lines['flanged-coating-and-bearing-renewals']['scenario_iqd'][name]==pytest.approx(round(fsum(x['corridor_present_value_iqd'] for x in row['flanged_renewal_schedule'][i]['events']),2),abs=.01)


@pytest.mark.parametrize('damage',['candidate','quantity','scoped','rail','shift'])
def test_mixed_or_forged_candidate_quantities_and_costs_are_rejected(actual,damage):
    args,_=actual;candidate,q,scoped,b,context=deepcopy(args)
    if damage=='candidate':candidate['candidate_id']='0'*64
    elif damage=='quantity':q['accounted_mass_kg_cases']['base']+=1;s._seal(q,'evaluation_id')
    elif damage=='scoped':scoped['cases']['base']['factory_gate_iqd']+=1;s._seal(scoped,'evaluation_id')
    elif damage=='rail':
        q['rail_mass_kg']+=1;s._seal(q,'evaluation_id')
    else:
        scoped['assumptions']['production_shifts_per_day']=1;s._seal(scoped,'evaluation_id')
    with pytest.raises(ValueError):f._quantity_checks(candidate,q,scoped,b)


def test_mixed_context_and_vehicle_cannot_gain_admission(actual):
    args,_=actual;_,_,_,baseline,context=deepcopy(args)
    context['vehicle_candidate_id']='0'*64;s._seal(context,'context_id')
    with pytest.raises(ValueError):f._contexts(baseline,context,ROOT,expected_baseline_manifest_id=BASELINE_MANIFEST_ID,require_current_tools=baseline['tool_context']==f.base._tools())


def test_gauge_and_process_changes_propagate_without_changing_vehicle_identity(actual):
    (_,_,_,b,context),result=actual
    candidate=s.generate('thick-flange');quantity=s.quantities(candidate);scoped=s.estimate(candidate,quantity)
    normalized=f._normalized(candidate,quantity,scoped,b)
    assert candidate['candidate_id']!=result['physical_definition']['civil_candidate_id']
    assert f.composition(candidate,b)['candidate_id']!=result['candidate_id']
    assert all(normalized['cases'][i]['factory_gate_iqd']>result['normalized_span_cost']['cases'][i]['factory_gate_iqd'] for i in range(3))
    assert context['vehicle_candidate_id']==result['physical_definition']['vehicle_components']['candidate_id']


@pytest.mark.parametrize('gauge',['thick-web','thick-flange'])
def test_actual_other_gauges_reach_all_scopes_under_same_service(actual,gauge):
    args,prior=actual;baseline=args[3];folder=ROOT/'docs/design-engine/flanged-span-study/original'/gauge
    request=json.loads((folder/'request.json').read_bytes());data=json.loads((folder/'result.json').read_bytes())
    result=f.compare(request['candidate'],data['quantities'],data['cost'],baseline,request['context'],root=ROOT,
        expected_baseline_manifest_id=BASELINE_MANIFEST_ID,require_current_tools=baseline['tool_context']==f.base._tools())
    assert result['candidate_id']!=prior['candidate_id']
    assert result['physical_definition']['civil_candidate_id']==request['candidate']['candidate_id']
    assert result['physical_definition']['vehicle_components']==prior['physical_definition']['vehicle_components']
    assert result['physical_definition']['route']==prior['physical_definition']['route']
    assert result['load_context_id']==prior['load_context_id']
    for case in model_cost.CASES:
        assert set(result['cases'][case]['scope_totals_iqd'])==set(model_cost.SCOPES)
        assert result['cases'][case]['corridor_basis']==prior['cases'][case]['corridor_basis']
        assert result['cases'][case]['support_demand_evaluation_id']==result['support_demands']['evaluation_id']
        assert result['cases'][case]['model_based_installed_CAPEX_iqd'][1]>prior['cases'][case]['model_based_installed_CAPEX_iqd'][1]
    assert result['integrated_selection'] is None and not result['physical_accepted']


def test_reserve_process_rates_increase_hours_and_cost_without_changing_physical_identity(actual):
    (candidate,q,scoped,b,_),result=actual;policy=f.reserve_process_spec()
    policy['rebar_cut_bend_tie_person_hours_per_kg']=[x*2 for x in policy['rebar_cut_bend_tie_person_hours_per_kg']]
    new=f._normalized(candidate,q,scoped,b,policy)
    assert new['candidate_id']==result['normalized_span_cost']['candidate_id']
    assert new['evaluation_id']!=result['normalized_span_cost']['evaluation_id']
    assert all(new['cases'][i]['total_factory_person_hours']>result['normalized_span_cost']['cases'][i]['total_factory_person_hours'] for i in range(3))
    assert all(new['cases'][i]['factory_gate_iqd']>result['normalized_span_cost']['cases'][i]['factory_gate_iqd'] for i in range(3))
    assert new['cases'][1]['actual_process_hours']['brace_assembly']==result['normalized_span_cost']['cases'][1]['actual_process_hours']['brace_assembly']


@pytest.mark.parametrize('damage',['zero','unordered','missing','yield'])
def test_missing_or_invalid_reserve_process_assumptions_are_rejected(damage):
    spec=f.reserve_process_spec()
    if damage=='zero':spec['rebar_cut_bend_tie_person_hours_per_kg'][1]=0
    elif damage=='unordered':spec['bracing_cut_weld_person_hours_per_kg']=[.2,.01,.3]
    elif damage=='missing':del spec['fabricated_reserve_qa_person_hours_per_kg']
    else:spec['steel_material_yield'][0]=1.1
    with pytest.raises(ValueError):f._reserve_spec(spec)


def test_resealed_forged_foundation_proxy_does_not_match_pinned_publication(actual):
    args,_=actual;b=deepcopy(args[3]);cost=b['cases']['base']['cost']
    line=next(x for x in cost['cost_line_items'] if x['line_key']=='foundation-footing-pier-proxy')
    line['scenario_iqd']={k:v/2 for k,v in line['scenario_iqd'].items()}
    if 'components_iqd' in line:
        line['components_iqd']={k:[v/2 for v in values] for k,values in line['components_iqd'].items()}
    f.base._seal(line,'line_id');f.base._seal(cost);f.base._seal(b,'baseline_id')
    with pytest.raises(ValueError,match='authenticated published archive'):
        f._authenticated_baseline(b,ROOT,BASELINE_MANIFEST_ID)


def test_wrong_or_missing_external_baseline_manifest_is_rejected(actual):
    b=actual[0][3]
    for value in ('0'*64,'wrong',None):
        with pytest.raises(ValueError):f._authenticated_baseline(b,ROOT,value)
