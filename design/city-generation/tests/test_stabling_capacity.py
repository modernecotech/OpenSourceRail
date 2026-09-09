import pytest

from osr_scenario.stabling_capacity import two_train_station_capacity


def fixture():
    return {'stations': [{'id': s} for s in ('a', 'b', 'unused')], 'fleets': [
        {'line': 'L1', 'trainset_count': 2, 'dispatch_points': [{'station': 'a'}, {'station': 'b'}]},
        {'line': 'L2', 'trainset_count': 2, 'dispatch_points': [{'station': 'a'}, {'station': 'b'}]},
    ]}


def test_shared_stations_are_not_counted_twice_for_different_lines():
    r = two_train_station_capacity(fixture(), [
        {'station': 'a', 'trainset_count': 2}, {'station': 'b', 'trainset_count': 2}])
    assert r['passed']
    assert r['selected_station_count'] == 2
    assert r['available_station_positions'] == 4


def test_a_spare_is_not_free_capacity_and_balanced_total_can_hide_local_overflow():
    r = two_train_station_capacity(fixture(), [
        {'station': 'a', 'trainset_count': 2, 'service_role': 'revenue'},
        {'station': 'a', 'trainset_count': 1, 'service_role': 'spare'},
        {'station': 'b', 'trainset_count': 1, 'service_role': 'revenue'}])
    assert r['inventory_excess_trainsets'] == 0
    assert r['over_capacity_station_count'] == r['excess_allocated_trainsets'] == 1
    assert not r['passed']


def test_missing_inventory_or_an_unselected_site_cannot_close_capacity():
    doc = fixture()
    r = two_train_station_capacity(doc, [{'station': 'a', 'trainset_count': 2}])
    assert not r['inventory_complete'] and not r['passed']
    r = two_train_station_capacity(doc, [
        {'station': 'a', 'trainset_count': 2}, {'station': 'unused', 'trainset_count': 2}])
    assert r['excess_allocated_trainsets'] == 2
    assert not r['passed']


def test_invalid_station_or_count_is_rejected():
    for station, count in [('unknown', 1), ('a', -1), ('a', 1.5), ('a', True)]:
        with pytest.raises(ValueError, match='invalid station allocation'):
            two_train_station_capacity(fixture(), [{'station': station, 'trainset_count': count}])


def test_depot_storage_does_not_consume_station_slots_at_same_site():
    doc = fixture()
    doc['fleets'][0]['trainset_count'] = 106
    rows = [{'station': 'a', 'trainset_count': 2}, {'station': 'b', 'trainset_count': 2},
            {'station': 'a', 'location_type': 'depot', 'trainset_count': 104}]
    result = two_train_station_capacity(doc, rows, depot_positions={'a': 104})
    assert result['passed'] and result['inventory_complete']
    assert result['station_allocated_trainsets'] == 4
    assert result['depot_allocated_trainsets'] == 104
    assert not two_train_station_capacity(doc, rows, depot_positions={'a': 103})['passed']
    with pytest.raises(ValueError, match='explicit stabling positions'):
        two_train_station_capacity(doc, rows)
