"""Acquire bounded city-context inputs, or check their offline viewports."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
import json
from pathlib import Path
import tomllib

from . import basemap, render

ROOT = Path(__file__).resolve().parents[2]


def proposal(path):
    """Use the same current stop generator as the city compiler, without duty."""
    from engineering.ferrite_maglev import cities, operating_plan
    path = Path(path)
    design = json.loads(path.read_bytes()); mapped = deepcopy(design)
    assumptions = tomllib.loads(cities.ASSUMPTIONS.read_text())
    if assumptions.get('operating_plan',{}).get('enabled',False):
        features = json.loads(path.with_name(design['city']['slug']+'.corridor.geojson').read_bytes())['features']
        mapped['stations'] = []
        for line in design['lines']:
            stations = sorted((s for s in deepcopy(design['stations']) if s['line']==line['name']),key=lambda s:s['s_m'])
            route = operating_plan.route_path(features,line)
            # This is precisely plan_line's station-layout stage. No vehicle
            # duty, SciPy trajectory or electrical simulation belongs in a
            # basemap acquisition job.
            planned = operating_plan.passenger_layout(route,line,stations,
                design.get('interchanges',[]),service_class=line.get('maglev_service_class','urban'))
            mapped['stations'].extend(planned['stations'])
    return mapped


def acquire(path,cache,*,check=False):
    mapped = proposal(path)
    geojson = path.with_name(mapped['city']['slug']+'.corridor.geojson')
    bounds, zoom = render.viewport(mapped,geojson)
    output = path.with_name('map-context.json.gz')
    if output.exists():
        context = basemap.load(output)
        if not context['layers'].get('roads') or not context['layers'].get('places'):
            raise ValueError('city basemap lacks roads or place context: '+str(path))
        if context['bounds_wsen']==bounds and context['zoom']==zoom:
            return dict(city=mapped['city']['slug'],state='verified-existing',zoom=zoom)
        if check:raise ValueError('stale basemap viewport: '+str(path))
    elif check:raise ValueError('missing basemap context: '+str(path))
    context = basemap.extract(bounds,zoom,output,cache)
    return dict(city=mapped['city']['slug'],state='extracted',zoom=zoom,
        features=context['receipt']['feature_counts'],network_bytes=context['receipt']['network_bytes'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('extract','check'))
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all',action='store_true')
    group.add_argument('--city')
    parser.add_argument('--cache',type=Path,default=ROOT/'build/city-maps/range-cache')
    parser.add_argument('--workers',type=int,default=2,choices=(1,2))
    args=parser.parse_args()
    paths=sorted((ROOT/'cities/catalogue').glob('*/*/*/city.json'))
    paths.sort(key=lambda p:(p.parent.name not in ('Baghdad','Lucknow'),str(p)))
    if args.city:
        paths=[p for p in paths if json.loads(p.read_bytes())['city']['slug']==args.city]
        if len(paths)!=1:parser.error('one known city slug required')
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(acquire,p,args.cache,check=args.action=='check'):p for p in paths}
        for job in as_completed(futures):
            try:print(json.dumps(job.result(),sort_keys=True),flush=True)
            except Exception:
                for future in futures:future.cancel()
                raise
    print(json.dumps(dict(city_count=len(paths),state='current',hidden_renderer_network=False)),flush=True)


if __name__=='__main__':main()
