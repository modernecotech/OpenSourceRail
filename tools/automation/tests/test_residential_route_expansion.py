"""Missing-neighbourhood and constrained-route regression cases."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from residential_route_expansion import cell_lonlat, connect_nearby_rings, plan, route_between


def fixture():
    grid=dict(height=401,width=401,cell_m=20.,bbox_west=0.,bbox_north=1.,
              m_per_deg_lat=111132.,m_per_deg_lon=111132.)
    cells=[[200,c] for c in range(20,381)]
    routes=dict(lines=[dict(name='line-1',shape='Radial',anchor_ids=[],cells=cells)])
    positions=cell_lonlat([[200,20],[200,200],[200,380]],grid)
    stations=[dict(lat=float(lat),lon=float(lon)) for lon,lat in positions]
    neighbourhoods=([[r,c] for r in range(40,61) for c in range(210,231)]+
                    [[r,c] for r in range(340,361) for c in range(80,101)])
    positions=cell_lonlat(neighbourhoods,grid)
    population=dict(lat=positions[:,1],lon=positions[:,0],counts=np.full(len(positions),50.))
    cfg=dict(station_radius_m=1000.,maximum_ordinary_station_gap_m=2000.,priority_bin_m=500.,
             minimum_priority_separation_m=1500.,maximum_priority_areas=12,maximum_added_lines=4,
             maximum_added_route_fraction=2.,maximum_added_route_m=20000.,minimum_line_m=2000.,
             maximum_line_m=10000.,minimum_incremental_population=1000.,minimum_population_fraction_per_line=.003,
             maximum_water_crossing_m=1000.,route_search_margin_m=2000.,
             minimum_incremental_residents_per_km=500.,target_station_radial_fraction=.8)
    return grid,routes,stations,population,cfg


def test_missing_residential_areas_get_connected_additional_lines_and_population_union():
    grid,routes,stations,population,cfg=fixture()
    mask=np.zeros((401,401),dtype=np.uint8);buildable=np.ones_like(mask,dtype=bool)
    revised,report=plan(routes,stations,grid,mask,buildable,population,cfg)
    assert revised['lines'][0]==routes['lines'][0]
    assert report['added_line_count']>=2
    assert report['baseline_actual_station_radial_fraction']==0
    assert .8<=report['proposed_station_sample_radial_fraction']<=1
    assert report['actual_regenerated_station_coverage'] is None
    old={tuple(c) for c in routes['lines'][0]['cells']}
    assert all(tuple(line['cells'][0]) in old for line in revised['lines'][1:])
    assert all(a['property_curve_vertical_profile_and_structural_release'] is False for a in report['added_lines'])


def test_line_budget_exposes_remaining_gap_instead_of_claiming_target_completion():
    grid,routes,stations,population,cfg=fixture();cfg['maximum_added_lines']=1;cfg['target_station_radial_fraction']=1.
    _,report=plan(routes,stations,grid,np.zeros((401,401),dtype=np.uint8),np.ones((401,401),dtype=bool),population,cfg)
    assert report['added_line_count']==1
    assert not report['target_met_in_proposed_station_sample']
    assert report['proposed_station_sample_radial_fraction']<1


def test_route_cannot_use_unknown_or_protected_cells_or_unapproved_long_water():
    _,_,_,_,cfg=fixture()
    mask=np.zeros((201,201),dtype=np.uint8);buildable=np.ones_like(mask,dtype=bool)
    buildable[80:120,85:115]=False;mask[70:80,85:115]=255
    path=route_between((160,100),(40,100),mask,buildable,cfg,20.)
    assert all(buildable[cell] and mask[cell]!=255 for cell in path)
    mask[:]=0;buildable[:]=True;mask[60:120,:]=1
    with pytest.raises(ValueError,match='long water crossing'):
        route_between((160,100),(40,100),mask,buildable,cfg,20.)


def test_near_ring_approach_becomes_a_continuous_real_contact_without_losing_priority_site():
    _,_,_,_,cfg=fixture();mask=np.zeros((201,201),dtype=np.uint8);buildable=np.ones_like(mask,dtype=bool)
    route=[(r,100) for r in range(5,196)]
    ring=([(r,115) for r in range(20,181)]+[(180,c) for c in range(116,191)]+
          [(r,190) for r in range(179,19,-1)]+[(20,c) for c in range(189,114,-1)])
    revised=connect_nearby_rings(route,[(100,100)],[dict(cells=ring)],
        lambda a,b:route_between(a,b,mask,buildable,cfg,20.),20.)
    assert route[0] in revised and route[-1] in revised
    assert (100,100) in revised
    assert set(revised)&set(ring)
    from shapely.geometry import LineString
    assert LineString(revised).is_simple
