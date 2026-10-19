"""Independent spherical line controls and exact native-count union semantics."""
from copy import deepcopy
import math

import numpy as np
import pytest

from engineering.assembly_design import site_catchments as s,site_context
from engineering.twin_workflow import core


def test_equator_cross_track_control_and_sampling_bound_independent_of_kdtree():
    pop=dict(lat=np.array([.001,.002,-.003,0.]),lon=np.array([.000123,.0021,-.0023,.00004]))
    distance,receipt=s.nearest_line_sample_distances(pop,[[-.01,0.],[.01,0.]])
    exact=s.EARTH_RADIUS_M*np.deg2rad(np.abs(pop['lat']))
    assert np.all(distance>=exact-1e-7)
    assert np.all(distance-exact<=25.+1e-7)
    assert receipt['maximum_spacing_m']<=50.
    # Nearest endpoint when longitudinally outside the line, checked by haversine.
    p=dict(lat=np.array([0.]),lon=np.array([.02]))
    d,_=s.nearest_line_sample_distances(p,[[-.01,0.],[.01,0.]])
    assert d[0]==pytest.approx(s.EARTH_RADIUS_M*math.radians(.01),abs=1e-7)


def test_native_count_bounds_and_duplicate_routes_count_once_in_union():
    counts=np.array([10.,20.,30.,40.]);valid=np.array([True,True,True,False]);distances=np.array([470.,500.,530.,100.])
    row=s.summaries(counts,valid,distances,radii=[500.])[0]
    assert row['nominal']['persons']==30
    assert row['algorithm_bounds']['lower']['persons']==10
    assert row['algorithm_bounds']['upper']['persons']==30
    assert row['algorithm_and_pixel_footprint_envelope']['upper']['persons']==60
    union=np.minimum(distances,distances)
    assert s.summaries(counts,valid,union,radii=[500.])[0]['nominal']['persons']==30


def test_line_vertices_turns_zero_segments_and_invalid_inputs():
    pop=dict(lat=np.array([0.]),lon=np.array([0.]))
    d,r=s.nearest_line_sample_distances(pop,[[0.,0.],[0.,0.],[.001,0.],[.001,.001]])
    assert d[0]==pytest.approx(0,abs=1e-8)
    with pytest.raises(ValueError):s.sample_polyline([[0.,0.],[0.,0.]])
    with pytest.raises(ValueError):s.sample_polyline([[0.,0.],[180.,0.]])
    with pytest.raises(ValueError):s.sample_polyline([[0.,0.],[.01,0.]],spacing_m=100.)


def test_actual_fourteen_route_report_is_native_union_with_provenance():
    p=core.ROOT/'engineering/assembly_design/data/site-catchments.json';report=site_context.read(p)
    assert s.verify(report)['verified']
    assert report['route_count']==14 and len(report['routes'])==14
    assert report['population_source']['status'].startswith('alpha')
    for radius in (0,1):
        total=report['network_union'][radius]['nominal']['persons']
        perroute=[r['population_proximity'][radius]['nominal']['persons']for r in report['routes']]
        assert max(perroute)<=total<=sum(perroute)
        assert total<=report['total_native_crop_population']
        bounds=report['network_union'][radius]['algorithm_bounds']
        assert bounds['lower']['persons']<=total<=bounds['upper']['persons']
    assert report['network_union'][0]['nominal']['persons']<=report['network_union'][1]['nominal']['persons']
    assert report['ridership'] is None and not report['validated_walking_access']
    changed=deepcopy(report);changed['network_union'][0]['nominal']['persons']+=1
    with pytest.raises(ValueError):s.verify(changed)
