"""Execute/read back hot-weather and support-winding engineering scenarios."""
import argparse
import json
from pathlib import Path
from . import ROOT
from .study import run, verify


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('run','verify'))
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps((run if args.action=='run' else verify)(args.output,args.root),sort_keys=True,indent=2))


if __name__=='__main__':main()
