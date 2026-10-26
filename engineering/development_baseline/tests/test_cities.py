"""The public current-city adapter exposes the v0.6 hold register."""
from engineering.development_baseline import cities as adapter
from engineering.station_rail import cities


def test_current_city_adapter_uses_explicit_wheelrail_hold_registry():
    assert adapter.evaluate_city is cities.evaluate_city
    assert adapter.publish_all is cities.publish_all
    assert cities.FAMILY == 'wheel_rail_station_lim'
    assert 'pending a validated station-drive envelope' in cities.HOLD
