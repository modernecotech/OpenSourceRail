"""Active passive-vehicle priority, separate from retained drivetrain studies."""
from itertools import product
from pathlib import Path
import argparse
import gzip
import io
import json
import time
import tomllib

from engineering.development_baseline import selection
from engineering.station_rail import ROOT, braking
from engineering.station_rail.common import digest, encoded, identity
from . import architecture_demand, launch_options, propulsion_layout, requirement_policy, sparse_launch

PRODUCER = 'engineering/design_search/station_accelerators.py'
SPEC = 'campaigns/station-accelerator-development.toml'
OUTPUT = 'docs/design-engine/station-accelerators'
FLAGS = propulsion_layout.FLAGS


def specification(root=ROOT):
    s = tomllib.loads((Path(root) / SPEC).read_text())
    a, p, c = s['architecture'], s['priority'], s['comparison']
    if (s['schema'] != 'osr-station-accelerator-priority/1' or s['purpose'] != 'next-experiment'
            or s['active_priority'] != 'passive-bogie-sparse-wayside-acceleration'
            or s['reference_changes_allowed'] is not False or s['native_dispatch'] is not False):
        raise ValueError('Explicit passive-wayside research priority required')
    if (a['passive_bogies_only'] is not True or type(a['onboard_powered_axles']) is not int
            or a['onboard_powered_axles'] != 0 or type(a['onboard_traction_motors']) is not int
            or a['onboard_traction_motors'] != 0 or a['onboard_traction_store_allowed'] is not False
            or a['auxiliary_and_essential_power_retained'] is not True
            or a['independent_service_emergency_parking_brakes_retained'] is not True):
        raise ValueError('No onboard traction; retain independent services and brakes')
    if (p['onboard_drive_studies'] != 'retained-secondary-research-comparisons'
            or p['physical_acceptance'] is not False or p['whole_life_winner'] is not False
            or p['site_count_and_length_are_revisable'] is not True
            or p['detailed_target_requests'] != 'lead-layout-only'):
        raise ValueError('Research priority cannot promote acceptance or fixed universal geometry')
    if (type(s['maximum_seconds']) is not int or not 1 <= s['maximum_seconds'] <= 120
            or type(s['maximum_layouts']) is not int or not 1 <= s['maximum_layouts'] <= 6
            or not 1 <= len(s['layouts']) <= s['maximum_layouts']):
        raise ValueError('Bounded layout experiment required')
    names = [row['name'] for row in s['layouts']]
    if len(set(names)) != len(names) or names.count(p['lead_layout']) != 1:
        raise ValueError('One named lead research layout required')
    if any(not 1 <= len(row['starts_m']) <= 8 for row in s['layouts']):
        raise ValueError('Bounded bank counts required; this is not a universal railway limit')
    fixed_context = dict(speed_m_s=20., acceleration_m_s2=.4, service_deceleration_m_s2=.6,
                         launch_command_m=500., headway_target_s=120., dwell_s=35.)
    if any(c.get(key) != expected for key, expected in fixed_context.items()):
        raise ValueError('Fixed reference-motion experiment differs; revise its reports and fault contexts explicitly')
    if (any(not propulsion_layout.positive(c[k]) for k in ('speed_m_s', 'acceleration_m_s2',
            'service_deceleration_m_s2', 'launch_command_m', 'headway_target_s', 'dwell_s'))
            or c['launch_command_m'] != c['speed_m_s']**2 / (2 * c['acceleration_m_s2'])
            or set(c['loads']) != {'empty', 'normal', 'crowd-control'} or len(c['loads']) != 3
            or not c['station_spacing_m'] or len(c['station_spacing_m']) > 3
            or len(set(c['station_spacing_m'])) != len(c['station_spacing_m'])
            or any(not propulsion_layout.positive(x) for x in c['station_spacing_m'])
            or not c['grade_fraction'] or len(c['grade_fraction']) > 3
            or len(set(c['grade_fraction'])) != len(c['grade_fraction'])
            or any(type(x) not in (int, float) or not -.02 <= x <= .02 for x in c['grade_fraction'])):
        raise ValueError('Explicit bounded loading and target-motion contexts required')
    return s


def _geometry(layout, launch_distance, initial_nose):
    return sparse_launch.geometry(layout['starts_m'], layout['bank_length_m'],
                                 initial_nose_m=initial_nose, launch_distance_m=launch_distance)


def _demand(geometry, mass_per_car, rotor_per_car, distance, grade, c):
    return architecture_demand.demand(distance, mass_per_car, rotor_per_car,
        powered_windows=geometry['required_launch_contact_union_m'], cars=6,
        speed_cap_m_s=c['speed_m_s'], acceleration_m_s2=c['acceleration_m_s2'],
        deceleration_m_s2=c['service_deceleration_m_s2'], grade=grade)


def _reference_interfaces(vehicle):
    definition = vehicle['physical_definition']
    body, motor = definition['vehicle'], definition['propulsion']
    if (body['cars'] != 6 or body['body_length_m'] != 17 or body['coupling_gap_m'] != .5
            or body['onboard_traction_motors'] != 0 or body['onboard_traction_battery_kWh'] != 0
            or definition['support']['family'] != 'two-passive-two-axle-bogies-per-car'
            or vehicle['support_counts']['bogies_per_train'] != 12
            or motor['secondary_length_m'] != 9
            or motor['all_powered_traction_equipment_wayside'] is not True):
        raise ValueError('Reference interfaces differ; revise the passive six-car experiment explicitly')


def _valid_hash(value):
    return (isinstance(value, str) and len(value) == 64 and
            all(char in '0123456789abcdef' for char in value))


def _fixed_bank_force_contract(*, layout, physical_option_id, geometry, evaluation_id,
                                priority_id, reference_vehicle_candidate_id,
                                target_demands):
    """Bind every installed research bank to its missing operating evidence.

    This is a fail-closed evidence contract, not a force model. It records the
    exact geometry and required demand contexts while leaving force, electrical
    limits, heat and installed quantities unknown until an exact component map
    and validation evidence are supplied.
    """
    starts = layout['starts_m']
    length = layout['bank_length_m']
    if (not starts or len(starts) != geometry['site_count'] or
            not propulsion_layout.positive(length) or
            not _valid_hash(physical_option_id) or not _valid_hash(evaluation_id) or
            not _valid_hash(priority_id) or not _valid_hash(reference_vehicle_candidate_id) or
            not _valid_hash(geometry.get('physical_geometry_id'))):
        raise ValueError('Exact fixed-bank physical and evaluation identities required')
    if any(not propulsion_layout.positive(start) for start in starts):
        raise ValueError('Positive fixed-bank start positions required')

    required = [
        'exact_primary_component_and_winding_geometry',
        'phase_sequence_and_electrical_grouping_per_bank',
        'position_speed_overlap_airgap_force_current_and_voltage_maps',
        'converter_current_voltage_frequency_and_protection_limits',
        'switching_commutation_and_interbank_phase_handoff',
        'primary_and_secondary_losses_temperature_and_repeated_duty_cooling',
        'receiving_extent_independent_braking_and_protected_recovery',
        'supports_feeders_transformer_cabling_and_complete_installed_quantities',
        'supplier_price_origin_lead_time_maintenance_and_replacement_scope',
        'independent_numerical_validation_and_physical_correlation',
    ]
    banks = []
    for index, start in enumerate(starts):
        bank_geometry = dict(index=index, start_m=start, length_m=length,
            physical_geometry_id=geometry['physical_geometry_id'],
            installed_extent_m=[start, start + length])
        bank = dict(bank_id=identity(dict(physical_option_id=physical_option_id,
                bank_geometry=bank_geometry)), **bank_geometry,
            physical_option_id=physical_option_id,
            exact_primary_component_id=None,
            electrical_group_id=None,
            phase_registration=None,
            force_map_id=None,
            available_force_N=None,
            converter_voltage_limit_V=None,
            converter_current_limit_A=None,
            operating_frequency_Hz=None,
            primary_loss_W=None,
            secondary_loss_W=None,
            cooling_capacity_W=None,
            maximum_operating_temperature_C=None,
            repeated_duty=None,
            installed_mass_kg=None,
            installed_cost_IQD=None,
            installed_cost_USD=None,
            source_ids=[],
            status='held',
            missing_evidence=list(required))
        bank['bank_record_id'] = identity(bank)
        banks.append(bank)

    scenarios = []
    for demand in target_demands:
        context = dict(load=demand['load'], distance_m=demand['distance_m'],
            grade_fraction=demand['grade_fraction'])
        scenario = dict(scenario_id=identity(dict(physical_option_id=physical_option_id,
                context=context, evaluation_id=evaluation_id)),
            **context,
            evaluation_id=evaluation_id,
            required_train_force_N=demand['result']['peak_required_force_N_train'],
            required_mechanical_power_W=demand['result']['peak_required_power_W_train'],
            actual_available_force_N=None,
            actual_electrical_input_W=None,
            position_resolved_bank_allocation=None,
            force_map_id=None,
            comparison='held-missing-force-map')
        scenarios.append(scenario)

    contract = dict(schema='osr-fixed-bank-lim-force-contract/1',
        purpose='candidate-bound-evidence-closure; not an operating-force-map',
        reference_vehicle_candidate_id=reference_vehicle_candidate_id,
        materialized_candidate_id=None,
        physical_option_id=physical_option_id,
        physical_geometry_id=geometry['physical_geometry_id'],
        priority_id=priority_id,
        evaluation_id=evaluation_id,
        active_bank_count=len(banks),
        installed_bank_length_m=length,
        installed_primary_length_m=geometry['summed_bank_length_m'],
        force_map_id=None,
        available_force_map_admitted=False,
        transferred_moving_lim_force_data=False,
        separate_moving_lim_study='docs/design-engine/moving-lim-method/assessment.json',
        required_evidence=required,
        banks=banks,
        demand_scenarios=scenarios,
        status='held',
        physical_acceptance=False,
        engineering_acceptance=False,
        native_evaluator_admission=False,
        selected_reference_changed=False,
        operating_release=False,
        configuration_adopted=False,
        manufacturing_release=False,
        physical_journey_completed=False)
    contract['contract_id'] = identity(contract)
    return contract


def compare(root=ROOT):
    root = Path(root).resolve()
    started = time.monotonic()
    spec = specification(root)
    reference = selection.load(root)
    vehicle = reference['vehicle']
    _reference_interfaces(vehicle)
    rotor = braking.rotating_stock(vehicle)['equivalent_inertial_mass_kg_per_car']
    c = spec['comparison']
    initial = 6 * 17 + 5 * .5
    priority_id = identity(dict(architecture=spec['architecture'], priority=spec['active_priority'],
                               purpose=spec['purpose'], comparison=c))
    masses = dict(empty=vehicle['mass']['accounted_tare_kg_per_car'],
        normal=vehicle['mass']['accounted_cap_loaded_kg_per_car'],
        **{'crowd-control': vehicle['mass']['accounted_160_control_kg_per_car']})
    requested = launch_options.bounds(6 * masses['normal'], 6 * rotor, c['speed_m_s'], c['acceleration_m_s2'])
    rows, pending = [], []
    for index, layout in enumerate(spec['layouts']):
        if time.monotonic() - started > spec['maximum_seconds']:
            pending = spec['layouts'][index:]
            break
        geometry = _geometry(layout, c['launch_command_m'], initial)
        physical = dict(parent_reference_vehicle_id=vehicle['candidate_id'],
            parent_support_component_id=vehicle['support_component_id'],
            installed_primary_geometry_id=geometry['physical_geometry_id'],
            passive_secondary=dict(length_m=9., setback_m=4., pitch_m=17.5,
                                   primary_winding_and_material_definition=None),
            passive_bogies=12, powered_bogies=0, onboard_traction_motors=0,
            onboard_traction_battery_kWh=0., onboard_traction_supercapacitors=0,
            auxiliary_and_independent_braking_retained=True, complete_installed_geometry=False)
        physical_id = identity(physical)
        demands = [dict(load=load, distance_m=distance, grade_fraction=grade,
            result=_demand(geometry, masses[load], rotor, distance, grade, c))
            for load, distance, grade in product(c['loads'], c['station_spacing_m'], c['grade_fraction'])] if layout['name'] == spec['priority']['lead_layout'] else []
        faults = []
        if layout['name'] == spec['priority']['lead_layout']:
            for disabled in range(len(layout['starts_m'])):
                active = dict(layout, starts_m=[p for i,p in enumerate(layout['starts_m']) if i != disabled])
                diagnostic = _geometry(active, c['launch_command_m'], initial)
                fault = dict(installed_physical_option_id=physical_id,
                    installed_primary_geometry_id=geometry['physical_geometry_id'],
                    installed_primary_extent_m=geometry['summed_bank_length_m'],
                    disabled_site_index=disabled, active_subset_is_installed_geometry=False,
                    target_distance_m=2000., target_load='normal', target_grade_fraction=0.,
                    active_contact_diagnostic=diagnostic,
                    departure_readiness='hold' if not diagnostic['initial_geometric_overlap'] else 'requires-qualified-degraded-operation',
                    target_demand=_demand(diagnostic, masses['normal'], rotor, 2000., 0., c),
                    recovery='independent safe stopping and protected external rescue/tow; no onboard traction credited', **FLAGS)
                fault['fault_evaluation_id'] = identity(fault)
                faults.append(fault)
        final_active = geometry['breakpoint_records'][-1]['active_sites']
        rows.append(dict(name=layout['name'], role=layout['role'], physical_definition=physical,
            physical_option_id=physical_id, materialized_candidate_id=None, geometry=geometry,
            target_demands=demands, fault_evaluations=faults,
            target_demand_scope='lead-layout-only; other layouts retain geometric comparisons',
            required_normal_launch=requested,
            necessary_force_at_one_final_active_site_N=None if not final_active else requested['required_body_drive_or_shaft_effort_N'] / final_active,
            available_force_map_id=None, actual_installed_mass_kg=None, installed_cost_USD=None,
            powered_receiving_extent_m=None, actual_brake_and_rescue_qualified=False,
            independent_power_and_shared_cabinet_design=None, **FLAGS))
    sources = {**reference['source_sha256'], **vehicle['source_sha256']}
    for name in (PRODUCER, SPEC, OUTPUT + '/README.md', 'engineering/design_search/sparse_launch.py',
        'engineering/design_search/architecture_demand.py', 'engineering/design_search/launch_options.py',
        'engineering/design_search/propulsion_layout.py', 'engineering/design_search/storage.py',
        'engineering/design_search/requirement_policy.py', 'engineering/station_rail/braking.py', 'engineering/requirements.txt'):
        sources[name] = digest(root / name)
    if digest(root / PRODUCER) != digest(__file__):
        raise ValueError('Executing priority producer differs from source tree')
    value = dict(schema='osr-station-accelerator-result/1', priority_id=priority_id,
        active_priority=spec['active_priority'], purpose='next-experiment',
        execution='interrupted-budget' if pending else 'completed', pending_layouts=pending,
        reference_candidate_id=vehicle['candidate_id'], reference_selection_id=reference['selection_id'],
        lead_research_layout_name=spec['priority']['lead_layout'], physical_selection_id=None,
        integrated_selection=None, onboard_traction_equipment_allowed=False,
        station_energy_buffer='optional offboard equipment; no capacity, loss or price credited',
        old_powered_bogie_studies='retained-secondary-research-comparisons',
        specification=spec, layouts=rows, requirement_policy=requirement_policy.assess({}),
        sources_sha256=dict(sorted(sources.items())), source_sha256=dict(sorted(sources.items())),
        budget_note='Bounded target-demand/geometry requests, never available-force journeys', **FLAGS)
    for row in rows:
        row['evaluation_id'] = identity(dict(physical_option_id=row['physical_option_id'],
            priority_id=priority_id, source_sha256=sources, target_demands=row['target_demands'], faults=row['fault_evaluations']))
        if row['name'] == spec['priority']['lead_layout']:
            layout = next(item for item in spec['layouts'] if item['name'] == row['name'])
            row['fixed_bank_force_contract'] = _fixed_bank_force_contract(
                layout=layout,
                physical_option_id=row['physical_option_id'],
                geometry=row['geometry'],
                evaluation_id=row['evaluation_id'],
                priority_id=priority_id,
                reference_vehicle_candidate_id=vehicle['candidate_id'],
                target_demands=row['target_demands'])
        else:
            row['fixed_bank_force_contract'] = None
    value['study_id'] = identity(value)
    return value


def summary(value):
    lead = next((row for row in value['layouts'] if row['name'] == value['lead_research_layout_name']), None)
    return dict(study_id=value['study_id'], priority_id=value['priority_id'], execution=value['execution'],
        active_priority=value['active_priority'], layouts=len(value['layouts']), pending_layouts=len(value['pending_layouts']),
        lead_research_layout_name=value['lead_research_layout_name'],
        lead_primary_extent_m=None if lead is None else lead['geometry']['summed_bank_length_m'],
        onboard_traction_equipment_allowed=False, integrated_selection=None, **FLAGS)


def report(value):
    text = ['# Passive wayside accelerator findings', '',
        'Active direction: passive bogies and reaction fins; all traction equipment stays wayside. Powered-bogie studies are retained comparisons.', '',
        '| Layout | Sites | Bank length | Active primary extent | Min summed overlap | Worst single-fin overlap | 500 m coverage |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for row in value['layouts']:
        g = row['geometry']
        text.append(f"| {row['name']} | {g['site_count']} | {g['physical_geometry']['bank_length_m']:g} m | {g['summed_bank_length_m']:g} m | {g['min_sum_overlap_m']:g} m | {g['longest_single_fin_min_m']:g} m | {g['geometric_covered_m']:g} m |")
    text += ['', 'These are geometric quantities, not thrust or installed-price reductions. At some positions a single bank must meet the whole train demand. The final active bank in the normal 72 km/h request requires about 66.6 kN and 1.33 MW mechanical; electrical input remains unknown.', '',
        '## Leading-layout faults', '',
        '| Disabled site | Geometric uncovered travel | Initial overlap | Departure readiness |',
        '|---:|---:|---|---|']
    for row in value['layouts']:
        if row['name'] != value['lead_research_layout_name']:
            continue
        for fault in row['fault_evaluations']:
            g = fault['active_contact_diagnostic']
            text.append(f"| {fault['disabled_site_index'] + 1} | {g['geometric_uncovered_m']:g} m | {g['initial_geometric_overlap']} | {fault['departure_readiness']} |")
    contract = next(row['fixed_bank_force_contract'] for row in value['layouts']
                    if row['name'] == value['lead_research_layout_name'])
    text += ['', '## Candidate-bound fixed-bank force contract', '',
        f"The five-bank layout is bound to a separate evidence contract (`{contract['contract_id']}`) with {contract['active_bank_count']} installed bank records and {len(contract['demand_scenarios'])} demand contexts.", '',
        '| Bank | Start | Length | Component ID | Force-map ID | Available force | Status |',
        '|---:|---:|---:|---|---|---:|---|']
    for bank in contract['banks']:
        text.append(f"| {bank['index'] + 1} | {bank['start_m']:g} m | {bank['length_m']:g} m | unknown | unknown | unknown | {bank['status']} |")
    text += ['',
        'Required force in each target-demand context is retained separately from available force; no geometry-derived thrust is admitted. The exact primary/winding, electrical groups, phase handoff, converter limits, heat/cooling duty, receiving/braking, installation quantities, prices and physical correlation are still required. The moving-LIM component study remains a separate 12.5 m/9 m configuration and is not transferred into this five-bank contract.', '']
    text += ['', 'Failed banks remain installed: no mass, stock or price is removed. A middle contact gap does not prove the train stops there; its motion and safe stopping require a validated force/brake model. An unavailable initial bank prohibits self-launch in the specified berth.', '',
        'Required next work: one/two-fin nonlinear position/force/current/thermal maps; current-control handoff; train-level fin/hanger/coupler load paths; receiving and independent braking; protection, external rescue and complete installation quotations.', '',
        f"Study identity: `{value['study_id']}`.", '']
    return '\n'.join(text)


def layout_figure(value):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    layout = next(row for row in value['specification']['layouts'] if row['name'] == value['lead_research_layout_name'])
    with matplotlib.rc_context():
        plt.rcdefaults()
        matplotlib.rcParams.update({'svg.hashsalt': value['study_id'], 'font.family': 'DejaVu Sans'})
        fig, axis = plt.subplots(figsize=(11, 2.8))
        axis.axvspan(0, 104.5, color='#e6edf1', alpha=.8)
        for car in range(6):
            front = 104.5 - 17.5 * car
            axis.add_patch(Rectangle((front - 17, 1.1), 17, .35, facecolor='#879da7', edgecolor='white'))
            axis.add_patch(Rectangle((front - 13, .78), 9, .10, facecolor='#227b91'))
        for index, start in enumerate(layout['starts_m']):
            axis.add_patch(Rectangle((start, .30), layout['bank_length_m'], .18, facecolor='#23794b'))
            axis.text(start + layout['bank_length_m']/2, .12, str(index + 1), ha='center', fontsize=9)
        axis.text(52.25, 1.57, 'Passive train at departure', ha='center', fontsize=9)
        axis.annotate('', xy=(604.5, 1.8), xytext=(104.5, 1.8), arrowprops={'arrowstyle':'->', 'color':'#384f60'})
        axis.text(354.5, 1.94, '500 m forward nose travel', ha='center', fontsize=10)
        axis.text(620, 1.22, 'Passive cars', ha='right', fontsize=9, color='#536a76')
        axis.text(620, .78, 'Passive fins', ha='right', fontsize=9, color='#227b91')
        axis.text(620, .32, 'Fixed primary banks', ha='right', fontsize=9, color='#23794b')
        axis.set(xlim=(-5, 630), ylim=(0, 2.2), yticks=[], xlabel='Along track from the berthed train rear (m)')
        axis.set_title('Passive vehicle, separate wayside accelerators: longitudinal schematic', loc='left', fontsize=12)
        axis.spines[['left','right','top']].set_visible(False)
        fig.tight_layout()
        output = io.BytesIO()
        fig.savefig(output, format='svg', metadata={'Date':None, 'Creator':'OpenSourceRail'})
        plt.close(fig)
    return b'\n'.join(line.rstrip() for line in output.getvalue().splitlines()) + b'\n'


def publish(root=ROOT):
    root = Path(root)
    value = compare(root)
    retained = propulsion_layout.retain(root, value)
    if value['execution'] != 'completed':
        return dict(published=False, retained_run=retained.relative_to(root).as_posix(), **summary(value))
    target = root / OUTPUT
    launch_options._write(target / 'comparison.json.gz', gzip.compress(encoded(value), mtime=0))
    launch_options._write(target / 'findings.md', report(value).encode())
    launch_options._write(target / 'layout.svg', layout_figure(value))
    manifest = dict(schema='osr-station-accelerator-publication/1', study_id=value['study_id'],
        priority_id=value['priority_id'], sources_sha256=value['sources_sha256'],
        files_sha256={name:digest(target / name) for name in ('comparison.json.gz', 'findings.md', 'layout.svg')}, **FLAGS)
    manifest['manifest_id'] = identity(manifest)
    launch_options._write(target / 'manifest.json', encoded(manifest))
    return dict(published=True, **summary(value))


def verify(root=ROOT):
    root = Path(root)
    value = compare(root)
    if value['execution'] != 'completed':
        propulsion_layout.retain(root, value)
        raise ValueError('Station priority verification interrupted; pending work retained')
    target = root / OUTPUT
    manifest = json.loads((target / 'manifest.json').read_bytes())
    if (value['execution'] != 'completed' or manifest.get('schema') != 'osr-station-accelerator-publication/1'
            or manifest.get('manifest_id') != identity({k:v for k,v in manifest.items() if k != 'manifest_id'})
            or manifest.get('study_id') != value['study_id'] or manifest.get('priority_id') != value['priority_id']
            or manifest.get('sources_sha256') != value['sources_sha256']
            or manifest.get('files_sha256') != {name:digest(target / name) for name in ('comparison.json.gz', 'findings.md', 'layout.svg')}
            or any(manifest.get(k) is not v for k,v in FLAGS.items())
            or gzip.decompress((target / 'comparison.json.gz').read_bytes()) != encoded(value)
            or (target / 'findings.md').read_text() != report(value)
            or (target / 'layout.svg').read_bytes() != layout_figure(value)):
        raise ValueError('Station priority source, payload or non-promoting disposition differs')
    return dict(verified=True, **summary(value))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('plan', 'compare', 'publish', 'verify'))
    action = parser.parse_args().action
    if action == 'plan':
        value = specification()
    elif action == 'compare':
        result = compare()
        propulsion_layout.retain(ROOT, result)
        value = summary(result)
    else:
        value = globals()[action]()
    print(json.dumps(value, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
