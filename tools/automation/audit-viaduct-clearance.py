#!/usr/bin/env python3
"""Retain footprint/height/terrain evidence and screen candidate viaducts."""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
import tomllib

import numpy as np
from shapely.geometry import LineString
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from viaduct_clearance import DEFAULT_POLICY, projected_buildings, screen_line


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(data):
    return (json.dumps(data, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def pack(raw):
    result = bytearray(gzip.compress(raw, mtime=0))
    result[9] = 255
    return bytes(result)


def projection(grid):
    return lambda lon, lat, z=None: ((lon-grid['bbox_west'])*grid['m_per_deg_lon'],
                                    (grid['bbox_north']-lat)*grid['m_per_deg_lat'])


def routes(city, slug, project):
    features = json.loads((city / f'{slug}.corridor.geojson').read_text())['features']
    return {feature['properties']['name']: LineString([project(lon, lat) for lon, lat, *_ in feature['geometry']['coordinates']])
            for feature in features if feature['geometry']['type'] == 'LineString'}


def prepare(design_path, directory, grid, route_map, fetch_terrain=False):
    design = tomllib.loads(design_path.read_text())
    slug = design['city']['slug']
    osm = ROOT / f'.cache/osr-pipeline/osm/{slug}.json'
    source = json.loads(osm.read_text())
    project = projection(grid)
    height_path = ROOT / f'.cache/osr-pipeline/clearance/{slug}-height-elements.json'
    heights = json.loads(height_path.read_text())['elements'] if height_path.is_file() else []
    tags = {str(element['id']): element.get('tags', {}) for element in heights}
    buildings = []
    for item in source.get('buildings', []):
        buildings.append({**item, 'tags': {**item.get('tags', {}), **tags.get(str(item['id']), {})}})
    # Additional height-tagged building parts can represent towers omitted
    # from the older footprint-only snapshot. Retain their own geometry too.
    ids = {str(item['id']) for item in buildings}
    for element in heights:
        if str(element['id']) not in ids and element.get('geometry'):
            buildings.append(dict(id=element['id'], tags=element.get('tags', {}),
                                  nodes=[[point['lat'], point['lon']] for point in element['geometry']]))
    polygons, records, invalid = projected_buildings(buildings, project)
    tree = STRtree(polygons)
    nearby = set()
    for route in route_map.values():
        nearby.update(map(int, tree.query(route.buffer(10.), predicate='intersects')))
    retained = [records[index]['properties'] for index in sorted(nearby)]
    path = directory / 'building-footprints.json.gz'
    path.write_bytes(pack(encoded(retained)))
    receipt = dict(dataset='Retained OpenStreetMap building footprints and optional height/building-part tags',
                   source_sha256=sha(osm), source_fetched_at=source.get('fetched_at'),
                   retained_sha256=sha(path), source_building_count=len(buildings),
                   retained_near_corridor_count=len(retained), invalid_footprints=invalid,
                   selection='Exact footprint intersection with every current corridor buffered by 10 m.',
                   corridor_sha256=sha(design_path.parent / f'{slug}.corridor.geojson'),
                   mapping_completeness='Unknown; OSM omissions and changes require survey/denser building evidence.',
                   attribution='© OpenStreetMap contributors; ODbL 1.0',
                   height_tag_documentation='https://wiki.openstreetmap.org/wiki/Key:height',
                   source_documentation='https://docs.overturemaps.org/guides/buildings/')
    if height_path.is_file():
        receipt['supplementary_height_snapshot_sha256'] = sha(height_path)
        receipt['supplementary_height_source'] = 'Overpass building height/levels/building-part query for the city bbox, 2026-10-05'
    (directory / 'building-source.json').write_bytes(encoded(receipt))
    retain_terrain(design_path,directory,grid,route_map,fetch_terrain)


def retain_terrain(design_path,directory,grid,route_map,fetch_terrain=False):
    slug=tomllib.loads(design_path.read_text())['city']['slug']
    elevation = ROOT / f'.cache/osr-pipeline/rasters/{slug}.elevation.npy'
    provenance = ROOT / f'.cache/osr-pipeline/rasters/{slug}.terrain-provenance.json'
    if fetch_terrain:
        sys.path.insert(0,str(ROOT/'design/city-generation/src'))
        from osr_geo.terrain import sample_elevation_grid
        from osr_osm.fetcher import BBox
        bbox=BBox(grid['bbox_north']-grid['height']*grid['cell_m']/grid['m_per_deg_lat'],
                  grid['bbox_west'],grid['bbox_north'],
                  grid['bbox_west']+grid['width']*grid['cell_m']/grid['m_per_deg_lon'])
        sample=sample_elevation_grid(bbox,grid['height'],grid['width'],ROOT/'.cache/osr-pipeline/terrain')
        sample.elevation_m.astype('<f4').tofile(elevation)
        sample.provenance['sampling']='Cell centres on the retained planning-grid metric projection, including ceil-sized bbox fringe.'
        provenance.write_bytes(encoded(sample.provenance))
    if elevation.is_file() and provenance.is_file():
        if elevation.stat().st_size != grid['height'] * grid['width'] * 4:
            raise ValueError('Terrain dimensions mismatch')
        source_raw = elevation.read_bytes()
        values=np.frombuffer(source_raw,dtype='<f4').reshape(grid['height'],grid['width'])
        selected=np.zeros(values.shape,dtype=bool)
        coordinates=[]
        for route in route_map.values():
            points=np.asarray(route.coords)[:,:2]
            cumulative=np.r_[0.,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))]
            at=np.arange(0.,route.length,grid['cell_m']/2)
            indices=np.minimum(len(points)-2,np.maximum(0,np.searchsorted(cumulative,at,side='right')-1))
            lengths=cumulative[indices+1]-cumulative[indices]
            fraction=np.divide(at-cumulative[indices],lengths,out=np.zeros_like(at),where=lengths>0)
            coordinates.append(np.vstack((points,points[indices]+fraction[:,None]*(points[indices+1]-points[indices]))))
        footprints=directory/'building-footprints.json.gz'
        if footprints.is_file():
            project=projection(grid)
            for building in json.loads(gzip.decompress(footprints.read_bytes())):
                nodes=building.get('nodes',[])
                if nodes:coordinates.append(np.asarray([project(lon,lat) for lat,lon in nodes]))
        for points in coordinates:
            # Full corridor vertices and 10 m samples plus a three-cell margin cover
            # sparse straight chords, beam/foundation envelopes and 5 m profile
            # samples. Building vertices preserve conservative roof datums.
            rr=np.floor(points[:,1]/grid['cell_m']).astype(int)
            cc=np.floor(points[:,0]/grid['cell_m']).astype(int)
            for dy in range(-3,4):
                for dx in range(-3,4):
                    rows,cols=rr+dy,cc+dx
                    valid=(rows>=0)&(rows<grid['height'])&(cols>=0)&(cols<grid['width'])
                    selected[rows[valid],cols[valid]]=True
        raw=np.where(selected,values,np.nan).astype('<f4').tobytes()
        (directory / 'terrain-elevation.f32.gz').write_bytes(pack(raw))
        (directory / 'terrain-source.json').write_bytes(encoded(dict(
            provenance=json.loads(provenance.read_text()), grid_sha256=sha(design_path.parent / 'engineering/alignment/planning-grid.json'),
            corridor_sha256=sha(design_path.parent/f'{slug}.corridor.geojson'),
            building_footprints_sha256=sha(footprints) if footprints.is_file() else None,
            source_grid_elevation_sha256=hashlib.sha256(source_raw).hexdigest(),
            retained_scope='Full-resolution route vertices, half-cell chainage samples and retained building vertices plus a three-cell margin; cells outside the review scope are NaN.',
            retained_sha256=sha(directory / 'terrain-elevation.f32.gz'), raw_sha256=hashlib.sha256(raw).hexdigest(),
            limitations='SRTM-based planning elevation can include surface/canopy/roof returns and is not surveyed bare earth.')))


def audit(design_path, check=False, retain=False, fetch_terrain=False, refresh_terrain=False):
    design = tomllib.loads(design_path.read_text())
    city = design_path.parent
    slug = design['city']['slug']
    directory = city / 'engineering/clearance'
    grid_path = city / 'engineering/alignment/planning-grid.json'
    grid = json.loads(grid_path.read_text())
    project = projection(grid)
    route_map = routes(city, slug, project)
    if not check:
        directory.mkdir(parents=True, exist_ok=True)
    if retain:
        prepare(design_path, directory, grid, route_map, fetch_terrain)
    elif refresh_terrain:
        retain_terrain(design_path,directory,grid,route_map,fetch_terrain)
    footprints = directory / 'building-footprints.json.gz'
    receipt_path = directory / 'building-source.json'
    sources = {path.relative_to(ROOT).as_posix(): sha(path) for path in (
        design_path, city / f'{slug}.corridor.geojson', grid_path,
        Path(__file__), Path(__file__).with_name('viaduct_clearance.py'))}
    polygons, records, invalid = [], [], []
    receipt = None
    if footprints.is_file() != receipt_path.is_file():
        raise ValueError('Incomplete building evidence: ' + slug)
    if footprints.is_file():
        receipt = json.loads(receipt_path.read_text())
        if receipt['retained_sha256'] != sha(footprints) or receipt['corridor_sha256'] != sha(city / f'{slug}.corridor.geojson'):
            raise ValueError('Building evidence altered or wrong corridor: ' + slug)
        polygons, records, invalid = projected_buildings(json.loads(gzip.decompress(footprints.read_bytes())), project)
        invalid += receipt.get('invalid_footprints', [])
        sources.update({path.relative_to(ROOT).as_posix(): sha(path) for path in (footprints, receipt_path)})
    terrain_path = directory / 'terrain-elevation.f32.gz'
    terrain_receipt = directory / 'terrain-source.json'
    elevation = None
    terrain_source = None
    if terrain_path.is_file() != terrain_receipt.is_file():
        raise ValueError('Incomplete terrain evidence: ' + slug)
    if terrain_path.is_file():
        terrain_source = json.loads(terrain_receipt.read_text())
        raw = gzip.decompress(terrain_path.read_bytes())
        if sha(terrain_path) != terrain_source['retained_sha256'] or hashlib.sha256(raw).hexdigest() != terrain_source['raw_sha256'] or sha(grid_path) != terrain_source['grid_sha256']:
            raise ValueError('Altered terrain evidence: ' + slug)
        if terrain_source.get('corridor_sha256',sha(city/f'{slug}.corridor.geojson'))!=sha(city/f'{slug}.corridor.geojson') or terrain_source.get('building_footprints_sha256',sha(footprints) if footprints.is_file() else None)!=(sha(footprints) if footprints.is_file() else None):
            raise ValueError('Terrain review scope differs from its corridor/buildings: '+slug)
        array = np.frombuffer(raw, dtype='<f4').reshape(grid['height'], grid['width'])
        def elevation(x, y):
            row, col = math.floor(y/grid['cell_m']), math.floor(x/grid['cell_m'])
            if not 0 <= row < array.shape[0] or not 0 <= col < array.shape[1] or not np.isfinite(array[row, col]):
                return None
            return float(array[row, col])
        sources.update({path.relative_to(ROOT).as_posix(): sha(path) for path in (terrain_path, terrain_receipt)})
    rows = []
    for name, route in route_map.items():
        civil = [item for item in design.get('civil_segments', []) if item['line'] == name]
        if not civil:
            raise ValueError('Missing civil classes: ' + name)
        expected = next(float(line['length_m']) for line in design['lines'] if (line.get('id') or line['name']) == name)
        if abs(expected-route.length) > max(2., .001*expected):
            raise ValueError('Civil/corridor chainage differs: ' + name)
        rows.append(dict(line=name, **screen_line(route, civil, polygons, records, elevation)))
    beam = Counter(check['status'] for row in rows for check in row['beam_building_checks'])
    pier = Counter(check['status'] for row in rows for check in row['reference_supports'])
    terrain = Counter(check['status'] for row in rows for check in row['terrain_checks'])
    unresolved = Counter(check['kind'] for row in rows for check in row['unresolved'])
    summary = dict(schema='osr-viaduct-clearance/1', city=slug, sources_sha256=sources,
                   status='physical-release-blocked', physical_release=False,
                   buildings_available=receipt is not None, terrain_available=elevation is not None,
                   mapped_footprints=len(polygons), known_height_footprints=sum(item['height_m'] is not None for item in records),
                   invalid_footprints=invalid, beam_building_status=dict(beam), reference_support_status=dict(pier),
                   terrain_status=dict(terrain), unresolved=dict(unresolved), policy=DEFAULT_POLICY,
                   designed_rail_profile_available=False, designed_rail_gradient_exceedances=None,
                   terrain_noise_attributed=False,
                   unique_buildings_with_beam_roof_events=len({r['building'] for line in rows for r in line['beam_building_checks'] if r['status']=='beam-roof-collision'}),
                   building_source=receipt, terrain_source=terrain_source,
                   limitations=['Incomplete building mapping, unknown roof heights, utilities and protected air rights are unresolved.',
                       '12 m rail height and 9 m envelope are explicit planning assumptions; no final vertical alignment is claimed.',
                       'Reference support grid is not a selected foundation layout; cap, pile group, utilities and boundary/special spans require design.',
                       'Terrain tiles are not surveyed ground; horizontal DEM resampling does not improve source accuracy.',
                       'Any change of route, height, support position, span or foundations requires new structural quantities, cost, delivery and native operating checks.'])
    details = dict(schema=summary['schema'], city=slug, lines=rows, physical_release=False)
    text = '\n'.join([f"# {design['city'].get('name', city.name)} — viaduct obstacle clearance", '',
        '**Physical release blocked.** This is a source-bound footprint and terrain screen of the existing planning route, not an obstacle-cleared alignment.', '',
        f"Mapped nearby footprints: **{len(polygons):,}**; source heights: **{summary['known_height_footprints']:,}**. Building source: {'retained' if receipt else 'unavailable'}; terrain: {'retained' if elevation else 'unavailable'}.", '',
        '| Screen | Status | Count |', '|---|---|---:|',
        *[f'| Beam/building | {status} | {count:,} |' for status, count in sorted(beam.items())],
        *[f'| Reference support/foundation | {status} | {count:,} |' for status, count in sorted(pier.items())],
        *[f'| Terrain | {status} | {count:,} |' for status, count in sorted(terrain.items())],
        *[f'| Unresolved geometry/input | {status} | {count:,} |' for status, count in sorted(unresolved.items())], '',
        'Counts are screening events per civil segment/reference support, not unique buildings, accepted piers or procurement quantities. Reference-gradient flags are DEM height differences between provisional supports; designed rail gradients are unavailable. Roof/canopy effects, raster quantisation, noise and real ground slope remain unseparated. These flags neither prove an unbuildable rail profile nor establish clearance.', '',
        '## Measures required for a buildable alignment', '',
        '- **Beam overflight:** surveyed roof/plant heights plus ground datum, swept train/deck/walkway envelope, lateral clearance, fire/rescue access and property/air rights. A source height below a provisional soffit is conditional only; building floors are an uncertain height estimate.',
        '- **Tall obstacles:** reroute, acquire/remove an approved obstacle, or raise the vertical alignment with gradient-compliant approaches and new pier/structure costs. Unknown heights never establish clearance.',
        '- **Supports:** place the entire pier/pile-cap/foundation and construction-access footprint clear of buildings and services. A clear beam does not clear its supports. Move support lines along a tangent using verified Pi20/Pi25 spans, change foundations/cap arrangement, or design a independently checked special span; do not invent a 30 m catalogue beam.',
        '- **Terrain:** survey a longitudinal/cross-section profile and test grades, vertical curves, terrain crests, flood levels and each erection stage. Straight beam soffits interpolate between supports; local ground peaks can still clash.',
        '- **Release:** close every conflict and missing-height/mapping/terrain/utility finding against survey and independent engineering checks before accepting the corridor. Recalculate route, stations, supports, quantities, cost and service evidence for adopted changes.', '',
        'The default screen uses a 9 m twin-track envelope plus 2 m lateral allowance, a 3 m foundation radius plus 2 m setback, 12 m reference rail height, 1.6 m conservative rail-to-soffit allowance, 2 m roof clearance and a 3.5% reference grade limit. The Pi structural depth is 1.155 m; the combined allowance leaves 0.445 m for an unverified track stack. Special products have unresolved depth and cannot pass a Pi roof-clearance check. Direct structural/foundation intersections are reported separately from clearance/setback conflicts. These are controlled screening assumptions requiring deployment-specific approval, not statutory clearances.', '',
        '[Summary and source hashes](summary.json) · [Per-line beam, support and terrain events](clearance-register.json.gz).', ''])
    outputs = {directory / 'summary.json': encoded(summary),
               directory / 'clearance-register.json.gz': pack(encoded(details)),
               directory / 'README.md': text.encode()}
    for path, raw in outputs.items():
        if check:
            if not path.is_file() or path.read_bytes() != raw:
                raise ValueError('Stale clearance screen: ' + str(path))
        else:
            path.write_bytes(raw)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--city', action='append')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--retain-inputs', action='store_true')
    parser.add_argument('--fetch-terrain', action='store_true',help='Fetch open DEM onto the exact retained grid without changing routes or water inputs')
    parser.add_argument('--refresh-terrain',action='store_true',help='Retain current cached terrain against existing footprints, without rereading the complete OSM snapshot')
    parser.add_argument('--jobs',type=int,default=1,help='1–3 independent city processes')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if not (args.all or args.city) or (args.check and (args.retain_inputs or args.refresh_terrain)) or (args.fetch_terrain and not (args.retain_inputs or args.refresh_terrain)) or not 1<=args.jobs<=3:
        parser.error('Select cities; --check uses retained evidence offline')
    selected = [p for p in sorted((ROOT/'cities/catalogue').glob('*/*/*/design.toml'))
                if args.all or tomllib.loads(p.read_text())['city']['slug'] in args.city]
    if not args.all and len(selected) != len(set(args.city)):
        parser.error('Unknown city selection')
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        futures={pool.submit(audit,path,args.check,args.retain_inputs,args.fetch_terrain,args.refresh_terrain):path for path in selected}
        for future in as_completed(futures):
            value=future.result()
            print(value['city'], value['mapped_footprints'], value['beam_building_status'], flush=True)


if __name__ == '__main__':
    main()
