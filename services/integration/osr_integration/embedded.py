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
    return {('facilities', 'lighting_pct'): finite(lighting_zone['dim_ppt'], 0, 1000) / 10 if lighting_zone['enabled'] else 0}
