"""Service comparisons cannot inherit old mass, free cooling or capacity credit."""
from copy import deepcopy
import json

import pytest

from engineering.ferrite_maglev import station
from engineering.maglev_research import service_envelope as s


def test_charging_balances_live_services_disconnected_dwell_and_reserve():
    result = s.charging(runtime_s=190., dwell_s=30., charger_kw_per_car=600.)
    assert result['travel_and_disconnected_dwell_kwh_per_car'] == pytest.approx(60*(190+7.5)/3600)
    assert result['recharge_available_kwh_per_car'] == 3.
    assert not result['recharge_screen_pass']
    assert result['reserve_screen_pass']
    assert result['minimum_dwell_for_energy_s'] == pytest.approx(60*190/(.9*.75*600-60))
    assert s.charging(runtime_s=190., dwell_s=45., charger_kw_per_car=600.)['recharge_screen_pass']
    assert not s.charging(runtime_s=400., dwell_s=60., charger_kw_per_car=600.)['reserve_screen_pass']


@pytest.mark.parametrize('change', [dict(dwell_s=True), dict(connected_fraction=1.1),
    dict(runtime_s=float('nan')), dict(reserve_minutes=-1)])
def test_invalid_services_inputs_cannot_supply_a_screen(change):
    values = dict(runtime_s=190., dwell_s=45., charger_kw_per_car=600.)
    values.update(change)
    with pytest.raises(ValueError):
        s.charging(**values)


@pytest.fixture(scope='module')
def report():
    return s.study()


def test_formation_and_mass_are_counted_in_capacity_platform_and_full_tail(report):
    assumptions = report['assumptions']
    assert assumptions['baseline_aw2_passengers_per_train'] == 720
    assert assumptions['reference_aw2_throughput_floor_pph'] == 14400
    assert assumptions['aw3_mass_kg_per_car'] == pytest.approx(37618.59150033463)
    assert report['coverage']['service_variants'] >= 1000
    profiles = {row['id']:row for row in report['motion_profiles']}
    for row in report['service_variants']:
        profile = profiles[row['motion_profile_id']]
        assert row['train_length_m'] == row['cars']*17+(row['cars']-1)*.5
        assert row['aw3_train_mass_kg'] == pytest.approx(row['cars']*assumptions['aw3_mass_kg_per_car'])
        assert row['aw2_passengers_per_train'] == row['cars']*120
        assert row['conditional_capacity_aw2_pph'] == pytest.approx(row['cars']*120*3600/row['headway_lower_bound_s'])
        assert profile['full_tail_clear_front_m'] == profile['train_length_m']+profile['full_engagement_zone']['end_m']+75.
        assert row['headway_lower_bound_s'] == row['runtime_s']+row['dwell_s']+profile['full_tail_clear_after_departure_s']+5.
        assert not row['system_eligible']
        assert not row['configuration_adopted']


def test_longer_formations_do_not_get_free_platform_stator_charger_or_thermal_duty(report):
    rows = report['service_variants']
    assert not any(r['reference_throughput_floor_pass'] for r in rows if r['cars'] in (6,8))
    assert report['ranking']['least_formation_meeting_reference_floor'] == 10
    winner = report['recommended_research_specification']
    assert winner['cars'] == 12 and winner['station_spacing_m'] == 1500.
    assert winner['conditional_capacity_pph'] >= 14400.
    assert winner['peak_connected_charger_input_mw_train'] == 7.2
    assert winner['train_length_m'] == 209.5
    assert winner['reference_throughput_floor_met']
    assert not winner['group_40cycle_no_cooling_screen_pass']
    assert winner['research_target_only']
    assert winner['worst_group_minimum_mean_heat_rejection_w_k'] < winner['worst_group_mean_heat_rejection_at_120c_load_w_k']
    assert not report['ranking']['selection_is_total_cost_optimum']
    assert report['grade_necessary_force_screen']['existing_grade_case_force_screen_pass'] is False
    assert any('grade' in gate.lower() for gate in winner['failed_gates'])
    assert all(not r['uniform_current_group_duty']['thermal_equilibrium_established'] for r in report['motion_profiles'])
    assert all(r['uniform_current_group_duty']['worst_group_equivalent_1349a_pulse_s'] > 5 for r in report['motion_profiles'])


def test_local_copper_integrals_and_sampling_converge_without_force_density_credit(report):
    winner = report['recommended_research_specification']
    profile = next(row for row in report['motion_profiles'] if row['id'] == winner['motion_profile_id'])
    duty = profile['uniform_current_group_duty']
    assert duty['peak_allocated_current_a'] < 1349.
    assert duty['worst_group_equivalent_1349a_pulse_s'] == pytest.approx(duty['worst_group_i2t_a2_s']/1349.**2)
    assert max(duty['all_group_i2t_a2_s']) == duty['worst_group_i2t_a2_s']
    assert duty['total_copper_heat_at_80c_kwh_per_train_cycle'] == pytest.approx(1.5*.016362387456000008*sum(duty['all_group_i2t_a2_s'])/3.6e6)
    t = station.trajectory(distance_m=winner['station_spacing_m'], runtime_s=winner['runtime_s'],
        cars=winner['cars'], car_mass_kg=report['assumptions']['aw3_mass_kg_per_car'],
        acceleration=winner['acceleration_m_s2'], deceleration=.2,
        speed_limit_kmh=3.6*winner['max_speed_m_s'], record_trace=False)
    zone = s.full_engagement_zone(t, winner['train_length_m'])
    assert zone['length_m'] % 5 == 0
    assert zone['start_m'] <= -winner['train_length_m']-t['phases']['braking']['distance_m']
    assert zone['end_m'] >= t['phases']['launch']['distance_m']
    fine = s.group_duty(t, zone, mass_kg_per_car=report['assumptions']['aw3_mass_kg_per_car'],
        cars=winner['cars'], body_length_m=17., coupling_gap_m=.5, band_length_m=12.,
        force_per_a=report['assumptions']['force_coupon_n_per_car']/1349., reference_current_a=1349.,
        group_resistance_80c_ohm=.016362387456000008, group_copper_mass_kg=297.271296,
        copper_specific_heat=385., copper_alpha=.00393, step_s=.05)
    assert fine['worst_group_i2t_a2_s'] == pytest.approx(duty['worst_group_i2t_a2_s'], rel=.01)
    assert fine['total_copper_heat_at_80c_kwh_per_train_cycle'] == pytest.approx(duty['total_copper_heat_at_80c_kwh_per_train_cycle'], rel=.002)
    assert profile['trajectory']['peak_traction_force_n']/winner['cars'] <= report['assumptions']['force_coupon_n_per_car']


def test_invalid_mass_cannot_replace_source_bound_comparison():
    with pytest.raises(ValueError, match='AW3 comparison mass'):
        s.study(comparison_mass_kg=True)


def test_retained_report_rejects_source_subsets_mass_and_capacity_tamper(report, tmp_path):
    path = tmp_path/'service.json'
    path.write_text(json.dumps(report))
    assert s.read_retained(path)['recommended_research_specification']['cars'] == 12
    for change in ('source-subset', 'mass', 'capacity'):
        altered = deepcopy(report)
        if change == 'source-subset':
            altered['source_sha256'].pop(next(iter(altered['source_sha256'])))
        elif change == 'mass':
            altered['study_parameters']['comparison_mass_kg'] += 1
        else:
            altered['service_variants'][0]['conditional_capacity_aw2_pph'] += 1
        path.write_text(json.dumps(altered))
        with pytest.raises(ValueError):
            s.read_retained(path)
