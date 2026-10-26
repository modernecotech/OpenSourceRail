"""Equal service and unknown costs must not be replaced by optimistic defaults."""
from copy import deepcopy

import pytest

from engineering.design_search import whole_system as w


def test_comfort_capacity_and_required_shorter_interval():
    assert w.capacity(6,46,120)==8280
    assert w.capacity(6,80,120)==14400
    assert 6*46*3600/14400==69
    with pytest.raises(ValueError):w.capacity(6,46,0)


def test_station_resource_screen_uses_requested_interval():
    m=17356.683728076856+46*75
    assert w.choose_zone(2000.,20.,m,35.,60.,1000.) is None
    z=w.choose_zone(2000.,20.,m,35.,120.,1000.)
    assert z['length_m']==800
    assert z['minimum_nominal_resource_interval_s']<120
    assert w.choose_zone(2000.,20.,m,35.,120.,600.) is None


def test_unknown_prices_cannot_win_by_becoming_zero():
    row=dict(trainsets=10,direction_winding_m=1000,directional_mainline_length_m=2000)
    assert w.quoted_cost(row,{}) is None
    quotes=dict(trainset_USD=100,direction_winding_USD_per_m=2,guideway_USD_per_direction_m=3,
                other_station_CAPEX_USD=100,depot_CAPEX_USD=200,present_value_OPEX_renewals_USD=300)
    assert w.quoted_cost(row,quotes)==9600
    quotes['present_value_OPEX_renewals_USD']=None
    assert w.quoted_cost(row,quotes) is None


def test_no_coasting_survivor_inherits_an_ideal_continuous_drive():
    line=dict(line='test',stations=[dict(id='a',s_m=0),dict(id='b',s_m=10000)],
              duty=dict(arrival_events_per_circuit=[dict(terminal_loop_allowance=False,distance_m=10000,
                    origin_station='a',destination_station='b')]))
    row=w.line_result(line,20806.683728076856,15,120,1000)
    assert row['coast_failures']
    assert row['fleet'] is None and row['direction_winding_m'] is None
    assert row['continuous_traction_kinematic_fleet_lower_bound']['total']>0
    assert row['continuous_traction_actual_vehicle_mass_price_power_and_braking'] is None


def test_lower_bound_is_triangular_for_short_distance():
    assert w.continuous_traction_lower_bound(10)<w.continuous_traction_lower_bound(2000)
    with pytest.raises(ValueError):w.continuous_traction_lower_bound(-1)
