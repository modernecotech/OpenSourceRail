"""Gateway bindings for observation-only Rust supervisory frames."""
import re

from .config import finite


def energy_measurements(frame):
    if frame.get('schema') != 'osr-energy-site/1':
        raise ValueError('Unsupported embedded energy frame')
    return {
        ('pv', 'power_kw'): finite(frame['pv_w'], 0, 1e9) / 1000,
        ('charger', 'power_kw'): finite(frame['to_pad_w'], 0, 1e9) / 1000,
        ('battery', 'soc_pct'): finite(frame['battery_soc_ppt'], 0, 1000) / 10,
    }


def station_measurements(output, lighting_zone):
    """osr-station-scada StationScadaOutput + LightingZoneStatus, no control bypass."""
    if output['health'] not in ('Nominal', 'Warning', 'Degraded'):
        raise ValueError('Unknown station health')
    enabled = output['lighting_enabled'][0]
    if type(enabled) is not bool:
        raise ValueError('Boolean effective lighting state required')
    return {('facilities', 'lighting_pct'): finite(lighting_zone['dim_ppt'], 0, 1000) / 10 if enabled else 0}


def operating_measurements(frame):
    """Strict simulation projection of the native Rust observation contract.

    The contract contains no command or safety-authority type. Missing, duplicate,
    unexpected, wrongly sourced or wrongly scaled observations fail the whole
    frame instead of becoming invented healthy values.
    """
    if set(frame) != {'schema', 'environment', 'authority', 'key', 'source_time_ns', 'observations'}:
        raise ValueError('Operating frame fields do not match the observation-only contract')
    if (frame['schema'] != 'osr-supervisory-observations/1'
            or frame['environment'] != 'simulation'
            or frame['authority'] != 'observation-only'):
        raise ValueError('Unsupported operating frame schema, environment or authority')
    if (not isinstance(frame['key'], str)
            or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:|\-]{0,159}', frame['key'])):
        raise ValueError('Invalid operating frame identity')
    if type(frame['source_time_ns']) is not int or frame['source_time_ns'] <= 0:
        raise ValueError('Invalid operating frame source time')

    spec = {
        ('pv', 'power_kw'): ('kW', ('osr-energy-site',), 0, 1000),
        ('charger', 'power_kw'): ('kW', ('osr-energy-site',), 0, 500),
        ('battery', 'soc_pct'): ('%', ('osr-energy-site',), 0, 100),
        ('facilities', 'lighting_pct'): ('%', ('osr-station-scada',), 0, 100),
        ('facilities', 'fault_count'): ('count', ('osr-station-scada',), 0, 10000),
        ('vehicle-bms', 'soc_pct'): ('%', ('osr-bms',), 0, 100),
        ('vehicle-bms', 'charge_limit_a'): ('A', ('osr-bms',), 0, 2000),
        ('vehicle-bms', 'trip'): ('bool', ('osr-bms',), 0, 1),
        ('vehicle-aux', 'comfort_power'): ('bool', ('osr-aux-power',), 0, 1),
        ('vehicle-aux', 'fault_count'): ('count', ('osr-aux-power',), 0, 3),
        ('vehicle-hvac', 'compressor_pct'): ('%', ('osr-hvac', 'osr-aux-power'), 0, 100),
        ('vehicle-hvac', 'fan_pct'): ('%', ('osr-hvac', 'osr-aux-power'), 0, 100),
        ('vehicle-hvac', 'reduced'): ('bool', ('osr-hvac', 'osr-aux-power'), 0, 1),
        ('vehicle-cbm', 'health'): ('severity', ('osr-cbm-onboard',), 0, 2),
        ('vehicle-cbm', 'brake_remaining_pct'): ('%', ('osr-cbm-onboard',), 0, 100),
        ('vehicle-cbm', 'bearing_vibration_mm_s'): ('mm/s', ('osr-cbm-onboard',), 0, 1000),
        ('points', 'detected_position'): ('position', ('osr-wayside-points',), 0, 2),
        ('points', 'detection_unknown'): ('bool', ('osr-wayside-points',), 0, 1),
        ('points', 'motor_active'): ('bool', ('osr-wayside-points',), 0, 1),
        ('level-crossing', 'state'): ('state', ('osr-level-crossing',), 0, 4),
        ('level-crossing', 'fault'): ('bool', ('osr-level-crossing',), 0, 1),
        ('level-crossing', 'warning_active'): ('bool', ('osr-level-crossing',), 0, 1),
        ('faregate', 'gate_open'): ('bool', ('osr-afc',), 0, 1),
        ('faregate', 'last_decision'): ('decision', ('osr-afc',), 0, 2),
        ('faregate', 'grant_count'): ('count', ('osr-afc',), 0, 1e12),
        ('faregate', 'denial_count'): ('count', ('osr-afc',), 0, 1e12),
    }
    integral = {
        ('facilities', 'fault_count'), ('vehicle-bms', 'trip'),
        ('vehicle-aux', 'comfort_power'), ('vehicle-aux', 'fault_count'),
        ('vehicle-hvac', 'reduced'), ('vehicle-cbm', 'health'),
        ('points', 'detected_position'), ('points', 'detection_unknown'),
        ('points', 'motor_active'), ('level-crossing', 'state'),
        ('level-crossing', 'fault'), ('level-crossing', 'warning_active'),
        ('faregate', 'gate_open'), ('faregate', 'last_decision'),
        ('faregate', 'grant_count'), ('faregate', 'denial_count'),
    }
    observations = frame['observations']
    if not isinstance(observations, list) or len(observations) != len(spec):
        raise ValueError('Operating frame has missing or excess observations')
    values = {}
    for observation in observations:
        if not isinstance(observation, dict) or set(observation) != {
                'equipment_type', 'measurement', 'value', 'unit', 'source_crates'}:
            raise ValueError('Observation fields do not match the contract')
        identity = (observation['equipment_type'], observation['measurement'])
        if identity not in spec or identity in values:
            raise ValueError('Unexpected or duplicate operating observation')
        unit, sources, low, high = spec[identity]
        if observation['unit'] != unit or tuple(observation['source_crates']) != sources:
            raise ValueError('Observation unit or source crate does not match its contract')
        value = finite(observation['value'], low, high)
        if identity in integral and value != int(value):
            raise ValueError('Discrete operating observation must be an integer')
        values[identity] = value
    if set(values) != set(spec):
        raise ValueError('Operating frame does not contain the exact observation set')
    return values
