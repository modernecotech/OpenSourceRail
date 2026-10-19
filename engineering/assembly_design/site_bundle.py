"""Portable desktop-investigation estimates on the existing publication path."""
import gzip
import io
from pathlib import Path
import tarfile
import tempfile

from engineering.twin_workflow import core
from engineering.design_delivery.pipeline import archive_members,safe
from . import site_context,site_screening,site_catchments

DATA=Path(__file__).parent/'data'
MAX_RAW=48*1024**2


def metrics(value):
    context=value['context'];screen=value['screening'];catchments=value['catchments']
    return dict(requested_bbox=context['requested_bbox'],modelled_population=context['population']['summary']['persons'],
        median_elevation_m=context['terrain']['summary']['median_m'],
        elevation_percentiles_m=context['terrain']['summary']['percentiles_m'],
        classified_area_km2=context['land_water']['summary']['approximate_sampled_area_km2'],
        built_up_fraction=context['land_water']['summary']['built_up_fraction_of_known_samples'],
        permanent_water_fraction=context['land_water']['summary']['permanent_water_fraction_of_known_samples'],
        missing_landcover_longitudes=context['land_water']['missing_requested_longitude_range'],
        concept_route_count=len(screen['routes']),concept_route_length_km=screen['estimates']['route_length_sum_m']/1000,
        river_centreline_crossings=sum(r['river_centreline_crossings'] for r in screen['routes']),
        investigation_locations={str(spacing):sum(next(s['nominal_chainage_locations'] for s in r['investigation_quantity_scenarios'] if s['spacing_m']==spacing) for r in screen['routes']) for spacing in (250,500)},
        landuse_investigation_candidates=len(screen['landuse_investigation_candidates']),
        network_corridor_population=catchments['network_union'],population_corridor_crop_extent=catchments['population_crop_extent'],
        population_corridor_basis='WorldPop2026 model and concept-line proximity; different retained extent from context total, unique-pixel network union, not ridership/walking access',
        site_investigation_complete=False)


def paths():
    context=core.read(DATA/'site-context.json')
    catchments=core.read(DATA/'site-catchments.json')
    values={*(str((DATA/name).relative_to(core.ROOT)) for name in ['site-context.json',*context['portable_inputs_sha256'],'site-catchments.json']),
            *context['source_receipts_and_inputs_sha256'],*catchments['input_sha256'],*site_screening.source_paths()}
    return sorted(values)


def snapshot():
    site_context.verify(DATA)
    screening=site_screening.snapshot()
    catchments=core.read(DATA/'site-catchments.json')
    # This recomputation is bounded to retained pixels and 14 concept routes;
    # no live network or whole-country data download occurs.
    site_catchments.verify(catchments)
    files={name:core.sha(core.ROOT/safe(name)) for name in paths()}
    if sum((core.ROOT/name).stat().st_size for name in files)>MAX_RAW:
        raise ValueError('portable site evidence exceeds budget')
    return dict(schema='osr-baghdad-site-review-bundle/1',context=core.read(DATA/'site-context.json'),
        screening=screening,catchments=catchments,files_sha256=files,
        scope='Actual open-data desktop estimates for investigation planning. No adopted soil capacity, groundwater/flood level, land title, buried utility clearance or site acceptance.',
        **core.FLAGS)


def export(value,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    raw=0
    with (output/'evidence.tar.gz').open('wb') as stream,gzip.GzipFile(fileobj=stream,mode='wb',mtime=0,filename='') as zipped,tarfile.open(fileobj=zipped,mode='w|') as archive:
        for name,digest in sorted(value['files_sha256'].items()):
            content=(core.ROOT/safe(name)).read_bytes();raw+=len(content)
            if core.sha(core.ROOT/name)!=digest or raw>MAX_RAW:raise ValueError('site evidence changed or exceeded budget')
            info=tarfile.TarInfo(name);info.size=len(content);info.mtime=0;archive.addfile(info,io.BytesIO(content))
    core.write(output/'summary.json',value)
    image=site_screening.build(value['screening'])
    (output/'map.svg').write_text(image['svg'])
    (output/'map.geojson.gz').write_bytes(gzip.compress(image['geojson'].encode(),mtime=0))


def verify(value,output):
    output=Path(output)
    if core.read(output/'summary.json',maximum=20_000_000)!=value:
        raise ValueError('site display summary differs from frozen baseline')
    if any(value.get(k) is not False for k in core.FLAGS):raise ValueError('desktop site data cannot issue release')
    members=archive_members(output/'evidence.tar.gz')
    if set(members)!=set(value['files_sha256']) or sum(map(len,members.values()))>MAX_RAW:
        raise ValueError('site raw evidence membership/budget differs')
    from hashlib import sha256
    for name,digest in value['files_sha256'].items():
        if sha256(members[safe(name)]).hexdigest()!=digest:raise ValueError('site raw evidence differs')
    with tempfile.TemporaryDirectory(prefix='osr-site-review-') as temporary:
        root=Path(temporary)
        for name,content in members.items():
            path=root/safe(name);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content)
        data=root/'engineering/assembly_design/data'
        site_context.verify(data,root=root)
        site_screening.verify(data,root=root)
        site_catchments.verify(value['catchments'],root=root)
        image=site_screening.build(value['screening'],root=root)
        if (output/'map.svg').read_text()!=image['svg'] or gzip.decompress((output/'map.geojson.gz').read_bytes()).decode()!=image['geojson']:
            raise ValueError('site map differs from frozen raw geometry')
    return dict(verified=True,source_files=len(members),physical_validation=False)
