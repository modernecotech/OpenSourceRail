#!/usr/bin/env python3
"""Import selected mapping sources, then reproduce neighbourhood access screens."""
from __future__ import annotations
import argparse,gzip,hashlib,io,json,sys,tomllib,zipfile
from pathlib import Path
from urllib.request import urlopen
import numpy as np
from mapping_evidence import coverage,encoded,extract_streets,load_population,retain_population,sha,walking_screen

ROOT=Path(__file__).resolve().parents[2]


def download(url,cache):
    path=cache/url.rsplit('/',1)[-1]
    if path.exists():return path
    temporary=path.with_suffix(path.suffix+'.partial')
    try:
        with urlopen(url,timeout=60) as response,temporary.open('wb') as stream:
            size=0
            while block:=response.read(1<<20):
                size+=len(block)
                if size>1_000_000_000:raise ValueError('Mapping download exceeds bounded size')
                stream.write(block)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return path


def run(city_slug='baghdad',fetch=False,check=False):
    config_path=ROOT/f'design/network-planning/{city_slug}-mapping-sources.json'
    cfg=json.loads(config_path.read_text());paths=[p for p in (ROOT/'cities/catalogue').glob('*/*/*/design.toml') if tomllib.loads(p.read_text())['city']['slug']==city_slug]
    if len(paths)!=1:raise ValueError('Mapping requires unique catalogue city')
    design_path=paths[0];city=design_path.parent;design=tomllib.loads(design_path.read_text());directory=city/'engineering/mapping'
    if not check:directory.mkdir(parents=True,exist_ok=True)
    if fetch:
        cache=ROOT/'.cache/osr-pipeline/mapping';cache.mkdir(parents=True,exist_ok=True)
        for spec in cfg['population']:
            archive=download(spec['url'],cache);raster=archive
            if archive.suffix=='.zip':
                with zipfile.ZipFile(archive) as bundle:
                    members=[v for v in bundle.namelist() if v.lower().endswith('.tif')]
                    if len(members)!=1:raise ValueError('Expected one population GeoTIFF')
                    member=members[0];raster=cache/Path(member).name
                    with bundle.open(member) as src,raster.open('wb') as dst:
                        import shutil
                        shutil.copyfileobj(src,dst)
            retain_population(raster,dict(spec,download_sha256=sha(archive)),design['city']['bbox'],directory)
        streets=cfg['streets'];pbf=download(streets['url'],cache)
        try:import osmium
        except ImportError:
            sys.path.insert(0,str(cache/'python'));import osmium
        extract_streets(pbf,design['city']['bbox'],directory,streets)
    all_paths=[config_path,Path(__file__),Path(__file__).with_name('mapping_evidence.py'),Path(__file__).with_name('city_access.py'),design_path]
    datasets={};selected=None
    for spec in cfg['population']:
        data,receipt,inputs=load_population(directory,spec['id']);all_paths+=inputs
        if receipt.get('retainer_sha256')!=sha(Path(__file__).with_name('mapping_evidence.py')):raise ValueError('Population retainer changed; fetch/reproduce native crop')
        if receipt['bbox']!=design['city']['bbox'] or any(receipt.get(k)!=spec[k] for k in spec):raise ValueError('Mapping population selection drift')
        datasets[spec['id']]=dict(source=receipt,access=coverage(data,design['stations'],cfg['sectors']))
        if spec['id']==cfg['selected_population']:selected=data
    if selected is None:raise ValueError('Selected mapping population is unavailable')
    old_dir=city/'engineering/access';old_receipt=json.loads((old_dir/'population-source.json').read_text())
    old_path=old_dir/'population-pixels.npz.gz'
    if sha(old_path)!=old_receipt['retained_sha256'] or old_receipt['bbox']!=design['city']['bbox']:raise ValueError('Retained 2020 population drift')
    with np.load(io.BytesIO(gzip.decompress(old_path.read_bytes())),allow_pickle=False) as values:old={k:values[k].copy() for k in ('lat','lon','counts','valid')}
    datasets['worldpop-2020']=dict(source=old_receipt,access=coverage(old,design['stations'],cfg['sectors']))
    all_paths+=[old_path,old_dir/'population-source.json']
    graph_path=directory/'walking-graph.npz.gz';street_path=directory/'street-source.json';geometry_path=directory/'walking-streets.geojson.gz';street=json.loads(street_path.read_text())
    if street.get('extractor_sha256')!=sha(Path(__file__).with_name('mapping_evidence.py')):raise ValueError('Street extractor changed; fetch/reproduce graph')
    if street['bbox']!=design['city']['bbox'] or street['graph_sha256']!=sha(graph_path) or street['geometry_sha256']!=sha(geometry_path):raise ValueError('Street evidence drift')
    all_paths+=[graph_path,street_path,geometry_path]
    with np.load(io.BytesIO(gzip.decompress(graph_path.read_bytes())),allow_pickle=False) as data:graph={k:data[k].copy() for k in data.files}
    walking=walking_screen(selected,design['stations'],graph,cfg['streets']['walking_station_snap_limit_m'],cfg['streets']['walking_pixel_snap_limit_m'])
    summary=dict(schema='osr-city-mapping/1',city=city_slug,as_of=cfg['as_of'],selected_population=cfg['selected_population'],
                 datasets=datasets,streets=street,potential_walking_graph_access=walking,traffic=cfg['traffic'],sector_definitions=cfg['sectors'],
                 sector_boundary_basis=cfg['sector_boundaries'],release=cfg['release'],
                 sources_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in all_paths},
                 limitations=['Population sources and epochs differ; disagreement is not a measured growth rate','GHSL and WorldPop are different models with potentially shared census inputs, not independent ground truth','OSM roads and buildings are geometry, never measured traffic or dwelling occupancy','No source raises paid trips, fares or release acceptance automatically'])
    rows=[]
    for identity,item in datasets.items():
        for row in item['access']['sectors']:rows.append(f"| {identity} | {row['sector']} | {row['population']:,.0f} | {row['radial_fraction']:.1%} | {row['radial_unserved_population']:,.0f} |")
    text='\n'.join(['# Baghdad mapping inputs and neighbourhood access','',
        'Source-selected planning evidence. Population counts remain native; no averaging across datasets or scaling to the catalogue total.','',
        '| Population source | Sector | Native population | Within 1 km of a station | Outside station circles |','|---|---|---:|---:|---:|',*rows,'',
        'Sector rectangles are explicit planning areas, not official neighbourhood boundaries. Station circles are radial screens, not surveyed walksheds.','',
        f"The selected WorldPop 2026 epoch is an **alpha modelled projection**, not a current census. GHSL 2025 is a separate model comparison. Potential graph access within 1 km: **{walking['fraction']:.1%}**, with {walking['stations_with_bounded_snap']}/{walking['unique_stations']} unique stations snapped within {walking['station_snap_limit_m']} m. Snaps, entrances, foot permissions, sidewalks and accessible paths remain unverified. Roads connect only through shared OSM node IDs; paths outside the retained bbox are unavailable.",'',
        f"Dated street extract: {street['snapshot']}; {street['node_count']:,} pedestrian graph nodes, {street['edge_count']:,} edges; {street['building_way_count']:,} mapped building ways. Incomplete building mapping never means an empty neighbourhood.",'',
        'Measured traffic counts, speeds and origin–destination data are **unavailable**. Iraq is absent from current TomTom classic and Orbis Traffic API coverage tables. No measured traffic benefit or passenger demand is inferred.','',
        '[Selected sources, licences and sector policy](../../../../../../../design/network-planning/baghdad-mapping-sources.json) · [Machine-readable report and hashes](summary.json) · [Street geometry](walking-streets.geojson.gz) · [Research and integration policy](../../../../../../../docs/data/automatic-mapping-sources.md).',''])
    for path,raw in [(directory/'summary.json',encoded(summary)),(directory/'README.md',text.encode())]:
        if check:
            if not path.exists() or path.read_bytes()!=raw:raise ValueError('Stale mapping report: '+str(path))
        else:path.write_bytes(raw)
    print(json.dumps(dict(city=city_slug,selected=cfg['selected_population'],datasets=list(datasets),walking_screen_fraction=walking['fraction'],traffic='unavailable')))
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--city',default='baghdad');parser.add_argument('--fetch',action='store_true');parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.fetch and args.check:parser.error('Checking is offline')
    run(args.city,args.fetch,args.check)
if __name__=='__main__':main()
