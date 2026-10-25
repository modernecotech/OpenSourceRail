"""Run, verify or publish the separately identified finite 3D continuation study."""
import argparse
import json
from pathlib import Path
from . import run,verify,publish


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    r=sub.add_parser('run');r.add_argument('--root',type=Path,required=True);r.add_argument('--output',type=Path,required=True);r.add_argument('--getdp',type=Path,required=True);r.add_argument('--reuse-mesh-root',type=Path);r.add_argument('--cases',nargs='+',choices=('coarse','fine','expanded'),default=['coarse','fine','expanded'])
    v=sub.add_parser('verify');v.add_argument('--root',type=Path);v.add_argument('--output',type=Path,required=True)
    q=sub.add_parser('publish');q.add_argument('--root',type=Path);q.add_argument('--run-dir',type=Path,required=True);q.add_argument('--output',type=Path,required=True)
    a=p.parse_args();args=vars(a);action=args.pop('action');output=args.pop('output');result={'run':run,'verify':verify,'publish':publish}[action](output,**args);print(json.dumps(result,sort_keys=True,indent=2,allow_nan=False))


if __name__=='__main__':main()
