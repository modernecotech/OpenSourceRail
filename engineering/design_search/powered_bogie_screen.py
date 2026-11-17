"""Source-bound powered-bogie electrical/storage demand, never an accepted drive.

This uses the retained event-resolved motion demand. Hardware availability,
ratings, braking, conductor safety and prices remain supplier/test inputs.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from engineering.design_search.architecture_demand import demand
from engineering.station_rail import braking, vehicle

ROOT = Path(__file__).resolve().parents[2]
SELECTED = '756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3'
INPUT = 'docs/design-engine/v07-powered-bogie/input.json'
COMPARISON = 'docs/design-engine/v07-demonstrator-propulsion/comparison.json'
SOURCES = (
    'engineering/design_search/powered_bogie_screen.py',
    'engineering/design_search/architecture_demand.py',
    'engineering/station_rail/vehicle.py',
    'engineering/station_rail/braking.py',
    'engineering/development-baseline.toml',
    INPUT, COMPARISON,
)


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def identity(value):
    return sha256(encoded(value)).hexdigest()


def _buffer_energy_kWh(trace, efficiency, auxiliaries_kW, battery_limit_kW):
    total = 0.0
    for left, right in zip(trace, trace[1:]):
        duration = right['time_s'] - left['time_s']
        if duration <= 0:
            continue
        power_kW = (left['required_traction_power_W_train'] + right['required_traction_power_W_train']) / 2000 / efficiency + auxiliaries_kW
        total += max(0.0, power_kW - battery_limit_kW) * duration / 3600
    return total


def evaluate(config, root=ROOT):
    root = Path(root)
    if config.get('schema') != 'osr-v07-powered-bogie-screen-input/1' or config.get('parent_selected_vehicle_candidate_id') != SELECTED:
        raise ValueError('Explicit selected-parent screen input required')
    source_comparison = json.loads((root / COMPARISON).read_bytes())
    if source_comparison['evaluation_id'] != config['source_demonstrator_evaluation_id'] or source_comparison['parent_selected_vehicle_candidate_id'] != SELECTED:
        raise ValueError('Source demonstrator comparison identity differs')
    if config['spacing_m'] != [1500, 2000] or config['grade_fractions_uphill'] != [-.02, 0, .02] or config['load_cases'] != ['normal', '160-person-crowd-control']:
        raise ValueError('Declared distance, grade and load controls required')
    if config['driven_axles'] != 24 or config['motorized_bogies'] != 12:
        raise ValueError('This screen is for four driven axles per six-car train car')
    eta = config['drive_motoring_efficiency_hypothesis']
    charger_eta = config['station_charge_efficiency_hypothesis']
    soc = config['battery_usable_fraction_hypothesis']
    cap_soc = config['supercapacitor_usable_fraction_hypothesis']
    if not all(0 < x <= 1 for x in (eta, charger_eta, soc, cap_soc)):
        raise ValueError('Efficiency and usable-fraction hypotheses must be within (0,1]')
    if config['station_charge_dwell_s_hypothesis'] <= 0 or config['continuous_dc_conductor_nominal_V_hypothesis'] <= 0 or config['hybrid_battery_discharge_limit_kW_hypothesis'] <= 0:
        raise ValueError('Positive dwell, conductor voltage and battery power limit required')
    v = vehicle.build(root)
    if v['candidate_id'] != SELECTED:
        raise ValueError('Selected vehicle source differs')
    rotor = braking.rotating_stock(v)['equivalent_inertial_mass_kg_per_car']
    source_sha = {name: sha256((root / name).read_bytes()).hexdigest() for name in SOURCES}
    source_id = identity(dict(input=config, source_sha256=source_sha))
    variants = [
        ('battery-station-charge', 'Onboard traction battery plus high-power station connectors'),
        ('battery-supercapacitor-station-charge', 'Onboard battery and supercapacitors plus high-power station connectors'),
        ('rigid-overhead-dc', '24 motorized axles with roof collector and rigid overhead DC contact; separately sized rescue store'),
    ]
    configurations = []
    for name, description in variants:
        definition = dict(parent_selected_vehicle_candidate_id=SELECTED, architecture=name,
                          motorized_bogies=12, driven_axles=24,
                          traction_supply=description, conductor_nominal_V=config['continuous_dc_conductor_nominal_V_hypothesis'] if name == 'rigid-overhead-dc' else None,
                          continuous_dc_pickup=config['continuous_dc_pickup'] if name == 'rigid-overhead-dc' else None)
        configurations.append(dict(name=name, research_physical_candidate_id=identity(definition), definition=definition,
                                   selected_reference_changed=False, physical_geometry_complete=False,
                                   installed_mass_complete=False, installed_capital_usd=None,
                                   physical_accepted=False))
    rows = []
    for load in config['load_cases']:
        mass = v['mass']['accounted_cap_loaded_kg_per_car'] if load == 'normal' else v['mass']['accounted_160_control_kg_per_car']
        for spacing in config['spacing_m']:
            for grade in config['grade_fractions_uphill']:
                result = demand(spacing, mass, rotor, powered_windows=[[0, spacing]],
                                cars=6, speed_cap_m_s=20, acceleration_m_s2=.4,
                                deceleration_m_s2=.6, grade=grade, dt=.2,
                                rolling_coefficient=.0025, constant_resistance_N_per_car=50,
                                aero_coefficient_N_s2_m2=1.8)
                if result['numerical_validity'] != 'valid' or not result['reachable']:
                    raise ValueError('Powered-wheel demanded trajectory did not reach analytically')
                mech_kWh = result['traction_mechanical_energy_J_train'] / 3.6e6
                aux_kWh = config['auxiliary_draw_kW_train_hypothesis'] * result['runtime_s'] / 3600
                electrical_kWh = mech_kWh / eta + aux_kWh
                electrical_peak_kW = result['peak_required_power_W_train'] / 1000 / eta + config['auxiliary_draw_kW_train_hypothesis']
                cap_kWh = _buffer_energy_kWh(result['trace'], eta, config['auxiliary_draw_kW_train_hypothesis'],
                                             config['hybrid_battery_discharge_limit_kW_hypothesis'])
                two_legs = config['two_leg_no_charge_reserve_count_hypothesis']
                dwell_h = config['station_charge_dwell_s_hypothesis'] / 3600
                station_charge_kW = electrical_kWh / charger_eta / dwell_h
                battery_only_kWh = two_legs * electrical_kWh / soc
                hybrid_battery_kWh = two_legs * (electrical_kWh - cap_kWh) / soc
                hybrid_cap_kWh = two_legs * cap_kWh / cap_soc
                row = dict(load_case=load, accounted_loaded_mass_kg_per_car=mass,
                           complete_installed_mass_kg_per_car=None, spacing_m=spacing,
                           grade_fraction_uphill=grade, demand_id=result['demand_id'],
                           runtime_s=result['runtime_s'], peak_mechanical_kW_train=result['peak_required_power_W_train']/1000,
                           peak_traction_force_kN_train=result['peak_required_force_N_train']/1000,
                           mechanical_motoring_kWh_train=mech_kWh,
                           mechanical_friction_braking_kWh_train=result['friction_brake_energy_J_train']/3.6e6,
                           electrical_motoring_plus_aux_kWh_train_hypothesis=electrical_kWh,
                           electrical_peak_kW_train_hypothesis=electrical_peak_kW,
                           peak_mechanical_kW_per_motor=result['peak_required_power_W_train']/1000/config['driven_axles'],
                           minimum_motor_peak_rating_kW_with_margin=result['peak_required_power_W_train']/1000/config['driven_axles']*(1+config['motor_peak_rating_margin_fraction_hypothesis']),
                           traction_mu_floor_24_driven_axles_optimistic_uniform_load=.4/9.80665+.0025+grade,
                           traction_mu_floor_16_driven_axles_optimistic_uniform_load=(.4/9.80665+.0025+grade)*24/16,
                           battery_only=dict(nominal_two_leg_kWh_hypothesis=battery_only_kWh,
                                             peak_discharge_C_per_hour_hypothesis=electrical_peak_kW/battery_only_kWh,
                                             station_charge_kW_per_train_hypothesis=station_charge_kW),
                           battery_supercapacitor=dict(battery_limit_kW_hypothesis=config['hybrid_battery_discharge_limit_kW_hypothesis'],
                                                       supercapacitor_output_kWh_per_leg_hypothesis=cap_kWh,
                                                       supercapacitor_nominal_two_leg_kWh_hypothesis=hybrid_cap_kWh,
                                                       battery_nominal_two_leg_kWh_hypothesis=hybrid_battery_kWh,
                                                       supercapacitor_peak_output_kW_hypothesis=max(0, electrical_peak_kW-config['hybrid_battery_discharge_limit_kW_hypothesis']),
                                                       station_charge_kW_per_train_hypothesis=station_charge_kW),
                           rigid_overhead_dc=dict(nominal_V_hypothesis=config['continuous_dc_conductor_nominal_V_hypothesis'],
                                                        pickup=config['continuous_dc_pickup'],
                                                        peak_train_current_A_hypothesis=electrical_peak_kW*1000/config['continuous_dc_conductor_nominal_V_hypothesis'],
                                                        power_return_and_protection_rated=False,
                                                        simultaneous_trains_modelled=False,
                                                        feeder_voltage_drop_V=None,
                                                        substation_count=None,
                                                        regenerative_receptivity_tested=False,
                                                        protective_sectioning_plan_approved=False,
                                                        traction_store_required_for_normal_motoring=False,
                                                        separately_sized_rescue_store_kWh=None),
                           regenerative_credit_kWh=0, independent_braking_verified=False,
                           physical_accepted=False)
                rows.append(row)
    worst = next(r for r in rows if r['load_case']=='normal' and r['spacing_m']==2000 and r['grade_fraction_uphill']==.02)
    mass_sensitivity = []
    for added in config['added_traction_equipment_mass_sensitivity_kg_per_car_hypothesis']:
        if added <= 0:
            raise ValueError('Positive added-equipment mass sensitivity required')
        result = demand(2000, worst['accounted_loaded_mass_kg_per_car'] + added, rotor,
                        powered_windows=[[0, 2000]], cars=6, speed_cap_m_s=20,
                        acceleration_m_s2=.4, deceleration_m_s2=.6, grade=.02, dt=.2,
                        rolling_coefficient=.0025, constant_resistance_N_per_car=50,
                        aero_coefficient_N_s2_m2=1.8)
        mass_sensitivity.append(dict(added_traction_equipment_kg_per_car_hypothesis=added,
                                     resulting_accounted_mass_kg_per_car=worst['accounted_loaded_mass_kg_per_car'] + added,
                                     peak_mechanical_kW_train=result['peak_required_power_W_train']/1000,
                                     mechanical_motoring_kWh_train=result['traction_mechanical_energy_J_train']/3.6e6,
                                     complete_installed_mass_kg_per_car=None,
                                     actual_motor_cooling_store_mass_kg_per_car=None,
                                     physical_accepted=False))
    mass_targets = []
    for kg in config['storage_mass_illustration_kg']:
        mass_targets.append(dict(illustrative_pack_mass_kg=kg,
                                 battery_only_required_Wh_per_kg=worst['battery_only']['nominal_two_leg_kWh_hypothesis']*1000/kg,
                                 battery_only_required_peak_kW_per_kg=worst['electrical_peak_kW_train_hypothesis']/kg,
                                 hybrid_supercapacitor_required_Wh_per_kg=worst['battery_supercapacitor']['supercapacitor_nominal_two_leg_kWh_hypothesis']*1000/kg,
                                 hybrid_supercapacitor_required_peak_kW_per_kg=worst['battery_supercapacitor']['supercapacitor_peak_output_kW_hypothesis']/kg))
    brake_m = worst['accounted_loaded_mass_kg_per_car']
    brake_me = brake_m + rotor
    brake_required_N_train = 6*(brake_me*.6 + brake_m*9.80665*.02 - brake_m*9.80665*.0025 - 50)
    brake_mu05_available_N_train = 6*brake_m*9.80665*.05
    output = dict(schema='osr-v07-powered-bogie-electrical-screen/1', source_id=source_id,
                  source_sha256=source_sha, parent_selected_vehicle_candidate_id=SELECTED,
                  source_demonstrator_evaluation_id=config['source_demonstrator_evaluation_id'],
                  supply_research_configurations=configurations, rows=rows,
                  storage_mass_targets=mass_targets, added_equipment_mass_sensitivity=mass_sensitivity,
                  preferred_prototype_research_configuration='rigid-overhead-dc',
                  rationale='Avoid megawatt station recharging and high-C-rate traction storage on the first demonstrator; size protected rigid overhead DC, motors, independent brakes and separately bounded rescue store with suppliers.',
                  independent_2pct_downhill_stop_necessary_bound=dict(normal_load_kg_per_car=brake_m,
                      target_net_deceleration_m_s2=.6, inherited_wheel_rail_mu_hypothesis=.05,
                      required_mechanical_brake_force_N_train_conservative_low_speed=brake_required_N_train,
                      mu05_contact_force_upper_bound_N_train=brake_mu05_available_N_train,
                      additional_independent_non_wheel_contact_force_required_N_train=max(0,brake_required_N_train-brake_mu05_available_N_train),
                      track_or_rail_contact_brake_force_measured=False, full_load_fault_hot_stop_verified=False),
                  existing_service_battery_traction_available=False,
                  no_supplier_ratings_or_prices_used=True,
                  hardware_quote_items=['24 motor/gear/axle installations and bogie structural revisions',
                                        'Six traction inverter and protection groups with DC isolation',
                                        'Roof collector, rigid overhead contact, return, sectionalising, touch protection and civil attachments',
                                        'Wayside rectifier and feeder, fault containment and regenerative sink',
                                        'Independent mechanical or track brakes with wheel-slide protection',
                                        'Separately sized rescue energy, tow couplers and maintenance access'],
                  test_sequence=['Bench torque-speed/efficiency/current/thermal maps for motor, gear and inverter',
                                 'Instrumented full-load moving force and low-adhesion traction test',
                                 'Repeated 120-second duty to hot equilibrium with feeder voltage drop',
                                 'Full-load independent hot/wet downhill stop, parked hold and degraded fault stop',
                                 'Protected tow and power-loss recovery on surveyed route'],
                  outstanding=['No surveyed alignment, adhesion measurement, motor/gear/inverter rating, overhead electrical/civil design or priced quote',
                               'Roof collector/contact force, structural/electrical clearance, insulation, earthing, safe evacuation and conductor access are unqualified',
                               'Nominal-voltage current excludes feeder sag; simultaneous trains, voltage drop, substation count, protection/sectioning and regeneration receptivity remain open',
                               'Inherited 0.05 adhesion is below the necessary 0.6 m/s² downgrade brake bound; independent track or rail-contact braking and parking remain unmeasured',
                               '160-person crowd case is a structural/energy sensitivity, not an approved high-capacity service formation',
                               'Base demand predates installed motor/gear/inverter/collector/brake mass; added 0.97–2.4 t/car screen is illustrative, not a complete mass reconciliation',
                               'Regeneration excluded until receptivity and braking safety are demonstrated',
                               'No full vehicle installed mass, axle reaction, thermal envelope, lifecycle or capital ranking'],
                  numerical_validity='conditional-model', evidence_maturity='analytical',
                  engineering_screen='held-on-hardware-and-brake-evidence',
                  physical_accepted=False, manufacturing_release=False, operating_release=False)
    output['evaluation_id'] = identity(output)
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT/INPUT)
    parser.add_argument('--output', type=Path, default=ROOT/'docs/design-engine/v07-powered-bogie/screen.json')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    raw = encoded(evaluate(json.loads(args.input.read_bytes())))
    if args.check:
        if args.output.read_bytes() != raw:
            raise SystemExit('Powered-bogie screen differs from current sources')
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(raw)
    result = json.loads(raw)
    print(json.dumps(dict(evaluation_id=result['evaluation_id'], rows=len(result['rows']), physical_accepted=False), sort_keys=True))


if __name__ == '__main__':
    main()
