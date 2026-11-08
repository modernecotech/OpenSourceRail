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
    p=sub.add_parser('review-pack');p.add_argument('--proposal',required=True)
    p.add_argument('--documents',required=True);p.add_argument('--conversions',required=True)
    p.add_argument('--artifact-root',required=True);p.add_argument('--city',required=True);p.add_argument('--output',required=True)
    args=parser.parse_args()
    if args.command=='compile':
        manifest=compile_run(args.study,args.body,args.service_id,args.output)
        result={k:manifest[k] for k in ('manifest_id','proposal_id','identities','completion')}
    elif args.command=='review-pack':
        from .review import compile_review_pack,export_review_pack
        from .export import load
        value=compile_review_pack(load(args.proposal),load(args.documents),load(args.conversions),
            artifact_root=args.artifact_root,city=args.city)
        result=export_review_pack(value,args.artifact_root,args.output)
    else:
        result=verify_run(args.output)
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':
    main()
