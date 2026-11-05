from copy import deepcopy
from pathlib import Path
import pytest
from engineering.outline import city_alignment as a
from engineering.station_rail.common import identity


def make_city(ring=False,bridge=False):
    points=[[0.,0.],[.01,.0002],[.02,0.]] if not ring else [[0.,0.],[.02,0.],[.02,.02],[0.,.02],[0.,0.]]
    chain=a.chainages(points);ids=['a','b','c','d'] if ring else ['a','c']
    stops=[dict(id=k,chainage_m=chain[i if ring else 2*i],lon=points[i if ring else 2*i][0],lat=points[i if ring else 2*i][1],dwell_s=35.) for i,k in enumerate(ids)]
    line=dict(line_id='A',shape='ring' if ring else 'radial',coordinates=points,coordinate_chainages_m=chain,route_m=chain[-1],stops=stops)
    a._legs(line)
    c=dict(city=dict(slug='fixture',country='XX'),lines=[line],interchanges=[],civil_segments=[dict(line_id='A',**{'class':'bridge' if bridge else 'elevated'},from_m=0.,to_m=chain[-1])],source_sha256={})
    c['input_id']=identity(c);return c


def test_original_is_preserved_and_revision_has_exact_geometry_identity_and_risk():
    c=make_city();before=deepcopy(c)
    v=a.propose(c,policy={'alignment':{'minimum_relative_saving':.00001,'minimum_saving_m':.01}})
    assert c==before and v['variants'][0]['city_input']==before
    candidate=v['variants'][1];new=candidate['city_input'];line=new['lines'][0]
    assert line['route_m']<c['lines'][0]['route_m']
    assert new['input_id']==identity({k:z for k,z in new.items() if k!='input_id'})
    assert candidate['risk_quantities']['additional_row_area_m2']>0
    assert all(new[k] is False for k in a.FLAGS)
    assert v['original_maps_modified'] is False


def test_stop_coordinates_and_civil_crossing_boundaries_are_anchor_constraints():
    c=make_city();stop=dict(id='b',chainage_m=c['lines'][0]['coordinate_chainages_m'][1],lon=.01,lat=.0002,dwell_s=35.)
    c['lines'][0]['stops'].insert(1,stop);c.pop('input_id');c['input_id']=identity(c)
    v=a.propose(c,policy={'alignment':{'minimum_relative_saving':.00001,'minimum_saving_m':.01}})['variants'][1]['city_input']
    assert [(z['lon'],z['lat']) for z in v['lines'][0]['stops']]==[(z['lon'],z['lat']) for z in c['lines'][0]['stops']]
    assert len(v['lines'][0]['coordinates'])>=3
    b=make_city(bridge=True);v=a.propose(b)['variants'][1]['city_input']
    assert v['lines'][0]['coordinates']==b['lines'][0]['coordinates']


def test_square_ring_has_four_edge_stations_sampled_curves_and_explicit_access_failure():
    c=make_city(ring=True);v=a.propose(c)
    square=v['variants'][2];line=square['city_input']['lines'][0]
    assert square['kind']=='rounded-four-edge-ring-research'
    assert len(line['stops'])==4
    assert len(line['coordinates'])>40 and line['coordinates'][0]==line['coordinates'][-1]
    assert line['design_speed_cap_m_s']==pytest.approx((line['minimum_turn_radius_m']*.5)**.5)
    assert square['selection_eligibility']['access_screen']=='fail'
    assert square['selection_eligibility']['status']=='hold'
    assert square['risk_quantities']['unverified_bridge_route_m_hypothesis']>0
    assert square['city_input']['alignment_hypothesis']['lines'][0]['quieter_operation_demonstrated'] is False


def test_mandatory_transfer_stop_retained_as_projected_station_and_access_still_checked():
    c=make_city(ring=True);c['interchanges']=[dict(id='X',platforms=['a'])];c.pop('input_id');c['input_id']=identity(c)
    v=a.propose(c)['variants'][2]
    assert 'a' in {z['id'] for z in v['city_input']['lines'][0]['stops']}
    assert v['selection_eligibility']['actual_walk_network_verified'] is False
    assert v['selection_eligibility']['physical_clearance_approval'] is False


def test_alignment_invalid_source_or_policy_rejected():
    c=make_city();c['lines'][0]['route_m']=0.
    with pytest.raises(ValueError,match='identity'):a.propose(c)
    with pytest.raises(ValueError):a.propose(make_city(),policy={'alignment':{'square_scale':2}})


def test_geometry_export_is_standalone_geojson_and_civil_lengths_reconcile():
    v=a.propose(make_city(ring=True))
    for variant in v['variants']:
        assert variant['geometry_geojson']['type']=='FeatureCollection'
        c=variant['city_input'];line=c['lines'][0]
        assert sum(z['to_m']-z['from_m'] for z in c['civil_segments'])==pytest.approx(line['route_m'])
        assert a.chainages(line['coordinates'])[-1]==pytest.approx(line['route_m'])
