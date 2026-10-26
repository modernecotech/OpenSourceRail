"""Independent necessary bounds for the physical-closure research adapters.

These checks use wheel energy, adhesion-limited body acceleration, and exact
rigid-body kinematics. They do not establish brake hardware or frame acceptance.
"""
from math import pi
import pytest
from engineering.station_rail import braking, vehicle


@pytest.fixture(scope='module')
def car():
    return vehicle.build()


def test_brake_work_removes_both_translation_and_counted_wheel_rotation(car):
    spec = braking.definition(car)
    mass = car['mass']['accounted_cap_loaded_kg_per_car']
    inertia_mass = spec['rotors']['equivalent_inertial_mass_kg_per_car']
    speed = 20.
    f = braking.force_state(spec, mass, speed, 100., rail_adhesion=1.)
    assert f['valid'] and not f['adhesion_limiter_active']
    # Independent uniform-pressure annular-pad moment: total force on BOTH
    # faces is 2*p*A. Applying another factor of two would fail this bound.
    mean_radius = (2./3.) * (.30**3 - .15**3) / (.30**2 - .15**2)
    torque = 8 * .35 * (2 * .6e6 * pi * .10**2 / 4) * mean_radius
    assert f['applied_brake_torque_Nm_per_car'] == pytest.approx(torque)
    stop_distance = speed**2 / (-2 * f['acceleration_m_s2'])
    brake_work = torque / .38 * stop_distance
    assert brake_work == pytest.approx(.5 * (mass + inertia_mass) * speed**2)
    assert brake_work > .5 * mass * speed**2


def test_ideal_adhesion_floor_acts_on_real_mass_not_inertial_equivalent(car):
    spec = braking.definition(car)
    for mass in (car['mass']['accounted_tare_kg_per_car'],
                 car['mass']['accounted_cap_loaded_kg_per_car'],
                 car['mass']['accounted_160_control_kg_per_car']):
        state = braking.force_state(spec, mass, 20., 100., rail_adhesion=.01)
        assert state['valid'] and state['adhesion_limiter_active']
        # On level track, adhesion-limited body deceleration is mu*g even
        # with rotating wheels; torque has to remove their additional energy.
        assert state['acceleration_m_s2'] == pytest.approx(-.01 * 9.80665)
        assert state['normal_load_N_per_car'] == pytest.approx(mass * 9.80665)
    no_adhesion = braking.force_state(spec, mass, 20., 100., rail_adhesion=0.)
    assert no_adhesion['valid']
    assert no_adhesion['applied_brake_torque_Nm_per_car'] == pytest.approx(0.)
    assert no_adhesion['acceleration_m_s2'] == pytest.approx(0.)


def test_section_contact_mpcs_preserve_all_six_rigid_body_modes(car):
    from engineering.station_rail import body_frame
    alternatives = body_frame.build(car)['variants']
    for alternative in alternatives:
        mesh = body_frame._mesh(alternative, .6)
        def component(node, dof, translation, rotation):
            if dof > 3:
                return rotation[dof - 4]
            x, y, z = mesh['nodes'][node]
            wx, wy, wz = rotation
            movement = (wy*z - wz*y, wz*x - wx*z, wx*y - wy*x)
            return translation[dof - 1] + movement[dof - 1]
        modes = [((1., 0., 0.), (0., 0., 0.)),
                 ((0., 1., 0.), (0., 0., 0.)),
                 ((0., 0., 1.), (0., 0., 0.)),
                 ((0., 0., 0.), (1., 0., 0.)),
                 ((0., 0., 0.), (0., 1., 0.)),
                 ((0., 0., 0.), (0., 0., 1.))]
        assert mesh['equations']
        for translation, rotation in modes:
            for equation in mesh['equations']:
                residual = sum(coefficient * component(node, dof, translation, rotation)
                               for node, dof, coefficient in equation)
                assert residual == pytest.approx(0., abs=1e-10)
