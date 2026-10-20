"""Recover a relative routing-demand layer from retained native population pixels.

This is a nearest-pixel planning index, not new population evidence. Resampled
values must never be summed to estimate residents or ridership.
"""
import gzip
import hashlib
import io
import json
import sys
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'design/city-generation/src'))
from osr_geo.cli import _load_city
from osr_geo.population import population_demand_layer, sample_retained_population_into_grid
from osr_geo.rasterize import GridRef,DEMAND_RADIUS_M,build_demand_surface


sample_native = sample_retained_population_into_grid


def restore(city,grid,check=False):
    pixels=city/'engineering/access/population-pixels.npz.gz';receipt=city/'engineering/access/population-source.json'
    if not pixels.exists() or not receipt.exists():return None,[]
    source=json.loads(receipt.read_text());raw=pixels.read_bytes()
    status=city/'engineering/access/summary.json'
    if status.exists() and json.loads(status.read_text())['population']['status']!='available':
        return None,[pixels,receipt,status]
    if hashlib.sha256(raw).hexdigest()!=source['retained_sha256']:raise ValueError('Retained population bytes differ')
    expected={k:getattr(grid,'bbox_'+k) for k in ('south','west','north','east')}
    if source['bbox']!=expected:raise ValueError('Retained population bbox differs from native route grid')
    with np.load(io.BytesIO(gzip.decompress(raw)),allow_pickle=False) as archive:
        population,supported=sample_native(archive,source,grid)
    design=city/'design.toml'
    import tomllib
    slug=tomllib.loads(design.read_text())['city']['slug']
    cache=ROOT/'.cache/osr-pipeline';osm=cache/'osm'/(slug+'.json')
    anchors=city/'engineering/alignment/network-demand-anchors.json'
    if not anchors.exists():
        if check:raise ValueError('Missing retained OSM demand anchors')
        value=json.loads(osm.read_text())
        anchors.write_text(json.dumps({k:value[k] for k in ('bbox','slug','fetched_at','anchors')}|
            dict(source_osm_sha256=hashlib.sha256(osm.read_bytes()).hexdigest(),attribution='OpenStreetMap contributors; ODbL 1.0'),sort_keys=True,indent=2)+'\n')
    geo=_load_city(anchors)
    layer=population_demand_layer(population,DEMAND_RADIUS_M/grid.cell_m)
    demand=build_demand_surface(geo,grid,population_layer=layer)
    raw=demand.astype('<f4').tobytes();target=city/'engineering/alignment/network-demand.f32.gz'
    metadata=dict(schema='osr-retained-native-demand/1',city=slug,population_source=source,
                  sampled_route_grid_cells=int(population.size),supported_native_grid_fraction=float(supported.mean()),
                  demand_sha256=hashlib.sha256(raw).hexdigest(),osm_json_sha256=json.loads(anchors.read_text())['source_osm_sha256'],
                  basis='Nearest retained WorldPop pixel at each actual native grid cell centre, existing log/smooth/normalise and OSM anchor blend; relative routing/station index only. Unsupported cells receive no population contribution, not an assertion of no residents.',
                  physical_release=False)
    report=target.with_name('network-demand-source.json')
    data=(json.dumps(metadata,indent=2,sort_keys=True)+'\n').encode()
    if check:
        if gzip.decompress(target.read_bytes())!=raw or report.read_bytes()!=data:raise ValueError('Stale retained population demand')
    else:
        target.write_bytes(gzip.compress(raw,mtime=0));report.write_bytes(data)
        (cache/'rasters'/(slug+'.demand.npy')).write_bytes(raw)
    return metadata,[pixels,receipt,target,report,anchors,Path(__file__),ROOT/'design/city-generation/src/osr_geo/cli.py',ROOT/'design/city-generation/src/osr_geo/rasterize.py',ROOT/'design/city-generation/src/osr_geo/population.py']
