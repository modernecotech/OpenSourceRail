from copy import deepcopy
import pytest
from engineering.station_rail import braking,vehicle

@pytest.fixture(scope='module')
def car():return vehicle.build()

def test_rotating_material_is_inertia_not_extra_weight(car):
    r=braking.rotating_stock(car)
    assert r['equivalent_inertial_mass_kg_per_car']==pytest.approx(1770.386589,rel=1e-6)
    assert not r['static_axle_load_uses_equivalent_inertial_mass']
    assert .5*r['I_kg_m2_per_car']*(20/r['radius_m'])**2>350000

def test_lim_thrust_is_not_wheel_adhesion_limited(car):
    d=braking.definition(car)
    f=braking.force_state(d,23000,10,0.,rail_adhesion=.02,wayside_force_N=12000)
    assert f['valid']
    assert f['wayside_force_N']>f['rail_contact_limit_N_per_car']
    assert abs(f['rail_contact_force_N_per_car'])<f['rail_contact_limit_N_per_car']

def test_brake_torque_and_rail_force_remain_separate(car):
    d=braking.definition(car);f=braking.force_state(d,23000,20,10.,rail_adhesion=.05,grade_down_fraction=.02)
    assert f['valid'] and f['adhesion_limiter_active']
    mrot=d['rotors']['equivalent_inertial_mass_kg_per_car']
    assert f['rail_contact_force_N_per_car']==pytest.approx(-mrot*f['acceleration_m_s2']-f['torque_equivalent_brake_force_N_per_car'])
    assert f['disc_heat_rate_W_per_car']==f['torque_equivalent_brake_force_N_per_car']*20
    assert f['torque_equivalent_brake_force_N_per_car']>abs(f['rail_contact_force_N_per_car'])

def test_unmodelled_sliding_is_refused_and_failures_increase_stop_bound(car):
    d=braking.definition(car)
    assert not braking.force_state(d,23000,20,10.,rail_adhesion=.03,ideal_WSP=False)['valid']
    ok=braking.force_state(d,23000,20,10.,rail_adhesion=.15)
    lost=braking.force_state(d,23000,20,10.,rail_adhesion=.15,available_discs=4)
    assert ok['acceleration_m_s2']<lost['acceleration_m_s2']<0
    no=braking.force_state(d,23000,20,10.,rail_adhesion=.03,grade_down_fraction=.04)
    assert no['acceleration_m_s2']>0
    with pytest.raises(ValueError):braking.force_state(d,float('nan'),20,0)
