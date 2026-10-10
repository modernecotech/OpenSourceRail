#!/usr/bin/env python3
"""Run and verify bounded complete civil-system exploration campaigns."""
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'design/component-catalogue/src'))

from engineering.civil_exploration.contracts import HERE,load,encoded
from engineering.civil_exploration.workflow import run_campaign, verify, compare, derive, worker,prepare,validate_candidate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    active=load(HERE/'config/qualification-target.json')['deployment']
    commands = parser.add_subparsers(dest='command', required=True)
    run = commands.add_parser('run')
    run.add_argument('--config', type=Path, default=HERE/'config/reference.json')
    run.add_argument('--output', type=Path)
    run.add_argument('--deployment',choices=['reference','baghdad'],default=active)
    run.add_argument('--train-record',type=Path)
    run.add_argument('--resume', action='store_true')
    run.add_argument('--retry-failed', action='store_true')
    check = commands.add_parser('verify')
    check.add_argument('bundle', type=Path); check.add_argument('--historical', action='store_true')
    report = commands.add_parser('compare'); report.add_argument('bundle', type=Path)
    child = commands.add_parser('derive')
    child.add_argument('--parent', type=Path, required=True); child.add_argument('--definition', type=Path, required=True)
    child.add_argument('--output', type=Path, required=True)
    child.add_argument('--reason', required=True, help='Reason for the recorded geometry modification')
    start=commands.add_parser('prepare',aliases=['generate'])
    start.add_argument('--config',type=Path,default=HERE/'config/reference.json');start.add_argument('--output',type=Path,required=True)
    programme=commands.add_parser('programme')
    programme.add_argument('--output',type=Path)
    programme.add_argument('--deployment',choices=['reference','baghdad'],default=active)
    programme.add_argument('--train-record',type=Path)
    programme.add_argument('--quick',action='store_true',help='Run refinements without repeating full reference transient campaign')
    programme.add_argument('--search-evaluations',type=int,default=32)
    benchmark=commands.add_parser('benchmark');benchmark.add_argument('--output',type=Path,required=True)
    optimiser=commands.add_parser('optimise',aliases=['optimize','search'])
    optimiser.add_argument('--config',type=Path,default=HERE/'config/reference.json');optimiser.add_argument('--output',type=Path,required=True)
    optimiser.add_argument('--evaluations',type=int,default=48);optimiser.add_argument('--seeds',type=int,nargs='+',default=[11,23,47])
    optimiser.add_argument('--population',type=int,default=12);optimiser.add_argument('--wall-seconds',type=int,default=600)
    optimiser.add_argument('--resume',action='store_true')
    detail=commands.add_parser('detail');detail.add_argument('--candidate',type=Path,required=True)
    detail.add_argument('--config',type=Path,default=HERE/'config/reference.json');detail.add_argument('--output',type=Path,required=True)
    detail.add_argument('--meshes',type=float,nargs=3,default=[.8,.4,.2])
    price=commands.add_parser('cost');price.add_argument('--candidate',type=Path,required=True)
    price.add_argument('--config',type=Path,default=HERE/'config/reference.json');price.add_argument('--quotes',type=Path,default=HERE/'config/commercial.json')
    price.add_argument('--output',type=Path,required=True)
    export=commands.add_parser('export-ifc');export.add_argument('--candidate',type=Path,required=True)
    export.add_argument('--config',type=Path,default=HERE/'config/reference.json');export.add_argument('--output',type=Path,required=True)
    archive=commands.add_parser('archive');archive.add_argument('bundle',type=Path);archive.add_argument('--output',type=Path,required=True)
    retrieval=commands.add_parser('restore');retrieval.add_argument('store',type=Path);retrieval.add_argument('--output',type=Path,required=True)
    validation=commands.add_parser('validate-data');validation.add_argument('dataset',type=Path);validation.add_argument('--output',type=Path,required=True)
    tests=commands.add_parser('test-plan');tests.add_argument('--candidate-ids',nargs='+',required=True);tests.add_argument('--output',type=Path,required=True)
    promotion=commands.add_parser('promotion-check');promotion.add_argument('bundle',type=Path);promotion.add_argument('--output',type=Path,required=True)
    promotion.add_argument('--design',type=Path);promotion.add_argument('--receipt-manifest',type=Path);promotion.add_argument('--evidence-root',type=Path)
    qualification=commands.add_parser('qualification')
    qualification.add_argument('--train-record',type=Path)
    qualification.add_argument('--output',type=Path,default=ROOT/'build/engineering/civil-studies/baghdad-qualification')
    native = commands.add_parser('_worker', help=argparse.SUPPRESS)
    native.add_argument('job', type=Path); native.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        if args.command=='qualification':
            from engineering.civil_exploration.qualification import build,write
            report=build(args.train_record);write(report,args.output);print(args.output/'qualification.md');return 0
        if args.command in ('run','programme'):
            if args.output is None:
                name=('first-campaign' if args.command=='run' else 'programme') if args.deployment=='reference' else 'baghdad-'+args.command
                args.output=ROOT/'build/engineering/civil-studies'/name
            if args.deployment=='baghdad':
                from engineering.civil_exploration.qualification import build,write
                report=build(args.train_record)
                if args.command=='programme' or not report['moving_force_execution_ready']:
                    write(report,args.output,resume=getattr(args,'resume',False))
                    reason=report['status'] if not report['moving_force_execution_ready'] else 'blocked-coupled-programme-inputs-and-project-model-selection'
                    print(f'Baghdad: {reason}; {args.output/"qualification.md"}',file=sys.stderr);return 2
                write(report,args.output,config=args.config,resume=args.resume)
                result=run_campaign(args.output/'solver-profile.json',args.output/'evaluation',resume=args.resume,retry_failed=args.retry_failed)
                rows=load(args.output/'evaluation/comparison.json')['rows']
                print(args.output/'evaluation/comparison.md')
                return int(any(r['execution']!='completed' or r['numerical_screen']!='passed' for r in rows))
            if args.train_record:raise ValueError('supplier train record belongs to the Baghdad deployment')
        if args.command in ('prepare','generate'):
            result=prepare(args.config,args.output);print(f"Prepared {len(result['cases'])} immutable candidates");return 0
        if args.command=='programme':
            from engineering.civil_exploration.programme import run as programme_run
            result=programme_run(args.output,full=not args.quick,search_evaluations=args.search_evaluations)
            print(args.output/'programme.md');return 0
        if args.command=='benchmark':
            from engineering.civil_exploration.programme import component_campaign
            result=component_campaign(args.output);print(json.dumps(result,indent=2));return int(not result['passed'])
        if args.command in ('optimise','optimize','search'):
            from engineering.civil_exploration.search import run as optimise
            result=optimise(load(args.config),args.output,seeds=args.seeds,evaluations=args.evaluations,population=args.population,wall_seconds=args.wall_seconds,resume=args.resume)
            print(args.output/'search.json');return int(result['status']!='completed')
        if args.command in ('detail','cost','export-ifc'):
            c=load(args.candidate);validate_candidate(c);s=load(args.config)
            if args.command=='detail':
                from engineering.civil_exploration.detailed import run as solid
                if args.output.exists():raise ValueError('detailed output must be new')
                rows=[solid(c,s,h,args.output/f'mesh-{h:g}') for h in args.meshes]
                args.output.joinpath('mesh-study.json').write_bytes(encoded(rows));print(args.output/'mesh-study.json')
            elif args.command=='cost':
                from engineering.civil_exploration.commercial import price
                args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(encoded(price(c,s,load(args.quotes))));print(args.output)
            else:
                from engineering.civil_exploration.bim import export
                export(c,s,args.output);print(args.output)
            return 0
        if args.command in ('archive','restore'):
            from engineering.civil_exploration import storage
            result=storage.pack(args.bundle,args.output) if args.command=='archive' else storage.restore(args.store,args.output)
            print(json.dumps({k:v for k,v in result.items() if k not in ('files','parts')},indent=2));return 0
        if args.command=='validate-data':
            from engineering.civil_exploration.validation import fit_and_holdout
            result=fit_and_holdout(load(args.dataset));args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_bytes(encoded(result));print(args.output);return 0
        if args.command=='test-plan':
            from engineering.civil_exploration.validation import protocols
            protocols(args.output,args.candidate_ids);print(args.output/'test-programme.json');return 0
        if args.command=='promotion-check':
            from engineering.civil_exploration.validation import promotion
            result=promotion(args.bundle,args.output,design=args.design,receipt_manifest=args.receipt_manifest,evidence_root=args.evidence_root)
            print(result['status']);return 0 if result['status']=='reviewed-proposal-ready-for-existing-change-process' else 2
        if args.command == '_worker':
            worker(args.job, args.output)
            return 0
        if args.command == 'run':
            result = run_campaign(args.config, args.output, resume=args.resume, retry_failed=args.retry_failed)
            rows = json.loads((args.output/'comparison.json').read_text())['rows']
            print(f"Retained {len(rows)} comparisons at {args.output/'comparison.md'}")
            return int(any(r['execution'] != 'completed' or r['numerical_screen'] != 'passed' for r in rows))
        if args.command == 'verify':
            result = verify(args.bundle, current=not args.historical)
            print(f"Verified {len(result['evaluations'])} evaluation attempts; physical release remains false")
        elif args.command == 'compare':
            compare(args.bundle); print(args.bundle/'comparison.md')
        else:
            result = derive(args.parent, args.definition, args.output, reason=args.reason)
            print(result['id'])
        return 0
    except (ValueError, RuntimeError, OSError) as error:
        print(f'Civil study: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
