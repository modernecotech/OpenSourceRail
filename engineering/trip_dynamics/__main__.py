"""Explicit trip experiments; evidence never falls back to ideal support."""
import argparse
import json
from pathlib import Path
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command')
    source_root = Path(__file__).resolve().parents[2]
    for name in ('status','catalogue','cases','simulate','fixture','execute-job','setup-tools','validate-map','validate-modal'):
        p = commands.add_parser(name)
        p.add_argument('--source-root', type=Path, default=source_root)
        if name in ('simulate','fixture','execute-job','setup-tools','validate-map','validate-modal'):
            p.add_argument('--output', required=True, type=Path)
        if name in ('simulate','validate-map','validate-modal'):
            p.add_argument('--vehicle-id')
            p.add_argument('--load-case', choices=('empty','AW3'), default='AW3')
            p.add_argument('--temperature-C', '--temperature', dest='temperature_C', type=float, choices=(20.,50.), default=20.)
        if name == 'simulate':
            p.add_argument('--mode', choices=('evidence','benchmark'), default='evidence')
            p.add_argument('--distance-m', type=int, choices=(1500,2000), default=2000)
            p.add_argument('--mechanical-step-s', type=float, choices=(.001,.0005), default=.001)
        if name == 'fixture':
            p.add_argument('fixture', choices=('current','laminate','nonlinear-magnetics'), nargs='?', default='nonlinear-magnetics')
        if name == 'execute-job':
            p.add_argument('--request', required=True, type=Path)
        if name in ('validate-map','validate-modal'):
            p.add_argument('--model', required=True, type=Path, help='Inline upload JSON; declared source-file paths are never followed')
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
    commands.add_parser('plan')
    p = commands.add_parser('probe')
    p.add_argument('--source-root', type=Path, default=source_root)
    args = parser.parse_args(argv)
    if args.command is None:
        args.command='status';args.source_root=source_root
    if args.command in ('status','catalogue','cases','simulate','fixture','execute-job','setup-tools','validate-map','validate-modal'):
        from . import experiments
        if args.command in ('status','catalogue'):
            answer=getattr(experiments,args.command)(args.source_root)
        elif args.command=='cases':
            answer=experiments.cases()
        else:
            def upload(path):
                if path.is_symlink() or not path.is_file() or path.stat().st_size>4*1024*1024:
                    raise ValueError('bounded ordinary request/model JSON required')
                return json.loads(path.read_bytes())
            parameters={}
            action=args.command
            if args.command=='execute-job':
                request=upload(args.request)
            else:
                if args.command in ('simulate','validate-map','validate-modal'):
                    parameters=dict(load_case=args.load_case,temperature_C=args.temperature_C)
                    if args.vehicle_id is not None:parameters['vehicle_id']=args.vehicle_id
                if args.command=='simulate':
                    action='experiment'
                    parameters.update(mode=args.mode,distance_m=args.distance_m,mechanical_step_s=args.mechanical_step_s)
                if args.command=='fixture':parameters['fixture']=args.fixture
                if args.command in ('validate-map','validate-modal'):parameters['model_data']=upload(args.model)
                request=dict(action=action,parameters=parameters)
            answer=experiments.execute(request,args.output,args.source_root)
        print(json.dumps(answer,sort_keys=True,indent=2,allow_nan=False))
        return 0
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
        # Campaigns invoke this command under native PyChrono and require its
        # original exact solver receipt. Ordinary CLI users also see the
        # actually installed private environment, without an ideal fallback.
        if answer.get('available') is not True:
            from .experiments import probe
            answer=probe(args.source_root)
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
