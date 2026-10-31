"""Current city geography catalogue with explicit holds on performance publication."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
import os

from . import ROOT, FLAGS
from .common import identity, encoded, source_map

FAMILY = 'wheel_rail_station_lim'
IDS = ('candidate_id', 'body_candidate_id', 'support_component_id', 'propulsion_component_id')
INDEX = 'docs/design-engine/current/cities.json'
INDEX_MANIFEST = 'docs/design-engine/current/city-catalogue-manifest.json'
CODE = 'engineering/station_rail/cities.py'
HOLD = ('v0.6 city performance regeneration is held pending a validated station-drive envelope, '
        'wheelrail braking and protection evidence, complete vehicle and civil interfaces, '
        'and an equal-service cost comparison. City routes and stops remain unqualified planning inputs.')


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def write(path, raw):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp-' + str(os.getpid()))
    temporary.write_bytes(raw); temporary.replace(path)


def catalogue(root=ROOT):
    """Return geographic availability, never a fallback engineering result."""
    root = Path(root).resolve(); rows = []
    for path in sorted((root/'cities/catalogue').glob('*/*/*/city.json')):
        value = json.loads(path.read_bytes()); rel = path.parent.relative_to(root).as_posix()
        route_path = rel+'/'+value['city']['slug']+'.corridor.geojson'
        rows.append(dict(slug=value['city']['slug'], name=value['name'], country=value['city']['country'],
            path=rel, execution='held',geography_available=True,performance_evaluated=False,
            totals=None,summary_path=None,geography_path=rel+'/city.json',
            route_geography_path=route_path,route_geography_available=(root/route_path).is_file()))
    if len({r['slug'] for r in rows}) != len(rows): raise ValueError('Unique city slugs required')
    return rows


def find_city(value, root=ROOT):
    root = Path(root).resolve(); path = Path(value)
    path = path if path.is_absolute() else root/path
    if path.is_dir(): path /= 'city.json'
    if path.is_file() and path.name == 'city.json':
        path = path.resolve(); path.relative_to(root/'cities/catalogue'); return path
    rows = [r for r in catalogue(root) if r['slug'].casefold() == str(value).casefold()]
    if len(rows) != 1: raise ValueError('Unknown city slug: '+str(value))
    return root/rows[0]['path']/'city.json'


def _baseline(record, root):
    from engineering.development_baseline import selection
    canonical = selection.load(root); selected = canonical if record is None else record
    if selected.get('selection_id') != canonical['selection_id']:
        raise ValueError('City and current selection identity differs')
    if canonical['selection']['family'] != FAMILY: raise ValueError('Explicit v0.6 wheelrail LIM selection required')
    car = selected['vehicle']; expected = canonical['vehicle']
    for key in IDS:
        if car.get(key) != expected[key]: raise ValueError('City physical identity differs: '+key)
    if car != expected: raise ValueError('City vehicle differs from selected physical bundle')
    if any(selected.get(k) is not False for k in FLAGS): raise ValueError('City selection cannot grant qualification')
    return canonical, car


def evaluate_city(value,baseline=None,root=ROOT,civil=None):
    root=Path(root).resolve(); path=find_city(value,root); selected,car=_baseline(baseline,root)
    geographic=json.loads(path.read_bytes()); rel=path.parent.relative_to(root).as_posix()
    source=dict(selected['source_sha256']); source.update(source_map(root,(CODE,'engineering/development_baseline/cities.py')))
    source[path.relative_to(root).as_posix()]=digest(path)
    route_path=rel+'/'+geographic['city']['slug']+'.corridor.geojson'
    map_path=route_path if (root/route_path).is_file() else rel+'/engineering/maglev/network.svg'
    result=dict(schema='osr-current-city-hold/1',family=FAMILY,version='0.6.0',
        **{k:car[k] for k in IDS},selection_id=selected['selection_id'],development_default=True,
        execution='held',reason=HOLD,source_sha256=dict(sorted(source.items())),
        city=dict(slug=geographic['city']['slug'],name=geographic['name'],country=geographic['city']['country']),
        city_path=rel,geography_available=True,performance_evaluated=False,totals=None,
        geography=dict(city_json_path=path.relative_to(root).as_posix(),city_json_sha256=digest(path),
            route_geography_path=route_path,route_geography_sha256=digest(root/route_path) if (root/route_path).is_file() else None,
            map_path=map_path,map_available=(root/map_path).is_file(),underlying_city_details_preserved=True,
            source_route_geometry_changed=False,basemaps_regenerated=False,route_and_sites_qualified=False),
        historical=dict(selected_for_v06=False,
            scope='Non-geographic service and performance records are not imported into the selected candidate'),
        city_performance_regeneration_authorized=False,physical_train_journeys_executed=0,**FLAGS)
    result['evaluation_id']=identity(result); return result


def publish_city(value,baseline=None,output=None,root=ROOT,civil=None,update_readme=False):
    """Return the hold without modifying any city packet or front page."""
    return evaluate_city(value,baseline,root,civil)


def read_catalogue(root=ROOT):
    path=Path(root)/INDEX
    if not path.is_file(): raise FileNotFoundError('Current city catalogue has not been generated: '+INDEX)
    value=json.loads(path.read_bytes())
    if value.get('schema')!='osr-current-city-catalogue/1' or value.get('family')!=FAMILY:
        raise ValueError('Current catalogue is not the v0.6 geographic hold register')
    return value



@lru_cache(maxsize=512)
def _context_geography(path_name, signature):
    path=Path(path_name); raw=path.read_bytes(); value=json.loads(raw)
    actual=path.stat()
    if (actual.st_size,actual.st_mtime_ns,actual.st_ctime_ns,actual.st_ino)!=signature:
        raise ValueError('Route context changed during geographic scan')
    largest=None; count=0
    for line in value.get('lines',[]):
        stops=sorted(line['stations'],key=lambda r:r['s_m'])
        for a,b in zip(stops,stops[1:]):
            row=dict(line=line['line'],from_station=a['id'],to_station=b['id'],distance_m=b['s_m']-a['s_m'])
            count+=1
            if largest is None or row['distance_m']>largest['distance_m']:largest=row
    return dict(longest=largest,adjacent_gaps=count,sha256=sha256(raw).hexdigest())


def route_geography(root=ROOT,rows=None):
    """Inspect current city stop chainages only; do not run a service model."""
    root=Path(root).resolve(); rows=catalogue(root) if rows is None else rows
    largest=None; count=0; sources={}; missing=[]
    for city in rows:
        name=city['geography_path']; path=root/name
        if not path.is_file():missing.append(name);continue
        raw=path.read_bytes(); value=json.loads(raw); sources[name]=sha256(raw).hexdigest()
        grouped={}
        for station in value.get('stations',[]):grouped.setdefault(station.get('line'),[]).append(station)
        local=None; local_count=0
        # Older synthetic fixtures without station geography retain only this
        # geography-only compatibility path. Current city inputs all use the
        # city.json station table above.
        if not grouped:
            fallback=path.parent/'engineering/maglev/summary.json'
            if fallback.is_file():
                summary=json.loads(fallback.read_bytes())
                grouped={line['line']:line.get('stations',[]) for line in summary.get('lines',[])}
                sources[fallback.relative_to(root).as_posix()]=digest(fallback)
        for line, stops in grouped.items():
            stops=sorted(stops,key=lambda row:row.get('s_m',0.))
            for first,last in zip(stops,stops[1:]):
                gap=float(last['s_m'])-float(first['s_m']);local_count+=1
                candidate=dict(line=line,from_station=first['id'],to_station=last['id'],distance_m=gap)
                if local is None or candidate['distance_m']>local['distance_m']:local=candidate
        count+=local_count
        if local is not None and (largest is None or local['distance_m']>largest['distance_m']):
            largest=dict(local,city=city['name'],city_slug=city['slug'],source_path=name,source_sha256=sources[name],
                scope='Adjacent current city stops ordered by chainage; geography only')
    return dict(longest_gap=largest,adjacent_gap_count=count,missing_route_contexts=missing,
        source_route_context_sha256=dict(sorted(sources.items())),performance_models_executed=0)


def _record(root,baseline):
    selected,car=_baseline(baseline,root); rows=catalogue(root)
    source=dict(selected['source_sha256']); source.update(source_map(root,(CODE,'engineering/development_baseline/cities.py')))
    geography={r['geography_path']:digest(root/r['geography_path']) for r in rows}; source.update(geography)
    route_files={r['route_geography_path']:digest(root/r['route_geography_path']) for r in rows
        if r.get('route_geography_available')}
    source.update(route_files)
    routes=route_geography(root,rows); source.update(routes['source_route_context_sha256'])
    counts=dict(city_count=len(rows),cities_held=len(rows),cities_with_geography=len(rows),
        cities_with_v06_performance=0,current_city_frontdoors_regenerated=False,total_trainsets=None)
    value=dict(schema='osr-current-city-catalogue/1',family=FAMILY,**{k:car[k] for k in IDS},selection_id=selected['selection_id'],
        city_count=len(rows),cities=rows,summary=counts,longest_gap=routes['longest_gap'],
        route_geography=routes,execution='held',reason=HOLD,development_default=True,
        source_sha256=dict(sorted(source.items())),source_city_json_sha256=geography,
        physical_train_journeys_executed=0,city_performance_packages_written=0,**FLAGS)
    value['evaluation_id']=identity(value); return value


def publish_all(output=None,baseline=None,root=ROOT,civil=None,update_readmes=False,*,destination=None):
    """Write only the global hold register. All existing city bytes are preserved."""
    root=Path(root).resolve(); output=root if output is None and destination is None else Path(destination if destination is not None else output).resolve()
    value=_record(root,baseline); write(output/INDEX,encoded(value))
    receipt=dict(schema='osr-current-city-catalogue-publication/1',**{k:value[k] for k in IDS},selection_id=value['selection_id'],
        evaluation_id=value['evaluation_id'],files_sha256={INDEX:digest(output/INDEX)},summary=value['summary'],
        development_default=True,city_performance_packages_written=0,**FLAGS)
    write(output/INDEX_MANIFEST,encoded(receipt)); return value


def verify_all(output=None,baseline=None,root=ROOT,civil=None,replay=True):
    root=Path(root).resolve(); output=root if output is None else Path(output).resolve()
    expected=_record(root,baseline); actual=read_catalogue(output)
    if actual!=expected: raise ValueError('City geographic hold register differs from current sources')
    receipt=json.loads((output/INDEX_MANIFEST).read_bytes())
    for key in ('selection_id',*IDS,'evaluation_id'):
        if receipt.get(key)!=actual[key]: raise ValueError('City hold receipt identity differs')
    if receipt.get('files_sha256')!={INDEX:digest(output/INDEX)}: raise ValueError('City hold payload differs')
    if any(receipt.get(k) is not False for k in FLAGS) or receipt.get('development_default') is not True:
        raise ValueError('City hold receipt cannot grant qualification')
    if receipt.get('city_performance_packages_written')!=0: raise ValueError('City performance was not authorized for regeneration')
    return dict(verified=True,replayed=replay,city_count=actual['city_count'],cities_held=actual['city_count'],
        selection_id=actual['selection_id'],candidate_id=actual['candidate_id'],source_and_payload_integrity=True,
        city_performance_packages_written=0,physical_acceptance=False)
