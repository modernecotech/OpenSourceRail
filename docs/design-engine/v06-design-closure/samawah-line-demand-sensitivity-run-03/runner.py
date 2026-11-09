from copy import deepcopy
from gzip import compress
from hashlib import sha256
from pathlib import Path
import json
import os
import resource
import subprocess
import sys
import time

ROOT = Path('/home/hayder/.local/state/opensourcerail/worktrees/v06-design-closure-20261108')
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from engineering.outline import city_inputs, city_service, city_project_cost, completion, coordinator
from engineering.station_rail.common import digest, encoded, identity


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded(value))


def save_record(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(compress(encoded(value), mtime=0))


def main():
    started = time.time()
    cpu_before = resource.getrusage(resource.RUSAGE_SELF).ru_utime + resource.getrusage(resource.RUSAGE_SELF).ru_stime
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    context = coordinator.prepare(ROOT)
    geography = city_inputs.prepare(ROOT)
    city = city_inputs.load('samawah', root=ROOT, context=geography)
    ids = {line['line_id'] for line in city['lines']}
    longest = max(city['lines'], key=lambda line: (line['route_m'], line['line_id']))['line_id']
    shortest = min(city['lines'], key=lambda line: (line['route_m'], line['line_id']))['line_id']
    default_rules = completion.policy(ROOT)
    control = float(default_rules['peak_demand_pphpd'])
    lower_sensitivity = 1200.0
    configurations = [
        dict(name='legacy-scalar-control', demands=None,
             interpretation='Published 4,000 pphpd scalar control; not a surveyed forecast.'),
        dict(name='mapped-uniform-control', demands={line_id: control for line_id in sorted(ids)},
             interpretation='Same published scalar control represented as exact per-line inputs.'),
        dict(name='longest-line-lower-sensitivity', demands={line_id: (lower_sensitivity if line_id == longest else control) for line_id in sorted(ids)},
             interpretation='One-line sensitivity only: lower-demand perturbation on the longest mapped line; not a local forecast.'),
        dict(name='shortest-line-lower-sensitivity', demands={line_id: (lower_sensitivity if line_id == shortest else control) for line_id in sorted(ids)},
             interpretation='One-line sensitivity only: lower-demand perturbation on the shortest mapped line; not a local forecast.'),
    ]
    request = dict(schema='osr-samawah-line-demand-sensitivity/1', source_commit=commit,
        city_slug='samawah', city_input_id=city['input_id'], reference_candidate_ids=city['reference_candidate_ids'],
        route_km_by_line={line['line_id']: line['route_m'] / 1000 for line in city['lines']},
        line_count=len(ids), longest_line_id=longest, shortest_line_id=shortest,
        scalar_control_pphpd=control, perturbation_pphpd=lower_sensitivity,
        demand_evidence='All values are explicit planning controls/sensitivities; none is surveyed demand.',
        configurations=configurations, native_cad_jobs=0, native_fem_jobs=0,
        physical_accepted=False, engineering_accepted=False, manufacturing_release=False,
        operating_release=False, movement_authority=False)
    request['request_id'] = identity(request)
    write_json(OUT / 'request.json', request)
    save_record(OUT / 'city-input.json.gz', city)
    write_json(OUT / 'status.json', dict(request_id=request['request_id'], state='running', completed_cases=[]))
    try:
        records = {}
        for item in configurations:
            rules = deepcopy(default_rules)
            if item['demands'] is not None:
                rules['line_peak_demand_pphpd'] = deepcopy(item['demands'])
                rules['demand_source'] = item['interpretation']
            service = city_service.evaluate(city, rules, context['spec']['design'], context['vehicle'], root=ROOT)
            costs = city_project_cost.evaluate_city_cost(city, service['line_services'], context, policy=rules, root=ROOT)
            record = completion._assemble_city(city, service, costs, context, rules)
            records[item['name']] = record
            save_record(OUT / 'cases' / (item['name'] + '.json.gz'), record)
            write_json(OUT / 'status.json', dict(request_id=request['request_id'], state='running',
                completed_cases=[dict(name=name, evaluation_id=value['evaluation_id']) for name, value in records.items()]))

        by_case = {name: {row['line_id']: row for row in value['service_evaluation']['line_services']}
                   for name, value in records.items()}
        legacy, mapped = by_case['legacy-scalar-control'], by_case['mapped-uniform-control']
        for line_id in sorted(ids):
            if legacy[line_id]['evaluation_id'] != mapped[line_id]['evaluation_id']:
                raise ValueError('Mapped 4,000 pphpd input changed unchanged per-line service identity')
        legacy_cost = records['legacy-scalar-control']['cost']
        mapped_cost = records['mapped-uniform-control']['cost']
        if legacy_cost['installed_capital_usd'] != mapped_cost['installed_capital_usd']:
            raise ValueError('Mapped 4,000 pphpd input changed installed capital')
        if legacy_cost['whole_life_npv_usd'] != mapped_cost['whole_life_npv_usd']:
            raise ValueError('Mapped 4,000 pphpd input changed lifecycle NPV')
        for name, changed_line in (('longest-line-lower-sensitivity', longest),
                                   ('shortest-line-lower-sensitivity', shortest)):
            for line_id in sorted(ids - {changed_line}):
                if by_case[name][line_id]['evaluation_id'] != mapped[line_id]['evaluation_id']:
                    raise ValueError('One-line demand perturbation changed an unrelated line identity')
            if by_case[name][changed_line]['evaluation_id'] == mapped[changed_line]['evaluation_id']:
                raise ValueError('Demand perturbation did not change the affected line evaluation identity')

        summary_cases = []
        for item in configurations:
            value = records[item['name']]
            lines = value['service_evaluation']['line_services']
            summary_cases.append(dict(name=item['name'], interpretation=item['interpretation'],
                evaluation_id=value['evaluation_id'], research_configuration_id=value['research_configuration_id'],
                line_services=[dict(line_id=row['line_id'], peak_demand_pphpd=row['requirements']['peak_demand_pphpd'],
                    headway_s=row['requirements']['headway_s'], trainsets=row['service']['total_trainsets'],
                    train_km_per_day=row['service']['train_km_per_day'],
                    mechanical_work_kwh_per_direction_trip=row['service']['mechanical_work_kwh_per_direction_trip'])
                    for row in lines],
                installed_capital_usd=value['cost']['installed_capital_usd'],
                whole_life_npv_usd=value['cost']['whole_life_npv_usd'],
                price_per_route_km_usd=value['cost']['price_per_route_km_usd'],
                scope_totals_usd=value['cost']['scope_totals_usd'], outline_complete=value['outline_complete'],
                physical_accepted=value['physical_accepted'], engineering_accepted=value['engineering_accepted']))
        summary = dict(schema='osr-samawah-line-demand-sensitivity-summary/1', request_id=request['request_id'],
            city_input_id=city['input_id'], reference_candidate_ids=city['reference_candidate_ids'],
            city_route_km=sum(x['route_m'] for x in city['lines']) / 1000,
            legacy_and_uniform_mapping_match=True, unrelated_line_identities_unchanged=True,
            cases=summary_cases, **{k: False for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release','movement_authority')})
        summary['summary_id'] = identity(summary)
        write_json(OUT / 'summary.json', summary)
        source_map = {}
        for value in records.values():
            for name, sha in value['source_sha256'].items():
                if name in source_map and source_map[name] != sha:
                    raise ValueError('Mixed source epochs across sensitivity cases: ' + name)
                source_map[name] = sha
        for mapping in (context.get('sources', {}), geography.get('source_sha256', {})):
            for name, sha in mapping.items():
                if name in source_map and source_map[name] != sha:
                    raise ValueError('Mixed coordinator/geography source epoch: ' + name)
                source_map[name] = sha
        extra_sources = {
            str(Path(completion.__file__).relative_to(ROOT)): digest(completion.__file__),
            str(Path(coordinator.__file__).relative_to(ROOT)): digest(coordinator.__file__),
            completion.POLICY: digest(ROOT / completion.POLICY),
            'engineering/development-baseline.toml': digest(ROOT / 'engineering/development-baseline.toml'),
        }
        for name, sha in extra_sources.items():
            if name in source_map and source_map[name] != sha:
                raise ValueError('Mixed explicit producer source epoch: ' + name)
            source_map[name] = sha
        for name, sha in source_map.items():
            if digest(ROOT / name) != sha:
                raise ValueError('Source changed during sensitivity run: ' + name)
        files = {path.relative_to(OUT).as_posix(): digest(path) for path in OUT.rglob('*')
                 if path.is_file() and path.name not in ('manifest.json', 'status.json', 'stdout.log', 'stderr.log')}
        ended = time.time()
        cpu_after = resource.getrusage(resource.RUSAGE_SELF).ru_utime + resource.getrusage(resource.RUSAGE_SELF).ru_stime
        execution = dict(request_id=request['request_id'], source_commit=commit,
            command='timeout -k 5s 120s prlimit --cpu=60 --as=1073741824 -- .venv/bin/python -B /home/hayder/.local/state/opensourcerail/runs/v06-design-closure-20261108/samawah-line-demand-sensitivity-run-03/runner.py',
            started_unix_s=started, ended_unix_s=ended, wall_s=ended - started, process_cpu_s=cpu_after - cpu_before,
            max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, cpu_limit_s=60,
            address_space_limit_bytes=1024**3, wall_limit_s=120, native_jobs=0,
            isolation='OS resource limits applied by parent process; filesystem was not sandboxed.',
            completed_cases=len(records), outcome='pass', physical_accepted=False)
        write_json(OUT / 'execution.json', execution)
        files['execution.json'] = digest(OUT / 'execution.json')
        manifest = dict(schema='osr-samawah-line-demand-sensitivity-run/1', request_id=request['request_id'],
            source_commit=commit, city_input_id=city['input_id'], source_sha256=dict(sorted(source_map.items())),
            files_sha256=dict(sorted(files.items())), **{k: False for k in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release','movement_authority')})
        manifest['manifest_id'] = identity(manifest)
        write_json(OUT / 'manifest.json', manifest)
        write_json(OUT / 'status.json', dict(request_id=request['request_id'], manifest_id=manifest['manifest_id'],
            state='completed', completed_cases=[dict(name=name, evaluation_id=value['evaluation_id']) for name, value in records.items()]))
    except BaseException as exc:
        write_json(OUT / 'failure.json', dict(request_id=request['request_id'], state='failed-or-interrupted',
            exception=type(exc).__name__, message=str(exc), completed_cases=sorted(records) if 'records' in locals() else []))
        write_json(OUT / 'status.json', dict(request_id=request['request_id'], state='failed-or-interrupted',
            completed_cases=[dict(name=name, evaluation_id=value['evaluation_id']) for name, value in records.items()] if 'records' in locals() else []))
        raise


if __name__ == '__main__':
    main()
