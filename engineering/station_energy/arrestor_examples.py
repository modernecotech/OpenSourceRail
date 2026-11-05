"""Explicit, non-exhaustive G1/G2/G3 station-module research configurations."""
from copy import deepcopy
import json
from math import sqrt
from pathlib import Path

from engineering.station_rail import ROOT

POLICY = 'engineering/station_energy/data/arrestor-scenario.json'
SCHEMA = 'osr-multistage-arrestor-request/1'


def policy(root=ROOT):
    value = json.loads((Path(root)/POLICY).read_bytes())
    if (value.get('schema') != 'osr-arrestor-scenario/1'
        or value.get('research_only') is not True):
        raise ValueError('Explicit research-only arrestor scenario required')
    return value


def case(store, capture, cruise, ratio, handover, arrangement, rules):
    fractions = rules['car_mass_fractions']
    forces = [0.0]*len(fractions)
    if arrangement == 'front':
        forces[0] = 1.0
    elif arrangement == 'rear':
        forces[-1] = 1.0
    elif arrangement == 'distributed':
        forces = list(fractions)
    else:
        raise ValueError('An explicit force-distribution arrangement is required')
    design = {k:v for k,v in store.items() if k not in ('id', 'name')}
    incoming = 0.5*rules['effective_mass_kg']*capture**2
    available = max(0.0, incoming*rules['efficiency_capture']*rules['efficiency_store']
        - rules['standing_loss_w']*rules['dwell_s'])
    launch_target = min(rules['launcher_target_speed_m_s'],
        sqrt(2*available*rules['efficiency_release']/rules['effective_mass_kg']), cruise/3.6)
    stages = [dict(exit_speed_m_s=capture*f,
        max_deceleration_m_s2=rules['max_capture_deceleration_m_s2'],
        max_jerk_m_s3=rules['max_capture_jerk_m_s3'],
        available_stroke_m=rules['available_stage_stroke_m'],
        force_limit_n=None, displacement_ratio=ratio)
        for f in rules['stage_exit_fractions']] if capture else []
    return dict(id=f"{store['id']}-c{capture:g}-v{cruise:g}-r{ratio:g}-{handover}-{arrangement}",
        effective_mass_kg=rules['effective_mass_kg'], capture_entry_speed_m_s=capture,
        grade_fraction=0.0, resistance_n=0.0, handover=handover, stages=stages,
        storage=dict(capacity_j=incoming*rules['capacity_headroom_factor'],
            initial_j=0.0, reserve_j=0.0, efficiency_capture=rules['efficiency_capture'],
            efficiency_store=rules['efficiency_store'], efficiency_release=rules['efficiency_release'],
            standing_loss_w=rules['standing_loss_w'], dwell_s=rules['dwell_s'],
            isolated_during_dwell=True, controlled_forward_transfer=True,
            departure_authorized=True, design=design),
        launch=dict(target_speed_m_s=launch_target,
            max_acceleration_m_s2=rules['max_launch_acceleration_m_s2'],
            max_jerk_m_s3=rules['max_launch_jerk_m_s3'],
            available_stroke_m=rules['available_launcher_stroke_m'], force_limit_n=None,
            mass_fractions=list(fractions), force_fractions=forces),
        booster=dict(target_speed_m_s=cruise/3.6,
            max_acceleration_m_s2=rules['max_launch_acceleration_m_s2'],
            max_jerk_m_s3=rules['max_launch_jerk_m_s3'],
            efficiency=rules['booster_efficiency'],
            available_stroke_m=rules['available_booster_stroke_m'],
            force_limit_n=None, source_power_limit_w=None),
        reset_s=rules['reset_s'], headway_s=rules['headway_s'])


def request(root=ROOT):
    rules = policy(root)
    cases = [case(store, capture, cruise, ratio, handover, arrangement, rules)
        for store in rules['stores'] for capture in rules['capture_speeds_m_s']
        for cruise in rules['cruise_speeds_kmh'] for ratio in rules['displacement_ratios']
        for handover in rules['handovers'] for arrangement in rules['launch_arrangements']]
    # Explicit full-release controls keep a booster optional. These are local
    # station events; upstream motion must supply the declared arrival energy.
    for store in rules['stores']:
        for cruise in (40.0, 50.0, 60.0):
            row = case(store, 20.0, cruise, 10.0, 'continuous-total-force', 'rear', rules)
            row['id'] = f"{store['id']}-full-release-c20-v{cruise:g}"
            row['launch']['target_speed_m_s'] = cruise/3.6
            row['launch']['available_stroke_m'] = 200.0
            row['reset_s'] = 60.0
            cases.append(row)
    for cruise in rules['cruise_speeds_kmh']:
        row = case(rules['stores'][0], 0.0, cruise, 1.0,
            'continuous-total-force', 'rear', rules)
        row['id'] = f'no-capture-v{cruise:g}'
        row['storage']['standing_loss_w'] = 0.0
        cases.append(row)
    if len(cases) > min(1000, rules['maximum_cases']):
        raise ValueError('Arrestor scenario exceeds the declared campaign budget')
    return dict(schema=SCHEMA, cases=deepcopy(cases))


def reference_case(root=ROOT):
    """A literature-density control with the user's ideal 70% return example."""
    rules = policy(root)
    store = dict(id='reference', name='Declared 140 J/kg material sensitivity',
        kind='declared-specific-energy', specific_energy_j_kg=140.0,
        density_kg_m3=7850.0, packing_fraction=0.2)
    row = case(store, 10.0, 72.0, 10.0, 'continuous-total-force', 'rear', rules)
    row['id'] = 'reference-160t-capture-10ms'
    row['storage']['capacity_j'] = 8000000.0
    row['storage']['standing_loss_w'] = 0.0
    row['launch']['target_speed_m_s'] = sqrt(70.0)
    return row
