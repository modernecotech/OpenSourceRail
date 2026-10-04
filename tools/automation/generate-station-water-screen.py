#!/usr/bin/env python3
"""Retain the actual planning water mask and check every platform cell.

The compressed mask supports reproducible checks in a fresh checkout. This
point-location screen does not release platform footprints, banks or access.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]


def packed_bytes(data):
    packed = bytearray(gzip.compress(data, mtime=0))
    packed[9] = 255  # Stable OS header across Python 3.11 and 3.13.
    return bytes(packed)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def platform_water_cells(stations, grid, mask):
    if len(mask) != grid['height'] * grid['width']:
        raise ValueError('Water mask does not match the controlled grid')
    cells = []
    for station in stations:
        row = math.floor((grid['bbox_north'] - station['lat']) * grid['m_per_deg_lat'] / grid['cell_m'])
        col = math.floor((station['lon'] - grid['bbox_west']) * grid['m_per_deg_lon'] / grid['cell_m'])
        if not 0 <= row < grid['height'] or not 0 <= col < grid['width']:
            raise ValueError('Platform is outside the controlled grid: ' + station['id'])
        water = mask[row * grid['width'] + col]
        cells.append(dict(station_id=station['id'], row=row, col=col, water_coverage_percent=water))
    return cells


def screen(design_path, *, check=False):
    design = tomllib.loads(design_path.read_text())
    city = design_path.parent
    slug = design['city']['slug']
    out = city / 'engineering/alignment'
    grid_path = out / 'planning-grid.json'
    grid = json.loads(grid_path.read_text())
    mask_path = out / 'planning-water-mask.bin.gz'
    cached = ROOT / f'.cache/osr-pipeline/rasters/{slug}.water.npy'
    if not check and not cached.is_file() and not mask_path.is_file():
        sys.path.insert(0, str(ROOT / 'design/city-generation/src'))
        from osr_geo.cli import _load_city
        from osr_geo.rasterize import GridRef, build_water_mask
        cached_grid = cached.with_name(slug + '.grid.json')
        reference = GridRef(**json.loads(cached_grid.read_text())['grid'])
        osm_path = ROOT / f'.cache/osr-pipeline/osm/{slug}.json'
        mask = build_water_mask(_load_city(osm_path), reference).tobytes()
        mask_path.write_bytes(packed_bytes(mask))
    if check or not cached.is_file():
        mask = gzip.decompress(mask_path.read_bytes())
    else:
        mask = cached.read_bytes()
        packed = packed_bytes(mask)
        if not mask_path.is_file() or mask_path.read_bytes() != packed:
            mask_path.write_bytes(packed)
    cells = platform_water_cells(design['stations'], grid, mask)
    wet = [r['station_id'] for r in cells if r['water_coverage_percent'] >= 50]
    report = dict(schema_version=1, city=slug, passed=not wet, physical_release=False,
        method='Platform point must be in a cell with less than 50% independent OSM water coverage; footprint, bank stability and access require project verification.',
        platforms_checked=len(cells), wet_platforms=wet, platforms=cells,
        uncompressed_water_mask_sha256=sha(mask), sources_sha256={
            p.relative_to(ROOT).as_posix(): sha(p.read_bytes())
            for p in [design_path, grid_path, mask_path, Path(__file__)]})
    path = out / 'station-water-screen.json'
    data = (json.dumps(report, indent=2, sort_keys=True) + '\n').encode()
    if check:
        if path.read_bytes() != data:
            raise ValueError('Stale station water screen: ' + slug)
    else:
        path.write_bytes(data)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--design', type=Path)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--prepare-grid', action='store_true', help='attach the retained independent water mask to the local design raster bundle before synthesis')
    args = parser.parse_args()
    paths = [args.design.resolve()] if args.design else sorted((ROOT / 'cities/catalogue').glob('*/*/*/design.toml'))
    count = platforms = 0
    findings = []
    for path in paths:
        if not (path.parent / 'alignment-policy.toml').is_file() or path.parent.name == 'Baghdad':
            continue
        if args.prepare_grid:
            slug=tomllib.loads(path.read_text())['city']['slug']
            mask_path=path.parent/'engineering/alignment/planning-water-mask.bin.gz'
            if not mask_path.is_file():
                screen(path)
            mask=gzip.decompress(mask_path.read_bytes())
            cached=ROOT/f'.cache/osr-pipeline/rasters/{slug}.water.npy'
            sidecar=cached.with_name(slug+'.grid.json')
            data=json.loads(sidecar.read_text());grid=data['grid']
            if len(mask)!=grid['height']*grid['width']:
                raise ValueError('Retained water mask and local design grid differ: '+slug)
            cached.write_bytes(mask)
            data['rasters']['water']=dict(path=cached.name,dtype='u8',shape=[grid['height'],grid['width']],byteorder='little')
            sidecar.write_text(json.dumps(data,indent=2)+'\n')
            count+=1
            continue
        report = screen(path, check=args.check)
        count += 1
        platforms += report['platforms_checked']
        if not report['passed']:
            findings.append((report['city'], report['wet_platforms']))
    print(f'Water {"grid preparations" if args.prepare_grid else "screens"}: {count} cities, {platforms} platform points; physical releases open.')
    if findings:
        raise ValueError('Platforms lie over mapped water: ' + json.dumps(findings))


if __name__ == '__main__':
    main()
