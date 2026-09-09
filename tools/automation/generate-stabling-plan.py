#!/usr/bin/env python3
"""Generate an explicit distributed-stabling operating candidate and open gates."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'design/city-generation/src'))
from osr_scenario.stabling import distributed_candidate  # noqa: E402


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capacity_requirements(design, allocations, profiles, archetypes):
    """Compare queues with the reference passenger-platform envelope only."""
    stations = {}
    for station in design['stations']:
        previous = stations.get(station['id'])
        if previous and any(previous.get(key) != station.get(key) for key in ('archetype', 'platform_length_m')):
            raise ValueError(f"{station['id']}: inconsistent physical platform definition")
        stations[station['id']] = station
    families = {line.get('id') or line['name']: line['rolling_stock'] for line in design['lines']}
    totals, lengths, roles = Counter(), {}, {}
    for allocation in allocations:
        station = allocation['station']
        totals[station] += allocation['trainset_count']
        length = float(profiles[families[allocation['line']]]['length_m'])
        if not math.isfinite(length) or length <= 0:
            raise ValueError(f'{station}: invalid consist length')
        lengths[station] = max(lengths.get(station, 0.0), length)
        roles.setdefault(station, Counter())[allocation['service_role']] += allocation['trainset_count']
    result = []
    for station, total in sorted(totals.items()):
        source = stations[station]
        platform_length = float(source['platform_length_m'])
        platform_count = archetypes[source['archetype']]['platform_count']
        if not math.isfinite(platform_length) or platform_length <= 0 or type(platform_count) is not int or platform_count < 1:
            raise ValueError(f'{station}: invalid platform envelope')
        # RFC 0014: one train plus 5 m at each end; no train may straddle a
        # turnout or overhang its assumed clear slot to make this comparison pass.
        slot = lengths[station] + 10.0
        berths = platform_count * math.floor((platform_length + 1e-9) / slot)
        excess = max(0, total - berths)
        result.append({'station': station, 'trainsets': total, 'service_roles': dict(roles[station]),
                       'longest_train_m': lengths[station], 'slot_length_with_clearance_m': slot,
                       'reference_platform_count': platform_count, 'platform_length_m': platform_length,
                       'reference_platform_berths': berths,
                       'trainsets_beyond_reference_platform_berths': excess,
                       'additional_usable_stabling_length_m': excess * slot,
                       'verified_stabling_slots': None})
    return result


def build(design_path: Path):
    design_path = design_path.resolve()
    design = tomllib.loads(design_path.read_text())
    slug = design['city']['slug']
    scenario_path = design_path.with_name(f'{slug}.toml')
    candidate, allocations = distributed_candidate(scenario_path.read_text(), design["fleets"])
    scenario = tomllib.loads(candidate)
    profiles = tomllib.loads((ROOT / 'lib/templates/rolling-stock.toml').read_text())['profiles']
    archetypes = tomllib.loads((ROOT / 'lib/templates/stations.toml').read_text())['archetypes']
    capacity = capacity_requirements(design, allocations, profiles, archetypes)
    roles = Counter()
    for allocation in allocations:
        roles[allocation['service_role']] += allocation['trainset_count']
    counts = Counter()
    for row in allocations:
        counts[row['station']] += row['trainset_count']
    sources = {'design': design_path, 'scenario': scenario_path,
               'generator': Path(__file__), 'allocation_model': ROOT / 'design/city-generation/src/osr_scenario/stabling.py',
               'depot_policy': ROOT / 'lib/templates/depots.toml', 'simulator': ROOT / 'crates/osr-sim/src/sim.rs',
               'loader': ROOT / 'crates/osr-sim/src/scenario_file.rs', 'schedule': ROOT / 'crates/osr-sim/src/schedule.rs',
               'station_template': ROOT / 'lib/templates/stations.toml',
               'rolling_stock_template': ROOT / 'lib/templates/rolling-stock.toml',
               'train_model': ROOT / 'crates/osr-sim/src/train.rs'}
    report = {
        'schema_version': 1, 'city': slug, 'status': 'operating-candidate-physical-allocation-open',
        'generation_passed': True, 'passed': False, 'deployment_release_ready': False,
        'source_paths': {key: str(path.relative_to(ROOT)) for key, path in sources.items()},
        'source_sha256': {key: digest(path) for key, path in sources.items()},
        'candidate_sha256': hashlib.sha256(candidate.encode()).hexdigest(),
        'candidate_local_path': f'build/engineering/stabling/{slug}.toml',
        'fleet_trainsets': sum(f['trainset_count'] for f in scenario['fleets']),
        'fleet_roles': dict(roles), 'station_capacity_requirements': capacity,
        'trainsets_beyond_reference_platform_berths': sum(row['trainsets_beyond_reference_platform_berths'] for row in capacity),
        'additional_usable_stabling_length_m': sum(row['additional_usable_stabling_length_m'] for row in capacity),
        'initial_station_count': len(counts), 'maximum_initial_trainsets_at_one_station': max(counts.values()),
        'initial_station_trainsets': dict(sorted(counts.items())), 'initial_allocations': allocations,
        'policy': {'healthy_fleet_location': 'powered stations near first morning trips',
                   'depot_role': 'maintenance, inspection and defective trains',
                   'holding_charge_power_kw_per_train': 150, 'holding_target_soc': 0.95,
                   'start_rule': 'line service start, subject to energy, headway and movement-authority gates'},
        'open_gates': ['track-by-track capacity and platform/turnout access', 'charger sharing and overnight delivery',
                      'security, CCTV, remote isolation and release inspection', 'reserve activation, defect routing and maintenance allocation',
                      'evening placement and morning demand/headway validation'],
        'limitations': ['Initial queues are balanced across powered station/direction choices; this is not a surveyed parking layout.',
                        'Declared spares and cold reserves remain parked and charge; automatic substitution, defect routing and maintenance release are not modelled.',
                        'Returning trains hold at selected powered stations after service ends; no train is teleported back to its initial placement.',
                        'Reference platform berths are an optimistic length/count comparison, not verified parking capacity; dedicated sidings and workshop bays receive no automatic credit.',
                        'Station berths, crossovers and shared junction conflicts are outside the simplified interstation movement-authority graph.',
                        'Existing depot/station energy quantities and service schedules are preserved, not accepted as correctly sized.'],
    }
    return candidate, report


def markdown(report):
    rows = ['# Distributed station stabling candidate', '',
            'Healthy trains stay at powered stations for coordinated morning starts. Depot bays serve maintenance, inspection and defective sets.', '',
            f"Operating allocation: **{report['fleet_trainsets']} trainsets at {report['initial_station_count']} stations**; largest initial station queue **{report['maximum_initial_trainsets_at_one_station']}**. Physical release: **open**.", '',
            'This candidate preserves all non-fleet scenario inputs and the existing fleet counts/service windows. It enables station holding and 150 kW top-up to 95% SoC, subject to shared site limits. Existing canonical simulation evidence still describes the retained endpoint-dispatch scenario.', '',
            f"Fleet roles: **{report['fleet_roles'].get('revenue', 0)} revenue, {report['fleet_roles'].get('spare', 0)} spare, {report['fleet_roles'].get('cold_reserve', 0)} cold reserve**. Reserves are held out of routine dispatch.", '',
            '| Line | Station | Direction | Role | Initial trainsets | Verified track slots |', '|---|---|---|---|---:|---|']
    rows += [f"| {r['line']} | {r['station']} | {r['heading']} | {r['service_role']} | {r['trainset_count']} | pending |" for r in report['initial_allocations']]
    rows += ['', '## Reference platform capacity comparison', '',
             f"**{report['trainsets_beyond_reference_platform_berths']} trainsets exceed the reference platform envelope**, requiring **{report['additional_usable_stabling_length_m']:,.1f} m** of additional usable slots under this initial allocation. This does not establish the location or need for new infrastructure; existing sidings require evidence before crediting them.", '',
             '| Station | Trainsets | Reference platform berths | Beyond envelope | Additional usable slot length m |',
             '|---|---:|---:|---:|---:|']
    rows += [f"| {r['station']} | {r['trainsets']} | {r['reference_platform_berths']} | {r['trainsets_beyond_reference_platform_berths']} | {r['additional_usable_stabling_length_m']:,.1f} |" for r in report['station_capacity_requirements']]
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
