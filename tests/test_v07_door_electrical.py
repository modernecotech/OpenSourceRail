"""Door electrical counts are evidence of inventory, not circuit acceptance."""

from copy import deepcopy

import pytest

from engineering.station_rail.common import identity
from engineering.vehicle_parts import door_electrical as electrical
from tools.automation import v07_door_route as route


def test_selected_interface_is_counted_source_bound_and_held():
    result = electrical.evaluate()
    assert result['assessment_id'] == identity({
        key: value for key, value in result.items() if key != 'assessment_id'})
    assert result['physical_candidate_id'] == route.PHYSICAL_CHILD
    assert result['installed_candidate_id'] == route.INSTALLED_CHILD
    assert result['electrical_part_types_per_opening'] == 23
    assert result['electrical_pieces_per_opening'] == 249
    assert result['electrical_pieces_per_six_car_train'] == 2988
    assert result['electrical_parts_per_opening']['services/door-motor'] == 1
    assert result['electrical_parts_per_opening']['services/door-closed-switch'] == 2
    assert result['mechanical_release_parts_per_opening']['body/door-manual-isolator'] == 1
    assert result['electrical_isolator_count'] is None
    assert result['circuit_protection_device_count'] is None
    assert result['electrical_state_switch_for_manual_release_count'] is None
    assert result['interlock_logic_verified'] is False
    assert result['ready_for_native_electrical'] is False
    assert result['physical_accepted'] is False


def test_stock_allowance_never_becomes_installed_route():
    result = electrical.evaluate()
    assert result['stock_allowances']['services/door-body-loom'] == {
        'quantity_per_opening': 1, 'stock_length_each_m': 5,
        'installed_route_length_m': None}
    assert result['stock_allowances']['services/door-trailing-loom'] == {
        'quantity_per_opening': 2, 'stock_length_each_m': 2,
        'installed_route_length_m': None}
    assert result['supply_voltage_v'] is None
    assert result['emergency_energy_wh'] is None
    assert result['conductor_cross_sections_mm2'] is None


def test_counted_motor_change_refuses_to_inherit_screen(monkeypatch):
    actual = electrical._inputs

    def changed(root):
        handoff, request, raw, request_raw = actual(root)
        handoff = deepcopy(handoff)
        next(row for row in handoff['parts'] if row['part_id'] == 'services/door-motor')[
            'quantity_per_opening'] = 2
        return handoff, request, raw, request_raw

    monkeypatch.setattr(electrical, '_inputs', changed)
    with pytest.raises(ValueError, match='counts changed'):
        electrical.evaluate()


def test_stale_upstream_source_refused(monkeypatch):
    actual = electrical.digest

    def changed(path):
        if str(path).endswith('engineering/vehicle_parts/policy.json'):
            return '0' * 64
        return actual(path)

    monkeypatch.setattr(electrical, 'digest', changed)
    with pytest.raises(ValueError, match='child source changed'):
        electrical.evaluate()
