"""Execute the 1.5/2 km integration matrix without inventing missing plants.

Each distance and architecture materializes its own canonical physical bundle.
Demand, brake hypotheses, civil loads and manufacturing/economic quantities share
that bundle. No generated demand curve is an available motor, and a checksum is
not a measured or independently approved component qualification.
"""
from pathlib import Path
import fcntl
import gzip
import json
import time
import tomllib

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from . import design_grammar as grammar, equipped_candidates, railway_bundle
from . import railway_campaign, revision_planner, system_motion, system_inventory
from . import route_bundle, fault_response, test_readiness

PRODUCER = 'engineering/design_search/demonstration.py'
SPEC = 'campaigns/end-to-end-railway-closure.toml'
OUTPUT = 'docs/design-engine/railway-closure'
FLAGS = dict(grammar.FLAGS, physical_journey_completed=False)


def specification(root=ROOT):
    value = tomllib.loads((Path(root) / SPEC).read_text())
    fixed = dict(schema='osr-end-to-end-railway-closure/1',
                 reference_changes_allowed=False, maximum_bundle_cases=12,
                 maximum_native_jobs=0, maintain_pending_tasks=True,
                 unknown_installed_quantities_are_zero=False,
                 allow_synthetic_operating_maps=False,
                 body_families=['aluminium_frame', 'aluminium_stressed_skin', 'gfrp_semimonocoque'],
                 architecture_families=['P1', 'P4'], distances_m=[1500., 2000.],
                 loads=['empty', 'normal', 'crowd', 'adverse-normal'],
                 faults=['failed-launch', 'wayside-power-loss', 'stranded-train-recovery'])
    if any(value.get(k) != v for k, v in fixed.items()):
        raise ValueError('Changed closure scope requires an explicit evaluator revision')
    if type(value['maximum_seconds']) is not int or not 1 <= value['maximum_seconds'] <= 300:
        raise ValueError('Closure execution budget must be at most 300 seconds')
    if value['completion'] != dict(equipped_candidates=3, authenticated_inputs_required=True,
            validated_available_force_map_required=True, independent_braking_and_fault_protection_required=True,
            whole_system_quantities_and_cost_required=True, automatic_physical_acceptance_allowed=False):
        raise ValueError('Physical completion obligations cannot be relaxed')
    return value


def sources(root=ROOT):
    root = Path(root)
    result = railway_campaign.source_epoch(root)
    for name in (PRODUCER, SPEC, route_bundle.PRODUCER, equipped_candidates.PRODUCER, fault_response.PRODUCER,
                 test_readiness.PRODUCER,test_readiness.DEFINITIONS,'engineering/development_baseline/entrypoint.py'):
        result[name] = digest(root / name)
    # Every producer must execute from this source tree, including a relocated checkout.
    if digest(root / PRODUCER) != digest(__file__):
        raise ValueError('Executing closure producer differs from declared source root')
    return result


def _write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.pending')
    temporary.write_bytes(encoded(value))
    temporary.replace(path)


def _seal(value):
    value['record_id'] = identity(value)
    return value


def _read(path):
    value = json.loads(Path(path).read_bytes())
    if value.get('record_id') != identity({k: v for k, v in value.items() if k != 'record_id'}):
        raise ValueError('Modified closure record: ' + str(path))
    if any(value.get(k) is not False for k in FLAGS):
        raise ValueError('Research evidence cannot grant physical acceptance or release')
    return value


def _scenarios(spec):
    return [('empty', dict(load='empty')), ('normal', dict(load='normal')),
            ('crowd', dict(load='crowd')),
            ('adverse-normal', dict(load='normal', **spec['adverse_hypothesis']))]


def evaluate(body, bundle, spec, *, root=ROOT):
    """Calculate actual conditional demands; leave unavailable fault plants held."""
    railway_bundle.validate(bundle)
    if body['candidate_id'] != bundle['body_candidate_id']:
        raise ValueError('Body and railway composition differ')
    architecture = railway_bundle.assess_architecture(bundle)
    civil = railway_bundle.assess_civil(bundle)
    inventory = system_inventory.evaluate(body, bundle_id=bundle['bundle_id'], source_root=root,
        component_substitutions=bundle['component_substitutions'], extra_equipment_tasks=bundle['unweighed_architecture_equipment'])
    if abs(inventory['known_accounted_mass_subtotal_kg'] - bundle['mass']['accounted_tare_kg_per_car']) > 1e-6:
        raise ValueError('Inventory and journey accounted-mass scopes differ')
    motion = []
    for name, overrides in _scenarios(spec):
        value = system_motion.evaluate(bundle, scenario_overrides=overrides)
        if value['candidate_id'] != bundle['candidate_id']:
            raise ValueError('Mixed longitudinal result')
        motion.append(dict(name=name, result=value))
    propulsion = railway_campaign.propulsion(bundle, architecture)
    economics = railway_campaign.economics(bundle, inventory, architecture,
                                          propulsion, motion[1]['result'], civil)
    responses = fault_response.evaluate(bundle, root=root)
    faults = [dict(name=name, execution='not-run', engineering_screen='unknown',
                   candidate_id=bundle['candidate_id'],
                   reason='Full fault journey held: validated propulsion, brake supply/protection/recovery plant and installed train state are absent; separate conditional responses start from declared hypotheses',
                   conditional_response_matrix_id=responses['evaluation_id'],
                   independent_brake_hypotheses_id=identity(motion[1]['result']['braking']),
                   **FLAGS) for name in spec['faults']]
    observation = dict(candidate_id=bundle['candidate_id'], evaluation_id=identity(motion),
                       requirement_revision=bundle['requirement_revision'], execution='completed',
                       numerical_validity='valid', failure_class='evidence-gap', domain='propulsion',
                       diagnosis='Installed train state and validated available moving-LIM map are absent; required thrust is conditional demand')
    plan = revision_planner.plan(bundle['candidate_id'], observation, maximum_proposals=2)
    return dict(candidate_id=bundle['candidate_id'], body_candidate_id=body['candidate_id'],
                family_id=bundle['family_id'], distance_m=bundle['architecture_case']['physical_definition']['route']['station_spacing_m'],
                mass_scope=bundle['mass_scope'], architecture=architecture, propulsion=propulsion,
                inventory_evaluation_id=inventory['evaluation_id'], inventory_summary=railway_campaign._inventory_summary(inventory),
                motion=motion, faults=faults, conditional_fault_responses=responses,
                required_test_programme=test_readiness.build(bundle,root=root),civil=civil,economics=economics,
                next_experiments=plan, complete_installed_mass_kg=None, **FLAGS)


def run(root=ROOT, *, state=None, maximum_new_bundles=None):
    root = Path(root)
    spec = specification(root)
    if maximum_new_bundles is not None and (type(maximum_new_bundles) is not int or not 0 <= maximum_new_bundles <= 12):
        raise ValueError('Zero to twelve new bundles per invocation required')
    folder = Path(state) if state is not None else root / 'build/railway-closure'
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / 'campaign.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        epoch = sources(root)
        contract = dict(specification=spec, source_sha256=epoch)
        contract_id = identity(contract)
        start = time.monotonic()
        # The equipped inventory is stored once; route/load cases reference it.
        equipped_path = folder / 'equipped' / (contract_id + '.json')
        if equipped_path.is_file():
            equipped = _read(equipped_path)
            if equipped['request'] != contract:
                raise ValueError('Equipped cache source identity differs')
        else:
            equipped = _seal(dict(request=contract, output=equipped_candidates.comparison(root), **FLAGS))
            if sources(root) != epoch:
                raise ValueError('Source epoch changed during equipped generation')
            _write(equipped_path, equipped)
        rows, pending, new, reused = [], [], 0, 0
        for parent in equipped['output']['candidates']:
            body = parent['body']
            for family in spec['architecture_families']:
                for distance in spec['distances_m']:
                    bundle = route_bundle.materialize(body, family=family, distance_m=distance, root=root)
                    request = dict(bundle_definition_id=bundle['definition_id'], bundle_id=bundle['bundle_id'],
                                   equipped_record_id=equipped['record_id'], contract_id=contract_id)
                    path = folder / 'cases' / (identity(request) + '.json')
                    if path.is_file():
                        record = _read(path)
                        if record['request'] != request or record['bundle'] != bundle:
                            raise ValueError('Closure case cache differs from exact bundle request')
                        reused += 1
                    elif (maximum_new_bundles is not None and new >= maximum_new_bundles) or time.monotonic() - start >= spec['maximum_seconds']:
                        pending.append(request)
                        continue
                    else:
                        if sources(root) != epoch:
                            raise ValueError('Closure sources changed before execution')
                        value = evaluate(body, bundle, spec, root=root)
                        if sources(root) != epoch:
                            raise ValueError('Closure sources changed during execution')
                        record = _seal(dict(request=request, bundle=bundle, output=value, **FLAGS))
                        _write(path, record)
                        new += 1
                    rows.append(record)
        result = dict(schema='osr-end-to-end-railway-closure-result/1', contract=contract,
                      contract_id=contract_id, equipped_record_id=equipped['record_id'], rows=rows,
                      pending=pending, new_bundles=new, reused_bundles=reused,
                      integrated_selection=None, selected_reference_changed=False, **FLAGS)
        result['evaluation_id'] = identity({k: v for k, v in result.items() if k not in ('new_bundles', 'reused_bundles')})
        _write(folder / 'latest.json', result)
        return result


def summary(value):
    rows = [r['output'] for r in value['rows']]
    return dict(schema='osr-end-to-end-railway-closure-summary/1', evaluation_id=value['evaluation_id'],
                contract_id=value['contract_id'], evaluated_bundles=len(rows), pending_bundles=len(value['pending']),
                conditional_loading_screens=sum(len(r['motion']) for r in rows),
                fault_scenarios_held=sum(len(r['faults']) for r in rows),
                conditional_brake_response_cases=sum(len(r['conditional_fault_responses']['cases']) for r in rows),
                physical_test_families=10,executed_physical_tests=0,
                complete_equipped_candidates=0, validated_operating_maps=0,
                physically_supported_journeys=0, complete_whole_life_costs=0,
                installed_mass_kg=None, whole_life_cost_USD=None, integrated_selection=None,
                completion_status='held-for-installed-and-authenticated-physical-inputs',
                open_obligations=['Located and counted equipment, joints, wiring, protection and maintenance access',
                  'Directional material/joint laws, strength, buckling, fatigue and approved load cases',
                  'Converged and independently validated finite-position LIM map with circuit and repeated thermal duty',
                  'Independent brake hardware, precise stopping and protected failed-launch/recovery demonstrations',
                  'Site-specific beam, pier, foundation, erection, station and access design',
                  'Manufacturing/installation quotes, energy purchases, service reliability and whole-life costs'], **FLAGS)


def comparative_report(value, equipped):
    """Publish a same-contract comparison without treating demand as available performance."""
    if not isinstance(equipped, dict) or equipped.get('record_id') != value.get('equipped_record_id'):
        raise ValueError('Comparative report requires the exact equipped-candidate record')
    body_families = {}
    for parent in equipped.get('output', {}).get('candidates', []):
        body = parent.get('body', {})
        body_id = body.get('candidate_id')
        family = body.get('parameters', {}).get('family')
        if not body_id or not family or body_id in body_families:
            raise ValueError('Equipped body candidates need unique identities and declared families')
        body_families[body_id] = family

    rows = []
    seen_bundles = set()
    for record in value.get('rows', []):
        bundle, output = record['bundle'], record['output']
        if (record.get('record_id') != identity({k: v for k, v in record.items() if k != 'record_id'})):
            raise ValueError('Comparative row does not match its immutable closure record')
        if (output.get('candidate_id') != bundle.get('candidate_id')
                or output.get('body_candidate_id') != bundle.get('body_candidate_id')
                or bundle.get('body_candidate_id') not in body_families
                or bundle.get('bundle_id') in seen_bundles):
            raise ValueError('Comparative report mixes or duplicates physical candidate identities')
        seen_bundles.add(bundle['bundle_id'])

        scenario_rows = []
        for motion_record in output.get('motion', []):
            motion = motion_record['result']
            demand = motion['required_demand']
            braking = motion['braking'].get('cases', [])
            scenario_rows.append({
                'scenario_name': motion_record['name'],
                'load_case': motion.get('scenario', {}).get('load'),
                'motion_evaluation_id': motion.get('evaluation_id'),
                'demand_id': demand.get('demand_id'),
                'raw_demand_id': demand.get('raw_demand_id'),
                'execution': demand.get('execution'),
                'numerical_validity': demand.get('numerical_validity'),
                'evidence': demand.get('evidence'),
                'evidence_maturity': demand.get('evidence_maturity'),
                'demand_path_reached_target': demand.get('reachable'),
                'demand_path_runtime_s': demand.get('runtime_s'),
                'required_peak_force_N_per_car': demand.get('peak_required_force_N_per_car'),
                'required_peak_force_N_train': demand.get('peak_required_force_N_train'),
                'required_peak_power_W_per_car': demand.get('peak_required_power_W_per_car'),
                'required_peak_power_W_train': demand.get('peak_required_power_W_train'),
                'required_traction_mechanical_energy_J_per_car': demand.get('traction_mechanical_energy_J_per_car'),
                'required_traction_mechanical_energy_J_train': demand.get('traction_mechanical_energy_J_train'),
                'available_force_N_per_car': demand.get('available_force'),
                'available_force_map_id': motion.get('forward_motion', {}).get('available_motor_map_id'),
                'actual_protected_headway_s': demand.get('actual_protection_headway_s'),
                'brake_hypothesis_cases': [{
                    'case': case.get('case'),
                    'state': case.get('state'),
                    'stopping_distance_m': case.get('distance_m'),
                    'final_speed_m_s': case.get('final_speed_m_s'),
                    'disc_heat_J_per_car': case.get('disc_heat_J_per_car'),
                    'lumped_disc_temperature_C_hypothesis': case.get('lumped_disc_temperature_C_hypothesis'),
                    'friction_fade_curve_qualified': case.get('friction_fade_curve_qualified'),
                } for case in braking],
            })

        normal = next((row for row in scenario_rows if row['scenario_name'] == 'normal'), None)
        adverse = next((row for row in scenario_rows if row['scenario_name'] == 'adverse-normal'), None)
        max_force = [row['required_peak_force_N_train'] for row in scenario_rows
                     if isinstance(row['required_peak_force_N_train'], (int, float))]
        max_power = [row['required_peak_power_W_train'] for row in scenario_rows
                     if isinstance(row['required_peak_power_W_train'], (int, float))]
        civil = output.get('civil', {})
        economics = output.get('economics', {})
        architecture = output.get('architecture', {})
        propulsion = output.get('propulsion', {})
        inventory = output.get('inventory_summary', {})
        geometry_coverage = inventory.get('geometry_coverage', {})
        supply_coverage = inventory.get('supply_coverage', {})
        available_map = propulsion.get('available_force_map')
        available_map_id = (available_map if isinstance(available_map, str) else
                            available_map.get('map_id', available_map.get('evaluation_id'))
                            if isinstance(available_map, dict) else None)
        mass = bundle.get('mass', {})
        row = {
            'bundle_id': bundle['bundle_id'],
            'bundle_definition_id': bundle.get('definition_id'),
            'candidate_id': bundle['candidate_id'],
            'body_candidate_id': bundle['body_candidate_id'],
            'body_family': body_families[bundle['body_candidate_id']],
            'architecture_family': bundle.get('family_id'),
            'route_distance_m': output.get('distance_m'),
            'requirement_revision': bundle.get('requirement_revision'),
            'mass': {
                'accounted_tare_kg_per_car': mass.get('accounted_tare_kg_per_car'),
                'accounted_normal_kg_per_car': mass.get('accounted_cap_loaded_kg_per_car'),
                'accounted_160_person_control_kg_per_car': mass.get('accounted_160_control_kg_per_car'),
                'mass_scope': output.get('mass_scope'),
                'complete_installed_mass_kg': output.get('complete_installed_mass_kg'),
                'complete_installed_CG_m': bundle.get('complete_installed_CG_m'),
                'complete_installed_inertia_kg_m2': bundle.get('complete_installed_inertia_kg_m2'),
            },
            'inventory_and_manufacturing': {
                'inventory_evaluation_id': output.get('inventory_evaluation_id'),
                'known_accounted_mass_subtotal_kg': inventory.get('known_accounted_mass_subtotal_kg'),
                'geometry_coverage': {
                    'located_fraction_of_accounted_mass': geometry_coverage.get('located_fraction_of_accounted_mass'),
                    'located_stock_occurrence_count': geometry_coverage.get('located_stock_occurrences'),
                    'unknown_joint_count': len(geometry_coverage.get('unknown_joint_ids', [])),
                    'unlocated_retained_account_count': len(geometry_coverage.get('unlocated_retained_account_ids', [])),
                    'unlocated_architecture_requirement_count': len(geometry_coverage.get('unlocated_architecture_requirement_ids', [])),
                    'scope': geometry_coverage.get('scope'),
                },
                'supply_coverage': {
                    'quoted_component_count': supply_coverage.get('quoted_component_count'),
                    'components_without_price_count': len(supply_coverage.get('components_without_price', [])),
                    'lead_time_known_count': supply_coverage.get('lead_time_known_count'),
                    'known_quoted_stock_cost_subtotal_USD': supply_coverage.get('known_quoted_stock_cost_subtotal_USD'),
                    'complete_installed_CAPEX_USD': supply_coverage.get('complete_installed_CAPEX_USD'),
                    'commercial_validity_assessed': supply_coverage.get('commercial_validity_assessed'),
                },
                'assembly_interfaces': inventory.get('assembly_interfaces'),
                'quantity_summary': inventory.get('quantities'),
                'complete_installed_mass_kg': inventory.get('complete_installed_mass_kg'),
            },
            'propulsion': {
                'physical_primary_definition_id': propulsion.get('physical_primary_definition_id'),
                'required_force_N_per_car_normal': propulsion.get('required_force_N_per_car'),
                'required_peak_power_W_train_normal': propulsion.get('required_peak_power_W_train'),
                'maximum_required_force_N_train_across_declared_loads': max(max_force) if max_force else None,
                'maximum_required_power_W_train_across_declared_loads': max(max_power) if max_power else None,
                'available_force_N_per_car': None if normal is None else normal['available_force_N_per_car'],
                'available_force_map_id': available_map_id,
                'electrical_thermal_duty_verified': propulsion.get('electrical_thermal_duty_verified'),
            },
            'architecture': {
                'candidate_id': architecture.get('candidate_id'),
                'evaluation_id': architecture.get('evaluation_id'),
                'required_cycle_s': architecture.get('required_cycle_s'),
                'serial_berth_interval_bound_s': architecture.get('serial_berth_interval_bound_s'),
                'actual_protected_headway_s': architecture.get('actual_protected_headway_s'),
                'price_coverage': architecture.get('price_coverage'),
                'quantity_coefficients': architecture.get('quantity_coefficients'),
            },
            'journey_scenarios': scenario_rows,
            'comparison_indicators': {
                'normal_demand_path_runtime_s': None if normal is None else normal['demand_path_runtime_s'],
                'normal_demand_path_reached_target': None if normal is None else normal['demand_path_reached_target'],
                'adverse_demand_path_runtime_s': None if adverse is None else adverse['demand_path_runtime_s'],
                'adverse_demand_path_reached_target': None if adverse is None else adverse['demand_path_reached_target'],
            },
            'faults': [{
                'scenario': fault.get('name'),
                'execution': fault.get('execution'),
                'engineering_screen': fault.get('engineering_screen'),
                'reason': fault.get('reason'),
            } for fault in output.get('faults', [])],
            'civil_alternatives': [{
                'alternative_id': alternative.get('alternative_id'),
                'physical_civil_component_id': alternative.get('physical_civil_component_id'),
                'family': alternative.get('family'),
                'span_m': alternative.get('span_m'),
                'concrete_m3': alternative.get('concrete_m3'),
                'counted_span_mass_kg': alternative.get('total_counted_span_mass_kg'),
                'counted_steel_kg': alternative.get('counted_steel_kg'),
                'deflection_screen': alternative.get('deflection_screen'),
                'engineering_screen': alternative.get('engineering_screen'),
                'torsion_and_unequal_rail_loading_qualified': alternative.get('torsion_and_unequal_rail_loading_qualified'),
                'actual_installed_cost_USD': alternative.get('actual_installed_cost_USD'),
                'installed_mass_complete': alternative.get('installed_mass_complete'),
            } for alternative in civil.get('alternatives', [])],
            'economics': {
                'evaluation_id': economics.get('evaluation_id'),
                'quantity_coefficients': economics.get('coefficients'),
                'vehicle_installed_cost_USD': economics.get('vehicle_installed_cost_USD'),
                'wayside_installed_cost_USD': economics.get('wayside_installed_cost_USD'),
                'civil_installed_cost_USD': economics.get('civil_installed_cost_USD'),
                'actual_energy_purchase_kWh': economics.get('actual_energy_purchase_kWh'),
                'maintenance_renewal_downtime_cost_USD': economics.get('maintenance_renewal_downtime_cost_USD'),
                'whole_life_cost_USD': economics.get('whole_life_cost_USD'),
                'price_scope': economics.get('scope'),
                'outstanding_cost_tasks': economics.get('tasks'),
            },
            'engineering_risks_and_next_work': {
                'architecture_screens': architecture.get('screens'),
                'architecture_failure_reasons': architecture.get('design_failure_reasons'),
                'propulsion_tasks': propulsion.get('tasks'),
                'fault_journeys': [{
                    'scenario': fault.get('name'), 'execution': fault.get('execution'),
                    'reason': fault.get('reason'),
                } for fault in output.get('faults', [])],
                'next_experiments': output.get('next_experiments'),
            },
            'acceptance': {key: output.get(key) for key in (
                'configuration_adopted', 'engineering_accepted', 'physical_accepted',
                'manufacturing_release', 'operating_release', 'physical_journey_completed')},
        }
        row['comparison_row_id'] = identity(row)
        rows.append(row)

    rows.sort(key=lambda row: (row['body_family'], row['architecture_family'],
                               row['route_distance_m'], row['candidate_id']))
    matrix = value['contract']['specification']
    expected = len(matrix['body_families']) * len(matrix['architecture_families']) * len(matrix['distances_m'])
    if len(rows) + len(value.get('pending', [])) != expected:
        raise ValueError('Comparative report does not cover the exact body/architecture/distance matrix')
    result = {
        'schema': 'osr-candidate-journey-comparison/1',
        'closure_evaluation_id': value['evaluation_id'],
        'contract_id': value['contract_id'],
        'equipped_record_id': equipped['record_id'],
        'same_service_specification': matrix,
        'body_candidate_count': len(body_families),
        'evaluated_bundle_count': len(rows),
        'pending_bundle_count': len(value.get('pending', [])),
        'rows': rows,
        'comparison_boundary': {
            'required_demand_is_available_thrust': False,
            'demand_path_reachability_is_operating_evidence': False,
            'complete_installed_mass_required_for_physical_journey': True,
            'unknown_cost_or_mass_is_zero': False,
            'research_architecture_results_transfer_between_candidates': False,
            'selection_or_physical_acceptance_claimed': False,
        },
        **FLAGS,
    }
    result['comparison_id'] = identity(result)
    return result


def _comparison_markdown(report):
    lines = [
        '## Candidate comparison matrix',
        '',
        'Each row is one exact body/architecture/route bundle under the same closure contract. Accounted masses are partial ledger values. Required force and power summarize demand across the four declared loads; they are not supplied propulsion performance. Adverse reachability applies only to the analytical demand path. A missing force map, installed mass or whole-life cost remains unknown.',
        '',
        '| Body family | Drive family | Route | Candidate | Accounted tare kg/car | Max required force kN/train | Max required power MW/train | Adverse demand path | Available force map | Complete mass | Whole-life cost |',
        '|---|---|---:|---|---:|---:|---:|---|---|---|---|',
    ]
    for row in report['rows']:
        force = row['propulsion']['maximum_required_force_N_train_across_declared_loads']
        power = row['propulsion']['maximum_required_power_W_train_across_declared_loads']
        adverse = row['comparison_indicators']['adverse_demand_path_reached_target']
        lines.append('| {body} | {drive} | {distance:g} km | `{candidate}` | {mass} | {force} | {power} | {adverse} | {available} | {complete_mass} | {cost} |'.format(
            body=row['body_family'], drive=row['architecture_family'],
            distance=row['route_distance_m'] / 1000,
            candidate=row['candidate_id'][:12],
            mass=('unknown' if row['mass']['accounted_tare_kg_per_car'] is None else f"{row['mass']['accounted_tare_kg_per_car']:.1f}"),
            force=('unknown' if force is None else f'{force / 1000:.2f}'),
            power=('unknown' if power is None else f'{power / 1_000_000:.3f}'),
            adverse=('unknown' if adverse is None else ('reached (demand only)' if adverse else 'missed (demand only)')),
            available=('unknown' if row['propulsion']['available_force_map_id'] is None else row['propulsion']['available_force_map_id'][:12]),
            complete_mass=('unknown' if row['mass']['complete_installed_mass_kg'] is None else f"{row['mass']['complete_installed_mass_kg']:.1f}"),
            cost=('unknown' if row['economics']['whole_life_cost_USD'] is None else f"{row['economics']['whole_life_cost_USD']:.2f}"),
        ))
    lines += ['', 'The full machine-readable report preserves complete IDs, per-load force/power/energy and runtime, brake hypotheses, civil alternatives, quantity coefficients, source evaluations and acceptance flags in [comparison.json](comparison.json).', '']
    return '\n'.join(lines)


def _contract(value, root):
    current = dict(specification=specification(root), source_sha256=sources(root))
    if value.get('contract') != current or value.get('contract_id') != identity(current):
        raise ValueError('Closure contract differs from the current campaign and producer sources')


def _coverage(value, equipped, root):
    expected = []
    spec = value['contract']['specification']
    if len(equipped['output']['candidates']) != 3 or {r['body']['parameters']['family'] for r in equipped['output']['candidates']} != set(spec['body_families']):
        raise ValueError('Exactly three physically distinct equipped projections required')
    for parent in equipped['output']['candidates']:
        for family in spec['architecture_families']:
            for distance in spec['distances_m']:
                bundle = route_bundle.materialize(parent['body'], family=family, distance_m=distance, root=root)
                expected.append(dict(bundle_definition_id=bundle['definition_id'], bundle_id=bundle['bundle_id'],
                                     equipped_record_id=equipped['record_id'], contract_id=value['contract_id']))
    actual = [r['request'] for r in value['rows']] + value['pending']
    if len(expected) != 12 or len(actual) != 12 or sorted(map(identity, actual)) != sorted(map(identity, expected)):
        raise ValueError('Executed and pending requests must cover the complete disjoint twelve-bundle matrix')


def publish(root=ROOT, *, state=None, output=None):
    root = Path(root)
    folder = Path(state) if state is not None else root / 'build/railway-closure'
    value = json.loads((folder / 'latest.json').read_bytes())
    _contract(value, root)
    # Verify all immutable records before publishing their index and data.
    equipped = _read(folder / 'equipped' / (value['contract_id'] + '.json'))
    if equipped['record_id'] != value['equipped_record_id']:
        raise ValueError('Equipped parent differs')
    _coverage(value, equipped, root)
    for row in value['rows']:
        if _read(folder / 'cases' / (identity(row['request']) + '.json')) != row:
            raise ValueError('Published case differs from retained execution')
    target = Path(output) if output is not None else root / OUTPUT
    target.mkdir(parents=True, exist_ok=True)
    s = summary(value)
    comparison = comparative_report(value, equipped)
    _write(target / 'summary.json', s)
    _write(target / 'comparison.json', comparison)
    _write(target / 'source-epochs.json', sources(root))
    (target / 'cases.json.gz').write_bytes(gzip.compress(encoded(value), mtime=0))
    (target / 'equipped.json.gz').write_bytes(gzip.compress(encoded(equipped), mtime=0))
    (target / 'required-tests.json.gz').write_bytes(gzip.compress(encoded([r['output']['required_test_programme'] for r in value['rows']]),mtime=0))
    text = ('# Candidate-to-journey closure\n\n'
            f"Three distinct body definitions feed {s['evaluated_bundles']} same-candidate railway bundles "
            'over 1.5 km and 2 km, with station-only P1 and separately identified P4 recovery-drive research. '
            f"{s['conditional_loading_screens']} empty, normal, crowd and adverse loading calculations "
            'propagate accounted mass to required force, independent brake hypotheses, civil loads and quantity coefficients. '
            f"{s['fault_scenarios_held']} full fault journeys remain explicitly not-run. "
            f"{s['conditional_brake_response_cases']} separate brake-response calculations use declared initial states, "
            'command latency, pressure rise, lost channels/pressure and adhesion. Static holding and rollback are resolved '
            'without reverse propulsion from a brake command. These are unqualified hypotheses, not completed fault journeys.\n\n'
            '**Zero complete installed vehicles, validated operating maps or physically supported journeys.** '
            'These are conditional calculations. Unlocated equipment accounts, GFRP/joint properties, '
            'actual electrical/thermal duty, brake hardware, site data and prices remain open. '
            'No preferred railway or physical release is selected.\n\n'
            + _comparison_markdown(comparison) + '\n'
            'The [required test programme](required-tests.json.gz) specifies ten test families with exact candidate/component bindings, '
            'conditions, measured channels and units, prerequisites, calibration/authentication needs and criterion derivations. '
            'Physical records are unavailable for this programme revision. Every test is unexecuted, every approval limit remains unassigned, '
            'and physical changes require a new as-built identity. These plans cannot admit a solver or qualify an article.\n\n'
            'The moving-conductor LIM method is a separate numerical component experiment; '
            'its benchmark, refinement and domain limitations remain separate from operating-map admission.\n\n'
            'Run `./osr design railway demonstrate --max-bundles 12`; resume the same command for pending cases. '
            'Use `./osr design railway demonstration-publish` and '
            '`./osr design railway demonstration-verify` to regenerate/check this packet.\n\n'
            '[Summary](summary.json) · [Candidate comparison](comparison.json) · [Executed cases](cases.json.gz) · '
            '[Bodies and equipped projections](equipped.json.gz) · [Sources](source-epochs.json)\n')
    (target / 'README.md').write_text(text)
    manifest = dict(schema='osr-end-to-end-railway-closure-publication/1', evaluation_id=value['evaluation_id'],
                    sources=sources(root), files={name: digest(target / name) for name in
                    ('README.md', 'summary.json', 'comparison.json', 'source-epochs.json', 'cases.json.gz', 'equipped.json.gz','required-tests.json.gz')}, **FLAGS)
    manifest['publication_id'] = identity(manifest)
    _write(target / 'manifest.json', manifest)
    return verify(root, output=target)


def verify(root=ROOT, *, output=None):
    target = Path(output) if output is not None else Path(root) / OUTPUT
    manifest = json.loads((target / 'manifest.json').read_bytes())
    if manifest.get('publication_id') != identity({k: v for k, v in manifest.items() if k != 'publication_id'}):
        raise ValueError('Closure publication identity differs')
    if manifest['sources'] != sources(root) or any(digest(target / n) != h for n, h in manifest['files'].items()):
        raise ValueError('Closure source or payload differs')
    value = json.loads(gzip.decompress((target / 'cases.json.gz').read_bytes()))
    _contract(value, root)
    if value['evaluation_id'] != identity({k: v for k, v in value.items() if k not in ('evaluation_id', 'new_bundles', 'reused_bundles')}):
        raise ValueError('Closure evaluation differs')
    if json.loads((target / 'summary.json').read_bytes()) != summary(value):
        raise ValueError('Closure summary differs')
    equipped = json.loads(gzip.decompress((target / 'equipped.json.gz').read_bytes()))
    if equipped.get('record_id') != identity({k: v for k, v in equipped.items() if k != 'record_id'}) or equipped['record_id'] != value['equipped_record_id']:
        raise ValueError('Closure equipped evidence differs')
    comparison = json.loads((target / 'comparison.json').read_bytes())
    if (comparison != comparative_report(value, equipped)
            or comparison.get('comparison_id') != identity({k: v for k, v in comparison.items()
                                                            if k != 'comparison_id'})):
        raise ValueError('Candidate comparison does not reproduce from exact closure rows')
    _coverage(value, equipped, root)
    if equipped['request'] != value['contract'] or equipped['output'] != equipped_candidates.comparison(root):
        raise ValueError('Equipped stock and installation projection do not reproduce')
    if json.loads(gzip.decompress((target/'required-tests.json.gz').read_bytes())) != [r['output']['required_test_programme'] for r in value['rows']]:
        raise ValueError('Required test programme index differs from executed candidate records')
    bodies = {p['body']['candidate_id']: p['body'] for p in equipped['output']['candidates']}
    for row in value['rows']:
        if row.get('record_id') != identity({k: v for k, v in row.items() if k != 'record_id'}):
            raise ValueError('Closure case identity differs')
        railway_bundle.validate(row['bundle'])
        if row['request'] != dict(bundle_definition_id=row['bundle']['definition_id'], bundle_id=row['bundle']['bundle_id'],
                                  equipped_record_id=equipped['record_id'], contract_id=value['contract_id']):
            raise ValueError('Closure case dependency request differs')
        if row['output'] != evaluate(bodies[row['bundle']['body_candidate_id']], row['bundle'], value['contract']['specification'], root=root):
            raise ValueError('Closure calculation does not reproduce')
    if any(manifest.get(k) is not False or value.get(k) is not False for k in FLAGS):
        raise ValueError('Closure cannot grant physical acceptance')
    if sources(root) != manifest['sources']:
        raise ValueError('Closure sources changed during verification')
    return dict(publication_id=manifest['publication_id'], **summary(value))
