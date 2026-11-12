"""Run or verify an immutable, demand-led railway outline study."""
import argparse
import json
import re
from pathlib import Path
from engineering.station_rail import ROOT
from . import coordinator

_CITY_SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def _disk_reserve_hold(root, action):
    from engineering.performance import disk_hold_record
    value = disk_hold_record(root, action, coordinator.FLAGS)
    if value is None:
        return False
    print(json.dumps(value, sort_keys=True))
    return True


def _complete_results_exist(output, cities):
    """Avoid reserving compute space for a complete, reusable worker state."""
    output = Path(output).resolve()
    request_path, designs_path = output/'request.json', output/'designs.json'
    if not request_path.is_file() or not designs_path.is_file():
        return False
    try:
        request = json.loads(request_path.read_bytes())
        if (not isinstance(request, dict)
                or request.get('schema') != 'osr-outline-completion-request/1'):
            return False
        stored_cities = request.get('cities')
        if (not isinstance(stored_cities, list) or not stored_cities
                or any(not isinstance(slug, str) or not _CITY_SLUG.fullmatch(slug)
                       for slug in stored_cities)
                or stored_cities != sorted(set(stored_cities))):
            return False
        cities = stored_cities if cities is None else sorted(set(cities))
        if (not isinstance(cities, list) or not cities
                or any(not isinstance(slug, str) or not _CITY_SLUG.fullmatch(slug)
                       for slug in cities)
                or cities != stored_cities):
            return False
        return all((output/'cities'/slug/'result.json').is_file() for slug in cities)
    except (OSError, ValueError, TypeError):
        return False


def main(argv=None,root=ROOT):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('run','verify','approaches','supply','supply-verify',
        'complete','complete-verify','complete-publish','city','city-verify','delivery'))
    parser.add_argument('--output',type=Path)
    parser.add_argument('--brief',type=Path)
    parser.add_argument('--request',type=Path,help='Mapped-city scenario or typed planning revision request')
    parser.add_argument('--city',help='Mapped city slug for a new study')
    parser.add_argument('--state',type=Path,help='Verified full execution state for compact publication')
    parser.add_argument('--cities',nargs='+',help='City slugs; omit to complete every mapped city')
    parser.add_argument('--workers',type=int,default=2,help='Bounded independent calculation processes (1–4)')
    parser.add_argument('--maximum-cities',type=int,help='Invocation budget; unprocessed cities remain resumable')
    parser.add_argument('--replay',action='store_true',help='Independently recalculate stored city and design results')
    parser.add_argument('--scheduler',choices=('python','rust'),default='python',help='Explicit delivery-only backend; city workers remain Python')
    parser.add_argument('--scheduler-binary',type=Path,help='Prebuilt verified Rust delivery scheduler; never built implicitly')
    args=parser.parse_args(argv)
    if args.action!='delivery' and (args.scheduler!='python' or args.scheduler_binary is not None):parser.error('Scheduler options require the explicit delivery action')
    if args.action=='approaches':
        from .approaches import catalogue
        print(json.dumps(catalogue(root=root),sort_keys=True));return
    if args.output is None:parser.error('--output is required for run and verify')
    if args.action=='delivery':
        if args.request is None:parser.error('--request sealed current city-record JSON is required')
        from .delivery_plan import run_delivery
        result=run_delivery(args.request,args.output,root=root,
            scheduler_backend=args.scheduler,scheduler_binary=args.scheduler_binary)
        print(json.dumps(result,sort_keys=True));return
    if args.action in ('city','city-verify'):
        from . import city_workflow
        if args.action=='city':
            value=json.loads(args.request.read_bytes()) if args.request else {}
            if args.city:value['city_slug']=args.city
            if 'city_slug' not in value:parser.error('--city or a city request is required')
            if _disk_reserve_hold(root,'outline-city'):
                return 3
            result=city_workflow.run(value,args.output,root=root)
        else:result=city_workflow.verify(args.output,root=root,replay=args.replay)
        print(json.dumps(result,sort_keys=True));return
    if args.action.startswith('complete'):
        from . import completion
        if args.action=='complete':
            reusable = args.workers > 1 and _complete_results_exist(args.output,args.cities)
            if not reusable and _disk_reserve_hold(root,'outline-complete'):
                return 3
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
        if _disk_reserve_hold(root,'outline-run'):
            return 3
        inputs=json.loads(args.brief.read_bytes()) if args.brief else {}
        result=coordinator.run(args.output,brief=inputs.get('brief'),variables=inputs.get('variables'),pricing_scenario=inputs.get('pricing_scenario'),root=root)
    print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
