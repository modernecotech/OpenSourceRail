import argparse,json,gzip
from pathlib import Path
from engineering.station_rail.common import encoded
from . import ROOT,catalogue,publication


def main(argv=None,*,root=ROOT):
    parser=argparse.ArgumentParser(prog='./osr design parts')
    commands=parser.add_subparsers(dest='command',required=True)
    commands.add_parser('plan')
    p=commands.add_parser('build');p.add_argument('--output',type=Path,required=True)
    p=commands.add_parser('publish');p.add_argument('--output',type=Path)
    p=commands.add_parser('verify');p.add_argument('--output',type=Path)
    args=parser.parse_args(argv)
    if args.command=='verify':value=publication.verify(root,args.output)
    elif args.command=='publish':value=publication.publish(root,args.output)
    else:
        bundle=catalogue.build(root);value=publication.summary(bundle)
        if args.command=='build':
            if args.output.exists():raise ValueError('Fresh immutable parts run required')
            args.output.mkdir(parents=True)
            publication.write(args.output/'manufacturing-bundle.json.gz',gzip.compress(encoded(bundle),mtime=0))
            publication.write(args.output/'summary.json',encoded(value))
            value=dict(output=str(args.output),**catalogue.verify(bundle,root))
        else:value={k:value[k] for k in ('candidate_id','counted','design_stage','electrical_checks','selected_reference_changed')}
    print(json.dumps(value,sort_keys=True,indent=2,allow_nan=False));return 0


if __name__=='__main__':raise SystemExit(main())
