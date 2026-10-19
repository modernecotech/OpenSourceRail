"""Actual open-raster Baghdad context, separate from site or geotechnical design.

Reuses retained WorldPop/GHSL/WorldCover evidence. A small native SRTM-derived
window and WorldPop crop make the new city-context estimates portable. No soil,
groundwater, flood stage, roof height, parcel availability or demand is inferred.
"""
import gzip
import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np

from engineering.twin_workflow import core

BBOX=dict(west=44.1,south=33.1,east=44.6,north=33.5)
CITY=Path('cities/catalogue/west-asia/Iraq/Baghdad/engineering')
TERRAIN_SHA='0320d54b902d0e25f72f3ded4406591d8f389ef1d1f667d8ee960ee8e3766ee3'
TERRAIN_URL='https://elevation-tiles-prod.s3.amazonaws.com/skadi/N33/N33E044.hgt.gz'
LABELS={0:'unknown',10:'tree cover',20:'shrubland',30:'grassland',40:'cropland',50:'built-up',
        60:'bare/sparse vegetation',70:'snow/ice',80:'permanent water',90:'herbaceous wetland',95:'mangroves',100:'moss/lichen'}


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):return json.loads(Path(path).read_text())


def write(path,value):Path(path).write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def pack(path,**arrays):
    memory=io.BytesIO();np.savez(memory,**arrays)
    Path(path).write_bytes(gzip.compress(memory.getvalue(),mtime=0))


def unpack(path):
    with np.load(io.BytesIO(gzip.decompress(Path(path).read_bytes())),allow_pickle=False) as data:
        return {k:data[k].copy() for k in data.files}


def selection(pop,bbox):
    return (pop['lon']>=bbox['west'])&(pop['lon']<bbox['east'])&(pop['lat']>=bbox['south'])&(pop['lat']<bbox['north'])


def population_summary(pop,bbox):
    inside=selection(pop,bbox);valid=inside&pop['valid']
    if np.any(valid&(~np.isfinite(pop['counts'])|(pop['counts']<0))):raise ValueError('invalid native population count')
    return dict(persons=math.fsum(map(float,pop['counts'][valid])),valid_native_pixels=int(valid.sum()),
                excluded_nodata_pixels=int((inside&~pop['valid']).sum()),
                native_pixel_count=int(inside.sum()),resampled=False)


def crop_population(raster,bbox,target):
    import rasterio
    from rasterio.windows import from_bounds,Window
    with rasterio.open(raster) as src:
        if src.crs.to_epsg()!=4326 or src.count!=1 or src.transform.b or src.transform.d:
            raise ValueError('native one-band north-up WGS84 count raster required')
        w=from_bounds(bbox['west'],bbox['south'],bbox['east'],bbox['north'],src.transform)
        row,col=math.floor(w.row_off),math.floor(w.col_off)
        window=Window(col,row,math.ceil(w.col_off+w.width)-col,math.ceil(w.row_off+w.height)-row)
        data=src.read(1,window=window,boundless=True,masked=True);tr=src.window_transform(window)
        rows,cols=np.indices(data.shape);lon=tr.c+(cols+.5)*tr.a;lat=tr.f+(rows+.5)*tr.e
        p=dict(lon=lon.ravel(),lat=lat.ravel(),counts=np.asarray(data.filled(0),dtype=np.float32).ravel(),
               valid=(~np.ma.getmaskarray(data)).ravel())
        keep=selection(p,bbox);p={k:v[keep] for k,v in p.items()}
        p['valid']&=np.isfinite(p['counts'])&(p['counts']>=0);p['counts'][~p['valid']]=0
        pack(target,**p)
        return p,dict(resolution_degrees=[abs(tr.a),abs(tr.e)],units='persons per native pixel',
                      selection='Native pixel centres in half-open requested bbox, no count interpolation')


def retain_terrain(tile,bbox,target):
    if sha(tile)!=TERRAIN_SHA:raise ValueError('terrain source revision differs from retained provenance')
    raw=gzip.decompress(Path(tile).read_bytes())
    if len(raw)!=3601*3601*2:raise ValueError('invalid HGT tile size')
    source=np.frombuffer(raw,dtype='>i2').reshape(3601,3601)
    row0=math.ceil((34-bbox['north'])*3600-1e-7);row1=math.floor((34-bbox['south'])*3600+1e-7)+1
    col0=math.ceil((bbox['west']-44)*3600-1e-7);col1=math.floor((bbox['east']-44)*3600+1e-7)+1
    data=source[row0:row1,col0:col1].astype(np.int16)
    lats=34-np.arange(row0,row1)/3600;lons=44+np.arange(col0,col1)/3600
    pack(target,elevation_m=data,lat=lats,lon=lons)
    return dict(elevation_m=data,lat=lats,lon=lons)


def terrain_summary(terrain,bbox):
    ri=(terrain['lat']>=bbox['south']-1e-9)&(terrain['lat']<=bbox['north']+1e-9)
    ci=(terrain['lon']>=bbox['west']-1e-9)&(terrain['lon']<=bbox['east']+1e-9)
    data=terrain['elevation_m'][np.ix_(ri,ci)];valid=data[data!=-32768].astype(float)
    return dict(native_nodes=int(data.size),void_nodes=int(data.size-valid.size),
        minimum_m=float(valid.min()) if valid.size else None,median_m=float(np.median(valid)) if valid.size else None,
        maximum_m=float(valid.max()) if valid.size else None,
        percentiles_m={str(p):float(np.percentile(valid,p)) if valid.size else None for p in (5,95)},
        vertical_reference='SRTM-derived orthometric terrain reference; verify source geoid and survey datum before design',
        ground_survey=False,roof_heights=False)


def land_summary(classes,grid,bbox):
    counts=np.zeros(256,dtype=np.int64)
    for i,(dy,dx) in enumerate(((.25,.25),(.25,.75),(.75,.25),(.75,.75))):
        lats=grid['bbox_north']-(np.arange(grid['height'])+dy)*grid['cell_m']/grid['m_per_deg_lat']
        lons=grid['bbox_west']+(np.arange(grid['width'])+dx)*grid['cell_m']/grid['m_per_deg_lon']
        ri=(lats>=bbox['south'])&(lats<bbox['north']);ci=(lons>=bbox['west'])&(lons<bbox['east'])
        values=classes[np.ix_(ri,ci,[i])].ravel()
        counts+=np.bincount(values,minlength=256)
    total=int(counts.sum());known=total-int(counts[0]);weight=grid['cell_m']**2/4
    rows=[dict(code=int(code),label=LABELS.get(int(code),'unrecognised'),samples=int(counts[code]),
               approximate_area_km2=float(counts[code]*weight/1e6),
               fraction_of_known_samples=float(counts[code]/known) if known and code!=0 else None)
          for code in np.flatnonzero(counts)]
    return dict(classifications=rows,total_samples=total,unknown_samples=int(counts[0]),
        permanent_water_fraction_of_known_samples=float(counts[80]/known) if known else None,
        built_up_fraction_of_known_samples=float(counts[50]/known) if known else None,
        area_method='Four equally weighted 10m-class samples per20m local planning cell;100m2/sample approximate quadrature, not exact classified pixel area',
        approximate_sampled_area_km2=total*weight/1e6,current_shoreline=False,parcel_or_vacancy_inferred=False)


LIMITS=[
    'Context cells and bbox are planning rectangles, not administrative boundaries or an appointed alignment/site.',
    'WorldPop2026 is an alpha projected count model, not the2024 census or measured passenger demand.',
    'GHSL2025 and WorldPop2020 are kept separate and only have retained coverage eastof44.2E; no scaling or averaging.',
    'WorldCover2021 is historical surface classification, not land ownership, vacancy, current utilities or approved foundation terrain.',
    'Permanent-water classification is not flood probability, river stage, groundwater depth or a current bank survey.',
    'SRTM-derived heights are1arcsecond source samples and can contain surface/roof/canopy effects; no geotechnical or clearance acceptance.',
    'No soil bearing capacity, pile length, liquefaction, contamination, groundwater, roof height, utility depth or construction-release value is inferred.',
]


def build(output,tile,*,bbox=None,root=None):
    root=Path(root or core.ROOT);output=Path(output);output.mkdir(parents=True,exist_ok=True);bbox=dict(bbox or BBOX)
    if not bbox['west']<bbox['east'] or not bbox['south']<bbox['north']:raise ValueError('ordered bbox required')
    city=root/CITY;wp_receipt=read(city/'mapping/worldpop-2026-source.json')
    raster=root/'.cache/osr-pipeline/mapping/irq_pop_2026_CN_100m_R2025A_v1.tif'
    if sha(raster)!=wp_receipt['source_sha256']:raise ValueError('WorldPop native source differs')
    wp_path=output/'site-context-worldpop.npz.gz';terrain_path=output/'site-context-terrain.npz.gz'
    pop,wp_geometry=crop_population(raster,bbox,wp_path);terrain=retain_terrain(tile,bbox,terrain_path)
    grid_path=city/'alignment/planning-grid.json';land_path=city/'alignment/independent-landcover-samples.bin.gz'
    water_receipt_path=city/'alignment/water-source-receipt.json';water=read(water_receipt_path);grid=read(grid_path)
    for path in (grid_path,land_path):
        if sha(path)!=water['sources_sha256'][path.relative_to(root).as_posix()]:raise ValueError('retained WorldCover grid/sample hash differs')
    classes=np.frombuffer(gzip.decompress(land_path.read_bytes()),dtype=np.uint8).reshape(grid['height'],grid['width'],4)
    comparisons={};comparison_arrays={}
    for identity,directory,prefix in [('ghsl-2025',city/'mapping','ghsl-2025'),('worldpop-2020',city/'access','population')]:
        receipt=read(directory/(prefix+'-source.json'));pixels=directory/(prefix+'-pixels.npz.gz')
        if sha(pixels)!=receipt['retained_sha256']:raise ValueError('comparison population evidence hash differs')
        arrays=unpack(pixels);comparison_arrays[identity]=arrays
        overlap={k:(max if k in {'west','south'} else min)(bbox[k],receipt['bbox'][k]) for k in bbox}
        comparisons[identity]=dict(summary=population_summary(arrays,bbox),retained_extent=receipt['bbox'],
            compared_extent=overlap,selected_worldpop_on_same_extent=population_summary(pop,overlap),
            source=receipt,coverage='Requested bbox intersect retained extent; west44.1..44.2E missing, not zero')
    features=[];step=.05
    ncols=round((bbox['east']-bbox['west'])/step);nrows=round((bbox['north']-bbox['south'])/step)
    if abs(ncols*step-(bbox['east']-bbox['west']))>1e-8 or abs(nrows*step-(bbox['north']-bbox['south']))>1e-8:
        raise ValueError('context grid currently requires multiples of0.05degree')
    for row in range(nrows):
        for col in range(ncols):
            box=dict(west=bbox['west']+col*step,east=bbox['west']+(col+1)*step,
                     south=bbox['south']+row*step,north=bbox['south']+(row+1)*step)
            w,e,s,n=[box[k] for k in ('west','east','south','north')]
            properties=dict(id=f'baghdad-context-{row:02d}-{col:02d}',bbox=box,
                worldpop_2026=population_summary(pop,box),terrain=terrain_summary(terrain,box),
                worldcover_2021=land_summary(classes,grid,box),
                comparison_population={key:population_summary(arrays,box) for key,arrays in comparison_arrays.items()},
                construction_accepted=False)
            features.append(dict(type='Feature',id=properties['id'],properties=properties,
                                 geometry=dict(type='Polygon',coordinates=[[[w,s],[e,s],[e,n],[w,n],[w,s]]])))
    geo=dict(type='FeatureCollection',name='Baghdad actual open-data context estimates',bbox=[bbox[k] for k in ('west','south','east','north')],
             features=features,limitations=LIMITS)
    geo_path=output/'site-context.geojson';write(geo_path,geo)
    source_paths=[city/'mapping/worldpop-2026-source.json',grid_path,land_path,water_receipt_path,
                  city/'mapping/ghsl-2025-source.json',city/'mapping/ghsl-2025-pixels.npz.gz',
                  city/'access/population-source.json',city/'access/population-pixels.npz.gz']
    context=dict(schema='osr-baghdad-open-site-context/1',requested_bbox=bbox,as_of='2026-10-19',generator_sha256=sha(Path(__file__)),
        method='Actual source-native raster counts and sampled classifications/elevations;0.05degree context cells, no site-design acceptance',
        population=dict(selected='worldpop-2026',summary=population_summary(pop,bbox),source=wp_receipt,native_geometry=wp_geometry,
                        comparisons=comparisons),
        terrain=dict(summary=terrain_summary(terrain,bbox),source_url=TERRAIN_URL,source_sha256=TERRAIN_SHA,
                     publisher='Mapzen/TerrainTiles, SRTM-derived via public AWS bucket',
                     documentation='https://registry.opendata.aws/terrain-tiles/',
                     licence='Underlying SRTM public-domain attribution; verify merged source attribution at https://github.com/tilezen/joerd/blob/master/docs/attribution.md',
                     original_sample_epoch='SRTM2000-derived; source blend/resampling noted',retrieved='2026-10-19',
                     native_resolution_degrees=1/3600,surface_accuracy_m=None),
        land_water=dict(summary=land_summary(classes,grid,bbox),source_receipt=water,
            actual_retained_extent=dict(west=grid['bbox_west'],east=grid['bbox_east'],south=grid['bbox_south'],north=grid['bbox_north']),
            missing_requested_longitude_range=[bbox['west'],grid['bbox_west']],missing_coverage_is_not_dry_land=True,
            nominal_native_resolution_m=10,retained_sampling_cell_m=20),
        context_cell_count=len(features),context_cell_size_degrees=step,
        source_receipts_and_inputs_sha256={p.relative_to(root).as_posix():sha(p) for p in source_paths},
        portable_inputs_sha256={p.name:sha(p) for p in (wp_path,terrain_path,geo_path)},
        limitations=LIMITS,soil_parameters=None,groundwater_level_m=None,design_flood_level_m=None,
        roof_heights_m=None,ground_survey_accepted=False,digital_specification_complete=False,**core.FLAGS)
    context['revision']=core.digest(context);write(output/'site-context.json',context)
    return context


def verify(output,*,root=None):
    root=Path(root or core.ROOT)
    output=Path(output);context=read(output/'site-context.json');revision=context.pop('revision')
    if core.digest(context)!=revision:raise ValueError('context receipt revision differs')
    if context.get('generator_sha256')!=sha(Path(__file__)):raise ValueError('site context generator revision differs')
    for name,digest in context['portable_inputs_sha256'].items():
        if Path(name).name!=name or sha(output/name)!=digest:raise ValueError('portable context evidence differs')
    for name,digest in context['source_receipts_and_inputs_sha256'].items():
        path=Path(name)
        if path.is_absolute() or '..' in path.parts or sha(root/path)!=digest:
            raise ValueError('retained repository context source differs')
    pop=unpack(output/'site-context-worldpop.npz.gz');terrain=unpack(output/'site-context-terrain.npz.gz')
    bbox=context['requested_bbox']
    if population_summary(pop,bbox)!=context['population']['summary'] or terrain_summary(terrain,bbox)!=context['terrain']['summary']:
        raise ValueError('context aggregate differs from actual native samples')
    geo=read(output/'site-context.geojson')
    if len(geo['features'])!=context['context_cell_count']:raise ValueError('context cell count differs')
    grid=read(root/CITY/'alignment/planning-grid.json')
    classes=np.frombuffer(gzip.decompress((root/CITY/'alignment/independent-landcover-samples.bin.gz').read_bytes()),dtype=np.uint8).reshape(grid['height'],grid['width'],4)
    if land_summary(classes,grid,bbox)!=context['land_water']['summary']:
        raise ValueError('land/water aggregate differs from retained source samples')
    for feature in geo['features']:
        p=feature['properties']
        if p['worldpop_2026']!=population_summary(pop,p['bbox']) or p['terrain']!=terrain_summary(terrain,p['bbox']):
            raise ValueError('context cell differs from native samples')
        if p['worldcover_2021']!=land_summary(classes,grid,p['bbox']):
            raise ValueError('context cell land/water differs from source samples')
    if any(context.get(k) is not False for k in core.FLAGS):raise ValueError('unexpected release assertion')
    if any(context.get(k) is not False for k in ('ground_survey_accepted','digital_specification_complete')):
        raise ValueError('unsupported site-design acceptance assertion')
    return dict(verified=True,cells=len(geo['features']),population=context['population']['summary']['persons'])
