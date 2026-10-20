"""A route map must represent a connected, continuously routed network."""
import sys
from pathlib import Path

import numpy as np
import pytest
from shapely.geometry import LineString

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from city_network_layout import components,connect_network,remove_small_knots,reverse_excursion
from residential_route_expansion import route_between
from retained_city_demand import sample_native,GridRef


def fixture():
    routes={'lines':[dict(name='west',shape='Radial',cells=[[r,20] for r in range(10,81)]),
                     dict(name='cross',shape='Radial',cells=[[50,c] for c in range(10,41)]),
                     dict(name='east',shape='Radial',cells=[[r,70] for r in range(10,81)])]}
    mask=np.zeros((100,100),dtype=np.uint8);buildable=np.ones_like(mask,dtype=bool)
    cfg=dict(route_search_margin_m=1000,maximum_water_crossing_m=100)
    def route(a,b,blocked):
        allowed=buildable.copy()
        for c in blocked or ():allowed[tuple(c)]=False
        return route_between(a,b,mask,allowed,cfg,20.)
    return routes,mask,buildable,route


def test_parallel_isolated_line_gets_a_real_continuous_connection():
    routes,mask,buildable,route=fixture()
    assert len(components(routes['lines']))==2
    revised,report=connect_network(routes,mask,buildable,20.,route)
    assert len(components(revised['lines']))==1
    assert {l['name'] for l in revised['lines']}=={l['name'] for l in routes['lines']}
    assert report['changes'] and not report['engineering_release']
    assert all(LineString(l['cells']).is_simple for l in revised['lines'])
    assert all(max(abs(a[0]-b[0]),abs(a[1]-b[1]))<=1
               for l in revised['lines'] for a,b in zip(l['cells'],l['cells'][1:]))


def test_protected_barrier_cannot_be_replaced_with_a_drawn_connector():
    routes,mask,buildable,route=fixture();buildable[:,50:61]=False
    with pytest.raises(ValueError,match='No bounded compliant connection'):
        connect_network(routes,mask,buildable,20.,route)


def test_unknown_water_is_a_barrier_not_a_dry_transfer():
    routes,mask,buildable,route=fixture();mask[:,50:61]=255
    with pytest.raises(ValueError,match='No bounded compliant connection'):
        connect_network(routes,mask,buildable,20.,route)


def test_connected_lines_are_preserved_exactly():
    routes,mask,buildable,route=fixture();routes['lines'].pop()
    revised,report=connect_network(routes,mask,buildable,20.,route)
    assert revised==routes and report['changes']==[]


def test_connected_simple_route_can_still_have_an_unacceptable_source_reversal():
    cells=[[0,0],[0,-100],[100,-100],[100,200]]
    assert LineString(cells).is_simple
    assert reverse_excursion(cells,20.)>750.
    assert reverse_excursion([[0,0],[0,100],[100,200]],20.)==0.


def test_disconnected_rings_require_a_separate_corridor_decision():
    routes={'lines':[dict(name=n,shape='Ring',cells=[[r,c],[r,c+5],[r+5,c+5],[r+5,c],[r,c]])
                     for n,r,c in [('a',5,5),('b',30,30)]]}
    mask=np.zeros((50,50),dtype=np.uint8)
    with pytest.raises(ValueError,match='No bounded compliant connection'):
        connect_network(routes,mask,np.ones_like(mask,dtype=bool),20.,lambda *args:None)


def test_a_projected_crossing_on_water_does_not_connect_the_passenger_network():
    lines=[dict(name='a',cells=[[0,5],[10,5]]),dict(name='b',cells=[[5,0],[5,10]])]
    mask=np.zeros((12,12),dtype=np.uint8);mask[5,5]=100
    assert len(components(lines))==1 and len(components(lines,mask))==2


def test_native_population_sampling_preserves_nodata_and_actual_cell_transform():
    grid=GridRef(height=3,width=4,cell_m=1,lat0=1,bbox_south=0,bbox_west=0,
                 bbox_north=3,bbox_east=4,m_per_deg_lat=1,m_per_deg_lon=1)
    values=dict(lat=np.array([.5,.5,2.5,2.5]),lon=np.array([.5,2.5,.5,2.5]),
                counts=np.array([10.,20.,30.,9999.]),valid=np.array([True,True,True,False]))
    counts,supported=sample_native(values,{'source_resolution_degrees':[2.,2.]},grid)
    assert counts[2,0]==10 and counts[0,0]==30
    assert counts[0,2]==0 and not supported[0,2]  # No invented people at nodata.
    assert counts[2,2]==20


def test_small_diagonal_knot_uses_a_dry_local_cell_edge_and_preserves_endpoints():
    cells=[[1,1],[2,2],[1,2],[2,1],[3,1]];mask=np.zeros((6,6),dtype=np.uint8)
    revised,changes=remove_small_knots(cells,20.,mask,np.ones_like(mask,dtype=bool))
    assert LineString(revised).is_simple and revised[0]==cells[0] and revised[-1]==cells[-1]
    assert changes and sum(c['removed_route_m'] for c in changes)<200
    mask[2,1]=100
    with pytest.raises(ValueError,match='larger controlled realignment'):
        remove_small_knots(cells,20.,mask,np.ones_like(mask,dtype=bool))


def test_large_loop_cannot_be_silently_removed_to_make_a_map_pass():
    cells=[[0,0],[0,1],[0,20],[20,20],[20,1],[0,1],[0,2]]
    mask=np.zeros((24,24),dtype=np.uint8)
    with pytest.raises(ValueError,match='larger controlled realignment'):
        remove_small_knots(cells,20.,mask,np.ones_like(mask,dtype=bool))


def test_connections_preserve_previously_selected_population_priority_sites():
    routes,mask,buildable,route=fixture();required={'cross':[[50,30]],'east':[[40,70]]}
    revised,report=connect_network(routes,mask,buildable,20.,route,protected_by_line=required)
    for line in revised['lines']:
        assert set(map(tuple,required.get(line['name'],[])))<=set(map(tuple,line['cells']))
    assert len(report['final_components'])==1


def test_geo_cli_reuses_checked_city_pixels_and_rejects_wrong_country_or_tampering(tmp_path,monkeypatch):
    import gzip,hashlib,io,json
    from osr_geo import cli
    from osr_osm.fetcher import BBox,CityOSM
    monkeypatch.setattr(cli,'__file__',str(tmp_path/'design/city-generation/src/osr_geo/cli.py'))
    city_dir=tmp_path/'cities/catalogue/east-africa/Kenya/Fixture';access=city_dir/'engineering/access';access.mkdir(parents=True)
    (city_dir/'design.toml').write_text('[city]\nslug="fixture"\ncountry="KE"\n[climate]\npreset="test"\n')
    grid=GridRef(height=3,width=4,cell_m=1,lat0=1,bbox_south=0,bbox_west=0,bbox_north=3,bbox_east=4,m_per_deg_lat=1,m_per_deg_lon=1)
    monkeypatch.setattr(cli,'_grid_ref',lambda *a:grid)
    values=dict(lat=np.array([.5,.5,2.5,2.5]),lon=np.array([.5,2.5,.5,2.5]),counts=np.array([10.,20.,30.,40.]),valid=np.ones(4,dtype=bool))
    stream=io.BytesIO();np.savez(stream,**values);raw=gzip.compress(stream.getvalue());pixels=access/'population-pixels.npz.gz';pixels.write_bytes(raw)
    (access/'population-source.json').write_text(json.dumps(dict(retained_sha256=hashlib.sha256(raw).hexdigest(),bbox=dict(south=0,west=0,north=3,east=4),source_resolution_degrees=[2.,2.],year=2020)))
    city=CityOSM(BBox(0,0,3,4),'fixture',0)
    assert cli.retained_population(city,'KE')[0,0]==30
    with pytest.raises(ValueError,match='jurisdiction/bbox'):
        cli.retained_population(city,'UG')
    pixels.write_bytes(raw+b'changed')
    with pytest.raises(ValueError,match='altered'):
        cli.retained_population(city,'KE')
