from copy import deepcopy
import pytest
from engineering.railway_closure import service,electrical


def test_impossible_terminal_maneuver_cannot_complete_plan():
    p=service.brief();p['turnaround_maneuver_s']=1.
    r=service.plan('a'*64,{'A':180.,'B':180.},p,headway_s=210.,phase_b_s=90.,active_trainsets=4)
    assert r['tests']['necessary_terminal_maneuver_time'] is False
    assert r['planned_service_complete'] is False


def test_counted_fleet_and_departure_phase_change_service_feasibility():
    p=service.brief();times={'A':171.68,'B':171.68}
    sync=service.plan('a'*64,times,p,headway_s=200,phase_b_s=0,active_trainsets=3)
    phased=service.plan('a'*64,times,p,headway_s=200,phase_b_s=60,active_trainsets=3)
    assert not sync['planned_service_complete'] and phased['planned_service_complete']
    assert all(x['train_id'] in {t['id'] for t in phased['counted_initial_trains']} for x in phased['departures'])
    assert phased['total_trainsets']==4
    assert not phased['native_force_driven_fleet_replayed'] and not phased['protected_service_qualified']


def test_demand_is_an_obligation_not_a_preferred_headway():
    p=service.brief();times={'A':171.68,'B':171.68}
    slow=service.plan('a'*64,times,p,headway_s=240,phase_b_s=0,active_trainsets=4)
    flexible=service.plan('a'*64,times,p,headway_s=210,phase_b_s=55,active_trainsets=3)
    assert not slow['tests']['demand'] and not slow['planned_service_complete']
    assert flexible['planning_capacity_pphpd']==pytest.approx(4021.714285714286)
    assert flexible['planned_service_complete']


def test_slow_physics_cannot_be_fixed_by_unpriced_trains():
    r=service.plan('a'*64,{'A':230.,'B':230.},service.brief(),headway_s=200,phase_b_s=60,active_trainsets=3)
    assert not r['planned_service_complete']
    assert not r['tests']['journey_time']
    assert len(r['counted_initial_trains'])==3


def test_station_rail_quantities_include_platform_pockets_and_crossovers():
    r=service.terminal_geometry(service.brief())
    q=r['track_quantities']
    assert q['total_track_m']>2*1500
    assert q['total_track_m']==pytest.approx(sum(q[k] for k in ('main_and_platform_track_m','pocket_track_m','crossover_track_m')))
    assert r['nominal_end_margin_m']>2
    assert not r['geometry_verified']


@pytest.mark.parametrize('value',[float('nan'),-1,0])
def test_invalid_headway_rejected(value):
    with pytest.raises(ValueError):service.plan('a'*64,{'A':170.,'B':170.},service.brief(),headway_s=value,phase_b_s=0,active_trainsets=3)


def test_two_type3_strings_narrowly_fail_unchanged_worst_mission():
    r=electrical.battery('Type3-20',2)
    assert r['nominal_pack_energy_kwh']==55.2
    assert r['missions']['hot']['reserve_margin_kwh']==pytest.approx(-.010355555555554,abs=1e-8)
    assert not r['internal_energy_screen']
    assert not r['thermal']['catalogue_direct_ambient_screen']


def test_high_heat_two_string_alternative_is_a_distinct_bounded_design():
    r=electrical.battery('Type4-23',2)
    assert r['nominal_pack_energy_kwh']==62.1
    assert r['module_mass_kg_per_car']==825.
    assert r['internal_energy_screen'] and r['conditioned_thermal_screen']
    assert r['thermal']['catalogue_direct_ambient_screen']
    assert not r['manufacturer_hot_current_curve_received'] and not r['physical_accepted']
    assert r['pack_voltage_range_V']==[450.,810.]


def test_emergency_energy_is_not_assumed_traction_battery_energy():
    r=electrical.battery('Type3-20',3)
    assert r['modules_per_six_car_train']==450
    assert r['internal_energy_screen']
    assert 'No battery propulsion assumed' in r['scope']
    assert not r['physical_accepted']


def test_piecewise_rc_matches_analytic_constant_heat_and_conserves_energy():
    r=electrical.repeated_thermal([dict(duration_s=100.,heat_W=1000.)],initial_C=30.,ambient_C=30.,capacity_J_K=10000.,rejection_W_K=0.)
    assert r['final_C']==40.
    assert r['input_heat_J']==100000.
    assert abs(r['balance_residual_J'])<1e-8
    assert not r['physical_accepted']
