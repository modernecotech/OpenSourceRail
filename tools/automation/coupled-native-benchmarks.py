#!/usr/bin/env python3
"""Bounded solid/transient method execution; never operating qualification."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engineering.design_search import grammar_shell, transient_lim
from engineering.station_rail.common import encoded, identity


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'build/coupled-native-ci')
    parser.add_argument('--plan', action='store_true')
    args = parser.parse_args()
    solids = grammar_shell.benchmark_plan()['cases']
    magnetic = transient_lim.benchmark_plan()['jobs']
    plan = dict(solid_cases=[c['id'] for c in solids],
                transient_cases=[c['id'] for c in magnetic],
                maximum_jobs=10, physical_accepted=False)
    if args.plan:
        print(json.dumps(plan, sort_keys=True))
        return 0
    if args.output.exists():
        raise ValueError('Fresh immutable benchmark directory required')
    args.output.mkdir(parents=True)
    (args.output / 'plan.json').write_bytes(encoded(plan))
    results = []
    for case in solids:
        results.append(grammar_shell.run_benchmark(case, args.output / case['id']))
    for job in magnetic:
        folder = args.output / job['id']
        results.append(transient_lim.run(job['case'], folder))
        transient_lim.verify(folder)
    complete = (all(r.get('method_screen') == 'pass' for r in results[:4])
                and all(r.get('execution') == 'completed' for r in results))
    summary = dict(schema='osr-coupled-native-method-CI/1',
                   status='method_execution_complete' if complete else 'fail',
                   results=results, physical_accepted=False,
                   full_body_qualified=False, nonlinear_operating_map_available=False,
                   scope='Fixture and kernel regression only; transient convergence remains unconfirmed')
    summary['run_id'] = identity(summary)
    (args.output / 'summary.json').write_bytes(encoded(summary))
    print(json.dumps(dict(status=summary['status'], native_cases=len(results),
                          physical_accepted=False), sort_keys=True))
    return 0 if complete else 1


if __name__ == '__main__':
    raise SystemExit(main())
