#!/usr/bin/env python3
"""Generate an explicit distributed-stabling operating candidate and open gates."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'design/city-generation/src'))
from osr_scenario.stabling import distributed_candidate  # noqa: E402


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(design_path: Path):
    design_path = design_path.resolve()
    design = tomllib.loads(design_path.read_text())
    slug = design['city']['slug']
    scenario_path = design_path.with_name(f'{slug}.toml')
    candidate, allocations = distributed_candidate(scenario_path.read_text())
    scenario = tomllib.loads(candidate)
    counts = Counter()
    for row in allocations:
        counts[row['station']] += row['trainset_count']
    sources = {'design': design_path, 'scenario': scenario_path,
               'generator': Path(__file__), 'allocation_model': ROOT / 'design/city-generation/src/osr_scenario/stabling.py',
               'depot_policy': ROOT / 'lib/templates/depots.toml', 'simulator': ROOT / 'crates/osr-sim/src/sim.rs',
               'loader': ROOT / 'crates/osr-sim/src/scenario_file.rs', 'schedule': ROOT / 'crates/osr-sim/src/schedule.rs'}
    report = {
        'schema_version': 1, 'city': slug, 'status': 'operating-candidate-physical-allocation-open',
        'generation_passed': True, 'passed': False, 'deployment_release_ready': False,
        'source_paths': {key: str(path.relative_to(ROOT)) for key, path in sources.items()},
        'source_sha256': {key: digest(path) for key, path in sources.items()},
        'candidate_sha256': hashlib.sha256(candidate.encode()).hexdigest(),
        'candidate_local_path': f'build/engineering/stabling/{slug}.toml',
        'fleet_trainsets': sum(f['trainset_count'] for f in scenario['fleets']),
        'initial_station_count': len(counts), 'maximum_initial_trainsets_at_one_station': max(counts.values()),
        'initial_station_trainsets': dict(sorted(counts.items())), 'initial_allocations': allocations,
        'policy': {'healthy_fleet_location': 'powered stations near first morning trips',
                   'depot_role': 'maintenance, inspection and defective trains',
                   'holding_charge_power_kw_per_train': 150, 'holding_target_soc': 0.95,
                   'start_rule': 'line service start, subject to energy, headway and movement-authority gates'},
        'open_gates': ['track-by-track capacity and platform/turnout access', 'charger sharing and overnight delivery',
                      'security, CCTV, remote isolation and release inspection', 'reserve/defect/maintenance allocation',
                      'evening placement and morning demand/headway validation'],
        'limitations': ['Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.',
                        'The legacy model makes the entire fleet available; spare, cold-reserve and defective-set assignments still need explicit operational roles.',
                        'Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.',
                        'Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.',
                        'Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.'],
    }
    return candidate, report


def markdown(report):
    rows = ['# Distributed station stabling candidate', '',
            'Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.', '',
            f"Operating allocation: **{report['fleet_trainsets']} trainsets at {report['initial_station_count']} stations**; largest initial station queue **{report['maximum_initial_trainsets_at_one_station']}**. Physical release: **open**.", '',
            'This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.', '',
            '| Line | Station | Direction | Initial trainsets | Verified track slots |', '|---|---|---|---:|---|']
    rows += [f"| {r['line']} | {r['station']} | {r['heading']} | {r['trainset_count']} | pending |" for r in report['initial_allocations']]
    rows += ['', *[f'- {x}' for x in report['limitations']], '',
             'Regenerate this report and its local runnable scenario with:', '', '```bash',
             f".venv/bin/python tools/automation/generate-stabling-plan.py --design '{report['source_paths']['design']}'", '```', '',
             'The scenario is generated under `build/engineering/stabling/`; its hash is recorded in `summary.json`. Source-linked operating replay evidence, where available, is in `operating-screen.json` beside this report.', '']
    return '\n'.join(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('--all', action='store_true')
    choice.add_argument('--design', type=Path)
    args = parser.parse_args()
    paths = sorted((ROOT / 'cities/catalogue').glob('*/*/*/design.toml')) if args.all else [args.design]
    for path in paths:
        candidate, report = build(path)
        folder = path.parent / 'engineering/stabling'
        folder.mkdir(parents=True, exist_ok=True)
        local = ROOT / report['candidate_local_path']
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_text(candidate)
        (folder / 'summary.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
        (folder / 'README.md').write_text(markdown(report))
        print(f"{report['city']}: {report['fleet_trainsets']} trainsets at {report['initial_station_count']} stations; physical allocation open")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
