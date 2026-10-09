#!/usr/bin/env python3
"""Retain a compact, source-bound civil campaign review without raw fields."""
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'design/component-catalogue/src'))

from engineering.civil_exploration.contracts import encoded, load, sha
from engineering.civil_exploration.workflow import verify


def review(bundle):
    manifest = verify(bundle)
    if not manifest['complete']:
        raise ValueError('campaign incomplete; compact review export blocked')
    benchmark = (bundle/manifest['benchmark']['path']).parent/'result.json'
    names = {c['candidate_id']: c['name'] for c in manifest['cases']}
    attempts, latest = [], {}
    for entry in manifest['evaluations']:
        record = load(bundle/entry['path'])
        attempts.append({k: record[k] for k in ('evaluation_id', 'attempt', 'candidate_id', 'ground_scenario', 'status', 'error')})
        latest[record['evaluation_id']] = (entry, record)
    cases = []
    for entry, record in latest.values():
        item = dict(candidate_name=names[record['candidate_id']], candidate_id=record['candidate_id'],
                    ground_scenario=record['ground_scenario'], execution=record['status'],
                    record_sha256=entry['sha256'], native_output_hashes=record['output_hashes'])
        if record['status'] == 'completed':
            result = load((bundle/entry['path']).parent/'result.json')
            for key in ('quantities', 'peak_responses', 'research_limits', 'convergence',
                        'numerical_screen_passed', 'engineering_feasibility', 'evidence_maturity', 'evidence_gaps', 'braking'):
                item[key] = result[key]
            item['static'] = result['static'][-1]
            item['handling'] = result['handling'][-1]
            item['dynamic_shortlist'] = [{key: result[key] for key in
                                         ('mesh', 'speed_m_s', 'time_step_s', 'damping_ratio', 'envelope', 'governing_time_s',
                                          'rail_load_distribution_length_m')} | {'frequencies_hz': result['modes']['frequencies_hz']}
                                         for result in result['dynamics'][2::3]]
        cases.append(item)
    return dict(schema='osr-civil-review/1', generator='tools/automation/export-civil-study-review.py',
                generator_sha256=sha(Path(__file__)), consumer='engineering/analysis/tests/test_civil_exploration_review.py',
                repository_commit=manifest['repository_commit'], native_manifest_sha256=sha(bundle/'manifest.json'),
                study=load(bundle/'study.json'), dependency_hashes=manifest['dependency_hashes'],
                environment=manifest['environment'], reference_benchmarks=load(benchmark),
                cases=cases, attempts=attempts, physical_release=False, operating_release=False,
                raw_fields_retained_in='build/engineering/civil-studies/first-campaign; regenerate or use archived checksummed artifacts',
                qualified_feasible_pareto_set=[])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT/'engineering/civil_exploration/examples/first-campaign.json')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        data = encoded(review(args.bundle))
        if args.check:
            if args.output.read_bytes() != data:
                raise ValueError('compact civil review is stale')
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_bytes(data)
        print('Compact civil review current; numerical research only, physical release false')
        return 0
    except (ValueError, OSError) as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
