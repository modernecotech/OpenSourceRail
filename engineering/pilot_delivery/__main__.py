"""Local proposal CLI; never connects to business or control services."""
import argparse
import json
from .export import compile_run, verify_run


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('compile');p.add_argument('--study',required=True);p.add_argument('--body',required=True)
    p.add_argument('--service-id',required=True);p.add_argument('--output',required=True)
    p=sub.add_parser('verify');p.add_argument('--output',required=True)
    args=parser.parse_args()
    if args.command=='compile':
        manifest=compile_run(args.study,args.body,args.service_id,args.output)
        result={k:manifest[k] for k in ('manifest_id','proposal_id','identities','completion')}
    else:
        result=verify_run(args.output)
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':
    main()
