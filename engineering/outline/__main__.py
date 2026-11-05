"""Run or verify an immutable, demand-led railway outline study."""
import argparse
import json
from pathlib import Path
from engineering.station_rail import ROOT
from . import coordinator

def main(argv=None,root=ROOT):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('run','verify','approaches','supply','supply-verify',
        'complete','complete-verify','complete-publish','city','city-verify'))
    parser.add_argument('--output',type=Path)
    parser.add_argument('--brief',type=Path)
    parser.add_argument('--request',type=Path,help='Mapped-city scenario or typed planning revision request')
    parser.add_argument('--city',help='Mapped city slug for a new study')
    parser.add_argument('--state',type=Path,help='Verified full execution state for compact publication')
    parser.add_argument('--cities',nargs='+',help='City slugs; omit to complete every mapped city')
    parser.add_argument('--workers',type=int,default=2,help='Bounded independent calculation processes (1–4)')
    parser.add_argument('--maximum-cities',type=int,help='Invocation budget; unprocessed cities remain resumable')
    parser.add_argument('--replay',action='store_true',help='Independently recalculate stored city and design results')
    args=parser.parse_args(argv)
    if args.action=='approaches':
        from .approaches import catalogue
        print(json.dumps(catalogue(root=root),sort_keys=True));return
    if args.output is None:parser.error('--output is required for run and verify')
    if args.action in ('city','city-verify'):
        from . import city_workflow
        if args.action=='city':
            value=json.loads(args.request.read_bytes()) if args.request else {}
            if args.city:value['city_slug']=args.city
            if 'city_slug' not in value:parser.error('--city or a city request is required')
            result=city_workflow.run(value,args.output,root=root)
        else:result=city_workflow.verify(args.output,root=root,replay=args.replay)
        print(json.dumps(result,sort_keys=True));return
    if args.action.startswith('complete'):
        from . import completion
        if args.action=='complete':
            result=completion.run(args.output,root=root,cities=args.cities,workers=args.workers,
                maximum_cities=args.maximum_cities)
        elif args.action=='complete-verify':
            result=completion.verify(args.output,root=root,replay=args.replay)
        else:
            if args.state is None:parser.error('--state is required for complete-publish')
            from .completion_publication import publish
            result=publish(args.state,args.output,root=root)
        print(json.dumps(result,sort_keys=True));return
    if args.action in ('supply','supply-verify'):
        from . import supply_economics as supply
        result=supply.publish(args.output,root=root) if args.action=='supply' else supply.verify(args.output,root=root)
        print(json.dumps(result,sort_keys=True));return
    if args.action=='verify': result=coordinator.verify(args.output,root=root)
    else:
        inputs=json.loads(args.brief.read_bytes()) if args.brief else {}
        result=coordinator.run(args.output,brief=inputs.get('brief'),variables=inputs.get('variables'),pricing_scenario=inputs.get('pricing_scenario'),root=root)
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
