#!/usr/bin/env python3
"""Replay retained and distributed scenarios across overnight shutdown/restart."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('stabling_plan', ROOT / 'tools/automation/generate-stabling-plan.py')
PLAN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PLAN)
from osr_scenario.stabling_evidence import inspect_morning_service  # noqa: E402


def replay(text, label, folder, binary):
    # Keep the original service window/schedule; this screen requires the
    # catalogue 02:00 closure and 05:30 opening rather than assuming other times.
    doc = tomllib.loads(text)
    if any(f['service_end'] != '02:00' or f['service_start'] != '05:30' for f in doc['fleets']):
        raise ValueError('overnight comparison currently requires 02:00 closure / 05:30 opening')
    text, count = re.subn(r'(?m)^start_time\s*=\s*"[^"]+"', 'start_time = "01:30"', text)
    if count != 1:
        raise ValueError('expected exactly one scenario start time')
    scenario = folder / f'{label}.toml'
    scenario.write_text(text)
    result_path, csv_path = folder / f'{label}.json', folder / f'{label}.csv'
    command = [str(binary), '--config', str(scenario), '--duration', '16201', '--status-every', '0',
               '--ma-check-every', '30', '--json-out', str(result_path), '--csv-out', str(csv_path), '--csv-every', '60']
    with (folder / f'{label}.log').open('w') as log:
        run = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=False)
    if run.returncode not in (0, 1) or not result_path.is_file():
        raise RuntimeError(f'{label}: simulator failed; see {folder / (label + ".log")}')
    result = json.loads(result_path.read_text())
    with csv_path.open() as handle:
        rows = list(csv.DictReader(handle))
    final_night = [r for r in rows if r['clock_tod_hms'] == '05:29:00']
    station_lookup = {}
    station_by_id = {station['id']: station for station in doc['stations']}
    for line in doc['lines']:
        for ref in line['stations']:
            key = (line['name'], station_by_id[ref['id']]['name'])
            if key in station_lookup and station_lookup[key] != ref['id']:
                raise ValueError(f'ambiguous CSV station identity: {key}')
            station_lookup[key] = ref['id']
    parked = Counter()
    for row in final_night:
        if row['phase'] in ('awaiting', 'dwelling'):
            parked[station_lookup[(row['line'], row['station'])]] += 1
    departures = [e for e in result['events'] if e['kind'] in ('DepartStation', 'Dispatched')]
    # The loader assigns StationIds in source order; events preserve those IDs.
    station_numbers = {i + 1: s['id'] for i, s in enumerate(doc['stations'])}
    directional = inspect_morning_service(doc, result["events"], final_night)
    first_morning = {}
    for event in departures:
        if event['sim_time_s'] >= 14400:
            first_morning.setdefault(station_numbers[event['station']], event['sim_time_s'] - 14400)
    late_night = [e for e in departures if 3600 <= e['sim_time_s'] < 14400]
    fleet = sum(f['trainset_count'] for f in doc['fleets'])
    all_parked = sum(parked.values()) == fleet and len(final_night) == fleet
    resumed = all(station in first_morning and first_morning[station] <= 60 for station in parked)
    passed = run.returncode == 0 and not result['invariant_violations'] and all_parked and not late_night and resumed and directional['passed']
    return {
        'passed': passed, 'scenario_sha256': PLAN.digest(scenario),
        'simulator_exit_code': run.returncode, 'invariant_violations': result['invariant_violations'],
        'directional_service': directional,
        'reserve_held_s': result.get('reserve_held_s', 0),
        'fleet_trainsets': fleet, 'parked_trainsets_at_0529': sum(parked.values()),
        'parked_station_count_at_0529': len(parked), 'parked_station_trainsets_at_0529': dict(sorted(parked.items())),
        'largest_overnight_station_queue': max(parked.values(), default=0),
        'departures_between_0230_and_0530': len(late_night),
        'first_morning_departure_delay_s': dict(sorted(first_morning.items())),
        'every_occupied_station_restarts_within_60s': resumed,
        'minimum_train_soc_at_0529': min(float(r['soc']) for r in final_night),
        'energy_charged_during_replay_kwh': result['total_energy_charged_kwh'],
        'site_energy': result['energy_sites'], 'movement_authority_check': result['ma_check'],
        'raw_result_local_path': str(result_path.relative_to(ROOT)), 'raw_result_sha256': PLAN.digest(result_path),
        'csv_local_path': str(csv_path.relative_to(ROOT)), 'csv_sha256': PLAN.digest(csv_path),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--design', type=Path, required=True)
    args = parser.parse_args()
    subprocess.run(['cargo', 'build', '--release', '-p', 'osr-sim', '--bin', 'osr-sim'], cwd=ROOT, check=True)
    candidate, plan = PLAN.build(args.design)
    folder = ROOT / 'build/engineering/stabling' / plan['city']
    folder.mkdir(parents=True, exist_ok=True)
    binary = ROOT / 'target/release/osr-sim'
    cases = {
        'retained_endpoints': replay((ROOT / plan['source_paths']['scenario']).read_text(), 'retained', folder, binary),
        'distributed_stations': replay(candidate, 'distributed', folder, binary),
    }
    sources = {**plan['source_paths'], 'screen_generator': str(Path(__file__).relative_to(ROOT)),
               'energy_model': 'crates/osr-sim/src/energy.rs', 'train_model': 'crates/osr-sim/src/train.rs',
               'physics_model': 'crates/osr-sim/src/physics.rs',
               'direction_model': 'design/city-generation/src/osr_scenario/stabling_evidence.py'}
    report = {'schema_version': 1, 'city': plan['city'], 'passed': cases['distributed_stations']['passed'],
              'deployment_release_ready': False, 'candidate_sha256': plan['candidate_sha256'],
              'source_paths': sources, 'source_sha256': {k:PLAN.digest(ROOT/v) for k,v in sources.items()},
              'simulator_sha256': PLAN.digest(binary), 'cases': cases,
              'scope': '01:30–06:00 operating comparison with a 60-second restart gate for every planned line/station/direction and no reserve dispatch',
              'limitations': ['Both cases start at 95% train SoC at 01:30; this is not a full-day energy-sizing or degraded-weather acceptance run.',
                              'CSV phase/location/SoC are used; its nominal charging-power column is not treated as metered delivery.',
                              'Candidate spares and cold reserves are held out of routine service; activation, defect routing and maintenance release remain unmodelled.',
                              'Station berths and crossovers remain abstract; physical track capacity, train health, maintenance routing and security are unverified.']}
    out = args.design.resolve().parent / 'engineering/stabling'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'operating-screen.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    rows = ['# Overnight operating comparison', '', f"Operating screen: **{'PASS' if report['passed'] else 'FAIL'}**. Physical/deployment release: **open**.", '',
            '| Case | Parked trainsets / stations at 05:29 | Largest station queue | 02:30–05:30 departures | All occupied stations restart within 60 s | Planned directions starting within 60 s | Reserve departures | Invariant violations |',
            '|---|---:|---:|---:|---|---:|---:|---:|']
    for name, case in cases.items():
        rows.append(f"| {name} | {case['parked_trainsets_at_0529']} / {case['parked_station_count_at_0529']} | {case['largest_overnight_station_queue']} | {case['departures_between_0230_and_0530']} | {case['every_occupied_station_restarts_within_60s']} | {case['directional_service']['directions_restarting_within_tolerance']} / {case['directional_service']['planned_direction_count']} | {len(case['directional_service']['reserve_departures'])} | {len(case['invariant_violations'])} |")
    rows += ['', '## Planned direction departures', '', '| Line | Station | Direction | Ready revenue trains at 05:29 | First departure delay s | Result |', '|---|---|---|---:|---:|---|']
    for row in cases['distributed_stations']['directional_service']['directional_departures']:
        rows.append(f"| {row['line']} | {row['station']} | {row['heading']} | {row['ready_revenue_trainsets_at_0529']} | {row['first_morning_departure_delay_s'] if row['first_morning_departure_delay_s'] is not None else 'missing'} | {'PASS' if row['passed'] else 'FAIL'} |")
    rows += ['', *[f'- {x}' for x in report['limitations']], '', 'Evidence and source hashes: [operating-screen.json](operating-screen.json). This is candidate evidence; the canonical city scenario and its acceptance results have not been replaced.', '']
    (out / 'operating-screen.md').write_text('\n'.join(rows))
    print(json.dumps({'city':report['city'], 'passed': report['passed'], 'cases': {k:{x:v[x] for x in ('parked_station_count_at_0529','largest_overnight_station_queue','every_occupied_station_restarts_within_60s')} for k,v in cases.items()}}))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
