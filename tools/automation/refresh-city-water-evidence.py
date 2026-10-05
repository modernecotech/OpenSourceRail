#!/usr/bin/env python3
"""Retain independently sampled WorldCover water evidence on the exact city grid.

Generation requires the geotiff extra; checking retained evidence is offline.
Class 80 is permanent water; class 0 is unknown, never evidence of dry land.
OSM rivers and ponds supplement the independent coverage. Invalid legacy OSM
relations are explicitly recorded rather than interpreted as dry polygons.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import threading
import tomllib

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / '.cache/osr-pipeline/worldcover'
BASE = 'https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/'
ATTRIBUTION = '© ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021) processed by ESA WorldCover consortium'
_locks: dict[str, threading.Lock] = {}
_guard = threading.Lock()
sys.path.insert(0, str(ROOT / 'design/city-generation/src'))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pack(raw):
    result = bytearray(gzip.compress(raw, mtime=0))
    result[9] = 255
    return bytes(result)


def tile_name(lat, lon):
    return f"{'N' if lat >= 0 else 'S'}{abs(lat):02d}{'E' if lon >= 0 else 'W'}{abs(lon):03d}"


def tile_path(lat, lon):
    name = f'ESA_WorldCover_10m_2021_v200_{tile_name(lat, lon)}_Map.tif'
    with _guard:
        lock = _locks.setdefault(name, threading.Lock())
    with lock:
        path = CACHE / name
        if not path.is_file():
            import requests
            CACHE.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix('.part')
            with requests.get(BASE + name, stream=True, timeout=(15, 60)) as response:
                response.raise_for_status()
                with temporary.open('wb') as output:
                    for chunk in response.iter_content(1024 * 1024):
                        output.write(chunk)
            temporary.replace(path)
        return path


def sample_classes(grid):
    import rasterio
    from rasterio.windows import Window, from_bounds
    # Four native-resolution samples per 20 m planning cell. Use the same
    # equirectangular transform as the Rust route and platform coordinates.
    classes = np.zeros((grid['height'], grid['width'], 4), dtype=np.uint8)
    tile_receipts = []
    # Ceil-sized grids can extend beyond the nominal city bbox by one cell.
    # Select sources for the actual sample extent, including neighbouring
    # tiles when that final cell straddles a three-degree boundary.
    southern_sample=grid['bbox_north']-(grid['height']-.25)*grid['cell_m']/grid['m_per_deg_lat']
    eastern_sample=grid['bbox_west']+(grid['width']-.25)*grid['cell_m']/grid['m_per_deg_lon']
    for south in range(math.floor(southern_sample/3)*3, math.floor(grid['bbox_north']/3)*3+1, 3):
        for west in range(math.floor(grid['bbox_west']/3)*3, math.floor(eastern_sample/3)*3+1, 3):
            path = tile_path(south, west)
            with rasterio.open(path) as source:
                if source.crs.to_epsg() != 4326 or source.count != 1:
                    raise ValueError('Unexpected WorldCover source geometry: ' + path.name)
                left = max(west, grid['bbox_west'])
                right = min(west+3, grid['bbox_east']+grid['cell_m']/grid['m_per_deg_lon'])
                bottom = max(south, grid['bbox_south']-grid['cell_m']/grid['m_per_deg_lat'])
                top = min(south+3, grid['bbox_north'])
                window = from_bounds(left, bottom, right, top, source.transform)
                col = max(0, math.floor(window.col_off))
                row = max(0, math.floor(window.row_off))
                end_col = min(source.width, math.ceil(window.col_off+window.width))
                end_row = min(source.height, math.ceil(window.row_off+window.height))
                array = source.read(1, window=Window(col, row, end_col-col, end_row-row))
                for index, (dy, dx) in enumerate(((.25,.25),(.25,.75),(.75,.25),(.75,.75))):
                    lats = grid['bbox_north']-(np.arange(grid['height'])+dy)*grid['cell_m']/grid['m_per_deg_lat']
                    lons = grid['bbox_west']+(np.arange(grid['width'])+dx)*grid['cell_m']/grid['m_per_deg_lon']
                    rr = np.floor((source.transform.f-lats)/-source.transform.e).astype(int)-row
                    cc = np.floor((lons-source.transform.c)/source.transform.a).astype(int)-col
                    valid_r = np.flatnonzero((rr >= 0) & (rr < array.shape[0]))
                    valid_c = np.flatnonzero((cc >= 0) & (cc < array.shape[1]))
                    classes[valid_r[:, None], valid_c[None, :], index] = array[rr[valid_r, None], cc[None, valid_c]]
                tile_receipts.append(dict(url=BASE+path.name, file_sha256=sha(path.read_bytes()),
                    native_window=[col,row,end_col-col,end_row-row], window_sha256=sha(array.tobytes()),
                    crs='EPSG:4326', pixel_size_degrees=[source.transform.a,-source.transform.e]))
    return classes, tile_receipts


def combined_mask(classes, osm_mask):
    if classes.shape != (*osm_mask.shape, 4):
        raise ValueError('Independent land-cover samples and OSM grid differ')
    water = (np.count_nonzero(classes == 80, axis=2)*25).astype(np.uint8)
    water = np.maximum(water, osm_mask)
    water[np.any(classes == 0, axis=2)] = 255
    return water


def refresh(design_path, check=False, from_retained=False):
    from osr_geo.rasterize import GridRef, build_water_mask
    from osr_osm.fetcher import BBox, CityOSM
    design = tomllib.loads(design_path.read_text())
    slug = design['city']['slug']; out = design_path.parent / 'engineering/alignment'
    grid_path = out / 'planning-grid.json'; grid = json.loads(grid_path.read_text())
    classes_path = out / 'independent-landcover-samples.bin.gz'
    osm_path = out / 'planning-water-features.json.gz'
    receipt_path = out / 'water-source-receipt.json'
    if check or from_retained:
        receipt = json.loads(receipt_path.read_text())
        osm = json.loads(gzip.decompress(osm_path.read_bytes()))
        classes = np.frombuffer(gzip.decompress(classes_path.read_bytes()), dtype=np.uint8).reshape(grid['height'],grid['width'],4)
        invalid = receipt['legacy_osm_missing_geometry_ids']
        tiles = receipt['worldcover_tiles']
        source_sha = receipt['processed_osm_snapshot_sha256']
    else:
        source_path = ROOT / '.cache/osr-pipeline/osm' / (slug+'.json')
        raw = source_path.read_bytes(); source = json.loads(raw)
        invalid = [f['id'] for f in source.get('water', []) if not f.get('nodes') and not f.get('outer_rings')]
        osm = [f for f in source.get('water', []) if f.get('nodes') or f.get('outer_rings')]
        osm_path.write_bytes(pack((json.dumps(osm, sort_keys=True, separators=(',',':'))+'\n').encode()))
        source_sha = sha(raw)
        del source, raw
        classes, tiles = sample_classes(grid)
        classes_path.write_bytes(pack(classes.tobytes()))
    city = CityOSM(BBox(grid['bbox_south'],grid['bbox_west'],grid['bbox_north'],grid['bbox_east']),slug,0,water=osm)
    osm_mask = build_water_mask(city, GridRef(**grid))
    mask = combined_mask(classes, osm_mask)
    mask_path = out / 'planning-water-mask.bin.gz'
    packed = pack(mask.tobytes())
    receipt = dict(schema_version=2,city=slug,
        status='independent-complete-grid-planning-screen' if not np.any(mask == 255) else 'incomplete-independent-coverage',
        physical_release=False, source='ESA WorldCover 2021 v200 plus retained OSM rivers and water polygons',
        source_documentation='https://esa-worldcover.org/en/data-access', attribution=ATTRIBUTION, license='CC-BY-4.0; OSM supplement ODbL-1.0',
        method='Four 10 m class samples per controlled 20 m grid cell; permanent-water class 80; unknown class 0 is excluded, not dry.',
        worldcover_tiles=tiles, processed_osm_snapshot_sha256=source_sha, legacy_osm_missing_geometry_ids=invalid,
        legacy_osm_status='incomplete polygons; independent full-grid layer supplies lake/sea coverage' if invalid else 'retained geometries available',
        unknown_cells=int(np.count_nonzero(mask == 255)), wet_cells=int(np.count_nonzero((mask > 0)&(mask != 255))),
        mask_sha256=sha(mask.tobytes()), sources_sha256={
            p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in [grid_path,classes_path,osm_path,Path(__file__).resolve(),ROOT/'design/city-generation/src/osr_geo/rasterize.py']},
        limitations=['Historical satellite classification is an independent planning screen, not a current shoreline survey.',
                    'Narrow streams, inundation, wetlands, platform footprints, bank access and foundation stability require site evidence.'])
    encoded=(json.dumps(receipt,indent=2,sort_keys=True)+'\n').encode()
    if check:
        if mask_path.read_bytes()!=packed or receipt_path.read_bytes()!=encoded:
            raise ValueError('Stale or altered independent water evidence: '+slug)
    else:
        mask_path.write_bytes(packed); receipt_path.write_bytes(encoded)
    return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--design',type=Path); parser.add_argument('--only',default='')
    parser.add_argument('--check',action='store_true'); parser.add_argument('--jobs',type=int,default=1)
    parser.add_argument('--from-retained',action='store_true',help='recompute masks and receipts from retained actual source samples without downloading again')
    args=parser.parse_args()
    paths=[args.design.resolve()] if args.design else sorted((ROOT/'cities/catalogue').glob('*/*/*/design.toml'))
    selected=set(args.only.split(',')) if args.only else None
    paths=[p for p in paths if (p.parent/'engineering/alignment/planning-grid.json').is_file() and (not selected or tomllib.loads(p.read_text())['city']['slug'] in selected)]
    if not 1<=args.jobs<=4:parser.error('Use 1–4 bounded water-source workers')
    results={}
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures={pool.submit(refresh,p,args.check,args.from_retained):p for p in paths}
        for future in as_completed(futures):
            path=futures[future]
            try:
                report=future.result();results[path.parent.name]=report['status'];print(path.parent.name,report['status'],report['wet_cells'],'wet cells',flush=True)
            except Exception as error:
                results[path.parent.name]='failed';print(path.parent.name,'FAILED',str(error),flush=True)
    if any(v!='independent-complete-grid-planning-screen' for v in results.values()):raise SystemExit(1)


if __name__=='__main__':main()
