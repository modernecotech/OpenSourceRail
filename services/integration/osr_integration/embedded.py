"""Gateway bindings for existing Rust controller serialization (read-only)."""
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
    """Typed, simulation-only projection of six native Rust evaluators.

    Missing values fail the frame instead of becoming invented healthy zeros.
    Physical supplier adapters must have their own commissioned contracts.
    """
    if frame.get('schema') != 'osr-operating-bridge/1' or frame.get('environment') != 'simulation':
        raise ValueError('Unsupported operating bridge frame/environment')
    def number(value, low, high):
        if isinstance(value, bool):
            raise ValueError('Numeric reading expected')
        return finite(value, low, high)
    def boolean(value):
        if type(value) is not bool:
            raise ValueError('Boolean reading expected')
        return int(value)
    def enum(value, choices):
        if value not in choices:
            raise ValueError('Unsupported embedded enum')
        return choices.index(value)
    mask = frame['aux']['state']['faults']
    if type(mask) is not int or not 0 <= mask <= 7:
        raise ValueError('Unsupported auxiliary fault mask')
    values = energy_measurements(frame['energy'])
    station, zone = frame['station'], frame['lighting']
    values.update(station_measurements(station, zone))
    values.update({
        ('facilities', 'fault_count'): number(station['fault_count'], 0, 10000),
        ('vehicle-bms', 'soc_pct'): number(frame['bms']['state']['soc_ppt'], 0, 1000) / 10,
        ('vehicle-bms', 'charge_limit_a'): number(frame['bms']['charge_limit_ma'], 0, 2000000) / 1000,
        ('vehicle-bms', 'trip'): int(enum(frame['bms']['state']['alarm'], ['Nominal','Warning','Trip']) == 2),
        ('vehicle-aux', 'comfort_power'): boolean(frame['aux']['direct_hv_enabled']),
        ('vehicle-aux', 'fault_count'): mask.bit_count(),
        ('vehicle-hvac', 'compressor_pct'): number(frame['hvac']['compressor_ppt'], 0, 1000) / 10,
        ('vehicle-hvac', 'fan_pct'): number(frame['hvac']['fan_ppt'], 0, 1000) / 10,
        ('vehicle-hvac', 'reduced'): int(enum(frame['hvac']['mode'], ['Off','Ventilating','Cooling','Heating','Reduced']) == 4),
        ('vehicle-cbm', 'health'): enum(frame['cbm']['sample']['worst_health'], ['Nominal','Watch','Service']),
        ('vehicle-cbm', 'brake_remaining_pct'): number(frame['cbm']['sample']['brake_pad_remaining_ppt'][0], 0, 1000) / 10,
        ('vehicle-cbm', 'bearing_vibration_mm_s'): number(frame['cbm']['sample']['bearing_vib_ppt'][0], 0, 1000000) / 1000,
    })
    return values
