import gzip
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('water_screen', ROOT/'tools/automation/generate-station-water-screen.py')
water = importlib.util.module_from_spec(spec)
spec.loader.exec_module(water)


def test_point_screen_keeps_actual_water_coverage_and_last_cell():
    grid = dict(height=2,width=2,cell_m=20,bbox_north=10,bbox_west=0,m_per_deg_lat=20,m_per_deg_lon=20)
    stations = [dict(id='dry',lat=9.5,lon=.5),dict(id='threshold',lat=9.5,lon=1.5),dict(id='last',lat=8.5,lon=1.5)]
    cells = water.platform_water_cells(stations,grid,bytes([49,50,0,100]))
    assert [r['water_coverage_percent'] for r in cells] == [49,50,100]
    assert [r['station_id'] for r in cells if r['water_coverage_percent']>=50] == ['threshold','last']
    assert (cells[-1]['row'],cells[-1]['col']) == (1,1)


def test_truncated_mask_and_outside_platform_are_rejected():
    grid = dict(height=1,width=1,cell_m=20,bbox_north=10,bbox_west=0,m_per_deg_lat=20,m_per_deg_lon=20)
    with pytest.raises(ValueError,match='match the controlled grid'):
        water.platform_water_cells([],grid,b'')
    with pytest.raises(ValueError,match='outside the controlled grid'):
        water.platform_water_cells([dict(id='outside',lat=8,lon=.5)],grid,b'\0')


def test_mask_snapshot_has_reproducible_header_and_preserves_all_cells():
    raw=bytes([0,100,50,0])*100
    first=water.packed_bytes(raw)
    assert first[9]==255
    assert first==water.packed_bytes(raw)
    assert gzip.decompress(first)==raw
