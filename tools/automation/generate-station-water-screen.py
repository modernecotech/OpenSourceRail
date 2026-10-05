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
    receipt_path = out / 'water-source-receipt.json'
    if receipt_path.is_file():
        receipt = json.loads(receipt_path.read_text())
        for name, digest in receipt['sources_sha256'].items():
            if sha((ROOT/name).read_bytes()) != digest:
                raise ValueError('Stale independent water source: ' + name)
        mask = gzip.decompress(mask_path.read_bytes())
        if sha(mask) != receipt['mask_sha256']:
            raise ValueError('Water mask differs from its independent source: ' + slug)
    else:
        raise ValueError('Missing independently complete water evidence: '+slug+'; run refresh-city-water-evidence.py')
    cached = ROOT / f'.cache/osr-pipeline/rasters/{slug}.water.npy'
    cells = platform_water_cells(design['stations'], grid, mask)
    wet = [r['station_id'] for r in cells if 0 < r['water_coverage_percent'] <= 100]
    unknown = [r['station_id'] for r in cells if r['water_coverage_percent'] == 255]
    report = dict(schema_version=2, city=slug, passed=not wet and not unknown, physical_release=False,
        method='Platform cell must have known land-cover coverage and no independently detected permanent water; OSM river/polygon evidence supplements the mask. Footprints, bank stability and access require project verification.',
        platforms_checked=len(cells), wet_platforms=wet, unknown_platforms=unknown, platforms=cells,
        uncompressed_water_mask_sha256=sha(mask), sources_sha256={
            p.relative_to(ROOT).as_posix(): sha(p.read_bytes())
            for p in [design_path, grid_path, mask_path, receipt_path, Path(__file__)]})
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
        if not args.design and (not (path.parent / 'alignment-policy.toml').is_file() or path.parent.name == 'Baghdad'):
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
            controlled=json.loads((path.parent/'engineering/alignment/planning-grid.json').read_text())
            if any(grid[k] != controlled[k] for k in ['height','width','cell_m','bbox_north','bbox_west']):
                raise ValueError('Retained water transform and local design grid differ: '+slug)
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
