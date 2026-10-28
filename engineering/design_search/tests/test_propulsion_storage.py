"""Independent closed-form controls for conservative capacitor sizing screens."""
from copy import deepcopy
import json
from math import sqrt
from pathlib import Path

import pytest

from engineering.design_search import propulsion_storage as storage


@pytest.fixture
def component():
    return json.loads((Path(storage.__file__).parent / 'data/skeleton-102v94f-catalogue.json').read_text())


@pytest.fixture
def settings():
    return dict(series_modules=7, banks=2, module_high_voltage_V=98.,
                module_low_voltage_V=49., capacitance_fraction_hypothesis=.8,
                ESR_multiplier=2., intake_C=50., min_terminal_bus_V=300.,
                max_parallel=64, charger_efficiency=.95)


def run(component, settings, energy=9.947032323914694, power=1480372.654643716,
        duration=50., charge=35.):
    return storage.size_bank(energy, power, duration, charge, component, settings)


def test_ideal_resistance_control_closes_energy_and_charge(component, settings):
    component['esr_1s_ohm'] = 0.
    component['continuous_current_A_at_15K_rise'] = 1e9
    component['maximum_peak_current_A'] = 1e9
    result = run(component, settings)
    row = result['chosen']
    assert row is not None
    assert row['parallel_strings_per_bank'] == result['energy_only_lower_bound']['parallel_strings_per_bank']
    assert row['discharge_ESR_energy_upper_kWh'] == 0
    assert row['charge_ESR_energy_upper_kWh'] == 0
    cb = 94 * .8 * row['parallel_strings_per_bank'] / 7
    end = sqrt((7 * 98) ** 2 - 2 * 9.947032323914694 * 3.6e6 / (2 * cb))
    assert row['post_discharge_open_voltage_lower_bound_V'] == pytest.approx(end)
    assert row['charge_bank_current_upper_A'] == pytest.approx(cb * (7 * 98 - end) / 35)
    assert row['charger_input_energy_upper_kWh'] == pytest.approx(9.947032323914694 / .95)


def test_quadratic_root_matches_terminal_power_and_lower_voltage():
    current = storage._peak_current(100000., 400., .1)
    assert current * (400 - current * .1) == pytest.approx(100000)
    assert storage._peak_current(100., 10., 1.) is None
    assert storage._peak_current(100., 10., 0.) == 10


def test_real_component_needs_more_than_energy_only_and_preserves_holds(component, settings):
    result = run(component, settings)
    row = result['chosen']
    assert row is not None
    assert row['parallel_strings_per_bank'] > result['energy_only_lower_bound']['parallel_strings_per_bank']
    assert all(trial['failures'] for trial in result['trials'][:-1])
    assert row['bare_module_mass_kg'] == row['module_count'] * 29
    assert row['bare_module_volume_L'] == row['module_count'] * 30.6
    assert row['required_capacitor_energy_upper_kWh'] <= row['capacitor_window_energy_kWh']
    assert row['terminal_bus_voltage_lower_bound_V'] >= 300
    assert row['charge_module_terminal_voltage_upper_V'] <= 102
    for key in ('discharge_steady_temperature_C', 'charge_steady_temperature_C'):
        assert row[key] <= 60
    assert all(result[key] is False for key in storage.FLAGS)
    for key in ('actual_installed_mass_kg', 'actual_available_power_W',
                'actual_operating_life_h', 'supplier_price', 'actual_motor_force_map_id'):
        assert result[key] is None
    assert result == run(component, settings)


def test_one_second_peak_cannot_admit_a_fifty_second_duty(component, settings):
    component['maximum_peak_current_A'] = 1e12
    settings['max_parallel'] = 1
    result = run(component, settings, energy=.1, power=200000.)
    assert result['chosen'] is None
    assert result['failure_counts']['discharge-continuous-thermal-bound'] == 1


def test_hot_intake_and_resistance_ageing_do_not_improve_sizes(component, settings):
    cool = dict(settings, intake_C=35., ESR_multiplier=1.)
    aged = run(component, settings)
    cold = run(component, cool)
    assert aged['chosen']['module_count'] >= cold['chosen']['module_count']
    assert aged['conditional_continuous_module_current_bound_A'] < cold['conditional_continuous_module_current_bound_A']


def test_charger_grid_energy_matches_constant_current_work_and_loss(component, settings):
    row = run(component, settings)['chosen']
    current = row['charge_bank_current_upper_A']
    beginning = row['post_discharge_open_voltage_lower_bound_V']
    end = settings['series_modules'] * settings['module_high_voltage_V']
    average_terminal_power = settings['banks'] * current * (
        (beginning + end) / 2 + current * row['bank_resistance_ohm'])
    grid_energy = average_terminal_power * 35 / settings['charger_efficiency'] / 3.6e6
    assert row['charger_input_energy_upper_kWh'] == pytest.approx(grid_energy)
    assert row['charger_input_peak_power_upper_W'] >= average_terminal_power / settings['charger_efficiency']


def test_charging_thermal_limit_is_checked_independently(component, settings):
    result = run(component, settings, charge=.1)
    assert result['chosen'] is None
    assert result['failure_counts']['charge-continuous-thermal-bound'] > 0


def test_capacitance_retention_changes_energy_floor_without_supplier_claim(component, settings):
    fresh = run(component, dict(settings, capacitance_fraction_hypothesis=1.))
    aged = run(component, settings)
    assert aged['energy_only_lower_bound']['module_count'] > fresh['energy_only_lower_bound']['module_count']
    assert component['published_EOL_capacitance_fraction'] is None


def test_terminal_voltage_cannot_be_replaced_by_open_circuit_voltage(component, settings):
    settings['min_terminal_bus_V'] = 7 * 49
    result = run(component, settings)
    assert result['chosen'] is None
    assert all('discharge-terminal-bus-voltage' in trial['failures']
               for trial in result['trials'] if 'terminal_bus_voltage_lower_bound_V' in trial)


def test_no_charge_headroom_rejects_nonzero_resistive_charging(component, settings):
    settings['module_high_voltage_V'] = 102.
    result = run(component, settings)
    assert result['chosen'] is None
    assert result['failure_counts']['charge-module-terminal-voltage'] > 0


def test_insufficient_parallel_budget_retains_failures(component, settings):
    settings['max_parallel'] = 2
    result = run(component, settings)
    assert result['chosen'] is None
    assert result['screen'] == 'no-size-within-bounds'
    assert len(result['trials']) == 2
    assert result['failure_counts']


@pytest.mark.parametrize('key,value', [
    ('series_modules', True), ('banks', 0), ('max_parallel', 65),
    ('module_high_voltage_V', 108.), ('module_low_voltage_V', 98.),
    ('capacitance_fraction_hypothesis', 1.01), ('ESR_multiplier', .5),
    ('intake_C', 60.), ('intake_C', float('nan')),
    ('min_terminal_bus_V', 0.), ('charger_efficiency', 1.01)])
def test_bad_settings_fail_closed(component, settings, key, value):
    settings[key] = value
    with pytest.raises(ValueError):
        run(component, settings)


@pytest.mark.parametrize('arguments', [
    dict(energy=float('inf')), dict(power=0.), dict(duration=-1.),
    dict(charge=0.), dict(energy=1., power=1., duration=1.)])
def test_bad_terminal_requests_fail_closed(component, settings, arguments):
    with pytest.raises(ValueError):
        run(component, settings, **arguments)


def test_catalogue_keeps_supplier_and_research_eol_claims_separate(component):
    assert component['published_EOL_capacitance_fraction'] is None
    assert component['published_design_esr_multiplier'] == 2
    assert 'draft' in component['source']['status']
    assert component['rail_qualification_authenticated'] is False


def test_input_units_and_series_domain_fail_closed(component, settings):
    invalid = deepcopy(component)
    invalid['thermal_resistance_K_per_W'] = None
    with pytest.raises(ValueError):
        run(invalid, settings)
    settings['series_modules'] = 13
    with pytest.raises(ValueError, match='series voltage'):
        run(component, settings)


def test_nonfinite_arithmetic_cannot_return_an_admitted_size(component, settings):
    result = run(component, settings, energy=1., power=1e308, duration=1e-300)
    assert result['chosen'] is None
    assert result['failure_counts']['peak-power-discriminant'] == 64
    component['esr_1s_ohm'] = 1e308
    with pytest.raises(ValueError):
        run(component, settings)


def test_public_result_keys_and_source_identity(component, settings):
    result = run(component, settings)
    assert result['calculation_status'] == 'sized-conditional-bound'
    assert result['module_count'] == result['chosen']['module_count']
    assert result['grid_recharge_energy_upper_kWh'] == result['chosen']['charger_input_energy_upper_kWh']
    component['source']['sha256'] = 'not-a-source-hash'
    with pytest.raises(ValueError, match='source document hash'):
        run(component, settings)
