"""Whole-network counterexamples to shortest-winding-only selection."""
from pathlib import Path
import pytest
from engineering.comfort_design import system_tradeoff as t

MAIN=Path('/home/hayder/Documents/OpenSourceRail')
ROOT=MAIN if (MAIN/'cities/catalogue/west-asia/Iraq/Baghdad/engineering/maglev/summary.json').is_file() else Path(__file__).resolve().parents[3]


@pytest.fixture(scope='module')
def result():
    v=dict(candidate_id='a'*64,body_candidate_id='b'*64,magnet_component_id='c'*64,
        mass=dict(accounted_tare_kg_per_car=17356.683728076856,
                  accounted_cap_loaded_kg_per_car=20806.683728076856))
    return t.evaluate(v,ROOT)


def test_bounded_six_alternatives_do_not_rewrite_vehicle_or_claim_prices(result):
    assert len(result['proposals'])==6
    assert len({r['proposal_id'] for r in result['proposals']})==6
    assert result['candidate_id']=='a'*64
    assert result['budget']['native_runs']==0
    assert all(r['actual_price_USD'] is None and not r['physical_accepted'] for r in result['proposals'])


def test_20m_s_journey_and_800m_overlap_are_actual_ode_results(result):
    d=result['two_km_20m_s_800m_diagnostic']
    assert d['profile']['runtime_s']==pytest.approx(151.9296321678,abs=1e-6)
    assert d['station']['geometry_full_engagement']
    assert 780<d['station']['full_engagement_bound_m']<790
    assert d['station']['actual_force_current_voltage_thermal_envelope'] is None


def test_faster_longer_spacing_counts_new_sites_and_complete_winding(result):
    by={(r['launch_speed_m_s'],r['maximum_station_spacing_m']):r for r in result['proposals']}
    slow=by[(15.,2000.)];fast=by[(20.,3000.)]
    assert slow['total_trainsets']==1206 and slow['additional_line_stop_sites']==120
    assert fast['all_station_library_screens_pass']
    assert fast['total_trainsets']<slow['total_trainsets']
    assert fast['additional_line_stop_sites']<slow['additional_line_stop_sites']
    assert fast['total_direction_winding_m']>0
    assert fast['mainline_motor_coverage_fraction'] is not None
    assert fast['terminal_winding_and_civil_scope_complete'] is False


def test_unreachable_plans_never_get_a_free_zero_fleet_or_motor_coverage(result):
    bad=[r for r in result['proposals'] if not r['all_mainline_events_reachable']]
    assert bad
    for r in bad:
        assert r['total_trainsets'] is None
        assert r['total_direction_winding_m'] is None
        assert r['mainline_motor_coverage_fraction'] is None
        assert not r['station_library_quantities_complete']


def test_overlap_union_does_not_turn_overlap_into_free_installed_hardware():
    r=t.interval_union([(0,100),(50,150),(200,250)],0,250)
    assert r==dict(union_m=200.,overlap_pairs=1,overlap_m=50.)


def test_break_even_keeps_unknown_costs_and_hotel_power_as_parameters(result):
    assert result['capital_and_hotel_break_even']
    for r in result['capital_and_hotel_break_even']:
        assert r['actual_complete_cost_difference_USD'] is None
        assert not r['unknown_prices_are_zero']
        if r['additional_direction_winding_m']>0:
            ratio=r['saved_trainsets']/r['additional_direction_winding_m']
            assert r['train_only_break_even_USD_per_m_per_USD_unit_trainset_price']==pytest.approx(ratio)
    assert all(r['actual_hotel_kW_per_car'] is None for r in result['proposals'])
