from copy import deepcopy

import pytest

from cities.Baghdad.airport_opening import opening_inputs
from cities.Baghdad.urban_opening import urban_comparison


@pytest.fixture(scope='module')
def inputs():
    cfg, report, _ = opening_inputs()
    return cfg, report


def test_urban_comparator_prices_standalone_corridors_at_identical_service(inputs):
    cfg, report = inputs
    result = urban_comparison(cfg, report)
    urban, airport = result['urban'], result['airport']
    assert result['group_name'] == 'Yellow'
    assert result['proxy_scores']['Yellow']['other_corridors'] == ['Airport', 'Blue', 'Green', 'Red', 'White']
    assert result['proxy_scores']['Yellow']['shared_named_stops']['Al Bayaa'] == ['Airport', 'Green', 'White']
    assert [row['route_km'] for row in (urban, airport)] == [30, 12]
    assert [row['station_count'] for row in (urban, airport)] == [8, 6]
    assert [row['grid_sites'] for row in (urban, airport)] == [6, 3]
    assert [row['active_sets'] for row in (urban, airport)] == [7, 3]
    for row in (urban, airport):
        assert row['fleet_sets'] == row['active_sets'] + 3
        assert row['hourly_departures_per_direction'] == [4] * 18
        assert row['normal_places_hour_direction'] == 2800
        assert row['annual_passenger_service_train_km'] == row['route_km'] * 144 * 365
        assert row['annual_empty_train_km_allowance'] == pytest.approx(.025 * row['annual_passenger_service_train_km'])
        assert row['capital_usd_m'] == pytest.approx(sum(row['common_capital_scopes_usd_m'].values()))
        assert row['annual_opex_usd_m'] == pytest.approx(sum(row['annual_opex_rows_usd_m'].values()))
        assert row['common_capital_scopes_usd_m']['Depot and control centre'] == (
            cfg['capital_rates_usd_m']['depot'] + cfg['capital_rates_usd_m']['control_centre'])
        assert row['observed_peak_directional_load'] is row['complete_opening_capital_usd_m'] is None
    assert urban['candidate_id'] != airport['candidate_id']
    assert urban['annual_opex_usd_m'] - airport['annual_opex_usd_m'] == pytest.approx(
        result['extra_paid_journeys_day_to_match_airport_operating_support'] * 365 * 637.5 / 1510 / 1e6)
    assert not result['rankable']


def test_urban_opening_rejects_unmatched_stop_patterns(inputs):
    cfg, report = inputs
    wrong = deepcopy(report)
    wrong['networks']['first']['groups']['Yellow']['outward_stops'][0]['id'] = 'Red-00'
    with pytest.raises(ValueError, match='named first-network routes'):
        urban_comparison(cfg, wrong)
