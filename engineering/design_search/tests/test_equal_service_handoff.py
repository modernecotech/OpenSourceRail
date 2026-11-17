import json
from math import isclose

import pytest

from engineering.design_search import equal_service_handoff as handoff


def _input():
    return json.loads((handoff.ROOT / 'docs/design-engine/v07-architecture-decision/input.json').read_bytes())


def test_published_screen_and_fourteen_scope_bridge_remain_source_bound():
    value = handoff.evaluate(_input())
    published = handoff.ROOT / 'docs/design-engine/v07-architecture-decision/result.json'
    assert published.read_bytes() == handoff.encoded(value)
    assert len(value['capital_14_scope_bridge']) == 14
    assert isclose(sum(r['line30_base_proxy_usd'] for r in value['capital_14_scope_bridge']),
                   value['line30_base_installed_capital_proxy_usd'], abs_tol=.01)
    assert value['candidate_priced_14_scope_installed_capital_usd'] is None
    assert all(r['installed_capital_usd'] is None for r in value['service_rows'])


def test_grade_and_fleet_maturity_stay_distinct():
    value = handoff.evaluate(_input())
    rows = {(r['architecture'], r['grade_magnitude']): r
            for r in value['service_rows']}
    assert rows['station-only', .01]['analytical_two_way_reach'] is False
    assert rows['station-plus-250m-booster', .02]['analytical_two_way_reach'] is False
    assert rows['powered-wheel-continuous-supply', .02]['analytical_two_way_reach'] is True
    assert rows['station-only', 0]['total_trainsets'] == 55
    assert rows['powered-wheel-continuous-supply', 0]['total_trainsets'] == 51
    assert rows['powered-wheel-continuous-supply', 0]['candidate_fleet_installed_delta_usd'] is None
    assert rows['powered-wheel-continuous-supply', 0]['unchanged_passive_delivered_fleet_quantity_proxy_delta_usd'] is None
    high = next(r for r in value['powered_wheel_mass_sensitivity']['rows']
                if r['grade_magnitude'] == .02 and r['direction'] == 'uphill')
    assert high['analytical_target_reached'] is True
    assert high['peak_required_mechanical_power_MW'] > 2.0
    assert value['powered_wheel_mass_sensitivity']['added_rotating_inertia_kg_per_car'] is None


def test_rejects_mixed_candidate_and_incomplete_capital_mapping():
    bad = _input()
    bad['parent_selected_vehicle_candidate_id'] = 'different'
    with pytest.raises(ValueError, match='identities differ'):
        handoff.evaluate(bad)
    bad = _input()
    bad['capital_scope_mapping'][0]['source_line_keys'].pop()
    with pytest.raises(ValueError, match='exactly once'):
        handoff.evaluate(bad)


def test_simple_span_is_an_unpriced_new_design():
    value = handoff.evaluate(_input())
    old, simple = value['civil_2km_alternatives']
    assert (old['piece_lifts'], simple['piece_lifts']) == (400, 400)
    assert (old['independent_supports'], simple['independent_supports']) == (202, 402)
    assert (old['structural_midspan_joints'], simple['structural_midspan_joints']) == (200, 0)
    assert simple['installed_cost_usd'] is None
    assert simple['temporary_tower_placements'] is None
