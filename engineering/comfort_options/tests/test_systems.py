"""Regression tests for payload accounting, evidence reuse and door heat topology."""
from copy import deepcopy
import importlib
import math
import os
from pathlib import Path

import pytest

from engineering.comfort_options import systems as s


EVIDENCE_ROOT = Path(os.environ.get('OSR_EVIDENCE_ROOT', s.ROOT))


@pytest.fixture(scope='module')
def parent():
    return s.parent_evidence(EVIDENCE_ROOT)


def test_exact_parent_inventory_and_three_separate_executed_samples(parent):
    old = parent['fitout']
    assert old['door']['physical_leaf_stock_mass_kg'] == pytest.approx(80.80384)
    assert old['door']['mechanism_reference_mass_kg'] == 164.
    assert old['glazing']['counted_material_mass_kg'] == pytest.approx(466.8656)
    assert old['material_plus_reference_subtotal_kg'] == pytest.approx(711.66944)
    assert parent['interior_allocation_kg'] == 800.
    assert parent['remaining_unlocated_allocation_kg'] == pytest.approx(5578.253763406856)
    by_gap = {r['gap_m']:r for r in parent['samples']}
    assert set(by_gap) == {.012,.028,.035338}
    assert by_gap[.028]['contour_Fz_N'] == [12515.567236579744,14550.488366164413]
    assert by_gap[.028]['vertical_contour_relative_difference'] == pytest.approx(.13985242820554794)
    assert all(not r['sampled_contours_are_confidence_bounds'] for r in by_gap.values())


def test_payload_reduction_changes_demand_without_inventing_new_force(parent):
    out = s.support_comparison(s.PARENT_TARE_KG, 80, parent['samples'])
    cases = {(r['passengers_total'],r['unclosed_additional_mass_kg']):r for r in out['cases']}
    assert set(p for p,extra in cases) == {0,80,100,120,160}
    small, crowded = cases[(80,0.)], cases[(160,0.)]
    assert crowded['accounted_loaded_kg_per_car']-small['accounted_loaded_kg_per_car'] == 6000.
    assert crowded['mean_weight_N_per_module']-small['mean_weight_N_per_module'] == pytest.approx(6000*s.G/24)
    for i in range(3):
        assert small['samples'][i]['contour_Fz_N'] == crowded['samples'][i]['contour_Fz_N']
        assert small['samples'][i]['force_at_other_gap_or_current'] is None
        assert small['samples'][i]['stable_hover_established'] is False
    assert out['cap_enforcement_qualified'] is False
    assert out['structural_and_credible_overcrowding_cases_reduced'] is False
    assert cases[(160,2000.)]['required_1_3_N_per_module'] == pytest.approx(16803.743030848927)


def test_lighter_vehicle_can_have_positive_force_error_without_stable_hover(parent):
    out = s.support_comparison(s.PARENT_TARE_KG, 54, parent['samples'])
    case = next(r for r in out['cases'] if r['passengers_total']==54 and r['unclosed_additional_mass_kg']==0)
    sample = next(r for r in case['samples'] if r['gap_m']==.012)
    assert min(sample['force_minus_mean_N_per_module']) > 0
    assert sample['fixed_gap_force_exceeds_mean_at_both_contours']
    assert not sample['stable_hover_established']
    assert not sample['equilibrium_solved']
    assert not sample['numerical_force_convergence_established']


@pytest.mark.parametrize('cap,headway,at180',[(54,81.,6480.),(80,120.,9600.),(100,150.,12000.),(120,180.,14400.)])
def test_equal_service_headway_and_capacity_use_total_hard_cap(cap,headway,at180):
    out=s.service_comparison(cap,2,accounted_tare_kg=17000.)
    assert out['required_headway_s_arithmetic']==headway
    assert out['at_180_s_pphpd']==at180
    assert out['frequency_ratio_to_180s']==pytest.approx(180/headway)
    assert out['safe_headway_s'] is None
    assert out['installed_fleet_count'] is None


def test_two_one_side_doors_preserve_normal_active_flow_and_extra_doors_are_hypotheses():
    two=s.service_comparison(80,2)
    three=s.service_comparison(80,3)
    assert two['baseline_active_doors_at_normal_platform']==2
    assert not two['normal_boarding_flow_halved']
    for a,b in zip(two['declared_exchange_hypotheses'],three['declared_exchange_hypotheses']):
        assert a['proposed_exchange_time_s']==a['baseline_two_active_doors_same_cap_exchange_time_s']
        assert b['proposed_exchange_time_s']==pytest.approx(a['proposed_exchange_time_s']*2/3)
        assert not a['dwell_qualified'] and not b['dwell_qualified']


def test_lower_cap_increases_accounted_mass_flow_at_equal_full_service():
    low=s.service_comparison(54,2,accounted_tare_kg=17000.)
    high=s.service_comparison(120,2,accounted_tare_kg=17000.)
    assert low['at_target_accounted_moving_tonnes_per_hour'] > high['at_target_accounted_moving_tonnes_per_hour']


def test_two_one_side_doors_do_not_halve_infiltration_or_fresh_air():
    base=s.thermal_load(passengers=80,doors_total=4,active_doors=2,solar_factor=.55,U_W_m2K=5.7)
    one=s.thermal_load(passengers=80,doors_total=2,active_doors=2,solar_factor=.55,U_W_m2K=5.7)
    assert one['door_average_outside_air_m3_s']==base['door_average_outside_air_m3_s']
    assert one['sensible_components_W']['doors_and_leakage']==base['sensible_components_W']['doors_and_leakage']
    assert one['fresh_air_cabin_m3_s']==base['fresh_air_cabin_m3_s']==.48
    assert one['scenario']['door_cycle_s']==180.
    assert one['door_recurrence_is_train_headway'] is False
    assert one['opaque_door_topology_correction_W']<0
    assert one['sensible_components_W']['glass_solar']==pytest.approx(26*.55*600.)
    assert one['HVAC_electric_scenario_kWe'] is None


def test_three_and_four_active_doors_increase_declared_infiltration():
    a=s.thermal_load(passengers=80,doors_total=3,active_doors=3,solar_factor=.55,U_W_m2K=5.7,humid=True)
    b=s.thermal_load(passengers=80,doors_total=4,active_doors=4,solar_factor=.55,U_W_m2K=5.7,humid=True)
    assert b['door_average_outside_air_m3_s']==pytest.approx(a['door_average_outside_air_m3_s']*4/3)
    assert a['scenario']['door_open_s']==60.
    assert a['scenario']['outdoor_RH']==.30
    for row in (a,b):
        assert row['total_kWthermal']==pytest.approx(row['sensible_kWthermal']+row['latent_kWthermal'])


def test_lower_passenger_count_keeps_per_person_ventilation_and_air_quality_assumptions():
    common=dict(doors_total=2,active_doors=2,solar_factor=.75,U_W_m2K=5.7,humid=True)
    low=s.thermal_load(passengers=80,**common)
    full=s.thermal_load(passengers=160,**common)
    assert low['fresh_air_cabin_m3_s']==full['fresh_air_cabin_m3_s']/2
    assert low['scenario']['fresh_air_L_s_per_person']==full['scenario']['fresh_air_L_s_per_person']==6.
    assert low['co2_steady_mechanical_only_ppm']==full['co2_steady_mechanical_only_ppm']
    assert low['latent_components_W']['occupants']==4400.
    assert low['actual_hot_condition_electrical_input_kWe'] is None
    assert low['actual_glazing_properties_verified'] is False


def test_four_package_quantity_and_n_minus_one_do_not_become_50C_ratings():
    rows=s.cooling_comparison(100.,installed_units=5)
    four=next(r for r in rows if r['units_proposed']==4 and r['failed_units']==0)
    four_failed=next(r for r in rows if r['units_proposed']==4 and r['failed_units']==1)
    assert four['hardware_supplier_reference_kg']==768.
    assert four['available_nameplate_kWthermal']==132.
    assert four_failed['available_nameplate_kWthermal']==99.
    assert four_failed['necessary_nameplate_screen']=='nominal-insufficient'
    assert four['actual_50C_capacity_kWthermal'] is None
    assert four['same_as_evaluated_candidate'] is False
    assert all(r['actual_50C_input_kWe'] is None for r in rows)


@pytest.mark.parametrize('bad',[0,1,-1,161,True,54.5,float('nan')])
def test_invalid_or_boolean_cap_is_rejected(bad):
    with pytest.raises(ValueError):s.service_comparison(bad,2)


def test_parent_digest_guard_rejects_any_edited_packet(tmp_path):
    with pytest.raises(ValueError,match='retained source differs'):
        s.parent_evidence(tmp_path)


def test_explicit_layout_glazing_composition_and_no_double_seating_credit(parent):
    # These two specialist modules are independently developed in this round.
    layouts=pytest.importorskip('engineering.comfort_options.layout')
    glazing=pytest.importorskip('engineering.comfort_options.glazing')
    layout=next(r for r in layouts.family(root=EVIDENCE_ROOT) if r['doors_total']==2)
    glass=glazing.options(doors_total=2)[0]
    out=s.evaluate(layout,glass,root=EVIDENCE_ROOT)
    m=out['mass']
    removed=sum(m['removed'].values())
    added=sum(m['added'].values())
    assert removed==pytest.approx(711.66944)
    assert m['net_accounting_change_kg_per_car']==pytest.approx(added-removed+m['additional_seat_stock_above_retained_budget_kg'])
    assert m['interior_allowance_saving_claimed_kg']==0.
    assert m['identified_seat_stock_within_interior_kg']+m['retained_unidentified_interior_budget_kg']==800.
    assert m['actual_installed_tare_kg_per_car'] is None
    assert not m['old_ancestor_500kg_door_and_500kg_glazing_allocations_removed_again']
    assert not m['door_leaf_glazing_counted']
    assert s.validate(out,layout,glass,root=EVIDENCE_ROOT)
    edited=deepcopy(out);edited['stable_hover_established']=True
    with pytest.raises(ValueError,match='payload or identity differs'):
        s.validate(edited,layout,glass,root=EVIDENCE_ROOT)
    four=s.evaluate(layout,glass,root=EVIDENCE_ROOT,hvac_units=4)
    assert four['candidate_id']!=out['candidate_id']
    assert four['mass']['accounted_tare_kg_per_car']==pytest.approx(m['accounted_tare_kg_per_car']-192.)
