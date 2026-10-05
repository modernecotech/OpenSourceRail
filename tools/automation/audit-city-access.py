#!/usr/bin/env python3
"""Retain native population pixels and audit real transfer connectivity offline."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import tomllib

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from city_access import population_audit, transfer_audit, transfer_recovery_candidates


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()


def pack(raw):
    result = bytearray(gzip.compress(raw, mtime=0))
    result[9] = 255
    return bytes(result)


def retain_population(design, directory, raster):
    import rasterio
    from rasterio.windows import Window, from_bounds
    box = design['city']['bbox']
    with rasterio.open(raster) as source:
        if source.crs.to_epsg() != 4326 or source.count != 1:
            raise ValueError('Expected a native EPSG:4326 population count raster')
        requested = from_bounds(box['west'], box['south'], box['east'], box['north'], source.transform)
        col, row = int(np.floor(requested.col_off)), int(np.floor(requested.row_off))
        width = int(np.ceil(requested.col_off + requested.width)) - col
        height = int(np.ceil(requested.row_off + requested.height)) - row
        window = Window(col, row, width, height)
        data = source.read(1, window=window, boundless=True, masked=True)
        transform = source.window_transform(window)
        yy, xx = np.indices(data.shape)
        lon = transform.c + (xx + .5) * transform.a + (yy + .5) * transform.b
        lat = transform.f + (xx + .5) * transform.d + (yy + .5) * transform.e
        inside = (lon >= box['west']) & (lon < box['east']) & (lat >= box['south']) & (lat < box['north'])
        values = np.asarray(data.filled(0), dtype=np.float32)[inside]
        valid = (~np.ma.getmaskarray(data))[inside] & np.isfinite(values) & (values >= 0)
        values[~valid] = 0
        memory = io.BytesIO()
        np.savez(memory, lat=lat[inside], lon=lon[inside], counts=values, valid=valid)
    path = directory / 'population-pixels.npz.gz'
    path.write_bytes(pack(memory.getvalue()))
    suffix = raster.name
    iso = suffix.split('_')[0].upper()
    url_path = (f'Global_2000_2020_Constrained/2020/BSGM/{iso}/'
                if 'constrained' in suffix else f'Global_2000_2020/2020/{iso}/')
    receipt = dict(dataset='WorldPop 2020 native gridded population counts',
                   year=2020, units='persons per native source pixel',
                   source_url='https://data.worldpop.org/GIS/Population/' + url_path + suffix,
                   source_sha256=sha(raster), retained_sha256=sha(path),
                   source_resolution_degrees=[abs(transform.a), abs(transform.e)],
                   bbox=box, pixel_selection='Native pixel centres inside the city bbox; no resampling.',
                   nodata='Source nodata/out-of-extent and invalid values excluded and reported; never filled with people.',
                   attribution='WorldPop, University of Southampton, 2020; CC BY 4.0',
                   source_documentation='https://www.worldpop.org/sdi/introapi/')
    (directory / 'population-source.json').write_bytes(encoded(receipt))


def report(design_path, fetch=False, check=False):
    design = tomllib.loads(design_path.read_text())
    city = design_path.parent
    directory = city / 'engineering/access'
    if not check:
        directory.mkdir(parents=True, exist_ok=True)
    pixels = directory / 'population-pixels.npz.gz'
    receipt_path = directory / 'population-source.json'
    override_path=ROOT/'docs/data/city-population-source-overrides.json'
    override=json.loads(override_path.read_text())['cities'].get(design['city']['slug'])
    source_country=override['source_country'] if override else design['city']['country']
    source_changed=bool(override and receipt_path.is_file() and json.loads(receipt_path.read_text())['source_url'].split('/')[-1].split('_')[0]!='ssd')
    if fetch and (not pixels.is_file() or source_changed):
        sys.path.insert(0, str(ROOT / 'design/city-generation/src'))
        from osr_geo.population import fetch_population_raster
        raster = fetch_population_raster(source_country, ROOT / '.cache/osr-pipeline/population')
        if raster:
            retain_population(design, directory, raster)
    sources = {path.relative_to(ROOT).as_posix(): sha(path)
               for path in (design_path, Path(__file__), Path(__file__).with_name('city_access.py'),override_path)}
    population = dict(status='unavailable', catchments=[],
                      reason='No retained native population-count evidence; routing-demand coverage cannot establish resident counts.')
    if pixels.is_file() != receipt_path.is_file():
        raise ValueError('Incomplete population evidence: ' + str(directory))
    if pixels.is_file():
        receipt = json.loads(receipt_path.read_text())
        if sha(pixels) != receipt['retained_sha256'] or receipt['bbox'] != design['city']['bbox']:
            raise ValueError('Altered or wrong-bbox population evidence: ' + str(city))
        with np.load(io.BytesIO(gzip.decompress(pixels.read_bytes())), allow_pickle=False) as values:
            population = population_audit(values['lat'], values['lon'], values['counts'], values['valid'], design)
        if override and receipt['source_url'].split('/')[-1].split('_')[0]!='ssd':
            population=dict(status='unavailable',catchments=[],reason='Retained country raster conflicts with the controlled jurisdiction finding; fetch corrected population source.')
        population['source'] = receipt
        sources.update({path.relative_to(ROOT).as_posix(): sha(path) for path in (pixels, receipt_path)})
    quality = next(city.glob('*.design-quality.yaml'), None)
    legacy = None
    if quality:
        match = re.search(r'high_demand_coverage:\s*([0-9.]+)', quality.read_text())
        legacy = float(match[1]) if match else None
        sources[quality.relative_to(ROOT).as_posix()] = sha(quality)
    summary = dict(schema='osr-city-access/1', city=design['city']['slug'],
                   population_source_country=source_country,input_findings=[override] if override else [],
                   sources_sha256=sources, population=population, transfers=transfer_audit(design),
                   transfer_recovery_candidates=transfer_recovery_candidates(design),
                   legacy_routing_score=dict(high_demand_cell_fraction=legacy,
                       basis='Fraction of demand >= 0.5 cells within 20 routing cells of any track; mixed POI/population/centre demand, not resident coverage.',
                       retired_resident_proxy=None), physical_release=False)
    graph = summary['transfers']
    fmt = lambda value: f'{value:.1%}' if value is not None else 'unavailable'
    text = '\n'.join([
        f"# {design['city'].get('name', city.name)} — population access and transfers", '',
        'Controlled planning screen; population counts, passenger transfers and routing demand are separate measures.', '',
        *([f"**Country-input discrepancy:** {override['finding']} [Verified jurisdiction]({override['evidence']}).",''] if override else []),
        '| Transfer measure | Value |', '|---|---:|',
        f"| Direct transfer line pairs | {fmt(graph['direct_transfer_fraction'])} |",
        f"| Reachable line pairs, including intermediate lines | {fmt(graph['reachable_line_pair_fraction'])} |",
        f"| Reachable with at most two transfers | {fmt(graph['reachable_with_at_most_two_transfers_fraction'])} |",
        f"| Connected line components | {len(graph['components'])} |",
        f"| Maximum transfers within a connected component | {graph['maximum_required_transfers']} |", '',
        'A crossing creates no transfer unless passenger interchange membership is recorded. Physical access, waiting time, timetable and fares remain unverified.', '',
        '## Population access', '',
        *( [f"Native **2020 bbox population: {population['bbox_population_2020']:,.0f}**. Catalogue planning population: {design['city']['population']:,}. Different dates and boundaries; no multiplication or rebasing of a demand score.", '',
             '| Radius | Residents in union of station circles (2020) | Share of raster bbox population |', '|---|---:|---:|',
             *[f"| {row['radius_m']} m | {row['covered_population_2020']:,.0f} | {fmt(row['fraction_of_raster_population'])} |" for row in population['catchments']], '',
             f"Excluded nodata pixels: {population['missing_pixels']:,}; valid pixels: {population['valid_pixels']:,}.", '',
             '[Retained source and attribution](population-source.json) · [Native count pixels](population-pixels.npz.gz).']
           if population['status'] == 'available' else [population.get('reason', 'No positive retained population counts.')]), '',
        'Station circles use great-circle distances and count each native pixel once. They are potential radial access, **not validated walking coverage**: rivers, motorways, walls, hills and actual entrances can reduce access. Native pixel-centre assignment adds source-resolution uncertainty at catchment boundaries. The 1,500–2,000 m cases are extended access/feeder sensitivities; no feeder service or finance is assumed.', '',
        f"The legacy routing score ({fmt(legacy)}) measures high-demand cells close to tracks. It can be lower or higher than population access. Its former multiplication by city population is retired. Coverage alone never increases modeled paid trips or financial viability.", '',
        '[Machine-readable accounting and source hashes](summary.json).', ''])
    for path, raw in ((directory / 'summary.json', encoded(summary)), (directory / 'README.md', text.encode())):
        if check:
            if not path.is_file() or path.read_bytes() != raw:
                raise ValueError('Stale access report: ' + str(path))
        else:
            path.write_bytes(raw)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--city', action='append')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--fetch-population', action='store_true')
    parser.add_argument('--jobs', type=int, default=2)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if not (args.all or args.city) or not 1 <= args.jobs <= 4 or (args.check and args.fetch_population):
        parser.error('Select --all or --city; 1–4 workers; checking is offline')
    paths = sorted((ROOT / 'cities/catalogue').glob('*/*/*/design.toml'))
    selected = [p for p in paths if args.all or tomllib.loads(p.read_text())['city']['slug'] in args.city]
    if not args.all and len(selected) != len(set(args.city)):
        parser.error('Unknown city selection')
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(report, p, args.fetch_population, args.check): p for p in selected}
        for future in as_completed(futures):
            value = future.result()
            print(value['city'], value['population']['status'],
                  value['transfers']['reachable_line_pair_fraction'], flush=True)


if __name__ == '__main__':
    main()
