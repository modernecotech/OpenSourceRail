#!/usr/bin/env python3
"""Index/plan/rebuild primary maglev city packages; legacy generation is explicit."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--legacy',action='store_true')
    sub = parser.add_subparsers(dest='action', required=True)
    index = sub.add_parser('index')
    index.add_argument('--output',type=Path)
    index.add_argument('--check',action='store_true')
    for action in ('plan','run'):
        command = sub.add_parser(action)
        command.add_argument('--city',nargs='+',required=True)
        if action=='run':
            command.add_argument('--output',type=Path,help='Isolated primary output directory per city; unavailable for legacy generation.')
    args = parser.parse_args()
    if args.legacy:
        from engineering.design_engine import catalogue as adapter
    else:
        from engineering.ferrite_maglev import navigation as adapter
    if args.action=='index':
        data = adapter.index() if args.legacy else adapter.city_index()
        output = args.output or ROOT/('build/legacy-capabilities/city-artifacts.json' if args.legacy else 'docs/capabilities/city-artifacts.json')
        value = json.dumps(data,indent=2,sort_keys=True)+'\n'
        if args.check:
            if not output.is_file() or output.read_text()!=value:
                raise ValueError('city artifact index differs')
        else:
            output.parent.mkdir(parents=True,exist_ok=True)
            output.write_text(value)
        print(json.dumps(dict(city_count=len(data['cities']),family=data.get('family','wheel-rail-reference'),physical_release=False)))
    elif args.action=='plan':
        print(json.dumps(adapter.selected_plan(args.city),indent=2))
    else:
        if args.legacy and args.output is not None:
            parser.error('--output is supported only by primary maglev generation')
        data = adapter.run_selected(args.city) if args.legacy else adapter.run_selected(args.city,output=args.output)
        print(json.dumps(data,indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError,KeyError,FileNotFoundError) as exc:
        raise SystemExit('City catalogue held: '+str(exc))
