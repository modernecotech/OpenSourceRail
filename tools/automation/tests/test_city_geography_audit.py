"""Independent geometry checks must reject nearby stops and wet platforms."""
import importlib.util
from pathlib import Path

import numpy as np

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
