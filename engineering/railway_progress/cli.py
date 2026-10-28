"""Unified front-door entry for continuing numerical reference-cell work."""
import argparse,json
from pathlib import Path
from . import ROOT
from . import coordinator


def main(argv=None,*,root=ROOT):
    p=argparse.ArgumentParser(prog='./osr design progress');p.add_argument('action',choices=('plan','run','verify','publish','verify-publication','verify-methods','serve'))
    p.add_argument('--state',type=Path,default=Path(root)/'build/continuing-cell')
    p.add_argument('--max-cases',type=int,default=10);p.add_argument('--maximum-seconds',type=float,default=1800.)
    p.add_argument('--port',type=int,default=8771);args=p.parse_args(argv)
    if args.action=='plan':r=coordinator.plan()
    elif args.action=='run':
        value=coordinator.run(args.state,root=root,max_cases=args.max_cases,maximum_seconds=args.maximum_seconds)
        r=dict(run_id=value['run_id'],cases=len(value['cases']),pending=len(value['pending']),new_cases=value['new_cases'])
    elif args.action=='verify':r=coordinator.verify(args.state,root=root)
    elif args.action=='publish':r=coordinator.publish(args.state,root=root)
    elif args.action=='verify-publication':r=coordinator.verify_publication(root=root)
    elif args.action=='verify-methods':
        from . import methods
        r=methods.verify(Path(root)/coordinator.OUTPUT,root=root)
    else:
        from . import workbench
        return workbench.serve(args.state,port=args.port,root=root)
    print(json.dumps(r,sort_keys=True,indent=2));return 0


if __name__=='__main__':raise SystemExit(main())
