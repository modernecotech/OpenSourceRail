"""Newfamily necessary bounds and configuration isolation; nofull trial runs."""
from math import hypot
import pytest
from engineering.compact_drive import gears,kinematics
from engineering.compact_drive.common import policy,vendor,parent
from engineering.compact_drive.design import stock_volume


def test_exact_two_stage_ratios_and_real_shaft_distances():
    p=policy();assert len(p['configs'])==3
    for config,want in zip(p['configs'],(7.37,7.37,9.8)):
        g=gears.train(config);assert g['ratio']==pytest.approx(want)
        for (a,b),distance in zip((('input','middle'),('middle','output')),g['centre_distances_m']):
            assert hypot(g['axes'][a][0]-g['axes'][b][0],g['axes'][a][2]-g['axes'][b][2])==pytest.approx(distance)
        assert all(x['root_diameter_m']>x['bore_m'] for x in g['gears'])


def test_contact_frame_does_not_sink_axle_by_suspension_jounce():
    pose=dict(wheel_radius_m=.34,cant_rad=0.,yaw_rad=0.,frame_roll_rad=0.,primary_m=-.04,secondary_m=-.04,lateral_m=0.)
    T=kinematics.frame_tree(2.1,-1.05,pose,.1)
    assert kinematics.apply(T['wheelset'],[1.05,0.,.38])[2]==pytest.approx(.34)
    assert kinematics.apply(T['bogie'],[2.1,0.,.41])[2]==pytest.approx(.33)
    assert kinematics.apply(T['body'],[2.1,0.,1.1])[2]==pytest.approx(.98)


def test_gear_swing_has_fixed_output_axis_and_is_about_Y():
    pose=dict(wheel_radius_m=.38,cant_rad=0.,yaw_rad=0.,frame_roll_rad=0.,primary_m=0.,secondary_m=0.,lateral_m=0.)
    T=kinematics.frame_tree(2.1,-1.05,pose,.1,gear_pitch=.02)['gear']
    assert kinematics.apply(T,[1.05,.5,.38])==pytest.approx([1.05,.5,.38])
    assert kinematics.apply(T,[1.15,.5,.38])[2]<.38


def test_stock_voids_positive_bearing_bores_and_exact_vendor_version():
    assert stock_volume(dict(kind='rhs',length_m=1.,width_m=.2,depth_m=.3,wall_m=.01))==pytest.approx(.2*.3-.18*.28)
    v=vendor();assert v['catalogue']['peak_duration_s']==30 and v['catalogue']['continuous_torque_Nm']==205
    assert v['STEP']['private_only'] and not v['STEP']['model_B_datasheet_C_compatibility_verified']
    assert len(kinematics.poses(policy()))<=24


def test_parent_read_is_exact_historical_candidate_only():
    b=parent();assert b['candidate_id']=='9f6d223074b3438a546d5b3d71cd9b970807387ef0542023bed79bef46dbdeba'
