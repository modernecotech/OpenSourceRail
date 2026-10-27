"""Matched identities, power accounting and negative protection fixtures."""
from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path

import pytest

from engineering.research_test_support import evidence_root
from engineering.comfort_design import ROOT
from engineering.comfort_design import interfaces as i, vehicle as vehicle_module, service as service_module

EVIDENCE_ROOT = evidence_root(Path(__file__).resolve().parents[3],
    required=('docs/design-engine/halbach-scaling/comparison.json',),
    sources=('engineering/comfort_design/interfaces.py',))


@pytest.fixture(scope='module')
def car():return vehicle_module.build(EVIDENCE_ROOT)


@pytest.fixture(scope='module')
def service(car):return service_module.evaluate(car,EVIDENCE_ROOT)


@pytest.fixture(scope='module')
def result(car,service):return i.evaluate(car,service,root=EVIDENCE_ROOT)


def test_same_candidate_and_no_installed_or_operating_acceptance(car,service,result):
    for key in ('candidate_id','body_candidate_id','magnet_component_id'):
        assert result[key]==service[key]==car[key]
    assert result['service_evaluation_id']==service['evaluation_id']
    assert result['same_candidate_inputs']['accounted_tare_kg_per_car']==pytest.approx(17356.683728076856)
    assert result['same_candidate_inputs']['retained_overcrowding_control_per_car']==160
    assert result['same_candidate_inputs']['local_magnetic_frame_reaction_hypothesis_N']==40000
    assert not result['complete_design_qualified'] and not result['installed_mass_complete']
    assert not result['complete_operating_train_established'] and not result['operating_release']


def test_exact_field_samples_do_not_become_a_hover_map(result):
    cases=result['support']['cases']
    cap=next(c for c in cases if c['passengers_total']==46 and c['unclosed_additional_mass_kg']==0)
    s=next(s for s in cap['samples'] if s['gap_m']==.028)
    assert s['contour_Fz_N']==[12515.567236579744,14550.488366164413]
    assert s['smaller_sampled_contour_1_3_margin_N']>0
    assert s['smaller_sampled_contour_1_3_margin_N']<s['vertical_contour_spread_N']
    assert s['fixed_gap_force_exceeds_mean_at_both_contours']
    assert not s['equilibrium_solved'] and not s['stable_hover_established']
    assert s['force_at_other_gap_or_current'] is None
    assert any(c['passengers_total']==160 and c['unclosed_additional_mass_kg']==2000 for c in cases)


def test_winding_heat_and_conductance_are_rms_not_zero_average(result):
    rows=result['winding']['repeated_duty_sensitivities']
    assert rows[2]['known_copper_loss_W_per_module']==pytest.approx(348.7681235592)
    assert rows[2]['known_copper_loss_W_per_module']/rows[0]['known_copper_loss_W_per_module']==pytest.approx(9)
    assert rows[2]['known_copper_loss_kW_per_car']==pytest.approx(8.37043496542)
    assert rows[2]['minimum_copper_to_50C_ambient_conductance_W_K_per_module']==pytest.approx(11.62560411864)
    assert result['winding']['actual_driver_voltage_V'] is None
    assert not result['winding']['actual_stable_hover_established']


def test_changed_roof_and_floor_are_in_thermal_model_without_headway_infiltration(result,service):
    rows=result['thermal']['cases'];selected=service['selected_scenario']
    expected_cycle=selected['profile']['runtime_s']+selected['inputs']['dwell_s']
    assert any(c['door_cycle_s']==expected_cycle for c in rows)
    assert all(c['door_cycle_s']!=120 for c in rows)
    assert all(not c['load']['door_recurrence_equals_line_headway'] for c in rows)
    c=rows[0]['load']['thermal_construction']
    assert c['roof_faces_m']==.0012 and c['roof_H60_core_m']==.045
    assert c['floor_faces_m']==.0009 and c['floor_H80_core_m']==.06
    assert c['new_rail_and_frame_bridge_UA_W_K'] is None
    assert result['thermal']['fresh_air_cabin_requirement_m3_h_46persons']==pytest.approx(993.6)
    assert all(r['actual_50C_normal_and_N_minus_1_screen']=='unknown' for r in rows)
    assert result['thermal']['package_reference']['actual_50C_electric_kWe'] is None


def test_hot_core_failure_requires_finish_evidence_not_free_coating(result):
    s=i.summary(result)
    assert s['roof_core_temperature_C_hypothesis']>70
    assert .30<s['maximum_roof_solar_absorptivity_for70C_core_hypothesis']<.40
    assert next(g for g in result['gates'] if g['name']=='roof-hot-core')['state']=='fail'
    construction=result['thermal']['cases'][0]['load']['thermal_construction']
    assert not construction['actual_aged_finish_absorptivity_and_coating_mass_known']
    assert construction['reflective_finish_design_target_solar_absorptivity_max']==.30


def test_shared_winding_routing_counts_and_actual_arrival_energy(result,service):
    r=result['station']['cases'][0];selected=service['selected_station'];profile=service['selected_scenario']['profile']
    assert r['station_id']==selected['station_id']
    assert r['shared_station_winding_length_m']==450
    assert r['sections_per_direction']==36
    assert r['two_direction_station_winding_subtotal_m']==900
    assert r['two_direction_motor_face_subtotal_m']==1800
    assert r['minimum_independent_train_current_phase_branch_sets_both_directions']==4
    assert r['logical_3phase_to_two_bank_routing_paths_both_directions']==432
    assert r['section_router_device_count_current_voltage_mass_and_cost'] is None
    assert r['receiving_entry_speed_m_s']<r['peak_speed_m_s']
    assert r['arrival_kinetic_energy_J']<r['launch_peak_kinetic_energy_J']
    assert r['receiving_mechanical_energy_kWh']==profile['theoretically_recoverable_mechanical_kWh_per_train']
    assert abs(r['launch_to_receiving_energy_residual_J'])<1e-7
    assert abs(r['coast_kinetic_balance_residual_J'])<1e-7
    assert r['dynamic_installed_motor_force_credit_N'] is None
    assert r['regenerative_energy_credit_kWh']==0


def test_charging_energy_needs_real_peak_power_and_charge_window(result):
    rows=result['station']['cases'][0]['hotel_charging']
    a=next(c for c in rows if c['HVAC_real_kWe_per_car_hypothesis']==40 and c['charge_window_s_hypothesis']==20)
    b=next(c for c in rows if c['HVAC_real_kWe_per_car_hypothesis']==40 and c['charge_window_s_hypothesis']==30)
    assert a['hotel_energy_kWh_train']==b['hotel_energy_kWh_train']
    assert a['input_charge_peak_kW']/b['input_charge_peak_kW']==pytest.approx(1.5)
    assert a['input_station_average_kW_direction']==b['input_station_average_kW_direction']
    assert a['input_charge_peak_kW']>a['input_station_average_kW_direction']
    assert all(not c['charge_window_fits_declared_dwell'] for c in rows if c['charge_window_s_hypothesis']==45)
    assert all(c['actual_complete_hotel_kWe_per_car'] is None for c in rows)


def test_civil_new_faces_supports_and_protection_surfaces_have_mass(result):
    c=result['civil']
    assert c['reference_concrete_top_z_m']==-1.60
    assert c['concrete_top_baseplate_bottom_z_m']==c['reference_concrete_top_z_m']
    assert c['crossmember_bottom_z_m']==c['concrete_top_baseplate_top_z_m']
    assert c['crossmember_bottom_z_m']-c['concrete_top_baseplate_bottom_z_m']==pytest.approx(.020)
    assert c['rail_centres_y_m']==[-.88,.88]
    assert c['overall_facing_envelope_width_m']==pytest.approx(2.26)
    assert c['facing_only_kg_per_span']==pytest.approx(6868.75)
    assert c['complete_counted_steel_stock_kg_per_span']==pytest.approx(sum(s['counted_mass_kg'] for s in c['stock']))
    assert c['complete_counted_steel_stock_kg_per_span']>3*c['facing_only_kg_per_span']
    assert c['anchors_per_span']==408
    assert c['brake_wear_surfaces']['inner_contact_abs_y_m']==.4355
    assert c['capture_caps']['top_z_m']==-.927
    assert c['installed_span_mass_kg'] is None and c['installed_cost_per_direction_km'] is None
    assert not c['old_61_9tonne_span_or_L_return_rail_cost_transferred']
    assert not c['magnetic_effect_of_steel_spreaders_risers_protection_strips_and_joints_included_in_field_maps']


def test_local_civil_failure_escalation_is_preserved(result):
    forty,seventy=result['civil']['local_member_fixtures']
    assert forty['local_module_force_hypothesis_N']==40000 and forty['necessary_member_screen']=='pass'
    assert seventy['local_module_force_hypothesis_N']==70000 and seventy['necessary_member_screen']=='fail'
    assert forty['combined_elastic_component_deflection_m']<.001<seventy['combined_elastic_component_deflection_m']
    assert not forty['force_bound_qualified'] and not seventy['force_bound_qualified']
    assert forty['actual_joint_weld_baseplate_anchor_capacity_N'] is None


def test_brakes_keep_unqualified_hardware_and_bad_friction_cases(result):
    p=result['protection'];r=p['brake_force_heat_sensitivities']
    assert p['retained_protection_subset_kg_per_car']==pytest.approx(345.1243056)
    assert not p['inherited_vehicle_mass_removed_or_credited_again']
    good=next(c for c in r if c['passengers_total']==46 and c['unclosed_extra_mass_kg']==0 and c['speed_m_s']==15 and c['active_pad_units']==3 and c['friction_coefficient_hypothesis']==.1 and c['downgrade_fraction_hypothesis']==0)
    bad=next(c for c in r if c['passengers_total']==46 and c['unclosed_extra_mass_kg']==0 and c['speed_m_s']==15 and c['active_pad_units']==3 and c['friction_coefficient_hypothesis']==.05 and c['downgrade_fraction_hypothesis']==0)
    assert good['necessary_force_screen']=='pass' and bad['necessary_force_screen']=='fail'
    assert good['single_stop_delta_C_per_pad']>0
    assert p['actual_guaranteed_onboard_deceleration_m_s2'] is None
    assert not p['release_actuation_requirement']['power_loss_applies_brake_by_verified_hardware']


def test_capture_known_linear_failure_and_new_unweighed_design_targets(result):
    rows=result['protection']['capture_energy_controls']
    assert all(c['linear_source_shoe_screen']=='fail' for c in rows)
    assert all(abs(c['linear_energy_residual_J'])<1e-8 for c in rows)
    crowd=next(c for c in rows if c['passengers_total']==160 and c['unclosed_extra_mass_kg']==2000)
    assert crowd['undamped_linear_energy_compression_m']>.008
    assert crowd['undamped_linear_peak_force_N_each']>50000
    targets={(t['shoes_proposed'],t['maximum_stroke_m_proposed']):t for t in crowd['redesign_targets']}
    assert targets[(12,.020)]['necessary_energy_force_stroke_screen']=='fail'
    assert targets[(16,.020)]['necessary_energy_force_stroke_screen']=='pass'
    assert .019<targets[(16,.020)]['required_compression_m']<.020
    assert all(t['new_hardware_mass_kg'] is None and not t['source8kg_shoe_mass_transferred'] for t in targets.values())
    assert next(g for g in result['gates'] if g['name']=='capture-energy')['state']=='fail'


def test_recovery_reach_and_contact_drag_are_not_an_offzone_restart(result):
    r=result['recovery']
    assert r['station_winch_retrieval_reach_m']==1000
    assert r['rope_length_including_tail_m']==1050
    assert r['rope_mass_kg']==pytest.approx(6468)
    assert r['old_nearest_node_half_spacing_reach_m']==500
    assert not r['old_nearest_node_reach_proves_tow_to_powered_station']
    assert r['force_cases'][0]['necessary_rope_screen']=='pass'
    assert all(c['necessary_rope_screen']=='fail' for c in r['force_cases'][1:])
    assert r['baseline_off_zone_restart']['action']=='hold'
    assert not r['normal120s_capacity_retained_during_recovery']
    assert any(c['pack_kWh_per_car_proposal']==30 and c['tow_speed_m_s_hypothesis']==.5 and c['necessary_energy_screen']=='fail' for c in r['essential_energy_cases'])
    assert any(c['pack_kWh_per_car_proposal']==50 and c['necessary_energy_screen']=='pass' for c in r['essential_energy_cases'])


def test_restart_requires_a_real_power_or_recovery_interface():
    base=dict(stationary=True,protected_path=True,brake_control_ready=True,support_healthy=True,
        at_powered_zone=False,power_confirmed=False)
    assert i.restart_permission(**base)['action']=='hold'
    assert i.restart_permission(**(base|dict(at_powered_zone=True,power_confirmed=True)))['action']=='conditional-powered-restart-procedure'
    tow=base|dict(rescue_asset_ready=True,coupling_inspected=True,tow_route_proved=True)
    assert i.restart_permission(**tow)['action']=='conditional-protected-tow-to-powered-berth'
    assert i.restart_permission(**(tow|dict(support_healthy=False)))['action']=='hold'
    assert not i.restart_permission(**(tow|dict(support_healthy=False,contact_support_qualified=True)))['physical_movement_authorized']
    with pytest.raises(ValueError):i.restart_permission(**(base|dict(stationary=1)))


def test_mixed_candidates_forged_mass_and_changed_results_are_rejected(car,service,result):
    wrong=deepcopy(service);wrong['body_candidate_id']='0'*64
    with pytest.raises(ValueError,match='another physical vehicle'):i.evaluate(car,wrong,root=EVIDENCE_ROOT)
    wrong=deepcopy(car);wrong['mass']['accounted_tare_kg_per_car']-=1000;wrong['mass']['accounted_cap_loaded_kg_per_car']-=1000
    wrong['evaluation_id']=i.identity({k:v for k,v in wrong.items() if k!='evaluation_id'})
    with pytest.raises(ValueError,match='inventory and accounted mass'):i.evaluate(wrong,service,root=EVIDENCE_ROOT)
    changed=deepcopy(result);changed['gates'][0]['state']='pass'
    with pytest.raises(ValueError,match='matched interface result'):i.validate(changed,car,service,root=EVIDENCE_ROOT)


def test_summary_dossier_svg_and_sources_remain_portable(result):
    s=i.summary(result);text=i.markdown(result);svg=i.render_section_svg(result)
    assert s['gate_states']['fail']==2
    assert s['candidate_id']==result['candidate_id']
    assert 'eight-shoe linear model fails' in text
    assert '35 mm-thick' in text and '38mm rope reference' in text
    assert '61.9 t beam' in text
    assert '<svg' in svg and '2.26 m' in svg and 'no physical release' in svg
    assert str(EVIDENCE_ROOT) not in json.dumps(result)
    assert all(not Path(name).is_absolute() for name in result['source_sha256'])
