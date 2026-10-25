"""Independent sign, stability, domain and energy benchmarks on synthetic maps."""
from copy import deepcopy
from itertools import product
import math

import pytest

from engineering.passive_suspension import controls


def field_map():
    axes = dict(gap_m=[.008, .010, .012], lateral_m=[-.002, 0., .002],
                current_A=[-20., 0., 20.], temperature_C=[20., 80.])
    rows = []
    for gap, lateral, current, temperature in product(*axes.values()):
        rows.append(dict(gap_m=gap, lateral_m=lateral, current_A=current, temperature_C=temperature,
                         F_z_N=1000.-100000.*(gap-.010)+50.*current-300.*(temperature-20.)/60.-2e6*lateral*lateral,
                         F_y_N=-20000.*lateral, dF_z_dgap_N_per_m=-100000., dF_z_dcurrent_N_per_A=50.,
                         dF_y_dlateral_N_per_m=-20000., dflux_dgap_Wb_turn_per_m={'lift': -50.},
                         dflux_dlateral_Wb_turn_per_m={'lift': 0.}, L_H={'lift': .01}, R_ohm={'lift': .2},
                         numerical_status='converged'))
    return dict(map_id='synthetic-analytic-benchmark', unit_scope='one synthetic supported lump; not a vehicle',
                control_circuit_id='lift', axes=axes, rows=rows, interpolation_usable=True,
                numerical_status='converged', physical_accepted=False)


def scenario(**updates):
    value = dict(mass_kg=100., load_N=1000., equilibrium_gap_m=.010,
                 lateral_m=0., temperature_C=20., equilibrium_current_A=0.,
                 proportional_A_per_m=5000., derivative_A_s_per_m=200., current_loop_gain_ohm=10.,
                 current_limit_A=20., voltage_limit_V=24., initial_displacement_m=.0001,
                 duration_s=.1, dt_s=.00005)
    return value | updates


def test_zero_current_load_balance_is_actively_unstable_and_load_temperature_dependent():
    data = field_map()
    result = controls.zero_current_equilibria(data, 1000., temperature_C=20., tolerance_m=.001)
    equilibrium = result['equilibria'][0]
    assert equilibrium['gap_m'] == pytest.approx(.010)
    assert equilibrium['attractive_gap_mode_unstable'] is True
    assert equilibrium['active_stabilisation_required'] is True
    assert equilibrium['open_loop_gap_growth_rate_per_s'] > 0
    assert equilibrium['tolerance_current_balance_available'] is True
    assert max(abs(current) for corner in equilibrium['tolerance_corners'] for current in corner['current_balance_roots_A']) > 1
    assert controls.zero_current_equilibria(data, 1100., temperature_C=20.)['equilibria'][0]['gap_m'] == pytest.approx(.009)
    assert controls.zero_current_equilibria(data, 1000., temperature_C=80.)['status'] == 'no-zero-current-equilibrium'
    assert controls.zero_current_equilibria(data, 1000., temperature_C=120.)['status'] == 'held-field-map'
    assert result['physical_accepted'] is False


def test_tolerance_domain_is_not_clipped_into_the_map():
    result = controls.zero_current_equilibria(field_map(), 1200., temperature_C=20., tolerance_m=.001)
    equilibrium = result['equilibria'][0]
    assert equilibrium['gap_m'] == .008
    assert not equilibrium['tolerance_current_balance_available']
    assert any(not corner['within_map'] for corner in equilibrium['tolerance_corners'])


@pytest.mark.parametrize('mutate', [
    lambda data: data.update(interpolation_usable=False),
    lambda data: data.update(numerical_status='nonconverged'),
    lambda data: data.update(unit_scope=None),
    lambda data: data['rows'].pop(),
    lambda data: data['rows'].__setitem__(0, data['rows'][1]),
    lambda data: data['rows'][0].update(numerical_status='failed'),
    lambda data: data['rows'][0].update(interpolation_usable=False),
])
def test_unusable_incomplete_or_ambiguous_maps_are_held(mutate):
    data = field_map();mutate(data)
    assert controls.zero_current_equilibria(data, 1000., temperature_C=20.)['status'] == 'held-field-map'


def test_field_map_linear_interpolation_has_no_extrapolation_and_preserves_unknowns():
    data = field_map();data['rows'][2]['R_ohm'] = None
    grid = controls.FieldMap(data)
    point = grid.sample(gap_m=.009, lateral_m=-.001, current_A=10., temperature_C=50.)
    # Lateral dependence is piecewise linear through retained samples, not the
    # unobserved exact quadratic used to construct this synthetic benchmark.
    assert point['F_z_N'] == pytest.approx(1446.)
    assert point['R_ohm'] is None
    with pytest.raises(controls.MapUnavailable, match='out-of-map'):
        grid.sample(gap_m=.007, lateral_m=0., current_A=0., temperature_C=20.)


def test_map_quantity_snapshot_cannot_change_after_admission():
    data = field_map();grid = controls.FieldMap(data)
    digest = grid.quantity_digest
    data['rows'][0]['F_z_N'] = -1e30
    data['map_id'] = 'changed-input'
    assert grid.data['map_id'] == 'synthetic-analytic-benchmark'
    assert grid.quantity_digest == digest
    assert grid.sample(gap_m=.008, lateral_m=-.002, current_A=-20., temperature_C=20.)['F_z_N'] == 192.


def test_cross_coupled_gap_lateral_modes_keep_attractive_unstable_mode_visible():
    point = dict(dF_z_dgap_N_per_m=-100., dF_z_dlateral_N_per_m=10.,
                 dF_y_dgap_N_per_m=-10., dF_y_dlateral_N_per_m=-200.)
    modes = controls.local_force_modes(point, mass_kg=10.)
    assert modes['force_jacobian_N_per_m'] == [[100., -10.], [-10., -200.]]
    assert modes['exponentially_unstable'] is True
    assert any(value['real'] > 0 for value in modes['modes_per_s'])
    assert modes['asymptotically_stable'] is False


def test_finite_current_bandwidth_can_invalidate_ideal_pd_stability():
    grid = controls.FieldMap(field_map())
    p = grid.sample(gap_m=.010, lateral_m=0., current_A=0., temperature_C=20.)
    slow = controls.local_gap_model(p, mass_kg=100., proportional_A_per_m=5000., derivative_A_s_per_m=200.)
    fast = controls.local_gap_model(p, mass_kg=100., proportional_A_per_m=5000., derivative_A_s_per_m=200., current_loop_gain_ohm=10.)
    assert slow['ideal_current_closed_stiffness_N_per_m'] > 0
    assert slow['ideal_current_closed_damping_N_s_per_m'] > 0
    assert slow['hurwitz_strict'] is False
    assert fast['hurwitz_strict'] is True
    assert controls.simulate_gap(field_map(), scenario(current_loop_gain_ohm=0.))['reason'] == 'finite-bandwidth local model is unstable'


def test_nonlinear_rl_response_stabilises_only_within_declared_domain_and_authority():
    result = controls.simulate_gap(field_map(), scenario())
    assert result['status'] == 'completed-local-scenario'
    assert abs(result['records'][-1]['gap_m']-.010) < .0001
    assert result['current_rms_A'] > 0
    assert result['winding_copper_loss_W'] == pytest.approx(.2*result['current_rms_A']**2)
    assert result['total_loss_W'] is None
    assert result['unknown_loss_terms'] == ['driver_loss_W', 'sensor_loss_W', 'other_loss_W']
    assert result['physical_accepted'] is False
    assert result['map_quantity_sha256'] == controls.FieldMap(field_map()).quantity_digest


@pytest.mark.parametrize('updates,reason', [
    (dict(current_limit_A=.1), 'current-command-clamped'),
    (dict(voltage_limit_V=.1), 'voltage-command-clamped'),
    (dict(initial_displacement_m=.003), 'out-of-map gap_m'),
    (dict(dt_s=.001), 'time step exceeds declared electrical resolution'),
    (dict(load_N=999.), 'requested linearisation is not a force equilibrium'),
])
def test_clamps_domain_and_linearisation_fail_closed(updates, reason):
    result = controls.simulate_gap(field_map(), scenario(**updates))
    assert result['status'] == 'held-local-model'
    assert result['reason'] == reason
    assert result['clamp_or_domain_failure'] is True
    assert result['current_rms_A'] is None


def test_missing_winding_electrical_quantity_has_no_rl_or_heat_credit():
    data = field_map()
    for row in data['rows']:row['L_H'] = None
    result = controls.simulate_gap(data, scenario())
    assert result['status'] == 'held-local-model'
    assert 'unknown L_H' in result['reason']
    assert result['winding_copper_loss_W'] is None


def test_zero_average_current_has_nonzero_rms_and_does_not_remove_heat():
    result = controls.current_loss_statistics([10., -10.], [.2, .4], weights_s=[1., 1.])
    assert result['current_mean_A'] == 0
    assert result['current_rms_A'] == 10
    assert result['winding_copper_loss_W'] == pytest.approx(30.)
    assert result['winding_copper_energy_J'] == pytest.approx(60.)
    assert result['total_installed_loss_W'] is None
    assert result['cooling_eliminated'] is False


def circuit(gradient, **updates):
    return dict(id='test-coil', flux_gradient_Wb_turn_per_m=gradient, L_H=.1,
                R_coil_ohm=1., R_load_ohm=1.) | updates


def test_resistor_shunt_frequency_rolloff_heat_split_and_static_force():
    result = controls.shunt_response([circuit([10.])], [0., 10., 100.], velocity_rms_m_s=[.1])
    low, middle, high = result['frequency_rows']
    assert low['damping_matrix_N_s_per_m'][0][0] == 50.
    assert low['absorbed_mechanical_power_W'] == pytest.approx(.5)
    assert low['coil_heat_W'] == low['resistor_heat_W'] == pytest.approx(.25)
    assert high['damping_matrix_N_s_per_m'][0][0] < middle['damping_matrix_N_s_per_m'][0][0] < 50.
    assert max(abs(row['energy_balance_residual_W']) for row in result['frequency_rows']) < 1e-12
    assert result['static_shunt_force_N'] == [0.]
    assert result['static_stiffness_N_per_m'] == [[0.]]
    assert result['static_attractive_instability_removed'] is False


def test_mimo_unobserved_mode_and_signed_series_cancellation():
    result = controls.shunt_response([circuit([1., 1.]), circuit([-1., -1.])], [1.], velocity_rms_m_s=[1., -1.])
    assert result['gradient_rank'] == 1
    assert result['frequency_rows'][0]['absorbed_mechanical_power_W'] == 0.
    independent = controls.shunt_response([circuit([1.]), circuit([-1.])], [1.], velocity_rms_m_s=[1.])
    series = controls.shunt_response([circuit(None, series_member_gradients_Wb_turn_per_m=[[1.], [-1.]])], [1.], velocity_rms_m_s=[1.])
    assert independent['frequency_rows'][0]['absorbed_mechanical_power_W'] > 0
    assert series['gradient_rank'] == 0
    assert series['signed_series_cancellation'] == ['test-coil']
    assert series['frequency_rows'][0]['absorbed_mechanical_power_W'] == 0.


def test_shunt_rejects_negative_resistance_and_preserves_missing_gradient():
    with pytest.raises(ValueError):controls.shunt_response([circuit([1.], R_load_ohm=-1.)], [1.])
    assert controls.shunt_response([circuit(None)], [1.])['status'] == 'held-shunt-data'


def test_reciprocal_rl_shunt_removes_mechanical_energy_with_balanced_heat():
    result = controls.simulate_shunt_decay(mass_kg=1., stiffness_N_per_m=100., damping_N_s_per_m=0.,
        flux_gradient_Wb_turn_per_m=5., L_H=.1, R_coil_ohm=1., R_load_ohm=4.,
        displacement_m=.01, duration_s=5., dt_s=.001)
    assert result['final_energy_J'] < .01*result['initial_energy_J']
    assert result['coil_heat_J'] > 0
    assert result['resistor_heat_J'] == pytest.approx(4*result['coil_heat_J'])
    assert abs(result['energy_balance_residual_J']) < 1e-8
    assert result['maximum_step_energy_increase_J'] < 1e-12
    assert result['passive_levitation_established'] is False


def test_stationary_cooling_scenario_counts_internal_conduction_and_unknowns():
    args = dict(ambient_C=40., maximum_coil_C=80., area_m2=2., convection_W_m2K=10., emissivity=0., coil_to_surface_K_per_W=.1)
    result = controls.passive_cooling_scenario(300., **args)
    assert result['maximum_rejection_W'] == pytest.approx(40/(1/20+.1))
    assert result['necessary_screen_pass'] is False
    assert result['cooling_eliminated'] is False
    assert controls.passive_cooling_scenario(100., **(args | dict(coil_to_surface_K_per_W=None)))['status'] == 'unknown-cooling-inputs'
    assert controls.passive_cooling_scenario(1., **(args | dict(convection_W_m2K=0.)))['maximum_rejection_W'] == 0.


def test_gravity_assistance_is_route_energy_not_support_power_or_free_return():
    result = controls.gravity_assistance_scenario(1000., vertical_drop_m=5., distance_m=500., target_speed_m_s=10.)
    assert result['potential_energy_J'] == pytest.approx(49033.25)
    assert result['ideal_no_resistance_speed_m_s'] == pytest.approx(math.sqrt(98.0665))
    assert result['energy_margin_J'] is None
    assert result['reverse_climb_energy_before_losses_J'] == result['potential_energy_J']
    assert result['independent_support_energy_credit_J'] == 0.
    assert result['route_adopted'] is False


def test_sign_or_circuit_inventory_mismatch_cannot_silently_gain_damping():
    with pytest.raises(ValueError, match='signed series gradient'):
        controls.shunt_response([circuit([2.], series_member_gradients_Wb_turn_per_m=[[1.], [-1.]])], [1.])
    with pytest.raises(ValueError, match='dimension'):
        controls.shunt_response([circuit([1., 2.]), circuit([1.])], [1.])


def test_actual_spatial_field_map_enters_controls_and_unchecked_map_is_held():
    """True FEM/RL integration on a small PM/passive-facing laboratory coupon.

    This fixture tests numerical interfaces; its geometry is not a train design.
    No monkeypatched forces, derivatives, convergence or electrical constants.
    """
    from engineering.passive_suspension import fields

    geometry = dict(length_x_m=.25, reference_gap_m=.03, regions=[
        dict(id='pm', material='ferrite', group='train', bounds_yz_m=[-.05, .05, -.09, -.03], Br_z_T=.45),
        dict(id='facing', material='steel', group='guideway', bounds_yz_m=[-.18, .18, 0., .04]),
        dict(id='cw+', material='copper', group='train', bounds_yz_m=[-.08, -.06, -.08, -.04], turns_per_m2=100000., circuit_id='lift'),
        dict(id='cw-', material='copper', group='train', bounds_yz_m=[.06, .08, -.08, -.04], turns_per_m2=-100000., circuit_id='lift')],
        circuits={'lift': dict(resistance_20c_ohm=.2)})
    axes = dict(gaps_m=[.028, .032], laterals_m=[0.], currents_A=[-1., 1.])
    settings = dict(mesh_size_m=.01, outer_margin_m=.15, check_convergence=True, max_solves=100)
    actual = fields.field_map(geometry, **axes, settings=settings)
    assert actual['interpolation_usable'] is True
    assert actual['solves'] <= 100
    grid = controls.FieldMap(actual)
    point = grid.sample(gap_m=.030, lateral_m=0., current_A=0., temperature_C=20.)
    load = point['F_z_N']
    assert load > 0
    equilibrium = controls.zero_current_equilibria(grid, load, temperature_C=20.)
    assert equilibrium['equilibria'][0]['gap_m'] == pytest.approx(.030)
    assert equilibrium['equilibria'][0]['attractive_gap_mode_unstable'] is True
    mass, omega = load/9.80665, 5.
    kp = (mass*omega*omega-point['dF_z_dgap_N_per_m'])/point['dF_z_dcurrent_N_per_A']
    kd = 2*.8*mass*omega/point['dF_z_dcurrent_N_per_A']
    rate = max(20., 2*abs(kp/kd))
    gain = max(0., rate*point['L_H']-point['R_ohm'])
    local = controls.local_gap_model(point, mass_kg=mass, proportional_A_per_m=kp,
                                    derivative_A_s_per_m=kd, current_loop_gain_ohm=gain)
    assert local['hurwitz_strict'] is True
    assert local['physical_accepted'] is False
    unchecked = fields.field_map(geometry, **axes, settings=settings | dict(check_convergence=False, max_solves=40))
    assert unchecked['numerical_status'] == 'converged'
    assert unchecked['interpolation_usable'] is False
    with pytest.raises(controls.MapUnavailable):controls.FieldMap(unchecked)
    assert controls.zero_current_equilibria(unchecked, load, temperature_C=20.)['status'] == 'held-field-map'
    held = controls.simulate_gap(unchecked, scenario())
    assert held['status'] == 'held-local-model'
    assert held['local_model'] is None
