"""Count actual spread rails; never inherit narrow civil or free terminal track."""
from copy import deepcopy
import pytest

from engineering.railway_project import alignment,bundle,station_tracks as tracks
from test_railway_project_alignment import corridor,PARAMETERS
from test_railway_project_bundle import inputs
from test_railway_project_bundle import civil_control
from test_railway_project_civil import seal


def controls(straight=425.):
    b,_=inputs()
    a=alignment.generate(corridor([[44.,33.],[44.,33.02],[44.,33.04]]),
        **dict(PARAMETERS,platform_straight_m=straight))
    s=bundle.stations(b,a,platform_width_m=3.,track_centres_y_m=[-3.,3.],
        nominal_boarding_gap_m=.075,stopping_tolerance_m=2.,boarding_length_m=125.)
    return a,s


def generate(a,s,**changes):
    return tracks.generate(a,s,**dict(dict(running_track_centres_y_m=[-1.6,1.6],transition_length_m=150.,
        lateral_sway_bound_m=.05,requested_speed_m_s=55/3.6,longitudinal_acceleration_bound_m_s2=1.,
        lateral_acceleration_target_m_s2=.5,lateral_jerk_target_m_s3=.3),**changes))


def test_septic_joins_have_no_offset_slope_curvature_or_curvature_rate_steps():
    assert tracks.transition(0.,150.,1.4)==(0.,0.,0.,0.)
    y,dy,ddy,dddy=tracks.transition(1.,150.,1.4)
    assert y==pytest.approx(1.4)
    assert (dy,ddy,dddy)==pytest.approx((0.,0.,0.))
    assert tracks.transition(.5,150.,1.4)[0]==pytest.approx(.7)


def test_station_spread_counts_each_transition_and_terminal_half_platform_once():
    a,s=controls();r=generate(a,s);q=r['quantities']
    assert q['transition_pairs']==4 and q['individual_track_transitions']==8
    assert q['terminal_extension_track_m']==250.
    assert q['station_plateau_track_m']==750.
    assert q['total_track_m']==pytest.approx(2*a['route_m']+250.+q['spread_additional_track_m'])
    assert q['spread_additional_track_m']>0
    assert q['total_rail_m']==2*q['total_track_m']
    assert r['numerical']['swept_inner_platform_clearance_m']==pytest.approx(.1)
    assert r['numerical']['swept_own_platform_clearance_m']==pytest.approx(.025)
    assert r['calculated_horizontal_screen_passed']
    assert not r['installed_station_complete'] and not r['physical_accepted']
    assert r['physical_definition']['turnback_definition_complete'] is False


def test_short_parent_straight_and_dynamic_platform_conflict_are_not_relabelled():
    a,s=controls(125.)
    with pytest.raises(ValueError,match='parent straight'):
        generate(a,s)
    a,s=controls()
    with pytest.raises(ValueError,match='swept train'):
        generate(a,s,lateral_sway_bound_m=.2)
    # Independent review found that positive inter-track clearance alone missed
    # each vehicle's own +Y platform. Preserve this 15 mm intrusion control.
    with pytest.raises(ValueError,match='swept train'):
        generate(a,s,lateral_sway_bound_m=.09)
    changed=deepcopy(s);changed['alignment_evaluation_id']='f'*64;seal(changed)
    with pytest.raises(ValueError,match='same-alignment'):
        generate(a,changed)


def test_speed_sway_and_evidence_are_evaluations_but_spread_length_changes_geometry():
    a,s=controls(525.)
    first=generate(a,s);slow=generate(a,s,requested_speed_m_s=10.)
    assert first['candidate_id']==slow['candidate_id']
    assert first['evaluation_id']!=slow['evaluation_id']
    longer=generate(a,s,transition_length_m=200.)
    assert longer['candidate_id']!=first['candidate_id']
    assert longer['numerical']['maximum_curvature_per_m']<first['numerical']['maximum_curvature_per_m']


def test_project_binds_spread_revision_without_inheriting_narrow_civil_capacity():
    b,_=inputs();a,s=controls();spread=generate(a,s)
    c=civil_control(b,a)
    c['physical_definition']['track_centres_y_m']=[-1.6,1.6]
    from engineering.station_rail.common import identity
    c['candidate_id']=identity(c['physical_definition']);seal(c)
    with pytest.raises(ValueError,match='explicit track spreading'):
        bundle.combine(b,a,c,s)
    project=bundle.combine(b,a,c,s,station_tracks=spread)
    assert project['physical_definition']['station_track_geometry_candidate_id']==spread['candidate_id']
    assert not project['widened_station_supports_verified']
    assert not project['terminal_routes_complete']
    assert not project['installed_station_complete']
    changed=deepcopy(spread);changed['station_evaluation_id']='f'*64;seal(changed)
    with pytest.raises(ValueError,match='different running civil'):
        bundle.combine(b,a,c,s,station_tracks=changed)
