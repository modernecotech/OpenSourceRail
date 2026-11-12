import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('civil_moving_load',Path(__file__).parents[1]/'engineering/design_search/craft_backends/civil_moving_load.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def test_single_axle_exact_midspan_and_reactions():
    r=m.response(20.,10.,10.,[0.],1000.)
    assert r['moment_Nm']==5000 and r['left_N']==r['right_N']==500
    e=m.envelope(20.,[0.],1000.,[],.5)
    assert e['max_moment']['moment_Nm']==5000
    assert e['max_left_reaction_N']==e['max_right_reaction_N']==1000
    assert e['maximum_balance_residual_N']==0


def test_uniform_dead_load_and_virtual_work_converge():
    dead=[dict(a_m=0.,b_m=20.,q_N_m=1000.)]
    assert m.dead_response(20.,10.,dead)==(10000.,10000.,50000.)
    EI=1e9
    exact=5*1000*20**4/(384*EI)
    coarse=m.midpoint_deflection(20.,[],1000.,dead,0.,EI,.5)
    fine=m.midpoint_deflection(20.,[],1000.,dead,0.,EI,.25)
    assert abs(fine-exact)<abs(coarse-exact)
    assert fine==pytest.approx(exact,rel=.001)


def test_axle_locations_use_actual_formation_and_bogies():
    v={'physical_definition':dict(vehicle=dict(cars=6,body_length_m=17.,coupling_gap_m=.5),
        support=dict(bogie_centres_x_m=[-6.4,6.4],bogie_wheelbase_m=2.1))}
    x=m.axle_positions(v)
    assert len(x)==24 and x[:4]==pytest.approx([1.05,3.15,13.85,15.95])
    assert x[-1]==pytest.approx(103.45)


def test_crane_refuses_missing_radius_and_generic_capacity():
    inputs=dict(installed_lift_mass_kg=5000.,rigging_mass_kg=200.,radius_m=None,
        hoist_factor=1.1,chart=[dict(radius_m=10.,configuration='A',capacity_kg=6000.)],configuration='A')
    assert m.crane_at_radius(**inputs)['execution']=='held'
    inputs['radius_m']=12.
    with pytest.raises(ValueError,match='Exact radius'):m.crane_at_radius(**inputs)
    inputs['radius_m']=10.
    r=m.crane_at_radius(**inputs)
    assert r['required_capacity_kg']==pytest.approx(5720.) and r['capacity_screen_pass'] is True
    assert r['physical_accepted'] is False


def test_bad_load_and_unbounded_grid_rejected():
    with pytest.raises(ValueError):m.response(20.,10.,0.,[0.],float('nan'))
    with pytest.raises(ValueError):m.envelope(20.,[0.],1000.,[],.00001)
