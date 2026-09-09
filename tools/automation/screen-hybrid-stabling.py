#!/usr/bin/env python3
"""Replay line-local station/depot allocations across complete service days."""
import argparse
import csv
import importlib.util
import json
from pathlib import Path
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('plan', ROOT / 'tools/automation/generate-stabling-plan.py')
PLAN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PLAN)
from osr_scenario.stabling_hybrid_cycles import inspect_hybrid_cycles


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--design', type=Path, required=True)
    parser.add_argument('--days', type=int, choices=range(1, 8), default=2)
    parser.add_argument('--analyze-existing', action='store_true', help='verify and re-analyze an unchanged native run')
    args = parser.parse_args()
    source, plan = PLAN.build(args.design)
    candidate = PLAN.native_hybrid_candidate(source, plan['hybrid_allocation'])
    doc = tomllib.loads(candidate)
    subprocess.run(['cargo', 'build', '--release', '-p', 'osr-sim', '--bin', 'osr-sim'], cwd=ROOT, check=True)
    binary = ROOT / 'target/release/osr-sim'
    folder = ROOT / 'build/engineering/stabling' / plan['city'] / 'hybrid-cycle'
    folder.mkdir(parents=True, exist_ok=True)
    scenario, raw, csv_path = (folder / f'hybrid.{ext}' for ext in ('toml', 'json', 'csv'))
    provenance = folder / 'run-provenance.json'
    import hashlib
    inputs = {'candidate_sha256': hashlib.sha256(candidate.encode()).hexdigest(),
              'binary_sha256': PLAN.digest(binary), 'days': args.days}
    if not args.analyze_existing:
        scenario.write_text(candidate)
        command = [str(binary), '--config', str(scenario), '--duration', str(args.days * 86400 + 1801),
                   '--status-every', '0', '--ma-check-every', '30', '--json-out', str(raw),
                   '--csv-out', str(csv_path), '--csv-every', '60']
        with (folder / 'hybrid.log').open('w') as handle:
            run = subprocess.run(command, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, check=False)
        if run.returncode not in (0, 1) or not raw.exists():
            raise RuntimeError(f'native replay failed; see {folder}')
        provenance.write_text(json.dumps({**inputs, 'exit_code': run.returncode,
            'raw_sha256': PLAN.digest(raw), 'csv_sha256': PLAN.digest(csv_path)}, indent=2) + '\n')
    recorded = json.loads(provenance.read_text())
    if any(recorded.get(k) != v for k, v in inputs.items()) or recorded['raw_sha256'] != PLAN.digest(raw) or recorded['csv_sha256'] != PLAN.digest(csv_path) or PLAN.digest(scenario) != inputs['candidate_sha256']:
        raise ValueError('native run inputs or output hashes changed; rerun the simulator')
    snapshots = {day * 86400 - 60: [] for day in range(1, args.days + 1)}
    with csv_path.open() as handle:
        for row in csv.DictReader(handle):
            if int(row['sim_time_s']) in snapshots:
                snapshots[int(row['sim_time_s'])].append(row)
    result = json.loads(raw.read_text())
    evidence = inspect_hybrid_cycles(doc, result, snapshots, args.days)
    conservation = all(s['conservation_errors'] == 0 for s in result['energy_sites'])
    sources = {**plan['source_paths'], 'screen_generator': str(Path(__file__).relative_to(ROOT)),
               'hybrid_cycle_model': 'design/city-generation/src/osr_scenario/stabling_hybrid_cycles.py',
               'energy_model': 'crates/osr-sim/src/energy.rs', 'physics_model': 'crates/osr-sim/src/physics.rs', 'report_model': 'crates/osr-sim/src/report.rs'}
    report = {**evidence, 'schema_version': 1, 'city': plan['city'], 'service_days': args.days,
        'passed': evidence['passed'] and conservation and recorded['exit_code'] == 0,
        'deployment_release_ready': False, 'candidate_sha256': inputs['candidate_sha256'],
        'simulator_sha256': inputs['binary_sha256'], 'simulator_exit_code': recorded['exit_code'],
        'source_paths': sources, 'source_sha256': {k: PLAN.digest(ROOT / p) for k, p in sources.items()},
        'site_conservation_passed': conservation, 'movement_authority_check': result['ma_check'],
        'invariant_violations': result['invariant_violations'],
        'raw_result_local_path': str(raw.relative_to(ROOT)), 'raw_result_sha256': recorded['raw_sha256'],
        'csv_local_path': str(csv_path.relative_to(ROOT)), 'csv_sha256': recorded['csv_sha256'],
        'scope': 'Actual same-line home placement, capacity, passenger closure and station launch stock after complete service days',
        'limitations': ['Yard geometry and berthing remain abstract node operations.',
                       'Reserve comparison allows 0.001 percentage point numerical tolerance, matching the city validator; the raw minimum is retained.',
                       'Nominal energy inputs are retained; this does not close electrical or daytime headway acceptance.',
                       'Empty returns may continue after passenger service closes; movements after 02:30 are reported.',
                       'Depot departures during the first 30 minutes are reported, not required for all depot revenue stock.']}
    out = args.design.resolve().parent / 'engineering/stabling'
    (out / 'hybrid-cycle-screen.json').write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + '\n')
    lines = ['# Line-local station/depot service-cycle screen', '',
        f"Operating screen: **{'PASS' if report['passed'] else 'FAIL'}** after {args.days} complete service days. Physical release remains open.", '',
        '| Day | Station / depot trains | Correct homes | Capacity | Station launch directions within 60 s | Passenger departures after closing | Empty returns 02:30–05:30 | Depot revenue departures in first 30 min |',
        '|---|---:|---|---|---:|---:|---:|---:|']
    for c in report['cycles']:
        lines.append(f"| {c['after_service_day']} | {c['station_trainsets']} / {c['depot_trainsets']} | {c['home_placement_passed']} | {c['capacity']['passed']} | {sum(d['passed'] for d in c['directional_service'])} / {len(c['directional_service'])} | {c['passenger_departures_after_closing']} | {c['empty_returns_between_0230_and_0530']} | {c['depot_revenue_departures_first_30_minutes']} |")
    lines += ['', f"Minimum train SoC across the run: {report['minimum_train_soc_during_run']:.3%}. Reserve departures: {len(report['reserve_departures'])}.", '',
        'Exact misplaced train IDs, allocations, direction delays and source/raw-output hashes are in [hybrid-cycle-screen.json](hybrid-cycle-screen.json).', '',
        *['- ' + item for item in report['limitations']], '', '```bash',
        f".venv/bin/python tools/automation/screen-hybrid-stabling.py --design '{plan['source_paths']['design']}' --days {args.days}", '```', '']
    (out / 'hybrid-cycle-screen.md').write_text('\n'.join(lines))
    print(json.dumps({'city': report['city'], 'passed': report['passed'], 'cycles': [
        {k: c[k] for k in ('after_service_day', 'station_trainsets', 'depot_trainsets', 'home_placement_passed', 'morning_launch_passed', 'departures_between_0230_and_0530')}
        for c in report['cycles']]}))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
