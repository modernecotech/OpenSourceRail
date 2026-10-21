"""Independent quantity controls and no-credit/unknown-evidence regressions."""
from copy import deepcopy
import math
import json
from pathlib import Path
import sys
import tomllib
import pytest
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from engineering.ferrite_maglev import model,optimisation,cities


@pytest.fixture(scope='module')
def context():return model.load()


def test_joint_search_retains_failed_cases_and_only_orders_research(context):
    _,c,k=context;r=optimisation.study(c,k)
    assert r['candidate_count']==720
    assert 0<r['numerical_screen_pass_count']<r['candidate_count']
    best=r['minimum_indexed_allowance_candidate']
    assert best['numerical_screen_pass']
    assert best['civil']['indexed_allowance_usd_dual_km']==min(v['civil']['indexed_allowance_usd_dual_km'] for v in r['candidates'] if v['numerical_screen_pass'])
    assert r['acceptance_eligible_candidate_count']==0
    assert all(not r[f] for f in model.FLAGS)
    assert r['local_value_added_fraction'] is None
    for row in r['candidates']:
        assert not row['accepted'] and all(not row['civil'][f] for f in model.FLAGS)
        assert row['civil']['total_installed_mass_kg_dual_km'] is None


def test_pareto_research_set_has_no_dominating_other_screen_pass(context):
    r=optimisation.study(context[1],context[2]);rows={v['id']:v for v in r['candidates']}
    for key in r['pareto_candidate_ids']:
        v=optimisation._vector(rows[key])
        assert rows[key]['numerical_screen_pass']
        assert not any(all(x<=y for x,y in zip(optimisation._vector(other),v)) and any(x<y for x,y in zip(optimisation._vector(other),v))
            for other in rows.values() if other['numerical_screen_pass'] and other['id']!=key)


def test_reference_cost_reconciles_current_quantity_bill(context):
    _,c,k=context;a=optimisation.load();_,v=optimisation.vehicle(c,k,a['vehicle_profiles'][0])
    box=c['civil']['narrow_box_screen'];span=c['civil']['reference_span_m']
    width,depth,web,flange=(box[key] for key in ('outer_width_m','outer_depth_m','web_thickness_m','flange_thickness_m'))
    void=(width-2*web)*(depth-2*flange);area=width*depth-void;infill=2*.4*void
    result=optimisation.civil(c,k,v,width,depth,web,flange,span,a)
    ref=model.cost_case(c,k,'base',3000,30)
    assert result['indexed_rows_usd_dual_km']==pytest.approx(ref['civil_rows_usd_dual_km'])
    assert result['indexed_allowance_usd_dual_km']==pytest.approx(ref['civil_usd_dual_km'])
    assert result['concrete_m3_dual_km']==pytest.approx((area+infill/span+.12)*2000)
    assert result['counted_concrete_mass_kg_dual_km']==pytest.approx((area+infill/span+.12)*2000*2500)
    assert result['maximum_bare_beam_lift_kg']==pytest.approx((area*span+infill)*2500)
    assert result['shared_supports_per_route_km']==40
    assert result['beam_lifts_per_route_km']==80


def test_longer_spans_reduce_support_count_but_increase_lift_and_deflection(context):
    _,c,k=context;a=optimisation.load();_,v=optimisation.vehicle(c,k,a['vehicle_profiles'][0])
    short=optimisation.civil(c,k,v,.8,1.8,.10,.15,20,a);long=optimisation.civil(c,k,v,.8,1.8,.10,.15,30,a)
    assert long['shared_supports_per_route_km']/short['shared_supports_per_route_km']==pytest.approx(2/3)
    assert long['maximum_bare_beam_lift_kg']/short['maximum_bare_beam_lift_kg']==pytest.approx((.54*30+.72)/(.54*20+.72))
    q=lambda length:(.54+.12)*2500+.72*2500/length+300.23424+26200/17
    assert long['section']['total_elastic_deflection_m']/short['section']['total_elastic_deflection_m']==pytest.approx(1.5**4*q(30)/q(20))
    for key in ('walkway_brackets','installation','night','qa','relocation','traffic'):
        assert short['indexed_rows_usd_dual_km'][key]==long['indexed_rows_usd_dual_km'][key]
    for key in ('supports','temporary','transport','erection'):
        assert long['indexed_rows_usd_dual_km'][key]/short['indexed_rows_usd_dual_km'][key]==pytest.approx(2/3)
    assert not long['crane_capacity_at_radius_verified']


def test_vehicle_targets_preserve_payload_storage_ferrite_capture_and_reserve(context):
    _,c,k=context;a=optimisation.load();baseline=model.mass(c,3000,30)
    for p in a['vehicle_profiles']:
        target,r=optimisation.vehicle(c,k,p)
        assert r['mass']['aw3_kg']-r['mass']['tare_kg']==12000
        assert r['mass']['aw2_kg']-r['mass']['tare_kg']==9000
        assert r['gross_storage_kwh_per_car']==30
        assert r['fixed_allocations_kg']=={'ferrite_base':3000,'capture_landing_emergency_braking':600,'services_battery_low_case_installed_kg':200,'growth_reserve':1800}
        assert r['mass']['tare_kg']==baseline['tare_kg']-r['assumed_mass_saving_kg']
        assert r['imported_input_usd'] is r['local_value_added_fraction'] is None
        assert r['total_moving_parts_count'] is None
        assert 'passenger doors' in r['required_systems_retained']
        assert 'support drives/sensing/cooling' in r['required_systems_retained']
        model.validate(target)


def test_mass_allocation_alone_does_not_invent_procurement_savings(context):
    _,c,k=context;a=optimisation.load();ref=optimisation.vehicle(c,k,a['vehicle_profiles'][0])[1]
    target=optimisation.vehicle(c,k,a['vehicle_profiles'][1])[1]
    assert target['mass']['tare_kg']<ref['mass']['tare_kg']
    assert target['repeat_reference_train_allowance_usd']==ref['repeat_reference_train_allowance_usd']


def test_vehicle_mass_changes_civil_loads_in_same_geometry(context):
    _,c,k=context;a=optimisation.load();target,v=optimisation.vehicle(c,k,a['vehicle_profiles'][-1])
    light=optimisation.civil(target,k,v,.8,1.8,.10,.15,25,a)
    heavy=optimisation.civil(c,k,v,.8,1.8,.10,.15,25,a)
    assert light['section']['vehicle_line_mass_kg_m']==pytest.approx(v['mass']['aw3_kg']/17)
    assert light['section']['total_moment_nm']<heavy['section']['total_moment_nm']
    assert light['section']['total_elastic_deflection_m']<heavy['section']['total_elastic_deflection_m']


def test_route_elevation_is_a_proposal_not_automatic_clearance():
    design={'lines':[{'length_m':1000}],'civil_segments':[
        {'class':name,'from_station_m':0,'to_station_m':length} for name,length in [('at-grade',400),('elevated',500),('bridge',100)]]}
    corridor={'lines':[{'name':'x','shape':'Radial','cells':[[0,0],[1,0],[1,1]]}]}
    before=deepcopy(design);r=optimisation.route_strategy(design,corridor)
    assert r['ordinary_viaduct_proposal_length_m']==900
    assert r['proposed_conversion_from_at_grade_m']==400
    assert r['special_crossings_length_m']=={'bridge':100}
    assert r['target_elevated_mainline_fraction']==.99
    assert r['radial_straightness_observations'][0]['raster_chord_to_path_ratio']==pytest.approx(math.sqrt(2)/2)
    assert not r['zero_impact_demonstrated'] and not r['geographic_alignment_recomputed']
    assert all(item['state']=='unknown' and not item['accepted'] for item in r['required_evidence'])
    assert r['elevated_coverage_achieved'] is r['housing_demolition_demonstrated'] is r['wildlife_impact_demonstrated'] is None
    assert design==before


def test_baghdad_elevated_cost_scope_includes_191km_conversion(context,tmp_path):
    path=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
    r=cities.generate(path,context,output_dir=tmp_path)
    strategy=r['routing_strategy']
    assert strategy['proposed_conversion_from_at_grade_m']==pytest.approx(191033.8)
    assert strategy['ordinary_viaduct_proposal_length_m']==pytest.approx(482238.1)
    assert strategy['special_crossings_length_m']['bridge']==pytest.approx(31097.4)
    for row in r['costs']['scenarios']:
        assert row['ordinary_viaduct_proposal_km']==pytest.approx(sum((segment['to_station_m']-segment['from_station_m'])*strategy['cost_quantity_chainage_scale_by_line'][segment['line']] for segment in json.loads((path/'city.json').read_text())['civil_segments'] if segment['class'] in {'at-grade','elevated'})/1000)
        assert row['complete_city_programme_usd'] is None
    assert {row['scenario'] for row in r['costs']['scenarios']}==set(context[2]['scenario_multipliers'])
    assert all(bill['cars']==6 for row in r['costs']['scenarios'] for bill in row['formation_bills'])
    assert all(g['state']=='open' for g in r['gates'])


@pytest.mark.parametrize('old,new',[
    ('zero_impact_demonstrated = false','zero_impact_demonstrated = true'),
    ('costs_are_quotes = false','costs_are_quotes = true'),
    ('target_elevated_mainline_fraction = 0.99','target_elevated_mainline_fraction = 0.5'),
    ('transport_cost_variable_fraction = 0.5','transport_cost_variable_fraction = 1.5'),
    ('structure_ratio = 0.9','structure_ratio = 0.0'),
    ('"qa", "relocation"','"free-qa", "relocation"'),
])
def test_invalid_or_unqualified_savings_configuration_is_rejected(monkeypatch,tmp_path,old,new):
    config=tmp_path/'search.toml';original=optimisation.INPUT.read_text();assert old in original
    config.write_text(original.replace(old,new));monkeypatch.setattr(optimisation,'INPUT',config)
    with pytest.raises(ValueError):optimisation.load()


def test_no_numerical_candidate_does_not_invent_an_accepted_design(context):
    _,c,k=context;a=optimisation.load();a['civil']['maximum_bare_beam_lift_mass_screen_kg']=1
    result=optimisation._study(optimisation.canonical_inputs(c,k,a))
    assert result['numerical_screen_pass_count']==0
    assert result['minimum_indexed_allowance_candidate'] is None
    assert result['pareto_candidate_ids']==[]
    assert result['acceptance_eligible_candidate_count']==0


def test_actual_retained_rail_mass_cannot_be_replaced_by_lighter_allowance(context):
    _,c,k=context;a=optimisation.load();_,v=optimisation.vehicle(c,k,a['vehicle_profiles'][0])
    box=c['civil']['narrow_box_screen'];span=c['civil']['reference_span_m']
    width,depth,web,flange=(box[key] for key in ('outer_width_m','outer_depth_m','web_thickness_m','flange_thickness_m'))
    void=(width-2*web)*(depth-2*flange);area=width*depth-void;infill=2*.4*void
    result=optimisation.civil(c,k,v,width,depth,web,flange,span,a)
    # Independently count 2 faces x10 cassettes x2.49m x0.96m x20mm x7850kg/m3 /25m.
    expected=2*10*2.49*.96*.02*7850/25
    assert result['native_passive_rail_line_mass_kg_m_per_direction']==pytest.approx(expected)
    assert result['section']['dead_line_mass_kg_m']==pytest.approx((area+infill/span+.12)*2500+expected)
    assert not result['other_attachment_mass_closed']


def test_scorecards_preserve_whole_system_unknowns_and_do_not_relabel_allowances(context):
    r=optimisation.study(context[1],context[2])
    unknown=('installed_cost_usd_dual_route_km','factory_gate_cost_usd_reference_train',
        'total_installed_mass_kg_dual_route_km','maximum_transported_assembly_mass_kg',
        'factory_labour_hours_per_route_km','onsite_labour_hours_per_route_km',
        'construction_working_days_per_route_km','unique_parts_count','moving_assemblies_count',
        'imported_value_usd','specialist_supplier_dependency_count','module_replacement_time_seconds','failed_train_recovery_time_seconds')
    for row in r['candidates']+r['beam_only_candidates']:
        score=row['system_scorecard']
        assert all(score[k] is None for k in unknown)
        assert score['indexed_ordinary_viaduct_allowance_usd_dual_route_km']==row['civil']['indexed_allowance_usd_dual_km']
        assert score['tare_kg_per_car']==row['vehicle']['mass']['tare_kg']
        assert not score['accepted'] and all(score[k] is False for k in model.FLAGS)
    assert not r['fully_coupled_optimisation']
    assert any('actual magnetic force/loss' in link['link'] and link['state'].startswith('open') for link in r['coupling_evidence'])


def test_matched_profile_separates_constant_services_from_mass_sensitive_station_energy(context):
    _,c,k=context;a=optimisation.load()
    ref=optimisation.vehicle(c,k,a['vehicle_profiles'][0])[1]
    light=optimisation.vehicle(c,k,a['vehicle_profiles'][1])[1]
    unchanged=deepcopy(a['vehicle_profiles'][0]);unchanged['hardware_target']=60000
    budget=optimisation.vehicle(c,k,unchanged)[1]
    assert light['matched_duty']['hot_aw3_no_regen_cycle_kwh_per_car']==ref['matched_duty']['hot_aw3_no_regen_cycle_kwh_per_car']
    assert light['matched_duty']['station_traction_input_kwh']<ref['matched_duty']['station_traction_input_kwh']
    assert budget['matched_duty']==ref['matched_duty']
    duty=light['matched_duty']
    p=c['power'];hotel=p['hot_hotel_kw_per_car'];connected=p['charger_effective_seconds']
    disconnected=p['station_dwell_seconds']-connected
    assert duty['balanced_charger_kw_per_car']==pytest.approx((hotel+hotel*(c['vehicle']['runtime_reference_seconds']+disconnected)/connected)/p['station_charger_efficiency_assumption'])
    assert not duty['actual_magnetic_loss_map_used'] and not duty['route_accepted']


def test_new_chute_mass_holds_candidate_energy_until_vehicle_mass_is_closed(context):
    r=optimisation.study(context[1],context[2])
    for row in r['beam_only_candidates']:
        s=row['system_scorecard']
        assert s['additional_onboard_evacuation_mass_required_but_unknown']
        assert s['hot_aw3_no_regen_cycle_kwh_per_car'] is s['balanced_charger_kw_per_car'] is None
    assert all(row['system_scorecard']['hot_aw3_no_regen_cycle_kwh_per_car']>0 for row in r['candidates'])


def test_distinct_extrema_only_use_passing_reference_configurations(context):
    r=optimisation.study(context[1],context[2]);passing=[v for v in r['candidates'] if v['numerical_screen_pass']]
    by_id={v['id']:v for v in passing};e=r['research_extrema']
    cost=by_id[e['lowest_indexed_ordinary_allowance_candidate_id']]
    mass=by_id[e['lowest_counted_concrete_mass_candidate_id']]
    assert cost['civil']['indexed_allowance_usd_dual_km']==min(v['civil']['indexed_allowance_usd_dual_km'] for v in passing)
    assert mass['civil']['counted_concrete_mass_kg_dual_km']==min(v['civil']['counted_concrete_mass_kg_dual_km'] for v in passing)
    assert e['fastest_construction_candidate_id'] is None
    a=optimisation.load();a['civil']['maximum_bare_beam_lift_mass_screen_kg']=1
    empty=optimisation._study(optimisation.canonical_inputs(context[1],context[2],a))['research_extrema']
    assert empty['lowest_indexed_ordinary_allowance_candidate_id'] is empty['lowest_counted_concrete_mass_candidate_id'] is None


def test_route_directness_defines_endpoints_and_does_not_score_rings_as_bad_radials():
    design={'lines':[{'length_m':1000}],'civil_segments':[{'class':'elevated','from_station_m':0,'to_station_m':1000}]}
    corridor={'lines':[
        {'name':'radial','shape':'Radial','cells':[[0,0],[1,0],[1,1]]},
        {'name':'ring','shape':'Ring','cells':[[0,0],[1,0],[1,1],[0,0]]},
        {'name':'zero','shape':'Radial','cells':[[0,0],[0,0]]},
        {'name':'missing','shape':'Radial','cells':[]}]}
    r=optimisation.route_strategy(design,corridor);metrics={m['line']:m for m in r['alignment_comparison_metrics']}
    assert metrics['radial']['path_to_endpoint_chord_ratio']==pytest.approx(math.sqrt(2))
    for key in ('ring','zero','missing'):assert metrics[key]['path_to_endpoint_chord_ratio'] is None
    assert metrics['radial']['minimum_horizontal_radius_m'] is None
    assert metrics['radial']['station_walking_catchment_population'] is None
    assert not metrics['radial']['interchange_access_accepted']



def test_process_rate_changes_invalidate_optimisation_and_city_replay(context):
    from engineering.ferrite_maglev import manufacturing
    from engineering.analysis.tests.test_ferrite_maglev_cities import replay_fixture
    original=manufacturing.INPUT
    assert original in cities.calculation_dependencies()
    _,c,k=context;a=optimisation.load()
    changed=deepcopy(k);changed['rates']['reaction_steel_finished_per_kg']*=2
    before=optimisation.canonical_inputs(c,k,a);after=optimisation.canonical_inputs(c,changed,a)
    assert before!=after
    _,v=optimisation.vehicle(c,k,a['vehicle_profiles'][0])
    old=optimisation.civil(c,k,v,.8,1.8,.10,.15,25,a)
    new=optimisation.civil(c,changed,v,.8,1.8,.10,.15,25,a)
    assert new['indexed_rows_usd_dual_km']['passive_rail_supply']==pytest.approx(2*old['indexed_rows_usd_dual_km']['passive_rail_supply'])
    plan=replay_fixture(context,tomllib.loads(cities.ASSUMPTIONS.read_text()))
    key=original.relative_to(ROOT).as_posix()
    assert key in plan['source_sha256']
    plan['source_sha256'][key]='0'*64
    with pytest.raises(ValueError,match='source'):cities.replay_city(plan)
