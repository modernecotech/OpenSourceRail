#!/usr/bin/env python3
"""Replay complete service days and audit the resulting overnight placement."""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('stabling_plan', ROOT / 'tools/automation/generate-stabling-plan.py')
PLAN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PLAN)
from osr_scenario.stabling_cycles import DAY_S, inspect_cycles  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--design', type=Path, required=True)
    parser.add_argument('--days', type=int, choices=range(1, 8), default=2)
    args = parser.parse_args()
    candidate, plan = PLAN.build(args.design)
    doc = tomllib.loads(candidate)
    if doc['scenario']['start_time'] != '05:30' or any(
        f['service_start'] != '05:30' or f['service_end'] != '02:00' for f in doc['fleets']
    ):
        raise ValueError('service-cycle screen requires 05:30 start/opening and 02:00 closure')
    subprocess.run(['cargo', 'build', '--release', '-p', 'osr-sim', '--bin', 'osr-sim'], cwd=ROOT, check=True)
    binary = ROOT / 'target/release/osr-sim'
    folder = ROOT / 'build/engineering/stabling' / plan['city'] / 'service-cycle'
    folder.mkdir(parents=True, exist_ok=True)
    scenario, result_path, csv_path = (folder / f'distributed.{ext}' for ext in ('toml', 'json', 'csv'))
    scenario.write_text(candidate)
    command = [str(binary), '--config', str(scenario), '--duration', str(args.days * DAY_S + 1801),
               '--status-every', '0', '--ma-check-every', '30', '--json-out', str(result_path),
               '--csv-out', str(csv_path), '--csv-every', '60']
    with (folder / 'distributed.log').open('w') as handle:
        run = subprocess.run(command, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, check=False)
    if run.returncode not in (0, 1) or not result_path.is_file():
        raise RuntimeError(f'simulator failed; see {folder / "distributed.log"}')
    result = json.loads(result_path.read_text())
    snapshots = {day * DAY_S - 60: [] for day in range(1, args.days + 1)}
    with csv_path.open() as handle:
        for row in csv.DictReader(handle):
            elapsed = int(row['sim_time_s'])
            if elapsed in snapshots:
                snapshots[elapsed].append(row)
    evidence = inspect_cycles(doc, result, snapshots, args.days)
    design = tomllib.loads(args.design.read_text())
    profiles = tomllib.loads((ROOT / plan['source_paths']['rolling_stock_template']).read_text())['profiles']
    archetypes = tomllib.loads((ROOT / plan['source_paths']['station_template']).read_text())['archetypes']
    for cycle in evidence['cycles']:
        capacity = PLAN.capacity_requirements(design, cycle['observed_allocations'], profiles, archetypes)
        cycle['station_capacity_requirements'] = capacity
        cycle['trainsets_beyond_reference_platform_berths'] = sum(r['trainsets_beyond_reference_platform_berths'] for r in capacity)
        cycle['additional_usable_stabling_length_m'] = sum(r['additional_usable_stabling_length_m'] for r in capacity)
    sources = {**plan['source_paths'], 'screen_generator': str(Path(__file__).relative_to(ROOT)),
               'cycle_model': 'design/city-generation/src/osr_scenario/stabling_cycles.py',
               'direction_model': 'design/city-generation/src/osr_scenario/stabling_evidence.py',
               'energy_model': 'crates/osr-sim/src/energy.rs', 'physics_model': 'crates/osr-sim/src/physics.rs'}
    conservation_ok = all(site['conservation_errors'] == 0 for site in result['energy_sites'])
    report = {**evidence, 'schema_version': 1, 'city': plan['city'],
              'passed': evidence['passed'] and run.returncode == 0 and conservation_ok,
              'operating_behavior_passed': evidence['operating_behavior_passed'] and run.returncode == 0 and conservation_ok,
              'deployment_release_ready': False, 'service_days': args.days,
              'duration_s': result['sim_duration_s'], 'simulator_exit_code': run.returncode,
              'candidate_sha256': plan['candidate_sha256'], 'scenario_sha256': PLAN.digest(scenario),
              'source_paths': sources, 'source_sha256': {key: PLAN.digest(ROOT / path) for key, path in sources.items()},
              'simulator_sha256': PLAN.digest(binary), 'invariant_violations': result['invariant_violations'],
              'site_conservation_passed': conservation_ok, 'site_energy': result['energy_sites'],
              'movement_authority_check': result['ma_check'],
              'energy_totals_kwh': {key: result[key] for key in (
                  'total_energy_consumed_kwh', 'total_energy_charged_kwh', 'total_grid_imported_kwh',
                  'total_grid_exported_kwh', 'total_pv_generated_kwh', 'total_delivered_to_trains_kwh')},
              'energy_adaptive_dispatches': result['energy_adaptive_dispatches'],
              'raw_result_local_path': str(result_path.relative_to(ROOT)), 'raw_result_sha256': PLAN.digest(result_path),
              'csv_local_path': str(csv_path.relative_to(ROOT)), 'csv_sha256': PLAN.digest(csv_path),
              'scope': 'Continuous full service days with a two-train station-capacity gate, overnight placement and direction-specific morning restart checks',
              'limitations': [
                  'Starts at 95% train SoC once; trains, site storage and positions are not reset between days.',
                  'Nominal scenario weather and existing grid/charging quantities are retained; degraded-weather and electrical acceptance remain separate.',
                  'Starting each planned direction does not establish every revenue train is serviceable or daytime headways are delivered.',
                  'Reference platform comparisons use observed parked allocations; physical tracks, access and charger connections remain unverified.',
                  'Low-SoC trains outside selected stabling locations require charging/recovery and evening placement review; reserves do not substitute automatically.',
                  'Movement-authority sweeps can report unknown positions for station-held trains outside the interstation occupancy model; counts are retained, not certified as complete station interlocking evidence.',
              ]}
    out = args.design.resolve().parent / 'engineering/stabling'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'service-cycle-screen.json').write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + '\n')
    (out / 'service-cycle-screen.md').write_text(markdown(report))
    print(json.dumps({'city': report['city'], 'passed': report['passed'], 'service_days': args.days,
                      'cycles': [{key: c[key] for key in ('after_service_day', 'passed', 'largest_station_queue',
                                  'trainsets_beyond_reference_platform_berths')} for c in report['cycles']]}))
    return 0 if report['passed'] else 1


def markdown(report):
    rows = ['# Continuous service-cycle stabling screen', '',
            f"Operating screen: **{'PASS' if report['passed'] else 'FAIL'}** after **{report['service_days']} complete service days**. Physical/deployment release: **open**.", '',
            f"Holding/charging/restart behavior: **{'PASS' if report['operating_behavior_passed'] else 'FAIL'}**. Two-train station capacity: **{'PASS' if report['station_capacity_passed'] else 'FAIL'}**. A behavior pass does not override excess station occupancy.", '',
            '| After service day | Parked trains / stations | Largest queue | Outside selected stabling locations | Directions restarting within 60 s | Minimum night SoC | Beyond reference platform berths | Result |',
            '|---|---:|---:|---:|---:|---:|---:|---|']
    for c in report['cycles']:
        d = c['directional_service']
        rows.append(f"| {c['after_service_day']} | {c['parked_trainsets']} / {c['parked_station_count']} | {c['largest_station_queue']} | {len(c['trainsets_outside_selected_stabling_stations'])} | {d['directions_restarting_within_tolerance']} / {d['planned_direction_count']} | {c['minimum_train_soc']:.1%} | {c['trainsets_beyond_reference_platform_berths']} | {'PASS' if c['passed'] else 'FAIL'} |")
    rows += ['', '## Two-train station capacity', '',
             '| Day | Station | Parked trainsets | Allowed | Excess |', '|---|---|---:|---:|---:|']
    for c in report['cycles']:
        for station in c['station_capacity']['stations']:
            if not station['passed']:
                rows.append(f"| {c['after_service_day']} | {station['station']} | {station['allocated_trainsets']} | {station['allowed_trainsets']} | {station['excess_trainsets']} |")
    rows += ['', '## Trains outside selected stabling locations', '',
             '| After service day | Train | Line | Station | Role | SoC |', '|---|---|---|---|---|---:|']
    for c in report['cycles']:
        for t in c['trainsets_outside_selected_stabling_stations']:
            rows.append(f"| {c['after_service_day']} | {t['train']} | {t['line']} | {t['station']} | {t['service_role']} | {t['soc']:.1%} |")
    rows += ['', f"Minimum train SoC over the complete run: **{report['minimum_train_soc_during_run']:.3%}**. Charging demand and delivered/grid energy are recorded per site in the JSON evidence.", '',
             *[f'- {item}' for item in report['limitations']], '',
             'Reproduce with:', '', '```bash',
             f".venv/bin/python tools/automation/screen-stabling-cycles.py --design '{report['source_paths']['design']}' --days {report['service_days']}", '```', '',
             'Evidence and hashes: [service-cycle-screen.json](service-cycle-screen.json). A failed screen exits with status 1; it does not promote the candidate or change canonical acceptance.', '']
    return '\n'.join(rows)


if __name__ == '__main__':
    raise SystemExit(main())
