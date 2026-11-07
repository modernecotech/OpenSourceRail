import argparse,json
from pathlib import Path
from . import ROOT,FLAGS,coordinator,publication


def main(argv=None):
    p=argparse.ArgumentParser(prog='./osr design station-pair')
    commands=p.add_subparsers(dest='command',required=True)
    commands.add_parser('plan')
    c=commands.add_parser('run');c.add_argument('--output',required=True,type=Path)
    c=commands.add_parser('publish');c.add_argument('--run',required=True,type=Path);c.add_argument('--output',type=Path)
    c=commands.add_parser('verify');c.add_argument('--output',type=Path);c.add_argument('--replay',action='store_true');c.add_argument('--state',type=Path)
    args=p.parse_args(argv)
    if args.command=='plan':
        b,bundle,m,v=coordinator.variants()
        result=dict(body_candidate_id=bundle['candidate_id'],mass_evaluation_id=m['evaluation_id'],
            physical_systems=len(v),normal_cases=len(v)*len(b['speed_caps_km_h']),brief=b,
            scope='Conditional source-rating envelopes; new parts proposal; no reference adoption',**FLAGS)
    elif args.command=='run':
        r=coordinator.run(args.output);result={k:r[k] for k in ('study_id','normal_case_count','conditional_arrivals','outline_screens','execution_wall_s',*FLAGS)}
    elif args.command=='publish':result=publication.publish(args.run,output=args.output)
    else:result=publication.verify(output=args.output,replay=args.replay,state=args.state)
    print(json.dumps(result,sort_keys=True,indent=2,allow_nan=False));return 0


if __name__=='__main__':raise SystemExit(main())
