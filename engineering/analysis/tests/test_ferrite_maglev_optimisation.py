"""Independent quantity controls and no-credit/unknown-evidence regressions."""
from copy import deepcopy
import math
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
    assert r['candidate_count']==432
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


def test_reference_cost_reproduces_workbook_without_double_credit(context):
    _,c,k=context;a=optimisation.load();_,v=optimisation.vehicle(c,k,a['vehicle_profiles'][0])
    result=optimisation.civil(c,k,v,.8,1.6,.15,.18,25,a)
    ref=model.cost_case(c,k,'base',3000,225)
    assert result['indexed_rows_usd_dual_km']==pytest.approx(ref['civil_rows_usd_dual_km'])
    assert result['indexed_allowance_usd_dual_km']==pytest.approx(ref['civil_usd_dual_km'])
    assert result['concrete_m3_dual_km']==pytest.approx(1560)
    assert result['counted_concrete_mass_kg_dual_km']==pytest.approx(3900000)
    assert result['maximum_bare_beam_lift_kg']==pytest.approx(41250)
    assert result['shared_supports_per_route_km']==40
    assert result['beam_lifts_per_route_km']==80


def test_longer_spans_reduce_support_count_but_increase_lift_and_deflection(context):
    _,c,k=context;a=optimisation.load();_,v=optimisation.vehicle(c,k,a['vehicle_profiles'][0])
    short=optimisation.civil(c,k,v,.8,1.6,.15,.18,20,a);long=optimisation.civil(c,k,v,.8,1.6,.15,.18,30,a)
    assert long['shared_supports_per_route_km']/short['shared_supports_per_route_km']==pytest.approx(2/3)
    assert long['maximum_bare_beam_lift_kg']/short['maximum_bare_beam_lift_kg']==pytest.approx(1.5)
    assert long['section']['total_elastic_deflection_m']/short['section']['total_elastic_deflection_m']==pytest.approx(1.5**4)
    for key in a['civil']['unchanged_cost_rows']:
        assert short['indexed_rows_usd_dual_km'][key]==long['indexed_rows_usd_dual_km'][key]
    assert not long['crane_capacity_at_radius_verified']


def test_vehicle_targets_preserve_payload_storage_ferrite_capture_and_reserve(context):
    _,c,k=context;a=optimisation.load();baseline=model.mass(c,3000,225)
    for p in a['vehicle_profiles']:
        target,r=optimisation.vehicle(c,k,p)
        assert r['mass']['aw3_kg']-r['mass']['tare_kg']==12000
        assert r['mass']['aw2_kg']-r['mass']['tare_kg']==9000
        assert r['gross_storage_kwh_per_car']==225
        assert r['fixed_allocations_kg']=={'ferrite_base':3000,'capture_landing_emergency_braking':600,'battery_150kwh_installed':1500,'growth_reserve':1800}
        assert r['mass']['tare_kg']==baseline['tare_kg']-r['assumed_mass_saving_kg']
        assert r['removed_wheel_gear_credit_usd_train']==206600
        assert r['imported_input_usd'] is r['local_value_added_fraction'] is None
        assert r['total_moving_parts_count'] is None
        assert 'passenger doors' in r['required_systems_retained']
        assert 'support drives/sensing/cooling' in r['required_systems_retained']
        model.validate(target)


def test_mass_allocation_alone_does_not_invent_procurement_savings(context):
    _,c,k=context;a=optimisation.load();ref=optimisation.vehicle(c,k,a['vehicle_profiles'][0])[1]
    target=optimisation.vehicle(c,k,a['vehicle_profiles'][1])[1]
    assert target['mass']['tare_kg']<ref['mass']['tare_kg']
    assert target['repeat_three_car_train_allowance_usd']==ref['repeat_three_car_train_allowance_usd']


def test_vehicle_mass_changes_civil_loads_in_same_geometry(context):
    _,c,k=context;a=optimisation.load();target,v=optimisation.vehicle(c,k,a['vehicle_profiles'][-1])
    light=optimisation.civil(target,k,v,.8,1.6,.15,.18,25,a)
    heavy=optimisation.civil(c,k,v,.8,1.6,.15,.18,25,a)
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
        assert row['ordinary_viaduct_proposal_km']==pytest.approx(482.2381)
        assert row['complete_city_programme_usd'] is None
    assert r['costs']['scenarios'][-1]['scenario']=='indexed-joint-optimisation-target'
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
    result=optimisation._study(__import__('json').dumps([c,k,a],sort_keys=True))
    assert result['numerical_screen_pass_count']==0
    assert result['minimum_indexed_allowance_candidate'] is None
    assert result['pareto_candidate_ids']==[]
    assert result['acceptance_eligible_candidate_count']==0


def test_actual_retained_rail_mass_cannot_be_replaced_by_lighter_allowance(context):
    _,c,k=context;a=optimisation.load();_,v=optimisation.vehicle(c,k,a['vehicle_profiles'][0])
    result=optimisation.civil(c,k,v,.8,1.6,.15,.18,25,a)
    # Independently count 2 faces x10 cassettes x2.49m x0.96m x20mm x7850kg/m3 /25m.
    expected=2*10*2.49*.96*.02*7850/25
    assert result['native_passive_rail_line_mass_kg_m_per_direction']==pytest.approx(expected)
    assert result['section']['dead_line_mass_kg_m']==pytest.approx((.66+.12)*2500+expected)
    assert not result['other_attachment_mass_closed']
