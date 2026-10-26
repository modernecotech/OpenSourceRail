from copy import deepcopy
import pytest
from engineering.design_search import propulsion_families as m


def parent():return dict(candidate_id='a'*64,requirement_revision='retained-comfort-requirements')


def test_expanded_plan_binds_twelve_options_to_parent_without_default_change():
    plan=m.expanded_plan(parent(),{'failure_reasons':['linear_steel_field_limit','insufficient_conditional_2D_force','unknown_whole_life_cost']})
    assert plan['candidate_proposal_count']==12
    assert plan['distinct_physical_designs']==12
    assert plan['budget']['reserved_primary_native_cases']<=12
    assert not plan['automatic_native_dispatch']
    for row in plan['proposals']:
        p=row['proposal'];assert p['parent_candidate_id']==parent()['candidate_id']
        assert not p['changes_development_default'] and p['available_installed_force_N'] is None
        assert p['physical_accepted'] is False
    alternatives=[r['proposal'] for r in plan['proposals'] if r['proposal']['service_is_requirement_alternative']]
    assert len(alternatives)==2
    assert all(a['requirement_revision']!=parent()['requirement_revision'] for a in alternatives)


def test_multiple_fins_count_material_and_never_scale_old_force():
    rows=m.expanded_plan(parent(),{} )['proposals'];two=rows[1]['screen'];three=rows[2]['screen']
    assert three['stock']['passive_secondary_kg_per_car']/two['stock']['passive_secondary_kg_per_car']==pytest.approx(1.5)
    assert three['available_installed_force_N'] is None
    assert not rows[1]['current_native_adapter_ready']
    with pytest.raises(ValueError,match='adapter'):m.wheel_motor_parameters(rows[1]['proposal'])


def test_cheap_current_fill_and_track_failures_are_retained():
    option=m.expanded_plan(parent(),{})['proposals'][0]['proposal'];p=deepcopy(option)
    p['evaluation_hypotheses']['current_peak_A']=1000.
    assert m.necessary_screens(p)['necessary_screens']['wire_density']=='fail'
    p=deepcopy(option);p['physical']['fin_centres_y_m']=[0.,.1];p['physical_design_id']=m._physical_identity(p['physical'])
    assert m.necessary_screens(p)['necessary_screens']['primary_cross_sections']=='fail'


def test_unknown_prices_and_thermal_mass_are_never_zero():
    row=m.expanded_plan(parent(),{})['proposals'][7]
    assert row['screen']['whole_life_cost_USD'] is None
    assert row['screen']['complete_installed_cost_USD'] is None
    assert row['proposal']['physical']['cooling']['installed_hardware_mass_kg'] is None
    assert row['screen']['actual_protected_headway_s'] is None
    assert row['screen']['nominal_arithmetic_passengers_per_hour_direction']==8280.


def test_supplier_polarization_points_are_not_a_validated_BH_map():
    data=m.material_options();s=data['sij-M330-50A']
    assert s['source_url'].startswith('https://cms.sij.si/') and len(s['source_sha256'])==64
    assert s['minimum_polarization_J_T']==[1.49,1.60,1.70]
    assert s['solver_BH_curve'] is None and s['curve_digitization_verified'] is False
    assert s['qualified'] is False
    assert data['isovac-simulation-catalogue']['solver_BH_curve'] is None


def test_diagnostics_choose_material_and_system_experiments():
    p=m.expanded_plan(parent(),{})['proposals'][0]['proposal']
    tasks=m.next_experiments(p,{'failure_reasons':['outside_linear_material_hypothesis','insufficient_thrust','cost_unknown']})
    kinds={t['kind'] for t in tasks}
    assert {'nonlinear-material-validation','finite-topology-force-map','equal-service-system-comparison'}<=kinds
    assert all(t['parent_candidate_id']==parent()['candidate_id'] and t['physical_acceptance'] is False for t in tasks)


def test_operation_and_display_labels_do_not_change_physical_identity():
    plan=m.expanded_plan(parent(),{});a=plan['proposals'][0]['proposal'];b=deepcopy(a)
    b['label']='renamed';b['evaluation_hypotheses']['current_peak_A']=10.
    assert m._physical_identity(a['physical'])==m._physical_identity(b['physical'])
    assert m.necessary_screens(a)['necessary_screens']['ideal_powered_length']=='pass'
    assert m.necessary_screens(a,dict(accounted_mass_kg_per_car=22672.,rotating_equivalent_mass_kg_per_car=1770.4,parent_passive_fin_mass_kg=9*.015*.16*2710))['required_launch_force_N_lower_bound']>10000


def test_unknown_parent_fin_weight_does_not_become_zero_in_force_requirement():
    option=m.expanded_plan(parent(),{})['proposals'][0]['proposal']
    row=m.necessary_screens(option,dict(accounted_mass_kg_per_car=22672.,rotating_equivalent_mass_kg_per_car=1770.4))
    assert row['accounted_translation_mass_lower_bound_kg_per_car'] is None
    assert row['required_launch_force_N_lower_bound'] is None
