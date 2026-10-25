"""Explicit trip experiments; evidence never falls back to ideal support."""
import argparse
import json
from pathlib import Path
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('run', 'verify'):
        p = commands.add_parser(name)
        p.add_argument('--output', required=True, type=Path)
        p.add_argument('--source-root', type=Path, default=Path(__file__).resolve().parents[2])
        if name == 'run':
            p.add_argument('--chrono-python', type=Path)
            p.add_argument('--getdp', type=Path)
            p.add_argument('--finite-coupon-archive', type=Path)
            p.add_argument('--without-rust', action='store_true')
    p = commands.add_parser('benchmark-worker')
    p.add_argument('--input', required=True, type=Path); p.add_argument('--output', required=True, type=Path)
    p = commands.add_parser('evaluate')
    p.add_argument('--candidate', required=True, type=Path); p.add_argument('--scenario', required=True, type=Path)
    p.add_argument('--registry', required=True, type=Path); p.add_argument('--output', required=True, type=Path)
    commands.add_parser('plan'); commands.add_parser('probe')
    args = parser.parse_args(argv)
    if args.command == 'benchmark-worker':
        from engineering.design_search.contracts import encoded, identity
        from engineering.design_search.storage import atomic_immutable
        from .scenario import validate
        if args.input.is_symlink() or args.input.stat().st_size > 1024*1024:
            raise ValueError('bounded ordinary benchmark request required')
        job = json.loads(args.input.read_bytes())
        if job.get('job_id') != identity({k:v for k,v in job.items() if k != 'job_id'}):
            raise ValueError('benchmark request identity differs')
        case = validate(job['scenario'])
        if case['mode'] != 'benchmark':
            raise ValueError('ideal benchmark cannot replace an evidence attempt')
        from .chrono_runner import run_benchmark
        answer = run_benchmark(case, job['masses_kg'], dt_s=job['mechanical_step_s'])
        if answer['backend']['solver_id'] != job['expected_solver_id']:
            raise ValueError('executed Chrono solver differs from the exact request')
        answer['input_job_id'] = job['job_id']
        atomic_immutable(args.output, encoded(answer))
        print(json.dumps(dict(input_job_id=job['job_id'], execution='executed')))
        return 0
    elif args.command == 'evaluate':
        from engineering.design_search.contracts import encoded
        from engineering.design_search.storage import atomic_immutable
        from .design_adapter import evaluate_preflight
        answer = evaluate_preflight(json.loads(args.candidate.read_bytes()), json.loads(args.scenario.read_bytes()), registry=args.registry)
        atomic_immutable(args.output, encoded(answer))
    elif args.command == 'plan':
        from .programme import tasks
        answer = tasks()
    elif args.command == 'probe':
        from .chrono_runner import solver_info
        answer = solver_info()
    else:
        from . import campaign
        answer = campaign.run(args.output, root=args.source_root, chrono_python=args.chrono_python,
                              run_rust=not args.without_rust, getdp=args.getdp,
                              finite_coupon_archive=args.finite_coupon_archive) if args.command == 'run' else campaign.verify(args.output, root=args.source_root)
    print(json.dumps(answer, sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, OSError, KeyError, TypeError) as error:
        print('Trip experiment refused: '+str(error), file=sys.stderr)
        sys.exit(2)
