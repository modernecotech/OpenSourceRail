"""Native-population corridor proximity, not station access or passenger demand.

All line distances use a declared spherical great-circle polyline. KDTree points
are no more than50m apart, so nearest-vertex distance overestimates that line's
true spherical distance by at most25m. Pixel counts remain native and are counted
once in the network union. Ellipsoid, route survey and resident locations within
pixels are separate uncertainties; this is not a verified walkshed.
"""
import gzip
import io
import json
import math
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

from engineering.twin_workflow import core
from . import site_context
from engineering.assurance.numerical_reproducibility import differences

EARTH_RADIUS_M=6371000.
STEP_M=50.
ROOT_ROUTE=Path('cities/catalogue/west-asia/Iraq/Baghdad/baghdad.corridor.geojson')
PIXELS=site_context.CITY/'mapping/worldpop-2026-pixels.npz.gz'
RECEIPT=site_context.CITY/'mapping/worldpop-2026-source.json'
# Reproduction only: sub-micrometre round-off in recomputed sampling diagnostics.
# Population sums, native counts, thresholds, geometry bytes, sources, decisions
# and the retained report's own content hash remain exact.
REPRODUCTION_RULES=((r'routes\[\d+\]\.geometry_sampling\.(?:spherical_length_m|maximum_spacing_m|maximum_distance_overestimate_m)',1e-7,1e-13),)


def xyz(lat,lon):
    lat=np.deg2rad(np.asarray(lat,dtype=float));lon=np.deg2rad(np.asarray(lon,dtype=float))
    return np.column_stack([np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)])


def sample_polyline(coordinates,spacing_m=STEP_M):
    values=np.asarray(coordinates,dtype=float)
    if values.ndim!=2 or values.shape[1]!=2 or len(values)<2 or not np.isfinite(values).all():
        raise ValueError('finite lon/lat polyline with at least two vertices required')
    if np.any(np.abs(values[:,0])>180) or np.any(np.abs(values[:,1])>90) or not 0<spacing_m<=50:
        raise ValueError('geographic coordinates and sampling spacing at most50m required')
    vertices=xyz(values[:,1],values[:,0]);points=[];length=0.;maximum=0.
    for a,b in zip(vertices,vertices[1:]):
        angle=math.atan2(float(np.linalg.norm(np.cross(a,b))),float(np.dot(a,b)))
        if angle<1e-14:continue
        if angle>=math.pi-1e-10:raise ValueError('antipodal segment is ambiguous')
        segment=EARTH_RADIUS_M*angle;n=max(1,math.ceil(segment/spacing_m));t=np.arange(n,dtype=float)/n
        p=np.sin((1-t)*angle)[:,None]/math.sin(angle)*a+np.sin(t*angle)[:,None]/math.sin(angle)*b
        points.append(p/np.linalg.norm(p,axis=1)[:,None]);length+=segment;maximum=max(maximum,segment/n)
    if not points:raise ValueError('nonzero route length required')
    points.append(vertices[-1:]);return np.concatenate(points)*EARTH_RADIUS_M,dict(
        spherical_length_m=length,sample_count=sum(len(p)for p in points),maximum_spacing_m=maximum,
        maximum_distance_overestimate_m=maximum/2)


def nearest_line_sample_distances(population,coordinates):
    points,receipt=sample_polyline(coordinates)
    tree=cKDTree(points)
    chord,_=tree.query(xyz(population['lat'],population['lon'])*EARTH_RADIUS_M,workers=1)
    distance=2*EARTH_RADIUS_M*np.arcsin(np.clip(chord/(2*EARTH_RADIUS_M),0,1))
    return distance,receipt


def summaries(counts,valid,distance,*,radii=(500.,1000.),algorithm_margin_m=25.,pixel_margin_m=71.):
    counts=np.asarray(counts);valid=np.asarray(valid);distance=np.asarray(distance)
    if counts.shape!=valid.shape or counts.shape!=distance.shape or valid.dtype!=np.bool_:
        raise ValueError('equal arrays and Boolean valid mask required')
    if np.any(valid&(~np.isfinite(counts)|(counts<0))) or np.any(~np.isfinite(distance)) or np.any(distance<0):
        raise ValueError('finite nonnegative population and distances required')
    def total(radius):
        keep=valid&(distance<=radius);return dict(persons=math.fsum(map(float,counts[keep])),native_pixels=int(keep.sum()))
    rows=[]
    for r in radii:
        if not math.isfinite(r) or r<=algorithm_margin_m+pixel_margin_m:raise ValueError('radius must exceed declared margins')
        rows.append(dict(radius_m=r,nominal=total(r),
            algorithm_bounds=dict(lower=total(r-algorithm_margin_m),upper=total(r+algorithm_margin_m)),
            algorithm_and_pixel_footprint_envelope=dict(lower=total(r-algorithm_margin_m-pixel_margin_m),
                                                       upper=total(r+algorithm_margin_m+pixel_margin_m)),
            algorithm_margin_m=algorithm_margin_m,pixel_footprint_margin_m=pixel_margin_m))
    return rows


def analyse(*,root=None):
    root=Path(root or core.ROOT);routes=site_context.read(root/ROOT_ROUTE);receipt=site_context.read(root/RECEIPT)
    if site_context.sha(root/PIXELS)!=receipt['retained_sha256']:raise ValueError('native population crop hash differs')
    pop=site_context.unpack(root/PIXELS);valid=pop['valid'];counts=pop['counts']
    selected=[f for f in routes['features']if f.get('properties',{}).get('kind')=='line']
    if not selected:raise ValueError('proposed line features required')
    identities=[f['properties']['name'] for f in selected]
    if len(set(identities))!=len(identities):raise ValueError('route identities must be unique')
    union=np.full(len(counts),np.inf);rows=[]
    for feature in selected:
        if feature['geometry']['type']!='LineString':raise ValueError('LineString route required')
        distance,geometry=nearest_line_sample_distances(pop,feature['geometry']['coordinates'])
        union=np.minimum(union,distance)
        rows.append(dict(id=feature['properties']['name'],geometry_sampling=geometry,
                         population_proximity=summaries(counts,valid,distance)))
    report=dict(schema='osr-baghdad-population-corridor-proximity/1',generator_sha256=site_context.sha(Path(__file__)),
        population_source=receipt,population_crop_extent=receipt['bbox'],route_count=len(rows),routes=rows,
        total_native_crop_population=math.fsum(map(float,counts[valid])),valid_pixels=int(valid.sum()),excluded_nodata_pixels=int((~valid).sum()),
        network_union=summaries(counts,valid,union),union_method='Minimum distance to any of14declared line polylines; native pixel counted once, never sum per-route populations',
        distance_model=dict(earth_radius_m=EARTH_RADIUS_M,geometry='Great-circle arcs between retained lon/lat vertices',
            spacing_limit_m=STEP_M,maximum_vertex_distance_overestimate_m=25.,
            algorithm_bounds='Conservative +/-25m threshold sensitivity; true spherical polyline distance lies between max(0,vertexdistance-25m) and vertexdistance',
            pixel_footprint_note='71m is a conservative half-diagonal envelope for nominal100m pixels; actual source3arcsecond dimensions differ with latitude. Native pixel centre does not locate individual residents.',
            spherical_to_wgs84_ellipsoid_distance_sensitivity='Up to0.6percent model-scale sensitivity remains separate;25m bounds concern the declared sphere only',
            independent_survey_error_m=None),
        input_sha256={p.as_posix():site_context.sha(root/p) for p in (ROOT_ROUTE,PIXELS,RECEIPT)},
        limitations=['Native WorldPop2026 alpha projected residents, not a current census, ridership or paid journeys',
            'Corridor buffers are not station catchments: entrances, river crossings, walking network, accessibility and station spacing are not modelled',
            'Routes are existing repository concepts, not surveyed, funded or operating lines',
            'Population outside the retained bbox is unknown and excluded, not zero; routes extend beyond some raster edge catchments',
            'Overlapping route results must never be summed; network_union is the unique native-pixel union',
            'Algorithm bounds address finite sampling on a sphere, not census/model error, future growth or individual resident location'],
        ridership=None,validated_walking_access=False,physical_acceptance=False,**core.FLAGS)
    report['revision']=core.digest(report);return report


def verify(report,*,root=None):
    if report.get('revision')!=core.digest({k:v for k,v in report.items() if k!='revision'}):
        raise ValueError('corridor retained report revision differs')
    expected=analyse(root=root)
    actual_values={k:v for k,v in report.items() if k!='revision'}
    expected_values={k:v for k,v in expected.items() if k!='revision'}
    changed=differences(actual_values,expected_values,rules=REPRODUCTION_RULES)
    if changed:raise ValueError('corridor population/source/revision differs at '+', '.join(changed[:8]))
    return dict(verified=True,routes=report['route_count'],
        reproduction_scope='Only named sampling diagnostics tolerate round-off; engineering limits and population/source/decision identity remain exact')
