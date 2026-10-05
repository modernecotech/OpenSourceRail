#!/usr/bin/env python3
"""Fetch planning DEM cells without changing route, cost or water inputs."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import json
from pathlib import Path
import sys
import threading
import tomllib

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'design/city-generation/src'))
from osr_geo import terrain
from osr_osm.fetcher import BBox

locks={};guard=threading.Lock();download=terrain._download_tile


def locked_download(lat,lon,cache):
    with guard:lock=locks.setdefault((lat,lon),threading.Lock())
    with lock:return download(lat,lon,cache)


terrain._download_tile=locked_download


def fetch(path):
    design=tomllib.loads(path.read_text());slug=design['city']['slug']
    grid_path=path.parent/'engineering/alignment/planning-grid.json'
    grid=json.loads(grid_path.read_text())
    bbox=BBox(grid['bbox_north']-grid['height']*grid['cell_m']/grid['m_per_deg_lat'],
              grid['bbox_west'],grid['bbox_north'],
              grid['bbox_west']+grid['width']*grid['cell_m']/grid['m_per_deg_lon'])
    sample=terrain.sample_elevation_grid(bbox,grid['height'],grid['width'],ROOT/'.cache/osr-pipeline/terrain')
    sample.provenance['sampling']='Cell centres on the retained planning-grid metric projection, including ceil-sized bbox fringe.'
    directory=ROOT/'.cache/osr-pipeline/rasters';directory.mkdir(parents=True,exist_ok=True)
    output=directory/(slug+'.elevation.npy');temporary=output.with_suffix('.clearance.tmp')
    sample.elevation_m.astype('<f4').tofile(temporary);temporary.replace(output)
    output=directory/(slug+'.terrain-provenance.json');temporary=output.with_suffix('.clearance.tmp')
    temporary.write_text(json.dumps(sample.provenance,sort_keys=True,indent=2)+'\n');temporary.replace(output)
    return slug


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--all',action='store_true');parser.add_argument('--city',action='append');args=parser.parse_args()
    if not(args.all or args.city):parser.error('Select --all or --city')
    paths=[p for p in sorted((ROOT/'cities/catalogue').glob('*/*/*/design.toml')) if args.all or tomllib.loads(p.read_text())['city']['slug'] in args.city]
    if not args.all and len(paths)!=len(set(args.city)):parser.error('Unknown city selection')
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs={pool.submit(fetch,path):path for path in paths}
        failures=[]
        for job in as_completed(jobs):
            try:print(job.result(),'terrain cached; routes unchanged',flush=True)
            except Exception as error:
                failures.append(jobs[job]);print(jobs[job],type(error).__name__,str(error),flush=True)
    if failures:raise SystemExit(1)
