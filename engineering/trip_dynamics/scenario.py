"""Explicit six-car route/load cases and an independent kinematic target."""
from copy import deepcopy
import math

from engineering.design_search.contracts import identity

SCHEMA = 'osr-trip-scenario/1'
MODES = {'evidence', 'benchmark', 'exploration'}
G = 9.80665


def finite(value, name, *, positive=False):
    if type(value) not in (int, float) or not math.isfinite(value) or (value <= 0 if positive else value < 0):
        raise ValueError('finite '+('positive ' if positive else 'nonnegative ')+name+' required')
    return float(value)


def scenario(case_id, distance_m, load_case, *, temperature_C=20., mode='evidence', fault=None,
             mechanical_step_s=.001, candidate_id=None, vehicle_id=None):
    value = dict(schema=SCHEMA, case_id=case_id, distance_m=float(distance_m), load_case=load_case,
                 temperature_C=float(temperature_C), cars=6, car_length_m=17., powered_zone_m=350.,
                 max_speed_m_s=20., acceleration_m_s2=.8, mechanical_step_s=mechanical_step_s,
                 mode=mode, fault=deepcopy(fault), candidate_id=candidate_id, vehicle_id=vehicle_id)
    value['scenario_id'] = identity(value)
    return validate(value)


def validate(value):
    if value.get('schema') != SCHEMA or value.get('mode') not in MODES:
        raise ValueError('declared trip schema and mode required')
    if value.get('cars') != 6 or type(value['cars']) is not int or value.get('car_length_m') != 17.:
        raise ValueError('this campaign retains six 17 m cars')
    if value.get('load_case') not in {'empty', 'AW3', 'asymmetric'}:
        raise ValueError('explicit empty/AW3/asymmetric load required')
    if not isinstance(value.get('case_id'), str) or not value['case_id']:
        raise ValueError('case identity required')
    for key in ('candidate_id', 'vehicle_id'):
        candidate = value.get(key)
        if candidate is not None and (not isinstance(candidate, str) or len(candidate) != 64 or any(c not in '0123456789abcdef' for c in candidate)):
            raise ValueError('separate physical/reference vehicle SHA256 required')
    finite(value['distance_m'], 'route distance')
    if not 0 <= value['distance_m'] <= 2000:
        raise ValueError('bounded 0–2 km route required')
    for key in ('car_length_m', 'powered_zone_m', 'max_speed_m_s', 'acceleration_m_s2', 'mechanical_step_s'):
        finite(value[key], key, positive=True)
    if not .00001 <= value['mechanical_step_s'] <= .02:
        raise ValueError('bounded mechanical clock required')
    if type(value['temperature_C']) not in (int, float) or not math.isfinite(value['temperature_C']) or not -20 <= value['temperature_C'] <= 80:
        raise ValueError('bounded declared environment required')
    if value.get('fault') is not None and value['fault'] != {'id': 'receiving-power-loss', 'at_s': 80.}:
        raise ValueError('only the explicit receiving-power-loss task is currently declared')
    payload = {k: v for k, v in value.items() if k != 'scenario_id'}
    if value.get('scenario_id') != identity(payload):
        raise ValueError('trip scenario identity differs')
    return deepcopy(value)


def bind_vehicle(value, candidate_id):
    value = validate(value)
    if value.get('candidate_id') not in (None, candidate_id):
        raise ValueError('scenario is bound to a different physical candidate')
    value['candidate_id'] = candidate_id
    value['scenario_id'] = identity({k: v for k, v in value.items() if k != 'scenario_id'})
    return validate(value)


def campaign_cases():
    return [scenario('A-hover-empty', 0, 'empty'), scenario('B-hover-AW3', 0, 'AW3'),
            scenario('C-1500-empty', 1500, 'empty'), scenario('D-1500-AW3', 1500, 'AW3'),
            scenario('E-2000-empty', 2000, 'empty'), scenario('F-2000-AW3', 2000, 'AW3'),
            scenario('G-2000-asymmetric', 2000, 'asymmetric'),
            scenario('H-2000-hot-AW3', 2000, 'AW3', temperature_C=50.),
            scenario('I-2000-receiver-loss', 2000, 'AW3', fault={'id': 'receiving-power-loss', 'at_s': 80.})]


def kinematic_target(case, masses_kg, *, acceleration_efficiency=.85):
    """Lossless independent target, not an actuator or hover calculation."""
    case = validate(case)
    if len(masses_kg) != 6:
        raise ValueError('six explicitly identified comparison masses required')
    mass = math.fsum(finite(m, 'comparison car mass', positive=True) for m in masses_kg)
    efficiency = finite(acceleration_efficiency, 'illustrative acceleration efficiency', positive=True)
    if efficiency > 1:
        raise ValueError('efficiency cannot exceed unity')
    a, distance = case['acceleration_m_s2'], case['distance_m']
    v = min(case['max_speed_m_s'], math.sqrt(a*distance))
    ta = v/a
    powered_distance = v*v/(2*a)
    coast = max(0., distance-2*powered_distance)
    duration = 2*ta+(coast/v if v else 0.)
    kinetic = .5*mass*v*v
    return dict(schema='osr-trip-kinematic-target/1', scenario_id=case['scenario_id'],
                total_comparison_mass_kg=mass, journey_time_s=duration, peak_speed_m_s=v,
                acceleration_distance_m=powered_distance, braking_distance_m=powered_distance,
                coasting_distance_m=coast, propulsive_force_N=mass*a if v else 0.,
                peak_mechanical_power_W=mass*a*v,
                illustrative_acceleration_input_peak_W=mass*a*v/efficiency,
                assumed_acceleration_efficiency=efficiency,
                arrival_kinetic_energy_J=kinetic, arrival_kinetic_energy_kWh=kinetic/3.6e6,
                geometry_only_zone_length_sufficient=powered_distance <= case['powered_zone_m'],
                full_formation_powered_overlap_proved=False,
                exclusions=['drag', 'grade', 'jerk limits', 'suspension and guidance',
                            'electrical limits', 'auxiliary power', 'thermal duty', 'finite train overlap'],
                physical_accepted=False)
