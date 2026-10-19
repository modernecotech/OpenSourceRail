"""Frozen real GIS evidence, open geotechnical gates and portable map replay."""
from copy import deepcopy
import gzip
import json
import math
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

import pytest

from engineering.assembly_design import site_screening as site
from engineering.twin_workflow import core


def test_real_sources_and_existing_proposed_routes_are_bound():
    report=site.snapshot();raw=json.loads(gzip.decompress(site.RAW.read_bytes()))
    assert report['osm_snapshot_utc']==raw['osm3s']['timestamp_osm_base']
    assert report['source_descriptions']['fresh_osm']['parsed_response_features']==len(raw['elements'])>=7000
    assert report['bbox_lonlat']==[44.1,33.1,44.6,33.5]
    assert len(report['routes'])==14
    assert {r['id'] for r in report['routes']}=={'line-'+str(i) for i in range(1,15)}
    assert 'concept' in report['source_descriptions']['proposed_routes']['status']
    assert 'ODbL' in report['source_descriptions']['fresh_osm']['license']
    assert all(not report[k] for k in core.FLAGS)
    assert report['site_investigation_complete'] is False and report['soil_parameters_adopted'] is False


def test_actual_exposure_metrics_and_investigation_quantities_are_consistent():
    report=site.snapshot()
    assert report['estimates']['mapped_water_polygon_area_km2']>0
    assert report['estimates']['mapped_rail_length_km']>0
    assert report['estimates']['mapped_landuse_area_km2']['farmland']>0
    assert sum(r['length_m'] for r in report['routes'])==pytest.approx(report['estimates']['route_length_sum_m'],abs=.02)
    for route in report['routes']:
        lengths=[route['water_proximity_length_m'][str(radius)] for radius in (100,250,500,1000)]
        assert 0<=lengths[0]<=lengths[1]<=lengths[2]<=lengths[3]<=route['length_m']+.02
        for scenario in route['investigation_quantity_scenarios']:
            assert scenario['nominal_chainage_locations']==math.ceil(route['length_m']/scenario['spacing_m'])+1
            assert 'Proposed' in scenario['basis']
        assert 0<=route['mapped_water_overlap_m']<=route['length_m']+.02
    for parcel in report['landuse_investigation_candidates']:
        assert parcel['land_availability'] is None and parcel['ownership'] is None
        assert parcel['soil_bearing_capacity_pa'] is None and parcel['groundwater_depth_m'] is None
        assert parcel['area_m2']>=20000 and parcel['distance_to_proposed_route_m']<=2000
    assert report['coverage']['roads_missing_requested_western_strip']==[44.1,33.1,44.2,33.5]


def test_map_contains_real_geometry_river_crossings_population_and_scale():
    report=site.snapshot();artifact=site.build(report);geojson=json.loads(artifact['geojson'])
    assert geojson['type']=='FeatureCollection'
    categories={f['properties']['category'] for f in geojson['features']}
    assert {'proposed-route','major-road','river-crossing','water-area','rail','power','population-context'}<=categories
    cells=[f for f in geojson['features'] if f['properties']['category']=='population-context']
    assert len(cells)==80 and all(f['properties']['modelled_persons']>=0 for f in cells)
    assert all(f['properties']['year']==2026 for f in cells)
    svg=ET.fromstring(artifact['svg'])
    assert svg.tag.endswith('svg')
    for label in ('Tigris','Karkh','Rusafa','5 km','WorldPop2026','groundwater depth'):
        assert label in artifact['svg']
    assert '<circle' in artifact['svg'] and '2026-10-19' in artifact['svg']


def test_portable_source_bundle_verifies_and_rebuilds_without_repo_gis_paths(tmp_path):
    expected=site.snapshot();root=tmp_path/'portable'
    for name in site.source_paths():
        target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(core.ROOT/name,target)
    data_dir=root/site.REPORT.parent.relative_to(core.ROOT)
    report=site.verify(data_dir,root=root)
    assert report['revision']==expected['revision']
    assert site.build(report,root=root)==site.build(expected)
    raw=root/site.RAW.relative_to(core.ROOT);raw.write_bytes(raw.read_bytes()+b'tamper')
    with pytest.raises(ValueError,match='source changed'):site.verify(data_dir,root=root)


@pytest.mark.parametrize('defect',('revision','code','escape','release','soil'))
def test_tampered_or_overclaimed_report_rejected(tmp_path,defect):
    report=deepcopy(site.snapshot())
    if defect=='revision':report['revision']='0'*64
    else:
        if defect=='code':report['analysis_code_sha256']='0'*64
        elif defect=='escape':report['source_sha256']['../escape']='0'*64
        elif defect=='release':report['manufacturing_release']=True
        elif defect=='soil':report['soil_parameters_adopted']=True
        report['revision']=core.digest({k:v for k,v in report.items() if k!='revision'})
    core.write(tmp_path/site.REPORT.name,report)
    with pytest.raises(ValueError):site.verify(tmp_path)
