"""No-edit projection preserves exact exposure; changed service still scales."""
from copy import deepcopy
from math import ceil

from engineering.outline.revision_service import project
from engineering.station_rail.common import identity


def service():
    value=dict(requirements=dict(headway_s=200.,stations=6),round_trip_s=1589.,
        fleet_direction_multiplier=1,design=dict(reserve_fraction=.15,terminal_turnback_s=180.),
        normal_places_per_train=276,train_km_per_day=11067.485676279803,
        departures_per_day=7891.187835105297,berth_resource_s=120.,
        baseline_budget_positions_per_end=2,tail_clearance_s_jerk_bound=10.)
    value['evaluation_id']=identity(value)
    return value


def test_same_headway_preserves_actual_exposure_hex_exactly():
    original=service();before=deepcopy(original)
    # Actual Benguela values expose the former nonidentity arithmetic.
    for field in ('train_km_per_day','departures_per_day'):
        assert original[field]*200./200.!=original[field]
    result=project(original,dict(headway_s=200.,legs=[dict(braking_time_s=50.)]),{})
    assert original==before
    for field in ('train_km_per_day','departures_per_day'):
        assert result[field].hex()==original[field].hex()
    assert result['evaluation_id']==identity({k:v for k,v in result.items() if k!='evaluation_id'})


def test_changed_headway_retains_declared_exposure_and_fleet_scaling():
    original=service();result=project(original,dict(headway_s=250.,legs=[dict(braking_time_s=50.)]),{})
    for field in ('train_km_per_day','departures_per_day'):
        assert result[field]==original[field]*200./250.
    active=ceil(original['round_trip_s']/250.)
    assert result['active_trainsets']==active
    assert result['spare_trainsets']==ceil(active*.15)
    assert result['planning_usable_capacity_pphpd']==276*3600/250*.85*.99
