"""Source-bound station launch and onboard wheel-assist demand comparison.

The wheel drive takes over at the 500 m leading-nose boundary. This is an
analytical allocation of required work, not an available-force or hardware
selection. All equipment added to the passive selected vehicle is unknown.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from math import ceil
from pathlib import Path

from engineering.design_search.architecture_demand import demand
from engineering.design_search.demonstrator_propulsion import (
    SELECTED, encoded, evaluate as demonstrator_evaluate, identity,
)
from engineering.design_search.powered_bogie_screen import _buffer_energy_kWh
from engineering.station_rail import braking, vehicle

ROOT = Path(__file__).resolve().parents[2]
BASE = 'docs/design-engine/v07-demonstrator-propulsion/'
SOURCES = (
    'engineering/design_search/station_assist_screen.py',
    'engineering/design_search/architecture_demand.py',
    'engineering/design_search/demonstrator_propulsion.py',
    'engineering/design_search/powered_bogie_screen.py',
    'engineering/station_rail/vehicle.py',
    'engineering/station_rail/braking.py',
    'engineering/development-baseline.toml',
    BASE + 'input.json', BASE + 'comparison.json', BASE + 'station-module.json',
    'docs/design-engine/v07-powered-bogie/input.json',
)


def _at_boundary(trace, position_m):
    """Interpolate cumulative work and demand at a source-change position."""
    for left, right in zip(trace, trace[1:]):
        x0, x1 = left['position_m'], right['position_m']
        if x0 <= position_m <= x1 and x1 > x0:
            fraction = (position_m-x0)/(x1-x0)
            keys = ('time_s', 'position_m', 'required_traction_power_W_train',
                    'required_traction_force_N_per_car', 'traction_mechanical_energy_J_train')
            point = {key: left[key]+fraction*(right[key]-left[key]) for key in keys}
            point['position_m'] = position_m
            return point
    raise ValueError('Source boundary absent from moving demand trace')


def _assist_trace(trace, boundary):
    point = _at_boundary(trace, boundary)
    return point, [point] + [p for p in trace if p['position_m'] > boundary and p['time_s'] > point['time_s']]


def evaluate(root=ROOT):
    root = Path(root)
    config = json.loads((root / (BASE+'input.json')).read_bytes())
    comparison_raw = (root / (BASE+'comparison.json')).read_bytes()
    comparison = json.loads(comparison_raw)
    if (config['parent_selected_vehicle_candidate_id'] != SELECTED
            or comparison['parent_selected_vehicle_candidate_id'] != SELECTED
            or encoded(demonstrator_evaluate(config, root)) != comparison_raw):
        raise ValueError('Demonstrator comparison is stale or has a different parent')
    module = json.loads((root / (BASE+'station-module.json')).read_bytes())
    if (module['parent_selected_vehicle_candidate_id'] != SELECTED
            or module['comparison_evaluation_id'] != comparison['evaluation_id']
            or module['selected_reference_changed'] is not False
            or module['physical_accepted'] is not False):
        raise ValueError('Station module ancestry or selection differs')
    primary = module['module_scope']['full_engagement_minimum_primary']
    sections = {s['section_id']: s for s in primary['sections']}
    launch = sections['departure-launch']
    if (primary['selected_vehicle_candidate_id'] != SELECTED
            or module['module_scope']['launch_command_window_m'] != [0, 500]
            or launch['installed_length_m'] <= 500):
        raise ValueError('Station launch physical stock or command boundary differs')
    model = config['model']
    if (model['cars'], model['speed_cap_m_s'], model['acceleration_command_m_s2'],
            model['independent_stop_target_m_s2'], model['headway_s']) != (6, 20, .4, .6, 120):
        raise ValueError('Fixed six-car demonstrator controls differ')
    storage = json.loads((root / 'docs/design-engine/v07-powered-bogie/input.json').read_bytes())
    if (storage['parent_selected_vehicle_candidate_id'] != SELECTED
            or storage['source_demonstrator_evaluation_id'] != comparison['evaluation_id']
            or storage['station_charge_dwell_s_hypothesis'] != 35):
        raise ValueError('Storage assumptions differ from demonstrator')
    v = vehicle.build(root)
    if v['candidate_id'] != SELECTED or v['physical_definition']['vehicle']['onboard_traction_motors'] != 0:
        raise ValueError('Selected passive parent vehicle differs')
    m = v['mass']['accounted_cap_loaded_kg_per_car']
    rotor = braking.rotating_stock(v)['equivalent_inertial_mass_kg_per_car']
    source_sha = {path: sha256((root/path).read_bytes()).hexdigest() for path in SOURCES}
    source_id = identity(dict(source_sha256=source_sha, parent=SELECTED))
    comparison_rows = []
    assist_rows = []
    for grade in (0, .02):
        for name in ('station-only', 'station-plus-midroute-booster'):
            matching = [r for r in comparison['rows'] if r['architecture'] == name
                        and r['spacing_m'] == 2000 and r['grade_up_fraction'] == grade]
            if len(matching) != 1:
                raise ValueError('Missing equal-assumption station comparison')
            row = matching[0]
            comparison_rows.append(dict(architecture=name, grade_up_fraction=grade,
                                        research_configuration_id=row['railway_research_configuration_id'],
                                        demand_id=row['demand_id'], reached=row['analytical_target_reached'],
                                        runtime_s=row['runtime_s'], reason=row['reason'],
                                        mechanical_energy_kWh_train=row['mechanical_energy_to_termination_kWh_train'],
                                        peak_mechanical_kW_train=row['peak_required_mechanical_power_MW_train']*1000))
        result = demand(2000, m, rotor, powered_windows=[[0, 2000]], cars=6,
                        speed_cap_m_s=20, acceleration_m_s2=.4, deceleration_m_s2=.6,
                        grade=grade, dt=model['dt_s'], rolling_coefficient=model['rolling_coefficient'],
                        constant_resistance_N_per_car=model['constant_resistance_N_per_car'],
                        aero_coefficient_N_s2_m2=model['aero_coefficient_N_s2_m2_per_car'])
        if result['numerical_validity'] != 'valid' or not result['reachable']:
            raise ValueError('Wheel-assist demand trajectory did not reach analytically')
        boundary, tail = _assist_trace(result['trace'], 500)
        wheel_j = result['traction_mechanical_energy_J_train'] - boundary['traction_mechanical_energy_J_train']
        if wheel_j <= 0:
            raise ValueError('Nonpositive wheel-assist work on declared leg')
        wheel_kWh = wheel_j/3.6e6
        peak_power_kW = max(p['required_traction_power_W_train'] for p in tail)/1000
        peak_force_N = max(p['required_traction_force_N_per_car'] for p in tail)*6
        eta = storage['drive_motoring_efficiency_hypothesis']
        aux_kWh = storage['auxiliary_draw_kW_train_hypothesis']*result['runtime_s']/3600
        electrical_kWh = wheel_kWh/eta + aux_kWh
        cap_kWh = _buffer_energy_kWh(tail, eta, storage['auxiliary_draw_kW_train_hypothesis'],
                                     storage['hybrid_battery_discharge_limit_kW_hypothesis'])
        legs = storage['two_leg_no_charge_reserve_count_hypothesis']
        battery_only = legs*electrical_kWh/storage['battery_usable_fraction_hypothesis']
        hybrid_battery = legs*(electrical_kWh-cap_kWh)/storage['battery_usable_fraction_hypothesis']
        hybrid_cap = legs*cap_kWh/storage['supercapacitor_usable_fraction_hypothesis']
        charge_kW = electrical_kWh*3600/(storage['station_charge_dwell_s_hypothesis']*storage['station_charge_efficiency_hypothesis'])
        axle_options = []
        for axles in (8, 12, 16, 24):
            definition = dict(parent_selected_vehicle_candidate_id=SELECTED,
                              station_primary_layout_id=primary['layout_id'],
                              station_primary_stock_evaluation_id=primary['stock_evaluation_id'],
                              architecture='station-launch-plus-onboard-wheel-assist',
                              command_window_m=[0, 500], driven_axles=axles, six_car_train=True)
            axle_options.append(dict(driven_axles=axles, research_configuration_id=identity(definition),
                                     optimistic_uniform_load_mu_floor=peak_force_N/(6*m*9.80665*axles/24),
                                     required_peak_mechanical_kW_per_driven_axle=peak_power_kW/axles,
                                     actual_adhesion_available=None, installed_motor_mass_kg=None,
                                     installed_motor_price_usd=None, selected=False))
        inherited_mu = comparison['independent_brake']['inherited_mu_hypothesis']
        minimum_axles_at_mu = ceil(peak_force_N/(6*m*9.80665*inherited_mu)*24)
        assist_rows.append(dict(grade_up_fraction=grade, demand_id=result['demand_id'],
                                source_change_nose_position_m=500, source_change_time_s=boundary['time_s'],
                                reached=result['reachable'], runtime_s=result['runtime_s'],
                                station_required_mechanical_kWh_train=boundary['traction_mechanical_energy_J_train']/3.6e6,
                                wheel_required_mechanical_kWh_train=wheel_kWh,
                                wheel_peak_mechanical_kW_train=peak_power_kW,
                                wheel_peak_required_force_kN_train=peak_force_N/1000,
                                wheel_drive_efficiency_hypothesis=eta,
                                wheel_electrical_kWh_train_hypothesis=wheel_kWh/eta,
                                auxiliary_kWh_whole_leg_hypothesis=aux_kWh,
                                station_recharge_kWh_train_hypothesis=electrical_kWh,
                                station_recharge_kW_35s_hypothesis=charge_kW,
                                battery_only_nominal_two_leg_kWh_hypothesis=battery_only,
                                hybrid_battery_limit_kW_hypothesis=storage['hybrid_battery_discharge_limit_kW_hypothesis'],
                                hybrid_cap_output_kWh_per_leg_hypothesis=cap_kWh,
                                hybrid_battery_nominal_two_leg_kWh_hypothesis=hybrid_battery,
                                hybrid_cap_nominal_two_leg_kWh_hypothesis=hybrid_cap,
                                peak_electrical_kW_train_hypothesis=peak_power_kW/eta+storage['auxiliary_draw_kW_train_hypothesis'],
                                average_drive_loss_kW_at_120s_hypothesis=(wheel_kWh/eta-wheel_kWh)*3600/120,
                                driven_axle_options=axle_options,
                                optimistic_minimum_driven_axles_if_inherited_mu_applied_to_traction=minimum_axles_at_mu,
                                inherited_mu_is_not_measured_traction_adhesion=True,
                                installed_vehicle_mass_kg=None, installed_cost_usd=None,
                                repeated_hot_duty_verified=False, physical_accepted=False))
    mass_sensitivity = []
    for added in storage['added_traction_equipment_mass_sensitivity_kg_per_car_hypothesis']:
        if added <= 0:
            raise ValueError('Positive installed-equipment mass sensitivity required')
        result = demand(2000, m+added, rotor, powered_windows=[[0, 2000]], cars=6,
                        speed_cap_m_s=20, acceleration_m_s2=.4, deceleration_m_s2=.6,
                        grade=.02, dt=model['dt_s'], rolling_coefficient=model['rolling_coefficient'],
                        constant_resistance_N_per_car=model['constant_resistance_N_per_car'],
                        aero_coefficient_N_s2_m2=model['aero_coefficient_N_s2_m2_per_car'])
        boundary, tail = _assist_trace(result['trace'], 500)
        mass_sensitivity.append(dict(added_equipment_kg_per_car_hypothesis=added,
                                     demand_id=result['demand_id'],
                                     wheel_mechanical_kWh_train=(result['traction_mechanical_energy_J_train']-boundary['traction_mechanical_energy_J_train'])/3.6e6,
                                     wheel_peak_mechanical_kW_train=max(p['required_traction_power_W_train'] for p in tail)/1000,
                                     complete_installed_mass_kg_per_car=None,
                                     physical_accepted=False))
    output = dict(schema='osr-v07-station-assist-research-screen/1',
                  source_id=source_id, source_sha256=source_sha,
                  parent_selected_vehicle_candidate_id=SELECTED,
                  comparison_evaluation_id=comparison['evaluation_id'],
                  station_module_evaluation_id=module['module_evaluation_id'],
                  station_primary_layout_id=primary['layout_id'],
                  station_primary_stock_evaluation_id=primary['stock_evaluation_id'],
                  station_primary_minimum_m=launch['installed_length_m'],
                  comparison_booster_primary_minimum_m=primary['totals']['installed_length_m'],
                  selected_reference_changed=False, baghdad_selected_changed=False,
                  scope='Synthetic 2 km level and +2% directional legs; station launch through 500 m, then onboard wheel demand to stop',
                  normal_loaded_parent_mass_kg_per_car=m,
                  rotating_equivalent_kg_per_car=rotor,
                  installed_equipment_register=[
                      dict(item='station-primary-modules-one-direction', minimum_quantity=launch['module_pieces'], actual_installed_quantity=None),
                      dict(item='station-primary-face-joints', minimum_quantity=launch['stator_face_module_joints'], actual_installed_quantity=None),
                      dict(item='station-primary-bank-ends', minimum_quantity=launch['independently_terminated_bank_ends'], actual_installed_quantity=None),
                      dict(item='motor-gear-axle-and-bogie-revisions', minimum_quantity=None, actual_installed_quantity=None),
                      dict(item='traction-inverters-and-control-electronics', minimum_quantity=None, actual_installed_quantity=None),
                      dict(item='battery-capacitor-containment-and-thermal-system', minimum_quantity=None, actual_installed_quantity=None),
                      dict(item='station-charger-grid-feeder-return-and-isolation', minimum_quantity=None, actual_installed_quantity=None),
                      dict(item='independent-brake-parking-and-wheel-slide-protection', minimum_quantity=None, actual_installed_quantity=None),
                      dict(item='train-detection-interlocking-and-fault-protection', minimum_quantity=None, actual_installed_quantity=None),
                      dict(item='rescue-energy-tow-and-access', minimum_quantity=None, actual_installed_quantity=None),
                  ],
                  comparison_rows=comparison_rows, assist_rows=assist_rows,
                  added_equipment_mass_sensitivity=mass_sensitivity,
                  independent_brake=comparison['independent_brake'],
                  installed_mass_kg=None, installed_capital_usd=None,
                  installed_cooling_and_protection=None, charging_grid_and_connector_ratings=None,
                  rescue_energy_and_force=None,
                  qualification_limits=('Station force map, phase/current/voltage and hot repeated duty; '
                                        'driven axle adhesion and motor/inverter thermal rating; storage module mass, '
                                        'charging and grid interface; installed mass/cost; independent downhill brake, '
                                        'parking and protected rescue all require separate evidence.'),
                  numerical_validity='conditional-analytical-demand',
                  engineering_accepted=False, physical_accepted=False,
                  manufacturing_release=False, operating_release=False)
    output['evaluation_id'] = identity(output)
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/(BASE+'station-assist.json'))
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    raw = encoded(evaluate())
    if args.check:
        if args.output.read_bytes() != raw:
            raise SystemExit('Station-assist screen differs from current sources')
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(raw)
    print(json.dumps(dict(evaluation_id=json.loads(raw)['evaluation_id'], physical_accepted=False), sort_keys=True))


if __name__ == '__main__':
    main()
