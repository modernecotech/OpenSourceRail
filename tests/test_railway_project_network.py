"""Mapped route/request controls; no native evaluation or timetable proof."""
from copy import deepcopy

import pytest

from engineering.railway_project import network
from engineering.station_rail.common import identity
from test_railway_project_frame import context,compile
from test_railway_project_civil import seal


def inputs(framed=True):
    args=context();p,a=args[2],args[4]
    legs=[]
    for i in range(len(a['legs'])):
        for direction in (1,-1):
            data=context(direction,i)
            q,m=compile(data)[:2] if framed else data[:2]
            legs.append((q,m))
    stations=a['physical_definition']['stations']
    trains=[dict(id='active1',initial_station_id=stations[0]['id'],initial_position_m=-.5,ready_at_s=0.,role='active',initial_drive_temperature_c=None),
        dict(id='reserve1',initial_station_id=stations[0]['id'],initial_position_m=0.,ready_at_s=0.,role='spare',initial_drive_temperature_c=None)]
    departures=[dict(id='out',route_id='leg-0-forward',departure_time_s=0.,requested_train_id='active1',departure_authorized=True),
        dict(id='onward',route_id='leg-1-forward',departure_time_s=500.,requested_train_id='active1',departure_authorized=True)]
    return p,a,legs,trains,departures


def evaluate(args,**kw):
    return network.compile_network(*args,**dict(dict(turnaround_s=30.,clearance_s=10.,
        release_control=dict(mode='grid-substitution-slew/2',force_slew_n_s=10000.,maximum_traction_share=1.,reserve_factor=2.)),**kw))


def test_route_lengths_cases_and_actual_signed_offsets_survive_compilation():
    args=inputs();before=deepcopy(args);q,m=evaluate(args)
    assert args==before
    assert q['id']==identity({k:v for k,v in q.items() if k!='id'})
    assert m['native_input_id']==identity(q) and m['route_m']==args[1]['route_m']
    assert q['trains'][0]['initial_position_m']==-.5
    assert m['active_trainsets']==m['spare_trainsets']==1
    assert m['service_evaluated'] is False and m['native_service_complete'] is False
    assert not m['physical_accepted']
    for departure in q['departures']:
        r=next(r for r in q['network']['routes'] if r['id']==departure['route_id'])
        assert r['distance_m']==departure['journey']['distance_m']-2
        assert r['from_station_id']==departure['departure_station_id']
        assert departure['frame_binding']['compiled_case_id']==departure['journey']['id']
    for s in q['stations']:
        assert s['initial_energy_j']==s['store']['capacity_j']==s['reset']['grid_energy_j']==0
        assert s['release']['max_force_n']==s['release']['max_power_w']==0


def test_unframed_negative_entry_is_retained_for_native_refusal():
    q,m=evaluate(inputs(False))
    assert q['trains'][0]['initial_position_m']==-.5
    assert all('entry_frame' not in r for r in q['network']['routes'])
    assert all('frame_binding' not in d for d in q['departures'])
    assert not m['native_service_complete']


def test_missing_or_aliased_directions_and_unknown_departure_routes_refuse():
    args=list(inputs());args[2]=args[2][:-1]
    with pytest.raises(ValueError,match='Both explicit directions'):
        evaluate(args)
    args=list(inputs());args[2][3]=deepcopy(args[2][0])
    with pytest.raises(ValueError,match='Duplicate directed leg'):
        evaluate(args)
    args=list(inputs());args[-1][0]['route_id']='invented-shortcut'
    with pytest.raises(ValueError,match='known route/train'):
        evaluate(args)


def test_resealed_stale_case_source_and_mixed_project_refuse():
    for edit,error in ((lambda m:m.update(native_method_sha256={}), 'current native source'),
                       (lambda m:m.update(bundle_evaluation_id='f'*64), 'same-project')):
        args=list(inputs());edit(args[2][0][1]);seal(args[2][0][1])
        with pytest.raises(ValueError,match=error):evaluate(args)
    args=list(inputs());q,m=args[2][0];q['mass_kg']+=1
    with pytest.raises(ValueError,match='Canonical same-project'):
        evaluate(args)


def test_extra_authority_is_not_a_coordinate_change_even_after_resealing():
    args=list(inputs());q,m=args[2][0]
    q['control']['end_of_authority_m']+=5
    q['id']=identity({k:v for k,v in q.items() if k!='id'})
    m['case_id']=q['id'];m['native_input_id']=identity(q);m['frame_binding']['compiled_case_id']=q['id'];seal(m)
    with pytest.raises(ValueError,match='Exact compiled frame'):
        evaluate(args)


def test_unknown_role_time_and_nonboolean_authorization_cannot_be_defaulted():
    args=list(inputs());args[3][0]['role']='probably-active'
    with pytest.raises(ValueError,match='roles'):
        evaluate(args)
    args=list(inputs());args[4][0]['departure_authorized']=1
    with pytest.raises(ValueError,match='authorization hypothesis'):
        evaluate(args)
    with pytest.raises(ValueError,match='clearance'):
        evaluate(inputs(),clearance_s=0.)
