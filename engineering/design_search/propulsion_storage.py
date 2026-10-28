"""Conservative scalar capacitor-bank bounds, never a transient or hardware admission.

The low-voltage peak-current bound is applied throughout discharge. Charging
then restores the worst-case lost capacitor energy at constant current. Both
currents must fit continuous thermal bounds with the catalogue airflow. This
deliberately conservative screen does not establish actual cooling, voltage
control, repeated vehicle duty, force, installed mass or railway qualification.
"""
from collections import Counter
from hashlib import sha256
import json
from math import ceil, isfinite, sqrt


SCHEMA = 'osr-propulsion-storage-screen/1'
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             native_evaluator_admission=False, configuration_adopted=False,
             manufacturing_release=False, operating_release=False)
SETTINGS = {'series_modules', 'banks', 'module_high_voltage_V',
            'module_low_voltage_V', 'capacitance_fraction_hypothesis',
            'ESR_multiplier', 'intake_C', 'min_terminal_bus_V',
            'max_parallel', 'charger_efficiency'}


def _number(value, name, *, zero=False):
    if (type(value) not in (int, float) or not isfinite(value)
            or (value < 0 if zero else value <= 0)):
        raise ValueError('Finite ' + ('nonnegative ' if zero else 'positive ') + name + ' required')
    return value


def _signed(value, name):
    if type(value) not in (int, float) or not isfinite(value):
        raise ValueError('Finite ' + name + ' required')
    return value


def _integer(value, name, maximum):
    if type(value) is not int or not 1 <= value <= maximum:
        raise ValueError('Bounded positive integer ' + name + ' required')
    return value


def _identity(value):
    try:
        return sha256((json.dumps(value, sort_keys=True, separators=(',', ':'),
                                  allow_nan=False) + '\n').encode()).hexdigest()
    except (TypeError, ValueError) as error:
        raise ValueError('Ordinary finite serializable component/settings required') from error


def _peak_current(power_W, voltage_V, resistance_ohm):
    """Low-current root of P = (Voc - IR) I, stable as R approaches zero."""
    discriminant = voltage_V ** 2 - 4 * resistance_ohm * power_W
    if not isfinite(discriminant):
        raise ValueError('Peak-power arithmetic outside finite model domain')
    if discriminant < 0:
        return None
    return 2 * power_W / (voltage_V + sqrt(discriminant))


def size_bank(terminal_energy_kWh, peak_power_W, powered_duration_s, charge_s,
              component, settings):
    """Validate and execute the bounded scalar screen; see ``_size_bank``."""
    try:
        return _size_bank(terminal_energy_kWh, peak_power_W, powered_duration_s,
                          charge_s, component, settings)
    except ArithmeticError as error:
        raise ValueError('Bank arithmetic outside finite model domain') from error


def _size_bank(terminal_energy_kWh, peak_power_W, powered_duration_s, charge_s,
               component, settings):
    """Find the first conditional parallel count in the explicit bounded scan.

    Energy and power are total demand at the capacitor-bank terminals, summed
    across all banks. Drive losses belong in the caller's terminal demand;
    charger efficiency applies only to charging input. Capacitance retention is
    a research hypothesis, not a supplier EOL claim. Actual power never exceeds
    the supplied peak and internal voltage never falls below the selected low
    voltage during the bounded discharge. Initial thermal state, real duty and
    all hardware admission remain outside this scalar screen.
    """
    energy_J = _number(terminal_energy_kWh, 'terminal_energy_kWh') * 3.6e6
    peak = _number(peak_power_W, 'peak_power_W')
    duration = _number(powered_duration_s, 'powered_duration_s')
    charge_time = _number(charge_s, 'charge_s')
    if not isfinite(energy_J) or not isfinite(peak * duration):
        raise ValueError('Energy/power arithmetic outside finite model domain')
    if energy_J > peak * duration * (1 + 1e-12):
        raise ValueError('Terminal energy exceeds peak power times powered duration')
    if type(component) is not dict or component.get('schema') != 'osr-supercapacitor-catalogue/1':
        raise ValueError('Explicit capacitor catalogue schema required')
    source = component.get('source', {})
    source_hash = source.get('sha256') if type(source) is dict else None
    if (type(component.get('component_id')) is not str or not component['component_id']
            or type(source_hash) is not str or len(source_hash) != 64
            or any(character not in '0123456789abcdef' for character in source_hash)):
        raise ValueError('Component identity and source document hash required')
    if type(settings) is not dict or set(settings) != SETTINGS:
        raise ValueError('Exact explicit capacitor sizing settings required')
    component_id = _identity(component)
    settings_id = _identity(settings)
    nominal = _number(component.get('nominal_voltage_V'), 'nominal_voltage_V')
    capacitance = _number(component.get('capacitance_F'), 'capacitance_F')
    resistance = _number(component.get('esr_1s_ohm'), 'esr_1s_ohm', zero=True)
    series_limit = _number(component.get('maximum_series_voltage_V'), 'maximum_series_voltage_V')
    thermal_R = _number(component.get('thermal_resistance_K_per_W'), 'thermal_resistance_K_per_W')
    airflow = _number(component.get('thermal_airflow_CFM'), 'thermal_airflow_CFM')
    rated_continuous = _number(component.get('continuous_current_A_at_15K_rise'), 'continuous_current_A_at_15K_rise')
    peak_current_limit = _number(component.get('maximum_peak_current_A'), 'maximum_peak_current_A')
    minimum_C = _signed(component.get('operating_temperature_min_C'), 'operating_temperature_min_C')
    maximum_C = _signed(component.get('operating_temperature_max_C'), 'operating_temperature_max_C')
    bare_mass = _number(component.get('bare_mass_kg'), 'bare_mass_kg')
    bare_volume = _number(component.get('bare_volume_L'), 'bare_volume_L')
    if maximum_C <= minimum_C:
        raise ValueError('Ordered catalogue operating temperatures required')
    ns = _integer(settings['series_modules'], 'series_modules', 64)
    banks = _integer(settings['banks'], 'banks', 64)
    max_parallel = _integer(settings['max_parallel'], 'max_parallel', 64)
    high = _number(settings['module_high_voltage_V'], 'module_high_voltage_V')
    low = _number(settings['module_low_voltage_V'], 'module_low_voltage_V')
    fraction = _number(settings['capacitance_fraction_hypothesis'], 'capacitance_fraction_hypothesis')
    multiplier = _number(settings['ESR_multiplier'], 'ESR_multiplier')
    intake = _signed(settings['intake_C'], 'intake_C')
    minimum_bus = _number(settings['min_terminal_bus_V'], 'min_terminal_bus_V')
    charger_efficiency = _number(settings['charger_efficiency'], 'charger_efficiency')
    if not 0 < low < high <= nominal or ns * nominal > series_limit:
        raise ValueError('Nominal module/series voltage domain exceeded')
    if fraction > 1 or multiplier < 1 or charger_efficiency > 1:
        raise ValueError('Bounded capacitance, resistance and efficiency hypotheses required')
    if not minimum_C <= intake < maximum_C:
        raise ValueError('Intake must leave a positive catalogue temperature-rise budget')

    cm = capacitance * fraction
    rm = resistance * multiplier
    rise_budget = maximum_C - intake
    catalogue_current_bound = rated_continuous * sqrt(rise_budget / 15 / multiplier)
    thermal_current_bound = sqrt(rise_budget / (thermal_R * rm)) if rm else None
    continuous_bound = min(catalogue_current_bound, thermal_current_bound) if rm else catalogue_current_bound
    module_window = .5 * cm * (high ** 2 - low ** 2)
    values = (cm, rm, module_window, continuous_bound, ns * high, ns * low)
    if any(not isfinite(value) for value in values) or module_window <= 0:
        raise ValueError('Component arithmetic outside finite model domain')
    energy_only_parallel = ceil(energy_J / (banks * ns * module_window))
    request = dict(terminal_energy_kWh=terminal_energy_kWh, peak_power_W=peak,
                   powered_duration_s=duration, charge_s=charge_time,
                   settings=dict(settings), component_id=component.get('component_id'),
                   component_identity=component_id, settings_identity=settings_id)
    result = dict(schema=SCHEMA, request=request,
        energy_only_lower_bound=dict(parallel_strings_per_bank=energy_only_parallel,
            module_count=banks * ns * energy_only_parallel,
            bare_module_mass_kg=banks * ns * energy_only_parallel * bare_mass,
            scope='Energy window only; excludes discharge/charge loss, current, voltage and thermal checks'),
        catalogue_airflow_CFM_per_module=airflow,
        temperature_rise_budget_K=rise_budget,
        conditional_continuous_module_current_bound_A=continuous_bound,
        conditional_bound_satisfied=False, chosen=None, trials=[],
        actual_installed_mass_kg=None, actual_available_power_W=None,
        actual_operating_life_h=None, supplier_price=None,
        actual_motor_force_map_id=None, actual_charger_map_id=None,
        actual_cooling_airflow_CFM=None, actual_onboard_cycle_period_s=None,
        engineering_screen='unknown', **FLAGS,
        assumptions=[
            'Equal bank loads and identical parallel strings; no failed bank/string.',
            'The supplied terminal power is nonnegative and bounded by the peak throughout discharge.',
            'Catalogue one-second ESR is extrapolated as constant resistance for this scalar duty screen.',
            'Capacitance retention is an explicit research hypothesis, not an authenticated supplier limit.',
            'Catalogue thermal resistance and current ratings require the stated airflow for every module.',
            'Steady continuous thermal bounds cover each phase; no one-second peak rating admits a longer duty.',
            'Initial thermal condition, real vehicle cycle, fan faults and hot supplier curves remain unestablished.',
            'Bare module stock excludes enclosure, busbars, conversion, protection, mounts, cooling and labour.'])
    counts = Counter()
    for parallel in range(1, max_parallel + 1):
        cb = cm * parallel / ns
        rb = rm * ns / parallel
        open_high = ns * high
        open_low = ns * low
        window_J = banks * .5 * cb * (open_high ** 2 - open_low ** 2)
        trial = dict(parallel_strings_per_bank=parallel,
                     module_count=banks * ns * parallel,
                     bank_capacitance_F=cb, bank_resistance_ohm=rb,
                     capacitor_window_energy_kWh=window_J / 3.6e6,
                     failures=[])
        current = _peak_current(peak / banks, open_low, rb)
        if current is None:
            trial['failures'].append('peak-power-discriminant')
        else:
            module_current = current / parallel
            terminal_low = open_low - current * rb
            loss_J = banks * current ** 2 * rb * duration
            used_J = energy_J + loss_J
            discharge_rise = module_current ** 2 * rm * thermal_R
            trial.update(discharge_bank_peak_current_A=current,
                discharge_module_peak_current_A=module_current,
                terminal_bus_voltage_lower_bound_V=terminal_low,
                discharge_ESR_energy_upper_kWh=loss_J / 3.6e6,
                required_capacitor_energy_upper_kWh=used_J / 3.6e6,
                discharge_steady_temperature_C=intake + discharge_rise)
            if terminal_low < minimum_bus:
                trial['failures'].append('discharge-terminal-bus-voltage')
            if discharge_rise > rise_budget or module_current > continuous_bound:
                trial['failures'].append('discharge-continuous-thermal-bound')
            if module_current > peak_current_limit:
                trial['failures'].append('discharge-absolute-current-limit')
            if used_J > window_J:
                trial['failures'].append('capacitor-energy-window')
            else:
                end_squared = open_high ** 2 - 2 * used_J / (banks * cb)
                if end_squared < 0:
                    raise ValueError('Energy-window arithmetic inconsistent')
                end = sqrt(end_squared)
                charging_current = cb * (open_high - end) / charge_time
                module_charging_current = charging_current / parallel
                charging_loss_J = banks * charging_current ** 2 * rb * charge_time
                charging_rise = module_charging_current ** 2 * rm * thermal_R
                charging_module_terminal = high + module_charging_current * rm
                charging_peak = banks * charging_current * (open_high + charging_current * rb)
                trial.update(post_discharge_open_voltage_lower_bound_V=end,
                    charge_bank_current_upper_A=charging_current,
                    charge_module_current_upper_A=module_charging_current,
                    charge_module_terminal_voltage_upper_V=charging_module_terminal,
                    charge_ESR_energy_upper_kWh=charging_loss_J / 3.6e6,
                    charge_steady_temperature_C=intake + charging_rise,
                    charger_output_peak_power_upper_W=charging_peak,
                    charger_input_peak_power_upper_W=charging_peak / charger_efficiency,
                    charger_input_energy_upper_kWh=(used_J + charging_loss_J) / charger_efficiency / 3.6e6,
                    charger_input_average_power_upper_W=(used_J + charging_loss_J) / charger_efficiency / charge_time)
                if charging_module_terminal > nominal:
                    trial['failures'].append('charge-module-terminal-voltage')
                if charging_rise > rise_budget or module_charging_current > continuous_bound:
                    trial['failures'].append('charge-continuous-thermal-bound')
                if module_charging_current > peak_current_limit:
                    trial['failures'].append('charge-absolute-current-limit')
        # Float overflow must never turn a bound into an admitted size.
        if any(type(value) is float and not isfinite(value) for value in trial.values()):
            raise ValueError('Bank arithmetic outside finite model domain')
        trial['conditional_scalar_screen'] = 'fail' if trial['failures'] else 'pass'
        result['trials'].append(trial)
        counts.update(trial['failures'])
        if not trial['failures']:
            result['chosen'] = dict(trial,
                bare_module_mass_kg=trial['module_count'] * bare_mass,
                bare_module_volume_L=trial['module_count'] * bare_volume)
            result['conditional_bound_satisfied'] = True
            break
    result['failure_counts'] = dict(sorted(counts.items()))
    result['scanned_parallel_count'] = len(result['trials'])
    result['screen'] = 'conditional-bounds-satisfied' if result['chosen'] else 'no-size-within-bounds'
    chosen = result['chosen']
    result.update(calculation_status='sized-conditional-bound' if chosen else 'no-size-within-bounds',
        module_count=chosen['module_count'] if chosen else None,
        parallel_strings_per_bank=chosen['parallel_strings_per_bank'] if chosen else None,
        bare_module_mass_kg=chosen['bare_module_mass_kg'] if chosen else None,
        bare_module_volume_L=chosen['bare_module_volume_L'] if chosen else None,
        grid_recharge_energy_upper_kWh=chosen['charger_input_energy_upper_kWh'] if chosen else None)
    result['evaluation_id'] = _identity({k: v for k, v in result.items() if k != 'evaluation_id'})
    return result
