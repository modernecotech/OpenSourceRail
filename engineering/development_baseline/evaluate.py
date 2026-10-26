"""Current development selection over frozen, source-bound physical evaluators.

The selected service is a 72 km/h retained-stop proposal.  Earlier 54 km/h
station fixtures remain comparisons; neither proposal grants operating release.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json

from engineering.comfort_design import interfaces as interface_model
from engineering.comfort_design import service as service_model
from engineering.comfort_design import system_tradeoff
from . import ROOT, FLAGS
from . import selection

SCHEMA = 'osr-current-development-evaluation/1'
PRODUCERS = ('engineering/development_baseline/__init__.py',
             'engineering/development_baseline/selection.py',
             'engineering/development_baseline/evaluate.py')


def encoded(value):
    return selection.encoded(value)


def identity(value):
    return selection.identity(value)


def _merge(*mappings):
    result = {}
    for mapping in mappings:
        for name, digest in mapping.items():
            if name in result and result[name] != digest:
                raise ValueError('mixed source revisions: ' + name)
            result[name] = digest
    return dict(sorted(result.items()))


def sources(root=ROOT):
    root = Path(root).resolve()
    result = {}
    for name in PRODUCERS:
        executed = Path(__file__).with_name(Path(name).name).read_bytes()
        path = root / name
        if path.is_symlink() or path.read_bytes() != executed:
            raise ValueError('executed current producer differs from source root: ' + name)
        result[name] = sha256(executed).hexdigest()
    return result


def _fleet(network, root):
    """The current fleet and winding quantities use the same retained-stop plan."""
    source = json.loads((Path(root) / service_model.CITY).read_bytes())
    original = {r['line']: r for r in source['lines']}
    lines = []
    for row in network['lines']:
        old = original[row['line']]
        lines.append(dict(line=row['line'], retained_total_trainsets=old['fleet']['total'],
            retained_headway_s=old['selected_peak_headway_seconds'], proposed_headway_s=120.,
            proposed_peak_trainsets=row['peak_trainsets'], proposed_spare_trainsets=row['spare_trainsets'],
            proposed_cold_reserve_trainsets=row['cold_reserve'], proposed_total_trainsets=row['total_trainsets'],
            calculated_circuit_s=row['circuit_s'], failed_mainline_events=deepcopy(row['coast_failures']),
            station_library_counts=deepcopy(row['station_library_counts']),
            required_winding_library_counts_per_mainline_circuit=deepcopy(row['station_library_counts']),
            total_required_direction_winding_m_per_mainline_circuit=row['direction_winding_m'],
            directional_winding_intervals=deepcopy(row['directional_winding_intervals']),
            motor_interval_overlap_count=row['motor_interval_overlap_count'],
            additional_passenger_station_sites=0, terminal_timing_reused_not_qualified=True,
            actual_trainset_price_USD=None, complete_city_service_qualified=False))
    return dict(city='Baghdad', scope='Retained fourteen-line analytical service proposal; other cities are separate current city packages',
        network_proposal_id=network['proposal_id'], realized_network_id=network['realized_network_id'],
        lines=lines, retained_total_trainsets=source['totals']['trainsets'],
        proposed_total_trainsets=network['total_trainsets'], total_trainsets=network['total_trainsets'],
        station_library_counts=deepcopy(network['station_library_counts']),
        station_winding_library_m=list(system_tradeoff.LIBRARY),
        total_direction_winding_m=network['total_direction_winding_m'],
        additional_passenger_station_sites=network['additional_line_stop_sites'],
        lines_with_unreachable_mainline_events=network['lines_with_unreachable_events'],
        motor_overlap_count=network['motor_overlap_count'],
        overlapping_motor_hardware_or_phase_handoff_qualified=False,
        operating_reserve_fraction_hypothesis=.12, terminal_cold_reserve_per_line_hypothesis=1,
        all_lines_qualified=False, actual_fleet_purchase_cost_USD=None,
        cost_claim='Trainset prices, revised depots, charging, crews, renewals and financing remain unpriced.')


def _current_service(selected, root):
    car, brief = selected['vehicle'], selected['selection']['service']
    old = service_model.evaluate(car, root=root)
    value = deepcopy(old)
    library = tuple(brief['station_winding_library_m'])
    if library != system_tradeoff.LIBRARY:
        raise ValueError('current network evaluator and selected station library differ')
    for scenario in value['scenarios']:
        p, inputs = scenario['profile'], scenario['inputs']
        scenario['motor_zone_options'] = ([] if p['runtime_s'] is None else
            [service_model.motor_zone(p, length, inputs['train_length_m'], inputs['dwell_s']) for length in library])
    chosen = next(r for r in value['scenarios'] if
        r['inputs']['distance_m'] == brief['prototype_station_spacing_m'] and
        r['inputs']['speed_cap_m_s'] == brief['launch_speed_cap_m_s'] and
        r['inputs']['dwell_s'] == brief['dwell_s'] and
        r['inputs']['constant_drag_N_per_car'] == brief['constant_drag_N_per_car_hypothesis'])
    station = next(z for z in chosen['motor_zone_options'] if z['length_m'] == brief['prototype_shared_winding_m'])
    if not station['geometry_full_engagement'] or station['nominal_resource_screen'] != 'pass':
        raise ValueError('selected current prototype fails its necessary resource/geometry screen')
    shortlist = [dict(scenario_id=chosen['scenario_id'], station_id=station['station_id'],
        runtime_s=chosen['profile']['runtime_s'], winding_length_m=station['length_m'])]
    for distance in (1000., 1500.):
        scenario = next(r for r in value['scenarios'] if r['inputs']['distance_m'] == distance and
            r['inputs']['speed_cap_m_s'] == brief['launch_speed_cap_m_s'] and
            r['inputs']['dwell_s'] == brief['dwell_s'] and
            r['inputs']['constant_drag_N_per_car'] == brief['constant_drag_N_per_car_hypothesis'])
        passing = [z for z in scenario['motor_zone_options'] if z['geometry_full_engagement'] and z['nominal_resource_screen'] == 'pass']
        if not passing:
            raise ValueError('current service spacing has no declared station library survivor')
        z = min(passing, key=lambda r: r['length_m'])
        shortlist.append(dict(scenario_id=scenario['scenario_id'], station_id=z['station_id'],
            runtime_s=scenario['profile']['runtime_s'], winding_length_m=z['length_m']))
    tradeoffs = system_tradeoff.evaluate(car, root=root)
    network = next(r for r in tradeoffs['proposals'] if r['proposal_id'] == selected['selection']['network_proposal_id'])
    if network != selected['network_proposal']:
        raise ValueError('current retained-stop calculation differs from the selected source proposal')
    value.update(schema='osr-current-development-service/1', development_default=True,
        development_selection_id=selected['selection_id'],
        selected_scenario=deepcopy(chosen), selected_station=deepcopy(station),
        selection=dict(selected_scenario_id=chosen['scenario_id'], selected_station_id=station['station_id'],
            purpose='Repository development default; physical and operating qualification remain open',
            development_selection_id=selected['selection_id'], network_proposal_id=network['proposal_id'],
            shortlist=shortlist, integrated_operating_design_selected=False,
            policy='Use the explicitly selected72km/h retained-stop network,120s headway and2km/800m prototype. Cost and physical feasibility remain unknown.'),
        station_resource_campaign=[service_model._resource_events(chosen['profile'], station, brief['dwell_s'],
            delay_first_dwell_s=delay, architecture=architecture)
            for architecture in ('section-addressed', 'whole-zone-exclusive') for delay in (0., 15., 60.)],
        fleet=_fleet(network, root), network_proposal=deepcopy(network),
        named_comparisons=dict(archived_54kmh_450m_prototype=dict(
            service_evaluation_id=old['evaluation_id'], selection=deepcopy(old['selection']),
            launch_speed_m_s=old['selected_scenario']['profile']['peak_speed_m_s'],
            shared_winding_m=old['selected_station']['length_m'],
            role='Retained historical next-experiment comparison; not the current default')),
        source_sha256=_merge(old['source_sha256'], tradeoffs['source_sha256'],
            selected['source_sha256'], sources(root)))
    value['budget'].update(motor_zone_subcomparisons=sum(len(s['motor_zone_options']) for s in value['scenarios']),
        maximum_motor_options_per_reaching_scenario=len(library), native_method_cases=6)
    value['assumptions']['station_winding_library_m'] = list(library)
    value['service'].update(launch_speed_cap_m_s=brief['launch_speed_cap_m_s'],
        dwell_s=brief['dwell_s'], development_default=True, retained_stops=True)
    p = chosen['profile']
    value['protection'].update(stopping_bound_at_launch_speed_m=service_model.stopping_distance_m(p['peak_speed_m_s']),
        stopping_bound_at_receiving_speed_m=service_model.stopping_distance_m(p['arrival_speed_before_braking_m_s']),
        downhill10permille_bound_at_launch_speed_m=service_model.stopping_distance_m(p['peak_speed_m_s'], grade_permille=10))
    value['selection']['selection_id'] = identity(value['selection'])
    value.pop('evaluation_id', None)
    value['evaluation_id'] = identity(value)
    return value, tradeoffs


def build(root=ROOT):
    root = Path(root).resolve()
    selected = selection.load(root)
    car = selected['vehicle']
    value, tradeoffs = _current_service(selected, root)
    interfaces = interface_model.evaluate(car, value, root=root)
    record = dict(schema=SCHEMA, selection_id=selected['selection_id'],
        candidate_id=car['candidate_id'], body_candidate_id=car['body_candidate_id'],
        magnet_component_id=car['magnet_component_id'], selection=selected['selection'],
        development_default=True, configuration_adopted_for_development=True,
        adoption_scope='Design and research default; no construction, manufacturing or operating release',
        vehicle=car, service=value, interfaces=interfaces, gates=deepcopy(interfaces['gates']),
        network_proposal=deepcopy(value['network_proposal']),
        whole_system_alternatives=tradeoffs,
        source_sha256=_merge(selected['source_sha256'], car['source_sha256'],
            value['source_sha256'], interfaces['source_sha256'], sources(root)), **FLAGS)
    record['evaluation_id'] = identity(record)
    return record


def validate(record, root=ROOT):
    if record != build(root):
        raise ValueError('current development candidate, sources, evaluation or selection differs')
    return True


def summary(record):
    car, service = record['vehicle'], record['service']
    return dict(selection_id=record['selection_id'], evaluation_id=record['evaluation_id'],
        candidate_id=record['candidate_id'], body_candidate_id=record['body_candidate_id'],
        magnet_component_id=record['magnet_component_id'], development_default=True,
        configuration_adopted_for_development=True, cars=6, normal_passengers_per_car=46,
        fixed_seats_per_car=44, wheelchair_places_per_car=2, standing_passengers_per_car=0,
        headway_s=120., capacity_pphpd=8280., launch_speed_cap_m_s=20.,
        accounted_tare_kg_per_car=car['mass']['accounted_tare_kg_per_car'],
        accounted_cap_loaded_kg_per_car=car['mass']['accounted_cap_loaded_kg_per_car'],
        installed_tare_kg_per_car=None, CG_m=None, inertia_kg_m2=None,
        selected_station_id=service['selected_station']['station_id'],
        shared_winding_m=service['selected_station']['length_m'],
        prototype_runtime_s=service['selected_scenario']['profile']['runtime_s'],
        baghdad_trainsets=service['fleet']['proposed_total_trainsets'],
        gates=deepcopy(record['gates']), **FLAGS)


def _files(output):
    output = Path(output)
    return {p.relative_to(output).as_posix(): sha256(p.read_bytes()).hexdigest()
        for p in sorted(output.rglob('*')) if p.is_file() and p != output / 'manifest.json'}


def _native_request(record):
    return dict(schema='osr-current-native-request/1', selection_id=record['selection_id'],
        evaluation_id=record['evaluation_id'], candidate_id=record['candidate_id'],
        service_evaluation_id=record['service']['evaluation_id'],
        scenario_id=record['service']['selected_scenario']['scenario_id'],
        station_id=record['service']['selected_station']['station_id'],
        source_sha256=record['source_sha256'], **FLAGS)


def run_native(output, root=ROOT):
    """Execute the unchanged Rust kernel with the newly selected actual profile."""
    root, output = Path(root).resolve(), Path(output).resolve()
    record = build(root)
    output.mkdir(parents=True, exist_ok=False)
    request = _native_request(record)
    (output / 'request.json').write_bytes(encoded(request))
    method = service_model.run_native(record['vehicle'], record['service'], output / 'method', root=root)
    result = dict(schema='osr-current-native-controls/1', **{k: request[k] for k in
        ('selection_id', 'candidate_id', 'service_evaluation_id', 'scenario_id', 'station_id', 'source_sha256')},
        current_evaluation_id=record['evaluation_id'], method_evaluation_id=method['evaluation_id'],
        controls=len(method['rows']), all_controls_pass=method['all_controls_pass'],
        synthetic_gap_range_um=method['synthetic_gap_range_um'],
        physical_gap_response_simulated=False, actual_vehicle_stable_hover_verified=False,
        physical_headway_qualified=False,
        scope='Six actual Rust protection software fixtures on the72km/h analytical profile; virtual6–8mm gaps do not establish an operating gap.', **FLAGS)
    if build(root) != record:
        raise ValueError('current candidate or producer changed during native execution')
    result['evaluation_id'] = identity(result)
    (output / 'result.json').write_bytes(encoded(result))
    (output / 'manifest.json').write_bytes(encoded(dict(schema='osr-current-native-manifest/1',
        selection_id=record['selection_id'], source_sha256=record['source_sha256'],
        evaluation_id=result['evaluation_id'], files_sha256=_files(output), **FLAGS)))
    verify_native(output, record, root)
    return result


def verify_native(output, record=None, root=ROOT):
    output = Path(output)
    expected = build(root)
    if record is not None and record != expected:
        raise ValueError('native verifier received a stale current evaluation')
    record = expected
    manifest = json.loads((output / 'manifest.json').read_bytes())
    result = json.loads((output / 'result.json').read_bytes())
    request = json.loads((output / 'request.json').read_bytes())
    if request != _native_request(record):
        raise ValueError('current native request differs from the selected evaluation')
    if (manifest.get('schema') != 'osr-current-native-manifest/1' or result.get('schema') != 'osr-current-native-controls/1'
        or manifest['source_sha256'] != record['source_sha256'] or result['source_sha256'] != record['source_sha256']
        or manifest['selection_id'] != record['selection_id'] or manifest['evaluation_id'] != result['evaluation_id']
        or manifest['files_sha256'] != _files(output)):
        raise ValueError('current native sources or payload differ')
    for key, value in FLAGS.items():
        if result.get(key) is not value or manifest.get(key) is not value or request.get(key) is not value:
            raise ValueError('native controls cannot grant physical or operating release')
    if (result['selection_id'] != record['selection_id'] or result['current_evaluation_id'] != record['evaluation_id']
        or result['candidate_id'] != record['candidate_id'] or request['evaluation_id'] != record['evaluation_id']
        or result['service_evaluation_id'] != record['service']['evaluation_id']
        or result['station_id'] != record['service']['selected_station']['station_id']
        or result['scenario_id'] != record['service']['selected_scenario']['scenario_id']):
        raise ValueError('native packet belongs to another selection or evaluation')
    if result['evaluation_id'] != identity({k: v for k, v in result.items() if k != 'evaluation_id'}):
        raise ValueError('current native identity differs')
    method = service_model.verify_native(record['vehicle'], record['service'], output / 'method', root=root)
    if method['controls'] != 6 or result['method_evaluation_id'] != method['evaluation_id'] or not result['all_controls_pass']:
        raise ValueError('all six selected-profile native controls must pass')
    return dict(current=True, controls=6, selection_id=record['selection_id'],
        evaluation_id=result['evaluation_id'], physical_headway_qualified=False, **FLAGS)
