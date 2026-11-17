"""Bounded equal-assumption propulsion demand for a proposed short demonstrator.

This reuses architecture_demand. A reached trajectory is never available force,
thermal duty, a selected drive, or an accepted braking system.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from engineering.design_search.architecture_demand import G, demand
from engineering.station_rail import braking, vehicle

ROOT = Path(__file__).resolve().parents[2]
SOURCES = (
    'engineering/design_search/demonstrator_propulsion.py',
    'engineering/design_search/architecture_demand.py',
    'engineering/station_rail/vehicle.py',
    'engineering/station_rail/braking.py',
    'engineering/development-baseline.toml',
)
SELECTED = '756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3'


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def identity(value):
    return sha256(encoded(value)).hexdigest()


def evaluate(config, root=ROOT):
    root = Path(root)
    if config.get('schema') != 'osr-v07-demonstrator-propulsion-input/1':
        raise ValueError('Explicit demonstrator input schema required')
    if config.get('parent_selected_vehicle_candidate_id') != SELECTED:
        raise ValueError('Mixed selected vehicle candidate')
    model = config['model']
    if model['speed_cap_m_s'] != 20 or model['cars'] != 6 or model['headway_s'] != 120:
        raise ValueError('Retained 72 km/h, six-car, 120-second comparison control required')
    if sorted(model['spacing_m']) != [1500, 2000] or sorted(model['uphill_grade_fraction']) != [0, .01, .02]:
        raise ValueError('Declared demonstrator spacing and grade controls required')
    if [a['id'] for a in config['architectures']] != [
        'station-only', 'station-plus-midroute-booster', 'powered-wheel-sustained'
    ]:
        raise ValueError('Three explicit architecture definitions required')
    v = vehicle.build(root)
    if v['candidate_id'] != SELECTED:
        raise ValueError('Selected vehicle source differs')
    m = v['mass']['accounted_cap_loaded_kg_per_car']
    rotor = braking.rotating_stock(v)['equivalent_inertial_mass_kg_per_car']
    sources = {p: sha256((root / p).read_bytes()).hexdigest() for p in SOURCES}
    input_id = identity(dict(config=config, source_sha256=sources))
    rows = []
    for spacing in model['spacing_m']:
        for grade in model['uphill_grade_fraction']:
            for architecture in config['architectures']:
                windows = architecture['powered_windows_m'][str(spacing)]
                result = demand(
                    spacing, m, rotor, powered_windows=windows,
                    cars=model['cars'], speed_cap_m_s=model['speed_cap_m_s'],
                    acceleration_m_s2=model['acceleration_command_m_s2'],
                    deceleration_m_s2=model['independent_stop_target_m_s2'],
                    grade=grade, dt=model['dt_s'],
                    rolling_coefficient=model['rolling_coefficient'],
                    constant_resistance_N_per_car=model['constant_resistance_N_per_car'],
                    aero_coefficient_N_s2_m2=model['aero_coefficient_N_s2_m2_per_car'],
                )
                definition = dict(parent_selected_vehicle_candidate_id=SELECTED,
                                  architecture=architecture['id'], spacing_m=spacing,
                                  powered_windows_m=windows,
                                  driven_axles=architecture['driven_axles'])
                row = dict(
                    railway_research_configuration_id=identity(definition),
                    architecture=architecture['id'], spacing_m=spacing,
                    grade_up_fraction=grade, powered_windows_m=windows,
                    declared_powered_window_m=sum(hi-lo for lo, hi in windows),
                    installed_stator_or_conductor_length_m=None,
                    driven_axles=architecture['driven_axles'],
                    demand_id=result['demand_id'], execution=result['execution'],
                    numerical_validity=result['numerical_validity'],
                    analytical_target_reached=result['reachable'],
                    reason=result['reason'], runtime_s=result['runtime_s'],
                    final_position_m=result['final_position_m'],
                    peak_required_force_kN_train=result['peak_required_force_N_train']/1000,
                    peak_required_mechanical_power_MW_train=result['peak_required_power_W_train']/1e6,
                    mechanical_energy_to_termination_kWh_train=result['traction_mechanical_energy_J_train']/3.6e6,
                    friction_brake_energy_to_termination_kWh_train=result['friction_brake_energy_J_train']/3.6e6,
                    energy_residual_relative=result['relative_energy_residual'],
                    complete_installed_mass_kg=None, installed_capital_usd=None,
                    moving_force_available=False, hot_repeated_duty_verified=False,
                    independent_stop_verified=False, rescue_verified=False,
                    physical_accepted=False,
                )
                if architecture['driven_axles']:
                    driven_fraction=architecture['driven_axles']/24
                    row['optimistic_uniform_axle_adhesion_mu_floor']=(
                        model['acceleration_command_m_s2']/G + model['rolling_coefficient'] + grade
                    )/driven_fraction
                rows.append(row)
    brake_mu_level=((m+rotor)*model['independent_stop_target_m_s2']
                    -m*G*model['rolling_coefficient']
                    -model['constant_resistance_N_per_car'])/(m*G)
    output = dict(
        schema='osr-v07-demonstrator-propulsion-comparison/1',
        input_id=input_id, source_sha256=sources,
        parent_selected_vehicle_candidate_id=SELECTED,
        railway_selection_id=None, selected_reference_changed=False,
        scope='Local 1.5–2 km constant-grade analytical demand; no surveyed alignment or complete 30 km timetable',
        equal_assumption_mass=dict(accounted_normal_loaded_kg_per_car=m,
                                   rotating_equivalent_kg_per_car=rotor,
                                   complete_installed_kg_per_car=None,
                                   powered_wheel_added_mass_kg=None),
        service=dict(cars=6,car_length_m=17,normal_places_per_train=276,
                     nominal_offered_pphpd=8280,headway_s=120,speed_cap_m_s=20,
                     dwell_hypothesis_s=35,actual_headway_and_fleet_verified=False),
        rows=rows,
        independent_brake=dict(target_m_s2=model['independent_stop_target_m_s2'],
                               optimistic_mu_floor_level=brake_mu_level,
                               optimistic_mu_floor_2pct_downhill=brake_mu_level+.02,
                               inherited_mu_hypothesis=model['brake_mu_hypothesis'],
                               pass_inherited_mu_hypothesis=brake_mu_level<=model['brake_mu_hypothesis'],
                               full_load_fault_hot_stop_verified=False),
        test_priority='Full-scale station group plus passive fin, controlled receiving brake and protected tow before a route installation',
        physical_holds=[
            'Survey actual grade, curvature, station spacing, utilities and rescue access',
            'Measure position-dependent full-overlap thrust, force ripple, phase registration, winding R/L/flux and converter current/voltage limits',
            'Count stator groups, overlap length, feeders, return, converters, switchgear, cooling, protection, supports, wiring and maintenance envelopes',
            'Repeat launches and receiving stops at 120 s headway to hot equilibrium; test power, cooling and group faults',
            'Prove independent full-load stopping, parking, adhesion or rail-brake force, energy sink and protected tow',
            'For powered wheels, add motors, bogies, gears, inverter, supply/store, thermal mass, axle loads and local repair/cost effects',
            'Recompute complete installed vehicle/civil/fleet/energy/capital and lifecycle costs after physical selection',
        ],
        execution='completed', numerical_validity='conditional-model',
        engineering_screen='held-on-physical-measurement',
        evidence_maturity='analytical-demand', physical_accepted=False,
        manufacturing_release=False, operating_release=False,
    )
    output['evaluation_id'] = identity(output)
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--check', action='store_true')
    args=parser.parse_args()
    value=evaluate(json.loads(args.input.read_bytes()))
    raw=encoded(value)
    if args.check:
        if args.output.read_bytes()!=raw:
            raise SystemExit('Demonstrator comparison differs from current input/source')
    else:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_bytes(raw)
    print(json.dumps(dict(evaluation_id=value['evaluation_id'],rows=len(value['rows']),
                          physical_accepted=value['physical_accepted']),sort_keys=True))


if __name__=='__main__':
    main()
