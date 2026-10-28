"""Actual material projection, span statics and primary-deadload regressions."""
from copy import deepcopy
from math import pi
import pytest

from engineering.station_rail import civil
from engineering.station_rail.common import identity
from engineering.railway_completion import infrastructure as i


def box(name,a,b,mass,system='civil/concrete'):
    p=dict(id=name,kind='box',at_m=[a,0.,0.],size_m=[b-a,1.,1.],volume_m3=b-a,mass_kg=mass,
        density_kg_m3=mass/(b-a),material='fixture')
    return dict(id=name,geometry=p,translation_m=[0.,0.,0.],mass_kg=mass,system=system,
        component_definition_id=identity(p),scope='nominal-stock')


def context(start=-120.,end=40.,rows=None):
    bundle=dict(schema='osr-infrastructure-method-test/1',candidate_id=identity('candidate'),definition_id=identity('definition'),
        mass=dict(accounted_tare_kg_per_car=1000.,accounted_cap_loaded_kg_per_car=2000.,accounted_160_control_kg_per_car=3000.),
        physical_definition=dict(vehicle=dict(cars=6,body_length_m=17.,coupling_gap_m=.5),
            support=dict(bogie_centres_x_m=[-6.4,6.4],bogie_wheelbase_m=2.1)),
        architecture_case=dict(physical_definition=dict(route=dict(counted_guideway_start_m=start,counted_guideway_end_m=end),guideway=dict(span_m=20.))))
    scene=dict(schema='osr-railway-twin-scene/1',candidate_id=bundle['candidate_id'],complete_installed_geometry=False,
        occurrences=rows or [box('beam',start,end,1000.),box('bank',-13.,7.,200.,'wayside/primary')])
    return scene,bundle


def test_bank_crosses_negative_berth_span_and_enters_both_support_reactions():
    scene,bundle=context();r=i.derive(scene,bundle)
    assert r['known_wayside_stock_weight_N']==pytest.approx(200*civil.G)
    bank=[row for row in r['source_line_loads'] if row['source_occurrence_id']=='bank'][0]
    assert [bank['a_m'],bank['b_m']]==[-13.,7.]
    without=deepcopy(scene);without['occurrences']=without['occurrences'][:1]
    control=i.derive(without,bundle)
    changes=[a['known_dead_reaction_N']-b['known_dead_reaction_N'] for a,b in zip(r['supports'],control['supports'])]
    assert sum(changes)==pytest.approx(200*civil.G)
    assert changes[5]>0 and changes[6]>0 and changes[7]>0
    assert changes[6]>changes[5] and changes[6]>changes[7]
    assert abs(r['force_residual_N'])<1e-8 and abs(r['first_moment_residual_Nm'])<1e-6
    assert r['complete_installed_dead_load_N'] is None


def test_full_uniform_span_reproduces_closed_form_force_and_moment():
    scene,bundle=context(0.,20.,[box('uniform',0.,20.,100.)]);r=i.derive(scene,bundle)
    span=r['spans'][0];P=100*civil.G
    assert span['left_reaction_N']==pytest.approx(P/2)
    assert span['right_reaction_N']==pytest.approx(P/2)
    assert span['peak_dead_moment_Nm']==pytest.approx(P*20/8)
    assert span['peak_dead_moment_chainage_m']==pytest.approx(10.)
    assert abs(span['force_residual_N'])<1e-9 and abs(span['moment_residual_Nm'])<1e-9


def test_vehicle_mass_is_not_added_as_dead_stock_and_live_load_remains_separate():
    scene,bundle=context();control=i.derive(scene,bundle)
    scene['occurrences'].append(box('train',-100.,0.,1000000.,'vehicle/body'))
    r=i.derive(scene,bundle)
    assert r['known_dead_weight_N']==control['known_dead_weight_N']
    assert r['dead_stock_occurrences']==2
    assert r['live_axle_loads']['dynamic_factor_hypothesis']==1.3
    assert all(p['conditional_crowd_train_reaction_N']>0 for p in r['supports'])
    assert all(p['complete_installed_design_reaction_N'] is None for p in r['supports'])


def test_transverse_hollow_cylinder_uses_circular_material_slices_not_uniform_envelope():
    mass=100.;volume=pi*(2**2-1**2)
    part=dict(id='pipe',kind='annular-cylinder',at_m=[0.,0.,0.],axis=[0.,1.,0.],length_m=1.,radius_m=2.,inner_radius_m=1.,
        volume_m3=volume,mass_kg=mass,density_kg_m3=mass/volume,material='fixture')
    row=dict(id='pipe',geometry=part,translation_m=[0.,0.,0.],mass_kg=mass,system='wayside/primary',
        component_definition_id=identity(part),scope='nominal-stock')
    scene,bundle=context(-20.,20.,[row]);r=i.derive(scene,bundle)
    assert [x['kind'] for x in r['source_line_loads']]==['disk','disk']
    assert r['spans'][0]['known_dead_force_N']==pytest.approx(mass*civil.G/2)
    assert r['spans'][1]['known_dead_force_N']==pytest.approx(mass*civil.G/2)
    assert abs(r['force_residual_N'])<1e-9 and abs(r['first_moment_residual_Nm'])<1e-8
    assert not r['unsupported_projection_hypotheses']


def test_oblique_tube_centroid_lumping_is_explicit_and_point_at_joint_is_counted_once():
    part=dict(id='diagonal',kind='oriented-RHS',start_m=[-1.,0.,0.],end_m=[1.,1.,0.],width_m=.1,height_m=.2,wall_m=.01,
        volume_m3=(5**.5)*(.1*.2-.08*.18),mass_kg=10.,material='fixture')
    row=dict(id='diagonal',geometry=part,translation_m=[0.,0.,0.],mass_kg=10.,system='wayside/structure',
        component_definition_id=identity(part),scope='nominal-stock')
    scene,bundle=context(-20.,20.,[row]);r=i.derive(scene,bundle)
    assert len(r['unsupported_projection_hypotheses'])==1
    assert r['known_dead_weight_N']==pytest.approx(10*civil.G)
    assert sum(p['known_dead_reaction_N'] for p in r['supports'])==pytest.approx(10*civil.G)
    assert r['supports'][1]['known_dead_reaction_N']==pytest.approx(10*civil.G)
    assert abs(r['force_residual_N'])<1e-8


def test_named_unlocated_accounts_keep_bounds_and_unknown_mass_stays_unknown():
    scene,bundle=context();ledger=dict(candidate_id=bundle['candidate_id'],unlocated_accounts=[
        dict(id='span/0/reinforcement_kg',system='civil/unlocated-stock',accounted_mass_kg=100.),
        dict(id='infrastructure/power-room',system='wayside/installation',accounted_mass_kg=None),
        dict(id='infrastructure/pier',system='civil/installation',accounted_mass_kg=50.),
        dict(id='car/0/bogie-residual',system='vehicle/bogies',accounted_mass_kg=200.)])
    control=i.derive(scene,bundle);r=i.derive(scene,bundle,ledger)
    assert r['known_dead_weight_N']-control['known_dead_weight_N']==pytest.approx(100*civil.G)
    a=r['named_span_account_assumptions'][0]
    assert a['actual_centroid_m'] is None and a['assumed_centroid_m']==-110.
    assert a['reaction_each_support_bounds_N']==pytest.approx([0.,100*civil.G])
    assert a['first_moment_bounds_Nm']==pytest.approx([-120*100*civil.G,-100*100*civil.G])
    assert r['unweighed_occurrence_ids']==['infrastructure/power-room']
    assert r['unassigned_known_weight_N']==pytest.approx(50*civil.G)
    assert control['unweighed_occurrence_ids'] is None and control['unassigned_known_weight_N'] is None


def test_outside_coverage_stock_is_retained_and_does_not_vanish_from_force_budget():
    scene,bundle=context(0.,20.,[box('crossing',-10.,10.,200.)]);r=i.derive(scene,bundle)
    assert r['outside_counted_guideway_weight_N']==pytest.approx(100*civil.G)
    assert sum(p['known_dead_reaction_N'] for p in r['supports'])==pytest.approx(100*civil.G)
    assert abs(r['force_residual_N'])<1e-8 and abs(r['first_moment_residual_Nm'])<1e-8


def test_mixed_candidates_and_inconsistent_source_mass_or_span_reject():
    scene,bundle=context();bad=deepcopy(scene);bad['candidate_id']='a'*64
    with pytest.raises(ValueError,match='mix'):i.derive(bad,bundle)
    bad=deepcopy(scene);bad['occurrences'][0]['mass_kg']=1.
    with pytest.raises(ValueError,match='mass'):i.derive(bad,bundle)
    bad=deepcopy(bundle);bad['architecture_case']['physical_definition']['guideway']['span_m']=25.
    with pytest.raises(ValueError,match='20m'):i.derive(scene,bad)


def test_unlocated_account_cannot_be_duplicated_or_bound_to_another_scene():
    scene,bundle=context();row=dict(id='span/0/account',system='civil/unlocated-stock',accounted_mass_kg=10.)
    ledger=dict(candidate_id=bundle['candidate_id'],unlocated_accounts=[row,row])
    with pytest.raises(ValueError,match='unique'):i.derive(scene,bundle,ledger)
    ledger['unlocated_accounts']=[row];ledger['scene_id']='a'*64
    with pytest.raises(ValueError,match='another scene'):i.derive(scene,bundle,ledger)
