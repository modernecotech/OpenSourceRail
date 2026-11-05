"""Retire an imposed station installation without changing reference body stock."""
from copy import deepcopy
from pathlib import Path
import tomllib

import pytest

from engineering.development_baseline import selection,propulsion_policy,system_cost
from engineering.station_rail import ROOT,operations,station_motor,propulsion_layout
from engineering.design_search import selected_reference_journey,wheel_motor


def test_baseline_selects_no_installed_drive_and_preserves_reference_vehicle_geometry():
    baseline=selection.load();p=baseline['active_propulsion_policy']
    assert baseline['vehicle']['candidate_id']=='756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3'
    assert baseline['selection_id']!='8e5905bc7c81d6177bbaafde81ab3a5f8cc54947c4923eb4493949566ac85cdc'
    assert baseline['selection']['family']=='wheel_rail_vehicle_reference'
    assert 'station_winding_library_m' not in baseline['selection']['service']
    for key in ('selected_installed_propulsion_id','selected_architecture','selected_powered_length_m',
                'selected_acceleration_m_s2','selected_braking_m_s2','selected_headway_s'):
        assert p[key] is None
    assert p['policy']['prescribed_powered_length'] is False
    assert p['policy']['reference_controls_are_requirements'] is False
    assert p['policy']['examples_are_exhaustive'] is False


def test_default_operational_controls_do_not_automatically_select_900_100_or_1000():
    v=selection.load()['vehicle'];r=operations.evaluate(v)
    assert r['selected_station'] is None and r['station_options']==[]
    assert r['reference_control_profile_is_installed_selection'] is False
    assert r['active_propulsion_policy']['selected_powered_length_m'] is None


@pytest.mark.parametrize('field,value',[('selected_powered_length_m',900),('selected_powered_length_m',100),
    ('default_powered_length_m',300),('prescribed_powered_length',True),('automatic_hardware_adoption',True),('prescribed_powered_length',0),('physical_qualification_required',1)])
def test_baseline_cannot_reintroduce_a_hidden_fixed_installation(field,value):
    config=tomllib.loads((Path(ROOT)/propulsion_policy.SELECTOR).read_text())
    config['propulsion_design'][field]=value
    with pytest.raises(ValueError):propulsion_policy.validate(config)


@pytest.mark.parametrize('a,distance',[(.4,500),(.6,1000/3),(.8,250),(1.,200),(1.5,400/3)])
def test_ideal_acceleration_distance_is_not_a_powered_hardware_selection(a,distance):
    p=operations.profile(2000,22000,speed_cap_m_s=20,acceleration_m_s2=a)
    assert p['launch_distance_m']==pytest.approx(distance)
    assert propulsion_policy.load()['selected_powered_length_m'] is None


def test_unit_primary_definitions_have_no_fixed_deployment_subtotal():
    for d in (station_motor.definition(),wheel_motor.definition(wheel_motor.default_parameters())):
        assert not any('900' in k for k in d)
        assert d['bare_primary_stock_kg_per_m']>0


def test_old_p1_cost_and_journey_cannot_be_implicit_active_selections():
    with pytest.raises(ValueError,match='Candidate-specific'):
        system_cost.evaluate({})
    with pytest.raises(ValueError,match='retired comparison'):
        selected_reference_journey.build()


def test_explicit_station_geometry_requires_explicit_service_and_same_vehicle():
    v=selection.load()['vehicle'];unit=station_motor.definition()
    layout=propulsion_layout.layout(candidate_id=v['candidate_id'],body_candidate_id=v['body_candidate_id'],
        passive_interface_id=v['propulsion_component_id'],sections=[dict(section_id='launch',role='launch',start_m=0.,length_m=203.)],
        module_length_m=12.5,magnetic_period_m=.5,module_policy='whole-modules',directions=2,
        independent_branches_per_direction=2,faces_per_track=2)
    with pytest.raises(ValueError,match='together'):operations.evaluate(v,station_layout=layout)
    params=dict(distance_m=2000.,speed_cap_m_s=20.,acceleration_m_s2=1.,service_deceleration_m_s2=.8,headway_s=180.,dwell_s=35.)
    result=operations.evaluate(v,service_parameters=params,station_layout=layout)
    assert result['selected_station']['length_m']==212.5
    assert result['selected_station']['quantity_evaluation']['actual_available_force_N'] is None
    assert result['selected_station']['geometry_full_engagement'] is None
