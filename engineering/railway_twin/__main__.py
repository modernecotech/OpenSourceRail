"""Command line for source-bound sparse-wayside digital twins."""
import argparse
import json
from pathlib import Path
from . import ROOT
from . import pipeline, model


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='action',required=True)
    sub.add_parser('plan')
    single=sub.add_parser('generate')
    single.add_argument('--family',choices=model.FAMILIES,default='gfrp_semimonocoque')
    single.add_argument('--distance',type=float,choices=(1500.,2000.),default=2000.)
    single.add_argument('--output',type=Path)
    single.add_argument('--native',action='store_true')
    run=sub.add_parser('run')
    run.add_argument('--state',type=Path)
    run.add_argument('--max-cases',type=int)
    run.add_argument('--native-jobs',type=int,default=0)
    publish=sub.add_parser('publish');publish.add_argument('--state',type=Path)
    sub.add_parser('verify-publication')
    verify=sub.add_parser('verify');verify.add_argument('package',type=Path)
    verify.add_argument('--require-complete',action='store_true')
    args=parser.parse_args()
    try:
        if args.action=='plan':
            value=pipeline.specification()
        elif args.action=='generate':
            value=pipeline.generate(family=args.family,distance_m=args.distance,output=args.output,native=args.native)
        elif args.action=='run':
            result=pipeline.run(state=args.state,maximum_new_cases=args.max_cases,native_jobs=args.native_jobs)
            value=dict(campaign_id=result['campaign_id'],completed_cases=len(result['cases']),pending=len(result['pending']),
                cases=[dict(candidate_id=r['validation']['candidate_id'],family=r['request']['family'],distance_m=r['request']['distance_m'],output=r['output']) for r in result['cases']],
                engineering_complete=False,physical_accepted=False)
        elif args.action=='verify-publication':
            value=pipeline.verify_publication()
        elif args.action=='publish':
            result=pipeline.publish(state=args.state)
            value=dict(publication_id=result['publication_id'],cases=len(result['cases']),pending=len(result['pending']),physical_accepted=False)
        else:
            function=pipeline.verify_archive if args.package.name.endswith('.tar.gz') else pipeline.verify
            value=function(args.package,require_complete=args.require_complete)
    except pipeline.IncompleteDesign as error:
        print(json.dumps(dict(verified=False,engineering_complete=False,blockers=error.blockers),indent=2))
        return 3
    print(json.dumps(value,indent=2,allow_nan=False))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
