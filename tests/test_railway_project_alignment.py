"""Analytical straight control, curve continuity and mapped corridor revision."""
from copy import deepcopy
from math import hypot

import pytest

from engineering.railway_project import alignment, route
from engineering.station_rail.common import identity
from engineering.outline import city_inputs


PARAMETERS = dict(platform_straight_m=125.,train_length_m=105.25,platform_end_margin_m=5.,
    requested_speed_m_s=55/3.6,lateral_acceleration_target_m_s2=.5,
    lateral_jerk_target_m_s3=.3,longitudinal_acceleration_bound_m_s2=1.,maximum_deviation_m=50.)


def corridor(coordinates):
    stations=[dict(id='s'+str(i),longitude=p[0],latitude=p[1],chainage_m=i*1000.) for i,p in enumerate(coordinates)]
    physical=dict(coordinates=coordinates,stations=stations)
    value=dict(schema='osr-mapped-corridor-input/1',definition=physical,corridor_geometry_id=identity(physical),
        source_sha256={},legs=[dict(distance_m=1000.) for _ in coordinates[1:]],route_m=1000.*(len(coordinates)-1))
    value['evaluation_id']=identity(value)
    return value


def test_analytical_straight_and_c2_station_joins():
    c=corridor([[44.,33.],[44.,33.02],[44.,33.04]])
    value=alignment.generate(c,**PARAMETERS)
    expected=alignment.R*__import__('math').radians(.04)
    assert value['route_m']==pytest.approx(expected,abs=1e-7)
    assert value['numerical']['maximum_sampled_curvature_per_m']<1e-14
    assert value['calculated_alignment_screen_passed']
    for piece in value['physical_definition']['pieces']:
        for at in (0.,1.):
            point,first,second,third=alignment.bezier(piece['control_points_xy_m'],at)
            assert hypot(*second)<1e-9
            assert first[1]>0
    assert value['physical_accepted'] is False


def test_real_baghdad_stair_steps_become_station_straights_without_losing_stops():
    city=city_inputs.load('baghdad');line=city['lines'][0]
    c=route.from_catalogue('baghdad',line['line_id'],line['stops'][6]['id'],line['stops'][9]['id'])
    value=alignment.generate(c,**PARAMETERS)
    assert value['route_m']<c['route_m']
    assert value['source_corridor_geometry_id']==c['corridor_geometry_id']
    assert [s['id'] for s in value['physical_definition']['stations']]==[s['id'] for s in c['definition']['stations']]
    assert value['calculated_alignment_screen_passed']
    assert value['numerical']['maximum_sampled_source_deviation_m']<50
    assert value['numerical']['interval_enclosure_verified'] is False


def test_performance_and_ancestry_changes_are_evaluation_only():
    c=corridor([[44.,33.],[44.0002,33.02],[44.001,33.04]])
    a=alignment.generate(c,**PARAMETERS)
    b=alignment.generate(c,**dict(PARAMETERS,requested_speed_m_s=10.))
    assert a['candidate_id']==b['candidate_id'] and a['evaluation_id']!=b['evaluation_id']
    changed=deepcopy(c);changed['source_sha256']={'other-proof':'e'*64};changed['evaluation_id']=identity({k:v for k,v in changed.items() if k!='evaluation_id'})
    d=alignment.generate(changed,**PARAMETERS)
    assert d['candidate_id']==a['candidate_id'] and d['evaluation_id']!=a['evaluation_id']


def test_impossible_platform_reverse_and_tight_spacing_fail_before_generation():
    c=corridor([[44.,33.],[44.,33.02]])
    with pytest.raises(ValueError,match='contain train'):
        alignment.generate(c,**dict(PARAMETERS,platform_straight_m=100.))
    with pytest.raises(ValueError,match='too close'):
        alignment.generate(corridor([[44.,33.],[44.,33.001]]),**PARAMETERS)
    with pytest.raises(ValueError,match='90degrees'):
        alignment.generate(corridor([[44.,33.],[44.,33.02],[44.02,33.02]]),**PARAMETERS)
