import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('ring_repair',ROOT/'tools/automation/rework-baghdad-alignment.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def test_one_cell_closed_ring_spur_is_removed_without_creating_an_edge():
    route=[[0,0],[0,1],[0,2],[0,1],[1,1],[1,0],[0,0]]
    repaired,records=module.remove_short_ring_spikes(route,20)
    assert repaired==[[0,0],[0,1],[1,1],[1,0],[0,0]]
    original={tuple(map(tuple,pair)) for pair in zip(route,route[1:])}
    assert all(tuple(map(tuple,pair)) in original for pair in zip(repaired,repaired[1:]))
    assert records[0]['removed_route_m']==40


def test_radial_long_and_protected_spurs_are_retained_for_review():
    open_route=[[0,0],[0,1],[0,0],[2,0]]
    assert module.remove_short_ring_spikes(open_route,20)[0]==open_route
    long=[[0,0],[0,1],[0,5],[0,1],[1,1],[1,0],[0,0]]
    assert module.remove_short_ring_spikes(long,20)[0]==long
    short=[[0,0],[0,1],[0,2],[0,1],[1,1],[1,0],[0,0]]
    assert module.remove_short_ring_spikes(short,20,protected_cells=[[0,2]])[0]==short
