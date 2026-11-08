import argparse,json
from pathlib import Path
from . import coordinator,publication


def main():
    p=argparse.ArgumentParser(prog='./osr design closure')
    sub=p.add_subparsers(dest='command',required=True)
    run=sub.add_parser('run');run.add_argument('--output',type=Path,required=True)
    run.add_argument('--bogie-detail',action='store_true',help='Explicit research body revision; unresolved gearbox/brake and underframe fit remains held')
    run.add_argument('--without-recovery',action='store_true')
    run.add_argument('--reuse-native',type=Path,help='Copy exact source/tool native state; bridges still enforce full input/resource/output parity')
    pub=sub.add_parser('publish');pub.add_argument('--run',type=Path,required=True);pub.add_argument('--output',type=Path)
    pub.add_argument('--native-cad-evidence',type=Path)
    check=sub.add_parser('verify');check.add_argument('--output',type=Path)
    args=p.parse_args()
    if args.command=='run':result=coordinator.run(args.output,with_recovery=not args.without_recovery,reuse_native=args.reuse_native,bogie_detail=args.bogie_detail)
    elif args.command=='publish':result=publication.publish(args.run,output=args.output,native_cad_evidence=args.native_cad_evidence)
    else:result=publication.verify(output=args.output)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
