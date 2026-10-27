#!/usr/bin/env python3
"""Historical v0.5 city packages; reproduce in their pinned checkout."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    index = sub.add_parser('index')
    index.add_argument('--output', type=Path)
    index.add_argument('--check', action='store_true')
    for action in ('plan','run'):
        command = sub.add_parser(action)
        command.add_argument('--city',nargs='+',required=True)
        if action=='run':
            command.add_argument('--output',type=Path,help='Isolated output directory per selected city.')
    args = parser.parse_args()
    from engineering.ferrite_maglev import navigation
    if args.action=='index':
        data = navigation.city_index()
        output = args.output or ROOT/'docs/capabilities/city-artifacts.json'
        value = json.dumps(data,indent=2,sort_keys=True)+'\n'
        if args.check:
            if not output.is_file() or output.read_text()!=value:
                raise ValueError('city artifact index differs')
        else:
            output.parent.mkdir(parents=True,exist_ok=True)
            output.write_text(value)
        print(json.dumps(dict(city_count=len(data['cities']),family=data['family'],physical_release=False)))
    elif args.action=='plan':
        print(json.dumps(navigation.selected_plan(args.city),indent=2))
    else:
        print(json.dumps(navigation.run_selected(args.city,output=args.output),indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError,KeyError,FileNotFoundError) as exc:
        raise SystemExit('City catalogue held: '+str(exc))
