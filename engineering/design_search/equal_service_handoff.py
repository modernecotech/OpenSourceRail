"""Same-assumption service screen and fourteen-scope accounting bridge.

This reuses the current event-resolved demand kernel and published 30 km cost
ledger. It never transfers the old station-drive price to a changed railway.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from math import ceil, isclose, sqrt
from pathlib import Path

from engineering.design_search.architecture_demand import demand

ROOT = Path(__file__).resolve().parents[2]
LINE = 'docs/design-engine/line30-current-20261117/result.json'
LINE_MANIFEST = 'docs/design-engine/line30-current-20261117/manifest.json'
PROPULSION = 'docs/design-engine/v07-demonstrator-propulsion/comparison.json'
PROPULSION_INPUT = 'docs/design-engine/v07-demonstrator-propulsion/input.json'
CIVIL = 'docs/design-engine/v07-segmented-span/plan.json'
SOURCES = (LINE, LINE_MANIFEST, PROPULSION, PROPULSION_INPUT, CIVIL,
           'engineering/design_search/architecture_demand.py',
           'engineering/design_search/equal_service_handoff.py')


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def identity(value):
    return sha256(encoded(value)).hexdigest()


def evaluate(config, root=ROOT):
    root = Path(root)
    line = json.loads((root / LINE).read_bytes())
    manifest = json.loads((root / LINE_MANIFEST).read_bytes())
    propulsion = json.loads((root / PROPULSION).read_bytes())
    prior_input = json.loads((root / PROPULSION_INPUT).read_bytes())
    civil = json.loads((root / CIVIL).read_bytes())
    if config['schema'] != 'osr-v07-equal-service-input/1':
        raise ValueError('Explicit equal-service input required')
    selected = line['selected_reference_vehicle_candidate_id']
    if (selected != config['parent_selected_vehicle_candidate_id']
            or selected != propulsion['parent_selected_vehicle_candidate_id']
            or selected != civil['selected_vehicle_candidate_id']):
        raise ValueError('Selected vehicle identities differ')
    if manifest['evaluation_id'] != line['evaluation_id'] or sha256((root / LINE).read_bytes()).hexdigest() != manifest['files']['result.json']:
        raise ValueError('Published line benchmark identity or bytes differ')
    if line['evaluation_id'] != config['source_line_evaluation_id'] or propulsion['evaluation_id'] != config['source_propulsion_evaluation_id']:
        raise ValueError('Source evaluation differs')
    requirements = line['specification']['requirements']
    if (requirements['route_km'], requirements['stations'], requirements['trackways'],
            requirements['headway_s'], requirements['dwell_s']) != (30., 12, 2, 120., 35.):
        raise ValueError('30 km service reference differs')
    m = prior_input['model']
    if (m['speed_cap_m_s'], m['acceleration_command_m_s2'], m['independent_stop_target_m_s2']) != (20, .4, .6):
        raise ValueError('Propulsion comparison motion control differs')
    if config['design']['speed_cap_m_s'] != 20 or config['design']['acceleration_command_m_s2'] != .4:
        raise ValueError('Declared service motion differs')
    if config['design']['headway_s'] != 120 or config['design']['dwell_s'] != 35:
        raise ValueError('Declared frequency differs')
    if sorted(config['grade_magnitudes']) != [0, .01, .02]:
        raise ValueError('Grade sensitivity differs')

    base = next(v for v in line['variants'] if v['mechanism'] == line['baseline_mechanism'])
    rows = {r['key']: r for r in base['capital_lines']}
    groups = config['capital_scope_mapping']
    keys = [key for group in groups for key in group['source_line_keys']]
    if len(groups) != 14 or len(keys) != len(set(keys)) or set(keys) != set(rows):
        raise ValueError('Fourteen scopes must cover each source capital line exactly once')
    fx = line['specification']['currency']['iqd_per_usd']
    scopes = [dict(scope=g['scope'], source_line_keys=g['source_line_keys'],
                   line30_base_proxy_usd=sum(rows[k]['costs_iqd']['base'] for k in g['source_line_keys']) / fx,
                   candidate_installed_usd=None) for g in groups]
    proxy = sum(s['line30_base_proxy_usd'] for s in scopes)
    if not isclose(proxy, base['installed_capital_usd']['base'], rel_tol=1e-12, abs_tol=.01):
        raise ValueError('Capital bridge does not reconcile')
    base_fleet = base['service']['total_trainsets']
    delivered_unit_proxy = rows['delivered-and-assembled-fleet']['costs_iqd']['base'] / fx / base_fleet

    normal = propulsion['equal_assumption_mass']['accounted_normal_loaded_kg_per_car']
    rotor = propulsion['equal_assumption_mass']['rotating_equivalent_kg_per_car']
    segment = requirements['route_km'] * 1000 / (requirements['stations'] - 1)
    service = []
    for architecture in config['architectures']:
        windows = [(float(lo), float(hi) if hi != 'segment_end' else segment)
                   for lo, hi in architecture['powered_windows_m']]
        if not all(0 <= lo < hi <= segment for lo, hi in windows):
            raise ValueError('Powered window outside segment')
        research_id = identity(dict(parent_selected_vehicle_candidate_id=selected,
                                    architecture=architecture['id'], windows=windows,
                                    driven_axles=architecture['driven_axles'],
                                    supply=architecture['traction_supply_hypothesis']))
        for magnitude in config['grade_magnitudes']:
            directions = {}
            for direction, grade in (('uphill', magnitude), ('downhill', -magnitude)):
                value = demand(segment, normal, rotor, powered_windows=windows,
                               cars=6, speed_cap_m_s=20,
                               acceleration_m_s2=.4, deceleration_m_s2=.6,
                               grade=grade, dt=m['dt_s'],
                               rolling_coefficient=m['rolling_coefficient'],
                               constant_resistance_N_per_car=m['constant_resistance_N_per_car'],
                               aero_coefficient_N_s2_m2=m['aero_coefficient_N_s2_m2_per_car'])
                directions[direction] = dict(demand_id=value['demand_id'],
                    reached=value['reachable'], runtime_s=value['runtime_s'],
                    reason=value['reason'], final_position_m=value['final_position_m'],
                    mechanical_traction_kwh=value['traction_mechanical_energy_J_train'] / 3.6e6,
                    peak_required_force_kN=value['peak_required_force_N_train'] / 1000,
                    peak_required_power_MW=value['peak_required_power_W_train'] / 1e6)
            reached = all(x['reached'] for x in directions.values())
            t = config['design']
            if reached:
                one_way = {side: (requirements['stations'] - 1) * x['runtime_s'] * (1 + t['running_time_margin_fraction'])
                           + (requirements['stations'] - 2) * t['dwell_s']
                           for side, x in directions.items()}
                cycle = sum(one_way.values()) + 2 * t['terminal_turnback_s']
                active = ceil(cycle / t['headway_s'])
                reserve = ceil(active * t['fleet_reserve_fraction'])
            else:
                one_way = {'uphill': None, 'downhill': None}
                cycle = active = reserve = None
            service.append(dict(architecture=architecture['id'], research_configuration_id=research_id,
                grade_magnitude=magnitude, segment_m=segment, directions=directions,
                analytical_two_way_reach=reached, one_way_s=one_way, roundtrip_s=cycle,
                active_trainsets=active, spare_trainsets=reserve,
                total_trainsets=active + reserve if reached else None,
                line30_base_trainsets=base_fleet,
                fleet_quantity_delta_from_line30_base=(active + reserve - base_fleet) if reached else None,
                unchanged_passive_delivered_fleet_quantity_proxy_delta_usd=(
                    (active + reserve - base_fleet) * delivered_unit_proxy
                    if reached and architecture['driven_axles'] == 0 else None),
                candidate_fleet_installed_delta_usd=None,
                normal_places_per_train=276, offered_places_per_hour_direction=8280,
                annual_train_km_at_120s_if_qualified=2 * 3600 / 120 * requirements['operating_hours_per_day'] * 30 * requirements['operating_days_per_year'],
                installed_mass_complete=False, available_traction_verified=False,
                independent_stop_verified=False, actual_headway_verified=False,
                installed_capital_usd=None, whole_life_npv_usd=None))

    added = config['powered_wheel_added_mass_sensitivity_kg_per_car']
    if added != 2400:
        raise ValueError('Declared rounded powered-equipment mass sensitivity differs')
    heavier = []
    for magnitude in config['grade_magnitudes']:
        for direction, grade in (('uphill', magnitude), ('downhill', -magnitude)):
            value = demand(segment, normal + added, rotor,
                           powered_windows=[(0, segment)], cars=6,
                           speed_cap_m_s=20, acceleration_m_s2=.4,
                           deceleration_m_s2=.6, grade=grade, dt=m['dt_s'],
                           rolling_coefficient=m['rolling_coefficient'],
                           constant_resistance_N_per_car=m['constant_resistance_N_per_car'],
                           aero_coefficient_N_s2_m2=m['aero_coefficient_N_s2_m2_per_car'])
            heavier.append(dict(grade_magnitude=magnitude, direction=direction,
                demand_id=value['demand_id'], analytical_target_reached=value['reachable'],
                runtime_s=value['runtime_s'],
                peak_required_force_kN=value['peak_required_force_N_train'] / 1000,
                peak_required_mechanical_power_MW=value['peak_required_power_W_train'] / 1e6,
                mechanical_traction_kwh=value['traction_mechanical_energy_J_train'] / 3.6e6))

    train_length = base['service']['train_length_m']
    stop_min = 20**2 / (2 * .6) + 20 * config['design']['illustrative_reaction_s'] + train_length
    if not isclose(train_length, 104.5, abs_tol=.01):
        raise ValueError('Selected full-train length differs')
    civil_2km = civil['straight_span_quantities']['demonstrator_2km']
    civil_options = [dict(id='jointed-20m-two-piece', route_m=2000, two_track_beam_units=civil_2km['beam_spans'],
        piece_lifts=civil_2km['required_piece_lifts'], independent_supports=civil_2km['independent_supports'],
        bearing_units=civil_2km['bearings'], structural_midspan_joints=civil_2km['beam_spans'],
        temporary_tower_placements=civil_2km['temporary_tower_placements'], installed_cost_usd=None),
        dict(id='two-independent-10m-simply-supported', route_m=2000,
        two_track_beam_units=2 * civil_2km['beam_spans'], piece_lifts=2 * civil_2km['beam_spans'],
        independent_supports=2 * civil_2km['beam_spans'] + 2,
        bearing_units=2 * civil_2km['bearings'],
        bearing_count_hypothesis='Four bearing units per newly designed 10 m simply supported beam; new end and support details required',
        structural_midspan_joints=0,
        temporary_tower_placements=None, installed_cost_usd=None)]
    result = dict(schema='osr-v07-equal-service-decision/1',
        source_sha256={path: sha256((root / path).read_bytes()).hexdigest() for path in SOURCES},
        input_id=identity(config), selected_reference_vehicle_candidate_id=selected,
        source_line_evaluation_id=line['evaluation_id'], source_propulsion_evaluation_id=propulsion['evaluation_id'],
        physical_candidate_id=None, selection_id=None,
        same_assumption_service=dict(route_km=30, stations=12, trackways=2, cars=6, normal_places_per_train=276,
            normal_capacity_pphpd=8280, headway_s=120, dwell_s=35, speed_cap_m_s=20,
            acceleration_command_m_s2=.4, independent_stop_target_m_s2=.6,
            accounted_normal_mass_kg_per_car=normal, complete_installed_mass_kg_per_car=None,
            powered_equipment_added_mass_kg_per_car=None,
            mass_scope='Optimistic parent-account comparison floor with omitted powered equipment; neither an exact installed mass nor a certified structural lower bound',
            full_train_length_m=train_length, optimistic_full_tail_receiving_stop_minimum_m=stop_min,
            receiving_reservation_safety_accepted=False),
        service_rows=service, capital_14_scope_bridge=scopes,
        powered_wheel_mass_sensitivity=dict(added_equipment_mass_hypothesis_kg_per_car=added,
            compared_accounted_normal_mass_kg_per_car=normal + added,
            added_rotating_inertia_kg_per_car=None,
            status='Rounded preliminary equipment account; still not complete installed mass or a rated drive',
            rows=heavier),
        line30_base_installed_capital_proxy_usd=proxy,
        line30_base_30_year_npv_proxy_usd=base['whole_life_npv_usd']['base'],
        line30_base_fleet_trainsets=base_fleet,
        line30_base_delivered_trainset_unit_proxy_usd=delivered_unit_proxy,
        proxy_acceleration_m_s2=line['specification']['design']['acceleration_m_s2'],
        independent_brake_optimistic_mu_floor_2pct_downgrade=propulsion['independent_brake']['optimistic_mu_floor_2pct_downhill'],
        inherited_brake_mu_hypothesis=propulsion['independent_brake']['inherited_mu_hypothesis'],
        candidate_priced_14_scope_installed_capital_usd=None,
        candidate_priced_30_year_npv_usd=None,
        civil_2km_alternatives=civil_options,
        higher_capacity_research=dict(places_per_train_hypothesis=700,
            offered_places_per_hour_direction_arithmetic_at_120s=21000,
            theoretical_headway_s_for_8280_places_per_hour=700 * 3600 / 8280,
            headway_120s_requirement_retained=True, installed_mass_kg=None,
            axle_loads=None, actual_dwell_s=None, physical_platform_length_m=None,
            fleet_trainsets=None, installed_capital_usd=None, lifecycle_cost_usd=None),
        hold='No cost winner or installed architecture is selected: changed drive, supply/store, brake, fleet, civil and site quantities lack same-candidate supplier and physical evidence.',
        execution='completed-analytical-screen', evidence_maturity='demand-and-accounting-proxy',
        selected_reference_changed=False, physical_accepted=False, engineering_accepted=False,
        manufacturing_release=False, operating_release=False)
    result['evaluation_id'] = identity(result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    value = evaluate(json.loads(args.input.read_bytes()))
    raw = encoded(value)
    if args.check:
        if args.output.read_bytes() != raw:
            raise ValueError('Equal-service decision differs from sources')
    else:
        if args.output.exists():
            raise ValueError('Fresh output path required')
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(raw)
    print(json.dumps(dict(evaluation_id=value['evaluation_id'], rows=len(value['service_rows']),
                          physical_accepted=False), sort_keys=True))


if __name__ == '__main__':
    main()
