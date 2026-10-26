"""Compose current readiness or run bounded, separately scoped native checks."""
import argparse
import json
from pathlib import Path
from . import ROOT


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    for name in ('native','native-worker','verify-native','publish','verify'):
        p=sub.add_parser(name);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--output',type=Path,required=True)
        if name in ('native','native-worker'):
            p.add_argument('--getdp',type=Path);p.add_argument('--ccx',type=Path)
        if name=='native':p.add_argument('--chrono-python',type=Path)
        if name=='native-worker':p.add_argument('--kind',choices=('chrono','magnetic','structure'),required=True)
        if name=='publish':
            p.add_argument('--suspension',type=Path,required=True);p.add_argument('--vehicle',type=Path,required=True)
            p.add_argument('--thermal',type=Path,required=True);p.add_argument('--native',type=Path,required=True)
            p.add_argument('--confirmation',type=Path)
    args=parser.parse_args()
    if args.command in ('native','native-worker','verify-native'):
        from . import native
        if args.command=='native':result=native.run(args.output,root=args.root,chrono_python=args.chrono_python,getdp=args.getdp,ccx=args.ccx)
        elif args.command=='native-worker':result=native.worker(args.kind,args.output,args.root,args.getdp,args.ccx)
        else:result=native.verify(args.output,args.root)
        print(json.dumps(result,sort_keys=True,indent=2,allow_nan=False))
        if args.command=='native' and not result['method_campaign_passed']:return 1
    else:
        from . import publication
        if args.command=='publish':result=publication.publish(args.output,root=args.root,suspension=args.suspension,vehicle=args.vehicle,thermal=args.thermal,native_dir=args.native,confirmation=args.confirmation)
        else:result=publication.verify(args.output,root=args.root)
        print(json.dumps(result,sort_keys=True,indent=2,allow_nan=False))
    return 0


if __name__=='__main__':raise SystemExit(main())
