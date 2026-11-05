"""Compressed presentation preserves completed calculations and release gates."""
from pathlib import Path
import json

import pytest

from engineering.outline import completion_publication as publication
from engineering.station_rail.common import encoded,identity,digest


@pytest.fixture(scope='module')
def published():
    return publication.verify()


def test_every_published_city_and_design_is_available_without_private_runs(published):
    manifest,value=published
    assert value['completed_cities']==266 and value['outline_accepted_cities']==266
    assert value['designs']['declared_design_count']==184
    assert len(manifest['files_sha256'])==533
    assert all('line_outlines' not in row for row in value['cities'])
    assert len(encoded(value))<4*1024**2


def test_city_detail_and_map_keep_same_calculated_identity_and_no_release(published):
    manifest,value=published
    root=Path(publication.ROOT)/publication.PUBLICATION
    row=next(r for r in value['cities'] if r['city']['slug']=='baghdad')
    detail=publication.read_json(root/'cities/baghdad.json.gz')
    geo=publication.read_json(root/'maps/baghdad.geojson.gz')
    assert detail['evaluation_id']==row['evaluation_id']
    assert detail['installed_capital_usd']==row['installed_capital_usd']
    assert detail['delivery_draft']['ERPNext']['disabled']==1
    assert detail['civil_quantities']['route_m']/1000==pytest.approx(row['route_km'])
    assert geo['type']=='FeatureCollection' and geo['features']
    assert any(f['properties']['variant']=='rounded-four-edge-ring-research' for f in geo['features'])
    assert all(detail[k] is False and geo[k] is False for k in publication.FLAGS)


def test_gzip_header_and_inflated_read_budget_are_explicit(tmp_path):
    path=tmp_path/'bounded.json.gz'
    publication._write_gzip(path,{'value':'x'*1000})
    raw=path.read_bytes()
    assert raw[4:8]==b'\0\0\0\0' and raw[9]==255
    with pytest.raises(ValueError,match='read budget'):
        publication.read_json(path,maximum=100)


def test_resealed_release_flag_is_rejected_before_reading_payload(tmp_path,published):
    manifest=json.loads(json.dumps(published[0]));manifest['operating_release']=True
    manifest['manifest_id']=identity({k:v for k,v in manifest.items() if k!='manifest_id'})
    (tmp_path/'manifest.json').write_bytes(encoded(manifest))
    with pytest.raises(ValueError,match='disposition differs'):
        publication.verify(tmp_path)


def test_resealed_city_path_escape_is_rejected(tmp_path,published):
    manifest=json.loads(json.dumps(published[0]));value=json.loads(json.dumps(published[1]))
    value['cities'][0]['city']['slug']='../outside'
    value['catalogue_id']=identity({k:v for k,v in value.items() if k!='catalogue_id'})
    manifest['catalogue_id']=value['catalogue_id']
    (tmp_path/'summary.json').write_bytes(encoded(value))
    manifest['files_sha256']['summary.json']=digest(tmp_path/'summary.json')
    manifest['manifest_id']=identity({k:v for k,v in manifest.items() if k!='manifest_id'})
    (tmp_path/'manifest.json').write_bytes(encoded(manifest))
    with pytest.raises(ValueError,match='Unique complete city catalogue'):
        publication.verify(tmp_path)
