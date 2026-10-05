import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('water_routes',ROOT/'tools/automation/water-route-constraints.py')
routes=importlib.util.module_from_spec(spec);spec.loader.exec_module(routes)


def test_sparse_straight_routes_are_checked_between_their_endpoints():
    mask=np.zeros((100,100),dtype=np.uint8);mask[20:80,20:80]=100
    cells=[[50,0],[50,99]]
    _,runs=routes.water_runs(cells,mask,20)
    assert runs[0]['length_m']==pytest.approx(1200)
    repaired,changes=routes.repair(cells,mask,20,maximum_unapproved_crossing_m=1000)
    assert changes and repaired[0]==cells[0] and repaired[-1]==cells[-1]
    _,after=routes.water_runs(repaired,mask,20)
    assert all(run['length_m']<=1000 for run in after)


def test_dry_geometry_and_short_priced_bridge_candidates_are_retained():
    cells=[[0,0],[0,19]];mask=np.zeros((20,20),dtype=np.uint8)
    mask[:,8:10]=100
    assert routes.repair(cells,mask,20)==(cells,[])


def test_unknown_coverage_is_excluded_and_unapproved_water_endpoints_fail():
    mask=np.zeros((20,20),dtype=np.uint8);mask[5,5]=255
    repaired,changes=routes.repair([[5,0],[5,19]],mask,20)
    assert changes and all(mask[tuple(cell)]!=255 for cell in repaired)
    mask[:,:12]=100
    with pytest.raises(ValueError,match='water tail'):
        routes.repair([[0,0],[0,19]],mask,100)


def test_crossing_budget_finds_a_short_bridge_instead_of_a_long_channel_crossing():
    mask=np.zeros((80,80),dtype=np.uint8);mask[:,30:50]=100
    mask[10:15,32:50]=0
    path,_=routes.detour((40,0),(40,79),mask,np.zeros_like(mask,dtype=bool),
                        cell_m=10,maximum_water_run_m=50)
    _,runs=routes.water_runs(path,mask,10)
    assert runs and all(run['length_m']<=50 for run in runs)
    assert path[0]==(40,0) and path[-1]==(40,79)


def test_long_coastal_tail_relocates_to_its_connected_shore_with_a_recorded_bound():
    mask=np.zeros((100,100),dtype=np.uint8);mask[:70,:30]=100
    original=[[20,20],[20,29],[80,29],[80,99]]
    repaired,changes=routes.repair(original,mask,20,maximum_endpoint_trim_m=600,
                                 maximum_endpoint_relocation_m=600)
    assert changes[0]['kind']=='bounded-endpoint-relocation-with-shore-route'
    assert changes[0]['endpoint_shift_m']<=600
    assert repaired[-1]==original[-1]
    assert mask[tuple(repaired[0])]==0
    _,runs=routes.water_runs(repaired,mask,20)
    assert not runs


def test_explicit_offshore_tail_scope_records_actual_removal_and_enforces_bound():
    mask=np.zeros((10,100),dtype=np.uint8);mask[:,30:90]=100
    original=[[5,0],[5,99]]
    retained,change=routes.crop_terminal_at_long_water(original,mask,20,False,1500)
    assert retained[0]==original[0] and retained[-1]==[5,29]
    assert change['removed_original_route_m']==pytest.approx(1400)
    with pytest.raises(ValueError,match='bound'):
        routes.crop_terminal_at_long_water(original,mask,20,False,1000)


def test_compiled_fallback_still_obeys_crossing_and_forbidden_corner_limits():
    mask=np.zeros((80,80),dtype=np.uint8);mask[:,30:50]=100
    mask[10:15,32:50]=0
    blocked=np.zeros_like(mask,dtype=bool)
    path,_=routes.detour((40,0),(40,79),mask,blocked,maximum_expansions=1,
                        cell_m=10,maximum_water_run_m=50)
    _,runs=routes.water_runs(path,mask,10)
    assert all(run['length_m']<=50 for run in runs)
    mask[:,:]=100;mask[:,0]=0;mask[:,-1]=0
    with pytest.raises(ValueError,match='unapproved crossing'):
        routes.detour((40,0),(40,79),mask,blocked,maximum_expansions=1,
                      cell_m=10,maximum_water_run_m=50)
