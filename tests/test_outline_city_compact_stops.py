"""Compact platforms must not inherit transitive chains of nearby markers."""
from copy import deepcopy
from math import fsum

import pytest

from engineering.outline.city_service import _repair_stops


def fixture(at, length=None, ring=False):
    stops=[dict(id='s'+str(i),chainage_m=float(x),dwell_s=35.,lon=x/100000,lat=0.) for i,x in enumerate(at)]
    length=float(length if length is not None else at[-1])
    legs=[dict(from_stop=a['id'],to_stop=b['id'],distance_m=b['chainage_m']-a['chainage_m'],closing_leg=False) for a,b in zip(stops,stops[1:])]
    if ring:legs.append(dict(from_stop=stops[-1]['id'],to_stop=stops[0]['id'],distance_m=length-at[-1]+at[0],closing_leg=True))
    return dict(line_id='test',shape='ring' if ring else 'radial',route_m=length,stops=stops,legs=legs)


def check(original,line,repair):
    assert len(line['stops'])>=2
    assert all(x['distance_m']>=120-1e-7 for x in line['legs'])
    assigned=[x for c in repair['complexes'] for x in c['original_stop_ids']]
    assert sorted(assigned)==sorted(x['id'] for x in original['stops'])
    assert len(assigned)==len(set(assigned))
    assert repair['maximum_added_walk_m']<=120
    assert repair['additional_shared_platform_length_m']==0
    assert repair['additional_access_walkway_m']==fsum(w['along_route_connector_m'] for c in repair['complexes'] for w in c['original_marker_walks'])
    assert all(c['boarding_platform_length_m']==120 for c in repair['complexes'])
    intervals=sorted(i for c in repair['complexes'] for i in c['boarding_platform_intervals_m'])
    assert all(a[1]<=b[0]+1e-7 for a,b in zip(intervals,intervals[1:]))


def test_long_transitive_chain_retains_compact_separated_platforms():
    original=fixture(list(range(0,2401,80)));before=deepcopy(original)
    line,repair=_repair_stops(original,120)
    check(original,line,repair)
    assert original==before
    assert len(line['stops'])==16
    assert repair['maximum_added_walk_m']==80
    assert repair['rejected_transitive_method_diagnostic']['group_count']==1
    assert repair['rejected_transitive_method_diagnostic']['maximum_added_walk_m']==2400
    assert not repair['rejected_transitive_method_diagnostic']['adopted']


def test_radial_terminals_retained_without_overlap():
    original=fixture(list(range(0,2201,110))+[2305])
    line,repair=_repair_stops(original,120);check(original,line,repair)
    assert [line['stops'][i]['chainage_m'] for i in (0,-1)]==[0,2305]


def test_ring_closure_and_split_platform_footprint():
    original=fixture(list(range(0,2400,80))+[2360],2400,True)
    line,repair=_repair_stops(original,120);check(original,line,repair)
    assert line['operational_route_m']==2400
    assert repair['complexes'][0]['boarding_platform_intervals_m']==[[2340,2400],[0,60]]


def test_connector_is_priced_without_long_boarding_platform():
    original=fixture([0,39,2000,3700])
    line,repair=_repair_stops(original,120);check(original,line,repair)
    assert [s['chainage_m'] for s in line['stops']]==[0,2000,3700]
    assert repair['additional_access_walkway_m']==39
    assert repair['complexes'][0]['original_marker_walks']==[
        dict(original_stop_id='s0',along_route_connector_m=0.),
        dict(original_stop_id='s1',along_route_connector_m=39.)]


def test_too_short_reference_route_is_not_falsely_completed():
    with pytest.raises(ValueError,match='cannot fit two'):_repair_stops(fixture([0,39]),120)


def test_nontransitive_pattern_is_repeatable():
    original=fixture([0,80,160,240,320,1000])
    assert _repair_stops(original,120)==_repair_stops(original,120)


def test_coincident_access_markers_remain_distinct_without_duplicate_platforms():
    original=fixture([0,0,80,160,160,2000])
    line,repair=_repair_stops(original,120);check(original,line,repair)
    assert len(line['stops'])==3
    assert repair['original_stop_count']==6
    assert repair['complexes'][0]['original_stop_ids']==['s0','s1','s2']
    assert repair['complexes'][1]['original_stop_ids']==['s3','s4']
