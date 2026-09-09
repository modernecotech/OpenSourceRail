#!/usr/bin/env python3
"""Sample pinned OpenLandMap soilDB layers and prepare civil investigation inputs.

Network access is explicit (--fetch). Retained city samples support offline
regeneration. Pedological predictions never become foundation design values.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'engineering/data/soildb/sources.json'
CACHE = ROOT / 'build/engineering/soildb'
PROPERTIES = ('clay', 'sand', 'silt', 'bd.core', 'soc', 'ph.h2o')
DEPTHS = ('0..30cm', '30..60cm', '60..100cm')
STATS = ('mean', 'p16', 'p84')
UNITS = {'clay': '%', 'sand': '%', 'silt': '%', 'bd.core': 'kg/m3', 'soc': 'g/kg', 'ph.h2o': 'pH'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n')
    temporary.replace(path)


def key(lon, lat):
    return f'{lon:.8f},{lat:.8f}'


def load_sources():
    source = json.loads(SOURCES.read_text())
    if sha(SOURCES.parent / 'OpenLandMap_soildb_COGS.csv') != source['catalogue_sha256']:
        raise ValueError('Pinned soilDB catalogue hash has changed')
    expected = {(p, d, s) for p in PROPERTIES for d in DEPTHS for s in STATS}
    actual = [(a['property'], a['depth_interval'], a['statistic']) for a in source['assets']]
    if len(actual) != len(expected) or set(actual) != expected:
        raise ValueError('Soil source lock must contain every property/depth/uncertainty layer exactly once')
    if not math.isfinite(source['sampling_interval_m']) or source['sampling_interval_m'] <= 0:
        raise ValueError('Soil route sampling interval must be finite and positive')
    return source


def sample_locations(city_dir, interval_m=1000):
    """Every station and civil-segment end/midpoint, plus <=1 km route spacing."""
    from pyproj import Geod
    geod = Geod(ellps='WGS84')
    layers = city_dir / 'engineering/gis/layers'
    points = []
    for feature in json.loads((layers / 'stations.geojson').read_text())['features']:
        p = feature['properties']; lon, lat = feature['geometry']['coordinates'][:2]
        points.append(dict(sample_id='station:' + p['id'], scope_type='station', scope_id=p['id'], line=p['line'], civil_class='station', chainage_m=p['chainage_m'], lon=lon, lat=lat))
    for feature in json.loads((layers / 'civil_segments.geojson').read_text())['features']:
        p = feature['properties']; coords = feature['geometry']['coordinates']
        if feature['geometry']['type'] != 'LineString' or len(coords) < 2:
            raise ValueError('Civil soil sampling requires nonempty LineStrings')
        legs = [geod.inv(*a[:2], *b[:2]) for a, b in zip(coords, coords[1:])]
        length = sum(leg[2] for leg in legs)
        if length <= 0:
            raise ValueError(f"Zero-length civil segment {p['id']}")
        fractions = sorted({0., .5, 1., *(min(i * interval_m / length, 1.) for i in range(1, math.ceil(length / interval_m)))})
        for i, fraction in enumerate(fractions):
            distance = fraction * length; travelled = 0.
            for j, (azimuth, _, leg_length) in enumerate(legs):
                if distance <= travelled + leg_length or j == len(legs) - 1:
                    lon, lat, _ = geod.fwd(*coords[j][:2], azimuth, max(0., distance - travelled))
                    break
                travelled += leg_length
            chainage = p['from_chainage_m'] + fraction * (p['to_chainage_m'] - p['from_chainage_m'])
            points.append(dict(sample_id=f"segment:{p['id']}:{i:04d}", scope_type='civil_segment', scope_id=p['id'], line=p['line'], civil_class=p['civil_class'], chainage_m=round(chainage, 3), lon=lon, lat=lat))
    for point in points:
        point['lon'] = round(point['lon'], 8); point['lat'] = round(point['lat'], 8)
    return sorted(points, key=lambda p: p['sample_id'])


def decode(raw, masked, scale, offset, prop):
    if masked:
        return None
    value = float(raw) * scale + offset
    # The upstream bd.core filename specifies g/cm3 and its TIFF scale is
    # 0.01; the catalogue unit column says kg/m3. Convert g/cm3 to kg/m3.
    if prop == 'bd.core':
        value *= 1000.
    bounds = {'clay': (0, 100), 'sand': (0, 100), 'silt': (0, 100), 'bd.core': (0, 3000), 'soc': (0, 1000), 'ph.h2o': (0, 14)}
    if not math.isfinite(value) or not bounds[prop][0] <= value <= bounds[prop][1]:
        raise ValueError(f'Invalid scaled {prop} value {value}')
    return round(value, 6)


def fetch_asset(asset, coordinates, cache_dir=CACHE):
    import rasterio
    import requests
    from rasterio.windows import Window
    cache_dir.mkdir(parents=True, exist_ok=True)
    token = digest({'asset': asset, 'coordinates': coordinates, 'scaling_schema': 'soilDB-TIFF-physical-units-v1'})
    target = cache_dir / f'{token}.json'
    if target.exists():
        result = json.loads(target.read_text())
        if result['request_sha256'] != token or result['values_sha256'] != digest(result['values']):
            raise ValueError(f'Corrupt soil cache {target}')
        return result
    response = requests.head(asset['url'], timeout=60)
    response.raise_for_status()
    metadata = {k: response.headers.get(k) for k in ('ETag', 'Last-Modified', 'Content-Length')}
    values = {}
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif', GDAL_HTTP_TIMEOUT='60', GDAL_HTTP_MAX_RETRY='3', GDAL_HTTP_RETRY_DELAY='1', GDAL_CACHEMAX=64 * 1024 * 1024):
        with rasterio.open(asset['url']) as source:
            if source.crs.to_epsg() != 4326:
                raise ValueError('Pinned soil layers must use EPSG:4326')
            scale, offset = source.scales[0], source.offsets[0]
            if not math.isclose(scale, asset['catalogue_scale']):
                raise ValueError(f"Scale differs from source lock: {asset['id']}")
            blocks = defaultdict(list)
            height, width = source.block_shapes[0]
            for lon, lat in coordinates:
                row, col = source.index(lon, lat)
                if 0 <= row < source.height and 0 <= col < source.width:
                    blocks[(row // height, col // width)].append((lon, lat, row, col))
                else:
                    values[key(lon, lat)] = None
            for (block_row, block_col), locations in sorted(blocks.items()):
                r0, c0 = block_row * height, block_col * width
                data = source.read(1, window=Window(c0, r0, min(width, source.width-c0), min(height, source.height-r0)), masked=True)
                for lon, lat, row, col in locations:
                    cell = data[row-r0, col-c0]
                    values[key(lon, lat)] = decode(cell.data if hasattr(cell, 'mask') else cell, bool(getattr(cell, 'mask', False)), scale, offset, asset['property'])
            metadata.update(scale=scale, offset=offset, nodata=source.nodata, crs=str(source.crs), pixel_size_degrees=list(source.res), width=source.width, height=source.height)
    after = requests.head(asset['url'], timeout=60); after.raise_for_status()
    if after.headers.get('ETag') != metadata['ETag']:
        raise ValueError('Soil source changed during sampling')
    result = dict(asset=asset, request_sha256=token, metadata=metadata, values=values, values_sha256=digest(values))
    write_json(target, result)
    return result


def investigation_flags(profile):
    """Transparent prioritisation triggers, not soil classes or acceptance limits."""
    flags = set()
    for values in profile.values():
        if any(values.get(f'{p}_{s}') is None for p in PROPERTIES for s in STATS):
            flags.add('coverage-gap')
        for p in PROPERTIES:
            lo, hi = values.get(p+'_p16'), values.get(p+'_p84')
            if lo is not None and hi is not None and lo > hi:
                flags.add('invalid-prediction-interval')
        if (values.get('clay_p84') or 0) >= 35:
            flags.add('fine-soil-plasticity-and-shrink-swell-tests')
        if (values.get('silt_p84') or 0) >= 50:
            flags.add('silt-moisture-frost-and-erosion-review')
        if (values.get('sand_p84') or 0) >= 70:
            flags.add('granular-density-and-groundwater-tests')
        if (values.get('soc_p84') or 0) >= 50:
            flags.add('organic-content-and-compressibility-tests')
        ph = values.get('ph.h2o_p16')
        if ph is not None and ph < 5.5:
            flags.add('acidic-soil-durability-testing')
    return sorted(flags)


def generate_city(city_dir, locations, fetched=None):
    output = city_dir / 'engineering/soil'; output.mkdir(parents=True, exist_ok=True)
    source = load_sources()
    sample_path = output / 'samples.csv'
    input_paths = {'design': city_dir / 'design.toml', 'stations': city_dir / 'engineering/gis/layers/stations.geojson', 'civil_segments': city_dir / 'engineering/gis/layers/civil_segments.geojson', 'source_lock': SOURCES}
    input_hashes = {k: sha(v) for k, v in input_paths.items()}
    fields = [*locations[0], 'depth_interval', *[p+'_'+s for p in PROPERTIES for s in STATS]]
    if fetched is not None:
        lookup = {(a['asset']['property'], a['asset']['depth_interval'], a['asset']['statistic']): a for a in fetched}
        rows = []
        for point in locations:
            for depth in DEPTHS:
                row = dict(point, depth_interval=depth)
                for p in PROPERTIES:
                    for stat in STATS:
                        row[p+'_'+stat] = lookup[(p, depth, stat)]['values'][key(point['lon'], point['lat'])]
                rows.append(row)
        with sample_path.open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator='\n'); writer.writeheader(); writer.writerows(rows)
        receipt = {'input_sha256': input_hashes, 'locations_sha256': digest(locations), 'samples_sha256': sha(sample_path), 'assets': [dict(asset=a['asset'], metadata=a['metadata']) for a in fetched]}
        write_json(output / 'source-receipt.json', receipt)
    else:
        receipt = json.loads((output / 'source-receipt.json').read_text())
        if receipt['input_sha256'] != input_hashes or receipt['locations_sha256'] != digest(locations) or receipt['samples_sha256'] != sha(sample_path):
            raise ValueError(f'{city_dir}: soil samples changed or inputs stale; fetch controlled data again')
    with sample_path.open() as handle:
        rows = list(csv.DictReader(handle))
    profiles = defaultdict(dict)
    for row in rows:
        profiles[row['sample_id']][row['depth_interval']] = {p+'_'+s: float(row[p+'_'+s]) if row[p+'_'+s] != '' else None for p in PROPERTIES for s in STATS}
    expected = {(p['sample_id'], d) for p in locations for d in DEPTHS}
    if len(rows) != len(expected) or {(r['sample_id'], r['depth_interval']) for r in rows} != expected:
        raise ValueError('Soil samples do not cover exactly the current locations/depths')
    scopes = {}; features = []; counts = Counter(); complete = 0
    for point in locations:
        profile = profiles[point['sample_id']]; flags = investigation_flags(profile); counts.update(flags)
        complete += 'coverage-gap' not in flags
        scope_key = point['scope_type'] + ':' + point['scope_id']
        scope = scopes.setdefault(scope_key, dict(scope_type=point['scope_type'], scope_id=point['scope_id'], line=point['line'], civil_class=point['civil_class'], sample_ids=[], investigation_flags=set()))
        scope['sample_ids'].append(point['sample_id']); scope['investigation_flags'].update(flags)
        features.append(dict(type='Feature', geometry=dict(type='Point', coordinates=[point['lon'], point['lat']]), properties=dict(point, investigation_flags=flags)))
    for scope in scopes.values():
        scope['investigation_flags'] = sorted(scope['investigation_flags'])
        scope['required_field_work'] = ['Verify made ground, stratigraphy and groundwater; obtain representative laboratory classification and compaction/CBR evidence.']
        if scope['civil_class'] in ('elevated', 'bridge', 'station'):
            scope['required_field_work'].append('Investigate support locations to influence depth; determine bearing, settlement and lateral response before choosing foundation dimensions.')
        scope['foundation_type'] = None
        scope['allowable_bearing_kpa'] = None
        scope['groundwater_depth_m'] = None
        scope['status'] = 'desktop-prioritised-field-investigation-required'
    civil_plan = dict(schema_version=1, design_sha256=input_hashes['design'], soil_samples_sha256=sha(sample_path), deployment_release_ready=False, scopes=list(scopes.values()))
    write_json(output / 'civil-investigation-plan.json', civil_plan)
    write_json(output / 'sample-locations.geojson', dict(type='FeatureCollection', features=features))
    design = tomllib.loads((city_dir / 'design.toml').read_text())
    ranges = []
    for depth in DEPTHS:
        for prop in PROPERTIES:
            values = [profile[depth] for profile in profiles.values()]
            means = [v[prop+'_mean'] for v in values if v[prop+'_mean'] is not None]
            lower = [v[prop+'_p16'] for v in values if v[prop+'_p16'] is not None]
            upper = [v[prop+'_p84'] for v in values if v[prop+'_p84'] is not None]
            ranges.append(dict(property=prop, unit=UNITS[prop], depth_interval=depth,
                               available_mean_count=len(means),
                               mean_min=min(means) if means else None, mean_max=max(means) if means else None,
                               p16_min=min(lower) if lower else None, p84_max=max(upper) if upper else None))
    summary = dict(schema_version=1, property_sample_ranges=ranges, city=design['city']['slug'], status='desktop-soil-screening-complete' if complete == len(locations) else 'desktop-soil-screening-with-coverage-gaps', desktop_screen_generated=True, deployment_release_ready=False, ground_design_validated=False, input_sha256=input_hashes, source_paths={k:str(v.relative_to(ROOT)) for k,v in input_paths.items()}, generator_sha256=sha(__file__), source_receipt_sha256=sha(output / 'source-receipt.json'), samples_sha256=sha(sample_path), civil_plan_sha256=sha(output / 'civil-investigation-plan.json'), sample_locations_sha256=sha(output / 'sample-locations.geojson'), sample_count=len(locations), complete_profile_count=complete, missing_profile_count=len(locations)-complete, station_count=sum(p['scope_type']=='station' for p in locations), civil_segment_count=sum(s['scope_type']=='civil_segment' for s in scopes.values()), investigation_flag_counts=dict(sorted(counts.items())), units=UNITS, depth_intervals=list(DEPTHS), prediction_interval='p16-p84; nominal 68% prediction interval; not engineering design characteristic values', sampling_resolution_m=120, sampling_spacing_m=source['sampling_interval_m'], density_unit_reconciliation='TIFF/filename g/cm3 × 1000 = kg/m3; upstream catalogue unit label differs', limitations=['No bearing capacity, CBR, friction angle, cohesion, groundwater, contamination, sulfate/chloride or deep stratigraphy is inferred from these maps.', 'Desert, water, urban fill and other nodata remain unknown; no nearest-pixel or climate-based substitution.', 'Texture fractions are independent predictions; they are not renormalised or converted to a geotechnical soil class.', 'Prioritisation thresholds are editable OSR screening rules, not statutory limits or evidence of a hazard.', 'No excavation depths, foundation dimensions, treatment quantities or civil costs are changed from pedological predictions.'])
    write_json(output / 'summary.json', summary)
    lines = [f"# {city_dir.name} civil soil screening", '', f"{len(locations):,} route/station sample locations; {complete:,} complete profiles; {len(locations)-complete:,} profiles with missing data.", '', 'Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.', '', 'The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.', '', '| Investigation trigger | Sample locations |', '|---|---:|', *[f'| {flag} | {count} |' for flag, count in sorted(counts.items())], '', *['- '+s for s in summary['limitations']], '', 'Source: [OpenLandMap soilDB](https://github.com/openlandmap/soildb), Hengl et al., DOI 10.5194/essd-2025-336, CC BY 4.0. Exact source revision, URLs and raster metadata are retained in the receipt.', '']
    lines += ['## Sampled property ranges', '',
              'Ranges below span the sampled locations; they are not a city-wide characteristic soil value. The uncertainty envelope spans the lowest p16 to highest p84.', '',
              '| Depth | Property | Unit | Mean range | Uncertainty envelope | Available locations |',
              '|---|---|---|---:|---:|---:|']
    def number(value): return 'unknown' if value is None else f'{value:g}'
    for r in ranges:
        lines.append(f"| {r['depth_interval']} | {r['property']} | {r['unit']} | {number(r['mean_min'])}–{number(r['mean_max'])} | {number(r['p16_min'])}–{number(r['p84_max'])} | {r['available_mean_count']} |")
    lines.append('')
    (output / 'README.md').write_text('\n'.join(lines))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--design', type=Path)
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--fetch', action='store_true')
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    if args.all == bool(args.design):
        parser.error('choose --design or --all')
    designs = sorted((ROOT / 'cities/catalogue').glob('*/*/*/design.toml')) if args.all else [args.design.resolve()]
    source = load_sources()
    cities = [(p.parent, sample_locations(p.parent, source['sampling_interval_m'])) for p in designs]
    coordinates = sorted({(p['lon'], p['lat']) for _, points in cities for p in points})
    fetched = None
    if args.fetch:
        fetched = []
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            tasks = {pool.submit(fetch_asset, a, coordinates): a for a in source['assets']}
            for task in as_completed(tasks):
                result = task.result(); fetched.append(result)
                print(f"sampled {result['asset']['id']}: {sum(v is not None for v in result['values'].values())}/{len(coordinates)}", flush=True)
        fetched.sort(key=lambda a:a['asset']['id'])
    for city_dir, points in cities:
        report = generate_city(city_dir, points, fetched)
        print(f"{report['city']}: {report['status']} ({report['complete_profile_count']}/{report['sample_count']})", flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
