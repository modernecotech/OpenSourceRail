#!/usr/bin/env python3
"""Materialise city survey/civil gates and operating cross-checks without erasing receipts."""
from __future__ import annotations
import argparse
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate(design, reuse_sumo=False, fetch_soils=False, include_soils=True):
    design = design.resolve(); city = design.parent
    slug = tomllib.loads(design.read_text())['city']['slug']
    survey = city / 'engineering/survey'
    steps = [('survey_package', ['--design', design, '--output-dir', survey])]
    sumo_path = city / 'engineering/sumo/summary.json'
    sumo = json.loads(sumo_path.read_text()) if sumo_path.exists() else {}
    if not reuse_sumo or any(sumo.get(k) != sha(v) for k,v in {'design_sha256':design, 'scenario_sha256':city/f'{slug}.toml', 'generator_sha256':ROOT/'engineering/analysis/benchmarks/sumo/city_timetable.py'}.items()):
        steps.insert(0, ('benchmarks/sumo/city_timetable', ['--design', design, '--output-dir', city / 'engineering/sumo']))
    if include_soils:
        steps.insert(0, ('city_soils', ['--design', design, *(['--fetch'] if fetch_soils else [])]))
    for name in ('survey_control', 'ground_model'):
        steps.append((name, ['--city', slug, '--manifest', survey / 'survey-input-manifest.csv', '--evidence-root', survey, '--output-dir', survey]))
    for name, stem in (('surveyed_alignment','surveyed-alignment'), ('route_station_fit','route-station-fit'), ('drainage_ground_design','drainage-ground'), ('structural_release','structural-release')):
        steps.append((name, ['--design', design, '--manifest', survey / f'{stem}-input-manifest.csv', '--evidence-root', survey, '--output-dir', survey, '--write-placeholder-manifest']))
    log_root = ROOT / 'build/engineering/deployment' / slug; log_root.mkdir(parents=True, exist_ok=True)
    binary = ROOT / 'target/release/osr-sim'
    raw = log_root / 'native-reference.json'
    subprocess.run([str(binary), '--config', str(city / f'{slug}.toml'), '--duration', '1', '--status-every', '0', '--compact-json', '--json-out', str(raw)], check=True, capture_output=True)
    result = json.loads(raw.read_text())
    reference = dict(schema_version=1, generator_sha256=sha(Path(__file__)), scope='kinematic-reference-only', generation_passed=bool(result.get('per_line_reference_trip_time_s')), design_sha256=sha(design), scenario_sha256=sha(city / f'{slug}.toml'), simulator_sha256=sha(binary), simulator_source_sha256=sha(ROOT / 'crates/osr-sim/src/sim.rs'), per_line_reference_trip_time_s=result.get('per_line_reference_trip_time_s', []))
    reference_path = city / 'engineering/simulation/native-timing-reference.json'
    reference_path.parent.mkdir(parents=True, exist_ok=True)
    reference_path.write_text(json.dumps(reference, indent=2, sort_keys=True)+'\n')
    steps.append(('operations_crosscheck', ['--design', design, '--sumo-summary', city / 'engineering/sumo/summary.json', '--simulation-summary', city / 'engineering/simulation/validation-summary.json', '--output-dir', city / 'engineering/simulation', '--native-reference', reference_path]))
    steps.append(('city_deployment', ['--design', design]))
    results = []
    log_root = ROOT / 'build/engineering/deployment' / slug; log_root.mkdir(parents=True, exist_ok=True)
    for name, arguments in steps:
        result = subprocess.run([sys.executable, str(ROOT / f'engineering/analysis/{name}.py'), *map(str, arguments)], capture_output=True, text=True)
        (log_root / f'{name.replace("/", "-")}.log').write_text(result.stdout + result.stderr)
        if result.returncode:
            # A real comparison failure must remain visible and does not
            # prevent other cities receiving their civil evidence packages.
            if name != 'operations_crosscheck' or 'Traceback' in result.stderr:
                raise RuntimeError(f'{slug}: {name} failed; see {log_root / (name+".log")}')
            results.append(name)
    return {'city':slug, 'failed_automatic_checks':results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--design', type=Path)
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--reuse-sumo', action='store_true')
    parser.add_argument('--fetch-soils', action='store_true')
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    if args.all == bool(args.design): parser.error('choose --all or --design')
    designs = sorted((ROOT / 'cities/catalogue').glob('*/*/*/design.toml')) if args.all else [args.design]
    subprocess.run(['cargo', 'build', '--release', '-p', 'osr-sim', '--bin', 'osr-sim'], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    results=[]
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for task in as_completed([pool.submit(generate,p,args.reuse_sumo,args.fetch_soils) for p in designs]):
            result=task.result();results.append(result);print(json.dumps(result),flush=True)
    return int(any(r['failed_automatic_checks'] for r in results))


if __name__ == '__main__': raise SystemExit(main())
