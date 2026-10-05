"""Infill follows actual corridor geometry and refuses wet planning platforms."""
import importlib.util
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('station_infill',ROOT/'tools/automation/apply-city-station-infill.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def fixture():
    stations=[dict(id='a',line='line-1',s_m=0,platform_length_m=59.5),dict(id='b',line='line-1',s_m=5000,platform_length_m=59.5)]
    lines=[dict(name='line-1',length_m=5000)]
    geometry={'line-1':[[0,0],[4,0],[4,6]]}
    grid=dict(width=12,height=12,m_per_deg_lon=1,m_per_deg_lat=1,bbox_north=10,bbox_west=0,cell_m=1)
    return stations,lines,geometry,grid,bytearray(144)

def test_infill_follows_the_bent_corridor_and_preserves_original_stations():
    args=fixture();original=list(args[0]);new=module.infill(*args,1500,1200)
    assert args[0]==original and len(new)==3
    assert [s['s_m'] for s in new]==[1250,2500,3750]
    assert (new[0]['lon'],new[0]['lat'])==(2.5,0)
    assert (new[1]['lon'],new[1]['lat'])==(4,1)
    assert all(s['anchor_kind']=='planning:infill' for s in new)

def test_infill_does_not_invent_a_dry_site_for_a_wet_point():
    args=fixture();args[-1][10*12+2]=100
    with pytest.raises(ValueError,match='dry in-grid'):module.infill(*args,1500,1200)

def test_spacing_cannot_be_packed_below_the_controlled_minimum():
    args=fixture();args[0][-1]['s_m']=1800
    with pytest.raises(ValueError,match='No compliant'):module.infill(*args,1500,1200)

def test_nearby_cross_line_platforms_get_a_transfer_without_moving_them():
    platforms=[dict(id='a',line='line-1',lat=0,lon=0,s_m=0,archetype='standard'),dict(id='b',line='line-2',lat=0,lon=.004,s_m=1000,archetype='standard'),dict(id='c',line='line-3',lat=0,lon=.02,s_m=0,archetype='standard')]
    civil=[dict(line='line-1',from_station_m=0,to_station_m=2000,**{'class':'elevated'})]
    current,groups=module.transfer_groups(platforms,[],civil)
    assert len(groups)==1 and groups[0]['platforms']==['a','b']
    assert [(s['lat'],s['lon'],s['s_m']) for s in current]==[(s['lat'],s['lon'],s['s_m']) for s in platforms]
    assert current[0]['junction_group']==current[1]['junction_group']
    assert current[0]['archetype']==current[1]['archetype']=='interchange-elevated'
    assert 'junction_group' not in current[2]
    assert module.transfer_groups(current,groups,civil)==(current,groups)

def test_transfer_group_preserves_radial_terminal_and_depot_roles():
    platforms=[dict(id='a',line='line-1',lat=0,lon=0,s_m=0,archetype='terminal'),dict(id='b',line='line-1',lat=0,lon=.004,s_m=2000,archetype='interchange-elevated'),dict(id='c',line='line-2',lat=0,lon=.006,s_m=2000,archetype='depot-terminal')]
    lines=[dict(name='line-1',shape='radial'),dict(name='line-2',shape='radial')]
    current,groups=module.transfer_groups(platforms,[],[],lines)
    assert current[1]['archetype']=='terminal' and current[2]['archetype']=='depot-terminal'
    assert current[1]['junction_group']==current[2]['junction_group']
