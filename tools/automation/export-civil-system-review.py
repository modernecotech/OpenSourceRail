#!/usr/bin/env python3
"""Export compact confirmed research evidence and the requested root README."""
from pathlib import Path
import argparse
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'design/component-catalogue/src'))
from engineering.civil_exploration.system_report import export
from engineering.civil_exploration.contracts import load,encoded


def history(bundle):
    """Explain recorded algorithm events and expose every changed choice field."""
    rows={r['package_id']:r for p in (bundle/'results').glob('*.json') for r in [load(p)]}
    reasons={'engineering-seed':'Registered control or family engineering seed',
             'random':'Seeded exploration of the registered family/material/system bounds',
             'pareto-evolution':'Bounded offspring exploration for declared cost, mass and working-time tradeoffs'}
    result=[]
    for event in load(bundle/'events.json'):
        current=rows[event['package_id']]['choice'];changes=[]
        for parent in event['parents']:
            if parent not in rows:raise ValueError('retained package history has a missing parent')
            previous=rows[parent]['choice']
            changes.append(dict(parent_package_id=parent,fields={k:dict(before=previous.get(k),after=current.get(k)) for k in previous.keys()|current.keys() if previous.get(k)!=current.get(k)}))
        result.append({**event,'reason_from_recorded_method':reasons[event['method']],'changes_from_parents':changes})
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle',type=Path)
    parser.add_argument('--output',type=Path,default=ROOT/'engineering/civil_exploration/examples/complete-system-review.json')
    parser.add_argument('--update-readme',action='store_true')
    args=parser.parse_args()
    try:
        report=export(args.bundle,args.output,Path(__file__),update_readme=args.update_readme)
        report['history']=history(args.bundle)
        args.output.write_bytes(encoded(report))
        print(args.output);return 0
    except (ValueError,RuntimeError,OSError) as error:
        print(f'Civil system review: {error}',file=sys.stderr);return 1


if __name__=='__main__':raise SystemExit(main())
