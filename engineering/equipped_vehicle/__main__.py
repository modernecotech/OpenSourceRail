"""Execute and verify equipped inventories and a native composite method fixture."""
import argparse
import json
from pathlib import Path
from . import ROOT
from .report import run,verify
from .structures import run_structural_fixture,verify_structural_fixture


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('run','verify','structural','verify-structural'))
    parser.add_argument('--output',required=True,type=Path);parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--ccx',type=Path)
    args=parser.parse_args()
    if args.action=='run':value=run(args.output,root=args.root,ccx=args.ccx)
    elif args.action=='verify':value=verify(args.output,root=args.root)
    elif args.action=='structural':value=run_structural_fixture(args.output,ccx=args.ccx,root=args.root)
    else:value=verify_structural_fixture(args.output,root=args.root)
    print(json.dumps(value,sort_keys=True,indent=2,allow_nan=False))


if __name__=='__main__':main()
