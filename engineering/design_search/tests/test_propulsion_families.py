from copy import deepcopy
import pytest
from engineering.design_search import propulsion_families as m


def service():
    return dict(speed_m_s=20.,acceleration_m_s2=1.,service_deceleration_m_s2=.8,
        headway_s=120.,dwell_s=35.,cars=6,people_per_car=46,train_length_m=104.5,
        car_length_m=17.,jerk_m_s3=.5,grade_fraction=0.,station_spacing_m=2000.)


def parent():return dict(candidate_id='a'*64,requirement_revision='explicit-comfort-requirements',service_requirements=service())


def layout():
    return dict(candidate_id='a'*64,body_candidate_id='b'*64,passive_interface_id='c'*64,
        module_length_m=12.5,module_policy='whole-modules',directions=2,
        independent_branches_per_direction=3,strategy='jerk-limited-launch-envelope',start_m=0.)


def plan(diagnostics=None,*,requested_service=None,requested_layout=None):
    return m.expanded_plan(parent(),diagnostics or {},service_requirements=service() if requested_service is None else requested_service,
        station_layout=layout() if requested_layout is None else requested_layout)


def revise(option,*,physical=None,evaluation=None,requested_service=None,requested_layout=None):
    return m._option(parent(),physical or deepcopy(option['physical']),evaluation or deepcopy(option['evaluation_hypotheses']),
        requested_service or deepcopy(option['service']),requested_layout or deepcopy(option['station_layout_request']),'revised','Explicit test revision')


def test_expanded_plan_binds_twelve_options_to_parent_without_default_change():
    value=plan({'failure_reasons':['linear_steel_field_limit','insufficient_conditional_2D_force','unknown_whole_life_cost']})
    assert value['candidate_proposal_count']==12
    assert value['distinct_physical_designs']==12
    assert value['budget']['reserved_primary_native_cases']<=12
    assert not value['automatic_native_dispatch']
    for row in value['proposals']:
        p=row['proposal'];assert p['parent_candidate_id']==parent()['candidate_id']
        assert not p['changes_development_default'] and p['available_installed_force_N'] is None
        assert p['physical_accepted'] is False
    alternatives=[r['proposal'] for r in value['proposals'] if r['proposal']['service_is_requirement_alternative']]
    assert not alternatives
    assert all(r['proposal']['service']==service() for r in value['proposals'])


def test_multiple_fins_count_material_and_never_scale_old_force():
    rows=plan()['proposals'];two=rows[1]['screen'];three=rows[2]['screen']
    assert three['stock']['passive_secondary_kg_per_car']/two['stock']['passive_secondary_kg_per_car']==pytest.approx(1.5)
    assert three['available_installed_force_N'] is None
    assert not rows[1]['current_native_adapter_ready']
    with pytest.raises(ValueError,match='adapter'):m.wheel_motor_parameters(rows[1]['proposal'])


def test_cheap_current_fill_and_track_failures_are_retained():
    option=plan()['proposals'][0]['proposal'];p=deepcopy(option)
    e=deepcopy(p['evaluation_hypotheses']);e['current_peak_A']=1000.;p=revise(p,evaluation=e)
    assert m.necessary_screens(p)['necessary_screens']['wire_density']=='fail'
    physical=deepcopy(option['physical']);physical['fin_centres_y_m']=[0.,.1];p=revise(option,physical=physical)
    assert m.necessary_screens(p)['necessary_screens']['primary_cross_sections']=='fail'


def test_unknown_prices_and_thermal_mass_are_never_zero():
    row=plan()['proposals'][7]
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
    p=plan()['proposals'][0]['proposal']
    tasks=m.next_experiments(p,{'failure_reasons':['outside_linear_material_hypothesis','insufficient_thrust','cost_unknown']})
    kinds={t['kind'] for t in tasks}
    assert {'nonlinear-material-validation','finite-topology-force-map','equal-service-system-comparison'}<=kinds
    assert all(t['parent_candidate_id']==parent()['candidate_id'] and t['physical_acceptance'] is False for t in tasks)


def test_operation_and_display_labels_do_not_change_physical_identity():
    value=plan();a=value['proposals'][0]['proposal'];e=deepcopy(a['evaluation_hypotheses']);e['current_peak_A']=10.;b=revise(a,evaluation=e)
    assert m._physical_identity(a['physical'])==m._physical_identity(b['physical'])
    assert m.necessary_screens(a)['necessary_screens']['ideal_powered_length']=='pass'
    assert m.necessary_screens(a,dict(accounted_mass_kg_per_car=22672.,rotating_equivalent_mass_kg_per_car=1770.4,parent_passive_fin_mass_kg=9*.015*.16*2710))['required_launch_force_N_lower_bound']>10000


def test_unknown_parent_fin_weight_does_not_become_zero_in_force_requirement():
    option=plan()['proposals'][0]['proposal']
    row=m.necessary_screens(option,dict(accounted_mass_kg_per_car=22672.,rotating_equivalent_mass_kg_per_car=1770.4))
    assert row['accounted_translation_mass_lower_bound_kg_per_car'] is None
    assert row['required_launch_force_N_lower_bound'] is None


def test_missing_context_never_chooses_a_powered_length_or_service():
    with pytest.raises(ValueError,match='service_requirements'):m.expanded_plan(parent(),{})
    with pytest.raises(ValueError,match='station_layout'):m.expanded_plan(parent(),{},service_requirements=service())
    broken=service();broken.pop('grade_fraction')
    with pytest.raises(ValueError,match='service_requirements'):plan(requested_service=broken)


def test_explicit_faster_acceleration_and_derived_geometry_have_no_catalogue_length():
    value=plan()
    for row in value['proposals']:
        p=row['proposal'];b=row['screen']['launch_bounds']
        assert p['service']['acceleration_m_s2']==1.
        assert b['constant_acceleration_stroke_m']==200.
        assert b['jerk_limited_stroke_m']==220.
        assert p['installation_layout']['per_direction']['installed_length_m']==325.
        assert 'service_bounds' not in row['screen']['necessary_screens']
        assert row['screen']['available_installed_force_N'] is None
        assert p['installation_layout']['per_direction']['installed_length_m'] not in (100.,900.)


def test_explicit_insufficient_launch_is_preserved_as_a_geometric_failure():
    request=layout();request.pop('strategy');request.pop('start_m')
    request['sections']=[dict(section_id='launch',start_m=0.,length_m=100.,role='launch')]
    row=plan(requested_layout=request)['proposals'][0]
    assert row['screen']['necessary_screens']['ideal_powered_length']=='fail'
    assert row['screen']['stock']['bare_primary_kg_per_station_direction']>0
    assert row['screen']['available_installed_force_N'] is None


def test_module_rounded_stock_counts_directions_but_not_electrical_branches():
    first=plan()['proposals'][0];request=layout();request['independent_branches_per_direction']=9
    other=plan(requested_layout=request)['proposals'][0]
    a=first['screen']['stock'];b=other['screen']['stock']
    assert a['bare_primary_kg_per_station_direction']==b['bare_primary_kg_per_station_direction']
    assert a['bare_primary_kg_all_directions']==2*a['bare_primary_kg_per_station_direction']
    assert b['electrical_branches']==18 and b['branch_count_duplicates_primary_stock'] is False
    assert first['proposal']['installation_layout']['layout_id']!=other['proposal']['installation_layout']['layout_id']


def test_physical_component_installation_and_evaluation_identities_are_separate():
    a=plan()['proposals'][0]['proposal'];svc=service();svc['headway_s']=180
    b=plan(requested_service=svc)['proposals'][0]['proposal']
    assert a['physical_design_id']==b['physical_design_id']
    assert a['candidate_configuration_id']==b['candidate_configuration_id']
    assert a['installation_layout']['physical_layout_id']==b['installation_layout']['physical_layout_id']
    assert a['evaluation_id']!=b['evaluation_id'] and a['service_requirements_id']!=b['service_requirements_id']
    request=layout();request.pop('strategy');request.pop('start_m')
    request['sections']=[dict(section_id='explicit-launch',start_m=0.,length_m=400.,role='launch')]
    c=plan(requested_layout=request)['proposals'][0]['proposal']
    assert a['physical_design_id']==c['physical_design_id']
    assert a['installation_layout']['physical_layout_id']!=c['installation_layout']['physical_layout_id']
    assert a['candidate_configuration_id']!=c['candidate_configuration_id']


def test_geometry_labels_do_not_create_another_physical_installation():
    r=layout();r.pop('strategy');r.pop('start_m');r['sections']=[dict(section_id='A',start_m=0.,length_m=400.,role='launch')]
    a=plan(requested_layout=r)['proposals'][0]['proposal'];r['sections'][0]['section_id']='renamed'
    b=plan(requested_layout=r)['proposals'][0]['proposal']
    assert a['candidate_configuration_id']==b['candidate_configuration_id']
    assert a['installation_layout']['physical_layout_id']==b['installation_layout']['physical_layout_id']
    assert a['installation_layout']['layout_id']!=b['installation_layout']['layout_id']


def test_current_hypothesis_changes_evaluation_without_changing_installed_geometry():
    a=plan()['proposals'][0]['proposal'];e=deepcopy(a['evaluation_hypotheses']);e['current_peak_A']=10.
    b=revise(a,evaluation=e)
    assert a['candidate_configuration_id']==b['candidate_configuration_id']
    assert a['evaluation_id']!=b['evaluation_id']
    assert m.necessary_screens(b)['evaluation_id']==b['evaluation_id']
    bad=deepcopy(a);bad['evaluation_hypotheses']['current_peak_A']=10.
    with pytest.raises(ValueError,match='evaluation identity'):m.necessary_screens(bad)


def test_grade_changes_required_effort_under_same_declared_counted_mass():
    c=dict(accounted_mass_kg_per_car=22672.,rotating_equivalent_mass_kg_per_car=1770.4,parent_passive_fin_mass_kg=9*.015*.16*2710)
    a=m.necessary_screens(plan()['proposals'][0]['proposal'],c)
    svc=service();svc['grade_fraction']=.02
    b=m.necessary_screens(plan(requested_service=svc)['proposals'][0]['proposal'],c)
    assert b['required_launch_force_N_lower_bound']>a['required_launch_force_N_lower_bound']


def test_single_and_multiple_fin_face_joint_counts_are_explicit():
    rows=plan()['proposals'];single=rows[8]['proposal']['installation_layout'];three=rows[2]['proposal']['installation_layout']
    assert single['physical_definition']['faces_per_track']==1
    assert three['physical_definition']['faces_per_track']==6
    assert three['per_direction']['stator_face_module_joints']==6*three['per_direction']['longitudinal_module_interfaces']


def test_mixed_parent_layout_and_overlapping_installed_sections_rejected():
    r=layout();r['candidate_id']='f'*64
    with pytest.raises(ValueError,match='different parent'):plan(requested_layout=r)
    r=layout();r.pop('strategy');r.pop('start_m')
    r['sections']=[dict(section_id='a',start_m=0.,length_m=101.,role='launch'),dict(section_id='b',start_m=101.,length_m=100.,role='receiving')]
    with pytest.raises(ValueError,match='overlap'):plan(requested_layout=r)


def test_receiving_plant_is_optional_but_not_an_independent_braking_proof():
    row=plan()['proposals'][0]
    assert [r['role'] for r in row['proposal']['installation_layout']['sections']]==['launch']
    assert row['screen']['installed_engineering_screen']=='unknown'
    assert row['screen']['actual_protected_headway_s'] is None
    assert any('headway' in s for s in row['screen']['unknown_inventory_and_evidence'])


def test_old_derived900_stock_is_not_reintroduced_by_wheel_native_definition(monkeypatch):
    original=m.wheel_motor.base.definition
    def finite_unit():
        d=original();d.pop('bare_900m_stock_kg_per_direction',None);return d
    monkeypatch.setattr(m.wheel_motor.base,'definition',finite_unit)
    value=m.wheel_motor.definition(m.wheel_motor_parameters(plan()['proposals'][0]['proposal']))
    assert 'bare_900m_stock_kg_per_direction' not in value


@pytest.mark.parametrize('bad',[True,float('nan'),float('inf'),0.,-1.])
def test_invalid_acceleration_cannot_enter_a_proposal(bad):
    svc=service();svc['acceleration_m_s2']=bad
    with pytest.raises(ValueError):plan(requested_service=svc)


def test_wrong_candidate_mass_cannot_enter_a_bound():
    with pytest.raises(ValueError,match='different parent'):
        m.necessary_screens(plan()['proposals'][0]['proposal'],dict(candidate_id='f'*64,accounted_mass_kg_per_car=22672.))


def test_disconnected_banks_are_not_summed_into_continuous_contact_evidence():
    r=layout();r.pop('strategy');r.pop('start_m')
    r['sections']=[dict(section_id='a',start_m=0.,length_m=200.,role='launch'),
                   dict(section_id='b',start_m=400.,length_m=200.,role='launch')]
    row=plan(requested_layout=r)['proposals'][0]
    assert row['screen']['stock']['installed_primary_length_m_per_direction']==400.
    assert row['screen']['maximum_contiguous_launch_bank_envelope_m']==200.
    assert row['screen']['necessary_screens']['ideal_powered_length']=='fail'
    assert row['screen']['physical_infeasibility_proven'] is False
