"""Newfamily necessary bounds and configuration isolation; nofull trial runs."""
from math import hypot
import pytest
from engineering.compact_drive import gears,kinematics
from engineering.compact_drive.common import policy,vendor,parent
from engineering.compact_drive.design import stock_volume,build,SUPPORT_FAMILY,SUPPORT_VARIANTS
from engineering.compact_drive.evaluate import evaluate
from engineering.station_rail.common import identity
import gzip,json
from pathlib import Path


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


def test_historical_three_compact_drive_geometries_are_unchanged():
    packet=Path('docs/design-engine/v06-design-closure/compact-drive-geometry-closure')
    expected={
        'compact-737-h100':'75075df9247dfff7082a78eadc273d3a99f37e5486450621536c43b1bfa2f797',
        'compact-737-h150':'5a3a6cd74fd33ab6d85e0a264afc899a5fff319e16e7fd94189637a6bfba44f3',
        'compact-980-h150':'9af20e27cdb4f53568ad1408efd082b61ee56ecdad89a0fb4ccebd7dcb6024dc',
    }
    for config,candidate in expected.items():
        reproduced=build(config_id=config)
        sealed=json.loads(gzip.open(packet/config/'body.json.gz','rb').read())
        assert reproduced['candidate_id']==candidate==sealed['candidate_id']
        assert reproduced['physical_definition']==sealed['physical_definition']
        assert identity(reproduced['physical_definition'])==candidate


def test_split_lane_support_family_has_distinct_candidates_and_reports_all_screens():
    a=build(config_id='compact-737-h100',support_family='offset-380mm')
    b=build(config_id='compact-737-h100',support_family='offset-420mm')
    parent_id='9f6d223074b3438a546d5b3d71cd9b970807387ef0542023bed79bef46dbdeba'
    assert a['parent_candidate_id']==b['parent_candidate_id']==parent_id
    assert a['candidate_id']!=b['candidate_id'] and a['candidate_id']!=parent_id and b['candidate_id']!=parent_id
    assert a['physical_definition']['support_package']['family']==SUPPORT_FAMILY
    assert a['physical_definition']['support_package']['variant']!=b['physical_definition']['support_package']['variant']
    assert a['physical_definition']['support_package']['variables']==SUPPORT_VARIANTS['offset-380mm']

    def support_mass(body):
        ids={r['id'] for r in body['parts'] if r['id'].startswith('compact-drive/pedestal-') or r['id'] in ('compact-drive/emergency-cap','compact-drive/emergency-riser')}
        return {case:sum(p['mass_kg'][case] for p in body['patterns'] if p['part_id'] in ids) for case in ('low','base','high')}
    legacy=build(config_id='compact-737-h100')
    assert support_mass(a)==pytest.approx(support_mass(legacy),rel=1e-12)
    assert a['installed_mass_complete'] is False
    report=evaluate(a)
    screen=report['support_package_screen']
    assert screen['candidate_id']==a['candidate_id']
    assert screen['all_12_bogies_screened'] is True
    assert screen['support_occurrences']>0 and screen['support_nominal_clearance_rows']>=0
    assert set(screen['screens'])=={'candidate_identity','support_occurrence_accounting','nominal_support_clearance','continuous_support_envelope','sampled_support_ground','support_load_path_and_joint_strength','support_stiffness_fatigue_and_retention','supplier_and_finished_geometry','finite_removal_and_service','physical_acceptance'}
    assert all(v in ('PASS','HOLD','PASS_WITHIN_DECLARED_GROSS_STOCK_SCREEN','PASS_WITHIN_DECLARED_CONTINUOUS_BOUND','PASS_WITHIN_SAMPLED_POSES') for v in screen['screens'].values())
    assert screen['screens']['support_load_path_and_joint_strength']=='HOLD'
    assert screen['screens']['support_stiffness_fatigue_and_retention']=='HOLD'
    assert screen['screens']['physical_acceptance']=='HOLD'
