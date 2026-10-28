"""Current numerical/evidence work; CLI has no authority to self-authenticate."""
import argparse
import json
from pathlib import Path
from engineering.railway_twin import model, pipeline as parent
from . import coordinator as c, evidence, experiments, variant_design


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='action',required=True)
    sub.add_parser('plan')
    generate=sub.add_parser('assess')
    generate.add_argument('--output',type=Path,required=True)
    generate.add_argument('--family',choices=model.FAMILIES,default='gfrp_semimonocoque')
    generate.add_argument('--distance',type=float,choices=(1500.,2000.),default=2000.)
    generate.add_argument('--input-root',type=Path)
    generate.add_argument('--input-manifest',type=Path)
    generate.add_argument('--motor-package',type=Path,action='append',default=[])
    generate.add_argument('--motor-state',type=Path)
    motors=sub.add_parser('motor-run');motors.add_argument('--state',type=Path,default=Path('build/current-motors'))
    motors.add_argument('--max-new-runs',type=int,default=8)
    verify=sub.add_parser('verify');verify.add_argument('package',type=Path)
    verify.add_argument('--require-complete',action='store_true')
    publish=sub.add_parser('publish');publish.add_argument('package',type=Path)
    mp=sub.add_parser('motor-publish');mp.add_argument('state',type=Path)
    sub.add_parser('motor-verify-publication')
    sub.add_parser('variants-publish')
    sub.add_parser('variants-verify-publication')
    sub.add_parser('verify-publication')
    args=parser.parse_args()
    try:
        if args.action=='plan':
            value=c.specification()
        elif args.action=='motor-run':
            result=experiments.run(args.state,maximum_new_runs=args.max_new_runs)
            value=dict(experiment_id=result['experiment_id'],runs=len(result['rows']),pending=len(result['pending']),
                summaries=[r['summary'] for r in result['rows']],physical_accepted=False)
        elif args.action=='motor-publish':
            value=experiments.publish(args.state,Path(c.ROOT)/c.OUTPUT)
        elif args.action=='motor-verify-publication':
            value=experiments.verify_publication(Path(c.ROOT)/c.OUTPUT)
        elif args.action=='variants-publish':
            value=variant_design.publish(Path(c.ROOT)/c.OUTPUT)
        elif args.action=='variants-verify-publication':
            value=variant_design.verify_publication(Path(c.ROOT)/c.OUTPUT)
        elif args.action=='assess':
            supplied=None
            if args.input_manifest is not None:
                if args.input_manifest.is_symlink() or args.input_manifest.stat().st_size>evidence.MAX_FILE:
                    raise ValueError('Bounded ordinary input manifest required')
                supplied=evidence.parse(args.input_manifest.read_bytes())
            packages=list(args.motor_package)
            if args.motor_state is not None:
                index=experiments.verify_index(args.motor_state)
                candidate=model.materialize(args.family,args.distance)['bundle']['candidate_id']
                packages += [args.motor_state/r['output'] for r in index['rows'] if r['summary']['candidate_id']==candidate and r['summary']['execution']!='held-necessary-bound']
            value=c.generate(args.output,family=args.family,distance_m=args.distance,
                input_root=args.input_root,input_manifest=supplied,motor_packages=packages)
        elif args.action=='verify':
            function=c.verify_archive if args.package.name.endswith('.tar.gz') else c.verify
            value=function(args.package,require_complete=args.require_complete)
        elif args.action=='publish':
            result=c.publish(args.package)
            value=dict(publication_id=result['publication_id'],**result['validation'])
        else:
            value=c.verify_publication()
    except parent.IncompleteDesign as error:
        print(json.dumps(dict(complete=False,frontier=error.blockers),indent=2));return 3
    print(json.dumps(value,indent=2,allow_nan=False));return 0


if __name__=='__main__':
    raise SystemExit(main())
