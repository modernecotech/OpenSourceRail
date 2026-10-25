import argparse
import json
from pathlib import Path
from . import ROOT


def main(argv=None):
    parser=argparse.ArgumentParser(description='Counted EPM/Halbach next experiments, never physical adoption')
    parser.add_argument('command',choices=('plan','run','verify','publish'))
    parser.add_argument('--source-root',type=Path,default=ROOT)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv)
    if args.command=='plan':
        from .study import study
        value=study(args.source_root)
        answer={k:value[k] for k in ('schema','study_id','summary','counts','next_experiment','physical_accepted')}
    else:
        if args.output is None:parser.error('--output required')
        from . import publication
        answer=getattr(publication,args.command)(args.output,args.source_root)
    print(json.dumps(answer,sort_keys=True,indent=2,allow_nan=False))


if __name__=='__main__':main()
