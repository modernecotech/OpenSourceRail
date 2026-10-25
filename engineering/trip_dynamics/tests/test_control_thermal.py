import math
import os
from pathlib import Path
import pytest
from engineering.trip_dynamics.thermal import temperature_step


def test_exact_thermal_balance_and_stationary_equilibrium():
    r = temperature_step(20., ambient_C=20., heat_W=100., capacity_J_K=1000., conductance_W_K=10., dt_s=100.)
    assert r['temperature_C'] == pytest.approx(30.-10.*math.exp(-1.))
    assert r['stored_heat_change_J']+r['rejected_heat_J'] == pytest.approx(10000.)
    adiabatic = temperature_step(20., ambient_C=20., heat_W=100., capacity_J_K=1000., conductance_W_K=0., dt_s=100.)
    assert adiabatic['temperature_C'] == 30.


@pytest.mark.parametrize('value', [0., -1., math.inf, math.nan])
def test_unknown_or_bad_thermal_capacity_refused(value):
    with pytest.raises(ValueError):
        temperature_step(20., ambient_C=20., heat_W=10., capacity_J_K=value, conductance_W_K=1., dt_s=1.)


def test_actual_rust_current_loop_energy_and_sensor_loss():
    binary = os.environ.get('OSR_RUST_CURRENT_LIBRARY')
    if not binary or not Path(binary).is_file():
        pytest.skip('explicit compiled Rust kernel path required')
    from engineering.trip_dynamics.onboard_control import current_fixture
    value = current_fixture(binary)
    assert value['maximum_RL_residual_J'] < 1e-10
    assert value['summed_dc_input_J'] == pytest.approx(value['summed_copper_heat_J']+value['summed_field_change_J'], abs=1e-10)
    assert value['sensor_loss']['applied_voltage_V'] == [0.,0.]
    assert value['sensor_loss']['current_A'][0] < value['final']['current_A'][0]
    assert value['sensor_loss']['copper_heat_J'] > 0
    assert not value['force_map_coupled'] and not value['physical_output_authorised']
