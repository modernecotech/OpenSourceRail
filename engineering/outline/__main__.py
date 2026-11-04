"""Run or verify an immutable, demand-led railway outline study."""
import argparse
import json
from pathlib import Path
from . import coordinator

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('run','verify','approaches'))
    parser.add_argument('--output',type=Path)
    parser.add_argument('--brief',type=Path)
    args=parser.parse_args()
    if args.action=='approaches':
        from .approaches import catalogue
        print(json.dumps(catalogue(),sort_keys=True));return
    if args.output is None:parser.error('--output is required for run and verify')
    if args.action=='verify': result=coordinator.verify(args.output)
    else:
        inputs=json.loads(args.brief.read_bytes()) if args.brief else {}
        result=coordinator.run(args.output,brief=inputs.get('brief'),variables=inputs.get('variables'))
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
