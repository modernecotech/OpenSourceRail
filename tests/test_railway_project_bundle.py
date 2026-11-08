"""Same-revision binding and physically consistent one-sided boarding interfaces."""
from copy import deepcopy
import pytest

from engineering.railway_project import alignment,bundle,civil
from engineering.station_rail.common import identity
from test_railway_project_alignment import corridor,PARAMETERS
from test_railway_project_civil import body,seal


def inputs():
    b=body();b['layout_definition_complete']=False;b['compact_drive_contract']['body_lift_m']=.1
    b['policy']['layout']=dict(cars=6,car_length_m=17.,intercar_gap_m=.65,car_width_m=2.65,
        door_centres_local_x_m=[-4.5,4.5],door_clear_width_m=1.4,floor_top_m=1.2)
    seal(b)
    a=alignment.generate(corridor([[44.,33.],[44.,33.02],[44.,33.04]]),**PARAMETERS)
    return b,a


def station(b,a,**changes):
    return bundle.stations(b,a,**dict(dict(platform_width_m=3.,track_centres_y_m=[-3.,3.],
        nominal_boarding_gap_m=.075,stopping_tolerance_m=2.),**changes))


def civil_control(b,a):
    # Isolated binding control, not an evaluated bridge or physical evidence.
    track={k:v for k,v in b['policy']['track_interface'].items() if k not in ('schema','real_profile_verified')}
    p=dict(span_geometry=dict(track_interface=track),track_centres_y_m=[-3.,3.])
    return seal(dict(schema='osr-project-civil-evaluation/1',candidate_id=identity(p),physical_definition=p,
        vehicle_candidate_id=b['candidate_id'],body_evaluation_id=b['evaluation_id'],alignment_candidate_id=a['candidate_id'],
        alignment_evaluation_id=a['evaluation_id'],cost=dict(base_usd=100.),source_sha256={},**civil.FLAGS))


def test_same_physical_door_side_is_preserved_after_travel_direction_reversal():
    b,a=inputs();s=station(b,a)
    assert s['quantities']['stations']==3 and s['quantities']['boarding_faces']==6
    assert s['quantities']['door_landing_interfaces']==72
    assert s['quantities']['beyond_terminal_centre_main_track_m']==250.
    first=s['physical_definition']['stations'][0]['boarding_faces']
    assert all(f['boarding_side_body_y']=='+Y' for f in first)
    assert first[0]['platform_polygon_local_xy_m'][0][1]==pytest.approx(-1.6)
    assert first[1]['platform_polygon_local_xy_m'][0][1]==pytest.approx(4.4)
    assert all(f['nominal_platform_top_above_rail_m']==pytest.approx(1.2) for f in first)
    assert s['installed_station_assembly_complete'] is False


def test_tight_running_track_centres_cannot_silently_fit_an_inner_boarding_platform():
    b,a=inputs()
    with pytest.raises(ValueError,match='conflicts'):
        station(b,a,track_centres_y_m=[-1.6,1.6])
    with pytest.raises(ValueError,match='fit declared'):
        station(b,a,stopping_tolerance_m=20.)


def test_cost_or_hypothesis_change_is_not_new_physical_project():
    b,a=inputs();s=station(b,a);c=civil_control(b,a)
    first=bundle.combine(b,a,c,s)
    changed=deepcopy(c);changed['cost']['base_usd']=200.;seal(changed)
    second=bundle.combine(b,a,changed,s)
    assert first['candidate_id']==second['candidate_id']
    assert first['evaluation_id']!=second['evaluation_id']
    assert first['complete_project_costed'] is False and first['force_driven_project_replayed'] is False
    assert first['installed_vehicle_complete'] is False


def test_changed_mass_revision_or_gauge_refuses_old_component_evidence():
    b,a=inputs();s=station(b,a);c=civil_control(b,a)
    revised=deepcopy(b);revised['mass_scenarios'][0]['train_mass_kg']+=1.;seal(revised)
    with pytest.raises(ValueError,match='different body or mass'):
        bundle.combine(revised,a,c,s)
    changed=deepcopy(c);changed['physical_definition']['span_geometry']['track_interface']['inner_face_gauge_m']=1.
    changed['candidate_id']=identity(changed['physical_definition']);seal(changed)
    with pytest.raises(ValueError,match='rail datums'):
        bundle.combine(b,a,changed,s)
