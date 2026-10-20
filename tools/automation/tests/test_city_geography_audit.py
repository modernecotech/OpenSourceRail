"""Independent geometry checks must reject nearby stops and wet platforms."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('city_geography_audit', ROOT/'tools/automation/audit-city-geography.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def test_nearby_grouped_stops_do_not_satisfy_an_actual_crossing():
    grid = dict(bbox_north=1.0,bbox_west=0.0,m_per_deg_lat=1000,m_per_deg_lon=1000,cell_m=20)
    def coord(row,col):return [(col+.5)*.02,1-(row+.5)*.02]
    features = {'features':[{'properties':{'name':name},'geometry':{'type':'LineString','coordinates':[coord(*a),coord(*b)]}}
                for name,a,b in [('A',(50,0),(50,99)),('B',(0,50),(99,50))]]}
    def station(name,row,col):
        lon,lat=coord(row,col)
        return dict(id=name,line=name,lon=lon,lat=lat,junction_group=0)
    mask=np.zeros((100,100),dtype=np.uint8)
    far={'stations':[station('A',50,40),station('B',40,50)]}
    result=audit.check_design(far,features,grid,mask)
    assert not result['passed'] and len(result['missing_crossing_platforms'])==1
    exact={'stations':[station('A',50,50),station('B',50,50)]}
    assert audit.check_design(exact,features,grid,mask)['passed']
    mask[50,50]=25
    result=audit.check_design(exact,features,grid,mask)
    assert not result['passed'] and len(result['wet_platforms'])==2
    mask[50,50]=255
    result=audit.check_design(exact,features,grid,mask)
    assert not result['passed'] and len(result['unknown_platforms'])==2


def test_shared_curved_trunk_requires_platforms_at_its_junctions_only():
    grid = dict(bbox_north=1.0, bbox_west=0.0, m_per_deg_lat=1000,
                m_per_deg_lon=1000, cell_m=20)
    def coord(row, col):
        return [(col+.5)*.02, 1-(row+.5)*.02]
    trunk = [(40, 40), (45, 45), (45, 50), (50, 55), (60, 60)]
    features = {'features': [
        {'properties': {'name': name}, 'geometry': {'type': 'LineString',
         'coordinates': [coord(*p) for p in points]}}
        for name, points in [('A', [(40, 0)]+trunk+[(60, 99)]),
                             ('B', [(0, 40)]+trunk+[(99, 60)])]]}
    stations = []
    for group, (row, col) in enumerate([trunk[0], trunk[-1]]):
        lon, lat = coord(row, col)
        for name in ['A', 'B']:
            stations.append(dict(id=f'{name}-{group}', line=name, lon=lon,
                                 lat=lat, junction_group=group, mandatory_crossing=True))
    result = audit.check_design({'stations': stations}, features, grid,
                                np.zeros((100, 100), dtype=np.uint8))
    assert result['passed']
    assert result['dry_geometric_crossings'] == 2


def test_a_network_without_rings_still_requires_every_line_to_connect():
    grid=dict(bbox_north=1.,bbox_west=0.,m_per_deg_lat=1000,m_per_deg_lon=1000,cell_m=20)
    def coord(r,c):return [(c+.5)*.02,1-(r+.5)*.02]
    features={'features':[{'properties':{'name':name},'geometry':{'type':'LineString',
                         'coordinates':[coord(*p) for p in points]}}
                         for name,points in [('a',[(2,2),(8,2)]),('b',[(2,8),(8,8)])]]}
    result=audit.check_design({'stations':[]},features,grid,np.zeros((12,12),dtype=np.uint8))
    assert not result['passed'] and not result['connected_network']
    assert result['geometric_components']==[['a'],['b']]


def test_a_self_crossing_cannot_pass_as_a_connected_single_line():
    grid=dict(bbox_north=1.,bbox_west=0.,m_per_deg_lat=1000,m_per_deg_lon=1000,cell_m=20)
    def coord(r,c):return [(c+.5)*.02,1-(r+.5)*.02]
    features={'features':[{'properties':{'name':'a'},'geometry':{'type':'LineString',
                         'coordinates':[coord(*p) for p in [(2,2),(8,8),(2,8),(8,2)]]}}]}
    result=audit.check_design({'stations':[]},features,grid,np.zeros((12,12),dtype=np.uint8))
    assert result['connected_network'] and not result['passed']
    assert result['self_intersecting_lines']==['a']


@pytest.mark.parametrize('city',[
    'east-africa/Kenya/Garissa',
    'central-africa/DR Congo/Kisangani',
    'central-africa/DR Congo/Lubumbashi',
])
def test_reported_city_maps_have_one_connected_dry_platform_network(city):
    import gzip,json,tomllib
    folder=ROOT/'cities/catalogue'/city;design=tomllib.loads((folder/'design.toml').read_text())
    grid=json.loads((folder/'engineering/alignment/planning-grid.json').read_text())
    mask=np.frombuffer(gzip.decompress((folder/'engineering/alignment/planning-water-mask.bin.gz').read_bytes()),dtype=np.uint8).reshape(grid['height'],grid['width'])
    features=json.loads((folder/(design['city']['slug']+'.corridor.geojson')).read_text())
    report=audit.check_design(design,features,grid,mask)
    assert report['passed'],report
    assert len(report['transfer_components'])==1


def test_diagonal_crossing_matches_native_half_up_cell_without_extending_tolerance():
    grid=dict(bbox_north=1.,bbox_west=0.,m_per_deg_lat=1000,m_per_deg_lon=1000,cell_m=20)
    def coord(row,col):return [(col+.5)*.02,1-(row+.5)*.02]
    features={'features':[
        {'properties':{'name':name},'geometry':{'type':'LineString',
         'coordinates':[coord(*cell) for cell in cells]}}
        for name,cells in [('A',[(3,3),(4,4)]),('B',[(7,4),(4,3),(3,4)])]]}
    def station(name,row,col):
        lon,lat=coord(row,col)
        return dict(id=name,line=name,lon=lon,lat=lat,junction_group=0)
    mask=np.zeros((12,12),dtype=np.uint8)
    # The diagonal intersection rounds to native cell (4,4): three cells
    # is exactly 60 m. A fourth cell must still fail the same hard limit.
    result=audit.check_design({'stations':[station('A',4,4),station('B',7,4)]},features,grid,mask)
    assert result['passed']
    result=audit.check_design({'stations':[station('A',4,4),station('B',8,4)]},features,grid,mask)
    assert not result['passed'] and result['missing_crossing_platforms']
