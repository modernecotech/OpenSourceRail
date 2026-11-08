"""Synthetic protocol controls; no native journey or geometry is evaluated."""
from copy import deepcopy

import pytest

from engineering.railway_project import alignment,bundle,frame,motion
from engineering.station_rail.common import identity
from test_railway_project_alignment import corridor,PARAMETERS
from test_railway_project_bundle import civil_control
from test_railway_project_civil import seal
from test_railway_project_motion import project,scenario
from test_railway_project_station_tracks import generate


def context(direction=1,leg_index=0):
    _,body,_,duty=project()
    a=alignment.generate(corridor([[44.,33.],[44.,33.02],[44.,33.04]]),
        **dict(PARAMETERS,platform_straight_m=425.))
    station=bundle.stations(body,a,platform_width_m=3.,track_centres_y_m=[-3.,3.],
        nominal_boarding_gap_m=.075,stopping_tolerance_m=2.,boarding_length_m=125.)
    tracks=generate(a,station);civil=civil_control(body,a)
    civil['physical_definition']['track_centres_y_m']=[-1.6,1.6]
    civil['candidate_id']=identity(civil['physical_definition']);seal(civil)
    p=bundle.combine(body,a,civil,station,station_tracks=tracks)
    s=scenario();s['emergency_at_m']=100.
    q,m=motion.compile_case(p,body,a,duty,leg_index,s,direction=direction)
    geometry=dict(project_candidate_id=p['candidate_id'],body_candidate_id=body['candidate_id'],
        body_evaluation_id=body['evaluation_id'],alignment_candidate_id=a['candidate_id'],
        alignment_evaluation_id=a['evaluation_id'],station_candidate_id=station['candidate_id'],
        station_evaluation_id=station['evaluation_id'],station_track_candidate_id=tracks['candidate_id'],
        station_track_evaluation_id=tracks['evaluation_id'],drive_duty_evaluation_id=duty['evaluation_id'])
    def coverage(kind):
        return seal(dict(schema=frame.COVERAGE_SCHEMA,kind=kind,geometry_binding=geometry,
            train_reference='formation-geometric-centre',physical_route_distance_m=q['distance_m'],
            leg_index=leg_index,direction=direction,reference_interval_m=[-2.,q['distance_m']],
            coverage_maturity='declared-research-domain',basis='Synthetic protocol declaration only; no actual finite-train or power capability.',
            limitations=['No real geometry or available-feed evidence supplied by this fixture.'],source_sha256={},**frame.FLAGS))
    return q,m,p,body,a,station,tracks,duty,coverage('operating-envelope'),coverage('continuous-feed')


def compile(args,**kw):
    return frame.compile_frame(*args,**dict(dict(origin_route_m=-2.,allowed_initial_route_interval_m=[-1.,1.]),**kw))


def test_frame_changes_coordinates_and_evaluation_not_train_distance_or_authority():
    args=context();before=deepcopy(args);q,m,f,b=compile(args)
    source=args[0];D=source['distance_m']
    assert args==before  # producer retains original physical request and records
    assert q['candidate_id']==source['candidate_id']==args[2]['candidate_id']
    assert f['physical_route_distance_m']==f['physical_target_route_m']==f['physical_authority_route_m']==D
    assert q['distance_m']==q['control']['end_of_authority_m']==D+2
    assert q['brake_start_m']==source['brake_start_m']+2
    assert q['fault']['emergency_at_m']==102.
    assert q['drive']['windows_m']==[[0.,D+2]]
    assert q['mass_kg']==source['mass_kg'] and q['thermal']==source['thermal']
    assert q['id']==identity({k:v for k,v in q.items() if k!='id'})!=source['id']
    assert b['compiled_case_id']==q['id'] and b['compiled_policy_id']==q['control']['policy_id']
    assert b['source_case_id']==source['id'] and b['source_policy_id']==source['control']['policy_id']
    assert f['context_id']==identity({k:v for k,v in f.items() if k!='context_id'})
    assert m['native_input_id']==identity(q) and m['source_input_evaluation_id']==args[1]['evaluation_id']
    assert not m['authority_extended'] and not m['physical_candidate_changed']
    assert not m['coverage_geometry_verified'] and not m['physical_accepted']


@pytest.mark.parametrize('direction,leg_index',[(1,0),(-1,0),(1,1),(-1,1)])
def test_station_order_and_physical_orientation_are_preserved(direction,leg_index):
    args=context(direction,leg_index);q,m,f,_=compile(args)
    assert (m['from_stop'],m['to_stop'])==(args[1]['from_stop'],args[1]['to_stop'])
    assert q['grade_fraction']==args[0]['grade_fraction']
    assert f['station_track_reference_domain_m'][0]<=-2
    assert f['station_track_reference_domain_m'][1]>=args[0]['distance_m']
    # Actual -0.5m route offset maps to+1.5m, without clipping or moving the train.
    assert -.5-f['origin_route_m']==1.5


def test_insufficient_negative_entry_or_coverage_refuses_instead_of_clipping():
    args=context()
    with pytest.raises(ValueError,match='biased observation'):
        compile(args,origin_route_m=-1.25)
    changed=list(deepcopy(args));changed[-1]['reference_interval_m'][0]=0.;seal(changed[-1])
    with pytest.raises(ValueError,match='Coverage omits'):
        compile(changed)
    with pytest.raises(ValueError,match='berth tolerance'):
        compile(args,allowed_initial_route_interval_m=[-1.1,1.])


def test_new_controller_policy_is_explicit_and_target_is_not_extra_authority():
    args=context();spec=dict(strategy='held-docking-speed-governor/2',brake_floor_n=10000.,creep_speed_m_s=.2)
    q,m,f,b=compile(args,controller_v2=spec)
    assert q['control']['research_v2']['berth_target_m']==q['control']['end_of_authority_m']
    assert q['control']['policy_id']!=args[0]['control']['policy_id']
    assert 'research_v2' not in args[0]['control'] and 'berth_target_m' not in spec
    with pytest.raises(ValueError,match='controller floor'):
        compile(args,controller_v2=dict(spec,creep_speed_m_s=.5))


def test_resealed_mixed_coverage_ancestry_and_stale_source_do_not_export():
    args=list(context());args[-1]['geometry_binding']=dict(args[-1]['geometry_binding'],body_evaluation_id='f'*64);seal(args[-1])
    with pytest.raises(ValueError,match='separately declared'):
        compile(args)
    args=list(context());args[1]['native_method_sha256']={};seal(args[1])
    with pytest.raises(ValueError,match='source epoch'):
        compile(args)
    args=list(context());args[1]['case_id']='f'*64;seal(args[1])
    with pytest.raises(ValueError,match='canonical unframed'):
        compile(args)
