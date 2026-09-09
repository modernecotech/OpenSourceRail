#!/usr/bin/env python3
"""Derive counterfactual queue targets and transfer requirements from native nights."""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('stabling_plan', ROOT / 'tools/automation/generate-stabling-plan.py')
PLAN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PLAN)
from osr_scenario.stabling_redistribution import balance_snapshot  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--design', type=Path, required=True)
    args = parser.parse_args()
    candidate, plan = PLAN.build(args.design)
    doc = tomllib.loads(candidate)
    if doc.get('faults'):
        raise ValueError('redistribution study currently requires a nominal scenario without faults')
    folder = args.design.resolve().parent / 'engineering/stabling'
    cycle_path = folder / 'service-cycle-screen.json'
    screen = json.loads(cycle_path.read_text())
    if not screen['passed'] or screen['candidate_sha256'] != plan['candidate_sha256']:
        raise ValueError('requires a passing continuous replay of the current candidate')
    for key, relative in screen['source_paths'].items():
        if PLAN.digest(ROOT / relative) != screen['source_sha256'][key]:
            raise ValueError(f'continuous replay has stale source {key}; regenerate it')
    trace = ROOT / screen['csv_local_path']
    if PLAN.digest(trace) != screen['csv_sha256']:
        raise ValueError('native CSV does not match its recorded evidence hash')
    snapshots = {c['night_snapshot_elapsed_s']: [] for c in screen['cycles']}
    with trace.open() as handle:
        for row in csv.DictReader(handle):
            elapsed = int(row['sim_time_s'])
            if elapsed in snapshots:
                snapshots[elapsed].append(row)
    consist, climate = doc['consist'], doc['climate']
    uplift = climate.get('hvac_uplift_frac', min(.25, max(0, (climate['ambient_c'] - 25) / 25)))
    energy = consist.get('energy_kwh_per_car_km', 4.0) * consist['car_count'] * (1 + uplift)
    design = tomllib.loads(args.design.read_text())
    profiles = tomllib.loads((ROOT / plan['source_paths']['rolling_stock_template']).read_text())['profiles']
    archetypes = tomllib.loads((ROOT / plan['source_paths']['station_template']).read_text())['archetypes']
    cycles = []
    for night in screen['cycles']:
        target = balance_snapshot(doc, snapshots[night['night_snapshot_elapsed_s']],
                                  kwh_per_km=energy, battery_kwh=consist['battery_capacity_kwh'],
                                  max_speed_kmh=consist['max_speed_kmh'])
        capacity = PLAN.capacity_requirements(design, target['target_allocations'], profiles, archetypes)
        target.update({'after_service_day': night['after_service_day'],
                       'night_snapshot_elapsed_s': night['night_snapshot_elapsed_s'],
                       'station_capacity_requirements': capacity,
                       'trainsets_beyond_reference_platform_berths': sum(r['trainsets_beyond_reference_platform_berths'] for r in capacity),
                       'additional_usable_stabling_length_m': sum(r['additional_usable_stabling_length_m'] for r in capacity),
                       'moves_exceeding_30_minutes_even_at_speed_limit': sum(m['travel_lower_bound_s'] > 1800 for m in target['moves']),
                       'longest_transfer_distance_km': max((m['distance_m'] for m in target['moves']), default=0) / 1000})
        cycles.append(target)
    sources = {**screen['source_paths'], 'cycle_report': str(cycle_path.relative_to(ROOT)),
               'study_generator': str(Path(__file__).relative_to(ROOT)),
               'redistribution_model': 'design/city-generation/src/osr_scenario/stabling_redistribution.py'}
    berths = sum(r['reference_platform_berths'] for r in plan['station_capacity_requirements'])
    report = {'schema_version': 1, 'city': plan['city'], 'generation_passed': True,
              'passed': False, 'deployment_release_ready': False,
              'status': 'counterfactual-allocation-movement-and-physical-validation-open',
              'fleet_trainsets': plan['fleet_trainsets'], 'reference_platform_berths': berths,
              'two_trainsets_per_station_reference': {
                  'station_count': plan['initial_station_count'],
                  'trainset_positions': 2 * plan['initial_station_count'],
                  'fleet_positions_elsewhere_or_to_resolve': max(0, plan['fleet_trainsets'] - 2 * plan['initial_station_count']),
              },
              'unavoidable_positions_beyond_selected_platform_envelope': max(0, plan['fleet_trainsets'] - berths),
              'candidate_sha256': plan['candidate_sha256'], 'cycles': cycles,
              'source_paths': sources, 'source_sha256': {k: PLAN.digest(ROOT / v) for k, v in sources.items()},
              'native_csv_local_path': screen['csv_local_path'], 'native_csv_sha256': screen['csv_sha256'],
              'energy_model': {'kwh_per_train_km': energy, 'battery_kwh': consist['battery_capacity_kwh'],
                               'operating_reserve_soc': .2, 'holding_target_soc': .95},
              'limitations': [
                  'This reassigns a recorded 05:29 snapshot on paper; no simulator train is moved or reset and no evening timetable is proven.',
                  'Only revenue trains move; reserve locations and at least one revenue train for every planned line/station/direction are preserved.',
                  'The station queue lower bound uses fleet totals, allowed locations and fixed reserve/direction coverage. Greedy shortest feasible moves are not guaranteed to minimize transfer distance.',
                  'Routes follow line order, terminal reversals and ring direction; transfers between lines or reversal at an intermediate station are not invented.',
                  'Energy allows precharging at the origin up to 95% and retains the 20% reserve, with no en-route charging or solar credited. Shared charger contention is not scheduled.',
                  'Time lower bounds omit acceleration, dwell, turnback, inspection and traffic conflicts. SoC is rounded in the native CSV; its 05:29 value is not evidence of energy available at 02:00.',
                  'Transfers must be incorporated into a validated earlier evening plan; they cannot be inserted into the protected overnight hold or the synchronized morning start.',
                  'Platform berths remain an unverified reference envelope. Existing sidings, revised infrastructure or fleet/service requirements need evidence before any new depot decision.',
              ]}
    (folder / 'redistribution-study.json').write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + '\n')
    (folder / 'redistribution-study.md').write_text(markdown(report))
    print(json.dumps({'city': report['city'], 'generation_passed': True, 'physical_and_movement_release': False,
                      'cycles': [{k: c[k] for k in ('after_service_day', 'target_maximum_queue', 'trainsets_to_move', 'total_transfer_train_km')} for c in cycles]}))
    return 0


def markdown(report):
    rows = ['# Station redistribution requirements', '',
            '**Counterfactual allocation study; movement and physical release remain open.**', '',
            f"The fleet has **{report['fleet_trainsets']} trains** and the selected stations have **{report['reference_platform_berths']} reference platform berths**. Even perfect redistribution leaves at least **{report['unavoidable_positions_beyond_selected_platform_envelope']} positions** beyond that envelope.", '',
            f"A uniform **two-trainsets-per-station** provision gives **{report['two_trainsets_per_station_reference']['trainset_positions']} positions at {report['two_trainsets_per_station_reference']['station_count']} stations**, leaving **{report['two_trainsets_per_station_reference']['fleet_positions_elsewhere_or_to_resolve']} fleet positions** elsewhere or unresolved. The larger platform reference includes four-berth interchange variants. Neither comparison verifies physical stabling capacity.", '',
            '| After service day | Observed largest queue | Target largest queue | Queue lower bound | Trains to move | Transfer train-km | Origin precharge kWh | Beyond platform envelope |',
            '|---|---:|---:|---:|---:|---:|---:|---:|']
    for c in report['cycles']:
        rows.append(f"| {c['after_service_day']} | {c['observed_maximum_queue']} | {c['target_maximum_queue']} | {c['queue_lower_bound']} | {c['trainsets_to_move']} | {c['total_transfer_train_km']:.1f} | {c['precharge_required_kwh']:.1f} | {c['trainsets_beyond_reference_platform_berths']} |")
    rows += ['', '## Required train transfers', '',
             '| Day | Train | Origin → target | Departure heading | Distance km | Travel lower bound min | Precharge kWh |',
             '|---|---|---|---|---:|---:|---:|']
    for c in report['cycles']:
        for m in c['moves']:
            rows.append(f"| {c['after_service_day']} | T{m['train']} | {m['from_station']} → {m['to_station']} | {m['from_heading']} → {m['to_heading']} | {m['distance_m']/1000:.2f} | {m['travel_lower_bound_s']/60:.1f} | {m['precharge_required_kwh']:.1f} |")
    rows += ['', *[f'- {item}' for item in report['limitations']], '', 'Reproduce after generating the continuous native replay:', '',
             '```bash', f".venv/bin/python tools/automation/study-stabling-redistribution.py --design '{report['source_paths']['design']}'", '```', '',
             'Source hashes, station targets and full routes: [redistribution-study.json](redistribution-study.json). Successful generation does not close the package gates.', '']
    return '\n'.join(rows)


if __name__ == '__main__':
    raise SystemExit(main())
