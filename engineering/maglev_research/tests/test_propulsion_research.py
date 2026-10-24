"""Negative controls for isolated propulsion electrical and thermal coupons."""
import copy
import json
import math

import pytest

from engineering.maglev_research import propulsion_research as p


def electrical(**changes):
    values = dict(resistance_ohm=.016, inductance_h=.000075, emf_v=42.)
    values.update(changes)
    return p.terminal_rl_coupon(**values)


def thermal(**changes):
    values = dict(current_a=1349., resistance_80c_ohm=.016362387456,
                  copper_mass_kg=297.271296, specific_heat_j_kg_k=385.,
                  alpha_per_k=.00393, pulse_s=5.)
    values.update(changes)
    return p.adiabatic_duty(**values)


def test_rl_midpoint_agrees_with_independent_closed_form_and_energy_identity():
    result = electrical()
    expected = 1349.*(1-math.exp(-.2/.01))
    assert math.isclose(result['on_end_current_a'], expected, abs_tol=1e-6)
    assert abs(result['energy_residual_j']) < 1e-7
    assert result['requested_waveform_unclipped']
    assert result['current_limit_pass']
    assert result['peak_current_a'] < 1350.
    assert result['configuration_adopted'] is False
    assert electrical(step_s=.00005)['final_current_a'] == pytest.approx(result['final_current_a'], rel=.0001)


def test_voltage_starvation_retains_failed_current_and_waveform_screens():
    result = electrical(voltage_limit_v=5.)
    assert result['voltage_limited_steps'] > 0
    assert not result['requested_waveform_unclipped']
    assert not result['current_limit_pass']
    assert abs(result['energy_residual_j']) < 1e-6


def test_energy_balance_cannot_justify_unresolved_voltage_clipped_rl_dynamics():
    # An unresolved midpoint step can double the physical -1000A steady-state
    # current in this fixture while still satisfying the energy identity.
    with pytest.raises(ValueError, match='electrical response'):
        electrical(inductance_h=1e-9, emf_v=21., voltage_limit_v=5.)


@pytest.mark.parametrize('changes', [dict(command_a=1400.), dict(step_s=.1),
    dict(on_s=100.), dict(emf_v=float('nan')), dict(inductance_h=0.), dict(command_a=True)])
def test_rl_rejects_invalid_or_unbounded_fixture(changes):
    with pytest.raises(ValueError):
        electrical(**changes)


def test_repeated_adiabatic_heat_uses_resistance_feedback_and_has_no_cooling_credit():
    result = thermal()
    capacity = 297.271296 * 385.
    coefficient = 1.5 * .016362387456 * 1349.**2 / (capacity * (1+60*.00393))
    expected = 20 + ((1+.00393*20)*math.exp(.00393*coefficient*200)-1)/.00393
    assert result['final_c'] == pytest.approx(expected)
    assert result['adiabatic_temperature_screen_pass']
    assert thermal(period_s=30.)['final_c'] == result['final_c']
    assert result['thermal_equilibrium_established'] is False
    assert thermal(current_a=0.)['final_c'] == 40.


def test_repeated_heat_stops_at_temperature_screen_instead_of_extrapolating():
    result = thermal(pulse_s=10.)
    assert not result['adiabatic_temperature_screen_pass']
    assert result['final_c'] == 120.
    assert result['evaluated_energised_s'] < result['requested_energised_s']
    with pytest.raises(ValueError):
        thermal(period_s=1.)


def test_two_meshes_and_positive_sampled_margins_never_imply_convergence():
    result = json.loads((p.ROOT/p.ARCHIVE/'executed/results.json').read_text())
    hypothesis = result['resolved_corner_alternative']['hypothesis_sha256']
    rows = p.mesh_diagnostics(result['rows'], hypothesis)
    assert [r['executed_meshes'] for r in rows] == [2, 2]
    assert all(r['all_sampled_material_screens_pass'] for r in rows)
    assert all(r['last_margin_change_a_m'] < 0 for r in rows)
    assert not any(r['independent_peak_convergence_established'] for r in rows)
    altered = copy.deepcopy(result['rows'])
    next(r for r in altered if r['id'] == 'resolved8mm-256-cold')['material_current_screen_pass'] = False
    assert not p.mesh_diagnostics(altered, hypothesis)[0]['all_sampled_material_screens_pass']


def test_source_bound_study_keeps_refused_requests_and_failed_duties():
    result = p.study()
    assert result['archive_verification']['executed_coupons'] == 21
    assert result['archive_verification']['unknown_refused_requests'] == 2
    assert result['transient_energy_balance_pass']
    assert result['search']['cases'] == 28
    variants = result['search']['variants']
    assert all(not row['system_eligible'] for row in variants)
    assert all(row['fixed_pose_force_n'] is None for row in variants if row['current_a'] >= 1350.)
    assert any(not row['adiabatic_duty']['adiabatic_temperature_screen_pass'] for row in variants)
    assert result['comparison']['maximum_grade_fraction_at_0_2_m_s2_with_inherited_resistance'] == pytest.approx(.00229756, rel=1e-6)
    assert not result['comparison']['changed_hypothesis_installed_mass_reconciled']
    assert result['physical_release'] is False
